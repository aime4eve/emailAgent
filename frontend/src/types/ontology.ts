/**
 * 本体管理相关类型定义
 */

// 本体类
export interface OntologyClass {
  id: string;
  name: string;
  label?: string;
  description?: string;
  parent_classes?: string[];
  child_classes?: string[];
  properties?: OntologyProperty[];
  instances?: string[];
  created_at?: string;
  updated_at?: string;
}

// 本体属性
export interface OntologyProperty {
  id: string;
  name: string;
  label?: string;
  description?: string;
  domain?: string[];
  range?: string[];
  type: PropertyType;
  required?: boolean;
  multiple?: boolean;
  default_value?: any;
}

// 属性类型枚举
export enum PropertyType {
  STRING = 'string',
  NUMBER = 'number',
  BOOLEAN = 'boolean',
  DATE = 'date',
  URI = 'uri',
  OBJECT = 'object',
}

// 本体状态枚举
export enum OntologyStatus {
  DRAFT = 'draft',
  ACTIVE = 'active',
  DEPRECATED = 'deprecated',
}

// 本体关系
export interface OntologyRelation {
  id: string;
  name: string;
  label?: string;
  description?: string;
  domain: string[];
  range: string[];
  inverse_of?: string;
  transitive?: boolean;
  symmetric?: boolean;
  functional?: boolean;
  properties?: Record<string, any>;
}

// 本体实例
export interface OntologyInstance {
  id: string;
  class_id: string;
  name: string;
  label?: string;
  properties: Record<string, any>;
  relations?: {
    relation_id: string;
    target_instance_id: string;
    properties?: Record<string, any>;
  }[];
  created_at?: string;
  updated_at?: string;
}

// 完整本体结构
export interface Ontology {
  id: string;
  name: string;
  description?: string;
  version: string;
  namespace?: string;
  status: 'draft' | 'active' | 'deprecated';
  classes: OntologyClass[];
  properties: OntologyProperty[];
  relations: OntologyRelation[];
  instances?: OntologyInstance[];
  created_at: string;
  updated_at: string;
  metadata: {
    created_by: string;
    [key: string]: any;
  };
}

// 本体验证结果
export interface OntologyValidationResult {
  valid: boolean;
  errors: ValidationError[];
  warnings: ValidationWarning[];
  statistics: {
    class_count: number;
    property_count: number;
    relation_count: number;
    instance_count: number;
  };
}

// 验证错误
export interface ValidationError {
  type: 'syntax' | 'semantic' | 'consistency';
  message: string;
  location?: {
    element_type: 'class' | 'property' | 'relation' | 'instance';
    element_id: string;
    line?: number;
  };
  severity: 'error' | 'warning';
}

// 验证警告
export interface ValidationWarning {
  type: 'best_practice' | 'performance' | 'completeness';
  message: string;
  suggestion?: string;
  location?: {
    element_type: 'class' | 'property' | 'relation' | 'instance';
    element_id: string;
  };
}

// 本体格式枚举
export enum OntologyFormat {
  JSON = 'json',
  OWL = 'owl',
  RDF = 'rdf',
  TTL = 'ttl',
}

// 本体操作请求
export interface OntologyOperationRequest {
  operation: 'create' | 'update' | 'delete' | 'validate' | 'export' | 'import';
  target_type: 'class' | 'property' | 'relation' | 'instance' | 'ontology';
  target_id?: string;
  data?: any;
  format?: OntologyFormat;
}