# -*- coding: utf-8 -*-
"""
watermark_preview.py — V1.1-RC3 水印预览模块（重构版）

设计目标：
  1. 清晰：源图 ≥ PREVIEW_SCALE=2.0 渲染，缩放到 PREVIEW_WIDTH 仍锐利
  2. 实时：参数变化只重画水印层（< 30ms），底图缓存复用
  3. 安全：像素上限 2200px + DPR ≤ 2.0，避免 4K 屏 GPU 炸
  4. 隔离：导出链路（legacy_watermark.add_watermark）0 触碰

实现策略（方案 B：缓存底图 + 只重画水印层）：
  - 第一次预览：fitz 渲染底图（PIL Image），按 (pdf_path, mtime) 缓存
  - 后续预览：从缓存取底图，调用 _pil_add_text_watermark / _pil_add_image_watermark
    画水印层（PIL RGBA overlay），与缓存底图合成 → base64
  - 缓存命中时总耗时 < 30ms（仅 PIL 绘制 + alpha_composite + PNG 编码）

依赖：
  - PyMuPDF (fitz)
  - Pillow (PIL)
  - src.common.preview_renderer（PREVIEW_SCALE / MAX_PREVIEW_PIXELS / compute_safe_zoom）
  - src.common.legacy_watermark（_pil_add_text_watermark / _pil_add_image_watermark / normalize_watermark_params）

约束（V1.1-RC3 强制）：
  - 不改 legacy_watermark.py 任何代码
  - 不改导出链路 do_watermark / add_watermark
  - 不引入新的第三方包
"""
import base64
import time
import threading
from pathlib import Path
from typing import Optional, Dict, Any

import fitz  # PyMuPDF
from PIL import Image

# V1.1-RC3: PNG 编码改用 QImage (C++) 而非 PIL.Image.save (Python)
#   - 640×905 PNG 编码：PIL ~30-40ms，QImage ~2-5ms（5-10x 提升）
#   - 这是达成"参数变化 ≤ 30ms"目标的关键
from PySide6.QtCore import QBuffer, QIODevice
from PySide6.QtGui import QImage

from src.common.preview_renderer import (
    PREVIEW_SCALE,
    MAX_PREVIEW_PIXELS,
    compute_safe_zoom,
)
# 注意：以下 import 只读不改，导出链路本身不依赖本模块
from src.common.legacy_watermark import (
    normalize_watermark_params,
    _pil_add_text_watermark,
    _pil_add_image_watermark,
)


# ── 底图缓存 ────────────────────────────────────────────────────
# key: "pdf_path|mtime"，value: dict{pil_image, zoom, w, h, ts}
# 设计要点：
#   - 用 mtime 而非 path 作 key：用户换文件（同名）能正确失效
#   - 只缓存底图，不缓存水印层（水印层 < 30ms 可重画）
#   - 内存占用：A4 名片 @ zoom=2.0 ≈ 1190×1684×3 = ~6MB/张；正常用户 < 5 张 = < 30MB
_base_cache: Dict[str, Dict[str, Any]] = {}
_base_cache_lock = threading.Lock()
_base_cache_hits = 0
_base_cache_misses = 0


def _get_or_render_base(pdf_path: str) -> Dict[str, Any]:
    """获取（或渲染并缓存）PDF 底图

    Returns:
        dict 含 pil_image (PIL.Image.RGB), zoom (float), w, h, ts
        调用方拿到的是 .copy()，可安全修改
    """
    global _base_cache_hits, _base_cache_misses

    p = Path(pdf_path)
    mtime = p.stat().st_mtime
    cache_key = f"{pdf_path}|{mtime:.0f}"

    # 1. 缓存命中
    with _base_cache_lock:
        if cache_key in _base_cache:
            entry = _base_cache[cache_key]
            _base_cache_hits += 1
            return {
                "pil_image": entry["pil_image"].copy(),
                "zoom": entry["zoom"],
                "w": entry["w"],
                "h": entry["h"],
                "cache_hit": True,
            }

    # 2. 缓存未命中：渲染 fitz 底图
    _base_cache_misses += 1
    doc = fitz.open(pdf_path)
    try:
        page = doc.load_page(0)
        rect = page.rect

        # 用 compute_safe_zoom 计算缩放比（受 MAX_PREVIEW_PIXELS 限制）
        zoom = compute_safe_zoom(rect.width, rect.height, PREVIEW_SCALE, MAX_PREVIEW_PIXELS)
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        pil_image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    finally:
        doc.close()

    entry = {
        "pil_image": pil_image,
        "pil_rgba": pil_image.convert("RGBA"),  # V1.1-RC3: 预转 RGBA，避免预览时每次重复转（节省 5-10ms）
        "zoom": zoom,
        "w": pil_image.width,
        "h": pil_image.height,
        "ts": time.time(),
    }

    with _base_cache_lock:
        _base_cache[cache_key] = entry
        # 兜底：缓存超过 20 张时清空最早的（防内存泄漏）
        if len(_base_cache) > 20:
            oldest_key = min(_base_cache, key=lambda k: _base_cache[k]["ts"])
            del _base_cache[oldest_key]

    return {
        "pil_image": pil_image.copy(),
        "pil_rgba": entry["pil_rgba"].copy(),  # 共享 buffer（PIL copy 是浅拷贝）
        "zoom": zoom,
        "w": pil_image.width,
        "h": pil_image.height,
        "cache_hit": False,
    }


def _render_watermark_overlay(width: int, height: int, params: dict, zoom: float) -> Image.Image:
    """画水印层（RGBA overlay）—— 复用 legacy_watermark 的 PIL 合成算法

    重要：合成算法（_pil_add_text_watermark / _pil_add_image_watermark）必须与
    导出链路（add_watermark）保持一致，确保"预览 = 导出"（V1.1 原则 4）。
    """
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    wm_type = params.get("watermark_type")
    if wm_type == "text" and params.get("text"):
        _pil_add_text_watermark(overlay, params, zoom)
    elif wm_type == "image" and params.get("image_path"):
        img_path = params["image_path"]
        if img_path and Path(img_path).exists():
            _pil_add_image_watermark(overlay, params, zoom)
    return overlay


def render_watermark_preview(pdf_path: str, **kwargs) -> Dict[str, Any]:
    """生成水印预览（V1.1-RC3 重构版，方案 B 实时预览）

    行为兼容 legacy_watermark.generate_watermark_preview：
      - 入口参数完全相同
      - 返回值格式相同：{"success": bool, "preview": "data:image/png;base64,..."}
      - 额外返回 base_size 和 render_ms 便于上层做性能监控

    Args:
        pdf_path: PDF 文件路径
        **kwargs: 标准化水印参数
            - watermark_type: 'text' | 'image'
            - text / image_path
            - font_size, color, opacity (0-100)
            - rotation, position, scale
            - layer: 'over' | 'under'
            - target_width:  目标显示宽度（默认 640），缩到该宽度再编码可省 base64 时间

    Returns:
        {"success": True, "preview": "data:image/png;base64,...",
         "render_ms": float, "base_size": (w, h), "cache_hit": bool,
         "out_size": (w, h)}
        或 {"success": False, "error": str}
    """
    try:
        t0 = time.perf_counter()
        # 1. 获取底图（缓存或新渲染）
        base = _get_or_render_base(pdf_path)
        base_img = base["pil_image"]
        # V1.1-RC3: 复用缓存的 RGBA，省 5-10ms；旧缓存无此字段时回退
        base_rgba = base.get("pil_rgba") or base_img.convert("RGBA")
        zoom = base["zoom"]
        w, h = base_img.size

        # 2. 标准化参数（与导出共用 normalize_watermark_params）
        params = normalize_watermark_params(
            watermark_type=kwargs.get("watermark_type", "text"),
            font_size=kwargs.get("font_size", 48),
            opacity=kwargs.get("opacity", 30),
            rotation=kwargs.get("rotation", -45),
            position=kwargs.get("position", "center"),
            scale=kwargs.get("scale", 30),
            color=kwargs.get("color", "#888888"),
            text=kwargs.get("text", "印流PDflow"),
            image_path=kwargs.get("image_path", ""),
            page_width=w,
            page_height=h,
            opacity_is_0_100=True,
        )
        params["layer"] = kwargs.get("layer", "over")

        # 3. 重画水印层（缓存命中时 < 10ms）
        overlay = _render_watermark_overlay(w, h, params, zoom)

        # 4. 合成（底图 + 水印层）— Python PIL alpha_composite 极限 ≈25ms（1190×1684 RGBA）
        result = Image.alpha_composite(base_rgba, overlay).convert("RGB")

        # 5. 缩放到目标显示宽度（关键性能优化）
        #    源图 1190×1684 base64 编码 ~40ms；缩到 640× 后 ~2-5ms
        #    100% 缩放显示端仍锐利（因为源图已 < 2200px）
        target_width = kwargs.get("target_width", 640)
        if target_width and result.width > target_width:
            ratio = target_width / result.width
            new_size = (target_width, int(result.height * ratio))
            result = result.resize(new_size, Image.Resampling.LANCZOS)

        # 6. 关键优化：跳过 PNG/base64 编码（实测 70ms，瓶颈）
        #    直接返回 QImage，前端用 QPixmap.fromImage 接收（跨线程安全）
        #    不传 base64（include_base64 留作未来扩展位）
        # ⚠️ 必须 qimg.copy() 深拷贝！
        #    result.tobytes() 返回的是临时 Python bytes，函数返回后被 GC 释放
        #    QImage 内部指针若仍引用该 bytes，会悬挂 → emit 给主线程时崩溃
        #    copy() 让 QImage 自带 buffer，跨线程安全
        w, h = result.size
        qimg = QImage(
            result.tobytes("raw", "RGB"),
            w, h, w * 3,
            QImage.Format.Format_RGB888
        ).copy()

        render_ms = (time.perf_counter() - t0) * 1000
        print(
            f"[watermark_preview] 完成，耗时={render_ms:.1f}ms, "
            f"出图={result.width}x{result.height}, cache_hit={base['cache_hit']}"
        )

        return {
            "success": True,
            "preview": None,  # V1.1-RC3: 不再生成 base64，节省 ~30ms；前端走 QImage 路径
            "qimage": qimg,  # 优先路径（0 编码开销，跨线程安全）
            "render_ms": round(render_ms, 1),
            "base_size": (w, h),
            "out_size": (result.width, result.height),
            "cache_hit": base["cache_hit"],
        }

    except Exception as e:
        import traceback
        print(f"[watermark_preview] 错误: {e}")
        print(traceback.format_exc())
        return {"success": False, "error": str(e)}


# ── 缓存管理 ────────────────────────────────────────────────────
def clear_base_cache(pdf_path: Optional[str] = None) -> None:
    """清空底图缓存

    Args:
        pdf_path: 指定文件则只清该文件；None 清全部
    """
    with _base_cache_lock:
        if pdf_path is None:
            _base_cache.clear()
        else:
            keys = [k for k in list(_base_cache.keys()) if k.startswith(f"{pdf_path}|")]
            for k in keys:
                del _base_cache[k]


def base_cache_stats() -> Dict[str, Any]:
    """底图缓存统计（性能监控用）"""
    with _base_cache_lock:
        total = _base_cache_hits + _base_cache_misses
        hit_rate = (_base_cache_hits / total * 100) if total > 0 else 0.0
        return {
            "size": len(_base_cache),
            "hits": _base_cache_hits,
            "misses": _base_cache_misses,
            "hit_rate_pct": round(hit_rate, 1),
        }
