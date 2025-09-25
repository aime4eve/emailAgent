/**
 * 产品分析页面
 * 提供产品需求分析、功能优化建议、市场定位分析等功能
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
  Tabs,
  Input,
  message,
  Badge,
  Rate,
  Modal,
  Descriptions,
  Timeline,
} from 'antd';
import {
  ProductOutlined,
  StarOutlined,
  BulbOutlined,
  SettingOutlined,
  SearchOutlined,
  HeartOutlined,
} from '@ant-design/icons';
import { Column, Radar } from '@ant-design/charts';
import type { ColumnsType } from 'antd/es/table';
import { insightsApi } from '../services/insightsApi';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;

// 产品分析数据类型
interface ProductAnalysisData {
  product_id: string;
  product_name: string;
  category: string;
  demand_score: number;
  market_potential: number;
  competition_level: 'high' | 'medium' | 'low';
  price_range: {
    min: number;
    max: number;
    optimal: number;
  };
  key_features: string[];
  customer_preferences: {
    feature: string;
    importance: number;
    satisfaction: number;
  }[];
  market_trends: {
    trend: string;
    impact: 'positive' | 'negative' | 'neutral';
    confidence: number;
  }[];
  optimization_suggestions: {
    type: 'feature' | 'price' | 'quality' | 'marketing';
    title: string;
    description: string;
    priority: 'high' | 'medium' | 'low';
    impact_score: number;
  }[];
}

// 功能需求数据类型
interface FeatureRequirement {
  feature_name: string;
  demand_frequency: number;
  importance_score: number;
  current_satisfaction: number;
  improvement_potential: number;
  related_products: string[];
}



const ProductAnalysisPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [productAnalysis, setProductAnalysis] = useState<ProductAnalysisData[]>([]);
  const [featureRequirements, setFeatureRequirements] = useState<FeatureRequirement[]>([]);
  const [selectedProduct, setSelectedProduct] = useState<string | null>(null);
  const [productDetailVisible, setProductDetailVisible] = useState(false);
  const [analysisText, setAnalysisText] = useState('');
  const [activeTab, setActiveTab] = useState('overview');

  // 模拟产品分析数据
  const mockProductAnalysis: ProductAnalysisData[] = [
    {
      product_id: 'P001',
      product_name: '工业控制器X1',
      category: '工业自动化',
      demand_score: 85,
      market_potential: 92,
      competition_level: 'medium',
      price_range: {
        min: 20000,
        max: 30000,
        optimal: 25000,
      },
      key_features: ['无线连接', '实时监控', '故障诊断', '远程控制'],
      customer_preferences: [
        { feature: '稳定性', importance: 95, satisfaction: 88 },
        { feature: '易用性', importance: 82, satisfaction: 75 },
        { feature: '价格', importance: 78, satisfaction: 70 },
        { feature: '技术支持', importance: 85, satisfaction: 80 },
      ],
      market_trends: [
        { trend: '智能化需求增长', impact: 'positive', confidence: 90 },
        { trend: '成本压力增加', impact: 'negative', confidence: 75 },
        { trend: '环保要求提升', impact: 'neutral', confidence: 65 },
      ],
      optimization_suggestions: [
        {
          type: 'feature',
          title: '增加AI预测功能',
          description: '集成机器学习算法，提供设备故障预测',
          priority: 'high',
          impact_score: 85,
        },
        {
          type: 'price',
          title: '优化定价策略',
          description: '根据市场分析调整价格区间',
          priority: 'medium',
          impact_score: 70,
        },
      ],
    },
    {
      product_id: 'P002',
      product_name: '智能传感器S2',
      category: '电子产品',
      demand_score: 78,
      market_potential: 88,
      competition_level: 'high',
      price_range: {
        min: 2500,
        max: 4500,
        optimal: 3500,
      },
      key_features: ['高精度', '低功耗', '无线传输', '防水防尘'],
      customer_preferences: [
        { feature: '精度', importance: 92, satisfaction: 85 },
        { feature: '耐用性', importance: 88, satisfaction: 82 },
        { feature: '价格', importance: 75, satisfaction: 68 },
        { feature: '兼容性', importance: 80, satisfaction: 78 },
      ],
      market_trends: [
        { trend: 'IoT应用扩展', impact: 'positive', confidence: 95 },
        { trend: '价格竞争激烈', impact: 'negative', confidence: 85 },
      ],
      optimization_suggestions: [
        {
          type: 'quality',
          title: '提升产品耐用性',
          description: '改进材料和工艺，延长使用寿命',
          priority: 'high',
          impact_score: 80,
        },
      ],
    },
  ];

  // 模拟功能需求数据
  const mockFeatureRequirements: FeatureRequirement[] = [
    {
      feature_name: '无线连接',
      demand_frequency: 156,
      importance_score: 88,
      current_satisfaction: 75,
      improvement_potential: 85,
      related_products: ['控制器', '传感器', '网关'],
    },
    {
      feature_name: '实时监控',
      demand_frequency: 142,
      importance_score: 92,
      current_satisfaction: 82,
      improvement_potential: 78,
      related_products: ['监控系统', '数据采集器'],
    },
    {
      feature_name: '故障诊断',
      demand_frequency: 128,
      importance_score: 85,
      current_satisfaction: 68,
      improvement_potential: 90,
      related_products: ['诊断工具', '分析软件'],
    },
  ];

  useEffect(() => {
    loadProductAnalysis();
  }, []);

  /**
   * 加载产品分析数据
   */
  const loadProductAnalysis = async () => {
    setLoading(true);
    try {
      // 尝试从API获取数据
      const response = await insightsApi.getProductAnalysis();
      if (response.success && response.data) {
        console.log('产品分析数据:', response.data);
      }
    } catch (error) {
      console.log('使用模拟数据');
    } finally {
      // 使用模拟数据
      setProductAnalysis(mockProductAnalysis);
      setFeatureRequirements(mockFeatureRequirements);
      setLoading(false);
    }
  };

  /**
   * 分析产品需求
   */
  const analyzeProductDemand = async () => {
    if (!analysisText.trim()) {
      message.warning('请输入产品信息');
      return;
    }

    setLoading(true);
    try {
      const response = await insightsApi.analyzeProductDemand({
        product_name: analysisText,
        category: '电子产品',
      });
      if (response.success) {
        message.success('产品需求分析完成');
        console.log('分析结果:', response.data);
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

  // 产品表格列定义
  const productColumns: ColumnsType<ProductAnalysisData> = [
    {
      title: '产品信息',
      key: 'product',
      render: (_, record) => (
        <div>
          <div style={{ fontWeight: 'bold' }}>{record.product_name}</div>
          <Tag color="blue">{record.category}</Tag>
        </div>
      ),
    },
    {
      title: '需求评分',
      dataIndex: 'demand_score',
      key: 'demand_score',
      render: (score) => (
        <div>
          <Progress percent={score} size="small" />
          <Text strong>{score}</Text>
        </div>
      ),
    },
    {
      title: '市场潜力',
      dataIndex: 'market_potential',
      key: 'market_potential',
      render: (potential) => (
        <div>
          <Progress percent={potential} size="small" status="active" />
          <Text strong>{potential}</Text>
        </div>
      ),
    },
    {
      title: '竞争程度',
      dataIndex: 'competition_level',
      key: 'competition_level',
      render: (level) => (
        <Tag
          color={
            level === 'high' ? 'red' : level === 'medium' ? 'orange' : 'green'
          }
        >
          {level === 'high' ? '激烈' : level === 'medium' ? '中等' : '较低'}
        </Tag>
      ),
    },
    {
      title: '最优价格',
      key: 'optimal_price',
      render: (_, record) => (
        <span style={{ color: '#52c41a', fontWeight: 'bold' }}>
          ${record.price_range.optimal.toLocaleString()}
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
            setSelectedProduct(record.product_id);
            setProductDetailVisible(true);
          }}
        >
          详细分析
        </Button>
      ),
    },
  ];

  // 功能需求图表数据
  const featureChartData = featureRequirements.map(item => ({
    feature: item.feature_name,
    demand: item.demand_frequency,
    satisfaction: item.current_satisfaction,
    potential: item.improvement_potential,
  }));

  // 客户偏好雷达图数据
  const selectedProductData = productAnalysis.find(p => p.product_id === selectedProduct) || productAnalysis[0];
  const radarData = selectedProductData?.customer_preferences.map(pref => ({
    item: pref.feature,
    importance: pref.importance,
    satisfaction: pref.satisfaction,
  })) || [];

  /**
   * 获取选中产品的详细信息
   */
  const getSelectedProductDetail = () => {
    return productAnalysis.find(p => p.product_id === selectedProduct);
  };

  /**
   * 关闭产品详情模态框
   */
  const handleCloseProductDetail = () => {
    setProductDetailVisible(false);
    setSelectedProduct(null);
  };

  const tabItems = [
    {
      key: 'overview',
      label: '产品概览',
      children: (
        <div>
          {/* 统计卡片 */}
          <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title="产品总数"
                  value={productAnalysis.length}
                  prefix={<ProductOutlined />}
                  valueStyle={{ color: '#1890ff' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title="平均需求评分"
                  value={Math.round(
                    productAnalysis.reduce((sum, p) => sum + p.demand_score, 0) /
                    productAnalysis.length
                  )}
                  prefix={<StarOutlined />}
                  valueStyle={{ color: '#52c41a' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title="高潜力产品"
                  value={productAnalysis.filter(p => p.market_potential > 85).length}
                  prefix={<StarOutlined />}
                  valueStyle={{ color: '#faad14' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title="优化建议"
                  value={productAnalysis.reduce((sum, p) => sum + p.optimization_suggestions.length, 0)}
                  prefix={<BulbOutlined />}
                  valueStyle={{ color: '#722ed1' }}
                />
              </Card>
            </Col>
          </Row>

          {/* 图表区域 */}
          <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
            <Col xs={24} lg={12}>
              <Card title="功能需求分析" extra={<SettingOutlined />}>
                <Column
                  data={featureChartData}
                  xField="feature"
                  yField="demand"
                  height={300}
                  color="#1890ff"
                />
              </Card>
            </Col>
            <Col xs={24} lg={12}>
              <Card title="客户偏好分析" extra={<HeartOutlined />}>
                <Radar
                  data={radarData}
                  xField="item"
                  yField="importance"
                  seriesField="type"
                  height={300}
                  color={['#1890ff', '#52c41a']}
                />
              </Card>
            </Col>
          </Row>

          {/* 产品列表 */}
          <Card title="产品分析列表" extra={<ProductOutlined />}>
            <Table
              columns={productColumns}
              dataSource={productAnalysis}
              rowKey="product_id"
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
      key: 'demand-analysis',
      label: '需求分析',
      children: (
        <div>
          <Card title="产品需求分析" style={{ marginBottom: 16 }}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <TextArea
                rows={4}
                placeholder="请输入产品名称或描述，系统将分析市场需求和优化建议..."
                value={analysisText}
                onChange={(e) => setAnalysisText(e.target.value)}
              />
              <Button
                type="primary"
                icon={<SearchOutlined />}
                onClick={analyzeProductDemand}
                loading={loading}
              >
                分析产品需求
              </Button>
            </Space>
          </Card>

          <Row gutter={[16, 16]}>
            <Col xs={24} lg={12}>
              <Card title="功能需求排行">
                <List
                  dataSource={featureRequirements}
                  renderItem={(item, index) => (
                    <List.Item>
                      <List.Item.Meta
                        avatar={<Badge count={index + 1} style={{ backgroundColor: '#1890ff' }} />}
                        title={
                          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                            <span>{item.feature_name}</span>
                            <Rate disabled defaultValue={Math.round(item.importance_score / 20)} />
                          </div>
                        }
                        description={
                          <div>
                            <div>需求频次: {item.demand_frequency} 次</div>
                            <div>当前满意度: {item.current_satisfaction}%</div>
                            <div>改进潜力: {item.improvement_potential}%</div>
                            <Progress
                              percent={item.improvement_potential}
                              size="small"
                              style={{ marginTop: 8 }}
                            />
                          </div>
                        }
                      />
                    </List.Item>
                  )}
                />
              </Card>
            </Col>
            <Col xs={24} lg={12}>
              <Card title="优化建议">
                {selectedProductData?.optimization_suggestions.map((suggestion, index) => (
                  <Card.Grid key={index} style={{ width: '100%', padding: 16 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <div style={{ flex: 1 }}>
                        <div style={{ fontWeight: 'bold', marginBottom: 8 }}>
                          <Tag
                            color={
                              suggestion.type === 'feature' ? 'blue' :
                              suggestion.type === 'price' ? 'green' :
                              suggestion.type === 'quality' ? 'orange' : 'purple'
                            }
                          >
                            {suggestion.type === 'feature' ? '功能' :
                             suggestion.type === 'price' ? '价格' :
                             suggestion.type === 'quality' ? '质量' : '营销'}
                          </Tag>
                          {suggestion.title}
                        </div>
                        <div style={{ color: '#666', marginBottom: 8 }}>
                          {suggestion.description}
                        </div>
                        <div>
                          <Tag
                            color={
                              suggestion.priority === 'high' ? 'red' :
                              suggestion.priority === 'medium' ? 'orange' : 'default'
                            }
                          >
                            {suggestion.priority === 'high' ? '高' :
                             suggestion.priority === 'medium' ? '中' : '低'}优先级
                          </Tag>
                          <span style={{ marginLeft: 8, color: '#52c41a' }}>
                            影响分数: {suggestion.impact_score}
                          </span>
                        </div>
                      </div>
                    </div>
                  </Card.Grid>
                ))}
              </Card>
            </Col>
          </Row>
        </div>
      ),
    },
  ];

  const productDetail = getSelectedProductDetail();

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <Title level={2}>产品分析</Title>
        <Paragraph>
          分析产品市场需求、功能偏好、价格敏感度，提供产品优化建议和市场定位策略。
        </Paragraph>
      </div>

      <Tabs
        activeKey={activeTab}
        onChange={setActiveTab}
        items={tabItems}
      />

      {/* 产品详细分析模态框 */}
      <Modal
        title="产品详细分析"
        open={productDetailVisible}
        onCancel={handleCloseProductDetail}
        footer={[
          <Button key="close" onClick={handleCloseProductDetail}>
            关闭
          </Button>,
        ]}
        width={800}
      >
        {productDetail && (
          <div>
            {/* 基本信息 */}
            <Card title="基本信息" style={{ marginBottom: 16 }}>
              <Descriptions column={2}>
                <Descriptions.Item label="产品名称">{productDetail.product_name}</Descriptions.Item>
                <Descriptions.Item label="产品类别">{productDetail.category}</Descriptions.Item>
                <Descriptions.Item label="需求评分">
                  <Progress percent={productDetail.demand_score} size="small" />
                  <span style={{ marginLeft: 8 }}>{productDetail.demand_score}</span>
                </Descriptions.Item>
                <Descriptions.Item label="市场潜力">
                  <Progress percent={productDetail.market_potential} size="small" status="active" />
                  <span style={{ marginLeft: 8 }}>{productDetail.market_potential}</span>
                </Descriptions.Item>
                <Descriptions.Item label="竞争程度">
                  <Tag
                    color={
                      productDetail.competition_level === 'high' ? 'red' : 
                      productDetail.competition_level === 'medium' ? 'orange' : 'green'
                    }
                  >
                    {productDetail.competition_level === 'high' ? '激烈' : 
                     productDetail.competition_level === 'medium' ? '中等' : '较低'}
                  </Tag>
                </Descriptions.Item>
                <Descriptions.Item label="价格区间">
                  ${productDetail.price_range.min.toLocaleString()} - ${productDetail.price_range.max.toLocaleString()}
                  <br />
                  <span style={{ color: '#52c41a', fontWeight: 'bold' }}>
                    最优价格: ${productDetail.price_range.optimal.toLocaleString()}
                  </span>
                </Descriptions.Item>
              </Descriptions>
            </Card>

            {/* 关键功能 */}
            <Card title="关键功能" style={{ marginBottom: 16 }}>
              <Space wrap>
                {productDetail.key_features.map((feature, index) => (
                  <Tag key={index} color="blue">{feature}</Tag>
                ))}
              </Space>
            </Card>

            {/* 客户偏好分析 */}
            <Card title="客户偏好分析" style={{ marginBottom: 16 }}>
              <List
                dataSource={productDetail.customer_preferences}
                renderItem={(pref) => (
                  <List.Item>
                    <List.Item.Meta
                      title={pref.feature}
                      description={
                        <div>
                          <div>重要性: <Progress percent={pref.importance} size="small" style={{ width: 100, display: 'inline-block' }} /> {pref.importance}%</div>
                          <div>满意度: <Progress percent={pref.satisfaction} size="small" style={{ width: 100, display: 'inline-block' }} /> {pref.satisfaction}%</div>
                        </div>
                      }
                    />
                  </List.Item>
                )}
              />
            </Card>

            {/* 市场趋势 */}
            <Card title="市场趋势" style={{ marginBottom: 16 }}>
              <Timeline>
                {productDetail.market_trends.map((trend, index) => (
                  <Timeline.Item
                    key={index}
                    color={
                      trend.impact === 'positive' ? 'green' :
                      trend.impact === 'negative' ? 'red' : 'blue'
                    }
                  >
                    <div>
                      <div style={{ fontWeight: 'bold' }}>{trend.trend}</div>
                      <div>
                        <Tag
                          color={
                            trend.impact === 'positive' ? 'green' :
                            trend.impact === 'negative' ? 'red' : 'default'
                          }
                        >
                          {trend.impact === 'positive' ? '积极' :
                           trend.impact === 'negative' ? '消极' : '中性'}
                        </Tag>
                        <span style={{ marginLeft: 8 }}>置信度: {trend.confidence}%</span>
                      </div>
                    </div>
                  </Timeline.Item>
                ))}
              </Timeline>
            </Card>

            {/* 优化建议 */}
            <Card title="优化建议">
              <List
                dataSource={productDetail.optimization_suggestions}
                renderItem={(suggestion) => (
                  <List.Item>
                    <List.Item.Meta
                      title={
                        <div>
                          <Tag
                            color={
                              suggestion.type === 'feature' ? 'blue' :
                              suggestion.type === 'price' ? 'green' :
                              suggestion.type === 'quality' ? 'orange' : 'purple'
                            }
                          >
                            {suggestion.type === 'feature' ? '功能' :
                             suggestion.type === 'price' ? '价格' :
                             suggestion.type === 'quality' ? '质量' : '营销'}
                          </Tag>
                          <span style={{ marginLeft: 8 }}>{suggestion.title}</span>
                        </div>
                      }
                      description={
                        <div>
                          <div style={{ marginBottom: 8 }}>{suggestion.description}</div>
                          <div>
                            <Tag
                              color={
                                suggestion.priority === 'high' ? 'red' :
                                suggestion.priority === 'medium' ? 'orange' : 'default'
                              }
                            >
                              {suggestion.priority === 'high' ? '高' :
                               suggestion.priority === 'medium' ? '中' : '低'}优先级
                            </Tag>
                            <span style={{ marginLeft: 8, color: '#52c41a' }}>
                              影响分数: {suggestion.impact_score}
                            </span>
                          </div>
                        </div>
                      }
                    />
                  </List.Item>
                )}
              />
            </Card>
          </div>
        )}
      </Modal>
     </div>
   );
};

export default ProductAnalysisPage;