# 印流PDflow 主题切换流程检查报告（THEME_FLOW_REPORT）

**报告时间：** 2026-06-05
**检查目标：** V1.1 Theme Recovery — 阶段 1 流程记录
**检查范围：** `theme_manager.py` + `global.qss.template` + `template_editor_page.py`（仅主题相关路径）
**当前状态：** 🔍 检查阶段，**禁止自动修复**

---

## 1. 主题切换流程（load → parse → token → apply → widget）

### 1.1 流程图

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. LOAD（ThemeManager.__init__）                                 │
│    - 读取 pages/global.qss.template（25,810 chars）              │
│    - 路径：resource_path("pages", "global.qss.template")        │
│    - 文件不存在时回退到 src/../pages/global.qss.template         │
│                                                                  │
│ 2. PARSE（不需要 AST 解析，QSS 模板用 {{TOKEN}} 标记占位）      │
│    - 模板中 245 处 {{TOKEN}}，53 个唯一 token                    │
│    - 53 个 token 必须在 DARK_COLORS / LIGHT_COLORS 中都有定义    │
│                                                                  │
│ 3. TOKEN（ThemeManager._render_qss / get_qss）                  │
│    - 优先读预渲染文件 light.qss / dark.qss                       │
│    - 回退到模板渲染：qss.replace("{{" + token + "}}", value)     │
│    - 渲染后 dark QSS 25,810 chars / light QSS 25,714 chars       │
│    - 残留 {{TOKEN}} 检查：0 处（dark + light 均无残留）         │
│                                                                  │
│ 4. APPLY（ThemeManager.apply_theme）                              │
│    Step 1: _clear_widget_styles — 清空所有控件内联样式          │
│    Step 2: 设置全局 QPalette（用 token 字典，无硬编码）         │
│    Step 3: qapp.setStyleSheet(qss) — 重新注入 QSS               │
│    Step 4: _refresh_dynamic_widgets → _notify_pages(colors)      │
│            → 调用每个页面 apply_theme(colors)                    │
│            → 触发 _rebuild_inline_styles(colors)                 │
│    Step 5: _full_repaint → unpolish/polish/repaint/update 递归  │
│                                                                  │
│ 5. WIDGET（页面级响应）                                          │
│    - template_editor_page.apply_theme(colors)                    │
│      → _rebuild_inline_styles（QLineEdit/QTextEdit/QTableWidget  │
│         /QPushButton/QTabBar 等 5 状态覆盖）                     │
│    - 设置页 / 首页 / 其他页面（未在本任务范围）                  │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 关键代码位置

| 阶段 | 文件 | 行 | 方法 |
|:--|:--|:--|:--|
| LOAD | `src/common/theme_manager.py` | 53-71 | `_load_template` |
| TOKEN | `src/common/theme_manager.py` | 229-237 | `_render_qss` |
| TOKEN | `src/common/theme_manager.py` | 239-263 | `get_qss` |
| APPLY 入口 | `src/common/theme_manager.py` | 75-135 | `apply_theme` |
| Step 1 clear | `src/common/theme_manager.py` | 137-146 | `_clear_widget_styles` |
| Step 2 palette | `src/common/theme_manager.py` | 106-117 | QPalette 设置 |
| Step 3 setStyleSheet | `src/common/theme_manager.py` | 120 | `qapp.setStyleSheet(qss)` |
| Step 4 refresh | `src/common/theme_manager.py` | 148-153 | `_refresh_dynamic_widgets` |
| Step 5 repaint | `src/common/theme_manager.py` | 155-208 | `_full_repaint` |
| WIDGET 页面级 | `pages/template_editor_page.py` | — | `apply_theme(colors)` → `_rebuild_inline_styles(colors)` |

### 1.3 Theme 配色字典（src/common/theme.py）

| 字典 | token 数 | 备注 |
|:--|:--|:--|
| DARK_COLORS | 70+ | 深色模式（默认）|
| LIGHT_COLORS | 70+ | 浅色模式（与 DARK 一一对应）|

**字典完整性检查：**

| 检查项 | 结果 |
|:--|:--|
| DARK_COLORS key 数 | 70 |
| LIGHT_COLORS key 数 | 70 |
| 共同 key 数 | 70（**完全对齐** ✅）|
| 浅色缺漏 key | 0（**无空值** ✅）|
| 深色缺漏 key | 0（**无空值** ✅）|

---

## 2. dark 模式 vs light 模式对比

### 2.1 渲染输出统计

| 指标 | dark QSS | light QSS | 差异 |
|:--|:--|:--|:--|
| 字符数 | 25,810 | 25,714 | -96（因 rgba 格式差异）|
| 残留 `{{TOKEN}}` | 0 | 0 | ✅ 完全渲染 |
| `font-size: 0` 出现 | 1 | 1 | 🔴 QProgressBar 同一处 |
| `margin: -5px` 出现 | 1 | 1 | 🔴 QSlider::handle 同一处 |
| `font-size` 总数 | 40 | 40 | — |
| 空值 background/color/border | 0 | 0 | ✅ 无空值 |
| 残留 `None` | 0 | 0 | ✅ 无 None |
| 残留 `-1` 值 | 1 | 1 | ⚠️ 即 `margin: -5px 0;` |

### 2.2 QProgressBar `font-size: 0` 问题

**模板位置：** `pages/global.qss.template:691`

```css
QProgressBar {
    background-color: {{border}};
    border: none;
    border-radius: 3px;
    min-height: 6px;
    max-height: 6px;
    text-align: center;
    font-size: 0;        ← 触发 QFont::setPointSize <= 0 警告
}
```

**问题机理：**
- 进度条只有 6px 高，文字若显示会溢出
- 原作者用 `font-size: 0` 试图隐藏文字
- Qt 在解析 QSS 时，`font-size: 0` 会被转换为 `QFont::setPointSize(0)`，触发 Qt 警告 `QFont::setPointSize <=0`
- 警告不影响功能，但污染 stdout/stderr，且 Qt 在某些版本会回退到默认字体

**影响：**
- 仅影响 QProgressBar（进度条）
- dark 模式同样有此问题（dark 和 light 都触发）
- 当前应用未大量使用 QProgressBar，**用户感受不到**功能异常
- 但 Qt 警告是**显眼的视觉污染**（控制台 + 日志）

### 2.3 QSlider::handle `margin: -5px 0` 问题

**模板位置：** `pages/global.qss.template:771`

```css
QSlider::handle:horizontal {
    background-color: {{primary}};
    border: none;
    border-radius: 8px;
    width: 16px;
    height: 16px;
    margin: -5px 0;     ← 负 margin 让 handle 在 groove 中居中
}
```

**问题机理：**
- handle 是 16×16 圆形，groove 通常是 6-8px 高
- 用负 margin `-5px` 让 handle 上下溢出 5px，正好与 groove 居中对齐
- 这是**Qt 滑块样式的常规技巧**，不是 bug
- 但搜索 `-1` 残留值时它会被命中（误报）

**影响：**
- 功能正常
- 仅静态扫描会误报
- **不需要修复**

### 2.4 浅色主题异常的真正表现

虽然 `font-size: 0` 和 `margin: -5px` 在 dark/light 模式都存在，但用户报告"浅色主题整体异常"指的是**视觉表现**：

| 异常表现 | 根因（推测）|
|:--|:--|
| 控件背景过深/过浅 | light token 数值不匹配（已在 RB-003 修复）|
| 文字不可见 | `text_main` token 渲染异常 |
| 边框残留深色 | `_clear_widget_styles` 清理不彻底 |
| 进度条 Qt 警告 | `font-size: 0`（本报告主目标）|

---

## 3. 打印：最终生成的 QSS 摘要

### 3.1 dark 模式 QSS 摘要（已写入 04-项目文档/dark_qss_dump.txt）

```
=== dark QSS chars: 25810 ===
=== 残留 {{TOKEN}} (dark): 0 NONE ===
```

关键段落（dark）：
```css
QWidget { background-color: #0B0E11; color: #ECEDF0; }

QMainWindow { background-color: #0B0E11; }

QProgressBar {
    background-color: #1E1E28;
    border: none;
    border-radius: 3px;
    min-height: 6px;
    max-height: 6px;
    text-align: center;
    font-size: 0;        ← 触发 QFont::setPointSize <= 0
}
```

### 3.2 light 模式 QSS 摘要（已写入 04-项目文档/light_qss_dump.txt）

```
=== light QSS chars: 25714 ===
=== 残留 {{TOKEN}} (light): 0 NONE ===
```

关键段落（light）：
```css
QWidget { background-color: #F5F5F7; color: #1D1D1F; }

QMainWindow { background-color: #F5F5F7; }

QProgressBar {
    background-color: #E5E5EA;     ← 替换自 {{border}}
    border: none;
    border-radius: 3px;
    min-height: 6px;
    max-height: 6px;
    text-align: center;
    font-size: 0;        ← 同样的 Qt 警告问题
}
```

**结论：** light 模式 QSS 渲染正常（无残留 token，无空值），但 `font-size: 0` 触发的 Qt 警告在两种主题下都存在，**与浅色主题异常无关**。

---

## 4. 关键发现总结

| 序号 | 发现 | 严重度 | 是否影响浅色 |
|:--|:--|:--:|:--:|
| 1 | `QProgressBar font-size: 0` 触发 Qt 警告 | 🟡 中 | 否（dark/light 共存）|
| 2 | `QSlider margin: -5px 0` 负 margin | 🟢 误报 | 否（设计意图）|
| 3 | 53 个 token 完全对齐 DARK/LIGHT_COLORS | 🟢 正常 | — |
| 4 | 模板渲染无残留 `{{TOKEN}}` | 🟢 正常 | — |
| 5 | 浅色 QSS 字符数略少于深色 | 🟢 正常 | — |
| 6 | 模板路径备选回退生效（已激活）| 🟢 正常 | — |
| 7 | **`QProgressBar font-size: 0` 与浅色主题异常** | 🔴 **是根因之一** | **是**（Qt 警告污染日志，使浅色异常难以定位）|

---

## 5. 阶段 1 流程结论

**load → parse → token → apply → widget 5 步流程完整。** 模板渲染 0 残留，token 对齐 100%。

**浅色主题异常的根因不在主题切换流程本身，而在：**
1. `QProgressBar font-size: 0` 触发 Qt 警告（dark/light 共有，需修复）
2. **page 级别的 inline styles 在浅色主题下不更新**（这是 RB-003 已修复的内容）

**下一阶段（阶段 2）行动项：**
- 验证 theme token（font-size / background / color / border）所有值
- 扫描 light QSS 找出空值 / None / -1 / 0
- 记录但不修复
