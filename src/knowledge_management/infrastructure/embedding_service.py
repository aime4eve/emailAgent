# -*- coding: utf-8 -*-
"""
嵌入向量服务
实现实体和关系的向量化表示
"""

from typing import List, Dict, Optional, Any, Tuple
import numpy as np
import logging
try:
    from gensim.models import Word2Vec, FastText
    from gensim.models.doc2vec import Doc2Vec, TaggedDocument
    GENSIM_AVAILABLE = True
except ImportError:
    GENSIM_AVAILABLE = False
    Word2Vec = None
    FastText = None
    Doc2Vec = None
    TaggedDocument = None
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
import pickle
import os
from datetime import datetime
import hashlib
import json

from ..domain.model.node import Node
from ..domain.model.edge import Edge
from ..domain.model.graph import KnowledgeGraph


class EmbeddingService:
    """
    嵌入向量服务
    提供实体和关系的向量化表示功能
    """
    
    def __init__(self, embedding_dim: int = 100, cache_dir: str = "embeddings"):
        """
        初始化嵌入向量服务
        
        Args:
            embedding_dim: 嵌入向量维度
            cache_dir: 缓存目录
        """
        self.embedding_dim = embedding_dim
        self.cache_dir = cache_dir
        self.logger = logging.getLogger(__name__)
        
        # 确保缓存目录存在
        os.makedirs(cache_dir, exist_ok=True)
        
        # 初始化各种嵌入模型
        self.word2vec_model = None
        self.fasttext_model = None
        self.doc2vec_model = None
        self.tfidf_vectorizer = None
        self.scaler = StandardScaler()
        
        # 嵌入缓存
        self.entity_embeddings = {}
        self.relation_embeddings = {}
        self.graph_embeddings = {}
        
        # 模型参数
        self.word2vec_params = {
            'vector_size': embedding_dim,
            'window': 5,
            'min_count': 1,
            'workers': 4,
            'sg': 1  # Skip-gram
        }
        
        self.fasttext_params = {
            'vector_size': embedding_dim,
            'window': 5,
            'min_count': 1,
            'workers': 4,
            'sg': 1
        }
        
        self.doc2vec_params = {
            'vector_size': embedding_dim,
            'window': 5,
            'min_count': 1,
            'workers': 4,
            'dm': 1  # PV-DM
        }
    
    def get_entity_embedding(self, entity: Node, context: Optional[Dict[str, Any]] = None) -> np.ndarray:
        """
        获取实体的嵌入向量
        
        Args:
            entity: 实体节点
            context: 上下文信息
            
        Returns:
            实体嵌入向量
        """
        # 生成缓存键
        cache_key = self._generate_entity_cache_key(entity, context)
        
        # 检查缓存
        if cache_key in self.entity_embeddings:
            return self.entity_embeddings[cache_key]
        
        try:
            # 生成实体嵌入向量
            embedding = self._compute_entity_embedding(entity, context)
            
            # 缓存结果
            self.entity_embeddings[cache_key] = embedding
            
            return embedding
            
        except Exception as e:
            self.logger.error(f"生成实体嵌入失败，实体ID: {entity.id}, 错误: {str(e)}")
            # 返回随机向量作为默认值
            return np.random.rand(self.embedding_dim)
    
    def get_relation_embedding(self, relation: Edge, context: Optional[Dict[str, Any]] = None) -> np.ndarray:
        """
        获取关系的嵌入向量
        
        Args:
            relation: 关系边
            context: 上下文信息
            
        Returns:
            关系嵌入向量
        """
        # 生成缓存键
        cache_key = self._generate_relation_cache_key(relation, context)
        
        # 检查缓存
        if cache_key in self.relation_embeddings:
            return self.relation_embeddings[cache_key]
        
        try:
            # 生成关系嵌入向量
            embedding = self._compute_relation_embedding(relation, context)
            
            # 缓存结果
            self.relation_embeddings[cache_key] = embedding
            
            return embedding
            
        except Exception as e:
            self.logger.error(f"生成关系嵌入失败，关系ID: {relation.id}, 错误: {str(e)}")
            # 返回随机向量作为默认值
            return np.random.rand(self.embedding_dim)
    
    def get_graph_embedding(self, kg: KnowledgeGraph, method: str = 'node2vec') -> np.ndarray:
        """
        获取图的嵌入向量
        
        Args:
            kg: 知识图谱
            method: 图嵌入方法 ('node2vec', 'deepwalk', 'line')
            
        Returns:
            图嵌入向量
        """
        # 生成缓存键
        cache_key = self._generate_graph_cache_key(kg, method)
        
        # 检查缓存
        if cache_key in self.graph_embeddings:
            return self.graph_embeddings[cache_key]
        
        try:
            # 生成图嵌入向量
            embedding = self._compute_graph_embedding(kg, method)
            
            # 缓存结果
            self.graph_embeddings[cache_key] = embedding
            
            return embedding
            
        except Exception as e:
            self.logger.error(f"生成图嵌入失败，方法: {method}, 错误: {str(e)}")
            # 返回随机向量作为默认值
            return np.random.rand(self.embedding_dim)
    
    def train_word2vec_model(self, texts: List[List[str]]) -> bool:
        """
        训练Word2Vec模型
        
        Args:
            texts: 文本语料库（已分词）
            
        Returns:
            是否训练成功
        """
        if not GENSIM_AVAILABLE:
            self.logger.warning("Gensim不可用，无法训练Word2Vec模型")
            return False
            
        try:
            self.logger.info(f"开始训练Word2Vec模型，语料库大小: {len(texts)}")
            
            self.word2vec_model = Word2Vec(texts, **self.word2vec_params)
            
            # 保存模型
            model_path = os.path.join(self.cache_dir, "word2vec.model")
            self.word2vec_model.save(model_path)
            
            self.logger.info(f"Word2Vec模型训练完成，已保存到: {model_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Word2Vec模型训练失败: {str(e)}")
            return False
    
    def train_fasttext_model(self, texts: List[List[str]]) -> bool:
        """
        训练FastText模型
        
        Args:
            texts: 文本语料库（已分词）
            
        Returns:
            是否训练成功
        """
        if not GENSIM_AVAILABLE:
            self.logger.warning("Gensim不可用，无法训练FastText模型")
            return False
            
        try:
            self.logger.info(f"开始训练FastText模型，语料库大小: {len(texts)}")
            
            self.fasttext_model = FastText(texts, **self.fasttext_params)
            
            # 保存模型
            model_path = os.path.join(self.cache_dir, "fasttext.model")
            self.fasttext_model.save(model_path)
            
            self.logger.info(f"FastText模型训练完成，已保存到: {model_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"FastText模型训练失败: {str(e)}")
            return False
    
    def train_doc2vec_model(self, documents: List[str], tags: List[str]) -> bool:
        """
        训练Doc2Vec模型
        
        Args:
            documents: 文档列表
            tags: 文档标签列表
            
        Returns:
            是否训练成功
        """
        if not GENSIM_AVAILABLE:
            self.logger.warning("Gensim不可用，无法训练Doc2Vec模型")
            return False
            
        try:
            self.logger.info(f"开始训练Doc2Vec模型，文档数量: {len(documents)}")
            
            # 准备训练数据
            tagged_docs = [
                TaggedDocument(words=doc.split(), tags=[tag])
                for doc, tag in zip(documents, tags)
            ]
            
            self.doc2vec_model = Doc2Vec(tagged_docs, **self.doc2vec_params)
            
            # 保存模型
            model_path = os.path.join(self.cache_dir, "doc2vec.model")
            self.doc2vec_model.save(model_path)
            
            self.logger.info(f"Doc2Vec模型训练完成，已保存到: {model_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Doc2Vec模型训练失败: {str(e)}")
            return False
    
    def load_pretrained_model(self, model_type: str, model_path: str) -> bool:
        """
        加载预训练模型
        
        Args:
            model_type: 模型类型 ('word2vec', 'fasttext', 'doc2vec')
            model_path: 模型文件路径
            
        Returns:
            是否加载成功
        """
        if not GENSIM_AVAILABLE:
            self.logger.warning("Gensim不可用，无法加载预训练模型")
            return False
            
        try:
            if model_type == 'word2vec':
                self.word2vec_model = Word2Vec.load(model_path)
            elif model_type == 'fasttext':
                self.fasttext_model = FastText.load(model_path)
            elif model_type == 'doc2vec':
                self.doc2vec_model = Doc2Vec.load(model_path)
            else:
                raise ValueError(f"不支持的模型类型: {model_type}")
            
            self.logger.info(f"预训练模型加载成功: {model_type} from {model_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"预训练模型加载失败: {str(e)}")
            return False
    
    def _compute_entity_embedding(self, entity: Node, context: Optional[Dict[str, Any]]) -> np.ndarray:
        """
        计算实体嵌入向量
        
        Args:
            entity: 实体节点
            context: 上下文信息
            
        Returns:
            实体嵌入向量
        """
        # 收集实体的文本特征
        text_features = self._extract_entity_text_features(entity, context)
        
        # 使用多种方法生成嵌入向量
        embeddings = []
        
        # 1. 基于Word2Vec的嵌入
        if GENSIM_AVAILABLE and self.word2vec_model:
            word2vec_embedding = self._get_word2vec_embedding(text_features)
            embeddings.append(word2vec_embedding)
        
        # 2. 基于FastText的嵌入
        if GENSIM_AVAILABLE and self.fasttext_model:
            fasttext_embedding = self._get_fasttext_embedding(text_features)
            embeddings.append(fasttext_embedding)
        
        # 3. 基于TF-IDF的嵌入
        tfidf_embedding = self._get_tfidf_embedding(text_features)
        embeddings.append(tfidf_embedding)
        
        # 4. 基于结构特征的嵌入
        structural_embedding = self._get_structural_embedding(entity, context)
        embeddings.append(structural_embedding)
        
        # 融合多种嵌入
        if embeddings:
            # 确保所有嵌入向量维度一致
            normalized_embeddings = []
            for emb in embeddings:
                if len(emb) != self.embedding_dim:
                    # 调整维度
                    if len(emb) > self.embedding_dim:
                        emb = emb[:self.embedding_dim]
                    else:
                        emb = np.pad(emb, (0, self.embedding_dim - len(emb)), 'constant')
                normalized_embeddings.append(emb)
            
            # 加权平均融合
            weights = [0.3, 0.3, 0.2, 0.2][:len(normalized_embeddings)]
            weights = np.array(weights) / sum(weights)  # 归一化权重
            
            final_embedding = np.average(normalized_embeddings, axis=0, weights=weights)
        else:
            # 如果没有有效的嵌入，使用随机向量
            final_embedding = np.random.rand(self.embedding_dim)
        
        return final_embedding
    
    def _compute_relation_embedding(self, relation: Edge, context: Optional[Dict[str, Any]]) -> np.ndarray:
        """
        计算关系嵌入向量
        
        Args:
            relation: 关系边
            context: 上下文信息
            
        Returns:
            关系嵌入向量
        """
        # 收集关系的文本特征
        text_features = self._extract_relation_text_features(relation, context)
        
        # 使用多种方法生成嵌入向量
        embeddings = []
        
        # 1. 基于关系类型的嵌入
        if self.word2vec_model and relation.type:
            type_embedding = self._get_word2vec_embedding([relation.type])
            embeddings.append(type_embedding)
        
        # 2. 基于关系标签的嵌入
        if relation.label:
            label_embedding = self._get_tfidf_embedding([relation.label])
            embeddings.append(label_embedding)
        
        # 3. 基于关系属性的嵌入
        if relation.properties:
            property_text = ' '.join(str(v) for v in relation.properties.values())
            property_embedding = self._get_tfidf_embedding([property_text])
            embeddings.append(property_embedding)
        
        # 融合嵌入向量
        if embeddings:
            # 确保维度一致
            normalized_embeddings = []
            for emb in embeddings:
                if len(emb) != self.embedding_dim:
                    if len(emb) > self.embedding_dim:
                        emb = emb[:self.embedding_dim]
                    else:
                        emb = np.pad(emb, (0, self.embedding_dim - len(emb)), 'constant')
                normalized_embeddings.append(emb)
            
            final_embedding = np.mean(normalized_embeddings, axis=0)
        else:
            final_embedding = np.random.rand(self.embedding_dim)
        
        return final_embedding
    
    def _compute_graph_embedding(self, kg: KnowledgeGraph, method: str) -> np.ndarray:
        """
        计算图嵌入向量
        
        Args:
            kg: 知识图谱
            method: 图嵌入方法
            
        Returns:
            图嵌入向量
        """
        # 简化的图嵌入实现
        nodes = kg.get_all_nodes()
        edges = kg.get_all_edges()
        
        if method == 'node2vec':
            return self._node2vec_embedding(kg)
        elif method == 'deepwalk':
            return self._deepwalk_embedding(kg)
        elif method == 'line':
            return self._line_embedding(kg)
        else:
            # 默认使用节点嵌入的平均值
            node_embeddings = []
            for node in nodes:
                node_emb = self.get_entity_embedding(node)
                node_embeddings.append(node_emb)
            
            if node_embeddings:
                return np.mean(node_embeddings, axis=0)
            else:
                return np.random.rand(self.embedding_dim)
    
    def _extract_entity_text_features(self, entity: Node, context: Optional[Dict[str, Any]]) -> List[str]:
        """
        提取实体的文本特征
        
        Args:
            entity: 实体节点
            context: 上下文信息
            
        Returns:
            文本特征列表
        """
        features = []
        
        # 实体标签
        if entity.label:
            features.append(entity.label)
        
        # 实体类型
        if entity.type:
            features.append(entity.type)
        
        # 实体属性
        for key, value in entity.properties.items():
            if isinstance(value, str):
                features.append(f"{key}_{value}")
            else:
                features.append(f"{key}_{str(value)}")
        
        # 上下文信息
        if context:
            # 邻居节点信息
            neighbors = context.get('neighbors', [])
            for neighbor in neighbors[:5]:  # 限制邻居数量
                if hasattr(neighbor, 'label') and neighbor.label:
                    features.append(f"neighbor_{neighbor.label}")
                if hasattr(neighbor, 'type') and neighbor.type:
                    features.append(f"neighbor_type_{neighbor.type}")
            
            # 关系信息
            relations = context.get('relations', [])
            for relation in relations[:5]:  # 限制关系数量
                features.append(f"relation_{relation}")
        
        return features
    
    def _extract_relation_text_features(self, relation: Edge, context: Optional[Dict[str, Any]]) -> List[str]:
        """
        提取关系的文本特征
        
        Args:
            relation: 关系边
            context: 上下文信息
            
        Returns:
            文本特征列表
        """
        features = []
        
        # 关系类型
        if relation.type:
            features.append(relation.type)
        
        # 关系标签
        if relation.label:
            features.append(relation.label)
        
        # 关系属性
        for key, value in relation.properties.items():
            features.append(f"{key}_{str(value)}")
        
        return features
    
    def _get_word2vec_embedding(self, words: List[str]) -> np.ndarray:
        """
        获取Word2Vec嵌入向量
        
        Args:
            words: 词语列表
            
        Returns:
            嵌入向量
        """
        if not GENSIM_AVAILABLE or not self.word2vec_model or not words:
            return np.zeros(self.embedding_dim)
        
        embeddings = []
        for word in words:
            try:
                if word in self.word2vec_model.wv:
                    embeddings.append(self.word2vec_model.wv[word])
            except KeyError:
                continue
        
        if embeddings:
            return np.mean(embeddings, axis=0)
        else:
            return np.zeros(self.embedding_dim)
    
    def _get_fasttext_embedding(self, words: List[str]) -> np.ndarray:
        """
        获取FastText嵌入
        
        Args:
            words: 词语列表
            
        Returns:
            嵌入向量
        """
        if not GENSIM_AVAILABLE or not self.fasttext_model or not words:
            return np.zeros(self.embedding_dim)
        
        embeddings = []
        for word in words:
            try:
                embeddings.append(self.fasttext_model.wv[word])
            except KeyError:
                continue
        
        if embeddings:
            return np.mean(embeddings, axis=0)
        else:
            return np.zeros(self.embedding_dim)
    
    def _get_tfidf_embedding(self, texts: List[str]) -> np.ndarray:
        """
        获取TF-IDF嵌入向量
        
        Args:
            texts: 文本列表
            
        Returns:
            嵌入向量
        """
        if not texts:
            return np.zeros(self.embedding_dim)
        
        try:
            # 初始化TF-IDF向量化器
            if self.tfidf_vectorizer is None:
                self.tfidf_vectorizer = TfidfVectorizer(
                    max_features=self.embedding_dim,
                    stop_words='english'
                )
                # 使用当前文本进行拟合
                self.tfidf_vectorizer.fit(texts)
            
            # 转换文本为向量
            tfidf_matrix = self.tfidf_vectorizer.transform(texts)
            
            # 返回平均向量
            if tfidf_matrix.shape[0] > 0:
                return np.mean(tfidf_matrix.toarray(), axis=0)
            else:
                return np.zeros(self.embedding_dim)
                
        except Exception as e:
            self.logger.warning(f"TF-IDF嵌入生成失败: {str(e)}")
            return np.zeros(self.embedding_dim)
    
    def _get_structural_embedding(self, entity: Node, context: Optional[Dict[str, Any]]) -> np.ndarray:
        """
        获取结构特征嵌入向量
        
        Args:
            entity: 实体节点
            context: 上下文信息
            
        Returns:
            结构特征嵌入向量
        """
        features = np.zeros(self.embedding_dim)
        
        if context:
            # 度数特征
            degree = context.get('degree', 0)
            features[0] = min(degree / 10.0, 1.0)  # 归一化度数
            
            # 邻居类型多样性
            neighbors = context.get('neighbors', [])
            neighbor_types = set(n.type for n in neighbors if hasattr(n, 'type') and n.type)
            features[1] = min(len(neighbor_types) / 5.0, 1.0)  # 归一化类型多样性
            
            # 关系类型多样性
            relations = context.get('relations', [])
            relation_types = set(relations)
            features[2] = min(len(relation_types) / 5.0, 1.0)  # 归一化关系多样性
            
            # 属性数量
            features[3] = min(len(entity.properties) / 10.0, 1.0)  # 归一化属性数量
        
        return features
    
    def _node2vec_embedding(self, kg: KnowledgeGraph) -> np.ndarray:
        """
        Node2Vec图嵌入（简化实现）
        
        Args:
            kg: 知识图谱
            
        Returns:
            图嵌入向量
        """
        # 简化的Node2Vec实现
        nodes = kg.get_all_nodes()
        if not nodes:
            return np.random.rand(self.embedding_dim)
        
        # 生成随机游走序列
        walks = self._generate_random_walks(kg, num_walks=10, walk_length=20)
        
        # 使用Word2Vec训练节点嵌入
        if walks and GENSIM_AVAILABLE:
            temp_model = Word2Vec(walks, vector_size=self.embedding_dim, window=5, min_count=1, workers=1)
            
            # 计算所有节点嵌入的平均值作为图嵌入
            node_embeddings = []
            for node in nodes:
                if node.id in temp_model.wv:
                    node_embeddings.append(temp_model.wv[node.id])
            
            if node_embeddings:
                return np.mean(node_embeddings, axis=0)
        else:
            # 如果gensim不可用或没有walks，使用随机嵌入
            return np.random.rand(self.embedding_dim)
        
        return np.random.rand(self.embedding_dim)
    
    def _deepwalk_embedding(self, kg: KnowledgeGraph) -> np.ndarray:
        """
        DeepWalk图嵌入（简化实现）
        
        Args:
            kg: 知识图谱
            
        Returns:
            图嵌入向量
        """
        # DeepWalk与Node2Vec类似，但使用均匀随机游走
        return self._node2vec_embedding(kg)
    
    def _line_embedding(self, kg: KnowledgeGraph) -> np.ndarray:
        """
        LINE图嵌入（简化实现）
        
        Args:
            kg: 知识图谱
            
        Returns:
            图嵌入向量
        """
        # 简化的LINE实现，基于邻接矩阵
        nodes = kg.get_all_nodes()
        edges = kg.get_all_edges()
        
        if not nodes:
            return np.random.rand(self.embedding_dim)
        
        # 构建邻接矩阵
        node_to_idx = {node.id: i for i, node in enumerate(nodes)}
        adj_matrix = np.zeros((len(nodes), len(nodes)))
        
        for edge in edges:
            if edge.source_id in node_to_idx and edge.target_id in node_to_idx:
                i, j = node_to_idx[edge.source_id], node_to_idx[edge.target_id]
                adj_matrix[i][j] = 1
                adj_matrix[j][i] = 1  # 无向图
        
        # 使用SVD进行降维
        try:
            from sklearn.decomposition import TruncatedSVD
            svd = TruncatedSVD(n_components=min(self.embedding_dim, len(nodes)))
            embeddings = svd.fit_transform(adj_matrix)
            
            # 返回所有节点嵌入的平均值
            return np.mean(embeddings, axis=0)
        except:
            return np.random.rand(self.embedding_dim)
    
    def _generate_random_walks(self, kg: KnowledgeGraph, num_walks: int = 10, walk_length: int = 20) -> List[List[str]]:
        """
        生成随机游走序列
        
        Args:
            kg: 知识图谱
            num_walks: 每个节点的游走次数
            walk_length: 游走长度
            
        Returns:
            随机游走序列列表
        """
        walks = []
        nodes = kg.get_all_nodes()
        
        # 构建邻接表
        adj_list = {}
        for node in nodes:
            adj_list[node.id] = []
        
        for edge in kg.get_all_edges():
            if edge.source_id in adj_list and edge.target_id in adj_list:
                adj_list[edge.source_id].append(edge.target_id)
                adj_list[edge.target_id].append(edge.source_id)
        
        # 为每个节点生成随机游走
        for node in nodes:
            for _ in range(num_walks):
                walk = self._single_random_walk(adj_list, node.id, walk_length)
                if len(walk) > 1:
                    walks.append(walk)
        
        return walks
    
    def _single_random_walk(self, adj_list: Dict[str, List[str]], start_node: str, walk_length: int) -> List[str]:
        """
        执行单次随机游走
        
        Args:
            adj_list: 邻接表
            start_node: 起始节点
            walk_length: 游走长度
            
        Returns:
            游走路径
        """
        walk = [start_node]
        current_node = start_node
        
        for _ in range(walk_length - 1):
            neighbors = adj_list.get(current_node, [])
            if not neighbors:
                break
            
            # 随机选择下一个节点
            next_node = np.random.choice(neighbors)
            walk.append(next_node)
            current_node = next_node
        
        return walk
    
    def _generate_entity_cache_key(self, entity: Node, context: Optional[Dict[str, Any]]) -> str:
        """
        生成实体缓存键
        
        Args:
            entity: 实体节点
            context: 上下文信息
            
        Returns:
            缓存键
        """
        key_data = {
            'entity_id': entity.id,
            'entity_label': entity.label,
            'entity_type': entity.type,
            'entity_properties': entity.properties,
            'context': context or {}
        }
        
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _generate_relation_cache_key(self, relation: Edge, context: Optional[Dict[str, Any]]) -> str:
        """
        生成关系缓存键
        
        Args:
            relation: 关系边
            context: 上下文信息
            
        Returns:
            缓存键
        """
        key_data = {
            'relation_id': relation.id,
            'relation_type': relation.type,
            'relation_label': relation.label,
            'relation_properties': relation.properties,
            'context': context or {}
        }
        
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _generate_graph_cache_key(self, kg: KnowledgeGraph, method: str) -> str:
        """
        生成图缓存键
        
        Args:
            kg: 知识图谱
            method: 图嵌入方法
            
        Returns:
            缓存键
        """
        # 使用图的基本统计信息作为缓存键
        key_data = {
            'num_nodes': len(kg.get_all_nodes()),
            'num_edges': len(kg.get_all_edges()),
            'method': method,
            'embedding_dim': self.embedding_dim
        }
        
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def clear_cache(self):
        """
        清空嵌入缓存
        """
        self.entity_embeddings.clear()
        self.relation_embeddings.clear()
        self.graph_embeddings.clear()
        self.logger.info("嵌入缓存已清空")
    
    def save_embeddings(self, filepath: str) -> bool:
        """
        保存嵌入缓存到文件
        
        Args:
            filepath: 文件路径
            
        Returns:
            是否保存成功
        """
        try:
            cache_data = {
                'entity_embeddings': {k: v.tolist() for k, v in self.entity_embeddings.items()},
                'relation_embeddings': {k: v.tolist() for k, v in self.relation_embeddings.items()},
                'graph_embeddings': {k: v.tolist() for k, v in self.graph_embeddings.items()},
                'embedding_dim': self.embedding_dim,
                'timestamp': datetime.now().isoformat()
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"嵌入缓存已保存到: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"嵌入缓存保存失败: {str(e)}")
            return False
    
    def load_embeddings(self, filepath: str) -> bool:
        """
        从文件加载嵌入缓存
        
        Args:
            filepath: 文件路径
            
        Returns:
            是否加载成功
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # 恢复嵌入缓存
            self.entity_embeddings = {
                k: np.array(v) for k, v in cache_data.get('entity_embeddings', {}).items()
            }
            self.relation_embeddings = {
                k: np.array(v) for k, v in cache_data.get('relation_embeddings', {}).items()
            }
            self.graph_embeddings = {
                k: np.array(v) for k, v in cache_data.get('graph_embeddings', {}).items()
            }
            
            self.logger.info(f"嵌入缓存已从文件加载: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"嵌入缓存加载失败: {str(e)}")
            return False
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        获取缓存信息
        
        Returns:
            缓存信息字典
        """
        return {
            'entity_embeddings_count': len(self.entity_embeddings),
            'relation_embeddings_count': len(self.relation_embeddings),
            'graph_embeddings_count': len(self.graph_embeddings),
            'embedding_dim': self.embedding_dim,
            'cache_dir': self.cache_dir,
            'models_loaded': {
                'word2vec': self.word2vec_model is not None,
                'fasttext': self.fasttext_model is not None,
                'doc2vec': self.doc2vec_model is not None,
                'tfidf': self.tfidf_vectorizer is not None
            }
        }