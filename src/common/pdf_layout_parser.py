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
import statistics as _stats
from typing import List, Dict, Any, Optional, Union, Tuple


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
    current_top = _w_get(blocks[0], "top", 0) if _w_get(blocks[0], "top") is not None else 0

    for b in blocks[1:]:
        top = _w_get(b, "top", 0) if _w_get(b, "top") is not None else 0
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
# 3b. Word 去重 + CJK 辅助（v1.1-patch3 新增）
# ============================================================
def _is_cjk_char(c: str) -> bool:
    """判断字符是否为 CJK 字符（汉字/标点/全角）"""
    cp = ord(c)
    return (0x4E00 <= cp <= 0x9FFF      # CJK 统一汉字
            or 0x3000 <= cp <= 0x303F    # CJK 标点
            or 0xFF00 <= cp <= 0xFFEF    # 全角 ASCII
            or 0x3400 <= cp <= 0x4DBF    # CJK 扩展 A
            or 0xAC00 <= cp <= 0xD7AF)   # 韩文


def _cjk_display_width(s: str) -> float:
    """计算字符串显示宽度（CJK 字符=2，其他=1）"""
    return sum(2.0 if _is_cjk_char(c) else 1.0 for c in s)


def _deduplicate_words(words: List[Any], overlap_ratio: float = 0.5) -> List[Any]:
    """去除空间重叠的 word 对象（v1.1-patch3: 修复 PDF 注释层/重复文本导致的乱码交叉）

    pdfplumber 对含注释层或重复文本对象的 PDF 会在同一空间区域返回多个重叠 word。
    当这些 word 被同行聚类后交叉拼接，产生乱码文本。

    算法：
    1. 按 (top, x0) 排序
    2. 对每个 word 检查与已 accepted word 的 bbox 重叠
    3. 重叠 > overlap_ratio 时保留文本更长的 word

    返回: 去重后的 word 列表
    """
    if not words:
        return []

    sorted_w = sorted(words, key=lambda w: (
        _w_get(w, "top", 0) if _w_get(w, "top") is not None else 0,
        _w_get(w, "x0", 0) if _w_get(w, "x0") is not None else 0,
    ))

    # accepted: [(word, x0, top, x1, bottom, text), ...]
    accepted: List[tuple] = []

    for w in sorted_w:
        x0 = _w_get(w, "x0", 0) if _w_get(w, "x0") is not None else 0
        top = _w_get(w, "top", 0) if _w_get(w, "top") is not None else 0
        x1_raw = _w_get(w, "x1")
        x1 = x1_raw if x1_raw is not None else x0
        bottom_raw = _w_get(w, "bottom")
        bottom = bottom_raw if bottom_raw is not None else (top + 10)
        text = str(_w_get(w, "text", "") or "")
        if not text:
            continue

        w_area = max((x1 - x0) * (bottom - top), 1.0)
        conflict = False

        for i, (_, ax0, atop, ax1, abottom, atext) in enumerate(accepted):
            x_overlap = max(0.0, min(x1, ax1) - max(x0, ax0))
            y_overlap = max(0.0, min(bottom, abottom) - max(top, atop))
            overlap_area = x_overlap * y_overlap
            a_area = max((ax1 - ax0) * (abottom - atop), 1.0)
            min_area = min(w_area, a_area)

            if min_area > 0 and (overlap_area / min_area) > overlap_ratio:
                conflict = True
                if len(text) > len(atext):
                    accepted[i] = (w, x0, top, x1, bottom, text)
                break

        if not conflict:
            accepted.append((w, x0, top, x1, bottom, text))

    return [item[0] for item in accepted]


# ============================================================
# 4. 行内列聚类（x-gap column detection — v1.1-patch2 保留）
# ============================================================
def _cluster_columns_in_line(
    line_words: List[Any],
    gap_threshold: float = 20.0,
) -> List[str]:
    """行内按 x 间距检测列分隔，禁止将整个行拼为单 cell

    算法：
    1. 按 x0 升序排列 words
    2. 相邻 word 的 x0 - prev_x1 > gap_threshold → 视为列分隔
    3. 每列内 words 以空格拼接

    返回：[col_text_1, col_text_2, ...]（多列字符串列表）

    v1.1-patch2 修复：
    - 旧逻辑：整行拼为单字符串 → 所有内容挤入 A 列
    - 新逻辑：基于 x-gap 拆列，保留 PDF 原始多列结构
    """
    if not line_words:
        return []

    sorted_w = sorted(line_words, key=lambda w: _w_get(w, "x0", 0) if _w_get(w, "x0") is not None else 0)

    columns: List[List[str]] = []
    current_col_words: List[str] = []
    prev_x1: float = -9999.0

    for w in sorted_w:
        x0 = _w_get(w, "x0", 0) if _w_get(w, "x0") is not None else 0
        text = str(_w_get(w, "text", "") or "")
        if not text:
            continue

        # x-gap 超过阈值 → 新列
        if current_col_words and (x0 - prev_x1) > gap_threshold:
            columns.append(current_col_words)
            current_col_words = []

        current_col_words.append(text)
        x1_raw = _w_get(w, "x1")
        x1 = x1_raw if x1_raw is not None else x0
        prev_x1 = x1

    if current_col_words:
        columns.append(current_col_words)

    return [" ".join(col).strip() for col in columns if col]


# ============================================================
# 4b. 全局列检测引擎（v1.1-patch3 新增）
# ============================================================
def _compute_dynamic_gap(all_words: List[Any], cjk_boost: float = 1.5) -> float:
    """基于间距跳跃检测计算动态列分隔阈值（v1.1-patch3 改进）

    算法（间距跳跃检测）：
    1. 收集所有行内相邻 word 的 gap（仅 gap > 0）
    2. 排序后找相邻 gap 之间的最大跳变（gap[i+1] - gap[i]）
    3. 阈值 = 跳变前 gap 与跳变后 gap 的中间值
    4. CJK 占比 > 30% 时乘以 cjk_boost
    5. 下限 8pt，封顶 40pt

    优势：对双峰分布（词内间距 vs 列间距）天然鲁棒，
    不依赖固定系数，CJK/英文混排均可正确识别列分隔。

    返回: 动态 gap 阈值 (float)
    """
    sorted_w = sorted(all_words, key=lambda w: (
        _w_get(w, "top", 0) if _w_get(w, "top") is not None else 0,
        _w_get(w, "x0", 0) if _w_get(w, "x0") is not None else 0,
    ))
    lines = cluster_by_y(sorted_w, threshold=3.0)

    gaps: List[float] = []
    cjk_chars = 0
    total_chars = 0

    for line in lines:
        sorted_line = sorted(line, key=lambda w: _w_get(w, "x0", 0) if _w_get(w, "x0") is not None else 0)
        prev_x1: float = -9999.0
        for w in sorted_line:
            x0 = _w_get(w, "x0", 0) if _w_get(w, "x0") is not None else 0
            x1_raw = _w_get(w, "x1")
            x1 = x1_raw if x1_raw is not None else x0
            text = str(_w_get(w, "text", "") or "")
            total_chars += len(text)
            cjk_chars += sum(1 for c in text if _is_cjk_char(c))

            if prev_x1 > -9000:
                gap = x0 - prev_x1
                if gap > 0:
                    gaps.append(gap)
            prev_x1 = x1

    if not gaps:
        return 20.0

    gaps.sort()

    # 间距跳跃检测：找排序后相邻 gap 之间的最大跳变
    if len(gaps) >= 3:
        max_jump = 0.0
        jump_idx = 0
        for i in range(len(gaps) - 1):
            jump = gaps[i + 1] - gaps[i]
            if jump > max_jump:
                max_jump = jump
                jump_idx = i

        largest_gap = gaps[-1]
        # 仅在最大跳变 > 5pt 且跳变后 gap > 15pt 时使用跳跃检测
        if max_jump > 5.0 and gaps[jump_idx + 1] > 15.0:
            threshold = (gaps[jump_idx] + gaps[jump_idx + 1]) / 2.0
        else:
            # 所有 gap 都很接近 → 无显著列分隔，用最大值 + 余量
            threshold = largest_gap * 1.5
    elif len(gaps) == 2:
        if gaps[1] > gaps[0] * 2.0 and gaps[1] > 15.0:
            threshold = (gaps[0] + gaps[1]) / 2.0
        else:
            threshold = max(gaps) * 1.5
    else:
        threshold = max(gaps[0] * 3.0, 20.0)

    # CJK 修正
    if total_chars > 0 and (cjk_chars / total_chars) > 0.3:
        threshold *= cjk_boost

    # 下限 8pt，封顶 40pt
    return min(max(threshold, 8.0), 40.0)


def _compute_global_columns(
    all_words: List[Any],
    min_support_ratio: float = 0.15,
) -> List[Tuple[float, float]]:
    """从全页 word 计算全局列边界（v1.1-patch3 核心）

    算法：
    1. 用动态阈值扫描所有行，收集列分隔点
    2. 过滤只保留被 >= min_support_ratio 行支持的分隔点
    3. 聚类相近分隔点（< 10pt），取中位数
    4. 生成列区间

    返回: [(x_start, x_end), ...] 全局列边界列表
    """
    gap_threshold = _compute_dynamic_gap(all_words)

    sorted_w = sorted(all_words, key=lambda w: (
        _w_get(w, "top", 0) if _w_get(w, "top") is not None else 0,
        _w_get(w, "x0", 0) if _w_get(w, "x0") is not None else 0,
    ))
    lines = cluster_by_y(sorted_w, threshold=3.0)

    split_points: List[float] = []
    page_left = 99999.0
    page_right = -99999.0

    for line in lines:
        sorted_line = sorted(line, key=lambda w: _w_get(w, "x0", 0) if _w_get(w, "x0") is not None else 0)
        prev_x1: float = -99999.0
        for w in sorted_line:
            x0 = _w_get(w, "x0", 0) if _w_get(w, "x0") is not None else 0
            x1_raw = _w_get(w, "x1")
            x1 = x1_raw if x1_raw is not None else x0
            page_left = min(page_left, x0)
            page_right = max(page_right, x1)
            if prev_x1 > -99000 and (x0 - prev_x1) > gap_threshold:
                split_points.append((prev_x1 + x0) / 2.0)
            prev_x1 = x1

    if not split_points or page_right <= page_left:
        return [(page_left if page_left < 99000 else 0,
                 page_right if page_right > -99000 else 100)]

    total_lines = len(lines)
    min_support = max(2, int(total_lines * min_support_ratio))

    split_points.sort()
    supported: List[float] = []
    i = 0
    while i < len(split_points):
        cluster = [split_points[i]]
        j = i + 1
        while j < len(split_points) and (split_points[j] - cluster[-1]) < 10:
            cluster.append(split_points[j])
            j += 1
        if len(cluster) >= min_support:
            supported.append(_stats.median(cluster))
        i = j

    if not supported:
        return [(page_left, page_right)]

    boundaries = [page_left] + supported + [page_right]
    columns: List[Tuple[float, float]] = []
    for i in range(len(boundaries) - 1):
        columns.append((boundaries[i], boundaries[i + 1]))
    return columns


def _assign_words_to_columns(
    line_words: List[Any],
    global_columns: List[Tuple[float, float]],
) -> List[str]:
    """将一行内的 words 分配到全局列中（v1.1-patch3: 保证列对齐）

    每个 word 取 x_center 找到落入的全局列，同列内按 x0 排序空格拼接。
    空列输出空字符串。

    返回: [col_text_0, col_text_1, ...] 长度 = len(global_columns)
    """
    n_cols = len(global_columns)
    col_buckets: List[List[str]] = [[] for _ in range(n_cols)]

    sorted_w = sorted(line_words, key=lambda w: _w_get(w, "x0", 0) if _w_get(w, "x0") is not None else 0)

    for w in sorted_w:
        x0 = _w_get(w, "x0", 0) if _w_get(w, "x0") is not None else 0
        x1_raw = _w_get(w, "x1")
        x1 = x1_raw if x1_raw is not None else x0
        x_center = (x0 + x1) / 2.0
        text = str(_w_get(w, "text", "") or "")
        if not text:
            continue

        assigned = n_cols - 1
        for ci, (col_start, col_end) in enumerate(global_columns):
            if x_center <= col_end:
                assigned = ci
                break

        col_buckets[assigned].append(text)

    return [" ".join(bucket).strip() for bucket in col_buckets]


# ============================================================
# 5. 主入口：parse_layout_blocks（v1.1-patch3 重构）
# ============================================================
def parse_layout_blocks(page, column_gap_threshold: float = None) -> List[List[str]]:
    """主入口：PDF page -> 二维 rows（全局列对齐 + word 去重）

    v1.1-patch3 重构流程：
    1. extract_words(x_tolerance=3, y_tolerance=3)
    2. _deduplicate_words() -- 去重叠 word（修复乱码交叉文本）
    3. 排序 + 行聚类
    4. _compute_global_columns() -- 全局列边界检测（修复列不对齐）
    5. _assign_words_to_columns() -- 行分配到全局列（修复 CJK 过度分列）
    6. 语义拆分 phone/email/url
    7. 列归一化: 所有行补齐到相同列数

    返回：List[List[str]] 二维 rows（所有行列数一致）

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

    # 1. Word 去重（v1.1-patch3: 修复乱码交叉文本）
    words = _deduplicate_words(words)
    if not words:
        return []

    # 2. 排序 + 行聚类（top 升序 = 从上到下，x0 升序 = 从左到右）
    sorted_words = sorted(words, key=lambda w: (
        _w_get(w, "top", 0) if _w_get(w, "top") is not None else 0,
        _w_get(w, "x0", 0) if _w_get(w, "x0") is not None else 0,
    ))
    lines = cluster_by_y(sorted_words, threshold=3.0)

    # 3. 全局列检测（v1.1-patch3: 修复列不对齐 + CJK 过度分列）
    global_columns = _compute_global_columns(words)

    # 4. 每行分配到全局列 + 语义拆分
    rows: List[List[str]] = []
    for line in lines:
        col_texts = _assign_words_to_columns(line, global_columns)

        # 语义拆分：对每列检查 phone/email/url
        final_cols: List[str] = []
        for ct in col_texts:
            split_parts = _split_by_special_tokens(ct)
            if len(split_parts) == 1:
                final_cols.append(ct)
            else:
                final_cols.extend(split_parts)

        if any(c.strip() for c in final_cols):
            rows.append(final_cols)

    # 5. 列归一化：所有行补齐到相同列数
    if rows:
        max_cols = max(len(r) for r in rows)
        for r in rows:
            while len(r) < max_cols:
                r.append("")

    return rows


# ============================================================
# 6. 兼容旧 API
# ============================================================
def parse_layout_rows(page) -> List[Dict[str, Any]]:
    """parse_layout_blocks 的 DataFrame 兼容版本

    返回：[{"内容": "col1 | col2 | ..."}, ...] 格式（与 _extract_page_words 旧 API 兼容）

    用于：在 _extract_page_best 内部表格提取失败时回退
    """
    rows = parse_layout_blocks(page)
    return [{"内容": " | ".join(c for c in r if c)} for r in rows if r]
