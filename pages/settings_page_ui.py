# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'settings_page.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFrame,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QScrollArea, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)

class Ui_SettingsPage(object):
    def setupUi(self, settingsPage):
        if not settingsPage.objectName():
            settingsPage.setObjectName(u"settingsPage")
        settingsPage.resize(780, 640)
        settingsPage.setStyleSheet(u"QWidget#settingsPage { background-color: #0B0E11; }")
        self.mainLayout = QVBoxLayout(settingsPage)
        self.mainLayout.setSpacing(0)
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setContentsMargins(24, 24, 24, 24)
        self.pageTitleLayout = QHBoxLayout()
        self.pageTitleLayout.setSpacing(10)
        self.pageTitleLayout.setObjectName(u"pageTitleLayout")
        self.lblPageIcon = QLabel(settingsPage)
        self.lblPageIcon.setObjectName(u"lblPageIcon")
        self.lblPageIcon.setMinimumSize(QSize(28, 28))
        self.lblPageIcon.setMaximumSize(QSize(28, 28))
        self.lblPageIcon.setAlignment(Qt.AlignCenter)
        self.lblPageIcon.setStyleSheet(u"QLabel#lblPageIcon {\n"
"    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4D7CFE, stop:1 #6B8FFF);\n"
"    border-radius: 6px;\n"
"    color: #FFFFFF;\n"
"    font-size: 14px;\n"
"}")

        self.pageTitleLayout.addWidget(self.lblPageIcon)

        self.lblPageTitle = QLabel(settingsPage)
        self.lblPageTitle.setObjectName(u"lblPageTitle")
        self.lblPageTitle.setStyleSheet(u"color: #EAECEF; font-size: 24px; font-weight: 700; background: transparent; border: none; padding: 0; letter-spacing: -1px;")

        self.pageTitleLayout.addWidget(self.lblPageTitle)


        self.mainLayout.addLayout(self.pageTitleLayout)

        self.scrollArea = QScrollArea(settingsPage)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setStyleSheet(u"QScrollArea { background: transparent; border: none; }\n"
"QScrollArea#scrollArea { background: transparent; border: none; }\n"
"QScrollArea > QWidget { background: #0B0E11; border: none; }")
        self.scrollArea.setWidgetResizable(True)
        self.scrollContent = QWidget()
        self.scrollContent.setObjectName(u"scrollContent")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollContent.sizePolicy().hasHeightForWidth())
        self.scrollContent.setSizePolicy(sizePolicy)
        self.scrollContent.setStyleSheet(u"QWidget#scrollContent { background-color: #0B0E11; }")
        self.scrollLayout = QVBoxLayout(self.scrollContent)
        self.scrollLayout.setSpacing(16)
        self.scrollLayout.setObjectName(u"scrollLayout")
        self.scrollLayout.setContentsMargins(0, 16, 0, 16)
        self.sectionGeneralTitleLayout = QHBoxLayout()
        self.sectionGeneralTitleLayout.setSpacing(8)
        self.sectionGeneralTitleLayout.setObjectName(u"sectionGeneralTitleLayout")
        self.sectionBar = QLabel(self.scrollContent)
        self.sectionBar.setObjectName(u"sectionBar")
        self.sectionBar.setMinimumSize(QSize(3, 14))
        self.sectionBar.setMaximumSize(QSize(3, 14))
        self.sectionBar.setStyleSheet(u"background-color: #4D7CFE; border-radius: 2px;")

        self.sectionGeneralTitleLayout.addWidget(self.sectionBar)

        self.lblSectionGeneral = QLabel(self.scrollContent)
        self.lblSectionGeneral.setObjectName(u"lblSectionGeneral")
        self.lblSectionGeneral.setStyleSheet(u"color: #5E6673; font-size: 12px; font-weight: 600; background: transparent; border: none; padding: 0; letter-spacing: 0.8px;")

        self.sectionGeneralTitleLayout.addWidget(self.lblSectionGeneral)

        self.generalTitleSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.sectionGeneralTitleLayout.addItem(self.generalTitleSpacer)


        self.scrollLayout.addLayout(self.sectionGeneralTitleLayout)

        self.generalCard = QFrame(self.scrollContent)
        self.generalCard.setObjectName(u"generalCard")
        self.generalCard.setStyleSheet(u"QFrame#generalCard {\n"
"    background-color: #1A1A22;\n"
"    border: 1px solid #2B3139;\n"
"    border-radius: 12px;\n"
"}")
        self.generalCardLayout = QVBoxLayout(self.generalCard)
        self.generalCardLayout.setSpacing(0)
        self.generalCardLayout.setObjectName(u"generalCardLayout")
        self.generalCardLayout.setContentsMargins(0, 0, 0, 0)
        self.rowLanguage = QFrame(self.generalCard)
        self.rowLanguage.setObjectName(u"rowLanguage")
        self.rowLanguage.setStyleSheet(u"QFrame#rowLanguage {\n"
"    background-color: #0B0E11;\n"
"    border-bottom: 1px solid #2B3139;\n"
"    padding: 16px 20px;\n"
"    border-top-left-radius: 12px;\n"
"    border-top-right-radius: 12px;\n"
"}")
        self.rowLanguageLayout = QHBoxLayout(self.rowLanguage)
        self.rowLanguageLayout.setSpacing(12)
        self.rowLanguageLayout.setObjectName(u"rowLanguageLayout")
        self.rowLanguageLayout.setContentsMargins(0, 0, 0, 0)
        self.langLabelLayout = QVBoxLayout()
        self.langLabelLayout.setSpacing(2)
        self.langLabelLayout.setObjectName(u"langLabelLayout")
        self.lblLanguage = QLabel(self.rowLanguage)
        self.lblLanguage.setObjectName(u"lblLanguage")
        self.lblLanguage.setStyleSheet(u"color: #EAECEF; font-size: 14px; font-weight: 500; background: transparent; border: none; padding: 0;")

        self.langLabelLayout.addWidget(self.lblLanguage)

        self.lblLanguageHint = QLabel(self.rowLanguage)
        self.lblLanguageHint.setObjectName(u"lblLanguageHint")
        self.lblLanguageHint.setStyleSheet(u"color: #5E6673; font-size: 12px; background: transparent; border: none; padding: 0;")

        self.langLabelLayout.addWidget(self.lblLanguageHint)


        self.rowLanguageLayout.addLayout(self.langLabelLayout)

        self.langSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.rowLanguageLayout.addItem(self.langSpacer)

        self.comboLanguage = QComboBox(self.rowLanguage)
        self.comboLanguage.addItem("")
        self.comboLanguage.addItem("")
        self.comboLanguage.addItem("")
        self.comboLanguage.setObjectName(u"comboLanguage")
        self.comboLanguage.setMinimumSize(QSize(140, 32))
        self.comboLanguage.setMaximumSize(QSize(160, 32))
        self.comboLanguage.setStyleSheet(u"QComboBox {\n"
"    background-color: #14141A;\n"
"    color: #EAECEF;\n"
"    border: 1px solid #2B3139;\n"
"    border-radius: 8px;\n"
"    padding: 0 28px 0 12px;\n"
"    font-size: 13px;\n"
"}\n"
"QComboBox:hover {\n"
"    border: 1px solid #3D4450;\n"
"}\n"
"QComboBox::drop-down {\n"
"    subcontrol-origin: padding;\n"
"    subcontrol-position: top right;\n"
"    width: 24px;\n"
"    border: none;\n"
"}\n"
"QComboBox::down-arrow {\n"
"    width: 0;\n"
"    height: 0;\n"
"    border: 5px solid transparent;\n"
"    border-top-color: #848E9C;\n"
"    margin-right: 4px;\n"
"}\n"
"QComboBox QAbstractItemView {\n"
"    background-color: #14141A;\n"
"    color: #EAECEF;\n"
"    border: 1px solid #2B3139;\n"
"    border-radius: 8px;\n"
"    selection-background-color: #1A1A22;\n"
"    selection-color: #4D7CFE;\n"
"    padding: 4px;\n"
"    outline: none;\n"
"}\n"
"QComboBox QAbstractItemView::item {\n"
"    min-height: 28px;\n"
"    padding: 4px 10px;\n"
"    border-radius: 4px;\n"
"}\n"
"QComboBox QAbstractItemV"
                        "iew::item:hover {\n"
"    background-color: #1A1A22;\n"
"    color: #4D7CFE;\n"
"}")

        self.rowLanguageLayout.addWidget(self.comboLanguage)


        self.generalCardLayout.addWidget(self.rowLanguage)

        self.rowDeveloper = QFrame(self.generalCard)
        self.rowDeveloper.setObjectName(u"rowDeveloper")
        self.rowDeveloper.setStyleSheet(u"QFrame#rowDeveloper {\n"
"    background-color: #0B0E11;\n"
"    padding: 16px 20px;\n"
"    border-bottom-left-radius: 12px;\n"
"    border-bottom-right-radius: 12px;\n"
"}")
        self.rowDeveloperLayout = QHBoxLayout(self.rowDeveloper)
        self.rowDeveloperLayout.setSpacing(12)
        self.rowDeveloperLayout.setObjectName(u"rowDeveloperLayout")
        self.rowDeveloperLayout.setContentsMargins(0, 0, 0, 0)
        self.devLabelLayout = QVBoxLayout()
        self.devLabelLayout.setSpacing(2)
        self.devLabelLayout.setObjectName(u"devLabelLayout")
        self.lblDeveloper = QLabel(self.rowDeveloper)
        self.lblDeveloper.setObjectName(u"lblDeveloper")
        self.lblDeveloper.setStyleSheet(u"color: #EAECEF; font-size: 14px; font-weight: 500; background: transparent; border: none; padding: 0;")

        self.devLabelLayout.addWidget(self.lblDeveloper)

        self.lblDeveloperHint = QLabel(self.rowDeveloper)
        self.lblDeveloperHint.setObjectName(u"lblDeveloperHint")
        self.lblDeveloperHint.setStyleSheet(u"color: #5E6673; font-size: 12px; background: transparent; border: none; padding: 0;")

        self.devLabelLayout.addWidget(self.lblDeveloperHint)


        self.rowDeveloperLayout.addLayout(self.devLabelLayout)

        self.devSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.rowDeveloperLayout.addItem(self.devSpacer)

        self.chkDeveloperMode = QCheckBox(self.rowDeveloper)
        self.chkDeveloperMode.setObjectName(u"chkDeveloperMode")
        self.chkDeveloperMode.setStyleSheet(u"QCheckBox { spacing: 0px; }\n"
"QCheckBox::indicator { width: 20px; height: 20px; }")

        self.rowDeveloperLayout.addWidget(self.chkDeveloperMode)


        self.generalCardLayout.addWidget(self.rowDeveloper)


        self.scrollLayout.addWidget(self.generalCard)

        self.sectionOutputTitleLayout = QHBoxLayout()
        self.sectionOutputTitleLayout.setSpacing(8)
        self.sectionOutputTitleLayout.setObjectName(u"sectionOutputTitleLayout")
        self.sectionBar2 = QLabel(self.scrollContent)
        self.sectionBar2.setObjectName(u"sectionBar2")
        self.sectionBar2.setMinimumSize(QSize(3, 14))
        self.sectionBar2.setMaximumSize(QSize(3, 14))
        self.sectionBar2.setStyleSheet(u"background-color: #4D7CFE; border-radius: 2px;")

        self.sectionOutputTitleLayout.addWidget(self.sectionBar2)

        self.lblSectionOutput = QLabel(self.scrollContent)
        self.lblSectionOutput.setObjectName(u"lblSectionOutput")
        self.lblSectionOutput.setStyleSheet(u"color: #5E6673; font-size: 12px; font-weight: 600; background: transparent; border: none; padding: 0; letter-spacing: 0.8px;")

        self.sectionOutputTitleLayout.addWidget(self.lblSectionOutput)

        self.outputTitleSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.sectionOutputTitleLayout.addItem(self.outputTitleSpacer)


        self.scrollLayout.addLayout(self.sectionOutputTitleLayout)

        self.outputCard = QFrame(self.scrollContent)
        self.outputCard.setObjectName(u"outputCard")
        self.outputCard.setStyleSheet(u"QFrame#outputCard {\n"
"    background-color: #1A1A22;\n"
"    border: 1px solid #2B3139;\n"
"    border-radius: 12px;\n"
"}")
        self.outputCardLayout = QVBoxLayout(self.outputCard)
        self.outputCardLayout.setSpacing(0)
        self.outputCardLayout.setObjectName(u"outputCardLayout")
        self.outputCardLayout.setContentsMargins(0, 0, 0, 0)
        self.rowOutputDir = QFrame(self.outputCard)
        self.rowOutputDir.setObjectName(u"rowOutputDir")
        self.rowOutputDir.setStyleSheet(u"QFrame#rowOutputDir {\n"
"    background-color: #0B0E11;\n"
"    border-bottom: 1px solid #2B3139;\n"
"    padding: 16px 20px;\n"
"    border-top-left-radius: 12px;\n"
"    border-top-right-radius: 12px;\n"
"}")
        self.rowOutputDirLayout = QHBoxLayout(self.rowOutputDir)
        self.rowOutputDirLayout.setSpacing(12)
        self.rowOutputDirLayout.setObjectName(u"rowOutputDirLayout")
        self.rowOutputDirLayout.setContentsMargins(0, 0, 0, 0)
        self.outputDirLabelLayout = QVBoxLayout()
        self.outputDirLabelLayout.setSpacing(2)
        self.outputDirLabelLayout.setObjectName(u"outputDirLabelLayout")
        self.lblOutputDir = QLabel(self.rowOutputDir)
        self.lblOutputDir.setObjectName(u"lblOutputDir")
        self.lblOutputDir.setStyleSheet(u"color: #EAECEF; font-size: 14px; font-weight: 500; background: transparent; border: none; padding: 0;")

        self.outputDirLabelLayout.addWidget(self.lblOutputDir)

        self.lblOutputDirHint = QLabel(self.rowOutputDir)
        self.lblOutputDirHint.setObjectName(u"lblOutputDirHint")
        self.lblOutputDirHint.setStyleSheet(u"color: #5E6673; font-size: 12px; background: transparent; border: none; padding: 0;")

        self.outputDirLabelLayout.addWidget(self.lblOutputDirHint)


        self.rowOutputDirLayout.addLayout(self.outputDirLabelLayout)

        self.outputDirSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.rowOutputDirLayout.addItem(self.outputDirSpacer)

        self.outputDirInputLayout = QHBoxLayout()
        self.outputDirInputLayout.setSpacing(8)
        self.outputDirInputLayout.setObjectName(u"outputDirInputLayout")
        self.editOutputDir = QLineEdit(self.rowOutputDir)
        self.editOutputDir.setObjectName(u"editOutputDir")
        self.editOutputDir.setMinimumSize(QSize(180, 32))
        self.editOutputDir.setMaximumSize(QSize(260, 32))
        self.editOutputDir.setReadOnly(True)
        self.editOutputDir.setStyleSheet(u"QLineEdit {\n"
"    background-color: #14141A;\n"
"    color: #EAECEF;\n"
"    border: 1px solid #2B3139;\n"
"    border-radius: 8px;\n"
"    padding: 0 12px;\n"
"    font-size: 13px;\n"
"}\n"
"QLineEdit:hover {\n"
"    border: 1px solid #3D4450;\n"
"}")

        self.outputDirInputLayout.addWidget(self.editOutputDir)

        self.btnBrowseOutputDir = QPushButton(self.rowOutputDir)
        self.btnBrowseOutputDir.setObjectName(u"btnBrowseOutputDir")
        self.btnBrowseOutputDir.setMinimumSize(QSize(80, 32))
        self.btnBrowseOutputDir.setMaximumSize(QSize(80, 32))
        self.btnBrowseOutputDir.setStyleSheet(u"QPushButton {\n"
"    background-color: #14141A;\n"
"    color: #848E9C;\n"
"    border: 1px solid #2B3139;\n"
"    border-radius: 8px;\n"
"    padding: 0 12px;\n"
"    font-size: 13px;\n"
"}\n"
"QPushButton:hover {\n"
"    border-color: #3D4450;\n"
"    color: #EAECEF;\n"
"}")

        self.outputDirInputLayout.addWidget(self.btnBrowseOutputDir)


        self.rowOutputDirLayout.addLayout(self.outputDirInputLayout)


        self.outputCardLayout.addWidget(self.rowOutputDir)

        self.rowSuffix = QFrame(self.outputCard)
        self.rowSuffix.setObjectName(u"rowSuffix")
        self.rowSuffix.setStyleSheet(u"QFrame#rowSuffix {\n"
"    background-color: #0B0E11;\n"
"    padding: 16px 20px;\n"
"    border-bottom-left-radius: 12px;\n"
"    border-bottom-right-radius: 12px;\n"
"}")
        self.rowSuffixLayout = QHBoxLayout(self.rowSuffix)
        self.rowSuffixLayout.setSpacing(12)
        self.rowSuffixLayout.setObjectName(u"rowSuffixLayout")
        self.rowSuffixLayout.setContentsMargins(0, 0, 0, 0)
        self.suffixLabelLayout = QVBoxLayout()
        self.suffixLabelLayout.setSpacing(2)
        self.suffixLabelLayout.setObjectName(u"suffixLabelLayout")
        self.lblSuffix = QLabel(self.rowSuffix)
        self.lblSuffix.setObjectName(u"lblSuffix")
        self.lblSuffix.setStyleSheet(u"color: #EAECEF; font-size: 14px; font-weight: 500; background: transparent; border: none; padding: 0;")

        self.suffixLabelLayout.addWidget(self.lblSuffix)

        self.lblSuffixHint = QLabel(self.rowSuffix)
        self.lblSuffixHint.setObjectName(u"lblSuffixHint")
        self.lblSuffixHint.setStyleSheet(u"color: #5E6673; font-size: 12px; background: transparent; border: none; padding: 0;")

        self.suffixLabelLayout.addWidget(self.lblSuffixHint)


        self.rowSuffixLayout.addLayout(self.suffixLabelLayout)

        self.suffixSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.rowSuffixLayout.addItem(self.suffixSpacer)

        self.suffixInputLayout = QHBoxLayout()
        self.suffixInputLayout.setSpacing(6)
        self.suffixInputLayout.setObjectName(u"suffixInputLayout")
        self.editSuffix = QLineEdit(self.rowSuffix)
        self.editSuffix.setObjectName(u"editSuffix")
        self.editSuffix.setMinimumSize(QSize(80, 32))
        self.editSuffix.setMaximumSize(QSize(80, 32))
        self.editSuffix.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.editSuffix.setStyleSheet(u"QLineEdit {\n"
"    background-color: #14141A;\n"
"    color: #EAECEF;\n"
"    border: 1px solid #2B3139;\n"
"    border-radius: 8px;\n"
"    padding: 0 8px;\n"
"    font-size: 13px;\n"
"    font-family: monospace;\n"
"}\n"
"QLineEdit:hover {\n"
"    border: 1px solid #3D4450;\n"
"}\n"
"QLineEdit:focus {\n"
"    border: 1px solid #4D7CFE;\n"
"}")

        self.suffixInputLayout.addWidget(self.editSuffix)

        self.lblSuffixExt = QLabel(self.rowSuffix)
        self.lblSuffixExt.setObjectName(u"lblSuffixExt")
        self.lblSuffixExt.setStyleSheet(u"color: #5E6673; font-size: 12px; background: transparent; border: none; padding: 0;")

        self.suffixInputLayout.addWidget(self.lblSuffixExt)


        self.rowSuffixLayout.addLayout(self.suffixInputLayout)


        self.outputCardLayout.addWidget(self.rowSuffix)


        self.scrollLayout.addWidget(self.outputCard)

        self.sectionAboutTitleLayout = QHBoxLayout()
        self.sectionAboutTitleLayout.setSpacing(8)
        self.sectionAboutTitleLayout.setObjectName(u"sectionAboutTitleLayout")
        self.sectionBar3 = QLabel(self.scrollContent)
        self.sectionBar3.setObjectName(u"sectionBar3")
        self.sectionBar3.setMinimumSize(QSize(3, 14))
        self.sectionBar3.setMaximumSize(QSize(3, 14))
        self.sectionBar3.setStyleSheet(u"background-color: #4D7CFE; border-radius: 2px;")

        self.sectionAboutTitleLayout.addWidget(self.sectionBar3)

        self.lblSectionAbout = QLabel(self.scrollContent)
        self.lblSectionAbout.setObjectName(u"lblSectionAbout")
        self.lblSectionAbout.setStyleSheet(u"color: #5E6673; font-size: 12px; font-weight: 600; background: transparent; border: none; padding: 0; letter-spacing: 0.8px;")

        self.sectionAboutTitleLayout.addWidget(self.lblSectionAbout)

        self.aboutTitleSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.sectionAboutTitleLayout.addItem(self.aboutTitleSpacer)


        self.scrollLayout.addLayout(self.sectionAboutTitleLayout)

        self.aboutCard = QFrame(self.scrollContent)
        self.aboutCard.setObjectName(u"aboutCard")
        self.aboutCard.setStyleSheet(u"QFrame#aboutCard {\n"
"    background-color: #1A1A22;\n"
"    border: 1px solid #2B3139;\n"
"    border-radius: 12px;\n"
"    padding: 20px 24px;\n"
"}")
        self.aboutCardLayout = QHBoxLayout(self.aboutCard)
        self.aboutCardLayout.setSpacing(16)
        self.aboutCardLayout.setObjectName(u"aboutCardLayout")
        self.aboutCardLayout.setContentsMargins(0, 0, 0, 0)
        self.lblAboutIcon = QLabel(self.aboutCard)
        self.lblAboutIcon.setObjectName(u"lblAboutIcon")
        self.lblAboutIcon.setMinimumSize(QSize(44, 44))
        self.lblAboutIcon.setMaximumSize(QSize(44, 44))
        self.lblAboutIcon.setAlignment(Qt.AlignCenter)
        self.lblAboutIcon.setStyleSheet(u"QLabel#lblAboutIcon {\n"
"    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4D7CFE, stop:1 #6B8FFF);\n"
"    border-radius: 10px;\n"
"    color: #FFFFFF;\n"
"    font-size: 20px;\n"
"}")

        self.aboutCardLayout.addWidget(self.lblAboutIcon)

        self.aboutInfoLayout = QVBoxLayout()
        self.aboutInfoLayout.setSpacing(3)
        self.aboutInfoLayout.setObjectName(u"aboutInfoLayout")
        self.lblAppName = QLabel(self.aboutCard)
        self.lblAppName.setObjectName(u"lblAppName")
        self.lblAppName.setStyleSheet(u"color: #EAECEF; font-size: 15px; font-weight: 700; background: transparent; border: none; padding: 0;")

        self.aboutInfoLayout.addWidget(self.lblAppName)

        self.lblAppVersion = QLabel(self.aboutCard)
        self.lblAppVersion.setObjectName(u"lblAppVersion")
        self.lblAppVersion.setStyleSheet(u"color: #848E9C; font-size: 12px; background: transparent; border: none; padding: 0;")

        self.aboutInfoLayout.addWidget(self.lblAppVersion)

        self.lblAppDesc = QLabel(self.aboutCard)
        self.lblAppDesc.setObjectName(u"lblAppDesc")
        self.lblAppDesc.setStyleSheet(u"color: #5E6673; font-size: 11px; background: transparent; border: none; padding: 0;")

        self.aboutInfoLayout.addWidget(self.lblAppDesc)


        self.aboutCardLayout.addLayout(self.aboutInfoLayout)

        self.aboutInfoSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.aboutCardLayout.addItem(self.aboutInfoSpacer)

        self.aboutBtnLayout = QHBoxLayout()
        self.aboutBtnLayout.setSpacing(8)
        self.aboutBtnLayout.setObjectName(u"aboutBtnLayout")
        self.btnCheckUpdate = QPushButton(self.aboutCard)
        self.btnCheckUpdate.setObjectName(u"btnCheckUpdate")
        self.btnCheckUpdate.setMinimumSize(QSize(0, 30))
        self.btnCheckUpdate.setStyleSheet(u"QPushButton {\n"
"    background-color: transparent;\n"
"    color: #848E9C;\n"
"    border: 1px solid #2B3139;\n"
"    border-radius: 8px;\n"
"    padding: 0 14px;\n"
"    font-size: 12px;\n"
"    font-weight: 500;\n"
"}\n"
"QPushButton:hover {\n"
"    border-color: #3D4450;\n"
"    color: #EAECEF;\n"
"}")

        self.aboutBtnLayout.addWidget(self.btnCheckUpdate)

        self.btnFeedback = QPushButton(self.aboutCard)
        self.btnFeedback.setObjectName(u"btnFeedback")
        self.btnFeedback.setMinimumSize(QSize(0, 30))
        self.btnFeedback.setStyleSheet(u"QPushButton {\n"
"    background-color: transparent;\n"
"    color: #848E9C;\n"
"    border: 1px solid #2B3139;\n"
"    border-radius: 8px;\n"
"    padding: 0 14px;\n"
"    font-size: 12px;\n"
"    font-weight: 500;\n"
"}\n"
"QPushButton:hover {\n"
"    border-color: #3D4450;\n"
"    color: #EAECEF;\n"
"}")

        self.aboutBtnLayout.addWidget(self.btnFeedback)


        self.aboutCardLayout.addLayout(self.aboutBtnLayout)


        self.scrollLayout.addWidget(self.aboutCard)

        self.lblFooterHint = QLabel(self.scrollContent)
        self.lblFooterHint.setObjectName(u"lblFooterHint")
        self.lblFooterHint.setAlignment(Qt.AlignCenter)
        self.lblFooterHint.setStyleSheet(u"color: #4A4B56; font-size: 11px; background: transparent; border: none; padding: 8px 0;")

        self.scrollLayout.addWidget(self.lblFooterHint)

        self.spacerBottom = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.scrollLayout.addItem(self.spacerBottom)

        self.scrollArea.setWidget(self.scrollContent)

        self.mainLayout.addWidget(self.scrollArea)


        self.retranslateUi(settingsPage)

        QMetaObject.connectSlotsByName(settingsPage)
    # setupUi

    def retranslateUi(self, settingsPage):
        self.lblPageIcon.setText("")
        self.lblPageTitle.setText(QCoreApplication.translate("SettingsPage", u"\u8bbe\u7f6e", None))
        self.sectionBar.setText("")
        self.lblSectionGeneral.setText(QCoreApplication.translate("SettingsPage", u"\u901a\u7528", None))
        self.lblLanguage.setText(QCoreApplication.translate("SettingsPage", u"\u8bed\u8a00", None))
        self.lblLanguageHint.setText(QCoreApplication.translate("SettingsPage", u"\u754c\u9762\u663e\u793a\u8bed\u8a00", None))
        self.comboLanguage.setItemText(0, QCoreApplication.translate("SettingsPage", u"\u7b80\u4f53\u4e2d\u6587", None))
        self.comboLanguage.setItemText(1, QCoreApplication.translate("SettingsPage", u"\u7e41\u9ad4\u4e2d\u6587", None))
        self.comboLanguage.setItemText(2, QCoreApplication.translate("SettingsPage", u"English", None))

        self.lblDeveloper.setText(QCoreApplication.translate("SettingsPage", u"\u5f00\u53d1\u8005\u6a21\u5f0f", None))
        self.lblDeveloperHint.setText(QCoreApplication.translate("SettingsPage", u"\u663e\u793a\u300c\u901f\u6587\u521b\u4f5c\u300d\u7b49\u5b9e\u9a8c\u6027\u529f\u80fd", None))
        self.chkDeveloperMode.setText("")
        self.sectionBar2.setText("")
        self.lblSectionOutput.setText(QCoreApplication.translate("SettingsPage", u"\u8f93\u51fa", None))
        self.lblOutputDir.setText(QCoreApplication.translate("SettingsPage", u"\u9ed8\u8ba4\u8f93\u51fa\u76ee\u5f55", None))
        self.lblOutputDirHint.setText(QCoreApplication.translate("SettingsPage", u"\u5904\u7406\u540e\u7684\u6587\u4ef6\u9ed8\u8ba4\u4fdd\u5b58\u4f4d\u7f6e", None))
        self.editOutputDir.setPlaceholderText(QCoreApplication.translate("SettingsPage", u"\u8f93\u5165\u6587\u4ef6\u6240\u5728\u76ee\u5f55", None))
        self.btnBrowseOutputDir.setText(QCoreApplication.translate("SettingsPage", u"\u6d4f\u89c8...", None))
        self.lblSuffix.setText(QCoreApplication.translate("SettingsPage", u"\u6587\u4ef6\u540d\u540e\u7f00", None))
        self.lblSuffixHint.setText(QCoreApplication.translate("SettingsPage", u"\u81ea\u52a8\u4e3a\u8f93\u51fa\u6587\u4ef6\u6dfb\u52a0\u540e\u7f00\u540d", None))
        self.editSuffix.setText(QCoreApplication.translate("SettingsPage", u"_out", None))
        self.lblSuffixExt.setText(QCoreApplication.translate("SettingsPage", u"+ \u6269\u5c55\u540d", None))
        self.sectionBar3.setText("")
        self.lblSectionAbout.setText(QCoreApplication.translate("SettingsPage", u"\u5173\u4e8e", None))
        self.lblAboutIcon.setText("")
        self.lblAppName.setText(QCoreApplication.translate("SettingsPage", u"\u5370\u6d41PDflow", None))
        self.lblAppVersion.setText(QCoreApplication.translate("SettingsPage", u"v1.2 \u00b7 2026.06.13", None))
        self.lblAppDesc.setText(QCoreApplication.translate("SettingsPage", u"\u8bbe\u8ba1\u5e08\u4e13\u7528\u7684\u8f7b\u91cf\u7ea7 PDF \u5de5\u5177\u7bb1", None))
        self.btnCheckUpdate.setText(QCoreApplication.translate("SettingsPage", u"\u68c0\u67e5\u66f4\u65b0", None))
        self.btnFeedback.setText(QCoreApplication.translate("SettingsPage", u"\u53cd\u9988", None))
        self.lblFooterHint.setText(QCoreApplication.translate("SettingsPage", u"\u8bbe\u7f6e\u4fee\u6539\u540e\u81ea\u52a8\u4fdd\u5b58 \u00b7 \u8bed\u8a00\u5207\u6362\u9700\u91cd\u542f\u751f\u6548", None))
        pass
    # retranslateUi

