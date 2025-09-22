# -*- coding: utf-8 -*-
"""
知识本体数据模型
定义本体的基本结构、实体类型、关系类型等核心组件
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum


class DataType(Enum):
    """数据类型枚举"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    URI = "uri"


@dataclass
class Property:
    """属性定义类"""
    name: str
    data_type: DataType
    description: str = ""
    required: bool = False
    default_value: Optional[Any] = None
    constraints: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = asdict(self)
        result['data_type'] = self.data_type.value
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Property':
        """从字典创建属性对象"""
        data['data_type'] = DataType(data['data_type'])
        return cls(**data)


@dataclass
class EntityType:
    """实体类型定义类"""
    id: str
    name: str
    description: str = ""
    properties: List[Property] = None
    parent_types: List[str] = None  # 继承的父类型ID列表
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        """初始化后处理"""
        if self.properties is None:
            self.properties = []
        if self.parent_types is None:
            self.parent_types = []
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

    def add_property(self, prop: Property) -> None:
        """添加属性"""
        self.properties.append(prop)
        self.updated_at = datetime.now()

    def remove_property(self, prop_name: str) -> bool:
        """移除属性"""
        for i, prop in enumerate(self.properties):
            if prop.name == prop_name:
                del self.properties[i]
                self.updated_at = datetime.now()
                return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'properties': [prop.to_dict() for prop in self.properties],
            'parent_types': self.parent_types,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EntityType':
        """从字典创建实体类型对象"""
        properties = [Property.from_dict(prop) for prop in data.get('properties', [])]
        created_at = datetime.fromisoformat(data['created_at']) if data.get('created_at') else None
        updated_at = datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None
        
        return cls(
            id=data['id'],
            name=data['name'],
            description=data.get('description', ''),
            properties=properties,
            parent_types=data.get('parent_types', []),
            created_at=created_at,
            updated_at=updated_at
        )


@dataclass
class RelationType:
    """关系类型定义类"""
    id: str
    name: str
    description: str = ""
    domain_types: List[str] = None  # 定义域实体类型ID列表
    range_types: List[str] = None   # 值域实体类型ID列表
    properties: List[Property] = None
    symmetric: bool = False  # 是否对称关系
    transitive: bool = False  # 是否传递关系
    functional: bool = False  # 是否函数关系
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        """初始化后处理"""
        if self.domain_types is None:
            self.domain_types = []
        if self.range_types is None:
            self.range_types = []
        if self.properties is None:
            self.properties = []
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'domain_types': self.domain_types,
            'range_types': self.range_types,
            'properties': [prop.to_dict() for prop in self.properties],
            'symmetric': self.symmetric,
            'transitive': self.transitive,
            'functional': self.functional,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RelationType':
        """从字典创建关系类型对象"""
        properties = [Property.from_dict(prop) for prop in data.get('properties', [])]
        created_at = datetime.fromisoformat(data['created_at']) if data.get('created_at') else None
        updated_at = datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None
        
        return cls(
            id=data['id'],
            name=data['name'],
            description=data.get('description', ''),
            domain_types=data.get('domain_types', []),
            range_types=data.get('range_types', []),
            properties=properties,
            symmetric=data.get('symmetric', False),
            transitive=data.get('transitive', False),
            functional=data.get('functional', False),
            created_at=created_at,
            updated_at=updated_at
        )


@dataclass
class Ontology:
    """知识本体主类"""
    id: str
    name: str
    description: str = ""
    version: str = "1.0.0"
    namespace: str = ""
    entity_types: List[EntityType] = None
    relation_types: List[RelationType] = None
    created_at: datetime = None
    updated_at: datetime = None
    author: str = ""
    tags: List[str] = None

    def __post_init__(self):
        """初始化后处理"""
        if self.entity_types is None:
            self.entity_types = []
        if self.relation_types is None:
            self.relation_types = []
        if self.tags is None:
            self.tags = []
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

    def add_entity_type(self, entity_type: EntityType) -> None:
        """添加实体类型"""
        self.entity_types.append(entity_type)
        self.updated_at = datetime.now()

    def remove_entity_type(self, entity_type_id: str) -> bool:
        """移除实体类型"""
        for i, et in enumerate(self.entity_types):
            if et.id == entity_type_id:
                del self.entity_types[i]
                self.updated_at = datetime.now()
                return True
        return False

    def add_relation_type(self, relation_type: RelationType) -> None:
        """添加关系类型"""
        self.relation_types.append(relation_type)
        self.updated_at = datetime.now()

    def remove_relation_type(self, relation_type_id: str) -> bool:
        """移除关系类型"""
        for i, rt in enumerate(self.relation_types):
            if rt.id == relation_type_id:
                del self.relation_types[i]
                self.updated_at = datetime.now()
                return True
        return False

    def get_entity_type(self, entity_type_id: str) -> Optional[EntityType]:
        """根据ID获取实体类型"""
        for et in self.entity_types:
            if et.id == entity_type_id:
                return et
        return None

    def get_relation_type(self, relation_type_id: str) -> Optional[RelationType]:
        """根据ID获取关系类型"""
        for rt in self.relation_types:
            if rt.id == relation_type_id:
                return rt
        return None

    def validate(self) -> List[str]:
        """验证本体的一致性，返回错误信息列表"""
        errors = []
        
        # 检查实体类型ID唯一性
        entity_ids = [et.id for et in self.entity_types]
        if len(entity_ids) != len(set(entity_ids)):
            errors.append("实体类型ID存在重复")
        
        # 检查关系类型ID唯一性
        relation_ids = [rt.id for rt in self.relation_types]
        if len(relation_ids) != len(set(relation_ids)):
            errors.append("关系类型ID存在重复")
        
        # 检查关系类型的定义域和值域是否存在
        for rt in self.relation_types:
            for domain_id in rt.domain_types:
                if domain_id not in entity_ids:
                    errors.append(f"关系类型 {rt.name} 的定义域 {domain_id} 不存在")
            for range_id in rt.range_types:
                if range_id not in entity_ids:
                    errors.append(f"关系类型 {rt.name} 的值域 {range_id} 不存在")
        
        # 检查实体类型的继承关系
        for et in self.entity_types:
            for parent_id in et.parent_types:
                if parent_id not in entity_ids:
                    errors.append(f"实体类型 {et.name} 的父类型 {parent_id} 不存在")
        
        return errors

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'namespace': self.namespace,
            'entity_types': [et.to_dict() for et in self.entity_types],
            'relation_types': [rt.to_dict() for rt in self.relation_types],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'author': self.author,
            'tags': self.tags
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Ontology':
        """从字典创建本体对象"""
        entity_types = [EntityType.from_dict(et) for et in data.get('entity_types', [])]
        relation_types = [RelationType.from_dict(rt) for rt in data.get('relation_types', [])]
        created_at = datetime.fromisoformat(data['created_at']) if data.get('created_at') else None
        updated_at = datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None
        
        return cls(
            id=data['id'],
            name=data['name'],
            description=data.get('description', ''),
            version=data.get('version', '1.0.0'),
            namespace=data.get('namespace', ''),
            entity_types=entity_types,
            relation_types=relation_types,
            created_at=created_at,
            updated_at=updated_at,
            author=data.get('author', ''),
            tags=data.get('tags', [])
        )

    def save_to_file(self, file_path: str) -> None:
        """保存本体到文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def load_from_file(cls, file_path: str) -> 'Ontology':
        """从文件加载本体"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)