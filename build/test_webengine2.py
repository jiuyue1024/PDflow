"""直接在打包环境模拟 QWebEngineView 创建，复现错误"""
import sys
import os
import traceback

# 设置打包环境
dist = r'E:\印流PDflow项目\dist\PDflow_V1.1-RC2\_internal'
sys.path.insert(0, dist)
sys.path.insert(0, os.path.join(dist, 'pages'))
sys.path.insert(0, os.path.join(dist, 'src'))
sys.path.insert(0, os.path.join(dist, 'src', 'common'))

# 模拟 PyInstaller 的 sys._MEIPASS
sys._MEIPASS = dist

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

app = QApplication(sys.argv)

# 模拟 theme_tokens 的 t() 函数
from src.common.theme_tokens import get_token as t

print("=" * 60)
print("模拟 template_editor_page 的 WebEngine 创建流程")
print("=" * 60)

print(f"\n[INFO] sys._MEIPASS = {getattr(sys, '_MEIPASS', 'NOT SET')}")
print(f"[INFO] t('on_accent') = {t('on_accent')}")

# 完全复现 template_editor_page.py 第 2206-2231 行的逻辑
try:
    print("\n[STEP 1] 导入 QWebEngineView...")
    from PySide6.QtWebEngineWidgets import QWebEngineView
    print("  -> 导入成功")
    
    print("\n[STEP 2] 创建 QWebEngineView 实例...")
    previewView = QWebEngineView()
    print(f"  -> 创建成功, 类型: {type(previewView)}")
    
    print("\n[STEP 3] 设置 objectName...")
    previewView.setObjectName("previewView")
    print("  -> 成功")
    
    print("\n[STEP 4] 设置 stylesheet...")
    ss = f"background-color: {t('on_accent')}; border: none;"
    print(f"  -> stylesheet: {ss}")
    previewView.setStyleSheet(ss)
    print("  -> 成功")
    
    print("\n[STEP 5] 设置 minimumHeight...")
    previewView.setMinimumHeight(300)
    print("  -> 成功")
    
    print("\n[STEP 6] 加载测试 HTML...")
    previewView.setHtml("<h1>Test</h1>")
    print("  -> 成功")
    
    print("\n" + "=" * 60)
    print("[RESULT] 全部步骤通过！WebEngine 预览功能正常！")
    print("=" * 60)
    
    previewView.deleteLater()

except Exception as e:
    print(f"\n[FAIL] 异常: {type(e).__name__}: {e}")
    traceback.print_exc()
    print("\n" + "=" * 60)
    print("[RESULT] WebEngine 预览失败！以上是错误详情")
    print("=" * 60)

app.quit()
