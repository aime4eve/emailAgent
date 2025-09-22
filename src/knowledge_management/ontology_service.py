# -*- coding: utf-8 -*-
"""
知识本体管理服务
提供本体的CRUD操作、文件管理、导入导出等功能
"""

import os
import json
import uuid
import shutil
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

from .ontology_model import Ontology, EntityType, RelationType


class OntologyService:
    """知识本体管理服务类"""
    
    def __init__(self, storage_path: str = "ontologies"):
        """初始化本体服务
        
        Args:
            storage_path: 本体存储目录路径
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        # 创建子目录
        self.json_path = self.storage_path / "json"
        self.backup_path = self.storage_path / "backup"
        self.export_path = self.storage_path / "export"
        
        for path in [self.json_path, self.backup_path, self.export_path]:
            path.mkdir(exist_ok=True)
    
    def create_ontology(self, ontology_data: Dict[str, Any]) -> Ontology:
        """创建新的本体
        
        Args:
            ontology_data: 本体数据字典
            
        Returns:
            创建的本体对象
        """
        # 生成唯一ID
        if 'id' not in ontology_data or not ontology_data['id']:
            ontology_data['id'] = str(uuid.uuid4())
        
        # 创建本体对象
        ontology = Ontology.from_dict(ontology_data)
        
        # 验证本体
        errors = ontology.validate()
        if errors:
            raise ValueError(f"本体验证失败: {'; '.join(errors)}")
        
        # 保存到文件
        file_path = self.json_path / f"{ontology.id}.json"
        ontology.save_to_file(str(file_path))
        
        return ontology
    
    def get_ontology(self, ontology_id: str) -> Optional[Ontology]:
        """根据ID获取本体
        
        Args:
            ontology_id: 本体ID
            
        Returns:
            本体对象，如果不存在则返回None
        """
        file_path = self.json_path / f"{ontology_id}.json"
        if not file_path.exists():
            return None
        
        try:
            return Ontology.load_from_file(str(file_path))
        except Exception as e:
            print(f"加载本体失败: {e}")
            return None
    
    def update_ontology(self, ontology_id: str, ontology_data: Dict[str, Any]) -> Optional[Ontology]:
        """更新本体
        
        Args:
            ontology_id: 本体ID
            ontology_data: 更新的本体数据
            
        Returns:
            更新后的本体对象，如果不存在则返回None
        """
        # 检查本体是否存在
        existing_ontology = self.get_ontology(ontology_id)
        if not existing_ontology:
            return None
        
        # 备份原本体
        self._backup_ontology(ontology_id)
        
        # 更新数据
        ontology_data['id'] = ontology_id
        ontology_data['updated_at'] = datetime.now().isoformat()
        
        # 创建更新后的本体对象
        updated_ontology = Ontology.from_dict(ontology_data)
        
        # 验证本体
        errors = updated_ontology.validate()
        if errors:
            raise ValueError(f"本体验证失败: {'; '.join(errors)}")
        
        # 保存到文件
        file_path = self.json_path / f"{ontology_id}.json"
        updated_ontology.save_to_file(str(file_path))
        
        return updated_ontology
    
    def delete_ontology(self, ontology_id: str) -> bool:
        """删除本体
        
        Args:
            ontology_id: 本体ID
            
        Returns:
            删除成功返回True，否则返回False
        """
        file_path = self.json_path / f"{ontology_id}.json"
        if not file_path.exists():
            return False
        
        # 备份后删除
        self._backup_ontology(ontology_id)
        file_path.unlink()
        
        return True
    
    def list_ontologies(self, page: int = 1, page_size: int = 10, 
                       search_term: str = None, tags: List[str] = None) -> Dict[str, Any]:
        """获取本体列表
        
        Args:
            page: 页码
            page_size: 每页大小
            search_term: 搜索关键词
            tags: 标签过滤
            
        Returns:
            包含本体列表和分页信息的字典
        """
        ontologies = []
        
        # 遍历所有本体文件
        for file_path in self.json_path.glob("*.json"):
            try:
                ontology = Ontology.load_from_file(str(file_path))
                
                # 应用搜索过滤
                if search_term:
                    search_lower = search_term.lower()
                    if (search_lower not in ontology.name.lower() and 
                        search_lower not in ontology.description.lower()):
                        continue
                
                # 应用标签过滤
                if tags:
                    if not any(tag in ontology.tags for tag in tags):
                        continue
                
                # 添加基本信息
                ontologies.append({
                    'id': ontology.id,
                    'name': ontology.name,
                    'description': ontology.description,
                    'version': ontology.version,
                    'author': ontology.author,
                    'tags': ontology.tags,
                    'entity_count': len(ontology.entity_types),
                    'relation_count': len(ontology.relation_types),
                    'created_at': ontology.created_at.isoformat() if ontology.created_at else None,
                    'updated_at': ontology.updated_at.isoformat() if ontology.updated_at else None
                })
            except Exception as e:
                print(f"加载本体文件 {file_path} 失败: {e}")
                continue
        
        # 按更新时间排序
        ontologies.sort(key=lambda x: x['updated_at'] or '', reverse=True)
        
        # 分页
        total = len(ontologies)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        page_ontologies = ontologies[start_idx:end_idx]
        
        return {
            'ontologies': page_ontologies,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }
    
    def import_ontology(self, file_path: str, file_format: str = 'json') -> Ontology:
        """导入本体文件
        
        Args:
            file_path: 文件路径
            file_format: 文件格式 (json, owl, rdf)
            
        Returns:
            导入的本体对象
        """
        if file_format.lower() == 'json':
            return self._import_json(file_path)
        elif file_format.lower() in ['owl', 'rdf']:
            return self._import_owl_rdf(file_path, file_format)
        else:
            raise ValueError(f"不支持的文件格式: {file_format}")
    
    def export_ontology(self, ontology_id: str, file_format: str = 'json') -> str:
        """导出本体文件
        
        Args:
            ontology_id: 本体ID
            file_format: 导出格式 (json, owl, rdf)
            
        Returns:
            导出文件的路径
        """
        ontology = self.get_ontology(ontology_id)
        if not ontology:
            raise ValueError(f"本体 {ontology_id} 不存在")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if file_format.lower() == 'json':
            export_file = self.export_path / f"{ontology.name}_{timestamp}.json"
            ontology.save_to_file(str(export_file))
        elif file_format.lower() == 'owl':
            export_file = self.export_path / f"{ontology.name}_{timestamp}.owl"
            self._export_owl(ontology, str(export_file))
        elif file_format.lower() == 'rdf':
            export_file = self.export_path / f"{ontology.name}_{timestamp}.rdf"
            self._export_rdf(ontology, str(export_file))
        else:
            raise ValueError(f"不支持的导出格式: {file_format}")
        
        return str(export_file)
    
    def get_ontology_statistics(self) -> Dict[str, Any]:
        """获取本体统计信息
        
        Returns:
            统计信息字典
        """
        total_ontologies = 0
        total_entities = 0
        total_relations = 0
        authors = set()
        tags = set()
        
        for file_path in self.json_path.glob("*.json"):
            try:
                ontology = Ontology.load_from_file(str(file_path))
                total_ontologies += 1
                total_entities += len(ontology.entity_types)
                total_relations += len(ontology.relation_types)
                if ontology.author:
                    authors.add(ontology.author)
                tags.update(ontology.tags)
            except Exception:
                continue
        
        return {
            'total_ontologies': total_ontologies,
            'total_entities': total_entities,
            'total_relations': total_relations,
            'unique_authors': len(authors),
            'unique_tags': len(tags),
            'all_tags': list(tags)
        }
    
    def _backup_ontology(self, ontology_id: str) -> None:
        """备份本体文件
        
        Args:
            ontology_id: 本体ID
        """
        source_file = self.json_path / f"{ontology_id}.json"
        if source_file.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_path / f"{ontology_id}_{timestamp}.json"
            shutil.copy2(source_file, backup_file)
    
    def _import_json(self, file_path: str) -> Ontology:
        """导入JSON格式本体
        
        Args:
            file_path: JSON文件路径
            
        Returns:
            导入的本体对象
        """
        ontology = Ontology.load_from_file(file_path)
        
        # 生成新的ID避免冲突
        ontology.id = str(uuid.uuid4())
        ontology.created_at = datetime.now()
        ontology.updated_at = datetime.now()
        
        # 验证并保存
        errors = ontology.validate()
        if errors:
            raise ValueError(f"导入的本体验证失败: {'; '.join(errors)}")
        
        save_path = self.json_path / f"{ontology.id}.json"
        ontology.save_to_file(str(save_path))
        
        return ontology
    
    def _import_owl_rdf(self, file_path: str, file_format: str) -> Ontology:
        """导入OWL/RDF格式本体
        
        Args:
            file_path: 文件路径
            file_format: 文件格式
            
        Returns:
            导入的本体对象
        """
        # 这里是简化实现，实际应该使用rdflib等库解析OWL/RDF
        # 目前返回一个基本的本体结构
        ontology_id = str(uuid.uuid4())
        file_name = Path(file_path).stem
        
        ontology = Ontology(
            id=ontology_id,
            name=f"Imported_{file_name}",
            description=f"从 {file_format.upper()} 文件导入的本体",
            version="1.0.0"
        )
        
        # 保存到文件
        save_path = self.json_path / f"{ontology.id}.json"
        ontology.save_to_file(str(save_path))
        
        return ontology
    
    def _export_owl(self, ontology: Ontology, file_path: str) -> None:
        """导出为OWL格式
        
        Args:
            ontology: 本体对象
            file_path: 导出文件路径
        """
        # 简化的OWL导出实现
        owl_content = f'''<?xml version="1.0"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:owl="http://www.w3.org/2002/07/owl#"
         xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#">

<owl:Ontology rdf:about="{ontology.namespace or '#'}">
    <rdfs:label>{ontology.name}</rdfs:label>
    <rdfs:comment>{ontology.description}</rdfs:comment>
    <owl:versionInfo>{ontology.version}</owl:versionInfo>
</owl:Ontology>

'''
        
        # 添加实体类型
        for entity_type in ontology.entity_types:
            owl_content += f'''<owl:Class rdf:about="#{entity_type.id}">
    <rdfs:label>{entity_type.name}</rdfs:label>
    <rdfs:comment>{entity_type.description}</rdfs:comment>
</owl:Class>

'''
        
        # 添加关系类型
        for relation_type in ontology.relation_types:
            owl_content += f'''<owl:ObjectProperty rdf:about="#{relation_type.id}">
    <rdfs:label>{relation_type.name}</rdfs:label>
    <rdfs:comment>{relation_type.description}</rdfs:comment>
</owl:ObjectProperty>

'''
        
        owl_content += '</rdf:RDF>'
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(owl_content)
    
    def _export_rdf(self, ontology: Ontology, file_path: str) -> None:
        """导出为RDF格式
        
        Args:
            ontology: 本体对象
            file_path: 导出文件路径
        """
        # 简化的RDF导出实现
        rdf_content = f'''<?xml version="1.0"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#">

<rdf:Description rdf:about="{ontology.namespace or '#'}">
    <rdfs:label>{ontology.name}</rdfs:label>
    <rdfs:comment>{ontology.description}</rdfs:comment>
</rdf:Description>

'''
        
        # 添加实体类型
        for entity_type in ontology.entity_types:
            rdf_content += f'''<rdf:Description rdf:about="#{entity_type.id}">
    <rdf:type rdf:resource="http://www.w3.org/2000/01/rdf-schema#Class"/>
    <rdfs:label>{entity_type.name}</rdfs:label>
    <rdfs:comment>{entity_type.description}</rdfs:comment>
</rdf:Description>

'''
        
        # 添加关系类型
        for relation_type in ontology.relation_types:
            rdf_content += f'''<rdf:Description rdf:about="#{relation_type.id}">
    <rdf:type rdf:resource="http://www.w3.org/1999/02/22-rdf-syntax-ns#Property"/>
    <rdfs:label>{relation_type.name}</rdfs:label>
    <rdfs:comment>{relation_type.description}</rdfs:comment>
</rdf:Description>

'''
        
        rdf_content += '</rdf:RDF>'
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(rdf_content)