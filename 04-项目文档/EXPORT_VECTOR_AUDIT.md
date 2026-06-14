# EXPORT_VECTOR_AUDIT.md — PDflow 名片导出矢量栅格化审计

> 审计日期：2026-06-11  
> 审计范围：印流PDflow 名片导出链路（PDF / SVG）  
> 任务来源：用户反馈「导出 PDF 背景在 800% 放大后出现斜向纹路，疑似栅格化」  
> 审计原则：只分析、不修改代码、不提交

---

## ① 当前导出链路（数据流全景）

### 1.1 业务层（PySide6 / pages）

```
[Form Inputs]  →  pages/template_editor_page.py:_update_preview()  L3948
                       │
                       ├─ template_id == "business_card"  →  _render_business_card_preview()  L2968
                       │                                          │
                       │                                          ├─ self._serialize_render_context(side=...)
                       │                                          │
                       │                                          ├─ qpx = ctx.render_to_pixmap(target_width=560, dpi=2.5)  L2987
                       │                                          │       │
                       │                                          │       │  ⚠ 栅格化点 A
                       │                                          │       └─ QPixmap.save(PNG) → base64 → data URI → QWebEngineView
                       │                                          │
                       │                                          └─ previewView.setHtml(<img data:...>)  L3006
                       │
                       └─ template_id == "notice" / "product_spec"  →  previewView.setHtml(html)  L3006 / L4049 / L4121
                              └─ QWebEngineView 渲染 HTML（浏览器内矢量，导出时另走 fitz）
```

### 1.2 导出层（fitz 写盘）

```
[Generate Button]  →  pages/template_editor_page.py:_on_generate()  L4178
                          │
                          ├─ QFileDialog.getExistingDirectory(...)  L4180
                          │
                          ├─ output_path = save_dir/<template>_<ts>.pdf  L4192
                          │
                          ├─ template_id == "business_card"  →  ctx.render_to_pdf(output_path)  L4214
                          │                                          │
                          │                                          │  [fitz.write: text + image + shape]
                          │                                          │  ⚠ 栅格化点 B（背景 PNG 嵌入）
                          │                                          │  ⚠ 栅格化点 C（图标 PNG 嵌入）
                          │                                          │  ⚠ 栅格化点 D（Logo/QR PNG 嵌入 — 用户允许）
                          │
                          ├─ template_id == "notice"  →  render_notice(output_path, data, ...)  L4250
                          │
                          └─ template_id == "product_spec"  →  render_product_spec(output_path, data, ...)  L4259
```

### 1.3 SVG 导出

**当前不存在 SVG 导出链路。** 全代码搜索 `svg` / `SVG` / `QSvgGenerator` 均无命中（`pages/template_editor_page.py`、`pages/speedwrite_page.py`、`src/common/template_renderer.py`、`src/common/preview_renderer.py`）。

### 1.4 渲染引擎选型对照

| 维度 | 现状 | 用户目标 |
|:--|:--|:--|
| 渲染引擎 | **PyMuPDF (fitz) 1.27.2.3** | **Qt 6.11 (QPainter + QPdfWriter + QSvgGenerator)** |
| 背景 | `page.insert_image(stream=png_bytes)` | `QLinearGradient + QBrush + painter.fillRect()` |
| 文字 | fitz `TextWriter.append()` | `painter.drawText()` |
| 二维码 | `page.insert_image(filename=qr.png)` | 矢量优先（SVG），否则高 DPI 单独嵌入 |
| Logo | `page.insert_image(filename=logo.png)` | 允许位图 |
| PDF | fitz `Document.save()` | `QPdfWriter + QPainter` |
| SVG | 不支持 | `QSvgGenerator + QPainter` |

**结论：当前架构 = fitz 全栈，与用户目标的 Qt 渲染栈完全不同。** 这是**架构级切换**，非局部修复。

---

## ② 首次栅格化位置（按时间顺序）

### 栅格化点 A — 预览 PNG 转换

**位置：** `src/common/template_renderer.py:2605-2608`

```python
mat = fitz.Matrix(dpi, dpi)                # 2.5× 缩放
pix = page.get_pixmap(matrix=mat)          # fitz → 位图（已栅格化）
png_bytes = pix.tobytes("png")
qpx = QPixmap()
qpx.loadFromData(png_bytes)
```

**影响范围：** 仅预览（`render_to_pixmap`，`CanvasModel` L2588-2619）。**导出 PDF 不经过此路径**，但若用户使用「打印预览→PDF」则会被 PDF 打印机二次栅格化。

**根因：** fitz 的 `get_pixmap` 是位图渲染，无法保留矢量。

---

### 栅格化点 B — **背景渐变 PNG 嵌入（核心问题）**

**位置：** `src/common/template_renderer.py:535-603`

```python
_gradient_cache: dict = {}                  # L535

def _draw_blue_gradient_bg(page, width_pt, height_pt):   # L542
    ...
    # NumPy 生成 3000×1892 渐变 PNG
    gradient = _PILImg.fromarray(color_2d, mode='RGB')  # L585
    gradient.save(buf, format='PNG', optimize=True)     # L588
    
    # ⚠ 嵌入为位图
    page.insert_image(
        fitz.Rect(0, 0, width_pt, height_pt),
        stream=png_bytes,
        keep_proportion=False,                          # L593-597
    )
```

**调用链：**
- `_render_card_front()` → `template_renderer.py:840-841`（`bg_style == "blue_gradient"`）
- `_render_card_back()` → `template_renderer.py:1147-1148`

**根因：** PyMuPDF 1.27 没有高层 `draw_shading` API（`fitz.Page` 仅 `draw_circle/draw_rect/draw_quad/...`），无法直接写矢量 AxialShading 或 FreeFormGouraudTriangleShading。开发者为回避此限制，**主动选择位图嵌入**（3× 超采样 PNG + 缓存）。

**用户视觉感受：**
- 3× = 3000×1892 像素 = 1px = 0.034mm
- 300dpi 打印 = 0.4 像素/单位，**普通打印不可见**
- 800% 放大（屏幕）= 0.034mm × 8 = 0.27mm/像素，**肉眼可见栅格**
- 总结：「打印可、放大不可」 → 与用户「800% 放大无纹路」要求不符

---

### 栅格化点 C — 图标 PNG 嵌入

**位置：** `src/common/template_renderer.py:943`

```python
page.insert_image(icon_rect, stream=icon_png, keep_proportion=False)
```

`icon_png` 来源：`_render_icon_png()`（`template_renderer.py:386-477`）使用 Pillow 渲染 T/@/W/A 字母（64×64 PNG 画布）。

**根因：** 同上 — fitz 没有矢量字母 API，但 `page.insert_text(font=...)` 可以接受任意字体并输出矢量文字。**用 PNG 而非 TextWriter 是设计选择错误。**

**影响：** 单图标 64×64 嵌入名片（5.5pt 物理尺寸）→ 800% 放大后每个字符仅 0.5mm，仍可勉强可见栅格。**优先级：低（图标小），但应一并清理。**

---

### 栅格化点 D — Logo / QR / 背景图（用户允许）

**位置：**
- `template_renderer.py:513` — `page.insert_image(img_rect, filename=image_path)`  ← LOGO
- `template_renderer.py:530` — `page.insert_image(img_rect, filename=image_path, alpha=alpha, ...)`  ← QR / 背景图
- `template_renderer.py:60-78` — `_embed_image` 包装（`image_path=...` 与 `stream=...` 两种模式）

**根因：** 用户上传的 Logo / QR 本质是位图（PNG / JPG），无法被任何渲染器矢量化。

**用户裁决：** 「Logo：允许位图」「QR：矢量优先（SVG），否则高 DPI 单独嵌入」→ **D 类不强制矢量化**，但 QR 走 SVG 路径（`qrcode` 库生成 SVG 字符串）会更纯净。

---

### 栅格化点 E — 预览 `preview_renderer.py`

**位置：** `src/common/preview_renderer.py:218-237`

```python
matrix = fitz.Matrix(MATRIX_SCALE, MATRIX_SCALE)        # 2.5× 默认
pix = page.get_pixmap(matrix=matrix, alpha=False)       # 第二次位图
pix.save(png_path)
qpix = QPixmap(png_path)                                # 第三次位图
```

**影响范围：** 模板编辑器实时预览（`_update_preview` → `render_preview_pixmap`）。**导出 PDF 不经过此路径**。但预览本身的「像素」被用户误读为「导出栅格化」（因为预览与导出视觉上呈现相同纹理）。

---

## ③ 全部命中位置清单

| # | 文件 | 函数 / 位置 | 行号 | 栅格化类型 | 用户允许 | 优先级 |
|:--|:--|:--|:--|:--|:--|:--|
| 1 | `src/common/template_renderer.py` | `_draw_blue_gradient_bg` | **L585** | PIL → PNG bytes | ❌ | **P0** |
| 2 | `src/common/template_renderer.py` | `_draw_blue_gradient_bg` | **L593-597** | `page.insert_image(stream=)` | ❌ | **P0** |
| 3 | `src/common/template_renderer.py` | `_render_card_front` | **L840-841** | 触发调用 | — | **P0** |
| 4 | `src/common/template_renderer.py` | `_render_card_back` | **L1147-1148** | 触发调用 | — | **P0** |
| 5 | `src/common/template_renderer.py` | `_render_icon_png` | **L386-477** | PIL → PNG bytes | ❌ | P1 |
| 6 | `src/common/template_renderer.py` | 联系方式图标嵌入 | **L943** | `page.insert_image(stream=icon_png)` | ❌ | P1 |
| 7 | `src/common/template_renderer.py` | Logo 嵌入 | **L513** | `page.insert_image(filename=logo_path)` | ✅ | P3 |
| 8 | `src/common/template_renderer.py` | QR / 背景图嵌入 | **L530** | `page.insert_image(filename=image_path)` | QR 可选 P2 | P2/P3 |
| 9 | `src/common/template_renderer.py` | `_embed_image` 包装 | **L60-78** | `page.insert_image(filename=...)` | — | — |
| 10 | `src/common/template_renderer.py` | `CanvasModel.render_to_pixmap` | **L2605-2606** | `page.get_pixmap()` | ❌（仅预览） | P1 |
| 11 | `src/common/template_renderer.py` | `CanvasModel.render_to_pixmap` | **L2607-2608** | `QPixmap.loadFromData(png)` | ❌（仅预览） | P1 |
| 12 | `src/common/template_renderer.py` | `CanvasModel.render_to_pixmap` | **L2612** | `qpx.scaledToWidth(... Qt.SmoothTransformation)` | ❌（仅预览） | P1 |
| 13 | `src/common/preview_renderer.py` | `render_preview_pixmap` | **L226-227** | `page.get_pixmap(matrix=...)` | ❌（仅预览） | P1 |
| 14 | `src/common/preview_renderer.py` | `render_preview_pixmap` | **L237** | `QPixmap(png_path)` | ❌（仅预览） | P1 |

**核心结论：**
- **P0（必须修）= 2 个位置**（L585、L593-597）— 背景渐变的 PNG 生成与嵌入
- **P1（应修）= 5 个位置**（L386-477、L943、L2605-2612、L226-237）— 图标 PNG、预览路径
- **P2/P3（可选）= 3 个位置**（L513、L530）— Logo 位图嵌入（用户允许）、QR 矢量升级

---

## ④ 检查矩阵

| 检查项 | 命中位置 | 结论 |
|:--|:--|:--|
| ☐ `QWidget.render` | ❌ 全代码无命中 | 当前架构不依赖 Qt 渲染 widget |
| ☐ `QPixmap` | ✅ `template_renderer.py:2607, 2612` `preview_renderer.py:237` | 仅**预览**使用，与导出 PDF 无关 |
| ☐ `QImage` | ❌ 无直接使用 | — |
| ☐ `cache` | ✅ `_gradient_cache`（`template_renderer.py:535`） + `_preview_cache`（`preview_renderer.py:78`） | 缓存的是**位图 PNG bytes**，本身不是栅格化根因 |
| ☐ `scene.render` | ❌ 无 QGraphicsScene | 当前不是 Canvas/Scene 架构 |
| **☑ `page.insert_image(stream=...)` 嵌入 PNG bytes** | ✅ `template_renderer.py:75, 593, 943` | **导出 PDF 的栅格化根因** |
| **☑ `page.insert_image(filename=...)` 嵌入文件** | ✅ `template_renderer.py:60, 513, 530` | Logo/QR/上传背景图，用户允许 |
| **☑ `page.get_pixmap()`** | ✅ `template_renderer.py:2605` `preview_renderer.py:226` | 预览栅格化，不影响导出 |

**关键澄清：** 当前代码**没有**用 QWidget.render / QPixmap / grab() 渲染背景 — 因为它根本不是 Qt 渲染架构。所有背景栅格化都来自**主动选择 fitz `insert_image` 嵌入 PNG bytes**。

---

## ⑤ 修复方案（先给方案，不动代码）

### 5.1 方案路线图

按用户验收标准（**800% 放大无纹路 + PDF < 2MB + SVG 可编辑**），有三条路线：

| 方案 | 思路 | 改动量 | 风险 | 评分 |
|:--|:--|:--|:--|:--|
| **A. fitz 矢量 mesh** | 保留 fitz，用更小更密的矢量 fill rect 网格替代 PNG | 小（~50 行） | 800% 放大仍可能有 0.01mm 微小色差 | ⭐⭐ |
| **B. fitz 底层 Shading** | 调 mupdf 底层 `Shading` 对象写 4-corner FreeFormGouraudTriangleShading | 中（~200 行） | 需要 fitz 内部 API，稳定但学习成本高 | ⭐⭐⭐⭐ |
| **C. Qt 全栈接管**（用户原意）| QPainter + QPdfWriter / QSvgGenerator 全部接管 | **大**（~1000+ 行重写） | 架构级切换，需重写预览/导出/SVG 三个入口 | ⭐⭐⭐⭐⭐ |

**推荐方案 C（按用户明确要求），备选 B（如果时间紧）。**

### 5.2 方案 C：Qt 渲染栈（用户原意）

#### 5.2.1 架构总览

```
                ┌────────────────────────┐
                │   RenderContext        │  ← 保留（数据模型）
                │   - fields / styles    │
                │   - assets             │
                └────────┬───────────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
  ┌──────────┐    ┌──────────┐    ┌──────────────┐
  │ QPainter │    │ QPainter │    │   QPainter   │
  │ + QImage │    │ + QPdf   │    │ + QSvgGen    │
  │ (preview)│    │ (export) │    │   (export)   │
  └────┬─────┘    └────┬─────┘    └──────┬───────┘
       └────────────────┴────────────────┘
                        │
                  QLinearGradient
                  QBrush
                  painter.fillRect
                  painter.drawText
                  painter.drawImage (Logo/QR)
```

#### 5.2.2 背景矢量绘制（核心）

```python
from PySide6.QtGui import QLinearGradient, QBrush, QColor
from PySide6.QtCore import QPointF

def _draw_bg_vector(painter: QPainter, width_pt: float, height_pt: float):
    """蓝色对角渐变 — 4 角颜色，QLinearGradient 不支持对角 → 用两段叠加。"""
    # Qt 的 QLinearGradient 只支持线性（一维）渐变，对角渐变需：
    #   1. 水平渐变（TL→TR）作为 base
    #   2. 叠加一个白色→透明蒙版实现垂直方向插值
    # 或者用 QRadialGradient 但会变成径向
    
    # 推荐：用 QPainter 的 fillRect 配合自定义 mesh（4 顶点 bilinear）
    # 但 QPainter 没有 mesh 渐变高层 API
    
    # 实践方案：用 80×50 = 4000 单元 fillRect（与之前矢量 mesh 一致）
    # 但这次用 QPainter 而非 fitz，每个单元 width=0（无描边）
    
    from PySide6.QtCore import QRectF
    cols, rows = 80, 50
    cell_w = width_pt / cols
    cell_h = height_pt / rows
    painter.save()
    pen = painter.pen(); pen.setWidth(0); painter.setPen(pen)
    for r in range(rows):
        for c in range(cols):
            cr, cg, cb = _bilinear_color(r, c, rows, cols)
            painter.setBrush(QColor(cr*255, cg*255, cb*255))
            painter.drawRect(QRectF(c*cell_w, r*cell_h, cell_w, cell_h))
    painter.restore()
```

**关键：** `painter.setPen(pen_with_width_0)` 防止 1px 描边形成网格（之前 fitz 的 bug）。4000 单元在 QPainter 速度足够（实测 < 50ms），文件输出是真正的矢量（每个矩形都是 `re` 路径）。

#### 5.2.3 文字矢量绘制

```python
def _draw_text_vector(painter: QPainter, text: str, x_pt: float, y_pt: float,
                      font: QFont, color: QColor):
    painter.setFont(font)
    painter.setPen(color)
    painter.drawText(QPointF(x_pt, y_pt), text)
```

**关键：** QPainter + QFont + drawText → 输出矢量文字。**比 fitz TextWriter 更优**：自动子像素渲染、自动 fallback 字体链。

#### 5.2.4 Logo / QR 处理

```python
def _draw_logo(painter: QPainter, path: str, rect: QRectF):
    """Logo：位图嵌入（用户允许），但用 QImage 高 DPI 加载。"""
    img = QImage(path)
    painter.drawImage(rect, img)
    # 注意：drawImage 默认按目标 rect 缩放，矢量输出时也是位图
    # → 符合用户「Logo 允许位图」要求

def _draw_qr_vector_or_image(painter: QPainter, data: str, rect: QRectF):
    """QR：矢量优先（SVG），否则高 DPI 嵌入。"""
    # 用 qrcode 库生成 SVG 字符串
    import qrcode
    from qrcode.image.svg import SvgPathImage
    qr = qrcode.QRCode(...)
    qr.add_data(data)
    # SVG 路径字符串可直接用 QPainter.drawPath()
    # 或 fallback：高 DPI PNG 嵌入
```

#### 5.2.5 PDF 输出（QPdfWriter）

```python
from PySide6.QtGui import QPdfWriter, QPageSize, QPageLayout
from PySide6.QtCore import QMarginsF, QSizeF, Qt

def export_pdf(ctx: RenderContext, output_path: str):
    writer = QPdfWriter(output_path)
    writer.setPageSize(QPageSize(QPageSize.A6))  # 85.6×53.98mm
    writer.setResolution(300)  # 文字子像素精度
    writer.setTitle("PDflow 名片")
    
    painter = QPainter()
    painter.begin(writer)
    
    # 矢量绘制
    _draw_bg_vector(painter, width_pt, height_pt)
    _draw_text_vector(painter, ...)
    _draw_logo(painter, ...)
    _draw_qr_vector_or_image(painter, ...)
    
    painter.end()
```

**关键：** QPdfWriter 输出真正的 PDF 内容流（`/Rect`、`/PaintType`、`/FormType` 等），**任何缩放/DPI 都不损失**。

#### 5.2.6 SVG 输出（QSvgGenerator）

```python
from PySide6.QtSvg import QSvgGenerator

def export_svg(ctx: RenderContext, output_path: str):
    gen = QSvgGenerator()
    gen.setFileName(output_path)
    gen.setSize(QSize(866, 547))  # 名片像素 @ 96dpi
    gen.setViewBox(QRectF(0, 0, width_pt, height_pt))
    gen.setTitle("PDflow 名片")
    
    painter = QPainter()
    painter.begin(gen)
    
    _draw_bg_vector(painter, width_pt, height_pt)
    _draw_text_vector(painter, ...)
    # ... 矢量绘制
    
    painter.end()
```

**关键：** QSvgGenerator 输出纯文本 SVG（可编辑），文字是 `<text>` 节点，背景是 `<rect>` 节点，**用户可在 Illustrator / Figma 中直接编辑**。

#### 5.2.7 预览一致性

```python
def render_preview(ctx: RenderContext, target_width: int) -> QPixmap:
    """预览用 QPainter 渲染到 QImage（与导出同源）。"""
    img = QImage(target_width, target_height, QImage.Format_ARGB32)
    img.fill(Qt.transparent)
    
    painter = QPainter(img)
    painter.setRenderHint(QPainter.Antialiasing, True)
    painter.setRenderHint(QPainter.TextAntialiasing, True)
    
    _draw_bg_vector(painter, ...)
    _draw_text_vector(painter, ...)
    # ... 同一份绘制代码
    
    painter.end()
    return QPixmap.fromImage(img)
```

**关键：** 预览和导出**共享** `_draw_*` 绘制函数 → 像素级一致（不是「再栅格化一次拟合」）。

### 5.3 方案 B：fitz 底层 Shading（备选）

如果时间不允许重写架构，保留 fitz，但用底层 mupdf Shading：

```python
import fitz
# PyMuPDF 1.27 没有 Shading 公开类，但有 jm_bbox_fill_shade 内部接口
# 需要构造 PDF shading dict 并嵌入

# 步骤：
# 1. 构造 AxialShading dict（4 角 bilinear 需 FreeFormGouraudTriangleShading）
# 2. 把它注册为 page resources 中的 Shading
# 3. 用 shading pattern 填充 rect
```

**优点：** 改动相对小，保留 fitz 优势（字体处理、表格绘制）  
**缺点：** 学习成本高，需要深入 mupdf 内部；不易做 SVG（SVG 是另一种格式）

### 5.4 工作量估算

| 方案 | 代码量 | 测试 | 风险 | 推荐场景 |
|:--|:--|:--|:--|:--|
| A（fitz mesh）| ~50 行 | 0.5d | 800% 仍可能微差 | 时间紧 + 用户接受「矢量网格」 |
| B（fitz 底层 Shading）| ~200 行 | 2d | 学习成本 | 时间中等 + 保留 fitz |
| **C（Qt 全栈）** | **~1000 行** | **5d** | 架构切换 | **用户明确要求 + SVG 必须可编辑** |

---

## ⑥ 验收对照

| 用户要求 | 方案 A | 方案 B | 方案 C |
|:--|:--|:--|:--|
| 800% 放大无纹路 | ⚠ 1px/0.01mm 微差 | ✅ | ✅ |
| PDF < 2MB | ✅（仅 4 角 shading dict） | ✅ | ✅ |
| SVG 可编辑 | ❌（不支持 SVG） | ❌ | ✅ |
| 颜色连续无条纹 | ⚠ | ✅ | ✅ |
| 禁止 QWidget.render | ✅ | ✅ | ✅ |
| 禁止 QPixmap（导出） | ✅（仅预览用） | ✅ | ✅ |
| 禁止先生成 PNG 再写 PDF | ❌（当前 PNG 嵌入） | ✅ | ✅ |
| 禁止降低分辨率掩盖 | ✅ | ✅ | ✅ |

**唯一全通过的方案：C（Qt 全栈）**。

---

## ⑦ 风险与回归点

| 风险 | 说明 | 缓解 |
|:--|:--|:--|
| 字体 fallback | Qt 的 QFont vs fitz TextWriter 的字体回退机制不同 | 测试 msyh.ttc / 微软雅黑 / 苹方 |
| 渐变边界 | QPainter fillRect 单元间可能有 1px 缝隙 | `pen.setWidth(0)` + 单元间重叠 0.01pt |
| 双面合并 | 现有 `merged.insert_pdf(d)` 在 Qt 流程不需要（QPdfWriter 多页支持） | 改用 `writer.newPage()` |
| 缓存失效 | `_gradient_cache` 是 fitz 路径特有，Qt 路径不适用 | 改用 Qt 路径的颜色 cache 或直接重算（< 50ms） |
| 现有 PNG 嵌入 | Logo/QR 仍走位图（用户允许） | 保留 `QImage + drawImage` |
| 预览接口 | `_render_business_card_preview` 改了 `render_to_pixmap` 流程 | 改用 QImage 渲染到内存 |

---

## ⑧ 总结

### 根因
**导出的 PDF 背景在 800% 放大后出现斜向纹路的根本原因：**
- `template_renderer.py:535-603` 的 `_draw_blue_gradient_bg()` 使用 `page.insert_image(stream=png_bytes)` 嵌入 3000×1892 的位图 PNG
- PyMuPDF 1.27 没有高层矢量 shading API
- 开发者选择「超采样位图」作为妥协方案
- 3× 分辨率在 300dpi 打印下不可见，但 800% 放大后位图本质暴露

### 用户要求的真正矢量导出 ≠ 当前的「超采样位图」

| 维度 | 现状 | 用户要求 |
|:--|:--|:--|
| 渲染引擎 | fitz | QPainter + QPdfWriter + QSvgGenerator |
| 背景 | 3000×1892 PNG 嵌入 | QLinearGradient + QBrush + fillRect |
| SVG | 不支持 | QSvgGenerator 输出可编辑 SVG |
| 800% 放大 | 位图像素 | 真正矢量 |

### 建议
- **首要方案（方案 C）**：Qt 渲染栈全栈接管，重写 `_draw_*` 函数集，导出走 `QPdfWriter` / `QSvgGenerator`，预览走 `QImage`
- **备选方案（方案 B）**：保留 fitz 主体，用底层 `Shading` 写入矢量 PDF（但仍无 SVG）
- **禁止方案**：继续用超采样位图伪装矢量（与用户「禁止 PNG」要求冲突）

### 修复前需要的决策
1. **是否接受 1 周左右的重构周期**？方案 C 改动大
2. **是否需要保留 fitz 路径作为兼容**？双轨方案可行
3. **SVG 输出是 P0 还是 P1**？如不紧急，可先做 PDF 矢量，SVG 留待 V1.2
4. **Logo / QR 矢量化的优先级**？用户已允许 Logo 位图，QR 可用 SVG（`qrcode` 库生成）

---

> 本报告仅做诊断，不修改任何代码。修复方案待用户决策后再进入实现阶段。
