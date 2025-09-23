#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多Agent邮件知识抽取框架
实现客户信息、产品需求、商务条件、情感分析等专门Agent的协作处理
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
import logging
import re
import json
from datetime import datetime
from dataclasses import dataclass

# NLP相关导入
try:
    import spacy
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    from textblob import TextBlob
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
except ImportError as e:
    logging.warning(f"NLP库导入失败: {e}")
    spacy = None
    pipeline = None
    TextBlob = None
    SentimentIntensityAnalyzer = None

@dataclass
class ExtractionResult:
    """抽取结果数据类"""
    agent_name: str
    extracted_data: Dict[str, Any]
    confidence: float
    processing_time: float
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []

class BaseExtractionAgent(ABC):
    """抽取Agent基类"""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        """
        初始化抽取Agent
        
        Args:
            name: Agent名称
            config: 配置参数
        """
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{name}")
        self._initialize_models()
    
    @abstractmethod
    def _initialize_models(self):
        """初始化模型和工具"""
        pass
    
    @abstractmethod
    def extract(self, email_content: str, email_subject: str = "") -> ExtractionResult:
        """执行抽取任务"""
        pass
    
    def _preprocess_text(self, text: str) -> str:
        """文本预处理"""
        # 清理HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        # 清理多余空白
        text = re.sub(r'\s+', ' ', text).strip()
        # 清理特殊字符
        text = re.sub(r'[^\w\s\.,!?;:()\-@]', '', text)
        return text
    
    def _extract_emails(self, text: str) -> List[str]:
        """提取邮箱地址"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.findall(email_pattern, text)
    
    def _extract_phones(self, text: str) -> List[str]:
        """提取电话号码"""
        phone_patterns = [
            r'\+?\d{1,4}[\s\-]?\(?\d{1,4}\)?[\s\-]?\d{1,4}[\s\-]?\d{1,9}',
            r'\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4}',
            r'\d{3}[\s\-]?\d{4}[\s\-]?\d{4}'
        ]
        
        phones = []
        for pattern in phone_patterns:
            phones.extend(re.findall(pattern, text))
        
        # 清理和验证电话号码
        cleaned_phones = []
        for phone in phones:
            cleaned = re.sub(r'[^\d+]', '', phone)
            if len(cleaned) >= 7:  # 最少7位数字
                cleaned_phones.append(phone.strip())
        
        return list(set(cleaned_phones))  # 去重
    
    def _extract_currencies_and_prices(self, text: str) -> List[Dict[str, Any]]:
        """提取货币和价格信息"""
        price_patterns = [
            r'\$\s?([\d,]+(?:\.\d{2})?)',  # 美元
            r'€\s?([\d,]+(?:\.\d{2})?)',  # 欧元
            r'£\s?([\d,]+(?:\.\d{2})?)',  # 英镑
            r'¥\s?([\d,]+(?:\.\d{2})?)',  # 人民币/日元
            r'USD\s?([\d,]+(?:\.\d{2})?)',  # USD
            r'EUR\s?([\d,]+(?:\.\d{2})?)',  # EUR
            r'CNY\s?([\d,]+(?:\.\d{2})?)',  # CNY
        ]
        
        prices = []
        for pattern in price_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                currency_symbol = match.group(0).replace(match.group(1), '').strip()
                amount_str = match.group(1).replace(',', '')
                try:
                    amount = float(amount_str)
                    prices.append({
                        'currency': currency_symbol,
                        'amount': amount,
                        'original_text': match.group(0)
                    })
                except ValueError:
                    continue
        
        return prices

class CustomerInfoExtractionAgent(BaseExtractionAgent):
    """客户信息抽取Agent"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("CustomerInfoExtractor", config)
    
    def _initialize_models(self):
        """初始化NLP模型"""
        try:
            if spacy:
                # 尝试加载中英文模型
                try:
                    self.nlp = spacy.load("zh_core_web_sm")
                except OSError:
                    try:
                        self.nlp = spacy.load("en_core_web_sm")
                    except OSError:
                        self.logger.warning("未找到spaCy模型，使用基础功能")
                        self.nlp = None
            else:
                self.nlp = None
        except Exception as e:
            self.logger.error(f"初始化NLP模型失败: {str(e)}")
            self.nlp = None
    
    def extract(self, email_content: str, email_subject: str = "") -> ExtractionResult:
        """提取客户信息"""
        start_time = datetime.now()
        errors = []
        
        try:
            # 预处理文本
            full_text = f"{email_subject} {email_content}"
            cleaned_text = self._preprocess_text(full_text)
            
            extracted_data = {
                'customer_name': self._extract_customer_name(cleaned_text),
                'email_addresses': self._extract_emails(cleaned_text),
                'phone_numbers': self._extract_phones(cleaned_text),
                'company_name': self._extract_company_name(cleaned_text),
                'location_info': self._extract_location_info(cleaned_text),
                'contact_person': self._extract_contact_person(cleaned_text)
            }
            
            # 计算置信度
            confidence = self._calculate_confidence(extracted_data)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return ExtractionResult(
                agent_name=self.name,
                extracted_data=extracted_data,
                confidence=confidence,
                processing_time=processing_time,
                errors=errors
            )
            
        except Exception as e:
            errors.append(f"客户信息抽取失败: {str(e)}")
            self.logger.error(f"客户信息抽取失败: {str(e)}")
            
            processing_time = (datetime.now() - start_time).total_seconds()
            return ExtractionResult(
                agent_name=self.name,
                extracted_data={},
                confidence=0.0,
                processing_time=processing_time,
                errors=errors
            )
    
    def _extract_customer_name(self, text: str) -> List[str]:
        """提取客户姓名"""
        names = []
        
        # 使用spaCy提取人名
        if self.nlp:
            try:
                doc = self.nlp(text)
                for ent in doc.ents:
                    if ent.label_ in ['PERSON', 'PER']:
                        names.append(ent.text.strip())
            except Exception as e:
                self.logger.warning(f"spaCy人名提取失败: {str(e)}")
        
        # 使用正则表达式提取常见签名格式
        signature_patterns = [
            r'Best regards,\s*([A-Za-z\s]+)',
            r'Sincerely,\s*([A-Za-z\s]+)',
            r'Thanks,\s*([A-Za-z\s]+)',
            r'From:\s*([A-Za-z\s]+)',
            r'Contact:\s*([A-Za-z\s]+)',
        ]
        
        for pattern in signature_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                name = match.strip()
                if len(name.split()) <= 3 and len(name) > 2:  # 合理的姓名长度
                    names.append(name)
        
        return list(set(names))  # 去重
    
    def _extract_company_name(self, text: str) -> List[str]:
        """提取公司名称"""
        companies = []
        
        # 使用spaCy提取组织名
        if self.nlp:
            try:
                doc = self.nlp(text)
                for ent in doc.ents:
                    if ent.label_ in ['ORG', 'ORGANIZATION']:
                        companies.append(ent.text.strip())
            except Exception as e:
                self.logger.warning(f"spaCy组织名提取失败: {str(e)}")
        
        # 使用正则表达式提取公司关键词
        company_patterns = [
            r'([A-Za-z\s]+)\s+(?:Co\.|Company|Corp\.|Corporation|Inc\.|Incorporated|Ltd\.|Limited|LLC)',
            r'From:\s*([A-Za-z\s]+)\s+(?:Co\.|Company|Corp\.|Corporation)',
            r'([A-Za-z\s]+)\s+(?:Manufacturing|Trading|Industrial|Technology|Tech)',
        ]
        
        for pattern in company_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                company = match.strip()
                if len(company) > 2 and len(company) < 50:
                    companies.append(company)
        
        return list(set(companies))  # 去重
    
    def _extract_location_info(self, text: str) -> Dict[str, List[str]]:
        """提取位置信息"""
        location_info = {
            'countries': [],
            'cities': [],
            'addresses': []
        }
        
        # 使用spaCy提取地理位置
        if self.nlp:
            try:
                doc = self.nlp(text)
                for ent in doc.ents:
                    if ent.label_ in ['GPE', 'LOC', 'LOCATION']:
                        location_text = ent.text.strip()
                        # 简单分类（实际应用中可能需要更复杂的逻辑）
                        if any(country in location_text.lower() for country in 
                               ['china', 'usa', 'germany', 'japan', 'india', 'uk', 'france']):
                            location_info['countries'].append(location_text)
                        else:
                            location_info['cities'].append(location_text)
            except Exception as e:
                self.logger.warning(f"spaCy地理位置提取失败: {str(e)}")
        
        # 使用正则表达式提取地址
        address_patterns = [
            r'Address:\s*([^\n]+)',
            r'Located in\s*([^\n]+)',
            r'From\s*([^,]+,\s*[^,]+,\s*[^\n]+)',
        ]
        
        for pattern in address_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                address = match.strip()
                if len(address) > 10:
                    location_info['addresses'].append(address)
        
        return location_info
    
    def _extract_contact_person(self, text: str) -> Dict[str, Any]:
        """提取联系人信息"""
        contact_info = {
            'name': '',
            'title': '',
            'department': ''
        }
        
        # 提取职位信息
        title_patterns = [
            r'([A-Za-z\s]+)\s*,\s*(Manager|Director|CEO|CTO|Sales|Engineer|Coordinator)',
            r'(Manager|Director|CEO|CTO|Sales|Engineer|Coordinator)\s*([A-Za-z\s]+)',
        ]
        
        for pattern in title_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple) and len(match) == 2:
                    name_part, title_part = match
                    if len(name_part.strip()) > len(title_part.strip()):
                        contact_info['name'] = name_part.strip()
                        contact_info['title'] = title_part.strip()
                    else:
                        contact_info['name'] = title_part.strip()
                        contact_info['title'] = name_part.strip()
                    break
        
        return contact_info
    
    def _calculate_confidence(self, extracted_data: Dict[str, Any]) -> float:
        """计算抽取置信度"""
        confidence = 0.0
        total_fields = 6
        
        # 根据提取到的信息计算置信度
        if extracted_data.get('email_addresses'):
            confidence += 0.3
        if extracted_data.get('customer_name'):
            confidence += 0.2
        if extracted_data.get('company_name'):
            confidence += 0.2
        if extracted_data.get('phone_numbers'):
            confidence += 0.1
        if extracted_data.get('location_info', {}).get('countries'):
            confidence += 0.1
        if extracted_data.get('contact_person', {}).get('name'):
            confidence += 0.1
        
        return min(confidence, 1.0)

class ProductDemandAnalysisAgent(BaseExtractionAgent):
    """产品需求分析Agent"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("ProductDemandAnalyzer", config)
    
    def _initialize_models(self):
        """初始化模型"""
        # 产品关键词词典
        self.product_keywords = {
            'electronics': ['phone', 'computer', 'laptop', 'tablet', 'camera', 'headphone'],
            'machinery': ['machine', 'equipment', 'motor', 'pump', 'valve', 'bearing'],
            'textiles': ['fabric', 'cloth', 'yarn', 'cotton', 'silk', 'polyester'],
            'chemicals': ['chemical', 'acid', 'polymer', 'resin', 'coating', 'paint'],
            'automotive': ['car', 'auto', 'vehicle', 'tire', 'brake', 'engine'],
            'furniture': ['chair', 'table', 'sofa', 'bed', 'cabinet', 'desk']
        }
        
        # 需求关键词
        self.demand_keywords = {
            'price': ['price', 'cost', 'cheap', 'expensive', 'budget', 'quote'],
            'quality': ['quality', 'grade', 'standard', 'certification', 'test'],
            'quantity': ['quantity', 'moq', 'minimum', 'order', 'pieces', 'units'],
            'delivery': ['delivery', 'shipping', 'lead time', 'urgent', 'fast'],
            'specification': ['spec', 'size', 'dimension', 'color', 'material', 'feature']
        }
    
    def extract(self, email_content: str, email_subject: str = "") -> ExtractionResult:
        """分析产品需求"""
        start_time = datetime.now()
        errors = []
        
        try:
            full_text = f"{email_subject} {email_content}"
            cleaned_text = self._preprocess_text(full_text)
            
            extracted_data = {
                'mentioned_products': self._extract_product_mentions(cleaned_text),
                'product_categories': self._classify_product_categories(cleaned_text),
                'technical_requirements': self._extract_technical_requirements(cleaned_text),
                'demand_types': self._classify_demand_types(cleaned_text),
                'specifications': self._extract_specifications(cleaned_text),
                'price_information': self._extract_currencies_and_prices(cleaned_text)
            }
            
            confidence = self._calculate_confidence(extracted_data)
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return ExtractionResult(
                agent_name=self.name,
                extracted_data=extracted_data,
                confidence=confidence,
                processing_time=processing_time,
                errors=errors
            )
            
        except Exception as e:
            errors.append(f"产品需求分析失败: {str(e)}")
            self.logger.error(f"产品需求分析失败: {str(e)}")
            
            processing_time = (datetime.now() - start_time).total_seconds()
            return ExtractionResult(
                agent_name=self.name,
                extracted_data={},
                confidence=0.0,
                processing_time=processing_time,
                errors=errors
            )
    
    def _extract_product_mentions(self, text: str) -> List[str]:
        """提取产品提及"""
        products = []
        text_lower = text.lower()
        
        # 遍历所有产品关键词
        for category, keywords in self.product_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    # 提取包含关键词的短语
                    pattern = rf'\b[\w\s]*{re.escape(keyword)}[\w\s]*\b'
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    for match in matches:
                        product = match.strip()
                        if len(product) > len(keyword) and len(product) < 50:
                            products.append(product)
        
        return list(set(products))
    
    def _classify_product_categories(self, text: str) -> List[str]:
        """分类产品类别"""
        categories = []
        text_lower = text.lower()
        
        for category, keywords in self.product_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                categories.append(category)
        
        return categories
    
    def _extract_technical_requirements(self, text: str) -> List[str]:
        """提取技术要求"""
        requirements = []
        
        # 技术要求模式
        tech_patterns = [
            r'requirement[s]?:\s*([^\n]+)',
            r'specification[s]?:\s*([^\n]+)',
            r'need[s]?\s+([^\n]+)',
            r'must\s+([^\n]+)',
            r'should\s+([^\n]+)'
        ]
        
        for pattern in tech_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                req = match.strip()
                if len(req) > 5:
                    requirements.append(req)
        
        return requirements
    
    def _classify_demand_types(self, text: str) -> Dict[str, int]:
        """分类需求类型"""
        demand_counts = {}
        text_lower = text.lower()
        
        for demand_type, keywords in self.demand_keywords.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            if count > 0:
                demand_counts[demand_type] = count
        
        return demand_counts
    
    def _extract_specifications(self, text: str) -> Dict[str, List[str]]:
        """提取规格信息"""
        specs = {
            'dimensions': [],
            'materials': [],
            'colors': [],
            'quantities': []
        }
        
        # 尺寸规格
        dimension_patterns = [
            r'(\d+)\s*[x×]\s*(\d+)\s*[x×]\s*(\d+)\s*(?:mm|cm|m|inch)',
            r'(\d+)\s*[x×]\s*(\d+)\s*(?:mm|cm|m|inch)',
            r'diameter\s*(\d+)\s*(?:mm|cm|m|inch)',
            r'length\s*(\d+)\s*(?:mm|cm|m|inch)'
        ]
        
        for pattern in dimension_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    specs['dimensions'].append(' x '.join(match))
                else:
                    specs['dimensions'].append(match)
        
        # 材料
        material_keywords = ['steel', 'aluminum', 'plastic', 'wood', 'glass', 'ceramic', 'rubber']
        for material in material_keywords:
            if material in text.lower():
                specs['materials'].append(material)
        
        # 颜色
        color_keywords = ['red', 'blue', 'green', 'black', 'white', 'yellow', 'gray', 'silver']
        for color in color_keywords:
            if color in text.lower():
                specs['colors'].append(color)
        
        # 数量
        quantity_patterns = [
            r'(\d+)\s*(?:pieces|pcs|units|sets)',
            r'quantity[:\s]*(\d+)',
            r'moq[:\s]*(\d+)'
        ]
        
        for pattern in quantity_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                specs['quantities'].append(match)
        
        return specs
    
    def _calculate_confidence(self, extracted_data: Dict[str, Any]) -> float:
        """计算置信度"""
        confidence = 0.0
        
        if extracted_data.get('mentioned_products'):
            confidence += 0.3
        if extracted_data.get('product_categories'):
            confidence += 0.2
        if extracted_data.get('demand_types'):
            confidence += 0.2
        if extracted_data.get('specifications', {}):
            confidence += 0.15
        if extracted_data.get('price_information'):
            confidence += 0.15
        
        return min(confidence, 1.0)

class BusinessConditionExtractionAgent(BaseExtractionAgent):
    """商务条件抽取Agent"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("BusinessConditionExtractor", config)
    
    def _initialize_models(self):
        """初始化模型"""
        pass
    
    def extract(self, email_content: str, email_subject: str = "") -> ExtractionResult:
        """提取商务条件"""
        start_time = datetime.now()
        errors = []
        
        try:
            full_text = f"{email_subject} {email_content}"
            cleaned_text = self._preprocess_text(full_text)
            
            extracted_data = {
                'price_information': self._extract_currencies_and_prices(cleaned_text),
                'payment_terms': self._extract_payment_terms(cleaned_text),
                'delivery_terms': self._extract_delivery_terms(cleaned_text),
                'moq_information': self._extract_moq_info(cleaned_text),
                'lead_time': self._extract_lead_time(cleaned_text),
                'certifications': self._extract_certifications(cleaned_text),
                'trade_terms': self._extract_trade_terms(cleaned_text)
            }
            
            confidence = self._calculate_confidence(extracted_data)
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return ExtractionResult(
                agent_name=self.name,
                extracted_data=extracted_data,
                confidence=confidence,
                processing_time=processing_time,
                errors=errors
            )
            
        except Exception as e:
            errors.append(f"商务条件抽取失败: {str(e)}")
            self.logger.error(f"商务条件抽取失败: {str(e)}")
            
            processing_time = (datetime.now() - start_time).total_seconds()
            return ExtractionResult(
                agent_name=self.name,
                extracted_data={},
                confidence=0.0,
                processing_time=processing_time,
                errors=errors
            )
    
    def _extract_payment_terms(self, text: str) -> List[str]:
        """提取付款条件"""
        payment_terms = []
        
        payment_patterns = [
            r'payment\s*terms?[:\s]*([^\n]+)',
            r'payment[:\s]*([^\n]+)',
            r'(T/T|L/C|D/P|D/A|Western Union|PayPal)',
            r'(\d+)%\s*advance',
            r'(\d+)\s*days?\s*after'
        ]
        
        for pattern in payment_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                term = match.strip() if isinstance(match, str) else ' '.join(match)
                if len(term) > 2:
                    payment_terms.append(term)
        
        return list(set(payment_terms))
    
    def _extract_delivery_terms(self, text: str) -> List[str]:
        """提取交付条件"""
        delivery_terms = []
        
        delivery_patterns = [
            r'delivery\s*terms?[:\s]*([^\n]+)',
            r'shipping[:\s]*([^\n]+)',
            r'(FOB|CIF|CFR|EXW|DDP|DDU)',
            r'delivery\s*time[:\s]*([^\n]+)',
            r'lead\s*time[:\s]*([^\n]+)'
        ]
        
        for pattern in delivery_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                term = match.strip()
                if len(term) > 2:
                    delivery_terms.append(term)
        
        return list(set(delivery_terms))
    
    def _extract_moq_info(self, text: str) -> List[Dict[str, Any]]:
        """提取最小起订量信息"""
        moq_info = []
        
        moq_patterns = [
            r'MOQ[:\s]*(\d+)\s*(\w+)?',
            r'minimum\s*order[:\s]*(\d+)\s*(\w+)?',
            r'min\s*qty[:\s]*(\d+)\s*(\w+)?'
        ]
        
        for pattern in moq_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                quantity = match[0]
                unit = match[1] if len(match) > 1 and match[1] else 'pieces'
                moq_info.append({
                    'quantity': int(quantity),
                    'unit': unit
                })
        
        return moq_info
    
    def _extract_lead_time(self, text: str) -> List[str]:
        """提取交付周期"""
        lead_times = []
        
        time_patterns = [
            r'lead\s*time[:\s]*(\d+)\s*(days?|weeks?|months?)',
            r'delivery\s*in\s*(\d+)\s*(days?|weeks?|months?)',
            r'(\d+)\s*(days?|weeks?|months?)\s*delivery',
            r'within\s*(\d+)\s*(days?|weeks?|months?)'
        ]
        
        for pattern in time_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    lead_time = f"{match[0]} {match[1]}"
                else:
                    lead_time = match
                lead_times.append(lead_time)
        
        return list(set(lead_times))
    
    def _extract_certifications(self, text: str) -> List[str]:
        """提取认证要求"""
        certifications = []
        
        cert_keywords = [
            'CE', 'ISO', 'FDA', 'FCC', 'RoHS', 'UL', 'CSA', 'ETL',
            'ASTM', 'ANSI', 'JIS', 'DIN', 'BS', 'GB', 'CPSIA'
        ]
        
        for cert in cert_keywords:
            if cert in text.upper():
                certifications.append(cert)
        
        # 提取认证相关描述
        cert_patterns = [
            r'certification[:\s]*([^\n]+)',
            r'certificate[:\s]*([^\n]+)',
            r'standard[:\s]*([^\n]+)'
        ]
        
        for pattern in cert_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                cert = match.strip()
                if len(cert) > 2:
                    certifications.append(cert)
        
        return list(set(certifications))
    
    def _extract_trade_terms(self, text: str) -> List[str]:
        """提取贸易条款"""
        trade_terms = []
        
        # 国际贸易术语
        incoterms = ['EXW', 'FCA', 'CPT', 'CIP', 'DAT', 'DAP', 'DDP', 'FAS', 'FOB', 'CFR', 'CIF']
        
        for term in incoterms:
            if term in text.upper():
                trade_terms.append(term)
        
        return trade_terms
    
    def _calculate_confidence(self, extracted_data: Dict[str, Any]) -> float:
        """计算置信度"""
        confidence = 0.0
        
        if extracted_data.get('price_information'):
            confidence += 0.25
        if extracted_data.get('payment_terms'):
            confidence += 0.2
        if extracted_data.get('delivery_terms'):
            confidence += 0.15
        if extracted_data.get('moq_information'):
            confidence += 0.15
        if extracted_data.get('lead_time'):
            confidence += 0.15
        if extracted_data.get('certifications'):
            confidence += 0.1
        
        return min(confidence, 1.0)

class SentimentAnalysisAgent(BaseExtractionAgent):
    """情感分析Agent"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("SentimentAnalyzer", config)
    
    def _initialize_models(self):
        """初始化情感分析模型"""
        try:
            if SentimentIntensityAnalyzer:
                self.vader_analyzer = SentimentIntensityAnalyzer()
            else:
                self.vader_analyzer = None
                
            # 尝试加载Transformers情感分析模型
            if pipeline:
                try:
                    self.transformer_analyzer = pipeline(
                        "sentiment-analysis",
                        model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                        return_all_scores=True
                    )
                except Exception:
                    self.transformer_analyzer = None
            else:
                self.transformer_analyzer = None
                
        except Exception as e:
            self.logger.error(f"初始化情感分析模型失败: {str(e)}")
            self.vader_analyzer = None
            self.transformer_analyzer = None
    
    def extract(self, email_content: str, email_subject: str = "") -> ExtractionResult:
        """分析情感和购买意向"""
        start_time = datetime.now()
        errors = []
        
        try:
            full_text = f"{email_subject} {email_content}"
            cleaned_text = self._preprocess_text(full_text)
            
            extracted_data = {
                'sentiment_scores': self._analyze_sentiment(cleaned_text),
                'urgency_level': self._analyze_urgency(cleaned_text),
                'purchase_intent': self._analyze_purchase_intent(cleaned_text),
                'emotional_indicators': self._extract_emotional_indicators(cleaned_text),
                'communication_tone': self._analyze_communication_tone(cleaned_text)
            }
            
            confidence = self._calculate_confidence(extracted_data)
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return ExtractionResult(
                agent_name=self.name,
                extracted_data=extracted_data,
                confidence=confidence,
                processing_time=processing_time,
                errors=errors
            )
            
        except Exception as e:
            errors.append(f"情感分析失败: {str(e)}")
            self.logger.error(f"情感分析失败: {str(e)}")
            
            processing_time = (datetime.now() - start_time).total_seconds()
            return ExtractionResult(
                agent_name=self.name,
                extracted_data={},
                confidence=0.0,
                processing_time=processing_time,
                errors=errors
            )
    
    def _analyze_sentiment(self, text: str) -> Dict[str, float]:
        """分析情感倾向"""
        sentiment_scores = {
            'compound': 0.0,
            'positive': 0.0,
            'negative': 0.0,
            'neutral': 0.0
        }
        
        # 使用VADER情感分析
        if self.vader_analyzer:
            try:
                scores = self.vader_analyzer.polarity_scores(text)
                sentiment_scores.update(scores)
            except Exception as e:
                self.logger.warning(f"VADER情感分析失败: {str(e)}")
        
        # 使用Transformers模型
        if self.transformer_analyzer:
            try:
                results = self.transformer_analyzer(text[:512])  # 限制长度
                for result in results[0]:  # 取第一个结果
                    label = result['label'].lower()
                    score = result['score']
                    if 'positive' in label:
                        sentiment_scores['positive'] = max(sentiment_scores['positive'], score)
                    elif 'negative' in label:
                        sentiment_scores['negative'] = max(sentiment_scores['negative'], score)
                    else:
                        sentiment_scores['neutral'] = max(sentiment_scores['neutral'], score)
            except Exception as e:
                self.logger.warning(f"Transformers情感分析失败: {str(e)}")
        
        return sentiment_scores
    
    def _analyze_urgency(self, text: str) -> str:
        """分析紧急程度"""
        urgency_keywords = {
            'urgent': ['urgent', 'asap', 'immediately', 'rush', 'emergency'],
            'high': ['soon', 'quickly', 'fast', 'priority', 'important'],
            'medium': ['need', 'want', 'looking for', 'interested'],
            'low': ['maybe', 'consider', 'think about', 'possible']
        }
        
        text_lower = text.lower()
        urgency_scores = {}
        
        for level, keywords in urgency_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            urgency_scores[level] = score
        
        # 返回得分最高的紧急程度
        if urgency_scores['urgent'] > 0:
            return 'urgent'
        elif urgency_scores['high'] > urgency_scores['medium']:
            return 'high'
        elif urgency_scores['medium'] > urgency_scores['low']:
            return 'medium'
        else:
            return 'low'
    
    def _analyze_purchase_intent(self, text: str) -> float:
        """分析购买意向强度"""
        intent_keywords = {
            'high': ['buy', 'purchase', 'order', 'need to buy', 'want to order', 'ready to buy'],
            'medium': ['interested', 'consider', 'looking for', 'need', 'require'],
            'low': ['inquiry', 'information', 'details', 'quote', 'price']
        }
        
        text_lower = text.lower()
        intent_score = 0.0
        
        # 高意向关键词
        high_count = sum(1 for keyword in intent_keywords['high'] if keyword in text_lower)
        intent_score += high_count * 0.8
        
        # 中等意向关键词
        medium_count = sum(1 for keyword in intent_keywords['medium'] if keyword in text_lower)
        intent_score += medium_count * 0.5
        
        # 低意向关键词
        low_count = sum(1 for keyword in intent_keywords['low'] if keyword in text_lower)
        intent_score += low_count * 0.2
        
        # 标准化到0-1范围
        return min(intent_score / 5.0, 1.0)
    
    def _extract_emotional_indicators(self, text: str) -> List[str]:
        """提取情感指标"""
        emotional_indicators = []
        
        # 积极情感词
        positive_words = ['excellent', 'great', 'good', 'satisfied', 'happy', 'pleased']
        # 消极情感词
        negative_words = ['bad', 'poor', 'disappointed', 'unsatisfied', 'problem', 'issue']
        # 中性词
        neutral_words = ['okay', 'fine', 'acceptable', 'standard', 'normal']
        
        text_lower = text.lower()
        
        for word in positive_words:
            if word in text_lower:
                emotional_indicators.append(f'positive: {word}')
        
        for word in negative_words:
            if word in text_lower:
                emotional_indicators.append(f'negative: {word}')
        
        for word in neutral_words:
            if word in text_lower:
                emotional_indicators.append(f'neutral: {word}')
        
        return emotional_indicators
    
    def _analyze_communication_tone(self, text: str) -> str:
        """分析沟通语调"""
        # 正式语调指标
        formal_indicators = ['dear sir', 'dear madam', 'sincerely', 'respectfully', 'kindly']
        # 非正式语调指标
        informal_indicators = ['hi', 'hello', 'thanks', 'cheers', 'best']
        # 商务语调指标
        business_indicators = ['inquiry', 'quotation', 'proposal', 'terms', 'conditions']
        
        text_lower = text.lower()
        
        formal_count = sum(1 for indicator in formal_indicators if indicator in text_lower)
        informal_count = sum(1 for indicator in informal_indicators if indicator in text_lower)
        business_count = sum(1 for indicator in business_indicators if indicator in text_lower)
        
        if business_count > max(formal_count, informal_count):
            return 'business'
        elif formal_count > informal_count:
            return 'formal'
        elif informal_count > 0:
            return 'informal'
        else:
            return 'neutral'
    
    def _calculate_confidence(self, extracted_data: Dict[str, Any]) -> float:
        """计算置信度"""
        confidence = 0.0
        
        if extracted_data.get('sentiment_scores', {}).get('compound', 0) != 0:
            confidence += 0.3
        if extracted_data.get('urgency_level'):
            confidence += 0.2
        if extracted_data.get('purchase_intent', 0) > 0:
            confidence += 0.2
        if extracted_data.get('emotional_indicators'):
            confidence += 0.15
        if extracted_data.get('communication_tone'):
            confidence += 0.15
        
        return min(confidence, 1.0)

class MultiAgentExtractor:
    """多Agent协作抽取器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化多Agent抽取器
        
        Args:
            config: 配置参数
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # 初始化各个Agent
        self.agents = {
            'customer_info': CustomerInfoExtractionAgent(config.get('customer_info', {})),
            'product_demand': ProductDemandAnalysisAgent(config.get('product_demand', {})),
            'business_condition': BusinessConditionExtractionAgent(config.get('business_condition', {})),
            'sentiment_analysis': SentimentAnalysisAgent(config.get('sentiment_analysis', {}))
        }
        
        self.logger.info("多Agent抽取器初始化完成")
    
    def extract_all(self, email_content: str, email_subject: str = "") -> Dict[str, ExtractionResult]:
        """
        使用所有Agent进行抽取
        
        Args:
            email_content: 邮件内容
            email_subject: 邮件主题
            
        Returns:
            所有Agent的抽取结果
        """
        results = {}
        
        for agent_name, agent in self.agents.items():
            try:
                self.logger.info(f"开始执行 {agent_name} 抽取")
                result = agent.extract(email_content, email_subject)
                results[agent_name] = result
                self.logger.info(f"{agent_name} 抽取完成，置信度: {result.confidence:.2f}")
            except Exception as e:
                self.logger.error(f"{agent_name} 抽取失败: {str(e)}")
                results[agent_name] = ExtractionResult(
                    agent_name=agent_name,
                    extracted_data={},
                    confidence=0.0,
                    processing_time=0.0,
                    errors=[str(e)]
                )
        
        return results
    
    def get_consolidated_result(self, results: Dict[str, ExtractionResult]) -> Dict[str, Any]:
        """
        整合所有Agent的抽取结果
        
        Args:
            results: 各Agent抽取结果
            
        Returns:
            整合后的结果
        """
        consolidated = {
            'extraction_summary': {
                'total_agents': len(results),
                'successful_agents': sum(1 for r in results.values() if r.confidence > 0),
                'average_confidence': sum(r.confidence for r in results.values()) / len(results),
                'total_processing_time': sum(r.processing_time for r in results.values())
            },
            'extracted_data': {},
            'errors': []
        }
        
        # 整合各Agent的数据
        for agent_name, result in results.items():
            consolidated['extracted_data'][agent_name] = result.extracted_data
            if result.errors:
                consolidated['errors'].extend([f"{agent_name}: {error}" for error in result.errors])
        
        return consolidated