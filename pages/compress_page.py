# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'compress_page.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QProgressBar, QPushButton,
    QRadioButton, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)
class Ui_CompressPage(object):
    def setupUi(self, compressPage):
        if not compressPage.objectName():
            compressPage.setObjectName(u"compressPage")
        compressPage.resize(780, 640)
        compressPage.setStyleSheet(u"QWidget#compressPage { background-color: #0B0E11; }")
        self.mainLayout = QVBoxLayout(compressPage)
        self.mainLayout.setSpacing(12)
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setContentsMargins(24, 20, 24, 24)
        self.topRow = QHBoxLayout()
        self.topRow.setSpacing(8)
        self.topRow.setObjectName(u"topRow")
        self.btnSelectFile = QPushButton(compressPage)
        self.btnSelectFile.setObjectName(u"btnSelectFile")
        self.btnSelectFile.setMinimumSize(QSize(160, 40))
        self.btnSelectFile.setMaximumSize(QSize(160, 40))
        self.btnSelectFile.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btnSelectFile.setFocusPolicy(Qt.StrongFocus)
        self.btnSelectFile.setStyleSheet(u"\n"
"QPushButton {\n"
"    background-color: #4D7CFE;\n"
"    color: #FFFFFF;\n"
"    border: none;\n"
"    border-radius: 8px;\n"
"    font-size: 14px;\n"
"    font-weight: 600;\n"
"    padding: 0 16px;\n"
"    min-height: 40px;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: #3D6CF0;\n"
"}\n"
"QPushButton:pressed {\n"
"    background-color: #2D5CD0;\n"
"}\n"
"        ")

        self.topRow.addWidget(self.btnSelectFile)

        self.btnClearAll = QPushButton(compressPage)
        self.btnClearAll.setObjectName(u"btnClearAll")
        self.btnClearAll.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btnClearAll.setFocusPolicy(Qt.StrongFocus)
        self.btnClearAll.setStyleSheet(u"\n"
"QPushButton {\n"
"    background-color: transparent;\n"
"    border: none;\n"
"    color: #848E9C;\n"
"    font-size: 13px;\n"
"    padding: 0 8px;\n"
"    min-height: 40px;\n"
"}\n"
"QPushButton:hover {\n"
"    color: #EAECEF;\n"
"}\n"
"        ")

        self.topRow.addWidget(self.btnClearAll)

        self.topSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.topRow.addItem(self.topSpacer)

        self.lblFileCount = QLabel(compressPage)
        self.lblFileCount.setObjectName(u"lblFileCount")
        self.lblFileCount.setStyleSheet(u"color: #848E9C; font-size: 13px;")

        self.topRow.addWidget(self.lblFileCount)


        self.mainLayout.addLayout(self.topRow)

        self.fileList = QListWidget(compressPage)
        self.fileList.setObjectName(u"fileList")
        self.fileList.setFrameShape(QFrame.NoFrame)
        self.fileList.setMinimumHeight(180)
        self.fileList.setStyleSheet(u"\n"
"QListWidget {\n"
"    background-color: #1A1A22;\n"
"    border: 1px solid #2B3139;\n"
"    border-radius: 8px;\n"
"    padding: 4px;\n"
"    outline: none;\n"
"}\n"
"QListWidget::item {\n"
"    background: transparent;\n"
"    border-radius: 6px;\n"
"    margin: 2px;\n"
"    padding: 8px 12px;\n"
"    min-height: 36px;\n"
"    color: #EAECEF;\n"
"    font-size: 13px;\n"
"}\n"
"QListWidget::item:hover {\n"
"    background: #1E2329;\n"
"}\n"
"QListWidget::item:selected {\n"
"    background-color: transparent;\n"
"}\n"
"      ")

        self.mainLayout.addWidget(self.fileList)

        self.spacer1 = QSpacerItem(0, 4, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.mainLayout.addItem(self.spacer1)

        self.qualityCard = QFrame(compressPage)
        self.qualityCard.setObjectName(u"qualityCard")
        self.qualityCard.setStyleSheet(u"\n"
"QFrame#qualityCard {\n"
"    background-color: #1A1A22;\n"
"    border: 1px solid #2B3139;\n"
"    border-radius: 8px;\n"
"    padding: 16px;\n"
"}\n"
"      ")
        self.qualityCardLayout = QVBoxLayout(self.qualityCard)
        self.qualityCardLayout.setSpacing(10)
        self.qualityCardLayout.setObjectName(u"qualityCardLayout")
        self.qualityCardLayout.setContentsMargins(0, 0, 0, 0)
        self.lblQualityTitle = QLabel(self.qualityCard)
        self.lblQualityTitle.setObjectName(u"lblQualityTitle")
        self.lblQualityTitle.setStyleSheet(u"color: #EAECEF; font-size: 15px; font-weight: 600; background: transparent; border: none; padding: 0; margin: 0;")

        self.qualityCardLayout.addWidget(self.lblQualityTitle)

        self.qualityInner = QFrame(self.qualityCard)
        self.qualityInner.setObjectName(u"qualityInner")
        self.qualityInner.setStyleSheet(u"\n"
"QFrame#qualityInner {\n"
"    background-color: #0B0E11;\n"
"    border: 1px solid #2B3139;\n"
"    border-radius: 6px;\n"
"    padding: 12px;\n"
"}\n"
"         ")
        self.qualityInnerLayout = QVBoxLayout(self.qualityInner)
        self.qualityInnerLayout.setSpacing(8)
        self.qualityInnerLayout.setObjectName(u"qualityInnerLayout")
        self.qualityInnerLayout.setContentsMargins(0, 0, 0, 0)
        self.radioHigh = QRadioButton(self.qualityInner)
        self.radioHigh.setObjectName(u"radioHigh")
        self.radioHigh.setChecked(True)
        self.radioHigh.setStyleSheet(u"color: #EAECEF; font-size: 14px; spacing: 8px; background: transparent; border: none;")

        self.qualityInnerLayout.addWidget(self.radioHigh)

        self.radioMedium = QRadioButton(self.qualityInner)
        self.radioMedium.setObjectName(u"radioMedium")
        self.radioMedium.setStyleSheet(u"color: #EAECEF; font-size: 14px; spacing: 8px; background: transparent; border: none;")

        self.qualityInnerLayout.addWidget(self.radioMedium)

        self.radioLow = QRadioButton(self.qualityInner)
        self.radioLow.setObjectName(u"radioLow")
        self.radioLow.setStyleSheet(u"color: #EAECEF; font-size: 14px; spacing: 8px; background: transparent; border: none;")

        self.qualityInnerLayout.addWidget(self.radioLow)


        self.qualityCardLayout.addWidget(self.qualityInner)


        self.mainLayout.addWidget(self.qualityCard)

        self.spacer2 = QSpacerItem(0, 4, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.mainLayout.addItem(self.spacer2)

        self.batchRow = QHBoxLayout()
        self.batchRow.setSpacing(16)
        self.batchRow.setObjectName(u"batchRow")
        self.btnStartBatch = QPushButton(compressPage)
        self.btnStartBatch.setObjectName(u"btnStartBatch")
        self.btnStartBatch.setMinimumSize(QSize(160, 40))
        self.btnStartBatch.setMaximumSize(QSize(160, 40))
        self.btnStartBatch.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btnStartBatch.setFocusPolicy(Qt.StrongFocus)
        self.btnStartBatch.setStyleSheet(u"\n"
"QPushButton {\n"
"    background-color: #4D7CFE;\n"
"    color: #FFFFFF;\n"
"    border: none;\n"
"    border-radius: 8px;\n"
"    font-size: 14px;\n"
"    font-weight: 600;\n"
"    padding: 0 24px;\n"
"    min-height: 40px;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: #3D6CF0;\n"
"}\n"
"QPushButton:pressed {\n"
"    background-color: #2D5CD0;\n"
"}\n"
"QPushButton:disabled {\n"
"    background-color: #2B3139;\n"
"    color: #848E9C;\n"
"}\n"
"        ")

        self.batchRow.addWidget(self.btnStartBatch)

        self.lblProgressText = QLabel(compressPage)
        self.lblProgressText.setObjectName(u"lblProgressText")
        self.lblProgressText.setStyleSheet(u"color: #848E9C; font-size: 13px;")

        self.batchRow.addWidget(self.lblProgressText)

        self.batchSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.batchRow.addItem(self.batchSpacer)


        self.mainLayout.addLayout(self.batchRow)

        self.progressBar = QProgressBar(compressPage)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setValue(0)
        self.progressBar.setTextVisible(False)
        self.progressBar.setStyleSheet(u"\n"
"QProgressBar {\n"
"    background-color: #1E1E28;\n"
"    border: none;\n"
"    border-radius: 3px;\n"
"    min-height: 6px;\n"
"    max-height: 6px;\n"
"}\n"
"QProgressBar::chunk {\n"
"    background-color: #4D7CFE;\n"
"    border-radius: 3px;\n"
"}\n"
"      ")

        self.mainLayout.addWidget(self.progressBar)

        self.lblStatus = QLabel(compressPage)
        self.lblStatus.setObjectName(u"lblStatus")
        self.lblStatus.setStyleSheet(u"color: #848E9C; font-size: 13px; min-height: 20px;")

        self.mainLayout.addWidget(self.lblStatus)

        self.resultCard = QFrame(compressPage)
        self.resultCard.setObjectName(u"resultCard")
        self.resultCard.setVisible(False)
        self.resultCard.setStyleSheet(u"\n"
"QFrame#resultCard {\n"
"    background-color: #1A1A22;\n"
"    border: 1px solid #4D7CFE;\n"
"    border-radius: 8px;\n"
"    padding: 16px;\n"
"}\n"
"      ")
        self.resultLayout = QVBoxLayout(self.resultCard)
        self.resultLayout.setSpacing(6)
        self.resultLayout.setObjectName(u"resultLayout")
        self.resultLayout.setContentsMargins(0, 0, 0, 0)
        self.lblResultTitle = QLabel(self.resultCard)
        self.lblResultTitle.setObjectName(u"lblResultTitle")
        self.lblResultTitle.setStyleSheet(u"color: #4D7CFE; font-size: 14px; font-weight: 600; background: transparent; border: none; padding: 0;")

        self.resultLayout.addWidget(self.lblResultTitle)

        self.lblTotalInfo = QLabel(self.resultCard)
        self.lblTotalInfo.setObjectName(u"lblTotalInfo")
        self.lblTotalInfo.setStyleSheet(u"color: #EAECEF; font-size: 13px; background: transparent; border: none; padding: 0;")

        self.resultLayout.addWidget(self.lblTotalInfo)

        self.lblOriginalSize = QLabel(self.resultCard)
        self.lblOriginalSize.setObjectName(u"lblOriginalSize")
        self.lblOriginalSize.setStyleSheet(u"color: #EAECEF; font-size: 13px; background: transparent; border: none; padding: 0;")

        self.resultLayout.addWidget(self.lblOriginalSize)

        self.lblCompressedSize = QLabel(self.resultCard)
        self.lblCompressedSize.setObjectName(u"lblCompressedSize")
        self.lblCompressedSize.setStyleSheet(u"color: #EAECEF; font-size: 13px; background: transparent; border: none; padding: 0;")

        self.resultLayout.addWidget(self.lblCompressedSize)

        self.lblAvgRatio = QLabel(self.resultCard)
        self.lblAvgRatio.setObjectName(u"lblAvgRatio")
        self.lblAvgRatio.setStyleSheet(u"color: #4D7CFE; font-size: 14px; font-weight: 600; background: transparent; border: none; padding: 0;")

        self.resultLayout.addWidget(self.lblAvgRatio)


        self.mainLayout.addWidget(self.resultCard)

        self.spacerBottom = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.mainLayout.addItem(self.spacerBottom)


        self.retranslateUi(compressPage)

        QMetaObject.connectSlotsByName(compressPage)
    # setupUi

    def retranslateUi(self, compressPage):
        self.btnSelectFile.setText(QCoreApplication.translate("CompressPage", u"\u9009\u62e9PDF\u6587\u4ef6", None))
        self.btnClearAll.setText(QCoreApplication.translate("CompressPage", u"\u6e05\u7a7a\u5168\u90e8", None))
        self.lblFileCount.setText(QCoreApplication.translate("CompressPage", u"\u5df2\u9009 0 \u4e2a\u6587\u4ef6", None))
        self.lblQualityTitle.setText(QCoreApplication.translate("CompressPage", u"\u538b\u7f29\u8d28\u91cf", None))
        self.radioHigh.setText(QCoreApplication.translate("CompressPage", u"\u9ad8\u8d28\u91cf\uff08\u9002\u5408\u6253\u5370\uff09", None))
        self.radioMedium.setText(QCoreApplication.translate("CompressPage", u"\u4e2d\u7b49\u8d28\u91cf\uff08\u9002\u5408\u9605\u8bfb\uff09", None))
        self.radioLow.setText(QCoreApplication.translate("CompressPage", u"\u4f4e\u8d28\u91cf\uff08\u9002\u5408\u5c4f\u5e55\u663e\u793a\uff09", None))
        self.btnStartBatch.setText(QCoreApplication.translate("CompressPage", u"\u5f00\u59cb\u6279\u91cf\u538b\u7f29", None))
        self.lblProgressText.setText("")
        self.lblStatus.setText("")
        self.lblResultTitle.setText(QCoreApplication.translate("CompressPage", u"\u2705 \u6279\u91cf\u538b\u7f29\u5b8c\u6210", None))
        self.lblTotalInfo.setText("")
        self.lblOriginalSize.setText("")
        self.lblCompressedSize.setText("")
        self.lblAvgRatio.setText("")
        pass
    # retranslateUi


# ================================================================
# 以下为业务逻辑代码（不覆盖UI类）
# CompressPage — PySide6 批量压缩功能页面
# 支持多文件选择、逐个压缩、进度显示、汇总结果
# 后端：调用 src/common/pdf_api.compress_pdf
# 文件选择：QFileDialog
# 使用方式：from pages.compress_page import CompressPage
# ================================================================

import os

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import QListWidgetItem, QFileDialog

from src.common.pdf_api import compress_pdf
from src.common.recent_files_manager import add_record
from src.common.error_handler import ErrorHandler, ErrorType
from translations.translation_manager import _ as _tr


class CompressWorker(QThread):
    """单个文件的压缩工作线程"""
    finished = Signal(int, dict)   # index, result dict
    error = Signal(int, str)       # index, error message
    pageProgress = Signal(int, int, int)  # index, current, total

    def __init__(self, index: int, input_path: str, quality: str, output_path: str):
        super().__init__()
        self._index = index
        self._input_path = input_path
        self._quality = quality
        self._output_path = output_path

    def run(self):
        try:
            result = compress_pdf(
                self._input_path,
                self._quality,
                self._output_path,
                progress_callback=self._on_progress,
            )
            self.finished.emit(self._index, result)
        except Exception as e:
            self.error.emit(self._index, str(e))

    def _on_progress(self, current: int, total: int):
        self.pageProgress.emit(self._index, current, total)


# ── 文件列表项角色 ──
_FILE_PATH_ROLE = Qt.UserRole + 1
_FILE_SIZE_ROLE = Qt.UserRole + 2
_FILE_STATUS_ROLE = Qt.UserRole + 3


class CompressPage(QWidget):
    """PDF批量压缩功能页面"""

    def __init__(self):
        super().__init__()
        self._file_paths = []
        self._worker = None
        self._processed_count = 0
        self._failed_count = 0
        self._total_original = 0
        self._total_compressed = 0
        self._is_busy = False

        # 加载编译的UI
        self.ui = Ui_CompressPage()
        self.ui.setupUi(self)

        # 连接信号
        self._connect_signals()

    def retranslateUi(self):
        self.ui.btnSelectFile.setText(_tr("选择PDF"))
        self.ui.btnClearAll.setText(_tr("清空全部"))
        self.ui.lblFileCount.setText(_tr("已选 0 个文件"))
        self.ui.lblQualityTitle.setText(_tr("压缩质量"))
        self.ui.radioHigh.setText(_tr("高质量（适合打印）"))
        self.ui.radioMedium.setText(_tr("中等质量（适合阅读）"))
        self.ui.radioLow.setText(_tr("低质量（适合屏幕显示）"))
        self.ui.btnStartBatch.setText(_tr("开始批量压缩"))
        self.ui.lblResultTitle.setText(_tr("✅ 批量压缩完成"))
        self._update_file_count()

    # ────────────────────────────────────────────────
    # 信号连接
    # ────────────────────────────────────────────────
    def _connect_signals(self):
        self.ui.btnSelectFile.clicked.connect(self._pick_files)
        self.ui.btnClearAll.clicked.connect(self._clear_all)
        self.ui.btnStartBatch.clicked.connect(self._start_batch)

    # ────────────────────────────────────────────────
    # 选择文件（多选）
    # ────────────────────────────────────────────────
    def _pick_files(self):
        if self._is_busy:
            return
        files, _ = QFileDialog.getOpenFileNames(
            self,
            _tr("选择要压缩的PDF文件（支持多选）"),
            "",
            "PDF Files (*.pdf)"
        )
        if not files:
            return
        existing = set(self._file_paths)
        for path in files:
            if path.lower() in [p.lower() for p in existing] or \
               not path.lower().endswith(".pdf"):
                continue
            self._add_file(path)
        self._update_file_count()

    def _add_file(self, path: str):
        self._file_paths.append(path)
        add_record(path, "compress")
        try:
            size = os.path.getsize(path)
            size_str = self._format_size(size)
            item_text = f"⏳ {os.path.basename(path)}  |  {size_str}"
        except Exception:
            size = 0
            item_text = f"❓ {os.path.basename(path)}  |  ???"

        item = QListWidgetItem(item_text)
        item.setData(_FILE_PATH_ROLE, path)
        item.setData(_FILE_SIZE_ROLE, size)
        item.setData(_FILE_STATUS_ROLE, "waiting")
        self.ui.fileList.addItem(item)

    def _clear_all(self):
        if self._is_busy:
            return
        self._file_paths.clear()
        self.ui.fileList.clear()
        self.ui.resultCard.setVisible(False)
        self.ui.lblStatus.setText("")
        self.ui.lblProgressText.setText("")
        self.ui.progressBar.setValue(0)
        self._update_file_count()

    def _update_file_count(self):
        count = len(self._file_paths)
        self.ui.lblFileCount.setText(_tr("已选择 {} 个PDF文件").format(count))
        self.ui.btnStartBatch.setEnabled(count > 0)

    # ────────────────────────────────────────────────
    # 批量压缩
    # ────────────────────────────────────────────────
    def _start_batch(self):
        if self._is_busy or not self._file_paths:
            return
    
        self._is_busy = True
        self._processed_count = 0
        self._failed_count = 0
        self._total_original = 0
        self._total_compressed = 0
    
        if self.ui.radioLow.isChecked():
            self._quality = "low"
        elif self.ui.radioMedium.isChecked():
            self._quality = "medium"
        else:
            self._quality = "high"
    
        self.ui.resultCard.setVisible(False)
        self.ui.lblStatus.setText("")
        self.ui.lblProgressText.setText("准备开始...")
        self.ui.btnStartBatch.setEnabled(False)
        self.ui.btnSelectFile.setEnabled(False)
        self.ui.btnClearAll.setEnabled(False)
    
        total = len(self._file_paths)
        self.ui.progressBar.setMaximum(total)
        self.ui.progressBar.setValue(0)
    
        # ── 收集每个文件的输出路径（支持自主命名） ─────
        self._output_paths = []
        for i, file_path in enumerate(self._file_paths):
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            default_name = f"{base_name}_\u538b\u7f29_{self._quality}.pdf"
    
            save_path, _ = QFileDialog.getSaveFileName(
                self,
                f"\u4fdd\u5b58\u538b\u7f29\u7ed3\u679c ({i + 1}/{total})",
                os.path.join(os.path.expanduser("~/Desktop"), default_name),
                "PDF \u6587\u4ef6 (*.pdf)"
            )
            if not save_path:
                # \u7528\u6237\u53d6\u6d88\uff0c\u4e2d\u6b62\u6574\u4e2a\u64cd\u4f5c
                self._is_busy = False
                self.ui.btnStartBatch.setEnabled(True)
                self.ui.btnSelectFile.setEnabled(True)
                self.ui.btnClearAll.setEnabled(True)
                self.ui.lblProgressText.setText("")
                return
    
            # \u786e\u4fdd\u540e\u7f00\u4e3a .pdf
            if not save_path.lower().endswith(".pdf"):
                save_path += ".pdf"
            self._output_paths.append(save_path)
    
        for i in range(self.ui.fileList.count()):
            item = self.ui.fileList.item(i)
            if item.data(_FILE_STATUS_ROLE) != "waiting":
                item.setData(_FILE_STATUS_ROLE, "waiting")
                path = item.data(_FILE_PATH_ROLE)
                size_str = self._format_size(item.data(_FILE_SIZE_ROLE))
                item.setText(f"\u23f3 {os.path.basename(path)}  |  {size_str}")
    
        self._current_index = 0
        self._process_next()

    def _process_next(self):
        if self._current_index >= len(self._file_paths):
            self._on_batch_done()
            return
    
        file_path = self._file_paths[self._current_index]
        item = self.ui.fileList.item(self._current_index)
        output_path = self._output_paths[self._current_index]

        item.setText(f"⚙️ {os.path.basename(file_path)}  |  压缩中...")
        item.setData(_FILE_STATUS_ROLE, "processing")

        total = len(self._file_paths)
        done = self._processed_count + self._failed_count
        self.ui.lblProgressText.setText(f"正在处理 ({done + 1}/{total})...")

        self._worker = CompressWorker(
            self._current_index, file_path, self._quality, output_path
        )
        self._worker.finished.connect(self._on_file_done)
        self._worker.error.connect(self._on_file_error)
        self._worker.pageProgress.connect(self._on_file_progress)
        self._worker.start()

    def _on_file_progress(self, index: int, current: int, total: int):
        if total > 0:
            pct = round(current / total * 100)
            self.ui.lblStatus.setText(f"压缩中… 已完成 {current}/{total} 个项目 ({pct}%)")

    def _on_file_done(self, index: int, result: dict):
        file_path = self._file_paths[index]
        orig = result.get("original_mb", 0)
        comp = result.get("compressed_mb", 0)
        ratio = result.get("ratio", "0%")
        output_path = result.get("output_path", "")

        self._processed_count += 1
        self._total_original += orig
        self._total_compressed += comp

        item = self.ui.fileList.item(index)
        size_str = self._format_size(item.data(_FILE_SIZE_ROLE))
        item.setText(f"✅ {os.path.basename(file_path)}  |  {size_str}  |  已压缩 {comp} MB ({ratio})")
        item.setData(_FILE_STATUS_ROLE, "done")

        done = self._processed_count + self._failed_count
        self.ui.progressBar.setValue(done)

        # 记录到最近使用
        if output_path and os.path.exists(output_path):
            add_record(file_path, "compress", output_path)

        self._current_index += 1
        self._process_next()

    def _on_file_error(self, index: int, msg: str):
        file_path = self._file_paths[index]
        self._failed_count += 1

        item = self.ui.fileList.item(index)
        size_str = self._format_size(item.data(_FILE_SIZE_ROLE))
        short_msg = msg[:60] + "..." if len(msg) > 60 else msg
        item.setText(f"❌ {os.path.basename(file_path)}  |  {size_str}  |  失败: {short_msg}")
        item.setData(_FILE_STATUS_ROLE, "failed")

        done = self._processed_count + self._failed_count
        self.ui.progressBar.setValue(done)

        # 单文件失败时使用统一错误处理弹窗
        ErrorHandler.show_error_dialog(
            title="压缩失败",
            message=f"文件「{os.path.basename(file_path)}」压缩失败",
            details=msg,
            parent_widget=self,
        )

        self._current_index += 1
        self._process_next()

    def _on_batch_done(self):
        self._is_busy = False
        self.ui.btnStartBatch.setEnabled(True)
        self.ui.btnSelectFile.setEnabled(True)
        self.ui.btnClearAll.setEnabled(True)

        total = len(self._file_paths)
        done = self._processed_count
        failed = self._failed_count

        self.ui.resultCard.setVisible(True)

        if failed > 0:
            if done > 0:
                self.ui.lblResultTitle.setText("✅ 批量压缩完成（部分失败）")
                self.ui.lblResultTitle.setStyleSheet(
                    "color: #FF9500; font-size: 14px; font-weight: 600;")
            else:
                self.ui.lblResultTitle.setText("⚠️ 批量压缩失败")
                self.ui.lblResultTitle.setStyleSheet(
                    "color: #FF3B30; font-size: 14px; font-weight: 600;")
        else:
            self.ui.lblResultTitle.setText("✅ 批量压缩完成")
            self.ui.lblResultTitle.setStyleSheet(
                "color: #4D7CFE; font-size: 14px; font-weight: 600;")

        self.ui.lblTotalInfo.setText(f"完成: {done} | 失败: {failed} | 总计: {total} 个文件")

        if done > 0:
            avg_ratio = round((1 - self._total_compressed / self._total_original) * 100, 1) if self._total_original > 0 else 0
            self.ui.lblOriginalSize.setText(f"原始总大小：{self._total_original:.2f} MB")
            self.ui.lblCompressedSize.setText(f"压缩后总大小：{self._total_compressed:.2f} MB")
            self.ui.lblAvgRatio.setText(f"平均压缩率：减少 {avg_ratio}%")
        else:
            self.ui.lblOriginalSize.setText("原始总大小：0 MB")
            self.ui.lblCompressedSize.setText("压缩后总大小：0 MB")
            self.ui.lblAvgRatio.setText("")

        self.ui.lblProgressText.setText(f"完成！({total}/{total})")
        self.ui.lblStatus.setText("")

    # ────────────────────────────────────────────────
    # 工具方法
    # ────────────────────────────────────────────────
    @staticmethod
    def _format_size(bytes_size: int) -> str:
        if bytes_size < 1024:
            return f"{bytes_size} B"
        elif bytes_size < 1024 * 1024:
            return f"{bytes_size / 1024:.1f} KB"
        else:
            return f"{bytes_size / 1024 / 1024:.2f} MB"

    # ────────────────────────────────────────────────
    # 主题切换
    # ────────────────────────────────────────────────

    def apply_theme(self, colors):
        """ThemeManager 主题切换时更新页面内联样式"""
        # 页面背景
        page_qss = f"QWidget#compressPage {{ background-color: {colors['bg']}; }}"
        self.setStyleSheet(page_qss)

        # 主要按钮（选择文件、开始压缩）
        btn_primary = (
            f"QPushButton {{\n"
            f"    background-color: {colors['primary']};\n"
            f"    color: {colors['white']};\n"
            f"    border: none; border-radius: 8px;\n"
            f"    font-size: 14px; font-weight: 600; padding: 0 16px;\n"
            f"    min-height: 40px;\n"
            f"}}\n"
            f"QPushButton:hover {{\n"
            f"    background-color: {colors['primary_hover']};\n"
            f"}}\n"
            f"QPushButton:pressed {{\n"
            f"    background-color: {colors['primary_pressed']};\n"
            f"}}\n"
            f"QPushButton:disabled {{\n"
            f"    background-color: {colors['disabled_bg_qss']};\n"
            f"    color: {colors['text_sub']};\n"
            f"}}"
        )
        self.ui.btnSelectFile.setStyleSheet(btn_primary)
        self.ui.btnStartBatch.setStyleSheet(btn_primary)

        # 清空按钮
        btn_ghost = (
            f"QPushButton {{\n"
            f"    background-color: transparent; border: none;\n"
            f"    color: {colors['text_sub']}; font-size: 13px; padding: 0 8px; min-height: 40px;\n"
            f"}}\n"
            f"QPushButton:hover {{ color: {colors['text_main']}; }}"
        )
        self.ui.btnClearAll.setStyleSheet(btn_ghost)

        # 文件列表
        file_list = (
            f"QListWidget {{\n"
            f"    background-color: {colors['card_bg']};\n"
            f"    border: 1px solid {colors['border_light']};\n"
            f"    border-radius: 8px; padding: 4px; outline: none;\n"
            f"}}\n"
            f"QListWidget::item {{\n"
            f"    background: transparent; border-radius: 6px; margin: 2px;\n"
            f"    padding: 8px 12px; min-height: 36px; color: {colors['text_main']};\n"
            f"    font-size: 13px;\n"
            f"}}\n"
            f"QListWidget::item:hover {{ background: {colors['hover_bg']}; }}\n"
            f"QListWidget::item:selected {{ background-color: transparent; }}"
        )
        self.ui.fileList.setStyleSheet(file_list)

        # 质量卡片
        self.ui.qualityCard.setStyleSheet(
            f"QFrame#qualityCard {{\n"
            f"    background-color: {colors['card_bg']};\n"
            f"    border: 1px solid {colors['border_light']};\n"
            f"    border-radius: 8px; padding: 16px;\n"
            f"}}"
        )
        self.ui.qualityInner.setStyleSheet(
            f"QFrame#qualityInner {{\n"
            f"    background-color: {colors['input_bg']};\n"
            f"    border: 1px solid {colors['border_light']};\n"
            f"    border-radius: 6px; padding: 12px;\n"
            f"}}"
        )

        # 单选按钮
        radio_style = (
            f"color: {colors['text_main']}; font-size: 14px; spacing: 8px; background: transparent; border: none;"
        )
        self.ui.radioHigh.setStyleSheet(radio_style)
        self.ui.radioMedium.setStyleSheet(radio_style)
        self.ui.radioLow.setStyleSheet(radio_style)

        # 标签
        lbl_title = f"color: {colors['text_main']}; font-size: 15px; font-weight: 600; background: transparent; border: none; padding: 0; margin: 0;"
        self.ui.lblQualityTitle.setStyleSheet(lbl_title)
        self.ui.lblFileCount.setStyleSheet(f"color: {colors['text_sub']}; font-size: 13px;")
        self.ui.lblProgressText.setStyleSheet(f"color: {colors['text_sub']}; font-size: 13px;")
        self.ui.lblStatus.setStyleSheet(f"color: {colors['text_sub']}; font-size: 13px; min-height: 20px;")

        # 进度条
        self.ui.progressBar.setStyleSheet(
            f"QProgressBar {{\n"
            f"    background-color: {colors['progress_bg']};\n"
            f"    border: none; border-radius: 3px;\n"
            f"    min-height: 6px; max-height: 6px;\n"
            f"}}\n"
            f"QProgressBar::chunk {{\n"
            f"    background-color: {colors['primary']}; border-radius: 3px;\n"
            f"}}"
        )

        # 结果卡片
        result_visible = self.ui.resultCard.isVisible()
        self.ui.resultCard.setStyleSheet(
            f"QFrame#resultCard {{\n"
            f"    background-color: {colors['card_bg']};\n"
            f"    border: 1px solid {colors['primary']};\n"
            f"    border-radius: 8px; padding: 16px;\n"
            f"}}"
        )
        self.ui.lblResultTitle.setStyleSheet(
            f"color: {colors['primary']}; font-size: 14px; font-weight: 600;"
            f" background: transparent; border: none; padding: 0;"
        )
        for name in ['lblTotalInfo', 'lblOriginalSize', 'lblCompressedSize']:
            lbl = getattr(self.ui, name, None)
            if lbl:
                lbl.setStyleSheet(
                    f"color: {colors['text_main']}; font-size: 13px;"
                    f" background: transparent; border: none; padding: 0;"
                )
        self.ui.lblAvgRatio.setStyleSheet(
            f"color: {colors['primary']}; font-size: 14px; font-weight: 600;"
            f" background: transparent; border: none; padding: 0;"
        )
        # 恢复结果卡片可见性
        self.ui.resultCard.setVisible(result_visible)
