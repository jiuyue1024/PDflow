# -*- coding: utf-8 -*-
"""
render_product_spec_patched.py — AT-07: render_product_spec() 升级版，支持 style 参数

此文件包含修改后的 render_product_spec() 及其依赖的辅助函数。
PM Agent 合并时，将此文件中的 render_product_spec() 替换到 template_renderer.py 中，
同时确保 template_renderer.py 已有 _hex_to_rgb 等辅助函数。

变更摘要（相对于 template_renderer.py 中的 render_product_spec）：
1. 函数签名新增 style: dict = None 参数
2. 主题色由 _hex_to_rgb(theme_color) 动态计算，替代硬编码 theme_rgb
3. 标题栏样式支持 bar / color_block / none 三种模式
4. 背景样式支持 white / light_gray / light_blue，以及 bg_custom_color 覆盖
5. 表格样式支持 striped / bordered / minimal 三种模式
6. _new_page() / _draw_table_header() 内部辅助函数也已适配 style 参数
"""
import fitz  # PyMuPDF
import os


# ================================================================
# 辅助函数（从 template_renderer.py 复制）
# ================================================================

def _mm_to_points(mm: float) -> float:
    """毫米转 PDF 点（1 inch = 25.4 mm = 72 points）"""
    return mm / 25.4 * 72


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


def _get_cjk_font():
    """查找系统中的中文字体文件，返回 fitz.Font 对象。"""
    font_candidates = [
        ("C:/Windows/Fonts/msyh.ttc", 0),
        ("C:/Windows/Fonts/msyhbd.ttc", 0),
        ("C:/Windows/Fonts/msyh.ttf", None),
        ("C:/Windows/Fonts/msyhbd.ttf", None),
        ("C:/Windows/Fonts/simhei.ttf", None),
        ("C:/Windows/Fonts/simsun.ttc", 0),
        ("C:/Windows/Fonts/simsunb.ttf", None),
        ("C:/Windows/Fonts/yahei.ttf", None),
        ("C:/Windows/Fonts/microsoftyahei.ttf", None),
        ("C:/Windows/Fonts/msyhl.ttc", 0),
    ]
    for fp, fontno in font_candidates:
        if os.path.exists(fp):
            try:
                if fontno is not None:
                    return fitz.Font(fontfile=fp, fontno=fontno)
                else:
                    return fitz.Font(fontfile=fp)
            except Exception as e:
                print(f"[render] 字体加载失败 {fp}: {e}")
                continue
    return None


def _insert_text_safe(page, text: str, x: float, y: float,
                     fontsize: float = 11, color: tuple = (0, 0, 0),
                     fontname: str = "helv"):
    """向页面插入文字，自动使用系统中文字体，避免 Helvetica 无法渲染中文的问题。"""
    if not text:
        return
    try:
        tw = fitz.TextWriter(page.rect, color=color)
        font = _get_cjk_font()
        if font:
            tw.append((x, y), text, font=font, fontsize=fontsize)
        else:
            tw.append((x, y), text, fontsize=fontsize)
        tw.write_text(page)
    except Exception as e:
        print(f"[render] 文本写入失败: {e}")


def _measure_text_width(text: str, fontsize: float = 11) -> float:
    """测量文本在指定字号下的渲染宽度（点），使用 CJK 字体或默认字体。"""
    if not text:
        return 0.0
    try:
        font = _get_cjk_font()
        if font:
            return font.text_length(text, fontsize=fontsize)
        else:
            return fitz.Font("helv").text_length(text, fontsize=fontsize)
    except Exception:
        cn_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        en_chars = len(text) - cn_chars
        return cn_chars * fontsize + en_chars * fontsize * 0.5


def _wrap_text_in_width(text: str, fontsize: float, max_width_pt: float) -> list:
    """
    将文本按指定宽度自动换行，返回分行列表。
    优先在空格、标点处断行；如果单字超宽也强制断行。
    """
    if not text:
        return []
    if _measure_text_width(text, fontsize) <= max_width_pt:
        return [text]

    lines = []
    remaining = text
    while remaining:
        best_idx = len(remaining)
        for i in range(len(remaining), 0, -1):
            if _measure_text_width(remaining[:i], fontsize) <= max_width_pt:
                best_idx = i
                break

        if best_idx == len(remaining):
            lines.append(remaining)
            break

        break_idx = best_idx
        for i in range(best_idx, max(best_idx - 8, 0), -1):
            if remaining[i] in (' ', '，', '。', '、', '；', '：', '）', ')',
                                '】', ']', '！', '?', '？', ',', '.', ';', ':'):
                break_idx = i + 1
                break

        if break_idx <= 0:
            break_idx = best_idx

        lines.append(remaining[:break_idx])
        remaining = remaining[break_idx:].lstrip()

    return lines


def _embed_image_in_page(page, image_path: str, x_mm: float, y_mm: float,
                         width_mm: float, height_mm: float):
    """将图片嵌入到 PDF 页面指定区域（单位：毫米）。"""
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


# ================================================================
# AT-07：升级版 render_product_spec（支持 style 参数）
# ================================================================

def render_product_spec(output_path: str, data: dict, image_path: str = None, style: dict = None) -> str:
    """
    渲染产品规格模板 PDF（A4 尺寸，自动分页）。

    data 键对应 product_spec.json 的 fields key：
      product_name, version, description, specs

    specs 可以是：
      - str: 旧格式，按换行符分段渲染
      - list[dict]: 新格式表格数据，如 [{"param": "尺寸", "value": "210×297mm"}, ...]

    image_path: 可选，上传的产品图片路径，会嵌入到页面右上角

    style: 样式参数字典，支持以下键：
      theme_color:  主题色 hex (默认 "#3355AA")
      header_style: 标题栏样式 "bar" | "color_block" | "none" (默认 "bar")
      bg_style:     背景样式 "white" | "light_gray" | "light_blue" (默认 "white")
      bg_custom_color: 自定义背景色 hex，非空时覆盖 bg_style (默认 "")
      table_style:  表格样式 "striped" | "bordered" | "minimal" (默认 "striped")

    布局：顶部产品名 + 版本号 → 中部产品描述 → 底部技术规格
    自动分页：内容超出当前页时自动新建页面，表格表头在每页顶部重复显示。
    """
    # ── AT-07: style 参数解析 ──
    style = style or {}
    theme_color = style.get("theme_color", "#3355AA")
    header_style = style.get("header_style", "bar")
    bg_style = style.get("bg_style", "white")
    bg_custom_color = style.get("bg_custom_color", "")
    table_style = style.get("table_style", "striped")

    # ── AT-07: 主题色动态计算 ──
    theme_rgb = _hex_to_rgb(theme_color)

    # ── AT-07: 背景色计算 ──
    if bg_custom_color:
        bg_fill = _hex_to_rgb(bg_custom_color)
    elif bg_style == "light_gray":
        bg_fill = _hex_to_rgb("#F5F5F5")
    elif bg_style == "light_blue":
        bg_fill = _hex_to_rgb("#EBF0FA")
    else:  # "white"
        bg_fill = (1, 1, 1)

    # 其他颜色常量
    accent_rgb = (0.85, 0.87, 0.92)   # 浅蓝灰（规格区背景）
    gray_rgb  = (0.5, 0.5, 0.5)       # 辅助灰
    dark_rgb  = (0.15, 0.15, 0.15)    # 深色正文

    # A4: 210mm × 297mm
    width_pt = _mm_to_points(210)
    height_pt = _mm_to_points(297)

    doc = fitz.open()
    page = doc.new_page(width=width_pt, height=height_pt)

    # ── AT-07: 动态背景色 ──
    page.draw_rect(fitz.Rect(0, 0, width_pt, height_pt),
                   color=bg_fill, fill=bg_fill, width=0)

    margin = _mm_to_points(20)
    content_width = width_pt - 2 * margin
    bottom_margin = margin + _mm_to_points(10)  # 底部留白
    max_y = height_pt - bottom_margin            # 内容区下界

    y = margin + _mm_to_points(5)

    # ── 辅助：新建一页（AT-07: 使用动态 bg_fill） ──
    def _new_page():
        nonlocal page, y
        page = doc.new_page(width=width_pt, height=height_pt)
        page.draw_rect(fitz.Rect(0, 0, width_pt, height_pt),
                       color=bg_fill, fill=bg_fill, width=0)
        y = margin + _mm_to_points(5)
        return page

    # ── 辅助：确保当前页有足够的垂直空间，不够则换页 ──
    def _ensure_space(needed_pt: float):
        nonlocal page, y
        if y + needed_pt > max_y:
            _new_page()

    # ── 产品名称（顶部大字，自动折行）──
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

    # ── 版本号（自动折行）──
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

    # ── 产品图片（右上角，仅第一页）──
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

    # ── AT-07: 标题栏装饰（根据 header_style 切换） ──
    if header_style == "bar":
        # 默认：保持现有装饰横条
        title_bar_h = _mm_to_points(2)
        page.draw_rect(
            fitz.Rect(margin, y, width_pt - margin, y + title_bar_h),
            color=theme_rgb, fill=theme_rgb, width=0
        )
        y += title_bar_h + _mm_to_points(10)
    elif header_style == "color_block":
        # 色块背景：标题行用主题色背景 + 白色文字
        color_block_h = _mm_to_points(8)
        page.draw_rect(
            fitz.Rect(margin, y, width_pt - margin, y + color_block_h),
            color=theme_rgb, fill=theme_rgb, width=0
        )
        _insert_text_safe(page, "产品规格", margin + _mm_to_points(3), y + _mm_to_points(4.5),
                         fontsize=12, color=(1, 1, 1))
        y += color_block_h + _mm_to_points(10)
    else:
        # none: 不画装饰条，仅留间距
        y += _mm_to_points(10)

    # ── 产品描述（支持自动分页，精确宽度折行）──
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

    # ── 技术规格（AT-07: 根据 table_style 切换渲染方式） ──
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
            # ── 表格参数 ──
            col1_w = 70   # 参数列宽度（mm）
            col2_w = 100  # 值列宽度（mm）
            base_row_h = _mm_to_points(7)
            cell_padding = _mm_to_points(2)
            text_fontsize = 10
            text_line_h = _mm_to_points(5)
            header_h = base_row_h + _mm_to_points(3)

            col1_text_w = _mm_to_points(col1_w) - 2 * cell_padding
            col2_text_w = _mm_to_points(col2_w) - 2 * cell_padding

            # AT-07: 表格绘制辅助函数，根据 table_style 调整
            def _draw_table_header(cur_page, cur_y):
                """在指定位置绘制表格表头行"""
                x1 = margin
                x2 = margin + _mm_to_points(col1_w)
                header_rect = fitz.Rect(x1, cur_y, x2 + _mm_to_points(col2_w), cur_y + base_row_h)

                if table_style == "bordered":
                    # bordered: 表头有主题色背景 + 边框
                    cur_page.draw_rect(header_rect, color=theme_rgb, fill=theme_rgb, width=0.8)
                    _insert_text_safe(cur_page, "参数", x1 + cell_padding, cur_y + _mm_to_points(2),
                                     fontsize=10, color=(1, 1, 1))
                    _insert_text_safe(cur_page, "值", x2 + cell_padding, cur_y + _mm_to_points(2),
                                     fontsize=10, color=(1, 1, 1))
                elif table_style == "minimal":
                    # minimal: 仅表头有底色，无边框
                    cur_page.draw_rect(header_rect, color=None, fill=theme_rgb, width=0)
                    _insert_text_safe(cur_page, "参数", x1 + cell_padding, cur_y + _mm_to_points(2),
                                     fontsize=10, color=(1, 1, 1))
                    _insert_text_safe(cur_page, "值", x2 + cell_padding, cur_y + _mm_to_points(2),
                                     fontsize=10, color=(1, 1, 1))
                else:
                    # striped (默认): 保持原样
                    cur_page.draw_rect(header_rect, color=theme_rgb, fill=theme_rgb, width=0.5)
                    _insert_text_safe(cur_page, "参数", x1 + cell_padding, cur_y + _mm_to_points(2),
                                     fontsize=10, color=(1, 1, 1))
                    _insert_text_safe(cur_page, "值", x2 + cell_padding, cur_y + _mm_to_points(2),
                                     fontsize=10, color=(1, 1, 1))

                return cur_y + base_row_h + _mm_to_points(1)

            # 预计算每行的折行结果与行高
            row_data = []
            for idx, row in enumerate(specs_list):
                if not isinstance(row, dict):
                    continue
                param = row.get("param", "").strip()
                value = row.get("value", "").strip()
                if not param and not value:
                    continue

                param_lines = _wrap_text_in_width(param, text_fontsize, col1_text_w) if param else []
                value_lines = _wrap_text_in_width(value, text_fontsize, col2_text_w) if value else []

                max_lines = max(len(param_lines), len(value_lines), 1)
                row_h = max(base_row_h, max_lines * text_line_h + _mm_to_points(1.5))

                row_data.append((param_lines, value_lines, row_h, idx))

            # 第一页绘制表头
            if row_data:
                _ensure_space(header_h + row_data[0][2])
            y = _draw_table_header(page, y)

            for param_lines, value_lines, row_h, idx in row_data:
                # 当前页放不下这一行 → 换页 + 重新绘制表头
                if y + row_h > max_y:
                    _new_page()
                    y = _draw_table_header(page, y)

                # ── AT-07: 根据 table_style 绘制数据行 ──
                x1 = margin
                x2 = margin + _mm_to_points(col1_w)
                x_end = x2 + _mm_to_points(col2_w)

                if table_style == "striped":
                    # 斑马纹：奇数行浅蓝灰背景，偶数行白色
                    bg_color = accent_rgb if idx % 2 == 0 else (1, 1, 1)

                    rect1 = fitz.Rect(x1, y, x2, y + row_h)
                    page.draw_rect(rect1, color=theme_rgb, fill=bg_color, width=0.5)
                    for li, line in enumerate(param_lines):
                        _insert_text_safe(page, line, x1 + cell_padding,
                                         y + _mm_to_points(2) + li * text_line_h,
                                         fontsize=text_fontsize, color=dark_rgb)

                    rect2 = fitz.Rect(x2, y, x_end, y + row_h)
                    page.draw_rect(rect2, color=theme_rgb, fill=bg_color, width=0.5)
                    for li, line in enumerate(value_lines):
                        _insert_text_safe(page, line, x2 + cell_padding,
                                         y + _mm_to_points(2) + li * text_line_h,
                                         fontsize=text_fontsize, color=dark_rgb)

                elif table_style == "bordered":
                    # 线框：每行有边框线，无背景色交替
                    rect1 = fitz.Rect(x1, y, x2, y + row_h)
                    page.draw_rect(rect1, color=theme_rgb, fill=bg_fill, width=0.8)
                    for li, line in enumerate(param_lines):
                        _insert_text_safe(page, line, x1 + cell_padding,
                                         y + _mm_to_points(2) + li * text_line_h,
                                         fontsize=text_fontsize, color=dark_rgb)

                    rect2 = fitz.Rect(x2, y, x_end, y + row_h)
                    page.draw_rect(rect2, color=theme_rgb, fill=bg_fill, width=0.8)
                    for li, line in enumerate(value_lines):
                        _insert_text_safe(page, line, x2 + cell_padding,
                                         y + _mm_to_points(2) + li * text_line_h,
                                         fontsize=text_fontsize, color=dark_rgb)

                elif table_style == "minimal":
                    # 极简：仅表头有底色，数据行无边框无背景
                    for li, line in enumerate(param_lines):
                        _insert_text_safe(page, line, x1 + cell_padding,
                                         y + _mm_to_points(2) + li * text_line_h,
                                         fontsize=text_fontsize, color=dark_rgb)

                    for li, line in enumerate(value_lines):
                        _insert_text_safe(page, line, x2 + cell_padding,
                                         y + _mm_to_points(2) + li * text_line_h,
                                         fontsize=text_fontsize, color=dark_rgb)

                y += row_h

        else:
            # 旧格式：逐行渲染（支持分页）
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

        # 最后一页的规格区底部分隔线
        # AT-07: bordered 和 minimal 样式下不画底部分隔线，仅 striped 保留
        if table_style == "striped":
            page.draw_line(
                fitz.Point(margin, y + _mm_to_points(3)),
                fitz.Point(width_pt - margin, y + _mm_to_points(3)),
                color=accent_rgb, width=0.5,
            )
        elif table_style == "bordered":
            # bordered: 画一条主题色分隔线收尾
            page.draw_line(
                fitz.Point(margin, y + _mm_to_points(2)),
                fitz.Point(width_pt - margin, y + _mm_to_points(2)),
                color=theme_rgb, width=0.8,
            )
        # minimal: 不画分隔线

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    doc.save(output_path)
    doc.close()
    return output_path
