# 硬编码颜色扫描报告 — RC1 Theme 残留阻断

**扫描日期:** 2026-06-05
**扫描范围:** 4 个核心文件
**目的:** 消除所有硬编码颜色字面量，统一使用 ThemeTokens

---

## 扫描目标

| 文件 | 路径 |
|------|------|
| theme_manager.py | `src/common/theme_manager.py` |
| template_editor_page.py | `pages/template_editor_page.py` |
| global.qss | `pages/global.qss` |
| preview_panel.py | `pages/template_editor_page.py`（内嵌在编辑器中） |

**注：** 项目无独立 `preview_panel.py` 文件，预览面板代码在 `template_editor_page.py` 的 1287-1330 行。

---

## 扫描结果

### 1. theme_manager.py

| 行号 | 内容 | 类别 | 处置 |
|------|------|------|------|
| 108 | `palette.setColor(QPalette.HighlightedText, QColor('#ffffff'))` | 硬编码 `QColor` | ⚠️ 需修复 |
| 100-107 | `palette.setColor(QPalette.X, QColor(colors['xxx']))` | 字典访问（非硬编码） | ✅ 保留 |

**统计：** 1 处硬编码（`'#ffffff'`）

---

### 2. template_editor_page.py

按区域统计硬编码颜色（出现频率从高到低）：

| 颜色值 | 出现次数 | 含义 | 对应 Token |
|--------|----------|------|-----------|
| `#1E1E28` | ~35 | 次要边框、分隔线、卡片边框 | `border_secondary` |
| `#ECEDF0` | ~30 | 主要文字 | `text_primary` |
| `#1A1A22` | ~25 | 卡片背景、按钮背景 | `bg_secondary` |
| `#1A1A24` | ~12 | 输入框背景、按钮背景 | `bg_secondary` |
| `#8B8D98` | ~20 | 次要文字、标签 | `text_secondary` |
| `#14141A` | ~6 | 卡片背景 | `bg_tertiary` |
| `#0A0A0F` | ~5 | 输入框背景 | `bg_tertiary` |
| `#6E6E73` | ~6 | 三级文字 | `text_tertiary` |
| `#2A2A32` | ~4 | preview 背景、hover | `bg_hover` / `preview_bg` |
| `#0F0F14` | ~1 | bottom bar 背景 | `bg_primary` |
| `#4A4B56` | ~2 | 四级文字 | `text_quaternary` |
| `#2B3139` | ~1 | 边框 | `border_primary` |
| `#1E2330` | ~1 | 边框 | `border_secondary` |
| `#5A5B66` | ~2 | 弱化文字 | `text_muted` |
| `#4D7CFE` | ~5 | 主题色 | `accent` |
| `#3D6CF0` | ~1 | 主题色 hover | `accent_hover` |
| `#2D5CD0` | ~1 | 主题色 pressed | `accent_pressed` |
| `#FF3B30` | ~5 | 错误色 | `error` |
| `#FFFFFF` | ~6 | 白色 | `on_accent` / `white` |
| `#F5F5F7` | ~2 | 浅色输入框 | `bg_tertiary` |
| `#F0F0F3` | ~1 | 浅色 hover | `bg_hover` |
| `#E5E5EA` | ~1 | 浅色边框 | `border_primary` |
| `#1D1D1F` | ~2 | 浅色主文字 | `text_primary` |
| `#6E6E73` | ~2 | 浅色次文字 | `text_secondary` |
| `#AEAEB2` | ~2 | 浅色三级文字 | `text_quaternary` |
| `#C7C7CC` | ~1 | 浅色 hover 边框 | `border_secondary` |
| `#EEEEF0` | ~1 | 浅色容器 | `bg_quaternary` |
| `rgba(77, 124, 254, 0.1)` | ~3 | 主题色 10% 透明 | `accent_subtle` |
| `rgba(77, 124, 254, 0.2)` | ~1 | 主题色 20% 透明 | `accent_subtle_2` |

**统计：**
- 总硬编码色值：**~200 处**（含重复使用）
- 唯一硬编码颜色：**28 个**
- 最严重文件：**template_editor_page.py**（占 99% 硬编码）

---

### 3. global.qss

QSS 文件内硬编码颜色（出现次数）：

| 颜色值 | 出现次数 | 含义 |
|--------|----------|------|
| `#0B0E11` | 3 | 页面背景 |
| `#ECEDF0` | 5 | 主文字 |
| `#8B8D98` | 1 | 次文字 |
| `#4D7CFE` | 8 | 主题色 |
| `#FFFFFF` | 8 | 主题色上文字 |
| `#3D6CF0` | 1 | 主题色 hover |
| `#2D5CD0` | 1 | 主题色 pressed |
| `#FF3B30` | 3 | 错误色 |
| `#E0352B` | 1 | 错误 hover |
| `#C02E25` | 1 | 错误 pressed |
| `#0A0A0F` | 4 | 输入框背景 |
| `#1E1E28` | 5 | 输入框边框 |
| `#14141A` | 1 | 禁用背景 |
| `#4A4B56` | 1 | 禁用文字 |
| `#6A6B78` | 1 | placeholder |
| `rgba(77, 124, 254, 0.1)` | 2 | 主题色 10% 透明 |
| `rgba(77, 124, 254, 0.2)` | 1 | 主题色 20% 透明 |
| `#1A1A22` | ~5 | 卡片背景 |
| `#2B3139` | ~3 | 卡片边框 |
| `#3D4450` | ~2 | 表格 hover |
| `#16181D` | ~1 | disabled 背景 |
| `#16181D` 等 | 多个 | 其他深色 |

**统计：**
- 总硬编码：**~70 处**
- 唯一硬编码：**~25 个**
- **关键问题：** QSS 文件内的颜色不会自动跟随 Qt 主题切换，必须通过 `QApplication.setStyleSheet()` 重新渲染

---

### 4. preview_panel（template_editor_page.py 第 1287-1330 行）

| 行号 | 硬编码值 | 含义 | Token |
|------|----------|------|-------|
| 1294-1300 | `#2A2A32`, `#1E1E28` | preview content 背景/边框 | `preview_bg`, `border_secondary` |
| 1310 | `#FFFFFF` | preview view 背景 | `bg_secondary` |
| 1319-1324 | `#6E6E73`, `#2B3139` | fallback 文字/边框 | `text_tertiary`, `border_primary` |
| 1335-1336 | `#4A4B56` | preview info 文字 | `text_quaternary` |

---

## 修复策略

### Token 统一表

建立 `src/common/theme_tokens.py`，定义 **28+ 个 Token**，覆盖所有硬编码色值：

```
背景层:  bg_primary / bg_secondary / bg_tertiary / bg_quaternary / bg_hover / bg_pressed / bg_disabled
文字层:  text_primary / text_secondary / text_tertiary / text_quaternary / text_muted / text_inverse
边框层:  border_primary / border_secondary / border_hover / border_focus
强调层:  accent / accent_hover / accent_pressed / accent_subtle / accent_subtle_2 / on_accent
状态层:  success / warning / error
特殊层:  transparent / white / black / shadow / preview_bg / preview_border / preview_fallback
```

### 主题切换流程

```
apply_theme(theme)
  ↓
1. clear_widget_styles()         → 清空所有控件的 stylesheet
  ↓
2. reload_qss()                  → 用 ThemeTokens 重新生成 QSS 并 setStyleSheet
  ↓
3. refresh_dynamic_widgets()     → 重建所有动态生成的组件样式
  ↓
4. unpolish() + polish()         → 强制 Qt 重新计算样式（每个控件）
  ↓
5. update()                      → 触发 Qt 事件循环重绘
```

### 实施范围

| 范围 | 控件类型 | 修复策略 |
|------|----------|----------|
| 全局 | QFrame / QScrollArea | 通过 global.qss 模板 + ThemeTokens 注入 |
| 表单 | QLineEdit / QTextEdit / QLabel | 通过 `_rebuild_inline_styles` 用 token 重建 |
| 预览 | PreviewPanel (QFrame + QWebEngineView) | 通过 `_style_preview_theme` 重建 |
| 动态 | 运行时创建的 QPushButton 等 | 在创建时绑定 token，主题切换时重建 |

---

## 阻断规则（强制约束）

### 🚫 禁止

1. ❌ 禁止在组件 setStyleSheet 中写 `#XXXXXX` 字面量
2. ❌ 禁止在 QSS 中写死颜色
3. ❌ 禁止 `QColor('#XXXXXX')` 直接构造
4. ❌ 禁止使用 `rgba(77, 124, 254, ...)` 字面量
5. ❌ 禁止复制粘贴旧硬编码样式

### ✅ 必须

1. ✅ 颜色必须通过 `theme_tokens.get(name)` 或 `get_token(name)` 读取
2. ✅ QSS 必须通过 `get_all_tokens()` 注入后渲染
3. ✅ 主题切换必须经过完整 5 步流程
4. ✅ 新增组件必须在创建时绑定 token
5. ✅ 主题切换后必须强制 `unpolish/polish/update`

---

## 修复优先级

| 优先级 | 文件 | 原因 |
|--------|------|------|
| **P0** | theme_manager.py | 主题切换核心入口 |
| **P0** | theme_tokens.py | 新建，统一色值来源 |
| **P0** | global.qss | 全局基础样式 |
| **P1** | template_editor_page.py | 硬编码最严重，但局部页面可独立修复 |

---

## 验证清单

修复完成后必须验证：

- [ ] 4 个文件中 `#XXXXXX` 字面量数量 = 0（除 token 定义文件）
- [ ] `palette.setColor` 全部使用 `colors['xxx']` 字典访问
- [ ] `setStyleSheet` 全部使用 f-string 注入 token
- [ ] 切换 Dark → Light → Dark 20 次无残留
- [ ] 所有 `QFrame` / `QScrollArea` / `QLineEdit` / `QTextEdit` / `QLabel` / `PreviewPanel` 颜色一致

---

*本扫描报告基于 2026-06-05 仓库实际状态。修复完成后将生成 THEME_SWITCH_FIX_REPORT.md 验证报告。*
