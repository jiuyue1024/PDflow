# -*- coding: utf-8 -*-
"""P0 Hotfix 单测：pdf_layout_parser (Layout Row Reconstruction)"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.common.pdf_layout_parser import (
    cluster_by_y,
    parse_layout_blocks,
    parse_layout_rows,
    _split_by_special_tokens,
    PHONE_PATTERN, EMAIL_PATTERN, URL_PATTERN,
)

print("=" * 60)
print("Layout Parser 单测")
print("=" * 60)

# Test 1: cluster_by_y 基础
print("\nTEST 1: cluster_by_y 基础")
blocks = [
    {"text": "A", "top": 100, "x0": 50},
    {"text": "B", "top": 100, "x0": 100},
    {"text": "C", "top": 110, "x0": 50},
]
lines = cluster_by_y(blocks, threshold=3.0)
print(f"  blocks: 3, lines: {len(lines)}")
print(f"  line 0: {[w['text'] for w in lines[0]]} (A B 同 top=100)")
print(f"  line 1: {[w['text'] for w in lines[1]]} (C 单独 top=110)")

# Test 2: 阈值严格
print("\nTEST 2: threshold=1.0 严格模式")
lines2 = cluster_by_y(blocks, threshold=1.0)
print(f"  lines: {len(lines2)} (A B C 各 1 行，因为 top 差 10 > 1)")

# Test 3: _split_by_special_tokens - 邮箱
print("\nTEST 3: _split_by_special_tokens 邮箱")
result = _split_by_special_tokens("邮箱: zhang@x.com 欢迎联系")
print(f"  result: {result}")

# Test 4: _split_by_special_tokens - 电话
print("\nTEST 4: _split_by_special_tokens 电话")
result = _split_by_special_tokens("电话: +86-138-1234-5678")
print(f"  result: {result}")

# Test 5: _split_by_special_tokens - URL
print("\nTEST 5: _split_by_special_tokens URL")
result = _split_by_special_tokens("网站 https://example.com 或 www.foo.com")
print(f"  result: {result}")

# Test 6: 无特殊 token
print("\nTEST 6: 无特殊 token")
result = _split_by_special_tokens("普通文本 张三")
print(f"  result: {result}")

# Test 7: 正则覆盖
print("\nTEST 7: 正则覆盖")
print(f"  PHONE test: '13812345678' -> {bool(PHONE_PATTERN.search('13812345678'))}")
print(f"  PHONE test: '+86-138-1234-5678' -> {bool(PHONE_PATTERN.search('+86-138-1234-5678'))}")
print(f"  EMAIL test: 'a@b.com' -> {bool(EMAIL_PATTERN.search('a@b.com'))}")
print(f"  URL test: 'https://x.com' -> {bool(URL_PATTERN.search('https://x.com'))}")
print(f"  URL test: 'www.x.com' -> {bool(URL_PATTERN.search('www.x.com'))}")

# Test 8: parse_layout_blocks (mock page)
print("\nTEST 8: parse_layout_blocks (mock page)")
class MockWord:
    def __init__(self, text, top, x0, x1=0):
        self.text = text
        self.top = top
        self.x0 = x0
        self.x1 = x1
    def __getitem__(self, k):
        return getattr(self, k)

class MockPage:
    def extract_words(self, **kwargs):
        return [
            MockWord("张三", 100, 50),
            MockWord("13812345678", 100, 100),
            MockWord("zhang@x.com", 100, 200),
            MockWord("地址: 北京市", 130, 50),
            MockWord("https://example.com", 130, 200),
        ]
    def close(self): pass

page = MockPage()
rows = parse_layout_blocks(page)
print(f"  rows count: {len(rows)}")
for i, r in enumerate(rows):
    print(f"  row {i}: {r}")

# Test 9: parse_layout_rows 兼容 API
print("\nTEST 9: parse_layout_rows 兼容 API")
rows_dict = parse_layout_rows(page)
print(f"  rows count: {len(rows_dict)}")
print(f"  first row: {rows_dict[0] if rows_dict else None}")

# Test 10: 空 page
print("\nTEST 10: 空 page")
class EmptyPage:
    def extract_words(self, **kwargs):
        return []
rows_empty = parse_layout_blocks(EmptyPage())
print(f"  empty rows: {rows_empty}")

# Test 11: 异常 page
print("\nTEST 11: 异常 page (extract_words raise)")
class ErrorPage:
    def extract_words(self, **kwargs):
        raise Exception("simulated error")
rows_err = parse_layout_blocks(ErrorPage())
print(f"  error rows: {rows_err} (空)")

print("\n" + "=" * 60)
print("ALL LAYOUT PARSER TESTS DONE")
print("=" * 60)
