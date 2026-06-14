# -*- coding: utf-8 -*-
"""精确复现 GUI 转换失败：传目录路径给 pdf_to_excel"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.common.pdf_api import pdf_to_excel

# 找一个真实的输入 PDF
test_input = None
for candidate in [
    "02-素材资源/assets/PDFlow_Logo品牌应用手册_2026-04-v2.pdf",
    "02-素材资源/assets/body.pdf",
]:
    if os.path.exists(candidate):
        test_input = candidate
        break

if not test_input:
    print("[SKIP] no test input found")
    sys.exit(0)

print("=" * 70)
print("精确复现 GUI 路径问题")
print("=" * 70)
print(f"test input: {test_input}")

# Case 1: 用户传了"完整文件路径"（GUI 正确行为）
out1 = os.path.join(os.path.dirname(test_input), "test_output.xlsx")
print(f"\n[Case 1] 完整文件路径: {out1!r}")
try:
    result = pdf_to_excel(test_input, out1)
    print(f"  [OK] {result['output']}")
except Exception as e:
    print(f"  [FAIL] {e}")

# Case 2: 用户传了"目录路径"（BUG: GUI 把 _output_dir 直接传进来）
out2 = os.path.dirname(test_input) + "\\"  # Windows 末尾反斜杠
print(f"\n[Case 2] 目录路径（带末尾 \\）: {out2!r}")
try:
    result = pdf_to_excel(test_input, out2)
    print(f"  [OK] {result['output']}")
except Exception as e:
    print(f"  [FAIL] {e}")
    print(f"  错误类型: {type(e).__name__}")

# Case 3: 用户传了"目录路径"（不带末尾反斜杠）
out3 = os.path.dirname(test_input)
print(f"\n[Case 3] 目录路径: {out3!r}")
try:
    result = pdf_to_excel(test_input, out3)
    print(f"  [OK] {result['output']}")
except Exception as e:
    print(f"  [FAIL] {e}")
    print(f"  错误类型: {type(e).__name__}")

# Case 4: 模拟 GUI 拼出的 "C:/Users/24785/Desktop\\" 路径
out4 = "C:/Users/24785/Desktop\\"
print(f"\n[Case 4] 模拟 GUI 路径（Desktop\\）: {out4!r}")
print(f"  isdir: {os.path.isdir(out4) if os.name == 'nt' else 'N/A (non-windows)'}")
try:
    result = pdf_to_excel(test_input, out4)
    print(f"  [OK] {result['output']}")
except Exception as e:
    print(f"  [FAIL] {e}")
    print(f"  错误类型: {type(e).__name__}")

print("\n" + "=" * 70)
print("DONE")
print("=" * 70)
