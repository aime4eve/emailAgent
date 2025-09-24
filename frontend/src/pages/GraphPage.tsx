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
  Alert,
  Dropdown,
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
import { knowledgeGraphStore } from '../services/knowledgeGraphStore';
import { getEntityTypeColor } from '../utils/graphDataConverter';
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
  const [selectedEdgeType, setSelectedEdgeType] = useState<string>('all');
  const [minConfidence, setMinConfidence] = useState<number>(0);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [highlightedNodes, setHighlightedNodes] = useState<Set<string>>(new Set());
  const [highlightedEdges, setHighlightedEdges] = useState<Set<string>>(new Set());
  const [drawerVisible, setDrawerVisible] = useState<boolean>(false);
  const [settingsVisible, setSettingsVisible] = useState<boolean>(false);
  const [originalGraphData, setOriginalGraphData] = useState<KnowledgeGraphData | null>(null);
  
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
      // 从存储中获取图谱数据
      const storedGraphData = knowledgeGraphStore.getMergedGraphData();
      
      if (storedGraphData && storedGraphData.nodes.length > 0 && storedGraphData.edges.length > 0) {
         setOriginalGraphData(storedGraphData);
         setGraphData(storedGraphData);
         message.success(`图谱数据加载成功：${storedGraphData.nodes.length} 个节点，${storedGraphData.edges.length} 个关系`);
       } else {
        // 如果没有存储数据，使用模拟数据
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
            node_count: 4,
            edge_count: 3,
            updated_at: new Date().toISOString(),
          },
        };
        
        setOriginalGraphData(mockData);
        setGraphData(mockData);
        message.info('使用示例数据，请先进行知识抽取以生成真实图谱数据');
      }
    } catch (error) {
      message.error('加载图谱数据时发生错误');
      console.error('Load graph data error:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * 应用筛选条件
   */
  const applyFilters = useCallback(() => {
    if (!originalGraphData) return;

    let filteredNodes = [...originalGraphData.nodes];
    let filteredEdges = [...originalGraphData.edges];

    // 按搜索关键词筛选
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filteredNodes = filteredNodes.filter(node => 
        node.label.toLowerCase().includes(query) ||
        node.type.toLowerCase().includes(query) ||
        Object.values(node.properties || {}).some(value => 
          String(value).toLowerCase().includes(query)
        )
      );
    }

    // 按节点类型筛选
    if (selectedNodeType !== 'all') {
      filteredNodes = filteredNodes.filter(node => node.type === selectedNodeType);
    }

    // 按置信度筛选
    if (minConfidence > 0) {
      filteredNodes = filteredNodes.filter(node => (node.weight || 0) >= minConfidence);
    }

    // 获取筛选后节点的ID集合
    const nodeIds = new Set(filteredNodes.map(node => node.id));

    // 筛选边：只保留两端节点都存在的边
    filteredEdges = filteredEdges.filter(edge => 
      nodeIds.has(edge.source as string) && nodeIds.has(edge.target as string)
    );

    // 按边类型筛选
    if (selectedEdgeType !== 'all') {
      filteredEdges = filteredEdges.filter(edge => edge.type === selectedEdgeType);
    }

    // 按边的置信度筛选
    if (minConfidence > 0) {
      filteredEdges = filteredEdges.filter(edge => (edge.weight || 0) >= minConfidence);
    }

    const filteredData: KnowledgeGraphData = {
      ...originalGraphData,
      nodes: filteredNodes,
      edges: filteredEdges,
      metadata: {
        ...originalGraphData.metadata,
        node_count: filteredNodes.length,
        edge_count: filteredEdges.length,
        updated_at: new Date().toISOString(),
      },
    };

    setGraphData(filteredData);
    
    if (searchQuery.trim() || selectedNodeType !== 'all' || selectedEdgeType !== 'all' || minConfidence > 0) {
      message.success(`筛选结果：${filteredNodes.length} 个节点，${filteredEdges.length} 个关系`);
    }
  }, [originalGraphData, searchQuery, selectedNodeType, selectedEdgeType, minConfidence]);

  /**
   * 重置筛选条件
   */
  const resetFilters = useCallback(() => {
    setSearchQuery('');
    setSelectedNodeType('all');
    setSelectedEdgeType('all');
    setMinConfidence(0);
    if (originalGraphData) {
      setGraphData(originalGraphData);
      message.info('已重置所有筛选条件');
    }
  }, [originalGraphData]);

  /**
   * 搜索图谱
   */
  const handleSearch = useCallback(() => {
    applyFilters();
  }, [applyFilters]);

  /**
   * 处理节点点击事件
   */
  const handleNodeClick = useCallback((node: GraphNode) => {
    setSelectedNode(node);
    setDrawerVisible(true);
    
    // 高亮相关节点和边
    if (graphData) {
      const connectedNodeIds = new Set<string>();
      const connectedEdgeIds = new Set<string>();
      
      // 找到与当前节点相连的所有边和节点
      graphData.edges.forEach(edge => {
        if (edge.source === node.id || (typeof edge.source === 'object' && edge.source.id === node.id)) {
          connectedEdgeIds.add(edge.id);
          const targetId = typeof edge.target === 'string' ? edge.target : edge.target.id;
          connectedNodeIds.add(targetId);
        }
        if (edge.target === node.id || (typeof edge.target === 'object' && edge.target.id === node.id)) {
          connectedEdgeIds.add(edge.id);
          const sourceId = typeof edge.source === 'string' ? edge.source : edge.source.id;
          connectedNodeIds.add(sourceId);
        }
      });
      
      // 包含当前节点
      connectedNodeIds.add(node.id);
      
      setHighlightedNodes(connectedNodeIds);
      setHighlightedEdges(connectedEdgeIds);
      
      // 更新可视化样式
      updateHighlightStyles(connectedNodeIds, connectedEdgeIds);
    }
  }, [graphData]);

  /**
   * 处理节点悬停事件
   */
  const handleNodeHover = useCallback((node: GraphNode, isHover: boolean) => {
    if (!graphData) return;
    
    if (isHover) {
      // 临时高亮相关节点和边
      const connectedNodeIds = new Set<string>();
      const connectedEdgeIds = new Set<string>();
      
      graphData.edges.forEach(edge => {
        if (edge.source === node.id || (typeof edge.source === 'object' && edge.source.id === node.id)) {
          connectedEdgeIds.add(edge.id);
          const targetId = typeof edge.target === 'string' ? edge.target : edge.target.id;
          connectedNodeIds.add(targetId);
        }
        if (edge.target === node.id || (typeof edge.target === 'object' && edge.target.id === node.id)) {
          connectedEdgeIds.add(edge.id);
          const sourceId = typeof edge.source === 'string' ? edge.source : edge.source.id;
          connectedNodeIds.add(sourceId);
        }
      });
      
      connectedNodeIds.add(node.id);
      updateHoverStyles(connectedNodeIds, connectedEdgeIds, true);
    } else {
      // 恢复正常样式
      updateHoverStyles(new Set(), new Set(), false);
    }
  }, [graphData]);

  /**
   * 更新高亮样式
   */
  const updateHighlightStyles = useCallback((nodeIds: Set<string>, edgeIds: Set<string>) => {
    if (!svgRef.current) return;
    
    const svg = d3.select(svgRef.current);
    
    // 更新节点样式
    svg.selectAll('.nodes circle')
      .style('opacity', (d: any) => nodeIds.has(d.id) ? 1 : 0.3)
      .style('stroke-width', (d: any) => nodeIds.has(d.id) ? 3 : 2);
    
    // 更新边样式
    svg.selectAll('.links line')
      .style('opacity', (d: any) => edgeIds.has(d.id) ? 1 : 0.1)
      .style('stroke-width', (d: any) => edgeIds.has(d.id) ? 3 : 1);
    
    // 更新标签样式
    svg.selectAll('.labels text')
      .style('opacity', (d: any) => nodeIds.has(d.id) ? 1 : 0.3)
      .style('font-weight', (d: any) => nodeIds.has(d.id) ? 'bold' : 'normal');
  }, []);

  /**
   * 更新悬停样式
   */
  const updateHoverStyles = useCallback((nodeIds: Set<string>, edgeIds: Set<string>, isHover: boolean) => {
    if (!svgRef.current) return;
    
    const svg = d3.select(svgRef.current);
    
    if (isHover) {
      // 应用悬停样式
      svg.selectAll('.nodes circle')
        .style('opacity', (d: any) => nodeIds.has(d.id) ? 1 : 0.2);
      
      svg.selectAll('.links line')
        .style('opacity', (d: any) => edgeIds.has(d.id) ? 0.8 : 0.1)
        .style('stroke-width', (d: any) => edgeIds.has(d.id) ? 2 : 1);
      
      svg.selectAll('.labels text')
        .style('opacity', (d: any) => nodeIds.has(d.id) ? 1 : 0.2);
    } else {
      // 恢复正常样式（但保持已选中的高亮）
      if (highlightedNodes.size > 0) {
        updateHighlightStyles(highlightedNodes, highlightedEdges);
      } else {
        svg.selectAll('.nodes circle').style('opacity', 1);
        svg.selectAll('.links line').style('opacity', 0.6).style('stroke-width', 1);
        svg.selectAll('.labels text').style('opacity', 1).style('font-weight', 'normal');
      }
    }
  }, [highlightedNodes, highlightedEdges, updateHighlightStyles]);

  /**
   * 清除高亮
   */
  const clearHighlight = useCallback(() => {
    setHighlightedNodes(new Set());
    setHighlightedEdges(new Set());
    
    if (svgRef.current) {
      const svg = d3.select(svgRef.current);
      svg.selectAll('.nodes circle').style('opacity', 1).style('stroke-width', 2);
      svg.selectAll('.links line').style('opacity', 0.6).style('stroke-width', 1);
      svg.selectAll('.labels text').style('opacity', 1).style('font-weight', 'normal');
    }
  }, []);



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

    // 创建容器组
    const container = svg.append('g');
    
    svg.call(zoom);

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

    // 使用统一的颜色映射函数
    const getNodeColor = (nodeType: string) => getEntityTypeColor(nodeType);

    // 创建节点
    const node = container.append('g')
      .attr('class', 'nodes')
      .selectAll('circle')
      .data(graphData.nodes)
      .enter().append('circle')
      .attr('r', graphConfig.nodeSize)
      .attr('fill', (d) => getNodeColor(d.type))
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
        handleNodeClick(d);
      })
      .on('mouseover', function(_, d) {
        handleNodeHover(d, true);
        d3.select(this).attr('r', graphConfig.nodeSize * 1.5);
      })
      .on('mouseout', function(_, d) {
        handleNodeHover(d, false);
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
   * 导出图谱为JSON格式
   */
  const exportAsJSON = useCallback(() => {
    if (!graphData) {
      message.warning('没有可导出的图谱数据');
      return;
    }

    try {
      const exportData = {
        ...graphData,
        exportedAt: new Date().toISOString(),
        version: '1.0',
      };
      
      const dataStr = JSON.stringify(exportData, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      
      const link = document.createElement('a');
      link.href = url;
      link.download = `knowledge_graph_${new Date().getTime()}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      
      message.success('图谱已导出为JSON格式');
    } catch (error) {
      message.error('导出JSON时发生错误');
      console.error('Export JSON error:', error);
    }
  }, [graphData]);

  /**
   * 导出图谱为CSV格式
   */
  const exportAsCSV = useCallback(() => {
    if (!graphData) {
      message.warning('没有可导出的图谱数据');
      return;
    }

    try {
      // 导出节点CSV
      const nodeHeaders = ['id', 'label', 'type', 'weight', 'properties'];
      const nodeRows = graphData.nodes.map(node => [
        node.id,
        node.label,
        node.type,
        node.weight || 0,
        JSON.stringify(node.properties || {})
      ]);
      
      const nodeCSV = [nodeHeaders, ...nodeRows]
        .map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(','))
        .join('\n');
      
      // 导出边CSV
      const edgeHeaders = ['id', 'source', 'target', 'label', 'type', 'weight', 'properties'];
      const edgeRows = graphData.edges.map(edge => [
        edge.id,
        typeof edge.source === 'string' ? edge.source : edge.source.id,
        typeof edge.target === 'string' ? edge.target : edge.target.id,
        edge.label || '',
        edge.type,
        edge.weight || 0,
        JSON.stringify(edge.properties || {})
      ]);
      
      const edgeCSV = [edgeHeaders, ...edgeRows]
        .map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(','))
        .join('\n');
      
      // 下载节点CSV
      const nodeBlob = new Blob([nodeCSV], { type: 'text/csv;charset=utf-8;' });
      const nodeUrl = URL.createObjectURL(nodeBlob);
      const nodeLink = document.createElement('a');
      nodeLink.href = nodeUrl;
      nodeLink.download = `knowledge_graph_nodes_${new Date().getTime()}.csv`;
      document.body.appendChild(nodeLink);
      nodeLink.click();
      document.body.removeChild(nodeLink);
      URL.revokeObjectURL(nodeUrl);
      
      // 下载边CSV
      const edgeBlob = new Blob([edgeCSV], { type: 'text/csv;charset=utf-8;' });
      const edgeUrl = URL.createObjectURL(edgeBlob);
      const edgeLink = document.createElement('a');
      edgeLink.href = edgeUrl;
      edgeLink.download = `knowledge_graph_edges_${new Date().getTime()}.csv`;
      document.body.appendChild(edgeLink);
      edgeLink.click();
      document.body.removeChild(edgeLink);
      URL.revokeObjectURL(edgeUrl);
      
      message.success('图谱已导出为CSV格式（节点和边分别保存）');
    } catch (error) {
      message.error('导出CSV时发生错误');
      console.error('Export CSV error:', error);
    }
  }, [graphData]);

  /**
   * 导出图谱为SVG格式
   */
  const exportAsSVG = useCallback(() => {
    if (!svgRef.current) {
      message.warning('没有可导出的图谱可视化');
      return;
    }

    try {
      const svgElement = svgRef.current;
      const serializer = new XMLSerializer();
      const svgString = serializer.serializeToString(svgElement);
      
      // 添加XML声明和样式
      const fullSvgString = `<?xml version="1.0" encoding="UTF-8"?>\n${svgString}`;
      
      const svgBlob = new Blob([fullSvgString], { type: 'image/svg+xml;charset=utf-8;' });
      const url = URL.createObjectURL(svgBlob);
      
      const link = document.createElement('a');
      link.href = url;
      link.download = `knowledge_graph_${new Date().getTime()}.svg`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      
      message.success('图谱已导出为SVG格式');
    } catch (error) {
      message.error('导出SVG时发生错误');
      console.error('Export SVG error:', error);
    }
  }, []);



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

  // 获取节点类型和边类型列表
  const nodeTypes = originalGraphData ? 
    Array.from(new Set(originalGraphData.nodes.map(node => node.type))) : [];
  const edgeTypes = originalGraphData ? 
    Array.from(new Set(originalGraphData.edges.map(edge => edge.type))) : [];

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
                  danger
                  onClick={() => {
                    knowledgeGraphStore.clearAll();
                    loadGraphData();
                    message.success('存储数据已清空，现在使用示例数据');
                  }}
                >
                  清空存储
                </Button>
                <Button
                  icon={<SettingOutlined />}
                  onClick={() => setSettingsVisible(true)}
                >
                  设置
                </Button>
                <Dropdown
                  menu={{
                    items: [
                      {
                        key: 'json',
                        label: 'JSON格式',
                        icon: <DownloadOutlined />,
                        onClick: exportAsJSON,
                      },
                      {
                        key: 'csv',
                        label: 'CSV格式',
                        icon: <DownloadOutlined />,
                        onClick: exportAsCSV,
                      },
                      {
                        key: 'svg',
                        label: 'SVG格式',
                        icon: <DownloadOutlined />,
                        onClick: exportAsSVG,
                      },
                    ],
                  }}
                  disabled={!graphData}
                >
                  <Button
                    type="primary"
                    icon={<DownloadOutlined />}
                    disabled={!graphData}
                  >
                    导出
                  </Button>
                </Dropdown>
              </Space>
            </div>
            
            {/* 搜索和筛选 */}
            <Row gutter={16} className="mb-16">
              <Col span={8}>
                <Input.Search
                  placeholder="搜索节点、关系或属性..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onSearch={handleSearch}
                  enterButton={<SearchOutlined />}
                  loading={loading}
                />
              </Col>
              <Col span={4}>
                <Select
                  value={selectedNodeType}
                  onChange={(value) => {
                    setSelectedNodeType(value);
                    // 自动应用筛选
                    setTimeout(applyFilters, 100);
                  }}
                  style={{ width: '100%' }}
                  placeholder="节点类型"
                >
                  <Option value="all">所有节点类型</Option>
                  {nodeTypes.map(type => (
                    <Option key={type} value={type}>{type}</Option>
                  ))}
                </Select>
              </Col>
              <Col span={4}>
                <Select
                  value={selectedEdgeType}
                  onChange={(value) => {
                    setSelectedEdgeType(value);
                    // 自动应用筛选
                    setTimeout(applyFilters, 100);
                  }}
                  style={{ width: '100%' }}
                  placeholder="关系类型"
                >
                  <Option value="all">所有关系类型</Option>
                  {edgeTypes.map(type => (
                    <Option key={type} value={type}>{type}</Option>
                  ))}
                </Select>
              </Col>
              <Col span={4}>
                <div>
                  <Text style={{ fontSize: '12px', color: '#666' }}>置信度 ≥ {minConfidence.toFixed(1)}</Text>
                  <Slider
                    min={0}
                    max={1}
                    step={0.1}
                    value={minConfidence}
                    onChange={(value) => {
                      setMinConfidence(value);
                      // 自动应用筛选
                      setTimeout(applyFilters, 100);
                    }}
                    style={{ marginTop: 4 }}
                  />
                </div>
              </Col>
              <Col span={4}>
                <Space>
                  <Button
                    onClick={resetFilters}
                    disabled={!originalGraphData}
                    size="small"
                  >
                    重置
                  </Button>
                  <Tooltip title="放大">
                    <Button
                      icon={<ZoomInOutlined />}
                      onClick={() => handleZoom(1.2)}
                      size="small"
                    />
                  </Tooltip>
                  <Tooltip title="缩小">
                    <Button
                      icon={<ZoomOutOutlined />}
                      onClick={() => handleZoom(0.8)}
                      size="small"
                    />
                  </Tooltip>
                  <Tooltip title="全屏">
                    <Button 
                      icon={<FullscreenOutlined />} 
                      size="small"
                    />
                  </Tooltip>
                </Space>
              </Col>
            </Row>
            
            {/* 筛选结果统计 */}
            {graphData && originalGraphData && (
              graphData.nodes.length !== originalGraphData.nodes.length || 
              graphData.edges.length !== originalGraphData.edges.length
            ) && (
              <Row className="mb-16">
                <Col span={24}>
                  <Alert
                    message={`筛选结果：显示 ${graphData.nodes.length}/${originalGraphData.nodes.length} 个节点，${graphData.edges.length}/${originalGraphData.edges.length} 个关系`}
                    type="info"
                    showIcon
                    closable={false}
                    style={{ fontSize: '12px' }}
                  />
                </Col>
              </Row>
            )}
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
        onClose={() => {
          setDrawerVisible(false);
          clearHighlight();
        }}
        open={drawerVisible}
        width={450}
      >
        {selectedNode && (
          <div>
            <div className="mb-16">
              <Space>
                <Button 
                  size="small" 
                  onClick={clearHighlight}
                >
                  清除高亮
                </Button>
                <Button 
                  size="small" 
                  type="primary"
                  onClick={() => {
                    // 重新高亮当前节点的连接
                    handleNodeClick(selectedNode);
                  }}
                >
                  重新高亮
                </Button>
              </Space>
            </div>
            
            <Descriptions column={1} bordered size="small">
              <Descriptions.Item label="ID">{selectedNode.id}</Descriptions.Item>
              <Descriptions.Item label="标签">{selectedNode.label}</Descriptions.Item>
              <Descriptions.Item label="类型">
                <Tag color={getEntityTypeColor(selectedNode.type).replace('#', '')}>
                  {selectedNode.type}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="置信度">
                {selectedNode.weight ? (selectedNode.weight * 100).toFixed(1) + '%' : 'N/A'}
              </Descriptions.Item>
              {selectedNode.properties && Object.keys(selectedNode.properties).length > 0 && (
                <Descriptions.Item label="属性">
                  <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
                    {Object.entries(selectedNode.properties).map(([key, value]) => (
                      <div key={key} style={{ marginBottom: '4px' }}>
                        <Text strong>{key}:</Text> <Text code>{String(value)}</Text>
                      </div>
                    ))}
                  </div>
                </Descriptions.Item>
              )}
            </Descriptions>
            
            {/* 连接信息 */}
            {graphData && (
              <div style={{ marginTop: '16px' }}>
                <Title level={5}>连接信息</Title>
                <div>
                  <Text>连接的节点数: </Text>
                  <Tag color="blue">{highlightedNodes.size - 1}</Tag>
                </div>
                <div style={{ marginTop: '8px' }}>
                  <Text>相关关系数: </Text>
                  <Tag color="green">{highlightedEdges.size}</Tag>
                </div>
                
                {/* 相关关系列表 */}
                {highlightedEdges.size > 0 && (
                  <div style={{ marginTop: '12px' }}>
                    <Text strong>相关关系:</Text>
                    <div style={{ marginTop: '8px', maxHeight: '150px', overflowY: 'auto' }}>
                      {graphData.edges
                        .filter(edge => highlightedEdges.has(edge.id))
                        .map(edge => {
                          const sourceLabel = graphData.nodes.find(n => n.id === edge.source)?.label || 'Unknown';
                          const targetLabel = graphData.nodes.find(n => n.id === edge.target)?.label || 'Unknown';
                          return (
                            <div key={edge.id} style={{ marginBottom: '4px', padding: '4px', backgroundColor: '#f5f5f5', borderRadius: '4px' }}>
                              <Text style={{ fontSize: '12px' }}>
                                {sourceLabel} → {edge.label || edge.type} → {targetLabel}
                              </Text>
                            </div>
                          );
                        })
                      }
                    </div>
                  </div>
                )}
              </div>
            )}
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