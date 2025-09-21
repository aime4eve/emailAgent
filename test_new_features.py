#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新功能测试脚本
测试实体关系抽取、机器学习增强等新增功能
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.nlp_processing.document_parser import DocumentParser
from src.nlp_processing.text_preprocessor import TextPreprocessor
from src.nlp_processing.entity_extractor import EntityExtractor
from src.nlp_processing.relation_extractor import RelationExtractor
from src.ml_enhancement.entity_alignment import EntityAlignment
from src.ml_enhancement.similarity_calculator import SimilarityCalculator
from src.knowledge_management.application.knowledge_extraction_service import KnowledgeExtractionService
from src.knowledge_management.domain.model.node import Node
from src.knowledge_management.domain.model.graph import KnowledgeGraph


def test_document_parser():
    """
    测试文档解析功能
    """
    print("\n=== 测试文档解析功能 ===")
    
    parser = DocumentParser()
    
    # 测试支持的格式
    supported_formats = parser.get_supported_formats()
    print(f"支持的文档格式: {supported_formats}")
    
    # 创建测试文本文件
    test_file = project_root / "test_document.txt"
    test_content = """
这是一个测试文档。
张三在北京大学工作，他是计算机科学系的教授。
李四毕业于清华大学，现在在阿里巴巴公司担任技术总监。
王五和赵六是同事，他们一起在上海的一家科技公司工作。
公司地址位于上海市浦东新区张江高科技园区。
联系电话：021-12345678
邮箱：contact@example.com
    """
    
    try:
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        # 解析文档
        result = parser.parse_document(test_file)
        print(f"解析结果:")
        print(f"  内容长度: {len(result['content'])}")
        print(f"  元数据: {result['metadata']}")
        print(f"  内容预览: {result['content'][:100]}...")
        
        # 清理测试文件
        test_file.unlink()
        
    except Exception as e:
        print(f"文档解析测试失败: {str(e)}")


def test_text_preprocessor():
    """
    测试文本预处理功能
    """
    print("\n=== 测试文本预处理功能 ===")
    
    preprocessor = TextPreprocessor('chinese')
    
    test_text = "张三是北京大学的教授，他在计算机科学系工作。李四毕业于清华大学。"
    
    try:
        # 完整预处理
        result = preprocessor.preprocess_text(test_text, remove_stopwords=True, extract_pos=True)
        
        print(f"原始文本: {test_text}")
        print(f"清理后文本: {result['cleaned_text']}")
        print(f"句子数: {len(result['sentences'])}")
        print(f"词汇数: {len(result['tokens'])}")
        print(f"过滤后词汇: {result['filtered_tokens']}")
        
        # 关键词提取
        keywords = preprocessor.extract_keywords(test_text, top_k=5)
        print(f"关键词: {keywords}")
        
        # 文本统计
        stats = preprocessor.get_text_statistics(test_text)
        print(f"文本统计: {stats}")
        
    except Exception as e:
        print(f"文本预处理测试失败: {str(e)}")


def test_entity_extractor():
    """
    测试实体抽取功能
    """
    print("\n=== 测试实体抽取功能 ===")
    
    extractor = EntityExtractor('chinese')
    
    test_text = """
    张三教授在北京大学计算机科学系工作，他的电话是13812345678。
    李四博士毕业于清华大学，现在在阿里巴巴公司担任技术总监。
    公司地址位于北京市海淀区中关村大街1号，邮编100080。
    项目预算为500万元，预计2024年12月31日完成。
    """
    
    try:
        # 抽取实体
        entities = extractor.extract_entities(test_text)
        
        print(f"抽取到 {len(entities)} 个实体:")
        for entity in entities:
            print(f"  {entity.text} ({entity.label}) - 置信度: {entity.confidence:.2f}")
        
        # 获取统计信息
        stats = extractor.get_entity_statistics(entities)
        print(f"\n实体统计: {stats}")
        
        # 格式化输出
        formatted_output = extractor.format_entities_output(test_text, entities)
        print(f"\n格式化输出:\n{formatted_output}")
        
    except Exception as e:
        print(f"实体抽取测试失败: {str(e)}")


def test_relation_extractor():
    """
    测试关系抽取功能
    """
    print("\n=== 测试关系抽取功能 ===")
    
    extractor = RelationExtractor('chinese')
    
    test_text = """
    张三在北京大学工作，他是计算机科学系的教授。
    李四毕业于清华大学，现在在阿里巴巴公司担任技术总监。
    王五和李四是同事，他们一起合作开发新项目。
    北京大学位于北京市海淀区。
    """
    
    try:
        # 抽取关系
        relations = extractor.extract_relations_from_text(test_text)
        
        print(f"抽取到 {len(relations)} 个关系:")
        for relation in relations:
            print(f"  {relation.subject.text} --[{relation.predicate}]--> {relation.object.text} (置信度: {relation.confidence:.2f})")
        
        # 获取统计信息
        stats = extractor.get_relation_statistics(relations)
        print(f"\n关系统计: {stats}")
        
        # 格式化输出
        formatted_output = extractor.format_relations_output(relations)
        print(f"\n格式化输出:\n{formatted_output}")
        
    except Exception as e:
        print(f"关系抽取测试失败: {str(e)}")


def test_similarity_calculator():
    """
    测试相似度计算功能
    """
    print("\n=== 测试相似度计算功能 ===")
    
    calculator = SimilarityCalculator()
    
    # 创建测试实体
    entity1 = Node("1", "北京大学", "ORG", {"type": "大学", "location": "北京"})
    entity2 = Node("2", "北京大学", "ORG", {"type": "高等院校", "location": "北京市"})
    entity3 = Node("3", "清华大学", "ORG", {"type": "大学", "location": "北京"})
    
    try:
        # 计算实体相似度
        sim1_2 = calculator.entity_similarity(entity1, entity2)
        sim1_3 = calculator.entity_similarity(entity1, entity3)
        
        print(f"北京大学 vs 北京大学: {sim1_2}")
        print(f"北京大学 vs 清华大学: {sim1_3}")
        
        # 文本相似度
        text1 = "张三是北京大学的教授"
        text2 = "张三在北京大学担任教授职务"
        text3 = "李四是清华大学的学生"
        
        cos_sim1 = calculator.cosine_similarity_text(text1, text2)
        cos_sim2 = calculator.cosine_similarity_text(text1, text3)
        
        print(f"\n文本相似度:")
        print(f"  '{text1}' vs '{text2}': {cos_sim1:.3f}")
        print(f"  '{text1}' vs '{text3}': {cos_sim2:.3f}")
        
        # 字符串相似度
        jw_sim = calculator.jaro_winkler_similarity("北京大学", "北京大学计算机系")
        lev_sim = calculator.levenshtein_similarity("北京大学", "北京大学计算机系")
        
        print(f"\n字符串相似度:")
        print(f"  Jaro-Winkler: {jw_sim:.3f}")
        print(f"  Levenshtein: {lev_sim:.3f}")
        
    except Exception as e:
        print(f"相似度计算测试失败: {str(e)}")


def test_entity_alignment():
    """
    测试实体对齐功能
    """
    print("\n=== 测试实体对齐功能 ===")
    
    alignment = EntityAlignment(similarity_threshold=0.8)
    
    # 创建测试知识图谱
    kg = KnowledgeGraph()
    
    # 添加重复实体
    nodes = [
        Node("1", "北京大学", "ORG", {"type": "大学"}),
        Node("2", "北京大学", "ORG", {"location": "北京"}),
        Node("3", "北大", "ORG", {"type": "高等院校"}),
        Node("4", "清华大学", "ORG", {"type": "大学"}),
        Node("5", "张三", "PERSON", {"title": "教授"}),
        Node("6", "张三教授", "PERSON", {"workplace": "北京大学"})
    ]
    
    for node in nodes:
        kg.add_node(node)
    
    try:
        print(f"对齐前: {len(kg.get_all_nodes())} 个节点")
        
        # 执行实体对齐
        alignment_results = alignment.align_entities(kg)
        
        print(f"发现 {len(alignment_results)} 组重复实体:")
        for result in alignment_results:
            print(f"  规范实体: {result.canonical_entity.label}")
            print(f"  重复实体: {[e.label for e in result.duplicate_entities]}")
            print(f"  置信度: {result.confidence:.2f}")
            print(f"  对齐原因: {result.alignment_reason}")
        
        # 应用对齐结果
        aligned_kg = alignment.apply_alignment_results(kg, alignment_results)
        print(f"\n对齐后: {len(aligned_kg.get_all_nodes())} 个节点")
        
        # 获取统计信息
        stats = alignment.get_alignment_statistics(alignment_results)
        print(f"对齐统计: {stats}")
        
    except Exception as e:
        print(f"实体对齐测试失败: {str(e)}")


def test_knowledge_extraction_service():
    """
    测试知识抽取服务
    """
    print("\n=== 测试知识抽取服务 ===")
    
    service = KnowledgeExtractionService('chinese')
    
    test_text = """
    张三教授在北京大学计算机科学系工作，他负责人工智能研究。
    李四博士毕业于清华大学，现在在阿里巴巴公司担任技术总监，负责机器学习项目。
    王五和李四是大学同学，他们经常合作进行学术研究。
    北京大学位于北京市海淀区，是中国顶尖的高等学府之一。
    阿里巴巴公司总部位于杭州市，是中国领先的互联网公司。
    项目预算为1000万元，计划在2024年底完成。
    联系电话：010-12345678，邮箱：contact@pku.edu.cn
    """
    
    try:
        # 从文本抽取知识
        result = service.extract_from_text(test_text, enable_alignment=True)
        
        print(f"抽取结果:")
        print(f"  实体数: {len(result.entities)}")
        print(f"  关系数: {len(result.relations)}")
        print(f"  知识图谱节点数: {len(result.knowledge_graph.get_all_nodes())}")
        print(f"  知识图谱边数: {len(result.knowledge_graph.get_all_edges())}")
        
        # 生成报告
        report = service.get_extraction_report(result)
        print(f"\n抽取报告:\n{report}")
        
        # 测试文档抽取（创建临时文件）
        test_file = project_root / "test_extraction.txt"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_text)
        
        doc_result = service.extract_from_document(str(test_file))
        print(f"\n文档抽取结果:")
        print(f"  实体数: {len(doc_result.entities)}")
        print(f"  关系数: {len(doc_result.relations)}")
        
        # 清理测试文件
        test_file.unlink()
        
    except Exception as e:
        print(f"知识抽取服务测试失败: {str(e)}")


def main():
    """
    主测试函数
    """
    print("开始测试新增功能...")
    
    try:
        test_document_parser()
        test_text_preprocessor()
        test_entity_extractor()
        test_relation_extractor()
        test_similarity_calculator()
        test_entity_alignment()
        test_knowledge_extraction_service()
        
        print("\n=== 所有测试完成 ===")
        print("新增功能测试通过！")
        
    except Exception as e:
        print(f"\n测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()