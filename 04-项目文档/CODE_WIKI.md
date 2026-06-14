# 印流PDflow - Code Wiki 文档

> **项目版本**: V1.1-RC1  
> **技术栈**: PySide6 (Qt 6.11+) + Python 3.12+ + PyMuPDF + Pillow  
> **最后更新**: 2026-06-08  
> **文档用途**: 项目架构说明、模块职责、API参考、开发指南

---

## 目录

1. [项目概述](#1-项目概述)
2. [整体架构](#2-整体架构)
3. [目录结构](#3-目录结构)
4. [核心模块详解](#4-核心模块详解)
5. [页面模块详解](#5-页面模块详解)
6. [关键类与函数API](#6-关键类与函数api)
7. [依赖关系图](#7-依赖关系图)
8. [项目运行方式](#8-项目运行方式)
9. [开发规范](#9-开发规范)
10. [附录](#10-附录)

---

## 1. 项目概述

### 1.1 产品定位

**印流PDflow** 是一款专为设计师打造的 PDF 版式设计工具，提供：

- **PDF工具箱**: 合并拆分、压缩优化、格式转换、水印处理
- **模板排版**: JSON模板定义 + 表单输入 + 实时预览 + PDF生成
- **速文创作**: AI驱动的文案创作功能（开发中）

### 1.2 技术特点

| 特性 | 说明 |
|------|------|
| 跨平台 | Windows/macOS/Linux (基于Qt框架) |
| 深色/浅色主题 | 完整的双主题支持，实时切换 |
| 国际化 | 支持简体中文/繁体中文/英文 |
| 无边框窗口 | 自定义标题栏，现代化UI |
| 模板系统 | JSON驱动，可扩展的模板引擎 |
| PDF处理 | 基于PyMuPDF的高质量PDF渲染 |

### 1.3 技术栈

| 层级 | 技术 | 版本 |
|------|------|------|
| GUI框架 | PySide6 | 6.11+ |
| 语言 | Python | 3.12+ |
| PDF处理 | PyMuPDF (fitz) | 1.27+ |
| 图像处理 | Pillow | 12.2+ |
| PDF转Word | pdf2docx | 0.5.13+ |
| PDF表格提取 | pdfplumber | 0.11.9+ |
| Excel处理 | openpyxl | 3.1.5+ |
| PPT生成 | python-pptx | 1.0.2+ |

---

## 2. 整体架构

### 2.1 架构分层

```
┌─────────────────────────────────────────────────────────────┐
│                      表现层 (UI Layer)                       │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐ │
│  │  首页        │ │ 工具箱页面   │ │ 模板排版/速文创作       │ │
│  │  HomePage   │ │ MergePage   │ │ TemplateLayoutPage     │ │
│  │             │ │ CompressPage│ │ TemplateEditorPage     │ │
│  │             │ │ ConvertPage │ │ SpeedwritePage        │ │
│  │             │ │ WatermarkPage│ │                       │ │
│  └─────────────┘ └─────────────┘ └─────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                    应用框架层 (Framework)                     │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐ │
│  │ MainWindow  │ │ThemeManager │ │ TranslationManager      │ │
│  │ 主窗口管理   │ │ 主题管理器   │ │ 国际化管理器             │ │
│  └─────────────┘ └─────────────┘ └─────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                    业务逻辑层 (Business)                      │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐ │
│  │  PDF API    │ │TemplateRender│ │ RecentFilesManager    │ │
│  │  PDF处理    │ │ 模板渲染引擎  │ │ 最近文件管理             │ │
│  └─────────────┘ └─────────────┘ └─────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                    基础设施层 (Infrastructure)                │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐ │
│  │    Paths    │ │   Config    │ │    Theme/Colors         │ │
│  │  路径管理    │ │  配置管理    │ │    主题配色系统          │ │
│  └─────────────┘ └─────────────┘ └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 核心数据流

```
用户操作 → 页面组件 → 业务逻辑 → PDF API/模板渲染 → 文件输出
                ↓
         ThemeManager (主题同步)
                ↓
         TranslationManager (语言同步)
```

### 2.3 核心设计模式

- **单例模式**: ThemeManager 使用单例模式确保全局唯一
- **工厂模式**: 页面通过工厂函数动态创建
- **观察者模式**: ThemeManager 通过Signal通知页面主题变化
- **MVC模式**: 页面采用 Ui_XXXPage (View) + XxxPage (Controller) 分离

---

## 3. 目录结构

```
印流PDflow项目/
│
├── run_main.py                    # ★ 应用程序入口点
│
├── pages/                         # ★ UI页面模块目录
│   ├── __init__.py
│   ├── main_window.py             # 主窗口UI类 (Ui_MainWindow)
│   ├── main_window.ui              # 主窗口Qt Designer文件
│   ├── main_window_uic.py          # main_window.ui 编译产物
│   ├── home_page.py                # 首页 (HomePage + Ui_HomePage)
│   ├── merge_page.py               # 合并拆分页面
│   ├── compress_page.py            # 压缩页面
│   ├── convert_page.py             # 格式转换页面
│   ├── watermark_page.py           # 水印页面
│   ├── template_layout_page.py     # 模板排版入口页
│   ├── template_editor_page.py     # 模板编辑器页面
│   ├── speedwrite_page.py          # 速文创作页面
│   ├── settings_page.py             # 设置页面
│   ├── ai_api.py                   # AI API调用
│   ├── ai_dialogs.py              # AI对话框
│   ├── pdf_to_img.py               # PDF转图片工具
│   ├── global.qss                  # 全局QSS样式表
│   ├── global.qss.template          # QSS模板（包含{{TOKEN}}占位符）
│   ├── dark.qss                    # 预渲染深色主题样式
│   └── light.qss                   # 预渲染浅色主题样式
│
├── src/                           # ★ 核心源码目录
│   ├── __init__.py
│   └── common/                    # ★ 公共模块
│       ├── __init__.py
│       ├── pdf_api.py             # PDF操作API封装
│       ├── template_renderer.py    # 模板渲染引擎
│       ├── theme.py               # 主题配色定义
│       ├── theme_manager.py        # 主题管理器（单例）
│       ├── theme_tokens.py         # 主题Token管理
│       ├── config.py              # 配置管理
│       ├── paths.py               # 路径管理
│       ├── recent_files_manager.py # 最近文件管理
│       ├── ocr_engine.py          # OCR引擎
│       ├── ocr_provider.py         # OCR提供者
│       ├── ai_text_processor.py   # AI文本处理
│       └── preview_renderer.py     # 预览渲染器
│
├── translations/                   # ★ 国际化目录
│   ├── __init__.py
│   ├── translation_manager.py     # 翻译管理器
│   ├── translations.py            # 翻译字典
│   └── translations_en_US.ts      # 英文翻译资源
│
├── assets/                        # ★ 资源文件
│   ├── templates/                 # JSON模板文件
│   │   ├── presets/              # 预设模板
│   │   │   ├── business_card.json
│   │   │   ├── notice.json
│   │   │   └── product_spec.json
│   │   ├── business_card.json    # 名片模板
│   │   ├── notice.json           # 公告模板
│   │   ├── product_spec.json     # 产品规格模板
│   │   ├── contract.json          # 合同模板
│   │   ├── invoice.json          # 发票模板
│   │   └── report.json           # 报告模板
│   └── icons/                    # SVG图标资源
│
├── build/                         # PyInstaller打包输出
├── dist/                          # 打包后的可执行文件
├── pyside6_env/                   # Python虚拟环境
│
├── 02-素材资源/                   # LOGO等品牌素材
│   └── assets/
│       └── pdflow-logo*.png       # 各尺寸LOGO
│
├── 04-项目文档/                   # 项目文档
│   ├── CODE_WIKI.md              # Code Wiki文档
│   ├── DESIGN.md                  # UI设计规范
│   ├── CODE_REVIEW.md             # 代码审查规范
│   └── ...
│
├── PDflow_V1.1-RC1.spec          # PyInstaller打包配置
├── requirements.txt                # Python依赖
├── config.json                    # 应用配置
└── _旧版归档/                     # 历史版本归档（不参与编译）
```

---

## 4. 核心模块详解

### 4.1 入口模块 (run_main.py)

**文件路径**: `run_main.py`

**职责**:
- 应用程序启动、主窗口初始化
- 全局系统连接（主题、翻译、导航）
- 无边框窗口和自定义标题栏创建

**核心流程**:
```python
def main():
    1. 创建 TranslationManager (i18n)
    2. 读取保存的语言设置
    3. 创建 QApplication
    4. 设置全局应用图标
    5. 初始化 ThemeManager
    6. 创建无边框主窗口
    7. 设置自定义标题栏（最小化/最大化/关闭按钮）
    8. 加载UI并嵌入主窗口
    9. 应用主题
    10. 配置导航切换 setup_navigation()
    11. 连接模板信号 _connect_template_signals()
    12. 连接设置信号 _connect_settings_signals()
    13. 注册所有页面到 ThemeManager
    14. 进入事件循环 app.exec()
```

**关键函数**:

| 函数 | 说明 |
|------|------|
| `main()` | 应用程序主入口 |
| `setup_navigation(ui)` | 配置导航按钮与QStackedLayout页面切换 |
| `_apply_main_window_theme(ui, colors, ...)` | 应用主题到主窗口内联样式 |
| `_connect_template_signals(ui, theme_mgr)` | 连接模板排版相关信号 |
| `_connect_settings_signals(ui, pages_stack, i18n)` | 连接设置页面信号 |
| `_show_about_dialog()` | 显示关于对话框 |

**导航配置**:
```python
NAV_ITEMS = [
    ("btnHome",            "首页",         HomePage),
    ("btnMerge",           "合并拆分",     MergePage),
    ("btnCompress",        "压缩",         CompressPage),
    ("btnConvert",         "格式转换",     ConvertPage),
    ("btnWatermark",       "水印",         WatermarkPage),
    ("btnSpeedwrite",      "速文创作",     None),   # 开发者模式控制
    ("btnTemplateLayout",  "模板排版",     TemplateLayoutPage),
    ("btnSettings",        "设置",         SettingsPage),
]
```

### 4.2 主窗口模块 (pages/main_window.py)

**类**: `Ui_MainWindow`

**职责**:
- 定义主窗口UI结构（Qt Designer生成的Python代码）
- 侧边栏导航按钮创建
- QStackedLayout页面容器管理

**核心方法**:

```python
# 创建导航行
_make_nav_row(container, icon_name, btn_text, btn_obj_name, default_checked)

# 创建导航图标
_create_nav_icon(parent, icon_name, color_hex)

# 渲染SVG图标
_render_nav_icon_svg(icon_name, color_hex)

# 应用侧边栏主题
apply_sidebar_theme(colors)
```

### 4.3 主题系统

#### 4.3.1 主题配色 (src/common/theme.py)

**常量定义**:

| 常量 | 说明 |
|------|------|
| `DARK_COLORS` | 深色模式配色字典（80+ token） |
| `LIGHT_COLORS` | 浅色模式配色字典（80+ token） |

**核心Token示例**:
```python
DARK_COLORS = {
    # 背景层
    "bg": "#0B0E11",              # 页面背景
    "card_bg": "#14141A",        # 卡片背景
    "input_bg": "#0A0A0F",       # 输入框背景
    "nav_bg": "#0F0F14",         # 侧边栏背景

    # 文字色
    "text_main": "#ECEDF0",      # 主要文字
    "text_sub": "#8B8D98",      # 次要文字
    "text_muted": "#4A4B56",    # 禁用文字

    # 主题色
    "primary": "#4D7CFE",        # 主题色（蓝）
    "primary_hover": "#3D6CF0",
    "primary_pressed": "#2D5CD0",

    # 语义色
    "success": "#34C759",
    "warning": "#FF9500",
    "error": "#FF3B30",

    # 导航侧边栏
    "sidebar_icon": "#848E9C",
    "sidebar_icon_active": "#4D7CFE",
    "sidebar_text": "#848E9C",
    "sidebar_text_active": "#EAECEF",

    # ... 更多token
}
```

**核心函数**:
```python
get_colors(theme=None)      # 获取指定主题的颜色字典
get_current_theme()         # 获取当前主题名称
set_theme(theme: str)       # 设置并保存主题
```

#### 4.3.2 主题管理器 (src/common/theme_manager.py)

**类**: `ThemeManager` (单例模式，继承QObject)

**职责**:
- 加载 global.qss.template 并替换 `{{TOKEN}}` 为实际色值
- 将生成的样式表应用到 QApplication
- 支持深色/浅色模式切换
- 通知所有注册的页面更新内联样式
- 持久化主题偏好到 app_config.json

**核心方法**:

```python
# 应用主题
def apply_theme(self, theme: str = None, app=None) -> None
    # 1. 替换模板中的token为实际色值
    # 2. 清除所有控件内联样式
    # 3. 设置全局调色板QPalette
    # 4. 注入QSS样式表
    # 5. 重建动态组件样式
    # 6. 完整重绘流程(unpolish → polish → repaint)
    # 7. 持久化到配置文件
    # 8. 发射theme_changed信号

# 注册页面
def register_page(self, widget) -> None
    # widget需实现 apply_theme(colors) 方法

# 获取渲染后的QSS
def get_qss(self, theme: str = None) -> str
    # 优先使用预渲染的 dark.qss / light.qss

# 切换主题
def toggle(self, app=None) -> None
```

**信号**:
```python
theme_changed = Signal(str)  # 参数: "dark" | "light"
```

**主题切换流程**:
```
apply_theme("dark")
    ↓
_load_template() → _render_qss(colors)
    ↓
_clear_widget_styles(qapp)     # 清空内联样式
    ↓
_set_qapp_palette(colors)     # 设置QPalette
    ↓
qapp.setStyleSheet(qss)        # 注入QSS
    ↓
_refresh_dynamic_widgets()      # 调用所有页面的apply_theme()
    ↓
_full_repaint()                # unpolish → polish → repaint
    ↓
set_theme("dark")              # 持久化
    ↓
theme_changed.emit("dark")     # 发射信号
```

### 4.4 PDF API 模块 (src/common/pdf_api.py)

**职责**: 封装所有PDF操作功能，基于PyMuPDF实现

#### 4.4.1 主要函数

| 类别 | 函数 | 说明 |
|------|------|------|
| 信息读取 | `get_pdf_info(file_path)` | 获取PDF页数、大小、标题 |
| 合并拆分 | `merge_pdfs(output_path, *filepaths)` | 合并多个PDF |
| | `split_pdf(filepath, output_dir, mode, range_str)` | 按页或范围拆分 |
| 压缩 | `compress_pdf(input_path, quality, output_path)` | 按质量等级压缩 |
| 转换 | `pdf_to_images(input_path, output_dir, dpi, fmt)` | PDF转图片 |
| | `images_to_pdf(image_paths, output_path, orientation, quality)` | 图片转PDF |
| | `pdf_to_word(input_path, output_path)` | PDF转Word |
| | `pdf_to_excel(input_path, output_path)` | PDF转Excel |
| | `pdf_to_ppt(input_path, output_dir)` | PDF转PPT |
| 水印 | `add_watermark(input_path, wm_text, output_path, ...)` | 添加文字水印 |
| 页面操作 | `reorder_pdf_pages(input_path, page_order, output_path)` | 页面重排序 |
| 批量处理 | `batch_convert(input_path, output_dir, batch_fmt)` | 批量转换 |
| | `batch_merge_pdfs(file_groups, output_dir)` | 批量合并 |
| | `batch_compress_pdfs(file_paths, output_dir, quality)` | 批量压缩 |
| OCR | `ocr_extract_text(input_path, progress_callback)` | OCR文字提取 |

#### 4.4.2 函数签名示例

```python
def compress_pdf(
    input_path: str,
    quality: str = "high",      # "high" | "medium" | "low"
    output_path: str = None,
    progress_callback=None,    # callable(current, total)
    timeout: int = 60          # 超时秒数
) -> dict

def pdf_to_excel(input_path: str, output_path: str = None) -> dict
    # 使用pdfplumber多参数优化表格提取
    # 返回: {"status": "ok", "output": path, "tables": N}

def add_watermark(
    input_path: str,
    wm_text: str,
    output_path: str = None,
    font_size: int = 60,
    opacity: float = 0.15,
    rotation: int = -45,
    color: tuple = (128, 128, 128),
    position: str = "center"   # "center" | "tile"
) -> dict
```

#### 4.4.3 PDFlowError 错误类

```python
class PDFlowError:
    """PDF操作错误信息载体"""
    def __init__(self, file_path, operation, message, recoverable=True)
    def to_dict(self) -> dict
    def __repr__(self) -> str
```

### 4.5 模板渲染引擎 (src/common/template_renderer.py)

**职责**: 将模板数据渲染为PDF，支持多种模板类型

#### 4.5.1 支持的模板

| 模板类型 | 渲染函数 | 尺寸 | 说明 |
|----------|----------|------|------|
| 名片 | `render_business_card()` | 90×54mm | 支持正反面、LOGO、二维码 |
| 公告 | `render_notice()` | A4 | 支持多种样式、自动分页 |
| 产品规格 | `render_product_spec()` | A4 | 支持表格数据 |
| 合同 | `render_contract()` | A4 | 双栏布局、甲乙方信息 |
| 发票 | `render_invoice()` | A4 | 表格明细、边框样式 |
| 分析报告 | `render_report()` | A4 | 封面、摘要、章节 |

#### 4.5.2 名片渲染参数

```python
def render_business_card(
    output_path: str,
    data: dict,                    # 名片数据字段
    logo_path: str = None,         # LOGO图片路径
    photo_path: str = None,        # 照片路径
    qr_image_path: str = None,     # 二维码路径
    style_options: dict = None,    # 样式选项
    bg_image_path: str = None,    # 背景图片
    bg_image_opacity: float = 50,  # 背景透明度
    bg_texture: str = "none",      # 纹理类型
    bg_custom_color: str = "",    # 自定义背景色
    text_color: str = "#2C3E50",   # 文字颜色
    text_secondary_color: str = "#7F8C8D",
    render_sides: list = None,    # ["front"] | ["front", "back"]
    progress_callback = None
) -> str
```

#### 4.5.3 辅助函数

```python
# 单位转换
_mm_to_points(mm: float) -> float    # 毫米转PDF点
_points_to_mm(pt: float) -> float    # PDF点转毫米

# 颜色转换
_hex_to_rgb(hex_color: str) -> tuple  # Hex转RGB
_hex_to_brightness(hex_color: str) -> float  # 计算亮度

# 文字处理
_insert_text_safe(page, text, x, y, fontsize, color, fontname)
_insert_text_centered(page, text, center_x, y, fontsize, width, color)
_measure_text_width(text, fontsize) -> float
_wrap_text_in_width(text, fontsize, max_width_pt) -> list

# 图片处理
_embed_image_in_page(page, image_path, x_mm, y_mm, width_mm, height_mm)
_embed_image_full_page(page, image_path, width_pt, height_pt, opacity)

# 纹理绘制
_draw_texture(page, width_pt, height_pt, texture_type, color)

# 字体
_get_cjk_font() -> fitz.Font  # 获取系统CJK字体
```

#### 4.5.4 CanvasModel 统一画布模型

```python
class CanvasModel:
    """
    统一的画布数据模型。
    同一份CanvasModel同时驱动预览和导出。
    """
    def __init__(self, template_id, side, fields, styles, assets, layout)

    def render_to_pixmap(self, target_width=560, dpi=2.5) -> QPixmap
        """渲染为QPixmap（用于预览）"""

    def render_to_pdf(self, output_path) -> str
        """渲染为PDF文件（用于导出）"""
```

#### 4.5.5 RenderContext 渲染上下文

```python
class RenderContext:
    """
    编辑器统一渲染上下文。
    一次serialize()锁定所有参数，同时驱动预览和导出。
    """
    def __init__(self, template_id, side, fields, styles, assets, layout)

    def to_canvas(self) -> CanvasModel
    def render_to_pixmap(self, target_width=560, dpi=2.5) -> QPixmap
    def render_to_pdf(self, output_path) -> str
    def debug_snapshot(self) -> dict
```

### 4.6 国际化系统 (translations/)

#### 4.6.1 翻译管理器 (translation_manager.py)

**类**: `TranslationManager`

**支持语言**:
- `zh_CN`: 简体中文
- `zh_TW`: 繁体中文
- `en_US`: 英文

**核心方法**:

```python
class TranslationManager:
    def register_page(self, page_instance, has_ui=True) -> None
        # 注册页面，语言切换时调用retranslateUi()

    def switch_language(self, locale_code: str) -> bool
        # 切换语言并重译所有已注册页面

    def _retranslate_all(self) -> None
        # 遍历已注册页面调用retranslateUi()
```

**快捷函数**:

```python
_(text: str) -> str    # 翻译文本
set_locale(locale: str) # 设置当前语言
get_locale() -> str     # 获取当前语言
```

### 4.7 路径管理 (src/common/paths.py)

**核心函数**:

```python
get_resource_root() -> str   # 获取资源根目录
    # 开发模式: 项目根目录
    # 打包模式: sys._MEIPASS

get_app_root() -> str        # 获取应用根目录
    # 开发模式: 项目根目录
    # 打包模式: exe所在目录

get_data_dir() -> str        # 获取用户数据目录
    # Windows: %APPDATA%/印流PDflow/
    # 其他: ~/.pdflow/

resource_path(*parts) -> str  # 拼接资源路径
data_path(*parts) -> str      # 拼接数据路径
```

### 4.8 最近文件管理 (src/common/recent_files_manager.py)

**核心函数**:

```python
add_record(file_path: str, action: str, output_path: str = None)
    # 添加历史记录，自动去重

get_recent_files(limit: int = 10) -> List[Dict]
    # 获取最近使用的文件列表

clear_records()
    # 清空所有历史记录

get_status_text(timestamp: float) -> str
    # 根据时间戳生成状态文本
    # "刚刚" / "5分钟前" / "昨天" / "3天前"
```

---

## 5. 页面模块详解

### 5.1 页面基类模式

所有页面遵循统一模式：

```python
class XxxPage(QWidget):
    # 信号定义
    signal_name = Signal(str)

    def __init__(self):
        super().__init__()
        self.ui = Ui_XxxPage()      # UI类实例
        self.ui.setupUi(self)       # 设置UI
        self._connect_signals()     # 连接信号

    def apply_theme(self, colors):
        """主题切换时更新样式"""
        self.setStyleSheet(f"background: {colors['bg']};")
        self.ui.apply_theme(colors)  # 传递到UI类

    def retranslateUi(self):
        """语言切换时更新文本"""
        pass

    def _connect_signals(self):
        """连接内部信号"""
        pass
```

### 5.2 首页 (pages/home_page.py)

**类**: `HomePage`, `Ui_HomePage`

**组件**:

| 组件 | 类 | 说明 |
|------|-----|------|
| 版本徽章 | `Badge` | 左侧绿色脉冲圆点 + 文字 |
| 光晕装饰 | `Glow` | 径向渐变背景装饰 |
| 功能卡片 | `FunctionCard` | 4个工具箱功能入口 |
| 步骤卡片 | `StepCard` | 快速上手3步流程 |
| 文件列表项 | `FileItem` | 最近使用文件列表 |
| 网格背景 | `GridBackground` | 背景网格线装饰 |
| 装饰色条 | `AccentStrip` | 悬停延伸的色条 |

**信号**:

```python
card_clicked = Signal(str)       # 卡片点击，参数: card_name
file_clicked = Signal(str, str)   # 文件点击，参数: nav_idx, file_path
```

**卡片映射**:
```python
CARD_TO_NAV = {
    "merge": 1,
    "compress": 2,
    "convert": 3,
    "watermark": 4,
}
```

### 5.3 合并拆分页面 (pages/merge_page.py)

**类**: `MergePage`, `Ui_MergePage`

**功能**:
- PDF文件合并（多文件拖拽排序）
- PDF拆分（按页或按范围）
- 页面重排序

### 5.4 压缩页面 (pages/compress_page.py)

**类**: `CompressPage`, `Ui_CompressPage`

**功能**:
- PDF压缩（高/中/低三种质量）
- 实时预览压缩效果

**压缩质量**:
```python
"high"   → 200DPI JPEG Q90  # 适合打印，预计减轻60-85%
"medium" → 150DPI JPEG Q75  # 适合阅读，预计减轻70-90%
"low"    → 72DPI  JPEG Q50  # 极致压缩，预计减轻90-97%
```

### 5.5 格式转换页面 (pages/convert_page.py)

**类**: `ConvertPage`, `Ui_ConvertPage`

**功能**:
- PDF转图片 (PNG/JPG等)
- 图片转PDF
- PDF转Word (.docx)
- PDF转Excel (.xlsx)
- PDF转PPT (.pptx)

### 5.6 水印页面 (pages/watermark_page.py)

**类**: `WatermarkPage`, `Ui_WatermarkPage`

**功能**:
- 添加文字水印
- 水印位置：居中/平铺
- 水印样式：字号、透明度、旋转角度、颜色

### 5.7 模板排版入口页 (pages/template_layout_page.py)

**类**: `TemplateLayoutPage`, `Ui_TemplateLayoutPage`

**职责**:
- 从 `assets/templates/` 加载JSON模板
- 以卡片网格展示可用模板
- 点击卡片弹出确认对话框
- 确认后发射信号打开编辑器

**信号**:

```python
editor_requested = Signal(str)  # 请求打开编辑器，参数: template_id
```

**模板JSON结构**:
```json
{
  "id": "business_card",
  "name": "商务名片",
  "description": "标准90×54mm商务名片",
  "type": "商务",
  "icon": "🎴",
  "fields": [...],
  "style_options": {...}
}
```

### 5.8 模板编辑器页面 (pages/template_editor_page.py)

**类**: `TemplateEditorPage`, `Ui_TemplateEditorPage`

**职责**:
- 表单输入（根据模板字段动态生成）
- 样式选项配置
- 实时预览
- 导出PDF

### 5.9 设置页面 (pages/settings_page.py)

**类**: `SettingsPage`, `Ui_SettingsPage`

**设置项**:
- 主题切换（深色/浅色）
- 语言切换
- 开发者模式

**信号**:

```python
developer_mode_changed = Signal(bool)  # 开发者模式切换
language_changed = Signal(str)          # 语言切换
```

---

## 6. 关键类与函数API

### 6.1 主题系统API

#### ThemeManager

```python
class ThemeManager(QObject):
    theme_changed = Signal(str)  # 参数: "dark" | "light"

    def apply_theme(self, theme: str = None, app=None) -> None
    def register_page(self, widget) -> None
    def unregister_page(self, widget) -> None
    def get_qss(self, theme: str = None) -> str
    def toggle(self, app=None) -> None

    @property
    def current_theme(self) -> str
    def is_dark(self) -> bool
```

#### 颜色获取

```python
# theme.py
DARK_COLORS: dict    # 深色配色字典
LIGHT_COLORS: dict   # 浅色配色字典

def get_colors(theme=None) -> dict
def get_current_theme() -> str
def set_theme(theme: str) -> None
```

### 6.2 PDF API

```python
# 信息读取
def get_pdf_info(file_path: str) -> dict
    # 返回: {"pages": N, "size_mb": M, "title": ""}

# 合并拆分
def merge_pdfs(output_path: str, *filepaths, progress_callback=None) -> dict
def split_pdf(filepath: str, output_dir: str, mode: str, range_str: str, progress_callback=None) -> dict

# 压缩
def compress_pdf(input_path: str, quality: str, output_path: str,
                 progress_callback=None, timeout: int = 60) -> dict

# 转换
def pdf_to_images(input_path: str, output_dir: str = None, dpi: int = 150, fmt: str = "png") -> dict
def images_to_pdf(image_paths: list, output_path: str = None,
                  orientation: str = "portrait", quality: str = "high") -> dict
def pdf_to_word(input_path: str, output_path: str = None) -> dict
def pdf_to_excel(input_path: str, output_path: str = None) -> dict
def pdf_to_ppt(input_path: str, output_dir: str = None) -> dict

# 水印
def add_watermark(input_path: str, wm_text: str, output_path: str = None,
                  font_size: int = 60, opacity: float = 0.15,
                  rotation: int = -45, color: tuple = (128, 128, 128),
                  position: str = "center") -> dict

# 页面操作
def reorder_pdf_pages(input_path: str, page_order: str, output_path: str = None) -> dict

# OCR
def ocr_extract_text(input_path: str, progress_callback=None) -> dict

# 批量处理
def batch_convert(input_path: str, output_dir: str = None, batch_fmt: str = "pdf",
                  progress_callback=None, timeout: int = 60) -> dict
def batch_merge_pdfs(file_groups: list, output_dir: str, progress_callback=None) -> dict
def batch_compress_pdfs(file_paths: list, output_dir: str, quality: str = "high",
                         progress_callback=None, timeout: int = 60) -> dict
```

### 6.3 模板渲染API

```python
# 统一入口
def render_template(template_id: str, output_path: str, data: dict, **kwargs) -> str

# 名片
def render_business_card(
    output_path: str, data: dict,
    logo_path: str = None, photo_path: str = None, qr_image_path: str = None,
    style_options: dict = None,
    bg_image_path: str = None, bg_image_opacity: float = 50,
    bg_texture: str = "none", bg_custom_color: str = "",
    text_color: str = "#2C3E50", text_secondary_color: str = "#7F8C8D",
    render_sides: list = None, progress_callback = None
) -> str

# 公告
def render_notice(output_path: str, data: dict, image_path: str = None,
                  style: dict = None, progress_callback=None) -> str

# 产品规格
def render_product_spec(output_path: str, data: dict, image_path: str = None,
                        style: dict = None, progress_callback=None) -> str

# 合同
def render_contract(output_path: str, data: dict, image_path: str = None,
                    style: dict = None, progress_callback=None) -> str

# 发票
def render_invoice(output_path: str, data: dict, image_path: str = None,
                   style: dict = None, progress_callback=None) -> str

# 分析报告
def render_report(output_path: str, data: dict, image_path: str = None,
                  style: dict = None, progress_callback=None) -> str
```

### 6.4 国际化API

```python
# 快捷翻译
def _(text: str) -> str

# 翻译管理器
class TranslationManager:
    def register_page(self, page_instance, has_ui=True) -> None
    def switch_language(self, locale_code: str) -> bool

# 语言设置
def set_locale(locale: str) -> None
def get_locale() -> str
```

### 6.5 路径API

```python
def resource_path(*parts) -> str  # 资源文件路径
def data_path(*parts) -> str      # 用户数据路径
def get_resource_root() -> str     # 资源根目录
def get_data_dir() -> str          # 数据目录
```

### 6.6 最近文件API

```python
def add_record(file_path: str, action: str, output_path: str = None) -> None
def get_recent_files(limit: int = 10) -> List[Dict]
def clear_records() -> None
def get_status_text(timestamp: float) -> str
```

---

## 7. 依赖关系图

### 7.1 模块依赖关系

```
run_main.py
├── pages/main_window.py
│   └── src/common/theme.py
├── pages/home_page.py
│   ├── src/common/recent_files_manager.py
│   └── translations/translation_manager.py
├── pages/merge_page.py
│   └── src/common/pdf_api.py
├── pages/compress_page.py
│   └── src/common/pdf_api.py
├── pages/convert_page.py
│   └── src/common/pdf_api.py
├── pages/watermark_page.py
│   └── src/common/pdf_api.py
├── pages/template_layout_page.py
│   └── src/common/paths.py
├── pages/template_editor_page.py
│   ├── src/common/template_renderer.py
│   └── src/common/pdf_api.py
├── pages/settings_page.py
│   └── src/common/theme_manager.py
└── src/common/theme_manager.py
    ├── src/common/theme.py
    ├── src/common/paths.py
    └── src/common/theme_tokens.py
```

### 7.2 第三方依赖

| 包名 | 用途 |
|------|------|
| PySide6 | Qt GUI框架 |
| PyMuPDF (fitz) | PDF处理核心 |
| Pillow | 图像处理 |
| pdf2docx | PDF转Word |
| pdfplumber | PDF表格提取 |
| pandas | Excel数据处理 |
| openpyxl | Excel文件读写 |
| python-pptx | PPT生成 |

---

## 8. 项目运行方式

### 8.1 开发环境运行

```bash
# 1. 进入项目目录
cd e:\印流PDflow项目

# 2. 激活虚拟环境
.\pyside6_env\Scripts\activate

# 3. 运行主程序
python run_main.py
```

### 8.2 打包发布

```bash
# 使用PyInstaller打包
pyinstaller PDflow_V1.1-RC1.spec
```

### 8.3 开发环境配置

```bash
# 创建虚拟环境
python -m venv pyside6_env

# 安装依赖
pip install PySide6 PyMuPDF Pillow pdf2docx pdfplumber pandas openpyxl python-pptx
```

---

## 9. 开发规范

### 9.1 代码规范

1. **文件编码**: UTF-8
2. **缩进**: 4个空格
3. **行长度**: 不超过100字符
4. **导入顺序**: 标准库 → 第三方库 → 本地模块
5. **文档字符串**: 类和公共函数必须添加docstring

### 9.2 UI开发规范

1. **页面类命名**: `XxxPage`
2. **UI类命名**: `Ui_XxxPage`
3. **必须实现方法**:
   - `apply_theme(colors)`: 响应主题切换
   - `retranslateUi()`: 响应语言切换

### 9.3 主题开发规范

1. 使用 `ThemeManager` 注册页面
2. 在 `apply_theme()` 中更新所有内联样式
3. 使用 `theme.py` 中定义的配色Token
4. 避免硬编码颜色值

### 9.4 信号命名规范

```python
# 使用描述性动词+过去式
card_clicked = Signal(str)
file_clicked = Signal(str, str)
editor_requested = Signal(str)
theme_changed = Signal(str)
language_changed = Signal(str)
```

---

## 10. 附录

### 10.1 配置文件说明

**config.json** (用户数据目录):

```json
{
  "theme": "dark",
  "language": "zh_CN",
  "developer_mode": false
}
```

**app_config.json** (应用配置):

```json
{
  "theme": "dark"
}
```

### 10.2 模板JSON格式

```json
{
  "id": "template_id",
  "name": "模板名称",
  "description": "模板描述",
  "type": "分类",
  "icon": "emoji图标",
  "fields": [
    {
      "key": "field_key",
      "label": "字段标签",
      "type": "text|textarea|image",
      "required": true
    }
  ],
  "style_options": {
    "theme_color": "#4D7CFE",
    "bar_position": "left"
  }
}
```

### 10.3 最近文件记录格式

```json
{
  "file_name": "example.pdf",
  "file_path": "C:/Users/.../example.pdf",
  "action": "merge|compress|convert|watermark",
  "datetime": "2026-06-08 10:30",
  "timestamp": 1751521800
}
```

### 10.4 相关文档索引

| 文档 | 路径 | 说明 |
|------|------|------|
| 项目总章程 | `04-项目文档/印流PDflow_项目总章程_V2.5.md` | 最高约束文档 |
| UI设计规范 | `04-项目文档/DESIGN.md` | 配色、组件规范 |
| 代码审查规范 | `04-项目文档/CODE_REVIEW.md` | 审查流程与标准 |
| PM Agent规则 | `04-项目文档/PM_SOUL.md` | PM Agent行为准则 |

---

**文档结束**

*本文档由 AI 自动分析项目代码生成，如有疑问请参考项目总章程或咨询项目负责人。*
