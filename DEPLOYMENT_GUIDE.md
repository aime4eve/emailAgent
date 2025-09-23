# 外贸询盘知识图谱系统部署指南

## 系统概述

外贸询盘知识图谱系统是一个基于人工智能和知识图谱技术的外贸客户管理和需求分析平台。系统提供客户价值分析、需求洞察、智能推荐等功能，帮助外贸企业提升客户管理效率和业务决策能力。

## 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端界面      │    │   API服务层     │    │   数据存储层    │
│   (React)       │◄──►│   (Flask)       │◄──►│   (ArangoDB)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │   业务服务层    │              │
         └──────────────►│ (知识管理服务)  │◄─────────────┘
                        └─────────────────┘
```

## 环境要求

### 系统要求
- 操作系统：Windows 10/11, macOS 10.15+, Ubuntu 18.04+
- 内存：至少 8GB RAM（推荐 16GB+）
- 存储：至少 20GB 可用空间
- 网络：稳定的互联网连接

### 软件依赖
- Python 3.8+
- Node.js 18+
- ArangoDB 3.9+
- Git

## 安装步骤

### 1. 环境准备

#### 1.1 安装 Python
```bash
# Windows
# 从 https://python.org 下载并安装 Python 3.8+

# macOS
brew install python@3.9

# Ubuntu
sudo apt update
sudo apt install python3.9 python3.9-pip python3.9-venv
```

#### 1.2 安装 Node.js
```bash
# Windows
# 从 https://nodejs.org 下载并安装 Node.js 18+

# macOS
brew install node

# Ubuntu
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

#### 1.3 安装 ArangoDB
```bash
# Windows
# 从 https://arangodb.com/download 下载并安装

# macOS
brew install arangodb

# Ubuntu
curl -OL https://download.arangodb.com/arangodb39/DEBIAN/Release.key
sudo apt-key add - < Release.key
echo 'deb https://download.arangodb.com/arangodb39/DEBIAN/ /' | sudo tee /etc/apt/sources.list.d/arangodb.list
sudo apt-get update
sudo apt-get install arangodb3
```

### 2. 项目部署

#### 2.1 克隆项目
```bash
git clone <repository-url>
cd emailAgent
```

#### 2.2 后端环境配置
```bash
# 创建Python虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安装Python依赖
pip install -r requirements.txt
```

#### 2.3 前端环境配置
```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 构建前端
npm run build
```

### 3. 数据库配置

#### 3.1 启动 ArangoDB
```bash
# Windows
# 通过服务管理器启动 ArangoDB 服务

# macOS
brew services start arangodb

# Ubuntu
sudo systemctl start arangodb3
sudo systemctl enable arangodb3
```

#### 3.2 创建数据库
```bash
# 访问 ArangoDB Web界面
# http://localhost:8529

# 使用默认用户名 root（密码为空或安装时设置的密码）
# 创建数据库：inquiry_knowledge_graph
```

#### 3.3 初始化数据库结构
```bash
# 运行数据库初始化脚本
python -c "from src.shared.database.arango_service import ArangoDBService; ArangoDBService().initialize_collections()"
```

### 4. 环境变量配置

创建 `.env` 文件：
```bash
# 数据库配置
ARANGO_HOST=localhost
ARANGO_PORT=8529
ARANGO_DATABASE=inquiry_knowledge_graph
ARANGO_USERNAME=root
ARANGO_PASSWORD=

# API配置
API_HOST=0.0.0.0
API_PORT=5000
FLASK_ENV=production

# 安全配置
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# 日志配置
LOG_LEVEL=INFO
```

## 运行系统

### 开发环境

#### 启动后端API服务
```bash
# 激活虚拟环境
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 启动API服务
python api_server.py
```

#### 启动前端开发服务器
```bash
cd frontend
npm run dev
```

访问系统：
- 前端界面：http://localhost:5173
- API服务：http://localhost:5000
- ArangoDB管理界面：http://localhost:8529

### 生产环境

#### 使用 Gunicorn 部署API服务
```bash
# 安装 Gunicorn
pip install gunicorn

# 启动服务
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 "src.web.api:create_production_app()"
```

#### 使用 Nginx 部署前端
```bash
# 构建生产版本
cd frontend
npm run build

# 配置 Nginx
sudo nano /etc/nginx/sites-available/emailagent
```

Nginx 配置示例：
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # 前端静态文件
    location / {
        root /path/to/emailAgent/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
    
    # API代理
    location /api/ {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 系统配置

### 数据库优化

#### ArangoDB 性能调优
```javascript
// 在 ArangoDB Web界面中执行
// 创建索引以提升查询性能
db.customers.ensureIndex({ type: "hash", fields: ["email"] });
db.customers.ensureIndex({ type: "hash", fields: ["country"] });
db.customers.ensureIndex({ type: "hash", fields: ["customer_grade"] });
db.inquiries.ensureIndex({ type: "hash", fields: ["customer_id"] });
db.inquiries.ensureIndex({ type: "skiplist", fields: ["created_at"] });
```

### 日志配置

创建日志目录：
```bash
mkdir logs
```

配置日志轮转（Linux）：
```bash
sudo nano /etc/logrotate.d/emailagent
```

```
/path/to/emailAgent/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
}
```

## 监控和维护

### 健康检查
```bash
# 检查API服务状态
curl http://localhost:5000/health

# 检查数据库连接
curl http://localhost:5000/api/info
```

### 系统监控

推荐使用以下工具进行系统监控：
- **应用监控**：Prometheus + Grafana
- **日志监控**：ELK Stack (Elasticsearch, Logstash, Kibana)
- **数据库监控**：ArangoDB自带监控界面

### 备份策略

#### 数据库备份
```bash
# 创建备份
arangodump --server.endpoint tcp://localhost:8529 --server.database inquiry_knowledge_graph --output-directory backup/$(date +%Y%m%d)

# 恢复备份
arangorestore --server.endpoint tcp://localhost:8529 --server.database inquiry_knowledge_graph --input-directory backup/20240115
```

#### 自动备份脚本
```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DATABASE="inquiry_knowledge_graph"

# 创建备份目录
mkdir -p $BACKUP_DIR/$DATE

# 备份数据库
arangodump --server.endpoint tcp://localhost:8529 \
           --server.database $DATABASE \
           --output-directory $BACKUP_DIR/$DATE

# 压缩备份
tar -czf $BACKUP_DIR/backup_$DATE.tar.gz -C $BACKUP_DIR $DATE
rm -rf $BACKUP_DIR/$DATE

# 清理旧备份（保留30天）
find $BACKUP_DIR -name "backup_*.tar.gz" -mtime +30 -delete

echo "备份完成: backup_$DATE.tar.gz"
```

## 故障排除

### 常见问题

#### 1. 数据库连接失败
```bash
# 检查ArangoDB服务状态
sudo systemctl status arangodb3

# 检查端口占用
netstat -tlnp | grep 8529

# 查看ArangoDB日志
sudo journalctl -u arangodb3 -f
```

#### 2. API服务启动失败
```bash
# 检查Python环境
python --version
pip list

# 检查端口占用
netstat -tlnp | grep 5000

# 查看详细错误信息
python api_server.py
```

#### 3. 前端构建失败
```bash
# 清理缓存
npm cache clean --force
rm -rf node_modules package-lock.json
npm install

# 检查Node.js版本
node --version
npm --version
```

#### 4. 内存不足
```bash
# 监控系统资源
top
htop
free -h

# 调整ArangoDB内存限制
# 编辑 /etc/arangodb3/arangod.conf
# 添加或修改：
# [rocksdb]
# block-cache-size = 2GB
```

### 性能优化

#### 1. 数据库优化
- 合理设计索引
- 定期清理无用数据
- 调整缓存大小
- 使用分片（大数据量时）

#### 2. API服务优化
- 增加Worker进程数
- 启用缓存机制
- 优化查询语句
- 使用连接池

#### 3. 前端优化
- 启用代码分割
- 使用CDN加速
- 压缩静态资源
- 启用浏览器缓存

## 安全配置

### 1. 数据库安全
```bash
# 设置ArangoDB密码
arangodb --server.authentication true

# 创建专用用户
# 在ArangoDB Web界面中创建应用专用用户
```

### 2. API安全
- 启用HTTPS
- 配置CORS策略
- 实施API限流
- 添加身份验证

### 3. 系统安全
- 定期更新系统和依赖
- 配置防火墙
- 启用日志审计
- 实施访问控制

## 扩展部署

### Docker 部署

创建 `docker-compose.yml`：
```yaml
version: '3.8'

services:
  arangodb:
    image: arangodb:3.9
    environment:
      ARANGO_ROOT_PASSWORD: your-password
    ports:
      - "8529:8529"
    volumes:
      - arangodb_data:/var/lib/arangodb3
      - arangodb_apps:/var/lib/arangodb3-apps

  api:
    build: .
    ports:
      - "5000:5000"
    environment:
      - ARANGO_HOST=arangodb
      - ARANGO_PASSWORD=your-password
    depends_on:
      - arangodb

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - api

volumes:
  arangodb_data:
  arangodb_apps:
```

### Kubernetes 部署

参考 `k8s/` 目录下的配置文件进行Kubernetes部署。

## 支持和维护

### 技术支持
- 查看系统日志：`tail -f logs/api.log`
- 运行集成测试：`python test_integration.py`
- 查看API文档：访问 `/api/info` 端点

### 版本更新
1. 备份当前数据
2. 更新代码
3. 安装新依赖
4. 运行数据库迁移
5. 重启服务
6. 验证功能

### 联系方式
如需技术支持，请联系开发团队或查看项目文档。

---

**注意**：本部署指南适用于系统版本 v1.0.0，不同版本可能存在差异，请参考对应版本的文档。