import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

try:
    from PySide6.QtWidgets import QApplication, QMainWindow
    from pages.main_window import Ui_MainWindow
except ModuleNotFoundError as exc:
    QApplication = None
    Ui_MainWindow = None
    _IMPORT_ERROR = str(exc)
else:
    _IMPORT_ERROR = ""


@unittest.skipIf(Ui_MainWindow is None, f"Desktop UI dependencies unavailable: {_IMPORT_ERROR}")
class UIM1ShellTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.window = QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.window)

    def tearDown(self):
        self.window.close()
        self.window.deleteLater()

    def test_shared_shell_has_sidebar_topbar_and_page_container(self):
        self.assertEqual(self.ui.sidebar.minimumWidth(), 240)
        self.assertEqual(self.ui.sidebar.maximumWidth(), 240)
        self.assertEqual(self.ui.topBar.height(), 56)
        self.assertIs(self.ui.contentTitle.parent(), self.ui.topBar)
        self.assertIsNotNone(self.ui.pageContainer)

    def test_navigation_groups_and_convert_contract_exist(self):
        self.assertEqual(self.ui.navSectionWorkspace.text(), "工作区")
        self.assertEqual(self.ui.navSectionTools.text(), "工具")
        self.assertEqual(self.ui.navSectionTemplates.text(), "模板")
        self.assertTrue(hasattr(self.ui, "btnConvert"))
        self.assertTrue(hasattr(self.ui, "pagesStack"))

    def test_protected_convert_page_import_remains_available(self):
        from pages.convert_page import ConvertPage

        self.assertTrue(callable(ConvertPage))


if __name__ == "__main__":
    unittest.main()
