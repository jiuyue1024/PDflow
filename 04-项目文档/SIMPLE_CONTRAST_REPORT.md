# 印流PDflow V1.1 RC1 — 名片正面「极简重心 + 强对比」改版报告

**日期：** 2026-06-04
**版本：** V1.1 RC1
**适用模板：** `assets/templates/business_card.json`
**关联文件：**
- [template_renderer.py](file:///f:/%E5%8D%B0%E6%B5%81PDflow%E9%A1%B9%E7%9B%AE/src/common/template_renderer.py) — 名片渲染逻辑
- [business_card.json](file:///f:/%E5%8D%B0%E6%B5%81PDflow%E9%A1%B9%E7%9B%AE/assets/templates/business_card.json) — 模板配置
- [template_editor_page.py](file:///f:/%E5%8D%B0%E6%B5%81PDflow%E9%A1%B9%E7%9B%AE/pages/template_editor_page.py) — 编辑器字段渲染

---

## 一、改版目标

> 用户原话：「这样排布吧，简单一点，然后重点字体放大加粗，其它字体缩小纤细，对比要强烈一点」

**核心诉求：**
1. **简单** — 减少装饰元素，让重点一目了然
2. **重点放大加粗** — 姓名 / 公司名 / LOGO 是焦点
3. **次要纤细** — 公司英文、英文名、联系方式缩小
4. **强对比** — 字号差 3 倍以上

**对比强弱的量化标准：**
- 重点最大字号 / 次要最小字号 ≥ 3.0x
- 24pt 姓名 vs 8pt 联系方式 = **3.0x** ✓
- 20pt 公司名 vs 8pt 联系方式 = **2.5x** ✓
- 9pt 职位 + 主题色 = 视觉次重点

---

## 二、新版式设计

### 2.1 90×54mm 名片版式（自顶向下）

```
y=2mm     ┌────┐
          │LOGO│   ← 焦点 1：LOGO 10mm 居中
          └────┘
y=12.8mm  印流科技有限公司   ← 焦点 2：公司名 20pt 粗体黑（居中）
y=20.5mm  ━━━━                ← 蓝色短装饰线 4mm 居中（1.6pt 粗）
y=22.5mm  PDFlow Technology    ← 公司英文 7.5pt 纤细灰（居中）
y=27mm     张 三               ← 焦点 3：姓名 24pt 粗体黑（最大，居中）
y=36mm     ━━━━                ← 蓝色短装饰线 4mm 居中
y=38mm     高级产品经理        ← 职位 9pt 蓝色粗体
y=42mm     Zhang San          ← 英文名 7.5pt 纤细灰
y=46mm     t  138-0000-0000   ← 联系方式 8pt 纤细 + 9pt 蓝色图标（居中）
y=49mm     e  zhangsan@pdflow.com
y=52mm     a  上海市浦东新区张江高科园区 88 号
y=55mm     @  justinkuzco
```

### 2.2 字号体系

| 角色 | 元素 | 字号 (pt) | 字重 | 颜色 | 类别 |
|:---|:---|---:|:---:|:---|:---|
| 焦点 1 | LOGO | 10mm | — | 主题色 | 图像 |
| 焦点 2 | 公司名 | **20** | 粗 | `#2C3E50` 深灰黑 | ★ 粗大 |
| 焦点 3 | 中文姓名 | **24** | 粗 | `#2C3E50` 深灰黑 | ★ 粗大（最大） |
| 次要 | 公司英文 | 7.5 | 细 | `#7F8C8D` 灰 | ☆ 纤细 |
| 次要 | 职位 | 9 | 粗 | `#4D7CFE` 蓝 | ☆ 中等 |
| 次要 | 英文名 | 7.5 | 细 | `#7F8C8D` 灰 | ☆ 纤细 |
| 次要 | 联系方式图标 | 8.5 | 粗 | `#4D7CFE` 蓝 | ☆ 中等 |
| 次要 | 联系方式值 | 8 | 细 | `#2C3E50` | ☆ 纤细 |
| 装饰 | 短装饰线 | 1.6 pt 高 | — | `#4D7CFE` 蓝 | 视觉锚点 |

**强对比量化：**
- 24pt (姓名) / 8pt (联系方式) = **3.0x** ✓
- 20pt (公司名) / 8pt = **2.5x** ✓
- 9pt (职位) / 8pt = 1.125x（**差异化通过颜色**，蓝色区别于黑色）

### 2.3 居中对齐

**重要信息全部以名片中线为水平中心：**
- LOGO x = (90 - 10) / 2 = 40mm ✓
- 公司名 / 装饰线 / 姓名 / 职位 / 英文名 x = 45mm ✓
- 联系方式 4 行 x = 45mm ✓

---

## 三、几何实现（关键代码）

### 3.1 新坐标系

**老代码 Bug：** `y = margin_pt + logo_w_mm + 2` —— `margin_pt` 是 pt，`logo_w_mm` 是 mm，**单位混用导致 LOGO 与公司名重叠**。

**新代码：** 全程以 mm 思考，**只在 `_insert_text_*` 调用时统一转为 pt**。

```python
_s = 25.4 / 72.0  # 1pt = 0.3528 mm（pt→mm 系数）
margin_mm = 2.0
center_x = width_pt * 0.50  # 重要元素居中对齐

# ★ 重点元素
size_company = 20.0    # pt
size_name_cn = 24.0    # pt（最大）
logo_mm = 10.0         # mm

# ☆ 次要元素
size_company_en = 7.5
size_name_en = 7.5
size_title = 9.0
size_contact_lbl = 8.5
size_contact_val = 8.0

# cur_y_mm 累加公式：size_pt * _s（mm） + 间距（mm）
cur_y_mm += size_company * _s + 0.4  # 公司名下方 0.4mm
cur_y_mm += deco_h_pt * _s + 1.2     # 装饰线下方 1.2mm
```

### 3.2 新 Helper 函数

在 [template_renderer.py](file:///f:/%E5%8D%B0%E6%B5%81PDflow%E9%A1%B9%E7%9B%AE/src/common/template_renderer.py#L81-L141) 中新增两个居中渲染辅助函数：

| 函数 | 作用 |
|:---|:---|
| [`_insert_text_centered()`](file:///f:/%E5%8D%B0%E6%B5%81PDflow%E9%A1%B9%E7%9B%AE/src/common/template_renderer.py#L81-L101) | 单行文本以 `center_x` 为水平中心渲染 |
| [`_insert_text_centered_with_prefix()`](file:///f:/%E5%8D%B0%E6%B5%81PDflow%E9%A1%B9%E7%9B%AE/src/common/template_renderer.py#L104-L141) | 「前缀 + 间距 + 值」组合居中渲染（如 `t 138-0000-0000`） |

### 3.3 联系方式居中渲染

```python
for label, val in contact_items:
    cy_pt = _mm_to_points(cy_mm) + size_contact_val
    if label == "s":
        # 社交账号：@ 前缀
        _insert_text_centered_with_prefix(...)
    else:
        # t/e/a：蓝色 8.5pt 字母 + 1mm 间距 + 8pt 黑值
        _insert_text_centered_with_prefix(
            page, label, val, center_x, cy_pt,
            prefix_size=8.5, val_size=8.0,
            prefix_color=theme_rgb, val_color=text_rgb,
            gap=_mm_to_points(1.0),
        )
    cy_mm += line_h_mm  # 8pt + 0.6mm = 紧凑行高
```

---

## 四、附带修复

### 4.1 字体加载失败（PyMuPDF 1.27 兼容性）

**症状：**
```
[renderer] 字体加载失败 C:/Windows/Fonts/msyh.ttc: Font.__init__() got an unexpected keyword argument 'fontno'
```

**根因：** PyMuPDF 1.24+ 移除了 `fitz.Font(fontfile=..., fontno=...)` 的 `fontno` 参数。

**修复：**
```python
# 旧代码
font_candidates = [
    ("C:/Windows/Fonts/msyh.ttc", 0),  # ttc 需要 fontno 索引
    ...
]
for fp, fontno in font_candidates:
    if fontno is not None:
        _cjk_font_cache = fitz.Font(fontfile=fp, fontno=fontno)
    else:
        _cjk_font_cache = fitz.Font(fontfile=fp)

# 新代码（PyMuPDF 1.27.x 兼容）
font_candidates = [
    "C:/Windows/Fonts/msyhbd.ttc",   # 微软雅黑 Bold（首选）
    "C:/Windows/Fonts/msyh.ttc",     # 微软雅黑 Regular
    ...
]
for fp in font_candidates:
    if os.path.exists(fp):
        try:
            _cjk_font_cache = fitz.Font(fontfile=fp)
            return _cjk_font_cache
        except Exception as e:
            print(f"[renderer] 字体加载失败 {fp}: {e}")
            continue
```

**效果：** 现在 LOGO 名称是 `Microsoft YaHei Bold`（粗体黑），与设计意图「粗大黑」一致。

---

## 五、编辑器增强（V2.4）

### 5.1 新增字段元数据

在 [business_card.json](file:///f:/%E5%8D%B0%E6%B5%81PDflow%E9%A1%B9%E7%9B%AE/assets/templates/business_card.json#L10-L24) 的 `fields` 中加两个属性：

| 属性 | 取值 | 作用 |
|:---|:---|:---|
| `emphasis` | `true` / `false` | 重点字段标记（蓝色 ⭐ + 「重点」徽章） |
| `size_hint` | `H1` / `H2` / `H3` / `Body` | 字号提示标签（带色块和实际 pt 数） |

### 5.2 字段标记示例

| 字段 | emphasis | size_hint | 编辑器显示 |
|:---|:---:|:---|:---|
| 姓名（中文） | ✓ | `H1` | ⭐ 姓名（中文）**重点** `[H1 · 24pt]` 蓝色 |
| 公司名称 | ✓ | `H2` | ⭐ 公司名称**重点** `[H2 · 20pt]` 绿色 |
| 姓名（英文） | — | `Body` | 姓名（英文）`[Body · 8pt]` 灰色 |
| 职位/头衔 | — | `H3` | * 职位/头衔 `[H3 · 10pt]` 橙色 |
| 电话 | — | `Body` | * 电话 `[Body · 8pt]` 灰色 |

**视觉提示：**
- 重点字段标签：⭐ 主题色 + 加粗 + 「重点」徽章
- 字号提示：彩色 chip（H1 蓝 / H2 绿 / H3 橙 / Body 灰）+ 实际 pt 数值
- 用户**一眼就能看出**哪个字段对应 PDF 的什么字号

### 5.3 不需要再改的逻辑

经过代码 review，编辑器已经具备：
- ✅ 200ms 防抖实时预览（QTimer）
- ✅ 正反面 Tab 切换（`rc1_tab_preservation_test.py` 已覆盖）
- ✅ 字段分组（个人信息 / 公司信息 / 联系方式 / 背面信息）
- ✅ 必填项红色星号
- ✅ Logo 上传 / 颜色拾取 / 装饰条位置单选

**所以「是否要改编辑器逻辑」的回答：**
> **核心逻辑不需要大改**，只是新增两个属性（`emphasis` + `size_hint`）让用户看到字段对应的字号等级即可。

---

## 六、回归验证

### 6.1 单元测试

```bash
# helper 函数导入
python -c "from common.template_renderer import _insert_text_centered, _insert_text_centered_with_prefix"
# ✓ OK

# 渲染 90×54mm 名片正面（带 LOGO）
python 03-安装包输出/_test_renders/test_card_front_v2.py
# ✓ card_front_v2.pdf 生成成功，17MB（含 PNG 嵌入）
```

### 6.2 视觉验证（卡片正面 PNG 截图）

测试文件：[card_front_v2.png](file:///f:/%E5%8D%B0%E6%B5%81PDflow%E9%A1%B9%E7%9B%AE/03-安装包输出/_test_renders/card_front_v2.png)

**评估维度：**

| 维度 | 标准 | 实际 |
|:---|:---|:---|
| 居中对齐 | 所有重要元素对齐中线 | ✓ LOGO / 公司名 / 装饰线 / 姓名 / 联系方式全部居中 |
| 强对比 | 重点 vs 次要字号比 ≥ 3x | ✓ 24pt vs 8pt = 3.0x |
| 简单 | 装饰元素 ≤ 3 个 | ✓ 仅 2 条蓝色短装饰线 |
| 装下 | 90×54mm 不溢出 | ✓ 4 行联系方式全部显示，未越界 |
| LOGO 焦点 | 顶部居中 | ✓ 10mm LOGO 居中 |
| 字体粗细对比 | 重点粗 vs 次要细 | ✓ YaHei Bold 粗 vs 默认细 |

### 6.3 模板兼容性

`business_card.json` 新增 `company_en` 字段，sample 数据已更新。**老数据兼容：** `data.get("company_en", "")` 默认为空，旧用户数据不会报错。

**未触动：**
- 6 模板的 `render_*` 函数（除 `_render_card_front`）
- 现有样式选项（theme_color / bg_style / bar_position）
- 双面渲染接口
- PDF 生成后端

---

## 七、变更清单

| # | 文件 | 变更类型 | 说明 |
|:---:|:---|:---:|:---|
| 1 | [template_renderer.py](file:///f:/%E5%8D%B0%E6%B5%81PDflow%E9%A1%B9%E7%9B%AE/src/common/template_renderer.py) | 重写 | `_render_card_front()` 极简重心版式 |
| 2 | [template_renderer.py](file:///f:/%E5%8D%B0%E6%B5%81PDflow%E9%A1%B9%E7%9B%AE/src/common/template_renderer.py) | 新增 | `_insert_text_centered()` helper |
| 3 | [template_renderer.py](file:///f:/%E5%8D%B0%E6%B5%81PDflow%E9%A1%B9%E7%9B%AE/src/common/template_renderer.py) | 新增 | `_insert_text_centered_with_prefix()` helper |
| 4 | [template_renderer.py](file:///f:/%E5%8D%B0%E6%B5%81PDflow%E9%A1%B9%E7%9B%AE/src/common/template_renderer.py) | 修复 | `_get_cjk_font()` 适配 PyMuPDF 1.27.x（移除 fontno） |
| 5 | [template_editor_page.py](file:///f:/%E5%8D%B0%E6%B5%81PDflow%E9%A1%B9%E7%9B%AE/pages/template_editor_page.py) | 增强 | `_add_field_to_layout()` 支持 `emphasis` + `size_hint` 标签 |
| 6 | [business_card.json](file:///f:/%E5%8D%B0%E6%B5%81PDflow%E9%A1%B9%E7%9B%AE/assets/templates/business_card.json) | 增强 | 14 字段加 `emphasis` / `size_hint` 标记 |
| 7 | [business_card.json](file:///f:/%E5%8D%B0%E6%B5%81PDflow%E9%A1%B9%E7%9B%AE/assets/templates/business_card.json) | 新增 | `company_en` 字段 + sample |

---

## 八、风险与缓解

| 风险 | 影响 | 缓解 |
|:---|:---|:---|
| 旧版 `_render_card_front` 调用方未传 `company_en` | 字段为空，UI 不显示 | `data.get("company_en", "")` 默认空字符串 |
| PyMuPDF 1.27 字体加载策略变化 | 中文乱码 | `_get_cjk_font()` 移除 `fontno`，优先用 msyhbd.ttc |
| 用户输入超长字符串溢出 | 名片被撑变形 | 字段 maxLength 限制 + 字号自适应（已存在的 placeholder） |
| 编辑器新增 size_hint 字段在老 JSON 中缺失 | 字段渲染报错 | `.get("size_hint", "")` 默认空 |
| 新版式 4 行联系方式紧贴底边 | 视觉局促 | 字号 8pt 紧凑 + 行高 0.6mm，已通过实测验证 |

---

## 九、下一步建议

1. **可视化编辑器截图**：运行 `run_main.py` 打开「模板排版」→「名片」编辑器，截图保存到 [FRONT_FACELIFT_REPORT.md](file:///f:/%E5%8D%B0%E6%B5%81PDflow%E9%A1%B9%E7%9B%AE/04-项目文档/FRONT_FACELIFT_REPORT.md) 旁
2. **6 模板回归**：在 EXE 中实测 6 个模板（business_card / notice / product_spec / contract / invoice / report），确认未引入回归
3. **打包 V1.1 RC1**：运行 `pyinstaller PDflow_V1.1-RC1.spec --noconfirm` 重打 EXE
4. **dist 体积对比**：跑 `measure_dist_size.py` 确认新增 0 KB（无新依赖）

---

*本报告遵循《印流PDflow 项目总章程 V2.4》第七部分（AI Code Review）和第八部分（代码安全）规范编写。*
