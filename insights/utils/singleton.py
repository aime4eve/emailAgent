# -*- coding: utf-8 -*-
"""
单例模式实现

提供线程安全的单例模式元类。
"""

import threading
from typing import Dict, Any

class Singleton(type):
    """线程安全的单例模式元类
    
    确保一个类只有一个实例，并提供全局访问点。
    """
    
    _instances: Dict[type, Any] = {}
    _lock = threading.Lock()
    
    def __call__(cls, *args, **kwargs):
        """创建或返回单例实例
        
        Args:
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            单例实例
        """
        if cls not in cls._instances:
            with cls._lock:
                # 双重检查锁定模式
                if cls not in cls._instances:
                    cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
    
    def clear_instance(cls):
        """清除单例实例（主要用于测试）
        
        Args:
            cls: 要清除的类
        """
        with cls._lock:
            if cls in cls._instances:
                del cls._instances[cls]
    
    def get_instances(cls) -> Dict[type, Any]:
        """获取所有单例实例（主要用于调试）
        
        Returns:
            所有单例实例的字典
        """
        return cls._instances.copy()