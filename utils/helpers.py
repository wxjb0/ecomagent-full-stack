"""
辅助函数工具模块
"""

import json
from typing import Any, Dict, List
from datetime import datetime

def make_json_serializable(obj: Any) -> Any:
    """使对象可JSON序列化"""
    if hasattr(obj, 'to_dict'):
        return obj.to_dict()
    elif hasattr(obj, '__dict__'):
        return obj.__dict__
    elif isinstance(obj, (int, float, str, bool, type(None))):
        return obj
    elif isinstance(obj, list):
        return [make_json_serializable(item) for item in obj]
    elif isinstance(obj, dict):
        return {str(k): make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, datetime):
        return obj.isoformat()
    else:
        return str(obj)

def format_currency(amount: float, currency: str = "¥") -> str:
    """格式化货币"""
    return f"{currency}{amount:,.2f}"

def truncate_text(text: str, max_length: int = 100) -> str:
    """截断文本"""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."

def calculate_growth_rate(current: float, previous: float) -> float:
    """计算增长率"""
    if previous == 0:
        return 0.0
    return (current - previous) / previous

def safe_get(d: Dict, *keys, default: Any = None) -> Any:
    """安全获取嵌套字典值"""
    for key in keys:
        if isinstance(d, dict) and key in d:
            d = d[key]
        else:
            return default
    return d
