# -*- coding: utf-8 -*-
"""
测试数据导入功能
"""

import json
import pandas as pd
import os
from pathlib import Path

# 添加项目路径
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.import_export import DataImportExport
from src.knowledge_graph.graph import KnowledgeGraph
from src.knowledge_graph.node import Node
from src.knowledge_graph.edge import Edge

def create_test_json_file():
    """创建测试JSON文件"""
    test_data = {
        "nodes": [
            {
                "id": "test1",
                "label": "测试节点1",
                "type": "Person",
                "properties": {
                    "name": "张三",
                    "age": 30
                }
            },
            {
                "id": "test2",
                "label": "测试节点2",
                "type": "Company",
                "properties": {
                    "name": "测试公司",
                    "industry": "科技"
                }
            }
        ],
        "edges": [
            {
                "id": "edge1",
                "source": "test1",
                "target": "test2",
                "label": "工作于",
                "type": "WorksAt",
                "properties": {
                    "start_date": "2020-01-01"
                }
            }
        ]
    }
    
    with open('test_import.json', 'w', encoding='utf-8') as f:
        json.dump(test_data, f, ensure_ascii=False, indent=2)
    
    print("已创建测试JSON文件: test_import.json")
    return 'test_import.json'

def create_test_excel_file():
    """创建测试Excel文件"""
    # 创建节点数据
    nodes_data = {
        'id': ['test1', 'test2'],
        'label': ['测试节点1', '测试节点2'],
        'type': ['Person', 'Company'],
        'name': ['张三', '测试公司'],
        'age': [30, None],
        'industry': [None, '科技']
    }
    
    # 创建边数据
    edges_data = {
        'id': ['edge1'],
        'source': ['test1'],
        'target': ['test2'],
        'label': ['工作于'],
        'type': ['WorksAt'],
        'start_date': ['2020-01-01']
    }
    
    with pd.ExcelWriter('test_import.xlsx', engine='openpyxl') as writer:
        pd.DataFrame(nodes_data).to_excel(writer, sheet_name='Nodes', index=False)
        pd.DataFrame(edges_data).to_excel(writer, sheet_name='Edges', index=False)
    
    print("已创建测试Excel文件: test_import.xlsx")
    return 'test_import.xlsx'

def test_json_import():
    """测试JSON导入功能"""
    print("\n=== 测试JSON导入功能 ===")
    
    # 创建测试文件
    json_file = create_test_json_file()
    
    try:
        # 创建导入导出处理器
        import_export_handler = DataImportExport()
        
        # 读取JSON文件
        with open(json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        print(f"JSON文件内容: {json.dumps(json_data, ensure_ascii=False, indent=2)}")
        
        # 测试导入
        imported_kg = import_export_handler.import_from_json(json_data)
        print(f"导入成功! 节点数: {len(imported_kg.get_all_nodes())}, 边数: {len(imported_kg.get_all_edges())}")
        
        # 验证数据
        validation_result = import_export_handler.validate_import_data(imported_kg.to_dict())
        print(f"验证结果: {validation_result}")
        
        # 清理测试文件
        os.remove(json_file)
        
        return True
        
    except Exception as e:
        print(f"JSON导入测试失败: {str(e)}")
        if os.path.exists(json_file):
            os.remove(json_file)
        return False

def test_excel_import():
    """测试Excel导入功能"""
    print("\n=== 测试Excel导入功能 ===")
    
    # 创建测试文件
    excel_file = create_test_excel_file()
    
    try:
        # 创建导入导出处理器
        import_export_handler = DataImportExport()
        
        # 测试导入
        imported_kg = import_export_handler.import_from_excel(excel_file)
        print(f"导入成功! 节点数: {len(imported_kg.get_all_nodes())}, 边数: {len(imported_kg.get_all_edges())}")
        
        # 验证数据
        validation_result = import_export_handler.validate_import_data(imported_kg.to_dict())
        print(f"验证结果: {validation_result}")
        
        # 清理测试文件
        os.remove(excel_file)
        
        return True
        
    except Exception as e:
        print(f"Excel导入测试失败: {str(e)}")
        return False
    finally:
        # 尝试删除测试文件，如果失败则忽略
        try:
            if os.path.exists(excel_file):
                os.remove(excel_file)
        except:
            pass

def test_web_upload_simulation():
    """模拟Web上传功能测试"""
    print("\n=== 模拟Web上传功能测试 ===")
    
    # 创建测试JSON文件
    json_file = create_test_json_file()
    
    try:
        import base64
        
        # 读取文件并编码（模拟Web上传）
        with open(json_file, 'rb') as f:
            file_content = f.read()
        
        # Base64编码
        encoded_content = base64.b64encode(file_content).decode('utf-8')
        contents = f"data:application/json;base64,{encoded_content}"
        
        print(f"模拟上传内容长度: {len(contents)}")
        
        # 模拟Web应用的处理逻辑
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        json_data = json.loads(decoded.decode('utf-8'))
        
        # 创建导入导出处理器
        import_export_handler = DataImportExport()
        imported_kg = import_export_handler.import_from_json(json_data)
        
        print(f"模拟Web上传成功! 节点数: {len(imported_kg.get_all_nodes())}, 边数: {len(imported_kg.get_all_edges())}")
        
        # 清理测试文件
        os.remove(json_file)
        
        return True
        
    except Exception as e:
        print(f"Web上传模拟测试失败: {str(e)}")
        if os.path.exists(json_file):
            os.remove(json_file)
        return False

if __name__ == "__main__":
    print("开始测试数据导入功能...")
    
    # 测试各种导入方式
    json_success = test_json_import()
    excel_success = test_excel_import()
    web_success = test_web_upload_simulation()
    
    print("\n=== 测试结果汇总 ===")
    print(f"JSON导入: {'✓ 成功' if json_success else '✗ 失败'}")
    print(f"Excel导入: {'✓ 成功' if excel_success else '✗ 失败'}")
    print(f"Web上传模拟: {'✓ 成功' if web_success else '✗ 失败'}")
    
    if all([json_success, excel_success, web_success]):
        print("\n所有导入功能测试通过！")
    else:
        print("\n部分导入功能存在问题，需要进一步检查。")