# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'speedwrite_page.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QHBoxLayout,
    QLabel, QListWidget, QListWidgetItem, QPushButton,
    QScrollArea, QSizePolicy, QSpacerItem, QSplitter,
    QTextEdit, QVBoxLayout, QWidget)

class Ui_SpeedwritePage(object):
    def setupUi(self, SpeedwritePage):
        if not SpeedwritePage.objectName():
            SpeedwritePage.setObjectName(u"SpeedwritePage")
        SpeedwritePage.resize(1280, 820)
        SpeedwritePage.setMinimumSize(QSize(960, 640))
        SpeedwritePage.setStyleSheet(u"\n"
"/* ===== \u9875\u9762\u6574\u4f53 ===== */\n"
"QWidget#SpeedwritePage {\n"
"    background-color: #0A0E17;\n"
"}\n"
"\n"
"/* ===== \u4e3b\u6309\u94ae\u6837\u5f0f ===== */\n"
"QPushButton#btnNewTask {\n"
"    background-color: #4D7CFE;\n"
"    color: #FFFFFF;\n"
"    border: none;\n"
"    border-radius: 8px;\n"
"    font-size: 13px;\n"
"    font-weight: 500;\n"
"    padding: 8px 16px;\n"
"    height: 36px;\n"
"}\n"
"QPushButton#btnNewTask:hover { background-color: #3D6CF0; }\n"
"QPushButton#btnNewTask:pressed { background-color: #3560E0; }\n"
"\n"
"/* ===== \u8f6e\u5ed3\u6309\u94ae ===== */\n"
"QPushButton#btnOpenFile {\n"
"    background-color: transparent;\n"
"    color: #848E9C;\n"
"    border: 1px solid rgba(255,255,255,0.1);\n"
"    border-radius: 8px;\n"
"    font-size: 13px;\n"
"    padding: 8px 16px;\n"
"    height: 36px;\n"
"}\n"
"QPushButton#btnOpenFile:hover { border-color: rgba(255,255,255,0.2); color: #EAECEF; }\n"
"\n"
"/* ===== \u5de5\u5177\u680f\u6309\u94ae\uff08\u900f\u660e\u80cc\u666f\uff09"
                        " ===== */\n"
"QPushButton#btnBold, QPushButton#btnItalic, QPushButton#btnUnderline,\n"
"QPushButton#btnStrike, QPushButton#btnAlignLeft, QPushButton#btnAlignCenter,\n"
"QPushButton#btnAlignRight, QPushButton#btnAlignJustify,\n"
"QPushButton#btnList, QPushButton#btnOrderedList,\n"
"QPushButton#btnOutdent, QPushButton#btnIndent,\n"
"QPushButton#btnUndo, QPushButton#btnRedo,\n"
"QPushButton#btnDarkMode {\n"
"    background-color: transparent;\n"
"    color: #848E9C;\n"
"    border: none;\n"
"    border-radius: 6px;\n"
"    font-size: 16px;\n"
"    font-weight: 600;\n"
"    width: 28px;\n"
"    height: 28px;\n"
"}\n"
"QPushButton#btnBold:hover, QPushButton#btnItalic:hover, QPushButton#btnUnderline:hover,\n"
"QPushButton#btnStrike:hover, QPushButton#btnAlignLeft:hover, QPushButton#btnAlignCenter:hover,\n"
"QPushButton#btnAlignRight:hover, QPushButton#btnAlignJustify:hover,\n"
"QPushButton#btnList:hover, QPushButton#btnOrderedList:hover,\n"
"QPushButton#btnOutdent:hover, QPushButton#btnIndent:hover,\n"
"QPushButton#"
                        "btnUndo:hover, QPushButton#btnRedo:hover,\n"
"QPushButton#btnDarkMode:hover {\n"
"    background-color: rgba(255,255,255,0.06);\n"
"    color: #EAECEF;\n"
"}\n"
"QPushButton#btnBold:checked, QPushButton#btnItalic:checked,\n"
"QPushButton#btnUnderline:checked, QPushButton#btnStrike:checked,\n"
"QPushButton#btnAlignLeft:checked, QPushButton#btnAlignCenter:checked,\n"
"QPushButton#btnAlignRight:checked, QPushButton#btnAlignJustify:checked {\n"
"    background-color: #4D7CFE;\n"
"    color: #FFFFFF;\n"
"}\n"
"\n"
"/* ===== \u52a8\u4f5c\u6309\u94ae\uff08\u900f\u660e+\u8fb9\u6846\uff09 ===== */\n"
"QPushButton#btnExport, QPushButton#btnExportNormal, QPushButton#btnExportMobile,\n"
"QPushButton#btnMobileMode, QPushButton#btnAiAssistant,\n"
"QPushButton#btnExportMd, QPushButton#btnExportTxt, QPushButton#btnPreview {\n"
"    background-color: transparent;\n"
"    color: #848E9C;\n"
"    border: 1px solid rgba(255,255,255,0.06);\n"
"    border-radius: 6px;\n"
"    font-size: 12px;\n"
"    padding: 0 10px;\n"
"    height"
                        ": 28px;\n"
"}\n"
"QPushButton#btnExport:hover, QPushButton#btnExportNormal:hover, QPushButton#btnExportMobile:hover,\n"
"QPushButton#btnMobileMode:hover, QPushButton#btnAiAssistant:hover,\n"
"QPushButton#btnExportMd:hover, QPushButton#btnExportTxt:hover, QPushButton#btnPreview:hover {\n"
"    background-color: rgba(255,255,255,0.04);\n"
"    color: #EAECEF;\n"
"    border-color: rgba(255,255,255,0.12);\n"
"}\n"
"\n"
"/* ===== \u989c\u8272\u6309\u94ae ===== */\n"
"QPushButton#btnTextColor, QPushButton#btnBgColor {\n"
"    border-radius: 4px;\n"
"    border: 2px solid rgba(255,255,255,0.1);\n"
"    width: 22px;\n"
"    height: 22px;\n"
"}\n"
"QPushButton#btnTextColor { background-color: #1A1A22; }\n"
"QPushButton#btnBgColor { background-color: #FFE066; }\n"
"QPushButton#btnTextColor:hover, QPushButton#btnBgColor:hover { border-color: rgba(255,255,255,0.3); }\n"
"\n"
"/* ===== \u4e0b\u62c9\u6846\u6837\u5f0f ===== */\n"
"QComboBox#fontCombo, QComboBox#sizeCombo, QComboBox#lineSpacingCombo, QComboBox#bgThemeCombo, "
                        "QComboBox#exportCombo {\n"
"    background-color: rgba(10,14,23,0.6);\n"
"    color: #EAECEF;\n"
"    border: 1px solid rgba(255,255,255,0.06);\n"
"    border-radius: 6px;\n"
"    font-size: 12px;\n"
"    padding: 0 10px;\n"
"    height: 30px;\n"
"    min-width: 80px;\n"
"}\n"
"QComboBox#fontCombo:hover, QComboBox#sizeCombo:hover, QComboBox#lineSpacingCombo:hover, QComboBox#bgThemeCombo:hover {\n"
"    border-color: rgba(255,255,255,0.12);\n"
"}\n"
"QComboBox#fontCombo::drop-down, QComboBox#sizeCombo::drop-down,\n"
"QComboBox#lineSpacingCombo::drop-down, QComboBox#bgThemeCombo::drop-down, QComboBox#exportCombo::drop-down {\n"
"    border: none;\n"
"    width: 20px;\n"
"}\n"
"QComboBox#fontCombo QAbstractItemView, QComboBox#sizeCombo QAbstractItemView,\n"
"QComboBox#lineSpacingCombo QAbstractItemView, QComboBox#bgThemeCombo QAbstractItemView, QComboBox#exportCombo QAbstractItemView {\n"
"    background-color: #181C24;\n"
"    color: #EAECEF;\n"
"    border: 1px solid rgba(255,255,255,0.08);\n"
"    border-radiu"
                        "s: 8px;\n"
"    selection-background-color: #4D7CFE;\n"
"    selection-color: #FFFFFF;\n"
"    padding: 4px;\n"
"}\n"
"\n"
"/* ===== \u7f16\u8f91\u5668\u6837\u5f0f ===== */\n"
"QTextEdit#editorTextEdit {\n"
"    background-color: rgba(10,14,23,0.5);\n"
"    color: #EAECEF;\n"
"    border: 1px solid rgba(255,255,255,0.04);\n"
"    border-radius: 12px;\n"
"    font-family: \"Microsoft YaHei\", \"PingFang SC\", sans-serif;\n"
"    font-size: 15px;\n"
"    padding: 28px;\n"
"    selection-background-color: #4D7CFE;\n"
"    selection-color: #FFFFFF;\n"
"}\n"
"QTextEdit#editorTextEdit:focus {\n"
"    border-color: #4D7CFE;\n"
"}\n"
"QTextEdit#editorTextEdit QScrollBar:vertical {\n"
"    background-color: transparent;\n"
"    width: 6px;\n"
"    border-radius: 3px;\n"
"}\n"
"QTextEdit#editorTextEdit QScrollBar::handle:vertical {\n"
"    background-color: rgba(255,255,255,0.08);\n"
"    border-radius: 3px;\n"
"    min-height: 40px;\n"
"}\n"
"QTextEdit#editorTextEdit QScrollBar::handle:vertical:hover {\n"
"    backgrou"
                        "nd-color: rgba(255,255,255,0.15);\n"
"}\n"
"\n"
"/* ===== \u5de6\u4fa7\u9762\u677f\u5361\u7247 ===== */\n"
"QFrame#leftPanel {\n"
"    background-color: rgba(10,12,17,0.4);\n"
"    border: none;\n"
"    border-right: 1px solid rgba(255,255,255,0.04);\n"
"}\n"
"\n"
"/* ===== AI\u52a9\u624b\u6309\u94ae\uff08\u5e26\u56fe\u6807\uff09 ===== */\n"
"QPushButton#btnGenOutline, QPushButton#btnWorldBuild, QPushButton#btnCharacter,\n"
"QPushButton#btnContinueWrite, QPushButton#btnPolish, QPushButton#btnDialogue {\n"
"    background-color: transparent;\n"
"    border: none;\n"
"    border-radius: 8px;\n"
"    text-align: left;\n"
"    padding: 10px 12px;\n"
"    font-size: 13px;\n"
"    color: #EAECEF;\n"
"}\n"
"QPushButton#btnGenOutline:hover, QPushButton#btnWorldBuild:hover, QPushButton#btnCharacter:hover,\n"
"QPushButton#btnContinueWrite:hover, QPushButton#btnPolish:hover, QPushButton#btnDialogue:hover {\n"
"    background-color: rgba(255,255,255,0.04);\n"
"}\n"
"\n"
"/* ===== \u65b0\u5efa\u7ae0\u8282\u6309\u94ae ====="
                        " */\n"
"QPushButton#btnNewChapter {\n"
"    background-color: rgba(77,124,254,0.15);\n"
"    color: #4D7CFE;\n"
"    border: none;\n"
"    border-radius: 6px;\n"
"    font-size: 16px;\n"
"    font-weight: 600;\n"
"    width: 28px;\n"
"    height: 28px;\n"
"    padding: 0;\n"
"}\n"
"QPushButton#btnNewChapter:hover {\n"
"    background-color: rgba(77,124,254,0.25);\n"
"}\n"
"\n"
"/* ===== \u6807\u7b7e\u6309\u94ae ===== */\n"
"QPushButton#btnWorldForce, QPushButton#btnWorldMap, QPushButton#btnWorldPower,\n"
"QPushButton#btnCharCard, QPushButton#btnRelationNet {\n"
"    background-color: rgba(40,45,51,0.4);\n"
"    color: #848E9C;\n"
"    border: 1px solid rgba(255,255,255,0.04);\n"
"    border-radius: 6px;\n"
"    font-size: 12px;\n"
"    padding: 0 12px;\n"
"    height: 32px;\n"
"}\n"
"QPushButton#btnWorldForce:hover, QPushButton#btnWorldMap:hover, QPushButton#btnWorldPower:hover,\n"
"QPushButton#btnCharCard:hover, QPushButton#btnRelationNet:hover {\n"
"    background-color: rgba(60,65,71,0.6);\n"
"    color: #E"
                        "AECEF;\n"
"    border-color: rgba(255,255,255,0.08);\n"
"}\n"
"\n"
"/* ===== \u7ae0\u8282\u5217\u8868 ===== */\n"
"QListWidget#chapterList {\n"
"    background-color: transparent;\n"
"    border: none;\n"
"    padding: 0;\n"
"    outline: none;\n"
"    show-decoration-selected: 0;\n"
"}\n"
"QListWidget#chapterList::item {\n"
"    background-color: transparent;\n"
"    color: transparent;\n"
"}\n"
"QListWidget#chapterList::item:hover {\n"
"    background-color: transparent;\n"
"}\n"
"QListWidget#chapterList::item:selected {\n"
"    background-color: transparent;\n"
"    color: transparent;\n"
"}\n"
"QListWidget#chapterList::item:selected:active {\n"
"    background-color: transparent;\n"
"    color: transparent;\n"
"}\n"
"QListWidget#chapterList::item:selected:!active {\n"
"    background-color: transparent;\n"
"    color: transparent;\n"
"}\n"
"QListWidget#chapterList QScrollBar:vertical {\n"
"    background-color: transparent;\n"
"    width: 4px;\n"
"    margin: 0;\n"
"}\n"
"QListWidget#chapterList QScrollBar"
                        "::handle:vertical {\n"
"    background-color: rgba(255,255,255,0.12);\n"
"    border-radius: 2px;\n"
"    min-height: 30px;\n"
"}\n"
"QListWidget#chapterList QScrollBar::handle:vertical:hover {\n"
"    background-color: rgba(255,255,255,0.2);\n"
"}\n"
"QListWidget#chapterList QScrollBar::add-line:vertical,\n"
"QListWidget#chapterList QScrollBar::sub-line:vertical {\n"
"    height: 0;\n"
"    background: none;\n"
"}\n"
"QListWidget#chapterList QScrollBar::add-page:vertical,\n"
"QListWidget#chapterList QScrollBar::sub-page:vertical {\n"
"    background: none;\n"
"}\n"
"\n"
"/* ===== \u8f93\u5165\u6846 ===== */\n"
"QLineEdit#outlineInput {\n"
"    background-color: rgba(10,14,23,0.8);\n"
"    color: #EAECEF;\n"
"    border: 1px solid rgba(255,255,255,0.08);\n"
"    border-radius: 8px;\n"
"    font-size: 12px;\n"
"    padding: 0 12px;\n"
"    height: 36px;\n"
"}\n"
"QLineEdit#outlineInput:focus {\n"
"    border-color: #4D7CFE;\n"
"    box-shadow: 0 0 0 3px rgba(77,124,254,0.1);\n"
"}\n"
"QLineEdit#outlineInput::pl"
                        "aceholder {\n"
"    color: #848E9C;\n"
"    opacity: 0.5;\n"
"}\n"
"\n"
"/* ===== \u5927\u7eb2\u751f\u6210\u6309\u94ae ===== */\n"
"QPushButton#btnGenerateOutline {\n"
"    background-color: #4D7CFE;\n"
"    color: #FFFFFF;\n"
"    border: none;\n"
"    border-radius: 8px;\n"
"    font-size: 14px;\n"
"    font-weight: 500;\n"
"    padding: 8px 16px;\n"
"    height: 40px;\n"
"}\n"
"QPushButton#btnGenerateOutline:hover { background-color: #3D6CF0; }\n"
"QPushButton#btnGenerateOutline:pressed { background-color: #3560E0; }\n"
"\n"
"/* ===== \u72b6\u6001\u680f ===== */\n"
"QFrame#statusBar {\n"
"    background-color: rgba(20,24,32,0.5);\n"
"    border: 1px solid rgba(255,255,255,0.04);\n"
"    border-radius: 8px;\n"
"}\n"
"\n"
"/* ===== \u5206\u5272\u7ebf ===== */\n"
"QFrame[frameShape=\"4\"] {\n"
"    background-color: rgba(255,255,255,0.06);\n"
"}\n"
"\n"
"/* ===== \u9876\u90e8\u6807\u9898 ===== */\n"
"QLabel#pageTitle {\n"
"    color: #EAECEF;\n"
"    font-size: 22px;\n"
"    font-weight: 700;\n"
"}\n"
"QLabel#"
                        "pageSubtitle {\n"
"    color: #848E9C;\n"
"    font-size: 13px;\n"
"}\n"
"\n"
"/* ===== \u5206\u5272\u5668\u624b\u67c4 ===== */\n"
"QSplitter::handle {\n"
"    background-color: rgba(255,255,255,0.04);\n"
"}\n"
"\n"
"/* ===== \u6eda\u52a8\u533a\u57df ===== */\n"
"QScrollArea#rightScrollArea {\n"
"    background-color: transparent;\n"
"    border: none;\n"
"}\n"
"QScrollArea#rightScrollArea > QWidget > QWidget {\n"
"    background-color: transparent;\n"
"}\n"
"QScrollArea#rightScrollArea QScrollBar:vertical {\n"
"    background-color: transparent;\n"
"    width: 6px;\n"
"    border-radius: 3px;\n"
"}\n"
"QScrollArea#rightScrollArea QScrollBar::handle:vertical {\n"
"    background-color: rgba(255,255,255,0.08);\n"
"    border-radius: 3px;\n"
"    min-height: 40px;\n"
"}\n"
"QScrollArea#rightScrollArea QScrollBar::handle:vertical:hover {\n"
"    background-color: rgba(255,255,255,0.15);\n"
"}\n"
"\n"
"/* ===== \u5de6\u4fa7\u6eda\u52a8\u533a\u57df ===== */\n"
"QScrollArea#leftScrollArea {\n"
"    background-color:"
                        " transparent;\n"
"    border: none;\n"
"}\n"
"QScrollArea#leftScrollArea > QWidget > QWidget {\n"
"    background-color: transparent;\n"
"}\n"
"QScrollArea#leftScrollArea QScrollBar:vertical {\n"
"    background-color: transparent;\n"
"    width: 4px;\n"
"    border-radius: 2px;\n"
"}\n"
"QScrollArea#leftScrollArea QScrollBar::handle:vertical {\n"
"    background-color: rgba(255,255,255,0.08);\n"
"    border-radius: 2px;\n"
"    min-height: 30px;\n"
"}\n"
"   ")
        self.mainLayout = QHBoxLayout(SpeedwritePage)
        self.mainLayout.setSpacing(0)
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainSplitter = QSplitter(SpeedwritePage)
        self.mainSplitter.setObjectName(u"mainSplitter")
        self.mainSplitter.setOrientation(Qt.Horizontal)
        self.mainSplitter.setHandleWidth(2)
        self.leftPanel = QFrame(self.mainSplitter)
        self.leftPanel.setObjectName(u"leftPanel")
        self.leftPanel.setMinimumSize(QSize(280, 0))
        self.leftPanel.setMaximumSize(QSize(320, 16777215))
        self.leftOuterLayout = QVBoxLayout(self.leftPanel)
        self.leftOuterLayout.setSpacing(0)
        self.leftOuterLayout.setObjectName(u"leftOuterLayout")
        self.leftOuterLayout.setContentsMargins(0, 0, 0, 0)
        self.leftScrollArea = QScrollArea(self.leftPanel)
        self.leftScrollArea.setObjectName(u"leftScrollArea")
        self.leftScrollArea.setFrameShape(QFrame.NoFrame)
        self.leftScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.leftScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.leftScrollArea.setWidgetResizable(True)
        self.leftScrollContent = QWidget()
        self.leftScrollContent.setObjectName(u"leftScrollContent")
        self.leftInnerLayout = QVBoxLayout(self.leftScrollContent)
        self.leftInnerLayout.setSpacing(12)
        self.leftInnerLayout.setObjectName(u"leftInnerLayout")
        self.leftInnerLayout.setContentsMargins(16, 16, 16, 16)
        self.aiAssistantTitle = QLabel(self.leftScrollContent)
        self.aiAssistantTitle.setObjectName(u"aiAssistantTitle")
        self.aiAssistantTitle.setStyleSheet(u"color: #4D7CFE; font-size: 14px; font-weight: 600; padding-bottom: 8px;")

        self.leftInnerLayout.addWidget(self.aiAssistantTitle)

        self.btnGenOutline = QPushButton(self.leftScrollContent)
        self.btnGenOutline.setObjectName(u"btnGenOutline")
        self.btnGenOutline.setMinimumHeight(52)
        self.btnGenOutline.setStyleSheet(u"\n"
"QPushButton#btnGenOutline {\n"
"    background-color: transparent;\n"
"    border: none;\n"
"    border-radius: 8px;\n"
"    text-align: left;\n"
"    padding: 10px 12px;\n"
"    color: #EAECEF;\n"
"    font-size: 13px;\n"
"}\n"
"QPushButton#btnGenOutline:hover {\n"
"    background-color: rgba(255,255,255,0.04);\n"
"}\n"
"              ")

        self.leftInnerLayout.addWidget(self.btnGenOutline)

        self.btnWorldBuild = QPushButton(self.leftScrollContent)
        self.btnWorldBuild.setObjectName(u"btnWorldBuild")
        self.btnWorldBuild.setMinimumHeight(52)
        self.btnWorldBuild.setStyleSheet(u"\n"
"QPushButton#btnWorldBuild {\n"
"    background-color: transparent;\n"
"    border: none;\n"
"    border-radius: 8px;\n"
"    text-align: left;\n"
"    padding: 10px 12px;\n"
"    color: #EAECEF;\n"
"    font-size: 13px;\n"
"}\n"
"QPushButton#btnWorldBuild:hover {\n"
"    background-color: rgba(255,255,255,0.04);\n"
"}\n"
"              ")

        self.leftInnerLayout.addWidget(self.btnWorldBuild)

        self.btnCharacter = QPushButton(self.leftScrollContent)
        self.btnCharacter.setObjectName(u"btnCharacter")
        self.btnCharacter.setMinimumHeight(52)
        self.btnCharacter.setStyleSheet(u"\n"
"QPushButton#btnCharacter {\n"
"    background-color: transparent;\n"
"    border: none;\n"
"    border-radius: 8px;\n"
"    text-align: left;\n"
"    padding: 10px 12px;\n"
"    color: #EAECEF;\n"
"    font-size: 13px;\n"
"}\n"
"QPushButton#btnCharacter:hover {\n"
"    background-color: rgba(255,255,255,0.04);\n"
"}\n"
"              ")

        self.leftInnerLayout.addWidget(self.btnCharacter)

        self.divider1 = QFrame(self.leftScrollContent)
        self.divider1.setObjectName(u"divider1")
        self.divider1.setFrameShape(QFrame.HLine)
        self.divider1.setMaximumHeight(1)
        self.divider1.setStyleSheet(u"color: rgba(255,255,255,0.04);")

        self.leftInnerLayout.addWidget(self.divider1)

        self.assistSectionTitle = QLabel(self.leftScrollContent)
        self.assistSectionTitle.setObjectName(u"assistSectionTitle")
        self.assistSectionTitle.setStyleSheet(u"color: #848E9C; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px;")

        self.leftInnerLayout.addWidget(self.assistSectionTitle)

        self.btnContinueWrite = QPushButton(self.leftScrollContent)
        self.btnContinueWrite.setObjectName(u"btnContinueWrite")
        self.btnContinueWrite.setMinimumHeight(52)
        self.btnContinueWrite.setStyleSheet(u"\n"
"QPushButton#btnContinueWrite {\n"
"    background-color: transparent;\n"
"    border: none;\n"
"    border-radius: 8px;\n"
"    text-align: left;\n"
"    padding: 10px 12px;\n"
"    color: #EAECEF;\n"
"    font-size: 13px;\n"
"}\n"
"QPushButton#btnContinueWrite:hover {\n"
"    background-color: rgba(255,255,255,0.04);\n"
"}\n"
"              ")

        self.leftInnerLayout.addWidget(self.btnContinueWrite)

        self.btnPolish = QPushButton(self.leftScrollContent)
        self.btnPolish.setObjectName(u"btnPolish")
        self.btnPolish.setMinimumHeight(52)
        self.btnPolish.setStyleSheet(u"\n"
"QPushButton#btnPolish {\n"
"    background-color: transparent;\n"
"    border: none;\n"
"    border-radius: 8px;\n"
"    text-align: left;\n"
"    padding: 10px 12px;\n"
"    color: #EAECEF;\n"
"    font-size: 13px;\n"
"}\n"
"QPushButton#btnPolish:hover {\n"
"    background-color: rgba(255,255,255,0.04);\n"
"}\n"
"              ")

        self.leftInnerLayout.addWidget(self.btnPolish)

        self.btnDialogue = QPushButton(self.leftScrollContent)
        self.btnDialogue.setObjectName(u"btnDialogue")
        self.btnDialogue.setMinimumHeight(52)
        self.btnDialogue.setStyleSheet(u"\n"
"QPushButton#btnDialogue {\n"
"    background-color: transparent;\n"
"    border: none;\n"
"    border-radius: 8px;\n"
"    text-align: left;\n"
"    padding: 10px 12px;\n"
"    color: #EAECEF;\n"
"    font-size: 13px;\n"
"}\n"
"QPushButton#btnDialogue:hover {\n"
"    background-color: rgba(255,255,255,0.04);\n"
"}\n"
"              ")

        self.leftInnerLayout.addWidget(self.btnDialogue)

        self.divider2 = QFrame(self.leftScrollContent)
        self.divider2.setObjectName(u"divider2")
        self.divider2.setFrameShape(QFrame.HLine)
        self.divider2.setMaximumHeight(1)
        self.divider2.setStyleSheet(u"color: rgba(255,255,255,0.04);")

        self.leftInnerLayout.addWidget(self.divider2)

        self.chapterHeaderLayout = QHBoxLayout()
        self.chapterHeaderLayout.setObjectName(u"chapterHeaderLayout")
        self.chapterSectionTitle = QLabel(self.leftScrollContent)
        self.chapterSectionTitle.setObjectName(u"chapterSectionTitle")
        self.chapterSectionTitle.setStyleSheet(u"color: #848E9C; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;")

        self.chapterHeaderLayout.addWidget(self.chapterSectionTitle)

        self.chapterHeaderSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.chapterHeaderLayout.addItem(self.chapterHeaderSpacer)

        self.btnNewChapter = QPushButton(self.leftScrollContent)
        self.btnNewChapter.setObjectName(u"btnNewChapter")
        self.btnNewChapter.setStyleSheet(u"QPushButton#btnNewChapter {\n"
"    background-color: rgba(77,124,254,0.15);\n"
"    color: #4D7CFE;\n"
"    border: none;\n"
"    border-radius: 6px;\n"
"    font-size: 16px;\n"
"    font-weight: 600;\n"
"    width: 28px;\n"
"    height: 28px;\n"
"    padding: 0;\n"
"}\n"
"QPushButton#btnNewChapter:hover {\n"
"    background-color: rgba(77,124,254,0.25);\n"
"}")

        self.chapterHeaderLayout.addWidget(self.btnNewChapter)


        self.leftInnerLayout.addLayout(self.chapterHeaderLayout)

        self.btnNewChapterBig = QPushButton(self.leftScrollContent)
        self.btnNewChapterBig.setObjectName(u"btnNewChapterBig")
        self.btnNewChapterBig.setMinimumHeight(44)
        self.btnNewChapterBig.setStyleSheet(u"QPushButton#btnNewChapterBig {\n"
"    background-color: rgba(30, 35, 41, 0.6);\n"
"    border: 1px solid rgba(255,255,255,0.06);\n"
"    border-radius: 10px;\n"
"    color: #848E9C;\n"
"    font-size: 13px;\n"
"    padding: 10px;\n"
"}\n"
"QPushButton#btnNewChapterBig:hover {\n"
"    background-color: rgba(40, 45, 51, 0.8);\n"
"    border-color: rgba(255,255,255,0.1);\n"
"    color: #EAECEF;\n"
"}")

        self.leftInnerLayout.addWidget(self.btnNewChapterBig)

        self.chapterList = QListWidget(self.leftScrollContent)
        self.chapterList.setObjectName(u"chapterList")
        self.chapterList.setMaximumHeight(400)

        self.leftInnerLayout.addWidget(self.chapterList)

        self.leftSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.leftInnerLayout.addItem(self.leftSpacer)

        self.leftScrollArea.setWidget(self.leftScrollContent)

        self.leftOuterLayout.addWidget(self.leftScrollArea)

        self.mainSplitter.addWidget(self.leftPanel)
        self.rightPanel = QWidget(self.mainSplitter)
        self.rightPanel.setObjectName(u"rightPanel")
        self.rightLayout = QVBoxLayout(self.rightPanel)
        self.rightLayout.setSpacing(0)
        self.rightLayout.setObjectName(u"rightLayout")
        self.rightLayout.setContentsMargins(0, 0, 0, 0)
        self.headerFrame = QFrame(self.rightPanel)
        self.headerFrame.setObjectName(u"headerFrame")
        self.headerFrame.setMinimumHeight(64)
        self.headerFrame.setStyleSheet(u"QFrame#headerFrame {\n"
"    background-color: transparent;\n"
"    border: none;\n"
"    border-bottom: 1px solid rgba(255,255,255,0.04);\n"
"}")
        self.headerLayout = QHBoxLayout(self.headerFrame)
        self.headerLayout.setSpacing(0)
        self.headerLayout.setObjectName(u"headerLayout")
        self.headerLayout.setContentsMargins(20, 12, 20, 12)
        self.headerLeft = QWidget(self.headerFrame)
        self.headerLeft.setObjectName(u"headerLeft")
        self.headerLeftLayout = QVBoxLayout(self.headerLeft)
        self.headerLeftLayout.setSpacing(2)
        self.headerLeftLayout.setObjectName(u"headerLeftLayout")
        self.headerLeftLayout.setContentsMargins(0, 12, 0, 12)
        self.pageTitle = QLabel(self.headerLeft)
        self.pageTitle.setObjectName(u"pageTitle")

        self.headerLeftLayout.addWidget(self.pageTitle)

        self.pageSubtitle = QLabel(self.headerLeft)
        self.pageSubtitle.setObjectName(u"pageSubtitle")

        self.headerLeftLayout.addWidget(self.pageSubtitle)


        self.headerLayout.addWidget(self.headerLeft)

        self.headerSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.headerLayout.addItem(self.headerSpacer)

        self.headerRight = QWidget(self.headerFrame)
        self.headerRight.setObjectName(u"headerRight")
        self.headerRightLayout = QHBoxLayout(self.headerRight)
        self.headerRightLayout.setSpacing(10)
        self.headerRightLayout.setObjectName(u"headerRightLayout")
        self.headerRightLayout.setContentsMargins(0, 12, 0, 12)
        self.btnOpenFile = QPushButton(self.headerRight)
        self.btnOpenFile.setObjectName(u"btnOpenFile")

        self.headerRightLayout.addWidget(self.btnOpenFile)

        self.btnNewTask = QPushButton(self.headerRight)
        self.btnNewTask.setObjectName(u"btnNewTask")

        self.headerRightLayout.addWidget(self.btnNewTask)


        self.headerLayout.addWidget(self.headerRight)


        self.rightLayout.addWidget(self.headerFrame)

        self.toolbarFrame = QFrame(self.rightPanel)
        self.toolbarFrame.setObjectName(u"toolbarFrame")
        self.toolbarFrame.setStyleSheet(u"QFrame#toolbarFrame {\n"
"    background-color: rgba(20,24,32,0.4);\n"
"    border: 1px solid rgba(255,255,255,0.04);\n"
"    border-radius: 10px;\n"
"}")
        self.toolbarOuterLayout = QVBoxLayout(self.toolbarFrame)
        self.toolbarOuterLayout.setSpacing(8)
        self.toolbarOuterLayout.setObjectName(u"toolbarOuterLayout")
        self.toolbarOuterLayout.setContentsMargins(14, 10, 14, 10)
        self.toolbarRow1 = QHBoxLayout()
        self.toolbarRow1.setSpacing(6)
        self.toolbarRow1.setObjectName(u"toolbarRow1")
        self.fontCombo = QComboBox(self.toolbarFrame)
        self.fontCombo.addItem("")
        self.fontCombo.addItem("")
        self.fontCombo.addItem("")
        self.fontCombo.addItem("")
        self.fontCombo.addItem("")
        self.fontCombo.addItem("")
        self.fontCombo.setObjectName(u"fontCombo")
        self.fontCombo.setMinimumSize(QSize(80, 0))

        self.toolbarRow1.addWidget(self.fontCombo)

        self.sizeCombo = QComboBox(self.toolbarFrame)
        self.sizeCombo.addItem("")
        self.sizeCombo.addItem("")
        self.sizeCombo.addItem("")
        self.sizeCombo.addItem("")
        self.sizeCombo.addItem("")
        self.sizeCombo.addItem("")
        self.sizeCombo.addItem("")
        self.sizeCombo.setObjectName(u"sizeCombo")
        self.sizeCombo.setMinimumSize(QSize(70, 0))

        self.toolbarRow1.addWidget(self.sizeCombo)

        self.btnBold = QPushButton(self.toolbarFrame)
        self.btnBold.setObjectName(u"btnBold")
        self.btnBold.setCheckable(True)

        self.toolbarRow1.addWidget(self.btnBold)

        self.btnItalic = QPushButton(self.toolbarFrame)
        self.btnItalic.setObjectName(u"btnItalic")
        self.btnItalic.setCheckable(True)

        self.toolbarRow1.addWidget(self.btnItalic)

        self.btnUnderline = QPushButton(self.toolbarFrame)
        self.btnUnderline.setObjectName(u"btnUnderline")
        self.btnUnderline.setCheckable(True)

        self.toolbarRow1.addWidget(self.btnUnderline)

        self.btnStrike = QPushButton(self.toolbarFrame)
        self.btnStrike.setObjectName(u"btnStrike")
        self.btnStrike.setCheckable(True)
        self.btnStrike.setStyleSheet(u"text-decoration: line-through;")

        self.toolbarRow1.addWidget(self.btnStrike)

        self.btnTextColor = QPushButton(self.toolbarFrame)
        self.btnTextColor.setObjectName(u"btnTextColor")

        self.toolbarRow1.addWidget(self.btnTextColor)

        self.btnBgColor = QPushButton(self.toolbarFrame)
        self.btnBgColor.setObjectName(u"btnBgColor")

        self.toolbarRow1.addWidget(self.btnBgColor)

        self.btnAlignLeft = QPushButton(self.toolbarFrame)
        self.btnAlignLeft.setObjectName(u"btnAlignLeft")
        self.btnAlignLeft.setCheckable(True)

        self.toolbarRow1.addWidget(self.btnAlignLeft)

        self.btnAlignCenter = QPushButton(self.toolbarFrame)
        self.btnAlignCenter.setObjectName(u"btnAlignCenter")
        self.btnAlignCenter.setCheckable(True)

        self.toolbarRow1.addWidget(self.btnAlignCenter)

        self.btnAlignRight = QPushButton(self.toolbarFrame)
        self.btnAlignRight.setObjectName(u"btnAlignRight")
        self.btnAlignRight.setCheckable(True)

        self.toolbarRow1.addWidget(self.btnAlignRight)

        self.btnAlignJustify = QPushButton(self.toolbarFrame)
        self.btnAlignJustify.setObjectName(u"btnAlignJustify")
        self.btnAlignJustify.setCheckable(True)

        self.toolbarRow1.addWidget(self.btnAlignJustify)

        self.btnList = QPushButton(self.toolbarFrame)
        self.btnList.setObjectName(u"btnList")

        self.toolbarRow1.addWidget(self.btnList)

        self.btnOrderedList = QPushButton(self.toolbarFrame)
        self.btnOrderedList.setObjectName(u"btnOrderedList")

        self.toolbarRow1.addWidget(self.btnOrderedList)

        self.btnOutdent = QPushButton(self.toolbarFrame)
        self.btnOutdent.setObjectName(u"btnOutdent")

        self.toolbarRow1.addWidget(self.btnOutdent)

        self.btnIndent = QPushButton(self.toolbarFrame)
        self.btnIndent.setObjectName(u"btnIndent")

        self.toolbarRow1.addWidget(self.btnIndent)

        self.row1Spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.toolbarRow1.addItem(self.row1Spacer)

        self.lineSpacingCombo = QComboBox(self.toolbarFrame)
        self.lineSpacingCombo.addItem("")
        self.lineSpacingCombo.addItem("")
        self.lineSpacingCombo.addItem("")
        self.lineSpacingCombo.setObjectName(u"lineSpacingCombo")
        self.lineSpacingCombo.setMinimumSize(QSize(80, 0))

        self.toolbarRow1.addWidget(self.lineSpacingCombo)

        self.btnUndo = QPushButton(self.toolbarFrame)
        self.btnUndo.setObjectName(u"btnUndo")

        self.toolbarRow1.addWidget(self.btnUndo)

        self.btnRedo = QPushButton(self.toolbarFrame)
        self.btnRedo.setObjectName(u"btnRedo")

        self.toolbarRow1.addWidget(self.btnRedo)


        self.toolbarOuterLayout.addLayout(self.toolbarRow1)

        self.toolbarRow2 = QHBoxLayout()
        self.toolbarRow2.setSpacing(6)
        self.toolbarRow2.setObjectName(u"toolbarRow2")
        self.wordCountLabel = QLabel(self.toolbarFrame)
        self.wordCountLabel.setObjectName(u"wordCountLabel")
        self.wordCountLabel.setStyleSheet(u"color: #848E9C; font-size: 12px; border: 1px solid rgba(255,255,255,0.12); border-radius: 6px; padding: 0 10px; height: 28px;")

        self.toolbarRow2.addWidget(self.wordCountLabel)

        self.exportCombo = QComboBox(self.toolbarFrame)
        self.exportCombo.addItem("")
        self.exportCombo.addItem("")
        self.exportCombo.setObjectName(u"exportCombo")
        self.exportCombo.setMinimumSize(QSize(80, 0))

        self.toolbarRow2.addWidget(self.exportCombo)

        self.row2Spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.toolbarRow2.addItem(self.row2Spacer)

        self.btnMobilePreview = QPushButton(self.toolbarFrame)
        self.btnMobilePreview.setObjectName(u"btnMobilePreview")

        self.toolbarRow2.addWidget(self.btnMobilePreview)

        self.bgThemeCombo = QComboBox(self.toolbarFrame)
        self.bgThemeCombo.addItem("")
        self.bgThemeCombo.addItem("")
        self.bgThemeCombo.addItem("")
        self.bgThemeCombo.addItem("")
        self.bgThemeCombo.addItem("")
        self.bgThemeCombo.setObjectName(u"bgThemeCombo")
        self.bgThemeCombo.setMinimumSize(QSize(100, 0))

        self.toolbarRow2.addWidget(self.bgThemeCombo)


        self.toolbarOuterLayout.addLayout(self.toolbarRow2)


        self.rightLayout.addWidget(self.toolbarFrame)

        self.editorTextEdit = QTextEdit(self.rightPanel)
        self.editorTextEdit.setObjectName(u"editorTextEdit")
        self.editorTextEdit.setAcceptRichText(True)

        self.rightLayout.addWidget(self.editorTextEdit)

        self.statusBar = QFrame(self.rightPanel)
        self.statusBar.setObjectName(u"statusBar")
        self.statusLayout = QHBoxLayout(self.statusBar)
        self.statusLayout.setSpacing(10)
        self.statusLayout.setObjectName(u"statusLayout")
        self.statusLayout.setContentsMargins(14, 6, 14, 6)
        self.statusWordCount = QLabel(self.statusBar)
        self.statusWordCount.setObjectName(u"statusWordCount")
        self.statusWordCount.setStyleSheet(u"color: #848E9C; font-size: 12px;")

        self.statusLayout.addWidget(self.statusWordCount)

        self.statusDot1 = QLabel(self.statusBar)
        self.statusDot1.setObjectName(u"statusDot1")
        self.statusDot1.setStyleSheet(u"color: #848E9C; opacity: 0.3;")

        self.statusLayout.addWidget(self.statusDot1)

        self.statusPageCount = QLabel(self.statusBar)
        self.statusPageCount.setObjectName(u"statusPageCount")
        self.statusPageCount.setStyleSheet(u"color: #848E9C; font-size: 12px;")

        self.statusLayout.addWidget(self.statusPageCount)

        self.statusSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.statusLayout.addItem(self.statusSpacer)

        self.statusDocName = QLabel(self.statusBar)
        self.statusDocName.setObjectName(u"statusDocName")
        self.statusDocName.setStyleSheet(u"color: #848E9C; font-size: 12px;")

        self.statusLayout.addWidget(self.statusDocName)


        self.rightLayout.addWidget(self.statusBar)

        self.mainSplitter.addWidget(self.rightPanel)

        self.mainLayout.addWidget(self.mainSplitter)


        self.retranslateUi(SpeedwritePage)

        QMetaObject.connectSlotsByName(SpeedwritePage)
    # setupUi

    def retranslateUi(self, SpeedwritePage):
        self.aiAssistantTitle.setText(QCoreApplication.translate("SpeedwritePage", u"AI \u521b\u4f5c\u52a9\u624b", None))
        self.btnGenOutline.setText(QCoreApplication.translate("SpeedwritePage", u"\u751f\u6210\u5927\u7eb2\n"
"\u8f93\u5165\u9898\u6750 / \u8bbe\u5b9a\u81ea\u52a8\u751f\u6210", None))
        self.btnWorldBuild.setText(QCoreApplication.translate("SpeedwritePage", u"\u4e16\u754c\u89c2\u6784\u5efa\n"
"\u52bf\u529b \u00b7 \u5730\u56fe \u00b7 \u529b\u91cf\u4f53\u7cfb", None))
        self.btnCharacter.setText(QCoreApplication.translate("SpeedwritePage", u"\u89d2\u8272\u5361\n"
"\u4eba\u7269\u6863\u6848 + \u5173\u7cfb\u7f51", None))
        self.assistSectionTitle.setText(QCoreApplication.translate("SpeedwritePage", u"\u5199\u4f5c\u8f85\u52a9", None))
        self.btnContinueWrite.setText(QCoreApplication.translate("SpeedwritePage", u"\u667a\u80fd\u7eed\u5199\n"
"\u57fa\u4e8e\u4e0a\u6587\u81ea\u52a8\u7eed\u5199", None))
        self.btnPolish.setText(QCoreApplication.translate("SpeedwritePage", u"\u6da6\u8272\u4f18\u5316\n"
"\u63d0\u5347\u6587\u7b14\u6d41\u7545\u5ea6", None))
        self.btnDialogue.setText(QCoreApplication.translate("SpeedwritePage", u"\u5bf9\u8bdd\u751f\u6210\n"
"\u89d2\u8272\u98ce\u683c\u5316\u5bf9\u8bdd", None))
        self.chapterSectionTitle.setText(QCoreApplication.translate("SpeedwritePage", u"\u7ae0\u8282\u5217\u8868", None))
        self.btnNewChapter.setText(QCoreApplication.translate("SpeedwritePage", u"+", None))
        self.btnNewChapterBig.setText(QCoreApplication.translate("SpeedwritePage", u"+  \u65b0\u5efa\u7ae0\u8282", None))
        self.pageTitle.setText(QCoreApplication.translate("SpeedwritePage", u"\u901f\u6587\u521b\u4f5c", None))
        self.pageSubtitle.setText(QCoreApplication.translate("SpeedwritePage", u"AI \u8f85\u52a9\u7f51\u6587\u5199\u4f5c\u5de5\u5177\uff0c\u8212\u9002\u6392\u7248 + AI \u5927\u7eb2\u751f\u6210", None))
        self.btnOpenFile.setText(QCoreApplication.translate("SpeedwritePage", u"\u6253\u5f00\u6587\u4ef6", None))
        self.btnNewTask.setText(QCoreApplication.translate("SpeedwritePage", u"\u65b0\u5efa\u4efb\u52a1", None))
        self.fontCombo.setItemText(0, QCoreApplication.translate("SpeedwritePage", u"\u5b57\u4f53", None))
        self.fontCombo.setItemText(1, QCoreApplication.translate("SpeedwritePage", u"\u5fae\u8f6f\u96c5\u9ed1", None))
        self.fontCombo.setItemText(2, QCoreApplication.translate("SpeedwritePage", u"\u5b8b\u4f53", None))
        self.fontCombo.setItemText(3, QCoreApplication.translate("SpeedwritePage", u"\u9ed1\u4f53", None))
        self.fontCombo.setItemText(4, QCoreApplication.translate("SpeedwritePage", u"\u6977\u4f53", None))
        self.fontCombo.setItemText(5, QCoreApplication.translate("SpeedwritePage", u"\u4eff\u5b8b", None))

        self.sizeCombo.setItemText(0, QCoreApplication.translate("SpeedwritePage", u"\u5b57\u53f7", None))
        self.sizeCombo.setItemText(1, QCoreApplication.translate("SpeedwritePage", u"12", None))
        self.sizeCombo.setItemText(2, QCoreApplication.translate("SpeedwritePage", u"14", None))
        self.sizeCombo.setItemText(3, QCoreApplication.translate("SpeedwritePage", u"16", None))
        self.sizeCombo.setItemText(4, QCoreApplication.translate("SpeedwritePage", u"18", None))
        self.sizeCombo.setItemText(5, QCoreApplication.translate("SpeedwritePage", u"20", None))
        self.sizeCombo.setItemText(6, QCoreApplication.translate("SpeedwritePage", u"24", None))

        self.btnBold.setText(QCoreApplication.translate("SpeedwritePage", u"B", None))
#if QT_CONFIG(tooltip)
        self.btnBold.setToolTip(QCoreApplication.translate("SpeedwritePage", u"\u7c97\u4f53", None))
#endif // QT_CONFIG(tooltip)
        self.btnItalic.setText(QCoreApplication.translate("SpeedwritePage", u"I", None))
#if QT_CONFIG(tooltip)
        self.btnItalic.setToolTip(QCoreApplication.translate("SpeedwritePage", u"\u659c\u4f53", None))
#endif // QT_CONFIG(tooltip)
        self.btnUnderline.setText(QCoreApplication.translate("SpeedwritePage", u"U", None))
#if QT_CONFIG(tooltip)
        self.btnUnderline.setToolTip(QCoreApplication.translate("SpeedwritePage", u"\u4e0b\u5212\u7ebf", None))
#endif // QT_CONFIG(tooltip)
        self.btnStrike.setText(QCoreApplication.translate("SpeedwritePage", u"S", None))
#if QT_CONFIG(tooltip)
        self.btnStrike.setToolTip(QCoreApplication.translate("SpeedwritePage", u"\u5220\u9664\u7ebf", None))
#endif // QT_CONFIG(tooltip)
        self.btnTextColor.setText(QCoreApplication.translate("SpeedwritePage", u"A", None))
#if QT_CONFIG(tooltip)
        self.btnTextColor.setToolTip(QCoreApplication.translate("SpeedwritePage", u"\u6587\u5b57\u989c\u8272", None))
#endif // QT_CONFIG(tooltip)
        self.btnBgColor.setText(QCoreApplication.translate("SpeedwritePage", u"A", None))
#if QT_CONFIG(tooltip)
        self.btnBgColor.setToolTip(QCoreApplication.translate("SpeedwritePage", u"\u80cc\u666f\u989c\u8272", None))
#endif // QT_CONFIG(tooltip)
        self.btnAlignLeft.setText(QCoreApplication.translate("SpeedwritePage", u"\u2af7", None))
#if QT_CONFIG(tooltip)
        self.btnAlignLeft.setToolTip(QCoreApplication.translate("SpeedwritePage", u"\u5de6\u5bf9\u9f50", None))
#endif // QT_CONFIG(tooltip)
        self.btnAlignCenter.setText(QCoreApplication.translate("SpeedwritePage", u"\u21d4", None))
#if QT_CONFIG(tooltip)
        self.btnAlignCenter.setToolTip(QCoreApplication.translate("SpeedwritePage", u"\u5c45\u4e2d\u5bf9\u9f50", None))
#endif // QT_CONFIG(tooltip)
        self.btnAlignRight.setText(QCoreApplication.translate("SpeedwritePage", u"\u2af8", None))
#if QT_CONFIG(tooltip)
        self.btnAlignRight.setToolTip(QCoreApplication.translate("SpeedwritePage", u"\u53f3\u5bf9\u9f50", None))
#endif // QT_CONFIG(tooltip)
        self.btnAlignJustify.setText(QCoreApplication.translate("SpeedwritePage", u"\u2630", None))
#if QT_CONFIG(tooltip)
        self.btnAlignJustify.setToolTip(QCoreApplication.translate("SpeedwritePage", u"\u4e24\u7aef\u5bf9\u9f50", None))
#endif // QT_CONFIG(tooltip)
        self.btnList.setText(QCoreApplication.translate("SpeedwritePage", u"\u2022", None))
#if QT_CONFIG(tooltip)
        self.btnList.setToolTip(QCoreApplication.translate("SpeedwritePage", u"\u65e0\u5e8f\u5217\u8868", None))
#endif // QT_CONFIG(tooltip)
        self.btnOrderedList.setText(QCoreApplication.translate("SpeedwritePage", u"#", None))
#if QT_CONFIG(tooltip)
        self.btnOrderedList.setToolTip(QCoreApplication.translate("SpeedwritePage", u"\u6709\u5e8f\u5217\u8868", None))
#endif // QT_CONFIG(tooltip)
        self.btnOutdent.setText(QCoreApplication.translate("SpeedwritePage", u"\u21e4", None))
#if QT_CONFIG(tooltip)
        self.btnOutdent.setToolTip(QCoreApplication.translate("SpeedwritePage", u"\u51cf\u5c11\u7f29\u8fdb", None))
#endif // QT_CONFIG(tooltip)
        self.btnIndent.setText(QCoreApplication.translate("SpeedwritePage", u"\u21e5", None))
#if QT_CONFIG(tooltip)
        self.btnIndent.setToolTip(QCoreApplication.translate("SpeedwritePage", u"\u589e\u52a0\u7f29\u8fdb", None))
#endif // QT_CONFIG(tooltip)
        self.lineSpacingCombo.setItemText(0, QCoreApplication.translate("SpeedwritePage", u"\u8212\u9002 1.8x", None))
        self.lineSpacingCombo.setItemText(1, QCoreApplication.translate("SpeedwritePage", u"\u7d27\u51d1 1.5x", None))
        self.lineSpacingCombo.setItemText(2, QCoreApplication.translate("SpeedwritePage", u"\u5bbd\u677e 2.0x", None))

        self.btnUndo.setText(QCoreApplication.translate("SpeedwritePage", u"\u21b6", None))
#if QT_CONFIG(tooltip)
        self.btnUndo.setToolTip(QCoreApplication.translate("SpeedwritePage", u"\u64a4\u9500", None))
#endif // QT_CONFIG(tooltip)
        self.btnRedo.setText(QCoreApplication.translate("SpeedwritePage", u"\u21b7", None))
#if QT_CONFIG(tooltip)
        self.btnRedo.setToolTip(QCoreApplication.translate("SpeedwritePage", u"\u91cd\u505a", None))
#endif // QT_CONFIG(tooltip)
        self.wordCountLabel.setText(QCoreApplication.translate("SpeedwritePage", u"<span style=\"color:#4D7CFE;font-weight:600;\">0</span> \u5b57 \u00b7 \u7ea6 0 \u9875", None))
        self.exportCombo.setItemText(0, QCoreApplication.translate("SpeedwritePage", u"\u5e38\u89c4\u5bfc\u51fa", None))
        self.exportCombo.setItemText(1, QCoreApplication.translate("SpeedwritePage", u"\u624b\u673a\u6a21\u5f0f", None))

        self.btnMobilePreview.setText(QCoreApplication.translate("SpeedwritePage", u"\u624b\u673a\u9884\u89c8", None))
        self.bgThemeCombo.setItemText(0, QCoreApplication.translate("SpeedwritePage", u"\u80cc\u666f\u9009\u62e9", None))
        self.bgThemeCombo.setItemText(1, QCoreApplication.translate("SpeedwritePage", u"\u9ed8\u8ba4 (\u767d\u5e95\u9ed1\u5b57)", None))
        self.bgThemeCombo.setItemText(2, QCoreApplication.translate("SpeedwritePage", u"\u67d4\u548c\u62a4\u773c (\u9ec4\u5e95\u9ed1\u5b57)", None))
        self.bgThemeCombo.setItemText(3, QCoreApplication.translate("SpeedwritePage", u"\u591c\u95f4\u6c89\u6d78 (\u9ed1\u5e95\u7070\u5b57)", None))
        self.bgThemeCombo.setItemText(4, QCoreApplication.translate("SpeedwritePage", u"\u6781\u7b80\u81ea\u7136 (\u725b\u76ae\u7eb8)", None))

        self.editorTextEdit.setPlaceholderText(QCoreApplication.translate("SpeedwritePage", u"\u5f00\u59cb\u4f60\u7684\u6545\u4e8b...\n"
"\n"
"\u00b7 \u5bcc\u6587\u672c\u683c\u5f0f\uff08\u52a0\u7c97/\u659c\u4f53/\u4e0b\u5212\u7ebf/\u989c\u8272\uff09\n"
"\u00b7 \u5b57\u4f53\u548c\u5b57\u53f7\u8c03\u8282\n"
"\u00b7 \u5b57\u6570\u7edf\u8ba1\n"
"\u00b7 \u624b\u673a\u9884\u89c8\u6a21\u5f0f\uff08\u70b9\u51fb\u53f3\u4e0a\u89d2\uff09\n"
"\u00b7 AI \u7eed\u5199\uff1a\u9009\u4e2d\u6587\u5b57\u540e\u70b9\u51fb\u300c\u7eed\u5199\u300d\n"
"\u00b7 Ctrl+S \u5feb\u901f\u4fdd\u5b58\n"
"\n"
"\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n"
"\u793a\u4f8b\u5f00\u5934\uff1a \u591c\u8272\u5982\u58a8\uff0c\u66b4\u96e8\u503e\u76c6\u800c\u4e0b\u3002\n"
"\n"
"\u6797\u8fdc\u7ad9\u5728\u65ad\u5d16\u8fb9\uff0c\u4efb\u7531\u96e8\u6c34\u51b2\u5237\u7740\u4ed6\u6ee1\u662f\u8840\u6c61\u7684\u8138\u3002\n"
"\u8eab\u540e\uff0c\u66fe\u7ecf\u8f89\u714c\u7684\u6797\u5bb6\u5927\u9662\u6b64\u523b\u5df2\u662f\u4e00\u7247\u706b\u6d77\uff0c\u558a\u6740"
                        "\u58f0\u6e10\u6e10\u5e73\u606f\uff0c\u53d6\u800c\u4ee3\u4e4b\u7684\u662f\u4e00\u7247\u6b7b\u5bc2\u3002\n"
"\n"
"\u300c\u4e09\u5e74\u4e86......\u300d\u4ed6\u5583\u5583\u81ea\u8bed\uff0c\u63e1\u7d27\u4e86\u624b\u4e2d\u90a3\u679a\u6b8b\u7834\u7684\u7389\u4f69\uff0c\u300c\u6211\u7ec8\u4e8e\u7b49\u5230\u4e86\u8fd9\u4e00\u5929\u3002\u300d", None))
        self.statusWordCount.setText(QCoreApplication.translate("SpeedwritePage", u"<span style=\"color:#4D7CFE;font-weight:600;\">0</span> \u5b57", None))
        self.statusDot1.setText(QCoreApplication.translate("SpeedwritePage", u"\u00b7", None))
        self.statusPageCount.setText(QCoreApplication.translate("SpeedwritePage", u"\u7ea6 <span style=\"font-weight:600;\">0</span> \u9875", None))
        self.statusDocName.setText(QCoreApplication.translate("SpeedwritePage", u"\u672a\u547d\u540d\u6587\u6863", None))
        pass
    # retranslateUi

