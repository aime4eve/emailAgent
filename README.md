# 外贸知识图谱洞察系统

## 系统概述

外贸知识图谱洞察系统是一个基于知识图谱技术的智能分析平台，专门用于外贸业务场景。系统通过分析邮件、文档等文本数据，构建知识图谱，并提供客户洞察、产品分析、市场洞察和风险预警等功能。

## 系统架构

### 基础能力层
- **知识抽取引擎**: 从文本中抽取实体、关系和属性
- **图谱构建引擎**: 构建和管理知识图谱
- **图算法引擎**: 执行图分析算法（PageRank、社区发现等）
- **可视化引擎**: 生成图表和可视化界面

### 业务应用层
- **客户洞察分析**: 客户需求分析、行为预测、价值评估
- **产品需求分析**: 产品特征分析、需求预测、竞争分析
- **市场洞察分析**: 市场趋势分析、机会识别、竞争格局
- **风险预警系统**: 风险识别、评估和预警

### 用户交互层
- **可视化仪表板**: 交互式数据可视化
- **分析报告**: 自动生成分析报告
- **预警通知**: 实时风险预警
- **API接口**: RESTful API服务

## 技术栈

- **编程语言**: Python 3.8+
- **Web框架**: Flask
- **图数据库**: Neo4j
- **缓存**: Redis
- **可视化**: Plotly, NetworkX
- **机器学习**: scikit-learn, transformers
- **文本处理**: spaCy, jieba

## 安装部署

### 环境要求

- Python 3.8 或更高版本
- Neo4j 4.0+ (可选)
- Redis 6.0+ (可选)

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd emailAgent
```

2. **安装Python依赖**
```bash
pip install -r requirements.txt
```

3. **安装可选依赖**
```bash
# 安装Neo4j Python驱动
pip install neo4j

# 安装Redis Python客户端
pip install redis

# 安装可视化库
pip install plotly networkx matplotlib seaborn

# 安装机器学习库
pip install scikit-learn transformers torch

# 安装文本处理库
pip install spacy jieba
```

4. **配置系统**

编辑 `insights_config.py` 文件，配置数据库连接等参数：

```python
# Neo4j配置
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"

# Redis配置
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
```

### 数据库设置

#### Neo4j设置（可选）

1. 下载并安装Neo4j Desktop
2. 创建新的数据库实例
3. 启动数据库服务
4. 在配置文件中设置连接参数

#### Redis设置（可选）

1. 下载并安装Redis
2. 启动Redis服务
3. 在配置文件中设置连接参数

## 使用指南

### 快速开始

1. **启动演示系统**
```bash
python start_insights_system.py
```

2. **运行系统测试**
```bash
python test_insights_system.py
```

3. **启动API服务器**
```bash
python -c "from start_insights_system import start_api_server; start_api_server()"
```

### API接口使用

系统提供RESTful API接口，默认运行在 `http://localhost:5000`

#### 主要API端点

- `GET /api/v1/health` - 健康检查
- `POST /api/v1/extract` - 知识抽取
- `POST /api/v1/graph/build` - 构建图谱
- `GET /api/v1/insights/customer` - 客户洞察
- `GET /api/v1/insights/product` - 产品分析
- `GET /api/v1/insights/market` - 市场洞察
- `GET /api/v1/risk/analysis` - 风险分析
- `POST /api/v1/visualize` - 生成可视化

#### API使用示例

```python
import requests

# 健康检查
response = requests.get('http://localhost:5000/api/v1/health')
print(response.json())

# 知识抽取
data = {
    'text': '我们需要高质量的LED灯具产品，要求符合CE认证标准。',
    'language': 'zh'
}
response = requests.post('http://localhost:5000/api/v1/extract', json=data)
print(response.json())
```

### 功能模块使用

#### 1. 知识抽取

```python
from insights.engines.knowledge_extractor import KnowledgeExtractor

extractor = KnowledgeExtractor()
result = extractor.extract_from_text("示例文本")
print(f"抽取到 {len(result.entities)} 个实体")
```

#### 2. 客户洞察

```python
from insights.business.customer_insights import CustomerInsights

customer_insights = CustomerInsights()
needs = customer_insights.analyze_customer_needs(customer_id="CUST001")
print(f"发现 {len(needs)} 个客户需求")
```

#### 3. 风险分析

```python
from insights.business.risk_analysis import RiskAnalysis

risk_analysis = RiskAnalysis()
risks = risk_analysis.identify_risk_factors(customer_id="CUST001")
print(f"识别到 {len(risks)} 个风险因子")
```

#### 4. 可视化

```python
from insights.engines.visualizer import Visualizer

visualizer = Visualizer()
data = {'x': [1, 2, 3], 'y': [10, 20, 30]}
chart = visualizer.create_business_chart('line', data, '示例图表')
print(f"生成图表: {chart.title}")
```

## 系统测试

### 运行测试

```bash
# 运行完整测试套件
python test_insights_system.py

# 运行特定模块测试
python -c "from test_insights_system import InsightsSystemTester; tester = InsightsSystemTester(); tester.test_knowledge_extraction()"
```

### 测试覆盖

系统测试包括以下模块：
- 配置管理测试
- 数据库连接测试
- 知识抽取引擎测试
- 图谱构建引擎测试
- 图算法引擎测试
- 可视化引擎测试
- 业务分析模块测试
- API接口测试
- 端到端工作流程测试

## 项目结构

```
emailAgent/
├── insights/                    # 主要代码目录
│   ├── __init__.py
│   ├── core/                   # 核心模块
│   │   ├── __init__.py
│   │   ├── database_manager.py # 数据库管理
│   │   └── graph_manager.py    # 图谱管理
│   ├── engines/                # 引擎模块
│   │   ├── __init__.py
│   │   ├── knowledge_extractor.py  # 知识抽取引擎
│   │   ├── graph_builder.py        # 图谱构建引擎
│   │   ├── graph_algorithms.py     # 图算法引擎
│   │   └── visualizer.py           # 可视化引擎
│   ├── business/               # 业务模块
│   │   ├── __init__.py
│   │   ├── customer_insights.py    # 客户洞察
│   │   ├── product_analysis.py     # 产品分析
│   │   ├── market_insights.py      # 市场洞察
│   │   └── risk_analysis.py        # 风险分析
│   ├── api/                    # API模块
│   │   ├── __init__.py
│   │   └── insights_api.py         # API接口
│   └── utils/                  # 工具模块
│       ├── __init__.py
│       ├── text_processor.py       # 文本处理
│       ├── data_validator.py       # 数据验证
│       └── performance_monitor.py  # 性能监控
├── insights_config.py          # 系统配置
├── start_insights_system.py    # 启动脚本
├── test_insights_system.py     # 测试脚本
├── requirements.txt            # 依赖列表
└── README.md                   # 说明文档
```

## 配置说明

### 主要配置项

```python
# 数据库配置
DATABASE_CONFIG = {
    'neo4j': {
        'uri': 'bolt://localhost:7687',
        'user': 'neo4j',
        'password': 'password'
    },
    'redis': {
        'host': 'localhost',
        'port': 6379,
        'db': 0
    }
}

# API配置
API_CONFIG = {
    'host': '0.0.0.0',
    'port': 5000,
    'debug': True
}

# 模型配置
MODEL_CONFIG = {
    'knowledge_extraction': {
        'model_name': 'bert-base-chinese',
        'max_length': 512
    },
    'text_processing': {
        'language': 'auto',
        'remove_stopwords': True
    }
}
```

## 性能优化

### 缓存策略

- 使用Redis缓存频繁查询的结果
- 实现多级缓存机制
- 设置合理的缓存过期时间

### 数据库优化

- 为Neo4j图数据库创建适当的索引
- 优化Cypher查询语句
- 使用批量操作提高写入性能

### 算法优化

- 使用并行处理提高计算效率
- 实现增量更新机制
- 优化图算法的内存使用

## 故障排除

### 常见问题

1. **模块导入错误**
   - 检查Python路径设置
   - 确认所有依赖已正确安装

2. **数据库连接失败**
   - 检查数据库服务是否启动
   - 验证连接配置参数

3. **API服务启动失败**
   - 检查端口是否被占用
   - 查看错误日志信息

4. **性能问题**
   - 检查系统资源使用情况
   - 优化数据库查询
   - 调整缓存策略

### 日志查看

系统日志保存在 `insights_system.log` 文件中，可以通过以下方式查看：

```bash
# 查看最新日志
tail -f insights_system.log

# 搜索错误日志
grep "ERROR" insights_system.log
```

## 扩展开发

### 添加新的业务模块

1. 在 `insights/business/` 目录下创建新模块
2. 继承基础类并实现必要方法
3. 在API中添加相应端点
4. 编写单元测试

### 添加新的数据源

1. 在 `insights/core/` 中扩展数据管理器
2. 实现数据连接和查询方法
3. 更新配置文件
4. 测试数据连接

### 自定义可视化

1. 在 `insights/engines/visualizer.py` 中添加新图表类型
2. 实现数据转换和渲染逻辑
3. 更新API接口
4. 添加前端展示

## 版本历史

- **v1.0.0** (2024-01-01)
  - 初始版本发布
  - 实现基础功能模块
  - 提供API接口
  - 完成系统测试

## 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。

## 联系方式

如有问题或建议，请通过以下方式联系：

- 邮箱: support@example.com
- 项目地址: https://github.com/example/emailAgent
- 文档地址: https://docs.example.com

## 致谢

感谢所有为本项目做出贡献的开发者和用户。