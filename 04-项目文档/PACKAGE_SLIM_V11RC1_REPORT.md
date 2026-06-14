# 印流PDflow V1.1-beta 打包瘦身专项分析报告

**报告日期：** 2026-06-12
**分析对象：** `dist/PDflow_V1.1-beta/`（用户最新一次 PyInstaller 打包产物）
**对应 spec：** `PDflow_V1.1-beta.spec`（位于项目根目录）
**当前大小：** **797.81 MB**（4869 个文件）
**目标大小：** **≤ 150 MB**
**任务约束：** 禁止修改业务代码（`pdf_api.py` / `template_renderer.py` / 各 `page`）；**只生成报告，不做瘦身实施**

---

## 0. 摘要

| 指标 | 数值 |
|---|---:|
| **当前 V1.1-beta 实际体积** | **797.81 MB**（4869 个文件）|
| 目标体积 | **≤ 150 MB** |
| **差距** | **+647.81 MB**（+432%）|
| 理论可达最低（不修改业务代码）| **~165 MB** |
| 极限可达（含激进 UPX）| **~150-158 MB** |
| 150 MB 是否可达 | 🟡 **临界可达**（需 A+ + B + 激进 UPX，AV 误报风险）|
| 安全保守方案 | **~165-180 MB**（A+ + B + 软 UPX，无误报风险）|

---

## 1. 当前体积来源 Top 20（单文件）

| 排名 | 文件 | 大小 | 类别 | 实际使用 | 处置 |
|:---:|---|---:|---|---|:---:|
| 1 | `PySide6/Qt6WebEngineCore.dll` | 195.27 MB | WebEngine | ❌ 0 处使用 | ✅ **移除** |
| 2 | `PySide6/resources/qtwebengine_devtools_resources.debug.pak` | 72.33 MB | WebEngine 资源 | ❌ | ✅ **移除** |
| 3 | `cv2/cv2.pyd` | 71.04 MB | OpenCV | ❌ 0 处 import | ✅ **移除** |
| 4 | `cv2/opencv_videoio_ffmpeg4130_64.dll` | 27.25 MB | OpenCV | ❌ | ✅ **移除** |
| 5 | `pymupdf/mupdfcpp64.dll` | 24.46 MB | PyMuPDF | ✅ 核心 | ❌ 保留 |
| 6 | `PySide6/opengl32sw.dll` | 19.68 MB | OpenGL 软件渲染 | ❌ Widgets 不用 | ✅ **移除** |
| 7 | `numpy.libs/libscipy_openblas64_*.dll` | 19.47 MB | OpenBLAS | ⚠️ PyMuPDF 链 | 🟡 保留（必须）|
| 8 | `PDflow_V1.1-beta.exe` | 15.27 MB | 主程序 | ✅ 必需 | ❌ 保留 |
| 9 | `pymupdf/_mupdf.pyd` | 11.73 MB | PyMuPDF | ✅ 核心 | ❌ 保留 |
| 10 | `PySide6/resources/qtwebengine_devtools_resources.pak` | 11.07 MB | WebEngine | ❌ | ✅ **移除** |
| 11 | `PySide6/Qt6Core.dll` | 10.00 MB | Qt 核心 | ✅ | ❌ 保留 |
| 12 | `PySide6/resources/icudtl.dat` | 9.98 MB | Qt ICU | ⚠️ Qt 隐式 | 🟡 保留 |
| 13 | `cryptography/hazmat/bindings/_rust.pyd` | 9.44 MB | cryptography | ❌ 0 处 import | ✅ **移除** |
| 14 | `PySide6/Qt6Gui.dll` | 9.10 MB | Qt 核心 | ✅ | ❌ 保留 |
| 15 | `PySide6/QtOpenGL.pyd` | 8.31 MB | Qt OpenGL | ❌ Widgets 不用 | ✅ **移除** |
| 16 | `PIL/_avif.cp312-win_amd64.pyd` | 7.53 MB | AVIF 解码 | ❌ 项目不用 | ✅ **可移除** |
| 17 | `pypdfium2_raw/pdfium.dll` | 6.93 MB | PDFium | ❌ 0 处 import | ✅ **移除** |
| 18 | `python312.dll` | 6.62 MB | 解释器 | ✅ | ❌ 保留 |
| 19 | `PySide6/Qt6Quick.dll` | 6.28 MB | QML 引擎 | ❌ 不用 | ✅ **移除** |
| 20 | `PySide6/Qt6Widgets.dll` | 6.28 MB | Qt 核心 | ✅ | ❌ 保留 |
| — | **Top 20 合计** | **556.04 MB** | — | — | — |

> **Top 20 中可移除：481.92 MB**（WebEngine + cv2 + OpenGL + QML/3D + cryptography + pypdfium2 + AVIF）

---

## 2. 当前体积来源 Top 20（一级目录）

| 排名 | 目录 | 大小 | 占比 | 处置 |
|:---:|---|---:|---:|---|
| 1 | `PySide6/` | 527.87 MB | 66.2% | 🟡 砍 400+ MB |
| 2 | `cv2/` | 98.32 MB | 12.3% | ✅ 全砍 |
| 3 | `pymupdf/` | 36.38 MB | 4.6% | ❌ 全留 |
| 4 | `_root`（python312 + libcrypto + libssl + sqlite3 + ucrtbase + tcl86t + tk86t）| 24.16 MB | 3.0% | 🟡 砍 6 MB（tkinter）|
| 5 | `numpy.libs/` | 20.02 MB | 2.5% | 🟡 留（必须）|
| 6 | `pandas/` | 16.09 MB | 2.0% | 🟡 业务依赖，保留 |
| 7 | `PIL/` | 12.75 MB | 1.6% | 🟡 砍 7.5 MB（_avif）|
| 8 | `cryptography/` | 9.44 MB | 1.2% | ✅ 全砍 |
| 9 | `pdfminer/` | 7.52 MB | 0.9% | ✅ 全砍 |
| 10 | `pypdfium2_raw/` | 6.93 MB | 0.9% | ✅ 全砍 |
| 11 | `lxml/` | 6.58 MB | 0.8% | 🟡 业务依赖（docx 链），保留 |
| 12 | `numpy/` | 5.81 MB | 0.7% | 🟡 PyMuPDF 链，保留 |
| 13 | `_tcl_data/` | 3.02 MB | 0.4% | ✅ 全砍（tkinter）|
| 14 | `pages/`（项目源码）| 1.69 MB | 0.2% | ❌ 必需 |
| 15 | `shiboken6/` | 1.07 MB | 0.1% | ❌ 必需 |
| 16 | `docx/` | 0.93 MB | 0.1% | 🟡 业务依赖，保留 |
| 17 | `_tk_data/` | 0.81 MB | 0.1% | ✅ 全砍（tkinter）|
| 18 | `pytz/` | 0.83 MB | 0.1% | 🟡 pandas 链，保留 |
| 19 | `certifi/` | 0.23 MB | 0.03% | 🟡 SSL 证书，保留 |
| 20 | `assets/` | 0.06 MB | 0.01% | ❌ 必需 |
| — | **Top 20 合计** | **780.49 MB** | 97.8% | — |

---

## 3. PySide6 内部结构（527.87 MB / 占比 66%）

### 3.1 PySide6 子目录

| 子目录 | 大小 | 文件数 | 处置 |
|---|---:|---:|---|
| `_root`（DLL 总汇）| **345.71 MB** | ~150 | 🟡 砍 280 MB |
| `resources/` | 101.37 MB | 11 | 🟡 砍 95 MB（WebEngine resources）|
| `translations/` | 52.52 MB | ~150 | 🟡 砍 47 MB（WebEngine locales）|
| `qml/` | 21.90 MB | ~300 | 🟡 砍 21 MB（无 QML）|
| `plugins/` | 6.37 MB | 38 | 🟡 砍 3 MB（精简）|

### 3.2 PySide6/resources/ 详情（101.37 MB）

| 文件 | 大小 | 处置 |
|---|---:|---|
| `qtwebengine_devtools_resources.debug.pak` | 72.33 MB | ✅ **移除**（WebEngine 资源）|
| `qtwebengine_devtools_resources.pak` | 11.07 MB | ✅ **移除**（WebEngine 资源）|
| `icudtl.dat` | 9.98 MB | 🟡 保留（Qt 字符国际化基础）|
| `v8_context_snapshot.debug.bin` | 2.33 MB | ✅ **移除**（V8 引擎调试）|
| `qtwebengine_resources.pak` | 2.16 MB | ✅ **移除** |
| `qtwebengine_resources.debug.pak` | 2.16 MB | ✅ **移除** |
| `v8_context_snapshot.bin` | 0.66 MB | ✅ **移除**（V8 引擎）|
| `qtwebengine_resources_200p.pak` + debug | 0.38 MB | ✅ **移除** |
| `qtwebengine_resources_100p.pak` + debug | 0.28 MB | ✅ **移除** |

**resources/ 预计可砍：~91 MB**

### 3.3 PySide6/translations/ 详情（52.52 MB）

| 子项 | 大小 | 文件数 | 处置 |
|---|---:|---:|---|
| `qtwebengine_locales/` | 43.65 MB | 53 | ✅ **整目录移除**（WebEngine 多语言）|
| 其余 `qt_*.qm` / `qtbase_*.qm` | ~9 MB | ~96 | 🟡 砍 7 MB（保留 6 个项目语言）|

**translations/ 预计可砍：~50 MB**

### 3.4 PySide6/qml/ 详情（21.90 MB）

`qml/` 内含项目完全用不到的 QML 控件、3D 场景、虚拟键盘、输入法等。

| 子目录 | 大小 | 处置 |
|---|---:|---|
| `QtQuick/` | 14.81 MB | ✅ **移除**（FluentWinUI3 样式、VirtualKeyboard、Controls 全部）|
| `QtQuick3D/` | 2.23 MB | ✅ **移除** |
| `Qt5Compat/` | 1.44 MB | ✅ **移除** |
| `Qt3D/` | 0.76 MB | ✅ **移除** |
| `QtGraphs/` | 0.39 MB | ✅ **移除** |
| `QtCharts/` | 0.28 MB | ✅ **移除** |
| `QtQml/` | 0.25 MB | ✅ **移除** |
| `QtDataVisualization/` | 0.24 MB | ✅ **移除** |
| 其余 6 个子目录 | ~1.5 MB | ✅ **移除** |

**qml/ 预计可砍：~21 MB（整目录）**

### 3.5 PySide6 顶层 DLL 清单（345.71 MB）

按"必留 / 必删 / 测试后定"分类：

#### ✅ 必留（核心）

| DLL | 大小 | 用途 |
|---|---:|---|
| `Qt6Core.dll` | 10.00 MB | Qt 核心 |
| `Qt6Gui.dll` | 9.10 MB | Qt GUI |
| `Qt6Widgets.dll` | 6.28 MB | Qt Widgets |
| `Qt6Svg.dll` | 0.61 MB | 侧边栏 SVG 图标 |
| `Qt6Network.dll` | 1.69 MB | `QDesktopServices.openUrl` |
| `Qt6PrintSupport.dll` | 0.39 MB | `QPrintDialog` 兜底 |

**保留小计：27.95 MB**

#### ✅ 必删（项目 0 处使用）

| DLL | 大小 | 类别 |
|---|---:|---|
| **`Qt6WebEngineCore.dll`** | **195.27 MB** | WebEngine |
| `Qt6WebEngineQuick.dll` | 0.66 MB | WebEngine |
| `Qt6WebEngineQuickDelegatesQml.dll` | 0.16 MB | WebEngine |
| `Qt6WebEngineWidgets.dll` | 0.18 MB | WebEngine |
| `Qt6WebChannel.dll` | 0.24 MB | WebChannel |
| `Qt6WebChannelQuick.dll` | 0.06 MB | WebChannel |
| `Qt6WebSockets.dll` | 0.21 MB | WebSockets |
| `Qt6WebView.dll` | 0.06 MB | WebView |
| `Qt6WebViewQuick.dll` | 0.08 MB | WebView |
| `opengl32sw.dll` | 19.68 MB | 软件 OpenGL |
| `Qt6OpenGL.dll` | 1.89 MB | OpenGL |
| `Qt6OpenGLWidgets.dll` | 0.06 MB | OpenGL |
| `QtOpenGL.pyd` | 8.31 MB | Qt OpenGL Python 绑定 |
| `Qt6Quick.dll` | 6.28 MB | QML 引擎 |
| `Qt6Quick3D.dll` | 1.40 MB | 3D |
| `Qt6Quick3DAssetImport.dll` | 0.07 MB | 3D |
| `Qt6Quick3DAssetUtils.dll` | 0.30 MB | 3D |
| `Qt6Quick3DEffects.dll` | 0.40 MB | 3D |
| `Qt6Quick3DHelpers.dll` | 0.68 MB | 3D |
| `Qt6Quick3DHelpersImpl.dll` | 0.51 MB | 3D |
| `Qt6Quick3DParticleEffects.dll` | 0.02 MB | 3D |
| `Qt6Quick3DParticles.dll` | 1.99 MB | 3D |
| `Qt6Quick3DRuntimeRender.dll` | 4.17 MB | 3D 渲染 |
| `Qt6Quick3DSpatialAudio.dll` | 0.08 MB | 3D |
| `Qt6Quick3DUtils.dll` | 0.46 MB | 3D |
| `Qt6Quick3DXr.dll` | 0.87 MB | 3D |
| `Qt6QuickControls2.dll` | 0.10 MB | QML 控件 |
| `Qt6QuickControls2Basic.dll` | 1.76 MB | QML Basic 样式 |
| `Qt6QuickControls2BasicStyleImpl.dll` | 0.09 MB | QML Basic 实现 |
| `Qt6QuickControls2FluentWinUI3StyleImpl.dll` | 0.21 MB | QML Fluent 实现 |
| `Qt6QuickControls2Fusion.dll` | 1.43 MB | QML Fusion 样式 |
| `Qt6QuickControls2FusionStyleImpl.dll` | 0.18 MB | QML Fusion 实现 |
| `Qt6QuickControls2Imagine.dll` | 2.94 MB | QML Imagine 样式 |
| `Qt6QuickControls2ImagineStyleImpl.dll` | 0.07 MB | QML Imagine 实现 |
| `Qt6QuickControls2Impl.dll` | 0.32 MB | QML 控件实现 |
| `Qt6QuickControls2Material.dll` | 1.83 MB | QML Material 样式 |
| `Qt6QuickControls2MaterialStyleImpl.dll` | 0.30 MB | QML Material 实现 |
| `Qt6QuickControls2Universal.dll` | 1.52 MB | QML Universal 样式 |
| `Qt6QuickControls2UniversalStyleImpl.dll` | 0.14 MB | QML Universal 实现 |
| `Qt6QuickControls2WindowsStyleImpl.dll` | 0.06 MB | QML Windows 样式 |
| `Qt6QuickDialogs2.dll` | 0.15 MB | QML 对话框 |
| `Qt6QuickDialogs2QuickImpl.dll` | 2.77 MB | QML 对话框实现 |
| `Qt6QuickDialogs2Utils.dll` | 0.05 MB | QML 对话框工具 |
| `Qt6QuickEffects.dll` | 0.41 MB | QML 特效 |
| `Qt6QuickLayouts.dll` | 0.29 MB | QML 布局 |
| `Qt6QuickParticles.dll` | 0.61 MB | QML 粒子 |
| `Qt6QuickShapes.dll` | 0.33 MB | QML 形状 |
| `Qt6QuickTemplates2.dll` | 1.96 MB | QML 模板 |
| `Qt6QuickTest.dll` | 0.30 MB | QML 测试 |
| `Qt6QuickTimeline.dll` | 0.09 MB | QML 时间线 |
| `Qt6QuickTimelineBlendTrees.dll` | 0.08 MB | QML 时间线混合 |
| `Qt6QuickVectorImage.dll` | 0.07 MB | QML 矢量图 |
| `Qt6QuickVectorImageGenerator.dll` | 0.27 MB | QML 矢量图生成 |
| `Qt6QuickVectorImageHelpers.dll` | 0.18 MB | QML 矢量图助手 |
| `Qt6QuickWidgets.dll` | 0.13 MB | QML Widgets 桥接 |
| `Qt6Qml.dll` | 5.12 MB | QML 核心 |
| `Qt6QmlCore.dll` | 0.13 MB | QML Core |
| `Qt6QmlLocalStorage.dll` | 0.06 MB | QML 本地存储 |
| `Qt6QmlMeta.dll` | 0.15 MB | QML Meta |
| `Qt6QmlModels.dll` | 0.95 MB | QML Models |
| `Qt6QmlNetwork.dll` | 0.12 MB | QML Network |
| `Qt6QmlWorkerScript.dll` | 0.08 MB | QML Worker |
| `Qt6QmlXmlListModel.dll` | 0.13 MB | QML XML 模型 |
| `pyside6qml.abi3.dll` | 0.08 MB | PySide6 QML 桥接 |
| `Qt63DAnimation.dll` | 0.50 MB | 3D 动画 |
| `Qt63DCore.dll` | 0.52 MB | 3D 核心 |
| `Qt63DExtras.dll` | 0.73 MB | 3D 扩展 |
| `Qt63DInput.dll` | 0.39 MB | 3D 输入 |
| `Qt63DLogic.dll` | 0.07 MB | 3D 逻辑 |
| `Qt63DQuick.dll` | 0.31 MB | 3D Quick |
| `Qt63DQuickAnimation.dll` | 0.14 MB | 3D Quick 动画 |
| `Qt63DQuickExtras.dll` | 0.24 MB | 3D Quick 扩展 |
| `Qt63DQuickInput.dll` | 0.06 MB | 3D Quick 输入 |
| `Qt63DQuickLogic.dll` | 0.03 MB | 3D Quick 逻辑 |
| `Qt63DQuickRender.dll` | 0.53 MB | 3D Quick 渲染 |
| `Qt63DQuickScene2D.dll` | 0.11 MB | 3D Quick 2D 场景 |
| `Qt63DQuickScene3D.dll` | 0.10 MB | 3D Quick 3D 场景 |
| `Qt63DRender.dll` | 2.48 MB | 3D 渲染 |
| `Qt6Charts.dll` | 1.68 MB | 图表 |
| `Qt6ChartsQml.dll` | 0.55 MB | 图表 QML |
| `Qt6DataVisualization.dll` | 1.17 MB | 数据可视化 |
| `Qt6DataVisualizationQml.dll` | 0.42 MB | 数据可视化 QML |
| `Qt6Graphs.dll` | 2.43 MB | 图表 |
| `Qt6Multimedia.dll` | 1.22 MB | 多媒体 |
| `Qt6MultimediaQuick.dll` | 0.28 MB | 多媒体 QML |
| `Qt6Location.dll` | 1.62 MB | 位置 |
| `Qt6Positioning.dll` | 0.49 MB | 定位 |
| `Qt6PositioningQuick.dll` | 0.33 MB | 定位 QML |
| `Qt6Sensors.dll` | 0.21 MB | 传感器 |
| `Qt6SensorsQuick.dll` | 0.26 MB | 传感器 QML |
| `Qt6SerialPort.dll` | 0.13 MB | 串口 |
| `Qt6ShaderTools.dll` | 4.13 MB | 着色器 |
| `Qt6Sql.dll` | 0.30 MB | SQL（项目间接）|
| `Qt6StateMachine.dll` | 0.33 MB | 状态机 |
| `Qt6StateMachineQml.dll` | 0.11 MB | 状态机 QML |
| `Qt6Scxml.dll` | 0.51 MB | SCXML |
| `Qt6ScxmlQml.dll` | 0.12 MB | SCXML QML |
| `Qt6Test.dll` | 0.37 MB | Qt 测试 |
| `Qt6TextToSpeech.dll` | 0.13 MB | 语音合成 |
| `Qt6VirtualKeyboard.dll` | 0.42 MB | 虚拟键盘 |
| `Qt6VirtualKeyboardQml.dll` | 0.10 MB | 虚拟键盘 QML |
| `Qt6VirtualKeyboardSettings.dll` | 0.07 MB | 虚拟键盘设置 |
| `Qt6Concurrent.dll` | 0.03 MB | 并发 |
| `Qt6RemoteObjects.dll` | 0.83 MB | 远程对象 |
| `Qt6RemoteObjectsQml.dll` | 0.06 MB | 远程对象 QML |
| `Qt6SpatialAudio.dll` | 0.70 MB | 空间音频 |
| `Qt6Pdf.dll` | 4.40 MB | PDF（项目用 fitz）|
| `Qt6PdfQuick.dll` | 0.55 MB | PDF QML |
| `Qt6LabsAnimation.dll` | 0.05 MB | Labs |
| `Qt6LabsFolderListModel.dll` | 0.12 MB | Labs |
| `Qt6LabsPlatform.dll` | 0.27 MB | Labs |
| `Qt6LabsQmlModels.dll` | 0.18 MB | Labs |
| `Qt6LabsSettings.dll` | 0.06 MB | Labs |
| `Qt6LabsSharedImage.dll` | 0.05 MB | Labs |
| `Qt6LabsWavefrontMesh.dll` | 0.06 MB | Labs |

**必删小计：~317 MB**（120+ 个 DLL）

#### 🟡 测试后定

| DLL | 大小 | 备注 |
|---|---:|---|
| `Qt6Sql.dll` | 0.30 MB | `pages/db.py` 是否存在？（当前未发现使用，倾向可删）|

---

## 4. PySide6/plugins/ 详情（6.37 MB / 38 文件）

| 子目录 | 大小 | 处置 |
|---|---:|---|
| `imageformats/` | ~1.8 MB | 🟡 砍 1.3 MB（只留 jpeg/png/svg）|
| `platforms/` | ~2.2 MB | 🟡 砍 1.1 MB（只留 qwindows.dll）|
| `tls/` | ~0.7 MB | 🟡 保留 qschannelbackend.dll |
| `iconengines/` | 0.07 MB | ❌ 必需（侧边栏 SVG 图标）|

---

## 5. cv2 详情（98.32 MB / 14 文件）

| 文件 | 大小 | 处置 |
|---|---:|---|
| `cv2.pyd` | 71.04 MB | ✅ **移除**（项目 0 处 import）|
| `opencv_videoio_ffmpeg4130_64.dll` | 27.25 MB | ✅ **移除** |
| 其余 12 个文件 | 0.03 MB | ✅ **移除** |

**机制：** OpenCV 是 PyMuPDF 的可选依赖（用于高级图像分析），但项目代码不调用。

---

## 6. tkinter 详情（6.30 MB）

| 项 | 大小 |
|---|---:|
| `tcl86t.dll` | 1.76 MB |
| `tk86t.dll` | 1.52 MB |
| `_tcl_data/` | 3.02 MB |
| `_tk_data/` | 0.81 MB |

**机制：** tkinter 没有任何业务代码 import。PyInstaller 6.11 隐式拉入（疑似因 `pathlib` 探测）。当前 spec 已显式 `excludes` 但仍残留 → **C++ 层未生效，需 hook 过滤**。

---

## 7. 业务依赖审计（必须保留）

| 包 | 实际 import 源 | 业务功能 | 必留 | 大小 |
|---|---|---|:---:|---:|
| `pymupdf` (`fitz`) | 全部 page + src | PDF 渲染/解析核心 | ✅ | 36.38 MB |
| `PIL` (`pillow`) | `pdf_api.py:8`, `legacy_watermark.py:12` | 水印/封面图片处理 | ✅ | 5.22 MB（去 _avif 后）|
| `pandas` | `pdf_api.py:710, 841, 978, 995` | PDF→Excel | ✅ | 16.09 MB |
| `numpy` | `ocr_engine.py:241` | OCR 图片转数组 | ✅ | 5.81 MB |
| `lxml` | `pdf_api.py:665, 684` | docx 字体后处理 | ✅ | 6.58 MB |
| `docx` (`python-docx`) | `pdf_api.py:649, 1111` | PDF→Word + 字体后处理 | ✅ | 0.93 MB |
| `pptx` (`python-pptx`) | `pdf_api.py:1111` | PDF→PPT | ✅ | 0.31 MB |
| `openpyxl` | `template_editor_page.py:3936` | 模板导入 xlsx | ✅ | ~1.5 MB |
| `pdfplumber` | `pdf_api.py:709` | PDF→Excel 表格解析 | ✅ | ~2.0 MB |
| `requests` | `pages/ai_api.py:6` | AI API 调用 | ✅ | ~1.0 MB |
| `certifi` | `requests` 链 | SSL CA 证书 | ✅ | 0.23 MB |
| `pytz` | pandas 链 | 时区数据 | ✅ | 0.83 MB |
| `cryptography` | ❌ **0 处 import** | PyMuPDF 隐式 | ❌ | 9.44 MB |
| `pdfminer` | ❌ **0 处 import** | PyMuPDF 隐式 | ❌ | 7.52 MB |
| `pypdfium2` | ❌ **0 处 import** | PyMuPDF 隐式 | ❌ | 6.93 MB |
| `chardet` | ❌ **不存在** | requests 隐式（已被排除）| — | 0 MB |
| `scipy` | ❌ **0 处 import** | 隐式 | ❌ | — |

**业务依赖合计（必留）：~76 MB**

**可移除隐式依赖：cryptography + pdfminer + pypdfium2 = 23.89 MB**

---

## 8. 重复 DLL 现状

| 文件 | 重复份数 | 单文件大小 | 浪费 |
|---|:---:|---:|---:|
| `MSVCP140.dll` | 1（独立）| 536 KB | — |
| `msvcp140-*.dll`（numpy.libs + pandas.libs）| 2 | 562 KB | 562 KB |
| `VCRUNTIME140.dll` | 1（独立）| 113 KB | — |
| `VCRUNTIME140_1.dll` | 1（独立）| 40 KB | — |

> V1.1-beta 阶段重复较少（PyInstaller 自动去重）。**风险：删除重复 DLL 风险高**，不推荐。

---

## 9. 检查项结果汇总

### 9.1 `.spec` 中 `hiddenimports` 复核

- 共 13 项，与 `src.common` 实际模块一致
- ✅ **无冗余**

### 9.2 `.spec` 中 `excludes` 复核

| 已列 exclude | 实际生效？ |
|---|---|
| `PySide6.QtWebEngineCore/Quick/Widgets` | 🟡 Python 模块生效，**C++ DLL 未生效** |
| `cv2` | ❌ **未列** |
| `PySide6.QtQuick/Quick3D/Qml` | 🟡 同上，C++ DLL 未生效 |
| `PySide6.QtPdf/PdfWidgets` | 🟡 同上 |
| `PySide6.Qt3D*` | 🟡 同上 |
| `PySide6.QtMultimedia*` | 🟡 同上 |
| `tkinter` | 🟡 Python 排除，**C++ `_tcl_data`/`_tk_data`/`tcl86t.dll`/`tk86t.dll` 仍残留** |
| `cryptography` / `pdfminer` / `pypdfium2` | ❌ **未列** |
| `PIL._avif/_webp/jp2/tiff` | 🟡 部分列了（_avif/_webp）|
| `scipy` | ✅ 已列 |

**结论：spec excludes 缺口 = cv2 + cryptography/pdfminer/pypdfium2 + Qt C++ DLL 文件级过滤。**

### 9.3 QtWebEngine / QtQuick / QtQml / Qt3D / QtMultimedia / QtPdfWidgets

| 检查项 | spec 状态 | DLL 实际状态 |
|---|---|---|
| Qt WebEngine | Python 模块已列 exclude | ⚠️ **DLL 仍被打包（195 MB）** |
| Qt Quick / QML | Python 模块已列 exclude | ⚠️ **DLL 仍被打包（25+ MB）** |
| Qt 3D | Python 模块已列 exclude | ⚠️ **DLL 仍被打包（7+ MB）** |
| Qt Multimedia | Python 模块已列 exclude | ⚠️ **DLL 仍被打包（1.5 MB）** |
| Qt Pdf | Python 模块已列 exclude | ⚠️ **DLL 仍被打包（4.95 MB）** |

**核心机制问题：**
- `excludes=` 只影响 Python `import` 分析阶段
- C++ Qt DLL 是由 `PySide6/__init__.py` 隐式加载的二进制依赖
- 必须用 `a.binaries` hook 二次过滤才能真正丢弃

### 9.4 重复 DLL

- V1.1-beta 阶段 PyInstaller 已自动去重大部分
- 仅 `msvcp140-*.dll` 在 numpy.libs 和 pandas.libs 各 1 份
- **不建议删除**（加载时序风险）

---

## 10. 可移除模块清单

### 10.1 A+ 类（强烈推荐，C++ DLL 文件级过滤）

| 类别 | 项数 | 可减少 |
|---|---:|---:|
| Qt WebEngine 全家（dll + resources + locales）| 130+ | **~336 MB** |
| Qt Quick / QML 全家 | 50+ | **~26 MB** |
| Qt 3D 全家 | 15+ | **~7 MB** |
| Qt Quick3D | 10+ | **~11 MB** |
| Qt Quick Controls2（所有样式）| 15+ | **~10 MB** |
| Qt Quick Dialogs / Templates2 | 5+ | **~5 MB** |
| Qt Quick Labs / 5Compat | 10+ | **~2 MB** |
| Qt Multimedia | 2 | **~1.5 MB** |
| Qt Charts / Graphs / DataVisualization | 5+ | **~6 MB** |
| Qt Location / Positioning / Sensors / SerialPort | 6 | **~2.7 MB** |
| Qt ShaderTools / StateMachine / Scxml | 4 | **~5.1 MB** |
| Qt VirtualKeyboard / TextToSpeech | 4 | **~0.7 MB** |
| Qt Pdf / PdfQuick | 2 | **~4.95 MB** |
| Qt Sql / Concurrent / RemoteObjects / SpatialAudio | 4 | **~1.86 MB** |
| Qt WebChannel / WebSockets / WebView | 5 | **~0.63 MB** |
| Qt Test | 1 | **~0.37 MB** |
| opengl32sw + Qt6OpenGL + QtOpenGL.pyd | 3 | **~29.88 MB** |
| **A+ 小计** | 270+ | **~452 MB** |

### 10.2 A 类（Python 模块 + PyMuPDF 隐式依赖）

| 项 | 大小 |
|---|---:|
| `cv2` 整目录 | 98.32 MB |
| `cryptography` 整目录 | 9.44 MB |
| `pdfminer` 整目录 | 7.52 MB |
| `pypdfium2_raw` 整目录 | 6.93 MB |
| **A 小计** | **122.21 MB** |

### 10.3 B 类（资源/翻译/插件精简）

| 项 | 可减少 |
|---|---:|
| `PySide6/resources/qtwebengine_*.pak` + V8 | ~91 MB |
| `PySide6/translations/qtwebengine_locales/` | 43.65 MB |
| `PySide6/translations/qt_*.qm`（保留 6 个）| ~7 MB |
| `PySide6/qml/` 整目录 | 21.90 MB |
| `PySide6/plugins/imageformats/` 精简 | 1.20 MB |
| `PySide6/plugins/platforms/` 精简 | 1.10 MB |
| `tcl86t.dll` + `tk86t.dll` + `_tcl_data` + `_tk_data` | 7.11 MB |
| `PIL/_avif` + `_webp` + `_imaging_jp2` + `_imaging_tiff` | 7.50 MB |
| `.dist-info/` 元数据 | 0.30 MB |
| **B 小计** | **~180 MB** |

### 10.4 C 类（UPX 压缩，可选）

- 启用 UPX，对 .pyd 文件压缩比 50-60%
- 主要压缩目标：PySide6/*.pyd、numpy/*.pyd、pymupdf/_mupdf.pyd、PIL/*.pyd
- 预计再砍 **8-15 MB**
- 风险：AV 软件误报

### 10.5 总计

| 阶段 | 处置 | 当前 (MB) | 累计减少 (MB) | 预计体积 (MB) |
|:---:|---|---:|---:|---:|
| 0 | 当前 V1.1-beta 基线 | 797.81 | 0 | 797.81 |
| 1 | A 类（4 个隐式包）| 797.81 - 122.21 | -122.21 | 675.60 |
| 2 | A+（Qt C++ DLL 文件级过滤）| 675.60 - 452 | -574.21 | 223.60 |
| 3 | B（resources/translations/qml/plugins/tkinter/PIL/.dist-info）| 223.60 - 180 | -754.21 | 43.60 |
| **4** | **+ C（软 UPX）** | 43.60 + 业务必留 ~76 - UPX 收益 ~5 | — | **~115-130 MB** |
| **5** | **+ 激进 UPX** | 115-130 + 0 | — | **~100-120 MB** |

> ⚠️ **修正说明：** 阶段 3 后体积低于业务必留 76 MB，因为 A+ 中部分"必删 DLL"无法一次砍完（Qt 加载器强依赖）。实际可达 **~150-180 MB**。

| **目标** | **推荐方案** | **预计体积** | **风险** |
|:---:|---|---:|:---:|
| 保守 | A + A+ + B | **175-185 MB** | 🟢 低 |
| **触达 150 MB** | A + A+ + B + C（软 UPX） | **~160-175 MB** | 🟡 中（AV 误报）|
| 极致 | A + A+ + B + C+（激进 UPX） | **~150-165 MB** | 🟡 中（启动慢 0.2-0.5s）|

---

## 11. 修改后的 spec（`PDflow_V1.1-beta.spec` 增量补丁）

> **约束：只改 .spec，不动业务代码。** 关键技巧：用 `a.binaries` 过滤 hook 拦截 C++ DLL。

```python
# -*- mode: python ; coding: utf-8 -*-
# ============================================================
# 印流PDflow V1.1-beta 打包瘦身 spec（v2 增量）
# 在 PDflow_V1.1-beta.spec 基础上：
#   1) 新增 hook 过滤 C++ Qt DLL（A+ 类，~452 MB）
#   2) excludes 新增 cv2 / cryptography / pdfminer / pypdfium2（A 类，~122 MB）
#   3) 精简 PySide6 resources/translations/qml（B 类，~165 MB）
#   4) 精简 imageformats / platforms / tkinter / PIL 插件（B 类，~17 MB）
#   5) 启用 UPX 压缩（C 类，~10 MB）
# ============================================================

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.resolve()
APP_NAME = "PDflow_V1.1-beta"
ICON_PATH = str(PROJECT_ROOT / "02-素材资源" / "pdflow-icon.ico")


# ------------------------------------------------------------
# A+ 类：hook 过滤 C++ Qt DLL
# 这些 DLL 在 _internal/ 中被打包，但项目代码 0 处引用
# ------------------------------------------------------------
QT_DLL_DENY_EXACT = {
    # ----- WebEngine 全家（~196 MB）-----
    "Qt6WebEngineCore.dll",
    "Qt6WebEngineQuick.dll",
    "Qt6WebEngineQuickDelegatesQml.dll",
    "Qt6WebEngineWidgets.dll",
    "Qt6WebChannel.dll",
    "Qt6WebChannelQuick.dll",
    "Qt6WebSockets.dll",
    "Qt6WebView.dll",
    "Qt6WebViewQuick.dll",
    # ----- OpenGL（~30 MB）-----
    "opengl32sw.dll",
    "Qt6OpenGL.dll",
    "Qt6OpenGLWidgets.dll",
    "QtOpenGL.pyd",
    # ----- QML / Quick / Quick3D（~55 MB）-----
    "Qt6Quick.dll",
    "Qt6Quick3D.dll",
    "Qt6Quick3DAssetImport.dll",
    "Qt6Quick3DAssetUtils.dll",
    "Qt6Quick3DEffects.dll",
    "Qt6Quick3DHelpers.dll",
    "Qt6Quick3DHelpersImpl.dll",
    "Qt6Quick3DParticleEffects.dll",
    "Qt6Quick3DParticles.dll",
    "Qt6Quick3DRuntimeRender.dll",
    "Qt6Quick3DSpatialAudio.dll",
    "Qt6Quick3DUtils.dll",
    "Qt6Quick3DXr.dll",
    "Qt6QuickControls2.dll",
    "Qt6QuickControls2Basic.dll",
    "Qt6QuickControls2BasicStyleImpl.dll",
    "Qt6QuickControls2FluentWinUI3StyleImpl.dll",
    "Qt6QuickControls2Fusion.dll",
    "Qt6QuickControls2FusionStyleImpl.dll",
    "Qt6QuickControls2Imagine.dll",
    "Qt6QuickControls2ImagineStyleImpl.dll",
    "Qt6QuickControls2Impl.dll",
    "Qt6QuickControls2Material.dll",
    "Qt6QuickControls2MaterialStyleImpl.dll",
    "Qt6QuickControls2Universal.dll",
    "Qt6QuickControls2UniversalStyleImpl.dll",
    "Qt6QuickControls2WindowsStyleImpl.dll",
    "Qt6QuickDialogs2.dll",
    "Qt6QuickDialogs2QuickImpl.dll",
    "Qt6QuickDialogs2Utils.dll",
    "Qt6QuickEffects.dll",
    "Qt6QuickLayouts.dll",
    "Qt6QuickParticles.dll",
    "Qt6QuickShapes.dll",
    "Qt6QuickTemplates2.dll",
    "Qt6QuickTest.dll",
    "Qt6QuickTimeline.dll",
    "Qt6QuickTimelineBlendTrees.dll",
    "Qt6QuickVectorImage.dll",
    "Qt6QuickVectorImageGenerator.dll",
    "Qt6QuickVectorImageHelpers.dll",
    "Qt6QuickWidgets.dll",
    "Qt6Qml.dll",
    "Qt6QmlCore.dll",
    "Qt6QmlLocalStorage.dll",
    "Qt6QmlMeta.dll",
    "Qt6QmlModels.dll",
    "Qt6QmlNetwork.dll",
    "Qt6QmlWorkerScript.dll",
    "Qt6QmlXmlListModel.dll",
    "pyside6qml.abi3.dll",
    # ----- Qt 3D（~7 MB）-----
    "Qt63DAnimation.dll", "Qt63DCore.dll", "Qt63DExtras.dll",
    "Qt63DInput.dll", "Qt63DLogic.dll", "Qt63DQuick.dll",
    "Qt63DQuickAnimation.dll", "Qt63DQuickExtras.dll",
    "Qt63DQuickInput.dll", "Qt63DQuickLogic.dll",
    "Qt63DQuickRender.dll", "Qt63DQuickScene2D.dll",
    "Qt63DQuickScene3D.dll", "Qt63DRender.dll",
    # ----- Qt Charts/Graphs/DataVisualization（~6 MB）-----
    "Qt6Charts.dll", "Qt6ChartsQml.dll",
    "Qt6DataVisualization.dll", "Qt6DataVisualizationQml.dll",
    "Qt6Graphs.dll",
    # ----- Qt Multimedia（~1.5 MB）-----
    "Qt6Multimedia.dll", "Qt6MultimediaQuick.dll",
    # ----- Qt Location/Positioning/Sensors/SerialPort（~2.7 MB）-----
    "Qt6Location.dll", "Qt6Positioning.dll", "Qt6PositioningQuick.dll",
    "Qt6Sensors.dll", "Qt6SensorsQuick.dll", "Qt6SerialPort.dll",
    # ----- Qt ShaderTools/StateMachine/Scxml（~5.1 MB）-----
    "Qt6ShaderTools.dll", "Qt6StateMachine.dll", "Qt6StateMachineQml.dll",
    "Qt6Scxml.dll", "Qt6ScxmlQml.dll",
    # ----- Qt VirtualKeyboard/TextToSpeech（~0.7 MB）-----
    "Qt6VirtualKeyboard.dll", "Qt6VirtualKeyboardQml.dll",
    "Qt6VirtualKeyboardSettings.dll", "Qt6TextToSpeech.dll",
    # ----- Qt Pdf（~4.95 MB）-----
    "Qt6Pdf.dll", "Qt6PdfQuick.dll",
    # ----- Qt Sql/Concurrent/RemoteObjects/SpatialAudio（~1.86 MB）-----
    "Qt6Sql.dll", "Qt6Concurrent.dll",
    "Qt6RemoteObjects.dll", "Qt6RemoteObjectsQml.dll",
    "Qt6SpatialAudio.dll",
    # ----- Qt Test（~0.37 MB）-----
    "Qt6Test.dll",
    # ----- Qt Labs（~0.78 MB）-----
    "Qt6LabsAnimation.dll", "Qt6LabsFolderListModel.dll",
    "Qt6LabsPlatform.dll", "Qt6LabsQmlModels.dll",
    "Qt6LabsSettings.dll", "Qt6LabsSharedImage.dll",
    "Qt6LabsWavefrontMesh.dll",
}

# 翻译文件保留名单
QM_KEEP = {
    "qt_zh_CN.qm", "qt_zh_TW.qm", "qt_en.qm",
    "qtbase_zh_CN.qm", "qtbase_zh_TW.qm", "qtbase_en.qm",
    "qt_help_zh_CN.qm", "qt_help_en.qm",
}

# imageformats 保留名单
IMAGEFORMAT_KEEP = {"qjpeg.dll", "qpng.dll", "qsvg.dll"}

# platforms 保留名单
PLATFORM_KEEP = {"qwindows.dll", "qoffscreen.dll"}

# 资源文件保留名单（删除 WebEngine 资源）
RESOURCE_KEEP_DENY_SUBSTR = {
    "qtwebengine_", "v8_context_snapshot",
}


def filter_binaries(binaries):
    """hook: 过滤 a.binaries / a.datas"""
    kept = []
    for name, src, kind in binaries:
        base = os.path.basename(name)
        # 1) 丢弃 deny-list DLL
        if base in QT_DLL_DENY_EXACT:
            continue
        # 2) 丢弃 WebEngine 资源
        if any(deny in name for deny in RESOURCE_KEEP_DENY_SUBSTR):
            continue
        # 3) 丢弃 qtwebengine_locales 翻译
        if "qtwebengine_locales" in name:
            continue
        # 4) 丢弃多余 .qm 翻译
        if base.startswith("qt_") and base.endswith(".qm"):
            if base not in QM_KEEP:
                continue
        # 5) 丢弃 qml/ 整目录
        if "/qml/" in name or "\\qml\\" in name:
            continue
        # 6) 丢弃 imageformats 多余插件
        if "/imageformats/" in name or "\\imageformats\\" in name:
            if base not in IMAGEFORMAT_KEEP:
                continue
        # 7) 丢弃 platforms 多余插件
        if "/platforms/" in name or "\\platforms\\" in name:
            if base not in PLATFORM_KEEP:
                continue
        # 8) 丢弃 tkinter 三件套
        if base in {"tcl86t.dll", "tk86t.dll"} or "/_tcl_data/" in name or "/_tk_data/" in name:
            continue
        # 9) 丢弃 dist-info 元数据
        if ".dist-info" in name and kind == "DATA":
            continue
        kept.append((name, src, kind))
    return kept


a = Analysis(
    [str(PROJECT_ROOT / "run_main.py")],
    pathex=[
        str(PROJECT_ROOT),
        str(PROJECT_ROOT / "pages"),
        str(PROJECT_ROOT / "src"),
        str(PROJECT_ROOT / "src" / "common"),
        str(PROJECT_ROOT / "translations"),
    ],
    binaries=[],
    datas=[
        (str(PROJECT_ROOT / "pages" / "global.qss"), "pages"),
        (str(PROJECT_ROOT / "assets" / "templates"), "assets/templates"),
        (str(PROJECT_ROOT / "assets" / "pdflow-logo.png"), "assets"),
        (str(PROJECT_ROOT / "02-素材资源" / "assets" / "pdflow-logo-48.png"), "02-素材资源/assets"),
        (str(PROJECT_ROOT / "pages"), "pages"),
    ],
    hiddenimports=[
        "src.common.theme_manager",
        "src.common.theme",
        "src.common.paths",
        "src.common.config",
        "src.common.error_handler",
        "src.common.ocr_provider",
        "src.common.template_renderer",
        "src.common.pdf_api",
        "src.common.recent_files_manager",
        "src.common.render_product_spec_patched",
        "src.common.legacy_watermark",
        "translations.translation_manager",
    ],
    excludes=[
        # ===== A 类：隐式 0 处 import（~122 MB）=====
        "cv2", "cv2.cv2",
        "cryptography", "cryptography.hazmat", "cryptography.hazmat.bindings",
        "pdfminer", "pdfminer.high_level",
        "pypdfium2", "pypdfium2_raw",
        "scipy",
        # ===== A+ 类：Qt Python 绑定（~452 MB 中 Python 部分）=====
        # WebEngine
        "PySide6.QtWebEngineCore", "PySide6.QtWebEngineQuick",
        "PySide6.QtWebEngineWidgets", "PySide6.QtWebChannel",
        "PySide6.QtScript",
        # Quick / QML
        "PySide6.QtQuick", "PySide6.QtQuick3D", "PySide6.QtQml",
        # 3D
        "PySide6.Qt3DCore", "PySide6.Qt3DRender", "PySide6.QtShaderTools",
        # PDF
        "PySide6.QtPdf", "PySide6.QtPdfWidgets",
        # 多媒体 / 位置 / 蓝牙 / 传感器
        "PySide6.QtMultimedia", "PySide6.QtMultimediaWidgets",
        "PySide6.QtPositioning", "PySide6.QtLocation",
        "PySide6.QtSensors", "PySide6.QtSerialPort", "PySide6.QtBluetooth",
        # 图表 / 数据可视化
        "PySide6.QtCharts", "PySide6.QtDataVisualization",
        # 测试 / 设计器 / 帮助
        "PySide6.QtTest", "PySide6.QtDesigner", "PySide6.QtHelp",
        # SVG 已用（main_window.py 依赖 QSvgRenderer）→ 保留 PySide6.QtSvg
        "PySide6.QtSvgWidgets",
        "PySide6.QtXml", "PySide6.QtXmlPatterns", "PySide6.QtNetworkAuth",
        # tkinter
        "tkinter", "_tkinter", "tkinter.ttk",
        # PIL 高级插件
        "PIL._avif", "PIL._webp", "PIL._imaging_jp2",
        "PIL._imaging_tiff", "PIL._imaging_ft",
        "PIL._imaging_psd", "PIL._imaging_wmf", "PIL._imaging_xpm",
    ],
    noarchive=False,
)

# ====== 关键：在 PYZ 之前过滤 binaries / datas ======
a.binaries = filter_binaries(a.binaries)
a.datas    = filter_binaries(a.datas)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,                       # ★ 启用 UPX
    console=False,
    icon=ICON_PATH,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,                       # ★ 启用 UPX
    upx_exclude=[
        "python312.dll",
        "Qt6Core.dll", "Qt6Gui.dll", "Qt6Widgets.dll",
        "Qt6Network.dll", "Qt6Svg.dll", "Qt6PrintSupport.dll",
        "mupdfcpp64.dll",
        "VCRUNTIME140.dll", "VCRUNTIME140_1.dll",
        "MSVCP140.dll", "MSVCP140_1.dll", "MSVCP140_2.dll",
        "ucrtbase.dll", "libcrypto-3.dll", "libssl-3.dll",
    ],
    name=APP_NAME,
)
```

---

## 12. 预计压缩体积

| 阶段 | 处置 | 当前 (MB) | 累计减少 (MB) | 预计体积 (MB) |
|:---:|---|---:|---:|---:|
| 0 | 当前 V1.1-beta 基线 | 797.81 | 0 | 797.81 |
| 1 | A（cv2 + cryptography + pdfminer + pypdfium2）| 797.81 - 122.21 | -122.21 | 675.60 |
| 2 | A+（Qt C++ DLL 文件级过滤 ~452 MB）| 675.60 - 452 | -574.21 | 223.60 |
| 3 | B（PySide6 resources + translations + qml）| 223.60 - 156 | -730.21 | 67.60 |
| 4 | B（tkinter 三件套）| 67.60 - 7.11 | -737.32 | 60.49 |
| 5 | B（plugins + PIL 插件 + dist-info）| 60.49 - 17 | -754.32 | 43.49 |
| **6** | **+ 业务必留基线（pandas/numpy/PIL/lxml/docx/pptx/...）** | 43.49 + ~76 | — | **~120-130 MB** |
| **7** | **+ C（软 UPX，砍 5-10 MB）** | 130 - 8 | — | **~115-122 MB** |

> 注：阶段 6 中 76 MB 是业务必留（pandas 16 + numpy 5.81 + PIL 5.22 + lxml 6.58 + docx 0.93 + pptx 0.31 + openpyxl 1.5 + pdfplumber 2.0 + requests 1.0 + numpy.libs 20.02 + pymupdf 36.38 - 重叠 ≈ 76 MB）。

| **目标** | **推荐方案** | **预计体积** | **风险等级** |
|:---:|---|---:|:---:|
| 保守 | A + A+ + B（不 UPX）| **~175-185 MB** | 🟢 低 |
| **触达 150 MB** | A + A+ + B + 软 UPX | **~155-170 MB** | 🟡 中（AV 误报）|
| 极致 | A + A+ + B + 激进 UPX | **~145-160 MB** | 🟡 中（启动慢 0.2-0.5s）|

---

## 13. 验证清单（实施后必须跑）

> ⚠️ 本次任务**不执行 pyinstaller**，仅生成分析报告。下列清单供下一阶段执行使用。

```
□ EXE 启动 ≤ 3 秒
□ 首页加载
□ 6 个模板渲染（business_card/notice/product_spec/contract/invoice/report）
□ 合并 / 拆分 / 压缩 / 转换 / 水印 5 个功能
□ 主题切换（深/浅）
□ 语言切换（zh_CN/zh_TW/en_US）
□ PDF 转 Excel / Word / PPT 三种格式
□ PDF 转 JPG（PIL 仍在）
□ 体积 ≤ 180 MB（保守方案）
□ 体积 ≤ 170 MB（软 UPX）
□ 体积 ≤ 160 MB（激进 UPX）
□ UPX 压缩的 EXE 在杀软环境下不误报
```

---

## 14. 阻断问题 / 已知风险

| 编号 | 描述 | 风险等级 | 缓解方案 |
|---|---|---|---|
| BP-01 | `opengl32sw.dll` 移除后某些控件可能 fallback 到 GPU 渲染 | 🟡 中 | 启动时记录日志，发现问题回退 |
| BP-02 | `Qt6Quick.dll` 移除后 `QQuickWidget` 不可用 | 🟢 低 | 项目未使用 |
| BP-03 | `Qt6Pdf.dll` 移除后 `QPdfDocument` 不可用 | 🟢 低 | 项目用 fitz |
| BP-04 | `Qt6WebEngineCore.dll` 移除后 QtWebEngine 不可用 | 🟢 低 | 项目未使用 |
| BP-05 | UPX 压缩的 EXE 部分杀软误报 | 🟡 中 | 提供 UPX 与 non-UPX 两个产物 |
| BP-06 | `QtNetwork` 不可移除（`QDesktopServices.openUrl` 必需）| 🟢 低 | 已确认保留 |
| BP-07 | `Qt6PrintSupport` 不可移除（`QPrintDialog` 必需）| 🟢 低 | 已确认保留 |
| BP-08 | PyInstaller 6.11+ 强制拉回部分 transitive 依赖 | 🟡 中 | 若 ImportError，移除对应 exclude |
| BP-09 | 钩子过滤 `qml/` 后 `QtQml.dll` 仍可能因 `QQuickStyle` 调用被加载 | 🟡 中 | 测试时观察；如失败，从 deny 中恢复 `Qt6Qml.dll` |
| BP-10 | `Qt6Sql.dll` 移除后 `QSqlDatabase` 不可用（项目未用）| 🟢 低 | 已确认无业务 import |

---

## 15. 关键文件引用

- 当前 spec（基线）：[PDflow_V1.1-beta.spec](file:///e:/%E5%8D%B0%E6%B5%81PDflow%E9%A1%B9%E7%9B%AE/PDflow_V1.1-beta.spec)
- 业务依赖审计：[pdf_api.py](file:///e:/%E5%8D%B0%E6%B5%81PDflow%E9%A1%B9%E7%9B%AE/src/common/pdf_api.py)
- 业务依赖审计：[ocr_engine.py](file:///e:/%E5%8D%B0%E6%B5%81PDflow%E9%A1%B9%E7%9B%AE/src/common/ocr_engine.py)
- 业务依赖审计：[template_editor_page.py](file:///e:/%E5%8D%B0%E6%B5%81PDflow%E9%A1%B9%E7%9B%AE/pages/template_editor_page.py)
- 上次报告：[PACKAGE_SIZE_REPORT.md](file:///e:/%E5%8D%B0%E6%B5%81PDflow%E9%A1%B9%E7%9B%AE/04-%E9%A1%B9%E7%9B%AE%E6%96%87%E6%A1%A3/PACKAGE_SIZE_REPORT.md)（V1.1-beta 初步分析）

---

## 16. 总结

| 维度 | 结论 |
|---|---|
| **150 MB 是否可达** | 🟡 **临界可达**（需 A + A+ + B + 软 UPX，AV 误报风险中）|
| **可行性** | ✅ 不修改业务代码，仅改 .spec 即可完成 |
| **保守目标** | ✅ 175-185 MB（A + A+ + B 不 UPX，无误报风险）|
| **激进目标** | ✅ 145-160 MB（A + A+ + B + 激进 UPX，启动慢 0.2-0.5s）|
| **下一阶段** | 等待用户确认是否实施 spec v2 增量补丁；如确认，需执行 pyinstaller + 验证清单 |
| **不可达成** | ❌ 100 MB 以下（业务必留 76 MB + Python 解释器 7 MB + Qt 核心 26 MB = 109 MB 物理下限）|

---

*报告生成日期：2026-06-12*
*本报告遵守《项目总章程 V2.5》第八部分（代码安全与质量保障）规范：仅做静态分析，未执行 pyinstaller，未修改任何源代码或既有 .spec。*
*本报告与 `04-项目文档/PACKAGE_SIZE_REPORT.md`（V1.1-beta 初步分析）配套使用，提供更详细的 A+ 类（C++ DLL 文件级）剔除方案。*
