/**
 * 智能推荐页面
 * 提供自然语言查询、客户推荐、产品推荐、营销策略推荐等功能
 */

import React, { useState } from 'react';
import {
  Card,
  Row,
  Col,
  Input,
  Button,
  Modal,
  Descriptions,
  Tag,
  Progress,
  Space,
  Tabs,
  Divider,
  Avatar,
  Badge,
  Typography,
  List,
  Rate,
  message,
} from 'antd';
import {
  SearchOutlined,
  UserOutlined,
  ShoppingCartOutlined,
  BulbOutlined,
  RobotOutlined,
  SendOutlined,
  StarOutlined,
  ThunderboltOutlined,
  ClockCircleOutlined,
  HistoryOutlined,
  QuestionCircleOutlined
} from '@ant-design/icons';

const { Search, TextArea } = Input;
const { Title, Text } = Typography;

// 查询结果类型
interface QueryResult {
  id: string;
  query: string;
  queryType: string;
  results: any[];
  confidence: number;
  processingTime: number;
  suggestions: string[];
  timestamp: string;
}

// 推荐结果类型
interface Recommendation {
  id: string;
  type: 'customer' | 'product' | 'strategy';
  targetId: string;
  targetName: string;
  score: number;
  reason: string;
  supportingData: any;
  tags: string[];
}

// 自动化服务动作类型
interface AutoServiceAction {
  id: string;
  actionType: 'classify' | 'prioritize' | 'respond' | 'follow_up';
  targetId: string;
  actionDescription: string;
  priority: number;
  suggestedResponse?: string;
  followUpDate?: string;
  status: 'pending' | 'in_progress' | 'completed';
}

// 模拟查询历史
const mockQueryHistory: QueryResult[] = [
  {
    id: '1',
    query: '哪些客户对工业设备最感兴趣？',
    queryType: 'customer_interest',
    results: [
      { customerId: '1', customerName: 'John Smith', company: 'ABC Trading', score: 0.95 },
      { customerId: '2', customerName: 'Maria Garcia', company: 'Empresa Int.', score: 0.87 },
    ],
    confidence: 0.92,
    processingTime: 1.2,
    suggestions: ['查看这些客户的详细需求分析', '分析客户的地域分布特征'],
    timestamp: '2024-01-15 14:30:25',
  },
  {
    id: '2',
    query: '最近3个月询盘频率最高的产品',
    queryType: 'product_inquiry_trend',
    results: [
      { productName: '工业自动化设备', inquiryCount: 156, growth: 0.22 },
      { productName: '智能传感器', inquiryCount: 134, growth: 0.18 },
    ],
    confidence: 0.88,
    processingTime: 0.8,
    suggestions: ['分析产品需求趋势', '制定相应的营销策略'],
    timestamp: '2024-01-15 10:15:42',
  },
];

// 模拟客户推荐
const mockCustomerRecommendations: Recommendation[] = [
  {
    id: '1',
    type: 'customer',
    targetId: 'cust_001',
    targetName: 'John Smith',
    score: 0.95,
    reason: '该客户曾询盘相似产品，价值评分95分，转化率高',
    supportingData: {
      company: 'ABC Trading Co.',
      country: 'United States',
      valueScore: 95,
      inquiryCount: 15,
      conversionRate: 0.8,
    },
    tags: ['高价值', 'A级客户', '活跃'],
  },
  {
    id: '2',
    type: 'customer',
    targetId: 'cust_002',
    targetName: 'Maria Garcia',
    score: 0.87,
    reason: '客户在相同产品类别中表现活跃，询盘频率8次/月',
    supportingData: {
      company: 'Empresa Internacional',
      country: 'Spain',
      valueScore: 72,
      inquiryCount: 8,
      conversionRate: 0.6,
    },
    tags: ['潜力客户', 'B级客户', '欧洲市场'],
  },
];

// 模拟产品推荐
const mockProductRecommendations: Recommendation[] = [
  {
    id: '1',
    type: 'product',
    targetId: 'prod_001',
    targetName: '智能控制器X2',
    score: 0.92,
    reason: '基于客户历史询盘记录，该产品与客户需求高度匹配',
    supportingData: {
      category: '工业自动化',
      price: 25000,
      features: ['无线连接', '智能诊断', '远程控制'],
      compatibility: '95%',
    },
    tags: ['热门产品', '高匹配度', '新技术'],
  },
  {
    id: '2',
    type: 'product',
    targetId: 'prod_002',
    targetName: '环保过滤材料M3',
    score: 0.85,
    reason: '相似客户经常询盘此产品，市场需求增长37%',
    supportingData: {
      category: '环保材料',
      price: 8500,
      features: ['高效过滤', '环保认证', '长寿命'],
      marketGrowth: 0.37,
    },
    tags: ['环保', '增长快', '认证齐全'],
  },
];

// 模拟营销策略推荐
const mockStrategyRecommendations: Recommendation[] = [
  {
    id: '1',
    type: 'strategy',
    targetId: 'strategy_001',
    targetName: 'VIP专属服务',
    score: 0.9,
    reason: 'A级客户享受最高优先级服务，提升客户满意度',
    supportingData: {
      targetCustomers: 'A级客户',
      expectedROI: '25%',
      implementationTime: '2周',
      resources: ['专属客户经理', '优先技术支持'],
    },
    tags: ['高价值客户', '服务升级', '客户保留'],
  },
  {
    id: '2',
    type: 'strategy',
    targetId: 'strategy_002',
    targetName: '定期跟进计划',
    score: 0.75,
    reason: 'B级客户需要定期维护关系，提升转化率',
    supportingData: {
      targetCustomers: 'B级客户',
      expectedROI: '15%',
      implementationTime: '1周',
      frequency: '每周一次',
    },
    tags: ['关系维护', '定期跟进', '转化提升'],
  },
];

// 模拟自动化服务动作
const mockAutoActions: AutoServiceAction[] = [
  {
    id: '1',
    actionType: 'classify',
    targetId: 'email_001',
    actionDescription: '邮件分类: 紧急询盘, 优先级: 5',
    priority: 5,
    status: 'pending',
  },
  {
    id: '2',
    actionType: 'respond',
    targetId: 'inquiry_001',
    actionDescription: '自动回复建议: 工业设备询盘',
    priority: 4,
    suggestedResponse: '感谢您对我们工业设备的询盘。我们的销售团队将在24小时内与您联系...',
    status: 'pending',
  },
  {
    id: '3',
    actionType: 'follow_up',
    targetId: 'cust_003',
    actionDescription: '高价值客户John Smith需要专属客户经理主动联系',
    priority: 5,
    followUpDate: '2024-01-16',
    status: 'in_progress',
  },
];

/**
 * 智能推荐页面组件
 */
const RecommendationsPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [queryText, setQueryText] = useState('');
  const [queryResults, setQueryResults] = useState<QueryResult[]>(mockQueryHistory);
  const [selectedRecommendation, setSelectedRecommendation] = useState<Recommendation | null>(null);
  const [recommendationModalVisible, setRecommendationModalVisible] = useState(false);
  const [autoActionModalVisible, setAutoActionModalVisible] = useState(false);
  const [selectedAutoAction, setSelectedAutoAction] = useState<AutoServiceAction | null>(null);

  // 处理自然语言查询
  const handleQuery = async () => {
    if (!queryText.trim()) {
      message.warning('请输入查询内容');
      return;
    }

    setLoading(true);
    
    // 模拟API调用
    setTimeout(() => {
      const newResult: QueryResult = {
        id: Date.now().toString(),
        query: queryText,
        queryType: 'general',
        results: [
          { type: 'customer', name: 'Sample Customer', score: 0.85 },
          { type: 'product', name: 'Sample Product', score: 0.78 },
        ],
        confidence: 0.82,
        processingTime: 1.5,
        suggestions: ['建议查看相关客户详情', '可以分析产品需求趋势'],
        timestamp: new Date().toLocaleString(),
      };
      
      setQueryResults([newResult, ...queryResults]);
      setQueryText('');
      setLoading(false);
      message.success('查询完成');
    }, 1500);
  };

  // 查看推荐详情
  const handleViewRecommendation = (recommendation: Recommendation) => {
    setSelectedRecommendation(recommendation);
    setRecommendationModalVisible(true);
  };

  // 查看自动化动作详情
  const handleViewAutoAction = (action: AutoServiceAction) => {
    setSelectedAutoAction(action);
    setAutoActionModalVisible(true);
  };

  // 执行自动化动作
  const handleExecuteAction = () => {
    message.success('动作执行成功');
    // 这里可以调用API执行实际动作
  };

  // 获取推荐类型图标
  const getRecommendationIcon = (type: string) => {
    switch (type) {
      case 'customer': return <UserOutlined />;
      case 'product': return <ShoppingCartOutlined />;
      case 'strategy': return <BulbOutlined />;
      default: return <StarOutlined />;
    }
  };

  // 获取推荐类型颜色
  const getRecommendationColor = (type: string) => {
    switch (type) {
      case 'customer': return '#1890ff';
      case 'product': return '#52c41a';
      case 'strategy': return '#722ed1';
      default: return '#d9d9d9';
    }
  };

  // 获取优先级颜色
  const getPriorityColor = (priority: number) => {
    if (priority >= 5) return '#f5222d';
    if (priority >= 4) return '#fa8c16';
    if (priority >= 3) return '#fadb14';
    return '#52c41a';
  };

  // 获取状态颜色
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'in_progress': return 'processing';
      case 'pending': return 'warning';
      default: return 'default';
    }
  };

  return (
    <div>
      {/* 智能查询区域 */}
      <Card 
        title={<><RobotOutlined /> 智能问答系统</>}
        style={{ marginBottom: 24 }}
      >
        <Row gutter={16}>
          <Col span={18}>
            <Search
              placeholder="请输入您的问题，例如：哪些客户对XX产品最感兴趣？最近热门的产品有哪些？"
              value={queryText}
              onChange={(e) => setQueryText(e.target.value)}
              onSearch={handleQuery}
              enterButton={<><SendOutlined /> 查询</>}
              size="large"
              loading={loading}
            />
          </Col>
          <Col span={6}>
            <Space>
              <Button 
                icon={<HistoryOutlined />}
                onClick={() => message.info('查询历史功能')}
              >
                查询历史
              </Button>
              <Button 
                icon={<QuestionCircleOutlined />}
                onClick={() => message.info('帮助文档')}
              >
                帮助
              </Button>
            </Space>
          </Col>
        </Row>
        
        {/* 常用查询建议 */}
        <div style={{ marginTop: 16 }}>
          <Text type="secondary">常用查询：</Text>
          <Space wrap style={{ marginTop: 8 }}>
            {[
              '哪些客户对工业设备最感兴趣？',
              '最近3个月热门产品排行',
              'A级客户的共同需求特征',
              '欧洲市场的需求趋势',
              '高价值客户推荐策略'
            ].map((suggestion, index) => (
              <Tag 
                key={index}
                style={{ cursor: 'pointer' }}
                onClick={() => setQueryText(suggestion)}
              >
                {suggestion}
              </Tag>
            ))}
          </Space>
        </div>
      </Card>

      {/* 主要内容选项卡 */}
      <Tabs 
        defaultActiveKey="recommendations" 
        type="card"
        items={[
          {
            key: 'recommendations',
            label: <><StarOutlined /> 智能推荐</>,
            children: (
          <Row gutter={16}>
            {/* 客户推荐 */}
            <Col span={8}>
              <Card 
                title={<><UserOutlined /> 客户推荐</>}
                extra={<Badge count={mockCustomerRecommendations.length} />}
                style={{ marginBottom: 16 }}
              >
                <List
                  dataSource={mockCustomerRecommendations}
                  renderItem={(item) => (
                    <List.Item
                      actions={[
                        <Button 
                          type="link" 
                          size="small"
                          onClick={() => handleViewRecommendation(item)}
                        >
                          查看详情
                        </Button>
                      ]}
                    >
                      <List.Item.Meta
                        avatar={<Avatar icon={<UserOutlined />} />}
                        title={
                          <div>
                            <span>{item.targetName}</span>
                            <Rate 
                              disabled 
                              defaultValue={Math.round(item.score * 5)} 
                              style={{ marginLeft: 8, fontSize: '12px' }}
                            />
                          </div>
                        }
                        description={
                          <div>
                            <div style={{ marginBottom: 4 }}>
                              {item.supportingData.company} - {item.supportingData.country}
                            </div>
                            <div style={{ fontSize: '12px', color: '#666' }}>
                              {item.reason}
                            </div>
                            <div style={{ marginTop: 4 }}>
                              {item.tags.map(tag => (
                                <Tag key={tag}>{tag}</Tag>
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

            {/* 产品推荐 */}
            <Col span={8}>
              <Card 
                title={<><ShoppingCartOutlined /> 产品推荐</>}
                extra={<Badge count={mockProductRecommendations.length} />}
                style={{ marginBottom: 16 }}
              >
                <List
                  dataSource={mockProductRecommendations}
                  renderItem={(item) => (
                    <List.Item
                      actions={[
                        <Button 
                          type="link" 
                          size="small"
                          onClick={() => handleViewRecommendation(item)}
                        >
                          查看详情
                        </Button>
                      ]}
                    >
                      <List.Item.Meta
                        avatar={<Avatar icon={<ShoppingCartOutlined />} style={{ backgroundColor: '#52c41a' }} />}
                        title={
                          <div>
                            <span>{item.targetName}</span>
                            <Progress 
                              percent={Math.round(item.score * 100)} 
                              size="small" 
                              style={{ marginLeft: 8, width: 60 }}
                              showInfo={false}
                            />
                          </div>
                        }
                        description={
                          <div>
                            <div style={{ marginBottom: 4 }}>
                              {item.supportingData.category} - ${item.supportingData.price.toLocaleString()}
                            </div>
                            <div style={{ fontSize: '12px', color: '#666' }}>
                              {item.reason}
                            </div>
                            <div style={{ marginTop: 4 }}>
                              {item.tags.map(tag => (
                                <Tag key={tag} color="green">{tag}</Tag>
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

            {/* 营销策略推荐 */}
            <Col span={8}>
              <Card 
                title={<><BulbOutlined /> 营销策略</>}
                extra={<Badge count={mockStrategyRecommendations.length} />}
                style={{ marginBottom: 16 }}
              >
                <List
                  dataSource={mockStrategyRecommendations}
                  renderItem={(item) => (
                    <List.Item
                      actions={[
                        <Button 
                          type="link" 
                          size="small"
                          onClick={() => handleViewRecommendation(item)}
                        >
                          查看详情
                        </Button>
                      ]}
                    >
                      <List.Item.Meta
                        avatar={<Avatar icon={<BulbOutlined />} style={{ backgroundColor: '#722ed1' }} />}
                        title={
                          <div>
                            <span>{item.targetName}</span>
                            <Tag color="purple" style={{ marginLeft: 8 }}>
                              {Math.round(item.score * 100)}分
                            </Tag>
                          </div>
                        }
                        description={
                          <div>
                            <div style={{ fontSize: '12px', color: '#666', marginBottom: 4 }}>
                              {item.reason}
                            </div>
                            <div>
                              预期ROI: <strong>{item.supportingData.expectedROI}</strong>
                            </div>
                            <div style={{ marginTop: 4 }}>
                              {item.tags.map(tag => (
                                <Tag key={tag} color="purple">{tag}</Tag>
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
          </Row>
            ),
          },
          {
            key: 'automation',
            label: <><ThunderboltOutlined /> 自动化服务</>,
            children: (
          <Row gutter={16}>
            <Col span={16}>
              <Card title="待处理任务">
                <List
                  dataSource={mockAutoActions.filter(action => action.status !== 'completed')}
                  renderItem={(item) => (
                    <List.Item
                      actions={[
                        <Button 
                          type="primary" 
                          size="small"
                          onClick={() => handleExecuteAction()}
                        >
                          执行
                        </Button>,
                        <Button 
                          type="link" 
                          size="small"
                          onClick={() => handleViewAutoAction(item)}
                        >
                          详情
                        </Button>
                      ]}
                    >
                      <List.Item.Meta
                        avatar={
                          <Badge 
                            count={item.priority} 
                            style={{ backgroundColor: getPriorityColor(item.priority) }}
                          >
                            <Avatar icon={<ThunderboltOutlined />} />
                          </Badge>
                        }
                        title={
                          <div>
                            <span>{item.actionDescription}</span>
                            <Badge 
                              status={getStatusColor(item.status) as any} 
                              text={
                                item.status === 'pending' ? '待处理' :
                                item.status === 'in_progress' ? '处理中' : '已完成'
                              }
                              style={{ marginLeft: 12 }}
                            />
                          </div>
                        }
                        description={
                          <div>
                            <div>类型: {item.actionType === 'classify' ? '邮件分类' : 
                                      item.actionType === 'respond' ? '自动回复' : 
                                      item.actionType === 'follow_up' ? '跟进提醒' : '优先级排序'}</div>
                            {item.followUpDate && (
                              <div>跟进日期: {item.followUpDate}</div>
                            )}
                          </div>
                        }
                      />
                    </List.Item>
                  )}
                />
              </Card>
            </Col>
            <Col span={8}>
              <Card title="自动化统计">
                <Row gutter={16}>
                  <Col span={12}>
                    <div style={{ textAlign: 'center', padding: '16px' }}>
                      <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#1890ff' }}>
                        {mockAutoActions.filter(a => a.status === 'pending').length}
                      </div>
                      <div>待处理</div>
                    </div>
                  </Col>
                  <Col span={12}>
                    <div style={{ textAlign: 'center', padding: '16px' }}>
                      <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#52c41a' }}>
                        {mockAutoActions.filter(a => a.status === 'completed').length}
                      </div>
                      <div>已完成</div>
                    </div>
                  </Col>
                </Row>
                <Divider />
                <div>
                  <div style={{ marginBottom: 8 }}>今日处理效率</div>
                  <Progress percent={85} strokeColor="#52c41a" />
                </div>
                <div style={{ marginTop: 16 }}>
                  <div style={{ marginBottom: 8 }}>平均响应时间</div>
                  <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#1890ff' }}>
                    2.3 小时
                  </div>
                </div>
              </Card>
            </Col>
          </Row>
            ),
          },
          {
            key: 'history',
            label: <><HistoryOutlined /> 查询历史</>,
            children: (
          <Card title="查询历史记录">
            <List
              dataSource={queryResults}
              renderItem={(item) => (
                <List.Item>
                  <List.Item.Meta
                    avatar={<Avatar icon={<SearchOutlined />} />}
                    title={
                      <div>
                        <span>{item.query}</span>
                        <Tag color="blue" style={{ marginLeft: 8 }}>
                          置信度: {Math.round(item.confidence * 100)}%
                        </Tag>
                        <Tag color="green">
                          {item.processingTime}s
                        </Tag>
                      </div>
                    }
                    description={
                      <div>
                        <div style={{ marginBottom: 8 }}>
                          <ClockCircleOutlined style={{ marginRight: 4 }} />
                          {item.timestamp}
                        </div>
                        <div style={{ marginBottom: 8 }}>
                          找到 <strong>{item.results.length}</strong> 个结果
                        </div>
                        <div>
                          <Text type="secondary">建议: </Text>
                          {item.suggestions.slice(0, 2).map((suggestion, index) => (
                            <Tag key={index}>{suggestion}</Tag>
                          ))}
                        </div>
                      </div>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>
            ),
          },
        ]}
      />

      {/* 推荐详情模态框 */}
      <Modal
        title="推荐详情"
        open={recommendationModalVisible}
        onCancel={() => setRecommendationModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setRecommendationModalVisible(false)}>
            关闭
          </Button>,
          <Button key="action" type="primary">
            采纳推荐
          </Button>
        ]}
        width={600}
      >
        {selectedRecommendation && (
          <div>
            <Row gutter={16} style={{ marginBottom: 16 }}>
              <Col span={4}>
                <Avatar 
                  size={64} 
                  icon={getRecommendationIcon(selectedRecommendation.type)}
                  style={{ backgroundColor: getRecommendationColor(selectedRecommendation.type) }}
                />
              </Col>
              <Col span={20}>
                <Title level={4}>{selectedRecommendation.targetName}</Title>
                <div style={{ marginBottom: 8 }}>
                  <Rate disabled defaultValue={Math.round(selectedRecommendation.score * 5)} />
                  <span style={{ marginLeft: 8 }}>推荐分数: {Math.round(selectedRecommendation.score * 100)}</span>
                </div>
                <div>
                  {selectedRecommendation.tags.map(tag => (
                    <Tag key={tag} color={getRecommendationColor(selectedRecommendation.type)}>
                      {tag}
                    </Tag>
                  ))}
                </div>
              </Col>
            </Row>
            
            <Descriptions title="推荐理由" column={1}>
              <Descriptions.Item label="推荐原因">
                {selectedRecommendation.reason}
              </Descriptions.Item>
            </Descriptions>
            
            <Divider />
            
            <Descriptions title="支持数据" column={2}>
              {Object.entries(selectedRecommendation.supportingData).map(([key, value]) => (
                <Descriptions.Item key={key} label={key}>
                  {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                </Descriptions.Item>
              ))}
            </Descriptions>
          </div>
        )}
      </Modal>

      {/* 自动化动作详情模态框 */}
      <Modal
        title="自动化任务详情"
        open={autoActionModalVisible}
        onCancel={() => setAutoActionModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setAutoActionModalVisible(false)}>
            关闭
          </Button>,
          <Button key="execute" type="primary" onClick={() => {
            if (selectedAutoAction) {
              handleExecuteAction();
              setAutoActionModalVisible(false);
            }
          }}>
            立即执行
          </Button>
        ]}
        width={600}
      >
        {selectedAutoAction && (
          <div>
            <Descriptions column={1}>
              <Descriptions.Item label="任务类型">
                {selectedAutoAction.actionType === 'classify' ? '邮件分类' : 
                 selectedAutoAction.actionType === 'respond' ? '自动回复' : 
                 selectedAutoAction.actionType === 'follow_up' ? '跟进提醒' : '优先级排序'}
              </Descriptions.Item>
              <Descriptions.Item label="任务描述">
                {selectedAutoAction.actionDescription}
              </Descriptions.Item>
              <Descriptions.Item label="优先级">
                <Badge 
                  count={selectedAutoAction.priority} 
                  style={{ backgroundColor: getPriorityColor(selectedAutoAction.priority) }}
                />
              </Descriptions.Item>
              <Descriptions.Item label="状态">
                <Badge 
                  status={getStatusColor(selectedAutoAction.status) as any} 
                  text={
                    selectedAutoAction.status === 'pending' ? '待处理' :
                    selectedAutoAction.status === 'in_progress' ? '处理中' : '已完成'
                  }
                />
              </Descriptions.Item>
              {selectedAutoAction.followUpDate && (
                <Descriptions.Item label="跟进日期">
                  {selectedAutoAction.followUpDate}
                </Descriptions.Item>
              )}
            </Descriptions>
            
            {selectedAutoAction.suggestedResponse && (
              <div style={{ marginTop: 16 }}>
                <Title level={5}>建议回复内容</Title>
                <TextArea 
                  value={selectedAutoAction.suggestedResponse}
                  rows={4}
                  readOnly
                />
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
};

export default RecommendationsPage;