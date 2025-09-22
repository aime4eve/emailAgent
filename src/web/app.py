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

# 导入本体管理相关模块
try:
    from src.knowledge_management.ontology_service import OntologyService
    from src.knowledge_management.ontology_model import Ontology
except ImportError as e:
    logging.warning(f"本体管理模块导入失败: {e}")
    OntologyService = None
    Ontology = None

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
    
    # 本体管理API路由
    @app.route('/api/ontologies', methods=['GET', 'OPTIONS'])
    def get_ontologies():
        """获取本体列表
        
        查询参数:
        - page: 页码 (默认1)
        - page_size: 每页大小 (默认10)
        - search: 搜索关键词
        - tags: 标签过滤 (逗号分隔)
        
        Returns:
            JSON响应包含本体列表和分页信息
        """
        # 处理OPTIONS预检请求
        if request.method == 'OPTIONS':
            return jsonify({'status': 'ok'}), 200
            
        app.logger.info(f"收到获取本体列表请求: {request.method} {request.url}")
        
        try:
            # 检查服务是否可用
            if OntologyService is None:
                return jsonify({
                    'error': '本体管理服务不可用',
                    'message': '请检查相关模块是否正确安装'
                }), 503
            
            # 获取查询参数
            page = int(request.args.get('page', 1))
            page_size = int(request.args.get('page_size', 10))
            search_term = request.args.get('search', None)
            tags_str = request.args.get('tags', None)
            tags = tags_str.split(',') if tags_str else None
            
            # 初始化服务
            ontology_service = OntologyService()
            
            # 获取本体列表
            result = ontology_service.list_ontologies(
                page=page,
                page_size=page_size,
                search_term=search_term,
                tags=tags
            )
            
            app.logger.info(f"返回本体列表: {result['total']}个本体")
            return jsonify(result)
            
        except Exception as e:
            app.logger.error(f"获取本体列表失败: {str(e)}")
            return jsonify({
                'error': '获取本体列表失败',
                'message': str(e)
            }), 500
    
    @app.route('/api/ontologies/<ontology_id>', methods=['GET', 'OPTIONS'])
    def get_ontology(ontology_id):
        """获取特定本体详情
        
        Args:
            ontology_id: 本体ID
            
        Returns:
            JSON响应包含本体详细信息
        """
        # 处理OPTIONS预检请求
        if request.method == 'OPTIONS':
            return jsonify({'status': 'ok'}), 200
            
        app.logger.info(f"收到获取本体详情请求: {ontology_id}")
        
        try:
            # 检查服务是否可用
            if OntologyService is None:
                return jsonify({
                    'error': '本体管理服务不可用',
                    'message': '请检查相关模块是否正确安装'
                }), 503
            
            # 初始化服务
            ontology_service = OntologyService()
            
            # 获取本体
            ontology = ontology_service.get_ontology(ontology_id)
            if not ontology:
                return jsonify({'error': '本体不存在'}), 404
            
            app.logger.info(f"返回本体详情: {ontology.name}")
            return jsonify(ontology.to_dict())
            
        except Exception as e:
            app.logger.error(f"获取本体详情失败: {str(e)}")
            return jsonify({
                'error': '获取本体详情失败',
                'message': str(e)
            }), 500
    
    @app.route('/api/ontologies', methods=['POST'])
    def create_ontology():
        """创建新本体
        
        请求体:
        - name: 本体名称 (必需)
        - description: 本体描述
        - version: 版本号
        - namespace: 命名空间
        - author: 作者
        - tags: 标签列表
        - entity_types: 实体类型列表
        - relation_types: 关系类型列表
        
        Returns:
            JSON响应包含创建的本体信息
        """
        app.logger.info(f"收到创建本体请求: {request.method} {request.url}")
        
        try:
            # 检查服务是否可用
            if OntologyService is None:
                return jsonify({
                    'error': '本体管理服务不可用',
                    'message': '请检查相关模块是否正确安装'
                }), 503
            
            # 获取请求数据
            data = request.get_json()
            if not data:
                return jsonify({'error': '请求数据格式错误'}), 400
            
            # 验证必需字段
            if 'name' not in data or not data['name'].strip():
                return jsonify({'error': '本体名称不能为空'}), 400
            
            # 初始化服务
            ontology_service = OntologyService()
            
            # 创建本体
            ontology = ontology_service.create_ontology(data)
            
            app.logger.info(f"本体创建成功: {ontology.name} (ID: {ontology.id})")
            return jsonify(ontology.to_dict()), 201
            
        except ValueError as e:
            app.logger.warning(f"本体创建验证失败: {str(e)}")
            return jsonify({
                'error': '本体创建验证失败',
                'message': str(e)
            }), 400
        except Exception as e:
            app.logger.error(f"创建本体失败: {str(e)}")
            return jsonify({
                'error': '创建本体失败',
                'message': str(e)
            }), 500
    
    @app.route('/api/ontologies/<ontology_id>', methods=['PUT'])
    def update_ontology(ontology_id):
        """更新本体
        
        Args:
            ontology_id: 本体ID
            
        请求体:
        - name: 本体名称
        - description: 本体描述
        - version: 版本号
        - namespace: 命名空间
        - author: 作者
        - tags: 标签列表
        - entity_types: 实体类型列表
        - relation_types: 关系类型列表
        
        Returns:
            JSON响应包含更新后的本体信息
        """
        app.logger.info(f"收到更新本体请求: {ontology_id}")
        
        try:
            # 检查服务是否可用
            if OntologyService is None:
                return jsonify({
                    'error': '本体管理服务不可用',
                    'message': '请检查相关模块是否正确安装'
                }), 503
            
            # 获取请求数据
            data = request.get_json()
            if not data:
                return jsonify({'error': '请求数据格式错误'}), 400
            
            # 初始化服务
            ontology_service = OntologyService()
            
            # 更新本体
            ontology = ontology_service.update_ontology(ontology_id, data)
            if not ontology:
                return jsonify({'error': '本体不存在'}), 404
            
            app.logger.info(f"本体更新成功: {ontology.name} (ID: {ontology.id})")
            return jsonify(ontology.to_dict())
            
        except ValueError as e:
            app.logger.warning(f"本体更新验证失败: {str(e)}")
            return jsonify({
                'error': '本体更新验证失败',
                'message': str(e)
            }), 400
        except Exception as e:
            app.logger.error(f"更新本体失败: {str(e)}")
            return jsonify({
                'error': '更新本体失败',
                'message': str(e)
            }), 500
    
    @app.route('/api/ontologies/<ontology_id>', methods=['DELETE'])
    def delete_ontology(ontology_id):
        """删除本体
        
        Args:
            ontology_id: 本体ID
            
        Returns:
            JSON响应确认删除结果
        """
        app.logger.info(f"收到删除本体请求: {ontology_id}")
        
        try:
            # 检查服务是否可用
            if OntologyService is None:
                return jsonify({
                    'error': '本体管理服务不可用',
                    'message': '请检查相关模块是否正确安装'
                }), 503
            
            # 初始化服务
            ontology_service = OntologyService()
            
            # 删除本体
            success = ontology_service.delete_ontology(ontology_id)
            if not success:
                return jsonify({'error': '本体不存在'}), 404
            
            app.logger.info(f"本体删除成功: {ontology_id}")
            return jsonify({'message': '本体删除成功'})
            
        except Exception as e:
            app.logger.error(f"删除本体失败: {str(e)}")
            return jsonify({
                'error': '删除本体失败',
                'message': str(e)
            }), 500
    
    @app.route('/api/ontologies/import', methods=['POST', 'OPTIONS'])
    def import_ontology():
        """导入本体文件
        
        请求参数:
        - file: 上传的本体文件
        - format: 文件格式 (json, owl, rdf)
        
        Returns:
            JSON响应包含导入的本体信息
        """
        # 处理OPTIONS预检请求
        if request.method == 'OPTIONS':
            return jsonify({'status': 'ok'}), 200
            
        app.logger.info(f"收到本体导入请求: {request.method} {request.url}")
        
        try:
            # 检查服务是否可用
            if OntologyService is None:
                return jsonify({
                    'error': '本体管理服务不可用',
                    'message': '请检查相关模块是否正确安装'
                }), 503
            
            # 检查是否有文件上传
            if 'file' not in request.files:
                return jsonify({'error': '没有上传文件'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': '文件名为空'}), 400
            
            # 获取文件格式
            file_format = request.form.get('format', 'json').lower()
            if file_format not in ['json', 'owl', 'rdf']:
                return jsonify({'error': '不支持的文件格式'}), 400
            
            # 保存上传的文件
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            try:
                # 初始化服务
                ontology_service = OntologyService()
                
                # 导入本体
                ontology = ontology_service.import_ontology(file_path, file_format)
                
                app.logger.info(f"本体导入成功: {ontology.name} (ID: {ontology.id})")
                return jsonify(ontology.to_dict()), 201
                
            finally:
                # 清理上传的文件
                try:
                    os.remove(file_path)
                except:
                    pass
            
        except ValueError as e:
            app.logger.warning(f"本体导入验证失败: {str(e)}")
            return jsonify({
                'error': '本体导入验证失败',
                'message': str(e)
            }), 400
        except Exception as e:
            app.logger.error(f"导入本体失败: {str(e)}")
            return jsonify({
                'error': '导入本体失败',
                'message': str(e)
            }), 500
    
    @app.route('/api/ontologies/<ontology_id>/export', methods=['GET', 'OPTIONS'])
    def export_ontology(ontology_id):
        """导出本体文件
        
        Args:
            ontology_id: 本体ID
            
        查询参数:
        - format: 导出格式 (json, owl, rdf, 默认json)
        
        Returns:
            文件下载响应或JSON错误信息
        """
        # 处理OPTIONS预检请求
        if request.method == 'OPTIONS':
            return jsonify({'status': 'ok'}), 200
            
        app.logger.info(f"收到本体导出请求: {ontology_id}")
        
        try:
            # 检查服务是否可用
            if OntologyService is None:
                return jsonify({
                    'error': '本体管理服务不可用',
                    'message': '请检查相关模块是否正确安装'
                }), 503
            
            # 获取导出格式
            export_format = request.args.get('format', 'json').lower()
            if export_format not in ['json', 'owl', 'rdf']:
                return jsonify({'error': '不支持的导出格式'}), 400
            
            # 初始化服务
            ontology_service = OntologyService()
            
            # 导出本体
            export_file_path = ontology_service.export_ontology(ontology_id, export_format)
            
            # 返回文件路径信息（实际应用中可能需要返回文件内容或下载链接）
            app.logger.info(f"本体导出成功: {export_file_path}")
            return jsonify({
                'message': '本体导出成功',
                'file_path': export_file_path,
                'format': export_format
            })
            
        except ValueError as e:
            app.logger.warning(f"本体导出失败: {str(e)}")
            return jsonify({
                'error': '本体导出失败',
                'message': str(e)
            }), 400
        except Exception as e:
            app.logger.error(f"导出本体失败: {str(e)}")
            return jsonify({
                'error': '导出本体失败',
                'message': str(e)
            }), 500
    
    @app.route('/api/ontologies/statistics', methods=['GET', 'OPTIONS'])
    def get_ontology_statistics():
        """获取本体统计信息
        
        Returns:
            JSON响应包含统计信息
        """
        # 处理OPTIONS预检请求
        if request.method == 'OPTIONS':
            return jsonify({'status': 'ok'}), 200
            
        app.logger.info(f"收到获取本体统计信息请求")
        
        try:
            # 检查服务是否可用
            if OntologyService is None:
                return jsonify({
                    'error': '本体管理服务不可用',
                    'message': '请检查相关模块是否正确安装'
                }), 503
            
            # 初始化服务
            ontology_service = OntologyService()
            
            # 获取统计信息
            statistics = ontology_service.get_ontology_statistics()
            
            app.logger.info(f"返回本体统计信息: {statistics['total_ontologies']}个本体")
            return jsonify(statistics)
            
        except Exception as e:
            app.logger.error(f"获取本体统计信息失败: {str(e)}")
            return jsonify({
                'error': '获取本体统计信息失败',
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