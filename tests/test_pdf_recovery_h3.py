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


def _block(page, rows):
    return RecoveryBlock(
        block_id=f"p{page}-b1",
        page_number=page,
        method="native_table",
        rows=rows,
        cells=[
            RecoveryCell(
                row_index=row_index,
                column_index=column_index,
                value=value,
                source_page=page,
                method="native_table",
            )
            for row_index, row in enumerate(rows)
            for column_index, value in enumerate(row)
        ],
    )


def _result(blocks, route_summaries=None, page_count=None):
    blocks = list(blocks)
    page_count = page_count or max((block.page_number for block in blocks), default=1)
    summaries = route_summaries or {}
    pages = []
    for page_number in range(1, page_count + 1):
        summary = summaries.get(page_number)
        pages.append(SourcePage(
            page_number=page_number,
            routing_decision=(
                RouteDecision(
                    page_number=page_number,
                    selected_method="native_table",
                    candidate_count=len(summary or []),
                    candidate_summaries=summary or [],
                )
                if summary is not None else None
            ),
        ))
    return RecoveryResult(
        source_document=SourceDocument(
            source_path="synthetic.pdf",
            page_count=page_count,
            pages=pages,
        ),
        blocks=blocks,
    )


def _candidate(index, rows, selected=False, columns=3, header="header"):
    return {
        "candidate_index": index,
        "selected": selected,
        "row_count": len(rows),
        "column_count": columns,
        "score": 0.8,
        "header_signature": header,
        "row_signatures": rows,
    }


class PdfRecoveryH3Tests(unittest.TestCase):
    def test_fuller_compatible_candidate_triggers_review(self):
        summaries = [[
            _candidate(1, ["a", "b", "c"], selected=True),
            _candidate(2, ["a", "b", "c", "d"]),
        ]]
        result = _result([_block(1, [["H"], ["a"], ["b"], ["c"]])], {1: summaries[0]})
        verify_recovery_result(result)
        issue = next(issue for issue in result.issues if issue.code == "POSSIBLE_INCOMPLETE_RECOVERY")
        self.assertEqual("fuller_compatible_candidate", issue.evidence["reason"])
        self.assertTrue(result.review_required)

    def test_unique_alternative_business_row_is_not_silent(self):
        summaries = [
            _candidate(1, ["a", "b", "c"], selected=True),
            _candidate(2, ["a", "b", "c", "businessrow"]),
        ]
        result = _result([_block(1, [["H"], ["a"], ["b"], ["c"]])], {1: summaries})
        verify_recovery_result(result)
        self.assertTrue(any(issue.code == "POSSIBLE_INCOMPLETE_RECOVERY" for issue in result.issues))

    def test_fragmented_and_header_only_candidate_is_ignored(self):
        summaries = [
            _candidate(1, ["alphaone", "betatwo", "gammathree"], selected=True),
            _candidate(2, ["alpha", "one", "beta", "two", "header"]),
        ]
        result = _result([_block(1, [["Header"], ["alphaone"], ["betatwo"], ["gammathree"]])], {1: summaries})
        verify_recovery_result(result)
        self.assertFalse(any(issue.code == "POSSIBLE_INCOMPLETE_RECOVERY" for issue in result.issues))

    def test_sparse_valid_table_does_not_trigger_completeness_warning(self):
        result = _result([_block(1, [["Item", "Amount"], ["A", ""], ["B", "2"]])])
        verify_recovery_result(result)
        self.assertFalse(any(issue.code == "POSSIBLE_INCOMPLETE_RECOVERY" for issue in result.issues))

    def test_section_and_subtotal_rows_do_not_trigger_completeness_warning(self):
        result = _result([_block(1, [
            ["Item", "Amount"], ["A", "1"], ["Services"],
            ["B", "2"], ["Subtotal", "3"],
        ])])
        verify_recovery_result(result)
        self.assertFalse(any(issue.code == "POSSIBLE_INCOMPLETE_RECOVERY" for issue in result.issues))

    def test_compatible_cross_page_row_drop_triggers_review(self):
        result = _result([
            _block(1, [["Name", "Amount"]] + [[f"A{i}", str(i)] for i in range(8)]),
            _block(2, [["Name", "Amount"], ["B1", "1"] , ["B2", "2"]]),
        ], page_count=2)
        verify_recovery_result(result)
        issue = next(issue for issue in result.issues if issue.code == "POSSIBLE_INCOMPLETE_RECOVERY")
        self.assertEqual("compatible_cross_page_row_drop", issue.evidence["reason"])

    def test_incompatible_adjacent_schemas_do_not_trigger_completeness_warning(self):
        result = _result([
            _block(1, [["Name", "Amount"]] + [[f"A{i}", str(i)] for i in range(8)]),
            _block(2, [["Product", "Quantity", "Price"], ["B", "2", "3"]]),
        ], page_count=2)
        verify_recovery_result(result)
        self.assertFalse(any(issue.code == "POSSIBLE_INCOMPLETE_RECOVERY" for issue in result.issues))

    def test_independent_structured_region_is_not_silently_accepted(self):
        summaries = [
            _candidate(1, ["a", "b", "c"], selected=True),
            _candidate(2, ["x", "y", "z"], columns=2, header="otherheader"),
        ]
        result = _result([_block(1, [["H"], ["a"], ["b"], ["c"]])], {1: summaries})
        verify_recovery_result(result)
        issue = next(issue for issue in result.issues if issue.code == "POSSIBLE_INCOMPLETE_RECOVERY")
        self.assertEqual("independent_structured_region", issue.evidence["reason"])

    def test_h2_ocr_quality_gate_remains_conservative(self):
        from src.common.pdf_api import _should_use_ocr

        self.assertFalse(_should_use_ocr("advanced", [["A", "B"], ["1", "2"]], True))
        self.assertTrue(_should_use_ocr("advanced", [["\ufffd\ufffd"]], True))

    def test_legacy_result_without_candidate_evidence_remains_compatible(self):
        result = _result([_block(1, [["A"], ["1"]])])
        verify_recovery_result(result)
        self.assertFalse(any(issue.code == "POSSIBLE_INCOMPLETE_RECOVERY" for issue in result.issues))


if __name__ == "__main__":
    unittest.main()
