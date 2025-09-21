/**
 * 本体管理页面
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
  Tabs,
  Upload,
  Progress,
  Tooltip,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  UploadOutlined,
  DownloadOutlined,
  EyeOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import type { TabsProps } from 'antd';
import { ontologyService } from '../services';
import {
  Ontology,
  OntologyClass,
  OntologyProperty,
  OntologyRelation,
  OntologyInstance,
  OntologyFormat,
} from '../types';

const { Title } = Typography;
const { TextArea } = Input;

/**
 * 本体管理页面组件
 */
const OntologyPage: React.FC = () => {
  // 状态管理
  const [loading, setLoading] = useState<boolean>(false);
  const [ontologies, setOntologies] = useState<Ontology[]>([]);
  const [selectedOntology, setSelectedOntology] = useState<Ontology | null>(null);
  const [classes, setClasses] = useState<OntologyClass[]>([]);
  const [properties, setProperties] = useState<OntologyProperty[]>([]);
  const [relations, setRelations] = useState<OntologyRelation[]>([]);
  const [instances, setInstances] = useState<OntologyInstance[]>([]);
  
  // 模态框状态
  const [ontologyModalVisible, setOntologyModalVisible] = useState<boolean>(false);
  const [importModalVisible, setImportModalVisible] = useState<boolean>(false);
  
  // 编辑状态
  const [editingOntology, setEditingOntology] = useState<Ontology | null>(null);
  
  // 表单实例
  const [ontologyForm] = Form.useForm();
  
  // 上传进度
  const [uploadProgress, setUploadProgress] = useState<number>(0);

  /**
   * 加载本体列表
   */
  const loadOntologies = useCallback(async () => {
    setLoading(true);
    try {
      const response = await ontologyService.getOntologies();
      if (response.success && response.data) {
        setOntologies(response.data);
      } else {
        message.error(response.error || '加载本体列表失败');
      }
    } catch (error) {
      message.error('加载本体列表时发生错误');
      console.error('Load ontologies error:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * 加载本体详情
   */
  const loadOntologyDetails = useCallback(async (ontologyId: string) => {
    setLoading(true);
    try {
      const [classesRes, propertiesRes, relationsRes, instancesRes] = await Promise.all([
        ontologyService.getClasses(ontologyId),
        ontologyService.getProperties(ontologyId),
        ontologyService.getRelations(ontologyId),
        ontologyService.getInstances(ontologyId),
      ]);
      
      if (classesRes.success) setClasses(classesRes.data || []);
      if (propertiesRes.success) setProperties(propertiesRes.data || []);
      if (relationsRes.success) setRelations(relationsRes.data || []);
      if (instancesRes.success) setInstances(instancesRes.data || []);
    } catch (error) {
      message.error('加载本体详情时发生错误');
      console.error('Load ontology details error:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * 创建/更新本体
   */
  const handleOntologySubmit = async (values: any) => {
    try {
      let response;
      if (editingOntology) {
        response = await ontologyService.updateOntology(editingOntology.id, values);
      } else {
        response = await ontologyService.createOntology(values);
      }
      
      if (response.success) {
        message.success(editingOntology ? '本体更新成功' : '本体创建成功');
        setOntologyModalVisible(false);
        ontologyForm.resetFields();
        setEditingOntology(null);
        loadOntologies();
      } else {
        message.error(response.error || '操作失败');
      }
    } catch (error) {
      message.error('操作时发生错误');
      console.error('Ontology submit error:', error);
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
  const handleExportOntology = async (ontologyId: string, format: OntologyFormat = OntologyFormat.JSON) => {
    try {
      const response = await ontologyService.exportOntology(ontologyId, format);
      if (response.success && response.data) {
        const url = URL.createObjectURL(response.data);
        const link = document.createElement('a');
        link.href = url;
        link.download = `ontology_${ontologyId}.${format.toLowerCase()}`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        message.success('本体导出成功');
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
  const handleImportOntology = async (file: File, format: OntologyFormat) => {
    try {
      const response = await ontologyService.importOntology(
        file,
        format,
        (progress) => setUploadProgress(progress)
      );
      
      if (response.success) {
        message.success('本体导入成功');
        setImportModalVisible(false);
        setUploadProgress(0);
        loadOntologies();
      } else {
        message.error(response.error || '导入失败');
      }
    } catch (error) {
      message.error('导入时发生错误');
      console.error('Import ontology error:', error);
    }
  };

  // 本体表格列定义
  const ontologyColumns: ColumnsType<Ontology> = [
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
      render: (text, record) => (
        <Button
          type="link"
          onClick={() => {
            setSelectedOntology(record);
            loadOntologyDetails(record.id);
          }}
        >
          {text}
        </Button>
      ),
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: '版本',
      dataIndex: 'version',
      key: 'version',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status) => (
        <Tag color={status === 'active' ? 'green' : 'orange'}>
          {status === 'active' ? '活跃' : '草稿'}
        </Tag>
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date) => new Date(date).toLocaleString(),
    },
    {
      title: '操作',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Tooltip title="查看">
            <Button
              icon={<EyeOutlined />}
              size="small"
              onClick={() => {
                setSelectedOntology(record);
                loadOntologyDetails(record.id);
              }}
            />
          </Tooltip>
          <Tooltip title="编辑">
            <Button
              icon={<EditOutlined />}
              size="small"
              onClick={() => {
                setEditingOntology(record);
                ontologyForm.setFieldsValue(record);
                setOntologyModalVisible(true);
              }}
            />
          </Tooltip>
          <Tooltip title="导出">
            <Button
              icon={<DownloadOutlined />}
              size="small"
              onClick={() => handleExportOntology(record.id)}
            />
          </Tooltip>
          <Popconfirm
            title="确定要删除这个本体吗？"
            onConfirm={() => handleDeleteOntology(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Tooltip title="删除">
              <Button
                icon={<DeleteOutlined />}
                size="small"
                danger
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
  }, [loadOntologies]);

  // 标签页配置
  const tabItems: TabsProps['items'] = [
    {
      key: 'classes',
      label: `类 (${classes.length})`,
      children: (
        <Table
          columns={[
            { title: '名称', dataIndex: 'name', key: 'name' },
            { title: '标签', dataIndex: 'label', key: 'label' },
            { title: '描述', dataIndex: 'description', key: 'description', ellipsis: true },
          ]}
          dataSource={classes}
          rowKey="id"
          loading={loading}
          size="small"
        />
      ),
    },
    {
      key: 'properties',
      label: `属性 (${properties.length})`,
      children: (
        <Table
          columns={[
            { title: '名称', dataIndex: 'name', key: 'name' },
            { title: '标签', dataIndex: 'label', key: 'label' },
            { title: '类型', dataIndex: 'type', key: 'type' },
          ]}
          dataSource={properties}
          rowKey="id"
          loading={loading}
          size="small"
        />
      ),
    },
    {
      key: 'relations',
      label: `关系 (${relations.length})`,
      children: (
        <Table
          columns={[
            { title: '名称', dataIndex: 'name', key: 'name' },
            { title: '标签', dataIndex: 'label', key: 'label' },
            { title: '源类', dataIndex: 'source_class', key: 'source_class' },
            { title: '目标类', dataIndex: 'target_class', key: 'target_class' },
          ]}
          dataSource={relations}
          rowKey="id"
          loading={loading}
          size="small"
        />
      ),
    },
    {
      key: 'instances',
      label: `实例 (${instances.length})`,
      children: (
        <Table
          columns={[
            { title: '名称', dataIndex: 'name', key: 'name' },
            { title: '标签', dataIndex: 'label', key: 'label' },
            { title: '类型', dataIndex: 'class_name', key: 'class_name' },
          ]}
          dataSource={instances}
          rowKey="id"
          loading={loading}
          size="small"
        />
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
                本体管理
              </Title>
              <Space>
                <Button
                  icon={<UploadOutlined />}
                  onClick={() => setImportModalVisible(true)}
                >
                  导入本体
                </Button>
                <Button
                  type="primary"
                  icon={<PlusOutlined />}
                  onClick={() => {
                    setEditingOntology(null);
                    ontologyForm.resetFields();
                    setOntologyModalVisible(true);
                  }}
                >
                  创建本体
                </Button>
              </Space>
            </div>
            
            <Table
              columns={ontologyColumns}
              dataSource={ontologies}
              rowKey="id"
              loading={loading}
              pagination={{ pageSize: 10 }}
            />
          </Card>
        </Col>
      </Row>

      {selectedOntology && (
        <Row gutter={[24, 24]} style={{ marginTop: 24 }}>
          <Col span={24}>
            <Card title={`本体详情: ${selectedOntology.name}`}>
              <Tabs items={tabItems} />
            </Card>
          </Col>
        </Row>
      )}

      {/* 本体创建/编辑模态框 */}
      <Modal
        title={editingOntology ? '编辑本体' : '创建本体'}
        open={ontologyModalVisible}
        onCancel={() => {
          setOntologyModalVisible(false);
          setEditingOntology(null);
          ontologyForm.resetFields();
        }}
        footer={null}
        width={600}
      >
        <Form
          form={ontologyForm}
          layout="vertical"
          onFinish={handleOntologySubmit}
        >
          <Form.Item
            name="name"
            label="名称"
            rules={[{ required: true, message: '请输入本体名称' }]}
          >
            <Input placeholder="输入本体名称" />
          </Form.Item>
          
          <Form.Item
            name="description"
            label="描述"
          >
            <TextArea rows={3} placeholder="输入本体描述" />
          </Form.Item>
          
          <Form.Item
            name="version"
            label="版本"
            rules={[{ required: true, message: '请输入版本号' }]}
          >
            <Input placeholder="如: 1.0.0" />
          </Form.Item>
          
          <Form.Item
            name="namespace"
            label="命名空间"
          >
            <Input placeholder="输入命名空间URI" />
          </Form.Item>
          
          <Form.Item>
            <Space>
              <Button onClick={() => setOntologyModalVisible(false)}>
                取消
              </Button>
              <Button type="primary" htmlType="submit">
                {editingOntology ? '更新' : '创建'}
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 导入本体模态框 */}
      <Modal
        title="导入本体"
        open={importModalVisible}
        onCancel={() => {
          setImportModalVisible(false);
          setUploadProgress(0);
        }}
        footer={null}
        width={500}
      >
        <div>
          <Upload.Dragger
            name="file"
            multiple={false}
            accept=".json,.owl,.rdf,.ttl"
            customRequest={({ file }) => {
              const format = (file as File).name.endsWith('.json') 
                ? OntologyFormat.JSON 
                : OntologyFormat.OWL;
              handleImportOntology(file as File, format);
            }}
            showUploadList={false}
          >
            <p className="ant-upload-drag-icon">
              <UploadOutlined style={{ fontSize: 48, color: '#1890ff' }} />
            </p>
            <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
            <p className="ant-upload-hint">
              支持 JSON、OWL、RDF、TTL 格式
            </p>
          </Upload.Dragger>
          
          {uploadProgress > 0 && (
            <div style={{ marginTop: 16 }}>
              <Progress percent={uploadProgress} status="active" />
            </div>
          )}
        </div>
      </Modal>
    </div>
  );
};

export default OntologyPage;