# -*- coding: utf-8 -*-
"""
ai_text_processor.py — 印流PDflow AI 文本处理抽象接口

⚠️ V1.1 状态：仅保留接口，具体实现延期至 V1.2

设计原则：
    1. 定义统一的 AI 文本处理接口（AITextProvider）
    2. 业务层（pdf_api / 模板渲染）只依赖抽象接口
    3. V1.1 期间所有调用都抛出 NotImplementedError 提示用户功能未启用
    4. V1.2 接入真实 API 时，无需修改业务层代码

V1.2 计划接入能力：
    - 文本摘要（summary）
    - 重点提取（key_points）
    - Markdown 输出
    - Word 文档输出
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional


# ================================================================
# 数据模型
# ================================================================

@dataclass
class SummaryResult:
    """摘要结果"""
    summary: str                       # 摘要正文
    key_points: List[str] = field(default_factory=list)  # 重点列表
    word_count: int = 0                # 原文字数
    summary_word_count: int = 0        # 摘要字数
    language: str = "zh"               # 识别到的语言
    duration_sec: float = 0.0          # 耗时（秒）


@dataclass
class MarkdownResult:
    """Markdown 转换结果"""
    markdown: str                      # Markdown 内容
    headings: List[str] = field(default_factory=list)  # 标题列表
    images_extracted: int = 0          # 提取的图片数
    duration_sec: float = 0.0


@dataclass
class WordResult:
    """Word 文档输出结果"""
    output_path: str                   # 输出文件路径
    pages_converted: int = 0           # 转换页数
    duration_sec: float = 0.0


# ================================================================
# 异常类
# ================================================================

class AITextError(Exception):
    """AI 文本处理通用异常基类"""
    pass


class AINotImplementedError(AITextError):
    """AI 文本处理功能未实现（V1.1 状态）"""
    pass


class AIInputError(AITextError):
    """AI 输入参数错误"""
    pass


# ================================================================
# 抽象接口
# ================================================================

class AITextProvider(ABC):
    """
    AI 文本处理提供者抽象基类

    V1.1 期间所有方法都抛出 NotImplementedError。
    V1.2 接入时，继承此类实现具体服务（OpenAI / Claude / 本地模型等）。
    """

    # 支持的文件扩展名
    SUPPORTED_EXTS = (".pdf", ".docx", ".txt", ".md")

    @abstractmethod
    def summarize(
        self,
        text: str,
        max_words: int = 200,
        language: str = "zh",
        progress_callback=None,
    ) -> SummaryResult:
        """
        生成文本摘要。

        Args:
            text: 待摘要文本
            max_words: 摘要最大词数
            language: 输出语言（zh/en/auto）
            progress_callback: 可选进度回调

        Returns:
            SummaryResult 对象
        """
        raise NotImplementedError(
            "AI 文本摘要功能延期至 V1.2 接入，V1.1 暂不提供。"
        )

    @abstractmethod
    def extract_key_points(
        self,
        text: str,
        max_points: int = 5,
        language: str = "zh",
        progress_callback=None,
    ) -> List[str]:
        """
        提取文本重点。

        Args:
            text: 待提取文本
            max_points: 最多返回的重点数
            language: 输出语言

        Returns:
            重点字符串列表
        """
        raise NotImplementedError(
            "AI 重点提取功能延期至 V1.2 接入，V1.1 暂不提供。"
        )

    @abstractmethod
    def to_markdown(
        self,
        filepath: str,
        output_path: Optional[str] = None,
        progress_callback=None,
    ) -> MarkdownResult:
        """
        将 PDF/Word 文档转换为 Markdown。

        Args:
            filepath: 源文件路径（.pdf / .docx）
            output_path: 可选，Markdown 输出路径
            progress_callback: 进度回调

        Returns:
            MarkdownResult 对象
        """
        raise NotImplementedError(
            "Markdown 转换功能延期至 V1.2 接入，V1.1 暂不提供。"
        )

    @abstractmethod
    def to_word(
        self,
        filepath: str,
        output_path: str,
        progress_callback=None,
    ) -> WordResult:
        """
        将 PDF 转换为 Word 文档（含 AI 优化排版）。

        Args:
            filepath: 源 PDF 路径
            output_path: 输出 Word 路径
            progress_callback: 进度回调

        Returns:
            WordResult 对象
        """
        raise NotImplementedError(
            "AI Word 优化输出功能延期至 V1.2 接入，V1.1 暂不提供。"
        )

    def get_provider_name(self) -> str:
        """返回当前 AI 服务提供商名称（子类重写）"""
        return "AITextProvider (未实现)"


# ================================================================
# 占位实现
# ================================================================

class StubAITextProvider(AITextProvider):
    """
    AI 文本处理占位实现

    V1.1 期间所有调用都抛出 AINotImplementedError，
    用于在 UI 层给出友好提示。
    """

    def get_provider_name(self) -> str:
        return "StubAITextProvider (V1.1 占位)"

    def summarize(self, text, max_words=200, language="zh", progress_callback=None):
        raise AINotImplementedError(
            "AI 文本摘要功能将在 V1.2 版本中提供。\n"
            "当前版本仅保留接口，暂不支持自动摘要。\n\n"
            "如需此功能，请关注官方更新：\n"
            "https://github.com/jiuyue1024/PDflow-/releases"
        )

    def extract_key_points(self, text, max_points=5, language="zh", progress_callback=None):
        raise AINotImplementedError(
            "AI 重点提取功能将在 V1.2 版本中提供。"
        )

    def to_markdown(self, filepath, output_path=None, progress_callback=None):
        raise AINotImplementedError(
            "Markdown 转换功能将在 V1.2 版本中提供。"
        )

    def to_word(self, filepath, output_path, progress_callback=None):
        raise AINotImplementedError(
            "AI Word 优化输出功能将在 V1.2 版本中提供。"
        )


# ================================================================
# 工厂函数
# ================================================================

_default_provider: Optional[AITextProvider] = None


def get_default_ai_text_provider() -> AITextProvider:
    """
    获取默认 AI 文本处理提供者

    V1.1 期间返回 StubAITextProvider（占位实现）。
    V1.2 接入真实 API 后，此处返回 OpenAITextProvider / ClaudeTextProvider 等。
    """
    global _default_provider
    if _default_provider is None:
        _default_provider = StubAITextProvider()
    return _default_provider


def reset_default_ai_text_provider():
    """重置默认 AI 提供者（V1.2 接入时用于重新初始化）"""
    global _default_provider
    _default_provider = None


# ================================================================
# 便捷函数（业务层调用入口）
# ================================================================

def summarize_text(
    text: str,
    max_words: int = 200,
    language: str = "zh",
    progress_callback=None,
) -> SummaryResult:
    """生成文本摘要（便捷函数）"""
    provider = get_default_ai_text_provider()
    return provider.summarize(
        text=text,
        max_words=max_words,
        language=language,
        progress_callback=progress_callback,
    )


def extract_key_points(
    text: str,
    max_points: int = 5,
    language: str = "zh",
    progress_callback=None,
) -> List[str]:
    """提取文本重点（便捷函数）"""
    provider = get_default_ai_text_provider()
    return provider.extract_key_points(
        text=text,
        max_points=max_points,
        language=language,
        progress_callback=progress_callback,
    )


def convert_to_markdown(
    filepath: str,
    output_path: Optional[str] = None,
    progress_callback=None,
) -> MarkdownResult:
    """转换为 Markdown（便捷函数）"""
    provider = get_default_ai_text_provider()
    return provider.to_markdown(
        filepath=filepath,
        output_path=output_path,
        progress_callback=progress_callback,
    )


def convert_to_word(
    filepath: str,
    output_path: str,
    progress_callback=None,
) -> WordResult:
    """转换为 Word（便捷函数）"""
    provider = get_default_ai_text_provider()
    return provider.to_word(
        filepath=filepath,
        output_path=output_path,
        progress_callback=progress_callback,
    )
