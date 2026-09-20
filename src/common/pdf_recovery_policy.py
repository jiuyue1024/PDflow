"""Deterministic review policy for existing recovery diagnostics.

The reliability band is a policy state derived from typed issues.  It is not a
statistical confidence score and does not gate export.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List

from src.common.pdf_recovery_models import RecoveryIssue, RecoveryResult


@dataclass(frozen=True)
class ReviewPolicyDecision:
    review_required: bool
    reliability_band: str
    review_reason_codes: List[str] = field(default_factory=list)
    review_summaries: List[str] = field(default_factory=list)


_SUMMARY_TEMPLATES: Dict[str, str] = {
    "MULTIPLE_TABLE_CANDIDATES": "Multiple table candidates detected on page {page}.",
    "LAYOUT_FALLBACK_USED": "Positioned-word/layout fallback was used on page {page}.",
    "OCR_USED": "OCR was used to recover values on page {page}.",
    "CROSS_PAGE_SCHEMA_MISMATCH": "Adjacent pages may not share the same table structure.",
    "ROW_SHAPE_INCONSISTENCY": "Row structure varies significantly in one recovered table.",
    "POSSIBLE_INCOMPLETE_RECOVERY": "Additional structured content may not be included in this recovered result.",
    "UNKNOWN_SOURCE_PAGE": "Some recovered values cannot be linked to a source page.",
    "EMPTY_RECOVERY": "No usable structured recovery was produced after structured recovery was attempted.",
}


def _page_label(issue: RecoveryIssue) -> str:
    return str(issue.page_number) if issue.page_number is not None else "some pages"


def _unknown_values_are_material(issue: RecoveryIssue) -> bool:
    """Escalate only when the evidence says attribution loss is substantial."""
    evidence = issue.evidence or {}
    return evidence.get("prevents_verification") is True


def evaluate_review_policy(issues: Iterable[RecoveryIssue]) -> ReviewPolicyDecision:
    issues = list(issues)
    review_required = False
    unusable = False
    has_caution = False
    reason_codes: List[str] = []
    summaries: List[str] = []

    for issue in issues:
        if issue.code not in reason_codes and issue.severity != "info":
            reason_codes.append(issue.code)
        template = _SUMMARY_TEMPLATES.get(issue.code)
        if template:
            summary = template.format(page=_page_label(issue))
            if summary not in summaries:
                summaries.append(summary)

        if issue.severity == "critical":
            review_required = True
            unusable = True
        elif issue.severity == "review":
            review_required = True
        elif issue.severity == "warning":
            has_caution = True
            if issue.code == "UNKNOWN_SOURCE_PAGE" and _unknown_values_are_material(issue):
                review_required = True
        elif issue.severity == "info":
            # OCR/layout usage is context, not evidence of incorrect output.
            has_caution = True

    if unusable:
        band = "unusable"
    elif review_required:
        band = "review_required"
    elif has_caution:
        band = "caution"
    else:
        band = "clear"

    return ReviewPolicyDecision(
        review_required=review_required,
        reliability_band=band,
        review_reason_codes=reason_codes,
        review_summaries=summaries,
    )


def apply_review_policy(result: RecoveryResult) -> RecoveryResult:
    """Apply policy fields to a sidecar without changing recovered content."""
    decision = evaluate_review_policy(result.issues)
    result.review_required = decision.review_required
    result.reliability_band = decision.reliability_band
    result.review_reason_codes = decision.review_reason_codes
    result.review_summaries = decision.review_summaries
    result.structural_confidence = None
    return result
