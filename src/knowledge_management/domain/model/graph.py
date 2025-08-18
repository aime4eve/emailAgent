# -*- coding: utf-8 -*-
"""
知识图谱主类
"""

from typing import Dict, List, Set, Optional, Any, Tuple
import networkx as nx
import json
from .node import Node
from .edge import Edge


class KnowledgeGraph:
    """
    知识图谱主类，管理节点和边的集合
    """
    
    def __init__(self):
        """
        初始化知识图谱
        """
        self.nodes: Dict[str, Node] = {}
        self.edges: Dict[str, Edge] = {}
        self._nx_graph = nx.Graph()
        
    def add_node(self, node: Node) -> None:
        """
        添加节点到图中
        
        Args:
            node: 要添加的节点
        """
        self.nodes[node.id] = node
        self._nx_graph.add_node(node.id, **node.to_dict())
        
    def add_edge(self, edge: Edge) -> None:
        """
        添加边到图中
        
        Args:
            edge: 要添加的边
        """
        # 确保源节点和目标节点存在
        if edge.source_id not in self.nodes:
            raise ValueError(f"Source node {edge.source_id} not found")
        if edge.target_id not in self.nodes:
            raise ValueError(f"Target node {edge.target_id} not found")
            
        self.edges[edge.id] = edge
        self._nx_graph.add_edge(
            edge.source_id, 
            edge.target_id, 
            edge_id=edge.id,
            **edge.to_dict()
        )
        
    def remove_node(self, node_id: str) -> None:
        """
        从图中移除节点及其相关边
        
        Args:
            node_id: 要移除的节点ID
        """
        if node_id not in self.nodes:
            return
            
        # 移除相关的边
        edges_to_remove = []
        for edge in self.edges.values():
            if edge.source_id == node_id or edge.target_id == node_id:
                edges_to_remove.append(edge.id)
                
        for edge_id in edges_to_remove:
            self.remove_edge(edge_id)
            
        # 移除节点
        del self.nodes[node_id]
        if self._nx_graph.has_node(node_id):
            self._nx_graph.remove_node(node_id)
            
    def remove_edge(self, edge_id: str) -> None:
        """
        从图中移除边
        
        Args:
            edge_id: 要移除的边ID
        """
        if edge_id not in self.edges:
            return
            
        edge = self.edges[edge_id]
        del self.edges[edge_id]
        
        if self._nx_graph.has_edge(edge.source_id, edge.target_id):
            self._nx_graph.remove_edge(edge.source_id, edge.target_id)
            
    def get_node(self, node_id: str) -> Optional[Node]:
        """
        获取节点
        
        Args:
            node_id: 节点ID
            
        Returns:
            节点实例或None
        """
        return self.nodes.get(node_id)
        
    def get_all_nodes(self) -> List[Node]:
        """
        获取所有节点
        
        Returns:
            所有节点的列表
        """
        return list(self.nodes.values())
        
    def get_all_edges(self) -> List[Edge]:
        """
        获取所有边
        
        Returns:
            所有边的列表
        """
        return list(self.edges.values())
        
    def has_node(self, node_id: str) -> bool:
        """
        检查节点是否存在
        
        Args:
            node_id: 节点ID
            
        Returns:
            节点是否存在
        """
        return node_id in self.nodes
        
    def get_edge(self, edge_id: str) -> Optional[Edge]:
        """
        获取边
        
        Args:
            edge_id: 边ID
            
        Returns:
            边实例或None
        """
        return self.edges.get(edge_id)
        
    def get_neighbors(self, node_id: str) -> List[str]:
        """
        获取节点的邻居节点ID列表
        
        Args:
            node_id: 节点ID
            
        Returns:
            邻居节点ID列表
        """
        if node_id not in self.nodes:
            return []
        return list(self._nx_graph.neighbors(node_id))
        
    def get_node_edges(self, node_id: str) -> List[Edge]:
        """
        获取与指定节点相关的所有边
        
        Args:
            node_id: 节点ID
            
        Returns:
            边列表
        """
        result = []
        for edge in self.edges.values():
            if edge.source_id == node_id or edge.target_id == node_id:
                result.append(edge)
        return result
        
    def search_nodes(self, query: str, search_fields: List[str] = None) -> List[Node]:
        """
        搜索节点
        
        Args:
            query: 搜索查询字符串
            search_fields: 要搜索的字段列表，默认为['label']
            
        Returns:
            匹配的节点列表
        """
        if search_fields is None:
            search_fields = ['label']
            
        results = []
        query_lower = query.lower()
        
        for node in self.nodes.values():
            for field in search_fields:
                if field == 'label' and query_lower in node.label.lower():
                    results.append(node)
                    break
                elif field in node.properties:
                    prop_value = str(node.properties[field]).lower()
                    if query_lower in prop_value:
                        results.append(node)
                        break
                        
        return results
        
    def filter_nodes_by_type(self, node_type: str) -> List[Node]:
        """
        按类型筛选节点
        
        Args:
            node_type: 节点类型
            
        Returns:
            指定类型的节点列表
        """
        return [node for node in self.nodes.values() if node.type == node_type]
        
    def get_shortest_path(self, source_id: str, target_id: str) -> Optional[List[str]]:
        """
        获取两个节点之间的最短路径
        
        Args:
            source_id: 源节点ID
            target_id: 目标节点ID
            
        Returns:
            最短路径节点ID列表，如果不存在路径则返回None
        """
        try:
            return nx.shortest_path(self._nx_graph, source_id, target_id)
        except nx.NetworkXNoPath:
            return None
            
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取图的统计信息
        
        Returns:
            包含统计信息的字典
        """
        return {
            'node_count': len(self.nodes),
            'edge_count': len(self.edges),
            'node_types': list(set(node.type for node in self.nodes.values())),
            'edge_types': list(set(edge.type for edge in self.edges.values())),
            'is_connected': nx.is_connected(self._nx_graph) if self.nodes else False,
            'density': nx.density(self._nx_graph) if self.nodes else 0.0
        }
        
    def to_dict(self) -> Dict[str, Any]:
        """
        将图转换为字典格式
        
        Returns:
            图的字典表示
        """
        return {
            'nodes': [node.to_dict() for node in self.nodes.values()],
            'edges': [edge.to_dict() for edge in self.edges.values()]
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KnowledgeGraph':
        """
        从字典创建图
        
        Args:
            data: 包含图信息的字典
            
        Returns:
            KnowledgeGraph实例
        """
        graph = cls()
        
        # 添加节点
        for node_data in data.get('nodes', []):
            node = Node.from_dict(node_data)
            graph.add_node(node)
            
        # 添加边
        for edge_data in data.get('edges', []):
            edge = Edge.from_dict(edge_data)
            graph.add_edge(edge)
            
        return graph
        
    def save_to_json(self, filepath: str) -> None:
        """
        将图保存为JSON文件
        
        Args:
            filepath: 文件路径
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
            
    @classmethod
    def load_from_json(cls, filepath: str) -> 'KnowledgeGraph':
        """
        从JSON文件加载图
        
        Args:
            filepath: 文件路径
            
        Returns:
            KnowledgeGraph实例
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)
        
    def clear(self) -> None:
        """
        清空图中的所有节点和边
        """
        self.nodes.clear()
        self.edges.clear()
        self._nx_graph.clear()