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
  Form,
  InputNumber,
  Checkbox,
} from 'antd';
// 动态导入xlsx库以避免Vite预构建问题
// import * as XLSX from 'xlsx';
import {
  SearchOutlined,
  UserOutlined,
  EyeOutlined,
  EditOutlined,
  StarOutlined,
  MailOutlined,
  TrophyOutlined,
  RiseOutlined,
  ClockCircleOutlined,
  PlusOutlined,
  DownloadOutlined,
  LoadingOutlined
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
  const [customers, setCustomers] = useState<Customer[]>(mockCustomers);
  const [filteredCustomers, setFilteredCustomers] = useState<Customer[]>(mockCustomers);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [gradeFilter, setGradeFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);
  const [detailVisible, setDetailVisible] = useState(false);
  const [inquiryDrawerVisible, setInquiryDrawerVisible] = useState(false);
  const [addCustomerVisible, setAddCustomerVisible] = useState(false);
  const [exportLoading, setExportLoading] = useState(false);
  const [emailModalVisible, setEmailModalVisible] = useState(false);
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [emailLoading, setEmailLoading] = useState(false);
  const [editLoading, setEditLoading] = useState(false);
  const [form] = Form.useForm();
  const [emailForm] = Form.useForm();
  const [editForm] = Form.useForm();

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

    setFilteredCustomers(filtered);
  };

  // 监听过滤条件变化
  useEffect(() => {
    filterCustomers();
  }, [searchText, gradeFilter, statusFilter, customers]);

  // 查看客户详情
  const handleViewDetail = (customer: Customer) => {
    setSelectedCustomer(customer);
    setDetailVisible(true);
  };



  /**
   * 发送邮件功能
   */
  const handleSendEmail = (customer: Customer) => {
    setSelectedCustomer(customer);
    setEmailModalVisible(true);
    // 预填充邮箱地址
    emailForm.setFieldsValue({
      to: customer.email,
      subject: '',
      template: 'custom',
      content: ''
    });
  };

  /**
   * 编辑客户功能
   */
  const handleEditCustomer = (customer: Customer) => {
    setSelectedCustomer(customer);
    setEditModalVisible(true);
    // 预填充客户数据
    editForm.setFieldsValue({
      name: customer.name,
      email: customer.email,
      phone: customer.phone,
      company: customer.company,
      country: customer.country,
      region: customer.region,
      grade: customer.grade,
      valueScore: customer.valueScore,
      tags: customer.tags
    });
  };

  /**
   * 提交邮件发送
   */
  const handleSubmitEmail = async (values: any) => {
    try {
      setEmailLoading(true);
      
      // 模拟邮件发送API调用
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      message.success(`邮件已成功发送至 ${values.to}`);
      setEmailModalVisible(false);
      emailForm.resetFields();
    } catch (error) {
      message.error('邮件发送失败，请重试');
    } finally {
      setEmailLoading(false);
    }
  };

  /**
   * 提交客户编辑
   */
  const handleSubmitEdit = async (values: any) => {
    try {
      setEditLoading(true);
      
      if (!selectedCustomer) return;
      
      // 更新客户数据
      const updatedCustomer: Customer = {
        ...selectedCustomer,
        name: values.name,
        email: values.email,
        phone: values.phone || '',
        company: values.company,
        country: values.country,
        region: values.region,
        grade: values.grade,
        valueScore: values.valueScore,
        tags: values.tags || []
      };
      
      // 模拟API调用延迟
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // 更新客户列表
      const updatedCustomers = customers.map(customer => 
        customer.id === selectedCustomer.id ? updatedCustomer : customer
      );
      setCustomers(updatedCustomers);
      setFilteredCustomers(updatedCustomers);
      
      message.success('客户信息更新成功！');
      setEditModalVisible(false);
      editForm.resetFields();
    } catch (error) {
      message.error('更新客户信息失败，请重试');
    } finally {
      setEditLoading(false);
    }
  };

  /**
   * 获取邮件模板内容
   */
  const getEmailTemplate = (templateType: string, customerName: string) => {
    const templates = {
      inquiry_reply: `尊敬的 ${customerName}，\n\n感谢您对我们产品的询盘。我们已收到您的询价需求，将在24小时内为您提供详细的报价方案。\n\n如有任何疑问，请随时联系我们。\n\n此致\n敬礼`,
      product_recommend: `尊敬的 ${customerName}，\n\n根据您的业务需求，我们为您推荐以下优质产品：\n\n[产品详情]\n\n我们相信这些产品能够满足您的需求，期待与您进一步沟通。\n\n此致\n敬礼`,
      holiday_greeting: `尊敬的 ${customerName}，\n\n值此佳节来临之际，我们向您致以最诚挚的节日问候！\n\n感谢您一直以来对我们的信任与支持。\n\n祝您节日快乐，工作顺利！\n\n此致\n敬礼`,
      follow_up: `尊敬的 ${customerName}，\n\n希望您一切安好。我们想了解一下您对我们之前讨论的项目是否还有兴趣。\n\n如果您需要任何帮助或有新的需求，请随时联系我们。\n\n期待您的回复。\n\n此致\n敬礼`,
      custom: ''
    };
    return templates[templateType as keyof typeof templates] || '';
  };

  /**
   * 添加客户功能
   */
  const handleAddCustomer = () => {
    setAddCustomerVisible(true);
  };

  /**
   * 提交新客户表单
   */
  const handleSubmitCustomer = async (values: any) => {
    try {
      setLoading(true);
      
      // 生成新客户ID
      const newId = (customers.length + 1).toString();
      
      // 创建新客户对象
      const newCustomer: Customer = {
        id: newId,
        name: values.name,
        email: values.email,
        phone: values.phone || '',
        company: values.company,
        country: values.country,
        region: values.region,
        grade: values.grade || 'C',
        valueScore: values.valueScore || 50,
        inquiryCount: 0,
        lastInquiryDate: new Date().toISOString().split('T')[0],
        totalOrderValue: 0,
        averageOrderValue: 0,
        conversionRate: 0,
        status: 'potential',
        tags: values.tags || [],
        createdAt: new Date().toISOString().split('T')[0],
      };
      
      // 模拟API调用延迟
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // 添加到客户列表
      const updatedCustomers = [...customers, newCustomer];
      setCustomers(updatedCustomers);
      setFilteredCustomers(updatedCustomers);
      
      message.success('客户添加成功！');
      setAddCustomerVisible(false);
      form.resetFields();
    } catch (error) {
      message.error('添加客户失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  /**
   * 导出客户数据功能（使用动态导入xlsx库）
   */
  const handleExportCustomers = async () => {
    try {
      setExportLoading(true);
      
      // 准备导出数据
      const exportData = filteredCustomers.map(customer => ({
        '客户姓名': customer.name,
        '邮箱': customer.email,
        '电话': customer.phone || '',
        '公司': customer.company,
        '国家': customer.country,
        '地区': customer.region,
        '客户等级': customer.grade + '级',
        '价值评分': customer.valueScore + '分',
        '询盘次数': customer.inquiryCount,
        '最后询盘日期': customer.lastInquiryDate,
        '总订单价值': '$' + customer.totalOrderValue.toLocaleString(),
        '平均订单价值': '$' + customer.averageOrderValue.toLocaleString(),
        '转化率': (customer.conversionRate * 100).toFixed(1) + '%',
        '状态': getStatusText(customer.status),
        '标签': customer.tags.join(', '),
        '创建日期': customer.createdAt,
      }));
      
      // 模拟导出处理时间
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      try {
        // 动态导入xlsx库
        const XLSX = await import('xlsx');
        
        // 创建工作簿
        const ws = XLSX.utils.json_to_sheet(exportData);
        const wb = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(wb, ws, '客户数据');
        
        // 设置列宽
        const colWidths = [
          { wch: 15 }, // 客户姓名
          { wch: 25 }, // 邮箱
          { wch: 15 }, // 电话
          { wch: 20 }, // 公司
          { wch: 12 }, // 国家
          { wch: 12 }, // 地区
          { wch: 10 }, // 客户等级
          { wch: 10 }, // 价值评分
          { wch: 10 }, // 询盘次数
          { wch: 15 }, // 最后询盘日期
          { wch: 15 }, // 总订单价值
          { wch: 15 }, // 平均订单价值
          { wch: 10 }, // 转化率
          { wch: 10 }, // 状态
          { wch: 20 }, // 标签
          { wch: 12 }, // 创建日期
        ];
        ws['!cols'] = colWidths;
        
        // 生成文件名
        const fileName = `客户数据_${new Date().toISOString().split('T')[0]}.xlsx`;
        
        // 下载文件
        XLSX.writeFile(wb, fileName);
        
        message.success(`成功导出 ${exportData.length} 条客户数据！`);
      } catch (xlsxError) {
        console.warn('XLSX导入失败，使用CSV格式导出:', xlsxError);
        // 如果xlsx导入失败，使用CSV格式导出
        exportAsCSV(exportData);
      }
    } catch (error) {
      message.error('导出失败，请重试');
      console.error('Export error:', error);
    } finally {
      setExportLoading(false);
    }
  };

  /**
   * CSV格式导出功能（备用方案）
   */
  const exportAsCSV = (data: any[]) => {
    try {
      if (data.length === 0) {
        message.warning('没有数据可导出');
        return;
      }

      // 获取表头
      const headers = Object.keys(data[0]);
      
      // 构建CSV内容
      const csvContent = [
        // 表头行
        headers.join(','),
        // 数据行
        ...data.map(row => 
          headers.map(header => {
            const value = row[header] || '';
            // 如果值包含逗号、引号或换行符，需要用引号包围并转义
            if (typeof value === 'string' && (value.includes(',') || value.includes('"') || value.includes('\n'))) {
              return `"${value.replace(/"/g, '""')}"`;
            }
            return value;
          }).join(',')
        )
      ].join('\n');

      // 添加BOM以支持中文
      const BOM = '\uFEFF';
      const blob = new Blob([BOM + csvContent], { type: 'text/csv;charset=utf-8;' });
      
      // 创建下载链接
      const link = document.createElement('a');
      const url = URL.createObjectURL(blob);
      link.setAttribute('href', url);
      link.setAttribute('download', `客户数据_${new Date().toISOString().split('T')[0]}.csv`);
      link.style.visibility = 'hidden';
      
      // 触发下载
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // 清理URL对象
      URL.revokeObjectURL(url);
      
      message.success(`成功导出 ${data.length} 条客户数据（CSV格式）！`);
    } catch (error) {
      message.error('CSV导出失败，请重试');
      console.error('CSV export error:', error);
    }
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
          <Tooltip title="发送邮件">
            <Button 
              type="text" 
              icon={<MailOutlined />} 
              onClick={() => handleSendEmail(record)}
            />
          </Tooltip>
          <Tooltip title="编辑">
            <Button 
              type="text" 
              icon={<EditOutlined />} 
              onClick={() => handleEditCustomer(record)}
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
              onChange={(e) => setSearchText(e.target.value)}
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
              <Button 
                icon={exportLoading ? <LoadingOutlined /> : <DownloadOutlined />}
                loading={exportLoading}
                onClick={handleExportCustomers}
              >
                导出客户
              </Button>
              <Button 
                type="primary" 
                icon={<PlusOutlined />}
                onClick={handleAddCustomer}
              >
                添加客户
              </Button>
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

      {/* 添加客户模态框 */}
      <Modal
        title="添加新客户"
        open={addCustomerVisible}
        onCancel={() => {
          setAddCustomerVisible(false);
          form.resetFields();
        }}
        footer={null}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmitCustomer}
          initialValues={{
            grade: 'C',
            valueScore: 50
          }}
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="客户姓名"
                name="name"
                rules={[{ required: true, message: '请输入客户姓名' }]}
              >
                <Input placeholder="请输入客户姓名" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="邮箱地址"
                name="email"
                rules={[
                  { required: true, message: '请输入邮箱地址' },
                  { type: 'email', message: '请输入有效的邮箱地址' }
                ]}
              >
                <Input placeholder="请输入邮箱地址" />
              </Form.Item>
            </Col>
          </Row>
          
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="电话号码"
                name="phone"
              >
                <Input placeholder="请输入电话号码" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="公司名称"
                name="company"
                rules={[{ required: true, message: '请输入公司名称' }]}
              >
                <Input placeholder="请输入公司名称" />
              </Form.Item>
            </Col>
          </Row>
          
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="国家"
                name="country"
                rules={[{ required: true, message: '请输入国家' }]}
              >
                <Input placeholder="请输入国家" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="地区"
                name="region"
                rules={[{ required: true, message: '请输入地区' }]}
              >
                <Select placeholder="请选择地区">
                  <Option value="North America">北美</Option>
                  <Option value="Europe">欧洲</Option>
                  <Option value="Asia">亚洲</Option>
                  <Option value="South America">南美</Option>
                  <Option value="Africa">非洲</Option>
                  <Option value="Oceania">大洋洲</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>
          
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="客户等级"
                name="grade"
              >
                <Select placeholder="请选择客户等级">
                  <Option value="A">A级客户</Option>
                  <Option value="B">B级客户</Option>
                  <Option value="C">C级客户</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="价值评分"
                name="valueScore"
              >
                <InputNumber 
                  min={0} 
                  max={100} 
                  placeholder="请输入价值评分" 
                  style={{ width: '100%' }}
                />
              </Form.Item>
            </Col>
          </Row>
          
          <Form.Item
            label="客户标签"
            name="tags"
          >
            <Checkbox.Group>
              <Row>
                <Col span={8}><Checkbox value="VIP">VIP</Checkbox></Col>
                <Col span={8}><Checkbox value="长期合作">长期合作</Checkbox></Col>
                <Col span={8}><Checkbox value="高价值">高价值</Checkbox></Col>
                <Col span={8}><Checkbox value="潜力客户">潜力客户</Checkbox></Col>
                <Col span={8}><Checkbox value="新客户">新客户</Checkbox></Col>
                <Col span={8}><Checkbox value="待培育">待培育</Checkbox></Col>
              </Row>
            </Checkbox.Group>
          </Form.Item>
          
          <Form.Item style={{ textAlign: 'right', marginBottom: 0 }}>
            <Space>
              <Button onClick={() => {
                setAddCustomerVisible(false);
                form.resetFields();
              }}>
                取消
              </Button>
              <Button type="primary" htmlType="submit" loading={loading}>
                添加客户
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 客户详情模态框 */}
      <Modal
        title="客户详情"
        open={detailVisible}
        onCancel={() => setDetailVisible(false)}
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
        onClose={() => setInquiryDrawerVisible(false)}
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

      {/* 发送邮件模态框 */}
      <Modal
        title={`发送邮件给 ${selectedCustomer?.name}`}
        open={emailModalVisible}
        onCancel={() => {
          setEmailModalVisible(false);
          emailForm.resetFields();
        }}
        footer={null}
        width={700}
      >
        <Form
          form={emailForm}
          layout="vertical"
          onFinish={handleSubmitEmail}
          onValuesChange={(changedValues) => {
            if (changedValues.template && changedValues.template !== 'custom' && selectedCustomer) {
              const templateContent = getEmailTemplate(changedValues.template, selectedCustomer.name);
              emailForm.setFieldsValue({ content: templateContent });
            }
          }}
        >
          <Form.Item
            label="收件人"
            name="to"
            rules={[{ required: true, message: '请输入收件人邮箱' }]}
          >
            <Input placeholder="请输入收件人邮箱" disabled />
          </Form.Item>
          
          <Form.Item
            label="邮件主题"
            name="subject"
            rules={[{ required: true, message: '请输入邮件主题' }]}
          >
            <Input placeholder="请输入邮件主题" />
          </Form.Item>
          
          <Form.Item
            label="邮件模板"
            name="template"
          >
            <Select placeholder="选择邮件模板">
              <Option value="custom">自定义内容</Option>
              <Option value="inquiry_reply">询盘回复</Option>
              <Option value="product_recommend">产品推荐</Option>
              <Option value="holiday_greeting">节日问候</Option>
              <Option value="follow_up">跟进邮件</Option>
            </Select>
          </Form.Item>
          
          <Form.Item
            label="邮件内容"
            name="content"
            rules={[{ required: true, message: '请输入邮件内容' }]}
          >
            <Input.TextArea 
              rows={8} 
              placeholder="请输入邮件内容" 
              showCount
              maxLength={2000}
            />
          </Form.Item>
          
          <Form.Item style={{ textAlign: 'right', marginBottom: 0 }}>
            <Space>
              <Button onClick={() => {
                setEmailModalVisible(false);
                emailForm.resetFields();
              }}>
                取消
              </Button>
              <Button type="primary" htmlType="submit" loading={emailLoading}>
                发送邮件
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 编辑客户模态框 */}
      <Modal
        title={`编辑客户 - ${selectedCustomer?.name}`}
        open={editModalVisible}
        onCancel={() => {
          setEditModalVisible(false);
          editForm.resetFields();
        }}
        footer={null}
        width={600}
      >
        <Form
          form={editForm}
          layout="vertical"
          onFinish={handleSubmitEdit}
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="客户姓名"
                name="name"
                rules={[{ required: true, message: '请输入客户姓名' }]}
              >
                <Input placeholder="请输入客户姓名" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="邮箱地址"
                name="email"
                rules={[
                  { required: true, message: '请输入邮箱地址' },
                  { type: 'email', message: '请输入有效的邮箱地址' }
                ]}
              >
                <Input placeholder="请输入邮箱地址" />
              </Form.Item>
            </Col>
          </Row>
          
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="电话号码"
                name="phone"
              >
                <Input placeholder="请输入电话号码" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="公司名称"
                name="company"
                rules={[{ required: true, message: '请输入公司名称' }]}
              >
                <Input placeholder="请输入公司名称" />
              </Form.Item>
            </Col>
          </Row>
          
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="国家"
                name="country"
                rules={[{ required: true, message: '请输入国家' }]}
              >
                <Input placeholder="请输入国家" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="地区"
                name="region"
                rules={[{ required: true, message: '请输入地区' }]}
              >
                <Select placeholder="请选择地区">
                  <Option value="North America">北美</Option>
                  <Option value="Europe">欧洲</Option>
                  <Option value="Asia">亚洲</Option>
                  <Option value="South America">南美</Option>
                  <Option value="Africa">非洲</Option>
                  <Option value="Oceania">大洋洲</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>
          
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="客户等级"
                name="grade"
              >
                <Select placeholder="请选择客户等级">
                  <Option value="A">A级客户</Option>
                  <Option value="B">B级客户</Option>
                  <Option value="C">C级客户</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="价值评分"
                name="valueScore"
              >
                <InputNumber 
                  min={0} 
                  max={100} 
                  placeholder="请输入价值评分" 
                  style={{ width: '100%' }}
                />
              </Form.Item>
            </Col>
          </Row>
          
          <Form.Item
            label="客户标签"
            name="tags"
          >
            <Checkbox.Group>
              <Row>
                <Col span={8}><Checkbox value="VIP">VIP</Checkbox></Col>
                <Col span={8}><Checkbox value="长期合作">长期合作</Checkbox></Col>
                <Col span={8}><Checkbox value="高价值">高价值</Checkbox></Col>
                <Col span={8}><Checkbox value="潜力客户">潜力客户</Checkbox></Col>
                <Col span={8}><Checkbox value="新客户">新客户</Checkbox></Col>
                <Col span={8}><Checkbox value="待培育">待培育</Checkbox></Col>
              </Row>
            </Checkbox.Group>
          </Form.Item>
          
          <Form.Item style={{ textAlign: 'right', marginBottom: 0 }}>
            <Space>
              <Button onClick={() => {
                setEditModalVisible(false);
                editForm.resetFields();
              }}>
                取消
              </Button>
              <Button type="primary" htmlType="submit" loading={editLoading}>
                保存修改
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default CustomersPage;