# -*- coding: utf-8 -*-
"""复现 GUI 路径问题：模拟 _next() 构造的 out 路径"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 模拟 QFileDialog.getExistingDirectory 在 Windows 上的返回值
# 实测：在 Windows 上，QFileDialog 返回的路径通常带或不带末尾斜杠
test_cases = [
    ("C:/Users/24785/Desktop", ".xlsx", "business_card_20260612_212107"),
    ("C:/Users/24785/Desktop/", ".xlsx", "business_card_20260612_212107"),
    ("C:/Users/24785/Desktop\\", ".xlsx", "business_card_20260612_212107"),
]

print("=" * 70)
print("复现 GUI 路径处理")
print("=" * 70)

for out_dir, out_ext, base in test_cases:
    out = os.path.join(out_dir, base + out_ext)
    print(f"\nout_dir = {out_dir!r}")
    print(f"  base  = {base!r}")
    print(f"  out_ext = {out_ext!r}")
    print(f"  -> out = {out!r}")
    print(f"  endswith(.xlsx) = {out.lower().endswith('.xlsx')}")
    print(f"  isdir(dirname) = {os.path.isdir(os.path.dirname(out)) if os.path.dirname(out) else 'N/A'}")

# 关键：检查 pdf_to_excel 内部处理
print("\n" + "=" * 70)
print("直接调用 pdf_to_excel（用户传目录）")
print("=" * 70)

# 用户可能传入纯目录路径的情况
test_input = "02-素材资源/assets/business_card_1.pdf"
if not os.path.exists(test_input):
    print(f"  [SKIP] test input not found: {test_input}")
else:
    from src.common.pdf_api import pdf_to_excel

    # Case 1: 用户传入目录路径
    print("\nCase 1: 用户传入 C:/Users/24785/Desktop/ (目录路径)")
    out_dir_only = "C:/Users/24785/Desktop/"
    try:
        # 直接模拟 GUI 拼出的路径
        base = os.path.splitext(os.path.basename(test_input))[0]
        gui_out = os.path.join(out_dir_only, base + ".xlsx")
        print(f"  GUI 拼出路径: {gui_out!r}")
        result = pdf_to_excel(test_input, gui_out)
        print(f"  [OK] {result['output']}")
    except Exception as e:
        print(f"  [FAIL] {e}")

    # Case 2: PDF → Excel 传入 None
    print("\nCase 2: 用户传入 None（自动生成）")
    try:
        result = pdf_to_excel(test_input)
        print(f"  [OK] {result['output']}")
    except Exception as e:
        print(f"  [FAIL] {e}")

print("\nDONE")
