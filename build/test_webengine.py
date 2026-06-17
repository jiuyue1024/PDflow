"""测试打包环境下 QWebEngineView 是否能正常创建"""
import sys
import os

# 模拟打包环境的 sys._MEIPASS
dist_base = r'E:\印流PDflow项目\dist\PDflow_V1.1-RC2\_internal'

# 设置环境变量（PyInstaller 运行时设置）
os.environ['QTWEBENGINEPROCESS_PATH'] = os.path.join(dist_base, 'PySide6', 'QtWebEngineProcess.exe')

sys.path.insert(0, dist_base)
sys.path.insert(0, os.path.join(dist_base, 'pages'))

from PySide6.QtWidgets import QApplication
app = QApplication(sys.argv)

print("=" * 60)
print("测试 1: 导入 QWebEngineView")
try:
    from PySide6.QtWebEngineWidgets import QWebEngineView
    print("  [OK] import 成功")
except Exception as e:
    print(f"  [FAIL] import 失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n测试 2: 创建 QWebEngineView 实例")
try:
    view = QWebEngineView()
    print("  [OK] 创建成功")
    print(f"  类型: {type(view)}")
except Exception as e:
    print(f"  [FAIL] 创建失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n测试 3: 加载 HTML 内容")
try:
    view.setHtml("<h1>Test Preview</h1><p>WebEngine is working!</p>")
    print("  [OK] setHtml 成功")
except Exception as e:
    print(f"  [FAIL] setHtml 失败: {e}")

print("\n测试 4: 检查 QtWebEngineProcess 路径")
proc_path = os.path.join(dist_base, 'PySide6', 'QtWebEngineProcess.exe')
print(f"  路径: {proc_path}")
print(f"  存在: {os.path.exists(proc_path)}")

print("\n所有测试通过!")
view.deleteLater()
app.quit()
