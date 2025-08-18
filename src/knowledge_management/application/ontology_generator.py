# -*- coding: utf-8 -*-
"""
本体生成器
从知识图谱数据自动生成本体结构
"""

from typing import Dict, List, Set, Any, Optional, Tuple
from collections import defaultdict, Counter
import re
from datetime import datetime

from src.knowledge_management.domain.model.ontology import (
    KnowledgeOntology, OntologyClass, OntologyRelation, 
    OntologyProperty, DataType
)
from src.knowledge_management.domain.model.graph import KnowledgeGraph
from src.knowledge_management.domain.model.node import Node
from src.knowledge_management.domain.model.edge import Edge


class OntologyGenerator:
    """本体生成器"""
    
    def __init__(self):
        self.type_inference_rules = {
            'string': self._is_string,
            'integer': self._is_integer,
            'float': self._is_float,
            'boolean': self._is_boolean,
            'date': self._is_date,
            'datetime': self._is_datetime,
            'uri': self._is_uri
        }
    
    def generate_ontology_from_graph(self, kg: KnowledgeGraph, 
                                   ontology_name: str = "Generated Ontology",
                                   namespace: str = None) -> KnowledgeOntology:
        """
        从知识图谱生成本体
        
        Args:
            kg: 知识图谱实例
            ontology_name: 本体名称
            namespace: 命名空间
            
        Returns:
            生成的知识本体
        """
        # 创建本体实例
        ontology = KnowledgeOntology(
            name=ontology_name,
            namespace=namespace,
            description=f"从包含{len(kg.get_all_nodes())}个节点和{len(kg.get_all_edges())}条边的知识图谱自动生成"
        )
        
        # 分析节点生成类
        node_analysis = self._analyze_nodes(kg.get_all_nodes())
        for class_name, class_info in node_analysis.items():
            ontology_class = self._create_ontology_class(class_name, class_info)
            ontology.add_class(ontology_class)
        
        # 分析边生成关系
        edge_analysis = self._analyze_edges(kg.get_all_edges())
        for relation_name, relation_info in edge_analysis.items():
            ontology_relation = self._create_ontology_relation(relation_name, relation_info)
            ontology.add_relation(ontology_relation)
        
        # 推断类层次结构
        self._infer_class_hierarchy(ontology, kg)
        
        # 推断关系属性
        self._infer_relation_properties(ontology, kg)
        
        return ontology
    
    def _analyze_nodes(self, nodes: List[Node]) -> Dict[str, Dict[str, Any]]:
        """
        分析节点，按类型分组并提取属性模式
        
        Args:
            nodes: 节点列表
            
        Returns:
            按类型分组的节点分析结果
        """
        type_analysis = defaultdict(lambda: {
            'instances': [],
            'properties': defaultdict(list),
            'labels': [],
            'count': 0
        })
        
        for node in nodes:
            node_type = node.type or 'Unknown'
            type_info = type_analysis[node_type]
            
            type_info['instances'].append(node.id)
            type_info['labels'].append(node.label)
            type_info['count'] += 1
            
            # 分析属性
            for prop_name, prop_value in node.properties.items():
                type_info['properties'][prop_name].append(prop_value)
        
        return dict(type_analysis)
    
    def _analyze_edges(self, edges: List[Edge]) -> Dict[str, Dict[str, Any]]:
        """
        分析边，按类型分组并提取模式
        
        Args:
            edges: 边列表
            
        Returns:
            按类型分组的边分析结果
        """
        type_analysis = defaultdict(lambda: {
            'instances': [],
            'properties': defaultdict(list),
            'labels': [],
            'source_types': set(),
            'target_types': set(),
            'count': 0
        })
        
        for edge in edges:
            edge_type = edge.type or 'Unknown'
            type_info = type_analysis[edge_type]
            
            type_info['instances'].append(edge.id)
            type_info['labels'].append(edge.label)
            type_info['count'] += 1
            
            # 记录源和目标类型（需要从图中获取节点信息）
            # 这里暂时记录ID，后续需要映射到类型
            type_info['source_types'].add(edge.source_id)
            type_info['target_types'].add(edge.target_id)
            
            # 分析属性
            for prop_name, prop_value in edge.properties.items():
                type_info['properties'][prop_name].append(prop_value)
        
        return dict(type_analysis)
    
    def _create_ontology_class(self, class_name: str, class_info: Dict[str, Any]) -> OntologyClass:
        """
        创建本体类
        
        Args:
            class_name: 类名
            class_info: 类信息
            
        Returns:
            本体类实例
        """
        ontology_class = OntologyClass(
            name=class_name,
            description=f"从{class_info['count']}个实例推断的{class_name}类",
            instances_count=class_info['count'],
            examples=class_info['labels'][:5]  # 取前5个作为示例
        )
        
        # 分析属性并创建本体属性
        for prop_name, prop_values in class_info['properties'].items():
            ontology_prop = self._create_ontology_property(prop_name, prop_values)
            ontology_class.add_property(ontology_prop)
        
        return ontology_class
    
    def _create_ontology_relation(self, relation_name: str, relation_info: Dict[str, Any]) -> OntologyRelation:
        """
        创建本体关系
        
        Args:
            relation_name: 关系名
            relation_info: 关系信息
            
        Returns:
            本体关系实例
        """
        ontology_relation = OntologyRelation(
            name=relation_name,
            description=f"从{relation_info['count']}个实例推断的{relation_name}关系",
            instances_count=relation_info['count'],
            examples=[{'label': label} for label in relation_info['labels'][:5]]
        )
        
        # 分析属性并创建本体属性
        for prop_name, prop_values in relation_info['properties'].items():
            ontology_prop = self._create_ontology_property(prop_name, prop_values)
            ontology_relation.add_property(ontology_prop)
        
        return ontology_relation
    
    def _create_ontology_property(self, prop_name: str, prop_values: List[Any]) -> OntologyProperty:
        """
        创建本体属性
        
        Args:
            prop_name: 属性名
            prop_values: 属性值列表
            
        Returns:
            本体属性实例
        """
        # 推断数据类型
        data_type = self._infer_data_type(prop_values)
        
        # 计算统计信息
        non_null_values = [v for v in prop_values if v is not None and v != '']
        value_counts = Counter(non_null_values)
        
        # 判断是否必需（出现频率超过50%）
        required = len(non_null_values) / len(prop_values) > 0.5 if prop_values else False
        
        # 获取示例值
        examples = list(value_counts.keys())[:3]
        
        # 创建约束
        constraints = {}
        if data_type == DataType.STRING:
            if non_null_values:
                constraints['min_length'] = min(len(str(v)) for v in non_null_values)
                constraints['max_length'] = max(len(str(v)) for v in non_null_values)
        elif data_type in [DataType.INTEGER, DataType.FLOAT]:
            if non_null_values:
                numeric_values = [float(v) for v in non_null_values if self._is_numeric(v)]
                if numeric_values:
                    constraints['min_value'] = min(numeric_values)
                    constraints['max_value'] = max(numeric_values)
        
        # 如果值的种类很少，可能是枚举类型
        if len(value_counts) <= 10 and len(non_null_values) > 5:
            constraints['enum_values'] = list(value_counts.keys())
        
        return OntologyProperty(
            name=prop_name,
            data_type=data_type,
            description=f"从{len(prop_values)}个值推断的{prop_name}属性",
            required=required,
            constraints=constraints,
            examples=examples
        )
    
    def _infer_data_type(self, values: List[Any]) -> DataType:
        """
        推断数据类型
        
        Args:
            values: 值列表
            
        Returns:
            推断的数据类型
        """
        if not values:
            return DataType.UNKNOWN
        
        # 过滤空值
        non_null_values = [v for v in values if v is not None and v != '']
        if not non_null_values:
            return DataType.UNKNOWN
        
        # 统计各类型的匹配数量
        type_counts = {}
        for type_name, checker in self.type_inference_rules.items():
            count = sum(1 for v in non_null_values if checker(v))
            if count > 0:
                type_counts[type_name] = count / len(non_null_values)
        
        # 选择匹配度最高的类型（至少50%匹配）
        if type_counts:
            best_type = max(type_counts.items(), key=lambda x: x[1])
            if best_type[1] >= 0.5:
                return DataType(best_type[0])
        
        return DataType.STRING  # 默认为字符串类型
    
    def _infer_class_hierarchy(self, ontology: KnowledgeOntology, kg: KnowledgeGraph) -> None:
        """
        推断类层次结构
        
        Args:
            ontology: 本体实例
            kg: 知识图谱
        """
        # 查找is_a关系来构建层次结构
        for edge in kg.get_all_edges():
            if edge.type and 'is_a' in edge.type.lower():
                source_node = kg.get_node(edge.source_id)
                target_node = kg.get_node(edge.target_id)
                
                if source_node and target_node:
                    source_type = source_node.type
                    target_type = target_node.type
                    
                    if source_type in ontology.classes and target_type in ontology.classes:
                        ontology.classes[source_type].add_parent_class(target_type)
    
    def _infer_relation_properties(self, ontology: KnowledgeOntology, kg: KnowledgeGraph) -> None:
        """
        推断关系属性（对称性、传递性等）
        
        Args:
            ontology: 本体实例
            kg: 知识图谱
        """
        # 按关系类型分组边
        edges_by_type = defaultdict(list)
        for edge in kg.get_all_edges():
            if edge.type:
                edges_by_type[edge.type].append(edge)
        
        # 分析每种关系类型
        for relation_type, edges in edges_by_type.items():
            if relation_type in ontology.relations:
                relation = ontology.relations[relation_type]
                
                # 收集源和目标节点类型
                for edge in edges:
                    source_node = kg.get_node(edge.source_id)
                    target_node = kg.get_node(edge.target_id)
                    
                    if source_node and target_node:
                        relation.add_domain_class(source_node.type)
                        relation.add_range_class(target_node.type)
                
                # 检查对称性
                relation.is_symmetric = self._check_symmetry(edges)
                
                # 检查传递性
                relation.is_transitive = self._check_transitivity(edges)
                
                # 检查函数性
                relation.is_functional = self._check_functionality(edges)
    
    def _check_symmetry(self, edges: List[Edge]) -> bool:
        """
        检查关系是否对称
        
        Args:
            edges: 边列表
            
        Returns:
            是否对称
        """
        edge_pairs = set()
        reverse_pairs = set()
        
        for edge in edges:
            pair = (edge.source_id, edge.target_id)
            reverse_pair = (edge.target_id, edge.source_id)
            
            edge_pairs.add(pair)
            if reverse_pair in edge_pairs:
                reverse_pairs.add(pair)
        
        # 如果超过80%的边都有反向边，认为是对称的
        return len(reverse_pairs) / len(edge_pairs) > 0.8 if edge_pairs else False
    
    def _check_transitivity(self, edges: List[Edge]) -> bool:
        """
        检查关系是否传递
        
        Args:
            edges: 边列表
            
        Returns:
            是否传递
        """
        # 构建邻接表
        adjacency = defaultdict(set)
        for edge in edges:
            adjacency[edge.source_id].add(edge.target_id)
        
        transitive_count = 0
        total_possible = 0
        
        # 检查传递性：如果A->B且B->C，则应该有A->C
        for a in adjacency:
            for b in adjacency[a]:
                if b in adjacency:
                    for c in adjacency[b]:
                        total_possible += 1
                        if c in adjacency[a]:
                            transitive_count += 1
        
        # 如果超过70%满足传递性，认为是传递的
        return transitive_count / total_possible > 0.7 if total_possible > 0 else False
    
    def _check_functionality(self, edges: List[Edge]) -> bool:
        """
        检查关系是否函数性（每个主体最多对应一个客体）
        
        Args:
            edges: 边列表
            
        Returns:
            是否函数性
        """
        source_targets = defaultdict(set)
        for edge in edges:
            source_targets[edge.source_id].add(edge.target_id)
        
        # 如果超过90%的源节点只对应一个目标节点，认为是函数性的
        functional_count = sum(1 for targets in source_targets.values() if len(targets) == 1)
        return functional_count / len(source_targets) > 0.9 if source_targets else False
    
    # 数据类型检查方法
    def _is_string(self, value: Any) -> bool:
        """检查是否为字符串类型"""
        return isinstance(value, str)
    
    def _is_integer(self, value: Any) -> bool:
        """检查是否为整数类型"""
        try:
            int(value)
            return '.' not in str(value)
        except (ValueError, TypeError):
            return False
    
    def _is_float(self, value: Any) -> bool:
        """检查是否为浮点数类型"""
        try:
            float(value)
            return '.' in str(value)
        except (ValueError, TypeError):
            return False
    
    def _is_boolean(self, value: Any) -> bool:
        """检查是否为布尔类型"""
        return isinstance(value, bool) or str(value).lower() in ['true', 'false', '1', '0']
    
    def _is_date(self, value: Any) -> bool:
        """检查是否为日期类型"""
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',
            r'\d{2}/\d{2}/\d{4}',
            r'\d{2}-\d{2}-\d{4}'
        ]
        value_str = str(value)
        return any(re.match(pattern, value_str) for pattern in date_patterns)
    
    def _is_datetime(self, value: Any) -> bool:
        """检查是否为日期时间类型"""
        datetime_patterns = [
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',
            r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
        ]
        value_str = str(value)
        return any(re.match(pattern, value_str) for pattern in datetime_patterns)
    
    def _is_uri(self, value: Any) -> bool:
        """检查是否为URI类型"""
        uri_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return re.match(uri_pattern, str(value)) is not None
    
    def _is_numeric(self, value: Any) -> bool:
        """检查是否为数值类型"""
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False