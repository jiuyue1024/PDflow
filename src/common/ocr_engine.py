# common/ocr_engine.py — 印流PDflow OCR引擎封装
# 支持 PaddleOCR（优先）和 Tesseract（回退），从PDF扫描件/图片提取文字

import os
import logging

logger = logging.getLogger(__name__)


class OCREngine:
    """OCR 引擎，支持 PaddleOCR（优先）和 Tesseract（回退）"""

    def __init__(self):
        self._paddle_available = False
        self._tesseract_available = False
        self._engine_name = "none"
        self._paddle_ocr = None
        self._check_engines()

    def _check_engines(self):
        """检测可用的 OCR 引擎"""
        # 尝试导入 PaddleOCR
        try:
            from paddleocr import PaddleOCR
            self._paddle_available = True
            self._engine_name = "paddleocr"
            logger.info("OCR引擎检测: PaddleOCR 可用")
        except ImportError:
            logger.info("OCR引擎检测: PaddleOCR 不可用")
        except Exception as e:
            logger.warning(f"OCR引擎检测: PaddleOCR 初始化异常 - {e}")

        # 如果 PaddleOCR 不可用，尝试 Tesseract
        if not self._paddle_available:
            try:
                import pytesseract
                # 检查 tesseract 可执行文件是否存在
                pytesseract.get_tesseract_version()
                self._tesseract_available = True
                self._engine_name = "tesseract"
                logger.info("OCR引擎检测: Tesseract 可用")
            except ImportError:
                logger.info("OCR引擎检测: Tesseract 不可用（未安装 pytesseract）")
            except Exception as e:
                logger.info(f"OCR引擎检测: Tesseract 不可用 - {e}")

        if self._engine_name == "none":
            logger.warning("OCR引擎检测: 无可用引擎，请安装 PaddleOCR 或 Tesseract")

    @property
    def available(self) -> bool:
        """是否有可用的 OCR 引擎"""
        return self._engine_name != "none"

    @property
    def engine_name(self) -> str:
        """当前使用的引擎名称"""
        return self._engine_name

    def _get_paddle_ocr(self):
        """懒加载 PaddleOCR 实例（首次调用时初始化，避免启动时卡顿）"""
        if self._paddle_ocr is None:
            try:
                from paddleocr import PaddleOCR
                self._paddle_ocr = PaddleOCR(
                    use_angle_cls=True,
                    lang='ch',
                    show_log=False,
                )
            except Exception as e:
                logger.error(f"PaddleOCR 初始化失败: {e}")
                self._paddle_available = False
                # 回退到 Tesseract
                if self._tesseract_available:
                    self._engine_name = "tesseract"
                else:
                    self._engine_name = "none"
                return None
        return self._paddle_ocr

    def extract_text_from_pdf(self, pdf_path: str, progress_callback=None) -> dict:
        """从 PDF 扫描件提取文字

        Args:
            pdf_path: PDF 文件路径
            progress_callback: callable(current_page, total_pages, status_text)

        Returns:
            {
                "status": "ok",
                "text": "提取的完整文本",
                "pages": [{"page_num": 1, "text": "页面文本", "confidence": 0.95}],
                "engine": "paddleocr" | "tesseract",
                "total_pages": 10,
            }
        """
        if not self.available:
            return {
                "status": "error",
                "message": "未安装 OCR 引擎，请安装 PaddleOCR 或 Tesseract",
            }

        # 校验文件路径
        if not os.path.isfile(pdf_path):
            return {
                "status": "error",
                "message": f"文件不存在: {pdf_path}",
            }

        ext = os.path.splitext(pdf_path)[1].lower()
        if ext != ".pdf":
            return {
                "status": "error",
                "message": f"不支持的文件格式: {ext}，仅支持 PDF 文件",
            }

        try:
            # 将 PDF 渲染为图片列表
            images = self._pdf_to_images(pdf_path)
            total_pages = len(images)

            if total_pages == 0:
                return {
                    "status": "error",
                    "message": "PDF 文件为空或无法读取",
                }

            all_text = []
            pages_result = []

            for i, img in enumerate(images):
                page_num = i + 1

                if progress_callback:
                    progress_callback(page_num, total_pages, f"正在识别第 {page_num}/{total_pages} 页")

                try:
                    if self._engine_name == "paddleocr":
                        text, confidence = self._extract_with_paddle(img)
                    else:
                        text, confidence = self._extract_with_tesseract(img)
                except Exception as e:
                    logger.warning(f"第 {page_num} 页 OCR 识别失败: {e}")
                    text = ""
                    confidence = 0.0

                all_text.append(text)
                pages_result.append({
                    "page_num": page_num,
                    "text": text,
                    "confidence": round(confidence, 4),
                })

            return {
                "status": "ok",
                "text": "\n".join(all_text),
                "pages": pages_result,
                "engine": self._engine_name,
                "total_pages": total_pages,
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"PDF OCR 识别失败: {e}",
            }

    def extract_text_from_image(self, image_path: str) -> dict:
        """从图片提取文字

        Args:
            image_path: 图片文件路径

        Returns:
            {
                "status": "ok",
                "text": "提取的文本",
                "confidence": 0.95,
                "engine": "paddleocr" | "tesseract",
            }
        """
        if not self.available:
            return {
                "status": "error",
                "message": "未安装 OCR 引擎，请安装 PaddleOCR 或 Tesseract",
            }

        if not os.path.isfile(image_path):
            return {
                "status": "error",
                "message": f"文件不存在: {image_path}",
            }

        # 校验图片扩展名
        valid_exts = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif", ".webp"}
        ext = os.path.splitext(image_path)[1].lower()
        if ext not in valid_exts:
            return {
                "status": "error",
                "message": f"不支持的图片格式: {ext}",
            }

        try:
            from PIL import Image
            img = Image.open(image_path)
            # 转为 RGB 模式（部分引擎不支持 RGBA）
            if img.mode == "RGBA":
                background = Image.new("RGB", img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background
            elif img.mode != "RGB":
                img = img.convert("RGB")

            if self._engine_name == "paddleocr":
                text, confidence = self._extract_with_paddle(img)
            else:
                text, confidence = self._extract_with_tesseract(img)

            return {
                "status": "ok",
                "text": text,
                "confidence": round(confidence, 4),
                "engine": self._engine_name,
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"图片 OCR 识别失败: {e}",
            }

    def _extract_with_paddle(self, image) -> tuple:
        """使用 PaddleOCR 提取文字，返回 (text, confidence)"""
        ocr = self._get_paddle_ocr()
        if ocr is None:
            # PaddleOCR 初始化失败，尝试回退到 Tesseract
            if self._tesseract_available:
                return self._extract_with_tesseract(image)
            raise RuntimeError("PaddleOCR 不可用且无回退引擎")

        import numpy as np
        # PaddleOCR 接受 numpy 数组或图片路径
        if hasattr(image, 'save'):
            # PIL Image 转 numpy 数组
            img_array = np.array(image)
        else:
            img_array = image

        result = ocr.ocr(img_array, cls=True)

        if not result or not result[0]:
            return ("", 0.0)

        texts = []
        confidences = []

        for line in result[0]:
            if line and len(line) >= 2:
                text = line[1][0] if isinstance(line[1], (list, tuple)) else str(line[1])
                conf = line[1][1] if isinstance(line[1], (list, tuple)) and len(line[1]) >= 2 else 0.0
                texts.append(text)
                confidences.append(conf)

        full_text = "\n".join(texts)
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        return (full_text, avg_confidence)

    def _extract_with_tesseract(self, image) -> tuple:
        """使用 Tesseract 提取文字，返回 (text, confidence)"""
        import pytesseract

        # Tesseract 中文+英文识别
        text = pytesseract.image_to_string(image, lang='chi_sim+eng')

        # 获取置信度数据
        try:
            data = pytesseract.image_to_data(image, lang='chi_sim+eng', output_type=pytesseract.Output.DICT)
            confidences = [int(c) for c in data['conf'] if int(c) > 0]
            avg_confidence = sum(confidences) / len(confidences) / 100.0 if confidences else 0.0
        except Exception:
            avg_confidence = 0.0

        return (text.strip(), avg_confidence)

    def _pdf_to_images(self, pdf_path: str) -> list:
        """将 PDF 页面渲染为 PIL Image 列表（用于 OCR）"""
        import fitz
        from PIL import Image
        import io

        images = []
        doc = fitz.open(pdf_path)

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            # 使用 200 DPI 渲染，兼顾识别精度和速度
            zoom = 200 / 72.0
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat, alpha=False)

            # 转为 PIL Image
            img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            images.append(img)

        doc.close()
        return images


# ============================================================
# 模块级单例与快捷函数
# ============================================================
_ocr_engine = None


def get_ocr_engine() -> OCREngine:
    """获取 OCR 引擎单例"""
    global _ocr_engine
    if _ocr_engine is None:
        _ocr_engine = OCREngine()
    return _ocr_engine


def extract_text_from_pdf(pdf_path: str, progress_callback=None) -> dict:
    """快捷函数：从 PDF 提取文字"""
    engine = get_ocr_engine()
    if not engine.available:
        return {"status": "error", "message": "未安装 OCR 引擎，请安装 PaddleOCR 或 Tesseract"}
    return engine.extract_text_from_pdf(pdf_path, progress_callback)


def extract_text_from_image(image_path: str) -> dict:
    """快捷函数：从图片提取文字"""
    engine = get_ocr_engine()
    if not engine.available:
        return {"status": "error", "message": "未安装 OCR 引擎"}
    return engine.extract_text_from_image(image_path)


def is_ocr_available() -> bool:
    """检查 OCR 是否可用"""
    return get_ocr_engine().available
