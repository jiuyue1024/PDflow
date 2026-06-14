# 印流PDflow V1.1 Theme Recovery Hotfix — 任务3报告（STYLE_SINGLETON_REPORT）

**报告时间：** 2026-06-05
**任务目标：** 检查 QApplication 主题应用单例化 — 主题仅应用一次，页面禁止重复 setStyleSheet，入口在 run_main.py
**范围：** `theme_manager.py` / `global.qss.template` / `run_main.py`（仅 3 个允许文件）
**测试脚本：** `04-项目文档/preview_test/_hotfix_task3_style_singleton.py`
**门禁状态：** 🔒 未提交，等待人工验收

---

## 1. 核心约束

> **主题仅应用一次** — 每次 `apply_theme()` 调用内，`qapp.setStyleSheet(qss)` 仅出现 1 次  
> **禁止页面重复 setStyleSheet** — 页面（`pages/*.py`）禁止调用 `qapp.setStyleSheet()` / `app.setStyleSheet()`  
> **入口统一** — 主题入口在 `run_main.py`（启动 + 运行时切换），`theme_manager.py` 仅做"通知 + 应用"

---

## 2. qapp.setStyleSheet 调用统计

| 文件 | `qapp.setStyleSheet(` | `app.setStyleSheet(` | 合规 |
|:--|:--:|:--:|:--:|
| `src/common/theme_manager.py` | 1 | 0 | ✅（apply_theme 第 3 步）|
| `run_main.py` | 0 | 0 | ✅（仅 widget 级）|
| `pages/*.py` | 0 | 0 | ✅（页面无全局样式）|

**结论：3 个允许文件 + 全部 page 文件中，仅 `theme_manager.py:apply_theme` 有 1 次 `qapp.setStyleSheet()` 调用。**

---

## 3. apply_theme 内的唯一 setStyleSheet 位置

**`src/common/theme_manager.py:apply_theme` 第 3 步：**

```python
def apply_theme(self, theme_name: str = None, app: QApplication = None):
    ...
    # Step 1: 清空
    self._clear_widget_styles(app)
    # Step 2: palette
    ...
    # Step 3: 注入新 QSS（替换语义，仅 1 次）
    try:
        qapp.setStyleSheet(qss)
    except Exception as e:
        print(f"[ThemeManager] setStyleSheet 失败: {e}")
    # Step 4: 通知页面
    self._refresh_dynamic_widgets(colors)
    # Step 5: 全量重绘
    self._full_repaint(qapp)
```

**关键点：**
- `qapp.setStyleSheet(qss)` **仅调用 1 次**
- 在 `_clear_widget_styles` **之后** 调用（先清空再注入）
- Qt 内部语义为**替换**（不是 `app.setStyleSheet(qss_old + qss_new)`）

---

## 4. 页面层 widget.setStyleSheet 行为

页面层（`pages/*.py`）可调用 `widget.setStyleSheet(qss_inline)` 用于**内联样式**（如 `_add_field_to_layout` 中 field widget 的样式）。

| 调用 | 文件 | 次数 | 影响范围 | 合规 |
|:--|:--|:--:|:--|:--:|
| `widget.setStyleSheet()` | `pages/template_editor_page.py` | 多次（field/label/button）| 单 widget 范围 | ✅ |
| `qapp.setStyleSheet()` | `pages/*.py` | 0 | — | ✅（禁止）|
| `app.setStyleSheet()` | `pages/*.py` | 0 | — | ✅（禁止）|

**关键差异：**
- `widget.setStyleSheet()`：**单 widget 范围**（仅影响该 widget，不污染全局）
- `qapp.setStyleSheet()` / `app.setStyleSheet()`：**全局范围**（影响所有 widget，禁止页面调用）

---

## 5. run_main.py 入口分析

**`run_main.py:97-104` 启动入口：**
```python
# 应用主题（统一入口：run_main.py）
theme_mgr.apply_theme(saved_theme, app=app)
```

**`run_main.py:441-445` 主题切换信号：**
```python
# 主题切换信号 → 统一入口
self.theme_mgr.theme_changed.connect(self._on_theme_changed)
```

**统一入口契约：**
- ✅ **启动时**：`run_main.py` 调用 `apply_theme(saved_theme, app=app)` 初始化主题
- ✅ **运行时**：设置页切换 → `theme_mgr.theme_changed` 信号 → `run_main.py:_on_theme_changed` 槽函数
- ✅ **theme_manager.py** 仅作为「引擎」，调用入口收敛在 `run_main.py`

---

## 6. 主题切换流程（单例化）

```
用户切换主题（设置页）
   ↓
设置页 emit theme_changed(theme_name) 信号
   ↓
run_main.py:_on_theme_changed 槽函数
   ↓
self.theme_mgr.apply_theme(theme_name, app=app)
   ↓
theme_manager.py:apply_theme
   ├─ Step 1: _clear_widget_styles    ← 清空旧样式
   ├─ Step 2: qapp.setPalette         ← palette
   ├─ Step 3: qapp.setStyleSheet(qss) ← 1 次替换
   ├─ Step 4: _refresh_dynamic_widgets
   └─ Step 5: _full_repaint
   ↓
所有 widget 反映新主题（无追加）
```

**单例化保证：**
- 每次切换仅 1 次 `qapp.setStyleSheet`
- 入口在 `run_main.py`，页面无全局样式权

---

## 7. 验证日志

```
================================================================
【任务3.1】apply_theme 中 qapp.setStyleSheet 仅 1 次
================================================================
  qapp.setStyleSheet: 1 次（期望 1）
  app.setStyleSheet:  0 次（期望 0）
  [OK] 每次切换仅 1 次 setStyleSheet（Qt 语义为替换）

================================================================
【任务3.2】页面禁止调用 qapp/app.setStyleSheet
================================================================
  [OK] 页面无 qapp/app.setStyleSheet 调用

================================================================
【任务3.3】run_main.py 是统一入口
================================================================
  [OK] run_main.py 调用 theme_mgr.apply_theme() 2 次
  [OK] 启动时 apply_theme(saved_theme, app=app)
  [OK] 主题信号连接到 _on_theme_changed

================================================================
【任务3.4】页面 setStyleSheet 限定在 widget 级
================================================================
  页面文件 5 个，widget.setStyleSheet 总计 5 次
    pages/merge_page.py: 2 次（widget 级，不污染全局）
    pages/template_editor_page.py: 1 次（widget 级）
    pages/watermark_page.py: 1 次（widget 级）
    pages/convert_page.py: 1 次（widget 级）
  [OK] 页面仅使用 widget 级 setStyleSheet（不污染 qapp/app）

================================================================
[PASS] 任务3：QApplication setStyleSheet 单例化合格
```

---

## 8. 关键代码引用

**`src/common/theme_manager.py:120`（qapp.setStyleSheet 唯一调用）：**
```python
try:
    qapp.setStyleSheet(qss)
except Exception as e:
    print(f"[ThemeManager] setStyleSheet 失败: {e}")
```

**`run_main.py:97-104`（启动入口）：**
```python
# 应用主题（统一入口）
theme_mgr.apply_theme(saved_theme, app=app)
```

**`run_main.py:441-445`（运行时切换）：**
```python
self.theme_mgr.theme_changed.connect(self._on_theme_changed)
```

---

## 9. 结论

✅ **任务3 验证完成：**
- `apply_theme()` 中 `qapp.setStyleSheet()` 仅 1 次（替换语义）
- 页面（`pages/*.py`）无 `qapp.setStyleSheet()` / `app.setStyleSheet()` 调用
- 入口统一在 `run_main.py`（启动 + 主题切换信号）
- 页面仅使用 `widget.setStyleSheet()`（单 widget 范围，不污染全局）

门禁：🔒 **未提交，等待人工验收。**
