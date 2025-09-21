# -*- coding: utf-8 -*-
"""
集成知识服务
整合实体关系抽取、机器学习增强、邮件知识抽取等功能，提供统一的知识管理接口
"""

import logging
import uuid
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path

from ..domain.model.extraction import (
    ExtractedEntity, ExtractedRelation, ExtractionResult, BatchExtractionResult
)
from ..domain.model.graph import KnowledgeGraph
from ..domain.model.node import Node
from ..domain.model.edge import Edge
from ..domain.model.ontology import KnowledgeOntology

from .entity_extraction_service import EntityExtractionService
from .ml_enhancement_service import MLEnhancementService
from .ontology_generator import OntologyGenerator
from ...email_ingestion.application.email_knowledge_service import EmailKnowledgeService
from ...email_ingestion.domain.model.email import Email


class IntegratedKnowledgeServiceError(Exception):
    """集成知识服务异常"""
    pass


class KnowledgeProcessingPipeline:
    """知识处理流水线"""
    
    def __init__(self):
        self.steps: List[Tuple[str, callable]] = []
        self.results: Dict[str, Any] = {}
    
    def add_step(self, name: str, func: callable):
        """添加处理步骤"""
        self.steps.append((name, func))
    
    def execute(self, input_data: Any) -> Dict[str, Any]:
        """执行流水线"""
        current_data = input_data
        
        for step_name, step_func in self.steps:
            try:
                current_data = step_func(current_data)
                self.results[step_name] = current_data
            except Exception as e:
                self.results[step_name] = {'error': str(e)}
                raise
        
        return self.results


class IntegratedKnowledgeService:
    """集成知识服务"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 初始化各个服务组件
        self.entity_extraction_service = EntityExtractionService()
        self.ml_enhancement_service = MLEnhancementService()
        self.ontology_generator = OntologyGenerator()
        self.email_knowledge_service = EmailKnowledgeService()
        
        self.logger.info("集成知识服务初始化完成")
    
    def process_documents_to_knowledge_graph(self, file_paths: List[str], 
                                           enable_ml_enhancement: bool = True,
                                           custom_entity_types: Optional[Dict[str, List[str]]] = None) -> Dict[str, Any]:
        """将文档处理为知识图谱
        
        Args:
            file_paths: 文档路径列表
            enable_ml_enhancement: 是否启用机器学习增强
            custom_entity_types: 自定义实体类型
            
        Returns:
            处理结果，包含知识图谱、本体、统计信息等
        """
        self.logger.info(f"开始文档知识图谱处理，文档数量: {len(file_paths)}")
        
        try:
            # 创建处理流水线
            pipeline = KnowledgeProcessingPipeline()
            
            # 添加处理步骤
            pipeline.add_step('entity_extraction', 
                             lambda data: self._extract_entities_from_documents(data, custom_entity_types))
            
            if enable_ml_enhancement:
                pipeline.add_step('ml_enhancement', 
                                 lambda data: self._enhance_with_ml(data))
            
            pipeline.add_step('knowledge_graph_construction', 
                             lambda data: self._construct_knowledge_graph(data))
            
            pipeline.add_step('ontology_generation', 
                             lambda data: self._generate_ontology(data))
            
            # 执行流水线
            results = pipeline.execute(file_paths)
            
            # 构建最终结果
            final_result = {
                'knowledge_graph': results.get('knowledge_graph_construction', {}),
                'ontology': results.get('ontology_generation', {}),
                'extraction_results': results.get('entity_extraction', {}),
                'ml_enhancement_results': results.get('ml_enhancement', {}),
                'processing_summary': self._generate_processing_summary(results),
                'pipeline_results': results
            }
            
            self.logger.info("文档知识图谱处理完成")
            return final_result
            
        except Exception as e:
            self.logger.error(f"文档知识图谱处理失败: {str(e)}")
            raise IntegratedKnowledgeServiceError(f"文档知识图谱处理失败: {str(e)}")
    
    def process_emails_to_knowledge_graph(self, emails: List[Email], 
                                        enable_ml_enhancement: bool = True) -> Dict[str, Any]:
        """将邮件处理为知识图谱
        
        Args:
            emails: 邮件列表
            enable_ml_enhancement: 是否启用机器学习增强
            
        Returns:
            处理结果
        """
        self.logger.info(f"开始邮件知识图谱处理，邮件数量: {len(emails)}")
        
        try:
            # 从邮件中抽取知识
            extraction_results = self.email_knowledge_service.extract_knowledge_from_emails(emails)
            
            # 分析邮件网络
            network_analysis = self.email_knowledge_service.analyze_email_network(emails)
            
            # 合并所有实体和关系
            all_entities = []
            all_relations = []
            
            for result in extraction_results:
                all_entities.extend(result.entities)
                all_relations.extend(result.relations)
            
            # 机器学习增强
            ml_results = {}
            if enable_ml_enhancement:
                ml_results = self._enhance_entities_and_relations(all_entities, all_relations)
                all_entities = ml_results.get('enhanced_entities', all_entities)
                all_relations = ml_results.get('enhanced_relations', all_relations)
            
            # 构建知识图谱
            knowledge_graph = self._build_knowledge_graph_from_entities_relations(all_entities, all_relations)
            
            # 生成本体
            ontology = self.ontology_generator.generate_ontology_from_graph(
                knowledge_graph, "Email Knowledge Ontology"
            )
            
            # 生成摘要
            knowledge_summary = self.email_knowledge_service.generate_email_knowledge_summary(extraction_results)
            
            result = {
                'knowledge_graph': {
                    'graph': knowledge_graph,
                    'nodes_count': len(knowledge_graph.get_all_nodes()),
                    'edges_count': len(knowledge_graph.get_all_edges())
                },
                'ontology': ontology,
                'extraction_results': extraction_results,
                'network_analysis': network_analysis,
                'ml_enhancement_results': ml_results,
                'knowledge_summary': knowledge_summary,
                'processing_summary': {
                    'total_emails': len(emails),
                    'total_entities': len(all_entities),
                    'total_relations': len(all_relations),
                    'processing_time': sum(r.processing_time for r in extraction_results)
                }
            }
            
            self.logger.info("邮件知识图谱处理完成")
            return result
            
        except Exception as e:
            self.logger.error(f"邮件知识图谱处理失败: {str(e)}")
            raise IntegratedKnowledgeServiceError(f"邮件知识图谱处理失败: {str(e)}")
    
    def enhance_existing_knowledge_graph(self, knowledge_graph: KnowledgeGraph) -> Dict[str, Any]:
        """增强现有知识图谱
        
        Args:
            knowledge_graph: 现有知识图谱
            
        Returns:
            增强结果
        """
        self.logger.info("开始增强现有知识图谱")
        
        try:
            # 从知识图谱中提取实体和关系
            entities, relations = self._extract_entities_relations_from_graph(knowledge_graph)
            
            # 应用机器学习增强
            ml_results = self._enhance_entities_and_relations(entities, relations)
            
            # 更新知识图谱
            enhanced_graph = self._update_knowledge_graph_with_enhancements(
                knowledge_graph, ml_results
            )
            
            # 重新生成本体
            enhanced_ontology = self.ontology_generator.generate_ontology_from_graph(
                enhanced_graph, "Enhanced Knowledge Ontology"
            )
            
            result = {
                'enhanced_knowledge_graph': enhanced_graph,
                'enhanced_ontology': enhanced_ontology,
                'ml_enhancement_results': ml_results,
                'improvement_statistics': self._calculate_improvement_statistics(
                    knowledge_graph, enhanced_graph
                )
            }
            
            self.logger.info("知识图谱增强完成")
            return result
            
        except Exception as e:
            self.logger.error(f"知识图谱增强失败: {str(e)}")
            raise IntegratedKnowledgeServiceError(f"知识图谱增强失败: {str(e)}")
    
    def _extract_entities_from_documents(self, file_paths: List[str], 
                                       custom_entity_types: Optional[Dict[str, List[str]]]) -> BatchExtractionResult:
        """从文档中抽取实体"""
        return self.entity_extraction_service.extract_from_files(file_paths, custom_entity_types)
    
    def _enhance_with_ml(self, batch_result: BatchExtractionResult) -> Dict[str, Any]:
        """使用机器学习增强抽取结果"""
        # 合并所有实体和关系
        all_entities = []
        all_relations = []
        
        for result in batch_result.results:
            all_entities.extend(result.entities)
            all_relations.extend(result.relations)
        
        return self._enhance_entities_and_relations(all_entities, all_relations)
    
    def _enhance_entities_and_relations(self, entities: List[ExtractedEntity], 
                                      relations: List[ExtractedRelation]) -> Dict[str, Any]:
        """增强实体和关系"""
        enhancement_results = {}
        
        try:
            # 实体对齐
            alignment_result = self.ml_enhancement_service.align_entities(entities)
            enhancement_results['entity_alignment'] = alignment_result
            
            # 语义消解
            disambiguation_result = self.ml_enhancement_service.disambiguate_entities(entities)
            enhancement_results['semantic_disambiguation'] = disambiguation_result
            
            # 关系推理
            inferred_relations = self.ml_enhancement_service.infer_relations(entities, relations)
            enhancement_results['inferred_relations'] = inferred_relations
            
            # 异常检测
            anomalies = self.ml_enhancement_service.detect_anomalies(entities, relations)
            enhancement_results['anomalies'] = anomalies
            
            # 计算实体重要性
            importance_scores = self.ml_enhancement_service.calculate_entity_importance(entities, relations)
            enhancement_results['entity_importance'] = importance_scores
            
            # 合并增强后的实体和关系
            enhanced_entities = disambiguation_result.disambiguated_entities
            enhanced_relations = relations + inferred_relations
            
            enhancement_results['enhanced_entities'] = enhanced_entities
            enhancement_results['enhanced_relations'] = enhanced_relations
            
        except Exception as e:
            self.logger.warning(f"机器学习增强部分失败: {str(e)}")
            enhancement_results['error'] = str(e)
            enhancement_results['enhanced_entities'] = entities
            enhancement_results['enhanced_relations'] = relations
        
        return enhancement_results
    
    def _construct_knowledge_graph(self, data: Any) -> Dict[str, Any]:
        """构建知识图谱"""
        # 处理不同类型的输入数据
        if hasattr(data, 'results'):  # BatchExtractionResult
            # 合并所有实体和关系
            entities = []
            relations = []
            for result in data.results:
                entities.extend(result.entities)
                relations.extend(result.relations)
        elif isinstance(data, dict):  # ML enhancement results
            entities = data.get('enhanced_entities', [])
            relations = data.get('enhanced_relations', [])
        else:
            entities = []
            relations = []
        
        knowledge_graph = self._build_knowledge_graph_from_entities_relations(entities, relations)
        
        return {
            'graph': knowledge_graph,
            'nodes_count': len(knowledge_graph.get_all_nodes()),
            'edges_count': len(knowledge_graph.get_all_edges()),
            'statistics': knowledge_graph.get_statistics()
        }
    
    def _generate_ontology(self, kg_results: Dict[str, Any]) -> KnowledgeOntology:
        """生成本体"""
        knowledge_graph = kg_results.get('graph')
        if knowledge_graph:
            return self.ontology_generator.generate_ontology_from_graph(
                knowledge_graph, "Generated Knowledge Ontology"
            )
        return KnowledgeOntology(name="Empty Ontology")
    
    def _build_knowledge_graph_from_entities_relations(self, entities: List[ExtractedEntity], 
                                                      relations: List[ExtractedRelation]) -> KnowledgeGraph:
        """从实体和关系构建知识图谱"""
        kg = KnowledgeGraph()
        
        # 添加节点
        entity_id_to_node = {}
        for entity in entities:
            node = Node(
                node_id=entity.entity_id,
                label=entity.text,
                node_type=entity.entity_type.value,
                properties={
                    **entity.properties,
                    'confidence': entity.confidence,
                    'start_pos': entity.start_pos,
                    'end_pos': entity.end_pos,
                    'source_document': entity.source_document
                }
            )
            kg.add_node(node)
            entity_id_to_node[entity.entity_id] = node
        
        # 添加边
        for relation in relations:
            source_node = entity_id_to_node.get(relation.source_entity.entity_id)
            target_node = entity_id_to_node.get(relation.target_entity.entity_id)
            
            if source_node and target_node:
                edge = Edge(
                    edge_id=relation.relation_id,
                    source_id=source_node.id,
                    target_id=target_node.id,
                    label=relation.relation_type.value,
                    edge_type=relation.relation_type.value,
                    properties={
                        **relation.properties,
                        'confidence': relation.confidence,
                        'evidence_text': relation.evidence_text,
                        'source_document': relation.source_document
                    }
                )
                kg.add_edge(edge)
        
        return kg
    
    def _extract_entities_relations_from_graph(self, kg: KnowledgeGraph) -> Tuple[List[ExtractedEntity], List[ExtractedRelation]]:
        """从知识图谱中提取实体和关系"""
        entities = []
        relations = []
        
        # 提取实体
        for node in kg.get_all_nodes():
            entity = ExtractedEntity(
                entity_id=node.id,
                text=node.label,
                entity_type=self._map_node_type_to_entity_type(node.type),
                confidence=node.properties.get('confidence', 0.8),
                start_pos=node.properties.get('start_pos', 0),
                end_pos=node.properties.get('end_pos', len(node.label)),
                properties=node.properties,
                source_document=node.properties.get('source_document')
            )
            entities.append(entity)
        
        # 提取关系
        entity_map = {entity.entity_id: entity for entity in entities}
        
        for edge in kg.get_all_edges():
            source_entity = entity_map.get(edge.source_id)
            target_entity = entity_map.get(edge.target_id)
            
            if source_entity and target_entity:
                relation = ExtractedRelation(
                    relation_id=edge.id,
                    source_entity=source_entity,
                    target_entity=target_entity,
                    relation_type=self._map_edge_type_to_relation_type(edge.type),
                    confidence=edge.properties.get('confidence', 0.8),
                    evidence_text=edge.properties.get('evidence_text'),
                    properties=edge.properties,
                    source_document=edge.properties.get('source_document')
                )
                relations.append(relation)
        
        return entities, relations
    
    def _map_node_type_to_entity_type(self, node_type: str):
        """将节点类型映射到实体类型"""
        from ..domain.model.extraction import EntityType
        
        mapping = {
            'PERSON': EntityType.PERSON,
            'ORGANIZATION': EntityType.ORGANIZATION,
            'LOCATION': EntityType.LOCATION,
            'DATE': EntityType.DATE,
            'TIME': EntityType.TIME,
            'MONEY': EntityType.MONEY,
            'PERCENT': EntityType.PERCENT,
            'PRODUCT': EntityType.PRODUCT,
            'EVENT': EntityType.EVENT
        }
        
        return mapping.get(node_type.upper(), EntityType.UNKNOWN)
    
    def _map_edge_type_to_relation_type(self, edge_type: str):
        """将边类型映射到关系类型"""
        from ..domain.model.extraction import RelationType
        
        mapping = {
            'WORK_FOR': RelationType.WORK_FOR,
            'LOCATED_IN': RelationType.LOCATED_IN,
            'PART_OF': RelationType.PART_OF,
            'COLLABORATE_WITH': RelationType.COLLABORATE_WITH,
            'REPORT_TO': RelationType.REPORT_TO,
            'PARTICIPATE_IN': RelationType.PARTICIPATE_IN,
            'OWNS': RelationType.OWNS,
            'RELATED_TO': RelationType.RELATED_TO
        }
        
        return mapping.get(edge_type.upper(), RelationType.UNKNOWN)
    
    def _update_knowledge_graph_with_enhancements(self, original_kg: KnowledgeGraph, 
                                                 ml_results: Dict[str, Any]) -> KnowledgeGraph:
        """使用增强结果更新知识图谱"""
        enhanced_entities = ml_results.get('enhanced_entities', [])
        enhanced_relations = ml_results.get('enhanced_relations', [])
        
        return self._build_knowledge_graph_from_entities_relations(enhanced_entities, enhanced_relations)
    
    def _calculate_improvement_statistics(self, original_kg: KnowledgeGraph, 
                                        enhanced_kg: KnowledgeGraph) -> Dict[str, Any]:
        """计算改进统计信息"""
        original_stats = original_kg.get_statistics()
        enhanced_stats = enhanced_kg.get_statistics()
        
        return {
            'nodes_improvement': enhanced_stats['nodes_count'] - original_stats['nodes_count'],
            'edges_improvement': enhanced_stats['edges_count'] - original_stats['edges_count'],
            'density_improvement': enhanced_stats.get('density', 0) - original_stats.get('density', 0),
            'original_statistics': original_stats,
            'enhanced_statistics': enhanced_stats
        }
    
    def _generate_processing_summary(self, pipeline_results: Dict[str, Any]) -> Dict[str, Any]:
        """生成处理摘要"""
        summary = {
            'pipeline_steps': list(pipeline_results.keys()),
            'successful_steps': [],
            'failed_steps': [],
            'total_processing_time': 0
        }
        
        for step_name, step_result in pipeline_results.items():
            if isinstance(step_result, dict) and 'error' in step_result:
                summary['failed_steps'].append(step_name)
            else:
                summary['successful_steps'].append(step_name)
        
        return summary
    
    def export_knowledge_graph(self, knowledge_graph: KnowledgeGraph, 
                              output_path: str, format: str = 'json') -> None:
        """导出知识图谱
        
        Args:
            knowledge_graph: 知识图谱
            output_path: 输出路径
            format: 导出格式 ('json', 'gexf', 'graphml')
        """
        try:
            if format.lower() == 'json':
                knowledge_graph.export_to_json(output_path)
            elif format.lower() == 'gexf':
                knowledge_graph.export_to_gexf(output_path)
            elif format.lower() == 'graphml':
                knowledge_graph.export_to_graphml(output_path)
            else:
                raise ValueError(f"不支持的导出格式: {format}")
            
            self.logger.info(f"知识图谱已导出到: {output_path}")
            
        except Exception as e:
            self.logger.error(f"导出知识图谱失败: {str(e)}")
            raise IntegratedKnowledgeServiceError(f"导出知识图谱失败: {str(e)}")
    
    def import_knowledge_graph(self, input_path: str, format: str = 'json') -> KnowledgeGraph:
        """导入知识图谱
        
        Args:
            input_path: 输入路径
            format: 导入格式 ('json', 'gexf', 'graphml')
            
        Returns:
            知识图谱
        """
        try:
            if format.lower() == 'json':
                return KnowledgeGraph.import_from_json(input_path)
            elif format.lower() == 'gexf':
                return KnowledgeGraph.import_from_gexf(input_path)
            elif format.lower() == 'graphml':
                return KnowledgeGraph.import_from_graphml(input_path)
            else:
                raise ValueError(f"不支持的导入格式: {format}")
            
        except Exception as e:
            self.logger.error(f"导入知识图谱失败: {str(e)}")
            raise IntegratedKnowledgeServiceError(f"导入知识图谱失败: {str(e)}")
    
    def get_service_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        status = {
            'service_name': 'IntegratedKnowledgeService',
            'status': 'running',
            'components': {},
            'supported_features': [
                'document_entity_extraction',
                'email_knowledge_extraction',
                'ml_enhancement',
                'ontology_generation',
                'knowledge_graph_construction'
            ]
        }
        
        # 检查各组件状态
        try:
            supported_extensions = self.entity_extraction_service.get_supported_file_types()
            status['components']['entity_extraction'] = {
                'status': 'available',
                'supported_file_types': supported_extensions
            }
        except Exception as e:
            status['components']['entity_extraction'] = {
                'status': 'error',
                'error': str(e)
            }
        
        try:
            # 测试ML服务
            test_entities = []
            self.ml_enhancement_service.align_entities(test_entities)
            status['components']['ml_enhancement'] = {'status': 'available'}
        except Exception as e:
            status['components']['ml_enhancement'] = {
                'status': 'error',
                'error': str(e)
            }
        
        status['components']['email_knowledge'] = {'status': 'available'}
        status['components']['ontology_generation'] = {'status': 'available'}
        
        return status