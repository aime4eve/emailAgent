/**
 * 通用类型定义
 */

// 导出所有类型
export * from './api';
export * from './graph';
export * from './ontology';

// 通用分页类型
export interface Pagination {
  current: number;
  pageSize: number;
  total: number;
  showSizeChanger?: boolean;
  showQuickJumper?: boolean;
  showTotal?: (total: number, range: [number, number]) => string;
}

// 表格列配置
export interface TableColumn<T = any> {
  key: string;
  title: string;
  dataIndex?: string;
  width?: number;
  align?: 'left' | 'center' | 'right';
  sorter?: boolean | ((a: T, b: T) => number);
  filters?: { text: string; value: any }[];
  render?: (value: any, record: T, index: number) => React.ReactNode;
}

// 表单字段类型
export interface FormField {
  name: string;
  label: string;
  type: 'input' | 'textarea' | 'select' | 'checkbox' | 'radio' | 'date' | 'number' | 'file';
  required?: boolean;
  placeholder?: string;
  options?: { label: string; value: any }[];
  rules?: any[];
  disabled?: boolean;
  defaultValue?: any;
}

// 菜单项类型
export interface MenuItem {
  key: string;
  label: string;
  icon?: React.ReactNode;
  path?: string;
  children?: MenuItem[];
  disabled?: boolean;
}

// 面包屑项类型
export interface BreadcrumbItem {
  title: string;
  path?: string;
}

// 通知类型
export interface Notification {
  id: string;
  type: 'success' | 'info' | 'warning' | 'error';
  title: string;
  message?: string;
  duration?: number;
  timestamp: string;
}

// 加载状态
export interface LoadingState {
  loading: boolean;
  error?: string | null;
  data?: any;
}

// 文件信息
export interface FileInfo {
  name: string;
  size: number;
  type: string;
  lastModified: number;
  url?: string;
}

// 搜索条件
export interface SearchCondition {
  keyword?: string;
  filters?: Record<string, any>;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
  page?: number;
  pageSize?: number;
}

// 操作结果
export interface OperationResult<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
  timestamp: string;
}

// 统计数据
export interface StatisticsData {
  label: string;
  value: number;
  unit?: string;
  trend?: 'up' | 'down' | 'stable';
  percentage?: number;
}

// 图表数据点
export interface ChartDataPoint {
  x: string | number;
  y: number;
  category?: string;
  [key: string]: any;
}

// 主题配置
export interface ThemeConfig {
  primaryColor: string;
  backgroundColor: string;
  textColor: string;
  borderColor: string;
  mode: 'light' | 'dark';
}