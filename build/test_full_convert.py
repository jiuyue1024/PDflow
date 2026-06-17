# -*- coding: utf-8 -*-
"""完整复现 GUI 转换流程：模拟 convert_page.py 的 _next() 路径拼接"""
import sys
import os
import traceback
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.common.pdf_api import pdf_to_excel

# 模拟 GUI 用户操作：
# 1. 用户选择了一个 PDF 文件
# 2. 用户选择了输出目录（如桌面）
# 3. 点击"开始转换"

test_pdf = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "02-素材资源", "assets", "body.pdf")

if not os.path.exists(test_pdf):
    print(f"[SKIP] test PDF not found: {test_pdf}")
    sys.exit(0)

print("=" * 70)
print("完整复现 GUI 转换流程")
print("=" * 70)
print(f"输入: {test_pdf}")
print(f"大小: {os.path.getsize(test_pdf)} bytes")

# 模拟 GUI _next() 的路径拼接逻辑
# convert_page.py 第 786 行: out = os.path.join(self._output_dir, base + out_ext)
output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "02-素材资源", "assets")
base = os.path.splitext(os.path.basename(test_pdf))[0]
out_ext = ".xlsx"
gui_out = os.path.join(output_dir, base + out_ext)

print(f"\nGUI 拼出路径: {gui_out}")
print(f"  dirname: {os.path.dirname(gui_out)}")
print(f"  exists: {os.path.exists(os.path.dirname(gui_out))}")

print("\n--- 开始转换 ---")
try:
    result = pdf_to_excel(test_pdf, gui_out)
    print(f"[OK] status: {result['status']}")
    print(f"[OK] output: {result['output']}")
    print(f"[OK] tables: {result['tables']}")
    if os.path.exists(result['output']):
        print(f"[OK] file exists, size: {os.path.getsize(result['output'])} bytes")
except Exception as e:
    print(f"[FAIL] {type(e).__name__}: {e}")
    traceback.print_exc()

# 清理
if os.path.exists(gui_out):
    os.remove(gui_out)
    print(f"\n[cleanup] removed: {gui_out}")

print("\n" + "=" * 70)
print("DONE")
