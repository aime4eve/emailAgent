# -*- coding: utf-8 -*-
"""
市场洞察分析模块

提供市场趋势分析、竞争对手分析、机会识别等功能。
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import re
from collections import Counter, defaultdict

from ..core.database_manager import DatabaseManager
from ..core.exceptions import InsightsException, BusinessLogicError
from ..utils.singleton import Singleton
from insights_config import InsightsConfig

@dataclass
class MarketTrend:
    """市场趋势数据类"""
    trend_id: str
    market_segment: str
    trend_type: str  # 'growth', 'decline', 'emerging', 'stable'
    direction: str  # 'up', 'down', 'stable'
    strength: float  # 0-1
    time_period: str
    key_indicators: List[str]
    impact_score: float
    confidence: float
    description: str
    driving_factors: List[str]
    
@dataclass
class CompetitorAnalysis:
    """竞争对手分析数据类"""
    competitor_id: str
    competitor_name: str
    market_share: float
    strengths: List[str]
    weaknesses: List[str]
    product_portfolio: List[str]
    pricing_strategy: str
    competitive_advantage: List[str]
    threat_level: str  # 'high', 'medium', 'low'
    market_position: str
    recent_activities: List[str]
    
@dataclass
class MarketOpportunity:
    """市场机会数据类"""
    opportunity_id: str
    opportunity_type: str  # 'product_gap', 'market_expansion', 'technology_shift'
    market_segment: str
    description: str
    potential_value: float
    feasibility: float  # 0-1
    time_to_market: int  # months
    required_investment: float
    risk_level: str  # 'high', 'medium', 'low'
    success_probability: float
    key_requirements: List[str]
    
@dataclass
class MarketSegment:
    """市场细分数据类"""
    segment_id: str
    segment_name: str
    size: float  # market size
    growth_rate: float
    customer_profile: Dict[str, Any]
    key_needs: List[str]
    price_sensitivity: str  # 'high', 'medium', 'low'
    competition_level: str  # 'high', 'medium', 'low'
    entry_barriers: List[str]
    profitability: float
    
class MarketInsights(metaclass=Singleton):
    """市场洞察分析类
    
    提供市场趋势分析、竞争对手分析、机会识别等功能。
    """
    
    def __init__(self):
        """初始化市场洞察分析"""
        self.logger = logging.getLogger(__name__)
        self.config = InsightsConfig()
        self.db_manager = None
        self.initialized = False
        
        # 市场趋势关键词
        self.trend_keywords = {
            'growth': ['增长', '上升', '扩大', '增加', '提升', '发展', '繁荣'],
            'decline': ['下降', '减少', '萎缩', '衰退', '降低', '缩减', '疲软'],
            'emerging': ['新兴', '崛起', '出现', '兴起', '涌现', '创新', '突破'],
            'stable': ['稳定', '平稳', '持续', '维持', '保持', '均衡', '稳固']
        }
        
        # 竞争分析关键词
        self.competitor_keywords = {
            'strengths': ['优势', '强项', '领先', '专长', '核心竞争力', '优秀'],
            'weaknesses': ['劣势', '弱点', '不足', '缺陷', '短板', '问题'],
            'threats': ['威胁', '挑战', '竞争', '冲击', '压力', '风险']
        }
        
        # 机会识别关键词
        self.opportunity_keywords = {
            'product_gap': ['空白', '缺口', '需求未满足', '市场空间', '产品缺失'],
            'market_expansion': ['扩张', '拓展', '新市场', '增长机会', '市场开发'],
            'technology_shift': ['技术变革', '创新', '数字化', '智能化', '升级']
        }
        
    def initialize(self) -> bool:
        """初始化市场洞察分析
        
        Returns:
            是否初始化成功
        """
        try:
            self.db_manager = DatabaseManager()
            self.initialized = True
            self.logger.info("市场洞察分析初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"市场洞察分析初始化失败: {e}")
            return False
            
    def analyze_market_trends(self, time_periods: List[int] = None) -> List[MarketTrend]:
        """分析市场趋势
        
        Args:
            time_periods: 分析时间段（天数）
            
        Returns:
            市场趋势列表
        """
        if not self.initialized:
            raise BusinessLogicError("市场洞察分析未初始化")
            
        try:
            if time_periods is None:
                time_periods = [30, 90, 180]  # 默认分析30天、90天、180天
                
            trends = []
            
            for period in time_periods:
                # 查询相关邮件数据
                query = """
                MATCH (e:Email)-[:MENTIONS]->(entity)
                WHERE e.timestamp >= datetime() - duration({days: $period})
                WITH entity, count(e) as mention_count, collect(e.content) as contents
                WHERE mention_count >= 3
                RETURN entity.name as entity_name, entity.type as entity_type, 
                       mention_count, contents
                ORDER BY mention_count DESC
                LIMIT 50
                """
                
                results = self.db_manager.execute_cypher_query(
                    query, {'period': period}
                )
                
                for record in results:
                    entity_name = record['entity_name']
                    entity_type = record['entity_type']
                    mention_count = record['mention_count']
                    contents = record['contents']
                    
                    # 分析趋势类型和方向
                    trend_analysis = self._analyze_trend_from_content(
                        contents, entity_name
                    )
                    
                    if trend_analysis:
                        trend = MarketTrend(
                            trend_id=f"{entity_name}_{period}d_{datetime.now().strftime('%Y%m%d')}",
                            market_segment=entity_type or 'general',
                            trend_type=trend_analysis['type'],
                            direction=trend_analysis['direction'],
                            strength=trend_analysis['strength'],
                            time_period=f"{period}天",
                            key_indicators=trend_analysis['indicators'],
                            impact_score=self._calculate_impact_score(
                                mention_count, trend_analysis['strength']
                            ),
                            confidence=trend_analysis['confidence'],
                            description=f"{entity_name}在{period}天内{trend_analysis['description']}",
                            driving_factors=trend_analysis['factors']
                        )
                        trends.append(trend)
                        
            # 按影响分数排序
            trends.sort(key=lambda x: x.impact_score, reverse=True)
            
            self.logger.info(f"分析了{len(trends)}个市场趋势")
            return trends
            
        except Exception as e:
            self.logger.error(f"市场趋势分析失败: {e}")
            raise BusinessLogicError(f"市场趋势分析失败: {e}")
            
    def analyze_competitors(self, competitor_names: List[str] = None) -> List[CompetitorAnalysis]:
        """分析竞争对手
        
        Args:
            competitor_names: 指定的竞争对手名称列表
            
        Returns:
            竞争对手分析列表
        """
        if not self.initialized:
            raise BusinessLogicError("市场洞察分析未初始化")
            
        try:
            competitors = []
            
            # 如果没有指定竞争对手，从图谱中发现
            if not competitor_names:
                competitor_names = self._discover_competitors()
                
            for competitor_name in competitor_names:
                # 查询竞争对手相关信息
                query = """
                MATCH (c:Company {name: $competitor_name})
                OPTIONAL MATCH (c)-[:MENTIONED_IN]->(e:Email)
                OPTIONAL MATCH (c)-[:OFFERS]->(p:Product)
                OPTIONAL MATCH (c)-[:COMPETES_IN]->(m:Market)
                RETURN c, collect(DISTINCT e.content) as emails, 
                       collect(DISTINCT p.name) as products,
                       collect(DISTINCT m.name) as markets
                """
                
                results = self.db_manager.execute_cypher_query(
                    query, {'competitor_name': competitor_name}
                )
                
                if results:
                    record = results[0]
                    company = record['c']
                    emails = record['emails']
                    products = record['products']
                    markets = record['markets']
                    
                    # 分析竞争对手特征
                    analysis = self._analyze_competitor_characteristics(
                        competitor_name, emails, products, markets
                    )
                    
                    competitor = CompetitorAnalysis(
                        competitor_id=company.get('id', competitor_name),
                        competitor_name=competitor_name,
                        market_share=analysis['market_share'],
                        strengths=analysis['strengths'],
                        weaknesses=analysis['weaknesses'],
                        product_portfolio=products,
                        pricing_strategy=analysis['pricing_strategy'],
                        competitive_advantage=analysis['advantages'],
                        threat_level=analysis['threat_level'],
                        market_position=analysis['position'],
                        recent_activities=analysis['activities']
                    )
                    competitors.append(competitor)
                    
            self.logger.info(f"分析了{len(competitors)}个竞争对手")
            return competitors
            
        except Exception as e:
            self.logger.error(f"竞争对手分析失败: {e}")
            raise BusinessLogicError(f"竞争对手分析失败: {e}")
            
    def identify_market_opportunities(self) -> List[MarketOpportunity]:
        """识别市场机会
        
        Returns:
            市场机会列表
        """
        if not self.initialized:
            raise BusinessLogicError("市场洞察分析未初始化")
            
        try:
            opportunities = []
            
            # 查询客户需求和产品缺口
            query = """
            MATCH (c:Customer)-[:HAS_NEED]->(n:Need)
            WHERE NOT EXISTS((p:Product)-[:SATISFIES]->(n))
            WITH n, count(c) as customer_count, collect(c.name) as customers
            WHERE customer_count >= 2
            RETURN n.type as need_type, n.description as description, 
                   customer_count, customers
            ORDER BY customer_count DESC
            LIMIT 20
            """
            
            results = self.db_manager.execute_cypher_query(query)
            
            for record in results:
                need_type = record['need_type']
                description = record['description']
                customer_count = record['customer_count']
                customers = record['customers']
                
                # 评估机会价值
                opportunity_analysis = self._evaluate_opportunity(
                    need_type, description, customer_count, customers
                )
                
                opportunity = MarketOpportunity(
                    opportunity_id=f"opp_{need_type}_{datetime.now().strftime('%Y%m%d')}",
                    opportunity_type='product_gap',
                    market_segment=need_type,
                    description=description,
                    potential_value=opportunity_analysis['value'],
                    feasibility=opportunity_analysis['feasibility'],
                    time_to_market=opportunity_analysis['time_to_market'],
                    required_investment=opportunity_analysis['investment'],
                    risk_level=opportunity_analysis['risk_level'],
                    success_probability=opportunity_analysis['success_prob'],
                    key_requirements=opportunity_analysis['requirements']
                )
                opportunities.append(opportunity)
                
            # 识别市场扩张机会
            expansion_opportunities = self._identify_expansion_opportunities()
            opportunities.extend(expansion_opportunities)
            
            # 识别技术变革机会
            tech_opportunities = self._identify_technology_opportunities()
            opportunities.extend(tech_opportunities)
            
            # 按潜在价值排序
            opportunities.sort(key=lambda x: x.potential_value, reverse=True)
            
            self.logger.info(f"识别了{len(opportunities)}个市场机会")
            return opportunities
            
        except Exception as e:
            self.logger.error(f"市场机会识别失败: {e}")
            raise BusinessLogicError(f"市场机会识别失败: {e}")
            
    def segment_market(self) -> List[MarketSegment]:
        """市场细分分析
        
        Returns:
            市场细分列表
        """
        if not self.initialized:
            raise BusinessLogicError("市场洞察分析未初始化")
            
        try:
            segments = []
            
            # 基于客户特征进行市场细分
            query = """
            MATCH (c:Customer)
            OPTIONAL MATCH (c)-[:INTERESTED_IN]->(p:Product)
            OPTIONAL MATCH (c)-[:HAS_NEED]->(n:Need)
            RETURN c.industry as industry, c.size as company_size, 
                   c.region as region, collect(DISTINCT p.category) as product_interests,
                   collect(DISTINCT n.type) as need_types, count(c) as customer_count
            """
            
            results = self.db_manager.execute_cypher_query(query)
            
            # 聚合相似的客户群体
            segment_groups = defaultdict(list)
            
            for record in results:
                industry = record['industry'] or 'unknown'
                company_size = record['company_size'] or 'unknown'
                region = record['region'] or 'unknown'
                
                segment_key = f"{industry}_{company_size}_{region}"
                segment_groups[segment_key].append(record)
                
            for segment_key, group_records in segment_groups.items():
                if len(group_records) >= 3:  # 至少3个客户才形成细分
                    segment_analysis = self._analyze_market_segment(
                        segment_key, group_records
                    )
                    
                    segment = MarketSegment(
                        segment_id=segment_key,
                        segment_name=segment_analysis['name'],
                        size=segment_analysis['size'],
                        growth_rate=segment_analysis['growth_rate'],
                        customer_profile=segment_analysis['profile'],
                        key_needs=segment_analysis['needs'],
                        price_sensitivity=segment_analysis['price_sensitivity'],
                        competition_level=segment_analysis['competition'],
                        entry_barriers=segment_analysis['barriers'],
                        profitability=segment_analysis['profitability']
                    )
                    segments.append(segment)
                    
            self.logger.info(f"识别了{len(segments)}个市场细分")
            return segments
            
        except Exception as e:
            self.logger.error(f"市场细分分析失败: {e}")
            raise BusinessLogicError(f"市场细分分析失败: {e}")
            
    def _analyze_trend_from_content(self, contents: List[str], entity_name: str) -> Optional[Dict[str, Any]]:
        """从内容中分析趋势
        
        Args:
            contents: 内容列表
            entity_name: 实体名称
            
        Returns:
            趋势分析结果
        """
        try:
            combined_content = ' '.join(contents)
            
            # 统计趋势关键词
            trend_scores = {}
            for trend_type, keywords in self.trend_keywords.items():
                score = sum(combined_content.count(keyword) for keyword in keywords)
                if score > 0:
                    trend_scores[trend_type] = score
                    
            if not trend_scores:
                return None
                
            # 确定主要趋势类型
            main_trend = max(trend_scores.items(), key=lambda x: x[1])
            trend_type = main_trend[0]
            
            # 确定趋势方向
            direction = 'up' if trend_type in ['growth', 'emerging'] else 'down' if trend_type == 'decline' else 'stable'
            
            # 计算强度
            total_mentions = sum(trend_scores.values())
            strength = min(main_trend[1] / max(total_mentions, 1), 1.0)
            
            # 提取关键指标
            indicators = self._extract_trend_indicators(combined_content, entity_name)
            
            # 提取驱动因素
            factors = self._extract_driving_factors(combined_content)
            
            return {
                'type': trend_type,
                'direction': direction,
                'strength': strength,
                'confidence': min(len(contents) / 10, 1.0),
                'indicators': indicators,
                'factors': factors,
                'description': self._generate_trend_description(trend_type, direction, strength)
            }
            
        except Exception as e:
            self.logger.error(f"趋势分析失败: {e}")
            return None
            
    def _calculate_impact_score(self, mention_count: int, strength: float) -> float:
        """计算影响分数
        
        Args:
            mention_count: 提及次数
            strength: 趋势强度
            
        Returns:
            影响分数
        """
        # 归一化提及次数（假设最大值为100）
        normalized_mentions = min(mention_count / 100, 1.0)
        
        # 综合计算影响分数
        impact_score = (normalized_mentions * 0.6 + strength * 0.4) * 100
        
        return round(impact_score, 2)
        
    def _discover_competitors(self) -> List[str]:
        """发现竞争对手
        
        Returns:
            竞争对手名称列表
        """
        try:
            query = """
            MATCH (c:Company)
            WHERE c.type = 'competitor' OR c.name CONTAINS '竞争'
            RETURN c.name as name
            ORDER BY c.mention_count DESC
            LIMIT 10
            """
            
            results = self.db_manager.execute_cypher_query(query)
            return [record['name'] for record in results]
            
        except Exception as e:
            self.logger.error(f"竞争对手发现失败: {e}")
            return []
            
    def _analyze_competitor_characteristics(self, competitor_name: str, emails: List[str], 
                                          products: List[str], markets: List[str]) -> Dict[str, Any]:
        """分析竞争对手特征
        
        Args:
            competitor_name: 竞争对手名称
            emails: 相关邮件内容
            products: 产品列表
            markets: 市场列表
            
        Returns:
            竞争对手特征分析
        """
        try:
            combined_content = ' '.join(emails)
            
            # 分析优势和劣势
            strengths = self._extract_characteristics(combined_content, 'strengths')
            weaknesses = self._extract_characteristics(combined_content, 'weaknesses')
            
            # 评估威胁等级
            threat_level = self._assess_threat_level(combined_content, len(products), len(markets))
            
            # 分析市场地位
            position = self._analyze_market_position(combined_content, len(products))
            
            # 提取最近活动
            activities = self._extract_recent_activities(combined_content)
            
            return {
                'market_share': self._estimate_market_share(combined_content),
                'strengths': strengths,
                'weaknesses': weaknesses,
                'pricing_strategy': self._analyze_pricing_strategy(combined_content),
                'advantages': self._extract_competitive_advantages(combined_content),
                'threat_level': threat_level,
                'position': position,
                'activities': activities
            }
            
        except Exception as e:
            self.logger.error(f"竞争对手特征分析失败: {e}")
            return {
                'market_share': 0.0,
                'strengths': [],
                'weaknesses': [],
                'pricing_strategy': 'unknown',
                'advantages': [],
                'threat_level': 'medium',
                'position': 'unknown',
                'activities': []
            }
            
    def _evaluate_opportunity(self, need_type: str, description: str, 
                            customer_count: int, customers: List[str]) -> Dict[str, Any]:
        """评估机会价值
        
        Args:
            need_type: 需求类型
            description: 描述
            customer_count: 客户数量
            customers: 客户列表
            
        Returns:
            机会评估结果
        """
        try:
            # 基于客户数量和需求类型评估价值
            base_value = customer_count * 10000  # 基础价值
            
            # 根据需求类型调整
            type_multiplier = {
                'technology': 1.5,
                'quality': 1.3,
                'cost': 1.2,
                'service': 1.1,
                'delivery': 1.0
            }.get(need_type, 1.0)
            
            potential_value = base_value * type_multiplier
            
            # 评估可行性
            feasibility = min(customer_count / 10, 1.0)  # 客户越多可行性越高
            
            # 估算上市时间
            complexity_score = len(description.split()) / 10
            time_to_market = max(int(complexity_score * 6), 3)  # 最少3个月
            
            # 估算投资需求
            required_investment = potential_value * 0.3  # 假设投资为潜在价值的30%
            
            # 评估风险等级
            risk_level = 'low' if feasibility > 0.7 else 'medium' if feasibility > 0.4 else 'high'
            
            # 成功概率
            success_probability = feasibility * 0.8  # 基于可行性
            
            return {
                'value': potential_value,
                'feasibility': feasibility,
                'time_to_market': time_to_market,
                'investment': required_investment,
                'risk_level': risk_level,
                'success_prob': success_probability,
                'requirements': self._extract_key_requirements(description)
            }
            
        except Exception as e:
            self.logger.error(f"机会评估失败: {e}")
            return {
                'value': 0.0,
                'feasibility': 0.0,
                'time_to_market': 12,
                'investment': 0.0,
                'risk_level': 'high',
                'success_prob': 0.0,
                'requirements': []
            }
            
    def _identify_expansion_opportunities(self) -> List[MarketOpportunity]:
        """识别市场扩张机会
        
        Returns:
            扩张机会列表
        """
        opportunities = []
        
        try:
            # 查询未开发的地区市场
            query = """
            MATCH (c:Customer)
            WITH c.region as region, count(c) as customer_count
            WHERE customer_count >= 2 AND customer_count <= 5
            RETURN region, customer_count
            ORDER BY customer_count DESC
            """
            
            results = self.db_manager.execute_cypher_query(query)
            
            for record in results:
                region = record['region']
                customer_count = record['customer_count']
                
                if region and region != 'unknown':
                    opportunity = MarketOpportunity(
                        opportunity_id=f"expansion_{region}_{datetime.now().strftime('%Y%m%d')}",
                        opportunity_type='market_expansion',
                        market_segment=region,
                        description=f"在{region}地区扩张市场",
                        potential_value=customer_count * 15000,
                        feasibility=0.6,
                        time_to_market=6,
                        required_investment=customer_count * 5000,
                        risk_level='medium',
                        success_probability=0.7,
                        key_requirements=['本地化', '渠道建设', '市场调研']
                    )
                    opportunities.append(opportunity)
                    
        except Exception as e:
            self.logger.error(f"扩张机会识别失败: {e}")
            
        return opportunities
        
    def _identify_technology_opportunities(self) -> List[MarketOpportunity]:
        """识别技术变革机会
        
        Returns:
            技术机会列表
        """
        opportunities = []
        
        try:
            # 查询技术相关的需求
            query = """
            MATCH (n:Need)
            WHERE n.description CONTAINS '智能' OR n.description CONTAINS '自动' 
                  OR n.description CONTAINS '数字化' OR n.description CONTAINS 'AI'
            WITH n.type as tech_type, count(n) as need_count
            WHERE need_count >= 2
            RETURN tech_type, need_count
            """
            
            results = self.db_manager.execute_cypher_query(query)
            
            for record in results:
                tech_type = record['tech_type']
                need_count = record['need_count']
                
                opportunity = MarketOpportunity(
                    opportunity_id=f"tech_{tech_type}_{datetime.now().strftime('%Y%m%d')}",
                    opportunity_type='technology_shift',
                    market_segment=tech_type,
                    description=f"基于{tech_type}的技术创新机会",
                    potential_value=need_count * 20000,
                    feasibility=0.5,
                    time_to_market=12,
                    required_investment=need_count * 8000,
                    risk_level='high',
                    success_probability=0.6,
                    key_requirements=['技术研发', '人才招聘', '合作伙伴']
                )
                opportunities.append(opportunity)
                
        except Exception as e:
            self.logger.error(f"技术机会识别失败: {e}")
            
        return opportunities
        
    def _analyze_market_segment(self, segment_key: str, group_records: List[Dict]) -> Dict[str, Any]:
        """分析市场细分
        
        Args:
            segment_key: 细分标识
            group_records: 分组记录
            
        Returns:
            细分分析结果
        """
        try:
            total_customers = sum(record['customer_count'] for record in group_records)
            
            # 聚合产品兴趣和需求类型
            all_interests = []
            all_needs = []
            
            for record in group_records:
                all_interests.extend(record['product_interests'])
                all_needs.extend(record['need_types'])
                
            # 统计最常见的兴趣和需求
            top_interests = [item for item, count in Counter(all_interests).most_common(5)]
            top_needs = [item for item, count in Counter(all_needs).most_common(5)]
            
            # 解析细分特征
            parts = segment_key.split('_')
            industry = parts[0] if len(parts) > 0 else 'unknown'
            company_size = parts[1] if len(parts) > 1 else 'unknown'
            region = parts[2] if len(parts) > 2 else 'unknown'
            
            return {
                'name': f"{industry}-{company_size}-{region}",
                'size': total_customers,
                'growth_rate': self._estimate_growth_rate(total_customers),
                'profile': {
                    'industry': industry,
                    'company_size': company_size,
                    'region': region,
                    'interests': top_interests
                },
                'needs': top_needs,
                'price_sensitivity': self._assess_price_sensitivity(company_size),
                'competition': self._assess_competition_level(industry),
                'barriers': self._identify_entry_barriers(industry, region),
                'profitability': self._estimate_profitability(total_customers, industry)
            }
            
        except Exception as e:
            self.logger.error(f"市场细分分析失败: {e}")
            return {
                'name': segment_key,
                'size': 0,
                'growth_rate': 0.0,
                'profile': {},
                'needs': [],
                'price_sensitivity': 'medium',
                'competition': 'medium',
                'barriers': [],
                'profitability': 0.0
            }
            
    def _extract_trend_indicators(self, content: str, entity_name: str) -> List[str]:
        """提取趋势指标"""
        indicators = []
        
        # 查找数字指标
        number_patterns = re.findall(r'\d+(?:\.\d+)?%?', content)
        if number_patterns:
            indicators.extend([f"数值指标: {p}" for p in number_patterns[:3]])
            
        # 查找时间相关的表述
        time_patterns = re.findall(r'(\d+年|\d+月|\d+季度)', content)
        if time_patterns:
            indicators.extend([f"时间周期: {p}" for p in time_patterns[:2]])
            
        return indicators[:5]  # 最多返回5个指标
        
    def _extract_driving_factors(self, content: str) -> List[str]:
        """提取驱动因素"""
        factors = []
        
        # 查找因果关系表述
        causal_patterns = ['由于', '因为', '导致', '促使', '推动', '影响']
        
        for pattern in causal_patterns:
            if pattern in content:
                # 提取包含因果关系的句子
                sentences = content.split('。')
                for sentence in sentences:
                    if pattern in sentence and len(sentence) < 100:
                        factors.append(sentence.strip())
                        if len(factors) >= 3:
                            break
                            
        return factors[:3]  # 最多返回3个因素
        
    def _generate_trend_description(self, trend_type: str, direction: str, strength: float) -> str:
        """生成趋势描述"""
        strength_desc = '强烈' if strength > 0.7 else '明显' if strength > 0.4 else '轻微'
        
        descriptions = {
            'growth': f"呈现{strength_desc}增长趋势",
            'decline': f"呈现{strength_desc}下降趋势",
            'emerging': f"呈现{strength_desc}新兴趋势",
            'stable': f"保持{strength_desc}稳定状态"
        }
        
        return descriptions.get(trend_type, "趋势不明确")
        
    def _extract_characteristics(self, content: str, char_type: str) -> List[str]:
        """提取特征（优势/劣势）"""
        characteristics = []
        keywords = self.competitor_keywords.get(char_type, [])
        
        for keyword in keywords:
            if keyword in content:
                # 提取包含关键词的句子
                sentences = content.split('。')
                for sentence in sentences:
                    if keyword in sentence and len(sentence) < 80:
                        characteristics.append(sentence.strip())
                        if len(characteristics) >= 3:
                            break
                            
        return characteristics[:3]
        
    def _assess_threat_level(self, content: str, product_count: int, market_count: int) -> str:
        """评估威胁等级"""
        threat_score = 0
        
        # 基于产品数量
        threat_score += min(product_count / 5, 1.0) * 30
        
        # 基于市场覆盖
        threat_score += min(market_count / 3, 1.0) * 30
        
        # 基于内容中的威胁关键词
        threat_keywords = self.competitor_keywords['threats']
        threat_mentions = sum(content.count(keyword) for keyword in threat_keywords)
        threat_score += min(threat_mentions / 5, 1.0) * 40
        
        if threat_score > 70:
            return 'high'
        elif threat_score > 40:
            return 'medium'
        else:
            return 'low'
            
    def _analyze_market_position(self, content: str, product_count: int) -> str:
        """分析市场地位"""
        if product_count >= 10:
            return 'leader'
        elif product_count >= 5:
            return 'challenger'
        elif product_count >= 2:
            return 'follower'
        else:
            return 'nicher'
            
    def _extract_recent_activities(self, content: str) -> List[str]:
        """提取最近活动"""
        activities = []
        
        # 查找活动相关的关键词
        activity_keywords = ['发布', '推出', '合作', '收购', '投资', '扩张', '升级']
        
        for keyword in activity_keywords:
            if keyword in content:
                sentences = content.split('。')
                for sentence in sentences:
                    if keyword in sentence and len(sentence) < 100:
                        activities.append(sentence.strip())
                        if len(activities) >= 5:
                            break
                            
        return activities[:5]
        
    def _estimate_market_share(self, content: str) -> float:
        """估算市场份额"""
        # 查找百分比数字
        percentages = re.findall(r'(\d+(?:\.\d+)?)%', content)
        if percentages:
            # 取最大的百分比作为市场份额估算
            return max(float(p) for p in percentages) / 100
        else:
            # 基于提及频率估算
            mention_count = len(content.split())
            return min(mention_count / 1000, 0.3)  # 最大30%
            
    def _analyze_pricing_strategy(self, content: str) -> str:
        """分析定价策略"""
        if any(keyword in content for keyword in ['低价', '便宜', '价格优势']):
            return 'cost_leadership'
        elif any(keyword in content for keyword in ['高端', '优质', '品质']):
            return 'premium'
        elif any(keyword in content for keyword in ['性价比', '平衡']):
            return 'value_based'
        else:
            return 'unknown'
            
    def _extract_competitive_advantages(self, content: str) -> List[str]:
        """提取竞争优势"""
        advantages = []
        advantage_keywords = ['优势', '领先', '专长', '核心竞争力', '独特']
        
        for keyword in advantage_keywords:
            if keyword in content:
                sentences = content.split('。')
                for sentence in sentences:
                    if keyword in sentence and len(sentence) < 80:
                        advantages.append(sentence.strip())
                        if len(advantages) >= 3:
                            break
                            
        return advantages[:3]
        
    def _extract_key_requirements(self, description: str) -> List[str]:
        """提取关键需求"""
        requirements = []
        
        # 基于描述内容提取需求
        if '技术' in description:
            requirements.append('技术开发')
        if '质量' in description:
            requirements.append('质量控制')
        if '服务' in description:
            requirements.append('服务提升')
        if '成本' in description:
            requirements.append('成本优化')
        if '交付' in description:
            requirements.append('交付改进')
            
        return requirements if requirements else ['需求分析']
        
    def _estimate_growth_rate(self, customer_count: int) -> float:
        """估算增长率"""
        # 基于客户数量估算增长潜力
        if customer_count >= 20:
            return 0.15  # 15%
        elif customer_count >= 10:
            return 0.20  # 20%
        elif customer_count >= 5:
            return 0.25  # 25%
        else:
            return 0.30  # 30%
            
    def _assess_price_sensitivity(self, company_size: str) -> str:
        """评估价格敏感度"""
        if company_size in ['large', '大型']:
            return 'low'
        elif company_size in ['medium', '中型']:
            return 'medium'
        else:
            return 'high'
            
    def _assess_competition_level(self, industry: str) -> str:
        """评估竞争水平"""
        high_competition_industries = ['制造', '贸易', '服务', '科技']
        
        if industry in high_competition_industries:
            return 'high'
        else:
            return 'medium'
            
    def _identify_entry_barriers(self, industry: str, region: str) -> List[str]:
        """识别进入壁垒"""
        barriers = []
        
        if industry == '制造':
            barriers.extend(['资本投入', '技术门槛', '规模经济'])
        elif industry == '服务':
            barriers.extend(['品牌认知', '客户关系', '服务网络'])
        elif industry == '科技':
            barriers.extend(['技术专利', '人才竞争', '研发投入'])
            
        if region not in ['国内', '本地']:
            barriers.append('地域限制')
            
        return barriers[:3]
        
    def _estimate_profitability(self, customer_count: int, industry: str) -> float:
        """估算盈利能力"""
        base_profit = customer_count * 1000  # 基础盈利
        
        # 行业调整系数
        industry_multiplier = {
            '制造': 1.2,
            '科技': 1.5,
            '服务': 1.1,
            '贸易': 1.0
        }.get(industry, 1.0)
        
        return base_profit * industry_multiplier