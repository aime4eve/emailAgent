# -*- coding: utf-8 -*-
"""
知识图谱边类
"""

from typing import Dict, Any, Optional
import uuid


class Edge:
    """
    知识图谱中的边类
    """
    
    def __init__(self,
                 source_id: str,
                 target_id: str,
                 edge_id: Optional[str] = None,
                 label: str = "",
                 edge_type: str = "default",
                 properties: Optional[Dict[str, Any]] = None,
                 weight: float = 1.0):
        """
        初始化边
        
        Args:
            source_id: 源节点ID
            target_id: 目标节点ID
            edge_id: 边唯一标识符，如果为None则自动生成
            label: 边显示标签
            edge_type: 边类型
            properties: 边属性字典
            weight: 边权重
        """
        self.id = edge_id or str(uuid.uuid4())
        self.source_id = source_id
        self.target_id = target_id
        self.label = label
        self.type = edge_type
        self.properties = properties or {}
        self.weight = weight
        
    def __str__(self) -> str:
        return f"Edge(id={self.id}, {self.source_id} -> {self.target_id}, label={self.label})"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Edge):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        return hash(self.id)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将边转换为字典格式
        
        Returns:
            边的字典表示
        """
        def convert_numpy_types(obj):
            """转换numpy类型为Python原生类型"""
            try:
                import numpy as np
                if isinstance(obj, np.integer):
                    return int(obj)
                elif isinstance(obj, np.floating):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                elif isinstance(obj, dict):
                    return {k: convert_numpy_types(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_numpy_types(item) for item in obj]
            except ImportError:
                pass
            return obj
        
        return {
            'id': self.id,
            'source_id': self.source_id,
            'target_id': self.target_id,
            'label': self.label,
            'type': self.type,
            'properties': convert_numpy_types(self.properties),
            'weight': convert_numpy_types(self.weight)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Edge':
        """
        从字典创建边
        
        Args:
            data: 包含边信息的字典
            
        Returns:
            Edge实例
        """
        return cls(
            source_id=data['source_id'],
            target_id=data['target_id'],
            edge_id=data.get('id'),
            label=data.get('label', ''),
            edge_type=data.get('type', 'default'),
            properties=data.get('properties', {}),
            weight=data.get('weight', 1.0)
        )
    
    def update_properties(self, properties: Dict[str, Any]) -> None:
        """
        更新边属性
        
        Args:
            properties: 要更新的属性字典
        """
        self.properties.update(properties)
    
    def get_property(self, key: str, default: Any = None) -> Any:
        """
        获取边属性
        
        Args:
            key: 属性键
            default: 默认值
            
        Returns:
            属性值
        """
        return self.properties.get(key, default)
    
    def reverse(self) -> 'Edge':
        """
        创建反向边
        
        Returns:
            反向的Edge实例
        """
        return Edge(
            source_id=self.target_id,
            target_id=self.source_id,
            label=self.label,
            edge_type=self.type,
            properties=self.properties.copy(),
            weight=self.weight
        )