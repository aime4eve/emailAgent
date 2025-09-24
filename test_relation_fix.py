#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试关系抽取修复效果
"""

import requests
import json

def test_relation_extraction():
    """测试关系抽取功能"""
    
    # 测试文本
    test_text = "张三来自北京，他在ABC公司工作。李四是张三的同事，他们一起开发了新产品iPhone。请联系张三，电话是13800138000。"
    
    # API端点
    url = "http://localhost:5000/api/extract"
    
    # 请求数据
    data = {
        "text": test_text
    }
    
    print("=== 测试关系抽取修复效果 ===")
    print(f"测试文本: {test_text}")
    print("\n发送请求到后端API...")
    
    try:
        response = requests.post(url, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                data = result['data']
                
                print("\n✅ 抽取成功！")
                print(f"实体数量: {len(data.get('entities', []))}")
                print(f"关系数量: {len(data.get('relations', []))}")
                
                # 显示实体
                print("\n📋 抽取的实体:")
                for i, entity in enumerate(data.get('entities', []), 1):
                    print(f"  {i}. {entity.get('text', '未知')} ({entity.get('type', '未知类型')}) - 置信度: {entity.get('confidence', 0):.2f}")
                
                # 显示关系
                print("\n🔗 抽取的关系:")
                relations = data.get('relations', [])
                if relations:
                    for i, relation in enumerate(relations, 1):
                        source_text = relation.get('source_text', '未知')
                        target_text = relation.get('target_text', '未知')
                        rel_type = relation.get('type', '未知关系')
                        confidence = relation.get('confidence', 0)
                        
                        print(f"  {i}. {source_text} → {rel_type} → {target_text} (置信度: {confidence:.2f})")
                        
                        # 检查是否还有"未知"实体
                        if source_text == '未知' or target_text == '未知':
                            print(f"     ⚠️  警告: 关系中仍有未知实体")
                        else:
                            print(f"     ✅ 关系实体识别正常")
                else:
                    print("  没有抽取到关系")
                
                # 统计信息
                stats = data.get('statistics', {})
                print(f"\n📊 统计信息:")
                print(f"  处理时间: {stats.get('processing_time', 0):.3f}秒")
                print(f"  平均置信度: {stats.get('confidence', 0):.2f}")
                
                # 检查修复效果
                unknown_relations = [r for r in relations if r.get('source_text') == '未知' or r.get('target_text') == '未知']
                if unknown_relations:
                    print(f"\n❌ 修复未完全成功: 仍有 {len(unknown_relations)} 个关系包含未知实体")
                    return False
                else:
                    print(f"\n✅ 修复成功: 所有关系都正确识别了实体名称")
                    return True
                    
            else:
                print(f"❌ API返回错误: {result.get('error', '未知错误')}")
                return False
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求异常: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_relation_extraction()
    if success:
        print("\n🎉 关系抽取修复验证成功！")
    else:
        print("\n💥 关系抽取仍需进一步修复")