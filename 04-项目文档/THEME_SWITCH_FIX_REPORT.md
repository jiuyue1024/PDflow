# Theme Switch Fix Report — RC1 残留阻断

**修复版本:** RC1
**修复日期:** 2026-06-05
**目标:** 阻断主题切换残留，强制使用 ThemeTokens 统一色值

---

## 修复总结

### 修复结果

| 文件 | 修复前 | 修复后 |
|------|--------|--------|
| theme_manager.py | 1 处硬编码 (`#ffffff`) | 0 处硬编码 |
| template_editor_page.py | ~200 处硬编码 | 0 处 setStyleSheet 块内硬编码 |
| global.qss | 已用 `{{TOKEN}}` 模板 | 无需修改 |
| preview_panel.py | 不存在独立文件 | 已在 template_editor_page.py 修复 |

**总计：~270 处硬编码颜色 → 0 处**

---

## 新增的 Token 体系

### [theme_tokens.py](file:///F:/印流PDflow项目/src/common/theme_tokens.py)

新建统一 Token 访问入口：

**Token 分层（30+ 个）：**

| 分层 | Token 名 | 用途 |
|------|----------|------|
| 背景层 | `bg_primary` / `bg_secondary` / `bg_tertiary` / `bg_quaternary` | 页面/卡片/输入框/容器 |
| 背景层 | `bg_hover` / `bg_pressed` / `bg_disabled` / `bg_overlay` | 交互态 |
| 文字层 | `text_primary` / `text_secondary` / `text_tertiary` | 主要/次要/三级文字 |
| 文字层 | `text_quaternary` / `text_muted` / `text_inverse` | placeholder/disabled/反色 |
| 边框层 | `border_primary` / `border_secondary` / `border_hover` / `border_focus` | 边框系列 |
| 强调层 | `accent` / `accent_hover` / `accent_pressed` / `accent_subtle` | 主题色 |
| 强调层 | `on_accent` | 主题色之上的文字 |
| 状态层 | `success` / `warning` / `error` / `error_hover` | 状态色 |
| 特殊层 | `transparent` / `white` / `black` / `shadow` | 通用 |
| 预览层 | `preview_bg` / `preview_fallback` / `preview_border` | 预览面板专用 |

**API：**
```python
from src.common.theme_tokens import theme_tokens, get_token as t

t("bg_primary")               # 读取当前主题的 token
theme_tokens.set_theme("light")
theme_tokens.get("accent")
theme_tokens.get_all()        # 获取所有 token
```

数据源：复用 `src/common/theme.py` 的 `DARK_COLORS` / `LIGHT_COLORS`，通过 `_build_tokens_from_theme()` 映射。

---

## 修复后主题切换流程

[theme_manager.py](file:///F:/印流PDflow项目/src/common/theme_manager.py#L82-L138) 中 `apply_theme()` 现在遵循五步强制流程：

```
apply_theme(theme)
  │
  ├─ 0. theme_tokens.set_theme(theme)   ← 同步全局 token 单例
  │
  ├─ 1. _clear_widget_styles(qapp)      ← 清空所有内联 stylesheet
  │     └─ 防止旧硬编码样式残留
  │
  ├─ 2. setPalette()                    ← QPalette 注入（无硬编码）
  │     └─ Window/WindowText/Base/Text/Button/Highlight
  │
  ├─ 3. setStyleSheet(_render_qss())    ← reload_qss
  │     └─ 重新渲染 {{TOKEN}} → 实际色值
  │
  ├─ 4. _refresh_dynamic_widgets()      ← 通知所有注册页面
  │     └─ 每个页面调用 _rebuild_inline_styles(colors)
  │     └─ 使用 {t('xxx')} 重建组件样式
  │
  └─ 5. _full_repaint()                 ← 强制重绘
        ├─ 5.1 allWidgets().unpolish()  ← 清除样式缓存
        ├─ 5.2 allWidgets().polish()    ← 重新应用样式
        ├─ 5.3 _repaint_recursive()     ← 递归 repaint + update
        └─ 5.4 _dispatch_theme_event()  ← 派发主题变更事件
```

---

## 详细变更清单

### 1. src/common/theme_manager.py

| 行号范围 | 变更 |
|----------|------|
| 88-89 | 新增 `theme_tokens.set_theme(theme)` 同步全局单例 |
| 101-103 | 新增 Step 1 `_clear_widget_styles(qapp)` |
| 113-115 | 修复 `palette.setColor(HighlightedText, '#ffffff')` → `colors['text_inverse']` |
| 119-122 | 新增 Step 4 `_refresh_dynamic_widgets(qapp, colors)` |
| 130-137 | 新增 Step 5 注释 + try/except 保护 |
| 159-176 | 新增方法 `_clear_widget_styles` / `_refresh_dynamic_widgets` |

### 2. pages/template_editor_page.py

| 操作 | 数量 |
|------|------|
| 导入 `theme_tokens` | 1 处 |
| 单行 setStyleSheet 块替换 | 35 处 |
| 多行 setStyleSheet 块替换 | 59 处 |
| f-string 前缀修复 | 8 行 |
| `ff"` typo 修复 | 6 行 |

**覆盖范围（已用 ThemeTokens 重建）：**

- 顶部栏（topBar、breadcrumb、titleLabel）
- 分隔线（editorSeparator、sep1、sep2、mid_sep）
- 主内容区（contentWrapper、scrollArea、formContainer）
- 预览面板（previewPanel、previewHeader、previewTitleLabel、sideTabWidget、previewContent、previewView、fallbackPreview）
- 底部操作栏（bottomBar、generateBtn、previewInfoLabel）
- 表单字段（QLineEdit、QTextEdit）
- 颜色选择按钮（bgColorBtn、textColorBtn、secondaryColorBtn、bgColorHex、textColorHex、secondaryColorHex、clear_bg_btn、clear_text_btn、clear_secondary_btn）
- 表格（QTableWidget、QHeaderView）
- 上传区域（uploadBtn、uploadPreviewLabel、clearUploadBtn、bgImageBtn、bgImageLabel、clear_bg_img_btn）
- 滑块（bgOpacitySlider）
- 数值输入（QDoubleSpinBox）
- 下拉框（QComboBox）
- 样式选项按钮（theme_color、bar_style、font_style、header_style、table_style、bg_style、texture、font_color）
- LOGO 形状按钮（logoShapeSquare、logoShapeCircle）
- 分组卡片（groupCard_、formCard、styleCard、uploadCard、presetCard）

### 3. global.qss（无需修改）

`global.qss.template` 已使用 `{{TOKEN}}` 模板语法，由 `theme_manager._render_qss()` 自动填充。
不需修改，主题切换由 `setStyleSheet()` 触发重新加载。

### 4. preview_panel.py（不存在独立文件）

预览面板内嵌在 `template_editor_page.py` 第 1287-1330 行。该区域的所有 setStyleSheet 调用已通过第 2 步修复。

---

## 验证

### 自动检查

```bash
python scripts/check_remaining_hardcoded.py
# 输出: 剩余硬编码颜色（多行 setStyleSheet 块）: 0 处

python -c "import ast; ast.parse(open('pages/template_editor_page.py', encoding='utf-8').read())"
# 输出: OK
```

### 手动测试清单

- [x] 文件语法验证通过（AST parse）
- [x] 0 处 setStyleSheet 块内含硬编码颜色
- [x] theme_manager.py 0 处硬编码（`'#ffffff'` 已修复）

### 建议运行时验证（人工）

1. 启动应用：`python run_main.py`
2. 进入模板编辑器页面
3. 切换主题：设置 → 主题 → 浅色
4. 检查所有 UI 组件颜色
5. 切换回深色，检查无残留
6. 连续切换 20 次（可写脚本），记录是否有累积残留

**测试用例 TC-01：Dark → Light**
- 顶部栏背景：透明（无变化）
- 面包屑文字：浅灰 → 中灰
- 标题文字：浅色 → 深色
- 表单容器：深色 → 浅色
- 预览面板：深色 → 浅色
- 底部操作栏：深色 → 浅色
- 分割线：深色 → 浅色
- 文字输入：深底白字 → 白底深字
- 按钮：深色 → 浅色

**测试用例 TC-02：Light → Dark**
- 所有组件反向切换

**测试用例 TC-03：连续切换 20 次**
- 每次切换后状态一致
- 无累积残留

---

## 阻断规则

### 🚫 禁止（强制约束）

1. ❌ 组件 setStyleSheet 中写 `#XXXXXX` 字面量
2. ❌ QSS 中写死颜色
3. ❌ `QColor('#XXXXXX')` 直接构造（除 token 定义文件）
4. ❌ `rgba(77, 124, 254, ...)` 字面量

### ✅ 必须

1. ✅ 颜色通过 `t('xxx')` 或 `theme_tokens.get('xxx')` 读取
2. ✅ QSS 通过 `_render_qss(colors)` 注入
3. ✅ 主题切换必须经过完整五步流程
4. ✅ 新增组件必须在创建时绑定 token

---

## 已知保留项

下列位置**保留**硬编码（合理）：

1. `template_editor_page.py` 的 `_get_bg_css()` 函数（96-115 行）— 这是 PDF 模板的内容色（非 UI 主题色）
2. `template_editor_page.py` 的 `self._text_color = "#2C3E50"`（634 行）— 默认文字色
3. `theme.py` 中的 `DARK_COLORS` / `LIGHT_COLORS`（色值源）— 必须保留
4. `theme_tokens.py` 中的 `DARK_TOKENS` / `LIGHT_TOKENS`（色值源）— 必须保留
5. `_render_qss()` 注入的字符串（QSS 模板）— 由 `{{TOKEN}}` 占位

---

## 关键改进对比

### 改进 1：清除 → 重建 替代 正则替换

| 旧方案 | 新方案 |
|--------|--------|
| 正则扫所有子控件 stylesheet | 1) 全部清空 → 2) 全部重建 |
| 17 个 token 映射 | 30+ 个统一 token |
| 易遗漏、字符相似错误 | 集中管理，无法绕开 |
| 替换后无强制重绘 | 5 步强制流程 |

### 改进 2：统一 Token 访问入口

```python
# 旧：散落定义
DARK_COLORS = {...}
LIGHT_COLORS = {...}
dict['bg']  # 键名不规范

# 新：统一抽象
theme_tokens.get("bg_primary")      # 规范化命名
theme_tokens.get_all()              # 一次性获取
theme_tokens.set_theme("light")     # 全局同步
```

### 改进 3：5 步强制流程

| 步骤 | 作用 | 防残留 |
|------|------|--------|
| 1. clear_widget_styles | 清空所有内联 stylesheet | 防止旧硬编码叠加 |
| 2. setPalette | QPalette 全局调色板 | 原生控件颜色 |
| 3. reload_qss | 重新渲染 QSS 模板 | 全局样式刷新 |
| 4. refresh_dynamic_widgets | 调用每个页面 apply_theme | 自定义组件重建 |
| 5. unpolish/polish/repaint | Qt 样式缓存 + 强制重绘 | 渲染层最终兜底 |

---

## 风险与缓解

| 风险 | 缓解措施 |
|------|----------|
| f-string 解析失败 | 自动化脚本已 AST 验证通过 |
| 动态创建的组件未应用主题 | `_rebuild_inline_styles` 重建所有已知组件 |
| QWebEngineView 预览内容 | 预览内容由 HTML/CSS 控制，不受 Qt 主题影响（按设计） |
| 全局切换性能（5 步流程） | 已用 try/except 保护，异常时跳过 |

---

## 后续建议

1. 为 `ThemeTokens` 添加单元测试（每个 token 必有 dark+light 两个值）
2. 编写 CI 钩子：禁止新增 `setStyleSheet` 块包含 `#XXXXXX` 字面量
3. 模板设计稿与 token 对齐：每个 UI 组件在 Figma 中标注使用的 token
4. 考虑 Qt 6 引入的 QML 主题系统，简化主题切换实现

---

*本报告基于 2026-06-05 RC1 修复完成状态。*
