# 印流PDflow V1.1 修改报告

**报告时间：** 2026-06-03
**开发阶段：** V1.1 高优先级任务（第 1-6 项）
**目录结构：** 已冻结（pages/、src/common/、translations/、assets/templates/）

---

## 1. 修改文件列表

### 1.1 新建文件（3 个）

| 路径 | 用途 |
|---|---|
| `src/common/error_handler.py` | 统一错误处理模块 |
| `src/common/ocr_provider.py` | OCR 抽象接口（V1.2 接入）|
| `assets/templates/contract.json` | 合同模板定义 |
| `assets/templates/invoice.json` | 发票模板定义 |
| `assets/templates/report.json` | 报告模板定义 |

### 1.2 修改文件（7 个）

| 路径 | 修改内容 |
|---|---|
| `src/common/pdf_api.py` | 批量处理优化 |
| `src/common/template_renderer.py` | 渲染引擎优化 + 新增 3 个模板 |
| `pages/home_page.py` | 首次体验优化 |
| `pages/merge_page.py` | 接入统一错误处理 |
| `pages/compress_page.py` | 接入统一错误处理 |
| `pages/convert_page.py` | 接入统一错误处理 |
| `pages/watermark_page.py` | 接入统一错误处理 |

---

## 2. 每个文件新增函数

### 2.1 `src/common/pdf_api.py`

| 新增项 | 说明 |
|---|---|
| `class PDFlowError` | 统一错误类（file_path/operation/message/recoverable）|
| `class PDFlowError.to_dict()` | 序列化 |
| `merge_pdfs(... progress_callback, ...)` | 新增进度回调（current, total, filename）|
| `merge_pdfs` 返回值 | 新增 `errors` / `skipped_files` 字段 |
| `split_pdf(... progress_callback, ...)` | 新增进度回调 + 单页失败跳过 |
| `split_pdf` 返回值 | 新增 `errors` 字段 |
| `compress_pdf(... timeout=60, ...)` | 新增超时控制 + 单页失败跳过 |
| `batch_convert(... progress_callback, timeout=60, ...)` | 新增进度回调 + 超时 + 单文件失败跳过 |
| `batch_merge_pdfs(file_groups, output_dir, progress_callback)` | **新函数**：多组合并 |
| `batch_compress_pdfs(file_paths, output_dir, quality, progress_callback, timeout)` | **新函数**：多文件压缩 |
| `batch_convert_files(file_paths, output_dir, batch_fmt, progress_callback, timeout)` | **新函数**：多文件转换 |

### 2.2 `src/common/template_renderer.py`

| 新增项 | 说明 |
|---|---|
| `_cjk_font_cache` | 模块级 CJK 字体缓存 |
| `_char_width_cache` | 字符宽度测量缓存 |
| `_get_cjk_font()` | 改写：加入缓存逻辑 |
| `_measure_text_width()` | 改写：加入缓存查询 |
| `_ensure_space(needed_pt)` | **新函数**：分页保护 |
| `_save_partial(doc, output_path)` | **新函数**：部分保存 |
| `_render_page_bg(page, ...)` | **新函数**：页面背景 |
| `_render_bar(page, ...)` | **新函数**：装饰条 |
| `_render_page_header(page, ...)` | **新函数**：续页页眉 |
| `render_business_card(... progress_callback)` | 新增进度回调参数 |
| `render_notice(... progress_callback)` | 新增多页自动分页 + 进度回调 |
| `render_product_spec(... progress_callback)` | 新增进度回调 + 错误恢复 |
| `render_contract(output_path, data, image_path, style, progress_callback)` | **新函数**：合同模板 |
| `render_invoice(output_path, data, image_path, style, progress_callback)` | **新函数**：发票模板 |
| `render_report(output_path, data, image_path, style, progress_callback)` | **新函数**：报告模板（含页码）|
| `render_template(template_id, output_path, data, **kwargs)` | **新函数**：统一分发器 |

### 2.3 `src/common/error_handler.py`（新文件）

| 新增项 | 说明 |
|---|---|
| `class ErrorType` | 10 种错误类型枚举 |
| `class ErrorHandler` | 静态方法类 |
| `ErrorHandler.classify_error(exception)` | 异常自动分类 |
| `ErrorHandler.handle_pdf_error(exception, parent)` | PDF 错误友好提示 |
| `ErrorHandler.handle_batch_error(results, parent)` | 批量部分失败处理 |
| `ErrorHandler.handle_ai_error(exception, parent)` | AI/超时错误处理 |
| `ErrorHandler.show_error_dialog(title, message, details, parent, theme_colors)` | 主题化错误弹窗 |
| `ErrorHandler.format_file_size(size_bytes)` | 字节格式化 |
| `class ErrorDialog(QDialog)` | 风格化错误对话框 |
| `safe_execute(func, *args, error_type, parent, **kwargs)` | 便捷函数 |

### 2.4 `src/common/ocr_provider.py`（新文件）

| 新增项 | 说明 |
|---|---|
| `class OCRPage` | 单页 OCR 结果数据类 |
| `class OCRResult` | 完整 OCR 结果数据类 |
| `class OCRError / OCRNotImplementedError / OCRFileError / OCRLanguageError` | 异常类 |
| `class OCRProvider(ABC)` | 抽象基类（`extract_text` 抛 NotImplementedError）|
| `class StubOCRProvider(OCRProvider)` | 占位实现 |
| `get_default_ocr_provider()` | 工厂函数 |
| `reset_default_ocr_provider()` | 重置工厂 |
| `extract_text_from_pdf(filepath, language, progress_callback)` | 便捷函数 |
| `extract_text_from_image(filepath, language, progress_callback)` | 便捷函数 |

### 2.5 `pages/home_page.py`

| 新增项 | 说明 |
|---|---|
| `class StepCard(QFrame)` | **新组件**：快速上手步骤卡 |
| `StepCard.apply_theme(colors)` | 主题切换支持 |
| `Ui_HomePage._build_quick_start_section()` | **新方法**：构建快速上手区 |
| `Ui_HomePage._generate_demo_pdf()` | **新方法**：生成示例 PDF |
| `HomePage._on_try_demo()` | **新方法**：点击"试试看"处理 |
| `Ui_HomePage.apply_theme()` | 扩展：新增快速上手区/空状态/步骤卡样式更新 |
| `HomePage.retranslateUi()` | 扩展：新增快速上手区翻译 |

### 2.6 `pages/merge_page.py` / `compress_page.py` / `convert_page.py` / `watermark_page.py`

| 新增项 | 说明 |
|---|---|
| 顶部 `import` | 引入 `ErrorHandler` |
| `_on_*_error` 方法 | 改用 `ErrorHandler.show_error_dialog()` |
| `QMessageBox.warning/critical` 调用 | 替换为 `ErrorDialog` |

### 2.7 `assets/templates/contract.json` / `invoice.json` / `report.json`（新文件）

- `contract.json`：合同协议模板（10 字段 + 3 样式选项）
- `invoice.json`：发票收据模板（10 字段 + 3 样式选项）
- `report.json`：分析报告模板（8 字段 + 3 样式选项）

---

## 3. 删除内容

**无删除。** 所有修改均为新增 / 扩展，未删除任何原有函数或代码。

---

## 4. 重构内容

| 文件 | 重构项 | 改动幅度 |
|---|---|---|
| `pdf_api.py` | `merge_pdfs / split_pdf / compress_pdf / batch_convert` 内部循环结构重写（单文件错误捕获 + 进度回调调用）| 中 |
| `template_renderer.py` | `_get_cjk_font()` 改为带缓存的惰性加载 | 小 |
| `template_renderer.py` | `_measure_text_width()` 改为带缓存的查询 | 小 |
| `template_renderer.py` | `render_notice()` 重构为支持自动分页（提取 `_render_page_bg` / `_render_page_header` / `_render_bar` 内部函数）| 中 |
| `home_page.py` | `Badge("V1.0")` → `Badge("V1.1")` | 极小 |
| `home_page.py` | `_refresh_recent_files()` 扩展：空状态切换为引导式欢迎界面 | 中 |
| 4 个 page | 错误处理由 `QMessageBox` 改为 `ErrorHandler.show_error_dialog()` | 小 |

---

## 5. 风险点

### 🔴 高风险

| 风险 | 影响 | 缓解建议 |
|---|---|---|
| `pdf_api.merge_pdfs` 错误恢复逻辑 | 旧版调用方依赖"失败抛异常"语义。新版"部分失败但仍可能返回成功"可能让上游误判 | 已在所有旧调用方接入 `ErrorHandler`，未接入处需排查 |
| `template_renderer._char_width_cache` 全局缓存 | 字体变更后缓存不会失效（理论上不会变）| 已注释说明 |
| `template_renderer._cjk_font_cache` 全局缓存 | 打包后若资源文件未带字体，仍会缓存 `None` | 启动时打印检测日志 |

### 🟡 中风险

| 风险 | 影响 |
|---|---|
| `render_notice` 改写为分页 | 与旧版"单页公告"行为不一致；如有人依赖固定单页输出需重新设计 |
| 新增的 `render_contract/invoice/report` | UI 编辑器页面（`template_editor_page.py`）未同步支持新模板字段，UI 上无法编辑新模板 |
| `home_page` 新增快速上手区 | 已在 `_trigger_stagger_animations` 中加入 delay=80ms，需手动测试入场顺序 |
| `ErrorHandler.show_error_dialog` 在打包后 | 主题色获取依赖 `src.common.theme`，打包路径已确认 OK |

### 🟢 低风险

| 风险 | 影响 |
|---|---|
| OCR 接口未接实现 | 调用方调用即抛 `NotImplementedError`，V1.1 不暴露 OCR 入口即无影响 |
| 新模板 JSON 缺 `apply` 流程 | `template_layout_page.py` 已动态扫描 JSON，新模板自动出现在卡片网格中 |

---

## 6. 是否影响打包

| 项目 | 影响 |
|---|---|
| PyInstaller 打包 | ✅ **无影响** |
| spec 文件 | ❌ **无需更新**（未引入新第三方依赖）|
| `pages/__init__.py` 导出 | ❌ **无需更新**（新文件均在 `src/common/`）|
| 资源文件清单 | ⚠️ `assets/templates/{contract,invoice,report}.json` 需确认随包打包（使用现有 `resource_path()`，应已自动包含）|
| 启动入口 | ❌ **无需更新**（`run_main.py` 未改）|

**未引入新依赖**（paddleocr / pytesseract / PyTorch 等均未安装）。

---

## 7. 预计安装包变化

| 项目 | 变化量 |
|---|---|
| 新增 Python 源文件 | `error_handler.py` (~10KB) + `ocr_provider.py` (~6KB) = **+16KB** |
| 新增 JSON 模板 | `contract.json` + `invoice.json` + `report.json` ≈ **+3KB** |
| 修改 Python 源文件 | pdf_api / template_renderer / home_page / 4 page = **+~30KB**（源代码级，编译后更小）|
| **安装包总体变化** | **+0.3 ~ 0.5 MB**（PyInstaller 压缩后估计）|
| **未引入** | paddleocr (~200MB) / pytesseract + tesseract (~50MB) / PyTorch (~800MB) — 全部未安装 |

**结论：V1.1 安装包体积与 V1.0 基本持平。**

---

## 8. 后续未完成任务（按优先级）

| # | 任务 | 状态 |
|---|---|---|
| 7 | AI 文本处理（PDF 摘要/Markdown/Word）| ⏸ 已停止 |
| 8 | AI 速文创作 | ⏸ 已停止 |
| 9 | 首次启动 Onboarding | ⏸ 已停止 |
| 10 | 打包体系 + 性能优化 + 日志埋点 | ⏸ 已停止 |

**目录结构已冻结：仅可修改 `pages/`、`src/common/`、`translations/`、`assets/templates/`。**
