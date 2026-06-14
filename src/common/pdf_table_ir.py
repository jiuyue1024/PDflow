# -*- coding: utf-8 -*-
"""
PDF→Excel v1.1-patch 轻量中间结构层（Table IR）

目标：
- 在 pdfplumber 原始输出与 openpyxl Excel 写入之间，建立规范化中间表示
- 保留单元格原始信息（特别是换行符 \\n）
- 为后续 v1.2 OCR+layout 引擎预留扩展点

设计原则（v1.1-patch）：
- 纯数据结构（dataclass + dict）
- 不依赖 pdfplumber / openpyxl（独立可测）
- 向后兼容：v1 的 DataFrame 流程可继续使用 IR 作为入参/出参
"""

from dataclasses import dataclass
from typing import List, Optional, Any, Dict, Union
import re


# ============================================================
# 1. 数据结构定义
# ============================================================
@dataclass
class TableMeta:
    """表格元信息"""
    page: int = 0                # PDF 页码（1-based）
    table_id: int = 0            # 当前页内的表格序号（1-based）
    confidence: float = 1.0      # 提取置信度（0-1，未来 v1.2 OCR 用）
    mode: str = "structured"     # structured / text_fallback / ocr_fallback


@dataclass
class TableBlock:
    """表格中间结构：rows + 可选 spans + meta"""
    rows: List[List[str]]
    spans: Optional[Any] = None   # 未来 v1.2 用于合并单元格 [(r, c, rowspan, colspan), ...]
    meta: Optional[TableMeta] = None

    def to_dict(self) -> Dict:
        """序列化为 dict（便于跨模块传递）"""
        return {
            "rows": self.rows,
            "spans": self.spans,
            "meta": {
                "page": self.meta.page,
                "table_id": self.meta.table_id,
                "confidence": self.meta.confidence,
                "mode": self.meta.mode,
            } if self.meta else None,
        }


# ============================================================
# 2. IR 清洗函数
# ================================================================
def clean_cell(text: Optional[str]) -> str:
    """清洗单元格文本：保留 \\n（关键！v1 强制替换为空格导致多行内容错乱）"""
    if text is None:
        return ""
    text = str(text)
    text = text.replace("\r", "")   # 仅去 \\r，保留 \\n
    return text


_WS_PATTERN = re.compile(r"\s+")


def normalize_table(rows: List[List[Optional[str]]]) -> List[List[str]]:
    """统一清洗整个表格：每行每格 clean_cell"""
    if not rows:
        return []
    return [
        [clean_cell(c) for c in row]
        for row in rows
    ]


# ============================================================
# 3. IR 构造入口
# ============================================================
def to_table_block(
    rows: List[List[Optional[str]]],
    page: int = 0,
    table_id: int = 0,
    confidence: float = 1.0,
    mode: str = "structured",
) -> Dict:
    """构造一个 TableBlock 并以 dict 形式返回（IR 主流形式）

    用法：
        ir = to_table_block(rows=pdfplumber_table, page=1, table_id=1)
        # ir = {"rows": [...], "spans": None, "meta": {...}}
    """
    return TableBlock(
        rows=normalize_table(rows),
        spans=None,
        meta=TableMeta(
            page=page,
            table_id=table_id,
            confidence=confidence,
            mode=mode,
        ),
    ).to_dict()


# ============================================================
# 4. IR 工具函数（供 v1.1-patch 的 pdf_api.py 调用）
# ============================================================
def ir_to_rows(ir: Union[Dict, TableBlock]) -> List[List[str]]:
    """从 IR 抽取 rows（统一 dict 和 dataclass 入参）"""
    if isinstance(ir, TableBlock):
        return ir.rows
    return ir.get("rows", [])


def ir_meta(ir: Union[Dict, TableBlock]) -> Optional[TableMeta]:
    """从 IR 抽取 meta"""
    if isinstance(ir, TableBlock):
        return ir.meta
    meta_dict = ir.get("meta")
    if not meta_dict:
        return None
    return TableMeta(
        page=meta_dict.get("page", 0),
        table_id=meta_dict.get("table_id", 0),
        confidence=meta_dict.get("confidence", 1.0),
        mode=meta_dict.get("mode", "structured"),
    )


def has_newline_cells(rows: List[List[str]]) -> bool:
    """检查表格中是否有含 \\n 的单元格（决定是否启用 wrap_text）"""
    for row in rows:
        for cell in row:
            if cell and "\n" in cell:
                return True
    return False
