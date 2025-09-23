#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
外贸询盘本体管理系统
定义客户、公司、产品、需求等核心概念类别
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union
from enum import Enum
from datetime import datetime
import uuid

class CustomerType(Enum):
    """客户类型枚举"""
    POTENTIAL = "potential"      # 潜在客户
    EXISTING = "existing"        # 现有客户
    HIGH_VALUE = "high_value"    # 高价值客户

class CustomerGrade(Enum):
    """客户分级枚举"""
    A = "A"  # 高价值、高潜力、优先跟进
    B = "B"  # 中等价值、有潜力、定期维护
    C = "C"  # 低价值、观察跟踪

class CompanyScale(Enum):
    """公司规模枚举"""
    STARTUP = "startup"          # 初创企业
    SMALL = "small"              # 小型企业
    MEDIUM = "medium"            # 中型企业
    LARGE = "large"              # 大型企业
    ENTERPRISE = "enterprise"    # 企业集团

class DemandType(Enum):
    """需求类型枚举"""
    # 产品需求
    PERFORMANCE = "performance"      # 性能需求
    APPEARANCE = "appearance"        # 外观设计
    MATERIAL = "material"            # 材料需求
    SMART_FEATURES = "smart_features" # 智能化需求
    
    # 商务需求
    PRICE = "price"                  # 价格关注
    MOQ = "moq"                      # 最小起订量
    LEAD_TIME = "lead_time"          # 交付周期
    CERTIFICATION = "certification"  # 认证要求

class InquiryUrgency(Enum):
    """询盘紧急程度枚举"""
    LOW = "low"        # 低
    MEDIUM = "medium"  # 中
    HIGH = "high"      # 高
    URGENT = "urgent"  # 紧急

@dataclass
class Customer:
    """客户实体类"""
    customer_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    email: str = ""
    phone: Optional[str] = None
    country: str = ""
    region: str = ""
    customer_type: CustomerType = CustomerType.POTENTIAL
    customer_grade: CustomerGrade = CustomerGrade.C
    value_score: float = 0.0  # 客户价值评分 (0-100)
    
    # 客户画像相关
    inquiry_frequency: int = 0  # 询盘频率
    avg_order_value: float = 0.0  # 平均订单价值
    communication_preference: str = "email"  # 沟通偏好
    price_sensitivity: float = 0.5  # 价格敏感度 (0-1)
    quality_focus: float = 0.5  # 质量关注度 (0-1)
    
    # 时间戳
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_inquiry_date: Optional[datetime] = None
    
    # 扩展属性
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'customer_id': self.customer_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'country': self.country,
            'region': self.region,
            'customer_type': self.customer_type.value,
            'customer_grade': self.customer_grade.value,
            'value_score': self.value_score,
            'inquiry_frequency': self.inquiry_frequency,
            'avg_order_value': self.avg_order_value,
            'communication_preference': self.communication_preference,
            'price_sensitivity': self.price_sensitivity,
            'quality_focus': self.quality_focus,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'last_inquiry_date': self.last_inquiry_date.isoformat() if self.last_inquiry_date else None,
            'properties': self.properties
        }

@dataclass
class Company:
    """公司实体类"""
    company_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    industry: str = ""
    scale: CompanyScale = CompanyScale.SMALL
    country: str = ""
    city: str = ""
    address: Optional[str] = None
    website: Optional[str] = None
    
    # 公司实力评估
    credit_rating: str = ""  # 信用等级
    annual_revenue: Optional[float] = None  # 年收入
    employee_count: Optional[int] = None  # 员工数量
    established_year: Optional[int] = None  # 成立年份
    
    # 时间戳
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # 扩展属性
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'company_id': self.company_id,
            'name': self.name,
            'industry': self.industry,
            'scale': self.scale.value,
            'country': self.country,
            'city': self.city,
            'address': self.address,
            'website': self.website,
            'credit_rating': self.credit_rating,
            'annual_revenue': self.annual_revenue,
            'employee_count': self.employee_count,
            'established_year': self.established_year,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'properties': self.properties
        }

@dataclass
class Product:
    """产品实体类"""
    product_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    model: str = ""
    category: str = ""
    subcategory: Optional[str] = None
    
    # 产品属性
    price: Optional[float] = None
    currency: str = "USD"
    specifications: Dict[str, Any] = field(default_factory=dict)
    features: List[str] = field(default_factory=list)
    materials: List[str] = field(default_factory=list)
    
    # 商务信息
    moq: Optional[int] = None  # 最小起订量
    lead_time: Optional[int] = None  # 交付周期（天）
    certifications: List[str] = field(default_factory=list)
    
    # 市场信息
    target_market: List[str] = field(default_factory=list)
    competitor_products: List[str] = field(default_factory=list)
    
    # 时间戳
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # 扩展属性
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'product_id': self.product_id,
            'name': self.name,
            'model': self.model,
            'category': self.category,
            'subcategory': self.subcategory,
            'price': self.price,
            'currency': self.currency,
            'specifications': self.specifications,
            'features': self.features,
            'materials': self.materials,
            'moq': self.moq,
            'lead_time': self.lead_time,
            'certifications': self.certifications,
            'target_market': self.target_market,
            'competitor_products': self.competitor_products,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'properties': self.properties
        }

@dataclass
class Demand:
    """需求/关注点实体类"""
    demand_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: DemandType = DemandType.PERFORMANCE
    description: str = ""
    priority: int = 1  # 优先级 (1-5)
    
    # 需求详情
    keywords: List[str] = field(default_factory=list)
    requirements: Dict[str, Any] = field(default_factory=dict)
    constraints: Dict[str, Any] = field(default_factory=dict)
    
    # 统计信息
    frequency: int = 0  # 出现频率
    satisfaction_rate: float = 0.0  # 满足率
    
    # 时间戳
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # 扩展属性
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'demand_id': self.demand_id,
            'type': self.type.value,
            'description': self.description,
            'priority': self.priority,
            'keywords': self.keywords,
            'requirements': self.requirements,
            'constraints': self.constraints,
            'frequency': self.frequency,
            'satisfaction_rate': self.satisfaction_rate,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'properties': self.properties
        }

@dataclass
class InquiryEvent:
    """询盘事件实体类"""
    inquiry_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    email_subject: str = ""
    email_content: str = ""
    content_summary: str = ""
    
    # 询盘属性
    urgency: InquiryUrgency = InquiryUrgency.MEDIUM
    purchase_intent: float = 0.5  # 购买意向强度 (0-1)
    sentiment_score: float = 0.0  # 情感分数 (-1到1)
    
    # 提取的信息
    mentioned_products: List[str] = field(default_factory=list)
    mentioned_demands: List[str] = field(default_factory=list)
    price_range: Optional[Dict[str, float]] = None  # {"min": 100, "max": 500}
    quantity_requested: Optional[int] = None
    delivery_deadline: Optional[datetime] = None
    
    # 时间戳
    inquiry_date: datetime = field(default_factory=datetime.now)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # 处理状态
    processed: bool = False
    response_sent: bool = False
    follow_up_required: bool = True
    
    # 扩展属性
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'inquiry_id': self.inquiry_id,
            'email_subject': self.email_subject,
            'email_content': self.email_content,
            'content_summary': self.content_summary,
            'urgency': self.urgency.value,
            'purchase_intent': self.purchase_intent,
            'sentiment_score': self.sentiment_score,
            'mentioned_products': self.mentioned_products,
            'mentioned_demands': self.mentioned_demands,
            'price_range': self.price_range,
            'quantity_requested': self.quantity_requested,
            'delivery_deadline': self.delivery_deadline.isoformat() if self.delivery_deadline else None,
            'inquiry_date': self.inquiry_date.isoformat(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'processed': self.processed,
            'response_sent': self.response_sent,
            'follow_up_required': self.follow_up_required,
            'properties': self.properties
        }

@dataclass
class Relationship:
    """关系实体类"""
    relationship_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    relationship_type: str = ""  # 关系类型
    source_entity: str = ""  # 源实体ID
    target_entity: str = ""  # 目标实体ID
    
    # 关系属性
    strength: float = 1.0  # 关系强度 (0-1)
    confidence: float = 1.0  # 置信度 (0-1)
    weight: float = 1.0  # 权重
    
    # 时间戳
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # 扩展属性
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'relationship_id': self.relationship_id,
            'relationship_type': self.relationship_type,
            'source_entity': self.source_entity,
            'target_entity': self.target_entity,
            'strength': self.strength,
            'confidence': self.confidence,
            'weight': self.weight,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'properties': self.properties
        }

class InquiryOntology:
    """外贸询盘本体管理类"""
    
    def __init__(self):
        """初始化本体管理器"""
        self.customers: Dict[str, Customer] = {}
        self.companies: Dict[str, Company] = {}
        self.products: Dict[str, Product] = {}
        self.demands: Dict[str, Demand] = {}
        self.inquiries: Dict[str, InquiryEvent] = {}
        self.relationships: Dict[str, Relationship] = {}
    
    def add_customer(self, customer: Customer) -> str:
        """添加客户"""
        self.customers[customer.customer_id] = customer
        return customer.customer_id
    
    def add_company(self, company: Company) -> str:
        """添加公司"""
        self.companies[company.company_id] = company
        return company.company_id
    
    def add_product(self, product: Product) -> str:
        """添加产品"""
        self.products[product.product_id] = product
        return product.product_id
    
    def add_demand(self, demand: Demand) -> str:
        """添加需求"""
        self.demands[demand.demand_id] = demand
        return demand.demand_id
    
    def add_inquiry(self, inquiry: InquiryEvent) -> str:
        """添加询盘事件"""
        self.inquiries[inquiry.inquiry_id] = inquiry
        return inquiry.inquiry_id
    
    def add_relationship(self, relationship: Relationship) -> str:
        """添加关系"""
        self.relationships[relationship.relationship_id] = relationship
        return relationship.relationship_id
    
    def get_customer_by_email(self, email: str) -> Optional[Customer]:
        """根据邮箱获取客户"""
        for customer in self.customers.values():
            if customer.email == email:
                return customer
        return None
    
    def get_products_by_category(self, category: str) -> List[Product]:
        """根据类别获取产品"""
        return [product for product in self.products.values() 
                if product.category.lower() == category.lower()]
    
    def get_high_value_customers(self, min_score: float = 80.0) -> List[Customer]:
        """获取高价值客户"""
        return [customer for customer in self.customers.values() 
                if customer.value_score >= min_score]
    
    def get_customer_inquiries(self, customer_id: str) -> List[InquiryEvent]:
        """获取客户的所有询盘"""
        customer_inquiries = []
        for relationship in self.relationships.values():
            if (relationship.relationship_type == "comes_from" and 
                relationship.target_entity == customer_id):
                inquiry_id = relationship.source_entity
                if inquiry_id in self.inquiries:
                    customer_inquiries.append(self.inquiries[inquiry_id])
        return customer_inquiries
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'customers': {k: v.to_dict() for k, v in self.customers.items()},
            'companies': {k: v.to_dict() for k, v in self.companies.items()},
            'products': {k: v.to_dict() for k, v in self.products.items()},
            'demands': {k: v.to_dict() for k, v in self.demands.items()},
            'inquiries': {k: v.to_dict() for k, v in self.inquiries.items()},
            'relationships': {k: v.to_dict() for k, v in self.relationships.items()}
        }