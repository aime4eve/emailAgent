/**
 * 可视化本体编辑器组件
 * 提供实体类型和关系类型的可视化编辑功能
 */

import React, { useState, useEffect } from 'react';
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
  Select,
  Divider,
  Tooltip,
  Badge,
  Tabs,
  Switch,
  Collapse,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  NodeIndexOutlined,
  ApartmentOutlined,
  SettingOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import type { TabsProps } from 'antd';

const { Title, Text } = Typography;
const { TextArea } = Input;
const { Option } = Select;
const { Panel } = Collapse;

/**
 * 数据类型枚举
 */
enum DataType {
  STRING = 'string',
  INTEGER = 'integer',
  FLOAT = 'float',
  BOOLEAN = 'boolean',
  DATE = 'date',
  DATETIME = 'datetime',
  URI = 'uri',
}

/**
 * 属性接口
 */
interface Property {
  name: string;
  data_type: DataType;
  description: string;
  required: boolean;
  default_value?: any;
  constraints?: Record<string, any>;
}

/**
 * 实体类型接口
 */
interface EntityType {
  id: string;
  name: string;
  description: string;
  properties: Property[];
  parent_types: string[];
  created_at?: string;
  updated_at?: string;
}

/**
 * 关系类型接口
 */
interface RelationType {
  id: string;
  name: string;
  description: string;
  domain_types: string[];
  range_types: string[];
  properties: Property[];
  symmetric: boolean;
  transitive: boolean;
  functional: boolean;
  created_at?: string;
  updated_at?: string;
}

/**
 * 本体编辑器组件属性
 */
interface OntologyEditorProps {
  ontologyId: string;
  ontologyData?: any;
  onSave?: (data: any) => void;
  className?: string;
}

/**
 * 本体编辑器组件
 */
const OntologyEditor: React.FC<OntologyEditorProps> = ({
  ontologyData,
  onSave,
  className,
}) => {
  // 状态管理
  const [loading] = useState<boolean>(false);
  const [entityTypes, setEntityTypes] = useState<EntityType[]>([]);
  const [relationTypes, setRelationTypes] = useState<RelationType[]>([]);
  
  // 模态框状态
  const [entityModalVisible, setEntityModalVisible] = useState<boolean>(false);
  const [relationModalVisible, setRelationModalVisible] = useState<boolean>(false);
  const [propertyModalVisible, setPropertyModalVisible] = useState<boolean>(false);
  
  // 编辑状态
  const [editingEntity, setEditingEntity] = useState<EntityType | null>(null);
  const [editingRelation, setRelationRelation] = useState<RelationType | null>(null);
  const [currentEditTarget, setCurrentEditTarget] = useState<'entity' | 'relation' | null>(null);
  const [currentEditTargetId, setCurrentEditTargetId] = useState<string | null>(null);
  
  // 表单实例
  const [entityForm] = Form.useForm();
  const [relationForm] = Form.useForm();
  const [propertyForm] = Form.useForm();

  /**
   * 初始化数据
   */
  useEffect(() => {
    if (ontologyData) {
      setEntityTypes(ontologyData.entity_types || []);
      setRelationTypes(ontologyData.relation_types || []);
    }
  }, [ontologyData]);

  /**
   * 添加实体类型
   */
  const handleAddEntityType = async (values: any) => {
    try {
      const newEntityType: EntityType = {
        id: `entity_${Date.now()}`,
        name: values.name,
        description: values.description || '',
        properties: [],
        parent_types: values.parent_types || [],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      
      const updatedEntityTypes = [...entityTypes, newEntityType];
      setEntityTypes(updatedEntityTypes);
      
      message.success('实体类型添加成功');
      setEntityModalVisible(false);
      entityForm.resetFields();
      
      // 触发保存回调
      if (onSave) {
        onSave({
          ...ontologyData,
          entity_types: updatedEntityTypes,
          relation_types: relationTypes,
        });
      }
    } catch (error) {
      message.error('添加实体类型失败');
      console.error('Add entity type error:', error);
    }
  };

  /**
   * 更新实体类型
   */
  const handleUpdateEntityType = async (values: any) => {
    if (!editingEntity) return;
    
    try {
      const updatedEntityType: EntityType = {
        ...editingEntity,
        name: values.name,
        description: values.description || '',
        parent_types: values.parent_types || [],
        updated_at: new Date().toISOString(),
      };
      
      const updatedEntityTypes = entityTypes.map(et => 
        et.id === editingEntity.id ? updatedEntityType : et
      );
      setEntityTypes(updatedEntityTypes);
      
      message.success('实体类型更新成功');
      setEntityModalVisible(false);
      entityForm.resetFields();
      setEditingEntity(null);
      
      // 触发保存回调
      if (onSave) {
        onSave({
          ...ontologyData,
          entity_types: updatedEntityTypes,
          relation_types: relationTypes,
        });
      }
    } catch (error) {
      message.error('更新实体类型失败');
      console.error('Update entity type error:', error);
    }
  };

  /**
   * 删除实体类型
   */
  const handleDeleteEntityType = (entityId: string) => {
    const updatedEntityTypes = entityTypes.filter(et => et.id !== entityId);
    setEntityTypes(updatedEntityTypes);
    
    message.success('实体类型删除成功');
    
    // 触发保存回调
    if (onSave) {
      onSave({
        ...ontologyData,
        entity_types: updatedEntityTypes,
        relation_types: relationTypes,
      });
    }
  };

  /**
   * 添加关系类型
   */
  const handleAddRelationType = async (values: any) => {
    try {
      const newRelationType: RelationType = {
        id: `relation_${Date.now()}`,
        name: values.name,
        description: values.description || '',
        domain_types: values.domain_types || [],
        range_types: values.range_types || [],
        properties: [],
        symmetric: values.symmetric || false,
        transitive: values.transitive || false,
        functional: values.functional || false,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      
      const updatedRelationTypes = [...relationTypes, newRelationType];
      setRelationTypes(updatedRelationTypes);
      
      message.success('关系类型添加成功');
      setRelationModalVisible(false);
      relationForm.resetFields();
      
      // 触发保存回调
      if (onSave) {
        onSave({
          ...ontologyData,
          entity_types: entityTypes,
          relation_types: updatedRelationTypes,
        });
      }
    } catch (error) {
      message.error('添加关系类型失败');
      console.error('Add relation type error:', error);
    }
  };

  /**
   * 更新关系类型
   */
  const handleUpdateRelationType = async (values: any) => {
    if (!editingRelation) return;
    
    try {
      const updatedRelationType: RelationType = {
        ...editingRelation,
        name: values.name,
        description: values.description || '',
        domain_types: values.domain_types || [],
        range_types: values.range_types || [],
        symmetric: values.symmetric || false,
        transitive: values.transitive || false,
        functional: values.functional || false,
        updated_at: new Date().toISOString(),
      };
      
      const updatedRelationTypes = relationTypes.map(rt => 
        rt.id === editingRelation.id ? updatedRelationType : rt
      );
      setRelationTypes(updatedRelationTypes);
      
      message.success('关系类型更新成功');
      setRelationModalVisible(false);
      relationForm.resetFields();
      setRelationRelation(null);
      
      // 触发保存回调
      if (onSave) {
        onSave({
          ...ontologyData,
          entity_types: entityTypes,
          relation_types: updatedRelationTypes,
        });
      }
    } catch (error) {
      message.error('更新关系类型失败');
      console.error('Update relation type error:', error);
    }
  };

  /**
   * 删除关系类型
   */
  const handleDeleteRelationType = (relationId: string) => {
    const updatedRelationTypes = relationTypes.filter(rt => rt.id !== relationId);
    setRelationTypes(updatedRelationTypes);
    
    message.success('关系类型删除成功');
    
    // 触发保存回调
    if (onSave) {
      onSave({
        ...ontologyData,
        entity_types: entityTypes,
        relation_types: updatedRelationTypes,
      });
    }
  };

  /**
   * 添加属性
   */
  const handleAddProperty = async (values: any) => {
    if (!currentEditTarget || !currentEditTargetId) return;
    
    try {
      const newProperty: Property = {
        name: values.name,
        data_type: values.data_type,
        description: values.description || '',
        required: values.required || false,
        default_value: values.default_value,
        constraints: values.constraints ? JSON.parse(values.constraints) : undefined,
      };
      
      if (currentEditTarget === 'entity') {
        const updatedEntityTypes = entityTypes.map(et => {
          if (et.id === currentEditTargetId) {
            return {
              ...et,
              properties: [...et.properties, newProperty],
              updated_at: new Date().toISOString(),
            };
          }
          return et;
        });
        setEntityTypes(updatedEntityTypes);
        
        // 触发保存回调
        if (onSave) {
          onSave({
            ...ontologyData,
            entity_types: updatedEntityTypes,
            relation_types: relationTypes,
          });
        }
      } else if (currentEditTarget === 'relation') {
        const updatedRelationTypes = relationTypes.map(rt => {
          if (rt.id === currentEditTargetId) {
            return {
              ...rt,
              properties: [...rt.properties, newProperty],
              updated_at: new Date().toISOString(),
            };
          }
          return rt;
        });
        setRelationTypes(updatedRelationTypes);
        
        // 触发保存回调
        if (onSave) {
          onSave({
            ...ontologyData,
            entity_types: entityTypes,
            relation_types: updatedRelationTypes,
          });
        }
      }
      
      message.success('属性添加成功');
      setPropertyModalVisible(false);
      propertyForm.resetFields();
      setCurrentEditTarget(null);
      setCurrentEditTargetId(null);
    } catch (error) {
      message.error('添加属性失败');
      console.error('Add property error:', error);
    }
  };

  /**
   * 删除属性
   */
  const handleDeleteProperty = (targetType: 'entity' | 'relation', targetId: string, propertyName: string) => {
    if (targetType === 'entity') {
      const updatedEntityTypes = entityTypes.map(et => {
        if (et.id === targetId) {
          return {
            ...et,
            properties: et.properties.filter(p => p.name !== propertyName),
            updated_at: new Date().toISOString(),
          };
        }
        return et;
      });
      setEntityTypes(updatedEntityTypes);
      
      // 触发保存回调
      if (onSave) {
        onSave({
          ...ontologyData,
          entity_types: updatedEntityTypes,
          relation_types: relationTypes,
        });
      }
    } else if (targetType === 'relation') {
      const updatedRelationTypes = relationTypes.map(rt => {
        if (rt.id === targetId) {
          return {
            ...rt,
            properties: rt.properties.filter(p => p.name !== propertyName),
            updated_at: new Date().toISOString(),
          };
        }
        return rt;
      });
      setRelationTypes(updatedRelationTypes);
      
      // 触发保存回调
      if (onSave) {
        onSave({
          ...ontologyData,
          entity_types: entityTypes,
          relation_types: updatedRelationTypes,
        });
      }
    }
    
    message.success('属性删除成功');
  };

  /**
   * 打开编辑实体模态框
   */
  const openEditEntityModal = (entity?: EntityType) => {
    if (entity) {
      setEditingEntity(entity);
      entityForm.setFieldsValue({
        name: entity.name,
        description: entity.description,
        parent_types: entity.parent_types,
      });
    } else {
      setEditingEntity(null);
      entityForm.resetFields();
    }
    setEntityModalVisible(true);
  };

  /**
   * 打开编辑关系模态框
   */
  const openEditRelationModal = (relation?: RelationType) => {
    if (relation) {
      setRelationRelation(relation);
      relationForm.setFieldsValue({
        name: relation.name,
        description: relation.description,
        domain_types: relation.domain_types,
        range_types: relation.range_types,
        symmetric: relation.symmetric,
        transitive: relation.transitive,
        functional: relation.functional,
      });
    } else {
      setRelationRelation(null);
      relationForm.resetFields();
    }
    setRelationModalVisible(true);
  };

  /**
   * 打开添加属性模态框
   */
  const openAddPropertyModal = (targetType: 'entity' | 'relation', targetId: string) => {
    setCurrentEditTarget(targetType);
    setCurrentEditTargetId(targetId);
    // setEditingProperty(null);
    propertyForm.resetFields();
    setPropertyModalVisible(true);
  };

  // 实体类型表格列定义
  const entityColumns: ColumnsType<EntityType> = [
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
      render: (text: string) => (
        <Space>
          <NodeIndexOutlined style={{ color: '#1890ff' }} />
          <Text strong>{text}</Text>
        </Space>
      ),
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: '属性数量',
      key: 'property_count',
      width: 100,
      render: (_, record: EntityType) => (
        <Badge count={record.properties.length} color="blue" />
      ),
    },
    {
      title: '父类型',
      dataIndex: 'parent_types',
      key: 'parent_types',
      width: 150,
      render: (parentTypes: string[]) => (
        <Space wrap>
          {parentTypes.map((parentId) => {
            const parentEntity = entityTypes.find(et => et.id === parentId);
            return (
              <Tag key={parentId} color="green">
                {parentEntity?.name || parentId}
              </Tag>
            );
          })}
        </Space>
      ),
    },
    {
      title: '操作',
      key: 'actions',
      width: 200,
      render: (_, record: EntityType) => (
        <Space>
          <Tooltip title="编辑">
            <Button
              type="text"
              icon={<EditOutlined />}
              onClick={() => openEditEntityModal(record)}
            />
          </Tooltip>
          <Tooltip title="添加属性">
            <Button
              type="text"
              icon={<PlusOutlined />}
              onClick={() => openAddPropertyModal('entity', record.id)}
            />
          </Tooltip>
          <Popconfirm
            title="确定要删除这个实体类型吗？"
            description="删除后无法恢复，请谨慎操作。"
            onConfirm={() => handleDeleteEntityType(record.id)}
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

  // 关系类型表格列定义
  const relationColumns: ColumnsType<RelationType> = [
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
      render: (text: string) => (
        <Space>
          <ApartmentOutlined style={{ color: '#fa8c16' }} />
          <Text strong>{text}</Text>
        </Space>
      ),
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: '定义域',
      dataIndex: 'domain_types',
      key: 'domain_types',
      width: 150,
      render: (domainTypes: string[]) => (
        <Space wrap>
          {domainTypes.map((domainId) => {
            const domainEntity = entityTypes.find(et => et.id === domainId);
            return (
              <Tag key={domainId} color="blue">
                {domainEntity?.name || domainId}
              </Tag>
            );
          })}
        </Space>
      ),
    },
    {
      title: '值域',
      dataIndex: 'range_types',
      key: 'range_types',
      width: 150,
      render: (rangeTypes: string[]) => (
        <Space wrap>
          {rangeTypes.map((rangeId) => {
            const rangeEntity = entityTypes.find(et => et.id === rangeId);
            return (
              <Tag key={rangeId} color="orange">
                {rangeEntity?.name || rangeId}
              </Tag>
            );
          })}
        </Space>
      ),
    },
    {
      title: '特性',
      key: 'characteristics',
      width: 120,
      render: (_, record: RelationType) => (
        <Space wrap>
          {record.symmetric && <Tag color="green">对称</Tag>}
          {record.transitive && <Tag color="blue">传递</Tag>}
          {record.functional && <Tag color="purple">函数</Tag>}
        </Space>
      ),
    },
    {
      title: '操作',
      key: 'actions',
      width: 200,
      render: (_, record: RelationType) => (
        <Space>
          <Tooltip title="编辑">
            <Button
              type="text"
              icon={<EditOutlined />}
              onClick={() => openEditRelationModal(record)}
            />
          </Tooltip>
          <Tooltip title="添加属性">
            <Button
              type="text"
              icon={<PlusOutlined />}
              onClick={() => openAddPropertyModal('relation', record.id)}
            />
          </Tooltip>
          <Popconfirm
            title="确定要删除这个关系类型吗？"
            description="删除后无法恢复，请谨慎操作。"
            onConfirm={() => handleDeleteRelationType(record.id)}
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

  // 标签页配置
  const tabItems: TabsProps['items'] = [
    {
      key: 'entities',
      label: (
        <Space>
          <NodeIndexOutlined />
          实体类型
          <Badge count={entityTypes.length} color="blue" />
        </Space>
      ),
      children: (
        <div>
          <div style={{ marginBottom: 16 }}>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => openEditEntityModal()}
            >
              添加实体类型
            </Button>
          </div>
          <Table
            columns={entityColumns}
            dataSource={entityTypes}
            rowKey="id"
            loading={loading}
            pagination={false}
            expandable={{
              expandedRowRender: (record: EntityType) => (
                <div style={{ padding: '16px 0' }}>
                  <Title level={5}>属性列表</Title>
                  {record.properties.length > 0 ? (
                    <Collapse size="small">
                      {record.properties.map((property, index) => (
                        <Panel
                          key={index}
                          header={
                            <Space>
                              <Text strong>{property.name}</Text>
                              <Tag color="blue">{property.data_type}</Tag>
                              {property.required && <Tag color="red">必需</Tag>}
                            </Space>
                          }
                          extra={
                            <Popconfirm
                              title="确定要删除这个属性吗？"
                              onConfirm={() => {
                                handleDeleteProperty('entity', record.id, property.name);
                              }}
                            >
                              <Button
                                type="text"
                                danger
                                size="small"
                                icon={<DeleteOutlined />}
                              />
                            </Popconfirm>
                          }
                        >
                          <div>
                            <Text>描述：{property.description || '-'}</Text>
                            <br />
                            <Text>默认值：{property.default_value || '-'}</Text>
                            {property.constraints && (
                              <>
                                <br />
                                <Text>约束：{JSON.stringify(property.constraints)}</Text>
                              </>
                            )}
                          </div>
                        </Panel>
                      ))}
                    </Collapse>
                  ) : (
                    <Text type="secondary">暂无属性</Text>
                  )}
                </div>
              ),
            }}
          />
        </div>
      ),
    },
    {
      key: 'relations',
      label: (
        <Space>
          <ApartmentOutlined />
          关系类型
          <Badge count={relationTypes.length} color="orange" />
        </Space>
      ),
      children: (
        <div>
          <div style={{ marginBottom: 16 }}>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => openEditRelationModal()}
            >
              添加关系类型
            </Button>
          </div>
          <Table
            columns={relationColumns}
            dataSource={relationTypes}
            rowKey="id"
            loading={loading}
            pagination={false}
            expandable={{
              expandedRowRender: (record: RelationType) => (
                <div style={{ padding: '16px 0' }}>
                  <Title level={5}>属性列表</Title>
                  {record.properties.length > 0 ? (
                    <Collapse size="small">
                      {record.properties.map((property, index) => (
                        <Panel
                          key={index}
                          header={
                            <Space>
                              <Text strong>{property.name}</Text>
                              <Tag color="blue">{property.data_type}</Tag>
                              {property.required && <Tag color="red">必需</Tag>}
                            </Space>
                          }
                          extra={
                            <Popconfirm
                              title="确定要删除这个属性吗？"
                              onConfirm={() => {
                                handleDeleteProperty('relation', record.id, property.name);
                              }}
                            >
                              <Button
                                type="text"
                                danger
                                size="small"
                                icon={<DeleteOutlined />}
                              />
                            </Popconfirm>
                          }
                        >
                          <div>
                            <Text>描述：{property.description || '-'}</Text>
                            <br />
                            <Text>默认值：{property.default_value || '-'}</Text>
                            {property.constraints && (
                              <>
                                <br />
                                <Text>约束：{JSON.stringify(property.constraints)}</Text>
                              </>
                            )}
                          </div>
                        </Panel>
                      ))}
                    </Collapse>
                  ) : (
                    <Text type="secondary">暂无属性</Text>
                  )}
                </div>
              ),
            }}
          />
        </div>
      ),
    },
  ];

  return (
    <div className={className}>
      <Card>
        <div style={{ marginBottom: 16 }}>
          <Title level={4} style={{ margin: 0 }}>
            <Space>
              <SettingOutlined />
              本体结构编辑器
            </Space>
          </Title>
        </div>
        
        <Tabs items={tabItems} />
      </Card>

      {/* 实体类型编辑模态框 */}
      <Modal
        title={editingEntity ? '编辑实体类型' : '添加实体类型'}
        open={entityModalVisible}
        onCancel={() => {
          setEntityModalVisible(false);
          entityForm.resetFields();
          setEditingEntity(null);
        }}
        footer={null}
        width={600}
      >
        <Form
          form={entityForm}
          layout="vertical"
          onFinish={editingEntity ? handleUpdateEntityType : handleAddEntityType}
        >
          <Form.Item
            name="name"
            label="实体类型名称"
            rules={[{ required: true, message: '请输入实体类型名称' }]}
          >
            <Input placeholder="请输入实体类型名称" />
          </Form.Item>
          
          <Form.Item
            name="description"
            label="描述"
          >
            <TextArea
              rows={3}
              placeholder="请输入实体类型描述"
            />
          </Form.Item>
          
          <Form.Item
            name="parent_types"
            label="父类型"
          >
            <Select
              mode="multiple"
              placeholder="选择父类型"
              allowClear
            >
              {entityTypes
                .filter(et => !editingEntity || et.id !== editingEntity.id)
                .map((et) => (
                  <Option key={et.id} value={et.id}>
                    {et.name}
                  </Option>
                ))
              }
            </Select>
          </Form.Item>
          
          <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
            <Space>
              <Button
                onClick={() => {
                  setEntityModalVisible(false);
                  entityForm.resetFields();
                  setEditingEntity(null);
                }}
              >
                取消
              </Button>
              <Button type="primary" htmlType="submit">
                {editingEntity ? '更新' : '添加'}
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 关系类型编辑模态框 */}
      <Modal
        title={editingRelation ? '编辑关系类型' : '添加关系类型'}
        open={relationModalVisible}
        onCancel={() => {
          setRelationModalVisible(false);
          relationForm.resetFields();
          setRelationRelation(null);
        }}
        footer={null}
        width={700}
      >
        <Form
          form={relationForm}
          layout="vertical"
          onFinish={editingRelation ? handleUpdateRelationType : handleAddRelationType}
        >
          <Form.Item
            name="name"
            label="关系类型名称"
            rules={[{ required: true, message: '请输入关系类型名称' }]}
          >
            <Input placeholder="请输入关系类型名称" />
          </Form.Item>
          
          <Form.Item
            name="description"
            label="描述"
          >
            <TextArea
              rows={3}
              placeholder="请输入关系类型描述"
            />
          </Form.Item>
          
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="domain_types"
                label="定义域（源实体类型）"
                rules={[{ required: true, message: '请选择定义域' }]}
              >
                <Select
                  mode="multiple"
                  placeholder="选择源实体类型"
                  allowClear
                >
                  {entityTypes.map((et) => (
                    <Option key={et.id} value={et.id}>
                      {et.name}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="range_types"
                label="值域（目标实体类型）"
                rules={[{ required: true, message: '请选择值域' }]}
              >
                <Select
                  mode="multiple"
                  placeholder="选择目标实体类型"
                  allowClear
                >
                  {entityTypes.map((et) => (
                    <Option key={et.id} value={et.id}>
                      {et.name}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>
          
          <Divider>关系特性</Divider>
          
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                name="symmetric"
                label="对称关系"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="transitive"
                label="传递关系"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="functional"
                label="函数关系"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
            </Col>
          </Row>
          
          <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
            <Space>
              <Button
                onClick={() => {
                  setRelationModalVisible(false);
                  relationForm.resetFields();
                  setRelationRelation(null);
                }}
              >
                取消
              </Button>
              <Button type="primary" htmlType="submit">
                {editingRelation ? '更新' : '添加'}
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 属性编辑模态框 */}
      <Modal
        title="添加属性"
        open={propertyModalVisible}
        onCancel={() => {
          setPropertyModalVisible(false);
          propertyForm.resetFields();
          setCurrentEditTarget(null);
          setCurrentEditTargetId(null);
        }}
        footer={null}
        width={600}
      >
        <Form
          form={propertyForm}
          layout="vertical"
          onFinish={handleAddProperty}
        >
          <Form.Item
            name="name"
            label="属性名称"
            rules={[{ required: true, message: '请输入属性名称' }]}
          >
            <Input placeholder="请输入属性名称" />
          </Form.Item>
          
          <Form.Item
            name="data_type"
            label="数据类型"
            rules={[{ required: true, message: '请选择数据类型' }]}
          >
            <Select placeholder="选择数据类型">
              {Object.values(DataType).map((type) => (
                <Option key={type} value={type}>
                  {type.toUpperCase()}
                </Option>
              ))}
            </Select>
          </Form.Item>
          
          <Form.Item
            name="description"
            label="描述"
          >
            <TextArea
              rows={2}
              placeholder="请输入属性描述"
            />
          </Form.Item>
          
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="required"
                label="是否必需"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="default_value"
                label="默认值"
              >
                <Input placeholder="请输入默认值" />
              </Form.Item>
            </Col>
          </Row>
          
          <Form.Item
            name="constraints"
            label="约束条件（JSON格式）"
          >
            <TextArea
              rows={3}
              placeholder='例如: {"min": 0, "max": 100}'
            />
          </Form.Item>
          
          <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
            <Space>
              <Button
                onClick={() => {
                  setPropertyModalVisible(false);
                  propertyForm.resetFields();
                  setCurrentEditTarget(null);
                  setCurrentEditTargetId(null);
                }}
              >
                取消
              </Button>
              <Button type="primary" htmlType="submit">
                添加
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default OntologyEditor;