#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识图谱节点类
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import uuid

@dataclass
class Node:
    """知识图谱节点"""
    id: str
    label: str
    node_type: str
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """初始化后处理"""
        if not self.id:
            self.id = str(uuid.uuid4())
    
    def get_property(self, key: str, default: Any = None) -> Any:
        """获取属性值"""
        return self.properties.get(key, default)
    
    def set_property(self, key: str, value: Any) -> None:
        """设置属性值"""
        self.properties[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'label': self.label,
            'type': self.node_type,
            'properties': self.properties
        }
    
    def __str__(self) -> str:
        return f"Node(id={self.id}, label={self.label}, type={self.node_type})"
    
    def __repr__(self) -> str:
        return self.__str__()