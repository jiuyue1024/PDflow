import json
import unittest

from src.common.pdf_recovery_models import RecoveryIssue, RecoveryResult, SourceDocument
from src.common.pdf_recovery_policy import apply_review_policy, evaluate_review_policy


def _issue(code, severity, evidence=None, page_number=1):
    return RecoveryIssue(
        code=code,
        severity=severity,
        page_number=page_number,
        evidence=evidence,
    )


def _result(issues=None):
    result = RecoveryResult(source_document=SourceDocument(source_path="synthetic.pdf"))
    result.issues = list(issues or [])
    return result


class PdfRecoverySlice2BTests(unittest.TestCase):
    def test_clean_native_result_is_clear(self):
        result = apply_review_policy(_result())
        self.assertEqual("clear", result.reliability_band)
        self.assertFalse(result.review_required)
        self.assertEqual([], result.review_reason_codes)

    def test_valid_ocr_and_layout_are_caution_without_review(self):
        result = apply_review_policy(_result([
            _issue("OCR_USED", "info"),
            _issue("LAYOUT_FALLBACK_USED", "info"),
        ]))
        self.assertEqual("caution", result.reliability_band)
        self.assertFalse(result.review_required)

    def test_multiple_candidates_are_caution_only(self):
        result = apply_review_policy(_result([
            _issue("MULTIPLE_TABLE_CANDIDATES", "warning", {"candidate_count": 2}),
        ]))
        self.assertEqual("caution", result.reliability_band)
        self.assertFalse(result.review_required)

    def test_unknown_source_page_is_caution_by_default(self):
        result = apply_review_policy(_result([
            _issue("UNKNOWN_SOURCE_PAGE", "warning", {"unknown_cell_count": 2}),
        ]))
        self.assertEqual("caution", result.reliability_band)
        self.assertFalse(result.review_required)

    def test_unknown_provenance_requires_explicit_verification_impact(self):
        result = apply_review_policy(_result([
            _issue("UNKNOWN_SOURCE_PAGE", "warning", {"unknown_cell_count": 5}),
        ]))
        self.assertEqual("caution", result.reliability_band)
        self.assertFalse(result.review_required)

        result = apply_review_policy(_result([
            _issue("UNKNOWN_SOURCE_PAGE", "warning", {
                "unknown_cell_count": 5,
                "prevents_verification": True,
            }),
        ]))
        self.assertEqual("review_required", result.reliability_band)
        self.assertTrue(result.review_required)

    def test_row_or_cross_page_issue_requires_review(self):
        result = apply_review_policy(_result([
            _issue("ROW_SHAPE_INCONSISTENCY", "review"),
            _issue("UNKNOWN_SOURCE_PAGE", "warning", {"unknown_cell_count": 1}),
        ]))
        self.assertEqual("review_required", result.reliability_band)
        self.assertTrue(result.review_required)
        self.assertIn("ROW_SHAPE_INCONSISTENCY", result.review_reason_codes)

        result = apply_review_policy(_result([
            _issue("CROSS_PAGE_SCHEMA_MISMATCH", "review"),
        ]))
        self.assertEqual("review_required", result.reliability_band)

    def test_empty_structured_recovery_is_unusable(self):
        result = apply_review_policy(_result([
            _issue("EMPTY_RECOVERY", "critical"),
        ]))
        self.assertEqual("unusable", result.reliability_band)
        self.assertTrue(result.review_required)

    def test_warning_count_does_not_escalate_policy(self):
        result = apply_review_policy(_result([
            _issue("MULTIPLE_TABLE_CANDIDATES", "warning"),
            _issue("UNKNOWN_SOURCE_PAGE", "warning", {"unknown_cell_count": 1}),
            _issue("MULTIPLE_TABLE_CANDIDATES", "warning"),
        ]))
        self.assertEqual("caution", result.reliability_band)
        self.assertFalse(result.review_required)

    def test_combination_with_review_issue_escalates_for_that_issue(self):
        result = apply_review_policy(_result([
            _issue("OCR_USED", "info"),
            _issue("UNKNOWN_SOURCE_PAGE", "warning", {"unknown_cell_count": 1}),
            _issue("CROSS_PAGE_SCHEMA_MISMATCH", "review"),
        ]))
        self.assertTrue(result.review_required)
        self.assertEqual("review_required", result.reliability_band)

    def test_review_summaries_are_factual_and_serializable(self):
        result = apply_review_policy(_result([
            _issue("MULTIPLE_TABLE_CANDIDATES", "warning", page_number=1),
            _issue("ROW_SHAPE_INCONSISTENCY", "review"),
            _issue("UNKNOWN_SOURCE_PAGE", "warning", {"unknown_cell_count": 1}),
        ]))
        self.assertIn("Multiple table candidates detected on page 1.", result.review_summaries)
        self.assertIn("Row structure varies significantly in one recovered table.", result.review_summaries)
        self.assertIn("Some recovered values cannot be linked to a source page.", result.review_summaries)
        json.dumps(result.to_dict())

    def test_existing_no_issue_contract_remains_serializable(self):
        result = RecoveryResult(source_document=SourceDocument(source_path="input.pdf"))
        payload = result.to_dict()
        self.assertEqual([], payload["issues"])
        self.assertFalse(payload["review_required"])
        self.assertIsNone(payload["structural_confidence"])
        json.dumps(payload)

    def test_existing_output_path_positional_slot_is_preserved(self):
        result = RecoveryResult(
            SourceDocument(source_path="input.pdf"), [], [], None, False, "output.xlsx"
        )
        self.assertEqual("output.xlsx", result.output_path)


if __name__ == "__main__":
    unittest.main()
