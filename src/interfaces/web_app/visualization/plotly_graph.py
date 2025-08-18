# -*- coding: utf-8 -*-
"""
Plotly知识图谱可视化组件
"""

from typing import Dict, List, Any, Optional, Tuple
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
import numpy as np
import math

from src.knowledge_management.domain.model.graph import KnowledgeGraph
from src.knowledge_management.domain.model.node import Node
from src.knowledge_management.domain.model.edge import Edge


class PlotlyGraphVisualizer:
    """
    使用Plotly创建知识图谱可视化
    """
    
    def __init__(self, width: int = 1200, height: int = 800):
        """
        初始化可视化器
        
        Args:
            width: 图表宽度
            height: 图表高度
        """
        self.width = width
        self.height = height
        self.node_colors = {
            'default': '#1f77b4',
            'person': '#ff7f0e',
            'organization': '#2ca02c',
            'location': '#d62728',
            'concept': '#9467bd',
            'event': '#8c564b'
        }
        self.edge_colors = {
            'default': '#888888',
            'related_to': '#1f77b4',
            'works_at': '#ff7f0e',
            'located_in': '#2ca02c',
            'participates_in': '#d62728'
        }
        
    def create_network_layout(self, kg: KnowledgeGraph, layout_type: str = 'spring') -> Dict[str, Tuple[float, float]]:
        """
        创建网络布局
        
        Args:
            kg: 知识图谱实例
            layout_type: 布局类型 ('spring', 'circular', 'random', 'kamada_kawai')
            
        Returns:
            节点位置字典 {node_id: (x, y)}
        """
        if not kg.nodes:
            return {}
            
        # 创建NetworkX图用于布局计算
        G = nx.Graph()
        for node_id in kg.nodes:
            G.add_node(node_id)
        for edge in kg.edges.values():
            G.add_edge(edge.source_id, edge.target_id)
            
        # 根据布局类型计算位置
        if layout_type == 'spring':
            pos = nx.spring_layout(G, k=3, iterations=50)
        elif layout_type == 'circular':
            pos = nx.circular_layout(G)
        elif layout_type == 'random':
            pos = nx.random_layout(G)
        elif layout_type == 'kamada_kawai':
            pos = nx.kamada_kawai_layout(G)
        else:
            pos = nx.spring_layout(G)
            
        # 缩放位置到合适的范围
        scale_factor = min(self.width, self.height) * 0.4
        scaled_pos = {}
        for node_id, (x, y) in pos.items():
            scaled_pos[node_id] = (x * scale_factor, y * scale_factor)
            
        return scaled_pos
        
    def create_node_trace(self, kg: KnowledgeGraph, positions: Dict[str, Tuple[float, float]]) -> go.Scatter:
        """
        创建节点轨迹
        
        Args:
            kg: 知识图谱实例
            positions: 节点位置字典
            
        Returns:
            Plotly散点图轨迹
        """
        node_x = []
        node_y = []
        node_text = []
        node_colors = []
        node_sizes = []
        node_info = []
        
        for node in kg.nodes.values():
            if node.id in positions:
                x, y = positions[node.id]
                node_x.append(x)
                node_y.append(y)
                node_text.append(node.label or node.id)
                
                # 设置节点颜色
                color = self.node_colors.get(node.type, self.node_colors['default'])
                node_colors.append(color)
                
                # 设置节点大小（基于连接数）
                connections = len(kg.get_neighbors(node.id))
                size = max(40, min(120, 40 + connections * 8))
                node_sizes.append(size)
                
                # 创建悬停信息
                info = f"<b>{node.label or node.id}</b><br>"
                info += f"类型: {node.type}<br>"
                info += f"连接数: {connections}<br>"
                if node.properties:
                    info += "属性:<br>"
                    for key, value in node.properties.items():
                        info += f"  {key}: {value}<br>"
                node_info.append(info)
                
        return go.Scatter(
            x=node_x,
            y=node_y,
            mode='markers+text',
            text=node_text,
            textposition='middle center',
            textfont=dict(size=16, color='white', family='Arial, sans-serif'),
            hoverinfo='text',
            hovertext=node_info,
            marker=dict(
                size=node_sizes,
                color=node_colors,
                line=dict(width=2, color='white'),
                opacity=0.8
            ),
            customdata=[node.id for node in kg.nodes.values() if node.id in positions],
            name='节点'
        )
        
    def create_edge_traces(self, kg: KnowledgeGraph, positions: Dict[str, Tuple[float, float]]) -> List[go.Scatter]:
        """
        创建边轨迹
        
        Args:
            kg: 知识图谱实例
            positions: 节点位置字典
            
        Returns:
            边轨迹列表
        """
        edge_traces = []
        
        # 按边类型分组
        edges_by_type = {}
        for edge in kg.edges.values():
            if edge.type not in edges_by_type:
                edges_by_type[edge.type] = []
            edges_by_type[edge.type].append(edge)
            
        # 为每种边类型创建轨迹
        for edge_type, edges in edges_by_type.items():
            edge_x = []
            edge_y = []
            
            for edge in edges:
                if edge.source_id in positions and edge.target_id in positions:
                    x0, y0 = positions[edge.source_id]
                    x1, y1 = positions[edge.target_id]
                    
                    edge_x.extend([x0, x1, None])
                    edge_y.extend([y0, y1, None])
            
            edge_trace = go.Scatter(
                x=edge_x,
                y=edge_y,
                line=dict(width=1, color=self.edge_colors.get(edge_type, self.edge_colors['default'])),
                mode='lines',
                name=edge_type,
                hoverinfo='none'
            )
            edge_traces.append(edge_trace)
            
        return edge_traces

    def create_figure(self, kg: KnowledgeGraph, layout_type: str = 'spring') -> go.Figure:
        """
        创建完整的Plotly图谱
        
        Args:
            kg: 知识图谱实例
            layout_type: 布局类型
            
        Returns:
            Plotly图形对象
        """
        # 1. 创建布局
        positions = self.create_network_layout(kg, layout_type)
        
        # 2. 创建节点轨迹
        node_trace = self.create_node_trace(kg, positions)
        
        # 3. 创建边轨迹
        edge_traces = self.create_edge_traces(kg, positions)
        
        # 4. 创建图形
        fig = go.Figure(data=edge_traces + [node_trace],
                        layout=go.Layout(
                            title=dict(text='知识图谱', font=dict(size=16)),
                            showlegend=False,
                            hovermode='closest',
                            margin=dict(b=20,l=5,r=5,t=40),
                            annotations=[ dict(
                                text="知识图谱可视化",
                                showarrow=False,
                                xref="paper", yref="paper",
                                x=0.005, y=-0.002 ) ],
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                        )
        
        fig.update_layout(
            width=self.width,
            height=self.height,
            plot_bgcolor='#f0f0f0',
            paper_bgcolor='white'
        )
        
        return fig