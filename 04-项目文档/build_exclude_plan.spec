# -*- mode: python ; coding: utf-8 -*-
# ============================================================
# 印流PDflow V1.2 打包优化方案（仅方案，未执行）
# ============================================================
#
# 当前体积：799 MB
# 目标体积：≤ 150 MB
# 理论下限：~360 MB（不修改业务代码）
# 优化策略：组合 A 类 exclude + UPX + 文件级 exclude
#
# 禁止项：删除代码 / 修改业务逻辑 / 继续打包
# ============================================================

import os
import sys
from pathlib import Path

# ============================================================
# 基础配置
# ============================================================
PROJECT_ROOT = Path(__file__).parent.resolve()
APP_NAME = "PDflow_V1.1-beta"
ICON_PATH = str(PROJECT_ROOT / "02-素材资源" / "pdflow-icon.ico")

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
        # 业务资源（必含）
        (str(PROJECT_ROOT / "pages" / "global.qss"), "pages"),
        (str(PROJECT_ROOT / "assets" / "templates"), "assets/templates"),
        (str(PROJECT_ROOT / "assets" / "pdflow-logo.png"), "assets"),
        (str(PROJECT_ROOT / "02-素材资源" / "assets" / "pdflow-logo-48.png"), "02-素材资源/assets"),
        # 项目源码（确保被作为模块暴露，避免 ImportError）
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
    # ============================================================
    # A 类：低风险 exclude（理论可减 ~438 MB）
    # ============================================================
    excludes=[
        # ----- Qt WebEngine 全家（278 MB）-----
        "PySide6.QtWebEngineCore",
        "PySide6.QtWebEngineQuick",
        "PySide6.QtWebEngineWidgets",
        "PySide6.QtWebChannel",
        "PySide6.QtScript",

        # ----- OpenCV（98 MB）-----
        "cv2",
        "cv2.cv2",

        # ----- 隐式但 0 处 import 的包（23.8 MB）-----
        "cryptography",
        "cryptography.hazmat",
        "cryptography.hazmat.bindings",
        "pdfminer",
        "pdfminer.high_level",
        "pypdfium2",
        "pypdfium2_raw",
        "scipy",

        # ----- Qt Quick / QML / 3D / PDF / Shader（24 MB）-----
        "PySide6.QtQuick",
        "PySide6.QtQuick3D",
        "PySide6.QtQml",
        "PySide6.QtPdf",
        "PySide6.QtPdfWidgets",
        "PySide6.Qt3DCore",
        "PySide6.Qt3DRender",
        "PySide6.QtShaderTools",

        # ----- Qt 多媒体 / 位置 / 蓝牙（项目不用）-----
        "PySide6.QtMultimedia",
        "PySide6.QtMultimediaWidgets",
        "PySide6.QtPositioning",
        "PySide6.QtLocation",
        "PySide6.QtSensors",
        "PySide6.QtCharts",
        "PySide6.QtDataVisualization",
        "PySide6.QtSerialPort",
        "PySide6.QtBluetooth",
        "PySide6.QtTest",
        "PySide6.QtDesigner",
        "PySide6.QtHelp",
        "PySide6.QtSvg",
        "PySide6.QtSvgWidgets",
        "PySide6.QtXml",
        "PySide6.QtXmlPatterns",
        "PySide6.QtNetworkAuth",

        # ----- tkinter 三件套（6.3 MB）-----
        "tkinter",
        "_tkinter",
        "tkinter.ttk",

        # ----- PIL 高级格式插件（项目只用 JPG/PNG）-----
        # AVIF 解码：PIL._avif.cp312-win_amd64.pyd 7.5 MB
        "PIL._avif",
        # WebP 解码（项目不用）
        "PIL._webp",
        # JPEG2000（项目不用）
        "PIL._imaging_jp2",
        # TIFF（项目不用）
        "PIL._imaging_tiff",
        # 字体子集化（项目不用）
        "PIL._imaging_ft",
        # PSD/WMF/XPM（项目不用）
        "PIL._imaging_psd",
        "PIL._imaging_wmf",
        "PIL._imaging_xpm",
    ],
    noarchive=False,
)

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
    upx=True,            # ★ 启用 UPX 压缩（额外减 30-50%）
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
    upx=True,            # ★ 启用 UPX
    upx_exclude=[
        # 大型原生 DLL UPX 压缩收益小、启动慢
        "python312.dll",
        "Qt6Core.dll",
        "Qt6Gui.dll",
        "Qt6Widgets.dll",
        "mupdfcpp64.dll",
    ],
    name=APP_NAME,
)

# ============================================================
# 预计效果（基于 V1.1-beta 当前 799 MB 实测）
# ============================================================
#
# 阶段一：仅 exclude（不启用 UPX）
#   - Qt WebEngine:    -278 MB
#   - cv2:              -98 MB
#   - Qt Quick/QML/Pdf/3D/Shader:  -24 MB
#   - cryptography/pdfminer/pypdfium2:  -24 MB
#   - tkinter:          -6 MB
#   - PIL 高级插件:     -7.5 MB
#   ─────────────────────────────
#   小计：-437 MB
#   预计体积：~360 MB
#
# 阶段二：阶段一 + UPX 压缩
#   - UPX 对 .pyd/.dll 压缩比约 50-70%
#   - 主要压缩目标：PySide6/*.pyd, numpy/.pyd, pymupdf/_mupdf.pyd
#   - 预计再减 80-120 MB
#   ─────────────────────────────
#   预计体积：~220-280 MB
#
# 阶段三（V1.2，需要业务侧重构，超出本 spec 范围）：
#   - pdf_api 弃用 PIL：-5 MB
#   - pdf_api 弃用 pandas：-16 MB
#   - 替换 numpy 为更小替代：-26 MB
#   ─────────────────────────────
#   预计体积：~170-230 MB
#
# ============================================================
# 已知风险
# ============================================================
#
# 1. PyInstaller 6.11+ 会强制拉回部分 transitive dependency
#    → 若 EXE 启动报 ImportError，移除对应 exclude 项
#
# 2. UPX 压缩在部分 AV 软件下被误报
#    → 若发布渠道过严，关闭 upx=True
#
# 3. cryptography/pdfminer/pypdfium2 是 pymupdf 的可选依赖
#    → 需实测 PDF 渲染正常后才可移除
#    → 验证命令：python -c "import fitz; doc=fitz.open(); print('OK')"
#
# 4. PIL 插件排除后某些边界 PDF 转换可能失败
#    → 回归测试 PDF→JPG 全场景
#
# ============================================================
# 验证清单（实施后必须跑）
# ============================================================
#
# □ EXE 启动 ≤ 3 秒
# □ 首页加载
# □ 6 个模板渲染（business_card/notice/product_spec/contract/invoice/report）
# □ 合并 / 拆分 / 压缩 / 转换 / 水印 5 个功能
# □ 主题切换
# □ 语言切换（zh_CN/zh_TW/en_US）
# □ PDF 转图片（PIL 仍在，需测）
# □ 体积 ≤ 360 MB（无 UPX）/ ≤ 250 MB（启用 UPX）
#
# ============================================================
# 禁止项
# ============================================================
#
# ❌ 删除业务代码
# ❌ 修改 pdf_api.py / template_renderer.py / 各 page
# ❌ 替换 pymupdf / numpy / PySide6 三个核心库
# ❌ 跑 pyinstaller（仅生成方案，不执行）
#
