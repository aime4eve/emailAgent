/**
 * 知识图谱相关类型定义
 */

// 图谱节点
export interface GraphNode {
  id: string;
  label: string;
  type: string;
  weight?: number;
  properties?: Record<string, any>;
  x?: number;
  y?: number;
  fx?: number | null;
  fy?: number | null;
}

// 图谱边
export interface GraphEdge {
  id: string;
  source: string | GraphNode;
  target: string | GraphNode;
  label?: string;
  type: string;
  weight?: number;
  properties?: Record<string, any>;
  style?: Record<string, any>;
}

// 知识图谱数据
export interface KnowledgeGraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
  metadata?: {
    node_count: number;
    edge_count: number;
    created_at?: string;
    updated_at?: string;
  };
}

// 图谱布局配置
export interface GraphLayoutConfig {
  type: 'force' | 'circular' | 'grid' | 'hierarchical';
  nodeSize?: number;
  linkDistance?: number;
  nodeStrength?: number;
  linkStrength?: number;
  iterations?: number;
}

// 图谱可视化配置
export interface GraphVisualizationConfig {
  width: number;
  height: number;
  layout: GraphLayoutConfig;
  nodeStyle?: {
    size?: number;
    color?: string;
    strokeColor?: string;
    strokeWidth?: number;
    labelVisible?: boolean;
    labelFontSize?: number;
  };
  edgeStyle?: {
    color?: string;
    width?: number;
    labelVisible?: boolean;
    labelFontSize?: number;
    arrow?: boolean;
  };
  interaction?: {
    draggable?: boolean;
    zoomable?: boolean;
    selectable?: boolean;
    hoverable?: boolean;
  };
}

// 图谱统计信息
export interface GraphStatistics {
  nodeCount: number;
  edgeCount: number;
  nodeTypeDistribution: Record<string, number>;
  edgeTypeDistribution: Record<string, number>;
  density: number;
  averageDegree: number;
  maxDegree: number;
  minDegree: number;
  connectedComponents: number;
}

// 图谱搜索结果
export interface GraphSearchResult {
  nodes: GraphNode[];
  edges: GraphEdge[];
  paths?: GraphPath[];
  total: number;
}

// 图谱路径
export interface GraphPath {
  nodes: string[];
  edges: string[];
  length: number;
  weight?: number;
}

// 图谱过滤条件
export interface GraphFilter {
  nodeTypes?: string[];
  edgeTypes?: string[];
  nodeProperties?: Record<string, any>;
  edgeProperties?: Record<string, any>;
  minConfidence?: number;
  maxConfidence?: number;
}