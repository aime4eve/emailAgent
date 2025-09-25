#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复验证测试脚本

验证前端错误日志修复是否成功。
"""

import requests
import json
import time
from typing import Dict, Any

class FixesVerificationTest:
    """修复验证测试类"""
    
    def __init__(self):
        """初始化测试"""
        self.backend_url = "http://localhost:5000"
        self.frontend_url = "http://localhost:3000"
        
    def test_backend_health(self) -> bool:
        """测试后端健康检查"""
        try:
            print("\n=== 测试后端健康检查 ===")
            response = requests.get(f"{self.backend_url}/api/v1/health", timeout=5)
            print(f"状态码: {response.status_code}")
            print(f"响应: {response.json()}")
            return response.status_code == 200
        except Exception as e:
            print(f"健康检查失败: {e}")
            return False
            
    def test_backend_status(self) -> bool:
        """测试后端状态接口"""
        try:
            print("\n=== 测试后端状态接口 ===")
            response = requests.get(f"{self.backend_url}/api/v1/status", timeout=5)
            print(f"状态码: {response.status_code}")
            print(f"响应: {response.json()}")
            return response.status_code == 200
        except Exception as e:
            print(f"状态接口测试失败: {e}")
            return False
            
    def test_extraction_api(self) -> bool:
        """测试知识抽取API"""
        try:
            print("\n=== 测试知识抽取API ===")
            test_data = {
                "text": "我们公司需要采购一批工业设备，请提供报价。"
            }
            response = requests.post(
                f"{self.backend_url}/api/v1/extraction/analyze",
                json=test_data,
                timeout=10
            )
            print(f"状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"抽取到 {len(data.get('entities', []))} 个实体")
                print(f"抽取到 {len(data.get('relations', []))} 个关系")
                return True
            else:
                print(f"错误响应: {response.text}")
                return False
        except Exception as e:
            print(f"知识抽取API测试失败: {e}")
            return False
            
    def test_insights_apis(self) -> bool:
        """测试洞察分析API"""
        try:
            print("\n=== 测试洞察分析API ===")
            
            # 测试客户洞察
            response = requests.get(f"{self.backend_url}/api/v1/insights/customer-analysis", timeout=5)
            print(f"客户洞察API状态码: {response.status_code}")
            customer_success = response.status_code == 200
            
            # 测试产品分析
            response = requests.get(f"{self.backend_url}/api/v1/insights/product-analysis", timeout=5)
            print(f"产品分析API状态码: {response.status_code}")
            product_success = response.status_code == 200
            
            # 测试风险分析
            response = requests.get(f"{self.backend_url}/api/v1/insights/risk-analysis", timeout=5)
            print(f"风险分析API状态码: {response.status_code}")
            risk_success = response.status_code == 200
            
            return customer_success and product_success and risk_success
            
        except Exception as e:
            print(f"洞察分析API测试失败: {e}")
            return False
            
    def test_frontend_accessibility(self) -> bool:
        """测试前端可访问性"""
        try:
            print("\n=== 测试前端可访问性 ===")
            response = requests.get(self.frontend_url, timeout=5)
            print(f"前端状态码: {response.status_code}")
            return response.status_code == 200
        except Exception as e:
            print(f"前端可访问性测试失败: {e}")
            return False
            
    def run_all_tests(self) -> Dict[str, bool]:
        """运行所有测试"""
        print("开始验证修复效果...")
        
        results = {
            "backend_health": self.test_backend_health(),
            "backend_status": self.test_backend_status(),
            "extraction_api": self.test_extraction_api(),
            "insights_apis": self.test_insights_apis(),
            "frontend_accessibility": self.test_frontend_accessibility()
        }
        
        print("\n=== 测试结果汇总 ===")
        for test_name, result in results.items():
            status = "✅ 通过" if result else "❌ 失败"
            print(f"{test_name}: {status}")
            
        success_count = sum(results.values())
        total_count = len(results)
        print(f"\n总体结果: {success_count}/{total_count} 项测试通过")
        
        if success_count == total_count:
            print("🎉 所有修复验证成功！")
        else:
            print("⚠️ 部分测试失败，需要进一步检查")
            
        return results

def main():
    """主函数"""
    tester = FixesVerificationTest()
    results = tester.run_all_tests()
    
    # 返回退出码
    if all(results.values()):
        exit(0)  # 所有测试通过
    else:
        exit(1)  # 有测试失败

if __name__ == "__main__":
    main()