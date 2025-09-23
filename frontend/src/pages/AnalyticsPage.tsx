/**
 * 客户分析页面
 * 提供客户价值分析、客户画像、分级管理等功能
 */

import React, { useState } from 'react';
import {
  Card,
  Row,
  Col,
  Statistic,
  Table,
  Select,
  DatePicker,
  Button,
  Modal,
  Descriptions,
  Tag,
  Progress,
  Space,
  Divider,
  Avatar,
  Typography,
  Alert
} from 'antd';
import {
  UserOutlined,
  DollarOutlined,
  RiseOutlined,
  FallOutlined,
  TrophyOutlined,
  StarOutlined,
  BarChartOutlined,
  LineChartOutlined,
  PieChartOutlined
} from '@ant-design/icons';
import { Line, Column, Pie } from '@ant-design/charts';
import type { ColumnsType } from 'antd/es/table';
import dayjs from 'dayjs';

const { RangePicker } = DatePicker;
const { Option } = Select;
const { Title, Text } = Typography;

// 客户价值指标类型
interface CustomerValueMetrics {
  customerId: string;
  customerName: string;
  company: string;
  country: string;
  grade: 'A' | 'B' | 'C';
  valueScore: number;
  inquiryActivity: number;
  productValue: number;
  companyStrength: number;
  conversionRate: number;
  avgOrderValue: number;
  totalOrderValue: number;
  inquiryFrequency: number;
  lastInquiryDays: number;
  potentialValue: number;
}

// 客户画像类型
interface CustomerProfile {
  customerId: string;
  basicInfo: {
    name: string;
    company: string;
    country: string;
    industry: string;
    companySize: string;
  };
  behaviorProfile: {
    inquiryFrequency: number;
    avgResponseTime: number;
    preferredContactTime: string;
    communicationStyle: string;
    decisionSpeed: string;
  };
  demandProfile: {
    primaryProducts: string[];
    priceRange: string;
    qualityRequirement: string;
    volumeRequirement: string;
    seasonality: string[];
  };
  riskProfile: {
    paymentHistory: string;
    creditRating: string;
    marketStability: string;
    competitorRelation: string;
  };
}

// 地区分析数据类型
interface RegionAnalysis {
  region: string;
  customerCount: number;
  avgValueScore: number;
  totalOrderValue: number;
  conversionRate: number;
  growthRate: number;
}

// 模拟客户价值数据
const mockCustomerMetrics: CustomerValueMetrics[] = [
  {
    customerId: '1',
    customerName: 'John Smith',
    company: 'ABC Trading Co.',
    country: 'United States',
    grade: 'A',
    valueScore: 95,
    inquiryActivity: 90,
    productValue: 95,
    companyStrength: 100,
    conversionRate: 0.8,
    avgOrderValue: 16667,
    totalOrderValue: 250000,
    inquiryFrequency: 15,
    lastInquiryDays: 5,
    potentialValue: 300000,
  },
  {
    customerId: '2',
    customerName: 'Maria Garcia',
    company: 'Empresa Internacional',
    country: 'Spain',
    grade: 'B',
    valueScore: 72,
    inquiryActivity: 70,
    productValue: 75,
    companyStrength: 70,
    conversionRate: 0.6,
    avgOrderValue: 15000,
    totalOrderValue: 120000,
    inquiryFrequency: 8,
    lastInquiryDays: 10,
    potentialValue: 180000,
  },
  {
    customerId: '3',
    customerName: 'Li Wei',
    company: '中国贸易有限公司',
    country: 'China',
    grade: 'C',
    valueScore: 45,
    inquiryActivity: 40,
    productValue: 50,
    companyStrength: 45,
    conversionRate: 0.3,
    avgOrderValue: 10000,
    totalOrderValue: 30000,
    inquiryFrequency: 3,
    lastInquiryDays: 30,
    potentialValue: 60000,
  },
];

// 模拟地区分析数据
const mockRegionAnalysis: RegionAnalysis[] = [
  {
    region: 'North America',
    customerCount: 45,
    avgValueScore: 78,
    totalOrderValue: 1250000,
    conversionRate: 0.65,
    growthRate: 0.15,
  },
  {
    region: 'Europe',
    customerCount: 38,
    avgValueScore: 72,
    totalOrderValue: 980000,
    conversionRate: 0.58,
    growthRate: 0.12,
  },
  {
    region: 'Asia',
    customerCount: 52,
    avgValueScore: 65,
    totalOrderValue: 850000,
    conversionRate: 0.52,
    growthRate: 0.22,
  },
  {
    region: 'Others',
    customerCount: 15,
    avgValueScore: 60,
    totalOrderValue: 320000,
    conversionRate: 0.45,
    growthRate: 0.08,
  },
];

// 模拟客户画像数据
const mockCustomerProfile: CustomerProfile = {
  customerId: '1',
  basicInfo: {
    name: 'John Smith',
    company: 'ABC Trading Co.',
    country: 'United States',
    industry: '制造业',
    companySize: '中型企业 (100-500人)',
  },
  behaviorProfile: {
    inquiryFrequency: 15,
    avgResponseTime: 2.5,
    preferredContactTime: '工作日 9:00-17:00',
    communicationStyle: '直接高效',
    decisionSpeed: '快速决策',
  },
  demandProfile: {
    primaryProducts: ['工业设备', '机械配件', '电子元件'],
    priceRange: '$10,000 - $50,000',
    qualityRequirement: '高品质要求',
    volumeRequirement: '中等批量',
    seasonality: ['Q1', 'Q3'],
  },
  riskProfile: {
    paymentHistory: '良好',
    creditRating: 'A级',
    marketStability: '稳定',
    competitorRelation: '无竞争关系',
  },
};

/**
 * 客户分析页面组件
 */
const AnalyticsPage: React.FC = () => {
  const [loading] = useState(false);
  const [selectedPeriod, setSelectedPeriod] = useState<[dayjs.Dayjs, dayjs.Dayjs] | null>(null);
  const [selectedRegion, setSelectedRegion] = useState<string>('all');
  const [selectedGrade, setSelectedGrade] = useState<string>('all');
  const [profileModalVisible] = useState(false);
  const [selectedCustomerProfile] = useState<CustomerProfile | null>(null);

  // 获取客户等级颜色
  const getGradeColor = (grade: string) => {
    switch (grade) {
      case 'A': return '#f50';
      case 'B': return '#2db7f5';
      case 'C': return '#87d068';
      default: return '#d9d9d9';
    }
  };

  // 获取价值评分颜色
  const getScoreColor = (score: number) => {
    if (score >= 80) return '#52c41a';
    if (score >= 60) return '#1890ff';
    if (score >= 40) return '#faad14';
    return '#f5222d';
  };

  // 客户价值表格列定义
  const valueColumns: ColumnsType<CustomerValueMetrics> = [
    {
      title: '客户信息',
      key: 'customer',
      width: 200,
      render: (_, record) => (
        <Space>
          <Avatar icon={<UserOutlined />} />
          <div>
            <div style={{ fontWeight: 'bold' }}>{record.customerName}</div>
            <div style={{ fontSize: '12px', color: '#666' }}>{record.company}</div>
            <div style={{ fontSize: '12px', color: '#999' }}>{record.country}</div>
          </div>
        </Space>
      ),
    },
    {
      title: '客户等级',
      dataIndex: 'grade',
      key: 'grade',
      width: 100,
      render: (grade) => (
        <Tag color={getGradeColor(grade)}>{grade}级</Tag>
      ),
    },
    {
      title: '综合评分',
      dataIndex: 'valueScore',
      key: 'valueScore',
      width: 120,
      render: (score) => (
        <div>
          <Progress 
            percent={score} 
            size="small" 
            strokeColor={getScoreColor(score)}
            showInfo={false}
          />
          <div style={{ textAlign: 'center', fontSize: '12px', marginTop: 4 }}>
            <strong>{score}</strong>分
          </div>
        </div>
      ),
    },
    {
      title: '询盘活跃度',
      dataIndex: 'inquiryActivity',
      key: 'inquiryActivity',
      width: 120,
      render: (score) => (
        <Progress 
          percent={score} 
          size="small" 
          strokeColor="#1890ff"
          format={() => `${score}分`}
        />
      ),
    },
    {
      title: '产品价值度',
      dataIndex: 'productValue',
      key: 'productValue',
      width: 120,
      render: (score) => (
        <Progress 
          percent={score} 
          size="small" 
          strokeColor="#52c41a"
          format={() => `${score}分`}
        />
      ),
    },
    {
      title: '公司实力度',
      dataIndex: 'companyStrength',
      key: 'companyStrength',
      width: 120,
      render: (score) => (
        <Progress 
          percent={score} 
          size="small" 
          strokeColor="#faad14"
          format={() => `${score}分`}
        />
      ),
    },
    {
      title: '转化率',
      dataIndex: 'conversionRate',
      key: 'conversionRate',
      width: 100,
      render: (rate) => (
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '16px', fontWeight: 'bold' }}>
            {(rate * 100).toFixed(1)}%
          </div>
        </div>
      ),
    },
    {
      title: '订单价值',
      key: 'orderValue',
      width: 150,
      render: (_, record) => (
        <div>
          <div>总计: <strong>${record.totalOrderValue.toLocaleString()}</strong></div>
          <div style={{ fontSize: '12px', color: '#666' }}>平均: ${record.avgOrderValue.toLocaleString()}</div>
        </div>
      ),
    },
    {
      title: '潜在价值',
      dataIndex: 'potentialValue',
      key: 'potentialValue',
      width: 120,
      render: (value) => (
        <div style={{ textAlign: 'center' }}>
          <div style={{ color: '#1890ff', fontWeight: 'bold' }}>
            ${value.toLocaleString()}
          </div>
        </div>
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 100,
      render: (_) => (
        <Button 
          type="link" 
          onClick={() => {
            // setSelectedCustomerProfile(mockCustomerProfile);
            // setProfileModalVisible(true);
            console.log('查看客户画像:', mockCustomerProfile);
          }}
        >
          查看画像
        </Button>
      ),
    },
  ];

  // 价值分布图表数据
  const valueDistributionData = [
    { grade: 'A级客户', count: mockCustomerMetrics.filter(c => c.grade === 'A').length, color: '#f50' },
    { grade: 'B级客户', count: mockCustomerMetrics.filter(c => c.grade === 'B').length, color: '#2db7f5' },
    { grade: 'C级客户', count: mockCustomerMetrics.filter(c => c.grade === 'C').length, color: '#87d068' },
  ];

  // 地区分析图表数据
  const regionChartData = mockRegionAnalysis.map(item => ({
    region: item.region,
    customerCount: item.customerCount,
    avgValueScore: item.avgValueScore,
    totalOrderValue: item.totalOrderValue / 1000, // 转换为千美元
    conversionRate: item.conversionRate * 100,
    growthRate: item.growthRate * 100,
  }));

  // 价值趋势数据（模拟）
  const valueTrendData = [
    { month: '2023-07', avgScore: 65 },
    { month: '2023-08', avgScore: 68 },
    { month: '2023-09', avgScore: 70 },
    { month: '2023-10', avgScore: 72 },
    { month: '2023-11', avgScore: 75 },
    { month: '2023-12', avgScore: 78 },
    { month: '2024-01', avgScore: 80 },
  ];

  // 雷达图配置（暂时注释，如需要可以启用）
  // const radarConfig = {
  //   data: selectedCustomerProfile ? [
  //     {
  //       name: selectedCustomerProfile.basicInfo.name,
  //       inquiryActivity: mockCustomerMetrics[0].inquiryActivity,
  //       productValue: mockCustomerMetrics[0].productValue,
  //       companyStrength: mockCustomerMetrics[0].companyStrength,
  //       conversionRate: mockCustomerMetrics[0].conversionRate * 100,
  //       responseSpeed: 85,
  //       loyaltyIndex: 90,
  //     }
  //   ] : [],
  //   xField: 'name',
  //   yField: 'value',
  //   seriesField: 'name',
  //   meta: {
  //     value: {
  //       alias: '分值',
  //       min: 0,
  //       max: 100,
  //     },
  //   },
  // };

  return (
    <div>
      {/* 筛选控件 */}
      <Card style={{ marginBottom: 24 }}>
        <Row gutter={16} align="middle">
          <Col span={6}>
            <Space>
              <Text strong>时间范围:</Text>
              <RangePicker
                value={selectedPeriod}
                onChange={(dates) => setSelectedPeriod(dates as [dayjs.Dayjs, dayjs.Dayjs] | null)}
                placeholder={['开始日期', '结束日期']}
              />
            </Space>
          </Col>
          <Col span={4}>
            <Space>
              <Text strong>地区:</Text>
              <Select
                value={selectedRegion}
                onChange={setSelectedRegion}
                style={{ width: 120 }}
              >
                <Option value="all">全部地区</Option>
                <Option value="North America">北美</Option>
                <Option value="Europe">欧洲</Option>
                <Option value="Asia">亚洲</Option>
                <Option value="Others">其他</Option>
              </Select>
            </Space>
          </Col>
          <Col span={4}>
            <Space>
              <Text strong>等级:</Text>
              <Select
                value={selectedGrade}
                onChange={setSelectedGrade}
                style={{ width: 120 }}
              >
                <Option value="all">全部等级</Option>
                <Option value="A">A级客户</Option>
                <Option value="B">B级客户</Option>
                <Option value="C">C级客户</Option>
              </Select>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* 关键指标统计 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="平均客户价值评分"
              value={Math.round(mockCustomerMetrics.reduce((sum, c) => sum + c.valueScore, 0) / mockCustomerMetrics.length)}
              prefix={<StarOutlined />}
              suffix="分"
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="高价值客户占比"
              value={Math.round((mockCustomerMetrics.filter(c => c.valueScore >= 80).length / mockCustomerMetrics.length) * 100)}
              prefix={<TrophyOutlined />}
              suffix="%"
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="平均转化率"
              value={Math.round((mockCustomerMetrics.reduce((sum, c) => sum + c.conversionRate, 0) / mockCustomerMetrics.length) * 100)}
              prefix={<RiseOutlined />}
              suffix="%"
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="总潜在价值"
              value={mockCustomerMetrics.reduce((sum, c) => sum + c.potentialValue, 0)}
              prefix={<DollarOutlined />}
              formatter={(value) => `$${Number(value).toLocaleString()}`}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 图表分析 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={8}>
          <Card title={<><PieChartOutlined /> 客户等级分布</>}>
            <Pie
              data={valueDistributionData}
              angleField="count"
              colorField="grade"
              radius={0.8}
              label={{
                content: '{name} {percentage}',
              }}
              interactions={[{ type: 'element-active' }]}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card title={<><BarChartOutlined /> 地区客户分析</>}>
            <Column
              data={regionChartData}
              xField="region"
              yField="customerCount"
              label={{
                position: 'top',
                style: {
                  fill: '#000000',
                  opacity: 0.8,
                },
              }}
              meta={{
                region: {
                  alias: '地区',
                },
                customerCount: {
                  alias: '客户数量',
                },
              }}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card title={<><LineChartOutlined /> 客户价值趋势</>}>
            <Line
              data={valueTrendData}
              xField="month"
              yField="avgScore"
              point={{
                size: 5,
                shape: 'diamond',
              }}
              label={{
                style: {
                  fill: '#aaa',
                },
              }}
              meta={{
                month: {
                  alias: '月份',
                },
                avgScore: {
                  alias: '平均评分',
                },
              }}
            />
          </Card>
        </Col>
      </Row>

      {/* 地区详细分析 */}
      <Card title="地区分析详情" style={{ marginBottom: 24 }}>
        <Row gutter={16}>
          {mockRegionAnalysis.map((region, index) => (
            <Col span={6} key={index}>
              <Card size="small">
                <div style={{ textAlign: 'center' }}>
                  <Title level={4}>{region.region}</Title>
                  <Row gutter={8}>
                    <Col span={12}>
                      <Statistic
                        title="客户数"
                        value={region.customerCount}
                        valueStyle={{ fontSize: '16px' }}
                      />
                    </Col>
                    <Col span={12}>
                      <Statistic
                        title="平均评分"
                        value={region.avgValueScore}
                        valueStyle={{ fontSize: '16px' }}
                      />
                    </Col>
                  </Row>
                  <Divider style={{ margin: '8px 0' }} />
                  <Row gutter={8}>
                    <Col span={12}>
                      <Statistic
                        title="转化率"
                        value={Math.round(region.conversionRate * 100)}
                        suffix="%"
                        valueStyle={{ fontSize: '14px' }}
                      />
                    </Col>
                    <Col span={12}>
                      <Statistic
                        title="增长率"
                        value={Math.round(region.growthRate * 100)}
                        suffix="%"
                        valueStyle={{ 
                          fontSize: '14px',
                          color: region.growthRate > 0.15 ? '#3f8600' : '#cf1322'
                        }}
                        prefix={region.growthRate > 0.15 ? <RiseOutlined /> : <FallOutlined />}
                      />
                    </Col>
                  </Row>
                </div>
              </Card>
            </Col>
          ))}
        </Row>
      </Card>

      {/* 客户价值详细分析表 */}
      <Card title="客户价值详细分析">
        <Alert
          message="价值评分说明"
          description="综合评分由询盘活跃度、产品价值度、公司实力度三个维度计算得出，分数越高表示客户价值越大。"
          type="info"
          showIcon
          style={{ marginBottom: 16 }}
        />
        <Table
          columns={valueColumns}
          dataSource={mockCustomerMetrics}
          rowKey="customerId"
          loading={loading}
          scroll={{ x: 1200 }}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
          }}
        />
      </Card>

      {/* 客户画像模态框 */}
      <Modal
        title="客户画像分析"
        open={profileModalVisible}
        onCancel={() => console.log('关闭客户画像弹窗')}
        footer={null}
        width={1000}
      >
        {selectedCustomerProfile && (
          <div>
            <Row gutter={16}>
              <Col span={12}>
                <Card title="基本信息" size="small" style={{ marginBottom: 16 }}>
                  <Descriptions column={1} size="small">
                    <Descriptions.Item label="客户姓名">{selectedCustomerProfile.basicInfo.name}</Descriptions.Item>
                    <Descriptions.Item label="公司名称">{selectedCustomerProfile.basicInfo.company}</Descriptions.Item>
                    <Descriptions.Item label="所在国家">{selectedCustomerProfile.basicInfo.country}</Descriptions.Item>
                    <Descriptions.Item label="所属行业">{selectedCustomerProfile.basicInfo.industry}</Descriptions.Item>
                    <Descriptions.Item label="公司规模">{selectedCustomerProfile.basicInfo.companySize}</Descriptions.Item>
                  </Descriptions>
                </Card>

                <Card title="行为画像" size="small" style={{ marginBottom: 16 }}>
                  <Descriptions column={1} size="small">
                    <Descriptions.Item label="询盘频率">{selectedCustomerProfile.behaviorProfile.inquiryFrequency} 次/月</Descriptions.Item>
                    <Descriptions.Item label="平均响应时间">{selectedCustomerProfile.behaviorProfile.avgResponseTime} 小时</Descriptions.Item>
                    <Descriptions.Item label="偏好联系时间">{selectedCustomerProfile.behaviorProfile.preferredContactTime}</Descriptions.Item>
                    <Descriptions.Item label="沟通风格">{selectedCustomerProfile.behaviorProfile.communicationStyle}</Descriptions.Item>
                    <Descriptions.Item label="决策速度">{selectedCustomerProfile.behaviorProfile.decisionSpeed}</Descriptions.Item>
                  </Descriptions>
                </Card>
              </Col>
              <Col span={12}>
                <Card title="需求画像" size="small" style={{ marginBottom: 16 }}>
                  <Descriptions column={1} size="small">
                    <Descriptions.Item label="主要产品">
                      {selectedCustomerProfile.demandProfile.primaryProducts.map(product => (
                        <Tag key={product} style={{ margin: '2px' }}>{product}</Tag>
                      ))}
                    </Descriptions.Item>
                    <Descriptions.Item label="价格区间">{selectedCustomerProfile.demandProfile.priceRange}</Descriptions.Item>
                    <Descriptions.Item label="质量要求">{selectedCustomerProfile.demandProfile.qualityRequirement}</Descriptions.Item>
                    <Descriptions.Item label="采购量级">{selectedCustomerProfile.demandProfile.volumeRequirement}</Descriptions.Item>
                    <Descriptions.Item label="季节性">
                      {selectedCustomerProfile.demandProfile.seasonality.map(season => (
                        <Tag key={season} color="blue" style={{ margin: '2px' }}>{season}</Tag>
                      ))}
                    </Descriptions.Item>
                  </Descriptions>
                </Card>

                <Card title="风险画像" size="small" style={{ marginBottom: 16 }}>
                  <Descriptions column={1} size="small">
                    <Descriptions.Item label="付款历史">
                      <Tag color="green">{selectedCustomerProfile.riskProfile.paymentHistory}</Tag>
                    </Descriptions.Item>
                    <Descriptions.Item label="信用评级">
                      <Tag color="gold">{selectedCustomerProfile.riskProfile.creditRating}</Tag>
                    </Descriptions.Item>
                    <Descriptions.Item label="市场稳定性">
                      <Tag color="blue">{selectedCustomerProfile.riskProfile.marketStability}</Tag>
                    </Descriptions.Item>
                    <Descriptions.Item label="竞争关系">
                      <Tag color="green">{selectedCustomerProfile.riskProfile.competitorRelation}</Tag>
                    </Descriptions.Item>
                  </Descriptions>
                </Card>
              </Col>
            </Row>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default AnalyticsPage;