"""
ai_dialogs.py - AI 功能交互对话框
包含 AI 设置对话框和 6 个 AI 功能对话框
采用 QThread 异步调用 API，避免 UI 卡顿
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTextEdit, QMessageBox, QWidget, QScrollArea, QFormLayout, QSpacerItem,
    QSizePolicy, QApplication
)
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from PySide6.QtGui import QFont

from . import ai_api

# ═══════════════════════════════════════════════════════════════
# AI 设置对话框
# ═══════════════════════════════════════════════════════════════

class AiSettingsDialog(QDialog):
    """AI 设置对话框：配置 API 地址、Key、模型"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AI 设置")
        self.setFixedSize(520, 360)
        self.setStyleSheet("""
            QDialog {
                background-color: #0A0E17;
            }
        """)
        self._setup_ui()
        self._load_config()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # 标题
        title = QLabel("AI 模型配置")
        title.setStyleSheet("color: #EAECEF; font-size: 18px; font-weight: 700;")
        layout.addWidget(title)

        desc = QLabel("支持任何 OpenAI 兼容协议的 API 服务，如 DeepSeek、通义千问、Ollama 本地等")
        desc.setStyleSheet("color: #848E9C; font-size: 12px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # 表单
        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self._input_base_url = QLineEdit()
        self._input_base_url.setPlaceholderText("https://api.deepseek.com")
        self._set_input_style(self._input_base_url)
        form.addRow("API 地址:", self._input_base_url)

        self._input_api_key = QLineEdit()
        self._input_api_key.setPlaceholderText("sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        self._input_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self._set_input_style(self._input_api_key)
        form.addRow("API Key:", self._input_api_key)

        self._input_model = QLineEdit()
        self._input_model.setPlaceholderText("deepseek-chat")
        self._set_input_style(self._input_model)
        form.addRow("模型名称:", self._input_model)

        layout.addLayout(form)

        # 测试连接按钮
        test_layout = QHBoxLayout()
        test_layout.addStretch()
        self._btn_test = QPushButton("测试连接")
        self._btn_test.setFixedSize(120, 36)
        self._btn_test.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #848E9C;
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 6px;
                font-size: 13px;
            }
            QPushButton:hover {
                border-color: rgba(255,255,255,0.2);
                color: #EAECEF;
            }
        """)
        self._btn_test.clicked.connect(self._test_connection)
        test_layout.addWidget(self._btn_test)
        layout.addLayout(test_layout)

        # 状态标签
        self._status_label = QLabel("")
        self._status_label.setStyleSheet("color: #848E9C; font-size: 12px;")
        self._status_label.setWordWrap(True)
        layout.addWidget(self._status_label)

        layout.addStretch()

        # 底部按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_cancel = QPushButton("取消")
        btn_cancel.setFixedSize(100, 36)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #848E9C;
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 6px;
                font-size: 13px;
            }
            QPushButton:hover { color: #EAECEF; border-color: rgba(255,255,255,0.2); }
        """)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        btn_save = QPushButton("保存")
        btn_save.setFixedSize(100, 36)
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #4D7CFE;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover { background-color: #3D6CF0; }
        """)
        btn_save.clicked.connect(self._save_and_accept)
        btn_layout.addWidget(btn_save)

        layout.addLayout(btn_layout)

    def _set_input_style(self, input_widget):
        input_widget.setFixedHeight(36)
        input_widget.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255,255,255,0.04);
                color: #EAECEF;
                border: 1px solid rgba(255,255,255,0.06);
                border-radius: 6px;
                padding: 0 12px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #4D7CFE;
            }
            QLineEdit::placeholder {
                color: #5A6270;
            }
        """)

    def _load_config(self):
        cfg = ai_api.get_api_config()
        self._input_base_url.setText(cfg["base_url"])
        self._input_api_key.setText(cfg["api_key"])
        self._input_model.setText(cfg["model"])

    def _test_connection(self):
        self._btn_test.setEnabled(False)
        self._btn_test.setText("测试中...")
        self._status_label.setStyleSheet("color: #848E9C; font-size: 12px;")
        self._status_label.setText("正在连接...")

        # 临时保存输入以便测试
        base_url = self._input_base_url.text().strip() or ai_api.DEFAULT_BASE_URL
        api_key = self._input_api_key.text().strip()
        model = self._input_model.text().strip() or ai_api.DEFAULT_MODEL

        if not api_key:
            self._status_label.setStyleSheet("color: #FF6B6B; font-size: 12px;")
            self._status_label.setText("请输入 API Key")
            self._btn_test.setEnabled(True)
            self._btn_test.setText("测试连接")
            return

        # 临时保存，测试连接
        old_cfg = ai_api.get_api_config()
        ai_api.save_api_config(base_url, api_key, model)

        success, msg = ai_api.test_connection()

        # 恢复旧配置（除非测试成功且用户保存）
        if not success:
            ai_api.save_api_config(
                old_cfg["base_url"], old_cfg["api_key"], old_cfg["model"]
            )

        if success:
            self._status_label.setStyleSheet("color: #4DCF7E; font-size: 12px;")
        else:
            self._status_label.setStyleSheet("color: #FF6B6B; font-size: 12px;")
        self._status_label.setText(msg)
        self._btn_test.setEnabled(True)
        self._btn_test.setText("测试连接")

    def _save_and_accept(self):
        base_url = self._input_base_url.text().strip() or ai_api.DEFAULT_BASE_URL
        api_key = self._input_api_key.text().strip()
        model = self._input_model.text().strip() or ai_api.DEFAULT_MODEL
        ai_api.save_api_config(base_url, api_key, model)
        self.accept()

    def apply_theme(self, colors):
        """应用主题色以适配浅色模式"""
        is_light = int(colors['bg'].lstrip('#')[:2], 16) > 128

        if is_light:
            bg_color = '#F5F5F7'
            text_color = '#1D1D1F'
            sub_color = '#6E6E73'
            input_bg = '#FFFFFF'
            border_color = '#E5E5EA'
            placeholder_color = '#8B8D98'
            btn_border = '#D1D1D6'
            btn_hover_border = '#BBBBC3'
        else:
            bg_color = '#0A0E17'
            text_color = '#EAECEF'
            sub_color = '#848E9C'
            input_bg = 'rgba(255,255,255,0.04)'
            border_color = 'rgba(255,255,255,0.06)'
            placeholder_color = '#5A6270'
            btn_border = 'rgba(255,255,255,0.1)'
            btn_hover_border = 'rgba(255,255,255,0.2)'

        self.setStyleSheet(f"""
            QDialog {{
                background-color: {bg_color};
            }}
        """)

        for lbl in self.findChildren(QLabel):
            ss = lbl.styleSheet()
            if 'font-size: 18px' in ss or 'font-weight: 700' in ss:
                lbl.setStyleSheet(
                    f"color: {text_color}; font-size: 18px; font-weight: 700;"
                )
            else:
                lbl.setStyleSheet(
                    f"color: {sub_color}; font-size: 12px;"
                )

        for le in self.findChildren(QLineEdit):
            le.setStyleSheet(f"""
                QLineEdit {{
                    background-color: {input_bg};
                    color: {text_color};
                    border: 1px solid {border_color};
                    border-radius: 6px;
                    padding: 0 12px;
                    font-size: 13px;
                }}
                QLineEdit:focus {{ border-color: #4D7CFE; }}
                QLineEdit::placeholder {{ color: {placeholder_color}; }}
            """)

        btn_test_style = f"""
            QPushButton {{
                background-color: transparent;
                color: {sub_color};
                border: 1px solid {btn_border};
                border-radius: 6px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                border-color: {btn_hover_border};
                color: {text_color};
            }}
        """
        self._btn_test.setStyleSheet(btn_test_style)

        for btn in self.findChildren(QPushButton):
            ss = btn.styleSheet()
            if '#4D7CFE' in ss:
                # 保存按钮保持主题色
                continue
            btn.setStyleSheet(btn_test_style)


# ═══════════════════════════════════════════════════════════════
# AI 生成线程（异步，避免 UI 卡顿）
# ═══════════════════════════════════════════════════════════════

class AiGenerateThread(QThread):
    """在独立线程中调用 LLM API，通过信号返回结果"""
    result_ready = Signal(str)      # 成功时发送结果文本
    error_occurred = Signal(str)    # 失败时发送错误信息

    def __init__(self, messages, parent=None):
        super().__init__(parent)
        self.messages = messages

    def run(self):
        try:
            result = ai_api.call_llm(self.messages)
            self.result_ready.emit(result)
        except (ValueError, ConnectionError, TimeoutError) as e:
            self.error_occurred.emit(str(e))
        except Exception as e:
            self.error_occurred.emit(f"未知错误: {e}")


# ═══════════════════════════════════════════════════════════════
# AI 功能对话框（通用）
# ═══════════════════════════════════════════════════════════════

class AiFeatureDialog(QDialog):
    """通用 AI 功能对话框"""

    # 6 个功能的预设配置
    FEATURES = {
        "gen_outline": {
            "title": "📝 生成大纲",
            "system_prompt": "你是一位资深网文大纲策划专家。请根据用户提供的题材、风格和设定，生成一份结构完整、逻辑清晰的小说创作大纲。包含：核心创意、主要角色设定、剧情主线、关键转折点、分卷/分章建议。",
            "fields": [
                ("题材类型:", "如：玄幻 / 都市 / 科幻 / 仙侠 / 言情", "玄幻修仙"),
                ("核心设定:", "世界观基础设定", "凡人修仙，逆天改命"),
                ("主角设定:", "主角身份、性格、目标", "资质平庸但意志坚定的少年"),
                ("风格:", "整体风格基调", "轻松热血"),
            ],
            "user_template": "题材：{0}\n核心设定：{1}\n主角设定：{2}\n风格：{3}\n\n请为我生成一份完整的小说创作大纲。",
        },
        "world_build": {
            "title": "🌍 世界观构建",
            "system_prompt": "你是一位专业的奇幻/科幻世界观设计师。请根据用户的需求，构建一个逻辑自洽、细节丰富的世界观设定。包含：世界背景、力量体系（如有）、主要势力分布、地理环境、文化特色、历史沿革。",
            "fields": [
                ("世界类型:", "如：奇幻 / 科幻 / 修真 / 末世", "奇幻"),
                ("核心设定:", "这个世界最独特的设定", "魔法源于远古巨龙的遗骸"),
                ("参考风格:", "如：西方史诗 / 东方玄幻 / 赛博朋克", "西方史诗"),
            ],
            "user_template": "世界类型：{0}\n核心设定：{1}\n参考风格：{2}\n\n请为我构建一个完整的世界观设定。",
        },
        "character": {
            "title": "👤 角色卡",
            "system_prompt": "你是一位角色设计专家。请根据用户的需求，设计一份详细的小说角色卡。包含：基本信息（姓名、年龄、性别）、外貌描述、性格特征、背景故事、能力/特长、弱点、角色关系、成长弧光。",
            "fields": [
                ("角色定位:", "如：主角 / 反派 / 配角", "主角"),
                ("角色名:", "角色姓名", "林尘"),
                ("性格关键词:", "用逗号分隔", "坚韧、善良、执着"),
                ("特殊设定:", "角色的独特之处", "身负神秘血脉之力"),
            ],
            "user_template": "角色定位：{0}\n角色名：{1}\n性格关键词：{2}\n特殊设定：{3}\n\n请为我设计一份详细的角色卡。",
        },
        "continue_write": {
            "title": "✍️ 智能续写",
            "system_prompt": "你是一位小说续写专家。请基于用户提供的上文内容，以完全相同的风格、人称和叙事视角继续往下写。保持文风一致，情节连贯，字数在300-500字之间。",
            "fields": [
                ("上文内容:", "将自动填入编辑器中的内容", ""),
                ("续写方向提示（可选）:", "如：战斗场景 / 对话 / 转折", "自然的剧情推进"),
            ],
            "user_template": "上文内容：\n{0}\n\n续写方向：{1}\n\n请以上述风格继续往下写。",
            "auto_fill_editor": True,
        },
        "polish": {
            "title": "✨ 润色优化",
            "system_prompt": "你是一位专业的文字润色专家。请优化用户提供的文字，提升流畅度和表现力，修正语病和不自然的表达，同时保持原文的风格和意思不变。直接输出优化后的文本。",
            "fields": [
                ("待润色文本:", "将自动填入编辑器选中的文本或当前段落", ""),
                ("润色方向:", "如：更流畅 / 更华丽 / 更简洁", "更流畅自然"),
            ],
            "user_template": "待润色文本：\n{0}\n\n润色方向：{1}\n\n请优化以上文本。",
            "auto_fill_editor": True,
        },
        "dialogue": {
            "title": "💬 对话生成",
            "system_prompt": "你是一位对话写作专家。请根据用户提供的角色设定和场景，生成一段自然生动、符合角色性格的对话。对话要体现角色各自的语气、用词习惯和性格特点。",
            "fields": [
                ("角色A:", "姓名 + 性格特点", "林尘（沉稳冷静）"),
                ("角色B:", "姓名 + 性格特点", "苏瑶（活泼开朗）"),
                ("场景:", "对话发生的场景", "两人在月下庭院相遇"),
                ("对话主题:", "对话围绕什么展开", "关于即将到来的试炼"),
            ],
            "user_template": "角色A：{0}\n角色B：{1}\n场景：{2}\n对话主题：{3}\n\n请根据以上设定生成一段对话。",
        },
    }

    def __init__(self, feature_key, parent=None, editor_text=""):
        super().__init__(parent)
        self.feature_key = feature_key
        self.feature = self.FEATURES[feature_key]
        self.editor_text = editor_text
        self._input_widgets = []
        self._worker = None
        self._theme_colors = None  # 由外部 apply_theme 设置

        self.setWindowTitle(self.feature["title"])
        self.setMinimumSize(580, 620)
        self.setStyleSheet("""
            QDialog {
                background-color: #0A0E17;
            }
        """)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # 标题
        title = QLabel(self.feature["title"])
        title.setStyleSheet("color: #EAECEF; font-size: 18px; font-weight: 700;")
        layout.addWidget(title)

        # 滚动区域（输入字段）
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(8)

        for i, (label_text, placeholder, default) in enumerate(self.feature["fields"]):
            field_label = QLabel(label_text)
            field_label.setStyleSheet("color: #848E9C; font-size: 12px; font-weight: 500;")
            scroll_layout.addWidget(field_label)

            if "自动填入" in label_text or "上文" in label_text:
                input_widget = QTextEdit()
                input_widget.setPlaceholderText(placeholder)
                input_widget.setFixedHeight(120)
                input_widget.setStyleSheet("""
                    QTextEdit {
                        background-color: rgba(255,255,255,0.04);
                        color: #EAECEF;
                        border: 1px solid rgba(255,255,255,0.06);
                        border-radius: 6px;
                        padding: 8px 12px;
                        font-size: 13px;
                    }
                    QTextEdit:focus { border-color: #4D7CFE; }
                """)
                if self.feature.get("auto_fill_editor") and self.editor_text:
                    input_widget.setPlainText(self.editor_text)
            else:
                input_widget = QLineEdit()
                input_widget.setPlaceholderText(placeholder)
                input_widget.setFixedHeight(36)
                input_widget.setStyleSheet("""
                    QLineEdit {
                        background-color: rgba(255,255,255,0.04);
                        color: #EAECEF;
                        border: 1px solid rgba(255,255,255,0.06);
                        border-radius: 6px;
                        padding: 0 12px;
                        font-size: 13px;
                    }
                    QLineEdit:focus { border-color: #4D7CFE; }
                    QLineEdit::placeholder { color: #5A6270; }
                """)
                if default:
                    input_widget.setText(default)

            self._input_widgets.append(input_widget)
            scroll_layout.addWidget(input_widget)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        # 生成按钮
        self._btn_generate = QPushButton("✨ 开始生成")
        self._btn_generate.setFixedHeight(40)
        self._btn_generate.setStyleSheet("""
            QPushButton {
                background-color: #4D7CFE;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #3D6CF0; }
            QPushButton:disabled { background-color: #2B3139; color: #5A6270; }
        """)
        self._btn_generate.clicked.connect(self._generate)
        layout.addWidget(self._btn_generate)

        # 输出区域
        output_label = QLabel("生成结果:")
        output_label.setStyleSheet("color: #848E9C; font-size: 12px; font-weight: 500;")
        layout.addWidget(output_label)

        self._output_text = QTextEdit()
        self._output_text.setReadOnly(True)
        self._output_text.setPlaceholderText("点击「开始生成」后，结果将显示在这里...")
        self._output_text.setMinimumHeight(160)
        self._output_text.setStyleSheet("""
            QTextEdit {
                background-color: rgba(255,255,255,0.03);
                color: #EAECEF;
                border: 1px solid rgba(255,255,255,0.06);
                border-radius: 6px;
                padding: 12px;
                font-size: 13px;
            }
        """)
        layout.addWidget(self._output_text)

        # 底部操作按钮
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        self._btn_insert = QPushButton("📥 插入到编辑器")
        self._btn_insert.setFixedHeight(36)
        self._btn_insert.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #EAECEF;
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 6px;
                font-size: 13px;
                padding: 0 16px;
            }
            QPushButton:hover { background-color: rgba(77,124,254,0.15); border-color: #4D7CFE; color: #4D7CFE; }
        """)
        self._btn_insert.clicked.connect(self._insert_to_editor)
        btn_layout.addWidget(self._btn_insert)

        self._btn_copy = QPushButton("📋 复制到剪贴板")
        self._btn_copy.setFixedHeight(36)
        self._btn_copy.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #848E9C;
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 6px;
                font-size: 13px;
                padding: 0 16px;
            }
            QPushButton:hover { border-color: rgba(255,255,255,0.2); color: #EAECEF; }
        """)
        self._btn_copy.clicked.connect(self._copy_to_clipboard)
        btn_layout.addWidget(self._btn_copy)

        btn_layout.addStretch()

        btn_close = QPushButton("关闭")
        btn_close.setFixedHeight(36)
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #848E9C;
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 6px;
                font-size: 13px;
                padding: 0 16px;
            }
            QPushButton:hover { border-color: rgba(255,255,255,0.2); color: #EAECEF; }
        """)
        btn_close.clicked.connect(self.close)
        btn_layout.addWidget(btn_close)

        layout.addLayout(btn_layout)

    def _get_input_values(self):
        values = []
        for w in self._input_widgets:
            if isinstance(w, QTextEdit):
                values.append(w.toPlainText().strip())
            else:
                values.append(w.text().strip())
        return values

    def _generate(self):
        values = self._get_input_values()
        if not values[0]:
            QMessageBox.warning(self, "提示", "请至少填写第一个输入字段")
            return

        if not ai_api.is_api_configured():
            reply = QMessageBox.question(
                self, "AI 未配置",
                "尚未配置 AI 模型，是否前往设置？",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                dialog = AiSettingsDialog(self)
                if self._theme_colors:
                    dialog.apply_theme(self._theme_colors)
                dialog.exec()
                if not ai_api.is_api_configured():
                    return
            else:
                return

        # 禁用按钮，显示加载状态
        self._btn_generate.setEnabled(False)
        self._btn_generate.setText("⏳ 生成中...")
        self._output_text.setPlainText("正在请求 AI 模型，请稍候...")

        # 构建消息
        system_prompt = self.feature["system_prompt"]
        user_prompt = self.feature["user_template"].format(*values)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        # 启动后台线程
        self._worker = AiGenerateThread(messages, self)
        self._worker.result_ready.connect(self._on_result_ready)
        self._worker.error_occurred.connect(self._on_error_occurred)
        self._worker.finished.connect(self._on_generation_finished)
        self._worker.start()

    def _on_result_ready(self, result):
        """API 成功返回结果"""
        self._output_text.setPlainText(result)

    def _on_error_occurred(self, error_msg):
        """API 调用出错"""
        self._output_text.setPlainText(f"❌ {error_msg}")

    def _on_generation_finished(self):
        """生成完成（无论成功或失败），恢复按钮状态"""
        self._btn_generate.setEnabled(True)
        self._btn_generate.setText("✨ 开始生成")
        self._worker = None

    def _insert_to_editor(self):
        text = self._output_text.toPlainText()
        if not text or text.startswith("❌"):
            return
        if self.parent() and hasattr(self.parent(), 'insert_ai_result'):
            self.parent().insert_ai_result(text)
            self.close()
        else:
            self._copy_to_clipboard()
            QMessageBox.information(self, "提示", "内容已复制到剪贴板，可在编辑器中粘贴")

    def _copy_to_clipboard(self):
        text = self._output_text.toPlainText()
        if text and not text.startswith("❌"):
            from PySide6.QtGui import QClipboard
            QApplication.clipboard().setText(text)
            self._btn_copy.setText("✅ 已复制")
            QTimer.singleShot(1500, lambda: self._btn_copy.setText("📋 复制到剪贴板"))

    def apply_theme(self, colors):
        """应用主题色以适配深色/浅色模式"""
        self._theme_colors = colors
        is_light = int(colors['bg'].lstrip('#')[:2], 16) > 128

        if is_light:
            bg_color = '#F5F5F7'
            text_color = '#1D1D1F'
            sub_color = '#6E6E73'
            muted_color = '#8B8D98'
            input_bg = '#FFFFFF'
            border_color = '#E5E5EA'
            placeholder_color = '#8B8D98'
            btn_border = '#D1D1D6'
            btn_hover_border = '#BBBBC3'
        else:
            bg_color = '#0A0E17'
            text_color = '#EAECEF'
            sub_color = '#848E9C'
            muted_color = '#5A6270'
            input_bg = 'rgba(255,255,255,0.04)'
            border_color = 'rgba(255,255,255,0.06)'
            placeholder_color = '#5A6270'
            btn_border = 'rgba(255,255,255,0.1)'
            btn_hover_border = 'rgba(255,255,255,0.2)'

        # 对话框背景
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {bg_color};
            }}
        """)

        # 更新滚动区域 viewport 背景（修复黑框）
        for sa in self.findChildren(QScrollArea):
            sa.setStyleSheet(f"""
                QScrollArea {{
                    border: none;
                    background-color: transparent;
                }}
            """)
            vp = sa.viewport()
            if vp:
                vp.setStyleSheet(f"background-color: transparent;")
            # 滚动条样式
            sa.setStyleSheet(sa.styleSheet() + f"""
                QScrollBar:vertical {{
                    background-color: transparent;
                    width: 6px;
                    border-radius: 3px;
                }}
                QScrollBar::handle:vertical {{
                    background-color: {placeholder_color};
                    border-radius: 3px;
                    min-height: 30px;
                }}
            """)

        # 更新所有 QLabel
        for lbl in self.findChildren(QLabel):
            ss = lbl.styleSheet()
            if 'font-size: 18px' in ss or 'font-weight: 700' in ss:
                lbl.setStyleSheet(
                    f"color: {text_color}; font-size: 18px; font-weight: 700;"
                )
            elif 'font-weight: 500' in ss:
                lbl.setStyleSheet(
                    f"color: {sub_color}; font-size: 12px; font-weight: 500;"
                )
            else:
                lbl.setStyleSheet(
                    f"color: {sub_color}; font-size: 12px;"
                )

        # 更新输入控件
        for w in self._input_widgets:
            if isinstance(w, QLineEdit):
                w.setStyleSheet(f"""
                    QLineEdit {{
                        background-color: {input_bg};
                        color: {text_color};
                        border: 1px solid {border_color};
                        border-radius: 6px;
                        padding: 0 12px;
                        font-size: 13px;
                    }}
                    QLineEdit:focus {{ border-color: #4D7CFE; }}
                    QLineEdit::placeholder {{ color: {placeholder_color}; }}
                """)
            elif isinstance(w, QTextEdit):
                w.setStyleSheet(f"""
                    QTextEdit {{
                        background-color: {input_bg};
                        color: {text_color};
                        border: 1px solid {border_color};
                        border-radius: 6px;
                        padding: 8px 12px;
                        font-size: 13px;
                    }}
                    QTextEdit:focus {{ border-color: #4D7CFE; }}
                """)

        # 输出文本区域
        self._output_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {input_bg};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 6px;
                padding: 12px;
                font-size: 13px;
            }}
        """)

        # 次要按钮（插入到编辑器）
        self._btn_insert.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {text_color};
                border: 1px solid {btn_border};
                border-radius: 6px;
                font-size: 13px;
                padding: 0 16px;
            }}
            QPushButton:hover {{
                background-color: rgba(77,124,254,0.15);
                border-color: #4D7CFE;
                color: #4D7CFE;
            }}
        """)

        # 复制/关闭按钮样式
        btn_tertiary_style = f"""
            QPushButton {{
                background-color: transparent;
                color: {sub_color};
                border: 1px solid {btn_border};
                border-radius: 6px;
                font-size: 13px;
                padding: 0 16px;
            }}
            QPushButton:hover {{
                border-color: {btn_hover_border};
                color: {text_color};
            }}
        """
        self._btn_copy.setStyleSheet(btn_tertiary_style)
        # 更新关闭按钮（查找第一个未自定义的 QPushButton）
        for btn in self.findChildren(QPushButton):
            ss = btn.styleSheet()
            if 'color: #FFFFFF' not in ss and 'color: #4D7CFE' not in ss:
                btn.setStyleSheet(btn_tertiary_style)

    def closeEvent(self, event):
        """关闭对话框时确保线程已终止"""
        if self._worker and self._worker.isRunning():
            self._worker.terminate()
            self._worker.wait(3000)
        event.accept()
