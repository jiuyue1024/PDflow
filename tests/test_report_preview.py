# -*- coding: utf-8 -*-
"""
验证报告模板 HTML 预览生成是否正确
"""
import sys
import os
import re

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pages.template_editor_page import REPORT_CSS

# 模拟 _update_preview 中的数据处理逻辑
accent_color = "#1A5276"
bg_color = "#FFFFFF"
bg_gradient = "transparent"
header_bg_css = "background: linear-gradient(135deg, #1A5276, #1A5276dd); color: #fff;"
header_text_color = "#FFFFFF"
subtitle_color = "rgba(255,255,255,0.75)"
text_color = "#2C3E50"
text_secondary_color = "#7F8C8D"

data = {
    "title": "市场分析报告",
    "subtitle": "2026年第二季度",
    "author": "分析部",
    "date": "2026年6月",
    "summary": "本报告针对2026年第二季度市场情况进行分析，旨在为业务决策提供数据支持。",
    "sections": "## 1. 总体概况\n本季度市场总规模环比上升12%，同比上升18%。\n\n## 2. 细分表现\n华东区占比45%，华南区占比30%，其他区域合计25%。",
    "conclusion": "建议加大华东区投入，重点优化复购链路。",
    "footer_text": "机密文件 · 仅供内部使用"
}

# Meta text
meta_parts = []
if data.get("author"):
    meta_parts.append(f"作者：{data['author']}")
if data.get("date"):
    meta_parts.append(f"日期：{data['date']}")
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

# Sections
sections_val = data.get("sections", "").strip()
sections_html = ""
if sections_val:
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

out_path = os.path.join(os.path.dirname(__file__), "_report_test_output.html")
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html)
print(f"Report HTML written to: {out_path}")

# 检查关键 CSS class 是否存在
for keyword in ['report-title', 'report-subtitle', 'report-header', 'report-meta',
                'report-summary', 'report-section-heading', 'report-conclusion', 'report-footer']:
    assert keyword in html, f"Missing CSS class: {keyword}"
print("All CSS classes present. PASS")
