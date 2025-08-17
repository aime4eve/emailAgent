#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本体导出功能测试脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.knowledge_graph.ontology import KnowledgeOntology, OntologyClass, OntologyRelation, OntologyProperty, DataType
from src.knowledge_graph.ontology_generator import OntologyGenerator
from src.knowledge_graph.graph import KnowledgeGraph
from src.knowledge_graph.node import Node
from src.knowledge_graph.edge import Edge
from datetime import datetime

def create_test_ontology():
    """创建测试本体"""
    # 创建测试知识图谱
    kg = KnowledgeGraph()
    
    # 添加测试节点
    person1 = Node(node_id="person1", label="张三", node_type="Person", properties={"name": "张三", "age": 30, "email": "zhangsan@example.com"})
    person2 = Node(node_id="person2", label="李四", node_type="Person", properties={"name": "李四", "age": 25, "email": "lisi@example.com"})
    company = Node(node_id="company1", label="科技公司", node_type="Company", properties={"name": "科技公司", "founded": "2010-01-01", "employees": 100})
    
    kg.add_node(person1)
    kg.add_node(person2)
    kg.add_node(company)
    
    # 添加测试边
    edge1 = Edge("person1", "company1", "works_for", {"position": "工程师", "start_date": "2020-01-01"})
    edge2 = Edge("person2", "company1", "works_for", {"position": "设计师", "start_date": "2021-06-01"})
    edge3 = Edge("person1", "person2", "knows", {"relationship": "同事", "since": "2021-06-01"})
    
    kg.add_edge(edge1)
    kg.add_edge(edge2)
    kg.add_edge(edge3)
    
    # 生成本体
    ontology_generator = OntologyGenerator()
    ontology = ontology_generator.generate_ontology_from_graph(kg)
    
    return ontology

def test_export_functions():
    """测试导出功能"""
    print("创建测试本体...")
    ontology = create_test_ontology()
    
    print(f"本体名称: {ontology.name}")
    print(f"类数量: {len(ontology.classes)}")
    print(f"关系数量: {len(ontology.relations)}")
    
    # 测试JSON导出
    print("\n测试JSON导出...")
    try:
        json_file = "test_ontology.json"
        ontology.export_to_json(json_file)
        print(f"JSON导出成功: {json_file}")
        
        # 验证文件大小
        if os.path.exists(json_file):
            size = os.path.getsize(json_file)
            print(f"文件大小: {size} 字节")
    except Exception as e:
        print(f"JSON导出失败: {e}")
    
    # 测试OWL导出
    print("\n测试OWL导出...")
    try:
        owl_file = "test_ontology.owl"
        ontology.export_to_owl(owl_file)
        print(f"OWL导出成功: {owl_file}")
        
        # 验证文件大小
        if os.path.exists(owl_file):
            size = os.path.getsize(owl_file)
            print(f"文件大小: {size} 字节")
            
            # 显示前几行内容
            with open(owl_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()[:10]
                print("前10行内容:")
                for i, line in enumerate(lines, 1):
                    print(f"{i:2d}: {line.rstrip()}")
    except Exception as e:
        print(f"OWL导出失败: {e}")
    
    # 测试RDF导出
    print("\n测试RDF导出...")
    try:
        rdf_file = "test_ontology.rdf"
        ontology.export_to_rdf(rdf_file)
        print(f"RDF导出成功: {rdf_file}")
        
        # 验证文件大小
        if os.path.exists(rdf_file):
            size = os.path.getsize(rdf_file)
            print(f"文件大小: {size} 字节")
            
            # 显示前几行内容
            with open(rdf_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()[:10]
                print("前10行内容:")
                for i, line in enumerate(lines, 1):
                    print(f"{i:2d}: {line.rstrip()}")
    except Exception as e:
        print(f"RDF导出失败: {e}")
    
    print("\n测试完成!")

if __name__ == "__main__":
    test_export_functions()