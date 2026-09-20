import copy
import unittest

from src.common.pdf_review_session import ReviewSession, create_review_session


def _recovery_result():
    return {
        "reliability_band": "review_required",
        "review_summaries": ["Row structure varies significantly in one recovered table."],
        "blocks": [{
            "block_id": "table-1",
            "page_number": 2,
            "rows": [["Name", "Age"], ["Alice", 30]],
            "cells": [
                {"row_index": 0, "column_index": 0, "value": "Name", "source_page": 2},
                {"row_index": 0, "column_index": 1, "value": "Age", "source_page": 2},
                {"row_index": 1, "column_index": 0, "value": "Alice", "source_page": None},
                {"row_index": 1, "column_index": 1, "value": 30, "source_page": 2},
            ],
        }],
        "issues": [{
            "code": "ROW_SHAPE_INCONSISTENCY",
            "severity": "review",
            "block_id": "table-1",
            "row_index": 1,
            "message": "Row structure varies in this table.",
        }],
    }


class DesktopVNextSlice4ATests(unittest.TestCase):
    def test_review_session_creation_copies_original_rows(self):
        recovery = _recovery_result()
        session = create_review_session(recovery)
        self.assertIsNotNone(session)
        self.assertEqual([["Name", "Age"], ["Alice", 30]], session.original_rows)
        self.assertEqual(session.original_rows, session.working_rows)
        session.working_rows[0][0] = "Changed"
        self.assertEqual("Name", session.original_rows[0][0])
        self.assertEqual("Name", recovery["blocks"][0]["rows"][0][0])

    def test_edit_one_cell_tracks_dirty_coordinate(self):
        session = create_review_session(_recovery_result())
        session.set_value(1, 1, "31")
        self.assertTrue(session.dirty)
        self.assertEqual({(1, 1)}, session.changed_cells)
        self.assertEqual(1, session.changed_cell_count)

    def test_multiple_edits_track_exact_count_and_revert(self):
        session = create_review_session(_recovery_result())
        session.set_value(0, 0, "Full name")
        session.set_value(1, 0, "Bob")
        session.set_value(1, 1, "31")
        self.assertEqual({(0, 0), (1, 0), (1, 1)}, session.changed_cells)
        session.set_value(1, 1, 30)
        self.assertEqual({(0, 0), (1, 0)}, session.changed_cells)

    def test_cancel_discards_edits_and_does_not_mutate_recovery_data(self):
        recovery = _recovery_result()
        original = copy.deepcopy(recovery)
        session = create_review_session(recovery)
        session.set_value(1, 0, "Changed")
        session.cancel()
        self.assertFalse(session.dirty)
        self.assertEqual([["Name", "Age"], ["Alice", 30]], session.working_rows)
        self.assertEqual(original, recovery)
        self.assertTrue(session.cancelled)

    def test_apply_stores_separate_reviewed_data_and_preserves_output_path(self):
        recovery = _recovery_result()
        recovery["output_path"] = "result.xlsx"
        original = copy.deepcopy(recovery)
        session = create_review_session(recovery)
        session.set_value(1, 1, "31")
        reviewed = session.apply()
        self.assertEqual("31", reviewed["rows"][1][1])
        self.assertEqual([["Name", "Age"], ["Alice", 30]], recovery["blocks"][0]["rows"])
        self.assertEqual("result.xlsx", recovery["output_path"])
        self.assertEqual(original, recovery)
        self.assertTrue(session.applied)
        self.assertEqual([((1, 1))], reviewed["changed_cells"])

    def test_cancel_after_apply_restores_last_confirmed_review(self):
        session = create_review_session(_recovery_result())
        session.set_value(1, 1, "31")
        session.apply()
        session.set_value(1, 0, "Changed but not applied")
        session.cancel()
        self.assertTrue(session.applied)
        self.assertEqual("31", session.working_rows[1][1])
        self.assertEqual("Alice", session.working_rows[1][0])

    def test_source_page_metadata_is_preserved_without_invention(self):
        session = create_review_session(_recovery_result())
        self.assertEqual(2, session.source_page_at(0, 0))
        self.assertIsNone(session.source_page_at(1, 0))
        reviewed = session.apply()
        self.assertEqual(2, reviewed["source_pages"]["0,0"])
        self.assertIsNone(reviewed["source_pages"]["1,0"])

    def test_issue_marker_uses_existing_issue_data_only(self):
        session = create_review_session(_recovery_result())
        self.assertEqual(["Row structure varies in this table."], session.issue_markers[(1, 0)])
        self.assertEqual(["Row structure varies in this table."], session.issue_markers[(1, 1)])
        self.assertNotIn((0, 0), session.issue_markers)

    def test_legacy_result_has_no_review_session(self):
        self.assertIsNone(create_review_session(None))
        self.assertIsNone(create_review_session({"status": "ok"}))
        self.assertIsNone(create_review_session({"blocks": []}))

    def test_unusable_without_structured_data_has_no_editable_session(self):
        recovery = {"reliability_band": "unusable", "issues": [{"code": "EMPTY_RECOVERY"}], "blocks": []}
        self.assertIsNone(create_review_session(recovery))

    def test_ui_review_dialog_edits_applies_and_cancels(self):
        try:
            from PySide6.QtWidgets import QApplication
            from pages.convert_page import RecoveryReviewDialog
        except ModuleNotFoundError as exc:
            self.skipTest(f"Desktop UI dependencies unavailable: {exc}")
        app = QApplication.instance() or QApplication([])

        apply_session = create_review_session(_recovery_result())
        apply_dialog = RecoveryReviewDialog(apply_session)
        apply_dialog._table.item(1, 1).setText("31")
        self.assertTrue(apply_session.dirty)
        apply_dialog._apply()
        self.assertTrue(apply_session.applied)
        self.assertEqual("31", apply_session.reviewed_data["rows"][1][1])

        cancel_session = create_review_session(_recovery_result())
        cancel_dialog = RecoveryReviewDialog(cancel_session)
        cancel_dialog._table.item(1, 0).setText("Changed")
        cancel_dialog.reject()
        self.assertTrue(cancel_session.cancelled)
        self.assertEqual("Alice", cancel_session.working_rows[1][0])
        apply_dialog.deleteLater()
        cancel_dialog.deleteLater()

    def test_ui_result_entry_respects_usable_and_unusable_states(self):
        try:
            from PySide6.QtWidgets import QApplication
            from pages.convert_page import ConvertPage
        except ModuleNotFoundError as exc:
            self.skipTest(f"Desktop UI dependencies unavailable: {exc}")
        app = QApplication.instance() or QApplication([])
        page = ConvertPage()
        page._selected_type = "pdf_excel"
        page._results = [{"status": "ok", "output": "result.xlsx", "recovery_result": _recovery_result()}]
        page._apply_recovery_result_view()
        self.assertFalse(page._btn_result_review.isHidden())
        self.assertEqual("Review recommended before using this result", page._lbl_result_title.text())

        unusable = {"reliability_band": "unusable", "issues": [{"code": "EMPTY_RECOVERY"}], "blocks": []}
        page._results = [{"status": "ok", "output": "result.xlsx", "recovery_result": unusable}]
        page._apply_recovery_result_view()
        self.assertTrue(page._btn_result_review.isHidden())
        self.assertEqual("No usable structured result was recovered", page._lbl_result_title.text())

        page._results = [{"status": "ok", "output": "result.xlsx"}]
        page._apply_recovery_result_view()
        self.assertTrue(page._btn_result_review.isHidden())
        page.deleteLater()


if __name__ == "__main__":
    unittest.main()
