# -*- coding: utf-8 -*-
"""
洞察系统异常定义

定义系统中使用的各种异常类型。
"""

class InsightsException(Exception):
    """洞察系统基础异常类"""
    
    def __init__(self, message: str, error_code: str = None):
        """初始化异常
        
        Args:
            message: 异常消息
            error_code: 错误代码
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or 'INSIGHTS_ERROR'
        
    def to_dict(self):
        """转换为字典格式
        
        Returns:
            异常信息字典
        """
        return {
            'error_code': self.error_code,
            'message': self.message,
            'type': self.__class__.__name__
        }

class DatabaseConnectionError(InsightsException):
    """数据库连接异常"""
    
    def __init__(self, message: str):
        super().__init__(message, 'DB_CONNECTION_ERROR')

class ConfigurationError(InsightsException):
    """配置错误异常"""
    
    def __init__(self, message: str):
        super().__init__(message, 'CONFIG_ERROR')

class ExtractionError(InsightsException):
    """知识抽取异常"""
    
    def __init__(self, message: str):
        super().__init__(message, 'EXTRACTION_ERROR')

class GraphBuildError(InsightsException):
    """图谱构建异常"""
    
    def __init__(self, message: str):
        super().__init__(message, 'GRAPH_BUILD_ERROR')

class AlgorithmError(InsightsException):
    """算法执行异常"""
    
    def __init__(self, message: str):
        super().__init__(message, 'ALGORITHM_ERROR')

class ValidationError(InsightsException):
    """数据验证异常"""
    
    def __init__(self, message: str):
        super().__init__(message, 'VALIDATION_ERROR')

class APIError(InsightsException):
    """API调用异常"""
    
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message, 'API_ERROR')
        self.status_code = status_code
        
    def to_dict(self):
        """转换为字典格式
        
        Returns:
            异常信息字典
        """
        result = super().to_dict()
        result['status_code'] = self.status_code
        return result

class BusinessLogicError(InsightsException):
    """业务逻辑异常"""
    
    def __init__(self, message: str):
        super().__init__(message, 'BUSINESS_LOGIC_ERROR')

class ResourceNotFoundError(InsightsException):
    """资源未找到异常"""
    
    def __init__(self, resource_type: str, resource_id: str):
        message = f"{resource_type} with id '{resource_id}' not found"
        super().__init__(message, 'RESOURCE_NOT_FOUND')
        self.resource_type = resource_type
        self.resource_id = resource_id
        
    def to_dict(self):
        """转换为字典格式
        
        Returns:
            异常信息字典
        """
        result = super().to_dict()
        result.update({
            'resource_type': self.resource_type,
            'resource_id': self.resource_id
        })
        return result

class PermissionDeniedError(InsightsException):
    """权限拒绝异常"""
    
    def __init__(self, action: str, resource: str = None):
        message = f"Permission denied for action '{action}'"
        if resource:
            message += f" on resource '{resource}'"
        super().__init__(message, 'PERMISSION_DENIED')
        self.action = action
        self.resource = resource
        
    def to_dict(self):
        """转换为字典格式
        
        Returns:
            异常信息字典
        """
        result = super().to_dict()
        result.update({
            'action': self.action,
            'resource': self.resource
        })
        return result

class RateLimitExceededError(InsightsException):
    """速率限制异常"""
    
    def __init__(self, limit: int, window: int):
        message = f"Rate limit exceeded: {limit} requests per {window} seconds"
        super().__init__(message, 'RATE_LIMIT_EXCEEDED')
        self.limit = limit
        self.window = window
        
    def to_dict(self):
        """转换为字典格式
        
        Returns:
            异常信息字典
        """
        result = super().to_dict()
        result.update({
            'limit': self.limit,
            'window': self.window
        })
        return result

class TimeoutError(InsightsException):
    """超时异常"""
    
    def __init__(self, operation: str, timeout: int):
        message = f"Operation '{operation}' timed out after {timeout} seconds"
        super().__init__(message, 'TIMEOUT_ERROR')
        self.operation = operation
        self.timeout = timeout
        
    def to_dict(self):
        """转换为字典格式
        
        Returns:
            异常信息字典
        """
        result = super().to_dict()
        result.update({
            'operation': self.operation,
            'timeout': self.timeout
        })
        return result