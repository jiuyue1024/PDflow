# -*- coding: utf-8 -*-
"""
template_layout_page.py — 模板排版入口页面
从 assets/templates/ 动态加载 JSON 模板并以卡片网格展示
点击卡片弹出 QDialog 确认进入编辑模式
"""
import sys
import os
import json

from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QScrollArea,
    QDialog, QSizePolicy, QSpacerItem,
)
from PySide6.QtGui import QFont

from src.common.paths import resource_path
from translations.translation_manager import _ as _tr


PROJECT_ROOT = resource_path()
TEMPLATES_DIR = os.path.join("assets", "templates")
TEMPLATES_PATH = os.path.join(PROJECT_ROOT, TEMPLATES_DIR)


# ================================================================
# Ui_TemplateLayoutPage — 与 .ui 文件对应的 UI 类
# ================================================================
class Ui_TemplateLayoutPage(object):
    """与 .ui 文件对应的 UI 类，供 TemplateLayoutPage 调用 setupUi"""

    def setupUi(self, TemplateLayoutPage):
        if not TemplateLayoutPage.objectName():
            TemplateLayoutPage.setObjectName("TemplateLayoutPage")
        TemplateLayoutPage.resize(1280, 820)
        TemplateLayoutPage.setMinimumSize(QSize(960, 600))
        TemplateLayoutPage.setStyleSheet(
            "QWidget#TemplateLayoutPage {\n"
            "    background-color: #0A0A0F;\n"
            "}\n"
        )

        self.mainLayout = QVBoxLayout(TemplateLayoutPage)
        self.mainLayout.setSpacing(16)
        self.mainLayout.setContentsMargins(24, 24, 24, 24)

        # 顶部标题
        self.pageTitle = QLabel("模板排版")
        self.pageTitle.setObjectName("pageTitle")
        self.pageTitle.setStyleSheet(
            "color: #EAECEF; font-size: 24px; font-weight: 700;"
        )
        self.mainLayout.addWidget(self.pageTitle)

        # 滚动区域
        self.templateScrollArea = QScrollArea()
        self.templateScrollArea.setObjectName("templateScrollArea")
        self.templateScrollArea.setWidgetResizable(True)
        self.templateScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.templateScrollArea.setStyleSheet(
            "QScrollArea#templateScrollArea { background-color: transparent; border: none; }\n"
            "QScrollArea#templateScrollArea > QWidget > QWidget { background-color: transparent; }\n"
            "QScrollArea#templateScrollArea QScrollBar:vertical {\n"
            "    background-color: #0A0A0F; width: 8px; border-radius: 4px;\n"
            "}\n"
            "QScrollArea#templateScrollArea QScrollBar::handle:vertical {\n"
            "    background-color: #1E1E28; border-radius: 4px; min-height: 40px;\n"
            "}\n"
            "QScrollArea#templateScrollArea QScrollBar::handle:vertical:hover {\n"
            "    background-color: #2B3139;\n"
            "}"
        )

        self.scrollContent = QWidget()
        self.scrollContent.setObjectName("scrollContent")
        self.scrollContent.setStyleSheet("QWidget#scrollContent { background-color: transparent; }")
        self.scrollContentLayout = QVBoxLayout(self.scrollContent)
        self.scrollContentLayout.setSpacing(16)
        self.scrollContentLayout.setContentsMargins(0, 0, 0, 0)

        # 空状态提示（默认隐藏）
        self.emptyHint = QLabel("暂无可用模板\n请在 assets/templates/ 目录中添加 JSON 模板文件")
        self.emptyHint.setObjectName("emptyHint")
        self.emptyHint.setAlignment(Qt.AlignCenter)
        self.emptyHint.setWordWrap(True)
        self.emptyHint.setStyleSheet("color: #4A4B56; font-size: 15px;")
        self.emptyHint.setMinimumHeight(200)
        self.emptyHint.setVisible(False)
        self.scrollContentLayout.addWidget(self.emptyHint)

        # 模板网格容器
        self.templateGridWidget = QWidget()
        self.templateGridWidget.setObjectName("templateGridWidget")
        self.templateGridLayout = QVBoxLayout(self.templateGridWidget)
        self.templateGridLayout.setSpacing(16)
        self.templateGridLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollContentLayout.addWidget(self.templateGridWidget)

        # 底部弹性空间
        self.scrollBottomSpacer = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.scrollContentLayout.addItem(self.scrollBottomSpacer)

        self.templateScrollArea.setWidget(self.scrollContent)
        self.mainLayout.addWidget(self.templateScrollArea, stretch=1)

        # 底部状态文字
        self.footerLabel = QLabel("共 0 个可用模板")
        self.footerLabel.setObjectName("footerLabel")
        self.footerLabel.setAlignment(Qt.AlignCenter)
        self.footerLabel.setStyleSheet("color: #848E9C; font-size: 13px;")
        self.mainLayout.addWidget(self.footerLabel)

    def retranslateUi(self, TemplateLayoutPage):
        self.pageTitle.setText(_tr("模板排版"))
        self.emptyHint.setText(_tr("暂无可用模板\n请在 assets/templates/ 目录中添加 JSON 模板文件"))
        self.footerLabel.setText(_tr("共 0 个可用模板"))


# ================================================================
# TemplateEntryDialog — 点击卡片的确认弹窗
# ================================================================
class TemplateEntryDialog(QDialog):
    """点击模板卡片后的确认弹窗"""

    def __init__(self, template_name, parent=None, theme_colors=None):
        super().__init__(parent)
        self.setWindowTitle(_tr("进入模板编辑"))
        self.setFixedSize(400, 180)

        # 如果未传入主题色，使用默认深色
        if theme_colors is None:
            theme_colors = {
                "bg": "#0B0E11",
                "card_bg": "#14141A",
                "border": "#1E1E28",
                "border_light": "#1E1E28",
                "text_main": "#EAECEF",
                "text_sub": "#848E9C",
                "text_muted": "#4A4B56",
                "primary": "#4D7CFE",
                "input_bg": "#0A0A0F",
            }

        self.setStyleSheet(
            f"QDialog {{\n"
            f"    background-color: {theme_colors['card_bg']};\n"
            f"    border: 1px solid {theme_colors['border']};\n"
            f"    border-radius: 12px;\n"
            f"}}"
        )
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)

        # 提示文字
        prompt = QLabel(_tr("即将进入编辑模式：「{}」").format(template_name))
        prompt.setAlignment(Qt.AlignCenter)
        prompt.setWordWrap(True)
        prompt.setStyleSheet(
            f"color: {theme_colors['text_main']}; font-size: 15px; font-weight: 500;"
        )
        layout.addWidget(prompt)

        # 按钮行
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(16)

        cancel_btn = QPushButton(_tr("取消"))
        cancel_btn.setObjectName("dialogCancelBtn")
        cancel_btn.setStyleSheet(
            f"QPushButton#dialogCancelBtn {{\n"
            f"    background-color: {theme_colors['input_bg']};\n"
            f"    color: {theme_colors['text_main']};\n"
            f"    border: 1px solid {theme_colors['border']};\n"
            f"    border-radius: 6px;\n"
            f"    font-size: 14px;\n"
            f"    padding: 8px 24px;\n"
            f"    min-height: 36px;\n"
            f"}}\n"
            f"QPushButton#dialogCancelBtn:hover {{\n"
            f"    background-color: {theme_colors['hover_bg'] if 'hover_bg' in theme_colors else '#1E2330'};\n"
            f"}}"
        )
        cancel_btn.clicked.connect(self.reject)

        start_btn = QPushButton(_tr("开始编辑"))
        start_btn.setObjectName("dialogStartBtn")
        start_btn.setStyleSheet(
            f"QPushButton#dialogStartBtn {{\n"
            f"    background-color: {theme_colors['primary']};\n"
            f"    color: #FFFFFF;\n"
            f"    border: none;\n"
            f"    border-radius: 6px;\n"
            f"    font-size: 14px;\n"
            f"    font-weight: 500;\n"
            f"    padding: 8px 24px;\n"
            f"    min-height: 36px;\n"
            f"}}\n"
            f"QPushButton#dialogStartBtn:hover {{\n"
            f"    background-color: #3D6CF0;\n"
            f"}}\n"
            f"QPushButton#dialogStartBtn:pressed {{\n"
            f"    background-color: #3560E0;\n"
            f"}}"
        )
        start_btn.clicked.connect(self.accept)

        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(start_btn)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)


# ================================================================
# TemplateLayoutPage — 主页面
# ================================================================
class TemplateLayoutPage(QWidget):
    """模板排版入口页面：以卡片网格展示可用模板"""

    editor_requested = Signal(str)    # 请求打开编辑器，参数为 template_id

    def __init__(self):
        super().__init__()
        self._templates = []  # 存储加载的模板数据

        # 加载 UI
        self.ui = Ui_TemplateLayoutPage()
        self.ui.setupUi(self)

        # 加载模板列表
        self.load_templates()

    # ── 模板加载与卡片 ──
    def load_templates(self):
        """从 assets/templates/ 加载 JSON 模板文件并生成卡片"""
        self._templates = []

        if not os.path.isdir(TEMPLATES_PATH):
            self._show_empty_state()
            return

        # 扫描 JSON 文件
        json_files = sorted([
            f for f in os.listdir(TEMPLATES_PATH)
            if f.endswith(".json")
        ])

        if not json_files:
            self._show_empty_state()
            return

        for filename in json_files:
            try:
                filepath = os.path.join(TEMPLATES_PATH, filename)
                with open(filepath, encoding="utf-8") as f:
                    data = json.load(f)
                self._templates.append(data)
            except (json.JSONDecodeError, IOError) as e:
                print(f"[模板排版] 加载失败: {filename} — {e}")

        if not self._templates:
            self._show_empty_state()
            return

        self._build_card_grid()
        self.ui.footerLabel.setText(_tr("共 {} 个可用模板").format(len(self._templates)))

    def _show_empty_state(self):
        """模板目录为空或无有效模板时显示友好提示"""
        self.ui.templateGridWidget.setVisible(False)
        self.ui.emptyHint.setVisible(True)
        self.ui.footerLabel.setText(_tr("共 0 个可用模板"))

    def _build_card_grid(self):
        """构建 3 列卡片网格"""
        self.ui.emptyHint.setVisible(False)
        self.ui.templateGridWidget.setVisible(True)

        # 清除旧的网格内容
        self._clear_layout(self.ui.templateGridLayout)

        # 每行 3 列
        cols = 3
        for i in range(0, len(self._templates), cols):
            row_templates = self._templates[i:i + cols]
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setSpacing(16)
            row_layout.setContentsMargins(0, 0, 0, 0)

            for tpl in row_templates:
                card = self._create_card(tpl)
                row_layout.addWidget(card, stretch=1)

            # 补充空白占位
            remaining = cols - len(row_templates)
            for _ in range(remaining):
                spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
                row_layout.addItem(spacer)

            self.ui.templateGridLayout.addWidget(row_widget)

    def _create_card(self, template_data):
        """创建单个模板卡片"""
        card = QFrame()
        card.setObjectName("card")
        card.setMinimumSize(QSize(320, 180))
        card.setMaximumSize(QSize(480, 220))
        card.setStyleSheet(
            "QFrame#card {\n"
            "    background-color: #14141A;\n"
            "    border: 1px solid #1E1E28;\n"
            "    border-radius: 8px;\n"
            "}\n"
            "QFrame#card:hover {\n"
            "    background-color: #1A1A22;\n"
            "    border: 1px solid #4D7CFE;\n"
            "}"
        )
        card.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout(card)
        layout.setSpacing(8)
        layout.setContentsMargins(20, 20, 20, 20)

        # 图标占位（背景透明）
        icon = template_data.get("icon", "📄")
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("background-color: transparent; font-size: 36px;")
        layout.addWidget(icon_label)

        # 模板名称（背景透明）
        name = template_data.get("name", _tr("未命名模板"))
        name_label = QLabel(name)
        name_label.setStyleSheet(
            "background-color: transparent; color: #EAECEF; font-size: 15px; font-weight: 600;"
        )
        layout.addWidget(name_label)

        # 描述（背景透明）
        desc = template_data.get("description", "")
        desc_label = QLabel(desc)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet(
            "background-color: transparent; color: #848E9C; font-size: 12px;"
        )
        layout.addWidget(desc_label)

        layout.addStretch()

        # 底部行：类型标签 + 预览按钮
        bottom_row = QWidget()
        bottom_row.setStyleSheet("background: transparent;")
        bottom_layout = QHBoxLayout(bottom_row)
        bottom_layout.setSpacing(8)
        bottom_layout.setContentsMargins(0, 0, 0, 0)

        tpl_type = template_data.get("type", "通用")
        type_label = QLabel(tpl_type)
        type_label.setStyleSheet(
            "background-color: rgba(77, 124, 254, 0.12);\n"
            "color: #4D7CFE;\n"
            "font-size: 11px;\n"
            "font-weight: 500;\n"
            "padding: 3px 10px;\n"
            "border-radius: 4px;"
        )
        type_label.setFixedHeight(22)
        type_label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        bottom_layout.addWidget(type_label)

        bottom_layout.addStretch()

        layout.addWidget(bottom_row)

        # 绑定主题更新方法到卡片
        card._name_label = name_label
        card._desc_label = desc_label
        card._type_label = type_label

        def _apply_card_theme(colors):
            card.setStyleSheet(
                f"QFrame#card {{\n"
                f"    background-color: {colors['card_bg']};\n"
                f"    border: 1px solid {colors['border']};\n"
                f"    border-radius: 8px;\n"
                f"}}\n"
                f"QFrame#card:hover {{\n"
                f"    background-color: {colors['hover_bg']};\n"
                f"    border: 1px solid {colors['primary']};\n"
                f"}}"
            )
            name_label.setStyleSheet(
                f"background-color: transparent; color: {colors['card_title']}; font-size: 15px; font-weight: 600;"
            )
            desc_label.setStyleSheet(
                f"background-color: transparent; color: {colors['card_desc']}; font-size: 12px;"
            )
            type_label.setStyleSheet(
                f"background-color: {colors['primary_light_12']};\n"
                f"color: {colors['primary']};\n"
                f"font-size: 11px;\n"
                f"font-weight: 500;\n"
                f"padding: 3px 10px;\n"
                f"border-radius: 4px;"
            )

        card._apply_card_theme = _apply_card_theme

        # 绑定点击事件（按钮自身吃掉 click，不触发卡片整体点击）
        name_str = name
        card.mousePressEvent = lambda event, n=name_str: self._on_card_clicked(n)

        return card

    def _on_card_clicked(self, template_name):
        """卡片点击：弹出确认对话框，确认后进入编辑界面"""
        dialog = TemplateEntryDialog(template_name, self, getattr(self, '_theme_colors', None))
        result = dialog.exec()

        if result == QDialog.Accepted:
            template_id = self._name_to_id(template_name)
            if template_id:
                self.editor_requested.emit(template_id)

    def _name_to_id(self, name: str) -> str:
        """根据模板名称查找 template_id"""
        for t in self._templates:
            if t.get("name") == name:
                return t.get("id", "")
        return ""

    @staticmethod
    def _clear_layout(layout):
        """递归清空布局中的所有子控件和子布局"""
        if layout is None:
            return
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                TemplateLayoutPage._clear_layout(item.layout())

    def refresh_style(self):
        """重新加载样式（遵循 watermark_page.py 的 refresh_style 模式）"""
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def retranslateUi(self):
        """语言切换时由 TranslationManager 调用"""
        self.ui.retranslateUi(self)
        count = len(self._templates)
        if count > 0:
            self.ui.footerLabel.setText(_tr("共 {} 个可用模板").format(count))
        if self._templates:
            self._build_card_grid()

    def apply_theme(self, colors):
        """ThemeManager 主题切换时更新页面内联样式"""
        self._theme_colors = colors
        # 页面背景
        self.setStyleSheet(
            f"TemplateLayoutPage {{\n"
            f"    background-color: {colors['bg']};\n"
            f"}}\n"
        )
        # 标题
        self.ui.pageTitle.setStyleSheet(
            f"color: {colors['text_main']}; font-size: 24px; font-weight: 700;"
        )
        # 滚动区域
        self.ui.templateScrollArea.setStyleSheet(
            f"QScrollArea#templateScrollArea {{ background-color: transparent; border: none; }}\n"
            f"QScrollArea#templateScrollArea > QWidget > QWidget {{ background-color: transparent; }}\n"
            f"QScrollArea#templateScrollArea QScrollBar:vertical {{\n"
            f"    background-color: {colors['bg']}; width: 8px; border-radius: 4px;\n"
            f"}}\n"
            f"QScrollArea#templateScrollArea QScrollBar::handle:vertical {{\n"
            f"    background-color: {colors['scrollbar_bg']}; border-radius: 4px; min-height: 40px;\n"
            f"}}\n"
            f"QScrollArea#templateScrollArea QScrollBar::handle:vertical:hover {{\n"
            f"    background-color: {colors['scrollbar_hover']};\n"
            f"}}"
        )
        # 空状态提示
        self.ui.emptyHint.setStyleSheet(
            f"color: {colors['text_muted']}; font-size: 15px;"
        )
        # 底部状态文字
        self.ui.footerLabel.setStyleSheet(
            f"color: {colors['text_sub']}; font-size: 13px;"
        )
        # 更新已创建的卡片
        self._apply_card_themes(colors)

    def _apply_card_themes(self, colors):
        """更新所有模板卡片的内联样式"""
        for i in range(self.ui.templateGridLayout.count()):
            row_widget = self.ui.templateGridLayout.itemAt(i).widget()
            if not row_widget:
                continue
            for j in range(row_widget.layout().count()):
                item = row_widget.layout().itemAt(j)
                if item and item.widget() and hasattr(item.widget(), '_apply_card_theme'):
                    item.widget()._apply_card_theme(colors)
