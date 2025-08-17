# 知识图谱可视化与管理平台

一个基于Python和Dash框架的知识图谱可视化与管理平台，提供直观的图谱展示、交互式编辑和完整的数据管理功能。

## 📋 目录

- [项目简介](#项目简介)
- [功能特性](#功能特性)
- [技术架构](#技术架构)
- [快速开始](#快速开始)
- [安装说明](#安装说明)
- [使用指南](#使用指南)
- [项目结构](#项目结构)
- [API文档](#api文档)
- [开发指南](#开发指南)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

## 🚀 项目简介

知识图谱可视化与管理平台是一个专为数据分析师、研究人员和知识工程师设计的Web应用程序。它提供了一个直观的界面来创建、编辑、可视化和管理知识图谱，支持多种数据格式的导入导出，并包含完整的本体管理功能。

### 核心价值

- **🎨 可视化展示**：直观展示复杂的知识关系网络
- **✏️ 交互式编辑**：支持实时的图谱编辑和修改
- **🔄 数据互通**：支持多种格式的数据导入导出
- **🏗️ 本体管理**：提供完整的知识本体构建和管理功能
- **👥 易于使用**：友好的用户界面，降低使用门槛

## ✨ 功能特性

### 核心功能

- **知识图谱可视化**
  - 多种布局算法（弹簧布局、圆形布局、层次布局）
  - 自定义节点和边的样式（颜色、大小、形状）
  - 缩放、平移、选择等基本交互操作
  - 节点和边的详细信息展示

- **数据管理**
  - 支持JSON、CSV、Excel格式的数据导入
  - 多种格式的数据导出
  - 文件上传和下载功能
  - 数据格式验证和错误提示

- **知识本体管理**
  - 本体类层次结构管理
  - 关系类型定义和管理
  - 属性定义和约束设置
  - 本体可视化展示
  - 本体导出（OWL、RDF格式）

- **搜索和筛选**
  - 节点标签搜索
  - 节点类型筛选
  - 属性值筛选
  - 搜索结果高亮显示

### 高级功能

- **图谱编辑**
  - 节点的添加、删除、修改
  - 边的创建、删除、编辑
  - 拖拽操作支持
  - 批量选择和操作

- **统计分析**
  - 图谱统计信息展示
  - 节点度分布分析
  - 连通性分析

## 🏗️ 技术架构

### 技术栈

- **前端框架**: Dash (基于React)
- **后端语言**: Python 3.8+
- **可视化库**: Plotly
- **图算法库**: NetworkX
- **数据处理**: Pandas
- **配置管理**: JSON配置文件

### 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                    Web Browser (前端)                        │
├─────────────────────────────────────────────────────────────┤
│                    Dash Framework                           │
├─────────────────────────────────────────────────────────────┤
│                    应用层 (Application Layer)                │
├─────────────────────────────────────────────────────────────┤
│                    业务逻辑层 (Business Layer)               │
├─────────────────────────────────────────────────────────────┤
│                    数据层 (Data Layer)                      │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 快速开始

### 环境要求

- Python 3.8 或更高版本
- 4GB 以上内存（推荐）
- 1GB 以上可用磁盘空间

### 快速启动

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd emailAgent
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **启动应用**
   ```bash
   python dev_start.py
   ```

4. **访问应用**
   
   打开浏览器访问：http://127.0.0.1:8050

## 📦 安装说明

### 使用pip安装

```bash
# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 依赖包说明

主要依赖包包括：
- `dash`: Web应用框架
- `plotly`: 数据可视化库
- `networkx`: 图算法库
- `pandas`: 数据处理库
- `numpy`: 数值计算库

## 📖 使用指南

### 基本操作

1. **创建知识图谱**
   - 点击"图谱管理"选项卡
   - 使用"添加节点"和"添加边"功能
   - 设置节点和边的属性

2. **导入数据**
   - 点击"数据导入"选项卡
   - 选择支持的文件格式（JSON、CSV、Excel）
   - 上传文件并验证数据格式

3. **可视化展示**
   - 在"图谱可视化"选项卡查看图谱
   - 选择不同的布局算法
   - 调整可视化参数

4. **本体管理**
   - 在"本体管理"选项卡管理本体结构
   - 定义类层次和关系类型
   - 导出本体文件

### 数据格式

#### JSON格式示例
```json
{
  "nodes": [
    {
      "id": "node_1",
      "label": "张三",
      "type": "person",
      "properties": {
        "age": 30,
        "department": "技术部"
      }
    }
  ],
  "edges": [
    {
      "id": "edge_1",
      "source_id": "node_1",
      "target_id": "node_2",
      "label": "工作于",
      "type": "works_at"
    }
  ]
}
```

#### CSV格式示例
**节点文件 (nodes.csv)**:
```csv
id,label,type,attr_age,attr_department
node_1,张三,person,30,技术部
node_2,ABC公司,organization,,
```

**边文件 (edges.csv)**:
```csv
source,target,type,label
node_1,node_2,works_at,工作于
```

## 📁 项目结构

```
emailAgent/
├── src/                          # 源代码目录
│   ├── knowledge_graph/          # 知识图谱核心模块
│   │   ├── graph.py             # 知识图谱主类
│   │   ├── node.py              # 节点类
│   │   ├── edge.py              # 边类
│   │   ├── ontology.py          # 本体类
│   │   └── ontology_generator.py # 本体生成器
│   ├── web_app/                 # Web应用模块
│   │   ├── web_app_main.py      # 主应用入口
│   │   ├── interaction_handler.py # 交互处理器
│   │   ├── ontology_components.py # 本体组件
│   │   └── assets/              # 静态资源
│   ├── visualization/           # 可视化模块
│   │   └── plotly_graph.py      # Plotly图谱可视化
│   └── utils/                   # 工具模块
│       ├── config.py            # 配置管理
│       ├── data_loader.py       # 数据加载器
│       └── import_export.py     # 导入导出处理
├── data/                        # 数据目录
│   └── sample_data.json         # 示例数据
├── docs/                        # 文档目录
│   ├── 系统设计需求.md           # 系统需求文档
│   └── 系统概要设计.md           # 系统设计文档
├── tests/                       # 测试目录
├── config/                      # 配置目录
├── requirements.txt             # 依赖包列表
├── dev_start.py                # 开发启动脚本
├── main_entry.py               # 主入口脚本
└── README.md                   # 项目说明文档
```

## 📚 API文档

### 核心类接口

#### KnowledgeGraph类
```python
class KnowledgeGraph:
    def add_node(self, node: Node) -> None:
        """添加节点到图中"""
    
    def add_edge(self, edge: Edge) -> None:
        """添加边到图中"""
    
    def get_node(self, node_id: str) -> Optional[Node]:
        """根据ID获取节点"""
    
    def search_nodes(self, query: str) -> List[Node]:
        """搜索节点"""
```

#### 数据导入导出接口
```python
class DataImportExport:
    def export_to_json(self, kg: KnowledgeGraph) -> str:
        """导出为JSON格式"""
    
    def import_from_json(self, source: Union[str, Dict, io.StringIO]) -> KnowledgeGraph:
        """从JSON格式导入"""
    
    def export_to_csv(self, kg: KnowledgeGraph, nodes_file: str, edges_file: str) -> Tuple[str, str]:
        """导出为CSV格式"""
```

## 🛠️ 开发指南

### 开发环境设置

1. **安装开发依赖**
   ```bash
   pip install -r requirements.txt
   pip install pytest pytest-cov black flake8
   ```

2. **代码格式化**
   ```bash
   black src/
   flake8 src/
   ```

3. **运行测试**
   ```bash
   pytest tests/
   ```

### 添加新功能

1. 在相应的模块目录下创建新文件
2. 实现功能逻辑
3. 添加单元测试
4. 更新文档

### 调试技巧

- 使用`debug=True`启动Dash应用进行调试
- 查看浏览器控制台的错误信息
- 使用Python调试器进行断点调试

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 如何贡献

1. **Fork项目**
2. **创建功能分支** (`git checkout -b feature/AmazingFeature`)
3. **提交更改** (`git commit -m 'Add some AmazingFeature'`)
4. **推送到分支** (`git push origin feature/AmazingFeature`)
5. **创建Pull Request**

### 贡献类型

- 🐛 Bug修复
- ✨ 新功能开发
- 📝 文档改进
- 🎨 UI/UX改进
- ⚡ 性能优化
- 🧪 测试覆盖

### 代码规范

- 遵循PEP 8代码风格
- 添加适当的注释和文档字符串
- 编写单元测试
- 保持代码简洁和可读性

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙋‍♂️ 支持与反馈

如果您在使用过程中遇到问题或有改进建议，请通过以下方式联系我们：

- 📧 邮件：[your-email@example.com]
- 🐛 问题反馈：[GitHub Issues]
- 💬 讨论：[GitHub Discussions]

## 🔗 相关链接

- [系统设计需求文档](docs/系统设计需求.md)
- [系统概要设计文档](docs/系统概要设计.md)
- [Dash官方文档](https://dash.plotly.com/)
- [Plotly官方文档](https://plotly.com/python/)
- [NetworkX官方文档](https://networkx.org/)

---

**版本**: 1.0.0  
**最后更新**: 2024年12月  
**维护者**: 开发团队

感谢您使用知识图谱可视化与管理平台！🎉