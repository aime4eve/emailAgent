/**
 * 主应用组件
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Layout, Menu, Typography, Avatar, Dropdown, Space } from 'antd';
import {
  ExperimentOutlined,
  NodeIndexOutlined,
  DatabaseOutlined,
  BarChartOutlined,
  UserOutlined,
  SettingOutlined,
  LogoutOutlined,
} from '@ant-design/icons';
import type { MenuProps } from 'antd';

// 页面组件（暂时使用占位符）
const ExtractionPage = React.lazy(() => import('./pages/ExtractionPage'));
const GraphPage = React.lazy(() => import('./pages/GraphPage'));
const OntologyPage = React.lazy(() => import('./pages/OntologyPage'));
const StatisticsPage = React.lazy(() => import('./pages/StatisticsPage'));

const { Header, Sider, Content } = Layout;
const { Title } = Typography;

/**
 * 主应用组件
 */
const App: React.FC = () => {
  const [collapsed, setCollapsed] = React.useState(false);
  const [selectedKey, setSelectedKey] = React.useState('extraction');

  // 菜单项配置
  const menuItems: MenuProps['items'] = [
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
    {
      key: 'statistics',
      icon: <BarChartOutlined />,
      label: '统计分析',
    },
  ];

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
    setSelectedKey(key);
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
    <Router>
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
                  const item = menuItems.find(item => item && 'key' in item && item.key === selectedKey);
                  return item && 'label' in item ? item.label : '知识图谱系统';
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
                <Route path="/statistics" element={<StatisticsPage />} />
                <Route path="*" element={<Navigate to="/extraction" replace />} />
              </Routes>
            </React.Suspense>
          </Content>
        </Layout>
      </Layout>
    </Router>
  );
};

export default App;