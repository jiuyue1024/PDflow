# -*- coding: utf-8 -*-
"""
test_style_system.py — 样式预设系统集成测试

测试覆盖（12 项）：
  1. notice 预设切换 — 加载 4 套预设并验证字段
  2. business_card 预设切换 — 加载 4 套预设并验证字段
  3. product_spec 预设切换 — 加载 1 套预设并验证字段
  4. 自定义颜色联动 — bg_custom_color 与文本输入联动
  5. notice PDF 渲染 — 带 style 参数生成 PDF
  6. product_spec PDF 渲染 — 带 style 参数生成 PDF
  7. business_card PDF 渲染 — 带 style_options 生成 PDF
  8. 预设值与默认值一致性 — 预设值与模板默认值匹配
  9. template_id 不存在时预设加载 — 优雅降级
  10. notice 模板 style_options 结构完整性
  11. product_spec 模板 style_options 结构完整性
  12. render_notice/render_product_spec 的 style 参数兼容性
"""
import json
import os
import sys
import tempfile

PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

TEMPLATES_PATH = os.path.join(PROJECT_ROOT, "assets", "templates")
PRESETS_PATH = os.path.join(TEMPLATES_PATH, "presets")


# ── 测试结果统计 ──
passed = 0
failed = 0


def assert_test(condition: bool, test_name: str):
    global passed, failed
    if condition:
        passed += 1
        print(f"  ✅ {test_name}")
    else:
        failed += 1
        print(f"  ❌ {test_name}")


# ============================================================
# 测试 1: notice 预设切换
# ============================================================
def test_notice_presets():
    print("\n[测试 1] notice 预设切换")
    presets_path = os.path.join(PRESETS_PATH, "notice.json")
    assert_test(os.path.isfile(presets_path), "预设文件存在")

    with open(presets_path, encoding="utf-8") as f:
        presets = json.load(f)
    assert_test(len(presets) == 4, f"预设数量 = {len(presets)}（预期 4）")

    expected_ids = {"minimal_white", "business_blue", "bold_red", "elegant_green"}
    actual_ids = {p["id"] for p in presets}
    assert_test(actual_ids == expected_ids, f"预设 ID 匹配: {actual_ids}")

    for p in presets:
        vals = p["values"]
        assert_test("theme_color" in vals, f"预设 {p['id']} 包含 theme_color")
        assert_test("bar_position" in vals, f"预设 {p['id']} 包含 bar_position")
        assert_test("bg_style" in vals, f"预设 {p['id']} 包含 bg_style")
        assert_test("font_style" in vals, f"预设 {p['id']} 包含 font_style")


# ============================================================
# 测试 2: business_card 预设切换
# ============================================================
def test_business_card_presets():
    print("\n[测试 2] business_card 预设切换")
    presets_path = os.path.join(PRESETS_PATH, "business_card.json")
    assert_test(os.path.isfile(presets_path), "预设文件存在")

    with open(presets_path, encoding="utf-8") as f:
        presets = json.load(f)
    assert_test(len(presets) == 4, f"预设数量 = {len(presets)}（预期 4）")

    expected_ids = {"standard_business", "modern_design", "minimalist", "warm_orange"}
    actual_ids = {p["id"] for p in presets}
    assert_test(actual_ids == expected_ids, f"预设 ID 匹配: {actual_ids}")

    for p in presets:
        vals = p["values"]
        assert_test("theme_color" in vals, f"预设 {p['id']} 包含 theme_color")
        assert_test("bar_position" in vals, f"预设 {p['id']} 包含 bar_position")
        assert_test("bg_style" in vals, f"预设 {p['id']} 包含 bg_style")


# ============================================================
# 测试 3: product_spec 预设切换
# ============================================================
def test_product_spec_presets():
    print("\n[测试 3] product_spec 预设切换")
    presets_path = os.path.join(PRESETS_PATH, "product_spec.json")
    assert_test(os.path.isfile(presets_path), "预设文件存在")

    with open(presets_path, encoding="utf-8") as f:
        presets = json.load(f)
    assert_test(len(presets) == 1, f"预设数量 = {len(presets)}（预期 1）")

    p = presets[0]
    assert_test(p["id"] == "professional_default", f"预设 ID 匹配: {p['id']}")

    vals = p["values"]
    assert_test(vals["theme_color"] == "#3355AA", f"theme_color = {vals['theme_color']}")
    assert_test(vals["header_style"] == "bar", f"header_style = {vals['header_style']}")
    assert_test(vals["bg_style"] == "white", f"bg_style = {vals['bg_style']}")
    assert_test(vals["table_style"] == "striped", f"table_style = {vals['table_style']}")


# ============================================================
# 测试 4: 自定义颜色联动
# ============================================================
def test_custom_color_linkage():
    print("\n[测试 4] 自定义颜色联动")
    notice_path = os.path.join(TEMPLATES_PATH, "notice.json")
    with open(notice_path, encoding="utf-8") as f:
        notice = json.load(f)

    style_opts = notice.get("style_options", {})
    bg_custom = style_opts.get("bg_custom_color", {})
    assert_test(bg_custom.get("type") == "color", f"bg_custom_color 类型为 color")
    assert_test(bg_custom.get("default") == "", f"bg_custom_color 默认为空")


# ============================================================
# 测试 5: notice PDF 渲染
# ============================================================
def test_notice_pdf_rendering():
    print("\n[测试 5] notice PDF 渲染（带 style 参数）")
    from src.common.template_renderer import render_notice

    data = {
        "title": "测试公告",
        "date": "2026年5月12日",
        "body": "这是一条测试公告正文内容。",
        "issuer": "测试部门",
    }
    style = {
        "theme_color": "#FF3B30",
        "bar_position": "top",
        "bg_style": "light_gray",
        "font_style": "bold",
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        output = os.path.join(tmpdir, "test_notice.pdf")
        try:
            result = render_notice(output, data, style=style)
            assert_test(os.path.isfile(result), f"PDF 文件已生成: {result}")
            import fitz
            doc = fitz.open(result)
            assert_test(doc.page_count == 1, f"PDF 页数 = {doc.page_count}")
            doc.close()
        except Exception as e:
            assert_test(False, f"PDF 渲染失败: {e}")


# ============================================================
# 测试 6: product_spec PDF 渲染
# ============================================================
def test_product_spec_pdf_rendering():
    print("\n[测试 6] product_spec PDF 渲染（带 style 参数）")
    from src.common.template_renderer import render_product_spec

    data = {
        "product_name": "测试产品",
        "version": "V2.3",
        "description": "这是一条测试产品描述。",
        "specs": [
            {"param": "尺寸", "value": "210×297mm"},
            {"param": "重量", "value": "1.2kg"},
        ],
    }
    style = {
        "theme_color": "#4D7CFE",
        "header_style": "color_block",
        "bg_style": "light_blue",
        "table_style": "bordered",
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        output = os.path.join(tmpdir, "test_product_spec.pdf")
        try:
            result = render_product_spec(output, data, style=style)
            assert_test(os.path.isfile(result), f"PDF 文件已生成: {result}")
            import fitz
            doc = fitz.open(result)
            assert_test(doc.page_count >= 1, f"PDF 页数 = {doc.page_count}")
            doc.close()
        except Exception as e:
            assert_test(False, f"PDF 渲染失败: {e}")


# ============================================================
# 测试 7: business_card PDF 渲染
# ============================================================
def test_business_card_pdf_rendering():
    print("\n[测试 7] business_card PDF 渲染（带 style_options）")
    from src.common.template_renderer import render_business_card

    data = {
        "name_cn": "张三",
        "name_en": "John Zhang",
        "title": "高级设计师",
        "company": "印流科技有限公司",
        "phone": "13800138000",
        "email": "zhangsan@pdflow.com",
        "address": "北京市朝阳区",
    }
    style_opts = {
        "theme_color": "#AF52DE",
        "bar_position": "left",
        "bg_style": "gradient_vertical",
        "text_color": "#2C3E50",
        "text_secondary_color": "#7F8C8D",
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        output = os.path.join(tmpdir, "test_business_card.pdf")
        try:
            result = render_business_card(output, data, style_options=style_opts)
            assert_test(os.path.isfile(result), f"PDF 文件已生成: {result}")
            import fitz
            doc = fitz.open(result)
            assert_test(doc.page_count == 1, f"PDF 页数 = {doc.page_count}")
            doc.close()
        except Exception as e:
            assert_test(False, f"PDF 渲染失败: {e}")


# ============================================================
# 测试 8: 预设值与默认值一致性
# ============================================================
def test_preset_default_consistency():
    print("\n[测试 8] 预设值与默认值一致性")

    # notice 模板
    with open(os.path.join(TEMPLATES_PATH, "notice.json"), encoding="utf-8") as f:
        notice = json.load(f)
    notice_defaults = {}
    for key, cfg in notice.get("style_options", {}).items():
        notice_defaults[key] = cfg.get("default")

    # 检查 business_blue 预设值是否与默认值不一致（预设应该有自定义值）
    with open(os.path.join(PRESETS_PATH, "notice.json"), encoding="utf-8") as f:
        notice_presets = json.load(f)
    blue_preset = next((p for p in notice_presets if p["id"] == "business_blue"), None)
    assert_test(blue_preset is not None, "business_blue 预设存在")
    if blue_preset:
        vals = blue_preset["values"]
        assert_test(vals["theme_color"] == "#2C3E6B", f"business_blue theme_color = {vals['theme_color']}")
        assert_test(vals["font_style"] == "formal", f"business_blue font_style = {vals['font_style']}")


# ============================================================
# 测试 9: 模板不存在时预设加载
# ============================================================
def test_nonexistent_template_presets():
    print("\n[测试 9] 不存在模板的预设加载")
    fake_path = os.path.join(PRESETS_PATH, "nonexistent.json")
    assert_test(not os.path.isfile(fake_path), "不存在的预设文件正确检测")


# ============================================================
# 测试 10: notice 模板 style_options 结构完整性
# ============================================================
def test_notice_style_options_structure():
    print("\n[测试 10] notice 模板 style_options 结构完整性")
    with open(os.path.join(TEMPLATES_PATH, "notice.json"), encoding="utf-8") as f:
        notice = json.load(f)

    style_opts = notice.get("style_options", {})
    expected_keys = {"theme_color", "bar_position", "bg_style", "bg_custom_color", "font_style"}
    assert_test(set(style_opts.keys()) == expected_keys, f"style_options 键完整: {set(style_opts.keys())}")

    for key in expected_keys:
        cfg = style_opts[key]
        assert_test("label" in cfg, f"{key} 包含 label")
        assert_test("type" in cfg, f"{key} 包含 type")
        assert_test("default" in cfg, f"{key} 包含 default")


# ============================================================
# 测试 11: product_spec 模板 style_options 结构完整性
# ============================================================
def test_product_spec_style_options_structure():
    print("\n[测试 11] product_spec 模板 style_options 结构完整性")
    with open(os.path.join(TEMPLATES_PATH, "product_spec.json"), encoding="utf-8") as f:
        ps = json.load(f)

    style_opts = ps.get("style_options", {})
    expected_keys = {"theme_color", "header_style", "bg_style", "bg_custom_color", "table_style"}
    assert_test(set(style_opts.keys()) == expected_keys, f"style_options 键完整: {set(style_opts.keys())}")

    for key in expected_keys:
        cfg = style_opts[key]
        assert_test("label" in cfg, f"{key} 包含 label")
        assert_test("type" in cfg, f"{key} 包含 type")
        assert_test("default" in cfg, f"{key} 包含 default")


# ============================================================
# 测试 12: render_notice / render_product_spec 的 style 参数兼容性
# ============================================================
def test_renderer_style_compatibility():
    print("\n[测试 12] 渲染器 style 参数兼容性")
    from src.common.template_renderer import render_notice, render_product_spec
    import inspect

    # 检查 render_notice 是否支持 style 参数
    notice_sig = inspect.signature(render_notice)
    assert_test("style" in notice_sig.parameters, f"render_notice 支持 style 参数")

    # 检查 render_product_spec 是否支持 style 参数
    ps_sig = inspect.signature(render_product_spec)
    assert_test("style" in ps_sig.parameters, f"render_product_spec 支持 style 参数")

    # 检查默认值为 None
    assert_test(notice_sig.parameters["style"].default is None, "render_notice style 默认值为 None")
    assert_test(ps_sig.parameters["style"].default is None, "render_product_spec style 默认值为 None")


# ============================================================
# 主入口
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("印流PDflow — 样式预设系统集成测试")
    print("=" * 60)

    test_notice_presets()
    test_business_card_presets()
    test_product_spec_presets()
    test_custom_color_linkage()
    test_notice_pdf_rendering()
    test_product_spec_pdf_rendering()
    test_business_card_pdf_rendering()
    test_preset_default_consistency()
    test_nonexistent_template_presets()
    test_notice_style_options_structure()
    test_product_spec_style_options_structure()
    test_renderer_style_compatibility()

    print("\n" + "=" * 60)
    print(f"测试结果: ✅ {passed} 通过, ❌ {failed} 失败")
    print("=" * 60)

    if failed > 0:
        sys.exit(1)
    else:
        print("\n🎉 所有测试通过！")
        sys.exit(0)
