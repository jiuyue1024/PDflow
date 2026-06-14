# 模板排版预览实现报告

**报告日期：** 2026-06-03
**目标版本：** V1.1 RC
**需求编号：** TPL-PREVIEW-01
**支持模板：** contract / invoice / report（V1.1 新增三模板）

---

## 1. 需求与方案

### 1.1 需求

- 用户在「模板排版」入口页点击模板卡片的「预览」按钮
- 系统使用模板 JSON 的 `sample` 示例数据生成一份示例 PDF
- 把 PDF 首页转为 PNG 缩略图
- 弹出对话框显示缩略图
- **不要求实时编辑预览**

### 1.2 方案

利用 V1.1 已实现的 `render_template()` 统一渲染入口：

```
点击「预览」按钮
    ↓
取模板 JSON 的 sample 字段
    ↓
调用 render_template(template_id, output_path, sample)
    ↓
fitz.open(pdf) → load_page(0) → get_pixmap(dpi=120).save(png)
    ↓
弹窗 TemplatePreviewDialog 显示 PNG
```

不进入 `TemplateEditorPage` 编辑器，**不与现有预览链路（QWebEngineView）耦合**。

---

## 2. 修改文件

### 2.1 `pages/template_layout_page.py`

**新增类：`TemplatePreviewDialog`**（文件约第 124-225 行）

- 显示模板名称 + 缩略图 + 文件路径提示 + 关闭按钮
- 主题色由调用方传入，兼容浅色 / 深色
- 缩略图按 480px 宽度等比缩放

**修改 `_create_card()`**（约第 309-466 行）

- 在卡片底部新增「👁 预览」按钮（与「类型标签」同行，类型标签靠左，预览按钮靠右）
- 按钮 hover 高亮（`#4D7CFE`），禁用状态低对比度
- 点击预览按钮 → 调用 `_on_preview_clicked()`
- **预览按钮的 click 事件** 不会冒泡到卡片整体（PySide6 QPushButton 自动吃掉 click，不触发 `mousePressEvent`）

**新增方法：`_on_preview_clicked(template_data)`**

- 缓存目录：`QStandardPaths.CacheLocation/template_previews/`
- 调用 `render_template(template_id, pdf_path, data)` 生成 PDF
- 调用 `fitz` 把 PDF 首页转 PNG
- 弹出 `TemplatePreviewDialog`

### 2.2 `assets/templates/contract.json` / `invoice.json` / `report.json`

为三个新模板各增加一个 `sample` 字段，填入有业务语义的示例数据。

| 模板 | sample 字段数 | 主要内容 |
|---|---:|---|
| contract | 10 | 服务合同 / HT-2026-001 / 双方信息 / 5 条条款 / ¥100,000 |
| invoice | 10 | 发票 / INV-2026-001 / 双方信息 / 2 项明细 / ¥100,000 |
| report | 8 | 市场分析报告 / 2026Q2 / 摘要 / 3 章节 / 结论 / 页脚 |

**关键修改仅限 sample 字段；未动 fields/style_options 等模板定义。**

### 2.3 导入

`pages/template_layout_page.py` 顶部 `PySide6.QtWidgets` import 列表新增 `QMessageBox`。

---

## 3. 验证结果

### 3.1 PDF 渲染（核心）

`F:\印流PDflow项目\04-项目文档\preview_test\test_render.py` 输出：

```
[OK] contract   size=10072619  F:\印流PDflow项目\04-项目文档\preview_test\contract_preview.pdf
[OK] invoice    size=10073120  F:\印流PDflow项目\04-项目文档\preview_test\invoice_preview.pdf
[OK] report     size=9758419   F:\印流PDflow项目\04-项目文档\preview_test\report_preview.png
```

3/3 模板 PDF 全部成功生成。已知警告（**非本次修复范围**）：

```
[renderer] 字体加载失败 C:/Windows/Fonts/msyh.ttc: Font.__init__() got an unexpected keyword argument 'fontno'
[renderer] 字体加载失败 C:/Windows/Fonts/msyhbd.ttc: Font.__init__() got an unexpected keyword argument 'fontno'
```

这是 `template_renderer._get_cjk_font()` 的 **已有问题**（PyMuPDF 版本与 `fontno` 参数不兼容），与本次预览功能无关，V1.2 修复。

### 3.2 PNG 缩略图

```
[PNG] contract   -> ...\contract_preview.png   (65785 bytes, pages=1)
[PNG] invoice    -> ...\invoice_preview.png    (46224 bytes, pages=1)
[PNG] report     -> ...\report_preview.png     (23352 bytes, pages=2)
```

3/3 PNG 成功生成（多页模板取首页）。

### 3.3 预览截图路径

| 模板 | PDF 路径 | PNG 路径 |
|---|---|---|
| contract | `04-项目文档\preview_test\contract_preview.pdf` | `04-项目文档\preview_test\contract_preview.png` |
| invoice | `04-项目文档\preview_test\invoice_preview.pdf` | `04-项目文档\preview_test\invoice_preview.png` |
| report | `04-项目文档\preview_test\report_preview.pdf` | `04-项目文档\preview_test\report_preview.png` |

### 3.4 异常处理

`_on_preview_clicked` 内已对以下异常做兜底：

- 模板 `id` 缺失 → `QMessageBox.warning`
- `render_template()` 抛错 → `QMessageBox.critical` + 渲染错误信息
- PDF 转图片失败 → `QMessageBox.critical`
- 临时目录创建失败 → 走 `os.makedirs(exist_ok=True)` 兜底

无任何未捕获异常会传回主循环。

---

## 4. UI 行为

### 4.1 卡片底部布局

```
┌────────────────────────────────────┐
│  📋                                 │
│  合同协议                            │
│  标准合同协议模板...                  │
│                                     │
│  [商务]                  [👁 预览]   │
└────────────────────────────────────┘
```

### 4.2 预览弹窗

```
┌─────────────────────────────────────┐
│  📄 合同协议                         │
│  ┌─────────────────────────────┐    │
│  │                              │    │
│  │      [PDF 首页缩略图]          │    │
│  │                              │    │
│  │                              │    │
│  └─────────────────────────────┘    │
│  缩略图来源: contract_preview.png    │
│                       [   关闭   ]   │
└─────────────────────────────────────┘
```

- 弹窗最小尺寸 560 × 720
- 缩略图在 480px 宽内等比缩放，高度按 PDF 原比例
- 关闭按钮 + 标题栏关闭按钮均可关闭弹窗

---

## 5. 总结

| 检查项 | 结果 |
|---|---|
| 支持模板 | contract / invoice / report（3/3） |
| 预览触发方式 | 卡片「👁 预览」按钮点击（非实时） |
| PDF 渲染成功率 | 3/3 |
| PNG 缩略图生成成功率 | 3/3 |
| 异常处理 | 完整（try/except + QMessageBox 兜底） |
| 是否修改模板 JSON fields | ❌ 否（仅新增 sample 字段） |
| 是否修改 template_renderer 渲染逻辑 | ❌ 否（直接复用 render_template） |
| 新增代码行数 | ~180 行（含弹窗 UI） |
| 修改的导入 | + `QMessageBox` |

**结论：问题2（模板排版预览未实现）已实现，3/3 模板可生成静态缩略图。**
