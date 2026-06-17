"""将 7z 压缩包 + SFX 模块 + 配置 组合成 Setup.exe"""
import os

PROJECT_ROOT = r"E:\印流PDflow项目"
SFX_PATH = os.path.join(PROJECT_ROOT, "build", "7z-extracted", "Files", "7-Zip", "7z.sfx")
CONFIG_PATH = os.path.join(PROJECT_ROOT, "build", "sfx_config.txt")
ARCHIVE_PATH = os.path.join(PROJECT_ROOT, "build", "PDFlow_V1.2.7z")
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "03-安装包输出", "PDFlow_V1.2_Setup.exe")

os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

# Read SFX module
with open(SFX_PATH, 'rb') as f:
    sfx_data = f.read()
print(f"SFX module: {len(sfx_data)/1024:.0f} KB")

# Read config (must be UTF-8 with BOM for some SFX modules)
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    config_text = f.read()
# Add BOM if not present
if not config_text.startswith('\ufeff'):
    config_text = '\ufeff' + config_text
config_data = config_text.encode('utf-8')
print(f"Config: {len(config_data)} bytes")

# Read archive
with open(ARCHIVE_PATH, 'rb') as f:
    archive_data = f.read()
print(f"Archive: {len(archive_data)/1024/1024:.1f} MB")

# Combine: SFX + config + archive = Setup.exe
with open(OUTPUT_PATH, 'wb') as f:
    f.write(sfx_data)
    f.write(config_data)
    f.write(archive_data)

final_size = os.path.getsize(OUTPUT_PATH)
print(f"\n{'='*50}")
print(f"Setup.exe 创建成功!")
print(f"输出: {OUTPUT_PATH}")
print(f"安装包大小: {final_size/1024/1024:.1f} MB")
print(f"{'='*50}")
