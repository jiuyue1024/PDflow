import unittest

try:
    from pages.convert_page import recovery_result_view
except ModuleNotFoundError as exc:
    # Keep discovery readable on environments without the Desktop UI extras.
    recovery_result_view = None
    _UI_IMPORT_ERROR = str(exc)
else:
    _UI_IMPORT_ERROR = ""


class _Widget:
    def __init__(self):
        self.visible = None
        self.text = None

    def setVisible(self, value):
        self.visible = value

    def setText(self, value):
        self.text = value

    def setStyleSheet(self, value):
        self.style = value


class _Button(_Widget):
    pass


@unittest.skipIf(recovery_result_view is None, f"Desktop UI dependencies unavailable: {_UI_IMPORT_ERROR}")
class DesktopVNextSlice3Tests(unittest.TestCase):
    def _page(self, recovery_result, selected_type="pdf_excel"):
        page = object.__new__(type("Page", (), {}))
        page._selected_type = selected_type
        page._results = [{"status": "ok", "output": "result.xlsx", "recovery_result": recovery_result}]
        page._lbl_result_status = _Widget()
        page._lbl_result_review = _Widget()
        page._btn_result_details = _Button()
        page._lbl_result_title = _Widget()
        page._apply_recovery_result_view = __import__("pages.convert_page", fromlist=["ConvertPage"]).ConvertPage._apply_recovery_result_view.__get__(page)
        return page

    def test_clear_shows_ready_without_review_warning(self):
        page = self._page({"reliability_band": "clear", "review_summaries": [], "issues": []})
        page._apply_recovery_result_view()
        self.assertEqual("Excel is ready", page._lbl_result_title.text)
        self.assertEqual("Status: Clear", page._lbl_result_status.text)
        self.assertNotIn("recommended", page._lbl_result_review.text.lower())
        self.assertNotIn("warning", page._lbl_result_review.text.lower())
        self.assertFalse(page._btn_result_details.visible)

    def test_caution_recommends_check_and_does_not_gate_output(self):
        page = self._page({
            "reliability_band": "caution",
            "review_summaries": ["OCR was used to recover values on page 1."],
            "issues": [{"code": "OCR_USED", "severity": "info", "page_number": 1}],
        })
        page._apply_recovery_result_view()
        self.assertIn("quick check is recommended", page._lbl_result_title.text)
        self.assertIn("OCR was used", page._lbl_result_review.text)
        self.assertTrue(page._btn_result_details.visible)
        self.assertEqual("result.xlsx", page._results[0]["output"])

    def test_review_required_shows_supplied_summaries_and_keeps_output(self):
        page = self._page({
            "reliability_band": "review_required",
            "review_required": True,
            "review_summaries": ["Row structure varies significantly in one recovered table."],
            "issues": [{"code": "ROW_SHAPE_INCONSISTENCY", "severity": "review"}],
        })
        page._apply_recovery_result_view()
        self.assertEqual("Review recommended before using this result", page._lbl_result_title.text)
        self.assertIn("Row structure varies", page._lbl_result_review.text)
        self.assertEqual("result.xlsx", page._results[0]["output"])

    def test_unusable_does_not_claim_excel_is_ready(self):
        page = self._page({
            "reliability_band": "unusable",
            "review_summaries": ["No usable structured recovery was produced after structured recovery was attempted."],
            "issues": [{"code": "EMPTY_RECOVERY", "severity": "critical", "page_number": 1}],
        })
        page._apply_recovery_result_view()
        self.assertEqual("No usable structured result was recovered", page._lbl_result_title.text)
        self.assertNotIn("Excel is ready", page._lbl_result_title.text)

    def test_legacy_result_without_sidecar_is_unchanged(self):
        page = self._page(None)
        page._results = [{"status": "ok", "output": "result.xlsx"}]
        page._apply_recovery_result_view()
        self.assertFalse(page._lbl_result_status.visible)
        self.assertFalse(page._lbl_result_review.visible)
        self.assertFalse(page._btn_result_details.visible)

    def test_missing_optional_fields_are_graceful(self):
        view = recovery_result_view({"reliability_band": "caution"})
        self.assertEqual([], view["summaries"])
        self.assertEqual([], view["issues"])

    def test_visible_summaries_are_limited_to_three(self):
        view = recovery_result_view({
            "reliability_band": "review_required",
            "review_summaries": ["one", "two", "three", "four"],
        })
        self.assertEqual(["one", "two", "three"], view["summaries"])

    def test_ui_does_not_recompute_band_from_issues(self):
        view = recovery_result_view({
            "reliability_band": "clear",
            "review_summaries": [],
            "issues": [{"code": "EMPTY_RECOVERY", "severity": "critical"}],
        })
        self.assertEqual("clear", view["band"])
        self.assertEqual("Excel is ready", view["title"])


if __name__ == "__main__":
    unittest.main()
