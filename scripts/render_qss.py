"""
生成 light.qss 和 dark.qss 预渲染文件。
从 global.qss.template 渲染并写入两个独立文件。
"""
import os
import sys

PROJECT_ROOT = r"F:\印流PDflow项目"
TEMPLATE_PATH = os.path.join(PROJECT_ROOT, "pages", "global.qss.template")
LIGHT_OUTPUT = os.path.join(PROJECT_ROOT, "pages", "light.qss")
DARK_OUTPUT = os.path.join(PROJECT_ROOT, "pages", "dark.qss")


def render(template: str, colors: dict) -> str:
    """填充 {{TOKEN}} → colors[token]"""
    out = template
    for token, value in colors.items():
        out = out.replace("{{" + token + "}}", value)
    return out


def main():
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template = f.read()

    # 导入色值
    sys.path.insert(0, PROJECT_ROOT)
    from src.common.theme import DARK_COLORS, LIGHT_COLORS

    # 渲染 dark
    dark_qss = render(template, DARK_COLORS)
    with open(DARK_OUTPUT, "w", encoding="utf-8") as f:
        f.write(dark_qss)
    print(f"✓ 生成 {DARK_OUTPUT} ({len(dark_qss)} 字符)")

    # 渲染 light
    light_qss = render(template, LIGHT_COLORS)
    with open(LIGHT_OUTPUT, "w", encoding="utf-8") as f:
        f.write(light_qss)
    print(f"✓ 生成 {LIGHT_OUTPUT} ({len(light_qss)} 字符)")


if __name__ == "__main__":
    main()
