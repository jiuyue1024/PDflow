# -*- coding: utf-8 -*-
"""
PDF Layout → Row 结构重建层（v1.1-patch P0 Hotfix）

解决问题：
- 旧 fallback 路径（page.extract_text() + split("\\n")）丢失坐标信息
- Excel 输出全部挤入 A 列（电话/邮箱/地址无法识别为独立行）

提供：
- cluster_by_y: 行聚类（按 y 坐标阈值）
- parse_layout_blocks: 主入口，按阅读顺序构建二维 rows
- 语义拆分：phone/email/url 强制独立成 row
- 严格禁止 page.extract_text() 和 text.split("\\n") 主路径
"""

import re
from typing import List, Dict, Any, Optional, Union


# ============================================================
# 1. 语义 token 正则（phone / email / url）
# ============================================================
# 电话：至少 7 位数字，可含 + - 空格
PHONE_PATTERN = re.compile(r'\+?\d[\d\-\s]{6,}\d')
# 邮箱：基础邮箱格式
EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}')
# URL：http/https/www 开头
URL_PATTERN = re.compile(r'(?:https?://|www\.)[^\s]+', re.IGNORECASE)


# ============================================================
# 2. 兼容 dict / object / 索引 三种 word 访问风格
# ============================================================
def _w_get(w: Any, key: str, default: Any = None) -> Any:
    """统一从 word 中读取字段，同时支持：
    - dict 风格（真实 pdfplumber 行为）：w.get("top")
    - object 风格（MockWord / namedtuple）：w.top
    - 索引风格：w["top"]

    这样既能在生产环境（pdfplumber 返回 dict）使用，
    也能在单测中用 MockWord 这样的 object 风格验证。
    """
    # 1) dict 优先（最快路径，也是真实 pdfplumber 路径）
    if isinstance(w, dict):
        return w.get(key, default)
    # 2) object 属性
    try:
        return getattr(w, key)
    except AttributeError:
        pass
    # 3) 索引（__getitem__）
    try:
        return w[key]
    except (KeyError, TypeError, IndexError, AttributeError):
        return default


# ============================================================
# 3. 行聚类（cluster_by_y）
# ============================================================
def cluster_by_y(blocks: List[Any], threshold: float = 3.0) -> List[List[Any]]:
    """按 y 坐标聚类（从上到下）

    入参：blocks 应该已经按 y 降序排序（同 y 按 x 升序）
    返回：lines，每 line 是同一 y 范围内的 block 列表

    threshold: 同行的 y 差值容忍（pt），默认 3pt
    """
    if not blocks:
        return []

    lines = []
    current_line = [blocks[0]]
    current_top = _w_get(blocks[0], "top", 0) or 0

    for b in blocks[1:]:
        top = _w_get(b, "top", 0) or 0
        if abs(top - current_top) > threshold:
            lines.append(current_line)
            current_line = [b]
            current_top = top
        else:
            current_line.append(b)

    if current_line:
        lines.append(current_line)

    return lines


# ============================================================
# 3. 语义 token 拆分
# ============================================================
def _is_special_token(text: str) -> bool:
    """判断文本是否包含 phone/email/url"""
    if not text:
        return False
    return bool(
        PHONE_PATTERN.search(text)
        or EMAIL_PATTERN.search(text)
        or URL_PATTERN.search(text)
    )


def _split_by_special_tokens(text: str) -> List[str]:
    """按 phone/email/url 拆分文本，每个 token 独立成 row

    例：
        "张三 13812345678 邮箱 zhang@x.com"
        → ["张三", "13812345678", "zhang@x.com"]

    例：
        "电话: +86-138-1234-5678 / 邮箱: a@b.com"
        → ["电话: +86-138-1234-5678", "/", "邮箱: a@b.com"]  （每行独立）
    """
    if not _is_special_token(text):
        return [text]

    # 找到所有 special token 位置
    matches = []
    for pattern in (PHONE_PATTERN, EMAIL_PATTERN, URL_PATTERN):
        for m in pattern.finditer(text):
            matches.append((m.start(), m.end()))

    if not matches:
        return [text]

    # 合并重叠区间
    matches.sort()
    merged = [matches[0]]
    for start, end in matches[1:]:
        if start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))

    # 拆分
    result = []
    last_end = 0
    for start, end in merged:
        pre = text[last_end:start].strip()
        if pre:
            result.append(pre)
        token = text[start:end].strip()
        if token:
            result.append(token)
        last_end = end
    rest = text[last_end:].strip()
    if rest:
        result.append(rest)

    return result if result else [text]


# ============================================================
# 4. 主入口：parse_layout_blocks
# ============================================================
def parse_layout_blocks(page) -> List[List[str]]:
    """P0 Hotfix 主入口：PDF page → 二维 rows（按阅读顺序）

    流程：
    1. page.extract_words(x_tolerance=3, y_tolerance=3) 拿带坐标的 words
    2. 按 y 降序排序（同 y 按 x 升序）
    3. 行聚类（threshold=3pt）
    4. 每行内：按 x 升序拼接 words
    5. 语义拆分：phone/email/url 独立成 row

    返回：List[List[str]] 二维 rows（每行通常是单列）

    禁止：
    - page.extract_text() 调用（丢失坐标）
    - text.split("\\n") 调用（破坏阅读顺序）
    """
    try:
        words = page.extract_words(x_tolerance=3, y_tolerance=3)
    except Exception:
        return []

    if not words:
        return []

    # 1. 按 y 降序排序（同 y 按 x 升序）
    sorted_words = sorted(words, key=lambda w: (-_w_get(w, "top", 0) or 0, _w_get(w, "x0", 0) or 0))

    # 2. 行聚类
    lines = cluster_by_y(sorted_words, threshold=3.0)

    # 3. 每行拼接 + 语义拆分
    rows = []
    for line in lines:
        sorted_line = sorted(line, key=lambda w: _w_get(w, "x0", 0) or 0)
        text = " ".join(str(_w_get(w, "text", "") or "") for w in sorted_line).strip()
        if not text:
            continue
        # 4. 语义拆分：phone/email/url 独立成 row
        split_rows = _split_by_special_tokens(text)
        for sr in split_rows:
            if sr:
                rows.append([sr])

    return rows


# ============================================================
# 5. 兼容旧 API
# ============================================================
def parse_layout_rows(page) -> List[Dict[str, Any]]:
    """parse_layout_blocks 的 DataFrame 兼容版本

    返回：[{"内容": "..."}, ...] 格式（与 _extract_page_words 旧 API 兼容）

    用于：在 _extract_page_best 内部表格提取失败时回退
    """
    rows = parse_layout_blocks(page)
    return [{"内容": r[0]} for r in rows if r]
