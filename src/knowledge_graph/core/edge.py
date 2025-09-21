#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识图谱边类
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import uuid

@dataclass
class Edge:
    """知识图谱边（关系）"""
    id: str
    source_id: str
    target_id: str
    relation_type: str
    properties: Dict[str, Any] = field(default_factory=dict)
    weight: float = 1.0
    
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
            'source_id': self.source_id,
            'target_id': self.target_id,
            'relation_type': self.relation_type,
            'properties': self.properties,
            'weight': self.weight
        }
    
    def __str__(self) -> str:
        return f"Edge(id={self.id}, {self.source_id} --[{self.relation_type}]--> {self.target_id})"
    
    def __repr__(self) -> str:
        return self.__str__()