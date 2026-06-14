# -*- coding: utf-8 -*-
"""
error_handler.py — 印流PDflow 统一错误处理模块
提供错误分类、友好提示、风格化错误对话框和便捷安全执行函数
AI 生成，已审查 2026-06-03
"""

import traceback
from enum import Enum

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QSizePolicy,
)

from src.common.theme import get_colors


# ================================================================
# ErrorType — 错误类型枚举
# ================================================================
class ErrorType(Enum):
    """错误分类枚举，用于区分不同来源的异常"""
    PDF_PARSE_ERROR = "pdf_parse"         # PDF 解析/读取失败
    FILE_NOT_FOUND = "file_not_found"     # 文件不存在或无法访问
    FILE_FORMAT_ERROR = "file_format"     # 不支持的文件格式
    BATCH_PARTIAL_FAILURE = "batch_partial"  # 批量操作部分失败
    AI_TIMEOUT = "ai_timeout"             # AI API 调用超时
    AI_SERVICE_ERROR = "ai_service"       # AI 服务不可用
    NETWORK_ERROR = "network"             # 网络连接问题
    PERMISSION_ERROR = "permission"       # 文件权限被拒绝
    DISK_SPACE_ERROR = "disk_space"       # 磁盘空间不足
    UNKNOWN_ERROR = "unknown"             # 未分类错误


# ================================================================
# 错误类型 → 用户友好信息映射
# ================================================================
_ERROR_MESSAGES = {
    ErrorType.PDF_PARSE_ERROR: "PDF 文件解析失败，文件可能已损坏或格式不正确",
    ErrorType.FILE_NOT_FOUND: "找不到指定文件，请检查文件路径是否正确",
    ErrorType.FILE_FORMAT_ERROR: "不支持的文件格式，请选择正确的文件类型",
    ErrorType.BATCH_PARTIAL_FAILURE: "批量操作部分文件处理失败",
    ErrorType.AI_TIMEOUT: "AI 服务响应超时，请稍后重试",
    ErrorType.AI_SERVICE_ERROR: "AI 服务暂时不可用，请稍后重试",
    ErrorType.NETWORK_ERROR: "网络连接异常，请检查网络设置",
    ErrorType.PERMISSION_ERROR: "文件访问被拒绝，请检查文件权限",
    ErrorType.DISK_SPACE_ERROR: "磁盘空间不足，请清理后重试",
    ErrorType.UNKNOWN_ERROR: "发生了未知错误",
}


# ================================================================
# ErrorDialog — 风格化错误对话框
# ================================================================
class ErrorDialog(QDialog):
    """统一风格的错误对话框，支持深色/浅色主题"""

    def __init__(self, title="错误", message="", details="",
                 parent=None, theme_colors=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(420)
        self.setMaximumWidth(560)

        # 主题色
        self._colors = theme_colors or get_colors()
        c = self._colors

        # 对话框背景
        self.setStyleSheet(
            f"QDialog {{\n"
            f"    background-color: {c['card_bg']};\n"
            f"    border: 1px solid {c['border']};\n"
            f"    border-radius: 12px;\n"
            f"}}"
        )
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowContextHelpButtonHint
        )

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # ── 顶部：图标 + 标题行 ──
        top_row = QHBoxLayout()
        top_row.setSpacing(12)

        icon_label = QLabel("⚠️")
        icon_label.setFixedSize(32, 32)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 24px; background: transparent;")
        top_row.addWidget(icon_label)

        title_label = QLabel(title)
        title_label.setStyleSheet(
            f"color: {c['error']}; font-size: 16px; font-weight: 600;"
            f" background: transparent;"
        )
        top_row.addWidget(title_label, stretch=1)
        layout.addLayout(top_row)

        # ── 消息正文 ──
        msg_label = QLabel(message)
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet(
            f"color: {c['text_main']}; font-size: 14px;"
            f" background: transparent;"
        )
        layout.addWidget(msg_label)

        # ── 可展开的详细信息 ──
        if details:
            self._details_text = QTextEdit()
            self._details_text.setReadOnly(True)
            self._details_text.setPlainText(details)
            self._details_text.setMaximumHeight(150)
            self._details_text.setVisible(False)
            self._details_text.setStyleSheet(
                f"QTextEdit {{\n"
                f"    background-color: {c['input_bg']};\n"
                f"    border: 1px solid {c['border_light']};\n"
                f"    border-radius: 6px;\n"
                f"    color: {c['text_sub']};\n"
                f"    font-family: 'Consolas', 'Courier New', monospace;\n"
                f"    font-size: 12px;\n"
                f"    padding: 8px;\n"
                f"}}"
            )
            layout.addWidget(self._details_text)

            # 展开按钮
            self._toggle_btn = QPushButton("显示详细信息 ▼")
            self._toggle_btn.setObjectName("errorToggleBtn")
            self._toggle_btn.setStyleSheet(
                f"QPushButton#errorToggleBtn {{\n"
                f"    background-color: transparent;\n"
                f"    color: {c['primary']};\n"
                f"    border: none;\n"
                f"    font-size: 13px;\n"
                f"    padding: 4px 0;\n"
                f"}}\n"
                f"QPushButton#errorToggleBtn:hover {{\n"
                f"    color: {c['primary_hover']};\n"
                f"}}"
            )
            self._toggle_btn.clicked.connect(self._toggle_details)
            layout.addWidget(self._toggle_btn)

        # ── 确定按钮 ──
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        ok_btn = QPushButton("确定")
        ok_btn.setObjectName("errorOkBtn")
        ok_btn.setFixedWidth(100)
        ok_btn.setStyleSheet(
            f"QPushButton#errorOkBtn {{\n"
            f"    background-color: {c['primary']};\n"
            f"    color: #FFFFFF;\n"
            f"    border: none;\n"
            f"    border-radius: 6px;\n"
            f"    font-size: 14px;\n"
            f"    font-weight: 500;\n"
            f"    padding: 8px 24px;\n"
            f"    min-height: 36px;\n"
            f"}}\n"
            f"QPushButton#errorOkBtn:hover {{\n"
            f"    background-color: {c['primary_hover']};\n"
            f"}}"
        )
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)
        layout.addLayout(btn_layout)

    def _toggle_details(self):
        """切换详细信息的显示/隐藏"""
        if self._details_text.isVisible():
            self._details_text.setVisible(False)
            self._toggle_btn.setText("显示详细信息 ▼")
        else:
            self._details_text.setVisible(True)
            self._toggle_btn.setText("隐藏详细信息 ▲")

    def apply_theme(self, colors):
        """外部主题切换时更新对话框样式"""
        self._colors = colors
        c = colors
        self.setStyleSheet(
            f"QDialog {{\n"
            f"    background-color: {c['card_bg']};\n"
            f"    border: 1px solid {c['border']};\n"
            f"    border-radius: 12px;\n"
            f"}}"
        )


# ================================================================
# ErrorHandler — 统一错误处理工具类
# ================================================================
class ErrorHandler:
    """提供静态方法用于各类错误的统一处理和用户提示"""

    @staticmethod
    def classify_error(exception: Exception) -> ErrorType:
        """根据异常类型自动分类错误

        Args:
            exception: 捕获到的异常对象

        Returns:
            对应的 ErrorType 枚举值
        """
        msg = str(exception).lower()
        exc_type = type(exception).__name__.lower()

        # 文件不存在
        if exc_type in ("filenotfounderror",) or "no such file" in msg:
            return ErrorType.FILE_NOT_FOUND

        # 权限错误
        if exc_type in ("permissionerror",) or "permission" in msg or "access denied" in msg:
            return ErrorType.PERMISSION_ERROR

        # 磁盘空间
        if "no space" in msg or "disk full" in msg:
            return ErrorType.DISK_SPACE_ERROR

        # 网络错误
        if exc_type in ("connectionerror", "timeouterror") or \
           "timeout" in msg or "connection" in msg or "network" in msg:
            return ErrorType.NETWORK_ERROR

        # PDF 解析错误（PyMuPDF / fitz 异常）
        if "pdf" in msg or "fitz" in msg or "page" in msg or \
           exc_type in ("runtimerror", "valueerror") and "pdf" in msg:
            return ErrorType.PDF_PARSE_ERROR

        # 文件格式
        if "format" in msg or "unsupported" in msg or "invalid" in msg:
            return ErrorType.FILE_FORMAT_ERROR

        return ErrorType.UNKNOWN_ERROR

    @staticmethod
    def handle_pdf_error(exception: Exception, parent_widget=None):
        """处理 PDF 相关错误，显示友好提示

        Args:
            exception: 捕获到的异常
            parent_widget: 父控件，用于对话框定位
        """
        error_type = ErrorHandler.classify_error(exception)
        user_msg = _ERROR_MESSAGES.get(error_type, _ERROR_MESSAGES[ErrorType.UNKNOWN_ERROR])
        details = f"{type(exception).__name__}: {str(exception)}"

        ErrorHandler.show_error_dialog(
            title="PDF 处理错误",
            message=user_msg,
            details=details,
            parent_widget=parent_widget,
        )

    @staticmethod
    def handle_batch_error(results: list, parent_widget=None):
        """处理批量操作结果中的部分失败

        Args:
            results: 批量结果列表，每项为 dict，包含 success/error 等字段
            parent_widget: 父控件
        """
        total = len(results)
        failed = [r for r in results if not r.get("success", True)]
        success_count = total - len(failed)

        if not failed:
            return  # 全部成功，无需提示

        if success_count == 0:
            message = f"全部 {total} 个文件处理失败"
        else:
            message = f"共 {total} 个文件，成功 {success_count} 个，失败 {len(failed)} 个"

        # 拼接失败详情
        detail_lines = []
        for i, r in enumerate(failed):
            name = r.get("file", r.get("input_path", f"文件#{i+1}"))
            err = r.get("error", "未知错误")
            detail_lines.append(f"• {name}: {err}")
        details = "\n".join(detail_lines)

        ErrorHandler.show_error_dialog(
            title="批量操作结果",
            message=message,
            details=details,
            parent_widget=parent_widget,
        )

    @staticmethod
    def handle_ai_error(exception: Exception, parent_widget=None):
        """处理 AI/超时相关错误

        Args:
            exception: 捕获到的异常
            parent_widget: 父控件
        """
        msg = str(exception).lower()
        if "timeout" in msg or "timed out" in msg:
            error_type = ErrorType.AI_TIMEOUT
        else:
            error_type = ErrorType.AI_SERVICE_ERROR

        user_msg = _ERROR_MESSAGES.get(error_type, _ERROR_MESSAGES[ErrorType.UNKNOWN_ERROR])
        details = f"{type(exception).__name__}: {str(exception)}"

        ErrorHandler.show_error_dialog(
            title="AI 服务错误",
            message=user_msg,
            details=details,
            parent_widget=parent_widget,
        )

    @staticmethod
    def show_error_dialog(title="错误", message="", details="",
                          parent_widget=None, theme_colors=None):
        """显示风格化错误对话框

        Args:
            title: 对话框标题
            message: 用户友好的错误描述
            details: 技术细节（可展开查看）
            parent_widget: 父控件
            theme_colors: 主题色字典，为 None 时自动获取当前主题
        """
        colors = theme_colors or get_colors()
        dlg = ErrorDialog(
            title=title,
            message=message,
            details=details,
            parent=parent_widget,
            theme_colors=colors,
        )
        dlg.exec()

    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """将字节数格式化为人类可读的大小字符串

        Args:
            size_bytes: 字节数

        Returns:
            格式化后的字符串，如 "1.5 MB"
        """
        if size_bytes < 0:
            return "0 B"
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / 1024 / 1024:.2f} MB"
        else:
            return f"{size_bytes / 1024 / 1024 / 1024:.2f} GB"


# ================================================================
# safe_execute — 便捷安全执行函数
# ================================================================
def safe_execute(func, *args, error_type=ErrorType.UNKNOWN_ERROR,
                 parent=None, **kwargs):
    """安全执行函数，自动捕获异常并显示用户提示

    Args:
        func: 要执行的函数
        *args: 位置参数
        error_type: 预期的错误类型，用于选择处理方式
        parent: 父控件，用于对话框定位
        **kwargs: 关键字参数

    Returns:
        函数执行结果，异常时返回 None
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        # 根据错误类型选择对应的处理方法
        if error_type in (ErrorType.PDF_PARSE_ERROR, ErrorType.FILE_NOT_FOUND,
                          ErrorType.FILE_FORMAT_ERROR, ErrorType.PERMISSION_ERROR,
                          ErrorType.DISK_SPACE_ERROR):
            ErrorHandler.handle_pdf_error(e, parent_widget=parent)
        elif error_type in (ErrorType.AI_TIMEOUT, ErrorType.AI_SERVICE_ERROR):
            ErrorHandler.handle_ai_error(e, parent_widget=parent)
        elif error_type == ErrorType.BATCH_PARTIAL_FAILURE:
            # 批量错误需要传入 results 列表
            ErrorHandler.show_error_dialog(
                title="批量操作错误",
                message=str(e),
                parent_widget=parent,
            )
        else:
            ErrorHandler.show_error_dialog(
                title="操作失败",
                message=_ERROR_MESSAGES.get(error_type, "发生了未知错误"),
                details=f"{type(e).__name__}: {str(e)}",
                parent_widget=parent,
            )
        return None
