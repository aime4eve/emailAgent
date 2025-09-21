# -*- coding: utf-8 -*-
"""
相似度计算器
提供多种相似度计算方法
"""

import re
import math
from typing import List, Dict, Set, Tuple, Optional, Any, Union
from collections import Counter
import logging

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
except ImportError:
    TfidfVectorizer = None
    cosine_similarity = None
    euclidean_distances = None

try:
    import numpy as np
except ImportError:
    np = None

from ..knowledge_management.domain.model.node import Node
from ..knowledge_management.domain.model.edge import Edge

logger = logging.getLogger(__name__)


class SimilarityCalculator:
    """
    相似度计算器
    提供多种文本和实体相似度计算方法
    """
    
    def __init__(self):
        """
        初始化相似度计算器
        """
        self.tfidf_vectorizer = None
        if TfidfVectorizer:
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words=None,
                ngram_range=(1, 2),
                lowercase=True
            )
    
    def jaccard_similarity(self, set1: Set[str], set2: Set[str]) -> float:
        """
        计算Jaccard相似度
        
        Args:
            set1: 集合1
            set2: 集合2
            
        Returns:
            Jaccard相似度 (0-1)
        """
        if not set1 and not set2:
            return 1.0
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    def jaccard_similarity_text(self, text1: str, text2: str) -> float:
        """计算文本Jaccard相似度"""
        if not text1 or not text2:
            return 0.0
            
        # 确保输入是字符串
        text1 = str(text1) if text1 is not None else ""
        text2 = str(text2) if text2 is not None else ""
        
        set1 = set(text1.lower().split())
        set2 = set(text2.lower().split())
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    def cosine_similarity_text(self, text1: str, text2: str) -> float:
        """
        计算文本余弦相似度
        
        Args:
            text1: 文本1
            text2: 文本2
            
        Returns:
            余弦相似度 (0-1)
        """
        if not self.tfidf_vectorizer or not cosine_similarity:
            # 使用简单的词汇重叠计算
            return self.jaccard_similarity_text(text1, text2)
        
        try:
            # 使用TF-IDF向量化
            texts = [text1, text2]
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)
            
            # 计算余弦相似度
            similarity_matrix = cosine_similarity(tfidf_matrix)
            return float(similarity_matrix[0, 1])
        
        except Exception as e:
            logger.warning(f"TF-IDF余弦相似度计算失败: {str(e)}")
            # 回退到简单方法
            return self.jaccard_similarity_text(text1, text2)
    
    def levenshtein_distance(self, s1: str, s2: str) -> int:
        """
        计算编辑距离（Levenshtein距离）
        
        Args:
            s1: 字符串1
            s2: 字符串2
            
        Returns:
            编辑距离
        """
        if len(s1) < len(s2):
            return self.levenshtein_distance(s2, s1)
        
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
    
    def levenshtein_similarity(self, s1: str, s2: str) -> float:
        """
        基于编辑距离的相似度
        
        Args:
            s1: 字符串1
            s2: 字符串2
            
        Returns:
            相似度 (0-1)
        """
        distance = self.levenshtein_distance(s1, s2)
        max_len = max(len(s1), len(s2))
        
        if max_len == 0:
            return 1.0
        
        return 1.0 - (distance / max_len)
    
    def jaro_similarity(self, s1: str, s2: str) -> float:
        """
        计算Jaro相似度
        
        Args:
            s1: 字符串1
            s2: 字符串2
            
        Returns:
            Jaro相似度 (0-1)
        """
        if s1 == s2:
            return 1.0
        
        len1, len2 = len(s1), len(s2)
        if len1 == 0 or len2 == 0:
            return 0.0
        
        # 匹配窗口
        match_window = max(len1, len2) // 2 - 1
        match_window = max(0, match_window)
        
        s1_matches = [False] * len1
        s2_matches = [False] * len2
        
        matches = 0
        transpositions = 0
        
        # 找到匹配字符
        for i in range(len1):
            start = max(0, i - match_window)
            end = min(i + match_window + 1, len2)
            
            for j in range(start, end):
                if s2_matches[j] or s1[i] != s2[j]:
                    continue
                
                s1_matches[i] = True
                s2_matches[j] = True
                matches += 1
                break
        
        if matches == 0:
            return 0.0
        
        # 计算转置
        k = 0
        for i in range(len1):
            if not s1_matches[i]:
                continue
            
            while not s2_matches[k]:
                k += 1
            
            if s1[i] != s2[k]:
                transpositions += 1
            
            k += 1
        
        jaro = (matches / len1 + matches / len2 + 
                (matches - transpositions / 2) / matches) / 3.0
        
        return jaro
    
    def jaro_winkler_similarity(self, s1: str, s2: str, prefix_scale: float = 0.1) -> float:
        """
        计算Jaro-Winkler相似度
        
        Args:
            s1: 字符串1
            s2: 字符串2
            prefix_scale: 前缀权重
            
        Returns:
            Jaro-Winkler相似度 (0-1)
        """
        jaro_sim = self.jaro_similarity(s1, s2)
        
        if jaro_sim < 0.7:
            return jaro_sim
        
        # 计算公共前缀长度（最多4个字符）
        prefix_len = 0
        for i in range(min(len(s1), len(s2), 4)):
            if s1[i] == s2[i]:
                prefix_len += 1
            else:
                break
        
        return jaro_sim + (prefix_len * prefix_scale * (1 - jaro_sim))
    
    def n_gram_similarity(self, s1: str, s2: str, n: int = 2) -> float:
        """
        计算N-gram相似度
        
        Args:
            s1: 字符串1
            s2: 字符串2
            n: N-gram大小
            
        Returns:
            N-gram相似度 (0-1)
        """
        def get_ngrams(text: str, n: int) -> Set[str]:
            if len(text) < n:
                return {text}
            return {text[i:i+n] for i in range(len(text) - n + 1)}
        
        ngrams1 = get_ngrams(s1.lower(), n)
        ngrams2 = get_ngrams(s2.lower(), n)
        
        return self.jaccard_similarity(ngrams1, ngrams2)
    
    def semantic_similarity(self, text1: str, text2: str) -> float:
        """
        计算语义相似度（基于词汇重叠和TF-IDF）
        
        Args:
            text1: 文本1
            text2: 文本2
            
        Returns:
            语义相似度 (0-1)
        """
        # 预处理文本
        def preprocess(text: str) -> List[str]:
            # 去除标点符号，转小写，分词
            text = re.sub(r'[^\w\s\u4e00-\u9fff]', ' ', text.lower())
            words = text.split()
            return [word for word in words if len(word) > 1]
        
        words1 = preprocess(text1)
        words2 = preprocess(text2)
        
        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0
        
        # 词汇重叠相似度
        set1, set2 = set(words1), set(words2)
        jaccard_sim = self.jaccard_similarity(set1, set2)
        
        # TF-IDF余弦相似度
        cosine_sim = self.cosine_similarity_text(text1, text2)
        
        # 加权平均
        return 0.4 * jaccard_sim + 0.6 * cosine_sim
    
    def entity_similarity(self, entity1: Node, entity2: Node) -> Dict[str, float]:
        """
        计算实体相似度（多维度）
        
        Args:
            entity1: 实体1
            entity2: 实体2
            
        Returns:
            相似度字典
        """
        similarities = {}
        
        # 标签相似度
        similarities['label_exact'] = 1.0 if entity1.label == entity2.label else 0.0
        similarities['label_levenshtein'] = self.levenshtein_similarity(entity1.label, entity2.label)
        similarities['label_jaro_winkler'] = self.jaro_winkler_similarity(entity1.label, entity2.label)
        similarities['label_semantic'] = self.semantic_similarity(entity1.label, entity2.label)
        
        # 类型相似度
        similarities['type_match'] = 1.0 if entity1.type == entity2.type else 0.0
        
        # 属性相似度
        prop_sim = self._calculate_property_similarity(entity1.properties or {}, 
                                                      entity2.properties or {})
        similarities['properties'] = prop_sim
        
        # 综合相似度
        weights = {
            'label_semantic': 0.4,
            'label_jaro_winkler': 0.2,
            'type_match': 0.2,
            'properties': 0.2
        }
        
        weighted_sum = sum(similarities[key] * weight for key, weight in weights.items())
        similarities['overall'] = weighted_sum
        
        return similarities
    
    def _calculate_property_similarity(self, props1: Dict[str, Any], 
                                     props2: Dict[str, Any]) -> float:
        """
        计算属性相似度
        
        Args:
            props1: 属性字典1
            props2: 属性字典2
            
        Returns:
            属性相似度 (0-1)
        """
        if not props1 and not props2:
            return 1.0
        
        if not props1 or not props2:
            return 0.0
        
        # 计算键的相似度
        keys1, keys2 = set(props1.keys()), set(props2.keys())
        key_similarity = self.jaccard_similarity(keys1, keys2)
        
        # 计算共同键的值相似度
        common_keys = keys1.intersection(keys2)
        if not common_keys:
            return key_similarity * 0.5  # 只有键相似度
        
        value_similarities = []
        for key in common_keys:
            val1, val2 = str(props1[key]), str(props2[key])
            if val1 == val2:
                value_similarities.append(1.0)
            else:
                # 根据值类型选择相似度计算方法
                if self._is_numeric(val1) and self._is_numeric(val2):
                    sim = self._numeric_similarity(float(val1), float(val2))
                else:
                    sim = self.semantic_similarity(val1, val2)
                value_similarities.append(sim)
        
        avg_value_similarity = sum(value_similarities) / len(value_similarities)
        
        # 综合键和值的相似度
        return 0.3 * key_similarity + 0.7 * avg_value_similarity
    
    def _is_numeric(self, value: str) -> bool:
        """
        检查字符串是否为数值
        
        Args:
            value: 字符串值
            
        Returns:
            是否为数值
        """
        try:
            float(value)
            return True
        except ValueError:
            return False
    
    def _numeric_similarity(self, num1: float, num2: float) -> float:
        """
        计算数值相似度
        
        Args:
            num1: 数值1
            num2: 数值2
            
        Returns:
            数值相似度 (0-1)
        """
        if num1 == num2:
            return 1.0
        
        # 使用相对差异计算相似度
        max_val = max(abs(num1), abs(num2))
        if max_val == 0:
            return 1.0
        
        relative_diff = abs(num1 - num2) / max_val
        return max(0.0, 1.0 - relative_diff)
    
    def batch_similarity(self, entities: List[Node], 
                        similarity_threshold: float = 0.7) -> List[Tuple[Node, Node, float]]:
        """
        批量计算实体相似度
        
        Args:
            entities: 实体列表
            similarity_threshold: 相似度阈值
            
        Returns:
            相似实体对列表 (实体1, 实体2, 相似度)
        """
        similar_pairs = []
        
        for i in range(len(entities)):
            for j in range(i + 1, len(entities)):
                entity1, entity2 = entities[i], entities[j]
                
                # 只比较同类型实体
                if entity1.type != entity2.type:
                    continue
                
                similarities = self.entity_similarity(entity1, entity2)
                overall_similarity = similarities['overall']
                
                if overall_similarity >= similarity_threshold:
                    similar_pairs.append((entity1, entity2, overall_similarity))
        
        # 按相似度降序排序
        similar_pairs.sort(key=lambda x: x[2], reverse=True)
        
        return similar_pairs
    
    def similarity_matrix(self, entities: List[Node]) -> np.ndarray:
        """
        计算实体相似度矩阵
        
        Args:
            entities: 实体列表
            
        Returns:
            相似度矩阵
        """
        if not np:
            raise ImportError("需要numpy库来计算相似度矩阵")
        
        n = len(entities)
        matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                if i == j:
                    matrix[i, j] = 1.0
                elif i < j:
                    similarities = self.entity_similarity(entities[i], entities[j])
                    similarity = similarities['overall']
                    matrix[i, j] = similarity
                    matrix[j, i] = similarity  # 对称矩阵
        
        return matrix
    
    def find_most_similar(self, target_entity: Node, 
                         candidate_entities: List[Node], 
                         top_k: int = 5) -> List[Tuple[Node, float]]:
        """
        找到与目标实体最相似的候选实体
        
        Args:
            target_entity: 目标实体
            candidate_entities: 候选实体列表
            top_k: 返回前k个最相似的实体
            
        Returns:
            最相似实体列表 (实体, 相似度)
        """
        similarities = []
        
        for candidate in candidate_entities:
            if candidate.id == target_entity.id:
                continue
            
            sim_scores = self.entity_similarity(target_entity, candidate)
            overall_sim = sim_scores['overall']
            similarities.append((candidate, overall_sim))
        
        # 按相似度降序排序
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]
    
    def get_similarity_statistics(self, similarities: List[float]) -> Dict[str, float]:
        """
        获取相似度统计信息
        
        Args:
            similarities: 相似度列表
            
        Returns:
            统计信息字典
        """
        if not similarities:
            return {
                'count': 0,
                'mean': 0.0,
                'median': 0.0,
                'std': 0.0,
                'min': 0.0,
                'max': 0.0
            }
        
        similarities = sorted(similarities)
        n = len(similarities)
        
        mean_sim = sum(similarities) / n
        median_sim = similarities[n // 2] if n % 2 == 1 else (similarities[n // 2 - 1] + similarities[n // 2]) / 2
        
        # 计算标准差
        variance = sum((x - mean_sim) ** 2 for x in similarities) / n
        std_sim = math.sqrt(variance)
        
        return {
            'count': n,
            'mean': mean_sim,
            'median': median_sim,
            'std': std_sim,
            'min': similarities[0],
            'max': similarities[-1]
        }