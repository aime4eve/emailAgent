# -*- coding: utf-8 -*-
"""
风险预警系统模块

提供风险识别、评估、预警和监控功能。
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import re
from collections import Counter, defaultdict

from ..core.database_manager import DatabaseManager
from ..core.exceptions import InsightsException, BusinessLogicError
from ..utils.singleton import Singleton
from insights_config import InsightsConfig

class RiskLevel(Enum):
    """风险等级枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RiskCategory(Enum):
    """风险类别枚举"""
    CUSTOMER = "customer"
    MARKET = "market"
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    COMPLIANCE = "compliance"
    REPUTATION = "reputation"
    TECHNOLOGY = "technology"

@dataclass
class RiskFactor:
    """风险因子数据类"""
    factor_id: str
    factor_name: str
    category: RiskCategory
    description: str
    impact_score: float  # 0-100
    probability: float  # 0-1
    detection_time: datetime
    source_data: List[str]
    indicators: List[str]
    
@dataclass
class RiskAssessment:
    """风险评估数据类"""
    risk_id: str
    risk_name: str
    category: RiskCategory
    level: RiskLevel
    overall_score: float  # 0-100
    impact_score: float
    probability_score: float
    factors: List[RiskFactor]
    mitigation_suggestions: List[str]
    monitoring_indicators: List[str]
    assessment_time: datetime
    
@dataclass
class RiskAlert:
    """风险预警数据类"""
    alert_id: str
    risk_id: str
    alert_type: str  # 'threshold', 'trend', 'anomaly'
    severity: RiskLevel
    message: str
    triggered_time: datetime
    affected_entities: List[str]
    recommended_actions: List[str]
    auto_resolved: bool
    
@dataclass
class RiskTrend:
    """风险趋势数据类"""
    trend_id: str
    risk_category: RiskCategory
    trend_direction: str  # 'increasing', 'decreasing', 'stable'
    change_rate: float
    time_period: str
    key_drivers: List[str]
    forecast: Dict[str, float]
    confidence: float
    
class RiskAnalysis(metaclass=Singleton):
    """风险预警系统类
    
    提供风险识别、评估、预警和监控功能。
    """
    
    def __init__(self):
        """初始化风险预警系统"""
        self.logger = logging.getLogger(__name__)
        self.config = InsightsConfig()
        self.db_manager = None
        self.initialized = False
        
        # 风险关键词字典
        self.risk_keywords = {
            RiskCategory.CUSTOMER: {
                'high': ['投诉', '不满', '取消订单', '拒绝付款', '违约', '纠纷'],
                'medium': ['延期', '犹豫', '价格敏感', '竞争对手', '需求变化'],
                'low': ['询问', '比较', '考虑', '评估']
            },
            RiskCategory.MARKET: {
                'high': ['市场萎缩', '需求下降', '激烈竞争', '价格战', '政策变化'],
                'medium': ['市场波动', '竞争加剧', '需求不稳', '价格压力'],
                'low': ['市场变化', '新进入者', '替代产品']
            },
            RiskCategory.FINANCIAL: {
                'high': ['资金短缺', '坏账', '汇率风险', '成本上升', '利润下降'],
                'medium': ['现金流紧张', '应收账款', '成本压力', '汇率波动'],
                'low': ['财务压力', '预算超支', '收入波动']
            },
            RiskCategory.OPERATIONAL: {
                'high': ['供应中断', '质量问题', '交付延误', '生产故障', '人员流失'],
                'medium': ['供应紧张', '质量波动', '交付压力', '产能不足'],
                'low': ['流程问题', '效率下降', '协调困难']
            },
            RiskCategory.COMPLIANCE: {
                'high': ['法规违反', '合规风险', '审计问题', '许可证', '标准不符'],
                'medium': ['合规要求', '标准变化', '认证问题', '审查'],
                'low': ['合规检查', '标准更新', '文档要求']
            },
            RiskCategory.REPUTATION: {
                'high': ['负面新闻', '公关危机', '品牌损害', '客户流失', '信任危机'],
                'medium': ['负面反馈', '声誉影响', '品牌形象', '客户不满'],
                'low': ['形象问题', '口碑影响', '品牌认知']
            },
            RiskCategory.TECHNOLOGY: {
                'high': ['系统故障', '数据泄露', '技术落后', '安全漏洞', '系统崩溃'],
                'medium': ['技术问题', '系统不稳', '安全风险', '升级需求'],
                'low': ['技术更新', '系统维护', '兼容性问题']
            }
        }
        
        # 风险阈值配置
        self.risk_thresholds = {
            'customer_complaint_rate': 0.05,  # 5%
            'order_cancellation_rate': 0.03,  # 3%
            'payment_delay_rate': 0.02,  # 2%
            'quality_issue_rate': 0.01,  # 1%
            'delivery_delay_rate': 0.05,  # 5%
            'customer_satisfaction': 0.8,  # 80%
            'market_share_decline': 0.1,  # 10%
            'cost_increase_rate': 0.15  # 15%
        }
        
    def initialize(self) -> bool:
        """初始化风险预警系统
        
        Returns:
            是否初始化成功
        """
        try:
            self.db_manager = DatabaseManager()
            self.initialized = True
            self.logger.info("风险预警系统初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"风险预警系统初始化失败: {e}")
            return False
            
    def identify_risk_factors(self, time_period: int = 30) -> List[RiskFactor]:
        """识别风险因子
        
        Args:
            time_period: 分析时间段（天数）
            
        Returns:
            风险因子列表
        """
        if not self.initialized:
            raise BusinessLogicError("风险预警系统未初始化")
            
        try:
            risk_factors = []
            
            # 查询最近的邮件数据
            query = """
            MATCH (e:Email)
            WHERE e.timestamp >= datetime() - duration({days: $period})
            RETURN e.content as content, e.sender as sender, 
                   e.timestamp as timestamp, e.subject as subject
            ORDER BY e.timestamp DESC
            LIMIT 1000
            """
            
            results = self.db_manager.execute_cypher_query(
                query, {'period': time_period}
            )
            
            # 按类别分析风险因子
            for category in RiskCategory:
                category_factors = self._analyze_category_risks(
                    category, results, time_period
                )
                risk_factors.extend(category_factors)
                
            # 按影响分数排序
            risk_factors.sort(key=lambda x: x.impact_score, reverse=True)
            
            self.logger.info(f"识别了{len(risk_factors)}个风险因子")
            return risk_factors
            
        except Exception as e:
            self.logger.error(f"风险因子识别失败: {e}")
            raise BusinessLogicError(f"风险因子识别失败: {e}")
            
    def assess_risks(self, risk_factors: List[RiskFactor] = None) -> List[RiskAssessment]:
        """评估风险
        
        Args:
            risk_factors: 风险因子列表，如果为None则重新识别
            
        Returns:
            风险评估列表
        """
        if not self.initialized:
            raise BusinessLogicError("风险预警系统未初始化")
            
        try:
            if risk_factors is None:
                risk_factors = self.identify_risk_factors()
                
            assessments = []
            
            # 按类别分组风险因子
            category_factors = defaultdict(list)
            for factor in risk_factors:
                category_factors[factor.category].append(factor)
                
            # 为每个类别创建风险评估
            for category, factors in category_factors.items():
                if factors:  # 只有存在风险因子的类别才创建评估
                    assessment = self._create_risk_assessment(category, factors)
                    assessments.append(assessment)
                    
            # 按总体分数排序
            assessments.sort(key=lambda x: x.overall_score, reverse=True)
            
            self.logger.info(f"完成了{len(assessments)}个风险评估")
            return assessments
            
        except Exception as e:
            self.logger.error(f"风险评估失败: {e}")
            raise BusinessLogicError(f"风险评估失败: {e}")
            
    def generate_alerts(self, assessments: List[RiskAssessment] = None) -> List[RiskAlert]:
        """生成风险预警
        
        Args:
            assessments: 风险评估列表，如果为None则重新评估
            
        Returns:
            风险预警列表
        """
        if not self.initialized:
            raise BusinessLogicError("风险预警系统未初始化")
            
        try:
            if assessments is None:
                assessments = self.assess_risks()
                
            alerts = []
            
            for assessment in assessments:
                # 基于风险等级生成预警
                if assessment.level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                    alert = self._create_risk_alert(assessment, 'threshold')
                    alerts.append(alert)
                    
                # 检查趋势预警
                trend_alert = self._check_trend_alert(assessment)
                if trend_alert:
                    alerts.append(trend_alert)
                    
                # 检查异常预警
                anomaly_alert = self._check_anomaly_alert(assessment)
                if anomaly_alert:
                    alerts.append(anomaly_alert)
                    
            # 按严重程度排序
            severity_order = {RiskLevel.CRITICAL: 4, RiskLevel.HIGH: 3, 
                            RiskLevel.MEDIUM: 2, RiskLevel.LOW: 1}
            alerts.sort(key=lambda x: severity_order[x.severity], reverse=True)
            
            self.logger.info(f"生成了{len(alerts)}个风险预警")
            return alerts
            
        except Exception as e:
            self.logger.error(f"风险预警生成失败: {e}")
            raise BusinessLogicError(f"风险预警生成失败: {e}")
            
    def analyze_risk_trends(self, time_periods: List[int] = None) -> List[RiskTrend]:
        """分析风险趋势
        
        Args:
            time_periods: 分析时间段列表
            
        Returns:
            风险趋势列表
        """
        if not self.initialized:
            raise BusinessLogicError("风险预警系统未初始化")
            
        try:
            if time_periods is None:
                time_periods = [7, 30, 90]  # 7天、30天、90天
                
            trends = []
            
            for category in RiskCategory:
                category_trends = self._analyze_category_trends(
                    category, time_periods
                )
                trends.extend(category_trends)
                
            self.logger.info(f"分析了{len(trends)}个风险趋势")
            return trends
            
        except Exception as e:
            self.logger.error(f"风险趋势分析失败: {e}")
            raise BusinessLogicError(f"风险趋势分析失败: {e}")
            
    def monitor_risk_indicators(self) -> Dict[str, Any]:
        """监控风险指标
        
        Returns:
            风险指标监控结果
        """
        if not self.initialized:
            raise BusinessLogicError("风险预警系统未初始化")
            
        try:
            indicators = {}
            
            # 客户相关指标
            indicators['customer_metrics'] = self._calculate_customer_risk_metrics()
            
            # 市场相关指标
            indicators['market_metrics'] = self._calculate_market_risk_metrics()
            
            # 财务相关指标
            indicators['financial_metrics'] = self._calculate_financial_risk_metrics()
            
            # 运营相关指标
            indicators['operational_metrics'] = self._calculate_operational_risk_metrics()
            
            # 合规相关指标
            indicators['compliance_metrics'] = self._calculate_compliance_risk_metrics()
            
            # 声誉相关指标
            indicators['reputation_metrics'] = self._calculate_reputation_risk_metrics()
            
            # 技术相关指标
            indicators['technology_metrics'] = self._calculate_technology_risk_metrics()
            
            # 计算综合风险指数
            indicators['overall_risk_index'] = self._calculate_overall_risk_index(indicators)
            
            indicators['monitoring_time'] = datetime.now().isoformat()
            
            self.logger.info("风险指标监控完成")
            return indicators
            
        except Exception as e:
            self.logger.error(f"风险指标监控失败: {e}")
            raise BusinessLogicError(f"风险指标监控失败: {e}")
            
    def _analyze_category_risks(self, category: RiskCategory, 
                              email_data: List[Dict], time_period: int) -> List[RiskFactor]:
        """分析特定类别的风险
        
        Args:
            category: 风险类别
            email_data: 邮件数据
            time_period: 时间段
            
        Returns:
            该类别的风险因子列表
        """
        try:
            factors = []
            keywords = self.risk_keywords.get(category, {})
            
            # 统计各风险等级的关键词出现次数
            risk_counts = {'high': 0, 'medium': 0, 'low': 0}
            risk_sources = {'high': [], 'medium': [], 'low': []}
            
            for email in email_data:
                content = email.get('content', '')
                
                for risk_level, level_keywords in keywords.items():
                    for keyword in level_keywords:
                        if keyword in content:
                            risk_counts[risk_level] += 1
                            risk_sources[risk_level].append({
                                'content': content[:200],  # 截取前200字符
                                'sender': email.get('sender'),
                                'timestamp': email.get('timestamp')
                            })
                            
            # 为每个有风险的等级创建风险因子
            for risk_level, count in risk_counts.items():
                if count > 0:
                    factor = RiskFactor(
                        factor_id=f"{category.value}_{risk_level}_{datetime.now().strftime('%Y%m%d')}",
                        factor_name=f"{category.value.title()}风险-{risk_level.upper()}",
                        category=category,
                        description=f"{category.value}类别中检测到{count}个{risk_level}级别风险信号",
                        impact_score=self._calculate_impact_score(count, risk_level, time_period),
                        probability=self._calculate_probability(count, len(email_data)),
                        detection_time=datetime.now(),
                        source_data=[s['content'] for s in risk_sources[risk_level][:5]],
                        indicators=self._extract_risk_indicators(risk_sources[risk_level])
                    )
                    factors.append(factor)
                    
            return factors
            
        except Exception as e:
            self.logger.error(f"类别风险分析失败: {e}")
            return []
            
    def _calculate_impact_score(self, count: int, risk_level: str, time_period: int) -> float:
        """计算影响分数
        
        Args:
            count: 风险信号数量
            risk_level: 风险等级
            time_period: 时间段
            
        Returns:
            影响分数（0-100）
        """
        # 基础分数
        base_scores = {'high': 80, 'medium': 50, 'low': 20}
        base_score = base_scores.get(risk_level, 20)
        
        # 频率调整
        frequency_factor = min(count / (time_period / 7), 2.0)  # 每周频率
        
        # 时间衰减
        time_factor = max(1.0 - (time_period - 30) / 365, 0.5)  # 时间越长影响越小
        
        impact_score = base_score * frequency_factor * time_factor
        
        return min(impact_score, 100.0)
        
    def _calculate_probability(self, count: int, total_emails: int) -> float:
        """计算概率
        
        Args:
            count: 风险信号数量
            total_emails: 总邮件数量
            
        Returns:
            概率（0-1）
        """
        if total_emails == 0:
            return 0.0
            
        # 基于频率计算概率
        frequency = count / total_emails
        
        # 使用逻辑函数平滑概率
        probability = 2 / (1 + pow(2.718, -10 * frequency)) - 1
        
        return min(max(probability, 0.0), 1.0)
        
    def _extract_risk_indicators(self, sources: List[Dict]) -> List[str]:
        """提取风险指标
        
        Args:
            sources: 风险来源数据
            
        Returns:
            风险指标列表
        """
        indicators = []
        
        for source in sources[:3]:  # 最多取3个来源
            content = source.get('content', '')
            
            # 提取数字指标
            numbers = re.findall(r'\d+(?:\.\d+)?%?', content)
            if numbers:
                indicators.extend([f"数值: {n}" for n in numbers[:2]])
                
            # 提取时间指标
            times = re.findall(r'\d+[天月年]', content)
            if times:
                indicators.extend([f"时间: {t}" for t in times[:2]])
                
        return list(set(indicators))[:5]  # 去重并限制数量
        
    def _create_risk_assessment(self, category: RiskCategory, 
                              factors: List[RiskFactor]) -> RiskAssessment:
        """创建风险评估
        
        Args:
            category: 风险类别
            factors: 风险因子列表
            
        Returns:
            风险评估
        """
        try:
            # 计算综合分数
            total_impact = sum(f.impact_score for f in factors)
            avg_probability = sum(f.probability for f in factors) / len(factors)
            overall_score = (total_impact / len(factors)) * avg_probability
            
            # 确定风险等级
            if overall_score >= 80:
                level = RiskLevel.CRITICAL
            elif overall_score >= 60:
                level = RiskLevel.HIGH
            elif overall_score >= 40:
                level = RiskLevel.MEDIUM
            else:
                level = RiskLevel.LOW
                
            # 生成缓解建议
            mitigation_suggestions = self._generate_mitigation_suggestions(category, level)
            
            # 生成监控指标
            monitoring_indicators = self._generate_monitoring_indicators(category)
            
            assessment = RiskAssessment(
                risk_id=f"{category.value}_assessment_{datetime.now().strftime('%Y%m%d_%H%M')}",
                risk_name=f"{category.value.title()}风险评估",
                category=category,
                level=level,
                overall_score=round(overall_score, 2),
                impact_score=round(total_impact / len(factors), 2),
                probability_score=round(avg_probability, 3),
                factors=factors,
                mitigation_suggestions=mitigation_suggestions,
                monitoring_indicators=monitoring_indicators,
                assessment_time=datetime.now()
            )
            
            return assessment
            
        except Exception as e:
            self.logger.error(f"风险评估创建失败: {e}")
            raise BusinessLogicError(f"风险评估创建失败: {e}")
            
    def _create_risk_alert(self, assessment: RiskAssessment, alert_type: str) -> RiskAlert:
        """创建风险预警
        
        Args:
            assessment: 风险评估
            alert_type: 预警类型
            
        Returns:
            风险预警
        """
        try:
            # 生成预警消息
            message = self._generate_alert_message(assessment, alert_type)
            
            # 提取受影响的实体
            affected_entities = self._extract_affected_entities(assessment)
            
            # 生成推荐行动
            recommended_actions = self._generate_recommended_actions(assessment)
            
            alert = RiskAlert(
                alert_id=f"alert_{assessment.risk_id}_{alert_type}",
                risk_id=assessment.risk_id,
                alert_type=alert_type,
                severity=assessment.level,
                message=message,
                triggered_time=datetime.now(),
                affected_entities=affected_entities,
                recommended_actions=recommended_actions,
                auto_resolved=False
            )
            
            return alert
            
        except Exception as e:
            self.logger.error(f"风险预警创建失败: {e}")
            raise BusinessLogicError(f"风险预警创建失败: {e}")
            
    def _check_trend_alert(self, assessment: RiskAssessment) -> Optional[RiskAlert]:
        """检查趋势预警
        
        Args:
            assessment: 风险评估
            
        Returns:
            趋势预警（如果有）
        """
        try:
            # 查询历史评估数据
            query = """
            MATCH (r:RiskAssessment)
            WHERE r.category = $category AND r.assessment_time >= datetime() - duration({days: 30})
            RETURN r.overall_score as score, r.assessment_time as time
            ORDER BY r.assessment_time DESC
            LIMIT 10
            """
            
            results = self.db_manager.execute_cypher_query(
                query, {'category': assessment.category.value}
            )
            
            if len(results) >= 3:  # 至少需要3个历史数据点
                scores = [r['score'] for r in results]
                
                # 计算趋势
                recent_avg = sum(scores[:3]) / 3
                older_avg = sum(scores[3:6]) / min(3, len(scores[3:6]))
                
                if recent_avg > older_avg * 1.2:  # 增长超过20%
                    return self._create_risk_alert(assessment, 'trend')
                    
            return None
            
        except Exception as e:
            self.logger.error(f"趋势预警检查失败: {e}")
            return None
            
    def _check_anomaly_alert(self, assessment: RiskAssessment) -> Optional[RiskAlert]:
        """检查异常预警
        
        Args:
            assessment: 风险评估
            
        Returns:
            异常预警（如果有）
        """
        try:
            # 检查是否存在异常高的单个风险因子
            max_impact = max(f.impact_score for f in assessment.factors)
            avg_impact = sum(f.impact_score for f in assessment.factors) / len(assessment.factors)
            
            if max_impact > avg_impact * 2:  # 单个因子影响超过平均值2倍
                return self._create_risk_alert(assessment, 'anomaly')
                
            return None
            
        except Exception as e:
            self.logger.error(f"异常预警检查失败: {e}")
            return None
            
    def _analyze_category_trends(self, category: RiskCategory, 
                               time_periods: List[int]) -> List[RiskTrend]:
        """分析类别风险趋势
        
        Args:
            category: 风险类别
            time_periods: 时间段列表
            
        Returns:
            该类别的风险趋势列表
        """
        trends = []
        
        try:
            for period in time_periods:
                # 查询该时间段的风险数据
                current_factors = self._get_period_risk_factors(category, period)
                previous_factors = self._get_period_risk_factors(category, period * 2, period)
                
                if current_factors and previous_factors:
                    # 计算变化率
                    current_score = sum(f.impact_score for f in current_factors) / len(current_factors)
                    previous_score = sum(f.impact_score for f in previous_factors) / len(previous_factors)
                    
                    change_rate = (current_score - previous_score) / previous_score if previous_score > 0 else 0
                    
                    # 确定趋势方向
                    if change_rate > 0.1:
                        direction = 'increasing'
                    elif change_rate < -0.1:
                        direction = 'decreasing'
                    else:
                        direction = 'stable'
                        
                    # 提取关键驱动因素
                    key_drivers = self._extract_trend_drivers(current_factors, previous_factors)
                    
                    # 生成预测
                    forecast = self._generate_risk_forecast(current_score, change_rate)
                    
                    trend = RiskTrend(
                        trend_id=f"{category.value}_trend_{period}d_{datetime.now().strftime('%Y%m%d')}",
                        risk_category=category,
                        trend_direction=direction,
                        change_rate=round(change_rate, 3),
                        time_period=f"{period}天",
                        key_drivers=key_drivers,
                        forecast=forecast,
                        confidence=self._calculate_trend_confidence(len(current_factors), len(previous_factors))
                    )
                    trends.append(trend)
                    
        except Exception as e:
            self.logger.error(f"类别趋势分析失败: {e}")
            
        return trends
        
    def _get_period_risk_factors(self, category: RiskCategory, 
                               period: int, offset: int = 0) -> List[RiskFactor]:
        """获取指定时间段的风险因子
        
        Args:
            category: 风险类别
            period: 时间段长度
            offset: 时间偏移
            
        Returns:
            风险因子列表
        """
        try:
            # 这里简化实现，实际应该从数据库查询历史数据
            # 为了演示，返回模拟数据
            factors = []
            
            # 模拟查询逻辑
            start_date = datetime.now() - timedelta(days=period + offset)
            end_date = datetime.now() - timedelta(days=offset)
            
            # 实际实现中应该查询数据库获取该时间段的风险因子
            # 这里返回空列表作为占位
            
            return factors
            
        except Exception as e:
            self.logger.error(f"获取时间段风险因子失败: {e}")
            return []
            
    def _calculate_customer_risk_metrics(self) -> Dict[str, float]:
        """计算客户风险指标"""
        try:
            metrics = {}
            
            # 客户投诉率
            query_complaints = """
            MATCH (e:Email)
            WHERE e.timestamp >= datetime() - duration({days: 30})
            WITH count(e) as total_emails,
                 count(CASE WHEN e.content CONTAINS '投诉' OR e.content CONTAINS '不满' THEN 1 END) as complaints
            RETURN toFloat(complaints) / total_emails as complaint_rate
            """
            
            result = self.db_manager.execute_cypher_query(query_complaints)
            metrics['complaint_rate'] = result[0]['complaint_rate'] if result else 0.0
            
            # 订单取消率
            query_cancellations = """
            MATCH (o:Order)
            WHERE o.created_date >= datetime() - duration({days: 30})
            WITH count(o) as total_orders,
                 count(CASE WHEN o.status = 'cancelled' THEN 1 END) as cancelled_orders
            RETURN toFloat(cancelled_orders) / total_orders as cancellation_rate
            """
            
            result = self.db_manager.execute_cypher_query(query_cancellations)
            metrics['cancellation_rate'] = result[0]['cancellation_rate'] if result else 0.0
            
            # 付款延迟率
            query_delays = """
            MATCH (p:Payment)
            WHERE p.due_date >= datetime() - duration({days: 30})
            WITH count(p) as total_payments,
                 count(CASE WHEN p.actual_date > p.due_date THEN 1 END) as delayed_payments
            RETURN toFloat(delayed_payments) / total_payments as delay_rate
            """
            
            result = self.db_manager.execute_cypher_query(query_delays)
            metrics['payment_delay_rate'] = result[0]['delay_rate'] if result else 0.0
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"客户风险指标计算失败: {e}")
            return {'complaint_rate': 0.0, 'cancellation_rate': 0.0, 'payment_delay_rate': 0.0}
            
    def _calculate_market_risk_metrics(self) -> Dict[str, float]:
        """计算市场风险指标"""
        try:
            metrics = {}
            
            # 市场份额变化
            query_market_share = """
            MATCH (c:Company {name: 'our_company'})-[:HAS_MARKET_SHARE]->(m:Market)
            RETURN m.current_share as current_share, m.previous_share as previous_share
            """
            
            result = self.db_manager.execute_cypher_query(query_market_share)
            if result:
                current = result[0]['current_share'] or 0
                previous = result[0]['previous_share'] or 0
                metrics['market_share_change'] = (current - previous) / previous if previous > 0 else 0
            else:
                metrics['market_share_change'] = 0.0
                
            # 竞争强度
            query_competition = """
            MATCH (c:Company)
            WHERE c.type = 'competitor'
            RETURN count(c) as competitor_count, avg(c.market_share) as avg_competitor_share
            """
            
            result = self.db_manager.execute_cypher_query(query_competition)
            if result:
                metrics['competition_intensity'] = result[0]['competitor_count'] * result[0]['avg_competitor_share']
            else:
                metrics['competition_intensity'] = 0.0
                
            return metrics
            
        except Exception as e:
            self.logger.error(f"市场风险指标计算失败: {e}")
            return {'market_share_change': 0.0, 'competition_intensity': 0.0}
            
    def _calculate_financial_risk_metrics(self) -> Dict[str, float]:
        """计算财务风险指标"""
        try:
            metrics = {}
            
            # 应收账款周转率
            query_receivables = """
            MATCH (r:Receivable)
            WHERE r.created_date >= datetime() - duration({days: 90})
            RETURN avg(duration.between(r.created_date, coalesce(r.collected_date, datetime())).days) as avg_collection_days
            """
            
            result = self.db_manager.execute_cypher_query(query_receivables)
            metrics['avg_collection_days'] = result[0]['avg_collection_days'] if result else 30.0
            
            # 成本上升率
            query_costs = """
            MATCH (c:Cost)
            WHERE c.date >= datetime() - duration({days: 60})
            WITH c.date as date, sum(c.amount) as daily_cost
            ORDER BY date
            WITH collect(daily_cost) as costs
            RETURN (costs[-1] - costs[0]) / costs[0] as cost_change_rate
            """
            
            result = self.db_manager.execute_cypher_query(query_costs)
            metrics['cost_increase_rate'] = result[0]['cost_change_rate'] if result else 0.0
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"财务风险指标计算失败: {e}")
            return {'avg_collection_days': 30.0, 'cost_increase_rate': 0.0}
            
    def _calculate_operational_risk_metrics(self) -> Dict[str, float]:
        """计算运营风险指标"""
        try:
            metrics = {}
            
            # 质量问题率
            query_quality = """
            MATCH (q:QualityIssue)
            WHERE q.reported_date >= datetime() - duration({days: 30})
            WITH count(q) as quality_issues
            MATCH (p:Product)
            WHERE p.produced_date >= datetime() - duration({days: 30})
            WITH quality_issues, count(p) as total_products
            RETURN toFloat(quality_issues) / total_products as quality_issue_rate
            """
            
            result = self.db_manager.execute_cypher_query(query_quality)
            metrics['quality_issue_rate'] = result[0]['quality_issue_rate'] if result else 0.0
            
            # 交付延迟率
            query_delivery = """
            MATCH (d:Delivery)
            WHERE d.scheduled_date >= datetime() - duration({days: 30})
            WITH count(d) as total_deliveries,
                 count(CASE WHEN d.actual_date > d.scheduled_date THEN 1 END) as delayed_deliveries
            RETURN toFloat(delayed_deliveries) / total_deliveries as delivery_delay_rate
            """
            
            result = self.db_manager.execute_cypher_query(query_delivery)
            metrics['delivery_delay_rate'] = result[0]['delivery_delay_rate'] if result else 0.0
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"运营风险指标计算失败: {e}")
            return {'quality_issue_rate': 0.0, 'delivery_delay_rate': 0.0}
            
    def _calculate_compliance_risk_metrics(self) -> Dict[str, float]:
        """计算合规风险指标"""
        try:
            metrics = {}
            
            # 合规检查通过率
            query_compliance = """
            MATCH (c:ComplianceCheck)
            WHERE c.check_date >= datetime() - duration({days: 90})
            WITH count(c) as total_checks,
                 count(CASE WHEN c.result = 'passed' THEN 1 END) as passed_checks
            RETURN toFloat(passed_checks) / total_checks as compliance_pass_rate
            """
            
            result = self.db_manager.execute_cypher_query(query_compliance)
            metrics['compliance_pass_rate'] = result[0]['compliance_pass_rate'] if result else 1.0
            
            # 证书到期风险
            query_certificates = """
            MATCH (cert:Certificate)
            WHERE cert.expiry_date <= datetime() + duration({days: 90})
            RETURN count(cert) as expiring_certificates
            """
            
            result = self.db_manager.execute_cypher_query(query_certificates)
            metrics['expiring_certificates'] = result[0]['expiring_certificates'] if result else 0
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"合规风险指标计算失败: {e}")
            return {'compliance_pass_rate': 1.0, 'expiring_certificates': 0}
            
    def _calculate_reputation_risk_metrics(self) -> Dict[str, float]:
        """计算声誉风险指标"""
        try:
            metrics = {}
            
            # 负面提及率
            query_sentiment = """
            MATCH (e:Email)
            WHERE e.timestamp >= datetime() - duration({days: 30})
            WITH count(e) as total_emails,
                 count(CASE WHEN e.sentiment = 'negative' THEN 1 END) as negative_emails
            RETURN toFloat(negative_emails) / total_emails as negative_mention_rate
            """
            
            result = self.db_manager.execute_cypher_query(query_sentiment)
            metrics['negative_mention_rate'] = result[0]['negative_mention_rate'] if result else 0.0
            
            # 客户满意度
            query_satisfaction = """
            MATCH (s:Satisfaction)
            WHERE s.survey_date >= datetime() - duration({days: 90})
            RETURN avg(s.score) as avg_satisfaction
            """
            
            result = self.db_manager.execute_cypher_query(query_satisfaction)
            metrics['customer_satisfaction'] = result[0]['avg_satisfaction'] if result else 0.8
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"声誉风险指标计算失败: {e}")
            return {'negative_mention_rate': 0.0, 'customer_satisfaction': 0.8}
            
    def _calculate_technology_risk_metrics(self) -> Dict[str, float]:
        """计算技术风险指标"""
        try:
            metrics = {}
            
            # 系统故障率
            query_incidents = """
            MATCH (i:Incident)
            WHERE i.occurred_date >= datetime() - duration({days: 30})
            WITH count(i) as total_incidents
            RETURN total_incidents as system_incidents
            """
            
            result = self.db_manager.execute_cypher_query(query_incidents)
            metrics['system_incidents'] = result[0]['system_incidents'] if result else 0
            
            # 安全漏洞数量
            query_vulnerabilities = """
            MATCH (v:Vulnerability)
            WHERE v.discovered_date >= datetime() - duration({days: 30}) AND v.status = 'open'
            RETURN count(v) as open_vulnerabilities
            """
            
            result = self.db_manager.execute_cypher_query(query_vulnerabilities)
            metrics['open_vulnerabilities'] = result[0]['open_vulnerabilities'] if result else 0
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"技术风险指标计算失败: {e}")
            return {'system_incidents': 0, 'open_vulnerabilities': 0}
            
    def _calculate_overall_risk_index(self, indicators: Dict[str, Any]) -> float:
        """计算综合风险指数
        
        Args:
            indicators: 各类风险指标
            
        Returns:
            综合风险指数（0-100）
        """
        try:
            risk_score = 0.0
            
            # 客户风险权重：25%
            customer_metrics = indicators.get('customer_metrics', {})
            customer_risk = (
                customer_metrics.get('complaint_rate', 0) * 100 +
                customer_metrics.get('cancellation_rate', 0) * 100 +
                customer_metrics.get('payment_delay_rate', 0) * 100
            ) / 3
            risk_score += customer_risk * 0.25
            
            # 市场风险权重：20%
            market_metrics = indicators.get('market_metrics', {})
            market_risk = abs(market_metrics.get('market_share_change', 0)) * 100
            risk_score += market_risk * 0.20
            
            # 财务风险权重：20%
            financial_metrics = indicators.get('financial_metrics', {})
            financial_risk = (
                min(financial_metrics.get('avg_collection_days', 30) / 90, 1.0) * 100 +
                abs(financial_metrics.get('cost_increase_rate', 0)) * 100
            ) / 2
            risk_score += financial_risk * 0.20
            
            # 运营风险权重：15%
            operational_metrics = indicators.get('operational_metrics', {})
            operational_risk = (
                operational_metrics.get('quality_issue_rate', 0) * 100 +
                operational_metrics.get('delivery_delay_rate', 0) * 100
            ) / 2
            risk_score += operational_risk * 0.15
            
            # 合规风险权重：10%
            compliance_metrics = indicators.get('compliance_metrics', {})
            compliance_risk = (
                (1 - compliance_metrics.get('compliance_pass_rate', 1.0)) * 100 +
                min(compliance_metrics.get('expiring_certificates', 0) / 10, 1.0) * 100
            ) / 2
            risk_score += compliance_risk * 0.10
            
            # 声誉风险权重：5%
            reputation_metrics = indicators.get('reputation_metrics', {})
            reputation_risk = (
                reputation_metrics.get('negative_mention_rate', 0) * 100 +
                (1 - reputation_metrics.get('customer_satisfaction', 0.8)) * 100
            ) / 2
            risk_score += reputation_risk * 0.05
            
            # 技术风险权重：5%
            technology_metrics = indicators.get('technology_metrics', {})
            technology_risk = (
                min(technology_metrics.get('system_incidents', 0) / 10, 1.0) * 100 +
                min(technology_metrics.get('open_vulnerabilities', 0) / 5, 1.0) * 100
            ) / 2
            risk_score += technology_risk * 0.05
            
            return min(risk_score, 100.0)
            
        except Exception as e:
            self.logger.error(f"综合风险指数计算失败: {e}")
            return 50.0  # 默认中等风险
            
    def _generate_mitigation_suggestions(self, category: RiskCategory, 
                                       level: RiskLevel) -> List[str]:
        """生成缓解建议"""
        suggestions_map = {
            RiskCategory.CUSTOMER: {
                RiskLevel.CRITICAL: ['立即联系客户', '启动客户挽留计划', '高层介入处理'],
                RiskLevel.HIGH: ['加强客户沟通', '提供补偿方案', '改进服务流程'],
                RiskLevel.MEDIUM: ['定期客户回访', '优化客户体验', '收集客户反馈'],
                RiskLevel.LOW: ['监控客户满意度', '预防性维护关系']
            },
            RiskCategory.MARKET: {
                RiskLevel.CRITICAL: ['紧急市场策略调整', '启动危机应对计划'],
                RiskLevel.HIGH: ['重新评估市场定位', '加强竞争分析'],
                RiskLevel.MEDIUM: ['优化产品组合', '拓展新市场'],
                RiskLevel.LOW: ['持续市场监控', '保持竞争优势']
            },
            RiskCategory.FINANCIAL: {
                RiskLevel.CRITICAL: ['紧急资金筹措', '启动财务重组'],
                RiskLevel.HIGH: ['加强现金流管理', '优化成本结构'],
                RiskLevel.MEDIUM: ['改进财务控制', '多元化收入来源'],
                RiskLevel.LOW: ['定期财务审查', '预算优化']
            },
            RiskCategory.OPERATIONAL: {
                RiskLevel.CRITICAL: ['停产检查', '紧急流程修复'],
                RiskLevel.HIGH: ['全面质量审查', '供应链优化'],
                RiskLevel.MEDIUM: ['改进操作流程', '员工培训'],
                RiskLevel.LOW: ['定期流程审查', '持续改进']
            },
            RiskCategory.COMPLIANCE: {
                RiskLevel.CRITICAL: ['立即合规整改', '法律咨询'],
                RiskLevel.HIGH: ['加强合规管理', '更新政策程序'],
                RiskLevel.MEDIUM: ['定期合规检查', '员工合规培训'],
                RiskLevel.LOW: ['监控法规变化', '预防性合规']
            },
            RiskCategory.REPUTATION: {
                RiskLevel.CRITICAL: ['危机公关', '媒体应对'],
                RiskLevel.HIGH: ['品牌修复计划', '客户沟通'],
                RiskLevel.MEDIUM: ['改善品牌形象', '加强宣传'],
                RiskLevel.LOW: ['维护品牌声誉', '正面宣传']
            },
            RiskCategory.TECHNOLOGY: {
                RiskLevel.CRITICAL: ['系统紧急修复', '数据备份恢复'],
                RiskLevel.HIGH: ['技术架构升级', '安全加固'],
                RiskLevel.MEDIUM: ['系统优化', '安全培训'],
                RiskLevel.LOW: ['定期维护', '技术监控']
            }
        }
        
        return suggestions_map.get(category, {}).get(level, ['制定应对计划', '加强监控'])
        
    def _generate_monitoring_indicators(self, category: RiskCategory) -> List[str]:
        """生成监控指标"""
        indicators_map = {
            RiskCategory.CUSTOMER: ['客户满意度', '投诉数量', '客户流失率', '订单取消率'],
            RiskCategory.MARKET: ['市场份额', '竞争对手动态', '价格变化', '需求趋势'],
            RiskCategory.FINANCIAL: ['现金流', '应收账款', '成本变化', '利润率'],
            RiskCategory.OPERATIONAL: ['质量指标', '交付准时率', '库存周转', '产能利用率'],
            RiskCategory.COMPLIANCE: ['合规检查结果', '证书有效期', '法规变化', '审计发现'],
            RiskCategory.REPUTATION: ['媒体报道', '客户反馈', '品牌提及', '社交媒体情绪'],
            RiskCategory.TECHNOLOGY: ['系统可用性', '安全事件', '性能指标', '技术债务']
        }
        
        return indicators_map.get(category, ['相关指标监控'])
        
    def _generate_alert_message(self, assessment: RiskAssessment, alert_type: str) -> str:
        """生成预警消息"""
        level_desc = {
            RiskLevel.CRITICAL: '严重',
            RiskLevel.HIGH: '高',
            RiskLevel.MEDIUM: '中等',
            RiskLevel.LOW: '低'
        }
        
        type_desc = {
            'threshold': '阈值',
            'trend': '趋势',
            'anomaly': '异常'
        }
        
        return f"{assessment.category.value.title()}风险达到{level_desc[assessment.level]}级别，" \
               f"触发{type_desc.get(alert_type, '')}预警。风险评分：{assessment.overall_score}"
               
    def _extract_affected_entities(self, assessment: RiskAssessment) -> List[str]:
        """提取受影响的实体"""
        entities = []
        
        for factor in assessment.factors:
            # 从风险因子的源数据中提取实体
            for source in factor.source_data[:2]:  # 最多取2个来源
                # 简单的实体提取（实际应该使用NER）
                words = source.split()
                entities.extend([w for w in words if len(w) > 2 and w.isalpha()][:3])
                
        return list(set(entities))[:5]  # 去重并限制数量
        
    def _generate_recommended_actions(self, assessment: RiskAssessment) -> List[str]:
        """生成推荐行动"""
        actions = []
        
        # 基于风险等级生成通用行动
        if assessment.level == RiskLevel.CRITICAL:
            actions.extend(['立即启动应急响应', '通知高级管理层', '暂停相关业务'])
        elif assessment.level == RiskLevel.HIGH:
            actions.extend(['制定应对计划', '加强监控频率', '准备应急预案'])
        elif assessment.level == RiskLevel.MEDIUM:
            actions.extend(['定期评估', '优化相关流程', '预防性措施'])
        else:
            actions.extend(['持续监控', '定期检查'])
            
        # 添加类别特定的行动
        category_actions = self._generate_mitigation_suggestions(assessment.category, assessment.level)
        actions.extend(category_actions[:2])  # 最多添加2个
        
        return actions[:5]  # 限制总数量
        
    def _extract_trend_drivers(self, current_factors: List[RiskFactor], 
                             previous_factors: List[RiskFactor]) -> List[str]:
        """提取趋势驱动因素"""
        drivers = []
        
        # 比较当前和历史因子，找出变化最大的
        current_impacts = {f.factor_name: f.impact_score for f in current_factors}
        previous_impacts = {f.factor_name: f.impact_score for f in previous_factors}
        
        for factor_name in current_impacts:
            if factor_name in previous_impacts:
                change = current_impacts[factor_name] - previous_impacts[factor_name]
                if abs(change) > 10:  # 变化超过10分
                    direction = '上升' if change > 0 else '下降'
                    drivers.append(f"{factor_name}{direction}")
                    
        return drivers[:3]  # 最多返回3个驱动因素
        
    def _generate_risk_forecast(self, current_score: float, change_rate: float) -> Dict[str, float]:
        """生成风险预测"""
        forecast = {}
        
        # 预测未来7天、30天、90天的风险分数
        for days in [7, 30, 90]:
            # 简单的线性预测（实际应该使用更复杂的模型）
            predicted_score = current_score * (1 + change_rate * days / 30)
            forecast[f"{days}天后"] = min(max(predicted_score, 0), 100)
            
        return forecast
        
    def _calculate_trend_confidence(self, current_count: int, previous_count: int) -> float:
        """计算趋势置信度"""
        # 基于数据点数量计算置信度
        total_points = current_count + previous_count
        
        if total_points >= 10:
            return 0.9
        elif total_points >= 5:
            return 0.7
        elif total_points >= 3:
            return 0.5
        else:
            return 0.3