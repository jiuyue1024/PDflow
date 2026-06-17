import os
base = r'E:\印流PDflow项目\dist\PDflow_V1.1-RC2\_internal'
checks = [
    'PySide6/QtWebEngineProcess.exe',
    'PySide6/resources/qtwebengine_resources.pak',
    'PySide6/resources/qtwebengine_resources_100p.pak',
    'PySide6/resources/qtwebengine_resources_200p.pak',
    'PySide6/resources/icudtl.dat',
    'PySide6/resources/v8_context_snapshot.bin',
    'PySide6/translations/qtwebengine_locales',
]
for c in checks:
    full = os.path.join(base, c)
    exists = os.path.exists(full)
    if os.path.isdir(full):
        count = len(os.listdir(full))
        print(f'[OK-DIR {count}] {c}')
    elif exists:
        sz = os.path.getsize(full) / 1024 / 1024
        print(f'[OK {sz:.1f}MB] {c}')
    else:
        print(f'[MISSING] {c}')

# Also check locale files
locale_dir = os.path.join(base, 'PySide6', 'translations', 'qtwebengine_locales')
if os.path.isdir(locale_dir):
    files = os.listdir(locale_dir)
    print(f'\nLocale files: {len(files)} (e.g. {files[:3]})')
