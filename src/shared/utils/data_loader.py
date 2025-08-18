# -*- coding: utf-8 -*-
"""
数据加载器模块
"""

import json
import csv
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
import os
from pathlib import Path

from src.knowledge_management.domain.model.graph import KnowledgeGraph
from src.knowledge_management.domain.model.node import Node
from src.knowledge_management.domain.model.edge import Edge


class DataLoader:
    """
    数据加载器，支持多种格式的数据导入导出
    """
    
    def __init__(self):
        """
        初始化数据加载器
        """
        self.supported_formats = ['json', 'csv', 'excel']
        
    def load_from_json(self, filepath: str) -> KnowledgeGraph:
        """
        从JSON文件加载知识图谱
        
        Args:
            filepath: JSON文件路径
            
        Returns:
            知识图谱实例
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return KnowledgeGraph.from_dict(data)
        except Exception as e:
            raise ValueError(f"加载JSON文件失败: {str(e)}")
            
    def save_to_json(self, kg: KnowledgeGraph, filepath: str) -> None:
        """
        将知识图谱保存为JSON文件
        
        Args:
            kg: 知识图谱实例
            filepath: 保存路径
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(kg.to_dict(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise ValueError(f"保存JSON文件失败: {str(e)}")
            
    def load_from_csv(self, nodes_file: str, edges_file: Optional[str] = None) -> KnowledgeGraph:
        """
        从CSV文件加载知识图谱
        
        Args:
            nodes_file: 节点CSV文件路径
            edges_file: 边CSV文件路径（可选）
            
        Returns:
            知识图谱实例
        """
        kg = KnowledgeGraph()
        
        try:
            # 加载节点
            nodes_df = pd.read_csv(nodes_file)
            required_node_columns = ['id', 'label']
            
            if not all(col in nodes_df.columns for col in required_node_columns):
                raise ValueError(f"节点CSV文件必须包含列: {required_node_columns}")
                
            for _, row in nodes_df.iterrows():
                properties = {}
                for col in nodes_df.columns:
                    if col not in ['id', 'label', 'type']:
                        if pd.notna(row[col]):
                            properties[col] = row[col]
                            
                node = Node(
                    node_id=str(row['id']),
                    label=str(row['label']),
                    node_type=str(row.get('type', 'default')),
                    properties=properties
                )
                kg.add_node(node)
                
            # 加载边（如果提供了边文件）
            if edges_file and os.path.exists(edges_file):
                edges_df = pd.read_csv(edges_file)
                required_edge_columns = ['source_id', 'target_id']
                
                if not all(col in edges_df.columns for col in required_edge_columns):
                    raise ValueError(f"边CSV文件必须包含列: {required_edge_columns}")
                    
                for _, row in edges_df.iterrows():
                    properties = {}
                    for col in edges_df.columns:
                        if col not in ['source_id', 'target_id', 'label', 'type', 'weight']:
                            if pd.notna(row[col]):
                                properties[col] = row[col]
                                
                    edge = Edge(
                        source_id=str(row['source_id']),
                        target_id=str(row['target_id']),
                        label=str(row.get('label', '')),
                        edge_type=str(row.get('type', 'default')),
                        properties=properties,
                        weight=float(row.get('weight', 1.0))
                    )
                    
                    # 只有当源节点和目标节点都存在时才添加边
                    if (edge.source_id in kg.nodes and edge.target_id in kg.nodes):
                        kg.add_edge(edge)
                        
            return kg
            
        except Exception as e:
            raise ValueError(f"加载CSV文件失败: {str(e)}")
            
    def save_to_csv(self, kg: KnowledgeGraph, nodes_file: str, edges_file: str) -> None:
        """
        将知识图谱保存为CSV文件
        
        Args:
            kg: 知识图谱实例
            nodes_file: 节点CSV文件路径
            edges_file: 边CSV文件路径
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(nodes_file), exist_ok=True)
            os.makedirs(os.path.dirname(edges_file), exist_ok=True)
            
            # 保存节点
            nodes_data = []
            for node in kg.nodes.values():
                node_dict = {
                    'id': node.id,
                    'label': node.label,
                    'type': node.type
                }
                node_dict.update(node.properties)
                nodes_data.append(node_dict)
                
            nodes_df = pd.DataFrame(nodes_data)
            nodes_df.to_csv(nodes_file, index=False, encoding='utf-8')
            
            # 保存边
            edges_data = []
            for edge in kg.edges.values():
                edge_dict = {
                    'source_id': edge.source_id,
                    'target_id': edge.target_id,
                    'label': edge.label,
                    'type': edge.type,
                    'weight': edge.weight
                }
                edge_dict.update(edge.properties)
                edges_data.append(edge_dict)
                
            edges_df = pd.DataFrame(edges_data)
            edges_df.to_csv(edges_file, index=False, encoding='utf-8')
            
        except Exception as e:
            raise ValueError(f"保存CSV文件失败: {str(e)}")
            
    def load_from_excel(self, filepath: str, nodes_sheet: str = 'nodes', edges_sheet: str = 'edges') -> KnowledgeGraph:
        """
        从Excel文件加载知识图谱
        
        Args:
            filepath: Excel文件路径
            nodes_sheet: 节点工作表名称
            edges_sheet: 边工作表名称
            
        Returns:
            知识图谱实例
        """
        kg = KnowledgeGraph()
        
        try:
            # 读取Excel文件
            excel_file = pd.ExcelFile(filepath)
            
            # 加载节点
            if nodes_sheet in excel_file.sheet_names:
                nodes_df = pd.read_excel(filepath, sheet_name=nodes_sheet)
                required_node_columns = ['id', 'label']
                
                if not all(col in nodes_df.columns for col in required_node_columns):
                    raise ValueError(f"节点工作表必须包含列: {required_node_columns}")
                    
                for _, row in nodes_df.iterrows():
                    properties = {}
                    for col in nodes_df.columns:
                        if col not in ['id', 'label', 'type']:
                            if pd.notna(row[col]):
                                properties[col] = row[col]
                                
                    node = Node(
                        node_id=str(row['id']),
                        label=str(row['label']),
                        node_type=str(row.get('type', 'default')),
                        properties=properties
                    )
                    kg.add_node(node)
                    
            # 加载边
            if edges_sheet in excel_file.sheet_names:
                edges_df = pd.read_excel(filepath, sheet_name=edges_sheet)
                required_edge_columns = ['source_id', 'target_id']
                
                if not all(col in edges_df.columns for col in required_edge_columns):
                    raise ValueError(f"边工作表必须包含列: {required_edge_columns}")
                    
                for _, row in edges_df.iterrows():
                    properties = {}
                    for col in edges_df.columns:
                        if col not in ['source_id', 'target_id', 'label', 'type', 'weight']:
                            if pd.notna(row[col]):
                                properties[col] = row[col]
                                
                    edge = Edge(
                        source_id=str(row['source_id']),
                        target_id=str(row['target_id']),
                        label=str(row.get('label', '')),
                        edge_type=str(row.get('type', 'default')),
                        properties=properties,
                        weight=float(row.get('weight', 1.0))
                    )
                    
                    # 只有当源节点和目标节点都存在时才添加边
                    if (edge.source_id in kg.nodes and edge.target_id in kg.nodes):
                        kg.add_edge(edge)
                        
            return kg
            
        except Exception as e:
            raise ValueError(f"加载Excel文件失败: {str(e)}")
            
    def save_to_excel(self, kg: KnowledgeGraph, filepath: str, nodes_sheet: str = 'nodes', edges_sheet: str = 'edges') -> None:
        """
        将知识图谱保存为Excel文件
        
        Args:
            kg: 知识图谱实例
            filepath: Excel文件路径
            nodes_sheet: 节点工作表名称
            edges_sheet: 边工作表名称
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # 保存节点
                nodes_data = []
                for node in kg.nodes.values():
                    node_dict = {
                        'id': node.id,
                        'label': node.label,
                        'type': node.type
                    }
                    node_dict.update(node.properties)
                    nodes_data.append(node_dict)
                    
                nodes_df = pd.DataFrame(nodes_data)
                nodes_df.to_excel(writer, sheet_name=nodes_sheet, index=False)
                
                # 保存边
                edges_data = []
                for edge in kg.edges.values():
                    edge_dict = {
                        'source_id': edge.source_id,
                        'target_id': edge.target_id,
                        'label': edge.label,
                        'type': edge.type,
                        'weight': edge.weight
                    }
                    edge_dict.update(edge.properties)
                    edges_data.append(edge_dict)
                    
                edges_df = pd.DataFrame(edges_data)
                edges_df.to_excel(writer, sheet_name=edges_sheet, index=False)
                
        except Exception as e:
            raise ValueError(f"保存Excel文件失败: {str(e)}")
            
    def create_sample_data(self) -> KnowledgeGraph:
        """
        创建示例数据
        
        Returns:
            包含示例数据的知识图谱
        """
        kg = KnowledgeGraph()
        
        # 示例节点数据
        sample_nodes = [
            {'id': 'ai', 'label': '人工智能', 'type': 'concept', 'properties': {'field': '计算机科学', 'importance': 'high'}},
            {'id': 'ml', 'label': '机器学习', 'type': 'concept', 'properties': {'field': '计算机科学', 'parent': 'ai'}},
            {'id': 'dl', 'label': '深度学习', 'type': 'concept', 'properties': {'field': '计算机科学', 'parent': 'ml'}},
            {'id': 'python', 'label': 'Python', 'type': 'technology', 'properties': {'type': '编程语言', 'year': 1991}},
            {'id': 'tensorflow', 'label': 'TensorFlow', 'type': 'technology', 'properties': {'type': '框架', 'company': 'Google'}},
            {'id': 'pytorch', 'label': 'PyTorch', 'type': 'technology', 'properties': {'type': '框架', 'company': 'Facebook'}},
            {'id': 'google', 'label': '谷歌', 'type': 'organization', 'properties': {'industry': '科技', 'founded': 1998}},
            {'id': 'facebook', 'label': 'Facebook', 'type': 'organization', 'properties': {'industry': '社交媒体', 'founded': 2004}}
        ]
        
        # 添加节点
        for node_data in sample_nodes:
            node = Node(
                node_id=node_data['id'],
                label=node_data['label'],
                node_type=node_data['type'],
                properties=node_data['properties']
            )
            kg.add_node(node)
            
        # 示例边数据
        sample_edges = [
            {'source_id': 'ml', 'target_id': 'ai', 'label': '属于', 'type': 'is_part_of'},
            {'source_id': 'dl', 'target_id': 'ml', 'label': '属于', 'type': 'is_part_of'},
            {'source_id': 'tensorflow', 'target_id': 'dl', 'label': '用于', 'type': 'used_for'},
            {'source_id': 'pytorch', 'target_id': 'dl', 'label': '用于', 'type': 'used_for'},
            {'source_id': 'python', 'target_id': 'ml', 'label': '用于', 'type': 'used_for'},
            {'source_id': 'google', 'target_id': 'tensorflow', 'label': '开发', 'type': 'develops'},
            {'source_id': 'facebook', 'target_id': 'pytorch', 'label': '开发', 'type': 'develops'}
        ]
        
        # 添加边
        for edge_data in sample_edges:
            edge = Edge(
                source_id=edge_data['source_id'],
                target_id=edge_data['target_id'],
                label=edge_data['label'],
                edge_type=edge_data['type']
            )
            kg.add_edge(edge)
            
        return kg
        
    def validate_data_format(self, filepath: str) -> Tuple[bool, str]:
        """
        验证数据文件格式
        
        Args:
            filepath: 文件路径
            
        Returns:
            (是否有效, 错误信息)
        """
        if not os.path.exists(filepath):
            return False, "文件不存在"
            
        file_ext = Path(filepath).suffix.lower()
        
        if file_ext == '.json':
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if 'nodes' not in data or 'edges' not in data:
                    return False, "JSON文件必须包含'nodes'和'edges'字段"
                return True, ""
            except json.JSONDecodeError:
                return False, "无效的JSON格式"
                
        elif file_ext == '.csv':
            try:
                df = pd.read_csv(filepath)
                if 'id' not in df.columns or 'label' not in df.columns:
                    return False, "CSV文件必须包含'id'和'label'列"
                return True, ""
            except Exception as e:
                return False, f"CSV文件读取错误: {str(e)}"
                
        elif file_ext in ['.xlsx', '.xls']:
            try:
                excel_file = pd.ExcelFile(filepath)
                if 'nodes' not in excel_file.sheet_names:
                    return False, "Excel文件必须包含'nodes'工作表"
                return True, ""
            except Exception as e:
                return False, f"Excel文件读取错误: {str(e)}"
                
        else:
            return False, f"不支持的文件格式: {file_ext}"