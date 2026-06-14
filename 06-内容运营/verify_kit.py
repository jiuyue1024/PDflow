"""Verify the release kit structure"""
from pathlib import Path
pkg = Path(r'E:\印流PDflow项目\印流PDflow_首帖素材包_post001_2026-06-13')
total_files = 0
total_bytes = 0
for p in sorted(pkg.rglob('*')):
    rel = p.relative_to(pkg)
    if p.is_dir():
        print(f"  [DIR]      {rel}\\")
    else:
        size = p.stat().st_size
        total_files += 1
        total_bytes += size
        print(f"  [{size:>7,} B]  {rel}")
print()
print(f"TOTAL: {total_files} files, {total_bytes:,} bytes ({total_bytes/1024:.1f} KB)")
