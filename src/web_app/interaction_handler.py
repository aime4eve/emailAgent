# -*- coding: utf-8 -*-
"""
交互功能模块
"""

import json
from typing import Dict, List, Any, Optional, Tuple
from dash import callback_context
import plotly.graph_objects as go
import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from knowledge_graph.graph import KnowledgeGraph
from knowledge_graph.node import Node
from knowledge_graph.edge import Edge
from visualization.plotly_graph import PlotlyGraphVisualizer
from utils.config import Config


class InteractionHandler:
    """
    处理Web应用的交互功能
    """
    
    def __init__(self, knowledge_graph: KnowledgeGraph, visualizer: PlotlyGraphVisualizer, config: Config):
        """
        初始化交互处理器
        
        Args:
            knowledge_graph: 知识图谱实例
            visualizer: 可视化器实例
            config: 配置实例
        """
        self.kg = knowledge_graph
        self.visualizer = visualizer
        self.config = config
        self.selected_nodes = set()
        self.filtered_node_types = set()
        
    def search_nodes(self, query: str, search_fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        搜索节点
        
        Args:
            query: 搜索查询
            search_fields: 搜索字段列表
            
        Returns:
            匹配的节点列表
        """
        if not query.strip():
            return []
            
        search_fields = search_fields or self.config.get('search.search_fields', ['label', 'type'])
        case_sensitive = self.config.get('search.case_sensitive', False)
        max_results = self.config.get('search.max_results', 100)
        
        if not case_sensitive:
            query = query.lower()
            
        results = []
        
        for node in self.kg.get_all_nodes():
            match_found = False
            
            for field in search_fields:
                field_value = getattr(node, field, None)
                if field_value is None:
                    field_value = node.properties.get(field, '')
                    
                if isinstance(field_value, str):
                    search_text = field_value if case_sensitive else field_value.lower()
                    if query in search_text:
                        match_found = True
                        break
                        
            if match_found:
                results.append({
                    'id': node.id,
                    'label': node.label,
                    'type': node.type,
                    'attributes': node.properties
                })
                
                if len(results) >= max_results:
                    break
                    
        return results
        
    def filter_nodes_by_type(self, node_types: List[str]) -> List[str]:
        """
        按类型筛选节点
        
        Args:
            node_types: 节点类型列表
            
        Returns:
            筛选后的节点ID列表
        """
        self.filtered_node_types = set(node_types)
        
        if not node_types:
            return [node.id for node in self.kg.get_all_nodes()]
            
        filtered_nodes = []
        for node in self.kg.get_all_nodes():
            if node.type in node_types:
                filtered_nodes.append(node.id)
                
        return filtered_nodes
        
    def add_node(self, node_id: str, label: str, node_type: str, 
                 attributes: Optional[Dict[str, Any]] = None,
                 position: Optional[Tuple[float, float]] = None) -> bool:
        """
        添加新节点
        
        Args:
            node_id: 节点ID
            label: 节点标签
            node_type: 节点类型
            attributes: 节点属性
            position: 节点位置 (x, y)
            
        Returns:
            是否添加成功
        """
        try:
            # 检查节点是否已存在
            if self.kg.has_node(node_id):
                return False
                
            # 创建新节点
            node = Node(
                node_id=node_id,
                label=label,
                node_type=node_type,
                properties=attributes or {}
            )
            
            # 设置位置
            if position:
                node.set_position(position[0], position[1])
                
            # 添加到图谱
            self.kg.add_node(node)
            return True
            
        except Exception as e:
            print(f"添加节点失败: {str(e)}")
            return False
            
    def remove_node(self, node_id: str) -> bool:
        """
        删除节点
        
        Args:
            node_id: 节点ID
            
        Returns:
            是否删除成功
        """
        try:
            if self.kg.has_node(node_id):
                self.kg.remove_node(node_id)
                # 从选中节点中移除
                self.selected_nodes.discard(node_id)
                return True
            return False
            
        except Exception as e:
            print(f"删除节点失败: {str(e)}")
            return False
            
    def add_edge(self, source_id: str, target_id: str, edge_type: str,
                 attributes: Optional[Dict[str, Any]] = None) -> bool:
        """
        添加新边
        
        Args:
            source_id: 源节点ID
            target_id: 目标节点ID
            edge_type: 边类型
            attributes: 边属性
            
        Returns:
            是否添加成功
        """
        try:
            # 检查节点是否存在
            if not (self.kg.has_node(source_id) and self.kg.has_node(target_id)):
                return False
                
            # 创建新边
            edge = Edge(
                source=source_id,
                target=target_id,
                edge_type=edge_type,
                attributes=attributes or {}
            )
            
            # 添加到图谱
            self.kg.add_edge(edge)
            return True
            
        except Exception as e:
            print(f"添加边失败: {str(e)}")
            return False
            
    def remove_edge(self, source_id: str, target_id: str) -> bool:
        """
        删除边
        
        Args:
            source_id: 源节点ID
            target_id: 目标节点ID
            
        Returns:
            是否删除成功
        """
        try:
            if self.kg.has_edge(source_id, target_id):
                self.kg.remove_edge(source_id, target_id)
                return True
            return False
            
        except Exception as e:
            print(f"删除边失败: {str(e)}")
            return False
            
    def select_node(self, node_id: str) -> None:
        """
        选中节点
        
        Args:
            node_id: 节点ID
        """
        self.selected_nodes.add(node_id)
        
    def deselect_node(self, node_id: str) -> None:
        """
        取消选中节点
        
        Args:
            node_id: 节点ID
        """
        self.selected_nodes.discard(node_id)
        
    def clear_selection(self) -> None:
        """
        清空选择
        """
        self.selected_nodes.clear()
        
    def get_selected_nodes(self) -> List[str]:
        """
        获取选中的节点
        
        Returns:
            选中的节点ID列表
        """
        return list(self.selected_nodes)
        
    def get_node_details(self, node_id: str) -> Optional[Dict[str, Any]]:
        """
        获取节点详情
        
        Args:
            node_id: 节点ID
            
        Returns:
            节点详情字典
        """
        node = self.kg.get_node(node_id)
        if not node:
            return None
            
        # 获取邻居信息
        neighbors = self.kg.get_neighbors(node_id)
        
        # 获取连接的边
        edges = []
        for neighbor_id in neighbors:
            edge = self.kg.get_edge(node_id, neighbor_id)
            if edge:
                edges.append({
                    'target': neighbor_id,
                    'type': edge.type,
                    'attributes': edge.attributes
                })
                
            # 检查反向边
            reverse_edge = self.kg.get_edge(neighbor_id, node_id)
            if reverse_edge:
                edges.append({
                    'source': neighbor_id,
                    'type': reverse_edge.type,
                    'attributes': reverse_edge.attributes
                })
                
        return {
            'id': node.id,
            'label': node.label,
            'type': node.type,
            'attributes': node.attributes,
            'position': node.position,
            'neighbors_count': len(neighbors),
            'edges': edges
        }
        
    def get_filtered_graph(self, node_types: Optional[List[str]] = None,
                          search_query: Optional[str] = None,
                          layout: str = 'spring') -> go.Figure:
        """
        获取筛选后的图谱可视化
        
        Args:
            node_types: 节点类型筛选
            search_query: 搜索查询
            layout: 布局类型
            
        Returns:
            Plotly图形对象
        """
        # 创建筛选后的图谱副本
        filtered_kg = KnowledgeGraph()
        
        # 添加筛选后的节点
        for node in self.kg.get_all_nodes():
            include_node = True
            
            # 类型筛选
            if node_types and node.type not in node_types:
                include_node = False
                
            # 搜索筛选
            if search_query and include_node:
                search_fields = self.config.get('search.search_fields', ['label', 'type'])
                case_sensitive = self.config.get('search.case_sensitive', False)
                query = search_query if case_sensitive else search_query.lower()
                
                match_found = False
                for field in search_fields:
                    field_value = getattr(node, field, None)
                    if field_value is None:
                        field_value = node.attributes.get(field, '')
                        
                    if isinstance(field_value, str):
                        search_text = field_value if case_sensitive else field_value.lower()
                        if query in search_text:
                            match_found = True
                            break
                            
                if not match_found:
                    include_node = False
                    
            if include_node:
                filtered_kg.add_node(node)
                
        # 添加相关的边
        for edge in self.kg.get_all_edges():
            if (filtered_kg.has_node(edge.source_id) and 
                filtered_kg.has_node(edge.target_id)):
                filtered_kg.add_edge(edge)
                
        # 生成可视化
        return self.visualizer.create_figure(filtered_kg, layout_type=layout)
        
    def get_node_types(self) -> List[str]:
        """
        获取所有节点类型
        
        Returns:
            节点类型列表
        """
        types = set()
        for node in self.kg.get_all_nodes():
            types.add(node.type)
        return sorted(list(types))
        
    def get_edge_types(self) -> List[str]:
        """
        获取所有边类型
        
        Returns:
            边类型列表
        """
        types = set()
        for edge in self.kg.get_all_edges():
            types.add(edge.type)
        return sorted(list(types))
        
    def handle_graph_click(self, click_data: Dict[str, Any]) -> Optional[str]:
        """
        处理图谱点击事件
        
        Args:
            click_data: 点击数据
            
        Returns:
            被点击的节点ID（如果有）
        """
        if not click_data or 'points' not in click_data:
            return None
            
        points = click_data['points']
        if not points:
            return None
            
        point = points[0]
        
        # 检查是否点击了节点
        if 'customdata' in point and point['customdata']:
            node_id = point['customdata']
            
            # 切换选择状态
            if node_id in self.selected_nodes:
                self.deselect_node(node_id)
            else:
                self.select_node(node_id)
                
            return node_id
            
        return None
        
    def export_selection(self) -> Dict[str, Any]:
        """
        导出选中的节点和边
        
        Returns:
            选中内容的字典
        """
        if not self.selected_nodes:
            return {'nodes': [], 'edges': []}
            
        # 导出选中的节点
        nodes = []
        for node_id in self.selected_nodes:
            node = self.kg.get_node(node_id)
            if node:
                nodes.append(node.to_dict())
                
        # 导出相关的边
        edges = []
        for edge in self.kg.get_all_edges():
            if (edge.source in self.selected_nodes or 
                edge.target in self.selected_nodes):
                edges.append(edge.to_dict())
                
        return {
            'nodes': nodes,
            'edges': edges,
            'metadata': {
                'selected_count': len(self.selected_nodes),
                'export_timestamp': str(pd.Timestamp.now())
            }
        }
        
    def import_selection(self, data: Dict[str, Any]) -> bool:
        """
        导入节点和边数据
        
        Args:
            data: 包含节点和边的数据字典
            
        Returns:
            是否导入成功
        """
        try:
            # 导入节点
            if 'nodes' in data:
                for node_data in data['nodes']:
                    node = Node.from_dict(node_data)
                    if not self.kg.has_node(node.id):
                        self.kg.add_node(node)
                        
            # 导入边
            if 'edges' in data:
                for edge_data in data['edges']:
                    edge = Edge.from_dict(edge_data)
                    if (self.kg.has_node(edge.source) and 
                        self.kg.has_node(edge.target) and
                        not self.kg.has_edge(edge.source, edge.target)):
                        self.kg.add_edge(edge)
                        
            return True
            
        except Exception as e:
            print(f"导入数据失败: {str(e)}")
            return False
            
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取交互统计信息
        
        Returns:
            统计信息字典
        """
        return {
            'selected_nodes_count': len(self.selected_nodes),
            'filtered_types_count': len(self.filtered_node_types),
            'total_node_types': len(self.get_node_types()),
            'total_edge_types': len(self.get_edge_types()),
            'graph_stats': self.kg.get_statistics()
        }
        
    def is_node_selected(self, node_id: str) -> bool:
        """
        检查节点是否被选中
        
        Args:
            node_id: 节点ID
            
        Returns:
            是否被选中
        """
        return node_id in self.selected_nodes