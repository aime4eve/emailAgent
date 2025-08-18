import dash
from dash import dcc, html, callback_context
from dash.dependencies import Input, Output, State
import pandas as pd
import base64
import io
import json
import os

from src.knowledge_management.domain.model.graph import KnowledgeGraph
from src.knowledge_management.domain.model.node import Node
from src.knowledge_management.domain.model.edge import Edge
from src.interfaces.web_app.visualization.plotly_graph import PlotlyGraphVisualizer
from src.shared.config import Config
from src.shared.utils.data_loader import DataLoader
from src.interfaces.web_app.interaction_handler import InteractionHandler
from src.shared.utils.import_export import DataImportExport
from src.interfaces.web_app.ontology_components import OntologyVisualizer
from src.knowledge_management.application.ontology_generator import OntologyGenerator

def create_app() -> dash.Dash:
    """
    创建并配置Dash应用
    """
    # 初始化配置
    config = Config()
    
    # 初始化应用
    app = dash.Dash(
        __name__,
        suppress_callback_exceptions=True,
        external_stylesheets=[
            "/assets/style.css"
        ]
    )
    
    # 实例化核心组件
    visualizer = PlotlyGraphVisualizer(
        width=config.get_visualization_config().get('graph_width', 1200),
        height=config.get_visualization_config().get('graph_height', 800)
    )
    data_loader = DataLoader()
    kg = KnowledgeGraph()  # 创建空的知识图谱
    interaction_handler = InteractionHandler(kg, visualizer, config)
    import_export_handler = DataImportExport()
    ontology_visualizer = OntologyVisualizer()
    ontology_generator = OntologyGenerator()

    # 定义应用布局
    app.layout = html.Div([
        dcc.Store(id='graph-data'),
        dcc.Store(id='log-messages', data=[]),
        dcc.Download(id='download-data'),
        
        # 标题栏
        html.Div([
            html.H1("知识图谱可视化与管理平台", className="app-title"),
        ], className="header"),
        
        # 主选项卡
        dcc.Tabs(id="main-tabs", value='graph-tab', children=[
            dcc.Tab(label='知识图谱', value='graph-tab'),
            dcc.Tab(label='数据管理', value='data-tab'),
            dcc.Tab(label='知识本体', value='ontology-tab'),
        ]),
        
        # 选项卡内容
        html.Div(id='main-tab-content')
    ])

    # 注册回调函数
    _register_callbacks(app, visualizer, data_loader, interaction_handler, import_export_handler, ontology_visualizer, ontology_generator)
    
    # 初始加载数据
    @app.callback(
        Output('graph-data', 'data', allow_duplicate=True),
        [Input('main-tabs', 'value')], # 初始加载时触发
        prevent_initial_call='initial_duplicate'
    )
    def initial_load(tab_value):
        if tab_value == 'graph-tab':
            kg = _load_sample_data_from_file()
            return kg.to_dict()
        return dash.no_update

    # 文件上传回调
    @app.callback(
        Output('graph-data', 'data', allow_duplicate=True),
        [Input('upload-data', 'contents')],
        [State('upload-data', 'filename'),
         State('graph-data', 'data')],
        prevent_initial_call=True
    )
    def handle_file_upload(contents, filename, graph_data):
        print(f" handle_file_upload triggered. Filename: {filename}")
        if contents:
            try:
                content_type, content_string = contents.split(',')
                decoded = base64.b64decode(content_string)
                
                print("  File content decoded successfully.")

                new_kg = KnowledgeGraph.from_dict(graph_data) # 从现有数据创建
                print(f"  KnowledgeGraph created from existing data. Nodes: {len(new_kg.nodes)}, Edges: {len(new_kg.edges)}")

                if 'json' in filename:
                    decoded_content = decoded.decode('utf-8')
                    string_io = io.StringIO(decoded_content)
                    new_kg = import_export_handler.import_from_json(string_io)
                    print(f"  Imported from JSON. New KG has Nodes: {len(new_kg.nodes)}, Edges: {len(new_kg.edges)}")
                elif 'csv' in filename:
                    # 假设CSV导入需要节点和边文件，这里简化处理
                    # 在实际应用中，可能需要更复杂的UI来处理多个文件
                    print("  CSV import placeholder.")
                    pass
                elif 'xls' in filename:
                    import_export_handler.import_from_excel(new_kg, decoded)
                    print("  Imported from Excel.")
                
                print(f"成功从 {filename} 导入数据")
                return new_kg.to_dict()
            
            except Exception as e:
                print(f"文件上传处理失败: {e}")
                import traceback
                traceback.print_exc()
                return dash.no_update
        return dash.no_update

    # 文件下载回调
    @app.callback(
        Output('download-data', 'data'),
        [Input('export-button', 'n_clicks')],
        [State('export-format', 'value'),
         State('graph-data', 'data')],
        prevent_initial_call=True
    )
    def handle_file_download(n_clicks, export_format, graph_data):
        """
        处理文件下载
        """
        if not n_clicks:
            return dash.no_update
            
        try:
            current_kg = KnowledgeGraph.from_dict(graph_data)
            timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
            
            if export_format == 'json':
                # JSON导出
                data = import_export_handler.export_to_json(current_kg, include_metadata=True)
                filename = f"knowledge_graph_{timestamp}.json"
                
                return dict(
                    content=json.dumps(data, ensure_ascii=False, indent=2),
                    filename=filename,
                    type="application/json"
                )
                
            elif export_format == 'csv':
                # CSV导出（返回压缩包）
                import zipfile
                import tempfile
                
                with tempfile.TemporaryDirectory() as temp_dir:
                    nodes_path = os.path.join(temp_dir, f"nodes_{timestamp}.csv")
                    edges_path = os.path.join(temp_dir, f"edges_{timestamp}.csv")
                    zip_path = os.path.join(temp_dir, f"knowledge_graph_{timestamp}.zip")
                    
                    # 导出CSV文件
                    import_export_handler.export_to_csv(current_kg, nodes_path, edges_path)
                    
                    # 创建ZIP文件
                    with zipfile.ZipFile(zip_path, 'w') as zipf:
                        zipf.write(nodes_path, f"nodes_{timestamp}.csv")
                        zipf.write(edges_path, f"edges_{timestamp}.csv")
                        
                    # 读取ZIP文件内容
                    with open(zip_path, 'rb') as f:
                        zip_content = f.read()
                        
                    return dict(
                        content=base64.b64encode(zip_content).decode(),
                        filename=f"knowledge_graph_{timestamp}.zip",
                        type="application/zip",
                        base64=True
                    )
                    
            elif export_format == 'excel':
                # Excel导出
                with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as temp_file:
                    temp_path = temp_file.name
                    
                try:
                    import_export_handler.export_to_excel(current_kg, temp_path)
                    
                    with open(temp_path, 'rb') as f:
                        excel_content = f.read()
                        
                    return dict(
                        content=base64.b64encode(excel_content).decode(),
                        filename=f"knowledge_graph_{timestamp}.xlsx",
                        type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        base64=True
                    )
                finally:
                    os.unlink(temp_path)
                    
        except Exception as e:
            # 错误情况下返回错误信息文件
            error_data = {
                'error': str(e),
                'timestamp': pd.Timestamp.now().isoformat()
            }
            return dict(
                content=json.dumps(error_data, ensure_ascii=False, indent=2),
                filename=f"export_error_{timestamp}.json",
                type="application/json"
            )
            
    return app

def _load_sample_data_from_file() -> KnowledgeGraph:
    """
    从data目录的JSON文件加载示例数据
    
    Returns:
        KnowledgeGraph: 加载了数据的知识图谱实例
    """
    kg = KnowledgeGraph() # 在函数内部创建实例
    try:
        # 获取data目录路径
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        data_file_path = os.path.join(current_dir, 'data', 'default_data.json')
        
        # 检查文件是否存在
        if not os.path.exists(data_file_path):
            print(f"警告: 样例数据文件不存在: {data_file_path}")
            return kg # 返回空图谱
            
        # 读取JSON文件
        with open(data_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # 添加节点
        if 'nodes' in data:
            for node_data in data['nodes']:
                node = Node.from_dict(node_data)
                kg.add_node(node)
                
        # 添加边
        if 'edges' in data:
            for edge_data in data['edges']:
                edge = Edge.from_dict(edge_data)
                kg.add_edge(edge)
                
        print(f"成功从文件加载样例数据: {len(data.get('nodes', []))}个节点, {len(data.get('edges', []))}条边")
        
    except Exception as e:
        print(f"加载样例数据失败: {str(e)}")
        # 如果加载失败，返回一个空的图谱
    
    return kg

def _register_callbacks(app: dash.Dash, visualizer: PlotlyGraphVisualizer, data_loader: DataLoader, interaction_handler: InteractionHandler, import_export_handler: DataImportExport, ontology_visualizer: OntologyVisualizer, ontology_generator: OntologyGenerator) -> None:
    """
    注册所有回调函数
    
    Args:
        app: Dash应用实例
        visualizer: 可视化器实例
        data_loader: 数据加载器实例
        interaction_handler: 交互处理器实例
        import_export_handler: 导入导出处理器实例
        ontology_visualizer: 本体可视化器实例
        ontology_generator: 本体生成器实例
    """
    


    # 动态更新添加节点的类型选项
    @app.callback(
        Output('new-node-type', 'options'),
        [Input('graph-data', 'data')]
    )
    def update_add_node_type_options(graph_data):
        """
        根据当前图数据动态更新添加节点的类型选项
        """
        if not graph_data:
            return []
        
        current_kg = KnowledgeGraph.from_dict(graph_data)
        stats = current_kg.get_statistics()
        
        # 生成类型选项，包含现有类型
        type_options = [{'label': t, 'value': t} for t in stats['node_types']]
        
        return type_options
    
    @app.callback(
        Output('graph-data', 'data', allow_duplicate=True),
        [Input('add-node-button', 'n_clicks'),
         Input('clear-button', 'n_clicks'),
         Input('reload-button', 'n_clicks')],
        [State('new-node-label', 'value'),
         State('new-node-type', 'value'),
         State('graph-data', 'data'),
         State('log-messages', 'data')],
        prevent_initial_call=True
    )
    def handle_data_operations(add_clicks, clear_clicks, reload_clicks,
                             node_label, node_type, graph_data, log_messages):
        """
        处理数据操作
        """
        ctx = callback_context
        if not ctx.triggered or not graph_data:
            return dash.no_update
        
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # 总是从 graph-data 创建 KG 实例
        current_kg = KnowledgeGraph.from_dict(graph_data)
        interaction_handler.kg = current_kg # 确保 handler 使用最新的 kg
        
        if button_id == 'add-node-button' and node_label:
            # 使用交互处理器添加新节点
            import uuid
            node_id = str(uuid.uuid4())
            success = interaction_handler.add_node(node_id, node_label, node_type)
            if success:
                # 保存到JSON文件
                try:
                    data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'sample_data.json')
                    export_data = import_export_handler.export_to_json(current_kg, include_metadata=True)
                    with open(data_path, 'w', encoding='utf-8') as f:
                        json.dump(export_data, f, ensure_ascii=False, indent=2)
                    log_messages.append(f"添加节点: {node_label} ({node_type}) - 已保存")
                except Exception as e:
                    log_messages.append(f"添加节点: {node_label} ({node_type}) - 保存失败: {str(e)}")
            else:
                log_messages.append(f"添加节点失败: {node_label}")
            
        elif button_id == 'clear-button':
            # 清空图谱
            current_kg.clear()
            interaction_handler.clear_selection()
            log_messages.append("清空图谱")
            
        elif button_id == 'reload-button':
            # 重新加载示例数据
            current_kg = _load_sample_data_from_file() # 获取新的KG实例
            interaction_handler.clear_selection()
            log_messages.append("重新加载示例数据")
            
        # 图形点击事件处理已移除，因为knowledge-graph组件不存在
        
        # 保持日志长度
        if len(log_messages) > 10:
            log_messages = log_messages[-10:]
        
        return current_kg.to_dict()
    
    @app.callback(
        Output('main-tab-content', 'children'),
        [Input('main-tabs', 'value'),
         Input('graph-data', 'data')]
    )
    def render_tab_content(active_tab, graph_data):
        if active_tab == 'graph-tab':
            node_type_options = []
            stats_content = html.Div("暂无统计信息")

            if graph_data:
                current_kg = KnowledgeGraph.from_dict(graph_data)
                stats = current_kg.get_statistics()
                node_type_options = [{'label': t, 'value': t} for t in stats['node_types']]
                stats_content = html.Div([
                    html.P(f"节点数量: {stats['node_count']}"),
                    html.P(f"边数量: {stats['edge_count']}"),
                    html.P(f"节点类型: {', '.join(stats['node_types'])}"),
                    html.P(f"边类型: {', '.join(stats['edge_types'])}"),
                ])

            return html.Div([
                # 控制面板
                html.Div([
                    dcc.Input(id='search-input', placeholder='搜索节点...', className='search-input'),
                    html.Button('搜索', id='search-button', className='search-button'),
                    dcc.Dropdown(
                        id='layout-dropdown',
                        options=[
                            {'label': 'Force-Directed', 'value': 'kamada_kawai'},
                            {'label': 'Circular', 'value': 'circular'},
                            {'label': 'Random', 'value': 'random'},
                            {'label': 'Shell', 'value': 'shell'},
                            {'label': 'Spectral', 'value': 'spectral'},
                        ],
                        value='kamada_kawai',
                        clearable=False,
                        className='layout-dropdown'
                    ),
                    dcc.Dropdown(
                        id='node-type-filter',
                        options=node_type_options,
                        multi=True,
                        placeholder='按节点类型筛选...',
                        className='node-type-filter'
                    ),
                ], className='control-panel'),

                # 主内容区
                html.Div([
                    # 图谱可视化
                    html.Div(
                        html.Div(id="graph-display"), # Container for the graph
                        className="graph-container"
                    ),
                    # 侧边栏
                    html.Div([
                        html.H3("图谱信息", className="sidebar-title"),
                        html.Div(stats_content, id="graph-stats", className="stats-container"),
                        html.H3("节点详情", className="sidebar-title"),
                        html.Div(id="node-details", className="details-container"),
                        html.H3("操作日志", className="sidebar-title"),
                        html.Div(id="operation-log", className="log-container", children=[
                            html.P("暂无操作记录")
                        ])
                    ], className="sidebar")
                ], className='graph-panel')
            ], className="graph-tab-content")

        elif active_tab == 'data-tab':
            # 数据管理选项卡内容
            return html.Div([
                html.H3("数据管理"),
                dcc.Upload(
                    id='upload-data',
                    children=html.Div(['拖放或 ', html.A('选择文件')]),
                    style={
                        'width': '100%', 'height': '60px', 'lineHeight': '60px',
                        'borderWidth': '1px', 'borderStyle': 'dashed',
                        'borderRadius': '5px', 'textAlign': 'center', 'margin': '10px'
                    },
                    multiple=False
                ),
                dcc.Dropdown(
                    id='export-format',
                    options=[
                        {'label': 'JSON', 'value': 'json'},
                        {'label': 'CSV (Zip)', 'value': 'csv'},
                        {'label': 'Excel', 'value': 'excel'}
                    ],
                    value='json',
                    clearable=False
                ),
                html.Button('导出数据', id='export-button')
            ], className="data-tab-content")
        
        elif active_tab == 'ontology-tab':
            # 知识本体选项卡内容
            return ontology_visualizer.create_ontology_overview_layout()
        
        return html.Div("选项卡内容加载中...")

    @app.callback(
        Output('graph-display', 'children'),
        [Input('search-button', 'n_clicks'),
         Input('layout-dropdown', 'value'),
         Input('node-type-filter', 'value'),
         Input('graph-data', 'data')],
        [State('search-input', 'value')]
    )
    def update_graph_display(search_clicks, layout, selected_types, graph_data, search_term):
        print(f"DEBUG: update_graph_display triggered. Data has {len(graph_data.get('nodes', []))} nodes.")
        ctx = callback_context
        
        # 如果没有数据或回调不是由用户交互触发的（初始加载），则显示默认视图
        if not graph_data or not graph_data.get('nodes'):
            print("DEBUG: No graph data, returning empty graph.")
            return dcc.Graph(
                id='knowledge-graph',
                figure={'data': [], 'layout': {'title': '暂无数据'}},
                config={'displayModeBar': True, 'scrollZoom': True},
                style={'height': '600px'}
            )

        print("DEBUG: Graph data found, proceeding to render.")
        current_kg = KnowledgeGraph.from_dict(graph_data)
        
        # 应用筛选
        filtered_nodes = []
        if selected_types or search_term:
            for node in current_kg.nodes.values():
                # 类型筛选
                if selected_types and node.type not in selected_types:
                    continue
                # 搜索筛选
                if search_term and search_term.lower() not in node.label.lower():
                    continue
                filtered_nodes.append(node)
        else:
            filtered_nodes = list(current_kg.nodes.values())

        
        filtered_kg = KnowledgeGraph()
        for node in filtered_nodes:
            filtered_kg.add_node(node)
        
        for edge in current_kg.edges.values():
            if edge.source_id in filtered_kg.nodes and edge.target_id in filtered_kg.nodes:
                filtered_kg.add_edge(edge)
        
        try:
            fig = visualizer.create_figure(filtered_kg, layout_type=layout)
            return dcc.Graph(
                id='knowledge-graph',
                figure=fig,
                config={'displayModeBar': True, 'scrollZoom': True},
                style={'height': '600px'}
            )
        except Exception as e:
            return html.Div(f"图谱渲染错误: {str(e)}")
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=8050)