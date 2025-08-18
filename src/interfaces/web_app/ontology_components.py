# -*- coding: utf-8 -*-
"""
本体可视化和编辑组件
为Dash应用提供本体管理界面
"""

from dash import dcc, html, Input, Output, State, callback_context
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List, Any, Optional
import json

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.knowledge_management.domain.model.ontology import KnowledgeOntology, OntologyClass, OntologyRelation
from src.knowledge_management.application.ontology_generator import OntologyGenerator


class OntologyVisualizer:
    """本体可视化器"""
    
    def __init__(self):
        self.colors = {
            'class': '#3498db',
            'relation': '#e74c3c',
            'property': '#2ecc71',
            'hierarchy': '#9b59b6'
        }
        self.ontology_data = None
        
    def register_callbacks(self, app, ontology_generator):
        """
        注册本体相关的回调函数
        
        Args:
            app: Dash应用实例
            ontology_generator: 本体生成器实例
        """
        from dash import Input, Output, State, callback_context
        
        # 本体生成按钮回调
        @app.callback(
            Output('ontology-stats', 'children'),
            [Input('generate-ontology-btn', 'n_clicks')],
            [State('ontology-data', 'data')]
        )
        def update_ontology_stats(n_clicks, ontology_data):
            """
            更新本体统计信息
            """
            if not ontology_data:
                return "暂无本体数据"
            
            try:
                from knowledge_graph.ontology import KnowledgeOntology
                ontology = KnowledgeOntology.from_dict(ontology_data)
                stats = ontology.get_statistics()
                
                return html.Div([
                    html.P(f"类数量: {stats['classes_count']}"),
                    html.P(f"关系数量: {stats['relations_count']}"),
                    html.P(f"属性总数: {stats['total_properties']}"),
                    html.P(f"实例总数: {stats['total_instances']}")
                ])
                
            except Exception as e:
                return f"统计信息生成失败: {str(e)}"
        
        # 本体选项卡内容回调
        @app.callback(
            Output('ontology-tab-content', 'children'),
            [Input('ontology-tabs', 'value')],
            [State('ontology-data', 'data')]
        )
        def render_ontology_tab_content(active_tab, ontology_data):
            """
            渲染本体选项卡内容
            """
            if not ontology_data:
                return html.Div("请先生成本体数据", className="no-data")
            
            try:
                from knowledge_graph.ontology import KnowledgeOntology
                ontology = KnowledgeOntology.from_dict(ontology_data)
                
                if active_tab == 'classes-tab':
                    return self.create_class_hierarchy_view(ontology)
                elif active_tab == 'relations-tab':
                    return self.create_relations_network_view(ontology)
                elif active_tab == 'properties-tab':
                    return self.create_properties_analysis_view(ontology)
                elif active_tab == 'details-tab':
                    return self.create_ontology_details_view(ontology)
                    
            except Exception as e:
                return html.Div(f"加载本体数据时出错: {str(e)}", className="error")
            
            return html.Div("选项卡内容加载中...")
        
        # 本体导出回调
        @app.callback(
            Output('download-ontology', 'data'),
            [Input('export-json-btn', 'n_clicks'),
             Input('export-owl-btn', 'n_clicks'),
             Input('export-rdf-btn', 'n_clicks')],
            [State('ontology-data', 'data')],
            prevent_initial_call=True
        )
        def export_ontology(json_clicks, owl_clicks, rdf_clicks, ontology_data):
            """
            导出本体数据
            """
            ctx = callback_context
            if not ctx.triggered or not ontology_data:
                return None
            
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            
            try:
                from knowledge_graph.ontology import KnowledgeOntology
                from datetime import datetime
                
                ontology = KnowledgeOntology.from_dict(ontology_data)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                if button_id == 'export-json-btn':
                    # 导出JSON格式
                    content = json.dumps(ontology_data, indent=2, ensure_ascii=False)
                    filename = f"{ontology.name}_ontology_{timestamp}.json"
                    return dict(content=content, filename=filename, type="application/json")
                
                elif button_id == 'export-owl-btn':
                    # 导出OWL格式
                    content = ontology._generate_owl_content() if hasattr(ontology, '_generate_owl_content') else json.dumps(ontology_data, indent=2, ensure_ascii=False)
                    filename = f"{ontology.name}_ontology_{timestamp}.owl"
                    return dict(content=content, filename=filename, type="application/rdf+xml")
                
                elif button_id == 'export-rdf-btn':
                    # 导出RDF格式
                    content = ontology._generate_rdf_content() if hasattr(ontology, '_generate_rdf_content') else json.dumps(ontology_data, indent=2, ensure_ascii=False)
                    filename = f"{ontology.name}_ontology_{timestamp}.rdf"
                    return dict(content=content, filename=filename, type="application/rdf+xml")
                
            except Exception as e:
                print(f"导出本体时出错: {e}")
                return None
            
            return None
    
    def create_ontology_overview_layout(self) -> html.Div:
        """
        创建本体概览布局
        
        Returns:
            本体概览的HTML布局
        """
        return html.Div([
            # 本体操作面板
            html.Div([
                html.H3("知识本体管理", className="ontology-title"),
                html.Div([
                    html.Button("生成本体", id="generate-ontology-btn", className="btn btn-primary"),
                    html.Div([
                        html.Button("导出本体", id="export-dropdown-btn", className="btn btn-secondary dropdown-toggle", **{"data-bs-toggle": "dropdown"}),
                        html.Div([
                            html.A("导出为JSON", id="export-json-btn", className="dropdown-item", href="#"),
                            html.A("导出为OWL", id="export-owl-btn", className="dropdown-item", href="#"),
                            html.A("导出为RDF", id="export-rdf-btn", className="dropdown-item", href="#"),
                        ], className="dropdown-menu")
                    ], className="dropdown d-inline-block"),
                    html.Button("清空本体", id="clear-ontology-btn", className="btn btn-warning"),
                    dcc.Upload(
                        id="upload-ontology",
                        children=html.Button("导入本体", className="btn btn-success"),
                        multiple=False
                    )
                ], className="ontology-controls")
            ], className="ontology-header"),
            
            # 本体统计信息
            html.Div([
                html.H4("本体统计"),
                html.Div(id="ontology-stats", className="ontology-stats")
            ], className="ontology-stats-panel"),
            
            # 下载组件
            dcc.Download(id="download-ontology"),
            
            # 本体可视化选项卡
            dcc.Tabs(id="ontology-tabs", value="classes-tab", children=[
                dcc.Tab(label="类层次结构", value="classes-tab"),
                dcc.Tab(label="关系网络", value="relations-tab"),
                dcc.Tab(label="属性分析", value="properties-tab"),
                dcc.Tab(label="本体详情", value="details-tab")
            ]),
            
            # 选项卡内容
            html.Div(id="ontology-tab-content"),
            
            # 隐藏的存储组件
            dcc.Store(id="ontology-data", data=None),
            dcc.Download(id="download-ontology")
        ], className="ontology-container")
    
    def create_class_hierarchy_view(self, ontology: KnowledgeOntology) -> html.Div:
        """
        创建类层次结构视图
        
        Args:
            ontology: 知识本体
            
        Returns:
            类层次结构的HTML布局
        """
        if not ontology or not ontology.classes:
            return html.Div("暂无本体数据", className="no-data")
        
        # 创建层次结构图
        fig = self._create_class_hierarchy_graph(ontology)
        
        # 创建类详情表格
        classes_table = self._create_classes_table(ontology)
        
        return html.Div([
            html.Div([
                dcc.Graph(figure=fig, id="class-hierarchy-graph")
            ], className="hierarchy-graph"),
            html.Div([
                html.H5("类详情"),
                classes_table
            ], className="classes-details")
        ], className="class-hierarchy-view")
    
    def create_relations_network_view(self, ontology: KnowledgeOntology) -> html.Div:
        """
        创建关系网络视图
        
        Args:
            ontology: 知识本体
            
        Returns:
            关系网络的HTML布局
        """
        if not ontology or not ontology.relations:
            return html.Div("暂无关系数据", className="no-data")
        
        # 创建关系网络图
        fig = self._create_relations_network_graph(ontology)
        
        # 创建关系详情表格
        relations_table = self._create_relations_table(ontology)
        
        return html.Div([
            html.Div([
                dcc.Graph(figure=fig, id="relations-network-graph")
            ], className="relations-graph"),
            html.Div([
                html.H5("关系详情"),
                relations_table
            ], className="relations-details")
        ], className="relations-network-view")
    
    def create_properties_analysis_view(self, ontology: KnowledgeOntology) -> html.Div:
        """
        创建属性分析视图
        
        Args:
            ontology: 知识本体
            
        Returns:
            属性分析的HTML布局
        """
        if not ontology:
            return html.Div("暂无本体数据", className="no-data")
        
        # 创建属性统计图表
        property_stats_fig = self._create_property_statistics_chart(ontology)
        data_types_fig = self._create_data_types_chart(ontology)
        
        return html.Div([
            html.Div([
                html.H5("属性统计"),
                dcc.Graph(figure=property_stats_fig)
            ], className="property-stats"),
            html.Div([
                html.H5("数据类型分布"),
                dcc.Graph(figure=data_types_fig)
            ], className="data-types")
        ], className="properties-analysis-view")
    
    def create_ontology_details_view(self, ontology: KnowledgeOntology) -> html.Div:
        """
        创建本体详情视图
        
        Args:
            ontology: 知识本体
            
        Returns:
            本体详情的HTML布局
        """
        if not ontology:
            return html.Div("暂无本体数据", className="no-data")
        
        stats = ontology.get_statistics()
        
        return html.Div([
            html.Div([
                html.H5("基本信息"),
                html.P(f"名称: {ontology.name}"),
                html.P(f"版本: {ontology.version}"),
                html.P(f"描述: {ontology.description or '无'}"),
                html.P(f"命名空间: {ontology.namespace or '无'}"),
                html.P(f"创建时间: {stats['created_at']}"),
                html.P(f"更新时间: {stats['updated_at']}")
            ], className="basic-info"),
            
            html.Div([
                html.H5("统计信息"),
                html.P(f"类数量: {stats['classes_count']}"),
                html.P(f"关系数量: {stats['relations_count']}"),
                html.P(f"属性总数: {stats['total_properties']}"),
                html.P(f"实例总数: {stats['total_instances']}"),
                html.P(f"关系实例总数: {stats['total_relation_instances']}")
            ], className="statistics-info"),
            
            html.Div([
                html.H5("元数据"),
                html.Pre(json.dumps(ontology.metadata, indent=2, ensure_ascii=False))
            ], className="metadata-info")
        ], className="ontology-details-view")
    
    def _create_class_hierarchy_graph(self, ontology: KnowledgeOntology) -> go.Figure:
        """
        创建类层次结构图
        
        Args:
            ontology: 知识本体
            
        Returns:
            Plotly图形对象
        """
        # 构建层次结构数据
        nodes = []
        edges = []
        
        # 添加节点
        for class_name, ontology_class in ontology.classes.items():
            nodes.append({
                'id': class_name,
                'label': class_name,
                'size': ontology_class.instances_count,
                'color': self.colors['class']
            })
        
        # 添加层次关系边
        for class_name, ontology_class in ontology.classes.items():
            for parent_class in ontology_class.parent_classes:
                if parent_class in ontology.classes:
                    edges.append({
                        'source': class_name,
                        'target': parent_class,
                        'type': 'is_a'
                    })
        
        # 使用网络布局
        return self._create_network_graph(nodes, edges, "类层次结构")
    
    def _create_relations_network_graph(self, ontology: KnowledgeOntology) -> go.Figure:
        """
        创建关系网络图
        
        Args:
            ontology: 知识本体
            
        Returns:
            Plotly图形对象
        """
        nodes = []
        edges = []
        
        # 添加类节点
        for class_name in ontology.classes.keys():
            nodes.append({
                'id': class_name,
                'label': class_name,
                'type': 'class',
                'color': self.colors['class']
            })
        
        # 添加关系边
        for relation_name, relation in ontology.relations.items():
            for domain_class in relation.domain_classes:
                for range_class in relation.range_classes:
                    if domain_class in ontology.classes and range_class in ontology.classes:
                        edges.append({
                            'source': domain_class,
                            'target': range_class,
                            'label': relation_name,
                            'type': relation_name
                        })
        
        return self._create_network_graph(nodes, edges, "关系网络")
    
    def _create_network_graph(self, nodes: List[Dict], edges: List[Dict], title: str) -> go.Figure:
        """
        创建网络图
        
        Args:
            nodes: 节点列表
            edges: 边列表
            title: 图标题
            
        Returns:
            Plotly图形对象
        """
        if not nodes:
            fig = go.Figure()
            fig.add_annotation(text="暂无数据", x=0.5, y=0.5, showarrow=False)
            return fig
        
        # 简单的圆形布局
        import math
        n = len(nodes)
        positions = {}
        for i, node in enumerate(nodes):
            angle = 2 * math.pi * i / n
            positions[node['id']] = {
                'x': math.cos(angle),
                'y': math.sin(angle)
            }
        
        # 创建边的轨迹
        edge_trace = go.Scatter(
            x=[], y=[],
            line=dict(width=2, color='#888'),
            hoverinfo='none',
            mode='lines'
        )
        
        for edge in edges:
            if edge['source'] in positions and edge['target'] in positions:
                x0, y0 = positions[edge['source']]['x'], positions[edge['source']]['y']
                x1, y1 = positions[edge['target']]['x'], positions[edge['target']]['y']
                edge_trace['x'] += (x0, x1, None)
                edge_trace['y'] += (y0, y1, None)
        
        # 创建节点的轨迹
        node_trace = go.Scatter(
            x=[positions[node['id']]['x'] for node in nodes],
            y=[positions[node['id']]['y'] for node in nodes],
            mode='markers+text',
            hoverinfo='text',
            text=[node['label'] for node in nodes],
            textposition="middle center",
            marker=dict(
                size=[max(10, min(30, node.get('size', 10))) for node in nodes],
                color=[node.get('color', self.colors['class']) for node in nodes],
                line=dict(width=2, color='white')
            )
        )
        
        # 设置悬停信息
        node_info = []
        for node in nodes:
            info = f"名称: {node['label']}<br>"
            if 'size' in node:
                info += f"实例数: {node['size']}<br>"
            if 'type' in node:
                info += f"类型: {node['type']}"
            node_info.append(info)
        node_trace.hovertext = node_info
        
        # 创建图形
        fig = go.Figure(data=[edge_trace, node_trace],
                       layout=go.Layout(
                           title=title,
                           titlefont_size=16,
                           showlegend=False,
                           hovermode='closest',
                           margin=dict(b=20,l=5,r=5,t=40),
                           annotations=[ dict(
                               text="拖拽节点可调整位置",
                               showarrow=False,
                               xref="paper", yref="paper",
                               x=0.005, y=-0.002,
                               xanchor='left', yanchor='bottom',
                               font=dict(color="#888", size=12)
                           )],
                           xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                       ))
        
        return fig
    
    def _create_classes_table(self, ontology: KnowledgeOntology) -> html.Table:
        """
        创建类详情表格
        
        Args:
            ontology: 知识本体
            
        Returns:
            HTML表格
        """
        headers = ["类名", "实例数", "属性数", "父类", "描述"]
        rows = []
        
        for class_name, ontology_class in ontology.classes.items():
            rows.append([
                class_name,
                str(ontology_class.instances_count),
                str(len(ontology_class.properties)),
                ", ".join(ontology_class.parent_classes) or "无",
                ontology_class.description or "无"
            ])
        
        return html.Table([
            html.Thead([html.Tr([html.Th(header) for header in headers])]),
            html.Tbody([html.Tr([html.Td(cell) for cell in row]) for row in rows])
        ], className="ontology-table")
    
    def _create_relations_table(self, ontology: KnowledgeOntology) -> html.Table:
        """
        创建关系详情表格
        
        Args:
            ontology: 知识本体
            
        Returns:
            HTML表格
        """
        headers = ["关系名", "实例数", "主体类", "客体类", "属性", "描述"]
        rows = []
        
        for relation_name, relation in ontology.relations.items():
            rows.append([
                relation_name,
                str(relation.instances_count),
                ", ".join(relation.domain_classes) or "无",
                ", ".join(relation.range_classes) or "无",
                f"对称: {'是' if relation.is_symmetric else '否'}, "
                f"传递: {'是' if relation.is_transitive else '否'}, "
                f"函数: {'是' if relation.is_functional else '否'}",
                relation.description or "无"
            ])
        
        return html.Table([
            html.Thead([html.Tr([html.Th(header) for header in headers])]),
            html.Tbody([html.Tr([html.Td(cell) for cell in row]) for row in rows])
        ], className="ontology-table")
    
    def _create_property_statistics_chart(self, ontology: KnowledgeOntology) -> go.Figure:
        """
        创建属性统计图表
        
        Args:
            ontology: 知识本体
            
        Returns:
            Plotly图形对象
        """
        # 统计每个类的属性数量
        class_props = []
        for class_name, ontology_class in ontology.classes.items():
            class_props.append({
                'class': class_name,
                'properties': len(ontology_class.properties),
                'instances': ontology_class.instances_count
            })
        
        if not class_props:
            fig = go.Figure()
            fig.add_annotation(text="暂无属性数据", x=0.5, y=0.5, showarrow=False)
            return fig
        
        df = pd.DataFrame(class_props)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df['class'],
            y=df['properties'],
            name='属性数量',
            marker_color=self.colors['property']
        ))
        
        fig.update_layout(
            title="各类属性数量统计",
            xaxis_title="类名",
            yaxis_title="属性数量",
            showlegend=False
        )
        
        return fig
    
    def _create_data_types_chart(self, ontology: KnowledgeOntology) -> go.Figure:
        """
        创建数据类型分布图表
        
        Args:
            ontology: 知识本体
            
        Returns:
            Plotly图形对象
        """
        # 统计数据类型分布
        type_counts = {}
        
        for ontology_class in ontology.classes.values():
            for prop in ontology_class.properties.values():
                type_name = prop.data_type.value
                type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        for relation in ontology.relations.values():
            for prop in relation.properties.values():
                type_name = prop.data_type.value
                type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        if not type_counts:
            fig = go.Figure()
            fig.add_annotation(text="暂无数据类型信息", x=0.5, y=0.5, showarrow=False)
            return fig
        
        fig = go.Figure(data=[go.Pie(
            labels=list(type_counts.keys()),
            values=list(type_counts.values()),
            hole=0.3
        )])
        
        fig.update_layout(
            title="数据类型分布",
            showlegend=True
        )
        
        return fig