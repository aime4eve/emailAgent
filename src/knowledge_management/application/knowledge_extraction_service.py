# -*- coding: utf-8 -*-
"""
知识抽取服务
整合NLP和ML功能，提供完整的知识抽取流程
"""

from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path
import logging
from dataclasses import dataclass

from ..domain.model.graph import KnowledgeGraph
from ..domain.model.node import Node
from ..domain.model.edge import Edge
from ...nlp_processing.document_parser import DocumentParser
from ...nlp_processing.text_preprocessor import TextPreprocessor
from ...nlp_processing.entity_extractor import EntityExtractor, Entity
from ...nlp_processing.relation_extractor import RelationExtractor, Relation
from ...ml_enhancement.entity_alignment import EntityAlignment
from ...ml_enhancement.similarity_calculator import SimilarityCalculator

logger = logging.getLogger(__name__)


@dataclass
class ExtractionResult:
    """
    抽取结果类
    """
    knowledge_graph: KnowledgeGraph
    entities: List[Entity]
    relations: List[Relation]
    statistics: Dict[str, Any]
    source_info: Dict[str, Any]


class KnowledgeExtractionService:
    """
    知识抽取服务
    提供从文档到知识图谱的完整抽取流程
    """
    
    def __init__(self, language: str = 'chinese'):
        """
        初始化知识抽取服务
        
        Args:
            language: 语言类型
        """
        self.language = language
        
        # 初始化各个组件
        self.document_parser = DocumentParser()
        self.text_preprocessor = TextPreprocessor(language)
        self.entity_extractor = EntityExtractor(language)
        self.relation_extractor = RelationExtractor(language)
        self.entity_alignment = EntityAlignment()
        self.similarity_calculator = SimilarityCalculator()
        
        logger.info(f"知识抽取服务初始化完成，语言: {language}")
    
    def extract_from_document(self, file_path: str, 
                            enable_alignment: bool = True,
                            custom_entity_patterns: Dict[str, List[str]] = None,
                            custom_relation_patterns: Dict[str, Any] = None) -> ExtractionResult:
        """
        从文档中抽取知识
        
        Args:
            file_path: 文档文件路径
            enable_alignment: 是否启用实体对齐
            custom_entity_patterns: 自定义实体模式
            custom_relation_patterns: 自定义关系模式
            
        Returns:
            抽取结果
        """
        logger.info(f"开始从文档抽取知识: {file_path}")
        
        try:
            # 1. 解析文档
            doc_result = self.document_parser.parse_document(file_path)
            text_content = doc_result['content']
            metadata = doc_result['metadata']
            
            if not text_content.strip():
                logger.warning(f"文档内容为空: {file_path}")
                return self._create_empty_result(file_path, metadata)
            
            # 2. 从文本抽取知识
            extraction_result = self.extract_from_text(
                text_content,
                enable_alignment=enable_alignment,
                custom_entity_patterns=custom_entity_patterns,
                custom_relation_patterns=custom_relation_patterns
            )
            
            # 3. 更新源信息
            extraction_result.source_info.update({
                'source_type': 'document',
                'file_path': file_path,
                'file_metadata': metadata
            })
            
            logger.info(f"文档知识抽取完成: {len(extraction_result.entities)}个实体, {len(extraction_result.relations)}个关系")
            return extraction_result
        
        except Exception as e:
            logger.error(f"文档知识抽取失败 {file_path}: {str(e)}")
            raise
    
    def extract_from_text(self, text: str,
                         enable_alignment: bool = True,
                         custom_entity_patterns: Dict[str, List[str]] = None,
                         custom_relation_patterns: Dict[str, Any] = None) -> ExtractionResult:
        """
        从文本中抽取知识
        
        Args:
            text: 输入文本
            enable_alignment: 是否启用实体对齐
            custom_entity_patterns: 自定义实体模式
            custom_relation_patterns: 自定义关系模式
            
        Returns:
            抽取结果
        """
        logger.info("开始从文本抽取知识")
        
        try:
            # 1. 文本预处理
            preprocessed = self.text_preprocessor.preprocess_text(text, remove_stopwords=False)
            cleaned_text = preprocessed['cleaned_text']
            
            # 2. 实体抽取
            entities = self.entity_extractor.extract_entities(
                cleaned_text,
                use_rules=True,
                use_model=True,
                custom_patterns=custom_entity_patterns
            )
            
            logger.info(f"抽取到 {len(entities)} 个实体")
            
            # 3. 关系抽取
            relations = self.relation_extractor.extract_relations_from_text(cleaned_text, entities)
            
            # 添加自定义关系模式
            if custom_relation_patterns:
                for rel_type, pattern_info in custom_relation_patterns.items():
                    self.relation_extractor.add_custom_relation_pattern(rel_type, pattern_info)
                
                custom_relations = self.relation_extractor.extract_relations_with_custom_patterns(
                    cleaned_text, entities
                )
                relations.extend(custom_relations)
            
            logger.info(f"抽取到 {len(relations)} 个关系")
            
            # 4. 构建知识图谱
            kg = self._build_knowledge_graph(entities, relations)
            
            # 5. 实体对齐（可选）
            if enable_alignment and len(entities) > 1:
                alignment_results = self.entity_alignment.align_entities(kg)
                if alignment_results:
                    kg = self.entity_alignment.apply_alignment_results(kg, alignment_results)
                    logger.info(f"实体对齐完成，合并了 {len(alignment_results)} 组重复实体")
            
            # 6. 生成统计信息
            statistics = self._generate_statistics(entities, relations, kg)
            
            result = ExtractionResult(
                knowledge_graph=kg,
                entities=entities,
                relations=relations,
                statistics=statistics,
                source_info={
                    'source_type': 'text',
                    'text_length': len(text),
                    'processed_text_length': len(cleaned_text)
                }
            )
            
            # 为了兼容性，添加get方法
            result.get = lambda key, default=None: getattr(result, key, result.source_info.get(key, default))
            
            logger.info("文本知识抽取完成")
            return result
        
        except Exception as e:
            logger.error(f"文本知识抽取失败: {str(e)}")
            raise
    
    def batch_extract_from_documents(self, file_paths: List[str],
                                   enable_alignment: bool = True) -> List[ExtractionResult]:
        """
        批量从文档抽取知识
        
        Args:
            file_paths: 文档文件路径列表
            enable_alignment: 是否启用实体对齐
            
        Returns:
            抽取结果列表
        """
        logger.info(f"开始批量抽取知识，共 {len(file_paths)} 个文档")
        
        results = []
        for i, file_path in enumerate(file_paths, 1):
            try:
                logger.info(f"处理文档 {i}/{len(file_paths)}: {file_path}")
                result = self.extract_from_document(file_path, enable_alignment)
                results.append(result)
            except Exception as e:
                logger.error(f"文档处理失败 {file_path}: {str(e)}")
                # 创建空结果
                empty_result = self._create_empty_result(file_path, {'error': str(e)})
                results.append(empty_result)
        
        logger.info(f"批量抽取完成，成功处理 {len([r for r in results if r.entities])} 个文档")
        return results
    
    def merge_extraction_results(self, results: List[ExtractionResult]) -> ExtractionResult:
        """
        合并多个抽取结果
        
        Args:
            results: 抽取结果列表
            
        Returns:
            合并后的抽取结果
        """
        logger.info(f"开始合并 {len(results)} 个抽取结果")
        
        # 合并所有实体和关系
        all_entities = []
        all_relations = []
        merged_kg = KnowledgeGraph()
        
        for result in results:
            all_entities.extend(result.entities)
            all_relations.extend(result.relations)
            
            # 合并知识图谱
            for node in result.knowledge_graph.get_all_nodes():
                merged_kg.add_node(node)
            
            for edge in result.knowledge_graph.get_all_edges():
                merged_kg.add_edge(edge)
        
        # 全局实体对齐
        if len(all_entities) > 1:
            alignment_results = self.entity_alignment.align_entities(merged_kg)
            if alignment_results:
                merged_kg = self.entity_alignment.apply_alignment_results(merged_kg, alignment_results)
                logger.info(f"全局实体对齐完成，合并了 {len(alignment_results)} 组重复实体")
        
        # 生成合并统计信息
        merged_statistics = self._generate_merged_statistics(results, merged_kg)
        
        merged_result = ExtractionResult(
            knowledge_graph=merged_kg,
            entities=all_entities,
            relations=all_relations,
            statistics=merged_statistics,
            source_info={
                'source_type': 'merged',
                'source_count': len(results),
                'sources': [r.source_info for r in results]
            }
        )
        
        logger.info(f"结果合并完成，最终包含 {len(merged_kg.get_all_nodes())} 个节点，{len(merged_kg.get_all_edges())} 条边")
        return merged_result
    
    def _build_knowledge_graph(self, entities: List[Entity], relations: List[Relation]) -> KnowledgeGraph:
        """
        从实体和关系构建知识图谱
        
        Args:
            entities: 实体列表
            relations: 关系列表
            
        Returns:
            知识图谱
        """
        kg = KnowledgeGraph()
        
        # 添加节点
        for entity in entities:
            node = Node(
                node_id=f"entity_{len(kg.get_all_nodes())}",
                label=entity.text,
                node_type=entity.label,
                properties={
                    'confidence': entity.confidence,
                    'start_pos': entity.start,
                    'end_pos': entity.end,
                    **entity.properties
                }
            )
            kg.add_node(node)
        
        # 创建实体到节点的映射
        entity_to_node = {}
        nodes = kg.get_all_nodes()
        for i, entity in enumerate(entities):
            if i < len(nodes):
                entity_to_node[entity] = nodes[i]
        
        # 添加边
        for relation in relations:
            subject_node = entity_to_node.get(relation.subject)
            object_node = entity_to_node.get(relation.object)
            
            if subject_node and object_node:
                edge = Edge(
                    source_id=subject_node.id,
                    target_id=object_node.id,
                    label=relation.predicate,
                    edge_type=relation.predicate,
                    properties={
                        'confidence': relation.confidence,
                        'context': relation.context,
                        **relation.properties
                    }
                )
                kg.add_edge(edge)
        
        return kg
    
    def _generate_statistics(self, entities: List[Entity], 
                           relations: List[Relation], 
                           kg: KnowledgeGraph) -> Dict[str, Any]:
        """
        生成统计信息
        
        Args:
            entities: 实体列表
            relations: 关系列表
            kg: 知识图谱
            
        Returns:
            统计信息字典
        """
        entity_stats = self.entity_extractor.get_entity_statistics(entities)
        relation_stats = self.relation_extractor.get_relation_statistics(relations)
        kg_stats = kg.get_statistics()
        
        return {
            'entities': entity_stats,
            'relations': relation_stats,
            'knowledge_graph': kg_stats,
            'extraction_quality': {
                'avg_entity_confidence': entity_stats.get('avg_confidence', 0.0),
                'avg_relation_confidence': relation_stats.get('avg_confidence', 0.0),
                'entity_relation_ratio': len(relations) / max(len(entities), 1)
            }
        }
    
    def _generate_merged_statistics(self, results: List[ExtractionResult], 
                                  merged_kg: KnowledgeGraph) -> Dict[str, Any]:
        """
        生成合并统计信息
        
        Args:
            results: 抽取结果列表
            merged_kg: 合并后的知识图谱
            
        Returns:
            合并统计信息字典
        """
        total_entities = sum(len(r.entities) for r in results)
        total_relations = sum(len(r.relations) for r in results)
        
        return {
            'source_count': len(results),
            'total_entities_before_merge': total_entities,
            'total_relations_before_merge': total_relations,
            'final_nodes': len(merged_kg.get_all_nodes()),
            'final_edges': len(merged_kg.get_all_edges()),
            'entity_reduction_rate': 1.0 - (len(merged_kg.get_all_nodes()) / max(total_entities, 1)),
            'relation_reduction_rate': 1.0 - (len(merged_kg.get_all_edges()) / max(total_relations, 1)),
            'individual_results': [r.statistics for r in results]
        }
    
    def _create_empty_result(self, source: str, metadata: Dict[str, Any]) -> ExtractionResult:
        """
        创建空的抽取结果
        
        Args:
            source: 数据源
            metadata: 元数据
            
        Returns:
            空的抽取结果
        """
        return ExtractionResult(
            knowledge_graph=KnowledgeGraph(),
            entities=[],
            relations=[],
            statistics={
                'entities': {'total_count': 0},
                'relations': {'total_count': 0},
                'knowledge_graph': {'nodes_count': 0, 'edges_count': 0}
            },
            source_info={
                'source': source,
                'metadata': metadata
            }
        )
    
    def enhance_knowledge_graph(self, kg: KnowledgeGraph) -> KnowledgeGraph:
        """
        增强知识图谱质量
        
        Args:
            kg: 原始知识图谱
            
        Returns:
            增强后的知识图谱
        """
        logger.info("开始增强知识图谱质量")
        
        # 1. 实体对齐
        alignment_results = self.entity_alignment.align_entities(kg)
        if alignment_results:
            kg = self.entity_alignment.apply_alignment_results(kg, alignment_results)
            logger.info(f"实体对齐完成，合并了 {len(alignment_results)} 组重复实体")
        
        # 2. 相似度计算和推荐
        nodes = kg.get_all_nodes()
        if len(nodes) > 1:
            similar_pairs = self.similarity_calculator.batch_similarity(nodes, 0.8)
            logger.info(f"发现 {len(similar_pairs)} 对高相似度实体")
        
        logger.info("知识图谱质量增强完成")
        return kg
    
    def get_extraction_report(self, result: ExtractionResult) -> str:
        """
        生成抽取报告
        
        Args:
            result: 抽取结果
            
        Returns:
            抽取报告文本
        """
        report_lines = [
            "=== 知识抽取报告 ===",
            f"数据源: {result.source_info.get('source_type', 'unknown')}",
            "",
            "=== 实体统计 ===",
            f"总实体数: {result.statistics['entities']['total_count']}",
        ]
        
        # 实体类型分布
        entity_types = result.statistics['entities'].get('by_type', {})
        for entity_type, type_info in entity_types.items():
            report_lines.append(f"  {entity_type}: {type_info['count']} 个")
        
        report_lines.extend([
            "",
            "=== 关系统计 ===",
            f"总关系数: {result.statistics['relations']['total_count']}",
        ])
        
        # 关系类型分布
        relation_types = result.statistics['relations'].get('by_type', {})
        for relation_type, type_info in relation_types.items():
            report_lines.append(f"  {relation_type}: {type_info['count']} 个")
        
        report_lines.extend([
            "",
            "=== 知识图谱统计 ===",
            f"节点数: {result.statistics['knowledge_graph']['nodes_count']}",
            f"边数: {result.statistics['knowledge_graph']['edges_count']}",
            "",
            "=== 质量评估 ===",
            f"平均实体置信度: {result.statistics['extraction_quality']['avg_entity_confidence']:.2f}",
            f"平均关系置信度: {result.statistics['extraction_quality']['avg_relation_confidence']:.2f}",
            f"实体关系比: {result.statistics['extraction_quality']['entity_relation_ratio']:.2f}",
        ])
        
        return "\n".join(report_lines)