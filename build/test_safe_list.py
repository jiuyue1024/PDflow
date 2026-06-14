# -*- coding: utf-8 -*-
"""safe_list 单测"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.common.pdf_table_ir import safe_list

print("=" * 60)
print("safe_list 单测")
print("=" * 60)

# Test 1: 原生 list
print("\nTEST 1: 原生 list")
result = safe_list([1, 2, 3])
assert result == [1, 2, 3], f"Expected [1,2,3], got {result}"
print(f"  [OK] {result}")

# Test 2: pandas Series
print("\nTEST 2: pandas Series")
import pandas as pd
s = pd.Series([10, 20, 30])
result = safe_list(s)
assert result == [10, 20, 30], f"Expected [10,20,30], got {result}"
print(f"  [OK] {result}")

# Test 3: pandas DataFrame
print("\nTEST 3: pandas DataFrame")
df = pd.DataFrame([[1, 2], [3, 4]])
result = safe_list(df)
assert result == [[1, 2], [3, 4]], f"Expected [[1,2],[3,4]], got {result}"
print(f"  [OK] {result}")

# Test 4: 单列 DataFrame（df[col] 可能返回 DataFrame 而非 Series）
print("\nTEST 4: 单列 DataFrame → safe_list 不崩溃")
df2 = pd.DataFrame({"A": [1, 2]})
col = df2[["A"]]  # 这返回 DataFrame，不是 Series
result = safe_list(col)
print(f"  [OK] type={type(col).__name__}, safe_list={result}")

# Test 5: numpy ndarray
print("\nTEST 5: numpy ndarray")
import numpy as np
arr = np.array([5, 6, 7])
result = safe_list(arr)
assert result == [5, 6, 7], f"Expected [5,6,7], got {result}"
print(f"  [OK] {result}")

# Test 6: 单值
print("\nTEST 6: 单值")
result = safe_list(42)
assert result == [42], f"Expected [42], got {result}"
print(f"  [OK] {result}")

# Test 7: 空列表
print("\nTEST 7: 空列表")
result = safe_list([])
assert result == [], f"Expected [], got {result}"
print(f"  [OK] {result}")

print("\n" + "=" * 60)
print("ALL SAFE_LIST TESTS PASSED")
print("=" * 60)
