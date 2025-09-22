/**
 * 本体可视化组件
 * 提供本体结构的图形化展示和交互功能
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Card,
  Row,
  Col,
  Button,
  Input,
  Space,
  Typography,
  Select,
  Tooltip,
  Badge,
  Tag,
  Slider,
  Switch,
  Popover,
  Divider,
} from 'antd';
import {
  SearchOutlined,
  ZoomInOutlined,
  ZoomOutOutlined,
  ReloadOutlined,
  SettingOutlined,
  NodeIndexOutlined,
  ApartmentOutlined,
} from '@ant-design/icons';

const { Text } = Typography;
const { Option } = Select;

/**
 * 节点类型
 */
interface GraphNode {
  id: string;
  label: string;
  type: 'entity' | 'relation';
  properties?: any[];
  x?: number;
  y?: number;
  color?: string;
  size?: number;
}

/**
 * 边类型
 */
interface GraphEdge {
  id: string;
  source: string;
  target: string;
  label?: string;
  type?: string;
  color?: string;
  width?: number;
}

/**
 * 图数据
 */
interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

/**
 * 本体可视化组件属性
 */
interface OntologyVisualizationProps {
  ontologyData?: any;
  onNodeClick?: (node: GraphNode) => void;
  onEdgeClick?: (edge: GraphEdge) => void;
  className?: string;
}

/**
 * 本体可视化组件
 */
const OntologyVisualization: React.FC<OntologyVisualizationProps> = ({
  ontologyData,
  onNodeClick,
  className,
}) => {
  // 状态管理
  const [graphData, setGraphData] = useState<GraphData>({ nodes: [], edges: [] });
  const [filteredData, setFilteredData] = useState<GraphData>({ nodes: [], edges: [] });
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [selectedNodeTypes, setSelectedNodeTypes] = useState<string[]>(['entity', 'relation']);
  const [zoomLevel, setZoomLevel] = useState<number>(100);
  const [showLabels, setShowLabels] = useState<boolean>(true);
  const [showProperties, setShowProperties] = useState<boolean>(false);
  const [layoutType, setLayoutType] = useState<string>('force');
  
  // 画布引用
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  
  // 画布状态
  const [canvasSize, setCanvasSize] = useState({ width: 800, height: 600 });
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [offset, setOffset] = useState({ x: 0, y: 0 });
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);

  /**
   * 从本体数据生成图数据
   */
  const generateGraphData = useCallback((data: any): GraphData => {
    if (!data) return { nodes: [], edges: [] };
    
    const nodes: GraphNode[] = [];
    const edges: GraphEdge[] = [];
    
    // 添加实体类型节点
    if (data.entity_types) {
      data.entity_types.forEach((entityType: any, index: number) => {
        nodes.push({
          id: entityType.id,
          label: entityType.name,
          type: 'entity',
          properties: entityType.properties || [],
          x: Math.cos(index * 2 * Math.PI / data.entity_types.length) * 200 + 400,
          y: Math.sin(index * 2 * Math.PI / data.entity_types.length) * 200 + 300,
          color: '#1890ff',
          size: 20 + (entityType.properties?.length || 0) * 2,
        });
        
        // 添加继承关系边
        if (entityType.parent_types) {
          entityType.parent_types.forEach((parentId: string) => {
            edges.push({
              id: `${entityType.id}-${parentId}`,
              source: entityType.id,
              target: parentId,
              label: '继承',
              type: 'inheritance',
              color: '#52c41a',
              width: 2,
            });
          });
        }
      });
    }
    
    // 添加关系类型节点和边
    if (data.relation_types) {
      data.relation_types.forEach((relationType: any, index: number) => {
        const relationNodeId = `relation_${relationType.id}`;
        nodes.push({
          id: relationNodeId,
          label: relationType.name,
          type: 'relation',
          properties: relationType.properties || [],
          x: Math.cos((index + data.entity_types?.length || 0) * 2 * Math.PI / (data.relation_types.length + (data.entity_types?.length || 0))) * 150 + 400,
          y: Math.sin((index + data.entity_types?.length || 0) * 2 * Math.PI / (data.relation_types.length + (data.entity_types?.length || 0))) * 150 + 300,
          color: '#fa8c16',
          size: 15 + (relationType.properties?.length || 0) * 1.5,
        });
        
        // 添加定义域边
        if (relationType.domain_types) {
          relationType.domain_types.forEach((domainId: string) => {
            edges.push({
              id: `${domainId}-${relationNodeId}`,
              source: domainId,
              target: relationNodeId,
              label: '定义域',
              type: 'domain',
              color: '#722ed1',
              width: 1.5,
            });
          });
        }
        
        // 添加值域边
        if (relationType.range_types) {
          relationType.range_types.forEach((rangeId: string) => {
            edges.push({
              id: `${relationNodeId}-${rangeId}`,
              source: relationNodeId,
              target: rangeId,
              label: '值域',
              type: 'range',
              color: '#eb2f96',
              width: 1.5,
            });
          });
        }
      });
    }
    
    return { nodes, edges };
  }, []);

  /**
   * 过滤图数据
   */
  const filterGraphData = useCallback((data: GraphData, search: string, nodeTypes: string[]): GraphData => {
    const filteredNodes = data.nodes.filter(node => {
      const matchesSearch = !search || node.label.toLowerCase().includes(search.toLowerCase());
      const matchesType = nodeTypes.includes(node.type);
      return matchesSearch && matchesType;
    });
    
    const nodeIds = new Set(filteredNodes.map(node => node.id));
    const filteredEdges = data.edges.filter(edge => 
      nodeIds.has(edge.source) && nodeIds.has(edge.target)
    );
    
    return { nodes: filteredNodes, edges: filteredEdges };
  }, []);

  /**
   * 绘制图形
   */
  const drawGraph = useCallback((ctx: CanvasRenderingContext2D, data: GraphData) => {
    // 清空画布
    ctx.clearRect(0, 0, canvasSize.width, canvasSize.height);
    
    // 应用缩放和偏移
    ctx.save();
    ctx.scale(zoomLevel / 100, zoomLevel / 100);
    ctx.translate(offset.x, offset.y);
    
    // 绘制边
    data.edges.forEach(edge => {
      const sourceNode = data.nodes.find(n => n.id === edge.source);
      const targetNode = data.nodes.find(n => n.id === edge.target);
      
      if (sourceNode && targetNode) {
        ctx.beginPath();
        ctx.moveTo(sourceNode.x || 0, sourceNode.y || 0);
        ctx.lineTo(targetNode.x || 0, targetNode.y || 0);
        ctx.strokeStyle = edge.color || '#d9d9d9';
        ctx.lineWidth = edge.width || 1;
        ctx.stroke();
        
        // 绘制箭头
        const angle = Math.atan2((targetNode.y || 0) - (sourceNode.y || 0), (targetNode.x || 0) - (sourceNode.x || 0));
        const arrowLength = 10;
        const arrowX = (targetNode.x || 0) - Math.cos(angle) * (targetNode.size || 20);
        const arrowY = (targetNode.y || 0) - Math.sin(angle) * (targetNode.size || 20);
        
        ctx.beginPath();
        ctx.moveTo(arrowX, arrowY);
        ctx.lineTo(arrowX - arrowLength * Math.cos(angle - Math.PI / 6), arrowY - arrowLength * Math.sin(angle - Math.PI / 6));
        ctx.moveTo(arrowX, arrowY);
        ctx.lineTo(arrowX - arrowLength * Math.cos(angle + Math.PI / 6), arrowY - arrowLength * Math.sin(angle + Math.PI / 6));
        ctx.stroke();
        
        // 绘制边标签
        if (showLabels && edge.label) {
          const midX = ((sourceNode.x || 0) + (targetNode.x || 0)) / 2;
          const midY = ((sourceNode.y || 0) + (targetNode.y || 0)) / 2;
          ctx.fillStyle = '#666';
          ctx.font = '12px Arial';
          ctx.textAlign = 'center';
          ctx.fillText(edge.label, midX, midY - 5);
        }
      }
    });
    
    // 绘制节点
    data.nodes.forEach(node => {
      const x = node.x || 0;
      const y = node.y || 0;
      const size = node.size || 20;
      
      // 绘制节点背景
      ctx.beginPath();
      if (node.type === 'entity') {
        ctx.arc(x, y, size, 0, 2 * Math.PI);
      } else {
        ctx.rect(x - size, y - size, size * 2, size * 2);
      }
      ctx.fillStyle = node.color || '#1890ff';
      ctx.fill();
      
      // 绘制节点边框
      ctx.strokeStyle = selectedNode?.id === node.id ? '#ff4d4f' : '#fff';
      ctx.lineWidth = selectedNode?.id === node.id ? 3 : 2;
      ctx.stroke();
      
      // 绘制节点标签
      if (showLabels) {
        ctx.fillStyle = '#fff';
        ctx.font = 'bold 12px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(node.label, x, y + 4);
      }
      
      // 绘制属性数量
      if (showProperties && node.properties && node.properties.length > 0) {
        ctx.fillStyle = '#f50';
        ctx.font = '10px Arial';
        ctx.fillText(node.properties.length.toString(), x + size - 5, y - size + 10);
      }
    });
    
    ctx.restore();
  }, [canvasSize, zoomLevel, offset, showLabels, showProperties, selectedNode]);

  /**
   * 处理鼠标点击
   */
  const handleCanvasClick = useCallback((event: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const rect = canvas.getBoundingClientRect();
    const x = (event.clientX - rect.left - offset.x) * 100 / zoomLevel;
    const y = (event.clientY - rect.top - offset.y) * 100 / zoomLevel;
    
    // 检查是否点击了节点
    const clickedNode = filteredData.nodes.find(node => {
      const nodeX = node.x || 0;
      const nodeY = node.y || 0;
      const nodeSize = node.size || 20;
      const distance = Math.sqrt((x - nodeX) ** 2 + (y - nodeY) ** 2);
      return distance <= nodeSize;
    });
    
    if (clickedNode) {
      setSelectedNode(clickedNode);
      onNodeClick?.(clickedNode);
    } else {
      setSelectedNode(null);
    }
  }, [filteredData.nodes, offset, zoomLevel, onNodeClick]);

  /**
   * 处理鼠标拖拽
   */
  const handleMouseDown = useCallback((event: React.MouseEvent<HTMLCanvasElement>) => {
    setIsDragging(true);
    setDragStart({ x: event.clientX - offset.x, y: event.clientY - offset.y });
  }, [offset]);

  const handleMouseMove = useCallback((event: React.MouseEvent<HTMLCanvasElement>) => {
    if (isDragging) {
      setOffset({
        x: event.clientX - dragStart.x,
        y: event.clientY - dragStart.y,
      });
    }
  }, [isDragging, dragStart]);

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  /**
   * 重置视图
   */
  const resetView = useCallback(() => {
    setZoomLevel(100);
    setOffset({ x: 0, y: 0 });
    setSelectedNode(null);
  }, []);

  /**
   * 自动布局
   */
  const applyLayout = useCallback((type: string) => {
    const newGraphData = { ...graphData };
    
    if (type === 'circle') {
      newGraphData.nodes.forEach((node, index) => {
        const angle = (index * 2 * Math.PI) / newGraphData.nodes.length;
        node.x = Math.cos(angle) * 200 + canvasSize.width / 2;
        node.y = Math.sin(angle) * 200 + canvasSize.height / 2;
      });
    } else if (type === 'grid') {
      const cols = Math.ceil(Math.sqrt(newGraphData.nodes.length));
      newGraphData.nodes.forEach((node, index) => {
        const row = Math.floor(index / cols);
        const col = index % cols;
        node.x = col * 150 + 100;
        node.y = row * 150 + 100;
      });
    }
    
    setGraphData(newGraphData);
  }, [graphData, canvasSize]);

  // 初始化图数据
  useEffect(() => {
    if (ontologyData) {
      const newGraphData = generateGraphData(ontologyData);
      setGraphData(newGraphData);
    }
  }, [ontologyData, generateGraphData]);

  // 过滤数据
  useEffect(() => {
    const filtered = filterGraphData(graphData, searchTerm, selectedNodeTypes);
    setFilteredData(filtered);
  }, [graphData, searchTerm, selectedNodeTypes, filterGraphData]);

  // 绘制图形
  useEffect(() => {
    const canvas = canvasRef.current;
    if (canvas) {
      const ctx = canvas.getContext('2d');
      if (ctx) {
        drawGraph(ctx, filteredData);
      }
    }
  }, [filteredData, drawGraph]);

  // 调整画布大小
  useEffect(() => {
    const updateCanvasSize = () => {
      if (containerRef.current) {
        const { clientWidth, clientHeight } = containerRef.current;
        setCanvasSize({ width: clientWidth, height: clientHeight - 100 });
      }
    };
    
    updateCanvasSize();
    window.addEventListener('resize', updateCanvasSize);
    
    return () => {
      window.removeEventListener('resize', updateCanvasSize);
    };
  }, []);

  return (
    <div className={className} ref={containerRef} style={{ height: '100%' }}>
      <Card>
        {/* 控制面板 */}
        <div style={{ marginBottom: 16 }}>
          <Row gutter={16} align="middle">
            <Col span={6}>
              <Input
                placeholder="搜索节点"
                prefix={<SearchOutlined />}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                allowClear
              />
            </Col>
            <Col span={6}>
              <Select
                mode="multiple"
                placeholder="选择节点类型"
                value={selectedNodeTypes}
                onChange={setSelectedNodeTypes}
                style={{ width: '100%' }}
              >
                <Option value="entity">
                  <Space>
                    <NodeIndexOutlined style={{ color: '#1890ff' }} />
                    实体类型
                  </Space>
                </Option>
                <Option value="relation">
                  <Space>
                    <ApartmentOutlined style={{ color: '#fa8c16' }} />
                    关系类型
                  </Space>
                </Option>
              </Select>
            </Col>
            <Col span={4}>
              <Select
                value={layoutType}
                onChange={(value) => {
                  setLayoutType(value);
                  applyLayout(value);
                }}
                style={{ width: '100%' }}
              >
                <Option value="force">力导向</Option>
                <Option value="circle">圆形</Option>
                <Option value="grid">网格</Option>
              </Select>
            </Col>
            <Col span={8}>
              <Space>
                <Tooltip title="缩小">
                  <Button
                    icon={<ZoomOutOutlined />}
                    onClick={() => setZoomLevel(Math.max(25, zoomLevel - 25))}
                  />
                </Tooltip>
                <Slider
                  min={25}
                  max={200}
                  value={zoomLevel}
                  onChange={setZoomLevel}
                  style={{ width: 100 }}
                />
                <Text>{zoomLevel}%</Text>
                <Tooltip title="放大">
                  <Button
                    icon={<ZoomInOutlined />}
                    onClick={() => setZoomLevel(Math.min(200, zoomLevel + 25))}
                  />
                </Tooltip>
                <Tooltip title="重置视图">
                  <Button icon={<ReloadOutlined />} onClick={resetView} />
                </Tooltip>
                <Popover
                  content={
                    <div style={{ width: 200 }}>
                      <div style={{ marginBottom: 8 }}>
                        <Text>显示选项</Text>
                      </div>
                      <div style={{ marginBottom: 8 }}>
                        <Space>
                          <Text>显示标签</Text>
                          <Switch
                            checked={showLabels}
                            onChange={setShowLabels}
                            size="small"
                          />
                        </Space>
                      </div>
                      <div>
                        <Space>
                          <Text>显示属性数量</Text>
                          <Switch
                            checked={showProperties}
                            onChange={setShowProperties}
                            size="small"
                          />
                        </Space>
                      </div>
                    </div>
                  }
                  title="显示设置"
                  trigger="click"
                >
                  <Tooltip title="显示设置">
                    <Button icon={<SettingOutlined />} />
                  </Tooltip>
                </Popover>
              </Space>
            </Col>
          </Row>
        </div>

        {/* 统计信息 */}
        <div style={{ marginBottom: 16 }}>
          <Space>
            <Badge count={filteredData.nodes.filter(n => n.type === 'entity').length} color="blue">
              <Tag color="blue">实体类型</Tag>
            </Badge>
            <Badge count={filteredData.nodes.filter(n => n.type === 'relation').length} color="orange">
              <Tag color="orange">关系类型</Tag>
            </Badge>
            <Badge count={filteredData.edges.length} color="green">
              <Tag color="green">连接</Tag>
            </Badge>
          </Space>
        </div>

        {/* 画布 */}
        <div style={{ border: '1px solid #d9d9d9', borderRadius: 6, overflow: 'hidden' }}>
          <canvas
            ref={canvasRef}
            width={canvasSize.width}
            height={canvasSize.height}
            style={{ cursor: isDragging ? 'grabbing' : 'grab' }}
            onClick={handleCanvasClick}
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
          />
        </div>

        {/* 选中节点信息 */}
        {selectedNode && (
          <div style={{ marginTop: 16 }}>
            <Divider>节点信息</Divider>
            <Row gutter={16}>
              <Col span={12}>
                <Space direction="vertical" size="small">
                  <div>
                    <Text strong>名称：</Text>
                    <Text>{selectedNode.label}</Text>
                  </div>
                  <div>
                    <Text strong>类型：</Text>
                    <Tag color={selectedNode.type === 'entity' ? 'blue' : 'orange'}>
                      {selectedNode.type === 'entity' ? '实体类型' : '关系类型'}
                    </Tag>
                  </div>
                  <div>
                    <Text strong>属性数量：</Text>
                    <Badge count={selectedNode.properties?.length || 0} color="green" />
                  </div>
                </Space>
              </Col>
              <Col span={12}>
                {selectedNode.properties && selectedNode.properties.length > 0 && (
                  <div>
                    <Text strong>属性列表：</Text>
                    <div style={{ marginTop: 8 }}>
                      <Space wrap>
                        {selectedNode.properties.map((prop: any, index: number) => (
                          <Tag key={index} color="blue">
                            {prop.name} ({prop.data_type})
                          </Tag>
                        ))}
                      </Space>
                    </div>
                  </div>
                )}
              </Col>
            </Row>
          </div>
        )}
      </Card>
    </div>
  );
};

export default OntologyVisualization;