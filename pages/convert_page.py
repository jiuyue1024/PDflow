# -*- coding: utf-8 -*-
"""
印流PDflow - 格式转换页面（重新设计版）
5区域卡片布局 + 6个横向转换类型按钮 + 动态参数区
"""

import os

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QFrame, QLabel, QPushButton, QListWidget, QListWidgetItem,
    QProgressBar, QComboBox, QSlider, QButtonGroup, QRadioButton,
    QFileDialog, QSizePolicy, QSpacerItem
)
from PySide6.QtCore import QCoreApplication, QLocale

# ================================================================
# 公共样式
# ================================================================
CARD_STYLE = """
QFrame {
    background-color: #1A1A22;
    border: 1px solid #2B3139;
    border-radius: 8px;
    padding: 16px;
}
"""
CARD_LABEL_STYLE = "color: #EAECEF; font-size: 14px; font-weight: 600; background: transparent; border: none; padding: 0; margin: 0;"
BTN_PRIMARY_STYLE = """
QPushButton {
    background-color: #4D7CFE;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 600;
    padding: 0 20px;
    min-height: 40px;
}
QPushButton:hover { background-color: #3D6CF0; }
QPushButton:pressed { background-color: #2D5CD0; }
QPushButton:disabled { background-color: #2B3139; color: #848E9C; }
"""
BTN_GHOST_STYLE = """
QPushButton {
    background-color: transparent;
    border: none;
    color: #848E9C;
    font-size: 13px;
    padding: 0 8px;
    min-height: 40px;
}
QPushButton:hover { color: #EAECEF; }
"""
BTN_TYPE_STYLE = """
QPushButton {
    background-color: #0B0E11;
    border: 1px solid #2B3139;
    border-radius: 6px;
    color: #848E9C;
    font-size: 13px;
    padding: 8px 16px;
    min-height: 36px;
}
QPushButton:hover { border-color: #4D7CFE; color: #EAECEF; }
QPushButton QWidget { background: transparent; }
"""
BTN_TYPE_SELECTED_STYLE = """
QPushButton {
    background-color: #4D7CFE;
    border: 1px solid #4D7CFE;
    border-radius: 6px;
    color: #FFFFFF;
    font-size: 13px;
    font-weight: 600;
    padding: 8px 16px;
    min-height: 36px;
}
"""
BTN_OUTLINE_STYLE = """
QPushButton {
    background-color: transparent;
    border: 1px solid #2B3139;
    border-radius: 6px;
    color: #EAECEF;
    font-size: 13px;
    padding: 8px 16px;
    min-height: 36px;
}
QPushButton:hover { border-color: #4D7CFE; color: #4D7CFE; }
"""
FILE_LIST_STYLE = """
QListWidget {
    background-color: #0B0E11;
    border: 1px solid #2B3139;
    border-radius: 6px;
    padding: 4px;
    outline: none;
}
QListWidget::item {
    background: transparent;
    border-radius: 4px;
    margin: 1px;
    padding: 6px 10px;
    min-height: 30px;
    color: #EAECEF;
    font-size: 12px;
}
QListWidget::item:hover { background: #1E2329; }
"""
COMBO_STYLE = """
QComboBox {
    background-color: #0B0E11;
    border: 1px solid #2B3139;
    border-radius: 6px;
    padding: 8px 12px;
    color: #EAECEF;
    font-size: 13px;
    min-height: 32px;
}
QComboBox:hover { border-color: #4D7CFE; }
QComboBox::drop-down { border: none; width: 20px; }
QComboBox QAbstractItemView {
    background-color: #1A1A22;
    border: 1px solid #2B3139;
    border-radius: 6px;
    padding: 4px;
    color: #EAECEF;
    selection-background-color: #4D7CFE;
}
"""
PROGRESS_STYLE = """
QProgressBar {
    background-color: #1E1E28;
    border: none;
    border-radius: 3px;
    min-height: 6px;
    max-height: 6px;
}
QProgressBar::chunk { background-color: #4D7CFE; border-radius: 3px; }
"""

# ================================================================
# 转换函数导入
# ================================================================
# 优先从 pdf_api.py 导入所有转换函数（完整版）
# pdf_api.py 包含: pdf_to_word, pdf_to_excel, pdf_to_images, images_to_pdf, pdf_to_ppt, batch_convert
from src.common.pdf_api import (
    pdf_to_word, pdf_to_excel, pdf_to_images, images_to_pdf, pdf_to_ppt, batch_convert
)
from src.common.recent_files_manager import add_record
from src.common.error_handler import ErrorHandler, ErrorType

# ================================================================
# 转换类型配置
# ================================================================
CONV_TYPES = [
    {"key": "pdf_word",  "label": "PDF → Word",  "src": "pdf",  "dst": "docx"},
    {"key": "pdf_excel", "label": "PDF → Excel", "src": "pdf",  "dst": "xlsx"},
    {"key": "pdf_ppt",   "label": "PDF → PPT",   "src": "pdf",  "dst": "pptx"},
    {"key": "pdf_img",   "label": "PDF → 图片",   "src": "pdf",  "dst": "img"},
    {"key": "img_pdf",   "label": "图片 → PDF",   "src": "img",  "dst": "pdf"},
    {"key": "batch",     "label": "批量转换",     "src": "any",  "dst": "any"},
]

# ================================================================
# 后台转换线程
# ================================================================
class ConvertWorker(QThread):
    finished = Signal(int, object)
    error = Signal(int, str)

    def __init__(self, idx, inp, outp, func, extra=None):
        super().__init__()
        self.idx = idx
        self.inp = inp
        self.outp = outp
        self.func = func
        self.extra = extra  # 额外参数（如DPI、格式等）

    def run(self):
        try:
            if self.func == images_to_pdf:
                # images_to_pdf 支持 orientation 和 quality 参数
                orientation = self.extra.get("orientation") if self.extra else "portrait"
                quality = self.extra.get("quality") if self.extra else "high"
                r = self.func([self.inp], self.outp, orientation=orientation, quality=quality)
            elif self.func == pdf_to_images:
                # pdf_to_images 支持 fmt 和 dpi 参数
                fmt = self.extra.get("fmt") if self.extra else "png"
                dpi = self.extra.get("dpi") if self.extra else 150
                r = self.func(self.inp, self.outp, dpi=dpi, fmt=fmt)
            elif self.func == batch_convert:
                batch_fmt = self.extra.get("batch_fmt") if self.extra else "pdf"
                r = self.func(self.inp, self.outp, batch_fmt=batch_fmt)
            else:
                r = self.func(self.inp, self.outp)
            self.finished.emit(self.idx, r)
        except Exception as e:
            self.error.emit(self.idx, str(e))


# ================================================================
# 主页面：ConvertPage
# ================================================================
class ConvertPage(QWidget):
    def __init__(self):
        super().__init__()
        self._paths = []
        self._worker = None
        self._busy = False
        self._selected_type = "pdf_word"  # 默认选中的转换类型

        # 动态参数默认值
        self._params = {
            "fmt": "png",       # PDF→图片：输出格式
            "dpi": 150,         # PDF→图片：DPI
            "orientation": "portrait",  # 图片→PDF：方向
            "quality": "high",  # 图片→PDF：质量
            "page_size": "A4",  # 图片→PDF：纸张大小
        }

        self._init_ui()
        self._connect()

    # ----------------------------------------------------------------
    # UI 初始化
    # ----------------------------------------------------------------
    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(24, 20, 24, 24)

        # ===== 区域1：文件选择 =====
        self._file_card, file_layout = self._make_card()
        main_layout.addWidget(self._file_card)

        # 文件选择行
        top_row = QHBoxLayout()
        top_row.setSpacing(8)

        self._btn_select = QPushButton("选择文件")
        self._btn_select.setMinimumSize(140, 38)
        self._btn_select.setStyleSheet(BTN_PRIMARY_STYLE)
        top_row.addWidget(self._btn_select)

        self._btn_clear = QPushButton("清空")
        self._btn_clear.setStyleSheet(BTN_GHOST_STYLE)
        top_row.addWidget(self._btn_clear)

        top_row.addStretch()

        self._lbl_count = QLabel("已选 0 个文件")
        self._lbl_count.setStyleSheet("color: #848E9C; font-size: 13px; background: transparent; border: none;")
        top_row.addWidget(self._lbl_count)

        file_layout.addLayout(top_row)

        # 文件列表
        self._file_list = QListWidget()
        self._file_list.setStyleSheet(FILE_LIST_STYLE)
        self._file_list.setMinimumHeight(120)
        file_layout.addWidget(self._file_list)

        # ===== 区域2：转换类型 =====
        self._type_card, type_layout = self._make_card()
        main_layout.addWidget(self._type_card)

        self._lbl_type = QLabel("转换格式")
        self._lbl_type.setStyleSheet(CARD_LABEL_STYLE)
        type_layout.addWidget(self._lbl_type)

        # 横向按钮组
        self._type_group = QButtonGroup()
        self._type_btns = {}
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        for ct in CONV_TYPES:
            key = ct["key"]
            btn = QPushButton(ct["label"])
            btn.setCheckable(True)
            btn.setStyleSheet(BTN_TYPE_STYLE if key != self._selected_type else BTN_TYPE_SELECTED_STYLE)
            self._type_group.addButton(btn)
            self._type_group.setId(btn, list(CONV_TYPES).index(ct))
            self._type_btns[key] = btn
            btn_row.addWidget(btn)

        btn_row.addStretch()
        type_layout.addLayout(btn_row)

        # ===== 区域3：参数设置（动态显示） =====
        self._param_card, param_layout = self._make_card()
        main_layout.addWidget(self._param_card)

        self._lbl_param = QLabel("参数设置")
        self._lbl_param.setStyleSheet(CARD_LABEL_STYLE)
        param_layout.addWidget(self._lbl_param)

        # 参数内容容器（动态切换）
        self._param_stack = QVBoxLayout()
        self._param_stack.setSpacing(8)
        param_layout.addLayout(self._param_stack)

        # 为每种类型创建参数面板
        self._param_panels = {}
        self._build_param_panel_pdf_img()   # PDF→图片 参数
        self._build_param_panel_img_pdf()   # 图片→PDF 参数
        self._build_param_panel_common()    # 通用（无额外参数）
        self._build_param_panel_batch()     # 批量转换 参数

        # 默认显示通用面板
        self._show_param_panel("common")

        # ===== 区域4：输出目录 =====
        self._output_card, output_layout = self._make_card()
        main_layout.addWidget(self._output_card)

        self._lbl_output = QLabel("输出目录")
        self._lbl_output.setStyleSheet(CARD_LABEL_STYLE)
        output_layout.addWidget(self._lbl_output)

        output_row = QHBoxLayout()
        output_row.setSpacing(8)

        self._lbl_output_path = QLabel("未选择")
        self._lbl_output_path.setStyleSheet("color: #848E9C; font-size: 13px; background: transparent; border: none;")
        self._lbl_output_path.setMinimumWidth(400)
        self._lbl_output_path.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        output_row.addWidget(self._lbl_output_path)

        self._btn_output = QPushButton("选择目录")
        self._btn_output.setStyleSheet(BTN_OUTLINE_STYLE)
        self._btn_output.setMinimumSize(100, 36)
        output_row.addWidget(self._btn_output)

        output_layout.addLayout(output_row)

        # ===== 区域5：底部操作 =====
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(16)

        self._btn_start = QPushButton("开始转换")
        self._btn_start.setMinimumSize(140, 40)
        self._btn_start.setStyleSheet(BTN_PRIMARY_STYLE)
        self._btn_start.setEnabled(False)
        bottom_row.addWidget(self._btn_start)

        self._lbl_status = QLabel("")
        self._lbl_status.setStyleSheet("color: #848E9C; font-size: 13px; background: transparent; border: none;")
        bottom_row.addWidget(self._lbl_status)

        bottom_row.addStretch()

        main_layout.addLayout(bottom_row)

        # 进度条
        self._progress = QProgressBar()
        self._progress.setStyleSheet(PROGRESS_STYLE)
        self._progress.setValue(0)
        self._progress.setTextVisible(False)
        self._progress.setMaximumHeight(6)
        main_layout.addWidget(self._progress)

        # 结果提示卡
        self._result_card = QFrame()
        self._result_card.setStyleSheet("""
            QFrame {
                background-color: #1A1A22;
                border: 1px solid #4D7CFE;
                border-radius: 8px;
                padding: 12px 16px;
            }
        """)
        self._result_card.setVisible(False)
        main_layout.addWidget(self._result_card)

        result_layout = QVBoxLayout(self._result_card)
        result_layout.setSpacing(4)
        result_layout.setContentsMargins(0, 0, 0, 0)

        self._lbl_result_title = QLabel("✓ 转换完成")
        self._lbl_result_title.setStyleSheet("color: #4D7CFE; font-size: 14px; font-weight: 600; background: transparent; border: none; padding: 0;")
        result_layout.addWidget(self._lbl_result_title)

        self._lbl_result_info = QLabel("")
        self._lbl_result_info.setStyleSheet("color: #EAECEF; font-size: 13px; background: transparent; border: none; padding: 0;")
        result_layout.addWidget(self._lbl_result_info)

        # 底部留白
        main_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.setLayout(main_layout)

    def _make_card(self):
        """创建卡片容器"""
        card = QFrame()
        card.setStyleSheet(CARD_STYLE)
        layout = QVBoxLayout(card)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)
        return card, layout

    # ----------------------------------------------------------------
    # 参数面板构建
    # ----------------------------------------------------------------
    def _build_param_panel_pdf_img(self):
        """PDF → 图片 参数面板"""
        panel = QFrame()
        panel.setStyleSheet("background: transparent; border: none;")
        vbox = QVBoxLayout(panel)
        vbox.setSpacing(10)
        vbox.setContentsMargins(0, 0, 0, 0)

        # 第一行：格式 + DPI
        row1 = QHBoxLayout()
        row1.setSpacing(16)

        # 格式选择
        fmt_box = QHBoxLayout()
        self._lbl_fmt = QLabel("输出格式：")
        self._lbl_fmt.setStyleSheet("color: #848E9C; font-size: 13px; background: transparent; border: none;")
        fmt_box.addWidget(self._lbl_fmt)

        self._combo_fmt = QComboBox()
        self._combo_fmt.addItems(["PNG", "JPEG", "WebP", "BMP"])
        self._combo_fmt.setCurrentText("PNG")
        self._combo_fmt.setStyleSheet(COMBO_STYLE)
        self._combo_fmt.setMinimumWidth(100)
        fmt_box.addWidget(self._combo_fmt)
        fmt_box.addStretch()
        row1.addLayout(fmt_box)

        # DPI 选择
        dpi_box = QHBoxLayout()
        self._lbl_dpi = QLabel("DPI：")
        self._lbl_dpi.setStyleSheet("color: #848E9C; font-size: 13px; background: transparent; border: none;")
        dpi_box.addWidget(self._lbl_dpi)

        self._combo_dpi = QComboBox()
        self._combo_dpi.addItems(["72", "150", "200", "300"])
        self._combo_dpi.setCurrentText("150")
        self._combo_dpi.setStyleSheet(COMBO_STYLE)
        self._combo_dpi.setMinimumWidth(80)
        dpi_box.addWidget(self._combo_dpi)
        dpi_box.addStretch()
        row1.addLayout(dpi_box)

        row1.addStretch()
        vbox.addLayout(row1)

        # 提示文字
        self._lbl_hint_pdf_img = QLabel("提示：PNG 支持透明背景，JPEG 体积更小")
        self._lbl_hint_pdf_img.setStyleSheet("color: #555; font-size: 12px; background: transparent; border: none;")
        vbox.addWidget(self._lbl_hint_pdf_img)

        self._param_panels["pdf_img"] = panel

    def _build_param_panel_img_pdf(self):
        """图片 → PDF 参数面板"""
        panel = QFrame()
        panel.setStyleSheet("background: transparent; border: none;")
        vbox = QVBoxLayout(panel)
        vbox.setSpacing(10)
        vbox.setContentsMargins(0, 0, 0, 0)

        # 第一行：方向 + 质量
        row1 = QHBoxLayout()
        row1.setSpacing(16)

        # 方向选择
        orient_box = QHBoxLayout()
        self._lbl_orient = QLabel("页面方向：")
        self._lbl_orient.setStyleSheet("color: #848E9C; font-size: 13px; background: transparent; border: none;")
        orient_box.addWidget(self._lbl_orient)

        self._combo_orient = QComboBox()
        self._combo_orient.addItems(["纵向", "横向", "自动"])
        self._combo_orient.setCurrentText("纵向")
        self._combo_orient.setStyleSheet(COMBO_STYLE)
        self._combo_orient.setMinimumWidth(100)
        orient_box.addWidget(self._combo_orient)
        orient_box.addStretch()
        row1.addLayout(orient_box)

        # 质量选择
        qual_box = QHBoxLayout()
        self._lbl_qual = QLabel("图片质量：")
        self._lbl_qual.setStyleSheet("color: #848E9C; font-size: 13px; background: transparent; border: none;")
        qual_box.addWidget(self._lbl_qual)

        self._combo_qual = QComboBox()
        self._combo_qual.addItems(["低（压缩率高）", "中", "高（最佳质量）"])
        self._combo_qual.setCurrentText("高（最佳质量）")
        self._combo_qual.setStyleSheet(COMBO_STYLE)
        self._combo_qual.setMinimumWidth(130)
        qual_box.addWidget(self._combo_qual)
        qual_box.addStretch()
        row1.addLayout(qual_box)

        row1.addStretch()
        vbox.addLayout(row1)

        # 第二行：纸张大小
        row2 = QHBoxLayout()
        row2.setSpacing(16)

        page_box = QHBoxLayout()
        self._lbl_page = QLabel("页面大小：")
        self._lbl_page.setStyleSheet("color: #848E9C; font-size: 13px; background: transparent; border: none;")
        page_box.addWidget(self._lbl_page)

        self._combo_page = QComboBox()
        self._combo_page.addItems(["A4", "A3", "Letter", "Legal", "自动适应"])
        self._combo_page.setCurrentText("A4")
        self._combo_page.setStyleSheet(COMBO_STYLE)
        self._combo_page.setMinimumWidth(120)
        page_box.addWidget(self._combo_page)
        page_box.addStretch()
        row2.addLayout(page_box)

        row2.addStretch()
        vbox.addLayout(row2)

        self._param_panels["img_pdf"] = panel

    def _build_param_panel_common(self):
        """通用参数面板（无额外参数）"""
        panel = QFrame()
        panel.setStyleSheet("background: transparent; border: none;")
        vbox = QVBoxLayout(panel)
        vbox.setSpacing(4)
        vbox.setContentsMargins(0, 0, 0, 0)

        hint = QLabel("此格式无需额外参数，请直接选择文件并点击开始转换")
        hint.setStyleSheet("color: #555; font-size: 13px; background: transparent; border: none;")
        vbox.addWidget(hint)

        self._param_panels["common"] = panel

    def _build_param_panel_batch(self):
        """批量转换参数面板"""
        panel = QFrame()
        panel.setStyleSheet("background: transparent; border: none;")
        vbox = QVBoxLayout(panel)
        vbox.setSpacing(10)
        vbox.setContentsMargins(0, 0, 0, 0)

        # 输出格式选择
        row = QHBoxLayout()
        row.setSpacing(16)

        self._lbl_batch_fmt = QLabel("输出格式：")
        self._lbl_batch_fmt.setStyleSheet("color: #848E9C; font-size: 13px; background: transparent; border: none;")
        row.addWidget(self._lbl_batch_fmt)

        self._combo_batch_fmt = QComboBox()
        self._combo_batch_fmt.addItems(["PDF（图片转PDF）", "Word（PDF转Word）", "Excel（PDF转Excel）", "PPT（PDF转PPT）", "图片（PDF转图片）"])
        self._combo_batch_fmt.setCurrentText("PDF（图片转PDF）")
        self._combo_batch_fmt.setStyleSheet(COMBO_STYLE)
        self._combo_batch_fmt.setMinimumWidth(160)
        row.addWidget(self._combo_batch_fmt)
        row.addStretch()
        vbox.addLayout(row)

        # 提示
        hint = QLabel("提示：批量转换将根据输入文件类型自动适配，图片→PDF 或 PDF→所选格式")
        hint.setStyleSheet("color: #555; font-size: 12px; background: transparent; border: none;")
        vbox.addWidget(hint)

        self._param_panels["batch"] = panel

    def _show_param_panel(self, key):
        """切换显示参数面板"""
        # 移除所有现有面板
        while self._param_stack.count():
            child = self._param_stack.takeAt(0)
            if child.widget():
                child.widget().hide()

        # 添加选中的面板
        panel = self._param_panels.get(key, self._param_panels["common"])
        self._param_stack.addWidget(panel)
        panel.show()

    # ----------------------------------------------------------------
    # 信号连接
    # ----------------------------------------------------------------
    def _connect(self):
        self._btn_select.clicked.connect(self._pick)
        self._btn_clear.clicked.connect(self._clear)
        self._btn_start.clicked.connect(self._start)
        self._btn_output.clicked.connect(self._pick_output)

        # 转换类型按钮
        self._type_group.buttonClicked.connect(self._on_type_changed)

        # 参数变化监听
        self._combo_fmt.currentTextChanged.connect(lambda t: self._params.update({"fmt": t.lower()}))
        self._combo_dpi.currentTextChanged.connect(lambda t: self._params.update({"dpi": int(t)}))

        orient_map = {"纵向": "portrait", "横向": "landscape", "自动": "auto"}
        self._combo_orient.currentTextChanged.connect(
            lambda t: self._params.update({"orientation": orient_map.get(t, "portrait")}))

        qual_map = {"低（压缩率高）": "low", "中": "medium", "高（最佳质量）": "high"}
        self._combo_qual.currentTextChanged.connect(
            lambda t: self._params.update({"quality": qual_map.get(t, "high")}))

    def _on_type_changed(self, btn):
        """切换转换类型（接收点击的按钮）"""
        btn_id = self._type_group.id(btn)
        if btn_id < 0 or btn_id >= len(CONV_TYPES):
            return
        ct = CONV_TYPES[btn_id]
        key = ct["key"]
        self._selected_type = key

        # 更新按钮样式
        for k, b in self._type_btns.items():
            b.setStyleSheet(BTN_TYPE_SELECTED_STYLE if k == key else BTN_TYPE_STYLE)

        # 切换参数面板
        if key == "pdf_img":
            self._show_param_panel("pdf_img")
        elif key == "img_pdf":
            self._show_param_panel("img_pdf")
        elif key == "batch":
            self._show_param_panel("batch")
        else:
            self._show_param_panel("common")

        # 切换文件选择提示（自动清空当前列表重新选择）
        self._lbl_status.setText("")

    # ----------------------------------------------------------------
    # 文件选择
    # ----------------------------------------------------------------
    def _pick(self):
        if self._busy:
            return

        # 根据转换类型确定允许的文件类型
        if self._selected_type in ("img_pdf",):
            ext_filter = "Image Files (*.png *.jpg *.jpeg *.bmp *.tiff *.webp)"
            title = "选择图片"
        elif self._selected_type == "batch":
            ext_filter = "All Files (*.pdf *.png *.jpg *.jpeg *.bmp *.tiff *.webp)"
            title = "选择文件（支持多选）"
        else:
            ext_filter = "PDF Files (*.pdf)"
            title = "选择PDF"

        files, _ = QFileDialog.getOpenFileNames(
            self,
            title,
            "",
            ext_filter
        )
        if not files:
            return
        for p in files:
            if p and os.path.exists(p):
                if p.lower() not in [x.lower() for x in self._paths]:
                    self._paths.append(p)
                    self._add_list_item(p, os.path.getsize(p))
                    add_record(p, "convert")
        self._update_count()

    def _add_list_item(self, path, size=0):
        name = os.path.basename(path)
        if size > 0:
            size_str = self._format_size(size)
            txt = f"⏳ {name}  |  {size_str}"
        else:
            txt = f"⏳ {name}  |  ???"
        item = QListWidgetItem(txt)
        item.setData(Qt.UserRole + 1, path)
        item.setData(Qt.UserRole + 2, size)
        item.setData(Qt.UserRole + 3, "waiting")
        self._file_list.addItem(item)

    def _clear(self):
        if self._busy:
            return
        self._paths.clear()
        self._file_list.clear()
        self._result_card.setVisible(False)
        self._lbl_status.setText("")
        self._progress.setValue(0)
        self._update_count()

    def _update_count(self):
        n = len(self._paths)
        self._lbl_count.setText(f"已选 {n} 个文件")
        self._btn_start.setEnabled(n > 0)

    def _pick_output(self):
        path = QFileDialog.getExistingDirectory(
            self,
            "选择输出目录"
        )
        if path:
            self._output_dir = path
            self._lbl_output_path.setText(path)

    # ----------------------------------------------------------------
    # 转换逻辑
    # ----------------------------------------------------------------
    def _start(self):
        if self._busy or not self._paths:
            return

        if not hasattr(self, "_output_dir") or not self._output_dir:
            self._lbl_status.setText("请先选择输出目录")
            return

        # 获取转换函数
        func_map = {
            "pdf_word": pdf_to_word,
            "pdf_excel": pdf_to_excel,
            "pdf_ppt": pdf_to_ppt,
            "pdf_img": pdf_to_images,
            "img_pdf": images_to_pdf,
            "batch": batch_convert,
        }
        func = func_map.get(self._selected_type)
        if func is None:
            self._lbl_status.setText("错误：未找到转换函数")
            return

        self._busy = True
        self._ok = 0
        self._fail = 0
        self._result_card.setVisible(False)
        self._lbl_status.setText("")
        self._btn_start.setEnabled(False)
        self._btn_select.setEnabled(False)
        self._btn_clear.setEnabled(False)
        self._progress.setMaximum(len(self._paths))
        self._progress.setValue(0)
        self._idx = 0
        self._total = len(self._paths)
        self._func = func

        # 更新列表状态
        for i in range(self._file_list.count()):
            it = self._file_list.item(i)
            it.setData(Qt.UserRole + 3, "waiting")
            p = it.data(Qt.UserRole + 1)
            s = self._format_size(it.data(Qt.UserRole + 2))
            it.setText(f"⏳ {os.path.basename(p)}  |  {s}")

        self._lbl_status.setText("准备开始...")
        self._next()

    def _next(self):
        if self._idx >= len(self._paths):
            self._done_all()
            return

        fp = self._paths[self._idx]
        base = os.path.splitext(os.path.basename(fp))[0]

        # 确定输出路径
        out_ext = {
            "pdf_word": ".docx", "pdf_excel": ".xlsx", "pdf_ppt": ".pptx",
            "pdf_img": "", "img_pdf": ".pdf", "batch": "",
        }.get(self._selected_type, "")

        if self._selected_type == "pdf_img":
            out_dir = os.path.join(self._output_dir, base + "_images")
            os.makedirs(out_dir, exist_ok=True)
            out = out_dir
        elif self._selected_type == "pdf_ppt":
            # pdf_to_ppt 期望 output_dir（目录），不是文件路径
            os.makedirs(self._output_dir, exist_ok=True)
            out = self._output_dir
        elif self._selected_type == "batch":
            out_dir = os.path.join(self._output_dir, "batch_output")
            os.makedirs(out_dir, exist_ok=True)
            out = out_dir
        else:
            out = os.path.join(self._output_dir, base + out_ext)

        it = self._file_list.item(self._idx)
        it.setText(f"⚙️ {os.path.basename(fp)}  |  转换中...")
        it.setData(Qt.UserRole + 3, "processing")

        self._lbl_status.setText(f"正在转换 ({self._idx + 1}/{self._total})...")

        # 准备额外参数
        extra = None
        if self._selected_type == "pdf_img":
            extra = {"fmt": self._params["fmt"], "dpi": self._params["dpi"]}
        elif self._selected_type == "img_pdf":
            extra = {"orientation": self._params["orientation"], "quality": self._params["quality"]}
        elif self._selected_type == "batch":
            batch_fmt_map = {
                "PDF（图片转PDF）": "pdf",
                "Word（PDF转Word）": "word",
                "Excel（PDF转Excel）": "excel",
                "PPT（PDF转PPT）": "ppt",
                "图片（PDF转图片）": "img"
            }
            batch_fmt = batch_fmt_map.get(self._combo_batch_fmt.currentText(), "pdf")
            extra = {"batch_fmt": batch_fmt}

        w = ConvertWorker(self._idx, fp, out, func=self._func, extra=extra)
        w.finished.connect(self._on_done)
        w.error.connect(self._on_error)
        self._worker = w
        w.start()

    def _on_done(self, idx, result):
        fp = self._paths[idx]
        it = self._file_list.item(idx)
        it.setText(f"✅ {os.path.basename(fp)}  |  转换完成")
        it.setData(Qt.UserRole + 3, "done")
        self._ok += 1
        self._progress.setValue(idx + 1)

        # 记录到最近使用
        output_path = result.get("output", "") if isinstance(result, dict) else ""
        if output_path and os.path.exists(output_path):
            add_record(fp, "convert", output_path)

        self._idx += 1
        if self._idx < len(self._paths):
            self._next()
        else:
            self._done_all()

    def _on_error(self, idx, msg):
        fp = self._paths[idx]
        it = self._file_list.item(idx)
        short = msg[:50] + "..." if len(msg) > 50 else msg
        it.setText(f"❌ {os.path.basename(fp)}  |  失败: {short}")
        it.setData(Qt.UserRole + 3, "failed")
        self._fail += 1
        self._progress.setValue(idx + 1)

        # 使用统一错误处理弹窗
        ErrorHandler.show_error_dialog(
            title="转换失败",
            message=f"文件「{os.path.basename(fp)}」转换失败",
            details=msg,
            parent_widget=self,
        )

        self._idx += 1
        if self._idx < len(self._paths):
            self._next()
        else:
            self._done_all()

    def _done_all(self):
        self._busy = False
        self._btn_start.setEnabled(True)
        self._btn_select.setEnabled(True)
        self._btn_clear.setEnabled(True)
        self._result_card.setVisible(True)

        if self._fail == 0:
            self._lbl_result_title.setText("✓ 转换完成")
            self._lbl_result_title.setStyleSheet("color: #4D7CFE; font-size: 14px; font-weight: 600; background: transparent; border: none; padding: 0;")
        else:
            self._lbl_result_title.setText(f"⚠️ 转换完成（{self._fail} 个失败）")
            self._lbl_result_title.setStyleSheet("color: #FF9500; font-size: 14px; font-weight: 600; background: transparent; border: none; padding: 0;")

        info = f"成功: {self._ok} | 失败: {self._fail} | 总计: {len(self._paths)} 个文件"

        if self._selected_type == "pdf_excel":
            info += "\n智能提取完成，复杂表格建议检查微调"

        self._lbl_result_info.setText(info)
        self._lbl_status.setText(f"完成！({self._total}/{self._total})")

    # ----------------------------------------------------------------
    # i18n: 重译所有界面文字
    # ----------------------------------------------------------------
    def retranslateUi(self):
        _t = QCoreApplication.translate
        ctx = "ConvertPage"

        # 区域1：文件选择
        self._btn_select.setText(_t(ctx, "选择文件", None))
        self._btn_clear.setText(_t(ctx, "清空", None))

        # 区域2：转换格式
        self._lbl_type.setText(_t(ctx, "转换格式", None))
        labels_map = {
            "pdf_word": _t(ctx, "PDF → Word", None),
            "pdf_excel": _t(ctx, "PDF → Excel", None),
            "pdf_ppt": _t(ctx, "PDF → PPT", None),
            "pdf_img": _t(ctx, "PDF → 图片", None),
            "img_pdf": _t(ctx, "图片 → PDF", None),
            "batch": _t(ctx, "批量转换", None),
        }
        for key, btn in self._type_btns.items():
            btn.setText(labels_map.get(key, key))

        # 区域3：参数设置
        self._lbl_param.setText(_t(ctx, "参数设置", None))
        # 更新类型按钮下方提示
        hint_map = {
            "pdf_word": _t(ctx, "此格式无需额外参数，请直接选择文件并点击开始转换", None),
            "pdf_excel": _t(ctx, "此格式无需额外参数，请直接选择文件并点击开始转换", None),
            "pdf_ppt": _t(ctx, "此格式无需额外参数，请直接选择文件并点击开始转换", None),
        }

        # 区域4：输出目录
        self._lbl_output.setText(_t(ctx, "输出目录", None))
        if not getattr(self, "_output_dir", None):
            self._lbl_output_path.setText(_t(ctx, "未选择", None))
        self._btn_output.setText(_t(ctx, "选择目录", None))

        # 区域5：操作
        if not self._busy:
            self._btn_start.setText(_t(ctx, "开始转换", None))

        # 参数面板标签
        self._lbl_fmt.setText(_t(ctx, "输出格式：", None))
        self._lbl_dpi.setText(_t(ctx, "DPI：", None))
        self._lbl_hint_pdf_img.setText(_t(ctx, "提示：PNG 支持透明背景，JPEG 体积更小", None))

        self._lbl_orient.setText(_t(ctx, "页面方向：", None))
        self._lbl_qual.setText(_t(ctx, "图片质量：", None))
        self._lbl_page.setText(_t(ctx, "页面大小：", None))

        self._lbl_hint_common.setText(_t(ctx, "此格式无需额外参数，请直接选择文件并点击开始转换", None))

        self._lbl_batch_fmt.setText(_t(ctx, "输出格式：", None))
        self._lbl_hint_batch.setText(_t(ctx, "提示：批量转换将根据输入文件类型自动适配，图片→PDF 或 PDF→所选格式", None))

        # ComboBox 项目
        self._combo_fmt.blockSignals(True)
        current_fmt = self._combo_fmt.currentText()
        self._combo_fmt.clear()
        for txt in ["PNG", "JPEG", "WebP", "BMP"]:
            self._combo_fmt.addItem(txt)
        self._combo_fmt.setCurrentText(current_fmt)
        self._combo_fmt.blockSignals(False)

        self._combo_orient.blockSignals(True)
        current_orient = self._combo_orient.currentText()
        self._combo_orient.clear()
        for txt in [_t(ctx, "纵向", None), _t(ctx, "横向", None), _t(ctx, "自动", None)]:
            self._combo_orient.addItem(txt)
        self._combo_orient.setCurrentText(current_orient)
        self._combo_orient.blockSignals(False)

        self._combo_qual.blockSignals(True)
        current_qual = self._combo_qual.currentText()
        self._combo_qual.clear()
        for txt in [_t(ctx, "低（压缩率高）", None), _t(ctx, "中", None), _t(ctx, "高（最佳质量）", None)]:
            self._combo_qual.addItem(txt)
        self._combo_qual.setCurrentText(current_qual)
        self._combo_qual.blockSignals(False)

        self._combo_page.blockSignals(True)
        current_page = self._combo_page.currentText()
        self._combo_page.clear()
        for txt in ["A4", "A3", "Letter", "Legal", _t(ctx, "自动适应", None)]:
            self._combo_page.addItem(txt)
        self._combo_page.setCurrentText(current_page)
        self._combo_page.blockSignals(False)

        self._combo_batch_fmt.blockSignals(True)
        current_batch = self._combo_batch_fmt.currentText()
        self._combo_batch_fmt.clear()
        for txt in [_t(ctx, "PDF（图片转PDF）", None), _t(ctx, "Word（PDF转Word）", None),
                     _t(ctx, "Excel（PDF转Excel）", None), _t(ctx, "PPT（PDF转PPT）", None),
                     _t(ctx, "图片（PDF转图片）", None)]:
            self._combo_batch_fmt.addItem(txt)
        self._combo_batch_fmt.setCurrentText(current_batch)
        self._combo_batch_fmt.blockSignals(False)

        # 重新设置 hint_map 中的提示
        if hasattr(self, "_lbl_hint_pdf_img"):
            self._lbl_hint_pdf_img.setText(_t(ctx, "提示：PNG 支持透明背景，JPEG 体积更小", None))
        if hasattr(self, "_lbl_hint_common"):
            self._lbl_hint_common.setText(_t(ctx, "此格式无需额外参数，请直接选择文件并点击开始转换", None))
        if hasattr(self, "_lbl_hint_batch"):
            self._lbl_hint_batch.setText(_t(ctx, "提示：批量转换将根据输入文件类型自动适配，图片→PDF 或 PDF→所选格式", None))

        # 更新文件计数
        self._update_count()

    # ----------------------------------------------------------------
    # 工具方法
    # ----------------------------------------------------------------
    @staticmethod
    def _format_size(b):
        if b < 1024:
            return f"{b} B"
        elif b < 1024 * 1024:
            return f"{b / 1024:.1f} KB"
        else:
            return f"{b / 1024 / 1024:.2f} MB"

    def apply_theme(self, colors):
        """Apply theme colors to all widget inline styles.

        Args:
            colors: dict with theme color tokens (from src.common.theme)
        """
        c = colors

        # --- Build themed style strings ---
        card_style = (
            f"QFrame {{"
            f"    background-color: {c['card_bg']};"
            f"    border: 1px solid {c['border_light']};"
            f"    border-radius: 8px;"
            f"    padding: 16px;"
            f"}}"
        )
        card_label_style = (
            f"color: {c['text_main']}; font-size: 14px; font-weight: 600;"
            f" background: transparent; border: none; padding: 0; margin: 0;"
        )
        btn_primary_style = (
            f"QPushButton {{"
            f"    background-color: {c['primary']};"
            f"    color: {c['white']};"
            f"    border: none;"
            f"    border-radius: 8px;"
            f"    font-size: 14px;"
            f"    font-weight: 600;"
            f"    padding: 0 20px;"
            f"    min-height: 40px;"
            f"}}"
            f"QPushButton:hover {{ background-color: {c['primary_hover']}; }}"
            f"QPushButton:pressed {{ background-color: {c['primary_pressed']}; }}"
            f"QPushButton:disabled {{ background-color: {c['disabled_bg_qss']}; color: {c['text_sub']}; }}"
        )
        btn_ghost_style = (
            f"QPushButton {{"
            f"    background-color: transparent;"
            f"    border: none;"
            f"    color: {c['text_sub']};"
            f"    font-size: 13px;"
            f"    padding: 0 8px;"
            f"    min-height: 40px;"
            f"}}"
            f"QPushButton:hover {{ color: {c['text_main']}; }}"
        )
        btn_type_style = (
            f"QPushButton {{"
            f"    background-color: {c['bg']};"
            f"    border: 1px solid {c['border_light']};"
            f"    border-radius: 6px;"
            f"    color: {c['text_sub']};"
            f"    font-size: 13px;"
            f"    padding: 8px 16px;"
            f"    min-height: 36px;"
            f"}}"
            f"QPushButton:hover {{ border-color: {c['primary']}; color: {c['text_main']}; }}"
            f"QPushButton QWidget {{ background: transparent; }}"
        )
        btn_type_selected_style = (
            f"QPushButton {{"
            f"    background-color: {c['primary']};"
            f"    border: 1px solid {c['primary']};"
            f"    border-radius: 6px;"
            f"    color: {c['white']};"
            f"    font-size: 13px;"
            f"    font-weight: 600;"
            f"    padding: 8px 16px;"
            f"    min-height: 36px;"
            f"}}"
        )
        btn_outline_style = (
            f"QPushButton {{"
            f"    background-color: transparent;"
            f"    border: 1px solid {c['border_light']};"
            f"    border-radius: 6px;"
            f"    color: {c['text_main']};"
            f"    font-size: 13px;"
            f"    padding: 8px 16px;"
            f"    min-height: 36px;"
            f"}}"
            f"QPushButton:hover {{ border-color: {c['primary']}; color: {c['primary']}; }}"
        )
        file_list_style = (
            f"QListWidget {{"
            f"    background-color: {c['bg']};"
            f"    border: 1px solid {c['border_light']};"
            f"    border-radius: 6px;"
            f"    padding: 4px;"
            f"    outline: none;"
            f"}}"
            f"QListWidget::item {{"
            f"    background: transparent;"
            f"    border-radius: 4px;"
            f"    margin: 1px;"
            f"    padding: 6px 10px;"
            f"    min-height: 30px;"
            f"    color: {c['text_main']};"
            f"    font-size: 12px;"
            f"}}"
            f"QListWidget::item:hover {{ background: {c['hover_bg']}; }}"
        )
        combo_style = (
            f"QComboBox {{"
            f"    background-color: {c['input_bg']};"
            f"    border: 1px solid {c['border_light']};"
            f"    border-radius: 6px;"
            f"    padding: 8px 12px;"
            f"    color: {c['text_main']};"
            f"    font-size: 13px;"
            f"    min-height: 32px;"
            f"}}"
            f"QComboBox:hover {{ border-color: {c['primary']}; }}"
            f"QComboBox::drop-down {{ border: none; width: 20px; }}"
            f"QComboBox QAbstractItemView {{"
            f"    background-color: {c['card_bg']};"
            f"    border: 1px solid {c['border_light']};"
            f"    border-radius: 6px;"
            f"    padding: 4px;"
            f"    color: {c['text_main']};"
            f"    selection-background-color: {c['primary']};"
            f"}}"
        )
        progress_style = (
            f"QProgressBar {{"
            f"    background-color: {c['progress_bg']};"
            f"    border: none;"
            f"    border-radius: 3px;"
            f"    min-height: 6px;"
            f"    max-height: 6px;"
            f"}}"
            f"QProgressBar::chunk {{ background-color: {c['primary']}; border-radius: 3px; }}"
        )
        text_sub_style = (
            f"color: {c['text_sub']}; font-size: 13px;"
            f" background: transparent; border: none;"
        )
        text_main_style = (
            f"color: {c['text_main']}; font-size: 13px;"
            f" background: transparent; border: none;"
        )
        primary_text_style = (
            f"color: {c['primary']}; font-size: 14px; font-weight: 600;"
            f" background: transparent; border: none; padding: 0;"
        )
        result_card_style = (
            f"QFrame {{"
            f"    background-color: {c['card_bg']};"
            f"    border: 1px solid {c['primary']};"
            f"    border-radius: 8px;"
            f"    padding: 12px 16px;"
            f"}}"
        )

        # --- Apply styles to widgets ---

        # File card (area 1)
        self._file_card.setStyleSheet(card_style)
        self._btn_select.setStyleSheet(btn_primary_style)
        self._btn_clear.setStyleSheet(btn_ghost_style)
        self._lbl_count.setStyleSheet(text_sub_style)
        self._file_list.setStyleSheet(file_list_style)

        # Type card (area 2)
        self._type_card.setStyleSheet(card_style)
        self._lbl_type.setStyleSheet(card_label_style)
        for key, btn in self._type_btns.items():
            if key == self._selected_type:
                btn.setStyleSheet(btn_type_selected_style)
            else:
                btn.setStyleSheet(btn_type_style)

        # Param card (area 3)
        self._param_card.setStyleSheet(card_style)
        self._lbl_param.setStyleSheet(card_label_style)

        # Output card (area 4)
        self._output_card.setStyleSheet(card_style)
        self._lbl_output.setStyleSheet(card_label_style)
        self._lbl_output_path.setStyleSheet(text_main_style)
        self._btn_output.setStyleSheet(btn_outline_style)

        # Bottom area (area 5)
        self._btn_start.setStyleSheet(btn_primary_style)
        self._lbl_status.setStyleSheet(text_sub_style)
        self._progress.setStyleSheet(progress_style)

        # Result card
        self._result_card.setStyleSheet(result_card_style)
        self._lbl_result_title.setStyleSheet(primary_text_style)
        self._lbl_result_info.setStyleSheet(text_main_style)

        # Combo boxes
        self._combo_fmt.setStyleSheet(combo_style)
        self._combo_dpi.setStyleSheet(combo_style)
        self._combo_orient.setStyleSheet(combo_style)
        self._combo_qual.setStyleSheet(combo_style)
        self._combo_page.setStyleSheet(combo_style)
        self._combo_batch_fmt.setStyleSheet(combo_style)

        # Parameter labels
        param_labels = [
            self._lbl_fmt, self._lbl_dpi, self._lbl_hint_pdf_img,
            self._lbl_orient, self._lbl_qual, self._lbl_page,
            self._lbl_batch_fmt,
        ]
        for lbl in param_labels:
            lbl.setStyleSheet(text_sub_style)

        # Hint labels that may or may not exist as instance attributes
        for attr_name in ('_lbl_hint_common', '_lbl_hint_batch'):
            if hasattr(self, attr_name):
                getattr(self, attr_name).setStyleSheet(text_sub_style)
