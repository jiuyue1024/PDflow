"""
settings_page.py — 印流PDflow 设置页

包含：
  Ui_SettingsPage — 由 pyside6-uic 自动生成的 UI 类（位于 settings_page_ui.py）
  SettingsPage    — 业务逻辑类，负责设置读写与信号分发
"""

import json
import os

from PySide6.QtWidgets import QWidget, QFileDialog, QFrame, QHBoxLayout, QVBoxLayout, QLabel, QComboBox
from PySide6.QtCore import Signal, QTimer, Qt, QUrl
from PySide6.QtGui import QPixmap, QDesktopServices

from pages.settings_page_ui import Ui_SettingsPage
from src.common.paths import data_path, resource_path
from src.common.theme import get_current_theme
from translations.translation_manager import _ as _tr


CONFIG_PATH = data_path("config.json")

LOCALE_MAP = {0: "zh_CN", 1: "zh_TW", 2: "en_US"}
INDEX_MAP = {v: k for k, v in LOCALE_MAP.items()}


def _read_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _write_config(data):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════════════════════════
# 业务逻辑类
# ═══════════════════════════════════════════════════════════════════════

class SettingsPage(QWidget):
    """设置页业务逻辑"""

    developer_mode_changed = Signal(bool)
    language_changed = Signal(str)
    output_dir_changed = Signal(str)

    def __init__(self):
        super().__init__()
        self.setObjectName("settingsPage")

        self.ui = Ui_SettingsPage()
        self.ui.setupUi(self)

        self._theme_mgr = None
        self._theme_row = None
        self._theme_combo = None
        self._theme_title_label = None
        self._theme_hint_label = None

        self._suffix_timer = QTimer()
        self._suffix_timer.setSingleShot(True)
        self._suffix_timer.timeout.connect(self._save_suffix)

        # ── 后缀输入组强制右对齐 ──
        # 取出 suffixInputLayout（index=2）→ 移除中间 spacer（index=1）→ 在末尾先加 stretch 再放回输入组
        input_layout = self.ui.rowSuffixLayout.takeAt(2)   # 取出 suffixInputLayout
        spacer_item = self.ui.rowSuffixLayout.takeAt(1)     # 移除中间 spacer
        del spacer_item
        self.ui.rowSuffixLayout.addStretch(1)               # 弹性空间（左）
        self.ui.rowSuffixLayout.addItem(input_layout)       # 输入组（被推到右侧）

        self._set_icons()
        self._create_theme_row()
        self._connect_signals()
        self._load_settings()

    def _set_icons(self):
        self.ui.lblPageIcon.setText("⚙")
        # 设置关于页 LOGO 图标（统一通过 resource_path 访问，兼容开发/打包模式）
        candidates = [
            resource_path("assets", "pdflow-logo.png"),
            resource_path("assets", "pdflow-logo-icon.png"),
            resource_path("02-素材资源", "assets", "pdflow-logo-48.png"),
        ]
        logo_path = next((p for p in candidates if os.path.exists(p)), None)
        if logo_path:
            pix = QPixmap(logo_path).scaled(36, 36, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.ui.lblAboutIcon.setPixmap(pix)
            self.ui.lblAboutIcon.setStyleSheet(
                "QLabel#lblAboutIcon {"
                "    background: transparent;"
                "    border-radius: 10px;"
                "}"
            )
        else:
            # 兜底：保证设置页布局完整
            self.ui.lblAboutIcon.setText("📄")
            self.ui.lblAboutIcon.setAlignment(Qt.AlignCenter)

    def _create_theme_row(self):
        """在通用卡片中创建主题切换行，插入到语言行和开发者行之间"""
        from src.common.theme import DARK_COLORS

        # ── 主题行容器 ──
        row = QFrame()
        row.setObjectName("rowTheme")
        self._theme_row = row
        row_layout = QHBoxLayout(row)
        row_layout.setSpacing(12)
        row_layout.setContentsMargins(0, 0, 0, 0)

        # ── 左侧标签 ──
        label_layout = QVBoxLayout()
        label_layout.setSpacing(2)

        title_label = QLabel(row)
        title_label.setObjectName("lblTheme")
        title_label.setText(_tr("主题"))
        self._theme_title_label = title_label
        label_layout.addWidget(title_label)

        hint_label = QLabel(row)
        hint_label.setObjectName("lblThemeHint")
        hint_label.setText(_tr("界面外观主题"))
        self._theme_hint_label = hint_label
        label_layout.addWidget(hint_label)

        row_layout.addLayout(label_layout)

        # ── 中间弹性空间（透明背景，避免继承全局 QSS 背景色形成色块）──
        spacer = QWidget()
        spacer.setStyleSheet("background: transparent; border: none;")
        spacer.setSizePolicy(type(QWidget().sizePolicy()).Expanding, type(QWidget().sizePolicy()).Preferred)
        row_layout.addWidget(spacer)

        # ── 右侧主题选择下拉框 ──
        combo = QComboBox(row)
        combo.setObjectName("comboTheme")
        combo.setMinimumSize(140, 32)
        combo.setMaximumSize(160, 32)
        combo.addItem("🌙 深色模式", "dark")
        combo.addItem("☀️ 浅色模式", "light")
        self._theme_combo = combo
        row_layout.addWidget(combo)

        # ── 应用初始深色样式（apply_theme 会在首次主题切换时覆盖）──
        dc = DARK_COLORS
        row.setStyleSheet(
            f"QFrame#rowTheme {{"
            f"    background-color: {dc['input_bg']};"
            f"    border-bottom: 1px solid {dc['border_light']};"
            f"    padding: 16px 20px;"
            f"}}"
        )
        title_label.setStyleSheet(
            f"color: {dc['text_main']}; font-size: 14px; font-weight: 500;"
            f" background: transparent; border: none; padding: 0;"
        )
        hint_label.setStyleSheet(
            f"color: {dc['text_meta']}; font-size: 12px;"
            f" background: transparent; border: none; padding: 0;"
        )

        # 下拉框初始深色样式
        combo.setStyleSheet(
            f"QComboBox {{"
            f"    background-color: {dc['card_bg']};"
            f"    color: {dc['text_main']};"
            f"    border: 1px solid {dc['border_light']};"
            f"    border-radius: 8px;"
            f"    padding: 0 28px 0 12px;"
            f"    font-size: 13px;"
            f"}}"
            f"QComboBox::drop-down {{"
            f"    subcontrol-origin: padding;"
            f"    subcontrol-position: top right;"
            f"    width: 24px;"
            f"    border: none;"
            f"}}"
            f"QComboBox::down-arrow {{"
            f"    width: 0; height: 0;"
            f"    border: 5px solid transparent;"
            f"    border-top-color: {dc['text_sub']};"
            f"    margin-right: 4px;"
            f"}}"
        )

        # ── 插入到通用卡片 layout 的位置 1（语言行之后，开发者行之前）──
        if hasattr(self.ui, 'generalCardLayout'):
            self.ui.generalCardLayout.insertWidget(1, row)
        else:
            # 回退：附加到末尾
            if hasattr(self.ui, 'generalCardLayout'):
                self.ui.generalCardLayout.addWidget(row)

    def _connect_signals(self):
        self.ui.comboLanguage.currentIndexChanged.connect(self._on_language_changed)
        self.ui.chkDeveloperMode.stateChanged.connect(self._on_developer_mode_changed)
        self.ui.btnBrowseOutputDir.clicked.connect(self._on_browse_output_dir)
        self.ui.editSuffix.textChanged.connect(self._on_suffix_changed)
        self.ui.btnCheckUpdate.clicked.connect(self._on_check_update)
        self.ui.btnFeedback.clicked.connect(self._on_feedback)

        # 主题切换
        if self._theme_combo:
            self._theme_combo.currentIndexChanged.connect(self._on_theme_changed)

    def _load_settings(self):
        config = _read_config()

        saved_locale = config.get("language", "zh_CN")
        saved_index = INDEX_MAP.get(saved_locale, 0)
        self.ui.comboLanguage.setCurrentIndex(saved_index)

        if config.get("developer_mode", False):
            self.ui.chkDeveloperMode.setChecked(True)

        saved_policy = config.get("output_dir_policy", "input_dir")
        custom_dir = config.get("output_custom_dir", "")
        if saved_policy == "custom" and custom_dir:
            self.ui.editOutputDir.setText(custom_dir)
        else:
            self.ui.editOutputDir.clear()

        suffix = config.get("output_suffix", "_out")
        self.ui.editSuffix.setText(suffix)

        # 加载主题设置
        saved_theme = get_current_theme()
        if self._theme_combo:
            idx = 0 if saved_theme == "dark" else 1
            self._theme_combo.setCurrentIndex(idx)

    def set_theme_manager(self, theme_mgr):
        """由 run_main.py 调用，传入 ThemeManager 实例"""
        self._theme_mgr = theme_mgr

        # 注册此页面以接收 apply_theme 回调
        if theme_mgr:
            theme_mgr.register_page(self)

    def _on_theme_changed(self, index):
        theme = "dark" if index == 0 else "light"
        if self._theme_mgr:
            from PySide6.QtWidgets import QApplication
            self._theme_mgr.apply_theme(theme, QApplication.instance())

    def _on_language_changed(self, index):
        locale = LOCALE_MAP.get(index, "zh_CN")
        config = _read_config()
        config["language"] = locale
        _write_config(config)
        self.language_changed.emit(locale)

    def _on_developer_mode_changed(self, state):
        enabled = state == 2
        config = _read_config()
        config["developer_mode"] = enabled
        _write_config(config)
        self.developer_mode_changed.emit(enabled)

    def _on_browse_output_dir(self):
        directory = QFileDialog.getExistingDirectory(
            self,
            _tr("选择输出目录"),
            os.path.expanduser("~"),
        )
        if directory:
            self.ui.editOutputDir.setText(directory)
            config = _read_config()
            config["output_dir_policy"] = "custom"
            config["output_custom_dir"] = directory
            _write_config(config)
            self.output_dir_changed.emit(directory)

    def _on_suffix_changed(self, text):
        self._suffix_timer.start(800)

    def _save_suffix(self):
        config = _read_config()
        config["output_suffix"] = self.ui.editSuffix.text()
        _write_config(config)

    def _on_check_update(self):
        """打开 GitHub Releases 页面检查更新"""
        url = QUrl("https://github.com/jiuyue1024/PDflow-/releases")
        QDesktopServices.openUrl(url)

    def _on_feedback(self):
        pass

    # ── 主题回调 ──

    def apply_theme(self, colors):
        """
        ThemeManager 在主题切换时调用此方法。
        更新设置页面的内联样式以适应当前主题。
        """
        # 页面背景
        self.setStyleSheet(f"QWidget#settingsPage {{ background-color: {colors['bg']}; }}")

        # 滚动区域内容背景
        if hasattr(self.ui, 'scrollContent'):
            self.ui.scrollContent.setStyleSheet(
                f"QWidget#scrollContent {{ background-color: {colors['bg']}; }}"
            )

        # ── 卡片样式 ──
        card_style = (
            f"QFrame#{{name}} {{"
            f"    background-color: {colors['card_bg']};"
            f"    border: 1px solid {colors['border_light']};"
            f"    border-radius: 12px;"
            f"}}"
        )
        for card_name in ['generalCard', 'outputCard']:
            card = getattr(self.ui, card_name, None)
            if card:
                card.setStyleSheet(card_style.replace("{name}", card_name))

        if hasattr(self.ui, 'aboutCard'):
            self.ui.aboutCard.setStyleSheet(
                f"QFrame#aboutCard {{"
                f"    background-color: {colors['card_bg']};"
                f"    border: 1px solid {colors['border_light']};"
                f"    border-radius: 12px;"
                f"    padding: 20px 24px;"
                f"}}"
            )

        # ── 行容器样式 ──
        row_border_style = (
            f"QFrame#{{name}} {{"
            f"    background-color: {colors['input_bg']};"
            f"    border-bottom: 1px solid {colors['border_light']};"
            f"    padding: 16px 20px;"
            f"    border-top-left-radius: 12px;"
            f"    border-top-right-radius: 12px;"
            f"}}"
        )
        row_no_border_style = (
            f"QFrame#{{name}} {{"
            f"    background-color: {colors['input_bg']};"
            f"    padding: 16px 20px;"
            f"    border-bottom-left-radius: 12px;"
            f"    border-bottom-right-radius: 12px;"
            f"}}"
        )

        # 带底部边框的行（语言、输出目录、主题）
        for row_name in ['rowLanguage', 'rowOutputDir']:
            row = getattr(self.ui, row_name, None)
            if row:
                row.setStyleSheet(row_border_style.replace("{name}", row_name))

        # 无底部边框的行（开发者、后缀）
        for row_name in ['rowDeveloper', 'rowSuffix']:
            row = getattr(self.ui, row_name, None)
            if row:
                row.setStyleSheet(row_no_border_style.replace("{name}", row_name))

        # 主题行
        if self._theme_row:
            self._theme_row.setStyleSheet(
                f"QFrame#rowTheme {{"
                f"    background-color: {colors['input_bg']};"
                f"    border-bottom: 1px solid {colors['border_light']};"
                f"    padding: 16px 20px;"
                f"}}"
            )

        # ── 各行内的标签颜色 ──
        self._update_row_labels(colors)

        # ── 页面其他标签 ──
        self._update_page_labels(colors)

        # ── 输入框 ──
        input_style = (
            f"QLineEdit {{"
            f"    background-color: {colors['card_bg']};"
            f"    color: {colors['text_main']};"
            f"    border: 1px solid {colors['border_light']};"
            f"    border-radius: 8px;"
            f"    padding: 0 12px;"
            f"    font-size: 13px;"
            f"}}"
            f"QLineEdit:hover {{"
            f"    border: 1px solid {colors['border_hover']};"
            f"}}"
            f"QLineEdit:focus {{"
            f"    border: 1px solid {colors['primary']};"
            f"}}"
        )
        if hasattr(self.ui, 'editOutputDir'):
            self.ui.editOutputDir.setStyleSheet(input_style)
        if hasattr(self.ui, 'editSuffix'):
            self.ui.editSuffix.setStyleSheet(
                f"QLineEdit {{"
                f"    background-color: {colors['card_bg']};"
                f"    color: {colors['text_main']};"
                f"    border: 1px solid {colors['border_light']};"
                f"    border-radius: 8px;"
                f"    padding: 0 8px;"
                f"    font-size: 13px;"
                f"    font-family: monospace;"
                f"}}"
                f"QLineEdit:hover {{"
                f"    border: 1px solid {colors['border_hover']};"
                f"}}"
                f"QLineEdit:focus {{"
                f"    border: 1px solid {colors['primary']};"
                f"}}"
            )

        # ── 通用按钮样式（浏览、检查更新、反馈）──
        btn_style = (
            f"QPushButton {{"
            f"    background-color: {colors['card_bg']};"
            f"    color: {colors['text_sub']};"
            f"    border: 1px solid {colors['border_light']};"
            f"    border-radius: 8px;"
            f"    padding: 0 14px;"
            f"    font-size: 12px;"
            f"    font-weight: 500;"
            f"}}"
            f"QPushButton:hover {{"
            f"    border-color: {colors['border_hover']};"
            f"    color: {colors['text_main']};"
            f"}}"
        )
        for btn_name in ['btnBrowseOutputDir', 'btnCheckUpdate', 'btnFeedback']:
            btn = getattr(self.ui, btn_name, None)
            if btn:
                btn.setStyleSheet(
                    btn_style.replace("font-size: 12px", "font-size: 13px")
                    if btn_name == 'btnBrowseOutputDir' else btn_style
                )

        # ── 下拉框（语言 + 主题）──
        combo_style = self._build_combo_style(colors)
        if hasattr(self.ui, 'comboLanguage'):
            self.ui.comboLanguage.setStyleSheet(combo_style)
        if self._theme_combo:
            self._theme_combo.setStyleSheet(combo_style)

        # ── 图标容器 ──
        icon_container_style = (
            f"background: qlineargradient("
            f"    x1:0, y1:0, x2:1, y2:1,"
            f"    stop:0 {colors['primary']}, stop:1 #6B8FFF"
            f");"
            f"border-radius: 6px;"
            f"color: #FFFFFF;"
            f"font-size: 14px;"
        )
        if hasattr(self.ui, 'lblPageIcon'):
            self.ui.lblPageIcon.setStyleSheet(
                f"QLabel#lblPageIcon {{ {icon_container_style} }}"
            )
        if hasattr(self.ui, 'lblAboutIcon'):
            self.ui.lblAboutIcon.setStyleSheet(
                f"background: transparent; border-radius: 10px;"
            )

    def _update_row_labels(self, colors):
        """更新设置行容器内各标签的颜色"""
        row_pairs = [
            ('rowLanguage', 'lblLanguage', 'lblLanguageHint'),
            ('rowDeveloper', 'lblDeveloper', 'lblDeveloperHint'),
            ('rowOutputDir', 'lblOutputDir', 'lblOutputDirHint'),
            ('rowSuffix', 'lblSuffix', 'lblSuffixHint'),
        ]
        for row_name, title_name, hint_name in row_pairs:
            row = getattr(self.ui, row_name, None)
            if not row:
                continue
            for child in row.findChildren(QLabel):
                if child.objectName() == title_name:
                    child.setStyleSheet(
                        f"color: {colors['text_main']}; font-size: 14px; font-weight: 500;"
                        f" background: transparent; border: none; padding: 0;"
                    )
                elif child.objectName() == hint_name or child.objectName() == 'lblSuffixExt':
                    child.setStyleSheet(
                        f"color: {colors['text_meta']}; font-size: 12px;"
                        f" background: transparent; border: none; padding: 0;"
                    )

        # 主题行标签
        if self._theme_title_label:
            self._theme_title_label.setStyleSheet(
                f"color: {colors['text_main']}; font-size: 14px; font-weight: 500;"
                f" background: transparent; border: none; padding: 0;"
            )
        if self._theme_hint_label:
            self._theme_hint_label.setStyleSheet(
                f"color: {colors['text_meta']}; font-size: 12px;"
                f" background: transparent; border: none; padding: 0;"
            )

    def _update_page_labels(self, colors):
        """更新页面内非行内标签的颜色"""
        label_map = {
            'lblPageTitle': (
                f"color: {colors['text_main']}; font-size: 24px; font-weight: 700;"
                f" background: transparent; border: none; padding: 0; letter-spacing: -1px;"
            ),
            'lblSectionGeneral': (
                f"color: {colors['text_meta']}; font-size: 12px; font-weight: 600;"
                f" background: transparent; border: none; padding: 0; letter-spacing: 0.8px;"
            ),
            'lblSectionOutput': (
                f"color: {colors['text_meta']}; font-size: 12px; font-weight: 600;"
                f" background: transparent; border: none; padding: 0; letter-spacing: 0.8px;"
            ),
            'lblSectionAbout': (
                f"color: {colors['text_meta']}; font-size: 12px; font-weight: 600;"
                f" background: transparent; border: none; padding: 0; letter-spacing: 0.8px;"
            ),
            'lblAppName': (
                f"color: {colors['text_main']}; font-size: 15px; font-weight: 700;"
                f" background: transparent; border: none; padding: 0;"
            ),
            'lblAppVersion': (
                f"color: {colors['text_sub']}; font-size: 12px;"
                f" background: transparent; border: none; padding: 0;"
            ),
            'lblAppDesc': (
                f"color: {colors['text_meta']}; font-size: 11px;"
                f" background: transparent; border: none; padding: 0;"
            ),
            'lblFooterHint': (
                f"color: {colors['text_muted']}; font-size: 11px;"
                f" background: transparent; border: none; padding: 8px 0;"
            ),
        }
        for obj_name, style in label_map.items():
            label = getattr(self.ui, obj_name, None)
            if label and hasattr(label, 'setStyleSheet'):
                label.setStyleSheet(style)

    def _build_combo_style(self, colors):
        """构建 QComboBox 样式字符串"""
        return (
            f"QComboBox {{"
            f"    background-color: {colors['card_bg']};"
            f"    color: {colors['text_main']};"
            f"    border: 1px solid {colors['border_light']};"
            f"    border-radius: 8px;"
            f"    padding: 0 28px 0 12px;"
            f"    font-size: 13px;"
            f"}}"
            f"QComboBox:hover {{"
            f"    border: 1px solid {colors['border_hover']};"
            f"}}"
            f"QComboBox::drop-down {{"
            f"    subcontrol-origin: padding;"
            f"    subcontrol-position: top right;"
            f"    width: 24px;"
            f"    border: none;"
            f"}}"
            f"QComboBox::down-arrow {{"
            f"    width: 0; height: 0;"
            f"    border: 5px solid transparent;"
            f"    border-top-color: {colors['text_sub']};"
            f"    margin-right: 4px;"
            f"}}"
            f"QComboBox QAbstractItemView {{"
            f"    background-color: {colors['menu_bg']};"
            f"    color: {colors['text_main']};"
            f"    border: 1px solid {colors['border']};"
            f"    border-radius: 8px;"
            f"    selection-background-color: {colors['hover_bg']};"
            f"    selection-color: {colors['primary']};"
            f"    padding: 4px;"
            f"    outline: none;"
            f"}}"
            f"QComboBox QAbstractItemView::item {{"
            f"    min-height: 28px;"
            f"    padding: 4px 10px;"
            f"    border-radius: 4px;"
            f"}}"
            f"QComboBox QAbstractItemView::item:hover {{"
            f"    background-color: {colors['hover_bg']};"
            f"    color: {colors['primary']};"
            f"}}"
        )

    def retranslateUi(self):
        self.ui.lblPageTitle.setText(_tr("设置"))
        self.ui.lblSectionGeneral.setText(_tr("通用"))
        self.ui.lblLanguage.setText(_tr("语言"))
        self.ui.lblLanguageHint.setText(_tr("界面显示语言"))
        self.ui.comboLanguage.setItemText(0, _tr("简体中文"))
        self.ui.comboLanguage.setItemText(1, _tr("繁體中文"))
        self.ui.comboLanguage.setItemText(2, _tr("English"))
        self.ui.lblDeveloper.setText(_tr("开发者模式"))
        self.ui.lblDeveloperHint.setText(_tr("显示「速文创作」等实验性功能"))
        self.ui.lblSectionOutput.setText(_tr("输出"))
        self.ui.lblOutputDir.setText(_tr("默认输出目录"))
        self.ui.lblOutputDirHint.setText(_tr("处理后的文件默认保存位置"))
        self.ui.editOutputDir.setPlaceholderText(_tr("输入文件所在目录"))
        self.ui.btnBrowseOutputDir.setText(_tr("浏览..."))
        self.ui.lblSuffix.setText(_tr("文件名后缀"))
        self.ui.lblSuffixHint.setText(_tr("自动为输出文件添加后缀名"))
        self.ui.lblSuffixExt.setText(_tr("+ 扩展名"))
        self.ui.lblSectionAbout.setText(_tr("关于"))
        self.ui.lblAppName.setText(_tr("印流PDflow"))
        self.ui.lblAppDesc.setText(_tr("设计师专用的轻量级 PDF 工具箱"))
        self.ui.btnCheckUpdate.setText(_tr("检查更新"))
        self.ui.btnFeedback.setText(_tr("反馈"))
        self.ui.lblFooterHint.setText(_tr("设置修改后自动保存 · 语言切换需重启生效"))

        # 主题行 i18n
        if self._theme_title_label:
            self._theme_title_label.setText(_tr("主题"))
        if self._theme_hint_label:
            self._theme_hint_label.setText(_tr("界面外观主题"))

        self._set_icons()
