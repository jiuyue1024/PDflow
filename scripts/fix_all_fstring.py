"""
修复所有 f-string 中的 ff" 和 f''f' 等组合typo，并修复未加 f 前缀的字符串。
"""
import re

PATH = r"F:\印流PDflow项目\pages\template_editor_page.py"

with open(PATH, "r", encoding="utf-8") as f:
    content = f.read()

# 修复 ff" -> f"
content = re.sub(r'ff"', 'f"', content)
content = re.sub(r"ff'", "f'", content)

# 修复 "..." 在 setStyleSheet 上下文中含 {t(...)} 但缺少 f 前缀
# 模式: 行首空白 + "..." (含 {t(  但不是 f" 也不是 f')
lines = content.split('\n')
fixed = 0
new_lines = []
for line in lines:
    stripped = line.lstrip()
    # 处理 ff 残留（重复一次确保）
    line = line.replace('ff"', 'f"').replace("ff'", "f'")
    # 字符串字面量
    if (
        stripped.startswith('"')
        and not stripped.startswith('f"')
        and not stripped.startswith("f'")
        and '{t(' in stripped
    ):
        line = line.replace('"', 'f"', 1)
        fixed += 1
    new_lines.append(line)

with open(PATH, "w", encoding="utf-8") as f:
    f.write('\n'.join(new_lines))

print(f"修复 f-string 前缀: {fixed} 行")
