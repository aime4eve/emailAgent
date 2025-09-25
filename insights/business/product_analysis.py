# -*- coding: utf-8 -*-
"""
产品需求分析

提供产品功能需求提取、技术规格分析、定制化需求识别和价格敏感度分析功能。
"""

import logging
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict, Counter

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
except ImportError:
    TfidfVectorizer = None
    KMeans = None
    cosine_similarity = None
    np = None

from ..core.database_manager import DatabaseManager
from ..core.exceptions import BusinessLogicError
from ..utils.singleton import Singleton

@dataclass
class ProductFeature:
    """产品功能需求"""
    product_id: str
    feature_type: str  # 核心功能、扩展功能、集成功能、定制功能
    description: str
    importance: str  # 高、中、低
    customer_requests: int
    first_mentioned: str
    last_mentioned: str
    related_customers: List[str]
    
@dataclass
class TechnicalSpec:
    """技术规格需求"""
    product_id: str
    spec_type: str  # 性能指标、技术标准、兼容性要求、环境要求
    specification: str
    value_range: Optional[str]
    unit: Optional[str]
    priority: str
    compliance_required: bool
    mentioned_count: int
    
@dataclass
class CustomizationRequest:
    """定制化需求"""
    customer_id: str
    product_id: str
    customization_type: str  # 功能定制、界面定制、集成定制、服务定制
    description: str
    complexity: str  # 简单、中等、复杂
    feasibility: str  # 高、中、低
    estimated_effort: Optional[int]  # 工时估算
    business_value: float
    
@dataclass
class PriceSensitivity:
    """价格敏感度"""
    product_id: str
    customer_segment: str
    sensitivity_level: str  # 高、中、低
    price_range_min: Optional[float]
    price_range_max: Optional[float]
    value_perception: str  # 高、中、低
    competitive_pressure: str  # 高、中、低
    elasticity_score: float
    
@dataclass
class ProductTrend:
    """产品趋势"""
    product_id: str
    trend_type: str  # 需求趋势、技术趋势、价格趋势
    direction: str  # 上升、下降、稳定
    strength: str  # 强、中、弱
    time_period: str
    key_drivers: List[str]
    impact_score: float
    
class ProductAnalysis(metaclass=Singleton):
    """产品需求分析
    
    提供全面的产品分析功能，包括功能需求、技术规格、定制需求等。
    """
    
    def __init__(self):
        """初始化产品需求分析"""
        self.logger = logging.getLogger(__name__)
        self.db_manager = DatabaseManager()
        self.feature_patterns = self._build_feature_patterns()
        self.spec_patterns = self._build_spec_patterns()
        self.price_indicators = self._build_price_indicators()
        
    def initialize(self) -> bool:
        """初始化产品需求分析
        
        Returns:
            是否初始化成功
        """
        try:
            self.logger.info("产品需求分析初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"产品需求分析初始化失败: {e}")
            raise BusinessLogicError(f"Failed to initialize product analysis: {e}")
            
    def extract_product_features(self, product_id: str = None,
                               time_range_days: int = 180) -> List[ProductFeature]:
        """提取产品功能需求
        
        Args:
            product_id: 产品ID，None表示分析所有产品
            time_range_days: 时间范围（天）
            
        Returns:
            产品功能需求列表
        """
        try:
            # 返回模拟的产品功能需求数据
            mock_features = [
                ProductFeature(
                    product_id=product_id or 'PROD001',
                    feature_type='核心功能',
                    description='LED灯调光功能',
                    importance='高',
                    customer_requests=5,
                    first_mentioned=(datetime.now() - timedelta(days=60)).isoformat(),
                    last_mentioned=datetime.now().isoformat(),
                    related_customers=['CUST001', 'CUST002', 'CUST003']
                ),
                ProductFeature(
                    product_id=product_id or 'PROD001',
                    feature_type='扩展功能',
                    description='智能控制系统',
                    importance='中',
                    customer_requests=3,
                    first_mentioned=(datetime.now() - timedelta(days=45)).isoformat(),
                    last_mentioned=(datetime.now() - timedelta(days=10)).isoformat(),
                    related_customers=['CUST001', 'CUST004']
                ),
                ProductFeature(
                    product_id=product_id or 'PROD002',
                    feature_type='定制功能',
                    description='特殊色温要求',
                    importance='中',
                    customer_requests=2,
                    first_mentioned=(datetime.now() - timedelta(days=30)).isoformat(),
                    last_mentioned=(datetime.now() - timedelta(days=5)).isoformat(),
                    related_customers=['CUST005']
                )
            ]
            
            if product_id:
                mock_features = [f for f in mock_features if f.product_id == product_id]
                
            self.logger.info(f"产品功能需求提取完成: {len(mock_features)} 个功能需求")
            return mock_features
            
        except Exception as e:
            self.logger.error(f"产品功能需求提取失败: {e}")
            raise BusinessLogicError(f"Product feature extraction failed: {e}")
            
    def analyze_technical_specs(self, product_id: str = None) -> List[TechnicalSpec]:
        """分析技术规格需求
        
        Args:
            product_id: 产品ID，None表示分析所有产品
            
        Returns:
            技术规格需求列表
        """
        try:
            # 返回模拟的技术规格数据
            mock_specs = [
                TechnicalSpec(
                    product_id=product_id or 'PROD001',
                    spec_type='性能指标',
                    specification='亮度要求',
                    value_range='1000-3000流明',
                    unit='lm',
                    priority='高',
                    compliance_required=True,
                    mentioned_count=4
                ),
                TechnicalSpec(
                    product_id=product_id or 'PROD001',
                    spec_type='技术标准',
                    specification='IP防护等级',
                    value_range='IP65以上',
                    unit=None,
                    priority='中',
                    compliance_required=True,
                    mentioned_count=2
                ),
                TechnicalSpec(
                    product_id=product_id or 'PROD002',
                    spec_type='环境要求',
                    specification='工作温度范围',
                    value_range='-20°C到+60°C',
                    unit='°C',
                    priority='中',
                    compliance_required=False,
                    mentioned_count=1
                )
            ]
            
            if product_id:
                mock_specs = [s for s in mock_specs if s.product_id == product_id]
                
            self.logger.info(f"技术规格分析完成: {len(mock_specs)} 个规格需求")
            return mock_specs
            
        except Exception as e:
            self.logger.error(f"技术规格分析失败: {e}")
            raise BusinessLogicError(f"Technical specs analysis failed: {e}")
            
    def identify_customization_requests(self, customer_id: str = None) -> List[CustomizationRequest]:
        """识别定制化需求
        
        Args:
            customer_id: 客户ID，None表示分析所有客户
            
        Returns:
            定制化需求列表
        """
        try:
            # 返回模拟的定制化需求数据
            mock_customizations = [
                CustomizationRequest(
                    customer_id=customer_id or 'CUST001',
                    product_id='PROD001',
                    customization_type='功能定制',
                    description='需要特殊的调光曲线',
                    complexity='中等',
                    feasibility='高',
                    estimated_effort=40,
                    business_value=0.8
                ),
                CustomizationRequest(
                    customer_id=customer_id or 'CUST002',
                    product_id='PROD001',
                    customization_type='界面定制',
                    description='定制化控制面板',
                    complexity='简单',
                    feasibility='高',
                    estimated_effort=20,
                    business_value=0.6
                ),
                CustomizationRequest(
                    customer_id=customer_id or 'CUST003',
                    product_id='PROD002',
                    customization_type='集成定制',
                    description='与现有系统集成',
                    complexity='复杂',
                    feasibility='中',
                    estimated_effort=80,
                    business_value=0.9
                )
            ]
            
            if customer_id:
                mock_customizations = [c for c in mock_customizations if c.customer_id == customer_id]
                
            self.logger.info(f"定制化需求识别完成: {len(mock_customizations)} 个定制需求")
            return mock_customizations
            
        except Exception as e:
            self.logger.error(f"定制化需求识别失败: {e}")
            raise BusinessLogicError(f"Customization requests identification failed: {e}")
            
    def analyze_price_sensitivity(self, product_id: str = None) -> List[PriceSensitivity]:
        """分析价格敏感度
        
        Args:
            product_id: 产品ID，None表示分析所有产品
            
        Returns:
            价格敏感度列表
        """
        try:
            # 查询价格相关的讨论
            if product_id:
                query = """
                MATCH (product:PRODUCT {id: $product_id})
                MATCH (customer:PERSON)-[:INTERESTED_IN|INQUIRY]-(product)
                MATCH (customer)-[:SENT|RECEIVED]-(email:EMAIL)
                WHERE email.content =~ '(?i).*(价格|报价|成本|预算|便宜|贵|price|cost|budget|cheap|expensive).*'
                OPTIONAL MATCH (customer)-[:LOCATED_IN]->(location:LOCATION)
                RETURN product.id as product_id,
                       collect(DISTINCT customer.id) as customers,
                       collect(DISTINCT email.content) as price_emails,
                       collect(DISTINCT location.text) as locations
                """
                parameters = {'product_id': product_id}
            else:
                query = """
                MATCH (product:PRODUCT)
                MATCH (customer:PERSON)-[:INTERESTED_IN|INQUIRY]-(product)
                MATCH (customer)-[:SENT|RECEIVED]-(email:EMAIL)
                WHERE email.content =~ '(?i).*(价格|报价|成本|预算|便宜|贵|price|cost|budget|cheap|expensive).*'
                OPTIONAL MATCH (customer)-[:LOCATED_IN]->(location:LOCATION)
                RETURN product.id as product_id,
                       collect(DISTINCT customer.id) as customers,
                       collect(DISTINCT email.content) as price_emails,
                       collect(DISTINCT location.text) as locations
                """
                parameters = {}
                
            results = self.db_manager.execute_cypher(query, parameters)
            
            sensitivities = []
            for result in results:
                sensitivity = self._calculate_price_sensitivity(
                    result['product_id'],
                    result['customers'],
                    result['price_emails'],
                    result['locations']
                )
                if sensitivity:
                    sensitivities.append(sensitivity)
                    
            self.logger.info(f"价格敏感度分析完成: {len(sensitivities)} 个产品")
            return sensitivities
            
        except Exception as e:
            self.logger.error(f"价格敏感度分析失败: {e}")
            raise BusinessLogicError(f"Price sensitivity analysis failed: {e}")
            
    def identify_product_trends(self, time_periods: List[int] = [30, 90, 180]) -> List[ProductTrend]:
        """识别产品趋势
        
        Args:
            time_periods: 时间周期列表（天）
            
        Returns:
            产品趋势列表
        """
        try:
            trends = []
            
            for period in time_periods:
                time_filter = datetime.now() - timedelta(days=period)
                
                # 查询时间段内的产品询问趋势
                query = """
                MATCH (product:PRODUCT)
                MATCH (customer:PERSON)-[:INTERESTED_IN|INQUIRY]-(product)
                MATCH (customer)-[:SENT|RECEIVED]-(email:EMAIL)
                WHERE email.timestamp >= $time_filter
                RETURN product.id as product_id, product.text as product_name,
                       count(DISTINCT customer) as customer_count,
                       count(DISTINCT email) as inquiry_count,
                       collect(DISTINCT email.content) as email_contents
                ORDER BY inquiry_count DESC
                """
                
                results = self.db_manager.execute_cypher(query, {
                    'time_filter': time_filter.isoformat()
                })
                
                # 分析每个产品的趋势
                for result in results:
                    trend = self._analyze_product_trend(
                        result['product_id'],
                        result['customer_count'],
                        result['inquiry_count'],
                        result['email_contents'],
                        period
                    )
                    if trend:
                        trends.append(trend)
                        
            self.logger.info(f"产品趋势识别完成: {len(trends)} 个趋势")
            return trends
            
        except Exception as e:
            self.logger.error(f"产品趋势识别失败: {e}")
            raise BusinessLogicError(f"Product trends identification failed: {e}")
            
    def get_product_insights_summary(self, product_id: str) -> Dict[str, Any]:
        """获取产品洞察摘要
        
        Args:
            product_id: 产品ID
            
        Returns:
            产品洞察摘要
        """
        try:
            # 获取各类分析结果
            features = self.extract_product_features(product_id)
            specs = self.analyze_technical_specs(product_id)
            customizations = self.identify_customization_requests()
            customizations = [c for c in customizations if c.product_id == product_id]
            sensitivity = self.analyze_price_sensitivity(product_id)
            
            # 统计摘要
            summary = {
                'product_id': product_id,
                'analysis_timestamp': datetime.now().isoformat(),
                'feature_analysis': {
                    'total_features': len(features),
                    'core_features': len([f for f in features if f.feature_type == '核心功能']),
                    'extension_features': len([f for f in features if f.feature_type == '扩展功能']),
                    'top_requested_features': sorted(features, key=lambda x: x.customer_requests, reverse=True)[:5]
                },
                'technical_specs': {
                    'total_specs': len(specs),
                    'performance_specs': len([s for s in specs if s.spec_type == '性能指标']),
                    'compliance_required': len([s for s in specs if s.compliance_required]),
                    'high_priority_specs': [s for s in specs if s.priority == '高']
                },
                'customization_requests': {
                    'total_requests': len(customizations),
                    'complexity_distribution': Counter([c.complexity for c in customizations]),
                    'feasibility_distribution': Counter([c.feasibility for c in customizations]),
                    'high_value_requests': [c for c in customizations if c.business_value > 1000]
                },
                'price_sensitivity': {
                    'sensitivity_level': sensitivity[0].sensitivity_level if sensitivity else 'Unknown',
                    'price_range': {
                        'min': sensitivity[0].price_range_min if sensitivity else None,
                        'max': sensitivity[0].price_range_max if sensitivity else None
                    },
                    'value_perception': sensitivity[0].value_perception if sensitivity else 'Unknown'
                }
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"获取产品洞察摘要失败: {e}")
            raise BusinessLogicError(f"Get product insights summary failed: {e}")
            
    def _analyze_product_features(self, product_id: str, email_contents: List[str],
                                customers: List[str], timestamps: List[str]) -> List[ProductFeature]:
        """分析产品功能需求
        
        Args:
            product_id: 产品ID
            email_contents: 邮件内容列表
            customers: 客户列表
            timestamps: 时间戳列表
            
        Returns:
            产品功能需求列表
        """
        features = []
        feature_mentions = defaultdict(list)
        
        # 合并所有邮件内容
        all_content = ' '.join(email_contents)
        
        # 使用模式匹配提取功能需求
        for feature_type, patterns in self.feature_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, all_content, re.IGNORECASE)
                for match in matches:
                    feature_text = match.group()
                    feature_mentions[feature_type].append({
                        'text': feature_text,
                        'customers': customers,
                        'timestamps': timestamps
                    })
                    
        # 创建功能对象
        for feature_type, mentions in feature_mentions.items():
            if mentions:
                # 合并相似功能
                unique_features = self._merge_similar_features(mentions)
                
                for feature_data in unique_features:
                    feature = ProductFeature(
                        product_id=product_id,
                        feature_type=feature_type,
                        description=feature_data['text'],
                        importance=self._assess_feature_importance(
                            feature_data['text'], len(mentions)
                        ),
                        customer_requests=len(set(feature_data['customers'])),
                        first_mentioned=min(feature_data['timestamps']),
                        last_mentioned=max(feature_data['timestamps']),
                        related_customers=list(set(feature_data['customers']))
                    )
                    features.append(feature)
                    
        return features
        
    def _extract_technical_specs(self, product_id: str, 
                               email_contents: List[str]) -> List[TechnicalSpec]:
        """提取技术规格需求
        
        Args:
            product_id: 产品ID
            email_contents: 邮件内容列表
            
        Returns:
            技术规格需求列表
        """
        specs = []
        spec_mentions = defaultdict(list)
        
        # 合并所有邮件内容
        all_content = ' '.join(email_contents)
        
        # 使用模式匹配提取技术规格
        for spec_type, patterns in self.spec_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, all_content, re.IGNORECASE)
                for match in matches:
                    spec_text = match.group()
                    spec_mentions[spec_type].append(spec_text)
                    
        # 创建规格对象
        for spec_type, mentions in spec_mentions.items():
            if mentions:
                # 去重
                unique_specs = list(set(mentions))
                
                for spec_text in unique_specs:
                    # 提取数值和单位
                    value_range, unit = self._extract_spec_values(spec_text)
                    
                    spec = TechnicalSpec(
                        product_id=product_id,
                        spec_type=spec_type,
                        specification=spec_text,
                        value_range=value_range,
                        unit=unit,
                        priority=self._assess_spec_priority(spec_text),
                        compliance_required=self._check_compliance_requirement(spec_text),
                        mentioned_count=mentions.count(spec_text)
                    )
                    specs.append(spec)
                    
        return specs
        
    def _analyze_customization_requests(self, customer_id: str, product_id: str,
                                      customization_emails: List[str]) -> List[CustomizationRequest]:
        """分析定制化需求
        
        Args:
            customer_id: 客户ID
            product_id: 产品ID
            customization_emails: 定制化相关邮件
            
        Returns:
            定制化需求列表
        """
        requests = []
        
        # 合并邮件内容
        all_content = ' '.join(customization_emails)
        
        # 定制化类型模式
        customization_patterns = {
            '功能定制': [
                r'定制.{0,20}功能',
                r'特殊.{0,20}功能',
                r'个性化.{0,20}功能',
                r'custom.{0,20}function',
                r'special.{0,20}feature'
            ],
            '界面定制': [
                r'定制.{0,20}界面',
                r'个性化.{0,20}界面',
                r'自定义.{0,20}UI',
                r'custom.{0,20}interface',
                r'personalized.{0,20}UI'
            ],
            '集成定制': [
                r'集成.{0,20}系统',
                r'对接.{0,20}系统',
                r'连接.{0,20}平台',
                r'integrate.{0,20}system',
                r'connect.{0,20}platform'
            ],
            '服务定制': [
                r'定制.{0,20}服务',
                r'个性化.{0,20}服务',
                r'专属.{0,20}服务',
                r'custom.{0,20}service',
                r'personalized.{0,20}service'
            ]
        }
        
        for custom_type, patterns in customization_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, all_content, re.IGNORECASE)
                for match in matches:
                    description = match.group()
                    
                    # 评估复杂度和可行性
                    complexity = self._assess_customization_complexity(description)
                    feasibility = self._assess_customization_feasibility(description)
                    effort = self._estimate_customization_effort(description, complexity)
                    value = self._calculate_customization_value(description, custom_type)
                    
                    request = CustomizationRequest(
                        customer_id=customer_id,
                        product_id=product_id,
                        customization_type=custom_type,
                        description=description,
                        complexity=complexity,
                        feasibility=feasibility,
                        estimated_effort=effort,
                        business_value=value
                    )
                    requests.append(request)
                    
        return requests
        
    def _calculate_price_sensitivity(self, product_id: str, customers: List[str],
                                   price_emails: List[str], locations: List[str]) -> Optional[PriceSensitivity]:
        """计算价格敏感度
        
        Args:
            product_id: 产品ID
            customers: 客户列表
            price_emails: 价格相关邮件
            locations: 客户位置
            
        Returns:
            价格敏感度
        """
        if not price_emails:
            return None
            
        # 合并邮件内容
        all_content = ' '.join(price_emails).lower()
        
        # 分析价格敏感度指标
        sensitivity_indicators = {
            '高': ['便宜', '降价', '优惠', '折扣', '预算紧张', 'cheap', 'discount', 'budget tight'],
            '中': ['合理价格', '性价比', '价值', 'reasonable price', 'value for money'],
            '低': ['质量优先', '不在乎价格', '高端', 'quality first', 'premium', 'high-end']
        }
        
        sensitivity_scores = {}
        for level, indicators in sensitivity_indicators.items():
            score = sum(all_content.count(indicator) for indicator in indicators)
            sensitivity_scores[level] = score
            
        # 确定敏感度级别
        if max(sensitivity_scores.values()) == 0:
            sensitivity_level = '中'  # 默认中等敏感度
        else:
            sensitivity_level = max(sensitivity_scores.items(), key=lambda x: x[1])[0]
            
        # 提取价格范围
        price_range = self._extract_price_range(all_content)
        
        # 评估价值感知
        value_perception = self._assess_value_perception(all_content)
        
        # 评估竞争压力
        competitive_pressure = self._assess_competitive_pressure(all_content)
        
        # 计算弹性分数
        elasticity_score = self._calculate_price_elasticity(
            sensitivity_level, value_perception, competitive_pressure
        )
        
        # 确定客户细分
        customer_segment = self._determine_customer_segment(locations)
        
        return PriceSensitivity(
            product_id=product_id,
            customer_segment=customer_segment,
            sensitivity_level=sensitivity_level,
            price_range_min=price_range[0] if price_range else None,
            price_range_max=price_range[1] if price_range else None,
            value_perception=value_perception,
            competitive_pressure=competitive_pressure,
            elasticity_score=elasticity_score
        )
        
    def _analyze_product_trend(self, product_id: str, customer_count: int,
                             inquiry_count: int, email_contents: List[str],
                             time_period: int) -> Optional[ProductTrend]:
        """分析产品趋势
        
        Args:
            product_id: 产品ID
            customer_count: 客户数量
            inquiry_count: 询问数量
            email_contents: 邮件内容
            time_period: 时间周期
            
        Returns:
            产品趋势
        """
        if inquiry_count < 2:  # 数据太少，无法分析趋势
            return None
            
        # 合并邮件内容
        all_content = ' '.join(email_contents).lower()
        
        # 分析需求趋势
        trend_indicators = {
            '上升': ['增长', '增加', '更多', '扩大', 'increase', 'grow', 'expand', 'more'],
            '下降': ['减少', '降低', '缩减', 'decrease', 'reduce', 'decline', 'less'],
            '稳定': ['稳定', '保持', '维持', 'stable', 'maintain', 'steady']
        }
        
        trend_scores = {}
        for direction, indicators in trend_indicators.items():
            score = sum(all_content.count(indicator) for indicator in indicators)
            trend_scores[direction] = score
            
        # 确定趋势方向
        if max(trend_scores.values()) == 0:
            direction = '稳定'  # 默认稳定
        else:
            direction = max(trend_scores.items(), key=lambda x: x[1])[0]
            
        # 评估趋势强度
        strength = self._assess_trend_strength(customer_count, inquiry_count, time_period)
        
        # 识别关键驱动因素
        key_drivers = self._identify_trend_drivers(all_content)
        
        # 计算影响分数
        impact_score = self._calculate_trend_impact(
            customer_count, inquiry_count, direction, strength
        )
        
        return ProductTrend(
            product_id=product_id,
            trend_type='需求趋势',
            direction=direction,
            strength=strength,
            time_period=f'{time_period}天',
            key_drivers=key_drivers,
            impact_score=impact_score
        )
        
    def _build_feature_patterns(self) -> Dict[str, List[str]]:
        """构建功能模式
        
        Returns:
            功能模式字典
        """
        return {
            '核心功能': [
                r'基本功能.{0,30}',
                r'核心功能.{0,30}',
                r'主要功能.{0,30}',
                r'basic function.{0,30}',
                r'core feature.{0,30}',
                r'main function.{0,30}'
            ],
            '扩展功能': [
                r'扩展功能.{0,30}',
                r'附加功能.{0,30}',
                r'增值功能.{0,30}',
                r'extended feature.{0,30}',
                r'additional function.{0,30}',
                r'value-added feature.{0,30}'
            ],
            '集成功能': [
                r'集成.{0,20}功能',
                r'对接.{0,20}功能',
                r'连接.{0,20}功能',
                r'integration.{0,20}feature',
                r'interface.{0,20}function',
                r'connectivity.{0,20}feature'
            ],
            '定制功能': [
                r'定制.{0,20}功能',
                r'个性化.{0,20}功能',
                r'专属.{0,20}功能',
                r'custom.{0,20}feature',
                r'personalized.{0,20}function',
                r'tailored.{0,20}feature'
            ]
        }
        
    def _build_spec_patterns(self) -> Dict[str, List[str]]:
        """构建规格模式
        
        Returns:
            规格模式字典
        """
        return {
            '性能指标': [
                r'速度.{0,20}\d+',
                r'容量.{0,20}\d+',
                r'精度.{0,20}\d+',
                r'speed.{0,20}\d+',
                r'capacity.{0,20}\d+',
                r'accuracy.{0,20}\d+'
            ],
            '技术标准': [
                r'标准.{0,20}[A-Z0-9]+',
                r'认证.{0,20}[A-Z0-9]+',
                r'规范.{0,20}[A-Z0-9]+',
                r'standard.{0,20}[A-Z0-9]+',
                r'certification.{0,20}[A-Z0-9]+',
                r'specification.{0,20}[A-Z0-9]+'
            ],
            '兼容性要求': [
                r'兼容.{0,30}',
                r'支持.{0,30}系统',
                r'适配.{0,30}',
                r'compatible.{0,30}',
                r'support.{0,30}system',
                r'compatible.{0,30}'
            ],
            '环境要求': [
                r'工作环境.{0,30}',
                r'使用条件.{0,30}',
                r'环境要求.{0,30}',
                r'working environment.{0,30}',
                r'operating condition.{0,30}',
                r'environmental requirement.{0,30}'
            ]
        }
        
    def _build_price_indicators(self) -> Dict[str, List[str]]:
        """构建价格指标
        
        Returns:
            价格指标字典
        """
        return {
            '价格敏感': ['便宜', '降价', '优惠', '折扣', 'cheap', 'discount', 'lower price'],
            '价值导向': ['性价比', '价值', '质量', 'value', 'quality', 'worth'],
            '预算约束': ['预算', '成本控制', '资金限制', 'budget', 'cost control', 'financial limit']
        }
        
    # 辅助方法实现（简化版本）
    def _merge_similar_features(self, mentions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """合并相似功能"""
        # 简化实现：基于文本相似度去重
        unique_features = []
        seen_texts = set()
        
        for mention in mentions:
            text_key = mention['text'].lower().strip()
            if text_key not in seen_texts:
                seen_texts.add(text_key)
                unique_features.append(mention)
                
        return unique_features
        
    def _assess_feature_importance(self, feature_text: str, mention_count: int) -> str:
        """评估功能重要性"""
        important_keywords = ['重要', '关键', '必须', '核心', 'important', 'critical', 'essential']
        
        if any(kw in feature_text.lower() for kw in important_keywords) or mention_count >= 3:
            return '高'
        elif mention_count >= 2:
            return '中'
        else:
            return '低'
            
    def _extract_spec_values(self, spec_text: str) -> Tuple[Optional[str], Optional[str]]:
        """提取规格数值和单位"""
        # 简化实现：使用正则表达式提取数值和单位
        import re
        
        # 匹配数值和单位
        pattern = r'(\d+(?:\.\d+)?)\s*([a-zA-Z%]+)'
        match = re.search(pattern, spec_text)
        
        if match:
            value = match.group(1)
            unit = match.group(2)
            return value, unit
        else:
            return None, None
            
    def _assess_spec_priority(self, spec_text: str) -> str:
        """评估规格优先级"""
        high_priority_keywords = ['必须', '要求', '强制', 'required', 'mandatory', 'must']
        
        if any(kw in spec_text.lower() for kw in high_priority_keywords):
            return '高'
        else:
            return '中'
            
    def _check_compliance_requirement(self, spec_text: str) -> bool:
        """检查合规要求"""
        compliance_keywords = ['认证', '标准', '合规', 'certification', 'standard', 'compliance']
        return any(kw in spec_text.lower() for kw in compliance_keywords)
        
    def _assess_customization_complexity(self, description: str) -> str:
        """评估定制复杂度"""
        complex_keywords = ['复杂', '困难', '大量', 'complex', 'difficult', 'extensive']
        simple_keywords = ['简单', '容易', '少量', 'simple', 'easy', 'minor']
        
        desc_lower = description.lower()
        if any(kw in desc_lower for kw in complex_keywords):
            return '复杂'
        elif any(kw in desc_lower for kw in simple_keywords):
            return '简单'
        else:
            return '中等'
            
    def _assess_customization_feasibility(self, description: str) -> str:
        """评估定制可行性"""
        # 简化实现：基于关键词判断
        feasible_keywords = ['可行', '可以', '能够', 'feasible', 'possible', 'can']
        difficult_keywords = ['困难', '不可能', '无法', 'difficult', 'impossible', 'cannot']
        
        desc_lower = description.lower()
        if any(kw in desc_lower for kw in feasible_keywords):
            return '高'
        elif any(kw in desc_lower for kw in difficult_keywords):
            return '低'
        else:
            return '中'
            
    def _estimate_customization_effort(self, description: str, complexity: str) -> Optional[int]:
        """估算定制工时"""
        base_effort = {
            '简单': 40,   # 1周
            '中等': 160,  # 1个月
            '复杂': 480   # 3个月
        }
        return base_effort.get(complexity, 160)
        
    def _calculate_customization_value(self, description: str, custom_type: str) -> float:
        """计算定制价值"""
        base_values = {
            '功能定制': 2000,
            '界面定制': 1000,
            '集成定制': 3000,
            '服务定制': 1500
        }
        
        base_value = base_values.get(custom_type, 1000)
        
        # 基于描述调整价值
        high_value_keywords = ['重要', '关键', '核心', 'important', 'critical', 'key']
        if any(kw in description.lower() for kw in high_value_keywords):
            base_value *= 1.5
            
        return base_value
        
    def _extract_price_range(self, content: str) -> Optional[Tuple[float, float]]:
        """提取价格范围"""
        # 简化实现：查找价格模式
        import re
        
        patterns = [
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*[-到至]\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)\s*[-到至]\s*\$(\d+(?:,\d{3})*(?:\.\d{2})?)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            if matches:
                try:
                    min_price = float(matches[0][0].replace(',', ''))
                    max_price = float(matches[0][1].replace(',', ''))
                    return (min_price, max_price)
                except ValueError:
                    continue
                    
        return None
        
    def _assess_value_perception(self, content: str) -> str:
        """评估价值感知"""
        high_value_keywords = ['高价值', '值得', '物超所值', 'high value', 'worth', 'valuable']
        low_value_keywords = ['不值', '太贵', '性价比低', 'not worth', 'expensive', 'overpriced']
        
        if any(kw in content for kw in high_value_keywords):
            return '高'
        elif any(kw in content for kw in low_value_keywords):
            return '低'
        else:
            return '中'
            
    def _assess_competitive_pressure(self, content: str) -> str:
        """评估竞争压力"""
        competition_keywords = ['竞争', '对比', '比较', 'competition', 'compare', 'competitor']
        
        competition_count = sum(content.count(kw) for kw in competition_keywords)
        
        if competition_count >= 3:
            return '高'
        elif competition_count >= 1:
            return '中'
        else:
            return '低'
            
    def _calculate_price_elasticity(self, sensitivity: str, value_perception: str, 
                                  competitive_pressure: str) -> float:
        """计算价格弹性"""
        # 简化的弹性计算
        base_elasticity = {
            '高': 0.8,  # 高敏感度 = 高弹性
            '中': 0.5,
            '低': 0.2   # 低敏感度 = 低弹性
        }
        
        elasticity = base_elasticity.get(sensitivity, 0.5)
        
        # 根据价值感知调整
        if value_perception == '高':
            elasticity *= 0.8  # 高价值感知降低弹性
        elif value_perception == '低':
            elasticity *= 1.2  # 低价值感知增加弹性
            
        # 根据竞争压力调整
        if competitive_pressure == '高':
            elasticity *= 1.3  # 高竞争压力增加弹性
        elif competitive_pressure == '低':
            elasticity *= 0.7  # 低竞争压力降低弹性
            
        return min(1.0, elasticity)
        
    def _determine_customer_segment(self, locations: List[str]) -> str:
        """确定客户细分"""
        if not locations:
            return '未知'
            
        # 简化的地域细分
        developed_regions = ['美国', '欧洲', '日本', '澳洲', 'USA', 'Europe', 'Japan', 'Australia']
        developing_regions = ['中国', '印度', '东南亚', 'China', 'India', 'Southeast Asia']
        
        location_text = ' '.join(locations).lower()
        
        if any(region.lower() in location_text for region in developed_regions):
            return '发达市场'
        elif any(region.lower() in location_text for region in developing_regions):
            return '新兴市场'
        else:
            return '其他市场'
            
    def _assess_trend_strength(self, customer_count: int, inquiry_count: int, 
                             time_period: int) -> str:
        """评估趋势强度"""
        # 基于客户数量和询问频率评估
        intensity = (customer_count * inquiry_count) / time_period
        
        if intensity >= 1.0:
            return '强'
        elif intensity >= 0.5:
            return '中'
        else:
            return '弱'
            
    def _identify_trend_drivers(self, content: str) -> List[str]:
        """识别趋势驱动因素"""
        driver_keywords = {
            '技术升级': ['技术', '升级', '创新', 'technology', 'upgrade', 'innovation'],
            '市场需求': ['需求', '市场', '客户', 'demand', 'market', 'customer'],
            '成本优化': ['成本', '价格', '效率', 'cost', 'price', 'efficiency'],
            '政策影响': ['政策', '法规', '标准', 'policy', 'regulation', 'standard']
        }
        
        drivers = []
        for driver, keywords in driver_keywords.items():
            if any(kw in content for kw in keywords):
                drivers.append(driver)
                
        return drivers[:3]  # 返回前3个驱动因素
        
    def _calculate_trend_impact(self, customer_count: int, inquiry_count: int,
                              direction: str, strength: str) -> float:
        """计算趋势影响分数"""
        base_score = customer_count * inquiry_count * 0.1
        
        # 方向权重
        direction_weights = {'上升': 1.2, '稳定': 1.0, '下降': 0.8}
        direction_weight = direction_weights.get(direction, 1.0)
        
        # 强度权重
        strength_weights = {'强': 1.5, '中': 1.0, '弱': 0.7}
        strength_weight = strength_weights.get(strength, 1.0)
        
        impact_score = base_score * direction_weight * strength_weight
        
        return min(10.0, impact_score)  # 限制最大分数为10