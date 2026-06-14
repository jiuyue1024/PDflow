"""验证主题切换：浅色模式下按钮 checked 状态是浅蓝。"""
import sys
sys.path.insert(0, '.')

from src.common.theme import LIGHT_COLORS, DARK_COLORS


def main():
    print("=== 浅色模式按钮 checked 状态 ===")
    print(f"  背景: {LIGHT_COLORS['nav_checked_bg_qss']}")
    print(f"  图标: {LIGHT_COLORS['sidebar_icon_active']}")
    print(f"  文字: {LIGHT_COLORS['sidebar_text_active']}")

    print()
    print("=== 深色模式按钮 checked 状态 ===")
    print(f"  背景: {DARK_COLORS['nav_checked_bg_qss']}")
    print(f"  图标: {DARK_COLORS['sidebar_icon_active']}")
    print(f"  文字: {DARK_COLORS['sidebar_text_active']}")

    # 验证：浅色模式 checked 背景应该是浅蓝
    color = LIGHT_COLORS['nav_checked_bg_qss']
    assert color.startswith('#'), f"浅色 checked 背景应该是 hex 色值，实际: {color}"
    r = int(color[1:3], 16)
    g = int(color[3:5], 16)
    b = int(color[5:7], 16)
    print(f"\n  浅色 checked 背景 RGB: ({r}, {g}, {b})")
    # 浅蓝：蓝色 > 红色
    assert b > r, f"蓝色分量应该 > 红色分量，实际 b={b} r={r}"
    print("  [PASS] 浅色 checked 背景是浅蓝")

    # 验证：浅色文字是深色（不是浅色）
    text_color = LIGHT_COLORS['sidebar_text_active']
    tr = int(text_color[1:3], 16)
    tg = int(text_color[3:5], 16)
    tb = int(text_color[5:7], 16)
    assert tr < 100, f"浅色 checked 文字应该是深色，实际 RGB({tr}, {tg}, {tb})"
    print(f"  [PASS] 浅色 checked 文字是深色 RGB({tr}, {tg}, {tb})")

    print("\n[ALL PASS] 浅色模式按钮 checked 状态颜色正确")


if __name__ == "__main__":
    main()
