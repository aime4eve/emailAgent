# -*- coding: utf-8 -*-
"""
机器学习模型定义
定义用于知识图谱增强的各种ML模型
"""

from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from datetime import datetime

from .node import Node
from .edge import Edge
from .graph import KnowledgeGraph


class SimilarityMethod(Enum):
    """相似度计算方法枚举"""
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    JACCARD = "jaccard"
    SEMANTIC = "semantic"


class InferenceMethod(Enum):
    """推理方法枚举"""
    RULE_BASED = "rule_based"
    EMBEDDING_BASED = "embedding_based"
    GRAPH_NEURAL_NETWORK = "gnn"
    STATISTICAL = "statistical"


@dataclass
class SimilarityResult:
    """相似度计算结果"""
    entity1_id: str
    entity2_id: str
    similarity_score: float
    method: SimilarityMethod
    confidence: float
    computed_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'entity1_id': self.entity1_id,
            'entity2_id': self.entity2_id,
            'similarity_score': self.similarity_score,
            'method': self.method.value,
            'confidence': self.confidence,
            'computed_at': self.computed_at.isoformat(),
            'metadata': self.metadata
        }


@dataclass
class InferenceResult:
    """推理结果"""
    source_entity_id: str
    target_entity_id: str
    relation_type: str
    confidence: float
    method: InferenceMethod
    evidence: List[str] = field(default_factory=list)
    computed_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'source_entity_id': self.source_entity_id,
            'target_entity_id': self.target_entity_id,
            'relation_type': self.relation_type,
            'confidence': self.confidence,
            'method': self.method.value,
            'evidence': self.evidence,
            'computed_at': self.computed_at.isoformat(),
            'metadata': self.metadata
        }


@dataclass
class AlignmentResult:
    """实体对齐结果"""
    entity1: Node
    entity2: Node
    alignment_score: float
    alignment_type: str  # 'exact', 'partial', 'semantic'
    confidence: float
    reasons: List[str] = field(default_factory=list)
    computed_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'entity1': self.entity1.to_dict(),
            'entity2': self.entity2.to_dict(),
            'alignment_score': self.alignment_score,
            'alignment_type': self.alignment_type,
            'confidence': self.confidence,
            'reasons': self.reasons,
            'computed_at': self.computed_at.isoformat()
        }


@dataclass
class ResolutionResult:
    """语义消解结果"""
    original_entity: Node
    resolved_entity: Node
    resolution_type: str  # 'disambiguation', 'normalization', 'canonicalization'
    confidence: float
    context_used: Dict[str, Any] = field(default_factory=dict)
    computed_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'original_entity': self.original_entity.to_dict(),
            'resolved_entity': self.resolved_entity.to_dict(),
            'resolution_type': self.resolution_type,
            'confidence': self.confidence,
            'context_used': self.context_used,
            'computed_at': self.computed_at.isoformat()
        }


class EntitySimilarity:
    """实体相似度模型"""
    
    def __init__(self, default_method: SimilarityMethod = SimilarityMethod.COSINE):
        """
        初始化实体相似度模型
        
        Args:
            default_method: 默认相似度计算方法
        """
        self.default_method = default_method
        self.similarity_cache = {}
    
    def calculate(self, embedding1: np.ndarray, embedding2: np.ndarray, 
                 method: Optional[SimilarityMethod] = None) -> float:
        """
        计算两个实体嵌入向量的相似度
        
        Args:
            embedding1: 第一个实体的嵌入向量
            embedding2: 第二个实体的嵌入向量
            method: 相似度计算方法
            
        Returns:
            相似度分数 (0-1)
        """
        if method is None:
            method = self.default_method
        
        if method == SimilarityMethod.COSINE:
            return self._cosine_similarity(embedding1, embedding2)
        elif method == SimilarityMethod.EUCLIDEAN:
            return self._euclidean_similarity(embedding1, embedding2)
        else:
            raise ValueError(f"不支持的相似度计算方法: {method}")
    
    def calculate_semantic_similarity(self, entity1: Node, entity2: Node, 
                                    context1: Dict[str, Any], context2: Dict[str, Any]) -> SimilarityResult:
        """
        计算语义相似度
        
        Args:
            entity1: 第一个实体
            entity2: 第二个实体
            context1: 第一个实体的上下文
            context2: 第二个实体的上下文
            
        Returns:
            相似度结果
        """
        # 综合考虑标签、类型、属性和上下文的相似度
        label_sim = self._text_similarity(entity1.label, entity2.label)
        type_sim = 1.0 if entity1.type == entity2.type else 0.0
        property_sim = self._property_similarity(entity1.properties, entity2.properties)
        context_sim = self._context_similarity(context1, context2)
        
        # 加权平均
        weights = [0.3, 0.2, 0.3, 0.2]  # 标签、类型、属性、上下文权重
        similarities = [label_sim, type_sim, property_sim, context_sim]
        
        overall_similarity = sum(w * s for w, s in zip(weights, similarities))
        confidence = min(0.9, overall_similarity + 0.1)  # 置信度略高于相似度
        
        return SimilarityResult(
            entity1_id=entity1.id,
            entity2_id=entity2.id,
            similarity_score=overall_similarity,
            method=SimilarityMethod.SEMANTIC,
            confidence=confidence,
            metadata={
                'label_similarity': label_sim,
                'type_similarity': type_sim,
                'property_similarity': property_sim,
                'context_similarity': context_sim
            }
        )
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """计算余弦相似度"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def _euclidean_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """计算欧几里得相似度"""
        distance = np.linalg.norm(vec1 - vec2)
        # 转换为相似度 (0-1)
        return 1.0 / (1.0 + distance)
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度"""
        if not text1 or not text2:
            return 0.0
        
        # 简单的字符级相似度
        set1 = set(text1.lower())
        set2 = set(text2.lower())
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    def _property_similarity(self, props1: Dict[str, Any], props2: Dict[str, Any]) -> float:
        """计算属性相似度"""
        if not props1 and not props2:
            return 1.0
        
        if not props1 or not props2:
            return 0.0
        
        common_keys = set(props1.keys()).intersection(set(props2.keys()))
        all_keys = set(props1.keys()).union(set(props2.keys()))
        
        if not all_keys:
            return 1.0
        
        # 计算共同属性的值相似度
        value_similarities = []
        for key in common_keys:
            val1, val2 = props1[key], props2[key]
            if val1 == val2:
                value_similarities.append(1.0)
            elif isinstance(val1, str) and isinstance(val2, str):
                value_similarities.append(self._text_similarity(val1, val2))
            else:
                value_similarities.append(0.0)
        
        # 综合相似度
        key_similarity = len(common_keys) / len(all_keys)
        value_similarity = np.mean(value_similarities) if value_similarities else 0.0
        
        return (key_similarity + value_similarity) / 2
    
    def _context_similarity(self, context1: Dict[str, Any], context2: Dict[str, Any]) -> float:
        """计算上下文相似度"""
        # 比较邻居节点和关系的相似度
        neighbors1 = set(n.type for n in context1.get('neighbors', []) if n.type)
        neighbors2 = set(n.type for n in context2.get('neighbors', []) if n.type)
        
        relations1 = set(context1.get('relations', []))
        relations2 = set(context2.get('relations', []))
        
        # 计算邻居类型相似度
        neighbor_sim = 0.0
        if neighbors1 or neighbors2:
            intersection = len(neighbors1.intersection(neighbors2))
            union = len(neighbors1.union(neighbors2))
            neighbor_sim = intersection / union if union > 0 else 0.0
        
        # 计算关系类型相似度
        relation_sim = 0.0
        if relations1 or relations2:
            intersection = len(relations1.intersection(relations2))
            union = len(relations1.union(relations2))
            relation_sim = intersection / union if union > 0 else 0.0
        
        return (neighbor_sim + relation_sim) / 2


class RelationInference:
    """关系推理模型"""
    
    def __init__(self):
        """
        初始化关系推理模型
        """
        self.inference_rules = self._load_inference_rules()
        self.confidence_threshold = 0.5
    
    def infer_relation(self, kg: KnowledgeGraph, entity1: Node, entity2: Node) -> Optional[InferenceResult]:
        """
        推断两个实体间的关系
        
        Args:
            kg: 知识图谱
            entity1: 源实体
            entity2: 目标实体
            
        Returns:
            推理结果，如果无法推断则返回None
        """
        # 尝试不同的推理方法
        results = []
        
        # 基于规则的推理
        rule_result = self._rule_based_inference(kg, entity1, entity2)
        if rule_result:
            results.append(rule_result)
        
        # 基于路径的推理
        path_result = self._path_based_inference(kg, entity1, entity2)
        if path_result:
            results.append(path_result)
        
        # 基于类型的推理
        type_result = self._type_based_inference(kg, entity1, entity2)
        if type_result:
            results.append(type_result)
        
        # 选择置信度最高的结果
        if results:
            best_result = max(results, key=lambda r: r.confidence)
            if best_result.confidence >= self.confidence_threshold:
                return best_result
        
        return None
    
    def _rule_based_inference(self, kg: KnowledgeGraph, entity1: Node, entity2: Node) -> Optional[InferenceResult]:
        """基于规则的关系推理"""
        for rule in self.inference_rules:
            if self._match_rule(kg, entity1, entity2, rule):
                return InferenceResult(
                    source_entity_id=entity1.id,
                    target_entity_id=entity2.id,
                    relation_type=rule['inferred_relation'],
                    confidence=rule['confidence'],
                    method=InferenceMethod.RULE_BASED,
                    evidence=[rule['description']]
                )
        return None
    
    def _path_based_inference(self, kg: KnowledgeGraph, entity1: Node, entity2: Node) -> Optional[InferenceResult]:
        """基于路径的关系推理"""
        # 查找两个实体间的路径
        paths = self._find_paths(kg, entity1.id, entity2.id, max_length=3)
        
        for path in paths:
            inferred_relation = self._infer_from_path(path)
            if inferred_relation:
                confidence = self._calculate_path_confidence(path)
                return InferenceResult(
                    source_entity_id=entity1.id,
                    target_entity_id=entity2.id,
                    relation_type=inferred_relation,
                    confidence=confidence,
                    method=InferenceMethod.STATISTICAL,
                    evidence=[f"路径推理: {' -> '.join(path)}"]
                )
        
        return None
    
    def _type_based_inference(self, kg: KnowledgeGraph, entity1: Node, entity2: Node) -> Optional[InferenceResult]:
        """基于类型的关系推理"""
        type1 = entity1.type
        type2 = entity2.type
        
        if not type1 or not type2:
            return None
        
        # 基于类型的关系映射
        type_relations = {
            ('Person', 'Person'): [('colleague', 0.6), ('friend', 0.5)],
            ('Person', 'Organization'): [('works_for', 0.7), ('member_of', 0.6)],
            ('Organization', 'Organization'): [('partner', 0.5), ('subsidiary', 0.4)]
        }
        
        possible_relations = type_relations.get((type1, type2), [])
        if possible_relations:
            relation, confidence = possible_relations[0]  # 选择最可能的关系
            return InferenceResult(
                source_entity_id=entity1.id,
                target_entity_id=entity2.id,
                relation_type=relation,
                confidence=confidence,
                method=InferenceMethod.STATISTICAL,
                evidence=[f"基于类型推理: {type1} -> {type2}"]
            )
        
        return None
    
    def _load_inference_rules(self) -> List[Dict[str, Any]]:
        """加载推理规则"""
        return [
            {
                'name': 'transitivity',
                'pattern': ['A', 'works_for', 'B', 'subsidiary_of', 'C'],
                'inferred_relation': 'works_for',
                'confidence': 0.8,
                'description': '传递性规则：如果A为B工作，B是C的子公司，则A为C工作'
            },
            {
                'name': 'colleague_inference',
                'pattern': ['A', 'works_for', 'X', 'works_for', 'B'],
                'inferred_relation': 'colleague',
                'confidence': 0.7,
                'description': '同事推理：如果A和B都为同一组织工作，则他们是同事'
            }
        ]
    
    def _match_rule(self, kg: KnowledgeGraph, entity1: Node, entity2: Node, rule: Dict[str, Any]) -> bool:
        """匹配推理规则"""
        # 简化的规则匹配逻辑
        pattern = rule['pattern']
        if len(pattern) == 5:  # A-rel1-B-rel2-C 模式
            # 查找中间节点
            edges1 = kg.get_edges_by_node(entity1.id)
            edges2 = kg.get_edges_by_node(entity2.id)
            
            for edge1 in edges1:
                if edge1.type == pattern[1]:  # 匹配第一个关系
                    intermediate_id = edge1.target_id if edge1.source_id == entity1.id else edge1.source_id
                    
                    for edge2 in edges2:
                        if (edge2.type == pattern[3] and  # 匹配第二个关系
                            (edge2.source_id == intermediate_id or edge2.target_id == intermediate_id)):
                            return True
        
        return False
    
    def _find_paths(self, kg: KnowledgeGraph, start_id: str, end_id: str, max_length: int) -> List[List[str]]:
        """查找两个节点间的路径"""
        paths = []
        visited = set()
        
        def dfs(current_id: str, target_id: str, path: List[str], depth: int):
            if depth > max_length:
                return
            
            if current_id == target_id and len(path) > 1:
                paths.append(path.copy())
                return
            
            if current_id in visited:
                return
            
            visited.add(current_id)
            edges = kg.get_edges_by_node(current_id)
            
            for edge in edges:
                next_id = edge.target_id if edge.source_id == current_id else edge.source_id
                if next_id not in visited:
                    path.append(edge.type or 'unknown')
                    dfs(next_id, target_id, path, depth + 1)
                    path.pop()
            
            visited.remove(current_id)
        
        dfs(start_id, end_id, [], 0)
        return paths[:5]  # 限制返回路径数量
    
    def _infer_from_path(self, path: List[str]) -> Optional[str]:
        """从路径推断关系"""
        # 简化的路径推理逻辑
        if len(path) == 2:
            rel1, rel2 = path
            if rel1 == 'works_for' and rel2 == 'works_for':
                return 'colleague'
            elif rel1 == 'friend' and rel2 == 'friend':
                return 'friend'  # 朋友的朋友可能是朋友
        
        return None
    
    def _calculate_path_confidence(self, path: List[str]) -> float:
        """计算路径推理的置信度"""
        # 路径越短，置信度越高
        base_confidence = 0.8
        length_penalty = 0.1 * (len(path) - 1)
        return max(0.1, base_confidence - length_penalty)


class EntityAlignment:
    """实体对齐模型"""
    
    def __init__(self):
        """
        初始化实体对齐模型
        """
        self.alignment_threshold = 0.8
        self.entity_similarity = EntitySimilarity()
    
    def calculate_similarity(self, entity1: Node, entity2: Node, 
                           embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        计算两个实体的对齐相似度
        
        Args:
            entity1: 第一个实体
            entity2: 第二个实体
            embedding1: 第一个实体的嵌入向量
            embedding2: 第二个实体的嵌入向量
            
        Returns:
            对齐相似度分数
        """
        # 综合多种相似度
        embedding_sim = self.entity_similarity.calculate(embedding1, embedding2)
        label_sim = self._label_similarity(entity1.label, entity2.label)
        type_sim = 1.0 if entity1.type == entity2.type else 0.0
        property_sim = self._property_alignment_similarity(entity1.properties, entity2.properties)
        
        # 加权计算
        weights = [0.4, 0.3, 0.1, 0.2]
        similarities = [embedding_sim, label_sim, type_sim, property_sim]
        
        return sum(w * s for w, s in zip(weights, similarities))
    
    def align_entities(self, entities1: List[Node], entities2: List[Node]) -> List[AlignmentResult]:
        """
        对齐两个实体集合
        
        Args:
            entities1: 第一个实体集合
            entities2: 第二个实体集合
            
        Returns:
            对齐结果列表
        """
        alignments = []
        
        for entity1 in entities1:
            best_match = None
            best_score = 0.0
            
            for entity2 in entities2:
                # 这里需要实际的嵌入向量，简化处理
                dummy_embedding1 = np.random.rand(100)  # 实际应用中应该是真实的嵌入
                dummy_embedding2 = np.random.rand(100)
                
                similarity = self.calculate_similarity(
                    entity1, entity2, dummy_embedding1, dummy_embedding2
                )
                
                if similarity > best_score and similarity >= self.alignment_threshold:
                    best_score = similarity
                    best_match = entity2
            
            if best_match:
                alignment_type = self._determine_alignment_type(entity1, best_match, best_score)
                alignments.append(AlignmentResult(
                    entity1=entity1,
                    entity2=best_match,
                    alignment_score=best_score,
                    alignment_type=alignment_type,
                    confidence=min(0.95, best_score + 0.1),
                    reasons=self._get_alignment_reasons(entity1, best_match)
                ))
        
        return alignments
    
    def _label_similarity(self, label1: str, label2: str) -> float:
        """计算标签相似度"""
        if not label1 or not label2:
            return 0.0
        
        # 精确匹配
        if label1.lower() == label2.lower():
            return 1.0
        
        # 包含关系
        if label1.lower() in label2.lower() or label2.lower() in label1.lower():
            return 0.8
        
        # 字符级相似度
        return self.entity_similarity._text_similarity(label1, label2)
    
    def _property_alignment_similarity(self, props1: Dict[str, Any], props2: Dict[str, Any]) -> float:
        """计算属性对齐相似度"""
        return self.entity_similarity._property_similarity(props1, props2)
    
    def _determine_alignment_type(self, entity1: Node, entity2: Node, score: float) -> str:
        """确定对齐类型"""
        if score >= 0.95:
            return 'exact'
        elif score >= 0.8:
            return 'semantic'
        else:
            return 'partial'
    
    def _get_alignment_reasons(self, entity1: Node, entity2: Node) -> List[str]:
        """获取对齐原因"""
        reasons = []
        
        if entity1.label.lower() == entity2.label.lower():
            reasons.append('标签完全匹配')
        elif entity1.label.lower() in entity2.label.lower() or entity2.label.lower() in entity1.label.lower():
            reasons.append('标签部分匹配')
        
        if entity1.type == entity2.type:
            reasons.append('类型匹配')
        
        common_props = set(entity1.properties.keys()).intersection(set(entity2.properties.keys()))
        if common_props:
            reasons.append(f'共同属性: {", ".join(list(common_props)[:3])}')
        
        return reasons


class SemanticResolver:
    """语义消解模型"""
    
    def __init__(self):
        """
        初始化语义消解模型
        """
        self.resolution_strategies = {
            'disambiguation': self._disambiguation_strategy,
            'normalization': self._normalization_strategy,
            'canonicalization': self._canonicalization_strategy
        }
    
    def resolve(self, entity: Node, embedding: np.ndarray, context: Dict[str, Any]) -> Node:
        """
        对实体进行语义消解
        
        Args:
            entity: 原始实体
            embedding: 实体嵌入向量
            context: 上下文信息
            
        Returns:
            消解后的实体
        """
        # 确定消解策略
        strategy = self._determine_resolution_strategy(entity, context)
        
        # 应用消解策略
        resolver_func = self.resolution_strategies.get(strategy, self._disambiguation_strategy)
        resolved_entity = resolver_func(entity, embedding, context)
        
        return resolved_entity
    
    def _determine_resolution_strategy(self, entity: Node, context: Dict[str, Any]) -> str:
        """确定消解策略"""
        # 如果实体标签有多种可能含义，使用消歧策略
        if self._is_ambiguous(entity):
            return 'disambiguation'
        
        # 如果实体标签需要标准化，使用标准化策略
        if self._needs_normalization(entity):
            return 'normalization'
        
        # 默认使用规范化策略
        return 'canonicalization'
    
    def _disambiguation_strategy(self, entity: Node, embedding: np.ndarray, context: Dict[str, Any]) -> Node:
        """消歧策略"""
        # 基于上下文进行消歧
        resolved_entity = entity.copy()
        
        # 根据邻居节点类型确定实体的具体含义
        neighbor_types = [n.type for n in context.get('neighbors', []) if n.type]
        
        if 'Organization' in neighbor_types and entity.type == 'Person':
            # 如果邻居中有组织，且实体是人，可能是员工
            resolved_entity.properties['role'] = 'employee'
        elif 'Project' in neighbor_types and entity.type == 'Person':
            # 如果邻居中有项目，且实体是人，可能是项目成员
            resolved_entity.properties['role'] = 'project_member'
        
        return resolved_entity
    
    def _normalization_strategy(self, entity: Node, embedding: np.ndarray, context: Dict[str, Any]) -> Node:
        """标准化策略"""
        resolved_entity = entity.copy()
        
        # 标准化实体标签
        normalized_label = self._normalize_label(entity.label)
        resolved_entity.label = normalized_label
        
        # 标准化属性值
        normalized_properties = self._normalize_properties(entity.properties)
        resolved_entity.properties.update(normalized_properties)
        
        return resolved_entity
    
    def _canonicalization_strategy(self, entity: Node, embedding: np.ndarray, context: Dict[str, Any]) -> Node:
        """规范化策略"""
        resolved_entity = entity.copy()
        
        # 使用规范形式
        canonical_form = self._get_canonical_form(entity)
        if canonical_form:
            resolved_entity.label = canonical_form
            resolved_entity.properties['canonical'] = True
        
        return resolved_entity
    
    def _is_ambiguous(self, entity: Node) -> bool:
        """判断实体是否存在歧义"""
        # 简化的歧义检测逻辑
        ambiguous_terms = ['apple', 'bank', 'java', 'python']  # 示例歧义词
        return entity.label.lower() in ambiguous_terms
    
    def _needs_normalization(self, entity: Node) -> bool:
        """判断实体是否需要标准化"""
        # 检查标签是否包含特殊字符、大小写不一致等
        label = entity.label
        return (
            label != label.strip() or  # 包含前后空格
            label.isupper() or label.islower() or  # 全大写或全小写
            any(char in label for char in ['_', '-', '.'])  # 包含特殊字符
        )
    
    def _normalize_label(self, label: str) -> str:
        """标准化标签"""
        # 去除前后空格，转换为标题格式
        normalized = label.strip()
        
        # 替换特殊字符
        normalized = normalized.replace('_', ' ').replace('-', ' ')
        
        # 转换为标题格式
        normalized = ' '.join(word.capitalize() for word in normalized.split())
        
        return normalized
    
    def _normalize_properties(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        """标准化属性"""
        normalized = {}
        
        for key, value in properties.items():
            # 标准化键名
            normalized_key = key.lower().replace(' ', '_')
            
            # 标准化值
            if isinstance(value, str):
                normalized_value = value.strip()
            else:
                normalized_value = value
            
            normalized[normalized_key] = normalized_value
        
        return normalized
    
    def _get_canonical_form(self, entity: Node) -> Optional[str]:
        """获取实体的规范形式"""
        # 简化的规范形式映射
        canonical_mapping = {
            'usa': 'United States of America',
            'uk': 'United Kingdom',
            'ai': 'Artificial Intelligence',
            'ml': 'Machine Learning'
        }
        
        return canonical_mapping.get(entity.label.lower())