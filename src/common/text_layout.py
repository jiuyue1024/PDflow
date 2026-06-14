# -*- coding: utf-8 -*-
"""
text_layout.py — 统一文本排版工具（纯 fitz，无 Qt 依赖）

提供 draw_wrapped_text()、truncate_text() 和 parse_items() 三个公共函数，
用于在 fitz.Page 上渲染自动换行、可选截断的文本段落，
以及统一解析明细项目输入。

依赖：fitz（PyMuPDF）
内部使用 from src.common.template_renderer 懒导入复刻的底层文本工具函数，
避免模块加载时的循环导入问题。
"""
import fitz


def parse_items(text: str) -> list:
    """
    统一解析明细项目输入文本。

    输入格式（每行一项）：
        项目名称|数量|金额

    返回：
        [{"name": str, "qty": str, "price": str}, ...]
        格式错误的行自动跳过。
    """
    rows = []
    for line in text.splitlines():
        parts = line.split("|")
        if len(parts) != 3:
            continue
        rows.append({
            "name": parts[0].strip(),
            "qty": parts[1].strip(),
            "price": parts[2].strip(),
        })
    return rows


def draw_wrapped_text(
    page: fitz.Page,
    text: str,
    rect,
    fontsize: float = 11,
    color: tuple = (0, 0, 0),
    line_gap: float = None,
    max_lines: int = None,
    regular: bool = False,
) -> float:
    """
    在指定的矩形区域内渲染自动换行文本。

    参数：
        page: fitz.Page 对象
        text: 待渲染文本（纯文本，可含换行符）
        rect: 目标矩形（fitz.Rect 或 (x0,y0,x1,y1) 四元组）
        fontsize: 字号（点）
        color: RGB 三元组 (0.0-1.0)
        line_gap: 行间距（点），默认 = fontsize * 0.35
        max_lines: 最大行数，超出时最后一行截断加省略号

    返回：
        实际使用的垂直高度（点），调用者可据此更新 y 坐标
    """
    # 懒导入：避免模块级循环导入
    from src.common.template_renderer import (
        _wrap_text_in_width,
        _truncate_to_width,
        _insert_text_safe,
    )

    if not text:
        return 0.0

    if line_gap is None:
        line_gap = fontsize * 0.35

    line_height = fontsize + line_gap

    # 支持 fitz.Rect 或四元组
    if hasattr(rect, 'x0'):
        x0, y0, x1 = rect.x0, rect.y0, rect.x1
    else:
        x0, y0, x1 = rect[0], rect[1], rect[2]

    content_width = x1 - x0
    if content_width <= 0:
        return 0.0

    # 将文本按显式换行符拆分为段落，再逐段换行
    paragraphs = text.split("\n")
    all_lines = []
    for para in paragraphs:
        para = para.strip()
        if not para:
            all_lines.append("")
            continue
        wrapped = _wrap_text_in_width(para, fontsize, content_width)
        if wrapped:
            all_lines.extend(wrapped)

    # 合并连续空行
    compact_lines = []
    prev_blank = False
    for line in all_lines:
        if line == "":
            if not prev_blank:
                compact_lines.append("")
                prev_blank = True
            continue
        compact_lines.append(line)
        prev_blank = False

    # 截断到 max_lines
    truncated = False
    if max_lines is not None and len(compact_lines) > max_lines:
        compact_lines = compact_lines[:max_lines]
        truncated = True

    # 渲染每一行
    cursor_y = y0
    actual_height = 0.0
    for idx, line in enumerate(compact_lines):
        if line == "":
            cursor_y += line_height
            actual_height += line_height
            continue

        if truncated and idx == len(compact_lines) - 1:
            display_text = _truncate_to_width(line, content_width, fontsize)
        else:
            display_text = line

        _insert_text_safe(page, display_text, x0, cursor_y + fontsize,
                          fontsize=fontsize, color=color, regular=regular)
        cursor_y += line_height
        actual_height += line_height

    return actual_height


def truncate_text(
    text: str,
    max_chars: int,
    max_width_pt: float = None,
    fontsize: float = 11,
    ellipsis: str = "…"
) -> str:
    """
    按字符数和渲染宽度双重截断文本。
    用于渲染前对 data 字段做防御性截断。

    参数：
        text: 原始文本
        max_chars: 最大字符数
        max_width_pt: 可选，最大渲染宽度（点）
        fontsize: 字号（点），仅当 max_width_pt 有效时使用
        ellipsis: 省略号字符

    返回：
        截断后的文本
    """
    if not text:
        return ""

    truncated = text[:max_chars]
    if len(text) > max_chars:
        truncated = truncated.rstrip() + ellipsis

    if max_width_pt is not None and max_width_pt > 0:
        from src.common.template_renderer import _truncate_to_width
        truncated = _truncate_to_width(truncated, max_width_pt, fontsize)

    return truncated
