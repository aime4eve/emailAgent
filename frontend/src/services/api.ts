/**
 * API服务基础类
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { ApiResponse } from '../types';

// API配置
const API_CONFIG = {
  baseURL: process.env.NODE_ENV === 'production' ? '/api' : 'http://localhost:5000/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
};

/**
 * API客户端类
 */
class ApiClient {
  public instance: AxiosInstance;

  constructor() {
    this.instance = axios.create(API_CONFIG);
    this.setupInterceptors();
  }

  /**
   * 设置请求和响应拦截器
   */
  private setupInterceptors(): void {
    // 请求拦截器
    this.instance.interceptors.request.use(
      (config) => {
        // 添加认证token（如果需要）
        const token = localStorage.getItem('token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        
        // 添加请求时间戳
        config.metadata = { startTime: new Date() };
        
        console.log('API Request:', {
          method: config.method?.toUpperCase(),
          url: config.url,
          data: config.data,
        });
        
        return config;
      },
      (error) => {
        console.error('Request Error:', error);
        return Promise.reject(error);
      }
    );

    // 响应拦截器
    this.instance.interceptors.response.use(
      (response: AxiosResponse) => {
        const duration = response.config.metadata?.startTime 
          ? new Date().getTime() - response.config.metadata.startTime.getTime()
          : 0;
        
        console.log('API Response:', {
          method: response.config.method?.toUpperCase(),
          url: response.config.url,
          status: response.status,
          duration: `${duration}ms`,
          data: response.data,
        });
        
        return response;
      },
      (error) => {
        console.error('Response Error:', {
          message: error.message,
          status: error.response?.status,
          data: error.response?.data,
        });
        
        // 统一错误处理
        if (error.response?.status === 401) {
          // 未授权，清除token并跳转到登录页
          localStorage.removeItem('token');
          window.location.href = '/login';
        }
        
        return Promise.reject(error);
      }
    );
  }

  /**
   * GET请求
   */
  async get<T = any>(
    url: string,
    config?: AxiosRequestConfig
  ): Promise<ApiResponse<T>> {
    try {
      const response = await this.instance.get(url, config);
      return this.handleResponse<T>(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  /**
   * POST请求
   */
  async post<T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<ApiResponse<T>> {
    try {
      const response = await this.instance.post(url, data, config);
      return this.handleResponse<T>(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  /**
   * PUT请求
   */
  async put<T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<ApiResponse<T>> {
    try {
      const response = await this.instance.put(url, data, config);
      return this.handleResponse<T>(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  /**
   * DELETE请求
   */
  async delete<T = any>(
    url: string,
    config?: AxiosRequestConfig
  ): Promise<ApiResponse<T>> {
    try {
      const response = await this.instance.delete(url, config);
      return this.handleResponse<T>(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  /**
   * 文件上传
   */
  async upload<T = any>(
    url: string,
    file: File,
    onProgress?: (progress: number) => void
  ): Promise<ApiResponse<T>> {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await this.instance.post(url, formData, {
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

      return this.handleResponse<T>(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  /**
   * 处理成功响应
   */
  private handleResponse<T>(response: AxiosResponse): ApiResponse<T> {
    // 检查后端是否已经返回了包含success字段的响应
    if (response.data && typeof response.data === 'object' && 'success' in response.data) {
      // 后端已经返回了标准格式，直接返回
      return response.data as ApiResponse<T>;
    }
    
    // 否则包装成标准格式
    return {
      success: true,
      data: response.data,
    };
  }

  /**
   * 处理错误响应
   */
  private handleError(error: any): ApiResponse {
    const message = error.response?.data?.error || error.message || '请求失败';
    
    return {
      success: false,
      error: message,
    };
  }
}

// 创建API客户端实例
export const apiClient = new ApiClient();

// 导出ApiClient类
export { ApiClient };

// 扩展axios配置类型
declare module 'axios' {
  interface AxiosRequestConfig {
    metadata?: {
      startTime: Date;
    };
  }
}