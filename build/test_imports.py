"""测试打包环境中 pdf2docx / pdfplumber 导入"""
import sys
import traceback

print("Python:", sys.version)
print("sys.path:", sys.path[:5])

# 测试 pdf2docx
print("\n=== pdf2docx ===")
try:
    from pdf2docx import Converter
    print("[OK] from pdf2docx import Converter")
except Exception as e:
    print(f"[FAIL] {type(e).__name__}: {e}")
    traceback.print_exc()

# 测试 cv2
print("\n=== cv2 ===")
try:
    import cv2
    print(f"[OK] cv2 version: {cv2.__version__}")
except Exception as e:
    print(f"[FAIL] {type(e).__name__}: {e}")
    traceback.print_exc()

# 测试 pdfplumber
print("\n=== pdfplumber ===")
try:
    import pdfplumber
    print(f"[OK] pdfplumber version: {pdfplumber.__version__}")
except Exception as e:
    print(f"[FAIL] {type(e).__name__}: {e}")
    traceback.print_exc()

# 测试 pandas
print("\n=== pandas ===")
try:
    import pandas as pd
    print(f"[OK] pandas version: {pd.__version__}")
except Exception as e:
    print(f"[FAIL] {type(e).__name__}: {e}")
    traceback.print_exc()

# 测试 openpyxl
print("\n=== openpyxl ===")
try:
    import openpyxl
    print(f"[OK] openpyxl version: {openpyxl.__version__}")
except Exception as e:
    print(f"[FAIL] {type(e).__name__}: {e}")
    traceback.print_exc()
