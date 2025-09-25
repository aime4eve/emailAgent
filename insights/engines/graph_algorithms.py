# -*- coding: utf-8 -*-
"""
图算法引擎

提供各种图算法功能，包括中心性分析、社区发现、路径分析等。
"""

import logging
import math
from typing import List, Dict, Any, Tuple, Optional, Set
from dataclasses import dataclass
from collections import defaultdict, deque

try:
    import networkx as nx
except ImportError:
    nx = None

try:
    import igraph as ig
except ImportError:
    ig = None

from ..core.database_manager import DatabaseManager
from ..core.exceptions import AlgorithmError
from ..utils.singleton import Singleton

@dataclass
class CentralityResult:
    """中心性分析结果"""
    node_id: str
    score: float
    rank: int
    
@dataclass
class CommunityResult:
    """社区发现结果"""
    community_id: int
    nodes: List[str]
    size: int
    modularity: float
    
@dataclass
class PathResult:
    """路径分析结果"""
    source: str
    target: str
    path: List[str]
    length: int
    weight: float
    
class GraphAlgorithms(metaclass=Singleton):
    """图算法引擎
    
    提供各种图分析算法的实现。
    """
    
    def __init__(self):
        """初始化图算法引擎"""
        self.logger = logging.getLogger(__name__)
        self.db_manager = DatabaseManager()
        self.graph_cache: Optional[nx.Graph] = None
        self.cache_timestamp = None
        
    def initialize(self) -> bool:
        """初始化图算法引擎
        
        Returns:
            是否初始化成功
        """
        try:
            if nx is None:
                raise ImportError("networkx not installed")
                
            self.logger.info("图算法引擎初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"图算法引擎初始化失败: {e}")
            raise AlgorithmError(f"Failed to initialize graph algorithms: {e}")
            
    def load_graph_from_database(self, force_reload: bool = False) -> nx.Graph:
        """从数据库加载图数据
        
        Args:
            force_reload: 是否强制重新加载
            
        Returns:
            NetworkX图对象
        """
        try:
            if self.graph_cache is not None and not force_reload:
                return self.graph_cache
                
            # 创建新的图对象
            G = nx.Graph()
            
            # 加载节点
            node_query = """
            MATCH (n)
            RETURN n.id as id, labels(n)[0] as label, properties(n) as properties
            """
            
            node_results = self.db_manager.execute_cypher(node_query)
            
            for result in node_results:
                node_id = result['id']
                label = result['label']
                properties = result['properties']
                properties['label'] = label
                G.add_node(node_id, **properties)
                
            # 加载边
            edge_query = """
            MATCH (source)-[r]->(target)
            RETURN source.id as source, target.id as target, 
                   type(r) as relation_type, properties(r) as properties
            """
            
            edge_results = self.db_manager.execute_cypher(edge_query)
            
            for result in edge_results:
                source = result['source']
                target = result['target']
                relation_type = result['relation_type']
                properties = result['properties']
                
                # 计算边权重
                weight = properties.get('confidence', 1.0)
                
                G.add_edge(source, target, 
                          relation_type=relation_type,
                          weight=weight,
                          **properties)
                          
            self.graph_cache = G
            self.logger.info(f"图数据加载完成: {G.number_of_nodes()} 节点, {G.number_of_edges()} 边")
            
            return G
            
        except Exception as e:
            self.logger.error(f"加载图数据失败: {e}")
            raise AlgorithmError(f"Failed to load graph data: {e}")
            
    def calculate_pagerank(self, alpha: float = 0.85, max_iter: int = 100,
                          tol: float = 1e-6) -> List[CentralityResult]:
        """计算PageRank中心性
        
        Args:
            alpha: 阻尼系数
            max_iter: 最大迭代次数
            tol: 收敛容差
            
        Returns:
            PageRank结果列表
        """
        try:
            G = self.load_graph_from_database()
            
            if G.number_of_nodes() == 0:
                return []
                
            # 计算PageRank
            pagerank_scores = nx.pagerank(G, alpha=alpha, max_iter=max_iter, tol=tol)
            
            # 排序并创建结果
            sorted_scores = sorted(pagerank_scores.items(), key=lambda x: x[1], reverse=True)
            
            results = []
            for rank, (node_id, score) in enumerate(sorted_scores, 1):
                results.append(CentralityResult(
                    node_id=node_id,
                    score=score,
                    rank=rank
                ))
                
            self.logger.info(f"PageRank计算完成: {len(results)} 个节点")
            return results
            
        except Exception as e:
            self.logger.error(f"PageRank计算失败: {e}")
            raise AlgorithmError(f"PageRank calculation failed: {e}")
            
    def calculate_betweenness_centrality(self, k: Optional[int] = None) -> List[CentralityResult]:
        """计算介数中心性
        
        Args:
            k: 采样节点数量，None表示使用所有节点
            
        Returns:
            介数中心性结果列表
        """
        try:
            G = self.load_graph_from_database()
            
            if G.number_of_nodes() == 0:
                return []
                
            # 计算介数中心性
            betweenness_scores = nx.betweenness_centrality(G, k=k, normalized=True)
            
            # 排序并创建结果
            sorted_scores = sorted(betweenness_scores.items(), key=lambda x: x[1], reverse=True)
            
            results = []
            for rank, (node_id, score) in enumerate(sorted_scores, 1):
                results.append(CentralityResult(
                    node_id=node_id,
                    score=score,
                    rank=rank
                ))
                
            self.logger.info(f"介数中心性计算完成: {len(results)} 个节点")
            return results
            
        except Exception as e:
            self.logger.error(f"介数中心性计算失败: {e}")
            raise AlgorithmError(f"Betweenness centrality calculation failed: {e}")
            
    def calculate_closeness_centrality(self) -> List[CentralityResult]:
        """计算接近中心性
        
        Returns:
            接近中心性结果列表
        """
        try:
            G = self.load_graph_from_database()
            
            if G.number_of_nodes() == 0:
                return []
                
            # 计算接近中心性
            closeness_scores = nx.closeness_centrality(G)
            
            # 排序并创建结果
            sorted_scores = sorted(closeness_scores.items(), key=lambda x: x[1], reverse=True)
            
            results = []
            for rank, (node_id, score) in enumerate(sorted_scores, 1):
                results.append(CentralityResult(
                    node_id=node_id,
                    score=score,
                    rank=rank
                ))
                
            self.logger.info(f"接近中心性计算完成: {len(results)} 个节点")
            return results
            
        except Exception as e:
            self.logger.error(f"接近中心性计算失败: {e}")
            raise AlgorithmError(f"Closeness centrality calculation failed: {e}")
            
    def detect_communities_louvain(self, resolution: float = 1.0, 
                                  random_state: int = 42) -> List[CommunityResult]:
        """使用Louvain算法进行社区发现
        
        Args:
            resolution: 分辨率参数
            random_state: 随机种子
            
        Returns:
            社区发现结果列表
        """
        try:
            G = self.load_graph_from_database()
            
            if G.number_of_nodes() == 0:
                return []
                
            # 使用Louvain算法
            try:
                import community as community_louvain
                partition = community_louvain.best_partition(G, resolution=resolution, random_state=random_state)
                modularity = community_louvain.modularity(partition, G)
            except ImportError:
                # 如果没有python-louvain，使用NetworkX的贪婪模块度最大化
                communities = nx.community.greedy_modularity_communities(G, resolution=resolution)
                partition = {}
                for i, community in enumerate(communities):
                    for node in community:
                        partition[node] = i
                modularity = nx.community.modularity(G, communities)
                
            # 组织结果
            community_nodes = defaultdict(list)
            for node, community_id in partition.items():
                community_nodes[community_id].append(node)
                
            results = []
            for community_id, nodes in community_nodes.items():
                results.append(CommunityResult(
                    community_id=community_id,
                    nodes=nodes,
                    size=len(nodes),
                    modularity=modularity
                ))
                
            # 按社区大小排序
            results.sort(key=lambda x: x.size, reverse=True)
            
            self.logger.info(f"社区发现完成: {len(results)} 个社区, 模块度: {modularity:.4f}")
            return results
            
        except Exception as e:
            self.logger.error(f"社区发现失败: {e}")
            raise AlgorithmError(f"Community detection failed: {e}")
            
    def find_shortest_paths(self, source: str, target: str = None, 
                           cutoff: int = None) -> List[PathResult]:
        """查找最短路径
        
        Args:
            source: 源节点ID
            target: 目标节点ID，None表示查找到所有节点的路径
            cutoff: 路径长度限制
            
        Returns:
            路径结果列表
        """
        try:
            G = self.load_graph_from_database()
            
            if source not in G:
                raise AlgorithmError(f"Source node {source} not found in graph")
                
            results = []
            
            if target is not None:
                # 查找到特定目标的路径
                if target not in G:
                    raise AlgorithmError(f"Target node {target} not found in graph")
                    
                try:
                    path = nx.shortest_path(G, source, target, weight='weight')
                    length = len(path) - 1
                    weight = nx.shortest_path_length(G, source, target, weight='weight')
                    
                    results.append(PathResult(
                        source=source,
                        target=target,
                        path=path,
                        length=length,
                        weight=weight
                    ))
                except nx.NetworkXNoPath:
                    self.logger.warning(f"No path found from {source} to {target}")
                    
            else:
                # 查找到所有可达节点的路径
                try:
                    paths = nx.single_source_shortest_path(G, source, cutoff=cutoff)
                    path_lengths = nx.single_source_shortest_path_length(G, source, cutoff=cutoff, weight='weight')
                    
                    for target_node, path in paths.items():
                        if target_node != source:
                            length = len(path) - 1
                            weight = path_lengths.get(target_node, float('inf'))
                            
                            results.append(PathResult(
                                source=source,
                                target=target_node,
                                path=path,
                                length=length,
                                weight=weight
                            ))
                            
                except Exception as e:
                    self.logger.error(f"路径计算失败: {e}")
                    
            # 按路径长度排序
            results.sort(key=lambda x: x.length)
            
            self.logger.info(f"路径查找完成: {len(results)} 条路径")
            return results
            
        except Exception as e:
            self.logger.error(f"最短路径查找失败: {e}")
            raise AlgorithmError(f"Shortest path finding failed: {e}")
            
    def find_influential_nodes(self, algorithm: str = 'pagerank', 
                              top_k: int = 10) -> List[CentralityResult]:
        """查找影响力节点
        
        Args:
            algorithm: 算法类型 ('pagerank', 'betweenness', 'closeness', 'degree')
            top_k: 返回前k个节点
            
        Returns:
            影响力节点列表
        """
        try:
            if algorithm == 'pagerank':
                results = self.calculate_pagerank()
            elif algorithm == 'betweenness':
                results = self.calculate_betweenness_centrality()
            elif algorithm == 'closeness':
                results = self.calculate_closeness_centrality()
            elif algorithm == 'degree':
                results = self.calculate_degree_centrality()
            else:
                raise AlgorithmError(f"Unknown algorithm: {algorithm}")
                
            return results[:top_k]
            
        except Exception as e:
            self.logger.error(f"影响力节点查找失败: {e}")
            raise AlgorithmError(f"Influential nodes finding failed: {e}")
            
    def calculate_degree_centrality(self) -> List[CentralityResult]:
        """计算度中心性
        
        Returns:
            度中心性结果列表
        """
        try:
            G = self.load_graph_from_database()
            
            if G.number_of_nodes() == 0:
                return []
                
            # 计算度中心性
            degree_scores = nx.degree_centrality(G)
            
            # 排序并创建结果
            sorted_scores = sorted(degree_scores.items(), key=lambda x: x[1], reverse=True)
            
            results = []
            for rank, (node_id, score) in enumerate(sorted_scores, 1):
                results.append(CentralityResult(
                    node_id=node_id,
                    score=score,
                    rank=rank
                ))
                
            self.logger.info(f"度中心性计算完成: {len(results)} 个节点")
            return results
            
        except Exception as e:
            self.logger.error(f"度中心性计算失败: {e}")
            raise AlgorithmError(f"Degree centrality calculation failed: {e}")
            
    def analyze_graph_structure(self) -> Dict[str, Any]:
        """分析图结构特征
        
        Returns:
            图结构分析结果
        """
        try:
            G = self.load_graph_from_database()
            
            if G.number_of_nodes() == 0:
                return {}
                
            # 基本统计
            num_nodes = G.number_of_nodes()
            num_edges = G.number_of_edges()
            density = nx.density(G)
            
            # 连通性分析
            is_connected = nx.is_connected(G)
            num_components = nx.number_connected_components(G)
            largest_cc_size = len(max(nx.connected_components(G), key=len)) if num_components > 0 else 0
            
            # 度分布
            degrees = [d for n, d in G.degree()]
            avg_degree = sum(degrees) / len(degrees) if degrees else 0
            max_degree = max(degrees) if degrees else 0
            min_degree = min(degrees) if degrees else 0
            
            # 聚类系数
            avg_clustering = nx.average_clustering(G)
            
            # 直径和平均路径长度（仅对连通图）
            diameter = None
            avg_path_length = None
            
            if is_connected and num_nodes > 1:
                try:
                    diameter = nx.diameter(G)
                    avg_path_length = nx.average_shortest_path_length(G)
                except:
                    pass
                    
            # 度分布统计
            degree_histogram = {}
            for degree in degrees:
                degree_histogram[degree] = degree_histogram.get(degree, 0) + 1
                
            result = {
                'basic_stats': {
                    'num_nodes': num_nodes,
                    'num_edges': num_edges,
                    'density': density
                },
                'connectivity': {
                    'is_connected': is_connected,
                    'num_components': num_components,
                    'largest_component_size': largest_cc_size
                },
                'degree_stats': {
                    'avg_degree': avg_degree,
                    'max_degree': max_degree,
                    'min_degree': min_degree,
                    'degree_histogram': degree_histogram
                },
                'clustering': {
                    'avg_clustering_coefficient': avg_clustering
                },
                'path_stats': {
                    'diameter': diameter,
                    'avg_path_length': avg_path_length
                }
            }
            
            self.logger.info("图结构分析完成")
            return result
            
        except Exception as e:
            self.logger.error(f"图结构分析失败: {e}")
            raise AlgorithmError(f"Graph structure analysis failed: {e}")
            
    def find_bridges(self) -> List[Tuple[str, str]]:
        """查找桥边（割边）
        
        Returns:
            桥边列表
        """
        try:
            G = self.load_graph_from_database()
            
            if G.number_of_edges() == 0:
                return []
                
            bridges = list(nx.bridges(G))
            
            self.logger.info(f"桥边查找完成: {len(bridges)} 条桥边")
            return bridges
            
        except Exception as e:
            self.logger.error(f"桥边查找失败: {e}")
            raise AlgorithmError(f"Bridge finding failed: {e}")
            
    def find_articulation_points(self) -> List[str]:
        """查找关节点（割点）
        
        Returns:
            关节点列表
        """
        try:
            G = self.load_graph_from_database()
            
            if G.number_of_nodes() == 0:
                return []
                
            articulation_points = list(nx.articulation_points(G))
            
            self.logger.info(f"关节点查找完成: {len(articulation_points)} 个关节点")
            return articulation_points
            
        except Exception as e:
            self.logger.error(f"关节点查找失败: {e}")
            raise AlgorithmError(f"Articulation points finding failed: {e}")
            
    def calculate_node_similarity(self, node1: str, node2: str, 
                                 method: str = 'jaccard') -> float:
        """计算节点相似度
        
        Args:
            node1: 节点1 ID
            node2: 节点2 ID
            method: 相似度计算方法 ('jaccard', 'adamic_adar', 'preferential_attachment')
            
        Returns:
            相似度分数
        """
        try:
            G = self.load_graph_from_database()
            
            if node1 not in G or node2 not in G:
                raise AlgorithmError(f"One or both nodes not found in graph")
                
            if method == 'jaccard':
                # Jaccard系数
                neighbors1 = set(G.neighbors(node1))
                neighbors2 = set(G.neighbors(node2))
                
                intersection = len(neighbors1.intersection(neighbors2))
                union = len(neighbors1.union(neighbors2))
                
                similarity = intersection / union if union > 0 else 0.0
                
            elif method == 'adamic_adar':
                # Adamic-Adar指数
                preds = nx.adamic_adar_index(G, [(node1, node2)])
                similarity = next(preds)[2]
                
            elif method == 'preferential_attachment':
                # 优先连接指数
                preds = nx.preferential_attachment(G, [(node1, node2)])
                similarity = next(preds)[2]
                
            else:
                raise AlgorithmError(f"Unknown similarity method: {method}")
                
            return similarity
            
        except Exception as e:
            self.logger.error(f"节点相似度计算失败: {e}")
            raise AlgorithmError(f"Node similarity calculation failed: {e}")
            
    def clear_cache(self):
        """清空图缓存"""
        self.graph_cache = None
        self.cache_timestamp = None
        self.logger.info("图缓存已清空")