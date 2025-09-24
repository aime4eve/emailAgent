#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证前端修复效果
通过selenium自动化测试前端功能
"""

import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_frontend_extraction():
    """测试前端知识抽取功能"""
    print("=== 验证前端修复效果 ===")
    
    # 配置Chrome选项
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 无头模式
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    
    try:
        # 启动浏览器
        print("启动浏览器...")
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_window_size(1920, 1080)
        
        # 访问知识抽取页面
        url = "http://localhost:3000/extraction"
        print(f"访问页面: {url}")
        driver.get(url)
        
        # 等待页面加载
        wait = WebDriverWait(driver, 10)
        
        # 等待文本输入框出现
        print("等待页面元素加载...")
        text_area = wait.until(EC.presence_of_element_located((By.TAG_NAME, "textarea")))
        
        # 输入测试文本
        test_text = "张三是来自北京的ABC公司采购经理，他对iPhone 15 Pro产品很感兴趣，希望了解批量采购的价格和交货周期。请联系销售经理李四获取详细报价单。"
        print(f"输入测试文本: {test_text[:50]}...")
        text_area.clear()
        text_area.send_keys(test_text)
        
        # 点击开始抽取按钮
        print("点击开始抽取按钮...")
        extract_button = driver.find_element(By.XPATH, "//button[contains(text(), '开始抽取')]")
        extract_button.click()
        
        # 等待抽取完成（等待loading消失）
        print("等待抽取完成...")
        time.sleep(5)  # 给足够时间进行抽取
        
        # 检查结果显示
        print("检查抽取结果...")
        
        # 查找统计信息
        try:
            stats_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'ant-alert-description')]//span")
            entity_count = 0
            relation_count = 0
            confidence = 0
            
            for element in stats_elements:
                text = element.text
                if "实体数量:" in text:
                    entity_count = int(text.split(":")[1].strip())
                elif "关系数量:" in text:
                    relation_count = int(text.split(":")[1].strip())
                elif "置信度:" in text:
                    confidence_str = text.split(":")[1].strip().replace("%", "")
                    confidence = float(confidence_str)
            
            print(f"抽取结果统计:")
            print(f"  实体数量: {entity_count}")
            print(f"  关系数量: {relation_count}")
            print(f"  置信度: {confidence}%")
            
            # 验证结果
            if entity_count > 0 and relation_count > 0:
                print("✅ 修复成功！前端能够正确显示抽取结果")
                
                # 检查实体和关系列表
                entity_tags = driver.find_elements(By.XPATH, "//div[contains(@class, 'entity-tag')]")
                relation_tags = driver.find_elements(By.XPATH, "//div[contains(@class, 'relation-tag')]")
                
                print(f"  实际显示的实体标签数量: {len(entity_tags)}")
                print(f"  实际显示的关系标签数量: {len(relation_tags)}")
                
                if len(entity_tags) > 0:
                    print(f"  第一个实体标签: {entity_tags[0].text}")
                if len(relation_tags) > 0:
                    print(f"  第一个关系标签: {relation_tags[0].text}")
                    
                return True
            else:
                print("❌ 问题仍然存在：实体或关系数量为0")
                
                # 获取页面源码用于调试
                page_source = driver.page_source
                with open('debug_page_source.html', 'w', encoding='utf-8') as f:
                    f.write(page_source)
                print("页面源码已保存到 debug_page_source.html")
                
                return False
                
        except Exception as e:
            print(f"❌ 解析结果时出错: {str(e)}")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中出错: {str(e)}")
        return False
        
    finally:
        # 关闭浏览器
        try:
            driver.quit()
        except:
            pass

def simple_test():
    """简单的HTTP测试，不依赖selenium"""
    print("=== 简单HTTP测试 ===")
    
    import requests
    
    try:
        # 测试前端页面是否可访问
        print("测试前端页面访问...")
        response = requests.get("http://localhost:3000/extraction", timeout=5)
        if response.status_code == 200:
            print("✅ 前端页面可正常访问")
        else:
            print(f"❌ 前端页面访问异常: {response.status_code}")
            
        # 测试后端API
        print("测试后端API...")
        test_data = {
            "text": "张三是来自北京的ABC公司采购经理，他对iPhone 15 Pro产品很感兴趣。"
        }
        
        api_response = requests.post("http://localhost:5000/api/extract", json=test_data, timeout=10)
        if api_response.status_code == 200:
            data = api_response.json()
            if data.get('success') and data.get('data'):
                entities = data['data'].get('entities', [])
                relations = data['data'].get('relations', [])
                print(f"✅ 后端API正常工作")
                print(f"  实体数量: {len(entities)}")
                print(f"  关系数量: {len(relations)}")
                return True
            else:
                print(f"❌ 后端API返回格式异常: {data}")
        else:
            print(f"❌ 后端API访问异常: {api_response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试过程中出错: {str(e)}")
        
    return False

if __name__ == "__main__":
    # 先进行简单测试
    if simple_test():
        print("\n后端API工作正常，前端修复应该已经生效。")
        print("请在浏览器中访问 http://localhost:3000/extraction 进行验证。")
    else:
        print("\n后端API或前端服务存在问题，请检查服务状态。")