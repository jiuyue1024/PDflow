# -*- coding: utf-8 -*-
"""v1.1-patch 路径鲁棒性测试：_resolve_output_path"""
import sys
import os
import tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.common.pdf_api import _resolve_output_path

print("=" * 70)
print("_resolve_output_path 路径鲁棒性测试")
print("=" * 70)

input_pdf = "business_card_20260612_212107.pdf"
work_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 用一个临时目录模拟 Desktop
with tempfile.TemporaryDirectory() as tmp:
    tmp_norm = os.path.normpath(tmp)
    print(f"\n临时目录: {tmp_norm}")

    # Case 1: 传 None（自动生成）
    print("\n[Case 1] output_path=None")
    out = _resolve_output_path(None, input_pdf, ".xlsx")
    print(f"  -> {out}")
    assert out.endswith(".xlsx"), f"应以后缀 .xlsx 结尾，实际: {out}"
    print(f"  [OK] 末尾: .xlsx")

    # Case 2: 完整文件路径
    print("\n[Case 2] 完整文件路径")
    full_path = os.path.join(tmp_norm, "result.xlsx")
    out = _resolve_output_path(full_path, input_pdf, ".xlsx")
    print(f"  -> {out}")
    assert out == full_path, f"应等于原路径，实际: {out} vs {full_path}"
    print(f"  [OK] 原样返回")

    # Case 3: 完整路径（无后缀）
    print("\n[Case 3] 完整路径但无后缀")
    no_ext = os.path.join(tmp_norm, "result")
    out = _resolve_output_path(no_ext, input_pdf, ".xlsx")
    print(f"  -> {out}")
    assert out.endswith(".xlsx"), f"应补后缀，实际: {out}"
    print(f"  [OK] 自动补 .xlsx")

    # Case 4: 用户传入目录路径（带末尾反斜杠）—— BUG 修复点
    print("\n[Case 4] 目录路径（带末尾 \\）")
    dir_with_sep = tmp_norm + os.sep
    out = _resolve_output_path(dir_with_sep, input_pdf, ".xlsx")
    print(f"  -> {out}")
    assert out.endswith(f"{os.path.splitext(os.path.basename(input_pdf))[0]}.xlsx"), \
        f"应在目录下生成 <basename>.xlsx，实际: {out}"
    print(f"  [OK] 在目录下生成 <basename>.xlsx")

    # Case 5: 用户传入目录路径（不带末尾反斜杠，但已存在）
    print("\n[Case 5] 目录路径（已存在，不带末尾 \\）")
    out = _resolve_output_path(tmp_norm, input_pdf, ".xlsx")
    print(f"  -> {out}")
    assert out.endswith(f"{os.path.splitext(os.path.basename(input_pdf))[0]}.xlsx"), \
        f"应在目录下生成 <basename>.xlsx，实际: {out}"
    print(f"  [OK] 在目录下生成 <basename>.xlsx")

    # Case 6: 不存在的路径（不视为目录）
    print("\n[Case 6] 不存在的路径（视为文件路径）")
    nonexistent = os.path.join(tmp_norm, "deep", "nested", "result.xlsx")
    out = _resolve_output_path(nonexistent, input_pdf, ".xlsx")
    print(f"  -> {out}")
    assert out.endswith(".xlsx"), f"应保留 .xlsx 后缀，实际: {out}"
    assert os.path.isdir(os.path.dirname(out)), f"父目录应被自动创建: {os.path.dirname(out)}"
    print(f"  [OK] 父目录自动创建")

    # Case 7: 大小写不敏感
    print("\n[Case 7] 大小写不敏感（.XLSX）")
    full_upper = os.path.join(tmp_norm, "result.XLSX")
    out = _resolve_output_path(full_upper, input_pdf, ".xlsx")
    print(f"  -> {out}")
    assert out == full_upper, f"应原样返回: {out}"
    print(f"  [OK] 大小写不敏感")

    # Case 8: 其他后缀
    print("\n[Case 8] .docx 后缀")
    out = _resolve_output_path(tmp_norm, input_pdf, ".docx")
    print(f"  -> {out}")
    assert out.endswith(".docx"), f"应使用 .docx 后缀: {out}"
    print(f"  [OK] .docx")

    # Case 9: .pdf 后缀
    print("\n[Case 9] .pdf 后缀")
    out = _resolve_output_path(tmp_norm, input_pdf, ".pdf")
    print(f"  -> {out}")
    assert out.endswith(".pdf"), f"应使用 .pdf 后缀: {out}"
    print(f"  [OK] .pdf")

print("\n" + "=" * 70)
print("ALL PATH RESOLVER TESTS PASSED")
print("=" * 70)
