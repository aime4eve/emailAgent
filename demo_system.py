#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识图谱系统演示脚本
演示实体关系抽取、机器学习增强、邮件知识抽取等功能
"""

import sys
import os
import json
import logging
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_document_parser():
    """测试文档解析功能"""
    print("\n=== 测试文档解析功能 ===")
    
    try:
        from src.knowledge_management.infrastructure.document_parser import DocumentParserFactory
        
        # 创建测试文档
        test_content = """苹果公司是一家美国跨国科技公司，总部位于加利福尼亚州库比蒂诺。
蒂姆·库克是苹果公司的首席执行官。
该公司以设计和制造消费电子产品而闻名，包括iPhone、iPad、Mac电脑等。
苹果公司成立于1976年，由史蒂夫·乔布斯、史蒂夫·沃兹尼亚克和罗纳德·韦恩共同创立。"""
        
        test_file = "test_document.txt"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        # 解析文档
        parser_factory = DocumentParserFactory()
        result = parser_factory.parse_document(test_file)
        
        print(f"✓ 文档解析成功")
        print(f"  - 文件类型: {result['metadata']['file_type']}")
        print(f"  - 文件大小: {result['metadata']['file_size']} 字节")
        print(f"  - 内容长度: {len(result['content'])} 字符")
        print(f"  - 内容预览: {result['content'][:100]}...")
        
        # 清理测试文件
        os.remove(test_file)
        
        return True
        
    except Exception as e:
        print(f"✗ 文档解析测试失败: {e}")
        return False

def test_nlp_processor():
    """测试NLP处理功能"""
    print("\n=== 测试NLP处理功能 ===")
    
    try:
        from src.knowledge_management.infrastructure.nlp_processor import ChineseNLPProcessor
        
        # 创建NLP处理器
        nlp_processor = ChineseNLPProcessor()
        
        # 测试文本
        test_text = "张三在北京大学工作，他是计算机科学系的教授。李四是他的同事，在同一个系工作。"
        
        # 抽取实体
        entities = nlp_processor.extract_entities(test_text)
        print(f"✓ 实体抽取成功，发现 {len(entities)} 个实体:")
        for entity in entities[:5]:  # 显示前5个
            print(f"  - {entity.text} ({entity.entity_type.value}, 置信度: {entity.confidence:.2f})")
        
        # 抽取关系
        relations = nlp_processor.extract_relations(test_text, entities)
        print(f"✓ 关系抽取成功，发现 {len(relations)} 个关系:")
        for relation in relations[:3]:  # 显示前3个
            print(f"  - {relation.source_entity.text} -> {relation.target_entity.text} ({relation.relation_type.value})")
        
        return True
        
    except Exception as e:
        print(f"✗ NLP处理测试失败: {e}")
        return False

def test_entity_extraction_service():
    """测试实体抽取服务"""
    print("\n=== 测试实体抽取服务 ===")
    
    try:
        from src.knowledge_management.application.entity_extraction_service import EntityExtractionService
        
        # 创建服务
        service = EntityExtractionService()
        
        # 测试文本
        test_text = """微软公司是一家美国跨国科技公司，总部位于华盛顿州雷德蒙德。
比尔·盖茨和保罗·艾伦于1975年创立了微软公司。
萨蒂亚·纳德拉是现任首席执行官，于2014年接任这一职位。
微软公司的主要产品包括Windows操作系统、Office办公软件套件和Azure云服务。"""
        
        # 从文本抽取
        result = service.extract_from_text(test_text)
        
        print(f"✓ 实体抽取服务测试成功")
        print(f"  - 处理时间: {result.processing_time:.2f} 秒")
        print(f"  - 抽取实体数: {len(result.entities)}")
        print(f"  - 抽取关系数: {len(result.relations)}")
        
        # 显示统计信息
        stats = result.get_statistics()
        print(f"  - 实体类型分布: {stats['entity_type_counts']}")
        print(f"  - 关系类型分布: {stats['relation_type_counts']}")
        
        return True
        
    except Exception as e:
        print(f"✗ 实体抽取服务测试失败: {e}")
        return False

def test_ml_enhancement_service():
    """测试机器学习增强服务"""
    print("\n=== 测试机器学习增强服务 ===")
    
    try:
        from src.knowledge_management.application.ml_enhancement_service import MLEnhancementService
        from src.knowledge_management.domain.model.extraction import (
            ExtractedEntity, ExtractedRelation, EntityType, RelationType
        )
        
        # 创建服务
        service = MLEnhancementService()
        
        # 创建测试实体
        entities = [
            ExtractedEntity(
                entity_id="1",
                text="张三",
                entity_type=EntityType.PERSON,
                confidence=0.9,
                start_pos=0,
                end_pos=2
            ),
            ExtractedEntity(
                entity_id="2",
                text="张三",  # 重复实体
                entity_type=EntityType.PERSON,
                confidence=0.8,
                start_pos=10,
                end_pos=12
            ),
            ExtractedEntity(
                entity_id="3",
                text="北京大学",
                entity_type=EntityType.ORGANIZATION,
                confidence=0.95,
                start_pos=5,
                end_pos=9
            )
        ]
        
        # 创建测试关系
        relations = [
            ExtractedRelation(
                relation_id="r1",
                source_entity=entities[0],
                target_entity=entities[2],
                relation_type=RelationType.WORK_FOR,
                confidence=0.8
            )
        ]
        
        # 测试实体对齐
        alignment_result = service.align_entities(entities)
        print(f"✓ 实体对齐完成，发现 {len(alignment_result.aligned_groups)} 个对齐组")
        
        # 测试语义消解
        disambiguation_result = service.disambiguate_entities(entities)
        print(f"✓ 语义消解完成，消解 {len(disambiguation_result.disambiguated_entities)} 个实体")
        
        # 测试关系推理
        inferred_relations = service.infer_relations(entities, relations)
        print(f"✓ 关系推理完成，推理出 {len(inferred_relations)} 个新关系")
        
        # 测试异常检测
        anomalies = service.detect_anomalies(entities, relations)
        total_anomalies = sum(len(anomaly_list) for anomaly_list in anomalies.values())
        print(f"✓ 异常检测完成，发现 {total_anomalies} 个异常")
        
        return True
        
    except Exception as e:
        print(f"✗ 机器学习增强服务测试失败: {e}")
        return False

def test_email_knowledge_service():
    """测试邮件知识抽取服务"""
    print("\n=== 测试邮件知识抽取服务 ===")
    
    try:
        from src.email_ingestion.application.email_knowledge_service import EmailKnowledgeService
        from src.email_ingestion.domain.model.email import Email
        
        # 创建服务
        service = EmailKnowledgeService()
        
        # 创建测试邮件
        test_email = Email(
            subject="项目进度会议通知",
            sender="project.manager@company.com",
            content="""各位团队成员，
            
我们将于明天下午2点在会议室A召开项目进度会议。
请各位项目成员准时参加，会议将讨论以下内容：
1. 当前项目进展情况
2. 遇到的技术难题
3. 下阶段工作安排

请大家提前准备相关材料。

项目经理
张三""",
            attachments=[{"filename": "项目进度报告.docx"}]
        )
        
        # 从邮件抽取知识
        result = service.extract_knowledge_from_email(test_email)
        
        print(f"✓ 邮件知识抽取成功")
        print(f"  - 处理时间: {result.processing_time:.2f} 秒")
        print(f"  - 抽取实体数: {len(result.entities)}")
        print(f"  - 抽取关系数: {len(result.relations)}")
        print(f"  - 邮件发件人: {result.metadata['email_sender']}")
        print(f"  - 邮件主题: {result.metadata['email_subject']}")
        
        # 显示抽取的实体
        print("  - 主要实体:")
        for entity in result.entities[:5]:
            print(f"    * {entity.text} ({entity.entity_type.value})")
        
        return True
        
    except Exception as e:
        print(f"✗ 邮件知识抽取服务测试失败: {e}")
        return False

def test_integrated_knowledge_service():
    """测试集成知识服务"""
    print("\n=== 测试集成知识服务 ===")
    
    try:
        from src.knowledge_management.application.integrated_knowledge_service import IntegratedKnowledgeService
        from src.email_ingestion.domain.model.email import Email
        
        # 创建服务
        service = IntegratedKnowledgeService()
        
        # 获取服务状态
        status = service.get_service_status()
        print(f"✓ 服务状态检查完成")
        print(f"  - 服务名称: {status['service_name']}")
        print(f"  - 服务状态: {status['status']}")
        print(f"  - 支持功能: {', '.join(status['supported_features'])}")
        
        # 测试邮件处理
        test_emails = [
            Email(
                subject="技术讨论",
                sender="developer1@company.com",
                content="关于新架构的技术方案，我认为应该采用微服务架构。",
                attachments=[]
            ),
            Email(
                subject="项目更新",
                sender="manager@company.com",
                content="项目进展顺利，预计下周完成第一阶段开发。",
                attachments=[]
            )
        ]
        
        # 处理邮件到知识图谱
        result = service.process_emails_to_knowledge_graph(
            test_emails, enable_ml_enhancement=False
        )
        
        print(f"✓ 邮件知识图谱处理完成")
        print(f"  - 处理邮件数: {result['processing_summary']['total_emails']}")
        print(f"  - 总实体数: {result['processing_summary']['total_entities']}")
        print(f"  - 总关系数: {result['processing_summary']['total_relations']}")
        print(f"  - 知识图谱节点数: {result['knowledge_graph']['nodes_count']}")
        print(f"  - 知识图谱边数: {result['knowledge_graph']['edges_count']}")
        
        return True
        
    except Exception as e:
        print(f"✗ 集成知识服务测试失败: {e}")
        return False

def create_demo_data():
    """创建演示数据"""
    print("\n=== 创建演示数据 ===")
    
    # 创建演示文档
    demo_content = """人工智能技术发展报告

概述：
人工智能（AI）是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。

主要公司和人物：
1. OpenAI公司由萨姆·奥特曼领导，开发了ChatGPT等产品
2. 谷歌公司的DeepMind团队在机器学习领域取得重大突破
3. 微软公司与OpenAI建立了战略合作关系
4. 特斯拉公司的埃隆·马斯克也在AI领域有重要投资

技术发展：
深度学习技术在图像识别、自然语言处理等领域取得显著进展。
大语言模型如GPT-4展现了强大的文本生成和理解能力。

应用领域：
- 自动驾驶：特斯拉、百度等公司在此领域投入巨大
- 医疗诊断：AI辅助医生进行疾病诊断
- 金融服务：智能投顾、风险控制等
- 教育：个性化学习、智能辅导

未来展望：
人工智能将继续快速发展，预计在未来5-10年内将在更多领域实现突破。
"""
    
    demo_file = "demo_ai_report.txt"
    with open(demo_file, 'w', encoding='utf-8') as f:
        f.write(demo_content)
    
    print(f"✓ 创建演示文档: {demo_file}")
    return demo_file

def run_full_demo():
    """运行完整演示"""
    print("\n=== 运行完整知识图谱系统演示 ===")
    
    try:
        from src.knowledge_management.application.integrated_knowledge_service import IntegratedKnowledgeService
        
        # 创建演示数据
        demo_file = create_demo_data()
        
        # 创建集成服务
        service = IntegratedKnowledgeService()
        
        # 处理文档到知识图谱
        print("\n正在处理文档...")
        result = service.process_documents_to_knowledge_graph(
            [demo_file],
            enable_ml_enhancement=False,  # 暂时禁用ML增强以避免依赖问题
            custom_entity_types={
                'COMPANY': ['OpenAI', '谷歌', '微软', '特斯拉', '百度'],
                'TECHNOLOGY': ['人工智能', '深度学习', '机器学习', 'ChatGPT', 'GPT-4']
            }
        )
        
        print(f"\n✓ 文档处理完成！")
        print(f"  - 知识图谱节点数: {result['knowledge_graph']['nodes_count']}")
        print(f"  - 知识图谱边数: {result['knowledge_graph']['edges_count']}")
        
        # 导出结果
        if result['knowledge_graph'].get('graph'):
            output_file = "demo_knowledge_graph.json"
            try:
                service.export_knowledge_graph(result['knowledge_graph']['graph'], output_file)
                print(f"  - 知识图谱已导出到: {output_file}")
            except Exception as export_error:
                print(f"  - 知识图谱导出跳过: {export_error}")
        
        # 显示本体信息
        if 'ontology' in result:
            ontology = result['ontology']
            if hasattr(ontology, 'get_statistics'):
                ontology_stats = ontology.get_statistics()
                print(f"  - 本体类数量: {ontology_stats.get('classes_count', 0)}")
                print(f"  - 本体关系数量: {ontology_stats.get('relations_count', 0)}")
        
        # 清理演示文件
        os.remove(demo_file)
        
        return True
        
    except Exception as e:
        print(f"✗ 完整演示失败: {e}")
        return False

def main():
    """主函数"""
    print("知识图谱可视化与管理平台 - 系统演示")
    print("=" * 50)
    
    # 测试结果统计
    test_results = []
    
    # 运行各项测试
    test_results.append(("文档解析", test_document_parser()))
    test_results.append(("NLP处理", test_nlp_processor()))
    test_results.append(("实体抽取服务", test_entity_extraction_service()))
    test_results.append(("ML增强服务", test_ml_enhancement_service()))
    test_results.append(("邮件知识抽取", test_email_knowledge_service()))
    test_results.append(("集成知识服务", test_integrated_knowledge_service()))
    
    # 运行完整演示
    test_results.append(("完整演示", run_full_demo()))
    
    # 显示测试结果摘要
    print("\n" + "=" * 50)
    print("测试结果摘要:")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n总计: {passed} 个测试通过, {failed} 个测试失败")
    
    if failed == 0:
        print("\n🎉 所有测试都通过了！系统功能正常。")
    else:
        print(f"\n⚠️  有 {failed} 个测试失败，请检查相关功能。")
    
    print("\n演示完成！")

if __name__ == "__main__":
    main()