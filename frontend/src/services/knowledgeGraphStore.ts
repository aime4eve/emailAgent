/**
 * 知识图谱数据存储服务
 * 负责管理抽取结果的持久化和检索
 */

import type { ExtractionResult } from '../types';
import type { KnowledgeGraphData } from '../types/graph';
import { convertExtractionToGraphData, mergeGraphData } from '../utils/graphDataConverter';

/**
 * 存储的图谱数据项
 */
interface StoredGraphItem {
  id: string;
  name: string;
  extractionResult: ExtractionResult;
  graphData: KnowledgeGraphData;
  createdAt: string;
  updatedAt: string;
  source: 'text' | 'file';
  originalContent?: string;
}

/**
 * 知识图谱存储服务类
 */
class KnowledgeGraphStore {
  private readonly STORAGE_KEY = 'knowledge_graph_data';
  private readonly MAX_STORED_ITEMS = 50; // 最大存储项目数

  /**
   * 保存抽取结果到本地存储
   * @param extractionResult 抽取结果
   * @param name 数据项名称
   * @param source 数据来源
   * @param originalContent 原始内容
   * @returns 保存的数据项ID
   */
  saveExtractionResult(
    extractionResult: ExtractionResult,
    name: string,
    source: 'text' | 'file' = 'text',
    originalContent?: string
  ): string {
    try {
      const id = this.generateId();
      const now = new Date().toISOString();
      
      // 转换为图谱数据
      const graphData = convertExtractionToGraphData(extractionResult);
      
      const item: StoredGraphItem = {
        id,
        name,
        extractionResult,
        graphData,
        createdAt: now,
        updatedAt: now,
        source,
        originalContent,
      };
      
      // 获取现有数据
      const existingItems = this.getAllStoredItems();
      
      // 添加新项目
      existingItems.unshift(item);
      
      // 限制存储数量
      if (existingItems.length > this.MAX_STORED_ITEMS) {
        existingItems.splice(this.MAX_STORED_ITEMS);
      }
      
      // 保存到本地存储
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(existingItems));
      
      console.log(`知识图谱数据已保存: ${name} (ID: ${id})`);
      return id;
    } catch (error) {
      console.error('保存知识图谱数据失败:', error);
      throw new Error('保存数据失败');
    }
  }

  /**
   * 获取所有存储的数据项
   * @returns 存储的数据项列表
   */
  getAllStoredItems(): StoredGraphItem[] {
    try {
      const data = localStorage.getItem(this.STORAGE_KEY);
      return data ? JSON.parse(data) : [];
    } catch (error) {
      console.error('读取存储数据失败:', error);
      return [];
    }
  }

  /**
   * 根据ID获取数据项
   * @param id 数据项ID
   * @returns 数据项或null
   */
  getItemById(id: string): StoredGraphItem | null {
    const items = this.getAllStoredItems();
    return items.find(item => item.id === id) || null;
  }

  /**
   * 获取最新的图谱数据
   * @returns 最新的图谱数据或null
   */
  getLatestGraphData(): KnowledgeGraphData | null {
    const items = this.getAllStoredItems();
    return items.length > 0 ? items[0].graphData : null;
  }

  /**
   * 获取合并后的所有图谱数据
   * @param limit 限制合并的数据项数量
   * @returns 合并后的图谱数据
   */
  getMergedGraphData(limit: number = 10): KnowledgeGraphData | null {
    const items = this.getAllStoredItems().slice(0, limit);
    if (items.length === 0) return null;
    
    const graphDataList = items.map(item => item.graphData);
    return mergeGraphData(graphDataList);
  }

  /**
   * 删除数据项
   * @param id 数据项ID
   * @returns 是否删除成功
   */
  deleteItem(id: string): boolean {
    try {
      const items = this.getAllStoredItems();
      const filteredItems = items.filter(item => item.id !== id);
      
      if (filteredItems.length === items.length) {
        return false; // 没有找到要删除的项目
      }
      
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(filteredItems));
      console.log(`数据项已删除: ${id}`);
      return true;
    } catch (error) {
      console.error('删除数据项失败:', error);
      return false;
    }
  }

  /**
   * 清空所有数据
   */
  clearAll(): void {
    try {
      localStorage.removeItem(this.STORAGE_KEY);
      console.log('所有知识图谱数据已清空');
    } catch (error) {
      console.error('清空数据失败:', error);
    }
  }

  /**
   * 更新数据项
   * @param id 数据项ID
   * @param updates 更新内容
   * @returns 是否更新成功
   */
  updateItem(id: string, updates: Partial<StoredGraphItem>): boolean {
    try {
      const items = this.getAllStoredItems();
      const itemIndex = items.findIndex(item => item.id === id);
      
      if (itemIndex === -1) {
        return false; // 没有找到要更新的项目
      }
      
      items[itemIndex] = {
        ...items[itemIndex],
        ...updates,
        updatedAt: new Date().toISOString(),
      };
      
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(items));
      console.log(`数据项已更新: ${id}`);
      return true;
    } catch (error) {
      console.error('更新数据项失败:', error);
      return false;
    }
  }

  /**
   * 搜索数据项
   * @param query 搜索关键词
   * @returns 匹配的数据项列表
   */
  searchItems(query: string): StoredGraphItem[] {
    const items = this.getAllStoredItems();
    const lowerQuery = query.toLowerCase();
    
    return items.filter(item => 
      item.name.toLowerCase().includes(lowerQuery) ||
      item.originalContent?.toLowerCase().includes(lowerQuery) ||
      item.extractionResult.entities?.some(entity => 
        (entity.text || '').toLowerCase().includes(lowerQuery)
      ) ||
      item.extractionResult.relations?.some(relation => 
        (relation.type || '').toLowerCase().includes(lowerQuery)
      )
    );
  }

  /**
   * 获取存储统计信息
   * @returns 统计信息
   */
  getStorageStats(): {
    totalItems: number;
    totalNodes: number;
    totalEdges: number;
    storageSize: string;
    oldestItem?: string;
    newestItem?: string;
  } {
    const items = this.getAllStoredItems();
    const totalNodes = items.reduce((sum, item) => sum + item.graphData.nodes.length, 0);
    const totalEdges = items.reduce((sum, item) => sum + item.graphData.edges.length, 0);
    
    // 计算存储大小（近似值）
    const storageData = localStorage.getItem(this.STORAGE_KEY) || '';
    const storageSize = `${(storageData.length / 1024).toFixed(2)} KB`;
    
    return {
      totalItems: items.length,
      totalNodes,
      totalEdges,
      storageSize,
      oldestItem: items.length > 0 ? items[items.length - 1].createdAt : undefined,
      newestItem: items.length > 0 ? items[0].createdAt : undefined,
    };
  }

  /**
   * 导出所有数据
   * @returns 导出的数据
   */
  exportAllData(): {
    version: string;
    exportedAt: string;
    items: StoredGraphItem[];
  } {
    return {
      version: '1.0',
      exportedAt: new Date().toISOString(),
      items: this.getAllStoredItems(),
    };
  }

  /**
   * 导入数据
   * @param data 导入的数据
   * @param merge 是否与现有数据合并
   * @returns 导入的项目数量
   */
  importData(data: any, merge: boolean = false): number {
    try {
      if (!data.items || !Array.isArray(data.items)) {
        throw new Error('无效的导入数据格式');
      }
      
      let items: StoredGraphItem[];
      
      if (merge) {
        const existingItems = this.getAllStoredItems();
        const existingIds = new Set(existingItems.map(item => item.id));
        const newItems = data.items.filter((item: StoredGraphItem) => !existingIds.has(item.id));
        items = [...existingItems, ...newItems];
      } else {
        items = data.items;
      }
      
      // 限制存储数量
      if (items.length > this.MAX_STORED_ITEMS) {
        items = items.slice(0, this.MAX_STORED_ITEMS);
      }
      
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(items));
      console.log(`已导入 ${data.items.length} 个数据项`);
      return data.items.length;
    } catch (error) {
      console.error('导入数据失败:', error);
      throw error;
    }
  }

  /**
   * 生成唯一ID
   * @returns 唯一ID
   */
  private generateId(): string {
    return `kg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}

// 创建单例实例
export const knowledgeGraphStore = new KnowledgeGraphStore();
export default knowledgeGraphStore;