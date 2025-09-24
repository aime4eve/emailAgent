#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版API服务器
不依赖ArangoDB，使用模拟数据快速启动
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
import time
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
            logger.info(f"开始处理文本知识抽取，文本长度: {len(text)}")
            
            # 导入知识抽取服务
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
            
            from nlp_processing.entity_extractor import EntityExtractor
            from nlp_processing.relation_extractor import RelationExtractor
            
            start_time = time.time()
            
            # 初始化抽取器
            entity_extractor = EntityExtractor(language='chinese')
            relation_extractor = RelationExtractor(language='chinese')
            
            # 抽取实体
            entities = entity_extractor.extract_entities(text, use_rules=True, use_model=False)
            logger.info(f"抽取到 {len(entities)} 个实体")
            
            # 抽取关系
            relations = relation_extractor.extract_from_text(text, entities)
            logger.info(f"抽取到 {len(relations)} 个关系")
            
            processing_time = time.time() - start_time
            
            # 转换实体格式
            formatted_entities = []
            for i, entity in enumerate(entities):
                formatted_entities.append({
                    'id': f'entity_{i+1}',
                    'text': entity.text,
                    'type': entity.label,
                    'confidence': entity.confidence,
                    'start_pos': entity.start,
                    'end_pos': entity.end,
                    'properties': entity.properties
                })
            
            # 转换关系格式
            formatted_relations = []
            for i, relation in enumerate(relations):
                # 安全地查找实体索引
                source_id = 'unknown'
                target_id = 'unknown'
                source_text = '未知'
                target_text = '未知'
                
                # 获取source实体信息
                if hasattr(relation, 'subject') and relation.subject:
                    if hasattr(relation.subject, 'text'):
                        source_text = relation.subject.text
                    try:
                        source_idx = entities.index(relation.subject)
                        source_id = f'entity_{source_idx+1}'
                    except (ValueError, AttributeError):
                        # 如果找不到实体索引，但有文本，仍然使用文本
                        pass
                
                # 获取target实体信息
                if hasattr(relation, 'object') and relation.object:
                    if hasattr(relation.object, 'text'):
                        target_text = relation.object.text
                    try:
                        target_idx = entities.index(relation.object)
                        target_id = f'entity_{target_idx+1}'
                    except (ValueError, AttributeError):
                        # 如果找不到实体索引，但有文本，仍然使用文本
                        pass
                
                formatted_relations.append({
                    'id': f'relation_{i+1}',
                    'source': {
                        'id': source_id,
                        'text': source_text
                    },
                    'target': {
                        'id': target_id,
                        'text': target_text
                    },
                    'source_text': source_text,  # 添加直接的source_text字段
                    'target_text': target_text,  # 添加直接的target_text字段
                    'type': relation.predicate,  # 使用predicate而不是relation_type
                    'confidence': relation.confidence
                })
            
            # 计算置信度
            avg_confidence = 0.0
            if entities or relations:
                total_confidence = sum(e.confidence for e in entities) + sum(r.confidence for r in relations)
                total_items = len(entities) + len(relations)
                avg_confidence = total_confidence / total_items if total_items > 0 else 0.0
            
            result = {
                'entities': formatted_entities,
                'relations': formatted_relations,
                'statistics': {
                    'total_entities': len(entities),
                    'total_relations': len(relations),
                    'processing_time': processing_time,
                    'confidence': avg_confidence
                }
            }
            
            logger.info(f"知识抽取完成，耗时: {processing_time:.2f}秒")
            
            return jsonify({
                'success': True,
                'data': result
            }), 200
            
        except Exception as e:
            logger.error(f"知识抽取失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': '知识抽取失败',
                'message': str(e)
            }), 500
    
    @app.route('/api/extract/file', methods=['POST', 'OPTIONS'])
    def extract_knowledge_from_file():
        """文件知识抽取接口"""
        if request.method == 'OPTIONS':
            return jsonify({'status': 'ok'}), 200
        
        try:
            # 检查是否有文件上传
            if 'file' not in request.files:
                return jsonify({
                    'success': False,
                    'error': '没有上传文件',
                    'message': '请选择要上传的文件'
                }), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({
                    'success': False,
                    'error': '文件名为空',
                    'message': '请选择有效的文件'
                }), 400
            
            # 获取文件信息
            filename = file.filename
            file_size = len(file.read())
            file.seek(0)  # 重置文件指针
            
            logger.info(f"处理文件上传 - 文件名: {filename}, 大小: {file_size} bytes")
            
            # 模拟文件内容解析
            if filename.lower().endswith(('.txt', '.eml', '.msg')):
                # 模拟邮件文件解析
                mock_content = """发件人: john.smith@example.com
收件人: sales@company.com
主题: 询盘 - iPhone 15 Pro 批量采购

您好，

我是来自美国ABC公司的采购经理John Smith。我们对贵公司的iPhone 15 Pro产品很感兴趣，希望了解以下信息：

1. 最小起订量是多少？
2. 批量采购的价格如何？
3. 交货周期大概多长时间？
4. 是否支持定制包装？

我们预计采购数量在1000-5000台之间。请提供详细的报价单。

期待您的回复。

最好的问候，
John Smith
ABC公司采购经理
电话: +1-555-0123
邮箱: john.smith@example.com"""
                
                # 模拟知识抽取结果
                mock_result = {
                    'file_info': {
                        'filename': filename,
                        'size': file_size,
                        'type': 'email',
                        'encoding': 'utf-8'
                    },
                    'extracted_content': mock_content,
                    'entities': [
                        {
                            'id': 'customer_1',
                            'text': 'John Smith',
                            'type': 'Customer',
                            'confidence': 0.98,
                            'start_pos': 45,
                            'end_pos': 55,
                            'properties': {
                                'email': 'john.smith@example.com',
                                'phone': '+1-555-0123',
                                'position': '采购经理'
                            }
                        },
                        {
                            'id': 'company_1',
                            'text': 'ABC公司',
                            'type': 'Company',
                            'confidence': 0.95,
                            'start_pos': 30,
                            'end_pos': 35,
                            'properties': {
                                'country': '美国',
                                'industry': '贸易'
                            }
                        },
                        {
                            'id': 'product_1',
                            'text': 'iPhone 15 Pro',
                            'type': 'Product',
                            'confidence': 0.99,
                            'start_pos': 80,
                            'end_pos': 94,
                            'properties': {
                                'category': '智能手机',
                                'brand': 'Apple'
                            }
                        },
                        {
                            'id': 'demand_1',
                            'text': '批量采购',
                            'type': 'Demand',
                            'confidence': 0.92,
                            'start_pos': 95,
                            'end_pos': 99,
                            'properties': {
                                'quantity_range': '1000-5000台',
                                'type': 'bulk_purchase'
                            }
                        }
                    ],
                    'relations': [
                        {
                            'id': 'relation_1',
                            'source': {'id': 'customer_1', 'text': 'John Smith'},
                            'target': {'id': 'company_1', 'text': 'ABC公司'},
                            'type': 'belongs_to',
                            'confidence': 0.95,
                            'label': '隶属于'
                        },
                        {
                            'id': 'relation_2',
                            'source': {'id': 'customer_1', 'text': 'John Smith'},
                            'target': {'id': 'product_1', 'text': 'iPhone 15 Pro'},
                            'type': 'inquires_about',
                            'confidence': 0.98,
                            'label': '询问'
                        },
                        {
                            'id': 'relation_3',
                            'source': {'id': 'customer_1', 'text': 'John Smith'},
                            'target': {'id': 'demand_1', 'text': '批量采购'},
                            'type': 'expresses',
                            'confidence': 0.90,
                            'label': '表达'
                        }
                    ],
                    'statistics': {
                        'total_entities': 4,
                        'total_relations': 3,
                        'processing_time': 0.35,
                        'confidence_avg': 0.95
                    },
                    'insights': {
                        'customer_value_score': 85,
                        'inquiry_urgency': 'medium',
                        'business_potential': 'high',
                        'key_requirements': ['价格', '起订量', '交货周期', '定制包装']
                    }
                }
                
                return jsonify({
                    'success': True,
                    'data': mock_result,
                    'message': '文件解析和知识抽取完成'
                }), 200
            
            else:
                return jsonify({
                    'success': False,
                    'error': '不支持的文件格式',
                    'message': '目前只支持 .txt, .eml, .msg 格式的文件'
                }), 400
                
        except Exception as e:
            logger.error(f"文件知识抽取失败: {str(e)}")
            return jsonify({
                'success': False,
                'error': '文件处理失败',
                'message': str(e)
            }), 500
    
    @app.route('/api/graph/<graph_id>/export', methods=['GET', 'OPTIONS'])
    def export_graph(graph_id):
        """导出图谱数据"""
        if request.method == 'OPTIONS':
            return jsonify({'status': 'ok'}), 200
        
        try:
            format_type = request.args.get('format', 'json')
            logger.info(f"导出图谱 - ID: {graph_id}, 格式: {format_type}")
            
            # 模拟图谱数据
            mock_graph_data = {
                'nodes': [
                    {
                        'id': 'customer_1',
                        'label': '张三',
                        'type': 'Customer',
                        'properties': {
                            'email': 'zhangsan@example.com',
                            'country': '中国',
                            'value_score': 85
                        }
                    },
                    {
                        'id': 'company_1',
                        'label': '阿里巴巴',
                        'type': 'Company',
                        'properties': {
                            'industry': '电子商务',
                            'size': '大型企业'
                        }
                    },
                    {
                        'id': 'product_1',
                        'label': 'iPhone 15',
                        'type': 'Product',
                        'properties': {
                            'category': '智能手机',
                            'price': 999
                        }
                    }
                ],
                'edges': [
                    {
                        'id': 'edge_1',
                        'source': 'customer_1',
                        'target': 'company_1',
                        'type': 'belongs_to',
                        'label': '隶属于'
                    },
                    {
                        'id': 'edge_2',
                        'source': 'customer_1',
                        'target': 'product_1',
                        'type': 'inquires_about',
                        'label': '询问'
                    }
                ],
                'metadata': {
                    'graph_id': graph_id,
                    'export_time': datetime.now().isoformat(),
                    'format': format_type,
                    'node_count': 3,
                    'edge_count': 2
                }
            }
            
            if format_type == 'json':
                from flask import make_response
                import json
                
                response_data = json.dumps(mock_graph_data, ensure_ascii=False, indent=2)
                response = make_response(response_data)
                response.headers['Content-Type'] = 'application/json; charset=utf-8'
                response.headers['Content-Disposition'] = f'attachment; filename=graph_{graph_id}.json'
                return response
            
            else:
                return jsonify({
                    'success': False,
                    'error': f'不支持的导出格式: {format_type}'
                }), 400
                
        except Exception as e:
            logger.error(f"导出图谱失败: {str(e)}")
            return jsonify({
                'success': False,
                'error': '导出图谱失败',
                'message': str(e)
            }), 500
    
    @app.route('/api/graph/json/export', methods=['GET', 'OPTIONS'])
    def export_graph_legacy():
        """兼容旧版本的图谱导出接口"""
        if request.method == 'OPTIONS':
            return jsonify({'status': 'ok'}), 200
        
        # 重定向到新的导出接口
        return export_graph('default')
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("\n" + "="*50)
    print("🚀 外贸询盘知识图谱系统API服务器")
    print("📍 服务地址: http://localhost:5000")
    print("🔗 健康检查: http://localhost:5000/api/health")
    print("📚 本体管理: http://localhost:5000/api/ontologies")
    print("🔍 知识抽取: http://localhost:5000/api/extract")
    print("📊 图谱导出: http://localhost:5000/api/graph/json/export")
    print("="*50 + "\n")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True
    )