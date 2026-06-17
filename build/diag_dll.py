"""诊断 QtWebEngineWidgets DLL 加载失败"""
import sys
import os
import ctypes

dist = r'E:\印流PDflow项目\dist\PDflow_V1.1-RC2\_internal'
pyside6_dir = os.path.join(dist, 'PySide6')

# 添加 DLL 搜索路径
os.add_dll_directory(pyside6_dir)

# 尝试逐个加载关键 DLL
dlls_to_check = [
    'Qt6Core.dll', 'Qt6Gui.dll', 'Qt6Widgets.dll',
    'Qt6Network.dll', 'Qt6WebEngineCore.dll',
    'Qt6Quick.dll', 'Qt6Qml.dll', 'Qt6WebEngineQuick.dll',
    'Qt6WebEngineWidgets.dll', 'Qt6OpenGL.dll',
    'Qt6WebChannel.dll', 'Qt6Positioning.dll',
]

print("=== DLL 加载测试 ===")
for dll_name in dlls_to_check:
    dll_path = os.path.join(pyside6_dir, dll_name)
    if not os.path.exists(dll_path):
        print(f"[NOT FOUND] {dll_name}")
        continue
    try:
        ctypes.CDLL(dll_path)
        print(f"[OK] {dll_name}")
    except OSError as e:
        print(f"[FAIL] {dll_name}: {e}")

print("\n=== Python import 测试 ===")
sys.path.insert(0, dist)

try:
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    print("[OK] QApplication")
except Exception as e:
    print(f"[FAIL] QApplication: {e}")

try:
    from PySide6.QtWebEngineWidgets import QWebEngineView
    print("[OK] QWebEngineView import")
    v = QWebEngineView()
    print("[OK] QWebEngineView create")
except Exception as e:
    print(f"[FAIL] QWebEngineView: {e}")
    import traceback
    traceback.print_exc()
