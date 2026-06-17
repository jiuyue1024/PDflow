"""后处理：删除 debug/冗余文件 + 重建 SFX 安装包"""
import os
import shutil

PROJECT_ROOT = r"E:\印流PDflow项目"
DIST = os.path.join(PROJECT_ROOT, "dist", "PDflow_V1.2", "_internal")

# 要删除的文件（debug + 冗余组件）
REMOVE_FILES = [
    # WebEngine debug 资源
    r"PySide6\resources\qtwebengine_devtools_resources.debug.pak",
    r"PySide6\resources\qtwebengine_resources.debug.pak",
    r"PySide6\resources\v8_context_snapshot.debug.bin",
    # OpenGL 软件渲染器（fallback，正常用硬件加速）
    r"PySide6\opengl32sw.dll",
    # 不用的 PDF 模块
    r"PySide6\Qt6Pdf.dll",
    # numpy OpenBLAS 不再删除（cv2/numpy 可能依赖）
    # r"numpy.libs\libscipy_openblas64_-63c857e738469261263c764a36be9436.dll",
    # 不用的平台插件
    r"PySide6\plugins\platforms\qminimal.dll",
    r"PySide6\plugins\platforms\qoffscreen.dll",
    r"PySide6\plugins\platforms\qdirect2d.dll",
    # 不用的图片格式插件
    r"PySide6\plugins\imageformats\qtga.dll",
    r"PySide6\plugins\imageformats\qwbmp.dll",
    r"PySide6\plugins\imageformats\qicns.dll",
    r"PySide6\plugins\imageformats\qpdf.dll",
    r"PySide6\plugins\imageformats\qwebp.dll",
    # 虚拟键盘
    r"PySide6\Qt6VirtualKeyboard.dll",
    r"PySide6\plugins\platforminputcontexts\qtvirtualkeyboardplugin.dll",
    # 其他不用的模块
    r"PySide6\plugins\networkinformation\qnetworklistmanager.dll",
    r"PySide6\plugins\generic\qtuiotouchplugin.dll",
    # Qt6Positioning.dll 不再删除（WebEngineCore 依赖）
    # r"PySide6\Qt6Positioning.dll",
]

removed_total = 0
for rel_path in REMOVE_FILES:
    full_path = os.path.join(DIST, rel_path)
    if os.path.exists(full_path):
        sz = os.path.getsize(full_path)
        os.remove(full_path)
        removed_total += sz
        print(f"  Removed: {rel_path} ({sz/1024/1024:.2f} MB)")

print(f"\n共清理: {removed_total/1024/1024:.1f} MB")

# 统计最终大小
total = 0
for root, dirs, files in os.walk(os.path.join(PROJECT_ROOT, "dist", "PDflow_V1.2")):
    for f in files:
        total += os.path.getsize(os.path.join(root, f))
print(f"最终解压后: {total/1024/1024:.1f} MB")

# 检查关键依赖是否存在
print("\n--- 关键依赖检查 ---")
checks = {
    "Qt6WebEngineCore.dll": r"PySide6\Qt6WebEngineCore.dll",
    "Qt6WebEngineQuick.dll": r"PySide6\Qt6WebEngineQuick.dll",
    "Qt6WebEngineWidgets.dll": r"PySide6\Qt6WebEngineWidgets.dll",
    "pdf2docx": "pdf2docx",
    "pdfplumber": "pdfplumber",
    "openpyxl": "openpyxl",
    "docx": "docx",
    "pandas": "pandas",
    "lxml": "lxml",
    "pymupdf": "pymupdf",
}
for name, rel in checks.items():
    full = os.path.join(DIST, rel)
    exists = os.path.exists(full) or os.path.isdir(full)
    # Also check if it's a directory with files
    if not exists:
        # Try as package directory
        pkg_dir = os.path.join(DIST, rel)
        exists = os.path.isdir(pkg_dir)
    status = "OK" if exists else "MISSING"
    print(f"  [{status}] {name}")
