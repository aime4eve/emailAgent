# -*- coding: utf-8 -*-
"""
配置管理模块
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path


class Config:
    """
    应用配置管理类
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        初始化配置
        
        Args:
            config_file: 配置文件路径，如果为None则使用默认配置
        """
        self.config_file = config_file
        self._config = self._load_default_config()
        
        if config_file and os.path.exists(config_file):
            self.load_from_file(config_file)
            
    def _load_default_config(self) -> Dict[str, Any]:
        """
        加载默认配置
        
        Returns:
            默认配置字典
        """
        return {
            # 应用设置
            'app': {
                'title': '知识图谱可视化应用',
                'debug': True,
                'host': '0.0.0.0',
                'port': 8050,
                'auto_reload': True
            },
            
            # 可视化设置
            'visualization': {
                'default_layout': 'spring',
                'graph_width': 1200,
                'graph_height': 800,
                'node_size_range': [10, 50],
                'edge_width_range': [1, 5],
                'show_labels': True,
                'enable_physics': True
            },
            
            # 节点颜色配置
            'node_colors': {
                'default': '#1f77b4',
                'person': '#ff7f0e',
                'organization': '#2ca02c',
                'location': '#d62728',
                'concept': '#9467bd',
                'event': '#8c564b',
                'technology': '#e377c2'
            },
            
            # 边颜色配置
            'edge_colors': {
                'default': '#888888',
                'related_to': '#1f77b4',
                'works_at': '#ff7f0e',
                'located_in': '#2ca02c',
                'participates_in': '#d62728',
                'is_part_of': '#9467bd',
                'develops': '#8c564b',
                'used_for': '#e377c2'
            },
            
            # 数据设置
            'data': {
                'auto_save': True,
                'save_interval': 300,  # 秒
                'backup_count': 5,
                'default_data_dir': './data',
                'supported_formats': ['json', 'csv', 'excel']
            },
            
            # 搜索设置
            'search': {
                'case_sensitive': False,
                'search_fields': ['label', 'type'],
                'max_results': 100,
                'highlight_results': True
            },
            
            # 性能设置
            'performance': {
                'max_nodes': 1000,
                'max_edges': 5000,
                'enable_clustering': True,
                'cluster_threshold': 100,
                'lazy_loading': True
            },
            
            # UI设置
            'ui': {
                'theme': 'light',
                'sidebar_width': 300,
                'control_panel_height': 120,
                'animation_duration': 300,
                'show_statistics': True,
                'show_minimap': False
            },
            
            # 导出设置
            'export': {
                'default_format': 'json',
                'include_metadata': True,
                'compress_output': False,
                'image_formats': ['png', 'svg', 'pdf'],
                'image_resolution': 300
            },
            
            # 日志设置
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'file': './logs/app.log',
                'max_size': '10MB',
                'backup_count': 3
            }
        }
        
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键，支持点号分隔的嵌套键
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
            
    def set(self, key: str, value: Any) -> None:
        """
        设置配置值
        
        Args:
            key: 配置键，支持点号分隔的嵌套键
            value: 配置值
        """
        keys = key.split('.')
        config = self._config
        
        # 导航到最后一级的父级
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
            
        # 设置值
        config[keys[-1]] = value
        
    def update(self, config_dict: Dict[str, Any]) -> None:
        """
        批量更新配置
        
        Args:
            config_dict: 配置字典
        """
        self._deep_update(self._config, config_dict)
        
    def _deep_update(self, base_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> None:
        """
        深度更新字典
        
        Args:
            base_dict: 基础字典
            update_dict: 更新字典
        """
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value
                
    def load_from_file(self, filepath: str) -> None:
        """
        从文件加载配置
        
        Args:
            filepath: 配置文件路径
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
            self.update(file_config)
        except Exception as e:
            raise ValueError(f"加载配置文件失败: {str(e)}")
            
    def save_to_file(self, filepath: Optional[str] = None) -> None:
        """
        保存配置到文件
        
        Args:
            filepath: 配置文件路径，如果为None则使用初始化时的路径
        """
        save_path = filepath or self.config_file
        if not save_path:
            raise ValueError("未指定配置文件路径")
            
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise ValueError(f"保存配置文件失败: {str(e)}")
            
    def reset_to_default(self) -> None:
        """
        重置为默认配置
        """
        self._config = self._load_default_config()
        
    def get_app_config(self) -> Dict[str, Any]:
        """
        获取应用配置
        
        Returns:
            应用配置字典
        """
        return self.get('app', {})
        
    def get_visualization_config(self) -> Dict[str, Any]:
        """
        获取可视化配置
        
        Returns:
            可视化配置字典
        """
        return self.get('visualization', {})
        
    def get_node_colors(self) -> Dict[str, str]:
        """
        获取节点颜色配置
        
        Returns:
            节点颜色字典
        """
        return self.get('node_colors', {})
        
    def get_edge_colors(self) -> Dict[str, str]:
        """
        获取边颜色配置
        
        Returns:
            边颜色字典
        """
        return self.get('edge_colors', {})
        
    def get_data_config(self) -> Dict[str, Any]:
        """
        获取数据配置
        
        Returns:
            数据配置字典
        """
        return self.get('data', {})
        
    def is_debug_mode(self) -> bool:
        """
        检查是否为调试模式
        
        Returns:
            是否为调试模式
        """
        return self.get('app.debug', False)
        
    def get_server_config(self) -> Dict[str, Any]:
        """
        获取服务器配置
        
        Returns:
            服务器配置字典
        """
        return {
            'host': self.get('app.host', '0.0.0.0'),
            'port': self.get('app.port', 8050),
            'debug': self.get('app.debug', True)
        }
        
    def validate_config(self) -> bool:
        """
        验证配置的有效性
        
        Returns:
            配置是否有效
        """
        try:
            # 检查必需的配置项
            required_keys = [
                'app.title',
                'app.port',
                'visualization.default_layout',
                'data.default_data_dir'
            ]
            
            for key in required_keys:
                if self.get(key) is None:
                    return False
                    
            # 检查端口范围
            port = self.get('app.port')
            if not isinstance(port, int) or port < 1 or port > 65535:
                return False
                
            # 检查图形尺寸
            width = self.get('visualization.graph_width')
            height = self.get('visualization.graph_height')
            if not isinstance(width, int) or not isinstance(height, int):
                return False
            if width < 100 or height < 100:
                return False
                
            return True
            
        except Exception:
            return False
            
    def to_dict(self) -> Dict[str, Any]:
        """
        获取完整配置字典
        
        Returns:
            配置字典
        """
        return self._config.copy()
        
    def __str__(self) -> str:
        return f"Config(file={self.config_file})"
        
    def __repr__(self) -> str:
        return self.__str__()


# 全局配置实例
_global_config = None


def get_config(config_file: Optional[str] = None) -> Config:
    """
    获取全局配置实例
    
    Args:
        config_file: 配置文件路径
        
    Returns:
        配置实例
    """
    global _global_config
    if _global_config is None:
        _global_config = Config(config_file)
    return _global_config


def set_config(config: Config) -> None:
    """
    设置全局配置实例
    
    Args:
        config: 配置实例
    """
    global _global_config
    _global_config = config