#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
洞察系统前端集成测试

测试前端和后端的集成是否正常工作
"""

import requests
import json
from typing import Dict, Any

def test_api_health() -> bool:
    """测试API健康检查"""
    try:
        response = requests.get('http://localhost:5000/api/v1/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API健康检查通过: {data['status']}")
            print(f"   数据库状态: {data['databases']}")
            return True
        else:
            print(f"❌ API健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API连接失败: {e}")
        return False

def test_text_analysis() -> bool:
    """测试文本分析功能"""
    try:
        test_text = "我们公司对您的LED灯产品很感兴趣，希望了解价格和交货时间。"
        response = requests.post(
            'http://localhost:5000/api/v1/extraction/analyze',
            json={'text': test_text},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 文本分析成功")
            print(f"   提取的实体数量: {len(data.get('data', {}).get('entities', []))}")
            print(f"   提取的关系数量: {len(data.get('data', {}).get('relations', []))}")
            return True
        else:
            print(f"❌ 文本分析失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 文本分析请求失败: {e}")
        return False

def test_customer_insights() -> bool:
    """测试客户洞察功能"""
    try:
        response = requests.get(
            'http://localhost:5000/api/v1/insights/customer-analysis',
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 客户洞察获取成功")
            insights = data.get('data', [])
            print(f"   洞察数量: {len(insights)}")
            return True
        else:
            print(f"❌ 客户洞察获取失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 客户洞察请求失败: {e}")
        return False

def test_product_analysis() -> bool:
    """测试产品分析功能"""
    try:
        response = requests.get(
            'http://localhost:5000/api/v1/insights/product-analysis',
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 产品分析获取成功")
            analysis = data.get('data', [])
            print(f"   分析数量: {len(analysis)}")
            return True
        else:
            print(f"❌ 产品分析获取失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 产品分析请求失败: {e}")
        return False

def test_risk_analysis() -> bool:
    """测试风险分析功能"""
    try:
        response = requests.get(
            'http://localhost:5000/api/v1/insights/risk-analysis',
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 风险分析获取成功")
            # 风险分析直接返回数组，不是包装在data字段中
            risks = data if isinstance(data, list) else data.get('data', [])
            print(f"   风险因子数量: {len(risks)}")
            return True
        else:
            print(f"❌ 风险分析获取失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 风险分析请求失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("🚀 开始洞察系统前端集成测试...\n")
    
    tests = [
        ("API健康检查", test_api_health),
        ("文本分析", test_text_analysis),
        ("客户洞察", test_customer_insights),
        ("产品分析", test_product_analysis),
        ("风险分析", test_risk_analysis)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 测试: {test_name}")
        if test_func():
            passed += 1
        print("-" * 50)
    
    print(f"\n📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！洞察系统前端集成成功！")
        return True
    else:
        print(f"⚠️  有 {total - passed} 个测试失败，请检查相关功能。")
        return False

if __name__ == '__main__':
    main()