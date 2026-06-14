"""
export/__init__.py

PDflow V1.1 RC 收尾 — 导出模块。

按 Route B（MuPDF 矢量）方案，所有可矢量化的元素都用真正的 PDF 矢量绘制，
禁止先生成 PNG/JPG 再嵌入。

架构：
    export/
    ├── __init__.py            # 本文件
    ├── pdf_exporter.py        # PDF 矢量绘制函数（背景 / 文字 / 图标 / QR）

调用方：
    src/common/template_renderer.py
    pages/template_editor_page.py  (未来可扩展 SVG exporter)
"""

from .pdf_exporter import (
    draw_linear_gradient,
    draw_diagonal_4corner_gradient,
    draw_text_icon,
    draw_icon_letter,
    embed_qr_code,
    render_with_pymupdf,
)

__all__ = [
    "draw_linear_gradient",
    "draw_diagonal_4corner_gradient",
    "draw_text_icon",
    "draw_icon_letter",
    "embed_qr_code",
    "render_with_pymupdf",
]
