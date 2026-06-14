# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'merge_page.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QPushButton, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

class Ui_MergePage(object):
    def setupUi(self, MergePage):
        if not MergePage.objectName():
            MergePage.setObjectName(u"MergePage")
        MergePage.resize(1280, 820)
        MergePage.setMinimumSize(QSize(1280, 820))
        MergePage.setStyleSheet(u"QWidget#MergePage {\n"
"    background-color: #0B0E11;\n"
"}\n"
"\n"
"/* ===== \u4e3b\u8981\u6309\u94ae\u6837\u5f0f ===== */\n"
"QPushButton#btnAddPdf, QPushButton#btnMergePdf {\n"
"    background-color: #4D7CFE;\n"
"    color: #FFFFFF;\n"
"    border: none;\n"
"    border-radius: 8px;\n"
"    font-family: \"Inter\", \"\u5fae\u8f6f\u96c5\u9ed1\";\n"
"    font-size: 14px;\n"
"    font-weight: 500;\n"
"    padding: 8px 20px;\n"
"}\n"
"\n"
"QPushButton#btnAddPdf:hover, QPushButton#btnMergePdf:hover {\n"
"    background-color: #3D6CF0;\n"
"}\n"
"\n"
"QPushButton#btnAddPdf:pressed, QPushButton#btnMergePdf:pressed {\n"
"    background-color: #3560E0;\n"
"}\n"
"\n"
"/* ===== \u6587\u5b57\u6309\u94ae\u6837\u5f0f\uff08\u6e05\u7a7a\u5168\u90e8\uff09 ===== */\n"
"QPushButton#btnClearAll {\n"
"    background-color: transparent;\n"
"    color: #848E9C;\n"
"    border: none;\n"
"    border-radius: 8px;\n"
"    font-family: \"Inter\", \"\u5fae\u8f6f\u96c5\u9ed1\";\n"
"    font-size: 14px;\n"
"    padding: 8px 16px;\n"
"}\n"
""
                        "\n"
"QPushButton#btnClearAll:hover {\n"
"    color: #EAECEF;\n"
"}\n"
"\n"
"/* ===== \u6b21\u8981\u6309\u94ae\u6837\u5f0f\uff08\u5408\u5e76/\u62c6\u5206\uff09 ===== */\n"
"QPushButton#btnMerge, QPushButton#btnSplit {\n"
"    background-color: #1E2329;\n"
"    color: #EAECEF;\n"
"    border: 1px solid #2B3139;\n"
"    border-radius: 8px;\n"
"    font-family: \"Inter\", \"\u5fae\u8f6f\u96c5\u9ed1\";\n"
"    font-size: 14px;\n"
"    padding: 6px 20px;\n"
"}\n"
"\n"
"QPushButton#btnMerge:hover, QPushButton#btnSplit:hover {\n"
"    background-color: #282D35;\n"
"    border-color: #3D4450;\n"
"}\n"
"\n"
"/* ===== \u6587\u4ef6\u5217\u8868\u6837\u5f0f ===== */\n"
"QListWidget#fileListWidget {\n"
"    background-color: #1A1A22;\n"
"    border: 1px solid #2B3139;\n"
"    border-radius: 8px;\n"
"    font-family: \"Inter\", \"\u5fae\u8f6f\u96c5\u9ed1\";\n"
"    font-size: 14px;\n"
"    color: #EAECEF;\n"
"    outline: none;\n"
"    padding: 4px;\n"
"}\n"
"\n"
"QListWidget#fileListWidget::item {\n"
"    height: 44px;\n"
" "
                        "   border-radius: 6px;\n"
"    padding: 0px 12px;\n"
"    color: #EAECEF;\n"
"}\n"
"\n"
"QListWidget#fileListWidget::item:hover {\n"
"    background-color: #1E2329;\n"
"}\n"
"\n"
"QListWidget#fileListWidget::item:selected {\n"
"    background-color: #2A3040;\n"
"    color: #FFFFFF;\n"
"}\n"
"\n"
"/* ===== \u72b6\u6001\u6807\u7b7e ===== */\n"
"QLabel#lblFileCount {\n"
"    color: #848E9C;\n"
"    font-family: \"Inter\", \"\u5fae\u8f6f\u96c5\u9ed1\";\n"
"    font-size: 13px;\n"
"}\n"
"\n"
"QLabel#lblHint {\n"
"    color: #848E9C;\n"
"    font-family: \"Inter\", \"\u5fae\u8f6f\u96c5\u9ed1\";\n"
"    font-size: 13px;\n"
"}")
        self.mainLayout = QVBoxLayout(MergePage)
        self.mainLayout.setSpacing(16)
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setContentsMargins(24, 20, 24, 20)
        self.topBarLayout = QHBoxLayout()
        self.topBarLayout.setSpacing(16)
        self.topBarLayout.setObjectName(u"topBarLayout")
        self.btnAddPdf = QPushButton(MergePage)
        self.btnAddPdf.setObjectName(u"btnAddPdf")
        self.btnAddPdf.setMinimumSize(QSize(0, 40))
        self.btnAddPdf.setMaximumSize(QSize(16777215, 40))

        self.topBarLayout.addWidget(self.btnAddPdf)

        self.btnClearAll = QPushButton(MergePage)
        self.btnClearAll.setObjectName(u"btnClearAll")
        self.btnClearAll.setMinimumSize(QSize(0, 40))
        self.btnClearAll.setMaximumSize(QSize(16777215, 40))

        self.topBarLayout.addWidget(self.btnClearAll)

        self.lblFileCount = QLabel(MergePage)
        self.lblFileCount.setObjectName(u"lblFileCount")

        self.topBarLayout.addWidget(self.lblFileCount)

        self.topBarSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.topBarLayout.addItem(self.topBarSpacer)


        self.mainLayout.addLayout(self.topBarLayout)

        self.fileListWidget = QListWidget(MergePage)
        self.fileListWidget.setObjectName(u"fileListWidget")

        self.mainLayout.addWidget(self.fileListWidget)

        self.mergeSplitLayout = QHBoxLayout()
        self.mergeSplitLayout.setSpacing(16)
        self.mergeSplitLayout.setObjectName(u"mergeSplitLayout")
        self.btnMerge = QPushButton(MergePage)
        self.btnMerge.setObjectName(u"btnMerge")
        self.btnMerge.setMinimumSize(QSize(0, 36))
        self.btnMerge.setMaximumSize(QSize(16777215, 36))

        self.mergeSplitLayout.addWidget(self.btnMerge)

        self.btnSplit = QPushButton(MergePage)
        self.btnSplit.setObjectName(u"btnSplit")
        self.btnSplit.setMinimumSize(QSize(0, 36))
        self.btnSplit.setMaximumSize(QSize(16777215, 36))

        self.mergeSplitLayout.addWidget(self.btnSplit)

        self.mergeSplitSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.mergeSplitLayout.addItem(self.mergeSplitSpacer)


        self.mainLayout.addLayout(self.mergeSplitLayout)

        self.bottomLayout = QVBoxLayout()
        self.bottomLayout.setSpacing(12)
        self.bottomLayout.setObjectName(u"bottomLayout")
        self.lblHint = QLabel(MergePage)
        self.lblHint.setObjectName(u"lblHint")

        self.bottomLayout.addWidget(self.lblHint)

        self.btnMergePdf = QPushButton(MergePage)
        self.btnMergePdf.setObjectName(u"btnMergePdf")
        self.btnMergePdf.setMinimumSize(QSize(0, 40))
        self.btnMergePdf.setMaximumSize(QSize(16777215, 40))

        self.bottomLayout.addWidget(self.btnMergePdf)


        self.mainLayout.addLayout(self.bottomLayout)


        self.retranslateUi(MergePage)

        QMetaObject.connectSlotsByName(MergePage)
    # setupUi

    def retranslateUi(self, MergePage):
        self.btnAddPdf.setText(QCoreApplication.translate("MergePage", u"\u6dfb\u52a0PDF\u6587\u4ef6", None))
        self.btnClearAll.setText(QCoreApplication.translate("MergePage", u"\u6e05\u7a7a\u5168\u90e8", None))
        self.lblFileCount.setText(QCoreApplication.translate("MergePage", u"\u5df2\u6dfb\u52a0 0 \u4e2a\u6587\u4ef6", None))
        self.btnMerge.setText(QCoreApplication.translate("MergePage", u"\u5408\u5e76", None))
        self.btnSplit.setText(QCoreApplication.translate("MergePage", u"\u62c6\u5206", None))
        self.lblHint.setText(QCoreApplication.translate("MergePage", u"\u9009\u62e9\u81f3\u5c112\u4e2aPDF\u6587\u4ef6\uff0c\u5408\u5e76\u4e3a\u4e00\u4e2aPDF\u6587\u4ef6", None))
        self.btnMergePdf.setText(QCoreApplication.translate("MergePage", u"\u5408\u5e76\u4e3a\u5355\u4e2aPDF", None))
        pass
    # retranslateUi


# ================================================================
# MergePage — PySide6 合并拆分功能页面
# 使用编译的 Ui_MergePage，支持合并和拆分两种模式
# 后端：调用 src/common/pdf_api
# 文件选择：QFileDialog
# ================================================================
import os

from PySide6.QtCore import Qt, QThread, Signal, QSize, QTimer
from PySide6.QtWidgets import (
    QWidget, QListWidgetItem, QRadioButton, QButtonGroup,
    QSpinBox, QLineEdit, QLabel, QVBoxLayout, QHBoxLayout,
    QFrame, QFileDialog,
)
from src.common.pdf_api import merge_pdfs, split_pdf
from src.common.recent_files_manager import add_record
from src.common.error_handler import ErrorHandler, ErrorType
from translations.translation_manager import _ as _tr


# ── 文件列表项角色 ──
_FILE_PATH_ROLE = Qt.UserRole + 1
_FILE_SIZE_ROLE = Qt.UserRole + 2


# ── 样式常量 ──
RADIO_STYLE = """
    QRadioButton {
        color: #EAECEF;
        font-size: 14px;
        spacing: 8px;
        background: transparent;
        border: none;
    }
    QRadioButton::indicator {
        width: 16px;
        height: 16px;
        border-radius: 8px;
        border: 2px solid #2B3139;
        background-color: transparent;
    }
    QRadioButton::indicator:checked {
        border: 2px solid #4D7CFE;
        background-color: #4D7CFE;
    }
"""

SPINBOX_STYLE = """
    QSpinBox {
        background-color: #1A1A22;
        border: 1px solid #2B3139;
        border-radius: 6px;
        color: #EAECEF;
        padding: 4px 8px;
        min-height: 28px;
    }
"""

LINEEDIT_STYLE = """
    QLineEdit {
        background-color: #1A1A22;
        border: 1px solid #2B3139;
        border-radius: 6px;
        color: #EAECEF;
        font-size: 14px;
        padding: 8px 12px;
        min-height: 18px;
    }
    QLineEdit:focus {
        border: 1px solid #4D7CFE;
    }
"""

BTN_ACTIVE_STYLE = """
    QPushButton {
        background-color: #4D7CFE;
        color: #FFFFFF;
        border: none;
        border-radius: 8px;
        font-size: 14px;
        padding: 6px 20px;
    }
    QPushButton:hover {
        background-color: #3D6CF0;
    }
"""

BTN_INACTIVE_STYLE = """
    QPushButton {
        background-color: #1E2329;
        color: #EAECEF;
        border: 1px solid #2B3139;
        border-radius: 8px;
        font-size: 14px;
        padding: 6px 20px;
    }
    QPushButton:hover {
        background-color: #282D35;
        border-color: #3D4450;
    }
"""


# ================================================================
# 工作线程：合并
# ================================================================
class MergeWorker(QThread):
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, output_path, file_list):
        super().__init__()
        self._output_path = output_path
        self._file_list = file_list

    def run(self):
        try:
            result = merge_pdfs(self._output_path, *self._file_list)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


# ================================================================
# 工作线程：拆分
# ================================================================
class SplitWorker(QThread):
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, filepath, output_dir, mode, range_str=None):
        super().__init__()
        self._filepath = filepath
        self._output_dir = output_dir
        self._mode = mode
        self._range_str = range_str

    def run(self):
        try:
            result = split_pdf(self._filepath, self._output_dir,
                               mode=self._mode, range_str=self._range_str)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


# ================================================================
# MergePage — 主页面
# ================================================================
class MergePage(QWidget):
    """合并拆分功能页面，使用编译的 Ui_MergePage"""

    def __init__(self):
        super().__init__()
        self._file_list = []
        self._merge_mode = True           # True=合并, False=拆分
        self._is_busy = False
        self._ph_item = None              # 空列表占位项

        # 加载编译的 UI
        self.ui = Ui_MergePage()
        self.ui.setupUi(self)

        # 构建动态控件（状态标签 + 拆分参数区）
        self._build_dynamic_ui()

        # 启用拖拽排序
        self.ui.fileListWidget.setDragDropMode(QListWidget.InternalMove)
        self.ui.fileListWidget.setDefaultDropAction(Qt.MoveAction)
        self.ui.fileListWidget.model().rowsMoved.connect(self._on_rows_moved)

        # 连接信号
        self._connect_signals()

        # 初始状态
        self._update_placeholder()
        self._update_file_ui()
        self._update_mode_ui()

    # ────────────────────────────────────────────────
    # 动态 UI 构建
    # ────────────────────────────────────────────────

    def _build_dynamic_ui(self):
        """在编译 UI 基础上添加共用状态标签和拆分模式参数控件"""
        # 状态标签（合并/拆分共用）
        self._status_lbl = QLabel("")
        self._status_lbl.setStyleSheet("color: #848E9C; font-size: 13px;")
        self._status_lbl.setWordWrap(True)
        self.ui.bottomLayout.addWidget(self._status_lbl)

        # 拆分参数区域（默认隐藏）
        self._split_params = QWidget()
        sp_lay = QVBoxLayout(self._split_params)
        sp_lay.setContentsMargins(0, 4, 0, 4)
        sp_lay.setSpacing(8)

        # 拆分模式：单选框组
        self._split_mode_group = QButtonGroup(self)
        self._rb_every = QRadioButton(_tr("每页单独保存"))
        self._rb_ranges = QRadioButton(_tr("按页码范围拆分"))
        self._rb_every.setStyleSheet(RADIO_STYLE)
        self._rb_ranges.setStyleSheet(RADIO_STYLE)
        self._split_mode_group.addButton(self._rb_every, 1)
        self._split_mode_group.addButton(self._rb_ranges, 2)
        self._rb_every.setChecked(True)
        self._split_mode_group.idClicked.connect(self._on_split_mode_changed)
        sp_lay.addWidget(self._rb_every)
        sp_lay.addWidget(self._rb_ranges)

        # 每 N 页参数行
        self._split_every_row = QHBoxLayout()
        self._lbl_every_prefix = QLabel(_tr("每"))
        self._split_every_row.addWidget(self._lbl_every_prefix)
        self._split_every_spin = QSpinBox()
        self._split_every_spin.setRange(1, 999)
        self._split_every_spin.setValue(1)
        self._split_every_spin.setFixedWidth(70)
        self._split_every_spin.setStyleSheet(SPINBOX_STYLE)
        self._split_every_row.addWidget(self._split_every_spin)
        self._lbl_every_suffix = QLabel(_tr("页为一份"))
        self._split_every_row.addWidget(self._lbl_every_suffix)
        self._split_every_row.addStretch()
        sp_lay.addLayout(self._split_every_row)

        # 页码范围输入
        self._split_ranges_input = QLineEdit()
        self._split_ranges_input.setPlaceholderText(_tr("如：1-3, 4-6, 7-10"))
        self._split_ranges_input.setVisible(False)
        self._split_ranges_input.setStyleSheet(LINEEDIT_STYLE)
        sp_lay.addWidget(self._split_ranges_input)

        self._split_params.setVisible(False)
        self.ui.bottomLayout.insertWidget(
            self.ui.bottomLayout.indexOf(self.ui.btnMergePdf),
            self._split_params
        )

    # ────────────────────────────────────────────────
    # 语言切换重译
    # ────────────────────────────────────────────────

    def retranslateUi(self):
        self.ui.btnAddPdf.setText(_tr("添加PDF"))
        self.ui.btnClearAll.setText(_tr("清空"))
        self.ui.btnMerge.setText(_tr("合并"))
        self.ui.btnSplit.setText(_tr("拆分"))

        self._rb_every.setText(_tr("每页单独保存"))
        self._rb_ranges.setText(_tr("按页码范围拆分"))
        self._lbl_every_prefix.setText(_tr("每"))
        self._lbl_every_suffix.setText(_tr("页为一份"))
        self._split_ranges_input.setPlaceholderText(_tr("如：1-3, 4-6, 7-10"))

        self._update_file_ui()
        self._update_mode_ui()

    # ────────────────────────────────────────────────
    # 信号连接
    # ────────────────────────────────────────────────

    def _connect_signals(self):
        self.ui.btnAddPdf.clicked.connect(self._add_files)
        self.ui.btnClearAll.clicked.connect(self._clear_all)
        self.ui.btnMerge.clicked.connect(self._switch_to_merge)
        self.ui.btnSplit.clicked.connect(self._switch_to_split)
        self.ui.btnMergePdf.clicked.connect(self._do_action)

    # ────────────────────────────────────────────────
    # 文件管理
    # ────────────────────────────────────────────────

    def _add_files(self):
        if self._is_busy:
            return
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "选择 PDF 文件（可多选）",
            "",
            "PDF Files (*.pdf)"
        )
        if not files:
            return
        self._on_files_selected(files)

    def _on_files_selected(self, file_paths):
        if not file_paths:
            return
        for fpath in file_paths:
            if fpath and os.path.exists(fpath):
                add_record(fpath, "merge")
        self._remove_placeholder()
        added = 0
        existing = set(self._file_list)
        for fpath in file_paths:
            if fpath.lower().endswith(".pdf") and fpath not in existing:
                self._file_list.append(fpath)
                existing.add(fpath)
                added += 1
                size = os.path.getsize(fpath) if os.path.exists(fpath) else 0
                item = QListWidgetItem()
                item.setData(_FILE_PATH_ROLE, fpath)
                item.setData(_FILE_SIZE_ROLE, size)
                item.setSizeHint(QSize(0, 44))
                self.ui.fileListWidget.addItem(item)
                self.ui.fileListWidget.setItemWidget(
                    item, self._make_file_item_widget(fpath, size, i=self.ui.fileListWidget.count() - 1)
                )
        if added > 0:
            self._update_file_ui()
        else:
            self._status_lbl.setText("未添加新文件（可能已存在或格式不对）")
            self._status_lbl.setStyleSheet("color: #FF9D00; font-size: 13px;")

    def _clear_all(self):
        if self._is_busy:
            return
        self._file_list.clear()
        self.ui.fileListWidget.clear()
        self._status_lbl.setText("")
        self._update_file_ui()
        self._update_placeholder()

    def _remove_file(self, file_path):
        if file_path in self._file_list:
            self._file_list.remove(file_path)
        for i in range(self.ui.fileListWidget.count()):
            item = self.ui.fileListWidget.item(i)
            if item and item.data(_FILE_PATH_ROLE) == file_path:
                self.ui.fileListWidget.takeItem(i)
                break
        self._update_file_ui()
        if not self._file_list:
            self._update_placeholder()

    def _make_file_item_widget(self, file_path, size_bytes, i=0):
        """创建自定义列表行：文件名 + 大小 + ✕ 删除按钮"""
        widget = QWidget()
        widget.setFixedHeight(44)
        lay = QHBoxLayout(widget)
        lay.setContentsMargins(12, 0, 8, 0)
        lay.setSpacing(8)

        basename = os.path.basename(file_path)
        size_kb = size_bytes // 1024 if size_bytes > 0 else 0

        name_label = QLabel(basename)
        name_label.setStyleSheet("color: #EAECEF; font-size: 13px;")

        size_label = QLabel(f"({size_kb} KB)")
        size_label.setStyleSheet("color: #6B7280; font-size: 12px;")

        remove_btn = QPushButton("\u2715")
        remove_btn.setFixedSize(24, 24)
        remove_btn.setCursor(Qt.PointingHandCursor)
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 12px;
                color: #6B7280;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FF4D4F22;
                color: #FF4D4F;
            }
        """)
        fp = file_path
        remove_btn.clicked.connect(lambda checked, p=fp: self._remove_file(p))

        lay.addWidget(name_label)
        lay.addWidget(size_label)
        lay.addStretch()
        lay.addWidget(remove_btn)

        return widget

    def _update_file_ui(self):
        count = len(self._file_list)
        self.ui.lblFileCount.setText(_tr("已添加 {} 个文件").format(count))

    def _update_placeholder(self):
        if len(self._file_list) == 0 and self.ui.fileListWidget.count() == 0:
            self._ph_item = QListWidgetItem("\u5c1a\u672a\u6dfb\u52a0\u6587\u4ef6\uff0c\u70b9\u51fb\u4e0a\u65b9\u6309\u94ae\u9009\u62e9PDF")
            self._ph_item.setFlags(Qt.NoItemFlags)
            self._ph_item.setTextAlignment(Qt.AlignCenter)
            f = self._ph_item.font()
            f.setPointSize(9)
            self._ph_item.setFont(f)
            from PySide6.QtGui import QColor as _QColor
            self._ph_item.setForeground(_QColor(132, 142, 156, 76))
            self.ui.fileListWidget.addItem(self._ph_item)
            QTimer.singleShot(0, self._adjust_ph_height)

    def _adjust_ph_height(self):
        if self._ph_item is not None and self.ui.fileListWidget.count() > 0:
            h = self.ui.fileListWidget.viewport().height()
            if h > 50:
                self._ph_item.setSizeHint(QSize(0, h))

    def _on_rows_moved(self, parent, start, end, destination, row):
        """拖拽排序后同步 self._file_list 顺序"""
        if self._ph_item is not None:
            return
        new_list = []
        for i in range(self.ui.fileListWidget.count()):
            item = self.ui.fileListWidget.item(i)
            if item is None:
                continue
            fpath = item.data(_FILE_PATH_ROLE)
            if fpath is not None:
                new_list.append(fpath)
        self._file_list = new_list

    def _remove_placeholder(self):
        if self._ph_item is not None and self.ui.fileListWidget.count() == 1 \
                and self.ui.fileListWidget.item(0) is self._ph_item:
            self.ui.fileListWidget.takeItem(0)
            self._ph_item = None

    # ────────────────────────────────────────────────
    # 模式切换（合并 / 拆分）
    # ────────────────────────────────────────────────

    def _switch_to_merge(self):
        self._merge_mode = True
        self._update_mode_ui()

    def _switch_to_split(self):
        self._merge_mode = False
        self._update_mode_ui()

    def _update_mode_ui(self):
        if self._merge_mode:
            self.ui.lblHint.setText(_tr("选择至少2个PDF文件，合并为一个PDF文件"))
            self.ui.btnMergePdf.setText(_tr("合并为单个PDF"))
            self._split_params.setVisible(False)
            self.ui.btnMerge.setStyleSheet(BTN_ACTIVE_STYLE)
            self.ui.btnSplit.setStyleSheet(BTN_INACTIVE_STYLE)
        else:
            self.ui.lblHint.setText(_tr("请选择拆分模式"))
            self.ui.btnMergePdf.setText(_tr("开始拆分"))
            self._split_params.setVisible(True)
            self.ui.btnMerge.setStyleSheet(BTN_INACTIVE_STYLE)
            self.ui.btnSplit.setStyleSheet(BTN_ACTIVE_STYLE)

    def _on_split_mode_changed(self, btn_id):
        is_every = (btn_id == 1)
        for i in range(self._split_every_row.count()):
            w = self._split_every_row.itemAt(i)
            if w and w.widget():
                w.widget().setVisible(is_every)
        self._split_ranges_input.setVisible(not is_every)

    # ────────────────────────────────────────────────
    # 主操作入口
    # ────────────────────────────────────────────────

    def _do_action(self):
        if self._merge_mode:
            self._do_merge()
        else:
            self._do_split()

    # ────────────────────────────────────────────────
    # 合并操作
    # ────────────────────────────────────────────────

    def _do_merge(self):
        if self._is_busy:
            return
        if len(self._file_list) < 2:
            self._status_lbl.setText("\u26a0 \u5408\u5e76\u81f3\u5c11\u9700\u8981 2 \u4e2a PDF \u6587\u4ef6")
            self._status_lbl.setStyleSheet("color: #FF9D00; font-size: 13px;")
            return

        base = os.path.splitext(os.path.basename(self._file_list[0]))[0]
        default_name = f"{base}\u5408\u5e76.pdf"

        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存合并后的 PDF",
            default_name,
            "PDF Files (*.pdf)"
        )
        if not save_path:
            return
        if not save_path.lower().endswith(".pdf"):
            save_path += ".pdf"

        self._is_busy = True
        self._status_lbl.setText("\u23f3 \u6b63\u5728\u5408\u5e76...")
        self._status_lbl.setStyleSheet("color: #4D7CFE; font-size: 13px;")
        self.ui.btnMergePdf.setEnabled(False)

        self._merge_worker = MergeWorker(save_path, list(self._file_list))
        self._merge_worker.finished.connect(self._on_merge_done)
        self._merge_worker.error.connect(self._on_merge_error)
        self._merge_worker.start()

    def _on_merge_done(self, result):
        self._is_busy = False
        self.ui.btnMergePdf.setEnabled(True)
        pages = result.get("total_pages", 0)
        out = result.get("output_path", "")
        size_bytes = result.get("output_size", 0)
        size_mb = size_bytes / 1024 / 1024
        self._status_lbl.setText(
            f"\u2705 \u5408\u5e76\u5b8c\u6210\uff01\u5171 {pages} \u9875 | "
            f"\u8f93\u51fa\uff1a{os.path.basename(out)}\uff08{size_mb:.1f} MB\uff09"
        )
        self._status_lbl.setStyleSheet("color: #00C853; font-size: 13px;")
        # 记录到最近使用
        if out:
            add_record(out, "merge", out)

    def _on_merge_error(self, msg):
        self._is_busy = False
        self.ui.btnMergePdf.setEnabled(True)
        self._status_lbl.setText("❌ 合并失败")
        self._status_lbl.setStyleSheet("color: #FF4D4F; font-size: 13px;")
        # 使用统一错误处理弹窗
        ErrorHandler.show_error_dialog(
            title="合并失败",
            message="PDF 合并过程中发生错误",
            details=msg,
            parent_widget=self,
        )

    # ────────────────────────────────────────────────
    # 拆分操作
    # ────────────────────────────────────────────────

    def _do_split(self):
        if self._is_busy:
            return
        if not self._file_list:
            self._status_lbl.setText("\u26a0 \u8bf7\u5148\u6dfb\u52a0 PDF \u6587\u4ef6")
            self._status_lbl.setStyleSheet("color: #FF9D00; font-size: 13px;")
            return

        input_path = self._file_list[0]
        output_dir = QFileDialog.getExistingDirectory(
            self,
            "选择拆分文件的保存目录"
        )
        if not output_dir:
            return

        mode_id = self._split_mode_group.checkedId()

        if mode_id == 2:
            ranges = self._split_ranges_input.text().strip()
            if not ranges:
                self._status_lbl.setText("\u26a0 \u8bf7\u8f93\u5165\u9875\u7801\u8303\u56f4\uff0c\u5982 1-3, 4-6")
                self._status_lbl.setStyleSheet("color: #FF9D00; font-size: 13px;")
                return

        self._is_busy = True
        self._status_lbl.setText("\u23f3 \u6b63\u5728\u62c6\u5206...")
        self._status_lbl.setStyleSheet("color: #4D7CFE; font-size: 13px;")
        self.ui.btnMergePdf.setEnabled(False)

        if mode_id == 1:
            self._split_worker = SplitWorker(input_path, output_dir, mode="page")
        else:
            ranges = self._split_ranges_input.text().strip()
            self._split_worker = SplitWorker(
                input_path, output_dir, mode="range", range_str=ranges
            )

        self._split_worker.finished.connect(self._on_split_done)
        self._split_worker.error.connect(self._on_split_error)
        self._split_worker.start()

    def _on_split_done(self, result):
        self._is_busy = False
        self.ui.btnMergePdf.setEnabled(True)
        count = result.get("count", 0)
        files = result.get("files", [])
        out_dir = os.path.dirname(files[0]) if files else ""
        self._status_lbl.setText(
            f"\u2705 \u62c6\u5206\u5b8c\u6210\uff01\u5171\u751f\u6210 {count} \u4e2a\u6587\u4ef6\n\u4fdd\u5b58\u81f3\uff1a{out_dir}"
        )
        self._status_lbl.setStyleSheet("color: #00C853; font-size: 13px;")
        # 记录到最近使用(使用第一个输出文件)
        if files:
            add_record(files[0], "merge", out_dir)

    def _on_split_error(self, msg):
        self._is_busy = False
        self.ui.btnMergePdf.setEnabled(True)
        self._status_lbl.setText("❌ 拆分失败")
        self._status_lbl.setStyleSheet("color: #FF4D4F; font-size: 13px;")
        # 使用统一错误处理弹窗
        ErrorHandler.show_error_dialog(
            title="拆分失败",
            message="PDF 拆分过程中发生错误",
            details=msg,
            parent_widget=self,
        )

    # ────────────────────────────────────────────────
    # 主题切换
    # ────────────────────────────────────────────────

    def apply_theme(self, colors):
        """ThemeManager 主题切换时更新页面内联样式"""
        # 页面背景
        page_bg = (
            f"QWidget#MergePage {{\n"
            f"    background-color: {colors['bg']};\n"
            f"}}\n"
        )
        # 主要按钮
        btn_primary = (
            f"QPushButton#btnAddPdf, QPushButton#btnMergePdf {{\n"
            f"    background-color: {colors['primary']};\n"
            f"    color: {colors['white']};\n"
            f"    border: none; border-radius: 8px;\n"
            f"    font-size: 14px; font-weight: 500; padding: 8px 20px;\n"
            f"}}\n"
            f"QPushButton#btnAddPdf:hover, QPushButton#btnMergePdf:hover {{\n"
            f"    background-color: {colors['primary_hover']};\n"
            f"}}\n"
            f"QPushButton#btnAddPdf:pressed, QPushButton#btnMergePdf:pressed {{\n"
            f"    background-color: {colors['primary_pressed']};\n"
            f"}}"
        )
        # 清空按钮
        btn_clear = (
            f"QPushButton#btnClearAll {{\n"
            f"    background-color: transparent; color: {colors['text_sub']};\n"
            f"    border: none; border-radius: 8px;\n"
            f"    font-size: 14px; padding: 8px 16px;\n"
            f"}}\n"
            f"QPushButton#btnClearAll:hover {{\n"
            f"    color: {colors['text_main']};\n"
            f"}}"
        )
        # 合并/拆分按钮
        btn_merge_split = (
            f"QPushButton#btnMerge, QPushButton#btnSplit {{\n"
            f"    background-color: {colors['active_bg']};\n"
            f"    color: {colors['text_main']};\n"
            f"    border: 1px solid {colors['border_light']};\n"
            f"    border-radius: 8px; font-size: 14px; padding: 6px 20px;\n"
            f"}}\n"
            f"QPushButton#btnMerge:hover, QPushButton#btnSplit:hover {{\n"
            f"    background-color: {colors['hover_bg']};\n"
            f"    border-color: {colors['border_hover']};\n"
            f"}}"
        )
        # 文件列表
        file_list = (
            f"QListWidget#fileListWidget {{\n"
            f"    background-color: {colors['card_bg']};\n"
            f"    border: 1px solid {colors['border_light']};\n"
            f"    border-radius: 8px; font-size: 14px;\n"
            f"    color: {colors['text_main']};\n"
            f"    outline: none; padding: 4px;\n"
            f"}}\n"
            f"QListWidget#fileListWidget::item {{\n"
            f"    height: 44px; border-radius: 6px;\n"
            f"    padding: 0px 12px; color: {colors['text_main']};\n"
            f"}}\n"
            f"QListWidget#fileListWidget::item:hover {{\n"
            f"    background-color: {colors['hover_bg']};\n"
            f"}}\n"
            f"QListWidget#fileListWidget::item:selected {{\n"
            f"    background-color: {colors['active_bg']};\n"
            f"}}"
        )
        # 状态标签
        lbl_count = (
            f"color: {colors['text_sub']}; font-size: 13px;"
        )
        lbl_hint = (
            f"color: {colors['text_sub']}; font-size: 13px;"
        )

        full_qss = page_bg + btn_primary + btn_clear + btn_merge_split + file_list
        self.setStyleSheet(full_qss)
        self.ui.lblFileCount.setStyleSheet(lbl_count)
        self.ui.lblHint.setStyleSheet(lbl_hint)

        # 更新动态样式
        self._status_lbl.setStyleSheet(f"color: {colors['text_sub']}; font-size: 13px;")

        # 重新应用 radio 和控件样式（在 dynamic UI 中）
        radio_style = (
            f"QRadioButton {{"
            f"    color: {colors['text_main']}; font-size: 14px; spacing: 8px;"
            f"    background: transparent; border: none;"
            f"}}"
            f"QRadioButton::indicator {{"
            f"    width: 16px; height: 16px; border-radius: 8px;"
            f"    border: 2px solid {colors['border_light']}; background: transparent;"
            f"}}"
            f"QRadioButton::indicator:checked {{"
            f"    border: 2px solid {colors['primary']}; background: {colors['primary']};"
            f"}}"
        )
        self._rb_every.setStyleSheet(radio_style)
        self._rb_ranges.setStyleSheet(radio_style)

        spinbox_style = (
            f"QSpinBox {{"
            f"    background-color: {colors['card_bg']};"
            f"    border: 1px solid {colors['border_light']};"
            f"    border-radius: 6px; color: {colors['text_main']};"
            f"    padding: 4px 8px; min-height: 28px;"
            f"}}"
        )
        self._split_every_spin.setStyleSheet(spinbox_style)

        lineedit_style = (
            f"QLineEdit {{"
            f"    background-color: {colors['card_bg']};"
            f"    border: 1px solid {colors['border_light']};"
            f"    border-radius: 6px; color: {colors['text_main']};"
            f"    font-size: 14px; padding: 8px 12px; min-height: 18px;"
            f"}}\n"
            f"QLineEdit:focus {{ border: 1px solid {colors['primary']}; }}"
        )
        self._split_ranges_input.setStyleSheet(lineedit_style)

        # 更新文件列表项的颜色
        self._update_file_item_themes(colors)

    def _update_file_item_themes(self, colors):
        """更新文件列表项中的标签颜色"""
        for i in range(self.ui.fileListWidget.count()):
            item = self.ui.fileListWidget.item(i)
            if item is None:
                continue
            widget = self.ui.fileListWidget.itemWidget(item)
            if widget is None:
                continue
            labels = widget.findChildren(QLabel)
            for lbl in labels:
                text = lbl.text()
                if text.endswith("KB") or text.endswith("MB") or text.endswith("B"):
                    lbl.setStyleSheet(f"color: {colors['text_meta']}; font-size: 12px;")
                else:
                    lbl.setStyleSheet(f"color: {colors['text_main']}; font-size: 13px;")
