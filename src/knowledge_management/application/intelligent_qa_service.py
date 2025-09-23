#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能问答和推荐系统
实现自然语言查询、推荐引擎和自动化客户服务功能
"""

from typing import Dict, List, Any, Optional, Tuple
import logging
import re
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict
import json

# NLP和机器学习相关导入
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.neighbors import NearestNeighbors
    import numpy as np
except ImportError as e:
    logging.warning(f"机器学习库导入失败: {e}")
    TfidfVectorizer = None
    cosine_similarity = None
    NearestNeighbors = None
    np = None

from ...shared.database.arango_service import ArangoDBService
from ..domain.model.inquiry_ontology import CustomerGrade

@dataclass
class QueryResult:
    """查询结果"""
    query: str
    query_type: str
    results: List[Dict[str, Any]]
    confidence: float
    processing_time: float
    suggestions: List[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'query': self.query,
            'query_type': self.query_type,
            'results': self.results,
            'confidence': self.confidence,
            'processing_time': self.processing_time,
            'suggestions': self.suggestions or []
        }

@dataclass
class Recommendation:
    """推荐结果"""
    recommendation_type: str  # 'customer', 'product', 'strategy'
    target_id: str
    target_name: str
    score: float
    reason: str
    supporting_data: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'recommendation_type': self.recommendation_type,
            'target_id': self.target_id,
            'target_name': self.target_name,
            'score': self.score,
            'reason': self.reason,
            'supporting_data': self.supporting_data
        }

@dataclass
class AutoServiceAction:
    """自动化服务动作"""
    action_type: str  # 'classify', 'prioritize', 'respond', 'follow_up'
    target_id: str
    action_description: str
    priority: int
    suggested_response: Optional[str] = None
    follow_up_date: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'action_type': self.action_type,
            'target_id': self.target_id,
            'action_description': self.action_description,
            'priority': self.priority,
            'suggested_response': self.suggested_response,
            'follow_up_date': self.follow_up_date.isoformat() if self.follow_up_date else None
        }

class IntelligentQAService:
    """智能问答和推荐服务"""
    
    def __init__(self, arango_service: ArangoDBService):
        """
        初始化智能问答服务
        
        Args:
            arango_service: ArangoDB数据库服务
        """
        self.arango_service = arango_service
        self.logger = logging.getLogger(__name__)
        
        # 查询模式定义
        self.query_patterns = {
            'customer_interest': [
                r'哪些客户对(.+)产品最?感兴趣',
                r'谁对(.+)感兴趣',
                r'(.+)产品的潜在客户',
                r'interested in (.+)',
                r'customers for (.+)'
            ],
            'regional_preference': [
                r'来自(.+)的客户主要关注(.+)',
                r'(.+)地区客户偏好',
                r'(.+)客户需求特点',
                r'customers from (.+) prefer',
                r'(.+) region customers focus on'
            ],
            'high_value_customers': [
                r'高价值客户.*共同需求',
                r'A级客户.*特征',
                r'优质客户.*偏好',
                r'high.value customers.*common',
                r'top customers.*requirements'
            ],
            'product_inquiry_trend': [
                r'最近(.+)询盘频率最高的产品',
                r'(.+)内热门产品',
                r'询盘最多的产品',
                r'most inquired products.*(.+)',
                r'popular products in (.+)'
            ],
            'demand_analysis': [
                r'(.+)需求趋势',
                r'需求变化.*(.+)',
                r'市场需求.*分析',
                r'demand trends for (.+)',
                r'market demand analysis'
            ]
        }
        
        # 推荐算法配置
        self.recommendation_config = {
            'customer_similarity_threshold': 0.7,
            'product_similarity_threshold': 0.6,
            'min_recommendation_score': 0.5,
            'max_recommendations': 10
        }
    
    def process_natural_language_query(self, query: str) -> QueryResult:
        """
        处理自然语言查询
        
        Args:
            query: 自然语言查询
            
        Returns:
            查询结果
        """
        start_time = datetime.now()
        
        try:
            self.logger.info(f"处理自然语言查询: {query}")
            
            # 1. 查询意图识别
            query_type, extracted_params = self._identify_query_intent(query)
            
            # 2. 执行对应的查询
            if query_type == 'customer_interest':
                results = self._query_customers_by_product_interest(extracted_params.get('product', ''))
            elif query_type == 'regional_preference':
                results = self._query_regional_preferences(extracted_params.get('region', ''))
            elif query_type == 'high_value_customers':
                results = self._query_high_value_customer_patterns()
            elif query_type == 'product_inquiry_trend':
                results = self._query_product_inquiry_trends(extracted_params.get('period', '3个月'))
            elif query_type == 'demand_analysis':
                results = self._query_demand_analysis(extracted_params.get('demand_type', ''))
            else:
                results = self._perform_general_search(query)
            
            # 3. 计算置信度
            confidence = self._calculate_query_confidence(query_type, results)
            
            # 4. 生成相关建议
            suggestions = self._generate_query_suggestions(query_type, results)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            query_result = QueryResult(
                query=query,
                query_type=query_type,
                results=results,
                confidence=confidence,
                processing_time=processing_time,
                suggestions=suggestions
            )
            
            self.logger.info(f"查询处理完成，返回 {len(results)} 条结果")
            return query_result
            
        except Exception as e:
            self.logger.error(f"处理自然语言查询失败: {str(e)}")
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return QueryResult(
                query=query,
                query_type='error',
                results=[],
                confidence=0.0,
                processing_time=processing_time,
                suggestions=['请尝试重新表述您的问题', '您可以询问客户、产品或需求相关的问题']
            )
    
    def recommend_customers_for_product(self, product_name: str, limit: int = 5) -> List[Recommendation]:
        """
        为特定产品推荐潜在客户
        
        Args:
            product_name: 产品名称
            limit: 推荐数量限制
            
        Returns:
            客户推荐列表
        """
        try:
            self.logger.info(f"为产品 '{product_name}' 推荐潜在客户")
            
            # 1. 找到相似产品的客户
            similar_product_customers = self._find_customers_by_similar_products(product_name)
            
            # 2. 基于客户行为模式推荐
            behavioral_recommendations = self._recommend_by_customer_behavior(product_name)
            
            # 3. 基于地域和行业模式推荐
            demographic_recommendations = self._recommend_by_demographics(product_name)
            
            # 4. 合并和排序推荐结果
            all_recommendations = (
                similar_product_customers + 
                behavioral_recommendations + 
                demographic_recommendations
            )
            
            # 去重并按分数排序
            unique_recommendations = self._deduplicate_recommendations(all_recommendations)
            unique_recommendations.sort(key=lambda x: x.score, reverse=True)
            
            self.logger.info(f"生成了 {len(unique_recommendations[:limit])} 个客户推荐")
            return unique_recommendations[:limit]
            
        except Exception as e:
            self.logger.error(f"客户推荐失败: {str(e)}")
            return []
    
    def recommend_products_for_customer(self, customer_id: str, limit: int = 5) -> List[Recommendation]:
        """
        为客户推荐相关产品
        
        Args:
            customer_id: 客户ID
            limit: 推荐数量限制
            
        Returns:
            产品推荐列表
        """
        try:
            self.logger.info(f"为客户 {customer_id} 推荐产品")
            
            # 1. 基于客户历史询盘推荐
            history_based = self._recommend_by_inquiry_history(customer_id)
            
            # 2. 基于相似客户推荐
            similarity_based = self._recommend_by_similar_customers(customer_id)
            
            # 3. 基于需求匹配推荐
            demand_based = self._recommend_by_demand_matching(customer_id)
            
            # 4. 合并和排序推荐结果
            all_recommendations = history_based + similarity_based + demand_based
            
            # 去重并按分数排序
            unique_recommendations = self._deduplicate_recommendations(all_recommendations)
            unique_recommendations.sort(key=lambda x: x.score, reverse=True)
            
            self.logger.info(f"生成了 {len(unique_recommendations[:limit])} 个产品推荐")
            return unique_recommendations[:limit]
            
        except Exception as e:
            self.logger.error(f"产品推荐失败: {str(e)}")
            return []
    
    def recommend_marketing_strategies(self, customer_id: str) -> List[Recommendation]:
        """
        基于客户画像推荐营销策略
        
        Args:
            customer_id: 客户ID
            
        Returns:
            营销策略推荐列表
        """
        try:
            self.logger.info(f"为客户 {customer_id} 推荐营销策略")
            
            # 获取客户信息
            customer_info = self._get_customer_profile(customer_id)
            
            if not customer_info:
                return []
            
            strategies = []
            
            # 基于客户等级的策略
            grade_strategies = self._recommend_strategies_by_grade(customer_info)
            strategies.extend(grade_strategies)
            
            # 基于需求偏好的策略
            demand_strategies = self._recommend_strategies_by_demands(customer_info)
            strategies.extend(demand_strategies)
            
            # 基于行为模式的策略
            behavior_strategies = self._recommend_strategies_by_behavior(customer_info)
            strategies.extend(behavior_strategies)
            
            # 按分数排序
            strategies.sort(key=lambda x: x.score, reverse=True)
            
            self.logger.info(f"生成了 {len(strategies)} 个营销策略推荐")
            return strategies
            
        except Exception as e:
            self.logger.error(f"营销策略推荐失败: {str(e)}")
            return []
    
    def auto_classify_emails(self, email_data: List[Dict[str, Any]]) -> List[AutoServiceAction]:
        """
        邮件自动分类和优先级排序
        
        Args:
            email_data: 邮件数据列表
            
        Returns:
            自动化服务动作列表
        """
        try:
            self.logger.info(f"自动分类 {len(email_data)} 封邮件")
            
            actions = []
            
            for email in email_data:
                # 分析邮件内容和发送者
                classification = self._classify_email(email)
                priority = self._calculate_email_priority(email, classification)
                
                action = AutoServiceAction(
                    action_type='classify',
                    target_id=email.get('email_id', ''),
                    action_description=f"邮件分类: {classification['category']}, 优先级: {priority}",
                    priority=priority
                )
                
                actions.append(action)
            
            # 按优先级排序
            actions.sort(key=lambda x: x.priority, reverse=True)
            
            self.logger.info(f"邮件分类完成，生成 {len(actions)} 个处理动作")
            return actions
            
        except Exception as e:
            self.logger.error(f"邮件自动分类失败: {str(e)}")
            return []
    
    def generate_auto_reply_suggestions(self, inquiry_id: str) -> List[AutoServiceAction]:
        """
        生成客户询盘自动回复建议
        
        Args:
            inquiry_id: 询盘ID
            
        Returns:
            自动回复建议列表
        """
        try:
            self.logger.info(f"为询盘 {inquiry_id} 生成自动回复建议")
            
            # 获取询盘信息
            inquiry_info = self._get_inquiry_details(inquiry_id)
            
            if not inquiry_info:
                return []
            
            # 分析询盘内容
            analysis = self._analyze_inquiry_content(inquiry_info)
            
            # 生成回复建议
            reply_suggestions = self._generate_reply_templates(inquiry_info, analysis)
            
            actions = []
            for i, suggestion in enumerate(reply_suggestions):
                action = AutoServiceAction(
                    action_type='respond',
                    target_id=inquiry_id,
                    action_description=f"自动回复建议 {i+1}",
                    priority=suggestion.get('priority', 3),
                    suggested_response=suggestion.get('template', '')
                )
                actions.append(action)
            
            self.logger.info(f"生成了 {len(actions)} 个回复建议")
            return actions
            
        except Exception as e:
            self.logger.error(f"生成自动回复建议失败: {str(e)}")
            return []
    
    def schedule_follow_up_tasks(self, days_ahead: int = 7) -> List[AutoServiceAction]:
        """
        安排跟进提醒和任务分配
        
        Args:
            days_ahead: 提前天数
            
        Returns:
            跟进任务列表
        """
        try:
            self.logger.info(f"安排未来 {days_ahead} 天的跟进任务")
            
            # 获取需要跟进的客户和询盘
            follow_up_targets = self._identify_follow_up_targets()
            
            actions = []
            
            for target in follow_up_targets:
                # 计算跟进优先级
                priority = self._calculate_follow_up_priority(target)
                
                # 确定跟进时间
                follow_up_date = self._calculate_follow_up_date(target, days_ahead)
                
                # 生成跟进建议
                follow_up_suggestion = self._generate_follow_up_suggestion(target)
                
                action = AutoServiceAction(
                    action_type='follow_up',
                    target_id=target.get('customer_id', ''),
                    action_description=follow_up_suggestion,
                    priority=priority,
                    follow_up_date=follow_up_date
                )
                
                actions.append(action)
            
            # 按优先级和时间排序
            actions.sort(key=lambda x: (x.priority, x.follow_up_date or datetime.now()), reverse=True)
            
            self.logger.info(f"安排了 {len(actions)} 个跟进任务")
            return actions
            
        except Exception as e:
            self.logger.error(f"安排跟进任务失败: {str(e)}")
            return []
    
    # 私有方法实现
    
    def _identify_query_intent(self, query: str) -> Tuple[str, Dict[str, Any]]:
        """识别查询意图"""
        query_lower = query.lower()
        
        for intent, patterns in self.query_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, query_lower)
                if match:
                    params = {}
                    if match.groups():
                        if intent == 'customer_interest':
                            params['product'] = match.group(1).strip()
                        elif intent == 'regional_preference':
                            params['region'] = match.group(1).strip()
                            if len(match.groups()) > 1:
                                params['focus'] = match.group(2).strip()
                        elif intent == 'product_inquiry_trend':
                            params['period'] = match.group(1).strip() if match.group(1) else '3个月'
                        elif intent == 'demand_analysis':
                            params['demand_type'] = match.group(1).strip()
                    
                    return intent, params
        
        return 'general', {}
    
    def _query_customers_by_product_interest(self, product_name: str) -> List[Dict[str, Any]]:
        """查询对特定产品感兴趣的客户"""
        try:
            aql = """
            FOR product IN products
                FILTER CONTAINS(LOWER(product.name), LOWER(@product_name))
                FOR inquiry IN 1..1 INBOUND product inquires_about
                    FOR customer IN 1..1 OUTBOUND inquiry comes_from
                    RETURN DISTINCT {
                        customer_id: customer._key,
                        customer_name: customer.name,
                        customer_email: customer.email,
                        customer_country: customer.country,
                        customer_grade: customer.customer_grade,
                        value_score: customer.value_score,
                        inquiry_date: inquiry.created_at,
                        purchase_intent: inquiry.purchase_intent,
                        product_name: product.name
                    }
            """
            
            results = list(self.arango_service.db.aql.execute(
                aql, bind_vars={'product_name': product_name}
            ))
            
            # 按价值评分排序
            results.sort(key=lambda x: x.get('value_score', 0), reverse=True)
            
            return results
            
        except Exception as e:
            self.logger.error(f"查询产品感兴趣客户失败: {str(e)}")
            return []
    
    def _query_regional_preferences(self, region: str) -> List[Dict[str, Any]]:
        """查询地区客户偏好"""
        try:
            aql = """
            FOR customer IN customers
                FILTER CONTAINS(LOWER(customer.country), LOWER(@region)) OR 
                       CONTAINS(LOWER(customer.region), LOWER(@region))
                FOR inquiry IN 1..1 INBOUND customer GRAPH 'inquiry_graph'
                    FOR demand IN 1..1 OUTBOUND inquiry expresses
                    COLLECT demand_type = demand.type WITH COUNT INTO count
                    SORT count DESC
                    RETURN {
                        region: @region,
                        demand_type: demand_type,
                        frequency: count
                    }
            """
            
            return list(self.arango_service.db.aql.execute(
                aql, bind_vars={'region': region}
            ))
            
        except Exception as e:
            self.logger.error(f"查询地区偏好失败: {str(e)}")
            return []
    
    def _query_high_value_customer_patterns(self) -> List[Dict[str, Any]]:
        """查询高价值客户模式"""
        try:
            aql = """
            FOR customer IN customers
                FILTER customer.customer_grade == 'A' OR customer.value_score >= 80
                FOR inquiry IN 1..1 INBOUND customer GRAPH 'inquiry_graph'
                    FOR demand IN 1..1 OUTBOUND inquiry expresses
                    COLLECT demand_type = demand.type WITH COUNT INTO count
                    SORT count DESC
                    RETURN {
                        demand_type: demand_type,
                        frequency: count,
                        customer_type: 'high_value'
                    }
            """
            
            return list(self.arango_service.db.aql.execute(aql))
            
        except Exception as e:
            self.logger.error(f"查询高价值客户模式失败: {str(e)}")
            return []
    
    def _query_product_inquiry_trends(self, period: str) -> List[Dict[str, Any]]:
        """查询产品询盘趋势"""
        try:
            # 解析时间周期
            days = self._parse_time_period(period)
            
            aql = """
            FOR inquiry IN inquiries
                FILTER DATE_DIFF(inquiry.created_at, DATE_NOW(), 'day') <= @days
                FOR product IN 1..1 OUTBOUND inquiry inquires_about
                COLLECT product_name = product.name,
                        product_category = product.category
                        WITH COUNT INTO count
                SORT count DESC
                LIMIT 10
                RETURN {
                    product_name: product_name,
                    product_category: product_category,
                    inquiry_count: count,
                    period: @period
                }
            """
            
            return list(self.arango_service.db.aql.execute(
                aql, bind_vars={'days': days, 'period': period}
            ))
            
        except Exception as e:
            self.logger.error(f"查询产品询盘趋势失败: {str(e)}")
            return []
    
    def _query_demand_analysis(self, demand_type: str) -> List[Dict[str, Any]]:
        """查询需求分析"""
        try:
            if demand_type:
                # 特定需求类型分析
                aql = """
                FOR demand IN demands
                    FILTER CONTAINS(LOWER(demand.type), LOWER(@demand_type)) OR
                           CONTAINS(LOWER(demand.description), LOWER(@demand_type))
                    FOR inquiry IN 1..1 INBOUND demand expresses
                        FOR customer IN 1..1 OUTBOUND inquiry comes_from
                        COLLECT country = customer.country WITH COUNT INTO count
                        SORT count DESC
                        RETURN {
                            demand_type: @demand_type,
                            country: country,
                            frequency: count
                        }
                """
                
                return list(self.arango_service.db.aql.execute(
                    aql, bind_vars={'demand_type': demand_type}
                ))
            else:
                # 总体需求分析
                aql = """
                FOR demand IN demands
                    COLLECT demand_type = demand.type WITH COUNT INTO count
                    SORT count DESC
                    RETURN {
                        demand_type: demand_type,
                        frequency: count
                    }
                """
                
                return list(self.arango_service.db.aql.execute(aql))
            
        except Exception as e:
            self.logger.error(f"查询需求分析失败: {str(e)}")
            return []
    
    def _perform_general_search(self, query: str) -> List[Dict[str, Any]]:
        """执行通用搜索"""
        try:
            # 在客户、产品、需求中搜索关键词
            keywords = query.lower().split()
            
            results = []
            
            # 搜索客户
            for keyword in keywords:
                customer_aql = """
                FOR customer IN customers
                    FILTER CONTAINS(LOWER(customer.name), @keyword) OR
                           CONTAINS(LOWER(customer.email), @keyword) OR
                           CONTAINS(LOWER(customer.country), @keyword)
                    LIMIT 5
                    RETURN {
                        type: 'customer',
                        id: customer._key,
                        name: customer.name,
                        details: customer
                    }
                """
                
                customer_results = list(self.arango_service.db.aql.execute(
                    customer_aql, bind_vars={'keyword': keyword}
                ))
                results.extend(customer_results)
            
            # 搜索产品
            for keyword in keywords:
                product_aql = """
                FOR product IN products
                    FILTER CONTAINS(LOWER(product.name), @keyword) OR
                           CONTAINS(LOWER(product.category), @keyword)
                    LIMIT 5
                    RETURN {
                        type: 'product',
                        id: product._key,
                        name: product.name,
                        details: product
                    }
                """
                
                product_results = list(self.arango_service.db.aql.execute(
                    product_aql, bind_vars={'keyword': keyword}
                ))
                results.extend(product_results)
            
            # 去重
            unique_results = []
            seen_ids = set()
            
            for result in results:
                result_id = f"{result['type']}_{result['id']}"
                if result_id not in seen_ids:
                    unique_results.append(result)
                    seen_ids.add(result_id)
            
            return unique_results[:10]  # 限制返回数量
            
        except Exception as e:
            self.logger.error(f"通用搜索失败: {str(e)}")
            return []
    
    def _calculate_query_confidence(self, query_type: str, results: List[Dict[str, Any]]) -> float:
        """计算查询置信度"""
        if not results:
            return 0.0
        
        # 基于查询类型和结果数量计算置信度
        base_confidence = 0.5
        
        if query_type in ['customer_interest', 'regional_preference', 'high_value_customers']:
            base_confidence = 0.8
        elif query_type in ['product_inquiry_trend', 'demand_analysis']:
            base_confidence = 0.7
        
        # 根据结果数量调整
        result_count = len(results)
        if result_count >= 5:
            confidence_boost = 0.2
        elif result_count >= 2:
            confidence_boost = 0.1
        else:
            confidence_boost = 0.0
        
        return min(base_confidence + confidence_boost, 1.0)
    
    def _generate_query_suggestions(self, query_type: str, results: List[Dict[str, Any]]) -> List[str]:
        """生成查询建议"""
        suggestions = []
        
        if query_type == 'customer_interest' and results:
            suggestions.extend([
                '您还可以查询这些客户的详细需求分析',
                '建议查看这些客户的历史询盘记录',
                '可以分析这些客户的地域分布特征'
            ])
        elif query_type == 'regional_preference' and results:
            suggestions.extend([
                '建议进一步分析该地区的行业分布',
                '可以查看该地区客户的价值评分分布',
                '推荐了解该地区的竞争对手情况'
            ])
        elif query_type == 'high_value_customers' and results:
            suggestions.extend([
                '建议制定针对高价值客户的专属服务策略',
                '可以分析高价值客户的产品偏好趋势',
                '推荐设计高价值客户的留存计划'
            ])
        else:
            suggestions.extend([
                '您可以尝试更具体的查询条件',
                '建议使用产品名称或客户地区进行查询',
                '可以询问关于需求趋势或客户分析的问题'
            ])
        
        return suggestions
    
    def _parse_time_period(self, period: str) -> int:
        """解析时间周期"""
        period_lower = period.lower()
        
        if '天' in period_lower or 'day' in period_lower:
            numbers = re.findall(r'\d+', period_lower)
            return int(numbers[0]) if numbers else 7
        elif '周' in period_lower or 'week' in period_lower:
            numbers = re.findall(r'\d+', period_lower)
            return int(numbers[0]) * 7 if numbers else 21
        elif '月' in period_lower or 'month' in period_lower:
            numbers = re.findall(r'\d+', period_lower)
            return int(numbers[0]) * 30 if numbers else 90
        else:
            return 30  # 默认30天
    
    def _find_customers_by_similar_products(self, product_name: str) -> List[Recommendation]:
        """通过相似产品找客户"""
        recommendations = []
        
        try:
            # 找到相似产品
            similar_products_aql = """
            FOR product IN products
                FILTER CONTAINS(LOWER(product.name), LOWER(@product_name)) OR
                       CONTAINS(LOWER(product.category), LOWER(@product_name))
                FOR inquiry IN 1..1 INBOUND product inquires_about
                    FOR customer IN 1..1 OUTBOUND inquiry comes_from
                    RETURN DISTINCT {
                        customer_id: customer._key,
                        customer_name: customer.name,
                        customer_email: customer.email,
                        value_score: customer.value_score,
                        purchase_intent: inquiry.purchase_intent
                    }
            """
            
            customers = list(self.arango_service.db.aql.execute(
                similar_products_aql, bind_vars={'product_name': product_name}
            ))
            
            for customer in customers:
                score = (
                    (customer.get('value_score', 0) / 100) * 0.6 +
                    (customer.get('purchase_intent', 0.5)) * 0.4
                )
                
                if score >= self.recommendation_config['min_recommendation_score']:
                    recommendation = Recommendation(
                        recommendation_type='customer',
                        target_id=customer['customer_id'],
                        target_name=customer['customer_name'],
                        score=score,
                        reason=f"该客户曾询盘相似产品，价值评分: {customer.get('value_score', 0)}",
                        supporting_data=customer
                    )
                    recommendations.append(recommendation)
            
        except Exception as e:
            self.logger.error(f"通过相似产品找客户失败: {str(e)}")
        
        return recommendations
    
    def _recommend_by_customer_behavior(self, product_name: str) -> List[Recommendation]:
        """基于客户行为推荐"""
        recommendations = []
        
        try:
            # 分析产品类别的客户行为模式
            behavior_aql = """
            FOR product IN products
                FILTER CONTAINS(LOWER(product.name), LOWER(@product_name))
                LET category = product.category
                FOR other_product IN products
                    FILTER other_product.category == category AND other_product._key != product._key
                    FOR inquiry IN 1..1 INBOUND other_product inquires_about
                        FOR customer IN 1..1 OUTBOUND inquiry comes_from
                        FILTER customer.value_score >= 60  // 中等价值以上客户
                        RETURN DISTINCT {
                            customer_id: customer._key,
                            customer_name: customer.name,
                            value_score: customer.value_score,
                            inquiry_frequency: customer.inquiry_frequency
                        }
            """
            
            customers = list(self.arango_service.db.aql.execute(
                behavior_aql, bind_vars={'product_name': product_name}
            ))
            
            for customer in customers:
                score = (
                    (customer.get('value_score', 0) / 100) * 0.5 +
                    min(customer.get('inquiry_frequency', 0) / 10, 1.0) * 0.5
                )
                
                if score >= self.recommendation_config['min_recommendation_score']:
                    recommendation = Recommendation(
                        recommendation_type='customer',
                        target_id=customer['customer_id'],
                        target_name=customer['customer_name'],
                        score=score,
                        reason=f"该客户在相同产品类别中表现活跃，询盘频率: {customer.get('inquiry_frequency', 0)}",
                        supporting_data=customer
                    )
                    recommendations.append(recommendation)
            
        except Exception as e:
            self.logger.error(f"基于客户行为推荐失败: {str(e)}")
        
        return recommendations
    
    def _recommend_by_demographics(self, product_name: str) -> List[Recommendation]:
        """基于地域和行业推荐"""
        recommendations = []
        
        try:
            # 分析产品的地域和行业分布
            demo_aql = """
            FOR product IN products
                FILTER CONTAINS(LOWER(product.name), LOWER(@product_name))
                FOR inquiry IN 1..1 INBOUND product inquires_about
                    FOR customer IN 1..1 OUTBOUND inquiry comes_from
                    COLLECT country = customer.country WITH COUNT INTO count
                    SORT count DESC
                    LIMIT 3
                    RETURN {
                        country: country,
                        frequency: count
                    }
            """
            
            top_countries = list(self.arango_service.db.aql.execute(
                demo_aql, bind_vars={'product_name': product_name}
            ))
            
            # 为这些国家的其他客户推荐
            for country_data in top_countries:
                country = country_data['country']
                
                country_customers_aql = """
                FOR customer IN customers
                    FILTER customer.country == @country
                    FILTER customer.value_score >= 50  // 基础价值要求
                    LIMIT 5
                    RETURN {
                        customer_id: customer._key,
                        customer_name: customer.name,
                        value_score: customer.value_score,
                        country: customer.country
                    }
                """
                
                customers = list(self.arango_service.db.aql.execute(
                    country_customers_aql, bind_vars={'country': country}
                ))
                
                for customer in customers:
                    score = (customer.get('value_score', 0) / 100) * 0.8  # 地域匹配权重较高
                    
                    if score >= self.recommendation_config['min_recommendation_score']:
                        recommendation = Recommendation(
                            recommendation_type='customer',
                            target_id=customer['customer_id'],
                            target_name=customer['customer_name'],
                            score=score,
                            reason=f"该客户来自产品热门地区 {country}，具有地域匹配优势",
                            supporting_data=customer
                        )
                        recommendations.append(recommendation)
            
        except Exception as e:
            self.logger.error(f"基于地域推荐失败: {str(e)}")
        
        return recommendations
    
    def _recommend_by_inquiry_history(self, customer_id: str) -> List[Recommendation]:
        """基于询盘历史推荐产品"""
        recommendations = []
        
        try:
            # 获取客户历史询盘的产品类别
            history_aql = """
            FOR customer IN customers
                FILTER customer._key == @customer_id
                FOR inquiry IN 1..1 INBOUND customer GRAPH 'inquiry_graph'
                    FOR product IN 1..1 OUTBOUND inquiry inquires_about
                    COLLECT category = product.category WITH COUNT INTO count
                    SORT count DESC
                    RETURN {
                        category: category,
                        frequency: count
                    }
            """
            
            categories = list(self.arango_service.db.aql.execute(
                history_aql, bind_vars={'customer_id': customer_id}
            ))
            
            # 为每个类别推荐新产品
            for category_data in categories:
                category = category_data['category']
                
                products_aql = """
                FOR product IN products
                    FILTER product.category == @category
                    // 排除客户已询盘的产品
                    LET already_inquired = (
                        FOR inquiry IN 1..1 INBOUND product inquires_about
                            FOR customer IN 1..1 OUTBOUND inquiry comes_from
                            FILTER customer._key == @customer_id
                            RETURN 1
                    )
                    FILTER LENGTH(already_inquired) == 0
                    LIMIT 3
                    RETURN {
                        product_id: product._key,
                        product_name: product.name,
                        category: product.category,
                        price: product.price
                    }
                """
                
                products = list(self.arango_service.db.aql.execute(
                    products_aql, bind_vars={'category': category, 'customer_id': customer_id}
                ))
                
                for product in products:
                    score = 0.8  # 基于历史的推荐分数较高
                    
                    recommendation = Recommendation(
                        recommendation_type='product',
                        target_id=product['product_id'],
                        target_name=product['product_name'],
                        score=score,
                        reason=f"基于您对 {category} 类别产品的历史询盘记录推荐",
                        supporting_data=product
                    )
                    recommendations.append(recommendation)
            
        except Exception as e:
            self.logger.error(f"基于询盘历史推荐失败: {str(e)}")
        
        return recommendations
    
    def _recommend_by_similar_customers(self, customer_id: str) -> List[Recommendation]:
        """基于相似客户推荐产品"""
        recommendations = []
        
        try:
            # 找到相似客户（基于地区、行业、价值评分）
            customer_info = self._get_customer_profile(customer_id)
            
            if not customer_info:
                return recommendations
            
            similar_customers_aql = """
            FOR customer IN customers
                FILTER customer._key != @customer_id
                FILTER customer.country == @country OR customer.region == @region
                FILTER ABS(customer.value_score - @value_score) <= 20
                FOR inquiry IN 1..1 INBOUND customer GRAPH 'inquiry_graph'
                    FOR product IN 1..1 OUTBOUND inquiry inquires_about
                    COLLECT product_id = product._key,
                            product_name = product.name,
                            category = product.category
                            WITH COUNT INTO frequency
                    SORT frequency DESC
                    LIMIT 5
                    RETURN {
                        product_id: product_id,
                        product_name: product_name,
                        category: category,
                        similarity_frequency: frequency
                    }
            """
            
            products = list(self.arango_service.db.aql.execute(similar_customers_aql, bind_vars={
                'customer_id': customer_id,
                'country': customer_info.get('country', ''),
                'region': customer_info.get('region', ''),
                'value_score': customer_info.get('value_score', 0)
            }))
            
            for product in products:
                score = min(product['similarity_frequency'] / 10, 1.0) * 0.7
                
                if score >= self.recommendation_config['min_recommendation_score']:
                    recommendation = Recommendation(
                        recommendation_type='product',
                        target_id=product['product_id'],
                        target_name=product['product_name'],
                        score=score,
                        reason=f"相似客户经常询盘此产品，相似度频次: {product['similarity_frequency']}",
                        supporting_data=product
                    )
                    recommendations.append(recommendation)
            
        except Exception as e:
            self.logger.error(f"基于相似客户推荐失败: {str(e)}")
        
        return recommendations
    
    def _recommend_by_demand_matching(self, customer_id: str) -> List[Recommendation]:
        """基于需求匹配推荐产品"""
        recommendations = []
        
        try:
            # 获取客户的需求偏好
            demands_aql = """
            FOR customer IN customers
                FILTER customer._key == @customer_id
                FOR inquiry IN 1..1 INBOUND customer GRAPH 'inquiry_graph'
                    FOR demand IN 1..1 OUTBOUND inquiry expresses
                    COLLECT demand_type = demand.type WITH COUNT INTO count
                    SORT count DESC
                    RETURN {
                        demand_type: demand_type,
                        frequency: count
                    }
            """
            
            demands = list(self.arango_service.db.aql.execute(
                demands_aql, bind_vars={'customer_id': customer_id}
            ))
            
            # 基于需求类型推荐产品
            for demand in demands:
                demand_type = demand['demand_type']
                
                # 这里可以根据需求类型匹配相应的产品特性
                # 简化实现：推荐该需求类型下热门的产品
                products_aql = """
                FOR demand IN demands
                    FILTER demand.type == @demand_type
                    FOR inquiry IN 1..1 INBOUND demand expresses
                        FOR product IN 1..1 OUTBOUND inquiry inquires_about
                        COLLECT product_id = product._key,
                                product_name = product.name,
                                category = product.category
                                WITH COUNT INTO frequency
                        SORT frequency DESC
                        LIMIT 3
                        RETURN {
                            product_id: product_id,
                            product_name: product_name,
                            category: category,
                            demand_match_frequency: frequency
                        }
                """
                
                products = list(self.arango_service.db.aql.execute(
                    products_aql, bind_vars={'demand_type': demand_type}
                ))
                
                for product in products:
                    score = min(product['demand_match_frequency'] / 5, 1.0) * 0.6
                    
                    if score >= self.recommendation_config['min_recommendation_score']:
                        recommendation = Recommendation(
                            recommendation_type='product',
                            target_id=product['product_id'],
                            target_name=product['product_name'],
                            score=score,
                            reason=f"该产品与您的 {demand_type} 需求高度匹配",
                            supporting_data=product
                        )
                        recommendations.append(recommendation)
            
        except Exception as e:
            self.logger.error(f"基于需求匹配推荐失败: {str(e)}")
        
        return recommendations
    
    def _get_customer_profile(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """获取客户档案"""
        try:
            customers = self.arango_service.db.collection('customers')
            return customers.get(customer_id)
        except Exception:
            return None
    
    def _recommend_strategies_by_grade(self, customer_info: Dict[str, Any]) -> List[Recommendation]:
        """基于客户等级推荐策略"""
        strategies = []
        
        grade = customer_info.get('customer_grade', 'C')
        customer_name = customer_info.get('name', '客户')
        
        if grade == 'A':
            strategies.extend([
                Recommendation(
                    recommendation_type='strategy',
                    target_id='vip_service',
                    target_name='VIP专属服务',
                    score=0.9,
                    reason='A级客户享受最高优先级服务',
                    supporting_data={'grade': grade, 'service_level': 'premium'}
                ),
                Recommendation(
                    recommendation_type='strategy',
                    target_id='custom_solution',
                    target_name='定制化解决方案',
                    score=0.85,
                    reason='为高价值客户提供个性化产品方案',
                    supporting_data={'customization_level': 'high'}
                )
            ])
        elif grade == 'B':
            strategies.extend([
                Recommendation(
                    recommendation_type='strategy',
                    target_id='regular_follow_up',
                    target_name='定期跟进服务',
                    score=0.7,
                    reason='B级客户需要定期维护关系',
                    supporting_data={'follow_up_frequency': 'weekly'}
                ),
                Recommendation(
                    recommendation_type='strategy',
                    target_id='upgrade_opportunity',
                    target_name='升级机会识别',
                    score=0.75,
                    reason='挖掘B级客户的升级潜力',
                    supporting_data={'upgrade_potential': 'medium'}
                )
            ])
        else:
            strategies.append(
                Recommendation(
                    recommendation_type='strategy',
                    target_id='nurture_program',
                    target_name='客户培育计划',
                    score=0.6,
                    reason='通过培育提升客户价值',
                    supporting_data={'nurture_duration': '3_months'}
                )
            )
        
        return strategies
    
    def _recommend_strategies_by_demands(self, customer_info: Dict[str, Any]) -> List[Recommendation]:
        """基于需求偏好推荐策略"""
        strategies = []
        
        # 这里简化实现，实际应该分析客户的具体需求偏好
        price_sensitivity = customer_info.get('price_sensitivity', 0.5)
        quality_focus = customer_info.get('quality_focus', 0.5)
        
        if price_sensitivity > 0.7:
            strategies.append(
                Recommendation(
                    recommendation_type='strategy',
                    target_id='cost_effective_solution',
                    target_name='性价比方案',
                    score=0.8,
                    reason='客户对价格敏感，推荐高性价比产品',
                    supporting_data={'price_sensitivity': price_sensitivity}
                )
            )
        
        if quality_focus > 0.7:
            strategies.append(
                Recommendation(
                    recommendation_type='strategy',
                    target_id='premium_quality',
                    target_name='高品质方案',
                    score=0.8,
                    reason='客户注重质量，推荐高品质产品和服务',
                    supporting_data={'quality_focus': quality_focus}
                )
            )
        
        return strategies
    
    def _recommend_strategies_by_behavior(self, customer_info: Dict[str, Any]) -> List[Recommendation]:
        """基于行为模式推荐策略"""
        strategies = []
        
        inquiry_frequency = customer_info.get('inquiry_frequency', 0)
        avg_purchase_intent = customer_info.get('avg_purchase_intent', 0.5)
        
        if inquiry_frequency > 5:
            strategies.append(
                Recommendation(
                    recommendation_type='strategy',
                    target_id='proactive_engagement',
                    target_name='主动互动策略',
                    score=0.75,
                    reason='客户询盘频繁，建议主动提供信息和服务',
                    supporting_data={'inquiry_frequency': inquiry_frequency}
                )
            )
        
        if avg_purchase_intent > 0.7:
            strategies.append(
                Recommendation(
                    recommendation_type='strategy',
                    target_id='accelerated_sales',
                    target_name='加速销售流程',
                    score=0.85,
                    reason='客户购买意向强烈，建议加快销售进程',
                    supporting_data={'purchase_intent': avg_purchase_intent}
                )
            )
        
        return strategies
    
    def _deduplicate_recommendations(self, recommendations: List[Recommendation]) -> List[Recommendation]:
        """去重推荐结果"""
        seen = set()
        unique_recommendations = []
        
        for rec in recommendations:
            key = f"{rec.recommendation_type}_{rec.target_id}"
            if key not in seen:
                unique_recommendations.append(rec)
                seen.add(key)
        
        return unique_recommendations
    
    def _classify_email(self, email: Dict[str, Any]) -> Dict[str, Any]:
        """分类邮件"""
        subject = email.get('subject', '').lower()
        content = email.get('content', '').lower()
        
        # 简单的关键词分类
        if any(word in subject + content for word in ['inquiry', 'quote', 'price', 'quotation']):
            category = 'inquiry'
            urgency = 'medium'
        elif any(word in subject + content for word in ['urgent', 'asap', 'immediately']):
            category = 'urgent_inquiry'
            urgency = 'high'
        elif any(word in subject + content for word in ['complaint', 'problem', 'issue']):
            category = 'complaint'
            urgency = 'high'
        elif any(word in subject + content for word in ['thank', 'thanks', 'feedback']):
            category = 'feedback'
            urgency = 'low'
        else:
            category = 'general'
            urgency = 'medium'
        
        return {
            'category': category,
            'urgency': urgency,
            'keywords': self._extract_keywords_from_email(subject + ' ' + content)
        }
    
    def _calculate_email_priority(self, email: Dict[str, Any], classification: Dict[str, Any]) -> int:
        """计算邮件优先级"""
        base_priority = 3  # 默认优先级
        
        # 基于分类调整优先级
        category_priorities = {
            'urgent_inquiry': 5,
            'complaint': 5,
            'inquiry': 4,
            'feedback': 2,
            'general': 3
        }
        
        priority = category_priorities.get(classification['category'], base_priority)
        
        # 基于发送者调整优先级
        sender = email.get('sender', '')
        if self._is_vip_customer(sender):
            priority = min(priority + 1, 5)
        
        return priority
    
    def _is_vip_customer(self, email_address: str) -> bool:
        """判断是否为VIP客户"""
        try:
            aql = """
            FOR customer IN customers
                FILTER customer.email == @email
                FILTER customer.customer_grade == 'A' OR customer.value_score >= 80
                RETURN customer
            """
            
            result = list(self.arango_service.db.aql.execute(
                aql, bind_vars={'email': email_address}
            ))
            
            return len(result) > 0
            
        except Exception:
            return False
    
    def _extract_keywords_from_email(self, text: str) -> List[str]:
        """从邮件中提取关键词"""
        # 简单的关键词提取
        words = re.findall(r'\b\w+\b', text.lower())
        # 过滤停用词和短词
        keywords = [w for w in words if len(w) > 3 and w not in 
                   ['this', 'that', 'with', 'have', 'will', 'from', 'they', 'been', 'your', 'please']]
        
        # 返回频率最高的关键词
        from collections import Counter
        word_counts = Counter(keywords)
        return [word for word, count in word_counts.most_common(10)]
    
    def _get_inquiry_details(self, inquiry_id: str) -> Optional[Dict[str, Any]]:
        """获取询盘详情"""
        try:
            inquiries = self.arango_service.db.collection('inquiries')
            return inquiries.get(inquiry_id)
        except Exception:
            return None
    
    def _analyze_inquiry_content(self, inquiry_info: Dict[str, Any]) -> Dict[str, Any]:
        """分析询盘内容"""
        content = inquiry_info.get('email_content', '')
        subject = inquiry_info.get('email_subject', '')
        
        analysis = {
            'content_length': len(content),
            'has_specific_requirements': len(re.findall(r'\d+', content)) > 0,
            'urgency_indicators': len(re.findall(r'urgent|asap|immediately|rush', content.lower())),
            'price_mentions': len(re.findall(r'price|cost|quote|budget', content.lower())),
            'quantity_mentions': len(re.findall(r'quantity|moq|pieces|units', content.lower()))
        }
        
        return analysis
    
    def _generate_reply_templates(self, inquiry_info: Dict[str, Any], 
                                analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成回复模板"""
        templates = []
        
        # 基础询盘回复
        templates.append({
            'template': f"""感谢您对我们产品的询盘。
            
我们已收到您关于{inquiry_info.get('mentioned_products', ['产品'])[0] if inquiry_info.get('mentioned_products') else '产品'}的询盘，我们的销售团队将在24小时内与您联系，为您提供详细的产品信息和报价。
            
如有紧急需求，请随时联系我们。
            
最诚挚的问候""",
            'priority': 3,
            'type': 'standard_inquiry'
        })
        
        # 紧急询盘回复
        if analysis['urgency_indicators'] > 0:
            templates.append({
                'template': """我们注意到您的询盘具有紧急性。
                
我们的专属客户经理将在2小时内与您直接联系，确保您的需求得到及时处理。
                
感谢您的信任。""",
                'priority': 5,
                'type': 'urgent_inquiry'
            })
        
        # 价格询盘回复
        if analysis['price_mentions'] > 0:
            templates.append({
                'template': """关于您询问的产品价格，我们将根据您的具体需求和数量要求为您提供最优惠的报价。
                
请提供以下信息以便我们为您准备准确报价：
                1. 具体产品规格要求
                2. 预计采购数量
                3. 交货时间要求
                4. 目标价格区间
                
我们承诺在收到完整信息后24小时内回复详细报价。""",
                'priority': 4,
                'type': 'price_inquiry'
            })
        
        return templates
    
    def _identify_follow_up_targets(self) -> List[Dict[str, Any]]:
        """识别需要跟进的目标"""
        try:
            # 查找最近有询盘但未跟进的客户
            aql = """
            FOR customer IN customers
                LET recent_inquiries = (
                    FOR inquiry IN 1..1 INBOUND customer GRAPH 'inquiry_graph'
                        FILTER DATE_DIFF(inquiry.created_at, DATE_NOW(), 'day') <= 30
                        SORT inquiry.created_at DESC
                        RETURN inquiry
                )
                FILTER LENGTH(recent_inquiries) > 0
                LET last_follow_up = customer.last_follow_up_date
                FILTER !last_follow_up OR DATE_DIFF(last_follow_up, DATE_NOW(), 'day') > 7
                RETURN {
                    customer_id: customer._key,
                    customer_name: customer.name,
                    customer_grade: customer.customer_grade,
                    value_score: customer.value_score,
                    last_inquiry_date: recent_inquiries[0].created_at,
                    inquiry_count: LENGTH(recent_inquiries),
                    last_follow_up_date: last_follow_up
                }
            """
            
            return list(self.arango_service.db.aql.execute(aql))
            
        except Exception as e:
            self.logger.error(f"识别跟进目标失败: {str(e)}")
            return []
    
    def _calculate_follow_up_priority(self, target: Dict[str, Any]) -> int:
        """计算跟进优先级"""
        base_priority = 3
        
        # 基于客户等级调整
        grade = target.get('customer_grade', 'C')
        if grade == 'A':
            base_priority += 2
        elif grade == 'B':
            base_priority += 1
        
        # 基于价值评分调整
        value_score = target.get('value_score', 0)
        if value_score >= 80:
            base_priority += 1
        
        # 基于询盘频率调整
        inquiry_count = target.get('inquiry_count', 0)
        if inquiry_count >= 3:
            base_priority += 1
        
        return min(base_priority, 5)
    
    def _calculate_follow_up_date(self, target: Dict[str, Any], days_ahead: int) -> datetime:
        """计算跟进日期"""
        priority = self._calculate_follow_up_priority(target)
        
        # 高优先级客户更早跟进
        if priority >= 5:
            days_offset = 1
        elif priority >= 4:
            days_offset = 2
        else:
            days_offset = min(days_ahead // 2, 3)
        
        return datetime.now() + timedelta(days=days_offset)
    
    def _generate_follow_up_suggestion(self, target: Dict[str, Any]) -> str:
        """生成跟进建议"""
        customer_name = target.get('customer_name', '客户')
        grade = target.get('customer_grade', 'C')
        inquiry_count = target.get('inquiry_count', 0)
        
        if grade == 'A':
            return f"高价值客户 {customer_name} 需要专属客户经理主动联系，了解最新需求并提供个性化服务"
        elif inquiry_count >= 3:
            return f"活跃客户 {customer_name} 近期询盘频繁，建议主动提供产品更新信息和优惠方案"
        else:
            return f"客户 {customer_name} 需要定期维护，发送产品资讯和行业动态保持联系"