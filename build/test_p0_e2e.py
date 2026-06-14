# -*- coding: utf-8 -*-
"""PDF -> Excel 端到端测试（用 pdf_to_excel 真实函数）"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import traceback

test_pdfs = [
    "02-素材资源/assets/body.pdf",
    "02-素材资源/assets/PDFlow_Logo品牌应用手册_2026-04-v2.pdf",
]

for pdf in test_pdfs:
    full = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), pdf)
    if not os.path.exists(full):
        print(f"[SKIP] {pdf} (not found)")
        continue

    print(f"\n{'='*60}")
    print(f"Testing: {pdf} ({os.path.getsize(full)} bytes)")
    print(f"{'='*60}")

    try:
        from src.common.pdf_api import pdf_to_excel
        out_xlsx = os.path.join("build", f"_e2e_{os.path.basename(pdf).replace('.pdf','')}.xlsx")
        os.makedirs("build", exist_ok=True)
        result = pdf_to_excel(full, out_xlsx)
        print(f"  [OK] status: {result['status']}, tables: {result['tables']}, output: {result['output']}")
        print(f"  [OK] file size: {os.path.getsize(out_xlsx)} bytes")
    except Exception as e:
        print(f"  [FAIL] {type(e).__name__}: {e}")
        traceback.print_exc()

print("\n" + "="*60)
print("E2E TEST COMPLETE")
print("="*60)
