# -*- mode: python ; coding: utf-8 -*-
"""Project-relative PyInstaller configuration for the internal vNext Beta."""

from pathlib import Path

from PyInstaller.utils.hooks import collect_all, collect_submodules


ROOT = Path(SPEC).resolve().parent

rapid_datas, rapid_binaries, rapid_hidden = collect_all("rapidocr_onnxruntime")
web_datas, web_binaries, web_hidden = collect_all("PySide6.QtWebEngineCore")
webchannel_datas, webchannel_binaries, webchannel_hidden = collect_all("PySide6.QtWebChannel")

hiddenimports = (
    collect_submodules("src.common")
    + collect_submodules("translations")
    + rapid_hidden
    + web_hidden
    + webchannel_hidden
    + [
        "pdfplumber",
        "openpyxl",
        "pytesseract",
        "PySide6.QtWebEngineCore",
        "PySide6.QtWebEngineWidgets",
        "PySide6.QtWebChannel",
    ]
)

datas = [
    (str(ROOT / "pages" / "global.qss"), "pages"),
    (str(ROOT / "pages" / "dark.qss"), "pages"),
    (str(ROOT / "pages" / "light.qss"), "pages"),
    (str(ROOT / "pages" / "global.qss.template"), "pages"),
    (str(ROOT / "assets"), "assets"),
]
optional_logo = ROOT / "02-素材资源" / "assets"
if optional_logo.is_dir():
    datas.append((str(optional_logo), "02-素材资源/assets"))
datas += rapid_datas + web_datas + webchannel_datas

a = Analysis(
    [str(ROOT / "run_main.py")],
    pathex=[str(ROOT)],
    binaries=rapid_binaries + web_binaries + webchannel_binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="PDflow_vNext_Beta",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    icon=str(ROOT / "assets" / "pdflow-logo.ico"),
    disable_windowed_traceback=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="PDflow_vNext_Beta",
)
