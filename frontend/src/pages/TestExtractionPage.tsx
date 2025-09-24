/**
 * 测试知识抽取功能页面
 */

import React, { useState } from 'react';
import { Button, Input, Card, message, Spin } from 'antd';
import { extractionService } from '../services';
import type { ExtractionResult } from '../types';

const { TextArea } = Input;

/**
 * 测试知识抽取页面组件
 */
const TestExtractionPage: React.FC = () => {
  const [textInput, setTextInput] = useState<string>('我是张三，来自北京的ABC公司。我们公司专门生产电子产品，包括手机和平板电脑。');
  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<ExtractionResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  /**
   * 测试文本抽取功能
   */
  const handleTestExtraction = async () => {
    console.log('=== 开始测试知识抽取功能 ===');
    console.log('输入文本:', textInput);
    
    if (!textInput.trim()) {
      message.warning('请输入要抽取的文本内容');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);
    
    try {
      console.log('调用extractionService.extractFromText...');
      const requestData = { text: textInput };
      console.log('请求数据:', requestData);
      
      const response = await extractionService.extractFromText(requestData);
      console.log('API响应:', response);
      
      if (response.success && response.data) {
        console.log('抽取成功!');
        console.log('实体数量:', response.data.entities?.length || 0);
        console.log('关系数量:', response.data.relations?.length || 0);
        console.log('置信度:', response.data.confidence);
        
        setResult(response.data);
        message.success('文本知识抽取完成');
      } else {
        console.error('抽取失败:', response.error);
        setError(response.error || '抽取失败');
        message.error(response.error || '抽取失败');
      }
    } catch (error: any) {
      console.error('抽取过程中发生异常:', error);
      setError(error.message || '抽取过程中发生错误');
      message.error('抽取过程中发生错误');
    } finally {
      setLoading(false);
      console.log('=== 测试结束 ===');
    }
  };

  return (
    <div style={{ padding: 24 }}>
      <Card title="知识抽取功能测试" style={{ marginBottom: 24 }}>
        <div style={{ marginBottom: 16 }}>
          <label>输入文本:</label>
          <TextArea
            value={textInput}
            onChange={(e) => setTextInput(e.target.value)}
            placeholder="请输入要进行知识抽取的文本内容..."
            rows={4}
            style={{ marginTop: 8 }}
          />
        </div>
        
        <Button
          type="primary"
          onClick={handleTestExtraction}
          loading={loading}
          disabled={!textInput.trim()}
        >
          开始抽取测试
        </Button>
      </Card>

      {loading && (
        <Card title="处理中...">
          <Spin size="large" />
          <p>正在进行知识抽取，请稍候...</p>
        </Card>
      )}

      {error && (
        <Card title="错误信息" style={{ borderColor: '#ff4d4f' }}>
          <p style={{ color: '#ff4d4f' }}>{error}</p>
        </Card>
      )}

      {result && (
        <Card title="抽取结果">
          <div style={{ marginBottom: 16 }}>
            <h4>统计信息:</h4>
            <p>实体数量: {result.entities?.length || 0}</p>
            <p>关系数量: {result.relations?.length || 0}</p>
            <p>置信度: {((result.confidence || 0) * 100).toFixed(1)}%</p>
          </div>
          
          {result.entities && result.entities.length > 0 && (
            <div style={{ marginBottom: 16 }}>
              <h4>实体列表:</h4>
              {result.entities.map((entity, index) => (
                <div key={index} style={{ marginBottom: 8, padding: 8, border: '1px solid #d9d9d9', borderRadius: 4 }}>
                  <strong>{entity.text}</strong> ({entity.type}) - 置信度: {(entity.confidence * 100).toFixed(1)}%
                </div>
              ))}
            </div>
          )}
          
          {result.relations && result.relations.length > 0 && (
            <div style={{ marginBottom: 16 }}>
              <h4>关系列表:</h4>
              {result.relations.map((relation, index) => (
                <div key={index} style={{ marginBottom: 8, padding: 8, border: '1px solid #d9d9d9', borderRadius: 4 }}>
                  <strong>{relation.source_text}</strong> → {relation.type} → <strong>{relation.target_text}</strong>
                  <br />置信度: {(relation.confidence * 100).toFixed(1)}%
                </div>
              ))}
            </div>
          )}
          
          <div>
            <h4>完整响应数据:</h4>
            <pre style={{ background: '#f5f5f5', padding: 12, borderRadius: 4, overflow: 'auto' }}>
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        </Card>
      )}
    </div>
  );
};

export default TestExtractionPage;