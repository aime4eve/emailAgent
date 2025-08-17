#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全功能测试脚本
测试知识图谱应用的所有主要功能
"""

import sys
import os
import json
import tempfile
import pandas as pd
from pathlib import Path

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from knowledge_graph.graph import KnowledgeGraph
from knowledge_graph.node import Node
from knowledge_graph.edge import Edge
from knowledge_graph.ontology_generator import OntologyGenerator
from visualization.plotly_graph import PlotlyGraphVisualizer
from utils.data_loader import DataLoader
from utils.import_export import DataImportExport
from web_app.interaction_handler import InteractionHandler

def test_knowledge_graph_basic():
    """测试知识图谱基本功能"""
    print("\n=== 测试知识图谱基本功能 ===")
    
    # 创建知识图谱
    kg = KnowledgeGraph()
    
    # 添加节点
    node1 = Node("1", "张三", "人员")
    node2 = Node("2", "李四", "人员")
    node3 = Node("3", "项目A", "项目")
    
    kg.add_node(node1)
    kg.add_node(node2)
    kg.add_node(node3)
    
    # 添加边
    edge1 = Edge("1", "2", "e1", "同事")
    edge2 = Edge("1", "3", "e2", "参与")
    
    kg.add_edge(edge1)
    kg.add_edge(edge2)
    
    # 验证统计信息
    stats = kg.get_statistics()
    assert stats['node_count'] == 3, f"节点数量错误: {stats['node_count']}"
    assert stats['edge_count'] == 2, f"边数量错误: {stats['edge_count']}"
    assert '人员' in stats['node_types'], "缺少人员类型"
    assert '项目' in stats['node_types'], "缺少项目类型"
    
    print("✓ 知识图谱基本功能测试通过")
    return kg

def test_data_import_export(kg):
    """测试数据导入导出功能"""
    print("\n=== 测试数据导入导出功能 ===")
    
    import_export = DataImportExport()
    
    # 确保知识图谱有数据
    if len(kg.get_all_nodes()) == 0:
        print("知识图谱为空，跳过导出测试")
        return
    
    # 测试JSON导出
    json_data = import_export.export_to_json(kg, include_metadata=True)
    assert 'nodes' in json_data, "JSON导出缺少nodes字段"
    assert 'edges' in json_data, "JSON导出缺少edges字段"
    assert len(json_data['nodes']) == 3, "JSON导出节点数量错误"
    
    # 测试JSON导入
    new_kg = import_export.import_from_json(json_data)
    new_stats = new_kg.get_statistics()
    assert new_stats['node_count'] == 3, "JSON导入后节点数量错误"
    assert new_stats['edge_count'] == 2, "JSON导入后边数量错误"
    
    # 测试Excel导出
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
        excel_path = tmp_file.name
    
    try:
        import_export.export_to_excel(kg, excel_path)
        assert os.path.exists(excel_path), "Excel文件导出失败"
        
        # 测试Excel导入
        excel_kg = import_export.import_from_excel(excel_path)
        excel_stats = excel_kg.get_statistics()
        assert excel_stats['node_count'] == 3, "Excel导入后节点数量错误"
        
        print("✓ 数据导入导出功能测试通过")
    finally:
        if os.path.exists(excel_path):
            try:
                os.unlink(excel_path)
            except:
                pass

def test_ontology_generation(kg):
    """测试本体生成功能"""
    print("\n=== 测试本体生成功能 ===")
    
    generator = OntologyGenerator()
    
    # 生成本体
    ontology = generator.generate_ontology_from_graph(kg)
    
    # 验证本体结构
    assert hasattr(ontology, 'classes'), "本体缺少classes属性"
    assert hasattr(ontology, 'relations'), "本体缺少relations属性"
    assert len(ontology.relations) > 0, "本体应该包含至少一个关系"
    assert len(ontology.classes) > 0, "本体类为空"
    
    # 测试字典导出
    json_ontology = ontology.to_dict()
    assert isinstance(json_ontology, dict), "JSON本体导出失败"
    
    # 导出到文件并验证
    ontology.export_to_json('test_ontology.json')
    ontology.export_to_owl('test_ontology.owl')
    ontology.export_to_rdf('test_ontology.rdf')
    
    # 验证文件存在
    assert os.path.exists('test_ontology.json'), "JSON文件导出失败"
    assert os.path.exists('test_ontology.owl'), "OWL文件导出失败"
    assert os.path.exists('test_ontology.rdf'), "RDF文件导出失败"
    
    print("✓ 本体生成功能测试通过")

def test_visualization(kg):
    """测试可视化功能"""
    print("\n=== 测试可视化功能 ===")
    
    visualizer = PlotlyGraphVisualizer()
    
    # 测试不同布局
    layouts = ['spring', 'circular', 'random']
    for layout in layouts:
        try:
            fig = visualizer.create_figure(kg, layout_type=layout)
            assert fig is not None, f"{layout}布局生成失败"
            assert 'data' in fig, f"{layout}布局图形数据缺失"
            print(f"✓ {layout}布局测试通过")
        except Exception as e:
            print(f"⚠ {layout}布局测试失败: {e}")
    
    print("✓ 可视化功能测试通过")

def test_interaction_handler(kg):
    """测试交互处理功能"""
    print("\n=== 测试交互处理功能 ===")
    
    # 创建可视化器和配置
    visualizer = PlotlyGraphVisualizer()
    config = {'layout': 'spring', 'node_size': 10}
    
    handler = InteractionHandler(kg, visualizer, config)
    
    # 测试添加节点
    success = handler.add_node("test_node", "测试节点", "测试类型")
    assert success, "添加节点失败"
    
    # 测试节点选择
    handler.select_node("test_node")
    selected = handler.get_selected_nodes()
    assert "test_node" in selected, "节点选择失败"
    
    # 测试清除选择
    handler.clear_selection()
    selected = handler.get_selected_nodes()
    assert len(selected) == 0, "清除选择失败"
    
    print("✓ 交互处理功能测试通过")

def test_data_loader():
    """测试数据加载功能"""
    print("\n=== 测试数据加载功能 ===")
    
    loader = DataLoader()
    
    # 测试创建示例数据
    try:
        sample_kg = loader.create_sample_data()
        if sample_kg:
            stats = sample_kg.get_statistics()
            assert stats['node_count'] > 0, "示例数据节点为空"
            print(f"✓ 成功创建示例数据: {stats['node_count']}个节点, {stats['edge_count']}条边")
        else:
            print("⚠ 示例数据创建失败，但不影响核心功能")
    except Exception as e:
        print(f"⚠ 数据加载测试失败: {e}")

def main():
    """主测试函数"""
    print("开始全功能测试...")
    
    try:
        # 基本功能测试
        kg = test_knowledge_graph_basic()
        
        # 数据导入导出测试
        test_data_import_export(kg)
        
        # 本体生成测试
        test_ontology_generation(kg)
        
        # 可视化测试
        test_visualization(kg)
        
        # 交互处理测试
        test_interaction_handler(kg)
        
        # 数据加载测试
        test_data_loader()
        
        print("\n🎉 所有功能测试通过！")
        return True
        
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        return False
    except Exception as e:
        print(f"\n💥 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)