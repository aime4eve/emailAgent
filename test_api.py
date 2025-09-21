#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识抽取API测试脚本
测试Web API的知识抽取功能
"""

import requests
import json
import time

def test_text_extraction():
    """测试文本知识抽取功能"""
    print("=== 测试文本知识抽取 ===")
    
    # 测试数据
    test_texts = [
        "苹果公司是一家美国科技公司，蒂姆·库克是CEO。",
        "张三在北京大学工作，他是计算机科学系的教授。李四是他的同事。",
        "Apple Inc. is an American technology company. Tim Cook is the CEO.",
        "Microsoft was founded by Bill Gates and Paul Allen in 1975."
    ]
    
    url = "http://localhost:5000/api/extract"
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n--- 测试 {i}: {text[:30]}... ---")
        
        data = {
            "text": text,
            "enable_ml_enhancement": False  # 暂时禁用ML增强
        }
        
        try:
            response = requests.post(url, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✓ 请求成功")
                print(f"  - 实体数量: {result['statistics']['entity_count']}")
                print(f"  - 关系数量: {result['statistics']['relation_count']}")
                print(f"  - 处理时间: {result['processing_time']}秒")
                
                if result['entities']:
                    print("  - 实体列表:")
                    for entity in result['entities'][:3]:  # 显示前3个
                        print(f"    * {entity['text']} ({entity['type']}, 置信度: {entity['confidence']})")
                
                if result['relations']:
                    print("  - 关系列表:")
                    for relation in result['relations'][:3]:  # 显示前3个
                        print(f"    * {relation['source']['text']} -> {relation['target']['text']} ({relation['type']})")
            else:
                print(f"✗ 请求失败: {response.status_code}")
                print(f"  错误信息: {response.text}")
                
        except Exception as e:
            print(f"✗ 请求异常: {str(e)}")
        
        time.sleep(1)  # 避免请求过快

def test_health_check():
    """测试健康检查接口"""
    print("\n=== 测试健康检查 ===")
    
    try:
        response = requests.get("http://localhost:5000/api/health", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ 服务健康状态: {result['status']}")
        else:
            print(f"✗ 健康检查失败: {response.status_code}")
            
    except Exception as e:
        print(f"✗ 健康检查异常: {str(e)}")

def test_service_info():
    """测试服务信息接口"""
    print("\n=== 测试服务信息 ===")
    
    try:
        response = requests.get("http://localhost:5000/", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ 服务信息:")
            print(f"  - 消息: {result['message']}")
            print(f"  - 版本: {result['version']}")
            print(f"  - 状态: {result['status']}")
        else:
            print(f"✗ 服务信息获取失败: {response.status_code}")
            
    except Exception as e:
        print(f"✗ 服务信息获取异常: {str(e)}")

def main():
    """主函数"""
    print("知识抽取API测试开始...")
    print("确保Web服务已启动: python src/web/app.py")
    print("="*50)
    
    # 测试服务基本功能
    test_service_info()
    test_health_check()
    
    # 测试知识抽取功能
    test_text_extraction()
    
    print("\n" + "="*50)
    print("测试完成！")
    print("\n注意事项:")
    print("1. 如果实体数量为0，可能是NLP模型未正确加载")
    print("2. 某些实体类型需要特定的语言模型支持")
    print("3. 可以尝试安装spaCy中文模型: python -m spacy download zh_core_web_sm")

if __name__ == "__main__":
    main()