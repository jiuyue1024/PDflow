# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = ['src.common.theme_manager', 'src.common.theme', 'src.common.paths', 'src.common.config', 'src.common.error_handler', 'src.common.ocr_provider', 'src.common.template_renderer', 'src.common.pdf_api', 'src.common.recent_files_manager', 'src.common.render_product_spec_patched', 'src.common.legacy_watermark', 'translations.translation_manager']
hiddenimports += collect_submodules('src.common')
hiddenimports += collect_submodules('translations')


a = Analysis(
    ['run_main.py'],
    pathex=['pages', 'src', 'src/common', 'translations'],
    binaries=[],
    datas=[('pages', 'pages'), ('assets/templates', 'assets/templates'), ('assets/pdflow-logo.png', 'assets'), ('02-素材资源/assets/pdflow-logo-48.png', '02-素材资源/assets')],
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
    name='PDflow_V1.1-beta',
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
    name='PDflow_V1.1-beta',
)
