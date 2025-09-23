#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
客户管理API路由
提供客户相关的RESTful API接口
"""

from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from marshmallow import Schema, fields, ValidationError
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

from ...shared.database.arango_service import ArangoDBService
from ...knowledge_management.application.customer_analytics_service import CustomerAnalyticsService
from ...knowledge_management.application.inquiry_ontology_service import InquiryOntologyService

# 创建蓝图
customers_bp = Blueprint('customers', __name__, url_prefix='/api/customers')
api = Api(customers_bp)
logger = logging.getLogger(__name__)

# 请求数据验证模式
class CustomerCreateSchema(Schema):
    """客户创建请求数据验证"""
    name = fields.Str(required=True, validate=lambda x: len(x.strip()) > 0)
    email = fields.Email(required=True)
    phone = fields.Str(missing=None)
    company = fields.Str(required=True)
    country = fields.Str(required=True)
    region = fields.Str(missing=None)
    industry = fields.Str(missing=None)
    company_size = fields.Str(missing=None)
    tags = fields.List(fields.Str(), missing=[])

class CustomerUpdateSchema(Schema):
    """客户更新请求数据验证"""
    name = fields.Str(missing=None)
    email = fields.Email(missing=None)
    phone = fields.Str(missing=None)
    company = fields.Str(missing=None)
    country = fields.Str(missing=None)
    region = fields.Str(missing=None)
    industry = fields.Str(missing=None)
    company_size = fields.Str(missing=None)
    tags = fields.List(fields.Str(), missing=None)

class CustomerQuerySchema(Schema):
    """客户查询请求数据验证"""
    page = fields.Int(missing=1, validate=lambda x: x > 0)
    page_size = fields.Int(missing=10, validate=lambda x: 0 < x <= 100)
    search = fields.Str(missing=None)
    grade = fields.Str(missing=None, validate=lambda x: x in ['A', 'B', 'C'] if x else True)
    status = fields.Str(missing=None, validate=lambda x: x in ['active', 'inactive', 'potential'] if x else True)
    country = fields.Str(missing=None)
    region = fields.Str(missing=None)
    sort_by = fields.Str(missing='created_at', validate=lambda x: x in ['name', 'created_at', 'value_score', 'last_inquiry_date'])
    sort_order = fields.Str(missing='desc', validate=lambda x: x in ['asc', 'desc'])

# 初始化服务
def get_services():
    """获取服务实例"""
    try:
        arango_service = ArangoDBService()
        analytics_service = CustomerAnalyticsService(arango_service)
        ontology_service = InquiryOntologyService(arango_service)
        return arango_service, analytics_service, ontology_service
    except Exception as e:
        logger.error(f"初始化服务失败: {str(e)}")
        raise

class CustomerListResource(Resource):
    """客户列表资源"""
    
    def get(self):
        """获取客户列表"""
        try:
            # 验证查询参数
            schema = CustomerQuerySchema()
            try:
                query_params = schema.load(request.args)
            except ValidationError as err:
                return {'error': '参数验证失败', 'details': err.messages}, 400
            
            arango_service, analytics_service, ontology_service = get_services()
            
            # 构建查询条件
            filters = {}
            if query_params.get('search'):
                filters['search'] = query_params['search']
            if query_params.get('grade'):
                filters['grade'] = query_params['grade']
            if query_params.get('status'):
                filters['status'] = query_params['status']
            if query_params.get('country'):
                filters['country'] = query_params['country']
            if query_params.get('region'):
                filters['region'] = query_params['region']
            
            # 查询客户数据
            customers = self._query_customers(
                arango_service,
                filters,
                query_params['page'],
                query_params['page_size'],
                query_params['sort_by'],
                query_params['sort_order']
            )
            
            # 获取总数
            total_count = self._get_total_count(arango_service, filters)
            
            # 计算客户价值指标
            for customer in customers:
                try:
                    metrics = analytics_service.calculate_customer_value_metrics(customer['_key'])
                    customer.update({
                        'value_score': metrics.value_score,
                        'customer_grade': metrics.customer_grade.value,
                        'inquiry_activity': metrics.inquiry_activity,
                        'product_value': metrics.product_value,
                        'company_strength': metrics.company_strength,
                    })
                except Exception as e:
                    logger.warning(f"计算客户 {customer['_key']} 价值指标失败: {str(e)}")
                    customer.update({
                        'value_score': 0,
                        'customer_grade': 'C',
                        'inquiry_activity': 0,
                        'product_value': 0,
                        'company_strength': 0,
                    })
            
            return {
                'success': True,
                'data': customers,
                'pagination': {
                    'page': query_params['page'],
                    'page_size': query_params['page_size'],
                    'total': total_count,
                    'pages': (total_count + query_params['page_size'] - 1) // query_params['page_size']
                }
            }, 200
            
        except Exception as e:
            logger.error(f"获取客户列表失败: {str(e)}")
            return {'error': '服务器内部错误', 'message': str(e)}, 500
    
    def post(self):
        """创建新客户"""
        try:
            # 验证请求数据
            schema = CustomerCreateSchema()
            try:
                customer_data = schema.load(request.json)
            except ValidationError as err:
                return {'error': '数据验证失败', 'details': err.messages}, 400
            
            arango_service, analytics_service, ontology_service = get_services()
            
            # 检查邮箱是否已存在
            if self._email_exists(arango_service, customer_data['email']):
                return {'error': '邮箱已存在', 'message': f"邮箱 {customer_data['email']} 已被使用"}, 409
            
            # 创建客户
            customer_data.update({
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'status': 'potential',  # 默认状态
                'value_score': 0,  # 初始价值评分
                'customer_grade': 'C',  # 初始等级
                'inquiry_count': 0,
                'last_inquiry_date': None,
                'total_order_value': 0,
                'average_order_value': 0,
                'conversion_rate': 0.0,
            })
            
            # 保存到数据库
            customers_collection = arango_service.db.collection('customers')
            result = customers_collection.insert(customer_data)
            
            # 创建客户实体到本体
            try:
                ontology_service.create_customer_with_company(
                    customer_id=result['_key'],
                    customer_name=customer_data['name'],
                    customer_email=customer_data['email'],
                    company_name=customer_data['company'],
                    country=customer_data['country'],
                    region=customer_data.get('region'),
                    industry=customer_data.get('industry')
                )
            except Exception as e:
                logger.warning(f"创建客户本体失败: {str(e)}")
            
            # 返回创建的客户信息
            customer_data['id'] = result['_key']
            
            return {
                'success': True,
                'message': '客户创建成功',
                'data': customer_data
            }, 201
            
        except Exception as e:
            logger.error(f"创建客户失败: {str(e)}")
            return {'error': '服务器内部错误', 'message': str(e)}, 500
    
    def _query_customers(self, arango_service, filters, page, page_size, sort_by, sort_order):
        """查询客户数据"""
        # 构建AQL查询
        aql_parts = ["FOR customer IN customers"]
        bind_vars = {}
        
        # 添加过滤条件
        filter_conditions = []
        
        if filters.get('search'):
            filter_conditions.append(
                "(CONTAINS(LOWER(customer.name), LOWER(@search)) OR "
                "CONTAINS(LOWER(customer.email), LOWER(@search)) OR "
                "CONTAINS(LOWER(customer.company), LOWER(@search)) OR "
                "CONTAINS(LOWER(customer.country), LOWER(@search)))"
            )
            bind_vars['search'] = filters['search']
        
        if filters.get('grade'):
            filter_conditions.append("customer.customer_grade == @grade")
            bind_vars['grade'] = filters['grade']
        
        if filters.get('status'):
            filter_conditions.append("customer.status == @status")
            bind_vars['status'] = filters['status']
        
        if filters.get('country'):
            filter_conditions.append("customer.country == @country")
            bind_vars['country'] = filters['country']
        
        if filters.get('region'):
            filter_conditions.append("customer.region == @region")
            bind_vars['region'] = filters['region']
        
        if filter_conditions:
            aql_parts.append(f"FILTER {' AND '.join(filter_conditions)}")
        
        # 添加排序
        sort_direction = "DESC" if sort_order == 'desc' else "ASC"
        aql_parts.append(f"SORT customer.{sort_by} {sort_direction}")
        
        # 添加分页
        offset = (page - 1) * page_size
        aql_parts.append(f"LIMIT {offset}, {page_size}")
        
        # 返回结果
        aql_parts.append("RETURN customer")
        
        aql = " ".join(aql_parts)
        return list(arango_service.db.aql.execute(aql, bind_vars=bind_vars))
    
    def _get_total_count(self, arango_service, filters):
        """获取符合条件的客户总数"""
        aql_parts = ["FOR customer IN customers"]
        bind_vars = {}
        
        # 添加过滤条件（与查询相同）
        filter_conditions = []
        
        if filters.get('search'):
            filter_conditions.append(
                "(CONTAINS(LOWER(customer.name), LOWER(@search)) OR "
                "CONTAINS(LOWER(customer.email), LOWER(@search)) OR "
                "CONTAINS(LOWER(customer.company), LOWER(@search)) OR "
                "CONTAINS(LOWER(customer.country), LOWER(@search)))"
            )
            bind_vars['search'] = filters['search']
        
        if filters.get('grade'):
            filter_conditions.append("customer.customer_grade == @grade")
            bind_vars['grade'] = filters['grade']
        
        if filters.get('status'):
            filter_conditions.append("customer.status == @status")
            bind_vars['status'] = filters['status']
        
        if filters.get('country'):
            filter_conditions.append("customer.country == @country")
            bind_vars['country'] = filters['country']
        
        if filters.get('region'):
            filter_conditions.append("customer.region == @region")
            bind_vars['region'] = filters['region']
        
        if filter_conditions:
            aql_parts.append(f"FILTER {' AND '.join(filter_conditions)}")
        
        aql_parts.append("COLLECT WITH COUNT INTO total RETURN total")
        
        aql = " ".join(aql_parts)
        result = list(arango_service.db.aql.execute(aql, bind_vars=bind_vars))
        return result[0] if result else 0
    
    def _email_exists(self, arango_service, email):
        """检查邮箱是否已存在"""
        aql = "FOR customer IN customers FILTER customer.email == @email RETURN customer"
        result = list(arango_service.db.aql.execute(aql, bind_vars={'email': email}))
        return len(result) > 0

class CustomerDetailResource(Resource):
    """客户详情资源"""
    
    def get(self, customer_id):
        """获取客户详情"""
        try:
            arango_service, analytics_service, ontology_service = get_services()
            
            # 获取客户基本信息
            customers_collection = arango_service.db.collection('customers')
            try:
                customer = customers_collection.get(customer_id)
            except Exception:
                return {'error': '客户不存在', 'message': f'客户ID {customer_id} 不存在'}, 404
            
            if not customer:
                return {'error': '客户不存在', 'message': f'客户ID {customer_id} 不存在'}, 404
            
            # 计算客户价值指标
            try:
                metrics = analytics_service.calculate_customer_value_metrics(customer_id)
                customer.update({
                    'value_score': metrics.value_score,
                    'customer_grade': metrics.customer_grade.value,
                    'inquiry_activity': metrics.inquiry_activity,
                    'product_value': metrics.product_value,
                    'company_strength': metrics.company_strength,
                })
            except Exception as e:
                logger.warning(f"计算客户价值指标失败: {str(e)}")
            
            # 获取客户画像
            try:
                profile = analytics_service.build_customer_profile(customer_id)
                customer['profile'] = {
                    'basic_info': profile.basic_info,
                    'behavior_profile': profile.behavior_profile,
                    'demand_profile': profile.demand_profile,
                    'risk_assessment': profile.risk_assessment,
                }
            except Exception as e:
                logger.warning(f"构建客户画像失败: {str(e)}")
                customer['profile'] = None
            
            # 获取询盘历史
            customer['inquiry_history'] = self._get_inquiry_history(arango_service, customer_id)
            
            return {
                'success': True,
                'data': customer
            }, 200
            
        except Exception as e:
            logger.error(f"获取客户详情失败: {str(e)}")
            return {'error': '服务器内部错误', 'message': str(e)}, 500
    
    def put(self, customer_id):
        """更新客户信息"""
        try:
            # 验证请求数据
            schema = CustomerUpdateSchema()
            try:
                update_data = schema.load(request.json)
            except ValidationError as err:
                return {'error': '数据验证失败', 'details': err.messages}, 400
            
            arango_service, analytics_service, ontology_service = get_services()
            
            # 检查客户是否存在
            customers_collection = arango_service.db.collection('customers')
            try:
                existing_customer = customers_collection.get(customer_id)
            except Exception:
                return {'error': '客户不存在', 'message': f'客户ID {customer_id} 不存在'}, 404
            
            if not existing_customer:
                return {'error': '客户不存在', 'message': f'客户ID {customer_id} 不存在'}, 404
            
            # 如果更新邮箱，检查是否与其他客户冲突
            if update_data.get('email') and update_data['email'] != existing_customer.get('email'):
                if self._email_exists_except(arango_service, update_data['email'], customer_id):
                    return {'error': '邮箱已存在', 'message': f"邮箱 {update_data['email']} 已被其他客户使用"}, 409
            
            # 更新数据
            update_data['updated_at'] = datetime.now().isoformat()
            
            # 执行更新
            customers_collection.update(customer_id, update_data)
            
            # 获取更新后的客户信息
            updated_customer = customers_collection.get(customer_id)
            
            return {
                'success': True,
                'message': '客户信息更新成功',
                'data': updated_customer
            }, 200
            
        except Exception as e:
            logger.error(f"更新客户信息失败: {str(e)}")
            return {'error': '服务器内部错误', 'message': str(e)}, 500
    
    def delete(self, customer_id):
        """删除客户"""
        try:
            arango_service, analytics_service, ontology_service = get_services()
            
            # 检查客户是否存在
            customers_collection = arango_service.db.collection('customers')
            try:
                existing_customer = customers_collection.get(customer_id)
            except Exception:
                return {'error': '客户不存在', 'message': f'客户ID {customer_id} 不存在'}, 404
            
            if not existing_customer:
                return {'error': '客户不存在', 'message': f'客户ID {customer_id} 不存在'}, 404
            
            # 检查是否有关联的询盘记录
            inquiry_count = self._get_inquiry_count(arango_service, customer_id)
            if inquiry_count > 0:
                return {
                    'error': '无法删除客户',
                    'message': f'客户有 {inquiry_count} 条询盘记录，请先处理相关数据'
                }, 409
            
            # 删除客户
            customers_collection.delete(customer_id)
            
            return {
                'success': True,
                'message': '客户删除成功'
            }, 200
            
        except Exception as e:
            logger.error(f"删除客户失败: {str(e)}")
            return {'error': '服务器内部错误', 'message': str(e)}, 500
    
    def _get_inquiry_history(self, arango_service, customer_id):
        """获取客户询盘历史"""
        try:
            aql = """
            FOR inquiry IN inquiries
                FILTER inquiry.customer_id == @customer_id
                SORT inquiry.created_at DESC
                LIMIT 10
                RETURN {
                    id: inquiry._key,
                    date: inquiry.created_at,
                    subject: inquiry.email_subject,
                    status: inquiry.status,
                    purchase_intent: inquiry.purchase_intent,
                    mentioned_products: inquiry.mentioned_products
                }
            """
            
            return list(arango_service.db.aql.execute(aql, bind_vars={'customer_id': customer_id}))
        except Exception as e:
            logger.warning(f"获取询盘历史失败: {str(e)}")
            return []
    
    def _email_exists_except(self, arango_service, email, except_customer_id):
        """检查邮箱是否已存在（排除指定客户）"""
        aql = "FOR customer IN customers FILTER customer.email == @email AND customer._key != @except_id RETURN customer"
        result = list(arango_service.db.aql.execute(aql, bind_vars={'email': email, 'except_id': except_customer_id}))
        return len(result) > 0
    
    def _get_inquiry_count(self, arango_service, customer_id):
        """获取客户询盘数量"""
        try:
            aql = "FOR inquiry IN inquiries FILTER inquiry.customer_id == @customer_id COLLECT WITH COUNT INTO total RETURN total"
            result = list(arango_service.db.aql.execute(aql, bind_vars={'customer_id': customer_id}))
            return result[0] if result else 0
        except Exception:
            return 0

class CustomerStatsResource(Resource):
    """客户统计资源"""
    
    def get(self):
        """获取客户统计信息"""
        try:
            arango_service, analytics_service, ontology_service = get_services()
            
            # 获取基本统计
            stats = {
                'total_customers': self._get_total_customers(arango_service),
                'active_customers': self._get_active_customers(arango_service),
                'grade_distribution': self._get_grade_distribution(arango_service),
                'region_distribution': self._get_region_distribution(arango_service),
                'recent_registrations': self._get_recent_registrations(arango_service),
                'avg_value_score': self._get_avg_value_score(arango_service),
            }
            
            return {
                'success': True,
                'data': stats
            }, 200
            
        except Exception as e:
            logger.error(f"获取客户统计失败: {str(e)}")
            return {'error': '服务器内部错误', 'message': str(e)}, 500
    
    def _get_total_customers(self, arango_service):
        """获取客户总数"""
        aql = "FOR customer IN customers COLLECT WITH COUNT INTO total RETURN total"
        result = list(arango_service.db.aql.execute(aql))
        return result[0] if result else 0
    
    def _get_active_customers(self, arango_service):
        """获取活跃客户数"""
        aql = "FOR customer IN customers FILTER customer.status == 'active' COLLECT WITH COUNT INTO total RETURN total"
        result = list(arango_service.db.aql.execute(aql))
        return result[0] if result else 0
    
    def _get_grade_distribution(self, arango_service):
        """获取客户等级分布"""
        aql = """
        FOR customer IN customers
            COLLECT grade = customer.customer_grade WITH COUNT INTO count
            RETURN { grade: grade, count: count }
        """
        return list(arango_service.db.aql.execute(aql))
    
    def _get_region_distribution(self, arango_service):
        """获取地区分布"""
        aql = """
        FOR customer IN customers
            COLLECT region = customer.region WITH COUNT INTO count
            SORT count DESC
            LIMIT 10
            RETURN { region: region, count: count }
        """
        return list(arango_service.db.aql.execute(aql))
    
    def _get_recent_registrations(self, arango_service):
        """获取最近注册数量（30天内）"""
        aql = """
        FOR customer IN customers
            FILTER DATE_DIFF(customer.created_at, DATE_NOW(), 'day') <= 30
            COLLECT WITH COUNT INTO total
            RETURN total
        """
        result = list(arango_service.db.aql.execute(aql))
        return result[0] if result else 0
    
    def _get_avg_value_score(self, arango_service):
        """获取平均价值评分"""
        aql = """
        FOR customer IN customers
            FILTER customer.value_score != null AND customer.value_score > 0
            COLLECT AGGREGATE avg_score = AVERAGE(customer.value_score)
            RETURN avg_score
        """
        result = list(arango_service.db.aql.execute(aql))
        return round(result[0], 2) if result and result[0] else 0

# 注册路由
api.add_resource(CustomerListResource, '/')
api.add_resource(CustomerDetailResource, '/<string:customer_id>')
api.add_resource(CustomerStatsResource, '/stats')

# 错误处理
@customers_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': '资源不存在', 'message': str(error)}), 404

@customers_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': '服务器内部错误', 'message': str(error)}), 500