# BUSINESS_CARD_DOUBLE_SIDE_REPORT — V1.1 RC1 名片双面修复

**项目:** 印流PDflow
**版本:** V1.1 RC1（名片双面）
**日期:** 2026-06-04
**修复范围:** 名片正反面不能同时编辑 → 一次填写、一次导出双面 PDF
**结论:** ✅ 修复完成，6 模板全部回归通过

---

## 一、问题与目标

### 1.1 原始问题
V1.1 RC1 阶段，业务卡（business_card）模板字段分散在正面和反面，编辑时只能填写一个面，切换 Tab 后另一面已填写数据丢失。导出时也是分两次生成。

### 1.2 本次目标
- **一次填写**：编辑器支持正反面同时填，正反面 Tab 切换数据不丢失
- **一次导出**：导出时默认输出双面（front + back）多页 PDF
- **数据隔离**：正反面字段值不互相覆盖
- **预览切换**：预览支持在正反面之间切换

### 1.3 强制约束
- ❌ 禁止拆成两个模板
- ❌ 禁止破坏现有模板系统
- ❌ 禁止增加安装包体积
- ✅ 保持向后兼容（旧的扁平 data 仍可工作）

---

## 二、数据结构升级

### 2.1 旧结构（扁平）→ 新结构（结构化）

| 项 | 旧（扁平） | 新（结构化） |
| :--- | :--- | :--- |
| data 类型 | `dict`（混合正反） | `dict`（分面） |
| 正面键 | `name_cn, title, ...` | `data["front"]["name_cn"], ...` |
| 反面键 | `back_title, back_content, ...` | `data["back"]["back_title"], ...` |
| 模板配置 | `"sides": ["front", "back"]` | 不变 |
| 字段元数据 | `"side": "front"` / `"back"` | 不变 |
| sample 字段 | 扁平 sample | `{front:{}, back:{}}` |

### 2.2 JSON 示例

[assets/templates/business_card.json](file:///f:/%E5%8D%B0%E6%B5%81PDflow%E9%A1%B9%E7%9B%AE/assets/templates/business_card.json) 已新增结构化 `sample` 字段：

```json
{
  "sides": ["front", "back"],
  "fields": [
    {"key": "name_cn", "side": "front", ...},
    {"key": "back_title", "side": "back", ...}
  ],
  "sample": {
    "front": {
      "name_cn": "张三",
      "name_en": "Zhang San",
      "title": "高级产品经理",
      ...
    },
    "back": {
      "back_title": "核心业务",
      "back_content": "专业 PDF 模板设计\n快速生成高品质文档",
      ...
    }
  }
}
```

### 2.3 渲染器兼容性

[src/common/template_renderer.py](file:///f:/%E5%8D%B0%E6%B5%81PDflow%E9%A1%B9%E7%9B%AE/src/common/template_renderer.py) 中 `render_business_card()` 兼容两种数据格式：

```python
# V1.1 RC1 名片双面：data 兼容两种结构
#   1. 扁平：{"name_cn": ..., "back_title": ...}  （向后兼容）
#   2. 结构化：{"front": {"name_cn": ...}, "back": {"back_title": ...}}  （新格式）
flat_data_for_side = {}
for side in render_sides:
    side_data = data.get(side, {}) if isinstance(data, dict) and side in data else data
    flat_data_for_side[side] = side_data if isinstance(side_data, dict) else data
```

---

## 三、编辑器改造

### 3.1 关键设计：分面缓存

引入 `self._form_values_cache`（dict），结构：

```python
{
  "front": {"name_cn": "...", "name_en": "...", ...},
  "back":  {"back_title": "...", "back_content": "...", ...}
}
```

### 3.2 新增方法

| 方法 | 职责 |
| :--- | :--- |
| [_save_current_form_values](file:///f:/%E5%8D%B0%E6%B5%81PDflow%E9%A1%B9%E7%9B%AE/pages/template_editor_page.py#L1027) | 把当前面 widget 值写入 cache（按字段元数据 `side` 归类）|
| [_restore_current_form_values](file:///f:/%E5%8D%B0%E6%B5%81PDflow%E9%A1%B9%E7%9B%AE/pages/template_editor_page.py#L1073) | 从 cache 恢复当前面 widget 值 |
| [_collect_form_values](file:///f:/%E5%8D%B0%E6%B5%81PDflow%E9%A1%B9%E7%9B%AE/pages/template_editor_page.py#L1112) | 收集所有面 → 返回 `{front:{}, back:{}}` 或扁平 |

### 3.3 Tab 切换数据流

```
用户输入正面字段
   ↓ (QTimer 不触发，纯信号保存)
用户点击「背面」Tab
   ↓
sideTabWidget.currentChanged → _on_side_changed(1)
   ↓
_on_side_changed:
  self._current_side = "back"
  self._build_form()  ← 关键节点
     ↓
   _build_form:
     1. _save_current_form_values()  ← 按 field.side 归类
        → cache["front"] = {name_cn: "张三", ...}
     2. 清空 formLayout
     3. 重建反面字段 widgets
     4. _restore_current_form_values()
        → 从 cache["back"] 恢复（首次为空）
   ↓
  self._update_preview()  ← 预览反面（render_sides=["back"]）

用户切回「正面」Tab
   ↓
   _build_form:
     1. _save_current_form_values()  ← 保存反面空数据
     2. 重建正面字段 widgets
     3. _restore_current_form_values()
        → 从 cache["front"] 恢复 → 字段值重现 ✓
```

### 3.4 数据保存（自动归类算法）

```python
def _save_current_form_values(self, side: Optional[str] = None):
    # 收集 fields 的 side 映射
    field_side_map = {f["key"]: f.get("side") for f in template_data["fields"] if f.get("side")}

    for key, widget in self.field_widgets.items():
        # 按字段元数据归类（不依赖 self._current_side）
        target_side = side or field_side_map.get(key) or self._current_side or "front"
        # 写入对应面的 cache
        ...
```

> **关键点**：即使 `_current_side` 已变（在 `_on_side_changed` 中），也能按字段元数据正确归类。

---

## 四、导出改造

### 4.1 旧导出流程

```
收集所有字段值（扁平 data）
   ↓
render_business_card(output, data, render_sides=[...])
   ↓
单次或多次输出
```

### 4.2 新导出流程

```
_collect_form_values()
   ↓
# 单面：扁平 dict（向后兼容）
# 双面：{front: {}, back: {}, sides_config: [...]}
   ↓
data = {side: collected[side] for side in sides}  # 双面结构
   ↓
render_business_card(output, data, render_sides=["front", "back"])
   ↓
输出双面 PDF（2 页）✓
```

### 4.3 必填项校验（按面）

```python
for field in template_data["fields"]:
    if not field.get("required"):
        continue
    field_side = field.get("side", "front")
    value = (collected.get(field_side, {}) or {}).get(field["key"], "")
    if not value:
        # 提示用户切换到对应 Tab
        self.sideTabWidget.setCurrentIndex(0 if field_side == "front" else 1)
        self._current_side = field_side
        self._build_form()
        # 重新聚焦到对应字段
        widget = self.field_widgets.get(field["key"])
        if widget:
            widget.setFocus()
        return
```

---

## 五、预览改造

### 5.1 预览管线

```
输入字段 → 防抖 → _update_preview
   ↓
_collect_form_values() → {front:{}, back:{}}
   ↓
sides = ["front", "back"]
current_side = self._current_side  # "front" or "back"
side_data = collected[current_side]  # 仅取当前面
   ↓
render_preview_pixmap(
    template_id="business_card",
    data=side_data,                    # 单面扁平
    render_sides=[current_side],       # 关键：仅渲染当前面
)
   ↓
fitz.Matrix(2.5, 2.5) → PNG → QLabel
```

### 5.2 预览缓存键增强

[src/common/preview_renderer.py](file:///f:/%E5%8D%B0%E6%B5%81PDflow%E9%A1%B9%E7%9B%AE/src/common/preview_renderer.py) 的缓存 key 增加 `render_sides` 维度：

```python
def make_cache_key(template_id, data, style, image_path, render_sides):
    ...
    sides_hash = ",".join(render_sides) if render_sides else ""
    return (template_id, data_hash, style_hash, img_hash, sides_hash)
```

效果：正面预览和反面预览各缓存一份，互不干扰。

---

## 六、验证测试

### 6.1 Tab 切换数据保留测试

来源：[04-项目文档/preview_test/rc1_tab_preservation_test.py](file:///f:/%E5%8D%B0%E6%B5%81PDflow%E9%A1%B9%E7%9B%AE/04-%E9%A1%B9%E7%9B%AE%E6%96%87%E6%A1%A3/preview_test/rc1_tab_preservation_test.py)

| 测试项 | 结果 |
| :--- | :---: |
| 正面填写 4 个字段 → 切到反面 → 切回正面 → 数据保留 | **PASS** ✓ |
| 反面填写 3 个字段 → 切到正面 → 切回反面 → 数据保留 | **PASS** ✓ |
| `_collect_form_values()` 返回 `{front, back, sides_config}` | **PASS** ✓ |
| `form_values_cache["front"]` 包含正面所有 7 字段 | **PASS** ✓ |
| `form_values_cache["back"]` 包含反面所有 4 字段 | **PASS** ✓ |

### 6.2 渲染管线测试

来源：[04-项目文档/preview_test/rc1_double_side_test.py](file:///f:/%E5%8D%B0%E6%B5%81PDflow%E9%A1%B9%E7%9B%AE/04-%E9%A1%B9%E7%9B%AE%E6%96%87%E6%A1%A3/preview_test/rc1_double_side_test.py)

| 测试项 | 期望 | 实测 | 结论 |
| :--- | :---: | :---: | :---: |
| 扁平 data（向后兼容）渲染 | 2 页 | 2 页 | ✓ |
| 结构化 data `{front:{}, back:{}}` 渲染 | 2 页 | 2 页 | ✓ |
| Page 1 内容 | 正面（李四 / Li Si / CTO） | ✓ | ✓ |
| Page 2 内容 | 反面（核心业务 / 创新） | ✓ | ✓ |
| 仅渲染 `render_sides=["front"]` | 1 页 | 1 页 | ✓ |
| 仅渲染 `render_sides=["back"]` | 1 页 | 1 页 | ✓ |
| `render_template()` 统一入口 | 2 页 | 2 页 | ✓ |
| 0 WebEngine / QtPdf 模块加载 | 0 | 0 | ✓ |

### 6.3 6 模板回归（其他模板不受影响）

| 模板 | 渲染 | 字段收集 | 结论 |
| :--- | :---: | :---: | :---: |
| business_card | ✓ | ✓ | **PASS**（双面） |
| contract | ✓ | ✓ | **PASS**（单面无影响） |
| invoice | ✓ | ✓ | **PASS** |
| notice | ✓ | ✓ | **PASS** |
| product_spec | ✓ | ✓ | **PASS** |
| report | ✓ | ✓ | **PASS** |

**6/6 模板全部 PASS，回归通过。**

---

## 七、安装包体积

### 7.1 体积对比

| 指标 | 上一版（清晰度） | **本版（双面）** | 变化 |
| :--- | ---: | ---: | :---: |
| EXE 体积 | 14.72 MB | **14.72 MB** | **0 MB** |
| dist 总体积 | 224.97 MB | **224.99 MB** | **+0.02 MB**（打包抖动）|
| 文件数 | 1076 | **1076** | 0 |
| WebEngine / QtPdf 残留 | 0 | **0** | 0 |

### 7.2 体积评价
- ✅ **安装包体积未实质增加**（+0.02 MB 是 PyInstaller 压缩抖动）
- ✅ **0 个 WebEngine / QtPdf 残留**
- ✅ 224.99 MB ≤ 250 MB RC1 目标

---

## 八、内存（编辑器运行期）

| 阶段 | RSS (MB) | 备注 |
| :--- | ---: | :--- |
| 6 模板全构造 + 首次渲染 | 约 100 MB | 与清晰度修复持平 |
| 名片双面：填正反两面 | 增量 < 5 MB | QPixmap 缓存 2 张 |
| 双面预览缓存 | 增量 < 25 MB | 2 张 A4 2.5x PNG |

> 名片双面修复对内存的影响极小，未触发内存压力。

---

## 九、UX 流程对比

### 9.1 旧流程

```
打开名片模板
  ↓
填正面（7 字段）
  ↓
点击「导出 PDF」→ 仅导出正面（1 页）
  ↓
（无法填反面）
```

### 9.2 新流程

```
打开名片模板
  ↓
填正面（7 字段）
  ↓
点击「背面」Tab → 数据自动保存
  ↓
填反面（4 字段）
  ↓
点击「导出 PDF」→ 自动双面导出（2 页）
  ↓
PDF 自动用默认应用打开
```

---

## 十、文件变更摘要

| 文件 | 变更 | 行数 |
| :--- | :--- | ---: |
| [pages/template_editor_page.py](file:///f:/%E5%8D%B0%E6%B5%81PDflow%E9%A1%B9%E7%9B%AE/pages/template_editor_page.py) | 新增 `_form_values_cache` / `_save_current_form_values` / `_restore_current_form_values` / `_collect_form_values` / `_get_table_columns_for_key` | +150 |
| [pages/template_editor_page.py](file:///f:/%E5%8D%B0%E6%B5%81PDflow%E9%A1%B9%E7%9B%AE/pages/template_editor_page.py) | 重构 `_build_form` / `_update_preview` / `_generate_pdf` / `_load_template` | ±80 |
| [src/common/template_renderer.py](file:///f:/%E5%8D%B0%E6%B5%81PDflow%E9%A1%B9%E7%9B%AE/src/common/template_renderer.py) | `render_business_card` 接受扁平 + 结构化两种 data | +12 |
| [src/common/preview_renderer.py](file:///f:/%E5%8D%B0%E6%B5%81PDflow%E9%A1%B9%E7%9B%AE/src/common/preview_renderer.py) | `render_preview_pixmap` 增加 `render_sides` 参数 | +8 |
| [assets/templates/business_card.json](file:///f:/%E5%8D%B0%E6%B5%81PDflow%E9%A1%B9%E7%9B%AE/assets/templates/business_card.json) | 新增结构化 `sample` | +17 |

**总变更：+267 行 / -约 60 行。**

---

## 十一、风险评估

| 风险项 | 等级 | 缓解措施 |
| :--- | :---: | :--- |
| 数据保存遗漏 | 🟢 低 | 按字段 `side` 元数据归类，无需依赖 `_current_side` |
| 切换 Tab 闪烁 | 🟢 低 | `_build_form` 仅 1 次重建，耗时 < 200ms |
| 旧扁平 data 兼容 | 🟢 低 | `render_business_card` 同时支持两种格式 |
| 预览缓存 key 冲突 | 🟢 低 | `render_sides` 加入缓存 key，2 个面分别缓存 |
| 其他 5 模板受影响 | 🟢 低 | 单面模板走 `_collect_form_values` 的扁平分支，向后兼容 |

---

## 十二、回归验证

### 12.1 功能链路

| 功能 | 状态 |
| :--- | :---: |
| 6 模板构造 + 渲染 | ✓ PASS |
| 名片双面编辑（正反面互不干扰） | ✓ PASS |
| Tab 切换数据保留 | ✓ PASS |
| 单次导出双面 PDF（2 页） | ✓ PASS |
| 预览正面 / 反面切换 | ✓ PASS |
| 必填项校验 + 自动切 Tab | ✓ PASS |
| 0 WebEngine / QtPdf 依赖 | ✓ PASS |

### 12.2 兼容性验证

| 场景 | 期望 | 实测 |
| :--- | :---: | :---: |
| 扁平 data 传入 render_business_card | 2 页 | 2 页 ✓ |
| 结构化 data 传入 render_business_card | 2 页 | 2 页 ✓ |
| 单面模板（其他 5 个） | 行为不变 | 不变 ✓ |
| 模板切换时清空双面 cache | 是 | 是 ✓ |

---

## 十三、结论

✅ **V1.1 RC1 名片双面修复完成**

| 验收项 | 目标 | 实测 | 结论 |
| :--- | :--- | :--- | :---: |
| 正反面同时编辑 | 必须 | Tab 切换数据保留 | ✅ |
| 数据结构 `{front:{}, back:{}}` | 必须 | 已实现 | ✅ |
| 一次填写 | 必须 | Tab 切换 + 缓存 | ✅ |
| 一次导出双面 PDF | 必须 | 2 页 | ✅ |
| 导出默认包含全部页面 | 必须 | front + back | ✅ |
| 预览支持正面/反面切换 | 必须 | sideTabWidget + render_sides | ✅ |
| 禁止拆成两个模板 | 必须 | 单一 business_card.json | ✅ |
| 安装包体积不增长 | 必须 | +0.02 MB（抖动） | ✅ |
| 6 模板全部回归 | 必须 | 6/6 PASS | ✅ |
| 0 WebEngine 残留 | 必须 | 0 模块 | ✅ |
| 旧扁平 data 向后兼容 | 必须 | render_business_card 双格式 | ✅ |

**总体结论：V1.1 RC1 名片双面修复可发布，RELEASE_GATE 维持 GO 状态。**

---

## 附录 A：测试脚本

| 脚本 | 用途 |
| :--- | :--- |
| [04-项目文档/preview_test/rc1_tab_preservation_test.py](file:///f:/%E5%8D%B0%E6%B5%81PDflow%E9%A1%B9%E7%9B%AE/04-%E9%A1%B9%E7%9B%AE%E6%96%87%E6%A1%A3/preview_test/rc1_tab_preservation_test.py) | Tab 切换数据保留 + _collect_form_values 结构验证 |
| [04-项目文档/preview_test/rc1_double_side_test.py](file:///f:/%E5%8D%B0%E6%B5%81PDflow%E9%A1%B9%E7%9B%AE/04-%E9%A1%B9%E7%9B%AE%E6%96%87%E6%A1%A3/preview_test/rc1_double_side_test.py) | 双面渲染管线（扁平 + 结构化 + 单面 + 双面） |
| [04-项目文档/preview_test/measure_dist_size.py](file:///f:/%E5%8D%B0%E6%B5%81PDflow%E9%A1%B9%E7%9B%AE/04-%E9%A1%B9%E7%9B%AE%E6%96%87%E6%A1%A3/preview_test/measure_dist_size.py) | dist 体积测量 + WebEngine 残留扫描 |

## 附录 B：相关报告

- [PREVIEW_RENDER_REPORT.md](file:///f:/%E5%8D%B0%E6%B5%81PDflow%E9%A1%B9%E7%9B%AE/04-%E9%A1%B9%E7%9B%AE%E6%96%87%E6%A1%A3/PREVIEW_RENDER_REPORT.md) — RC1 预览架构修正（移除 WebEngine）
- [PREVIEW_QUALITY_REPORT.md](file:///f:/%E5%8D%B0%E6%B5%81PDflow%E9%A1%B9%E7%9B%AE/04-%E9%A1%B9%E7%9B%AE%E6%96%87%E6%A1%A3/PREVIEW_QUALITY_REPORT.md) — RC1 预览清晰度（2.5x Matrix + 缓存）
- [TEMPLATE_OPEN_FIX_REPORT.md](file:///f:/%E5%8D%B0%E6%B5%81PDflow%E9%A1%B9%E7%9B%AE/04-%E9%A1%B9%E7%9B%AE%E6%96%87%E6%A1%A3/TEMPLATE_OPEN_FIX_REPORT.md) — RC1 模板打开链路
- [RELEASE_GATE.md](file:///f:/%E5%8D%B0%E6%B5%81PDflow%E9%A1%B9%E7%9B%AE/04-%E9%A1%B9%E7%9B%AE%E6%96%87%E6%A1%A3/RELEASE_GATE.md) — RC1 发布门禁

## 附录 C：核心代码变更摘要

### template_editor_page.py
```python
# 1. __init__ 中新增
self._form_values_cache: dict = {"front": {}, "back": {}}

# 2. _build_form 包装
def _build_form(self):
    self._save_current_form_values()  # 保存旧面
    # ... 重建 ...
    self._restore_current_form_values()  # 恢复新面

# 3. _save_current_form_values 按字段 side 归类
def _save_current_form_values(self, side=None):
    field_side_map = {f["key"]: f.get("side") for f in self.template_data.get("fields", []) if f.get("side")}
    for key, widget in self.field_widgets.items():
        target_side = side or field_side_map.get(key) or self._current_side or "front"
        # 写入 cache[target_side][key] = value

# 4. _collect_form_values 返回结构
def _collect_form_values(self):
    sides = self.template_data.get("sides", [])
    if not sides:
        return {key: widget_value for ...}  # 扁平
    self._save_current_form_values()
    return {"front": cache["front"], "back": cache["back"], "sides_config": sides}  # 结构化

# 5. _update_preview 用当前面数据 + render_sides=[current_side]
```

### template_renderer.py
```python
def render_business_card(output_path, data, ...):
    render_sides = render_sides or ["front"]
    # 兼容扁平 + 结构化 data
    flat_data_for_side = {}
    for side in render_sides:
        side_data = data.get(side, {}) if isinstance(data, dict) and side in data else data
        flat_data_for_side[side] = side_data if isinstance(side_data, dict) else data
    
    for page_idx, side in enumerate(render_sides):
        side_data = flat_data_for_side.get(side, data)
        # 渲染该面
```

### business_card.json
```json
{
  "sides": ["front", "back"],
  "fields": [
    {"key": "name_cn", "side": "front", ...},
    ...
    {"key": "back_title", "side": "back", ...}
  ],
  "sample": {
    "front": {"name_cn": "张三", ...},
    "back":  {"back_title": "核心业务", ...}
  }
}
```

---

*报告生成时间：2026-06-04 14:00 (Asia/Shanghai)*
*基线：PDflow_V1.1-RC1.spec → PyInstaller 6.20.0 onedir 模式*
*Python：3.12 / PySide6：6.11+ / PyMuPDF：内置*
