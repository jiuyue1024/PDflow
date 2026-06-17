# -*- mode: python ; coding: utf-8 -*-
# ============================================================
# 印流PDflow V1.1 RC1 打包 spec
# ============================================================
# 体积目标：≤ 250 MB
# 排除规则（V1.1 RC 验证通过）：
#   - Qt WebEngine 全家
#   - cv2 / OpenCV
#   - cryptography / pdfminer / pypdfium2
#   - PIL._avif / _webp / _imaging_jp2 / _imaging_tiff
#   - tkinter
# 保留：PySide6.QtSvg（main_window.py 依赖 QSvgRenderer）
# ============================================================

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(r"F:\印流PDflow项目")
APP_NAME = "PDflow_V1.1-RC1"
ICON_PATH = str(PROJECT_ROOT / "assets" / "pdflow-logo.ico")

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
        # Logo 资源（修复后统一用 assets/pdflow-logo.png，V1.1 RC1 严格匹配）
        (str(PROJECT_ROOT / "assets" / "pdflow-logo.png"), "assets"),
        (str(PROJECT_ROOT / "assets" / "pdflow-logo.ico"), "assets"),
        # 导航图标（SVG 经 QtSvg 渲染，必须保留）
        (str(PROJECT_ROOT / "assets" / "icons"), "assets/icons"),
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
        "src.common.preview_renderer",
        "src.common.pdf_api",
        "src.common.recent_files_manager",
        "src.common.render_product_spec_patched",
        "src.common.legacy_watermark",
        "translations.translation_manager",
    ],
    excludes=[
        # ----- Qt WebEngine 全家 -----
        "PySide6.QtWebEngineCore",
        "PySide6.QtWebEngineQuick",
        "PySide6.QtWebEngineWidgets",
        "PySide6.QtWebChannel",
        "PySide6.QtScript",

        # ----- OpenCV -----
        "cv2",
        "cv2.cv2",

        # ----- 隐式但 0 处 import 的包 -----
        "cryptography",
        "cryptography.hazmat",
        "cryptography.hazmat.bindings",
        "pdfminer",
        "pdfminer.high_level",
        "pypdfium2",
        "pypdfium2_raw",
        "scipy",

        # ----- Qt Quick / QML / 3D / PDF / Shader -----
        "PySide6.QtQuick",
        "PySide6.QtQuick3D",
        "PySide6.QtQml",
        "PySide6.QtPdf",
        "PySide6.QtPdfWidgets",
        "PySide6.Qt3DCore",
        "PySide6.Qt3DRender",
        "PySide6.QtShaderTools",

        # ----- Qt 多媒体 / 位置 / 蓝牙 -----
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
        # 注意：不排除 PySide6.QtSvg（main_window.py 依赖）
        "PySide6.QtSvgWidgets",
        "PySide6.QtXml",
        "PySide6.QtXmlPatterns",
        "PySide6.QtNetworkAuth",

        # ----- tkinter -----
        "tkinter",
        "_tkinter",
        "tkinter.ttk",

        # ----- PIL 高级格式插件 -----
        "PIL._avif",
        "PIL._webp",
        "PIL._imaging_jp2",
        "PIL._imaging_tiff",
        "PIL._imaging_ft",
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
    upx=False,
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
    upx=False,
    name=APP_NAME,
)
