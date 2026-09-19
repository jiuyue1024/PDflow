"""Conservative, model-only verification diagnostics for PDF recovery.

This module deliberately does not inspect PDFs or invoke any extraction/OCR
runtime.  It only examines the already-built recovery sidecar.
"""

from __future__ import annotations

from collections import Counter
from typing import Iterable, List, Optional, Sequence, Tuple

from src.common.pdf_recovery_models import RecoveryBlock, RecoveryIssue, RecoveryResult


def _usable_rows(block: RecoveryBlock) -> List[list]:
    return [row for row in block.rows if any(value not in (None, "") for value in row)]


def _effective_width(row: Sequence[object]) -> int:
    """Count columns after removing empty trailing cells only."""
    width = len(row)
    while width and row[width - 1] in (None, ""):
        width -= 1
    return width


def _shape_stats(rows: Sequence[Sequence[object]]) -> Tuple[List[int], float]:
    widths = [_effective_width(row) for row in rows]
    if not widths:
        return [], 0.0
    mode_width, mode_count = Counter(widths).most_common(1)[0]
    mismatch_ratio = (len(widths) - mode_count) / len(widths)
    return widths, mismatch_ratio


def _row_shape_stats(rows: Sequence[Sequence[object]]) -> Tuple[List[int], float]:
    """Measure stored row widths, preserving explicit trailing empty cells."""
    widths = [len(row) for row in rows]
    if not widths:
        return [], 0.0
    _, mode_count = Counter(widths).most_common(1)[0]
    mismatch_ratio = (len(widths) - mode_count) / len(widths)
    return widths, mismatch_ratio


def _header_values(block: RecoveryBlock) -> set[str]:
    rows = _usable_rows(block)
    if not rows:
        return set()
    return {
        str(value).strip() for value in rows[0]
        if value not in (None, "") and str(value).strip()
    }


def _append_route_issues(result: RecoveryResult, issues: List[RecoveryIssue]) -> None:
    for page in result.source_document.pages:
        route = page.routing_decision
        if route is None:
            continue
        if route.candidate_count > 1:
            issues.append(RecoveryIssue(
                code="MULTIPLE_TABLE_CANDIDATES",
                severity="warning",
                page_number=page.page_number,
                message="Multiple native table candidates were exposed for this page.",
                evidence={"candidate_count": route.candidate_count},
            ))
        if route.used_layout_fallback:
            issues.append(RecoveryIssue(
                code="LAYOUT_FALLBACK_USED",
                severity="info",
                page_number=page.page_number,
                message="Positioned-word/layout fallback was used for this page.",
                evidence={"selected_method": route.selected_method},
            ))
        if route.used_ocr:
            issues.append(RecoveryIssue(
                code="OCR_USED",
                severity="info",
                page_number=page.page_number,
                message="OCR produced replacement or recovered rows for this page.",
                evidence={"selected_method": route.selected_method},
            ))


def _append_row_shape_issues(blocks: Iterable[RecoveryBlock], issues: List[RecoveryIssue]) -> None:
    for block in blocks:
        rows = _usable_rows(block)
        if len(rows) < 3:
            continue
        widths, mismatch_ratio = _row_shape_stats(rows)
        if not widths or len(set(widths)) <= 1:
            continue
        # Require both a material width difference and repeated variation. A
        # single short row is not enough evidence of a structural problem.
        if max(widths) - min(widths) >= 2 and mismatch_ratio >= 0.4:
            issues.append(RecoveryIssue(
                code="ROW_SHAPE_INCONSISTENCY",
                severity="review",
                page_number=block.page_number if block.page_number > 0 else None,
                block_id=block.block_id,
                message="Recovered rows have materially inconsistent column shapes.",
                evidence={
                    "observed_column_counts": widths,
                    "row_count": len(rows),
                    "mismatch_ratio": round(mismatch_ratio, 4),
                },
            ))


def _append_cross_page_issues(blocks: Sequence[RecoveryBlock], issues: List[RecoveryIssue]) -> None:
    comparable = [
        block for block in blocks
        if block.page_number > 0 and block.block_type == "table" and len(_usable_rows(block)) >= 2
    ]
    comparable.sort(key=lambda block: (block.page_number, block.block_id))
    for previous, current in zip(comparable, comparable[1:]):
        if current.page_number != previous.page_number + 1:
            continue
        if previous.method != current.method:
            continue
        previous_header = _header_values(previous)
        current_header = _header_values(current)
        if not previous_header or not current_header:
            continue
        overlap = len(previous_header & current_header) / min(
            len(previous_header), len(current_header)
        )
        # One shared generic column is not strong enough evidence that two
        # adjacent tables are a continuation. Require substantial header
        # agreement before comparing schemas.
        if overlap < 0.75:
            continue
        previous_widths, _ = _shape_stats(_usable_rows(previous))
        current_widths, _ = _shape_stats(_usable_rows(current))
        previous_schema = max(previous_widths, default=0)
        current_schema = max(current_widths, default=0)
        if previous_schema == current_schema:
            continue
        mismatch_ratio = abs(previous_schema - current_schema) / max(
            previous_schema, current_schema, 1
        )
        issues.append(RecoveryIssue(
            code="CROSS_PAGE_SCHEMA_MISMATCH",
            severity="review",
            page_number=current.page_number,
            message="Comparable adjacent table blocks have inconsistent column schemas.",
            evidence={
                "affected_pages": [previous.page_number, current.page_number],
                "observed_column_counts": [previous_schema, current_schema],
                "mismatch_ratio": round(mismatch_ratio, 4),
                "header_overlap": round(overlap, 4),
            },
        ))


def _append_unknown_page_issues(blocks: Iterable[RecoveryBlock], issues: List[RecoveryIssue]) -> None:
    for block in blocks:
        rows = _usable_rows(block)
        unknown_cells = sum(
            1 for cell in block.cells
            if cell.value not in (None, "") and cell.source_page is None
        )
        if block.page_number <= 0 and rows:
            unknown_cells = max(unknown_cells, sum(len(row) for row in rows))
        if not rows or not unknown_cells:
            continue
        issues.append(RecoveryIssue(
            code="UNKNOWN_SOURCE_PAGE",
            severity="warning",
            page_number=block.page_number if block.page_number > 0 else None,
            block_id=block.block_id,
            message="Recovered values exist without a reliable source page attribution.",
            evidence={"row_count": len(rows), "unknown_cell_count": unknown_cells},
        ))


def collect_recovery_issues(result: RecoveryResult) -> List[RecoveryIssue]:
    """Return deterministic diagnostics for an already-built sidecar."""
    issues: List[RecoveryIssue] = []
    _append_route_issues(result, issues)
    _append_row_shape_issues(result.blocks, issues)
    _append_cross_page_issues(result.blocks, issues)
    _append_unknown_page_issues(result.blocks, issues)

    structured_attempted = any(
        page.routing_decision is not None and (
            page.routing_decision.candidate_count > 0
            or page.routing_decision.selected_method in {
                "native_table", "layout_fallback", "ocr"
            }
            or page.routing_decision.used_ocr
            or page.routing_decision.used_layout_fallback
        )
        for page in result.source_document.pages
    )
    if (
        structured_attempted
        and not any(_usable_rows(block) for block in result.blocks)
        and result.source_document.pages
    ):
        issues.append(RecoveryIssue(
            code="EMPTY_RECOVERY",
            severity="critical",
            message="The recovery sidecar contains no usable recovered rows.",
            evidence={"page_count": result.source_document.page_count},
        ))
    return issues


def verify_recovery_result(result: RecoveryResult) -> RecoveryResult:
    """Populate issues/review_required without calculating confidence."""
    from src.common.pdf_recovery_policy import apply_review_policy

    result.issues = collect_recovery_issues(result)
    return apply_review_policy(result)
