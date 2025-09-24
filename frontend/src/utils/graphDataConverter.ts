/**
 * 图谱数据转换工具
 * 将知识抽取结果转换为D3.js可视化所需的格式
 */

import type { ExtractionResult, Entity, Relation } from '../types';
import type { KnowledgeGraphData, GraphNode, GraphEdge } from '../types/graph';

/**
 * 实体类型到颜色的映射
 */
const ENTITY_TYPE_COLORS: Record<string, string> = {
  PERSON: '#1890ff',      // 人名 - 蓝色
  ORG: '#52c41a',         // 组织 - 绿色
  ORGANIZATION: '#52c41a', // 组织 - 绿色
  LOCATION: '#fa8c16',    // 地点 - 橙色
  GPE: '#fa8c16',         // 地缘政治实体 - 橙色
  TIME: '#722ed1',        // 时间 - 紫色
  DATE: '#722ed1',        // 日期 - 紫色
  EVENT: '#f5222d',       // 事件 - 红色
  PRODUCT: '#13c2c2',     // 产品 - 青色
  CONCEPT: '#13c2c2',     // 概念 - 青色
  MONEY: '#eb2f96',       // 金钱 - 粉色
  PERCENT: '#faad14',     // 百分比 - 黄色
  PHONE: '#2f54eb',       // 电话 - 深蓝色
  EMAIL: '#2f54eb',       // 邮箱 - 深蓝色
  DEFAULT: '#666666',     // 默认 - 灰色
};

/**
 * 关系类型到标签的映射
 */
const RELATION_TYPE_LABELS: Record<string, string> = {
  WORKS_AT: '工作于',
  LOCATED_IN: '位于',
  BORN_IN: '出生于',
  LIVES_IN: '居住于',
  MANAGES: '管理',
  OWNS: '拥有',
  PRODUCES: '生产',
  SELLS: '销售',
  BUYS: '购买',
  CONTACTS: '联系',
  COOPERATES_WITH: '合作',
  COMPETES_WITH: '竞争',
  PART_OF: '属于',
  RELATED_TO: '相关',
  DEFAULT: '关联',
};

/**
 * 将知识抽取结果转换为图谱数据
 * @param extractionResult 知识抽取结果
 * @returns 图谱数据
 */
export function convertExtractionToGraphData(
  extractionResult: ExtractionResult
): KnowledgeGraphData {
  const nodes: GraphNode[] = [];
  const edges: GraphEdge[] = [];
  const nodeMap = new Map<string, GraphNode>();

  // 转换实体为节点
  if (extractionResult.entities && extractionResult.entities.length > 0) {
    extractionResult.entities.forEach((entity: Entity, index: number) => {
      const nodeId = `entity_${index}_${entity.text || 'unknown'}`;
      const entityType = entity.type || 'DEFAULT';
      
      const node: GraphNode = {
        id: nodeId,
        label: entity.text || 'Unknown',
        type: entityType,
        weight: entity.confidence || 1,
        properties: {
          confidence: entity.confidence || 0,
          start_pos: entity.start_pos,
          end_pos: entity.end_pos,
          originalText: entity.text,
          entityType: entityType,
          ...entity.properties,
        },
      };
      
      nodes.push(node);
      nodeMap.set(entity.text || 'unknown', node);
    });
  }

  // 转换关系为边
  if (extractionResult.relations && extractionResult.relations.length > 0) {
    extractionResult.relations.forEach((relation: Relation, index: number) => {
      const sourceText = relation.source_text;
      const targetText = relation.target_text;
      const relationType = relation.type || 'DEFAULT';
      
      if (sourceText && targetText) {
        const sourceNode = nodeMap.get(sourceText);
        const targetNode = nodeMap.get(targetText);
        
        if (sourceNode && targetNode) {
          const edge: GraphEdge = {
            id: `relation_${index}_${sourceText}_${targetText}`,
            source: sourceNode.id,
            target: targetNode.id,
            label: RELATION_TYPE_LABELS[relationType] || relationType,
            type: relationType,
            weight: relation.confidence || 1,
            properties: {
              confidence: relation.confidence || 0,
              originalRelation: relation,
              relationType: relationType,
              ...relation.properties,
            },
          };
          
          edges.push(edge);
        } else {
          // 如果关系中的实体不在节点列表中，创建新节点
          if (!sourceNode && sourceText) {
            const newSourceNode: GraphNode = {
              id: `missing_entity_${sourceText}`,
              label: sourceText,
              type: 'INFERRED',
              weight: 0.5,
              properties: {
                confidence: 0.5,
                inferred: true,
                originalText: sourceText,
              },
            };
            nodes.push(newSourceNode);
            nodeMap.set(sourceText, newSourceNode);
          }
          
          if (!targetNode && targetText) {
            const newTargetNode: GraphNode = {
              id: `missing_entity_${targetText}`,
              label: targetText,
              type: 'INFERRED',
              weight: 0.5,
              properties: {
                confidence: 0.5,
                inferred: true,
                originalText: targetText,
              },
            };
            nodes.push(newTargetNode);
            nodeMap.set(targetText, newTargetNode);
          }
          
          // 重新尝试创建边
          const finalSourceNode = nodeMap.get(sourceText);
          const finalTargetNode = nodeMap.get(targetText);
          
          if (finalSourceNode && finalTargetNode) {
            const edge: GraphEdge = {
              id: `relation_${index}_${sourceText}_${targetText}`,
              source: finalSourceNode.id,
              target: finalTargetNode.id,
              label: RELATION_TYPE_LABELS[relationType] || relationType,
              type: relationType,
              weight: relation.confidence || 1,
              properties: {
                confidence: relation.confidence || 0,
                originalRelation: relation,
                relationType: relationType,
                ...relation.properties,
              },
            };
            
            edges.push(edge);
          }
        }
      }
    });
  }

  // 构建图谱数据
  const graphData: KnowledgeGraphData = {
    nodes,
    edges,
    metadata: {
      node_count: nodes.length,
      edge_count: edges.length,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      source: 'knowledge_extraction',
    },
  };

  return graphData;
}

/**
 * 获取实体类型对应的颜色
 * @param entityType 实体类型
 * @returns 颜色值
 */
export function getEntityTypeColor(entityType: string): string {
  return ENTITY_TYPE_COLORS[entityType.toUpperCase()] || ENTITY_TYPE_COLORS.DEFAULT;
}

/**
 * 获取关系类型对应的标签
 * @param relationType 关系类型
 * @returns 关系标签
 */
export function getRelationTypeLabel(relationType: string): string {
  return RELATION_TYPE_LABELS[relationType.toUpperCase()] || relationType;
}

/**
 * 合并多个图谱数据
 * @param graphDataList 图谱数据列表
 * @returns 合并后的图谱数据
 */
export function mergeGraphData(graphDataList: KnowledgeGraphData[]): KnowledgeGraphData {
  const allNodes: GraphNode[] = [];
  const allEdges: GraphEdge[] = [];
  const nodeIdSet = new Set<string>();
  const edgeIdSet = new Set<string>();

  graphDataList.forEach((graphData) => {
    // 合并节点，避免重复
    graphData.nodes.forEach((node) => {
      if (!nodeIdSet.has(node.id)) {
        allNodes.push(node);
        nodeIdSet.add(node.id);
      }
    });

    // 合并边，避免重复
    graphData.edges.forEach((edge) => {
      if (!edgeIdSet.has(edge.id)) {
        allEdges.push(edge);
        edgeIdSet.add(edge.id);
      }
    });
  });

  return {
    nodes: allNodes,
    edges: allEdges,
    metadata: {
      node_count: allNodes.length,
      edge_count: allEdges.length,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      source: 'merged_data',
    },
  };
}

/**
 * 过滤图谱数据
 * @param graphData 原始图谱数据
 * @param filter 过滤条件
 * @returns 过滤后的图谱数据
 */
export function filterGraphData(
  graphData: KnowledgeGraphData,
  filter: {
    nodeTypes?: string[];
    edgeTypes?: string[];
    minConfidence?: number;
    searchQuery?: string;
  }
): KnowledgeGraphData {
  let filteredNodes = graphData.nodes;
  let filteredEdges = graphData.edges;

  // 按节点类型过滤
  if (filter.nodeTypes && filter.nodeTypes.length > 0) {
    filteredNodes = filteredNodes.filter((node) =>
      filter.nodeTypes!.includes(node.type)
    );
  }

  // 按置信度过滤
  if (filter.minConfidence !== undefined) {
    filteredNodes = filteredNodes.filter(
      (node) => (node.weight || 0) >= filter.minConfidence!
    );
  }

  // 按搜索关键词过滤
  if (filter.searchQuery) {
    const query = filter.searchQuery.toLowerCase();
    filteredNodes = filteredNodes.filter(
      (node) =>
        node.label.toLowerCase().includes(query) ||
        node.type.toLowerCase().includes(query)
    );
  }

  // 获取过滤后节点的ID集合
  const nodeIds = new Set(filteredNodes.map((node) => node.id));

  // 过滤边：只保留两端节点都存在的边
  filteredEdges = filteredEdges.filter(
    (edge) =>
      nodeIds.has(edge.source as string) && nodeIds.has(edge.target as string)
  );

  // 按边类型过滤
  if (filter.edgeTypes && filter.edgeTypes.length > 0) {
    filteredEdges = filteredEdges.filter((edge) =>
      filter.edgeTypes!.includes(edge.type)
    );
  }

  // 按边的置信度过滤
  if (filter.minConfidence !== undefined) {
    filteredEdges = filteredEdges.filter(
      (edge) => (edge.weight || 0) >= filter.minConfidence!
    );
  }

  return {
    nodes: filteredNodes,
    edges: filteredEdges,
    metadata: {
      ...graphData.metadata,
      node_count: filteredNodes.length,
      edge_count: filteredEdges.length,
      updated_at: new Date().toISOString(),
    },
  };
}