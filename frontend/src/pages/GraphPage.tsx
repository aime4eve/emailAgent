/**
 * 知识图谱可视化页面
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Card,
  Row,
  Col,
  Button,
  Input,
  Select,
  Space,
  Typography,
  Spin,
  message,
  Drawer,
  Descriptions,
  Tag,
  Slider,
  Switch,
  Tooltip,
  Empty,
} from 'antd';
import {
  SearchOutlined,
  FullscreenOutlined,
  DownloadOutlined,
  SettingOutlined,
  ReloadOutlined,
  ZoomInOutlined,
  ZoomOutOutlined,
} from '@ant-design/icons';
import * as d3 from 'd3';
import { graphService } from '../services';
import type { KnowledgeGraphData, GraphNode, GraphEdge } from '../types';

const { Title, Text } = Typography;
const { Option } = Select;

/**
 * 知识图谱可视化页面组件
 */
const GraphPage: React.FC = () => {
  // 状态管理
  const [loading, setLoading] = useState<boolean>(false);
  const [graphData, setGraphData] = useState<KnowledgeGraphData | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedNodeType, setSelectedNodeType] = useState<string>('all');
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [drawerVisible, setDrawerVisible] = useState<boolean>(false);
  const [settingsVisible, setSettingsVisible] = useState<boolean>(false);
  
  // 图谱配置
  const [graphConfig, setGraphConfig] = useState({
    nodeSize: 8,
    linkDistance: 100,
    charge: -300,
    showLabels: true,
    showArrows: true,
  });

  // D3 相关引用
  const svgRef = useRef<SVGSVGElement>(null);
  const simulationRef = useRef<d3.Simulation<GraphNode, GraphEdge> | null>(null);

  /**
   * 加载图谱数据
   */
  const loadGraphData = useCallback(async () => {
    setLoading(true);
    try {
      // 暂时使用模拟数据，因为后端图谱API尚未实现
      const mockData: KnowledgeGraphData = {
        nodes: [
          { id: '1', label: '张三', type: 'PERSON', properties: { age: 30 } },
          { id: '2', label: '李四', type: 'PERSON', properties: { age: 25 } },
          { id: '3', label: '北京公司', type: 'ORGANIZATION', properties: { industry: '科技' } },
          { id: '4', label: '项目A', type: 'CONCEPT', properties: { status: '进行中' } },
        ],
        edges: [
          { id: 'e1', source: '1', target: '3', label: '工作于', type: 'WORKS_AT', weight: 1 },
          { id: 'e2', source: '2', target: '3', label: '工作于', type: 'WORKS_AT', weight: 1 },
          { id: 'e3', source: '1', target: '4', label: '负责', type: 'RESPONSIBLE_FOR', weight: 1 },
        ],
        metadata: {
          nodeCount: 4,
          edgeCount: 3,
          lastUpdated: new Date().toISOString(),
        },
      };
      
      setGraphData(mockData);
      message.success('图谱数据加载成功（模拟数据）');
    } catch (error) {
      message.error('加载图谱数据时发生错误');
      console.error('Load graph data error:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * 搜索图谱
   */
  const handleSearch = useCallback(async () => {
    if (!searchQuery.trim()) {
      loadGraphData();
      return;
    }

    setLoading(true);
    try {
      // 暂时使用本地搜索，因为后端搜索API尚未实现
      if (graphData) {
        const filteredNodes = graphData.nodes.filter(node => 
          node.label.toLowerCase().includes(searchQuery.toLowerCase()) ||
          node.type.toLowerCase().includes(searchQuery.toLowerCase())
        );
        
        const nodeIds = new Set(filteredNodes.map(node => node.id));
        const filteredEdges = graphData.edges.filter(edge => 
          nodeIds.has(edge.source as string) || nodeIds.has(edge.target as string)
        );
        
        const filteredData: KnowledgeGraphData = {
          ...graphData,
          nodes: filteredNodes,
          edges: filteredEdges,
        };
        
        setGraphData(filteredData);
        message.success(`找到 ${filteredNodes.length} 个相关节点`);
      } else {
        message.warning('请先加载图谱数据');
      }
    } catch (error) {
      message.error('搜索时发生错误');
      console.error('Search graph error:', error);
    } finally {
      setLoading(false);
    }
  }, [searchQuery, loadGraphData, graphData]);

  /**
   * 初始化D3图谱
   */
  const initializeGraph = useCallback(() => {
    if (!graphData || !svgRef.current) return;

    const svg = d3.select(svgRef.current);
    const width = 800;
    const height = 600;

    // 清空之前的内容
    svg.selectAll('*').remove();

    // 设置SVG尺寸
    svg.attr('width', width).attr('height', height);

    // 创建缩放行为
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => {
        container.attr('transform', event.transform);
      });

    svg.call(zoom);

    // 创建容器组
    const container = svg.append('g');

    // 创建箭头标记
    const defs = svg.append('defs');
    defs.append('marker')
      .attr('id', 'arrowhead')
      .attr('viewBox', '-0 -5 10 10')
      .attr('refX', 13)
      .attr('refY', 0)
      .attr('orient', 'auto')
      .attr('markerWidth', 13)
      .attr('markerHeight', 13)
      .attr('xoverflow', 'visible')
      .append('svg:path')
      .attr('d', 'M 0,-5 L 10 ,0 L 0,5')
      .attr('fill', '#999')
      .style('stroke', 'none');

    // 创建力导向布局
    const simulation = d3.forceSimulation<GraphNode>(graphData.nodes)
      .force('link', d3.forceLink<GraphNode, GraphEdge>(graphData.edges)
        .id((d) => d.id)
        .distance(graphConfig.linkDistance)
      )
      .force('charge', d3.forceManyBody().strength(graphConfig.charge))
      .force('center', d3.forceCenter(width / 2, height / 2));

    simulationRef.current = simulation;

    // 创建连线
    const link = container.append('g')
      .attr('class', 'links')
      .selectAll('line')
      .data(graphData.edges)
      .enter().append('line')
      .attr('stroke', '#999')
      .attr('stroke-opacity', 0.6)
      .attr('stroke-width', (d) => Math.sqrt(d.weight || 1))
      .attr('marker-end', graphConfig.showArrows ? 'url(#arrowhead)' : null);

    // 节点颜色映射
    const nodeColors: Record<string, string> = {
      PERSON: '#1890ff',
      ORGANIZATION: '#52c41a',
      LOCATION: '#fa8c16',
      TIME: '#722ed1',
      EVENT: '#f5222d',
      CONCEPT: '#13c2c2',
    };

    // 创建节点
    const node = container.append('g')
      .attr('class', 'nodes')
      .selectAll('circle')
      .data(graphData.nodes)
      .enter().append('circle')
      .attr('r', graphConfig.nodeSize)
      .attr('fill', (d) => nodeColors[d.type] || '#666')
      .attr('stroke', '#fff')
      .attr('stroke-width', 2)
      .style('cursor', 'pointer')
      .call(d3.drag<SVGCircleElement, GraphNode>()
        .on('start', (event, d) => {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
        })
        .on('drag', (event, d) => {
          d.fx = event.x;
          d.fy = event.y;
        })
        .on('end', (event, d) => {
          if (!event.active) simulation.alphaTarget(0);
          d.fx = null;
          d.fy = null;
        })
      )
      .on('click', (_, d) => {
        setSelectedNode(d);
        setDrawerVisible(true);
      })
      .on('mouseover', function() {
        d3.select(this).attr('r', graphConfig.nodeSize * 1.5);
      })
      .on('mouseout', function() {
        d3.select(this).attr('r', graphConfig.nodeSize);
      });

    // 创建标签
    const label = container.append('g')
      .attr('class', 'labels')
      .selectAll('text')
      .data(graphData.nodes)
      .enter().append('text')
      .text((d) => d.label)
      .style('font-size', '12px')
      .style('fill', '#333')
      .style('text-anchor', 'middle')
      .style('pointer-events', 'none')
      .style('display', graphConfig.showLabels ? 'block' : 'none');

    // 更新位置
    simulation.on('tick', () => {
      link
        .attr('x1', (d: any) => (d.source.x || 0))
        .attr('y1', (d: any) => (d.source.y || 0))
        .attr('x2', (d: any) => (d.target.x || 0))
        .attr('y2', (d: any) => (d.target.y || 0));

      node
        .attr('cx', (d) => d.x || 0)
        .attr('cy', (d) => d.y || 0);

      label
        .attr('x', (d) => d.x || 0)
        .attr('y', (d) => (d.y || 0) + graphConfig.nodeSize + 15);
    });

  }, [graphData, graphConfig]);

  /**
   * 导出图谱
   */
  const handleExportGraph = useCallback(async () => {
    if (!graphData) {
      message.warning('没有可导出的图谱数据');
      return;
    }

    try {
      const response = await graphService.exportGraph('json');
      if (response.success && response.data) {
        const url = URL.createObjectURL(response.data);
        const link = document.createElement('a');
        link.href = url;
        link.download = `knowledge_graph_${new Date().getTime()}.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        message.success('图谱已导出');
      } else {
        message.error(response.error || '导出失败');
      }
    } catch (error) {
      message.error('导出时发生错误');
      console.error('Export graph error:', error);
    }
  }, [graphData]);

  /**
   * 缩放控制
   */
  const handleZoom = (scale: number) => {
    if (svgRef.current) {
      const svg = d3.select(svgRef.current);
      svg.transition().duration(300).call(
        d3.zoom<SVGSVGElement, unknown>().scaleBy as any,
        scale
      );
    }
  };

  // 组件挂载时加载数据
  useEffect(() => {
    loadGraphData();
  }, [loadGraphData]);

  // 图谱数据变化时重新初始化
  useEffect(() => {
    initializeGraph();
  }, [initializeGraph]);

  // 获取节点类型列表
  const nodeTypes = graphData ? 
    Array.from(new Set(graphData.nodes.map(node => node.type))) : [];

  return (
    <div>
      <Row gutter={[24, 24]}>
        <Col span={24}>
          <Card>
            <div className="flex-between mb-16">
              <Title level={2} style={{ margin: 0 }}>
                知识图谱
              </Title>
              <Space>
                <Button
                  icon={<ReloadOutlined />}
                  onClick={loadGraphData}
                  loading={loading}
                >
                  刷新
                </Button>
                <Button
                  icon={<SettingOutlined />}
                  onClick={() => setSettingsVisible(true)}
                >
                  设置
                </Button>
                <Button
                  type="primary"
                  icon={<DownloadOutlined />}
                  onClick={handleExportGraph}
                  disabled={!graphData}
                >
                  导出
                </Button>
              </Space>
            </div>
            
            {/* 搜索和筛选 */}
            <Row gutter={16} className="mb-16">
              <Col span={12}>
                <Input.Search
                  placeholder="搜索节点或关系..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onSearch={handleSearch}
                  enterButton={<SearchOutlined />}
                  loading={loading}
                />
              </Col>
              <Col span={6}>
                <Select
                  value={selectedNodeType}
                  onChange={setSelectedNodeType}
                  style={{ width: '100%' }}
                  placeholder="选择节点类型"
                >
                  <Option value="all">所有类型</Option>
                  {nodeTypes.map(type => (
                    <Option key={type} value={type}>{type}</Option>
                  ))}
                </Select>
              </Col>
              <Col span={6}>
                <Space>
                  <Tooltip title="放大">
                    <Button
                      icon={<ZoomInOutlined />}
                      onClick={() => handleZoom(1.2)}
                    />
                  </Tooltip>
                  <Tooltip title="缩小">
                    <Button
                      icon={<ZoomOutOutlined />}
                      onClick={() => handleZoom(0.8)}
                    />
                  </Tooltip>
                  <Tooltip title="全屏">
                    <Button icon={<FullscreenOutlined />} />
                  </Tooltip>
                </Space>
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>

      <Row gutter={[24, 24]} style={{ marginTop: 24 }}>
        <Col span={24}>
          <Card title="图谱可视化" className="graph-container">
            <Spin spinning={loading}>
              {graphData && graphData.nodes.length > 0 ? (
                <div style={{ width: '100%', height: '600px', overflow: 'hidden' }}>
                  <svg ref={svgRef} style={{ width: '100%', height: '100%' }} />
                </div>
              ) : (
                <Empty
                  description="暂无图谱数据"
                  image={Empty.PRESENTED_IMAGE_SIMPLE}
                  style={{ padding: '100px 0' }}
                />
              )}
            </Spin>
          </Card>
        </Col>
      </Row>

      {/* 节点详情抽屉 */}
      <Drawer
        title="节点详情"
        placement="right"
        onClose={() => setDrawerVisible(false)}
        open={drawerVisible}
        width={400}
      >
        {selectedNode && (
          <div>
            <Descriptions column={1} bordered>
              <Descriptions.Item label="ID">{selectedNode.id}</Descriptions.Item>
              <Descriptions.Item label="标签">{selectedNode.label}</Descriptions.Item>
              <Descriptions.Item label="类型">
                <Tag color="blue">{selectedNode.type}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="权重">{selectedNode.weight}</Descriptions.Item>
              {selectedNode.properties && Object.keys(selectedNode.properties).length > 0 && (
                <Descriptions.Item label="属性">
                  {Object.entries(selectedNode.properties).map(([key, value]) => (
                    <div key={key}>
                      <Text strong>{key}:</Text> {String(value)}
                    </div>
                  ))}
                </Descriptions.Item>
              )}
            </Descriptions>
          </div>
        )}
      </Drawer>

      {/* 设置抽屉 */}
      <Drawer
        title="图谱设置"
        placement="right"
        onClose={() => setSettingsVisible(false)}
        open={settingsVisible}
        width={350}
      >
        <div>
          <div className="mb-24">
            <Text strong>节点大小</Text>
            <Slider
              min={4}
              max={20}
              value={graphConfig.nodeSize}
              onChange={(value) => setGraphConfig(prev => ({ ...prev, nodeSize: value }))}
              style={{ marginTop: 8 }}
            />
          </div>
          
          <div className="mb-24">
            <Text strong>连线距离</Text>
            <Slider
              min={50}
              max={200}
              value={graphConfig.linkDistance}
              onChange={(value) => setGraphConfig(prev => ({ ...prev, linkDistance: value }))}
              style={{ marginTop: 8 }}
            />
          </div>
          
          <div className="mb-24">
            <Text strong>节点斥力</Text>
            <Slider
              min={-500}
              max={-100}
              value={graphConfig.charge}
              onChange={(value) => setGraphConfig(prev => ({ ...prev, charge: value }))}
              style={{ marginTop: 8 }}
            />
          </div>
          
          <div className="mb-24">
            <div className="flex-between">
              <Text strong>显示标签</Text>
              <Switch
                checked={graphConfig.showLabels}
                onChange={(checked) => setGraphConfig(prev => ({ ...prev, showLabels: checked }))}
              />
            </div>
          </div>
          
          <div className="mb-24">
            <div className="flex-between">
              <Text strong>显示箭头</Text>
              <Switch
                checked={graphConfig.showArrows}
                onChange={(checked) => setGraphConfig(prev => ({ ...prev, showArrows: checked }))}
              />
            </div>
          </div>
        </div>
      </Drawer>
    </div>
  );
};

export default GraphPage;