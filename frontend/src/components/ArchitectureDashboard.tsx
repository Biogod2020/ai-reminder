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
  Handle,
  Position,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import dagre from 'dagre';
import { Box, Code2, Database, Info } from 'lucide-react';

const CustomNode = ({ data }: any) => {
  return (
    <div className="px-4 py-2 shadow-sm rounded-md bg-white border border-[#e9e9e7] min-w-[150px] hover:border-[#2383e2] transition-colors group">
      <Handle type="target" position={Position.Top} className="w-2 h-2 !bg-[#2383e2]" />
      <div className="flex items-center gap-2">
        <div className="w-6 h-6 rounded bg-[#f7f6f3] flex items-center justify-center text-[#2383e2]">
          <Box size={14} />
        </div>
        <div className="flex-1">
          <div className="text-[12px] font-bold text-[#37352f]">{data.label}</div>
          <div className="text-[10px] text-[#787774] truncate">{data.role || 'Component'}</div>
        </div>
        <Info size={12} className="text-[#e9e9e7] group-hover:text-[#2383e2] transition-colors" />
      </div>
      <Handle type="source" position={Position.Bottom} className="w-2 h-2 !bg-[#2383e2]" />
    </div>
  );
};

const nodeTypes = {
  custom: CustomNode,
};

const initialNodes = [
  { id: 'classify', type: 'custom', data: { label: 'Classify', role: 'Intent Classifier' }, position: { x: 0, y: 0 } },
  { id: 'handle_task', type: 'custom', data: { label: 'Handle Task', role: 'Task Atomizer' }, position: { x: 0, y: 0 } },
  { id: 'handle_memory', type: 'custom', data: { label: 'Handle Memory', role: 'Memory Synthesizer' }, position: { x: 0, y: 0 } },
  { id: 'handle_planner', type: 'custom', data: { label: 'Handle Planner', role: 'Macro Planner' }, position: { x: 0, y: 0 } },
  { id: 'handle_clarify', type: 'custom', data: { label: 'Handle Clarify', role: 'Clarification Engine' }, position: { x: 0, y: 0 } },
  { id: 'await_approval', type: 'custom', data: { label: 'Await Approval', role: 'User Validation' }, position: { x: 0, y: 0 } },
  { id: 'notify', type: 'custom', data: { label: 'Notify', role: 'Communication' }, position: { x: 0, y: 0 } },
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
const nodeHeight = 56;

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
    <div className="h-full w-full bg-[#f7f6f3] flex flex-col">
      <header className="px-6 py-4 border-b border-[#e9e9e7] bg-white flex items-center justify-between z-10">
        <div>
          <h1 className="text-lg font-bold text-[#37352f]">Architecture Engine</h1>
          <p className="text-xs text-[#787774]">Dynamic visualization of the Soul Agent's cognitive graph</p>
        </div>
        <div className="flex items-center gap-2">
           <div className="px-2 py-1 rounded bg-[#f7f6f3] text-[10px] font-medium text-[#787774] flex items-center gap-1">
             <Database size={10} /> Data-Driven
           </div>
           <div className="px-2 py-1 rounded bg-[#f7f6f3] text-[10px] font-medium text-[#787774] flex items-center gap-1">
             <Code2 size={10} /> LangGraph
           </div>
        </div>
      </header>
      <div className="flex-1 relative">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          nodeTypes={nodeTypes}
          fitView
          className="architecture-flow"
        >
          <Background color="#e9e9e7" gap={20} />
          <Controls />
          <MiniMap zoomable pannable />
        </ReactFlow>
      </div>
    </div>
  );
};

export default ArchitectureDashboard;
