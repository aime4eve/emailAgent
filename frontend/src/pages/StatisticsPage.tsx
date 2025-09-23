/**
 * 统计分析页面
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  Card,
  Row,
  Col,
  Statistic,
  Typography,
  DatePicker,
  Select,
  Space,
  Button,
  Table,
  Tag,
  Progress,
  Spin,
  message,
} from 'antd';
import {
  BarChartOutlined,
  LineChartOutlined,
  PieChartOutlined,
  DownloadOutlined,
  ReloadOutlined,
  RiseOutlined,
} from '@ant-design/icons';
import { Column, Pie, Line } from '@ant-design/charts';
import type { ColumnsType } from 'antd/es/table';

const { Title } = Typography;
const { RangePicker } = DatePicker;
const { Option } = Select;

// 统计数据接口
interface StatisticsData {
  totalExtractions: number;
  totalEntities: number;
  totalRelations: number;
  totalOntologies: number;
  extractionTrend: Array<{ date: string; count: number }>;
  entityTypeDistribution: Array<{ type: string; count: number }>;
  relationTypeDistribution: Array<{ type: string; count: number }>;
  performanceMetrics: {
    avgProcessingTime: number;
    successRate: number;
    errorRate: number;
  };
  recentExtractions: Array<{
    id: string;
    text: string;
    entityCount: number;
    relationCount: number;
    confidence: number;
    createdAt: string;
  }>;
}

/**
 * 统计分析页面组件
 */
const StatisticsPage: React.FC = () => {
  // 状态管理
  const [loading, setLoading] = useState<boolean>(false);
  const [statisticsData, setStatisticsData] = useState<StatisticsData | null>(null);
  const [dateRange, setDateRange] = useState<[string, string] | null>(null);
  const [selectedMetric, setSelectedMetric] = useState<string>('extractions');

  /**
   * 加载统计数据
   */
  const loadStatistics = useCallback(async () => {
    setLoading(true);
    try {
      // 模拟统计数据（实际应用中应该从后端API获取）
      const mockData: StatisticsData = {
        totalExtractions: 1248,
        totalEntities: 5632,
        totalRelations: 3421,
        totalOntologies: 12,
        extractionTrend: [
          { date: '2024-01-01', count: 45 },
          { date: '2024-01-02', count: 52 },
          { date: '2024-01-03', count: 48 },
          { date: '2024-01-04', count: 61 },
          { date: '2024-01-05', count: 55 },
          { date: '2024-01-06', count: 67 },
          { date: '2024-01-07', count: 72 },
        ],
        entityTypeDistribution: [
          { type: 'PERSON', count: 1245 },
          { type: 'ORGANIZATION', count: 987 },
          { type: 'LOCATION', count: 856 },
          { type: 'TIME', count: 654 },
          { type: 'EVENT', count: 432 },
          { type: 'CONCEPT', count: 1458 },
        ],
        relationTypeDistribution: [
          { type: '工作于', count: 456 },
          { type: '位于', count: 389 },
          { type: '参与', count: 567 },
          { type: '拥有', count: 234 },
          { type: '关联', count: 678 },
          { type: '属于', count: 1097 },
        ],
        performanceMetrics: {
          avgProcessingTime: 2.3,
          successRate: 94.5,
          errorRate: 5.5,
        },
        recentExtractions: [
          {
            id: '1',
            text: '苹果公司在加利福尼亚州库比蒂诺市成立...',
            entityCount: 12,
            relationCount: 8,
            confidence: 0.92,
            createdAt: '2024-01-07 14:30:00',
          },
          {
            id: '2',
            text: '马云创立了阿里巴巴集团，总部位于杭州...',
            entityCount: 15,
            relationCount: 11,
            confidence: 0.88,
            createdAt: '2024-01-07 13:45:00',
          },
          {
            id: '3',
            text: '人工智能技术在医疗领域的应用越来越广泛...',
            entityCount: 9,
            relationCount: 6,
            confidence: 0.85,
            createdAt: '2024-01-07 12:20:00',
          },
        ],
      };
      
      // 模拟API延迟
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setStatisticsData(mockData);
      message.success('统计数据加载成功');
    } catch (error) {
      message.error('加载统计数据时发生错误');
      console.error('Load statistics error:', error);
    } finally {
      setLoading(false);
    }
  }, [dateRange]);

  /**
   * 导出统计报告
   */
  const handleExportReport = () => {
    if (!statisticsData) {
      message.warning('没有可导出的统计数据');
      return;
    }

    const reportData = {
      exportTime: new Date().toISOString(),
      dateRange,
      statistics: statisticsData,
    };

    const dataStr = JSON.stringify(reportData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `statistics_report_${new Date().getTime()}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    message.success('统计报告已导出');
  };

  // 组件挂载时加载数据
  useEffect(() => {
    loadStatistics();
  }, [loadStatistics]);

  // 最近抽取记录表格列定义
  const recentExtractionsColumns: ColumnsType<any> = [
    {
      title: '文本内容',
      dataIndex: 'text',
      key: 'text',
      ellipsis: true,
      width: 300,
    },
    {
      title: '实体数量',
      dataIndex: 'entityCount',
      key: 'entityCount',
      width: 100,
      render: (count) => <Tag color="blue">{count}</Tag>,
    },
    {
      title: '关系数量',
      dataIndex: 'relationCount',
      key: 'relationCount',
      width: 100,
      render: (count) => <Tag color="green">{count}</Tag>,
    },
    {
      title: '置信度',
      dataIndex: 'confidence',
      key: 'confidence',
      width: 120,
      render: (confidence) => (
        <Progress
          percent={Math.round(confidence * 100)}
          size="small"
          status={confidence > 0.8 ? 'success' : confidence > 0.6 ? 'normal' : 'exception'}
        />
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'createdAt',
      key: 'createdAt',
      width: 150,
    },
  ];

  if (!statisticsData) {
    return (
      <div className="loading-container">
        <Spin size="large" />
        <div style={{ marginTop: 16 }}>加载统计数据中...</div>
      </div>
    );
  }

  return (
    <div>
      <Row gutter={[24, 24]}>
        <Col span={24}>
          <Card>
            <div className="flex-between mb-16">
              <Title level={2} style={{ margin: 0 }}>
                统计分析
              </Title>
              <Space>
                <RangePicker
                  onChange={(_, dateStrings) => {
                    setDateRange(dateStrings as [string, string]);
                  }}
                />
                <Select
                  value={selectedMetric}
                  onChange={setSelectedMetric}
                  style={{ width: 120 }}
                >
                  <Option value="extractions">抽取量</Option>
                  <Option value="entities">实体量</Option>
                  <Option value="relations">关系量</Option>
                </Select>
                <Button
                  icon={<ReloadOutlined />}
                  onClick={loadStatistics}
                  loading={loading}
                >
                  刷新
                </Button>
                <Button
                  type="primary"
                  icon={<DownloadOutlined />}
                  onClick={handleExportReport}
                >
                  导出报告
                </Button>
              </Space>
            </div>
          </Card>
        </Col>
      </Row>

      {/* 概览统计卡片 */}
      <Row gutter={[24, 24]} style={{ marginTop: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="总抽取次数"
              value={statisticsData.totalExtractions}
              prefix={<BarChartOutlined />}
              suffix={<RiseOutlined style={{ color: '#3f8600' }} />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="总实体数量"
              value={statisticsData.totalEntities}
              prefix={<PieChartOutlined />}
              suffix={<RiseOutlined style={{ color: '#3f8600' }} />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="总关系数量"
              value={statisticsData.totalRelations}
              prefix={<LineChartOutlined />}
              suffix={<RiseOutlined style={{ color: '#3f8600' }} />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="本体数量"
              value={statisticsData.totalOntologies}
              prefix={<BarChartOutlined />}
            />
          </Card>
        </Col>
      </Row>

      {/* 性能指标 */}
      <Row gutter={[24, 24]} style={{ marginTop: 24 }}>
        <Col span={8}>
          <Card title="平均处理时间">
            <Statistic
              value={statisticsData.performanceMetrics.avgProcessingTime}
              suffix="秒"
              precision={1}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card title="成功率">
            <Statistic
              value={statisticsData.performanceMetrics.successRate}
              suffix="%"
              precision={1}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card title="错误率">
            <Statistic
              value={statisticsData.performanceMetrics.errorRate}
              suffix="%"
              precision={1}
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 图表区域 */}
      <Row gutter={[24, 24]} style={{ marginTop: 24 }}>
        <Col span={12}>
          <Card title="抽取趋势">
            <Line
              data={statisticsData.extractionTrend}
              xField="date"
              yField="count"
              height={300}
              smooth
              point={{
                size: 5,
                shape: 'diamond',
              }}
            />
          </Card>
        </Col>
        <Col span={12}>
          <Card title="实体类型分布">
            <Column
              data={statisticsData.entityTypeDistribution}
              xField="type"
              yField="count"
              height={300}
              meta={{
                type: {
                  alias: '实体类型',
                },
                count: {
                  alias: '数量',
                },
              }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[24, 24]} style={{ marginTop: 24 }}>
        <Col span={12}>
          <Card title="关系类型分布">
            <Pie
              data={statisticsData.relationTypeDistribution}
              angleField="count"
              colorField="type"
              radius={0.8}
              height={300}
              legend={{
                position: 'right',
              }}
              interactions={[
                {
                  type: 'element-active',
                },
              ]}
            />
          </Card>
        </Col>
        <Col span={12}>
          <Card title="最近抽取记录">
            <Table
              columns={recentExtractionsColumns}
              dataSource={statisticsData.recentExtractions}
              rowKey="id"
              pagination={false}
              size="small"
              scroll={{ y: 300 }}
            />
          </Card>
        </Col>
      </Row>

      {/* 详细统计表格 */}
      <Row gutter={[24, 24]} style={{ marginTop: 24 }}>
        <Col span={24}>
          <Card title="详细统计">
            <Row gutter={[16, 16]}>
              <Col span={12}>
                <Title level={4}>实体类型统计</Title>
                <Table
                  columns={[
                    { title: '类型', dataIndex: 'type', key: 'type' },
                    { title: '数量', dataIndex: 'count', key: 'count' },
                    {
                      title: '占比',
                      key: 'percentage',
                      render: (_, record) => {
                        const percentage = ((record.count / statisticsData.totalEntities) * 100).toFixed(1);
                        return `${percentage}%`;
                      },
                    },
                  ]}
                  dataSource={statisticsData.entityTypeDistribution}
                  rowKey="type"
                  pagination={false}
                  size="small"
                />
              </Col>
              <Col span={12}>
                <Title level={4}>关系类型统计</Title>
                <Table
                  columns={[
                    { title: '类型', dataIndex: 'type', key: 'type' },
                    { title: '数量', dataIndex: 'count', key: 'count' },
                    {
                      title: '占比',
                      key: 'percentage',
                      render: (_, record) => {
                        const percentage = ((record.count / statisticsData.totalRelations) * 100).toFixed(1);
                        return `${percentage}%`;
                      },
                    },
                  ]}
                  dataSource={statisticsData.relationTypeDistribution}
                  rowKey="type"
                  pagination={false}
                  size="small"
                />
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default StatisticsPage;