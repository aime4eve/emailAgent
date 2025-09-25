# -*- coding: utf-8 -*-
"""
数据验证工具模块

提供数据验证、格式检查、完整性验证等功能。
"""

import re
import logging
from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class ValidationResult:
    """验证结果数据类"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    metadata: Dict[str, Any]
    
@dataclass
class ValidationRule:
    """验证规则数据类"""
    field_name: str
    rule_type: str  # 'required', 'type', 'format', 'range', 'custom'
    rule_value: Any
    error_message: str
    severity: str = 'error'  # 'error', 'warning'
    
class DataValidator:
    """数据验证器类
    
    提供数据验证、格式检查、完整性验证等功能。
    """
    
    def __init__(self):
        """初始化数据验证器"""
        self.logger = logging.getLogger(__name__)
        
        # 预定义的格式验证正则表达式
        self.format_patterns = {
            'email': re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'),
            'phone': re.compile(r'^[\+]?[1-9]?\d{9,15}$'),
            'url': re.compile(r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))?)?$'),
            'ip_address': re.compile(r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'),
            'date_iso': re.compile(r'^\d{4}-\d{2}-\d{2}$'),
            'datetime_iso': re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?(?:Z|[+-]\d{2}:\d{2})$'),
            'uuid': re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$', re.IGNORECASE),
            'chinese_text': re.compile(r'^[\u4e00-\u9fff\s\w\d\p{P}]*$'),
            'english_text': re.compile(r'^[a-zA-Z\s\w\d\p{P}]*$'),
            'numeric': re.compile(r'^-?\d+(?:\.\d+)?$'),
            'positive_number': re.compile(r'^\d+(?:\.\d+)?$'),
            'integer': re.compile(r'^-?\d+$'),
            'positive_integer': re.compile(r'^\d+$')
        }
        
        # 数据类型映射
        self.type_mapping = {
            'string': str,
            'str': str,
            'integer': int,
            'int': int,
            'float': float,
            'number': (int, float),
            'boolean': bool,
            'bool': bool,
            'list': list,
            'array': list,
            'dict': dict,
            'object': dict,
            'datetime': datetime
        }
        
    def validate_data(self, data: Dict[str, Any], rules: List[ValidationRule]) -> ValidationResult:
        """验证数据
        
        Args:
            data: 待验证的数据
            rules: 验证规则列表
            
        Returns:
            验证结果
        """
        errors = []
        warnings = []
        metadata = {
            'validation_time': datetime.now().isoformat(),
            'total_rules': len(rules),
            'data_fields': list(data.keys()) if isinstance(data, dict) else []
        }
        
        try:
            for rule in rules:
                result = self._apply_validation_rule(data, rule)
                
                if not result['is_valid']:
                    if rule.severity == 'error':
                        errors.append(result['message'])
                    else:
                        warnings.append(result['message'])
                        
            is_valid = len(errors) == 0
            
            return ValidationResult(
                is_valid=is_valid,
                errors=errors,
                warnings=warnings,
                metadata=metadata
            )
            
        except Exception as e:
            self.logger.error(f"数据验证失败: {e}")
            return ValidationResult(
                is_valid=False,
                errors=[f"验证过程出错: {str(e)}"],
                warnings=[],
                metadata=metadata
            )
            
    def _apply_validation_rule(self, data: Dict[str, Any], rule: ValidationRule) -> Dict[str, Any]:
        """应用单个验证规则
        
        Args:
            data: 数据
            rule: 验证规则
            
        Returns:
            验证结果
        """
        try:
            field_value = data.get(rule.field_name)
            
            if rule.rule_type == 'required':
                return self._validate_required(field_value, rule)
            elif rule.rule_type == 'type':
                return self._validate_type(field_value, rule)
            elif rule.rule_type == 'format':
                return self._validate_format(field_value, rule)
            elif rule.rule_type == 'range':
                return self._validate_range(field_value, rule)
            elif rule.rule_type == 'length':
                return self._validate_length(field_value, rule)
            elif rule.rule_type == 'custom':
                return self._validate_custom(field_value, rule)
            else:
                return {
                    'is_valid': False,
                    'message': f"未知的验证规则类型: {rule.rule_type}"
                }
                
        except Exception as e:
            return {
                'is_valid': False,
                'message': f"规则应用失败: {str(e)}"
            }
            
    def _validate_required(self, value: Any, rule: ValidationRule) -> Dict[str, Any]:
        """验证必填字段"""
        if rule.rule_value and (value is None or value == "" or (isinstance(value, (list, dict)) and len(value) == 0)):
            return {
                'is_valid': False,
                'message': rule.error_message or f"字段 {rule.field_name} 是必填的"
            }
        return {'is_valid': True, 'message': ''}
        
    def _validate_type(self, value: Any, rule: ValidationRule) -> Dict[str, Any]:
        """验证数据类型"""
        if value is None:
            return {'is_valid': True, 'message': ''}  # None值跳过类型检查
            
        expected_type = self.type_mapping.get(rule.rule_value, rule.rule_value)
        
        if not isinstance(value, expected_type):
            return {
                'is_valid': False,
                'message': rule.error_message or f"字段 {rule.field_name} 类型错误，期望 {rule.rule_value}，实际 {type(value).__name__}"
            }
        return {'is_valid': True, 'message': ''}
        
    def _validate_format(self, value: Any, rule: ValidationRule) -> Dict[str, Any]:
        """验证格式"""
        if value is None or value == "":
            return {'is_valid': True, 'message': ''}  # 空值跳过格式检查
            
        if not isinstance(value, str):
            return {
                'is_valid': False,
                'message': f"字段 {rule.field_name} 必须是字符串才能进行格式验证"
            }
            
        pattern = self.format_patterns.get(rule.rule_value)
        if pattern:
            if not pattern.match(value):
                return {
                    'is_valid': False,
                    'message': rule.error_message or f"字段 {rule.field_name} 格式不正确，期望格式: {rule.rule_value}"
                }
        else:
            # 自定义正则表达式
            try:
                custom_pattern = re.compile(rule.rule_value)
                if not custom_pattern.match(value):
                    return {
                        'is_valid': False,
                        'message': rule.error_message or f"字段 {rule.field_name} 不匹配指定格式"
                    }
            except re.error:
                return {
                    'is_valid': False,
                    'message': f"无效的正则表达式: {rule.rule_value}"
                }
                
        return {'is_valid': True, 'message': ''}
        
    def _validate_range(self, value: Any, rule: ValidationRule) -> Dict[str, Any]:
        """验证数值范围"""
        if value is None:
            return {'is_valid': True, 'message': ''}
            
        if not isinstance(value, (int, float)):
            return {
                'is_valid': False,
                'message': f"字段 {rule.field_name} 必须是数值才能进行范围验证"
            }
            
        range_config = rule.rule_value
        if isinstance(range_config, dict):
            min_val = range_config.get('min')
            max_val = range_config.get('max')
            
            if min_val is not None and value < min_val:
                return {
                    'is_valid': False,
                    'message': rule.error_message or f"字段 {rule.field_name} 值 {value} 小于最小值 {min_val}"
                }
                
            if max_val is not None and value > max_val:
                return {
                    'is_valid': False,
                    'message': rule.error_message or f"字段 {rule.field_name} 值 {value} 大于最大值 {max_val}"
                }
        elif isinstance(range_config, (list, tuple)) and len(range_config) == 2:
            min_val, max_val = range_config
            if not (min_val <= value <= max_val):
                return {
                    'is_valid': False,
                    'message': rule.error_message or f"字段 {rule.field_name} 值 {value} 不在范围 [{min_val}, {max_val}] 内"
                }
                
        return {'is_valid': True, 'message': ''}
        
    def _validate_length(self, value: Any, rule: ValidationRule) -> Dict[str, Any]:
        """验证长度"""
        if value is None:
            return {'is_valid': True, 'message': ''}
            
        if not hasattr(value, '__len__'):
            return {
                'is_valid': False,
                'message': f"字段 {rule.field_name} 不支持长度验证"
            }
            
        length = len(value)
        length_config = rule.rule_value
        
        if isinstance(length_config, dict):
            min_len = length_config.get('min')
            max_len = length_config.get('max')
            
            if min_len is not None and length < min_len:
                return {
                    'is_valid': False,
                    'message': rule.error_message or f"字段 {rule.field_name} 长度 {length} 小于最小长度 {min_len}"
                }
                
            if max_len is not None and length > max_len:
                return {
                    'is_valid': False,
                    'message': rule.error_message or f"字段 {rule.field_name} 长度 {length} 大于最大长度 {max_len}"
                }
        elif isinstance(length_config, (list, tuple)) and len(length_config) == 2:
            min_len, max_len = length_config
            if not (min_len <= length <= max_len):
                return {
                    'is_valid': False,
                    'message': rule.error_message or f"字段 {rule.field_name} 长度 {length} 不在范围 [{min_len}, {max_len}] 内"
                }
        elif isinstance(length_config, int):
            if length != length_config:
                return {
                    'is_valid': False,
                    'message': rule.error_message or f"字段 {rule.field_name} 长度 {length} 不等于期望长度 {length_config}"
                }
                
        return {'is_valid': True, 'message': ''}
        
    def _validate_custom(self, value: Any, rule: ValidationRule) -> Dict[str, Any]:
        """自定义验证"""
        try:
            if callable(rule.rule_value):
                result = rule.rule_value(value)
                if isinstance(result, bool):
                    if not result:
                        return {
                            'is_valid': False,
                            'message': rule.error_message or f"字段 {rule.field_name} 自定义验证失败"
                        }
                elif isinstance(result, dict):
                    return result
                else:
                    return {
                        'is_valid': False,
                        'message': f"自定义验证函数返回值格式错误"
                    }
            else:
                return {
                    'is_valid': False,
                    'message': f"自定义验证规则必须是可调用对象"
                }
                
        except Exception as e:
            return {
                'is_valid': False,
                'message': f"自定义验证执行失败: {str(e)}"
            }
            
        return {'is_valid': True, 'message': ''}
        
    def validate_email_data(self, email_data: Dict[str, Any]) -> ValidationResult:
        """验证邮件数据
        
        Args:
            email_data: 邮件数据
            
        Returns:
            验证结果
        """
        rules = [
            ValidationRule('sender', 'required', True, '发件人不能为空'),
            ValidationRule('sender', 'format', 'email', '发件人邮箱格式不正确'),
            ValidationRule('subject', 'required', True, '邮件主题不能为空'),
            ValidationRule('subject', 'length', {'min': 1, 'max': 200}, '邮件主题长度应在1-200字符之间'),
            ValidationRule('content', 'required', True, '邮件内容不能为空'),
            ValidationRule('content', 'length', {'min': 1, 'max': 10000}, '邮件内容长度应在1-10000字符之间'),
            ValidationRule('timestamp', 'type', 'datetime', '时间戳格式不正确')
        ]
        
        return self.validate_data(email_data, rules)
        
    def validate_customer_data(self, customer_data: Dict[str, Any]) -> ValidationResult:
        """验证客户数据
        
        Args:
            customer_data: 客户数据
            
        Returns:
            验证结果
        """
        rules = [
            ValidationRule('customer_id', 'required', True, '客户ID不能为空'),
            ValidationRule('customer_id', 'type', 'string', '客户ID必须是字符串'),
            ValidationRule('name', 'required', True, '客户名称不能为空'),
            ValidationRule('name', 'length', {'min': 1, 'max': 100}, '客户名称长度应在1-100字符之间'),
            ValidationRule('email', 'format', 'email', '客户邮箱格式不正确', 'warning'),
            ValidationRule('phone', 'format', 'phone', '客户电话格式不正确', 'warning'),
            ValidationRule('industry', 'type', 'string', '行业信息必须是字符串', 'warning'),
            ValidationRule('company_size', 'type', 'string', '公司规模必须是字符串', 'warning')
        ]
        
        return self.validate_data(customer_data, rules)
        
    def validate_product_data(self, product_data: Dict[str, Any]) -> ValidationResult:
        """验证产品数据
        
        Args:
            product_data: 产品数据
            
        Returns:
            验证结果
        """
        rules = [
            ValidationRule('product_id', 'required', True, '产品ID不能为空'),
            ValidationRule('product_id', 'type', 'string', '产品ID必须是字符串'),
            ValidationRule('name', 'required', True, '产品名称不能为空'),
            ValidationRule('name', 'length', {'min': 1, 'max': 200}, '产品名称长度应在1-200字符之间'),
            ValidationRule('category', 'type', 'string', '产品类别必须是字符串', 'warning'),
            ValidationRule('price', 'type', 'number', '产品价格必须是数值', 'warning'),
            ValidationRule('price', 'range', {'min': 0}, '产品价格不能为负数', 'warning'),
            ValidationRule('description', 'length', {'max': 1000}, '产品描述长度不能超过1000字符', 'warning')
        ]
        
        return self.validate_data(product_data, rules)
        
    def validate_graph_data(self, graph_data: Dict[str, Any]) -> ValidationResult:
        """验证图谱数据
        
        Args:
            graph_data: 图谱数据
            
        Returns:
            验证结果
        """
        rules = [
            ValidationRule('nodes', 'required', True, '节点数据不能为空'),
            ValidationRule('nodes', 'type', 'list', '节点数据必须是列表'),
            ValidationRule('edges', 'required', True, '边数据不能为空'),
            ValidationRule('edges', 'type', 'list', '边数据必须是列表')
        ]
        
        result = self.validate_data(graph_data, rules)
        
        # 验证节点和边的具体结构
        if result.is_valid:
            nodes = graph_data.get('nodes', [])
            edges = graph_data.get('edges', [])
            
            # 验证节点结构
            for i, node in enumerate(nodes):
                node_rules = [
                    ValidationRule('id', 'required', True, f'节点{i}的ID不能为空'),
                    ValidationRule('type', 'type', 'string', f'节点{i}的类型必须是字符串', 'warning')
                ]
                node_result = self.validate_data(node, node_rules)
                result.errors.extend(node_result.errors)
                result.warnings.extend(node_result.warnings)
                
            # 验证边结构
            node_ids = {node.get('id') for node in nodes}
            for i, edge in enumerate(edges):
                edge_rules = [
                    ValidationRule('source', 'required', True, f'边{i}的源节点不能为空'),
                    ValidationRule('target', 'required', True, f'边{i}的目标节点不能为空'),
                    ValidationRule('relation_type', 'type', 'string', f'边{i}的关系类型必须是字符串', 'warning')
                ]
                edge_result = self.validate_data(edge, edge_rules)
                result.errors.extend(edge_result.errors)
                result.warnings.extend(edge_result.warnings)
                
                # 验证边的节点引用
                source = edge.get('source')
                target = edge.get('target')
                if source and source not in node_ids:
                    result.errors.append(f'边{i}的源节点{source}不存在')
                if target and target not in node_ids:
                    result.errors.append(f'边{i}的目标节点{target}不存在')
                    
            result.is_valid = len(result.errors) == 0
            
        return result
        
    def validate_api_request(self, request_data: Dict[str, Any], endpoint: str) -> ValidationResult:
        """验证API请求数据
        
        Args:
            request_data: 请求数据
            endpoint: API端点
            
        Returns:
            验证结果
        """
        if endpoint == '/api/v1/extraction/analyze':
            rules = [
                ValidationRule('text', 'required', True, '文本内容不能为空'),
                ValidationRule('text', 'type', 'string', '文本内容必须是字符串'),
                ValidationRule('text', 'length', {'min': 1, 'max': 50000}, '文本长度应在1-50000字符之间'),
                ValidationRule('source_id', 'type', 'string', '来源ID必须是字符串', 'warning')
            ]
        elif endpoint == '/api/v1/algorithms/centrality':
            rules = [
                ValidationRule('algorithm', 'type', 'string', '算法类型必须是字符串', 'warning'),
                ValidationRule('top_k', 'type', 'integer', 'top_k必须是整数', 'warning'),
                ValidationRule('top_k', 'range', {'min': 1, 'max': 100}, 'top_k应在1-100之间', 'warning')
            ]
        elif endpoint == '/api/v1/insights/customer-analysis':
            rules = [
                ValidationRule('customer_id', 'type', 'string', '客户ID必须是字符串', 'warning'),
                ValidationRule('analysis_type', 'type', 'string', '分析类型必须是字符串', 'warning')
            ]
        else:
            # 通用验证
            rules = []
            
        return self.validate_data(request_data, rules)
        
    def validate_configuration(self, config_data: Dict[str, Any]) -> ValidationResult:
        """验证配置数据
        
        Args:
            config_data: 配置数据
            
        Returns:
            验证结果
        """
        rules = [
            # Neo4j配置验证
            ValidationRule('neo4j', 'required', True, 'Neo4j配置不能为空'),
            ValidationRule('neo4j', 'type', 'dict', 'Neo4j配置必须是字典'),
            
            # Redis配置验证
            ValidationRule('redis', 'required', True, 'Redis配置不能为空'),
            ValidationRule('redis', 'type', 'dict', 'Redis配置必须是字典'),
            
            # API配置验证
            ValidationRule('api', 'required', True, 'API配置不能为空'),
            ValidationRule('api', 'type', 'dict', 'API配置必须是字典')
        ]
        
        result = self.validate_data(config_data, rules)
        
        # 验证具体配置项
        if result.is_valid:
            # 验证Neo4j配置
            neo4j_config = config_data.get('neo4j', {})
            neo4j_rules = [
                ValidationRule('uri', 'required', True, 'Neo4j URI不能为空'),
                ValidationRule('uri', 'type', 'string', 'Neo4j URI必须是字符串'),
                ValidationRule('username', 'required', True, 'Neo4j用户名不能为空'),
                ValidationRule('password', 'required', True, 'Neo4j密码不能为空')
            ]
            neo4j_result = self.validate_data(neo4j_config, neo4j_rules)
            result.errors.extend(neo4j_result.errors)
            result.warnings.extend(neo4j_result.warnings)
            
            # 验证Redis配置
            redis_config = config_data.get('redis', {})
            redis_rules = [
                ValidationRule('host', 'required', True, 'Redis主机不能为空'),
                ValidationRule('host', 'type', 'string', 'Redis主机必须是字符串'),
                ValidationRule('port', 'required', True, 'Redis端口不能为空'),
                ValidationRule('port', 'type', 'integer', 'Redis端口必须是整数'),
                ValidationRule('port', 'range', {'min': 1, 'max': 65535}, 'Redis端口范围应在1-65535之间')
            ]
            redis_result = self.validate_data(redis_config, redis_rules)
            result.errors.extend(redis_result.errors)
            result.warnings.extend(redis_result.warnings)
            
            result.is_valid = len(result.errors) == 0
            
        return result
        
    def sanitize_data(self, data: Any, data_type: str = 'auto') -> Any:
        """数据清理和标准化
        
        Args:
            data: 原始数据
            data_type: 数据类型
            
        Returns:
            清理后的数据
        """
        try:
            if data is None:
                return None
                
            if data_type == 'string' or (data_type == 'auto' and isinstance(data, str)):
                # 字符串清理
                data = str(data).strip()
                # 移除控制字符
                data = ''.join(char for char in data if ord(char) >= 32 or char in '\n\r\t')
                return data
                
            elif data_type == 'email' or (data_type == 'auto' and isinstance(data, str) and '@' in data):
                # 邮箱清理
                data = str(data).strip().lower()
                return data
                
            elif data_type == 'number' or (data_type == 'auto' and isinstance(data, (int, float))):
                # 数值清理
                if isinstance(data, str):
                    data = data.strip().replace(',', '')
                    try:
                        return float(data) if '.' in data else int(data)
                    except ValueError:
                        return None
                return data
                
            elif data_type == 'list' or (data_type == 'auto' and isinstance(data, list)):
                # 列表清理
                return [self.sanitize_data(item, 'auto') for item in data if item is not None]
                
            elif data_type == 'dict' or (data_type == 'auto' and isinstance(data, dict)):
                # 字典清理
                return {k: self.sanitize_data(v, 'auto') for k, v in data.items() if v is not None}
                
            else:
                return data
                
        except Exception as e:
            self.logger.error(f"数据清理失败: {e}")
            return data
            
    def check_data_completeness(self, data: Dict[str, Any], required_fields: List[str]) -> Dict[str, Any]:
        """检查数据完整性
        
        Args:
            data: 数据
            required_fields: 必需字段列表
            
        Returns:
            完整性检查结果
        """
        try:
            missing_fields = []
            empty_fields = []
            present_fields = []
            
            for field in required_fields:
                if field not in data:
                    missing_fields.append(field)
                elif data[field] is None or data[field] == "" or (isinstance(data[field], (list, dict)) and len(data[field]) == 0):
                    empty_fields.append(field)
                else:
                    present_fields.append(field)
                    
            completeness_score = len(present_fields) / len(required_fields) if required_fields else 1.0
            
            return {
                'is_complete': len(missing_fields) == 0 and len(empty_fields) == 0,
                'completeness_score': round(completeness_score, 2),
                'missing_fields': missing_fields,
                'empty_fields': empty_fields,
                'present_fields': present_fields,
                'total_required': len(required_fields),
                'total_present': len(present_fields)
            }
            
        except Exception as e:
            self.logger.error(f"完整性检查失败: {e}")
            return {
                'is_complete': False,
                'completeness_score': 0.0,
                'error': str(e)
            }
            
    def validate_json_schema(self, data: Any, schema: Dict[str, Any]) -> ValidationResult:
        """验证JSON模式
        
        Args:
            data: 待验证数据
            schema: JSON模式
            
        Returns:
            验证结果
        """
        # 简化的JSON模式验证实现
        errors = []
        warnings = []
        
        try:
            def validate_object(obj, obj_schema, path=""):
                if obj_schema.get('type') == 'object':
                    if not isinstance(obj, dict):
                        errors.append(f"{path}: 期望对象类型，实际 {type(obj).__name__}")
                        return
                        
                    properties = obj_schema.get('properties', {})
                    required = obj_schema.get('required', [])
                    
                    # 检查必需属性
                    for req_prop in required:
                        if req_prop not in obj:
                            errors.append(f"{path}.{req_prop}: 必需属性缺失")
                            
                    # 验证属性
                    for prop, prop_schema in properties.items():
                        if prop in obj:
                            validate_object(obj[prop], prop_schema, f"{path}.{prop}")
                            
                elif obj_schema.get('type') == 'array':
                    if not isinstance(obj, list):
                        errors.append(f"{path}: 期望数组类型，实际 {type(obj).__name__}")
                        return
                        
                    items_schema = obj_schema.get('items', {})
                    for i, item in enumerate(obj):
                        validate_object(item, items_schema, f"{path}[{i}]")
                        
                elif obj_schema.get('type') == 'string':
                    if not isinstance(obj, str):
                        errors.append(f"{path}: 期望字符串类型，实际 {type(obj).__name__}")
                        
                elif obj_schema.get('type') == 'number':
                    if not isinstance(obj, (int, float)):
                        errors.append(f"{path}: 期望数值类型，实际 {type(obj).__name__}")
                        
                elif obj_schema.get('type') == 'boolean':
                    if not isinstance(obj, bool):
                        errors.append(f"{path}: 期望布尔类型，实际 {type(obj).__name__}")
                        
            validate_object(data, schema)
            
            return ValidationResult(
                is_valid=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                metadata={'schema_validation': True}
            )
            
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                errors=[f"JSON模式验证失败: {str(e)}"],
                warnings=[],
                metadata={'error': str(e)}
            )