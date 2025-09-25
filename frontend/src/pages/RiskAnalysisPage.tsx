/**
 * 风险分析页面
 * 提供信用风险、合规风险、市场风险等分析功能
 */

import React, { useState, useEffect } from 'react';
import {
  Card,
  Row,
  Col,
  Typography,
  Button,
  Table,
  Tag,
  Progress,
  Statistic,
  Alert,
  Space,
  Input,
  message,
  Badge,
  Timeline,
  List,
  Empty,
  Tabs,
  Modal,
  Descriptions,
} from 'antd';
import {
  ExclamationCircleOutlined,
  CheckCircleOutlined,
  WarningOutlined,
  ClockCircleOutlined,
  SearchOutlined,
} from '@ant-design/icons';
import { Column, Gauge, Line } from '@ant-design/charts';
import type { ColumnsType } from 'antd/es/table';
import { insightsApi } from '../services/insightsApi';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;

// 风险评估数据类型
interface RiskAssessment {
  assessment_id: string;
  customer_id: string;
  customer_name: string;
  overall_risk_score: number;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  assessment_date: string;
  risk_factors: {
    category: string;
    factor_name: string;
    score: number;
    impact: string;
  }[];
  recommendations: string[];
  next_review_date: string;
}

// 风险趋势数据类型
interface RiskTrend {
  date: string;
  credit_risk: number;
  market_risk: number;
  operational_risk: number;
  compliance_risk: number;
}

// 风险预警数据类型
interface RiskAlert {
  alert_id: string;
  alert_type: 'credit' | 'market' | 'operational' | 'compliance';
  severity: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  description: string;
  affected_entities: string[];
  created_time: string;
  status: 'active' | 'resolved' | 'investigating';
  recommended_actions: string[];
}

const RiskAnalysisPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [riskAssessments, setRiskAssessments] = useState<RiskAssessment[]>([]);
  const [riskTrends, setRiskTrends] = useState<RiskTrend[]>([]);
  const [riskAlerts, setRiskAlerts] = useState<RiskAlert[]>([]);
  const [selectedAssessment, setSelectedAssessment] = useState<string | null>(null);
  const [assessmentData, setAssessmentData] = useState('');
  const [activeTab, setActiveTab] = useState('overview');
  const [detailModalVisible, setDetailModalVisible] = useState(false);

  // 模拟风险评估数据
  const mockRiskAssessments: RiskAssessment[] = [
    {
      assessment_id: 'RA001',
      customer_id: 'C001',
      customer_name: 'TechCorp Inc.',
      overall_risk_score: 75,
      risk_level: 'medium',
      assessment_date: '2024-01-15',
      risk_factors: [
        { category: '信用风险', factor_name: '付款历史', score: 85, impact: '低风险' },
        { category: '市场风险', factor_name: '行业波动', score: 65, impact: '中等风险' },
        { category: '合规风险', factor_name: '法规变化', score: 70, impact: '中等风险' },
      ],
      recommendations: [
        '建议设置信用额度上限',
        '定期监控行业动态',
        '加强合规培训',
      ],
      next_review_date: '2024-04-15',
    },
    {
      assessment_id: 'RA002',
      customer_id: 'C002',
      customer_name: 'Global Manufacturing',
      overall_risk_score: 45,
      risk_level: 'low',
      assessment_date: '2024-01-12',
      risk_factors: [
        { category: '信用风险', factor_name: '财务状况', score: 90, impact: '低风险' },
        { category: '运营风险', factor_name: '供应链', score: 60, impact: '中等风险' },
      ],
      recommendations: [
        '维持当前合作关系',
        '关注供应链稳定性',
      ],
      next_review_date: '2024-07-12',
    },
    {
      assessment_id: 'RA003',
      customer_id: 'C003',
      customer_name: 'StartupTech Ltd.',
      overall_risk_score: 85,
      risk_level: 'high',
      assessment_date: '2024-01-10',
      risk_factors: [
        { category: '信用风险', factor_name: '资金流动性', score: 35, impact: '高风险' },
        { category: '市场风险', factor_name: '竞争压力', score: 40, impact: '高风险' },
      ],
      recommendations: [
        '要求预付款或担保',
        '缩短付款周期',
        '密切监控财务状况',
      ],
      next_review_date: '2024-02-10',
    },
  ];

  // 模拟风险趋势数据
  const mockRiskTrends: RiskTrend[] = [
    { date: '2024-01-01', credit_risk: 65, market_risk: 70, operational_risk: 55, compliance_risk: 60 },
    { date: '2024-01-08', credit_risk: 68, market_risk: 72, operational_risk: 58, compliance_risk: 62 },
    { date: '2024-01-15', credit_risk: 70, market_risk: 75, operational_risk: 60, compliance_risk: 65 },
    { date: '2024-01-22', credit_risk: 72, market_risk: 73, operational_risk: 62, compliance_risk: 63 },
    { date: '2024-01-29', credit_risk: 69, market_risk: 71, operational_risk: 59, compliance_risk: 61 },
  ];

  // 模拟风险预警数据
  const mockRiskAlerts: RiskAlert[] = [
    {
      alert_id: 'AL001',
      alert_type: 'credit',
      severity: 'high',
      title: '客户信用评级下调',
      description: 'StartupTech Ltd. 信用评级从B+下调至B-，建议调整信用政策',
      affected_entities: ['StartupTech Ltd.'],
      created_time: '2024-01-15 10:30:00',
      status: 'active',
      recommended_actions: ['调整信用额度', '要求额外担保', '加强监控'],
    },
    {
      alert_id: 'AL002',
      alert_type: 'market',
      severity: 'medium',
      title: '行业波动风险',
      description: '电子制造业面临原材料价格上涨压力，可能影响客户盈利能力',
      affected_entities: ['Asia Electronics', 'TechCorp Inc.'],
      created_time: '2024-01-14 14:20:00',
      status: 'investigating',
      recommended_actions: ['监控价格变化', '评估合同条款', '考虑价格调整'],
    },
    {
      alert_id: 'AL003',
      alert_type: 'compliance',
      severity: 'low',
      title: '新法规要求',
      description: '欧盟发布新的环保法规，可能影响部分产品出口',
      affected_entities: ['Global Manufacturing'],
      created_time: '2024-01-13 09:15:00',
      status: 'resolved',
      recommended_actions: ['更新产品认证', '调整出口策略'],
    },
  ];

  useEffect(() => {
    loadRiskAnalysis();
  }, []);

  /**
   * 加载风险分析数据
   */
  const loadRiskAnalysis = async () => {
    setLoading(true);
    try {
      // 尝试从API获取数据
      const response = await insightsApi.getRiskAnalysis();
      if (response.success && response.data) {
        console.log('风险分析数据:', response.data);
      }
    } catch (error) {
      console.log('使用模拟数据');
    } finally {
      // 使用模拟数据
      setRiskAssessments(mockRiskAssessments);
      setRiskTrends(mockRiskTrends);
      setRiskAlerts(mockRiskAlerts);
      setLoading(false);
    }
  };

  /**
   * 评估业务风险
   */
  const assessBusinessRisk = async () => {
    if (!assessmentData.trim()) {
      message.warning('请输入评估数据');
      return;
    }

    setLoading(true);
    try {
      const response = await insightsApi.assessBusinessRisk({
        customer_id: 'C001',
        transaction_amount: 100000,
        product_category: '工业设备',
        region: 'North America',
      });
      if (response.success) {
        message.success('风险评估完成');
        console.log('评估结果:', response.data);
      } else {
        message.error('评估失败: ' + response.message);
      }
    } catch (error) {
      message.error('评估过程中出现错误');
      console.error('评估错误:', error);
    } finally {
      setLoading(false);
    }
  };

  // 风险评估表格列定义
  const assessmentColumns: ColumnsType<RiskAssessment> = [
    {
      title: '客户信息',
      key: 'customer',
      render: (_, record) => (
        <div>
          <div style={{ fontWeight: 'bold' }}>{record.customer_name}</div>
          <div style={{ color: '#666', fontSize: '12px' }}>ID: {record.customer_id}</div>
        </div>
      ),
    },
    {
      title: '风险评分',
      dataIndex: 'overall_risk_score',
      key: 'overall_risk_score',
      render: (score) => (
        <div>
          <Progress
            percent={score}
            size="small"
            strokeColor={score > 80 ? '#ff4d4f' : score > 60 ? '#faad14' : '#52c41a'}
          />
          <Text strong>{score}</Text>
        </div>
      ),
    },
    {
      title: '风险等级',
      dataIndex: 'risk_level',
      key: 'risk_level',
      render: (level) => {
        const config = {
          low: { color: 'green', text: '低风险', icon: <CheckCircleOutlined /> },
    medium: { color: 'orange', text: '中等风险', icon: <ExclamationCircleOutlined /> },
    high: { color: 'red', text: '高风险', icon: <WarningOutlined /> },
    critical: { color: 'purple', text: '极高风险', icon: <ExclamationCircleOutlined /> },
        };
        const { color, text, icon } = config[level as keyof typeof config];
        return (
          <Tag color={color} icon={icon}>
            {text}
          </Tag>
        );
      },
    },
    {
      title: '评估日期',
      dataIndex: 'assessment_date',
      key: 'assessment_date',
      render: (date) => <Text>{date}</Text>,
    },
    {
      title: '下次复评',
      dataIndex: 'next_review_date',
      key: 'next_review_date',
      render: (date) => (
        <Text type={new Date(date) < new Date() ? 'danger' : 'secondary'}>
          <ClockCircleOutlined /> {date}
        </Text>
      ),
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Button
          type="link"
          onClick={() => {
            setSelectedAssessment(record.assessment_id);
            setDetailModalVisible(true); // 显示详情模态框
          }}
        >
          查看详情
        </Button>
      ),
    },
  ];

  // 风险预警表格列定义
  const alertColumns: ColumnsType<RiskAlert> = [
    {
      title: '预警信息',
      key: 'alert',
      render: (_, record) => (
        <div>
          <div style={{ fontWeight: 'bold' }}>{record.title}</div>
          <div style={{ color: '#666', fontSize: '12px' }}>{record.description}</div>
        </div>
      ),
    },
    {
      title: '类型',
      dataIndex: 'alert_type',
      key: 'alert_type',
      render: (type) => {
        const config = {
          credit: { color: 'blue', text: '信用风险' },
          market: { color: 'green', text: '市场风险' },
          operational: { color: 'orange', text: '运营风险' },
          compliance: { color: 'purple', text: '合规风险' },
        };
        const { color, text } = config[type as keyof typeof config];
        return <Tag color={color}>{text}</Tag>;
      },
    },
    {
      title: '严重程度',
      dataIndex: 'severity',
      key: 'severity',
      render: (severity) => {
        const config = {
          low: { color: 'default', text: '低' },
          medium: { color: 'orange', text: '中' },
          high: { color: 'red', text: '高' },
          critical: { color: 'purple', text: '极高' },
        };
        const { color, text } = config[severity as keyof typeof config];
        return <Tag color={color}>{text}</Tag>;
      },
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status) => {
        const config = {
          active: { color: 'red', text: '活跃' },
          investigating: { color: 'orange', text: '调查中' },
          resolved: { color: 'green', text: '已解决' },
        };
        const { text } = config[status as keyof typeof config];
        return <Badge status={status === 'active' ? 'error' : status === 'investigating' ? 'processing' : 'success'} text={text} />;
      },
    },
    {
      title: '创建时间',
      dataIndex: 'created_time',
      key: 'created_time',
      render: (time) => <Text>{time}</Text>,
    },
  ];

  // 风险趋势图表数据
  const trendChartData = riskTrends.flatMap(item => [
    { date: item.date, type: '信用风险', value: item.credit_risk },
    { date: item.date, type: '市场风险', value: item.market_risk },
    { date: item.date, type: '运营风险', value: item.operational_risk },
    { date: item.date, type: '合规风险', value: item.compliance_risk },
  ]);

  // 风险分布数据
  const riskDistribution = [
    { level: '低风险', count: riskAssessments.filter(r => r.risk_level === 'low').length },
    { level: '中等风险', count: riskAssessments.filter(r => r.risk_level === 'medium').length },
    { level: '高风险', count: riskAssessments.filter(r => r.risk_level === 'high').length },
    { level: '极高风险', count: riskAssessments.filter(r => r.risk_level === 'critical').length },
  ];

  // 总体风险评分
  const overallRiskScore = riskAssessments.length > 0 
    ? Math.round(riskAssessments.reduce((sum, r) => sum + r.overall_risk_score, 0) / riskAssessments.length)
    : 0;

  const tabItems = [
    {
      key: 'overview',
      label: '风险概览',
      children: (
        <div>
          {/* 统计卡片 */}
          <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title="总体风险评分"
                  value={overallRiskScore}
                  suffix="/100"
                  prefix={<CheckCircleOutlined />}
                  valueStyle={{ 
                    color: overallRiskScore > 80 ? '#ff4d4f' : overallRiskScore > 60 ? '#faad14' : '#52c41a' 
                  }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title="活跃预警"
                  value={riskAlerts.filter(a => a.status === 'active').length}
                  prefix={<ExclamationCircleOutlined />}
                  valueStyle={{ color: '#ff4d4f' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title="高风险客户"
                  value={riskAssessments.filter(r => r.risk_level === 'high' || r.risk_level === 'critical').length}
                  prefix={<WarningOutlined />}
                  valueStyle={{ color: '#faad14' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title="待复评客户"
                  value={riskAssessments.filter(r => new Date(r.next_review_date) < new Date()).length}
                  prefix={<ClockCircleOutlined />}
                  valueStyle={{ color: '#722ed1' }}
                />
              </Card>
            </Col>
          </Row>

          {/* 总体风险仪表盘 */}
          <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
            <Col xs={24} lg={8}>
              <Card title="总体风险评分" extra={<CheckCircleOutlined />}>
                <Gauge
                  percent={overallRiskScore / 100}
                  range={{
                    color: overallRiskScore > 80 ? '#ff4d4f' : overallRiskScore > 60 ? '#faad14' : '#52c41a',
                  }}
                  height={200}
                  statistic={{
                    content: {
                      style: {
                        fontSize: '24px',
                        color: overallRiskScore > 80 ? '#ff4d4f' : overallRiskScore > 60 ? '#faad14' : '#52c41a',
                      },
                      formatter: (value) => {
                        // 安全处理value参数，防止undefined导致的TypeError
                        if (value && typeof value === 'object' && 'percent' in value && typeof value.percent === 'number') {
                          return Math.round(value.percent * 100).toString();
                        }
                        // 如果value无效，使用overallRiskScore作为默认值
                        return (overallRiskScore || 0).toString();
                      },
                    },
                  }}
                />
                <div style={{ textAlign: 'center', marginTop: 16 }}>
                  <Text strong style={{ fontSize: 18 }}>
                    {overallRiskScore > 80 ? '高风险' : overallRiskScore > 60 ? '中等风险' : '低风险'}
                  </Text>
                </div>
              </Card>
            </Col>
            <Col xs={24} lg={8}>
              <Card title="风险分布" extra={<ExclamationCircleOutlined />}>
                <Column
                  data={riskDistribution}
                  xField="level"
                  yField="count"
                  height={200}
                  color={['#52c41a', '#faad14', '#ff4d4f', '#722ed1']}
                />
              </Card>
            </Col>
            <Col xs={24} lg={8}>
              <Card title="风险趋势" extra={<WarningOutlined />}>
                <Line
                  data={trendChartData}
                  xField="date"
                  yField="value"
                  seriesField="type"
                  height={200}
                  color={['#1890ff', '#52c41a', '#faad14', '#722ed1']}
                />
              </Card>
            </Col>
          </Row>

          {/* 风险评估列表 */}
          <Card title="风险评估列表" extra={<CheckCircleOutlined />}>
            <Table
              columns={assessmentColumns}
              dataSource={riskAssessments}
              rowKey="assessment_id"
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
      key: 'assessment',
      label: '风险评估',
      children: (
        <div>
          <Card title="业务风险评估" style={{ marginBottom: 16 }}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <TextArea
                rows={4}
                placeholder="请输入客户信息、交易金额、产品类别等数据，系统将进行风险评估..."
                value={assessmentData}
                onChange={(e) => setAssessmentData(e.target.value)}
              />
              <Button
                type="primary"
                icon={<SearchOutlined />}
                onClick={assessBusinessRisk}
                loading={loading}
              >
                开始风险评估
              </Button>
            </Space>
          </Card>

          <Row gutter={[16, 16]}>
            <Col xs={24} lg={12}>
              <Card title="风险因子分析">
                {selectedAssessment ? (
                  <div>
                    {riskAssessments
                      .find(r => r.assessment_id === selectedAssessment)
                      ?.risk_factors.map((factor, index) => (
                      <div key={index} style={{ marginBottom: 16 }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                          <Text strong>{factor.factor_name}</Text>
                          <Tag color={factor.score > 80 ? 'green' : factor.score > 60 ? 'orange' : 'red'}>
                            {factor.impact}
                          </Tag>
                        </div>
                        <Progress percent={factor.score} size="small" />
                        <Text type="secondary">{factor.category}</Text>
                      </div>
                    ))}
                  </div>
                ) : (
                  <Empty description="请选择一个风险评估查看详情" />
                )}
              </Card>
            </Col>
            <Col xs={24} lg={12}>
              <Card title="风险缓解建议">
                {selectedAssessment ? (
                  <List
                    dataSource={riskAssessments.find(r => r.assessment_id === selectedAssessment)?.recommendations || []}
                    renderItem={(item, index) => (
                      <List.Item>
                        <List.Item.Meta
                          avatar={<Badge count={index + 1} style={{ backgroundColor: '#1890ff' }} />}
                          description={item}
                        />
                      </List.Item>
                    )}
                  />
                ) : (
                  <Empty description="请选择一个风险评估查看建议" />
                )}
              </Card>
            </Col>
          </Row>
        </div>
      ),
    },
    {
      key: 'alerts',
      label: '风险预警',
      children: (
        <div>
          {/* 预警统计 */}
          <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
            <Col xs={24} sm={8}>
              <Alert
                message="活跃预警"
                description={`${riskAlerts.filter(a => a.status === 'active').length} 个预警需要处理`}
                type="error"
                showIcon
              />
            </Col>
            <Col xs={24} sm={8}>
              <Alert
                message="调查中"
                description={`${riskAlerts.filter(a => a.status === 'investigating').length} 个预警正在调查`}
                type="warning"
                showIcon
              />
            </Col>
            <Col xs={24} sm={8}>
              <Alert
                message="已解决"
                description={`${riskAlerts.filter(a => a.status === 'resolved').length} 个预警已解决`}
                type="success"
                showIcon
              />
            </Col>
          </Row>

          {/* 预警时间线 */}
          <Card title="最新预警" style={{ marginBottom: 16 }}>
            <Timeline>
              {riskAlerts.slice(0, 5).map((alert) => (
                <Timeline.Item
                  key={alert.alert_id}
                  color={
                    alert.severity === 'critical' ? 'red' :
                    alert.severity === 'high' ? 'orange' :
                    alert.severity === 'medium' ? 'blue' : 'green'
                  }
                >
                  <div>
                    <div style={{ fontWeight: 'bold' }}>{alert.title}</div>
                    <div style={{ color: '#666', marginBottom: 8 }}>{alert.description}</div>
                    <div>
                      <Tag color="blue">{alert.alert_type}</Tag>
                      <Tag color={alert.severity === 'high' ? 'red' : 'orange'}>{alert.severity}</Tag>
                      <Text type="secondary">{alert.created_time}</Text>
                    </div>
                  </div>
                </Timeline.Item>
              ))}
            </Timeline>
          </Card>

          {/* 预警列表 */}
          <Card title="风险预警列表">
            <Table
              columns={alertColumns}
              dataSource={riskAlerts}
              rowKey="alert_id"
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
  ];

  // 获取选中的风险评估详情
  const getSelectedAssessmentDetail = () => {
    return riskAssessments.find(r => r.assessment_id === selectedAssessment);
  };

  const selectedDetail = getSelectedAssessmentDetail();

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <Title level={2}>风险分析</Title>
        <Paragraph>
          全面评估业务风险，包括信用风险、市场风险、运营风险和合规风险，提供风险预警和缓解建议。
        </Paragraph>
      </div>

      <Tabs
        activeKey={activeTab}
        onChange={setActiveTab}
        items={tabItems}
      />

      {/* 风险评估详情模态框 */}
      <Modal
        title="风险评估详情"
        open={detailModalVisible}
        onCancel={() => {
          setDetailModalVisible(false);
          setSelectedAssessment(null);
        }}
        footer={[
          <Button key="close" onClick={() => {
            setDetailModalVisible(false);
            setSelectedAssessment(null);
          }}>
            关闭
          </Button>,
        ]}
        width={800}
      >
        {selectedDetail ? (
          <div>
            {/* 基本信息 */}
            <Card title="基本信息" style={{ marginBottom: 16 }}>
              <Descriptions column={2}>
                <Descriptions.Item label="客户名称">{selectedDetail.customer_name}</Descriptions.Item>
                <Descriptions.Item label="客户ID">{selectedDetail.customer_id}</Descriptions.Item>
                <Descriptions.Item label="风险评分">
                  <div>
                    <Progress
                      percent={selectedDetail.overall_risk_score}
                      size="small"
                      strokeColor={selectedDetail.overall_risk_score > 80 ? '#ff4d4f' : selectedDetail.overall_risk_score > 60 ? '#faad14' : '#52c41a'}
                      style={{ width: 100, marginRight: 8 }}
                    />
                    <Text strong>{selectedDetail.overall_risk_score}</Text>
                  </div>
                </Descriptions.Item>
                <Descriptions.Item label="风险等级">
                  <Tag color={selectedDetail.risk_level === 'high' ? 'red' : selectedDetail.risk_level === 'medium' ? 'orange' : 'green'}>
                    {selectedDetail.risk_level === 'high' ? '高风险' : selectedDetail.risk_level === 'medium' ? '中等风险' : '低风险'}
                  </Tag>
                </Descriptions.Item>
                <Descriptions.Item label="评估日期">{selectedDetail.assessment_date}</Descriptions.Item>
                <Descriptions.Item label="下次复评">{selectedDetail.next_review_date}</Descriptions.Item>
              </Descriptions>
            </Card>

            {/* 风险因子分析 */}
            <Card title="风险因子分析" style={{ marginBottom: 16 }}>
              {selectedDetail.risk_factors.map((factor, index) => (
                <div key={index} style={{ marginBottom: 16 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                    <Text strong>{factor.factor_name}</Text>
                    <Tag color={factor.score > 80 ? 'green' : factor.score > 60 ? 'orange' : 'red'}>
                      {factor.impact}
                    </Tag>
                  </div>
                  <Progress percent={factor.score} size="small" />
                  <Text type="secondary" style={{ fontSize: '12px' }}>{factor.category}</Text>
                </div>
              ))}
            </Card>

            {/* 风险缓解建议 */}
            <Card title="风险缓解建议">
              <List
                dataSource={selectedDetail.recommendations}
                renderItem={(item, index) => (
                  <List.Item>
                    <List.Item.Meta
                      avatar={<Badge count={index + 1} style={{ backgroundColor: '#1890ff' }} />}
                      description={item}
                    />
                  </List.Item>
                )}
              />
            </Card>
          </div>
        ) : (
          <Empty description="未找到风险评估详情" />
        )}
      </Modal>
    </div>
  );
};

export default RiskAnalysisPage;