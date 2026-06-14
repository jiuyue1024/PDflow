"""
watermark_page.py — 水印功能 PySide6 界面
布局：左侧参数面板 + 右侧预览区
后端：调用 src/common/legacy_watermark.py

v2: 所有数值参数改为「滑条+数字输入」组合，修复导出旋转角度不匹配
"""
import sys
import os
import base64
import io
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QSpinBox, QDoubleSpinBox, QSlider, QComboBox, QGroupBox,
    QFileDialog, QColorDialog, QScrollArea, QFrame,
    QSizePolicy, QCheckBox, QMessageBox, QProgressBar,
    QAbstractSpinBox, QApplication,
)
from PySide6.QtCore import Qt, QTimer, QThread, Signal, QCoreApplication
from PySide6.QtGui import QPixmap, QImage, QColor, QPainter, QFont

# ── 后端导入 ──
# 预览：V1.1-RC3 重构（方案 B：缓存底图 + 只重画水印层，参数变化 ≤30ms）
# 导出：legacy_watermark 链路保持不变（用户已确认导出正确）
from src.common.watermark_preview import render_watermark_preview
from src.common.preview_renderer import MAX_DPR
from src.common.legacy_watermark import (
    do_watermark,
    normalize_watermark_params,
)
from src.common.recent_files_manager import add_record
from src.common.error_handler import ErrorHandler, ErrorType

# ================================================================
# 水印类型和位置选项
# ================================================================
WATERMARK_TYPES = ["文字水印", "图片水印"]
POSITION_OPTIONS = ["居中", "平铺", "左上角", "右上角", "左下角", "右下角"]
POSITION_MAP = {
    "居中": "center", "平铺": "tile",
    "左上角": "top-left", "右上角": "top-right",
    "左下角": "bottom-left", "右下角": "bottom-right",
}
LAYER_OPTIONS = ["覆盖 (over)", "底层 (under)"]
LAYER_MAP = {"覆盖 (over)": "over", "底层 (under)": "under"}


# ================================================================
# 样式常量
# ================================================================
SLIDER_STYLE = """
QSlider::groove:horizontal {
    background: #2B3139;
    border: none;
    border-radius: 3px;
    height: 6px;
}
QSlider::sub-page:horizontal {
    background: #4D7CFE;
    border: none;
    border-radius: 3px;
    height: 6px;
}
QSlider::handle:horizontal {
    background: #EAECEF;
    border: none;
    border-radius: 7px;
    width: 14px;
    height: 14px;
    margin: -4px 0;
}
QSlider::handle:horizontal:hover {
    background: #FFFFFF;
}
"""

DOUBLESPIN_STYLE = """
QDoubleSpinBox {
    background-color: #1A1A22;
    border: 1px solid #2B3139;
    border-radius: 6px;
    color: #EAECEF;
    padding: 4px 8px;
    min-height: 32px;
    max-width: 100px;
}
"""

COMBOBOX_STYLE = """
QComboBox {
    background-color: #1A1A22;
    border: 1px solid #2B3139;
    border-radius: 6px;
    color: #EAECEF;
    font-size: 14px;
    padding: 4px 8px;
    min-height: 32px;
}
QComboBox:focus {
    border: 1px solid #3E7FFF;
}
QComboBox::drop-down {
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 24px;
    border: none;
    border-top-right-radius: 6px;
    border-bottom-right-radius: 6px;
}
QComboBox::down-arrow {
    image: none;
    width: 0;
    height: 0;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #848E9C;
}
QComboBox QAbstractItemView {
    background-color: #1E2329;
    border: 1px solid #2B3139;
    border-radius: 4px;
    outline: none;
    padding: 2px;
}
QComboBox QAbstractItemView::item {
    color: #EAECEF;
    background-color: transparent;
    padding: 6px 8px;
    border: none;
    min-height: 28px;
}
QComboBox QAbstractItemView::item:hover,
QComboBox QAbstractItemView::item:selected {
    background-color: #3E7FFF;
    color: #FFFFFF;
    border: none;
    border-radius: 3px;
}
"""

BUTTON_ARROW_STYLE = """
QPushButton {
    background-color: #1E2329;
    border: none;
    border-radius: 2px;
    color: #848E9C;
    font-size: 8px;
    width: 16px;
    height: 14px;
    padding: 0;
    margin: 0;
}
QPushButton:hover {
    background-color: #2B3139;
}
QPushButton:pressed {
    background-color: #353C46;
}
"""

SPINBOX_STYLE = """
QSpinBox {
    background-color: #1A1A22;
    border: 1px solid #2B3139;
    border-radius: 4px;
    color: #EAECEF;
    padding: 0 6px;
    min-height: 32px;
    font-size: 13px;
}
QSpinBox:focus {
    border: 1px solid #4D7CFE;
}
QSpinBox::up-button, QSpinBox::down-button {
    width: 20px;
    border: none;
    background: transparent;
}
QSpinBox::up-arrow {
    width: 0; height: 0;
    border: 4px solid transparent;
    border-bottom-color: #8B8D98;
    margin-top: 4px;
}
QSpinBox::down-arrow {
    width: 0; height: 0;
    border: 4px solid transparent;
    border-top-color: #8B8D98;
    margin-bottom: 4px;
}
"""


# ================================================================
# 后台预览线程（避免界面卡顿）
# ================================================================
class PreviewWorker(QThread):
    finished = Signal(object)

    def __init__(self, pdf_path, params, target_width=640):
        super().__init__()
        self.pdf_path = pdf_path
        self.params = params
        self.target_width = target_width

    def run(self):
        try:
            result = render_watermark_preview(self.pdf_path, target_width=self.target_width, **self.params)
            self.finished.emit(result)
        except Exception as e:
            self.finished.emit({"success": False, "error": str(e)})


# ================================================================
# 导出线程
# ================================================================
class ExportWorker(QThread):
    finished = Signal(object)

    def __init__(self, pdf_path, output_path, params):
        super().__init__()
        self.pdf_path = pdf_path
        self.output_path = output_path
        self.params = params

    def run(self):
        try:
            result = do_watermark(self.pdf_path, self.output_path, **self.params)
            self.finished.emit(result)
        except Exception as e:
            self.finished.emit({"success": False, "error": str(e)})


# ================================================================
# 水印页面主控件
# ================================================================
class WatermarkPage(QWidget):
    """水印功能页面：左侧参数面板 + 右侧预览图"""

    PREVIEW_WIDTH, PREVIEW_HEIGHT = 640, 480

    def __init__(self, parent=None):
        super().__init__(parent)
        self._pdf_path = ""
        self._current_color = "#888888"
        self._preview_timer = QTimer(self)
        self._preview_timer.setSingleShot(True)
        # V1.1-RC3: 500 → 300ms，与模板排版一致（方案 B 实际渲染 ≤30ms，300ms 给用户"停手"时间）
        self._preview_timer.setInterval(300)
        self._preview_timer.timeout.connect(self._do_preview)

        # 存储 slider-spinbox 对，用于信号屏蔽
        self._slider_spin_pairs = []

        # i18n: 存储滑条标签引用
        self._slider_labels = []
        self._group_boxes = {}

        self._build_ui()
        self._connect_signals()

    # ── 工具方法：创建 滑条 + 数字输入 组合控件 ──

    def _make_slider_spin_row(self, label, min_val, max_val, default, suffix="", step=1):
        """创建水平布局：标签 + 滑条 + 数字框 + ▲按钮 + ▼按钮"""
        row = QHBoxLayout()
        row.setSpacing(4)

        # 标签
        lbl = QLabel(label)
        lbl.setFixedWidth(48)
        self._slider_labels.append(lbl)
        row.addWidget(lbl)

        # 滑条
        slider = QSlider(Qt.Horizontal)
        slider.setRange(int(min_val), int(max_val))
        slider.setValue(int(default))
        slider.setStyleSheet(SLIDER_STYLE)
        slider.setFixedHeight(22)
        row.addWidget(slider, stretch=1)

        # 数字输入框（隐藏默认箭头按钮）
        spin = QDoubleSpinBox()
        spin.setButtonSymbols(QAbstractSpinBox.NoButtons)
        spin.setRange(min_val, max_val)
        spin.setDecimals(0)
        spin.setValue(default)
        spin.setSingleStep(1)
        spin.setFixedWidth(100)
        if suffix:
            spin.setSuffix(suffix)
        spin.setStyleSheet(DOUBLESPIN_STYLE)
        row.addWidget(spin)

        # ▲ ▼ 自定义按钮，垂直排列
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(1)
        btn_layout.setContentsMargins(0, 0, 0, 0)

        btn_up = QPushButton("\u25B2")
        btn_up.setFixedSize(16, 14)
        btn_up.setStyleSheet(BUTTON_ARROW_STYLE)
        btn_up.clicked.connect(lambda: self._on_arrow_up(spin, slider, step))
        btn_layout.addWidget(btn_up)

        btn_down = QPushButton("\u25BC")
        btn_down.setFixedSize(16, 14)
        btn_down.setStyleSheet(BUTTON_ARROW_STYLE)
        btn_down.clicked.connect(lambda: self._on_arrow_down(spin, slider, step))
        btn_layout.addWidget(btn_down)

        row.addLayout(btn_layout)

        # 双向同步
        self._slider_spin_pairs.append((slider, spin))

        # 滑条 → 数字
        slider.valueChanged.connect(
            lambda val, s=spin: self._on_slider_changed(s, val)
        )
        # 数字 → 滑条（需屏蔽滑条信号避免死循环）
        spin.valueChanged.connect(
            lambda val, s=slider: self._on_spin_changed(s, val)
        )

        return row, slider, spin

    def _on_slider_changed(self, spin, val):
        """滑条变化 -> 更新数字框"""
        spin.blockSignals(True)
        spin.setValue(val)
        spin.blockSignals(False)
        self._on_param_changed()

    def _on_spin_changed(self, slider, val):
        """数字框变化 -> 更新滑条"""
        slider.blockSignals(True)
        slider.setValue(int(round(val)))
        slider.blockSignals(False)
        self._on_param_changed()

    def _on_arrow_up(self, spin, slider, step):
        """▲ 按钮：增加一个步长"""
        new_val = spin.value() + step
        if new_val > spin.maximum():
            new_val = spin.maximum()
        spin.blockSignals(True)
        spin.setValue(new_val)
        spin.blockSignals(False)
        # 同步滑条
        slider.blockSignals(True)
        slider.setValue(int(round(new_val)))
        slider.blockSignals(False)
        self._on_param_changed()

    def _on_arrow_down(self, spin, slider, step):
        """▼ 按钮：减少一个步长"""
        new_val = spin.value() - step
        if new_val < spin.minimum():
            new_val = spin.minimum()
        spin.blockSignals(True)
        spin.setValue(new_val)
        spin.blockSignals(False)
        # 同步滑条
        slider.blockSignals(True)
        slider.setValue(int(round(new_val)))
        slider.blockSignals(False)
        self._on_param_changed()

    # ─── UI 构建 ────────────────────────────────────────────────

    def _build_ui(self):
        """主布局：左侧参数面板 | 右侧预览区"""
        root = QHBoxLayout(self)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        # ── 左侧参数面板 ──
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumWidth(380)
        scroll.setMaximumWidth(420)
        scroll.setObjectName("sidebar")
        scroll.setStyleSheet(
            "QScrollArea { border-right: 1px solid #1E1E28; background: transparent; }"
        )

        panel = QWidget()
        self._panel_layout = QVBoxLayout(panel)
        self._panel_layout.setSpacing(12)
        self._panel_layout.setContentsMargins(16, 16, 16, 16)

        self._build_file_section(panel)
        self._build_type_section(panel)
        self._build_text_section(panel)
        self._build_image_section(panel)
        self._build_common_section(panel)
        self._build_action_section(panel)
        self._panel_layout.addStretch()

        scroll.setWidget(panel)
        root.addWidget(scroll)

        # ── 右侧预览区 ──
        preview_frame = QFrame()
        preview_frame.setObjectName("container")
        preview_layout = QVBoxLayout(preview_frame)
        preview_layout.setContentsMargins(20, 20, 20, 20)

        self._preview_header = QLabel("水印预览")
        self._preview_header.setObjectName("headingH2")
        self._preview_header.setStyleSheet(
            "color: #EAECEF; font-size: 18px; font-weight: 600; margin-bottom: 12px;"
        )
        preview_layout.addWidget(self._preview_header)

        self._preview_label = QLabel("请先选择 PDF 文件，然后点击「预览」或调整参数")
        self._preview_label.setAlignment(Qt.AlignCenter)
        self._preview_label.setMinimumSize(self.PREVIEW_WIDTH, self.PREVIEW_HEIGHT)
        self._preview_label.setStyleSheet(
            "color: #4A4B56; background-color: #14141A; border: 1px dashed #1E1E28; border-radius: 8px;"
        )
        self._preview_label.setObjectName("previewLabel")
        preview_layout.addWidget(self._preview_label, stretch=1)

        self._status_label = QLabel("")
        self._status_label.setObjectName("caption")
        preview_layout.addWidget(self._status_label)

        root.addWidget(preview_frame, stretch=1)

    # ----------------------------------------------------------------
    # i18n: 重译所有界面文字
    # ----------------------------------------------------------------
    def retranslateUi(self):
        _t = QCoreApplication.translate
        ctx = "WatermarkPage"

        # GroupBox 标题
        self._group_boxes["file"].setTitle(_t(ctx, "PDF 文件", None))
        self._group_boxes["type"].setTitle(_t(ctx, "水印类型", None))
        self._group_boxes["text"].setTitle(_t(ctx, "文字水印参数", None))
        self._group_boxes["image"].setTitle(_t(ctx, "图片水印参数", None))
        self._group_boxes["common"].setTitle(_t(ctx, "通用参数", None))
        self._group_boxes["action"].setTitle(_t(ctx, "操作", None))

        # 预览区域
        self._preview_header.setText(_t(ctx, "水印预览", None))
        self._preview_label.setText(_t(ctx, "请先选择 PDF 文件，然后点击「预览」或调整参数", None))

        # 文件选择
        self._pdf_input.setPlaceholderText(_t(ctx, "选择 PDF 文件...", None))
        self._btn_browse.setText(_t(ctx, "浏览...", None))

        # 水印类型
        # 注意：watermark_page 使用 _type_combo（ComboBox），不是 _type_radios
        # 所以重译 ComboBox 的项目即可
        self._type_combo.blockSignals(True)
        cur_type = self._type_combo.currentText()
        self._type_combo.clear()
        type_items = [_t(ctx, "文字水印", None), _t(ctx, "图片水印", None)]
        self._type_combo.addItems(type_items)
        # 尝试恢复选中项
        idx_map = {"文字水印": 0, "图片水印": 1}
        old_idx = idx_map.get(cur_type, 0)
        self._type_combo.setCurrentIndex(min(old_idx, 1))
        self._type_combo.blockSignals(False)

        # 文字水印参数
        self._lbl_text_content.setText(_t(ctx, "文字内容", None))
        self._lbl_font_size.setText(_t(ctx, "字号", None))
        self._lbl_color.setText(_t(ctx, "颜色", None))

        # 图片水印参数
        self._image_path_input.setPlaceholderText(_t(ctx, "选择水印图片...", None))
        if hasattr(self, "_btn_img"):
            self._btn_img.setText(_t(ctx, "浏览...", None))

        # 通用参数 - 滑条标签
        slider_names = [_t(ctx, "透明度", None), _t(ctx, "旋转", None),
                        _t(ctx, "缩放", None)]
        for i, lbl in enumerate(self._slider_labels[:3]):
            lbl.setText(slider_names[i])

        self._lbl_position.setText(_t(ctx, "位置", None))
        self._lbl_layer.setText(_t(ctx, "图层", None))

        # 位置 ComboBox
        pos_items = [_t(ctx, "居中", None), _t(ctx, "平铺", None),
                     _t(ctx, "左上角", None), _t(ctx, "右上角", None),
                     _t(ctx, "左下角", None), _t(ctx, "右下角", None)]
        self._position_combo.blockSignals(True)
        cur_pos = self._position_combo.currentText()
        self._position_combo.clear()
        self._position_combo.addItems(pos_items)
        self._position_combo.setCurrentText(cur_pos)
        self._position_combo.blockSignals(False)

        # 图层 ComboBox
        layer_items = [_t(ctx, "覆盖 (over)", None), _t(ctx, "底层 (under)", None)]
        self._layer_combo.blockSignals(True)
        cur_lay = self._layer_combo.currentText()
        self._layer_combo.clear()
        self._layer_combo.addItems(layer_items)
        self._layer_combo.setCurrentText(cur_lay)
        self._layer_combo.blockSignals(False)

        # 操作按钮
        self._preview_btn.setText(_t(ctx, "🔄 预览", None))
        self._export_btn.setText(_t(ctx, "📥 导出", None))

    # ── 子区域：文件选择 ──
    def _build_file_section(self, parent):
        g = QGroupBox("PDF 文件")
        self._group_boxes["file"] = g
        lay = QVBoxLayout(g)
        lay.setSpacing(6)

        row = QHBoxLayout()
        self._pdf_input = QLineEdit()
        self._pdf_input.setPlaceholderText("选择 PDF 文件...")
        self._pdf_input.setReadOnly(True)
        self._btn_browse = QPushButton("浏览...")
        self._btn_browse.setObjectName("secondaryButton")
        self._btn_browse.setProperty("cssClass", "secondary")
        self._btn_browse.clicked.connect(self._select_pdf)
        row.addWidget(self._pdf_input, stretch=1)
        row.addWidget(self._btn_browse)
        lay.addLayout(row)
        self._panel_layout.addWidget(g)

    # ── 子区域：水印类型切换 ──
    def _build_type_section(self, parent):
        g = QGroupBox("水印类型")
        self._group_boxes["type"] = g
        lay = QVBoxLayout(g)
        self._type_combo = QComboBox()
        self._type_combo.addItems(WATERMARK_TYPES)
        lay.addWidget(self._type_combo)
        self._panel_layout.addWidget(g)

    # ── 子区域：文字水印参数 ──
    def _build_text_section(self, parent):
        self._text_group = QGroupBox("文字水印参数")
        self._group_boxes["text"] = self._text_group
        lay = QVBoxLayout(self._text_group)
        lay.setSpacing(8)

        # 文字内容
        self._lbl_text_content = QLabel("文字内容")
        lay.addWidget(self._lbl_text_content)
        self._text_input = QLineEdit("印流PDflow")
        lay.addWidget(self._text_input)

        # 字号
        row_fs = QHBoxLayout()
        self._lbl_font_size = QLabel("字号")
        row_fs.addWidget(self._lbl_font_size)
        self._font_size_spin = QSpinBox()
        self._font_size_spin.setRange(12, 200)
        self._font_size_spin.setValue(48)
        self._font_size_spin.setSuffix(" pt")
        self._font_size_spin.setFixedWidth(80)
        self._font_size_spin.setStyleSheet(SPINBOX_STYLE)
        row_fs.addWidget(self._font_size_spin, stretch=1)
        lay.addLayout(row_fs)

        # 颜色
        row_color = QHBoxLayout()
        self._lbl_color = QLabel("颜色")
        row_color.addWidget(self._lbl_color)
        self._color_btn = QPushButton()
        self._color_btn.setFixedSize(32, 32)
        self._color_btn.setStyleSheet(
            f"background-color: {self._current_color}; "
            "border: 1px solid #2B3139; border-radius: 4px;"
        )
        self._color_btn.clicked.connect(self._choose_color)
        self._color_label = QLabel(self._current_color)
        self._color_label.setObjectName("monospace")
        row_color.addWidget(self._color_btn)
        row_color.addWidget(self._color_label, stretch=1)
        lay.addLayout(row_color)

        self._panel_layout.addWidget(self._text_group)

    # ── 子区域：图片水印参数 ──
    def _build_image_section(self, parent):
        self._image_group = QGroupBox("图片水印参数")
        self._group_boxes["image"] = self._image_group
        lay = QVBoxLayout(self._image_group)
        lay.setSpacing(6)

        row = QHBoxLayout()
        self._image_path_input = QLineEdit()
        self._image_path_input.setPlaceholderText("选择水印图片...")
        self._image_path_input.setReadOnly(True)
        self._btn_img = QPushButton("浏览...")
        self._btn_img.setObjectName("secondaryButton")
        self._btn_img.setProperty("cssClass", "secondary")
        self._btn_img.clicked.connect(self._select_image)
        row.addWidget(self._image_path_input, stretch=1)
        row.addWidget(self._btn_img)
        lay.addLayout(row)
        self._image_group.setVisible(False)  # 默认隐藏
        self._panel_layout.addWidget(self._image_group)

    # ── 子区域：通用参数（滑条 + 数字输入组合） ──
    def _build_common_section(self, parent):
        g = QGroupBox("通用参数")
        self._group_boxes["common"] = g
        lay = QVBoxLayout(g)
        lay.setSpacing(10)

        # ── 透明度（0-100%，步长5） ──
        row_op, slider_op, spin_op = self._make_slider_spin_row(
            "透明度", 1, 100, 30, "%", step=5
        )
        self._opacity_slider = slider_op
        self._opacity_spin = spin_op
        lay.addLayout(row_op)

        # ── 旋转角度（-180° ~ 180°，步长1） ──
        row_rot, slider_rot, spin_rot = self._make_slider_spin_row(
            "旋转", -180, 180, -45, "°", step=1
        )
        self._rotation_slider = slider_rot
        self._rotation_spin = spin_rot
        lay.addLayout(row_rot)

        # ── 位置（下拉框） ──
        row_pos = QHBoxLayout()
        self._lbl_position = QLabel("位置")
        row_pos.addWidget(self._lbl_position)
        self._position_combo = QComboBox()
        self._position_combo.setStyleSheet(COMBOBOX_STYLE)
        self._position_combo.setMaxVisibleItems(10)
        self._position_combo.addItems(POSITION_OPTIONS)
        row_pos.addWidget(self._position_combo, stretch=1)
        lay.addLayout(row_pos)

        # ── 缩放（1-200%，步长5） ──
        row_sc, slider_sc, spin_sc = self._make_slider_spin_row(
            "缩放", 1, 200, 30, "%", step=5
        )
        self._scale_slider = slider_sc
        self._scale_spin = spin_sc
        lay.addLayout(row_sc)

        # ── 图层 ──
        row_lay = QHBoxLayout()
        self._lbl_layer = QLabel("图层")
        row_lay.addWidget(self._lbl_layer)
        self._layer_combo = QComboBox()
        self._layer_combo.setStyleSheet(COMBOBOX_STYLE)
        self._layer_combo.setMaxVisibleItems(10)
        self._layer_combo.addItems(LAYER_OPTIONS)
        row_lay.addWidget(self._layer_combo, stretch=1)
        lay.addLayout(row_lay)

        self._panel_layout.addWidget(g)

    # ── 子区域：操作按钮 ──
    def _build_action_section(self, parent):
        g = QGroupBox("操作")
        self._group_boxes["action"] = g
        lay = QHBoxLayout(g)
        lay.setSpacing(12)

        self._preview_btn = QPushButton("🔄 预览")
        self._preview_btn.setObjectName("primaryButton")
        self._preview_btn.setProperty("cssClass", "primary")
        self._preview_btn.clicked.connect(self._on_preview_click)

        self._export_btn = QPushButton("📥 导出")
        self._export_btn.setObjectName("secondaryButton")
        self._export_btn.setProperty("cssClass", "secondary")
        self._export_btn.clicked.connect(self._on_export_click)

        lay.addWidget(self._preview_btn)
        lay.addWidget(self._export_btn)
        self._panel_layout.addWidget(g)

    # ─── 信号绑定 ────────────────────────────────────────────────

    def _connect_signals(self):
        """所有参数变更触发防抖预览（滑条/输入框已经在 _make_slider_spin_row 中连接了）"""
        self._type_combo.currentIndexChanged.connect(self._on_type_changed)
        self._type_combo.currentIndexChanged.connect(self._on_param_changed)
        self._text_input.textChanged.connect(self._on_param_changed)
        self._font_size_spin.valueChanged.connect(self._on_param_changed)
        self._position_combo.currentIndexChanged.connect(self._on_param_changed)
        self._layer_combo.currentIndexChanged.connect(self._on_param_changed)
        self._image_path_input.textChanged.connect(self._on_param_changed)

    # ─── 槽函数 ──────────────────────────────────────────────────

    def _select_pdf(self):
        _t = QCoreApplication.translate
        path, _ = QFileDialog.getOpenFileName(
            self, _t("WatermarkPage", "选择 PDF 文件", None), "",
            _t("WatermarkPage", "PDF 文件 (*.pdf)", None)
        )
        if path:
            self._pdf_path = path
            self._pdf_input.setText(path)
            add_record(path, "watermark")
            self._do_preview()

    def _select_image(self):
        _t = QCoreApplication.translate
        path, _ = QFileDialog.getOpenFileName(
            self, _t("WatermarkPage", "选择水印图片", None), "",
            _t("WatermarkPage", "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif)", None)
        )
        if path:
            self._image_path_input.setText(path)

    def _choose_color(self):
        _t = QCoreApplication.translate
        qcolor = QColorDialog.getColor(QColor(self._current_color), self, _t("WatermarkPage", "选择水印颜色", None))
        if qcolor.isValid():
            self._current_color = qcolor.name()
            self._color_btn.setStyleSheet(
                f"background-color: {self._current_color}; "
                "border: 1px solid #2B3139; border-radius: 4px;"
            )
            self._color_label.setText(self._current_color)
            self._on_param_changed()

    def _on_type_changed(self):
        is_text = self._type_combo.currentText() == "文字水印"
        self._text_group.setVisible(is_text)
        self._image_group.setVisible(not is_text)

    def _on_param_changed(self):
        """防抖：停止上一次计时，重新开始"""
        self._preview_timer.stop()
        self._preview_timer.start()

    def _on_preview_click(self):
        """手动预览按钮直接触发，不防抖"""
        self._preview_timer.stop()
        self._do_preview()

    # ─── 核心逻辑 ────────────────────────────────────────────────

    def _collect_params(self):
        """收集当前界面参数，转换为后端需要的格式。

        注意：
        - opacity 以 0-100（百分比）形式返回
        - 预览路径 generate_watermark_preview 内部设置 opacity_is_0_100=True，自动 ÷100
        - 导出路径在 _on_export_click 中手动 ÷100（因为 do_watermark → add_watermark
          使用 opacity_is_0_100=False，期望 0-1 浮点数）
        """
        wm_type = "image" if self._type_combo.currentText() == "图片水印" else "text"
        return {
            "watermark_type": wm_type,
            "text": self._text_input.text(),
            "font_size": self._font_size_spin.value(),
            "color": self._current_color,
            # opacity 以 0-100（百分比）传出，预览函数会自动 ÷100
            "opacity": self._opacity_spin.value(),
            "rotation": self._rotation_spin.value(),
            "position": POSITION_MAP.get(self._position_combo.currentText(), "center"),
            "layer": LAYER_MAP.get(self._layer_combo.currentText(), "over"),
            "image_path": self._image_path_input.text(),
            "scale": self._scale_spin.value(),
        }

    def _do_preview(self):
        """生成水印预览"""
        if not self._pdf_path or not os.path.exists(self._pdf_path):
            self._status_label.setText("⚠️ 请先选择 PDF 文件")
            return

        params = self._collect_params()
        self._status_label.setText("⏳ 生成预览中...")
        self._preview_label.setText("⏳ 正在渲染...")

        # 请求全分辨率（不经过 PIL 缩放），避免双重缩放导致模糊
        self._preview_worker = PreviewWorker(
            self._pdf_path, params, target_width=None
        )
        self._preview_worker.finished.connect(self._on_preview_done)
        self._preview_worker.start()

    def _on_preview_done(self, result):
        """预览线程完成回调（V1.1-RC3 优化：优先用 QImage 路径，跳过 base64）"""
        if not result.get("success"):
            self._status_label.setText(
                f"❌ 预览失败: {result.get('error', '未知错误')}"
            )
            self._preview_label.setText("预览失败，请检查参数")
            return

        # V1.1-RC3 优先路径：QImage 直接转 QPixmap（0 编码开销，~0ms）
        qimg = result.get("qimage")
        if qimg is not None and not qimg.isNull():
            pixmap = QPixmap.fromImage(qimg)
        else:
            # 兜底路径：base64 → 解码（~30ms）
            b64_data = result.get("preview", "")
            if not b64_data:
                self._status_label.setText("❌ 预览数据为空")
                return
            if "," in b64_data:
                b64_data = b64_data.split(",", 1)[1]
            img_bytes = base64.b64decode(b64_data)
            pixmap = QPixmap()
            pixmap.loadFromData(img_bytes, "PNG")
            if pixmap.isNull():
                self._status_label.setText("❌ 图片解码失败")
                return

        # V1.1-RC3: HiDPI 屏 DPR 感知缩放（修复双重缩放导致模糊）
        # 源图是全分辨率（如 1190×1684），需要在物理像素层面缩放到
        # 标签逻辑尺寸 × DPR，然后设置 DPR 让 Qt 正确映射回逻辑像素
        app = QApplication.instance()
        dpr = min(app.devicePixelRatio() if app else 1.0, MAX_DPR)
        phys_w = int(self.PREVIEW_WIDTH * dpr)
        phys_h = int(self.PREVIEW_HEIGHT * dpr)

        scaled = pixmap.scaled(
            phys_w, phys_h,
            Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        scaled.setDevicePixelRatio(dpr)
        self._preview_label.setPixmap(scaled)
        self._preview_label.setStyleSheet(
            "background-color: #14141A; border: 1px solid #1E1E28; border-radius: 8px;"
        )
        self._status_label.setText(
            f"✅ 预览完成 ({scaled.width() // int(dpr)}×{scaled.height() // int(dpr)}px, {dpr:.0f}x DPR)"
        )

    def _on_export_click(self):
        """导出带水印的 PDF

        关键修复：
        1. opacity：UI 使用 0-100（百分比），后端期望 0-1 浮点数，÷100
        2. rotation：UI 与后端均使用角度制，直接传递
        """
        if not self._pdf_path or not os.path.exists(self._pdf_path):
            ErrorHandler.show_error_dialog(
                title="提示",
                message="请先选择 PDF 文件",
                parent_widget=self,
            )
            return

        params = self._collect_params()

        # ── 【关键修复1】将 opacity 从 0-100 转换为 0-1 ──
        raw_opacity = params["opacity"]
        params["opacity"] = raw_opacity / 100.0

        # ── rotation 直接传递（值已在后端 _draw_text_watermark 中通过 morph 旋转矩阵处理）──
        print(f"[水印导出] 界面旋转值: {params['rotation']}, 实际传入值: {params['rotation']}")
        print(f"[水印导出] 透明度（原始）: {raw_opacity}%")
        print(f"[水印导出] 透明度（归一化）: {params['opacity']:.4f}")
        print(f"[水印导出] 颜色: {params['color']}")
        print(f"[水印导出] 位置: {params['position']}")
        # ─────────────────────────────────────────────────

        default_name = f"水印_{os.path.basename(self._pdf_path)}"
        default_dir = os.path.dirname(self._pdf_path)
        output_path, _ = QFileDialog.getSaveFileName(
            self, "保存带水印的 PDF",
            os.path.join(default_dir, default_name),
            "PDF 文件 (*.pdf)"
        )
        if not output_path:
            return

        self._export_btn.setEnabled(False)
        self._export_btn.setText("⏳ 导出中...")
        self._status_label.setText("⏳ 正在添加水印...")

        self._export_worker = ExportWorker(self._pdf_path, output_path, params)
        self._export_worker.finished.connect(self._on_export_done)
        self._export_worker.start()

    def _on_export_done(self, result):
        """导出线程完成回调"""
        self._export_btn.setEnabled(True)
        self._export_btn.setText("📥 导出")

        if result.get("success"):
            output_path = result.get("output_path", "")
            self._status_label.setText(f"✅ 导出成功: {output_path}")
            # 记录到最近使用
            if self._pdf_path and output_path:
                add_record(self._pdf_path, "watermark", output_path)
            QMessageBox.information(
                self, "导出成功",
                f"水印已添加到 PDF\n\n保存位置:\n{output_path}"
            )
        else:
            err = result.get("error", "未知错误")
            self._status_label.setText(f"❌ 导出失败: {err}")
            ErrorHandler.handle_pdf_error(
                Exception(err),
                parent_widget=self,
            )

    # ─── 主题应用 ────────────────────────────────────────────────

    def apply_theme(self, colors):
        """应用主题颜色到所有控件样式

        colors 字典包含以下令牌:
            bg, card_bg, border_light, text_main, text_sub, text_muted,
            primary, primary_hover, input_bg, hover_bg, active_bg
        """
        # ── 样式常量（使用 colors 令牌重构） ──
        slider_style = f"""
        QSlider::groove:horizontal {{
            background: {colors['border_light']};
            border: none;
            border-radius: 3px;
            height: 6px;
        }}
        QSlider::sub-page:horizontal {{
            background: {colors['primary']};
            border: none;
            border-radius: 3px;
            height: 6px;
        }}
        QSlider::handle:horizontal {{
            background: {colors['text_main']};
            border: none;
            border-radius: 7px;
            width: 14px;
            height: 14px;
            margin: -4px 0;
        }}
        QSlider::handle:horizontal:hover {{
            background: {colors['text_main']};
        }}
        """

        doublespin_style = f"""
        QDoubleSpinBox {{
            background-color: {colors['input_bg']};
            border: 1px solid {colors['border_light']};
            border-radius: 6px;
            color: {colors['text_main']};
            padding: 4px 8px;
            min-height: 32px;
            max-width: 100px;
        }}
        """

        combobox_style = f"""
        QComboBox {{
            background-color: {colors['input_bg']};
            border: 1px solid {colors['border_light']};
            border-radius: 6px;
            color: {colors['text_main']};
            font-size: 14px;
            padding: 4px 8px;
            min-height: 32px;
        }}
        QComboBox:focus {{
            border: 1px solid {colors['primary']};
        }}
        QComboBox::drop-down {{
            subcontrol-origin: border;
            subcontrol-position: top right;
            width: 24px;
            border: none;
            border-top-right-radius: 6px;
            border-bottom-right-radius: 6px;
        }}
        QComboBox::down-arrow {{
            image: none;
            width: 0;
            height: 0;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 6px solid {colors['text_sub']};
        }}
        QComboBox QAbstractItemView {{
            background-color: {colors['card_bg']};
            border: 1px solid {colors['border_light']};
            border-radius: 4px;
            outline: none;
            padding: 2px;
        }}
        QComboBox QAbstractItemView::item {{
            color: {colors['text_main']};
            background-color: transparent;
            padding: 6px 8px;
            border: none;
            min-height: 28px;
        }}
        QComboBox QAbstractItemView::item:hover,
        QComboBox QAbstractItemView::item:selected {{
            background-color: {colors['primary']};
            color: #FFFFFF;
            border: none;
            border-radius: 3px;
        }}
        """

        button_arrow_style = f"""
        QPushButton {{
            background-color: {colors['card_bg']};
            border: none;
            border-radius: 2px;
            color: {colors['text_sub']};
            font-size: 8px;
            width: 16px;
            height: 14px;
            padding: 0;
            margin: 0;
        }}
        QPushButton:hover {{
            background-color: {colors['border_light']};
        }}
        QPushButton:pressed {{
            background-color: {colors['active_bg']};
        }}
        """

        spinbox_style = f"""
        QSpinBox {{
            background-color: {colors['input_bg']};
            border: 1px solid {colors['border_light']};
            border-radius: 4px;
            color: {colors['text_main']};
            padding: 0 6px;
            min-height: 32px;
            font-size: 13px;
        }}
        QSpinBox:focus {{
            border: 1px solid {colors['primary']};
        }}
        QSpinBox::up-button, QSpinBox::down-button {{
            width: 20px;
            border: none;
            background: transparent;
        }}
        QSpinBox::up-arrow {{
            width: 0; height: 0;
            border: 4px solid transparent;
            border-bottom-color: {colors['text_sub']};
            margin-top: 4px;
        }}
        QSpinBox::down-arrow {{
            width: 0; height: 0;
            border: 4px solid transparent;
            border-top-color: {colors['text_sub']};
            margin-bottom: 4px;
        }}
        """

        # ── 1. 更新所有滑条样式 (SLIDER_STYLE) ──
        for slider, _ in self._slider_spin_pairs:
            slider.setStyleSheet(slider_style)

        # ── 2. 更新所有数字输入框样式 (DOUBLESPIN_STYLE) ──
        for _, spin in self._slider_spin_pairs:
            spin.setStyleSheet(doublespin_style)

        # ── 3. 更新下拉框样式 (COMBOBOX_STYLE) ──
        self._type_combo.setStyleSheet(combobox_style)
        self._position_combo.setStyleSheet(combobox_style)
        self._layer_combo.setStyleSheet(combobox_style)

        # ── 4. 更新箭头按钮样式 (BUTTON_ARROW_STYLE) ──
        for btn in self.findChildren(QPushButton):
            if btn.text() in ("\u25B2", "\u25BC"):
                btn.setStyleSheet(button_arrow_style)

        # ── 5. 字号数字框样式 (SPINBOX_STYLE) ──
        self._font_size_spin.setStyleSheet(spinbox_style)

        # ── 6. 滚动区域侧边栏边框 ──
        sidebar = self.findChild(QScrollArea, "sidebar")
        if sidebar is not None:
            sidebar.setStyleSheet(
                f"QScrollArea {{ border-right: 1px solid {colors['border_light']}; background: transparent; }}"
            )

        # ── 7. 预览标签（边框 + 占位文字色 + 背景） ──
        self._preview_label.setStyleSheet(
            f"color: {colors['text_muted']}; background-color: {colors['input_bg']}; border: 1px dashed {colors['border_light']}; border-radius: 8px;"
        )

        # ── 7b. 预览容器底色（透明，避免背景框干扰小标题文字） ──
        preview_container = self.findChild(QFrame, "container")
        if preview_container:
            preview_container.setStyleSheet(
                f"QFrame#container {{\n"
                f"    background-color: transparent;\n"
                f"    border: none;\n"
                f"    border-radius: 8px;\n"
                f"    padding: 16px;\n"
                f"}}"
            )

        # ── 8. 状态标签 ──
        self._status_label.setStyleSheet(f"color: {colors['text_sub']};")

        # ── 9. 预览标题 ──
        self._preview_header.setStyleSheet(
            f"color: {colors['text_main']}; font-size: 18px; font-weight: 600; margin-bottom: 12px;"
        )

        # ── 10. 颜色按钮边框 ──
        self._color_btn.setStyleSheet(
            f"background-color: {self._current_color}; "
            f"border: 1px solid {colors['border_light']}; border-radius: 4px;"
        )

        # ── 11. 颜色标签文字色 ──
        self._color_label.setStyleSheet(f"color: {colors['text_main']};")

        # ── 12-14. 输入框样式 ──
        input_style = f"""
        QLineEdit {{
            background-color: {colors['input_bg']};
            border: 1px solid {colors['border_light']};
            border-radius: 6px;
            color: {colors['text_main']};
            padding: 4px 8px;
            min-height: 32px;
        }}
        """
        readonly_input_style = f"""
        QLineEdit {{
            background-color: {colors['input_bg']};
            border: 1px solid {colors['border_light']};
            border-radius: 6px;
            color: {colors['text_muted']};
            padding: 4px 8px;
            min-height: 32px;
        }}
        """
        self._text_input.setStyleSheet(input_style)
        self._pdf_input.setStyleSheet(readonly_input_style)
        self._image_path_input.setStyleSheet(readonly_input_style)

        # ── 16-17. 次要按钮（浏览...） ──
        secondary_btn_style = f"""
        QPushButton {{
            background-color: transparent;
            border: 1px solid {colors['primary']};
            border-radius: 8px;
            color: {colors['primary']};
            padding: 6px 16px;
            min-height: 36px;
        }}
        QPushButton:hover {{
            background-color: rgba(77, 124, 254, 0.1);
        }}
        """
        self._btn_browse.setStyleSheet(secondary_btn_style)
        self._btn_img.setStyleSheet(secondary_btn_style)

        # ── 18. 分组框 ──
        groupbox_style = f"""
        QGroupBox {{
            border: 1px solid {colors['border_light']};
            border-radius: 8px;
            margin-top: 20px;
            padding: 20px 16px 16px 16px;
            font-size: 14px;
            font-weight: 600;
            color: {colors['text_main']};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 8px;
            background-color: transparent;
            color: {colors['text_main']};
        }}
        """
        for gb in self._group_boxes.values():
            gb.setStyleSheet(groupbox_style)

        # ── 19. 主要按钮（预览） ──
        primary_btn_style = f"""
        QPushButton {{
            background-color: {colors['primary']};
            border: none;
            border-radius: 8px;
            color: #FFFFFF;
            padding: 6px 16px;
            min-height: 36px;
        }}
        QPushButton:hover {{
            background-color: {colors['primary_hover']};
        }}
        QPushButton:disabled {{
            background-color: rgba(77, 124, 254, 0.4);
        }}
        """
        self._preview_btn.setStyleSheet(primary_btn_style)

        # ── 20. 次要按钮（导出） ──
        self._export_btn.setStyleSheet(secondary_btn_style)

        # ── 22-23. 标签文字（次文字色） ──
        sub_label_style = f"color: {colors['text_sub']};"
        self._lbl_text_content.setStyleSheet(sub_label_style)
        self._lbl_font_size.setStyleSheet(sub_label_style)
        self._lbl_color.setStyleSheet(sub_label_style)
        self._lbl_position.setStyleSheet(sub_label_style)
        self._lbl_layer.setStyleSheet(sub_label_style)

        # ── 滑条标签（次文字色） ──
        for lbl in self._slider_labels:
            lbl.setStyleSheet(sub_label_style)
