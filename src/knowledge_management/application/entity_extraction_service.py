# -*- coding: utf-8 -*-
"""
实体关系抽取服务
整合文档解析和NLP处理功能，提供完整的实体关系抽取能力
"""

import os
import time
import logging
import uuid
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path

from ..domain.model.extraction import (
    ExtractedEntity, ExtractedRelation, ExtractionResult, 
    BatchExtractionResult, EntityType, RelationType
)
from ..infrastructure.document_parser import (
    DocumentParserFactory, DocumentParseError
)
from ..infrastructure.nlp_processor import (
    get_nlp_processor, NLPProcessorError
)


class EntityExtractionServiceError(Exception):
    """实体抽取服务异常"""
    pass


class EntityExtractionService:
    """实体关系抽取服务"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.document_parser = DocumentParserFactory()
        self.nlp_processor = None
        self._init_nlp_processor()
    
    def _init_nlp_processor(self):
        """初始化NLP处理器"""
        try:
            self.nlp_processor = get_nlp_processor()
            self.logger.info("NLP处理器初始化成功")
        except Exception as e:
            self.logger.error(f"NLP处理器初始化失败: {e}")
            raise EntityExtractionServiceError(f"NLP处理器初始化失败: {e}")
    
    def extract_from_file(self, file_path: str, 
                         custom_entity_types: Optional[Dict[str, List[str]]] = None) -> ExtractionResult:
        """从文件中抽取实体和关系
        
        Args:
            file_path: 文件路径
            custom_entity_types: 自定义实体类型和对应的关键词
            
        Returns:
            抽取结果
        """
        start_time = time.time()
        
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                raise EntityExtractionServiceError(f"文件不存在: {file_path}")
            
            self.logger.info(f"开始处理文件: {file_path}")
            
            # 解析文档
            document_data = self._parse_document(file_path)
            
            # 抽取实体和关系
            entities, relations = self._extract_entities_and_relations(
                document_data['content'], custom_entity_types
            )
            
            # 创建抽取结果
            processing_time = time.time() - start_time
            result = ExtractionResult(
                document_id=str(uuid.uuid4()),
                document_path=file_path,
                entities=entities,
                relations=relations,
                processing_time=processing_time,
                metadata={
                    'file_name': os.path.basename(file_path),
                    'file_size': document_data['metadata'].get('file_size', 0),
                    'file_type': document_data['metadata'].get('file_type', 'unknown'),
                    'content_length': len(document_data['content']),
                    'custom_entity_types': custom_entity_types or {}
                }
            )
            
            # 设置实体和关系的来源文档
            for entity in result.entities:
                entity.source_document = file_path
            
            for relation in result.relations:
                relation.source_document = file_path
            
            self.logger.info(
                f"文件处理完成: {file_path}, "
                f"实体数: {len(entities)}, 关系数: {len(relations)}, "
                f"耗时: {processing_time:.2f}秒"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"处理文件失败: {file_path}, 错误: {str(e)}")
            raise EntityExtractionServiceError(f"处理文件失败: {str(e)}")
    
    def extract_from_text(self, text: str, 
                         document_id: Optional[str] = None,
                         custom_entity_types: Optional[Dict[str, List[str]]] = None) -> ExtractionResult:
        """从文本中抽取实体和关系
        
        Args:
            text: 文本内容
            document_id: 文档标识
            custom_entity_types: 自定义实体类型和对应的关键词
            
        Returns:
            抽取结果
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"开始处理文本，长度: {len(text)}")
            
            # 抽取实体和关系
            entities, relations = self._extract_entities_and_relations(text, custom_entity_types)
            
            # 创建抽取结果
            processing_time = time.time() - start_time
            result = ExtractionResult(
                document_id=document_id or str(uuid.uuid4()),
                document_path="<text_input>",
                entities=entities,
                relations=relations,
                processing_time=processing_time,
                metadata={
                    'content_length': len(text),
                    'custom_entity_types': custom_entity_types or {}
                }
            )
            
            self.logger.info(
                f"文本处理完成，实体数: {len(entities)}, 关系数: {len(relations)}, "
                f"耗时: {processing_time:.2f}秒"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"处理文本失败: {str(e)}")
            raise EntityExtractionServiceError(f"处理文本失败: {str(e)}")
    
    def extract_from_files(self, file_paths: List[str], 
                          custom_entity_types: Optional[Dict[str, List[str]]] = None) -> BatchExtractionResult:
        """批量处理文件
        
        Args:
            file_paths: 文件路径列表
            custom_entity_types: 自定义实体类型和对应的关键词
            
        Returns:
            批量抽取结果
        """
        batch_result = BatchExtractionResult(
            batch_id=str(uuid.uuid4()),
            total_documents=len(file_paths)
        )
        
        self.logger.info(f"开始批量处理 {len(file_paths)} 个文件")
        
        for i, file_path in enumerate(file_paths, 1):
            try:
                self.logger.info(f"处理文件 {i}/{len(file_paths)}: {file_path}")
                result = self.extract_from_file(file_path, custom_entity_types)
                batch_result.add_result(result)
                
            except Exception as e:
                error_msg = f"处理文件失败 {file_path}: {str(e)}"
                self.logger.error(error_msg)
                batch_result.add_error(error_msg)
        
        batch_result.finish()
        
        summary = batch_result.get_summary_statistics()
        self.logger.info(
            f"批量处理完成，成功: {summary['successful_documents']}, "
            f"失败: {summary['failed_documents']}, "
            f"总耗时: {summary['total_processing_time']:.2f}秒"
        )
        
        return batch_result
    
    def _parse_document(self, file_path: str) -> Dict[str, Any]:
        """解析文档"""
        try:
            return self.document_parser.parse_document(file_path)
        except DocumentParseError as e:
            raise EntityExtractionServiceError(f"文档解析失败: {str(e)}")
    
    def _extract_entities_and_relations(self, text: str, 
                                       custom_entity_types: Optional[Dict[str, List[str]]] = None) -> Tuple[List[ExtractedEntity], List[ExtractedRelation]]:
        """抽取实体和关系"""
        if not text or not text.strip():
            return [], []
        
        try:
            # 使用NLP处理器抽取实体
            entities = self.nlp_processor.extract_entities(text)
            
            # 添加自定义实体类型的抽取
            if custom_entity_types:
                custom_entities = self._extract_custom_entities(text, custom_entity_types)
                entities.extend(custom_entities)
            
            # 去重实体
            entities = self._deduplicate_entities(entities)
            
            # 抽取关系
            relations = self.nlp_processor.extract_relations(text, entities)
            
            return entities, relations
            
        except NLPProcessorError as e:
            raise EntityExtractionServiceError(f"NLP处理失败: {str(e)}")
    
    def _extract_custom_entities(self, text: str, custom_entity_types: Dict[str, List[str]]) -> List[ExtractedEntity]:
        """抽取自定义实体类型"""
        entities = []
        
        for entity_type_name, keywords in custom_entity_types.items():
            # 尝试将字符串映射到EntityType枚举
            try:
                entity_type = EntityType(entity_type_name.upper())
            except ValueError:
                entity_type = EntityType.CUSTOM
            
            for keyword in keywords:
                # 查找关键词在文本中的所有出现位置
                start = 0
                while True:
                    pos = text.find(keyword, start)
                    if pos == -1:
                        break
                    
                    entity = ExtractedEntity(
                        entity_id=str(uuid.uuid4()),
                        text=keyword,
                        entity_type=entity_type,
                        confidence=0.9,  # 自定义实体的置信度较高
                        start_pos=pos,
                        end_pos=pos + len(keyword),
                        properties={'custom_type': entity_type_name}
                    )
                    entities.append(entity)
                    start = pos + 1
        
        return entities
    
    def _deduplicate_entities(self, entities: List[ExtractedEntity]) -> List[ExtractedEntity]:
        """去重实体"""
        seen = {}
        unique_entities = []
        
        for entity in entities:
            # 使用文本、类型和位置作为去重键
            key = (entity.text.lower().strip(), entity.entity_type, entity.start_pos)
            
            if key not in seen:
                seen[key] = entity
                unique_entities.append(entity)
            else:
                # 如果重复，保留置信度更高的
                existing = seen[key]
                if entity.confidence > existing.confidence:
                    # 替换现有实体
                    index = unique_entities.index(existing)
                    unique_entities[index] = entity
                    seen[key] = entity
        
        return unique_entities
    
    def get_supported_file_types(self) -> List[str]:
        """获取支持的文件类型"""
        return self.document_parser.get_supported_extensions()
    
    def validate_file(self, file_path: str) -> Dict[str, Any]:
        """验证文件是否可以处理
        
        Returns:
            验证结果，包含是否支持、文件信息等
        """
        result = {
            'is_supported': False,
            'file_exists': False,
            'file_size': 0,
            'file_type': None,
            'error': None
        }
        
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                result['error'] = '文件不存在'
                return result
            
            result['file_exists'] = True
            result['file_size'] = os.path.getsize(file_path)
            
            # 检查文件类型是否支持
            parser = self.document_parser.get_parser(file_path)
            if parser:
                result['is_supported'] = True
                result['file_type'] = Path(file_path).suffix.lower()
            else:
                result['error'] = '不支持的文件类型'
            
            # 检查文件大小（限制为50MB）
            max_size = 50 * 1024 * 1024  # 50MB
            if result['file_size'] > max_size:
                result['is_supported'] = False
                result['error'] = f'文件过大，最大支持 {max_size // (1024*1024)}MB'
            
        except Exception as e:
            result['error'] = f'验证文件时出错: {str(e)}'
        
        return result
    
    def get_extraction_statistics(self, results: List[ExtractionResult]) -> Dict[str, Any]:
        """获取抽取统计信息"""
        if not results:
            return {}
        
        total_entities = sum(len(result.entities) for result in results)
        total_relations = sum(len(result.relations) for result in results)
        total_processing_time = sum(result.processing_time for result in results)
        
        # 统计实体类型分布
        entity_type_counts = {}
        for result in results:
            for entity in result.entities:
                entity_type = entity.entity_type.value
                entity_type_counts[entity_type] = entity_type_counts.get(entity_type, 0) + 1
        
        # 统计关系类型分布
        relation_type_counts = {}
        for result in results:
            for relation in result.relations:
                relation_type = relation.relation_type.value
                relation_type_counts[relation_type] = relation_type_counts.get(relation_type, 0) + 1
        
        # 统计置信度分布
        entity_confidence_stats = self._calculate_confidence_stats(
            [entity.confidence for result in results for entity in result.entities]
        )
        
        relation_confidence_stats = self._calculate_confidence_stats(
            [relation.confidence for result in results for relation in result.relations]
        )
        
        return {
            'total_documents': len(results),
            'total_entities': total_entities,
            'total_relations': total_relations,
            'average_entities_per_document': total_entities / len(results),
            'average_relations_per_document': total_relations / len(results),
            'total_processing_time': total_processing_time,
            'average_processing_time': total_processing_time / len(results),
            'entity_type_distribution': entity_type_counts,
            'relation_type_distribution': relation_type_counts,
            'entity_confidence_stats': entity_confidence_stats,
            'relation_confidence_stats': relation_confidence_stats
        }
    
    def _calculate_confidence_stats(self, confidences: List[float]) -> Dict[str, float]:
        """计算置信度统计信息"""
        if not confidences:
            return {}
        
        confidences.sort()
        n = len(confidences)
        
        return {
            'min': min(confidences),
            'max': max(confidences),
            'mean': sum(confidences) / n,
            'median': confidences[n // 2] if n % 2 == 1 else (confidences[n // 2 - 1] + confidences[n // 2]) / 2,
            'q25': confidences[n // 4],
            'q75': confidences[3 * n // 4]
        }
    
    def export_results_to_json(self, results: List[ExtractionResult], output_path: str) -> None:
        """将抽取结果导出为JSON文件"""
        import json
        
        try:
            export_data = {
                'export_time': datetime.now().isoformat(),
                'total_documents': len(results),
                'statistics': self.get_extraction_statistics(results),
                'results': [result.to_dict() for result in results]
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"抽取结果已导出到: {output_path}")
            
        except Exception as e:
            self.logger.error(f"导出结果失败: {str(e)}")
            raise EntityExtractionServiceError(f"导出结果失败: {str(e)}")
    
    def import_results_from_json(self, input_path: str) -> List[ExtractionResult]:
        """从JSON文件导入抽取结果"""
        import json
        
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            results = []
            for result_data in data.get('results', []):
                result = ExtractionResult.from_dict(result_data)
                results.append(result)
            
            self.logger.info(f"从 {input_path} 导入了 {len(results)} 个抽取结果")
            return results
            
        except Exception as e:
            self.logger.error(f"导入结果失败: {str(e)}")
            raise EntityExtractionServiceError(f"导入结果失败: {str(e)}")