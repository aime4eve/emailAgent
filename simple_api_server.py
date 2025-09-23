#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版API服务器
不依赖ArangoDB，使用模拟数据快速启动
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """创建Flask应用"""
    app = Flask(__name__)
    
    # 配置CORS
    CORS(app, 
         origins=['http://localhost:3000', 'http://localhost:5173'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         allow_headers=['Content-Type', 'Authorization'],
         supports_credentials=True)
    
    # 模拟数据
    mock_ontologies = [
        {
            'id': '1',
            'name': '外贸询盘本体',
            'description': '外贸询盘业务的核心本体模型',
            'version': '1.0.0',
            'category': 'business',
            'status': 'active',
            'created_at': '2024-01-15T10:30:00Z',
            'updated_at': '2024-01-20T14:45:00Z',
            'entities_count': 156,
            'relations_count': 89,
            'author': '系统管理员'
        },
        {
            'id': '2',
            'name': '客户关系本体',
            'description': '客户关系管理相关的本体定义',
            'version': '1.1.0',
            'category': 'customer',
            'status': 'active',
            'created_at': '2024-01-10T09:15:00Z',
            'updated_at': '2024-01-25T16:20:00Z',
            'entities_count': 78,
            'relations_count': 45,
            'author': '业务分析师'
        },
        {
            'id': '3',
            'name': '产品信息本体',
            'description': '产品信息和规格的本体模型',
            'version': '2.0.0',
            'category': 'product',
            'status': 'draft',
            'created_at': '2024-01-05T11:00:00Z',
            'updated_at': '2024-01-22T13:30:00Z',
            'entities_count': 234,
            'relations_count': 167,
            'author': '产品经理'
        }
    ]
    
    @app.route('/')
    def index():
        """主页"""
        return jsonify({
            'message': '外贸询盘知识图谱系统API',
            'version': '1.0.0',
            'status': 'running',
            'timestamp': datetime.now().isoformat()
        })
    
    @app.route('/api/health')
    def health_check():
        """健康检查"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat()
        })
    
    @app.route('/api/ontologies', methods=['GET', 'OPTIONS'])
    def get_ontologies():
        """获取本体列表"""
        if request.method == 'OPTIONS':
            return jsonify({'status': 'ok'}), 200
        
        try:
            # 获取查询参数
            page = request.args.get('page', 1, type=int)
            page_size = min(request.args.get('page_size', 10, type=int), 100)
            search = request.args.get('search', '')
            category = request.args.get('category', '')
            
            logger.info(f"获取本体列表 - 页码: {page}, 页大小: {page_size}, 搜索: {search}")
            
            # 应用搜索过滤
            filtered_ontologies = mock_ontologies
            if search:
                filtered_ontologies = [
                    ont for ont in filtered_ontologies 
                    if search.lower() in ont['name'].lower() or search.lower() in ont['description'].lower()
                ]
            
            # 应用类别过滤
            if category:
                filtered_ontologies = [ont for ont in filtered_ontologies if ont['category'] == category]
            
            # 计算分页
            total = len(filtered_ontologies)
            start = (page - 1) * page_size
            end = start + page_size
            ontologies = filtered_ontologies[start:end]
            
            return jsonify({
                'success': True,
                'data': ontologies,
                'pagination': {
                    'page': page,
                    'page_size': page_size,
                    'total': total,
                    'pages': (total + page_size - 1) // page_size
                }
            }), 200
            
        except Exception as e:
            logger.error(f"获取本体列表失败: {str(e)}")
            return jsonify({
                'success': False,
                'error': '获取本体列表失败',
                'message': str(e)
            }), 500
    
    @app.route('/api/ontologies/statistics', methods=['GET', 'OPTIONS'])
    def get_ontology_statistics():
        """获取本体统计信息"""
        if request.method == 'OPTIONS':
            return jsonify({'status': 'ok'}), 200
        
        try:
            logger.info("获取本体统计信息")
            
            # 模拟统计数据
            statistics = {
                'total_ontologies': len(mock_ontologies),
                'active_ontologies': len([ont for ont in mock_ontologies if ont['status'] == 'active']),
                'draft_ontologies': len([ont for ont in mock_ontologies if ont['status'] == 'draft']),
                'total_entities': sum(ont['entities_count'] for ont in mock_ontologies),
                'total_relations': sum(ont['relations_count'] for ont in mock_ontologies),
                'categories': {
                    'business': len([ont for ont in mock_ontologies if ont['category'] == 'business']),
                    'customer': len([ont for ont in mock_ontologies if ont['category'] == 'customer']),
                    'product': len([ont for ont in mock_ontologies if ont['category'] == 'product'])
                },
                'recent_activities': [
                    {
                        'action': '更新本体',
                        'ontology_name': '客户关系本体',
                        'timestamp': '2024-01-25T16:20:00Z',
                        'user': '业务分析师'
                    },
                    {
                        'action': '创建本体',
                        'ontology_name': '产品信息本体',
                        'timestamp': '2024-01-22T13:30:00Z',
                        'user': '产品经理'
                    }
                ],
                'usage_metrics': {
                    'queries_today': 156,
                    'queries_this_week': 1234,
                    'queries_this_month': 5678,
                    'avg_response_time': 0.25
                }
            }
            
            return jsonify({
                'success': True,
                'data': statistics
            }), 200
            
        except Exception as e:
            logger.error(f"获取本体统计信息失败: {str(e)}")
            return jsonify({
                'success': False,
                'error': '获取统计信息失败',
                'message': str(e)
            }), 500
    
    @app.route('/api/ontologies/<ontology_id>', methods=['GET', 'PUT', 'DELETE', 'OPTIONS'])
    def handle_ontology(ontology_id):
        """处理单个本体的操作"""
        if request.method == 'OPTIONS':
            return jsonify({'status': 'ok'}), 200
        
        try:
            if request.method == 'GET':
                # 获取本体详情
                ontology_detail = {
                    'id': ontology_id,
                    'name': '外贸询盘本体',
                    'description': '外贸询盘业务的核心本体模型，包含客户、产品、需求等核心概念',
                    'version': '1.0.0',
                    'category': 'business',
                    'status': 'active',
                    'created_at': '2024-01-15T10:30:00Z',
                    'updated_at': '2024-01-20T14:45:00Z',
                    'author': '系统管理员',
                    'entities': [
                        {'name': '客户', 'type': 'Customer', 'count': 45},
                        {'name': '公司', 'type': 'Company', 'count': 32},
                        {'name': '产品', 'type': 'Product', 'count': 67},
                        {'name': '需求', 'type': 'Demand', 'count': 12}
                    ],
                    'relations': [
                        {'name': '来自', 'type': 'comes_from', 'count': 23},
                        {'name': '隶属于', 'type': 'belongs_to', 'count': 34},
                        {'name': '询问', 'type': 'inquires_about', 'count': 18},
                        {'name': '表达', 'type': 'expresses', 'count': 14}
                    ],
                    'statistics': {
                        'total_entities': 156,
                        'total_relations': 89,
                        'last_updated': '2024-01-20T14:45:00Z'
                    }
                }
                
                return jsonify({
                    'success': True,
                    'data': ontology_detail
                }), 200
            
            elif request.method == 'PUT':
                # 更新本体
                data = request.get_json() or {}
                updated_ontology = {
                    'id': ontology_id,
                    'name': data.get('name', '外贸询盘本体'),
                    'description': data.get('description', '外贸询盘业务的核心本体模型'),
                    'category': data.get('category', 'business'),
                    'version': '1.0.1',
                    'status': data.get('status', 'active'),
                    'updated_at': datetime.now().isoformat(),
                    'entities_count': 156,
                    'relations_count': 89,
                    'author': '系统管理员'
                }
                
                return jsonify({
                    'success': True,
                    'data': updated_ontology,
                    'message': '本体更新成功'
                }), 200
            
            elif request.method == 'DELETE':
                # 删除本体
                return jsonify({
                    'success': True,
                    'message': f'本体 {ontology_id} 已成功删除'
                }), 200
            
        except Exception as e:
            logger.error(f"处理本体操作失败: {str(e)}")
            return jsonify({
                'success': False,
                'error': '操作失败',
                'message': str(e)
            }), 500
    
    @app.route('/api/extract', methods=['POST', 'OPTIONS'])
    def extract_knowledge():
        """知识抽取接口"""
        if request.method == 'OPTIONS':
            return jsonify({'status': 'ok'}), 200
        
        try:
            data = request.get_json()
            if not data or not data.get('text'):
                return jsonify({'error': '请求数据格式错误或缺少文本内容'}), 400
            
            text = data['text']
            
            # 模拟抽取结果
            mock_result = {
                'entities': [
                    {
                        'id': 'entity_1',
                        'text': '苹果公司',
                        'type': 'Company',
                        'confidence': 0.95,
                        'start_pos': 0,
                        'end_pos': 3,
                        'properties': {'industry': 'Technology'}
                    },
                    {
                        'id': 'entity_2',
                        'text': 'iPhone',
                        'type': 'Product',
                        'confidence': 0.92,
                        'start_pos': 10,
                        'end_pos': 16,
                        'properties': {'category': 'Smartphone'}
                    }
                ],
                'relations': [
                    {
                        'id': 'relation_1',
                        'source': {'id': 'entity_1', 'text': '苹果公司'},
                        'target': {'id': 'entity_2', 'text': 'iPhone'},
                        'type': 'produces',
                        'confidence': 0.88
                    }
                ],
                'statistics': {
                    'total_entities': 2,
                    'total_relations': 1,
                    'processing_time': 0.15
                }
            }
            
            return jsonify({
                'success': True,
                'data': mock_result
            }), 200
            
        except Exception as e:
            logger.error(f"知识抽取失败: {str(e)}")
            return jsonify({
                'success': False,
                'error': '知识抽取失败',
                'message': str(e)
            }), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("\n" + "="*50)
    print("🚀 外贸询盘知识图谱系统API服务器")
    print("📍 服务地址: http://localhost:5000")
    print("🔗 健康检查: http://localhost:5000/api/health")
    print("📚 本体管理: http://localhost:5000/api/ontologies")
    print("🔍 知识抽取: http://localhost:5000/api/extract")
    print("="*50 + "\n")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )