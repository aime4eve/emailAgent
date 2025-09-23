/**
 * 需求洞察页面
 * 提供需求趋势分析、产品优化建议、关联分析等功能
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
  Space,
  Tag,
  Button,
  Modal,
  List,
  Typography,
  Progress,
  Alert,
  Tabs,
  Tooltip,
  Badge,
  Divider,
  Timeline,
  Descriptions,
} from 'antd';
import {
  BulbOutlined,
  FireOutlined,
  RiseOutlined,
  FallOutlined,
  ThunderboltOutlined,
  StarOutlined,
  GlobalOutlined,
  LineChartOutlined,
  NodeIndexOutlined,
  CheckCircleOutlined,
  DollarOutlined,
} from '@ant-design/icons';
import { Column, Pie } from '@ant-design/charts';
import type { ColumnsType } from 'antd/es/table';
import dayjs from 'dayjs';

const { RangePicker } = DatePicker;
const { Option } = Select;
const { Title, Text, Paragraph } = Typography;
// const { TabPane } = Tabs; // 已废弃，使用items属性替代

// 需求趋势数据类型
interface DemandTrend {
  id: string;
  demandType: string;
  category: string;
  currentVolume: number;
  previousVolume: number;
  growthRate: number;
  avgPrice: number;
  totalValue: number;
  hotIndex: number;
  seasonality: string[];
  regions: string[];
  predictedGrowth: number;
}

// 产品优化建议类型
interface ProductOptimization {
  id: string;
  productName: string;
  category: string;
  currentPerformance: number;
  optimizationPotential: number;
  suggestions: {
    type: 'feature' | 'price' | 'quality' | 'marketing';
    title: string;
    description: string;
    impact: 'high' | 'medium' | 'low';
    effort: 'high' | 'medium' | 'low';
    priority: number;
  }[];
  marketGap: string;
  competitorAnalysis: string;
}

// 需求关联分析类型
interface DemandAssociation {
  sourceProduct: string;
  targetProduct: string;
  associationStrength: number;
  coOccurrenceRate: number;
  crossSellPotential: number;
  seasonalPattern: string;
}

// 地域需求分析类型
interface RegionalDemand {
  region: string;
  country: string;
  topDemands: {
    product: string;
    volume: number;
    growth: number;
  }[];
  marketCharacteristics: string[];
  opportunities: string[];
}

// 模拟需求趋势数据
const mockDemandTrends: DemandTrend[] = [
  {
    id: '1',
    demandType: '工业自动化设备',
    category: '机械设备',
    currentVolume: 156,
    previousVolume: 128,
    growthRate: 0.22,
    avgPrice: 25000,
    totalValue: 3900000,
    hotIndex: 95,
    seasonality: ['Q1', 'Q4'],
    regions: ['North America', 'Europe', 'Asia'],
    predictedGrowth: 0.28,
  },
  {
    id: '2',
    demandType: '电子元器件',
    category: '电子产品',
    currentVolume: 234,
    previousVolume: 198,
    growthRate: 0.18,
    avgPrice: 1200,
    totalValue: 280800,
    hotIndex: 88,
    seasonality: ['Q2', 'Q3'],
    regions: ['Asia', 'North America'],
    predictedGrowth: 0.15,
  },
  {
    id: '3',
    demandType: '环保材料',
    category: '原材料',
    currentVolume: 89,
    previousVolume: 65,
    growthRate: 0.37,
    avgPrice: 8500,
    totalValue: 756500,
    hotIndex: 92,
    seasonality: ['Q1', 'Q2', 'Q3'],
    regions: ['Europe', 'North America'],
    predictedGrowth: 0.42,
  },
  {
    id: '4',
    demandType: '智能传感器',
    category: '电子产品',
    currentVolume: 178,
    previousVolume: 145,
    growthRate: 0.23,
    avgPrice: 3500,
    totalValue: 623000,
    hotIndex: 90,
    seasonality: ['Q3', 'Q4'],
    regions: ['Asia', 'Europe'],
    predictedGrowth: 0.25,
  },
];

// 模拟产品优化建议数据
const mockOptimizations: ProductOptimization[] = [
  {
    id: '1',
    productName: '工业控制器X1',
    category: '工业自动化',
    currentPerformance: 72,
    optimizationPotential: 85,
    suggestions: [
      {
        type: 'feature',
        title: '增加无线连接功能',
        description: '添加WiFi和蓝牙连接，提升产品智能化水平',
        impact: 'high',
        effort: 'medium',
        priority: 1,
      },
      {
        type: 'price',
        title: '优化定价策略',
        description: '根据市场分析，建议价格调整至$22,000-$28,000区间',
        impact: 'medium',
        effort: 'low',
        priority: 2,
      },
      {
        type: 'quality',
        title: '提升耐用性',
        description: '改进材料和工艺，延长产品使用寿命至10年以上',
        impact: 'high',
        effort: 'high',
        priority: 3,
      },
    ],
    marketGap: '市场缺乏高性价比的中端工业控制器产品',
    competitorAnalysis: '主要竞争对手在智能化功能方面存在不足',
  },
  {
    id: '2',
    productName: '环保过滤材料M2',
    category: '环保材料',
    currentPerformance: 68,
    optimizationPotential: 90,
    suggestions: [
      {
        type: 'feature',
        title: '提升过滤效率',
        description: '采用新型纳米材料，将过滤效率提升至99.9%',
        impact: 'high',
        effort: 'high',
        priority: 1,
      },
      {
        type: 'marketing',
        title: '强化环保认证',
        description: '获得更多国际环保认证，提升市场认可度',
        impact: 'medium',
        effort: 'medium',
        priority: 2,
      },
    ],
    marketGap: '高效环保过滤材料需求快速增长，供应不足',
    competitorAnalysis: '竞争对手产品在过滤效率和环保性能方面有待提升',
  },
];

// 模拟需求关联数据
const mockAssociations: DemandAssociation[] = [
  {
    sourceProduct: '工业控制器',
    targetProduct: '传感器模块',
    associationStrength: 0.85,
    coOccurrenceRate: 0.78,
    crossSellPotential: 0.82,
    seasonalPattern: '同步增长',
  },
  {
    sourceProduct: '电机驱动器',
    targetProduct: '编码器',
    associationStrength: 0.79,
    coOccurrenceRate: 0.72,
    crossSellPotential: 0.75,
    seasonalPattern: '滞后1个月',
  },
  {
    sourceProduct: '环保材料',
    targetProduct: '检测设备',
    associationStrength: 0.68,
    coOccurrenceRate: 0.65,
    crossSellPotential: 0.70,
    seasonalPattern: '领先2周',
  },
];

// 模拟地域需求数据
const mockRegionalDemands: RegionalDemand[] = [
  {
    region: 'North America',
    country: 'United States',
    topDemands: [
      { product: '工业自动化设备', volume: 89, growth: 0.25 },
      { product: '智能传感器', volume: 67, growth: 0.18 },
      { product: '环保材料', volume: 45, growth: 0.35 },
    ],
    marketCharacteristics: ['技术导向', '质量要求高', '价格敏感度中等'],
    opportunities: ['智能制造升级', '环保政策推动', '基础设施更新'],
  },
  {
    region: 'Europe',
    country: 'Germany',
    topDemands: [
      { product: '环保材料', volume: 78, growth: 0.42 },
      { product: '工业自动化设备', volume: 56, growth: 0.20 },
      { product: '精密仪器', volume: 34, growth: 0.15 },
    ],
    marketCharacteristics: ['环保优先', '技术标准严格', '长期合作偏好'],
    opportunities: ['绿色转型', '工业4.0', '可持续发展'],
  },
  {
    region: 'Asia',
    country: 'China',
    topDemands: [
      { product: '电子元器件', volume: 156, growth: 0.28 },
      { product: '智能传感器', volume: 89, growth: 0.32 },
      { product: '工业控制器', volume: 67, growth: 0.22 },
    ],
    marketCharacteristics: ['成本敏感', '批量采购', '快速决策'],
    opportunities: ['制造业升级', '新基建投资', '出口贸易增长'],
  },
];

/**
 * 需求洞察页面组件
 */
const InsightsPage: React.FC = () => {
  const [loading] = useState(false);
  const [selectedPeriod, setSelectedPeriod] = useState<[dayjs.Dayjs, dayjs.Dayjs] | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedRegion, setSelectedRegion] = useState<string>('all');
  const [optimizationModalVisible] = useState(false);
  const [selectedOptimization] = useState<ProductOptimization | null>(null);

  // 获取趋势颜色
  const getTrendColor = (growth: number) => {
    if (growth > 0.2) return '#52c41a';
    if (growth > 0.1) return '#1890ff';
    if (growth > 0) return '#faad14';
    return '#f5222d';
  };

  // 获取热度颜色
  const getHotColor = (hotIndex: number) => {
    if (hotIndex >= 90) return '#ff4d4f';
    if (hotIndex >= 80) return '#ff7a45';
    if (hotIndex >= 70) return '#ffa940';
    return '#d9d9d9';
  };

  // 需求趋势表格列定义
  const trendColumns: ColumnsType<DemandTrend> = [
    {
      title: '需求类型',
      dataIndex: 'demandType',
      key: 'demandType',
      width: 200,
      render: (text, record) => (
        <div>
          <div style={{ fontWeight: 'bold' }}>{text}</div>
          <div style={{ fontSize: '12px', color: '#666' }}>{record.category}</div>
        </div>
      ),
    },
    {
      title: '当前询盘量',
      dataIndex: 'currentVolume',
      key: 'currentVolume',
      width: 120,
      render: (volume) => (
        <div style={{ textAlign: 'center', fontWeight: 'bold' }}>
          {volume}
        </div>
      ),
    },
    {
      title: '增长趋势',
      key: 'growth',
      width: 150,
      render: (_, record) => (
        <div>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: 4 }}>
            {record.growthRate > 0 ? (
              <RiseOutlined style={{ color: '#52c41a', marginRight: 4 }} />
            ) : (
              <FallOutlined style={{ color: '#f5222d', marginRight: 4 }} />
            )}
            <span style={{ color: getTrendColor(record.growthRate), fontWeight: 'bold' }}>
              {(record.growthRate * 100).toFixed(1)}%
            </span>
          </div>
          <Progress 
            percent={Math.abs(record.growthRate * 100)} 
            size="small" 
            strokeColor={getTrendColor(record.growthRate)}
            showInfo={false}
          />
        </div>
      ),
    },
    {
      title: '热度指数',
      dataIndex: 'hotIndex',
      key: 'hotIndex',
      width: 120,
      render: (hotIndex) => (
        <div style={{ textAlign: 'center' }}>
          <div style={{ 
            color: getHotColor(hotIndex), 
            fontWeight: 'bold',
            fontSize: '16px'
          }}>
            {hotIndex}
          </div>
          <div style={{ fontSize: '12px' }}>
            {hotIndex >= 90 && <><FireOutlined style={{ color: '#ff4d4f' }} /> 极热</>}
            {hotIndex >= 80 && hotIndex < 90 && <><ThunderboltOutlined style={{ color: '#ff7a45' }} /> 很热</>}
            {hotIndex >= 70 && hotIndex < 80 && <><StarOutlined style={{ color: '#ffa940' }} /> 较热</>}
            {hotIndex < 70 && <>一般</>}
          </div>
        </div>
      ),
    },
    {
      title: '平均价格',
      dataIndex: 'avgPrice',
      key: 'avgPrice',
      width: 120,
      render: (price) => (
        <div style={{ textAlign: 'right' }}>
          ${price.toLocaleString()}
        </div>
      ),
    },
    {
      title: '总价值',
      dataIndex: 'totalValue',
      key: 'totalValue',
      width: 150,
      render: (value) => (
        <div style={{ textAlign: 'right', fontWeight: 'bold' }}>
          ${value.toLocaleString()}
        </div>
      ),
    },
    {
      title: '季节性',
      dataIndex: 'seasonality',
      key: 'seasonality',
      width: 120,
      render: (seasons: string[]) => (
        <div>
          {seasons.map(season => (
            <Tag key={season} color="blue">{season}</Tag>
          ))}
        </div>
      ),
    },
    {
      title: '主要地区',
      dataIndex: 'regions',
      key: 'regions',
      width: 150,
      render: (regions: string[]) => (
        <div>
          {regions.slice(0, 2).map(region => (
            <Tag key={region}>{region}</Tag>
          ))}
          {regions.length > 2 && (
            <Tooltip title={regions.slice(2).join(', ')}>
              <Tag>+{regions.length - 2}</Tag>
            </Tooltip>
          )}
        </div>
      ),
    },
    {
      title: '预测增长',
      dataIndex: 'predictedGrowth',
      key: 'predictedGrowth',
      width: 120,
      render: (growth) => (
        <div style={{ textAlign: 'center' }}>
          <div style={{ color: getTrendColor(growth), fontWeight: 'bold' }}>
            {(growth * 100).toFixed(1)}%
          </div>
          <div style={{ fontSize: '12px', color: '#666' }}>下季度</div>
        </div>
      ),
    },
  ];

  // 产品优化建议表格列定义
  const optimizationColumns: ColumnsType<ProductOptimization> = [
    {
      title: '产品名称',
      dataIndex: 'productName',
      key: 'productName',
      width: 200,
      render: (text, record) => (
        <div>
          <div style={{ fontWeight: 'bold' }}>{text}</div>
          <div style={{ fontSize: '12px', color: '#666' }}>{record.category}</div>
        </div>
      ),
    },
    {
      title: '当前表现',
      dataIndex: 'currentPerformance',
      key: 'currentPerformance',
      width: 120,
      render: (performance) => (
        <Progress 
          percent={performance} 
          size="small" 
          strokeColor={performance >= 80 ? '#52c41a' : performance >= 60 ? '#1890ff' : '#faad14'}
        />
      ),
    },
    {
      title: '优化潜力',
      dataIndex: 'optimizationPotential',
      key: 'optimizationPotential',
      width: 120,
      render: (potential) => (
        <Progress 
          percent={potential} 
          size="small" 
          strokeColor="#722ed1"
        />
      ),
    },
    {
      title: '建议数量',
      key: 'suggestionCount',
      width: 100,
      render: (_, record) => (
        <div style={{ textAlign: 'center' }}>
          <Badge count={record.suggestions.length} style={{ backgroundColor: '#52c41a' }} />
        </div>
      ),
    },
    {
      title: '市场机会',
      dataIndex: 'marketGap',
      key: 'marketGap',
      ellipsis: true,
      render: (text) => (
        <Tooltip title={text}>
          <Text ellipsis>{text}</Text>
        </Tooltip>
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 120,
      render: (_, record) => (
        <Button 
          type="primary" 
          size="small"
          onClick={() => {
            // setSelectedOptimization(record);
            // setOptimizationModalVisible(true);
            console.log('查看优化详情:', record);
          }}
        >
          查看详情
        </Button>
      ),
    },
  ];

  // 需求关联表格列定义
  const associationColumns: ColumnsType<DemandAssociation> = [
    {
      title: '产品关联',
      key: 'association',
      width: 250,
      render: (_, record) => (
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <Tag color="blue">{record.sourceProduct}</Tag>
          <NodeIndexOutlined style={{ margin: '0 8px', color: '#1890ff' }} />
          <Tag color="green">{record.targetProduct}</Tag>
        </div>
      ),
    },
    {
      title: '关联强度',
      dataIndex: 'associationStrength',
      key: 'associationStrength',
      width: 150,
      render: (strength) => (
        <div>
          <Progress 
            percent={strength * 100} 
            size="small" 
            strokeColor="#1890ff"
          />
          <div style={{ textAlign: 'center', fontSize: '12px', marginTop: 4 }}>
            {(strength * 100).toFixed(1)}%
          </div>
        </div>
      ),
    },
    {
      title: '共现率',
      dataIndex: 'coOccurrenceRate',
      key: 'coOccurrenceRate',
      width: 120,
      render: (rate) => (
        <div style={{ textAlign: 'center', fontWeight: 'bold' }}>
          {(rate * 100).toFixed(1)}%
        </div>
      ),
    },
    {
      title: '交叉销售潜力',
      dataIndex: 'crossSellPotential',
      key: 'crossSellPotential',
      width: 150,
      render: (potential) => (
        <div>
          <Progress 
            percent={potential * 100} 
            size="small" 
            strokeColor="#52c41a"
          />
          <div style={{ textAlign: 'center', fontSize: '12px', marginTop: 4 }}>
            {(potential * 100).toFixed(1)}%
          </div>
        </div>
      ),
    },
    {
      title: '季节模式',
      dataIndex: 'seasonalPattern',
      key: 'seasonalPattern',
      width: 120,
      render: (pattern) => (
        <Tag color={pattern.includes('同步') ? 'green' : pattern.includes('领先') ? 'blue' : 'orange'}>
          {pattern}
        </Tag>
      ),
    },
  ];

  // 趋势图表数据
  const trendChartData = mockDemandTrends.map(item => ({
    demandType: item.demandType,
    currentVolume: item.currentVolume,
    previousVolume: item.previousVolume,
    growthRate: item.growthRate * 100,
  }));

  // 热度分布数据
  const hotIndexData = mockDemandTrends.map(item => ({
    demandType: item.demandType,
    hotIndex: item.hotIndex,
    category: item.category,
  }));

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
              <Text strong>产品类别:</Text>
              <Select
                value={selectedCategory}
                onChange={setSelectedCategory}
                style={{ width: 120 }}
              >
                <Option value="all">全部类别</Option>
                <Option value="机械设备">机械设备</Option>
                <Option value="电子产品">电子产品</Option>
                <Option value="原材料">原材料</Option>
              </Select>
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
              title="热门需求类型"
              value={mockDemandTrends.filter(d => d.hotIndex >= 90).length}
              prefix={<FireOutlined />}
              suffix="个"
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="平均增长率"
              value={Math.round((mockDemandTrends.reduce((sum, d) => sum + d.growthRate, 0) / mockDemandTrends.length) * 100)}
              prefix={<RiseOutlined />}
              suffix="%"
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="总需求价值"
              value={mockDemandTrends.reduce((sum, d) => sum + d.totalValue, 0)}
              prefix={<DollarOutlined />}
              formatter={(value) => `$${Number(value || 0).toLocaleString()}`}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="优化机会"
              value={mockOptimizations.length}
              prefix={<BulbOutlined />}
              suffix="个产品"
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 主要内容选项卡 */}
      <Tabs 
        defaultActiveKey="trends" 
        type="card"
        items={[
          {
            key: 'trends',
            label: <><LineChartOutlined /> 需求趋势分析</>,
            children: (
              <div>
                {/* 趋势图表 */}
                <Row gutter={16} style={{ marginBottom: 24 }}>
                  <Col span={12}>
                    <Card title="需求量对比">
                      <Column
                        data={trendChartData}
                        xField="demandType"
                        yField="currentVolume"
                        columnStyle={{
                          radius: [4, 4, 0, 0],
                        }}
                        meta={{
                          demandType: {
                            alias: '需求类型',
                          },
                          currentVolume: {
                            alias: '当前询盘量',
                          },
                        }}
                      />
                    </Card>
                  </Col>
                  <Col span={12}>
                    <Card title="热度分布">
                      <Pie
                        data={hotIndexData}
                        angleField="hotIndex"
                        colorField="demandType"
                        radius={0.8}
                        label={false}
                        interactions={[{ type: 'element-active' }]}
                      />
                    </Card>
                  </Col>
                </Row>

                {/* 需求趋势详细表格 */}
                <Card title="需求趋势详细分析">
                  <Alert
                    message="趋势分析说明"
                    description="基于历史询盘数据和市场分析，识别热门需求类型和增长趋势，为产品规划和市场策略提供数据支持。"
                    type="info"
                    showIcon
                    style={{ marginBottom: 16 }}
                  />
                  <Table
                    columns={trendColumns}
                    dataSource={mockDemandTrends}
                    rowKey="id"
                    loading={loading}
                    scroll={{ x: 1200 }}
                    pagination={{
                      pageSize: 10,
                      showSizeChanger: true,
                      showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
                    }}
                  />
                </Card>
              </div>
            )
          },

          {
            key: 'optimization',
            label: <><BulbOutlined /> 产品优化建议</>,
            children: (
              <Card title="产品优化机会分析">
                <Alert
                  message="优化建议说明"
                  description="基于市场需求分析和竞争对手研究，为现有产品提供优化建议，提升市场竞争力和客户满意度。"
                  type="info"
                  showIcon
                  style={{ marginBottom: 16 }}
                />
                <Table
                  columns={optimizationColumns}
                  dataSource={mockOptimizations}
                  rowKey="id"
                  loading={loading}
                  pagination={{
                    pageSize: 10,
                    showSizeChanger: true,
                    showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
                  }}
                />
              </Card>
            )
          },

          {
            key: 'association',
            label: <><NodeIndexOutlined /> 需求关联分析</>,
            children: (
              <Card title="产品需求关联性分析">
                <Alert
                  message="关联分析说明"
                  description="分析不同产品之间的需求关联性，识别交叉销售机会和产品组合策略。"
                  type="info"
                  showIcon
                  style={{ marginBottom: 16 }}
                />
                <Table
                  columns={associationColumns}
                  dataSource={mockAssociations}
                  rowKey={(record) => `${record.sourceProduct}-${record.targetProduct}`}
                  loading={loading}
                  pagination={{
                    pageSize: 10,
                    showSizeChanger: true,
                    showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
                  }}
                />
              </Card>
            )
          },

          {
            key: 'regional',
            label: <><GlobalOutlined /> 地域需求分析</>,
            children: (
              <Row gutter={16}>
                {mockRegionalDemands.map((region, index) => (
                  <Col span={8} key={index}>
                    <Card 
                      title={`${region.region} - ${region.country}`}
                      style={{ marginBottom: 16 }}
                    >
                      <div style={{ marginBottom: 16 }}>
                        <Title level={5}>热门需求</Title>
                        <List
                          size="small"
                          dataSource={region.topDemands}
                          renderItem={(item) => (
                            <List.Item>
                              <div style={{ width: '100%' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                  <span>{item.product}</span>
                                  <div>
                                    <Badge count={item.volume} style={{ backgroundColor: '#52c41a', marginRight: 8 }} />
                                    <Tag color={getTrendColor(item.growth)}>
                                      {(item.growth * 100).toFixed(1)}%
                                    </Tag>
                                  </div>
                                </div>
                              </div>
                            </List.Item>
                          )}
                        />
                      </div>
                      
                      <Divider />
                      
                      <div style={{ marginBottom: 16 }}>
                        <Title level={5}>市场特征</Title>
                        <div>
                          {region.marketCharacteristics.map(char => (
                            <Tag key={char} style={{ margin: '2px' }}>{char}</Tag>
                          ))}
                        </div>
                      </div>
                      
                      <div>
                        <Title level={5}>市场机会</Title>
                        <List
                          size="small"
                          dataSource={region.opportunities}
                          renderItem={(item) => (
                            <List.Item>
                              <CheckCircleOutlined style={{ color: '#52c41a', marginRight: 8 }} />
                              {item}
                            </List.Item>
                          )}
                        />
                      </div>
                    </Card>
                  </Col>
                ))}
              </Row>
            )
          }
        ]}
      />

      {/* 产品优化详情模态框 */}
      <Modal
        title="产品优化建议详情"
        open={optimizationModalVisible}
        onCancel={() => console.log('关闭优化建议弹窗')}
        footer={null}
        width={800}
      >
        {selectedOptimization && (
          <div>
            <Row gutter={16} style={{ marginBottom: 24 }}>
              <Col span={12}>
                <Card title="产品概况" size="small">
                  <Descriptions column={1} size="small">
                    <Descriptions.Item label="产品名称">{selectedOptimization.productName}</Descriptions.Item>
                    <Descriptions.Item label="产品类别">{selectedOptimization.category}</Descriptions.Item>
                    <Descriptions.Item label="当前表现">
                      <Progress percent={selectedOptimization.currentPerformance} size="small" />
                    </Descriptions.Item>
                    <Descriptions.Item label="优化潜力">
                      <Progress percent={selectedOptimization.optimizationPotential} size="small" strokeColor="#722ed1" />
                    </Descriptions.Item>
                  </Descriptions>
                </Card>
              </Col>
              <Col span={12}>
                <Card title="市场分析" size="small">
                  <div style={{ marginBottom: 12 }}>
                    <Text strong>市场机会：</Text>
                    <Paragraph>{selectedOptimization.marketGap}</Paragraph>
                  </div>
                  <div>
                    <Text strong>竞争分析：</Text>
                    <Paragraph>{selectedOptimization.competitorAnalysis}</Paragraph>
                  </div>
                </Card>
              </Col>
            </Row>
            
            <Card title="优化建议" size="small">
              <Timeline>
                {selectedOptimization.suggestions
                  .sort((a, b) => a.priority - b.priority)
                  .map((suggestion, index) => (
                    <Timeline.Item
                      key={index}
                      color={suggestion.impact === 'high' ? 'red' : suggestion.impact === 'medium' ? 'blue' : 'green'}
                    >
                      <div>
                        <div style={{ display: 'flex', alignItems: 'center', marginBottom: 8 }}>
                          <Title level={5} style={{ margin: 0, marginRight: 12 }}>
                            {suggestion.title}
                          </Title>
                          <Tag color={suggestion.impact === 'high' ? 'red' : suggestion.impact === 'medium' ? 'blue' : 'green'}>
                            {suggestion.impact === 'high' ? '高影响' : suggestion.impact === 'medium' ? '中影响' : '低影响'}
                          </Tag>
                          <Tag color={suggestion.effort === 'high' ? 'red' : suggestion.effort === 'medium' ? 'blue' : 'green'}>
                            {suggestion.effort === 'high' ? '高投入' : suggestion.effort === 'medium' ? '中投入' : '低投入'}
                          </Tag>
                        </div>
                        <Paragraph>{suggestion.description}</Paragraph>
                      </div>
                    </Timeline.Item>
                  ))
                }
              </Timeline>
            </Card>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default InsightsPage;