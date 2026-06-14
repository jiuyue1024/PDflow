# Theme Switch Fix Report - RC1

**修复目标:** 主题切换完全重绘，消除浅色模式残留深色颜色  
**日期:** 2026-06-05  
**版本:** RC1  

---

## 问题分析

### 根因

切换浅色模式后，模板编辑器页面残留深色颜色的原因：

1. **theme_manager.py** 只刷新了 `topLevelWidgets()`，没有递归处理嵌套子控件（表单容器、预览面板内的深层控件）
2. **template_editor_page.py** 的 `apply_theme` 使用正则替换硬编码颜色，但 token 映射不完整（只有17个），且替换后没有强制重绘
3. Qt 的 stylesheet 缓存机制：设置新 stylesheet 不会自动触发已渲染控件的重绘

### 受影响的组件

| 组件 | 硬编码深色颜色 | 残留表现 |
|------|--------------|----------|
| 表单容器 | `#0A0A0F` | 浅色模式下背景仍为黑色 |
| 卡片 | `#14141A` | 卡片背景不跟随主题 |
| 分隔线 | `#1E1E28` | 分割线在浅色下不可见 |
| 预览面板 | `#1A1A22` | 预览面板深色残留 |
| 底部操作栏 | `#0F0F14` | 操作栏背景不变化 |
| 文字颜色 | `#ECEDF0` | 浅色模式下文字仍为白色（在浅背景上看不清） |

---

## 修复方案

### 修复流程（apply_theme 四步法）

```
apply_theme()
  ↓
1. reload_qss()      → 清除所有内联 stylesheet 缓存
  ↓
2. clear_cache()     → 清空 self._current_theme_colors 防残留
  ↓
3. rebuild_inline_styles(colors)  → 使用 theme token 重建所有内联样式
  ↓
4. repaint_all() + update()       → 递归重绘所有子控件
```

### 修改文件

| 文件 | 变更 |
|------|------|
| `src/common/theme_manager.py` | 增强 `apply_theme` 重绘流程 |
| `pages/template_editor_page.py` | 重写 `apply_theme` 方法 |

---

## 详细变更

### 1. theme_manager.py

**修改前：**
```python
for widget in qapp.topLevelWidgets():
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    widget.update()
```

**修改后：**
```python
self._full_repaint(qapp, colors)
```

新增方法：
- `_full_repaint()` — 完整重绘流程入口
- `_repaint_recursive()` — 递归遍历顶层控件
- `_repaint_widget_recursive()` — 递归重绘单个控件及其所有子控件
- `_dispatch_theme_event()` — 派发主题变更事件到控件树

**重绘流程：**
1. `allWidgets().unpolish()` — 清除所有控件的样式缓存
2. `allWidgets().polish()` — 重新应用全局样式表
3. `_repaint_recursive()` — 逐控件 `unpolish → polish → repaint → update`
4. `_dispatch_theme_event()` — 派发自定义主题变更事件

### 2. template_editor_page.py

**修改前：**
```python
def apply_theme(self, colors: dict):
    # 正则替换 17 个硬编码 token
    token_map = {
        '#0A0A0F': colors.get('input_bg', '#F5F5F7'),
        '#0B0E11': colors.get('bg', '#FAFAFA'),
        ...
    }
```

**修改后：**
```python
def apply_theme(self, colors: dict):
    self._reload_qss()           # 清除所有内联 stylesheet
    self._clear_theme_cache()    # 清空旧主题色缓存
    self._rebuild_inline_styles(colors)  # 使用 token 重建
    self._repaint_all()          # 递归重绘
    self.update()                # 触发 Qt 事件循环
```

新增方法：
- `_reload_qss()` — 清空所有控件的 stylesheet
- `_clear_theme_cache()` — 清空 `_current_theme_colors`
- `_repaint_all()` — 递归 unpolish → polish → repaint → update
- `_rebuild_inline_styles(colors)` — 使用 theme token 重建所有内联样式
- `_style_radio_btn_theme(btn, checked, colors)` — 使用 token 重建选项按钮
- `_style_logo_shape_btn_theme(active, colors)` — 使用 token 重建 LOGO 形状按钮

覆盖的 UI 组件：
- 顶部栏（topBar、breadcrumb、titleLabel）
- 分隔线（editorSeparator）
- 表单容器（formContainer、scrollArea）
- 预览面板（previewPanel、previewHeader、previewTitleLabel、sideTabWidget、previewContent）
- 底部操作栏（bottomBar、generateBtn）
- 字段控件（QLineEdit、QTextEdit）
- 分组卡片（groupCard_、formCard、styleCard、uploadCard）
- 样式选项按钮（主题色、装饰条、背景、纹理、字体风格）
- 颜色选择器（bgColorBtn、textColorBtn、secondaryColorBtn）
- LOGO 形状按钮（logoShapeSquare、logoShapeCircle）
- 表格（QTableWidget）
- 上传区域（uploadBtn、uploadPreviewLabel）
- 输入控件（QComboBox、QDoubleSpinBox、QSlider）

### 3. 实例属性化

将 `_setup_ui` 中的局部变量改为实例属性，使 `apply_theme` 可以访问：

| 原变量 | 新属性 |
|--------|--------|
| `top_bar` | `self.topBar` |
| `sep` | `self.editorSeparator` |
| `preview_header` | `self.previewHeader` |

---

## 验证方案

### 测试用例

| 测试 | 操作 | 预期结果 |
|------|------|----------|
| TC-01 | Dark → Light | 所有组件切换为浅色，无深色残留 |
| TC-02 | Light → Dark | 所有组件切换回深色，无浅色残留 |
| TC-03 | Dark → Light → Dark（连续10次） | 每次切换后颜色正确，无累积残留 |
| TC-04 | 打开模板编辑器，切换主题 | 编辑器内所有组件跟随主题 |
| TC-05 | 填写表单后切换主题 | 输入框、标签、按钮颜色正确切换 |
| TC-06 | 预览面板切换主题 | 预览面板容器颜色跟随主题 |

### 人工检查清单

- [ ] 页面背景颜色正确
- [ ] 表单输入框背景颜色正确
- [ ] 卡片容器背景颜色正确
- [ ] 分隔线颜色正确
- [ ] 主要文字颜色正确
- [ ] 次要文字颜色正确
- [ ] 按钮背景/文字颜色正确
- [ ] 预览面板容器颜色正确
- [ ] 底部操作栏颜色正确
- [ ] 样式选项按钮颜色正确
- [ ] 表格样式正确
- [ ] 无硬编码颜色残留

---

## 关键改进

### 改进 1：递归重绘所有子控件

旧方案只处理顶层控件，新方案递归处理控件树中的所有节点：

```python
def _repaint_widget_recursive(self, widget):
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    widget.repaint()
    widget.update()
    for child in widget.children():
        if hasattr(child, 'style'):
            self._repaint_widget_recursive(child)
```

### 改进 2：从 token 映射改为 token 重建

旧方案用正则替换硬编码颜色，容易遗漏；新方案直接销毁旧样式并用主题 token 重建：

```python
# 旧：正则替换
token_map = {'#0A0A0F': colors.get('input_bg')}
widget.setStyleSheet(pattern.sub(value, cur))

# 新：完全重建
widget.setStyleSheet(f"""
    QLineEdit {{
        background-color: {input_bg};
        color: {text_main};
        border: 1px solid {border};
    }}
""")
```

### 改进 3：样式缓存清除

在重建样式前，先清空所有控件的 stylesheet，确保没有旧样式残留：

```python
def _reload_qss(self):
    for widget in [self] + self.findChildren(QWidget):
        if widget.styleSheet():
            widget.setStyleSheet("")
```

---

## 已知限制

1. **WebEngineView 预览**：预览面板使用 QWebEngineView 渲染 HTML，其内部样式由 CSS 模板控制，不受 Qt 主题切换影响（预览内容颜色由模板 CSS 独立控制）
2. **动态创建的控件**：`_build_form` 动态创建的表单控件在首次构建时使用硬编码样式，需在主题切换后通过 `_rebuild_inline_styles` 重建

---

## 后续建议

1. 将 `_setup_ui` 中所有硬编码颜色替换为从主题 token 读取
2. 新增控件时自动绑定主题监听
3. 考虑引入 CSS 变量机制，避免手动重建样式
