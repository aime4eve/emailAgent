# -*- coding: utf-8 -*-
"""
NLP处理器
基于spaCy和jieba实现自然语言处理功能
"""

import re
import logging
from typing import Dict, List, Optional, Any, Tuple, Set
from abc import ABC, abstractmethod
import uuid

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

try:
    from transformers import pipeline
except ImportError:
    pipeline = None

from ..domain.model.extraction import (
    ExtractedEntity, ExtractedRelation, EntityType, RelationType
)


class NLPProcessorError(Exception):
    """NLP处理异常"""
    pass


class BaseNLPProcessor(ABC):
    """NLP处理器基类"""
    
    @abstractmethod
    def extract_entities(self, text: str) -> List[ExtractedEntity]:
        """提取实体"""
        pass
    
    @abstractmethod
    def extract_relations(self, text: str, entities: List[ExtractedEntity]) -> List[ExtractedRelation]:
        """提取关系"""
        pass


class ChineseNLPProcessor(BaseNLPProcessor):
    """中文NLP处理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._init_jieba()
        self._init_patterns()
    
    def _init_jieba(self):
        """初始化jieba分词器"""
        if jieba is None:
            raise NLPProcessorError("jieba库未安装，请安装 jieba")
        
        # 添加自定义词典
        custom_words = [
            ('人工智能', 10, 'n'),
            ('机器学习', 10, 'n'),
            ('深度学习', 10, 'n'),
            ('知识图谱', 10, 'n'),
            ('自然语言处理', 10, 'n')
        ]
        
        for word, freq, tag in custom_words:
            jieba.add_word(word, freq, tag)
    
    def _init_patterns(self):
        """初始化正则表达式模式"""
        # 人名模式
        self.person_patterns = [
            r'[\u4e00-\u9fa5]{2,4}(?:先生|女士|老师|教授|博士|硕士|经理|总监|主任|部长|局长)',
            r'(?:先生|女士|老师|教授|博士|硕士|经理|总监|主任|部长|局长)[\u4e00-\u9fa5]{2,4}',
            r'[\u4e00-\u9fa5]{2,4}(?:说|表示|认为|指出|提到)',
        ]
        
        # 机构名模式
        self.org_patterns = [
            r'[\u4e00-\u9fa5]+(?:公司|企业|集团|有限公司|股份有限公司|科技|技术)',
            r'[\u4e00-\u9fa5]+(?:大学|学院|研究所|研究院|实验室)',
            r'[\u4e00-\u9fa5]+(?:部|局|委|厅|署|办)',
        ]
        
        # 地名模式
        self.location_patterns = [
            r'[\u4e00-\u9fa5]+(?:省|市|县|区|镇|村|街道|路|街|巷)',
            r'(?:北京|上海|天津|重庆|广州|深圳|杭州|南京|武汉|成都|西安|沈阳|大连|青岛|厦门)',
        ]
        
        # 时间模式
        self.time_patterns = [
            r'\d{4}年\d{1,2}月\d{1,2}日',
            r'\d{4}-\d{1,2}-\d{1,2}',
            r'\d{1,2}月\d{1,2}日',
            r'(?:今天|昨天|明天|前天|后天)',
            r'(?:上午|下午|晚上|凌晨)\d{1,2}[：:]\d{2}',
        ]
        
        # 关系模式
        self.relation_patterns = {
            RelationType.WORK_FOR: [
                r'(.+?)(?:在|于)(.+?)(?:工作|任职|就职)',
                r'(.+?)(?:是|为)(.+?)(?:员工|职员|成员)',
            ],
            RelationType.LOCATED_IN: [
                r'(.+?)(?:位于|在)(.+?)(?:地区|地方|城市|省|市)',
                r'(.+?)(?:坐落在|设在)(.+?)',
            ],
            RelationType.PART_OF: [
                r'(.+?)(?:属于|隶属于)(.+?)',
                r'(.+?)(?:是)(.+?)(?:的一部分|的组成部分)',
            ],
            RelationType.COLLABORATE_WITH: [
                r'(.+?)(?:与|和)(.+?)(?:合作|协作|配合)',
                r'(.+?)(?:联合)(.+?)(?:开展|进行)',
            ],
        }
    
    def segment_text(self, text: str) -> List[Tuple[str, str]]:
        """分词和词性标注"""
        if pseg is None:
            raise NLPProcessorError("jieba.posseg模块未安装")
        
        words = pseg.cut(text)
        return [(word, flag) for word, flag in words if word.strip()]
    
    def extract_entities(self, text: str) -> List[ExtractedEntity]:
        """提取实体"""
        entities = []
        
        # 使用正则表达式提取实体
        entities.extend(self._extract_entities_by_pattern(text, self.person_patterns, EntityType.PERSON))
        entities.extend(self._extract_entities_by_pattern(text, self.org_patterns, EntityType.ORGANIZATION))
        entities.extend(self._extract_entities_by_pattern(text, self.location_patterns, EntityType.LOCATION))
        entities.extend(self._extract_entities_by_pattern(text, self.time_patterns, EntityType.DATE))
        
        # 使用词性标注提取实体
        entities.extend(self._extract_entities_by_pos(text))
        
        # 去重和过滤
        entities = self._deduplicate_entities(entities)
        
        return entities
    
    def _extract_entities_by_pattern(self, text: str, patterns: List[str], entity_type: EntityType) -> List[ExtractedEntity]:
        """使用正则表达式模式提取实体"""
        entities = []
        
        for pattern in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                entity_text = match.group().strip()
                if len(entity_text) > 1:  # 过滤单字符
                    entity = ExtractedEntity(
                        entity_id=str(uuid.uuid4()),
                        text=entity_text,
                        entity_type=entity_type,
                        confidence=0.7,  # 正则表达式的置信度设为0.7
                        start_pos=match.start(),
                        end_pos=match.end()
                    )
                    entities.append(entity)
        
        return entities
    
    def _extract_entities_by_pos(self, text: str) -> List[ExtractedEntity]:
        """使用词性标注提取实体"""
        entities = []
        words = self.segment_text(text)
        
        current_pos = 0
        for word, pos in words:
            # 查找词在原文中的位置
            start_pos = text.find(word, current_pos)
            if start_pos == -1:
                current_pos += len(word)
                continue
            
            end_pos = start_pos + len(word)
            current_pos = end_pos
            
            entity_type = None
            confidence = 0.6
            
            # 根据词性判断实体类型
            if pos in ['nr', 'nrf']:  # 人名
                entity_type = EntityType.PERSON
            elif pos in ['ns', 'nsf']:  # 地名
                entity_type = EntityType.LOCATION
            elif pos in ['nt', 'ntc', 'ntcf', 'ntcb', 'ntch', 'nto', 'ntu', 'nts', 'nth']:  # 机构名
                entity_type = EntityType.ORGANIZATION
            elif pos in ['t']:  # 时间
                entity_type = EntityType.DATE
            
            if entity_type and len(word) > 1:
                entity = ExtractedEntity(
                    entity_id=str(uuid.uuid4()),
                    text=word,
                    entity_type=entity_type,
                    confidence=confidence,
                    start_pos=start_pos,
                    end_pos=end_pos,
                    properties={'pos_tag': pos}
                )
                entities.append(entity)
        
        return entities
    
    def _deduplicate_entities(self, entities: List[ExtractedEntity]) -> List[ExtractedEntity]:
        """去重实体"""
        seen = set()
        unique_entities = []
        
        for entity in entities:
            # 使用文本和类型作为去重键
            key = (entity.text, entity.entity_type)
            if key not in seen:
                seen.add(key)
                unique_entities.append(entity)
            else:
                # 如果重复，保留置信度更高的
                for i, existing in enumerate(unique_entities):
                    if existing.text == entity.text and existing.entity_type == entity.entity_type:
                        if entity.confidence > existing.confidence:
                            unique_entities[i] = entity
                        break
        
        return unique_entities
    
    def extract_relations(self, text: str, entities: List[ExtractedEntity]) -> List[ExtractedRelation]:
        """提取关系"""
        relations = []
        
        # 使用正则表达式模式提取关系
        for relation_type, patterns in self.relation_patterns.items():
            relations.extend(self._extract_relations_by_pattern(text, patterns, relation_type, entities))
        
        # 基于实体位置推断关系
        relations.extend(self._infer_relations_by_proximity(text, entities))
        
        return relations
    
    def _extract_relations_by_pattern(self, text: str, patterns: List[str], 
                                     relation_type: RelationType, 
                                     entities: List[ExtractedEntity]) -> List[ExtractedRelation]:
        """使用正则表达式模式提取关系"""
        relations = []
        
        for pattern in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                if len(match.groups()) >= 2:
                    source_text = match.group(1).strip()
                    target_text = match.group(2).strip()
                    
                    # 查找对应的实体
                    source_entity = self._find_entity_by_text(source_text, entities)
                    target_entity = self._find_entity_by_text(target_text, entities)
                    
                    if source_entity and target_entity:
                        relation = ExtractedRelation(
                            relation_id=str(uuid.uuid4()),
                            source_entity=source_entity,
                            target_entity=target_entity,
                            relation_type=relation_type,
                            confidence=0.7,
                            evidence_text=match.group()
                        )
                        relations.append(relation)
        
        return relations
    
    def _infer_relations_by_proximity(self, text: str, entities: List[ExtractedEntity]) -> List[ExtractedRelation]:
        """基于实体邻近性推断关系"""
        relations = []
        
        # 按位置排序实体
        sorted_entities = sorted(entities, key=lambda e: e.start_pos)
        
        for i, entity1 in enumerate(sorted_entities):
            for j, entity2 in enumerate(sorted_entities[i+1:], i+1):
                # 如果两个实体距离较近（小于50个字符），尝试推断关系
                if entity2.start_pos - entity1.end_pos < 50:
                    relation_type = self._infer_relation_type(entity1, entity2, text)
                    if relation_type:
                        # 提取两个实体之间的文本作为证据
                        evidence_start = entity1.start_pos
                        evidence_end = entity2.end_pos
                        evidence_text = text[evidence_start:evidence_end]
                        
                        relation = ExtractedRelation(
                            relation_id=str(uuid.uuid4()),
                            source_entity=entity1,
                            target_entity=entity2,
                            relation_type=relation_type,
                            confidence=0.5,  # 推断关系的置信度较低
                            evidence_text=evidence_text
                        )
                        relations.append(relation)
        
        return relations
    
    def _infer_relation_type(self, entity1: ExtractedEntity, entity2: ExtractedEntity, text: str) -> Optional[RelationType]:
        """根据实体类型推断关系类型"""
        # 人员-机构关系
        if entity1.entity_type == EntityType.PERSON and entity2.entity_type == EntityType.ORGANIZATION:
            return RelationType.WORK_FOR
        
        # 机构-地点关系
        if entity1.entity_type == EntityType.ORGANIZATION and entity2.entity_type == EntityType.LOCATION:
            return RelationType.LOCATED_IN
        
        # 人员-人员关系
        if entity1.entity_type == EntityType.PERSON and entity2.entity_type == EntityType.PERSON:
            return RelationType.COLLABORATE_WITH
        
        return None
    
    def _find_entity_by_text(self, text: str, entities: List[ExtractedEntity]) -> Optional[ExtractedEntity]:
        """根据文本查找实体"""
        for entity in entities:
            if entity.text == text or text in entity.text or entity.text in text:
                return entity
        return None


class SpacyNLPProcessor(BaseNLPProcessor):
    """基于spaCy的NLP处理器"""
    
    def __init__(self, model_name: str = "zh_core_web_sm"):
        self.logger = logging.getLogger(__name__)
        self.model_name = model_name
        self.nlp = None
        self._load_model()
    
    def _load_model(self):
        """加载spaCy模型"""
        if spacy is None:
            raise NLPProcessorError("spaCy库未安装，请安装 spacy")
        
        try:
            self.nlp = spacy.load(self.model_name)
            self.logger.info(f"成功加载spaCy模型: {self.model_name}")
        except OSError:
            self.logger.warning(f"无法加载spaCy模型 {self.model_name}，尝试使用英文模型")
            try:
                self.nlp = spacy.load("en_core_web_sm")
                self.logger.info("成功加载英文spaCy模型")
            except OSError:
                raise NLPProcessorError("无法加载spaCy模型，请安装相应的语言模型")
    
    def extract_entities(self, text: str) -> List[ExtractedEntity]:
        """使用spaCy提取实体"""
        if self.nlp is None:
            raise NLPProcessorError("spaCy模型未加载")
        
        doc = self.nlp(text)
        entities = []
        
        for ent in doc.ents:
            entity_type = self._map_spacy_label_to_entity_type(ent.label_)
            if entity_type:
                entity = ExtractedEntity(
                    entity_id=str(uuid.uuid4()),
                    text=ent.text,
                    entity_type=entity_type,
                    confidence=0.8,  # spaCy的置信度设为0.8
                    start_pos=ent.start_char,
                    end_pos=ent.end_char,
                    properties={'spacy_label': ent.label_}
                )
                entities.append(entity)
        
        return entities
    
    def _map_spacy_label_to_entity_type(self, spacy_label: str) -> Optional[EntityType]:
        """将spaCy标签映射到实体类型"""
        mapping = {
            'PERSON': EntityType.PERSON,
            'ORG': EntityType.ORGANIZATION,
            'GPE': EntityType.LOCATION,  # Geopolitical entity
            'LOC': EntityType.LOCATION,
            'DATE': EntityType.DATE,
            'TIME': EntityType.TIME,
            'MONEY': EntityType.MONEY,
            'PERCENT': EntityType.PERCENT,
            'PRODUCT': EntityType.PRODUCT,
            'EVENT': EntityType.EVENT
        }
        return mapping.get(spacy_label)
    
    def extract_relations(self, text: str, entities: List[ExtractedEntity]) -> List[ExtractedRelation]:
        """使用spaCy提取关系（基于依存句法分析）"""
        if self.nlp is None:
            raise NLPProcessorError("spaCy模型未加载")
        
        doc = self.nlp(text)
        relations = []
        
        # 基于依存关系提取关系
        for token in doc:
            if token.dep_ in ['nsubj', 'dobj', 'pobj']:  # 主语、直接宾语、介词宾语
                head = token.head
                
                # 查找对应的实体
                source_entity = self._find_entity_by_position(token.idx, token.idx + len(token.text), entities)
                target_entity = self._find_entity_by_position(head.idx, head.idx + len(head.text), entities)
                
                if source_entity and target_entity and source_entity != target_entity:
                    relation_type = self._infer_relation_from_dependency(token.dep_, head.pos_)
                    if relation_type:
                        relation = ExtractedRelation(
                            relation_id=str(uuid.uuid4()),
                            source_entity=source_entity,
                            target_entity=target_entity,
                            relation_type=relation_type,
                            confidence=0.6,
                            evidence_text=f"{token.text} {head.text}",
                            properties={'dependency': token.dep_, 'head_pos': head.pos_}
                        )
                        relations.append(relation)
        
        return relations
    
    def _find_entity_by_position(self, start: int, end: int, entities: List[ExtractedEntity]) -> Optional[ExtractedEntity]:
        """根据位置查找实体"""
        for entity in entities:
            if (entity.start_pos <= start < entity.end_pos or 
                entity.start_pos < end <= entity.end_pos or
                (start <= entity.start_pos and end >= entity.end_pos)):
                return entity
        return None
    
    def _infer_relation_from_dependency(self, dep: str, head_pos: str) -> Optional[RelationType]:
        """根据依存关系推断关系类型"""
        if dep == 'nsubj' and head_pos == 'VERB':
            return RelationType.RELATED_TO
        elif dep == 'dobj':
            return RelationType.RELATED_TO
        elif dep == 'pobj':
            return RelationType.RELATED_TO
        return None


class HybridNLPProcessor(BaseNLPProcessor):
    """混合NLP处理器，结合多种方法"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.processors = []
        
        # 尝试初始化各种处理器
        try:
            self.processors.append(ChineseNLPProcessor())
            self.logger.info("成功初始化中文NLP处理器")
        except Exception as e:
            self.logger.warning(f"无法初始化中文NLP处理器: {e}")
        
        try:
            self.processors.append(SpacyNLPProcessor())
            self.logger.info("成功初始化spaCy NLP处理器")
        except Exception as e:
            self.logger.warning(f"无法初始化spaCy NLP处理器: {e}")
        
        if not self.processors:
            raise NLPProcessorError("无法初始化任何NLP处理器")
    
    def extract_entities(self, text: str) -> List[ExtractedEntity]:
        """使用所有可用处理器提取实体并合并结果"""
        all_entities = []
        
        for processor in self.processors:
            try:
                entities = processor.extract_entities(text)
                all_entities.extend(entities)
            except Exception as e:
                self.logger.error(f"处理器 {type(processor).__name__} 提取实体失败: {e}")
        
        # 合并和去重
        return self._merge_entities(all_entities)
    
    def extract_relations(self, text: str, entities: List[ExtractedEntity]) -> List[ExtractedRelation]:
        """使用所有可用处理器提取关系并合并结果"""
        all_relations = []
        
        for processor in self.processors:
            try:
                relations = processor.extract_relations(text, entities)
                all_relations.extend(relations)
            except Exception as e:
                self.logger.error(f"处理器 {type(processor).__name__} 提取关系失败: {e}")
        
        # 合并和去重
        return self._merge_relations(all_relations)
    
    def _merge_entities(self, entities: List[ExtractedEntity]) -> List[ExtractedEntity]:
        """合并实体，去重并选择最佳结果"""
        entity_groups = {}
        
        # 按文本分组
        for entity in entities:
            key = entity.text.lower().strip()
            if key not in entity_groups:
                entity_groups[key] = []
            entity_groups[key].append(entity)
        
        merged_entities = []
        for group in entity_groups.values():
            if len(group) == 1:
                merged_entities.append(group[0])
            else:
                # 选择置信度最高的实体
                best_entity = max(group, key=lambda e: e.confidence)
                merged_entities.append(best_entity)
        
        return merged_entities
    
    def _merge_relations(self, relations: List[ExtractedRelation]) -> List[ExtractedRelation]:
        """合并关系，去重并选择最佳结果"""
        relation_groups = {}
        
        # 按源实体、目标实体和关系类型分组
        for relation in relations:
            key = (relation.source_entity.text, relation.target_entity.text, relation.relation_type)
            if key not in relation_groups:
                relation_groups[key] = []
            relation_groups[key].append(relation)
        
        merged_relations = []
        for group in relation_groups.values():
            if len(group) == 1:
                merged_relations.append(group[0])
            else:
                # 选择置信度最高的关系
                best_relation = max(group, key=lambda r: r.confidence)
                merged_relations.append(best_relation)
        
        return merged_relations


# 全局NLP处理器实例
nlp_processor = None

def get_nlp_processor() -> BaseNLPProcessor:
    """获取NLP处理器实例"""
    global nlp_processor
    if nlp_processor is None:
        try:
            nlp_processor = HybridNLPProcessor()
        except Exception as e:
            logging.error(f"无法初始化NLP处理器: {e}")
            raise
    return nlp_processor