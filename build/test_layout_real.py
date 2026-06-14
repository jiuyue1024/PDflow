# -*- coding: utf-8 -*-
"""P0 Hotfix 验证：真实 PDF → parse_layout_blocks 行结构重建效果"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pdfplumber

test_pdfs = [
    "02-素材资源/assets/body.pdf",
    "02-素材资源/assets/PDFlow_Logo品牌应用手册_2026-04-v2.pdf",
    "02-素材资源/assets/business_card_1.pdf",
    "02-素材资源/assets/business_card_2.pdf",
]

from src.common.pdf_layout_parser import parse_layout_blocks

print("=" * 70)
print("Layout Row Reconstruction 真实 PDF 验证")
print("=" * 70)

for pdf_rel in test_pdfs:
    full = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), pdf_rel)
    if not os.path.exists(full):
        print(f"\n[SKIP] {pdf_rel}")
        continue

    print(f"\n{'='*70}")
    print(f"PDF: {pdf_rel} ({os.path.getsize(full)} bytes)")
    print(f"{'='*70}")

    try:
        with pdfplumber.open(full) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                # 取首页 + 中间页 + 末页 各1 张（避免太大）
                if page_num not in (1, max(1, len(pdf.pages)//2), len(pdf.pages)):
                    continue
                rows = parse_layout_blocks(page)
                print(f"\n--- Page {page_num} ---")
                print(f"  rows (前 15 行): {len(rows)} total")
                for i, r in enumerate(rows[:15]):
                    print(f"  [{i:02d}] {r[0][:80]}")
                if len(rows) > 15:
                    print(f"  ... +{len(rows)-15} more")
    except Exception as e:
        print(f"  [ERR] {type(e).__name__}: {e}")

print("\n" + "=" * 70)
print("DONE")
print("=" * 70)
