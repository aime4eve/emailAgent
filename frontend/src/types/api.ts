/**
 * API相关类型定义
 */

// 基础API响应类型
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

// 实体类型
export interface Entity {
  id: string;
  text: string;
  type: EntityType;
  confidence: number;
  start_pos: number;
  end_pos: number;
  properties?: Record<string, any>;
}

// 实体类型枚举
export enum EntityType {
  PERSON = 'PERSON',
  ORGANIZATION = 'ORGANIZATION', 
  LOCATION = 'LOCATION',
  TIME = 'TIME',
  EMAIL = 'EMAIL',
  PHONE = 'PHONE',
  OTHER = 'OTHER'
}

// 关系类型
export interface Relation {
  id: string;
  source_entity: Entity;
  target_entity: Entity;
  source_text: string;
  target_text: string;
  type: string;
  confidence: number;
  evidence_text?: string;
  properties?: Record<string, any>;
}

// 关系类型枚举
export enum RelationType {
  WORK_FOR = 'WORK_FOR',
  LOCATED_IN = 'LOCATED_IN',
  PART_OF = 'PART_OF',
  RELATED_TO = 'RELATED_TO',
  OTHER = 'OTHER'
}

// 知识抽取结果
export interface ExtractionResult {
  entities: Entity[];
  relations: Relation[];
  confidence: number;
  statistics?: ExtractionStatistics;
  metadata?: Record<string, any>;
  processing_time?: number;
}

// 抽取统计信息
export interface ExtractionStatistics {
  entity_count: number;
  relation_count: number;
  entity_type_counts: Record<string, number>;
  relation_type_counts: Record<string, number>;
  processing_time: number;
  confidence_distribution?: {
    high: number;
    medium: number;
    low: number;
  };
}

// 知识抽取请求
export interface ExtractionRequest {
  text: string;
  enable_ml_enhancement?: boolean;
  custom_entity_types?: string[];
  confidence_threshold?: number;
}

// 文件上传请求
export interface FileUploadRequest {
  file: File;
  enable_ml_enhancement?: boolean;
  custom_entity_types?: string[];
}

// 健康检查响应
export interface HealthCheckResponse {
  status: 'healthy' | 'unhealthy';
  timestamp: string;
  version?: string;
}

// 服务状态响应
export interface ServiceStatusResponse {
  message: string;
  version: string;
  status: 'running' | 'stopped';
}