import json
import unittest

from src.common.pdf_recovery_models import (
    RecoveryBlock,
    RecoveryCell,
    RecoveryIssue,
    RecoveryResult,
    RouteDecision,
    SourceDocument,
    SourcePage,
)
from src.common.pdf_table_ir import TableBlock, TableMeta


class PdfRecoverySlice1Tests(unittest.TestCase):
    def test_models_are_constructible_and_serializable(self):
        source = SourceDocument(
            source_path="C:/input.pdf",
            source_name="input.pdf",
            file_size=12,
            page_count=1,
            pages=[SourcePage(
                page_number=1,
                width=100,
                height=200,
                routing_decision=RouteDecision(
                    page_number=1,
                    selected_method="rapidocr",
                    reasons=["fallback"],
                    used_ocr=True,
                ),
            )],
        )
        block = RecoveryBlock(
            block_id="p1-b1",
            page_number=1,
            region_bbox=(1, 2, 3, 4),
            method="rapidocr",
            rows=[["value"]],
            cells=[RecoveryCell(
                row_index=0,
                column_index=0,
                value="value",
                source_page=1,
                source_bbox=(1, 2, 3, 4),
                method="rapidocr",
                ocr_confidence=0.91,
            )],
            structural_confidence=0.62,
        )
        result = RecoveryResult(
            source_document=source,
            blocks=[block],
            issues=[RecoveryIssue(code="LOW_CONFIDENCE", message="Review")],
            review_required=True,
        )

        payload = result.to_dict()
        json.dumps(payload)
        self.assertEqual(payload["blocks"][0]["cells"][0]["source_page"], 1)
        self.assertEqual(payload["blocks"][0]["cells"][0]["ocr_confidence"], 0.91)
        self.assertEqual(payload["blocks"][0]["structural_confidence"], 0.62)

    def test_ocr_confidence_is_not_document_structural_confidence(self):
        result = RecoveryResult(
            source_document=SourceDocument(source_path="input.pdf"),
            blocks=[RecoveryBlock(
                block_id="p1-b1",
                page_number=1,
                method="rapidocr",
                structural_confidence=0.58,
                cells=[RecoveryCell(
                    row_index=0,
                    column_index=0,
                    value="42",
                    method="rapidocr",
                    ocr_confidence=0.97,
                )],
            )],
            structural_confidence=None,
        )
        payload = result.to_dict()
        self.assertEqual(payload["blocks"][0]["cells"][0]["ocr_confidence"], 0.97)
        self.assertEqual(payload["blocks"][0]["structural_confidence"], 0.58)
        self.assertIsNone(payload["structural_confidence"])

    def test_table_provenance_is_optional_and_backward_compatible(self):
        legacy = TableBlock(rows=[["value"]], meta=TableMeta())
        self.assertNotIn("provenance", legacy.to_dict()["meta"])

        with_provenance = TableBlock(
            rows=[["value"]],
            meta=TableMeta(provenance={"page_number": 1}),
        )
        self.assertEqual(
            with_provenance.to_dict()["meta"]["provenance"],
            {"page_number": 1},
        )


if __name__ == "__main__":
    unittest.main()
