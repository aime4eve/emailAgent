/**
 * 主应用组件
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import { Layout, Menu, Typography, Avatar, Dropdown, Space } from 'antd';
import {
  ExperimentOutlined,
  NodeIndexOutlined,
  DatabaseOutlined,
  BarChartOutlined,
  UserOutlined,
  SettingOutlined,
  LogoutOutlined,
  TeamOutlined,
  FundOutlined,
  BulbOutlined,
  RobotOutlined,
  AppstoreOutlined,
  ContactsOutlined,
  DashboardOutlined,
} from '@ant-design/icons';
import type { MenuProps } from 'antd';

// 页面组件（暂时使用占位符）
const ExtractionPage = React.lazy(() => import('./pages/ExtractionPage'));
const GraphPage = React.lazy(() => import('./pages/GraphPage'));
const OntologyPage = React.lazy(() => import('./pages/OntologyPage'));
const CustomersPage = React.lazy(() => import('./pages/CustomersPage'));
const AnalyticsPage = React.lazy(() => import('./pages/AnalyticsPage'));
const InsightsPage = React.lazy(() => import('./pages/InsightsPage'));
const RecommendationsPage = React.lazy(() => import('./pages/RecommendationsPage'));
const StatisticsPage = React.lazy(() => import('./pages/StatisticsPage'));

const { Header, Sider, Content } = Layout;
const { Title } = Typography;

/**
 * 应用内容组件
 */
const AppContent: React.FC = () => {
  const [collapsed, setCollapsed] = React.useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  
  // 根据当前路径设置选中的菜单项
  const getSelectedKey = () => {
    const path = location.pathname;
    if (path.includes('/extraction')) return 'extraction';
    if (path.includes('/graph')) return 'graph';
    if (path.includes('/ontology')) return 'ontology';
    if (path.includes('/customers')) return 'customers';
    if (path.includes('/analytics')) return 'analytics';
    if (path.includes('/insights')) return 'insights';
    if (path.includes('/recommendations')) return 'recommendations';
    if (path.includes('/statistics')) return 'statistics';
    return 'extraction';
  };
  
  const selectedKey = getSelectedKey();

  // 菜单项配置 - 分类结构
  const menuItems: MenuProps['items'] = [
    {
      key: 'core-functions',
      icon: <AppstoreOutlined />,
      label: '核心功能',
      type: 'group',
      children: [
        {
          key: 'extraction',
          icon: <ExperimentOutlined />,
          label: '知识抽取',
        },
        {
          key: 'graph',
          icon: <NodeIndexOutlined />,
          label: '知识图谱',
        },
        {
          key: 'ontology',
          icon: <DatabaseOutlined />,
          label: '本体管理',
        },
      ],
    },
    {
      key: 'customer-management',
      icon: <ContactsOutlined />,
      label: '客户管理',
      type: 'group',
      children: [
        {
          key: 'customers',
          icon: <TeamOutlined />,
          label: '客户管理',
        },
        {
          key: 'analytics',
          icon: <FundOutlined />,
          label: '客户分析',
        },
      ],
    },
    {
      key: 'analysis-insights',
      icon: <DashboardOutlined />,
      label: '分析洞察',
      type: 'group',
      children: [
        {
          key: 'insights',
          icon: <BulbOutlined />,
          label: '需求洞察',
        },
        {
          key: 'recommendations',
          icon: <RobotOutlined />,
          label: '智能推荐',
        },
        {
          key: 'statistics',
          icon: <BarChartOutlined />,
          label: '统计分析',
        },
      ],
    },
  ];

  // 获取所有菜单项的扁平化列表（用于标题显示）
  const getAllMenuItems = () => {
    const items: { key: string; label: string }[] = [];
    menuItems.forEach(group => {
      if (group && 'children' in group && group.children) {
        group.children.forEach(child => {
          if (child && 'key' in child && 'label' in child) {
            items.push({ key: child.key as string, label: child.label as string });
          }
        });
      }
    });
    return items;
  };

  const allMenuItems = getAllMenuItems();

  // 用户下拉菜单
  const userMenuItems: MenuProps['items'] = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: '个人资料',
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: '系统设置',
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
    },
  ];

  // 处理菜单点击
  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(`/${key}`);
  };

  // 处理用户菜单点击
  const handleUserMenuClick = ({ key }: { key: string }) => {
    switch (key) {
      case 'logout':
        // 处理退出登录
        console.log('退出登录');
        break;
      default:
        console.log('点击了:', key);
    }
  };



  return (
    <Layout className="full-height">
        {/* 侧边栏 */}
        <Sider
          collapsible
          collapsed={collapsed}
          onCollapse={setCollapsed}
          width={240}
          theme="light"
        >
          <div
            style={{
              height: 64,
              display: 'flex',
              alignItems: 'center',
              justifyContent: collapsed ? 'center' : 'flex-start',
              padding: collapsed ? 0 : '0 24px',
              borderBottom: '1px solid #f0f0f0',
            }}
          >
            {!collapsed && (
              <Title level={4} style={{ margin: 0, color: '#1890ff' }}>
                知识图谱系统
              </Title>
            )}
            {collapsed && (
              <div
                style={{
                  width: 32,
                  height: 32,
                  background: '#1890ff',
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#fff',
                  fontWeight: 'bold',
                }}
              >
                知
              </div>
            )}
          </div>
          <Menu
            mode="inline"
            selectedKeys={[selectedKey]}
            items={menuItems}
            onClick={handleMenuClick}
            style={{ borderRight: 'none', marginTop: 16 }}
          />
        </Sider>

        <Layout>
          {/* 头部 */}
          <Header
            style={{
              padding: '0 24px',
              background: '#fff',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              borderBottom: '1px solid #f0f0f0',
            }}
          >
            <div>
              <Title level={3} style={{ margin: 0 }}>
                {(() => {
                  const item = allMenuItems.find(item => item.key === selectedKey);
                  return item ? item.label : '知识图谱系统';
                })()}
              </Title>
            </div>
            <div>
              <Dropdown
                menu={{
                  items: userMenuItems,
                  onClick: handleUserMenuClick,
                }}
                placement="bottomRight"
              >
                <Space style={{ cursor: 'pointer' }}>
                  <Avatar icon={<UserOutlined />} />
                  <span>管理员</span>
                </Space>
              </Dropdown>
            </div>
          </Header>

          {/* 内容区域 */}
          <Content
            style={{
              margin: '24px',
              padding: '24px',
              background: '#fff',
              borderRadius: '8px',
              minHeight: 'calc(100vh - 112px)',
              overflow: 'auto',
            }}
          >
            <React.Suspense
              fallback={
                <div className="loading-container">
                  <div>加载中...</div>
                </div>
              }
            >
              <Routes>
                <Route path="/" element={<Navigate to="/extraction" replace />} />
                <Route path="/extraction" element={<ExtractionPage />} />
                <Route path="/graph" element={<GraphPage />} />
                <Route path="/ontology" element={<OntologyPage />} />
                <Route path="/customers" element={<CustomersPage />} />
                <Route path="/analytics" element={<AnalyticsPage />} />
                <Route path="/insights" element={<InsightsPage />} />
                <Route path="/recommendations" element={<RecommendationsPage />} />
                <Route path="/statistics" element={<StatisticsPage />} />
                <Route path="*" element={<Navigate to="/extraction" replace />} />
              </Routes>
            </React.Suspense>
          </Content>
        </Layout>
      </Layout>
  );
};

/**
 * 主应用组件
 */
const App: React.FC = () => {
  return (
    <Router>
      <AppContent />
    </Router>
  );
};

export default App;