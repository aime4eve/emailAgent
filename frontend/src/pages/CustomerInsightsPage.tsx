/**
 * 客户洞察页面
 * 提供客户需求分析、购买意向识别、决策链分析等功能
 */

import React, { useState, useEffect } from 'react';
import {
  Card,
  Row,
  Col,
  Statistic,
  Table,
  Space,
  Tag,
  Button,
  List,
  Typography,
  Progress,
  Alert,
  Tabs,
  Input,
  message,
  Empty,
  Badge,
  Modal,
  Descriptions,
  Timeline,
} from 'antd';
import {
  UserOutlined,
  TeamOutlined,
  TrophyOutlined,
  SearchOutlined,
  BulbOutlined,
  DollarOutlined,
} from '@ant-design/icons';
import { Column, Pie } from '@ant-design/charts';
import type { ColumnsType } from 'antd/es/table';
import { insightsApi } from '../services/insightsApi';

const { Title, Paragraph } = Typography;
const { TextArea } = Input;

// 客户洞察数据类型
interface CustomerInsightData {
  customer_id: string;
  customer_name: string;
  company: string;
  email: string;
  region: string;
  total_interactions: number;
  purchase_intent_score: number;
  intent_level: 'high' | 'medium' | 'low';
  key_needs: string[];
  decision_stage: string;
  last_interaction: string;
  potential_value: number;
}

// 需求分析数据类型
interface NeedAnalysis {
  need_type: string;
  frequency: number;
  urgency: 'high' | 'medium' | 'low';
  satisfaction_level: number;
  related_products: string[];
}



const CustomerInsightsPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [customerInsights, setCustomerInsights] = useState<CustomerInsightData[]>([]);
  const [needsAnalysis, setNeedsAnalysis] = useState<NeedAnalysis[]>([]);
  const [analysisText, setAnalysisText] = useState('');
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedCustomer, setSelectedCustomer] = useState<string | null>(null);
  const [customerDetailVisible, setCustomerDetailVisible] = useState(false);

  // 模拟客户洞察数据
  const mockCustomerInsights: CustomerInsightData[] = [
    {
      customer_id: 'C001',
      customer_name: 'John Smith',
      company: 'TechCorp Inc.',
      email: 'john.smith@techcorp.com',
      region: 'North America',
      total_interactions: 15,
      purchase_intent_score: 85,
      intent_level: 'high',
      key_needs: ['工业自动化', '质量控制', '成本优化'],
      decision_stage: '方案评估',
      last_interaction: '2024-01-15',
      potential_value: 250000,
    },
    {
      customer_id: 'C002',
      customer_name: 'Maria Garcia',
      company: 'Global Manufacturing',
      email: 'maria.garcia@globalmfg.com',
      region: 'Europe',
      total_interactions: 8,
      purchase_intent_score: 65,
      intent_level: 'medium',
      key_needs: ['环保材料', '供应链优化'],
      decision_stage: '需求确认',
      last_interaction: '2024-01-12',
      potential_value: 180000,
    },
    {
      customer_id: 'C003',
      customer_name: 'Li Wei',
      company: 'Asia Electronics',
      email: 'li.wei@asiaelec.com',
      region: 'Asia',
      total_interactions: 12,
      purchase_intent_score: 72,
      intent_level: 'high',
      key_needs: ['电子元器件', '技术支持', '批量采购'],
      decision_stage: '价格谈判',
      last_interaction: '2024-01-14',
      potential_value: 320000,
    },
  ];

  // 模拟需求分析数据
  const mockNeedsAnalysis: NeedAnalysis[] = [
    {
      need_type: '工业自动化设备',
      frequency: 45,
      urgency: 'high',
      satisfaction_level: 68,
      related_products: ['控制器', '传感器', '执行器'],
    },
    {
      need_type: '环保材料',
      frequency: 32,
      urgency: 'medium',
      satisfaction_level: 72,
      related_products: ['可降解塑料', '回收材料', '绿色涂料'],
    },
    {
      need_type: '电子元器件',
      frequency: 38,
      urgency: 'high',
      satisfaction_level: 75,
      related_products: ['芯片', '电容', '电阻'],
    },
  ];

  useEffect(() => {
    loadCustomerInsights();
  }, []);

  /**
   * 加载客户洞察数据
   */
  const loadCustomerInsights = async () => {
    setLoading(true);
    try {
      // 尝试从API获取数据
      const response = await insightsApi.getCustomerInsights();
      if (response.success && response.data) {
        // 处理API数据
        console.log('客户洞察数据:', response.data);
      }
    } catch (error) {
      console.log('使用模拟数据');
    } finally {
      // 使用模拟数据
      setCustomerInsights(mockCustomerInsights);
      setNeedsAnalysis(mockNeedsAnalysis);
      setLoading(false);
    }
  };

  /**
   * 分析客户需求
   */
  const analyzeCustomerNeeds = async () => {
    if (!analysisText.trim()) {
      message.warning('请输入要分析的邮件内容');
      return;
    }

    setLoading(true);
    try {
      const response = await insightsApi.analyzeCustomerNeeds(analysisText);
      if (response.success) {
        message.success('客户需求分析完成');
        console.log('分析结果:', response.data);
        // 更新界面数据
      } else {
        message.error('分析失败: ' + response.message);
      }
    } catch (error) {
      message.error('分析过程中出现错误');
      console.error('分析错误:', error);
    } finally {
      setLoading(false);
    }
  };

  // 客户表格列定义
  const customerColumns: ColumnsType<CustomerInsightData> = [
    {
      title: '客户信息',
      key: 'customer',
      render: (_, record) => (
        <div>
          <div style={{ fontWeight: 'bold' }}>{record.customer_name}</div>
          <div style={{ color: '#666', fontSize: '12px' }}>{record.company}</div>
          <div style={{ color: '#999', fontSize: '11px' }}>{record.email}</div>
        </div>
      ),
    },
    {
      title: '地区',
      dataIndex: 'region',
      key: 'region',
      render: (region) => <Tag color="blue">{region}</Tag>,
    },
    {
      title: '购买意向',
      key: 'intent',
      render: (_, record) => (
        <div>
          <Progress
            percent={record.purchase_intent_score}
            size="small"
            status={record.intent_level === 'high' ? 'active' : 'normal'}
          />
          <Tag
            color={
              record.intent_level === 'high'
                ? 'red'
                : record.intent_level === 'medium'
                ? 'orange'
                : 'default'
            }
          >
            {record.intent_level === 'high' ? '高' : record.intent_level === 'medium' ? '中' : '低'}
          </Tag>
        </div>
      ),
    },
    {
      title: '关键需求',
      dataIndex: 'key_needs',
      key: 'key_needs',
      render: (needs: string[]) => (
        <div>
          {needs.slice(0, 2).map((need, index) => (
            <Tag key={index} style={{ marginBottom: 2 }}>
              {need}
            </Tag>
          ))}
          {needs.length > 2 && <Tag>+{needs.length - 2}</Tag>}
        </div>
      ),
    },
    {
      title: '决策阶段',
      dataIndex: 'decision_stage',
      key: 'decision_stage',
      render: (stage) => <Badge status="processing" text={stage} />,
    },
    {
      title: '潜在价值',
      dataIndex: 'potential_value',
      key: 'potential_value',
      render: (value) => (
        <span style={{ color: '#52c41a', fontWeight: 'bold' }}>
          ${value.toLocaleString()}
        </span>
      ),
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Button
          type="link"
          onClick={() => {
            setSelectedCustomer(record.customer_id);
            setCustomerDetailVisible(true);
          }}
        >
          详细分析
        </Button>
      ),
    },
  ];

  // 需求分析图表数据
  const needsChartData = needsAnalysis.map(item => ({
    type: item.need_type,
    value: item.frequency,
    urgency: item.urgency,
  }));

  // 购买意向分布数据
  const intentDistribution = [
    { type: '高意向', value: customerInsights.filter(c => c.intent_level === 'high').length },
    { type: '中意向', value: customerInsights.filter(c => c.intent_level === 'medium').length },
    { type: '低意向', value: customerInsights.filter(c => c.intent_level === 'low').length },
  ];

  const tabItems = [
    {
      key: 'overview',
      label: '概览',
      children: (
        <div>
          {/* 统计卡片 */}
          <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title="总客户数"
                  value={customerInsights.length}
                  prefix={<UserOutlined />}
                  valueStyle={{ color: '#1890ff' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title="高意向客户"
                  value={customerInsights.filter(c => c.intent_level === 'high').length}
                  prefix={<TrophyOutlined />}
                  valueStyle={{ color: '#52c41a' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title="潜在总价值"
                  value={customerInsights.reduce((sum, c) => sum + c.potential_value, 0)}
                  prefix={<DollarOutlined />}
                  formatter={(value) => `$${Number(value).toLocaleString()}`}
                  valueStyle={{ color: '#faad14' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title="平均意向分数"
                  value={Math.round(
                    customerInsights.reduce((sum, c) => sum + c.purchase_intent_score, 0) /
                    customerInsights.length
                  )}
                  suffix="%"
                  prefix={<BulbOutlined />}
                  valueStyle={{ color: '#722ed1' }}
                />
              </Card>
            </Col>
          </Row>

          {/* 图表区域 */}
          <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
            <Col xs={24} lg={12}>
              <Card title="需求类型分析" extra={<BulbOutlined />}>
                <Column
                  data={needsChartData}
                  xField="type"
                  yField="value"
                  colorField="urgency"
                  color={['#ff4d4f', '#faad14', '#52c41a']}
                  height={300}
                />
              </Card>
            </Col>
            <Col xs={24} lg={12}>
              <Card title="购买意向分布" extra={<TeamOutlined />}>
                <Pie
                  data={intentDistribution}
                  angleField="value"
                  colorField="type"
                  radius={0.8}
                  height={300}
                  color={['#52c41a', '#faad14', '#d9d9d9']}
                />
              </Card>
            </Col>
          </Row>

          {/* 客户列表 */}
          <Card title="客户洞察列表" extra={<TeamOutlined />}>
            <Table
              columns={customerColumns}
              dataSource={customerInsights}
              rowKey="customer_id"
              loading={loading}
              pagination={{
                pageSize: 10,
                showSizeChanger: true,
                showQuickJumper: true,
                showTotal: (total) => `共 ${total} 条记录`,
              }}
            />
          </Card>
        </div>
      ),
    },
    {
      key: 'analysis',
      label: '需求分析',
      children: (
        <div>
          <Card title="邮件内容分析" style={{ marginBottom: 16 }}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <TextArea
                rows={6}
                placeholder="请输入客户邮件内容，系统将自动分析客户需求和购买意向..."
                value={analysisText}
                onChange={(e) => setAnalysisText(e.target.value)}
              />
              <Button
                type="primary"
                icon={<SearchOutlined />}
                onClick={analyzeCustomerNeeds}
                loading={loading}
              >
                分析客户需求
              </Button>
            </Space>
          </Card>

          <Row gutter={[16, 16]}>
            <Col xs={24} lg={12}>
              <Card title="需求频次分析">
                <List
                  dataSource={needsAnalysis}
                  renderItem={(item) => (
                    <List.Item>
                      <List.Item.Meta
                        title={
                          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                            <span>{item.need_type}</span>
                            <Tag
                              color={
                                item.urgency === 'high'
                                  ? 'red'
                                  : item.urgency === 'medium'
                                  ? 'orange'
                                  : 'default'
                              }
                            >
                              {item.urgency === 'high' ? '高' : item.urgency === 'medium' ? '中' : '低'}紧急
                            </Tag>
                          </div>
                        }
                        description={
                          <div>
                            <div>提及频次: {item.frequency} 次</div>
                            <div>满意度: {item.satisfaction_level}%</div>
                            <div style={{ marginTop: 8 }}>
                              相关产品: {item.related_products.map((product, index) => (
                                <Tag key={index}>{product}</Tag>
                              ))}
                            </div>
                          </div>
                        }
                      />
                    </List.Item>
                  )}
                />
              </Card>
            </Col>
            <Col xs={24} lg={12}>
              <Card title="客户决策链分析">
                <Alert
                  message="决策链分析"
                  description="基于邮件交互分析客户内部决策流程和关键决策者"
                  type="info"
                  style={{ marginBottom: 16 }}
                />
                <Empty description="暂无决策链数据" />
              </Card>
            </Col>
          </Row>
        </div>
      ),
    },
  ];

  // 获取选中客户的详细信息
  const getSelectedCustomerDetail = () => {
    return customerInsights.find(customer => customer.customer_id === selectedCustomer);
  };

  const selectedCustomerDetail = getSelectedCustomerDetail();

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <Title level={2}>客户洞察分析</Title>
        <Paragraph>
          通过分析客户邮件内容和交互行为，识别客户需求、评估购买意向、分析决策链，为销售策略提供数据支撑。
        </Paragraph>
      </div>

      <Tabs
        activeKey={activeTab}
        onChange={setActiveTab}
        items={tabItems}
      />

      {/* 客户详细分析模态框 */}
      <Modal
        title="客户详细分析"
        open={customerDetailVisible}
        onCancel={() => {
          setCustomerDetailVisible(false);
          setSelectedCustomer(null);
        }}
        footer={[
          <Button key="close" onClick={() => {
            setCustomerDetailVisible(false);
            setSelectedCustomer(null);
          }}>
            关闭
          </Button>,
        ]}
        width={800}
      >
        {selectedCustomerDetail && (
          <div>
            {/* 基本信息 */}
            <Card title="基本信息" style={{ marginBottom: 16 }}>
              <Descriptions column={2}>
                <Descriptions.Item label="客户姓名">{selectedCustomerDetail.customer_name}</Descriptions.Item>
                <Descriptions.Item label="公司名称">{selectedCustomerDetail.company}</Descriptions.Item>
                <Descriptions.Item label="邮箱地址">{selectedCustomerDetail.email}</Descriptions.Item>
                <Descriptions.Item label="所在地区">
                  <Tag color="blue">{selectedCustomerDetail.region}</Tag>
                </Descriptions.Item>
                <Descriptions.Item label="交互次数">{selectedCustomerDetail.total_interactions} 次</Descriptions.Item>
                <Descriptions.Item label="最后交互">{selectedCustomerDetail.last_interaction}</Descriptions.Item>
              </Descriptions>
            </Card>

            {/* 购买意向分析 */}
            <Card title="购买意向分析" style={{ marginBottom: 16 }}>
              <Row gutter={16}>
                <Col span={12}>
                  <Statistic
                    title="意向评分"
                    value={selectedCustomerDetail.purchase_intent_score}
                    suffix="%"
                    valueStyle={{
                      color: selectedCustomerDetail.intent_level === 'high' ? '#52c41a' : 
                             selectedCustomerDetail.intent_level === 'medium' ? '#faad14' : '#d9d9d9'
                    }}
                  />
                </Col>
                <Col span={12}>
                  <Statistic
                    title="潜在价值"
                    value={selectedCustomerDetail.potential_value}
                    prefix="$"
                    formatter={(value) => Number(value).toLocaleString()}
                    valueStyle={{ color: '#1890ff' }}
                  />
                </Col>
              </Row>
              <div style={{ marginTop: 16 }}>
                <span>意向等级: </span>
                <Tag
                  color={
                    selectedCustomerDetail.intent_level === 'high' ? 'red' :
                    selectedCustomerDetail.intent_level === 'medium' ? 'orange' : 'default'
                  }
                >
                  {selectedCustomerDetail.intent_level === 'high' ? '高意向' :
                   selectedCustomerDetail.intent_level === 'medium' ? '中意向' : '低意向'}
                </Tag>
              </div>
            </Card>

            {/* 关键需求 */}
            <Card title="关键需求分析" style={{ marginBottom: 16 }}>
              <div>
                {selectedCustomerDetail.key_needs.map((need, index) => (
                  <Tag key={index} color="processing" style={{ marginBottom: 8 }}>
                    {need}
                  </Tag>
                ))}
              </div>
            </Card>

            {/* 决策进程 */}
            <Card title="决策进程跟踪">
              <Timeline
                items={[
                  {
                    color: 'green',
                    children: (
                      <div>
                        <div><strong>当前阶段: {selectedCustomerDetail.decision_stage}</strong></div>
                        <div style={{ color: '#666' }}>最后更新: {selectedCustomerDetail.last_interaction}</div>
                      </div>
                    ),
                  },
                  {
                    color: 'blue',
                    children: (
                      <div>
                        <div>需求确认阶段</div>
                        <div style={{ color: '#666' }}>客户明确了具体需求</div>
                      </div>
                    ),
                  },
                  {
                    color: 'gray',
                    children: (
                      <div>
                        <div>初步接触</div>
                        <div style={{ color: '#666' }}>建立了初步联系</div>
                      </div>
                    ),
                  },
                ]}
              />
            </Card>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default CustomerInsightsPage;