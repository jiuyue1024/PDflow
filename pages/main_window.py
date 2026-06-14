# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.11.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QMainWindow,
    QPushButton, QSizePolicy, QSpacerItem, QStackedLayout,
    QStatusBar, QVBoxLayout, QWidget, QFrame)
from src.common.theme import get_current_theme, get_colors
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1280, 820)
        self.centralWidget = QWidget(MainWindow)
        self.centralWidget.setObjectName(u"centralWidget")
        self.mainLayout = QHBoxLayout(self.centralWidget)
        self.mainLayout.setSpacing(0)
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.sidebar = QWidget(self.centralWidget)
        self.sidebar.setObjectName(u"sidebar")
        self.sidebar.setMinimumSize(QSize(220, 0))
        self.sidebar.setMaximumSize(QSize(220, 16777215))
        self.sidebarLayout = QVBoxLayout(self.sidebar)
        self.sidebarLayout.setSpacing(2)
        self.sidebarLayout.setObjectName(u"sidebarLayout")
        self.sidebarLayout.setContentsMargins(0, 0, 0, 0)

        # 品牌区：LOGO + 文字（HBox 布局）
        self.brandRow = QWidget(self.sidebar)
        self.brandRow.setObjectName("brandRow")
        self.brandRow.setStyleSheet("QWidget#brandRow{background:transparent;border:none;}")
        self.brandLayout = QHBoxLayout(self.brandRow)
        self.brandLayout.setSpacing(10)
        self.brandLayout.setContentsMargins(20, 20, 20, 16)
        self.brandLayout.setAlignment(Qt.AlignVCenter)

        self.navLogo = QLabel(self.brandRow)
        self.navLogo.setObjectName("navLogo")
        self.navLogo.setFixedSize(24, 24)
        self.navLogo.setMinimumSize(24, 24)
        self.navLogo.setMaximumSize(24, 24)
        self.brandLayout.addWidget(self.navLogo)

        self.navTitle = QLabel(self.brandRow)
        self.navTitle.setObjectName(u"navTitle")
        self.navTitle.setStyleSheet("background:transparent;border:none;")
        self.brandLayout.addWidget(self.navTitle)

        self.sidebarLayout.addWidget(self.brandRow)

        # 导航按钮容器（模拟 HTML 中的 sidebar-nav: padding 0 10px, gap 2px）
        self.sidebarNav = QWidget(self.sidebar)
        self.sidebarNav.setObjectName("sidebarNav")
        self.sidebarNav.setStyleSheet(
            "QWidget#sidebarNav { "
            "    background: transparent; "
            "    border: none; "
            "}"
        )
        self.navLayout = QVBoxLayout(self.sidebarNav)
        self.navLayout.setSpacing(2)
        self.navLayout.setContentsMargins(10, 0, 10, 0)

        # 每个导航项使用 HBox：指示器 + 图标 + 按钮
        # 背景样式绑定在 row 上（checked 时整行圆角背景）
        # 存储当前主题色，供 _update_row_bg 使用
        # 根据用户保存的主题偏好初始化，而非硬编码 DARK_COLORS
        self._nav_theme_colors = dict(get_colors())

        def _make_nav_row(container, icon_name, btn_text, btn_obj_name, default_checked=False):
            row = QWidget(container)
            row.setObjectName("navRow_" + btn_obj_name)
            row.setAttribute(Qt.WA_StyledBackground, True)
            row_layout = QHBoxLayout(row)
            row_layout.setSpacing(8)
            row_layout.setContentsMargins(10, 0, 0, 0)
            row_layout.setAlignment(Qt.AlignVCenter)
            ind = self._create_indicator(row)
            row_layout.addWidget(ind)
            icon = self._create_nav_icon(row, icon_name, self._nav_theme_colors['sidebar_icon'])
            row_layout.addWidget(icon)
            btn = QPushButton(btn_text)
            btn.setObjectName(btn_obj_name)
            btn.setCheckable(True)
            btn.setChecked(default_checked)
            btn.setMinimumHeight(40)
            # ── 修复：不再写内联 stylesheet，让 global.qss.template 的 QPushButton#navButton 选择器生效 ──
            # 仅设置 border:none 以避免 QSS 边框冲突
            row_layout.addWidget(btn, 1)

            # 按钮状态变化时刷新 row 背景和图标颜色
            def _update_row_bg(checked):
                if checked:
                    row.setStyleSheet(
                        f"background-color: {self._nav_theme_colors['nav_checked_bg_qss']}; border-radius: 8px;"
                    )
                    self._set_nav_icon_color(icon, self._nav_theme_colors['sidebar_icon_active'])
                else:
                    row.setStyleSheet("background-color: transparent; border-radius: 0;")
                    self._set_nav_icon_color(icon, self._nav_theme_colors['sidebar_icon'])
            btn.toggled.connect(_update_row_bg)
            if default_checked:
                row.setStyleSheet(f"background-color: {self._nav_theme_colors['nav_checked_bg_qss']}; border-radius: 8px;")
                self._set_nav_icon_color(icon, self._nav_theme_colors['sidebar_icon_active'])
            else:
                row.setStyleSheet("background: transparent; border-radius: 0;")

            self.navLayout.addWidget(row)
            icon_attr = btn_obj_name + "Icon"
            setattr(self, icon_attr, icon)
            return row, btn, ind

        self.btnHome_row, self.btnHome, self.btnHome_ind = _make_nav_row(self.sidebarNav, "nav-home", "首页", "btnHome", True)
        self.btnMerge_row, self.btnMerge, self.btnMerge_ind = _make_nav_row(self.sidebarNav, "nav-merge", "合并拆分", "btnMerge")
        self.btnCompress_row, self.btnCompress, self.btnCompress_ind = _make_nav_row(self.sidebarNav, "nav-compress", "压缩优化", "btnCompress")
        self.btnConvert_row, self.btnConvert, self.btnConvert_ind = _make_nav_row(self.sidebarNav, "nav-convert", "格式转换", "btnConvert")
        self.btnWatermark_row, self.btnWatermark, self.btnWatermark_ind = _make_nav_row(self.sidebarNav, "nav-watermark", "水印处理", "btnWatermark")
        self.btnSpeedwrite_row, self.btnSpeedwrite, self.btnSpeedwrite_ind = _make_nav_row(self.sidebarNav, "nav-pen", "速文创作", "btnSpeedwrite")
        self.btnSpeedwrite_row.setVisible(False)
        self.btnTemplateLayout_row, self.btnTemplateLayout, self.btnTemplateLayout_ind = _make_nav_row(self.sidebarNav, "nav-template", "模板排版", "btnTemplateLayout")

        self.sidebarLayout.addWidget(self.sidebarNav)

        # 底部 spacer
        self.sidebarSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.sidebarLayout.addItem(self.sidebarSpacer)

        # 设置区域（底部独立，带顶部边框）
        self.sidebarFooter = QFrame(self.sidebar)
        self.sidebarFooter.setObjectName("sidebarFooter")
        self.sidebarFooter.setStyleSheet(
            "QFrame#sidebarFooter {\n"
            f"    border-top: 1px solid {self._nav_theme_colors['white_8_qss']};\n"
            "    background: transparent;\n"
            "}\n"
        )
        self.footerLayout = QVBoxLayout(self.sidebarFooter)
        self.footerLayout.setSpacing(0)
        self.footerLayout.setContentsMargins(10, 16, 10, 16)

        self.btnSettings = QPushButton(self.sidebarFooter)
        self.btnSettings.setObjectName(u"btnSettings")
        self.btnSettings.setCheckable(True)
        self.footerLayout.addWidget(self.btnSettings)

        self.sidebarLayout.addWidget(self.sidebarFooter)

        self.mainLayout.addWidget(self.sidebar)

        self.contentArea = QWidget(self.centralWidget)
        self.contentArea.setObjectName(u"contentArea")
        self.contentLayout = QVBoxLayout(self.contentArea)
        self.contentLayout.setSpacing(0)
        self.contentLayout.setObjectName(u"contentLayout")
        self.contentLayout.setContentsMargins(0, 0, 0, 0)
        self.contentTitle = QLabel(self.contentArea)
        self.contentTitle.setObjectName(u"contentTitle")

        self.contentLayout.addWidget(self.contentTitle)

        self.pageContainer = QWidget(self.contentArea)
        self.pageContainer.setObjectName(u"pageContainer")
        self.pagesStack = QStackedLayout(self.pageContainer)
        self.pagesStack.setObjectName(u"pagesStack")
        self.pagesStack.setContentsMargins(0, 0, 0, 0)

        self.contentLayout.addWidget(self.pageContainer)


        self.mainLayout.addWidget(self.contentArea)

        MainWindow.setCentralWidget(self.centralWidget)
        self.statusBar = QStatusBar(MainWindow)
        self.statusBar.setObjectName(u"statusBar")
        self.statusBar.setSizeGripEnabled(False)
        MainWindow.setStatusBar(self.statusBar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def _create_nav_icon(self, parent, icon_name, color_hex="#848E9C"):
        """创建导航图标标签，存储 icon_name 供后续重新着色"""
        icon_lbl = QLabel(parent)
        icon_lbl.setObjectName("navIcon")
        icon_lbl._icon_name = icon_name
        icon_lbl.setFixedSize(20, 20)
        icon_lbl.setMinimumSize(20, 20)
        icon_lbl.setMaximumSize(20, 20)
        icon_lbl.setStyleSheet(
            "QLabel { background: transparent; border: none; }"
        )
        icon_lbl.setAlignment(Qt.AlignCenter)
        pix = self._render_nav_icon_svg(icon_name, color_hex)
        if pix:
            icon_lbl.setPixmap(pix)
        return icon_lbl

    def _render_nav_icon_svg(self, icon_name, color_hex):
        """将 SVG 图标渲染为指定颜色的 QPixmap"""
        import os
        import re
        from src.common.paths import resource_path
        from PySide6.QtCore import QByteArray
        icon_path = resource_path("assets", "icons", f"{icon_name}.svg")
        if not os.path.exists(icon_path):
            return None
        with open(icon_path, "r", encoding="utf-8") as f:
            svg_data = f.read()
        svg_data = svg_data.replace("currentColor", color_hex)
        svg_data = re.sub(r'stroke="#[^"]*"', f'stroke="{color_hex}"', svg_data)
        renderer = QSvgRenderer(QByteArray(svg_data.encode("utf-8")))
        pix = QPixmap(20, 20)
        pix.fill(Qt.transparent)
        p = QPainter(pix)
        renderer.render(p)
        p.end()
        return pix

    def _set_nav_icon_color(self, icon_label, color_hex):
        """重新渲染导航图标为指定颜色"""
        icon_name = getattr(icon_label, '_icon_name', None)
        if not icon_name:
            return
        pix = self._render_nav_icon_svg(icon_name, color_hex)
        if pix:
            icon_label.setPixmap(pix)

    def apply_sidebar_theme(self, colors):
        """主题切换时更新侧边栏所有导航图标颜色 + 重新计算 row 背景。"""
        self._nav_theme_colors = colors
        # 所有导航 row 重新着色（按钮 + 背景 + 图标）
        nav_rows = [
            ('btnHome_row', 'btnHome', 'btnHomeIcon'),
            ('btnMerge_row', 'btnMerge', 'btnMergeIcon'),
            ('btnCompress_row', 'btnCompress', 'btnCompressIcon'),
            ('btnConvert_row', 'btnConvert', 'btnConvertIcon'),
            ('btnWatermark_row', 'btnWatermark', 'btnWatermarkIcon'),
            ('btnSpeedwrite_row', 'btnSpeedwrite', 'btnSpeedwriteIcon'),
            ('btnTemplateLayout_row', 'btnTemplateLayout', 'btnTemplateLayoutIcon'),
        ]
        for row_attr, btn_attr, icon_attr in nav_rows:
            row = getattr(self, row_attr, None)
            btn = getattr(self, btn_attr, None)
            icon = getattr(self, icon_attr, None) if icon_attr else None

            if btn is None:
                continue

            if btn.isChecked():
                # 重新设置选中态 row 背景（使用新主题色）
                if row is not None:
                    row.setStyleSheet(
                        f"background-color: {colors['nav_checked_bg_qss']}; border-radius: 8px;"
                    )
                if icon is not None:
                    self._set_nav_icon_color(icon, colors['sidebar_icon_active'])
            else:
                if row is not None:
                    row.setStyleSheet("background-color: transparent; border-radius: 0;")
                if icon is not None:
                    self._set_nav_icon_color(icon, colors['sidebar_icon'])

    def _create_indicator(self, parent):
        """创建左侧活跃指示条（短蓝色条，checked时可见）"""
        ind = QFrame(parent)
        ind.setFixedSize(3, 20)
        ind.setMinimumSize(3, 20)
        ind.setMaximumSize(3, 20)
        ind.setStyleSheet(
            "QFrame {"
            "    background: transparent;"
            "    border: none;"
            "}"
        )
        return ind

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"\u5370\u6d41PDflow", None))
        MainWindow.setStyleSheet("")
        self.navTitle.setText(QCoreApplication.translate("MainWindow", u"\u5370\u6d41PDflow", None))
        self.btnHome.setText(QCoreApplication.translate("MainWindow", u"\u9996\u9875", None))
        self.btnHome.setObjectName(QCoreApplication.translate("MainWindow", u"navButton", None))
        self.btnMerge.setText(QCoreApplication.translate("MainWindow", u"\u5408\u5e76\u62c6\u5206", None))
        self.btnMerge.setObjectName(QCoreApplication.translate("MainWindow", u"navButton", None))
        self.btnCompress.setText(QCoreApplication.translate("MainWindow", u"\u538b\u7f29\u4f18\u5316", None))
        self.btnCompress.setObjectName(QCoreApplication.translate("MainWindow", u"navButton", None))
        self.btnConvert.setText(QCoreApplication.translate("MainWindow", u"\u683c\u5f0f\u8f6c\u6362", None))
        self.btnConvert.setObjectName(QCoreApplication.translate("MainWindow", u"navButton", None))
        self.btnWatermark.setText(QCoreApplication.translate("MainWindow", u"\u6c34\u5370\u5904\u7406", None))
        self.btnWatermark.setObjectName(QCoreApplication.translate("MainWindow", u"navButton", None))
        self.btnSpeedwrite.setText(QCoreApplication.translate("MainWindow", u"\u901f\u6587\u521b\u4f5c", None))
        self.btnSpeedwrite.setObjectName(QCoreApplication.translate("MainWindow", u"navButton", None))
        self.btnTemplateLayout.setText(QCoreApplication.translate("MainWindow", u"\u6a21\u677f\u6392\u7248", None))
        self.btnTemplateLayout.setObjectName(QCoreApplication.translate("MainWindow", u"navButton", None))
        self.btnSettings.setText(QCoreApplication.translate("MainWindow", u"\u8bbe\u7f6e", None))
        self.btnSettings.setObjectName(QCoreApplication.translate("MainWindow", u"navButton", None))
        self.contentTitle.setText(QCoreApplication.translate("MainWindow", u"\u9996\u9875", None))
        self.pageContainer.setStyleSheet("")
    # retranslateUi

