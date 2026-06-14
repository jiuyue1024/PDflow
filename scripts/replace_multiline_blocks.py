"""
第三轮：处理多行 setStyleSheet 块（多个连续字符串字面量）。
将块内所有含颜色字面量的字符串前缀加上 f。
"""
import re

PATH = r"F:\印流PDflow项目\pages\template_editor_page.py"

with open(PATH, "r", encoding="utf-8") as f:
    content = f.read()

# 颜色字面量
COLOR_RE = re.compile(r'#[0-9A-Fa-f]{6}|#[0-9A-Fa-f]{3}\b|rgba?\(.*?\)')

# 颜色 → token 映射
COLOR_TO_TOKEN = {
    "#8B8D98": "text_secondary",
    "#ECEDF0": "text_primary",
    "#1A1A22": "bg_secondary",
    "#1A1A24": "bg_secondary",
    "#1E1E28": "border_secondary",
    "#0A0A0F": "bg_tertiary",
    "#14141A": "bg_secondary",
    "#0B0E11": "bg_primary",
    "#0F0F14": "bg_primary",
    "#1E2330": "border_secondary",
    "#2A2A32": "bg_hover",
    "#2B3139": "border_primary",
    "#3D4450": "border_hover",
    "#16181D": "bg_disabled",
    "#6E6E73": "text_tertiary",
    "#4A4B56": "text_quaternary",
    "#5A5B66": "text_muted",
    "#1A1A1A": "text_primary",
    "#FFFFFF": "on_accent",
    "#FAFAFA": "bg_primary",
    "#F5F5F7": "bg_tertiary",
    "#F0F0F3": "bg_hover",
    "#E5E5EA": "border_primary",
    "#EEEEF0": "bg_quaternary",
    "#C7C7CC": "border_secondary",
    "#1D1D1F": "text_primary",
    "#8E8E93": "text_tertiary",
    "#AEAEB2": "text_quaternary",
    "#4D7CFE": "accent",
    "#3D6CF0": "accent_hover",
    "#2D5CD0": "accent_pressed",
    "#FF3B30": "error",
    "#E0352B": "error_hover",
    "#C02E25": "error_pressed",
    "rgba(77, 124, 254, 0.1)": "accent_subtle",
    "rgba(77, 124, 254, 0.2)": "accent_subtle_2",
}


def replace_in_string(s: str) -> str:
    """把字符串内的颜色字面量替换为 {t('xxx')}。"""
    for color, token in COLOR_TO_TOKEN.items():
        s = s.replace(color, "{t('" + token + "')}")
    return s


# 找到所有 setStyleSheet 调用块（含跨行）
# 匹配 .setStyleSheet( ... )，其中可能包含多个 "..." 字符串
# 用平衡括号匹配：手动实现

def find_setstylesheet_blocks(text):
    """返回 [(start, end, content)] 列表"""
    blocks = []
    pos = 0
    while True:
        idx = text.find('.setStyleSheet(', pos)
        if idx < 0:
            break
        # 找到匹配的 )
        # 跳过 .setStyleSheet(
        i = idx + len('.setStyleSheet(')
        depth = 1
        in_string = False
        string_char = None
        j = i
        while j < len(text) and depth > 0:
            c = text[j]
            if in_string:
                if c == '\\' and j + 1 < len(text):
                    j += 2
                    continue
                if c == string_char:
                    in_string = False
            else:
                if c in ('"', "'"):
                    in_string = True
                    string_char = c
                elif c == '(':
                    depth += 1
                elif c == ')':
                    depth -= 1
            j += 1
        blocks.append((idx, j, text[idx:j]))
        pos = j
    return blocks


blocks = find_setstylesheet_blocks(content)

new_content = content
offset = 0
modified_blocks = 0

for start, end, block in blocks:
    # 提取所有 "..." 字符串的内容
    # 模式: "..." 可能跨行
    str_pattern = re.compile(r'"((?:[^"\\]|\\.)*)"', re.DOTALL)

    def repl_str(m):
        body = m.group(1)
        new_body = replace_in_string(body)
        if new_body != body:
            return 'f"' + new_body + '"'
        return m.group(0)

    new_block = str_pattern.sub(repl_str, block)
    if new_block != block:
        modified_blocks += 1
        new_content = new_content[:start + offset] + new_block + new_content[end + offset:]
        offset += len(new_block) - len(block)

with open(PATH, "w", encoding="utf-8") as f:
    f.write(new_content)

print(f"修改 setStyleSheet 块: {modified_blocks} 处")
