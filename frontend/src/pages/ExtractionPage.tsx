/**
 * 知识抽取页面
 * 提供文本和文件的知识抽取功能
 */

import React, { useState, useCallback, useEffect } from 'react';
import {
  Card,
  Tabs,
  Input,
  Button,
  Upload,
  message,
  Spin,
  Row,
  Col,
  Tag,
  Typography,
  Space,
  Divider,
  Alert,
  Progress,
  Empty,
  notification,
} from 'antd';
import {
  UploadOutlined,
  FileTextOutlined,
  ExperimentOutlined,
  DownloadOutlined,
  ClearOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons';
import type { UploadProps, TabsProps } from 'antd';
import { extractionService } from '../services';
import { knowledgeGraphStore } from '../services/knowledgeGraphStore';
import type { ExtractionResult, Entity, Relation } from '../types';

const { TextArea } = Input;
const { Title, Text, Paragraph } = Typography;


/**
 * 知识抽取页面组件
 */
const ExtractionPage: React.FC = () => {
  // 状态管理
  const [activeTab, setActiveTab] = useState<string>('text');
  const [textInput, setTextInput] = useState<string>('我是张三，来自北京的ABC公司。我们公司专门生产电子产品，包括手机、平板电脑和笔记本电脑。我们希望与贵公司建立长期的合作关系。请联系我们的销售经理李四，电话是13800138000。');
  const [loading, setLoading] = useState<boolean>(false);
  const [extractionResult, setExtractionResult] = useState<ExtractionResult | null>(null);
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const [fileList, setFileList] = useState<any[]>([]);
  const [apiStatus, setApiStatus] = useState<'checking' | 'available' | 'unavailable'>('checking');

  /**
   * 检查API服务状态
   */
  const checkApiStatus = useCallback(async () => {
    try {
      console.log('检查API服务状态...');
      const response = await extractionService.checkHealth();
      console.log('API健康检查响应:', response);
      
      if (response.success) {
        setApiStatus('available');
        console.log('API服务可用');
      } else {
        setApiStatus('unavailable');
        console.error('API服务不可用:', response.error);
      }
    } catch (error) {
      console.error('API健康检查失败:', error);
      setApiStatus('unavailable');
    }
  }, []);

  // 组件挂载时检查API状态
  useEffect(() => {
    checkApiStatus();
  }, [checkApiStatus]);

  /**
   * 处理文本抽取
   */
  const handleTextExtraction = useCallback(async () => {
    console.log('=== 开始文本知识抽取 ===');
    console.log('文本内容:', textInput);
    console.log('文本长度:', textInput.length);
    console.log('API状态:', apiStatus);
    
    // 检查输入
    if (!textInput.trim()) {
      message.warning('请输入要抽取的文本内容');
      return;
    }

    // 检查API状态
    if (apiStatus === 'unavailable') {
      message.error('API服务不可用，请检查后端服务是否正常运行');
      return;
    }

    // 验证文本
    const validation = extractionService.validateText(textInput);
    if (!validation.valid) {
      message.error(validation.message || '文本验证失败');
      return;
    }

    setLoading(true);
    setExtractionResult(null);
    
    // 显示开始通知
    notification.info({
      message: '开始知识抽取',
      description: '正在分析文本内容，请稍候...',
      icon: <ExperimentOutlined style={{ color: '#1890ff' }} />,
      duration: 2,
    });
    
    try {
      const requestData = { text: textInput.trim() };
      console.log('发送API请求:', {
        url: '/api/extract',
        method: 'POST',
        data: requestData,
      });
      
      const startTime = Date.now();
      const response = await extractionService.extractFromText(requestData);
      const endTime = Date.now();
      const duration = endTime - startTime;
      
      console.log('API响应:', {
        success: response.success,
        duration: `${duration}ms`,
        data: response.data,
        error: response.error,
      });
      
      if (response.success && response.data) {
        console.log('抽取成功!');
        console.log('原始响应数据:', response.data);
        
        // 处理后端返回的数据结构
        const processedData = {
          entities: response.data.entities || [],
          relations: response.data.relations || [],
          confidence: response.data.confidence || 0,
          statistics: response.data.statistics,
          processing_time: response.data.statistics?.processing_time || response.data.processing_time
        };
        
        console.log('处理后的数据:', processedData);
        console.log('实体数量:', processedData.entities.length);
        console.log('关系数量:', processedData.relations.length);
        console.log('置信度:', processedData.confidence);
        
        setExtractionResult(processedData);
        
        // 保存抽取结果到图谱存储
        try {
          const itemName = `文本抽取_${new Date().toLocaleString()}`;
          const savedId = knowledgeGraphStore.saveExtractionResult(
            processedData,
            itemName,
            'text',
            textInput.trim()
          );
          console.log('抽取结果已保存到图谱存储:', savedId);
        } catch (saveError) {
          console.warn('保存抽取结果失败:', saveError);
        }
        
        // 显示成功通知
        notification.success({
          message: '知识抽取完成',
          description: `成功抽取 ${processedData.entities.length} 个实体和 ${processedData.relations.length} 个关系，已保存到图谱数据库`,
          icon: <CheckCircleOutlined style={{ color: '#52c41a' }} />,
          duration: 4,
        });
        
        message.success(`抽取完成！用时 ${duration}ms`);
      } else {
        console.error('抽取失败:', response.error);
        
        // 显示错误通知
        notification.error({
          message: '知识抽取失败',
          description: response.error || '未知错误',
          icon: <ExclamationCircleOutlined style={{ color: '#ff4d4f' }} />,
          duration: 6,
        });
        
        message.error(response.error || '抽取失败');
      }
    } catch (error: any) {
      console.error('抽取过程中发生异常:', error);
      
      // 显示异常通知
      notification.error({
        message: '系统错误',
        description: error.message || '抽取过程中发生未知错误',
        icon: <ExclamationCircleOutlined style={{ color: '#ff4d4f' }} />,
        duration: 8,
      });
      
      message.error('抽取过程中发生错误，请检查网络连接和后端服务');
    } finally {
      setLoading(false);
      console.log('=== 文本知识抽取结束 ===');
    }
  }, [textInput, apiStatus]);

  /**
   * 处理文件上传
   */
  const handleFileUpload: UploadProps['customRequest'] = async (options) => {
    const { file, onSuccess, onError, onProgress } = options;
    
    setLoading(true);
    setUploadProgress(0);
    
    try {
      const response = await extractionService.extractFromFile(
        file as File,
        undefined,
        (progress: number) => {
          setUploadProgress(progress);
          onProgress?.({ percent: progress });
        }
      );
      
      if (response.success && response.data) {
        setExtractionResult(response.data);
        message.success('文件知识抽取完成');
        onSuccess?.(response.data);
      } else {
        message.error(response.error || '抽取失败');
        onError?.(new Error(response.error || '抽取失败'));
      }
    } catch (error) {
      message.error('文件上传失败');
      onError?.(error as Error);
      console.error('File upload error:', error);
    } finally {
      setLoading(false);
      setUploadProgress(0);
    }
  };

  /**
   * 处理文件列表变化
   */
  const handleFileChange: UploadProps['onChange'] = (info) => {
    setFileList(info.fileList);
  };

  /**
   * 清空结果
   */
  const handleClearResults = () => {
    setExtractionResult(null);
    setTextInput('');
    setFileList([]);
    message.info('已清空抽取结果');
  };

  /**
   * 导出结果
   */
  const handleExportResults = () => {
    if (!extractionResult) {
      message.warning('没有可导出的结果');
      return;
    }

    const dataStr = JSON.stringify(extractionResult, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `extraction_result_${new Date().getTime()}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    message.success('结果已导出');
  };

  /**
   * 渲染实体标签
   */
  const renderEntityTags = (entities: Entity[]) => {
    if (!entities || !Array.isArray(entities)) {
      return null;
    }

    const entityColors: Record<string, string> = {
      PERSON: 'blue',
      ORG: 'green',
      ORGANIZATION: 'green',
      LOC: 'orange',
      LOCATION: 'orange',
      TIME: 'purple',
      PRODUCT: 'magenta',
      PHONE: 'cyan',
      EMAIL: 'geekblue',
      CONTACT: 'volcano',
      EVENT: 'red',
      CONCEPT: 'cyan',
    };

    return entities.map((entity, index) => {
      // 安全地获取实体信息
      const entityText = entity.text || '未知实体';
      const entityType = entity.type || '未知类型';
      const confidence = entity.confidence ? `${(entity.confidence * 100).toFixed(0)}%` : '';
      
      return (
        <Tag
          key={`${entity.id}-${index}`}
          color={entityColors[entityType] || 'default'}
          className="entity-tag"
          style={{ margin: '2px 4px 2px 0' }}
          title={`置信度: ${confidence}`}
        >
          {entityText} ({entityType})
        </Tag>
      );
    });
  };

  /**
   * 渲染关系标签
   */
  const renderRelationTags = (relations: Relation[]) => {
    if (!relations || !Array.isArray(relations)) {
      return null;
    }

    return relations.map((relation, index) => {
      // 安全地获取关系信息，兼容不同的数据结构
      const sourceText = relation.source_text || '未知';
      const targetText = relation.target_text || '未知';
      const relationType = relation.type || '未知关系';
      const confidence = relation.confidence ? `${(relation.confidence * 100).toFixed(0)}%` : '';
      
      return (
        <Tag
          key={`${relation.id}-${index}`}
          color="geekblue"
          className="relation-tag"
          style={{ margin: '2px 4px 2px 0' }}
          title={`置信度: ${confidence}`}
        >
          {sourceText} → {relationType} → {targetText}
        </Tag>
      );
    });
  };

  // 标签页配置
  const tabItems: TabsProps['items'] = [
    {
      key: 'text',
      label: (
        <span>
          <FileTextOutlined />
          文本抽取
        </span>
      ),
      children: (
        <div>
          <Card title="输入文本" className="mb-16">
            <TextArea
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              placeholder="请输入要进行知识抽取的文本内容..."
              rows={8}
              showCount
              maxLength={10000}
            />
            <div style={{ marginTop: 16, textAlign: 'right' }}>
              <Space>
                <Button onClick={() => setTextInput('')}>清空</Button>
                <Button
                  type="primary"
                  icon={<ExperimentOutlined />}
                  onClick={handleTextExtraction}
                  loading={loading}
                  disabled={!textInput.trim()}
                >
                  开始抽取
                </Button>
              </Space>
            </div>
          </Card>
        </div>
      ),
    },
    {
      key: 'file',
      label: (
        <span>
          <UploadOutlined />
          文件抽取
        </span>
      ),
      children: (
        <div>
          <Card title="上传文件" className="mb-16">
            <Upload.Dragger
              name="file"
              multiple={false}
              fileList={fileList}
              customRequest={handleFileUpload}
              onChange={handleFileChange}
              accept=".txt,.pdf,.doc,.docx"
              disabled={loading}
            >
              <p className="ant-upload-drag-icon">
                <UploadOutlined style={{ fontSize: 48, color: '#1890ff' }} />
              </p>
              <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
              <p className="ant-upload-hint">
                支持 TXT、PDF、DOC、DOCX 格式文件
              </p>
            </Upload.Dragger>
            
            {uploadProgress > 0 && (
              <div style={{ marginTop: 16 }}>
                <Progress percent={uploadProgress} status="active" />
              </div>
            )}
          </Card>
        </div>
      ),
    },
  ];

  return (
    <div>
      <Row gutter={[24, 24]}>
        <Col span={24}>
          <Card>
            <div className="flex-between mb-16">
              <Title level={2} style={{ margin: 0 }}>
                知识抽取
              </Title>
              <Space>
                {/* API状态指示器 */}
                <div style={{ display: 'flex', alignItems: 'center', marginRight: 16 }}>
                  {apiStatus === 'checking' && (
                    <>
                      <Spin size="small" style={{ marginRight: 8 }} />
                      <Text type="secondary">检查服务状态...</Text>
                    </>
                  )}
                  {apiStatus === 'available' && (
                    <>
                      <CheckCircleOutlined style={{ color: '#52c41a', marginRight: 8 }} />
                      <Text style={{ color: '#52c41a' }}>服务正常</Text>
                    </>
                  )}
                  {apiStatus === 'unavailable' && (
                    <>
                      <ExclamationCircleOutlined style={{ color: '#ff4d4f', marginRight: 8 }} />
                      <Text style={{ color: '#ff4d4f' }}>服务异常</Text>
                      <Button 
                        size="small" 
                        type="link" 
                        onClick={checkApiStatus}
                        style={{ padding: '0 8px' }}
                      >
                        重试
                      </Button>
                    </>
                  )}
                </div>
                
                <Button
                  icon={<ClearOutlined />}
                  onClick={handleClearResults}
                  disabled={!extractionResult}
                >
                  清空结果
                </Button>
                <Button
                  type="primary"
                  icon={<DownloadOutlined />}
                  onClick={handleExportResults}
                  disabled={!extractionResult}
                >
                  导出结果
                </Button>
              </Space>
            </div>
            
            <Paragraph type="secondary">
              从文本或文件中自动抽取实体、关系等知识元素，构建结构化的知识表示。
            </Paragraph>
            
            {/* API状态警告 */}
            {apiStatus === 'unavailable' && (
              <Alert
                message="后端服务不可用"
                description="请确保后端API服务正在运行（http://localhost:5000），然后点击重试按钮。"
                type="warning"
                showIcon
                style={{ marginTop: 16 }}
              />
            )}
          </Card>
        </Col>
      </Row>

      <Row gutter={[24, 24]} style={{ marginTop: 24 }}>
        <Col span={12}>
          <Card title="输入" className="full-height">
            <Tabs
              activeKey={activeTab}
              onChange={setActiveTab}
              items={tabItems}
            />
          </Card>
        </Col>
        
        <Col span={12}>
          <Card title="抽取结果" className="full-height">
            <Spin spinning={loading}>
              {extractionResult ? (
                <div>
                  {/* 统计信息 */}
                  <Alert
                    message="抽取统计"
                    description={
                      <div>
                        <Text>实体数量: {extractionResult.entities?.length || 0}</Text>
                        <br />
                        <Text>关系数量: {extractionResult.relations?.length || 0}</Text>
                        <br />
                        <Text>置信度: {((extractionResult.confidence || 0) * 100).toFixed(1)}%</Text>
                      </div>
                    }
                    type="info"
                    showIcon
                    className="mb-16"
                  />

                  {/* 实体列表 */}
                  <div className="mb-24">
                    <Title level={4}>实体 ({extractionResult.entities?.length || 0})</Title>
                    {(extractionResult.entities?.length || 0) > 0 ? (
                      <div style={{ maxHeight: 200, overflowY: 'auto' }}>
                        {renderEntityTags(extractionResult.entities || [])}
                      </div>
                    ) : (
                      <Empty description="未发现实体" image={Empty.PRESENTED_IMAGE_SIMPLE} />
                    )}
                  </div>

                  <Divider />

                  {/* 关系列表 */}
                  <div>
                    <Title level={4}>关系 ({extractionResult.relations?.length || 0})</Title>
                    {(extractionResult.relations?.length || 0) > 0 ? (
                      <div style={{ maxHeight: 200, overflowY: 'auto' }}>
                        {renderRelationTags(extractionResult.relations || [])}
                      </div>
                    ) : (
                      <Empty description="未发现关系" image={Empty.PRESENTED_IMAGE_SIMPLE} />
                    )}
                  </div>
                </div>
              ) : (
                <Empty
                  description="请选择文本或文件进行知识抽取"
                  image={Empty.PRESENTED_IMAGE_SIMPLE}
                />
              )}
            </Spin>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default ExtractionPage;