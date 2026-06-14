# -*- coding: utf-8 -*-
"""
验证合同模板 HTML 预览生成是否正确
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pages.template_editor_page import CONTRACT_CSS

# 模拟 _update_preview 中的数据处理逻辑
accent_color = "#2C3E6B"
bg_color = "#FFFFFF"
bg_gradient = "transparent"
header_bg_css = "border-bottom: 3px solid #2C3E6B; padding-bottom: 12px;"
header_text_color = "#2C3E6B"
text_color = "#2C3E50"
text_secondary_color = "#7F8C8D"

data = {
    "title": "服务合同",
    "contract_no": "HT-2026-001",
    "party_a": "示例科技有限公司",
    "party_a_addr": "北京市朝阳区xx路1号",
    "party_b": "客户企业有限公司",
    "party_b_addr": "上海市浦东新区xx路2号",
    "date": "2026年6月3日",
    "terms": "第一条  双方应严格遵守本合同约定。\n第二条  服务内容详见附件A。\n第三条  付款方式：合同签订后7日内支付50%预付款。\n第五条  因履行本合同发生的争议，提交北京仲裁委员会仲裁。",
    "amount": "¥100,000.00",
    "remark": "本合同自双方签字盖章之日起生效。"
}

# Contract number
contract_no = data.get("contract_no", "").strip()
contract_no_html = f'<div class="contract-no">合同编号：{contract_no}</div>' if contract_no else ""

# Terms
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

out_path = os.path.join(os.path.dirname(__file__), "_contract_test_output.html")
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html)
print(f"Contract HTML written to: {out_path}")

# 检查关键 CSS class 是否存在
for keyword in ['contract-title', 'contract-header', 'contract-no', 'contract-parties',
                'party-row', 'contract-terms', 'contract-amount', 'contract-sign', 'contract-date']:
    assert keyword in html, f"Missing CSS class: {keyword}"
print("All CSS classes present. PASS")
