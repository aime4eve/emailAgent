/**
 * 知识抽取服务
 */

import { apiClient } from './api';
import {
  ExtractionRequest,
  ExtractionResult,
  HealthCheckResponse,
  ServiceStatusResponse,
  ApiResponse,
} from '../types';

/**
 * 知识抽取服务类
 */
export class ExtractionService {
  /**
   * 检查服务健康状态
   */
  async checkHealth(): Promise<ApiResponse<HealthCheckResponse>> {
    return apiClient.get<HealthCheckResponse>('/health');
  }

  /**
   * 获取服务状态
   */
  async getServiceStatus(): Promise<ApiResponse<ServiceStatusResponse>> {
    return apiClient.get<ServiceStatusResponse>('/');
  }

  /**
   * 从文本中抽取知识
   * @param request 抽取请求参数
   */
  async extractFromText(
    request: ExtractionRequest
  ): Promise<ApiResponse<ExtractionResult>> {
    return apiClient.post<ExtractionResult>('/extract', request);
  }

  /**
   * 从文件抽取知识
   * @param file 文件对象
   * @param options 抽取选项
   * @param onProgress 上传进度回调
   */
  async extractFromFile(
    file: File,
    options?: { enable_ml_enhancement?: boolean; custom_entity_types?: string[]; confidence_threshold?: number },
    onProgress?: (progress: number) => void
  ): Promise<ApiResponse<ExtractionResult>> {
    const formData = new FormData();
    formData.append('file', file);
    
    // 添加选项参数
    if (options) {
      if (options.enable_ml_enhancement !== undefined) {
        formData.append('enable_ml_enhancement', String(options.enable_ml_enhancement));
      }
      if (options.custom_entity_types) {
        formData.append('custom_entity_types', JSON.stringify(options.custom_entity_types));
      }
      if (options.confidence_threshold !== undefined) {
        formData.append('confidence_threshold', String(options.confidence_threshold));
      }
    }

    try {
      const response = await apiClient.instance.post('/extract/file', formData, {
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
        error: error.response?.data?.error || error.message || '文件上传失败',
      };
    }
  }

  /**
   * 批量处理文件
   * @param files 文件列表
   * @param options 抽取选项
   * @param onProgress 总体进度回调
   * @param onFileProgress 单个文件进度回调
   */
  async batchExtractFromFiles(
    files: File[],
    options: {
      enable_ml_enhancement?: boolean;
      custom_entity_types?: string[];
      confidence_threshold?: number;
    } = {},
    onProgress?: (completed: number, total: number) => void,
    onFileProgress?: (fileIndex: number, progress: number) => void
  ): Promise<ApiResponse<ExtractionResult[]>> {
    const results: ExtractionResult[] = [];
    const errors: string[] = [];

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      
      try {
        const result = await this.extractFromFile(
          file,
          options,
          (progress) => onFileProgress?.(i, progress)
        );

        if (result.success && result.data) {
          results.push(result.data);
        } else {
          errors.push(`文件 ${file.name}: ${result.error}`);
        }
      } catch (error: any) {
        errors.push(`文件 ${file.name}: ${error.message}`);
      }

      // 更新总体进度
      onProgress?.(i + 1, files.length);
    }

    if (errors.length > 0 && results.length === 0) {
      return {
        success: false,
        error: `所有文件处理失败:\n${errors.join('\n')}`,
      };
    }

    return {
      success: true,
      data: results,
      message: errors.length > 0 
        ? `部分文件处理失败:\n${errors.join('\n')}` 
        : undefined,
    };
  }

  /**
   * 获取支持的文件类型
   */
  async getSupportedFileTypes(): Promise<ApiResponse<string[]>> {
    return apiClient.get<string[]>('/extract/supported-types');
  }

  /**
   * 获取可用的实体类型
   */
  async getAvailableEntityTypes(): Promise<ApiResponse<string[]>> {
    return apiClient.get<string[]>('/extract/entity-types');
  }

  /**
   * 获取可用的关系类型
   */
  async getAvailableRelationTypes(): Promise<ApiResponse<string[]>> {
    return apiClient.get<string[]>('/extract/relation-types');
  }

  /**
   * 验证文本内容
   * @param text 要验证的文本
   */
  validateText(text: string): { valid: boolean; message?: string } {
    if (!text || text.trim().length === 0) {
      return { valid: false, message: '文本内容不能为空' };
    }

    if (text.length > 100000) {
      return { valid: false, message: '文本内容过长，请控制在10万字符以内' };
    }

    return { valid: true };
  }

  /**
   * 验证文件
   * @param file 要验证的文件
   */
  validateFile(file: File): { valid: boolean; message?: string } {
    // 检查文件大小（限制为50MB）
    const maxSize = 50 * 1024 * 1024;
    if (file.size > maxSize) {
      return { valid: false, message: '文件大小不能超过50MB' };
    }

    // 检查文件类型
    const supportedTypes = [
      'text/plain',
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'application/vnd.ms-excel',
    ];

    if (!supportedTypes.includes(file.type)) {
      return { 
        valid: false, 
        message: '不支持的文件类型，请上传TXT、PDF、Word或Excel文件' 
      };
    }

    return { valid: true };
  }
}

// 创建服务实例
export const extractionService = new ExtractionService();