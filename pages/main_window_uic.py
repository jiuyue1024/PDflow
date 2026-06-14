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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QMainWindow,
    QPushButton, QSizePolicy, QSpacerItem, QStackedLayout,
    QStatusBar, QVBoxLayout, QWidget)
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
        self.sidebarLayout.setSpacing(4)
        self.sidebarLayout.setObjectName(u"sidebarLayout")
        self.sidebarLayout.setContentsMargins(0, 0, 0, 0)
        self.navTitle = QLabel(self.sidebar)
        self.navTitle.setObjectName(u"navTitle")

        self.sidebarLayout.addWidget(self.navTitle)

        self.btnHome = QPushButton(self.sidebar)
        self.btnHome.setObjectName(u"btnHome")
        self.btnHome.setCheckable(True)
        self.btnHome.setChecked(True)

        self.sidebarLayout.addWidget(self.btnHome)

        self.btnMerge = QPushButton(self.sidebar)
        self.btnMerge.setObjectName(u"btnMerge")
        self.btnMerge.setCheckable(True)

        self.sidebarLayout.addWidget(self.btnMerge)

        self.btnCompress = QPushButton(self.sidebar)
        self.btnCompress.setObjectName(u"btnCompress")
        self.btnCompress.setCheckable(True)

        self.sidebarLayout.addWidget(self.btnCompress)

        self.btnConvert = QPushButton(self.sidebar)
        self.btnConvert.setObjectName(u"btnConvert")
        self.btnConvert.setCheckable(True)

        self.sidebarLayout.addWidget(self.btnConvert)

        self.btnWatermark = QPushButton(self.sidebar)
        self.btnWatermark.setObjectName(u"btnWatermark")
        self.btnWatermark.setCheckable(True)

        self.sidebarLayout.addWidget(self.btnWatermark)

        self.btnTemplateLayout = QPushButton(self.sidebar)
        self.btnTemplateLayout.setObjectName(u"btnTemplateLayout")
        self.btnTemplateLayout.setCheckable(True)

        self.sidebarLayout.addWidget(self.btnTemplateLayout)

        self.btnSpeedwrite = QPushButton(self.sidebar)
        self.btnSpeedwrite.setObjectName(u"btnSpeedwrite")
        self.btnSpeedwrite.setCheckable(True)

        self.sidebarLayout.addWidget(self.btnSpeedwrite)

        self.sidebarSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.sidebarLayout.addItem(self.sidebarSpacer)

        self.btnSettings = QPushButton(self.sidebar)
        self.btnSettings.setObjectName(u"btnSettings")
        self.btnSettings.setCheckable(True)

        self.sidebarLayout.addWidget(self.btnSettings)


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

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"\u5370\u6d41PDflow", None))
        MainWindow.setStyleSheet(QCoreApplication.translate("MainWindow", u"\n"
"    QMainWindow {\n"
"        background-color: #0B0E11;\n"
"    }\n"
"    QWidget#centralWidget {\n"
"        background-color: #0B0E11;\n"
"    }\n"
"    QLabel#navTitle {\n"
"        color: #EAECEF;\n"
"        font-size: 16px;\n"
"        font-weight: bold;\n"
"        padding: 20px 16px 12px 16px;\n"
"    }\n"
"    QPushButton#navButton {\n"
"        color: #848E9C;\n"
"        background-color: transparent;\n"
"        text-align: left;\n"
"        padding: 10px 16px;\n"
"        border: none;\n"
"        border-radius: 6px;\n"
"        font-size: 14px;\n"
"    }\n"
"    QPushButton#navButton:hover {\n"
"        background-color: #1E2329;\n"
"        color: #EAECEF;\n"
"    }\n"
"    QPushButton#navButton:checked {\n"
"        background-color: #3E7FFF;\n"
"        color: #FFFFFF;\n"
"    }\n"
"    QWidget#sidebar {\n"
"        background-color: #121418;\n"
"        border-right: 1px solid #2B3139;\n"
"    }\n"
"    QWidget#contentArea {\n"
"        background-color: #0B0E11;\n"
"    }\n"
"    QLabe"
                        "l#contentTitle {\n"
"        color: #EAECEF;\n"
"        font-size: 24px;\n"
"        font-weight: bold;\n"
"        padding: 24px;\n"
"    }\n"
"    QStatusBar {\n"
"        background-color: #121418;\n"
"        color: #848E9C;\n"
"        border-top: 1px solid #2B3139;\n"
"    }\n"
"   ", None))
        self.navTitle.setText(QCoreApplication.translate("MainWindow", u"\u5370\u6d41PDflow", None))
        self.btnHome.setText(QCoreApplication.translate("MainWindow", u"\U0001f3a8 \U00009996\U00009875", None))
        self.btnHome.setObjectName(QCoreApplication.translate("MainWindow", u"navButton", None))
        self.btnMerge.setText(QCoreApplication.translate("MainWindow", u"\U0001f4c4 \U00005408\U00005e76\U000062c6\U00005206", None))
        self.btnMerge.setObjectName(QCoreApplication.translate("MainWindow", u"navButton", None))
        self.btnCompress.setText(QCoreApplication.translate("MainWindow", u"\U0001f4e6 \U0000538b\U00007f29", None))
        self.btnCompress.setObjectName(QCoreApplication.translate("MainWindow", u"navButton", None))
        self.btnConvert.setText(QCoreApplication.translate("MainWindow", u"\U0001f504 \U0000683c\U00005f0f\U00008f6c\U00006362", None))
        self.btnConvert.setObjectName(QCoreApplication.translate("MainWindow", u"navButton", None))
        self.btnWatermark.setText(QCoreApplication.translate("MainWindow", u"\U0001f4a7 \U00006c34\U00005370", None))
        self.btnWatermark.setObjectName(QCoreApplication.translate("MainWindow", u"navButton", None))
        self.btnTemplateLayout.setText(QCoreApplication.translate("MainWindow", u"\U0001f4d0 \U00006a21\U0000677f\U00006392\U00007248", None))
        self.btnTemplateLayout.setObjectName(QCoreApplication.translate("MainWindow", u"navButton", None))
        self.btnSpeedwrite.setText(QCoreApplication.translate("MainWindow", u"\u270d\ufe0f \u901f\u6587\u521b\u4f5c", None))
        self.btnSpeedwrite.setObjectName(QCoreApplication.translate("MainWindow", u"navButton", None))
        self.btnSettings.setText(QCoreApplication.translate("MainWindow", u"\u2699\ufe0f \u8bbe\u7f6e", None))
        self.btnSettings.setObjectName(QCoreApplication.translate("MainWindow", u"navButton", None))
        self.contentTitle.setText(QCoreApplication.translate("MainWindow", u"\u9996\u9875", None))
        self.pageContainer.setStyleSheet(QCoreApplication.translate("MainWindow", u"background-color: #0B0E11;", None))
    # retranslateUi

