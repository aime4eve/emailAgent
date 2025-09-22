# 知识图谱可视化与管理平台 - 系统概要设计（单体部署完整版）

## 1. 设计概述

### 1.1 设计背景
基于《系统设计需求.md》中"### 7.1 技术约束"章节的要求，本设计将企业级分布式架构适配为单体部署架构，使用Python技术栈实现完整的知识图谱可视化与管理功能。

### 1.2 技术约束适配

**原技术约束要求**：
- 前端：React + TypeScript + AntV G6
- 后端：Spring Boot + TinkerPop Gremlin Server
- 图数据库：JanusGraph（兼容TinkerPop）
- 通信：WebSocket/HTTP2

**单体部署适配**：
- 前端：Dash + Plotly（基于React的Python Web框架）
- 后端：Flask + NetworkX（Python内置图处理库）
- 存储：NetworkX内存图 + JSON持久化（本地文件存储）
- 通信：Flask内置HTTP服务器（简化通信）

### 1.3 设计目标
- **功能完整**：实现需求文档中的所有核心功能
- **部署简化**：单文件部署，无需复杂配置
- **数据安全**：本地存储，无需外部依赖
- **性能优化**：针对单机环境优化内存和CPU使用

## 2. 系统架构设计

### 2.1 单体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    用户浏览器层                                │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Dash Web界面 (React-based)                   │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │ │
│  │  │  知识图谱   │  │   数据管理   │  │   知识本体   │      │ │
│  │  │  可视化页   │  │   导入导出   │  │   管理页    │      │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘      │ │
│  └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                    应用服务层                                  │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Flask + Dash应用服务                          │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │ │
│  │  │  路由处理   │  │  业务逻辑   │  │  数据验证   │      │ │
│  │  │  中间件     │  │  处理器     │  │  过滤器     │      │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘      │ │
│  └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                    业务逻辑层                                  │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              核心功能模块                                 │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │ │
│  │  │  图谱管理   │  │  可视化   │  │  导入导出   │      │ │
│  │  │  NetworkX   │  │  Plotly   │  │  多格式     │      │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘      │ │
│  └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                    数据存储层                                  │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              本地文件存储                                 │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │ │
│  │  │  JSON文件   │  │  CSV文件   │  │  配置文件   │      │ │
│  │  │  主数据     │  │  表格数据   │  │  YAML/JSON  │      │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘      │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 技术栈详细说明

#### 2.2.1 前端技术栈（Dash替代React）
- **Dash框架**：基于React的Python Web框架
- **Plotly.js**：内置的高性能可视化库
- **Bootstrap**：响应式UI组件
- **自定义CSS**：个性化样式定制

#### 2.2.2 后端技术栈（Flask替代Spring Boot）
- **Flask**：轻量级Python Web框架
- **NetworkX**：图论算法和图数据结构
- **Pandas**：数据处理和分析
- **NumPy**：数值计算

#### 2.2.3 存储方案（本地替代JanusGraph）
- **主数据**：JSON Lines格式文件
- **配置数据**：YAML格式文件
- **缓存数据**：SQLite轻量级数据库
- **日志数据**：轮转日志文件

### 2.3 模块层次结构

```
knowledge-graph-app/
├── app.py                    # 主应用入口
├── requirements.txt          # 依赖列表
├── config/
│   ├── app.yaml             # 应用配置
│   └── logging.yaml         # 日志配置
├── src/
│   ├── __init__.py
│   ├── core/                # 核心业务逻辑
│   │   ├── __init__.py
│   │   ├── knowledge_graph/ # 图数据管理
│   │   │   ├── __init__.py
│   │   │   ├── graph.py     # 知识图谱类
│   │   │   ├── node.py      # 节点类
│   │   │   ├── edge.py      # 边类
│   │   │   └── algorithms.py # 图算法
│   │   ├── ontology/        # 本体管理
│   │   │   ├── __init__.py
│   │   │   ├── manager.py   # 本体管理器
│   │   │   └── validator.py # 本体验证器
│   │   └── storage/         # 数据存储
│   │       ├── __init__.py
│   │       ├── json_store.py # JSON存储
│   │       └── file_manager.py # 文件管理
│   ├── services/            # 业务服务
│   │   ├── __init__.py
│   │   ├── visualization.py # 可视化服务
│   │   ├── import_export.py # 导入导出服务
│   │   └── email_processor.py # 邮件处理服务
│   ├── web/                 # Web界面
│   │   ├── __init__.py
│   │   ├── app.py           # Dash应用配置
│   │   ├── layouts.py       # 页面布局
│   │   ├── callbacks.py     # 回调函数
│   │   └── components.py    # UI组件
│   └── utils/               # 工具类
│       ├── __init__.py
│       ├── config.py        # 配置管理
│       ├── logger.py        # 日志工具
│       └── validators.py    # 数据验证
├── data/
│   ├── graphs/              # 图谱数据
│   ├── ontologies/          # 本体定义
│   ├── backups/             # 自动备份
│   └── logs/                # 应用日志
└── tests/                   # 测试代码
    ├── __init__.py
    ├── unit/                # 单元测试
    └── integration/         # 集成测试
```

## 3. 核心数据模型设计

### 3.1 知识图谱数据模型

#### 3.1.1 节点数据结构
```python
@dataclass
class KGNode:
    """知识图谱节点"""
    id: str
    label: str
    node_type: str
    properties: Dict[str, Any] = field(default_factory=dict)
    x: Optional[float] = None
    y: Optional[float] = None
    size: float = 20.0
    color: str = "#1f77b4"
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "label": self.label,
            "type": self.node_type,
            "properties": self.properties,
            "x": self.x,
            "y": self.y,
            "size": self.size,
            "color": self.color
        }
```

#### 3.1.2 边数据结构
```python
@dataclass
class KGEdge:
    """知识图谱边"""
    id: str
    source: str
    target: str
    label: str
    edge_type: str
    properties: Dict[str, Any] = field(default_factory=dict)
    weight: float = 1.0
    color: str = "#888888"
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "source": self.source,
            "target": self.target,
            "label": self.label,
            "type": self.edge_type,
            "properties": self.properties,
            "weight": self.weight,
            "color": self.color
        }
```

#### 3.1.3 知识图谱主类
```python
class KnowledgeGraph:
    """知识图谱主类"""
    def __init__(self, graph_id: str = None):
        self.id = graph_id or str(uuid.uuid4())
        self.name = "Untitled Graph"
        self.description = ""
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.nodes: Dict[str, KGNode] = {}
        self.edges: Dict[str, KGEdge] = {}
        self.ontology: Optional[KnowledgeOntology] = None
        
    def to_networkx(self) -> nx.Graph:
        """转换为NetworkX图"""
        G = nx.Graph()
        for node in self.nodes.values():
            G.add_node(node.id, **node.to_dict())
        for edge in self.edges.values():
            G.add_edge(edge.source, edge.target, **edge.to_dict())
        return G
```

### 3.2 本体数据模型

#### 3.2.1 本体类定义
```python
@dataclass
class OntologyClass:
    """本体类定义"""
    name: str
    label: str
    description: str = ""
    parent: Optional[str] = None
    properties: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "label": self.label,
            "description": self.description,
            "parent": self.parent,
            "properties": self.properties
        }
```

#### 3.2.2 本体属性定义
```python
@dataclass
class OntologyProperty:
    """本体属性定义"""
    name: str
    label: str
    property_type: str  # "string", "number", "boolean", "date"
    domain: str
    range: str
    description: str = ""
    required: bool = False
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "label": self.label,
            "type": self.property_type,
            "domain": self.domain,
            "range": self.range,
            "description": self.description,
            "required": self.required
        }
```

### 3.3 邮件处理数据模型

#### 3.3.1 邮件元数据
```python
@dataclass
class EmailMetadata:
    """邮件元数据"""
    message_id: str
    thread_id: str
    from_address: str
    from_name: str
    to_addresses: List[str]
    cc_addresses: List[str] = field(default_factory=list)
    subject: str = ""
    date: datetime = None
    priority: str = "normal"
    labels: List[str] = field(default_factory=list)
```

#### 3.3.2 邮件实体
```python
@dataclass
class EmailEntity:
    """邮件中提取的实体"""
    text: str
    entity_type: str
    start_pos: int
    end_pos: int
    confidence: float
    properties: Dict[str, Any] = field(default_factory=dict)
```

## 4. 功能模块设计

### 4.1 知识图谱管理模块

#### 4.1.1 图谱管理器
```python
class GraphManager:
    """知识图谱管理器"""
    
    def __init__(self, storage_dir: str):
        self.storage_dir = Path(storage_dir)
        self.current_graph: Optional[KnowledgeGraph] = None
        self.graph_cache: Dict[str, KnowledgeGraph] = {}
        
    def create_graph(self, name: str, description: str = "") -> str:
        """创建新图谱"""
        graph = KnowledgeGraph()
        graph.name = name
        graph.description = description
        self.save_graph(graph)
        return graph.id
        
    def load_graph(self, graph_id: str) -> KnowledgeGraph:
        """加载图谱"""
        if graph_id in self.graph_cache:
            return self.graph_cache[graph_id]
            
        file_path = self.storage_dir / f"{graph_id}.json"
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            graph = KnowledgeGraph.from_dict(data)
            self.graph_cache[graph_id] = graph
            return graph
        raise FileNotFoundError(f"Graph {graph_id} not found")
        
    def save_graph(self, graph: KnowledgeGraph):
        """保存图谱"""
        file_path = self.storage_dir / f"{graph.id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(graph.to_dict(), f, ensure_ascii=False, indent=2)
        self.graph_cache[graph.id] = graph
```

#### 4.1.2 图算法引擎
```python
class GraphAlgorithms:
    """图算法引擎"""
    
    @staticmethod
    def calculate_centrality(graph: KnowledgeGraph, algorithm: str = "degree") -> Dict[str, float]:
        """计算节点中心性"""
        G = graph.to_networkx()
        if algorithm == "degree":
            return nx.degree_centrality(G)
        elif algorithm == "betweenness":
            return nx.betweenness_centrality(G)
        elif algorithm == "closeness":
            return nx.closeness_centrality(G)
        elif algorithm == "eigenvector":
            return nx.eigenvector_centrality(G, max_iter=1000)
        else:
            raise ValueError(f"Unknown centrality algorithm: {algorithm}")
    
    @staticmethod
    def find_communities(graph: KnowledgeGraph, algorithm: str = "louvain") -> Dict[str, int]:
        """社区发现"""
        G = graph.to_networkx()
        if algorithm == "louvain":
            # 使用NetworkX的社区发现
            communities = nx.community.louvain_communities(G)
            node_community = {}
            for i, community in enumerate(communities):
                for node in community:
                    node_community[node] = i
            return node_community
        else:
            raise ValueError(f"Unknown community algorithm: {algorithm}")
```

### 4.2 可视化模块

#### 4.2.1 可视化引擎
```python
class VisualizationEngine:
    """可视化引擎"""
    
    def __init__(self, width: int = 1200, height: int = 800):
        self.width = width
        self.height = height
        self.color_scheme = {
            "person": "#1f77b4",
            "organization": "#ff7f0e",
            "location": "#2ca02c",
            "event": "#d62728",
            "default": "#7f7f7f"
        }
        
    def create_graph_figure(self, graph: KnowledgeGraph, layout: str = "spring") -> go.Figure:
        """创建图谱可视化"""
        G = graph.to_networkx()
        
        # 计算布局
        if layout == "spring":
            pos = nx.spring_layout(G, k=1, iterations=50)
        elif layout == "circular":
            pos = nx.circular_layout(G)
        elif layout == "hierarchical":
            pos = nx.shell_layout(G)
        else:
            pos = nx.spring_layout(G)
            
        # 创建边轨迹
        edge_x, edge_y = [], []
        for edge in graph.edges.values():
            x0, y0 = pos[edge.source]
            x1, y1 = pos[edge.target]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1, color='#888'),
            hoverinfo='none',
            mode='lines')
            
        # 创建节点轨迹
        node_x, node_y = [], []
        node_text, node_color = [], []
        
        for node in graph.nodes.values():
            x, y = pos[node.id]
            node_x.append(x)
            node_y.append(y)
            node_text.append(node.label)
            node_color.append(self.color_scheme.get(node.type, self.color_scheme["default"]))
            
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            text=node_text,
            textposition="top center",
            marker=dict(
                size=20,
                color=node_color,
                line=dict(width=2, color='white')
            ),
            hovertemplate='<b>%{text}</b><br>Type: %{customdata}<extra></extra>',
            customdata=[node.type for node in graph.nodes.values()]
        )
        
        # 创建图形
        fig = go.Figure(data=[edge_trace, node_trace],
                       layout=go.Layout(
                           showlegend=False,
                           hovermode='closest',
                           margin=dict(b=20, l=5, r=5, t=40),
                           xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           width=self.width,
                           height=self.height
                       ))
        
        return fig
```

### 4.3 导入导出模块

#### 4.3.1 多格式导入器
```python
class DataImporter:
    """多格式数据导入器"""
    
    def __init__(self):
        self.supported_formats = ['json', 'csv', 'excel', 'owl', 'rdf']
    
    def import_from_json(self, file_path: str) -> KnowledgeGraph:
        """从JSON导入"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return KnowledgeGraph.from_dict(data)
    
    def import_from_csv(self, nodes_file: str, edges_file: str) -> KnowledgeGraph:
        """从CSV导入"""
        graph = KnowledgeGraph()
        
        # 导入节点
        nodes_df = pd.read_csv(nodes_file)
        for _, row in nodes_df.iterrows():
            node = KGNode(
                id=str(row.get('id', uuid.uuid4())),
                label=str(row.get('label', '')),
                node_type=str(row.get('type', 'default')),
                properties=row.drop(['id', 'label', 'type']).to_dict()
            )
            graph.nodes[node.id] = node
            
        # 导入边
        edges_df = pd.read_csv(edges_file)
        for _, row in edges_df.iterrows():
            edge = KGEdge(
                id=str(row.get('id', uuid.uuid4())),
                source=str(row['source']),
                target=str(row['target']),
                label=str(row.get('label', '')),
                edge_type=str(row.get('type', 'default')),
                properties=row.drop(['id', 'source', 'target', 'label', 'type']).to_dict()
            )
            graph.edges[edge.id] = edge
            
        return graph
    
    def import_from_excel(self, file_path: str, sheet_name: str = None) -> KnowledgeGraph:
        """从Excel导入"""
        # 实现Excel导入逻辑
        pass
```

#### 4.3.2 多格式导出器
```python
class DataExporter:
    """多格式数据导出器"""
    
    def export_to_json(self, graph: KnowledgeGraph, file_path: str):
        """导出为JSON"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(graph.to_dict(), f, ensure_ascii=False, indent=2)
    
    def export_to_csv(self, graph: KnowledgeGraph, nodes_file: str, edges_file: str):
        """导出为CSV"""
        # 导出节点
        nodes_data = []
        for node in graph.nodes.values():
            node_data = {
                'id': node.id,
                'label': node.label,
                'type': node.node_type,
                **node.properties
            }
            nodes_data.append(node_data)
        
        nodes_df = pd.DataFrame(nodes_data)
        nodes_df.to_csv(nodes_file, index=False, encoding='utf-8')
        
        # 导出边
        edges_data = []
        for edge in graph.edges.values():
            edge_data = {
                'id': edge.id,
                'source': edge.source,
                'target': edge.target,
                'label': edge.label,
                'type': edge.edge_type,
                **edge.properties
            }
            edges_data.append(edge_data)
            
        edges_df = pd.DataFrame(edges_data)
        edges_df.to_csv(edges_file, index=False, encoding='utf-8')
    
    def export_to_excel(self, graph: KnowledgeGraph, file_path: str):
        """导出为Excel"""
        # 实现Excel导出逻辑
        pass
```

### 4.4 邮件处理模块

#### 4.4.1 邮件客户端
```python
class EmailClient:
    """邮件客户端"""
    
    def __init__(self, config: dict):
        self.imap_server = config.get('imap_server')
        self.email = config.get('email')
        self.password = config.get('password')
        self.port = config.get('port', 993)
        self.use_ssl = config.get('use_ssl', True)
    
    def connect(self) -> imaplib.IMAP4_SSL:
        """连接邮件服务器"""
        try:
            if self.use_ssl:
                mail = imaplib.IMAP4_SSL(self.imap_server, self.port)
            else:
                mail = imaplib.IMAP4(self.imap_server, self.port)
            mail.login(self.email, self.password)
            return mail
        except Exception as e:
            raise ConnectionError(f"Failed to connect to email server: {e}")
    
    def fetch_emails(self, folder: str = "INBOX", limit: int = 100) -> List[EmailMetadata]:
        """获取邮件列表"""
        mail = self.connect()
        mail.select(folder)
        
        # 搜索未读邮件
        status, messages = mail.search(None, 'UNSEEN')
        
        emails = []
        message_ids = messages[0].split()
        
        for msg_id in message_ids[:limit]:
            status, msg_data = mail.fetch(msg_id, '(RFC822)')
            raw_email = msg_data[0][1]
            email_message = email.message_from_bytes(raw_email)
            
            # 解析邮件元数据
            email_meta = self._parse_email_metadata(email_message, msg_id.decode())
            emails.append(email_meta)
            
        mail.close()
        mail.logout()
        return emails
    
    def _parse_email_metadata(self, msg: email.message.Message, msg_id: str) -> EmailMetadata:
        """解析邮件元数据"""
        # 实现邮件解析逻辑
        pass
```

#### 4.4.2 实体提取器
```python
class EntityExtractor:
    """邮件实体提取器"""
    
    def __init__(self):
        self.patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',
            'date': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            'url': r'https?://[^\s<>"{}|\\^`\[\]]*',
            'person': r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',
            'organization': r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Inc|Corp|Ltd|LLC|Company)\b'
        }
    
    def extract_entities(self, text: str) -> List[EmailEntity]:
        """从文本中提取实体"""
        entities = []
        
        for entity_type, pattern in self.patterns.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                entity = EmailEntity(
                    text=match.group(),
                    entity_type=entity_type,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.8
                )
                entities.append(entity)
                
        return entities
```

## 5. 数据存储设计

### 5.1 存储架构

#### 5.1.1 文件组织结构
```
data/
├── graphs/
│   ├── active/              # 当前使用的图谱
│   │   ├── graph_001.json   # 主图谱文件
│   │   └── graph_002.json   # 备用图谱
│   ├── archived/            # 归档图谱
│   └── snapshots/           # 自动快照
│       ├── 2024-12-20_10-00-00_graph_001.json
│       └── 2024-12-20_15-30-00_graph_001.json
├── ontologies/
│   ├── system/              # 系统本体
│   └── user/                # 用户自定义本体
├── email_data/
│   ├── processed/           # 已处理邮件
│   └── attachments/         # 邮件附件
├── configs/
│   ├── app_config.yaml      # 应用配置
│   └── user_settings.json   # 用户设置
└── logs/
    ├── app.log              # 应用日志
    └── error.log            # 错误日志
```

#### 5.1.2 数据文件格式

**知识图谱JSON格式**:
```json
{
  "metadata": {
    "id": "graph_001",
    "name": "企业知识图谱",
    "description": "包含公司人员、部门、项目等信息",
    "version": "1.0.0",
    "created_at": "2024-12-20T10:00:00Z",
    "updated_at": "2024-12-20T15:30:00Z",
    "node_count": 150,
    "edge_count": 200
  },
  "ontology": {
    "classes": [
      {
        "name": "Person",
        "label": "人员",
        "description": "公司人员",
        "properties": ["name", "email", "department", "position"]
      }
    ],
    "properties": [
      {
        "name": "name",
        "label": "姓名",
        "type": "string",
        "required": true
      }
    ]
  },
  "nodes": [
    {
      "id": "person_001",
      "label": "张三",
      "type": "Person",
      "properties": {
        "name": "张三",
        "email": "zhangsan@company.com",
        "department": "技术部",
        "position": "高级工程师"
      },
      "x": 100.5,
      "y": 200.3,
      "size": 25.0,
      "color": "#1f77b4"
    }
  ],
  "edges": [
    {
      "id": "edge_001",
      "source": "person_001",
      "target": "person_002",
      "label": "同事",
      "type": "colleague",
      "properties": {
        "relationship": "同事",
        "since": "2023-01-15"
      },
      "weight": 1.0,
      "color": "#888888"
    }
  ]
}
```

### 5.2 配置管理

#### 5.2.1 应用配置文件
```yaml
# config/app_config.yaml
app:
  name: "知识图谱可视化与管理平台"
  version: "1.0.0"
  debug: false
  max_file_size: "100MB"

server:
  host: "127.0.0.1"
  port: 8050
  debug: false
  threaded: true

storage:
  data_dir: "./data"
  backup_enabled: true
  backup_interval: 3600  # 秒
  max_backups: 10
  compression: true

visualization:
  default_layout: "spring"
  node_size: 20
  edge_width: 2
  colors:
    person: "#1f77b4"
    organization: "#ff7f0e"
    location: "#2ca02c"
    event: "#d62728"
    default: "#7f7f7f"
  
email:
  enabled: false
  check_interval: 300  # 秒
  max_emails_per_batch: 100
  imap_server: "imap.company.com"
  port: 993
  use_ssl: true

logging:
  level: "INFO"
  file: "./data/logs/app.log"
  max_size: "10MB"
  backup_count: 5
```

#### 5.2.2 运行时配置
```python
class AppConfig:
    """应用配置管理器"""
    
    def __init__(self, config_path: str = "config/app_config.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """加载配置文件"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return self._get_default_config()
    
    def _get_default_config(self) -> dict:
        """获取默认配置"""
        return {
            "app": {"name": "知识图谱平台", "debug": False},
            "server": {"host": "127.0.0.1", "port": 8050},
            "storage": {"data_dir": "./data", "backup_enabled": True}
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            value = value.get(k, {})
        return value if value != {} else default
```

## 6. 部署方案

### 6.1 单机部署

#### 6.1.1 安装步骤
```bash
#!/bin/bash
# install.sh - 安装脚本

echo "开始安装知识图谱可视化与管理平台..."

# 1. 检查Python版本
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.8"
if [[ $(echo "$python_version >= $required_version" | bc -l) -eq 0 ]]; then
    echo "错误: Python版本需要3.8或更高版本"
    exit 1
fi

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 创建数据目录
mkdir -p data/{graphs,ontologies,email_data,configs,logs}

# 5. 初始化配置
cp config/default_config.yaml data/configs/app_config.yaml

# 6. 启动应用
echo "安装完成！运行以下命令启动应用："
echo "source venv/bin/activate"
echo "python app.py"
```

#### 6.1.2 启动脚本
```python
#!/usr/bin/env python3
# app.py - 主应用启动文件

import os
import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.web.app import create_app
from src.utils.config import AppConfig

def main():
    """主函数"""
    # 确保数据目录存在
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # 加载配置
    config = AppConfig()
    
    # 创建并启动应用
    app = create_app(config)
    
    # 启动服务器
    host = config.get("server.host", "127.0.0.1")
    port = config.get("server.port", 8050)
    debug = config.get("app.debug", False)
    
    print(f"启动知识图谱可视化平台...")
    print(f"访问地址: http://{host}:{port}")
    
    app.run_server(host=host, port=port, debug=debug)

if __name__ == "__main__":
    main()
```

### 6.2 配置验证

#### 6.2.1 环境检查脚本
```python
# scripts/check_env.py

import sys
import os
from pathlib import Path
import importlib.util

def check_environment():
    """检查运行环境"""
    print("=== 环境检查报告 ===")
    
    # Python版本检查
    print(f"Python版本: {sys.version}")
    if sys.version_info < (3, 8):
        print("❌ Python版本需要3.8或更高")
        return False
    else:
        print("✅ Python版本符合要求")
    
    # 检查依赖
    required_packages = [
        'dash', 'plotly', 'networkx', 'pandas', 'flask', 'pyyaml'
    ]
    
    missing_packages = []
    for package in required_packages:
        spec = importlib.util.find_spec(package)
        if spec is None:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ 缺失依赖包: {', '.join(missing_packages)}")
        return False
    else:
        print("✅ 所有依赖包已安装")
    
    # 检查数据目录
    data_dir = Path("data")
    if not data_dir.exists():
        print("❌ 数据目录不存在")
        return False
    else:
        print("✅ 数据目录存在")
    
    # 检查配置文件
    config_file = Path("data/configs/app_config.yaml")
    if not config_file.exists():
        print("❌ 配置文件不存在")
        return False
    else:
        print("✅ 配置文件存在")
    
    print("✅ 环境检查通过")
    return True

if __name__ == "__main__":
    check_environment()
```

### 6.3 性能优化

#### 6.3.1 内存管理策略
- **懒加载**：大型图谱按需加载节点和边
- **分页显示**：节点列表分页显示，每页50-100个
- **缓存机制**：最近使用的图谱缓存在内存中
- **垃圾回收**：定期清理不用的对象

#### 6.3.2 渲染优化
- **节点过滤**：只渲染可见区域内的节点（视窗裁剪）
- **LOD技术**：根据缩放级别调整渲染细节
- **异步加载**：大数据量分批次加载
- **WebGL加速**：使用Plotly的WebGL渲染模式

#### 6.3.3 存储优化
- **增量保存**：只保存变更的部分
- **压缩存储**：JSON数据使用gzip压缩
- **索引优化**：为常用查询字段建立索引
- **定期清理**：自动清理过期日志和备份

## 7. 测试策略

### 7.1 测试类型

#### 7.1.1 单元测试
```python
# tests/unit/test_knowledge_graph.py

import unittest
from src.core.knowledge_graph.graph import KnowledgeGraph
from src.core.knowledge_graph.node import KGNode
from src.core.knowledge_graph.edge import KGEdge

class TestKnowledgeGraph(unittest.TestCase):
    
    def setUp(self):
        self.graph = KnowledgeGraph()
        self.node1 = KGNode(id="node1", label="Test Node 1", node_type="test")
        self.node2 = KGNode(id="node2", label="Test Node 2", node_type="test")
        self.edge = KGEdge(id="edge1", source="node1", target="node2", label="Test Edge")
    
    def test_add_node(self):
        """测试添加节点"""
        self.graph.nodes[self.node1.id] = self.node1
        self.assertEqual(len(self.graph.nodes), 1)
        self.assertEqual(self.graph.nodes[self.node1.id].label, "Test Node 1")
    
    def test_add_edge(self):
        """测试添加边"""
        self.graph.nodes[self.node1.id] = self.node1
        self.graph.nodes[self.node2.id] = self.node2
        self.graph.edges[self.edge.id] = self.edge
        
        self.assertEqual(len(self.graph.edges), 1)
        self.assertEqual(self.graph.edges[self.edge.id].label, "Test Edge")
    
    def test_to_networkx(self):
        """测试转换为NetworkX"""
        self.graph.nodes[self.node1.id] = self.node1
        self.graph.nodes[self.node2.id] = self.node2
        self.graph.edges[self.edge.id] = self.edge
        
        nx_graph = self.graph.to_networkx()
        self.assertEqual(nx_graph.number_of_nodes(), 2)
        self.assertEqual(nx_graph.number_of_edges(), 1)

if __name__ == '__main__':
    unittest.main()
```

#### 7.1.2 集成测试
```python
# tests/integration/test_web_app.py

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestWebApp:
    
    @pytest.fixture(scope="class")
    def driver(self):
        driver = webdriver.Chrome()
        driver.implicitly_wait(10)
        yield driver
        driver.quit()
    
    def test_app_loads(self, driver):
        """测试应用加载"""
        driver.get("http://localhost:8050")
        assert "知识图谱" in driver.title
    
    def test_graph_visualization(self, driver):
        """测试图谱可视化"""
        driver.get("http://localhost:8050")
        
        # 等待图谱加载
        wait = WebDriverWait(driver, 10)
        graph_element = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "js-plotly-plot"))
        )
        
        assert graph_element is not None
    
    def test_file_upload(self, driver):
        """测试文件上传"""
        driver.get("http://localhost:8050")
        
        # 切换到数据管理标签
        data_tab = driver.find_element(By.ID, "data-tab")
        data_tab.click()
        
        # 测试文件上传功能
        upload_element = driver.find_element(By.ID, "upload-data")
        assert upload_element is not None

if __name__ == '__main__':
    pytest.main([__file__])
```

### 7.2 测试数据

#### 7.2.1 测试数据集
- **小规模测试**：50节点，100边
- **中等规模测试**：500节点，1000边
- **大规模测试**：5000节点，10000边
- **边界测试**：空图、单节点、环形图

#### 7.2.2 性能基准
- **加载时间**：< 3秒（1000节点以内）
- **渲染时间**：< 5秒（1000节点以内）
- **内存使用**：< 500MB（1000节点以内）
- **文件导入**：< 10秒（1MB JSON文件）

## 8. 监控与维护

### 8.1 运行监控

#### 8.1.1 性能监控
```python
import time
import psutil
import logging

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def monitor_operation(self, operation_name: str):
        """监控操作性能"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
                
                try:
                    result = func(*args, **kwargs)
                    
                    end_time = time.time()
                    end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
                    
                    duration = end_time - start_time
                    memory_delta = end_memory - start_memory
                    
                    self.logger.info(
                        f"{operation_name}: {duration:.2f}s, "
                        f"Memory: {end_memory:.1f}MB (Δ{memory_delta:+.1f}MB)"
                    )
                    
                    return result
                    
                except Exception as e:
                    self.logger.error(f"{operation_name} failed: {e}")
                    raise
            
            return wrapper
        return decorator
```

#### 8.1.2 健康检查
```python
class HealthChecker:
    """健康检查器"""
    
    def __init__(self, config: AppConfig):
        self.config = config
    
    def check_all(self) -> dict:
        """执行所有健康检查"""
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "checks": {
                "storage": self.check_storage(),
                "memory": self.check_memory(),
                "config": self.check_config()
            }
        }
    
    def check_storage(self) -> dict:
        """检查存储状态"""
        data_dir = Path(self.config.get("storage.data_dir", "./data"))
        free_space = psutil.disk_usage(str(data_dir)).free / 1024 / 1024 / 1024  # GB
        
        return {
            "status": "ok" if free_space > 1.0 else "warning",
            "free_space_gb": round(free_space, 2),
            "message": f"{free_space:.1f}GB free space"
        }
    
    def check_memory(self) -> dict:
        """检查内存状态"""
        memory = psutil.virtual_memory()
        return {
            "status": "ok" if memory.percent < 80 else "warning",
            "used_percent": memory.percent,
            "available_gb": round(memory.available / 1024 / 1024 / 1024, 2)
        }
```

### 8.2 维护计划

#### 8.2.1 日常维护任务
- **日志清理**：每日清理过期日志（保留7天）
- **备份验证**：每日验证备份文件完整性
- **性能监控**：每小时记录关键性能指标
- **错误报告**：每日汇总错误日志并发送报告

#### 8.2.2 定期维护任务
- **数据清理**：每周清理临时文件和缓存
- **索引重建**：每月重建数据索引
- **版本检查**：每月检查依赖包更新
- **性能调优**：每季度进行性能分析和优化

## 9. 安全设计

### 9.1 数据安全

#### 9.1.1 本地数据保护
- **文件权限**：配置文件和数据文件设置适当权限（600/644）
- **加密存储**：敏感配置使用加密存储
- **备份加密**：重要备份文件使用AES加密
- **访问控制**：本地文件系统权限控制

#### 9.1.2 输入验证
```python
class InputValidator:
    """输入验证器"""
    
    @staticmethod
    def validate_file_upload(filename: str, content: bytes) -> bool:
        """验证文件上传"""
        # 检查文件大小
        max_size = 100 * 1024 * 1024  # 100MB
        if len(content) > max_size:
            return False
        
        # 检查文件类型
        allowed_extensions = {'.json', '.csv', '.xlsx', '.owl', '.rdf'}
        file_ext = Path(filename).suffix.lower()
        if file_ext not in allowed_extensions:
            return False
        
        return True
    
    @staticmethod
    def validate_node_data(data: dict) -> tuple[bool, str]:
        """验证节点数据"""
        required_fields = {'label', 'type'}
        if not all(field in data for field in required_fields):
            return False, "缺少必要字段"
        
        if not isinstance(data['label'], str) or len(data['label']) == 0:
            return False, "标签不能为空"
        
        if len(data['label']) > 100:
            return False, "标签长度不能超过100字符"
        
        return True, ""
```

### 9.2 错误处理

#### 9.2.1 异常处理策略
```python
class ErrorHandler:
    """错误处理器"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def handle_exception(self, e: Exception, context: str = "") -> dict:
        """统一异常处理"""
        error_info = {
            "error": str(e),
            "type": type(e).__name__,
            "context": context,
            "timestamp": datetime.now().isoformat()
        }
        
        self.logger.error(f"Error in {context}: {e}", exc_info=True)
        
        # 用户友好的错误消息
        user_message = self._get_user_message(e)
        
        return {
            "success": False,
            "error": user_message,
            "details": error_info if os.getenv("DEBUG") else None
        }
    
    def _get_user_message(self, e: Exception) -> str:
        """获取用户友好的错误消息"""
        error_messages = {
            FileNotFoundError: "文件未找到",
            json.JSONDecodeError: "JSON格式错误",
            ValueError: "数据格式错误",
            MemoryError: "内存不足",
            PermissionError: "权限不足"
        }
        
        return error_messages.get(type(e), "发生未知错误")
```

## 10. 扩展性设计

### 10.1 插件架构

#### 10.1.1 插件接口定义
```python
from abc import ABC, abstractmethod

class PluginInterface(ABC):
    """插件接口"""
    
    @abstractmethod
    def get_name(self) -> str:
        """获取插件名称"""
        pass
    
    @abstractmethod
    def get_version(self) -> str:
        """获取插件版本"""
        pass
    
    @abstractmethod
    def initialize(self, config: dict) -> bool:
        """初始化插件"""
        pass
    
    @abstractmethod
    def process_data(self, data: Any) -> Any:
        """处理数据"""
        pass

class PluginManager:
    """插件管理器"""
    
    def __init__(self, plugins_dir: str):
        self.plugins_dir = Path(plugins_dir)
        self.plugins: Dict[str, PluginInterface] = {}
    
    def load_plugins(self):
        """加载所有插件"""
        if not self.plugins_dir.exists():
            return
        
        for plugin_file in self.plugins_dir.glob("*.py"):
            # 动态加载插件
            spec = importlib.util.spec_from_file_location(plugin_file.stem, plugin_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 查找插件类
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, PluginInterface) and 
                    obj != PluginInterface):
                    plugin_instance = obj()
                    self.plugins[plugin_instance.get_name()] = plugin_instance
```

### 10.2 数据源扩展

#### 10.2.1 数据源接口
```python
class DataSourceInterface(ABC):
    """数据源接口"""
    
    @abstractmethod
    def get_name(self) -> str:
        """获取数据源名称"""
        pass
    
    @abstractmethod
    def connect(self, config: dict) -> bool:
        """连接数据源"""
        pass
    
    @abstractmethod
    def fetch_data(self, query: dict) -> List[dict]:
        """获取数据"""
        pass
    
    @abstractmethod
    def disconnect(self):
        """断开连接"""
        pass

class DataSourceManager:
    """数据源管理器"""
    
    def __init__(self):
        self.sources: Dict[str, DataSourceInterface] = {}
    
    def register_source(self, source: DataSourceInterface):
        """注册数据源"""
        self.sources[source.get_name()] = source
    
    def get_data(self, source_name: str, query: dict) -> List[dict]:
        """从指定数据源获取数据"""
        if source_name not in self.sources:
            raise ValueError(f"Unknown data source: {source_name}")
        
        source = self.sources[source_name]
        return source.fetch_data(query)
```

## 11. 总结

本系统概要设计基于《系统设计需求.md》中"### 7.1 技术约束"的要求，成功将企业级分布式架构适配为单体部署架构。通过技术栈映射、模块重构、数据模型优化等手段，实现了：

1. **技术约束适配**：将React+Spring Boot+JanusGraph映射为Dash+Flask+NetworkX
2. **功能完整性**：保留了所有核心功能需求
3. **部署简化**：实现单文件部署，零配置启动
4. **性能优化**：针对单机环境进行专门优化
5. **扩展性设计**：预留插件接口和数据源扩展能力

该设计为后续详细设计和开发提供了完整的技术路线和实现方案。