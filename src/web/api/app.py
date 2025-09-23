#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask API应用程序
外贸询盘知识图谱系统的RESTful API服务
"""

from flask import Flask, jsonify, request, g
from flask_cors import CORS
from flask_restful import Api
from flask_jwt_extended import JWTManager
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Any

# 导入路由蓝图
from .routes.customers import customers_bp
from .routes.analytics import analytics_bp
from .routes.ontologies import ontologies_bp

# 导入配置和服务
from ...shared.config import Config
from ...shared.database.arango_service import ArangoDBService

def create_app(config_name: str = 'development') -> Flask:
    """
    创建Flask应用程序
    
    Args:
        config_name: 配置环境名称
        
    Returns:
        Flask应用实例
    """
    app = Flask(__name__)
    
    # 配置应用
    configure_app(app, config_name)
    
    # 配置日志
    configure_logging(app)
    
    # 配置CORS
    configure_cors(app)
    
    # 配置JWT
    configure_jwt(app)
    
    # 注册蓝图
    register_blueprints(app)
    
    # 注册中间件
    register_middleware(app)
    
    # 注册错误处理器
    register_error_handlers(app)
    
    # 注册健康检查
    register_health_check(app)
    
    return app

def configure_app(app: Flask, config_name: str) -> None:
    """
    配置应用程序设置
    
    Args:
        app: Flask应用实例
        config_name: 配置环境名称
    """
    # 基础配置
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    
    # 数据库配置
    app.config['ARANGO_HOST'] = os.environ.get('ARANGO_HOST', 'localhost')
    app.config['ARANGO_PORT'] = int(os.environ.get('ARANGO_PORT', 8529))
    app.config['ARANGO_DATABASE'] = os.environ.get('ARANGO_DATABASE', 'inquiry_knowledge_graph')
    app.config['ARANGO_USERNAME'] = os.environ.get('ARANGO_USERNAME', 'root')
    app.config['ARANGO_PASSWORD'] = os.environ.get('ARANGO_PASSWORD', '')
    
    # API配置
    app.config['API_VERSION'] = 'v1'
    app.config['API_TITLE'] = '外贸询盘知识图谱系统API'
    app.config['API_DESCRIPTION'] = '提供客户管理、需求分析、智能推荐等功能的RESTful API'
    
    # 分页配置
    app.config['DEFAULT_PAGE_SIZE'] = 10
    app.config['MAX_PAGE_SIZE'] = 100
    
    # 缓存配置
    app.config['CACHE_TYPE'] = 'simple'
    app.config['CACHE_DEFAULT_TIMEOUT'] = 300
    
    # 环境特定配置
    if config_name == 'production':
        app.config['DEBUG'] = False
        app.config['TESTING'] = False
        app.config['LOG_LEVEL'] = logging.INFO
    elif config_name == 'testing':
        app.config['DEBUG'] = False
        app.config['TESTING'] = True
        app.config['LOG_LEVEL'] = logging.DEBUG
    else:  # development
        app.config['DEBUG'] = True
        app.config['TESTING'] = False
        app.config['LOG_LEVEL'] = logging.DEBUG

def configure_logging(app: Flask) -> None:
    """
    配置日志系统
    
    Args:
        app: Flask应用实例
    """
    log_level = app.config.get('LOG_LEVEL', logging.INFO)
    
    # 配置根日志记录器
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('logs/api.log') if os.path.exists('logs') else logging.NullHandler()
        ]
    )
    
    # 配置Flask应用日志
    app.logger.setLevel(log_level)
    
    # 配置第三方库日志级别
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)

def configure_cors(app: Flask) -> None:
    """
    配置跨域资源共享
    
    Args:
        app: Flask应用实例
    """
    CORS(app, 
         origins=['http://localhost:3000', 'http://localhost:5173'],  # 前端开发服务器
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         allow_headers=['Content-Type', 'Authorization'],
         supports_credentials=True)

def configure_jwt(app: Flask) -> None:
    """
    配置JWT认证
    
    Args:
        app: Flask应用实例
    """
    jwt = JWTManager(app)
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'error': 'Token已过期',
            'message': '请重新登录获取新的访问令牌'
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'error': 'Token无效',
            'message': '提供的访问令牌无效'
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'error': '缺少访问令牌',
            'message': '请在请求头中提供有效的访问令牌'
        }), 401

def register_blueprints(app: Flask) -> None:
    """
    注册蓝图路由
    
    Args:
        app: Flask应用实例
    """
    # 注册API路由蓝图
    app.register_blueprint(customers_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(ontologies_bp)
    
    app.logger.info('已注册所有API路由蓝图')

def register_middleware(app: Flask) -> None:
    """
    注册中间件
    
    Args:
        app: Flask应用实例
    """
    @app.before_request
    def before_request():
        """请求前处理"""
        # 记录请求信息
        app.logger.debug(f'收到请求: {request.method} {request.url}')
        
        # 设置请求开始时间
        g.start_time = datetime.now()
        
        # 初始化数据库连接（如果需要）
        try:
            if not hasattr(g, 'arango_service'):
                g.arango_service = ArangoDBService()
        except Exception as e:
            app.logger.error(f'初始化数据库连接失败: {str(e)}')
    
    @app.after_request
    def after_request(response):
        """请求后处理"""
        # 计算请求处理时间
        if hasattr(g, 'start_time'):
            duration = (datetime.now() - g.start_time).total_seconds()
            response.headers['X-Response-Time'] = f'{duration:.3f}s'
        
        # 添加API版本信息
        response.headers['X-API-Version'] = app.config.get('API_VERSION', 'v1')
        
        # 记录响应信息
        app.logger.debug(f'响应状态: {response.status_code}')
        
        return response
    
    @app.teardown_appcontext
    def teardown_db(error):
        """清理数据库连接"""
        if hasattr(g, 'arango_service'):
            # 这里可以添加数据库连接清理逻辑
            pass

def register_error_handlers(app: Flask) -> None:
    """
    注册错误处理器
    
    Args:
        app: Flask应用实例
    """
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'error': '请求错误',
            'message': '请求参数或格式不正确',
            'status_code': 400
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'error': '未授权',
            'message': '需要有效的身份验证',
            'status_code': 401
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'error': '禁止访问',
            'message': '没有权限访问此资源',
            'status_code': 403
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': '资源不存在',
            'message': '请求的资源未找到',
            'status_code': 404
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'error': '方法不允许',
            'message': '请求方法不被允许',
            'status_code': 405
        }), 405
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        return jsonify({
            'error': '请求频率超限',
            'message': '请求过于频繁，请稍后再试',
            'status_code': 429
        }), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'服务器内部错误: {str(error)}')
        return jsonify({
            'error': '服务器内部错误',
            'message': '服务器遇到了一个错误，无法完成请求',
            'status_code': 500
        }), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        app.logger.error(f'未处理的异常: {str(error)}', exc_info=True)
        return jsonify({
            'error': '服务器错误',
            'message': '发生了未预期的错误',
            'status_code': 500
        }), 500

def register_health_check(app: Flask) -> None:
    """
    注册健康检查端点
    
    Args:
        app: Flask应用实例
    """
    @app.route('/health', methods=['GET'])
    def health_check():
        """健康检查端点"""
        try:
            # 检查数据库连接
            arango_service = ArangoDBService()
            db_status = 'healthy' if arango_service.db else 'unhealthy'
            
            health_data = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'version': app.config.get('API_VERSION', 'v1'),
                'services': {
                    'database': db_status,
                    'api': 'healthy'
                },
                'uptime': 'N/A'  # 可以添加应用启动时间计算
            }
            
            return jsonify(health_data), 200
            
        except Exception as e:
            app.logger.error(f'健康检查失败: {str(e)}')
            return jsonify({
                'status': 'unhealthy',
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }), 503
    
    @app.route('/api/info', methods=['GET'])
    def api_info():
        """API信息端点"""
        return jsonify({
            'title': app.config.get('API_TITLE', 'API'),
            'description': app.config.get('API_DESCRIPTION', ''),
            'version': app.config.get('API_VERSION', 'v1'),
            'endpoints': {
                'customers': '/api/customers',
                'analytics': '/api/analytics',
                'health': '/health',
                'info': '/api/info'
            },
            'documentation': '/api/docs',  # 如果有API文档
            'timestamp': datetime.now().isoformat()
        }), 200

# 创建应用实例
def create_production_app():
    """创建生产环境应用"""
    return create_app('production')

def create_development_app():
    """创建开发环境应用"""
    return create_app('development')

def create_testing_app():
    """创建测试环境应用"""
    return create_app('testing')

# 如果直接运行此文件
if __name__ == '__main__':
    app = create_development_app()
    
    # 确保日志目录存在
    os.makedirs('logs', exist_ok=True)
    
    app.logger.info('启动开发服务器')
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=True,
        threaded=True
    )