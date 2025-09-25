# -*- coding: utf-8 -*-
"""
洞察系统API接口

提供完整的RESTful API服务。
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

from ..engines.knowledge_extractor import KnowledgeExtractor
from ..engines.graph_builder import GraphBuilder
from ..engines.graph_algorithms import GraphAlgorithms
from ..engines.visualizer import Visualizer
from ..business.customer_insights import CustomerInsights
from ..business.product_analysis import ProductAnalysis
from ..core.database_manager import DatabaseManager
from ..core.exceptions import InsightsException
from insights_config import InsightsConfig

class InsightsAPI:
    """洞察系统API服务
    
    提供完整的API接口服务。
    """
    
    def __init__(self):
        """初始化API服务"""
        self.logger = logging.getLogger(__name__)
        self.app = Flask(__name__)
        CORS(self.app)
        
        # 初始化组件
        self.config = InsightsConfig()
        self.db_manager = DatabaseManager()
        self.knowledge_extractor = KnowledgeExtractor()
        self.graph_builder = GraphBuilder()
        self.graph_algorithms = GraphAlgorithms()
        self.visualizer = Visualizer()
        self.customer_insights = CustomerInsights()
        self.product_analysis = ProductAnalysis()
        
        # 注册路由
        self._register_routes()
        
    def initialize(self) -> bool:
        """初始化API服务
        
        Returns:
            是否初始化成功
        """
        try:
            # 初始化数据库连接
            neo4j_config = self.config.get_config('neo4j')
            self.db_manager.initialize_neo4j(
                neo4j_config['uri'],
                neo4j_config['username'],
                neo4j_config['password'],
                neo4j_config['database']
            )
            
            redis_config = self.config.get_config('redis')
            self.db_manager.initialize_redis(
                redis_config['host'],
                redis_config['port'],
                redis_config['db'],
                redis_config['password']
            )
            
            # 初始化各个组件
            self.knowledge_extractor.initialize()
            self.graph_builder.initialize()
            self.graph_algorithms.initialize()
            self.visualizer.initialize()
            self.customer_insights.initialize()
            self.product_analysis.initialize()
            
            self.logger.info("洞察系统API初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"洞察系统API初始化失败: {e}")
            return False
            
    def _register_routes(self):
        """注册API路由"""
        
        @self.app.route('/api/v1/health', methods=['GET'])
        def health_check():
            """健康检查"""
            try:
                health_status = self.db_manager.health_check()
                return jsonify({
                    'status': 'healthy',
                    'timestamp': datetime.now().isoformat(),
                    'databases': health_status
                })
            except Exception as e:
                return jsonify({
                    'status': 'unhealthy',
                    'error': str(e)
                }), 500
                
        @self.app.route('/api/v1/status', methods=['GET'])
        def get_status():
            """获取服务状态"""
            try:
                return jsonify({
                    'service': 'Insights API',
                    'version': '1.0.0',
                    'status': 'running',
                    'timestamp': datetime.now().isoformat(),
                    'endpoints': {
                        'health': '/api/v1/health',
                        'extraction': '/api/v1/extraction/analyze',
                        'graph': '/api/v1/graph/*',
                        'insights': '/api/v1/insights/*'
                    }
                })
            except Exception as e:
                return jsonify({
                    'error': str(e)
                }), 500
                
        @self.app.route('/api/v1/extraction/analyze', methods=['POST'])
        def analyze_text():
            """分析文本并抽取知识"""
            try:
                data = request.get_json()
                text = data.get('text', '')
                
                if not text:
                    return jsonify({'error': 'Text is required'}), 400
                    
                # 抽取知识
                result = self.knowledge_extractor.extract_knowledge(text)
                
                # 构建图谱
                build_result = self.graph_builder.build_graph_from_extraction(
                    result, data.get('source_id')
                )
                
                return jsonify({
                    'entities': [{
                        'text': e.text,
                        'label': e.label,
                        'confidence': e.confidence,
                        'start': e.start,
                        'end': e.end
                    } for e in result.entities],
                    'relations': [{
                        'source': r.source.text,
                        'target': r.target.text,
                        'relation_type': r.relation_type,
                        'confidence': r.confidence
                    } for r in result.relations],
                    'graph_build_result': build_result
                })
                
            except Exception as e:
                self.logger.error(f"文本分析失败: {e}")
                return jsonify({'error': str(e)}), 500
                
        @self.app.route('/api/v1/graph/entities', methods=['GET'])
        def get_entities():
            """获取图谱实体"""
            try:
                label = request.args.get('label')
                limit = int(request.args.get('limit', 100))
                
                entities = self.graph_builder.query_nodes(label=label, limit=limit)
                
                return jsonify({
                    'entities': entities,
                    'count': len(entities)
                })
                
            except Exception as e:
                self.logger.error(f"获取实体失败: {e}")
                return jsonify({'error': str(e)}), 500
                
        @self.app.route('/api/v1/graph/relationships', methods=['GET'])
        def get_relationships():
            """获取图谱关系"""
            try:
                source_id = request.args.get('source_id')
                target_id = request.args.get('target_id')
                relation_type = request.args.get('relation_type')
                limit = int(request.args.get('limit', 100))
                
                relationships = self.graph_builder.query_relationships(
                    source_id=source_id,
                    target_id=target_id,
                    relation_type=relation_type,
                    limit=limit
                )
                
                return jsonify({
                    'relationships': relationships,
                    'count': len(relationships)
                })
                
            except Exception as e:
                self.logger.error(f"获取关系失败: {e}")
                return jsonify({'error': str(e)}), 500
                
        @self.app.route('/api/v1/graph/statistics', methods=['GET'])
        def get_graph_statistics():
            """获取图谱统计信息"""
            try:
                stats = self.graph_builder.get_graph_statistics()
                
                return jsonify({
                    'node_count': stats.node_count,
                    'edge_count': stats.edge_count,
                    'node_types': stats.node_types,
                    'edge_types': stats.edge_types,
                    'avg_degree': stats.avg_degree,
                    'density': stats.density
                })
                
            except Exception as e:
                self.logger.error(f"获取图谱统计失败: {e}")
                return jsonify({'error': str(e)}), 500
                
        @self.app.route('/api/v1/algorithms/centrality', methods=['POST'])
        def calculate_centrality():
            """计算中心性"""
            try:
                data = request.get_json()
                algorithm = data.get('algorithm', 'pagerank')
                top_k = data.get('top_k', 10)
                
                results = self.graph_algorithms.find_influential_nodes(algorithm, top_k)
                
                return jsonify({
                    'algorithm': algorithm,
                    'results': [{
                        'node_id': r.node_id,
                        'score': r.score,
                        'rank': r.rank
                    } for r in results]
                })
                
            except Exception as e:
                self.logger.error(f"中心性计算失败: {e}")
                return jsonify({'error': str(e)}), 500
                
        @self.app.route('/api/v1/algorithms/communities', methods=['POST'])
        def detect_communities():
            """社区发现"""
            try:
                data = request.get_json()
                resolution = data.get('resolution', 1.0)
                
                communities = self.graph_algorithms.detect_communities_louvain(resolution)
                
                return jsonify({
                    'communities': [{
                        'community_id': c.community_id,
                        'size': c.size,
                        'nodes': c.nodes[:10],  # 限制返回节点数量
                        'modularity': c.modularity
                    } for c in communities]
                })
                
            except Exception as e:
                self.logger.error(f"社区发现失败: {e}")
                return jsonify({'error': str(e)}), 500
                
        @self.app.route('/api/v1/visualization/graph', methods=['POST'])
        def create_graph_visualization():
            """创建图谱可视化"""
            try:
                data = request.get_json()
                filter_params = data.get('filters', {})
                
                visualization = self.visualizer.create_graph_visualization(
                    filter_params=filter_params
                )
                
                return jsonify({
                    'html_content': visualization.html_content,
                    'json_data': visualization.json_data,
                    'metadata': visualization.metadata
                })
                
            except Exception as e:
                self.logger.error(f"图谱可视化创建失败: {e}")
                return jsonify({'error': str(e)}), 500
                
        @self.app.route('/api/v1/insights/customer-analysis', methods=['GET', 'POST'])
        def analyze_customer_insights():
            """客户洞察分析"""
            try:
                if request.method == 'GET':
                    customer_id = request.args.get('customer_id')
                    analysis_type = request.args.get('analysis_type', 'all')
                else:
                    data = request.get_json() or {}
                    customer_id = data.get('customer_id')
                    analysis_type = data.get('analysis_type', 'all')
                
                results = {}
                
                if analysis_type in ['all', 'needs']:
                    needs = self.customer_insights.analyze_customer_needs(customer_id)
                    results['needs'] = [{
                        'customer_id': n.customer_id,
                        'need_type': n.need_type,
                        'description': n.description,
                        'priority': n.priority,
                        'mentioned_count': n.mentioned_count
                    } for n in needs]
                    
                if analysis_type in ['all', 'intent']:
                    intents = self.customer_insights.identify_purchase_intent(customer_id)
                    results['purchase_intents'] = [{
                        'customer_id': i.customer_id,
                        'intent_level': i.intent_level,
                        'confidence_score': i.confidence_score,
                        'key_indicators': i.key_indicators,
                        'products_of_interest': i.products_of_interest
                    } for i in intents]
                    
                if analysis_type in ['all', 'value']:
                    values = self.customer_insights.evaluate_customer_value(customer_id)
                    results['customer_values'] = [{
                        'customer_id': v.customer_id,
                        'tier': v.tier,
                        'total_score': v.total_score,
                        'transaction_value': v.transaction_value,
                        'lifetime_value': v.lifetime_value
                    } for v in values]
                    
                return jsonify(results)
                
            except Exception as e:
                self.logger.error(f"客户洞察分析失败: {e}")
                return jsonify({'error': str(e)}), 500
                
        @self.app.route('/api/v1/insights/product-analysis', methods=['GET', 'POST'])
        def analyze_product_insights():
            """产品洞察分析"""
            try:
                if request.method == 'GET':
                    product_id = request.args.get('product_id')
                    analysis_type = request.args.get('analysis_type', 'all')
                else:
                    data = request.get_json() or {}
                    product_id = data.get('product_id')
                    analysis_type = data.get('analysis_type', 'all')
                
                results = {}
                
                if analysis_type in ['all', 'features']:
                    features = self.product_analysis.extract_product_features(product_id)
                    results['features'] = [{
                        'product_id': f.product_id,
                        'feature_type': f.feature_type,
                        'description': f.description,
                        'importance': f.importance,
                        'customer_requests': f.customer_requests
                    } for f in features]
                    
                if analysis_type in ['all', 'specs']:
                    specs = self.product_analysis.analyze_technical_specs(product_id)
                    results['technical_specs'] = [{
                        'product_id': s.product_id,
                        'spec_type': s.spec_type,
                        'specification': s.specification,
                        'priority': s.priority,
                        'compliance_required': s.compliance_required
                    } for s in specs]
                    
                if analysis_type in ['all', 'customization']:
                    customizations = self.product_analysis.identify_customization_requests()
                    if product_id:
                        customizations = [c for c in customizations if c.product_id == product_id]
                    results['customization_requests'] = [{
                        'customer_id': c.customer_id,
                        'product_id': c.product_id,
                        'customization_type': c.customization_type,
                        'description': c.description,
                        'complexity': c.complexity,
                        'feasibility': c.feasibility,
                        'business_value': c.business_value
                    } for c in customizations]
                    
                return jsonify(results)
                
            except Exception as e:
                self.logger.error(f"产品洞察分析失败: {e}")
                return jsonify({'error': str(e)}), 500
                
        @self.app.route('/api/v1/insights/risk-analysis', methods=['GET', 'POST'])
        def analyze_risk_insights():
            """风险分析"""
            try:
                if request.method == 'GET':
                    risk_type = request.args.get('risk_type', 'all')
                    customer_id = request.args.get('customer_id')
                else:
                    data = request.get_json() or {}
                    risk_type = data.get('risk_type', 'all')
                    customer_id = data.get('customer_id')
                
                # 返回模拟的风险分析数据
                risk_factors = [
                    {
                        'factor_id': 'RF001',
                        'factor_name': '客户信用风险',
                        'category': '信用风险',
                        'description': '基于历史交易记录的客户信用评估',
                        'impact_score': 0.7,
                        'probability': 0.3,
                        'mitigation_strategies': ['要求预付款', '购买信用保险', '缩短付款期限']
                    },
                    {
                        'factor_id': 'RF002',
                        'factor_name': '汇率波动风险',
                        'category': '市场风险',
                        'description': '外汇汇率变动对交易价值的影响',
                        'impact_score': 0.6,
                        'probability': 0.8,
                        'mitigation_strategies': ['使用远期合约', '多币种定价', '汇率条款']
                    },
                    {
                        'factor_id': 'RF003',
                        'factor_name': '合规风险',
                        'category': '合规风险',
                        'description': '产品或服务不符合目标市场法规要求',
                        'impact_score': 0.9,
                        'probability': 0.2,
                        'mitigation_strategies': ['法规咨询', '合规认证', '定期审查']
                    }
                ]
                
                if risk_type != 'all':
                    risk_factors = [rf for rf in risk_factors if rf['category'] == risk_type]
                
                return jsonify(risk_factors)
                
            except Exception as e:
                self.logger.error(f"风险分析失败: {e}")
                return jsonify({'error': str(e)}), 500
                
        @self.app.route('/api/v1/dashboard', methods=['GET'])
        def get_dashboard():
            """获取仪表板数据"""
            try:
                # 获取图谱统计
                graph_stats = self.graph_builder.get_graph_statistics()
                
                # 获取最新的客户洞察
                recent_intents = self.customer_insights.identify_purchase_intent()
                high_intent_customers = [i for i in recent_intents if i.intent_level == '高意向'][:5]
                
                # 获取产品趋势
                product_trends = self.product_analysis.identify_product_trends([30])
                
                dashboard_data = {
                    'graph_statistics': {
                        'node_count': graph_stats.node_count,
                        'edge_count': graph_stats.edge_count,
                        'node_types': graph_stats.node_types,
                        'edge_types': graph_stats.edge_types
                    },
                    'high_intent_customers': [{
                        'customer_id': i.customer_id,
                        'confidence_score': i.confidence_score,
                        'products_of_interest': i.products_of_interest[:3]
                    } for i in high_intent_customers],
                    'product_trends': [{
                        'product_id': t.product_id,
                        'trend_type': t.trend_type,
                        'direction': t.direction,
                        'strength': t.strength,
                        'impact_score': t.impact_score
                    } for t in product_trends[:5]],
                    'timestamp': datetime.now().isoformat()
                }
                
                return jsonify(dashboard_data)
                
            except Exception as e:
                self.logger.error(f"获取仪表板数据失败: {e}")
                return jsonify({'error': str(e)}), 500
                
        @self.app.errorhandler(InsightsException)
        def handle_insights_exception(e):
            """处理洞察系统异常"""
            return jsonify(e.to_dict()), 400
            
        @self.app.errorhandler(Exception)
        def handle_general_exception(e):
            """处理通用异常"""
            self.logger.error(f"未处理的异常: {e}")
            return jsonify({
                'error': 'Internal server error',
                'message': str(e)
            }), 500
            
    def run(self, host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
        """运行API服务
        
        Args:
            host: 主机地址
            port: 端口号
            debug: 是否调试模式
        """
        self.logger.info(f"启动洞察系统API服务: {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)
        
    def get_app(self):
        """获取Flask应用实例
        
        Returns:
            Flask应用实例
        """
        return self.app