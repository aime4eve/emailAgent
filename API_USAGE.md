# 知识抽取API使用说明

## 概述

知识抽取API已成功集成到Flask Web应用中，提供了强大的实体关系抽取功能。系统能够从文本和文件中自动识别实体（人名、地名、机构名等）和它们之间的关系。

## API端点

### 1. 服务状态检查

#### GET `/`
获取服务基本信息

**响应示例：**
```json
{
  "message": "欢迎使用邮件智能代理系统",
  "version": "1.0.0",
  "status": "running"
}
```

#### GET `/api/health`
健康检查接口

**响应示例：**
```json
{
  "status": "healthy",
  "timestamp": "1758471807.4343123"
}
```

### 2. 文本知识抽取

#### POST `/api/extract`
从文本中抽取实体和关系

**请求参数：**
```json
{
  "text": "要分析的文本内容",
  "enable_ml_enhancement": true,  // 可选，是否启用ML增强
  "custom_entity_types": {        // 可选，自定义实体类型
    "PROJECT": ["项目Alpha", "项目Beta"]
  }
}
```

**响应示例：**
```json
{
  "success": true,
  "entities": [
    {
      "id": "entity_1",
      "text": "苹果公司",
      "type": "ORG",
      "confidence": 0.9,
      "start_pos": 0,
      "end_pos": 4,
      "properties": {}
    }
  ],
  "relations": [
    {
      "id": "relation_1",
      "source": {
        "id": "entity_1",
        "text": "苹果公司"
      },
      "target": {
        "id": "entity_2",
        "text": "美国"
      },
      "type": "LOCATED_IN",
      "confidence": 0.8,
      "evidence": "苹果公司是一家美国科技公司",
      "properties": {}
    }
  ],
  "statistics": {
    "entity_count": 2,
    "relation_count": 1,
    "entity_types": {
      "ORG": 1,
      "LOC": 1
    },
    "relation_types": {
      "LOCATED_IN": 1
    },
    "text_length": 45
  },
  "processing_time": 0.893,
  "ml_enhancement": {
    "enabled": false
  },
  "metadata": {
    "extraction_time": 0.033,
    "custom_entity_types": {},
    "timestamp": "2025-09-22 00:24:08"
  }
}
```

### 3. 文件知识抽取

#### POST `/api/extract/file`
从上传的文件中抽取实体和关系

**请求参数：**
- `file`: 上传的文件（支持PDF、Word、Excel、TXT等格式）
- `enable_ml_enhancement`: 可选，是否启用ML增强（form参数）

**响应格式：** 与文本抽取类似，额外包含文件信息

## 使用示例

### PowerShell示例

```powershell
# 1. 健康检查
Invoke-RestMethod -Uri "http://localhost:5000/api/health" -Method GET

# 2. 文本知识抽取
$testData = @{
    text = "苹果公司是一家美国科技公司，蒂姆·库克是CEO。"
    enable_ml_enhancement = $false
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/extract" -Method POST -Body $testData -ContentType "application/json"

# 3. 文件上传抽取（需要实际文件）
# $form = @{
#     file = Get-Item "test.txt"
#     enable_ml_enhancement = "false"
# }
# Invoke-RestMethod -Uri "http://localhost:5000/api/extract/file" -Method POST -Form $form
```

### Python示例

```python
import requests
import json

# 文本知识抽取
url = "http://localhost:5000/api/extract"
data = {
    "text": "张三在北京大学工作，他是计算机科学系的教授。",
    "enable_ml_enhancement": False
}

response = requests.post(url, json=data)
result = response.json()

print(f"实体数量: {result['statistics']['entity_count']}")
print(f"关系数量: {result['statistics']['relation_count']}")
```

### curl示例

```bash
# 健康检查
curl http://localhost:5000/api/health

# 文本知识抽取
curl -X POST http://localhost:5000/api/extract \
  -H "Content-Type: application/json" \
  -d '{"text":"苹果公司是一家美国科技公司，蒂姆·库克是CEO。"}'
```

## 实体类型说明

系统支持以下实体类型：

- **PERSON**: 人名
- **ORG**: 组织机构名
- **LOC**: 地点名称
- **TIME**: 时间表达式
- **EMAIL**: 邮箱地址
- **PHONE**: 电话号码
- **URL**: 网址链接
- **MONEY**: 金额
- **PERCENT**: 百分比

## 关系类型说明

系统支持以下关系类型：

- **WORK_FOR**: 工作关系
- **LOCATED_IN**: 位置关系
- **PART_OF**: 从属关系
- **FOUNDED_BY**: 创立关系
- **MANAGES**: 管理关系
- **COLLABORATES_WITH**: 合作关系

## 测试结果

根据测试结果，系统表现如下：

### ✅ 成功功能
- 中文文本实体抽取：能够识别人名、地名、机构名等
- 关系抽取：能够识别实体间的语义关系
- API响应格式：完整的JSON响应包含统计信息
- 处理时间：中文文本处理速度快（0.004-0.893秒）

### ⚠️ 注意事项
- 英文文本抽取：当前配置下英文实体识别效果有限
- NLP模型：可能需要安装额外的语言模型以提升效果
- ML增强：需要完整的知识图谱结构才能发挥最佳效果

## 启动服务

```bash
# 启动Web服务
cd d:\emailAgent
python src/web/app.py

# 服务将在以下地址启动：
# http://localhost:5000
# http://127.0.0.1:5000
```

## 错误处理

系统提供详细的错误信息：

- **400**: 请求参数错误
- **500**: 服务内部错误
- **503**: 服务不可用

每个错误响应都包含具体的错误信息和建议。

## 性能优化建议

1. **批量处理**: 对于大量文本，建议使用批量处理接口
2. **缓存**: 相同文本的重复请求会被缓存
3. **异步处理**: 大文件处理建议使用异步方式
4. **模型优化**: 可以根据具体需求调整NLP模型配置

## 扩展功能

系统架构支持以下扩展：

- 自定义实体类型和关系类型
- 多语言支持
- 深度学习模型集成
- 实时流式处理
- 知识图谱可视化

---

**注意**: 这是开发版本的API，生产环境使用时请配置适当的安全措施和性能优化。