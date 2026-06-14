# -*- mode: python ; coding: utf-8 -*-
# ============================================================
# 印流PDflow V1.1-RC2 打包 spec（WebEngine 恢复版）
# ============================================================
# 相对 RC2.spec 变更（2026-06-13）：
#   ✅ 恢复 WebEngine 全家，仅用于预览链路
#   - 删除 PySide6.QtWebEngineCore / Quick / Widgets / WebChannel excludes
#   - 显式 collect_data_files / collect_dynamic_libs 恢复：
#       DLLs:
#         Qt6WebEngineCore.dll
#         Qt6WebEngineQuick.dll
#         Qt6WebEngineWidgets.dll
#         Qt6WebChannel.dll
#         Qt6WebSockets.dll
#         Qt6WebView.dll
#       资源:
#         qtwebengine_resources.pak
#         qtwebengine_resources_100p.pak
#         qtwebengine_resources_200p.pak
#         qtwebengine_locales/
#         icudtl.dat
#         v8_context_snapshot.bin
#   - 其余排除：cv2 / OpenCV / tkinter / PIL 高级插件
#   - 已恢复：pdfminer（pdfplumber依赖）、QtQuick/QtQml（WebEngineQuick渲染管线）
# 体积预估：300-360 MB（WebEngine 加 80-130 MB）
# ============================================================

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(r"E:\印流PDflow项目")
APP_NAME = "PDflow_V1.1-RC2"
ICON_PATH = str(PROJECT_ROOT / "assets" / "pdflow-logo.ico")

# UPX 路径
UPX_DIR = str(PROJECT_ROOT / "build" / "upx" / "upx-4.2.4-win64")

from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

# WebEngine DLLs + 资源（恢复预览链路）
webengine_datas = collect_data_files("PySide6.QtWebEngineCore", includes=["*.pak", "*.dat", "*.bin", "*.pak.info"])
# v1.1-patch: 显式收集 qtwebengine_locales 子目录中的语言包（默认 collect_data_files 不会进子目录）
webengine_locales_datas = collect_data_files("PySide6.QtWebEngineCore", includes=["qtwebengine_locales/*.pak"])
# v1.1-patch: 显式收集 qt.conf（WebEngine 自己的 Qt 配置，与主程序 qt.conf 区分）
webengine_qtconf_datas = collect_data_files("PySide6.QtWebEngineCore", includes=["qt.conf"])
webengine_binaries = collect_dynamic_libs("PySide6.QtWebEngineCore")
webchannel_datas = collect_data_files("PySide6.QtWebChannel", includes=["*.pak", "*.dat", "*.bin"])
webchannel_binaries = collect_dynamic_libs("PySide6.QtWebChannel")

a = Analysis(
    [str(PROJECT_ROOT / "run_main.py")],
    pathex=[
        str(PROJECT_ROOT),
        str(PROJECT_ROOT / "pages"),
        str(PROJECT_ROOT / "src"),
        str(PROJECT_ROOT / "src" / "common"),
        str(PROJECT_ROOT / "translations"),
    ],
    binaries=webengine_binaries + webchannel_binaries,
    datas=[
        # 业务资源（必含）
        (str(PROJECT_ROOT / "pages" / "global.qss"), "pages"),
        (str(PROJECT_ROOT / "assets" / "templates"), "assets/templates"),
        # Logo 资源
        (str(PROJECT_ROOT / "assets" / "pdflow-logo.png"), "assets"),
        (str(PROJECT_ROOT / "assets" / "pdflow-logo.ico"), "assets"),
        # 导航图标（SVG 经 QtSvg 渲染，必须保留）
        (str(PROJECT_ROOT / "assets" / "icons"), "assets/icons"),
        # 项目源码
        (str(PROJECT_ROOT / "pages"), "pages"),
        # WebEngine 资源
        *webengine_datas,
        *webengine_locales_datas,
        *webengine_qtconf_datas,
        *webchannel_datas,
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
        # 恢复 WebEngine 相关 hidden imports（v1.1-patch: 显式注入，不依赖 collect_all）
        "PySide6.QtWebEngineCore",
        "PySide6.QtWebEngineQuick",
        "PySide6.QtWebEngineWidgets",
        "PySide6.QtWebChannel",
        "PySide6.QtWebSockets",
        # PDF 转换依赖（PDF→Word / PDF→Excel）
        "pdf2docx",
        "pdfplumber",
        "openpyxl",
        "docx",
    ],
    excludes=[
        # ✅ WebEngine 排除项已全部移除
        # "PySide6.QtWebEngineCore",       ← 已恢复
        # "PySide6.QtWebEngineQuick",      ← 已恢复（QWebEngineView 依赖）
        # "PySide6.QtWebEngineWidgets",    ← 已恢复
        # "PySide6.QtWebChannel",          ← 已恢复
        "PySide6.QtScript",  # 仍排除（不在预览链路）

        # ----- OpenCV -----
        # cv2 不再排除（pdf2docx.common.algorithm 顶层 import cv2）
        # "cv2",
        # "cv2.cv2",

        # ----- 隐式但 0 处 import 的包 -----
        # cryptography 不再排除（pdfminer/pdfplumber PDF→Excel 依赖）
        # "cryptography",
        # "cryptography.hazmat",
        # "cryptography.hazmat.bindings",
        # pdfminer 不再排除（pdfplumber PDF→Excel 依赖）
        # "pdfminer",
        # "pdfminer.high_level",
        "pypdfium2",
        "pypdfium2_raw",
        "scipy",

        # ----- Qt Quick / QML / 3D / PDF / Shader -----
        # QtQuick/QtQml 不再排除（WebEngineQuick 渲染管线依赖）
        # "PySide6.QtQuick",
        # "PySide6.QtQml",
        "PySide6.QtQuick3D",
        "PySide6.QtPdf",
        "PySide6.QtPdfWidgets",
        "PySide6.Qt3DCore",
        "PySide6.Qt3DRender",
        "PySide6.QtShaderTools",

        # ----- Qt 多媒体 / 位置 / 蓝牙 -----
        "PySide6.QtMultimedia",
        "PySide6.QtMultimediaWidgets",
        # PySide6.QtPositioning 不再排除（WebEngineCore 依赖）
        "PySide6.QtLocation",
        "PySide6.QtSensors",
        "PySide6.QtCharts",
        "PySide6.QtDataVisualization",
        "PySide6.QtSerialPort",
        "PySide6.QtBluetooth",
        "PySide6.QtTest",
        "PySide6.QtDesigner",
        "PySide6.QtHelp",
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
    upx=True,
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
    upx=True,
    name=APP_NAME,
)
