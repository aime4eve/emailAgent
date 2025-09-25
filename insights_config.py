# -*- coding: utf-8 -*-
"""
外贸知识图谱洞察系统配置文件

本文件包含系统的核心配置参数，包括数据库连接、API配置、算法参数等。
"""

import os
from typing import Dict, Any

class InsightsConfig:
    """洞察系统配置类"""
    
    # 基础配置
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY', 'insights-secret-key-2024')
    
    # 数据库配置
    NEO4J_CONFIG = {
        'uri': os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
        'username': os.getenv('NEO4J_USERNAME', 'neo4j'),
        'password': os.getenv('NEO4J_PASSWORD', 'password'),
        'database': os.getenv('NEO4J_DATABASE', 'neo4j')
    }
    
    REDIS_CONFIG = {
        'host': os.getenv('REDIS_HOST', 'localhost'),
        'port': int(os.getenv('REDIS_PORT', 6379)),
        'db': int(os.getenv('REDIS_DB', 0)),
        'password': os.getenv('REDIS_PASSWORD', None)
    }
    
    MONGODB_CONFIG = {
        'host': os.getenv('MONGODB_HOST', 'localhost'),
        'port': int(os.getenv('MONGODB_PORT', 27017)),
        'database': os.getenv('MONGODB_DATABASE', 'insights_db'),
        'username': os.getenv('MONGODB_USERNAME', None),
        'password': os.getenv('MONGODB_PASSWORD', None)
    }
    
    # NLP配置
    NLP_CONFIG = {
        'spacy_model': 'zh_core_web_sm',  # 中文模型
        'transformers_model': 'bert-base-chinese',
        'max_text_length': 10000,
        'batch_size': 32,
        'confidence_threshold': 0.7
    }
    
    # 知识抽取配置
    EXTRACTION_CONFIG = {
        'entity_types': [
            'PERSON',      # 人员实体
            'ORG',         # 组织实体
            'PRODUCT',     # 产品实体
            'GPE',         # 地理实体
            'MONEY',       # 金额实体
            'DATE',        # 时间实体
            'EMAIL',       # 邮箱实体
            'PHONE'        # 电话实体
        ],
        'relation_types': [
            'INTERESTED_IN',    # 感兴趣
            'PURCHASE',         # 购买
            'INQUIRY',          # 询问
            'QUOTE',            # 报价
            'NEGOTIATE',        # 谈判
            'ORDER',            # 下单
            'DELIVERY',         # 交付
            'PAYMENT',          # 付款
            'WORKS_FOR',        # 工作于
            'REPRESENTS',       # 代表
            'LOCATED_IN',       # 位于
            'SUPPLIES',         # 供应
            'NEEDS'             # 需要
        ],
        'min_confidence': 0.6,
        'max_relations_per_text': 50
    }
    
    # 图算法配置
    GRAPH_ALGORITHM_CONFIG = {
        'pagerank': {
            'alpha': 0.85,
            'max_iter': 100,
            'tol': 1e-6
        },
        'community_detection': {
            'algorithm': 'louvain',
            'resolution': 1.0,
            'random_state': 42
        },
        'centrality': {
            'k': 100,  # 计算前k个重要节点
            'normalized': True
        }
    }
    
    # 业务洞察配置
    BUSINESS_INSIGHTS_CONFIG = {
        'customer_analysis': {
            'intent_threshold': 0.7,
            'value_tiers': ['钻石', '黄金', '白银', '青铜'],
            'intent_levels': ['高意向', '中意向', '低意向', '观望']
        },
        'product_analysis': {
            'feature_extraction_threshold': 0.6,
            'price_sensitivity_levels': ['高', '中', '低'],
            'customization_types': ['功能定制', '界面定制', '集成定制', '服务定制']
        },
        'market_analysis': {
            'trend_window_days': 90,
            'competitor_threshold': 0.8,
            'market_segments': ['地理', '经济', '文化', '政策']
        },
        'risk_analysis': {
            'risk_levels': ['高', '中', '低'],
            'alert_threshold': 0.8,
            'risk_types': ['信用风险', '市场风险', '操作风险', '合规风险']
        }
    }
    
    # API配置
    API_CONFIG = {
        'version': 'v1',
        'rate_limit': '1000/hour',
        'timeout': 30,
        'max_page_size': 100,
        'default_page_size': 20
    }
    
    # 缓存配置
    CACHE_CONFIG = {
        'default_timeout': 3600,  # 1小时
        'graph_query_timeout': 1800,  # 30分钟
        'insights_timeout': 7200,  # 2小时
        'key_prefix': 'insights:'
    }
    
    # 日志配置
    LOGGING_CONFIG = {
        'level': os.getenv('LOG_LEVEL', 'INFO'),
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'file': 'logs/insights.log',
        'max_bytes': 10 * 1024 * 1024,  # 10MB
        'backup_count': 5
    }
    
    # 性能配置
    PERFORMANCE_CONFIG = {
        'max_concurrent_requests': 100,
        'request_timeout': 30,
        'db_pool_size': 20,
        'worker_processes': 4
    }
    
    @classmethod
    def get_config(cls, section: str = None) -> Dict[str, Any]:
        """获取配置信息
        
        Args:
            section: 配置节名称，如果为None则返回所有配置
            
        Returns:
            配置字典
        """
        if section is None:
            return {
                'neo4j': cls.NEO4J_CONFIG,
                'redis': cls.REDIS_CONFIG,
                'mongodb': cls.MONGODB_CONFIG,
                'nlp': cls.NLP_CONFIG,
                'extraction': cls.EXTRACTION_CONFIG,
                'graph_algorithm': cls.GRAPH_ALGORITHM_CONFIG,
                'business_insights': cls.BUSINESS_INSIGHTS_CONFIG,
                'api': cls.API_CONFIG,
                'cache': cls.CACHE_CONFIG,
                'logging': cls.LOGGING_CONFIG,
                'performance': cls.PERFORMANCE_CONFIG
            }
        
        config_map = {
            'neo4j': cls.NEO4J_CONFIG,
            'redis': cls.REDIS_CONFIG,
            'mongodb': cls.MONGODB_CONFIG,
            'nlp': cls.NLP_CONFIG,
            'extraction': cls.EXTRACTION_CONFIG,
            'graph_algorithm': cls.GRAPH_ALGORITHM_CONFIG,
            'business_insights': cls.BUSINESS_INSIGHTS_CONFIG,
            'api': cls.API_CONFIG,
            'cache': cls.CACHE_CONFIG,
            'logging': cls.LOGGING_CONFIG,
            'performance': cls.PERFORMANCE_CONFIG
        }
        
        return config_map.get(section, {})
    
    @classmethod
    def validate_config(cls) -> bool:
        """验证配置的有效性
        
        Returns:
            配置是否有效
        """
        try:
            # 验证必要的配置项
            required_configs = [
                cls.NEO4J_CONFIG['uri'],
                cls.REDIS_CONFIG['host'],
                cls.NLP_CONFIG['spacy_model']
            ]
            
            for config in required_configs:
                if not config:
                    return False
                    
            return True
        except Exception:
            return False

# 全局配置实例
config = InsightsConfig()