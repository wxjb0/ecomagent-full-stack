"""
缓存管理器 - 提供智能缓存功能
"""

import hashlib
import json
import functools
from typing import Any, Dict, Optional, Callable
from datetime import datetime, timedelta
from data.database import db_manager

class CacheManager:
    """智能缓存管理器"""
    
    def __init__(self):
        self.memory_cache = {}
        self.default_ttl = 3600  # 默认1小时
    
    def generate_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """生成缓存键"""
        key_data = {
            "prefix": prefix,
            "args": args,
            "kwargs": kwargs
        }
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return f"{prefix}:{hashlib.md5(key_str.encode()).hexdigest()}"
    
    def get(self, cache_key: str) -> Optional[Any]:
        """获取缓存值"""
        # 先查内存缓存
        if cache_key in self.memory_cache:
            entry = self.memory_cache[cache_key]
            if entry["expires_at"] > datetime.now():
                return entry["value"]
            else:
                del self.memory_cache[cache_key]
        
        # 再查数据库缓存
        return db_manager.get_cached_result(cache_key)
    
    def set(self, cache_key: str, value: Any, platform: str = "", 
            cache_type: str = "general", ttl_seconds: int = None):
        """设置缓存值"""
        ttl = ttl_seconds or self.default_ttl
        expires_at = datetime.now() + timedelta(seconds=ttl)
        
        # 保存到内存缓存
        self.memory_cache[cache_key] = {
            "value": value,
            "expires_at": expires_at
        }
        
        # 保存到数据库缓存
        expire_hours = ttl / 3600
        db_manager.set_cached_result(cache_key, platform, cache_type, value, expire_hours)
    
    def delete(self, cache_key: str):
        """删除缓存"""
        if cache_key in self.memory_cache:
            del self.memory_cache[cache_key]
    
    def clear(self):
        """清空所有缓存"""
        self.memory_cache.clear()
        db_manager.clear_expired_cache()
    
    def cached(self, prefix: str, ttl_seconds: int = None, platform_param: str = None):
        """缓存装饰器"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # 生成缓存键
                cache_key = self.generate_cache_key(prefix, *args, **kwargs)
                
                # 尝试获取缓存
                cached_value = self.get(cache_key)
                if cached_value is not None:
                    return cached_value
                
                # 执行函数
                result = func(*args, **kwargs)
                
                # 获取平台参数
                platform = kwargs.get(platform_param, "general") if platform_param else "general"
                
                # 保存缓存
                self.set(cache_key, result, platform, prefix, ttl_seconds)
                
                return result
            return wrapper
        return decorator

# 全局缓存管理器实例
cache_manager = CacheManager()
