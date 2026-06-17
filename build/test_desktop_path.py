# -*- coding: utf-8 -*-
"""验证 _resolve_output_path 对 Desktop 目录的处理"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.common.pdf_api import _resolve_output_path

# 用户实际遇到的路径
test_path = "C:/Users/24785/Desktop"

print("=" * 70)
print("验证 _resolve_output_path 对用户实际路径的处理")
print("=" * 70)

print(f"\n输入: {test_path!r}")
print(f"os.path.isdir: {os.path.isdir(test_path)}")
print(f"os.path.endswith('/'): {test_path.endswith('/')}")
print(f"os.path.endswith('\\\\'): {test_path.endswith(chr(92))}")

result = _resolve_output_path(test_path, "business_card_20260612_212107.pdf", ".xlsx")
print(f"\n输出: {result!r}")
print(f"endswith .xlsx: {result.lower().endswith('.xlsx')}")
print(f"包含 Desktop: {'Desktop' in result}")

# 也测试末尾带反斜杠的情况
test_path2 = "C:/Users/24785/Desktop\\"
print(f"\n输入2: {test_path2!r}")
result2 = _resolve_output_path(test_path2, "business_card_20260612_212107.pdf", ".xlsx")
print(f"输出2: {result2!r}")

# 测试末尾带正斜杠
test_path3 = "C:/Users/24785/Desktop/"
print(f"\n输入3: {test_path3!r}")
result3 = _resolve_output_path(test_path3, "business_card_20260612_212107.pdf", ".xlsx")
print(f"输出3: {result3!r}")

print("\n" + "=" * 70)
print("DONE")
