# V1.1 打包减重依赖验证报告

**报告日期：** 2026-06-03
**验证方式：** 一次性排除全部 6 个候选依赖 → 打包 → 功能验证
**打包产物：** `dist/PDflow_V1.1-slim/`
**体积变化：** 799 MB → **224.77 MB**（减少 574 MB，降幅 72%）

---

## 验证方法

1. 创建 `_slim.spec`，在 `excludes` 中加入全部 6 个候选依赖
2. PyInstaller `--onedir` 打包
3. 检查排除是否生效（逐个确认文件不存在）
4. 运行 7 项功能验证：首页 / 设置 / 模板(6个) / PDF导出 / 最近文件 / 主题切换 / 语言切换

---

## 逐个依赖验证结果

### 1. PySide6.QtWebEngineCore

| 项目 | 结果 |
|---|---|
| **是否移除** | ✅ **可移除** |
| 排除项 | `PySide6.QtWebEngineCore`, `QtWebEngineQuick`, `QtWebEngineWidgets`, `QtWebChannel` |
| 减少体积 | ~278 MB（含 Qt6WebEngineCore.dll 195MB + devtools pak 72MB + 其他） |
| 影响功能 | 无。项目不渲染网页，不使用 QWebEngineView |
| 回滚方式 | 从 excludes 列表中移除 `PySide6.QtWebEngine*` 四项 |
| **最终推荐** | ✅ **移除** |

### 2. cv2 (OpenCV)

| 项目 | 结果 |
|---|---|
| **是否移除** | ✅ **可移除** |
| 排除项 | `cv2` |
| 减少体积 | ~98 MB（cv2.pyd 71MB + ffmpeg dll 27MB） |
| 影响功能 | 无。项目代码 0 处 `import cv2`，PyMuPDF 不依赖 cv2 |
| 回滚方式 | 从 excludes 列表中移除 `cv2` |
| **最终推荐** | ✅ **移除** |

### 3. cryptography

| 项目 | 结果 |
|---|---|
| **是否移除** | ✅ **可移除** |
| 排除项 | `cryptography`, `cryptography.hazmat`, `cryptography.hazmat.bindings` |
| 减少体积 | ~9.4 MB |
| 影响功能 | 无。项目代码 0 处 `import cryptography`。PDF 加密/签名功能未实现 |
| 回滚方式 | 从 excludes 列表中移除 `cryptography*` 三项 |
| **最终推荐** | ✅ **移除** |

### 4. pdfminer

| 项目 | 结果 |
|---|---|
| **是否移除** | ✅ **可移除** |
| 排除项 | `pdfminer`, `pdfminer.high_level` |
| 减少体积 | ~7.5 MB |
| 影响功能 | 无。项目代码 0 处 `import pdfminer`，PDF 解析完全由 PyMuPDF (fitz) 处理 |
| 回滚方式 | 从 excludes 列表中移除 `pdfminer*` 两项 |
| **最终推荐** | ✅ **移除** |

### 5. pypdfium2

| 项目 | 结果 |
|---|---|
| **是否移除** | ✅ **可移除** |
| 排除项 | `pypdfium2`, `pypdfium2_raw` |
| 减少体积 | ~6.9 MB |
| 影响功能 | 无。项目代码 0 处 `import pypdfium2`，PDF 渲染由 PyMuPDF 处理 |
| 回滚方式 | 从 excludes 列表中移除 `pypdfium2*` 两项 |
| **最终推荐** | ✅ **移除** |

### 6. PIL._avif (及高级格式插件)

| 项目 | 结果 |
|---|---|
| **是否移除** | ✅ **可移除** |
| 排除项 | `PIL._avif`, `PIL._webp`, `PIL._imaging_jp2`, `PIL._imaging_tiff` |
| 减少体积 | ~7.5 MB（_avif.pyd 7.5MB + 其他） |
| 影响功能 | 无。项目 PDF→图片 仅输出 PNG/JPG，不用 AVIF/WebP/JP2/TIFF 格式 |
| 回滚方式 | 从 excludes 列表中移除 `PIL._avif` 等四项 |
| **最终推荐** | ✅ **移除** |

---

## 功能验证结果

| 功能 | 结果 | 说明 |
|---|---|---|
| 首页 | ✅ 通过 | demo PDF 生成正常 (1470 bytes) |
| 设置 | ✅ 通过 | SettingsPage 加载正常 |
| 模板(6个) | ✅ 通过 | business_card/notice/product_spec/contract/invoice/report 全部渲染成功 |
| PDF导出(merge) | ✅ 通过 | merge_pdfs 正常 (19.5 MB 输出) |
| PDF导出(compress) | ⚠️ 失败 | 字体 `fontno` 兼容问题（**已存在问题**，非依赖排除引起） |
| 最近文件 | ✅ 通过 | add_record / get_recent_files 正常 |
| 主题切换 | ✅ 通过 | dark ↔ light 切换正常 |
| 语言切换 | ✅ 通过 | TranslationManager 加载正常 |

**compress 失败原因：** `Font.__init__() got an unexpected keyword argument 'fontno'` — 这是 `template_renderer.py::_get_cjk_font` 的已存在 PyMuPDF 版本兼容问题，与本次依赖排除无关。

---

## 排除确认

| 文件 | 排除前 | 排除后 |
|---|---|---|
| `Qt6WebEngineCore.dll` | 195 MB | ❌ 不存在（已排除）|
| `cv2.pyd` | 71 MB | ❌ 不存在（已排除）|
| `cryptography/` | 9.4 MB | ❌ 不存在（已排除）|
| `pdfminer/` | 7.5 MB | ❌ 不存在（已排除）|
| `pypdfium2_raw/` | 6.9 MB | ❌ 不存在（已排除）|
| `PIL/_avif*.pyd` | 7.5 MB | ❌ 不存在（已排除）|

---

## 最终推荐

| 依赖 | 是否移除 | 影响功能 | 回滚方式 |
|---|:---:|---|---|
| **PySide6.QtWebEngine*** | ✅ 移除 | 无 | excludes 中移除 4 项 |
| **cv2** | ✅ 移除 | 无 | excludes 中移除 1 项 |
| **cryptography** | ✅ 移除 | 无 | excludes 中移除 3 项 |
| **pdfminer** | ✅ 移除 | 无 | excludes 中移除 2 项 |
| **pypdfium2** | ✅ 移除 | 无 | excludes 中移除 2 项 |
| **PIL._avif 等** | ✅ 移除 | 无 | excludes 中移除 4 项 |

**6/6 候选依赖全部可安全移除。**

---

## 体积对比

| 版本 | 体积 | 说明 |
|---|---:|---|
| V1.1-beta（全量） | 799 MB | 无 exclude |
| **V1.1-slim（6 项排除）** | **224.77 MB** | 本次验证 |
| V1.2 目标（+UPX 压缩） | ~150-180 MB | 预估 |

---

## 打包 spec 推荐

正式打包时使用 `04-项目文档/build_exclude_plan.spec` 中定义的 excludes 列表（已包含本次验证通过的 6 项 + 始终排除的 Qt Quick/QML/Pdf 等），预计体积 **~225 MB**。启用 UPX 后可进一步压缩至 **~150-180 MB**。
