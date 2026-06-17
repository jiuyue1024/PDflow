"""创建 PDFlow V1.2 的 7z 高压缩安装包"""
import py7zr
import os
import time

PROJECT_ROOT = r"E:\印流PDflow项目"
ARCHIVE_PATH = os.path.join(PROJECT_ROOT, "build", "PDFlow_V1.2.7z")
DIST_DIR = os.path.join(PROJECT_ROOT, "dist", "PDflow_V1.2")

os.makedirs(os.path.dirname(ARCHIVE_PATH), exist_ok=True)

print(f"源目录: {DIST_DIR}")
print(f"输出: {ARCHIVE_PATH}")
print("正在创建 LZMA2 高压缩 7z 包...")

t0 = time.time()
fcount = 0

with py7zr.SevenZipFile(ARCHIVE_PATH, 'w', filters=[{'id': py7zr.FILTER_LZMA2, 'preset': 9}]) as archive:
    for root, dirs, files in os.walk(DIST_DIR):
        for f in files:
            filepath = os.path.join(root, f)
            arcname = os.path.relpath(filepath, DIST_DIR)
            archive.write(filepath, arcname)
            fcount += 1
            if fcount % 50 == 0:
                print(f"  已打包 {fcount} 个文件...")

elapsed = time.time() - t0
sz = os.path.getsize(ARCHIVE_PATH)
src_sz = sum(os.path.getsize(os.path.join(r, f)) for r, d, fs in os.walk(DIST_DIR) for f in fs)

print(f"\n{'='*50}")
print(f"打包完成!")
print(f"文件数: {fcount}")
print(f"原始大小: {src_sz/1024/1024:.1f} MB")
print(f"压缩包大小: {sz/1024/1024:.1f} MB")
print(f"压缩率: {sz/src_sz*100:.1f}%")
print(f"耗时: {elapsed:.1f}s")
print(f"{'='*50}")
