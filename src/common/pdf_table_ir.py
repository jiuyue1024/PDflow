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


# ============================================================
# 5. P0 Hotfix: 统一输出协议（v1.1-patch Excel crash 修复）
# ============================================================
def safe_list(x):
    """安全转 list：兼容 pandas Series / DataFrame / ndarray / 原生 list

    禁止直接调用 .tolist()（DataFrame.tolist() 不存在，Series.tolist() 可能因
    DataFrame 伪装成 Series 而崩溃）。本函数统一处理：

    - pd.Series → .tolist()
    - pd.DataFrame → .values.tolist()（二维 list）
    - numpy ndarray → .tolist()
    - list → 原样返回
    - 其他 → list()
    """
    # pandas DataFrame（有 values 和 columns 和 fillna）
    if hasattr(x, "columns") and hasattr(x, "fillna"):
        return x.values.tolist()
    # pandas Series（有 values 但没有 columns）
    if hasattr(x, "values") and hasattr(x, "tolist"):
        return x.tolist()
    # numpy ndarray
    if hasattr(x, "tolist"):
        return x.tolist()
    # 原生 list
    if isinstance(x, list):
        return x
    # 其他可迭代
    try:
        return list(x)
    except TypeError:
        return [x]


def to_dataframe(ir_or_rows):
    """IR / rows → pandas.DataFrame 统一入口

    支持入参：
    - TableBlock dataclass
    - dict IR {"rows": [...], "spans": ..., "meta": ...}
    - list of list（裸 rows）
    - pandas.DataFrame（透传）
    """
    # 1. 已经是 DataFrame
    if hasattr(ir_or_rows, "values") and hasattr(ir_or_rows, "columns") and hasattr(ir_or_rows, "fillna"):
        return ir_or_rows

    # 2. TableBlock dataclass
    if isinstance(ir_or_rows, TableBlock):
        import pandas as pd
        return pd.DataFrame(ir_or_rows.rows)

    # 3. dict IR
    if isinstance(ir_or_rows, dict) and "rows" in ir_or_rows:
        import pandas as pd
        return pd.DataFrame(ir_or_rows["rows"])

    # 4. 裸 list of list
    if isinstance(ir_or_rows, list):
        import pandas as pd
        return pd.DataFrame(ir_or_rows)

    raise Exception(f"Unsupported Excel input type: {type(ir_or_rows).__name__}")


def normalize_excel_input(result):
    """P0 Hotfix: 统一 IR / DataFrame / list 结构 → DataFrame

    Excel 写入层只接受 pandas.DataFrame，禁止任何路径直接调用 df.tolist()

    支持入参：
    - 有 to_dataframe 方法的对象
    - dict IR
    - 已经是 pandas DataFrame
    - 裸 list of list
    """
    # 1) 有 to_dataframe 方法的对象（IR dataclass）
    if hasattr(result, "to_dataframe") and callable(getattr(result, "to_dataframe", None)):
        return result.to_dataframe()

    # 2) dict IR
    if isinstance(result, dict) and "rows" in result:
        return to_dataframe(result)

    # 3) 已经是 DataFrame（通过特征属性判断，避免 isinstance 对 import 未加载 pandas 的情况报错）
    if hasattr(result, "values") and hasattr(result, "columns") and hasattr(result, "fillna"):
        return result

    # 4) 裸 list of list
    if isinstance(result, list) and (not result or isinstance(result[0], (list, str))):
        return to_dataframe(result)

    raise Exception(f"normalize_excel_input: unsupported type: {type(result).__name__}")


# 给 TableBlock 加 to_dataframe 方法
def _tableblock_to_dataframe(self) -> "pd.DataFrame":
    """TableBlock.to_dataframe()：IR → DataFrame"""
    return to_dataframe(self)


TableBlock.to_dataframe = _tableblock_to_dataframe


# ============================================================
# 6. Fallback 工厂（统一 fallback 返回结构）
# ============================================================
def fallback_block(rows: List[List[str]], page: int = 0, table_id: int = 0,
                   confidence: float = 0.5) -> Dict:
    """fallback 统一返回 IR dict（带 mode="text_fallback"）

    禁止 fallback 返回 DataFrame + IR 混合类型
    """
    return to_table_block(
        rows=rows,
        page=page,
        table_id=table_id,
        confidence=confidence,
        mode="text_fallback",
    )
