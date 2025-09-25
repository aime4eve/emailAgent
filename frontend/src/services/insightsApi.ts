/**
 * 洞察系统API服务
 * 提供客户洞察、产品分析、市场洞察、风险分析等功能的API调用
 */

import { ApiClient } from './api';
import { ApiResponse } from '../types';

// 洞察系统相关类型定义
export interface CustomerInsight {
  customer_id: string;
  need_type: string;
  description: string;
  priority: string;
  mentioned_count: number;
  confidence: number;
  extracted_time: string;
}

export interface ProductAnalysis {
  product_name: string;
  category: string;
  features: string[];
  requirements: string[];
  market_demand: number;
  competition_level: string;
  price_range: {
    min: number;
    max: number;
  };
}

export interface MarketInsight {
  region: string;
  market_size: number;
  growth_rate: number;
  key_trends: string[];
  opportunities: string[];
  challenges: string[];
}

export interface RiskFactor {
  factor_id: string;
  factor_name: string;
  category: string;
  description: string;
  impact_score: number;
  probability: number;
  mitigation_strategies: string[];
}

export interface BusinessReport {
  report_id: string;
  report_type: string;
  title: string;
  summary: string;
  insights: any[];
  recommendations: string[];
  created_time: string;
}

/**
 * 洞察系统API服务类
 */
class InsightsApiService {
  private apiClient: ApiClient;

  constructor() {
    this.apiClient = new ApiClient();
  }

  /**
   * 获取系统健康状态
   */
  async getHealth(): Promise<ApiResponse<{ status: string; timestamp: string }>> {
    return this.apiClient.get('/v1/health');
  }

  /**
   * 分析文本内容
   * @param text 要分析的文本内容
   */
  async analyzeText(text: string): Promise<ApiResponse<{
    entities: any[];
    relations: any[];
    insights: any[];
  }>> {
    return this.apiClient.post('/v1/extraction/analyze', { text });
  }

  /**
   * 获取客户洞察
   * @param customerId 客户ID（可选）
   */
  async getCustomerInsights(customerId?: string): Promise<ApiResponse<CustomerInsight[]>> {
    const params = customerId ? { customer_id: customerId } : {};
    return this.apiClient.get('/v1/insights/customer-analysis', { params });
  }

  /**
   * 分析客户需求
   * @param emailContent 邮件内容
   */
  async analyzeCustomerNeeds(emailContent: string): Promise<ApiResponse<{
    needs: CustomerInsight[];
    purchase_intent: {
      level: string;
      confidence: number;
      indicators: string[];
    };
    decision_factors: string[];
  }>> {
    return this.apiClient.post('/v1/insights/customer-needs', { email_content: emailContent });
  }

  /**
   * 获取产品分析
   * @param productName 产品名称（可选）
   */
  async getProductAnalysis(productName?: string): Promise<ApiResponse<ProductAnalysis[]>> {
    const params = productName ? { product_name: productName } : {};
    return this.apiClient.get('/v1/insights/product-analysis', { params });
  }

  /**
   * 分析产品需求
   * @param productData 产品数据
   */
  async analyzeProductDemand(productData: {
    product_name: string;
    category?: string;
    features?: string[];
  }): Promise<ApiResponse<{
    demand_level: string;
    market_potential: number;
    feature_preferences: any[];
    price_sensitivity: {
      level: string;
      optimal_range: { min: number; max: number };
    };
  }>> {
    return this.apiClient.post('/v1/insights/product-demand', productData);
  }

  /**
   * 获取市场洞察
   * @param region 地区（可选）
   */
  async getMarketInsights(region?: string): Promise<ApiResponse<MarketInsight[]>> {
    const params = region ? { region } : {};
    return this.apiClient.get('/v1/insights/market-analysis', { params });
  }

  /**
   * 分析市场趋势
   * @param timeRange 时间范围
   */
  async analyzeMarketTrends(timeRange: {
    start_date: string;
    end_date: string;
    region?: string;
  }): Promise<ApiResponse<{
    trends: any[];
    growth_forecast: any[];
    competitive_landscape: any[];
  }>> {
    return this.apiClient.post('/v1/insights/market-trends', timeRange);
  }

  /**
   * 获取风险分析
   * @param riskType 风险类型（可选）
   */
  async getRiskAnalysis(riskType?: string): Promise<ApiResponse<RiskFactor[]>> {
    const params = riskType ? { risk_type: riskType } : {};
    return this.apiClient.get('/v1/insights/risk-analysis', { params });
  }

  /**
   * 评估业务风险
   * @param businessData 业务数据
   */
  async assessBusinessRisk(businessData: {
    customer_id?: string;
    transaction_amount?: number;
    product_category?: string;
    region?: string;
  }): Promise<ApiResponse<{
    overall_risk_score: number;
    risk_level: string;
    risk_factors: RiskFactor[];
    recommendations: string[];
  }>> {
    return this.apiClient.post('/v1/insights/risk-assessment', businessData);
  }

  /**
   * 生成业务报告
   * @param reportType 报告类型
   * @param parameters 报告参数
   */
  async generateBusinessReport(reportType: string, parameters: any): Promise<ApiResponse<BusinessReport>> {
    return this.apiClient.post('/v1/insights/generate-report', {
      report_type: reportType,
      parameters
    });
  }

  /**
   * 获取业务报告列表
   */
  async getBusinessReports(): Promise<ApiResponse<BusinessReport[]>> {
    return this.apiClient.get('/v1/insights/reports');
  }

  /**
   * 获取智能推荐
   * @param context 上下文信息
   */
  async getRecommendations(context: {
    customer_id?: string;
    product_category?: string;
    interaction_history?: any[];
  }): Promise<ApiResponse<{
    product_recommendations: any[];
    pricing_suggestions: any[];
    marketing_strategies: any[];
    next_actions: string[];
  }>> {
    return this.apiClient.post('/v1/insights/recommendations', context);
  }

  /**
   * 获取统计数据
   * @param metric 指标类型
   * @param timeRange 时间范围
   */
  async getStatistics(metric: string, timeRange?: {
    start_date: string;
    end_date: string;
  }): Promise<ApiResponse<{
    metric: string;
    data: any[];
    summary: {
      total: number;
      average: number;
      growth_rate: number;
    };
  }>> {
    const params = { metric, ...timeRange };
    return this.apiClient.get('/v1/insights/statistics', { params });
  }
}

// 导出单例实例
export const insightsApi = new InsightsApiService();
export default insightsApi;