import json
import unittest

from src.common.pdf_recovery_models import (
    RecoveryBlock,
    RecoveryCell,
    RecoveryResult,
    RouteDecision,
    SourceDocument,
    SourcePage,
)
from src.common.pdf_recovery_verify import verify_recovery_result


def _result(blocks, routes=None, page_count=None):
    if isinstance(blocks, RecoveryBlock):
        blocks = [blocks]
    routes = routes or {}
    page_numbers = sorted({block.page_number for block in blocks if block.page_number > 0})
    page_count = page_count if page_count is not None else max(page_numbers or [1])
    pages = [SourcePage(
        page_number=page_number,
        routing_decision=routes.get(page_number),
    ) for page_number in range(1, page_count + 1)]
    return RecoveryResult(
        source_document=SourceDocument(
            source_path="synthetic.pdf",
            page_count=page_count,
            pages=pages,
        ),
        blocks=blocks,
    )


def _block(page, rows, method="native_table", cells=None):
    cells = cells if cells is not None else [
        RecoveryCell(row_index=row_index, column_index=column_index,
                     value=value, source_page=page, method=method)
        for row_index, row in enumerate(rows)
        for column_index, value in enumerate(row)
    ]
    return RecoveryBlock(
        block_id=f"p{page}-b1",
        page_number=page,
        method=method,
        rows=rows,
        cells=cells,
    )


class PdfRecoverySlice2ATests(unittest.TestCase):
    def test_consistent_native_table_has_no_review_issue(self):
        result = _result(_block(1, [["A", "B"], ["1", "2"], ["3", "4"]]))
        verify_recovery_result(result)
        self.assertFalse(result.review_required)
        self.assertFalse(any(issue.severity == "review" for issue in result.issues))
        self.assertIsNone(result.structural_confidence)

    def test_multiple_candidates_is_warning_not_critical(self):
        route = RouteDecision(page_number=1, selected_method="native_table",
                              candidate_count=2)
        result = _result(_block(1, [["A"], ["1"]]), {1: route})
        verify_recovery_result(result)
        issue = next(issue for issue in result.issues
                     if issue.code == "MULTIPLE_TABLE_CANDIDATES")
        self.assertEqual("warning", issue.severity)
        self.assertFalse(result.review_required)
        self.assertEqual(2, issue.evidence["candidate_count"])

    def test_row_shape_instability_requires_repeated_material_variation(self):
        result = _result(_block(1, [
            ["A", "B", "C"], ["1"], ["2", "3", "4"], ["5"],
        ]))
        verify_recovery_result(result)
        issue = next(issue for issue in result.issues
                     if issue.code == "ROW_SHAPE_INCONSISTENCY")
        self.assertEqual("review", issue.severity)
        self.assertTrue(result.review_required)
        self.assertEqual([3, 1, 3, 1], issue.evidence["observed_column_counts"])

    def test_sparse_trailing_empty_cells_are_normalized(self):
        result = _result(_block(1, [
            ["A", "B", "C"], ["1", "2", ""], ["3", "", ""],
        ]))
        verify_recovery_result(result)
        self.assertFalse(any(issue.code == "ROW_SHAPE_INCONSISTENCY"
                             for issue in result.issues))

    def test_single_subtotal_or_section_row_does_not_trigger_review(self):
        result = _result(_block(1, [
            ["A", "B", "C"], ["1", "2", "3"],
            ["Subtotal"], ["4", "5", "6"], ["7", "8", "9"],
        ]))
        verify_recovery_result(result)
        self.assertFalse(any(issue.code == "ROW_SHAPE_INCONSISTENCY"
                             for issue in result.issues))

    def test_cross_page_consistent_schema_has_no_mismatch(self):
        result = _result([
            _block(1, [["Name", "Age"], ["A", "1"]]),
            _block(2, [["Name", "Age"], ["B", "2"]]),
        ], page_count=2)
        verify_recovery_result(result)
        self.assertFalse(any(issue.code == "CROSS_PAGE_SCHEMA_MISMATCH"
                             for issue in result.issues))

    def test_cross_page_inconsistent_schema_requires_header_evidence(self):
        result = _result([
            _block(1, [["Name", "Age"], ["A", "1"]]),
            _block(2, [["Name", "Age", "Dept"], ["B", "2", "X"]]),
        ], page_count=2)
        verify_recovery_result(result)
        issue = next(issue for issue in result.issues
                     if issue.code == "CROSS_PAGE_SCHEMA_MISMATCH")
        self.assertEqual("review", issue.severity)
        self.assertEqual([1, 2], issue.evidence["affected_pages"])
        self.assertTrue(result.review_required)

    def test_cross_page_continuation_without_page_two_header_is_not_mismatch(self):
        result = _result([
            _block(1, [["Name", "Age"], ["A", "1"]]),
            _block(2, [["B", "2"], ["C", "3"]]),
        ], page_count=2)
        verify_recovery_result(result)
        self.assertFalse(any(issue.code == "CROSS_PAGE_SCHEMA_MISMATCH"
                             for issue in result.issues))

    def test_cross_page_optional_trailing_column_is_compatible(self):
        result = _result([
            _block(1, [["Name", "Age", "Dept"], ["A", "1", ""]]),
            _block(2, [["Name", "Age", "Dept"], ["B", "2", ""]]),
        ], page_count=2)
        verify_recovery_result(result)
        self.assertFalse(any(issue.code == "CROSS_PAGE_SCHEMA_MISMATCH"
                             for issue in result.issues))

    def test_adjacent_unrelated_tables_are_not_compared(self):
        result = _result([
            _block(1, [["Invoice", "Total"], ["A", "1"]]),
            _block(2, [["Product", "Qty", "Price"], ["B", "2", "3"]]),
        ], page_count=2)
        verify_recovery_result(result)
        self.assertFalse(any(issue.code == "CROSS_PAGE_SCHEMA_MISMATCH"
                             for issue in result.issues))

    def test_one_shared_generic_header_is_not_comparable_evidence(self):
        result = _result([
            _block(1, [["Name", "Total"], ["A", "1"]]),
            _block(2, [["Name", "Qty", "Price"], ["B", "2", "3"]]),
        ], page_count=2)
        verify_recovery_result(result)
        self.assertFalse(any(issue.code == "CROSS_PAGE_SCHEMA_MISMATCH"
                             for issue in result.issues))

    def test_ocr_and_layout_diagnostics_do_not_become_confidence(self):
        route = RouteDecision(page_number=1, selected_method="ocr",
                              used_ocr=True, used_layout_fallback=True)
        result = _result(_block(1, [["A"], ["1"]], method="ocr"), {1: route})
        verify_recovery_result(result)
        codes = {issue.code for issue in result.issues}
        self.assertIn("OCR_USED", codes)
        self.assertIn("LAYOUT_FALLBACK_USED", codes)
        self.assertIsNone(result.structural_confidence)
        self.assertFalse(result.review_required)

    def test_unknown_source_page_is_reported_only_for_populated_unknown_values(self):
        block = RecoveryBlock(
            block_id="global-b1",
            page_number=0,
            method="layout_fallback",
            rows=[["unknown"]],
            cells=[RecoveryCell(row_index=0, column_index=0,
                                value="unknown", source_page=None)],
        )
        result = _result([block])
        verify_recovery_result(result)
        issue = next(issue for issue in result.issues
                     if issue.code == "UNKNOWN_SOURCE_PAGE")
        self.assertEqual("warning", issue.severity)
        self.assertIsNone(issue.page_number)

    def test_empty_recovery_is_critical_only_when_no_rows_exist(self):
        route = RouteDecision(page_number=1, selected_method="native_table",
                              candidate_count=1)
        result = _result([], {1: route}, page_count=1)
        verify_recovery_result(result)
        issue = next(issue for issue in result.issues
                     if issue.code == "EMPTY_RECOVERY")
        self.assertEqual("critical", issue.severity)
        self.assertTrue(result.review_required)

    def test_text_only_sidecar_without_structured_attempt_is_not_empty_critical(self):
        result = _result([], page_count=1)
        verify_recovery_result(result)
        self.assertFalse(any(issue.code == "EMPTY_RECOVERY"
                             for issue in result.issues))
        self.assertFalse(result.review_required)

    def test_issue_evidence_is_json_serializable(self):
        route = RouteDecision(page_number=1, candidate_count=2,
                              selected_method="native_table")
        result = _result([_block(1, [["A", "B", "C"], ["1"], ["2", "3", "4"], ["5"]])], {1: route})
        verify_recovery_result(result)
        json.dumps(result.to_dict())
        for issue in result.issues:
            self.assertIsInstance(issue.evidence, dict)


if __name__ == "__main__":
    unittest.main()
