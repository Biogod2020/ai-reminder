import { useCallback } from 'react';
import {
  ReactFlow,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  Background,
  Controls,
  MiniMap,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import dagre from 'dagre';

const initialNodes = [
  { id: 'classify', data: { label: 'Classify' }, position: { x: 0, y: 0 } },
  { id: 'handle_task', data: { label: 'Handle Task' }, position: { x: 0, y: 0 } },
  { id: 'handle_memory', data: { label: 'Handle Memory' }, position: { x: 0, y: 0 } },
  { id: 'handle_planner', data: { label: 'Handle Planner' }, position: { x: 0, y: 0 } },
  { id: 'handle_clarify', data: { label: 'Handle Clarify' }, position: { x: 0, y: 0 } },
  { id: 'await_approval', data: { label: 'Await Approval' }, position: { x: 0, y: 0 } },
  { id: 'notify', data: { label: 'Notify' }, position: { x: 0, y: 0 } },
];

const initialEdges = [
  { id: 'e-classify-task', source: 'classify', target: 'handle_task', animated: true, label: 'intent: task' },
  { id: 'e-classify-memory', source: 'classify', target: 'handle_memory', animated: true, label: 'intent: memory' },
  { id: 'e-classify-planner', source: 'classify', target: 'handle_planner', animated: true, label: 'intent: planner' },
  { id: 'e-classify-clarify', source: 'classify', target: 'handle_clarify', animated: true, label: 'intent: clarify' },
  { id: 'e-task-approval', source: 'handle_task', target: 'await_approval' },
  { id: 'e-planner-approval', source: 'handle_planner', target: 'await_approval' },
  { id: 'e-memory-notify', source: 'handle_memory', target: 'notify' },
];

const nodeWidth = 172;
const nodeHeight = 36;

const getLayoutedElements = (nodes: any[], edges: any[], direction = 'TB') => {
  const dagreGraph = new dagre.graphlib.Graph();
  dagreGraph.setDefaultEdgeLabel(() => ({}));
  
  const isHorizontal = direction === 'LR';
  dagreGraph.setGraph({ rankdir: direction });

  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, { width: nodeWidth, height: nodeHeight });
  });

  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  dagre.layout(dagreGraph);

  const layoutedNodes = nodes.map((node) => {
    const nodeWithPosition = dagreGraph.node(node.id);
    return {
      ...node,
      targetPosition: isHorizontal ? 'left' : 'top',
      sourcePosition: isHorizontal ? 'right' : 'bottom',
      position: {
        x: nodeWithPosition.x - nodeWidth / 2,
        y: nodeWithPosition.y - nodeHeight / 2,
      },
    };
  });

  return { nodes: layoutedNodes, edges };
};

const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(
  initialNodes,
  initialEdges
);

const ArchitectureDashboard = () => {
  const [nodes, setNodes, onNodesChange] = useNodesState(layoutedNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(layoutedEdges);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  return (
    <div className="h-full w-full bg-[#f7f6f3]">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        fitView
        className="architecture-flow"
      >
        <Background color="#e9e9e7" gap={20} />
        <Controls />
        <MiniMap zoomable pannable />
      </ReactFlow>
    </div>
  );
};

export default ArchitectureDashboard;
