/**
 * 本体管理服务
 */

import { apiClient } from './api';
import {
  ApiResponse,
} from '../types';

/**
 * 本体管理服务类
 */
export class OntologyService {
  /**
   * 获取本体列表
   * @param page 页码
   * @param pageSize 每页大小
   * @param search 搜索关键词
   * @param tags 标签过滤
   */
  async getOntologies(
    page: number = 1,
    pageSize: number = 10,
    search?: string,
    tags?: string[]
  ): Promise<ApiResponse<{
    ontologies: any[];
    total: number;
    page: number;
    page_size: number;
    total_pages: number;
  }>> {
    const params = new URLSearchParams();
    params.append('page', page.toString());
    params.append('page_size', pageSize.toString());
    if (search) params.append('search', search);
    if (tags && tags.length > 0) params.append('tags', tags.join(','));
    
    return apiClient.get(`/ontologies?${params.toString()}`);
  }

  /**
   * 获取本体详情
   * @param ontologyId 本体ID
   */
  async getOntology(ontologyId: string): Promise<ApiResponse<any>> {
    return apiClient.get(`/ontologies/${ontologyId}`);
  }

  /**
   * 创建本体
   * @param ontology 本体数据
   */
  async createOntology(ontology: any): Promise<ApiResponse<any>> {
    return apiClient.post('/ontologies', ontology);
  }

  /**
   * 更新本体
   * @param ontologyId 本体ID
   * @param ontology 本体数据
   */
  async updateOntology(
    ontologyId: string,
    ontology: any
  ): Promise<ApiResponse<any>> {
    return apiClient.put(`/ontologies/${ontologyId}`, ontology);
  }

  /**
   * 删除本体
   * @param ontologyId 本体ID
   */
  async deleteOntology(ontologyId: string): Promise<ApiResponse<void>> {
    return apiClient.delete(`/ontologies/${ontologyId}`);
  }

  /**
   * 导入本体
   * @param file 文件
   * @param format 文件格式
   */
  async importOntology(
    file: File,
    format: string = 'json'
  ): Promise<ApiResponse<any>> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('format', format);
    
    return apiClient.post('/ontologies/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  }

  /**
   * 导出本体
   * @param ontologyId 本体ID
   * @param format 导出格式
   */
  async exportOntology(
    ontologyId: string,
    format: string = 'json'
  ): Promise<ApiResponse<any>> {
    return apiClient.get(`/ontologies/${ontologyId}/export?format=${format}`);
  }

  /**
   * 获取本体统计信息
   */
  async getStatistics(): Promise<ApiResponse<{
    total_ontologies: number;
    total_entities: number;
    total_relations: number;
    unique_authors: number;
    unique_tags: number;
    all_tags: string[];
  }>> {
    return apiClient.get('/ontologies/statistics');
  }


}

// 创建服务实例
export const ontologyService = new OntologyService();