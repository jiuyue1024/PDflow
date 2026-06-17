# common/theme.py — 主题配色系统（V2.2）
# 全局主题色定义，支持 dark/light 模式，配置持久化到 app_config.json
# 配色严格对齐 DESIGN.md，双模式 token 一一对应
# V2.2: 新增 text_meta / border_hover / sidebar_text / sidebar_text_active 等 token，对齐 global.qss.template

import os, json
from src.common.paths import data_path

# ===================================================================
# DARK_COLORS — 深色模式（默认）
# 值精确匹配 global.qss 原始硬编码颜色
# ===================================================================
DARK_COLORS = {
    # --- 背景层 ---
    "bg":                "#0B0E11",      # 页面背景 — QWidget/QMainWindow/QDialog
    "nav_bg":           "#0F0F14",      # 侧边栏背景 — DESIGN.md
    "card_bg":          "#14141A",      # 卡片/容器背景 — DESIGN.md
    "card_glass":       "rgba(20, 20, 26, 0.72)",  # 毛玻璃效果
    "input_bg":         "#0A0A0F",      # 输入框背景 — DESIGN.md
    "hover_bg":         "#1A1A22",      # 卡片悬停态 — DESIGN.md
    "active_bg":        "#1E1E28",      # 选中态背景
    "title_bar_bg":     "#0B0E11",      # 自定义标题栏背景
    "tab_bg":           "#0A0A0F",      # 标签页内容区背景
    "disabled_bg":      "#14141A",      # 禁用态背景
    "menu_bg":          "#14141A",      # 下拉菜单背景
    "tooltip_bg":       "#14141A",      # 提示框背景
    "white":            "#FFFFFF",      # 纯白

    # ── 按钮状态（v3.0 新增：明确语义）──
    "bg_normal":        "#0B0E11",      # normal 态背景
    "bg_hover":         "#1A1A22",      # hover 态背景
    "bg_pressed":       "#1E1E28",      # pressed 态背景
    "bg_selected":      "#1E2330",      # selected/checked 态背景（区分 hover）
    "bg_focus":         "#1E1E28",      # focus 态背景
    "bg_disabled":      "#16181D",      # disabled 态背景
    "text_normal":      "#ECEDF0",      # normal 态文字
    "text_hover":       "#FFFFFF",      # hover 态文字
    "text_pressed":     "#FFFFFF",      # pressed 态文字
    "text_selected":    "#EAECEF",      # selected 态文字
    "text_disabled":    "#4A4B56",      # disabled 态文字
    "border_normal":    "#1E1E28",      # normal 态边框
    "border_hover":     "#3D4450",      # hover 态边框
    "border_pressed":   "#2B3139",      # pressed 态边框
    "border_selected":  "#4D7CFE",      # selected 态边框（主题色）
    "border_focus":     "#4D7CFE",      # focus 态边框
    "border_disabled":  "#1E1E28",      # disabled 态边框

    # --- 边框与分割线 ---
    "border":           "#1E1E28",      # 卡片边框 — DESIGN.md
    "border_light":     "#2B3139",      # 浅边框（设置页卡片）
    "border_hover":     "#3D4450",      # 边框悬停态（设置页控件）
    "separator":        "#1E1E28",      # 分割线颜色

    # --- 文字色 ---
    "text_main":        "#ECEDF0",      # 主要文字 — DESIGN.md
    "text_sub":         "#8B8D98",      # 次要文字 — DESIGN.md
    "text_muted":       "#4A4B56",      # 禁用/占位文字 — DESIGN.md
    "text_meta":        "#5E6673",      # 元信息文字（设置页节标题）
    "placeholder_text": "#6A6B78",      # 输入框占位符文字
    "card_title":       "#EAECEF",      # 卡片标题文字
    "card_desc":        "#8B8D98",      # 卡片描述文字

    # --- 主题色与语义色 ---
    "primary":          "#4D7CFE",      # 主题色（蓝）— DESIGN.md
    "primary_hover":    "#3D6CF0",      # 主题色悬停态
    "primary_pressed":  "#2D5CD0",      # 主题色按下态
    "primary_pressed_alt": "#3560E0",   # generateBtn 按下态
    "primary_light":    "rgba(77, 124, 254, 0.10)",  # 待废弃，兼容旧代码
    "success":          "#34C759",      # 成功绿 — DESIGN.md
    "warning":          "#FF9500",      # 警告橙 — DESIGN.md
    "error":            "#FF3B30",      # 错误红 — DESIGN.md
    "error_hover":      "#E0352B",      # 错误悬停
    "error_pressed":    "#C02E25",      # 错误按下
    "status_green":     "#34C759",      # 状态栏绿色

    # --- 导航侧边栏 ---
    "sidebar_icon":         "#848E9C",  # 导航图标默认色
    "sidebar_icon_active":  "#4D7CFE",  # 导航图标选中色
    "sidebar_text":         "#848E9C",  # 侧边栏按钮文字色
    "sidebar_text_active":  "#EAECEF",  # 侧边栏按钮选中文字色
    "nav_hover":        "rgba(255, 255, 255, 0.03)",  # 侧边栏悬停背景 (float alpha)
    "nav_checked_bg":   "rgba(77, 124, 254, 0.10)",   # 侧边栏选中背景 (float alpha)

    # --- 按钮 rgba 透明度层 ---
    "primary_light_10": "rgba(77, 124, 254, 0.1)",   # 10% 主题色 (浮点数)
    "primary_light_12": "rgba(77, 124, 254, 0.12)",  # 12% 主题色
    "primary_light_20": "rgba(77, 124, 254, 0.2)",   # 20% 主题色
    "nav_btn_hover_bg": "rgba(77, 124, 254, 0.08)",  # 导航按钮悬停

    # --- 语义色透明度层 ---
    "success_light_15": "rgba(52, 199, 89, 0.15)",   # 成功绿 15%
    "warning_light_15": "rgba(255, 149, 0, 0.15)",   # 警告橙 15%
    "error_light_15":   "rgba(255, 59, 48, 0.15)",   # 错误红 15%

    # --- QSS 特定格式 (整数 alpha 0-255) ---
    "nav_checked_bg_qss": "rgba(77, 124, 254, 10)",      # 侧边栏选中 bg (10/255)
    "nav_hover_qss":      "rgba(255, 255, 255, 6)",      # 侧边栏悬停 (6/255)
    "white_8_qss":        "rgba(255, 255, 255, 8)",      # 8/255 白
    "white_13_qss":       "rgba(255, 255, 255, 13)",     # 13/255 白
    "white_15_qss":       "rgba(255, 255, 255, 15)",     # 15/255 白
    "recent_bg_qss":      "rgba(20, 22, 28, 166)",       # 最近文件容器 bg
    "func_card_bg_qss":   "rgba(16, 18, 24, 184)",       # 功能卡片 bg
    "func_card_hover_qss": "rgba(30, 34, 40, 204)",      # 功能卡片悬停
    "func_card_border_hover_qss": "rgba(77, 124, 254, 64)", # 功能卡片悬停边框
    "disabled_bg_qss":    "#2B3139",                      # generateBtn 禁用 bg
    "preview_bg":         "#2A2A32",                      # 预览视图背景

    # --- 渐变 (QSS 整数 alpha) ---
    "gradient_start_qss":  "rgba(77,124,254,31)",         # 图标容器渐变起点
    "gradient_end_qss":    "rgba(77,124,254,10)",         # 图标容器渐变终点
    "gradient_border_qss": "rgba(77,124,254,26)",         # 图标容器边框

    # --- PDF 图标 (QSS 整数 alpha) ---
    "pdf_icon_red_bg_qss":    "rgba(255, 59, 48, 8)",     # PDF 图标红色 bg
    "pdf_icon_red_border_qss":"rgba(255, 59, 48, 10)",    # PDF 图标红色边框
    "pdf_icon_blue_bg_qss":   "rgba(77, 124, 254, 8)",    # PDF 图标蓝色 bg
    "pdf_icon_blue_border_qss":"rgba(77, 124, 254, 10)",  # PDF 图标蓝色边框

    # --- 组件色 ---
    "scrollbar_bg":     "#1E1E28",      # 滚动条滑块
    "scrollbar_hover":  "#4A4B56",      # 滚动条悬停
    "progress_bg":      "#1E1E28",      # 进度条背景
    "badge_bg":         "rgba(77, 124, 254, 0.15)",  # 徽章背景
    "card_border_hover": "#4D7CFE",     # 卡片悬停边框

    # --- 阴影 ---
    "shadow_sm":        "0 2px 8px rgba(0,0,0,0.15)",   # 悬浮层阴影 — DESIGN.md
    "shadow_md":        "0 8px 32px rgba(0,0,0,0.25)",  # 模态层阴影 — DESIGN.md
}

# ===================================================================
# LIGHT_COLORS — 浅色模式
# 与 DARK_COLORS token 一一对应，配色对齐 DESIGN.md 浅色模式色值
# ===================================================================
LIGHT_COLORS = {
    # --- 背景层 ---
    "bg":                "#F5F5F7",      # 页面背景 — DESIGN.md
    "nav_bg":           "#EEEEF0",      # 侧边栏背景 — DESIGN.md
    "card_bg":          "#FFFFFF",      # 卡片/容器背景 — DESIGN.md
    "card_glass":       "rgba(255, 255, 255, 0.72)",  # 毛玻璃效果
    "input_bg":         "#FFFFFF",      # 输入框背景 — DESIGN.md
    "hover_bg":         "#EEEEF0",      # 卡片悬停态
    "active_bg":        "#E5E5EA",      # 选中态背景
    "title_bar_bg":     "#F5F5F7",      # 自定义标题栏背景
    "tab_bg":           "#F5F5F7",      # 标签页内容区背景
    "disabled_bg":      "#F2F2F5",      # 禁用态背景
    "menu_bg":          "#FFFFFF",      # 下拉菜单背景
    "tooltip_bg":       "#FFFFFF",      # 提示框背景
    "white":            "#FFFFFF",      # 纯白

    # ── 按钮状态（v3.0 新增：明确语义）──
    # 浅色模式关键修复：selected/checked 态背景不能太深，
    # 否则会"点击后变深色"
    "bg_normal":        "#F5F5F7",      # normal 态背景（与页面背景同）
    "bg_hover":         "#EEEEF0",      # hover 态背景（浅灰）
    "bg_pressed":       "#E5E5EA",      # pressed 态背景（中灰）
    "bg_selected":      "#DDE5FF",      # selected/checked 态背景（主题色 15% 浅）
    "bg_focus":         "#FFFFFF",      # focus 态背景
    "bg_disabled":      "#F2F2F5",      # disabled 态背景
    "text_normal":      "#1D1D1F",      # normal 态文字（深色）
    "text_hover":       "#1D1D1F",      # hover 态文字（深色）
    "text_pressed":     "#1D1D1F",      # pressed 态文字（深色）
    "text_selected":    "#4D7CFE",      # selected 态文字（主题色）
    "text_disabled":    "#AEAEB2",      # disabled 态文字
    "border_normal":    "#E5E5EA",      # normal 态边框
    "border_hover":     "#4D7CFE",      # hover 态边框（主题色）
    "border_pressed":   "#2D5CD0",      # pressed 态边框（深主题色）
    "border_selected":  "#4D7CFE",      # selected 态边框（主题色）
    "border_focus":     "#4D7CFE",      # focus 态边框
    "border_disabled":  "#E5E5EA",      # disabled 态边框

    # --- 边框与分割线 ---
    "border":           "#E5E5EA",      # 卡片边框 — DESIGN.md
    "border_light":     "#D1D1D6",      # 浅边框（设置页卡片）
    "border_hover":     "#C7C7CC",      # 边框悬停态（设置页控件）
    "separator":        "#D1D1D6",      # 分割线颜色

    # --- 文字色 ---
    "text_main":        "#1D1D1F",      # 主要文字 — DESIGN.md
    "text_sub":         "#6E6E73",      # 次要文字 — DESIGN.md
    "text_muted":       "#8B8D98",      # 禁用/占位文字
    "text_meta":        "#8B8D98",      # 元信息文字（设置页节标题）
    "placeholder_text": "#AEAEB2",      # 输入框占位符文字
    "card_title":       "#1D1D1F",      # 卡片标题文字
    "card_desc":        "#6E6E73",      # 卡片描述文字

    # --- 主题色与语义色 ---
    "primary":          "#4D7CFE",      # 主题色（蓝）— DESIGN.md（与深色模式统一）
    "primary_hover":    "#3D6CF0",      # 主题色悬停态
    "primary_pressed":  "#2D5CD0",      # 主题色按下态
    "primary_pressed_alt": "#3560E0",   # generateBtn 按下态
    "primary_light":    "rgba(77, 124, 254, 0.10)",  # 待废弃，兼容旧代码
    "success":          "#34C759",      # 成功绿（与深色模式统一）
    "warning":          "#FF9500",      # 警告橙（与深色模式统一）
    "error":            "#FF3B30",      # 错误红（与深色模式统一）
    "error_hover":      "#E0352B",      # 错误悬停
    "error_pressed":    "#C02E25",      # 错误按下
    "status_green":     "#34C759",      # 状态栏绿色

    # --- 导航侧边栏 ---
    "sidebar_icon":         "#6E6E73",  # 导航图标默认色
    "sidebar_icon_active":  "#4D7CFE",  # 导航图标选中色
    "sidebar_text":         "#6E6E73",  # 侧边栏按钮文字色
    "sidebar_text_active":  "#1D1D1F",  # 侧边栏按钮选中文字色
    "nav_hover":        "rgba(0, 0, 0, 0.04)",  # 侧边栏悬停背景 (float alpha)
    "nav_checked_bg":   "rgba(77, 124, 254, 0.08)",   # 侧边栏选中背景 (float alpha)

    # --- 按钮 rgba 透明度层 ---
    "primary_light_10": "rgba(77, 124, 254, 0.1)",   # 10% 主题色 (浮点数)
    "primary_light_12": "rgba(77, 124, 254, 0.12)",  # 12% 主题色
    "primary_light_20": "rgba(77, 124, 254, 0.2)",   # 20% 主题色
    "nav_btn_hover_bg": "rgba(77, 124, 254, 0.08)",  # 导航按钮悬停

    # --- 语义色透明度层 ---
    "success_light_15": "rgba(52, 199, 89, 0.15)",   # 成功绿 15%
    "warning_light_15": "rgba(255, 149, 0, 0.15)",   # 警告橙 15%
    "error_light_15":   "rgba(255, 59, 48, 0.15)",   # 错误红 15%

    # --- QSS 特定格式 (整数 alpha 0-255) ---
    "nav_checked_bg_qss": "#DDE5FF",          # 侧边栏选中 — 主题色 15% 浅色（修复点击变深色）
    "nav_hover_qss":      "#EEEEF0",          # 侧边栏悬停 — 浅灰
    "white_8_qss":        "#E5E5EA",          # 浅色 8% 等效（边线）
    "white_13_qss":       "rgba(0, 0, 0, 8)",            # 8/255 黑 (替换13/255白)
    "white_15_qss":       "rgba(0, 0, 0, 10)",           # 10/255 黑 (替换15/255白)
    "recent_bg_qss":      "rgba(255, 255, 255, 200)",    # 最近文件容器 bg (白底)
    "func_card_bg_qss":   "rgba(255, 255, 255, 230)",    # 功能卡片 bg (白底)
    "func_card_hover_qss": "rgba(245, 245, 247, 230)",   # 功能卡片悬停 (浅灰)
    "func_card_border_hover_qss": "rgba(77, 124, 254, 64)", # 功能卡片悬停边框
    "disabled_bg_qss":    "#E5E5EA",                      # generateBtn 禁用 bg
    "preview_bg":         "#F0F0F2",                      # 预览视图背景

    # --- 渐变 (QSS 整数 alpha) ---
    "gradient_start_qss":  "rgba(77,124,254,15)",         # 图标容器渐变起点 (减淡)
    "gradient_end_qss":    "rgba(77,124,254,5)",          # 图标容器渐变终点 (减淡)
    "gradient_border_qss": "rgba(77,124,254,13)",         # 图标容器边框 (减淡)

    # --- PDF 图标 (QSS 整数 alpha) ---
    "pdf_icon_red_bg_qss":    "rgba(255, 59, 48, 5)",     # PDF 图标红色 bg
    "pdf_icon_red_border_qss":"rgba(255, 59, 48, 8)",     # PDF 图标红色边框
    "pdf_icon_blue_bg_qss":   "rgba(77, 124, 254, 5)",    # PDF 图标蓝色 bg
    "pdf_icon_blue_border_qss":"rgba(77, 124, 254, 8)",   # PDF 图标蓝色边框

    # --- 组件色 ---
    "scrollbar_bg":     "#D1D1D6",      # 滚动条滑块
    "scrollbar_hover":  "#AEAEB2",      # 滚动条悬停
    "progress_bg":      "#E5E5EA",      # 进度条背景
    "badge_bg":         "rgba(77, 124, 254, 0.10)",  # 徽章背景
    "card_border_hover": "#4D7CFE",     # 卡片悬停边框

    # --- 阴影（浅色模式阴影减淡）---
    "shadow_sm":        "0 2px 8px rgba(0,0,0,0.04)",  # 悬浮层阴影
    "shadow_md":        "0 8px 32px rgba(0,0,0,0.06)", # 模态层阴影
}


CONFIG_FILE = data_path("app_config.json")


def _load_theme():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f).get("theme", "dark")
    except Exception as e:
        print(f"[theme] 读取失败: {e}")
    return "dark"


def get_colors(theme=None):
    if theme is None:
        theme = _load_theme()
    return DARK_COLORS if theme == "dark" else LIGHT_COLORS


def set_theme(theme: str):
    try:
        cfg = {}
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        cfg["theme"] = theme
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[theme] 保存失败: {e}")


def get_current_theme():
    return _load_theme()
