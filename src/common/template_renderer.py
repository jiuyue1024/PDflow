# -*- coding: utf-8 -*-
"""
template_renderer.py — 模板排版 PDF 渲染引擎

TPL-02：实现 business_card 模板渲染（支持样式选项）
TPL-03：后续实现 notice / product_spec 模板渲染
TPL-05：支持上传图片嵌入名片模板
"""
import fitz  # PyMuPDF
import os
import sys

# V1.1 RC 收尾：导入 PDF 矢量绘制函数集（Route B — 禁止任何 PNG 嵌入作为背景/图标）
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)
from export import (
    draw_linear_gradient as _draw_linear_gradient,
    draw_diagonal_4corner_gradient as _draw_diagonal_4corner_gradient,
    draw_text_icon as _draw_text_icon,
    embed_qr_code as _embed_qr_code,
    render_with_pymupdf as _render_bg_with_pymupdf,
)
import math

# 统一文本排版工具（V1.1-beta 文本约束修复）
from src.common.text_layout import draw_wrapped_text, truncate_text, parse_items


# ================================================================
# 模块级缓存
# ================================================================

# CJK 字体缓存：避免每次调用 _get_cjk_font() 时重复扫描磁盘
_cjk_font_cache = None

# 字符宽度缓存：避免 _wrap_text_in_width 中对相同字符+字号重复测量
_char_width_cache = {}


# ================================================================
# 辅助函数
# ================================================================

def _mm_to_points(mm: float) -> float:
    """毫米转 PDF 点（1 inch = 25.4 mm = 72 points）"""
    return mm / 25.4 * 72


def _points_to_mm(pt: float) -> float:
    """PDF 点转毫米"""
    return pt / 72 * 25.4


def _hex_to_rgb(hex_color: str) -> tuple:
    """将 hex 颜色字符串 (#RRGGBB) 转换为 RGB 三元组 (0.0-1.0)。"""
    if not hex_color or len(hex_color) < 7:
        return (0, 0, 0)
    try:
        hex_color = hex_color.lstrip("#")
        r = int(hex_color[0:2], 16) / 255
        g = int(hex_color[2:4], 16) / 255
        b = int(hex_color[4:6], 16) / 255
        return (r, g, b)
    except Exception:
        return (0, 0, 0)


def _safe_insert_image(page, file_path: str, rect) -> bool:
    """V1.1 RC 收尾：健壮的图片插入 — 先尝试直接插入，失败时用 PIL 转换为 PNG bytes 再插入。
    解决 fitz `page.insert_image(filename=...)` 对部分格式（PDF/损坏）报 code=7 的问题。
    返回是否插入成功。
    """
    # 1) 直接插入（PNG/JPG 一般 OK）
    try:
        page.insert_image(rect, filename=file_path)
        return True
    except Exception as e1:
        print(f"[renderer] insert_image(filename) 失败: {e1}，尝试 PIL 转码后插入")

    # 2) 用 PIL 转换为 RGBA PNG bytes
    try:
        from PIL import Image as _PILImg
        import io
        with _PILImg.open(file_path) as _img:
            if _img.mode not in ("RGB", "RGBA", "L"):
                _img = _img.convert("RGBA")
            buf = io.BytesIO()
            _img.save(buf, format='PNG', optimize=True)
            buf.seek(0)
            page.insert_image(rect, stream=buf.getvalue())
            return True
    except Exception as e2:
        print(f"[renderer] PIL 转码插入也失败: {e2}")
        return False


def _hex_to_brightness(hex_color: str) -> float:
    """将 hex 颜色转换为相对亮度值 (0.0-1.0)，使用 ITU-R BT.709 公式。"""
    if not hex_color or len(hex_color) < 7:
        return 0.0
    try:
        hex_color = hex_color.lstrip("#")
        r = int(hex_color[0:2], 16) / 255
        g = int(hex_color[2:4], 16) / 255
        b = int(hex_color[4:6], 16) / 255
        return r * 0.299 + g * 0.587 + b * 0.114
    except Exception:
        return 0.0


def _insert_text_safe(page, text: str, x: float, y: float,
                     fontsize: float = 11, color: tuple = (0, 0, 0),
                     fontname: str = "helv", regular: bool = False):
    """向页面插入文字，自动使用系统中文字体，避免 Helvetica 无法渲染中文的问题。
    regular=True 时使用 Regular 细体（用于次要文字：联系方式、描述、SLOGAN 等）。"""
    if not text:
        return
    try:
        tw = fitz.TextWriter(page.rect, color=color)
        font = _get_cjk_font_regular() if regular else _get_cjk_font()
        if font:
            tw.append((x, y), text, font=font, fontsize=fontsize)
        else:
            tw.append((x, y), text, fontsize=fontsize)
        tw.write_text(page)
    except Exception as e:
        print(f"[renderer] 文本写入失败: {e}")


def _insert_text_centered(page, text: str, center_x: float, y: float,
                          fontsize: float = 11, width: float = 0,
                          color: tuple = (0, 0, 0)):
    """居中渲染文本（以 center_x 为水平中心）。

    参数：
        page: fitz.Page 对象
        text: 要渲染的文本（空字符串自动跳过）
        center_x: 文本水平中心 x 坐标（点）
        y: 文本基线 y 坐标（点）
        fontsize: 字号（点）
        width: 整段可用宽度（点，仅用于扩展点预留，暂未使用）
        color: RGB 三元组 (0.0-1.0)
    """
    if not text:
        return
    try:
        text_w = _measure_text_width(text, fontsize=fontsize)
        start_x = center_x - text_w / 2
        _insert_text_safe(page, text, start_x, y, fontsize=fontsize, color=color)
    except Exception as e:
        print(f"[renderer] 居中文字渲染失败: {e}")


def _insert_text_centered_with_prefix(page, prefix: str, val: str,
                                      center_x: float, y: float,
                                      prefix_size: float, val_size: float,
                                      prefix_color: tuple, val_color: tuple,
                                      gap: float = 0):
    """居中渲染「带前缀的组合文本」（如「t 138-0000-0000」）。

    整个组合（prefix + gap + val）的水平中心对齐到 center_x，
    其中 prefix 用 prefix_size 字号 + prefix_color，val 用 val_size 字号 + val_color。

    参数：
        page: fitz.Page 对象
        prefix: 前缀文字（如 "t" / "e" / "a"），允许为空
        val: 主要文本（如电话号码）
        center_x: 组合整体水平中心
        y: 文本基线
        prefix_size: 前缀字号
        val_size: 主要文本字号
        prefix_color: 前缀颜色
        val_color: 主要文本颜色
        gap: 前缀与主要文本之间的间距（点）
    """
    if not val:
        return
    try:
        prefix_w = _measure_text_width(prefix, fontsize=prefix_size) if prefix else 0.0
        val_w = _measure_text_width(val, fontsize=val_size)
        total_w = prefix_w + gap + val_w
        start_x = center_x - total_w / 2

        if prefix:
            _insert_text_safe(page, prefix, start_x, y,
                              fontsize=prefix_size, color=prefix_color)
        _insert_text_safe(page, val, start_x + prefix_w + gap, y,
                          fontsize=val_size, color=val_color)
    except Exception as e:
        print(f"[renderer] 带前缀居中文字渲染失败: {e}")


def _measure_text_width(text: str, fontsize: float = 11) -> float:
    """测量文本在指定字号下的渲染宽度（点），使用 CJK 字体或默认字体。
    带字符级宽度缓存，避免重复测量。
    """
    if not text:
        return 0.0
    try:
        font = _get_cjk_font()
        if font:
            # 逐字符缓存宽度，再累加
            total = 0.0
            for ch in text:
                cache_key = (ch, fontsize)
                if cache_key in _char_width_cache:
                    total += _char_width_cache[cache_key]
                else:
                    w = font.text_length(ch, fontsize=fontsize)
                    _char_width_cache[cache_key] = w
                    total += w
            return total
        else:
            return fitz.Font("helv").text_length(text, fontsize=fontsize)
    except Exception:
        # 粗略估算：中文约等于字号宽度，英文约等于字号*0.5
        cn_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        en_chars = len(text) - cn_chars
        return cn_chars * fontsize + en_chars * fontsize * 0.5


def _truncate_to_width(text: str, max_width_pt: float, fontsize: float,
                       ellipsis: str = "…") -> str:
    """按渲染宽度截断文本，超出 max_width_pt 时末尾加省略号。
    用于固定字号布局中的横向溢出保护（不缩字号，仅截断）。
    """
    if not text:
        return text
    if max_width_pt <= 0:
        return ""
    full_w = _measure_text_width(text, fontsize)
    if full_w <= max_width_pt:
        return text
    # 二分搜索最长可容纳长度
    ellipsis_w = _measure_text_width(ellipsis, fontsize)
    available = max_width_pt - ellipsis_w
    if available <= 0:
        return ellipsis
    lo, hi = 0, len(text)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if _measure_text_width(text[:mid], fontsize) <= available:
            lo = mid
        else:
            hi = mid - 1
    return text[:lo] + ellipsis


def _wrap_text_in_width(text: str, fontsize: float, max_width_pt: float) -> list:
    """
    将文本按指定宽度自动换行，返回分行列表。
    优先在空格、标点处断行；如果单字超宽也强制断行。
    利用 _measure_text_width 的字符级缓存加速重复测量。
    """
    if not text:
        return []
    if _measure_text_width(text, fontsize) <= max_width_pt:
        return [text]

    lines = []
    remaining = text
    while remaining:
        # 逐字符测量，找到不超过 max_width_pt 的最大子串
        best_idx = len(remaining)
        for i in range(len(remaining), 0, -1):
            if _measure_text_width(remaining[:i], fontsize) <= max_width_pt:
                best_idx = i
                break

        if best_idx == len(remaining):
            lines.append(remaining)
            break

        # 尝试在 best_idx 附近找断点（空格或标点）
        break_idx = best_idx
        for i in range(best_idx, max(best_idx - 8, 0), -1):
            if remaining[i] in (' ', '\uff0c', '\u3002', '\u3001', '\uff1b', '\uff1a', '\uff09', ')',
                                '\u3011', ']', '\uff01', '?', '\uff1f', ',', '.', ';', ':'):
                break_idx = i + 1
                break

        if break_idx <= 0:
            break_idx = best_idx  # 强制断行

        lines.append(remaining[:break_idx])
        remaining = remaining[break_idx:].lstrip()

    return lines


def _get_cjk_font():
    """查找系统中的中文字体文件（Bold），返回 fitz.Font 对象。
    使用模块级缓存，避免每次调用时重复扫描磁盘。

    优先使用微软雅黑 Bold（最接近设计稿的粗细感），其次常规雅黑，最后其它。
    """
    global _cjk_font_cache
    if _cjk_font_cache is not None:
        return _cjk_font_cache

    # 注意：PyMuPDF 1.24+ 已移除 fontno 参数，所有 .ttc 文件必须按集合名加载
    font_candidates = [
        "C:/Windows/Fonts/msyhbd.ttc",   # 微软雅黑 Bold（首选，强对比感）
        "C:/Windows/Fonts/msyh.ttc",     # 微软雅黑 Regular
        "C:/Windows/Fonts/simhei.ttf",   # SimHei
        "C:/Windows/Fonts/simsun.ttc",   # SimSun
        "C:/Windows/Fonts/yahei.ttf",
        "C:/Windows/Fonts/microsoftyahei.ttf",
    ]
    for fp in font_candidates:
        if os.path.exists(fp):
            try:
                _cjk_font_cache = fitz.Font(fontfile=fp)
                return _cjk_font_cache
            except Exception as e:
                print(f"[renderer] 字体加载失败 {fp}: {e}")
                continue
    # 未找到任何字体，缓存 None 以避免反复扫描
    _cjk_font_cache = None
    return None


_cjk_font_regular_cache = None
def _get_cjk_font_regular():
    """返回细体（Regular）中文字体，用于次要文字（联系方式、描述、SLOGAN 等）。"""
    global _cjk_font_regular_cache
    if _cjk_font_regular_cache is not None:
        return _cjk_font_regular_cache
    # 优先 Regular；如果只有 Bold 就降级用 Regular 路径
    candidates = [
        "C:/Windows/Fonts/msyh.ttc",     # 微软雅黑 Regular（首选）
        "C:/Windows/Fonts/simsun.ttc",   # SimSun
        "C:/Windows/Fonts/msyhbd.ttc",   # Bold 兜底
    ]
    for fp in candidates:
        if os.path.exists(fp):
            try:
                _cjk_font_regular_cache = fitz.Font(fontfile=fp)
                return _cjk_font_regular_cache
            except Exception as e:
                print(f"[renderer] Regular 字体加载失败 {fp}: {e}")
                continue
    _cjk_font_regular_cache = None
    return None


_cjk_font_file_cache = None
def _get_cjk_font_file():
    """返回中文字体文件路径（字符串），供 insert_textbox 使用。"""
    global _cjk_font_file_cache
    if _cjk_font_file_cache is not None:
        return _cjk_font_file_cache
    font_candidates = [
        "C:/Windows/Fonts/msyhbd.ttc",
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/simsun.ttc",
        "C:/Windows/Fonts/yahei.ttf",
        "C:/Windows/Fonts/microsoftyahei.ttf",
    ]
    for fp in font_candidates:
        if os.path.exists(fp):
            _cjk_font_file_cache = fp
            return fp
    _cjk_font_file_cache = ""
    return ""


_cjk_font_file_regular_cache = None
def _get_cjk_font_file_regular():
    """返回 Regular 细体中文字体文件路径（字符串），供 insert_textbox 使用。"""
    global _cjk_font_file_regular_cache
    if _cjk_font_file_regular_cache is not None:
        return _cjk_font_file_regular_cache
    candidates = [
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simsun.ttc",
        "C:/Windows/Fonts/msyhbd.ttc",
    ]
    for fp in candidates:
        if os.path.exists(fp):
            _cjk_font_file_regular_cache = fp
            return fp
    _cjk_font_file_regular_cache = ""
    return ""


def _draw_location_pin(page, x: float, y: float, size: float, color: tuple,
                        align_width: float = 0):
    """在PDF中绘制位置图钉图标（圆形顶部 + 尖端底部 + 中心白点）。
    
    参数：
        page: fitz.Page
        x: 图标左边界 x 坐标（点）
        y: 图标基线 y 坐标（点），图标向上绘制
        size: 图标整体高度（点）
        color: RGB 三元组 (0.0-1.0)
        align_width: 图标+间距占据的总宽度（用于与☎✉图标对齐），0=自动
    """
    # 图钉参数：圆形头部占整体高度的 60%，尖端占 40%
    head_ratio = 0.60
    head_h = size * head_ratio      # 圆形头部高度
    tail_h = size * (1 - head_ratio)  # 尖端高度
    
    # 圆形头部的半径（使圆形高度 = 2r ≈ head_h）
    r = head_h / 2.0
    
    # 圆心位置
    cx = x + r  # 圆心 x（左对齐）
    cy = y - tail_h - r  # 圆心 y（从基线向上：先过尖端，再过圆形）
    
    # 绘制尖端（三角形，尖端朝下）
    tail_pts = [
        fitz.Point(cx - r * 0.75, cy + r * 0.3),  # 左上
        fitz.Point(cx + r * 0.75, cy + r * 0.3),  # 右上
        fitz.Point(cx, y),                          # 尖端（基线位置）
    ]
    page.draw_polyline(tail_pts, color=color, fill=color, closePath=True)
    
    # 绘制圆形头部（覆盖尖端与圆形的连接处）
    page.draw_circle(fitz.Point(cx, cy), r, color=color, fill=color)
    
    # 中心白色圆点
    page.draw_circle(fitz.Point(cx, cy), r * 0.38, color=(1, 1, 1), fill=(1, 1, 1))
    
    # 返回文字起始 x 坐标：对齐 ☎ 图标宽度
    if align_width > 0:
        return x + align_width
    return cx + r + 1.5


# ================================================================
# V1.1 RC 收尾：联系图标 — 英文简写（无徽章，纯字符）
# 字母映射：phone=T, email=@, website=W, address=A
# 颜色自适应：浅色底用主题蓝（#4D7CFE），深色底用白色
# 规范：64×64 透明画布 + 居中大字符
# ================================================================

_icon_png_cache: dict = {}


def _load_english_font(size: int):
    """加载英文字体粗体（带 fallback）。"""
    from PIL import ImageFont
    import os
    for fp in [
        r"C:\Windows\Fonts\arialbd.ttf",
        r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\msyhbd.ttc",
        r"C:\Windows\Fonts\msyh.ttc",
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]:
        try:
            if os.path.isfile(fp):
                return ImageFont.truetype(fp, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _render_icon_png(icon_type: str, size_px: int = 64, color: tuple = (0.30, 0.49, 0.99)) -> bytes:
    """用 Pillow 渲染英文简写图标（无徽章，字符严格统一视觉大小）。

    V1.1 RC 收尾：T/@/W/A 字符自然宽度不同（T 窄 W 宽），先用 1.0x 渲染测 bbox，
    再等比缩放使 max(w, h) = target_visual = 80% 画布，最后居中绘制 — 像素级统一。

    字母映射：
        phone   → T  (Telephone)
        email   → @  (Email 通用)
        website → W  (Web)
        address → A  (Address)
    """
    from PIL import Image, ImageDraw
    import io

    # 0-1 RGB → 0-255 RGBA
    rgb = (
        max(0, min(255, int(round(color[0] * 255)))),
        max(0, min(255, int(round(color[1] * 255)))),
        max(0, min(255, int(round(color[2] * 255)))),
    )
    letter_rgba = (rgb[0], rgb[1], rgb[2], 255)

    img = Image.new("RGBA", (size_px, size_px), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    letter_map = {
        "phone":   "T",
        "email":   "@",
        "website": "W",
        "address": "A",
    }
    letter = letter_map.get(icon_type, "?")

    # 1. 初始字号（足够大以保证缩放质量）
    initial_size = int(size_px * 1.0)  # 1.0x 画布
    font = _load_english_font(initial_size)

    # 2. V1.1 RC 收尾：用实测透明像素 bbox 作为视觉大小基准（不是 font metrics）
    #    原因：T/W/@/A 字符的 getmetrics() ascent 接近，但 @ 的实际像素 bbox（54px）
    #    比 T（40px）大很多；用 ascent 缩放无法消除 @ 字符的"看起来更大"问题。
    #    改为：先在临时大画布渲染，测实际非透明像素 bbox，再缩放使 max(w, h) = target_pix
    target_pix = int(size_px * 0.85)  # 85% 画布作为统一视觉大小

    # 临时画布测实际像素 bbox
    test_img = Image.new("RGBA", (size_px, size_px), (0, 0, 0, 0))
    test_draw = ImageDraw.Draw(test_img)
    # 居中渲染（先按 bbox 估算位置）
    bbox0 = test_draw.textbbox((0, 0), letter, font=font)
    tw0 = bbox0[2] - bbox0[0]
    th0 = bbox0[3] - bbox0[1]
    test_draw.text(((size_px - tw0) // 2 - bbox0[0], (size_px - th0) // 2 - bbox0[1]),
                   letter, fill=(0, 0, 0, 255), font=font)
    pix_bbox = test_img.getbbox()  # 非透明像素 bbox
    if pix_bbox:
        pw = pix_bbox[2] - pix_bbox[0]
        ph = pix_bbox[3] - pix_bbox[1]
        current_max = max(pw, ph)
        if current_max > 0 and current_max != target_pix:
            scale = target_pix / current_max
            new_size = max(1, int(initial_size * scale))
            font = _load_english_font(new_size)

    # 3. 居中绘制
    img = Image.new("RGBA", (size_px, size_px), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    bbox = draw.textbbox((0, 0), letter, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (size_px - text_w) // 2 - bbox[0]
    y = (size_px - text_h) // 2 - bbox[1]
    draw.text((x, y), letter, fill=letter_rgba, font=font)

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def _get_icon_png(icon_type: str, color: tuple, size_px: int = 64) -> bytes:
    """获取图标 PNG bytes（带全局缓存）。"""
    key = (icon_type, tuple(color), size_px)
    if key not in _icon_png_cache:
        _icon_png_cache[key] = _render_icon_png(icon_type, size_px, color)
    return _icon_png_cache[key]


def _embed_image_in_page(page, image_path: str, x_mm: float, y_mm: float,
                         width_mm: float, height_mm: float):
    """
    将图片嵌入到 PDF 页面指定区域（单位：毫米）。
    支持 .png / .jpg / .jpeg 格式。
    如果文件不存在或格式不支持，静默忽略。
    """
    if not image_path or not os.path.isfile(image_path):
        return

    ext = os.path.splitext(image_path)[1].lower()
    if ext not in [".png", ".jpg", ".jpeg"]:
        return

    try:
        x = _mm_to_points(x_mm)
        y = _mm_to_points(y_mm)
        w = _mm_to_points(width_mm)
        h = _mm_to_points(height_mm)

        img_rect = fitz.Rect(x, y, x + w, y + h)
        page.insert_image(img_rect, filename=image_path)
    except Exception as e:
        print(f"[template_renderer] 嵌入图片失败: {image_path} — {e}")


def _embed_image_full_page(page, image_path: str, width_pt: float, height_pt: float, opacity: float = 1.0):
    """
    将背景图片以全尺寸嵌入 PDF 页面，支持透明度。
    """
    if not image_path or not os.path.isfile(image_path):
        return
    ext = os.path.splitext(image_path)[1].lower()
    if ext not in [".png", ".jpg", ".jpeg"]:
        return
    try:
        img_rect = fitz.Rect(0, 0, width_pt, height_pt)
        alpha = max(0.0, min(1.0, opacity))
        page.insert_image(img_rect, filename=image_path, alpha=alpha, keep_proportion=False)
    except Exception as e:
        print(f"[template_renderer] 背景图片嵌入失败: {e}")


_gradient_cache: dict = {}
"""V1.1 RC 收尾：保留为空缓存（已废弃，原 PNG 缓存逻辑删除）。

原实现：用 3× 超采样 PNG 嵌入作为背景 → 800% 放大暴露位图纹路。
Route B 修复：改用 export/pdf_exporter.draw_diagonal_4corner_gradient()
矢量 2D 网格（80×50 fillRect + width=0 无描边）→ 100% 矢量输出。
"""


def _draw_blue_gradient_bg(page, width_pt, height_pt):
    """绘制参考图风格的蓝色对角渐变背景（顶浅底深，主题蓝系）。

    V1.1 RC 收尾（Route B — PDF Native Shading）：
        - 4 角对角线 AxialShading（顶浅底深）
        - 100% 矢量（PDF Type 2 Shading），零 PNG 嵌入
        - 放大 800% 完全平滑（ΔRGB ≤ 1/255 @ 300dpi）
        - 通过 export/pdf_exporter 模块化实现
    """
    _render_bg_with_pymupdf(
        page, width_pt, height_pt,
        bg_style="blue_gradient",
    )


def _draw_background_solid(page, width_pt, height_pt, rgb):
    """绘制纯色背景"""
    page.draw_rect(
        fitz.Rect(0, 0, width_pt, height_pt),
        color=rgb, fill=rgb, width=0,
    )


def _is_dark_color(hex_color: str) -> bool:
    """判断 hex 颜色是否深色（亮度 < 0.5）"""
    try:
        r = int(hex_color[1:3], 16) / 255
        g = int(hex_color[3:5], 16) / 255
        b = int(hex_color[5:7], 16) / 255
        return (r + g + b) / 3.0 < 0.5
    except Exception:
        return False


def _draw_texture(page, width_pt: float, height_pt: float,
                  texture_type: str = "none", color: tuple = (0.85, 0.87, 0.90)):
    """
    在 PDF 页面上绘制纹理背景图案。
    支持：dot（点阵）、grid（网格）、diagonal（斜线）
    """
    if texture_type == "none":
        return

    try:
        if texture_type == "dot":
            spacing = _mm_to_points(3)
            dot_size = 0.8
            x = spacing
            while x < width_pt:
                y = spacing
                while y < height_pt:
                    page.draw_rect(
                        fitz.Rect(x, y, x + dot_size, y + dot_size),
                        color=color, fill=color, width=0,
                    )
                    y += spacing
                x += spacing

        elif texture_type == "grid":
            spacing = _mm_to_points(5)
            line_w = 0.3
            x = spacing
            while x < width_pt:
                page.draw_line(fitz.Point(x, 0), fitz.Point(x, height_pt), color=color, width=line_w)
                x += spacing
            y = spacing
            while y < height_pt:
                page.draw_line(fitz.Point(0, y), fitz.Point(width_pt, y), color=color, width=line_w)
                y += spacing

        elif texture_type == "diagonal":
            spacing = _mm_to_points(4)
            line_w = 0.3
            diag_len = math.sqrt(width_pt ** 2 + height_pt ** 2) + spacing
            start = -diag_len
            while start < diag_len:
                p1 = fitz.Point(start, 0)
                p2 = fitz.Point(start + diag_len, diag_len)
                page.draw_line(p1, p2, color=color, width=line_w)
                start += spacing
    except Exception as e:
        print(f"[template_renderer] 纹理绘制失败: {e}")


def _save_partial(doc, output_path):
    """安全保存 PDF 文档（用于错误恢复时保存部分渲染结果）。"""
    try:
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        doc.save(output_path)
        doc.close()
    except Exception as e:
        print(f"[renderer] 部分输出保存失败: {e}")


# ================================================================
# business_card — 名片模板（RC1 极简居中版）
# ================================================================

def render_business_card(output_path: str, data: dict,
                        logo_path: str = None, photo_path: str = None,
                        qr_image_path: str = None,
                        back_logo_path: str = None,
                        style_options: dict = None,
                        logo_width_mm: float = 21,
                        logo_right_mm: float = 5,
                        logo_top_mm: float = 4,
                        logo_shape: str = "square",
                        bg_image_path: str = None,
                        bg_image_opacity: float = 50,
                        bg_texture: str = "none",
                        bg_custom_color: str = "",
                        text_color: str = "#2C3E50",
                        text_secondary_color: str = "#7F8C8D",
                        render_sides: list = None,
                        progress_callback=None) -> str:
    """
    渲染名片模板 PDF（RC1 极简居中版）。

    尺寸：90 × 54 mm（标准名片），转换为 PDF 点：255 × 153 pt
    data 键对应 business_card.json 的 fields key：
      name_cn, name_en, title, phone, email
      back_logo, back_qr_image, back_qr_text, back_content

    图片参数（TPL-05）：
      logo_path  — LOGO 文件路径，支持 .png / .jpg / .jpeg
      photo_path — 预留，暂未使用
      qr_image_path — 背面二维码路径

    样式参数：
      style_options — 样式选项，包含 theme_color, bg_style
        theme_color: hex color string (default: "#4D7CFE")
        bg_style: "white" | "light_gray" | "gradient_vertical" | "gradient_horizontal" (default: "white")

    背景参数：
      bg_custom_color: 自定义背景色 hex，如 "#EEF2FF"
      bg_texture: 纹理类型 "none" | "dot" | "grid" | "diagonal"
      bg_image_path: 自定义背景图片文件路径
      bg_image_opacity: 背景图片透明度 0-100

    字体颜色：
      text_color: 主要文字颜色 hex (default: "#2C3E50")
      text_secondary_color: 次要文字颜色 hex (default: "#7F8C8D")

    双面渲染：
      render_sides: 要渲染的面列表，如 ["front"] 或 ["front", "back"]
                   默认 ["front", "back"]（双面）

    进度回调：
      progress_callback: 可选，签名 progress_callback(current_page, total_pages, status_text)
                        在关键渲染节点被调用

    输出：成功返回 output_path，失败抛出异常。
    """
    if render_sides is None:
        render_sides = ["front", "back"]

    width_pt = _mm_to_points(90)
    height_pt = _mm_to_points(55)

    # RC1 双面：data 兼容两种结构
    flat_data_for_side = {}
    for side in render_sides:
        side_data = data.get(side, {}) if isinstance(data, dict) and side in data else data
        if isinstance(side_data, dict):
            flat_data_for_side[side] = side_data
        else:
            flat_data_for_side[side] = data

    doc = fitz.open()
    total_pages = len(render_sides)
    error_info = None

    try:
        for page_idx, side in enumerate(render_sides):
            if progress_callback:
                progress_callback(page_idx, total_pages, f"正在渲染名片{'正面' if side == 'front' else '背面'}")

            page = doc.new_page(width=width_pt, height=height_pt)
            side_data = flat_data_for_side.get(side, data)

            if side == "front":
                # v4 设计：正面 = 个人信息，LOGO 在右上角，二维码在右下角
                _render_card_front(page, side_data, style_options, back_logo_path,
                                  logo_width_mm, logo_right_mm, logo_top_mm,
                                  bg_image_path, bg_image_opacity, bg_texture,
                                  bg_custom_color, text_color, text_secondary_color,
                                  width_pt, height_pt,
                                  qr_image_path=qr_image_path)
            elif side == "back":
                # v4 设计：背面 = 公司品牌，LOGO 居中
                _render_card_back(page, side_data, style_options,
                                 bg_image_path, bg_image_opacity, bg_texture,
                                 bg_custom_color, text_color, text_secondary_color,
                                 width_pt, height_pt,
                                 logo_path=logo_path)

        if progress_callback:
            progress_callback(total_pages, total_pages, "名片渲染完成")

    except Exception as e:
        error_info = f"名片渲染过程中出错: {e}"
        print(f"[renderer] {error_info}")
        # 尝试保存已渲染的部分
        _save_partial(doc, output_path)
        if error_info:
            raise RuntimeError(error_info)

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    doc.save(output_path)
    doc.close()
    return output_path


# ================================================================
# 名片双面渲染辅助函数（RC1 极简居中版）
# ================================================================

def _render_card_front(page, data, style_options, logo_path,
                       logo_width_mm, logo_right_mm, logo_top_mm,
                       bg_image_path, bg_image_opacity, bg_texture,
                       bg_custom_color, text_color, text_secondary_color,
                       width_pt, height_pt,
                       qr_image_path: str = None):
    """渲染名片正面 — 参考设计版（左侧：姓名+职位+联系方式+描述；右下：LOGO）

    设计原则：
      - 蓝色渐变背景为默认（与背面统一视觉）
      - 左侧 10% 边距对齐：姓名 → 职位（带下划线）→ 联系方式组 → 描述
      - LOGO 放右下角（保留原图比例）
      - 字号控制：姓名 16pt、职位 8pt、联系方式 7pt、描述 7pt
      - 深色背景上文字统一用白色 / 浅灰
    """
    if style_options is None:
        style_options = {}
    theme_color = style_options.get("theme_color", "#4D7CFE")
    bg_style = style_options.get("bg_style", "blue_gradient")

    # ── 背景 ──
    has_bg_image = bool(bg_image_path and os.path.isfile(bg_image_path))
    if bg_custom_color:
        cr = int(bg_custom_color[1:3], 16) / 255
        cg = int(bg_custom_color[3:5], 16) / 255
        cb = int(bg_custom_color[5:7], 16) / 255
        bg_fill = (cr, cg, cb)
        _draw_background_solid(page, width_pt, height_pt, bg_fill)
    elif bg_style == "blue_gradient":
        _draw_blue_gradient_bg(page, width_pt, height_pt)
    elif bg_style == "light_gray":
        _draw_background_solid(page, width_pt, height_pt, (0.96, 0.96, 0.97))
    elif bg_style == "gradient_vertical":
        _draw_background_solid(page, width_pt, height_pt, (0.96, 0.97, 1.0))
    elif bg_style == "gradient_horizontal":
        _draw_background_solid(page, width_pt, height_pt, (0.97, 0.96, 1.0))
    else:
        _draw_background_solid(page, width_pt, height_pt, (1, 1, 1))

    if has_bg_image:
        _embed_image_full_page(page, bg_image_path, width_pt, height_pt,
                               opacity=bg_image_opacity / 100)

    # ── 文字颜色（深色背景默认白字，浅色背景用 text_color）──
    is_dark_bg = (bg_style == "blue_gradient") or (bg_custom_color and _is_dark_color(bg_custom_color))
    if is_dark_bg:
        text_primary = (1.0, 1.0, 1.0)
        text_sec = (0.85, 0.88, 0.95)
        accent = (1.0, 1.0, 1.0)
    else:
        text_primary = _hex_to_rgb(text_color)
        text_sec = _hex_to_rgb(text_secondary_color)
        accent = _hex_to_rgb(theme_color)

    # ── 字号（用户要求"字体不要太大"+"变细"，主标题用 Bold，次要内容用 Regular）──
    size_name = 16.0
    size_title = 8.0
    size_contact = 5.5   # V1.1 RC 收尾：联系方式缩小 + 变细
    size_description = 5.5  # V1.1 RC 收尾：描述缩小 + 变细
    line_gap_contact = 7.5  # V1.1 RC 收尾：4 项联系方式紧凑排布（line_gap 缩小）
    line_gap_description = 8.0

    # ── 左右对称边距（5% width，LOGO/QR/文本全部一致）──
    margin_left_pt = width_pt * 0.05
    margin_right_pt = width_pt * 0.05
    left_x = margin_left_pt
    right_edge = width_pt - margin_right_pt
    content_w = right_edge - left_x

    # ── V1.1 RC 收尾：布局重构 — 上组（姓名+职位+下划线）+ 下组（联系方式+描述）两段式 ──
    # 上组从顶部 ~10% 起，下组从 ~50% 起，中间留出大间距（参考图三）
    # 描述宽度限制到 2/3 名片宽度
    desc_max_w = width_pt * 2.0 / 3.0

    # ── 1. 姓名（左对齐，从 10% 卡高起，16pt 粗）──
    cur_y = height_pt * 0.10
    name_cn = data.get("name_cn", "").strip()
    if name_cn:
        baseline_pt = cur_y + size_name
        text_to_draw = _truncate_to_width(name_cn, content_w, size_name)
        _insert_text_safe(page, text_to_draw, left_x, baseline_pt,
                          fontsize=size_name, color=text_primary)
        cur_y = baseline_pt + 4  # 姓名→职位 小间距

    # ── 2. 职位（带下划线，紧贴姓名）──
    title_text = data.get("title", "").strip()
    if title_text:
        baseline_pt = cur_y + size_title + 2
        text_to_draw = _truncate_to_width(title_text, content_w, size_title)
        _insert_text_safe(page, text_to_draw, left_x, baseline_pt,
                          fontsize=size_title, color=text_sec, regular=True)
        # 下划线（长度按职位文字宽度）
        underline_w = _measure_text_width(text_to_draw, size_title) * 0.6
        underline_w = min(underline_w, content_w * 0.5)
        line_y = baseline_pt + 4
        page.draw_line(
            fitz.Point(left_x, line_y),
            fitz.Point(left_x + underline_w, line_y),
            color=accent, width=0.6,
        )
        # 上组结束，不再累加 cur_y（直接跳到下组）

    # ── 3. 联系方式（4 项：电话/邮箱/网站/地址，从 51% 卡高起 — 紧贴描述）──
    # V1.1 RC 收尾：图标 PNG 嵌入 = size_contact（5.5pt），字符 85% 画布 = 视觉 4.7pt Bold
    #            等价于 ~5.2pt Regular 视觉重量 — 与右边信息同大，只稍加粗
    CONTACT_ICON_SIZE = 5.5   # pt（与 size_contact 文字同大）
    ICON_GAP = 2.0            # pt（图标与文字间距，紧贴）
    ICON_PX = 64              # PNG 画布像素
    icon_color = (1.0, 1.0, 1.0) if is_dark_bg else _hex_to_rgb(theme_color)
    cur_y = height_pt * 0.51
    contact_items = []
    phone   = data.get("phone", "").strip()
    email   = data.get("email", "").strip()
    website = data.get("website", "").strip()
    address = data.get("address", "").strip()
    if phone:   contact_items.append(("phone",   phone))
    if email:   contact_items.append(("email",   email))
    if website: contact_items.append(("website", website))
    if address: contact_items.append(("address", address))

    for icon_type, val in contact_items:
        baseline_pt = cur_y + size_contact
        # V1.1 收尾：图标(hebo)与文字(msyh)字体不同，视觉中心不对齐
        # hebo T cap center = 0.3645em → 2.005pt @5.5pt
        # msyh Latin center = (asc+desc)/2 = 0.3982em → 2.190pt @5.5pt
        # 图标需下移 0.185pt 使视觉中心与文字对齐 → 系数 0.0337
        icon_y = baseline_pt - 0.034 * size_contact
        icon_x = left_x
        try:
            _draw_text_icon(
                page, icon_type,
                x_pt=icon_x,
                y_pt=icon_y,
                size_pt=CONTACT_ICON_SIZE,
                color=icon_color,
            )
        except Exception as e:
            print(f"[renderer] 矢量图标 {icon_type} 失败: {e}")
        # value 在 icon 右侧 2pt（与缩小后的图标匹配）
        val_x = left_x + CONTACT_ICON_SIZE + ICON_GAP
        val_max_w = right_edge - val_x - 1
        if val_max_w <= 0:
            cur_y = baseline_pt + line_gap_contact - size_contact
            continue
        text_to_draw = _truncate_to_width(val, val_max_w, size_contact)
        _insert_text_safe(page, text_to_draw, val_x, baseline_pt,
                          fontsize=size_contact, color=text_primary, regular=True)
        cur_y = baseline_pt + line_gap_contact - size_contact

    # ── 4. 描述（强制从 75% 卡高起，宽度限制到 2/3 名片宽度）──
    description = data.get("description", "").strip() or data.get("back_content", "").strip()
    if description:
        cur_y = height_pt * 0.75
        # 简单按 \n 拆分，单行超宽自动换行（换行宽度 = 2/3 名片宽度）
        all_lines = []
        for line in description.split("\n"):
            wrapped = _wrap_text_in_width(line, size_description, desc_max_w)
            all_lines.extend(wrapped)
        for line in all_lines:
            baseline_pt = cur_y + size_description
            _insert_text_safe(page, line, left_x, baseline_pt,
                              fontsize=size_description, color=text_sec, regular=True)
            cur_y = baseline_pt + line_gap_description - size_description

    # ── 5. LOGO（右上角，保留原图比例）──
    placeholder_color = (1.0, 1.0, 1.0) if is_dark_bg else (0.2, 0.2, 0.3)
    has_logo = bool(logo_path and os.path.isfile(logo_path))
    logo_insert_ok = False
    logo_w_pt = logo_width_mm * 2.835 if logo_width_mm > 0 else width_pt * 0.16
    logo_h_pt = logo_w_pt  # placeholder 用 1:1
    if has_logo:
        try:
            from PIL import Image as _PILImg
            with _PILImg.open(logo_path) as _pimg:
                _w_native, _h_native = _pimg.size
            native_aspect = (_w_native / _h_native) if _h_native > 0 else 1.0
        except Exception:
            native_aspect = 1.0
        # LOGO 大小：默认 12mm 宽（更显眼）
        logo_w_pt = min((logo_width_mm if logo_width_mm > 0 else 12) * 2.835, width_pt * 0.30)
        logo_h_pt = logo_w_pt / native_aspect
        if logo_h_pt > height_pt * 0.18:
            logo_h_pt = height_pt * 0.18
            logo_w_pt = logo_h_pt * native_aspect
        margin_right_pt = logo_right_mm * 2.835 if logo_right_mm > 0 else width_pt * 0.05
        margin_top_pt = logo_top_mm * 2.835 if logo_top_mm > 0 else height_pt * 0.05
        logo_right = width_pt - margin_right_pt
        logo_top = margin_top_pt
        logo_x = logo_right - logo_w_pt
        try:
            img_rect = fitz.Rect(logo_x, logo_top, logo_x + logo_w_pt, logo_top + logo_h_pt)
            logo_insert_ok = _safe_insert_image(page, logo_path, img_rect)
            if not logo_insert_ok:
                print(f"[renderer] 正面 LOGO 插入失败: {logo_path}")
        except Exception as e:
            print(f"[renderer] 嵌入 LOGO 失败: {e}")

    # ── V1.1 RC 收尾：LOGO 占位框（区分"未上传"和"加载失败"）──
    if not logo_insert_ok:
        logo_w_pt = min(width_pt * 0.16, 36.0)
        logo_h_pt = logo_w_pt
        margin_right_pt = width_pt * 0.05
        margin_top_pt = height_pt * 0.05
        logo_x = width_pt - margin_right_pt - logo_w_pt
        logo_y = margin_top_pt
        # 状态文案：有路径但加载失败 vs 完全没路径
        status_text = "LOGO ✗ 加载失败" if has_logo else "LOGO"
        ph_color = (1.0, 0.55, 0.55) if has_logo else placeholder_color  # 失败时红色提示
        # 手动画虚线 4 边（fitz dashes 参数兼容性差）
        for offset in range(0, int(logo_w_pt * 2 + logo_h_pt * 2), 5):
            # top
            if offset < logo_w_pt:
                page.draw_line(
                    fitz.Point(logo_x + offset, logo_y),
                    fitz.Point(min(logo_x + offset + 3, logo_x + logo_w_pt), logo_y),
                    color=ph_color, width=0.5,
                )
            # bottom
            if offset < logo_w_pt:
                page.draw_line(
                    fitz.Point(logo_x + offset, logo_y + logo_h_pt),
                    fitz.Point(min(logo_x + offset + 3, logo_x + logo_w_pt), logo_y + logo_h_pt),
                    color=ph_color, width=0.5,
                )
            # left
            if offset < logo_h_pt:
                page.draw_line(
                    fitz.Point(logo_x, logo_y + offset),
                    fitz.Point(logo_x, min(logo_y + offset + 3, logo_y + logo_h_pt)),
                    color=ph_color, width=0.5,
                )
            # right
            if offset < logo_h_pt:
                page.draw_line(
                    fitz.Point(logo_x + logo_w_pt, logo_y + offset),
                    fitz.Point(logo_x + logo_w_pt, min(logo_y + offset + 3, logo_y + logo_h_pt)),
                    color=ph_color, width=0.5,
                )
        # 占位文字
        _insert_text_safe(
            page, status_text,
            logo_x + logo_w_pt / 2 - len(status_text) * 2.0,
            logo_y + logo_h_pt / 2 + 3,
            fontsize=7, color=ph_color, regular=True,
        )

    # ── 6. 二维码（右侧，与左侧信息块中部对齐，参考图二风格，TPL-05）──
    has_qr = bool(qr_image_path and os.path.isfile(qr_image_path))
    qr_insert_ok = False
    qr_w_pt = width_pt * 0.18
    qr_h_pt = qr_w_pt
    if has_qr:
        try:
            from PIL import Image as _PILImg
            with _PILImg.open(qr_image_path) as _pimg:
                _qw_native, _qh_native = _pimg.size
            qr_aspect = (_qw_native / _qh_native) if _qh_native > 0 else 1.0
        except Exception:
            qr_aspect = 1.0
        qr_h_pt = min(height_pt * 0.24, 36.0)
        qr_w_pt = qr_h_pt * qr_aspect
        if qr_w_pt > width_pt * 0.22:
            qr_w_pt = width_pt * 0.22
            qr_h_pt = qr_w_pt / qr_aspect
        # V1.1 RC 收尾：二维码下移（60% → 75%），与左侧描述中部对齐
        qr_right = right_edge
        qr_center_y = height_pt * 0.75
        qr_x = qr_right - qr_w_pt
        qr_y = qr_center_y - qr_h_pt / 2
        try:
            img_rect = fitz.Rect(qr_x, qr_y, qr_x + qr_w_pt, qr_y + qr_h_pt)
            qr_insert_ok = _safe_insert_image(page, qr_image_path, img_rect)
        except Exception as e:
            print(f"[renderer] 嵌入二维码失败: {e}")

    # ── V1.1 RC 收尾：二维码占位框（未上传时显示虚线提示）──
    if not qr_insert_ok:
        qr_w_pt = min(width_pt * 0.18, 32.0)
        qr_h_pt = qr_w_pt
        qr_right = right_edge
        qr_center_y = height_pt * 0.75
        qr_x = qr_right - qr_w_pt
        qr_y = qr_center_y - qr_h_pt / 2
        # 手动画虚线 4 边
        for offset in range(0, int(qr_w_pt * 2 + qr_h_pt * 2), 5):
            if offset < qr_w_pt:
                page.draw_line(
                    fitz.Point(qr_x + offset, qr_y),
                    fitz.Point(min(qr_x + offset + 3, qr_x + qr_w_pt), qr_y),
                    color=placeholder_color, width=0.5,
                )
                page.draw_line(
                    fitz.Point(qr_x + offset, qr_y + qr_h_pt),
                    fitz.Point(min(qr_x + offset + 3, qr_x + qr_w_pt), qr_y + qr_h_pt),
                    color=placeholder_color, width=0.5,
                )
            if offset < qr_h_pt:
                page.draw_line(
                    fitz.Point(qr_x, qr_y + offset),
                    fitz.Point(qr_x, min(qr_y + offset + 3, qr_y + qr_h_pt)),
                    color=placeholder_color, width=0.5,
                )
                page.draw_line(
                    fitz.Point(qr_x + qr_w_pt, qr_y + offset),
                    fitz.Point(qr_x + qr_w_pt, min(qr_y + offset + 3, qr_y + qr_h_pt)),
                    color=placeholder_color, width=0.5,
                )
        _insert_text_safe(
            page, "QR", qr_x + qr_w_pt / 2 - 5, qr_y + qr_h_pt / 2 + 3,
            fontsize=8, color=placeholder_color, regular=True,
        )


def _render_card_back(page, data, style_options,
                      bg_image_path, bg_image_opacity, bg_texture,
                      bg_custom_color, text_color, text_secondary_color,
                      width_pt, height_pt,
                      logo_path: str = None, qr_image_path: str = None):
    """渲染名片背面 — 参考设计版（居中 LOGO + 公司 + SLOGAN）

    设计原则：
      - 蓝色渐变背景（与正面统一）
      - LOGO 居中（顶部 30% 处）
      - 公司名居中（16pt，白色）
      - SLOGAN 居中（8pt，字间距 0.4em，白色半透明）
      - 整体节奏：LOGO → 大间隔 → 公司 → 小间隔 → SLOGAN
    """
    if style_options is None:
        style_options = {}
    theme_color = style_options.get("theme_color", "#4D7CFE")
    bg_style = style_options.get("bg_style", "blue_gradient")

    # ── 背景 ──
    has_bg_image = bool(bg_image_path and os.path.isfile(bg_image_path))
    if bg_custom_color:
        cr = int(bg_custom_color[1:3], 16) / 255
        cg = int(bg_custom_color[3:5], 16) / 255
        cb = int(bg_custom_color[5:7], 16) / 255
        _draw_background_solid(page, width_pt, height_pt, (cr, cg, cb))
    elif bg_style == "blue_gradient":
        _draw_blue_gradient_bg(page, width_pt, height_pt)
    elif bg_style == "light_gray":
        _draw_background_solid(page, width_pt, height_pt, (0.96, 0.96, 0.97))
    elif bg_style == "gradient_vertical":
        _draw_background_solid(page, width_pt, height_pt, (0.96, 0.97, 1.0))
    elif bg_style == "gradient_horizontal":
        _draw_background_solid(page, width_pt, height_pt, (0.97, 0.96, 1.0))
    else:
        _draw_background_solid(page, width_pt, height_pt, (1, 1, 1))

    if has_bg_image:
        _embed_image_full_page(page, bg_image_path, width_pt, height_pt,
                               opacity=bg_image_opacity / 100)

    # ── 文字色（深色背景用白字）──
    is_dark_bg = (bg_style == "blue_gradient") or (bg_custom_color and _is_dark_color(bg_custom_color))
    if is_dark_bg:
        text_primary = (1.0, 1.0, 1.0)
        text_sec = (0.80, 0.85, 0.95)
    else:
        text_primary = _hex_to_rgb(text_color)
        text_sec = _hex_to_rgb(text_secondary_color)

    # ── 居中布局 ──
    center_x = width_pt * 0.50
    margin_side_pct = 0.10
    content_w = width_pt * (1 - 2 * margin_side_pct)

    size_company = 16.0
    size_slogan = 8.0

    # ── 1. LOGO（顶部 28% 居中，保留原图比例，放大）──
    has_logo = bool(logo_path and os.path.isfile(logo_path))
    logo_insert_ok = False
    if has_logo:
        try:
            from PIL import Image as _PILImg
            with _PILImg.open(logo_path) as _pimg:
                _w_native, _h_native = _pimg.size
            native_aspect = (_w_native / _h_native) if _h_native > 0 else 1.0
        except Exception as e:
            print(f"[renderer] LOGO 加载失败 {logo_path}: {e}")
            native_aspect = 1.0
        # V1.1 RC 收尾：放大到 22% 卡高（约 33pt），宽限 35%
        logo_h_pt = min(height_pt * 0.22, 34.0)
        logo_w_pt = logo_h_pt * native_aspect
        if logo_w_pt > width_pt * 0.35:
            logo_w_pt = width_pt * 0.35
            logo_h_pt = logo_w_pt / native_aspect
        logo_center_y = height_pt * 0.28
        logo_x = center_x - logo_w_pt / 2
        logo_top = logo_center_y - logo_h_pt / 2
        try:
            img_rect = fitz.Rect(logo_x, logo_top, logo_x + logo_w_pt, logo_top + logo_h_pt)
            logo_insert_ok = _safe_insert_image(page, logo_path, img_rect)
        except Exception as e:
            print(f"[renderer] 嵌入背面 LOGO 失败: {e}")

    # ── 2. 公司名称（居中，16pt）──
    company_text = data.get("company", "").strip()
    if company_text:
        baseline_pt = height_pt * 0.55
        text_to_draw = _truncate_to_width(company_text, content_w, size_company)
        # 加宽字间距（手动插入空格 — PyMuPDF TextWriter 暂不直接支持 letter-spacing）
        spaced = _letter_spaced_text(text_to_draw, extra_pt=1.0, fontsize=size_company)
        text_w = _measure_text_width(spaced, size_company)
        _insert_text_safe(page, spaced, center_x - text_w / 2, baseline_pt,
                          fontsize=size_company, color=text_primary)

    # ── 3. SLOGAN（居中，8pt，字间距宽，变细）──
    slogan_text = data.get("slogan", "").strip()
    if slogan_text:
        baseline_pt = height_pt * 0.66
        spaced = _letter_spaced_text(slogan_text, extra_pt=0.5, fontsize=size_slogan)
        text_w = _measure_text_width(spaced, size_slogan)
        _insert_text_safe(page, spaced, center_x - text_w / 2, baseline_pt,
                          fontsize=size_slogan, color=text_sec, regular=True)
        # V1.1 RC 收尾：二维码已迁到正面右下角，背面不再渲染


def _letter_spaced_text(text: str, extra_pt: float = 1.0, fontsize: float = 12.0) -> str:
    """为文本加宽字间距（用普通空格占位 — 简单稳定方案）。"""
    if not text:
        return text
    # 估算每个空格占 extra_pt 宽度 ≈ 0.6×字号宽度
    space_w = fontsize * 0.6
    n_spaces = max(1, int(extra_pt / space_w)) if extra_pt > 0 else 1
    filler = " " * n_spaces
    parts = text.split(" ")
    return filler.join(parts)


# ================================================================
# notice — 公告模板
# ================================================================

def render_notice(output_path: str, data: dict, image_path: str = None,
                  style: dict = None, progress_callback=None) -> str:
    """
    渲染公告模板 PDF（A4 尺寸，自动分页）。
    """
    style = style or {}
    theme_color = style.get("theme_color", "#2C3E6B")
    bar_position = style.get("bar_position", "top")
    bg_style_val = style.get("bg_style", "white")
    bg_custom_color = style.get("bg_custom_color", "")
    font_style = style.get("font_style", "formal")

    theme_rgb = _hex_to_rgb(theme_color)
    gray_rgb  = (0.55, 0.55, 0.55)
    light_rgb = _hex_to_rgb(theme_color)

    if font_style == "modern":
        title_fontsize = 20
        body_fontsize = 11
        line_gap_mm = 5
        title_underline_width = 60
        title_underline_weight = 0.8
    elif font_style == "bold":
        title_fontsize = 28
        body_fontsize = 13
        line_gap_mm = 7
        title_underline_width = 100
        title_underline_weight = 2.0
    else:
        title_fontsize = 24
        body_fontsize = 12
        line_gap_mm = 6
        title_underline_width = 80
        title_underline_weight = 1.0

    width_pt = _mm_to_points(210)
    height_pt = _mm_to_points(297)
    margin = _mm_to_points(25)
    content_width = width_pt - 2 * margin
    bottom_margin = margin + _mm_to_points(10)
    max_y = height_pt - bottom_margin

    if bg_custom_color:
        bg_fill = _hex_to_rgb(bg_custom_color)
    elif bg_style_val == "light_gray":
        bg_fill = _hex_to_rgb("#F5F5F5")
    elif bg_style_val == "light_blue":
        bg_fill = _hex_to_rgb("#EBF0FA")
    elif bg_style_val == "gradient_vertical":
        bg_fill = (1, 1, 1)
    else:
        bg_fill = (1, 1, 1)

    doc = fitz.open()
    page = doc.new_page(width=width_pt, height=height_pt)
    page_count = 1
    error_info = None

    try:
        def _render_page_bg(p):
            p.draw_rect(fitz.Rect(0, 0, width_pt, height_pt),
                        color=bg_fill, fill=bg_fill, width=0)
            if bg_style_val == "gradient_vertical" and not bg_custom_color:
                steps = 40
                top_rgb = (1, 1, 1)
                bottom_rgb = _hex_to_rgb("#F0F0F5")
                step_h = height_pt / steps
                for i in range(steps):
                    cr = top_rgb[0] + (bottom_rgb[0] - top_rgb[0]) * i / steps
                    cg = top_rgb[1] + (bottom_rgb[1] - top_rgb[1]) * i / steps
                    cb = top_rgb[2] + (bottom_rgb[2] - top_rgb[2]) * i / steps
                    p.draw_rect(
                        fitz.Rect(0, i * step_h, width_pt, (i + 1) * step_h),
                        color=(cr, cg, cb), fill=(cr, cg, cb), width=0
                    )

        def _render_bar(p):
            bar_h = _mm_to_points(2)
            if bar_position == "top":
                p.draw_rect(
                    fitz.Rect(margin, margin, width_pt - margin, margin + bar_h),
                    color=theme_rgb, fill=theme_rgb, width=0
                )
            elif bar_position == "bottom":
                p.draw_rect(
                    fitz.Rect(margin, height_pt - margin - bar_h, width_pt - margin, height_pt - margin),
                    color=theme_rgb, fill=theme_rgb, width=0
                )
            elif bar_position == "left":
                bar_w = _mm_to_points(3)
                p.draw_rect(
                    fitz.Rect(margin, margin, margin + bar_w, height_pt - margin),
                    color=theme_rgb, fill=theme_rgb, width=0
                )

        def _render_page_header(p):
            _render_page_bg(p)
            _render_bar(p)
            header_y = margin + _mm_to_points(2)
            if bar_position == "top":
                header_y = margin + _mm_to_points(4) + _mm_to_points(2)
            title_text = data.get("title", "").strip()
            if title_text:
                _insert_text_safe(p, title_text, margin, header_y + 10,
                                 fontsize=10, color=gray_rgb)
                header_y += _mm_to_points(12)
            p.draw_line(
                fitz.Point(margin, header_y),
                fitz.Point(width_pt - margin, header_y),
                color=light_rgb, width=0.3,
            )
            return header_y + _mm_to_points(8)

        _render_page_bg(page)
        _render_bar(page)

        def _new_page():
            nonlocal page, page_count
            page = doc.new_page(width=width_pt, height=height_pt)
            page_count += 1
            header_bottom = _render_page_header(page)
            if progress_callback:
                progress_callback(page_count, -1, f"自动分页：第 {page_count} 页")
            return header_bottom

        def _ensure_space(needed_pt: float):
            nonlocal page, y
            if y + needed_pt > max_y:
                y = _new_page()

        if progress_callback:
            progress_callback(1, -1, "正在渲染公告首页")

        if image_path and os.path.isfile(image_path):
            img_w_mm = 25
            img_h_mm = 25
            img_x_mm = 210 - 25 - img_w_mm
            img_y_mm = 10
            _embed_image_in_page(
                page, image_path=image_path,
                x_mm=img_x_mm, y_mm=img_y_mm,
                width_mm=img_w_mm, height_mm=img_h_mm,
            )

        if bar_position == "top":
            y = margin + _mm_to_points(2) + _mm_to_points(18)
        else:
            y = margin + _mm_to_points(18)

        title = data.get("title", "").strip()
        if title:
            _insert_text_safe(page, title, margin, y,
                             fontsize=title_fontsize, color=(0.1, 0.1, 0.1))
            y += _mm_to_points(10)
            page.draw_line(
                fitz.Point(margin, y),
                fitz.Point(margin + _mm_to_points(title_underline_width), y),
                color=theme_rgb, width=title_underline_weight,
            )
            y += _mm_to_points(8)

        date = data.get("date", "").strip()
        if date:
            _insert_text_safe(page, date, margin, y,
                             fontsize=10, color=gray_rgb)
            y += _mm_to_points(10)

        page.draw_line(
            fitz.Point(margin, y),
            fitz.Point(width_pt - margin, y),
            color=light_rgb, width=0.5,
        )
        y += _mm_to_points(12)

        body = data.get("body", "").strip()
        if body:
            line_gap = _mm_to_points(line_gap_mm)
            paragraphs = body.split("\n")
            for para in paragraphs:
                para = para.strip()
                if not para:
                    y += line_gap * 0.5
                    continue
                wrapped_lines = _wrap_text_in_width(para, body_fontsize, content_width)
                for wl in wrapped_lines:
                    _ensure_space(line_gap)
                    _insert_text_safe(page, wl, margin, y,
                                     fontsize=body_fontsize, color=(0.2, 0.2, 0.2))
                    y += line_gap
            y += _mm_to_points(8)

        issuer = data.get("issuer", "").strip()
        if issuer:
            _ensure_space(_mm_to_points(15))
            _insert_text_safe(
                page, issuer,
                width_pt - margin - _mm_to_points(70),
                y,
                fontsize=11, color=gray_rgb,
            )

        if progress_callback:
            progress_callback(page_count, page_count, "公告渲染完成")

    except Exception as e:
        error_info = f"公告渲染过程中出错: {e}"
        print(f"[renderer] {error_info}")
        _save_partial(doc, output_path)
        if error_info:
            raise RuntimeError(error_info)

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    doc.save(output_path)
    doc.close()
    return output_path


# ================================================================
# product_spec — 产品规格模板
# ================================================================

def render_product_spec(output_path: str, data: dict, image_path: str = None,
                        style: dict = None, progress_callback=None) -> str:
    """
    渲染产品规格模板 PDF（A4 尺寸，自动分页）。
    """
    style = style or {}
    theme_color = style.get("theme_color", "#3355AA")
    header_style = style.get("header_style", "bar")
    bg_style_val = style.get("bg_style", "white")
    bg_custom_color = style.get("bg_custom_color", "")
    table_style = style.get("table_style", "striped")

    theme_rgb = _hex_to_rgb(theme_color)
    width_pt = _mm_to_points(210)
    height_pt = _mm_to_points(297)

    doc = fitz.open()
    page = doc.new_page(width=width_pt, height=height_pt)

    if bg_custom_color:
        bg_fill = _hex_to_rgb(bg_custom_color)
    elif bg_style_val == "light_gray":
        bg_fill = _hex_to_rgb("#F5F5F7")
    elif bg_style_val == "light_blue":
        bg_fill = _hex_to_rgb("#EBF0FA")
    else:
        bg_fill = (1, 1, 1)

    page.draw_rect(fitz.Rect(0, 0, width_pt, height_pt),
                   color=bg_fill, fill=bg_fill, width=0)

    accent_rgb = tuple(max(0, min(1, theme_rgb[i] * 0.85 + 0.15)) for i in range(3))
    gray_rgb  = (0.5, 0.5, 0.5)
    dark_rgb  = (0.15, 0.15, 0.15)

    margin = _mm_to_points(20)
    content_width = width_pt - 2 * margin
    bottom_margin = margin + _mm_to_points(10)
    max_y = height_pt - bottom_margin

    y = margin + _mm_to_points(5)
    error_info = None

    try:
        if progress_callback:
            progress_callback(1, -1, "正在渲染产品规格首页")

        def _new_page():
            nonlocal page, y
            page = doc.new_page(width=width_pt, height=height_pt)
            page.draw_rect(fitz.Rect(0, 0, width_pt, height_pt),
                           color=bg_fill, fill=bg_fill, width=0)
            y = margin + _mm_to_points(5)
            if progress_callback:
                progress_callback(doc.page_count, -1, f"自动分页：第 {doc.page_count} 页")
            return page

        def _ensure_space(needed_pt: float):
            nonlocal page, y
            if y + needed_pt > max_y:
                _new_page()

        product_name = data.get("product_name", "").strip()
        if product_name:
            title_fontsize = 22
            title_line_gap = _mm_to_points(8)
            has_image = image_path and os.path.isfile(image_path)
            title_max_w = (content_width - _mm_to_points(35)) if has_image else content_width
            title_lines = _wrap_text_in_width(product_name, title_fontsize, title_max_w)
            for tl in title_lines[:2]:
                _insert_text_safe(page, tl, margin, y,
                                 fontsize=title_fontsize, color=dark_rgb)
                y += title_line_gap
            y += _mm_to_points(2)

        version = data.get("version", "").strip()
        if version:
            ver_text = f"版本：{version}"
            ver_lines = _wrap_text_in_width(ver_text, 11, content_width)
            ver_line_gap = _mm_to_points(5)
            for vl in ver_lines:
                _insert_text_safe(page, vl, margin, y,
                                 fontsize=11, color=gray_rgb)
                y += ver_line_gap
            y += _mm_to_points(5)

        if image_path and os.path.isfile(image_path):
            img_w_mm = 30
            img_h_mm = 30
            img_x_mm = 210 - 20 - img_w_mm
            img_y_mm = 10
            _embed_image_in_page(
                page, image_path=image_path,
                x_mm=img_x_mm, y_mm=img_y_mm,
                width_mm=img_w_mm, height_mm=img_h_mm,
            )

        if header_style == "bar":
            title_bar_h = _mm_to_points(2)
            page.draw_rect(
                fitz.Rect(margin, y, width_pt - margin, y + title_bar_h),
                color=theme_rgb, fill=theme_rgb, width=0
            )
            y += title_bar_h + _mm_to_points(10)
        elif header_style == "color_block":
            block_h = _mm_to_points(12)
            page.draw_rect(
                fitz.Rect(margin, y, width_pt - margin, y + block_h),
                color=theme_rgb, fill=theme_rgb, width=0
            )
            y += block_h + _mm_to_points(6)

        description = data.get("description", "").strip()
        if description:
            _insert_text_safe(page, "▎ 产品描述", margin, y,
                             fontsize=9, color=theme_rgb)
            y += _mm_to_points(7)

            desc_fontsize = 11
            desc_line_gap = _mm_to_points(6)
            paragraphs = description.split("\n")
            for para in paragraphs:
                para = para.strip()
                if not para:
                    y += desc_line_gap * 0.5
                    continue
                wrapped_lines = _wrap_text_in_width(para, desc_fontsize, content_width)
                for wl in wrapped_lines:
                    _ensure_space(desc_line_gap)
                    _insert_text_safe(page, wl, margin, y,
                                     fontsize=desc_fontsize, color=dark_rgb)
                    y += desc_line_gap
            y += _mm_to_points(8)

        specs = data.get("specs", "")
        specs_list = []
        is_table_format = False

        if isinstance(specs, list) and specs:
            specs_list = specs
            is_table_format = True
        elif isinstance(specs, str) and specs.strip():
            for line in specs.strip().split("\n"):
                line = line.strip()
                if line:
                    specs_list.append(line)

        if specs_list:
            _insert_text_safe(page, "▎ 技术规格", margin, y,
                             fontsize=9, color=theme_rgb)
            y += _mm_to_points(7)

            line_gap = _mm_to_points(6)

            if is_table_format:
                list_fontsize = 10
                list_line_gap = _mm_to_points(5.5)
                content_width = width_pt - 2 * margin
                param_font_color = dark_rgb
                value_font_color = dark_rgb

                for row in specs_list:
                    if not isinstance(row, dict):
                        continue
                    param = row.get("param", "").strip()
                    value = row.get("value", "").strip()
                    if not param and not value:
                        continue

                    _ensure_space(list_line_gap)

                    if param and value:
                        display_text = f"{param}：{value}"
                    elif param:
                        display_text = param
                    else:
                        display_text = value

                    wrapped = _wrap_text_in_width(display_text, list_fontsize, content_width)
                    for wl in wrapped:
                        _insert_text_safe(page, wl, margin, y,
                                         fontsize=list_fontsize, color=param_font_color)
                        y += list_line_gap

            else:
                for para in specs_list:
                    if not para:
                        y += line_gap * 0.5
                        continue
                    display = f"• {para}" if not para.startswith(("•", "·", "-")) else para
                    max_chars = 50
                    while display:
                        _ensure_space(line_gap)
                        if len(display) <= max_chars:
                            _insert_text_safe(page, display, margin, y,
                                             fontsize=10.5, color=dark_rgb)
                            y += line_gap
                            break
                        else:
                            split_idx = max_chars
                            for i in range(max_chars - 1, max_chars - 15, -1):
                                if display[i] in (' ', '，', '。', '、', '；', '：'):
                                    split_idx = i + 1
                                    break
                            _insert_text_safe(page, display[:split_idx], margin, y,
                                             fontsize=10.5, color=dark_rgb)
                            y += line_gap
                            display = display[split_idx:].strip()

            if not is_table_format:
                sep_y = y + _mm_to_points(3)
                if sep_y < max_y:
                    page.draw_line(
                        fitz.Point(margin, sep_y),
                        fitz.Point(width_pt - margin, sep_y),
                        color=accent_rgb, width=0.5,
                    )

        if progress_callback:
            progress_callback(doc.page_count, doc.page_count, "产品规格渲染完成")

    except Exception as e:
        error_info = f"产品规格渲染过程中出错: {e}"
        print(f"[renderer] {error_info}")
        _save_partial(doc, output_path)
        if error_info:
            raise RuntimeError(error_info)

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    doc.save(output_path)
    doc.close()
    return output_path


# ================================================================
# contract — 合同协议模板
# ================================================================

def render_contract(output_path: str, data: dict, image_path: str = None,
                    style: dict = None, progress_callback=None) -> str:
    """
    渲染合同协议模板 PDF（A4 尺寸，自动分页）。
    """
    style = style or {}
    theme_color = style.get("theme_color", "#2C3E6B")
    header_style = style.get("header_style", "bar")
    bg_style_val = style.get("bg_style", "white")

    theme_rgb = _hex_to_rgb(theme_color)
    gray_rgb = (0.5, 0.5, 0.5)
    dark_rgb = (0.15, 0.15, 0.15)

    width_pt = _mm_to_points(210)
    height_pt = _mm_to_points(297)

    margin = _mm_to_points(25)
    content_width = width_pt - 2 * margin
    bottom_margin = margin + _mm_to_points(10)
    max_y = height_pt - bottom_margin

    if bg_style_val == "light_gray":
        bg_fill = _hex_to_rgb("#F5F5F5")
    elif bg_style_val == "light_blue":
        bg_fill = _hex_to_rgb("#EBF0FA")
    else:
        bg_fill = (1, 1, 1)

    doc = fitz.open()
    page = doc.new_page(width=width_pt, height=height_pt)
    page_count = 1
    error_info = None

    try:
        def _render_page_bg(p):
            p.draw_rect(fitz.Rect(0, 0, width_pt, height_pt),
                        color=bg_fill, fill=bg_fill, width=0)

        def _render_header_deco(p, y_pos):
            if header_style == "bar":
                bar_h = _mm_to_points(2)
                p.draw_rect(
                    fitz.Rect(margin, y_pos, width_pt - margin, y_pos + bar_h),
                    color=theme_rgb, fill=theme_rgb, width=0
                )
                return y_pos + bar_h + _mm_to_points(8)
            elif header_style == "color_block":
                block_h = _mm_to_points(12)
                p.draw_rect(
                    fitz.Rect(margin, y_pos, width_pt - margin, y_pos + block_h),
                    color=theme_rgb, fill=theme_rgb, width=0
                )
                return y_pos + block_h + _mm_to_points(6)
            return y_pos

        def _new_page():
            nonlocal page, page_count, y
            page = doc.new_page(width=width_pt, height=height_pt)
            page_count += 1
            _render_page_bg(page)
            y = margin + _mm_to_points(5)
            title_text = data.get("title", "").strip()
            if title_text:
                _insert_text_safe(page, title_text, margin, y + 8,
                                 fontsize=10, color=gray_rgb)
                y += _mm_to_points(14)
            page.draw_line(
                fitz.Point(margin, y),
                fitz.Point(width_pt - margin, y),
                color=theme_rgb, width=0.3,
            )
            y += _mm_to_points(8)
            if progress_callback:
                progress_callback(page_count, -1, f"自动分页：第 {page_count} 页")

        def _ensure_space(needed_pt: float):
            nonlocal page, y
            if y + needed_pt > max_y:
                _new_page()

        if progress_callback:
            progress_callback(1, -1, "正在渲染合同首页")

        _render_page_bg(page)

        y = margin + _mm_to_points(5)
        y = _render_header_deco(page, y)

        title = data.get("title", "").strip()
        if title:
            title_fontsize = 22
            title_lines = _wrap_text_in_width(title, title_fontsize, content_width)
            for tl in title_lines[:2]:
                _insert_text_safe(page, tl, margin, y,
                                 fontsize=title_fontsize, color=dark_rgb)
                y += _mm_to_points(9)
            y += _mm_to_points(3)

        contract_no = data.get("contract_no", "").strip()
        if contract_no:
            _insert_text_safe(page, f"合同编号：{contract_no}", margin, y,
                             fontsize=10, color=gray_rgb, regular=True)
            y += _mm_to_points(8)

        page.draw_line(
            fitz.Point(margin, y),
            fitz.Point(width_pt - margin, y),
            color=theme_rgb, width=0.5,
        )
        y += _mm_to_points(10)

        col_width = content_width / 2 - _mm_to_points(5)  # 减少列宽，增大间距
        party_a = truncate_text(data.get("party_a", "").strip(), max_chars=40)
        party_a_addr = data.get("party_a_addr", "").strip()
        party_b = truncate_text(data.get("party_b", "").strip(), max_chars=40)
        party_b_addr = data.get("party_b_addr", "").strip()

        info_fontsize = 11
        info_line_gap = _mm_to_points(6)

        y_left = y
        if party_a:
            _insert_text_safe(page, "甲方（发包方）", margin, y_left,
                             fontsize=9, color=theme_rgb)
            y_left += info_line_gap
            _insert_text_safe(page, party_a, margin, y_left,
                             fontsize=info_fontsize, color=dark_rgb)
            y_left += info_line_gap
        if party_a_addr:
            _insert_text_safe(page, "地址：", margin, y_left,
                             fontsize=9, color=gray_rgb, regular=True)
            y_left += _mm_to_points(5)
            draw_wrapped_text(
                page, party_a_addr,
                fitz.Rect(margin, y_left,
                          margin + col_width, max_y),
                fontsize=9, line_gap=_mm_to_points(4), regular=True
            )
            y_left += info_line_gap * 2

        x_right = margin + col_width + _mm_to_points(14)  # 加大列间距
        y_right = y
        if party_b:
            _insert_text_safe(page, "乙方（承包方）", x_right, y_right,
                             fontsize=9, color=theme_rgb)
            y_right += info_line_gap
            _insert_text_safe(page, party_b, x_right, y_right,
                             fontsize=info_fontsize, color=dark_rgb)
            y_right += info_line_gap
        if party_b_addr:
            right_col_width = width_pt - margin - x_right
            _insert_text_safe(page, "地址：", x_right, y_right,
                             fontsize=9, color=gray_rgb, regular=True)
            y_right += _mm_to_points(5)
            draw_wrapped_text(
                page, party_b_addr,
                fitz.Rect(x_right, y_right,
                          x_right + right_col_width, max_y),
                fontsize=9, line_gap=_mm_to_points(4), regular=True
            )
            y_right += info_line_gap * 2

        y = max(y_left, y_right) + _mm_to_points(6)

        page.draw_line(
            fitz.Point(margin, y),
            fitz.Point(width_pt - margin, y),
            color=theme_rgb, width=0.3,
        )
        y += _mm_to_points(10)

        terms = truncate_text(data.get("terms", "").strip(), max_chars=3000)
        if terms:
            _insert_text_safe(page, "合同条款", margin, y,
                             fontsize=12, color=dark_rgb)
            y += _mm_to_points(8)

            term_fontsize = 10.5
            term_line_gap = _mm_to_points(6)
            term_lines = terms.split("\n")
            term_num = 1
            for line in term_lines:
                line = line.strip()
                if not line:
                    continue
                numbered_text = f"第{term_num}条  {line}"
                term_num += 1
                wrapped = _wrap_text_in_width(numbered_text, term_fontsize, content_width)
                for wl in wrapped:
                    _ensure_space(term_line_gap)
                    _insert_text_safe(page, wl, margin, y,
                                     fontsize=term_fontsize, color=dark_rgb, regular=True)
                    y += term_line_gap
                y += _mm_to_points(3)

            y += _mm_to_points(5)

        amount = data.get("amount", "").strip()
        if amount:
            _ensure_space(_mm_to_points(15))
            _insert_text_safe(page, f"合同金额：{amount}", margin, y,
                             fontsize=13, color=theme_rgb)
            y += _mm_to_points(12)

        remark = data.get("remark", "").strip()
        if remark:
            _ensure_space(_mm_to_points(15))
            _insert_text_safe(page, "备注：", margin, y,
                             fontsize=10, color=gray_rgb, regular=True)
            remark_label_w = _measure_text_width("备注：", 10)
            draw_wrapped_text(
                page, remark,
                fitz.Rect(margin + remark_label_w, y,
                          margin + content_width, max_y),
                fontsize=10, line_gap=_mm_to_points(5.5), regular=True
            )
            y += _mm_to_points(10)

        _ensure_space(_mm_to_points(50))
        y += _mm_to_points(15)

        page.draw_line(
            fitz.Point(margin, y),
            fitz.Point(width_pt - margin, y),
            color=theme_rgb, width=0.3,
        )
        y += _mm_to_points(10)

        sign_col_width = content_width / 2 - _mm_to_points(5)
        _insert_text_safe(page, "甲方（签章）：", margin, y,
                         fontsize=11, color=dark_rgb)
        sign_line_y = y + _mm_to_points(20)
        page.draw_line(
            fitz.Point(margin, sign_line_y),
            fitz.Point(margin + sign_col_width, sign_line_y),
            color=gray_rgb, width=0.5,
        )

        x_right_sign = margin + sign_col_width + _mm_to_points(10)
        _insert_text_safe(page, "乙方（签章）：", x_right_sign, y,
                         fontsize=11, color=dark_rgb)
        page.draw_line(
            fitz.Point(x_right_sign, sign_line_y),
            fitz.Point(x_right_sign + sign_col_width, sign_line_y),
            color=gray_rgb, width=0.5,
        )

        y = sign_line_y + _mm_to_points(8)

        date = data.get("date", "").strip()
        if date:
            _insert_text_safe(page, f"签订日期：{date}", margin, y,
                             fontsize=10, color=gray_rgb, regular=True)

        if progress_callback:
            progress_callback(page_count, page_count, "合同渲染完成")

    except Exception as e:
        error_info = f"合同渲染过程中出错: {e}"
        print(f"[renderer] {error_info}")
        _save_partial(doc, output_path)
        if error_info:
            raise RuntimeError(error_info)

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    doc.save(output_path)
    doc.close()
    return output_path


# ================================================================
# invoice — 发票收据模板
# ================================================================

def render_invoice(output_path: str, data: dict, image_path: str = None,
                   style: dict = None, progress_callback=None) -> str:
    """
    渲染发票收据模板 PDF（A4 尺寸，自动分页）。
    """
    style = style or {}
    theme_color = style.get("theme_color", "#8B0000")
    border_style = style.get("border_style", "double")
    bg_style_val = style.get("bg_style", "white")

    theme_rgb = _hex_to_rgb(theme_color)
    gray_rgb = (0.5, 0.5, 0.5)
    dark_rgb = (0.15, 0.15, 0.15)

    width_pt = _mm_to_points(210)
    height_pt = _mm_to_points(297)

    margin = _mm_to_points(20)
    content_width = width_pt - 2 * margin
    bottom_margin = margin + _mm_to_points(10)
    max_y = height_pt - bottom_margin

    if bg_style_val == "light_gray":
        bg_fill = _hex_to_rgb("#F5F5F5")
    else:
        bg_fill = (1, 1, 1)

    doc = fitz.open()
    page = doc.new_page(width=width_pt, height=height_pt)
    page_count = 1
    error_info = None

    try:
        def _render_page_bg(p):
            p.draw_rect(fitz.Rect(0, 0, width_pt, height_pt),
                        color=bg_fill, fill=bg_fill, width=0)

        def _draw_border(p):
            if border_style == "double":
                outer_margin = _mm_to_points(8)
                p.draw_rect(
                    fitz.Rect(outer_margin, outer_margin,
                              width_pt - outer_margin, height_pt - outer_margin),
                    color=theme_rgb, fill=None, width=1.5
                )
                inner_margin = _mm_to_points(11)
                p.draw_rect(
                    fitz.Rect(inner_margin, inner_margin,
                              width_pt - inner_margin, height_pt - inner_margin),
                    color=theme_rgb, fill=None, width=0.5
                )
            elif border_style == "single":
                border_margin = _mm_to_points(10)
                p.draw_rect(
                    fitz.Rect(border_margin, border_margin,
                              width_pt - border_margin, height_pt - border_margin),
                    color=theme_rgb, fill=None, width=1.0
                )

        def _new_page():
            nonlocal page, page_count, y
            page = doc.new_page(width=width_pt, height=height_pt)
            page_count += 1
            _render_page_bg(page)
            _draw_border(page)
            y = margin + _mm_to_points(5)
            title_text = data.get("title", "").strip()
            if title_text:
                _insert_text_safe(page, title_text, margin, y + 8,
                                 fontsize=10, color=gray_rgb)
                y += _mm_to_points(14)
            page.draw_line(
                fitz.Point(margin, y),
                fitz.Point(width_pt - margin, y),
                color=theme_rgb, width=0.3,
            )
            y += _mm_to_points(8)
            if progress_callback:
                progress_callback(page_count, -1, f"自动分页：第 {page_count} 页")

        def _ensure_space(needed_pt: float):
            nonlocal page, y
            if y + needed_pt > max_y:
                _new_page()

        if progress_callback:
            progress_callback(1, -1, "正在渲染发票首页")

        _render_page_bg(page)
        _draw_border(page)

        y = margin + _mm_to_points(10)

        title = data.get("title", "发票").strip()
        if title:
            title_fontsize = 24
            title_w = _measure_text_width(title, title_fontsize)
            title_x = (width_pt - title_w) / 2
            _insert_text_safe(page, title, title_x, y,
                             fontsize=title_fontsize, color=theme_rgb)
            y += _mm_to_points(12)

        invoice_no = data.get("invoice_no", "").strip()
        date = data.get("date", "").strip()
        if invoice_no:
            _insert_text_safe(page, f"编号：{invoice_no}", margin, y,
                             fontsize=10, color=gray_rgb, regular=True)
        if date:
            date_text = f"日期：{date}"
            date_w = _measure_text_width(date_text, 10)
            _insert_text_safe(page, date_text, width_pt - margin - date_w, y,
                             fontsize=10, color=gray_rgb, regular=True)
        y += _mm_to_points(8)

        page.draw_line(
            fitz.Point(margin, y),
            fitz.Point(width_pt - margin, y),
            color=theme_rgb, width=0.5,
        )
        y += _mm_to_points(8)

        ADDRESS_MAX_LINES = 3
        ADDRESS_MAX_CHARS = 120
        col_width = content_width / 2 - _mm_to_points(3)
        seller = data.get("seller", "").strip()
        seller_addr = truncate_text(data.get("seller_addr", "").strip(), max_chars=ADDRESS_MAX_CHARS)
        buyer = data.get("buyer", "").strip()
        buyer_addr = truncate_text(data.get("buyer_addr", "").strip(), max_chars=ADDRESS_MAX_CHARS)

        info_fontsize = 10.5
        info_line_gap = _mm_to_points(5.5)

        y_left = y
        if seller:
            _insert_text_safe(page, "销售方", margin, y_left,
                             fontsize=9, color=theme_rgb)
            y_left += info_line_gap
            _insert_text_safe(page, seller, margin, y_left,
                             fontsize=info_fontsize, color=dark_rgb)
            y_left += info_line_gap
        if seller_addr:
            used_h = draw_wrapped_text(
                page, seller_addr,
                fitz.Rect(margin, y_left, margin + col_width, max_y),
                fontsize=9, line_gap=_mm_to_points(4),
                max_lines=ADDRESS_MAX_LINES, regular=True,
            )
            y_left += used_h + info_line_gap

        x_right = margin + col_width + _mm_to_points(6)
        y_right = y
        if buyer:
            _insert_text_safe(page, "购买方", x_right, y_right,
                             fontsize=9, color=theme_rgb)
            y_right += info_line_gap
            _insert_text_safe(page, buyer, x_right, y_right,
                             fontsize=info_fontsize, color=dark_rgb)
            y_right += info_line_gap
        if buyer_addr:
            used_h = draw_wrapped_text(
                page, buyer_addr,
                fitz.Rect(x_right, y_right, x_right + col_width, max_y),
                fontsize=9, line_gap=_mm_to_points(4),
                max_lines=ADDRESS_MAX_LINES, regular=True,
            )
            y_right += used_h + info_line_gap

        y = max(y_left, y_right) + _mm_to_points(6)

        page.draw_line(
            fitz.Point(margin, y),
            fitz.Point(width_pt - margin, y),
            color=theme_rgb, width=0.3,
        )
        y += _mm_to_points(8)

        items_raw = data.get("items", "")
        if isinstance(items_raw, list):
            items = items_raw[:10]
        elif isinstance(items_raw, str) and items_raw.strip():
            items = parse_items(items_raw.strip())[:10]
        else:
            items = []

        if items:
            items = items[:10]  # 最多 10 行
            _insert_text_safe(page, "明细项目", margin, y,
                             fontsize=11, color=dark_rgb)
            y += _mm_to_points(5)

            ITEM_NAME_WIDTH = 260  # 项目名称列宽（点）
            QTY_WIDTH = 80         # 数量列宽（点）
            PRICE_WIDTH = 120      # 单价列宽（点）

            # ── 表头矩形 ──
            header_h = _mm_to_points(8)
            page.draw_rect(
                fitz.Rect(margin, y, width_pt - margin, y + header_h),
                color=theme_rgb, fill=theme_rgb, width=0
            )
            # 表头文字用 Rect 文本框渲染（垂直居中）
            header_font_file = _get_cjk_font_file()
            header_fontsize = 9
            header_padding = _mm_to_points(2)
            # 垂直居中偏移：CJK 实际需要 fontsize×1.6 高度，差值的一半作为顶部偏移
            header_text_h = header_fontsize * 1.6
            header_v_offset = max(0, (header_h - header_text_h) / 2)
            # 项目名称
            page.insert_textbox(
                fitz.Rect(margin + header_padding, y + header_v_offset,
                          margin + ITEM_NAME_WIDTH, y + header_h - header_v_offset),
                "项目名称", fontsize=header_fontsize, color=(1, 1, 1),
                fontname="cjk", fontfile=header_font_file,
                align=fitz.TEXT_ALIGN_LEFT,
            )
            # 数量
            page.insert_textbox(
                fitz.Rect(margin + ITEM_NAME_WIDTH + header_padding, y + header_v_offset,
                          margin + ITEM_NAME_WIDTH + QTY_WIDTH, y + header_h - header_v_offset),
                "数量", fontsize=header_fontsize, color=(1, 1, 1),
                fontname="cjk", fontfile=header_font_file,
                align=fitz.TEXT_ALIGN_LEFT,
            )
            # 单价
            page.insert_textbox(
                fitz.Rect(margin + ITEM_NAME_WIDTH + QTY_WIDTH + header_padding, y + header_v_offset,
                          margin + ITEM_NAME_WIDTH + QTY_WIDTH + PRICE_WIDTH, y + header_h - header_v_offset),
                "单价", fontsize=header_fontsize, color=(1, 1, 1),
                fontname="cjk", fontfile=header_font_file,
                align=fitz.TEXT_ALIGN_LEFT,
            )
            y += header_h

            # ── 数据行 ──
            row_fontsize = 10
            row_padding = _mm_to_points(2)
            # insert_textbox 对 CJK 10pt 至少需要 fontsize×1.6 的内部高度
            cjk_line_h = row_fontsize * 1.6
            alt_fill = _hex_to_rgb("#F8F8FA")
            data_font_file = _get_cjk_font_file_regular()

            for idx, item in enumerate(items):
                item_name = truncate_text(item.get("name", ""), max_chars=50)
                item_qty = truncate_text(item.get("qty", ""), max_chars=10)
                item_price = truncate_text(item.get("price", ""), max_chars=15)

                # 计算行高（考虑换行 + CJK 字体最小行高）
                name_lines = _wrap_text_in_width(item_name, row_fontsize,
                                                 ITEM_NAME_WIDTH - 2 * row_padding)
                name_line_count = max(len(name_lines), 1)
                row_h = max(_mm_to_points(9),
                            name_line_count * cjk_line_h + 2 * row_padding)

                _ensure_space(row_h)

                # 交替背景色
                if idx % 2 == 1:
                    page.draw_rect(
                        fitz.Rect(margin, y, width_pt - margin, y + row_h),
                        color=alt_fill, fill=alt_fill, width=0
                    )

                # 垂直居中偏移（单行时）
                row_text_h = cjk_line_h * name_line_count
                row_v_offset = max(0, (row_h - row_text_h) / 2)

                # 项目名称（Rect 文本框，垂直居中 + 自动换行）
                page.insert_textbox(
                    fitz.Rect(margin + row_padding, y + row_v_offset,
                              margin + ITEM_NAME_WIDTH - row_padding, y + row_h - row_v_offset),
                    item_name, fontsize=row_fontsize, color=dark_rgb,
                    fontname="cjk", fontfile=data_font_file,
                    align=fitz.TEXT_ALIGN_LEFT,
                )

                # 数量（Rect 文本框，垂直居中）
                page.insert_textbox(
                    fitz.Rect(margin + ITEM_NAME_WIDTH + row_padding, y + row_v_offset,
                              margin + ITEM_NAME_WIDTH + QTY_WIDTH - row_padding, y + row_h - row_v_offset),
                    item_qty, fontsize=row_fontsize, color=dark_rgb,
                    fontname="cjk", fontfile=data_font_file,
                    align=fitz.TEXT_ALIGN_LEFT,
                )

                # 单价（Rect 文本框，垂直居中）
                page.insert_textbox(
                    fitz.Rect(margin + ITEM_NAME_WIDTH + QTY_WIDTH + row_padding, y + row_v_offset,
                              margin + ITEM_NAME_WIDTH + QTY_WIDTH + PRICE_WIDTH - row_padding, y + row_h - row_v_offset),
                    item_price, fontsize=row_fontsize, color=dark_rgb,
                    fontname="cjk", fontfile=data_font_file,
                    align=fitz.TEXT_ALIGN_LEFT,
                )

                # 行分隔线
                page.draw_line(
                    fitz.Point(margin, y + row_h),
                    fitz.Point(width_pt - margin, y + row_h),
                    color=gray_rgb, width=0.3,
                )
                y += row_h

            y += _mm_to_points(5)

        total_amount = data.get("total_amount", "").strip()
        if total_amount:
            _ensure_space(_mm_to_points(15))
            total_h = _mm_to_points(9)
            total_fill = tuple(min(1.0, theme_rgb[i] * 0.15 + 0.85) for i in range(3))
            page.draw_rect(
                fitz.Rect(margin, y, width_pt - margin, y + total_h),
                color=total_fill, fill=total_fill, width=0
            )
            # 合计文字垂直居中
            total_font_file = _get_cjk_font_file()
            total_fontsize = 12
            total_text_h = total_fontsize * 1.6
            total_v_offset = max(0, (total_h - total_text_h) / 2)
            page.insert_textbox(
                fitz.Rect(margin + _mm_to_points(2), y + total_v_offset,
                          width_pt - margin, y + total_h - total_v_offset),
                f"合计：{total_amount}", fontsize=total_fontsize, color=theme_rgb,
                fontname="cjk", fontfile=total_font_file,
                align=fitz.TEXT_ALIGN_LEFT,
            )
            y += total_h + _mm_to_points(8)

        remark = truncate_text(data.get("remark", "").strip(), max_chars=150)
        if remark:
            _ensure_space(_mm_to_points(12))
            _insert_text_safe(page, "备注：", margin, y,
                             fontsize=10, color=gray_rgb, regular=True)
            remark_label_w = _measure_text_width("备注：", 10)
            used_h = draw_wrapped_text(
                page, remark,
                fitz.Rect(margin + remark_label_w, y,
                          margin + content_width, max_y),
                fontsize=10, line_gap=_mm_to_points(5.5),
                max_lines=4, regular=True,
            )
            y += max(used_h, _mm_to_points(8)) + _mm_to_points(2)

        if progress_callback:
            progress_callback(page_count, page_count, "发票渲染完成")

    except Exception as e:
        error_info = f"发票渲染过程中出错: {e}"
        print(f"[renderer] {error_info}")
        _save_partial(doc, output_path)
        if error_info:
            raise RuntimeError(error_info)

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    doc.save(output_path)
    doc.close()
    return output_path


# ================================================================
# report — 分析报告模板
# ================================================================

def render_report(output_path: str, data: dict, image_path: str = None,
                  style: dict = None, progress_callback=None) -> str:
    """
    渲染分析报告模板 PDF（A4 尺寸，自动分页 + 页码）。
    """
    style = style or {}
    theme_color = style.get("theme_color", "#1A5276")
    header_style = style.get("header_style", "color_block")
    bg_style_val = style.get("bg_style", "white")

    theme_rgb = _hex_to_rgb(theme_color)
    gray_rgb = (0.5, 0.5, 0.5)
    dark_rgb = (0.15, 0.15, 0.15)
    light_theme = tuple(min(1.0, theme_rgb[i] * 0.15 + 0.85) for i in range(3))

    width_pt = _mm_to_points(210)
    height_pt = _mm_to_points(297)

    margin = _mm_to_points(25)
    content_width = width_pt - 2 * margin
    bottom_margin = margin + _mm_to_points(15)
    max_y = height_pt - bottom_margin

    if bg_style_val == "light_gray":
        bg_fill = _hex_to_rgb("#F5F5F7")
    else:
        bg_fill = (1, 1, 1)

    doc = fitz.open()
    error_info = None

    try:
        footer_text = data.get("footer_text", "").strip()

        def _render_page_bg(p):
            p.draw_rect(fitz.Rect(0, 0, width_pt, height_pt),
                        color=bg_fill, fill=bg_fill, width=0)

        def _render_footer(p, page_num):
            footer_y = height_pt - margin + _mm_to_points(2)
            page_text = f"— {page_num} —"
            page_w = _measure_text_width(page_text, 9)
            _insert_text_safe(p, page_text, (width_pt - page_w) / 2, footer_y,
                             fontsize=9, color=gray_rgb, regular=True)
            if footer_text:
                _insert_text_safe(p, footer_text, margin, footer_y,
                                 fontsize=8, color=gray_rgb, regular=True)

        def _render_header_deco(p, y_pos):
            if header_style == "bar":
                bar_h = _mm_to_points(2)
                p.draw_rect(
                    fitz.Rect(margin, y_pos, width_pt - margin, y_pos + bar_h),
                    color=theme_rgb, fill=theme_rgb, width=0
                )
                return y_pos + bar_h + _mm_to_points(8)
            elif header_style == "color_block":
                block_h = _mm_to_points(12)
                p.draw_rect(
                    fitz.Rect(margin, y_pos, width_pt - margin, y_pos + block_h),
                    color=theme_rgb, fill=theme_rgb, width=0
                )
                return y_pos + block_h + _mm_to_points(6)
            return y_pos

        def _new_content_page():
            nonlocal page, y
            page = doc.new_page(width=width_pt, height=height_pt)
            _render_page_bg(page)
            y = margin + _mm_to_points(5)
            y = _render_header_deco(page, y)
            title_text = data.get("title", "").strip()
            if title_text:
                _insert_text_safe(page, title_text, margin, y + 8,
                                 fontsize=10, color=gray_rgb)
                y += _mm_to_points(14)
            page.draw_line(
                fitz.Point(margin, y),
                fitz.Point(width_pt - margin, y),
                color=theme_rgb, width=0.3,
            )
            y += _mm_to_points(8)
            if progress_callback:
                progress_callback(doc.page_count, -1, f"自动分页：第 {doc.page_count} 页")

        def _ensure_space(needed_pt: float):
            nonlocal page, y
            if y + needed_pt > max_y:
                _render_footer(page, doc.page_count)
                _new_content_page()

        if progress_callback:
            progress_callback(1, -1, "正在渲染报告封面")

        # 封面页
        page = doc.new_page(width=width_pt, height=height_pt)
        _render_page_bg(page)

        cover_y = margin + _mm_to_points(5)
        cover_y = _render_header_deco(page, cover_y)
        cover_y += _mm_to_points(60)

        title = data.get("title", "").strip()
        if title:
            cover_title_fontsize = 28
            title_lines = _wrap_text_in_width(title, cover_title_fontsize, content_width)
            for tl in title_lines[:3]:
                tl_w = _measure_text_width(tl, cover_title_fontsize)
                _insert_text_safe(page, tl, (width_pt - tl_w) / 2, cover_y,
                                 fontsize=cover_title_fontsize, color=dark_rgb)
                cover_y += _mm_to_points(14)
            cover_y += _mm_to_points(5)

        subtitle = data.get("subtitle", "").strip()
        if subtitle:
            sub_fontsize = 16
            sub_lines = _wrap_text_in_width(subtitle, sub_fontsize, content_width)
            for sl in sub_lines[:2]:
                sl_w = _measure_text_width(sl, sub_fontsize)
                _insert_text_safe(page, sl, (width_pt - sl_w) / 2, cover_y,
                                 fontsize=sub_fontsize, color=gray_rgb, regular=True)
                cover_y += _mm_to_points(10)
            cover_y += _mm_to_points(5)

        cover_y += _mm_to_points(10)
        line_w = _mm_to_points(60)
        page.draw_line(
            fitz.Point((width_pt - line_w) / 2, cover_y),
            fitz.Point((width_pt + line_w) / 2, cover_y),
            color=theme_rgb, width=1.0,
        )
        cover_y += _mm_to_points(15)

        author = data.get("author", "").strip()
        if author:
            author_fontsize = 13
            author_w = _measure_text_width(author, author_fontsize)
            _insert_text_safe(page, author, (width_pt - author_w) / 2, cover_y,
                             fontsize=author_fontsize, color=dark_rgb, regular=True)
            cover_y += _mm_to_points(10)

        date = data.get("date", "").strip()
        if date:
            date_fontsize = 12
            date_w = _measure_text_width(date, date_fontsize)
            _insert_text_safe(page, date, (width_pt - date_w) / 2, cover_y,
                             fontsize=date_fontsize, color=gray_rgb, regular=True)

        _render_footer(page, 1)

        # 正文页
        _new_content_page()

        summary = data.get("summary", "").strip()
        if summary:
            summary = truncate_text(summary, max_chars=300)
            _insert_text_safe(page, "▎ 摘要", margin, y,
                             fontsize=12, color=theme_rgb)
            y += _mm_to_points(7)

            summary_rect = fitz.Rect(margin, y, margin + content_width, max_y)
            used_h = draw_wrapped_text(
                page, summary, summary_rect,
                fontsize=11, line_gap=_mm_to_points(6),
                max_lines=20, regular=True,
            )
            y += used_h + _mm_to_points(8)

            page.draw_line(
                fitz.Point(margin, y),
                fitz.Point(width_pt - margin, y),
                color=light_theme, width=0.5,
            )
            y += _mm_to_points(10)

        sections_raw = data.get("sections", "").strip()
        if sections_raw:
            section_parts = sections_raw.split("## ")
            parsed_sections = []
            for part in section_parts:
                part = part.strip()
                if not part:
                    continue
                lines = part.split("\n", 1)
                sec_title = lines[0].strip()
                sec_title = truncate_text(sec_title, max_chars=60)
                sec_content = lines[1].strip() if len(lines) > 1 else ""
                sec_content = truncate_text(sec_content, max_chars=1200)
                parsed_sections.append((sec_title, sec_content))

            section_title_fontsize = 14
            section_body_fontsize = 11
            section_line_gap = _mm_to_points(6)
            section_title_gap = _mm_to_points(8)
            MAX_SECTION_HEIGHT = 180  # 点（约 63mm）

            for sec_title, sec_content in parsed_sections:
                _ensure_space(section_title_gap + _mm_to_points(5))
                deco_w = _mm_to_points(2)
                deco_h = _mm_to_points(6)
                page.draw_rect(
                    fitz.Rect(margin, y, margin + deco_w, y + deco_h),
                    color=theme_rgb, fill=theme_rgb, width=0
                )
                _insert_text_safe(page, sec_title, margin + deco_w + _mm_to_points(3),
                                 y + section_title_fontsize * 0.7,
                                 fontsize=section_title_fontsize, color=dark_rgb)
                y += section_title_gap + _mm_to_points(3)

                if sec_content:
                    sections_used = 0.0
                    paragraphs = sec_content.split("\n")
                    for para in paragraphs:
                        para = para.strip()
                        if not para:
                            sections_used += section_line_gap * 0.5
                            continue
                        if sections_used >= MAX_SECTION_HEIGHT:
                            break
                        para_rect = fitz.Rect(
                            margin, y,
                            margin + content_width,
                            y + (MAX_SECTION_HEIGHT - sections_used)
                        )
                        used_h = draw_wrapped_text(
                            page, para, para_rect,
                            fontsize=section_body_fontsize,
                            line_gap=section_line_gap,
                            regular=True,
                        )
                        y += used_h
                        sections_used += used_h

                y += _mm_to_points(8)

        conclusion = data.get("conclusion", "").strip()
        if conclusion:
            conclusion = truncate_text(conclusion, max_chars=500)
            _ensure_space(_mm_to_points(20))
            _insert_text_safe(page, "▎ 结论与建议", margin, y,
                             fontsize=12, color=theme_rgb)
            y += _mm_to_points(7)

            conclusion_rect = fitz.Rect(margin, y, margin + content_width, max_y)
            used_h = draw_wrapped_text(
                page, conclusion, conclusion_rect,
                fontsize=11, line_gap=_mm_to_points(6),
                max_lines=35, regular=True,
            )
            y += used_h

        _render_footer(page, doc.page_count)

        for i in range(1, doc.page_count):
            p = doc[i]
            _render_footer(p, i + 1)

        if progress_callback:
            progress_callback(doc.page_count, doc.page_count, "报告渲染完成")

    except Exception as e:
        error_info = f"报告渲染过程中出错: {e}"
        print(f"[renderer] {error_info}")
        _save_partial(doc, output_path)
        if error_info:
            raise RuntimeError(error_info)

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    doc.save(output_path)
    doc.close()
    return output_path


# ================================================================
# 统一模板渲染入口
# ================================================================

def render_template(template_id: str, output_path: str, data: dict, **kwargs) -> str:
    """统一模板渲染入口，根据 template_id 分发到对应的渲染函数
    
    Args:
        template_id: 模板ID，如 "business_card", "notice", "product_spec", "contract", "invoice", "report"
        output_path: 输出PDF路径
        data: 模板数据字典
        **kwargs: 传递给具体渲染函数的额外参数
    
    Returns:
        输出文件路径
    
    Raises:
        ValueError: 不支持的模板类型
    """
    if template_id == "business_card":
        return render_business_card(output_path, data, **kwargs)
    elif template_id == "notice":
        return render_notice(output_path, data, **kwargs)
    elif template_id == "product_spec":
        return render_product_spec(output_path, data, **kwargs)
    elif template_id == "contract":
        return render_contract(output_path, data, **kwargs)
    elif template_id == "invoice":
        return render_invoice(output_path, data, **kwargs)
    elif template_id == "report":
        return render_report(output_path, data, **kwargs)
    else:
        raise ValueError(
            f"不支持的模板类型: '{template_id}'。"
            f"当前支持的模板: business_card, notice, product_spec, contract, invoice, report"
        )


# ================================================================
# CanvasModel — 统一画布模型（RC1 预览/导出 一致性阻断修复）
# ================================================================

class CanvasModel:
    """
    统一的画布数据模型。

    职责：
      - 一次性汇总「布局变量 + 字段 + 样式 + 资源」四类数据
      - 同一份 CanvasModel 同时驱动预览和导出
      - 消除"预览走 HTML/CSS、导出走 PDF"的重复实现

    字段：
      template_id : str
      side        : "front" | "back"
      fields      : dict  — 业务字段（name_cn/title/phone/...）
      styles      : dict  — 样式选项（theme_color/bg_style/...）
      assets      : dict  — 资源路径（logo_path/qr_image_path/...）
      layout      : dict  — 布局变量（margins, sizes, positions）
    """

    def __init__(self, template_id, side, fields, styles, assets, layout):
        self.template_id = template_id
        self.side = side
        self.fields = fields
        self.styles = styles
        self.assets = assets
        self.layout = layout

    def render_to_pixmap(self, target_width: int = 560, dpi: float = 2.5):
        """
        把当前 CanvasModel 渲染为 QPixmap（用于预览）。
        流程：先渲染为临时 PDF → fitz 转 PNG → QPixmap。
        与导出共用同一份 layout / fields，所以像素级一致。
        """
        import tempfile
        from PySide6.QtGui import QPixmap

        tmp_pdf = os.path.join(
            tempfile.gettempdir(), f"PDflow_Canvas_{self.side}_{id(self)}.pdf"
        )
        try:
            self.render_to_pdf(tmp_pdf)
            doc = fitz.open(tmp_pdf)
            page = doc.load_page(0)
            mat = fitz.Matrix(dpi, dpi)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            png_bytes = pix.tobytes("png")
            qpx = QPixmap()
            qpx.loadFromData(png_bytes)
            doc.close()
            if target_width and qpx.width() != target_width:
                from PySide6.QtCore import Qt
                qpx = qpx.scaledToWidth(target_width, Qt.SmoothTransformation)
            return qpx
        finally:
            try:
                if os.path.isfile(tmp_pdf):
                    os.remove(tmp_pdf)
            except Exception:
                pass

    def render_to_pdf(self, output_path: str) -> str:
        """
        把当前 CanvasModel 渲染为 PDF 文件（用于导出）。
        与预览共用同一份 layout / fields，所以像素级一致。
        """
        if self.template_id == "business_card":
            return render_business_card(
                output_path=output_path,
                data=self.fields,
                logo_path=self.assets.get("logo_path"),
                qr_image_path=self.assets.get("qr_image_path"),
                back_logo_path=self.assets.get("back_logo_path"),  # V1.1 RC 收尾：补传正面 LOGO（之前漏传导致正面 LOGO 永远不显示）
                style_options=self.styles,
                logo_width_mm=self.layout.get("logo_width_mm", 8.0),
                logo_right_mm=self.layout.get("logo_right_mm", 5.0),
                logo_top_mm=self.layout.get("logo_top_mm", 4.0),
                logo_shape=self.layout.get("logo_shape", "square"),
                bg_image_path=self.styles.get("bg_image_path"),
                bg_image_opacity=self.styles.get("bg_image_opacity", 50),
                bg_texture=self.styles.get("bg_texture", "none"),
                bg_custom_color=self.styles.get("bg_custom_color", ""),
                text_color=self.styles.get("text_color", "#2C3E50"),
                text_secondary_color=self.styles.get("text_secondary_color", "#7F8C8D"),
                render_sides=[self.side],
            )
        raise ValueError(f"CanvasModel 不支持的模板: {self.template_id}")


def render_business_card_canvas(data: dict, mode: str = "preview",
                                side: str = "front",
                                styles: dict = None,
                                assets: dict = None,
                                layout: dict = None) -> CanvasModel:
    """
    统一名片入口（RC1 预览/导出 一致性修复）。

    参数：
        data   : 字段 dict（name_cn/title/phone/...）
        mode   : "preview" | "export"（仅日志/调试用，不影响渲染）
        side   : "front" | "back"
        styles : 样式 dict（theme_color/bg_style/text_color/...）
        assets : 资源路径 dict（logo_path/qr_image_path/...）
        layout : 布局变量 dict（logo_width_mm/...）

    返回：
        CanvasModel 实例 — 同一份对象可调用 render_to_pixmap() 或 render_to_pdf()

    用法：
        canvas = render_business_card_canvas(data, side="front",
                                             styles=styles, assets=assets)
        qpixmap = canvas.render_to_pixmap()            # 预览
        canvas.render_to_pdf("output.pdf")             # 导出
    """
    return CanvasModel(
        template_id="business_card",
        side=side,
        fields=data or {},
        styles=styles or {},
        assets=assets or {},
        layout=layout or {},
    )


# ================================================================
# RenderContext — 统一的编辑器渲染上下文（RC1 导出一致性修复）
# ================================================================

class RenderContext:
    """
    编辑器统一渲染上下文。

    职责：
      - 一次 serialize() 锁定：fields + styles + assets + layout + side
      - 同一份上下文同时驱动预览和导出，杜绝预览/导出走两条不同路径
      - 支持多面（front/back）独立序列化，但所有面共享同一份样式/资源
      - 禁止 load_template()、禁止重新读取模板默认值

    字段：
      template_id : str
      side        : "front" | "back"
      fields      : dict  — 业务字段（name_cn/title/phone/...）
      styles      : dict  — 样式选项（theme_color/bg_style/text_color/...）
      assets      : dict  — 资源路径（logo_path/qr_image_path/back_logo/...）
      layout      : dict  — 布局变量（logo_width_mm/logo_top_mm/...）
    """

    def __init__(self, template_id, side, fields, styles, assets, layout):
        self.template_id = template_id
        self.side = side
        self.fields = dict(fields or {})
        self.styles = dict(styles or {})
        self.assets = dict(assets or {})
        self.layout = dict(layout or {})

    def to_canvas(self) -> CanvasModel:
        """把 RenderContext 转成 CanvasModel 用于渲染。"""
        return CanvasModel(
            template_id=self.template_id,
            side=self.side,
            fields=self.fields,
            styles=self.styles,
            assets=self.assets,
            layout=self.layout,
        )

    def render_to_pixmap(self, target_width: int = 560, dpi: float = 2.5):
        """预览：同一份上下文 → QPixmap。"""
        return self.to_canvas().render_to_pixmap(target_width=target_width, dpi=dpi)

    def render_to_pdf(self, output_path: str) -> str:
        """导出：同一份上下文 → PDF。"""
        return self.to_canvas().render_to_pdf(output_path)

    def debug_snapshot(self) -> dict:
        """调试用：导出当前上下文的完整快照，便于与 export 路径对比。"""
        return {
            "template_id": self.template_id,
            "side": self.side,
            "fields_keys": sorted(self.fields.keys()),
            "fields_non_empty": sorted(k for k, v in self.fields.items() if v),
            "styles": dict(self.styles),
            "assets": {k: v for k, v in self.assets.items() if v},
            "layout": dict(self.layout),
        }


def make_render_context(
    template_id: str,
    side: str,
    fields: dict,
    styles: dict,
    logo_path: str = None,
    qr_image_path: str = None,
    back_logo_path: str = None,
    logo_width_mm: float = 8.0,
    logo_right_mm: float = 5.0,
    logo_top_mm: float = 4.0,
    logo_shape: str = "square",
) -> RenderContext:
    """
    工厂方法：从编辑器参数一键打包 RenderContext。

    禁止任何模板默认值的"二次读取"——所有值都从传入的 fields/styles 拷贝。
    """
    assets = {
        "logo_path": logo_path,
        "qr_image_path": qr_image_path,
        "back_logo_path": back_logo_path,
    }
    layout = {
        "logo_width_mm": logo_width_mm,
        "logo_right_mm": logo_right_mm,
        "logo_top_mm": logo_top_mm,
        "logo_shape": logo_shape,
    }
    return RenderContext(
        template_id=template_id,
        side=side,
        fields=fields or {},
        styles=styles or {},
        assets=assets,
        layout=layout,
    )
