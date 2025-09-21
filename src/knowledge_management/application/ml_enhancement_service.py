# -*- coding: utf-8 -*-
"""
机器学习增强服务
提供语义消解、实体对齐、关系推理等ML增强功能
"""

from typing import List, Dict, Set, Tuple, Optional, Any
import numpy as np
from collections import defaultdict
import logging

from ..domain.model.graph import KnowledgeGraph
from ..domain.model.node import Node
from ..domain.model.edge import Edge
from ..domain.model.ml_models import (
    EntitySimilarity, RelationInference, EntityAlignment, SemanticResolver
)
from ..infrastructure.ml_processor import MLProcessor
from ..infrastructure.embedding_service import EmbeddingService


class MLEnhancementService:
    """
    机器学习增强服务
    提供知识图谱的智能增强功能
    """
    
    def __init__(self, ml_processor: MLProcessor, embedding_service: EmbeddingService):
        """
        初始化ML增强服务
        
        Args:
            ml_processor: 机器学习处理器
            embedding_service: 嵌入向量服务
        """
        self.ml_processor = ml_processor
        self.embedding_service = embedding_service
        self.logger = logging.getLogger(__name__)
        
        # 初始化ML模型
        self.entity_similarity = EntitySimilarity()
        self.relation_inference = RelationInference()
        self.entity_alignment = EntityAlignment()
        self.semantic_resolver = SemanticResolver()
    
    def semantic_resolution(self, kg: KnowledgeGraph, ambiguous_entities: List[Node]) -> Dict[str, Node]:
        """
        语义消解服务 - 解决实体歧义问题
        
        Args:
            kg: 知识图谱
            ambiguous_entities: 存在歧义的实体列表
            
        Returns:
            消解结果字典 {entity_id: resolved_entity}
        """
        self.logger.info(f"开始语义消解，处理{len(ambiguous_entities)}个歧义实体")
        
        resolved_entities = {}
        
        for entity in ambiguous_entities:
            try:
                # 获取实体的上下文信息
                context = self._get_entity_context(kg, entity)
                
                # 生成实体嵌入向量
                entity_embedding = self.embedding_service.get_entity_embedding(entity, context)
                
                # 使用语义消解模型
                resolved_entity = self.semantic_resolver.resolve(
                    entity, entity_embedding, context
                )
                
                resolved_entities[entity.id] = resolved_entity
                
            except Exception as e:
                self.logger.error(f"语义消解失败，实体ID: {entity.id}, 错误: {str(e)}")
                resolved_entities[entity.id] = entity  # 保持原实体
        
        self.logger.info(f"语义消解完成，成功处理{len(resolved_entities)}个实体")
        return resolved_entities
    
    def entity_alignment(self, kg: KnowledgeGraph, similarity_threshold: float = 0.8) -> List[Tuple[Node, Node]]:
        """
        实体对齐服务 - 识别和合并重复实体
        
        Args:
            kg: 知识图谱
            similarity_threshold: 相似度阈值
            
        Returns:
            需要合并的实体对列表
        """
        self.logger.info(f"开始实体对齐，相似度阈值: {similarity_threshold}")
        
        nodes = kg.get_all_nodes()
        alignment_pairs = []
        
        # 生成所有实体的嵌入向量
        entity_embeddings = {}
        for node in nodes:
            try:
                context = self._get_entity_context(kg, node)
                embedding = self.embedding_service.get_entity_embedding(node, context)
                entity_embeddings[node.id] = embedding
            except Exception as e:
                self.logger.warning(f"生成实体嵌入失败，实体ID: {node.id}, 错误: {str(e)}")
        
        # 计算实体间相似度
        processed_pairs = set()
        for i, node1 in enumerate(nodes):
            if node1.id not in entity_embeddings:
                continue
                
            for j, node2 in enumerate(nodes[i+1:], i+1):
                if node2.id not in entity_embeddings:
                    continue
                
                pair_key = tuple(sorted([node1.id, node2.id]))
                if pair_key in processed_pairs:
                    continue
                processed_pairs.add(pair_key)
                
                try:
                    # 计算相似度
                    similarity = self.entity_alignment.calculate_similarity(
                        node1, node2,
                        entity_embeddings[node1.id],
                        entity_embeddings[node2.id]
                    )
                    
                    if similarity >= similarity_threshold:
                        alignment_pairs.append((node1, node2))
                        
                except Exception as e:
                    self.logger.warning(f"计算实体相似度失败: {node1.id} vs {node2.id}, 错误: {str(e)}")
        
        self.logger.info(f"实体对齐完成，发现{len(alignment_pairs)}对相似实体")
        return alignment_pairs
    
    def relation_inference(self, kg: KnowledgeGraph, confidence_threshold: float = 0.7) -> List[Edge]:
        """
        关系推理服务 - 基于现有关系推断新关系
        
        Args:
            kg: 知识图谱
            confidence_threshold: 置信度阈值
            
        Returns:
            推断出的新关系列表
        """
        self.logger.info(f"开始关系推理，置信度阈值: {confidence_threshold}")
        
        inferred_relations = []
        nodes = kg.get_all_nodes()
        existing_edges = kg.get_all_edges()
        
        # 构建现有关系的索引
        existing_relations = set()
        for edge in existing_edges:
            existing_relations.add((edge.source_id, edge.target_id, edge.type))
        
        # 为每对节点推理可能的关系
        for i, node1 in enumerate(nodes):
            for j, node2 in enumerate(nodes):
                if i == j:  # 跳过自环
                    continue
                
                # 检查是否已存在关系
                has_relation = any(
                    (node1.id, node2.id, edge_type) in existing_relations
                    for edge_type in self._get_possible_relation_types(node1, node2)
                )
                
                if has_relation:
                    continue
                
                try:
                    # 使用关系推理模型
                    inferred_relation = self.relation_inference.infer_relation(
                        kg, node1, node2
                    )
                    
                    if inferred_relation and inferred_relation.confidence >= confidence_threshold:
                        # 创建新的边
                        new_edge = Edge(
                            id=f"inferred_{node1.id}_{node2.id}_{inferred_relation.relation_type}",
                            source_id=node1.id,
                            target_id=node2.id,
                            type=inferred_relation.relation_type,
                            label=inferred_relation.relation_type,
                            properties={
                                'confidence': inferred_relation.confidence,
                                'inferred': True,
                                'inference_method': inferred_relation.method
                            }
                        )
                        inferred_relations.append(new_edge)
                        
                except Exception as e:
                    self.logger.warning(f"关系推理失败: {node1.id} -> {node2.id}, 错误: {str(e)}")
        
        self.logger.info(f"关系推理完成，推断出{len(inferred_relations)}个新关系")
        return inferred_relations
    
    def entity_linking(self, kg: KnowledgeGraph, external_kb_urls: List[str]) -> Dict[str, List[str]]:
        """
        实体链接服务 - 将实体链接到外部知识库
        
        Args:
            kg: 知识图谱
            external_kb_urls: 外部知识库URL列表
            
        Returns:
            实体链接结果 {entity_id: [linked_urls]}
        """
        self.logger.info(f"开始实体链接，目标知识库数量: {len(external_kb_urls)}")
        
        linking_results = {}
        nodes = kg.get_all_nodes()
        
        for node in nodes:
            try:
                # 生成实体嵌入
                context = self._get_entity_context(kg, node)
                entity_embedding = self.embedding_service.get_entity_embedding(node, context)
                
                # 执行实体链接
                linked_urls = self._link_to_external_kb(
                    node, entity_embedding, external_kb_urls
                )
                
                if linked_urls:
                    linking_results[node.id] = linked_urls
                    
            except Exception as e:
                self.logger.warning(f"实体链接失败，实体ID: {node.id}, 错误: {str(e)}")
        
        self.logger.info(f"实体链接完成，成功链接{len(linking_results)}个实体")
        return linking_results
    
    def similarity_calculation(self, kg: KnowledgeGraph) -> Dict[str, Dict[str, float]]:
        """
        相似度计算服务 - 计算实体和关系的相似度
        
        Args:
            kg: 知识图谱
            
        Returns:
            相似度矩阵 {entity_id: {other_entity_id: similarity}}
        """
        self.logger.info("开始计算实体相似度矩阵")
        
        nodes = kg.get_all_nodes()
        similarity_matrix = defaultdict(dict)
        
        # 生成所有实体的嵌入向量
        entity_embeddings = {}
        for node in nodes:
            try:
                context = self._get_entity_context(kg, node)
                embedding = self.embedding_service.get_entity_embedding(node, context)
                entity_embeddings[node.id] = embedding
            except Exception as e:
                self.logger.warning(f"生成实体嵌入失败，实体ID: {node.id}")
        
        # 计算两两相似度
        for node1 in nodes:
            if node1.id not in entity_embeddings:
                continue
                
            for node2 in nodes:
                if node2.id not in entity_embeddings or node1.id == node2.id:
                    continue
                
                try:
                    similarity = self.entity_similarity.calculate(
                        entity_embeddings[node1.id],
                        entity_embeddings[node2.id]
                    )
                    similarity_matrix[node1.id][node2.id] = similarity
                    
                except Exception as e:
                    self.logger.warning(f"计算相似度失败: {node1.id} vs {node2.id}")
        
        self.logger.info(f"相似度计算完成，处理{len(similarity_matrix)}个实体")
        return dict(similarity_matrix)
    
    def clustering_analysis(self, kg: KnowledgeGraph, n_clusters: int = None) -> Dict[str, int]:
        """
        聚类分析服务 - 对实体进行聚类分析
        
        Args:
            kg: 知识图谱
            n_clusters: 聚类数量，None表示自动确定
            
        Returns:
            聚类结果 {entity_id: cluster_id}
        """
        self.logger.info(f"开始聚类分析，目标聚类数: {n_clusters or '自动'}")
        
        nodes = kg.get_all_nodes()
        
        # 生成实体嵌入向量矩阵
        embeddings = []
        entity_ids = []
        
        for node in nodes:
            try:
                context = self._get_entity_context(kg, node)
                embedding = self.embedding_service.get_entity_embedding(node, context)
                embeddings.append(embedding)
                entity_ids.append(node.id)
            except Exception as e:
                self.logger.warning(f"生成实体嵌入失败，实体ID: {node.id}")
        
        if not embeddings:
            self.logger.warning("没有有效的实体嵌入，无法进行聚类")
            return {}
        
        # 执行聚类
        try:
            embeddings_array = np.array(embeddings)
            cluster_labels = self.ml_processor.cluster_entities(
                embeddings_array, n_clusters
            )
            
            # 构建结果字典
            clustering_results = {
                entity_ids[i]: int(cluster_labels[i])
                for i in range(len(entity_ids))
            }
            
            self.logger.info(f"聚类分析完成，生成{len(set(cluster_labels))}个聚类")
            return clustering_results
            
        except Exception as e:
            self.logger.error(f"聚类分析失败: {str(e)}")
            return {}
    
    def anomaly_detection(self, kg: KnowledgeGraph, contamination: float = 0.1) -> List[str]:
        """
        异常检测服务 - 识别图谱中的异常数据
        
        Args:
            kg: 知识图谱
            contamination: 异常数据比例
            
        Returns:
            异常实体ID列表
        """
        self.logger.info(f"开始异常检测，异常比例阈值: {contamination}")
        
        nodes = kg.get_all_nodes()
        
        # 生成实体特征向量
        features = []
        entity_ids = []
        
        for node in nodes:
            try:
                # 提取实体特征
                feature_vector = self._extract_entity_features(kg, node)
                features.append(feature_vector)
                entity_ids.append(node.id)
            except Exception as e:
                self.logger.warning(f"提取实体特征失败，实体ID: {node.id}")
        
        if not features:
            self.logger.warning("没有有效的实体特征，无法进行异常检测")
            return []
        
        # 执行异常检测
        try:
            features_array = np.array(features)
            anomaly_labels = self.ml_processor.detect_anomalies(
                features_array, contamination
            )
            
            # 提取异常实体ID
            anomalous_entities = [
                entity_ids[i] for i, label in enumerate(anomaly_labels)
                if label == -1  # -1表示异常
            ]
            
            self.logger.info(f"异常检测完成，发现{len(anomalous_entities)}个异常实体")
            return anomalous_entities
            
        except Exception as e:
            self.logger.error(f"异常检测失败: {str(e)}")
            return []
    
    def _get_entity_context(self, kg: KnowledgeGraph, entity: Node) -> Dict[str, Any]:
        """
        获取实体的上下文信息
        
        Args:
            kg: 知识图谱
            entity: 实体节点
            
        Returns:
            上下文信息字典
        """
        context = {
            'neighbors': [],
            'relations': [],
            'properties': entity.properties.copy(),
            'degree': 0
        }
        
        # 获取邻居节点和关系
        edges = kg.get_edges_by_node(entity.id)
        context['degree'] = len(edges)
        
        for edge in edges:
            if edge.source_id == entity.id:
                neighbor_id = edge.target_id
            else:
                neighbor_id = edge.source_id
            
            neighbor = kg.get_node(neighbor_id)
            if neighbor:
                context['neighbors'].append(neighbor)
                context['relations'].append(edge.type)
        
        return context
    
    def _get_possible_relation_types(self, node1: Node, node2: Node) -> List[str]:
        """
        获取两个节点间可能的关系类型
        
        Args:
            node1: 源节点
            node2: 目标节点
            
        Returns:
            可能的关系类型列表
        """
        # 基于节点类型推断可能的关系
        type1 = node1.type or 'Unknown'
        type2 = node2.type or 'Unknown'
        
        # 这里可以根据具体业务逻辑定义关系类型映射
        relation_mapping = {
            ('Person', 'Person'): ['knows', 'colleague', 'friend', 'relative'],
            ('Person', 'Organization'): ['works_for', 'member_of', 'founded'],
            ('Organization', 'Organization'): ['partner', 'subsidiary', 'competitor'],
            ('Person', 'Project'): ['participates_in', 'leads', 'manages'],
            ('Organization', 'Project'): ['sponsors', 'owns', 'collaborates_on']
        }
        
        return relation_mapping.get((type1, type2), ['related_to'])
    
    def _link_to_external_kb(self, entity: Node, embedding: np.ndarray, kb_urls: List[str]) -> List[str]:
        """
        将实体链接到外部知识库
        
        Args:
            entity: 实体节点
            embedding: 实体嵌入向量
            kb_urls: 外部知识库URL列表
            
        Returns:
            链接的URL列表
        """
        # 这里是一个简化的实现，实际应用中需要调用外部知识库API
        linked_urls = []
        
        for kb_url in kb_urls:
            try:
                # 模拟外部知识库查询
                # 实际实现需要调用具体的知识库API
                if self._match_external_entity(entity, kb_url):
                    linked_urls.append(f"{kb_url}/entity/{entity.label}")
            except Exception as e:
                self.logger.warning(f"外部知识库链接失败: {kb_url}, 错误: {str(e)}")
        
        return linked_urls
    
    def _match_external_entity(self, entity: Node, kb_url: str) -> bool:
        """
        匹配外部知识库中的实体
        
        Args:
            entity: 实体节点
            kb_url: 知识库URL
            
        Returns:
            是否匹配成功
        """
        # 简化的匹配逻辑，实际应用中需要更复杂的匹配算法
        return len(entity.label) > 2 and entity.type in ['Person', 'Organization', 'Location']
    
    def _extract_entity_features(self, kg: KnowledgeGraph, entity: Node) -> List[float]:
        """
        提取实体特征向量用于异常检测
        
        Args:
            kg: 知识图谱
            entity: 实体节点
            
        Returns:
            特征向量
        """
        features = []
        
        # 基本特征
        features.append(len(entity.label))  # 标签长度
        features.append(len(entity.properties))  # 属性数量
        
        # 图结构特征
        edges = kg.get_edges_by_node(entity.id)
        features.append(len(edges))  # 度数
        
        # 入度和出度
        in_degree = sum(1 for edge in edges if edge.target_id == entity.id)
        out_degree = sum(1 for edge in edges if edge.source_id == entity.id)
        features.append(in_degree)
        features.append(out_degree)
        
        # 关系类型多样性
        relation_types = set(edge.type for edge in edges if edge.type)
        features.append(len(relation_types))
        
        # 邻居节点类型多样性
        neighbor_types = set()
        for edge in edges:
            neighbor_id = edge.target_id if edge.source_id == entity.id else edge.source_id
            neighbor = kg.get_node(neighbor_id)
            if neighbor and neighbor.type:
                neighbor_types.add(neighbor.type)
        features.append(len(neighbor_types))
        
        return features