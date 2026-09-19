import json
import os
import tempfile
import unittest

import fitz

from src.common.pdf_api import pdf_to_excel


class _Item:
    def setText(self, value):
        self.text = value

    def setData(self, role, value):
        self.data = (role, value)


class _List:
    def __init__(self, item):
        self._item = item

    def item(self, index):
        return self._item


class _Progress:
    def setValue(self, value):
        self.value = value


class PdfRecoverySlice1BTests(unittest.TestCase):
    def _make_pdf(self):
        handle, path = tempfile.mkstemp(suffix=".pdf")
        os.close(handle)
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 72), "Name Age\nAlice 30")
        doc.save(path)
        doc.close()
        return path

    def test_pdf_to_excel_adds_serializable_sidecar_without_changing_legacy_fields(self):
        source = self._make_pdf()
        output = tempfile.mktemp(suffix=".xlsx")
        try:
            result = pdf_to_excel(source, output, mode="standard")
            self.assertEqual({"status", "output", "tables"},
                             set(result) - {"recovery_result"})
            self.assertEqual("ok", result["status"])
            self.assertTrue(os.path.isfile(result["output"]))
            json.dumps(result["recovery_result"])
        finally:
            for path in (source, output):
                if os.path.exists(path):
                    os.remove(path)

    def test_route_and_confidence_contract(self):
        source = self._make_pdf()
        output = tempfile.mktemp(suffix=".xlsx")
        try:
            sidecar = pdf_to_excel(source, output, mode="standard")["recovery_result"]
            self.assertIsNone(sidecar["structural_confidence"])
            page = sidecar["source_document"]["pages"][0]
            self.assertEqual("native_table", page["routing_decision"]["selected_method"])
            self.assertFalse(page["routing_decision"]["used_ocr"])
            self.assertTrue(sidecar["blocks"])
            self.assertEqual(1, sidecar["blocks"][0]["cells"][0]["source_page"])
            self.assertIsNone(sidecar["blocks"][0]["cells"][0]["ocr_confidence"])
        finally:
            for path in (source, output):
                if os.path.exists(path):
                    os.remove(path)

    def test_convert_page_preserves_present_and_absent_sidecars(self):
        from pages.convert_page import ConvertPage

        page = ConvertPage.__new__(ConvertPage)
        page._paths = ["input.pdf"]
        page._file_list = _List(_Item())
        page._progress = _Progress()
        page._ok = 0
        page._idx = 0
        page._done_all = lambda: None
        sidecar = {"structural_confidence": None}

        page._on_done(0, {"status": "ok", "output": "", "recovery_result": sidecar})
        self.assertIs(sidecar, page._results[0]["recovery_result"])

        page._ok = 0
        page._on_done(0, {"status": "ok", "output": ""})
        self.assertNotIn("recovery_result", page._results[0])


if __name__ == "__main__":
    unittest.main()
