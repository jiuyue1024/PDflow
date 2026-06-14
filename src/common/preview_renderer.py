# -*- coding: utf-8 -*-
"""
preview_renderer.py — V1.1 RC1 预览清晰度模块

职责：
  1. 高 DPI PDF → PNG 转换（fitz.Matrix(2.5, 2.5)）
  2. 字段 / 样式 hash 缓存（未变化不重新渲染）
  3. QPixmap 缩放（Qt.KeepAspectRatio + Qt.SmoothTransformation）

约束（V1.1 RC1 强制）：
  - 不依赖 PySide6-WebEngine
  - 不依赖 QtPdf / QtWebEngineWidgets
  - 不引入新的第三方包

依赖：
  - PyMuPDF (fitz)
  - PySide6.QtGui (QPixmap)
  - PySide6.QtCore (Qt.KeepAspectRatio, Qt.SmoothTransformation)
"""
import hashlib
import os
import tempfile
import time
import threading
from typing import Optional, Tuple, Dict, Any

import fitz  # PyMuPDF

from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt


# ── 默认配置 ────────────────────────────────────────────────────
# 预览 QLabel 固定显示宽度（像素）。所有 A4 模板渲染后都缩放到此宽度。
PREVIEW_FIXED_WIDTH = 560

# fitz Matrix 缩放系数（V1.1-RC3 统一预览倍率，避免预览发糊）
#   PREVIEW_SCALE = 2.0  （2.5 → 2.0：渲染像素数 -36%，缩放到 560px 仍锐利，内存增长<15%）
#   - 禁止 1.0（明显糊）
#   - 禁止 3.0（内存上涨明显）
#   作用范围：模板预览 / 名片预览 / PDF 缩略图 / 水印实时预览
#   不影响：PDF 导出 / 压缩 / OCR / PDF→图片 / PDF→PPT
PREVIEW_SCALE = 2.0
MATRIX_SCALE = PREVIEW_SCALE

# 像素上限（V1.1-RC3 新增）：避免 4K 显示器实时重绘 GPU 炸
#   - 最长边 ≤ 2200 px：fitz 渲染单页峰值
#   - 4K 屏实际显示 ≈ 3840×2160，预览缩放到 2200px 仍能 100% 可读（缩放后约 50% 屏宽）
#   - 配合 MAX_DPR=2.0，HiDPI 屏按 2x 算，源图最长边实际限制 ≈ 4400 物理像素
MAX_PREVIEW_PIXELS = 2200
MAX_DPR = 2.0


# ── 缓存 ────────────────────────────────────────────────────────
# 进程级缓存：key = (template_id, data_hash, style_hash, image_path)
# value = {"qpixmap": QPixmap, "w": int, "h": int, "render_ms": float, "ts": float}
_cache: Dict[Tuple[str, str, str, str], Dict[str, Any]] = {}
_cache_lock = threading.Lock()
_cache_hits = 0
_cache_misses = 0


def _hash_value(v: Any) -> str:
    """稳定的 hash：对 dict / list 排序后序列化"""
    if isinstance(v, dict):
        items = sorted(v.items(), key=lambda x: str(x[0]))
        return "{" + ",".join(f"{_hash_value(k)}:{_hash_value(val)}" for k, val in items) + "}"
    if isinstance(v, (list, tuple)):
        return "[" + ",".join(_hash_value(x) for x in v) + "]"
    return repr(v)


def make_cache_key(
    template_id: str,
    data: dict,
    style: Optional[dict] = None,
    image_path: Optional[str] = None,
    render_sides: Optional[list] = None,
    qr_image_path: Optional[str] = None,
) -> Tuple[str, str, str, str, str, str]:
    """生成稳定缓存 key"""
    data_hash = hashlib.md5(_hash_value(data).encode("utf-8")).hexdigest()[:16]
    style_hash = hashlib.md5(_hash_value(style or {}).encode("utf-8")).hexdigest()[:16]
    img_hash = image_path or ""
    sides_hash = ",".join(render_sides) if render_sides else ""
    qr_hash = qr_image_path or ""
    return (template_id, data_hash, style_hash, img_hash, sides_hash, qr_hash)


def cache_stats() -> Dict[str, int]:
    """缓存命中统计"""
    with _cache_lock:
        return {
            "hits": _cache_hits,
            "misses": _cache_misses,
            "size": len(_cache),
        }


def compute_safe_zoom(page_width_pt: float, page_height_pt: float,
                      target_scale: float = PREVIEW_SCALE,
                      max_pixels: int = MAX_PREVIEW_PIXELS) -> float:
    """根据页面尺寸 + 像素上限，计算安全的 fitz 缩放比

    用途：避免 4K 屏/A3 大页 等场景下渲染像素爆炸。
    算法：
        1. 目标 zoom = target_scale（默认 2.0）
        2. 限制 zoom：max_pixels / max(page_w, page_h)
        3. 取 min(target_scale, 上限)
        4. 不强制下限：超大页面（A0/A1）允许 zoom < 1.0，宁可缩源也不超像素上限

    Args:
        page_width_pt:  PDF 页面宽度（pt）
        page_height_pt: PDF 页面高度（pt）
        target_scale:   目标缩放比（默认 PREVIEW_SCALE=2.0）
        max_pixels:     渲染后最长边上限（默认 2200 px）

    Returns:
        安全的 fitz Matrix 缩放比（float，可能 < 1.0 但不会超过 max_pixels）
    """
    if page_width_pt <= 0 or page_height_pt <= 0:
        return target_scale
    long_edge_pt = max(page_width_pt, page_height_pt)
    pixel_cap_zoom = max_pixels / long_edge_pt
    return min(target_scale, pixel_cap_zoom)


def clear_cache() -> None:
    """清空缓存（模板切换 / 字体加载修复时调用）"""
    global _cache_hits, _cache_misses
    with _cache_lock:
        _cache.clear()
        _cache_hits = 0
        _cache_misses = 0


# ── 临时路径 ────────────────────────────────────────────────────
_TMP_DIR = os.path.join(
    os.environ.get("TEMP", tempfile.gettempdir()),
    "PDflow_Preview",
)
os.makedirs(_TMP_DIR, exist_ok=True)


# ── 核心函数 ────────────────────────────────────────────────────
def render_preview_pixmap(
    template_id: str,
    data: dict,
    style: Optional[dict] = None,
    image_path: Optional[str] = None,
    qr_image_path: Optional[str] = None,
    target_width: int = PREVIEW_FIXED_WIDTH,
    use_cache: bool = True,
    render_sides: Optional[list] = None,
) -> Tuple[QPixmap, Dict[str, Any]]:
    """
    渲染模板预览为高清晰度 QPixmap。

    流程：
      1. 计算缓存 key (template_id + data_hash + style_hash + image_path)
      2. 命中 → 直接返回缓存的 QPixmap（不重新生成 PDF/PNG）
      3. 未命中 → render_template() → fitz.Matrix(2.5, 2.5) → PNG → QPixmap
      4. 缓存并返回

    Returns:
        (QPixmap, info_dict)
        info_dict 包含：
          - "render_ms": 总耗时（ms）
          - "pdf_ms": PDF 渲染耗时
          - "pixmap_ms": fitz 转 PNG 耗时
          - "qpx_ms": Qt 加载 + 缩放耗时
          - "src_w", "src_h": 源 PNG 尺寸
          - "out_w", "out_h": QPixmap 输出尺寸
          - "cache_hit": bool
          - "matrix_scale": 2.5
          - "scale_factor": 输出 / 源 比例
    """
    info: Dict[str, Any] = {
        "render_ms": 0.0,
        "pdf_ms": 0.0,
        "pixmap_ms": 0.0,
        "qpx_ms": 0.0,
        "src_w": 0,
        "src_h": 0,
        "out_w": 0,
        "out_h": 0,
        "cache_hit": False,
        "matrix_scale": MATRIX_SCALE,
        "scale_factor": 0.0,
    }

    t_start = time.time()

    if not template_id:
        raise ValueError("template_id 不能为空")

    # ── 1. 缓存 key ──
    key = make_cache_key(template_id, data, style, image_path, render_sides, qr_image_path=qr_image_path)
    if use_cache:
        with _cache_lock:
            cached = _cache.get(key)
        if cached is not None:
            global _cache_hits
            _cache_hits += 1
            info["cache_hit"] = True
            info["render_ms"] = round((time.time() - t_start) * 1000, 1)
            info["out_w"] = cached["w"]
            info["out_h"] = cached["h"]
            info["src_w"] = cached.get("src_w", 0)
            info["src_h"] = cached.get("src_h", 0)
            info["scale_factor"] = round(cached["w"] / max(cached.get("src_w", 1), 1), 3)
            return cached["qpixmap"], info

    # ── 2. 未命中 → 渲染 ──
    global _cache_misses
    _cache_misses += 1

    pdf_path = os.path.join(_TMP_DIR, f"preview_{template_id}.pdf")
    png_path = os.path.join(_TMP_DIR, f"preview_{template_id}.png")

    # 2.1 调 render_template 生成 PDF
    t_pdf_start = time.time()
    from src.common.template_renderer import render_template  # 延迟 import 避免循环
    extra_kwargs: Dict[str, Any] = {}
    if render_sides:
        # V1.1 RC1 名片双面：仅渲染指定面用于预览
        extra_kwargs["render_sides"] = render_sides
    if qr_image_path:
        # V1.1 RC1 名片双面：QR 图片路径
        extra_kwargs["qr_image_path"] = qr_image_path
    try:
        # 注意：render_business_card 的 style 参数名是 style_options，
        # 而 render_template / render_notice 等其它渲染器用 style。
        # 这里统一传 style_options，render_business_card 会接受，其它渲染器
        # 会因参数名不匹配抛 TypeError，然后 fallback 路径会用通用调用。
        render_template(
            template_id, pdf_path, data,
            image_path=image_path,
            style_options=style,
            **extra_kwargs,
        )
    except TypeError as e:
        # 旧签名 fallback（render_notice 等不支持 render_sides/style_options）
        # 保留关键参数：render_sides 让双面模板能只渲染当前面
        fallback_kwargs = {}
        if render_sides:
            fallback_kwargs["render_sides"] = render_sides
        if qr_image_path:
            fallback_kwargs["qr_image_path"] = qr_image_path
        try:
            render_template(template_id, pdf_path, data, **fallback_kwargs)
        except TypeError:
            render_template(template_id, pdf_path, data)
    info["pdf_ms"] = round((time.time() - t_pdf_start) * 1000, 1)

    # 2.2 fitz.Matrix(PREVIEW_SCALE, PREVIEW_SCALE) 高 DPI 转 PNG
    t_pix_start = time.time()
    doc = fitz.open(pdf_path)
    try:
        if not doc.page_count:
            raise ValueError("PDF 无页面")
        page = doc.load_page(0)
        # 使用 Matrix 缩放 2.5x，比 dpi= 更可控
        matrix = fitz.Matrix(MATRIX_SCALE, MATRIX_SCALE)
        pix = page.get_pixmap(matrix=matrix, alpha=False)
        pix.save(png_path)
        src_w, src_h = pix.width, pix.height
    finally:
        doc.close()
    info["pixmap_ms"] = round((time.time() - t_pix_start) * 1000, 1)
    info["src_w"] = src_w
    info["src_h"] = src_h

    # 2.3 加载为 QPixmap 并按目标宽度等比缩放
    t_qpx_start = time.time()
    qpix = QPixmap(png_path)
    if qpix.isNull():
        raise ValueError(f"无法加载 PNG: {png_path}")

    # 等比缩放到固定宽度（A4 高宽比 ≈ 1.414，允许高度 4 倍内）
    scaled = qpix.scaled(
        target_width, target_width * 4,
        Qt.KeepAspectRatio, Qt.SmoothTransformation,
    )
    info["qpx_ms"] = round((time.time() - t_qpx_start) * 1000, 1)
    info["out_w"] = scaled.width()
    info["out_h"] = scaled.height()
    info["scale_factor"] = round(scaled.width() / max(src_w, 1), 3)
    info["render_ms"] = round((time.time() - t_start) * 1000, 1)

    # ── 3. 写入缓存 ──
    if use_cache:
        with _cache_lock:
            _cache[key] = {
                "qpixmap": scaled,
                "w": scaled.width(),
                "h": scaled.height(),
                "src_w": src_w,
                "src_h": src_h,
                "ts": time.time(),
            }

    return scaled, info
