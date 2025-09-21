# 知识图谱可视化与管理平台

## 系统概述

本系统是一个基于DDD架构的知识图谱管理平台，集成了实体关系抽取、机器学习增强、邮件知识抽取等功能，能够从文档和邮件中自动构建知识图谱。

## 核心功能模块

### 1. 实体关系抽取模块 (`src/knowledge_management`)

#### 领域模型 (`domain/model/extraction.py`)
- **ExtractedEntity**: 抽取的实体对象，包含ID、类型、文本、置信度等属性
- **ExtractedRelation**: 抽取的关系对象，包含源实体、目标实体、关系类型等
- **ExtractionResult**: 抽取结果容器，包含实体列表、关系列表和元数据
- **BatchExtractionResult**: 批量抽取结果，支持统计分析

#### 基础设施层 (`infrastructure/`)
- **DocumentParser**: 文档解析器，支持PDF、Word、Excel、TXT格式
- **NLPProcessor**: 自然语言处理器，基于spaCy和jieba实现中文NLP

#### 应用服务层 (`application/`)
- **EntityExtractionService**: 实体抽取服务，提供文档和文本的实体关系抽取
- **MLEnhancementService**: 机器学习增强服务，提供实体对齐、语义消解、关系推理等功能
- **IntegratedKnowledgeService**: 集成知识服务，统一管理所有知识处理功能

### 2. 邮件知识抽取模块 (`src/email_ingestion`)

#### 应用服务 (`application/email_knowledge_service.py`)
- **EmailKnowledgeService**: 邮件知识抽取服务
  - 从邮件内容中抽取实体和关系
  - 分析邮件网络结构
  - 生成邮件知识摘要

## 系统架构特点

### DDD架构模式
- **领域层**: 定义核心业务对象和规则
- **应用层**: 实现业务用例和服务编排
- **基础设施层**: 提供技术实现和外部接口

### 设计模式应用
- **工厂模式**: DocumentParserFactory管理不同格式的文档解析器
- **策略模式**: 不同的NLP处理策略（中文、英文、混合）
- **管道模式**: KnowledgeProcessingPipeline实现处理流水线

## 功能演示

### 运行系统演示
```bash
python demo_system.py
```

演示包含以下测试：
1. **文档解析测试**: 验证各种格式文档的解析能力
2. **NLP处理测试**: 验证中文实体识别和关系抽取
3. **实体抽取服务测试**: 验证完整的实体抽取流程
4. **机器学习增强测试**: 验证实体对齐、语义消解等功能
5. **邮件知识抽取测试**: 验证邮件内容的知识抽取
6. **集成知识服务测试**: 验证服务集成和状态管理
7. **完整演示**: 端到端的文档处理和知识图谱构建

### 演示结果示例
```
知识图谱可视化与管理平台 - 系统演示
==================================================

=== 测试文档解析功能 ===
✓ 文档解析成功
  - 文件类型: txt
  - 文件大小: 123 字节
  - 内容长度: 123 字符

=== 测试NLP处理功能 ===
✓ 实体抽取成功，发现 8 个实体:
  - 张三 (PERSON, 置信度: 0.90)
  - 北京大学 (ORGANIZATION, 置信度: 0.95)
  - 计算机科学系 (ORGANIZATION, 置信度: 0.85)

✓ 关系抽取成功，发现 3 个关系:
  - 张三 -> 北京大学 (WORK_FOR)
  - 张三 -> 计算机科学系 (WORK_FOR)

=== 完整演示 ===
✓ 文档处理完成！
  - 知识图谱节点数: 29
  - 知识图谱边数: 10
  - 本体类数量: 5
  - 本体关系数量: 3

🎉 所有测试都通过了！系统功能正常。
```

## 技术栈

### 核心依赖
- **Python 3.8+**: 主要开发语言
- **spaCy**: 英文自然语言处理
- **jieba**: 中文分词
- **scikit-learn**: 机器学习算法
- **networkx**: 图结构处理

### 文档处理
- **pdfplumber**: PDF文档解析
- **python-docx**: Word文档处理
- **openpyxl**: Excel文件处理

### 数据处理
- **pandas**: 数据分析和处理
- **numpy**: 数值计算

## 使用指南

### 1. 基本实体抽取
```python
from src.knowledge_management.application.entity_extraction_service import EntityExtractionService

service = EntityExtractionService()
result = service.extract_from_text("张三在北京大学工作")

print(f"抽取到 {len(result.entities)} 个实体")
for entity in result.entities:
    print(f"- {entity.text} ({entity.entity_type.value})")
```

### 2. 文档批量处理
```python
service = EntityExtractionService()
result = service.extract_from_files(["document1.pdf", "document2.docx"])

print(f"处理了 {len(result.results)} 个文档")
print(f"总共抽取 {result.total_entities} 个实体")
```

### 3. 邮件知识抽取
```python
from src.email_ingestion.application.email_knowledge_service import EmailKnowledgeService
from src.email_ingestion.domain.model.email import Email

service = EmailKnowledgeService()
email = Email(subject="会议通知", sender="manager@company.com", content="...")
result = service.extract_knowledge_from_email(email)

print(f"从邮件中抽取到 {len(result.entities)} 个实体")
```

### 4. 集成知识处理
```python
from src.knowledge_management.application.integrated_knowledge_service import IntegratedKnowledgeService

service = IntegratedKnowledgeService()
result = service.process_documents_to_knowledge_graph(
    ["document.pdf"],
    enable_ml_enhancement=True
)

print(f"知识图谱包含 {result['knowledge_graph']['nodes_count']} 个节点")
```

## 扩展开发

### 添加新的实体类型
1. 在 `domain/model/extraction.py` 中扩展 `EntityType` 枚举
2. 在 `infrastructure/nlp_processor.py` 中添加识别规则
3. 更新相关的映射和处理逻辑

### 添加新的文档格式支持
1. 在 `infrastructure/document_parser.py` 中创建新的解析器类
2. 继承 `BaseDocumentParser` 并实现 `parse` 方法
3. 在 `DocumentParserFactory` 中注册新的解析器

### 集成新的NLP模型
1. 在 `infrastructure/nlp_processor.py` 中创建新的处理器类
2. 继承 `BaseNLPProcessor` 并实现相关方法
3. 在全局处理器获取函数中添加选择逻辑

## 性能优化建议

1. **批量处理**: 使用批量API处理大量文档，提高处理效率
2. **缓存机制**: 对重复文档和实体抽取结果进行缓存
3. **并行处理**: 利用多进程或多线程处理独立的文档
4. **模型优化**: 根据具体领域调优NLP模型参数

## 故障排除

### 常见问题

1. **依赖安装失败**
   - 确保Python版本 >= 3.8
   - 使用虚拟环境避免依赖冲突
   - 分步安装复杂依赖如pandas、scipy

2. **中文处理异常**
   - 确保jieba库正确安装
   - 检查文本编码格式（推荐UTF-8）

3. **文档解析失败**
   - 检查文档格式是否受支持
   - 确认文档文件完整性
   - 查看详细错误日志

4. **内存使用过高**
   - 减少批量处理的文档数量
   - 启用增量处理模式
   - 优化实体去重算法

## 系统监控

系统提供详细的日志记录，包括：
- 文档处理进度和性能指标
- 实体抽取统计信息
- 错误和异常详情
- 服务状态和健康检查

查看日志：
```bash
# 查看最近的处理日志
tail -f logs/knowledge_extraction.log

# 查看错误日志
grep "ERROR" logs/knowledge_extraction.log
```

## 贡献指南

1. 遵循DDD架构原则
2. 添加完整的函数级注释
3. 编写相应的单元测试
4. 更新相关文档
5. 遵循Python PEP 8编码规范

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

---

**联系方式**: 如有问题或建议，请通过项目Issues页面反馈。