#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
外贸询盘本体管理服务
提供本体实体的创建、查询、更新和分析功能
"""

from typing import Dict, List, Any, Optional, Tuple
import logging
from datetime import datetime, timedelta
import statistics

from ..domain.model.inquiry_ontology import (
    Customer, Company, Product, Demand, InquiryEvent, Relationship,
    CustomerType, CustomerGrade, CompanyScale, DemandType, InquiryUrgency
)
from ...shared.database.arango_service import ArangoDBService

class InquiryOntologyService:
    """
    外贸询盘本体管理服务类
    提供本体实体的业务逻辑和数据操作
    """
    
    def __init__(self, arango_service: ArangoDBService):
        """
        初始化本体管理服务
        
        Args:
            arango_service: ArangoDB数据库服务实例
        """
        self.arango_service = arango_service
        self.logger = logging.getLogger(__name__)
        
        # 初始化数据库集合
        self.arango_service.initialize_collections()
    
    def create_customer_with_company(self, customer_data: Dict[str, Any], 
                                   company_data: Optional[Dict[str, Any]] = None) -> Tuple[str, Optional[str]]:
        """
        创建客户及其关联公司
        
        Args:
            customer_data: 客户数据
            company_data: 公司数据（可选）
            
        Returns:
            Tuple[客户ID, 公司ID]
        """
        try:
            # 创建客户实体
            customer = Customer(
                name=customer_data.get('name', ''),
                email=customer_data.get('email', ''),
                phone=customer_data.get('phone'),
                country=customer_data.get('country', ''),
                region=customer_data.get('region', ''),
                customer_type=CustomerType(customer_data.get('customer_type', 'potential')),
                properties=customer_data.get('properties', {})
            )
            
            # 保存客户到数据库
            customer_result = self.arango_service.create_customer(customer.to_dict())
            customer_key = customer_result['_key']
            
            company_key = None
            if company_data:
                # 创建公司实体
                company = Company(
                    name=company_data.get('name', ''),
                    industry=company_data.get('industry', ''),
                    scale=CompanyScale(company_data.get('scale', 'small')),
                    country=company_data.get('country', ''),
                    city=company_data.get('city', ''),
                    properties=company_data.get('properties', {})
                )
                
                # 保存公司到数据库
                company_result = self.arango_service.create_company(company.to_dict())
                company_key = company_result['_key']
                
                # 创建客户-公司关系
                self.arango_service.create_relationship(
                    'customers', customer_key,
                    'companies', company_key,
                    'belongs_to',
                    {'relationship_type': 'employment'}
                )
            
            self.logger.info(f"成功创建客户: {customer_key}, 公司: {company_key}")
            return customer_key, company_key
            
        except Exception as e:
            self.logger.error(f"创建客户和公司失败: {str(e)}")
            raise
    
    def create_inquiry_event(self, inquiry_data: Dict[str, Any], 
                           customer_email: str,
                           mentioned_products: List[str] = None,
                           mentioned_demands: List[str] = None) -> str:
        """
        创建询盘事件并建立关联关系
        
        Args:
            inquiry_data: 询盘数据
            customer_email: 客户邮箱
            mentioned_products: 提及的产品列表
            mentioned_demands: 提及的需求列表
            
        Returns:
            询盘事件ID
        """
        try:
            # 创建询盘事件实体
            inquiry = InquiryEvent(
                email_subject=inquiry_data.get('email_subject', ''),
                email_content=inquiry_data.get('email_content', ''),
                content_summary=inquiry_data.get('content_summary', ''),
                urgency=InquiryUrgency(inquiry_data.get('urgency', 'medium')),
                purchase_intent=inquiry_data.get('purchase_intent', 0.5),
                sentiment_score=inquiry_data.get('sentiment_score', 0.0),
                mentioned_products=mentioned_products or [],
                mentioned_demands=mentioned_demands or [],
                properties=inquiry_data.get('properties', {})
            )
            
            # 保存询盘事件到数据库
            inquiry_result = self.arango_service.create_inquiry(inquiry.to_dict())
            inquiry_key = inquiry_result['_key']
            
            # 查找客户
            customer = self._find_customer_by_email(customer_email)
            if customer:
                # 创建询盘-客户关系
                self.arango_service.create_relationship(
                    'inquiries', inquiry_key,
                    'customers', customer['_key'],
                    'comes_from',
                    {'inquiry_date': inquiry.inquiry_date.isoformat()}
                )
                
                # 更新客户的最后询盘时间
                self._update_customer_last_inquiry(customer['_key'], inquiry.inquiry_date)
            
            # 创建产品关联关系
            if mentioned_products:
                for product_name in mentioned_products:
                    product = self._find_product_by_name(product_name)
                    if product:
                        self.arango_service.create_relationship(
                            'inquiries', inquiry_key,
                            'products', product['_key'],
                            'inquires_about',
                            {'interest_level': inquiry.purchase_intent}
                        )
            
            # 创建需求关联关系
            if mentioned_demands:
                for demand_desc in mentioned_demands:
                    demand = self._find_or_create_demand(demand_desc)
                    if demand:
                        self.arango_service.create_relationship(
                            'inquiries', inquiry_key,
                            'demands', demand['_key'],
                            'expresses',
                            {'priority': 1}
                        )
            
            self.logger.info(f"成功创建询盘事件: {inquiry_key}")
            return inquiry_key
            
        except Exception as e:
            self.logger.error(f"创建询盘事件失败: {str(e)}")
            raise
    
    def calculate_customer_value_score(self, customer_id: str) -> float:
        """
        计算客户价值评分
        
        Args:
            customer_id: 客户ID
            
        Returns:
            客户价值评分 (0-100)
        """
        try:
            # 获取客户信息
            customer = self._get_customer_by_id(customer_id)
            if not customer:
                return 0.0
            
            # 评估维度权重
            weights = {
                'inquiry_activity': 0.25,    # 询盘活跃度
                'product_value': 0.25,       # 产品价值度
                'company_strength': 0.20,    # 公司实力度
                'demand_clarity': 0.15,      # 需求明确度
                'cooperation_potential': 0.15 # 合作潜力度
            }
            
            scores = {}
            
            # 1. 询盘活跃度评分
            inquiry_score = self._calculate_inquiry_activity_score(customer_id)
            scores['inquiry_activity'] = inquiry_score
            
            # 2. 产品价值度评分
            product_score = self._calculate_product_value_score(customer_id)
            scores['product_value'] = product_score
            
            # 3. 公司实力度评分
            company_score = self._calculate_company_strength_score(customer_id)
            scores['company_strength'] = company_score
            
            # 4. 需求明确度评分
            demand_score = self._calculate_demand_clarity_score(customer_id)
            scores['demand_clarity'] = demand_score
            
            # 5. 合作潜力度评分
            cooperation_score = self._calculate_cooperation_potential_score(customer_id)
            scores['cooperation_potential'] = cooperation_score
            
            # 计算加权总分
            total_score = sum(scores[key] * weights[key] for key in weights.keys())
            
            # 更新客户价值评分
            self._update_customer_value_score(customer_id, total_score)
            
            self.logger.info(f"客户 {customer_id} 价值评分: {total_score:.2f}")
            return total_score
            
        except Exception as e:
            self.logger.error(f"计算客户价值评分失败: {str(e)}")
            return 0.0
    
    def classify_customer_grade(self, customer_id: str) -> CustomerGrade:
        """
        客户分级管理
        
        Args:
            customer_id: 客户ID
            
        Returns:
            客户等级
        """
        try:
            value_score = self.calculate_customer_value_score(customer_id)
            
            if value_score >= 80:
                grade = CustomerGrade.A  # 高价值、高潜力、优先跟进
            elif value_score >= 60:
                grade = CustomerGrade.B  # 中等价值、有潜力、定期维护
            else:
                grade = CustomerGrade.C  # 低价值、观察跟踪
            
            # 更新客户等级
            self._update_customer_grade(customer_id, grade)
            
            self.logger.info(f"客户 {customer_id} 分级: {grade.value}")
            return grade
            
        except Exception as e:
            self.logger.error(f"客户分级失败: {str(e)}")
            return CustomerGrade.C
    
    def get_customer_profile(self, customer_id: str) -> Dict[str, Any]:
        """
        构建客户画像
        
        Args:
            customer_id: 客户ID
            
        Returns:
            客户画像数据
        """
        try:
            customer = self._get_customer_by_id(customer_id)
            if not customer:
                return {}
            
            # 基础信息画像
            basic_profile = {
                'customer_info': customer,
                'geographic_info': {
                    'country': customer.get('country'),
                    'region': customer.get('region')
                }
            }
            
            # 行为画像
            behavior_profile = self._get_customer_behavior_profile(customer_id)
            
            # 需求画像
            demand_profile = self._get_customer_demand_profile(customer_id)
            
            # 公司信息
            company_info = self._get_customer_company_info(customer_id)
            
            profile = {
                'basic_profile': basic_profile,
                'behavior_profile': behavior_profile,
                'demand_profile': demand_profile,
                'company_info': company_info,
                'value_score': customer.get('value_score', 0),
                'customer_grade': customer.get('customer_grade', 'C'),
                'last_updated': datetime.now().isoformat()
            }
            
            self.logger.info(f"构建客户 {customer_id} 画像完成")
            return profile
            
        except Exception as e:
            self.logger.error(f"构建客户画像失败: {str(e)}")
            return {}
    
    def get_product_inquiry_statistics(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        获取产品询盘统计
        
        Args:
            days: 统计天数
            
        Returns:
            产品询盘统计数据
        """
        try:
            aql = """
            FOR inquiry IN inquiries
                FILTER DATE_DIFF(inquiry.created_at, DATE_NOW(), 'day') <= @days
                FOR product IN 1..1 OUTBOUND inquiry inquires_about
                COLLECT product_name = product.name, 
                        product_category = product.category 
                        WITH COUNT INTO inquiry_count
                SORT inquiry_count DESC
                RETURN {
                    product_name: product_name,
                    product_category: product_category,
                    inquiry_count: inquiry_count
                }
            """
            
            result = list(self.arango_service.db.aql.execute(aql, bind_vars={'days': days}))
            self.logger.info(f"获取 {days} 天内产品询盘统计完成")
            return result
            
        except Exception as e:
            self.logger.error(f"获取产品询盘统计失败: {str(e)}")
            return []
    
    def get_demand_trend_analysis(self, days: int = 90) -> Dict[str, Any]:
        """
        获取需求趋势分析
        
        Args:
            days: 分析天数
            
        Returns:
            需求趋势分析数据
        """
        try:
            # 获取需求频率统计
            demand_stats = self.arango_service.get_demand_trends(days)
            
            # 按时间分组统计
            aql = """
            FOR inquiry IN inquiries
                FILTER DATE_DIFF(inquiry.created_at, DATE_NOW(), 'day') <= @days
                FOR demand IN 1..1 OUTBOUND inquiry expresses
                COLLECT date_group = DATE_FORMAT(inquiry.created_at, '%Y-%m-%d'),
                        demand_type = demand.type
                        WITH COUNT INTO count
                SORT date_group DESC
                RETURN {
                    date: date_group,
                    demand_type: demand_type,
                    count: count
                }
            """
            
            time_series = list(self.arango_service.db.aql.execute(aql, bind_vars={'days': days}))
            
            # 地域需求分析
            regional_aql = """
            FOR inquiry IN inquiries
                FILTER DATE_DIFF(inquiry.created_at, DATE_NOW(), 'day') <= @days
                FOR customer IN 1..1 OUTBOUND inquiry comes_from
                    FOR demand IN 1..1 OUTBOUND inquiry expresses
                    COLLECT country = customer.country,
                            demand_type = demand.type
                            WITH COUNT INTO count
                    SORT count DESC
                    RETURN {
                        country: country,
                        demand_type: demand_type,
                        count: count
                    }
            """
            
            regional_stats = list(self.arango_service.db.aql.execute(regional_aql, bind_vars={'days': days}))
            
            analysis = {
                'demand_frequency': demand_stats,
                'time_series': time_series,
                'regional_distribution': regional_stats,
                'analysis_period': f'{days} days',
                'generated_at': datetime.now().isoformat()
            }
            
            self.logger.info(f"需求趋势分析完成，分析周期: {days} 天")
            return analysis
            
        except Exception as e:
            self.logger.error(f"需求趋势分析失败: {str(e)}")
            return {}
    
    # 私有辅助方法
    
    def _find_customer_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """根据邮箱查找客户"""
        try:
            aql = "FOR customer IN customers FILTER customer.email == @email RETURN customer"
            result = list(self.arango_service.db.aql.execute(aql, bind_vars={'email': email}))
            return result[0] if result else None
        except Exception:
            return None
    
    def _find_product_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """根据名称查找产品"""
        try:
            aql = "FOR product IN products FILTER CONTAINS(LOWER(product.name), LOWER(@name)) RETURN product"
            result = list(self.arango_service.db.aql.execute(aql, bind_vars={'name': name}))
            return result[0] if result else None
        except Exception:
            return None
    
    def _find_or_create_demand(self, description: str) -> Optional[Dict[str, Any]]:
        """查找或创建需求"""
        try:
            # 先尝试查找
            aql = "FOR demand IN demands FILTER CONTAINS(LOWER(demand.description), LOWER(@desc)) RETURN demand"
            result = list(self.arango_service.db.aql.execute(aql, bind_vars={'desc': description}))
            
            if result:
                return result[0]
            
            # 如果不存在则创建
            demand = Demand(
                description=description,
                type=self._classify_demand_type(description)
            )
            
            demands = self.arango_service.db.collection('demands')
            result = demands.insert(demand.to_dict())
            return {'_key': result['_key'], **demand.to_dict()}
            
        except Exception:
            return None
    
    def _classify_demand_type(self, description: str) -> DemandType:
        """根据描述分类需求类型"""
        description_lower = description.lower()
        
        if any(word in description_lower for word in ['price', 'cost', 'cheap', 'expensive']):
            return DemandType.PRICE
        elif any(word in description_lower for word in ['quality', 'performance', 'speed']):
            return DemandType.PERFORMANCE
        elif any(word in description_lower for word in ['design', 'appearance', 'color']):
            return DemandType.APPEARANCE
        elif any(word in description_lower for word in ['material', 'steel', 'plastic']):
            return DemandType.MATERIAL
        elif any(word in description_lower for word in ['moq', 'minimum', 'quantity']):
            return DemandType.MOQ
        elif any(word in description_lower for word in ['delivery', 'lead time', 'shipping']):
            return DemandType.LEAD_TIME
        elif any(word in description_lower for word in ['certificate', 'certification', 'standard']):
            return DemandType.CERTIFICATION
        else:
            return DemandType.PERFORMANCE  # 默认类型
    
    def _get_customer_by_id(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取客户"""
        try:
            customers = self.arango_service.db.collection('customers')
            return customers.get(customer_id)
        except Exception:
            return None
    
    def _calculate_inquiry_activity_score(self, customer_id: str) -> float:
        """计算询盘活跃度评分"""
        try:
            # 获取最近90天的询盘数量
            aql = """
            FOR inquiry IN inquiries
                FOR customer IN 1..1 OUTBOUND inquiry comes_from
                FILTER customer._key == @customer_id
                FILTER DATE_DIFF(inquiry.created_at, DATE_NOW(), 'day') <= 90
                RETURN inquiry
            """
            
            inquiries = list(self.arango_service.db.aql.execute(aql, bind_vars={'customer_id': customer_id}))
            inquiry_count = len(inquiries)
            
            # 根据询盘数量计算分数 (0-100)
            if inquiry_count >= 10:
                return 100.0
            elif inquiry_count >= 5:
                return 80.0
            elif inquiry_count >= 2:
                return 60.0
            elif inquiry_count >= 1:
                return 40.0
            else:
                return 20.0
                
        except Exception:
            return 20.0
    
    def _calculate_product_value_score(self, customer_id: str) -> float:
        """计算产品价值度评分"""
        try:
            # 获取客户询盘的产品平均价格
            aql = """
            FOR inquiry IN inquiries
                FOR customer IN 1..1 OUTBOUND inquiry comes_from
                FILTER customer._key == @customer_id
                FOR product IN 1..1 OUTBOUND inquiry inquires_about
                FILTER product.price != null
                RETURN product.price
            """
            
            prices = list(self.arango_service.db.aql.execute(aql, bind_vars={'customer_id': customer_id}))
            
            if not prices:
                return 50.0  # 默认分数
            
            avg_price = statistics.mean(prices)
            
            # 根据平均价格计算分数
            if avg_price >= 1000:
                return 100.0
            elif avg_price >= 500:
                return 80.0
            elif avg_price >= 200:
                return 60.0
            elif avg_price >= 100:
                return 40.0
            else:
                return 20.0
                
        except Exception:
            return 50.0
    
    def _calculate_company_strength_score(self, customer_id: str) -> float:
        """计算公司实力度评分"""
        try:
            # 获取客户所属公司信息
            aql = """
            FOR customer IN customers
                FILTER customer._key == @customer_id
                FOR company IN 1..1 OUTBOUND customer belongs_to
                RETURN company
            """
            
            companies = list(self.arango_service.db.aql.execute(aql, bind_vars={'customer_id': customer_id}))
            
            if not companies:
                return 30.0  # 无公司信息默认分数
            
            company = companies[0]
            score = 30.0  # 基础分数
            
            # 根据公司规模加分
            scale = company.get('scale', 'small')
            if scale == 'enterprise':
                score += 40.0
            elif scale == 'large':
                score += 30.0
            elif scale == 'medium':
                score += 20.0
            else:
                score += 10.0
            
            # 根据年收入加分
            if company.get('annual_revenue'):
                revenue = company['annual_revenue']
                if revenue >= 10000000:  # 1000万以上
                    score += 30.0
                elif revenue >= 1000000:  # 100万以上
                    score += 20.0
                else:
                    score += 10.0
            
            return min(score, 100.0)
            
        except Exception:
            return 30.0
    
    def _calculate_demand_clarity_score(self, customer_id: str) -> float:
        """计算需求明确度评分"""
        try:
            # 获取客户询盘中表达的需求
            aql = """
            FOR inquiry IN inquiries
                FOR customer IN 1..1 OUTBOUND inquiry comes_from
                FILTER customer._key == @customer_id
                FOR demand IN 1..1 OUTBOUND inquiry expresses
                RETURN {
                    demand: demand,
                    inquiry: inquiry
                }
            """
            
            results = list(self.arango_service.db.aql.execute(aql, bind_vars={'customer_id': customer_id}))
            
            if not results:
                return 20.0
            
            # 计算需求描述的详细程度
            total_score = 0.0
            for result in results:
                demand = result['demand']
                inquiry = result['inquiry']
                
                # 根据需求描述长度和详细程度评分
                desc_length = len(demand.get('description', ''))
                if desc_length > 100:
                    total_score += 20.0
                elif desc_length > 50:
                    total_score += 15.0
                elif desc_length > 20:
                    total_score += 10.0
                else:
                    total_score += 5.0
                
                # 根据询盘内容长度评分
                content_length = len(inquiry.get('email_content', ''))
                if content_length > 500:
                    total_score += 10.0
                elif content_length > 200:
                    total_score += 5.0
            
            avg_score = total_score / len(results) if results else 20.0
            return min(avg_score, 100.0)
            
        except Exception:
            return 20.0
    
    def _calculate_cooperation_potential_score(self, customer_id: str) -> float:
        """计算合作潜力度评分"""
        try:
            customer = self._get_customer_by_id(customer_id)
            if not customer:
                return 30.0
            
            score = 30.0  # 基础分数
            
            # 根据购买意向评分
            inquiries_aql = """
            FOR inquiry IN inquiries
                FOR customer IN 1..1 OUTBOUND inquiry comes_from
                FILTER customer._key == @customer_id
                RETURN inquiry.purchase_intent
            """
            
            intents = list(self.arango_service.db.aql.execute(inquiries_aql, bind_vars={'customer_id': customer_id}))
            
            if intents:
                avg_intent = statistics.mean([intent for intent in intents if intent is not None])
                score += avg_intent * 40.0  # 最高40分
            
            # 根据情感分析评分
            sentiment_aql = """
            FOR inquiry IN inquiries
                FOR customer IN 1..1 OUTBOUND inquiry comes_from
                FILTER customer._key == @customer_id
                RETURN inquiry.sentiment_score
            """
            
            sentiments = list(self.arango_service.db.aql.execute(sentiment_aql, bind_vars={'customer_id': customer_id}))
            
            if sentiments:
                avg_sentiment = statistics.mean([s for s in sentiments if s is not None])
                # 将情感分数(-1到1)转换为0到30分
                sentiment_score = (avg_sentiment + 1) * 15.0
                score += sentiment_score
            
            return min(score, 100.0)
            
        except Exception:
            return 30.0
    
    def _update_customer_last_inquiry(self, customer_key: str, inquiry_date: datetime):
        """更新客户最后询盘时间"""
        try:
            customers = self.arango_service.db.collection('customers')
            customers.update(customer_key, {
                'last_inquiry_date': inquiry_date.isoformat(),
                'updated_at': datetime.now().isoformat()
            })
        except Exception as e:
            self.logger.error(f"更新客户最后询盘时间失败: {str(e)}")
    
    def _update_customer_value_score(self, customer_key: str, score: float):
        """更新客户价值评分"""
        try:
            customers = self.arango_service.db.collection('customers')
            customers.update(customer_key, {
                'value_score': score,
                'updated_at': datetime.now().isoformat()
            })
        except Exception as e:
            self.logger.error(f"更新客户价值评分失败: {str(e)}")
    
    def _update_customer_grade(self, customer_key: str, grade: CustomerGrade):
        """更新客户等级"""
        try:
            customers = self.arango_service.db.collection('customers')
            customers.update(customer_key, {
                'customer_grade': grade.value,
                'updated_at': datetime.now().isoformat()
            })
        except Exception as e:
            self.logger.error(f"更新客户等级失败: {str(e)}")
    
    def _get_customer_behavior_profile(self, customer_id: str) -> Dict[str, Any]:
        """获取客户行为画像"""
        try:
            # 询盘习惯分析
            inquiry_pattern_aql = """
            FOR inquiry IN inquiries
                FOR customer IN 1..1 OUTBOUND inquiry comes_from
                FILTER customer._key == @customer_id
                RETURN {
                    hour: DATE_HOUR(inquiry.created_at),
                    day_of_week: DATE_DAYOFWEEK(inquiry.created_at),
                    urgency: inquiry.urgency
                }
            """
            
            patterns = list(self.arango_service.db.aql.execute(inquiry_pattern_aql, bind_vars={'customer_id': customer_id}))
            
            # 产品偏好分析
            product_pref_aql = """
            FOR inquiry IN inquiries
                FOR customer IN 1..1 OUTBOUND inquiry comes_from
                FILTER customer._key == @customer_id
                FOR product IN 1..1 OUTBOUND inquiry inquires_about
                COLLECT category = product.category WITH COUNT INTO count
                SORT count DESC
                RETURN {
                    category: category,
                    count: count
                }
            """
            
            preferences = list(self.arango_service.db.aql.execute(product_pref_aql, bind_vars={'customer_id': customer_id}))
            
            return {
                'inquiry_patterns': patterns,
                'product_preferences': preferences,
                'total_inquiries': len(patterns)
            }
            
        except Exception:
            return {}
    
    def _get_customer_demand_profile(self, customer_id: str) -> Dict[str, Any]:
        """获取客户需求画像"""
        try:
            demand_aql = """
            FOR inquiry IN inquiries
                FOR customer IN 1..1 OUTBOUND inquiry comes_from
                FILTER customer._key == @customer_id
                FOR demand IN 1..1 OUTBOUND inquiry expresses
                COLLECT demand_type = demand.type WITH COUNT INTO count
                SORT count DESC
                RETURN {
                    demand_type: demand_type,
                    count: count
                }
            """
            
            demands = list(self.arango_service.db.aql.execute(demand_aql, bind_vars={'customer_id': customer_id}))
            
            # 分析价格敏感度和质量关注度
            price_focus = sum(1 for d in demands if d['demand_type'] == 'price')
            quality_focus = sum(1 for d in demands if d['demand_type'] in ['performance', 'certification'])
            total_demands = sum(d['count'] for d in demands)
            
            return {
                'demand_distribution': demands,
                'price_sensitivity': price_focus / total_demands if total_demands > 0 else 0,
                'quality_focus': quality_focus / total_demands if total_demands > 0 else 0,
                'total_demands': total_demands
            }
            
        except Exception:
            return {}
    
    def _get_customer_company_info(self, customer_id: str) -> Dict[str, Any]:
        """获取客户公司信息"""
        try:
            company_aql = """
            FOR customer IN customers
                FILTER customer._key == @customer_id
                FOR company IN 1..1 OUTBOUND customer belongs_to
                RETURN company
            """
            
            companies = list(self.arango_service.db.aql.execute(company_aql, bind_vars={'customer_id': customer_id}))
            return companies[0] if companies else {}
            
        except Exception:
            return {}