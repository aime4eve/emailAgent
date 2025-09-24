#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试知识抽取功能修复
"""

import requests
import json
import time

def test_extraction_api():
    """测试知识抽取API"""
    url = "http://localhost:5000/api/extract"
    
    # 测试数据
    test_data = {
        "text": "我是张三，来自北京的ABC公司。我们公司专门生产电子产品，包括手机、平板电脑和笔记本电脑。我们希望与贵公司建立长期的合作关系。请联系我们的销售经理李四，电话是13800138000。"
    }
    
    print("=== 测试知识抽取API ===")
    print(f"请求URL: {url}")
    print(f"请求数据: {json.dumps(test_data, ensure_ascii=False, indent=2)}")
    print()
    
    try:
        # 发送请求
        start_time = time.time()
        response = requests.post(url, json=test_data, timeout=30)
        end_time = time.time()
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应时间: {(end_time - start_time):.2f}秒")
        print()
        
        if response.status_code == 200:
            result = response.json()
            print("=== API响应结果 ===")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            print()
            
            if result.get('success'):
                data = result.get('data', {})
                entities = data.get('entities', [])
                relations = data.get('relations', [])
                statistics = data.get('statistics', {})
                
                print("=== 抽取结果分析 ===")
                print(f"实体数量: {len(entities)}")
                print(f"关系数量: {len(relations)}")
                print(f"置信度: {statistics.get('confidence', 0):.2f}")
                print(f"处理时间: {statistics.get('processing_time', 0):.2f}秒")
                print()
                
                if entities:
                    print("=== 实体列表 ===")
                    for i, entity in enumerate(entities, 1):
                        print(f"{i}. {entity.get('text')} ({entity.get('type')}) - 置信度: {entity.get('confidence', 0):.2f}")
                    print()
                
                if relations:
                    print("=== 关系列表 ===")
                    for i, relation in enumerate(relations, 1):
                        source_text = relation.get('source', {}).get('text', '未知')
                        target_text = relation.get('target', {}).get('text', '未知')
                        rel_type = relation.get('type', '未知关系')
                        confidence = relation.get('confidence', 0)
                        print(f"{i}. {source_text} → {rel_type} → {target_text} - 置信度: {confidence:.2f}")
                    print()
                
                print("✅ 知识抽取功能正常工作！")
                return True
            else:
                print(f"❌ API返回失败: {result.get('error', '未知错误')}")
                return False
        else:
            print(f"❌ HTTP请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return False

def test_health_check():
    """测试健康检查API"""
    url = "http://localhost:5000/api/health"
    
    print("=== 测试健康检查API ===")
    print(f"请求URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"健康状态: {result.get('status', '未知')}")
            print("✅ 后端服务正常运行！")
            return True
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
        return False

if __name__ == "__main__":
    print("开始测试知识抽取功能修复...")
    print()
    
    # 测试健康检查
    health_ok = test_health_check()
    print()
    
    if health_ok:
        # 测试知识抽取
        extraction_ok = test_extraction_api()
        
        if extraction_ok:
            print("🎉 所有测试通过！知识抽取功能修复成功！")
        else:
            print("❌ 知识抽取功能仍有问题")
    else:
        print("❌ 后端服务不可用，请检查服务器状态")