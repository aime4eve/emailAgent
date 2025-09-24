#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试API响应数据
直接测试后端API返回的数据结构
"""

import requests
import json
import time

def test_api_response():
    """测试API响应数据结构"""
    url = "http://localhost:5000/api/extract"
    
    # 测试数据
    test_data = {
        "text": "张三是来自北京的ABC公司采购经理，他对iPhone 15 Pro产品很感兴趣，希望了解批量采购的价格和交货周期。请联系销售经理李四获取详细报价单。"
    }
    
    print("=== 调试API响应数据 ===")
    print(f"请求URL: {url}")
    print(f"请求数据: {json.dumps(test_data, ensure_ascii=False, indent=2)}")
    print()
    
    try:
        # 发送POST请求
        start_time = time.time()
        response = requests.post(url, json=test_data, headers={'Content-Type': 'application/json'})
        end_time = time.time()
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应时间: {(end_time - start_time):.2f}秒")
        print(f"响应头: {dict(response.headers)}")
        print()
        
        if response.status_code == 200:
            # 解析响应数据
            response_data = response.json()
            print("=== 完整响应数据 ===")
            print(json.dumps(response_data, ensure_ascii=False, indent=2))
            print()
            
            # 分析数据结构
            print("=== 数据结构分析 ===")
            print(f"响应根级别键: {list(response_data.keys())}")
            
            if 'success' in response_data:
                print(f"success: {response_data['success']}")
            
            if 'data' in response_data:
                data = response_data['data']
                print(f"data键的类型: {type(data)}")
                if isinstance(data, dict):
                    print(f"data的键: {list(data.keys())}")
                    
                    if 'entities' in data:
                        entities = data['entities']
                        print(f"entities数量: {len(entities) if isinstance(entities, list) else 'N/A'}")
                        if isinstance(entities, list) and len(entities) > 0:
                            print(f"第一个实体: {json.dumps(entities[0], ensure_ascii=False, indent=2)}")
                    
                    if 'relations' in data:
                        relations = data['relations']
                        print(f"relations数量: {len(relations) if isinstance(relations, list) else 'N/A'}")
                        if isinstance(relations, list) and len(relations) > 0:
                            print(f"第一个关系: {json.dumps(relations[0], ensure_ascii=False, indent=2)}")
                    
                    if 'statistics' in data:
                        statistics = data['statistics']
                        print(f"statistics: {json.dumps(statistics, ensure_ascii=False, indent=2)}")
            
            print()
            print("=== 前端期望的数据结构 ===")
            print("前端期望接收到的数据应该是:")
            print("response.data = {")
            print("  entities: [...],")
            print("  relations: [...],")
            print("  statistics: {...}")
            print("}")
            print()
            
            # 模拟前端处理逻辑
            print("=== 模拟前端处理逻辑 ===")
            if response_data.get('success') and response_data.get('data'):
                processed_data = {
                    'entities': response_data['data'].get('entities', []),
                    'relations': response_data['data'].get('relations', []),
                    'confidence': response_data['data'].get('statistics', {}).get('confidence', 0),
                    'statistics': response_data['data'].get('statistics'),
                    'processing_time': response_data['data'].get('statistics', {}).get('processing_time')
                }
                
                print(f"处理后的数据:")
                print(f"  实体数量: {len(processed_data['entities'])}")
                print(f"  关系数量: {len(processed_data['relations'])}")
                print(f"  置信度: {processed_data['confidence']}")
                print(f"  处理时间: {processed_data['processing_time']}")
                
                if len(processed_data['entities']) == 0 and len(processed_data['relations']) == 0:
                    print("❌ 问题确认: 前端处理后实体和关系数量都为0")
                else:
                    print("✅ 数据处理正常")
            
        else:
            print(f"❌ API请求失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接错误: 无法连接到后端服务器")
        print("请确保后端服务器正在运行在 http://localhost:5000")
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")

if __name__ == "__main__":
    test_api_response()