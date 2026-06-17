# -*- coding: utf-8 -*-
"""测试 v1.2 OCR + 图片提取功能"""
import sys
sys.path.insert(0, '.')

from src.common.pdf_api import (
    _check_tesseract_available,
    _check_text_quality,
    _extract_page_images,
)


def test_tesseract_available():
    """Test 1: _check_tesseract_available 不崩溃"""
    result = _check_tesseract_available()
    print(f"Test 1 PASS: _check_tesseract_available() = {result}")
    assert isinstance(result, bool)


def test_quality_good_text():
    """Test 2: 正常英文文本应判定为 good"""
    good_rows = [["Hello World", "Test Data"], ["Row 2 Col 1", "Row 2 Col 2"]]
    result = _check_text_quality(good_rows)
    print(f"Test 2 PASS: good text quality = {result}")
    assert result["quality"] == "good", f"Expected good, got {result['quality']}"
    assert result["need_ocr"] == False, "Expected need_ocr=False"


def test_quality_garbled_text():
    """Test 3: 乱码文本应触发 OCR"""
    garbled_rows = [["\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a", "more garbage"]]
    result = _check_text_quality(garbled_rows)
    print(f"Test 3 PASS: garbled text quality = {result}")
    assert result["need_ocr"] == True, "Expected need_ocr=True for garbled text"


def test_quality_none():
    """Test 4: None 输入应触发 OCR"""
    result = _check_text_quality(None)
    print(f"Test 4 PASS: None quality = {result}")
    assert result["need_ocr"] == True, "Expected need_ocr=True for None"


def test_quality_empty():
    """Test 5: 空列表应触发 OCR"""
    result = _check_text_quality([])
    print(f"Test 5 PASS: empty rows quality = {result}")
    assert result["need_ocr"] == True, "Expected need_ocr=True for empty"


def test_quality_cjk():
    """Test 6: CJK 文本应判定为 good"""
    cjk_rows = [["专业服务", "CORE BUSINESS"], ["北京市朝阳区", "联系方式"]]
    result = _check_text_quality(cjk_rows)
    print(f"Test 6 PASS: CJK text quality = {result}")
    assert result["quality"] == "good", f"Expected good for CJK, got {result['quality']}"


def test_quality_mixed():
    """Test 7: 中英文混合文本应判定为 good"""
    mixed_rows = [["COMPANY NAME", "公司名称"], ["CORE BUSINESS · 专业服务", "联系方式"]]
    result = _check_text_quality(mixed_rows)
    print(f"Test 7 PASS: mixed text quality = {result}")
    assert result["quality"] == "good", f"Expected good for mixed, got {result['quality']}"


def test_quality_ir_dict():
    """Test 8: IR dict 输入应正常处理"""
    from src.common.pdf_table_ir import fallback_block
    ir = fallback_block(rows=[["Hello", "World"], ["Test", "Data"]], page=1, table_id=1)
    result = _check_text_quality(ir)
    print(f"Test 8 PASS: IR dict quality = {result}")
    assert result["quality"] == "good", f"Expected good for IR dict, got {result['quality']}"


def test_extract_images_no_images():
    """Test 9: 空 PDF 应返回空图片列表"""
    import fitz
    doc = fitz.open()
    page = doc.new_page()
    images = _extract_page_images(doc, 0)
    print(f"Test 9 PASS: empty PDF images = {len(images)}")
    assert len(images) == 0
    doc.close()


def test_pdf_to_excel_mode_param():
    """Test 10: pdf_to_excel 接受 mode 参数"""
    import inspect
    from src.common.pdf_api import pdf_to_excel
    sig = inspect.signature(pdf_to_excel)
    params = list(sig.parameters.keys())
    print(f"Test 10 PASS: pdf_to_excel params = {params}")
    assert "mode" in params, f"Expected 'mode' in params, got {params}"
    assert sig.parameters["mode"].default == "advanced", "Expected default mode='advanced'"


if __name__ == "__main__":
    tests = [
        test_tesseract_available,
        test_quality_good_text,
        test_quality_garbled_text,
        test_quality_none,
        test_quality_empty,
        test_quality_cjk,
        test_quality_mixed,
        test_quality_ir_dict,
        test_extract_images_no_images,
        test_pdf_to_excel_mode_param,
    ]
    
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as e:
            print(f"FAIL: {t.__name__}: {e}")
            failed += 1
    
    print(f"\n{'='*40}")
    print(f"Results: {passed} passed, {failed} failed, {len(tests)} total")
    if failed == 0:
        print("All tests PASSED!")
    else:
        sys.exit(1)
