/**
 * 知识图谱服务
 */

import { apiClient } from './api';
import {
  KnowledgeGraphData,
  GraphNode,
  GraphEdge,
  GraphStatistics,
  GraphSearchResult,
  GraphFilter,
  ApiResponse,
} from '../types';

/**
 * 知识图谱服务类
 */
export class GraphService {
  /**
   * 获取知识图谱数据
   * @param filter 过滤条件
   */
  async getGraphData(
    filter?: GraphFilter
  ): Promise<ApiResponse<KnowledgeGraphData>> {
    const params = filter ? { filter: JSON.stringify(filter) } : {};
    return apiClient.get<KnowledgeGraphData>('/graph', { params });
  }

  /**
   * 创建知识图谱
   * @param data 图谱数据
   */
  async createGraph(
    data: KnowledgeGraphData
  ): Promise<ApiResponse<KnowledgeGraphData>> {
    return apiClient.post<KnowledgeGraphData>('/graph', data);
  }

  /**
   * 更新知识图谱
   * @param graphId 图谱ID
   * @param data 更新数据
   */
  async updateGraph(
    graphId: string,
    data: Partial<KnowledgeGraphData>
  ): Promise<ApiResponse<KnowledgeGraphData>> {
    return apiClient.put<KnowledgeGraphData>(`/graph/${graphId}`, data);
  }

  /**
   * 删除知识图谱
   * @param graphId 图谱ID
   */
  async deleteGraph(graphId: string): Promise<ApiResponse<void>> {
    return apiClient.delete(`/graph/${graphId}`);
  }

  /**
   * 添加节点
   * @param graphId 图谱ID
   * @param node 节点数据
   */
  async addNode(
    graphId: string,
    node: Omit<GraphNode, 'id'>
  ): Promise<ApiResponse<GraphNode>> {
    return apiClient.post<GraphNode>(`/graph/${graphId}/nodes`, node);
  }

  /**
   * 更新节点
   * @param graphId 图谱ID
   * @param nodeId 节点ID
   * @param node 节点数据
   */
  async updateNode(
    graphId: string,
    nodeId: string,
    node: Partial<GraphNode>
  ): Promise<ApiResponse<GraphNode>> {
    return apiClient.put<GraphNode>(`/graph/${graphId}/nodes/${nodeId}`, node);
  }

  /**
   * 删除节点
   * @param graphId 图谱ID
   * @param nodeId 节点ID
   */
  async deleteNode(
    graphId: string,
    nodeId: string
  ): Promise<ApiResponse<void>> {
    return apiClient.delete(`/graph/${graphId}/nodes/${nodeId}`);
  }

  /**
   * 添加边
   * @param graphId 图谱ID
   * @param edge 边数据
   */
  async addEdge(
    graphId: string,
    edge: Omit<GraphEdge, 'id'>
  ): Promise<ApiResponse<GraphEdge>> {
    return apiClient.post<GraphEdge>(`/graph/${graphId}/edges`, edge);
  }

  /**
   * 更新边
   * @param graphId 图谱ID
   * @param edgeId 边ID
   * @param edge 边数据
   */
  async updateEdge(
    graphId: string,
    edgeId: string,
    edge: Partial<GraphEdge>
  ): Promise<ApiResponse<GraphEdge>> {
    return apiClient.put<GraphEdge>(`/graph/${graphId}/edges/${edgeId}`, edge);
  }

  /**
   * 删除边
   * @param graphId 图谱ID
   * @param edgeId 边ID
   */
  async deleteEdge(
    graphId: string,
    edgeId: string
  ): Promise<ApiResponse<void>> {
    return apiClient.delete(`/graph/${graphId}/edges/${edgeId}`);
  }

  /**
   * 搜索图谱
   * @param graphId 图谱ID
   * @param query 搜索查询
   * @param options 搜索选项
   */
  async searchGraph(
    graphId: string,
    query: string,
    options: {
      searchType?: 'node' | 'edge' | 'both';
      limit?: number;
      includeProperties?: boolean;
    } = {}
  ): Promise<ApiResponse<GraphSearchResult>> {
    const params = {
      q: query,
      ...options,
    };
    return apiClient.get<GraphSearchResult>(`/graph/${graphId}/search`, { params });
  }

  /**
   * 获取图谱统计信息
   * @param graphId 图谱ID
   */
  async getGraphStatistics(
    graphId: string
  ): Promise<ApiResponse<GraphStatistics>> {
    return apiClient.get<GraphStatistics>(`/graph/${graphId}/statistics`);
  }

  /**
   * 导出图谱数据
   * @param graphId 图谱ID
   * @param format 导出格式
   */
  async exportGraph(
    graphId: string,
    format: 'json' | 'csv' | 'gexf' | 'graphml' = 'json'
  ): Promise<ApiResponse<Blob>> {
    try {
      const response = await apiClient.instance.get(
        `/graph/${graphId}/export`,
        {
          params: { format },
          responseType: 'blob',
        }
      );

      return {
        success: true,
        data: response.data,
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || error.message || '导出失败',
      };
    }
  }

  /**
   * 导入图谱数据
   * @param file 图谱文件
   * @param format 文件格式
   * @param onProgress 上传进度回调
   */
  async importGraph(
    file: File,
    format: 'json' | 'csv' | 'gexf' | 'graphml' = 'json',
    onProgress?: (progress: number) => void
  ): Promise<ApiResponse<KnowledgeGraphData>> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('format', format);

    try {
      const response = await apiClient.instance.post('/graph/import', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (onProgress && progressEvent.total) {
            const progress = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            );
            onProgress(progress);
          }
        },
      });

      return {
        success: true,
        data: response.data,
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || error.message || '导入失败',
      };
    }
  }

  /**
   * 获取节点的邻居
   * @param graphId 图谱ID
   * @param nodeId 节点ID
   * @param depth 搜索深度
   */
  async getNodeNeighbors(
    graphId: string,
    nodeId: string,
    depth: number = 1
  ): Promise<ApiResponse<{ nodes: GraphNode[]; edges: GraphEdge[] }>> {
    return apiClient.get(`/graph/${graphId}/nodes/${nodeId}/neighbors`, {
      params: { depth },
    });
  }

  /**
   * 查找两个节点之间的路径
   * @param graphId 图谱ID
   * @param sourceId 源节点ID
   * @param targetId 目标节点ID
   * @param maxDepth 最大搜索深度
   */
  async findPath(
    graphId: string,
    sourceId: string,
    targetId: string,
    maxDepth: number = 5
  ): Promise<ApiResponse<{ nodes: GraphNode[]; edges: GraphEdge[] }>> {
    return apiClient.get(`/graph/${graphId}/path`, {
      params: {
        source: sourceId,
        target: targetId,
        maxDepth,
      },
    });
  }

  /**
   * 验证图谱数据
   * @param data 图谱数据
   */
  validateGraphData(data: KnowledgeGraphData): {
    valid: boolean;
    errors: string[];
  } {
    const errors: string[] = [];

    // 检查节点
    if (!data.nodes || data.nodes.length === 0) {
      errors.push('图谱必须包含至少一个节点');
    } else {
      const nodeIds = new Set<string>();
      data.nodes.forEach((node, index) => {
        if (!node.id) {
          errors.push(`节点 ${index} 缺少ID`);
        } else if (nodeIds.has(node.id)) {
          errors.push(`节点ID "${node.id}" 重复`);
        } else {
          nodeIds.add(node.id);
        }

        if (!node.label) {
          errors.push(`节点 "${node.id}" 缺少标签`);
        }

        if (!node.type) {
          errors.push(`节点 "${node.id}" 缺少类型`);
        }
      });

      // 检查边
      if (data.edges) {
        const edgeIds = new Set<string>();
        data.edges.forEach((edge, index) => {
          if (!edge.id) {
            errors.push(`边 ${index} 缺少ID`);
          } else if (edgeIds.has(edge.id)) {
            errors.push(`边ID "${edge.id}" 重复`);
          } else {
            edgeIds.add(edge.id);
          }

          if (!edge.source) {
            errors.push(`边 "${edge.id}" 缺少源节点`);
          } else if (!nodeIds.has(typeof edge.source === 'string' ? edge.source : edge.source.id)) {
            const sourceId = typeof edge.source === 'string' ? edge.source : edge.source.id;
            errors.push(`边 "${edge.id}" 的源节点 "${sourceId}" 不存在`);
          }

          if (!edge.target) {
            errors.push(`边 "${edge.id}" 缺少目标节点`);
          } else if (!nodeIds.has(typeof edge.target === 'string' ? edge.target : edge.target.id)) {
            const targetId = typeof edge.target === 'string' ? edge.target : edge.target.id;
            errors.push(`边 "${edge.id}" 的目标节点 "${targetId}" 不存在`);
          }

          if (!edge.type) {
            errors.push(`边 "${edge.id}" 缺少类型`);
          }
        });
      }
    }

    return {
      valid: errors.length === 0,
      errors,
    };
  }
}

// 创建服务实例
export const graphService = new GraphService();