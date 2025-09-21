# -*- coding: utf-8 -*-
"""
实体关系抽取相关数据模型
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class EntityType(Enum):
    """实体类型枚举"""
    PERSON = "PERSON"  # 人名
    ORGANIZATION = "ORG"  # 机构名
    LOCATION = "LOC"  # 地名
    DATE = "DATE"  # 日期
    TIME = "TIME"  # 时间
    MONEY = "MONEY"  # 金额
    PERCENT = "PERCENT"  # 百分比
    PRODUCT = "PRODUCT"  # 产品
    EVENT = "EVENT"  # 事件
    CUSTOM = "CUSTOM"  # 自定义类型
    UNKNOWN = "UNKNOWN"  # 未知类型


class RelationType(Enum):
    """关系类型枚举"""
    WORK_FOR = "WORK_FOR"  # 工作于
    LOCATED_IN = "LOCATED_IN"  # 位于
    PART_OF = "PART_OF"  # 属于
    COLLABORATE_WITH = "COLLABORATE_WITH"  # 合作
    REPORT_TO = "REPORT_TO"  # 汇报给
    PARTICIPATE_IN = "PARTICIPATE_IN"  # 参与
    OWNS = "OWNS"  # 拥有
    RELATED_TO = "RELATED_TO"  # 相关
    CUSTOM = "CUSTOM"  # 自定义关系
    UNKNOWN = "UNKNOWN"  # 未知关系


@dataclass
class ExtractedEntity:
    """抽取的实体类"""
    entity_id: str  # 实体唯一标识
    text: str  # 实体文本
    entity_type: EntityType  # 实体类型
    confidence: float  # 置信度 (0.0-1.0)
    start_pos: int  # 在原文中的起始位置
    end_pos: int  # 在原文中的结束位置
    properties: Dict[str, Any] = field(default_factory=dict)  # 实体属性
    source_document: Optional[str] = None  # 来源文档
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'entity_id': self.entity_id,
            'text': self.text,
            'entity_type': self.entity_type.value,
            'confidence': self.confidence,
            'start_pos': self.start_pos,
            'end_pos': self.end_pos,
            'properties': self.properties,
            'source_document': self.source_document
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExtractedEntity':
        """从字典创建实体对象"""
        return cls(
            entity_id=data['entity_id'],
            text=data['text'],
            entity_type=EntityType(data['entity_type']),
            confidence=data['confidence'],
            start_pos=data['start_pos'],
            end_pos=data['end_pos'],
            properties=data.get('properties', {}),
            source_document=data.get('source_document')
        )


@dataclass
class ExtractedRelation:
    """抽取的关系类"""
    relation_id: str  # 关系唯一标识
    source_entity: ExtractedEntity  # 源实体
    target_entity: ExtractedEntity  # 目标实体
    relation_type: RelationType  # 关系类型
    confidence: float  # 置信度 (0.0-1.0)
    evidence_text: Optional[str] = None  # 支持该关系的文本证据
    properties: Dict[str, Any] = field(default_factory=dict)  # 关系属性
    source_document: Optional[str] = None  # 来源文档
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'relation_id': self.relation_id,
            'source_entity': self.source_entity.to_dict(),
            'target_entity': self.target_entity.to_dict(),
            'relation_type': self.relation_type.value,
            'confidence': self.confidence,
            'evidence_text': self.evidence_text,
            'properties': self.properties,
            'source_document': self.source_document
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExtractedRelation':
        """从字典创建关系对象"""
        return cls(
            relation_id=data['relation_id'],
            source_entity=ExtractedEntity.from_dict(data['source_entity']),
            target_entity=ExtractedEntity.from_dict(data['target_entity']),
            relation_type=RelationType(data['relation_type']),
            confidence=data['confidence'],
            evidence_text=data.get('evidence_text'),
            properties=data.get('properties', {}),
            source_document=data.get('source_document')
        )


@dataclass
class ExtractionResult:
    """抽取结果类"""
    document_id: str  # 文档标识
    document_path: str  # 文档路径
    entities: List[ExtractedEntity] = field(default_factory=list)  # 抽取的实体列表
    relations: List[ExtractedRelation] = field(default_factory=list)  # 抽取的关系列表
    extraction_time: datetime = field(default_factory=datetime.now)  # 抽取时间
    processing_time: float = 0.0  # 处理耗时（秒）
    metadata: Dict[str, Any] = field(default_factory=dict)  # 元数据
    
    def add_entity(self, entity: ExtractedEntity) -> None:
        """添加实体"""
        self.entities.append(entity)
    
    def add_relation(self, relation: ExtractedRelation) -> None:
        """添加关系"""
        self.relations.append(relation)
    
    def get_entities_by_type(self, entity_type: EntityType) -> List[ExtractedEntity]:
        """根据类型获取实体"""
        return [entity for entity in self.entities if entity.entity_type == entity_type]
    
    def get_relations_by_type(self, relation_type: RelationType) -> List[ExtractedRelation]:
        """根据类型获取关系"""
        return [relation for relation in self.relations if relation.relation_type == relation_type]
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        entity_type_counts = {}
        for entity in self.entities:
            entity_type = entity.entity_type.value
            entity_type_counts[entity_type] = entity_type_counts.get(entity_type, 0) + 1
        
        relation_type_counts = {}
        for relation in self.relations:
            relation_type = relation.relation_type.value
            relation_type_counts[relation_type] = relation_type_counts.get(relation_type, 0) + 1
        
        return {
            'total_entities': len(self.entities),
            'total_relations': len(self.relations),
            'entity_type_counts': entity_type_counts,
            'relation_type_counts': relation_type_counts,
            'processing_time': self.processing_time,
            'extraction_time': self.extraction_time.isoformat()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'document_id': self.document_id,
            'document_path': self.document_path,
            'entities': [entity.to_dict() for entity in self.entities],
            'relations': [relation.to_dict() for relation in self.relations],
            'extraction_time': self.extraction_time.isoformat(),
            'processing_time': self.processing_time,
            'metadata': self.metadata,
            'statistics': self.get_statistics()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExtractionResult':
        """从字典创建抽取结果对象"""
        result = cls(
            document_id=data['document_id'],
            document_path=data['document_path'],
            extraction_time=datetime.fromisoformat(data['extraction_time']),
            processing_time=data.get('processing_time', 0.0),
            metadata=data.get('metadata', {})
        )
        
        # 添加实体
        for entity_data in data.get('entities', []):
            result.add_entity(ExtractedEntity.from_dict(entity_data))
        
        # 添加关系
        for relation_data in data.get('relations', []):
            result.add_relation(ExtractedRelation.from_dict(relation_data))
        
        return result


@dataclass
class BatchExtractionResult:
    """批量抽取结果类"""
    batch_id: str  # 批次标识
    results: List[ExtractionResult] = field(default_factory=list)  # 抽取结果列表
    start_time: datetime = field(default_factory=datetime.now)  # 开始时间
    end_time: Optional[datetime] = None  # 结束时间
    total_documents: int = 0  # 总文档数
    successful_documents: int = 0  # 成功处理的文档数
    failed_documents: int = 0  # 失败的文档数
    errors: List[str] = field(default_factory=list)  # 错误信息列表
    
    def add_result(self, result: ExtractionResult) -> None:
        """添加抽取结果"""
        self.results.append(result)
        self.successful_documents += 1
    
    def add_error(self, error: str) -> None:
        """添加错误信息"""
        self.errors.append(error)
        self.failed_documents += 1
    
    def finish(self) -> None:
        """完成批量处理"""
        self.end_time = datetime.now()
    
    def get_total_processing_time(self) -> float:
        """获取总处理时间"""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0
    
    def get_summary_statistics(self) -> Dict[str, Any]:
        """获取汇总统计信息"""
        total_entities = sum(len(result.entities) for result in self.results)
        total_relations = sum(len(result.relations) for result in self.results)
        
        return {
            'batch_id': self.batch_id,
            'total_documents': self.total_documents,
            'successful_documents': self.successful_documents,
            'failed_documents': self.failed_documents,
            'total_entities': total_entities,
            'total_relations': total_relations,
            'total_processing_time': self.get_total_processing_time(),
            'average_processing_time': self.get_total_processing_time() / max(self.successful_documents, 1),
            'success_rate': self.successful_documents / max(self.total_documents, 1),
            'error_count': len(self.errors)
        }