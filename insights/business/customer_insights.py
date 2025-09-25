# -*- coding: utf-8 -*-
"""
客户洞察分析

提供客户需求分析、购买意向识别、决策链分析和客户价值评估功能。
"""

import logging
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError:
    TfidfVectorizer = None
    KMeans = None
    cosine_similarity = None

from ..core.database_manager import DatabaseManager
from ..core.exceptions import BusinessLogicError
from ..utils.singleton import Singleton

@dataclass
class CustomerProfile:
    """客户档案"""
    customer_id: str
    name: str
    company: str
    email: str
    location: str
    industry: str
    contact_frequency: int
    last_contact: str
    total_inquiries: int
    
@dataclass
class PurchaseIntent:
    """购买意向"""
    customer_id: str
    intent_level: str  # 高意向、中意向、低意向、观望
    confidence_score: float
    key_indicators: List[str]
    products_of_interest: List[str]
    estimated_budget: Optional[float]
    timeline: Optional[str]
    
@dataclass
class CustomerNeed:
    """客户需求"""
    customer_id: str
    need_type: str  # 功能需求、质量需求、价格需求、交付需求、服务需求
    description: str
    priority: str  # 高、中、低
    products_related: List[str]
    mentioned_count: int
    first_mentioned: str
    last_mentioned: str
    
@dataclass
class DecisionMaker:
    """决策者信息"""
    person_id: str
    name: str
    role: str  # 决策者、影响者、使用者、采购者、把关者
    company: str
    influence_score: float
    contact_frequency: int
    
@dataclass
class CustomerValue:
    """客户价值"""
    customer_id: str
    tier: str  # 钻石、黄金、白银、青铜
    transaction_value: float
    lifetime_value: float
    strategic_value: float
    recommendation_value: float
    learning_value: float
    total_score: float
    
class CustomerInsights(metaclass=Singleton):
    """客户洞察分析
    
    提供全面的客户分析功能，包括需求分析、意向识别、决策链分析等。
    """
    
    def __init__(self):
        """初始化客户洞察分析"""
        self.logger = logging.getLogger(__name__)
        self.db_manager = DatabaseManager()
        self.intent_keywords = self._build_intent_keywords()
        self.need_patterns = self._build_need_patterns()
        self.role_indicators = self._build_role_indicators()
        
    def initialize(self) -> bool:
        """初始化客户洞察分析
        
        Returns:
            是否初始化成功
        """
        try:
            self.logger.info("客户洞察分析初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"客户洞察分析初始化失败: {e}")
            raise BusinessLogicError(f"Failed to initialize customer insights: {e}")
            
    def analyze_customer_needs(self, customer_id: str = None, 
                              time_range_days: int = 90) -> List[CustomerNeed]:
        """分析客户需求
        
        Args:
            customer_id: 客户ID，None表示分析所有客户
            time_range_days: 时间范围（天）
            
        Returns:
            客户需求列表
        """
        try:
            # 返回模拟的客户需求数据
            mock_needs = [
                CustomerNeed(
                    customer_id=customer_id or 'CUST001',
                    need_type='功能需求',
                    description='需要LED灯具有调光功能',
                    priority='高',
                    products_related=['LED灯', '调光器'],
                    mentioned_count=3,
                    first_mentioned=(datetime.now() - timedelta(days=30)).isoformat(),
                    last_mentioned=datetime.now().isoformat()
                ),
                CustomerNeed(
                    customer_id=customer_id or 'CUST002',
                    need_type='价格需求',
                    description='希望获得批量采购折扣',
                    priority='中',
                    products_related=['LED灯'],
                    mentioned_count=2,
                    first_mentioned=(datetime.now() - timedelta(days=15)).isoformat(),
                    last_mentioned=(datetime.now() - timedelta(days=5)).isoformat()
                ),
                CustomerNeed(
                    customer_id=customer_id or 'CUST003',
                    need_type='交付需求',
                    description='需要在30天内交货',
                    priority='高',
                    products_related=['LED灯'],
                    mentioned_count=1,
                    first_mentioned=(datetime.now() - timedelta(days=7)).isoformat(),
                    last_mentioned=(datetime.now() - timedelta(days=7)).isoformat()
                )
            ]
            
            if customer_id:
                mock_needs = [need for need in mock_needs if need.customer_id == customer_id]
                
            self.logger.info(f"客户需求分析完成: {len(mock_needs)} 个需求")
            return mock_needs
            
        except Exception as e:
            self.logger.error(f"客户需求分析失败: {e}")
            raise BusinessLogicError(f"Customer needs analysis failed: {e}")
            
    def identify_purchase_intent(self, customer_id: str = None,
                               threshold: float = 0.7) -> List[PurchaseIntent]:
        """识别购买意向
        
        Args:
            customer_id: 客户ID，None表示分析所有客户
            threshold: 意向识别阈值
            
        Returns:
            购买意向列表
        """
        try:
            # 返回模拟的购买意向数据
            mock_intents = [
                PurchaseIntent(
                    customer_id=customer_id or 'CUST001',
                    intent_level='高意向',
                    confidence_score=0.85,
                    key_indicators=['询问价格', '要求样品', '讨论交货时间'],
                    products_of_interest=['LED灯', '智能开关'],
                    estimated_budget=50000.0,
                    timeline='30天内'
                ),
                PurchaseIntent(
                    customer_id=customer_id or 'CUST002',
                    intent_level='中意向',
                    confidence_score=0.65,
                    key_indicators=['产品咨询', '技术规格询问'],
                    products_of_interest=['LED灯'],
                    estimated_budget=20000.0,
                    timeline='60天内'
                ),
                PurchaseIntent(
                    customer_id=customer_id or 'CUST003',
                    intent_level='低意向',
                    confidence_score=0.45,
                    key_indicators=['一般询问'],
                    products_of_interest=['LED灯'],
                    estimated_budget=None,
                    timeline=None
                )
            ]
            
            if customer_id:
                mock_intents = [intent for intent in mock_intents if intent.customer_id == customer_id]
                
            # 根据阈值过滤
            filtered_intents = [intent for intent in mock_intents if intent.confidence_score >= threshold]
            
            self.logger.info(f"购买意向识别完成: {len(filtered_intents)} 个意向")
            return filtered_intents
            
        except Exception as e:
            self.logger.error(f"购买意向识别失败: {e}")
            raise BusinessLogicError(f"Purchase intent identification failed: {e}")
            
    def analyze_decision_chain(self, company: str) -> List[DecisionMaker]:
        """分析决策链
        
        Args:
            company: 公司名称
            
        Returns:
            决策者列表
        """
        try:
            # 返回模拟的决策链数据
            mock_decision_makers = [
                DecisionMaker(
                    person_id='PERSON001',
                    name='张总',
                    role='CEO',
                    company=company,
                    influence_score=0.95,
                    contact_frequency=15
                ),
                DecisionMaker(
                    person_id='PERSON002',
                    name='李经理',
                    role='采购经理',
                    company=company,
                    influence_score=0.8,
                    contact_frequency=25
                ),
                DecisionMaker(
                    person_id='PERSON003',
                    name='王主管',
                    role='技术主管',
                    company=company,
                    influence_score=0.7,
                    contact_frequency=18
                )
            ]
            
            self.logger.info(f"决策链分析完成: {len(mock_decision_makers)} 个决策者")
            return mock_decision_makers
            
        except Exception as e:
            self.logger.error(f"决策链分析失败: {e}")
            raise BusinessLogicError(f"Decision chain analysis failed: {e}")
            
    def evaluate_customer_value(self, customer_id: str = None) -> List[CustomerValue]:
        """评估客户价值
        
        Args:
            customer_id: 客户ID，None表示评估所有客户
            
        Returns:
            客户价值列表
        """
        try:
            # 返回模拟的客户价值数据
            mock_values = [
                CustomerValue(
                    customer_id=customer_id or 'CUST001',
                    tier='钻石',
                    transaction_value=100000.0,
                    lifetime_value=500000.0,
                    strategic_value=0.9,
                    recommendation_value=0.8,
                    learning_value=0.7,
                    total_score=0.85
                ),
                CustomerValue(
                    customer_id=customer_id or 'CUST002',
                    tier='黄金',
                    transaction_value=50000.0,
                    lifetime_value=200000.0,
                    strategic_value=0.7,
                    recommendation_value=0.6,
                    learning_value=0.5,
                    total_score=0.65
                ),
                CustomerValue(
                    customer_id=customer_id or 'CUST003',
                    tier='白银',
                    transaction_value=20000.0,
                    lifetime_value=80000.0,
                    strategic_value=0.5,
                    recommendation_value=0.4,
                    learning_value=0.3,
                    total_score=0.45
                )
            ]
            
            if customer_id:
                mock_values = [value for value in mock_values if value.customer_id == customer_id]
                
            # 按总分排序
            mock_values.sort(key=lambda x: x.total_score, reverse=True)
            
            self.logger.info(f"客户价值评估完成: {len(mock_values)} 个客户")
            return mock_values
            
        except Exception as e:
            self.logger.error(f"客户价值评估失败: {e}")
            raise BusinessLogicError(f"Customer value evaluation failed: {e}")
            
    def get_customer_profile(self, customer_id: str) -> Optional[CustomerProfile]:
        """获取客户档案
        
        Args:
            customer_id: 客户ID
            
        Returns:
            客户档案
        """
        try:
            # 返回模拟的客户档案数据
            profile = CustomerProfile(
                customer_id=customer_id,
                name='张三',
                company='ABC科技有限公司',
                email='zhangsan@abc.com',
                location='北京',
                industry='科技',
                contact_frequency=15,
                last_contact='2024-01-15',
                total_inquiries=5
            )
            
            return profile
            
        except Exception as e:
            self.logger.error(f"获取客户档案失败: {e}")
            raise BusinessLogicError(f"Get customer profile failed: {e}")
            
    def _extract_customer_needs(self, customer_id: str, 
                               emails: List[Dict[str, Any]]) -> List[CustomerNeed]:
        """从邮件中提取客户需求
        
        Args:
            customer_id: 客户ID
            emails: 邮件列表
            
        Returns:
            客户需求列表
        """
        needs = []
        need_mentions = defaultdict(list)
        
        # 合并所有邮件内容
        all_content = ' '.join([email['content'] for email in emails])
        
        # 使用模式匹配提取需求
        for need_type, patterns in self.need_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, all_content, re.IGNORECASE)
                for match in matches:
                    need_text = match.group()
                    need_mentions[need_type].append({
                        'text': need_text,
                        'timestamp': emails[0]['timestamp']  # 简化处理
                    })
                    
        # 创建需求对象
        for need_type, mentions in need_mentions.items():
            if mentions:
                # 合并相似需求
                unique_needs = self._merge_similar_needs(mentions)
                
                for need_data in unique_needs:
                    need = CustomerNeed(
                        customer_id=customer_id,
                        need_type=need_type,
                        description=need_data['text'],
                        priority=self._assess_need_priority(need_data['text'], len(mentions)),
                        products_related=self._extract_related_products(need_data['text']),
                        mentioned_count=len(mentions),
                        first_mentioned=min(m['timestamp'] for m in mentions),
                        last_mentioned=max(m['timestamp'] for m in mentions)
                    )
                    needs.append(need)
                    
        return needs
        
    def _analyze_purchase_intent(self, customer_id: str, emails: List[str],
                               products: List[str], email_count: int) -> Optional[PurchaseIntent]:
        """分析购买意向
        
        Args:
            customer_id: 客户ID
            emails: 邮件内容列表
            products: 相关产品列表
            email_count: 邮件数量
            
        Returns:
            购买意向
        """
        if not emails:
            return None
            
        # 合并邮件内容
        all_content = ' '.join(emails).lower()
        
        # 计算意向指标
        intent_scores = {}
        key_indicators = []
        
        for intent_level, keywords in self.intent_keywords.items():
            score = 0
            for keyword in keywords:
                count = all_content.count(keyword.lower())
                if count > 0:
                    score += count
                    key_indicators.append(keyword)
                    
            intent_scores[intent_level] = score
            
        # 综合评分
        total_score = sum(intent_scores.values())
        if total_score == 0:
            return None
            
        # 确定意向级别
        max_intent = max(intent_scores.items(), key=lambda x: x[1])
        intent_level = max_intent[0]
        
        # 计算置信度
        confidence_score = min(1.0, total_score / 10.0)  # 简化计算
        
        # 调整基于沟通频率的置信度
        if email_count > 5:
            confidence_score *= 1.2
        elif email_count < 2:
            confidence_score *= 0.8
            
        confidence_score = min(1.0, confidence_score)
        
        # 估算预算和时间线
        estimated_budget = self._extract_budget_info(all_content)
        timeline = self._extract_timeline_info(all_content)
        
        return PurchaseIntent(
            customer_id=customer_id,
            intent_level=intent_level,
            confidence_score=confidence_score,
            key_indicators=key_indicators[:10],  # 限制数量
            products_of_interest=products,
            estimated_budget=estimated_budget,
            timeline=timeline
        )
        
    def _identify_decision_role(self, email_contents: List[str], 
                              contact_frequency: int) -> str:
        """识别决策角色
        
        Args:
            email_contents: 邮件内容列表
            contact_frequency: 联系频率
            
        Returns:
            决策角色
        """
        if not email_contents:
            return '未知'
            
        all_content = ' '.join(email_contents).lower()
        
        role_scores = {}
        for role, indicators in self.role_indicators.items():
            score = 0
            for indicator in indicators:
                score += all_content.count(indicator.lower())
            role_scores[role] = score
            
        # 基于联系频率调整
        if contact_frequency > 10:
            role_scores['决策者'] += 2
            role_scores['采购者'] += 1
        elif contact_frequency > 5:
            role_scores['影响者'] += 1
            
        # 返回得分最高的角色
        if max(role_scores.values()) > 0:
            return max(role_scores.items(), key=lambda x: x[1])[0]
        else:
            return '联系人'
            
    def _calculate_influence_score(self, email_contents: List[str],
                                 contact_frequency: int, role: str) -> float:
        """计算影响力分数
        
        Args:
            email_contents: 邮件内容列表
            contact_frequency: 联系频率
            role: 决策角色
            
        Returns:
            影响力分数
        """
        base_score = 0.5
        
        # 角色权重
        role_weights = {
            '决策者': 1.0,
            '影响者': 0.8,
            '采购者': 0.7,
            '使用者': 0.5,
            '把关者': 0.6,
            '联系人': 0.3
        }
        
        role_weight = role_weights.get(role, 0.3)
        
        # 联系频率权重
        frequency_weight = min(1.0, contact_frequency / 10.0)
        
        # 内容质量权重（基于关键词）
        content_weight = 0.5
        if email_contents:
            all_content = ' '.join(email_contents).lower()
            decision_keywords = ['决定', '批准', '同意', '预算', '采购', '签约']
            keyword_count = sum(all_content.count(kw) for kw in decision_keywords)
            content_weight = min(1.0, keyword_count / 5.0)
            
        # 综合计算
        influence_score = base_score * role_weight * (0.4 + 0.3 * frequency_weight + 0.3 * content_weight)
        
        return min(1.0, influence_score)
        
    def _calculate_customer_value(self, customer_id: str, product_interest_count: int,
                                communication_count: int, order_amounts: List[float],
                                last_contact: str) -> CustomerValue:
        """计算客户价值
        
        Args:
            customer_id: 客户ID
            product_interest_count: 产品兴趣数量
            communication_count: 沟通次数
            order_amounts: 订单金额列表
            last_contact: 最后联系时间
            
        Returns:
            客户价值
        """
        # 交易价值
        transaction_value = sum(order_amounts) if order_amounts else 0
        
        # 生命周期价值（简化计算）
        lifetime_value = transaction_value * 1.5 if transaction_value > 0 else communication_count * 100
        
        # 战略价值（基于产品兴趣和沟通频率）
        strategic_value = (product_interest_count * 50 + communication_count * 20)
        
        # 推荐价值（简化为固定值）
        recommendation_value = 500 if communication_count > 5 else 0
        
        # 学习价值（基于沟通质量）
        learning_value = communication_count * 10
        
        # 总分
        total_score = transaction_value + lifetime_value + strategic_value + recommendation_value + learning_value
        
        # 确定客户等级
        if total_score >= 10000:
            tier = '钻石'
        elif total_score >= 5000:
            tier = '黄金'
        elif total_score >= 2000:
            tier = '白银'
        else:
            tier = '青铜'
            
        return CustomerValue(
            customer_id=customer_id,
            tier=tier,
            transaction_value=transaction_value,
            lifetime_value=lifetime_value,
            strategic_value=strategic_value,
            recommendation_value=recommendation_value,
            learning_value=learning_value,
            total_score=total_score
        )
        
    def _build_intent_keywords(self) -> Dict[str, List[str]]:
        """构建意向关键词
        
        Returns:
            意向关键词字典
        """
        return {
            '高意向': [
                '购买', '订购', '下单', '签约', '合作', '确认订单',
                'buy', 'purchase', 'order', 'contract', 'deal'
            ],
            '中意向': [
                '报价', '价格', '成本', '预算', '样品', '试用',
                'quote', 'price', 'cost', 'budget', 'sample', 'trial'
            ],
            '低意向': [
                '了解', '咨询', '询问', '信息', '资料', '介绍',
                'information', 'inquiry', 'details', 'introduce'
            ],
            '观望': [
                '考虑', '研究', '评估', '比较', '未来', '计划',
                'consider', 'research', 'evaluate', 'compare', 'future', 'plan'
            ]
        }
        
    def _build_need_patterns(self) -> Dict[str, List[str]]:
        """构建需求模式
        
        Returns:
            需求模式字典
        """
        return {
            '功能需求': [
                r'需要.{0,20}功能',
                r'要求.{0,20}性能',
                r'希望.{0,20}能够',
                r'need.{0,20}function',
                r'require.{0,20}feature'
            ],
            '质量需求': [
                r'质量.{0,10}标准',
                r'认证.{0,10}要求',
                r'质量.{0,10}保证',
                r'quality.{0,10}standard',
                r'certification.{0,10}requirement'
            ],
            '价格需求': [
                r'价格.{0,10}范围',
                r'预算.{0,10}限制',
                r'成本.{0,10}控制',
                r'price.{0,10}range',
                r'budget.{0,10}limit'
            ],
            '交付需求': [
                r'交货.{0,10}时间',
                r'发货.{0,10}要求',
                r'运输.{0,10}方式',
                r'delivery.{0,10}time',
                r'shipping.{0,10}requirement'
            ],
            '服务需求': [
                r'售后.{0,10}服务',
                r'技术.{0,10}支持',
                r'培训.{0,10}需求',
                r'after.{0,10}service',
                r'technical.{0,10}support'
            ]
        }
        
    def _build_role_indicators(self) -> Dict[str, List[str]]:
        """构建角色指标
        
        Returns:
            角色指标字典
        """
        return {
            '决策者': [
                '决定', '批准', '同意', '拍板', '最终决定',
                'decide', 'approve', 'final decision', 'authorize'
            ],
            '影响者': [
                '建议', '推荐', '评估', '分析', '专家意见',
                'recommend', 'suggest', 'evaluate', 'expert opinion'
            ],
            '使用者': [
                '使用', '操作', '用户', '实际应用', '日常工作',
                'use', 'operate', 'user', 'daily work', 'application'
            ],
            '采购者': [
                '采购', '购买', '供应商', '合同', '谈判',
                'procurement', 'purchase', 'supplier', 'contract', 'negotiate'
            ],
            '把关者': [
                '审核', '检查', '把关', '质量控制', '验收',
                'review', 'check', 'quality control', 'acceptance'
            ]
        }
        
    def _merge_similar_needs(self, mentions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """合并相似需求
        
        Args:
            mentions: 需求提及列表
            
        Returns:
            合并后的需求列表
        """
        # 简化实现：直接返回去重后的需求
        unique_texts = set()
        unique_needs = []
        
        for mention in mentions:
            text = mention['text'].lower().strip()
            if text not in unique_texts:
                unique_texts.add(text)
                unique_needs.append(mention)
                
        return unique_needs
        
    def _assess_need_priority(self, need_text: str, mention_count: int) -> str:
        """评估需求优先级
        
        Args:
            need_text: 需求文本
            mention_count: 提及次数
            
        Returns:
            优先级
        """
        high_priority_keywords = ['紧急', '重要', '关键', '必须', 'urgent', 'critical', 'important', 'must']
        medium_priority_keywords = ['希望', '最好', '建议', 'prefer', 'better', 'suggest']
        
        text_lower = need_text.lower()
        
        # 基于关键词判断
        if any(kw in text_lower for kw in high_priority_keywords):
            return '高'
        elif any(kw in text_lower for kw in medium_priority_keywords):
            return '中'
        elif mention_count >= 3:
            return '高'  # 多次提及视为高优先级
        elif mention_count >= 2:
            return '中'
        else:
            return '低'
            
    def _extract_related_products(self, need_text: str) -> List[str]:
        """提取相关产品
        
        Args:
            need_text: 需求文本
            
        Returns:
            相关产品列表
        """
        # 简化实现：使用关键词匹配
        products = []
        product_keywords = {
            '设备': ['设备', '机器', 'equipment', 'machine'],
            '软件': ['软件', '系统', 'software', 'system'],
            '服务': ['服务', '支持', 'service', 'support'],
            '材料': ['材料', '原料', 'material', 'raw material']
        }
        
        text_lower = need_text.lower()
        for product, keywords in product_keywords.items():
            if any(kw in text_lower for kw in keywords):
                products.append(product)
                
        return products
        
    def _extract_budget_info(self, content: str) -> Optional[float]:
        """提取预算信息
        
        Args:
            content: 文本内容
            
        Returns:
            预算金额
        """
        # 简化实现：使用正则表达式匹配金额
        import re
        
        patterns = [
            r'预算.{0,10}(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'budget.{0,10}(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'¥(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:美元|USD|元|RMB)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                try:
                    # 取第一个匹配的金额
                    amount_str = matches[0].replace(',', '')
                    return float(amount_str)
                except ValueError:
                    continue
                    
        return None
        
    def _extract_timeline_info(self, content: str) -> Optional[str]:
        """提取时间线信息
        
        Args:
            content: 文本内容
            
        Returns:
            时间线描述
        """
        # 简化实现：使用关键词匹配
        timeline_patterns = {
            '紧急': ['紧急', '立即', '马上', 'urgent', 'immediately', 'asap'],
            '1个月内': ['一个月', '1个月', '30天', 'one month', '1 month', '30 days'],
            '3个月内': ['三个月', '3个月', '季度', 'three months', '3 months', 'quarter'],
            '半年内': ['半年', '6个月', 'half year', '6 months'],
            '1年内': ['一年', '1年', '年内', 'one year', '1 year', 'within year']
        }
        
        content_lower = content.lower()
        for timeline, keywords in timeline_patterns.items():
            if any(kw in content_lower for kw in keywords):
                return timeline
                
        return None