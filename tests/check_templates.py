# -*- coding: utf-8 -*-
"""验证所有模板 JSON 文件可加载"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

templates_dir = os.path.join(os.path.dirname(__file__), "..", "assets", "templates")
json_files = sorted([f for f in os.listdir(templates_dir) if f.endswith(".json")])
print(f"Found {len(json_files)} template files:")
for f in json_files:
    filepath = os.path.join(templates_dir, f)
    with open(filepath, encoding="utf-8") as fh:
        data = json.load(fh)
    print(f"  - {data.get('id','?'):15s} {data.get('name','?'):10s} ({data.get('type','?')})")
print("\nAll templates loaded OK!")
