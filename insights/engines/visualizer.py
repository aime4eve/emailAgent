# -*- coding: utf-8 -*-
"""
可视化引擎模块

提供图谱可视化、数据可视化、报表生成等功能。
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
import base64
from io import BytesIO

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    import networkx as nx
    import matplotlib.pyplot as plt
    import seaborn as sns
    import pandas as pd
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False
    
from ..core.database_manager import DatabaseManager
from ..core.exceptions import InsightsException, BusinessLogicError
from ..utils.singleton import Singleton
from insights_config import InsightsConfig

@dataclass
class VisualizationResult:
    """可视化结果数据类"""
    visualization_id: str
    title: str
    description: str
    chart_type: str
    html_content: str
    json_data: Dict[str, Any]
    metadata: Dict[str, Any]
    created_time: datetime
    
@dataclass
class GraphVisualization:
    """图谱可视化数据类"""
    graph_id: str
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    layout: str
    html_content: str
    json_data: Dict[str, Any]
    metadata: Dict[str, Any]
    
@dataclass
class DashboardConfig:
    """仪表板配置数据类"""
    dashboard_id: str
    title: str
    layout: str  # 'grid', 'tabs', 'single'
    widgets: List[Dict[str, Any]]
    refresh_interval: int  # seconds
    filters: Dict[str, Any]
    
class Visualizer(metaclass=Singleton):
    """可视化引擎类
    
    提供图谱可视化、数据可视化、报表生成等功能。
    """
    
    def __init__(self):
        """初始化可视化引擎"""
        self.logger = logging.getLogger(__name__)
        self.config = InsightsConfig()
        self.db_manager = None
        self.initialized = False
        
        # 检查可视化库是否可用
        if not VISUALIZATION_AVAILABLE:
            self.logger.warning("可视化库未安装，部分功能将不可用")
            
        # 默认颜色配置
        self.color_schemes = {
            'default': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                       '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'],
            'business': ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#592E83'],
            'risk': ['#28a745', '#ffc107', '#fd7e14', '#dc3545', '#6f42c1'],
            'network': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
        }
        
        # 图表模板
        self.chart_templates = {
            'line': {'type': 'scatter', 'mode': 'lines+markers'},
            'bar': {'type': 'bar'},
            'pie': {'type': 'pie'},
            'scatter': {'type': 'scatter', 'mode': 'markers'},
            'heatmap': {'type': 'heatmap'},
            'network': {'type': 'network'}
        }
        
    def initialize(self) -> bool:
        """初始化可视化引擎
        
        Returns:
            是否初始化成功
        """
        try:
            self.db_manager = DatabaseManager()
            self.initialized = True
            self.logger.info("可视化引擎初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"可视化引擎初始化失败: {e}")
            return False
            
    def create_graph_visualization(self, filter_params: Dict[str, Any] = None, 
                                 layout: str = 'force') -> GraphVisualization:
        """创建图谱可视化
        
        Args:
            filter_params: 过滤参数
            layout: 布局类型 ('force', 'circular', 'hierarchical')
            
        Returns:
            图谱可视化结果
        """
        if not self.initialized:
            raise BusinessLogicError("可视化引擎未初始化")
            
        try:
            # 查询图谱数据
            nodes, edges = self._query_graph_data(filter_params)
            
            if not nodes:
                raise BusinessLogicError("没有找到图谱数据")
                
            # 创建网络图
            if VISUALIZATION_AVAILABLE:
                html_content, json_data = self._create_network_plot(
                    nodes, edges, layout
                )
            else:
                html_content, json_data = self._create_simple_network_html(
                    nodes, edges
                )
                
            # 生成元数据
            metadata = {
                'node_count': len(nodes),
                'edge_count': len(edges),
                'layout': layout,
                'filter_params': filter_params,
                'created_time': datetime.now().isoformat()
            }
            
            visualization = GraphVisualization(
                graph_id=f"graph_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                nodes=nodes,
                edges=edges,
                layout=layout,
                html_content=html_content,
                json_data=json_data,
                metadata=metadata
            )
            
            self.logger.info(f"创建图谱可视化成功，包含{len(nodes)}个节点，{len(edges)}条边")
            return visualization
            
        except Exception as e:
            self.logger.error(f"图谱可视化创建失败: {e}")
            raise BusinessLogicError(f"图谱可视化创建失败: {e}")
            
    def create_business_chart(self, chart_type: str, data: Dict[str, Any], 
                            title: str = "", **kwargs) -> VisualizationResult:
        """创建业务图表
        
        Args:
            chart_type: 图表类型 ('line', 'bar', 'pie', 'scatter', 'heatmap')
            data: 图表数据
            title: 图表标题
            **kwargs: 其他参数
            
        Returns:
            可视化结果
        """
        if not self.initialized:
            raise BusinessLogicError("可视化引擎未初始化")
            
        try:
            if VISUALIZATION_AVAILABLE:
                html_content, json_data = self._create_plotly_chart(
                    chart_type, data, title, **kwargs
                )
            else:
                html_content, json_data = self._create_simple_chart_html(
                    chart_type, data, title
                )
                
            metadata = {
                'chart_type': chart_type,
                'data_points': len(data.get('x', [])) if 'x' in data else 0,
                'created_time': datetime.now().isoformat(),
                'parameters': kwargs
            }
            
            result = VisualizationResult(
                visualization_id=f"{chart_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                title=title or f"{chart_type.title()} Chart",
                description=f"{chart_type}类型的业务图表",
                chart_type=chart_type,
                html_content=html_content,
                json_data=json_data,
                metadata=metadata,
                created_time=datetime.now()
            )
            
            self.logger.info(f"创建{chart_type}图表成功")
            return result
            
        except Exception as e:
            self.logger.error(f"业务图表创建失败: {e}")
            raise BusinessLogicError(f"业务图表创建失败: {e}")
            
    def create_risk_dashboard(self, risk_data: Dict[str, Any]) -> VisualizationResult:
        """创建风险仪表板
        
        Args:
            risk_data: 风险数据
            
        Returns:
            仪表板可视化结果
        """
        if not self.initialized:
            raise BusinessLogicError("可视化引擎未初始化")
            
        try:
            if VISUALIZATION_AVAILABLE:
                html_content, json_data = self._create_risk_dashboard_plotly(risk_data)
            else:
                html_content, json_data = self._create_simple_dashboard_html(risk_data)
                
            metadata = {
                'dashboard_type': 'risk',
                'risk_categories': list(risk_data.keys()),
                'created_time': datetime.now().isoformat()
            }
            
            result = VisualizationResult(
                visualization_id=f"risk_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                title="风险预警仪表板",
                description="综合风险监控和预警仪表板",
                chart_type="dashboard",
                html_content=html_content,
                json_data=json_data,
                metadata=metadata,
                created_time=datetime.now()
            )
            
            self.logger.info("创建风险仪表板成功")
            return result
            
        except Exception as e:
            self.logger.error(f"风险仪表板创建失败: {e}")
            raise BusinessLogicError(f"风险仪表板创建失败: {e}")
            
    def create_customer_insights_chart(self, insights_data: Dict[str, Any]) -> VisualizationResult:
        """创建客户洞察图表
        
        Args:
            insights_data: 客户洞察数据
            
        Returns:
            客户洞察可视化结果
        """
        if not self.initialized:
            raise BusinessLogicError("可视化引擎未初始化")
            
        try:
            if VISUALIZATION_AVAILABLE:
                html_content, json_data = self._create_customer_insights_plotly(insights_data)
            else:
                html_content, json_data = self._create_simple_insights_html(insights_data)
                
            metadata = {
                'insights_type': 'customer',
                'data_categories': list(insights_data.keys()),
                'created_time': datetime.now().isoformat()
            }
            
            result = VisualizationResult(
                visualization_id=f"customer_insights_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                title="客户洞察分析",
                description="客户行为和需求洞察可视化",
                chart_type="insights",
                html_content=html_content,
                json_data=json_data,
                metadata=metadata,
                created_time=datetime.now()
            )
            
            self.logger.info("创建客户洞察图表成功")
            return result
            
        except Exception as e:
            self.logger.error(f"客户洞察图表创建失败: {e}")
            raise BusinessLogicError(f"客户洞察图表创建失败: {e}")
            
    def create_market_trends_chart(self, trends_data: Dict[str, Any]) -> VisualizationResult:
        """创建市场趋势图表
        
        Args:
            trends_data: 市场趋势数据
            
        Returns:
            市场趋势可视化结果
        """
        if not self.initialized:
            raise BusinessLogicError("可视化引擎未初始化")
            
        try:
            if VISUALIZATION_AVAILABLE:
                html_content, json_data = self._create_market_trends_plotly(trends_data)
            else:
                html_content, json_data = self._create_simple_trends_html(trends_data)
                
            metadata = {
                'trends_type': 'market',
                'trend_categories': list(trends_data.keys()),
                'created_time': datetime.now().isoformat()
            }
            
            result = VisualizationResult(
                visualization_id=f"market_trends_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                title="市场趋势分析",
                description="市场动态和趋势可视化",
                chart_type="trends",
                html_content=html_content,
                json_data=json_data,
                metadata=metadata,
                created_time=datetime.now()
            )
            
            self.logger.info("创建市场趋势图表成功")
            return result
            
        except Exception as e:
            self.logger.error(f"市场趋势图表创建失败: {e}")
            raise BusinessLogicError(f"市场趋势图表创建失败: {e}")
            
    def generate_report(self, report_type: str, data: Dict[str, Any], 
                       template: str = 'default') -> str:
        """生成分析报告
        
        Args:
            report_type: 报告类型 ('customer', 'market', 'risk', 'comprehensive')
            data: 报告数据
            template: 报告模板
            
        Returns:
            HTML格式的报告内容
        """
        if not self.initialized:
            raise BusinessLogicError("可视化引擎未初始化")
            
        try:
            report_generators = {
                'customer': self._generate_customer_report,
                'market': self._generate_market_report,
                'risk': self._generate_risk_report,
                'comprehensive': self._generate_comprehensive_report
            }
            
            generator = report_generators.get(report_type)
            if not generator:
                raise BusinessLogicError(f"不支持的报告类型: {report_type}")
                
            report_html = generator(data, template)
            
            self.logger.info(f"生成{report_type}报告成功")
            return report_html
            
        except Exception as e:
            self.logger.error(f"报告生成失败: {e}")
            raise BusinessLogicError(f"报告生成失败: {e}")
            
    def _query_graph_data(self, filter_params: Dict[str, Any] = None) -> Tuple[List[Dict], List[Dict]]:
        """查询图谱数据
        
        Args:
            filter_params: 过滤参数
            
        Returns:
            节点和边的数据
        """
        try:
            # 构建查询条件
            where_clause = ""
            if filter_params:
                conditions = []
                if 'node_types' in filter_params:
                    node_types = "', '".join(filter_params['node_types'])
                    conditions.append(f"n.type IN ['{node_types}']")
                if 'limit' in filter_params:
                    limit = int(filter_params['limit'])
                else:
                    limit = 100
                    
                if conditions:
                    where_clause = "WHERE " + " AND ".join(conditions)
                    
            # 查询节点
            nodes_query = f"""
            MATCH (n)
            {where_clause}
            RETURN n.id as id, n.name as name, n.type as type, 
                   n.properties as properties
            LIMIT {limit if 'limit' in locals() else 100}
            """
            
            nodes_result = self.db_manager.execute_cypher_query(nodes_query)
            
            # 查询边
            edges_query = f"""
            MATCH (n1)-[r]->(n2)
            {where_clause.replace('n.', 'n1.') if where_clause else ''}
            RETURN n1.id as source, n2.id as target, type(r) as relation_type,
                   r.properties as properties
            LIMIT {limit if 'limit' in locals() else 100}
            """
            
            edges_result = self.db_manager.execute_cypher_query(edges_query)
            
            # 转换数据格式
            nodes = [{
                'id': record['id'],
                'name': record['name'] or record['id'],
                'type': record['type'] or 'unknown',
                'properties': record['properties'] or {}
            } for record in nodes_result]
            
            edges = [{
                'source': record['source'],
                'target': record['target'],
                'relation_type': record['relation_type'],
                'properties': record['properties'] or {}
            } for record in edges_result]
            
            return nodes, edges
            
        except Exception as e:
            self.logger.error(f"图谱数据查询失败: {e}")
            return [], []
            
    def _create_network_plot(self, nodes: List[Dict], edges: List[Dict], 
                           layout: str) -> Tuple[str, Dict]:
        """创建网络图
        
        Args:
            nodes: 节点数据
            edges: 边数据
            layout: 布局类型
            
        Returns:
            HTML内容和JSON数据
        """
        try:
            # 创建NetworkX图
            G = nx.Graph()
            
            # 添加节点
            for node in nodes:
                G.add_node(node['id'], **node)
                
            # 添加边
            for edge in edges:
                if edge['source'] in G.nodes and edge['target'] in G.nodes:
                    G.add_edge(edge['source'], edge['target'], **edge)
                    
            # 计算布局
            if layout == 'force':
                pos = nx.spring_layout(G, k=1, iterations=50)
            elif layout == 'circular':
                pos = nx.circular_layout(G)
            elif layout == 'hierarchical':
                pos = nx.nx_agraph.graphviz_layout(G, prog='dot') if hasattr(nx, 'nx_agraph') else nx.spring_layout(G)
            else:
                pos = nx.spring_layout(G)
                
            # 创建Plotly图
            edge_x = []
            edge_y = []
            for edge in G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
                
            edge_trace = go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=0.5, color='#888'),
                hoverinfo='none',
                mode='lines'
            )
            
            node_x = []
            node_y = []
            node_text = []
            node_color = []
            
            for node in G.nodes():
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
                
                # 节点信息
                node_info = G.nodes[node]
                node_text.append(f"{node_info.get('name', node)}<br>类型: {node_info.get('type', 'unknown')}")
                
                # 节点颜色（基于类型）
                node_type = node_info.get('type', 'unknown')
                type_colors = {
                    'customer': '#FF6B6B',
                    'product': '#4ECDC4',
                    'company': '#45B7D1',
                    'email': '#96CEB4',
                    'unknown': '#FFEAA7'
                }
                node_color.append(type_colors.get(node_type, '#FFEAA7'))
                
            node_trace = go.Scatter(
                x=node_x, y=node_y,
                mode='markers',
                hoverinfo='text',
                text=node_text,
                marker=dict(
                    showscale=True,
                    colorscale='YlGnBu',
                    reversescale=True,
                    color=node_color,
                    size=10,
                    colorbar=dict(
                        thickness=15,
                        len=0.5,
                        x=1.02,
                        title="节点类型"
                    ),
                    line=dict(width=2)
                )
            )
            
            # 创建图形
            fig = go.Figure(data=[edge_trace, node_trace],
                          layout=go.Layout(
                              title='知识图谱可视化',
                              titlefont_size=16,
                              showlegend=False,
                              hovermode='closest',
                              margin=dict(b=20,l=5,r=5,t=40),
                              annotations=[ dict(
                                  text="知识图谱网络结构",
                                  showarrow=False,
                                  xref="paper", yref="paper",
                                  x=0.005, y=-0.002,
                                  xanchor='left', yanchor='bottom',
                                  font=dict(size=12)
                              )],
                              xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                              yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                          ))
            
            html_content = fig.to_html(include_plotlyjs='cdn')
            json_data = fig.to_dict()
            
            return html_content, json_data
            
        except Exception as e:
            self.logger.error(f"网络图创建失败: {e}")
            return self._create_simple_network_html(nodes, edges)
            
    def _create_plotly_chart(self, chart_type: str, data: Dict[str, Any], 
                           title: str, **kwargs) -> Tuple[str, Dict]:
        """创建Plotly图表
        
        Args:
            chart_type: 图表类型
            data: 数据
            title: 标题
            **kwargs: 其他参数
            
        Returns:
            HTML内容和JSON数据
        """
        try:
            if chart_type == 'line':
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=data.get('x', []),
                    y=data.get('y', []),
                    mode='lines+markers',
                    name=data.get('name', 'Series 1')
                ))
                
            elif chart_type == 'bar':
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=data.get('x', []),
                    y=data.get('y', []),
                    name=data.get('name', 'Series 1')
                ))
                
            elif chart_type == 'pie':
                fig = go.Figure()
                fig.add_trace(go.Pie(
                    labels=data.get('labels', []),
                    values=data.get('values', []),
                    name=data.get('name', 'Pie Chart')
                ))
                
            elif chart_type == 'scatter':
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=data.get('x', []),
                    y=data.get('y', []),
                    mode='markers',
                    name=data.get('name', 'Scatter')
                ))
                
            elif chart_type == 'heatmap':
                fig = go.Figure()
                fig.add_trace(go.Heatmap(
                    z=data.get('z', []),
                    x=data.get('x', []),
                    y=data.get('y', []),
                    colorscale='Viridis'
                ))
                
            else:
                raise ValueError(f"不支持的图表类型: {chart_type}")
                
            # 更新布局
            fig.update_layout(
                title=title,
                xaxis_title=kwargs.get('x_title', 'X轴'),
                yaxis_title=kwargs.get('y_title', 'Y轴'),
                template='plotly_white'
            )
            
            html_content = fig.to_html(include_plotlyjs='cdn')
            json_data = fig.to_dict()
            
            return html_content, json_data
            
        except Exception as e:
            self.logger.error(f"Plotly图表创建失败: {e}")
            return self._create_simple_chart_html(chart_type, data, title)
            
    def _create_risk_dashboard_plotly(self, risk_data: Dict[str, Any]) -> Tuple[str, Dict]:
        """创建风险仪表板（Plotly版本）"""
        try:
            # 创建子图
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('风险等级分布', '风险趋势', '风险类别', '综合风险指数'),
                specs=[[{"type": "pie"}, {"type": "scatter"}],
                       [{"type": "bar"}, {"type": "indicator"}]]
            )
            
            # 风险等级分布饼图
            if 'risk_levels' in risk_data:
                levels = risk_data['risk_levels']
                fig.add_trace(
                    go.Pie(
                        labels=list(levels.keys()),
                        values=list(levels.values()),
                        name="风险等级"
                    ),
                    row=1, col=1
                )
                
            # 风险趋势线图
            if 'risk_trends' in risk_data:
                trends = risk_data['risk_trends']
                fig.add_trace(
                    go.Scatter(
                        x=trends.get('dates', []),
                        y=trends.get('scores', []),
                        mode='lines+markers',
                        name="风险趋势"
                    ),
                    row=1, col=2
                )
                
            # 风险类别柱状图
            if 'risk_categories' in risk_data:
                categories = risk_data['risk_categories']
                fig.add_trace(
                    go.Bar(
                        x=list(categories.keys()),
                        y=list(categories.values()),
                        name="风险类别"
                    ),
                    row=2, col=1
                )
                
            # 综合风险指数仪表盘
            overall_risk = risk_data.get('overall_risk_index', 50)
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number+delta",
                    value=overall_risk,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "综合风险指数"},
                    delta={'reference': 50},
                    gauge={
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 25], 'color': "lightgray"},
                            {'range': [25, 50], 'color': "gray"},
                            {'range': [50, 75], 'color': "orange"},
                            {'range': [75, 100], 'color': "red"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 90
                        }
                    }
                ),
                row=2, col=2
            )
            
            fig.update_layout(
                title_text="风险预警仪表板",
                showlegend=False,
                height=600
            )
            
            html_content = fig.to_html(include_plotlyjs='cdn')
            json_data = fig.to_dict()
            
            return html_content, json_data
            
        except Exception as e:
            self.logger.error(f"风险仪表板创建失败: {e}")
            return self._create_simple_dashboard_html(risk_data)
            
    def _create_simple_network_html(self, nodes: List[Dict], edges: List[Dict]) -> Tuple[str, Dict]:
        """创建简单的网络图HTML（无依赖版本）"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>知识图谱可视化</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .graph-container {{ border: 1px solid #ccc; padding: 20px; }}
                .node {{ display: inline-block; margin: 5px; padding: 8px; 
                        background: #e1f5fe; border-radius: 5px; }}
                .edge {{ margin: 2px 0; color: #666; }}
            </style>
        </head>
        <body>
            <h2>知识图谱可视化</h2>
            <div class="graph-container">
                <h3>节点 ({len(nodes)}个)</h3>
                <div>
                    {''.join([f'<div class="node">{node["name"]} ({node["type"]})</div>' for node in nodes[:20]])}
                    {f'<div>... 还有{len(nodes)-20}个节点</div>' if len(nodes) > 20 else ''}
                </div>
                <h3>关系 ({len(edges)}条)</h3>
                <div>
                    {''.join([f'<div class="edge">{edge["source"]} → {edge["target"]} ({edge["relation_type"]})</div>' for edge in edges[:10]])}
                    {f'<div>... 还有{len(edges)-10}条关系</div>' if len(edges) > 10 else ''}
                </div>
            </div>
        </body>
        </html>
        """
        
        json_data = {
            'nodes': nodes,
            'edges': edges,
            'type': 'simple_network'
        }
        
        return html_content, json_data
        
    def _create_simple_chart_html(self, chart_type: str, data: Dict[str, Any], title: str) -> Tuple[str, Dict]:
        """创建简单图表HTML（无依赖版本）"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .chart-container {{ border: 1px solid #ccc; padding: 20px; }}
                .data-item {{ margin: 5px 0; padding: 5px; background: #f5f5f5; }}
            </style>
        </head>
        <body>
            <h2>{title}</h2>
            <div class="chart-container">
                <h3>{chart_type.title()} 数据</h3>
                <div>
                    {self._format_data_for_html(data)}
                </div>
            </div>
        </body>
        </html>
        """
        
        json_data = {
            'chart_type': chart_type,
            'data': data,
            'title': title
        }
        
        return html_content, json_data
        
    def _format_data_for_html(self, data: Dict[str, Any]) -> str:
        """格式化数据为HTML"""
        html_parts = []
        
        for key, value in data.items():
            if isinstance(value, list):
                if len(value) <= 10:
                    items = ', '.join(str(v) for v in value)
                else:
                    items = ', '.join(str(v) for v in value[:10]) + f' ... (共{len(value)}项)'
                html_parts.append(f'<div class="data-item"><strong>{key}:</strong> {items}</div>')
            else:
                html_parts.append(f'<div class="data-item"><strong>{key}:</strong> {value}</div>')
                
        return ''.join(html_parts)
        
    def _create_simple_dashboard_html(self, data: Dict[str, Any]) -> Tuple[str, Dict]:
        """创建简单仪表板HTML"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>风险预警仪表板</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .dashboard {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
                .widget {{ border: 1px solid #ccc; padding: 15px; border-radius: 5px; }}
                .metric {{ font-size: 24px; font-weight: bold; color: #333; }}
                .label {{ color: #666; margin-bottom: 5px; }}
            </style>
        </head>
        <body>
            <h2>风险预警仪表板</h2>
            <div class="dashboard">
                {self._create_dashboard_widgets(data)}
            </div>
        </body>
        </html>
        """
        
        json_data = {
            'dashboard_type': 'risk',
            'data': data
        }
        
        return html_content, json_data
        
    def _create_dashboard_widgets(self, data: Dict[str, Any]) -> str:
        """创建仪表板小部件"""
        widgets = []
        
        # 综合风险指数
        overall_risk = data.get('overall_risk_index', 50)
        risk_color = 'red' if overall_risk > 75 else 'orange' if overall_risk > 50 else 'green'
        widgets.append(f"""
        <div class="widget">
            <div class="label">综合风险指数</div>
            <div class="metric" style="color: {risk_color}">{overall_risk:.1f}</div>
        </div>
        """)
        
        # 风险等级分布
        if 'risk_levels' in data:
            levels = data['risk_levels']
            widgets.append(f"""
            <div class="widget">
                <div class="label">风险等级分布</div>
                {''.join([f'<div>{k}: {v}</div>' for k, v in levels.items()])}
            </div>
            """)
            
        # 风险类别
        if 'risk_categories' in data:
            categories = data['risk_categories']
            widgets.append(f"""
            <div class="widget">
                <div class="label">风险类别</div>
                {''.join([f'<div>{k}: {v:.1f}</div>' for k, v in categories.items()])}
            </div>
            """)
            
        # 最新预警
        if 'recent_alerts' in data:
            alerts = data['recent_alerts'][:3]  # 最多显示3个
            widgets.append(f"""
            <div class="widget">
                <div class="label">最新预警</div>
                {''.join([f'<div style="color: red; margin: 5px 0;">{alert}</div>' for alert in alerts])}
            </div>
            """)
            
        return ''.join(widgets)
        
    def _create_customer_insights_plotly(self, insights_data: Dict[str, Any]) -> Tuple[str, Dict]:
        """创建客户洞察Plotly图表"""
        # 简化实现，返回基本HTML
        return self._create_simple_insights_html(insights_data)
        
    def _create_simple_insights_html(self, insights_data: Dict[str, Any]) -> Tuple[str, Dict]:
        """创建简单客户洞察HTML"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>客户洞察分析</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .insights-container {{ border: 1px solid #ccc; padding: 20px; }}
                .insight-item {{ margin: 10px 0; padding: 10px; background: #f9f9f9; }}
            </style>
        </head>
        <body>
            <h2>客户洞察分析</h2>
            <div class="insights-container">
                {self._format_insights_data(insights_data)}
            </div>
        </body>
        </html>
        """
        
        json_data = {
            'insights_type': 'customer',
            'data': insights_data
        }
        
        return html_content, json_data
        
    def _format_insights_data(self, data: Dict[str, Any]) -> str:
        """格式化洞察数据"""
        html_parts = []
        
        for category, items in data.items():
            html_parts.append(f'<h3>{category}</h3>')
            if isinstance(items, list):
                for item in items[:5]:  # 最多显示5项
                    if isinstance(item, dict):
                        item_html = '<br>'.join([f'{k}: {v}' for k, v in item.items()])
                    else:
                        item_html = str(item)
                    html_parts.append(f'<div class="insight-item">{item_html}</div>')
            else:
                html_parts.append(f'<div class="insight-item">{items}</div>')
                
        return ''.join(html_parts)
        
    def _create_market_trends_plotly(self, trends_data: Dict[str, Any]) -> Tuple[str, Dict]:
        """创建市场趋势Plotly图表"""
        # 简化实现，返回基本HTML
        return self._create_simple_trends_html(trends_data)
        
    def _create_simple_trends_html(self, trends_data: Dict[str, Any]) -> Tuple[str, Dict]:
        """创建简单趋势HTML"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>市场趋势分析</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .trends-container {{ border: 1px solid #ccc; padding: 20px; }}
                .trend-item {{ margin: 10px 0; padding: 10px; background: #f0f8ff; }}
            </style>
        </head>
        <body>
            <h2>市场趋势分析</h2>
            <div class="trends-container">
                {self._format_trends_data(trends_data)}
            </div>
        </body>
        </html>
        """
        
        json_data = {
            'trends_type': 'market',
            'data': trends_data
        }
        
        return html_content, json_data
        
    def _format_trends_data(self, data: Dict[str, Any]) -> str:
        """格式化趋势数据"""
        html_parts = []
        
        for trend_type, trends in data.items():
            html_parts.append(f'<h3>{trend_type}</h3>')
            if isinstance(trends, list):
                for trend in trends[:5]:  # 最多显示5项
                    if isinstance(trend, dict):
                        trend_html = '<br>'.join([f'{k}: {v}' for k, v in trend.items()])
                    else:
                        trend_html = str(trend)
                    html_parts.append(f'<div class="trend-item">{trend_html}</div>')
            else:
                html_parts.append(f'<div class="trend-item">{trends}</div>')
                
        return ''.join(html_parts)
        
    def _generate_customer_report(self, data: Dict[str, Any], template: str) -> str:
        """生成客户报告"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>客户分析报告</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .section {{ margin: 20px 0; }}
                .summary {{ background: #f5f5f5; padding: 15px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>客户分析报告</h1>
                <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="section">
                <h2>执行摘要</h2>
                <div class="summary">
                    本报告基于客户数据分析，提供客户行为洞察和建议。
                </div>
            </div>
            
            <div class="section">
                <h2>客户洞察</h2>
                {self._format_report_data(data)}
            </div>
            
            <div class="section">
                <h2>建议和行动计划</h2>
                <ul>
                    <li>加强高价值客户关系维护</li>
                    <li>优化客户服务流程</li>
                    <li>制定个性化营销策略</li>
                </ul>
            </div>
        </body>
        </html>
        """
        
    def _generate_market_report(self, data: Dict[str, Any], template: str) -> str:
        """生成市场报告"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>市场分析报告</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .section {{ margin: 20px 0; }}
                .summary {{ background: #f0f8ff; padding: 15px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>市场分析报告</h1>
                <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="section">
                <h2>市场概况</h2>
                <div class="summary">
                    本报告分析当前市场趋势和竞争态势。
                </div>
            </div>
            
            <div class="section">
                <h2>市场趋势</h2>
                {self._format_report_data(data)}
            </div>
            
            <div class="section">
                <h2>战略建议</h2>
                <ul>
                    <li>把握市场机会</li>
                    <li>应对竞争挑战</li>
                    <li>优化产品组合</li>
                </ul>
            </div>
        </body>
        </html>
        """
        
    def _generate_risk_report(self, data: Dict[str, Any], template: str) -> str:
        """生成风险报告"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>风险分析报告</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .section {{ margin: 20px 0; }}
                .summary {{ background: #fff5f5; padding: 15px; border-radius: 5px; }}
                .risk-high {{ color: red; font-weight: bold; }}
                .risk-medium {{ color: orange; font-weight: bold; }}
                .risk-low {{ color: green; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>风险分析报告</h1>
                <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="section">
                <h2>风险概述</h2>
                <div class="summary">
                    本报告识别和评估当前业务风险。
                </div>
            </div>
            
            <div class="section">
                <h2>风险评估</h2>
                {self._format_report_data(data)}
            </div>
            
            <div class="section">
                <h2>风险缓解措施</h2>
                <ul>
                    <li>建立风险监控机制</li>
                    <li>制定应急响应计划</li>
                    <li>加强风险管理培训</li>
                </ul>
            </div>
        </body>
        </html>
        """
        
    def _generate_comprehensive_report(self, data: Dict[str, Any], template: str) -> str:
        """生成综合报告"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>综合分析报告</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .section {{ margin: 20px 0; }}
                .summary {{ background: #f8f9fa; padding: 15px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>综合分析报告</h1>
                <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="section">
                <h2>综合概述</h2>
                <div class="summary">
                    本报告提供客户、市场和风险的综合分析。
                </div>
            </div>
            
            <div class="section">
                <h2>分析结果</h2>
                {self._format_report_data(data)}
            </div>
            
            <div class="section">
                <h2>总体建议</h2>
                <ul>
                    <li>优化业务流程</li>
                    <li>加强风险管控</li>
                    <li>提升客户价值</li>
                    <li>把握市场机遇</li>
                </ul>
            </div>
        </body>
        </html>
        """
        
    def _format_report_data(self, data: Dict[str, Any]) -> str:
        """格式化报告数据"""
        html_parts = []
        
        for section, content in data.items():
            html_parts.append(f'<h3>{section}</h3>')
            if isinstance(content, dict):
                html_parts.append('<ul>')
                for key, value in content.items():
                    html_parts.append(f'<li><strong>{key}:</strong> {value}</li>')
                html_parts.append('</ul>')
            elif isinstance(content, list):
                html_parts.append('<ul>')
                for item in content[:10]:  # 最多显示10项
                    html_parts.append(f'<li>{item}</li>')
                html_parts.append('</ul>')
            else:
                html_parts.append(f'<p>{content}</p>')
                
        return ''.join(html_parts)