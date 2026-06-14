"""
最近使用文件历史记录管理模块
存储位置: <项目根目录>/data/recent_files.json
"""
import os
import json
import time
from datetime import datetime
from typing import List, Dict, Optional

from src.common.paths import data_path

_DATA_DIR = data_path("data")
_DATA_FILE = os.path.join(_DATA_DIR, "recent_files.json")

# 最大记录数
_MAX_RECORDS = 50

# 操作类型映射
ACTION_NAMES = {
    "merge": "合并拆分",
    "compress": "压缩优化",
    "convert": "格式转换",
    "watermark": "水印处理",
    "template": "模板排版",
}


def _ensure_data_dir():
    """确保数据目录存在"""
    if not os.path.exists(_DATA_DIR):
        os.makedirs(_DATA_DIR)


def _load_records() -> List[Dict]:
    """读取所有历史记录"""
    if not os.path.exists(_DATA_FILE):
        return []
    try:
        with open(_DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def _save_records(records: List[Dict]):
    """保存历史记录"""
    _ensure_data_dir()
    with open(_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def add_record(file_path: str, action: str, output_path: Optional[str] = None):
    """
    添加一条历史记录

    Args:
        file_path: 输入文件路径
        action: 操作类型 (merge/compress/convert/watermark/template)
        output_path: 输出文件路径(可选)
    """
    if not file_path or not os.path.exists(file_path):
        return

    records = _load_records()

    # 去重:如果同一文件同一操作已存在,先删除旧记录
    records = [
        r for r in records
        if not (r.get("file_path") == file_path and r.get("action") == action)
    ]

    # 添加新记录到开头
    record = {
        "file_path": file_path,
        "file_name": os.path.basename(file_path),
        "action": action,
        "action_name": ACTION_NAMES.get(action, action),
        "timestamp": time.time(),
        "datetime": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "output_path": output_path or "",
    }
    records.insert(0, record)

    # 限制最大记录数
    if len(records) > _MAX_RECORDS:
        records = records[:_MAX_RECORDS]

    _save_records(records)


def get_recent_files(limit: int = 10) -> List[Dict]:
    """
    获取最近使用的文件列表

    Args:
        limit: 返回最大条数

    Returns:
        历史记录列表,每条包含 file_path, file_name, action, action_name, timestamp, datetime
    """
    records = _load_records()
    return records[:limit]


def clear_records():
    """清空所有历史记录"""
    _save_records([])


def get_status_text(timestamp: float) -> str:
    """根据时间戳生成状态文本(刚刚/昨天/3天前等)"""
    now = time.time()
    diff = now - timestamp

    if diff < 60:
        return "刚刚"
    elif diff < 3600:
        return f"{int(diff // 60)}分钟前"
    elif diff < 7200:
        return "1小时前"
    elif diff < 86400:
        return f"{int(diff // 3600)}小时前"
    elif diff < 172800:
        return "昨天"
    elif diff < 259200:
        return "2天前"
    elif diff < 345600:
        return "3天前"
    elif diff < 432000:
        return "4天前"
    elif diff < 518400:
        return "5天前"
    elif diff < 604800:
        return "6天前"
    else:
        return f"{int(diff // 86400)}天前"
