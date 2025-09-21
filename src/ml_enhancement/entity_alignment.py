# -*- coding: utf-8 -*-
"""
实体对齐模块
识别和合并重复实体，提高知识图谱质量
"""

import re
from typing import List, Dict, Set, Tuple, Optional, Any
from dataclasses import dataclass
import logging
from collections import defaultdict

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.cluster import DBSCAN
except ImportError:
    TfidfVectorizer = None
    cosine_similarity = None
    DBSCAN = None

try:
    import numpy as np
except ImportError:
    np = None

from ..knowledge_management.domain.model.node import Node
from ..knowledge_management.domain.model.edge import Edge
from ..knowledge_management.domain.model.graph import KnowledgeGraph

logger = logging.getLogger(__name__)


@dataclass
class AlignmentResult:
    """
    对齐结果类
    """
    canonical_entity: Node  # 规范实体
    duplicate_entities: List[Node]  # 重复实体列表
    confidence: float  # 对齐置信度
    alignment_reason: str  # 对齐原因
    merged_properties: Dict[str, Any]  # 合并后的属性


class EntityAlignment:
    """
    实体对齐器
    识别和合并知识图谱中的重复实体
    """
    
    def __init__(self, similarity_threshold: float = 0.8):
        """
        初始化实体对齐器
        
        Args:
            similarity_threshold: 相似度阈值
        """
        self.similarity_threshold = similarity_threshold
        self.vectorizer = None
        
        # 初始化TF-IDF向量化器
        if TfidfVectorizer:
            self.vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words=None,
                ngram_range=(1, 2),
                lowercase=True
            )
        
        # 对齐规则
        self.alignment_rules = self._init_alignment_rules()
    
    def _init_alignment_rules(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        初始化对齐规则
        
        Returns:
            对齐规则字典
        """
        return {
            'exact_match': {
                'weight': 1.0,
                'description': '完全匹配'
            },
            'case_insensitive_match': {
                'weight': 0.95,
                'description': '忽略大小写匹配'
            },
            'punctuation_normalized': {
                'weight': 0.9,
                'description': '标点符号标准化匹配'
            },
            'abbreviation_match': {
                'weight': 0.85,
                'description': '缩写匹配'
            },
            'semantic_similarity': {
                'weight': 0.8,
                'description': '语义相似度匹配'
            },
            'partial_match': {
                'weight': 0.7,
                'description': '部分匹配'
            }
        }
    
    def align_entities(self, kg: KnowledgeGraph) -> List[AlignmentResult]:
        """
        对知识图谱中的实体进行对齐
        
        Args:
            kg: 知识图谱
            
        Returns:
            对齐结果列表
        """
        nodes = kg.get_all_nodes()
        alignment_results = []
        
        # 按实体类型分组
        entities_by_type = defaultdict(list)
        for node in nodes:
            entities_by_type[node.type].append(node)
        
        # 对每种类型的实体进行对齐
        for entity_type, entities in entities_by_type.items():
            if len(entities) < 2:
                continue
            
            logger.info(f"对齐 {entity_type} 类型的 {len(entities)} 个实体")
            type_alignments = self._align_entities_by_type(entities)
            alignment_results.extend(type_alignments)
        
        return alignment_results
    
    def _align_entities_by_type(self, entities: List[Node]) -> List[AlignmentResult]:
        """
        对同类型实体进行对齐
        
        Args:
            entities: 同类型实体列表
            
        Returns:
            对齐结果列表
        """
        alignment_results = []
        processed_entities = set()
        
        for i, entity1 in enumerate(entities):
            if entity1.id in processed_entities:
                continue
            
            duplicates = []
            
            for j, entity2 in enumerate(entities[i+1:], i+1):
                if entity2.id in processed_entities:
                    continue
                
                similarity, reason = self._calculate_entity_similarity(entity1, entity2)
                
                if similarity >= self.similarity_threshold:
                    duplicates.append(entity2)
                    processed_entities.add(entity2.id)
            
            if duplicates:
                # 选择最具代表性的实体作为规范实体
                canonical_entity = self._select_canonical_entity([entity1] + duplicates)
                
                # 合并属性
                merged_properties = self._merge_entity_properties([entity1] + duplicates)
                
                alignment_result = AlignmentResult(
                    canonical_entity=canonical_entity,
                    duplicate_entities=duplicates,
                    confidence=min(0.95, max(similarity for similarity, _ in 
                                   [self._calculate_entity_similarity(canonical_entity, dup) 
                                    for dup in duplicates])),
                    alignment_reason=reason,
                    merged_properties=merged_properties
                )
                
                alignment_results.append(alignment_result)
                processed_entities.add(entity1.id)
        
        # 按相似度排序
        try:
            alignment_results.sort(key=lambda x: x.confidence, reverse=True)
        except TypeError:
            # 如果比较失败，使用默认排序
            alignment_results.sort(key=lambda x: str(x.confidence), reverse=True)
        
        return alignment_results
    
    def _calculate_entity_similarity(self, entity1: Node, entity2: Node) -> Tuple[float, str]:
        """
        计算两个实体的相似度
        
        Args:
            entity1: 实体1
            entity2: 实体2
            
        Returns:
            (相似度, 匹配原因) 元组
        """
        # 1. 完全匹配
        if entity1.label == entity2.label:
            return 1.0, "完全匹配"
        
        # 2. 忽略大小写匹配
        if entity1.label.lower() == entity2.label.lower():
            return 0.95, "忽略大小写匹配"
        
        # 3. 标点符号标准化匹配
        normalized1 = self._normalize_text(entity1.label)
        normalized2 = self._normalize_text(entity2.label)
        if normalized1 == normalized2:
            return 0.9, "标点符号标准化匹配"
        
        # 4. 缩写匹配
        abbrev_sim = self._check_abbreviation_match(entity1.label, entity2.label)
        if abbrev_sim > 0.8:
            return abbrev_sim, "缩写匹配"
        
        # 5. 语义相似度匹配
        if self.vectorizer and cosine_similarity:
            semantic_sim = self._calculate_semantic_similarity(entity1.label, entity2.label)
            if semantic_sim > 0.7:
                return semantic_sim, "语义相似度匹配"
        
        # 6. 部分匹配
        partial_sim = self._calculate_partial_similarity(entity1.label, entity2.label)
        if partial_sim > 0.6:
            return partial_sim, "部分匹配"
        
        # 7. 属性相似度
        property_sim = self._calculate_property_similarity(entity1, entity2)
        if property_sim > 0.7:
            return property_sim, "属性相似度匹配"
        
        return 0.0, "无匹配"
    
    def _normalize_text(self, text: str) -> str:
        """
        标准化文本
        
        Args:
            text: 原始文本
            
        Returns:
            标准化后的文本
        """
        # 去除标点符号和空格
        normalized = re.sub(r'[^\w\u4e00-\u9fff]', '', text.lower())
        return normalized
    
    def _check_abbreviation_match(self, text1: str, text2: str) -> float:
        """
        检查缩写匹配
        
        Args:
            text1: 文本1
            text2: 文本2
            
        Returns:
            缩写匹配相似度
        """
        # 简单的缩写检查
        shorter, longer = (text1, text2) if len(text1) < len(text2) else (text2, text1)
        
        if len(shorter) < 3 or len(longer) < 6:
            return 0.0
        
        # 检查是否为首字母缩写
        if len(shorter) <= 5:
            words = longer.split()
            if len(words) >= len(shorter):
                initials = ''.join(word[0].upper() for word in words[:len(shorter)])
                if initials == shorter.upper():
                    return 0.85
        
        # 检查是否包含关系
        if shorter in longer or longer in shorter:
            return 0.7
        
        return 0.0
    
    def _calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """
        计算语义相似度
        
        Args:
            text1: 文本1
            text2: 文本2
            
        Returns:
            语义相似度
        """
        if not self.vectorizer or not cosine_similarity or not np:
            return 0.0
        
        try:
            # 使用TF-IDF向量化
            texts = [text1, text2]
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            
            # 计算余弦相似度
            similarity_matrix = cosine_similarity(tfidf_matrix)
            return float(similarity_matrix[0, 1])
        
        except Exception as e:
            logger.warning(f"语义相似度计算失败: {str(e)}")
            return 0.0
    
    def _calculate_partial_similarity(self, text1: str, text2: str) -> float:
        """
        计算部分相似度
        
        Args:
            text1: 文本1
            text2: 文本2
            
        Returns:
            部分相似度
        """
        # 使用编辑距离计算相似度
        def levenshtein_distance(s1: str, s2: str) -> int:
            if len(s1) < len(s2):
                return levenshtein_distance(s2, s1)
            
            if len(s2) == 0:
                return len(s1)
            
            previous_row = list(range(len(s2) + 1))
            for i, c1 in enumerate(s1):
                current_row = [i + 1]
                for j, c2 in enumerate(s2):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (c1 != c2)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row
            
            return previous_row[-1]
        
        distance = levenshtein_distance(text1.lower(), text2.lower())
        max_len = max(len(text1), len(text2))
        
        if max_len == 0:
            return 1.0
        
        similarity = 1.0 - (distance / max_len)
        return max(0.0, similarity)
    
    def _calculate_property_similarity(self, entity1: Node, entity2: Node) -> float:
        """
        计算属性相似度
        
        Args:
            entity1: 实体1
            entity2: 实体2
            
        Returns:
            属性相似度
        """
        props1 = entity1.properties or {}
        props2 = entity2.properties or {}
        
        if not props1 and not props2:
            return 0.0
        
        # 计算共同属性的相似度
        common_keys = set(props1.keys()) & set(props2.keys())
        if not common_keys:
            return 0.0
        
        similarities = []
        for key in common_keys:
            val1, val2 = str(props1[key]), str(props2[key])
            if val1 == val2:
                similarities.append(1.0)
            else:
                # 使用部分相似度
                sim = self._calculate_partial_similarity(val1, val2)
                similarities.append(sim)
        
        return sum(similarities) / len(similarities) if similarities else 0.0
    
    def _select_canonical_entity(self, entities: List[Node]) -> Node:
        """
        选择规范实体
        
        Args:
            entities: 实体列表
            
        Returns:
            规范实体
        """
        # 选择标准：
        # 1. 标签最长的
        # 2. 属性最多的
        # 3. ID最小的（保证一致性）
        
        def entity_score(entity: Node) -> Tuple[int, int, str]:
            label_len = len(entity.label)
            prop_count = len(entity.properties or {})
            return (label_len, prop_count, entity.id)
        
        return max(entities, key=entity_score)
    
    def _merge_entity_properties(self, entities: List[Node]) -> Dict[str, Any]:
        """
        合并实体属性
        
        Args:
            entities: 实体列表
            
        Returns:
            合并后的属性字典
        """
        merged_props = {}
        
        for entity in entities:
            if entity.properties:
                for key, value in entity.properties.items():
                    if key not in merged_props:
                        merged_props[key] = value
                    elif merged_props[key] != value:
                        # 如果值不同，保存所有值
                        if not isinstance(merged_props[key], list):
                            merged_props[key] = [merged_props[key]]
                        if value not in merged_props[key]:
                            merged_props[key].append(value)
        
        return merged_props
    
    def apply_alignment_results(self, kg: KnowledgeGraph, 
                               alignment_results: List[AlignmentResult]) -> KnowledgeGraph:
        """
        应用对齐结果到知识图谱
        
        Args:
            kg: 原始知识图谱
            alignment_results: 对齐结果列表
            
        Returns:
            对齐后的知识图谱
        """
        # 创建新的知识图谱
        aligned_kg = KnowledgeGraph()
        
        # 记录需要合并的实体
        entities_to_merge = {}
        canonical_entities = {}
        
        for result in alignment_results:
            canonical_id = result.canonical_entity.id
            canonical_entities[canonical_id] = result.canonical_entity
            
            # 更新规范实体的属性
            result.canonical_entity.properties.update(result.merged_properties)
            
            for duplicate in result.duplicate_entities:
                entities_to_merge[duplicate.id] = canonical_id
        
        # 添加节点
        for node in kg.get_all_nodes():
            if node.id in entities_to_merge:
                # 跳过重复实体
                continue
            elif node.id in canonical_entities:
                # 使用更新后的规范实体
                aligned_kg.add_node(canonical_entities[node.id])
            else:
                # 添加普通实体
                aligned_kg.add_node(node)
        
        # 添加边，更新引用
        for edge in kg.get_all_edges():
            source_id = edge.source_id
            target_id = edge.target_id
            
            # 更新源节点ID
            if source_id in entities_to_merge:
                source_id = entities_to_merge[source_id]
            
            # 更新目标节点ID
            if target_id in entities_to_merge:
                target_id = entities_to_merge[target_id]
            
            # 避免自环
            if source_id != target_id:
                new_edge = Edge(
                    source_id=source_id,
                    target_id=target_id,
                    edge_id=edge.id,
                    label=edge.label,
                    edge_type=edge.type,
                    properties=edge.properties,
                    weight=edge.weight
                )
                aligned_kg.add_edge(new_edge)
        
        return aligned_kg
    
    def get_alignment_statistics(self, alignment_results: List[AlignmentResult]) -> Dict[str, Any]:
        """
        获取对齐统计信息
        
        Args:
            alignment_results: 对齐结果列表
            
        Returns:
            统计信息字典
        """
        if not alignment_results:
            return {
                'total_alignments': 0,
                'total_duplicates_found': 0,
                'avg_confidence': 0.0,
                'alignment_reasons': {}
            }
        
        total_duplicates = sum(len(result.duplicate_entities) for result in alignment_results)
        avg_confidence = sum(result.confidence for result in alignment_results) / len(alignment_results)
        
        # 统计对齐原因
        reason_counts = defaultdict(int)
        for result in alignment_results:
            reason_counts[result.alignment_reason] += 1
        
        return {
            'total_alignments': len(alignment_results),
            'total_duplicates_found': total_duplicates,
            'avg_confidence': avg_confidence,
            'alignment_reasons': dict(reason_counts),
            'entities_reduced': total_duplicates
        }
    
    def cluster_similar_entities(self, entities: List[Node], eps: float = 0.3) -> List[List[Node]]:
        """
        使用聚类算法对相似实体进行分组
        
        Args:
            entities: 实体列表
            eps: DBSCAN聚类参数
            
        Returns:
            实体聚类列表
        """
        if not DBSCAN or not self.vectorizer or len(entities) < 2:
            return [[entity] for entity in entities]
        
        try:
            # 提取实体标签
            labels = [entity.label for entity in entities]
            
            # TF-IDF向量化
            tfidf_matrix = self.vectorizer.fit_transform(labels)
            
            # DBSCAN聚类
            clustering = DBSCAN(eps=eps, min_samples=2, metric='cosine')
            cluster_labels = clustering.fit_predict(tfidf_matrix.toarray())
            
            # 组织聚类结果
            clusters = defaultdict(list)
            for i, cluster_id in enumerate(cluster_labels):
                clusters[cluster_id].append(entities[i])
            
            return list(clusters.values())
        
        except Exception as e:
            logger.error(f"实体聚类失败: {str(e)}")
            return [[entity] for entity in entities]