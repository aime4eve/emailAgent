#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析服务API路由
提供客户分析、需求洞察、智能推荐等RESTful API接口
"""

from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from marshmallow import Schema, fields, ValidationError
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timedelta

from ...shared.database.arango_service import ArangoDBService
from ...knowledge_management.application.customer_analytics_service import CustomerAnalyticsService
from ...knowledge_management.application.demand_insights_service import DemandInsightsService
from ...knowledge_management.application.intelligent_qa_service import IntelligentQAService

# 创建蓝图
analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')
api = Api(analytics_bp)
logger = logging.getLogger(__name__)

# 请求数据验证模式
class CustomerAnalyticsQuerySchema(Schema):
    """客户分析查询参数验证"""
    customer_ids = fields.List(fields.Str(), missing=None)
    grade = fields.Str(missing=None, validate=lambda x: x in ['A', 'B', 'C'] if x else True)
    region = fields.Str(missing=None)
    country = fields.Str(missing=None)
    date_from = fields.DateTime(missing=None)
    date_to = fields.DateTime(missing=None)
    limit = fields.Int(missing=10, validate=lambda x: 0 < x <= 100)

class DemandAnalysisQuerySchema(Schema):
    """需求分析查询参数验证"""
    category = fields.Str(missing=None)
    region = fields.Str(missing=None)
    date_from = fields.DateTime(missing=None)
    date_to = fields.DateTime(missing=None)
    sort_by = fields.Str(missing='volume', validate=lambda x: x in ['volume', 'growth', 'value'])
    limit = fields.Int(missing=20, validate=lambda x: 0 < x <= 100)

class NaturalLanguageQuerySchema(Schema):
    """自然语言查询参数验证"""
    query = fields.Str(required=True, validate=lambda x: len(x.strip()) > 0)
    context = fields.Dict(missing={})

class RecommendationQuerySchema(Schema):
    """推荐查询参数验证"""
    type = fields.Str(required=True, validate=lambda x: x in ['customer', 'product', 'strategy'])
    target_id = fields.Str(missing=None)
    limit = fields.Int(missing=5, validate=lambda x: 0 < x <= 20)
    filters = fields.Dict(missing={})

# 初始化服务
def get_services():
    """获取服务实例"""
    try:
        arango_service = ArangoDBService()
        analytics_service = CustomerAnalyticsService(arango_service)
        insights_service = DemandInsightsService(arango_service)
        qa_service = IntelligentQAService(arango_service)
        return arango_service, analytics_service, insights_service, qa_service
    except Exception as e:
        logger.error(f"初始化服务失败: {str(e)}")
        raise

class CustomerAnalyticsResource(Resource):
    """客户分析资源"""
    
    def get(self):
        """获取客户分析数据"""
        try:
            # 验证查询参数
            schema = CustomerAnalyticsQuerySchema()
            try:
                query_params = schema.load(request.args)
            except ValidationError as err:
                return {'error': '参数验证失败', 'details': err.messages}, 400
            
            arango_service, analytics_service, insights_service, qa_service = get_services()
            
            # 获取客户价值指标
            if query_params.get('customer_ids'):
                # 批量计算指定客户的价值指标
                metrics_list = []
                for customer_id in query_params['customer_ids']:
                    try:
                        metrics = analytics_service.calculate_customer_value_metrics(customer_id)
                        metrics_list.append(metrics.to_dict())
                    except Exception as e:
                        logger.warning(f"计算客户 {customer_id} 价值指标失败: {str(e)}")
                
                return {
                    'success': True,
                    'data': {
                        'customer_metrics': metrics_list
                    }
                }, 200
            else:
                # 获取整体分析数据
                dashboard_data = analytics_service.get_customer_dashboard_data(
                    date_from=query_params.get('date_from'),
                    date_to=query_params.get('date_to'),
                    region=query_params.get('region'),
                    grade=query_params.get('grade')
                )
                
                return {
                    'success': True,
                    'data': dashboard_data
                }, 200
            
        except Exception as e:
            logger.error(f"获取客户分析数据失败: {str(e)}")
            return {'error': '服务器内部错误', 'message': str(e)}, 500

class CustomerProfileResource(Resource):
    """客户画像资源"""
    
    def get(self, customer_id):
        """获取客户画像"""
        try:
            arango_service, analytics_service, insights_service, qa_service = get_services()
            
            # 构建客户画像
            profile = analytics_service.build_customer_profile(customer_id)
            
            return {
                'success': True,
                'data': {
                    'customer_id': customer_id,
                    'basic_info': profile.basic_info,
                    'behavior_profile': profile.behavior_profile,
                    'demand_profile': profile.demand_profile,
                    'risk_assessment': profile.risk_assessment,
                    'generated_at': datetime.now().isoformat()
                }
            }, 200
            
        except Exception as e:
            logger.error(f"获取客户画像失败: {str(e)}")
            return {'error': '服务器内部错误', 'message': str(e)}, 500

class CustomerSegmentationResource(Resource):
    """客户细分资源"""
    
    def get(self):
        """获取客户细分结果"""
        try:
            # 验证查询参数
            schema = CustomerAnalyticsQuerySchema()
            try:
                query_params = schema.load(request.args)
            except ValidationError as err:
                return {'error': '参数验证失败', 'details': err.messages}, 400
            
            arango_service, analytics_service, insights_service, qa_service = get_services()
            
            # 执行客户细分
            segmentation_result = analytics_service.segment_customers(
                region=query_params.get('region'),
                date_from=query_params.get('date_from'),
                date_to=query_params.get('date_to')
            )
            
            return {
                'success': True,
                'data': segmentation_result
            }, 200
            
        except Exception as e:
            logger.error(f"客户细分失败: {str(e)}")
            return {'error': '服务器内部错误', 'message': str(e)}, 500

class DemandTrendsResource(Resource):
    """需求趋势资源"""
    
    def get(self):
        """获取需求趋势分析"""
        try:
            # 验证查询参数
            schema = DemandAnalysisQuerySchema()
            try:
                query_params = schema.load(request.args)
            except ValidationError as err:
                return {'error': '参数验证失败', 'details': err.messages}, 400
            
            arango_service, analytics_service, insights_service, qa_service = get_services()
            
            # 分析需求趋势
            trends = insights_service.analyze_demand_trends(
                category=query_params.get('category'),
                region=query_params.get('region'),
                date_from=query_params.get('date_from'),
                date_to=query_params.get('date_to'),
                limit=query_params['limit']
            )
            
            return {
                'success': True,
                'data': {
                    'trends': [trend.to_dict() for trend in trends],
                    'analysis_date': datetime.now().isoformat()
                }
            }, 200
            
        except Exception as e:
            logger.error(f"需求趋势分析失败: {str(e)}")
            return {'error': '服务器内部错误', 'message': str(e)}, 500

class ProductOptimizationResource(Resource):
    """产品优化建议资源"""
    
    def get(self):
        """获取产品优化建议"""
        try:
            # 验证查询参数
            schema = DemandAnalysisQuerySchema()
            try:
                query_params = schema.load(request.args)
            except ValidationError as err:
                return {'error': '参数验证失败', 'details': err.messages}, 400
            
            arango_service, analytics_service, insights_service, qa_service = get_services()
            
            # 生成产品优化建议
            suggestions = insights_service.generate_product_optimization_suggestions(
                category=query_params.get('category'),
                limit=query_params['limit']
            )
            
            return {
                'success': True,
                'data': {
                    'suggestions': [suggestion.to_dict() for suggestion in suggestions],
                    'generated_at': datetime.now().isoformat()
                }
            }, 200
            
        except Exception as e:
            logger.error(f"产品优化建议生成失败: {str(e)}")
            return {'error': '服务器内部错误', 'message': str(e)}, 500

class DemandAssociationResource(Resource):
    """需求关联分析资源"""
    
    def get(self):
        """获取需求关联分析"""
        try:
            # 验证查询参数
            schema = DemandAnalysisQuerySchema()
            try:
                query_params = schema.load(request.args)
            except ValidationError as err:
                return {'error': '参数验证失败', 'details': err.messages}, 400
            
            arango_service, analytics_service, insights_service, qa_service = get_services()
            
            # 分析需求关联
            associations = insights_service.analyze_demand_associations(
                category=query_params.get('category'),
                region=query_params.get('region'),
                limit=query_params['limit']
            )
            
            return {
                'success': True,
                'data': {
                    'associations': [assoc.to_dict() for assoc in associations],
                    'analysis_date': datetime.now().isoformat()
                }
            }, 200
            
        except Exception as e:
            logger.error(f"需求关联分析失败: {str(e)}")
            return {'error': '服务器内部错误', 'message': str(e)}, 500

class InsightsDashboardResource(Resource):
    """洞察仪表板资源"""
    
    def get(self):
        """获取需求洞察仪表板数据"""
        try:
            # 验证查询参数
            schema = DemandAnalysisQuerySchema()
            try:
                query_params = schema.load(request.args)
            except ValidationError as err:
                return {'error': '参数验证失败', 'details': err.messages}, 400
            
            arango_service, analytics_service, insights_service, qa_service = get_services()
            
            # 获取仪表板数据
            dashboard_data = insights_service.get_demand_insights_dashboard(
                date_from=query_params.get('date_from'),
                date_to=query_params.get('date_to'),
                region=query_params.get('region')
            )
            
            return {
                'success': True,
                'data': dashboard_data
            }, 200
            
        except Exception as e:
            logger.error(f"获取洞察仪表板数据失败: {str(e)}")
            return {'error': '服务器内部错误', 'message': str(e)}, 500

class NaturalLanguageQueryResource(Resource):
    """自然语言查询资源"""
    
    def post(self):
        """处理自然语言查询"""
        try:
            # 验证请求数据
            schema = NaturalLanguageQuerySchema()
            try:
                query_data = schema.load(request.json)
            except ValidationError as err:
                return {'error': '数据验证失败', 'details': err.messages}, 400
            
            arango_service, analytics_service, insights_service, qa_service = get_services()
            
            # 处理自然语言查询
            result = qa_service.process_natural_language_query(query_data['query'])
            
            return {
                'success': True,
                'data': result.to_dict()
            }, 200
            
        except Exception as e:
            logger.error(f"自然语言查询处理失败: {str(e)}")
            return {'error': '服务器内部错误', 'message': str(e)}, 500

class RecommendationResource(Resource):
    """推荐系统资源"""
    
    def get(self):
        """获取推荐结果"""
        try:
            # 验证查询参数
            schema = RecommendationQuerySchema()
            try:
                query_params = schema.load(request.args)
            except ValidationError as err:
                return {'error': '参数验证失败', 'details': err.messages}, 400
            
            arango_service, analytics_service, insights_service, qa_service = get_services()
            
            recommendation_type = query_params['type']
            target_id = query_params.get('target_id')
            limit = query_params['limit']
            
            if recommendation_type == 'customer':
                if not target_id:
                    return {'error': '参数错误', 'message': '客户推荐需要提供产品ID'}, 400
                
                # 为产品推荐客户
                recommendations = qa_service.recommend_customers_for_product(
                    product_name=target_id,  # 这里简化处理，实际应该通过产品ID获取产品名称
                    limit=limit
                )
                
            elif recommendation_type == 'product':
                if not target_id:
                    return {'error': '参数错误', 'message': '产品推荐需要提供客户ID'}, 400
                
                # 为客户推荐产品
                recommendations = qa_service.recommend_products_for_customer(
                    customer_id=target_id,
                    limit=limit
                )
                
            elif recommendation_type == 'strategy':
                if not target_id:
                    return {'error': '参数错误', 'message': '策略推荐需要提供客户ID'}, 400
                
                # 推荐营销策略
                recommendations = qa_service.recommend_marketing_strategies(
                    customer_id=target_id
                )
                
            else:
                return {'error': '参数错误', 'message': f'不支持的推荐类型: {recommendation_type}'}, 400
            
            return {
                'success': True,
                'data': {
                    'type': recommendation_type,
                    'target_id': target_id,
                    'recommendations': [rec.to_dict() for rec in recommendations],
                    'generated_at': datetime.now().isoformat()
                }
            }, 200
            
        except Exception as e:
            logger.error(f"获取推荐结果失败: {str(e)}")
            return {'error': '服务器内部错误', 'message': str(e)}, 500

class AutoServiceResource(Resource):
    """自动化服务资源"""
    
    def get(self):
        """获取自动化服务任务"""
        try:
            arango_service, analytics_service, insights_service, qa_service = get_services()
            
            # 获取待处理的自动化任务
            follow_up_tasks = qa_service.schedule_follow_up_tasks(days_ahead=7)
            
            return {
                'success': True,
                'data': {
                    'follow_up_tasks': [task.to_dict() for task in follow_up_tasks],
                    'generated_at': datetime.now().isoformat()
                }
            }, 200
            
        except Exception as e:
            logger.error(f"获取自动化服务任务失败: {str(e)}")
            return {'error': '服务器内部错误', 'message': str(e)}, 500
    
    def post(self):
        """执行自动化服务动作"""
        try:
            request_data = request.json
            action_type = request_data.get('action_type')
            
            arango_service, analytics_service, insights_service, qa_service = get_services()
            
            if action_type == 'classify_emails':
                # 邮件自动分类
                email_data = request_data.get('email_data', [])
                actions = qa_service.auto_classify_emails(email_data)
                
                return {
                    'success': True,
                    'data': {
                        'actions': [action.to_dict() for action in actions],
                        'processed_count': len(email_data)
                    }
                }, 200
                
            elif action_type == 'generate_reply':
                # 生成自动回复
                inquiry_id = request_data.get('inquiry_id')
                if not inquiry_id:
                    return {'error': '参数错误', 'message': '需要提供询盘ID'}, 400
                
                suggestions = qa_service.generate_auto_reply_suggestions(inquiry_id)
                
                return {
                    'success': True,
                    'data': {
                        'suggestions': [suggestion.to_dict() for suggestion in suggestions]
                    }
                }, 200
                
            else:
                return {'error': '参数错误', 'message': f'不支持的动作类型: {action_type}'}, 400
            
        except Exception as e:
            logger.error(f"执行自动化服务动作失败: {str(e)}")
            return {'error': '服务器内部错误', 'message': str(e)}, 500

# 注册路由
api.add_resource(CustomerAnalyticsResource, '/customers')
api.add_resource(CustomerProfileResource, '/customers/<string:customer_id>/profile')
api.add_resource(CustomerSegmentationResource, '/customers/segmentation')
api.add_resource(DemandTrendsResource, '/demands/trends')
api.add_resource(ProductOptimizationResource, '/products/optimization')
api.add_resource(DemandAssociationResource, '/demands/associations')
api.add_resource(InsightsDashboardResource, '/insights/dashboard')
api.add_resource(NaturalLanguageQueryResource, '/query')
api.add_resource(RecommendationResource, '/recommendations')
api.add_resource(AutoServiceResource, '/automation')

# 错误处理
@analytics_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': '资源不存在', 'message': str(error)}), 404

@analytics_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': '服务器内部错误', 'message': str(error)}), 500