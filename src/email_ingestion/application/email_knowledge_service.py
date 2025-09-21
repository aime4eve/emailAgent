# -*- coding: utf-8 -*-
"""
邮件知识抽取服务
从邮件内容中抽取知识并构建图谱
"""

import re
import logging
import uuid
from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime
from email.utils import parseaddr, parsedate_to_datetime
from collections import defaultdict, Counter

from ..domain.model.email import Email
from ...knowledge_management.domain.model.extraction import (
    ExtractedEntity, ExtractedRelation, ExtractionResult,
    EntityType, RelationType
)
from ...knowledge_management.application.entity_extraction_service import (
    EntityExtractionService
)


class EmailKnowledgeServiceError(Exception):
    """邮件知识抽取服务异常"""
    pass


class EmailNetworkAnalysis:
    """邮件网络分析结果"""
    
    def __init__(self):
        self.communication_graph: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.email_frequency: Dict[str, int] = defaultdict(int)
        self.collaboration_patterns: Dict[str, List[str]] = defaultdict(list)
        self.time_patterns: Dict[str, List[datetime]] = defaultdict(list)
        self.topic_distribution: Dict[str, Counter] = defaultdict(Counter)
    
    def add_communication(self, sender: str, recipient: str, timestamp: datetime, topics: List[str]):
        """添加通信记录"""
        self.communication_graph[sender][recipient] += 1
        self.email_frequency[sender] += 1
        self.time_patterns[sender].append(timestamp)
        
        for topic in topics:
            self.topic_distribution[sender][topic] += 1
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取网络分析统计信息"""
        total_communications = sum(
            sum(recipients.values()) for recipients in self.communication_graph.values()
        )
        
        unique_senders = len(self.communication_graph)
        unique_recipients = len(set(
            recipient for recipients in self.communication_graph.values()
            for recipient in recipients.keys()
        ))
        
        return {
            'total_communications': total_communications,
            'unique_senders': unique_senders,
            'unique_recipients': unique_recipients,
            'average_emails_per_sender': total_communications / max(unique_senders, 1),
            'most_active_sender': max(self.email_frequency.items(), key=lambda x: x[1])[0] if self.email_frequency else None,
            'communication_density': total_communications / max(unique_senders * unique_recipients, 1)
        }


class EmailKnowledgeService:
    """邮件知识抽取服务"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.entity_extraction_service = EntityExtractionService()
        self._init_patterns()
    
    def _init_patterns(self):
        """初始化邮件特定的模式"""
        # 邮件地址模式
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        
        # 项目名称模式
        self.project_patterns = [
            r'项目[：:]\s*([^\n\r，。；！？]+)',
            r'([^\n\r，。；！？]+)项目',
            r'Project[：:]\s*([^\n\r，。；！？]+)',
        ]
        
        # 任务模式
        self.task_patterns = [
            r'任务[：:]\s*([^\n\r，。；！？]+)',
            r'Task[：:]\s*([^\n\r，。；！？]+)',
            r'需要([^\n\r，。；！？]+)',
            r'完成([^\n\r，。；！？]+)',
        ]
        
        # 会议模式
        self.meeting_patterns = [
            r'会议[：:]\s*([^\n\r，。；！？]+)',
            r'Meeting[：:]\s*([^\n\r，。；！？]+)',
            r'讨论([^\n\r，。；！？]+)',
        ]
        
        # 时间模式
        self.time_patterns = [
            r'(\d{4}年\d{1,2}月\d{1,2}日)',
            r'(\d{1,2}月\d{1,2}日)',
            r'(明天|后天|下周|下个月)',
            r'(\d{1,2}[：:]\d{2})',
        ]
        
        # 关系指示词
        self.relation_indicators = {
            RelationType.WORK_FOR: ['工作于', '任职于', '在', '供职于'],
            RelationType.COLLABORATE_WITH: ['合作', '协作', '配合', '一起', '共同'],
            RelationType.REPORT_TO: ['汇报', '报告', '向', '请示'],
            RelationType.PARTICIPATE_IN: ['参与', '参加', '加入', '出席'],
        }
    
    def extract_knowledge_from_email(self, email: Email) -> ExtractionResult:
        """从单个邮件中抽取知识
        
        Args:
            email: 邮件对象
            
        Returns:
            抽取结果
        """
        self.logger.info(f"开始从邮件中抽取知识: {email.subject}")
        
        try:
            # 构建完整的邮件文本
            full_text = self._build_email_text(email)
            
            # 使用通用实体抽取服务
            base_result = self.entity_extraction_service.extract_from_text(
                full_text, 
                document_id=f"email_{uuid.uuid4()}"
            )
            
            # 添加邮件特定的实体和关系
            email_entities = self._extract_email_specific_entities(email, full_text)
            email_relations = self._extract_email_specific_relations(email, full_text, 
                                                                   base_result.entities + email_entities)
            
            # 合并结果
            all_entities = base_result.entities + email_entities
            all_relations = base_result.relations + email_relations
            
            # 创建最终结果
            result = ExtractionResult(
                document_id=base_result.document_id,
                document_path=f"email://{email.sender}/{email.subject}",
                entities=all_entities,
                relations=all_relations,
                processing_time=base_result.processing_time,
                metadata={
                    **base_result.metadata,
                    'email_sender': email.sender,
                    'email_subject': email.subject,
                    'email_attachments_count': len(email.attachments),
                    'extraction_type': 'email_knowledge'
                }
            )
            
            self.logger.info(
                f"邮件知识抽取完成: {email.subject}, "
                f"实体数: {len(all_entities)}, 关系数: {len(all_relations)}"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"邮件知识抽取失败: {email.subject}, 错误: {str(e)}")
            raise EmailKnowledgeServiceError(f"邮件知识抽取失败: {str(e)}")
    
    def extract_knowledge_from_emails(self, emails: List[Email]) -> List[ExtractionResult]:
        """从多个邮件中批量抽取知识
        
        Args:
            emails: 邮件列表
            
        Returns:
            抽取结果列表
        """
        self.logger.info(f"开始批量邮件知识抽取，邮件数量: {len(emails)}")
        
        results = []
        errors = []
        
        for i, email in enumerate(emails, 1):
            try:
                self.logger.info(f"处理邮件 {i}/{len(emails)}: {email.subject}")
                result = self.extract_knowledge_from_email(email)
                results.append(result)
                
            except Exception as e:
                error_msg = f"处理邮件失败 {email.subject}: {str(e)}"
                self.logger.error(error_msg)
                errors.append(error_msg)
        
        self.logger.info(
            f"批量邮件知识抽取完成，成功: {len(results)}, 失败: {len(errors)}"
        )
        
        return results
    
    def analyze_email_network(self, emails: List[Email]) -> EmailNetworkAnalysis:
        """分析邮件通信网络
        
        Args:
            emails: 邮件列表
            
        Returns:
            邮件网络分析结果
        """
        self.logger.info(f"开始邮件网络分析，邮件数量: {len(emails)}")
        
        analysis = EmailNetworkAnalysis()
        
        try:
            for email in emails:
                # 解析发件人
                sender = self._extract_email_address(email.sender)
                
                # 解析收件人（这里简化处理，实际应该从邮件头中提取）
                recipients = self._extract_recipients_from_content(email.content)
                
                # 提取主题关键词作为话题
                topics = self._extract_topics_from_subject(email.subject)
                
                # 估算时间（这里使用当前时间，实际应该从邮件头中提取）
                timestamp = datetime.now()
                
                # 添加通信记录
                for recipient in recipients:
                    analysis.add_communication(sender, recipient, timestamp, topics)
            
            self.logger.info("邮件网络分析完成")
            
        except Exception as e:
            self.logger.error(f"邮件网络分析失败: {str(e)}")
            raise EmailKnowledgeServiceError(f"邮件网络分析失败: {str(e)}")
        
        return analysis
    
    def _build_email_text(self, email: Email) -> str:
        """构建完整的邮件文本"""
        text_parts = []
        
        # 添加主题
        if email.subject:
            text_parts.append(f"主题: {email.subject}")
        
        # 添加发件人
        if email.sender:
            text_parts.append(f"发件人: {email.sender}")
        
        # 添加正文
        if email.content:
            text_parts.append(f"内容: {email.content}")
        
        # 添加附件信息
        if email.attachments:
            attachment_names = [att.get('filename', '未知附件') for att in email.attachments]
            text_parts.append(f"附件: {', '.join(attachment_names)}")
        
        return "\n".join(text_parts)
    
    def _extract_email_specific_entities(self, email: Email, full_text: str) -> List[ExtractedEntity]:
        """抽取邮件特定的实体"""
        entities = []
        
        # 抽取邮件地址
        email_addresses = self.email_pattern.findall(full_text)
        for addr in email_addresses:
            entity = ExtractedEntity(
                entity_id=str(uuid.uuid4()),
                text=addr,
                entity_type=EntityType.PERSON,  # 邮件地址通常代表人员
                confidence=0.9,
                start_pos=full_text.find(addr),
                end_pos=full_text.find(addr) + len(addr),
                properties={'email_address': addr, 'entity_source': 'email_pattern'}
            )
            entities.append(entity)
        
        # 抽取项目名称
        entities.extend(self._extract_entities_by_patterns(
            full_text, self.project_patterns, EntityType.PRODUCT, 'project'
        ))
        
        # 抽取任务
        entities.extend(self._extract_entities_by_patterns(
            full_text, self.task_patterns, EntityType.EVENT, 'task'
        ))
        
        # 抽取会议
        entities.extend(self._extract_entities_by_patterns(
            full_text, self.meeting_patterns, EntityType.EVENT, 'meeting'
        ))
        
        # 抽取时间
        entities.extend(self._extract_entities_by_patterns(
            full_text, self.time_patterns, EntityType.DATE, 'time'
        ))
        
        return entities
    
    def _extract_entities_by_patterns(self, text: str, patterns: List[str], 
                                     entity_type: EntityType, source: str) -> List[ExtractedEntity]:
        """使用模式抽取实体"""
        entities = []
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entity_text = match.group(1) if match.groups() else match.group()
                entity_text = entity_text.strip()
                
                if len(entity_text) > 1:  # 过滤单字符
                    entity = ExtractedEntity(
                        entity_id=str(uuid.uuid4()),
                        text=entity_text,
                        entity_type=entity_type,
                        confidence=0.8,
                        start_pos=match.start(),
                        end_pos=match.end(),
                        properties={'entity_source': f'email_{source}_pattern'}
                    )
                    entities.append(entity)
        
        return entities
    
    def _extract_email_specific_relations(self, email: Email, full_text: str, 
                                         entities: List[ExtractedEntity]) -> List[ExtractedRelation]:
        """抽取邮件特定的关系"""
        relations = []
        
        # 基于关系指示词抽取关系
        for relation_type, indicators in self.relation_indicators.items():
            for indicator in indicators:
                relations.extend(self._extract_relations_by_indicator(
                    full_text, indicator, relation_type, entities
                ))
        
        # 抽取发件人与提到的人员/组织的关系
        sender_entity = self._find_or_create_sender_entity(email.sender, entities)
        if sender_entity:
            relations.extend(self._infer_sender_relations(sender_entity, entities, full_text))
        
        # 抽取基于邮件结构的关系
        relations.extend(self._extract_structural_relations(email, entities))
        
        return relations
    
    def _extract_relations_by_indicator(self, text: str, indicator: str, 
                                       relation_type: RelationType, 
                                       entities: List[ExtractedEntity]) -> List[ExtractedRelation]:
        """基于关系指示词抽取关系"""
        relations = []
        
        # 查找包含指示词的句子
        sentences = re.split(r'[。！？\n]', text)
        
        for sentence in sentences:
            if indicator in sentence:
                # 在句子中查找实体
                sentence_entities = []
                for entity in entities:
                    if entity.text in sentence:
                        sentence_entities.append(entity)
                
                # 如果找到多个实体，尝试建立关系
                if len(sentence_entities) >= 2:
                    for i, entity1 in enumerate(sentence_entities):
                        for entity2 in sentence_entities[i+1:]:
                            # 根据实体类型和指示词确定关系方向
                            source, target = self._determine_relation_direction(
                                entity1, entity2, relation_type
                            )
                            
                            if source and target:
                                relation = ExtractedRelation(
                                    relation_id=str(uuid.uuid4()),
                                    source_entity=source,
                                    target_entity=target,
                                    relation_type=relation_type,
                                    confidence=0.7,
                                    evidence_text=sentence.strip(),
                                    properties={'extraction_method': 'indicator_based'}
                                )
                                relations.append(relation)
        
        return relations
    
    def _determine_relation_direction(self, entity1: ExtractedEntity, entity2: ExtractedEntity, 
                                    relation_type: RelationType) -> Tuple[Optional[ExtractedEntity], Optional[ExtractedEntity]]:
        """确定关系方向"""
        # 根据关系类型和实体类型确定方向
        if relation_type == RelationType.WORK_FOR:
            if entity1.entity_type == EntityType.PERSON and entity2.entity_type == EntityType.ORGANIZATION:
                return entity1, entity2
            elif entity1.entity_type == EntityType.ORGANIZATION and entity2.entity_type == EntityType.PERSON:
                return entity2, entity1
        
        elif relation_type == RelationType.LOCATED_IN:
            if entity2.entity_type == EntityType.LOCATION:
                return entity1, entity2
            elif entity1.entity_type == EntityType.LOCATION:
                return entity2, entity1
        
        # 默认情况下，按出现顺序确定方向
        if entity1.start_pos < entity2.start_pos:
            return entity1, entity2
        else:
            return entity2, entity1
    
    def _find_or_create_sender_entity(self, sender: str, entities: List[ExtractedEntity]) -> Optional[ExtractedEntity]:
        """查找或创建发件人实体"""
        # 提取邮件地址
        email_addr = self._extract_email_address(sender)
        
        # 查找现有实体
        for entity in entities:
            if (entity.text == sender or 
                entity.text == email_addr or 
                email_addr in entity.properties.get('email_address', '')):
                return entity
        
        # 创建新实体
        sender_entity = ExtractedEntity(
            entity_id=str(uuid.uuid4()),
            text=email_addr or sender,
            entity_type=EntityType.PERSON,
            confidence=0.95,
            start_pos=0,
            end_pos=len(sender),
            properties={'email_address': email_addr, 'role': 'sender'}
        )
        
        return sender_entity
    
    def _infer_sender_relations(self, sender_entity: ExtractedEntity, 
                               entities: List[ExtractedEntity], 
                               text: str) -> List[ExtractedRelation]:
        """推断发件人与其他实体的关系"""
        relations = []
        
        for entity in entities:
            if entity.entity_id == sender_entity.entity_id:
                continue
            
            # 根据实体类型推断关系
            relation_type = None
            confidence = 0.5
            
            if entity.entity_type == EntityType.ORGANIZATION:
                relation_type = RelationType.WORK_FOR
                confidence = 0.6
            elif entity.entity_type == EntityType.PERSON:
                relation_type = RelationType.COLLABORATE_WITH
                confidence = 0.5
            elif entity.entity_type == EntityType.EVENT:
                relation_type = RelationType.PARTICIPATE_IN
                confidence = 0.6
            
            if relation_type:
                relation = ExtractedRelation(
                    relation_id=str(uuid.uuid4()),
                    source_entity=sender_entity,
                    target_entity=entity,
                    relation_type=relation_type,
                    confidence=confidence,
                    evidence_text=f"发件人 {sender_entity.text} 在邮件中提到 {entity.text}",
                    properties={'extraction_method': 'sender_inference'}
                )
                relations.append(relation)
        
        return relations
    
    def _extract_structural_relations(self, email: Email, entities: List[ExtractedEntity]) -> List[ExtractedRelation]:
        """基于邮件结构抽取关系"""
        relations = []
        
        # 如果邮件有附件，创建发件人与附件的关系
        if email.attachments:
            sender_entity = None
            for entity in entities:
                if entity.properties.get('role') == 'sender':
                    sender_entity = entity
                    break
            
            if sender_entity:
                for attachment in email.attachments:
                    filename = attachment.get('filename', '未知附件')
                    
                    # 创建附件实体
                    attachment_entity = ExtractedEntity(
                        entity_id=str(uuid.uuid4()),
                        text=filename,
                        entity_type=EntityType.PRODUCT,
                        confidence=0.9,
                        start_pos=0,
                        end_pos=len(filename),
                        properties={'type': 'attachment', 'filename': filename}
                    )
                    
                    # 创建关系
                    relation = ExtractedRelation(
                        relation_id=str(uuid.uuid4()),
                        source_entity=sender_entity,
                        target_entity=attachment_entity,
                        relation_type=RelationType.OWNS,
                        confidence=0.9,
                        evidence_text=f"邮件附件: {filename}",
                        properties={'extraction_method': 'structural'}
                    )
                    relations.append(relation)
        
        return relations
    
    def _extract_email_address(self, email_string: str) -> str:
        """从邮件字符串中提取邮件地址"""
        match = self.email_pattern.search(email_string)
        return match.group() if match else email_string
    
    def _extract_recipients_from_content(self, content: str) -> List[str]:
        """从邮件内容中提取收件人（简化实现）"""
        # 这里简化处理，实际应该从邮件头中提取
        email_addresses = self.email_pattern.findall(content)
        return list(set(email_addresses))  # 去重
    
    def _extract_topics_from_subject(self, subject: str) -> List[str]:
        """从邮件主题中提取话题关键词"""
        if not subject:
            return []
        
        # 简单的关键词提取
        # 移除常见的邮件前缀
        cleaned_subject = re.sub(r'^(Re:|Fwd?:|回复:|转发:)\s*', '', subject, flags=re.IGNORECASE)
        
        # 分词并过滤
        words = re.findall(r'[\u4e00-\u9fa5a-zA-Z0-9]+', cleaned_subject)
        
        # 过滤短词和常见词
        stop_words = {'的', '了', '在', '是', '和', '与', '或', '但', '而', 'the', 'and', 'or', 'but'}
        topics = [word for word in words if len(word) > 1 and word.lower() not in stop_words]
        
        return topics[:5]  # 最多返回5个话题
    
    def generate_email_knowledge_summary(self, results: List[ExtractionResult]) -> Dict[str, Any]:
        """生成邮件知识抽取摘要
        
        Args:
            results: 抽取结果列表
            
        Returns:
            知识摘要
        """
        if not results:
            return {}
        
        # 统计实体类型分布
        entity_type_counts = Counter()
        relation_type_counts = Counter()
        
        all_entities = []
        all_relations = []
        
        for result in results:
            all_entities.extend(result.entities)
            all_relations.extend(result.relations)
            
            for entity in result.entities:
                entity_type_counts[entity.entity_type.value] += 1
            
            for relation in result.relations:
                relation_type_counts[relation.relation_type.value] += 1
        
        # 统计邮件特定信息
        senders = set()
        subjects = []
        
        for result in results:
            metadata = result.metadata
            if 'email_sender' in metadata:
                senders.add(metadata['email_sender'])
            if 'email_subject' in metadata:
                subjects.append(metadata['email_subject'])
        
        # 计算处理统计
        total_processing_time = sum(result.processing_time for result in results)
        avg_processing_time = total_processing_time / len(results)
        
        return {
            'total_emails': len(results),
            'total_entities': len(all_entities),
            'total_relations': len(all_relations),
            'unique_senders': len(senders),
            'entity_type_distribution': dict(entity_type_counts),
            'relation_type_distribution': dict(relation_type_counts),
            'processing_statistics': {
                'total_time': total_processing_time,
                'average_time': avg_processing_time,
                'emails_per_second': len(results) / max(total_processing_time, 0.001)
            },
            'top_entities': self._get_top_entities(all_entities, 10),
            'top_relations': self._get_top_relations(all_relations, 10)
        }
    
    def _get_top_entities(self, entities: List[ExtractedEntity], limit: int) -> List[Dict[str, Any]]:
        """获取置信度最高的实体"""
        sorted_entities = sorted(entities, key=lambda e: e.confidence, reverse=True)
        return [
            {
                'text': entity.text,
                'type': entity.entity_type.value,
                'confidence': entity.confidence
            }
            for entity in sorted_entities[:limit]
        ]
    
    def _get_top_relations(self, relations: List[ExtractedRelation], limit: int) -> List[Dict[str, Any]]:
        """获取置信度最高的关系"""
        sorted_relations = sorted(relations, key=lambda r: r.confidence, reverse=True)
        return [
            {
                'source': relation.source_entity.text,
                'target': relation.target_entity.text,
                'type': relation.relation_type.value,
                'confidence': relation.confidence
            }
            for relation in sorted_relations[:limit]
        ]