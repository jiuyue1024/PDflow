"""
印流PDflow 主题 Token 统一体系
所有 UI 颜色必须通过 ThemeTokens 读取，禁止硬编码。

Token 分层：
- 基础层：bg_primary / bg_secondary / bg_tertiary (背景)
- 文字层：text_primary / text_secondary / text_tertiary (文字)
- 边框层：border_primary / border_secondary (边框)
- 强调层：accent / accent_hover / accent_pressed (强调)
- 状态层：success / warning / error (状态)
- 特殊层：overlay / shadow / transparent

每个 token 在 DARK_TOKENS / LIGHT_TOKENS 中都有具体色值。
所有 UI 组件通过 tokens[name] 读取，不允许出现 #XXXXXX 字面量。

数据来源：复用 src/common/theme.py 中的 DARK_COLORS / LIGHT_COLORS，
通过 _ALIAS_MAP 把分散的 keys 映射到统一的 token 名。
"""
from __future__ import annotations
from typing import Dict, Optional


def _build_tokens_from_theme(colors: Dict[str, str]) -> Dict[str, str]:
    """从 DARK_COLORS / LIGHT_COLORS 构建统一 token 表。
    复用已有 key 映射，未提供的 key 给出合理默认值。
    """
    return {
        # ── 背景层 ──
        "bg_primary":    colors.get("bg",              "#0B0E11"),
        "bg_secondary":  colors.get("card_bg",         "#14141A"),
        "bg_tertiary":   colors.get("input_bg",        "#0A0A0F"),
        "bg_quaternary": colors.get("active_bg",       "#1E1E28"),
        "bg_hover":      colors.get("hover_bg",        "#1A1A22"),
        "bg_pressed":    colors.get("active_bg",       "#1E1E28"),
        "bg_disabled":   colors.get("disabled_bg",     "#14141A"),
        "bg_overlay":    "rgba(0, 0, 0, 0.6)",

        # ── 文字层 ──
        "text_primary":    colors.get("text_main",        "#ECEDF0"),
        "text_secondary":  colors.get("text_sub",         "#8B8D98"),
        "text_tertiary":   colors.get("card_desc",        "#8B8D98"),
        "text_quaternary": colors.get("text_muted",       "#4A4B56"),
        "text_muted":      colors.get("text_meta",        "#5E6673"),
        "text_inverse":    colors.get("white",            "#FFFFFF"),

        # ── 边框层 ──
        "border_primary":   colors.get("border_light",  "#2B3139"),
        "border_secondary": colors.get("border",        "#1E1E28"),
        "border_hover":     colors.get("border_hover",  "#3D4450"),
        "border_focus":     colors.get("primary",       "#4D7CFE"),

        # ── 强调层 ──
        "accent":          colors.get("primary",          "#4D7CFE"),
        "accent_hover":    colors.get("primary_hover",    "#3D6CF0"),
        "accent_pressed":  colors.get("primary_pressed",  "#2D5CD0"),
        "accent_subtle":   colors.get("primary_light_10", "rgba(77, 124, 254, 0.1)"),
        "accent_subtle_2": colors.get("primary_light_20", "rgba(77, 124, 254, 0.2)"),
        "on_accent":       colors.get("white",            "#FFFFFF"),

        # ── 状态层 ──
        "success":       colors.get("success",       "#34C759"),
        "success_hover": colors.get("success",       "#2DB350"),
        "warning":       colors.get("warning",       "#FF9500"),
        "warning_hover": colors.get("warning",       "#E08F09"),
        "error":         colors.get("error",         "#FF3B30"),
        "error_hover":   colors.get("error_hover",   "#E0352B"),

        # ── 特殊 ──
        "transparent": "transparent",
        "white":       colors.get("white", "#FFFFFF"),
        "black":       "#000000",
        "shadow":      "rgba(0, 0, 0, 0.3)",

        # ── 预览面板专用 ──
        "preview_bg":       colors.get("preview_bg",      "#2A2A32"),
        "preview_fallback": colors.get("text_sub",        "#8B8D98"),
        "preview_border":   colors.get("border",          "#1E1E28"),
    }


# ============================================================
# 初始化 Token 表（从 theme.py 拉取真实色值）
# ============================================================
try:
    from src.common.theme import DARK_COLORS, LIGHT_COLORS
    DARK_TOKENS: Dict[str, str] = _build_tokens_from_theme(DARK_COLORS)
    LIGHT_TOKENS: Dict[str, str] = _build_tokens_from_theme(LIGHT_COLORS)
except Exception:
    # 降级默认（理论上不会发生）
    DARK_TOKENS = {
        "bg_primary": "#0B0E11", "bg_secondary": "#14141A", "bg_tertiary": "#0A0A0F",
        "text_primary": "#ECEDF0", "text_secondary": "#8B8D98",
        "border_primary": "#2B3139", "border_secondary": "#1E1E28",
        "accent": "#4D7CFE", "error": "#FF3B30",
    }
    LIGHT_TOKENS = {
        "bg_primary": "#FAFAFA", "bg_secondary": "#FFFFFF", "bg_tertiary": "#F5F5F7",
        "text_primary": "#1D1D1F", "text_secondary": "#6E6E73",
        "border_primary": "#E5E5EA", "border_secondary": "#D1D1D6",
        "accent": "#4D7CFE", "error": "#FF3B30",
    }


class ThemeTokens:
    """统一主题 token 访问入口。所有 UI 组件必须通过此类读取颜色。"""

    _instance: Optional["ThemeTokens"] = None
    _current_theme: str = "dark"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def set_theme(self, theme: str) -> None:
        """切换当前主题。theme: 'dark' / 'light'"""
        if theme not in ("dark", "light"):
            raise ValueError(f"Invalid theme: {theme}")
        self._current_theme = theme

    def get(self, name: str) -> str:
        """读取指定 token 的当前主题色值。"""
        tokens = DARK_TOKENS if self._current_theme == "dark" else LIGHT_TOKENS
        if name not in tokens:
            raise KeyError(
                f"Token '{name}' not defined. "
                f"Available tokens: {sorted(tokens.keys())}"
            )
        return tokens[name]

    def get_all(self) -> Dict[str, str]:
        """获取当前主题的所有 token（用于 QSS 模板渲染）。"""
        tokens = DARK_TOKENS if self._current_theme == "dark" else LIGHT_TOKENS
        return dict(tokens)

    @property
    def theme(self) -> str:
        return self._current_theme


# 全局单例
theme_tokens = ThemeTokens()


def get_token(name: str) -> str:
    """快捷函数：读取当前主题的 token。"""
    return theme_tokens.get(name)


def get_all_tokens() -> Dict[str, str]:
    """快捷函数：获取当前主题的所有 token。"""
    return theme_tokens.get_all()
