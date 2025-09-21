# -*- coding: utf-8 -*-
"""
关系抽取器
识别实体间的语义关系
"""

import re
from typing import List, Dict, Set, Optional, Tuple, Any
from dataclasses import dataclass
import logging
from itertools import combinations

from .entity_extractor import Entity, EntityExtractor
from .text_preprocessor import TextPreprocessor

logger = logging.getLogger(__name__)


@dataclass
class Relation:
    """
    关系类
    """
    subject: Entity      # 主体实体
    predicate: str       # 关系类型
    object: Entity       # 客体实体
    confidence: float    # 置信度
    context: str         # 上下文
    properties: Dict[str, Any] = None  # 额外属性
    
    def __post_init__(self):
        if self.properties is None:
            self.properties = {}


class RelationExtractor:
    """
    关系抽取器类
    基于规则和模式匹配的关系抽取
    """
    
    def __init__(self, language: str = 'chinese'):
        """
        初始化关系抽取器
        
        Args:
            language: 语言类型
        """
        self.language = language
        self.preprocessor = TextPreprocessor(language)
        self.entity_extractor = EntityExtractor(language)
        
        # 初始化关系模式
        self.relation_patterns = self._init_relation_patterns()
        
        # 自定义关系模式
        self.custom_relation_patterns = {}
    
    def _init_relation_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        初始化关系模式
        
        Returns:
            关系模式字典
        """
        if self.language == 'chinese':
            return {
                'WORK_AT': [
                    {
                        'pattern': r'(.+?)(?:在|于)(.+?)(?:工作|任职|就职|上班)',
                        'subject_group': 1,
                        'object_group': 2,
                        'subject_types': ['PERSON'],
                        'object_types': ['ORG']
                    },
                    {
                        'pattern': r'(.+?)(?:是|担任)(.+?)(?:的)?(?:员工|职员|经理|主任|总监|CEO|CTO|CFO)',
                        'subject_group': 1,
                        'object_group': 2,
                        'subject_types': ['PERSON'],
                        'object_types': ['ORG']
                    }
                ],
                'LOCATED_IN': [
                    {
                        'pattern': r'(.+?)(?:位于|坐落于|在)(.+?)(?:市|省|区|县|街道|路)',
                        'subject_group': 1,
                        'object_group': 2,
                        'subject_types': ['ORG', 'LOC'],
                        'object_types': ['LOC']
                    },
                    {
                        'pattern': r'(.+?)(?:的)?(?:地址|位置)(?:是|为)(.+)',
                        'subject_group': 1,
                        'object_group': 2,
                        'subject_types': ['ORG', 'PERSON'],
                        'object_types': ['LOC']
                    }
                ],
                'BORN_IN': [
                    {
                        'pattern': r'(.+?)(?:出生于|生于)(.+?)(?:年|市|省)',
                        'subject_group': 1,
                        'object_group': 2,
                        'subject_types': ['PERSON'],
                        'object_types': ['TIME', 'LOC']
                    }
                ],
                'GRADUATED_FROM': [
                    {
                        'pattern': r'(.+?)(?:毕业于|就读于)(.+?)(?:大学|学院|学校)',
                        'subject_group': 1,
                        'object_group': 2,
                        'subject_types': ['PERSON'],
                        'object_types': ['ORG']
                    }
                ],
                'FOUNDED': [
                    {
                        'pattern': r'(.+?)(?:创立|创建|成立|建立)(?:了)?(.+?)(?:公司|企业|组织)',
                        'subject_group': 1,
                        'object_group': 2,
                        'subject_types': ['PERSON'],
                        'object_types': ['ORG']
                    }
                ],
                'MARRIED_TO': [
                    {
                        'pattern': r'(.+?)(?:和|与)(.+?)(?:结婚|成婚|结为夫妻)',
                        'subject_group': 1,
                        'object_group': 2,
                        'subject_types': ['PERSON'],
                        'object_types': ['PERSON']
                    }
                ],
                'PARENT_OF': [
                    {
                        'pattern': r'(.+?)(?:是)(.+?)(?:的)?(?:父亲|母亲|爸爸|妈妈|家长)',
                        'subject_group': 1,
                        'object_group': 2,
                        'subject_types': ['PERSON'],
                        'object_types': ['PERSON']
                    }
                ],
                'COLLABORATE_WITH': [
                    {
                        'pattern': r'(.+?)(?:和|与)(.+?)(?:合作|协作|共同)',
                        'subject_group': 1,
                        'object_group': 2,
                        'subject_types': ['PERSON', 'ORG'],
                        'object_types': ['PERSON', 'ORG']
                    }
                ],
                'OWNS': [
                    {
                        'pattern': r'(.+?)(?:拥有|持有|拥有)(.+?)(?:股份|股权|资产)',
                        'subject_group': 1,
                        'object_group': 2,
                        'subject_types': ['PERSON', 'ORG'],
                        'object_types': ['ORG', 'MONEY']
                    }
                ]
            }
        else:
            return {
                'WORK_AT': [
                    {
                        'pattern': r'(.+?) works? at (.+)',
                        'subject_group': 1,
                        'object_group': 2,
                        'subject_types': ['PERSON'],
                        'object_types': ['ORG']
                    },
                    {
                        'pattern': r'(.+?) (?:is|was) (?:a|an|the) (?:employee|manager|director|CEO|CTO|CFO) (?:of|at) (.+)',
                        'subject_group': 1,
                        'object_group': 2,
                        'subject_types': ['PERSON'],
                        'object_types': ['ORG']
                    }
                ],
                'LOCATED_IN': [
                    {
                        'pattern': r'(.+?) (?:is|was) located in (.+)',
                        'subject_group': 1,
                        'object_group': 2,
                        'subject_types': ['ORG', 'LOC'],
                        'object_types': ['LOC']
                    }
                ],
                'BORN_IN': [
                    {
                        'pattern': r'(.+?) (?:was|is) born in (.+)',
                        'subject_group': 1,
                        'object_group': 2,
                        'subject_types': ['PERSON'],
                        'object_types': ['TIME', 'LOC']
                    }
                ],
                'GRADUATED_FROM': [
                    {
                        'pattern': r'(.+?) graduated from (.+)',
                        'subject_group': 1,
                        'object_group': 2,
                        'subject_types': ['PERSON'],
                        'object_types': ['ORG']
                    }
                ],
                'FOUNDED': [
                    {
                        'pattern': r'(.+?) founded (.+)',
                        'subject_group': 1,
                        'object_group': 2,
                        'subject_types': ['PERSON'],
                        'object_types': ['ORG']
                    }
                ],
                'MARRIED_TO': [
                    {
                        'pattern': r'(.+?) (?:is|was) married to (.+)',
                        'subject_group': 1,
                        'object_group': 2,
                        'subject_types': ['PERSON'],
                        'object_types': ['PERSON']
                    }
                ]
            }
    
    def extract_relations(self, text: str, entities: List[Entity] = None) -> List[Relation]:
        """抽取关系 - 别名方法"""
        return self.extract_from_text(text, entities)
    
    def extract_relations_from_text(self, text: str, entities: List[Entity] = None) -> List[Relation]:
        """从文本抽取关系 - 别名方法"""
        return self.extract_from_text(text, entities)
    
    def extract_from_text(self, text: str, entities: List[Entity] = None) -> List[Relation]:
        """
        从文本中抽取关系
        
        Args:
            text: 输入文本
            entities: 已识别的实体列表，如果为None则自动抽取
            
        Returns:
            关系列表
        """
        if entities is None:
            entities = self.entity_extractor.extract_entities(text)
        
        relations = []
        
        # 基于模式的关系抽取
        pattern_relations = self._extract_relations_by_patterns(text, entities)
        relations.extend(pattern_relations)
        
        # 基于实体共现的关系抽取
        cooccurrence_relations = self._extract_relations_by_cooccurrence(text, entities)
        relations.extend(cooccurrence_relations)
        
        # 去重和排序
        relations = self._deduplicate_relations(relations)
        relations.sort(key=lambda x: x.confidence, reverse=True)
        
        return relations
    
    def _extract_relations_by_patterns(self, text: str, entities: List[Entity]) -> List[Relation]:
        """
        基于模式的关系抽取
        
        Args:
            text: 输入文本
            entities: 实体列表
            
        Returns:
            关系列表
        """
        relations = []
        
        # 创建实体位置映射
        entity_map = {}
        for entity in entities:
            for i in range(entity.start, entity.end):
                entity_map[i] = entity
        
        # 遍历所有关系模式
        for relation_type, patterns in self.relation_patterns.items():
            for pattern_info in patterns:
                pattern = pattern_info['pattern']
                subject_group = pattern_info['subject_group']
                object_group = pattern_info['object_group']
                subject_types = pattern_info.get('subject_types', [])
                object_types = pattern_info.get('object_types', [])
                
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    try:
                        subject_text = match.group(subject_group).strip()
                        object_text = match.group(object_group).strip()
                        
                        # 查找对应的实体
                        subject_entity = self._find_entity_by_text(subject_text, entities, subject_types)
                        object_entity = self._find_entity_by_text(object_text, entities, object_types)
                        
                        if subject_entity and object_entity:
                            relation = Relation(
                                subject=subject_entity,
                                predicate=relation_type,
                                object=object_entity,
                                confidence=0.8,
                                context=match.group(0)
                            )
                            relations.append(relation)
                    
                    except Exception as e:
                        logger.warning(f"模式匹配错误: {str(e)}")
        
        return relations
    
    def _extract_relations_by_cooccurrence(self, text: str, entities: List[Entity]) -> List[Relation]:
        """
        基于实体共现的关系抽取
        
        Args:
            text: 输入文本
            entities: 实体列表
            
        Returns:
            关系列表
        """
        relations = []
        
        # 将文本分割为句子
        sentences = self.preprocessor.extract_sentences(text)
        
        for sentence in sentences:
            # 找到句子中的实体
            sentence_entities = []
            for entity in entities:
                if sentence in text[max(0, entity.start-50):entity.end+50]:
                    sentence_entities.append(entity)
            
            # 为句子中的实体对生成默认关系
            if len(sentence_entities) >= 2:
                for entity1, entity2 in combinations(sentence_entities, 2):
                    # 根据实体类型推断可能的关系
                    inferred_relation = self._infer_relation_type(entity1, entity2, sentence)
                    
                    if inferred_relation:
                        relation = Relation(
                            subject=entity1,
                            predicate=inferred_relation,
                            object=entity2,
                            confidence=0.5,  # 共现关系置信度较低
                            context=sentence
                        )
                        relations.append(relation)
        
        return relations
    
    def _find_entity_by_text(self, text: str, entities: List[Entity], 
                            allowed_types: List[str] = None) -> Optional[Entity]:
        """
        根据文本查找实体
        
        Args:
            text: 实体文本
            entities: 实体列表
            allowed_types: 允许的实体类型
            
        Returns:
            匹配的实体或None
        """
        # 精确匹配
        for entity in entities:
            if entity.text == text:
                if not allowed_types or entity.label in allowed_types:
                    return entity
        
        # 包含匹配
        for entity in entities:
            if text in entity.text or entity.text in text:
                if not allowed_types or entity.label in allowed_types:
                    return entity
        
        return None
    
    def _infer_relation_type(self, entity1: Entity, entity2: Entity, context: str) -> Optional[str]:
        """
        根据实体类型和上下文推断关系类型
        
        Args:
            entity1: 实体1
            entity2: 实体2
            context: 上下文
            
        Returns:
            推断的关系类型或None
        """
        type1, type2 = entity1.label, entity2.label
        
        # 基于实体类型的关系推断规则
        if type1 == 'PERSON' and type2 == 'ORG':
            if any(keyword in context for keyword in ['工作', '任职', '就职', 'work', 'employee']):
                return 'WORK_AT'
            elif any(keyword in context for keyword in ['创立', '创建', 'founded', 'established']):
                return 'FOUNDED'
            elif any(keyword in context for keyword in ['毕业', 'graduated']):
                return 'GRADUATED_FROM'
        
        elif type1 == 'PERSON' and type2 == 'PERSON':
            if any(keyword in context for keyword in ['结婚', '夫妻', 'married']):
                return 'MARRIED_TO'
            elif any(keyword in context for keyword in ['父亲', '母亲', '儿子', '女儿', 'father', 'mother', 'son', 'daughter']):
                return 'PARENT_OF'
            elif any(keyword in context for keyword in ['合作', '协作', 'collaborate']):
                return 'COLLABORATE_WITH'
        
        elif type1 == 'ORG' and type2 == 'LOC':
            if any(keyword in context for keyword in ['位于', '坐落', 'located']):
                return 'LOCATED_IN'
        
        elif type1 == 'PERSON' and type2 == 'LOC':
            if any(keyword in context for keyword in ['出生', '生于', 'born']):
                return 'BORN_IN'
            elif any(keyword in context for keyword in ['居住', '住在', 'live']):
                return 'LIVE_IN'
        
        # 默认关系
        return 'RELATED_TO'
    
    def _deduplicate_relations(self, relations: List[Relation]) -> List[Relation]:
        """
        去除重复关系
        
        Args:
            relations: 关系列表
            
        Returns:
            去重后的关系列表
        """
        seen = set()
        unique_relations = []
        
        for relation in relations:
            key = (
                relation.subject.text,
                relation.predicate,
                relation.object.text
            )
            
            if key not in seen:
                seen.add(key)
                unique_relations.append(relation)
            else:
                # 如果已存在相同关系，保留置信度更高的
                for i, existing in enumerate(unique_relations):
                    existing_key = (
                        existing.subject.text,
                        existing.predicate,
                        existing.object.text
                    )
                    if existing_key == key and relation.confidence > existing.confidence:
                        unique_relations[i] = relation
                        break
        
        return unique_relations
    
    def add_custom_relation_pattern(self, relation_type: str, pattern_info: Dict[str, Any]):
        """
        添加自定义关系模式
        
        Args:
            relation_type: 关系类型
            pattern_info: 模式信息字典
        """
        if relation_type not in self.custom_relation_patterns:
            self.custom_relation_patterns[relation_type] = []
        
        self.custom_relation_patterns[relation_type].append(pattern_info)
        logger.info(f"添加自定义关系模式: {relation_type}")
    
    def extract_relations_with_custom_patterns(self, text: str, entities: List[Entity] = None) -> List[Relation]:
        """
        使用自定义模式抽取关系
        
        Args:
            text: 输入文本
            entities: 实体列表
            
        Returns:
            关系列表
        """
        if entities is None:
            entities = self.entity_extractor.extract_entities(text)
        
        relations = []
        
        # 使用自定义模式
        for relation_type, patterns in self.custom_relation_patterns.items():
            for pattern_info in patterns:
                pattern = pattern_info['pattern']
                subject_group = pattern_info['subject_group']
                object_group = pattern_info['object_group']
                
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    try:
                        subject_text = match.group(subject_group).strip()
                        object_text = match.group(object_group).strip()
                        
                        subject_entity = self._find_entity_by_text(subject_text, entities)
                        object_entity = self._find_entity_by_text(object_text, entities)
                        
                        if subject_entity and object_entity:
                            relation = Relation(
                                subject=subject_entity,
                                predicate=relation_type,
                                object=object_entity,
                                confidence=0.7,
                                context=match.group(0)
                            )
                            relations.append(relation)
                    
                    except Exception as e:
                        logger.warning(f"自定义模式匹配错误: {str(e)}")
        
        return relations
    
    def get_relation_statistics(self, relations: List[Relation]) -> Dict[str, Any]:
        """
        获取关系统计信息
        
        Args:
            relations: 关系列表
            
        Returns:
            统计信息字典
        """
        if not relations:
            return {'total_count': 0, 'by_type': {}}
        
        stats = {
            'total_count': len(relations),
            'by_type': {},
            'avg_confidence': sum(r.confidence for r in relations) / len(relations),
            'entity_pairs': set()
        }
        
        # 按类型统计
        for relation in relations:
            rel_type = relation.predicate
            if rel_type not in stats['by_type']:
                stats['by_type'][rel_type] = {
                    'count': 0,
                    'examples': [],
                    'avg_confidence': 0
                }
            
            stats['by_type'][rel_type]['count'] += 1
            if len(stats['by_type'][rel_type]['examples']) < 3:
                example = f"{relation.subject.text} -> {relation.object.text}"
                stats['by_type'][rel_type]['examples'].append(example)
            
            # 记录实体对
            entity_pair = (relation.subject.text, relation.object.text)
            stats['entity_pairs'].add(entity_pair)
        
        # 计算各类型平均置信度
        for rel_type in stats['by_type']:
            type_relations = [r for r in relations if r.predicate == rel_type]
            stats['by_type'][rel_type]['avg_confidence'] = (
                sum(r.confidence for r in type_relations) / len(type_relations)
            )
        
        stats['unique_entity_pairs'] = len(stats['entity_pairs'])
        del stats['entity_pairs']  # 不需要在输出中显示
        
        return stats
    
    def format_relations_output(self, relations: List[Relation]) -> str:
        """
        格式化关系输出
        
        Args:
            relations: 关系列表
            
        Returns:
            格式化后的文本
        """
        if not relations:
            return "未发现关系"
        
        output_lines = []
        for i, relation in enumerate(relations, 1):
            line = f"{i}. {relation.subject.text} --[{relation.predicate}]--> {relation.object.text} (置信度: {relation.confidence:.2f})"
            if relation.context:
                line += f"\n   上下文: {relation.context[:100]}..."
            output_lines.append(line)
        
        return "\n\n".join(output_lines)