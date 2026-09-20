import unittest

import pandas as pd

from src.common.pdf_api import (
    _global_fallback_matches_page_blocks,
    _is_duplicate_table,
    _should_use_ocr,
)
from src.common.pdf_table_ir import fallback_block


class PdfRecoveryH2Tests(unittest.TestCase):
    def test_fragmented_candidate_is_duplicate_of_clean_rows(self):
        clean = pd.DataFrame(
            [["North", "120", "18,450.25"], ["South", "98", "14,320.00"]],
            columns=["Region", "Units", "Revenue"],
        )
        fragmented = pd.DataFrame(
            [
                ["North", "120", "18,450.25", ""],
                ["South", "98", "14,320.00", ""],
            ],
            columns=["Region", "Units", "Revenue", ""],
        )
        self.assertTrue(_is_duplicate_table(clean, fragmented))

    def test_distinct_candidate_content_is_preserved(self):
        first = pd.DataFrame([["North", "120"], ["South", "98"]], columns=["Region", "Units"])
        second = pd.DataFrame([["Online", "154"], ["Central", "76"]], columns=["Region", "Units"])
        self.assertFalse(_is_duplicate_table(first, second))

    def test_candidate_with_unique_business_row_is_preserved(self):
        retained = pd.DataFrame(
            [["P-100", "12"], ["P-110", "8"], ["P-170", "30"]],
            columns=["Product Code", "Qty"],
        )
        candidate_with_additional_row = pd.DataFrame(
            [["P-100", "12"], ["P-110", "8"], ["P-170", "30"], ["P-180", "9"]],
            columns=["Product Code", "Qty"],
        )
        self.assertFalse(_is_duplicate_table(candidate_with_additional_row, retained))

    def test_exact_global_fallback_replay_is_detected(self):
        page = fallback_block([["Name", "Value"], ["A", "1"]], page=1, table_id=1)
        fallback = fallback_block([["Name", "Value"], ["A", "1"]], page=0, table_id=0)
        self.assertTrue(_global_fallback_matches_page_blocks(fallback, [(1, page)]))

    def test_global_fallback_with_unique_rows_is_preserved(self):
        page = fallback_block([["Name", "Value"], ["A", "1"]], page=1, table_id=1)
        fallback = fallback_block(
            [["Name", "Value"], ["A", "1"], ["Only in fallback", "2"]],
            page=0,
            table_id=0,
        )
        self.assertFalse(_global_fallback_matches_page_blocks(fallback, [(1, page)]))

    def test_usable_native_rows_do_not_trigger_ocr(self):
        self.assertFalse(
            _should_use_ocr("advanced", [["Region", "Units"], ["North", "120"]], True)
        )

    def test_poor_text_quality_still_allows_ocr(self):
        garbled = [["\ufffd\ufffd\ufffd\ufffd", "\ufffd\ufffd\ufffd"], ["\ufffd\ufffd", "\ufffd\ufffd"]]
        self.assertTrue(_should_use_ocr("advanced", garbled, True))


if __name__ == "__main__":
    unittest.main()
