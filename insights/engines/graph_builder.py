# -*- coding: utf-8 -*-
"""
图谱构建引擎

将抽取的实体和关系构建成知识图谱，并存储到Neo4j数据库中。
"""

import logging
import hashlib
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

from .knowledge_extractor import Entity, Relation, ExtractionResult
from ..core.database_manager import DatabaseManager
from ..core.exceptions import GraphBuildError
from ..utils.singleton import Singleton

@dataclass
class GraphNode:
    """图节点数据类"""
    id: str
    label: str
    properties: Dict[str, Any]
    created_at: str = None
    updated_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = self.created_at

@dataclass
class GraphEdge:
    """图边数据类"""
    source_id: str
    target_id: str
    relation_type: str
    properties: Dict[str, Any]
    weight: float = 1.0
    created_at: str = None
    updated_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = self.created_at

@dataclass
class GraphStats:
    """图谱统计信息"""
    node_count: int
    edge_count: int
    node_types: Dict[str, int]
    edge_types: Dict[str, int]
    avg_degree: float
    density: float
    
class GraphBuilder(metaclass=Singleton):
    """图谱构建引擎
    
    负责将抽取的知识构建成图谱结构并存储。
    """
    
    def __init__(self):
        """初始化图谱构建引擎"""
        self.logger = logging.getLogger(__name__)
        self.db_manager = DatabaseManager()
        self.node_cache: Dict[str, GraphNode] = {}
        self.edge_cache: Set[Tuple[str, str, str]] = set()
        
    def initialize(self) -> bool:
        """初始化图谱构建引擎
        
        Returns:
            是否初始化成功
        """
        try:
            # 创建图谱索引和约束
            self._create_graph_schema()
            
            self.logger.info("图谱构建引擎初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"图谱构建引擎初始化失败: {e}")
            raise GraphBuildError(f"Failed to initialize graph builder: {e}")
            
    def build_graph_from_extraction(self, extraction_result: ExtractionResult,
                                   source_id: str = None) -> Dict[str, Any]:
        """从抽取结果构建图谱
        
        Args:
            extraction_result: 知识抽取结果
            source_id: 数据源ID（如邮件ID）
            
        Returns:
            构建结果统计
        """
        try:
            nodes_created = 0
            edges_created = 0
            
            # 构建节点
            entity_nodes = {}
            for entity in extraction_result.entities:
                node = self._create_node_from_entity(entity, source_id)
                if self._add_node_to_graph(node):
                    nodes_created += 1
                entity_nodes[id(entity)] = node
                
            # 构建边
            for relation in extraction_result.relations:
                source_node = entity_nodes.get(id(relation.source))
                target_node = entity_nodes.get(id(relation.target))
                
                if source_node and target_node:
                    edge = self._create_edge_from_relation(
                        relation, source_node.id, target_node.id, source_id
                    )
                    if self._add_edge_to_graph(edge):
                        edges_created += 1
                        
            # 更新缓存
            self._update_cache()
            
            result = {
                'nodes_created': nodes_created,
                'edges_created': edges_created,
                'source_id': source_id,
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"图谱构建完成: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"图谱构建失败: {e}")
            raise GraphBuildError(f"Graph building failed: {e}")
            
    def build_graph_batch(self, extraction_results: List[ExtractionResult],
                         source_ids: List[str] = None) -> Dict[str, Any]:
        """批量构建图谱
        
        Args:
            extraction_results: 抽取结果列表
            source_ids: 数据源ID列表
            
        Returns:
            批量构建结果统计
        """
        try:
            total_nodes = 0
            total_edges = 0
            
            if source_ids is None:
                source_ids = [None] * len(extraction_results)
                
            for i, result in enumerate(extraction_results):
                source_id = source_ids[i] if i < len(source_ids) else None
                build_result = self.build_graph_from_extraction(result, source_id)
                total_nodes += build_result['nodes_created']
                total_edges += build_result['edges_created']
                
            return {
                'total_documents': len(extraction_results),
                'total_nodes_created': total_nodes,
                'total_edges_created': total_edges,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"批量图谱构建失败: {e}")
            raise GraphBuildError(f"Batch graph building failed: {e}")
            
    def _create_node_from_entity(self, entity: Entity, source_id: str = None) -> GraphNode:
        """从实体创建图节点
        
        Args:
            entity: 实体对象
            source_id: 数据源ID
            
        Returns:
            图节点对象
        """
        # 生成节点ID
        node_id = self._generate_node_id(entity.text, entity.label)
        
        # 构建节点属性
        properties = {
            'text': entity.text,
            'confidence': entity.confidence,
            'start_pos': entity.start,
            'end_pos': entity.end
        }
        
        # 添加实体属性
        if entity.properties:
            properties.update(entity.properties)
            
        # 添加数据源信息
        if source_id:
            properties['source_id'] = source_id
            
        return GraphNode(
            id=node_id,
            label=entity.label,
            properties=properties
        )
        
    def _create_edge_from_relation(self, relation: Relation, source_id: str,
                                 target_id: str, doc_source_id: str = None) -> GraphEdge:
        """从关系创建图边
        
        Args:
            relation: 关系对象
            source_id: 源节点ID
            target_id: 目标节点ID
            doc_source_id: 文档源ID
            
        Returns:
            图边对象
        """
        # 构建边属性
        properties = {
            'confidence': relation.confidence
        }
        
        # 添加关系属性
        if relation.properties:
            properties.update(relation.properties)
            
        # 添加数据源信息
        if doc_source_id:
            properties['source_id'] = doc_source_id
            
        return GraphEdge(
            source_id=source_id,
            target_id=target_id,
            relation_type=relation.relation_type,
            properties=properties,
            weight=relation.confidence
        )
        
    def _add_node_to_graph(self, node: GraphNode) -> bool:
        """添加节点到图谱
        
        Args:
            node: 图节点对象
            
        Returns:
            是否成功添加（新节点）
        """
        try:
            # 检查节点是否已存在
            if node.id in self.node_cache:
                # 更新现有节点
                self._update_existing_node(node)
                return False
                
            # 创建新节点的Cypher查询
            query = f"""
            MERGE (n:{node.label} {{id: $id}})
            ON CREATE SET n += $properties, n.created_at = $created_at
            ON MATCH SET n += $properties, n.updated_at = $updated_at
            RETURN n
            """
            
            parameters = {
                'id': node.id,
                'properties': node.properties,
                'created_at': node.created_at,
                'updated_at': datetime.now().isoformat()
            }
            
            result = self.db_manager.execute_cypher_write(query, parameters)
            
            # 添加到缓存
            self.node_cache[node.id] = node
            
            return result['nodes_created'] > 0
            
        except Exception as e:
            self.logger.error(f"添加节点失败: {e}")
            return False
            
    def _add_edge_to_graph(self, edge: GraphEdge) -> bool:
        """添加边到图谱
        
        Args:
            edge: 图边对象
            
        Returns:
            是否成功添加（新边）
        """
        try:
            # 检查边是否已存在
            edge_key = (edge.source_id, edge.target_id, edge.relation_type)
            if edge_key in self.edge_cache:
                # 更新现有边
                self._update_existing_edge(edge)
                return False
                
            # 创建新边的Cypher查询
            query = f"""
            MATCH (source {{id: $source_id}})
            MATCH (target {{id: $target_id}})
            MERGE (source)-[r:{edge.relation_type}]->(target)
            ON CREATE SET r += $properties, r.created_at = $created_at
            ON MATCH SET r += $properties, r.updated_at = $updated_at
            RETURN r
            """
            
            parameters = {
                'source_id': edge.source_id,
                'target_id': edge.target_id,
                'properties': edge.properties,
                'created_at': edge.created_at,
                'updated_at': datetime.now().isoformat()
            }
            
            result = self.db_manager.execute_cypher_write(query, parameters)
            
            # 添加到缓存
            self.edge_cache.add(edge_key)
            
            return result['relationships_created'] > 0
            
        except Exception as e:
            self.logger.error(f"添加边失败: {e}")
            return False
            
    def _update_existing_node(self, node: GraphNode):
        """更新现有节点
        
        Args:
            node: 图节点对象
        """
        try:
            query = f"""
            MATCH (n:{node.label} {{id: $id}})
            SET n += $properties, n.updated_at = $updated_at
            RETURN n
            """
            
            parameters = {
                'id': node.id,
                'properties': node.properties,
                'updated_at': datetime.now().isoformat()
            }
            
            self.db_manager.execute_cypher_write(query, parameters)
            
            # 更新缓存
            self.node_cache[node.id] = node
            
        except Exception as e:
            self.logger.error(f"更新节点失败: {e}")
            
    def _update_existing_edge(self, edge: GraphEdge):
        """更新现有边
        
        Args:
            edge: 图边对象
        """
        try:
            query = f"""
            MATCH (source {{id: $source_id}})-[r:{edge.relation_type}]->(target {{id: $target_id}})
            SET r += $properties, r.updated_at = $updated_at
            RETURN r
            """
            
            parameters = {
                'source_id': edge.source_id,
                'target_id': edge.target_id,
                'properties': edge.properties,
                'updated_at': datetime.now().isoformat()
            }
            
            self.db_manager.execute_cypher_write(query, parameters)
            
        except Exception as e:
            self.logger.error(f"更新边失败: {e}")
            
    def _generate_node_id(self, text: str, label: str) -> str:
        """生成节点ID
        
        Args:
            text: 节点文本
            label: 节点标签
            
        Returns:
            节点ID
        """
        # 使用文本和标签的哈希值作为ID
        content = f"{label}:{text.lower().strip()}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
        
    def _create_graph_schema(self):
        """创建图谱模式（索引和约束）"""
        try:
            # 创建节点唯一性约束
            node_labels = ['PERSON', 'COMPANY', 'PRODUCT', 'LOCATION', 'EMAIL', 'PHONE', 'MONEY', 'DATE']
            
            for label in node_labels:
                constraint_query = f"""
                CREATE CONSTRAINT IF NOT EXISTS FOR (n:{label})
                REQUIRE n.id IS UNIQUE
                """
                self.db_manager.execute_cypher_write(constraint_query)
                
            # 创建文本搜索索引
            for label in node_labels:
                index_query = f"""
                CREATE INDEX IF NOT EXISTS FOR (n:{label}) ON (n.text)
                """
                self.db_manager.execute_cypher_write(index_query)
                
            # 创建时间索引
            time_index_query = """
            CREATE INDEX IF NOT EXISTS FOR (n) ON (n.created_at)
            """
            self.db_manager.execute_cypher_write(time_index_query)
            
            self.logger.info("图谱模式创建成功")
            
        except Exception as e:
            self.logger.error(f"创建图谱模式失败: {e}")
            raise GraphBuildError(f"Failed to create graph schema: {e}")
            
    def _update_cache(self):
        """更新缓存"""
        try:
            # 定期清理缓存以避免内存溢出
            if len(self.node_cache) > 10000:
                # 保留最近的5000个节点
                sorted_nodes = sorted(
                    self.node_cache.items(),
                    key=lambda x: x[1].updated_at,
                    reverse=True
                )
                self.node_cache = dict(sorted_nodes[:5000])
                
            if len(self.edge_cache) > 50000:
                # 清空边缓存
                self.edge_cache.clear()
                
        except Exception as e:
            self.logger.error(f"更新缓存失败: {e}")
            
    def get_graph_statistics(self) -> GraphStats:
        """获取图谱统计信息
        
        Returns:
            图谱统计信息
        """
        try:
            # 获取节点统计
            node_query = """
            MATCH (n)
            RETURN labels(n)[0] as label, count(n) as count
            """
            node_results = self.db_manager.execute_cypher(node_query)
            
            node_types = {}
            total_nodes = 0
            for result in node_results:
                label = result['label']
                count = result['count']
                node_types[label] = count
                total_nodes += count
                
            # 获取边统计
            edge_query = """
            MATCH ()-[r]->()
            RETURN type(r) as relation_type, count(r) as count
            """
            edge_results = self.db_manager.execute_cypher(edge_query)
            
            edge_types = {}
            total_edges = 0
            for result in edge_results:
                relation_type = result['relation_type']
                count = result['count']
                edge_types[relation_type] = count
                total_edges += count
                
            # 计算平均度和密度
            avg_degree = (2 * total_edges) / total_nodes if total_nodes > 0 else 0
            max_edges = total_nodes * (total_nodes - 1)
            density = total_edges / max_edges if max_edges > 0 else 0
            
            return GraphStats(
                node_count=total_nodes,
                edge_count=total_edges,
                node_types=node_types,
                edge_types=edge_types,
                avg_degree=avg_degree,
                density=density
            )
            
        except Exception as e:
            self.logger.error(f"获取图谱统计失败: {e}")
            return GraphStats(
                node_count=0,
                edge_count=0,
                node_types={},
                edge_types={},
                avg_degree=0.0,
                density=0.0
            )
            
    def query_nodes(self, label: str = None, properties: Dict[str, Any] = None,
                   limit: int = 100) -> List[Dict[str, Any]]:
        """查询节点
        
        Args:
            label: 节点标签
            properties: 节点属性过滤条件
            limit: 结果限制数量
            
        Returns:
            节点列表
        """
        try:
            # 构建查询条件
            where_conditions = []
            parameters = {'limit': limit}
            
            if properties:
                for key, value in properties.items():
                    where_conditions.append(f"n.{key} = ${key}")
                    parameters[key] = value
                    
            where_clause = f"WHERE {' AND '.join(where_conditions)}" if where_conditions else ""
            label_clause = f":{label}" if label else ""
            
            query = f"""
            MATCH (n{label_clause})
            {where_clause}
            RETURN n
            LIMIT $limit
            """
            
            results = self.db_manager.execute_cypher(query, parameters)
            return [result['n'] for result in results]
            
        except Exception as e:
            self.logger.error(f"查询节点失败: {e}")
            return []
            
    def query_relationships(self, source_id: str = None, target_id: str = None,
                          relation_type: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """查询关系
        
        Args:
            source_id: 源节点ID
            target_id: 目标节点ID
            relation_type: 关系类型
            limit: 结果限制数量
            
        Returns:
            关系列表
        """
        try:
            # 构建查询条件
            where_conditions = []
            parameters = {'limit': limit}
            
            if source_id:
                where_conditions.append("source.id = $source_id")
                parameters['source_id'] = source_id
                
            if target_id:
                where_conditions.append("target.id = $target_id")
                parameters['target_id'] = target_id
                
            where_clause = f"WHERE {' AND '.join(where_conditions)}" if where_conditions else ""
            relation_clause = f":{relation_type}" if relation_type else ""
            
            query = f"""
            MATCH (source)-[r{relation_clause}]->(target)
            {where_clause}
            RETURN source, r, target
            LIMIT $limit
            """
            
            results = self.db_manager.execute_cypher(query, parameters)
            return results
            
        except Exception as e:
            self.logger.error(f"查询关系失败: {e}")
            return []
            
    def delete_graph_data(self, source_id: str = None) -> Dict[str, int]:
        """删除图谱数据
        
        Args:
            source_id: 数据源ID，如果指定则只删除该源的数据
            
        Returns:
            删除统计信息
        """
        try:
            if source_id:
                # 删除特定源的数据
                query = """
                MATCH (n {source_id: $source_id})
                DETACH DELETE n
                """
                parameters = {'source_id': source_id}
            else:
                # 删除所有数据
                query = """
                MATCH (n)
                DETACH DELETE n
                """
                parameters = {}
                
            result = self.db_manager.execute_cypher_write(query, parameters)
            
            # 清空缓存
            if not source_id:
                self.node_cache.clear()
                self.edge_cache.clear()
                
            return {
                'nodes_deleted': result['nodes_deleted'],
                'relationships_deleted': result['relationships_deleted']
            }
            
        except Exception as e:
            self.logger.error(f"删除图谱数据失败: {e}")
            return {'nodes_deleted': 0, 'relationships_deleted': 0}