/**
 * 知识抽取页面
 */

import React, { useState, useCallback } from 'react';
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
} from 'antd';
import {
  UploadOutlined,
  FileTextOutlined,
  ExperimentOutlined,
  DownloadOutlined,
  ClearOutlined,
} from '@ant-design/icons';
import type { UploadProps, TabsProps } from 'antd';
import { extractionService } from '../services';
import type { ExtractionResult, Entity, Relation } from '../types';

const { TextArea } = Input;
const { Title, Text, Paragraph } = Typography;


/**
 * 知识抽取页面组件
 */
const ExtractionPage: React.FC = () => {
  // 状态管理
  const [activeTab, setActiveTab] = useState<string>('text');
  const [textInput, setTextInput] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [extractionResult, setExtractionResult] = useState<ExtractionResult | null>(null);
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const [fileList, setFileList] = useState<any[]>([]);

  /**
   * 处理文本抽取
   */
  const handleTextExtraction = useCallback(async () => {
    if (!textInput.trim()) {
      message.warning('请输入要抽取的文本内容');
      return;
    }

    setLoading(true);
    try {
      const response = await extractionService.extractFromText({ text: textInput });
      if (response.success && response.data) {
        setExtractionResult(response.data);
        message.success('文本知识抽取完成');
      } else {
        message.error(response.error || '抽取失败');
      }
    } catch (error) {
      message.error('抽取过程中发生错误');
      console.error('Text extraction error:', error);
    } finally {
      setLoading(false);
    }
  }, [textInput]);

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
    const entityColors: Record<string, string> = {
      PERSON: 'blue',
      ORGANIZATION: 'green',
      LOCATION: 'orange',
      TIME: 'purple',
      EVENT: 'red',
      CONCEPT: 'cyan',
    };

    return entities.map((entity, index) => (
      <Tag
        key={`${entity.id}-${index}`}
        color={entityColors[entity.type] || 'default'}
        className="entity-tag"
        style={{ margin: '2px 4px 2px 0' }}
      >
        {entity.text} ({entity.type})
      </Tag>
    ));
  };

  /**
   * 渲染关系标签
   */
  const renderRelationTags = (relations: Relation[]) => {
    return relations.map((relation, index) => (
      <Tag
        key={`${relation.id}-${index}`}
        color="geekblue"
        className="relation-tag"
        style={{ margin: '2px 4px 2px 0' }}
      >
        {relation.source_text} → {relation.type} → {relation.target_text}
      </Tag>
    ));
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
                        <Text>实体数量: {extractionResult.entities.length}</Text>
                        <br />
                        <Text>关系数量: {extractionResult.relations.length}</Text>
                        <br />
                        <Text>置信度: {(extractionResult.confidence * 100).toFixed(1)}%</Text>
                      </div>
                    }
                    type="info"
                    showIcon
                    className="mb-16"
                  />

                  {/* 实体列表 */}
                  <div className="mb-24">
                    <Title level={4}>实体 ({extractionResult.entities.length})</Title>
                    {extractionResult.entities.length > 0 ? (
                      <div style={{ maxHeight: 200, overflowY: 'auto' }}>
                        {renderEntityTags(extractionResult.entities)}
                      </div>
                    ) : (
                      <Empty description="未发现实体" image={Empty.PRESENTED_IMAGE_SIMPLE} />
                    )}
                  </div>

                  <Divider />

                  {/* 关系列表 */}
                  <div>
                    <Title level={4}>关系 ({extractionResult.relations.length})</Title>
                    {extractionResult.relations.length > 0 ? (
                      <div style={{ maxHeight: 200, overflowY: 'auto' }}>
                        {renderRelationTags(extractionResult.relations)}
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