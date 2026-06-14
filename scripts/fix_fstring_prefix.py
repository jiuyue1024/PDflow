"""
二次修复：把含 {t(...)} 的字符串字面量前缀加上 f，使其成为 f-string。
仅处理 setStyleSheet 调用相关的字符串。
"""
import re

PATH = r"F:\印流PDflow项目\pages\template_editor_page.py"

with open(PATH, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
fixed = 0
for line in lines:
    stripped = line.lstrip()
    # 仅修改以下模式的行：
    # 缩进 + "..."  (双引号字符串字面量)
    # 且字符串内容包含 {t(
    # 且行首不是 f"
    if (
        stripped.startswith('"')
        and not stripped.startswith('f"')
        and not stripped.startswith("f'")
        and "{t(" in stripped
    ):
        # 把首个 " 替换为 f"
        new_line = line.replace('"', 'f"', 1)
        new_lines.append(new_line)
        fixed += 1
    else:
        new_lines.append(line)

with open(PATH, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print(f"修复 f-string 前缀: {fixed} 行")
