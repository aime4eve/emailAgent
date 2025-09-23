#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
需求洞察分析系统
实现需求趋势分析、产品优化建议和需求关联分析
"""

from typing import Dict, List, Any, Optional, Tuple
import logging
import statistics
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict, Counter
import re

# 数据分析相关导入
try:
    import pandas as pd
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    from sklearn.decomposition import LatentDirichletAllocation
    from sklearn.metrics.pairwise import cosine_similarity
    import networkx as nx
except ImportError as e:
    logging.warning(f"数据分析库导入失败: {e}")
    pd = None
    np = None
    TfidfVectorizer = None
    KMeans = None
    LatentDirichletAllocation = None
    cosine_similarity = None
    nx = None

# 时间序列分析
try:
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.seasonal import seasonal_decompose
except ImportError as e:
    logging.warning(f"时间序列分析库导入失败: {e}")
    ARIMA = None
    seasonal_decompose = None

from ...shared.database.arango_service import ArangoDBService

@dataclass
class DemandTrend:
    """需求趋势数据"""
    demand_type: str
    trend_direction: str  # 'increasing', 'decreasing', 'stable'
    growth_rate: float
    frequency_data: List[Dict[str, Any]]
    seasonal_pattern: Optional[Dict[str, Any]] = None
    forecast: Optional[List[Dict[str, Any]]] = None

@dataclass
class ProductOptimizationSuggestion:
    """产品优化建议"""
    product_category: str
    suggestion_type: str  # 'improvement', 'new_product', 'positioning'
    priority: int  # 1-5
    description: str
    supporting_data: Dict[str, Any]
    expected_impact: str
    implementation_difficulty: str  # 'low', 'medium', 'high'

@dataclass
class DemandAssociation:
    """需求关联规则"""
    antecedent: List[str]  # 前置需求
    consequent: List[str]  # 后续需求
    support: float  # 支持度
    confidence: float  # 置信度
    lift: float  # 提升度
    rule_strength: str  # 'strong', 'medium', 'weak'

class DemandInsightsService:
    """需求洞察分析服务"""
    
    def __init__(self, arango_service: ArangoDBService):
        """
        初始化需求洞察分析服务
        
        Args:
            arango_service: ArangoDB数据库服务
        """
        self.arango_service = arango_service
        self.logger = logging.getLogger(__name__)
        
        # 需求关键词映射
        self.demand_keywords = {
            'price': ['price', 'cost', 'cheap', 'expensive', 'budget', 'affordable'],
            'quality': ['quality', 'grade', 'standard', 'durable', 'reliable'],
            'performance': ['performance', 'speed', 'efficiency', 'power', 'capacity'],
            'appearance': ['design', 'appearance', 'color', 'style', 'beautiful'],
            'material': ['material', 'steel', 'aluminum', 'plastic', 'wood'],
            'certification': ['certificate', 'certification', 'standard', 'compliance'],
            'delivery': ['delivery', 'shipping', 'lead time', 'fast', 'urgent'],
            'moq': ['moq', 'minimum', 'quantity', 'order', 'batch']
        }
    
    def analyze_demand_trends(self, days: int = 90) -> Dict[str, Any]:
        """
        分析需求趋势
        
        Args:
            days: 分析天数
            
        Returns:
            需求趋势分析结果
        """
        try:
            self.logger.info(f"开始分析 {days} 天内的需求趋势")
            
            # 1. 数据收集和预处理
            demand_data = self._collect_demand_data(days)
            
            # 2. 关键词提取和主题建模
            keywords_analysis = self._extract_keywords_and_topics(demand_data)
            
            # 3. 时间序列分析
            time_series_analysis = self._analyze_time_series(demand_data, days)
            
            # 4. 地域和行业对比分析
            regional_analysis = self._analyze_regional_differences(demand_data)
            industry_analysis = self._analyze_industry_patterns(demand_data)
            
            # 5. 结果可视化和报告生成
            insights_report = {
                'analysis_period': f'{days} days',
                'total_demands': len(demand_data),
                'keywords_analysis': keywords_analysis,
                'time_series_analysis': time_series_analysis,
                'regional_analysis': regional_analysis,
                'industry_analysis': industry_analysis,
                'trend_summary': self._generate_trend_summary(time_series_analysis),
                'generated_at': datetime.now().isoformat()
            }
            
            self.logger.info("需求趋势分析完成")
            return insights_report
            
        except Exception as e:
            self.logger.error(f"需求趋势分析失败: {str(e)}")
            return {}
    
    def generate_product_optimization_suggestions(self) -> List[ProductOptimizationSuggestion]:
        """
        生成产品优化建议
        
        Returns:
            产品优化建议列表
        """
        try:
            self.logger.info("开始生成产品优化建议")
            
            suggestions = []
            
            # 1. 需求频率统计分析
            demand_frequency = self._analyze_demand_frequency()
            
            # 2. 产品改进方向识别
            improvement_suggestions = self._identify_improvement_opportunities(demand_frequency)
            suggestions.extend(improvement_suggestions)
            
            # 3. 新产品开发机会评估
            new_product_suggestions = self._identify_new_product_opportunities(demand_frequency)
            suggestions.extend(new_product_suggestions)
            
            # 4. 营销策略制定
            positioning_suggestions = self._generate_positioning_strategies(demand_frequency)
            suggestions.extend(positioning_suggestions)
            
            # 按优先级排序
            suggestions.sort(key=lambda x: x.priority, reverse=True)
            
            self.logger.info(f"生成了 {len(suggestions)} 条产品优化建议")
            return suggestions
            
        except Exception as e:
            self.logger.error(f"生成产品优化建议失败: {str(e)}")
            return []
    
    def analyze_demand_associations(self, min_support: float = 0.1, min_confidence: float = 0.5) -> List[DemandAssociation]:
        """
        分析需求关联规则
        
        Args:
            min_support: 最小支持度
            min_confidence: 最小置信度
            
        Returns:
            需求关联规则列表
        """
        try:
            self.logger.info("开始分析需求关联规则")
            
            # 1. 需求共现模式挖掘
            cooccurrence_data = self._mine_demand_cooccurrence()
            
            # 2. 依赖关系分析
            dependency_analysis = self._analyze_demand_dependencies()
            
            # 3. 客户需求演进路径追踪
            evolution_patterns = self._track_demand_evolution_patterns()
            
            # 4. 关联规则生成和验证
            association_rules = self._generate_association_rules(
                cooccurrence_data, min_support, min_confidence
            )
            
            # 5. 规则质量评估
            validated_rules = self._validate_association_rules(association_rules)
            
            self.logger.info(f"发现 {len(validated_rules)} 条有效的需求关联规则")
            return validated_rules
            
        except Exception as e:
            self.logger.error(f"需求关联分析失败: {str(e)}")
            return []
    
    def get_demand_insights_dashboard(self) -> Dict[str, Any]:
        """
        获取需求洞察仪表板数据
        
        Returns:
            仪表板数据
        """
        try:
            dashboard_data = {
                'overview': self._get_demand_overview(),
                'hot_demands': self._get_hot_demands(),
                'trend_analysis': self._get_trend_summary(),
                'regional_insights': self._get_regional_insights(),
                'product_opportunities': self._get_product_opportunities(),
                'association_insights': self._get_association_insights()
            }
            
            self.logger.info("需求洞察仪表板数据获取完成")
            return dashboard_data
            
        except Exception as e:
            self.logger.error(f"获取需求洞察仪表板数据失败: {str(e)}")
            return {}
    
    # 私有方法实现
    
    def _collect_demand_data(self, days: int) -> List[Dict[str, Any]]:
        """收集需求数据"""
        try:
            aql = """
            FOR inquiry IN inquiries
                FILTER DATE_DIFF(inquiry.created_at, DATE_NOW(), 'day') <= @days
                FOR demand IN 1..1 OUTBOUND inquiry expresses
                    FOR customer IN 1..1 OUTBOUND inquiry comes_from
                    RETURN {
                        demand_id: demand._key,
                        demand_type: demand.type,
                        demand_description: demand.description,
                        keywords: demand.keywords,
                        inquiry_date: inquiry.created_at,
                        customer_country: customer.country,
                        customer_region: customer.region,
                        company_industry: (
                            FOR company IN 1..1 OUTBOUND customer belongs_to
                            RETURN company.industry
                        )[0],
                        urgency: inquiry.urgency,
                        purchase_intent: inquiry.purchase_intent
                    }
            """
            
            return list(self.arango_service.db.aql.execute(aql, bind_vars={'days': days}))
            
        except Exception as e:
            self.logger.error(f"收集需求数据失败: {str(e)}")
            return []
    
    def _extract_keywords_and_topics(self, demand_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """提取关键词和主题"""
        try:
            if not demand_data:
                return {}
            
            # 合并所有需求描述
            descriptions = [d.get('demand_description', '') for d in demand_data if d.get('demand_description')]
            
            if not descriptions:
                return {}
            
            # TF-IDF关键词提取
            keywords_analysis = self._extract_tfidf_keywords(descriptions)
            
            # 主题建模
            topics_analysis = self._perform_topic_modeling(descriptions)
            
            # 词云数据
            word_cloud_data = self._generate_word_cloud_data(descriptions)
            
            return {
                'top_keywords': keywords_analysis,
                'topics': topics_analysis,
                'word_cloud': word_cloud_data,
                'total_descriptions': len(descriptions)
            }
            
        except Exception as e:
            self.logger.error(f"关键词和主题提取失败: {str(e)}")
            return {}
    
    def _extract_tfidf_keywords(self, descriptions: List[str], top_k: int = 20) -> List[Dict[str, Any]]:
        """使用TF-IDF提取关键词"""
        try:
            if not TfidfVectorizer:
                return self._extract_simple_keywords(descriptions, top_k)
            
            # 文本预处理
            cleaned_descriptions = [self._clean_text(desc) for desc in descriptions]
            
            # TF-IDF向量化
            vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=2
            )
            
            tfidf_matrix = vectorizer.fit_transform(cleaned_descriptions)
            feature_names = vectorizer.get_feature_names_out()
            
            # 计算平均TF-IDF分数
            mean_scores = np.mean(tfidf_matrix.toarray(), axis=0)
            
            # 获取top-k关键词
            top_indices = np.argsort(mean_scores)[::-1][:top_k]
            
            keywords = []
            for idx in top_indices:
                keywords.append({
                    'keyword': feature_names[idx],
                    'score': float(mean_scores[idx]),
                    'frequency': int(np.sum(tfidf_matrix[:, idx] > 0))
                })
            
            return keywords
            
        except Exception as e:
            self.logger.error(f"TF-IDF关键词提取失败: {str(e)}")
            return self._extract_simple_keywords(descriptions, top_k)
    
    def _extract_simple_keywords(self, descriptions: List[str], top_k: int = 20) -> List[Dict[str, Any]]:
        """简单关键词提取"""
        try:
            # 统计词频
            word_counts = Counter()
            
            for desc in descriptions:
                words = re.findall(r'\b\w+\b', desc.lower())
                # 过滤停用词和短词
                filtered_words = [w for w in words if len(w) > 3 and w not in 
                                ['this', 'that', 'with', 'have', 'will', 'from', 'they', 'been']]
                word_counts.update(filtered_words)
            
            # 获取top-k关键词
            top_words = word_counts.most_common(top_k)
            
            keywords = []
            for word, count in top_words:
                keywords.append({
                    'keyword': word,
                    'score': count / len(descriptions),
                    'frequency': count
                })
            
            return keywords
            
        except Exception as e:
            self.logger.error(f"简单关键词提取失败: {str(e)}")
            return []
    
    def _perform_topic_modeling(self, descriptions: List[str], n_topics: int = 5) -> List[Dict[str, Any]]:
        """执行主题建模"""
        try:
            if not LatentDirichletAllocation or not TfidfVectorizer:
                return []
            
            if len(descriptions) < n_topics:
                return []
            
            # 文本预处理和向量化
            cleaned_descriptions = [self._clean_text(desc) for desc in descriptions]
            
            vectorizer = TfidfVectorizer(
                max_features=100,
                stop_words='english',
                min_df=2,
                max_df=0.8
            )
            
            doc_term_matrix = vectorizer.fit_transform(cleaned_descriptions)
            
            # LDA主题建模
            lda = LatentDirichletAllocation(
                n_components=n_topics,
                random_state=42,
                max_iter=10
            )
            
            lda.fit(doc_term_matrix)
            
            # 提取主题
            feature_names = vectorizer.get_feature_names_out()
            topics = []
            
            for topic_idx, topic in enumerate(lda.components_):
                top_words_idx = topic.argsort()[::-1][:10]
                top_words = [feature_names[i] for i in top_words_idx]
                top_weights = [float(topic[i]) for i in top_words_idx]
                
                topics.append({
                    'topic_id': topic_idx,
                    'words': top_words,
                    'weights': top_weights,
                    'coherence': float(np.mean(top_weights))
                })
            
            return topics
            
        except Exception as e:
            self.logger.error(f"主题建模失败: {str(e)}")
            return []
    
    def _generate_word_cloud_data(self, descriptions: List[str]) -> List[Dict[str, Any]]:
        """生成词云数据"""
        try:
            # 统计词频
            word_counts = Counter()
            
            for desc in descriptions:
                words = re.findall(r'\b\w+\b', desc.lower())
                filtered_words = [w for w in words if len(w) > 3]
                word_counts.update(filtered_words)
            
            # 转换为词云格式
            word_cloud_data = []
            for word, count in word_counts.most_common(50):
                word_cloud_data.append({
                    'text': word,
                    'value': count,
                    'weight': count / max(word_counts.values())
                })
            
            return word_cloud_data
            
        except Exception as e:
            self.logger.error(f"生成词云数据失败: {str(e)}")
            return []
    
    def _analyze_time_series(self, demand_data: List[Dict[str, Any]], days: int) -> Dict[str, Any]:
        """时间序列分析"""
        try:
            if not demand_data:
                return {}
            
            # 按日期分组统计
            daily_counts = defaultdict(int)
            demand_type_daily = defaultdict(lambda: defaultdict(int))
            
            for demand in demand_data:
                date_str = demand['inquiry_date'][:10]  # 提取日期部分
                daily_counts[date_str] += 1
                demand_type_daily[demand.get('demand_type', 'unknown')][date_str] += 1
            
            # 生成完整日期序列
            start_date = datetime.now() - timedelta(days=days)
            date_series = []
            count_series = []
            
            for i in range(days):
                date = start_date + timedelta(days=i)
                date_str = date.strftime('%Y-%m-%d')
                date_series.append(date_str)
                count_series.append(daily_counts.get(date_str, 0))
            
            # 趋势分析
            trend_analysis = self._calculate_trend(count_series)
            
            # 季节性分析
            seasonal_analysis = self._analyze_seasonality(count_series) if len(count_series) > 14 else {}
            
            # 预测
            forecast = self._forecast_demand(count_series) if len(count_series) > 7 else []
            
            return {
                'daily_data': [{'date': d, 'count': c} for d, c in zip(date_series, count_series)],
                'trend_analysis': trend_analysis,
                'seasonal_analysis': seasonal_analysis,
                'forecast': forecast,
                'demand_type_trends': self._analyze_demand_type_trends(demand_type_daily, date_series)
            }
            
        except Exception as e:
            self.logger.error(f"时间序列分析失败: {str(e)}")
            return {}
    
    def _calculate_trend(self, data: List[int]) -> Dict[str, Any]:
        """计算趋势"""
        try:
            if len(data) < 2:
                return {'direction': 'stable', 'slope': 0, 'r_squared': 0}
            
            # 简单线性回归
            x = np.arange(len(data))
            y = np.array(data)
            
            # 计算斜率
            slope = np.polyfit(x, y, 1)[0]
            
            # 计算R²
            y_pred = np.polyval(np.polyfit(x, y, 1), x)
            ss_res = np.sum((y - y_pred) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            
            # 判断趋势方向
            if abs(slope) < 0.1:
                direction = 'stable'
            elif slope > 0:
                direction = 'increasing'
            else:
                direction = 'decreasing'
            
            return {
                'direction': direction,
                'slope': float(slope),
                'r_squared': float(r_squared),
                'strength': 'strong' if abs(r_squared) > 0.7 else 'moderate' if abs(r_squared) > 0.3 else 'weak'
            }
            
        except Exception as e:
            self.logger.error(f"趋势计算失败: {str(e)}")
            return {'direction': 'stable', 'slope': 0, 'r_squared': 0}
    
    def _analyze_seasonality(self, data: List[int]) -> Dict[str, Any]:
        """分析季节性"""
        try:
            if not seasonal_decompose or len(data) < 14:
                return {}
            
            # 使用statsmodels进行季节性分解
            ts = pd.Series(data)
            decomposition = seasonal_decompose(ts, model='additive', period=7)  # 周期为7天
            
            return {
                'has_seasonality': True,
                'seasonal_strength': float(np.std(decomposition.seasonal)),
                'trend_strength': float(np.std(decomposition.trend.dropna())),
                'residual_strength': float(np.std(decomposition.resid.dropna()))
            }
            
        except Exception as e:
            self.logger.error(f"季节性分析失败: {str(e)}")
            return {'has_seasonality': False}
    
    def _forecast_demand(self, data: List[int], periods: int = 7) -> List[Dict[str, Any]]:
        """需求预测"""
        try:
            if not ARIMA or len(data) < 10:
                # 简单移动平均预测
                return self._simple_forecast(data, periods)
            
            # ARIMA预测
            ts = pd.Series(data)
            model = ARIMA(ts, order=(1, 1, 1))
            fitted_model = model.fit()
            
            forecast = fitted_model.forecast(steps=periods)
            conf_int = fitted_model.get_forecast(steps=periods).conf_int()
            
            forecast_data = []
            for i in range(periods):
                forecast_data.append({
                    'period': i + 1,
                    'forecast': float(forecast.iloc[i]),
                    'lower_bound': float(conf_int.iloc[i, 0]),
                    'upper_bound': float(conf_int.iloc[i, 1])
                })
            
            return forecast_data
            
        except Exception as e:
            self.logger.error(f"ARIMA预测失败: {str(e)}")
            return self._simple_forecast(data, periods)
    
    def _simple_forecast(self, data: List[int], periods: int = 7) -> List[Dict[str, Any]]:
        """简单预测"""
        try:
            if len(data) < 3:
                avg_value = statistics.mean(data) if data else 0
            else:
                # 使用最近3天的平均值
                avg_value = statistics.mean(data[-3:])
            
            forecast_data = []
            for i in range(periods):
                forecast_data.append({
                    'period': i + 1,
                    'forecast': avg_value,
                    'lower_bound': max(0, avg_value * 0.8),
                    'upper_bound': avg_value * 1.2
                })
            
            return forecast_data
            
        except Exception:
            return []
    
    def _analyze_demand_type_trends(self, demand_type_daily: Dict[str, Dict[str, int]], 
                                  date_series: List[str]) -> List[Dict[str, Any]]:
        """分析需求类型趋势"""
        try:
            trends = []
            
            for demand_type, daily_data in demand_type_daily.items():
                # 生成完整时间序列
                counts = [daily_data.get(date, 0) for date in date_series]
                
                if sum(counts) > 0:  # 只分析有数据的需求类型
                    trend = self._calculate_trend(counts)
                    trends.append({
                        'demand_type': demand_type,
                        'total_count': sum(counts),
                        'trend': trend,
                        'daily_data': [{'date': d, 'count': c} for d, c in zip(date_series, counts)]
                    })
            
            # 按总数排序
            trends.sort(key=lambda x: x['total_count'], reverse=True)
            return trends
            
        except Exception as e:
            self.logger.error(f"需求类型趋势分析失败: {str(e)}")
            return []
    
    def _analyze_regional_differences(self, demand_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析地域需求差异"""
        try:
            regional_stats = defaultdict(lambda: defaultdict(int))
            
            for demand in demand_data:
                country = demand.get('customer_country', 'Unknown')
                demand_type = demand.get('demand_type', 'unknown')
                regional_stats[country][demand_type] += 1
            
            # 计算相似度和差异指数
            regional_analysis = []
            
            for country, demands in regional_stats.items():
                total_demands = sum(demands.values())
                demand_distribution = {k: v/total_demands for k, v in demands.items()}
                
                regional_analysis.append({
                    'country': country,
                    'total_demands': total_demands,
                    'demand_distribution': demand_distribution,
                    'top_demand': max(demands.items(), key=lambda x: x[1])[0] if demands else 'none'
                })
            
            # 按需求总数排序
            regional_analysis.sort(key=lambda x: x['total_demands'], reverse=True)
            
            return {
                'regional_distribution': regional_analysis,
                'total_countries': len(regional_stats),
                'diversity_index': self._calculate_diversity_index(regional_stats)
            }
            
        except Exception as e:
            self.logger.error(f"地域差异分析失败: {str(e)}")
            return {}
    
    def _analyze_industry_patterns(self, demand_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析行业需求模式"""
        try:
            industry_stats = defaultdict(lambda: defaultdict(int))
            
            for demand in demand_data:
                industry = demand.get('company_industry', 'Unknown')
                demand_type = demand.get('demand_type', 'unknown')
                if industry:  # 只统计有行业信息的数据
                    industry_stats[industry][demand_type] += 1
            
            industry_analysis = []
            
            for industry, demands in industry_stats.items():
                total_demands = sum(demands.values())
                demand_distribution = {k: v/total_demands for k, v in demands.items()}
                
                industry_analysis.append({
                    'industry': industry,
                    'total_demands': total_demands,
                    'demand_distribution': demand_distribution,
                    'primary_demand': max(demands.items(), key=lambda x: x[1])[0] if demands else 'none',
                    'demand_diversity': len(demands)
                })
            
            # 按需求总数排序
            industry_analysis.sort(key=lambda x: x['total_demands'], reverse=True)
            
            return {
                'industry_patterns': industry_analysis,
                'total_industries': len(industry_stats)
            }
            
        except Exception as e:
            self.logger.error(f"行业模式分析失败: {str(e)}")
            return {}
    
    def _calculate_diversity_index(self, stats: Dict[str, Dict[str, int]]) -> float:
        """计算多样性指数"""
        try:
            # 使用Shannon多样性指数
            total_count = sum(sum(demands.values()) for demands in stats.values())
            if total_count == 0:
                return 0.0
            
            diversity = 0.0
            for demands in stats.values():
                for count in demands.values():
                    if count > 0:
                        p = count / total_count
                        diversity -= p * np.log(p)
            
            return float(diversity)
            
        except Exception:
            return 0.0
    
    def _generate_trend_summary(self, time_series_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """生成趋势摘要"""
        try:
            trend = time_series_analysis.get('trend_analysis', {})
            forecast = time_series_analysis.get('forecast', [])
            
            summary = {
                'overall_trend': trend.get('direction', 'stable'),
                'trend_strength': trend.get('strength', 'weak'),
                'growth_rate': trend.get('slope', 0),
                'forecast_direction': 'stable'
            }
            
            # 预测趋势
            if forecast and len(forecast) > 1:
                forecast_values = [f['forecast'] for f in forecast]
                if forecast_values[-1] > forecast_values[0]:
                    summary['forecast_direction'] = 'increasing'
                elif forecast_values[-1] < forecast_values[0]:
                    summary['forecast_direction'] = 'decreasing'
            
            return summary
            
        except Exception as e:
            self.logger.error(f"生成趋势摘要失败: {str(e)}")
            return {}
    
    def _analyze_demand_frequency(self) -> Dict[str, Any]:
        """分析需求频率"""
        try:
            aql = """
            FOR demand IN demands
                COLLECT demand_type = demand.type WITH COUNT INTO count
                SORT count DESC
                RETURN {
                    demand_type: demand_type,
                    frequency: count
                }
            """
            
            frequency_data = list(self.arango_service.db.aql.execute(aql))
            
            # 计算需求满足率
            satisfaction_aql = """
            FOR demand IN demands
                COLLECT demand_type = demand.type 
                AGGREGATE avg_satisfaction = AVERAGE(demand.satisfaction_rate)
                RETURN {
                    demand_type: demand_type,
                    avg_satisfaction: avg_satisfaction
                }
            """
            
            satisfaction_data = list(self.arango_service.db.aql.execute(satisfaction_aql))
            satisfaction_map = {item['demand_type']: item['avg_satisfaction'] for item in satisfaction_data}
            
            # 合并数据
            for item in frequency_data:
                item['satisfaction_rate'] = satisfaction_map.get(item['demand_type'], 0.0)
                item['gap_score'] = item['frequency'] * (1 - item['satisfaction_rate'])  # 需求缺口分数
            
            return {
                'frequency_distribution': frequency_data,
                'total_demand_types': len(frequency_data),
                'high_frequency_demands': [item for item in frequency_data if item['frequency'] > 10],
                'high_gap_demands': sorted(frequency_data, key=lambda x: x['gap_score'], reverse=True)[:5]
            }
            
        except Exception as e:
            self.logger.error(f"需求频率分析失败: {str(e)}")
            return {}
    
    def _identify_improvement_opportunities(self, demand_frequency: Dict[str, Any]) -> List[ProductOptimizationSuggestion]:
        """识别产品改进机会"""
        suggestions = []
        
        try:
            high_gap_demands = demand_frequency.get('high_gap_demands', [])
            
            for demand in high_gap_demands[:3]:  # 取前3个高缺口需求
                demand_type = demand['demand_type']
                gap_score = demand['gap_score']
                
                if gap_score > 5:  # 缺口分数阈值
                    suggestion = ProductOptimizationSuggestion(
                        product_category='通用',
                        suggestion_type='improvement',
                        priority=min(5, int(gap_score / 2)),
                        description=f"针对{demand_type}需求的产品改进：当前满足率较低，建议重点优化相关功能",
                        supporting_data={
                            'demand_frequency': demand['frequency'],
                            'satisfaction_rate': demand['satisfaction_rate'],
                            'gap_score': gap_score
                        },
                        expected_impact='提升客户满意度，增加订单转化率',
                        implementation_difficulty='medium'
                    )
                    suggestions.append(suggestion)
            
        except Exception as e:
            self.logger.error(f"识别产品改进机会失败: {str(e)}")
        
        return suggestions
    
    def _identify_new_product_opportunities(self, demand_frequency: Dict[str, Any]) -> List[ProductOptimizationSuggestion]:
        """识别新产品开发机会"""
        suggestions = []
        
        try:
            # 分析未满足的需求组合
            high_frequency_demands = demand_frequency.get('high_frequency_demands', [])
            
            # 寻找需求组合机会
            for i, demand1 in enumerate(high_frequency_demands[:3]):
                for demand2 in high_frequency_demands[i+1:4]:
                    if demand1['satisfaction_rate'] < 0.7 and demand2['satisfaction_rate'] < 0.7:
                        suggestion = ProductOptimizationSuggestion(
                            product_category='创新产品',
                            suggestion_type='new_product',
                            priority=4,
                            description=f"开发同时满足{demand1['demand_type']}和{demand2['demand_type']}需求的新产品",
                            supporting_data={
                                'demand1': demand1,
                                'demand2': demand2,
                                'market_potential': demand1['frequency'] + demand2['frequency']
                            },
                            expected_impact='开拓新市场，提升竞争优势',
                            implementation_difficulty='high'
                        )
                        suggestions.append(suggestion)
                        break  # 每个需求只生成一个组合建议
            
        except Exception as e:
            self.logger.error(f"识别新产品机会失败: {str(e)}")
        
        return suggestions
    
    def _generate_positioning_strategies(self, demand_frequency: Dict[str, Any]) -> List[ProductOptimizationSuggestion]:
        """生成定位策略"""
        suggestions = []
        
        try:
            frequency_data = demand_frequency.get('frequency_distribution', [])
            
            if frequency_data:
                top_demand = frequency_data[0]
                
                suggestion = ProductOptimizationSuggestion(
                    product_category='市场定位',
                    suggestion_type='positioning',
                    priority=3,
                    description=f"基于{top_demand['demand_type']}需求的差异化定位策略",
                    supporting_data={
                        'primary_demand': top_demand,
                        'market_share': top_demand['frequency'] / sum(d['frequency'] for d in frequency_data)
                    },
                    expected_impact='提升品牌认知度，增强市场竞争力',
                    implementation_difficulty='low'
                )
                suggestions.append(suggestion)
            
        except Exception as e:
            self.logger.error(f"生成定位策略失败: {str(e)}")
        
        return suggestions
    
    def _mine_demand_cooccurrence(self) -> Dict[str, Any]:
        """挖掘需求共现模式"""
        try:
            # 获取同一询盘中的需求组合
            aql = """
            FOR inquiry IN inquiries
                LET demands = (
                    FOR demand IN 1..1 OUTBOUND inquiry expresses
                    RETURN demand.type
                )
                FILTER LENGTH(demands) > 1
                RETURN demands
            """
            
            demand_combinations = list(self.arango_service.db.aql.execute(aql))
            
            # 统计共现频率
            cooccurrence_matrix = defaultdict(lambda: defaultdict(int))
            total_inquiries = len(demand_combinations)
            
            for demands in demand_combinations:
                for i, demand1 in enumerate(demands):
                    for demand2 in demands[i+1:]:
                        cooccurrence_matrix[demand1][demand2] += 1
                        cooccurrence_matrix[demand2][demand1] += 1
            
            return {
                'cooccurrence_matrix': dict(cooccurrence_matrix),
                'total_inquiries': total_inquiries,
                'frequent_pairs': self._find_frequent_pairs(cooccurrence_matrix, min_support=3)
            }
            
        except Exception as e:
            self.logger.error(f"需求共现模式挖掘失败: {str(e)}")
            return {}
    
    def _find_frequent_pairs(self, cooccurrence_matrix: Dict[str, Dict[str, int]], 
                           min_support: int = 3) -> List[Dict[str, Any]]:
        """查找频繁需求对"""
        frequent_pairs = []
        
        try:
            for demand1, related_demands in cooccurrence_matrix.items():
                for demand2, count in related_demands.items():
                    if count >= min_support and demand1 < demand2:  # 避免重复
                        frequent_pairs.append({
                            'demand1': demand1,
                            'demand2': demand2,
                            'cooccurrence_count': count,
                            'support': count  # 简化的支持度
                        })
            
            # 按共现次数排序
            frequent_pairs.sort(key=lambda x: x['cooccurrence_count'], reverse=True)
            
        except Exception as e:
            self.logger.error(f"查找频繁需求对失败: {str(e)}")
        
        return frequent_pairs
    
    def _analyze_demand_dependencies(self) -> Dict[str, Any]:
        """分析需求依赖关系"""
        try:
            # 分析客户需求的时间序列，识别依赖模式
            aql = """
            FOR customer IN customers
                LET customer_inquiries = (
                    FOR inquiry IN 1..1 INBOUND customer GRAPH 'inquiry_graph'
                    SORT inquiry.created_at
                    RETURN {
                        inquiry_date: inquiry.created_at,
                        demands: (
                            FOR demand IN 1..1 OUTBOUND inquiry expresses
                            RETURN demand.type
                        )
                    }
                )
                FILTER LENGTH(customer_inquiries) > 1
                RETURN {
                    customer_id: customer._key,
                    inquiry_sequence: customer_inquiries
                }
            """
            
            customer_sequences = list(self.arango_service.db.aql.execute(aql))
            
            # 分析需求转换模式
            transition_matrix = defaultdict(lambda: defaultdict(int))
            
            for customer_data in customer_sequences:
                inquiries = customer_data['inquiry_sequence']
                for i in range(len(inquiries) - 1):
                    current_demands = set(inquiries[i]['demands'])
                    next_demands = set(inquiries[i + 1]['demands'])
                    
                    # 记录需求转换
                    for curr_demand in current_demands:
                        for next_demand in next_demands:
                            if curr_demand != next_demand:
                                transition_matrix[curr_demand][next_demand] += 1
            
            return {
                'transition_matrix': dict(transition_matrix),
                'total_sequences': len(customer_sequences),
                'dependency_patterns': self._identify_dependency_patterns(transition_matrix)
            }
            
        except Exception as e:
            self.logger.error(f"需求依赖关系分析失败: {str(e)}")
            return {}
    
    def _identify_dependency_patterns(self, transition_matrix: Dict[str, Dict[str, int]]) -> List[Dict[str, Any]]:
        """识别依赖模式"""
        patterns = []
        
        try:
            for source_demand, transitions in transition_matrix.items():
                total_transitions = sum(transitions.values())
                if total_transitions >= 3:  # 最少3次转换
                    for target_demand, count in transitions.items():
                        probability = count / total_transitions
                        if probability > 0.3:  # 转换概率阈值
                            patterns.append({
                                'source_demand': source_demand,
                                'target_demand': target_demand,
                                'transition_count': count,
                                'probability': probability,
                                'strength': 'strong' if probability > 0.6 else 'moderate'
                            })
            
            # 按概率排序
            patterns.sort(key=lambda x: x['probability'], reverse=True)
            
        except Exception as e:
            self.logger.error(f"识别依赖模式失败: {str(e)}")
        
        return patterns
    
    def _track_demand_evolution_patterns(self) -> Dict[str, Any]:
        """追踪需求演进模式"""
        try:
            # 分析需求随时间的变化模式
            aql = """
            FOR inquiry IN inquiries
                FOR demand IN 1..1 OUTBOUND inquiry expresses
                COLLECT month = DATE_FORMAT(inquiry.created_at, '%Y-%m'),
                        demand_type = demand.type
                        WITH COUNT INTO count
                SORT month, demand_type
                RETURN {
                    month: month,
                    demand_type: demand_type,
                    count: count
                }
            """
            
            monthly_data = list(self.arango_service.db.aql.execute(aql))
            
            # 构建需求演进时间线
            evolution_timeline = defaultdict(list)
            for item in monthly_data:
                evolution_timeline[item['demand_type']].append({
                    'month': item['month'],
                    'count': item['count']
                })
            
            # 识别演进模式
            evolution_patterns = []
            for demand_type, timeline in evolution_timeline.items():
                if len(timeline) >= 3:  # 至少3个月的数据
                    pattern = self._analyze_evolution_pattern(demand_type, timeline)
                    evolution_patterns.append(pattern)
            
            return {
                'evolution_timeline': dict(evolution_timeline),
                'evolution_patterns': evolution_patterns
            }
            
        except Exception as e:
            self.logger.error(f"需求演进模式追踪失败: {str(e)}")
            return {}
    
    def _analyze_evolution_pattern(self, demand_type: str, timeline: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析单个需求的演进模式"""
        try:
            counts = [item['count'] for item in timeline]
            
            # 计算趋势
            trend = self._calculate_trend(counts)
            
            # 识别生命周期阶段
            max_count = max(counts)
            max_index = counts.index(max_count)
            
            if max_index < len(counts) * 0.3:
                lifecycle_stage = 'declining'
            elif max_index > len(counts) * 0.7:
                lifecycle_stage = 'growing'
            else:
                lifecycle_stage = 'mature'
            
            return {
                'demand_type': demand_type,
                'trend': trend,
                'lifecycle_stage': lifecycle_stage,
                'peak_month': timeline[max_index]['month'],
                'peak_count': max_count,
                'volatility': statistics.stdev(counts) if len(counts) > 1 else 0
            }
            
        except Exception as e:
            self.logger.error(f"分析演进模式失败: {str(e)}")
            return {'demand_type': demand_type, 'trend': {'direction': 'stable'}}
    
    def _generate_association_rules(self, cooccurrence_data: Dict[str, Any], 
                                  min_support: float, min_confidence: float) -> List[DemandAssociation]:
        """生成关联规则"""
        rules = []
        
        try:
            frequent_pairs = cooccurrence_data.get('frequent_pairs', [])
            total_inquiries = cooccurrence_data.get('total_inquiries', 1)
            
            for pair in frequent_pairs:
                demand1 = pair['demand1']
                demand2 = pair['demand2']
                cooccurrence_count = pair['cooccurrence_count']
                
                # 计算支持度
                support = cooccurrence_count / total_inquiries
                
                if support >= min_support:
                    # 计算置信度（双向）
                    # 获取单个需求的频率
                    demand1_count = self._get_demand_frequency(demand1)
                    demand2_count = self._get_demand_frequency(demand2)
                    
                    if demand1_count > 0 and demand2_count > 0:
                        confidence_1_to_2 = cooccurrence_count / demand1_count
                        confidence_2_to_1 = cooccurrence_count / demand2_count
                        
                        # 计算提升度
                        expected_cooccurrence = (demand1_count * demand2_count) / total_inquiries
                        lift = cooccurrence_count / expected_cooccurrence if expected_cooccurrence > 0 else 0
                        
                        # 生成规则（如果满足置信度要求）
                        if confidence_1_to_2 >= min_confidence:
                            rule = DemandAssociation(
                                antecedent=[demand1],
                                consequent=[demand2],
                                support=support,
                                confidence=confidence_1_to_2,
                                lift=lift,
                                rule_strength=self._classify_rule_strength(confidence_1_to_2, lift)
                            )
                            rules.append(rule)
                        
                        if confidence_2_to_1 >= min_confidence:
                            rule = DemandAssociation(
                                antecedent=[demand2],
                                consequent=[demand1],
                                support=support,
                                confidence=confidence_2_to_1,
                                lift=lift,
                                rule_strength=self._classify_rule_strength(confidence_2_to_1, lift)
                            )
                            rules.append(rule)
            
        except Exception as e:
            self.logger.error(f"生成关联规则失败: {str(e)}")
        
        return rules
    
    def _get_demand_frequency(self, demand_type: str) -> int:
        """获取需求频率"""
        try:
            aql = """
            FOR demand IN demands
                FILTER demand.type == @demand_type
                RETURN demand
            """
            
            result = list(self.arango_service.db.aql.execute(aql, bind_vars={'demand_type': demand_type}))
            return len(result)
            
        except Exception:
            return 0
    
    def _classify_rule_strength(self, confidence: float, lift: float) -> str:
        """分类规则强度"""
        if confidence > 0.8 and lift > 2.0:
            return 'strong'
        elif confidence > 0.6 and lift > 1.5:
            return 'medium'
        else:
            return 'weak'
    
    def _validate_association_rules(self, rules: List[DemandAssociation]) -> List[DemandAssociation]:
        """验证关联规则"""
        # 过滤掉弱规则
        validated_rules = [rule for rule in rules if rule.rule_strength in ['strong', 'medium']]
        
        # 按置信度排序
        validated_rules.sort(key=lambda x: x.confidence, reverse=True)
        
        return validated_rules
    
    def _clean_text(self, text: str) -> str:
        """清理文本"""
        # 转小写
        text = text.lower()
        # 移除特殊字符
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        # 移除多余空格
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    # 仪表板数据获取方法
    
    def _get_demand_overview(self) -> Dict[str, Any]:
        """获取需求概览"""
        try:
            aql = """
            RETURN {
                total_demands: LENGTH(demands),
                total_inquiries: LENGTH(inquiries),
                avg_demands_per_inquiry: LENGTH(demands) / LENGTH(inquiries),
                active_demand_types: LENGTH(
                    FOR demand IN demands
                    COLLECT type = demand.type
                    RETURN type
                )
            }
            """
            
            return list(self.arango_service.db.aql.execute(aql))[0]
            
        except Exception as e:
            self.logger.error(f"获取需求概览失败: {str(e)}")
            return {}
    
    def _get_hot_demands(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取热门需求"""
        try:
            aql = """
            FOR demand IN demands
                COLLECT demand_type = demand.type WITH COUNT INTO count
                SORT count DESC
                LIMIT @limit
                RETURN {
                    demand_type: demand_type,
                    frequency: count
                }
            """
            
            return list(self.arango_service.db.aql.execute(aql, bind_vars={'limit': limit}))
            
        except Exception as e:
            self.logger.error(f"获取热门需求失败: {str(e)}")
            return []
    
    def _get_trend_summary(self) -> Dict[str, Any]:
        """获取趋势摘要"""
        try:
            # 获取最近30天的趋势
            trend_analysis = self.analyze_demand_trends(30)
            return trend_analysis.get('trend_summary', {})
            
        except Exception as e:
            self.logger.error(f"获取趋势摘要失败: {str(e)}")
            return {}
    
    def _get_regional_insights(self) -> List[Dict[str, Any]]:
        """获取地域洞察"""
        try:
            aql = """
            FOR inquiry IN inquiries
                FOR customer IN 1..1 OUTBOUND inquiry comes_from
                FOR demand IN 1..1 OUTBOUND inquiry expresses
                COLLECT country = customer.country,
                        demand_type = demand.type
                        WITH COUNT INTO count
                SORT count DESC
                LIMIT 20
                RETURN {
                    country: country,
                    demand_type: demand_type,
                    count: count
                }
            """
            
            return list(self.arango_service.db.aql.execute(aql))
            
        except Exception as e:
            self.logger.error(f"获取地域洞察失败: {str(e)}")
            return []
    
    def _get_product_opportunities(self) -> List[Dict[str, Any]]:
        """获取产品机会"""
        try:
            suggestions = self.generate_product_optimization_suggestions()
            return [{
                'category': s.product_category,
                'type': s.suggestion_type,
                'priority': s.priority,
                'description': s.description
            } for s in suggestions[:5]]  # 返回前5个建议
            
        except Exception as e:
            self.logger.error(f"获取产品机会失败: {str(e)}")
            return []
    
    def _get_association_insights(self) -> List[Dict[str, Any]]:
        """获取关联洞察"""
        try:
            associations = self.analyze_demand_associations()
            return [{
                'antecedent': ' + '.join(a.antecedent),
                'consequent': ' + '.join(a.consequent),
                'confidence': a.confidence,
                'strength': a.rule_strength
            } for a in associations[:5]]  # 返回前5个关联规则
            
        except Exception as e:
            self.logger.error(f"获取关联洞察失败: {str(e)}")
            return []