import os
import tempfile

from PySide6.QtCore import (
    Qt, QSize, Signal, QPropertyAnimation,
    QEasingCurve, QTimer, QRect, QPoint, QPointF,
    QParallelAnimationGroup, QVariantAnimation,
)
from PySide6.QtGui import (
    QPainter, QBrush, QColor, QPen, QPainterPath,
    QRadialGradient, QLinearGradient, QFont,
)
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QScrollArea,
    QSizePolicy, QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect, QMessageBox,
)
from src.common.recent_files_manager import get_recent_files, get_status_text, clear_records
from translations.translation_manager import _ as _tr


# ================================================================
# 辅助组件
# ================================================================
class Badge(QFrame):
    """版本徽章：左侧绿色脉冲圆点 + 文字"""

    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        self.setObjectName("badge")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        layout = QHBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(10, 5, 10, 5)
        dot = QLabel()
        dot.setFixedSize(5, 5)
        dot.setStyleSheet(
            "QLabel {"
            "    background-color: #34C759;"
            "    border-radius: 3px;"
            "}"
        )
        layout.addWidget(dot)
        self.label = QLabel(text)
        self.label.setStyleSheet("color: #4D7CFE; font-size: 12px; font-weight: 600;")
        layout.addWidget(self.label)
        self.setStyleSheet(
            "QFrame#badge {\n"
            "    background: rgba(77, 124, 254, 20);\n"
            "    border: 1px solid rgba(77, 124, 254, 38);\n"
            "    border-radius: 12px;\n"
            "}\n"
        )

    def setText(self, text: str):
        self.label.setText(text)


class Glow(QWidget):
    """径向渐变光晕装饰（背景层）"""

    def __init__(self, color=QColor(77, 124, 254), radius=200, alpha=8, parent=None):
        super().__init__(parent)
        self._color = color
        self._alpha = alpha
        self._radius = radius
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setFixedSize(radius * 2, radius * 2)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        gradient = QRadialGradient(
            QPointF(self._radius, self._radius), self._radius
        )
        gradient.setColorAt(0.0, QColor(self._color.red(), self._color.green(), self._color.blue(), self._alpha))
        gradient.setColorAt(1.0, QColor(self._color.red(), self._color.green(), self._color.blue(), 0))
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, self._radius * 2, self._radius * 2)


class AccentStrip(QFrame):
    """左上角装饰色条，悬停时从 14px 延伸到 24px"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("accentStrip")
        self.setFixedWidth(3)
        self._default_height = 14
        self.setMinimumHeight(self._default_height)
        self.setMaximumHeight(self._default_height)
        self.setStyleSheet(
            "QFrame#accentStrip {\n"
            "    background-color: #4D7CFE;\n"
            "}\n"
        )
        self._anim = QPropertyAnimation(self, b"minimumHeight")
        self._anim.setDuration(300)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)

    def extend(self, to_height: int):
        self.setMaximumHeight(to_height)
        self._anim.setEndValue(to_height)
        self._anim.start()


# ================================================================
# FunctionCard - 功能卡片（纯 QSS，无 paintEvent）
# ================================================================
class FunctionCard(QFrame):
    """
    功能卡片：
      - 半透明背景 + 边框（纯 QSS）
      - 左上角装饰色条
      - 48px 图标 + 渐变背景
      - hover：边框变色 + 色条延伸
      - 入场：opacity 0→1 + translateY 24→0（stagger 延迟）
    """

    card_clicked = Signal(str)

    def __init__(self, icon: str, title: str, desc: str,
                 icon_color: str = "#4D7CFE",
                 card_name: str = "", parent=None):
        super().__init__(parent)
        self.card_name = card_name
        self.setObjectName("funcCard")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setCursor(Qt.PointingHandCursor)
        self._is_hovered = False
        self._theme_colors = None  # 主题色缓存，hover 时用于主题感知

        self.setMinimumHeight(180)
        self.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Fixed
        )

        # 入场动画属性
        self._opacity = 0.0
        self._offset_y = 24

        card_layout = QVBoxLayout(self)
        card_layout.setSpacing(0)
        card_layout.setContentsMargins(0, 0, 0, 0)

        # 色条区域
        strip_holder = QWidget()
        strip_holder.setObjectName("stripHolder")
        strip_holder.setFixedHeight(28)
        strip_holder.setAttribute(Qt.WA_TransparentForMouseEvents)
        strip_holder.setStyleSheet(
            "QWidget#stripHolder {"
            "    background: transparent;"
            "    border: none;"
            "}"
        )
        strip_layout = QHBoxLayout(strip_holder)
        strip_layout.setSpacing(0)
        strip_layout.setContentsMargins(0, 0, 0, 0)
        self.accent_strip = AccentStrip(strip_holder)
        self.accent_strip.setAttribute(Qt.WA_TransparentForMouseEvents)
        strip_layout.addWidget(self.accent_strip)
        strip_layout.addStretch()
        card_layout.addWidget(strip_holder)

        # 内容区
        content = QVBoxLayout()
        content.setSpacing(0)
        content.setContentsMargins(24, 4, 24, 24)
        content.setAlignment(Qt.AlignCenter)

        # 图标容器
        icon_frame = QFrame()
        icon_frame.setObjectName("cardIconFrame")
        icon_frame.setFixedSize(48, 48)
        icon_frame.setAttribute(Qt.WA_TransparentForMouseEvents)
        icon_frame.setStyleSheet(
            "QFrame#cardIconFrame {\n"
            "    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,\n"
            "        stop:0 rgba(77,124,254,31),\n"
            "        stop:1 rgba(77,124,254,10));\n"
            "    border: 1px solid rgba(77,124,254,26);\n"
            "    border-radius: 8px;\n"
            "}\n"
        )
        icon_layout = QHBoxLayout(icon_frame)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setAlignment(Qt.AlignCenter)
        icon_label = QLabel(icon)
        icon_label.setObjectName("cardIcon")
        icon_label.setAttribute(Qt.WA_TransparentForMouseEvents)
        icon_label.setStyleSheet(f"color: {icon_color}; font-size: 24px;")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_layout.addWidget(icon_label)

        content.addWidget(icon_frame, 0, Qt.AlignCenter)
        content.addSpacing(18)

        # 标题
        self.title_label = QLabel(title)
        self.title_label.setObjectName("cardTitle")
        self.title_label.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.title_label.setStyleSheet(
            "color: #EAECEF; font-size: 15px; font-weight: 600;"
        )
        self.title_label.setAlignment(Qt.AlignCenter)
        content.addWidget(self.title_label)
        content.addSpacing(6)

        # 描述
        self.desc_label = QLabel(desc)
        self.desc_label.setObjectName("cardDesc")
        self.desc_label.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.desc_label.setStyleSheet(
            "color: #8B8D98; font-size: 12px;"
        )
        self.desc_label.setAlignment(Qt.AlignCenter)
        self.desc_label.setWordWrap(True)
        content.addWidget(self.desc_label)

        card_layout.addLayout(content)

        # 默认样式（纯 QSS）
        self._update_style(False)

    def _update_style(self, hover: bool, colors: dict = None):
        if colors:
            bg = colors['func_card_hover_qss'] if hover else colors['func_card_bg_qss']
            border = colors['func_card_border_hover_qss'] if hover else colors['white_13_qss']
        else:
            # 回退硬编码深色值（初始加载时使用）
            if hover:
                bg = "rgba(30, 34, 40, 204)"
                border = "rgba(77, 124, 254, 64)"
            else:
                bg = "rgba(16, 18, 24, 184)"
                border = "rgba(255, 255, 255, 13)"
        self.setStyleSheet(
            f"QFrame#funcCard {{\n"
            f"    background: {bg};\n"
            f"    border: 1px solid {border};\n"
            f"    border-radius: 16px;\n"
            f"}}\n"
        )

    def apply_theme(self, colors):
        """主题切换时更新卡片内联样式"""
        self._theme_colors = colors
        # 更新卡片背景（保存当前 hover 状态）
        if self._is_hovered:
            bg = colors['func_card_hover_qss']
            border = colors['func_card_border_hover_qss']
        else:
            bg = colors['func_card_bg_qss']
            border = colors['white_13_qss']
        self.setStyleSheet(
            f"QFrame#funcCard {{\n"
            f"    background: {bg};\n"
            f"    border: 1px solid {border};\n"
            f"    border-radius: 16px;\n"
            f"}}\n"
        )
        # 更新图标容器
        icon_frame = self.findChild(QFrame, "cardIconFrame")
        if icon_frame:
            icon_frame.setStyleSheet(
                f"QFrame#cardIconFrame {{\n"
                f"    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,\n"
                f"        stop:0 {colors['gradient_start_qss']},\n"
                f"        stop:1 {colors['gradient_end_qss']});\n"
                f"    border: 1px solid {colors['gradient_border_qss']};\n"
                f"    border-radius: 8px;\n"
                f"}}\n"
            )
        # 更新标题
        if self.title_label:
            self.title_label.setStyleSheet(
                f"color: {colors['card_title']}; font-size: 15px; font-weight: 600;"
            )
        # 更新描述
        if self.desc_label:
            self.desc_label.setStyleSheet(
                f"color: {colors['text_sub']}; font-size: 12px;"
            )

    def enterEvent(self, event):
        self._is_hovered = True
        if self._theme_colors:
            self._update_style(True, self._theme_colors)
        else:
            self._update_style(True)
        self.accent_strip.extend(24)
        self.update()

    def leaveEvent(self, event):
        self._is_hovered = False
        if self._theme_colors:
            self._update_style(False, self._theme_colors)
        else:
            self._update_style(False)
        self.accent_strip.extend(14)
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.card_clicked.emit(self.card_name)
        super().mousePressEvent(event)

    def start_stagger_animation(self, delay_ms: int):
        """启动入场动画（stagger延迟 + fadeUp）"""
        QTimer.singleShot(delay_ms, lambda: self._run_fade_up())

    def _run_fade_up(self):
        """执行 fade-up 动画：opacity 0→1, offset_y 24→0, 500ms"""
        self._opacity = 0.0
        self._offset_y = 24
        self.update()

        def _start():
            op_anim = QVariantAnimation()
            op_anim.setStartValue(0.0)
            op_anim.setEndValue(1.0)
            op_anim.setDuration(500)
            op_anim.setEasingCurve(QEasingCurve.OutCubic)
            op_anim.valueChanged.connect(self._on_card_opacity_changed)
            op_anim.start()

            offset_anim = QVariantAnimation()
            offset_anim.setStartValue(24.0)
            offset_anim.setEndValue(0.0)
            offset_anim.setDuration(500)
            offset_anim.setEasingCurve(QEasingCurve.OutCubic)
            offset_anim.valueChanged.connect(self._on_card_offset_changed)
            offset_anim.start()

            self._card_fade_anims = [op_anim, offset_anim]

        QTimer.singleShot(0, _start)

    def _on_card_opacity_changed(self, val):
        self._opacity = val
        self.update()

    def _on_card_offset_changed(self, val):
        self._offset_y = val
        self.update()


# ================================================================
# 文件列表项
# ================================================================
class FileItem(QFrame):
    """最近文件列表中的单个文件项"""

    file_clicked = Signal(str, str)

    def __init__(self, filename: str, meta: str, status: str,
                 file_path: str = "", action: str = "",
                 is_red: bool = False, parent=None):
        super().__init__(parent)
        self._file_path = file_path
        self._action = action
        self._is_red = is_red
        self.setObjectName("fileItem")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setFixedHeight(56)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(
            "QFrame#fileItem {\n"
            "    background: transparent;\n"
            "    border: none;\n"
            "    border-radius: 6px;\n"
            "}\n"
            "QFrame#fileItem:hover {\n"
            "    background: rgba(255,255,255,8);\n"
            "}\n"
        )

        layout = QHBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(12, 8, 12, 8)

        # PDF 图标（极简：圆角方块 + PDF 文字）
        self.pdf_icon = QFrame()
        self.pdf_icon.setObjectName("pdfIcon")
        self.pdf_icon.setFixedSize(32, 40)

        if is_red:
            self.pdf_icon.setStyleSheet(
                "QFrame#pdfIcon {\n"
                "    background: rgba(255,59,48,8);\n"
                "    border: 1px solid rgba(255,59,48,10);\n"
                "    border-radius: 4px;\n"
                "}\n"
            )
            text_color = "#FF3B30"
        else:
            self.pdf_icon.setStyleSheet(
                "QFrame#pdfIcon {\n"
                "    background: rgba(77,124,254,8);\n"
                "    border: 1px solid rgba(77,124,254,10);\n"
                "    border-radius: 4px;\n"
                "}\n"
            )
            text_color = "#4D7CFE"

        icon_layout = QVBoxLayout(self.pdf_icon)
        icon_layout.setSpacing(0)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setAlignment(Qt.AlignCenter)

        pdf_label = QLabel("PDF")
        pdf_label.setStyleSheet(
            f"color: {text_color}; font-size: 12px; font-weight: 700;"
        )
        pdf_label.setAlignment(Qt.AlignCenter)
        icon_layout.addWidget(pdf_label)
        layout.addWidget(self.pdf_icon)

        # 文件名 + 元信息
        info_layout = QVBoxLayout()
        info_layout.setSpacing(1)
        self.name_label = QLabel(filename)
        self.name_label.setObjectName("fileName")
        self.name_label.setStyleSheet(
            "color: #EAECEF; font-size: 13px; font-weight: 500;"
        )
        self.name_label.setWordWrap(True)
        info_layout.addWidget(self.name_label)
        self.meta_label = QLabel(meta)
        self.meta_label.setObjectName("fileMeta")
        self.meta_label.setStyleSheet(
            "color: #4A4B56; font-size: 11px;"
        )
        info_layout.addWidget(self.meta_label)
        layout.addLayout(info_layout, 1)

        # 状态标签
        self.status_label = QLabel(status)
        self.status_label.setStyleSheet(
            "color: #4A4B56; font-size: 11px;"
            "padding: 2px 8px; border-radius: 10px;"
            "background-color: rgba(255,255,255,8);"
        )
        layout.addWidget(self.status_label)

        # 更多按钮（悬停显示）
        self.more_btn = QPushButton("⋮")
        self.more_btn.setObjectName("fileMoreBtn")
        self.more_btn.setFixedSize(28, 28)
        self.more_btn.setCursor(Qt.PointingHandCursor)
        self.more_btn.setStyleSheet(
            "QPushButton#fileMoreBtn {\n"
            "    color: #4A4B56;\n"
            "    background: transparent;\n"
            "    border: none;\n"
            "    border-radius: 6px;\n"
            "    font-size: 16px;\n"
            "}\n"
            "QPushButton#fileMoreBtn:hover {\n"
            "    color: #EAECEF;\n"
            "    background: rgba(255,255,255,13);\n"
            "}\n"
        )
        layout.addWidget(self.more_btn)

    def apply_theme(self, colors):
        """主题切换时更新文件项内联样式"""
        # 更新 fileItem hover 样式
        self.setStyleSheet(
            f"QFrame#fileItem {{\n"
            f"    background: transparent;\n"
            f"    border: none;\n"
            f"    border-radius: 6px;\n"
            f"}}\n"
            f"QFrame#fileItem:hover {{\n"
            f"    background: {colors['white_8_qss']};\n"
            f"}}\n"
        )
        # 更新 PDF 图标
        if self._is_red:
            self.pdf_icon.setStyleSheet(
                f"QFrame#pdfIcon {{\n"
                f"    background: {colors['pdf_icon_red_bg_qss']};\n"
                f"    border: 1px solid {colors['pdf_icon_red_border_qss']};\n"
                f"    border-radius: 4px;\n"
                f"}}\n"
            )
        else:
            self.pdf_icon.setStyleSheet(
                f"QFrame#pdfIcon {{\n"
                f"    background: {colors['pdf_icon_blue_bg_qss']};\n"
                f"    border: 1px solid {colors['pdf_icon_blue_border_qss']};\n"
                f"    border-radius: 4px;\n"
                f"}}\n"
            )
        # 更新文件名
        self.name_label.setStyleSheet(
            f"color: {colors['card_title']}; font-size: 13px; font-weight: 500;"
        )
        # 更新元信息
        self.meta_label.setStyleSheet(
            f"color: {colors['text_muted']}; font-size: 11px;"
        )
        # 更新状态标签
        self.status_label.setStyleSheet(
            f"color: {colors['text_muted']}; font-size: 11px;"
            f"padding: 2px 8px; border-radius: 10px;"
            f"background-color: {colors['white_8_qss']};"
        )
        # 更新更多按钮
        self.more_btn.setStyleSheet(
            f"QPushButton#fileMoreBtn {{\n"
            f"    color: {colors['text_muted']};\n"
            f"    background: transparent;\n"
            f"    border: none;\n"
            f"    border-radius: 6px;\n"
            f"    font-size: 16px;\n"
            f"}}\n"
            f"QPushButton#fileMoreBtn:hover {{\n"
            f"    color: {colors['card_title']};\n"
            f"    background: {colors['white_13_qss']};\n"
            f"}}\n"
        )

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.file_clicked.emit(self._file_path, self._action)
        super().mousePressEvent(event)


# ================================================================
# 网格背景
# ================================================================
class GridBackground(QWidget):
    """背景网格线装饰（主题感知）"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("background: transparent;")
        self._grid_alpha = 4  # 深色模式默认 alpha

    def set_theme(self, colors):
        """主题切换时更新网格线透明度"""
        from src.common.theme import get_current_theme
        self._grid_alpha = 4 if get_current_theme() == "dark" else 8
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(QColor(128, 128, 128, self._grid_alpha), 0.5, Qt.SolidLine)
        painter.setPen(pen)
        w = self.width()
        h = self.height()
        for x in range(0, w, 48):
            painter.drawLine(x, 0, x, h)
        for y in range(0, h, 48):
            painter.drawLine(0, y, w, y)


# ================================================================
# StepCard - 快速上手步骤卡片
# ================================================================
class StepCard(QFrame):
    """快速上手步骤卡片：步骤图标 + 标题 + 描述"""

    def __init__(self, step_icon: str, step_title: str, step_desc: str, parent=None):
        super().__init__(parent)
        self.setObjectName("stepCard")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setStyleSheet(
            "QFrame#stepCard {\n"
            "    background: rgba(16, 18, 24, 184);\n"
            "    border: 1px solid rgba(255, 255, 255, 13);\n"
            "    border-radius: 12px;\n"
            "}\n"
        )

        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setAlignment(Qt.AlignCenter)

        # 步骤图标
        self.icon_label = QLabel(step_icon)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet("font-size: 28px;")
        layout.addWidget(self.icon_label)

        # 步骤标题
        self.title_label = QLabel(step_title)
        self.title_label.setObjectName("stepTitle")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet(
            "color: #EAECEF; font-size: 14px; font-weight: 600;"
        )
        layout.addWidget(self.title_label)

        # 步骤描述
        self.desc_label = QLabel(step_desc)
        self.desc_label.setObjectName("stepDesc")
        self.desc_label.setAlignment(Qt.AlignCenter)
        self.desc_label.setWordWrap(True)
        self.desc_label.setStyleSheet(
            "color: #8B8D98; font-size: 11px;"
        )
        layout.addWidget(self.desc_label)

    def apply_theme(self, colors):
        """主题切换时更新步骤卡片样式"""
        self.setStyleSheet(
            f"QFrame#stepCard {{\n"
            f"    background: {colors['func_card_bg_qss']};\n"
            f"    border: 1px solid {colors['white_13_qss']};\n"
            f"    border-radius: 12px;\n"
            f"}}\n"
        )
        self.title_label.setStyleSheet(
            f"color: {colors['card_title']}; font-size: 14px; font-weight: 600;"
        )
        self.desc_label.setStyleSheet(
            f"color: {colors['text_sub']}; font-size: 11px;"
        )


# ================================================================
# Ui_HomePage
# ================================================================
class Ui_HomePage(object):
    """首页 UI 类"""

    def setupUi(self, HomePage):
        HomePage.setObjectName("homePage")
        main_layout = QVBoxLayout(HomePage)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("homeScrollArea")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet(
            "QScrollArea#homeScrollArea {"
            "    border: none; background: transparent;"
            "}"
            "QScrollArea#homeScrollArea > QWidget > QWidget {"
            "    background: transparent;"
            "}"
            "QScrollBar:vertical {"
            "    width: 6px; background: transparent;"
            "    margin: 0px;"
            "}"
            "QScrollBar::handle:vertical {"
            "    background: rgba(255,255,255,20);"
            "    border-radius: 3px;"
            "    min-height: 30px;"
            "}"
            "QScrollBar::handle:vertical:hover {"
            "    background: rgba(255,255,255,31);"
            "}"
            "QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {"
            "    background: transparent;"
            "}"
        )

        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("scrollContent")
        self.scroll_content.setAttribute(Qt.WA_StyledBackground, True)
        self.scroll_content.setStyleSheet("background: transparent;")

        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(56, 48, 56, 48)
        self.scroll_layout.setSpacing(0)

        self.scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_area)

        # 网格背景
        self.grid_bg = GridBackground(self.scroll_content)
        self.grid_bg.lower()

        # 品牌区
        self._build_hero_section()
        self._build_quick_start_section()
        self._build_cards_section()
        self._build_divider()
        self._build_recent_section()
        # 底部弹性空间（仅添加一次，防止重复）
        self.scroll_layout.addStretch()

    def _build_hero_section(self):
        """品牌区：标题 + 版本 + 副标题 + 光晕"""
        self.hero_section = QWidget()
        self.hero_layout = QVBoxLayout(self.hero_section)
        self.hero_layout.setSpacing(12)
        self.hero_layout.setContentsMargins(0, 0, 0, 48)

        title_row = QHBoxLayout()
        title_row.setSpacing(0)
        
        self.title_label = QLabel("印流<span style='color:#4D7CFE;border-bottom:2px solid rgba(77,124,254,77);'>P</span>Dflow")
        self.title_label.setTextFormat(Qt.RichText)
        self.title_label.setStyleSheet(
            "color: #EAECEF; font-size: 32px; "
            "font-weight: 800; "
        )
        title_row.addWidget(self.title_label)
        self.badge = Badge("V1.2")
        title_row.addWidget(self.badge)
        title_row.addStretch()
        self.hero_layout.addLayout(title_row)

        self.subtitle_label = QLabel(_tr("设计师专用的轻量级 PDF 工具箱"))
        self.subtitle_label.setStyleSheet(
            "color: #8B8D98; font-size: 14px; font-weight: 400;"
        )
        self.hero_layout.addWidget(self.subtitle_label)

        # 光晕装饰
        self.glow1 = Glow(self.hero_section, radius=200, alpha=8)
        self.glow1.move(0, 0)
        self.hero_layout.addStretch()
        # 将光晕放在标题右侧
        self.hero_section.setStyleSheet("background: transparent;")

        self.scroll_layout.addWidget(self.hero_section)

    def _build_quick_start_section(self):
        """快速上手区域：3 步流程卡片 + 试试看按钮（仅首次用户显示）"""
        self.quick_start_section = QFrame()
        self.quick_start_section.setObjectName("quickStartSection")
        self.quick_start_section.setAttribute(Qt.WA_StyledBackground, True)
        self.quick_start_section.setStyleSheet(
            "QFrame#quickStartSection {\n"
            "    background: rgba(77, 124, 254, 8);\n"
            "    border: 1px solid rgba(77, 124, 254, 20);\n"
            "    border-radius: 16px;\n"
            "}\n"
        )

        section_layout = QVBoxLayout(self.quick_start_section)
        section_layout.setSpacing(0)
        section_layout.setContentsMargins(24, 20, 24, 20)

        # 标题行
        header_row = QHBoxLayout()
        header_row.setSpacing(8)
        self.quick_start_title = QLabel(_tr("快速上手"))
        self.quick_start_title.setObjectName("quickStartTitle")
        self.quick_start_title.setStyleSheet(
            "color: #EAECEF; font-size: 14px; font-weight: 600;"
        )
        header_row.addWidget(self.quick_start_title)
        header_row.addStretch()
        section_layout.addLayout(header_row)

        section_layout.addSpacing(16)

        # 步骤卡片行
        steps_row = QHBoxLayout()
        steps_row.setSpacing(12)
        steps_row.setContentsMargins(0, 0, 0, 0)

        # 步骤数据
        steps_data = [
            ("1️⃣", _tr("选择文件"), _tr("拖入或浏览 PDF 文件")),
            ("2️⃣", _tr("一键处理"), _tr("选择功能，自动完成")),
            ("3️⃣", _tr("下载结果"), _tr("保存到指定位置")),
        ]

        self.step_cards = []
        for i, (icon, title, desc) in enumerate(steps_data):
            card = StepCard(icon, title, desc)
            self.step_cards.append(card)
            steps_row.addWidget(card)

            # 步骤之间添加箭头
            if i < len(steps_data) - 1:
                arrow = QLabel("→")
                arrow.setObjectName("stepArrow")
                arrow.setAlignment(Qt.AlignCenter)
                arrow.setFixedWidth(24)
                arrow.setStyleSheet(
                    "color: #4D7CFE; font-size: 18px; font-weight: 600;"
                )
                steps_row.addWidget(arrow)

        section_layout.addLayout(steps_row)

        section_layout.addSpacing(16)

        # 试试看按钮
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.try_demo_btn = QPushButton(_tr("试试看"))
        self.try_demo_btn.setObjectName("tryDemoBtn")
        self.try_demo_btn.setCursor(Qt.PointingHandCursor)
        self.try_demo_btn.setFixedSize(120, 36)
        self.try_demo_btn.setStyleSheet(
            "QPushButton#tryDemoBtn {\n"
            "    color: #FFFFFF; font-size: 13px; font-weight: 600;\n"
            "    background: #4D7CFE; border: none;\n"
            "    border-radius: 6px;\n"
            "}\n"
            "QPushButton#tryDemoBtn:hover {\n"
            "    background: #3D6CF0;\n"
            "}\n"
            "QPushButton#tryDemoBtn:pressed {\n"
            "    background: #2D5CD0;\n"
            "}\n"
        )
        btn_row.addWidget(self.try_demo_btn)
        btn_row.addStretch()
        section_layout.addLayout(btn_row)

        # 根据是否有最近文件决定是否显示
        records = get_recent_files(limit=1)
        self.quick_start_section.setVisible(len(records) == 0)

        self.scroll_layout.addWidget(self.quick_start_section)
        self.scroll_layout.addSpacing(24)

    def _build_cards_section(self):
        """4 个功能卡片"""
        self.cards_section = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_section)
        self.cards_layout.setSpacing(0)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)

        title_row = QHBoxLayout()
        title_row.setSpacing(0)
        self.section_title = QLabel(_tr("工具箱"))
        self.section_title.setStyleSheet(
            "color: #8B8D98; font-size: 13px; "
            "font-weight: 500; letter-spacing: 0.5px;"
        )
        title_row.addWidget(self.section_title)
        title_row.addStretch()
        self.cards_layout.addLayout(title_row)

        self.cards_layout.addSpacing(20)

        cards_row = QHBoxLayout()
        cards_row.setSpacing(16)
        cards_row.setContentsMargins(0, 0, 0, 0)

        self.card_widgets = {}

        def make_card(icon, title, desc, icon_color, card_name):
            card = FunctionCard(icon, title, desc, icon_color, card_name)
            self.card_widgets[card_name] = card
            cards_row.addWidget(card)

        make_card("⬇", _tr("合并拆分"), _tr("PDF 合并、拆分与页面管理"), "#4D7CFE", "merge")
        make_card("📦", _tr("压缩优化"), _tr("智能减小 PDF 文件体积"), "#FF9500", "compress")
        make_card("🔄", _tr("格式转换"), _tr("图片与 PDF 双向互转"), "#34C759", "convert")
        make_card("💧", _tr("水印处理"), _tr("添加文字或图片水印"), "#FF3B30", "watermark")

        self.cards_layout.addLayout(cards_row)
        self.scroll_layout.addWidget(self.cards_section)

    def _build_divider(self):
        """渐变分割线"""
        self.divider = QFrame()
        self.divider.setFrameShape(QFrame.HLine)
        self.divider.setStyleSheet(
            "QFrame {"
            "    background: qlineargradient("
            "        x1:0, y1:0, x2:1, y2:0,"
            "        stop:0 rgba(77,124,254,255),"
            "        stop:0.04 rgba(77,124,254,51),"
            "        stop:1 rgba(255,255,255,5)"
            "    );"
            "    border: none;"
            "    height: 1px;"
            "}"
        )
        self.scroll_layout.addSpacing(32)
        self.scroll_layout.addWidget(self.divider)
        self.scroll_layout.addSpacing(32)

    def _build_recent_section(self):
        """最近文件容器 + 文件列表"""
        self.recent_section = QFrame()
        self.recent_section.setObjectName("recentSection")
        self.recent_section.setAttribute(Qt.WA_StyledBackground, True)
        self.recent_section.setStyleSheet(
            "QFrame#recentSection {\n"
            "    background-color: rgba(20, 22, 28, 166);\n"
            "    border: 1px solid rgba(255, 255, 255, 15);\n"
            "    border-radius: 16px;\n"
            "}\n"
        )

        section_layout = QVBoxLayout(self.recent_section)
        section_layout.setSpacing(0)
        section_layout.setContentsMargins(24, 20, 24, 20)

        # 标题行
        header_row = QHBoxLayout()
        header_row.setSpacing(0)
        self.section_label = QLabel(" " + _tr("最近使用的文件"))
        self.section_label.setStyleSheet(
            "color: #8B8D98; font-size: 13px; font-weight: 500;"
        )
        header_row.addWidget(self.section_label)
        header_row.addStretch()
        self.clear_btn = QPushButton(_tr("清空记录"))
        self.clear_btn.setObjectName("clearBtn")
        self.clear_btn.setCursor(Qt.PointingHandCursor)
        self.clear_btn.setStyleSheet(
            "QPushButton#clearBtn {"
            "    color: #4A4B56; font-size: 12px;"
            "    background: transparent; border: none;"
            "    border-radius: 4px; padding: 4px 10px;"
            "}"
            "QPushButton#clearBtn:hover {"
            "    color: #EAECEF; background: rgba(255,255,255,8);"
            "}"
        )
        header_row.addWidget(self.clear_btn)
        section_layout.addLayout(header_row)

        section_layout.addSpacing(16)

        # 文件列表
        self.file_list_layout = QVBoxLayout()
        self.file_list_layout.setSpacing(4)
        self.file_list_layout.setContentsMargins(0, 0, 0, 0)

        self._refresh_recent_files()

        section_layout.addLayout(self.file_list_layout)
        self.scroll_layout.addWidget(self.recent_section)

    def _refresh_recent_files(self):
        """刷新最近使用的文件列表"""
        # 清空现有列表
        while self.file_list_layout.count():
            item = self.file_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        records = get_recent_files(limit=10)

        # 获取当前主题色，确保新建的文件项立即跟随主题
        from src.common.theme import DARK_COLORS, LIGHT_COLORS, get_current_theme
        cur_colors = DARK_COLORS if get_current_theme() == "dark" else LIGHT_COLORS

        # 更新快速上手区域可见性
        if hasattr(self, 'quick_start_section'):
            self.quick_start_section.setVisible(len(records) == 0)

        if not records:
            # 首次用户空状态：引导式欢迎界面
            empty_widget = QWidget()
            empty_layout = QVBoxLayout(empty_widget)
            empty_layout.setSpacing(8)
            empty_layout.setContentsMargins(0, 16, 0, 16)
            empty_layout.setAlignment(Qt.AlignCenter)

            # 图标
            empty_icon = QLabel("📂")
            empty_icon.setAlignment(Qt.AlignCenter)
            empty_icon.setStyleSheet("font-size: 36px;")
            empty_layout.addWidget(empty_icon)

            # 主文字
            self.empty_primary = QLabel(_tr("开始你的第一次体验"))
            self.empty_primary.setObjectName("emptyPrimary")
            self.empty_primary.setAlignment(Qt.AlignCenter)
            self.empty_primary.setStyleSheet(
                f"color: {cur_colors['card_title']}; font-size: 15px; font-weight: 600;"
            )
            empty_layout.addWidget(self.empty_primary)

            # 副文字
            self.empty_secondary = QLabel(_tr("选择上方功能卡片，或点击「试试看」生成示例文件"))
            self.empty_secondary.setObjectName("emptySecondary")
            self.empty_secondary.setAlignment(Qt.AlignCenter)
            self.empty_secondary.setWordWrap(True)
            self.empty_secondary.setStyleSheet(
                f"color: {cur_colors['text_sub']}; font-size: 12px;"
            )
            empty_layout.addWidget(self.empty_secondary)

            self.file_list_layout.addWidget(empty_widget)
            return

        for record in records:
            file_name = record.get("file_name", "未知文件")
            file_path = record.get("file_path", "")
            action = record.get("action", "")
            dt = record.get("datetime", "")
            timestamp = record.get("timestamp", 0)
            status = get_status_text(timestamp) if timestamp else ""
            is_red = status == "刚刚"

            item = FileItem(file_name, f"— · {dt}", status, file_path, action, is_red)
            # 关键：创建后立即应用当前主题色，避免沿用 __init__ 中的深色硬编码
            if hasattr(item, 'apply_theme'):
                item.apply_theme(cur_colors)
            self.file_list_layout.addWidget(item)

    def apply_theme(self, colors):
        """主题切换时更新首页内联样式"""
        # 更新滚动区域样式（滚动条颜色切换）
        self.scroll_area.setStyleSheet(
            "QScrollArea#homeScrollArea {"
            "    border: none; background: transparent;"
            "}"
            "QScrollArea#homeScrollArea > QWidget > QWidget {"
            "    background: transparent;"
            "}"
            "QScrollBar:vertical {"
            "    width: 6px; background: transparent;"
            "    margin: 0px;"
            "}"
            "QScrollBar::handle:vertical {"
            f"    background: {colors['scrollbar_bg']};"
            "    border-radius: 3px;"
            "    min-height: 30px;"
            "}"
            "QScrollBar::handle:vertical:hover {"
            f"    background: {colors['scrollbar_hover']};"
            "}"
            "QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {"
            "    background: transparent;"
            "}"
        )
        # 更新标题
        self.title_label.setStyleSheet(
            f"color: {colors['card_title']}; font-size: 32px; "
            f"font-weight: 800; "
        )
        # 更新副标题
        self.subtitle_label.setStyleSheet(
            f"color: {colors['text_sub']}; font-size: 14px; font-weight: 400;"
        )
        # 更新"工具箱"节标题
        self.section_title.setStyleSheet(
            f"color: {colors['text_sub']}; font-size: 13px; "
            f"font-weight: 500; letter-spacing: 0.5px;"
        )
        # 更新"最近使用的文件"标题
        self.section_label.setStyleSheet(
            f"color: {colors['text_sub']}; font-size: 13px; font-weight: 500;"
        )
        # 更新渐变分割线
        self.divider.setStyleSheet(
            "QFrame {"
            "    background: qlineargradient("
            "        x1:0, y1:0, x2:1, y2:0,"
            "        stop:0 rgba(77,124,254,255),"
            "        stop:0.04 rgba(77,124,254,51),"
            f"        stop:1 {colors['white_8_qss']}"
            "    );"
            "    border: none;"
            "    height: 1px;"
            "}"
        )
        # 更新最近文件容器背景和边框
        self.recent_section.setStyleSheet(
            f"QFrame#recentSection {{\n"
            f"    background-color: {colors['recent_bg_qss']};\n"
            f"    border: 1px solid {colors['white_15_qss']};\n"
            f"    border-radius: 16px;\n"
            f"}}\n"
        )
        # 更新清空按钮
        self.clear_btn.setStyleSheet(
            f"QPushButton#clearBtn {{"
            f"    color: {colors['text_muted']}; font-size: 12px;"
            f"    background: transparent; border: none;"
            f"    border-radius: 4px; padding: 4px 10px;"
            f"}}"
            f"QPushButton#clearBtn:hover {{"
            f"    color: {colors['card_title']}; background: {colors['white_8_qss']};"
            f"}}"
        )
        # 更新空状态标签
        if hasattr(self, 'empty_primary') and self.empty_primary:
            self.empty_primary.setStyleSheet(
                f"color: {colors['card_title']}; font-size: 15px; font-weight: 600;"
            )
        if hasattr(self, 'empty_secondary') and self.empty_secondary:
            self.empty_secondary.setStyleSheet(
                f"color: {colors['text_sub']}; font-size: 12px;"
            )
        # 更新快速上手区域
        if hasattr(self, 'quick_start_section'):
            self.quick_start_section.setStyleSheet(
                f"QFrame#quickStartSection {{\n"
                f"    background: {colors['primary_light_10']};\n"
                f"    border: 1px solid {colors['primary_light_20']};\n"
                f"    border-radius: 16px;\n"
                f"}}\n"
            )
        if hasattr(self, 'quick_start_title') and self.quick_start_title:
            self.quick_start_title.setStyleSheet(
                f"color: {colors['card_title']}; font-size: 14px; font-weight: 600;"
            )
        if hasattr(self, 'try_demo_btn') and self.try_demo_btn:
            self.try_demo_btn.setStyleSheet(
                f"QPushButton#tryDemoBtn {{\n"
                f"    color: #FFFFFF; font-size: 13px; font-weight: 600;\n"
                f"    background: {colors['primary']}; border: none;\n"
                f"    border-radius: 6px;\n"
                f"}}\n"
                f"QPushButton#tryDemoBtn:hover {{\n"
                f"    background: {colors['primary_hover']};\n"
                f"}}\n"
                f"QPushButton#tryDemoBtn:pressed {{\n"
                f"    background: {colors['primary_pressed']};\n"
                f"}}\n"
            )
        # 更新步骤卡片
        if hasattr(self, 'step_cards'):
            for card in self.step_cards:
                card.apply_theme(colors)
        # 更新所有 FileItem
        for i in range(self.file_list_layout.count()):
            item = self.file_list_layout.itemAt(i)
            if item and item.widget() and hasattr(item.widget(), 'apply_theme'):
                item.widget().apply_theme(colors)
        # 更新网格背景
        if hasattr(self, 'grid_bg') and self.grid_bg:
            self.grid_bg.set_theme(colors)


# ================================================================
# HomePage
# ================================================================
class HomePage(QWidget):
    """首页页面包装类"""

    card_clicked = Signal(str)
    file_clicked = Signal(str, str)

    CARD_TO_NAV = {
        "merge": 1,
        "compress": 2,
        "convert": 3,
        "watermark": 4,
    }

    # 文件操作类型映射到导航索引
    ACTION_TO_NAV = {
        "merge": 1,
        "compress": 2,
        "convert": 3,
        "watermark": 4,
    }

    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(
            "HomePage {"
            "    background-color: #0B0E11;"
            "}"
        )
        self._demo_pdf_path = ""  # 示例 PDF 文件路径
        self.ui = Ui_HomePage()
        self.ui.setupUi(self)
        self._connect_signals()
        self._trigger_stagger_animations()

    def _connect_signals(self):
        for card_name, card_widget in self.ui.card_widgets.items():
            card_widget.card_clicked.connect(self._on_card_clicked)
        self.ui.clear_btn.clicked.connect(self._on_clear_records)
        if hasattr(self.ui, 'try_demo_btn') and self.ui.try_demo_btn:
            self.ui.try_demo_btn.clicked.connect(self._on_try_demo)
        self._connect_file_item_signals()

    def retranslateUi(self):
        self.ui.subtitle_label.setText(_tr("设计师专用的轻量级 PDF 工具箱"))
        self.ui.section_title.setText(_tr("工具箱"))
        self.ui.section_label.setText(" " + _tr("最近使用的文件"))
        self.ui.clear_btn.setText(_tr("清空记录"))
        # 快速上手区域翻译
        if hasattr(self.ui, 'quick_start_title') and self.ui.quick_start_title:
            self.ui.quick_start_title.setText(_tr("快速上手"))
        if hasattr(self.ui, 'try_demo_btn') and self.ui.try_demo_btn:
            self.ui.try_demo_btn.setText(_tr("试试看"))
        if hasattr(self.ui, 'step_cards'):
            step_translations = [
                (_tr("选择文件"), _tr("拖入或浏览 PDF 文件")),
                (_tr("一键处理"), _tr("选择功能，自动完成")),
                (_tr("下载结果"), _tr("保存到指定位置")),
            ]
            for i, (title, desc) in enumerate(step_translations):
                if i < len(self.ui.step_cards):
                    self.ui.step_cards[i].title_label.setText(title)
                    self.ui.step_cards[i].desc_label.setText(desc)
        card_translations = {
            "merge": (_tr("合并拆分"), _tr("PDF 合并、拆分与页面管理")),
            "compress": (_tr("压缩优化"), _tr("智能减小 PDF 文件体积")),
            "convert": (_tr("格式转换"), _tr("图片与 PDF 双向互转")),
            "watermark": (_tr("水印处理"), _tr("添加文字或图片水印")),
        }
        for card_name, (title, desc) in card_translations.items():
            card = self.ui.card_widgets.get(card_name)
            if card:
                card.title_label.setText(title)
                card.desc_label.setText(desc)
        self.ui._refresh_recent_files()

    def _connect_file_item_signals(self):
        """连接最近文件列表项的点击信号"""
        for i in range(self.ui.file_list_layout.count()):
            item = self.ui.file_list_layout.itemAt(i)
            if item and item.widget():
                file_item = item.widget()
                if hasattr(file_item, 'file_clicked'):
                    file_item.file_clicked.connect(self._on_file_item_clicked)

    def _on_file_item_clicked(self, file_path: str, action: str):
        """处理最近文件项点击：跳转到对应功能页并传递文件路径"""
        nav_idx = self.ACTION_TO_NAV.get(action)
        if nav_idx is not None:
            self.file_clicked.emit(str(nav_idx), file_path)

    def _on_clear_records(self):
        """清空最近使用记录"""
        clear_records()
        self.ui._refresh_recent_files()
        # 重新连接信号
        self._connect_file_item_signals()

    def refresh_recent_files(self):
        """公开方法：刷新最近使用的文件列表(从外部调用)"""
        self.ui._refresh_recent_files()
        self._connect_file_item_signals()

    def _trigger_stagger_animations(self):
        """启动首页各区域入场动画：品牌区 → 快速上手 → 卡片区 → 文件区（依次 fadeUp）"""
        self._fade_up(self.ui.hero_section, delay=0, duration=600)
        if hasattr(self.ui, 'quick_start_section') and self.ui.quick_start_section.isVisible():
            self._fade_up(self.ui.quick_start_section, delay=80, duration=600)
        self._fade_up(self.ui.cards_section, delay=100, duration=600)
        self._fade_up(self.ui.divider, delay=200, duration=600)
        self._fade_up(self.ui.recent_section, delay=250, duration=600)
        for idx, (card_name, card_widget) in enumerate(self.ui.card_widgets.items()):
            delays = [150, 220, 290, 360]
            delay = delays[idx] if idx < len(delays) else 430
            card_widget.start_stagger_animation(delay)

    def _fade_up(self, widget, delay: int, duration: int):
        """淡入动画：opacity 0→1, 600ms"""
        effect = QGraphicsOpacityEffect(widget)
        effect.setOpacity(0.0)
        widget.setGraphicsEffect(effect)

        def _start():
            from PySide6.QtCore import QPropertyAnimation, QEasingCurve
            op_anim = QPropertyAnimation(effect, b"opacity")
            op_anim.setStartValue(0.0)
            op_anim.setEndValue(1.0)
            op_anim.setDuration(duration)
            op_anim.setEasingCurve(QEasingCurve.OutCubic)
            op_anim.start()
            widget._fade_anim = op_anim

        QTimer.singleShot(delay, _start)

    def _generate_demo_pdf(self) -> str:
        """生成示例 PDF 文件，返回文件路径"""
        try:
            import fitz
            tmp_dir = tempfile.gettempdir()
            demo_path = os.path.join(tmp_dir, "印流PDflow_示例文件.pdf")

            doc = fitz.open()
            page = doc.new_page(width=595, height=842)  # A4 尺寸

            # 标题
            title_rect = fitz.Rect(72, 120, 523, 170)
            page.insert_textbox(
                title_rect,
                "印流PDflow 示例文件",
                fontsize=28,
                fontname="helv",
                color=(0.30, 0.49, 0.99),  # 主题蓝 #4D7CFE
                align=fitz.TEXT_ALIGN_CENTER,
            )

            # 分隔线
            shape = page.new_shape()
            shape.draw_line(fitz.Point(72, 190), fitz.Point(523, 190))
            shape.finish(color=(0.30, 0.49, 0.99), width=1)
            shape.commit()

            # 正文
            body_rect = fitz.Rect(72, 210, 523, 600)
            page.insert_textbox(
                body_rect,
                "这是一份由印流PDflow自动生成的示例PDF文件。\n\n"
                "你可以使用这个文件来体验以下功能：\n\n"
                "  • 合并拆分 — 将PDF拆分为单页或合并多个文件\n"
                "  • 压缩优化 — 减小PDF文件体积\n"
                "  • 格式转换 — PDF与图片互转\n"
                "  • 水印处理 — 添加文字或图片水印\n\n"
                "选择上方任意功能卡片，即可开始体验！",
                fontsize=13,
                fontname="helv",
                color=(0.30, 0.30, 0.35),
                align=fitz.TEXT_ALIGN_LEFT,
            )

            # 页脚
            footer_rect = fitz.Rect(72, 750, 523, 790)
            page.insert_textbox(
                footer_rect,
                "印流PDflow — 设计师专用的轻量级 PDF 工具箱",
                fontsize=10,
                fontname="helv",
                color=(0.55, 0.55, 0.60),
                align=fitz.TEXT_ALIGN_CENTER,
            )

            doc.save(demo_path)
            doc.close()
            self._demo_pdf_path = demo_path
            return demo_path
        except Exception as e:
            print(f"[HomePage] 生成示例PDF失败: {e}")
            return ""

    def _on_try_demo(self):
        """试试看按钮：生成示例PDF并提示用户"""
        demo_path = self._generate_demo_pdf()
        if demo_path:
            msg = QMessageBox(self)
            msg.setWindowTitle(_tr("示例文件已生成"))
            msg.setText(_tr("示例文件已生成！点击下方功能卡片开始体验"))
            msg.setInformativeText(_tr("文件路径：{}").format(demo_path))
            msg.setIcon(QMessageBox.Information)
            msg.setStyleSheet(
                "QMessageBox { background-color: #1A1A22; color: #EAECEF; }"
                "QPushButton { "
                "    color: #FFFFFF; background: #4D7CFE; "
                "    border: none; border-radius: 4px; "
                "    padding: 6px 20px; min-width: 80px; "
                "}"
                "QPushButton:hover { background: #3D6CF0; }"
                "QLabel { color: #EAECEF; }"
            )
            msg.exec()

    def _on_card_clicked(self, card_name: str):
        nav_idx = self.CARD_TO_NAV.get(card_name)
        if nav_idx is not None:
            self.card_clicked.emit(str(nav_idx))

    def apply_theme(self, colors):
        """主题切换时更新首页整体样式"""
        # 更新自身背景
        self.setStyleSheet(
            f"HomePage {{"
            f"    background-color: {colors['bg']};"
            f"}}"
        )
        # 通知 Ui_HomePage 更新子组件
        self.ui.apply_theme(colors)
        # 更新所有功能卡片的主题
        for card_name, card_widget in self.ui.card_widgets.items():
            card_widget.apply_theme(colors)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self.ui, 'grid_bg'):
            self.ui.grid_bg.setGeometry(
                self.ui.scroll_content.rect()
            )
