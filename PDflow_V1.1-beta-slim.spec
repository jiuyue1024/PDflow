# -*- mode: python ; coding: utf-8 -*-
# ============================================================
# 印流PDflow V1.1-beta 瘦身版 spec
# 生成日期：2026-06-12
# 实施范围：A 类 + 部分 B 类（不实施 A+ DLL 大清洗）
#
# 实施项（与用户确认一致）：
#   [A]   Python module 层 excludes
#         - pdfminer / pdfminer.high_level         (~8 MB)
#         - pypdfium2 / pypdfium2_raw              (~7 MB)
#         - cryptography / cryptography.hazmat     (~9 MB) - 已撤销（cv2 需要）
#         - PIL._avif / _webp / _imaging_jp2 / _imaging_tiff
#
#   [B-部分]  小型 binaries hook 文件级过滤
#         - PySide6/translations/qt_*.qm（保留 zh_CN/zh_TW/en）
#         - PySide6/plugins/imageformats/（保留 jpeg/png/svg）
#         - .dist-info/ 元数据
#
#   [不实施]  A+ DLL 大清洗：Qt6Quick*.dll / Qt6Qml*.dll / Qt6Pdf*.dll /
#             opengl32sw.dll / Qt6OpenGL.dll / QtOpenGL.pyd / 3D / Charts / 等
#             （保持 QtWidgets / QtGui / QtCore 隐式依赖的 DLL 不变）
#
#   [必须保留功能]  ── 用户验收：所有功能必须工作
#         - 模板排版预览：依赖 PySide6.QtWebEngineCore 全家 + WebEngine resources
#         - 格式转换 PDF→Word：依赖 pdf2docx → cv2（必须）+ tkinter（间接）
#         - 格式转换 PDF→Excel：依赖 pdfplumber + pandas + openpyxl
#
# 预估结果：797.81 MB → ~770 MB（保留所有功能 + cv2 + pdfplumber + openpyxl）
# ============================================================

import os
from pathlib import Path

# ------------------------------------------------------------
# 小型 deny-list（仅用于文件级过滤，不动 A+ 范围）
# 注意：WebEngine 相关资源/翻译 必须保留（用于模板预览功能）
# ------------------------------------------------------------

# qtwebengine_locales 整目录 - 必须保留
def is_qtwebengine_locales(name: str) -> bool:
    return "qtwebengine_locales" in name

# qt 多语言翻译保留名单（项目只支持 zh_CN / zh_TW / en）
# 注：不再过滤 WebEngine 翻译，因为模板预览需要 WebEngine 全套资源
QM_KEEP = {
    "qt_zh_CN.qm", "qt_zh_TW.qm", "qt_en.qm",
    "qtbase_zh_CN.qm", "qtbase_zh_TW.qm", "qtbase_en.qm",
    "qt_help_zh_CN.qm", "qt_help_en.qm",
}

# imageformats 保留名单
IMAGEFORMAT_KEEP = {"qjpeg.dll", "qpng.dll", "qsvg.dll"}


def filter_binaries(binaries):
    """小型 hook：过滤多语言 / 图像格式 / dist-info（tkinter C++ 也保留）"""
    kept = []
    for name, src, kind in binaries:
        base = os.path.basename(name)
        normalized = name.replace("\\", "/")

        # 1) WebEngine locales - 保留（不删除）

        # 2) PySide6 多语言翻译（仅保留 6 个；WebEngine 翻译通过 #1 保留）
        if base.startswith("qt_") and base.endswith(".qm"):
            if base not in QM_KEEP:
                continue

        # 3) imageformats 插件精简
        if "/imageformats/" in normalized:
            if base not in IMAGEFORMAT_KEEP:
                continue

        # 4) .dist-info 元数据（运行时不需要）
        if ".dist-info" in normalized and kind == "DATA":
            continue

        # 5) tkinter C++ 运行时 - 保留（cv2 间接依赖）
        #    （之前 deny，现已恢复 tkinter）

        kept.append((name, src, kind))
    return kept


# ------------------------------------------------------------
# PyInstaller Analysis
# ------------------------------------------------------------

from PyInstaller.utils.hooks import collect_submodules

hiddenimports = [
    'src.common.theme_manager', 'src.common.theme', 'src.common.paths',
    'src.common.config', 'src.common.error_handler', 'src.common.ocr_provider',
    'src.common.template_renderer', 'src.common.pdf_api',
    'src.common.recent_files_manager', 'src.common.render_product_spec_patched',
    'src.common.legacy_watermark', 'translations.translation_manager',
    # 模板预览必须
    'PySide6.QtWebEngineCore',
    'PySide6.QtWebEngineWidgets',
    'PySide6.QtWebEngineQuick',
    'PySide6.QtWebChannel',
    'PySide6.QtPrintSupport',
    # 格式转换必须 - PDF→Word 依赖
    'pdf2docx',
    # 格式转换必须 - PDF→Excel 依赖
    'pdfplumber',
    'openpyxl',
    'et_xmlfile',
    # cv2（pdf2docx 必需） - 通过 collect_submodules 拉入
]
hiddenimports += collect_submodules('src.common')
hiddenimports += collect_submodules('translations')
# pdf2docx 有 11 个子模块（common/converter/font/gui/image/layout/main/page/shape/table/text）
# 仅在 hiddenimports 中加 'pdf2docx' 不够，必须 collect_submodules 拉全
try:
    hiddenimports += collect_submodules('pdf2docx')
except Exception:
    pass
# pdfplumber 同理
try:
    hiddenimports += collect_submodules('pdfplumber')
except Exception:
    pass
# openpyxl 子模块
try:
    hiddenimports += collect_submodules('openpyxl')
except Exception:
    pass
# cv2 是 OpenCV Python wrapper，内部有大量子模块
try:
    hiddenimports += collect_submodules('cv2')
except Exception:
    pass


a = Analysis(
    ['run_main.py'],
    pathex=['pages', 'src', 'src/common', 'translations'],
    binaries=[],
    datas=[
        ('pages', 'pages'),
        ('assets/templates', 'assets/templates'),
        ('assets/pdflow-logo.png', 'assets'),
        ('02-素材资源/assets/pdflow-logo-48.png', '02-素材资源/assets'),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # ===== A 类：Python module 层 excludes =====

        # pdfminer（隐式但项目 0 处 import）
        'pdfminer', 'pdfminer.high_level',

        # pypdfium2（隐式但项目 0 处 import）
        'pypdfium2', 'pypdfium2_raw',

        # scipy（项目 0 处 import）
        'scipy',

        # ----- PIL 高级插件（项目 0 处使用）-----
        'PIL._avif',
        'PIL._webp',
        'PIL._imaging_jp2',
        'PIL._imaging_tiff',
        'PIL._imaging_ft',
        'PIL._imaging_psd',
        'PIL._imaging_wmf',
        'PIL._imaging_xpm',

        # 注意：以下不在 A 范围，**不列入** excludes：
        # - cv2（PDF→Word 必须）
        # - tkinter（cv2 / pdf2docx 间接依赖）
        # - cryptography（cv2 间接依赖）
        # - PySide6.QtWebEngineCore / Quick / Widgets（必须保留，模板预览依赖）
        # - PySide6.QtQuick / QtQml / QtPdf / Qt3D / QtMultimedia
        # - PySide6.QtCharts / QtDataVisualization / QtShaderTools
        # - PySide6.QtPositioning / QtLocation / QtSensors / QtSerialPort
        # - PySide6.QtDesigner / QtHelp / QtTest
        # - PySide6.QtSvgWidgets / QtXml / QtXmlPatterns / QtNetworkAuth
    ],
    noarchive=False,
    optimize=0,
)

# 在 PYZ 之前应用小型 hook 过滤
a.binaries = filter_binaries(a.binaries)
a.datas    = filter_binaries(a.datas)


pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PDflow_V1.1-beta-slim',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
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
    upx_exclude=[],
    name='PDflow_V1.1-beta-slim',
)
