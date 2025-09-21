#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CORS和API连通性测试脚本
"""

import requests
import json

def test_api_connectivity():
    """测试API连通性"""
    base_url = "http://localhost:5000"
    
    print("=== API连通性测试 ===")
    
    # 测试主页
    try:
        response = requests.get(f"{base_url}/")
        print(f"✓ 主页访问: {response.status_code}")
        print(f"  响应: {response.json()}")
    except Exception as e:
        print(f"✗ 主页访问失败: {e}")
    
    # 测试健康检查
    try:
        response = requests.get(f"{base_url}/api/health")
        print(f"✓ 健康检查: {response.status_code}")
        print(f"  响应: {response.json()}")
    except Exception as e:
        print(f"✗ 健康检查失败: {e}")
    
    # 测试CORS预检请求
    try:
        headers = {
            'Origin': 'http://localhost:3000',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        response = requests.options(f"{base_url}/api/extract", headers=headers)
        print(f"✓ CORS预检请求: {response.status_code}")
        print(f"  CORS头: {dict(response.headers)}")
    except Exception as e:
        print(f"✗ CORS预检请求失败: {e}")
    
    # 测试知识抽取接口
    try:
        headers = {
            'Content-Type': 'application/json',
            'Origin': 'http://localhost:3000'
        }
        data = {
            'text': '张三在北京大学工作，他是计算机科学系的教授。'
        }
        response = requests.post(f"{base_url}/api/extract", 
                               json=data, headers=headers)
        print(f"✓ 知识抽取接口: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"  实体数量: {result.get('statistics', {}).get('entity_count', 0)}")
            print(f"  关系数量: {result.get('statistics', {}).get('relation_count', 0)}")
        else:
            print(f"  错误: {response.text}")
    except Exception as e:
        print(f"✗ 知识抽取接口失败: {e}")
    
    # 测试文件上传接口（OPTIONS）
    try:
        headers = {
            'Origin': 'http://localhost:3000',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        response = requests.options(f"{base_url}/api/extract/file", headers=headers)
        print(f"✓ 文件上传CORS预检: {response.status_code}")
    except Exception as e:
        print(f"✗ 文件上传CORS预检失败: {e}")

if __name__ == '__main__':
    test_api_connectivity()