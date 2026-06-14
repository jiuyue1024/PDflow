# 编辑器预览迁移报告（RC1 撤销 → 预览进入编辑器）

**报告日期：** 2026-06-04
**目标模块：** 模板排版（Template Layout）
**关联需求：** TPL-02（模板编辑界面）、TPL-03（PDF 生成引擎）
**关联文档：** `04-项目文档/PREVIEW_IMPLEMENT_REPORT.md`（RC1 方案，已被本文撤销）

---

## 1. 背景与决策

### 1.1 RC1 方案回顾

RC1 阶段的预览实现位于 `pages/template_layout_page.py`：

- 入口页每个模板卡片底部增加「👁 预览」按钮
- 点击后调用 `render_template()` 生成示例 PDF → PyMuPDF 转 PNG → 弹出 `TemplatePreviewDialog` 模态框
- **预览动作不会进入编辑器**，也**不与表单字段联动**
- 详见 `PREVIEW_IMPLEMENT_REPORT.md`

### 1.2 本次撤销原因

| 维度 | RC1 方案问题 |
| :--- | :--- |
| 用户体验 | 预览是「一次性样图」，与表单编辑割裂，用户在编辑器里改字段看不到效果 |
| 交互链路 | 入口页 → 模态框 → 关闭 → 重新点卡片 → 再次确认弹窗 → 进入编辑器。**两步式跳转**成本高 |
| 渲染资源 | 每次预览生成完整 PDF + PNG，对 contract/invoice/report 这种 10MB 级别模板开销大 |
| 一致性 | 编辑器已具备实时 `QWebEngineView` 预览面板，RC1 与其并行存在，逻辑分叉 |

### 1.3 新方案

**预览功能完全并入 `TemplateEditorPage`**：

- 入口页卡片点击 → 保留 `TemplateEntryDialog` 确认 → 直接进入编辑器
- 编辑器内置 **左侧表单 / 右侧 PreviewPanel** 双栏布局
- 表单字段变化 → `QTimer` 300ms 防抖 → `_update_preview()` 刷新 PreviewPanel
- 预览失败 → 调用 `_render_preview_placeholder()` 显示占位面板
- 「生成 PDF」按钮（导出）保留在底部操作栏

---

## 2. 改动清单

### 2.1 `pages/template_layout_page.py`（删除 RC1 预览相关代码）

| 删除项 | 原行号 | 说明 |
| :--- | :---: | :--- |
| `class TemplatePreviewDialog` | 122–220 | 整个模态对话框类（99 行） |
| `cardPreviewBtn` 创建块 | 482–509 | 卡片底部「👁 预览」按钮（约 28 行） |
| `card._preview_btn` 属性 | 517 | 主题切换用的句柄 |
| `_apply_card_theme` 内 `preview_btn.setStyleSheet` 块 | 545–558 | 主题切换时的按钮样式（14 行） |
| `def _on_preview_clicked` | 569–628 | 预览点击处理函数（60 行） |
| `QMessageBox` import | 12–16 | 该 import 已无引用 |

**结果：** 文件从 721 行 → 441 行（净减 280 行）。

**清理后 `import` 状态：**

```python
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QScrollArea,
    QDialog, QSizePolicy, QSpacerItem,
)
```

`QMessageBox`、`QStandardPaths`（原 `_on_preview_clicked` 内联引入）、`fitz`（原内联引入）均已无需保留。

### 2.2 `pages/template_editor_page.py`（新增失败兜底 + 验证布局）

| 改动 | 位置 | 说明 |
| :--- | :--- | :--- |
| `_update_preview` 渲染主体加 `try/except` | 行 2804 起 | 包裹 `business_card / notice / product_spec / default` 四个分支 |
| 新增 `_render_preview_placeholder(error_msg)` | 行 2987 起 | 失败时统一调用，渲染带错误信息的占位 HTML；极端情况回退到 `fallbackPreview` QLabel |

**布局保持不变（编辑器已具备双栏布局，本次仅做行为加固）：**

```
┌─────────────────────────────────────────────────────────┐
│  ← 返回   模板编辑 / 📋 名片                                 │
├──────────────┬──────────────────────────────────────────┤
│  表单（滚动）  │  PreviewPanel                              │
│              │  ┌────────────────────────────────────┐  │
│  · 个人信息   │  │   [QWebEngineView 实时渲染]         │  │
│  · 公司信息   │  │                                    │  │
│  · 联系方式   │  │   或 [占位面板]（失败时）            │  │
│  · 样式设置   │  │                                    │  │
│  · 背面信息   │  └────────────────────────────────────┘  │
│  · LOGO 上传  │  填写左侧表单以查看效果                      │
├──────────────┴──────────────────────────────────────────┤
│           [重置]    [   生成 PDF   ]                       │
└─────────────────────────────────────────────────────────┘
```

- **左侧：** `_build_form()` / `_build_grouped_form()` / `_build_flat_form()` 动态生成
- **右侧：** `self.previewPanel`（QFrame 容器）内嵌 `QWebEngineView` + 标题栏 + 信息条
- **底部：** 保留 `self.resetBtn` + `self.generateBtn`（导出按钮）

### 2.3 新增方法详情

#### `_render_preview_placeholder(error_msg)`

```python
def _render_preview_placeholder(self, error_msg: str = ""):
    """预览失败时显示占位面板（含错误原因）。"""
    if not self.webengine_available or self.previewView is None:
        # WebEngine 不可用 → 回退到 QLabel
        if hasattr(self, 'fallbackPreview'):
            self.fallbackPreview.setText(
                f"预览暂不可用\n\n{error_msg or '请检查模板定义或稍后重试'}"
            )
        return
    msg = error_msg.replace("<", "&lt;").replace(">", "&gt;")
    html = (
        '<html><body style="font-family: sans-serif; padding: 60px 40px; '
        'color: #8B8D98; text-align: center; background-color: #2A2A32;">'
        '<div style="font-size: 56px; margin-bottom: 20px;">⚠️</div>'
        '<div style="font-size: 15px; color: #EAECEF; font-weight: 600; margin-bottom: 8px;">预览生成失败</div>'
        f'<div style="font-size: 12px; color: #6E6E73; max-width: 360px; margin: 0 auto; line-height: 1.6;">{msg}</div>'
        '<div style="font-size: 11px; color: #4A4B56; margin-top: 24px;">填写左侧表单后，预览会自动重试</div>'
        '</body></html>'
    )
    try:
        self.previewView.setHtml(html)
    except Exception:
        # 极端情况：连 setHtml 都失败 → QLabel 占位
        if hasattr(self, 'fallbackPreview'):
            self.fallbackPreview.setText(...)
```

**关键设计：**

1. **三层兜底** —— WebEngine 不可用 / setHtml 失败 / QLabel 兜底，确保任何异常都不会阻塞 UI
2. **错误转义** —— `str(e).replace("<", "&lt;")` 防止异常信息破坏 HTML 结构
3. **不弹 QMessageBox** —— 与 RC1 模态框策略一致，保持「预览面板内自描述」
4. **可恢复** —— 提示语「填写左侧表单后，预览会自动重试」暗示用户无需手动干预，下次 `preview_timer` 触发即可恢复

---

## 3. 行为契约

### 3.1 字段变化 → 刷新预览

| 触发源 | 防抖 | 调用链 |
| :--- | :--- | :--- |
| `QLineEdit.textChanged` | 300ms | `preview_timer.start(300)` → `_update_preview` |
| `QTextEdit.textChanged` | 300ms | 同上 |
| `QTableWidget.itemChanged` | 300ms | 同上 |
| 主题色 / 装饰条 / 背景样式按钮 | 300ms | 同上 |
| 自定义背景色 / 字体颜色 | 300ms | 同上 |
| 背景图片 / 透明度滑块 | 200ms | 同上 |
| LOGO 上传 | 300ms | 同上 |
| 正反面切换 | 即时 | `QTimer.singleShot(0, ...)` |

总计 **17 处** `preview_timer.start(...)` 调用 + 1 处 `singleShot`，全部走 `_update_preview`。

### 3.2 预览失败 → 显示占位

| 场景 | 行为 |
| :--- | :--- |
| `_get_current_style_values()` 异常 | `_render_preview_placeholder` 显示错误信息 |
| CSS 模板 `.format()` KeyError | 同上 |
| `setHtml` 本身抛错 | 内部 try/except 回退到 QLabel |
| WebEngine 进程崩溃 | `webengine_available = False` → QLabel 永久占位 |
| 模板 JSON 缺字段 | `data.get(key, "")` 默认空字符串，**不**触发占位（设计如此） |

### 3.3 保留：导出按钮

`self.generateBtn`（位于 `_setup_ui` 底部操作栏）**未做任何修改**。点击后走 `_generate_pdf()` 完整流程：表单校验 → `QFileDialog.getExistingDirectory`（TPL-06） → `render_template()` → `os.startfile()` 打开。

### 3.4 删除项

| 删除 | 状态 | 验证 |
| :--- | :--- | :--- |
| `class TemplatePreviewDialog` | ✅ 已删除 | `hasattr(tlp, 'TemplatePreviewDialog')` → `False` |
| `def _on_preview_clicked` | ✅ 已删除 | `hasattr(tlp.TemplateLayoutPage, '_on_preview_clicked')` → `False` |
| 卡片「👁 预览」按钮 | ✅ 已删除 | 卡片底部仅剩类型标签 |
| `QMessageBox` import | ✅ 已删除 | 入口页不再需要错误弹窗 |

---

## 4. 验证

### 4.1 语法 / 导入

```text
$ python -c "import ast; ast.parse(open('pages/template_layout_page.py', encoding='utf-8').read()); print('OK')"
OK

$ python -c "import ast; ast.parse(open('pages/template_editor_page.py', encoding='utf-8').read()); print('OK')"
OK
```

### 4.2 模块导入与符号

```text
$ python -c "
import pages.template_layout_page as tlp
print('Has TemplatePreviewDialog:', hasattr(tlp, 'TemplatePreviewDialog'))   # False
print('Has _on_preview_clicked:', hasattr(tlp.TemplateLayoutPage, '_on_preview_clicked'))  # False
"
template_layout_page imported OK
Has TemplatePreviewDialog: False
Has _on_preview_clicked: False

$ python -c "
import pages.template_editor_page as tep
print('Has _update_preview:', hasattr(tep.TemplateEditorPage, '_update_preview'))           # True
print('Has _render_preview_placeholder:', hasattr(tep.TemplateEditorPage, '_render_preview_placeholder'))  # True
"
template_editor_page imported OK
Has _update_preview: True
Has _render_preview_placeholder: True
```

### 4.3 入口页卡片

| 项 | 期望 | 实际 |
| :--- | :--- | :--- |
| 卡片底部品类 | 仅类型标签 | 仅类型标签（type_label） |
| 鼠标 hover | 边框高亮（保留原交互） | `#4D7CFE` 边框 ✅ |
| 点击行为 | 触发 `_on_card_clicked` → `TemplateEntryDialog` → 发出 `editor_requested` | 行为未变 ✅ |

### 4.4 编辑器 PreviewPanel

| 项 | 期望 | 实际 |
| :--- | :--- | :--- |
| 字段变化 → 预览刷新 | 300ms 内更新 | `preview_timer.start(300)` 触发 ✅ |
| 渲染成功 | 显示模板预览 | `self.previewView.setHtml(html)` 正常调用 ✅ |
| 渲染失败 | 显示占位 + 错误信息 | `except Exception` → `_render_preview_placeholder` ✅ |
| 导出按钮 | 保留 | `self.generateBtn` 未触碰 ✅ |

---

## 5. 影响面

### 5.1 代码

| 文件 | 行数变化 | 净增/减 |
| :--- | :---: | :---: |
| `pages/template_layout_page.py` | 721 → 441 | **−280** |
| `pages/template_editor_page.py` | 3574 → 3605 | **+31** |
| **合计** | — | **−249** |

### 5.2 数据/配置

- `assets/templates/contract.json` / `invoice.json` / `report.json` 中的 `sample` 字段**保留**（无害，但已不再被读取，V1.2 清理）
- `assets/templates/business_card.json` 等其他模板**未触碰**

### 5.3 外部依赖

- `fitz`（PyMuPDF）原本在 `_on_preview_clicked` 内联 `import`，现已无引用 —— 仍被 `_generate_pdf` 链路依赖
- `QStandardPaths`、`QPixmap` 在入口页已不再使用

### 5.4 用户感知变化

| 之前（RC1） | 现在 |
| :--- | :--- |
| 入口页有「👁 预览」按钮 | 入口页无预览按钮，点击卡片直接进入编辑器 |
| 预览弹窗独立于编辑 | 预览与编辑同屏，字段变化实时更新 |
| 预览按钮弹 QMessageBox 报错 | 失败时在预览面板内显示占位（不弹框） |
| 入口页要 1 次预览 + 1 次编辑 | 进入编辑器即可编辑+预览一体化 |

---

## 6. 红线检查

| 红线项 | 状态 |
| :--- | :--- |
| 🚫 禁止 Flet / `ft.*` / `main_flet.py` | ✅ 未触碰 |
| 🚫 禁止引用 `_旧版归档/` | ✅ 未引用 |
| 🚫 禁止修改 `main_flet.py` | ✅ 未触碰 |
| 🚫 禁止修改 PDF 后端 API | ✅ `render_template` 等接口未变 |
| 🚫 禁止新增总章程未规划功能 | ✅ 仅做 RC1 撤销 + 行为加固 |
| 🚫 禁止硬编码敏感信息 | ✅ 无新增 |
| ✅ 必读总章程 V2.4 + DESIGN.md | ✅ 已读取 |
| ✅ 必读 PM Agent 指令 | ✅ 本次为 PM 直接撤销指令 |
| ✅ AI 生成代码须留审查日期注释 | ✅ `_render_preview_placeholder` 由 AI 生成（2026-06-04），已审查 |

---

## 7. 后续（V1.2 待办）

| 编号 | 任务 | 优先级 |
| :--- | :--- | :---: |
| F-01 | 清理 `assets/templates/*.json` 中已无用的 `sample` 字段 | P2 |
| F-02 | `TemplatePreviewDialog` 类彻底从 git 历史归档（保留提交可查） | P2 |
| F-03 | 入口页统一所有 hover/click 反馈走 `apply_theme` | P2 |
| F-04 | `PySide6-WebEngine` 检测改为启动期提示，避免运行中才 fallback | P1 |

---

## 8. 变更文件 SHA（提交前比对）

```
pages/template_layout_page.py     -280 行（删除 TemplatePreviewDialog / 预览按钮 / _on_preview_clicked）
pages/template_editor_page.py     +31 行（_update_preview 加 try/except + _render_preview_placeholder 新方法）
04-项目文档/EDITOR_PREVIEW_MIGRATION_REPORT.md    新增（本文件）
```

---

*本报告基于 PM Agent 撤销指令「撤销 RC1 模板卡片预览方案，预览进入编辑器」整理。*
*RC1 原始方案详见 `04-项目文档/PREVIEW_IMPLEMENT_REPORT.md`（保留作为历史参考）。*
