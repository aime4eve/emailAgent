#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
外贸知识图谱洞察系统启动脚本

演示系统的主要功能和使用方法。
"""

import sys
import os
import logging
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from insights_config import InsightsConfig
from insights.api.insights_api import InsightsAPI
from insights.engines.knowledge_extractor import KnowledgeExtractor
from insights.engines.visualizer import Visualizer
from insights.business.customer_insights import CustomerInsights
from insights.business.risk_analysis import RiskAnalysis

def setup_logging():
    """设置日志记录"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('insights_system.log', encoding='utf-8')
        ]
    )
    
def demo_text_analysis():
    """演示文本分析功能"""
    print("\n" + "="*60)
    print("文本分析演示")
    print("="*60)
    
    # 示例邮件文本
    sample_texts = [
        "我们需要高质量的LED灯具产品，要求符合CE认证标准，预算在10万美元左右。希望能提供详细的产品规格和报价。",
        "对贵公司的太阳能板很感兴趣，希望了解批量采购的价格和交付时间。我们是德国的进口商。",
        "上次订购的产品质量有问题，希望能够退换货并改进质量控制。客户满意度是我们最关心的。"
    ]
    
    try:
        extractor = KnowledgeExtractor()
        extractor.initialized = True  # 模拟初始化
        
        for i, text in enumerate(sample_texts, 1):
            print(f"\n文本 {i}: {text[:50]}...")
            
            # 模拟知识抽取
            result = extractor._create_mock_extraction_result(text)
            
            print(f"抽取到 {len(result.entities)} 个实体:")
            for entity in result.entities[:3]:  # 显示前3个
                print(f"  - {entity.text} ({entity.label}, 置信度: {entity.confidence:.2f})")
                
            print(f"抽取到 {len(result.relations)} 个关系:")
            for relation in result.relations[:2]:  # 显示前2个
                print(f"  - {relation.source.text} -> {relation.target.text} ({relation.relation_type})")
                
    except Exception as e:
        print(f"文本分析演示失败: {e}")
        
def demo_customer_insights():
    """演示客户洞察功能"""
    print("\n" + "="*60)
    print("客户洞察演示")
    print("="*60)
    
    try:
        customer_insights = CustomerInsights()
        customer_insights.initialized = True
        
        # 模拟客户需求分析
        mock_needs = customer_insights._create_mock_customer_needs()
        
        print("客户需求分析结果:")
        for need in mock_needs:
            print(f"  - 客户: {need.customer_id}")
            print(f"    需求类型: {need.need_type}")
            print(f"    描述: {need.description}")
            print(f"    优先级: {need.priority}")
            print(f"    提及次数: {need.mentioned_count}")
            print()
            
    except Exception as e:
        print(f"客户洞察演示失败: {e}")
        
def demo_risk_analysis():
    """演示风险分析功能"""
    print("\n" + "="*60)
    print("风险分析演示")
    print("="*60)
    
    try:
        risk_analysis = RiskAnalysis()
        risk_analysis.initialized = True
        
        # 模拟风险因子识别
        mock_risks = risk_analysis._create_mock_risk_factors()
        
        print("风险因子识别结果:")
        for risk in mock_risks:
            print(f"  - 风险ID: {risk.factor_id}")
            print(f"    风险名称: {risk.factor_name}")
            print(f"    风险类别: {risk.category.value}")
            print(f"    描述: {risk.description}")
            print(f"    影响分数: {risk.impact_score:.1f}")
            print(f"    概率: {risk.probability:.2f}")
            print()
            
    except Exception as e:
        print(f"风险分析演示失败: {e}")
        
def demo_visualization():
    """演示可视化功能"""
    print("\n" + "="*60)
    print("可视化演示")
    print("="*60)
    
    try:
        visualizer = Visualizer()
        visualizer.initialized = True
        
        # 创建示例图表
        test_data = {
            'x': ['1月', '2月', '3月', '4月', '5月'],
            'y': [120, 150, 180, 200, 250],
            'name': '月度销售额'
        }
        
        chart_result = visualizer.create_business_chart('line', test_data, '销售趋势图')
        
        print(f"成功创建 {chart_result.chart_type} 图表")
        print(f"图表标题: {chart_result.title}")
        print(f"数据点数量: {chart_result.metadata.get('data_points', 0)}")
        print(f"创建时间: {chart_result.created_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 保存HTML文件
        html_filename = f"chart_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(chart_result.html_content)
        print(f"图表已保存到: {html_filename}")
        
    except Exception as e:
        print(f"可视化演示失败: {e}")
        
def demo_api_server():
    """演示API服务器"""
    print("\n" + "="*60)
    print("API服务器演示")
    print("="*60)
    
    try:
        api = InsightsAPI()
        app = api.get_app()
        
        print("API服务器已创建")
        print("可用的API端点:")
        
        routes = []
        for rule in app.url_map.iter_rules():
            if rule.endpoint != 'static':
                routes.append(f"  {rule.methods} {rule.rule}")
                
        for route in sorted(routes)[:10]:  # 显示前10个路由
            print(route)
            
        print(f"\n总共注册了 {len(routes)} 个API端点")
        print("\n要启动API服务器，请运行:")
        print("  python -c \"from start_insights_system import start_api_server; start_api_server()\"")
        
    except Exception as e:
        print(f"API服务器演示失败: {e}")
        
def start_api_server():
    """启动API服务器"""
    try:
        print("正在启动外贸知识图谱洞察系统API服务器...")
        
        api = InsightsAPI()
        
        # 尝试初始化（在没有真实数据库的情况下会失败，但不影响演示）
        try:
            api.initialize()
        except Exception as e:
            print(f"注意: 数据库初始化失败 ({e})，但API服务器仍可启动用于演示")
            
        print("API服务器启动成功!")
        print("访问地址: http://localhost:5000")
        print("健康检查: http://localhost:5000/api/v1/health")
        print("按 Ctrl+C 停止服务器")
        
        api.run(host='0.0.0.0', port=5000, debug=True)
        
    except KeyboardInterrupt:
        print("\nAPI服务器已停止")
    except Exception as e:
        print(f"API服务器启动失败: {e}")
        
def show_system_info():
    """显示系统信息"""
    print("\n" + "="*60)
    print("系统信息")
    print("="*60)
    
    try:
        config = InsightsConfig()
        
        print(f"系统名称: 外贸知识图谱洞察系统")
        print(f"版本: 1.0.0")
        print(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\n主要功能模块:")
        modules = [
            "知识抽取引擎 - 从邮件文本中抽取实体和关系",
            "图谱构建引擎 - 构建和管理知识图谱",
            "图算法引擎 - 执行图分析算法",
            "可视化引擎 - 生成图表和可视化",
            "客户洞察分析 - 分析客户需求和行为",
            "产品需求分析 - 分析产品特征和需求",
            "市场洞察分析 - 分析市场趋势和机会",
            "风险预警系统 - 识别和评估业务风险",
            "API接口服务 - 提供RESTful API"
        ]
        
        for i, module in enumerate(modules, 1):
            print(f"  {i}. {module}")
            
        print("\n配置信息:")
        try:
            neo4j_config = config.get_config('neo4j')
            print(f"  Neo4j URI: {neo4j_config.get('uri', 'bolt://localhost:7687')}")
        except:
            print("  Neo4j: 配置未加载")
            
        try:
            redis_config = config.get_config('redis')
            print(f"  Redis: {redis_config.get('host', 'localhost')}:{redis_config.get('port', 6379)}")
        except:
            print("  Redis: 配置未加载")
            
    except Exception as e:
        print(f"获取系统信息失败: {e}")
        
def main():
    """主函数"""
    setup_logging()
    
    print("="*60)
    print("外贸知识图谱洞察系统")
    print("Foreign Trade Knowledge Graph Insights System")
    print("="*60)
    
    show_system_info()
    
    while True:
        print("\n请选择演示功能:")
        print("1. 文本分析演示")
        print("2. 客户洞察演示")
        print("3. 风险分析演示")
        print("4. 可视化演示")
        print("5. API服务器演示")
        print("6. 启动API服务器")
        print("7. 运行系统测试")
        print("0. 退出")
        
        try:
            choice = input("\n请输入选择 (0-7): ").strip()
            
            if choice == '0':
                print("感谢使用外贸知识图谱洞察系统！")
                break
            elif choice == '1':
                demo_text_analysis()
            elif choice == '2':
                demo_customer_insights()
            elif choice == '3':
                demo_risk_analysis()
            elif choice == '4':
                demo_visualization()
            elif choice == '5':
                demo_api_server()
            elif choice == '6':
                start_api_server()
            elif choice == '7':
                print("\n正在运行系统测试...")
                os.system('python test_insights_system.py')
            else:
                print("无效选择，请重新输入")
                
        except KeyboardInterrupt:
            print("\n\n感谢使用外贸知识图谱洞察系统！")
            break
        except Exception as e:
            print(f"操作失败: {e}")
            
if __name__ == "__main__":
    main()