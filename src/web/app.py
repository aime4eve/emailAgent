#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask Web应用
提供邮件智能代理系统的Web接口
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import sys
import logging
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入知识抽取相关模块
try:
    from src.knowledge_management.application.entity_extraction_service import EntityExtractionService
    from src.knowledge_management.application.ml_enhancement_service import MLEnhancementService
    from src.knowledge_management.infrastructure.ml_processor import MLProcessor
    from src.knowledge_management.infrastructure.embedding_service import EmbeddingService
    from src.knowledge_management.domain.model.extraction import EntityType, RelationType
except ImportError as e:
    logging.warning(f"知识抽取模块导入失败: {e}")
    EntityExtractionService = None
    MLEnhancementService = None

def create_app(config=None):
    """创建Flask应用实例
    
    Args:
        config: 可选的配置字典
        
    Returns:
        配置好的Flask应用实例
    """
    app = Flask(__name__)
    
    # 配置CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # 基础配置
    app.config.update({
        'SECRET_KEY': os.environ.get('SECRET_KEY', 'dev-secret-key'),
        'DEBUG': os.environ.get('FLASK_DEBUG', 'False').lower() == 'true',
        'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB max file size
        'UPLOAD_FOLDER': os.path.join(os.path.dirname(__file__), 'uploads')
    })
    
    if config:
        app.config.update(config)
    
    # 配置日志
    if not app.debug:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    # 创建上传目录
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # 注册路由
    register_routes(app)
    
    return app

def register_routes(app):
    """注册路由"""
    
    @app.route('/')
    def index():
        """主页"""
        return jsonify({
            'message': '欢迎使用邮件智能代理系统',
            'version': '1.0.0',
            'status': 'running'
        })
    
    @app.route('/api/health')
    def health_check():
        """健康检查"""
        return jsonify({
            'status': 'healthy',
            'timestamp': str(Path(__file__).stat().st_mtime)
        })
    
    @app.route('/api/extract', methods=['POST', 'OPTIONS'])
    def extract_knowledge():
        """知识抽取接口
        
        接收文本内容，返回抽取的实体和关系信息
        
        Returns:
            JSON响应包含:
            - entities: 实体列表
            - relations: 关系列表
            - statistics: 统计信息
            - processing_time: 处理时间
        """
        # 处理OPTIONS预检请求
        if request.method == 'OPTIONS':
            return jsonify({'status': 'ok'}), 200
            
        app.logger.info(f"收到知识抽取请求: {request.method} {request.url}")
        app.logger.info(f"请求头: {dict(request.headers)}")
        
        start_time = time.time()
        
        try:
            # 获取请求数据
            data = request.get_json()
            if not data:
                return jsonify({'error': '请求数据格式错误'}), 400
                
            text = data.get('text', '')
            if not text or not text.strip():
                return jsonify({'error': '文本内容不能为空'}), 400
            
            # 获取可选参数
            enable_ml_enhancement = data.get('enable_ml_enhancement', True)
            custom_entity_types = data.get('custom_entity_types', None)
            
            # 检查服务是否可用
            if EntityExtractionService is None:
                return jsonify({
                    'error': '知识抽取服务不可用',
                    'message': '请检查相关模块是否正确安装'
                }), 503
            
            # 初始化服务
            try:
                extraction_service = EntityExtractionService()
                
                if enable_ml_enhancement:
                    ml_processor = MLProcessor()
                    embedding_service = EmbeddingService()
                    ml_service = MLEnhancementService(ml_processor, embedding_service)
                else:
                    ml_service = None
                    
            except Exception as e:
                app.logger.error(f"服务初始化失败: {str(e)}")
                return jsonify({
                    'error': '服务初始化失败',
                    'message': str(e)
                }), 500
            
            # 执行实体关系抽取
            try:
                extraction_result = extraction_service.extract_from_text(
                    text=text,
                    custom_entity_types=custom_entity_types
                )
                
                # 格式化实体数据
                entities = []
                for entity in extraction_result.entities:
                    entities.append({
                        'id': entity.entity_id,
                        'text': entity.text,
                        'type': entity.entity_type.value if hasattr(entity.entity_type, 'value') else str(entity.entity_type),
                        'confidence': round(entity.confidence, 3),
                        'start_pos': entity.start_pos,
                        'end_pos': entity.end_pos,
                        'properties': entity.properties
                    })
                
                # 格式化关系数据
                relations = []
                for relation in extraction_result.relations:
                    relations.append({
                        'id': relation.relation_id,
                        'source': {
                            'id': relation.source_entity.entity_id,
                            'text': relation.source_entity.text
                        },
                        'target': {
                            'id': relation.target_entity.entity_id,
                            'text': relation.target_entity.text
                        },
                        'type': relation.relation_type.value if hasattr(relation.relation_type, 'value') else str(relation.relation_type),
                        'confidence': round(relation.confidence, 3),
                        'evidence': relation.evidence_text,
                        'properties': relation.properties
                    })
                
                # 获取统计信息
                statistics = extraction_result.get_statistics()
                
                # ML增强处理（如果启用）
                ml_enhancement_info = {}
                if ml_service and len(entities) > 0:
                    try:
                        # 这里可以添加实体对齐和语义消解
                        # 由于需要知识图谱结构，暂时跳过
                        ml_enhancement_info = {
                            'enabled': True,
                            'message': 'ML增强功能需要完整的知识图谱结构'
                        }
                    except Exception as e:
                        app.logger.warning(f"ML增强处理失败: {str(e)}")
                        ml_enhancement_info = {
                            'enabled': False,
                            'error': str(e)
                        }
                else:
                    ml_enhancement_info = {'enabled': False}
                
                # 计算总处理时间
                processing_time = time.time() - start_time
                
                # 构建响应
                result = {
                    'success': True,
                    'entities': entities,
                    'relations': relations,
                    'statistics': {
                        'entity_count': len(entities),
                        'relation_count': len(relations),
                        'entity_types': statistics.get('entity_type_counts', {}),
                        'relation_types': statistics.get('relation_type_counts', {}),
                        'text_length': len(text)
                    },
                    'processing_time': round(processing_time, 3),
                    'ml_enhancement': ml_enhancement_info,
                    'metadata': {
                        'extraction_time': round(extraction_result.processing_time, 3),
                        'custom_entity_types': custom_entity_types or {},
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                    }
                }
                
                app.logger.info(
                    f"知识抽取完成: 实体{len(entities)}个, 关系{len(relations)}个, "
                    f"耗时{processing_time:.3f}秒"
                )
                
                return jsonify(result)
                
            except Exception as e:
                app.logger.error(f"知识抽取执行失败: {str(e)}")
                return jsonify({
                    'error': '知识抽取执行失败',
                    'message': str(e)
                }), 500
            
        except Exception as e:
            app.logger.error(f"知识抽取接口异常: {str(e)}")
            return jsonify({
                 'error': '服务内部错误',
                 'message': str(e)
             }), 500
    
    @app.route('/api/extract/file', methods=['POST', 'OPTIONS'])
    def extract_from_file():
        """文件知识抽取接口
        
        接收上传的文件，返回抽取的实体和关系信息
        
        Returns:
            JSON响应包含:
            - entities: 实体列表
            - relations: 关系列表
            - statistics: 统计信息
            - processing_time: 处理时间
        """
        # 处理OPTIONS预检请求
        if request.method == 'OPTIONS':
            return jsonify({'status': 'ok'}), 200
            
        app.logger.info(f"收到文件上传请求: {request.method} {request.url}")
        app.logger.info(f"请求头: {dict(request.headers)}")
        
        start_time = time.time()
        
        try:
            # 检查是否有文件上传
            if 'file' not in request.files:
                return jsonify({'error': '没有上传文件'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': '文件名为空'}), 400
            
            # 获取可选参数
            enable_ml_enhancement = request.form.get('enable_ml_enhancement', 'true').lower() == 'true'
            
            # 检查服务是否可用
            if EntityExtractionService is None:
                return jsonify({
                    'error': '知识抽取服务不可用',
                    'message': '请检查相关模块是否正确安装'
                }), 503
            
            # 保存上传的文件
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            try:
                # 初始化服务
                extraction_service = EntityExtractionService()
                
                if enable_ml_enhancement:
                    ml_processor = MLProcessor()
                    embedding_service = EmbeddingService()
                    ml_service = MLEnhancementService(ml_processor, embedding_service)
                else:
                    ml_service = None
                
                # 执行文件抽取
                extraction_result = extraction_service.extract_from_file(file_path)
                
                # 格式化实体数据
                entities = []
                for entity in extraction_result.entities:
                    entities.append({
                        'id': entity.entity_id,
                        'text': entity.text,
                        'type': entity.entity_type.value if hasattr(entity.entity_type, 'value') else str(entity.entity_type),
                        'confidence': round(entity.confidence, 3),
                        'start_pos': entity.start_pos,
                        'end_pos': entity.end_pos,
                        'properties': entity.properties
                    })
                
                # 格式化关系数据
                relations = []
                for relation in extraction_result.relations:
                    relations.append({
                        'id': relation.relation_id,
                        'source': {
                            'id': relation.source_entity.entity_id,
                            'text': relation.source_entity.text
                        },
                        'target': {
                            'id': relation.target_entity.entity_id,
                            'text': relation.target_entity.text
                        },
                        'type': relation.relation_type.value if hasattr(relation.relation_type, 'value') else str(relation.relation_type),
                        'confidence': round(relation.confidence, 3),
                        'evidence': relation.evidence_text,
                        'properties': relation.properties
                    })
                
                # 获取统计信息
                statistics = extraction_result.get_statistics()
                
                # 计算总处理时间
                processing_time = time.time() - start_time
                
                # 构建响应
                result = {
                    'success': True,
                    'entities': entities,
                    'relations': relations,
                    'statistics': {
                        'entity_count': len(entities),
                        'relation_count': len(relations),
                        'entity_types': statistics.get('entity_type_counts', {}),
                        'relation_types': statistics.get('relation_type_counts', {}),
                        'file_info': {
                            'filename': filename,
                            'file_size': extraction_result.metadata.get('file_size', 0),
                            'file_type': extraction_result.metadata.get('file_type', 'unknown')
                        }
                    },
                    'processing_time': round(processing_time, 3),
                    'metadata': {
                        'extraction_time': round(extraction_result.processing_time, 3),
                        'document_id': extraction_result.document_id,
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                    }
                }
                
                app.logger.info(
                    f"文件知识抽取完成: {filename}, 实体{len(entities)}个, 关系{len(relations)}个, "
                    f"耗时{processing_time:.3f}秒"
                )
                
                return jsonify(result)
                
            finally:
                # 清理上传的文件
                try:
                    os.remove(file_path)
                except:
                    pass
            
        except Exception as e:
            app.logger.error(f"文件知识抽取接口异常: {str(e)}")
            return jsonify({
                'error': '服务内部错误',
                'message': str(e)
            }), 500
    
    @app.errorhandler(404)
    def not_found(error):
        """404错误处理"""
        return jsonify({'error': '页面未找到'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """500错误处理"""
        return jsonify({'error': '内部服务器错误'}), 500

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)