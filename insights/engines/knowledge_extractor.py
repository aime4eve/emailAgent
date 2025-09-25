# -*- coding: utf-8 -*-
"""
知识抽取引擎

从邮件文本中抽取实体、关系和事件信息，构建结构化知识。
"""

import re
import logging
from typing import List, Dict, Any, Tuple, Optional, Set
from dataclasses import dataclass
from datetime import datetime

try:
    import spacy
    from spacy import displacy
except ImportError:
    spacy = None

try:
    import jieba
    import jieba.posseg as pseg
except ImportError:
    jieba = None
    pseg = None

from ..core.exceptions import ExtractionError
from ..utils.singleton import Singleton

@dataclass
class Entity:
    """实体数据类"""
    text: str
    label: str
    start: int
    end: int
    confidence: float = 0.0
    properties: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.properties is None:
            self.properties = {}

@dataclass
class Relation:
    """关系数据类"""
    source: Entity
    target: Entity
    relation_type: str
    confidence: float = 0.0
    properties: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.properties is None:
            self.properties = {}

@dataclass
class ExtractionResult:
    """抽取结果数据类"""
    entities: List[Entity]
    relations: List[Relation]
    text: str
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {
                'extraction_time': datetime.now().isoformat(),
                'entity_count': len(self.entities),
                'relation_count': len(self.relations)
            }

class KnowledgeExtractor(metaclass=Singleton):
    """知识抽取引擎
    
    负责从文本中抽取实体、关系和事件信息。
    """
    
    def __init__(self):
        """初始化知识抽取引擎"""
        self.logger = logging.getLogger(__name__)
        self.nlp = None
        self.entity_patterns = self._build_entity_patterns()
        self.relation_patterns = self._build_relation_patterns()
        self.business_keywords = self._build_business_keywords()
        
    def initialize(self, model_name: str = 'zh_core_web_sm') -> bool:
        """初始化NLP模型
        
        Args:
            model_name: spaCy模型名称
            
        Returns:
            是否初始化成功
        """
        try:
            if spacy is None:
                raise ImportError("spacy not installed")
                
            # 加载spaCy模型
            try:
                self.nlp = spacy.load(model_name)
            except OSError:
                self.logger.warning(f"模型 {model_name} 未找到，使用英文模型")
                self.nlp = spacy.load('en_core_web_sm')
                
            # 初始化jieba（如果可用）
            if jieba is not None:
                jieba.initialize()
                
            self.logger.info(f"知识抽取引擎初始化成功，使用模型: {model_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"知识抽取引擎初始化失败: {e}")
            raise ExtractionError(f"Failed to initialize knowledge extractor: {e}")
            
    def extract_knowledge(self, text: str, extract_entities: bool = True,
                         extract_relations: bool = True) -> ExtractionResult:
        """从文本中抽取知识
        
        Args:
            text: 输入文本
            extract_entities: 是否抽取实体
            extract_relations: 是否抽取关系
            
        Returns:
            抽取结果
        """
        if not text or not text.strip():
            return ExtractionResult(entities=[], relations=[], text=text)
            
        try:
            entities = []
            relations = []
            
            # 预处理文本
            cleaned_text = self._preprocess_text(text)
            
            if extract_entities:
                entities = self._extract_entities(cleaned_text)
                
            if extract_relations and entities:
                relations = self._extract_relations(cleaned_text, entities)
                
            return ExtractionResult(
                entities=entities,
                relations=relations,
                text=text
            )
            
        except Exception as e:
            self.logger.error(f"知识抽取失败: {e}")
            raise ExtractionError(f"Knowledge extraction failed: {e}")
            
    def _preprocess_text(self, text: str) -> str:
        """预处理文本
        
        Args:
            text: 原始文本
            
        Returns:
            预处理后的文本
        """
        # 去除多余空白字符
        text = re.sub(r'\s+', ' ', text.strip())
        
        # 标准化标点符号
        text = re.sub(r'[，。！？；：]', lambda m: {'，': ',', '。': '.', '！': '!', 
                                                '？': '?', '；': ';', '：': ':'}[m.group()], text)
        
        return text
        
    def _extract_entities(self, text: str) -> List[Entity]:
        """抽取实体
        
        Args:
            text: 输入文本
            
        Returns:
            实体列表
        """
        entities = []
        
        # 使用spaCy进行命名实体识别
        if self.nlp:
            entities.extend(self._extract_entities_spacy(text))
            
        # 使用规则模式抽取特定实体
        entities.extend(self._extract_entities_patterns(text))
        
        # 去重和合并
        entities = self._merge_entities(entities)
        
        return entities
        
    def _extract_entities_spacy(self, text: str) -> List[Entity]:
        """使用spaCy抽取实体
        
        Args:
            text: 输入文本
            
        Returns:
            实体列表
        """
        entities = []
        
        try:
            doc = self.nlp(text)
            
            for ent in doc.ents:
                # 映射spaCy标签到我们的实体类型
                entity_type = self._map_spacy_label(ent.label_)
                if entity_type:
                    entity = Entity(
                        text=ent.text,
                        label=entity_type,
                        start=ent.start_char,
                        end=ent.end_char,
                        confidence=0.8,  # spaCy默认置信度
                        properties={'spacy_label': ent.label_}
                    )
                    entities.append(entity)
                    
        except Exception as e:
            self.logger.error(f"spaCy实体抽取失败: {e}")
            
        return entities
        
    def _extract_entities_patterns(self, text: str) -> List[Entity]:
        """使用规则模式抽取实体
        
        Args:
            text: 输入文本
            
        Returns:
            实体列表
        """
        entities = []
        
        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    entity = Entity(
                        text=match.group(),
                        label=entity_type,
                        start=match.start(),
                        end=match.end(),
                        confidence=0.9,  # 规则模式高置信度
                        properties={'pattern_matched': True}
                    )
                    entities.append(entity)
                    
        return entities
        
    def _extract_relations(self, text: str, entities: List[Entity]) -> List[Relation]:
        """抽取关系
        
        Args:
            text: 输入文本
            entities: 已抽取的实体列表
            
        Returns:
            关系列表
        """
        relations = []
        
        # 基于模式的关系抽取
        relations.extend(self._extract_relations_patterns(text, entities))
        
        # 基于依存句法的关系抽取
        if self.nlp:
            relations.extend(self._extract_relations_dependency(text, entities))
            
        # 基于业务规则的关系抽取
        relations.extend(self._extract_relations_business(text, entities))
        
        return relations
        
    def _extract_relations_patterns(self, text: str, entities: List[Entity]) -> List[Relation]:
        """基于模式抽取关系
        
        Args:
            text: 输入文本
            entities: 实体列表
            
        Returns:
            关系列表
        """
        relations = []
        
        for relation_type, patterns in self.relation_patterns.items():
            for pattern in patterns:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    # 查找匹配范围内的实体
                    start, end = match.span()
                    related_entities = [
                        e for e in entities 
                        if (e.start >= start - 50 and e.end <= end + 50)
                    ]
                    
                    # 创建实体间的关系
                    for i, source in enumerate(related_entities):
                        for target in related_entities[i+1:]:
                            if source != target:
                                relation = Relation(
                                    source=source,
                                    target=target,
                                    relation_type=relation_type,
                                    confidence=0.7,
                                    properties={'pattern_matched': pattern}
                                )
                                relations.append(relation)
                                
        return relations
        
    def _extract_relations_dependency(self, text: str, entities: List[Entity]) -> List[Relation]:
        """基于依存句法抽取关系
        
        Args:
            text: 输入文本
            entities: 实体列表
            
        Returns:
            关系列表
        """
        relations = []
        
        try:
            doc = self.nlp(text)
            
            # 构建实体到token的映射
            entity_tokens = {}
            for ent in doc.ents:
                for entity in entities:
                    if (entity.start <= ent.start_char <= entity.end or 
                        entity.start <= ent.end_char <= entity.end):
                        entity_tokens[ent] = entity
                        break
                        
            # 分析依存关系
            for token in doc:
                if token.ent_iob_ != 'O':  # 是实体的一部分
                    for child in token.children:
                        if child.ent_iob_ != 'O':  # 子节点也是实体
                            # 根据依存关系类型推断语义关系
                            relation_type = self._map_dependency_to_relation(token.dep_)
                            if relation_type:
                                source_entity = entity_tokens.get(token.ent)
                                target_entity = entity_tokens.get(child.ent)
                                
                                if source_entity and target_entity:
                                    relation = Relation(
                                        source=source_entity,
                                        target=target_entity,
                                        relation_type=relation_type,
                                        confidence=0.6,
                                        properties={'dependency': token.dep_}
                                    )
                                    relations.append(relation)
                                    
        except Exception as e:
            self.logger.error(f"依存句法关系抽取失败: {e}")
            
        return relations
        
    def _extract_relations_business(self, text: str, entities: List[Entity]) -> List[Relation]:
        """基于业务规则抽取关系
        
        Args:
            text: 输入文本
            entities: 实体列表
            
        Returns:
            关系列表
        """
        relations = []
        
        # 查找业务关键词
        for keyword_type, keywords in self.business_keywords.items():
            for keyword in keywords:
                if keyword in text.lower():
                    # 查找关键词附近的实体
                    keyword_pos = text.lower().find(keyword)
                    nearby_entities = [
                        e for e in entities
                        if abs(e.start - keyword_pos) < 100  # 100字符范围内
                    ]
                    
                    # 根据业务规则创建关系
                    if len(nearby_entities) >= 2:
                        for i, source in enumerate(nearby_entities):
                            for target in nearby_entities[i+1:]:
                                relation_type = self._infer_business_relation(
                                    keyword_type, source.label, target.label
                                )
                                if relation_type:
                                    relation = Relation(
                                        source=source,
                                        target=target,
                                        relation_type=relation_type,
                                        confidence=0.8,
                                        properties={'business_keyword': keyword}
                                    )
                                    relations.append(relation)
                                    
        return relations
        
    def _merge_entities(self, entities: List[Entity]) -> List[Entity]:
        """合并重复实体
        
        Args:
            entities: 原始实体列表
            
        Returns:
            合并后的实体列表
        """
        merged = []
        entities = sorted(entities, key=lambda x: (x.start, x.end))
        
        for entity in entities:
            # 检查是否与已有实体重叠
            overlapped = False
            for existing in merged:
                if (entity.start < existing.end and entity.end > existing.start):
                    # 重叠，选择置信度更高的
                    if entity.confidence > existing.confidence:
                        merged.remove(existing)
                        merged.append(entity)
                    overlapped = True
                    break
                    
            if not overlapped:
                merged.append(entity)
                
        return merged
        
    def _build_entity_patterns(self) -> Dict[str, List[str]]:
        """构建实体识别模式
        
        Returns:
            实体模式字典
        """
        return {
            'EMAIL': [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            ],
            'PHONE': [
                r'\b(?:\+86)?\s*1[3-9]\d{9}\b',
                r'\b\d{3,4}-\d{7,8}\b'
            ],
            'MONEY': [
                r'\$\s*\d+(?:,\d{3})*(?:\.\d{2})?',
                r'¥\s*\d+(?:,\d{3})*(?:\.\d{2})?',
                r'\d+(?:,\d{3})*(?:\.\d{2})?\s*(?:美元|美金|USD|元|RMB)'
            ],
            'PRODUCT': [
                r'\b(?:产品|商品|货物|设备|机器|系统)\s*[：:]?\s*([\u4e00-\u9fa5A-Za-z0-9\s-]+)',
                r'\b(?:型号|规格|款式)\s*[：:]?\s*([A-Za-z0-9-]+)'
            ],
            'COMPANY': [
                r'([\u4e00-\u9fa5A-Za-z0-9\s]+)(?:公司|有限公司|集团|企业|Corp|Inc|Ltd|LLC)\b',
                r'\b([A-Za-z0-9\s&]+)\s+(?:Company|Corporation|Inc|Ltd|LLC)\b'
            ]
        }
        
    def _build_relation_patterns(self) -> Dict[str, List[str]]:
        """构建关系识别模式
        
        Returns:
            关系模式字典
        """
        return {
            'INTERESTED_IN': [
                r'(?:感兴趣|有兴趣|想要了解|希望购买)',
                r'(?:interested in|want to buy|looking for)'
            ],
            'INQUIRY': [
                r'(?:询问|咨询|了解|请问)',
                r'(?:inquiry|ask about|question about)'
            ],
            'QUOTE': [
                r'(?:报价|价格|多少钱|费用)',
                r'(?:quote|price|cost|how much)'
            ],
            'ORDER': [
                r'(?:订购|下单|购买|采购)',
                r'(?:order|purchase|buy)'
            ],
            'WORKS_FOR': [
                r'(?:工作于|就职于|任职于)',
                r'(?:works for|employed by|works at)'
            ],
            'LOCATED_IN': [
                r'(?:位于|在|来自)',
                r'(?:located in|based in|from)'
            ]
        }
        
    def _build_business_keywords(self) -> Dict[str, List[str]]:
        """构建业务关键词
        
        Returns:
            业务关键词字典
        """
        return {
            'purchase': ['购买', '采购', '订购', 'buy', 'purchase', 'order'],
            'negotiation': ['谈判', '商谈', '协商', 'negotiate', 'discuss', 'talk'],
            'delivery': ['交货', '发货', '运输', 'delivery', 'shipping', 'transport'],
            'payment': ['付款', '支付', '结算', 'payment', 'pay', 'settle'],
            'quality': ['质量', '品质', '标准', 'quality', 'standard', 'specification']
        }
        
    def _map_spacy_label(self, label: str) -> Optional[str]:
        """映射spaCy标签到系统实体类型
        
        Args:
            label: spaCy实体标签
            
        Returns:
            系统实体类型
        """
        mapping = {
            'PERSON': 'PERSON',
            'ORG': 'COMPANY',
            'GPE': 'LOCATION',
            'MONEY': 'MONEY',
            'DATE': 'DATE',
            'TIME': 'DATE',
            'PRODUCT': 'PRODUCT'
        }
        return mapping.get(label)
        
    def _map_dependency_to_relation(self, dep: str) -> Optional[str]:
        """映射依存关系到语义关系
        
        Args:
            dep: 依存关系标签
            
        Returns:
            语义关系类型
        """
        mapping = {
            'nsubj': 'SUBJECT_OF',
            'dobj': 'OBJECT_OF',
            'prep': 'RELATED_TO',
            'compound': 'PART_OF',
            'appos': 'SAME_AS'
        }
        return mapping.get(dep)
        
    def _infer_business_relation(self, keyword_type: str, source_label: str, 
                               target_label: str) -> Optional[str]:
        """推断业务关系类型
        
        Args:
            keyword_type: 关键词类型
            source_label: 源实体标签
            target_label: 目标实体标签
            
        Returns:
            业务关系类型
        """
        # 业务关系推理规则
        rules = {
            ('purchase', 'PERSON', 'PRODUCT'): 'INTERESTED_IN',
            ('purchase', 'COMPANY', 'PRODUCT'): 'WANTS_TO_BUY',
            ('negotiation', 'PERSON', 'PERSON'): 'NEGOTIATES_WITH',
            ('delivery', 'COMPANY', 'LOCATION'): 'DELIVERS_TO',
            ('payment', 'COMPANY', 'MONEY'): 'PAYS'
        }
        
        return rules.get((keyword_type, source_label, target_label))
        
    def get_extraction_statistics(self, results: List[ExtractionResult]) -> Dict[str, Any]:
        """获取抽取统计信息
        
        Args:
            results: 抽取结果列表
            
        Returns:
            统计信息字典
        """
        if not results:
            return {}
            
        total_entities = sum(len(r.entities) for r in results)
        total_relations = sum(len(r.relations) for r in results)
        
        entity_types = {}
        relation_types = {}
        
        for result in results:
            for entity in result.entities:
                entity_types[entity.label] = entity_types.get(entity.label, 0) + 1
                
            for relation in result.relations:
                relation_types[relation.relation_type] = relation_types.get(relation.relation_type, 0) + 1
                
        return {
            'total_documents': len(results),
            'total_entities': total_entities,
            'total_relations': total_relations,
            'avg_entities_per_doc': total_entities / len(results),
            'avg_relations_per_doc': total_relations / len(results),
            'entity_type_distribution': entity_types,
            'relation_type_distribution': relation_types
        }