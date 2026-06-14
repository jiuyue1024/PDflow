"""
theme_manager.py — 印流PDflow 主题管理类

职责：
  1. 加载 global.qss.template 并替换 {{TOKEN}} 为实际色值
  2. 将生成的样式表应用到 QApplication
  3. 支持深色/浅色模式切换
  4. 通知所有注册的页面（apply_theme）更新内联样式
  5. 持久化主题偏好

用法：
  theme_mgr = ThemeManager()
  theme_mgr.apply_theme("dark")   # 切换到深色模式
  theme_mgr.apply_theme("light")  # 切换到浅色模式
  theme_mgr.register_page(widget) # 让 widget 在切换时收到 apply_theme(colors) 调用
"""

import os

from PySide6.QtCore import Signal, QObject

from src.common.theme import DARK_COLORS, LIGHT_COLORS, get_current_theme, set_theme
from src.common.paths import resource_path


class ThemeManager(QObject):
    """全局主题管理器（单例模式）"""

    theme_changed = Signal(str)  # 参数: "dark" | "light"

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized"):
            return
        super().__init__()
        self._initialized = True

        self._template_path = resource_path("pages", "global.qss.template")
        self._template_content = None
        self._current_theme = "dark"
        self._pages = []  # 注册的页面列表，每项为 (widget, has_apply_theme)

        self._load_template()

    # ── 模板加载 ──

    def _load_template(self):
        """读取 QSS 模板文件"""
        if os.path.exists(self._template_path):
            with open(self._template_path, encoding="utf-8") as f:
                self._template_content = f.read()
            print(f"[ThemeManager] ✓ 已加载模板: {self._template_path}")
        else:
            # 回退：直接使用 qss.template 的搜索路径
            alt_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "pages", "global.qss.template"
            )
            if os.path.exists(alt_path):
                with open(alt_path, encoding="utf-8") as f:
                    self._template_content = f.read()
                print(f"[ThemeManager] ✓ 已加载模板（备选路径）: {alt_path}")
            else:
                print(f"[ThemeManager] ✗ 未找到模板: {self._template_path}")
                self._template_content = ""

    # ── 主题应用 ──

    def apply_theme(self, theme: str = None, app=None):
        """
        应用主题：替换模板中的 token → 实际色值 → 设置 QApplication 样式表
        
        参数：
          theme: "dark" | "light"，为 None 则从配置文件读取
          app:   QApplication 实例，为 None 则自动获取
        """
        from PySide6.QtWidgets import QApplication
        from PySide6.QtGui import QPalette, QColor

        if theme is None:
            theme = get_current_theme()

        self._current_theme = theme
        colors = DARK_COLORS if theme == "dark" else LIGHT_COLORS

        # ── 同步 ThemeTokens 全局单例 ──
        from src.common.theme_tokens import theme_tokens
        theme_tokens.set_theme(theme)

        # 生成样式表（优先用预渲染 light.qss / dark.qss，回退到模板渲染）
        qss = self.get_qss(theme)

        # 应用到 QApplication
        qapp = app or QApplication.instance()
        if qapp:
            # ── 仅当窗口已可见时才冻结画面（启动时跳过，避免延迟首次显示）──
            freeze = any(w.isVisible() for w in qapp.topLevelWidgets())
            if freeze:
                for w in qapp.topLevelWidgets():
                    w.setUpdatesEnabled(False)

            try:
                # ── Step 1: 设置全局调色板（用 token 字典访问，无硬编码） ──
                palette = QPalette()
                palette.setColor(QPalette.Window, QColor(colors['bg']))
                palette.setColor(QPalette.WindowText, QColor(colors['text_main']))
                palette.setColor(QPalette.Base, QColor(colors['input_bg']))
                palette.setColor(QPalette.AlternateBase, QColor(colors['card_bg']))
                palette.setColor(QPalette.Text, QColor(colors['text_main']))
                palette.setColor(QPalette.Button, QColor(colors['card_bg']))
                palette.setColor(QPalette.ButtonText, QColor(colors['text_main']))
                palette.setColor(QPalette.Highlight, QColor(colors['primary']))
                palette.setColor(QPalette.HighlightedText, QColor(colors.get('text_inverse', '#ECEDF0')))
                qapp.setPalette(palette)

                # ── Step 2: reload_qss — 重新注入 QSS 模板 ──
                qapp.setStyleSheet(qss)

                # ── Step 3: refresh_dynamic_widgets — 重建所有动态生成的控件样式 ──
                self._refresh_dynamic_widgets(qapp, colors)

                # ── Step 4: 强制完全重绘流程（unpolish → polish → update） ──
                self._full_repaint(qapp, colors)

                # 持久化
                set_theme(theme)

                # 发射信号（触发 _apply_main_window_theme 等处理器，仍在冻结期内）
                self.theme_changed.emit(theme)
            finally:
                # ── 解冻画面（仅当启动后切换主题时才执行）──
                if freeze:
                    for w in qapp.topLevelWidgets():
                        w.setUpdatesEnabled(True)

        mode_name = "深色模式" if theme == "dark" else "浅色模式"
        print(f"[ThemeManager] ✓ 已切换到{mode_name}")

    def _clear_widget_styles(self, qapp):
        """Step 1: 清空所有控件的内联 stylesheet。
        防止旧硬编码样式在切换后残留。
        """
        for widget in qapp.allWidgets():
            try:
                if widget and widget.styleSheet():
                    widget.setStyleSheet("")
            except Exception:
                pass

    def _refresh_dynamic_widgets(self, qapp, colors: dict):
        """Step 3: 重建所有动态生成的组件样式。
        调用每个页面的 apply_theme(colors) 方法。
        """
        # 通知所有注册页面（这一步会触发每个页面的 _rebuild_inline_styles）
        self._notify_pages(colors)

    def _full_repaint(self, qapp, colors: dict):
        """Step 4: 完整重绘流程：unpolish → polish → repaint → update 递归
        确保主题切换后无残留深色/浅色颜色。
        """
        from PySide6.QtCore import QEvent

        # Step 4.1: 清除样式缓存（所有控件）
        for widget in qapp.allWidgets():
            if widget:
                try:
                    widget.style().unpolish(widget)
                except Exception:
                    pass

        # Step 4.2: 重新应用样式（所有控件）
        for widget in qapp.allWidgets():
            if widget:
                try:
                    widget.style().polish(widget)
                except Exception:
                    pass

        # Step 4.3: 递归强制重绘所有控件（包括嵌套子控件）
        self._repaint_recursive(qapp)

        # Step 4.4: 派发主题变更事件（让自定义控件也能响应）
        for widget in qapp.topLevelWidgets():
            self._dispatch_theme_event(widget, colors)

    def _repaint_recursive(self, qapp):
        """递归重绘所有控件及其子控件"""
        for top_widget in qapp.topLevelWidgets():
            self._repaint_widget_recursive(top_widget)

    def _repaint_widget_recursive(self, widget):
        """递归重绘单个控件及其所有子控件"""
        try:
            # 清除并重绘当前控件
            widget.style().unpolish(widget)
            widget.style().polish(widget)
            widget.repaint()
            widget.update()

            # 递归处理所有子控件
            for child in widget.children():
                if hasattr(child, 'style') and hasattr(child, 'repaint'):
                    child.style().unpolish(child)
                    child.style().polish(child)
                    child.repaint()
                    child.update()
                    # 递归子控件的子控件
                    self._repaint_widget_recursive(child)
        except Exception:
            pass

    def _dispatch_theme_event(self, widget, colors: dict):
        """派发主题变更事件到控件树"""
        try:
            from PySide6.QtCore import QEvent
            event_type = QEvent.Type(QEvent.User + 100)
            event = QEvent(event_type)

            # 派发事件到当前控件
            if hasattr(widget, 'event'):
                widget.event(event)

            # 递归派发所有子控件
            for child in widget.children():
                if hasattr(child, 'event'):
                    child.event(event)
                self._dispatch_theme_event(child, colors)
        except Exception:
            pass

    def _render_qss(self, colors: dict) -> str:
        """将模板中的 {{TOKEN}} 替换为实际色值"""
        if not self._template_content:
            return ""

        qss = self._template_content
        for token, value in colors.items():
            qss = qss.replace("{{" + token + "}}", value)
        return qss

    def get_qss(self, theme: str = None) -> str:
        """返回渲染后的 QSS 字符串（不应用到 app）。

        优先使用预渲染文件 light.qss / dark.qss，回退到模板渲染。
        """
        if theme is None:
            theme = self._current_theme

        # 优先加载预渲染文件
        static_path = resource_path("pages", f"{theme}.qss")
        if os.path.exists(static_path):
            try:
                with open(static_path, encoding="utf-8") as f:
                    qss = f.read()
                # 静态文件不应包含 {{TOKEN}} 残留
                if "{{" in qss:
                    print(f"[ThemeManager] ⚠ 静态 QSS 含未渲染 token，回退到模板渲染")
                else:
                    return qss
            except Exception as e:
                print(f"[ThemeManager] ⚠ 加载静态 QSS 失败: {e}")

        # 回退到模板渲染
        colors = DARK_COLORS if theme == "dark" else LIGHT_COLORS
        return self._render_qss(colors)

    # ── 页面注册 ──

    def register_page(self, widget):
        """
        注册支持主题切换的页面。
        widget 需实现 apply_theme(colors) 方法。
        重复注册同一个 widget 会自动去重。
        """
        if hasattr(widget, "apply_theme"):
            if widget not in self._pages:
                self._pages.append(widget)
        else:
            print(f"[ThemeManager] ⚠ {widget.__class__.__name__} 未实现 apply_theme，跳过注册")

    def unregister_page(self, widget):
        """取消注册页面"""
        if widget in self._pages:
            self._pages.remove(widget)

    def _notify_pages(self, colors: dict):
        """通知所有注册页面更新内联样式"""
        for widget in self._pages:
            try:
                widget.apply_theme(colors)
            except Exception as e:
                print(f"[ThemeManager] ⚠ 通知 {widget.__class__.__name__} 失败: {e}")

    # ── 查询 ──

    @property
    def current_theme(self) -> str:
        return self._current_theme

    def is_dark(self) -> bool:
        return self._current_theme == "dark"

    def toggle(self, app=None):
        """切换深色/浅色"""
        new = "light" if self._current_theme == "dark" else "dark"
        self.apply_theme(new, app)
