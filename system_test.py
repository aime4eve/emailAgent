#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统测试脚本
测试邮件智能代理系统的所有功能模块
"""

import os
import sys
import json
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_knowledge_graph():
    """测试知识图谱核心功能"""
    print("\n=== 测试知识图谱功能 ===")
    try:
        from src.knowledge_graph.core.graph import KnowledgeGraph
        from src.knowledge_graph.core.node import Node
        from src.knowledge_graph.core.edge import Edge
        
        # 创建知识图谱
        kg = KnowledgeGraph()
        
        # 添加节点
        node1 = Node("person_1", "张三", "PERSON", {"age": 30, "job": "教授"})
        node2 = Node("org_1", "北京大学", "ORGANIZATION", {"type": "大学", "location": "北京"})
        
        kg.add_node(node1)
        kg.add_node(node2)
        
        # 添加关系
        edge = Edge("rel_1", node1.id, node2.id, "WORKS_AT", {"since": "2020"})
        kg.add_edge(edge)
        
        # 验证
        assert len(kg.get_all_nodes()) == 2
        assert len(kg.get_all_edges()) == 1
        
        print("✓ 知识图谱基础功能测试通过")
        return True
        
    except Exception as e:
        print(f"✗ 知识图谱测试失败: {e}")
        return False

def test_nlp_processing():
    """测试NLP处理功能"""
    print("\n=== 测试NLP处理功能 ===")
    try:
        from src.nlp_processing.text_preprocessor import TextPreprocessor
        from src.nlp_processing.entity_extractor import EntityExtractor
        from src.nlp_processing.relation_extractor import RelationExtractor
        
        # 测试文本预处理
        preprocessor = TextPreprocessor()
        text = "张三是北京大学的教授，他在计算机科学系工作。"
        
        tokens = preprocessor.tokenize(text)
        sentences = preprocessor.extract_sentences(text)
        
        print(f"✓ 文本预处理: {len(tokens)} 个词，{len(sentences)} 个句子")
        
        # 测试实体抽取
        extractor = EntityExtractor()
        entities = extractor.extract_entities(text)
        
        print(f"✓ 实体抽取: 发现 {len(entities)} 个实体")
        
        # 测试关系抽取
        relation_extractor = RelationExtractor()
        relations = relation_extractor.extract_relations(text, entities)
        
        print(f"✓ 关系抽取: 发现 {len(relations)} 个关系")
        
        return True
        
    except Exception as e:
        print(f"✗ NLP处理测试失败: {e}")
        return False

def test_ml_enhancement():
    """测试机器学习增强功能"""
    print("\n=== 测试机器学习增强功能 ===")
    try:
        from src.ml_enhancement.similarity_calculator import SimilarityCalculator
        from src.ml_enhancement.entity_alignment import EntityAlignment
        
        # 测试相似度计算
        calc = SimilarityCalculator()
        
        similarity = calc.jaccard_similarity_text("北京大学", "清华大学")
        print(f"✓ 相似度计算: Jaccard相似度 = {similarity:.3f}")
        
        # 测试实体对齐
        alignment = EntityAlignment()
        print("✓ 实体对齐模块初始化成功")
        
        return True
        
    except Exception as e:
        print(f"✗ 机器学习增强测试失败: {e}")
        return False

def test_knowledge_extraction_service():
    """测试知识抽取服务"""
    print("\n=== 测试知识抽取服务 ===")
    try:
        from src.knowledge_management.application.knowledge_extraction_service import KnowledgeExtractionService
        
        service = KnowledgeExtractionService()
        
        # 测试文本知识抽取
        text = "张三是北京大学的教授，专门研究人工智能。李四是清华大学的学生。"
        result = service.extract_from_text(text)
        
        print(f"✓ 知识抽取服务: 处理文本成功")
        print(f"  - 实体数量: {len(result.get('entities', []))}")
        print(f"  - 关系数量: {len(result.get('relations', []))}")
        
        return True
        
    except Exception as e:
        print(f"✗ 知识抽取服务测试失败: {e}")
        return False

def test_web_interface():
    """测试Web接口"""
    print("\n=== 测试Web接口 ===")
    try:
        # 检查Flask应用是否可以启动
        from src.web.app import create_app
        
        app = create_app()
        
        with app.test_client() as client:
            # 测试主页
            response = client.get('/')
            assert response.status_code == 200
            
            print("✓ Web接口测试通过")
            return True
            
    except Exception as e:
        print(f"✗ Web接口测试失败: {e}")
        return False

def test_document_processing():
    """测试文档处理功能"""
    print("\n=== 测试文档处理功能 ===")
    try:
        from src.nlp_processing.document_parser import DocumentParser
        
        parser = DocumentParser()
        
        # 创建测试文本文件
        test_file = "test_document.txt"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("这是一个测试文档。张三是北京大学的教授。")
        
        try:
            # 测试文档解析
            result = parser.parse_document(test_file)
            
            print(f"✓ 文档解析: 提取文本长度 {len(result['content'])} 字符")
            
            return True
            
        finally:
            # 清理测试文件
            if os.path.exists(test_file):
                os.remove(test_file)
                
    except Exception as e:
        print(f"✗ 文档处理测试失败: {e}")
        return False

def generate_test_report(results):
    """生成测试报告"""
    print("\n" + "="*50)
    print("系统测试报告")
    print("="*50)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    
    print(f"总测试数: {total_tests}")
    print(f"通过测试: {passed_tests}")
    print(f"失败测试: {total_tests - passed_tests}")
    print(f"通过率: {passed_tests/total_tests*100:.1f}%")
    
    print("\n详细结果:")
    for test_name, result in results.items():
        status = "✓ 通过" if result else "✗ 失败"
        print(f"  {test_name}: {status}")
    
    # 保存报告到文件
    report = {
        "timestamp": str(Path(__file__).stat().st_mtime),
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "pass_rate": passed_tests/total_tests*100,
        "results": results
    }
    
    with open("test_report.json", 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n测试报告已保存到: test_report.json")
    
    return passed_tests == total_tests

def main():
    """主测试函数"""
    print("开始系统测试...")
    
    # 执行所有测试
    test_results = {
        "知识图谱功能": test_knowledge_graph(),
        "NLP处理功能": test_nlp_processing(),
        "机器学习增强": test_ml_enhancement(),
        "知识抽取服务": test_knowledge_extraction_service(),
        "文档处理功能": test_document_processing(),
        "Web接口": test_web_interface()
    }
    
    # 生成测试报告
    all_passed = generate_test_report(test_results)
    
    if all_passed:
        print("\n🎉 所有测试通过！系统功能正常。")
        return 0
    else:
        print("\n⚠️  部分测试失败，请检查相关模块。")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)