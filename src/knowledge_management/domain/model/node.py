# -*- coding: utf-8 -*-
"""
知识图谱节点类
"""

from typing import Dict, Any, Optional
import uuid


class Node:
    """
    知识图谱中的节点类
    """
    
    def __init__(self, 
                 node_id: Optional[str] = None,
                 label: str = "",
                 node_type: str = "default",
                 properties: Optional[Dict[str, Any]] = None,
                 x: Optional[float] = None,
                 y: Optional[float] = None):
        """
        初始化节点
        
        Args:
            node_id: 节点唯一标识符，如果为None则自动生成
            label: 节点显示标签
            node_type: 节点类型
            properties: 节点属性字典
            x: 节点x坐标
            y: 节点y坐标
        """
        self.id = node_id or str(uuid.uuid4())
        self.label = label
        self.type = node_type
        self.properties = properties or {}
        self.x = x
        self.y = y
        
    def __str__(self) -> str:
        return f"Node(id={self.id}, label={self.label}, type={self.type})"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Node):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        return hash(self.id)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将节点转换为字典格式
        
        Returns:
            节点的字典表示
        """
        return {
            'id': self.id,
            'label': self.label,
            'type': self.type,
            'properties': self.properties,
            'x': self.x,
            'y': self.y
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Node':
        """
        从字典创建节点
        
        Args:
            data: 包含节点信息的字典
            
        Returns:
            Node实例
        """
        return cls(
            node_id=data.get('id'),
            label=data.get('label', ''),
            node_type=data.get('type', 'default'),
            properties=data.get('properties', {}),
            x=data.get('x'),
            y=data.get('y')
        )
    
    def update_properties(self, properties: Dict[str, Any]) -> None:
        """
        更新节点属性
        
        Args:
            properties: 要更新的属性字典
        """
        self.properties.update(properties)
    
    def get_property(self, key: str, default: Any = None) -> Any:
        """
        获取节点属性
        
        Args:
            key: 属性键
            default: 默认值
            
        Returns:
            属性值
        """
        return self.properties.get(key, default)
    
    def set_position(self, x: float, y: float) -> None:
        """
        设置节点位置
        
        Args:
            x: x坐标
            y: y坐标
        """
        self.x = x
        self.y = y