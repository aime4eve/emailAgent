/**
 * 客户管理页面
 * 提供客户列表、详情查看、价值分析等功能
 */

import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Button,
  Input,
  Select,
  Space,
  Tag,
  Modal,
  Descriptions,
  Progress,
  Row,
  Col,
  Statistic,
  Avatar,
  Tooltip,
  message,
  Drawer,
  Badge,
} from 'antd';
import {
  SearchOutlined,
  UserOutlined,
  EyeOutlined,
  EditOutlined,
  StarOutlined,
  MailOutlined,
  TrophyOutlined,
  RiseOutlined,
  ClockCircleOutlined
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';

const { Search } = Input;
const { Option } = Select;

// 客户数据类型定义
interface Customer {
  id: string;
  name: string;
  email: string;
  phone?: string;
  company: string;
  country: string;
  region: string;
  grade: 'A' | 'B' | 'C';
  valueScore: number;
  inquiryCount: number;
  lastInquiryDate: string;
  totalOrderValue: number;
  averageOrderValue: number;
  conversionRate: number;
  status: 'active' | 'inactive' | 'potential';
  tags: string[];
  createdAt: string;
}

// 询盘记录类型
interface InquiryRecord {
  id: string;
  date: string;
  product: string;
  status: 'pending' | 'quoted' | 'closed' | 'lost';
  value: number;
  description: string;
}

// 模拟客户数据
const mockCustomers: Customer[] = [
  {
    id: '1',
    name: 'John Smith',
    email: 'john.smith@example.com',
    phone: '+1-555-0123',
    company: 'ABC Trading Co.',
    country: 'United States',
    region: 'North America',
    grade: 'A',
    valueScore: 95,
    inquiryCount: 15,
    lastInquiryDate: '2024-01-15',
    totalOrderValue: 250000,
    averageOrderValue: 16667,
    conversionRate: 0.8,
    status: 'active',
    tags: ['VIP', '长期合作', '高价值'],
    createdAt: '2023-06-01',
  },
  {
    id: '2',
    name: 'Maria Garcia',
    email: 'maria.garcia@empresa.es',
    company: 'Empresa Internacional',
    country: 'Spain',
    region: 'Europe',
    grade: 'B',
    valueScore: 72,
    inquiryCount: 8,
    lastInquiryDate: '2024-01-10',
    totalOrderValue: 120000,
    averageOrderValue: 15000,
    conversionRate: 0.6,
    status: 'active',
    tags: ['潜力客户', '欧洲市场'],
    createdAt: '2023-08-15',
  },
  {
    id: '3',
    name: 'Li Wei',
    email: 'li.wei@company.cn',
    phone: '+86-138-0000-0000',
    company: '中国贸易有限公司',
    country: 'China',
    region: 'Asia',
    grade: 'C',
    valueScore: 45,
    inquiryCount: 3,
    lastInquiryDate: '2023-12-20',
    totalOrderValue: 30000,
    averageOrderValue: 10000,
    conversionRate: 0.3,
    status: 'potential',
    tags: ['新客户', '待培育'],
    createdAt: '2023-11-01',
  },
];

// 模拟询盘记录
const mockInquiries: Record<string, InquiryRecord[]> = {
  '1': [
    {
      id: 'inq1',
      date: '2024-01-15',
      product: '工业设备A',
      status: 'quoted',
      value: 50000,
      description: '询问100台工业设备的报价和交货期',
    },
    {
      id: 'inq2',
      date: '2024-01-10',
      product: '配件B',
      status: 'closed',
      value: 15000,
      description: '采购相关配件，已成交',
    },
  ],
  '2': [
    {
      id: 'inq3',
      date: '2024-01-10',
      product: '电子产品C',
      status: 'pending',
      value: 25000,
      description: '询问电子产品的技术规格和价格',
    },
  ],
  '3': [
    {
      id: 'inq4',
      date: '2023-12-20',
      product: '原材料D',
      status: 'lost',
      value: 8000,
      description: '价格竞争激烈，客户选择了其他供应商',
    },
  ],
};

/**
 * 客户管理页面组件
 */
const CustomersPage: React.FC = () => {
  const [customers] = useState<Customer[]>(mockCustomers);
  const [filteredCustomers] = useState<Customer[]>(mockCustomers);
  const [loading] = useState(false);
  const [searchText] = useState('');
  const [gradeFilter, setGradeFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [selectedCustomer] = useState<Customer | null>(null);
  const [detailVisible] = useState(false);
  const [inquiryDrawerVisible] = useState(false);
  // const [selectedRowKeys] = useState<React.Key[]>([]);

  // 获取客户等级颜色
  const getGradeColor = (grade: string) => {
    switch (grade) {
      case 'A': return 'gold';
      case 'B': return 'blue';
      case 'C': return 'default';
      default: return 'default';
    }
  };

  // 获取状态颜色
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'inactive': return 'default';
      case 'potential': return 'processing';
      default: return 'default';
    }
  };

  // 获取状态文本
  const getStatusText = (status: string) => {
    switch (status) {
      case 'active': return '活跃';
      case 'inactive': return '非活跃';
      case 'potential': return '潜在';
      default: return status;
    }
  };

  // 过滤客户数据
  const filterCustomers = () => {
    let filtered = customers;

    // 搜索过滤
    if (searchText) {
      filtered = filtered.filter(customer => 
        customer.name.toLowerCase().includes(searchText.toLowerCase()) ||
        customer.email.toLowerCase().includes(searchText.toLowerCase()) ||
        customer.company.toLowerCase().includes(searchText.toLowerCase()) ||
        customer.country.toLowerCase().includes(searchText.toLowerCase())
      );
    }

    // 等级过滤
    if (gradeFilter !== 'all') {
      filtered = filtered.filter(customer => customer.grade === gradeFilter);
    }

    // 状态过滤
    if (statusFilter !== 'all') {
      filtered = filtered.filter(customer => customer.status === statusFilter);
    }

    // setFilteredCustomers(filtered);
    console.log('过滤客户:', filtered);
  };

  // 监听过滤条件变化
  useEffect(() => {
    filterCustomers();
  }, [searchText, gradeFilter, statusFilter, customers]);

  // 查看客户详情
  const handleViewDetail = (customer: Customer) => {
    // setSelectedCustomer(customer);
    // setDetailVisible(true);
    console.log('查看客户详情:', customer);
  };

  // 查看询盘记录
  const handleViewInquiries = (customer: Customer) => {
    // setSelectedCustomer(customer);
    // setInquiryDrawerVisible(true);
    console.log('查看询盘记录:', customer);
  };

  // 表格列定义
  const columns: ColumnsType<Customer> = [
    {
      title: '客户信息',
      key: 'customer',
      width: 250,
      render: (_, record) => (
        <Space>
          <Avatar icon={<UserOutlined />} />
          <div>
            <div style={{ fontWeight: 'bold' }}>{record.name}</div>
            <div style={{ fontSize: '12px', color: '#666' }}>{record.company}</div>
            <div style={{ fontSize: '12px', color: '#999' }}>{record.email}</div>
          </div>
        </Space>
      ),
    },
    {
      title: '地区',
      dataIndex: 'country',
      key: 'country',
      width: 120,
      render: (country, record) => (
        <div>
          <div>{country}</div>
          <div style={{ fontSize: '12px', color: '#666' }}>{record.region}</div>
        </div>
      ),
    },
    {
      title: '客户等级',
      dataIndex: 'grade',
      key: 'grade',
      width: 100,
      render: (grade) => (
        <Tag color={getGradeColor(grade)} icon={<TrophyOutlined />}>
          {grade}级
        </Tag>
      ),
    },
    {
      title: '价值评分',
      dataIndex: 'valueScore',
      key: 'valueScore',
      width: 120,
      render: (score) => (
        <div>
          <Progress 
            percent={score} 
            size="small" 
            strokeColor={score >= 80 ? '#52c41a' : score >= 60 ? '#1890ff' : '#faad14'}
          />
          <div style={{ textAlign: 'center', fontSize: '12px' }}>{score}分</div>
        </div>
      ),
    },
    {
      title: '询盘统计',
      key: 'inquiry',
      width: 120,
      render: (_, record) => (
        <div>
          <div><strong>{record.inquiryCount}</strong> 次询盘</div>
          <div style={{ fontSize: '12px', color: '#666' }}>转化率: {(record.conversionRate * 100).toFixed(1)}%</div>
        </div>
      ),
    },
    {
      title: '订单价值',
      key: 'orderValue',
      width: 150,
      render: (_, record) => (
        <div>
          <div>总计: ${record.totalOrderValue.toLocaleString()}</div>
          <div style={{ fontSize: '12px', color: '#666' }}>平均: ${record.averageOrderValue.toLocaleString()}</div>
        </div>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status) => (
        <Badge 
          status={getStatusColor(status) as any} 
          text={getStatusText(status)}
        />
      ),
    },
    {
      title: '最后询盘',
      dataIndex: 'lastInquiryDate',
      key: 'lastInquiryDate',
      width: 120,
      render: (date) => (
        <div>
          <ClockCircleOutlined style={{ marginRight: 4 }} />
          {date}
        </div>
      ),
    },
    {
      title: '标签',
      dataIndex: 'tags',
      key: 'tags',
      width: 150,
      render: (tags: string[]) => (
        <div>
          {tags.slice(0, 2).map(tag => (
            <Tag key={tag}>{tag}</Tag>
          ))}
          {tags.length > 2 && (
            <Tooltip title={tags.slice(2).join(', ')}>
              <Tag>+{tags.length - 2}</Tag>
            </Tooltip>
          )}
        </div>
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      fixed: 'right',
      render: (_, record) => (
        <Space>
          <Tooltip title="查看详情">
            <Button 
              type="text" 
              icon={<EyeOutlined />} 
              onClick={() => handleViewDetail(record)}
            />
          </Tooltip>
          <Tooltip title="询盘记录">
            <Button 
              type="text" 
              icon={<MailOutlined />} 
              onClick={() => handleViewInquiries(record)}
            />
          </Tooltip>
          <Tooltip title="编辑">
            <Button 
              type="text" 
              icon={<EditOutlined />} 
              onClick={() => message.info('编辑功能开发中')}
            />
          </Tooltip>
        </Space>
      ),
    },
  ];

  // 询盘记录表格列
  const inquiryColumns: ColumnsType<InquiryRecord> = [
    {
      title: '日期',
      dataIndex: 'date',
      key: 'date',
      width: 120,
    },
    {
      title: '产品',
      dataIndex: 'product',
      key: 'product',
      width: 150,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status) => {
        const statusMap = {
          pending: { color: 'processing', text: '待处理' },
          quoted: { color: 'warning', text: '已报价' },
          closed: { color: 'success', text: '已成交' },
          lost: { color: 'error', text: '已流失' },
        };
        const config = statusMap[status as keyof typeof statusMap];
        return <Badge status={config.color as any} text={config.text} />;
      },
    },
    {
      title: '价值',
      dataIndex: 'value',
      key: 'value',
      width: 120,
      render: (value) => `$${value.toLocaleString()}`,
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
    },
  ];

  return (
    <div>
      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="总客户数"
              value={customers.length}
              prefix={<UserOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="A级客户"
              value={customers.filter(c => c.grade === 'A').length}
              prefix={<TrophyOutlined />}
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="活跃客户"
              value={customers.filter(c => c.status === 'active').length}
              prefix={<RiseOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="平均价值评分"
              value={Math.round(customers.reduce((sum, c) => sum + c.valueScore, 0) / customers.length)}
              prefix={<StarOutlined />}
              suffix="分"
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 搜索和过滤 */}
      <Card style={{ marginBottom: 24 }}>
        <Row gutter={16} align="middle">
          <Col span={8}>
            <Search
              placeholder="搜索客户姓名、邮箱、公司或国家"
              value={searchText}
              onChange={(e) => console.log('搜索:', e.target.value)}
              onSearch={filterCustomers}
              enterButton={<SearchOutlined />}
            />
          </Col>
          <Col span={4}>
            <Select
              value={gradeFilter}
              onChange={setGradeFilter}
              style={{ width: '100%' }}
              placeholder="客户等级"
            >
              <Option value="all">全部等级</Option>
              <Option value="A">A级客户</Option>
              <Option value="B">B级客户</Option>
              <Option value="C">C级客户</Option>
            </Select>
          </Col>
          <Col span={4}>
            <Select
              value={statusFilter}
              onChange={setStatusFilter}
              style={{ width: '100%' }}
              placeholder="客户状态"
            >
              <Option value="all">全部状态</Option>
              <Option value="active">活跃</Option>
              <Option value="inactive">非活跃</Option>
              <Option value="potential">潜在</Option>
            </Select>
          </Col>
          <Col span={8}>
            <Space>
              <Button onClick={() => message.info('导出功能开发中')}>导出客户</Button>
              <Button type="primary" onClick={() => message.info('添加客户功能开发中')}>添加客户</Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* 客户列表 */}
      <Card>
        <Table
          columns={columns}
          dataSource={filteredCustomers}
          rowKey="id"
          loading={loading}
          scroll={{ x: 1400 }}
          pagination={{
            total: filteredCustomers.length,
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
          }}
        />
      </Card>

      {/* 客户详情模态框 */}
      <Modal
        title="客户详情"
        open={detailVisible}
        onCancel={() => console.log('关闭客户详情弹窗')}
        footer={null}
        width={800}
      >
        {selectedCustomer && (
          <div>
            <Row gutter={16}>
              <Col span={12}>
                <Descriptions title="基本信息" column={1}>
                  <Descriptions.Item label="姓名">{selectedCustomer.name}</Descriptions.Item>
                  <Descriptions.Item label="邮箱">{selectedCustomer.email}</Descriptions.Item>
                  <Descriptions.Item label="电话">{selectedCustomer.phone || '未提供'}</Descriptions.Item>
                  <Descriptions.Item label="公司">{selectedCustomer.company}</Descriptions.Item>
                  <Descriptions.Item label="国家">{selectedCustomer.country}</Descriptions.Item>
                  <Descriptions.Item label="地区">{selectedCustomer.region}</Descriptions.Item>
                </Descriptions>
              </Col>
              <Col span={12}>
                <Descriptions title="业务信息" column={1}>
                  <Descriptions.Item label="客户等级">
                    <Tag color={getGradeColor(selectedCustomer.grade)}>{selectedCustomer.grade}级</Tag>
                  </Descriptions.Item>
                  <Descriptions.Item label="价值评分">
                    <Progress percent={selectedCustomer.valueScore} size="small" />
                  </Descriptions.Item>
                  <Descriptions.Item label="询盘次数">{selectedCustomer.inquiryCount}</Descriptions.Item>
                  <Descriptions.Item label="转化率">{(selectedCustomer.conversionRate * 100).toFixed(1)}%</Descriptions.Item>
                  <Descriptions.Item label="总订单价值">${selectedCustomer.totalOrderValue.toLocaleString()}</Descriptions.Item>
                  <Descriptions.Item label="平均订单价值">${selectedCustomer.averageOrderValue.toLocaleString()}</Descriptions.Item>
                </Descriptions>
              </Col>
            </Row>
            <div style={{ marginTop: 16 }}>
              <strong>客户标签：</strong>
              {selectedCustomer.tags.map(tag => (
                <Tag key={tag} style={{ margin: '4px' }}>{tag}</Tag>
              ))}
            </div>
          </div>
        )}
      </Modal>

      {/* 询盘记录抽屉 */}
      <Drawer
        title={`${selectedCustomer?.name} - 询盘记录`}
        placement="right"
        width={800}
        open={inquiryDrawerVisible}
        onClose={() => console.log('关闭询盘记录抽屉')}
      >
        {selectedCustomer && (
          <Table
            columns={inquiryColumns}
            dataSource={mockInquiries[selectedCustomer.id] || []}
            rowKey="id"
            pagination={false}
          />
        )}
      </Drawer>
    </div>
  );
};

export default CustomersPage;