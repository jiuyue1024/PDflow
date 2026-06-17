"""
印流PDflow - 主窗口启动脚本
加载 main_window.py 的 Ui_MainWindow，渲染窗口并进入事件循环

每个导航按钮连接到独立的功能页面。
"""
import sys
import os
import json

_root = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_root, "pages"))
sys.path.insert(0, _root)



from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QSizePolicy, QGraphicsColorizeEffect, QMessageBox, QPushButton
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QPen, QPainter

from src.common.paths import resource_path, data_path
from src.common.theme_manager import ThemeManager
from src.common.theme import DARK_COLORS, LIGHT_COLORS, get_current_theme

QSS_PATH = resource_path("pages", "global.qss")

# 动态导入生成的 UI 类
from main_window import Ui_MainWindow

# ── 导入各功能页面 ──
from pages.home_page import HomePage
from pages.merge_page import MergePage
from pages.compress_page import CompressPage
from pages.convert_page import ConvertPage
from pages.watermark_page import WatermarkPage
from pages.template_layout_page import TemplateLayoutPage
from pages.template_editor_page import TemplateEditorPage
from pages.settings_page import SettingsPage

# ── 导入 i18n 管理器 ──
from translations.translation_manager import TranslationManager, set_locale as _set_locale
from translations.translation_manager import _ as _tr


# 导航菜单配置：(按钮属性名, 页面标题, 页面工厂函数或 None(占位))
# 注意：btnSpeedwrite 的可见性由开发者模式控制，在 setup_navigation 中动态处理
NAV_ITEMS = [
    ("btnHome",            "首页",         HomePage),
    ("btnMerge",           "合并拆分",     MergePage),
    ("btnCompress",        "压缩",         CompressPage),
    ("btnConvert",         "格式转换",     ConvertPage),
    ("btnWatermark",       "水印",         WatermarkPage),
    ("btnSpeedwrite",      "速文创作",     None),   # 由开发者模式控制显示/隐藏
    ("btnTemplateLayout",  "模板排版",     TemplateLayoutPage),
    ("btnSettings",        "设置",         SettingsPage),
]

CONFIG_PATH = data_path("config.json")


def _load_config():
    """读取本地配置文件，返回开发者模式状态"""
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        return cfg.get("developer_mode", False)
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return False


_dev_mode_enabled = _load_config()

# 速文创作页面按钮索引（在 NAV_ITEMS 中）
_SPEEDWRITE_INDEX = 5


def _get_or_create_widget(factory, title):
    """根据工厂函数创建页面控件，工厂为 None 则创建占位标签"""
    if factory is None:
        widget = QLabel()
        widget.setAlignment(Qt.AlignCenter)
        widget.setObjectName("headingH1")
        widget.setStyleSheet("color: #4A4B56;")
        widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        return widget
    try:
        return factory()
    except Exception as e:
        print(f"[!] 创建页面 {title} 失败: {e}")
        widget = QLabel(f"⚠️ {title}\n页面加载失败，请检查依赖")
        widget.setAlignment(Qt.AlignCenter)
        widget.setStyleSheet("color: #848E9C; font-size: 16px;")
        return widget


def setup_navigation(ui):
    """将导航按钮与 QStackedLayout 绑定，实现页面切换。"""
    pages_stack = ui.pagesStack
    page_widgets = []

    # 隐藏/显示速文创作按钮行
    if hasattr(ui, "btnSpeedwrite_row"):
        ui.btnSpeedwrite_row.setVisible(_dev_mode_enabled)

    # 预创建所有页面控件（速文创作始终创建，可见性由 row 控制）
    for btn_attr, title, factory in NAV_ITEMS:
        if factory is None:
            # 速文创作：预加载真实页面，避免首次点击延迟
            widget = _create_speedwrite_page()
        else:
            widget = _get_or_create_widget(factory, title)
        pages_stack.addWidget(widget)
        page_widgets.append(widget)

    # 绑定所有按钮的点击事件（速文创作始终绑定，可见性由 row 控制）
    stack_index = 0
    for btn_attr, title, factory in NAV_ITEMS:
        button = getattr(ui, btn_attr)

        if factory is None:
            # 速文创作按钮：使用专用切换函数
            button.clicked.connect(lambda: _switch_to_speedwrite(ui, pages_stack))
        else:
            def make_handler(idx, ti, ba):
                def handler():
                    pages_stack.setCurrentIndex(idx)
                    ui.contentTitle.setText(ti)
                    for ba2, _, _ in NAV_ITEMS:
                        try:
                            getattr(ui, ba2).setChecked(False)
                        except AttributeError:
                            pass
                    getattr(ui, ba).setChecked(True)
                    # 切换到首页时刷新最近文件列表
                    if idx == 0 and page_widgets:
                        home_widget = page_widgets[0]
                        if hasattr(home_widget, 'refresh_recent_files'):
                            home_widget.refresh_recent_files()
                return handler

            button.clicked.connect(make_handler(stack_index, title, btn_attr))
        stack_index += 1

    # 默认选中首页
    pages_stack.setCurrentIndex(0)
    ui.contentTitle.hide()
    ui.btnHome.setChecked(True)

    # 连接导航按钮切换指示器颜色
    _connect_nav_indicators(ui)

    # 设置侧边栏 LOGO
    _setup_sidebar_logo(ui)

    # 侧边栏装饰：右侧渐变分割线
    _setup_sidebar_decorations(ui)

    # 连接首页卡片点击导航信号
    _connect_home_card_signals(ui, pages_stack, page_widgets)

    # 添加"关于"按钮到侧边栏底部
    _setup_about_button(ui)


def _setup_about_button(ui):
    """
    在侧边栏底部 footer 内创建并设置"关于"按钮。

    设计要点：
    - 位于 sidebarFooter 内部，紧贴设置按钮下方
    - 通过 1px 细线分隔，与"设置"形成「系统区」视觉分组
    - 按钮文字带版本号后缀（V1.1-beta），低对比度
    - 圆角 8px，与导航按钮保持节奏一致
    """
    from PySide6.QtWidgets import QPushButton, QFrame, QSizePolicy

    # ── 分隔细线 ──
    separator = QFrame()
    separator.setObjectName("aboutSeparator")
    separator.setFixedHeight(1)
    separator.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    # ── "关于"按钮（纯 QPushButton，避免内嵌 QLabel 的 QSS 兼容问题）──
    btn_about = QPushButton(_tr("关于印流PDflow") + "  V1.2")
    btn_about.setObjectName("btnAbout")
    btn_about.setCheckable(False)
    btn_about.setCursor(Qt.PointingHandCursor)
    btn_about.setMinimumHeight(36)

    # ── 应用样式（深色模式默认，主题切换时由 _apply_main_window_theme 更新）──
    cur_colors = DARK_COLORS if get_current_theme() == "dark" else LIGHT_COLORS
    btn_about.setStyleSheet(
        f"QPushButton#btnAbout {{"
        f"    background: transparent;"
        f"    border: none;"
        f"    border-radius: 8px;"
        f"    color: {cur_colors['sidebar_text']};"
        f"    text-align: left;"
        f"    padding: 8px 12px;"
        f"    font-size: 13px;"
        f"}}"
        f"QPushButton#btnAbout:hover {{"
        f"    color: {cur_colors['sidebar_text_active']};"
        f"    background: {cur_colors['nav_hover_qss']};"
        f"}}"
        f"QPushButton#btnAbout:pressed {{"
        f"    background: {cur_colors['white_13_qss']};"
        f"}}"
    )

    # ── 分隔细线样式 ──
    separator.setStyleSheet(
        f"QFrame#aboutSeparator {{"
        f"    background: {cur_colors['separator']};"
        f"    border: none;"
        f"}}"
    )

    # ── 连接点击事件 ──
    btn_about.clicked.connect(_show_about_dialog)

    # ── 保存到 ui 对象，方便后续主题切换时更新 ──
    ui.btnAbout = btn_about
    ui.aboutSeparator = separator

    # ── 添加到 footer 内部（设置按钮下方）──
    if hasattr(ui, "footerLayout"):
        ui.footerLayout.addSpacing(8)
        ui.footerLayout.addWidget(separator)
        ui.footerLayout.addSpacing(4)
        ui.footerLayout.addWidget(btn_about)


def _setup_sidebar_logo(ui):
    """
    设置侧边栏 LOGO（统一通过 resource_path 访问，不写死绝对路径）
    
    资源路径策略：
      - 打包前：开发目录 assets/pdflow-logo.png
      - 打包后：sys._MEIPASS/assets/pdflow-logo.png  (经 spec 的 datas 写入)
    """
    from PySide6.QtGui import QPixmap

    # 统一资源路径：与 build_exclude_plan.spec 的 datas 配置对齐
    # spec 第 39 行：把 assets/pdflow-logo.png 拷到 assets/
    candidates = [
        resource_path("assets", "pdflow-logo.png"),
        resource_path("assets", "pdflow-logo-48.png"),
        resource_path("02-素材资源", "assets", "pdflow-logo-48.png"),
    ]
    logo_path = None
    for p in candidates:
        if os.path.exists(p):
            logo_path = p
            break

    if logo_path:
        pixmap = QPixmap(logo_path)
        scaled = pixmap.scaled(
            24, 24,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        ui.navLogo.setPixmap(scaled)
    else:
        # 兜底：显示一个内置 emoji 字符，保证布局不空
        ui.navLogo.setText("📕")
        ui.navLogo.setAlignment(Qt.AlignCenter)
        ui.navLogo.setStyleSheet(
            "QLabel#navLogo { background: transparent; font-size: 18px; }"
        )
    ui.navTitle.setText(_tr("印流PDflow"))


def _setup_sidebar_decorations(ui):
    """侧边栏视觉装饰：右侧渐变分割线 + 按钮 slideIn 入场动画"""
    from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
    from PySide6.QtWidgets import QFrame, QGraphicsOpacityEffect
    from PySide6.QtGui import QPainter, QLinearGradient, QColor

    class GradientLineWidget(QFrame):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setFixedWidth(1)
            self.setAttribute(Qt.WA_TransparentForMouseEvents)
        def paintEvent(self, event):
            painter = QPainter(self)
            gradient = QLinearGradient(0, 0, 0, self.height())
            transparent = QColor(255, 255, 255, 0)
            accent = QColor(77, 124, 254, 38)
            gradient.setColorAt(0.1, transparent)
            gradient.setColorAt(0.5, accent)
            gradient.setColorAt(0.9, transparent)
            painter.setBrush(gradient)
            painter.setPen(Qt.NoPen)
            painter.drawRect(self.rect())

    line = GradientLineWidget(ui.sidebar)

    def _update_line_position():
        sidebar_w = ui.sidebar.width()
        nav_bottom = ui.navTitle.geometry().bottom()
        footer_top = ui.sidebarFooter.geometry().top() if hasattr(ui, 'sidebarFooter') else ui.sidebar.height()
        line_height = max(footer_top - nav_bottom - 10, 100)
        line.setGeometry(sidebar_w - 1, nav_bottom, 1, line_height)

    QTimer.singleShot(100, _update_line_position)

    # ── 侧边栏按钮 slideIn 入场动画（渐入效果）──
    # V1.1 RC：sidebarFooter 不参与 fade 动画，立即可见（避免 fade 失败时整个 footer 不可见）
    nav_buttons = [
        ui.navTitle,
        ui.btnHome, ui.btnMerge, ui.btnCompress,
        ui.btnConvert, ui.btnWatermark,
    ]
    if _dev_mode_enabled and hasattr(ui, "btnSpeedwrite"):
        nav_buttons.append(ui.btnSpeedwrite)
    nav_buttons.append(ui.btnTemplateLayout)

    delays = [50, 100, 130, 160, 190, 220, 250, 280]

    for idx, widget in enumerate(nav_buttons):
        delay = delays[idx] if idx < len(delays) else 350
        effect = QGraphicsOpacityEffect(widget)
        effect.setOpacity(0.0)
        widget.setGraphicsEffect(effect)
        # 保存 effect 引用防止被 GC
        widget._opacity_effect = effect

        def _do_fade(w=widget, eff=effect):
            anim = QPropertyAnimation(eff, b"opacity")
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.setDuration(400)
            anim.setEasingCurve(QEasingCurve.OutCubic)
            anim.start()
            w._fade_anim = anim

        QTimer.singleShot(delay, _do_fade)

    # V1.1 RC：sidebarFooter 立即可见，不参与 fade 动画
    if hasattr(ui, 'sidebarFooter'):
        ui.sidebarFooter.setGraphicsEffect(None)

def _connect_nav_indicators(ui):
    """连接导航按钮切换指示器颜色（checked时显示蓝色条）和图标颜色"""
    ICONS = {
        "btnHome": "btnHomeIcon",
        "btnMerge": "btnMergeIcon",
        "btnCompress": "btnCompressIcon",
        "btnConvert": "btnConvertIcon",
        "btnWatermark": "btnWatermarkIcon",
        "btnTemplateLayout": "btnTemplateLayoutIcon",
        "btnSpeedwrite": "btnSpeedwriteIcon",
    }
    INDICATORS = {
        "btnHome": "btnHome_ind",
        "btnMerge": "btnMerge_ind",
        "btnCompress": "btnCompress_ind",
        "btnConvert": "btnConvert_ind",
        "btnWatermark": "btnWatermark_ind",
        "btnTemplateLayout": "btnTemplateLayout_ind",
        "btnSpeedwrite": "btnSpeedwrite_ind",
    }

    init_colors = DARK_COLORS if get_current_theme() == "dark" else LIGHT_COLORS

    # 为每个图标创建着色器
    for btn_attr, icon_attr in ICONS.items():
        if not hasattr(ui, icon_attr):
            continue
        icon_lbl = getattr(ui, icon_attr)
        effect = QGraphicsColorizeEffect(icon_lbl)
        effect.setColor(QColor(init_colors['sidebar_icon']))
        effect.setStrength(1.0)
        icon_lbl.setGraphicsEffect(effect)
        icon_lbl._colorize = effect  # 保持引用防 GC

    def _update_indicators():
        cur_colors = DARK_COLORS if get_current_theme() == "dark" else LIGHT_COLORS
        for btn_attr, ind_attr in INDICATORS.items():
            if not hasattr(ui, btn_attr) or not hasattr(ui, ind_attr):
                continue
            btn = getattr(ui, btn_attr)
            ind = getattr(ui, ind_attr)
            if btn.isChecked():
                ind.setStyleSheet(
                    f"QFrame {{"
                    f"    background: {cur_colors['sidebar_icon_active']};"
                    f"    border: none;"
                    f"    border-radius: 0 2px 2px 0;"
                    f"}}"
                )
            else:
                ind.setStyleSheet(
                    "QFrame {"
                    "    background: transparent;"
                    "    border: none;"
                    "}"
                )

        # 同步图标颜色
        for btn_attr, icon_attr in ICONS.items():
            if not hasattr(ui, btn_attr) or not hasattr(ui, icon_attr):
                continue
            btn = getattr(ui, btn_attr)
            icon_lbl = getattr(ui, icon_attr)
            if hasattr(icon_lbl, "_colorize"):
                if btn.isChecked():
                    icon_lbl._colorize.setColor(QColor(cur_colors['sidebar_icon_active']))
                else:
                    icon_lbl._colorize.setColor(QColor(cur_colors['sidebar_icon']))

    for btn_attr in ICONS.keys():
        if not hasattr(ui, btn_attr):
            continue
        button = getattr(ui, btn_attr)
        button.toggled.connect(_update_indicators)

    _update_indicators()

def _connect_home_card_signals(ui, pages_stack, page_widgets):
    """连接 HomePage 卡片的 card_clicked 信号，点击卡片跳转到对应功能页"""
    home_page = page_widgets[0] if page_widgets else None
    if not home_page:
        print("[!] _connect_home_card_signals: home_page not found")
        return

    if not hasattr(home_page, "ui") or not hasattr(home_page.ui, "card_widgets"):
        print("[!] _connect_home_card_signals: card_widgets not found")
        return

    CARD_TO_NAV = {
        "merge": "btnMerge",
        "compress": "btnCompress",
        "convert": "btnConvert",
        "watermark": "btnWatermark",
    }

    nav_map = {}
    for idx, (btn_attr, title, _) in enumerate(NAV_ITEMS):
        nav_map[btn_attr] = (idx, title)

    def make_navigator(card_name):
        def _nav():
            target_btn = CARD_TO_NAV.get(card_name)
            if target_btn is None or target_btn not in nav_map:
                return
            target_idx, target_title = nav_map[target_btn]
            pages_stack.setCurrentIndex(target_idx)
            ui.contentTitle.setText(target_title)
            for ba, _, _ in NAV_ITEMS:
                if hasattr(ui, ba):
                    getattr(ui, ba).setChecked(False)
            if hasattr(ui, target_btn):
                getattr(ui, target_btn).setChecked(True)
        return _nav

    for card_name, card in home_page.ui.card_widgets.items():
        if hasattr(card, "card_clicked"):
            card.card_clicked.connect(make_navigator(card_name))

    # ── 连接最近文件项点击信号 ──
    def _on_file_clicked(nav_idx_str, file_path):
        """点击最近文件：跳转到对应功能页并加载文件"""
        nav_idx = int(nav_idx_str)
        target_btn = None
        target_title = None
        for idx, (btn_attr, title, _) in enumerate(NAV_ITEMS):
            if idx == nav_idx:
                target_btn = btn_attr
                target_title = title
                break

        if target_btn is None:
            return

        pages_stack.setCurrentIndex(nav_idx)
        ui.contentTitle.setText(target_title)
        for ba, _, _ in NAV_ITEMS:
            if hasattr(ui, ba):
                getattr(ui, ba).setChecked(False)
        if hasattr(ui, target_btn):
            getattr(ui, target_btn).setChecked(True)

        # 尝试将文件路径传递给目标页面
        target_widget = page_widgets[nav_idx] if nav_idx < len(page_widgets) else None
        if target_widget and file_path and os.path.exists(file_path):
            _load_file_into_page(target_widget, file_path, target_btn)

    if hasattr(home_page, "file_clicked"):
        home_page.file_clicked.connect(_on_file_clicked)


def _load_file_into_page(widget, file_path, btn_attr):
    """将文件路径加载到对应功能页面"""
    try:
        if btn_attr == "btnMerge":
            # 合并页面：添加到文件列表
            if hasattr(widget, "_file_list") and hasattr(widget, "_on_files_selected"):
                widget._on_files_selected([file_path])
        elif btn_attr == "btnCompress":
            # 压缩页面：添加到文件列表
            if hasattr(widget, "_file_paths") and hasattr(widget, "_add_file"):
                widget._add_file(file_path)
                widget._update_file_count()
        elif btn_attr == "btnConvert":
            # 转换页面：添加到文件列表
            if hasattr(widget, "_paths") and hasattr(widget, "_add_list_item"):
                if file_path.lower() not in [p.lower() for p in widget._paths]:
                    widget._paths.append(file_path)
                    widget._add_list_item(file_path, os.path.getsize(file_path))
                    widget._update_count()
        elif btn_attr == "btnWatermark":
            if hasattr(widget, "_pdf_path"):
                widget._pdf_path = file_path
                widget._pdf_input.setText(file_path)
                if hasattr(widget, "_do_preview"):
                    widget._do_preview()
    except Exception as e:
        print(f"[!] 加载文件到页面失败: {e}")


def _connect_template_signals(ui, theme_mgr):
    """
    TPL-02：连接模板排版页面信号
      - editor_requested(template_id) → 打开模板编辑器
      - editor.back_requested()       → 返回模板列表

    在创建编辑器页面时注册到 ThemeManager 并应用主题，
    确保懒加载的页面也能跟随主题切换。
    """
    from src.common.theme import DARK_COLORS, LIGHT_COLORS, get_current_theme
    pages_stack = ui.pagesStack

    # ── 查找 TemplateLayoutPage 实例 ──
    tpl_page = None
    tpl_index = -1
    for i in range(pages_stack.count()):
        w = pages_stack.widget(i)
        if isinstance(w, TemplateLayoutPage):
            tpl_page = w
            tpl_index = i
            break

    if tpl_page is None:
        print("[!] 未找到 TemplateLayoutPage，信号未连接")
        return

    # ── 模板编辑器页面（懒加载）──
    editor_page_ref = [None]
    editor_index_ref = [-1]

    def _on_editor_requested(template_id: str):
        """点击卡片确认后，进入模板编辑页面"""
        if editor_page_ref[0] is None:
            editor_page_ref[0] = TemplateEditorPage(template_id)
            pages_stack.addWidget(editor_page_ref[0])
            editor_index_ref[0] = pages_stack.count() - 1
            # 连接返回信号
            editor_page_ref[0].back_requested.connect(_on_back_requested)

            # 注册到 ThemeManager，使后续主题切换能自动更新该页面
            theme_mgr.register_page(editor_page_ref[0])

            # 立即应用当前主题（覆盖 __init__ 中硬编码的深色模式）
            # 优先使用 ThemeManager 内存状态，避免配置文件读取失败
            cur_theme = theme_mgr.current_theme if theme_mgr else get_current_theme()
            cur_colors = DARK_COLORS if cur_theme == "dark" else LIGHT_COLORS
            editor_page_ref[0].apply_theme(cur_colors)
        else:
            # 已创建，切换模板重新加载
            editor_page_ref[0].load_template(template_id)

            # load_template 重建了表单控件（又用了深色硬编码），需重新应用主题
            cur_theme = theme_mgr.current_theme if theme_mgr else get_current_theme()
            cur_colors = DARK_COLORS if cur_theme == "dark" else LIGHT_COLORS
            editor_page_ref[0].apply_theme(cur_colors)

        pages_stack.setCurrentIndex(editor_index_ref[0])
        ui.contentTitle.setText("模板编辑")

    def _on_back_requested():
        """编辑器点击返回，回到模板列表"""
        pages_stack.setCurrentIndex(tpl_index)
        ui.contentTitle.setText("模板排版")

    # ── 连接信号 ──
    tpl_page.editor_requested.connect(_on_editor_requested)


def _create_speedwrite_page():
    """预创建速文创作页面，返回 QWidget 实例"""
    try:
        from pages.speedwrite_page import SpeedwritePage
        page = SpeedwritePage()
        page.setObjectName("speedwritePage")
        return page
    except Exception as e:
        print(f"[!] 预创建速文创作页面失败: {e}")
        page = QLabel("✍️ 自由创作页面（待实现）")
        page.setAlignment(Qt.AlignCenter)
        page.setStyleSheet("color: #848E9C; font-size: 18px;")
        page.setObjectName("speedwritePage")
        return page


def _switch_to_speedwrite(ui, pages_stack):
    """切换到「速文创作」页面（已预加载，无延迟）"""
    pages_stack.setCurrentIndex(_SPEEDWRITE_INDEX)
    ui.contentTitle.setText("速文创作")

    for btn_attr, _, _ in NAV_ITEMS:
        try:
            getattr(ui, btn_attr).setChecked(False)
        except AttributeError:
            pass
    ui.btnSpeedwrite.setChecked(True)


def _show_about_dialog():
    """
    显示"关于印流PDflow"对话框。

    设计要点：
    - 自定义 QDialog，保留系统标题栏（避免 FramelessWindowHint 导致中文乱码）
    - 顶部：LOGO + 产品名（双行）
    - 中部：版本号徽章 + 简短描述
    - 下部：技术栈 chip 标签
    - 底部：版权信息 + "确定"按钮
    - 自适应深色/浅色模式
    - 圆角 12px（DESIGN.md 大卡片规范）
    """
    from PySide6.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
    )
    from PySide6.QtGui import QPixmap, QFont

    # ── 读取当前主题色（优先用 ThemeManager 内存状态）──
    cur_theme = theme_mgr.current_theme if theme_mgr else get_current_theme()
    cur_colors = DARK_COLORS if cur_theme == "dark" else LIGHT_COLORS

    bg = cur_colors['bg']
    card_bg = cur_colors['card_bg']
    title_color = cur_colors['text_main']
    sub_color = cur_colors['text_sub']
    muted = cur_colors['text_muted']
    border = cur_colors['border']
    primary = cur_colors['primary']
    primary_hover = cur_colors['primary_hover']
    primary_pressed = cur_colors['primary_pressed']

    # ── 创建对话框（保留系统标题栏，避免中文乱码）──
    dlg = QDialog()
    dlg.setWindowTitle(_tr("关于印流PDflow"))
    dlg.setModal(True)
    dlg.setFixedSize(420, 480)

    # ── 主布局 ──
    root = QVBoxLayout(dlg)
    root.setContentsMargins(24, 24, 24, 20)
    root.setSpacing(0)

    # ════════ 头部：LOGO + 标题 ════════
    header = QHBoxLayout()
    header.setSpacing(16)
    header.setAlignment(Qt.AlignVCenter)

    # LOGO
    logo_label = QLabel()
    logo_label.setFixedSize(56, 56)
    logo_label.setAlignment(Qt.AlignCenter)
    logo_path = resource_path("02-素材资源", "assets", "pdflow-logo-48.png")
    if os.path.exists(logo_path):
        pix = QPixmap(logo_path).scaled(
            56, 56, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        logo_label.setPixmap(pix)
    else:
        logo_label.setText("印")
        logo_label.setStyleSheet(
            f"background: {primary}; color: #FFFFFF;"
            f" border-radius: 14px; font-size: 26px; font-weight: 700;"
        )
    header.addWidget(logo_label)

    # 标题区
    title_box = QVBoxLayout()
    title_box.setSpacing(2)

    title_main = QLabel(_tr("印流PDflow"))
    title_main.setObjectName("aboutTitle")
    f_title = QFont()
    f_title.setPointSize(16)
    f_title.setBold(True)
    title_main.setFont(f_title)
    title_box.addWidget(title_main)

    title_sub = QLabel(_tr("设计师专用 PDF 排版工具"))
    title_sub.setObjectName("aboutSubtitle")
    f_sub = QFont()
    f_sub.setPointSize(10)
    title_sub.setFont(f_sub)
    title_box.addWidget(title_sub)

    header.addLayout(title_box)
    header.addStretch(1)
    root.addLayout(header)

    root.addSpacing(24)

    # ════════ 中部：版本徽章 + 描述 ════════
    version_row = QHBoxLayout()
    version_row.setSpacing(8)
    version_row.setAlignment(Qt.AlignVCenter)

    ver_badge = QLabel("V1.2")
    ver_badge.setObjectName("aboutVersionBadge")
    ver_badge.setAlignment(Qt.AlignCenter)
    ver_badge.setFixedHeight(22)
    f_ver = QFont()
    f_ver.setPointSize(9)
    f_ver.setBold(True)
    ver_badge.setFont(f_ver)
    version_row.addWidget(ver_badge)

    channel = QLabel(_tr("Beta版"))
    channel.setObjectName("aboutChannel")
    channel.setAlignment(Qt.AlignCenter)
    channel.setFixedHeight(22)
    f_ch = QFont()
    f_ch.setPointSize(9)
    channel.setFont(f_ch)
    version_row.addWidget(channel)
    version_row.addStretch(1)
    root.addLayout(version_row)

    root.addSpacing(16)

    # 描述文字
    desc = QLabel(
        _tr("一站式 PDF 解决方案，为设计师量身打造。\n")
        + _tr("日常办公工具箱 + 专业排版设计模块。")
    )
    desc.setObjectName("aboutDesc")
    desc.setWordWrap(True)
    f_desc = QFont()
    f_desc.setPointSize(10)
    desc.setFont(f_desc)
    root.addWidget(desc)

    root.addSpacing(20)

    # ════════ 技术栈 chip 标签 ════════
    tech_label = QLabel(_tr("技术栈"))
    tech_label.setObjectName("aboutTechLabel")
    f_tl = QFont()
    f_tl.setPointSize(9)
    tech_label.setFont(f_tl)
    root.addWidget(tech_label)

    root.addSpacing(8)

    chips_row = QHBoxLayout()
    chips_row.setSpacing(8)
    chips = ["PySide6", "PyMuPDF", "Python 3.12"]
    for chip_text in chips:
        chip = QLabel(chip_text)
        chip.setObjectName("aboutChip")
        chip.setAlignment(Qt.AlignCenter)
        chip.setFixedHeight(24)
        f_chip = QFont()
        f_chip.setPointSize(9)
        chip.setFont(f_chip)
        chips_row.addWidget(chip)
    chips_row.addStretch(1)
    root.addLayout(chips_row)

    # 弹性空间
    root.addStretch(1)

    # ════════ 底部：版权 + 确定按钮 ════════
    copyright_line = QFrame()
    copyright_line.setObjectName("aboutDivider")
    copyright_line.setFixedHeight(1)
    root.addWidget(copyright_line)

    root.addSpacing(12)

    footer_row = QHBoxLayout()
    footer_row.setSpacing(12)
    footer_row.setAlignment(Qt.AlignVCenter)

    copyright_label = QLabel("© 2026 印流PDflow. All rights reserved.")
    copyright_label.setObjectName("aboutCopyright")
    f_cp = QFont()
    f_cp.setPointSize(9)
    copyright_label.setFont(f_cp)
    footer_row.addWidget(copyright_label)
    footer_row.addStretch(1)

    ok_btn = QPushButton(_tr("确定"))
    ok_btn.setObjectName("aboutOkBtn")
    ok_btn.setFixedSize(96, 36)
    ok_btn.setCursor(Qt.PointingHandCursor)
    f_btn = QFont()
    f_btn.setPointSize(10)
    ok_btn.setFont(f_btn)
    ok_btn.clicked.connect(dlg.accept)
    footer_row.addWidget(ok_btn)

    root.addLayout(footer_row)

    # ── 统一样式（全部在 dlg 上设置，避免父子样式冲突）──
    dlg.setStyleSheet(
        f"QDialog {{"
        f"    background: {bg};"
        f"}}"
        f"QLabel#aboutTitle {{ color: {title_color}; background: transparent; }}"
        f"QLabel#aboutSubtitle {{ color: {sub_color}; background: transparent; }}"
        f"QLabel#aboutDesc {{ color: {sub_color}; background: transparent; }}"
        f"QLabel#aboutTechLabel {{ color: {muted}; background: transparent; }}"
        f"QLabel#aboutVersionBadge {{"
        f"    color: #FFFFFF;"
        f"    background: {primary};"
        f"    border-radius: 11px;"
        f"    padding: 0 10px;"
        f"}}"
        f"QLabel#aboutChannel {{"
        f"    color: {sub_color};"
        f"    background: {border};"
        f"    border-radius: 11px;"
        f"    padding: 0 10px;"
        f"}}"
        f"QLabel#aboutChip {{"
        f"    color: {sub_color};"
        f"    background: {border};"
        f"    border-radius: 12px;"
        f"    padding: 0 10px;"
        f"}}"
        f"QFrame#aboutDivider {{ background: {border}; border: none; }}"
        f"QLabel#aboutCopyright {{ color: {muted}; background: transparent; }}"
        f"QPushButton#aboutOkBtn {{"
        f"    background: {primary};"
        f"    color: #FFFFFF;"
        f"    border: none;"
        f"    border-radius: 6px;"
        f"    font-size: 13px;"
        f"}}"
        f"QPushButton#aboutOkBtn:hover {{ background: {primary_hover}; }}"
        f"QPushButton#aboutOkBtn:pressed {{ background: {primary_pressed}; }}"
    )

    dlg.exec()


def _connect_settings_signals(ui, pages_stack, translation_manager=None):
    """
    连接设置页面的开发者模式切换信号 + 语言切换信号
    当开发者模式状态改变时，更新 btnSpeedwrite 行的可见性
    """
    settings_page = None
    for i in range(pages_stack.count()):
        w = pages_stack.widget(i)
        if isinstance(w, SettingsPage):
            settings_page = w
            break

    if settings_page is None:
        return

    def _on_developer_mode_changed(enabled):
        global _dev_mode_enabled
        _dev_mode_enabled = enabled

        if hasattr(ui, "btnSpeedwrite_row"):
            ui.btnSpeedwrite_row.setVisible(enabled)

    settings_page.developer_mode_changed.connect(_on_developer_mode_changed)

    # 连接语言切换信号
    if translation_manager is not None:
        # 注册所有可见页面到 TranslationManager
        _register_pages_for_translation(pages_stack, translation_manager)
        settings_page.language_changed.connect(translation_manager.switch_language)
        settings_page.language_changed.connect(lambda _: _retranslate_sidebar(ui))


def _register_pages_for_translation(pages_stack, translation_manager):
    """将页面栈中的所有页面注册到 TranslationManager"""
    for i in range(pages_stack.count()):
        w = pages_stack.widget(i)
        if isinstance(w, HomePage):
            translation_manager.register_page(w, has_ui=False)
        elif isinstance(w, SettingsPage):
            translation_manager.register_page(w, has_ui=False)
        elif isinstance(w, MergePage):
            translation_manager.register_page(w, has_ui=False)
        elif isinstance(w, CompressPage):
            translation_manager.register_page(w, has_ui=False)
        elif isinstance(w, ConvertPage):
            translation_manager.register_page(w, has_ui=False)
        elif isinstance(w, WatermarkPage):
            translation_manager.register_page(w, has_ui=False)
        elif isinstance(w, TemplateLayoutPage):
            translation_manager.register_page(w, has_ui=False)


def _retranslate_sidebar(ui):
    """翻译侧边栏导航按钮文字"""
    ui.navTitle.setText(_tr("印流PDflow"))
    ui.btnHome.setText(_tr("首页"))
    ui.btnMerge.setText(_tr("合并拆分"))
    ui.btnCompress.setText(_tr("压缩优化"))
    ui.btnConvert.setText(_tr("格式转换"))
    ui.btnWatermark.setText(_tr("水印处理"))
    ui.btnSpeedwrite.setText(_tr("速文创作"))
    ui.btnTemplateLayout.setText(_tr("模板排版"))
    ui.btnSettings.setText(_tr("设置"))


# ── 自定义标题栏按钮（V1.1 RC — QPainter 直接绘制几何图形）──
class TitleBarBtn(QPushButton):
    """自定义绘制标题栏按钮 — 摆脱 QStyle 图标的细线风格。

    V1.1 RC：完全控制图标粗细、颜色、hover 状态。
    """

    def __init__(self, kind, parent=None):
        super().__init__(parent)
        self.kind = kind  # 'min' / 'max' / 'close'
        self.is_close = (kind == 'close')
        self.setFixedSize(36, 32)
        self.setCursor(Qt.PointingHandCursor)
        # 默认颜色（启动时）
        self._icon_color = QColor("#B4B4B4")
        self._hover_bg = QColor(255, 255, 255, 25)
        self._close_bg = QColor("#E81123")
        self._close_hover_fg = QColor("#FFFFFF")
        self._is_maximized = False

    def apply_theme(self, icon_color, hover_bg, close_bg="#E81123", close_hover_fg="#FFFFFF"):
        """主题切换时更新颜色"""
        self._icon_color = QColor(icon_color)
        self._hover_bg = QColor(hover_bg)
        self._close_bg = QColor(close_bg)
        self._close_hover_fg = QColor(close_hover_fg)
        self.update()

    def set_maximized_state(self, is_max):
        if self.kind == 'max':
            self._is_maximized = is_max
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        rect = self.rect()
        w, h = rect.width(), rect.height()
        cx, cy = w // 2, h // 2

        is_hover = self.underMouse()

        # 背景
        if self.is_close and is_hover:
            painter.fillRect(rect, self._close_bg)
        elif is_hover:
            painter.fillRect(rect, self._hover_bg)

        # 图标颜色
        if self.is_close and is_hover:
            color = self._close_hover_fg
        else:
            color = self._icon_color

        pen = QPen(color, 1.5)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)

        if self.kind == 'min':
            # 粗横线
            painter.drawLine(cx - 5, cy, cx + 5, cy)
        elif self.kind == 'max':
            if self._is_maximized:
                # 还原图标 — 两个嵌套方框
                painter.drawRect(cx - 3, cy - 5, 6, 6)
                painter.drawRect(cx - 5, cy - 3, 6, 6)
            else:
                # 单方框（10x10）
                painter.drawRect(cx - 5, cy - 5, 10, 10)
        elif self.kind == 'close':
            # X — 两条交叉线
            painter.drawLine(cx - 4, cy - 4, cx + 4, cy + 4)
            painter.drawLine(cx - 4, cy + 4, cx + 4, cy - 4)


def _apply_main_window_theme(ui, colors, title_bar=None, central=None, title_btns=None):
    """
    主题切换时更新主窗口中所有硬编码的内联样式。

    设计原则：
    - 全局 QSS 样式由 ThemeManager 通过 app.setStyleSheet() 统一管理
    - 此函数只覆盖 main_window.py 中 setStyleSheet() 设置的内联样式
    - 不再向 app 或 window 追加 QSS，避免覆盖全局样式
    """
    # ── 1. 更新导航按钮的内联样式（覆盖 _make_nav_row 中的 setStyleSheet）──
    nav_rows = [
        ('btnHome', 'btnHome_row', 'btnHome_ind'),
        ('btnMerge', 'btnMerge_row', 'btnMerge_ind'),
        ('btnCompress', 'btnCompress_row', 'btnCompress_ind'),
        ('btnConvert', 'btnConvert_row', 'btnConvert_ind'),
        ('btnWatermark', 'btnWatermark_row', 'btnWatermark_ind'),
        ('btnSpeedwrite', 'btnSpeedwrite_row', 'btnSpeedwrite_ind'),
        ('btnTemplateLayout', 'btnTemplateLayout_row', 'btnTemplateLayout_ind'),
    ]
    for btn_attr, row_attr, ind_attr in nav_rows:
        btn = getattr(ui, btn_attr, None)
        row = getattr(ui, row_attr, None)
        ind = getattr(ui, ind_attr, None)
        if btn:
            btn.setStyleSheet(
                f"QPushButton {{"
                f"    background: transparent; border: none; color: {colors['sidebar_text']};"
                f"    text-align: left; padding: 0 12px; font-size: 14px;"
                f"}}"
                f"QPushButton:hover {{ color: {colors['sidebar_text_active']}; }}"
                f"QPushButton:checked {{ color: {colors['sidebar_text_active']}; font-weight: 600; }}"
            )
        if row:
            if btn and btn.isChecked():
                row.setStyleSheet(
                    f"background: {colors['nav_checked_bg_qss']}; border-radius: 8px;"
                )
            else:
                row.setStyleSheet("background: transparent; border-radius: 0;")
        if ind:
            if btn and btn.isChecked():
                ind.setStyleSheet(
                    f"QFrame {{"
                    f"    background: {colors['sidebar_icon_active']};"
                    f"    border: none; border-radius: 1px;"
                    f"}}"
                )
            else:
                ind.setStyleSheet(
                    "QFrame {"
                    "    background: transparent;"
                    "    border: none;"
                    "}"
                )

    # ── 2. 更新设置按钮 ──
    if hasattr(ui, 'btnSettings'):
        ui.btnSettings.setStyleSheet(
            f"QPushButton {{"
            f"    background: transparent; border: none; color: {colors['sidebar_text']};"
            f"    text-align: left; padding: 0 14px; font-size: 13px;"
            f"}}"
            f"QPushButton:hover {{ color: {colors['sidebar_text_active']}; }}"
        )

    # ── 3. 更新"关于"按钮（侧边栏底部）──
    if hasattr(ui, 'btnAbout'):
        ui.btnAbout.setStyleSheet(
            f"QPushButton#btnAbout {{"
            f"    background: transparent;"
            f"    border: none;"
            f"    border-radius: 8px;"
            f"    color: {colors['sidebar_text']};"
            f"    text-align: left;"
            f"    padding: 8px 12px;"
            f"    font-size: 13px;"
            f"}}"
            f"QPushButton#btnAbout:hover {{"
            f"    color: {colors['sidebar_text_active']};"
            f"    background: {colors['nav_hover_qss']};"
            f"}}"
            f"QPushButton#btnAbout:pressed {{"
            f"    background: {colors['white_13_qss']};"
            f"}}"
        )
        if hasattr(ui, 'aboutSeparator'):
            ui.aboutSeparator.setStyleSheet(
                f"QFrame#aboutSeparator {{"
                f"    background: {colors['separator']};"
                f"    border: none;"
                f"}}"
            )

    # ── 4. 更新侧边栏 footer ──
    if hasattr(ui, 'sidebarFooter'):
        ui.sidebarFooter.setStyleSheet(
            f"QFrame#sidebarFooter {{\n"
            f"    border-top: 1px solid {colors['white_8_qss']};\n"
            f"    background: transparent;\n"
            f"}}\n"
        )

    # ── 5. 更新导航图标颜色（通过 apply_sidebar_theme）──
    if hasattr(ui, 'apply_sidebar_theme'):
        ui.apply_sidebar_theme(colors)

    # ── 6. 更新导航指示器颜色（QGraphicsColorizeEffect）──
    ICONS = {
        "btnHome": "btnHomeIcon",
        "btnMerge": "btnMergeIcon",
        "btnCompress": "btnCompressIcon",
        "btnConvert": "btnConvertIcon",
        "btnWatermark": "btnWatermarkIcon",
        "btnTemplateLayout": "btnTemplateLayoutIcon",
        "btnSpeedwrite": "btnSpeedwriteIcon",
    }
    for btn_attr, icon_attr in ICONS.items():
        btn = getattr(ui, btn_attr, None)
        icon_lbl = getattr(ui, icon_attr, None)
        if btn and icon_lbl and hasattr(icon_lbl, "_colorize"):
            if btn.isChecked():
                icon_lbl._colorize.setColor(QColor(colors['sidebar_icon_active']))
            else:
                icon_lbl._colorize.setColor(QColor(colors['sidebar_icon']))

    # ── 7. 更新自定义标题栏和窗口控件的内联样式 ──
    if title_bar is not None:
        title_bar.setStyleSheet(
            f"QWidget#titleBar {{"
            f"    background: {colors['title_bar_bg']};"
            f"    border-top-left-radius: 8px;"
            f"    border-top-right-radius: 8px;"
            f"}}"
        )

    if central is not None:
        central.setStyleSheet(
            f"background: {colors['bg']}; border-radius: 8px;"
        )

    if title_btns:
        btn_min, btn_max, btn_close = title_btns
        # V1.1 RC：TitleBarBtn 自定义 paintEvent，用 apply_theme 更新颜色
        icon_color = colors['text_sub']
        hover_bg = colors['hover_bg']
        for btn in (btn_min, btn_max, btn_close):
            if isinstance(btn, TitleBarBtn):
                btn.apply_theme(icon_color=icon_color, hover_bg=hover_bg)


def main():
    # 创建 i18n 管理器
    i18n = TranslationManager()

    # 读取保存的语言设置
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        saved_locale = cfg.get("language", "zh_CN")
    except (FileNotFoundError, json.JSONDecodeError):
        saved_locale = "zh_CN"
    _set_locale(saved_locale)

    app = QApplication(sys.argv)
    app.setApplicationName("印流PDflow")

    # 设置全局应用图标（影响任务栏和窗口图标）
    from PySide6.QtGui import QIcon
    # 优先使用 .ico（Windows 任务栏/系统托盘都识别）
    ico_path = resource_path("assets", "pdflow-logo.ico")
    png_path = resource_path("assets", "pdflow-logo.png")
    icon_path = ico_path if os.path.exists(ico_path) else png_path
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # ── 初始化主题管理器（在创建窗口之前）──
    theme_mgr = ThemeManager()
    saved_theme = get_current_theme()
    colors = DARK_COLORS if saved_theme == "dark" else LIGHT_COLORS

    # 创建主窗口（无边框 + 自定义标题栏）
    window = QMainWindow()
    window.setWindowFlags(Qt.FramelessWindowHint)
    window.setAttribute(Qt.WA_TranslucentBackground, False)

    # 创建自定义标题栏容器
    from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel
    from PySide6.QtGui import QFont, QPixmap, QPainter

    central = QWidget()
    central.setObjectName("centralWidget")
    central.setStyleSheet(f"background: {colors['bg']}; border-radius: 8px;")
    main_vlayout = QVBoxLayout(central)
    main_vlayout.setSpacing(0)
    main_vlayout.setContentsMargins(0, 0, 0, 0)

    # ── 自定义标题栏 ──
    title_bar = QWidget()
    title_bar.setObjectName("titleBar")
    title_bar.setFixedHeight(40)
    title_bar.setStyleSheet(
        f"QWidget#titleBar {{"
        f"    background: {colors['title_bar_bg']};"
        f"    border-top-left-radius: 8px;"
        f"    border-top-right-radius: 8px;"
        f"}}"
    )
    title_hlayout = QHBoxLayout(title_bar)
    title_hlayout.setSpacing(0)
    title_hlayout.setContentsMargins(0, 0, 0, 0)
    title_hlayout.setAlignment(Qt.AlignVCenter)
    title_hlayout.addStretch()

    # 最小化按钮
    btn_min = TitleBarBtn('min')
    btn_min.clicked.connect(window.showMinimized)
    title_hlayout.addWidget(btn_min)

    # 最大化/还原按钮
    btn_max = TitleBarBtn('max')
    def _toggle_max():
        if window.isMaximized():
            window.showNormal()
            btn_max.set_maximized_state(False)
        else:
            window.showMaximized()
            btn_max.set_maximized_state(True)
    btn_max.clicked.connect(_toggle_max)
    title_hlayout.addWidget(btn_max)

    # 关闭按钮
    btn_close = TitleBarBtn('close')
    btn_close.clicked.connect(window.close)
    title_hlayout.addWidget(btn_close)

    main_vlayout.addWidget(title_bar)

    # ── 原 UI 内容 ──
    # 直接在目标 window 上运行 setupUi，然后取出 centralWidget 嵌入
    ui = Ui_MainWindow()
    ui.setupUi(window)
    old_central = window.centralWidget()
    old_central.setParent(None)  # 从 window 分离
    main_vlayout.addWidget(old_central, 1)

    window.setCentralWidget(central)

    # ── 应用主题（使用 ThemeManager，覆盖全局 QSS）──
    theme_mgr.apply_theme(saved_theme, app=app)

    # ── 应用内联样式（标题栏、导航按钮等）──
    _apply_main_window_theme(
        ui, colors,
        title_bar=title_bar,
        central=central,
        title_btns=(btn_min, btn_max, btn_close)
    )

    # 配置导航切换
    setup_navigation(ui)

    # TPL-02：连接模板排版相关信号
    _connect_template_signals(ui, theme_mgr)

    # 连接设置页面信号 + 语言切换信号
    _connect_settings_signals(ui, ui.pagesStack, i18n)

    # ── 注册所有页面到 ThemeManager，并在启动时应用主题内联样式 ──
    for i in range(ui.pagesStack.count()):
        w = ui.pagesStack.widget(i)
        # 注册页面，使 ThemeManager 在后续主题切换时自动调用 apply_theme
        theme_mgr.register_page(w)
        # 启动时立即应用主题（覆盖各页面 __init__ 中硬编码的深色模式内联样式）
        if hasattr(w, 'apply_theme'):
            try:
                w.apply_theme(colors)
            except Exception as e:
                print(f"[main] 启动时应用主题到 {w.__class__.__name__} 失败: {e}")
        # 设置页面额外传入 theme_mgr 引用
        if isinstance(w, SettingsPage):
            w.set_theme_manager(theme_mgr)

    # ── 连接主题切换信号（更新侧边栏、标题栏等主窗口内联样式）──
    def _on_theme_changed(theme_name):
        new_colors = DARK_COLORS if theme_name == "dark" else LIGHT_COLORS
        _apply_main_window_theme(
            ui, new_colors,
            title_bar=title_bar,
            central=central,
            title_btns=(btn_min, btn_max, btn_close)
        )

    theme_mgr.theme_changed.connect(_on_theme_changed)

    # ── 标题栏拖拽移动 ──
    class DragHelper:
        def __init__(self, widget, target):
            self.widget = widget
            self.target = target
            self.drag_pos = None
            widget.mousePressEvent = self._mouse_press
            widget.mouseMoveEvent = self._mouse_move
            widget.mouseReleaseEvent = self._mouse_release

        def _mouse_press(self, event):
            if event.button() == Qt.LeftButton:
                self.drag_pos = event.globalPos() - self.target.frameGeometry().topLeft()
                event.accept()

        def _mouse_move(self, event):
            if self.drag_pos and event.buttons() == Qt.LeftButton:
                self.target.move(event.globalPos() - self.drag_pos)
                event.accept()

        def _mouse_release(self, event):
            self.drag_pos = None
            event.accept()

    DragHelper(title_bar, window)

    # 双击标题栏最大化/还原
    def _title_dbl_click(event):
        _toggle_max()
    title_bar.mouseDoubleClickEvent = _title_dbl_click

    # ═══════════════════════════════════════════════════════════════
    # 系统托盘图标（关闭按钮隐藏到托盘，不退出进程）
    # ═══════════════════════════════════════════════════════════════
    from PySide6.QtWidgets import QSystemTrayIcon, QMenu
    from PySide6.QtGui import QCursor, QAction

    tray_icon = None
    if QSystemTrayIcon.isSystemTrayAvailable():
        tray_icon = QSystemTrayIcon(QIcon(icon_path), app)
        tray_icon.setToolTip("印流PDflow V1.2")

        tray_menu = QMenu()

        def _tray_show():
            window.showNormal()
            window.activateWindow()
            window.raise_()

        def _tray_quit():
            # 真正退出（绕过 closeEvent 的隐藏逻辑）
            window.setProperty("__force_quit__", True)
            window.close()
            app.quit()

        act_show = QAction("显示主窗口", tray_menu)
        act_show.triggered.connect(_tray_show)
        act_quit = QAction("退出", tray_menu)
        act_quit.triggered.connect(_tray_quit)
        tray_menu.addAction(act_show)
        tray_menu.addSeparator()
        tray_menu.addAction(act_quit)
        tray_icon.setContextMenu(tray_menu)

        # 双击托盘 = 显示主窗口
        def _tray_activated(reason):
            if reason == QSystemTrayIcon.DoubleClick:
                _tray_show()
        tray_icon.activated.connect(_tray_activated)

        tray_icon.show()

        # 拦截 closeEvent：默认隐藏到托盘，菜单"退出"才真正退出
        def _close_event(event):
            if window.property("__force_quit__"):
                event.accept()
                return
            if tray_icon and tray_icon.isVisible():
                window.hide()
                tray_icon.showMessage(
                    "印流PDflow",
                    "应用已最小化到系统托盘。右键托盘图标可退出。",
                    QSystemTrayIcon.Information,
                    2000
                )
                event.ignore()
            else:
                event.accept()
        window.closeEvent = _close_event

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
