"""
Build-Kit-Post001.py
Create a self-contained release kit for the first content post (post_001).
Copies all assets, renames with semantic prefixes, writes README.
"""
import os
import shutil
from pathlib import Path

PROJECT = Path(r"E:\印流PDflow项目")
PKG = PROJECT / "06-内容运营" / "印流PDflow_首帖素材包_post001_2026-06-13"

# Source paths
SRC_DRAFTS = PROJECT / "06-内容运营" / "drafts"
SRC_SCREENS = PROJECT / "06-内容运营" / "assets" / "screenshots"
SRC_COVER = PROJECT / "06-内容运营" / "assets" / "cover"
SRC_OPS = PROJECT / "06-内容运营"
BUILD_LOG = PROJECT / "build_log_post001.txt"

# Clean and create
if PKG.exists():
    shutil.rmtree(PKG)
for sub in ["01_文案", "02_配图", "03_运营记录", "04_备用工具", "05_post002_素材"]:
    (PKG / sub).mkdir(parents=True)

# Clean up old package in project root (from earlier misplaced build)
OLD_PKG = PROJECT / "印流PDflow_首帖素材包_post001_2026-06-13"
if OLD_PKG.exists():
    shutil.rmtree(OLD_PKG)
    print(f"CLEANED old package at: {OLD_PKG}")

# 1) 文案（3 篇）
shutil.copy2(
    SRC_DRAFTS / "xiaohongshu" / "post_001.md",
    PKG / "01_文案" / "01_小红书_≤300字_主推.md"
)
shutil.copy2(
    SRC_DRAFTS / "nodeloc" / "post_001.md",
    PKG / "01_文案" / "02_Nodeloc_V2EX_约1200字.md"
)
shutil.copy2(
    SRC_DRAFTS / "wechat" / "post_001.md",
    PKG / "01_文案" / "03_公众号_约2100字.md"
)

# 2) 配图
shutil.copy2(
    SRC_SCREENS / "post_001_all_build_798mb.png",
    PKG / "02_配图" / "01_主图_终端TotalMB_797.81MB_1280x720.png"
)
shutil.copy2(
    SRC_SCREENS / "post_001_dist_folder.png",
    PKG / "02_配图" / "02_配图_资源管理器属性_1280x720.png"
)
shutil.copy2(
    SRC_SCREENS / "采集清单.md",
    PKG / "02_配图" / "采集清单.md"
)

# 3) 运营记录
shutil.copy2(SRC_OPS / "changelog.md", PKG / "03_运营记录" / "changelog.md")
shutil.copy2(SRC_OPS / "ideas.md", PKG / "03_运营记录" / "ideas.md")

# 4) 备用工具
shutil.copy2(SRC_COVER / "prompts.md", PKG / "04_备用工具" / "Seedream_prompts_备用.md")
shutil.copy2(SRC_SCREENS / "generate_screenshots.ps1", PKG / "04_备用工具" / "generate_screenshots.ps1")

# 5) post_002 素材
if BUILD_LOG.exists():
    shutil.copy2(BUILD_LOG, PKG / "05_post002_素材" / "build_log_post001.txt")
else:
    print(f"WARNING: build log not found at {BUILD_LOG}")

print("PACKAGE CREATED:", PKG)
print()
for item in sorted(PKG.rglob("*")):
    rel = item.relative_to(PKG)
    size = item.stat().st_size if item.is_file() else 0
    kind = "[DIR]" if item.is_dir() else f"[{size:>7,} B]"
    print(f"  {kind}  {rel}")
