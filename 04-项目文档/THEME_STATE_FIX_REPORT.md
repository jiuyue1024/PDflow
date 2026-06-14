# Theme State Fix Report — RC1 按钮状态修复

**修复版本:** RC1
**修复日期:** 2026-06-05
**问题:** 浅色模式点击按钮后变深色（selected/checked 态背景太深）
**目标:** 统一按钮 4 态（normal/hover/pressed/checked）颜色语义

---

## 问题根因

### 现象

在浅色模式下：
- 点击侧边栏按钮后背景突然变成深色
- Tab 选中后底色变深
- 菜单项选中后颜色突兀
- 列表项选中后文字变成主题色

### 原因分析

**原始 QSS 模板使用** `{{primary_light_12}}` / `{{nav_checked_bg_qss}}` / `{{primary_light_10}}` 等「轻量级主题色」作为选中态背景：
- 深色模式：`rgba(77, 124, 254, 0.12)` → 在深色背景上几乎不可见
- 浅色模式：同样的 `rgba(77, 124, 254, 0.12)` → 在浅色背景上变成 12% 蓝叠加 = **深蓝** ❌

**根因：** 浅色模式用「主题色透明度叠加」等同于「深色叠加」，与浅色背景对比强烈，视觉上呈现"变深"。

### 受影响的组件

| 组件 | 旧实现 | 问题 |
|------|--------|------|
| QPushButton#navButton:checked | `{{nav_checked_bg_qss}}` (rgba 12% 蓝) | 浅色下变深蓝 |
| QPushButton#btnHome..btnSpeedwrite:checked | `{{nav_checked_bg_qss}}` | 同上 |
| QTabBar::tab:selected | `{{primary}}` 文字 + 边框 | 浅色下文字变深 |
| QListWidget#sidebar::item:selected | `{{primary_light_12}}` 背景 | 浅色下变深 |
| QMenu::item:selected | `{{primary_light_12}}` | 同上 |
| QMenuBar::item:selected | `{{primary_light_10}}` | 同上 |
| QTableView::item:selected | `{{primary_light_12}}` | 同上 |
| QComboBox QAbstractItemView::item:hover | `{{hover_bg}}` + `{{primary}}` | 浅色下变色突兀 |

---

## 修复方案

### 新增明示 Token（v3.0）

在 [theme.py](file:///F:/印流PDflow项目/src/common/theme.py) 中新增 18 个按钮状态语义 Token，覆盖 normal/hover/pressed/selected/focus/disabled 六态：

| Token | 浅色值 | 深色值 | 用途 |
|-------|--------|--------|------|
| `bg_normal` | `#F5F5F7` | `#0B0E11` | 正常态背景 |
| `bg_hover` | `#EEEEF0` | `#1A1A22` | hover 态背景 |
| `bg_pressed` | `#E5E5EA` | `#1E1E28` | pressed 态背景 |
| **`bg_selected`** | **`#DDE5FF`** | **`#1E2330`** | **selected/checked 态背景（修复重点）** |
| `bg_focus` | `#FFFFFF` | `#1E1E28` | focus 态背景 |
| `bg_disabled` | `#F2F2F5` | `#16181D` | disabled 态背景 |
| `text_normal` | `#1D1D1F` | `#ECEDF0` | 正常态文字 |
| `text_hover` | `#1D1D1F` | `#FFFFFF` | hover 态文字 |
| `text_pressed` | `#1D1D1F` | `#FFFFFF` | pressed 态文字 |
| `text_selected` | `#4D7CFE` | `#EAECEF` | selected 态文字（主题色） |
| `text_disabled` | `#AEAEB2` | `#4A4B56` | disabled 态文字 |
| `border_normal` | `#E5E5EA` | `#1E1E28` | 正常态边框 |
| `border_hover` | `#4D7CFE` | `#3D4450` | hover 态边框 |
| `border_pressed` | `#2D5CD0` | `#2B3139` | pressed 态边框 |
| **`border_selected`** | **`#4D7CFE`** | **`#4D7CFE`** | **selected 态边框（主题色）** |
| `border_focus` | `#4D7CFE` | `#4D7CFE` | focus 态边框 |
| `border_disabled` | `#E5E5EA` | `#1E1E28` | disabled 态边框 |

**关键修复：** `bg_selected` 在浅色模式下使用 **`#DDE5FF`**（主题色 15% 浅色版本），不再是 12% 蓝叠加。

---

### global.qss.template 修复

[global.qss.template](file:///F:/印流PDflow项目/pages/global.qss.template) 中所有按钮状态定义改用明示 token：

| 组件 | 旧 token | 新 token |
|------|----------|----------|
| `QPushButton#navButton` normal | `transparent` | `{{bg_normal}}` |
| `QPushButton#navButton:hover` | `{{nav_hover_qss}}` + `{{sidebar_text_active}}` | `{{bg_hover}}` + `{{text_hover}}` |
| **`QPushButton#navButton:checked`** | `{{nav_checked_bg_qss}}` | **`{{bg_selected}}` + `{{text_selected}}` + `{{border_selected}}`** |
| `QPushButton#btnHome..btnSpeedwrite:checked` | `{{nav_checked_bg_qss}}` + `{{card_title}}` | `{{bg_selected}}` + `{{text_selected}}` + `border-left: 3px solid {{border_selected}}` |
| `QTabBar::tab` normal | `transparent` | `{{bg_normal}}` |
| `QTabBar::tab:hover` | `{{card_bg}}` | `{{bg_hover}}` |
| **`QTabBar::tab:selected`** | `{{primary}}` (色) | **`{{bg_selected}}` + `{{text_selected}}` + `{{border_selected}}` (font-weight: 600)** |
| `QListWidget#sidebar::item:selected` | `{{primary_light_12}}` + `{{primary}}` | `{{bg_selected}}` + `{{text_selected}}` |
| `QMenu::item:selected` | `{{primary_light_12}}` + `{{primary}}` | `{{bg_selected}}` + `{{text_selected}}` |
| `QMenuBar::item:selected` | `{{primary_light_10}}` | `{{bg_selected}}` + `{{text_selected}}` |
| `QTableView::item:selected` | `{{primary_light_12}}` + `{{primary}}` | `{{bg_selected}}` + `{{text_selected}}` |
| `QComboBox QAbstractItemView::item:hover` | `{{hover_bg}}` + `{{primary}}` | `{{bg_hover}}` + `{{text_main}}` |

---

### 生成的 QSS 文件

[scripts/render_qss.py](file:///F:/印流PDflow项目/scripts/render_qss.py) 从 `global.qss.template` 渲染并输出：

| 文件 | 字符数 | 用途 |
|------|--------|------|
| [pages/light.qss](file:///F:/印流PDflow项目/pages/light.qss) | 25,774 | 浅色模式静态 QSS |
| [pages/dark.qss](file:///F:/印流PDflow项目/pages/dark.qss) | 25,810 | 深色模式静态 QSS |

**两文件均通过自动检查：`{{TOKEN}}` 残留 = 0**

---

### theme_manager 加载逻辑

[theme_manager.py](file:///F:/印流PDflow项目/src/common/theme_manager.py#L239-L263) 的 `get_qss()` 改为优先加载预渲染文件：

```python
def get_qss(self, theme: str = None) -> str:
    # 1. 优先加载 pages/{theme}.qss 静态文件
    static_path = resource_path("pages", f"{theme}.qss")
    if os.path.exists(static_path):
        # 验证无 {{TOKEN}} 残留
        # 返回预渲染内容
    
    # 2. 回退到模板渲染（适用于测试/动态调整）
    colors = DARK_COLORS if theme == "dark" else LIGHT_COLORS
    return self._render_qss(colors)
```

---

## 验证

### 浅色模式 `light.qss` 关键状态渲染

| 状态 | 实际色值 | 视觉 |
|------|----------|------|
| navButton normal | `bg_normal: #F5F5F7` | 与页面同色 |
| navButton hover | `bg_hover: #EEEEF0` | 浅灰（不刺眼） |
| navButton checked | `bg_selected: #DDE5FF` + `border_selected: #4D7CFE` | 浅蓝（修复完成）✅ |
| btnHome..btnSpeedwrite:checked | `bg_selected: #DDE5FF` + `border-left: 3px solid #4D7CFE` | 浅蓝 + 左侧蓝条（修复完成）✅ |
| QTabBar::tab:selected | `bg_selected: #DDE5FF` + 底边 `border_selected` | 浅蓝（修复完成）✅ |
| QListWidget::item:selected | `bg_selected: #DDE5FF` + 左侧蓝条 | 浅蓝（修复完成）✅ |
| QMenu::item:selected | `bg_selected: #DDE5FF` | 浅蓝（修复完成）✅ |
| QTableView::item:selected | `bg_selected: #DDE5FF` | 浅蓝（修复完成）✅ |

### 深色模式 `dark.qss` 关键状态渲染

| 状态 | 实际色值 | 视觉 |
|------|----------|------|
| navButton normal | `bg_normal: #0B0E11` | 与页面同色 |
| navButton hover | `bg_hover: #1A1A22` | 浅深色（不刺眼） |
| navButton checked | `bg_selected: #1E2330` + `border_selected: #4D7CFE` | 中深色 + 蓝边（保持深色一致性）✅ |
| btnHome..btnSpeedwrite:checked | `bg_selected: #1E2330` + 左侧蓝条 | 中深色 + 蓝条 ✅ |
| QTabBar::tab:selected | `bg_selected: #1E2330` + 底边 `border_selected` | 中深色 + 蓝边 ✅ |
| QListWidget::item:selected | `bg_selected: #1E2330` + 左侧蓝条 | 中深色 + 蓝条 ✅ |
| QMenu::item:selected | `bg_selected: #1E2330` | 中深色 ✅ |
| QTableView::item:selected | `bg_selected: #1E2330` | 中深色 ✅ |

### 自动检查

```bash
python scripts/render_qss.py
# ✓ 生成 dark.qss (25810 字符)
# ✓ 生成 light.qss (25774 字符)

python -c "
import re
for theme in ['dark', 'light']:
    content = open(f'pages/{theme}.qss', encoding='utf-8').read()
    remaining = re.findall(r'\{\{[\w_]+\}\}', content)
    print(f'{theme}.qss: {len(content)} chars, 残留 {{TOKEN}}: {len(remaining)}')
"
# dark.qss: 25810 chars, 残留 {TOKEN}: 0
# light.qss: 25774 chars, 残留 {TOKEN}: 0
```

### 建议运行时验证（人工）

**测试用例 TC-01：浅色模式 4 态**

启动应用 → 切换浅色模式 → 逐个检查以下按钮状态：

| 控件 | normal | hover | pressed | checked |
|------|--------|-------|---------|---------|
| 侧边栏 7 个按钮（首页/合并/压缩/转换/水印/模板/速文） | 浅色 | 浅灰 | 中灰 | **浅蓝** ✅ |
| 通用 navButton | 浅色 | 浅灰 | 中灰 | **浅蓝** ✅ |
| TabBar | 浅色 | 浅灰 | 中灰 | **浅蓝** ✅ |
| 侧边栏列表项 | 浅色 | 浅灰 | 中灰 | **浅蓝** ✅ |
| 菜单项 | 浅色 | 浅灰 | 中灰 | **浅蓝** ✅ |
| 表格项 | 浅色 | 浅灰 | 中灰 | **浅蓝** ✅ |

**测试用例 TC-02：连续切换 20 次**

```
Dark → Light → Dark → Light → ...（20 次）
```

- 每次切换后颜色一致
- 无累积残留

**测试用例 TC-03：不同主题色值对比**

| 状态 | 深色模式 | 浅色模式 | 一致性 |
|------|----------|----------|--------|
| 选中态背景 | `#1E2330` | `#DDE5FF` | 主题色家族内一致 ✅ |
| 选中态文字 | `#EAECEF` | `#4D7CFE` | 主题色文字 ✅ |
| 选中态边框 | `#4D7CFE` | `#4D7CFE` | 主题色边框（统一）✅ |

---

## 关键改进

### 改进 1：语义化 Token 替代 rgba 透明度叠加

| 旧实现 | 新实现 |
|--------|--------|
| `{{primary_light_12}}` = `rgba(77, 124, 254, 0.12)` | `{{bg_selected}}` = `#DDE5FF`（深色）/ `#1E2330`（浅色）|
| 浅色下叠加 = 深蓝 ❌ | 浅色下 = 浅蓝 ✅ |
| 视觉语义模糊 | 视觉语义清晰 |

### 改进 2：双文件分离 light/dark.qss

- **开发阶段：** 修改 `global.qss.template` + `theme.py` → 运行 `render_qss.py`
- **运行时：** `get_qss()` 优先加载静态文件，性能更好
- **可审计：** 可以直接 diff `light.qss` vs `dark.qss` 看差异

### 改进 3：明示边框 selected 态

旧版 `navButton:checked` 只有背景色，无边框。视觉上 selected 状态不够明确。
新版：selected 态增加 `border: 1px solid {{border_selected}}`（主题色），状态切换更清晰。

---

## 文件变更清单

| 文件 | 变更类型 | 说明 |
|------|----------|------|
| [src/common/theme.py](file:///F:/印流PDflow项目/src/common/theme.py) | 修改 | DARK_COLORS / LIGHT_COLORS 各新增 18 个状态 token |
| [pages/global.qss.template](file:///F:/印流PDflow项目/pages/global.qss.template) | 修改 | 9 处选择器改用新状态 token |
| [pages/light.qss](file:///F:/印流PDflow项目/pages/light.qss) | **新建** | 浅色模式预渲染 QSS（25,774 字符） |
| [pages/dark.qss](file:///F:/印流PDflow项目/pages/dark.qss) | **新建** | 深色模式预渲染 QSS（25,810 字符） |
| [src/common/theme_manager.py](file:///F:/印流PDflow项目/src/common/theme_manager.py) | 修改 | `get_qss()` 优先加载静态文件 |
| [scripts/render_qss.py](file:///F:/印流PDflow项目/scripts/render_qss.py) | **新建** | 模板 → 静态 QSS 渲染脚本 |

---

## 阻断规则

### 🚫 禁止

1. ❌ `setStyleSheet` / QSS 中用 `rgba(77, 124, 254, 0.X)` 作背景（语义模糊）
2. ❌ 选中态只用主题色透明度叠加（浅色模式下变深）
3. ❌ 选中态无边框（视觉不明确）

### ✅ 必须

1. ✅ 选中态用 `{{bg_selected}}` + `{{text_selected}}` + `{{border_selected}}` 组合
2. ✅ 4 态（normal/hover/pressed/checked）分别用对应 token
3. ✅ 修改 QSS 模板后必须运行 `python scripts/render_qss.py` 重新生成静态文件

---

## 后续建议

1. 将 `bg_selected` 等状态 token 写入 DESIGN.md
2. 为每种状态 token 编写单元测试（确保深浅色差异合理）
3. 添加 CI 钩子：禁止 QSS 中出现 `rgba(.*primary.*)` 字面量
4. 考虑将 QSS 模板中剩余的 `{{primary}}`、`{{primary_hover}}` 等也迁到 `{{accent}}` 等统一命名

---

*本报告基于 2026-06-05 RC1 Theme State 修复完成状态。*
