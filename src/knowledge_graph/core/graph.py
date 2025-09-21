#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识图谱类
"""

from typing import Dict, List, Optional, Set, Any
from collections import defaultdict
import json

from .node import Node
from .edge import Edge

class KnowledgeGraph:
    """知识图谱类"""
    
    def __init__(self):
        """初始化知识图谱"""
        self._nodes: Dict[str, Node] = {}
        self._edges: Dict[str, Edge] = {}
        self._node_edges: Dict[str, Set[str]] = defaultdict(set)
    
    def add_node(self, node: Node) -> bool:
        """添加节点"""
        if node.id in self._nodes:
            return False
        
        self._nodes[node.id] = node
        return True
    
    def add_edge(self, edge: Edge) -> bool:
        """添加边"""
        if edge.id in self._edges:
            return False
        
        # 检查源节点和目标节点是否存在
        if edge.source_id not in self._nodes or edge.target_id not in self._nodes:
            return False
        
        self._edges[edge.id] = edge
        self._node_edges[edge.source_id].add(edge.id)
        self._node_edges[edge.target_id].add(edge.id)
        
        return True
    
    def get_node(self, node_id: str) -> Optional[Node]:
        """获取节点"""
        return self._nodes.get(node_id)
    
    def get_edge(self, edge_id: str) -> Optional[Edge]:
        """获取边"""
        return self._edges.get(edge_id)
    
    def get_all_nodes(self) -> List[Node]:
        """获取所有节点"""
        return list(self._nodes.values())
    
    def get_all_edges(self) -> List[Edge]:
        """获取所有边"""
        return list(self._edges.values())
    
    def remove_node(self, node_id: str) -> bool:
        """删除节点"""
        if node_id not in self._nodes:
            return False
        
        # 删除相关的边
        edges_to_remove = list(self._node_edges[node_id])
        for edge_id in edges_to_remove:
            self.remove_edge(edge_id)
        
        # 删除节点
        del self._nodes[node_id]
        del self._node_edges[node_id]
        
        return True
    
    def remove_edge(self, edge_id: str) -> bool:
        """删除边"""
        if edge_id not in self._edges:
            return False
        
        edge = self._edges[edge_id]
        
        # 从节点的边集合中移除
        self._node_edges[edge.source_id].discard(edge_id)
        self._node_edges[edge.target_id].discard(edge_id)
        
        # 删除边
        del self._edges[edge_id]
        
        return True
    
    def get_neighbors(self, node_id: str) -> List[Node]:
        """获取邻居节点"""
        if node_id not in self._nodes:
            return []
        
        neighbors = []
        for edge_id in self._node_edges[node_id]:
            edge = self._edges[edge_id]
            if edge.source_id == node_id:
                neighbor_id = edge.target_id
            else:
                neighbor_id = edge.source_id
            
            if neighbor_id in self._nodes:
                neighbors.append(self._nodes[neighbor_id])
        
        return neighbors
    
    def get_node_edges(self, node_id: str) -> List[Edge]:
        """获取节点的所有边"""
        if node_id not in self._nodes:
            return []
        
        return [self._edges[edge_id] for edge_id in self._node_edges[node_id]]
    
    def find_nodes_by_type(self, node_type: str) -> List[Node]:
        """根据类型查找节点"""
        return [node for node in self._nodes.values() if node.node_type == node_type]
    
    def find_nodes_by_label(self, label: str) -> List[Node]:
        """根据标签查找节点"""
        return [node for node in self._nodes.values() if node.label == label]
    
    def find_edges_by_type(self, relation_type: str) -> List[Edge]:
        """根据关系类型查找边"""
        return [edge for edge in self._edges.values() if edge.relation_type == relation_type]
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取图谱统计信息"""
        node_types = defaultdict(int)
        edge_types = defaultdict(int)
        
        for node in self._nodes.values():
            node_types[node.node_type] += 1
        
        for edge in self._edges.values():
            edge_types[edge.relation_type] += 1
        
        return {
            'total_nodes': len(self._nodes),
            'total_edges': len(self._edges),
            'node_types': dict(node_types),
            'edge_types': dict(edge_types)
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'nodes': [node.to_dict() for node in self._nodes.values()],
            'edges': [edge.to_dict() for edge in self._edges.values()],
            'statistics': self.get_statistics()
        }
    
    def to_json(self, indent: int = 2) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)
    
    def clear(self) -> None:
        """清空图谱"""
        self._nodes.clear()
        self._edges.clear()
        self._node_edges.clear()
    
    def __len__(self) -> int:
        """返回节点数量"""
        return len(self._nodes)
    
    def __str__(self) -> str:
        stats = self.get_statistics()
        return f"KnowledgeGraph(nodes={stats['total_nodes']}, edges={stats['total_edges']})"
    
    def __repr__(self) -> str:
        return self.__str__()