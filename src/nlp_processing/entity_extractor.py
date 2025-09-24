# -*- coding: utf-8 -*-
"""
实体抽取器
提供命名实体识别和自定义实体抽取功能
"""

import re
from typing import List, Dict, Set, Optional, Tuple, Any
from dataclasses import dataclass, field
import logging

try:
    import spacy
except ImportError:
    spacy = None

from .text_preprocessor import TextPreprocessor

logger = logging.getLogger(__name__)


@dataclass
class Entity:
    """实体数据类"""
    text: str
    label: str
    start: int
    end: int
    confidence: float = 1.0
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def __hash__(self):
        """使Entity可哈希"""
        return hash((self.text, self.label, self.start, self.end))
    
    def __eq__(self, other):
        """实体相等性比较"""
        if not isinstance(other, Entity):
            return False
        return (self.text == other.text and 
                self.label == other.label and
                self.start == other.start and 
                self.end == other.end)


class EntityExtractor:
    """
    实体抽取器类
    支持基于规则和模型的实体识别
    """
    
    def __init__(self, language: str = 'chinese', model_name: str = None):
        """
        初始化实体抽取器
        
        Args:
            language: 语言类型
            model_name: spaCy模型名称
        """
        self.language = language
        self.preprocessor = TextPreprocessor(language)
        self.nlp_model = None
        
        # 尝试加载spaCy模型
        if spacy and model_name:
            try:
                self.nlp_model = spacy.load(model_name)
                logger.info(f"成功加载spaCy模型: {model_name}")
            except Exception as e:
                logger.warning(f"无法加载spaCy模型 {model_name}: {str(e)}")
        
        # 初始化规则模式
        self.rule_patterns = self._init_rule_patterns()
        
        # 自定义实体类型
        self.custom_entity_types = {}
    
    def _init_rule_patterns(self) -> Dict[str, List[str]]:
        """
        初始化规则模式
        
        Returns:
            规则模式字典
        """
        if self.language == 'chinese':
            return {
                'PERSON': [
                    # 基本人名模式
                    r'[\u4e00-\u9fff]{2,4}(?:先生|女士|老师|教授|博士|硕士|经理|总监|主任|局长|市长|省长)',
                    r'(?:先生|女士|老师|教授|博士|硕士|经理|总监|主任|局长|市长|省长)[\u4e00-\u9fff]{2,4}',
                    r'[\u4e00-\u9fff]{2,4}(?:同志|同学)',
                    # 增强的人名识别
                    r'(?:我是|我叫|姓名是|名字是|联系)[\u4e00-\u9fff]{2,4}',
                    r'[\u4e00-\u9fff]{2,4}(?=，|。|！|？|来自|工作|负责)',
                    r'(?:销售经理|采购经理|项目经理|部门经理|总经理)[\u4e00-\u9fff]{2,4}',
                    # 常见中文姓名
                    r'(?:张|李|王|刘|陈|杨|赵|黄|周|吴|徐|孙|胡|朱|高|林|何|郭|马|罗|梁|宋|郑|谢|韩|唐|冯|于|董|萧|程|曹|袁|邓|许|傅|沈|曾|彭|吕|苏|卢|蒋|蔡|贾|丁|魏|薛|叶|阎|余|潘|杜|戴|夏|钟|汪|田|任|姜|范|方|石|姚|谭|廖|邹|熊|金|陆|郝|孔|白|崔|康|毛|邱|秦|江|史|顾|侯|邵|孟|龙|万|段|雷|钱|汤|尹|黎|易|常|武|乔|贺|赖|龚|文)[\u4e00-\u9fff]{1,3}',
                ],
                'ORG': [
                    # 基本公司模式
                    r'[\u4e00-\u9fff]+(?:公司|企业|集团|有限公司|股份有限公司|科技|技术)',
                    r'[\u4e00-\u9fff]+(?:大学|学院|学校|研究所|研究院|实验室)',
                    r'[\u4e00-\u9fff]+(?:医院|银行|政府|部门|局|委|办)',
                    r'[\u4e00-\u9fff]+(?:省|市|县|区|镇|村)(?:政府|委员会)?',
                    # 增强的公司识别
                    r'(?:ABC|XYZ|华为|腾讯|阿里巴巴|百度|京东|小米|字节跳动|美团|滴滴|网易|新浪|搜狐|360|联想|海尔|格力|美的|TCL|中兴|OPPO|vivo|一加)(?:公司|集团|科技)?',
                    r'[A-Z]{2,}(?:公司|集团|科技|技术|有限公司)',
                    r'(?:我们公司|贵公司|本公司|该公司)',
                ],
                'LOC': [
                    # 基本地点模式
                    r'[\u4e00-\u9fff]+(?:省|市|县|区|镇|村|街道|路|街|巷|号)',
                    r'(?:北京|上海|天津|重庆|广州|深圳|杭州|南京|武汉|成都|西安|沈阳|大连|青岛|厦门|宁波|苏州|无锡|佛山|东莞|中山|珠海|惠州|江门|汕头|湛江|肇庆|梅州|茂名|阳江|韶关|清远|潮州|揭阳|云浮|河源)',
                    r'[\u4e00-\u9fff]+(?:国|州|洲|岛|山|河|湖|海|港|湾)',
                    # 增强的地点识别
                    r'(?:来自|位于|在)[\u4e00-\u9fff]{2,6}(?:市|省|区|县)',
                ],
                'PRODUCT': [
                     # 电子产品
                     r'(?:手机|平板电脑|笔记本电脑|台式电脑|智能手机|智能手表|耳机|音响|电视|显示器)',
                     r'(?:iPhone|iPad|MacBook|Surface|Galaxy|华为|小米|OPPO|vivo|一加)\s*[\w\d]*',
                     r'电子产品',
                     # 其他产品
                     r'[\u4e00-\u9fff]*(?:产品|设备|器材|工具|软件|系统|平台)',
                 ],
                 'CONTACT': [
                     # 联系方式
                     r'(?:联系|请联系|可联系)[\u4e00-\u9fff]{2,4}',
                     r'(?:销售|客服|技术|商务)(?:经理|专员|代表|人员)',
                 ],
                'TIME': [
                    r'\d{4}年\d{1,2}月\d{1,2}日',
                    r'\d{4}-\d{1,2}-\d{1,2}',
                    r'\d{1,2}月\d{1,2}日',
                    r'(?:今天|明天|昨天|前天|后天)',
                    r'(?:上午|下午|晚上|凌晨)\d{1,2}[：:]\d{2}',
                    r'\d{1,2}[：:]\d{2}'
                ],
                'MONEY': [
                    r'\d+(?:\.\d+)?(?:元|万元|亿元|美元|欧元|英镑|日元)',
                    r'[￥$€£¥]\d+(?:\.\d+)?',
                    r'\d+(?:\.\d+)?万',
                    r'\d+(?:\.\d+)?亿'
                ],
                'PHONE': [
                    r'1[3-9]\d{9}',
                    r'\d{3,4}-\d{7,8}',
                    r'\(\d{3,4}\)\d{7,8}'
                ],
                'EMAIL': [
                    r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                ],
                'ID_CARD': [
                    r'\d{17}[\dXx]',
                    r'\d{15}'
                ]
            }
        else:
            return {
                'PERSON': [
                    r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',
                    r'\b(?:Mr|Mrs|Ms|Dr|Prof)\. [A-Z][a-z]+\b'
                ],
                'ORG': [
                    r'\b[A-Z][a-zA-Z\s]+ (?:Inc|Corp|Ltd|LLC|Company|University|College|Institute)\b',
                    r'\b(?:Apple|Google|Microsoft|Amazon|Facebook|Tesla|IBM|Oracle)\b'
                ],
                'LOC': [
                    r'\b[A-Z][a-zA-Z\s]+ (?:City|State|Country|Street|Avenue|Road|Boulevard)\b',
                    r'\b(?:New York|Los Angeles|Chicago|Houston|Phoenix|Philadelphia|San Antonio|San Diego|Dallas|San Jose)\b'
                ],
                'TIME': [
                    r'\b\d{1,2}/\d{1,2}/\d{4}\b',
                    r'\b\d{4}-\d{2}-\d{2}\b',
                    r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4}\b',
                    r'\b\d{1,2}:\d{2} (?:AM|PM)\b'
                ],
                'MONEY': [
                    r'\$\d+(?:,\d{3})*(?:\.\d{2})?',
                    r'\b\d+(?:,\d{3})* dollars?\b',
                    r'\b\d+(?:,\d{3})* (?:USD|EUR|GBP|JPY)\b'
                ],
                'PHONE': [
                    r'\b\d{3}-\d{3}-\d{4}\b',
                    r'\(\d{3}\) \d{3}-\d{4}',
                    r'\+\d{1,3} \d{3} \d{3} \d{4}'
                ],
                'EMAIL': [
                    r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                ]
            }
    
    def extract_entities_by_rules(self, text: str) -> List[Entity]:
        """
        基于规则的实体抽取
        
        Args:
            text: 输入文本
            
        Returns:
            实体列表
        """
        entities = []
        
        for entity_type, patterns in self.rule_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text)
                for match in matches:
                    entity = Entity(
                        text=match.group(),
                        label=entity_type,
                        start=match.start(),
                        end=match.end(),
                        confidence=0.8  # 规则匹配的置信度设为0.8
                    )
                    entities.append(entity)
        
        # 去重和排序
        entities = self._deduplicate_entities(entities)
        entities.sort(key=lambda x: x.start)
        
        return entities
    
    def extract_entities_by_model(self, text: str) -> List[Entity]:
        """
        基于模型的实体抽取
        
        Args:
            text: 输入文本
            
        Returns:
            实体列表
        """
        if not self.nlp_model:
            logger.warning("NLP模型未加载，无法进行模型实体抽取")
            return []
        
        entities = []
        
        try:
            doc = self.nlp_model(text)
            
            for ent in doc.ents:
                entity = Entity(
                    text=ent.text,
                    label=ent.label_,
                    start=ent.start_char,
                    end=ent.end_char,
                    confidence=0.9  # 模型预测的置信度设为0.9
                )
                entities.append(entity)
        
        except Exception as e:
            logger.error(f"模型实体抽取失败: {str(e)}")
        
        return entities
    
    def extract_custom_entities(self, text: str, entity_patterns: Dict[str, List[str]]) -> List[Entity]:
        """
        抽取自定义实体
        
        Args:
            text: 输入文本
            entity_patterns: 自定义实体模式字典
            
        Returns:
            实体列表
        """
        entities = []
        
        for entity_type, patterns in entity_patterns.items():
            for pattern in patterns:
                try:
                    matches = re.finditer(pattern, text)
                    for match in matches:
                        entity = Entity(
                            text=match.group(),
                            label=entity_type,
                            start=match.start(),
                            end=match.end(),
                            confidence=0.7  # 自定义规则的置信度设为0.7
                        )
                        entities.append(entity)
                except re.error as e:
                    logger.error(f"正则表达式错误 {pattern}: {str(e)}")
        
        return entities
    
    def extract_entities(self, text: str, 
                        use_rules: bool = True,
                        use_model: bool = True,
                        custom_patterns: Dict[str, List[str]] = None) -> List[Entity]:
        """
        综合实体抽取
        
        Args:
            text: 输入文本
            use_rules: 是否使用规则抽取
            use_model: 是否使用模型抽取
            custom_patterns: 自定义实体模式
            
        Returns:
            实体列表
        """
        all_entities = []
        
        # 规则抽取
        if use_rules:
            rule_entities = self.extract_entities_by_rules(text)
            all_entities.extend(rule_entities)
        
        # 模型抽取
        if use_model:
            model_entities = self.extract_entities_by_model(text)
            all_entities.extend(model_entities)
        
        # 自定义抽取
        if custom_patterns:
            custom_entities = self.extract_custom_entities(text, custom_patterns)
            all_entities.extend(custom_entities)
        
        # 去重和合并
        merged_entities = self._merge_overlapping_entities(all_entities)
        merged_entities.sort(key=lambda x: x.start)
        
        return merged_entities
    
    def _deduplicate_entities(self, entities: List[Entity]) -> List[Entity]:
        """
        去除重复实体
        
        Args:
            entities: 实体列表
            
        Returns:
            去重后的实体列表
        """
        seen = set()
        unique_entities = []
        
        for entity in entities:
            key = (entity.text, entity.label, entity.start, entity.end)
            if key not in seen:
                seen.add(key)
                unique_entities.append(entity)
        
        return unique_entities
    
    def _merge_overlapping_entities(self, entities: List[Entity]) -> List[Entity]:
        """
        合并重叠的实体
        
        Args:
            entities: 实体列表
            
        Returns:
            合并后的实体列表
        """
        if not entities:
            return []
        
        # 按起始位置排序
        entities.sort(key=lambda x: (x.start, x.end))
        
        merged = []
        current = entities[0]
        
        for next_entity in entities[1:]:
            # 检查是否重叠
            if self._entities_overlap(current, next_entity):
                # 选择置信度更高的实体，或者更长的实体
                if (next_entity.confidence > current.confidence or 
                    (next_entity.confidence == current.confidence and 
                     len(next_entity.text) > len(current.text))):
                    current = next_entity
            else:
                merged.append(current)
                current = next_entity
        
        merged.append(current)
        return merged
    
    def _entities_overlap(self, entity1: Entity, entity2: Entity) -> bool:
        """
        检查两个实体是否重叠
        
        Args:
            entity1: 实体1
            entity2: 实体2
            
        Returns:
            是否重叠
        """
        return not (entity1.end <= entity2.start or entity2.end <= entity1.start)
    
    def add_custom_entity_type(self, entity_type: str, patterns: List[str]):
        """
        添加自定义实体类型
        
        Args:
            entity_type: 实体类型名称
            patterns: 正则表达式模式列表
        """
        self.custom_entity_types[entity_type] = patterns
        logger.info(f"添加自定义实体类型: {entity_type}")
    
    def get_entity_statistics(self, entities: List[Entity]) -> Dict[str, Any]:
        """
        获取实体统计信息
        
        Args:
            entities: 实体列表
            
        Returns:
            统计信息字典
        """
        if not entities:
            return {'total_count': 0, 'by_type': {}}
        
        stats = {
            'total_count': len(entities),
            'by_type': {},
            'avg_confidence': sum(e.confidence for e in entities) / len(entities),
            'confidence_distribution': {}
        }
        
        # 按类型统计
        for entity in entities:
            entity_type = entity.label
            if entity_type not in stats['by_type']:
                stats['by_type'][entity_type] = {
                    'count': 0,
                    'examples': [],
                    'avg_confidence': 0
                }
            
            stats['by_type'][entity_type]['count'] += 1
            if len(stats['by_type'][entity_type]['examples']) < 5:
                stats['by_type'][entity_type]['examples'].append(entity.text)
        
        # 计算各类型平均置信度
        for entity_type in stats['by_type']:
            type_entities = [e for e in entities if e.label == entity_type]
            stats['by_type'][entity_type]['avg_confidence'] = (
                sum(e.confidence for e in type_entities) / len(type_entities)
            )
        
        # 置信度分布
        confidence_ranges = [(0.0, 0.5), (0.5, 0.7), (0.7, 0.9), (0.9, 1.0)]
        for low, high in confidence_ranges:
            range_key = f"{low}-{high}"
            count = sum(1 for e in entities if low <= e.confidence < high)
            stats['confidence_distribution'][range_key] = count
        
        return stats
    
    def extract_entities_from_sentences(self, sentences: List[str]) -> Dict[int, List[Entity]]:
        """
        从句子列表中抽取实体
        
        Args:
            sentences: 句子列表
            
        Returns:
            句子索引到实体列表的映射
        """
        results = {}
        
        for i, sentence in enumerate(sentences):
            entities = self.extract_entities(sentence)
            if entities:
                results[i] = entities
        
        return results
    
    def format_entities_output(self, text: str, entities: List[Entity]) -> str:
        """
        格式化实体输出，用于可视化
        
        Args:
            text: 原始文本
            entities: 实体列表
            
        Returns:
            格式化后的文本
        """
        if not entities:
            return text
        
        # 按起始位置倒序排序，避免位置偏移
        entities.sort(key=lambda x: x.start, reverse=True)
        
        result = text
        for entity in entities:
            # 插入标记
            marked_text = f"[{entity.text}]({entity.label}:{entity.confidence:.2f})"
            result = result[:entity.start] + marked_text + result[entity.end:]
        
        return result