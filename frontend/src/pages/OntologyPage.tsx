/**
 * 本体管理页面
 */

import React from 'react';
import { Typography } from 'antd';
import OntologyManagement from '../components/OntologyManagement';

const { Title } = Typography;

/**
 * 本体管理页面组件
 */
const OntologyPage: React.FC = () => {
  return (
    <div style={{ padding: '24px' }}>
      <div style={{ marginBottom: '24px' }}>
        <Title level={2}>知识本体管理</Title>
      </div>
      <OntologyManagement />
    </div>
  );
};

export default OntologyPage;