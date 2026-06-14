"""
speedwrite_page.py - 速文创作页面（PySide6 版）
UI 由 pyside6-uic 从 speedwrite_page.ui 编译而来
"""
import os
import re
import zipfile

try:
    from defusedxml.ElementTree import fromstring as _safe_fromstring
except ImportError:
    from xml.etree import ElementTree as ET
    def _safe_fromstring(data):
        parser = ET.XMLParser(resolve_entities=False)  # nosec B314
        return ET.fromstring(data, parser=parser)      # nosec B314

from PySide6.QtWidgets import (
    QWidget, QListWidgetItem, QColorDialog, QHBoxLayout, QVBoxLayout, QLabel,
    QLineEdit, QMenu, QSizePolicy, QMessageBox
)
from PySide6.QtGui import QTextCursor, QTextCharFormat, QFont, QColor, QTextDocument, QTextBlockFormat, QPalette, QTextListFormat, QFontDatabase
from PySide6.QtCore import QTimer, Qt, QSize, QPoint
from .Ui_speedwrite_page import Ui_SpeedwritePage
from .ai_dialogs import AiFeatureDialog, AiSettingsDialog


class SpeedwritePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # 加载 UI
        self.ui = Ui_SpeedwritePage()
        self.ui.setupUi(self)

        # 保存 .ui 文件原始样式表（用于 apply_theme 中重建完整 QSS）
        self._base_stylesheet = self.styleSheet()

        self._current_font_size = 14
        self._current_font_family = "Microsoft YaHei"
        self._current_line_spacing = 1.8

        # 章节数据：{章节名: 内容}
        self._chapters = {}
        self._current_chapter = None

        # 任务列表：存储所有打开/创建的创作任务
        self._tasks = []  # [(task_name, chapters_dict, current_chapter), ...]
        self._current_task_index = -1

        # 是否在输入模式
        self._is_input_mode = False

        # 显示右侧编辑区顶部标题，显示当前章节名和进度
        self.ui.pageTitle.setVisible(True)
        self.ui.pageSubtitle.setVisible(True)
        self.ui.pageTitle.setText("章节：")
        self.ui.pageSubtitle.setText("暂无章节")

        # 在 fontCombo 和 sizeCombo 前插入独立标题标签
        self._insert_combo_label(self.ui.fontCombo, "字体")
        self._insert_combo_label(self.ui.sizeCombo, "字号")

        # 修复所有下拉框视图：强制使用系统字体渲染列表项
        # fontCombo 的字体名本身用对应字体渲染，某些字体无中文字形会导致中文名不可见
        self.ui.fontCombo.view().setFont(QFont("Microsoft YaHei", 11))
        self.ui.sizeCombo.view().setFont(QFont("Microsoft YaHei", 11))
        self.ui.lineSpacingCombo.view().setFont(QFont("Microsoft YaHei", 11))
        self.ui.bgThemeCombo.view().setFont(QFont("Microsoft YaHei", 11))
        self.ui.exportCombo.view().setFont(QFont("Microsoft YaHei", 11))

        # 设置编辑器默认样式（灰黑底色，不随主题变化）
        self.ui.editorTextEdit.setStyleSheet("""
            QTextEdit {
                background-color: #1A1E26;
                color: #C8CCD0;
                border: 1px solid rgba(255,255,255,0.04);
                border-radius: 12px;
                font-size: 15px;
                padding: 28px;
                selection-background-color: #4D7CFE;
                selection-color: #FFFFFF;
            }
            QTextEdit QScrollBar:vertical {
                background-color: transparent; width: 6px;
            }
            QTextEdit QScrollBar::handle:vertical {
                background-color: rgba(255,255,255,0.15);
                border-radius: 3px; min-height: 40px;
            }
        """)

        # 设置编辑器占位符颜色（QPalette 方式，QSS ::placeholder 不可靠）
        palette = self.ui.editorTextEdit.palette()
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("#848E9C"))
        self.ui.editorTextEdit.setPalette(palette)

        self._init_left_panel_header()
        self._init_chapters()
        self._apply_editor_font()
        self._connect_signals()
        self._start_auto_save_timer()
        self._update_header_chapter_info()

        # 手机预览按钮加上图标
        self.ui.btnMobilePreview.setText("📱 手机预览")

        # 往字体下拉框添加主流的英文字体（仅在系统存在时添加）
        fd = QFontDatabase()
        available_fonts = set(fd.families(QFontDatabase.WritingSystem.Latin))
        english_fonts = [
            "Arial", "Helvetica", "Times New Roman", "Georgia", "Verdana",
            "Courier New", "Impact", "Trebuchet MS", "Tahoma", "Century Gothic",
            "Calibri", "Cambria", "Consolas", "Segoe UI", "Palatino Linotype"
        ]
        for ef in english_fonts:
            if ef in available_fonts:
                self.ui.fontCombo.addItem(ef)

    def _insert_combo_label(self, combo_widget, text):
        layout = combo_widget.parent().layout()
        if layout is None:
            return
        idx = layout.indexOf(combo_widget)
        if idx < 0:
            return
        label = QLabel(text)
        label.setObjectName("comboLabel")
        label.setStyleSheet(
            "font-size: 12px; background: transparent; border: none; padding-right: 2px;"
        )
        layout.insertWidget(idx, label)

    # ── 左侧面板顶部大标题 ──
    def _init_left_panel_header(self):
        """在左侧面板顶部添加速文创作大标题和描述，并重绘AI功能按钮"""
        # 创建标题容器（高度与右侧 headerFrame 对齐：64px）
        header_widget = QWidget()
        header_widget.setFixedHeight(64)
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(2)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # 大标题
        title_label = QLabel("速文创作")
        title_label.setStyleSheet("""
            color: #EAECEF;
            font-size: 24px;
            font-weight: 700;
            background: transparent;
        """)
        header_layout.addWidget(title_label)

        # 描述
        desc_label = QLabel("AI 辅助网文写作工具，舒适排版 + AI 大纲生成")
        desc_label.setStyleSheet("""
            color: #848E9C;
            font-size: 12px;
            font-weight: 400;
            background: transparent;
        """)
        header_layout.addWidget(desc_label)

        # 插入到 leftInnerLayout 的最顶部
        self.ui.leftInnerLayout.insertWidget(0, header_widget)

        # 重绘 AI 功能按钮为图标+文字两列布局
        self._redraw_ai_button(self.ui.btnGenOutline, "📋", "生成大纲", "输入题材 / 设定自动生成")
        self._redraw_ai_button(self.ui.btnWorldBuild, "🏛️", "世界观构建", "势力 · 地图 · 力量体系")
        self._redraw_ai_button(self.ui.btnCharacter, "👤", "角色卡", "人物档案 + 关系网")
        self._redraw_ai_button(self.ui.btnContinueWrite, "✍️", "智能续写", "基于上文自动续写")
        self._redraw_ai_button(self.ui.btnPolish, "✨", "润色优化", "提升文笔流畅度")
        self._redraw_ai_button(self.ui.btnDialogue, "💬", "对话生成", "角色风格化对话")

    def _redraw_ai_button(self, button, icon_text, title, desc):
        """将按钮重绘为图标+文字两列布局（图标与文字垂直居中）"""
        button.setText("")
        button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 8px;
                padding: 0;
                text-align: left;
            }
            QPushButton:hover {
                background-color: rgba(255,255,255,0.04);
            }
        """)

        # 用 QVBoxLayout 撑开按钮高度，使内容垂直居中
        outer_layout = QVBoxLayout(button)
        outer_layout.setContentsMargins(12, 0, 12, 0)
        outer_layout.setSpacing(0)

        # 上弹性空间
        outer_layout.addStretch(1)

        # 水平内容行：图标 + 文字
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(12)

        # 左侧图标背景
        icon_bg = QLabel(icon_text)
        icon_bg.setFixedSize(36, 36)
        icon_bg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_bg.setStyleSheet("""
            background-color: rgba(77,124,254,0.12);
            border-radius: 8px;
            font-size: 16px;
            color: #4D7CFE;
        """)
        row_layout.addWidget(icon_bg)

        # 右侧文字区域
        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(2)

        title_label = QLabel(title)
        title_label.setStyleSheet("color: #EAECEF; font-size: 14px; font-weight: 500; background: transparent;")
        text_layout.addWidget(title_label)

        desc_label = QLabel(desc)
        desc_label.setStyleSheet("color: #848E9C; font-size: 11px; font-weight: 400; background: transparent;")
        text_layout.addWidget(desc_label)

        row_layout.addLayout(text_layout)
        row_layout.addStretch()

        outer_layout.addLayout(row_layout)

        # 下弹性空间
        outer_layout.addStretch(1)

        button.setMinimumHeight(56)

    # ── 章节初始化 ──
    def _init_chapters(self):
        """初始化：不添加默认章节，只显示新建章节按钮"""
        self._update_chapter_button_visibility()

    # ── 编辑器样式 ──
    def _apply_editor_font(self):
        editor = self.ui.editorTextEdit
        font = QFont(self._current_font_family, self._current_font_size)
        editor.setFont(font)
        # 用 QTextCharFormat 设置字体（作用于选中文本或后续输入）
        char_fmt = QTextCharFormat()
        char_fmt.setFont(font)
        cursor = editor.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        cursor.mergeCharFormat(char_fmt)
        # 设置行距
        block_fmt = QTextBlockFormat()
        spacing_map = {1.5: 3, 1.8: 6, 2.0: 10}
        margin_px = spacing_map.get(self._current_line_spacing, 4)
        block_fmt.setTopMargin(margin_px)
        block_fmt.setBottomMargin(margin_px)
        cursor.mergeBlockFormat(block_fmt)

    # ── 信号连接 ──
    def _connect_signals(self):
        editor = self.ui.editorTextEdit
        editor.textChanged.connect(self._update_word_count)
        self.ui.sizeCombo.currentTextChanged.connect(self._on_size_changed)
        self.ui.fontCombo.currentTextChanged.connect(self._on_font_changed)
        self.ui.lineSpacingCombo.currentTextChanged.connect(self._on_line_spacing_changed)

        # 格式按钮
        self.ui.btnBold.clicked.connect(self._toggle_bold)
        self.ui.btnItalic.clicked.connect(self._toggle_italic)
        self.ui.btnUnderline.clicked.connect(self._toggle_underline)
        self.ui.btnStrike.clicked.connect(self._toggle_strike)

        # 颜色按钮
        self.ui.btnTextColor.clicked.connect(self._pick_text_color)
        self.ui.btnBgColor.clicked.connect(self._pick_bg_color)

        # 对齐按钮
        self.ui.btnAlignLeft.clicked.connect(self._align_left)
        self.ui.btnAlignCenter.clicked.connect(self._align_center)
        self.ui.btnAlignRight.clicked.connect(self._align_right)
        self.ui.btnAlignJustify.clicked.connect(self._align_justify)

        # 列表
        self.ui.btnList.clicked.connect(self._toggle_bullet_list)
        self.ui.btnOrderedList.clicked.connect(self._toggle_ordered_list)

        # 缩进
        self.ui.btnOutdent.clicked.connect(self._decrease_indent)
        self.ui.btnIndent.clicked.connect(self._increase_indent)

        # 撤销/重做
        self.ui.btnUndo.clicked.connect(editor.undo)
        self.ui.btnRedo.clicked.connect(editor.redo)

        # 背景选择
        self.ui.bgThemeCombo.currentIndexChanged.connect(self._on_bg_theme_changed)

        # 导出（使用 activated 信号，即使选择同一项也会触发）
        self.ui.exportCombo.activated.connect(self._on_export_combo_activated)

        # 手机预览
        self.ui.btnMobilePreview.clicked.connect(self._toggle_mobile_preview)

        # 打开文件
        self.ui.btnOpenFile.clicked.connect(self._on_open_file)
        # 新建任务
        self.ui.btnNewTask.clicked.connect(self._on_new_task)

        # 新建章节（只用大按钮）
        self.ui.btnNewChapterBig.clicked.connect(self._on_new_chapter)
        # 隐藏标题栏的小加号按钮
        self.ui.btnNewChapter.setVisible(False)

        # ── AI 功能按钮 ──
        self.ui.btnGenOutline.clicked.connect(lambda: self._open_ai_dialog("gen_outline"))
        self.ui.btnWorldBuild.clicked.connect(lambda: self._open_ai_dialog("world_build"))
        self.ui.btnCharacter.clicked.connect(lambda: self._open_ai_dialog("character"))
        self.ui.btnContinueWrite.clicked.connect(lambda: self._open_ai_dialog("continue_write"))
        self.ui.btnPolish.clicked.connect(lambda: self._open_ai_dialog("polish"))
        self.ui.btnDialogue.clicked.connect(lambda: self._open_ai_dialog("dialogue"))

        # 章节切换
        self.ui.chapterList.currentRowChanged.connect(self._on_chapter_changed)

        # 底部状态栏文档名点击 → 切换任务
        self.ui.statusDocName.setCursor(Qt.CursorShape.PointingHandCursor)
        self.ui.statusDocName.mousePressEvent = lambda event: self._on_status_doc_name_clicked()

        # 快捷键
        from PySide6.QtGui import QKeySequence, QShortcut
        QShortcut(QKeySequence("Ctrl+B"), self, self.ui.btnBold.click)
        QShortcut(QKeySequence("Ctrl+I"), self, self.ui.btnItalic.click)
        QShortcut(QKeySequence("Ctrl+U"), self, self.ui.btnUnderline.click)
        QShortcut(QKeySequence("Ctrl+S"), self, self._manual_save)
        QShortcut(QKeySequence("Ctrl+Z"), self, editor.undo)
        QShortcut(QKeySequence("Ctrl+Shift+Z"), self, editor.redo)

    # ── 字数统计 ──
    def _update_word_count(self):
        text = self.ui.editorTextEdit.toPlainText()
        length = len(text)
        pages = max(1, length // 1500) if length > 0 else 0
        self.ui.statusWordCount.setText(f'<span style="color:#4D7CFE;font-weight:600;">{length}</span> 字')
        self.ui.statusPageCount.setText(f'约 <span style="font-weight:600;">{pages}</span> 页')
        self.ui.wordCountLabel.setText(f'<span style="color:#4D7CFE;font-weight:600;">{length}</span> 字 · 约 {pages} 页')

    # ── 自动保存 ──
    def _start_auto_save_timer(self):
        self._auto_save_timer = QTimer(self)
        self._auto_save_timer.setInterval(300000)  # 5 分钟
        self._auto_save_timer.timeout.connect(self._auto_save)
        self._auto_save_timer.start()

    def _auto_save(self):
        print("[速文] 自动保存...")

    def _manual_save(self):
        print("[速文] 手动保存 (Ctrl+S)")

    # ── 格式 ──
    def _toggle_bold(self):
        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Bold if self.ui.btnBold.isChecked() else QFont.Normal)
        self.ui.editorTextEdit.mergeCurrentCharFormat(fmt)

    def _toggle_italic(self):
        fmt = QTextCharFormat()
        fmt.setFontItalic(self.ui.btnItalic.isChecked())
        self.ui.editorTextEdit.mergeCurrentCharFormat(fmt)

    def _toggle_underline(self):
        fmt = QTextCharFormat()
        fmt.setFontUnderline(self.ui.btnUnderline.isChecked())
        self.ui.editorTextEdit.mergeCurrentCharFormat(fmt)

    def _toggle_strike(self):
        fmt = QTextCharFormat()
        fmt.setFontStrikeOut(self.ui.btnStrike.isChecked())
        self.ui.editorTextEdit.mergeCurrentCharFormat(fmt)

    # ── 颜色 ──
    def _pick_text_color(self):
        color = QColorDialog.getColor(QColor("#EAECEF"), self, "选择文字颜色")
        if color.isValid():
            fmt = QTextCharFormat()
            fmt.setForeground(color)
            self.ui.editorTextEdit.mergeCurrentCharFormat(fmt)
            # 更新按钮背景色以显示所选颜色
            self.ui.btnTextColor.setStyleSheet(
                f"background-color: {color.name()}; color: #FFFFFF; "
                f"border-radius: 4px; border: 2px solid rgba(255,255,255,0.2);"
            )

    def _pick_bg_color(self):
        color = QColorDialog.getColor(QColor("#1A1A22"), self, "选择背景颜色")
        if color.isValid():
            fmt = QTextCharFormat()
            fmt.setBackground(color)
            self.ui.editorTextEdit.mergeCurrentCharFormat(fmt)
            # 更新按钮背景色以显示所选颜色
            txt_color = "#FFFFFF" if color.lightness() < 128 else "#1D1D1F"
            self.ui.btnBgColor.setStyleSheet(
                f"background-color: {color.name()}; color: {txt_color}; "
                f"border-radius: 4px; border: 2px solid rgba(255,255,255,0.2);"
            )

    # ── 对齐 ──
    def _align_left(self):
        if self.ui.btnAlignLeft.isChecked():
            self.ui.editorTextEdit.setAlignment(Qt.AlignmentFlag.AlignLeft)
            self.ui.btnAlignCenter.setChecked(False)
            self.ui.btnAlignRight.setChecked(False)
            self.ui.btnAlignJustify.setChecked(False)

    def _align_center(self):
        if self.ui.btnAlignCenter.isChecked():
            self.ui.editorTextEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.ui.btnAlignLeft.setChecked(False)
            self.ui.btnAlignRight.setChecked(False)
            self.ui.btnAlignJustify.setChecked(False)

    def _align_right(self):
        if self.ui.btnAlignRight.isChecked():
            self.ui.editorTextEdit.setAlignment(Qt.AlignmentFlag.AlignRight)
            self.ui.btnAlignLeft.setChecked(False)
            self.ui.btnAlignCenter.setChecked(False)
            self.ui.btnAlignJustify.setChecked(False)

    def _align_justify(self):
        if self.ui.btnAlignJustify.isChecked():
            self.ui.editorTextEdit.setAlignment(Qt.AlignmentFlag.AlignJustify)
            self.ui.btnAlignLeft.setChecked(False)
            self.ui.btnAlignCenter.setChecked(False)
            self.ui.btnAlignRight.setChecked(False)

    # ── 下拉框 ──
    def _on_font_changed(self, text):
        if text in ("字体",):
            return
        self._current_font_family = text
        self._apply_editor_font()

    def _on_size_changed(self, text):
        try:
            size = int(text)
        except ValueError:
            return
        self._current_font_size = size
        self._apply_editor_font()

    def _on_line_spacing_changed(self, text):
        mapping = {"舒适 1.8x": 1.8, "紧凑 1.5x": 1.5, "宽松 2.0x": 2.0}
        self._current_line_spacing = mapping.get(text, 1.8)
        self._apply_editor_font()

    # ── 背景主题 ──
    def _on_bg_theme_changed(self, index):
        editor = self.ui.editorTextEdit
        theme_map = {
            0: None,  # 背景选择 (placeholder)
            1: {"bg": "#FFFFFF", "fg": "#1A1A1A"},   # 默认
            2: {"bg": "#F5F0E1", "fg": "#2C2820"},   # 柔和护眼
            3: {"bg": "#1A1E26", "fg": "#C8CCD0"},   # 夜间沉浸
            4: {"bg": "#E8DCC8", "fg": "#3A3520"},   # 极简自然
        }
        if index == 0:
            return
        theme = theme_map.get(index)
        if theme:
            current_spacing = self._current_line_spacing
            editor.setStyleSheet(f"""
                QTextEdit {{
                    background-color: {theme['bg']};
                    color: {theme['fg']};
                    border: 1px solid rgba(255,255,255,0.04);
                    border-radius: 12px;
                    font-size: 15px;
                    padding: 28px;
                    selection-background-color: #4D7CFE;
                    selection-color: #FFFFFF;
                }}
            """)
            if index in (1, 2, 4):
                editor.setStyleSheet(editor.styleSheet() + """
                    QTextEdit QScrollBar:vertical { background-color: transparent; width: 6px; }
                    QTextEdit QScrollBar::handle:vertical { background-color: rgba(0,0,0,0.15); border-radius: 3px; min-height: 40px; }
                """)
            # 恢复占位符颜色（setStyleSheet 会重置 QPalette）
            palette = editor.palette()
            palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("#848E9C"))
            editor.setPalette(palette)
            # 重新应用行距
            self._current_line_spacing = current_spacing
            self._apply_editor_font()

    # ── 列表 ──
    def _toggle_bullet_list(self):
        cursor = self.ui.editorTextEdit.textCursor()
        if cursor.currentList():
            # 已在列表中，移除列表格式
            cursor.setBlockFormat(QTextBlockFormat())
        else:
            cursor.createList(QTextListFormat.Style.ListDisc)
        self.ui.editorTextEdit.setTextCursor(cursor)

    def _toggle_ordered_list(self):
        cursor = self.ui.editorTextEdit.textCursor()
        if cursor.currentList():
            cursor.setBlockFormat(QTextBlockFormat())
        else:
            cursor.createList(QTextListFormat.Style.ListDecimal)
        self.ui.editorTextEdit.setTextCursor(cursor)

    # ── 缩进 ──
    def _increase_indent(self):
        cursor = self.ui.editorTextEdit.textCursor()
        block_fmt = cursor.blockFormat()
        block_fmt.setIndent(block_fmt.indent() + 1)
        cursor.setBlockFormat(block_fmt)
        self.ui.editorTextEdit.setTextCursor(cursor)

    def _decrease_indent(self):
        cursor = self.ui.editorTextEdit.textCursor()
        block_fmt = cursor.blockFormat()
        if block_fmt.indent() > 0:
            block_fmt.setIndent(block_fmt.indent() - 1)
        cursor.setBlockFormat(block_fmt)
        self.ui.editorTextEdit.setTextCursor(cursor)

    # ── 导出 ──
    def _on_export_combo_activated(self, index):
        if index == 0:
            self._export_normal()
        elif index == 1:
            self._export_mobile()
        # 不重置索引，保持用户选择的文字显示

    def _export_normal(self):
        """常规导出：弹出格式选择菜单，支持网文常用格式"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1A1A22;
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 8px;
                padding: 6px;
                min-width: 160px;
            }
            QMenu::item {
                color: #EAECEF;
                padding: 10px 16px;
                border-radius: 6px;
                font-size: 13px;
            }
            QMenu::item:selected {
                background-color: rgba(77,124,254,0.15);
                color: #4D7CFE;
            }
        """)
        formats = [
            ("📄  TXT 纯文本", "txt"),
            ("📝  Markdown", "md"),
            ("📖  HTML 网页", "html"),
            ("📕  EPUB 电子书", "epub"),
        ]
        for label, fmt in formats:
            action = menu.addAction(label)
            action.triggered.connect(lambda checked, f=fmt: self._do_export(f))
        menu.exec(self.ui.exportCombo.mapToGlobal(
            self.ui.exportCombo.rect().bottomLeft()
        ))

    def _export_mobile(self):
        """手机模式导出：适合手机阅读的排版"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1A1A22;
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 8px;
                padding: 6px;
                min-width: 160px;
            }
            QMenu::item {
                color: #EAECEF;
                padding: 10px 16px;
                border-radius: 6px;
                font-size: 13px;
            }
            QMenu::item:selected {
                background-color: rgba(77,124,254,0.15);
                color: #4D7CFE;
            }
        """)
        formats = [
            ("📱  手机 TXT（自动换行）", "mobile_txt"),
            ("📱  手机 HTML（适配屏幕）", "mobile_html"),
        ]
        for label, fmt in formats:
            action = menu.addAction(label)
            action.triggered.connect(lambda checked, f=fmt: self._do_export(f))
        menu.exec(self.ui.exportCombo.mapToGlobal(
            self.ui.exportCombo.rect().bottomLeft()
        ))

    def _do_export(self, fmt):
        """执行导出操作"""
        from PySide6.QtWidgets import QFileDialog
        content = self.ui.editorTextEdit.toPlainText()
        if not content.strip():
            QMessageBox.information(self, "提示", "编辑器内容为空，无法导出")
            return

        if fmt == "txt":
            path, _ = QFileDialog.getSaveFileName(self, "导出 TXT", "", "文本文件 (*.txt)")
            if path:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"[速文] 已导出 TXT: {path}")

        elif fmt == "md":
            path, _ = QFileDialog.getSaveFileName(self, "导出 Markdown", "", "Markdown (*.md)")
            if path:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"[速文] 已导出 Markdown: {path}")

        elif fmt == "html":
            path, _ = QFileDialog.getSaveFileName(self, "导出 HTML", "", "HTML (*.html)")
            if path:
                html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>速文创作导出</title>
<style>body{{font-family:"Microsoft YaHei",sans-serif;max-width:800px;margin:0 auto;padding:40px;line-height:1.8;color:#333;}}</style>
</head><body>{''.join(f'<p>{line}</p>' for line in content.split('\n'))}</body></html>"""
                with open(path, "w", encoding="utf-8") as f:
                    f.write(html)
                print(f"[速文] 已导出 HTML: {path}")

        elif fmt == "epub":
            path, _ = QFileDialog.getSaveFileName(self, "导出 EPUB", "", "EPUB (*.epub)")
            if path:
                self._export_epub(path, content)

        elif fmt == "mobile_txt":
            path, _ = QFileDialog.getSaveFileName(self, "导出手机 TXT", "", "文本文件 (*.txt)")
            if path:
                # 手机端：每行不超过 42 字符自动换行
                lines = []
                for line in content.split('\n'):
                    while len(line) > 42:
                        lines.append(line[:42])
                        line = line[42:]
                    lines.append(line)
                with open(path, "w", encoding="utf-8") as f:
                    f.write('\n'.join(lines))
                print(f"[速文] 已导出手机 TXT: {path}")

        elif fmt == "mobile_html":
            path, _ = QFileDialog.getSaveFileName(self, "导出手机 HTML", "", "HTML (*.html)")
            if path:
                html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>速文创作导出</title>
<style>body{{font-family:"Microsoft YaHei",sans-serif;max-width:420px;margin:0 auto;padding:20px;line-height:2.0;font-size:16px;color:#333;}}</style>
</head><body>{''.join(f'<p>{line}</p>' for line in content.split('\n'))}</body></html>"""
                with open(path, "w", encoding="utf-8") as f:
                    f.write(html)
                print(f"[速文] 已导出手机 HTML: {path}")

    def _export_epub(self, path, content):
        """导出 EPUB 电子书格式（纯 Python 实现，无需外部库）"""
        import zipfile
        import uuid
        uid = str(uuid.uuid4())
        paragraphs = ''.join(f'<p>{line}</p>' for line in content.split('\n'))
        with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr('mimetype', 'application/epub+zip')
            zf.writestr('META-INF/container.xml', f"""<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles><rootfile full-path="content.opf" media-type="application/oebps-package+xml"/></rootfiles>
</container>""")
            zf.writestr('content.opf', f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">{uid}</dc:identifier>
    <dc:title>速文创作导出</dc:title>
    <dc:language>zh</dc:language>
    <meta property="dcterms:modified">2026-01-01T00:00:00Z</meta>
  </metadata>
  <manifest>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
    <item id="chap1" href="chapter1.xhtml" media-type="application/xhtml+xml"/>
    <item id="css" href="style.css" media-type="text/css"/>
  </manifest>
  <spine><itemref idref="chap1"/></spine>
</package>""")
            zf.writestr('nav.xhtml', f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head><title>速文创作导出</title></head>
<body><nav epub:type="toc"><ol><li><a href="chapter1.xhtml">正文</a></li></ol></nav></body></html>""")
            zf.writestr('style.css', 'body{font-family:sans-serif;line-height:1.8;margin:1em;}')
            zf.writestr('chapter1.xhtml', f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml">
<head><title>正文</title><link rel="stylesheet" href="style.css"/></head>
<body>{paragraphs}</body></html>""")
        print(f"[速文] 已导出 EPUB: {path}")

    # ── 手机预览 ──
    def _toggle_mobile_preview(self):
        """切换手机预览模式：编辑器宽度变窄，模拟手机屏幕"""
        if not hasattr(self, '_mobile_preview_active'):
            self._mobile_preview_active = False
        self._mobile_preview_active = not self._mobile_preview_active
        editor = self.ui.editorTextEdit
        btn = self.ui.btnMobilePreview
        if self._mobile_preview_active:
            # 保存原始宽度策略
            self._original_size_policy = editor.sizePolicy()
            editor.setMaximumWidth(420)
            # 手机预览模式：添加模拟手机边框
            editor.setStyleSheet(editor.styleSheet() + """
                QTextEdit {
                    border-left: 12px solid #2B3139;
                    border-right: 12px solid #2B3139;
                    border-top: 40px solid #2B3139;
                    border-bottom: 12px solid #2B3139;
                    border-top-left-radius: 20px;
                    border-top-right-radius: 20px;
                }
            """)
            # 激活状态：更亮的蓝色
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3D6CF0;
                    color: #FFFFFF;
                    border: 2px solid #FFFFFF;
                    border-radius: 8px;
                    font-size: 12px;
                    font-weight: 600;
                    padding: 2px 12px;
                    height: 28px;
                }
            """)
            print("[速文] 手机预览模式: 开启")
        else:
            editor.setMaximumWidth(16777215)
            editor.setSizePolicy(self._original_size_policy)
            # 重新应用主题样式（不直接用 setStyleSheet("")，否则会丢失蓝色背景）
            if hasattr(self, '_theme_colors'):
                c2 = self._theme_colors
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {c2['primary']};
                        color: #FFFFFF;
                        border: none;
                        border-radius: 6px;
                        font-size: 12px;
                        padding: 0 10px;
                        height: 28px;
                    }}
                """)
            else:
                btn.setStyleSheet("")
            # 恢复编辑器样式（从 apply_theme 重建）
            if hasattr(self, '_theme_colors'):
                c = self._theme_colors
                is_light = int(c['bg'].lstrip('#')[:2], 16) > 128
                _editor_bg = '#FFFFFF' if is_light else '#1A1E26'
                _editor_border = '1px solid #E5E5EA' if is_light else f"1px solid {c['border_light']}"
                editor.setStyleSheet(f"""
                    QTextEdit {{
                        background-color: {_editor_bg};
                        color: {c['text_main']};
                        border: {_editor_border};
                        border-radius: 12px;
                        font-size: 15px;
                        padding: 28px;
                        selection-background-color: {c['primary']};
                        selection-color: #FFFFFF;
                    }}
                    QTextEdit QScrollBar:vertical {{
                        background-color: transparent; width: 6px;
                    }}
                    QTextEdit QScrollBar::handle:vertical {{
                        background-color: {c['text_muted']};
                        border-radius: 3px; min-height: 40px;
                    }}
                """)
                palette = editor.palette()
                palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(c['text_sub']))
                editor.setPalette(palette)
            print("[速文] 手机预览模式: 关闭")

    # ═══════════════════════════════════════════════════════════════
    # 章节管理（重写）
    # ═══════════════════════════════════════════════════════════════

    def _create_chapter_item_widget(self, index, chapter_name, is_selected=False):
        """创建章节列表项的自定义 Widget（示意2风格：左侧序号 + 右侧名称）"""
        container = QWidget()
        container.setObjectName("chapterItemContainer")
        container.setFixedHeight(40)
        # 修复黑框：使用 palette 设置背景色而不是 styleSheet
        container.setAutoFillBackground(True)
        palette = container.palette()
        if is_selected:
            palette.setColor(container.backgroundRole(), QColor(77, 124, 254, 25))
        else:
            palette.setColor(container.backgroundRole(), Qt.transparent)
        container.setPalette(palette)

        layout = QHBoxLayout(container)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(16)

        # 左侧序号标签
        idx_label = QLabel(f"{index:02d}")
        idx_label.setObjectName("chapterIndexLabel")
        idx_label.setStyleSheet("color: #5A6270; font-size: 13px; font-weight: 400; background: transparent;")
        idx_label.setFixedWidth(28)
        layout.addWidget(idx_label)

        # 右侧章节名标签
        name_label = QLabel(chapter_name)
        name_label.setObjectName("chapterNameLabel")
        if is_selected:
            name_label.setStyleSheet("color: #4D7CFE; font-size: 13px; font-weight: 500; background: transparent;")
        else:
            name_label.setStyleSheet("color: #848E9C; font-size: 13px; font-weight: 400; background: transparent;")
        layout.addWidget(name_label)

        layout.addStretch()

        # 双击编辑章节名（通过查找当前 widget 所在 row 来动态确定）
        container.mouseDoubleClickEvent = lambda event, c=container: self._on_chapter_double_click(self._get_chapter_row(c))
        # 右键菜单
        container.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        container.customContextMenuRequested.connect(lambda pos, c=container: self._on_chapter_context_menu(self._get_chapter_row(c), pos))

        return container

    def _get_chapter_row(self, container_widget):
        """根据 container widget 查找其在列表中的 row"""
        for i in range(self.ui.chapterList.count()):
            item = self.ui.chapterList.item(i)
            widget = self.ui.chapterList.itemWidget(item)
            if widget is container_widget:
                return i
        return -1

    def _update_chapter_item_styles(self):
        """更新所有章节项的样式以反映选中状态"""
        for i in range(self.ui.chapterList.count()):
            item = self.ui.chapterList.item(i)
            widget = self.ui.chapterList.itemWidget(item)
            if widget is None:
                continue
            name_label = widget.findChild(QLabel, "chapterNameLabel")
            idx_label = widget.findChild(QLabel, "chapterIndexLabel")
            if name_label is None or idx_label is None:
                continue
            if i == self.ui.chapterList.currentRow():
                palette = widget.palette()
                palette.setColor(widget.backgroundRole(), QColor(77, 124, 254, 25))
                widget.setPalette(palette)
                name_label.setStyleSheet("color: #4D7CFE; font-size: 13px; font-weight: 500; background: transparent;")
                idx_label.setStyleSheet("color: #5A6270; font-size: 13px; font-weight: 400; background: transparent;")
            else:
                palette = widget.palette()
                palette.setColor(widget.backgroundRole(), Qt.transparent)
                widget.setPalette(palette)
                name_label.setStyleSheet("color: #848E9C; font-size: 13px; font-weight: 400; background: transparent;")
                idx_label.setStyleSheet("color: #5A6270; font-size: 13px; font-weight: 400; background: transparent;")

    def _on_new_chapter(self):
        """点击 + 按钮：大按钮隐藏，显示输入框"""
        if self._is_input_mode:
            return
        self._is_input_mode = True
        self.ui.btnNewChapterBig.setVisible(False)
        self._show_chapter_input()

    def _show_chapter_input(self):
        """在列表底部显示章节名称输入框"""
        # 创建输入框容器
        container = QWidget()
        container.setObjectName("chapterInputContainer")
        container.setFixedHeight(44)
        container.setStyleSheet("""
            QWidget#chapterInputContainer {
                background-color: rgba(30, 35, 41, 0.6);
                border: 1px solid #4D7CFE;
                border-radius: 10px;
            }
        """)

        layout = QHBoxLayout(container)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(0)

        # 输入框
        line_edit = QLineEdit()
        line_edit.setObjectName("chapterNameInput")
        line_edit.setPlaceholderText("输入章节名称，按回车确认...")
        line_edit.setStyleSheet("""
            QLineEdit {
                background-color: transparent;
                color: #EAECEF;
                border: none;
                font-size: 13px;
                padding: 0;
            }
        """)
        line_edit.returnPressed.connect(lambda: self._on_input_confirmed(line_edit))
        line_edit.installEventFilter(self)
        layout.addWidget(line_edit)

        # 添加到列表末尾
        item = QListWidgetItem()
        item.setSizeHint(QSize(0, 48))
        self.ui.chapterList.addItem(item)
        self.ui.chapterList.setItemWidget(item, container)

        # 聚焦输入框
        line_edit.setFocus()

    def _on_input_confirmed(self, line_edit):
        """输入框按回车确认"""
        name = line_edit.text().strip()
        if not name:
            # 空名称，取消输入
            self._cancel_input()
            return

        # 保存当前章节内容
        if self._current_chapter:
            self._chapters[self._current_chapter] = self.ui.editorTextEdit.toPlainText()

        # 检查是否重名
        if name in self._chapters:
            # 如果重名，添加序号后缀
            base_name = name
            counter = 2
            while name in self._chapters:
                name = f"{base_name} ({counter})"
                counter += 1

        # 删除输入框 item
        last_item = self.ui.chapterList.item(self.ui.chapterList.count() - 1)
        self.ui.chapterList.takeItem(self.ui.chapterList.count() - 1)
        del last_item

        # 添加新章节
        self._chapters[name] = ""
        idx = self.ui.chapterList.count() + 1  # 新章节的序号

        # 创建章节项
        widget = self._create_chapter_item_widget(idx, name, True)
        item = QListWidgetItem()
        item.setSizeHint(QSize(0, 44))
        self.ui.chapterList.addItem(item)
        self.ui.chapterList.setItemWidget(item, widget)

        # 自动选中新章节并清空编辑器
        self._current_chapter = name
        self.ui.chapterList.setCurrentRow(self.ui.chapterList.count() - 1)
        self.ui.editorTextEdit.setPlainText("")
        self._update_chapter_item_styles()

        # 恢复状态
        self._is_input_mode = False
        self._update_chapter_button_visibility()
        self._update_header_chapter_info()

    def _cancel_input(self):
        """取消输入"""
        if self.ui.chapterList.count() > 0:
            last_item = self.ui.chapterList.item(self.ui.chapterList.count() - 1)
            widget = self.ui.chapterList.itemWidget(last_item)
            if widget and widget.objectName() == "chapterInputContainer":
                self.ui.chapterList.takeItem(self.ui.chapterList.count() - 1)
                del last_item
        self._is_input_mode = False
        self._update_chapter_button_visibility()

    def eventFilter(self, obj, event):
        """事件过滤器：处理输入框失去焦点时取消输入"""
        if event.type() == event.Type.FocusOut:
            if isinstance(obj, QLineEdit) and obj.objectName() == "chapterNameInput":
                # 延迟检查，避免点击列表其他位置时的竞争条件
                QTimer.singleShot(100, self._check_input_cancel)
        return super().eventFilter(obj, event)

    def _check_input_cancel(self):
        """检查是否需要取消输入"""
        if self._is_input_mode:
            # 检查当前焦点是否还在输入框
            from PySide6.QtWidgets import QApplication
            focus_widget = QApplication.focusWidget()
            if not (isinstance(focus_widget, QLineEdit) and focus_widget.objectName() == "chapterNameInput"):
                self._cancel_input()

    def _on_chapter_changed(self, row):
        """切换章节时保存当前内容并加载新章节内容"""
        if row < 0 or row >= self.ui.chapterList.count():
            return

        # 检查是否是输入框项
        item = self.ui.chapterList.item(row)
        widget = self.ui.chapterList.itemWidget(item)
        if widget and widget.objectName() == "chapterInputContainer":
            return

        # 保存当前章节内容
        if self._current_chapter:
            self._chapters[self._current_chapter] = self.ui.editorTextEdit.toPlainText()

        # 从 item 的 widget 中获取纯章节名
        new_chapter = ""
        if widget:
            name_label = widget.findChild(QLabel, "chapterNameLabel")
            if name_label:
                new_chapter = name_label.text()

        if not new_chapter:
            return

        self._current_chapter = new_chapter
        content = self._chapters.get(new_chapter, "")
        self.ui.editorTextEdit.setPlainText(content)

        # 更新文档名显示（显示纯名称，不带序号）
        self.set_document_name(new_chapter)

        # 更新所有项的样式
        self._update_chapter_item_styles()
        self._update_header_chapter_info()

    def _on_chapter_double_click(self, row):
        """双击章节项：进入编辑模式"""
        if row < 0 or row >= self.ui.chapterList.count():
            return
        self._start_chapter_edit(row)

    def _start_chapter_edit(self, row):
        """开始编辑章节名称"""
        item = self.ui.chapterList.item(row)
        widget = self.ui.chapterList.itemWidget(item)
        if not widget:
            return
        name_label = widget.findChild(QLabel, "chapterNameLabel")
        idx_label = widget.findChild(QLabel, "chapterIndexLabel")
        if not name_label or not idx_label:
            return

        old_name = name_label.text()

        # 创建输入框替换标签
        line_edit = QLineEdit(old_name)
        line_edit.setObjectName("chapterEditInput")
        line_edit.setStyleSheet("""
            QLineEdit {
                background-color: transparent;
                color: #EAECEF;
                border: none;
                font-size: 13px;
                padding: 0;
            }
        """)

        # 替换布局中的标签
        layout = widget.layout()
        layout.replaceWidget(name_label, line_edit)
        name_label.deleteLater()

        line_edit.setFocus()
        line_edit.selectAll()

        def on_edit_finished():
            new_name = line_edit.text().strip()
            if new_name and new_name != old_name:
                # 更新数据
                if old_name in self._chapters:
                    content = self._chapters.pop(old_name)
                    self._chapters[new_name] = content
                if self._current_chapter == old_name:
                    self._current_chapter = new_name
                    self.set_document_name(new_name)

            # 恢复为标签
            new_label = QLabel(new_name or old_name)
            new_label.setObjectName("chapterNameLabel")
            layout.replaceWidget(line_edit, new_label)
            line_edit.deleteLater()
            self._update_chapter_item_styles()
            self._update_header_chapter_info()

        line_edit.returnPressed.connect(on_edit_finished)
        line_edit.editingFinished.connect(on_edit_finished)

    def _on_chapter_context_menu(self, row, pos):
        """右键章节项：显示删除菜单"""
        if row < 0 or row >= self.ui.chapterList.count():
            return

        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1A1A22;
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 8px;
                padding: 4px;
            }
            QMenu::item {
                color: #EAECEF;
                padding: 8px 16px;
                border-radius: 6px;
            }
            QMenu::item:selected {
                background-color: rgba(77,124,254,0.15);
            }
        """)

        delete_action = menu.addAction("删除本章节")
        action = menu.exec(self.ui.chapterList.viewport().mapToGlobal(pos))

        if action == delete_action:
            self._delete_chapter(row)

    def _delete_chapter(self, row):
        """删除指定章节"""
        item = self.ui.chapterList.item(row)
        widget = self.ui.chapterList.itemWidget(item)
        if not widget:
            return

        name_label = widget.findChild(QLabel, "chapterNameLabel")
        if not name_label:
            return

        chapter_name = name_label.text()

        # 从数据中删除
        if chapter_name in self._chapters:
            del self._chapters[chapter_name]

        # 如果删除的是当前章节，清空编辑器
        if self._current_chapter == chapter_name:
            self._current_chapter = None
            self.ui.editorTextEdit.setPlainText("")
            self.set_document_name("")

        # 从列表中删除
        self.ui.chapterList.takeItem(row)
        del item

        # 重新排序序号
        self._reindex_chapters()

        # 更新样式
        self._update_chapter_item_styles()
        self._update_header_chapter_info()

    def _reindex_chapters(self):
        """重新排序章节序号"""
        for i in range(self.ui.chapterList.count()):
            item = self.ui.chapterList.item(i)
            widget = self.ui.chapterList.itemWidget(item)
            if not widget:
                continue
            idx_label = widget.findChild(QLabel, "chapterIndexLabel")
            if idx_label:
                idx_label.setText(f"{i+1:02d}")

    def _update_chapter_button_visibility(self):
        """大按钮始终显示（只要不在输入模式）"""
        self.ui.btnNewChapterBig.setVisible(not self._is_input_mode)

    # ── 文档名 ──
    def set_document_name(self, name):
        """设置文档名称（显示在底部状态栏）"""
        self.ui.statusDocName.setText(name)
        self._current_doc_name = name

    def _update_header_chapter_info(self):
        """更新右侧编辑区顶部章节信息显示"""
        if self._current_chapter:
            self.ui.pageTitle.setText(f"章节：{self._current_chapter}")
            self.ui.pageSubtitle.setText(f"当前章节 · 共 {len(self._chapters)} 章")
        else:
            self.ui.pageTitle.setText("章节：")
            self.ui.pageSubtitle.setText("暂无章节")

    # ── 编码自动检测 ──
    def _read_text_file(self, path):
        """自动检测编码读取纯文本文件"""
        encodings = ["utf-8", "gbk", "gb2312", "gb18030", "big5", "utf-16", "latin-1"]
        for enc in encodings:
            try:
                with open(path, "r", encoding=enc) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        with open(path, "r", encoding="latin-1") as f:
            return f.read()

    def _read_docx_file(self, path):
        """读取 .docx 文件中的纯文本内容"""
        try:
            with zipfile.ZipFile(path, "r") as zf:
                xml_content = zf.read("word/document.xml")
            root = _safe_fromstring(xml_content)
            ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
            paragraphs = []
            for p in root.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p"):
                texts = [t.text for t in p.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t") if t.text]
                if texts:
                    paragraphs.append("".join(texts))
            return "\n".join(paragraphs)
        except Exception as e:
            raise RuntimeError(f"解析 Word 文档失败: {e}")

    def _read_html_file(self, path):
        """读取 HTML 文件，提取纯文本"""
        content = self._read_text_file(path)
        # 简单去除标签
        text = re.sub(r"<script[^>]*>[\s\S]*?</script>", "", content, flags=re.IGNORECASE)
        text = re.sub(r"<style[^>]*>[\s\S]*?</style>", "", text, flags=re.IGNORECASE)
        text = re.sub(r"<[^>]+>", "", text)
        text = re.sub(r"&nbsp;|&amp;|&lt;|&gt;|&quot;", lambda m: {"&nbsp;": " ", "&amp;": "&", "&lt;": "<", "&gt;": ">", "&quot;": '"'}[m.group()], text)
        return text.strip()

    def _read_file_content(self, path):
        """根据文件扩展名选择正确的读取方式"""
        ext = os.path.splitext(path)[1].lower()
        if ext == ".docx":
            return self._read_docx_file(path)
        elif ext in (".html", ".htm"):
            return self._read_html_file(path)
        elif ext in (".txt", ".md", ".rtf"):
            return self._read_text_file(path)
        else:
            # 未知格式，尝试当作文本读取
            return self._read_text_file(path)

    # ── 保存当前任务状态 ──
    def _save_current_task(self):
        """保存当前任务到任务列表"""
        if self._current_task_index >= 0 and self._current_task_index < len(self._tasks):
            # 保存当前章节内容
            if self._current_chapter:
                self._chapters[self._current_chapter] = self.ui.editorTextEdit.toPlainText()
            task_name = self._tasks[self._current_task_index][0]
            self._tasks[self._current_task_index] = (
                task_name, dict(self._chapters), self._current_chapter
            )

    def _load_task(self, index):
        """加载指定任务"""
        if index < 0 or index >= len(self._tasks):
            return
        self._save_current_task()
        self._current_task_index = index
        task_name, chapters, current_chapter = self._tasks[index]
        self._chapters = dict(chapters)
        self._current_chapter = current_chapter
        # 重建章节列表
        self.ui.chapterList.clear()
        for i, (name, content) in enumerate(self._chapters.items(), 1):
            widget = self._create_chapter_item_widget(i, name, name == current_chapter)
            item = QListWidgetItem()
            item.setSizeHint(QSize(0, 44))
            self.ui.chapterList.addItem(item)
            self.ui.chapterList.setItemWidget(item, widget)
        # 恢复编辑器内容
        if current_chapter and current_chapter in self._chapters:
            self.ui.editorTextEdit.setPlainText(self._chapters[current_chapter])
        else:
            self.ui.editorTextEdit.setPlainText("")
        self.set_document_name(task_name)
        self._update_chapter_item_styles()
        self._update_chapter_button_visibility()
        self._update_header_chapter_info()
        self._update_word_count()

    # ── 打开文件 ──
    def _on_open_file(self):
        """打开文件：弹出文件选择器，加载文本内容到编辑器"""
        from PySide6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getOpenFileName(
            self, "打开文件", "",
            "所有文本文件 (*.txt *.md *.docx *.doc *.rtf *.epub *.html *.htm);;"
            "纯文本 (*.txt);;"
            "Markdown (*.md);;"
            "Word 文档 (*.docx *.doc);;"
            "富文本 (*.rtf);;"
            "电子书 (*.epub);;"
            "网页 (*.html *.htm);;"
            "所有文件 (*)"
        )
        if not path:
            return
        try:
            content = self._read_file_content(path)
            # 保存当前任务
            self._save_current_task()
            # 创建新任务
            name = os.path.splitext(os.path.basename(path))[0]
            # 清空旧数据，创建单章节任务
            self._chapters = {name: content}
            self._current_chapter = name
            self.ui.chapterList.clear()
            widget = self._create_chapter_item_widget(1, name, True)
            item = QListWidgetItem()
            item.setSizeHint(QSize(0, 44))
            self.ui.chapterList.addItem(item)
            self.ui.chapterList.setItemWidget(item, widget)
            self.ui.editorTextEdit.setPlainText(content)
            self.set_document_name(name)
            # 添加到任务列表
            self._tasks.append((name, dict(self._chapters), name))
            self._current_task_index = len(self._tasks) - 1
            self._update_chapter_item_styles()
            self._update_chapter_button_visibility()
            self._update_header_chapter_info()
            self._update_word_count()
            print(f"[速文] 已打开文件: {path}")
        except Exception as e:
            print(f"[速文] 打开文件失败: {e}")
            QMessageBox.warning(self, "打开失败", f"无法打开文件:\n{e}")

    # ── 新建任务 ──
    def _on_new_task(self):
        """新建任务：点击后在状态栏上方显示任务选择弹窗"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1A1A22;
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 8px;
                padding: 6px;
                min-width: 180px;
            }
            QMenu::item {
                color: #EAECEF;
                padding: 10px 16px;
                border-radius: 6px;
                font-size: 13px;
            }
            QMenu::item:selected {
                background-color: rgba(77,124,254,0.15);
                color: #4D7CFE;
            }
        """)

        # 任务列表
        tasks = [
            ("📝  日常写作", "自由写作，不限题材"),
            ("📖  小说创作", "长篇网文 / 出版小说"),
            ("✍️  专栏文章", "系列专栏内容创作"),
            ("📋  读书笔记", "阅读摘录与心得整理"),
            ("📄  工作文档", "报告、方案等正式写作"),
        ]

        for title, desc in tasks:
            action = menu.addAction(f"{title}")
            action.setToolTip(desc)
            action.triggered.connect(lambda checked, t=title: self._on_task_selected(t))

        # 在按钮下方弹出
        menu.exec(self.ui.btnNewTask.mapToGlobal(
            self.ui.btnNewTask.rect().bottomLeft()
        ))

    def _on_task_selected(self, task_name):
        """选择任务后创建新任务"""
        self._save_current_task()
        # 清空当前数据，创建新任务
        self._chapters = {}
        self._current_chapter = None
        self.ui.chapterList.clear()
        self.ui.editorTextEdit.setPlainText("")
        self.set_document_name(task_name)
        # 添加到任务列表
        self._tasks.append((task_name, {}, None))
        self._current_task_index = len(self._tasks) - 1
        self._update_chapter_button_visibility()
        self._update_word_count()
        print(f"[速文] 已创建任务: {task_name}")

    def _on_status_doc_name_clicked(self):
        """点击底部状态栏文档名：弹出任务切换菜单"""
        if not self._tasks:
            return
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1A1A22;
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 8px;
                padding: 6px;
                min-width: 200px;
            }
            QMenu::item {
                color: #EAECEF;
                padding: 10px 16px;
                border-radius: 6px;
                font-size: 13px;
            }
            QMenu::item:selected {
                background-color: rgba(77,124,254,0.15);
                color: #4D7CFE;
            }
        """)
        for idx, (task_name, _, _) in enumerate(self._tasks):
            # 当前任务加标记
            display_name = f"✓  {task_name}" if idx == self._current_task_index else f"    {task_name}"
            action = menu.addAction(display_name)
            action.triggered.connect(lambda checked, i=idx: self._load_task(i))
        # 在状态栏上方弹出
        menu.exec(self.ui.statusDocName.mapToGlobal(
            self.ui.statusDocName.rect().topLeft() - QPoint(0, menu.sizeHint().height() + 4)
        ))

    # ── AI 功能 ──
    def _open_ai_dialog(self, feature_key):
        """打开 AI 功能对话框"""
        # 获取编辑器选中文本（如果有），否则获取全部内容
        cursor = self.ui.editorTextEdit.textCursor()
        selected_text = cursor.selectedText()
        editor_text = selected_text if selected_text else self.ui.editorTextEdit.toPlainText()

        dialog = AiFeatureDialog(feature_key, self, editor_text)
        # 传递主题色以适配浅色模式
        if hasattr(self, '_theme_colors'):
            dialog.apply_theme(self._theme_colors)
        dialog.exec()

    def insert_ai_result(self, text):
        """将 AI 生成结果插入到编辑器当前光标位置"""
        cursor = self.ui.editorTextEdit.textCursor()
        cursor.insertText(text)
        self.ui.editorTextEdit.setTextCursor(cursor)
        self.ui.editorTextEdit.setFocus()

    # ── 获取内容 ──
    def get_text(self):
        return self.ui.editorTextEdit.toPlainText()

    def set_text(self, text):
        self.ui.editorTextEdit.setPlainText(text)

    # ── 主题应用 ──
    def apply_theme(self, colors):
        """Apply theme colors to all stylable elements.

        Args:
            colors: dict with keys — bg, card_bg, border_light, border,
                    text_main, text_sub, text_muted, input_bg, primary,
                    primary_hover, hover_bg, active_bg
        """
        c = colors
        self._theme_colors = colors

        # 清除 .ui 文件设置的控件级样式表（否则会覆盖页面级 QSS）
        self.ui.headerFrame.setStyleSheet("")
        self.ui.toolbarFrame.setStyleSheet("")

        # 1. Detect theme mode & build comprehensive QSS stylesheet
        #    包含原 .ui 文件所有样式，使用主题色参数化
        is_light = int(c['bg'].lstrip('#')[:2], 16) > 128

        # 主题相关的参数
        _editor_bg = '#FFFFFF' if is_light else '#1A1E26'
        _toolbar_bg = c['card_bg'] if is_light else 'rgba(20,24,32,0.4)'
        _tb_border = 'none' if is_light else '1px solid rgba(255,255,255,0.04)'
        _combo_bg = '#FFFFFF' if is_light else c['card_bg']
        _combo_color = c['text_main']
        _dd_bg = c['card_bg']
        _tool_overlay = 'rgba(0,0,0,0.04)' if is_light else c['hover_bg']
        _tool_clr = '#6E6E73' if is_light else c['text_sub']
        _tool_clr_hv = c['text_main']
        _border_subtle = 'rgba(0,0,0,0.06)' if is_light else c['border_light']
        _border_hover = c['border'] if not is_light else '#D1D1D6'
        _hf_border = f'border-bottom: 1px solid {_border_subtle}'
        _tb_radius = '0px' if is_light else '10px'
        _sb_bg = '#FAFAFC' if is_light else _toolbar_bg
        _sb_radius = '0px' if is_light else '8px'

        self.setStyleSheet(f"""
QWidget#SpeedwritePage {{
    background-color: {c['bg']};
}}

/* toolbar frame */
QFrame#toolbarFrame {{
    background-color: {_toolbar_bg};
    {f'border: none; border-bottom: 1px solid rgba(0,0,0,0.06);' if is_light else f'border: {_tb_border};'}
    border-radius: {_tb_radius};
}}

/* header frame */
QFrame#headerFrame {{
    background-color: transparent;
    border: none;
    {_hf_border};
}}

/* primary button */
QPushButton#btnNewTask {{
    background-color: {c['primary']};
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 500;
    padding: 8px 16px;
    height: 36px;
}}
QPushButton#btnNewTask:hover {{ background-color: {c['primary_hover']}; }}
QPushButton#btnNewTask:pressed {{ background-color: {c['primary_hover']}; }}

/* outline button */
QPushButton#btnOpenFile {{
    background-color: transparent;
    color: {c['text_sub']};
    border: 1px solid {_border_subtle};
    border-radius: 8px;
    font-size: 13px;
    padding: 8px 16px;
    height: 36px;
}}
QPushButton#btnOpenFile:hover {{ border-color: {_border_hover}; color: {c['text_main']}; }}

/* toolbar icon buttons */
QPushButton#btnBold, QPushButton#btnItalic, QPushButton#btnUnderline,
QPushButton#btnStrike, QPushButton#btnAlignLeft, QPushButton#btnAlignCenter,
QPushButton#btnAlignRight, QPushButton#btnAlignJustify,
QPushButton#btnList, QPushButton#btnOrderedList,
QPushButton#btnOutdent, QPushButton#btnIndent,
QPushButton#btnUndo, QPushButton#btnRedo,
QPushButton#btnDarkMode {{
    background-color: transparent;
    color: {_tool_clr};
    border: none;
    border-radius: 6px;
    font-size: 16px;
    font-weight: 600;
    width: 28px;
    height: 28px;
}}
QPushButton#btnBold:hover, QPushButton#btnItalic:hover, QPushButton#btnUnderline:hover,
QPushButton#btnStrike:hover, QPushButton#btnAlignLeft:hover, QPushButton#btnAlignCenter:hover,
QPushButton#btnAlignRight:hover, QPushButton#btnAlignJustify:hover,
QPushButton#btnList:hover, QPushButton#btnOrderedList:hover,
QPushButton#btnOutdent:hover, QPushButton#btnIndent:hover,
QPushButton#btnUndo:hover, QPushButton#btnRedo:hover,
QPushButton#btnDarkMode:hover {{
    background-color: {_tool_overlay};
    color: {_tool_clr_hv};
}}
QPushButton#btnBold:checked, QPushButton#btnItalic:checked,
QPushButton#btnUnderline:checked, QPushButton#btnStrike:checked,
QPushButton#btnAlignLeft:checked, QPushButton#btnAlignCenter:checked,
QPushButton#btnAlignRight:checked, QPushButton#btnAlignJustify:checked {{
    background-color: {c['primary']};
    color: #FFFFFF;
}}

/* action buttons */
QPushButton#btnExport, QPushButton#btnExportNormal, QPushButton#btnExportMobile,
QPushButton#btnMobileMode, QPushButton#btnAiAssistant,
QPushButton#btnExportMd, QPushButton#btnExportTxt, QPushButton#btnPreview {{
    background-color: transparent;
    color: {_tool_clr};
    border: 1px solid {_border_subtle};
    border-radius: 6px;
    font-size: 12px;
    padding: 0 10px;
    height: 28px;
}}
QPushButton#btnExport:hover, QPushButton#btnExportNormal:hover, QPushButton#btnExportMobile:hover,
QPushButton#btnMobileMode:hover, QPushButton#btnAiAssistant:hover,
QPushButton#btnExportMd:hover, QPushButton#btnExportTxt:hover, QPushButton#btnPreview:hover {{
    background-color: {_tool_overlay};
    color: {_tool_clr_hv};
    border-color: {_border_hover};
}}

/* color buttons */
QPushButton#btnTextColor, QPushButton#btnBgColor {{
    border-radius: 4px;
    border: 2px solid {_border_subtle};
    width: 22px;
    height: 22px;
}}
QPushButton#btnTextColor {{ background-color: #1A1A22; color: #FFFFFF; }}
QPushButton#btnBgColor {{ background-color: #FFE066; color: #1D1D1F; }}
QPushButton#btnTextColor:hover, QPushButton#btnBgColor:hover {{ border-color: {_border_hover}; }}

/* combo boxes */
QComboBox#fontCombo, QComboBox#sizeCombo, QComboBox#lineSpacingCombo,
QComboBox#bgThemeCombo, QComboBox#exportCombo {{
    background-color: {_combo_bg};
    color: {_combo_color};
    border: {f'1px solid {c["border"]}' if is_light else f'1px solid {c["border_light"]}'};
    border-radius: 6px;
    font-size: 12px;
    padding: 0 10px;
    height: 30px;
    min-width: 80px;
}}
QComboBox#fontCombo:hover, QComboBox#sizeCombo:hover,
QComboBox#lineSpacingCombo:hover, QComboBox#bgThemeCombo:hover {{
    background-color: {_tool_overlay};
    border-color: {_border_hover};
}}
QLabel#comboLabel {{
    color: {_tool_clr};
    font-size: 12px;
    background: transparent;
    border: none;
    padding-right: 2px;
}}
QComboBox#fontCombo::drop-down, QComboBox#sizeCombo::drop-down,
QComboBox#lineSpacingCombo::drop-down, QComboBox#bgThemeCombo::drop-down,
QComboBox#exportCombo::drop-down {{
    border: none;
    width: 22px;
}}
QComboBox#fontCombo::down-arrow, QComboBox#sizeCombo::down-arrow,
QComboBox#lineSpacingCombo::down-arrow, QComboBox#bgThemeCombo::down-arrow,
QComboBox#exportCombo::down-arrow {{
    {f'image: none; border-left: 4px solid transparent; border-right: 4px solid transparent; border-top: 5px solid #8E8E93; width: 0; height: 0;' if not is_light else 'image: none; width: 0; height: 0;'}
}}
QComboBox#fontCombo QAbstractItemView, QComboBox#sizeCombo QAbstractItemView,
QComboBox#lineSpacingCombo QAbstractItemView,
QComboBox#bgThemeCombo QAbstractItemView,
QComboBox#exportCombo QAbstractItemView {{
    background-color: {_dd_bg};
    color: {_combo_color};
    font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
    font-size: 12px;
    border: 1px solid {_border_subtle};
    border-radius: 8px;
    selection-background-color: {c['primary']};
    selection-color: #FFFFFF;
    padding: 4px;
}}
/* explicit item states for persistent selection highlight */
QComboBox#fontCombo QAbstractItemView::item:selected,
QComboBox#sizeCombo QAbstractItemView::item:selected,
QComboBox#lineSpacingCombo QAbstractItemView::item:selected,
QComboBox#bgThemeCombo QAbstractItemView::item:selected,
QComboBox#exportCombo QAbstractItemView::item:selected {{
    background-color: {c['primary']};
    color: #FFFFFF;
}}
QComboBox#fontCombo QAbstractItemView::item:hover,
QComboBox#sizeCombo QAbstractItemView::item:hover,
QComboBox#lineSpacingCombo QAbstractItemView::item:hover,
QComboBox#bgThemeCombo QAbstractItemView::item:hover,
QComboBox#exportCombo QAbstractItemView::item:hover {{
    background-color: {c['primary_hover']};
    color: #FFFFFF;
}}

/* left panel */
QFrame#leftPanel {{
    background-color: transparent;
    border: none;
    border-right: 1px solid {_border_subtle};
}}

/* AI assistant buttons */
QPushButton#btnGenOutline, QPushButton#btnWorldBuild, QPushButton#btnCharacter,
QPushButton#btnContinueWrite, QPushButton#btnPolish, QPushButton#btnDialogue {{
    background-color: transparent;
    border: none;
    border-radius: 8px;
    text-align: left;
    padding: 10px 12px;
    font-size: 13px;
    color: {c['text_main']};
}}
QPushButton#btnGenOutline:hover, QPushButton#btnWorldBuild:hover,
QPushButton#btnCharacter:hover, QPushButton#btnContinueWrite:hover,
QPushButton#btnPolish:hover, QPushButton#btnDialogue:hover {{
    background-color: {_tool_overlay};
}}

/* new chapter button */
QPushButton#btnNewChapter {{
    background-color: rgba(77,124,254,0.15);
    color: {c['primary']};
    border: none;
    border-radius: 6px;
    font-size: 16px;
    font-weight: 600;
    width: 28px;
    height: 28px;
    padding: 0;
}}
QPushButton#btnNewChapter:hover {{
    background-color: rgba(77,124,254,0.25);
}}

/* tag buttons */
QPushButton#btnWorldForce, QPushButton#btnWorldMap, QPushButton#btnWorldPower,
QPushButton#btnCharCard, QPushButton#btnRelationNet {{
    background-color: {c['hover_bg']};
    color: {c['text_sub']};
    border: 1px solid {_border_subtle};
    border-radius: 6px;
    font-size: 12px;
    padding: 0 12px;
    height: 32px;
}}
QPushButton#btnWorldForce:hover, QPushButton#btnWorldMap:hover,
QPushButton#btnWorldPower:hover, QPushButton#btnCharCard:hover,
QPushButton#btnRelationNet:hover {{
    background-color: {c['active_bg']};
    color: {c['text_main']};
    border-color: {_border_hover};
}}

/* chapter list */
QListWidget#chapterList {{
    background-color: transparent;
    border: none;
    padding: 0;
    outline: none;
    show-decoration-selected: 0;
}}
QListWidget#chapterList::item {{
    background-color: transparent;
    color: transparent;
}}
QListWidget#chapterList::item:hover {{
    background-color: transparent;
}}
QListWidget#chapterList::item:selected {{
    background-color: transparent;
    color: transparent;
}}
QListWidget#chapterList::item:selected:active {{
    background-color: transparent;
    color: transparent;
}}
QListWidget#chapterList::item:selected:!active {{
    background-color: transparent;
    color: transparent;
}}
QListWidget#chapterList QScrollBar:vertical {{
    background-color: transparent;
    width: 4px;
    margin: 0;
}}
QListWidget#chapterList QScrollBar::handle:vertical {{
    background-color: {c['text_muted']};
    border-radius: 2px;
    min-height: 30px;
}}
QListWidget#chapterList QScrollBar::handle:vertical:hover {{
    background-color: {c['text_sub']};
}}
QListWidget#chapterList QScrollBar::add-line:vertical,
QListWidget#chapterList QScrollBar::sub-line:vertical {{
    height: 0;
    background: none;
}}
QListWidget#chapterList QScrollBar::add-page:vertical,
QListWidget#chapterList QScrollBar::sub-page:vertical {{
    background: none;
}}

/* line edit */
QLineEdit#outlineInput {{
    background-color: {c['input_bg']};
    color: {c['text_main']};
    border: 1px solid {_border_subtle};
    border-radius: 8px;
    font-size: 12px;
    padding: 0 12px;
    height: 36px;
}}
QLineEdit#outlineInput:focus {{
    border-color: {c['primary']};
}}
QLineEdit#outlineInput::placeholder {{
    color: {c['text_muted']};
    opacity: 0.5;
}}

/* generate outline button */
QPushButton#btnGenerateOutline {{
    background-color: {c['primary']};
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 500;
    padding: 8px 16px;
    height: 40px;
}}
QPushButton#btnGenerateOutline:hover {{ background-color: {c['primary_hover']}; }}
QPushButton#btnGenerateOutline:pressed {{ background-color: {c['primary_hover']}; }}

/* status bar */
QFrame#statusBar {{
    background-color: {_sb_bg};
    {f'border: none; border-top: 1px solid rgba(0,0,0,0.06);' if is_light else f'border: {_tb_border};'}
    border-radius: {_sb_radius};
}}

/* page titles */
QLabel#pageTitle {{
    color: {c['text_main']};
    font-size: 18px;
    font-weight: 700;
}}
QLabel#pageSubtitle {{
    color: {c['text_sub']};
    font-size: 12px;
}}

/* splitter */
QSplitter::handle {{
    background-color: {_border_subtle};
}}

/* scroll areas */
QScrollArea#rightScrollArea {{
    background-color: transparent;
    border: none;
}}
QScrollArea#rightScrollArea > QWidget > QWidget {{
    background-color: transparent;
}}
QScrollArea#rightScrollArea QScrollBar:vertical {{
    background-color: transparent;
    width: 6px;
    border-radius: 3px;
}}
QScrollArea#rightScrollArea QScrollBar::handle:vertical {{
    background-color: {c['text_muted']};
    border-radius: 3px;
    min-height: 40px;
}}
QScrollArea#rightScrollArea QScrollBar::handle:vertical:hover {{
    background-color: {c['text_sub']};
}}

QScrollArea#leftScrollArea {{
    background-color: transparent;
    border: none;
}}
QScrollArea#leftScrollArea > QWidget > QWidget {{
    background-color: transparent;
}}
QScrollArea#leftScrollArea QScrollBar:vertical {{
    background-color: transparent;
    width: 4px;
    border-radius: 2px;
}}
QScrollArea#leftScrollArea QScrollBar::handle:vertical {{
    background-color: {c['text_muted']};
    border-radius: 2px;
    min-height: 30px;
}}
""")

        # 2. Left panel header (title_label & desc_label created in _init_left_panel_header)
        try:
            hw = self.ui.leftInnerLayout.itemAt(0).widget()
            if hw is not None:
                for lbl in hw.findChildren(QLabel):
                    ss = lbl.styleSheet()
                    if "font-size: 24px" in ss and "font-weight: 700" in ss:
                        lbl.setStyleSheet(
                            f"color: {c['text_main']}; font-size: 24px; "
                            f"font-weight: 700; background: transparent;"
                        )
                    elif "font-size: 12px" in ss:
                        lbl.setStyleSheet(
                            f"color: {c['text_sub']}; font-size: 12px; "
                            f"font-weight: 400; background: transparent;"
                        )
        except Exception:
            pass

        # 3. AI feature card labels + button hover styles
        ai_btn_names = [
            "btnGenOutline", "btnWorldBuild", "btnCharacter",
            "btnContinueWrite", "btnPolish", "btnDialogue",
        ]
        for btn_name in ai_btn_names:
            try:
                btn = getattr(self.ui, btn_name)
                # Update button hover style
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        border: none;
                        border-radius: 8px;
                        padding: 0;
                        text-align: left;
                    }}
                    QPushButton:hover {{
                        background-color: {c['hover_bg']};
                    }}
                """)
                # Update icon_bg / title_label / desc_label inside button
                for lbl in btn.findChildren(QLabel):
                    ss = lbl.styleSheet()
                    if "background-color" in ss and "rgba" in ss:
                        lbl.setStyleSheet(
                            f"background-color: rgba(77,124,254,0.12); "
                            f"border-radius: 8px; font-size: 16px; "
                            f"color: #4D7CFE;"
                        )
                    elif "font-weight: 500" in ss:
                        # title_label
                        lbl.setStyleSheet(
                            f"color: {c['text_main']}; font-size: 14px; "
                            f"font-weight: 500; background: transparent;"
                        )
                    elif "font-size: 11px" in ss:
                        # desc_label
                        lbl.setStyleSheet(
                            f"color: {c['text_sub']}; font-size: 11px; "
                            f"font-weight: 400; background: transparent;"
                        )
            except Exception:
                pass

        # 4. Editor text edit（深色模式灰黑，浅色模式灰色）
        try:
            editor = self.ui.editorTextEdit
            _editor_border = '1px solid #E5E5EA' if is_light else f"1px solid {c['border_light']}"
            editor.setStyleSheet(f"""
                QTextEdit {{
                    background-color: {_editor_bg};
                    color: {c['text_main']};
                    border: {_editor_border};
                    border-radius: 12px;
                    font-size: 15px;
                    padding: 28px;
                    selection-background-color: {c['primary']};
                    selection-color: #FFFFFF;
                }}
                QTextEdit QScrollBar:vertical {{
                    background-color: transparent; width: 6px;
                }}
                QTextEdit QScrollBar::handle:vertical {{
                    background-color: {c['text_muted']};
                    border-radius: 3px; min-height: 40px;
                }}
            """)
            # Restore placeholder color (setStyleSheet resets QPalette)
            palette = editor.palette()
            palette.setColor(
                QPalette.ColorRole.PlaceholderText,
                QColor(c['text_sub'])
            )
            editor.setPalette(palette)
        except Exception:
            pass

        # 5. Mobile preview button
        try:
            self.ui.btnMobilePreview.setStyleSheet(f"""
                QPushButton {{
                    background-color: {c['primary']};
                    color: #FFFFFF;
                    border: none;
                    border-radius: 6px;
                    font-size: 12px;
                    padding: 0 10px;
                    height: 28px;
                }}
            """)
        except Exception:
            pass

        # 6. Chapter list document item labels
        try:
            for i in range(self.ui.chapterList.count()):
                item = self.ui.chapterList.item(i)
                w = self.ui.chapterList.itemWidget(item)
                if w is None:
                    continue
                idx_lbl = w.findChild(QLabel, "chapterIndexLabel")
                name_lbl = w.findChild(QLabel, "chapterNameLabel")
                if idx_lbl is not None:
                    idx_lbl.setStyleSheet(
                        f"color: {c['text_muted']}; font-size: 13px; "
                        f"font-weight: 400; background: transparent;"
                    )
                if name_lbl is not None:
                    is_sel = (i == self.ui.chapterList.currentRow())
                    if is_sel:
                        name_lbl.setStyleSheet(
                            f"color: {c['primary']}; font-size: 13px; "
                            f"font-weight: 500; background: transparent;"
                        )
                    else:
                        name_lbl.setStyleSheet(
                            f"color: {c['text_sub']}; font-size: 13px; "
                            f"font-weight: 400; background: transparent;"
                        )
        except Exception:
            pass

        # 7. Chapter input container (if currently in input mode)
        try:
            for i in range(self.ui.chapterList.count()):
                item = self.ui.chapterList.item(i)
                w = self.ui.chapterList.itemWidget(item)
                if w is not None and w.objectName() == "chapterInputContainer":
                    w.setStyleSheet(f"""
                        QWidget#chapterInputContainer {{
                            background-color: rgba(30, 35, 41, 0.6);
                            border: 1px solid {c['primary']};
                            border-radius: 10px;
                        }}
                    """)
                    le = w.findChild(QLineEdit, "chapterNameInput")
                    if le is not None:
                        le.setStyleSheet(f"""
                            QLineEdit {{
                                background-color: transparent;
                                color: {c['text_main']};
                                border: none;
                                font-size: 13px;
                                padding: 0;
                            }}
                        """)
        except Exception:
            pass

        # 8. Chapter edit input line edit (if currently in edit mode)
        try:
            for i in range(self.ui.chapterList.count()):
                item = self.ui.chapterList.item(i)
                w = self.ui.chapterList.itemWidget(item)
                if w is not None:
                    le = w.findChild(QLineEdit, "chapterEditInput")
                    if le is not None:
                        le.setStyleSheet(f"""
                            QLineEdit {{
                                background-color: transparent;
                                color: {c['text_main']};
                                border: none;
                                font-size: 13px;
                                padding: 0;
                            }}
                        """)
        except Exception:
            pass
            pass
