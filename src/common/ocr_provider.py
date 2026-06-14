# -*- coding: utf-8 -*-
"""
ocr_provider.py — 印流PDflow OCR 抽象接口

⚠️ V1.1 状态：仅保留接口，具体实现延期至 V1.2

设计原则：
    1. 定义统一的 OCR 提供者接口（OCRProvider）
    2. 具体的 OCR 引擎（PaddleOCR / Tesseract / 云服务等）作为子类实现
    3. 业务层（pdf_api / 模板渲染 / AI 文本处理）只依赖抽象接口
    4. V1.1 期间所有调用都抛出 NotImplementedError 提示用户功能未启用
    5. V1.2 接入真实实现时，无需修改业务层代码

使用示例（V1.2 接入后）：
    from src.common.ocr_provider import get_default_ocr_provider

    provider = get_default_ocr_provider()
    result = provider.extract_text("scan.pdf", language="ch")
    print(result.text)        # 提取的纯文本
    print(result.pages)       # 按页分组的文字列表
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional


# ================================================================
# 数据模型
# ================================================================

@dataclass
class OCRPage:
    """单页 OCR 结果"""
    page_no: int                       # 页码（从 1 开始）
    text: str                          # 该页提取的纯文本
    confidence: float = 0.0            # 平均置信度（0.0-1.0）
    blocks: List[dict] = field(default_factory=list)  # 文本块列表（坐标 + 内容）


@dataclass
class OCRResult:
    """OCR 识别结果"""
    text: str                          # 全文拼接后的纯文本
    pages: List[OCRPage] = field(default_factory=list)  # 按页分组的结果
    language: str = ""                 # 识别使用的语言
    engine: str = ""                   # 使用的 OCR 引擎名称
    total_pages: int = 0               # 总页数
    duration_sec: float = 0.0          # 耗时（秒）


# ================================================================
# 异常类
# ================================================================

class OCRError(Exception):
    """OCR 通用异常基类"""
    pass


class OCRNotImplementedError(OCRError):
    """OCR 功能未实现（V1.1 状态）"""
    pass


class OCRFileError(OCRError):
    """OCR 文件读取错误"""
    pass


class OCRLanguageError(OCRError):
    """OCR 语言不支持错误"""
    pass


# ================================================================
# 抽象接口
# ================================================================

class OCRProvider(ABC):
    """
    OCR 提供者抽象基类

    V1.1 期间所有方法都抛出 NotImplementedError，提示用户功能延期至 V1.2。
    V1.2 接入时，继承此类实现具体引擎（PaddleOCR / Tesseract / 云服务等）。
    """

    # 支持的文件扩展名白名单
    SUPPORTED_EXTS = (".pdf", ".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp")

    # 支持的语言代码
    SUPPORTED_LANGUAGES = ("ch", "en", "ch_en", "japan", "korean")

    @abstractmethod
    def extract_text(
        self,
        filepath: str,
        language: str = "ch",
        progress_callback=None,
    ) -> OCRResult:
        """
        从 PDF / 图片文件中提取文字。

        Args:
            filepath: 文件路径（.pdf / .png / .jpg / ...）
            language: 识别语言，默认中文（"ch"）
            progress_callback: 可选进度回调，签名 (current_page, total_pages, status_text)

        Returns:
            OCRResult 对象，包含全文和分页结果

        Raises:
            OCRError: 识别过程中的通用错误
        """
        raise NotImplementedError(
            "OCR 功能延期至 V1.2 接入，V1.1 暂不提供实际识别能力。"
        )

    def is_supported(self, filepath: str) -> bool:
        """检查文件格式是否支持"""
        import os
        ext = os.path.splitext(filepath)[1].lower()
        return ext in self.SUPPORTED_EXTS

    def get_engine_name(self) -> str:
        """返回当前 OCR 引擎名称（子类重写）"""
        return "OCRProvider (未实现)"


# ================================================================
# 占位实现
# ================================================================

class StubOCRProvider(OCRProvider):
    """
    OCR 占位实现

    V1.1 期间所有调用都会抛出 OCRNotImplementedError，
    用于在 UI 层给出友好提示，而不是直接崩溃。
    """

    def get_engine_name(self) -> str:
        return "StubOCRProvider (V1.1 占位)"

    def extract_text(
        self,
        filepath: str,
        language: str = "ch",
        progress_callback=None,
    ) -> OCRResult:
        raise OCRNotImplementedError(
            "OCR 文字识别功能将在 V1.2 版本中提供。\n"
            "当前版本仅保留接口，暂不支持扫描件文字提取。\n\n"
            "如需此功能，请关注官方更新：\n"
            "https://github.com/jiuyue1024/PDflow-/releases"
        )


# ================================================================
# 工厂函数
# ================================================================

_default_provider: Optional[OCRProvider] = None


def get_default_ocr_provider() -> OCRProvider:
    """
    获取默认 OCR 提供者实例

    V1.1 期间返回 StubOCRProvider（占位实现）。
    V1.2 接入真实引擎后，此处返回 PaddleOCRProvider 或 TesseractProvider。
    """
    global _default_provider
    if _default_provider is None:
        _default_provider = StubOCRProvider()
    return _default_provider


def reset_default_ocr_provider():
    """重置默认 OCR 提供者（V1.2 接入时用于重新初始化）"""
    global _default_provider
    _default_provider = None


# ================================================================
# 便捷函数（业务层调用入口）
# ================================================================

def extract_text_from_pdf(
    filepath: str,
    language: str = "ch",
    progress_callback=None,
) -> OCRResult:
    """
    从 PDF 扫描件提取文字（便捷函数）

    V1.1 期间调用此函数会抛出 OCRNotImplementedError。
    V1.2 接入后此函数可直接使用，无需修改业务层代码。

    Args:
        filepath: PDF 文件路径
        language: 识别语言
        progress_callback: 进度回调

    Returns:
        OCRResult 对象
    """
    provider = get_default_ocr_provider()
    return provider.extract_text(
        filepath=filepath,
        language=language,
        progress_callback=progress_callback,
    )


def extract_text_from_image(
    filepath: str,
    language: str = "ch",
    progress_callback=None,
) -> OCRResult:
    """
    从图片提取文字（便捷函数）

    V1.1 期间调用此函数会抛出 OCRNotImplementedError。
    """
    provider = get_default_ocr_provider()
    return provider.extract_text(
        filepath=filepath,
        language=language,
        progress_callback=progress_callback,
    )
