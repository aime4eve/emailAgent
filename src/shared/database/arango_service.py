#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ArangoDB数据库服务类
提供外贸询盘知识图谱的数据存储和查询功能
"""

from arango import ArangoClient
from typing import Dict, List, Any, Optional
import json
import logging
from datetime import datetime

class ArangoDBService:
    """
    ArangoDB数据库服务类
    提供外贸询盘知识图谱的数据存储和查询功能
    """
    
    def __init__(self, host: str = 'localhost', port: int = 8529, 
                 database: str = 'emailagent', username: str = 'root', password: str = None):
        """
        初始化ArangoDB连接
        
        Args:
            host: ArangoDB服务器地址
            port: 端口号
            database: 数据库名称
            username: 用户名
            password: 密码
        """
        self.logger = logging.getLogger(__name__)
        self.host = host
        self.port = port
        self.database_name = database
        self.username = username
        self.password = password
        
        try:
            self.client = ArangoClient(hosts=f'http://{host}:{port}')
            self.db = self.client.db(database, username=username, password=password)
            self.logger.info(f"成功连接到ArangoDB数据库: {database}")
        except Exception as e:
            self.logger.error(f"连接ArangoDB失败: {str(e)}")
            raise
    
    def initialize_collections(self) -> bool:
        """
        初始化外贸询盘知识图谱所需的集合
        
        Returns:
            bool: 初始化是否成功
        """
        try:
            # 文档集合（顶点）
            document_collections = [
                'customers',      # 客户
                'companies',      # 公司
                'products',       # 产品
                'demands',        # 需求/关注点
                'inquiries',      # 询盘事件
                'emails'          # 邮件内容
            ]
            
            # 边集合（关系）
            edge_collections = [
                'comes_from',     # 询盘事件 → 客户
                'belongs_to',     # 客户 → 公司
                'inquires_about', # 询盘事件 → 产品
                'expresses',      # 询盘事件 → 需求
                'focuses_on',     # 客户 → 需求
                'works_for',      # 客户 → 公司
                'has_feature',    # 产品 → 特性
                'competes_with'   # 产品 → 产品
            ]
            
            # 创建文档集合
            for collection_name in document_collections:
                if not self.db.has_collection(collection_name):
                    self.db.create_collection(collection_name)
                    self.logger.info(f"创建文档集合: {collection_name}")
            
            # 创建边集合
            for collection_name in edge_collections:
                if not self.db.has_collection(collection_name):
                    self.db.create_collection(collection_name, edge=True)
                    self.logger.info(f"创建边集合: {collection_name}")
            
            # 创建图
            graph_name = 'inquiry_graph'
            if not self.db.has_graph(graph_name):
                graph_definition = {
                    'edge_definitions': [
                        {
                            'edge_collection': 'comes_from',
                            'from_vertex_collections': ['inquiries'],
                            'to_vertex_collections': ['customers']
                        },
                        {
                            'edge_collection': 'belongs_to',
                            'from_vertex_collections': ['customers'],
                            'to_vertex_collections': ['companies']
                        },
                        {
                            'edge_collection': 'inquires_about',
                            'from_vertex_collections': ['inquiries'],
                            'to_vertex_collections': ['products']
                        },
                        {
                            'edge_collection': 'expresses',
                            'from_vertex_collections': ['inquiries'],
                            'to_vertex_collections': ['demands']
                        },
                        {
                            'edge_collection': 'focuses_on',
                            'from_vertex_collections': ['customers'],
                            'to_vertex_collections': ['demands']
                        }
                    ]
                }
                self.db.create_graph(graph_name, graph_definition)
                self.logger.info(f"创建图: {graph_name}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"初始化集合失败: {str(e)}")
            return False
    
    def create_customer(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建客户文档
        
        Args:
            customer_data: 客户数据字典
            
        Returns:
            创建结果
        """
        try:
            # 添加时间戳
            customer_data['created_at'] = datetime.now().isoformat()
            customer_data['updated_at'] = datetime.now().isoformat()
            
            customers = self.db.collection('customers')
            result = customers.insert(customer_data)
            self.logger.info(f"创建客户成功: {result['_key']}")
            return result
        except Exception as e:
            self.logger.error(f"创建客户失败: {str(e)}")
            raise
    
    def create_company(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建公司文档
        
        Args:
            company_data: 公司数据字典
            
        Returns:
            创建结果
        """
        try:
            company_data['created_at'] = datetime.now().isoformat()
            company_data['updated_at'] = datetime.now().isoformat()
            
            companies = self.db.collection('companies')
            result = companies.insert(company_data)
            self.logger.info(f"创建公司成功: {result['_key']}")
            return result
        except Exception as e:
            self.logger.error(f"创建公司失败: {str(e)}")
            raise
    
    def create_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建产品文档
        
        Args:
            product_data: 产品数据字典
            
        Returns:
            创建结果
        """
        try:
            product_data['created_at'] = datetime.now().isoformat()
            product_data['updated_at'] = datetime.now().isoformat()
            
            products = self.db.collection('products')
            result = products.insert(product_data)
            self.logger.info(f"创建产品成功: {result['_key']}")
            return result
        except Exception as e:
            self.logger.error(f"创建产品失败: {str(e)}")
            raise
    
    def create_inquiry(self, inquiry_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建询盘事件文档
        
        Args:
            inquiry_data: 询盘数据字典
            
        Returns:
            创建结果
        """
        try:
            inquiry_data['created_at'] = datetime.now().isoformat()
            inquiry_data['updated_at'] = datetime.now().isoformat()
            
            inquiries = self.db.collection('inquiries')
            result = inquiries.insert(inquiry_data)
            self.logger.info(f"创建询盘事件成功: {result['_key']}")
            return result
        except Exception as e:
            self.logger.error(f"创建询盘事件失败: {str(e)}")
            raise
    
    def create_relationship(self, from_collection: str, from_key: str, 
                          to_collection: str, to_key: str, 
                          edge_collection: str, edge_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        创建实体间关系
        
        Args:
            from_collection: 源集合名
            from_key: 源文档键
            to_collection: 目标集合名
            to_key: 目标文档键
            edge_collection: 边集合名
            edge_data: 边数据
            
        Returns:
            创建结果
        """
        try:
            edges = self.db.collection(edge_collection)
            edge_doc = {
                '_from': f'{from_collection}/{from_key}',
                '_to': f'{to_collection}/{to_key}',
                'created_at': datetime.now().isoformat(),
                **(edge_data or {})
            }
            result = edges.insert(edge_doc)
            self.logger.info(f"创建关系成功: {edge_collection} - {result['_key']}")
            return result
        except Exception as e:
            self.logger.error(f"创建关系失败: {str(e)}")
            raise
    
    def query_high_value_customers(self, min_score: float = 80.0) -> List[Dict[str, Any]]:
        """
        查询高价值客户及其关联信息
        
        Args:
            min_score: 最低价值评分
            
        Returns:
            高价值客户列表
        """
        try:
            aql = """
            FOR customer IN customers
                FILTER customer.value_score >= @min_score
                LET company = FIRST(
                    FOR c IN 1..1 OUTBOUND customer belongs_to
                    RETURN c
                )
                LET inquiries = (
                    FOR inquiry IN 1..1 INBOUND customer GRAPH 'inquiry_graph'
                    RETURN inquiry
                )
                RETURN {
                    customer: customer,
                    company: company,
                    inquiry_count: LENGTH(inquiries),
                    recent_inquiries: inquiries[0..2]
                }
            """
            result = list(self.db.aql.execute(aql, bind_vars={'min_score': min_score}))
            self.logger.info(f"查询到 {len(result)} 个高价值客户")
            return result
        except Exception as e:
            self.logger.error(f"查询高价值客户失败: {str(e)}")
            raise
    
    def analyze_customer_product_preferences(self, customer_id: str) -> List[Dict[str, Any]]:
        """
        分析客户产品偏好
        
        Args:
            customer_id: 客户ID
            
        Returns:
            客户产品偏好分析结果
        """
        try:
            aql = """
            FOR customer IN customers
                FILTER customer.customer_id == @customer_id
                FOR inquiry IN 1..1 INBOUND customer GRAPH 'inquiry_graph'
                    FOR product IN 1..1 OUTBOUND inquiry inquires_about
                    COLLECT category = product.category WITH COUNT INTO count
                    SORT count DESC
                    RETURN {
                        category: category,
                        inquiry_count: count
                    }
            """
            result = list(self.db.aql.execute(aql, bind_vars={'customer_id': customer_id}))
            self.logger.info(f"分析客户 {customer_id} 的产品偏好完成")
            return result
        except Exception as e:
            self.logger.error(f"分析客户产品偏好失败: {str(e)}")
            raise
    
    def get_demand_trends(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        获取需求趋势分析
        
        Args:
            days: 分析天数
            
        Returns:
            需求趋势数据
        """
        try:
            aql = """
            FOR inquiry IN inquiries
                FILTER DATE_DIFF(inquiry.created_at, DATE_NOW(), 'day') <= @days
                FOR demand IN 1..1 OUTBOUND inquiry expresses
                COLLECT demand_type = demand.type WITH COUNT INTO count
                SORT count DESC
                RETURN {
                    demand_type: demand_type,
                    count: count
                }
            """
            result = list(self.db.aql.execute(aql, bind_vars={'days': days}))
            self.logger.info(f"获取 {days} 天内需求趋势完成")
            return result
        except Exception as e:
            self.logger.error(f"获取需求趋势失败: {str(e)}")
            raise
    
    def search_customers_by_product_interest(self, product_name: str) -> List[Dict[str, Any]]:
        """
        根据产品兴趣搜索客户
        
        Args:
            product_name: 产品名称
            
        Returns:
            感兴趣的客户列表
        """
        try:
            aql = """
            FOR product IN products
                FILTER CONTAINS(LOWER(product.name), LOWER(@product_name))
                FOR inquiry IN 1..1 INBOUND product inquires_about
                    FOR customer IN 1..1 OUTBOUND inquiry comes_from
                    RETURN DISTINCT {
                        customer: customer,
                        product: product,
                        inquiry_date: inquiry.created_at
                    }
            """
            result = list(self.db.aql.execute(aql, bind_vars={'product_name': product_name}))
            self.logger.info(f"找到 {len(result)} 个对产品 '{product_name}' 感兴趣的客户")
            return result
        except Exception as e:
            self.logger.error(f"搜索客户失败: {str(e)}")
            raise
    
    def get_customer_statistics(self) -> Dict[str, Any]:
        """
        获取客户统计信息
        
        Returns:
            客户统计数据
        """
        try:
            aql = """
            RETURN {
                total_customers: LENGTH(customers),
                high_value_customers: LENGTH(
                    FOR c IN customers
                    FILTER c.value_score >= 80
                    RETURN c
                ),
                total_inquiries: LENGTH(inquiries),
                total_products: LENGTH(products),
                total_companies: LENGTH(companies)
            }
            """
            result = list(self.db.aql.execute(aql))[0]
            self.logger.info("获取客户统计信息完成")
            return result
        except Exception as e:
            self.logger.error(f"获取客户统计信息失败: {str(e)}")
            raise