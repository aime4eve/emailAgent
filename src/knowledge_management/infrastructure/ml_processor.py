# -*- coding: utf-8 -*-
"""
机器学习处理器
实现基于scikit-learn的机器学习算法
"""

from typing import List, Dict, Optional, Any, Tuple
import numpy as np
import logging
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.neighbors import NearestNeighbors
import pickle
import os
from datetime import datetime


class MLProcessor:
    """
    机器学习处理器
    提供各种机器学习算法的统一接口
    """
    
    def __init__(self, model_cache_dir: str = "models"):
        """
        初始化ML处理器
        
        Args:
            model_cache_dir: 模型缓存目录
        """
        self.model_cache_dir = model_cache_dir
        self.logger = logging.getLogger(__name__)
        self.scaler = StandardScaler()
        self.models = {}
        
        # 确保模型缓存目录存在
        os.makedirs(model_cache_dir, exist_ok=True)
        
        # 初始化各种算法的默认参数
        self.clustering_params = {
            'kmeans': {'random_state': 42, 'n_init': 10},
            'dbscan': {'eps': 0.5, 'min_samples': 5},
            'agglomerative': {'linkage': 'ward'}
        }
        
        self.anomaly_params = {
            'isolation_forest': {'random_state': 42, 'n_estimators': 100}
        }
    
    def cluster_entities(self, embeddings: np.ndarray, n_clusters: Optional[int] = None, 
                        method: str = 'kmeans') -> np.ndarray:
        """
        对实体进行聚类分析
        
        Args:
            embeddings: 实体嵌入向量矩阵
            n_clusters: 聚类数量，None表示自动确定
            method: 聚类方法 ('kmeans', 'dbscan', 'agglomerative')
            
        Returns:
            聚类标签数组
        """
        self.logger.info(f"开始聚类分析，方法: {method}, 数据点数量: {len(embeddings)}")
        
        if len(embeddings) < 2:
            self.logger.warning("数据点数量不足，无法进行聚类")
            return np.zeros(len(embeddings))
        
        try:
            # 数据标准化
            scaled_embeddings = self.scaler.fit_transform(embeddings)
            
            if method == 'kmeans':
                return self._kmeans_clustering(scaled_embeddings, n_clusters)
            elif method == 'dbscan':
                return self._dbscan_clustering(scaled_embeddings)
            elif method == 'agglomerative':
                return self._agglomerative_clustering(scaled_embeddings, n_clusters)
            else:
                raise ValueError(f"不支持的聚类方法: {method}")
                
        except Exception as e:
            self.logger.error(f"聚类分析失败: {str(e)}")
            return np.zeros(len(embeddings))
    
    def detect_anomalies(self, features: np.ndarray, contamination: float = 0.1, 
                        method: str = 'isolation_forest') -> np.ndarray:
        """
        检测异常数据点
        
        Args:
            features: 特征矩阵
            contamination: 异常数据比例
            method: 异常检测方法
            
        Returns:
            异常标签数组 (1表示正常，-1表示异常)
        """
        self.logger.info(f"开始异常检测，方法: {method}, 异常比例: {contamination}")
        
        if len(features) < 10:
            self.logger.warning("数据点数量不足，无法进行异常检测")
            return np.ones(len(features))
        
        try:
            # 数据标准化
            scaled_features = self.scaler.fit_transform(features)
            
            if method == 'isolation_forest':
                return self._isolation_forest_detection(scaled_features, contamination)
            else:
                raise ValueError(f"不支持的异常检测方法: {method}")
                
        except Exception as e:
            self.logger.error(f"异常检测失败: {str(e)}")
            return np.ones(len(features))
    
    def calculate_similarity_matrix(self, embeddings: np.ndarray, 
                                  method: str = 'cosine') -> np.ndarray:
        """
        计算相似度矩阵
        
        Args:
            embeddings: 嵌入向量矩阵
            method: 相似度计算方法 ('cosine', 'euclidean')
            
        Returns:
            相似度矩阵
        """
        self.logger.info(f"计算相似度矩阵，方法: {method}, 向量数量: {len(embeddings)}")
        
        try:
            if method == 'cosine':
                return cosine_similarity(embeddings)
            elif method == 'euclidean':
                distances = euclidean_distances(embeddings)
                # 转换为相似度 (距离越小，相似度越高)
                max_distance = np.max(distances)
                return 1 - (distances / max_distance) if max_distance > 0 else np.ones_like(distances)
            else:
                raise ValueError(f"不支持的相似度计算方法: {method}")
                
        except Exception as e:
            self.logger.error(f"相似度矩阵计算失败: {str(e)}")
            return np.eye(len(embeddings))  # 返回单位矩阵作为默认值
    
    def find_nearest_neighbors(self, embeddings: np.ndarray, query_embedding: np.ndarray, 
                              k: int = 5) -> Tuple[np.ndarray, np.ndarray]:
        """
        查找最近邻
        
        Args:
            embeddings: 候选嵌入向量矩阵
            query_embedding: 查询嵌入向量
            k: 返回的邻居数量
            
        Returns:
            (距离数组, 索引数组)
        """
        self.logger.info(f"查找最近邻，k={k}")
        
        try:
            # 使用KNN算法
            knn = NearestNeighbors(n_neighbors=min(k, len(embeddings)), metric='cosine')
            knn.fit(embeddings)
            
            distances, indices = knn.kneighbors([query_embedding])
            return distances[0], indices[0]
            
        except Exception as e:
            self.logger.error(f"最近邻查找失败: {str(e)}")
            return np.array([]), np.array([])
    
    def reduce_dimensionality(self, embeddings: np.ndarray, method: str = 'pca', 
                            n_components: int = 2) -> np.ndarray:
        """
        降维处理
        
        Args:
            embeddings: 高维嵌入向量矩阵
            method: 降维方法 ('pca', 'tsne')
            n_components: 目标维度
            
        Returns:
            降维后的向量矩阵
        """
        self.logger.info(f"降维处理，方法: {method}, 目标维度: {n_components}")
        
        try:
            if method == 'pca':
                reducer = PCA(n_components=n_components, random_state=42)
            elif method == 'tsne':
                reducer = TSNE(n_components=n_components, random_state=42, perplexity=min(30, len(embeddings)-1))
            else:
                raise ValueError(f"不支持的降维方法: {method}")
            
            reduced_embeddings = reducer.fit_transform(embeddings)
            return reduced_embeddings
            
        except Exception as e:
            self.logger.error(f"降维处理失败: {str(e)}")
            return embeddings[:, :n_components] if embeddings.shape[1] >= n_components else embeddings
    
    def save_model(self, model: Any, model_name: str) -> bool:
        """
        保存模型到文件
        
        Args:
            model: 要保存的模型
            model_name: 模型名称
            
        Returns:
            是否保存成功
        """
        try:
            model_path = os.path.join(self.model_cache_dir, f"{model_name}.pkl")
            with open(model_path, 'wb') as f:
                pickle.dump({
                    'model': model,
                    'timestamp': datetime.now(),
                    'model_name': model_name
                }, f)
            
            self.logger.info(f"模型已保存: {model_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"模型保存失败: {str(e)}")
            return False
    
    def load_model(self, model_name: str) -> Optional[Any]:
        """
        从文件加载模型
        
        Args:
            model_name: 模型名称
            
        Returns:
            加载的模型，失败时返回None
        """
        try:
            model_path = os.path.join(self.model_cache_dir, f"{model_name}.pkl")
            if not os.path.exists(model_path):
                self.logger.warning(f"模型文件不存在: {model_path}")
                return None
            
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.logger.info(f"模型已加载: {model_path}")
            return model_data['model']
            
        except Exception as e:
            self.logger.error(f"模型加载失败: {str(e)}")
            return None
    
    def _kmeans_clustering(self, embeddings: np.ndarray, n_clusters: Optional[int]) -> np.ndarray:
        """
        K-means聚类
        
        Args:
            embeddings: 嵌入向量矩阵
            n_clusters: 聚类数量
            
        Returns:
            聚类标签
        """
        if n_clusters is None:
            n_clusters = self._estimate_optimal_clusters(embeddings)
        
        n_clusters = min(n_clusters, len(embeddings))  # 确保聚类数不超过数据点数
        
        kmeans = KMeans(n_clusters=n_clusters, **self.clustering_params['kmeans'])
        labels = kmeans.fit_predict(embeddings)
        
        # 缓存模型
        self.models['kmeans'] = kmeans
        
        return labels
    
    def _dbscan_clustering(self, embeddings: np.ndarray) -> np.ndarray:
        """
        DBSCAN聚类
        
        Args:
            embeddings: 嵌入向量矩阵
            
        Returns:
            聚类标签
        """
        dbscan = DBSCAN(**self.clustering_params['dbscan'])
        labels = dbscan.fit_predict(embeddings)
        
        # 缓存模型
        self.models['dbscan'] = dbscan
        
        return labels
    
    def _agglomerative_clustering(self, embeddings: np.ndarray, n_clusters: Optional[int]) -> np.ndarray:
        """
        层次聚类
        
        Args:
            embeddings: 嵌入向量矩阵
            n_clusters: 聚类数量
            
        Returns:
            聚类标签
        """
        if n_clusters is None:
            n_clusters = self._estimate_optimal_clusters(embeddings)
        
        n_clusters = min(n_clusters, len(embeddings))
        
        agg_clustering = AgglomerativeClustering(
            n_clusters=n_clusters, 
            **self.clustering_params['agglomerative']
        )
        labels = agg_clustering.fit_predict(embeddings)
        
        # 缓存模型
        self.models['agglomerative'] = agg_clustering
        
        return labels
    
    def _isolation_forest_detection(self, features: np.ndarray, contamination: float) -> np.ndarray:
        """
        孤立森林异常检测
        
        Args:
            features: 特征矩阵
            contamination: 异常比例
            
        Returns:
            异常标签
        """
        iso_forest = IsolationForest(
            contamination=contamination,
            **self.anomaly_params['isolation_forest']
        )
        labels = iso_forest.fit_predict(features)
        
        # 缓存模型
        self.models['isolation_forest'] = iso_forest
        
        return labels
    
    def _estimate_optimal_clusters(self, embeddings: np.ndarray) -> int:
        """
        估计最优聚类数量
        
        Args:
            embeddings: 嵌入向量矩阵
            
        Returns:
            估计的最优聚类数
        """
        n_samples = len(embeddings)
        
        # 使用肘部法则的简化版本
        if n_samples < 10:
            return 2
        elif n_samples < 50:
            return min(5, n_samples // 3)
        elif n_samples < 200:
            return min(10, n_samples // 10)
        else:
            return min(20, int(np.sqrt(n_samples)))
    
    def get_clustering_metrics(self, embeddings: np.ndarray, labels: np.ndarray) -> Dict[str, float]:
        """
        计算聚类评估指标
        
        Args:
            embeddings: 嵌入向量矩阵
            labels: 聚类标签
            
        Returns:
            评估指标字典
        """
        try:
            from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
            
            metrics = {}
            
            # 轮廓系数 (越高越好)
            if len(set(labels)) > 1:
                metrics['silhouette_score'] = silhouette_score(embeddings, labels)
                metrics['calinski_harabasz_score'] = calinski_harabasz_score(embeddings, labels)
                metrics['davies_bouldin_score'] = davies_bouldin_score(embeddings, labels)
            
            # 聚类数量
            metrics['n_clusters'] = len(set(labels))
            
            # 噪声点数量 (对于DBSCAN)
            metrics['n_noise'] = np.sum(labels == -1)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"聚类指标计算失败: {str(e)}")
            return {}
    
    def get_anomaly_metrics(self, labels: np.ndarray) -> Dict[str, Any]:
        """
        计算异常检测评估指标
        
        Args:
            labels: 异常标签 (1表示正常，-1表示异常)
            
        Returns:
            评估指标字典
        """
        try:
            metrics = {
                'total_samples': len(labels),
                'normal_samples': np.sum(labels == 1),
                'anomaly_samples': np.sum(labels == -1),
                'anomaly_ratio': np.sum(labels == -1) / len(labels)
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"异常检测指标计算失败: {str(e)}")
            return {}
    
    def batch_process(self, data_batches: List[np.ndarray], 
                     process_func: callable, **kwargs) -> List[Any]:
        """
        批量处理数据
        
        Args:
            data_batches: 数据批次列表
            process_func: 处理函数
            **kwargs: 处理函数的参数
            
        Returns:
            处理结果列表
        """
        results = []
        
        for i, batch in enumerate(data_batches):
            try:
                self.logger.info(f"处理批次 {i+1}/{len(data_batches)}")
                result = process_func(batch, **kwargs)
                results.append(result)
            except Exception as e:
                self.logger.error(f"批次 {i+1} 处理失败: {str(e)}")
                results.append(None)
        
        return results
    
    def clear_cache(self):
        """
        清空模型缓存
        """
        self.models.clear()
        self.logger.info("模型缓存已清空")
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息
        
        Returns:
            模型信息字典
        """
        info = {
            'cached_models': list(self.models.keys()),
            'model_cache_dir': self.model_cache_dir,
            'clustering_params': self.clustering_params,
            'anomaly_params': self.anomaly_params
        }
        
        # 获取缓存文件信息
        cached_files = []
        if os.path.exists(self.model_cache_dir):
            for filename in os.listdir(self.model_cache_dir):
                if filename.endswith('.pkl'):
                    filepath = os.path.join(self.model_cache_dir, filename)
                    stat = os.stat(filepath)
                    cached_files.append({
                        'filename': filename,
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
        
        info['cached_files'] = cached_files
        
        return info