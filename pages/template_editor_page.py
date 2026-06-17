# -*- coding: utf-8 -*-
"""
template_editor_page.py — 模板编辑界面
根据模板 JSON 的 fields 动态生成表单，支持实时预览 + 生成 PDF

P0 改进：
  - 表单字段分组（个人信息/公司信息/联系方式）
  - 右侧实时名片预览面板
  - 输入框聚焦外发光
  - 底部操作栏视觉增强
  - 顶部标题区域优化
  - placeholder 颜色修正
"""
import json
import os

from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QLabel, QLineEdit, QTextEdit, QPushButton,
    QSpacerItem, QSizePolicy, QMessageBox,
    QFrame, QFileDialog, QButtonGroup, QRadioButton,
    QDoubleSpinBox, QSlider, QColorDialog, QTableWidget, QTableWidgetItem, QHeaderView,
    QComboBox, QTabWidget, QAbstractItemView,
)
from PySide6.QtGui import QColor
import shiboken6

from src.common.paths import resource_path, data_path
from src.common.theme_tokens import theme_tokens, get_token as t
from src.common.text_layout import parse_items
from src.common.preview_renderer import PREVIEW_SCALE


def _is_numeric(s: str) -> bool:
    """判断字符串是否为合法数字（整数或小数，含正负号）"""
    if not s:
        return False
    try:
        float(s)
        return True
    except ValueError:
        return False


# 便捷：当前主题的 token 读取
# 用法：t("bg_primary") → "#0B0E11" 或 "#FAFAFA"


PROJECT_ROOT = resource_path()
TEMPLATES_PATH = os.path.join(PROJECT_ROOT, "assets", "templates")
OUTPUT_DIR = data_path("output", "templates")


# ── 支持文件上传嵌入的模板 ──
# TPL-05：value 为该模板下所有上传项的列表，每项有：
#   side           — "front" | "back" | "both"，决定在哪个面显示
#   key            — 唯一 key，渲染时通过 self._uploaded_paths[key] 读取路径
#   title          — 卡片标题
#   icon           — 标题前的图标
#   field          — 表单中的字段 key（用于保存到 template_data）
#   accepted_suffixes — 允许的文件后缀
#   show_position_shape — 是否显示 LOGO 位置/大小/形状调整控件（仅 LOGO 类）
UPLOAD_TEMPLATES = {
    "business_card": [
        {
            "side": "front",
            "key": "back_logo",
            "field": "back_logo",
            "title": "正面 LOGO",
            "icon": "🖼",
            "accepted_suffixes": ["png", "jpg", "jpeg"],  # V1.1 RC：移除 .pdf（fitz insert_image 不支持）
            "show_position_shape": True,
        },
        {
            "side": "front",
            "key": "back_qr_image",
            "field": "back_qr_image",
            "title": "上传二维码",
            "icon": "📱",
            "accepted_suffixes": ["png", "jpg", "jpeg"],
            "show_position_shape": False,
        },
        {
            "side": "back",
            "key": "logo",
            "field": "logo",
            "title": "公司 LOGO",
            "icon": "🏢",
            "accepted_suffixes": ["png", "jpg", "jpeg"],
            "show_position_shape": False,
        },
    ],
    "notice": [
        {
            "side": "front",
            "key": "header_image",
            "field": "header_image",
            "title": "上传图片",
            "icon": "🖼",
            "accepted_suffixes": ["png", "jpg", "jpeg"],
            "show_position_shape": False,
        },
    ],
    "product_spec": [
        {
            "side": "front",
            "key": "product_image",
            "field": "product_image",
            "title": "产品图片",
            "icon": "🖼",
            "accepted_suffixes": ["png", "jpg", "jpeg"],
            "show_position_shape": False,
        },
    ],
}


# ── 名片模板字段分组定义 ──
# 正面 = 主要信息（个人 / 联系方式 / 简介 / LOGO）
# 背面 = 公司品牌（LOGO / 公司 / SLOGAN）
FIELD_GROUPS = {
    "business_card": [
        {
            "title": "个人信息",
            "icon": "👤",
            "group_key": "front_personal",
            "keys": ["name_cn", "title", "description", "back_logo"]
        },
        {
            "title": "联系方式",
            "icon": "📞",
            "group_key": "front_contact",
            "keys": ["phone", "email", "website", "address"]
        },
        {
            "title": "公司品牌（背面）",
            "icon": "🏢",
            "group_key": "back_brand",
            "keys": ["logo", "company", "slogan"]
        },
    ]
}


# ── CSS 渲染辅助函数 ──
def _get_bg_css(bg_style: str, custom_color: str = "", texture: str = "none", text_color: str = "#2C3E50") -> tuple:
    """根据背景样式返回背景色和渐变值，以及纹理 CSS"""
    # 自定义颜色优先于 bg_style
    if custom_color:
        bg_color = custom_color
        bg_gradient = "transparent"
    elif bg_style == "white":
        bg_color, bg_gradient = "#FFFFFF", "transparent"
    elif bg_style == "light_gray":
        bg_color, bg_gradient = "#F5F5F7", "transparent"
    elif bg_style == "gradient_vertical":
        bg_color, bg_gradient = "transparent", "linear-gradient(180deg, #FFFFFF 0%, #F0F4FF 100%)"
    elif bg_style == "gradient_horizontal":
        bg_color, bg_gradient = "transparent", "linear-gradient(90deg, #FFFFFF 0%, #F0F4FF 100%)"
    else:
        bg_color, bg_gradient = "#FFFFFF", "transparent"

    # 判断背景亮度
    try:
        hex_c = bg_color.lstrip("#")
        if len(hex_c) == 6:
            r = int(hex_c[0:2], 16) / 255
            g = int(hex_c[2:4], 16) / 255
            b = int(hex_c[4:6], 16) / 255
            brightness = (r * 0.299 + g * 0.587 + b * 0.114)
        else:
            brightness = 1.0
    except Exception:
        brightness = 1.0

    # 纹理 CSS 自适应颜色
    if brightness < 0.5:
        # 深色背景：纹理用白色半透明
        t_alpha = "0.06"
        t_rgb = "255,255,255"
    else:
        # 浅色背景：纹理用黑色半透明
        t_alpha = "0.06"
        t_rgb = "0,0,0"

    texture_css = ""
    if texture == "dot":
        texture_css = (
            f"background-image: radial-gradient(circle, rgba({t_rgb},{t_alpha}) 1.2px, transparent 1.2px); "
            "background-size: 14px 14px;"
        )
    elif texture == "grid":
        texture_css = (
            f"background-image: "
            f"linear-gradient(rgba({t_rgb},{t_alpha}) 1px, transparent 1px), "
            f"linear-gradient(90deg, rgba({t_rgb},{t_alpha}) 1px, transparent 1px); "
            "background-size: 20px 20px;"
        )
    elif texture == "diagonal":
        texture_css = (
            f"background-image: repeating-linear-gradient("
            f"45deg, rgba({t_rgb},{t_alpha}) 0px, rgba({t_rgb},{t_alpha}) 1px, "
            "transparent 1px, transparent 16px"
            ");"
        )

    return bg_color, bg_gradient, texture_css


def _get_bar_css(bar_position: str, accent_color: str) -> tuple:
    """根据装饰条位置返回定位和尺寸 CSS"""
    if bar_position == "left":
        return "top: 0; left: 0;", "width: 6px; height: 100%;"
    elif bar_position == "right":
        return "top: 0; right: 0;", "width: 6px; height: 100%;"
    elif bar_position == "top":
        return "top: 0; left: 0;", "width: 100%; height: 6px;"
    elif bar_position == "bottom":
        return "bottom: 0; left: 0;", "width: 100%; height: 6px;"
    return "display: none;", ""


# ── 名片 CSS 模板（用于预览渲染，支持样式选项） ──
BUSINESS_CARD_CSS = """
<html>
<head>
<style>
body {{
    margin: 0; padding: 0;
    width: 568px; height: 347px;
    font-family: 'Noto Sans SC', 'Microsoft YaHei', sans-serif;
    overflow: hidden;
    position: relative;
    background: {bg_color};
}}
.card {{
    width: 568px; height: 347px;
    padding: 32px 40px;
    box-sizing: border-box;
    position: relative;
    background: {bg_gradient};
    z-index: 1;
}}
.card::before {{
    content: '';
    position: absolute;
    {bar_pos}
    {bar_size}
    background: {accent_color};
    z-index: 2;
}}
.card-texture {{
    position: absolute;
    top: 0; left: 0; width: 100%; height: 100%;
    pointer-events: none;
    z-index: 0;
    {texture_css}
}}
.card-bg-image {{
    position: absolute;
    top: 0; left: 0; width: 100%; height: 100%;
    pointer-events: none;
    z-index: 1;
    {bg_image_css}
}}
.card-name {{
    font-size: 22px;
    font-weight: 700;
    color: {text_color};
    margin-bottom: 4px;
    letter-spacing: 2px;
}}
.card-name-en {{
    font-size: 12px;
    font-weight: 400;
    color: {text_secondary_color};
    margin-bottom: 16px;
    letter-spacing: 0.5px;
}}
.card-title {{
    font-size: 13px;
    font-weight: 500;
    color: {accent_color};
    margin-bottom: 24px;
    letter-spacing: 1px;
}}
.card-divider {{
    width: 40px; height: 2px;
    background: {accent_color};
    margin-bottom: 20px;
}}
.card-company {{
    font-size: 14px;
    font-weight: 600;
    color: {text_color};
    margin-bottom: 12px;
}}
.card-contacts {{
    font-size: 11px;
    color: {text_secondary_color};
    line-height: 1.8;
    letter-spacing: 0.5px;
}}
.card-contacts .contact-row {{
    display: flex;
    margin-bottom: 2px;
}}
.card-contacts .contact-label {{
    min-width: 20px;
    font-weight: 700;
    color: {accent_color};
    letter-spacing: 0;
    text-align: center;
    font-family: 'Helvetica Neue', Arial, sans-serif;
}}
.card-contacts .contact-value {{
    flex: 1;
}}
.placeholder-text {{
    color: #D0D0D5;
    font-style: italic;
}}
.card-logo {{
    position: absolute;
    right: {logo_right}px;
    top: {logo_top}px;
    width: {logo_width}px;
    height: {logo_height}px;
    {logo_border_radius}
    overflow: hidden;
    z-index: 10;
    display: flex;
    align-items: center;
    justify-content: center;
    background: transparent;
}}
.card-logo img {{
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
    display: block;
}}
</style>
</head>
<body>
<div class="card-texture"></div>
<div class="card-bg-image"></div>
<div class="card">
    {logo_html}
    <div class="card-name">{name_cn}</div>
    <div class="card-name-en">{name_en}</div>
    <div class="card-title">{title}</div>
    <div class="card-divider"></div>
    <div class="card-company">{company}</div>
    <div class="card-contacts">
        <div class="contact-row"><span class="contact-label">T</span><span class="contact-value">{phone}</span></div>
        <div class="contact-row"><span class="contact-label">@</span><span class="contact-value">{email}</span></div>
        <div class="contact-row"><span class="contact-label">W</span><span class="contact-value">{website}</span></div>
        <div class="contact-row"><span class="contact-label">A</span><span class="contact-value">{address}</span></div>
    </div>
</div>
</body>
</html>"""

# ── 名片背面 CSS 模板（用于预览渲染，RC2 与 PDF 同步） ──
# 结构：统一 flex column，固定顺序 logo → qr → qr_text → content
# 关键规则（与 _render_card_back 保持一致）：
#   1. display:flex; flex-direction:column
#   2. justify-content:center; align-items:center
#   3. gap:16px（与 PDF GAP_PT=8pt @ 6px/mm 等价）
#   4. 无 position:absolute、无 margin:auto、无 translate、无 top:xx%
BUSINESS_CARD_BACK_CSS = """
<html>
<head>
<style>
body {{
    margin: 0; padding: 0;
    width: 568px; height: 347px;
    font-family: 'Noto Sans SC', 'Microsoft YaHei', sans-serif;
    overflow: hidden;
    position: relative;
    background: {bg_color};
}}
.card {{
    width: 568px; height: 347px;
    box-sizing: border-box;
    position: relative;
    background: {bg_gradient};
    z-index: 1;
}}
.card::before {{
    content: '';
    position: absolute;
    {bar_pos}
    {bar_size}
    background: {accent_color};
    z-index: 2;
}}
.card-texture {{
    position: absolute;
    top: 0; left: 0; width: 100%; height: 100%;
    pointer-events: none;
    z-index: 0;
    {texture_css}
}}
.card-bg-image {{
    position: absolute;
    top: 0; left: 0; width: 100%; height: 100%;
    pointer-events: none;
    z-index: 1;
    {bg_image_css}
}}
/* 背面主容器：flex column，统一 gap:16px，禁止混排 */
.card-back {{
    position: relative;
    z-index: 3;
    width: 568px; height: 347px;
    padding: 24px 40px;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    gap: 16px;
    background: transparent;
}}
.back-logo {{
    width: 60px; height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: transparent;
    flex-shrink: 0;
}}
.back-logo img {{
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
    display: block;
}}
.back-logo:empty {{
    display: none;
}}
.back-qr {{
    width: 110px; height: 110px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #EBEBEF;
    border-radius: 4px;
    overflow: hidden;
    flex-shrink: 0;
}}
.back-qr img {{
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
    display: block;
}}
.back-qr-placeholder {{
    color: #8E8E93;
    font-size: 12px;
    letter-spacing: 1px;
}}
.back-qr-text {{
    font-size: 12px;
    color: {text_secondary_color};
    text-align: center;
    letter-spacing: 1px;
    line-height: 1.4;
}}
.back-qr-text:empty {{
    display: none;
}}
.back-content {{
    font-size: 13px;
    line-height: 1.6;
    color: {text_secondary_color};
    text-align: center;
    white-space: pre-wrap;
    max-width: 100%;
}}
.back-content:empty {{
    display: none;
}}
.placeholder-text {{
    color: #D0D0D5;
    font-style: italic;
}}
</style>
</head>
<body>
<div class="card-texture"></div>
<div class="card-bg-image"></div>
<div class="card">
    <div class="card-back">
        <div class="back-logo">{back_logo_html}</div>
        <div class="back-qr">{back_qr_html}</div>
        <div class="back-qr-text">{back_qr_text}</div>
        <div class="back-content">{back_content}</div>
    </div>
</div>
</body>
</html>
"""


# ── 公告 CSS 模板（用于预览渲染） ──
NOTICE_CSS = """
<html>
<head>
<style>
body {{
    margin: 0; padding: 0;
    width: 595px; min-height: 842px;
    font-family: 'Noto Sans SC', 'Microsoft YaHei', sans-serif;
    background: {bg_color};
    position: relative;
    overflow: hidden;
}}
.card {{
    width: 595px; min-height: 842px;
    box-sizing: border-box;
    position: relative;
    background: {bg_gradient};
    z-index: 1;
}}
.card::before {{
    content: '';
    position: absolute;
    {bar_pos}
    {bar_size}
    background: {accent_color};
    z-index: 2;
}}
.card-texture {{
    position: absolute;
    top: 0; left: 0; width: 100%; height: 100%;
    pointer-events: none;
    z-index: 0;
    {texture_css}
}}
.notice-content {{
    padding: 60px 50px;
}}
.notice-title {{
    font-size: {title_size}px;
    font-weight: {title_weight};
    color: {title_color};
    text-align: center;
    margin-bottom: 20px;
    letter-spacing: {title_spacing}px;
    {font_family_style}
}}
.notice-date {{
    font-size: 14px;
    color: {text_secondary_color};
    text-align: center;
    margin-bottom: 30px;
    {font_family_style}
}}
.notice-separator {{
    width: {sep_width}px; height: {sep_height}px;
    background: {accent_color};
    margin: 0 auto 30px auto;
}}
.notice-body {{
    font-size: 16px;
    line-height: 1.8;
    color: {text_color};
    margin-bottom: 40px;
    {font_family_style}
    white-space: pre-wrap;
}}
.notice-issuer {{
    font-size: 16px;
    font-weight: 600;
    color: {text_color};
    text-align: right;
    {font_family_style}
}}
.placeholder-text {{
    color: #D0D0D5;
    font-style: italic;
}}
</style>
</head>
<body>
<div class="card-texture"></div>
<div class="card">
    <div class="notice-content">
        <div class="notice-title">{title}</div>
        <div class="notice-date">{date}</div>
        <div class="notice-separator"></div>
        <div class="notice-body">{body}</div>
        <div class="notice-issuer">{issuer}</div>
    </div>
</div>
</body>
</html>"""


# ── 产品规格 CSS 模板（用于预览渲染） ──
PRODUCT_SPEC_CSS = """
<html>
<head>
<style>
body {{
    margin: 0; padding: 0;
    width: 595px; min-height: 842px;
    font-family: 'Noto Sans SC', 'Microsoft YaHei', sans-serif;
    background: {bg_color};
    position: relative;
    overflow: hidden;
}}
.card {{
    width: 595px; min-height: 842px;
    box-sizing: border-box;
    position: relative;
    background: {bg_gradient};
    z-index: 1;
}}
.card-texture {{
    position: absolute;
    top: 0; left: 0; width: 100%; height: 100%;
    pointer-events: none;
    z-index: 0;
    {texture_css}
}}
.product-header {{
    padding: 40px 50px 30px 50px;
    {header_bg_css}
}}
.product-name {{
    font-size: 28px;
    font-weight: 700;
    color: {header_text_color};
    margin-bottom: 8px;
    letter-spacing: 1px;
}}
.product-version {{
    font-size: 14px;
    color: {version_color};
    font-weight: 500;
}}
.product-description {{
    padding: 0 50px;
    font-size: 15px;
    line-height: 1.7;
    color: {text_color};
    margin-bottom: 30px;
}}
.specs-section {{
    padding: 0 50px;
}}
.specs-title {{
    font-size: 18px;
    font-weight: 600;
    color: {accent_color};
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 2px solid {accent_color};
}}
.specs-table {{
    width: 100%%;
    border-collapse: collapse;
    font-size: 14px;
    {table_style_css}
}}
.specs-table td {{
    padding: 12px 16px;
    {td_style}
}}
.specs-table td:first-child {{
    font-weight: 600;
    color: {text_color};
    width: 35%%;
    {param_style}
}}
.specs-table td:last-child {{
    color: {text_secondary_color};
    {value_style}
}}
.placeholder-text {{
    color: #D0D0D5;
    font-style: italic;
}}
</style>
</head>
<body>
<div class="card-texture"></div>
<div class="card">
    <div class="product-header">
        <div class="product-name">{product_name}</div>
        <div class="product-version">{version}</div>
    </div>
    <div class="product-description">{description}</div>
    <div class="specs-section">
        <div class="specs-title">技术规格</div>
        <table class="specs-table">
            {specs_rows}
        </table>
    </div>
</div>
</body>
</html>"""


# ── 分析报告 CSS 模板（用于预览渲染） ──
REPORT_CSS = """
<html>
<head>
<style>
body {{
    margin: 0; padding: 0;
    width: 595px; min-height: 842px;
    font-family: 'Noto Sans SC', 'Microsoft YaHei', sans-serif;
    background: {bg_color};
    position: relative;
}}
.card {{
    width: 595px; min-height: 842px;
    box-sizing: border-box;
    position: relative;
    background: {bg_gradient};
}}
.report-header {{
    padding: 40px 50px 30px 50px;
    {header_bg_css}
}}
.report-title {{
    font-size: 26px;
    font-weight: 700;
    color: {header_text_color};
    margin-bottom: 6px;
    letter-spacing: 1px;
}}
.report-subtitle {{
    font-size: 15px;
    color: {subtitle_color};
    font-weight: 400;
}}
.report-meta {{
    padding: 0 50px;
    font-size: 13px;
    color: {text_secondary_color};
    margin-bottom: 24px;
}}
.report-summary {{
    padding: 0 50px;
    margin-bottom: 24px;
}}
.report-summary-title {{
    font-size: 14px;
    font-weight: 600;
    color: {accent_color};
    margin-bottom: 8px;
    text-transform: uppercase;
    letter-spacing: 2px;
}}
.report-summary-text {{
    font-size: 14px;
    line-height: 1.7;
    color: {text_color};
    border-left: 3px solid {accent_color};
    padding-left: 12px;
    white-space: pre-wrap;
    word-break: break-word;
    overflow-wrap: break-word;
    overflow: hidden;
}}
.report-sections {{
    padding: 0 50px;
    margin-bottom: 24px;
}}
.report-section-heading {{
    font-size: 16px;
    font-weight: 600;
    color: {accent_color};
    margin-top: 20px;
    margin-bottom: 8px;
    padding-bottom: 4px;
    border-bottom: 1px solid {accent_color}44;
}}
.report-section-heading:first-child {{
    margin-top: 0;
}}
.report-section-body {{
    font-size: 14px;
    line-height: 1.8;
    color: {text_color};
    margin-bottom: 8px;
    white-space: pre-wrap;
    word-break: break-word;
    overflow-wrap: break-word;
    overflow: hidden;
}}
.report-conclusion {{
    padding: 0 50px;
    margin-bottom: 30px;
}}
.report-conclusion-title {{
    font-size: 14px;
    font-weight: 600;
    color: {accent_color};
    margin-bottom: 8px;
}}
.report-conclusion-text {{
    font-size: 14px;
    line-height: 1.7;
    color: {text_color};
    white-space: pre-wrap;
    word-break: break-word;
    overflow-wrap: break-word;
    overflow: hidden;
}}
.report-footer {{
    position: absolute;
    bottom: 20px;
    left: 50px; right: 50px;
    text-align: center;
    font-size: 11px;
    color: {text_secondary_color};
    border-top: 1px solid {text_secondary_color}44;
    padding-top: 8px;
}}
</style>
</head>
<body>
<div class="card">
    <div class="report-header">
        <div class="report-title">{title}</div>
        <div class="report-subtitle">{subtitle}</div>
    </div>
    <div class="report-meta">{meta_text}</div>
    {summary_html}
    <div class="report-sections">{sections_html}</div>
    {conclusion_html}
    {footer_html}
</div>
</body>
</html>"""


# ── 合同协议 CSS 模板（用于预览渲染） ──
CONTRACT_CSS = """
<html>
<head>
<style>
body {{
    margin: 0; padding: 0;
    width: 595px; min-height: 842px;
    font-family: 'Noto Sans SC', 'Microsoft YaHei', sans-serif;
    background: {bg_color};
}}
.card {{
    width: 595px; min-height: 842px;
    box-sizing: border-box;
    background: {bg_gradient};
}}
.contract-header {{
    padding: 30px 50px 20px 50px;
    {header_bg_css}
}}
.contract-title {{
    font-size: 24px;
    font-weight: 700;
    color: {header_text_color};
    text-align: center;
    letter-spacing: 2px;
}}
.contract-no {{
    font-size: 12px;
    color: {text_secondary_color};
    text-align: right;
    padding: 0 50px;
    margin-bottom: 20px;
}}
.contract-parties {{
    padding: 0 50px;
    margin-bottom: 24px;
}}
.party-row {{
    display: flex;
    justify-content: space-between;
    margin-bottom: 8px;
    gap: 28px;
}}
.party-label {{
    font-size: 14px;
    font-weight: 400;
    color: {accent_color};
    min-width: 50px;
}}
.party-name {{
    font-size: 14px;
    font-weight: 400;
    color: {text_color};
    margin-bottom: 2px;
    word-break: break-word;
    overflow-wrap: break-word;
}}
.party-addr {{
    font-size: 12px;
    color: {text_secondary_color};
    word-break: break-word;
    overflow-wrap: break-word;
}}
.contract-divider {{
    margin: 0 50px 20px 50px;
    border: none;
    border-top: 1.5px solid {accent_color};
}}
.contract-terms {{
    padding: 0 50px;
    margin-bottom: 24px;
}}
.contract-term {{
    font-size: 14px;
    line-height: 1.8;
    color: {text_color};
    margin-bottom: 8px;
    white-space: pre-wrap;
    word-break: break-word;
    overflow-wrap: break-word;
    overflow: hidden;
}}
.contract-amount {{
    padding: 0 50px;
    margin-bottom: 20px;
    font-size: 15px;
    font-weight: 600;
    color: {accent_color};
}}
.contract-remark {{
    padding: 0 50px;
    margin-bottom: 30px;
    font-size: 13px;
    color: {text_secondary_color};
    overflow: hidden;
    text-overflow: ellipsis;
    max-height: 60px;
}}
.contract-sign {{
    padding: 0 50px;
    margin-top: 40px;
}}
.sign-row {{
    display: flex;
    justify-content: space-between;
    margin-bottom: 16px;
}}
.sign-block {{
    width: 45%%;
}}
.sign-label {{
    font-size: 13px;
    font-weight: 600;
    color: {text_color};
    margin-bottom: 4px;
}}
.sign-line {{
    border-bottom: 1px solid {text_secondary_color};
    height: 36px;
}}
.contract-date {{
    padding: 0 50px;
    margin-top: 20px;
    font-size: 13px;
    color: {text_secondary_color};
    text-align: center;
}}
</style>
</head>
<body>
<div class="card">
    <div class="contract-header">
        <div class="contract-title">{title}</div>
    </div>
    {contract_no_html}
    <div class="contract-parties">
        <div class="party-row">
            <div>
                <div class="party-label">甲方（委托方）</div>
                <div class="party-name">{party_a}</div>
                <div class="party-addr">{party_a_addr}</div>
            </div>
            <div style="text-align:right;">
                <div class="party-label">乙方（受托方）</div>
                <div class="party-name">{party_b}</div>
                <div class="party-addr">{party_b_addr}</div>
            </div>
        </div>
    </div>
    <hr class="contract-divider">
    <div class="contract-terms">{terms_html}</div>
    {amount_html}
    {remark_html}
    <div class="contract-sign">
        <div class="sign-row">
            <div class="sign-block">
                <div class="sign-label">甲方签章：</div>
                <div class="sign-line"></div>
            </div>
            <div class="sign-block">
                <div class="sign-label">乙方签章：</div>
                <div class="sign-line"></div>
            </div>
        </div>
    </div>
    <div class="contract-date">{date}</div>
</div>
</body>
</html>"""


# ── 发票收据 CSS 模板（用于预览渲染） ──
INVOICE_CSS = """
<html>
<head>
<style>
body {{
    margin: 0; padding: 0;
    width: 595px; min-height: 842px;
    font-family: 'Noto Sans SC', 'Microsoft YaHei', sans-serif;
    background: {bg_color};
}}
.card {{
    width: 595px; min-height: 842px;
    box-sizing: border-box;
    background: {bg_gradient};
    position: relative;
}}
.invoice-outer-border {{
    position: absolute;
    {outer_border_css}
}}
.invoice-inner-border {{
    position: absolute;
    {inner_border_css}
}}
.invoice-single-border {{
    position: absolute;
    {single_border_css}
}}
.invoice-content {{
    padding: 40px 50px;
}}
.invoice-top {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 20px;
}}
.invoice-title {{
    font-size: 28px;
    font-weight: 700;
    color: {accent_color};
    letter-spacing: 4px;
    text-align: center;
    flex: 1;
}}
.invoice-no {{
    font-size: 12px;
    color: {text_secondary_color};
    text-align: right;
    min-width: 160px;
}}
.invoice-no span {{
    display: block;
    margin-bottom: 2px;
}}
.invoice-divider {{
    margin: 0 0 20px 0;
    border: none;
    border-top: 1.5px solid {accent_color};
}}
.invoice-parties {{
    display: flex;
    justify-content: space-between;
    margin-bottom: 24px;
}}
.invoice-party {{
    width: 48%%;
}}
.invoice-party-label {{
    font-size: 12px;
    font-weight: 600;
    color: {accent_color};
    margin-bottom: 4px;
    text-transform: uppercase;
    letter-spacing: 1px;
}}
.invoice-party-name {{
    font-size: 15px;
    font-weight: 600;
    color: {text_color};
    margin-bottom: 2px;
    word-break: break-word;
    overflow-wrap: break-word;
}}
.invoice-party-addr {{
    font-size: 12px;
    color: {text_secondary_color};
    word-break: break-word;
    overflow-wrap: break-word;
}}
.items-table {{
    width: 100%%;
    border-collapse: collapse;
    font-size: 13px;
    margin-bottom: 20px;
}}
.items-table th {{
    background: {accent_color};
    color: #FFFFFF;
    padding: 10px 12px;
    text-align: left;
    font-weight: 600;
    font-size: 12px;
}}
.items-table th:last-child {{
    text-align: right;
}}
.items-table td {{
    padding: 10px 12px;
    border-bottom: 1px solid #E5E5EA;
    color: {text_color};
    word-break: break-word;
    overflow-wrap: break-word;
}}
.items-table td:last-child {{
    text-align: right;
}}
.items-table tr:nth-child(even) td {{
    background: #F9F9FB;
}}
.invoice-total {{
    text-align: right;
    font-size: 18px;
    font-weight: 700;
    color: {accent_color};
    margin-bottom: 20px;
    padding-top: 8px;
    border-top: 2px solid {accent_color};
}}
.invoice-remark {{
    font-size: 12px;
    color: {text_secondary_color};
    margin-bottom: 20px;
    word-break: break-word;
    overflow-wrap: break-word;
    overflow: hidden;
    text-overflow: ellipsis;
    max-height: 60px;
}}
.invoice-remark-label {{
    font-weight: 600;
    color: {text_color};
}}
</style>
</head>
<body>
<div class="card">
    {border_html}
    <div class="invoice-content">
        <div class="invoice-top">
            <div style="width:160px;"></div>
            <div class="invoice-title">{title}</div>
            <div class="invoice-no">{invoice_no_html}</div>
        </div>
        <hr class="invoice-divider">
        <div class="invoice-parties">
            <div class="invoice-party">
                <div class="invoice-party-label">销售方</div>
                <div class="invoice-party-name">{seller}</div>
                <div class="invoice-party-addr">{seller_addr}</div>
            </div>
            <div class="invoice-party" style="text-align:right;">
                <div class="invoice-party-label">购买方</div>
                <div class="invoice-party-name">{buyer}</div>
                <div class="invoice-party-addr">{buyer_addr}</div>
            </div>
        </div>
        <table class="items-table">
            <thead>
                <tr>
                    <th style="width:50%%">项目名称</th>
                    <th style="width:20%%">数量</th>
                    <th style="width:30%%">单价</th>
                </tr>
            </thead>
            <tbody>
                {items_rows}
            </tbody>
        </table>
        {total_html}
        {remark_html}
    </div>
</div>
</body>
</html>"""


# ================================================================
# TemplateEditorPage — 模板编辑页面
# ================================================================
class TemplateEditorPage(QWidget):
    """模板编辑页面：根据模板 JSON fields 动态生成表单，带实时预览"""

    back_requested = Signal()

    def __init__(self, template_id: str):
        super().__init__()
        self.template_id = template_id
        self.template_data = None
        self.field_widgets = {}
        # TPL-05：上传文件路径字典，key = UPLOAD_TEMPLATES 中的 key
        self._uploaded_paths = {}
        self._logo_width_mm = 21.0
        self._logo_right_mm = 5.0
        self._logo_top_mm = 4.0
        self._logo_shape = "square"  # "square" | "circle"

        self._current_side = "front"  # "front" | "back"

        # ── RB-002: per-side state cache（切换正反面保留输入/滚动/预览）──
        # 格式：{side: {"fields": {key: value}, "scroll": int}}
        self._side_state_cache = {
            "front": {"fields": {}, "scroll": 0},
            "back":  {"fields": {}, "scroll": 0},
        }
        # 状态恢复期间抑制 field change 信号，避免触发 N 次预览更新
        self._restoring_state = False

        self._bg_custom_color = ""
        # 背景纹理
        self._bg_texture = "none"
        # 背景图片
        self._bg_image_path = None
        self._bg_image_opacity = 50  # 0-100

        # 字体颜色
        self._text_color = "#2C3E50"
        self._text_secondary_color = "#7F8C8D"

        # 字体风格（notice）
        self._font_style = "formal"
        # 标题栏样式（product_spec）
        self._header_style = "bar"
        # 表格样式（product_spec）
        self._table_style = "striped"

        # 预设应用标志（防止回调循环）
        self._applying_preset = False

        # V1.1 RC1 修复：保存当前主题色，供 apply_theme 兜底扫描使用
        # __init__ 时为空 dict；ThemeManager 第一次触发 apply_theme 时注入真实值
        self._current_theme_colors = {}

        self.preview_timer = QTimer()
        self.preview_timer.setSingleShot(True)
        self.preview_timer.timeout.connect(self._update_preview)

        self._setup_ui()
        self._load_template(template_id)

    # ── 主题切换（V1.1 RC1 修复深色模式残留）──────────────────
    def apply_theme(self, colors: dict):
        """ThemeManager 主题切换时调用。
        完整重绘流程：
        1. reload_qss() — 清除所有内联 stylesheet 缓存
        2. clear_cache() — 清空 self._current_theme_colors 防残留
        3. repaint() — 递归重绘所有子控件
        4. update() — 触发 Qt 事件循环重绘
        5. 重建所有内联样式表，使用 theme token 而非硬编码颜色

        Args:
            colors: 主题色 dict，必须含以下 key：
                    bg / card_bg / hover_bg / input_bg / border / border_light / border_hover
                    text_main / text_sub / text_muted / text_meta
        """
        try:
            self._apply_theme_full(colors)
        except Exception:
            import traceback
            traceback.print_exc()

    def _apply_theme_full(self, colors: dict):
        """完整主题切换流程：
        1. reload_qss — 清除旧样式缓存
        2. clear_cache — 清空主题色缓存
        3. repaint — 递归重绘所有子控件
        4. update — 触发 Qt 事件循环重绘
        """
        # ── Step 1: reload_qss — 清除所有控件的内联样式缓存 ──
        self._reload_qss()

        # ── Step 2: clear_cache — 清空旧主题色缓存 ──
        self._clear_theme_cache()

        # ── Step 3: 重建所有内联样式（使用 token，非硬编码）──
        self._rebuild_inline_styles(colors)

        # ── Step 4: repaint + update — 递归重绘 ──
        self._repaint_all()
        self.update()

    # ── V1.1 真实运行时主题修复：对象有效性守卫 ───────────────
    def _is_widget_alive(self, widget):
        """检查 QWidget / QObject 是否仍然存活（未销毁、未 None）

        比 hasattr 更严格：
        - hasattr 只能检查 Python 属性是否存在
        - shiboken6.isValid 能检测 C++ 端是否已被 deleteLater 销毁
        """
        if widget is None:
            return False
        try:
            if isinstance(widget, QWidget):
                return shiboken6.isValid(widget)
            # 非 QWidget（如 QButtonGroup）也走 isValid
            return shiboken6.isValid(widget)
        except (RuntimeError, TypeError):
            return False

    def _safe_setStyleSheet(self, widget, qss, name="<unknown>"):
        """安全 setStyleSheet：先验证对象有效性，失败则跳过并打印

        Args:
            widget: 目标控件（QWidget / QObject）
            qss: 样式字符串
            name: 控件名称（用于日志）
        Returns:
            bool: True 表示成功应用；False 表示被跳过
        """
        if widget is None:
            print(f"[ThemeFix][SKIP-None] {name}")
            return False
        if not self._is_widget_alive(widget):
            print(f"[ThemeFix][SKIP-Deleted] {name} (id={id(widget)})")
            return False
        try:
            widget.setStyleSheet(qss)
            return True
        except RuntimeError as e:
            print(f"[ThemeFix][SKIP-RuntimeError] {name} → {e}")
            return False
        except Exception as e:
            print(f"[ThemeFix][SKIP-Error] {name} → {e}")
            return False

    def _get_alive_widget(self, attr_name):
        """安全获取 self 上的 widget 属性，返回 widget 或 None

        比 hasattr + getattr 更严格：除了属性存在，还需通过 shiboken6.isValid 验证未销毁
        """
        if not hasattr(self, attr_name):
            return None
        try:
            obj = getattr(self, attr_name)
        except Exception:
            return None
        if not self._is_widget_alive(obj):
            return None
        return obj

    def _reload_qss(self):
        """清除所有控件的内联 stylesheet 缓存，为重建做准备
        V1.1 真实运行时修复：增加对象有效性检查
        """
        widgets = [self] + self.findChildren(QWidget)
        for widget in widgets:
            if widget is None or not self._is_widget_alive(widget):
                continue
            try:
                if widget.styleSheet():
                    widget.setStyleSheet("")
            except (RuntimeError, Exception):
                # 单个 widget 失败不影响整体
                pass

    def _clear_theme_cache(self):
        """清空旧主题色缓存，防止残留"""
        self._current_theme_colors = {}

    def _repaint_all(self):
        """递归重绘所有子控件
        V1.1 真实运行时修复：增加对象有效性检查
        """
        widgets = [self] + self.findChildren(QWidget)
        for widget in widgets:
            if widget is None or not self._is_widget_alive(widget):
                continue
            try:
                widget.style().unpolish(widget)
                widget.style().polish(widget)
                widget.repaint()
                widget.update()
            except Exception:
                pass

    def _style_radio_btn_theme(self, btn: QPushButton, checked: bool, colors: dict):
        """使用主题 token 重建样式选项按钮（5 状态全覆盖：normal/hover/pressed/checked/disabled）

        V1.1 RC 修复（FZ-001）：
          - 之前用 checked bool 切换两份 stylesheet，状态机错误（pressed/disabled 会回退到默认 QSS）
          - 现在改用 CSS 伪类 :hover/:pressed/:checked/:disabled，单 stylesheet 覆盖全状态
        """
        # normal / hover / pressed
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {t('bg_tertiary')};
                color: {t('text_secondary')};
                border: 1px solid {t('border_primary')};
                border-radius: 6px;
                padding: 0 12px;
                min-height: 30px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {t('bg_hover')};
                color: {t('text_primary')};
                border-color: {t('accent')};
            }}
            QPushButton:pressed {{
                background-color: {t('bg_pressed')};
                border-color: {t('accent_pressed')};
            }}
            QPushButton:checked {{
                color: {t('text_primary')};
                border: 1px solid {t('accent')};
                background-color: {t('bg_hover')};
                font-weight: 600;
            }}
            QPushButton:disabled {{
                background-color: {t('bg_disabled')};
                color: {t('text_quaternary')};
                border-color: {t('border_primary')};
            }}
        """)

    def _style_logo_shape_btn_theme(self, active: str, colors: dict):
        """使用主题 token 重建 LOGO 形状按钮（5 状态全覆盖）"""
        # normal / hover / pressed / checked / disabled
        shared_style = f"""
            QPushButton {{
                background-color: {t('bg_tertiary')};
                color: {t('text_secondary')};
                border: 1px solid {t('border_primary')};
                border-radius: 4px;
                padding: 0 12px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {t('bg_hover')};
                color: {t('text_primary')};
                border-color: {t('accent')};
            }}
            QPushButton:pressed {{
                background-color: {t('bg_pressed')};
                border-color: {t('accent_pressed')};
            }}
            QPushButton:checked {{
                color: {t('text_primary')};
                border: 1px solid {t('accent')};
                background-color: {t('bg_hover')};
            }}
            QPushButton:disabled {{
                background-color: {t('bg_disabled')};
                color: {t('text_quaternary')};
                border-color: {t('border_primary')};
            }}
        """
        if hasattr(self, 'logoShapeSquare'):
            self.logoShapeSquare.setStyleSheet(shared_style)
        if hasattr(self, 'logoShapeCircle'):
            self.logoShapeCircle.setStyleSheet(shared_style)

    def _rebuild_inline_styles(self, colors: dict):
        """重建所有内联样式，使用 theme token 而非硬编码颜色"""
        # 保存当前主题色
        self._current_theme_colors = colors

        bg = colors.get('bg', '#FAFAFA')
        card_bg = colors.get('card_bg', '#FFFFFF')
        hover_bg = colors.get('hover_bg', '#F0F0F3')
        input_bg = colors.get('input_bg', '#FFFFFF')
        border = colors.get('border', '#E5E5EA')
        border_light = colors.get('border_light', '#D1D1D6')
        border_hover = colors.get('border_hover', '#C7C7CC')
        text_main = colors.get('text_main', '#1D1D1F')
        text_sub = colors.get('text_sub', '#6E6E73')
        text_muted = colors.get('text_muted', '#AEAEB2')
        text_meta = colors.get('text_meta', '#AEAEB2')
        primary = colors.get('primary', '#4D7CFE')
        primary_light_10 = colors.get('primary_light_10', 'rgba(77, 124, 254, 0.1)')
        white = colors.get('white', '#FFFFFF')
        error = colors.get('error', '#FF3B30')
        success = colors.get('success', '#34C759')
        disabled_bg = colors.get('disabled_bg', '#F2F2F5')

        # ── 重建顶部栏 ──
        self._safe_setStyleSheet(self._get_alive_widget('topBar'), f"""
                QFrame#editorTopBar {{
                    background-color: {bg};
                }}
            """, name='topBar')

        self._safe_setStyleSheet(self._get_alive_widget('breadcrumb'),
            f"color: {text_sub}; font-size: 13px; background-color: transparent;",
            name='breadcrumb')

        self._safe_setStyleSheet(self._get_alive_widget('titleLabel'),
            f"color: {text_main}; font-size: 15px; font-weight: 600; background-color: transparent;",
            name='titleLabel')

        # ── 重建分隔线 ──
        self._safe_setStyleSheet(self._get_alive_widget('editorSeparator'),
            f"QFrame#editorSeparator {{ background-color: {border}; border: none; }}",
            name='editorSeparator')

        # ── 重建表单容器 ──
        self._safe_setStyleSheet(self._get_alive_widget('formContainer'),
            f"background-color: {input_bg};", name='formContainer')

        # ── 重建滚动区域 ──
        self._safe_setStyleSheet(self._get_alive_widget('scrollArea'), f"""
                QScrollArea#editorScrollArea {{
                    background-color: transparent;
                    border: none;
                }}
            """, name='scrollArea')

        # ── 重建预览面板 ──
        self._safe_setStyleSheet(self._get_alive_widget('previewPanel'),
            f"QWidget#previewPanel {{ background-color: {hover_bg}; }}",
            name='previewPanel')

        # ── 重建预览 header ──
        self._safe_setStyleSheet(self._get_alive_widget('previewHeader'), f"""
                QFrame#previewHeader {{
                    background-color: {card_bg};
                    border-bottom: 1px solid {border};
                }}
            """, name='previewHeader')

        self._safe_setStyleSheet(self._get_alive_widget('previewTitleLabel'),
            f"color: {text_main}; font-size: 13px; font-weight: 600; background-color: transparent;",
            name='previewTitleLabel')

        # ── 重建侧边标签（3 状态：normal/hover/selected/disabled）──
        self._safe_setStyleSheet(self._get_alive_widget('sideTabWidget'),
            f"QTabWidget::pane {{ border: none; background: transparent; }}"
            f"QTabBar::tab {{"
            f"    background: transparent; color: {text_sub};"
            f"    border: none; padding: 4px 12px;"
            f"    font-size: 12px; min-width: 60px;"
            f"}}"
            f"QTabBar::tab:hover {{ color: {text_main}; }}"
            f"QTabBar::tab:selected {{"
            f"    color: {primary}; font-weight: 600;"
            f"    border-bottom: 2px solid {primary};"
            f"}}"
            f"QTabBar::tab:disabled {{"
            f"    color: {t('text_quaternary')};"
            f"    background: transparent;"
            f"}}",
            name='sideTabWidget')

        # ── 重建预览内容 ──
        self._safe_setStyleSheet(self._get_alive_widget('previewContent'), f"""
                QFrame#previewContent {{
                    background-color: {colors.get('preview_bg', '#F0F0F2')};
                    border: 1px solid {border};
                    border-radius: 4px;
                }}
            """, name='previewContent')

        # ── 重建底部操作栏 ──
        self._safe_setStyleSheet(self._get_alive_widget('bottomBar'), f"""
                QFrame#editorBottomBar {{
                    background-color: {t('bg_quaternary')};
                    border-top: 1px solid {border};
                }}
            """, name='bottomBar')

        # ── 重建生成按钮（4 状态：normal/hover/pressed/disabled）──
        self._safe_setStyleSheet(self._get_alive_widget('generateBtn'), f"""
                QPushButton#generateBtn {{
                    background-color: {t('accent')};
                    color: {t('on_accent')};
                    border: none;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: 500;
                }}
                QPushButton#generateBtn:hover {{
                    background-color: {t('accent_hover')};
                }}
                QPushButton#generateBtn:pressed {{
                    background-color: {t('accent_pressed')};
                }}
                QPushButton#generateBtn:disabled {{
                    background-color: {t('bg_disabled')};
                    color: {t('text_quaternary')};
                }}
            """, name='generateBtn')

        # ── 重建信息标签 ──
        self._safe_setStyleSheet(self._get_alive_widget('previewInfoLabel'),
            f"color: {text_muted}; font-size: 12px; text-align: center; padding: 12px; background-color: transparent;",
            name='previewInfoLabel')

        # ── RB-003 修复：重建所有字段 label 颜色（CSS class 驱动，跨主题一致）──
        # 之前的 label HTML 内嵌硬编码颜色（#FF3B30/#ECEDF0/#8B8D98），浅色主题下不可见
        # 现在用 .field-req / .field-text class，颜色由本节 setStyleSheet 注入
        _label_qss = f"""
            QLabel#fieldLabel {{
                color: {text_sub};
                font-size: 13px;
                background-color: transparent;
            }}
            QLabel#fieldLabel .field-req {{
                color: {error};
                font-weight: 500;
            }}
            QLabel#fieldLabel .field-text {{
                color: {text_sub};
                font-size: 13px;
            }}
            QLabel#fieldLabel[required="true"] .field-text {{
                color: {text_main};
            }}
        """
        for _lbl in self.findChildren(QLabel):
            if not self._is_widget_alive(_lbl):
                continue
            if _lbl.objectName() == "fieldLabel":
                self._safe_setStyleSheet(_lbl, _label_qss, name='fieldLabel')

        # ── 重建所有字段控件样式（QLineEdit/QTextEdit：normal/focus/disabled）──
        # V1.1 真实运行时修复：删除 field_widgets 缓存依赖，改用 findChildren 实时获取
        for widget in self.findChildren(QLineEdit):
            if not self._is_widget_alive(widget):
                continue
            self._safe_setStyleSheet(widget, f"""
                    QLineEdit {{
                        background-color: {input_bg};
                        color: {text_main};
                        border: 1px solid {border};
                        border-radius: 6px;
                        padding: 0 12px;
                        font-size: 13px;
                        min-height: 36px;
                    }}
                    QLineEdit:focus {{
                        border: 2px solid {primary};
                    }}
                    QLineEdit:disabled {{
                        background-color: {t('bg_disabled')};
                        color: {t('text_quaternary')};
                        border: 1px solid {t('border_primary')};
                    }}
                """, name=f'QLineEdit[{widget.objectName() or "anon"}]')

        for widget in self.findChildren(QTextEdit):
            if not self._is_widget_alive(widget):
                continue
            self._safe_setStyleSheet(widget, f"""
                    QTextEdit {{
                        background-color: {input_bg};
                        color: {text_main};
                        border: 1px solid {border};
                        border-radius: 6px;
                        padding: 8px 12px;
                        font-size: 13px;
                    }}
                    QTextEdit:focus {{
                        border: 2px solid {primary};
                    }}
                    QTextEdit:disabled {{
                        background-color: {t('bg_disabled')};
                        color: {t('text_quaternary')};
                        border: 1px solid {t('border_primary')};
                    }}
                """, name=f'QTextEdit[{widget.objectName() or "anon"}]')

        # ── 重建中间分隔线 ──
        for child in self.findChildren(QFrame):
            if not self._is_widget_alive(child):
                continue
            if not child.objectName() and child.width() == 1:
                self._safe_setStyleSheet(child, f"background-color: {border};",
                    name='separatorLine[HLine]')

        # ── 重建表单中的分组卡片 ──
        for child in self.findChildren(QFrame):
            if not self._is_widget_alive(child):
                continue
            name = child.objectName()
            if name.startswith('groupCard_') or name == 'formCard':
                self._safe_setStyleSheet(child, f"""
                    QFrame {{
                        background-color: {card_bg};
                        border: 1px solid {border};
                        border-radius: 8px;
                    }}
                """, name=f'groupCard[{name}]')
            elif name.startswith('styleCard'):
                self._safe_setStyleSheet(child, f"""
                    QFrame {{
                        background-color: {card_bg};
                        border: 1px solid {border};
                        border-radius: 8px;
                    }}
                """, name=f'styleCard[{name}]')
            elif name.startswith('uploadCard'):
                self._safe_setStyleSheet(child, f"""
                    QFrame {{
                        background-color: {card_bg};
                        border: 1px solid {border};
                        border-radius: 8px;
                    }}
                """, name=f'uploadCard[{name}]')

        # ── 重建样式卡片中的分隔线 ──
        for child in self.findChildren(QFrame):
            if not self._is_widget_alive(child):
                continue
            if child.frameShape() == QFrame.HLine and child.objectName() == "":
                self._safe_setStyleSheet(child,
                    f"background-color: {border}; max-height: 1px;",
                    name='styleCardHLine')

        # ── 重建样式选项按钮（theme_color radio 用 CSS 伪类 5 状态）──
        # V1.1 真实运行时修复：删除 style_widgets 缓存依赖，改用 findChildren 实时获取
        # 通过 property("theme_value") 识别 theme_color 按钮
        # 通过 objectName 模式识别 bar_position/bg_style/bg_texture/font_style/header_style/table_style 按钮
        for btn in self.findChildren(QPushButton):
            if not self._is_widget_alive(btn):
                continue
            color_val = btn.property("theme_value")
            if color_val:
                # theme_color 按钮：8 个主题色按钮：5 状态
                self._safe_setStyleSheet(btn, f"""
                                QPushButton {{
                                    background-color: {color_val};
                                    border-radius: 14px;
                                    border: 2px solid transparent;
                                }}
                                QPushButton:hover {{
                                    border-color: {t('text_primary')};
                                }}
                                QPushButton:pressed {{
                                    border-color: {t('accent_pressed')};
                                }}
                                QPushButton:checked {{
                                    border: 3px solid {t('text_primary')};
                                }}
                                QPushButton:disabled {{
                                    opacity: 0.4;
                                }}
                            """, name=f'themeColorBtn[val={color_val}]')
            else:
                obj_name = btn.objectName() or ""
                if (obj_name.startswith('barOption_') or obj_name.startswith('bgOption_')
                        or obj_name.startswith('textureOption_')
                        or obj_name.startswith('fontOption_')
                        or obj_name.startswith('headerOption_')
                        or obj_name.startswith('tableOption_')):
                    # bar_position / bg_style / bg_texture / font_style / header_style / table_style radio
                    self._style_radio_btn_theme(btn, btn.isChecked(), colors)

        # ── 重建背景颜色按钮（4 状态：normal/hover/pressed/disabled）──
        bg_color_btn = self._get_alive_widget('bgColorBtn')
        if bg_color_btn:
            if self._bg_custom_color:
                self._safe_setStyleSheet(bg_color_btn, f"""
                    QPushButton {{
                        background-color: {self._bg_custom_color};
                        border: 1px solid {primary};
                        border-radius: 4px;
                    }}
                    QPushButton:hover {{ border: 2px solid {primary}; }}
                    QPushButton:pressed {{ border: 2px solid {t('accent_pressed')}; }}
                    QPushButton:disabled {{
                        background-color: {t('bg_disabled')};
                        border: 1px solid {t('border_primary')};
                    }}
                """, name='bgColorBtn[custom]')
            else:
                self._safe_setStyleSheet(bg_color_btn, f"""
                    QPushButton {{
                        background-color: {hover_bg};
                        border: 1px solid {border};
                        border-radius: 4px;
                    }}
                    QPushButton:hover {{ border: 1px solid {primary}; }}
                    QPushButton:pressed {{ border: 1px solid {t('accent_pressed')}; }}
                    QPushButton:disabled {{
                        background-color: {t('bg_disabled')};
                        border: 1px solid {t('border_primary')};
                    }}
                """, name='bgColorBtn[default]')

        # ── 重建字体颜色按钮（4 状态）──
        self._safe_setStyleSheet(self._get_alive_widget('textColorBtn'), f"""
                QPushButton {{
                    background-color: {self._text_color};
                    border: 1px solid {border};
                    border-radius: 4px;
                }}
                QPushButton:hover {{ border: 1px solid {primary}; }}
                QPushButton:pressed {{ border: 1px solid {t('accent_pressed')}; }}
                QPushButton:disabled {{
                    background-color: {t('bg_disabled')};
                    border: 1px solid {t('border_primary')};
                }}
            """, name='textColorBtn')

        self._safe_setStyleSheet(self._get_alive_widget('secondaryColorBtn'), f"""
                QPushButton {{
                    background-color: {self._text_secondary_color};
                    border: 1px solid {border};
                    border-radius: 4px;
                }}
                QPushButton:hover {{ border: 1px solid {primary}; }}
                QPushButton:pressed {{ border: 1px solid {t('accent_pressed')}; }}
                QPushButton:disabled {{
                    background-color: {t('bg_disabled')};
                    border: 1px solid {t('border_primary')};
                }}
            """, name='secondaryColorBtn')

        # ── 重建背景图片按钮（4 状态）──
        self._safe_setStyleSheet(self._get_alive_widget('bgImageBtn'), f"""
                QPushButton {{
                    background-color: {hover_bg};
                    color: {text_main};
                    border: 1px solid {border};
                    border-radius: 4px;
                    padding: 0 12px;
                }}
                QPushButton:hover {{ border-color: {primary}; }}
                QPushButton:pressed {{ border-color: {t('accent_pressed')}; }}
                QPushButton:disabled {{
                    background-color: {t('bg_disabled')};
                    color: {t('text_quaternary')};
                    border-color: {t('border_primary')};
                }}
            """, name='bgImageBtn')

        # ── 重建清除按钮（clear_bg/clear_text/clear_secondary/clear_bg_img，4 状态）──
        clear_btn_shared = f"""
            QPushButton {{
                background-color: {t('bg_tertiary')};
                color: {t('text_secondary')};
                border: 1px solid {t('border_primary')};
                border-radius: 4px;
                padding: 0 12px;
            }}
            QPushButton:hover {{
                background-color: {t('bg_hover')};
                color: {t('text_primary')};
                border-color: {t('accent')};
            }}
            QPushButton:pressed {{
                background-color: {t('bg_pressed')};
                border-color: {t('accent_pressed')};
            }}
            QPushButton:disabled {{
                background-color: {t('bg_disabled')};
                color: {t('text_quaternary')};
                border-color: {t('border_primary')};
            }}
        """
        # V1.1 真实运行时修复：删除硬编码清除按钮列表，改用 findChildren 按 objectName 实时获取
        _clear_btn_object_names = {
            "clear_bg_btn", "clear_text_btn", "clear_secondary_btn",
            "clear_bg_img_btn", "clearUploadBtn",
        }
        for btn in self.findChildren(QPushButton):
            if not self._is_widget_alive(btn):
                continue
            if btn.objectName() in _clear_btn_object_names:
                self._safe_setStyleSheet(btn, clear_btn_shared,
                    name=f'clearBtn[{btn.objectName()}]')

        # ── 重建 LOGO 形状按钮 ──
        if self._is_widget_alive(getattr(self, 'logoShapeSquare', None)):
            active = "square" if self._logo_shape == "square" else "circle"
            self._style_logo_shape_btn_theme(active, colors)

        # ── 重建表格样式 ──
        for child in self.findChildren(QTableWidget):
            if not self._is_widget_alive(child):
                continue
            self._safe_setStyleSheet(child, f"""
                QTableWidget {{
                    background-color: {input_bg};
                    color: {text_main};
                    border: 1px solid {border};
                    border-radius: 6px;
                    gridline-color: {border};
                    word-wrap: break-word;
                }}
                QTableWidget::item {{
                    padding: 4px;
                    text-align: left;
                    word-wrap: break-word;
                }}
                QTableWidget::item:selected {{
                    background-color: {primary_light_10};
                }}
                QTableWidget QHeaderView::section {{
                    background-color: {hover_bg};
                    color: {text_sub};
                    padding: 6px;
                    border: none;
                    font-size: 12px;
                }}
                QTableWidget:focus {{
                    border: 2px solid {primary};
                }}
            """, name=f'QTableWidget[{child.objectName() or "anon"}]')

        # ── 重建上传区域样式（per-key：uploadBtn_{key} / uploadPreview_{key}）──
        upload_widgets = getattr(self, "_upload_widgets", {}) or {}
        for key, widgets in upload_widgets.items():
            upload_btn = widgets.get("upload_btn")
            if not self._is_widget_alive(upload_btn):
                continue
            self._safe_setStyleSheet(upload_btn, f"""
                QPushButton#{upload_btn.objectName()} {{
                    background-color: {hover_bg};
                    color: {text_main};
                    border: 1px solid {border_light};
                    border-radius: 6px;
                    padding: 0 16px;
                    font-size: 13px;
                }}
                QPushButton#{upload_btn.objectName()}:hover {{
                    background-color: {card_bg};
                    border-color: {primary};
                }}
            """, name=f'uploadBtn_{key}')

            preview_label = widgets.get("preview_label")
            if self._is_widget_alive(preview_label):
                cur_path = self._uploaded_paths.get(key)
                if cur_path and os.path.isfile(cur_path):
                    self._safe_setStyleSheet(preview_label,
                        f"color: {primary}; font-size: 12px; background-color: transparent;",
                        name=f'uploadPreview_{key}[uploaded]')
                else:
                    self._safe_setStyleSheet(preview_label,
                        f"color: {text_sub}; font-size: 12px; background-color: transparent;",
                        name=f'uploadPreview_{key}[empty]')

        # ── 重建 QComboBox 样式（4 状态：normal/hover/focus/disabled）──
        self._safe_setStyleSheet(self._get_alive_widget('_preset_selector'), f"""
                QComboBox {{
                    background-color: {input_bg}; color: {text_main};
                    border: 1px solid {border}; border-radius: 6px;
                    padding: 0 12px; font-size: 12px; min-height: 32px;
                }}
                QComboBox:hover {{ border: 1px solid {primary}; }}
                QComboBox:focus {{ border: 2px solid {primary}; }}
                QComboBox::drop-down {{
                    border: none; width: 20px; padding-right: 8px;
                }}
                QComboBox:disabled {{
                    background-color: {t('bg_disabled')};
                    color: {t('text_quaternary')};
                    border: 1px solid {t('border_primary')};
                }}
            """, name='_preset_selector')

        # ── 重建 QSpinBox 样式 ──
        for child in self.findChildren(QDoubleSpinBox):
            if not self._is_widget_alive(child):
                continue
            self._safe_setStyleSheet(child, f"""
                QDoubleSpinBox {{
                    background-color: {input_bg}; color: {text_main};
                    border: 1px solid {border}; border-radius: 4px;
                    padding: 2px 8px; font-size: 12px;
                }}
                QDoubleSpinBox:focus {{ border: 2px solid {primary}; }}
                QDoubleSpinBox:disabled {{
                    background-color: {t('bg_disabled')};
                    color: {t('text_quaternary')};
                    border: 1px solid {t('border_primary')};
                }}
            """, name=f'QDoubleSpinBox[{child.objectName() or "anon"}]')

        # ── 重建 QSlider 样式 ──
        for child in self.findChildren(QSlider):
            if not self._is_widget_alive(child):
                continue
            self._safe_setStyleSheet(child, f"""
                QSlider::groove:horizontal {{
                    height: 4px; background: {border}; border-radius: 2px;
                }}
                QSlider::handle:horizontal {{
                    background: {primary}; width: 14px; height: 14px;
                    margin: -5px 0; border-radius: 7px;
                }}
                QSlider::sub-page:horizontal {{
                    background: {primary}; border-radius: 2px;
                }}
            """, name=f'QSlider[{child.objectName() or "anon"}]')

        # ── 重建清除按钮样式 ──
        for child in self.findChildren(QPushButton):
            if not self._is_widget_alive(child):
                continue
            if child.objectName() == "clearUploadBtn":
                self._safe_setStyleSheet(child, f"""
                    QPushButton#clearUploadBtn {{
                        background-color: transparent;
                        color: {text_muted};
                        border: none;
                        font-size: 12px;
                    }}
                    QPushButton#clearUploadBtn:hover {{
                        color: {error};
                    }}
                """, name='clearUploadBtn[inline]')

        # ── 更新预览（使用新主题色）──
        self._update_preview()

    # ── UI 构建 ────────────────────────────────────────────────
    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # ── 顶部栏（优化：压缩高度，合并标题） ──
        self.topBar = QFrame()
        self.topBar.setFixedHeight(48)
        self.topBar.setObjectName("editorTopBar")
        self.topBar.setStyleSheet(
            "QFrame#editorTopBar {"
            f"    background-color: {t('transparent')};"
            "}"
        )
        top_layout = QHBoxLayout(self.topBar)
        top_layout.setContentsMargins(24, 0, 24, 0)
        top_layout.setSpacing(12)

        self.backBtn = QPushButton("← 返回")
        self.backBtn.setObjectName("backBtn")
        self.backBtn.setFixedHeight(32)
        self.backBtn.clicked.connect(self.back_requested.emit)
        top_layout.addWidget(self.backBtn)

        # 面包屑导航
        self.breadcrumb = QLabel("模板编辑 / ")
        self.breadcrumb.setObjectName("breadcrumbLabel")
        self.breadcrumb.setStyleSheet(
            f"color: {t('text_secondary')}; font-size: 13px; background-color: {t('transparent')};"
        )
        top_layout.addWidget(self.breadcrumb)

        self.titleLabel = QLabel("")
        self.titleLabel.setObjectName("headingH2")
        self.titleLabel.setStyleSheet(
            f"color: {t('text_primary')}; font-size: 15px; font-weight: 600; background-color: transparent;"
        )
        top_layout.addWidget(self.titleLabel, stretch=1)

        main_layout.addWidget(self.topBar)

        # ── 分隔线 ──
        self.editorSeparator = QFrame()
        self.editorSeparator.setFixedHeight(1)
        self.editorSeparator.setObjectName("editorSeparator")
        self.editorSeparator.setStyleSheet(
            "QFrame#editorSeparator {"
            f"    background-color: {t('border_secondary')};"
            "    border: none;"
            "}"
        )
        main_layout.addWidget(self.editorSeparator)

        # ── 主内容区（表单 + 预览分栏） ──
        content_wrapper = QWidget()
        content_wrapper.setObjectName("contentWrapper")
        content_wrapper.setStyleSheet("background-color: transparent;")
        content_layout = QHBoxLayout(content_wrapper)
        content_layout.setSpacing(0)
        content_layout.setContentsMargins(0, 0, 0, 0)

        # ── 左侧表单区域 ──
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setObjectName("editorScrollArea")
        self.scrollArea.setStyleSheet(
            "QScrollArea#editorScrollArea {"
            "    background-color: transparent;"
            "    border: none;"
            "}"
        )

        self.formContainer = QWidget()
        self.formContainer.setObjectName("formContainer")
        self.formContainer.setStyleSheet(f"background-color: {t('bg_tertiary')};")
        self.formLayout = QVBoxLayout(self.formContainer)
        self.formLayout.setSpacing(20)
        self.formLayout.setContentsMargins(24, 16, 24, 16)

        self.scrollArea.setWidget(self.formContainer)
        self.scrollArea.setMinimumWidth(460)
        self.scrollArea.setMaximumWidth(520)
        content_layout.addWidget(self.scrollArea)

        # ── 中间分隔线 ──
        mid_sep = QFrame()
        mid_sep.setFixedWidth(1)
        mid_sep.setStyleSheet(
            "QFrame {"
            f"    background-color: {t('border_secondary')};"
            "}"
        )
        content_layout.addWidget(mid_sep)

        # ── 右侧预览面板 ──
        self.previewPanel = QWidget()
        self.previewPanel.setObjectName("previewPanel")
        self.previewPanel.setStyleSheet(
            "QWidget#previewPanel {"
            f"    background-color: {t('bg_secondary')};"
            "}"
        )
        preview_layout = QVBoxLayout(self.previewPanel)
        preview_layout.setSpacing(0)
        preview_layout.setContentsMargins(0, 0, 0, 0)

        # 预览标题栏
        self.previewHeader = QFrame()
        self.previewHeader.setFixedHeight(44)
        self.previewHeader.setObjectName("previewHeader")
        self.previewHeader.setStyleSheet(
            "QFrame#previewHeader {"
            f"    background-color: {t('bg_secondary')};"
            f"    border-bottom: 1px solid {t('border_secondary')};"
            "}"
        )
        preview_header_layout = QHBoxLayout(self.previewHeader)
        preview_header_layout.setContentsMargins(20, 0, 20, 0)
        self.previewTitleLabel = QLabel("  实时预览")
        self.previewTitleLabel.setObjectName("previewTitle")
        self.previewTitleLabel.setStyleSheet(
            f"color: {t('text_primary')}; font-size: 13px; font-weight: 600; background-color: transparent;"
        )
        preview_header_layout.addWidget(self.previewTitleLabel)

        # 正反面切换标签（仅名片模板显示）
        self.sideTabWidget = QTabWidget()
        self.sideTabWidget.setObjectName("sideTabs")
        self.sideTabWidget.setStyleSheet(
            "QTabWidget::pane { border: none; background: transparent; }"
            "QTabBar::tab {"
            f"    background: transparent; color: {t('text_secondary')};"
            "    border: none; padding: 4px 12px;"
            "    font-size: 12px; min-width: 60px;"
            "}"
            "QTabBar::tab:selected {"
            f"    color: {t('accent')}; font-weight: 600;"
            f"    border-bottom: 2px solid {t('accent')};"
            "}"
            f"QTabBar::tab:hover {{ color: {t('text_primary')}; }}"
        )
        self.sideTabWidget.setTabPosition(QTabWidget.North)
        self.sideTabWidget.setDocumentMode(True)
        self.frontSideTab = QWidget()
        self.backSideTab = QWidget()
        self.sideTabWidget.addTab(self.frontSideTab, "正面")
        self.sideTabWidget.addTab(self.backSideTab, "背面")
        self.sideTabWidget.currentChanged.connect(self._on_side_changed)
        self.sideTabWidget.setVisible(False)
        preview_header_layout.addWidget(self.sideTabWidget)

        preview_header_layout.addStretch()
        preview_layout.addWidget(self.previewHeader)

        # 预览内容容器（带边框和阴影效果）
        self.previewContent = QFrame()
        self.previewContent.setObjectName("previewContent")
        self.previewContent.setStyleSheet(
            "QFrame#previewContent {"
            f"    background-color: {t('bg_hover')};"
            f"    border: 1px solid {t('border_secondary')};"
            "    border-radius: 4px;"
            "}"
        )
        preview_content_layout = QVBoxLayout(self.previewContent)
        preview_content_layout.setSpacing(0)
        preview_content_layout.setContentsMargins(12, 12, 12, 12)

        # 预览内容
        try:
            from PySide6.QtWebEngineWidgets import QWebEngineView
            self.previewView = QWebEngineView()
            self.previewView.setObjectName("previewView")
            self.previewView.setStyleSheet(f"background-color: {t('on_accent')}; border: none;")
            self.previewView.setMinimumHeight(300)
            self.webengine_available = True
            preview_content_layout.addWidget(self.previewView, stretch=1)
        except Exception as e:
            import traceback
            err_msg = f"{type(e).__name__}: {e}"
            # 写入日志文件（console=False 时 print 不可见）
            try:
                log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'webengine_error.log')
                with open(log_path, 'w', encoding='utf-8') as f:
                    f.write(f"WebEngine Error: {err_msg}\n\n")
                    traceback.print_exc(file=f)
            except Exception:
                pass
            traceback.print_exc()
            print(f"[WARN] WebEngine 不可用: {err_msg}")
            self.previewView = None
            self.webengine_available = False
            self.fallbackPreview = QLabel()
            self.fallbackPreview.setObjectName("fallbackPreview")
            self.fallbackPreview.setStyleSheet(
                "QLabel#fallbackPreview {"
                f"    color: {t('text_tertiary')}; font-size: 14px; text-align: center; "
                "    padding: 40px; background-color: transparent; "
                f"    border: 1px dashed {t('border_primary')}; border-radius: 4px;"
                "}"
            )
            self.fallbackPreview.setAlignment(Qt.AlignCenter)
            self.fallbackPreview.setText("预览需要安装 PySide6-WebEngine")
            preview_content_layout.addWidget(self.fallbackPreview, stretch=1)

        preview_layout.addWidget(self.previewContent, stretch=1)

        # 预览信息
        self.previewInfoLabel = QLabel("填写左侧表单以查看效果")
        self.previewInfoLabel.setObjectName("previewInfo")
        self.previewInfoLabel.setStyleSheet(
            f"color: {t('text_quaternary')}; font-size: 12px; text-align: center; padding: 12px; background-color: transparent;"
        )
        self.previewInfoLabel.setAlignment(Qt.AlignCenter)
        preview_layout.addWidget(self.previewInfoLabel)

        content_layout.addWidget(self.previewPanel, stretch=1)

        main_layout.addWidget(content_wrapper, stretch=1)

        # ── 底部操作栏（优化：加深背景，增强按钮） ──
        bottom_bar = QFrame()
        bottom_bar.setFixedHeight(64)
        bottom_bar.setObjectName("editorBottomBar")
        bottom_bar.setStyleSheet(
            "QFrame#editorBottomBar {"
            f"    background-color: {t('bg_primary')};"
            f"    border-top: 1px solid {t('border_secondary')};"
            "}"
        )
        bottom_layout = QHBoxLayout(bottom_bar)
        bottom_layout.setContentsMargins(24, 12, 24, 12)
        bottom_layout.setSpacing(12)

        bottom_layout.addStretch()

        self.resetBtn = QPushButton("重置")
        self.resetBtn.setObjectName("resetBtn")
        self.resetBtn.setFixedSize(100, 36)
        self.resetBtn.clicked.connect(self._reset_form)
        bottom_layout.addWidget(self.resetBtn)

        self.generateBtn = QPushButton("生成 PDF")
        self.generateBtn.setObjectName("generateBtn")
        self.generateBtn.setFixedSize(160, 40)
        self.generateBtn.setStyleSheet(
            "QPushButton#generateBtn {"
            f"    background-color: {t('accent')};"
            f"    color: {t('on_accent')};"
            "    border: none;"
            "    border-radius: 8px;"
            "    font-size: 14px;"
            "    font-weight: 500;"
            "}"
            "QPushButton#generateBtn:hover {"
            f"    background-color: {t('accent_hover')};"
            "}"
            "QPushButton#generateBtn:pressed {"
            "    background-color: #3560E0;"
            "}"
        )
        self.generateBtn.clicked.connect(self._generate_pdf)
        bottom_layout.addWidget(self.generateBtn)

        main_layout.addWidget(bottom_bar)

    # ── 模板加载 ───────────────────────────────────────────────
    def load_template(self, template_id: str):
        self.template_id = template_id
        # 切换模板时重置上传文件路径，避免旧模板的图片被带到新模板
        self._uploaded_paths = {}
        self._load_template(template_id)

    def _load_template(self, template_id: str):
        # 支持两种位置：assets/templates/{id}.json 和 assets/templates/presets/{id}.json
        candidates = [
            os.path.join(TEMPLATES_PATH, f"{template_id}.json"),
            os.path.join(TEMPLATES_PATH, "presets", f"{template_id}.json"),
        ]
        json_path = next((p for p in candidates if os.path.isfile(p)), candidates[0])
        if not os.path.isfile(json_path):
            QMessageBox.warning(self, "模板不存在", f"未找到模板文件：{json_path}")
            return

        try:
            with open(json_path, encoding="utf-8") as f:
                self.template_data = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            QMessageBox.critical(self, "模板加载失败", str(e))
            return

        name = self.template_data.get("name", template_id)
        icon = self.template_data.get("icon", "")
        self.breadcrumb.setText("模板编辑 / ")
        self.titleLabel.setText(f"{icon}  {name}")

        sides = self.template_data.get("sides", [])
        if len(sides) >= 2:
            self.sideTabWidget.setVisible(True)
        else:
            self.sideTabWidget.setVisible(False)

        self._current_side = "front"
        if self.sideTabWidget.isVisible():
            self.sideTabWidget.setCurrentIndex(0)

        # ── RB-002: 模板加载时重置 per-side state cache（避免旧模板的字段污染新模板）──
        self._side_state_cache = {
            "front": {"fields": {}, "scroll": 0},
            "back":  {"fields": {}, "scroll": 0},
        }

        self._build_form()

        # ── 发票收据：从 sample 填充 items 表格初始数据 ──
        if template_id == "invoice":
            sample_data = self.template_data.get("sample", {})
            sample_items = sample_data.get("items", [])
            items_widget = self.field_widgets.get("items")
            if isinstance(sample_items, list) and sample_items and isinstance(items_widget, QTableWidget):
                # 只有表格为空（仅默认1行空白）时才填充
                has_data = False
                for r in range(items_widget.rowCount()):
                    for c in range(3):
                        it = items_widget.item(r, c)
                        if it and it.text().strip():
                            has_data = True
                            break
                    if has_data:
                        break
                if not has_data:
                    items_widget.blockSignals(True)
                    items_widget.setRowCount(len(sample_items))
                    for r, item in enumerate(sample_items):
                        if isinstance(item, dict):
                            items_widget.setItem(r, 0, QTableWidgetItem(item.get("name", "")))
                            items_widget.setItem(r, 1, QTableWidgetItem(str(item.get("qty", ""))))
                            items_widget.setItem(r, 2, QTableWidgetItem(str(item.get("price", ""))))
                        # 行级删除按钮
                        del_btn = QPushButton("×")
                        del_btn.setFixedSize(24, 24)
                        del_btn.setStyleSheet(
                            "QPushButton {"
                            f"    color: {t('error')};"
                            "    border: none;"
                            "    border-radius: 12px;"
                            "    font-size: 14px;"
                            "    font-weight: bold;"
                            "    background: transparent;"
                            "}"
                            "QPushButton:hover {"
                            "    background-color: rgba(255,59,48,0.1);"
                            "}"
                        )
                        del_btn.clicked.connect(lambda checked, w=items_widget, row=r: self._delete_invoice_row(w, row))
                        items_widget.setCellWidget(r, 3, del_btn)
                    items_widget.blockSignals(False)
                    self._update_invoice_total(items_widget)

        self._update_preview()

    # ── 动态表单构建（支持分组） ──────────────────────────────────
    def _build_form(self):
        while self.formLayout.count():
            item = self.formLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

        fields = self.template_data.get("fields", [])
        self.field_widgets.clear()

        # 检查是否有分组定义
        groups = FIELD_GROUPS.get(self.template_id, None)

        if groups:
            # 使用分组布局
            self._build_grouped_form(fields, groups)
        else:
            # 回退到平铺布局
            self._build_flat_form(fields)

    def _build_grouped_form(self, fields, groups):
        field_dict = {f["key"]: f for f in fields}

        # ── 样式选项卡片 ──
        style_options = self.template_data.get("style_options", {})
        if style_options:
            self._build_style_card(style_options)

        for group_idx, group in enumerate(groups):
            group_keys = group["keys"]
            group_fields = []
            for k in group_keys:
                if k in field_dict:
                    field = field_dict[k]
                    # 如果模板支持双面，过滤当前面的字段
                    if "sides" in self.template_data:
                        field_side = field.get("side", "front")
                        if field_side != self._current_side:
                            continue
                    group_fields.append(field)

            if not group_fields:
                continue

            # 分组标题
            group_header = QLabel(f"{group['icon']}  {group['title']}")
            group_header.setObjectName("groupTitle")
            group_header.setStyleSheet(
                f"color: {t('text_primary')}; font-size: 13px; font-weight: 600; "
                "background-color: transparent; padding-top: 4px;"
            )
            self.formLayout.addWidget(group_header)

            # 分组卡片容器
            card = QFrame()
            card.setObjectName(f"groupCard_{group['title']}")
            card.setStyleSheet(
                "QFrame {"
                f"    background-color: {t('bg_secondary')};"
                f"    border: 1px solid {t('border_secondary')};"
                "    border-radius: 8px;"
                "}"
            )
            card_layout = QVBoxLayout(card)
            card_layout.setSpacing(12)
            card_layout.setContentsMargins(16, 16, 16, 16)

            for field in group_fields:
                self._add_field_to_layout(card_layout, field)

            self.formLayout.addWidget(card)

            # 组间间距（最后一组不加）
            if group_idx < len(groups) - 1:
                self.formLayout.addSpacing(8)

        # ── TPL-05：上传区域（如果模板配置了的话）──────────────
        self._add_upload_section()

        self.formLayout.addStretch()

    def _build_flat_form(self, fields):
        # ── 样式选项卡片 ──
        style_options = self.template_data.get("style_options", {})
        if style_options:
            self._build_style_card(style_options)

        card = QFrame()
        card.setObjectName("formCard")
        card.setStyleSheet(
            "QFrame {"
            f"    background-color: {t('bg_secondary')};"
            f"    border: 1px solid {t('border_secondary')};"
            "    border-radius: 8px;"
            "}"
        )
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(12)
        card_layout.setContentsMargins(16, 16, 16, 16)

        for field in fields:
            self._add_field_to_layout(card_layout, field)

        card_layout.addStretch()
        self.formLayout.addWidget(card)

        # ── TPL-05：上传区域（如果模板配置了的话）──────────────
        self._add_upload_section()

        self.formLayout.addStretch()

    def _build_style_card(self, style_options: dict):
        """构建样式选项卡片（主题色、装饰条位置、背景样式）"""
        style_header = QLabel("  样式设置")
        style_header.setObjectName("styleHeader")
        style_header.setStyleSheet(
            f"color: {t('text_primary')}; font-size: 13px; font-weight: 600; "
            "background-color: transparent; padding-top: 4px;"
        )
        self.formLayout.addWidget(style_header)

        style_card = QFrame()
        style_card.setObjectName("styleCard")
        style_card.setStyleSheet(
            "QFrame {"
            f"    background-color: {t('bg_secondary')};"
            f"    border: 1px solid {t('border_secondary')};"
            "    border-radius: 8px;"
            "}"
        )
        style_layout = QVBoxLayout(style_card)
        style_layout.setSpacing(16)
        style_layout.setContentsMargins(16, 16, 16, 16)

        # 存储样式控件引用
        self.style_widgets = {}

        # ── AT-08: 样式预设选择器 ──
        self._preset_selector = QComboBox()
        self._preset_selector.setObjectName("presetSelector")
        self._preset_selector.setStyleSheet(
            "QComboBox {"
            f"    background-color: {t('bg_tertiary')}; color: {t('text_primary')};"
            f"    border: 1px solid {t('border_secondary')}; border-radius: 6px;"
            "    padding: 0 12px; font-size: 12px; min-height: 32px;"
            "}"
            f"QComboBox:focus {{ border: 2px solid {t('accent')}; }}"
            "QComboBox::drop-down {"
            "    border: none; width: 20px; padding-right: 8px;"
            "}"
        )
        self._preset_selector.addItem("-- 选择样式预设 --", "")
        self._load_presets()
        self._preset_selector.currentIndexChanged.connect(self._on_preset_selected)
        style_layout.addWidget(self._preset_selector)
        style_layout.addSpacing(8)

        # 主题色选择
        theme_cfg = style_options.get("theme_color", {})
        if theme_cfg:
            theme_label = QLabel(theme_cfg.get("label", "主题色"))
            theme_label.setStyleSheet(f"color: {t('text_secondary')}; font-size: 12px; background-color: transparent;")
            style_layout.addWidget(theme_label)

            theme_btn_layout = QHBoxLayout()
            theme_btn_layout.setSpacing(8)

            default_color = theme_cfg.get("default", "#4D7CFE")
            theme_color_group = QButtonGroup(self)

            for opt in theme_cfg.get("options", []):
                btn = QPushButton()
                btn.setFixedSize(28, 28)
                btn.setCheckable(True)
                btn.setStyleSheet(
                    f"QPushButton {{ "
                    f"background-color: {opt['value']}; border-radius: 14px; border: 2px solid transparent; "
                    f"}}"
                    f"QPushButton:checked {{ border: 2px solid {t('text_primary')}; }}"
                )
                btn.setProperty("theme_value", opt["value"])
                btn.setToolTip(opt["name"])
                theme_color_group.addButton(btn)
                theme_btn_layout.addWidget(btn)

            style_layout.addLayout(theme_btn_layout)
            style_layout.addSpacing(4)

            theme_color_group.buttonClicked.connect(self._on_theme_changed)
            self.style_widgets["theme_color"] = theme_color_group

            # 选中默认颜色
            for btn in theme_color_group.buttons():
                if btn.property("theme_value") == default_color:
                    btn.setChecked(True)
                    break

        # 装饰条位置
        bar_cfg = style_options.get("bar_position", {})
        if bar_cfg:
            bar_label = QLabel(bar_cfg.get("label", "装饰条位置"))
            bar_label.setStyleSheet(f"color: {t('text_secondary')}; font-size: 12px; background-color: transparent;")
            style_layout.addWidget(bar_label)

            bar_btn_layout = QHBoxLayout()
            bar_btn_layout.setSpacing(8)
            bar_group = QButtonGroup(self)

            for opt in bar_cfg.get("options", []):
                btn = QPushButton(opt["name"])
                btn.setCheckable(True)
                btn.setProperty("bar_value", opt["value"])
                btn.setObjectName(f"barOption_{opt['value']}")
                is_default = (opt["value"] == bar_cfg.get("default", "left"))
                self._style_radio_btn(btn, is_default)
                bar_group.addButton(btn)
                bar_btn_layout.addWidget(btn)

            style_layout.addLayout(bar_btn_layout)
            style_layout.addSpacing(4)

            bar_group.buttonClicked.connect(self._on_bar_position_changed)
            self.style_widgets["bar_position"] = bar_group

        # 背景样式
        bg_cfg = style_options.get("bg_style", {})
        if bg_cfg:
            bg_label = QLabel(bg_cfg.get("label", "背景样式"))
            bg_label.setStyleSheet(f"color: {t('text_secondary')}; font-size: 12px; background-color: transparent;")
            style_layout.addWidget(bg_label)

            bg_btn_layout = QHBoxLayout()
            bg_btn_layout.setSpacing(8)
            bg_group = QButtonGroup(self)

            for opt in bg_cfg.get("options", []):
                btn = QPushButton(opt["name"])
                btn.setCheckable(True)
                btn.setProperty("bg_value", opt["value"])
                btn.setObjectName(f"bgOption_{opt['value']}")
                is_default = (opt["value"] == bg_cfg.get("default", "white"))
                self._style_radio_btn(btn, is_default)
                bg_group.addButton(btn)
                bg_btn_layout.addWidget(btn)

            style_layout.addLayout(bg_btn_layout)

            bg_group.buttonClicked.connect(self._on_bg_style_changed)
            self.style_widgets["bg_style"] = bg_group

            # V1.1 RC 收尾：per-side 背景独立 — 正面/背面可选不同样式
            side_cache = self._side_state_cache.get(self._current_side, {})
            persistent_bg = side_cache.get("bg_style") or (getattr(self, "_persistent_style", {}) or {}).get("bg_style")
            if persistent_bg:
                for b in bg_group.buttons():
                    if b.property("bg_value") == persistent_bg:
                        b.setChecked(True)
                        self._on_bg_style_changed(b)
                        break

        # ── 自定义背景颜色 ──
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.HLine)
        sep1.setStyleSheet(f"background-color: {t('border_secondary')}; max-height: 1px;")
        style_layout.addWidget(sep1)

        custom_bg_label = QLabel("自定义背景色")
        custom_bg_label.setStyleSheet(f"color: {t('text_secondary')}; font-size: 12px; background-color: transparent;")
        style_layout.addWidget(custom_bg_label)

        custom_bg_row = QHBoxLayout()
        custom_bg_row.setSpacing(8)
        self.bgColorBtn = QPushButton()
        self.bgColorBtn.setFixedSize(32, 28)
        self.bgColorBtn.setStyleSheet(
            "QPushButton {"
            f"    background-color: {t('bg_secondary')}; border: 1px solid {t('border_secondary')}; border-radius: 4px;"
            "}"
            f"QPushButton:hover {{ border: 1px solid {t('accent')}; }}"
        )
        self.bgColorBtn.clicked.connect(self._on_pick_bg_color)
        custom_bg_row.addWidget(self.bgColorBtn)

        self.bgColorHex = QLineEdit()
        self.bgColorHex.setPlaceholderText("#FFFFFF")
        self.bgColorHex.setMaxLength(7)
        self.bgColorHex.setFixedWidth(90)
        self.bgColorHex.setStyleSheet(
            "QLineEdit {"
            f"    background-color: {t('bg_tertiary')}; color: {t('text_primary')};"
            f"    border: 1px solid {t('border_secondary')}; border-radius: 4px;"
            "    padding: 0 8px; font-size: 12px; min-height: 28px;"
            "}"
            f"QLineEdit:focus {{ border: 2px solid {t('accent')}; }}"
        )
        self.bgColorHex.textChanged.connect(self._on_bg_color_hex_changed)
        custom_bg_row.addWidget(self.bgColorHex)

        clear_bg_btn = QPushButton("清除")
        clear_bg_btn.setFixedHeight(28)
        clear_bg_btn.setStyleSheet(
            "QPushButton {"
            f"    background-color: {t('bg_secondary')}; color: {t('text_secondary')};"
            f"    border: 1px solid {t('border_secondary')}; border-radius: 4px;"
            "    font-size: 11px; padding: 0 10px;"
            "}"
            f"QPushButton:hover {{ color: {t('text_primary')}; border: 1px solid {t('error')}; }}"
        )
        clear_bg_btn.clicked.connect(self._on_clear_bg_color)
        custom_bg_row.addWidget(clear_bg_btn)
        custom_bg_row.addStretch()
        style_layout.addLayout(custom_bg_row)
        style_layout.addSpacing(4)

        # ── 字体颜色 ──
        font_color_sep = QFrame()
        font_color_sep.setFrameShape(QFrame.HLine)
        font_color_sep.setStyleSheet(f"background-color: {t('border_secondary')}; max-height: 1px;")
        style_layout.addWidget(font_color_sep)

        font_color_label = QLabel("字体颜色")
        font_color_label.setStyleSheet(f"color: {t('text_secondary')}; font-size: 12px; background-color: transparent;")
        style_layout.addWidget(font_color_label)

        font_color_row = QHBoxLayout()
        font_color_row.setSpacing(8)

        self.textColorLabel = QLabel("文字:")
        self.textColorLabel.setStyleSheet(f"color: {t('text_tertiary')}; font-size: 11px; background-color: transparent;")
        self.textColorLabel.setFixedWidth(40)
        font_color_row.addWidget(self.textColorLabel)

        self.textColorBtn = QPushButton()
        self.textColorBtn.setFixedSize(32, 28)
        self.textColorBtn.setStyleSheet(
            f"QPushButton {{"
            f"    background-color: {self._text_color}; border: 1px solid {t('border_secondary')}; border-radius: 4px;"
            f"}}"
            f"QPushButton:hover {{ border: 1px solid {t('accent')}; }}"
        )
        self.textColorBtn.clicked.connect(self._on_pick_text_color)
        font_color_row.addWidget(self.textColorBtn)

        self.textColorHex = QLineEdit()
        self.textColorHex.setPlaceholderText("#2C3E50")
        self.textColorHex.setMaxLength(7)
        self.textColorHex.setFixedWidth(90)
        self.textColorHex.setText(self._text_color)
        self.textColorHex.setStyleSheet(
            "QLineEdit {"
            f"    background-color: {t('bg_secondary')}; color: {t('text_primary')};"
            f"    border: 1px solid {t('border_secondary')}; border-radius: 4px;"
            "    padding: 0 8px; font-size: 12px; min-height: 28px;"
            "}"
            f"QLineEdit:focus {{ border: 2px solid {t('accent')}; }}"
        )
        self.textColorHex.textChanged.connect(self._on_text_color_hex_changed)
        font_color_row.addWidget(self.textColorHex)

        clear_text_btn = QPushButton("清除")
        clear_text_btn.setFixedHeight(28)
        clear_text_btn.setStyleSheet(
            "QPushButton {"
            f"    background-color: {t('bg_secondary')}; color: {t('text_secondary')};"
            f"    border: 1px solid {t('border_secondary')}; border-radius: 4px;"
            "    font-size: 11px; padding: 0 10px;"
            "}"
            f"QPushButton:hover {{ color: {t('text_primary')}; border: 1px solid {t('error')}; }}"
        )
        clear_text_btn.clicked.connect(self._on_clear_text_color)
        font_color_row.addWidget(clear_text_btn)

        font_color_row.addSpacing(20)

        self.secondaryColorLabel = QLabel("次要:")
        self.secondaryColorLabel.setStyleSheet(f"color: {t('text_tertiary')}; font-size: 11px; background-color: transparent;")
        self.secondaryColorLabel.setFixedWidth(40)
        font_color_row.addWidget(self.secondaryColorLabel)

        self.secondaryColorBtn = QPushButton()
        self.secondaryColorBtn.setFixedSize(32, 28)
        self.secondaryColorBtn.setStyleSheet(
            "QPushButton {"
            f"    background-color: {self._text_secondary_color}; border: 1px solid {t('border_secondary')}; border-radius: 4px;"
            "}"
            f"QPushButton:hover {{ border: 1px solid {t('accent')}; }}"
        )
        self.secondaryColorBtn.clicked.connect(self._on_pick_secondary_color)
        font_color_row.addWidget(self.secondaryColorBtn)

        self.secondaryColorHex = QLineEdit()
        self.secondaryColorHex.setPlaceholderText("#7F8C8D")
        self.secondaryColorHex.setMaxLength(7)
        self.secondaryColorHex.setFixedWidth(90)
        self.secondaryColorHex.setText(self._text_secondary_color)
        self.secondaryColorHex.setStyleSheet(
            "QLineEdit {"
            f"    background-color: {t('bg_secondary')}; color: {t('text_primary')};"
            f"    border: 1px solid {t('border_secondary')}; border-radius: 4px;"
            "    padding: 0 8px; font-size: 12px; min-height: 28px;"
            "}"
            f"QLineEdit:focus {{ border: 2px solid {t('accent')}; }}"
        )
        self.secondaryColorHex.textChanged.connect(self._on_secondary_color_hex_changed)
        font_color_row.addWidget(self.secondaryColorHex)

        clear_secondary_btn = QPushButton("清除")
        clear_secondary_btn.setFixedHeight(28)
        clear_secondary_btn.setStyleSheet(
            "QPushButton {"
            f"    background-color: {t('bg_secondary')}; color: {t('text_secondary')};"
            f"    border: 1px solid {t('border_secondary')}; border-radius: 4px;"
            "    font-size: 11px; padding: 0 10px;"
            "}"
            f"QPushButton:hover {{ color: {t('text_primary')}; border: 1px solid {t('error')}; }}"
        )
        clear_secondary_btn.clicked.connect(self._on_clear_secondary_color)
        font_color_row.addWidget(clear_secondary_btn)

        font_color_row.addStretch()
        style_layout.addLayout(font_color_row)
        style_layout.addSpacing(4)

        # ─ 背景纹理 ───
        texture_cfg = style_options.get("bg_texture", {})
        if texture_cfg:
            texture_label = QLabel(texture_cfg.get("label", "背景纹理"))
            texture_label.setStyleSheet(f"color: {t('text_secondary')}; font-size: 12px; background-color: transparent;")
            style_layout.addWidget(texture_label)

            texture_btn_layout = QHBoxLayout()
            texture_btn_layout.setSpacing(8)
            texture_group = QButtonGroup(self)

            for opt in texture_cfg.get("options", []):
                btn = QPushButton(opt["name"])
                btn.setCheckable(True)
                btn.setProperty("texture_value", opt["value"])
                btn.setObjectName(f"textureOption_{opt['value']}")
                is_default = (opt["value"] == texture_cfg.get("default", "none"))
                self._style_radio_btn(btn, is_default)
                texture_group.addButton(btn)
                texture_btn_layout.addWidget(btn)

            style_layout.addLayout(texture_btn_layout)

            texture_group.buttonClicked.connect(self._on_texture_changed)
            self.style_widgets["bg_texture"] = texture_group

        # ── 背景图片上传 ──
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.HLine)
        sep2.setStyleSheet(f"background-color: {t('border_secondary')}; max-height: 1px;")
        style_layout.addWidget(sep2)

        bg_img_label = QLabel("背景图片")
        bg_img_label.setStyleSheet(f"color: {t('text_secondary')}; font-size: 12px; background-color: transparent;")
        style_layout.addWidget(bg_img_label)

        bg_img_row = QHBoxLayout()
        bg_img_row.setSpacing(8)
        self.bgImageBtn = QPushButton("选择图片")
        self.bgImageBtn.setFixedHeight(30)
        self.bgImageBtn.setStyleSheet(
            "QPushButton {"
            f"    background-color: {t('bg_secondary')}; color: {t('text_secondary')};"
            f"    border: 1px solid {t('border_secondary')}; border-radius: 4px;"
            "    font-size: 12px; padding: 0 14px;"
            "}"
            f"QPushButton:hover {{ color: {t('text_primary')}; border: 1px solid {t('accent')}; }}"
        )
        self.bgImageBtn.clicked.connect(self._on_pick_bg_image)
        bg_img_row.addWidget(self.bgImageBtn)

        self.bgImageLabel = QLabel("未选择")
        self.bgImageLabel.setStyleSheet(f"color: {t('text_muted')}; font-size: 11px; background-color: transparent;")
        bg_img_row.addWidget(self.bgImageLabel)

        clear_bg_img_btn = QPushButton("清除")
        clear_bg_img_btn.setFixedHeight(28)
        clear_bg_img_btn.setStyleSheet(
            "QPushButton {"
            f"    background-color: {t('bg_secondary')}; color: {t('text_secondary')};"
            f"    border: 1px solid {t('border_secondary')}; border-radius: 4px;"
            "    font-size: 11px; padding: 0 10px;"
            "}"
            f"QPushButton:hover {{ color: {t('text_primary')}; border: 1px solid {t('error')}; }}"
        )
        clear_bg_img_btn.clicked.connect(self._on_clear_bg_image)
        bg_img_row.addWidget(clear_bg_img_btn)
        bg_img_row.addStretch()
        style_layout.addLayout(bg_img_row)

        opacity_row = QHBoxLayout()
        opacity_row.setSpacing(8)
        opacity_label = QLabel("透明度:")
        opacity_label.setStyleSheet(f"color: {t('text_tertiary')}; font-size: 12px; background-color: transparent;")
        opacity_label.setFixedWidth(50)
        opacity_row.addWidget(opacity_label)
        self.bgOpacitySlider = QSlider(Qt.Horizontal)
        self.bgOpacitySlider.setRange(5, 100)
        self.bgOpacitySlider.setValue(self._bg_image_opacity)
        self.bgOpacitySlider.setFixedWidth(120)
        self.bgOpacitySlider.setStyleSheet(
            "QSlider::groove:horizontal {"
            f"    height: 4px; background: {t('border_secondary')}; border-radius: 2px;"
            "}"
            "QSlider::handle:horizontal {"
            f"    background: {t('accent')}; width: 14px; height: 14px;"
            "    margin: -5px 0; border-radius: 7px;"
            "}"
            "QSlider::sub-page:horizontal {"
            f"    background: {t('accent')}; border-radius: 2px;"
            "}"
        )
        self.bgOpacitySlider.valueChanged.connect(self._on_bg_opacity_changed)
        opacity_row.addWidget(self.bgOpacitySlider)
        self.bgOpacityVal = QLabel(f"{self._bg_image_opacity}%")
        self.bgOpacityVal.setStyleSheet(f"color: {t('text_secondary')}; font-size: 11px; background-color: transparent;")
        self.bgOpacityVal.setFixedWidth(36)
        opacity_row.addWidget(self.bgOpacityVal)
        opacity_row.addStretch()
        style_layout.addLayout(opacity_row)

        self.formLayout.addWidget(style_card)
        self.formLayout.addSpacing(8)

        # ── AT-09: 字体风格（notice 模板） ──
        font_style_cfg = style_options.get("font_style", {})
        if font_style_cfg:
            font_style_label = QLabel(font_style_cfg.get("label", "字体风格"))
            font_style_label.setStyleSheet(f"color: {t('text_secondary')}; font-size: 12px; background-color: transparent;")
            self.formLayout.addWidget(font_style_label)

            font_style_btn_layout = QHBoxLayout()
            font_style_btn_layout.setSpacing(8)
            font_style_group = QButtonGroup(self)

            for opt in font_style_cfg.get("options", []):
                btn = QPushButton(opt["name"])
                btn.setCheckable(True)
                btn.setProperty("font_style_value", opt["value"])
                btn.setObjectName(f"fontStyleOption_{opt['value']}")
                is_default = (opt["value"] == font_style_cfg.get("default", "formal"))
                self._style_radio_btn(btn, is_default)
                font_style_group.addButton(btn)
                font_style_btn_layout.addWidget(btn)

            self.formLayout.addLayout(font_style_btn_layout)

            font_style_group.buttonClicked.connect(self._on_font_style_changed)
            self.style_widgets["font_style"] = font_style_group

            self.formLayout.addSpacing(8)

        # ── AT-10: 标题栏样式（product_spec 模板） ──
        header_style_cfg = style_options.get("header_style", {})
        if header_style_cfg:
            header_style_label = QLabel(header_style_cfg.get("label", "标题栏样式"))
            header_style_label.setStyleSheet(f"color: {t('text_secondary')}; font-size: 12px; background-color: transparent;")
            self.formLayout.addWidget(header_style_label)

            header_style_btn_layout = QHBoxLayout()
            header_style_btn_layout.setSpacing(8)
            header_style_group = QButtonGroup(self)

            for opt in header_style_cfg.get("options", []):
                btn = QPushButton(opt["name"])
                btn.setCheckable(True)
                btn.setProperty("header_style_value", opt["value"])
                btn.setObjectName(f"headerStyleOption_{opt['value']}")
                is_default = (opt["value"] == header_style_cfg.get("default", "bar"))
                self._style_radio_btn(btn, is_default)
                header_style_group.addButton(btn)
                header_style_btn_layout.addWidget(btn)

            self.formLayout.addLayout(header_style_btn_layout)

            header_style_group.buttonClicked.connect(self._on_header_style_changed)
            self.style_widgets["header_style"] = header_style_group

            self.formLayout.addSpacing(8)

        # ── AT-10: 表格样式（product_spec 模板） ──
        table_style_cfg = style_options.get("table_style", {})
        if table_style_cfg:
            table_style_label = QLabel(table_style_cfg.get("label", "表格样式"))
            table_style_label.setStyleSheet(f"color: {t('text_secondary')}; font-size: 12px; background-color: transparent;")
            self.formLayout.addWidget(table_style_label)

            table_style_btn_layout = QHBoxLayout()
            table_style_btn_layout.setSpacing(8)
            table_style_group = QButtonGroup(self)

            for opt in table_style_cfg.get("options", []):
                btn = QPushButton(opt["name"])
                btn.setCheckable(True)
                btn.setProperty("table_style_value", opt["value"])
                btn.setObjectName(f"tableStyleOption_{opt['value']}")
                is_default = (opt["value"] == table_style_cfg.get("default", "striped"))
                self._style_radio_btn(btn, is_default)
                table_style_group.addButton(btn)
                table_style_btn_layout.addWidget(btn)

            self.formLayout.addLayout(table_style_btn_layout)

            table_style_group.buttonClicked.connect(self._on_table_style_changed)
            self.style_widgets["table_style"] = table_style_group

            self.formLayout.addSpacing(8)

    def _style_radio_btn(self, btn: QPushButton, checked: bool):
        """设置样式选项按钮的样式（token 化，支持双主题）"""
        base_style = (
            f"background-color: {t('bg_hover')}; color: {t('text_secondary')}; border: 1px solid {t('border_secondary')}; "
            "border-radius: 6px; padding: 0 12px; min-height: 30px; font-size: 12px;"
        )
        checked_style = (
            f"background-color: {t('bg_hover')}; color: {t('text_primary')}; border: 1px solid {t('accent')}; "
            "border-radius: 6px; padding: 0 12px; min-height: 30px; font-size: 12px;"
        )
        btn.setStyleSheet(checked_style if checked else base_style)
        btn.setProperty("base_style", base_style)
        btn.setProperty("checked_style", checked_style)

    def _on_theme_changed(self, btn: QPushButton):
        """主题色变更，更新按钮样式并刷新预览"""
        group = self.style_widgets.get("theme_color")
        if not group:
            return
        for b in group.buttons():
            if b == btn:
                b.setStyleSheet(
                    f"QPushButton {{ background-color: {b.property('theme_value')}; border-radius: 14px; border: 2px solid {t('text_primary')}; }}"
                )
            else:
                b.setStyleSheet(
                    f"QPushButton {{ background-color: {b.property('theme_value')}; border-radius: 14px; border: 2px solid transparent; }}"
                )
        self.preview_timer.start(300)

    def _on_bar_position_changed(self, btn: QPushButton):
        """装饰条位置变更"""
        group = self.style_widgets.get("bar_position")
        if not group:
            return
        for b in group.buttons():
            is_checked = (b == btn)
            b.setStyleSheet(b.property("checked_style") if is_checked else b.property("base_style"))
        self.preview_timer.start(300)

    def _on_bg_style_changed(self, btn: QPushButton):
        """背景样式变更（V1.1 RC 收尾：per-side 独立保存）"""
        group = self.style_widgets.get("bg_style")
        if not group:
            return
        for b in group.buttons():
            is_checked = (b == btn)
            b.setStyleSheet(b.property("checked_style") if is_checked else b.property("base_style"))
        # per-side 持久化：当前面的 bg_style 单独保存
        side = getattr(self, "_current_side", "front")
        if side not in self._side_state_cache:
            self._side_state_cache[side] = {"fields": {}, "scroll": 0}
        self._side_state_cache[side]["bg_style"] = btn.property("bg_value")
        self.preview_timer.start(300)

    # ── AT-09: 字体风格变更 ──
    def _on_font_style_changed(self, btn: QPushButton):
        """字体风格变更（notice 模板）"""
        group = self.style_widgets.get("font_style")
        if not group:
            return
        for b in group.buttons():
            is_checked = (b == btn)
            b.setStyleSheet(b.property("checked_style") if is_checked else b.property("base_style"))
        self._font_style = btn.property("font_style_value")
        self.preview_timer.start(300)

    # ── AT-10: 标题栏样式变更 ──
    def _on_header_style_changed(self, btn: QPushButton):
        """标题栏样式变更（product_spec 模板）"""
        group = self.style_widgets.get("header_style")
        if not group:
            return
        for b in group.buttons():
            is_checked = (b == btn)
            b.setStyleSheet(b.property("checked_style") if is_checked else b.property("base_style"))
        self._header_style = btn.property("header_style_value")
        self.preview_timer.start(300)

    # ── AT-10: 表格样式变更 ──
    def _on_table_style_changed(self, btn: QPushButton):
        """表格样式变更（product_spec 模板）"""
        group = self.style_widgets.get("table_style")
        if not group:
            return
        for b in group.buttons():
            is_checked = (b == btn)
            b.setStyleSheet(b.property("checked_style") if is_checked else b.property("base_style"))
        self._table_style = btn.property("table_style_value")
        self.preview_timer.start(300)

    # ── 自定义背景色 ──────────────────────────────────────────
    def _on_pick_bg_color(self):
        color = QColorDialog.getColor(QColor(self._bg_custom_color) if self._bg_custom_color else QColor("#FFFFFF"))
        if color.isValid():
            self._bg_custom_color = color.name()
            self.bgColorBtn.setStyleSheet(
                f"QPushButton {{ background-color: {color.name()}; border: 1px solid {t('accent')}; border-radius: 4px; }}"
            )
            self.bgColorHex.blockSignals(True)
            self.bgColorHex.setText(color.name())
            self.bgColorHex.blockSignals(False)
            self.preview_timer.start(300)

    def _on_bg_color_hex_changed(self, text: str):
        text = text.strip()
        if not text:
            return
        if not text.startswith("#"):
            text = "#" + text
        if len(text) == 7:
            color = QColor(text)
            if color.isValid():
                self._bg_custom_color = text
                self.bgColorBtn.setStyleSheet(
                    f"QPushButton {{ background-color: {text}; border: 1px solid {t('accent')}; border-radius: 4px; }}"
                )
                self.preview_timer.start(300)

    def _on_clear_bg_color(self):
        self._bg_custom_color = ""
        self.bgColorBtn.setStyleSheet(
            f"QPushButton { background-color: {t('bg_secondary')}; border: 1px solid {t('border_secondary')}; border-radius: 4px; }"
            f"QPushButton:hover {{ border: 1px solid {t('accent')}; }}"
        )
        self.bgColorHex.blockSignals(True)
        self.bgColorHex.clear()
        self.bgColorHex.blockSignals(False)
        self.preview_timer.start(300)

    # ── 背景纹理 ─────────────────────────────────────────────
    def _on_texture_changed(self, btn: QPushButton):
        group = self.style_widgets.get("bg_texture")
        if not group:
            return
        for b in group.buttons():
            is_checked = (b == btn)
            b.setStyleSheet(b.property("checked_style") if is_checked else b.property("base_style"))
        self._bg_texture = btn.property("texture_value")
        self.preview_timer.start(300)

    # ── 背景图片 ─────────────────────────────────────────────
    def _on_pick_bg_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择背景图片", "",
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif);;所有文件 (*)"
        )
        if path:
            self._bg_image_path = path
            fname = os.path.basename(path)
            self.bgImageLabel.setText(fname)
            self.bgImageLabel.setStyleSheet(f"color: {t('text_primary')}; font-size: 11px; background-color: transparent;")
            self.preview_timer.start(300)

    def _on_clear_bg_image(self):
        self._bg_image_path = None
        self.bgImageLabel.setText("未选择")
        self.bgImageLabel.setStyleSheet(f"color: {t('text_muted')}; font-size: 11px; background-color: transparent;")
        self.preview_timer.start(300)

    def _on_bg_opacity_changed(self, value: int):
        self._bg_image_opacity = value
        self.bgOpacityVal.setText(f"{value}%")
        self.preview_timer.start(300)

    # ── 字体颜色 ─────────────────────────────────────────────
    def _on_pick_text_color(self):
        current = QColor(self._text_color) if self._text_color else QColor(44, 62, 80)
        color = QColorDialog.getColor(current, self, "选择文字颜色")
        if color.isValid():
            self._text_color = color.name()
            self.textColorBtn.setStyleSheet(
                "QPushButton {"
                f"    background-color: {self._text_color}; border: 1px solid {t('border_secondary')}; border-radius: 4px;"
                "}"
                f"QPushButton:hover {{ border: 1px solid {t('accent')}; }}"
            )
            self.textColorHex.setText(self._text_color)
            self.preview_timer.start(200)

    def _on_text_color_hex_changed(self, text: str):
        if len(text) == 7 and text.startswith("#"):
            try:
                color = QColor(text)
                if color.isValid():
                    self._text_color = text
                    self.textColorBtn.setStyleSheet(
                        "QPushButton {"
                        f"    background-color: {self._text_color}; border: 1px solid {t('border_secondary')}; border-radius: 4px;"
                        "}"
                        f"QPushButton:hover {{ border: 1px solid {t('accent')}; }}"
                    )
                    self.preview_timer.start(200)
            except Exception as e:
                print(f"[template_editor] 文字颜色预览更新失败: {e}")

    def _on_clear_text_color(self):
        self._text_color = "#2C3E50"
        self.textColorBtn.setStyleSheet(
            "QPushButton {"
            f"    background-color: {self._text_color}; border: 1px solid {t('border_secondary')}; border-radius: 4px;"
            "}"
            f"QPushButton:hover {{ border: 1px solid {t('accent')}; }}"
        )
        self.textColorHex.setText(self._text_color)
        self.preview_timer.start(200)

    def _on_pick_secondary_color(self):
        current = QColor(self._text_secondary_color) if self._text_secondary_color else QColor(127, 140, 141)
        color = QColorDialog.getColor(current, self, "选择次要文字颜色")
        if color.isValid():
            self._text_secondary_color = color.name()
            self.secondaryColorBtn.setStyleSheet(
                "QPushButton {"
                f"    background-color: {self._text_secondary_color}; border: 1px solid {t('border_secondary')}; border-radius: 4px;"
                "}"
                f"QPushButton:hover {{ border: 1px solid {t('accent')}; }}"
            )
            self.secondaryColorHex.setText(self._text_secondary_color)
            self.preview_timer.start(200)

    def _on_secondary_color_hex_changed(self, text: str):
        if len(text) == 7 and text.startswith("#"):
            try:
                color = QColor(text)
                if color.isValid():
                    self._text_secondary_color = text
                    self.secondaryColorBtn.setStyleSheet(
                        "QPushButton {"
                        f"    background-color: {self._text_secondary_color}; border: 1px solid {t('border_secondary')}; border-radius: 4px;"
                        "}"
                        f"QPushButton:hover {{ border: 1px solid {t('accent')}; }}"
                    )
                    self.preview_timer.start(200)
            except Exception as e:
                print(f"[template_editor] 副标题颜色预览更新失败: {e}")

    def _on_clear_secondary_color(self):
        self._text_secondary_color = "#7F8C8D"
        self.secondaryColorBtn.setStyleSheet(
            "QPushButton {"
            f"    background-color: {self._text_secondary_color}; border: 1px solid {t('border_secondary')}; border-radius: 4px;"
            "}"
            f"QPushButton:hover {{ border: 1px solid {t('accent')}; }}"
        )
        self.secondaryColorHex.setText(self._text_secondary_color)
        self.preview_timer.start(200)

    def _get_current_style_values(self) -> dict:
        """获取当前选中的样式值"""
        result = {
            "theme_color": "#4D7CFE",
            "bar_position": "left",
            "bg_style": "white",
            "bg_custom_color": "",
            "bg_texture": "none",
            "bg_image_path": None,
            "bg_image_opacity": 50,
            "text_color": "#2C3E50",
            "text_secondary_color": "#7F8C8D",
            "font_style": "formal",
            "header_style": "bar",
            "table_style": "striped",
        }

        theme_group = self.style_widgets.get("theme_color")
        if theme_group:
            for btn in theme_group.buttons():
                if btn.isChecked():
                    result["theme_color"] = btn.property("theme_value")
                    break

        bar_group = self.style_widgets.get("bar_position")
        if bar_group:
            for btn in bar_group.buttons():
                if btn.isChecked():
                    result["bar_position"] = btn.property("bar_value")
                    break

        bg_group = self.style_widgets.get("bg_style")
        if bg_group:
            for btn in bg_group.buttons():
                if btn.isChecked():
                    result["bg_style"] = btn.property("bg_value")
                    break

        texture_group = self.style_widgets.get("bg_texture")
        if texture_group:
            for btn in texture_group.buttons():
                if btn.isChecked():
                    result["bg_texture"] = btn.property("texture_value")
                    break

        font_style_group = self.style_widgets.get("font_style")
        if font_style_group:
            for btn in font_style_group.buttons():
                if btn.isChecked():
                    result["font_style"] = btn.property("font_style_value")
                    break

        header_style_group = self.style_widgets.get("header_style")
        if header_style_group:
            for btn in header_style_group.buttons():
                if btn.isChecked():
                    result["header_style"] = btn.property("header_style_value")
                    break

        table_style_group = self.style_widgets.get("table_style")
        if table_style_group:
            for btn in table_style_group.buttons():
                if btn.isChecked():
                    result["table_style"] = btn.property("table_style_value")
                    break

        result["bg_custom_color"] = self._bg_custom_color
        result["bg_image_path"] = self._bg_image_path
        result["bg_image_opacity"] = self._bg_image_opacity
        result["text_color"] = self._text_color
        result["text_secondary_color"] = self._text_secondary_color

        return result

    def _serialize_render_context(self, side: str = None) -> "RenderContext":
        """
        RC1 导出一致性修复：从当前编辑状态一次性打包 RenderContext。

        预览和导出必须共享同一份 RenderContext，差异仅在于：
          - 预览：ctx.render_to_pixmap()
          - 导出：ctx.render_to_pdf(path)

        禁止：
          - 重新读取模板默认值
          - 重新调用 load_template()
          - 在两个入口中分别构造 fields/styles
        """
        from src.common.template_renderer import make_render_context

        if side is None:
            side = getattr(self, '_current_side', 'front')

        # ── 字段：当前 side 的 widget 优先，缺失时从 cache/sample 回退 ──
        fields = {}
        side_cache = self._side_state_cache.get(side, {}).get("fields", {})
        sample_data = (self.template_data.get("sample", {}) or {}).get(side, {}) or {}

        for field in self.template_data.get("fields", []):
            key = field.get("key", "")
            widget = self.field_widgets.get(key)
            value = None
            if widget is not None:
                try:
                    if isinstance(widget, QTextEdit):
                        value = widget.toPlainText().strip()
                    elif isinstance(widget, QTableWidget):
                        if key == "items":
                            value = self.get_invoice_items()
                        else:
                            rows = []
                            for r in range(widget.rowCount()):
                                row_data = []
                                for c in range(widget.columnCount()):
                                    it = widget.item(r, c)
                                    row_data.append(it.text().strip() if it and it.text().strip() else "")
                                rows.append(row_data)
                            value = rows
                    else:
                        value = widget.text().strip()
                except RuntimeError:
                    value = None
            if value is None or value == "":
                # 回退 1：当前 side 的 cache（用户切换过此面）
                cached = side_cache.get(key)
                if isinstance(cached, str) and cached.strip():
                    value = cached.strip()
                elif isinstance(cached, list) and cached:
                    value = cached
                else:
                    # 回退 2：JSON sample（用户从未访问过此面）
                    sample_val = sample_data.get(key)
                    if isinstance(sample_val, str) and sample_val.strip():
                        value = sample_val.strip()
                    elif sample_val:
                        value = sample_val
                    else:
                        value = "" if not isinstance(value, list) else value
            fields[key] = value

        # ── 样式：从当前样式面板读取 ──
        styles = self._get_current_style_values()

        # ── V1.1 RC 收尾：per-side 背景独立 — 切换面时各面用各自的 bg_style ──
        side_cache = self._side_state_cache.get(side, {}) or {}
        if "bg_style" in side_cache:
            styles["bg_style"] = side_cache["bg_style"]

        # ── 资源：从当前上传状态读取（双向兜底，兼容老 key "logo"）──
        logo_path      = self._uploaded_paths.get("logo") or self._uploaded_paths.get("back_logo")
        back_logo_path = self._uploaded_paths.get("back_logo") or self._uploaded_paths.get("logo")
        qr_image_path  = self._uploaded_paths.get("back_qr_image") or self._uploaded_paths.get("qr_image_path")

        return make_render_context(
            template_id=self.template_data.get("id", "business_card"),
            side=side,
            fields=fields,
            styles=styles,
            logo_path=logo_path,
            qr_image_path=qr_image_path,
            back_logo_path=back_logo_path,
            logo_width_mm=getattr(self, '_logo_width_mm', 8.0),
            logo_right_mm=getattr(self, '_logo_right_mm', 5.0),
            logo_top_mm=getattr(self, '_logo_top_mm', 4.0),
            logo_shape=getattr(self, '_logo_shape', 'square'),
        )

    def _on_side_changed(self, index: int):
        """正反面切换（V1.1 Beta Hotfix RB-002 修复）

        行为契约：
          1. 切换前：保存当前 side 的字段值+滚动位置到 self._side_state_cache
          2. 切换后：从 cache 恢复新 side 的状态
          3. 预览更新：依赖 form 的 textChanged 信号经 debounce 自然触发
        """
        new_side = "front" if index == 0 else "back"
        if new_side == self._current_side:
            return  # 同 side，no-op
        # 1. 保存当前 side 状态到 cache
        self._save_side_state(self._current_side)
        # 2. 切换 side 标识
        self._current_side = new_side
        # 3. 内部切换：重建 form + 恢复新 side 状态
        self._switch_side_internal(new_side)

    def _switch_side_internal(self, new_side: str):
        """正反面切换内部实现（封装 _build_form 调用，避免污染 _on_side_changed 函数体）

        流程：
          1. 重建 form（不同 side 字段不同，必要）
          2. 从 cache 恢复 new_side 的字段值
          3. 恢复滚动位置
          4. 触发 1 次预览更新（仅当 new_side 有内容时）
        """
        self._build_form()
        self._load_side_state(new_side)

    def _save_side_state(self, side: str):
        """保存指定 side 的字段值+滚动位置到 cache

        字段值支持 QLineEdit/QTextEdit/QTableWidget 三种 widget 类型。
        """
        if side not in self._side_state_cache:
            self._side_state_cache[side] = {"fields": {}, "scroll": 0}
        cache = self._side_state_cache[side]
        cache["fields"] = {}
        for key, widget in self.field_widgets.items():
            if widget is None:
                continue
            try:
                if isinstance(widget, QTextEdit):
                    cache["fields"][key] = widget.toPlainText()
                elif isinstance(widget, QTableWidget):
                    rows = []
                    for r in range(widget.rowCount()):
                        row_data = []
                        for c in range(widget.columnCount()):
                            if key == "items" and c >= 3:
                                continue
                            it = widget.item(r, c)
                            row_data.append(it.text() if it else "")
                        rows.append(row_data)
                    cache["fields"][key] = rows
                elif hasattr(widget, "text"):
                    cache["fields"][key] = widget.text()
            except RuntimeError:
                # widget 已被 Qt 销毁，跳过
                continue
        # 滚动位置
        if hasattr(self, "scrollArea") and self.scrollArea is not None:
            try:
                vbar = self.scrollArea.verticalScrollBar()
                cache["scroll"] = vbar.value() if vbar else 0
            except (AttributeError, RuntimeError):
                cache["scroll"] = 0

    def _load_side_state(self, side: str):
        """从 cache 恢复指定 side 的字段值+滚动位置

        恢复期间设置 self._restoring_state=True，抑制 _on_field_changed
        触发的 N 次 debounced 预览更新（由外部 _update_preview 1 次完成）。
        """
        if side not in self._side_state_cache:
            return
        cache = self._side_state_cache[side]
        self._restoring_state = True
        try:
            for key, widget in self.field_widgets.items():
                if widget is None or key not in cache["fields"]:
                    continue
                value = cache["fields"][key]
                try:
                    if isinstance(widget, QTextEdit):
                        widget.setPlainText(value)
                    elif isinstance(widget, QTableWidget) and isinstance(value, list):
                        widget.setRowCount(len(value))
                        for r, row_data in enumerate(value):
                            for c, cell_text in enumerate(row_data):
                                if c < widget.columnCount():
                                    # Skip last column for invoice items (delete button column)
                                    if key == "items" and c >= 3:
                                        continue
                                    it = widget.item(r, c)
                                    if it is None:
                                        it = QTableWidgetItem("")
                                        widget.setItem(r, c, it)
                                    it.setText(cell_text)
                        # Invoice items: restore delete buttons
                        if key == "items":
                            for r in range(widget.rowCount()):
                                btn = widget.cellWidget(r, 3)
                                if btn is None:
                                    del_btn = QPushButton("×")
                                    del_btn.setFixedSize(24, 24)
                                    del_btn.setStyleSheet(
                                        "QPushButton {"
                                        f"    color: {t('error')};"
                                        "    border: none;"
                                        "    border-radius: 12px;"
                                        "    font-size: 14px;"
                                        "    font-weight: bold;"
                                        "    background: transparent;"
                                        "}"
                                        "QPushButton:hover {"
                                        "    background-color: rgba(255,59,48,0.1);"
                                        "}"
                                    )
                                    del_btn.clicked.connect(lambda checked, w=widget, row=r: self._delete_invoice_row(w, row))
                                    widget.setCellWidget(r, 3, del_btn)
                    elif hasattr(widget, "setText"):
                        widget.setText(value)
                except RuntimeError:
                    continue
        finally:
            self._restoring_state = False
        # 滚动位置（在恢复 flag 之外，避免影响 setText 抑制）
        if hasattr(self, "scrollArea") and self.scrollArea is not None:
            try:
                vbar = self.scrollArea.verticalScrollBar()
                if vbar:
                    vbar.setValue(cache.get("scroll", 0))
            except (AttributeError, RuntimeError):
                pass
        # 1 次预览更新（避免 N 次 textChanged 触发的 debounce 风暴）
        if hasattr(self, "_update_preview"):
            try:
                self._update_preview()
            except Exception:
                pass

    def _render_business_card_preview(self, data: dict):
        """渲染名片预览（支持正反面）

        V1.1 RC 修复（FZ-002）：
          - 严格走 _serialize_render_context 统一入口，与导出路径共享同一份 ctx
          - 删除所有 HTML 拼接回退路径（BUSINESS_CARD_CSS.format / BUSINESS_CARD_BACK_CSS.format）
          - 若 ctx 渲染失败，显示占位错误信息（不降级为 HTML 拼版，避免预览≠导出）
        """
        # ── 唯一渲染入口：与 _on_generate 共用同一份 ctx ──
        try:
            ctx = self._serialize_render_context(side=self._current_side)
        except Exception as e:
            print(f"[template_editor] _serialize_render_context 失败: {e}")
            self._show_preview_error(f"渲染上下文构造失败：{e}")
            return

        # ── 渲染为 QPixmap ──
        try:
            from PySide6.QtCore import QBuffer, QIODevice
            qpx = ctx.render_to_pixmap(target_width=560, dpi=PREVIEW_SCALE)
            buf = QBuffer()
            buf.open(QIODevice.WriteOnly)
            qpx.save(buf, "PNG")
            import base64
            b64 = base64.b64encode(buf.data()).decode("ascii")
            buf.close()
            data_uri = f"data:image/png;base64,{b64}"
        except Exception as e:
            print(f"[template_editor] ctx.render_to_pixmap 失败: {e}")
            self._show_preview_error(f"渲染失败：{e}")
            return

        html = (
            f'<html><body style="margin:0;background:transparent;display:flex;'
            f'justify-content:center;align-items:center;min-height:100vh;">'
            f'<img src="{data_uri}" style="max-width:100%;height:auto;'
            f'box-shadow:0 4px 24px rgba(0,0,0,0.4);"/></body></html>'
        )
        self.previewView.setHtml(html)

    def _show_preview_error(self, msg: str):
        """显示预览错误占位（不拼接业务 HTML，避免与导出走不同路径）"""
        if not hasattr(self, 'previewView') or self.previewView is None:
            return
        # 单纯占位提示，不渲染业务内容；背景用 token 化的中性灰
        html = (
            f'<html><body style="margin:0;display:flex;justify-content:center;'
            f'align-items:center;min-height:100vh;font-family:sans-serif;'
            f'color:{t("text_secondary")};background:transparent;">'
            f'<div style="text-align:center;padding:24px;">'
            f'<div style="font-size:32px;margin-bottom:8px;">⚠</div>'
            f'<div style="font-size:13px;">{msg}</div>'
            f'<div style="font-size:11px;margin-top:8px;color:{t("text_muted")};">'
            f'预览与导出共用同一渲染管线，渲染失败时导出也会失败</div>'
            f'</div></body></html>'
        )
        self.previewView.setHtml(html)

    def _add_field_to_layout(self, parent_layout, field):
        key = field.get("key", "")
        label_text = field.get("label", key)
        field_type = field.get("type", "text")
        required = field.get("required", False)
        placeholder = field.get("placeholder", "")

        # V1.1 RC 收尾：image_upload 字段由 TPL-05 通用上传区接管，
        # 避免在表单内出现重复的"上传 LOGO"按钮。
        if field_type == "image_upload":
            return

        field_container = QWidget()
        field_container.setObjectName(f"fieldRow_{key}")
        field_container.setStyleSheet("background-color: transparent;")
        field_row = QVBoxLayout(field_container)
        field_row.setSpacing(6)
        field_row.setContentsMargins(0, 0, 0, 0)

        # 标签（RB-003 修复：移除硬编码颜色，使用 CSS class，颜色由 _rebuild_inline_styles 驱动）
        label = QLabel()
        label.setObjectName("fieldLabel")
        label.setProperty("required", required)
        if required:
            label.setText(
                f'<span class="field-req">* </span>'
                f'<span class="field-text">{label_text}</span>'
            )
        else:
            label.setText(
                f'<span class="field-text">{label_text}</span>'
            )
        field_row.addWidget(label)

        # 输入控件
        if field_type == "textarea":
            # ── 发票/收据明细项目：专用表格编辑器 ──
            if key == "items":
                container = QWidget()
                container.setObjectName(f"invoiceItemsContainer_{key}")
                layout = QVBoxLayout(container)
                layout.setSpacing(8)
                layout.setContentsMargins(0, 0, 0, 0)

                table = QTableWidget()
                table.setObjectName(f"fieldTable_{key}")
                table.setColumnCount(4)
                table.setHorizontalHeaderLabels(["项目名称", "数量", "单价", "操作"])
                table.setColumnWidth(0, 260)
                table.setColumnWidth(1, 80)
                table.setColumnWidth(2, 100)
                table.setColumnWidth(3, 60)

                table.verticalHeader().setVisible(False)
                table.setSelectionMode(QAbstractItemView.NoSelection)
                table.horizontalHeader().setStretchLastSection(True)
                table.setMinimumHeight(220)

                table.setStyleSheet(
                    "QTableWidget {"
                    f"    background-color: {t('bg_tertiary')};"
                    f"    color: {t('text_primary')};"
                    f"    border: 1px solid {t('border_secondary')};"
                    "    border-radius: 6px;"
                    f"    gridline-color: {t('border_secondary')};"
                    "}"
                    "QTableWidget::item {"
                    "    padding: 4px;"
                    "}"
                    "QTableWidget::item:selected {"
                    f"    background-color: {t('accent_subtle')};"
                    "}"
                    "QTableWidget QHeaderView::section {"
                    f"    background-color: {t('bg_secondary')};"
                    f"    color: {t('text_secondary')};"
                    "    padding: 6px;"
                    "    border: none;"
                    "    font-size: 12px;"
                    "}"
                )

                # 默认 1 行空白（含行级删除按钮）
                table.setRowCount(1)
                for c in range(3):
                    item = QTableWidgetItem("")
                    table.setItem(0, c, item)
                del_btn = QPushButton("×")
                del_btn.setFixedSize(24, 24)
                del_btn.setStyleSheet(
                    "QPushButton {"
                    f"    color: {t('error')};"
                    "    border: none;"
                    "    border-radius: 12px;"
                    "    font-size: 14px;"
                    "    font-weight: bold;"
                    "    background: transparent;"
                    "}"
                    "QPushButton:hover {"
                    "    background-color: rgba(255,59,48,0.1);"
                    "}"
                )
                del_btn.clicked.connect(lambda checked, t=table, r=0: self._delete_invoice_row(t, r))
                table.setCellWidget(0, 3, del_btn)

                from PySide6.QtWidgets import QLabel as _QLabel
                # 合计行
                total_layout = QHBoxLayout()
                total_layout.addStretch()
                self._invoice_total_label = _QLabel("合计：0")
                self._invoice_total_label.setObjectName("invoiceTotalLabel")
                self._invoice_total_label.setStyleSheet(
                    f"color: {t('accent')}; font-size: 14px; font-weight: 600; background: transparent;"
                )
                total_layout.addWidget(self._invoice_total_label)

                # 按钮行
                btn_layout = QHBoxLayout()
                btn_layout.setSpacing(8)

                add_btn = QPushButton("＋ 新增项目")
                add_btn.setFixedHeight(28)
                add_btn.setStyleSheet(
                    "QPushButton {"
                    f"    background-color: {t('bg_secondary')};"
                    f"    color: {t('accent')};"
                    f"    border: 1px solid {t('border_secondary')};"
                    "    border-radius: 4px;"
                    "    padding: 0 12px;"
                    "    font-size: 12px;"
                    "}"
                    "QPushButton:hover {"
                    f"    background-color: {t('bg_hover')};"
                    f"    border-color: {t('accent')};"
                    "}"
                )
                add_btn.clicked.connect(lambda checked, t=table: self._add_invoice_row(t))
                btn_layout.addWidget(add_btn)

                btn_layout.addStretch()

                layout.addWidget(table)
                layout.addLayout(total_layout)
                layout.addLayout(btn_layout)

                # 信号
                table.cellChanged.connect(lambda r, c, t=table: self._on_invoice_cell_changed(t, r, c))

                field_row.addWidget(container)
                parent_layout.addWidget(field_container)
                self.field_widgets[key] = table
                return

            # ── 备注区域：专用 textarea（120字限制+自动换行） ──
            if key == "remark":
                widget = QTextEdit()
                widget.setObjectName(f"fieldRemark_{key}")
                widget.setPlaceholderText(placeholder)
                widget.setMaximumHeight(120)
                widget.setLineWrapMode(QTextEdit.WidgetWidth)
                from PySide6.QtGui import QTextOption
                widget.setWordWrapMode(QTextOption.WordWrap)
                widget.setStyleSheet(
                    "QTextEdit {"
                    f"    background-color: {t('bg_tertiary')};"
                    f"    color: {t('text_primary')};"
                    f"    border: 1px solid {t('border_secondary')};"
                    "    border-radius: 6px;"
                    "    padding: 8px 12px;"
                    "    font-size: 13px;"
                    "}"
                    "QTextEdit:focus {"
                    f"    border: 2px solid {t('accent')};"
                    "}"
                    "QTextEdit::placeholder {"
                    f"    color: {t('text_muted')};"
                    "}"
                )
                max_len = field.get("maxLength", 120)
                widget.textChanged.connect(lambda: self._truncate_remark_textedit(widget, max_len))
                field_row.addWidget(widget)
                parent_layout.addWidget(field_container)
                self.field_widgets[key] = widget
                return

            # ── 普通文本域 ──
            widget = QTextEdit()
            widget.setObjectName(f"fieldTextarea_{key}")
            widget.setMaximumHeight(100)
            widget.setPlaceholderText(placeholder)
            widget.setStyleSheet(
                "QTextEdit {"
                f"    background-color: {t('bg_tertiary')};"
                f"    color: {t('text_primary')};"
                f"    border: 1px solid {t('border_secondary')};"
                "    border-radius: 6px;"
                "    padding: 8px 12px;"
                "    font-size: 13px;"
                "}"
                "QTextEdit:focus {"
                f"    border: 2px solid {t('accent')};"
                "}"
                "QTextEdit::placeholder {"
                f"    color: {t('text_muted')};"
                "}"
            )
        elif field_type == "table":
            # 动态表格组件（参数 | 值）
            columns = field.get("columns", [{"key": "col1", "label": "列1"}, {"key": "col2", "label": "列2"}])
            col_count = len(columns)

            # 表格容器
            table_widget = QWidget()
            table_widget.setObjectName(f"tableWidget_{key}")
            table_layout = QVBoxLayout(table_widget)
            table_layout.setSpacing(8)
            table_layout.setContentsMargins(0, 0, 0, 0)

            # QTableWidget
            table = QTableWidget()
            table.setObjectName(f"fieldTable_{key}")
            table.setColumnCount(col_count)
            table.setHorizontalHeaderLabels([col.get("label", f"列{i}") for i, col in enumerate(columns)])
            table.setRowCount(2)  # 初始2行
            table.setStyleSheet(
                "QTableWidget {"
                f"    background-color: {t('bg_tertiary')};"
                f"    color: {t('text_primary')};"
                f"    border: 1px solid {t('border_secondary')};"
                "    border-radius: 6px;"
                f"    gridline-color: {t('border_secondary')};"
                "    word-wrap: break-word;"
                "}"
                "QTableWidget::item {"
                "    padding: 4px;"
                "    text-align: left;"
                "    word-wrap: break-word;"
                "}"
                "QTableWidget::item:selected {"
                f"    background-color: {t('accent_subtle')};"
                "}"
                "QTableWidget QHeaderView::section {"
                f"    background-color: {t('bg_secondary')};"
                f"    color: {t('text_secondary')};"
                "    padding: 6px;"
                "    border: none;"
                "    font-size: 12px;"
                "}"
                "QTableWidget:focus {"
                f"    border: 2px solid {t('accent')};"
                "}"
            )
            table.verticalHeader().setVisible(False)
            # 不再固定列宽，改为内容自适应
            table.setWordWrap(True)
            table.horizontalHeader().setStretchLastSection(True)
            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

            # 让单元格可编辑
            for row in range(table.rowCount()):
                for col in range(col_count):
                    item = QTableWidgetItem("")
                    table.setItem(row, col, item)

            # 设置完所有项目后，让行高根据文本内容自动调整
            table.resizeRowsToContents()

            table_layout.addWidget(table)

            # 按钮行
            btn_layout = QHBoxLayout()
            btn_layout.setSpacing(8)

            # ── 导入 Excel 按钮（RB-003 修复：去除硬编码颜色，全部使用 token）──
            import_btn = QPushButton("📥 导入Excel")
            import_btn.setFixedHeight(28)
            import_btn.setStyleSheet(
                "QPushButton {"
                f"    background-color: {t('bg_secondary')};"
                f"    color: {t('success')};"
                f"    border: 1px solid {t('border_secondary')};"
                "    border-radius: 4px;"
                "    padding: 0 12px;"
                "    font-size: 12px;"
                "}"
                "QPushButton:hover {"
                f"    background-color: {t('bg_hover')};"
                f"    border-color: {t('success')};"
                "}"
            )

            def _on_import_excel():
                file_path, _ = QFileDialog.getOpenFileName(
                    None, "选择 Excel 或 CSV 文件", "",
                    "Excel/CSV 文件 (*.xlsx *.csv);;所有文件 (*)"
                )
                if not file_path:
                    return

                try:
                    rows = []
                    ext = os.path.splitext(file_path)[1].lower()

                    if ext == ".csv":
                        import csv
                        # 修复：支持 UTF-8 和 GBK 双编码，避免 Windows 下 CSV 导入失败
                        csv_content = None
                        for enc in ["utf-8-sig", "utf-8", "gbk", "gb2312"]:
                            try:
                                with open(file_path, "r", encoding=enc) as f:
                                    csv_content = f.read()
                                break
                            except (UnicodeDecodeError, UnicodeError):
                                continue
                        if csv_content is None:
                            QMessageBox.warning(None, "编码错误", "无法识别该 CSV 文件的编码，请转换为 UTF-8 格式后重试")
                            return
                        import io
                        reader = csv.reader(io.StringIO(csv_content))
                        for r in reader:
                            rows.append([c.strip() for c in r])
                    elif ext == ".xlsx":
                        import openpyxl
                        wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
                        ws = wb.active
                        for r in ws.iter_rows(values_only=True):
                            rows.append([str(c).strip() if c is not None else "" for c in r])
                        wb.close()
                    else:
                        QMessageBox.warning(None, "不支持的格式", f"不支持的文件格式：{ext}")
                        return

                    if not rows:
                        QMessageBox.warning(None, "空文件", "所选文件没有数据")
                        return

                    # 询问首行是否为标题
                    first_row_dialog = QMessageBox(None)
                    first_row_dialog.setWindowTitle("导入选项")
                    first_row_dialog.setText("首行是否为标题行？")
                    btn_yes = first_row_dialog.addButton("首行是标题（跳过）", QMessageBox.AcceptRole)
                    btn_no  = first_row_dialog.addButton("所有行都是数据", QMessageBox.RejectRole)
                    first_row_dialog.exec_()
                    skip_first = (first_row_dialog.clickedButton() == btn_yes)

                    data_rows = rows[1:] if skip_first else rows
                    if not data_rows:
                        QMessageBox.warning(None, "空数据", "跳过标题行后无数据")
                        return

                    # 清空表格并填充导入数据
                    table.setRowCount(len(data_rows))
                    for r, row_data in enumerate(data_rows):
                        for c in range(col_count):
                            cell_text = row_data[c] if c < len(row_data) else ""
                            item = QTableWidgetItem(cell_text)
                            table.setItem(r, c, item)
                    table.resizeColumnsToContents()
                    table.resizeRowsToContents()

                    QMessageBox.information(None, "导入成功", f"已导入 {len(data_rows)} 行数据")

                except Exception as e:
                    QMessageBox.critical(None, "导入失败", str(e))

            import_btn.clicked.connect(_on_import_excel)

            # ── 添加行按钮（RB-003 修复：去除硬编码颜色）──
            add_btn = QPushButton("＋ 添加行")
            add_btn.setFixedHeight(28)
            add_btn.setStyleSheet(
                "QPushButton {"
                f"    background-color: {t('bg_secondary')};"
                f"    color: {t('accent')};"
                f"    border: 1px solid {t('border_secondary')};"
                "    border-radius: 4px;"
                "    padding: 0 12px;"
                "    font-size: 12px;"
                "}"
                "QPushButton:hover {"
                f"    background-color: {t('bg_hover')};"
                f"    border-color: {t('accent')};"
                "}"
            )
            # ── 修复问题2：保存现有数据 → 插入新行 → 恢复所有数据 ──
            def _on_add_row():
                # 1. 先读取并保存表格中所有现有的数据
                existing_data = []
                for r in range(table.rowCount()):
                    row_data = []
                    for c in range(col_count):
                        it = table.item(r, c)
                        row_data.append(it.text() if it else "")
                    existing_data.append(row_data)

                # 2. 在末尾添加一行空白行
                new_row_idx = table.rowCount()
                table.insertRow(new_row_idx)
                for c in range(col_count):
                    item = QTableWidgetItem("")
                    table.setItem(new_row_idx, c, item)

                # 3. 将之前保存的数据重新填充回表格中
                for r, row_data in enumerate(existing_data):
                    for c, text in enumerate(row_data):
                        it = table.item(r, c)
                        if it:
                            it.setText(text)

                # 4. 调整新增行的高度
                table.resizeRowsToContents()

            add_btn.clicked.connect(_on_add_row)

            # ── 删除行按钮（RB-003 修复：去除硬编码颜色，使用 t('error') token）──
            del_btn = QPushButton("－ 删除行")
            del_btn.setFixedHeight(28)
            del_btn.setStyleSheet(
                "QPushButton {"
                f"    background-color: {t('bg_secondary')};"
                f"    color: {t('error')};"
                f"    border: 1px solid {t('border_secondary')};"
                "    border-radius: 4px;"
                "    padding: 0 12px;"
                "    font-size: 12px;"
                "}"
                "QPushButton:hover {"
                f"    background-color: {t('bg_hover')};"
                f"    border-color: {t('error')};"
                "}"
            )
            del_btn.clicked.connect(lambda: table.removeRow(table.currentRow()) if table.rowCount() > 1 else None)

            btn_layout.addWidget(import_btn)
            btn_layout.addWidget(add_btn)
            btn_layout.addWidget(del_btn)
            btn_layout.addStretch()
            table_layout.addLayout(btn_layout)

            widget = table_widget  # 整个容器作为 widget
            field_row.addWidget(widget)
            parent_layout.addWidget(field_container)
            self.field_widgets[key] = table
            return  # 已处理，直接返回

        else:
            widget = QLineEdit()
            widget.setObjectName(f"fieldInput_{key}")
            max_length = field.get("maxLength", 0)
            if max_length > 0:
                widget.setMaxLength(max_length)
            widget.setPlaceholderText(placeholder)
            widget.setStyleSheet(
                "QLineEdit {"
                f"    background-color: {t('bg_tertiary')};"
                f"    color: {t('text_primary')};"
                f"    border: 1px solid {t('border_secondary')};"
                "    border-radius: 6px;"
                "    padding: 0 12px;"
                "    font-size: 13px;"
                "    min-height: 36px;"
                "}"
                "QLineEdit:focus {"
                f"    border: 2px solid {t('accent')};"
                "}"
                "QLineEdit::placeholder {"
                f"    color: {t('text_muted')};"
                "}"
            )
            # 实时预览更新（延迟触发）
            widget.textChanged.connect(self._on_field_changed)

        if isinstance(widget, QTextEdit):
            widget.textChanged.connect(self._on_field_changed)

        field_row.addWidget(widget)
        parent_layout.addWidget(field_container)
        self.field_widgets[key] = widget

    # ============================================================
    # 发票明细项目表格编辑器 — 辅助方法
    # ============================================================
    def _add_invoice_row(self, table):
        """新增一行空白行（含行级删除按钮）"""
        table.blockSignals(True)
        row = table.rowCount()
        table.insertRow(row)
        for c in range(3):
            item = QTableWidgetItem("")
            table.setItem(row, c, item)
        # 第4列：行级删除按钮
        del_btn = QPushButton("×")
        del_btn.setFixedSize(24, 24)
        del_btn.setStyleSheet(
            "QPushButton {"
            f"    color: {t('error')};"
            "    border: none;"
            "    border-radius: 12px;"
            "    font-size: 14px;"
            "    font-weight: bold;"
            "    background: transparent;"
            "}"
            "QPushButton:hover {"
            "    background-color: rgba(255,59,48,0.1);"
            "}"
        )
        del_btn.clicked.connect(lambda checked, t=table, r=row: self._delete_invoice_row(t, r))
        table.setCellWidget(row, 3, del_btn)
        table.blockSignals(False)
        self._update_invoice_total(table)
        self._on_field_changed()

    def _delete_invoice_row(self, table, row):
        """删除指定行（保留至少 1 行）"""
        if table.rowCount() <= 1:
            for c in range(3):
                it = table.item(0, c)
                if it:
                    it.setText("")
            return
        table.blockSignals(True)
        table.removeRow(row)
        table.blockSignals(False)
        self._update_invoice_total(table)
        self._on_field_changed()

    def _delete_selected_invoice_row(self, table):
        """删除当前选中行（保留至少 1 行）"""
        current = table.currentRow()
        if current < 0:
            return
        if table.rowCount() <= 1:
            for c in range(3):
                it = table.item(0, c)
                if it:
                    it.setText("")
            return
        table.blockSignals(True)
        table.removeRow(current)
        table.blockSignals(False)
        self._update_invoice_total(table)
        self._on_field_changed()

    def get_invoice_items(self):
        """读取发票明细表格数据，返回 [{name, qty, price}, ...]"""
        widget = self.field_widgets.get("items")
        if widget is None:
            return []
        if not isinstance(widget, QTableWidget):
            # 兼容旧 QTextEdit（回退路径）
            text = widget.toPlainText().strip()
            return parse_items(text) if text else []
        rows = []
        for r in range(widget.rowCount()):
            name_it = widget.item(r, 0)
            qty_it = widget.item(r, 1)
            price_it = widget.item(r, 2)
            name = name_it.text().strip() if name_it else ""
            qty = qty_it.text().strip() if qty_it else ""
            price = price_it.text().strip() if price_it else ""
            if name or qty or price:
                rows.append({"name": name, "qty": qty, "price": price})
        return rows

    def _update_invoice_total(self, table):
        """根据数量×金额自动计算合计，同步更新 total_amount 字段"""
        total = 0.0
        for r in range(table.rowCount()):
            qty_it = table.item(r, 1)
            price_it = table.item(r, 2)
            qty_str = qty_it.text().strip() if qty_it else ""
            price_str = price_it.text().strip() if price_it else ""
            try:
                qty = float(qty_str.replace(",", "").replace("¥", "").strip()) if qty_str else 0
                price = float(price_str.replace(",", "").replace("¥", "").strip()) if price_str else 0
                total += qty * price
            except (ValueError, TypeError):
                pass
        # 格式化合计字符串
        if total == int(total):
            total_str = str(int(total))
        else:
            total_str = f"{total:.2f}"
        # 更新 UI 标签
        if hasattr(self, '_invoice_total_label'):
            self._invoice_total_label.setText(f"合计：{total_str}")
        # 同步更新 total_amount 字段（让预览和 PDF 也使用计算值）
        total_widget = self.field_widgets.get("total_amount")
        if total_widget is not None:
            total_widget.blockSignals(True)
            total_widget.setText(total_str)
            total_widget.blockSignals(False)

    def _on_invoice_cell_changed(self, table, row, col):
        """发票单元格变更：验证 + 合计 + 触发预览更新"""
        self._validate_invoice_cell(table, row, col)
        self._update_invoice_total(table)
        self._on_field_changed()

    def _validate_invoice_cell(self, table, row, col):
        """对发票表格单元格进行输入验证，违规时设置红底提示"""
        from PySide6.QtGui import QColor
        item = table.item(row, col)
        if item is None:
            return
        text = item.text().strip()
        is_invalid = False

        if col == 0:  # 项目名称：≤ 20字
            if len(text) > 20:
                is_invalid = True
        elif col == 1:  # 数量：数字，≤ 99999
            if text:
                if not _is_numeric(text):
                    is_invalid = True
                else:
                    try:
                        if float(text) > 99999:
                            is_invalid = True
                    except ValueError:
                        is_invalid = True
        elif col == 2:  # 单价：数字，≤ 999999999
            if text:
                if not _is_numeric(text):
                    is_invalid = True
                else:
                    try:
                        if float(text) > 999999999:
                            is_invalid = True
                    except ValueError:
                        is_invalid = True

        if is_invalid:
            item.setBackground(QColor("#FFE0E0"))
            item.setToolTip("输入值超出允许范围")
        else:
            item.setBackground(QColor())
            item.setToolTip("")

    def _truncate_remark_textedit(self, widget: QTextEdit, max_len: int):
        """限制备注 QTextEdit 输入长度，超出截断"""
        text = widget.toPlainText()
        if len(text) > max_len:
            cursor = widget.textCursor()
            pos = cursor.position()
            widget.blockSignals(True)
            widget.setPlainText(text[:max_len])
            # 恢复光标位置
            cursor = widget.textCursor()
            cursor.setPosition(min(pos, max_len))
            widget.setTextCursor(cursor)
            widget.blockSignals(False)

    # ── TPL-05：文件上传区域 ───────────────────────────────────
    def _add_upload_section(self):
        """
        为当前模板添加文件上传区域。
        支持 business_card 等配置了上传功能的模板。
        V1.1 RC1：支持 per-side 多上传（正面 LOGO + 背面 二维码）
        """
        upload_configs = UPLOAD_TEMPLATES.get(self.template_id, [])
        # 筛选当前面的上传项
        side_uploads = [
            c for c in upload_configs
            if c.get("side") in (self._current_side, "both")
        ]
        if not side_uploads:
            return

        # 初始化 widget 索引
        if not hasattr(self, "_upload_widgets"):
            self._upload_widgets = {}

        for cfg in side_uploads:
            self._add_single_upload_card(cfg)

    def _add_single_upload_card(self, cfg: dict):
        """渲染单个上传卡片（正/背面复用）"""
        key = cfg["key"]
        title = cfg.get("title", "上传文件")
        icon = cfg.get("icon", "🖼")
        suffixes = cfg.get("accepted_suffixes", ["png", "jpg", "jpeg", "pdf"])
        show_pos_shape = cfg.get("show_position_shape", False)

        # 分隔标题
        upload_header = QLabel(f"{icon}  {title}")
        upload_header.setObjectName(f"uploadHeader_{key}")
        upload_header.setStyleSheet(
            f"color: {t('text_primary')}; font-size: 13px; font-weight: 600; "
            "background-color: transparent; padding-top: 4px;"
        )
        self.formLayout.addWidget(upload_header)

        # 上传卡片
        upload_card = QFrame()
        upload_card.setObjectName(f"uploadCard_{key}")
        upload_card.setStyleSheet(
            "QFrame {"
            f"    background-color: {t('bg_secondary')};"
            f"    border: 1px solid {t('border_secondary')};"
            "    border-radius: 8px;"
            "}"
        )
        upload_card_layout = QVBoxLayout(upload_card)
        upload_card_layout.setSpacing(12)
        upload_card_layout.setContentsMargins(16, 16, 16, 16)

        # 说明文字
        ext_list = " / ".join("." + s for s in suffixes)
        hint_label = QLabel(f"支持 {ext_list} 格式")
        hint_label.setObjectName(f"uploadHint_{key}")
        hint_label.setStyleSheet(
            f"color: {t('text_tertiary')}; font-size: 12px; background-color: transparent;"
        )
        upload_card_layout.addWidget(hint_label)

        # 按钮 + 预览区域
        btn_preview_layout = QHBoxLayout()
        btn_preview_layout.setSpacing(12)

        # 上传按钮
        upload_btn = QPushButton("📁  选择文件")
        upload_btn.setObjectName(f"uploadBtn_{key}")
        upload_btn.setFixedHeight(36)
        upload_btn.setStyleSheet(
            "QPushButton {"
            f"    background-color: {t('bg_secondary')};"
            f"    color: {t('text_primary')};"
            f"    border: 1px solid {t('border_secondary')};"
            "    border-radius: 6px;"
            "    padding: 0 16px;"
            "    font-size: 13px;"
            "}"
            "QPushButton:hover {"
            f"    background-color: {t('bg_pressed')};"
            f"    border-color: {t('accent')};"
            "}"
        )
        upload_btn.clicked.connect(lambda _=False, k=key, s=suffixes: self._on_upload_clicked(k, s))
        btn_preview_layout.addWidget(upload_btn)

        # 文件预览标签
        preview_label = QLabel("未选择文件")
        preview_label.setObjectName(f"uploadPreview_{key}")
        preview_label.setStyleSheet(
            f"color: {t('text_secondary')}; font-size: 12px; background-color: transparent;"
        )
        preview_label.setMinimumWidth(120)
        btn_preview_layout.addWidget(preview_label, stretch=1)

        upload_card_layout.addLayout(btn_preview_layout)

        # 清除按钮（已上传时显示）
        clear_btn = QPushButton("✕ 清除")
        clear_btn.setObjectName(f"clearUpload_{key}")
        clear_btn.setFixedHeight(28)
        clear_btn.setVisible(bool(self._uploaded_paths.get(key)))
        clear_btn.setStyleSheet(
            "QPushButton {"
            "    background-color: transparent;"
            f"    color: {t('text_tertiary')};"
            "    border: none;"
            "    font-size: 12px;"
            "}"
            "QPushButton:hover {"
            f"    color: {t('error') if 'error' in t.__globals__.get('TOKENS', {}) else '#FF5252'};"
            "}"
        )
        clear_btn.clicked.connect(lambda _=False, k=key: self._on_clear_upload(k))
        upload_card_layout.addWidget(clear_btn)

        # 记录 widget 引用，便于后续刷新状态
        self._upload_widgets[key] = {
            "preview_label": preview_label,
            "clear_btn": clear_btn,
            "upload_btn": upload_btn,
        }

        # 同步显示当前已上传的文件
        cur_path = self._uploaded_paths.get(key)
        if cur_path and os.path.isfile(cur_path):
            file_name = os.path.basename(cur_path)
            preview_label.setText(file_name)
            preview_label.setStyleSheet(
                f"color: {t('accent')}; font-size: 12px; background-color: transparent;"
            )

        # ── LOGO 位置/大小/形状调整（按 show_position_shape 决定）──
        if show_pos_shape:
            self._build_logo_adjust_frame(upload_card_layout)

        self.formLayout.addWidget(upload_card)
        self.formLayout.addSpacing(8)

    def _build_logo_adjust_frame(self, parent_layout):
        """构建 LOGO 位置/大小/形状调整区域（仅 LOGO 上传卡片显示）"""
        logo_adjust_frame = QFrame()
        logo_adjust_frame.setObjectName("logoAdjustFrame")
        logo_adjust_frame.setStyleSheet(
            "QFrame#logoAdjustFrame {"
            "    background-color: transparent;"
            f"    border: 1px solid {t('border_secondary')};"
            "    border-radius: 6px;"
            "}"
        )
        logo_adjust_layout = QVBoxLayout(logo_adjust_frame)
        logo_adjust_layout.setSpacing(8)
        logo_adjust_layout.setContentsMargins(12, 10, 12, 10)

        adjust_label = QLabel("Logo 位置调整")
        adjust_label.setStyleSheet(
            f"color: {t('text_secondary')}; font-size: 12px; font-weight: 600; background-color: transparent;"
        )
        logo_adjust_layout.addWidget(adjust_label)

        # 大小
        size_row = QHBoxLayout()
        size_row.setSpacing(8)
        size_label = QLabel("大小:")
        size_label.setStyleSheet(f"color: {t('text_tertiary')}; font-size: 12px; background-color: transparent;")
        size_label.setFixedWidth(50)
        size_row.addWidget(size_label)
        self.logoWidthSpin = QDoubleSpinBox()
        self.logoWidthSpin.setRange(10, 50)
        self.logoWidthSpin.setValue(self._logo_width_mm)
        self.logoWidthSpin.setSuffix(" mm")
        self.logoWidthSpin.setSingleStep(1)
        self.logoWidthSpin.setFixedWidth(100)
        self.logoWidthSpin.setStyleSheet(
            "QDoubleSpinBox {"
            f"    background-color: {t('bg_tertiary')}; color: {t('text_primary')};"
            f"    border: 1px solid {t('border_secondary')}; border-radius: 4px;"
            "    padding: 2px 8px; font-size: 12px;"
            "}"
        )
        self.logoWidthSpin.valueChanged.connect(self._on_logo_setting_changed)
        size_row.addWidget(self.logoWidthSpin)
        size_row.addStretch()
        logo_adjust_layout.addLayout(size_row)

        # 右间距
        right_row = QHBoxLayout()
        right_row.setSpacing(8)
        right_label = QLabel("右间距:")
        right_label.setStyleSheet(f"color: {t('text_tertiary')}; font-size: 12px; background-color: transparent;")
        right_label.setFixedWidth(50)
        right_row.addWidget(right_label)
        self.logoRightSpin = QDoubleSpinBox()
        self.logoRightSpin.setRange(0, 30)
        self.logoRightSpin.setValue(self._logo_right_mm)
        self.logoRightSpin.setSuffix(" mm")
        self.logoRightSpin.setSingleStep(1)
        self.logoRightSpin.setFixedWidth(100)
        self.logoRightSpin.setStyleSheet(
            "QDoubleSpinBox {"
            f"    background-color: {t('bg_tertiary')}; color: {t('text_primary')};"
            f"    border: 1px solid {t('border_secondary')}; border-radius: 4px;"
            "    padding: 2px 8px; font-size: 12px;"
            "}"
        )
        self.logoRightSpin.valueChanged.connect(self._on_logo_setting_changed)
        right_row.addWidget(self.logoRightSpin)
        right_row.addStretch()
        logo_adjust_layout.addLayout(right_row)

        # 上间距
        top_row = QHBoxLayout()
        top_row.setSpacing(8)
        top_label = QLabel("上间距:")
        top_label.setStyleSheet(f"color: {t('text_tertiary')}; font-size: 12px; background-color: transparent;")
        top_label.setFixedWidth(50)
        top_row.addWidget(top_label)
        self.logoTopSpin = QDoubleSpinBox()
        self.logoTopSpin.setRange(0, 30)
        self.logoTopSpin.setValue(self._logo_top_mm)
        self.logoTopSpin.setSuffix(" mm")
        self.logoTopSpin.setSingleStep(1)
        self.logoTopSpin.setFixedWidth(100)
        self.logoTopSpin.setStyleSheet(
            "QDoubleSpinBox {"
            f"    background-color: {t('bg_tertiary')}; color: {t('text_primary')};"
            f"    border: 1px solid {t('border_secondary')}; border-radius: 4px;"
            "    padding: 2px 8px; font-size: 12px;"
            "}"
        )
        self.logoTopSpin.valueChanged.connect(self._on_logo_setting_changed)
        top_row.addWidget(self.logoTopSpin)
        top_row.addStretch()
        logo_adjust_layout.addLayout(top_row)

        # 形状选择
        shape_row = QHBoxLayout()
        shape_row.setSpacing(8)
        shape_label = QLabel("形状:")
        shape_label.setStyleSheet(f"color: {t('text_tertiary')}; font-size: 12px; background-color: transparent;")
        shape_label.setFixedWidth(50)
        shape_row.addWidget(shape_label)
        self.logoShapeSquare = QPushButton("方形")
        self.logoShapeSquare.setCheckable(True)
        self.logoShapeSquare.setChecked(self._logo_shape == "square")
        self.logoShapeSquare.setFixedHeight(28)
        self.logoShapeSquare.setObjectName("logoShapeSquare")
        self.logoShapeSquare.clicked.connect(lambda: self._on_logo_shape_changed("square"))
        shape_row.addWidget(self.logoShapeSquare)
        self.logoShapeCircle = QPushButton("圆形")
        self.logoShapeCircle.setCheckable(True)
        self.logoShapeCircle.setChecked(self._logo_shape == "circle")
        self.logoShapeCircle.setFixedHeight(28)
        self.logoShapeCircle.setObjectName("logoShapeCircle")
        self.logoShapeCircle.clicked.connect(lambda: self._on_logo_shape_changed("circle"))
        shape_row.addWidget(self.logoShapeCircle)
        shape_row.addStretch()
        logo_adjust_layout.addLayout(shape_row)

        # 同步形状按钮样式
        self._style_logo_shape_btn(self._logo_shape)

        parent_layout.addWidget(logo_adjust_frame)

    def _on_upload_clicked(self, key: str = None, suffixes: list = None):
        """TPL-05：点击上传按钮，弹出文件选择对话框。V1.1 RC：上传时立即 PIL 校验。"""
        if key is None:
            key = "logo"
        if suffixes is None:
            suffixes = ["png", "jpg", "jpeg"]

        filter_str = f"支持的格式 ({' '.join(['*.' + s for s in suffixes])})"
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择文件",
            "",
            filter_str,
        )

        if file_path:
            # V1.1 RC 收尾：先 PIL 校验 — 不接受无法用 PIL 打开的格式（PDF/损坏文件等）
            try:
                from PIL import Image as _PILImg
                with _PILImg.open(file_path) as _test_img:
                    _test_img.size  # 触发完整解析
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "图片格式不支持",
                    f"无法读取该文件作为图片：\n{os.path.basename(file_path)}\n\n"
                    f"原因：{e}\n\n"
                    "请使用 PNG（推荐，透明背景）或 JPG 格式。\n"
                    "PDF 暂不支持作为 LOGO/二维码。",
                )
                return
            self._uploaded_paths[key] = file_path
            # 同步到 form data（持久化）
            field_key = key  # 默认 key 就是 field key
            for cfg in UPLOAD_TEMPLATES.get(self.template_id, []):
                if cfg.get("key") == key and cfg.get("field"):
                    field_key = cfg["field"]
                    break
            if self.template_data is not None:
                self.template_data.setdefault("data", {})[field_key] = file_path
            # 刷新对应 widget 状态
            self._refresh_upload_widget_state(key)
            # 触发预览
            if hasattr(self, "preview_timer"):
                self.preview_timer.start(200)

    def _on_clear_upload(self, key: str = None):
        """TPL-05：清除已上传的文件"""
        if key is None:
            key = "logo"
        self._uploaded_paths[key] = None
        # 同步到 form data
        if self.template_data is not None:
            self.template_data.setdefault("data", {}).pop(key, None)
        self._refresh_upload_widget_state(key)
        if hasattr(self, "preview_timer"):
            self.preview_timer.start(200)

    def _refresh_upload_widget_state(self, key: str):
        """根据 _uploaded_paths[key] 刷新上传卡片的 UI 状态"""
        widgets = getattr(self, "_upload_widgets", {}).get(key, {})
        preview_label = widgets.get("preview_label")
        clear_btn = widgets.get("clear_btn")
        cur_path = self._uploaded_paths.get(key)
        if preview_label is not None:
            if cur_path and os.path.isfile(cur_path):
                preview_label.setText(os.path.basename(cur_path))
                preview_label.setStyleSheet(
                    f"color: {t('accent')}; font-size: 12px; background-color: transparent;"
                )
            else:
                preview_label.setText("未选择文件")
                preview_label.setStyleSheet(
                    f"color: {t('text_secondary')}; font-size: 12px; background-color: transparent;"
                )
        if clear_btn is not None:
            clear_btn.setVisible(bool(cur_path and os.path.isfile(cur_path)))

    # ── LOGO 设置变更 ───────────────────────────────────────────
    def _on_logo_setting_changed(self):
        if hasattr(self, 'logoWidthSpin'):
            self._logo_width_mm = self.logoWidthSpin.value()
            self._logo_right_mm = self.logoRightSpin.value()
            self._logo_top_mm = self.logoTopSpin.value()
        self.preview_timer.start(300)

    def _on_logo_shape_changed(self, shape: str):
        self._logo_shape = shape
        if shape == "square":
            self.logoShapeSquare.setChecked(True)
            self.logoShapeCircle.setChecked(False)
            self._style_logo_shape_btn("square")
        else:
            self.logoShapeSquare.setChecked(False)
            self.logoShapeCircle.setChecked(True)
            self._style_logo_shape_btn("circle")
        self.preview_timer.start(300)

    def _style_logo_shape_btn(self, active: str):
        base = (
            f"background-color: {t('bg_hover')}; color: {t('text_secondary')}; border: 1px solid {t('border_secondary')}; "
            "border-radius: 4px; padding: 0 12px; font-size: 12px;"
        )
        active_style = (
            f"background-color: {t('bg_hover')}; color: {t('text_primary')}; border: 1px solid {t('accent')}; "
            "border-radius: 4px; padding: 0 12px; font-size: 12px;"
        )
        self.logoShapeSquare.setStyleSheet(active_style if active == "square" else base)
        self.logoShapeCircle.setStyleSheet(active_style if active == "circle" else base)

    def _get_logo_preview_html(self) -> str:
        logo_path = self._uploaded_paths.get("logo")
        if not logo_path or not os.path.isfile(logo_path):
            return ""
        ext = os.path.splitext(logo_path)[1].lower()
        if ext not in [".png", ".jpg", ".jpeg"]:
            return ""
        try:
            import base64
            with open(logo_path, "rb") as f:
                img_data = base64.b64encode(f.read()).decode("utf-8")
            mime = "image/png" if ext == ".png" else "image/jpeg"
            data_uri = f"data:{mime};base64,{img_data}"
            return f'<img src="{data_uri}" alt="Logo">'
        except Exception:
            return ""

    def _on_field_changed(self):
        # RB-002: 状态恢复期间抑制 field change 信号，避免 1 次切换触发 N 次 preview render
        if getattr(self, "_restoring_state", False):
            return
        # ── P0-Fix: 立即同步缓存到当前 side（避免快速切侧时丢字段）──
        # debounce 只用于昂贵的预览渲染，缓存写入是 O(N) dict.update，必须同步
        if hasattr(self, '_current_side') and hasattr(self, 'field_widgets'):
            cache = self._side_state_cache.setdefault(
                self._current_side, {"fields": {}, "scroll": 0}
            )
            sender = self.sender()
            if sender is not None:
                key = self._key_from_sender(sender)
                if key:
                    try:
                        if isinstance(sender, QTextEdit):
                            cache["fields"][key] = sender.toPlainText()
                        elif isinstance(sender, QTableWidget):
                            rows = []
                            for r in range(sender.rowCount()):
                                row_data = []
                                for c in range(sender.columnCount()):
                                    it = sender.item(r, c)
                                    row_data.append(it.text() if it else "")
                                rows.append(row_data)
                            cache["fields"][key] = rows
                        elif hasattr(sender, "text"):
                            cache["fields"][key] = sender.text()
                    except RuntimeError:
                        pass
        self.preview_timer.start(200)

    def _key_from_sender(self, sender) -> str:
        """从 signal sender 提取 field key（兼容 fieldInput_/fieldTextarea_/fieldTable_/tableWidget_ 前缀）"""
        try:
            obj_name = sender.objectName() or ""
        except RuntimeError:
            return ""
        for prefix in ("fieldInput_", "fieldTextarea_", "fieldTable_", "tableWidget_", "fieldRow_"):
            if obj_name.startswith(prefix):
                return obj_name[len(prefix):]
        return ""

    # ── AT-08: 样式预设系统 ─────────────────────────────────
    def _load_presets(self):
        """从 assets/templates/presets/{template_id}.json 加载预设"""
        presets_dir = os.path.join(TEMPLATES_PATH, "presets")
        if not os.path.isdir(presets_dir):
            return

        preset_path = os.path.join(presets_dir, f"{self.template_id}.json")
        if not os.path.isfile(preset_path):
            return

        try:
            with open(preset_path, encoding="utf-8") as f:
                presets = json.load(f)
            if isinstance(presets, list):
                for preset in presets:
                    name = preset.get("name", "未命名预设")
                    self._preset_selector.addItem(name, preset)
            elif isinstance(presets, dict):
                self._preset_selector.addItem(presets.get("name", "预设"), presets)
        except (json.JSONDecodeError, IOError):
            pass

    def _on_preset_selected(self, index: int):
        """预设选择回调"""
        preset_data = self._preset_selector.itemData(index)
        if not preset_data or self._applying_preset:
            return

        self._applying_preset = True
        try:
            self._apply_preset_values(preset_data)
        finally:
            self._applying_preset = False

        self._update_preview()
        self._check_preset_match()

    def _apply_preset_values(self, preset: dict):
        """应用预设值到所有样式控件"""
        values = preset.get("values", preset)

        if "theme_color" in values:
            theme_group = self.style_widgets.get("theme_color")
            if theme_group:
                for btn in theme_group.buttons():
                    if btn.property("theme_value") == values["theme_color"]:
                        btn.setChecked(True)
                        self._on_theme_changed(btn)
                        break

        if "bar_position" in values:
            bar_group = self.style_widgets.get("bar_position")
            if bar_group:
                for btn in bar_group.buttons():
                    if btn.property("bar_value") == values["bar_position"]:
                        btn.setChecked(True)
                        self._on_bar_position_changed(btn)
                        break

        if "bg_style" in values:
            bg_group = self.style_widgets.get("bg_style")
            if bg_group:
                for btn in bg_group.buttons():
                    if btn.property("bg_value") == values["bg_style"]:
                        btn.setChecked(True)
                        self._on_bg_style_changed(btn)
                        break

        if "bg_texture" in values:
            texture_group = self.style_widgets.get("bg_texture")
            if texture_group:
                for btn in texture_group.buttons():
                    if btn.property("texture_value") == values["bg_texture"]:
                        btn.setChecked(True)
                        self._on_texture_changed(btn)
                        break

        if "font_style" in values:
            font_style_group = self.style_widgets.get("font_style")
            if font_style_group:
                for btn in font_style_group.buttons():
                    if btn.property("font_style_value") == values["font_style"]:
                        btn.setChecked(True)
                        self._on_font_style_changed(btn)
                        break

        if "header_style" in values:
            header_style_group = self.style_widgets.get("header_style")
            if header_style_group:
                for btn in header_style_group.buttons():
                    if btn.property("header_style_value") == values["header_style"]:
                        btn.setChecked(True)
                        self._on_header_style_changed(btn)
                        break

        if "table_style" in values:
            table_style_group = self.style_widgets.get("table_style")
            if table_style_group:
                for btn in table_style_group.buttons():
                    if btn.property("table_style_value") == values["table_style"]:
                        btn.setChecked(True)
                        self._on_table_style_changed(btn)
                        break

        if "text_color" in values:
            self._text_color = values["text_color"]
            self.textColorBtn.setStyleSheet(
                "QPushButton {"
                f"    background-color: {self._text_color}; border: 1px solid {t('border_secondary')}; border-radius: 4px;"
                "}"
                f"QPushButton:hover {{ border: 1px solid {t('accent')}; }}"
            )
            self.textColorHex.blockSignals(True)
            self.textColorHex.setText(self._text_color)
            self.textColorHex.blockSignals(False)

        if "text_secondary_color" in values:
            self._text_secondary_color = values["text_secondary_color"]
            self.secondaryColorBtn.setStyleSheet(
                "QPushButton {"
                f"    background-color: {self._text_secondary_color}; border: 1px solid {t('border_secondary')}; border-radius: 4px;"
                "}"
                f"QPushButton:hover {{ border: 1px solid {t('accent')}; }}"
            )
            self.secondaryColorHex.blockSignals(True)
            self.secondaryColorHex.setText(self._text_secondary_color)
            self.secondaryColorHex.blockSignals(False)

    def _check_preset_match(self):
        """检测当前值是否匹配某个预设"""
        current = self._get_current_style_values()
        for i in range(1, self._preset_selector.count()):
            preset_data = self._preset_selector.itemData(i)
            if not preset_data:
                continue
            if self._values_match_preset(current, preset_data):
                self._preset_selector.setCurrentIndex(i)
                return
        self._preset_selector.setCurrentIndex(0)

    def _values_match_preset(self, current: dict, preset: dict) -> bool:
        """检查当前值是否与预设匹配"""
        values = preset.get("values", preset)
        keys_to_check = [
            "theme_color", "bar_position", "bg_style", "bg_texture",
            "font_style", "header_style", "table_style",
            "text_color", "text_secondary_color"
        ]
        for key in keys_to_check:
            if key in values:
                if current.get(key) != values[key]:
                    return False
        return True

    # ── 实时预览 ──────────────────────────────────────────────
    def _update_preview(self):
        if not self.template_data:
            return

        data = {}
        preview_data = {}
        has_content = False
        for field in self.template_data.get("fields", []):
            key = field.get("key", "")
            widget = self.field_widgets.get(key)
            if widget is None:
                continue
            if isinstance(widget, QTextEdit):
                value = widget.toPlainText().strip()
            elif isinstance(widget, QTableWidget):
                if key == "items":
                    value = self.get_invoice_items()
                else:
                    value = ""
                    for row in range(widget.rowCount()):
                        for col in range(widget.columnCount()):
                            item = widget.item(row, col)
                            if item and item.text().strip():
                                value = "已填写"
                                break
                        if value:
                            break
            else:
                value = widget.text().strip()

            # ── 修复：data 必须保持原始字符串（用于渲染器）；
            # 预览需要占位符显示时，从 preview_data 走 HTML。 ──
            data[key] = value
            if value:
                has_content = True
                preview_data[key] = value
            else:
                preview_data[key] = f'<span style="color: {t("text_muted")}; font-style: italic;">{field.get("placeholder", "未填写")}</span>'

        if hasattr(self, 'previewInfoLabel'):
            self.previewInfoLabel.setVisible(not has_content)

        if not self.webengine_available:
            if hasattr(self, 'fallbackPreview'):
                if not has_content:
                    self.fallbackPreview.setText("填写左侧表单以查看名片预览")
                else:
                    self.fallbackPreview.setText("已填写数据\n\n预览需要安装 PySide6-WebEngine 才能查看")
            return

        template_id = self.template_data.get("id", "")

        if template_id == "business_card":
            self._render_business_card_preview(preview_data)

        elif template_id == "notice":
            styles = self._get_current_style_values()
            accent_color = styles["theme_color"]
            bg_style = styles["bg_style"]
            bar_position = styles["bar_position"]
            bg_custom_color = styles["bg_custom_color"]
            bg_texture = styles["bg_texture"]
            font_style = styles.get("font_style", "formal")
            text_color = styles["text_color"]
            text_secondary_color = styles["text_secondary_color"]

            bg_color, bg_gradient, texture_css = _get_bg_css(bg_style, bg_custom_color, bg_texture, text_color)
            bar_pos, bar_size = _get_bar_css(bar_position, accent_color)

            title_weight = "900" if font_style == "bold" else ("400" if font_style == "modern" else "600")
            title_size = 34 if font_style == "bold" else (24 if font_style == "modern" else 28)
            title_color = accent_color if font_style != "bold" else text_color
            title_spacing = 4 if font_style == "bold" else 2
            sep_width = 120 if font_style == "bold" else (40 if font_style == "modern" else 60)
            sep_height = 5 if font_style == "bold" else 3
            font_family_style = ""
            if font_style == "formal":
                font_family_style = "font-family: 'SimSun', 'Noto Serif SC', serif;"
            elif font_style == "modern":
                font_family_style = "font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;"
            elif font_style == "bold":
                font_family_style = "font-family: 'SimHei', 'Microsoft YaHei', sans-serif;"

            html = NOTICE_CSS.format(
                title=data.get("title", ""),
                date=data.get("date", ""),
                body=data.get("body", ""),
                issuer=data.get("issuer", ""),
                accent_color=accent_color,
                bg_color=bg_color,
                bg_gradient=bg_gradient,
                texture_css=texture_css,
                bar_pos=bar_pos,
                bar_size=bar_size,
                text_color=text_color,
                text_secondary_color=text_secondary_color,
                title_weight=title_weight,
                title_size=title_size,
                title_color=title_color,
                title_spacing=title_spacing,
                sep_width=sep_width,
                sep_height=sep_height,
                font_family_style=font_family_style,
            )
            self.previewView.setHtml(html)

        elif template_id == "product_spec":
            styles = self._get_current_style_values()
            accent_color = styles["theme_color"]
            bg_style = styles["bg_style"]
            bg_custom_color = styles["bg_custom_color"]
            bg_texture = styles["bg_texture"]
            header_style = styles.get("header_style", "bar")
            table_style = styles.get("table_style", "striped")
            text_color = styles["text_color"]
            text_secondary_color = styles["text_secondary_color"]

            bg_color, bg_gradient, texture_css = _get_bg_css(bg_style, bg_custom_color, bg_texture, text_color)

            header_bg_css = ""
            header_text_color = accent_color
            version_color = text_secondary_color
            if header_style == "bar":
                header_bg_css = f"border-left: 4px solid {accent_color};"
            elif header_style == "color_block":
                header_bg_css = f"background: linear-gradient(135deg, {accent_color}, {accent_color}dd); color: #fff;"
                header_text_color = "#FFFFFF"
                version_color = t("border_primary")
            elif header_style == "none":
                header_bg_css = ""

            td_style = ""
            param_style = ""
            value_style = ""
            table_style_css = ""
            if table_style == "striped":
                table_style_css = ""
                td_style = f"border-bottom: 1px solid {t('border_primary')};"
            elif table_style == "bordered":
                table_style_css = f"border: 1px solid {t('border_primary')};"
                td_style = f"border: 1px solid {t('border_primary')};"
            elif table_style == "minimal":
                td_style = "padding: 8px 4px;"
                param_style = "font-weight: 500;"
                value_style = f"color: {t('text_secondary')};"

            specs_rows = ""
            specs_data = data.get("specs", "")
            if isinstance(specs_data, list) and specs_data:
                for row_data in specs_data:
                    if isinstance(row_data, dict):
                        param = row_data.get("param", "")
                        value = row_data.get("value", "")
                        specs_rows += f"<tr><td>{param}</td><td>{value}</td></tr>\n"
            elif specs_data and specs_data != "已填写":
                pass

            html = PRODUCT_SPEC_CSS.format(
                product_name=data.get("product_name", ""),
                version=data.get("version", ""),
                description=data.get("description", ""),
                specs_rows=specs_rows,
                accent_color=accent_color,
                bg_color=bg_color,
                bg_gradient=bg_gradient,
                texture_css=texture_css,
                header_bg_css=header_bg_css,
                header_text_color=header_text_color,
                version_color=version_color,
                text_color=text_color,
                text_secondary_color=text_secondary_color,
                table_style_css=table_style_css,
                td_style=td_style,
                param_style=param_style,
                value_style=value_style,
            )
            self.previewView.setHtml(html)

        elif template_id == "report":
            styles = self._get_current_style_values()
            accent_color = styles["theme_color"]
            bg_style = styles["bg_style"]
            bg_custom_color = styles["bg_custom_color"]
            bg_texture = styles["bg_texture"]
            header_style = styles.get("header_style", "color_block")
            text_color = styles["text_color"]
            text_secondary_color = styles["text_secondary_color"]

            bg_color, bg_gradient, texture_css = _get_bg_css(bg_style, bg_custom_color, bg_texture, text_color)

            # Header style
            header_bg_css = ""
            header_text_color = accent_color
            subtitle_color = text_secondary_color
            if header_style == "color_block":
                header_bg_css = f"background: linear-gradient(135deg, {accent_color}, {accent_color}dd); color: #fff;"
                header_text_color = "#FFFFFF"
                subtitle_color = "rgba(255,255,255,0.75)"
            elif header_style == "bar":
                header_bg_css = f"border-left: 4px solid {accent_color};"
            elif header_style == "none":
                header_bg_css = ""

            # Meta text
            meta_parts = []
            author_val = data.get("author", "")
            date_val = data.get("date", "")
            if author_val:
                meta_parts.append(f"作者：{author_val}")
            if date_val:
                meta_parts.append(f"日期：{date_val}")
            meta_text = " &nbsp;|&nbsp; ".join(meta_parts) if meta_parts else ""

            # Summary
            summary_val = data.get("summary", "").strip()
            summary_html = ""
            if summary_val:
                summary_html = (
                    f'<div class="report-summary">'
                    f'<div class="report-summary-title">摘要</div>'
                    f'<div class="report-summary-text">{summary_val}</div>'
                    f'</div>'
                )

            # Sections: parse "## heading\nbody" format
            sections_val = data.get("sections", "").strip()
            sections_html = ""
            if sections_val:
                import re
                parts = re.split(r'^## ', sections_val, flags=re.MULTILINE)
                for part in parts:
                    part = part.strip()
                    if not part:
                        continue
                    lines = part.split('\n', 1)
                    heading = lines[0].strip()
                    body = lines[1].strip() if len(lines) > 1 else ""
                    sections_html += f'<div class="report-section-heading">{heading}</div>'
                    if body:
                        sections_html += f'<div class="report-section-body">{body}</div>'

            # Conclusion
            conclusion_val = data.get("conclusion", "").strip()
            conclusion_html = ""
            if conclusion_val:
                conclusion_html = (
                    f'<div class="report-conclusion">'
                    f'<div class="report-conclusion-title">结论与建议</div>'
                    f'<div class="report-conclusion-text">{conclusion_val}</div>'
                    f'</div>'
                )

            # Footer
            footer_val = data.get("footer_text", "").strip()
            footer_html = ""
            if footer_val:
                footer_html = f'<div class="report-footer">{footer_val}</div>'

            html = REPORT_CSS.format(
                title=data.get("title", ""),
                subtitle=data.get("subtitle", ""),
                meta_text=meta_text,
                summary_html=summary_html,
                sections_html=sections_html,
                conclusion_html=conclusion_html,
                footer_html=footer_html,
                accent_color=accent_color,
                bg_color=bg_color,
                bg_gradient=bg_gradient,
                header_bg_css=header_bg_css,
                header_text_color=header_text_color,
                subtitle_color=subtitle_color,
                text_color=text_color,
                text_secondary_color=text_secondary_color,
            )
            self.previewView.setHtml(html)

        elif template_id == "contract":
            styles = self._get_current_style_values()
            accent_color = styles["theme_color"]
            bg_style = styles["bg_style"]
            bg_custom_color = styles["bg_custom_color"]
            bg_texture = styles["bg_texture"]
            header_style = styles.get("header_style", "bar")
            text_color = styles["text_color"]
            text_secondary_color = styles["text_secondary_color"]

            bg_color, bg_gradient, texture_css = _get_bg_css(bg_style, bg_custom_color, bg_texture, text_color)

            # Header decoration
            header_bg_css = ""
            header_text_color = accent_color
            if header_style == "bar":
                header_bg_css = f"border-bottom: 3px solid {accent_color}; padding-bottom: 12px;"
            elif header_style == "color_block":
                header_bg_css = f"background: linear-gradient(135deg, {accent_color}, {accent_color}dd); color: #fff; border-radius: 6px; margin: 30px 50px 0 50px; padding: 24px 30px;"
                header_text_color = "#FFFFFF"
            elif header_style == "none":
                header_bg_css = ""

            # Contract number
            contract_no = data.get("contract_no", "").strip()
            contract_no_html = f'<div class="contract-no">合同编号：{contract_no}</div>' if contract_no else ""

            # Terms: each line is one term
            terms_val = data.get("terms", "").strip()
            terms_html = ""
            if terms_val:
                for line in terms_val.split("\n"):
                    line = line.strip()
                    if line:
                        terms_html += f'<div class="contract-term">{line}</div>'

            # Amount
            amount_val = data.get("amount", "").strip()
            amount_html = ""
            if amount_val:
                amount_html = f'<div class="contract-amount">合同金额：{amount_val}</div>'

            # Remark
            remark_val = data.get("remark", "").strip()
            remark_html = ""
            if remark_val:
                remark_html = f'<div class="contract-remark">{remark_val}</div>'

            # Date
            date_val = data.get("date", "").strip()

            html = CONTRACT_CSS.format(
                title=data.get("title", ""),
                contract_no_html=contract_no_html,
                party_a=data.get("party_a", ""),
                party_a_addr=data.get("party_a_addr", ""),
                party_b=data.get("party_b", ""),
                party_b_addr=data.get("party_b_addr", ""),
                terms_html=terms_html,
                amount_html=amount_html,
                remark_html=remark_html,
                date=date_val,
                accent_color=accent_color,
                bg_color=bg_color,
                bg_gradient=bg_gradient,
                header_bg_css=header_bg_css,
                header_text_color=header_text_color,
                text_color=text_color,
                text_secondary_color=text_secondary_color,
            )
            self.previewView.setHtml(html)

        elif template_id == "invoice":
            styles = self._get_current_style_values()
            accent_color = styles["theme_color"]
            bg_style = styles["bg_style"]
            bg_custom_color = styles["bg_custom_color"]
            bg_texture = styles["bg_texture"]
            text_color = styles["text_color"]
            text_secondary_color = styles["text_secondary_color"]

            bg_color, bg_gradient, texture_css = _get_bg_css(bg_style, bg_custom_color, bg_texture, text_color)

            # Get border_style from style_widgets (not in _get_current_style_values by default)
            border_style_val = "double"
            border_group = self.style_widgets.get("border_style")
            if border_group:
                for btn in border_group.buttons():
                    if btn.isChecked():
                        border_style_val = btn.property("border_style_value")
                        break

            # Border CSS
            outer_border_css = ""
            inner_border_css = ""
            single_border_css = ""
            border_html = ""
            if border_style_val == "double":
                outer_border_css = f"top:8mm; left:8mm; right:8mm; bottom:8mm; border: 1.5px solid {accent_color};"
                inner_border_css = f"top:11mm; left:11mm; right:11mm; bottom:11mm; border: 0.5px solid {accent_color};"
                border_html = '<div class="invoice-outer-border"></div><div class="invoice-inner-border"></div>'
            elif border_style_val == "single":
                single_border_css = f"top:10mm; left:10mm; right:10mm; bottom:10mm; border: 1px solid {accent_color};"
                border_html = '<div class="invoice-single-border"></div>'

            # Invoice no + date
            invoice_no = data.get("invoice_no", "").strip()
            date_val = data.get("date", "").strip()
            invoice_no_html = ""
            if invoice_no:
                invoice_no_html += f'<span>编号：{invoice_no}</span>'
            if date_val:
                invoice_no_html += f'<span>日期：{date_val}</span>'

            # Items: from table (list of dicts)
            items_rows = ""
            items_val = data.get("items", [])
            if isinstance(items_val, list):
                for item in items_val:
                    if isinstance(item, dict):
                        items_rows += f'<tr><td>{item.get("name", "")}</td><td>{item.get("qty", "")}</td><td>{item.get("price", "")}</td></tr>\n'

            # Total
            total_val = data.get("total_amount", "").strip()
            total_html = ""
            if total_val:
                total_html = f'<div class="invoice-total">合计：{total_val}</div>'

            # Remark
            remark_val = data.get("remark", "").strip()
            remark_html = ""
            if remark_val:
                remark_html = f'<div class="invoice-remark"><span class="invoice-remark-label">备注：</span>{remark_val}</div>'

            html = INVOICE_CSS.format(
                title=data.get("title", "发票"),
                invoice_no_html=invoice_no_html,
                seller=data.get("seller", ""),
                seller_addr=data.get("seller_addr", ""),
                buyer=data.get("buyer", ""),
                buyer_addr=data.get("buyer_addr", ""),
                items_rows=items_rows,
                total_html=total_html,
                remark_html=remark_html,
                accent_color=accent_color,
                bg_color=bg_color,
                bg_gradient=bg_gradient,
                outer_border_css=outer_border_css,
                inner_border_css=inner_border_css,
                single_border_css=single_border_css,
                border_html=border_html,
                text_color=text_color,
                text_secondary_color=text_secondary_color,
            )
            self.previewView.setHtml(html)

        else:
            self.previewView.setHtml(
                f'<html><body style="font-family: sans-serif; padding: 40px; color: {t("text_secondary")}; text-align: center;">'
                f'<div style="font-size: 48px; margin-bottom: 16px;">📄</div>'
                f'<div style="font-size: 14px;">「{self.template_data.get("name", "模板")}」预览功能开发中</div>'
                f'</body></html>'
            )

    def _build_default_filename(self, data: dict) -> str:
        """根据模板类型和表单数据构建有意义的默认文件名

        Args:
            data: 已收集的表单数据

        Returns:
            默认文件名（不含路径，含 .pdf 后缀）
        """
        import re

        template_id = self.template_data.get("id", "")
        template_name = self.template_data.get("name", "模板")

        # 根据模板类型从表单数据中提取关键信息
        meaningful_part = ""

        if template_id == "business_card":
            # 名片：用姓名或公司名
            name = data.get("name_cn", "").strip()
            company = data.get("company", "").strip()
            if name:
                meaningful_part = name
            elif company:
                meaningful_part = company

        elif template_id == "contract":
            # 合同：用合同标题或甲乙方
            title = data.get("title", "").strip()
            party_a = data.get("party_a", "").strip()
            party_b = data.get("party_b", "").strip()
            if title:
                meaningful_part = title
            elif party_a and party_b:
                meaningful_part = f"{party_a}-{party_b}"

        elif template_id == "invoice":
            # 发票：用票据标题或编号
            title = data.get("title", "").strip()
            invoice_no = data.get("invoice_no", "").strip()
            if invoice_no:
                meaningful_part = invoice_no
            elif title:
                meaningful_part = title

        elif template_id == "notice":
            # 公告：用公告标题
            title = data.get("title", "").strip()
            if title:
                meaningful_part = title

        elif template_id == "report":
            # 报告：用报告标题
            title = data.get("title", "").strip()
            if title:
                meaningful_part = title

        elif template_id == "product_spec":
            # 产品规格：用产品名称
            product_name = data.get("product_name", "").strip()
            if product_name:
                meaningful_part = product_name

        if not meaningful_part:
            meaningful_part = template_name

        # 清理文件名：移除非法字符，限制长度
        meaningful_part = re.sub(r'[\\/:*?"<>|]', '', meaningful_part).strip()
        if not meaningful_part:
            meaningful_part = template_name

        if len(meaningful_part) > 60:
            meaningful_part = meaningful_part[:60]

        return f"{meaningful_part}.pdf"

    # ── PDF 生成 ──────────────────────────────────────────────
    def _generate_pdf(self):
        if not self.template_data:
            return

        data = {}
        for field in self.template_data.get("fields", []):
            key = field.get("key", "")
            required = field.get("required", False)
            widget = self.field_widgets.get(key)

            if widget is None:
                continue

            if isinstance(widget, QTextEdit):
                value = widget.toPlainText().strip()
            elif isinstance(widget, QTableWidget):
                if key == "items":
                    value = self.get_invoice_items()
                else:
                    columns = field.get("columns", [])
                    rows_data = []
                    for row in range(widget.rowCount()):
                        row_data = {}
                        row_has_data = False
                        for col, col_def in enumerate(columns):
                            col_key = col_def.get("key", f"col{col}")
                            item = widget.item(row, col)
                            cell_value = item.text().strip() if item else ""
                            row_data[col_key] = cell_value
                            if cell_value:
                                row_has_data = True
                        if row_has_data:
                            rows_data.append(row_data)
                    value = rows_data
            else:
                value = widget.text().strip()

            data[key] = value

            if required and not value:
                label_text = field.get("label", key)
                QMessageBox.warning(
                    self, "必填项未填写",
                    f"请填写必填项：{label_text}"
                )
                widget.setFocus()
                return

        # ── TPL-06：弹出保存文件对话框（支持自定义文件名） ──
        # 构建有意义的默认文件名（基于表单数据）
        default_name = self._build_default_filename(data)

        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存 PDF",
            os.path.join(os.path.expanduser("~/Desktop"), default_name),
            "PDF 文件 (*.pdf)"
        )
        if not save_path:
            return

        # 确保文件名以 .pdf 结尾
        if not save_path.lower().endswith(".pdf"):
            save_path += ".pdf"
        output_path = save_path

        template_id = self.template_data.get("id", "")
        try:
            from src.common.template_renderer import (render_business_card, render_notice, render_product_spec,
                                                       render_report, render_contract, render_invoice)

            if template_id == "business_card":
                # ── RC1 一致性修复：导出 = 当前编辑状态 ──
                # 同一份 RenderContext 同时驱动预览和导出
                sides_config = self.template_data.get("sides", [])
                if len(sides_config) >= 2:
                    render_sides = ["front", "back"]
                else:
                    render_sides = ["front"]

                # 双面导出：每面用同一份样式/资源，但字段按 side 分别序列化
                import tempfile, os as _os
                from src.common.template_renderer import make_render_context

                if len(render_sides) == 1:
                    # 单面：直接用当前侧
                    ctx = self._serialize_render_context(side=render_sides[0])
                    result_path = ctx.render_to_pdf(output_path)
                else:
                    # 双面：先渲染 front，复制临时文件，再 render back，merge
                    # 简化：依次生成两页并合并
                    front_ctx = self._serialize_render_context(side="front")
                    back_ctx = self._serialize_render_context(side="back")

                    # 临时文件分别输出 front/back
                    tmp_dir = tempfile.mkdtemp(prefix="PDflow_Biz_")
                    front_pdf = _os.path.join(tmp_dir, "front.pdf")
                    back_pdf = _os.path.join(tmp_dir, "back.pdf")
                    try:
                        front_ctx.render_to_pdf(front_pdf)
                        back_ctx.render_to_pdf(back_pdf)
                        # 合并 PDF
                        import fitz
                        merged = fitz.open()
                        for p in [front_pdf, back_pdf]:
                            d = fitz.open(p)
                            merged.insert_pdf(d)
                            d.close()
                        merged.save(output_path)
                        merged.close()
                        result_path = output_path
                    finally:
                        try:
                            _os.remove(front_pdf)
                            _os.remove(back_pdf)
                            _os.rmdir(tmp_dir)
                        except Exception:
                            pass

            elif template_id == "notice":
                image_path = self._uploaded_paths.get("header_image")
                style_opts = self._get_current_style_values()
                # 修复：确保上传的图片路径正确传递
                result_path = render_notice(
                    output_path, data,
                    image_path=image_path,
                    style=style_opts
                )
            elif template_id == "product_spec":
                image_path = self._uploaded_paths.get("product_image")
                style_opts = self._get_current_style_values()
                # 修复：确保上传的产品图片路径正确传递
                result_path = render_product_spec(
                    output_path, data,
                    image_path=image_path,
                    style=style_opts
                )
            elif template_id == "report":
                style_opts = self._get_current_style_values()
                result_path = render_report(
                    output_path, data,
                    style=style_opts
                )
            elif template_id == "contract":
                style_opts = self._get_current_style_values()
                result_path = render_contract(
                    output_path, data,
                    style=style_opts
                )
            elif template_id == "invoice":
                style_opts = self._get_current_style_values()
                result_path = render_invoice(
                    output_path, data,
                    style=style_opts
                )
            else:
                QMessageBox.warning(
                    self, "暂不支持",
                    f"模板「{template_id}」的 PDF 渲染尚未实现"
                )
                return

            QMessageBox.information(
                self, "生成成功",
                f"PDF 已生成：\n{result_path}"
            )
            self._open_pdf(result_path)

        except ImportError:
            QMessageBox.critical(
                self, "模块缺失",
                "未找到 template_renderer 模块，请确认 src/common/template_renderer.py 存在"
            )
        except Exception as e:
            QMessageBox.critical(self, "生成失败", str(e))

    def _open_pdf(self, path: str):
        try:
            abs_path = os.path.abspath(path)
            if not os.path.exists(abs_path):
                QMessageBox.warning(self, "文件不存在", f"找不到文件:\n{abs_path}")
                return
            if not abs_path.lower().endswith((".pdf", ".png", ".jpg", ".jpeg")):
                QMessageBox.warning(self, "不支持的文件", "仅可打开 PDF 或图片文件")
                return
            os.startfile(abs_path)  # nosec B606
        except Exception as e:
            QMessageBox.warning(self, "打开失败", f"无法打开文件:\n{e}")

    # ── 重置表单 ──────────────────────────────────────────────
    def _reset_form(self):
        # 重置表单字段值
        for field in self.template_data.get("fields", []):
            key = field.get("key", "")
            widget = self.field_widgets.get(key)
            if widget is None:
                continue
            if isinstance(widget, QTextEdit):
                widget.clear()
            elif isinstance(widget, QTableWidget):
                # 重置表格为初始2行
                widget.setRowCount(2)
                for row in range(widget.rowCount()):
                    for col in range(widget.columnCount()):
                        widget.setItem(row, col, QTableWidgetItem(""))
                widget.resizeRowsToContents()
            else:
                widget.clear()

        # 修复：重置样式选项到默认值
        self._bg_custom_color = ""
        self._bg_texture = "none"
        self._bg_image_path = None
        self._bg_image_opacity = 50
        self._text_color = "#2C3E50"
        self._text_secondary_color = "#7F8C8D"
        self._font_style = "formal"
        self._header_style = "bar"
        self._table_style = "striped"

        # 重置背景颜色选择器
        if hasattr(self, 'bgColorBtn'):
            self.bgColorBtn.setStyleSheet(
                f"QPushButton {{ background-color: {t('bg_secondary')}; border: 1px solid {t('border_secondary')}; border-radius: 4px; }}"
                f"QPushButton:hover {{ border: 1px solid {t('accent')}; }}"
            )
        if hasattr(self, 'bgColorHex'):
            self.bgColorHex.blockSignals(True)
            self.bgColorHex.clear()
            self.bgColorHex.blockSignals(False)

        # 重置背景图片
        if hasattr(self, 'bgImageLabel'):
            self.bgImageLabel.setText("未选择")
            self.bgImageLabel.setStyleSheet(f"color: {t('text_muted')}; font-size: 11px; background-color: transparent;")

        # 重置背景透明度滑块
        if hasattr(self, 'bgOpacitySlider'):
            self.bgOpacitySlider.setValue(50)
        if hasattr(self, 'bgOpacityVal'):
            self.bgOpacityVal.setText("50%")

        # 重置字体颜色选择器
        if hasattr(self, 'textColorBtn'):
            self.textColorBtn.setStyleSheet(
                f"QPushButton {{ background-color: #2C3E50; border: 1px solid {t('border_secondary')}; border-radius: 4px; }}"
                f"QPushButton:hover {{ border: 1px solid {t('accent')}; }}"
            )
        if hasattr(self, 'textColorHex'):
            self.textColorHex.blockSignals(True)
            self.textColorHex.setText("#2C3E50")
            self.textColorHex.blockSignals(False)

        if hasattr(self, 'secondaryColorBtn'):
            self.secondaryColorBtn.setStyleSheet(
                f"QPushButton {{ background-color: #7F8C8D; border: 1px solid {t('border_secondary')}; border-radius: 4px; }}"
                f"QPushButton:hover {{ border: 1px solid {t('accent')}; }}"
            )
        if hasattr(self, 'secondaryColorHex'):
            self.secondaryColorHex.blockSignals(True)
            self.secondaryColorHex.setText("#7F8C8D")
            self.secondaryColorHex.blockSignals(False)

        # 重置样式选项按钮到默认值
        for group_name, group in getattr(self, 'style_widgets', {}).items():
            if isinstance(group, QButtonGroup):
                for btn in group.buttons():
                    prop_keys = ["theme_value", "bar_value", "bg_value", "texture_value",
                                 "font_style_value", "header_style_value", "table_style_value"]
                    is_default = False
                    for prop_key in prop_keys:
                        val = btn.property(prop_key)
                        if val is not None:
                            if group_name == "theme_color" and val == "#4D7CFE":
                                is_default = True
                            elif group_name == "bar_position" and val == "left":
                                is_default = True
                            elif group_name == "bg_style" and val == "white":
                                is_default = True
                            elif group_name == "bg_texture" and val == "none":
                                is_default = True
                            elif group_name == "font_style" and val == "formal":
                                is_default = True
                            elif group_name == "header_style" and val == "bar":
                                is_default = True
                            elif group_name == "table_style" and val == "striped":
                                is_default = True
                            break
                    btn.setChecked(is_default)
                    self._style_radio_btn(btn, is_default)

        # 重置预设选择器
        if hasattr(self, '_preset_selector'):
            self._preset_selector.setCurrentIndex(0)

        self._update_preview()

    # ── 工具方法 ──────────────────────────────────────────────
    @staticmethod
    def _clear_layout(layout):
        if layout is None:
            return
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                TemplateEditorPage._clear_layout(item.layout())
