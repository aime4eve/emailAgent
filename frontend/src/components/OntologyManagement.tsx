/**
 * 知识本体管理组件
 * 提供本体的创建、编辑、删除、导入导出等功能
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  Card,
  Row,
  Col,
  Button,
  Table,
  Modal,
  Form,
  Input,
  Space,
  Typography,
  message,
  Popconfirm,
  Tag,
  Upload,
  Select,
  Divider,
  Tooltip,
  Badge,
  Spin,
  Empty,
  Pagination,
  Drawer,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  UploadOutlined,
  DownloadOutlined,
  EyeOutlined,
  SearchOutlined,
  ReloadOutlined,
  FileTextOutlined,
  SettingOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { ontologyService } from '../services';
import OntologyEditor from './OntologyEditor';
import OntologyVisualization from './OntologyVisualization';

const { Title, Text } = Typography;
const { TextArea } = Input;
const { Option } = Select;

/**
 * 本体数据接口
 */
interface OntologyData {
  id: string;
  name: string;
  description: string;
  version: string;
  author: string;
  tags: string[];
  entity_count: number;
  relation_count: number;
  created_at: string;
  updated_at: string;
}

/**
 * 本体管理组件属性
 */
interface OntologyManagementProps {
  className?: string;
}

/**
 * 本体管理组件
 */
const OntologyManagement: React.FC<OntologyManagementProps> = ({ className }) => {
  // 状态管理
  const [loading, setLoading] = useState<boolean>(false);
  const [ontologies, setOntologies] = useState<OntologyData[]>([]);
  const [selectedOntology, setSelectedOntology] = useState<OntologyData | null>(null);
  const [statistics, setStatistics] = useState<any>(null);
  
  // 分页状态
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(10);
  const [total, setTotal] = useState<number>(0);
  
  // 搜索和过滤状态
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [availableTags, setAvailableTags] = useState<string[]>([]);
  
  // 模态框状态
  const [createModalVisible, setCreateModalVisible] = useState<boolean>(false);
  const [editModalVisible, setEditModalVisible] = useState<boolean>(false);
  const [importModalVisible, setImportModalVisible] = useState<boolean>(false);
  const [detailModalVisible, setDetailModalVisible] = useState<boolean>(false);
  const [editorDrawerVisible, setEditorDrawerVisible] = useState<boolean>(false);
  
  // 编辑状态
  const [editingOntology, setEditingOntology] = useState<OntologyData | null>(null);
  const [ontologyDetail, setOntologyDetail] = useState<any>(null);
  
  // 表单实例
  const [createForm] = Form.useForm();
  const [editForm] = Form.useForm();
  const [importForm] = Form.useForm();

  /**
   * 加载本体列表
   */
  const loadOntologies = useCallback(async () => {
    setLoading(true);
    try {
      const response = await ontologyService.getOntologies(
        currentPage,
        pageSize,
        searchTerm || undefined,
        selectedTags.length > 0 ? selectedTags : undefined
      );
      
      if (response.success && response.data) {
        setOntologies(response.data.ontologies || []);
        setTotal(response.data.total || 0);
      } else {
        message.error(response.error || '加载本体列表失败');
      }
    } catch (error) {
      message.error('加载本体列表时发生错误');
      console.error('Load ontologies error:', error);
    } finally {
      setLoading(false);
    }
  }, [currentPage, pageSize, searchTerm, selectedTags]);

  /**
   * 加载统计信息
   */
  const loadStatistics = useCallback(async () => {
    try {
      const response = await ontologyService.getStatistics();
      if (response.success && response.data) {
        setStatistics(response.data);
        setAvailableTags(response.data.all_tags || []);
      }
    } catch (error) {
      // 静默处理统计信息加载错误，不影响主要功能
      console.warn('Statistics API not available:', error);
      // 设置默认统计信息
      setStatistics({
        total_ontologies: ontologies.length,
        total_entities: 0,
        total_relations: 0,
        unique_authors: 0,
        unique_tags: 0,
        all_tags: []
      });
    }
  }, [ontologies.length]);

  /**
   * 加载本体详情
   */
  const loadOntologyDetail = useCallback(async (ontologyId: string) => {
    setLoading(true);
    try {
      const response = await ontologyService.getOntology(ontologyId);
      if (response.success && response.data) {
        setOntologyDetail(response.data);
      } else {
        message.error(response.error || '加载本体详情失败');
      }
    } catch (error) {
      message.error('加载本体详情时发生错误');
      console.error('Load ontology detail error:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * 创建本体
   */
  const handleCreateOntology = async (values: any) => {
    try {
      const response = await ontologyService.createOntology({
        ...values,
        entity_types: [],
        relation_types: [],
        tags: values.tags || []
      });
      
      if (response.success) {
        message.success('本体创建成功');
        setCreateModalVisible(false);
        createForm.resetFields();
        loadOntologies();
        loadStatistics();
      } else {
        message.error(response.error || '创建失败');
      }
    } catch (error) {
      message.error('创建时发生错误');
      console.error('Create ontology error:', error);
    }
  };

  /**
   * 更新本体
   */
  const handleUpdateOntology = async (values: any) => {
    if (!editingOntology) return;
    
    try {
      const response = await ontologyService.updateOntology(editingOntology.id, {
        ...values,
        tags: values.tags || []
      });
      
      if (response.success) {
        message.success('本体更新成功');
        setEditModalVisible(false);
        editForm.resetFields();
        setEditingOntology(null);
        loadOntologies();
        loadStatistics();
      } else {
        message.error(response.error || '更新失败');
      }
    } catch (error) {
      message.error('更新时发生错误');
      console.error('Update ontology error:', error);
    }
  };

  /**
   * 删除本体
   */
  const handleDeleteOntology = async (ontologyId: string) => {
    try {
      const response = await ontologyService.deleteOntology(ontologyId);
      if (response.success) {
        message.success('本体删除成功');
        loadOntologies();
        loadStatistics();
        if (selectedOntology?.id === ontologyId) {
          setSelectedOntology(null);
        }
      } else {
        message.error(response.error || '删除失败');
      }
    } catch (error) {
      message.error('删除时发生错误');
      console.error('Delete ontology error:', error);
    }
  };

  /**
   * 导出本体
   */
  const handleExportOntology = async (ontologyId: string, format: string = 'json') => {
    try {
      const response = await ontologyService.exportOntology(ontologyId, format);
      if (response.success && response.data) {
        message.success(`本体导出成功: ${response.data.file_path}`);
      } else {
        message.error(response.error || '导出失败');
      }
    } catch (error) {
      message.error('导出时发生错误');
      console.error('Export ontology error:', error);
    }
  };

  /**
   * 导入本体
   */
  const handleImportOntology = async (values: any) => {
    const { file, format } = values;
    if (!file || !file.file) {
      message.error('请选择要导入的文件');
      return;
    }
    
    try {
      const response = await ontologyService.importOntology(file.file, format);
      if (response.success) {
        message.success('本体导入成功');
        setImportModalVisible(false);
        importForm.resetFields();
        loadOntologies();
        loadStatistics();
      } else {
        message.error(response.error || '导入失败');
      }
    } catch (error) {
      message.error('导入时发生错误');
      console.error('Import ontology error:', error);
    }
  };

  /**
   * 打开编辑模态框
   */
  const openEditModal = (ontology: OntologyData) => {
    setEditingOntology(ontology);
    editForm.setFieldsValue({
      name: ontology.name,
      description: ontology.description,
      version: ontology.version,
      author: ontology.author,
      tags: ontology.tags
    });
    setEditModalVisible(true);
  };

  /**
   * 打开详情模态框
   */
  const openDetailModal = async (ontology: OntologyData) => {
    setSelectedOntology(ontology);
    await loadOntologyDetail(ontology.id);
    setDetailModalVisible(true);
  };

  /**
   * 搜索处理
   */
  const handleSearch = () => {
    setCurrentPage(1);
    loadOntologies();
  };

  /**
   * 重置搜索
   */
  const handleResetSearch = () => {
    setSearchTerm('');
    setSelectedTags([]);
    setCurrentPage(1);
  };

  // 表格列定义
  const columns: ColumnsType<OntologyData> = [
    {
      title: '本体名称',
      dataIndex: 'name',
      key: 'name',
      render: (text: string) => (
        <Space>
          <FileTextOutlined />
          <Text strong>{text}</Text>
        </Space>
      ),
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: {
        showTitle: false,
      },
      render: (text: string) => (
        <Tooltip placement="topLeft" title={text}>
          {text || '-'}
        </Tooltip>
      ),
    },
    {
      title: '版本',
      dataIndex: 'version',
      key: 'version',
      width: 100,
    },
    {
      title: '作者',
      dataIndex: 'author',
      key: 'author',
      width: 120,
    },
    {
      title: '标签',
      dataIndex: 'tags',
      key: 'tags',
      width: 200,
      render: (tags: string[]) => (
        <Space wrap>
          {tags?.map((tag) => (
            <Tag key={tag} color="blue">
              {tag}
            </Tag>
          ))}
        </Space>
      ),
    },
    {
      title: '实体/关系',
      key: 'counts',
      width: 120,
      render: (_, record: OntologyData) => (
        <Space>
          <Badge count={record.entity_count} color="green" />
          <Text>/</Text>
          <Badge count={record.relation_count} color="orange" />
        </Space>
      ),
    },
    {
      title: '更新时间',
      dataIndex: 'updated_at',
      key: 'updated_at',
      width: 180,
      render: (text: string) => (
        text ? new Date(text).toLocaleString() : '-'
      ),
    },
    {
      title: '操作',
      key: 'actions',
      width: 200,
      render: (_, record: OntologyData) => (
        <Space>
          <Tooltip title="查看详情">
            <Button
              type="text"
              icon={<EyeOutlined />}
              onClick={() => openDetailModal(record)}
            />
          </Tooltip>
          <Tooltip title="编辑基本信息">
            <Button
              type="text"
              icon={<EditOutlined />}
              onClick={() => openEditModal(record)}
            />
          </Tooltip>
          <Tooltip title="结构编辑器">
            <Button
              type="text"
              icon={<SettingOutlined />}
              onClick={() => {
                setSelectedOntology(record);
                setEditorDrawerVisible(true);
              }}
            />
          </Tooltip>
          <Tooltip title="导出">
            <Button
              type="text"
              icon={<DownloadOutlined />}
              onClick={() => handleExportOntology(record.id)}
            />
          </Tooltip>
          <Popconfirm
            title="确定要删除这个本体吗？"
            description="删除后无法恢复，请谨慎操作。"
            onConfirm={() => handleDeleteOntology(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Tooltip title="删除">
              <Button
                type="text"
                danger
                icon={<DeleteOutlined />}
              />
            </Tooltip>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  // 组件挂载时加载数据
  useEffect(() => {
    loadOntologies();
    loadStatistics();
  }, [loadOntologies, loadStatistics]);

  // 搜索条件变化时重新加载
  useEffect(() => {
    const timer = setTimeout(() => {
      if (currentPage === 1) {
        loadOntologies();
      } else {
        setCurrentPage(1);
      }
    }, 500);
    
    return () => clearTimeout(timer);
  }, [searchTerm, selectedTags]);

  return (
    <div className={className}>
      {/* 统计信息卡片 */}
      {statistics && (
        <Row gutter={16} style={{ marginBottom: 16 }}>
          <Col span={6}>
            <Card>
              <div style={{ textAlign: 'center' }}>
                <Title level={3} style={{ margin: 0, color: '#1890ff' }}>
                  {statistics.total_ontologies}
                </Title>
                <Text type="secondary">总本体数</Text>
              </div>
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <div style={{ textAlign: 'center' }}>
                <Title level={3} style={{ margin: 0, color: '#52c41a' }}>
                  {statistics.total_entities}
                </Title>
                <Text type="secondary">总实体数</Text>
              </div>
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <div style={{ textAlign: 'center' }}>
                <Title level={3} style={{ margin: 0, color: '#fa8c16' }}>
                  {statistics.total_relations}
                </Title>
                <Text type="secondary">总关系数</Text>
              </div>
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <div style={{ textAlign: 'center' }}>
                <Title level={3} style={{ margin: 0, color: '#722ed1' }}>
                  {statistics.unique_tags}
                </Title>
                <Text type="secondary">标签数</Text>
              </div>
            </Card>
          </Col>
        </Row>
      )}

      {/* 主要内容卡片 */}
      <Card>
        <div style={{ marginBottom: 16 }}>
          <Row justify="space-between" align="middle">
            <Col>
              <Title level={4} style={{ margin: 0 }}>
                知识本体管理
              </Title>
            </Col>
            <Col>
              <Space>
                <Button
                  type="primary"
                  icon={<PlusOutlined />}
                  onClick={() => setCreateModalVisible(true)}
                >
                  创建本体
                </Button>
                <Button
                  icon={<UploadOutlined />}
                  onClick={() => setImportModalVisible(true)}
                >
                  导入本体
                </Button>
                <Button
                  icon={<ReloadOutlined />}
                  onClick={() => {
                    loadOntologies();
                    loadStatistics();
                  }}
                >
                  刷新
                </Button>
              </Space>
            </Col>
          </Row>
        </div>

        {/* 搜索和过滤 */}
        <Row gutter={16} style={{ marginBottom: 16 }}>
          <Col span={8}>
            <Input
              placeholder="搜索本体名称或描述"
              prefix={<SearchOutlined />}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onPressEnter={handleSearch}
            />
          </Col>
          <Col span={8}>
            <Select
              mode="multiple"
              placeholder="选择标签过滤"
              value={selectedTags}
              onChange={setSelectedTags}
              style={{ width: '100%' }}
            >
              {availableTags.map((tag) => (
                <Option key={tag} value={tag}>
                  {tag}
                </Option>
              ))}
            </Select>
          </Col>
          <Col span={8}>
            <Space>
              <Button type="primary" icon={<SearchOutlined />} onClick={handleSearch}>
                搜索
              </Button>
              <Button onClick={handleResetSearch}>
                重置
              </Button>
            </Space>
          </Col>
        </Row>

        {/* 本体列表表格 */}
        <Table
          columns={columns}
          dataSource={ontologies}
          rowKey="id"
          loading={loading}
          pagination={false}
          locale={{
            emptyText: (
              <Empty
                description="暂无本体数据"
                image={Empty.PRESENTED_IMAGE_SIMPLE}
              />
            ),
          }}
        />

        {/* 分页 */}
        <div style={{ marginTop: 16, textAlign: 'right' }}>
          <Pagination
            current={currentPage}
            pageSize={pageSize}
            total={total}
            showSizeChanger
            showQuickJumper
            showTotal={(total, range) =>
              `第 ${range[0]}-${range[1]} 条，共 ${total} 条`
            }
            onChange={(page, size) => {
              setCurrentPage(page);
              setPageSize(size || 10);
            }}
          />
        </div>
      </Card>

      {/* 创建本体模态框 */}
      <Modal
        title="创建知识本体"
        open={createModalVisible}
        onCancel={() => {
          setCreateModalVisible(false);
          createForm.resetFields();
        }}
        footer={null}
        width={600}
      >
        <Form
          form={createForm}
          layout="vertical"
          onFinish={handleCreateOntology}
        >
          <Form.Item
            name="name"
            label="本体名称"
            rules={[{ required: true, message: '请输入本体名称' }]}
          >
            <Input placeholder="请输入本体名称" />
          </Form.Item>
          
          <Form.Item
            name="description"
            label="本体描述"
          >
            <TextArea
              rows={3}
              placeholder="请输入本体描述"
            />
          </Form.Item>
          
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="version"
                label="版本号"
                initialValue="1.0.0"
                rules={[{ required: true, message: '请输入版本号' }]}
              >
                <Input placeholder="请输入版本号" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="author"
                label="作者"
              >
                <Input placeholder="请输入作者" />
              </Form.Item>
            </Col>
          </Row>
          
          <Form.Item
            name="namespace"
            label="命名空间"
          >
            <Input placeholder="请输入命名空间" />
          </Form.Item>
          
          <Form.Item
            name="tags"
            label="标签"
          >
            <Select
              mode="tags"
              placeholder="请输入或选择标签"
              style={{ width: '100%' }}
            >
              {availableTags.map((tag) => (
                <Option key={tag} value={tag}>
                  {tag}
                </Option>
              ))}
            </Select>
          </Form.Item>
          
          <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
            <Space>
              <Button
                onClick={() => {
                  setCreateModalVisible(false);
                  createForm.resetFields();
                }}
              >
                取消
              </Button>
              <Button type="primary" htmlType="submit">
                创建
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 编辑本体模态框 */}
      <Modal
        title="编辑知识本体"
        open={editModalVisible}
        onCancel={() => {
          setEditModalVisible(false);
          editForm.resetFields();
          setEditingOntology(null);
        }}
        footer={null}
        width={600}
      >
        <Form
          form={editForm}
          layout="vertical"
          onFinish={handleUpdateOntology}
        >
          <Form.Item
            name="name"
            label="本体名称"
            rules={[{ required: true, message: '请输入本体名称' }]}
          >
            <Input placeholder="请输入本体名称" />
          </Form.Item>
          
          <Form.Item
            name="description"
            label="本体描述"
          >
            <TextArea
              rows={3}
              placeholder="请输入本体描述"
            />
          </Form.Item>
          
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="version"
                label="版本号"
                rules={[{ required: true, message: '请输入版本号' }]}
              >
                <Input placeholder="请输入版本号" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="author"
                label="作者"
              >
                <Input placeholder="请输入作者" />
              </Form.Item>
            </Col>
          </Row>
          
          <Form.Item
            name="tags"
            label="标签"
          >
            <Select
              mode="tags"
              placeholder="请输入或选择标签"
              style={{ width: '100%' }}
            >
              {availableTags.map((tag) => (
                <Option key={tag} value={tag}>
                  {tag}
                </Option>
              ))}
            </Select>
          </Form.Item>
          
          <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
            <Space>
              <Button
                onClick={() => {
                  setEditModalVisible(false);
                  editForm.resetFields();
                  setEditingOntology(null);
                }}
              >
                取消
              </Button>
              <Button type="primary" htmlType="submit">
                更新
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 导入本体模态框 */}
      <Modal
        title="导入知识本体"
        open={importModalVisible}
        onCancel={() => {
          setImportModalVisible(false);
          importForm.resetFields();
        }}
        footer={null}
        width={500}
      >
        <Form
          form={importForm}
          layout="vertical"
          onFinish={handleImportOntology}
        >
          <Form.Item
            name="format"
            label="文件格式"
            initialValue="json"
            rules={[{ required: true, message: '请选择文件格式' }]}
          >
            <Select>
              <Option value="json">JSON</Option>
              <Option value="owl">OWL</Option>
              <Option value="rdf">RDF</Option>
            </Select>
          </Form.Item>
          
          <Form.Item
            name="file"
            label="选择文件"
            rules={[{ required: true, message: '请选择要导入的文件' }]}
          >
            <Upload
              beforeUpload={() => false}
              maxCount={1}
              accept=".json,.owl,.rdf"
            >
              <Button icon={<UploadOutlined />}>选择文件</Button>
            </Upload>
          </Form.Item>
          
          <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
            <Space>
              <Button
                onClick={() => {
                  setImportModalVisible(false);
                  importForm.resetFields();
                }}
              >
                取消
              </Button>
              <Button type="primary" htmlType="submit">
                导入
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 本体详情模态框 */}
      <Modal
        title={`本体详情 - ${selectedOntology?.name}`}
        open={detailModalVisible}
        onCancel={() => {
          setDetailModalVisible(false);
          setSelectedOntology(null);
          setOntologyDetail(null);
        }}
        footer={[
          <Button
            key="close"
            onClick={() => {
              setDetailModalVisible(false);
              setSelectedOntology(null);
              setOntologyDetail(null);
            }}
          >
            关闭
          </Button>,
        ]}
        width={1200}
      >
        {ontologyDetail ? (
          <div>
            {/* 使用标签页展示不同视图 */}
            <div>
              <div style={{ marginBottom: 16 }}>
                <Space>
                  <Button
                    type="primary"
                    onClick={() => {
                      // 切换到基本信息视图
                    }}
                  >
                    基本信息
                  </Button>
                  <Button
                    onClick={() => {
                      // 切换到可视化视图
                    }}
                  >
                    结构可视化
                  </Button>
                </Space>
              </div>
              
              {/* 基本信息 */}
              <div>
                <Divider orientation="left">基本信息</Divider>
                <Row gutter={16}>
                  <Col span={12}>
                    <Text strong>名称：</Text>
                    <Text>{ontologyDetail.name}</Text>
                  </Col>
                  <Col span={12}>
                    <Text strong>版本：</Text>
                    <Text>{ontologyDetail.version}</Text>
                  </Col>
                </Row>
                <Row gutter={16} style={{ marginTop: 8 }}>
                  <Col span={12}>
                    <Text strong>作者：</Text>
                    <Text>{ontologyDetail.author || '-'}</Text>
                  </Col>
                  <Col span={12}>
                    <Text strong>命名空间：</Text>
                    <Text>{ontologyDetail.namespace || '-'}</Text>
                  </Col>
                </Row>
                <Row style={{ marginTop: 8 }}>
                  <Col span={24}>
                    <Text strong>描述：</Text>
                    <br />
                    <Text>{ontologyDetail.description || '-'}</Text>
                  </Col>
                </Row>
                <Row style={{ marginTop: 8 }}>
                  <Col span={24}>
                    <Text strong>标签：</Text>
                    <br />
                    <Space wrap>
                      {ontologyDetail.tags?.map((tag: string) => (
                        <Tag key={tag} color="blue">
                          {tag}
                        </Tag>
                      ))}
                    </Space>
                  </Col>
                </Row>
                
                <Divider orientation="left">统计信息</Divider>
                <Row gutter={16}>
                  <Col span={8}>
                    <div style={{ textAlign: 'center' }}>
                      <Title level={4} style={{ margin: 0, color: '#52c41a' }}>
                        {ontologyDetail.entity_types?.length || 0}
                      </Title>
                      <Text type="secondary">实体类型</Text>
                    </div>
                  </Col>
                  <Col span={8}>
                    <div style={{ textAlign: 'center' }}>
                      <Title level={4} style={{ margin: 0, color: '#fa8c16' }}>
                        {ontologyDetail.relation_types?.length || 0}
                      </Title>
                      <Text type="secondary">关系类型</Text>
                    </div>
                  </Col>
                  <Col span={8}>
                    <div style={{ textAlign: 'center' }}>
                      <Title level={4} style={{ margin: 0, color: '#1890ff' }}>
                        {new Date(ontologyDetail.created_at).toLocaleDateString()}
                      </Title>
                      <Text type="secondary">创建时间</Text>
                    </div>
                  </Col>
                </Row>
                
                <Divider orientation="left">结构可视化</Divider>
                <div style={{ height: '400px' }}>
                  <OntologyVisualization
                    ontologyData={ontologyDetail}
                    onNodeClick={(node) => {
                      console.log('点击节点:', node);
                    }}
                  />
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            <Spin size="large" />
          </div>
        )}
      </Modal>

      {/* 本体结构编辑器抽屉 */}
      <Drawer
        title={`编辑本体结构 - ${selectedOntology?.name}`}
        placement="right"
        size="large"
        open={editorDrawerVisible}
        onClose={() => {
          setEditorDrawerVisible(false);
          setSelectedOntology(null);
        }}
        extra={
          <Button
            type="primary"
            onClick={() => {
              message.success('本体结构保存成功');
              loadOntologies();
            }}
          >
            保存
          </Button>
        }
      >
        {selectedOntology && (
          <OntologyEditor
            ontologyId={selectedOntology.id}
            ontologyData={ontologyDetail}
            onSave={(data) => {
              // 这里可以调用API保存本体结构
              console.log('保存本体结构:', data);
            }}
          />
        )}
      </Drawer>
    </div>
  );
};

export default OntologyManagement;