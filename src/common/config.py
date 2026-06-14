# common/config.py — 应用配置持久化模块
import os, json

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "app_config.json")

DEFAULT_CONFIG = {
    "theme": "dark",   # "dark" | "light"
}

def load_config():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"[config] 读取失败: {e}")
    return dict(DEFAULT_CONFIG)

def save_config(cfg: dict):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[config] 保存失败: {e}")

def get_theme():
    cfg = load_config()
    return cfg.get("theme", "dark")

def set_theme(theme: str):
    cfg = load_config()
    cfg["theme"] = theme
    save_config(cfg)