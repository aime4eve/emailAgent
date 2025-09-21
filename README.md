# 邮件智能代理知识图谱系统

一个基于React+TypeScript前端和Flask后端的智能知识图谱系统，专门用于邮件数据的知识抽取、本体管理和图谱可视化。

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

邮件智能代理知识图谱系统是一个现代化的全栈Web应用，专为处理和分析邮件数据而设计。系统集成了先进的自然语言处理技术，能够从邮件内容中自动抽取实体、关系和语义信息，构建结构化的知识图谱。

### 核心价值

- **🤖 智能抽取**：基于spaCy和机器学习的知识自动抽取
- **🎨 可视化展示**：直观展示复杂的知识关系网络
- **📧 邮件专用**：专门针对邮件数据优化的处理流程
- **🏗️ 本体管理**：完整的知识本体构建和管理功能
- **⚡ 现代技术**：React+TypeScript前端，Flask后端

## ✨ 功能特性

### 知识抽取功能

- **文本知识抽取**
  - 实体识别（人名、组织、地点、时间等）
  - 关系抽取（工作关系、地理关系等）
  - 语义消解和实体对齐
  - 机器学习增强处理

- **文件处理**
  - 支持多种文件格式（TXT、PDF、DOC等）
  - 批量文件处理
  - 文件内容解析和预处理

### 前端界面功能

- **知识抽取页面**
  - 文本输入和实时抽取
  - 文件上传和批量处理
  - 抽取结果可视化展示

- **图谱可视化**
  - 交互式图谱展示
  - 多种布局算法
  - 节点和边的详细信息
  - 缩放、平移、搜索功能

- **本体管理**
  - 本体类层次结构管理
  - 关系类型定义
  - 属性约束设置
  - 本体导出功能

- **统计分析**
  - 抽取统计信息
  - 图谱分析报告
  - 性能监控面板

## 🏗️ 技术架构

### 技术栈

**前端**
- React 18 + TypeScript
- Ant Design UI组件库
- Recharts 图表库
- Axios HTTP客户端
- Vite 构建工具

**后端**
- Flask Web框架
- spaCy 自然语言处理
- scikit-learn 机器学习
- Flask-CORS 跨域支持
- Werkzeug 文件处理

### 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                React + TypeScript 前端                      │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │ 知识抽取页面 │ │ 图谱可视化   │ │ 本体管理     │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
├─────────────────────────────────────────────────────────────┤
│                     HTTP API 接口                          │
├─────────────────────────────────────────────────────────────┤
│                    Flask 后端服务                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │ 知识抽取服务 │ │ 实体识别     │ │ 关系抽取     │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
├─────────────────────────────────────────────────────────────┤
│                NLP处理层 (spaCy + ML)                      │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 快速开始

### 环境要求

- Python 3.8+ 
- Node.js 16+
- 4GB+ 内存（推荐）
- 2GB+ 可用磁盘空间

### 快速启动

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd emailAgent
   ```

2. **后端设置**
   ```bash
   # 安装Python依赖
   pip install -r requirements.txt
   
   # 启动后端服务
   python src/web/app.py
   ```

3. **前端设置**
   ```bash
   # 进入前端目录
   cd frontend
   
   # 安装依赖
   npm install
   
   # 启动前端开发服务器
   npm run dev
   ```

4. **访问应用**
   - 前端：http://localhost:3000
   - 后端API：http://localhost:5000

## 📦 安装说明

### 后端安装

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

# 下载spaCy中文模型
python -m spacy download zh_core_web_sm
```

### 前端安装

```bash
cd frontend
npm install
```

### 主要依赖说明

**后端依赖**：
- `flask`: Web应用框架
- `spacy`: 自然语言处理库
- `scikit-learn`: 机器学习库
- `flask-cors`: 跨域资源共享

**前端依赖**：
- `react`: 前端框架
- `typescript`: 类型系统
- `antd`: UI组件库
- `recharts`: 图表库

## 📖 使用指南

### 知识抽取

1. **文本抽取**
   - 在知识抽取页面输入文本
   - 点击"抽取知识"按钮
   - 查看抽取的实体和关系结果

2. **文件抽取**
   - 选择"文件上传"选项卡
   - 上传支持的文件格式
   - 等待处理完成并查看结果

### 图谱可视化

1. **查看图谱**
   - 切换到"图谱可视化"页面
   - 浏览交互式知识图谱
   - 使用搜索和筛选功能

2. **图谱操作**
   - 拖拽节点调整位置
   - 点击节点查看详细信息
   - 使用缩放和平移功能

### 本体管理

1. **管理本体**
   - 进入"本体管理"页面
   - 查看和编辑本体结构
   - 定义新的类和关系

2. **导出本体**
   - 选择导出格式
   - 下载本体文件

## 📁 项目结构

```
emailAgent/
├── frontend/                     # React前端应用
│   ├── src/
│   │   ├── components/          # React组件
│   │   ├── pages/              # 页面组件
│   │   ├── services/           # API服务
│   │   ├── types/              # TypeScript类型定义
│   │   └── utils/              # 工具函数
│   ├── public/                 # 静态资源
│   └── package.json            # 前端依赖配置
├── src/                        # Python后端代码
│   ├── web/                    # Flask Web应用
│   │   └── app.py             # 主应用文件
│   ├── knowledge_management/   # 知识管理模块
│   │   ├── application/       # 应用服务层
│   │   ├── domain/            # 领域模型层
│   │   └── infrastructure/    # 基础设施层
│   └── utils/                 # 工具模块
├── data/                      # 数据目录
├── docs/                      # 文档目录
├── tests/                     # 测试目录
├── requirements.txt           # Python依赖
└── README.md                  # 项目说明
```

## 📚 API文档

### 知识抽取接口

#### POST /api/extract
从文本中抽取知识

**请求体**：
```json
{
  "text": "张三在北京的ABC公司工作。"
}
```

**响应**：
```json
{
  "success": true,
  "entities": [
    {
      "text": "张三",
      "label": "PERSON",
      "start": 0,
      "end": 2
    }
  ],
  "relations": [
    {
      "head": "张三",
      "relation": "工作于",
      "tail": "ABC公司"
    }
  ]
}
```

#### POST /api/extract/file
从文件中抽取知识

**请求**：multipart/form-data格式，包含文件

**响应**：与文本抽取相同格式

#### GET /api/health
健康检查接口

**响应**：
```json
{
  "status": "healthy",
  "services": {
    "nlp_service": "available",
    "ml_service": "available"
  }
}
```

## 🛠️ 开发指南

### 开发环境设置

1. **后端开发**
   ```bash
   # 安装开发依赖
   pip install -r requirements.txt
   pip install pytest pytest-cov black flake8
   
   # 代码格式化
   black src/
   flake8 src/
   
   # 运行测试
   pytest tests/
   ```

2. **前端开发**
   ```bash
   cd frontend
   
   # 安装依赖
   npm install
   
   # 启动开发服务器
   npm run dev
   
   # 类型检查
   npm run type-check
   
   # 代码检查
   npm run lint
   ```

### 添加新功能

1. **后端功能**
   - 在相应模块添加服务类
   - 在Flask应用中添加路由
   - 编写单元测试
   - 更新API文档

2. **前端功能**
   - 创建新的React组件
   - 添加TypeScript类型定义
   - 集成API服务
   - 编写组件测试

### 调试技巧

- **后端调试**：使用Flask的debug模式
- **前端调试**：使用浏览器开发者工具
- **API测试**：使用Postman或curl命令
- **日志查看**：检查控制台输出和日志文件

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

- **Python**：遵循PEP 8代码风格
- **TypeScript**：使用ESLint和Prettier
- **提交信息**：使用约定式提交格式
- **测试**：保持良好的测试覆盖率

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙋‍♂️ 支持与反馈

如果您在使用过程中遇到问题或有改进建议，请通过以下方式联系我们：

- 🐛 问题反馈：[GitHub Issues]
- 💬 讨论：[GitHub Discussions]
- 📧 邮件联系：[your-email@example.com]

## 🔗 相关链接

- [Flask官方文档](https://flask.palletsprojects.com/)
- [React官方文档](https://reactjs.org/)
- [spaCy官方文档](https://spacy.io/)
- [Ant Design官方文档](https://ant.design/)
- [TypeScript官方文档](https://www.typescriptlang.org/)

---

**版本**: 2.0.0  
**最后更新**: 2024年12月  
**维护者**: 开发团队

感谢您使用邮件智能代理知识图谱系统！🎉