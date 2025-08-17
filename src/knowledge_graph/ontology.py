# -*- coding: utf-8 -*-
"""
知识本体相关类定义
"""

from typing import Dict, List, Set, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import json
from datetime import datetime


class DataType(Enum):
    """数据类型枚举"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    URI = "uri"
    UNKNOWN = "unknown"


@dataclass
class OntologyProperty:
    """本体属性类"""
    name: str
    data_type: DataType
    description: Optional[str] = None
    required: bool = False
    default_value: Any = None
    constraints: Dict[str, Any] = field(default_factory=dict)
    examples: List[Any] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'data_type': self.data_type.value,
            'description': self.description,
            'required': self.required,
            'default_value': self.default_value,
            'constraints': self.constraints,
            'examples': self.examples
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OntologyProperty':
        return cls(
            name=data['name'],
            data_type=DataType(data['data_type']),
            description=data.get('description'),
            required=data.get('required', False),
            default_value=data.get('default_value'),
            constraints=data.get('constraints', {}),
            examples=data.get('examples', [])
        )


@dataclass
class OntologyClass:
    """本体类"""
    name: str
    description: Optional[str] = None
    parent_classes: Set[str] = field(default_factory=set)
    properties: Dict[str, OntologyProperty] = field(default_factory=dict)
    instances_count: int = 0
    examples: List[str] = field(default_factory=list)
    
    def add_property(self, prop: OntologyProperty) -> None:
        """添加属性"""
        self.properties[prop.name] = prop
    
    def remove_property(self, prop_name: str) -> None:
        """移除属性"""
        if prop_name in self.properties:
            del self.properties[prop_name]
    
    def add_parent_class(self, parent_name: str) -> None:
        """添加父类"""
        self.parent_classes.add(parent_name)
    
    def remove_parent_class(self, parent_name: str) -> None:
        """移除父类"""
        self.parent_classes.discard(parent_name)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'description': self.description,
            'parent_classes': list(self.parent_classes),
            'properties': {name: prop.to_dict() for name, prop in self.properties.items()},
            'instances_count': self.instances_count,
            'examples': self.examples
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OntologyClass':
        ontology_class = cls(
            name=data['name'],
            description=data.get('description'),
            parent_classes=set(data.get('parent_classes', [])),
            instances_count=data.get('instances_count', 0),
            examples=data.get('examples', [])
        )
        
        for prop_name, prop_data in data.get('properties', {}).items():
            ontology_class.add_property(OntologyProperty.from_dict(prop_data))
        
        return ontology_class


@dataclass
class OntologyRelation:
    """本体关系类"""
    name: str
    description: Optional[str] = None
    domain_classes: Set[str] = field(default_factory=set)  # 主体类
    range_classes: Set[str] = field(default_factory=set)   # 客体类
    properties: Dict[str, OntologyProperty] = field(default_factory=dict)
    is_symmetric: bool = False
    is_transitive: bool = False
    is_functional: bool = False
    instances_count: int = 0
    examples: List[Dict[str, str]] = field(default_factory=list)
    
    def add_domain_class(self, class_name: str) -> None:
        """添加定义域类"""
        self.domain_classes.add(class_name)
    
    def add_range_class(self, class_name: str) -> None:
        """添加值域类"""
        self.range_classes.add(class_name)
    
    def add_property(self, prop: OntologyProperty) -> None:
        """添加属性"""
        self.properties[prop.name] = prop
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'description': self.description,
            'domain_classes': list(self.domain_classes),
            'range_classes': list(self.range_classes),
            'properties': {name: prop.to_dict() for name, prop in self.properties.items()},
            'is_symmetric': self.is_symmetric,
            'is_transitive': self.is_transitive,
            'is_functional': self.is_functional,
            'instances_count': self.instances_count,
            'examples': self.examples
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OntologyRelation':
        relation = cls(
            name=data['name'],
            description=data.get('description'),
            domain_classes=set(data.get('domain_classes', [])),
            range_classes=set(data.get('range_classes', [])),
            is_symmetric=data.get('is_symmetric', False),
            is_transitive=data.get('is_transitive', False),
            is_functional=data.get('is_functional', False),
            instances_count=data.get('instances_count', 0),
            examples=data.get('examples', [])
        )
        
        for prop_name, prop_data in data.get('properties', {}).items():
            relation.add_property(OntologyProperty.from_dict(prop_data))
        
        return relation


@dataclass
class KnowledgeOntology:
    """知识本体类"""
    name: str
    version: str = "1.0.0"
    description: Optional[str] = None
    namespace: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    classes: Dict[str, OntologyClass] = field(default_factory=dict)
    relations: Dict[str, OntologyRelation] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_class(self, ontology_class: OntologyClass) -> None:
        """添加类"""
        self.classes[ontology_class.name] = ontology_class
        self.updated_at = datetime.now()
    
    def remove_class(self, class_name: str) -> None:
        """移除类"""
        if class_name in self.classes:
            del self.classes[class_name]
            self.updated_at = datetime.now()
    
    def add_relation(self, relation: OntologyRelation) -> None:
        """添加关系"""
        self.relations[relation.name] = relation
        self.updated_at = datetime.now()
    
    def remove_relation(self, relation_name: str) -> None:
        """移除关系"""
        if relation_name in self.relations:
            del self.relations[relation_name]
            self.updated_at = datetime.now()
    
    def get_class_hierarchy(self) -> Dict[str, List[str]]:
        """获取类层次结构"""
        hierarchy = {}
        for class_name, ontology_class in self.classes.items():
            hierarchy[class_name] = list(ontology_class.parent_classes)
        return hierarchy
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        total_properties = sum(len(cls.properties) for cls in self.classes.values())
        total_instances = sum(cls.instances_count for cls in self.classes.values())
        total_relation_instances = sum(rel.instances_count for rel in self.relations.values())
        
        return {
            'classes_count': len(self.classes),
            'relations_count': len(self.relations),
            'properties_count': total_properties,
            'instances_count': total_instances,
            'relation_instances_count': total_relation_instances,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'namespace': self.namespace,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'classes': {name: cls.to_dict() for name, cls in self.classes.items()},
            'relations': {name: rel.to_dict() for name, rel in self.relations.items()},
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KnowledgeOntology':
        ontology = cls(
            name=data['name'],
            version=data.get('version', '1.0.0'),
            description=data.get('description'),
            namespace=data.get('namespace'),
            created_at=datetime.fromisoformat(data.get('created_at', datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get('updated_at', datetime.now().isoformat())),
            metadata=data.get('metadata', {})
        )
        
        # 添加类
        for class_name, class_data in data.get('classes', {}).items():
            ontology.add_class(OntologyClass.from_dict(class_data))
        
        # 添加关系
        for relation_name, relation_data in data.get('relations', {}).items():
            ontology.add_relation(OntologyRelation.from_dict(relation_data))
        
        return ontology
    
    def export_to_json(self, file_path: str) -> None:
        """导出为JSON文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
    
    @classmethod
    def import_from_json(cls, file_path: str) -> 'KnowledgeOntology':
        """从JSON文件导入"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)
    
    def export_to_owl(self, file_path: str) -> None:
        """导出为OWL格式文件"""
        owl_content = self._generate_owl_content()
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(owl_content)
    
    def export_to_rdf(self, file_path: str) -> None:
        """导出为RDF格式文件"""
        rdf_content = self._generate_rdf_content()
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(rdf_content)
    
    def _generate_owl_content(self) -> str:
        """生成OWL格式内容"""
        namespace = self.namespace or f"http://example.org/{self.name.lower().replace(' ', '_')}"
        
        owl_lines = [
            '<?xml version="1.0"?>',
            f'<rdf:RDF xmlns="{namespace}#"',
            f'     xml:base="{namespace}"',
            '     xmlns:owl="http://www.w3.org/2002/07/owl#"',
            '     xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"',
            '     xmlns:xml="http://www.w3.org/XML/1998/namespace"',
            '     xmlns:xsd="http://www.w3.org/2001/XMLSchema#"',
            '     xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#">',
            f'    <owl:Ontology rdf:about="{namespace}">',
            f'        <rdfs:label>{self.name}</rdfs:label>',
        ]
        
        if self.description:
            owl_lines.append(f'        <rdfs:comment>{self.description}</rdfs:comment>')
        
        owl_lines.extend([
            f'        <owl:versionInfo>{self.version}</owl:versionInfo>',
            '    </owl:Ontology>',
            ''
        ])
        
        # 添加类定义
        for class_name, ontology_class in self.classes.items():
            owl_lines.extend([
                f'    <!-- {class_name} -->',
                f'    <owl:Class rdf:about="#{class_name}">',
                f'        <rdfs:label>{class_name}</rdfs:label>'
            ])
            
            if ontology_class.description:
                owl_lines.append(f'        <rdfs:comment>{ontology_class.description}</rdfs:comment>')
            
            # 添加父类关系
            for parent_class in ontology_class.parent_classes:
                owl_lines.append(f'        <rdfs:subClassOf rdf:resource="#{parent_class}"/>')
            
            owl_lines.append('    </owl:Class>')
            owl_lines.append('')
        
        # 添加属性定义
        for class_name, ontology_class in self.classes.items():
            for prop_name, prop in ontology_class.properties.items():
                owl_lines.extend([
                    f'    <!-- {prop_name} -->',
                    f'    <owl:DatatypeProperty rdf:about="#{prop_name}">',
                    f'        <rdfs:label>{prop_name}</rdfs:label>',
                    f'        <rdfs:domain rdf:resource="#{class_name}"/>'
                ])
                
                if prop.description:
                    owl_lines.append(f'        <rdfs:comment>{prop.description}</rdfs:comment>')
                
                # 添加数据类型
                xsd_type = self._get_xsd_type(prop.data_type)
                owl_lines.append(f'        <rdfs:range rdf:resource="{xsd_type}"/>')
                
                owl_lines.append('    </owl:DatatypeProperty>')
                owl_lines.append('')
        
        # 添加关系定义
        for relation_name, relation in self.relations.items():
            owl_lines.extend([
                f'    <!-- {relation_name} -->',
                f'    <owl:ObjectProperty rdf:about="#{relation_name}">',
                f'        <rdfs:label>{relation_name}</rdfs:label>'
            ])
            
            if relation.description:
                owl_lines.append(f'        <rdfs:comment>{relation.description}</rdfs:comment>')
            
            # 添加定义域和值域
            for domain_class in relation.domain_classes:
                owl_lines.append(f'        <rdfs:domain rdf:resource="#{domain_class}"/>')
            
            for range_class in relation.range_classes:
                owl_lines.append(f'        <rdfs:range rdf:resource="#{range_class}"/>')
            
            # 添加关系属性
            if relation.is_symmetric:
                owl_lines.append('        <rdf:type rdf:resource="http://www.w3.org/2002/07/owl#SymmetricProperty"/>')
            
            if relation.is_transitive:
                owl_lines.append('        <rdf:type rdf:resource="http://www.w3.org/2002/07/owl#TransitiveProperty"/>')
            
            if relation.is_functional:
                owl_lines.append('        <rdf:type rdf:resource="http://www.w3.org/2002/07/owl#FunctionalProperty"/>')
            
            owl_lines.append('    </owl:ObjectProperty>')
            owl_lines.append('')
        
        owl_lines.append('</rdf:RDF>')
        return '\n'.join(owl_lines)
    
    def _generate_rdf_content(self) -> str:
        """生成RDF格式内容"""
        namespace = self.namespace or f"http://example.org/{self.name.lower().replace(' ', '_')}"
        
        rdf_lines = [
            '<?xml version="1.0"?>',
            '<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"',
            '         xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"',
            f'         xmlns:kg="{namespace}#">',
            ''
        ]
        
        # 添加本体信息
        rdf_lines.extend([
            f'  <rdf:Description rdf:about="{namespace}">',
            f'    <rdfs:label>{self.name}</rdfs:label>',
        ])
        
        if self.description:
            rdf_lines.append(f'    <rdfs:comment>{self.description}</rdfs:comment>')
        
        rdf_lines.extend([
            f'    <kg:version>{self.version}</kg:version>',
            f'    <kg:createdAt>{self.created_at.isoformat()}</kg:createdAt>',
            f'    <kg:updatedAt>{self.updated_at.isoformat()}</kg:updatedAt>',
            '  </rdf:Description>',
            ''
        ])
        
        # 添加类信息
        for class_name, ontology_class in self.classes.items():
            rdf_lines.extend([
                f'  <rdf:Description rdf:about="{namespace}#{class_name}">',
                '    <rdf:type rdf:resource="http://www.w3.org/2000/01/rdf-schema#Class"/>',
                f'    <rdfs:label>{class_name}</rdfs:label>'
            ])
            
            if ontology_class.description:
                rdf_lines.append(f'    <rdfs:comment>{ontology_class.description}</rdfs:comment>')
            
            rdf_lines.append(f'    <kg:instancesCount>{ontology_class.instances_count}</kg:instancesCount>')
            
            # 添加父类关系
            for parent_class in ontology_class.parent_classes:
                rdf_lines.append(f'    <rdfs:subClassOf rdf:resource="{namespace}#{parent_class}"/>')
            
            rdf_lines.append('  </rdf:Description>')
            rdf_lines.append('')
        
        # 添加关系信息
        for relation_name, relation in self.relations.items():
            rdf_lines.extend([
                f'  <rdf:Description rdf:about="{namespace}#{relation_name}">',
                '    <rdf:type rdf:resource="http://www.w3.org/1999/02/22-rdf-syntax-ns#Property"/>',
                f'    <rdfs:label>{relation_name}</rdfs:label>'
            ])
            
            if relation.description:
                rdf_lines.append(f'    <rdfs:comment>{relation.description}</rdfs:comment>')
            
            rdf_lines.append(f'    <kg:instancesCount>{relation.instances_count}</kg:instancesCount>')
            
            # 添加定义域和值域
            for domain_class in relation.domain_classes:
                rdf_lines.append(f'    <rdfs:domain rdf:resource="{namespace}#{domain_class}"/>')
            
            for range_class in relation.range_classes:
                rdf_lines.append(f'    <rdfs:range rdf:resource="{namespace}#{range_class}"/>')
            
            # 添加关系属性
            if relation.is_symmetric:
                rdf_lines.append('    <kg:isSymmetric>true</kg:isSymmetric>')
            
            if relation.is_transitive:
                rdf_lines.append('    <kg:isTransitive>true</kg:isTransitive>')
            
            if relation.is_functional:
                rdf_lines.append('    <kg:isFunctional>true</kg:isFunctional>')
            
            rdf_lines.append('  </rdf:Description>')
            rdf_lines.append('')
        
        rdf_lines.append('</rdf:RDF>')
        return '\n'.join(rdf_lines)
    
    def _get_xsd_type(self, data_type: DataType) -> str:
        """获取XSD数据类型"""
        type_mapping = {
            DataType.STRING: 'http://www.w3.org/2001/XMLSchema#string',
            DataType.INTEGER: 'http://www.w3.org/2001/XMLSchema#integer',
            DataType.FLOAT: 'http://www.w3.org/2001/XMLSchema#float',
            DataType.BOOLEAN: 'http://www.w3.org/2001/XMLSchema#boolean',
            DataType.DATE: 'http://www.w3.org/2001/XMLSchema#date',
            DataType.DATETIME: 'http://www.w3.org/2001/XMLSchema#dateTime',
            DataType.URI: 'http://www.w3.org/2001/XMLSchema#anyURI',
            DataType.UNKNOWN: 'http://www.w3.org/2001/XMLSchema#string'
        }
        return type_mapping.get(data_type, 'http://www.w3.org/2001/XMLSchema#string')