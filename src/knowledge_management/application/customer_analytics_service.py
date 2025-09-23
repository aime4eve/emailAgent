#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
客户价值分析系统
实现客户价值评估模型、分级管理和客户画像构建
"""

from typing import Dict, List, Any, Optional, Tuple
import logging
import statistics
import numpy as np
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict

# 机器学习相关导入
try:
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA
    import pandas as pd
except ImportError as e:
    logging.warning(f"机器学习库导入失败: {e}")
    KMeans = None
    StandardScaler = None
    PCA = None
    pd = None

from ...shared.database.arango_service import ArangoDBService
from ..domain.model.inquiry_ontology import CustomerGrade, CustomerType

@dataclass
class CustomerValueMetrics:
    """客户价值指标"""
    customer_id: str
    inquiry_activity_score: float = 0.0      # 询盘活跃度评分
    product_value_score: float = 0.0         # 产品价值度评分
    company_strength_score: float = 0.0      # 公司实力度评分
    demand_clarity_score: float = 0.0        # 需求明确度评分
    cooperation_potential_score: float = 0.0 # 合作潜力度评分
    overall_score: float = 0.0               # 综合评分
    grade: CustomerGrade = CustomerGrade.C   # 客户等级
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'customer_id': self.customer_id,
            'inquiry_activity_score': self.inquiry_activity_score,
            'product_value_score': self.product_value_score,
            'company_strength_score': self.company_strength_score,
            'demand_clarity_score': self.demand_clarity_score,
            'cooperation_potential_score': self.cooperation_potential_score,
            'overall_score': self.overall_score,
            'grade': self.grade.value
        }

@dataclass
class CustomerProfile:
    """客户画像"""
    customer_id: str
    basic_info: Dict[str, Any]
    behavioral_profile: Dict[str, Any]
    demand_profile: Dict[str, Any]
    value_metrics: CustomerValueMetrics
    segmentation: str
    recommendations: List[str]
    last_updated: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'customer_id': self.customer_id,
            'basic_info': self.basic_info,
            'behavioral_profile': self.behavioral_profile,
            'demand_profile': self.demand_profile,
            'value_metrics': self.value_metrics.to_dict(),
            'segmentation': self.segmentation,
            'recommendations': self.recommendations,
            'last_updated': self.last_updated.isoformat()
        }

class CustomerAnalyticsService:
    """客户价值分析服务"""
    
    def __init__(self, arango_service: ArangoDBService):
        """
        初始化客户分析服务
        
        Args:
            arango_service: ArangoDB数据库服务
        """
        self.arango_service = arango_service
        self.logger = logging.getLogger(__name__)
        
        # 评估维度权重配置
        self.evaluation_weights = {
            'inquiry_activity': 0.25,     # 询盘活跃度
            'product_value': 0.25,        # 产品价值度
            'company_strength': 0.20,     # 公司实力度
            'demand_clarity': 0.15,       # 需求明确度
            'cooperation_potential': 0.15  # 合作潜力度
        }
        
        # 客户分级阈值
        self.grade_thresholds = {
            CustomerGrade.A: 80.0,  # A级客户：高价值、高潜力、优先跟进
            CustomerGrade.B: 60.0,  # B级客户：中等价值、有潜力、定期维护
            CustomerGrade.C: 0.0    # C级客户：低价值、观察跟踪
        }
    
    def calculate_customer_value_metrics(self, customer_id: str) -> CustomerValueMetrics:
        """
        计算客户价值指标
        
        Args:
            customer_id: 客户ID
            
        Returns:
            客户价值指标
        """
        try:
            metrics = CustomerValueMetrics(customer_id=customer_id)
            
            # 1. 询盘活跃度评分
            metrics.inquiry_activity_score = self._calculate_inquiry_activity_score(customer_id)
            
            # 2. 产品价值度评分
            metrics.product_value_score = self._calculate_product_value_score(customer_id)
            
            # 3. 公司实力度评分
            metrics.company_strength_score = self._calculate_company_strength_score(customer_id)
            
            # 4. 需求明确度评分
            metrics.demand_clarity_score = self._calculate_demand_clarity_score(customer_id)
            
            # 5. 合作潜力度评分
            metrics.cooperation_potential_score = self._calculate_cooperation_potential_score(customer_id)
            
            # 6. 计算综合评分
            metrics.overall_score = self._calculate_overall_score(metrics)
            
            # 7. 确定客户等级
            metrics.grade = self._determine_customer_grade(metrics.overall_score)
            
            self.logger.info(f"客户 {customer_id} 价值评估完成，综合评分: {metrics.overall_score:.2f}")
            return metrics
            
        except Exception as e:
            self.logger.error(f"计算客户价值指标失败: {str(e)}")
            return CustomerValueMetrics(customer_id=customer_id)
    
    def batch_calculate_customer_metrics(self, customer_ids: List[str] = None) -> List[CustomerValueMetrics]:
        """
        批量计算客户价值指标
        
        Args:
            customer_ids: 客户ID列表，如果为None则计算所有客户
            
        Returns:
            客户价值指标列表
        """
        try:
            if customer_ids is None:
                # 获取所有客户ID
                aql = "FOR customer IN customers RETURN customer._key"
                customer_ids = list(self.arango_service.db.aql.execute(aql))
            
            metrics_list = []
            for customer_id in customer_ids:
                metrics = self.calculate_customer_value_metrics(customer_id)
                metrics_list.append(metrics)
                
                # 更新数据库中的客户价值信息
                self._update_customer_value_in_db(customer_id, metrics)
            
            self.logger.info(f"批量计算 {len(metrics_list)} 个客户的价值指标完成")
            return metrics_list
            
        except Exception as e:
            self.logger.error(f"批量计算客户价值指标失败: {str(e)}")
            return []
    
    def build_customer_profile(self, customer_id: str) -> CustomerProfile:
        """
        构建客户画像
        
        Args:
            customer_id: 客户ID
            
        Returns:
            客户画像
        """
        try:
            # 获取基础信息
            basic_info = self._get_customer_basic_info(customer_id)
            
            # 构建行为画像
            behavioral_profile = self._build_behavioral_profile(customer_id)
            
            # 构建需求画像
            demand_profile = self._build_demand_profile(customer_id)
            
            # 计算价值指标
            value_metrics = self.calculate_customer_value_metrics(customer_id)
            
            # 客户细分
            segmentation = self._determine_customer_segmentation(value_metrics, behavioral_profile)
            
            # 生成推荐建议
            recommendations = self._generate_customer_recommendations(value_metrics, behavioral_profile, demand_profile)
            
            profile = CustomerProfile(
                customer_id=customer_id,
                basic_info=basic_info,
                behavioral_profile=behavioral_profile,
                demand_profile=demand_profile,
                value_metrics=value_metrics,
                segmentation=segmentation,
                recommendations=recommendations,
                last_updated=datetime.now()
            )
            
            self.logger.info(f"客户 {customer_id} 画像构建完成")
            return profile
            
        except Exception as e:
            self.logger.error(f"构建客户画像失败: {str(e)}")
            return CustomerProfile(
                customer_id=customer_id,
                basic_info={},
                behavioral_profile={},
                demand_profile={},
                value_metrics=CustomerValueMetrics(customer_id=customer_id),
                segmentation='unknown',
                recommendations=[],
                last_updated=datetime.now()
            )
    
    def perform_customer_segmentation(self, customer_ids: List[str] = None) -> Dict[str, List[str]]:
        """
        执行客户细分分析
        
        Args:
            customer_ids: 客户ID列表
            
        Returns:
            客户细分结果
        """
        try:
            if not KMeans or not pd:
                self.logger.warning("机器学习库不可用，使用基础细分方法")
                return self._basic_customer_segmentation(customer_ids)
            
            # 获取客户价值指标数据
            metrics_list = self.batch_calculate_customer_metrics(customer_ids)
            
            if len(metrics_list) < 3:
                self.logger.warning("客户数量太少，无法进行聚类分析")
                return self._basic_customer_segmentation(customer_ids)
            
            # 准备特征数据
            features = []
            customer_id_list = []
            
            for metrics in metrics_list:
                features.append([
                    metrics.inquiry_activity_score,
                    metrics.product_value_score,
                    metrics.company_strength_score,
                    metrics.demand_clarity_score,
                    metrics.cooperation_potential_score
                ])
                customer_id_list.append(metrics.customer_id)
            
            # 标准化特征
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(features)
            
            # K-means聚类
            n_clusters = min(5, len(features))  # 最多5个聚类
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            cluster_labels = kmeans.fit_predict(features_scaled)
            
            # 整理聚类结果
            segmentation_result = defaultdict(list)
            segment_names = ['高价值活跃型', '潜力成长型', '稳定合作型', '观察培育型', '低价值型']
            
            for i, customer_id in enumerate(customer_id_list):
                cluster_id = cluster_labels[i]
                segment_name = segment_names[cluster_id] if cluster_id < len(segment_names) else f'细分{cluster_id}'
                segmentation_result[segment_name].append(customer_id)
            
            self.logger.info(f"客户细分完成，共 {len(segmentation_result)} 个细分")
            return dict(segmentation_result)
            
        except Exception as e:
            self.logger.error(f"客户细分分析失败: {str(e)}")
            return self._basic_customer_segmentation(customer_ids)
    
    def get_customer_analytics_dashboard(self) -> Dict[str, Any]:
        """
        获取客户分析仪表板数据
        
        Returns:
            仪表板数据
        """
        try:
            dashboard_data = {
                'overview': self._get_customer_overview(),
                'grade_distribution': self._get_grade_distribution(),
                'value_score_distribution': self._get_value_score_distribution(),
                'geographic_distribution': self._get_geographic_distribution(),
                'industry_distribution': self._get_industry_distribution(),
                'top_customers': self._get_top_customers(),
                'trends': self._get_customer_trends()
            }
            
            self.logger.info("客户分析仪表板数据获取完成")
            return dashboard_data
            
        except Exception as e:
            self.logger.error(f"获取客户分析仪表板数据失败: {str(e)}")
            return {}
    
    # 私有方法实现
    
    def _calculate_inquiry_activity_score(self, customer_id: str) -> float:
        """计算询盘活跃度评分"""
        try:
            # 获取最近90天的询盘数据
            aql = """
            FOR inquiry IN inquiries
                FOR customer IN 1..1 OUTBOUND inquiry comes_from
                FILTER customer._key == @customer_id
                FILTER DATE_DIFF(inquiry.created_at, DATE_NOW(), 'day') <= 90
                RETURN {
                    inquiry_date: inquiry.created_at,
                    urgency: inquiry.urgency,
                    purchase_intent: inquiry.purchase_intent
                }
            """
            
            inquiries = list(self.arango_service.db.aql.execute(aql, bind_vars={'customer_id': customer_id}))
            
            if not inquiries:
                return 20.0  # 基础分数
            
            # 基础活跃度评分
            inquiry_count = len(inquiries)
            base_score = min(inquiry_count * 10, 60)  # 最高60分
            
            # 询盘频率评分
            if inquiry_count > 1:
                dates = [datetime.fromisoformat(inq['inquiry_date'].replace('Z', '+00:00')) for inq in inquiries]
                dates.sort()
                intervals = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
                avg_interval = statistics.mean(intervals) if intervals else 30
                
                # 间隔越短，分数越高
                frequency_score = max(0, 20 - avg_interval * 0.5)
            else:
                frequency_score = 0
            
            # 紧急程度评分
            urgency_scores = {'urgent': 4, 'high': 3, 'medium': 2, 'low': 1}
            avg_urgency = statistics.mean([urgency_scores.get(inq.get('urgency', 'low'), 1) for inq in inquiries])
            urgency_score = avg_urgency * 5  # 最高20分
            
            total_score = base_score + frequency_score + urgency_score
            return min(total_score, 100.0)
            
        except Exception as e:
            self.logger.error(f"计算询盘活跃度评分失败: {str(e)}")
            return 20.0
    
    def _calculate_product_value_score(self, customer_id: str) -> float:
        """计算产品价值度评分"""
        try:
            # 获取客户询盘的产品信息
            aql = """
            FOR inquiry IN inquiries
                FOR customer IN 1..1 OUTBOUND inquiry comes_from
                FILTER customer._key == @customer_id
                FOR product IN 1..1 OUTBOUND inquiry inquires_about
                RETURN {
                    price: product.price,
                    category: product.category,
                    moq: product.moq
                }
            """
            
            products = list(self.arango_service.db.aql.execute(aql, bind_vars={'customer_id': customer_id}))
            
            if not products:
                return 30.0  # 默认分数
            
            # 价格评分
            prices = [p['price'] for p in products if p.get('price')]
            if prices:
                avg_price = statistics.mean(prices)
                if avg_price >= 1000:
                    price_score = 40.0
                elif avg_price >= 500:
                    price_score = 30.0
                elif avg_price >= 200:
                    price_score = 20.0
                else:
                    price_score = 10.0
            else:
                price_score = 15.0
            
            # 产品类别多样性评分
            categories = set(p['category'] for p in products if p.get('category'))
            diversity_score = min(len(categories) * 10, 30)  # 最高30分
            
            # MOQ评分（订单量大小）
            moqs = [p['moq'] for p in products if p.get('moq')]
            if moqs:
                avg_moq = statistics.mean(moqs)
                if avg_moq >= 1000:
                    moq_score = 30.0
                elif avg_moq >= 500:
                    moq_score = 20.0
                elif avg_moq >= 100:
                    moq_score = 15.0
                else:
                    moq_score = 10.0
            else:
                moq_score = 15.0
            
            total_score = price_score + diversity_score + moq_score
            return min(total_score, 100.0)
            
        except Exception as e:
            self.logger.error(f"计算产品价值度评分失败: {str(e)}")
            return 30.0
    
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
                return 20.0  # 无公司信息默认分数
            
            company = companies[0]
            score = 20.0  # 基础分数
            
            # 公司规模评分
            scale_scores = {
                'enterprise': 30.0,
                'large': 25.0,
                'medium': 20.0,
                'small': 15.0,
                'startup': 10.0
            }
            scale = company.get('scale', 'small')
            score += scale_scores.get(scale, 15.0)
            
            # 年收入评分
            annual_revenue = company.get('annual_revenue')
            if annual_revenue:
                if annual_revenue >= 100000000:  # 1亿以上
                    score += 25.0
                elif annual_revenue >= 10000000:  # 1000万以上
                    score += 20.0
                elif annual_revenue >= 1000000:  # 100万以上
                    score += 15.0
                else:
                    score += 10.0
            
            # 员工数量评分
            employee_count = company.get('employee_count')
            if employee_count:
                if employee_count >= 1000:
                    score += 15.0
                elif employee_count >= 500:
                    score += 12.0
                elif employee_count >= 100:
                    score += 10.0
                elif employee_count >= 50:
                    score += 8.0
                else:
                    score += 5.0
            
            # 成立年份评分（历史悠久程度）
            established_year = company.get('established_year')
            if established_year:
                years_in_business = datetime.now().year - established_year
                if years_in_business >= 20:
                    score += 10.0
                elif years_in_business >= 10:
                    score += 8.0
                elif years_in_business >= 5:
                    score += 5.0
                else:
                    score += 2.0
            
            return min(score, 100.0)
            
        except Exception as e:
            self.logger.error(f"计算公司实力度评分失败: {str(e)}")
            return 20.0
    
    def _calculate_demand_clarity_score(self, customer_id: str) -> float:
        """计算需求明确度评分"""
        try:
            # 获取客户询盘中的需求信息
            aql = """
            FOR inquiry IN inquiries
                FOR customer IN 1..1 OUTBOUND inquiry comes_from
                FILTER customer._key == @customer_id
                FOR demand IN 1..1 OUTBOUND inquiry expresses
                RETURN {
                    demand_description: demand.description,
                    demand_type: demand.type,
                    inquiry_content: inquiry.email_content,
                    specifications: inquiry.mentioned_products
                }
            """
            
            demands = list(self.arango_service.db.aql.execute(aql, bind_vars={'customer_id': customer_id}))
            
            if not demands:
                return 15.0  # 默认分数
            
            total_score = 0.0
            
            for demand in demands:
                score = 0.0
                
                # 需求描述详细程度评分
                description = demand.get('demand_description', '')
                if len(description) > 100:
                    score += 20.0
                elif len(description) > 50:
                    score += 15.0
                elif len(description) > 20:
                    score += 10.0
                else:
                    score += 5.0
                
                # 询盘内容详细程度评分
                content = demand.get('inquiry_content', '')
                if len(content) > 500:
                    score += 15.0
                elif len(content) > 200:
                    score += 10.0
                elif len(content) > 100:
                    score += 8.0
                else:
                    score += 5.0
                
                # 产品规格明确性评分
                specifications = demand.get('specifications', [])
                if len(specifications) > 3:
                    score += 15.0
                elif len(specifications) > 1:
                    score += 10.0
                elif len(specifications) > 0:
                    score += 5.0
                
                total_score += score
            
            avg_score = total_score / len(demands) if demands else 15.0
            return min(avg_score, 100.0)
            
        except Exception as e:
            self.logger.error(f"计算需求明确度评分失败: {str(e)}")
            return 15.0
    
    def _calculate_cooperation_potential_score(self, customer_id: str) -> float:
        """计算合作潜力度评分"""
        try:
            # 获取客户询盘的情感和意向数据
            aql = """
            FOR inquiry IN inquiries
                FOR customer IN 1..1 OUTBOUND inquiry comes_from
                FILTER customer._key == @customer_id
                RETURN {
                    purchase_intent: inquiry.purchase_intent,
                    sentiment_score: inquiry.sentiment_score,
                    urgency: inquiry.urgency,
                    follow_up_required: inquiry.follow_up_required
                }
            """
            
            inquiries = list(self.arango_service.db.aql.execute(aql, bind_vars={'customer_id': customer_id}))
            
            if not inquiries:
                return 25.0  # 默认分数
            
            score = 25.0  # 基础分数
            
            # 购买意向评分
            purchase_intents = [inq.get('purchase_intent', 0.5) for inq in inquiries if inq.get('purchase_intent') is not None]
            if purchase_intents:
                avg_intent = statistics.mean(purchase_intents)
                score += avg_intent * 30.0  # 最高30分
            
            # 情感分析评分
            sentiment_scores = [inq.get('sentiment_score', 0.0) for inq in inquiries if inq.get('sentiment_score') is not None]
            if sentiment_scores:
                avg_sentiment = statistics.mean(sentiment_scores)
                # 将情感分数(-1到1)转换为0到20分
                sentiment_score = (avg_sentiment + 1) * 10.0
                score += sentiment_score
            
            # 紧急程度评分
            urgency_counts = defaultdict(int)
            for inq in inquiries:
                urgency = inq.get('urgency', 'low')
                urgency_counts[urgency] += 1
            
            urgency_weights = {'urgent': 4, 'high': 3, 'medium': 2, 'low': 1}
            weighted_urgency = sum(urgency_weights.get(urgency, 1) * count for urgency, count in urgency_counts.items())
            avg_urgency = weighted_urgency / len(inquiries) if inquiries else 1
            score += avg_urgency * 5.0  # 最高20分
            
            # 跟进需求评分
            follow_up_count = sum(1 for inq in inquiries if inq.get('follow_up_required', False))
            follow_up_ratio = follow_up_count / len(inquiries) if inquiries else 0
            score += follow_up_ratio * 5.0  # 最高5分
            
            return min(score, 100.0)
            
        except Exception as e:
            self.logger.error(f"计算合作潜力度评分失败: {str(e)}")
            return 25.0
    
    def _calculate_overall_score(self, metrics: CustomerValueMetrics) -> float:
        """计算综合评分"""
        overall_score = (
            metrics.inquiry_activity_score * self.evaluation_weights['inquiry_activity'] +
            metrics.product_value_score * self.evaluation_weights['product_value'] +
            metrics.company_strength_score * self.evaluation_weights['company_strength'] +
            metrics.demand_clarity_score * self.evaluation_weights['demand_clarity'] +
            metrics.cooperation_potential_score * self.evaluation_weights['cooperation_potential']
        )
        return round(overall_score, 2)
    
    def _determine_customer_grade(self, overall_score: float) -> CustomerGrade:
        """确定客户等级"""
        if overall_score >= self.grade_thresholds[CustomerGrade.A]:
            return CustomerGrade.A
        elif overall_score >= self.grade_thresholds[CustomerGrade.B]:
            return CustomerGrade.B
        else:
            return CustomerGrade.C
    
    def _update_customer_value_in_db(self, customer_id: str, metrics: CustomerValueMetrics):
        """更新数据库中的客户价值信息"""
        try:
            customers = self.arango_service.db.collection('customers')
            customers.update(customer_id, {
                'value_score': metrics.overall_score,
                'customer_grade': metrics.grade.value,
                'inquiry_activity_score': metrics.inquiry_activity_score,
                'product_value_score': metrics.product_value_score,
                'company_strength_score': metrics.company_strength_score,
                'demand_clarity_score': metrics.demand_clarity_score,
                'cooperation_potential_score': metrics.cooperation_potential_score,
                'value_updated_at': datetime.now().isoformat()
            })
        except Exception as e:
            self.logger.error(f"更新客户价值信息失败: {str(e)}")
    
    def _get_customer_basic_info(self, customer_id: str) -> Dict[str, Any]:
        """获取客户基础信息"""
        try:
            customers = self.arango_service.db.collection('customers')
            customer = customers.get(customer_id)
            return customer if customer else {}
        except Exception:
            return {}
    
    def _build_behavioral_profile(self, customer_id: str) -> Dict[str, Any]:
        """构建行为画像"""
        try:
            # 询盘行为分析
            inquiry_aql = """
            FOR inquiry IN inquiries
                FOR customer IN 1..1 OUTBOUND inquiry comes_from
                FILTER customer._key == @customer_id
                RETURN {
                    inquiry_date: inquiry.created_at,
                    urgency: inquiry.urgency,
                    purchase_intent: inquiry.purchase_intent,
                    hour: DATE_HOUR(inquiry.created_at),
                    day_of_week: DATE_DAYOFWEEK(inquiry.created_at)
                }
            """
            
            inquiries = list(self.arango_service.db.aql.execute(inquiry_aql, bind_vars={'customer_id': customer_id}))
            
            # 产品偏好分析
            product_aql = """
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
            
            product_preferences = list(self.arango_service.db.aql.execute(product_aql, bind_vars={'customer_id': customer_id}))
            
            # 时间行为模式
            if inquiries:
                hours = [inq['hour'] for inq in inquiries if inq.get('hour') is not None]
                days = [inq['day_of_week'] for inq in inquiries if inq.get('day_of_week') is not None]
                
                preferred_hours = statistics.mode(hours) if hours else None
                preferred_days = statistics.mode(days) if days else None
            else:
                preferred_hours = None
                preferred_days = None
            
            return {
                'total_inquiries': len(inquiries),
                'product_preferences': product_preferences,
                'preferred_inquiry_hour': preferred_hours,
                'preferred_inquiry_day': preferred_days,
                'avg_purchase_intent': statistics.mean([inq.get('purchase_intent', 0.5) for inq in inquiries]) if inquiries else 0.5,
                'inquiry_frequency': len(inquiries) / max((datetime.now() - datetime.fromisoformat(inquiries[0]['inquiry_date'].replace('Z', '+00:00'))).days, 1) if inquiries else 0
            }
            
        except Exception as e:
            self.logger.error(f"构建行为画像失败: {str(e)}")
            return {}
    
    def _build_demand_profile(self, customer_id: str) -> Dict[str, Any]:
        """构建需求画像"""
        try:
            # 需求类型分析
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
            
            demand_distribution = list(self.arango_service.db.aql.execute(demand_aql, bind_vars={'customer_id': customer_id}))
            
            # 价格敏感度分析
            price_focus = sum(d['count'] for d in demand_distribution if d['demand_type'] == 'price')
            quality_focus = sum(d['count'] for d in demand_distribution if d['demand_type'] in ['performance', 'certification'])
            total_demands = sum(d['count'] for d in demand_distribution)
            
            return {
                'demand_distribution': demand_distribution,
                'price_sensitivity': price_focus / total_demands if total_demands > 0 else 0,
                'quality_focus': quality_focus / total_demands if total_demands > 0 else 0,
                'total_demands': total_demands,
                'primary_demand_type': demand_distribution[0]['demand_type'] if demand_distribution else 'unknown'
            }
            
        except Exception as e:
            self.logger.error(f"构建需求画像失败: {str(e)}")
            return {}
    
    def _determine_customer_segmentation(self, value_metrics: CustomerValueMetrics, behavioral_profile: Dict[str, Any]) -> str:
        """确定客户细分"""
        try:
            score = value_metrics.overall_score
            inquiry_count = behavioral_profile.get('total_inquiries', 0)
            avg_intent = behavioral_profile.get('avg_purchase_intent', 0.5)
            
            if score >= 80 and inquiry_count >= 5:
                return '高价值活跃型'
            elif score >= 60 and avg_intent >= 0.7:
                return '潜力成长型'
            elif score >= 60:
                return '稳定合作型'
            elif inquiry_count >= 3:
                return '观察培育型'
            else:
                return '低价值型'
                
        except Exception:
            return '未分类'
    
    def _generate_customer_recommendations(self, value_metrics: CustomerValueMetrics, 
                                         behavioral_profile: Dict[str, Any], 
                                         demand_profile: Dict[str, Any]) -> List[str]:
        """生成客户推荐建议"""
        recommendations = []
        
        try:
            # 基于客户等级的建议
            if value_metrics.grade == CustomerGrade.A:
                recommendations.extend([
                    '优先响应客户询盘，提供专属客户经理服务',
                    '定期主动联系，了解最新需求动态',
                    '提供定制化产品方案和优惠政策'
                ])
            elif value_metrics.grade == CustomerGrade.B:
                recommendations.extend([
                    '定期跟进客户需求，保持良好沟通',
                    '提供标准化产品方案和合理报价',
                    '关注客户业务发展，寻找合作机会'
                ])
            else:
                recommendations.extend([
                    '基础服务响应，观察客户发展潜力',
                    '提供标准产品信息和报价',
                    '适时进行客户培育和关系维护'
                ])
            
            # 基于行为特征的建议
            if behavioral_profile.get('avg_purchase_intent', 0) > 0.7:
                recommendations.append('客户购买意向强烈，建议加快报价和方案制定')
            
            if behavioral_profile.get('inquiry_frequency', 0) > 0.5:
                recommendations.append('客户询盘频繁，建议建立长期合作关系')
            
            # 基于需求特征的建议
            if demand_profile.get('price_sensitivity', 0) > 0.5:
                recommendations.append('客户对价格敏感，建议提供性价比方案')
            
            if demand_profile.get('quality_focus', 0) > 0.5:
                recommendations.append('客户注重质量，建议强调产品质量和认证')
            
        except Exception as e:
            self.logger.error(f"生成客户推荐建议失败: {str(e)}")
        
        return recommendations
    
    def _basic_customer_segmentation(self, customer_ids: List[str] = None) -> Dict[str, List[str]]:
        """基础客户细分方法"""
        try:
            if customer_ids is None:
                aql = "FOR customer IN customers RETURN customer._key"
                customer_ids = list(self.arango_service.db.aql.execute(aql))
            
            segmentation = {
                '高价值客户': [],
                '中等价值客户': [],
                '低价值客户': []
            }
            
            for customer_id in customer_ids:
                metrics = self.calculate_customer_value_metrics(customer_id)
                if metrics.grade == CustomerGrade.A:
                    segmentation['高价值客户'].append(customer_id)
                elif metrics.grade == CustomerGrade.B:
                    segmentation['中等价值客户'].append(customer_id)
                else:
                    segmentation['低价值客户'].append(customer_id)
            
            return segmentation
            
        except Exception as e:
            self.logger.error(f"基础客户细分失败: {str(e)}")
            return {}
    
    def _get_customer_overview(self) -> Dict[str, Any]:
        """获取客户概览"""
        try:
            aql = """
            RETURN {
                total_customers: LENGTH(customers),
                a_grade_customers: LENGTH(
                    FOR c IN customers
                    FILTER c.customer_grade == 'A'
                    RETURN c
                ),
                b_grade_customers: LENGTH(
                    FOR c IN customers
                    FILTER c.customer_grade == 'B'
                    RETURN c
                ),
                c_grade_customers: LENGTH(
                    FOR c IN customers
                    FILTER c.customer_grade == 'C'
                    RETURN c
                ),
                avg_value_score: AVERAGE(
                    FOR c IN customers
                    FILTER c.value_score != null
                    RETURN c.value_score
                )
            }
            """
            
            result = list(self.arango_service.db.aql.execute(aql))[0]
            return result
            
        except Exception as e:
            self.logger.error(f"获取客户概览失败: {str(e)}")
            return {}
    
    def _get_grade_distribution(self) -> List[Dict[str, Any]]:
        """获取客户等级分布"""
        try:
            aql = """
            FOR customer IN customers
                COLLECT grade = customer.customer_grade WITH COUNT INTO count
                RETURN {
                    grade: grade,
                    count: count
                }
            """
            
            return list(self.arango_service.db.aql.execute(aql))
            
        except Exception as e:
            self.logger.error(f"获取客户等级分布失败: {str(e)}")
            return []
    
    def _get_value_score_distribution(self) -> List[Dict[str, Any]]:
        """获取价值评分分布"""
        try:
            aql = """
            FOR customer IN customers
                FILTER customer.value_score != null
                COLLECT score_range = FLOOR(customer.value_score / 10) * 10 WITH COUNT INTO count
                SORT score_range
                RETURN {
                    score_range: CONCAT(TO_STRING(score_range), '-', TO_STRING(score_range + 9)),
                    count: count
                }
            """
            
            return list(self.arango_service.db.aql.execute(aql))
            
        except Exception as e:
            self.logger.error(f"获取价值评分分布失败: {str(e)}")
            return []
    
    def _get_geographic_distribution(self) -> List[Dict[str, Any]]:
        """获取地理分布"""
        try:
            aql = """
            FOR customer IN customers
                COLLECT country = customer.country WITH COUNT INTO count
                SORT count DESC
                RETURN {
                    country: country,
                    count: count
                }
            """
            
            return list(self.arango_service.db.aql.execute(aql))
            
        except Exception as e:
            self.logger.error(f"获取地理分布失败: {str(e)}")
            return []
    
    def _get_industry_distribution(self) -> List[Dict[str, Any]]:
        """获取行业分布"""
        try:
            aql = """
            FOR customer IN customers
                FOR company IN 1..1 OUTBOUND customer belongs_to
                COLLECT industry = company.industry WITH COUNT INTO count
                SORT count DESC
                RETURN {
                    industry: industry,
                    count: count
                }
            """
            
            return list(self.arango_service.db.aql.execute(aql))
            
        except Exception as e:
            self.logger.error(f"获取行业分布失败: {str(e)}")
            return []
    
    def _get_top_customers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取顶级客户"""
        try:
            aql = """
            FOR customer IN customers
                FILTER customer.value_score != null
                SORT customer.value_score DESC
                LIMIT @limit
                RETURN {
                    customer_id: customer._key,
                    name: customer.name,
                    email: customer.email,
                    country: customer.country,
                    value_score: customer.value_score,
                    customer_grade: customer.customer_grade
                }
            """
            
            return list(self.arango_service.db.aql.execute(aql, bind_vars={'limit': limit}))
            
        except Exception as e:
            self.logger.error(f"获取顶级客户失败: {str(e)}")
            return []
    
    def _get_customer_trends(self) -> Dict[str, Any]:
        """获取客户趋势"""
        try:
            # 新客户趋势
            new_customers_aql = """
            FOR customer IN customers
                FILTER DATE_DIFF(customer.created_at, DATE_NOW(), 'day') <= 30
                COLLECT date_group = DATE_FORMAT(customer.created_at, '%Y-%m-%d')
                WITH COUNT INTO count
                SORT date_group
                RETURN {
                    date: date_group,
                    count: count
                }
            """
            
            new_customers = list(self.arango_service.db.aql.execute(new_customers_aql))
            
            # 价值评分趋势
            value_trend_aql = """
            FOR customer IN customers
                FILTER customer.value_updated_at != null
                FILTER DATE_DIFF(customer.value_updated_at, DATE_NOW(), 'day') <= 30
                COLLECT date_group = DATE_FORMAT(customer.value_updated_at, '%Y-%m-%d')
                AGGREGATE avg_score = AVERAGE(customer.value_score)
                SORT date_group
                RETURN {
                    date: date_group,
                    avg_value_score: avg_score
                }
            """
            
            value_trends = list(self.arango_service.db.aql.execute(value_trend_aql))
            
            return {
                'new_customers': new_customers,
                'value_score_trends': value_trends
            }
            
        except Exception as e:
            self.logger.error(f"获取客户趋势失败: {str(e)}")
            return {}