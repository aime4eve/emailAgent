/**
 * 本体管理服务
 */

import { apiClient } from './api';
import {
  Ontology,
  OntologyClass,
  OntologyProperty,
  OntologyRelation,
  OntologyInstance,
  OntologyValidationResult,
  OntologyFormat,
  ApiResponse,
} from '../types';

/**
 * 本体管理服务类
 */
export class OntologyService {
  /**
   * 获取本体列表
   */
  async getOntologies(): Promise<ApiResponse<Ontology[]>> {
    return apiClient.get<Ontology[]>('/ontology');
  }

  /**
   * 获取本体详情
   * @param ontologyId 本体ID
   */
  async getOntology(ontologyId: string): Promise<ApiResponse<Ontology>> {
    return apiClient.get<Ontology>(`/ontology/${ontologyId}`);
  }

  /**
   * 创建本体
   * @param ontology 本体数据
   */
  async createOntology(
    ontology: Omit<Ontology, 'id' | 'metadata'>
  ): Promise<ApiResponse<Ontology>> {
    return apiClient.post<Ontology>('/ontology', ontology);
  }

  /**
   * 更新本体
   * @param ontologyId 本体ID
   * @param ontology 本体数据
   */
  async updateOntology(
    ontologyId: string,
    ontology: Partial<Ontology>
  ): Promise<ApiResponse<Ontology>> {
    return apiClient.put<Ontology>(`/ontology/${ontologyId}`, ontology);
  }

  /**
   * 删除本体
   * @param ontologyId 本体ID
   */
  async deleteOntology(ontologyId: string): Promise<ApiResponse<void>> {
    return apiClient.delete(`/ontology/${ontologyId}`);
  }

  /**
   * 获取本体类列表
   * @param ontologyId 本体ID
   */
  async getClasses(ontologyId: string): Promise<ApiResponse<OntologyClass[]>> {
    return apiClient.get<OntologyClass[]>(`/ontology/${ontologyId}/classes`);
  }

  /**
   * 创建本体类
   * @param ontologyId 本体ID
   * @param ontologyClass 类数据
   */
  async createClass(
    ontologyId: string,
    ontologyClass: Omit<OntologyClass, 'id'>
  ): Promise<ApiResponse<OntologyClass>> {
    return apiClient.post<OntologyClass>(
      `/ontology/${ontologyId}/classes`,
      ontologyClass
    );
  }

  /**
   * 更新本体类
   * @param ontologyId 本体ID
   * @param classId 类ID
   * @param ontologyClass 类数据
   */
  async updateClass(
    ontologyId: string,
    classId: string,
    ontologyClass: Partial<OntologyClass>
  ): Promise<ApiResponse<OntologyClass>> {
    return apiClient.put<OntologyClass>(
      `/ontology/${ontologyId}/classes/${classId}`,
      ontologyClass
    );
  }

  /**
   * 删除本体类
   * @param ontologyId 本体ID
   * @param classId 类ID
   */
  async deleteClass(
    ontologyId: string,
    classId: string
  ): Promise<ApiResponse<void>> {
    return apiClient.delete(`/ontology/${ontologyId}/classes/${classId}`);
  }

  /**
   * 获取本体属性列表
   * @param ontologyId 本体ID
   */
  async getProperties(
    ontologyId: string
  ): Promise<ApiResponse<OntologyProperty[]>> {
    return apiClient.get<OntologyProperty[]>(
      `/ontology/${ontologyId}/properties`
    );
  }

  /**
   * 创建本体属性
   * @param ontologyId 本体ID
   * @param property 属性数据
   */
  async createProperty(
    ontologyId: string,
    property: Omit<OntologyProperty, 'id'>
  ): Promise<ApiResponse<OntologyProperty>> {
    return apiClient.post<OntologyProperty>(
      `/ontology/${ontologyId}/properties`,
      property
    );
  }

  /**
   * 更新本体属性
   * @param ontologyId 本体ID
   * @param propertyId 属性ID
   * @param property 属性数据
   */
  async updateProperty(
    ontologyId: string,
    propertyId: string,
    property: Partial<OntologyProperty>
  ): Promise<ApiResponse<OntologyProperty>> {
    return apiClient.put<OntologyProperty>(
      `/ontology/${ontologyId}/properties/${propertyId}`,
      property
    );
  }

  /**
   * 删除本体属性
   * @param ontologyId 本体ID
   * @param propertyId 属性ID
   */
  async deleteProperty(
    ontologyId: string,
    propertyId: string
  ): Promise<ApiResponse<void>> {
    return apiClient.delete(
      `/ontology/${ontologyId}/properties/${propertyId}`
    );
  }

  /**
   * 获取本体关系列表
   * @param ontologyId 本体ID
   */
  async getRelations(
    ontologyId: string
  ): Promise<ApiResponse<OntologyRelation[]>> {
    return apiClient.get<OntologyRelation[]>(
      `/ontology/${ontologyId}/relations`
    );
  }

  /**
   * 创建本体关系
   * @param ontologyId 本体ID
   * @param relation 关系数据
   */
  async createRelation(
    ontologyId: string,
    relation: Omit<OntologyRelation, 'id'>
  ): Promise<ApiResponse<OntologyRelation>> {
    return apiClient.post<OntologyRelation>(
      `/ontology/${ontologyId}/relations`,
      relation
    );
  }

  /**
   * 更新本体关系
   * @param ontologyId 本体ID
   * @param relationId 关系ID
   * @param relation 关系数据
   */
  async updateRelation(
    ontologyId: string,
    relationId: string,
    relation: Partial<OntologyRelation>
  ): Promise<ApiResponse<OntologyRelation>> {
    return apiClient.put<OntologyRelation>(
      `/ontology/${ontologyId}/relations/${relationId}`,
      relation
    );
  }

  /**
   * 删除本体关系
   * @param ontologyId 本体ID
   * @param relationId 关系ID
   */
  async deleteRelation(
    ontologyId: string,
    relationId: string
  ): Promise<ApiResponse<void>> {
    return apiClient.delete(
      `/ontology/${ontologyId}/relations/${relationId}`
    );
  }

  /**
   * 获取本体实例列表
   * @param ontologyId 本体ID
   * @param classId 类ID（可选）
   */
  async getInstances(
    ontologyId: string,
    classId?: string
  ): Promise<ApiResponse<OntologyInstance[]>> {
    const params = classId ? { class_id: classId } : {};
    return apiClient.get<OntologyInstance[]>(
      `/ontology/${ontologyId}/instances`,
      { params }
    );
  }

  /**
   * 创建本体实例
   * @param ontologyId 本体ID
   * @param instance 实例数据
   */
  async createInstance(
    ontologyId: string,
    instance: Omit<OntologyInstance, 'id'>
  ): Promise<ApiResponse<OntologyInstance>> {
    return apiClient.post<OntologyInstance>(
      `/ontology/${ontologyId}/instances`,
      instance
    );
  }

  /**
   * 更新本体实例
   * @param ontologyId 本体ID
   * @param instanceId 实例ID
   * @param instance 实例数据
   */
  async updateInstance(
    ontologyId: string,
    instanceId: string,
    instance: Partial<OntologyInstance>
  ): Promise<ApiResponse<OntologyInstance>> {
    return apiClient.put<OntologyInstance>(
      `/ontology/${ontologyId}/instances/${instanceId}`,
      instance
    );
  }

  /**
   * 删除本体实例
   * @param ontologyId 本体ID
   * @param instanceId 实例ID
   */
  async deleteInstance(
    ontologyId: string,
    instanceId: string
  ): Promise<ApiResponse<void>> {
    return apiClient.delete(
      `/ontology/${ontologyId}/instances/${instanceId}`
    );
  }

  /**
   * 验证本体
   * @param ontologyId 本体ID
   */
  async validateOntology(
    ontologyId: string
  ): Promise<ApiResponse<OntologyValidationResult>> {
    return apiClient.post<OntologyValidationResult>(
      `/ontology/${ontologyId}/validate`
    );
  }

  /**
   * 导出本体
   * @param ontologyId 本体ID
   * @param format 导出格式
   */
  async exportOntology(
    ontologyId: string,
    format: OntologyFormat = OntologyFormat.JSON
  ): Promise<ApiResponse<Blob>> {
    try {
      const response = await apiClient.instance.get(
        `/ontology/${ontologyId}/export`,
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
   * 导入本体
   * @param file 本体文件
   * @param format 文件格式
   * @param onProgress 上传进度回调
   */
  async importOntology(
    file: File,
    format: OntologyFormat = OntologyFormat.JSON,
    onProgress?: (progress: number) => void
  ): Promise<ApiResponse<Ontology>> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('format', format);

    try {
      const response = await apiClient.instance.post(
        '/ontology/import',
        formData,
        {
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
        }
      );

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
   * 搜索本体元素
   * @param ontologyId 本体ID
   * @param query 搜索查询
   * @param elementType 元素类型
   */
  async searchOntology(
    ontologyId: string,
    query: string,
    elementType?: 'class' | 'property' | 'relation' | 'instance'
  ): Promise<ApiResponse<any[]>> {
    const params = {
      q: query,
      ...(elementType && { type: elementType }),
    };
    return apiClient.get(`/ontology/${ontologyId}/search`, { params });
  }

  /**
   * 获取本体统计信息
   * @param ontologyId 本体ID
   */
  async getOntologyStatistics(
    ontologyId: string
  ): Promise<ApiResponse<{
    class_count: number;
    property_count: number;
    relation_count: number;
    instance_count: number;
  }>> {
    return apiClient.get(`/ontology/${ontologyId}/statistics`);
  }
}

// 创建服务实例
export const ontologyService = new OntologyService();