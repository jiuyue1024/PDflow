# 印流PDflow - Code Wiki 文档

> **项目版本**: V1.1-RC2（v1.1-patch 分支）
> **技术栈**: PySide6 (Qt 6.11+) + Python 3.12+ + PyMuPDF + Pillow + pdfplumber
> **最后更新**: 2026-06-14
> **文档用途**: 项目架构说明、模块职责、API参考、开发指南
> **配套文档**: `印流PDflow_项目总章程_V2.5.md`、`DESIGN.md`、`CODE_REVIEW.md`

---

## 目录

1. [项目概述](#1-项目概述)
2. [整体架构](#2-整体架构)
3. [目录结构](#3-目录结构)
4. [核心模块详解](#4-核心模块详解)
5. [页面模块详解](#5-页面模块详解)
6. [关键类与函数 API](#6-关键类与函数-api)
7. [依赖关系图](#7-依赖关系图)
8. [项目运行方式](#8-项目运行方式)
9. [v1.1-patch 关键修复](#9-v11-patch-关键修复)
10. [开发规范与红线](#10-开发规范与红线)
11. [附录](#11-附录)

---

## 1. 项目概述

### 1.1 产品定位

**印流PDflow** 是一款专为设计师打造的 PDF 版式设计工具，提供：

- **PDF 工具箱**: 合并拆分、压缩优化、格式转换、水印处理
- **模板排版**: JSON 模板定义 + 表单输入 + 实时预览 + 矢量 PDF 生成
- **速文创作**: AI 驱动的文案创作（开发者模式开关，受 `developer_mode` 配置控制）

### 1.2 技术特点

| 特性 | 说明 |
|------|------|
| 跨平台 | Windows / macOS / Linux（基于 Qt 框架） |
| 双主题 | 深色 / 浅色，实时切换，统一通过 `ThemeManager` 管控 |
| 三语 i18n | 简体中文 / 繁体中文 / 英文（`TranslationManager`） |
| 无边框窗口 | 自定义标题栏 + QPainter 自绘窗控按钮 |
| 模板系统 | JSON 驱动，可扩展的模板引擎（`assets/templates/*.json`） |
| 矢量 PDF | PDF AxialShading 渐变，禁止 PNG 嵌入背景 |
| 桌面环境 | 统一托盘、关闭到托盘、自定义拖拽 |
| 性能 | 预览倍率 `PREVIEW_SCALE=2.0` 统一，4K 屏像素上限 2200px |

### 1.3 技术栈

| 层级 | 技术 | 版本 |
|------|------|------|
| GUI 框架 | PySide6 | 6.11+ |
| 语言 | Python | 3.12+ |
| PDF 处理核心 | PyMuPDF (fitz) | 1.27+ |
| 图像处理 | Pillow | 12.2+ |
| 表格提取 | pdfplumber | 0.11.9+ |
| PDF → Word | pdf2docx | 0.5.13+ |
| Excel 读写 | openpyxl + pandas | 3.1.5+ / 2.3.3+ |
| PPT 生成 | python-pptx | 1.0.2+ |
| 安全工具 | bandit / pip-audit / slopscan | — |

---

## 2. 整体架构

### 2.1 架构分层

```
┌──────────────────────────────────────────────────────────────────────┐
│                        表现层 (UI Layer)                              │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────────────┐ │
│  │ 首页         │ │ 工具箱 4 个  │ │ 模板排版（入口 + 编辑器）    │ │
│  │ HomePage     │ │ MergePage    │ │ TemplateLayoutPage           │ │
│  │              │ │ CompressPage │ │ TemplateEditorPage           │ │
│  │              │ │ ConvertPage  │ │ SpeedwritePage（开发者模式） │ │
│  │              │ │ WatermarkPage│ │                              │ │
│  └──────────────┘ └──────────────┘ └──────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────┤
│                      应用框架层 (Framework)                          │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────┐ │
│  │ MainWindow   │ │ThemeManager  │ │Translation   │ │ Preview    │ │
│  │ (run_main)   │ │ (单例 QObject)│ │ Manager     │ │ Renderer   │ │
│  └──────────────┘ └──────────────┘ └──────────────┘ └────────────┘ │
├──────────────────────────────────────────────────────────────────────┤
│                      业务逻辑层 (Business)                           │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────┐ │
│  │ pdf_api.py   │ │template_     │ │ pdf_table_ir │ │ pdf_layout │ │
│  │  PDF 操作    │ │ renderer.py  │ │ (Table IR)   │ │ _parser    │ │
│  │              │ │  模板渲染     │ │ Excel 中间层 │ │ (Layout重建)│ │
│  └──────────────┘ └──────────────┘ └──────────────┘ └────────────┘ │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                 │
│  │ export/      │ │ text_layout  │ │ recent_files │                 │
│  │ pdf_exporter │ │  文本排版     │ │  最近文件    │                 │
│  │  矢量 PDF    │ │              │ │              │                 │
│  └──────────────┘ └──────────────┘ └──────────────┘                 │
├──────────────────────────────────────────────────────────────────────┤
│                       基础设施层 (Infra)                             │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                  │
│  │ paths.py     │ │ theme.py     │ │ theme_tokens │                  │
│  │ 路径管理     │ │  配色定义     │ │  主题 token   │                  │
│  └──────────────┘ └──────────────┘ └──────────────┘                  │
└──────────────────────────────────────────────────────────────────────┘
```

### 2.2 核心数据流

```
用户操作 → 页面组件 (pages/*.py)
                ↓
         业务逻辑 (src/common/*.py)
                ↓
    ┌───────────┼───────────┐
    ↓           ↓           ↓
 PDF API    模板渲染    IR/Layout
 (fitz)    (fitz+export) (pdfplumber+fitz)
    ↓           ↓           ↓
  PDF 文件  PDF 矢量文件   Excel/JSON 输出
                ↓
         ThemeManager (主题同步)
                ↓
         TranslationManager (语言同步)
```

### 2.3 核心设计模式

- **单例模式**: `ThemeManager` 使用 `__new__` 单例，确保全局唯一
- **工厂模式**: `run_main.setup_navigation()` 通过 `NAV_ITEMS` 工厂映射创建页面
- **观察者模式**: `ThemeManager.theme_changed` Signal 通知所有注册页面更新内联样式
- **MVC 模式**: 页面采用 `Ui_XXXPage` (View) + `XxxPage` (Controller) 分离
- **IR 中间表示**: `TableBlock` (dataclass) + `to_table_block()` 字典双形式流转
- **三段渲染**: 预览（QPixmap）↔ 同一 CanvasModel ↔ 导出（PDF AxialShading）

---

## 3. 目录结构

```
印流PDflow项目/
│
├── run_main.py                    # ★ 应用入口（PySide6 主窗口）
│
├── pages/                         # ★ UI 页面模块
│   ├── __init__.py
│   ├── main_window.py             # Ui_MainWindow（Qt Designer 生成）
│   ├── main_window.ui             # 主窗口 .ui 文件
│   ├── main_window_uic.py         # .ui 编译产物
│   ├── global.qss                 # 全局 QSS（动态主题）
│   ├── global.qss.template        # QSS 模板（含 {{TOKEN}} 占位符）
│   ├── dark.qss                   # 预渲染深色 QSS
│   ├── light.qss                  # 预渲染浅色 QSS
│   ├── home_page.py               # 首页
│   ├── merge_page.py / .ui        # 合并拆分
│   ├── compress_page.py / .ui     # 压缩
│   ├── convert_page.py / .ui      # 格式转换
│   ├── watermark_page.py / .ui    # 水印
│   ├── template_layout_page.py    # 模板排版入口（卡片网格）
│   ├── template_editor_page.py    # 模板编辑器（表单 + 预览）
│   ├── speedwrite_page.py / .ui   # 速文创作（开发者模式）
│   ├── settings_page.py / .ui     # 设置
│   ├── settings_page_ui.py        # 设置页 UI 编译产物
│   ├── ai_api.py / ai_dialogs.py  # AI 接口（占位）
│   └── pdf_to_img.py              # PDF 转图片工具
│
├── src/                           # ★ 核心源码
│   ├── __init__.py
│   ├── tk_file_picker.py          # 文件选择工具
│   └── common/                    # 公共模块
│       ├── __init__.py
│       ├── pdf_api.py             # ★ PDF 后端 API（合并/拆分/压缩/转换/水印）
│       ├── template_renderer.py   # ★ 模板渲染引擎（business_card/notice/...）
│       ├── text_layout.py         # ★ 统一文本排版（draw_wrapped_text）
│       ├── preview_renderer.py    # 统一预览（PREVIEW_SCALE=2.0）
│       ├── pdf_table_ir.py        # ★ v1.1-patch PDF→Excel 中间结构
│       ├── pdf_layout_parser.py   # ★ v1.1-patch 布局行重建
│       ├── theme.py               # 主题配色（DARK_COLORS / LIGHT_COLORS）
│       ├── theme_manager.py       # 主题管理器（单例 QObject）
│       ├── theme_tokens.py        # 主题 token 全局单例
│       ├── config.py              # 配置管理
│       ├── paths.py               # 路径管理（开发/打包/数据）
│       ├── recent_files_manager.py# 最近文件
│       ├── ocr_engine.py          # OCR 引擎
│       ├── ocr_provider.py        # OCR provider 抽象
│       ├── ai_text_processor.py   # AI 文本处理
│       ├── legacy_watermark.py    # 水印后端（沿用 v1）
│       ├── watermark_preview.py   # 水印实时预览（缓存底图 + 重画水印）
│       ├── error_handler.py       # 统一错误处理
│       └── render_product_spec_patched.py  # 产品规格模板补丁
│
├── export/                        # ★ PDF 矢量导出模块（Route B）
│   ├── __init__.py                # 导出 draw_linear_gradient 等
│   └── pdf_exporter.py            # PDF AxialShading 注入 + QR 矢量 + 图标矢量
│
├── translations/                  # 国际化
│   ├── __init__.py
│   ├── translation_manager.py     # 翻译管理器
│   ├── translations.py            # 翻译字典
│   └── translations_en_US.ts      # 英文翻译资源
│
├── assets/                        # 资源文件
│   ├── templates/                 # JSON 模板
│   │   ├── presets/              # 预设变体
│   │   │   ├── business_card.json
│   │   │   ├── notice.json
│   │   │   └── product_spec.json
│   │   ├── business_card.json     # 名片（V4.0）
│   │   ├── contract.json          # 合同（V1.0）
│   │   ├── invoice.json           # 发票
│   │   ├── notice.json            # 公告（V2.0）
│   │   ├── product_spec.json      # 产品规格（V2.0）
│   │   └── report.json            # 分析报告（V1.0）
│   ├── icons/                     # SVG 图标（nav-*.svg）
│   ├── tools/                     # 启动脚本（set-env / remove-env）
│   ├── pdflow-logo.ico            # 任务栏图标
│   └── pdflow-logo.png            # 主 LOGO
│
├── build/                         # 打包与测试
│   ├── *.spec                     # PyInstaller 打包配置
│   ├── make_sfx.py / make_7z.py   # SFX / 7z 打包脚本
│   ├── sfx_config.txt             # SFX 配置
│   ├── test_p0_hotfix.py          # v1.1-patch P0 单元测试
│   ├── test_p0_e2e.py             # 端到端测试
│   ├── test_layout_parser.py      # 布局解析单测
│   ├── test_export_vector_test.py # 矢量导出测试
│   └── test_gui_*.py              # GUI 路径测试
│
├── tests/                         # 端到端 + 视觉测试
│   ├── export_vector_test.py      # 矢量导出对比
│   ├── test_contract_preview.py
│   ├── test_report_preview.py
│   └── test_style_system.py
│
├── scripts/                       # 工具脚本
│   ├── check_remaining_hardcoded.py
│   ├── fix_all_fstring.py
│   ├── replace_hardcoded_colors.py
│   └── verify_theme_state.py
│
├── 02-素材资源/                   # LOGO / 品牌素材
├── 04-项目文档/                   # 项目文档
│   ├── 印流PDflow_项目总章程_V2.5.md   # ★ 最高约束
│   ├── DESIGN.md                  # UI 设计规范
│   ├── CODE_REVIEW.md             # Code Review 规范
│   ├── PM_SOUL.md                 # PM Agent 行为准则
│   ├── CODE_WIKI.md               # ← 本文件
│   ├── KNOWN_ISSUES.md            # 已知问题
│   ├── CHANGELOG.md               # 变更日志
│   ├── RELEASE_NOTES.md           # 发布说明
│   └── *.md                       # 各专题报告
├── 07-计划书&上架资料/             # 上架资料
│   └── 软件截图/                  # ★ ≥5 张核心功能截图
│
├── pyside6_env/                   # Python 虚拟环境
├── _旧版归档/                     # ★ 历史框架（不可修改、不参与运行时）
│
├── requirements.txt               # Python 依赖清单（含安全工具）
├── PDflow_V1.1-RC2.spec           # PyInstaller 打包配置（主）
├── PDflow_V1.1-RC2.webengine.spec # WebEngine 打包变体
├── config.json                    # 应用配置
├── start.bat / start.ps1          # 启动脚本
├── start_debug.bat / start_debug.ps1  # 调试启动
└── 印流PDflow项目.rar              # 备份归档
```

---

## 4. 核心模块详解

### 4.1 入口模块 (run_main.py)

**职责**:
- 创建 QApplication + 无边框主窗口
- 加载 `Ui_MainWindow`、注入自定义标题栏
- 初始化 `ThemeManager` + `TranslationManager`
- 配置 8 个页面导航 + 信号连接
- 启动系统托盘（关闭按钮默认隐藏到托盘）

**核心流程**:

```python
def main():
    1. 创建 i18n 管理器 TranslationManager
    2. 读取 config.json 中的 language / developer_mode
    3. 创建 QApplication + 设置应用图标（.ico 优先）
    4. 初始化 ThemeManager（单例）
    5. 创建无边框 QMainWindow + 自定义 TitleBarBtn
    6. 加载 Ui_MainWindow.setupUi(window)
    7. 嵌入 centralWidget（保留标题栏）
    8. theme_mgr.apply_theme(saved_theme, app)
    9. _apply_main_window_theme(...) 更新内联样式
    10. setup_navigation(ui)           # 8 个页面
    11. _connect_template_signals(ui)  # TPL-02 模板信号
    12. _connect_settings_signals(ui)  # 开发者模式 + 语言
    13. 注册所有页面到 theme_mgr
    14. 启动系统托盘
    15. window.show(); app.exec()
```

**导航配置**:
```python
NAV_ITEMS = [
    ("btnHome",           "首页",         HomePage),
    ("btnMerge",          "合并拆分",     MergePage),
    ("btnCompress",       "压缩",         CompressPage),
    ("btnConvert",        "格式转换",     ConvertPage),
    ("btnWatermark",      "水印",         WatermarkPage),
    ("btnSpeedwrite",     "速文创作",     None),   # 开发者模式控制
    ("btnTemplateLayout", "模板排版",     TemplateLayoutPage),
    ("btnSettings",       "设置",         SettingsPage),
]
```

**关键类**:
- `TitleBarBtn(QPushButton)`: 自定义绘制标题栏按钮（min / max / close），用 QPainter 画几何图形

**关键函数**:
- `setup_navigation(ui)`: 绑定 8 个导航按钮与 QStackedLayout
- `_apply_main_window_theme(ui, colors, ...)`: 主题切换时更新内联样式
- `_connect_template_signals(ui, theme_mgr)`: TPL-02 懒加载编辑器信号
- `_connect_settings_signals(ui, pages_stack, i18n)`: 开发者模式 + 语言
- `_show_about_dialog()`: 关于弹窗（LOGO + 版本 + 技术栈 chip）

---

### 4.2 主题系统

#### 4.2.1 主题配色 (src/common/theme.py)

定义两组 `dict` 配色变量：`DARK_COLORS` / `LIGHT_COLORS`，token 一一对应，共 ~100 个 key。

**核心 Token 分类**:

| 分类 | 示例 token |
|------|------|
| 背景层 | `bg`、`nav_bg`、`card_bg`、`input_bg`、`hover_bg`、`title_bar_bg`、`menu_bg`、`tooltip_bg` |
| 按钮态 | `bg_normal/hover/pressed/selected/focus/disabled` + `text_*` + `border_*` |
| 边框/分割 | `border`、`border_light`、`border_hover`、`separator` |
| 文字 | `text_main`、`text_sub`、`text_muted`、`text_meta`、`placeholder_text` |
| 主题/语义 | `primary`（#4D7CFE）、`primary_hover`、`success`（#34C759）、`warning`（#FF9500）、`error`（#FF3B30） |
| 侧边栏 | `sidebar_icon`、`sidebar_icon_active`、`sidebar_text`、`sidebar_text_active`、`nav_hover`、`nav_checked_bg` |
| 透明色（QSS） | `nav_checked_bg_qss`、`white_8_qss`、`white_13_qss`、`func_card_bg_qss` |
| 组件 | `scrollbar_bg`、`progress_bg`、`badge_bg`、`card_border_hover` |
| 阴影 | `shadow_sm`、`shadow_md` |

**核心函数**:
```python
get_colors(theme=None) -> dict        # 获取配色字典
get_current_theme() -> str            # "dark" | "light"
set_theme(theme: str) -> None         # 持久化到 app_config.json
```

**持久化文件**: `<项目根>/src/common/app_config.json`（即 `data_path` 或 `__file__` 同级）

#### 4.2.2 主题管理器 (src/common/theme_manager.py)

**类**: `ThemeManager(QObject)` — **单例**（`__new__` 拦截）

**核心方法**:

```python
def apply_theme(self, theme: str = None, app=None) -> None
    """
    完整主题切换流程：
      1. 同步 theme_tokens 全局单例
      2. 加载预渲染 dark.qss / light.qss（或模板渲染回退）
      3. 设置 QApplication 全局 QPalette
      4. qapp.setStyleSheet(qss)
      5. _refresh_dynamic_widgets()  → 通知所有注册页面 apply_theme(colors)
      6. _full_repaint()             → unpolish → polish → 递归 repaint
      7. set_theme(theme)            → 持久化
      8. theme_changed.emit(theme)   → 触发 _apply_main_window_theme
    """

def register_page(self, widget) -> None
    # widget 需实现 apply_theme(colors) 方法，重复注册自动去重

def get_qss(self, theme: str = None) -> str
    # 优先加载 pages/{theme}.qss（预渲染），回退到模板渲染

def toggle(self, app=None) -> None  # 切换 dark/light
```

**信号**:
```python
theme_changed = Signal(str)  # 参数: "dark" | "light"
```

#### 4.2.3 主题 Token (src/common/theme_tokens.py)

为页面提供 `get_token("bg")` 风格的间接访问，避免页面直接 `import theme`。`theme_tokens.set_theme()` 会在 `ThemeManager.apply_theme` 内自动同步。

---

### 4.3 PDF API 模块 (src/common/pdf_api.py)

**职责**: 封装所有 PDF 后端操作，对接 PyMuPDF + pdfplumber + pdf2docx + openpyxl + python-pptx。

#### 4.3.1 核心函数清单

| 类别 | 函数 | 说明 |
|------|------|------|
| **路径** | `get_output_path(input, suffix, output_dir)` | 生成输出路径 |
| | `_resolve_output_path(output, input, default_ext)` | v1.1-patch：兼容目录型入参 |
| **信息** | `get_pdf_info(path)` | `{pages, size_mb, title}` |
| **合并** | `merge_pdfs(output, *paths, progress_callback)` | 合并多 PDF |
| **拆分** | `split_pdf(path, out_dir, mode, range_str)` | 按页 / 范围拆分 |
| **页面** | `reorder_pdf_pages(input, page_order, output)` | 重排序 |
| **压缩** | `compress_pdf(input, quality, output, progress, timeout)` | quality ∈ {high, medium, low} |
| **转换** | `pdf_to_images(input, out_dir, dpi, fmt)` | PDF→PNG/JPG |
| | `images_to_pdf(paths, output, orient, quality)` | 图片→PDF |
| | `pdf_to_word(input, output)` | PDF→DOCX（pdf2docx） |
| | `pdf_to_excel(input, output)` | **PDF→XLSX**（走 IR 层） |
| | `pdf_to_ppt(input, out_dir)` | PDF→PPTX |
| **水印** | `add_watermark(input, wm_text, output, ...)` | 文字水印 |
| **OCR** | `ocr_extract_text(input, progress)` | OCR 文字提取 |
| **批量** | `batch_convert / batch_merge / batch_compress` | 批处理 |
| **错误** | `PDFlowError` dataclass | 错误信息载体 |

#### 4.3.2 关键函数签名

```python
def merge_pdfs(output_path: str, *filepaths, progress_callback=None) -> dict

def compress_pdf(
    input_path: str, quality: str = "high",
    output_path: str = None, progress_callback=None, timeout: int = 60,
) -> dict
# high  → 200DPI JPEG Q90（适合打印，减轻 60-85%）
# medium→ 150DPI JPEG Q75（适合阅读，减轻 70-90%）
# low   →  72DPI JPEG Q50（极限压缩，减轻 90-97%）

def add_watermark(
    input_path: str, wm_text: str, output_path: str = None,
    font_size: int = 60, opacity: float = 0.15,
    rotation: int = -45, color: tuple = (128, 128, 128),
    position: str = "center",  # center | tile
) -> dict
```

#### 4.3.3 PDF→Excel 数据流（v1.1-patch）

```
pdfplumber.extract_tables() 或 extract_words()
    ↓
pdf_table_ir.to_table_block(rows, page, table_id, mode)
    ↓ (IR dict: {rows, spans, meta})
pdf_table_ir.normalize_excel_input(ir)  → DataFrame
    ↓
openpyxl 写入
```

**统一输出协议（修复 v1.1 的 `DataFrame has no attribute 'tolist'` 崩溃）**:
- 禁止调用 `df.tolist()` / `df.values.tolist()`
- 统一改用 `df.to_dict('records')`
- IR dict 结构：`{"rows": List[List[str]], "spans": None, "meta": {page, table_id, confidence, mode}}`

---

### 4.4 PDF→Excel 中间结构 (src/common/pdf_table_ir.py)  ★v1.1-patch 新增

**职责**: 在 pdfplumber 与 openpyxl 之间建立规范化中间表示（IR），保留 `\n` 换行，屏蔽 DataFrame / list / dict 异构输入。

#### 4.4.1 数据结构

```python
@dataclass
class TableMeta:
    page: int = 0
    table_id: int = 0
    confidence: float = 1.0
    mode: str = "structured"  # structured / text_fallback / ocr_fallback

@dataclass
class TableBlock:
    rows: List[List[str]]
    spans: Optional[Any] = None
    meta: Optional[TableMeta] = None
    # 挂载方法：to_dict() / to_dataframe()
```

#### 4.4.2 核心函数

```python
clean_cell(text) -> str                      # 清洗单格（保留 \n）
normalize_table(rows) -> List[List[str]]     # 整表清洗
to_table_block(rows, page, table_id, ...) -> Dict   # 构造 IR dict
ir_to_rows(ir) -> List[List[str]]            # 从 IR 抽 rows
ir_meta(ir) -> Optional[TableMeta]           # 从 IR 抽 meta
has_newline_cells(rows) -> bool              # 是否含 \n（决定 wrap_text）
to_dataframe(ir_or_rows) -> pd.DataFrame     # 统一入口（支持 4 种入参）
normalize_excel_input(result) -> DataFrame  # 统一输出协议（强制 DataFrame）
fallback_block(rows, ...) -> Dict            # 统一 fallback 返回 IR dict
```

**入参类型支持**:
1. `TableBlock` dataclass
2. `dict` IR（`{"rows": ..., "meta": ...}`）
3. 裸 `List[List[str]]`
4. `pandas.DataFrame`（透传）

---

### 4.5 PDF Layout Parser (src/common/pdf_layout_parser.py)  ★v1.1-patch 新增

**职责**: 修复 v1.1 中"PDF 内容被压扁到 A 列"的问题，从坐标层面重建二维行结构。

#### 4.5.1 核心流程

```
page.extract_words(x_tolerance=3, y_tolerance=3)
    ↓ 按 y 降序排序（同 y 按 x 升序）
cluster_by_y(words, threshold=3.0)
    ↓ 行内按 x 升序拼接 + 语义拆分
_split_by_special_tokens(text)  # phone/email/url 独立成行
    ↓
List[List[str]]  # 二维 rows
```

#### 4.5.2 核心函数

```python
# 语义正则
PHONE_PATTERN   = r'\+?\d[\d\-\s]{6,}\d'           # 电话
EMAIL_PATTERN   = r'[a-zA-Z0-9._%+\-]+@[\w.\-]+\.\w{2,}'  # 邮箱
URL_PATTERN     = r'(?:https?://|www\.)[^\s]+'      # URL

# 访问工具
_w_get(w, key, default) -> Any  # 兼容 dict / object / 索引 三种 word 风格

# 聚类
cluster_by_y(blocks, threshold=3.0) -> List[List[Any]]

# 拆分
_is_special_token(text) -> bool
_split_by_special_tokens(text) -> List[str]  # "张三 13812345678 z@a.com" → ["张三", "13812345678", "z@a.com"]

# 主入口
parse_layout_blocks(page) -> List[List[str]]     # P0 Hotfix 主入口
parse_layout_rows(page) -> List[Dict[str, Any]]  # 兼容旧 _extract_page_words API
```

**禁止使用**:
- ❌ `page.extract_text()` （丢失坐标）
- ❌ `text.split("\n")` （破坏阅读顺序）

---

### 4.6 模板渲染引擎 (src/common/template_renderer.py)

**职责**: 模板 → PDF 矢量输出，对接 `export/pdf_exporter.py` 完成 Route B 矢量绘制。

#### 4.6.1 模板入口

```python
def render_template(template_id: str, output_path: str, data: dict, **kwargs) -> str
```

#### 4.6.2 各模板渲染函数

| 模板 | 函数 | 尺寸 | 特性 |
|------|------|------|------|
| 名片 (business_card) | `render_business_card()` | 90×54mm | 正反面 / LOGO / QR / 渐变背景 |
| 公告 (notice) | `render_notice()` | A4 | 多字体风格 / 装饰条 / 多背景 |
| 产品规格 (product_spec) | `render_product_spec()` | A4 | 表格数据 / 标题栏样式 |
| 合同 (contract) | `render_contract()` | A4 | 甲乙方 / 条款 / 签章 |
| 发票 (invoice) | `render_invoice()` | A4 | 表格明细 / 边框 |
| 分析报告 (report) | `render_report()` | A4 | 目录 / 章节 / 图表占位 |

#### 4.6.3 名片渲染参数

```python
def render_business_card(
    output_path: str, data: dict,
    logo_path: str = None, photo_path: str = None, qr_image_path: str = None,
    style_options: dict = None,
    bg_image_path: str = None, bg_image_opacity: float = 50,
    bg_texture: str = "none", bg_custom_color: str = "",
    text_color: str = "#2C3E50", text_secondary_color: str = "#7F8C8D",
    render_sides: list = None,    # ["front"] | ["front", "back"]
    progress_callback=None,
) -> str
```

#### 4.6.4 关键约束（来自 project_memory）

- **尺寸**: ISO/IEC 7810 ID-1 标准（85.6×53.98mm / 242.6×153.0pt）
- **字号**: name ≤ min(card_h*0.12, 16pt)，title 10px，contact 9px（固定上限）
- **LOGO**: 保持原始宽高比，PIL.Image 渲染防变形
- **背景**: 渐变使用 PDF AxialShading（禁止 PNG 位图）
- **缺失资源**: 显示虚线占位框 + "LOGO"/"QR" 文字

#### 4.6.5 辅助函数集

```python
# 单位转换
_mm_to_points(mm) -> float
_points_to_mm(pt) -> float

# 颜色
_hex_to_rgb(hex) -> tuple
_hex_to_brightness(hex) -> float

# 文字
_insert_text_safe(page, text, x, y, fontsize, color, fontname, regular)
_insert_text_centered(page, text, center_x, y, fontsize, width, color)
_insert_text_centered_with_prefix(...)    # 居中带前缀（图标 + 文本）
_measure_text_width(text, fontsize) -> float
_wrap_text_in_width(text, fontsize, max_width_pt) -> list
_truncate_to_width(text, max_width_pt, fontsize) -> str

# 图片
_safe_insert_image(page, file_path, rect) -> bool  # 健壮：先尝试直接插入，失败时 PIL 转码

# 字体
_get_cjk_font() -> fitz.Font
_get_cjk_font_regular() -> fitz.Font
```

#### 4.6.6 模块级缓存

- `_cjk_font_cache`: CJK 字体（避免重复扫描）
- `_char_width_cache`: 字符宽度（避免重复测量）

---

### 4.7 文本排版工具 (src/common/text_layout.py)

**职责**: 纯 fitz（无 Qt 依赖）的统一文本排版工具。

```python
def draw_wrapped_text(
    page, text, rect, fontsize=11, color=(0,0,0),
    line_gap=None, max_lines=None, regular=False,
) -> float
    """在 fitz.Rect 区域内渲染自动换行文本，返回实际高度"""

def truncate_text(text, max_chars, max_width_pt=None, fontsize=11, ellipsis="…") -> str
    """按字符数和渲染宽度双重截断"""

def parse_items(text) -> list
    """解析"项目名称|数量|金额"格式（发票 / 合同明细用）"""
```

懒导入 `template_renderer._wrap_text_in_width / _truncate_to_width / _insert_text_safe` 避免循环导入。

---

### 4.8 导出模块 (export/)  ★v1.1 RC 收尾

**架构**: Route B（MuPDF 矢量）方案，所有可矢量化的元素都用 PDF 原生矢量绘制，**禁止**先生成 PNG/JPG 再嵌入。

#### 4.8.1 模块导出 (export/__init__.py)

```python
from .pdf_exporter import (
    draw_linear_gradient,
    draw_diagonal_4corner_gradient,
    draw_text_icon,
    draw_icon_letter,
    embed_qr_code,
    render_with_pymupdf,
)
```

#### 4.8.2 核心函数 (export/pdf_exporter.py)

| 函数 | 说明 |
|------|------|
| `draw_linear_gradient(doc, page, rect, c0, c1, angle)` | 2 角线性渐变（PDF AxialShading Type 2） |
| `draw_diagonal_4corner_gradient(...)` | 4 角双线性渐变（2× AxialShading 叠加） |
| `draw_text_icon(page, rect, letter, ...)` | 文字图标（T/@/W/A）矢量绘制 |
| `draw_icon_letter(...)` | 同 draw_text_icon 别名 |
| `embed_qr_code(page, rect, qr_text, fallback_png)` | QR 矢量优先，PNG 兜底 |
| `render_with_pymupdf(...)` | 顶层渲染入口 |

#### 4.8.3 内部：PDF AxialShading 注入

```python
def _inject_axial_shading(doc, page, rect, c0, c1, angle, shading_name="Sh1")
    """
    注入 PDF AxialShading（Type 2）到指定 page。
    100% 矢量，无位图，无 cell 边界，放大 800% 完全平滑。
    
    步骤：
      1. 创建 Function (Type 2 Exponential) — C0→C1 插值
      2. 创建 Shading (Type 2 Axial) — 渐变轴 / Coords
      3. Page /Resources 添加 /Shading << /Sh1 <xref> 0 R >>
      4. content stream 追加: 'q <rect> re W n /Sh1 sh Q'
    """
```

#### 4.8.4 关键约束

- ✅ PDF AxialShading 原生渐变
- ✅ QR 码 SVG path 渲染
- ❌ 禁止 `fitz.page.insert_image` 嵌入 PNG 作为背景（会光栅化 + 出现色带）
- ❌ 禁止 vector mesh（fill_rect 网格）— 会产生可见网格线
- 修复后 PDF 文件大小变化 <20%，放大 800% 无色带 / 像素块

---

### 4.9 预览渲染 (src/common/preview_renderer.py)

**职责**: 统一预览清晰度（V1.1-RC3 重构），跨模板/名片/PDF 缩略图/水印实时预览共享 `PREVIEW_SCALE`。

```python
# V1.1-RC3 统一预览倍率（2.5 → 2.0，渲染像素 -36%，内存增长 <15%）
PREVIEW_SCALE = 2.0
MATRIX_SCALE = PREVIEW_SCALE

# 像素上限（避免 4K 屏 GPU 炸）
MAX_PREVIEW_PIXELS = 2200  # 最长边 ≤ 2200px
MAX_DPR = 2.0              # HiDPI 屏按 2x 算

# 进程级缓存
_cache: Dict[(template_id, data_hash, style_hash, image_path), Dict] = {}
# value = {"qpixmap": QPixmap, "w": int, "h": int, "render_ms": float, "ts": float}
```

**作用范围**（统一引用）:
- 模板预览
- 名片预览
- PDF 缩略图
- 水印实时预览

**不影响**: PDF 导出 / 压缩 / OCR / PDF→图片 / PDF→PPT

**约束**:
- ❌ 禁止 1.0（明显发糊）
- ❌ 禁止 3.0（内存上涨明显）

---

### 4.10 路径管理 (src/common/paths.py)

```python
def get_resource_root() -> str
    # 开发模式: sys.argv[0] 所在目录
    # 打包模式: sys._MEIPASS（PyInstaller 临时解压）

def get_app_root() -> str
    # 开发模式: 项目根目录
    # 打包模式: exe 所在目录

def get_data_dir() -> str
    # Windows: %APPDATA%/印流PDflow/
    # 其他:   ~/.pdflow/

def resource_path(*parts) -> str  # 资源文件（只读）
def data_path(*parts) -> str      # 用户数据（可写）
```

---

### 4.11 最近文件管理 (src/common/recent_files_manager.py)

**存储**: `<data_dir>/data/recent_files.json`，最大 50 条。

```python
add_record(file_path, action, output_path=None)
    # action: merge / compress / convert / watermark / template

get_recent_files(limit=10) -> List[Dict]
    # [{file_path, file_name, action, action_name, timestamp, datetime, output_path}]

clear_records()
get_status_text(timestamp) -> str  # "刚刚" / "5分钟前" / "昨天" / "3天前"
```

---

### 4.12 国际化 (translations/)

#### 4.12.1 翻译管理器 (translation_manager.py)

```python
LOCALE_NAMES = {"zh_CN": "简体中文", "zh_TW": "繁體中文", "en_US": "English"}
_current_locale = "zh_CN"

def set_locale(locale: str): ...
def get_locale() -> str: ...
def _(text: str) -> str: ...           # 快捷翻译

class TranslationManager:
    def register_page(page_instance, has_ui=True)  # 注册页面（语言切换时回调 retranslateUi）
    def switch_language(locale_code: str) -> bool  # 切换语言 + 重译所有注册页面
```

#### 4.12.2 翻译字典 (translations.py)

维护 zh_CN / zh_TW / en_US 三语映射表。

---

## 5. 页面模块详解

### 5.1 页面基类模式

```python
class XxxPage(QWidget):
    signal_name = Signal(str)        # 信号定义

    def __init__(self):
        super().__init__()
        self.ui = Ui_XxxPage()       # UI 类实例
        self.ui.setupUi(self)        # 设置 UI
        self._connect_signals()      # 连接信号

    def apply_theme(self, colors: dict):
        """主题切换时由 ThemeManager 调用，更新内联样式"""
        self.setStyleSheet(f"background: {colors['bg']};")
        self.ui.apply_theme(colors)  # 传递到 UI 类

    def retranslateUi(self):
        """语言切换时由 TranslationManager 调用"""
        self.ui.retranslateUi(self)
```

### 5.2 首页 (pages/home_page.py)

**类**: `HomePage` / `Ui_HomePage`

**辅助组件**:

| 组件 | 作用 |
|------|------|
| `Badge` | 左侧绿色脉冲圆点 + 文字（V1.1-beta 徽章） |
| `Glow` | 径向渐变光晕装饰 |
| `FunctionCard` | 4 个工具箱入口卡片（带 hover 色条动画） |
| `StepCard` | 快速上手 3 步流程 |
| `FileItem` | 最近使用文件列表项 |
| `GridBackground` | 背景网格线装饰 |
| `AccentStrip` | 左上角装饰色条（hover 时 14→24px） |

**信号**:
```python
card_clicked = Signal(str)        # 卡片点击 → 跳转
file_clicked = Signal(str, str)    # 文件点击 → 加载到对应页面
```

**布局**: 3+2 网格 + 区域容器化 + 渐变分隔线（V2.4 设计）。

### 5.3 工具箱页面（合并/压缩/转换/水印）

| 页面 | 关键功能 | 后端 |
|------|---------|------|
| **MergePage** | 多文件拖拽合并、按页/范围拆分、页面重排序 | `pdf_api.merge_pdfs / split_pdf / reorder_pdf_pages` |
| **CompressPage** | 三档质量压缩 + 实时预览 | `pdf_api.compress_pdf` |
| **ConvertPage** | PDF↔图片 / PDF→Word / PDF→Excel / PDF→PPT | `pdf_api.images_to_pdf / pdf_to_word / pdf_to_excel / pdf_to_ppt` |
| **WatermarkPage** | 文字/图片水印，6 种位置，实时预览 | `legacy_watermark.do_watermark` + `watermark_preview.render_watermark_preview` |

**水印页 V1.1-RC3 重构**:
- 方案 B：**缓存底图 + 只重画水印层**（参数变化 ≤30ms 响应）
- 共享 `PREVIEW_SCALE=2.0` 和 `MAX_DPR=2.0`
- 滑条 + 数字输入组合，修复导出旋转角度不匹配

### 5.4 模板排版入口 (pages/template_layout_page.py)

**类**: `TemplateLayoutPage` / `Ui_TemplateLayoutPage` / `TemplateEntryDialog`

**职责**:
- 从 `assets/templates/` 动态加载 JSON
- 3 列卡片网格展示
- 点击卡片 → `TemplateEntryDialog` 确认 → 发射 `editor_requested` 信号

**信号**:
```python
editor_requested = Signal(str)   # 请求打开编辑器，参数: template_id
```

### 5.5 模板编辑器 (pages/template_editor_page.py)

**类**: `TemplateEditorPage` + 动态构建的 UI 控件

**职责**:
- 根据 JSON `fields` 动态生成表单
- 字段分组（个人信息/公司信息/联系方式/上传项）
- 右侧实时预览面板
- 顶部 `RenderContext` 锁定一次参数同时驱动预览 + 导出
- 底部操作栏：生成 PDF / 导出文件夹选择（TPL-06）

**支持文件上传（TPL-05）**: 通过 `UPLOAD_TEMPLATES` 字典为模板配置上传项：

```python
UPLOAD_TEMPLATES = {
    "business_card": [
        {"side": "front", "key": "back_logo", "field": "back_logo",
         "title": "正面 LOGO", "icon": "🖼", "accepted_suffixes": ["png", "jpg", "jpeg"],
         "show_position_shape": True},
        {"side": "front", "key": "back_qr_image", ...},
        {"side": "back",  "key": "logo", ...},
    ],
    "notice": [...],
}
```

**RenderContext / CanvasModel**（统一画布模型，V1.1 关键修复）:
```python
class RenderContext:
    """编辑器统一渲染上下文，一次 serialize 锁定所有参数"""
    def __init__(self, template_id, side, fields, styles, assets, layout): ...
    def to_canvas() -> CanvasModel
    def render_to_pixmap(target_width=560, dpi=2.5) -> QPixmap
    def render_to_pdf(output_path) -> str
    def debug_snapshot() -> dict

class CanvasModel:
    """同一份 CanvasModel 同时驱动预览和导出（保证一致性）"""
```

### 5.6 设置页 (pages/settings_page.py)

**类**: `SettingsPage` / `Ui_SettingsPage`（由 pyside6-uic 生成于 `settings_page_ui.py`）

**信号**:
```python
developer_mode_changed = Signal(bool)   # 开发者模式切换
language_changed = Signal(str)          # 语言切换
output_dir_changed = Signal(str)        # 输出目录变更
```

**设置项**: 主题切换 / 语言切换 / 开发者模式 / 输出后缀 / 关于 / 输出目录 / LOGO

### 5.7 速文创作 (pages/speedwrite_page.py)

**类**: `SpeedwritePage` — 开发者模式专属入口（按钮可见性由 `developer_mode` 配置控制）

**状态**: 界面已就绪，待模板排版稳定后启用（P2）。

---

## 6. 关键类与函数 API

### 6.1 主题系统 API

```python
class ThemeManager(QObject):
    theme_changed = Signal(str)

    def apply_theme(self, theme: str = None, app=None) -> None
    def register_page(self, widget) -> None
    def unregister_page(self, widget) -> None
    def get_qss(self, theme: str = None) -> str
    def toggle(self, app=None) -> None
    @property
    def current_theme(self) -> str
    def is_dark(self) -> bool
```

### 6.2 PDF API

```python
def get_pdf_info(path: str) -> dict
def merge_pdfs(output: str, *paths, progress_callback=None) -> dict
def split_pdf(path: str, out_dir: str, mode: str, range_str: str, ...) -> dict
def compress_pdf(input: str, quality: str, output: str, progress=None, timeout=60) -> dict
def pdf_to_images(input: str, out_dir=None, dpi=150, fmt="png") -> dict
def images_to_pdf(paths: list, output=None, orient="portrait", quality="high") -> dict
def pdf_to_word(input: str, output=None) -> dict
def pdf_to_excel(input: str, output=None) -> dict
def pdf_to_ppt(input: str, out_dir=None) -> dict
def add_watermark(input: str, wm_text: str, output=None, font_size=60,
                  opacity=0.15, rotation=-45, color=(128,128,128), position="center") -> dict
def reorder_pdf_pages(input: str, page_order: str, output=None) -> dict
def ocr_extract_text(input: str, progress=None) -> dict
def batch_convert(...) / batch_merge_pdfs(...) / batch_compress_pdfs(...)
class PDFlowError:  # 错误信息载体
```

### 6.3 模板 IR / Layout Parser API

```python
# pdf_table_ir.py
@dataclass
class TableMeta:    # page / table_id / confidence / mode
@dataclass
class TableBlock:   # rows / spans / meta

def clean_cell(text) -> str
def normalize_table(rows) -> List[List[str]]
def to_table_block(rows, page=0, table_id=0, confidence=1.0, mode="structured") -> Dict
def ir_to_rows(ir) -> List[List[str]]
def ir_meta(ir) -> Optional[TableMeta]
def has_newline_cells(rows) -> bool
def to_dataframe(ir_or_rows) -> pd.DataFrame
def normalize_excel_input(result) -> pd.DataFrame
def fallback_block(rows, page=0, table_id=0, confidence=0.5) -> Dict

# pdf_layout_parser.py
def _w_get(w, key, default=None) -> Any
def cluster_by_y(blocks, threshold=3.0) -> List[List[Any]]
def _is_special_token(text) -> bool
def _split_by_special_tokens(text) -> List[str]
def parse_layout_blocks(page) -> List[List[str]]
def parse_layout_rows(page) -> List[Dict[str, Any]]
```

### 6.4 模板渲染 API

```python
def render_template(template_id: str, output_path: str, data: dict, **kwargs) -> str
def render_business_card(output_path, data, logo_path=None, photo_path=None,
                        qr_image_path=None, style_options=None, bg_image_path=None,
                        bg_image_opacity=50, bg_texture="none", bg_custom_color="",
                        text_color="#2C3E50", text_secondary_color="#7F8C8D",
                        render_sides=None, progress_callback=None) -> str
def render_notice(output, data, image_path=None, style=None, progress=None) -> str
def render_product_spec(output, data, image_path=None, style=None, progress=None) -> str
def render_contract(output, data, image_path=None, style=None, progress=None) -> str
def render_invoice(output, data, image_path=None, style=None, progress=None) -> str
def render_report(output, data, image_path=None, style=None, progress=None) -> str
```

### 6.5 文本排版 / 导出 / 预览 API

```python
# text_layout.py
def draw_wrapped_text(page, text, rect, fontsize=11, color=(0,0,0),
                     line_gap=None, max_lines=None, regular=False) -> float
def truncate_text(text, max_chars, max_width_pt=None, fontsize=11, ellipsis="…") -> str
def parse_items(text) -> list  # "项目|数量|金额" 解析

# export/pdf_exporter.py
def draw_linear_gradient(doc, page, rect, c0, c1, angle=0.0) -> None
def draw_diagonal_4corner_gradient(doc, page, rect, c1, c2, c3, c4) -> None
def draw_text_icon(page, rect, letter, color, size) -> None
def embed_qr_code(page, rect, qr_text, fallback_png=None) -> bool
def render_with_pymupdf(...) -> ...

# preview_renderer.py
PREVIEW_SCALE = 2.0
MAX_PREVIEW_PIXELS = 2200
MAX_DPR = 2.0
```

### 6.6 路径 / 最近文件 / i18n API

```python
# paths.py
def get_resource_root() -> str
def get_app_root() -> str
def get_data_dir() -> str
def resource_path(*parts) -> str
def data_path(*parts) -> str

# recent_files_manager.py
def add_record(file_path, action, output_path=None) -> None
def get_recent_files(limit=10) -> List[Dict]
def clear_records() -> None
def get_status_text(timestamp) -> str

# translation_manager.py
def _(text: str) -> str
def set_locale(locale: str) -> None
def get_locale() -> str
class TranslationManager:
    def register_page(page, has_ui=True) -> None
    def switch_language(locale_code: str) -> bool
```

### 6.7 模板 JSON Schema

```json
{
  "id": "template_id",
  "name": "模板名称",
  "icon": "emoji",
  "description": "模板描述",
  "type": "分类",
  "version": "1.0",
  "version_note": "版本说明",
  "sides": ["front", "back"],     // 名片专用
  "fields": [
    {
      "key": "field_key",
      "label": "字段标签",
      "type": "text | textarea | image_upload | table",
      "required": true,
      "maxLength": 50,
      "placeholder": "提示",
      "group": "分组键",
      "side": "front | back",
      "emphasis": true,
      "size_hint": "H1 | Body | Small",
      "default": "默认值"
    }
  ],
  "style_options": {
    "theme_color": {
      "label": "主题色",
      "type": "color_preset",
      "default": "#4D7CFE",
      "options": [{"name": "科技蓝", "value": "#4D7CFE"}, ...]
    },
    "bg_style": {
      "label": "背景样式",
      "type": "radio | select",
      "default": "white",
      "options": [{"name": "纯白", "value": "white"}, ...]
    }
  },
  "sample": {
    "front": {...},
    "back": {...}
  }
}
```

---

## 7. 依赖关系图

### 7.1 模块依赖

```
run_main.py
├── pages/main_window.py
│   └── src/common/{theme, paths, theme_manager}
├── pages/home_page.py
│   ├── src/common/recent_files_manager
│   └── translations/translation_manager
├── pages/merge_page.py
│   ├── src/common/pdf_api
│   └── src/common/{paths, recent_files_manager, error_handler}
├── pages/compress_page.py → src/common/pdf_api
├── pages/convert_page.py
│   ├── src/common/pdf_api           (走 pdf_table_ir)
│   ├── src/common/pdf_table_ir      ★v1.1-patch
│   └── src/common/pdf_layout_parser ★v1.1-patch
├── pages/watermark_page.py
│   ├── src/common/legacy_watermark
│   ├── src/common/watermark_preview
│   └── src/common/preview_renderer
├── pages/template_layout_page.py → src/common/paths
├── pages/template_editor_page.py
│   ├── src/common/template_renderer
│   ├── src/common/preview_renderer   (PREVIEW_SCALE)
│   ├── src/common/text_layout
│   ├── src/common/theme_tokens
│   └── export/pdf_exporter           (Route B 矢量)
├── pages/settings_page.py
│   ├── src/common/theme_manager
│   └── src/common/{theme, paths}

src/common/template_renderer.py
├── export/pdf_exporter (Route B 矢量)
└── src/common/text_layout

src/common/pdf_api.py
├── src/common/pdf_table_ir   (PDF→Excel IR)
└── src/common/pdf_layout_parser (Layout 重建)
```

### 7.2 第三方依赖

| 包 | 用途 |
|----|------|
| PySide6 6.11+ | Qt GUI 框架（核心） |
| PyMuPDF (fitz) 1.27+ | PDF 处理核心 |
| Pillow 12.2+ | 图像处理、LOGO 渲染 |
| pdf2docx 0.5.13+ | PDF → Word |
| pdfplumber 0.11.9+ | 表格提取 |
| pandas 2.3.3+ | Excel 数据处理 |
| openpyxl 3.1.5+ | Excel 读写 |
| python-pptx 1.0.2+ | PPT 生成 |
| shiboken6 6.11+ | PySide6 绑定 |
| bandit 1.9.4 | Python 静态安全分析 |
| pip-audit 2.10.0 | 依赖漏洞扫描 |
| slopscan 0.1.0 | AI 生成代码漏洞检测 |

---

## 8. 项目运行方式

### 8.1 开发环境

```bash
# 1. 激活虚拟环境
e:\印流PDflow项目\pyside6_env\Scripts\activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动应用
python run_main.py
```

或使用项目自带脚本：

```bash
# Windows 启动
start.bat              # 前台
start_debug.bat        # 调试模式（带控制台）

# PowerShell
start.ps1
start_debug.ps1
```

### 8.2 打包发布

```bash
# 主打包（PyInstaller）
pyinstaller PDflow_V1.1-RC2.spec

# WebEngine 变体（含 QtWebEngine 隐藏导入修复）
pyinstaller PDflow_V1.1-RC2.webengine.spec

# 7z 二次压缩
python build/make_7z.py

# SFX 自解压安装包
python build/make_sfx.py
```

**打包产物**:
- `build/PDflow_V1.1-RC2/PDflow_V1.1-RC2.exe`（单文件）
- `build/PDflow_V1.1-RC2.exe`（SFX 安装包）

### 8.3 测试

```bash
# P0 Hotfix 单测（PDF→Excel）
python build/test_p0_hotfix.py

# 端到端测试
python build/test_p0_e2e.py

# Layout 解析单测
python build/test_layout_parser.py

# 矢量导出回归
python tests/export_vector_test.py

# GUI 路径验证
python build/test_gui_path.py
python build/check_webengine.py
```

### 8.4 安全扫描

```bash
# 依赖漏洞
pip-audit -r requirements.txt

# Python 静态安全
bandit -r src/ pages/ export/

# AI 生成代码特征
slopscan pages/ --ai-detection
```

---

## 9. v1.1-patch 关键修复

### 9.1 P0 Hotfix #1：PDF→Excel 输出协议统一

**问题**: `DataFrame has no attribute 'tolist'` 崩溃
- IR dict / DataFrame / list 入参混用，`df.tolist()` 调用导致 AttributeError

**修复**:
- 新增 `src/common/pdf_table_ir.py`，定义 `TableBlock` dataclass + IR dict
- 统一 `normalize_excel_input(result)` 入口，**强制返回 DataFrame**
- 替换 `df.tolist()` / `df.values.tolist()` → `df.to_dict('records')`
- 标准化 fallback 返回结构为 `{"rows", "mode", "meta"}` dict
- Excel 写入入口统一接收 DataFrame

**影响文件**:
- `src/common/pdf_api.py` (+34/-28)
- `src/common/pdf_table_ir.py` (+91 新增)
- `build/test_p0_hotfix.py` (+104 新增)

### 9.2 P0 Hotfix #2：Layout Row Reconstruction

**问题**: 所有 PDF 内容被压扁到 A 列，电话/邮箱/地址无法识别为独立行
- 旧 fallback 用 `page.extract_text() + split("\n")` 丢失坐标信息

**修复**:
- 新增 `src/common/pdf_layout_parser.py`
  - `parse_layout_blocks(page)` 主入口：按 y 降序排序 + 行聚类（threshold=3pt）
  - `_w_get` 兼容 dict / object / 索引 三种 word 风格
  - `_split_by_special_tokens` 语义拆分：phone / email / url 强制独立成行
  - 严格禁止 `page.extract_text()` 和 `text.split("\n")`
- 修改 `src/common/pdf_api.py`:
  - `_extract_page_best`（lines 898-909）改用 `parse_layout_blocks`
  - `_extract_text_fallback`（lines 1040-1068）改用 `parse_layout_blocks`
  - 删除冗余 `_extract_page_words`（43 行）

**测试**: `test_layout_parser.py` 11 个用例全通过；E2E 验证 body.pdf（17 sheets）、品牌手册（14 sheets）。

### 9.3 V1.1 RC 收尾：PDF 矢量导出（Route B）

**问题**: 渐变背景用 PNG 位图嵌入导致放大后色带 / 像素块；vector mesh 产生可见网格线

**修复**:
- 新增 `export/pdf_exporter.py`：`draw_linear_gradient` 等矢量函数
- PDF AxialShading（Type 2）原生渐变 → 放大 800% 仍平滑
- QR 码 SVG path 渲染 + PNG 兜底
- 文字图标（T/@/W/A）矢量绘制
- 修复后 PDF 文件大小变化 <20%

### 9.4 V1.1-RC3 修复：统一预览倍率

**修复**:
- `src/common/preview_renderer.py`: `PREVIEW_SCALE = 2.0`（原 2.5）
- 渲染像素 -36%，缩放到 560px 仍锐利，内存增长 <15%
- 作用范围统一：模板预览 / 名片预览 / PDF 缩略图 / 水印实时预览
- 水印页：方案 B（缓存底图 + 只重画水印层），参数变化 ≤30ms

---

## 10. 开发规范与红线

### 10.1 代码规范

1. **文件编码**: UTF-8
2. **缩进**: 4 个空格
3. **行长度**: ≤100 字符
4. **导入顺序**: 标准库 → 第三方 → 本地模块
5. **文档字符串**: 公共函数必须添加 docstring

### 10.2 UI 开发规范

1. **页面类**: `XxxPage`（QWidget 子类）
2. **UI 类**: `Ui_XxxPage`（由 pyside6-uic 生成）
3. **必须实现方法**:
   - `apply_theme(colors)`: 响应主题切换
   - `retranslateUi()`: 响应语言切换

### 10.3 主题开发规范

1. 使用 `ThemeManager` 注册页面
2. 在 `apply_theme()` 中更新所有内联样式
3. 使用 `theme.py` 中定义的配色 Token
4. **禁止硬编码颜色**（深色模式色值直接写在 setStyleSheet 中）

### 10.4 技术性开发红线

| 红线项 | 说明 |
|--------|------|
| 🚫 禁止 Flet 相关代码 | `import flet` / `ft.*` 均违规 |
| 🚫 禁止 `ft.SegmentedButton` / `ft.FilePicker` | 改用 `QFileDialog` |
| 🚫 禁止修改 `main_flet.py` | 已废弃 |
| 🚫 禁止引用 `_旧版归档/` | 仅作参考 |
| 🚫 禁止 `TkFilePicker` | Flet 时代方案 |
| 🚫 禁止 PNG 位图作为背景 | 用 PDF AxialShading |
| 🚫 禁止 vector mesh（fill_rect 网格）| 有可见网格线 |
| 🚫 禁止 df.tolist() | 用 df.to_dict('records') |

### 10.5 PDF 渲染硬约束

- 名片字号固定上限：name ≤ min(card_h*0.12, 16pt)，title 10px，contact 9px
- 名片尺寸：ISO/IEC 7810 ID-1（85.6×53.98mm / 242.6×153.0pt）
- LOGO 保持原始宽高比（PIL.Image 渲染）
- 背景填满（`keep_proportion=False`），禁止白边
- 缺失资源显示虚线占位框 + "LOGO"/"QR"
- 渐变背景：PDF AxialShading（不允许位图嵌入）
- 修复后 PDF 大小变化 <20%

### 10.6 预览约束

- 统一引用 `PREVIEW_SCALE = 2.0`
- 禁止 1.0（明显糊）、禁止 3.0（内存上涨）
- 像素上限 `MAX_PREVIEW_PIXELS = 2200`，DPR 上限 `MAX_DPR = 2.0`
- 预览用 `fitz.Matrix(2.0, 2.0)` + `alpha=False`（减少透明层 / 锯齿）

### 10.7 变更边界（V1.1-patch）

✅ **允许修改**:
- `export/` 目录
- `src/common/template_renderer.py`
- `export/pdf_exporter.py`
- `src/common/preview_renderer.py` 的 `PREVIEW_SCALE`
- `src/common/pdf_table_ir.py`（新增）
- `src/common/pdf_layout_parser.py`（新增）

❌ **禁止修改**:
- `src/common/pdf_api.py` 中除 P0 Hotfix 涉及行外的逻辑
- `src/common/legacy_watermark.py` / `ocr_engine.py`
- 业务逻辑、WebEngine、安装包配置

---

## 11. 附录

### 11.1 配置文件

**`config.json`**（用户数据目录）:
```json
{
  "theme": "dark",
  "language": "zh_CN",
  "developer_mode": false,
  "output_suffix": "_processed",
  "output_dir": ""
}
```

**`app_config.json`**（`src/common/app_config.json`）:
```json
{ "theme": "dark" }
```

### 11.2 最近文件记录格式

```json
{
  "file_name": "example.pdf",
  "file_path": "C:/Users/.../example.pdf",
  "action": "merge|compress|convert|watermark|template",
  "action_name": "合并拆分",
  "timestamp": 1751521800.0,
  "datetime": "2026-06-14 10:30",
  "output_path": "C:/.../example_processed.pdf"
}
```

### 11.3 IR / Layout 数据格式

**TableBlock IR**:
```python
{
  "rows": [["姓名", "电话"], ["张三", "138-0000-0000"]],
  "spans": None,  # 预留 v1.2 OCR 合并单元格
  "meta": {
    "page": 1,
    "table_id": 1,
    "confidence": 1.0,
    "mode": "structured"  # structured / text_fallback / ocr_fallback
  }
}
```

**Layout Blocks 输出**:
```python
[
  ["张三"],              # 姓名
  ["138-0000-0000"],     # 电话（独立行）
  ["zhang@example.com"], # 邮箱（独立行）
  ["www.example.com"],   # URL（独立行）
]
```

### 11.4 安全工具

| 工具 | 用途 | 频率 |
|------|------|------|
| `bandit` | Python 静态安全 | 日常 |
| `pip-audit` | 依赖漏洞 | 新增依赖时 / 每月 |
| `slopscan` | AI 代码漏洞 | 每个模块完成后 |
| `safety` | 商业级依赖扫描 | 互补 pip-audit |

### 11.5 截图管理规范

**路径**: `07-计划书&上架资料/软件截图/`
**要求**: ≥5 张核心功能截图
**命名**: `截图_功能名称_版本号.png`
**格式**: PNG，≥1920×1080

必覆盖场景:
1. 首页全貌
2. 合并拆分
3. 水印 / 压缩
4. 格式转换
5. 模板排版

### 11.6 相关文档索引

| 文档 | 路径 | 说明 |
|------|------|------|
| 项目总章程 | `04-项目文档/印流PDflow_项目总章程_V2.5.md` | 最高约束 |
| UI 设计规范 | `04-项目文档/DESIGN.md` | 配色、组件规范 |
| Code Review | `04-项目文档/CODE_REVIEW.md` | 5 维度 30+ 检查项 |
| PM Agent 规则 | `04-项目文档/PM_SOUL.md` | 需求分析模板 |
| 已知问题 | `04-项目文档/KNOWN_ISSUES.md` | 遗留问题跟踪 |
| 变更日志 | `04-项目文档/CHANGELOG.md` | 版本变更 |
| 发布说明 | `04-项目文档/RELEASE_NOTES.md` | 用户可见变更 |
| 发布门禁 | `04-项目文档/RELEASE_GATE.md` | 发布标准 |
| 路线图 | `04-项目文档/ROADMAP.md` | V1.0→V2.0 演进 |

### 11.7 配套报告文档

`04-项目文档/` 目录下的专题报告：
- `EXPORT_VECTOR_AUDIT.md` / `EXPORT_VECTOR_FIX_REPORT.md` — 矢量导出修复
- `PREVIEW_RENDER_REPORT.md` / `PREVIEW_QUALITY_REPORT.md` — 预览质量
- `THEME_FLOW_REPORT.md` / `THEME_RECOVERY_REPORT.md` — 主题系统
- `BUSINESS_CARD_LAYOUT_V2_REPORT.md` — 名片布局 V2
- `BUSINESS_CARD_DOUBLE_SIDE_REPORT.md` — 名片正反面
- `PACKAGE_SIZE_REPORT.md` / `PACKAGE_SLIM_V11RC1_REPORT.md` — 安装包瘦身
- `EXPORT_PARITY_REPORT.md` / `PREVIEW_EXPORT_PARITY_REPORT.md` — 预览导出对齐
- `RC_BLOCKER_REPORT.md` — RC 阻断项
- `V1.1_BETA_ACCEPTANCE_REPORT.md` — V1.1-beta 验收
- `FREEZE_PATCH_REPORT.md` / `FREEZE_REPORT.md` — 冻结补丁
- `安全审计报告_V1.0.md` — 安全审计

---

**文档结束**

*本文档由 AI 自动分析项目代码生成（V1.1-RC2 / v1.1-patch），如发现与代码不一致，请以最新代码为准并向项目负责人反馈。*
