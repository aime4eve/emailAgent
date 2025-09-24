#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试前端API调用
"""

import requests
import json

def test_api_extract():
    """测试知识抽取API"""
    url = "http://localhost:5000/api/extract"
    
    test_data = {
        "text": "我是张三，来自北京的ABC公司。我们公司专门生产电子产品，包括手机、平板电脑和笔记本电脑。我们希望与贵公司建立长期的合作关系。请联系我们的销售经理李四，电话是13800138000。"
    }
    
    print("=== 测试知识抽取API ===")
    print(f"请求URL: {url}")
    print(f"请求数据: {json.dumps(test_data, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(url, json=test_data, timeout=30)
        print(f"\n响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n响应数据结构:")
            print(f"- success: {data.get('success')}")
            print(f"- data存在: {'data' in data}")
            
            if 'data' in data and data['data']:
                result_data = data['data']
                print(f"\ndata字段内容:")
                print(f"- entities存在: {'entities' in result_data}")
                print(f"- relations存在: {'relations' in result_data}")
                print(f"- statistics存在: {'statistics' in result_data}")
                
                if 'entities' in result_data:
                    entities = result_data['entities']
                    print(f"- entities数量: {len(entities)}")
                    if entities:
                        print(f"- 第一个实体: {entities[0]}")
                
                if 'relations' in result_data:
                    relations = result_data['relations']
                    print(f"- relations数量: {len(relations)}")
                    if relations:
                        print(f"- 第一个关系: {relations[0]}")
                
                if 'statistics' in result_data:
                    stats = result_data['statistics']
                    print(f"- statistics: {stats}")
            
            print(f"\n完整响应数据:")
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            print(f"请求失败: {response.text}")
            
    except Exception as e:
        print(f"请求异常: {e}")

def test_health_check():
    """测试健康检查API"""
    url = "http://localhost:5000/api/health"
    
    print("\n=== 测试健康检查API ===")
    print(f"请求URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
        else:
            print(f"请求失败: {response.text}")
            
    except Exception as e:
        print(f"请求异常: {e}")

if __name__ == '__main__':
    test_health_check()
    test_api_extract()