"""
批量替换 template_editor_page.py 中的硬编码颜色为 ThemeTokens。
仅处理 setStyleSheet 调用的字符串字面量。
"""
import re
import sys

PATH = r"F:\印流PDflow项目\pages\template_editor_page.py"

# 颜色 → token 映射（按长度从长到短，避免子串误匹配）
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


def transform_setstylesheet_block(content: str) -> tuple[str, int]:
    """匹配 setStyleSheet(\n    "..."\n) 多行字符串，转换为 f-string + token。"""
    # 匹配 setStyleSheet(\n   "...")  块
    # 字符串可能跨多行
    pattern = re.compile(
        r'(\.setStyleSheet\(\s*")((?:[^"\\]|\\.)*)("\s*\))',
        re.DOTALL
    )

    count = 0

    def replace_block(m: re.Match) -> str:
        nonlocal count
        prefix = m.group(1)  # .setStyleSheet( "
        body = m.group(2)    # string content
        suffix = m.group(3)  # " )
        # 转义反斜杠
        new_body = body
        has_token_already = "{t(" in new_body
        # 替换每个颜色
        for color, token in COLOR_TO_TOKEN.items():
            token_repr = "{t('" + token + "')}"
            new_body = new_body.replace(color, token_repr)
        if new_body != body:
            count += 1
        return prefix + new_body + suffix

    new_content = pattern.sub(replace_block, content)
    return new_content, count


def main():
    with open(PATH, "r", encoding="utf-8") as f:
        content = f.read()
    new_content, count = transform_setstylesheet_block(content)
    if new_content != content:
        with open(PATH, "w", encoding="utf-8") as f:
            f.write(new_content)
    print(f"替换 setStyleSheet 块: {count} 处")


if __name__ == "__main__":
    main()
