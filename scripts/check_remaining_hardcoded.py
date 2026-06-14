"""
检测 template_editor_page.py 中多行 setStyleSheet 块内是否仍含硬编码颜色。
"""
import re

PATH = r"F:\印流PDflow项目\pages\template_editor_page.py"

with open(PATH, "r", encoding="utf-8") as f:
    content = f.read()

# 找所有 setStyleSheet 多行块（含跨行字符串）
pattern = re.compile(
    r'\.setStyleSheet\(\s*"((?:[^"\\]|\\.)*)"\s*\)',
    re.DOTALL
)

hex_pat = re.compile(r'#[0-9A-Fa-f]{6}|#[0-9A-Fa-f]{3}\b|rgba?\(.*?\)')

remaining = []
for m in pattern.finditer(content):
    body = m.group(1)
    line_no = content[:m.start()].count('\n') + 1
    for h in hex_pat.finditer(body):
        remaining.append((line_no, h.group()))

print(f"剩余硬编码颜色（多行 setStyleSheet 块）: {len(remaining)} 处")
for ln, color in remaining[:30]:
    print(f"  L{ln}: {color}")
if len(remaining) > 30:
    print(f"  ... 还有 {len(remaining) - 30} 处")
