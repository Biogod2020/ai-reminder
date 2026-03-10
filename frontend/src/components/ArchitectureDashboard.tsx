import { useCallback, useEffect, useState } from 'react';
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
import { Box, Code2, Database, Info, X, Activity, Cpu, Layers } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const CustomNode = ({ data, selected }: any) => {
  return (
    <div className={`px-4 py-3 shadow-md rounded-lg bg-white border-2 transition-all group min-w-[180px] ${selected ? 'border-[#2383e2] shadow-[#2383e2]/10' : 'border-[#e9e9e7] hover:border-[#2383e2]'}`}>
      <Handle type="target" position={Position.Top} className="w-3 h-3 !bg-[#2383e2] border-2 border-white" />
      <div className="flex items-center gap-3">
        <div className={`w-8 h-8 rounded-lg flex items-center justify-center transition-colors ${selected ? 'bg-[#2383e2] text-white' : 'bg-[#f7f6f3] text-[#2383e2]'}`}>
          <Cpu size={16} />
        </div>
        <div className="flex-1">
          <div className="text-[13px] font-bold text-[#37352f] leading-tight">{data.label}</div>
          <div className="text-[10px] text-[#787774] font-medium uppercase tracking-wider mt-0.5">{data.role || 'Process'}</div>
        </div>
        <div className={`transition-opacity ${selected ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'}`}>
          <Info size={14} className="text-[#2383e2]" />
        </div>
      </div>
      <Handle type="source" position={Position.Bottom} className="w-3 h-3 !bg-[#2383e2] border-2 border-white" />
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
  { id: 'e-classify-task', source: 'classify', target: 'handle_task', animated: true, label: 'task' },
  { id: 'e-classify-memory', source: 'classify', target: 'handle_memory', animated: true, label: 'memory' },
  { id: 'e-classify-planner', source: 'classify', target: 'handle_planner', animated: true, label: 'planner' },
  { id: 'e-classify-clarify', source: 'classify', target: 'handle_clarify', animated: true, label: 'clarify' },
  { id: 'e-task-approval', source: 'handle_task', target: 'await_approval' },
  { id: 'e-planner-approval', source: 'handle_planner', target: 'await_approval' },
  { id: 'e-memory-notify', source: 'handle_memory', target: 'notify' },
];

const nodeWidth = 200;
const nodeHeight = 80;

const getLayoutedElements = (nodes: any[], edges: any[], direction = 'TB') => {
  const dagreGraph = new dagre.graphlib.Graph();
  dagreGraph.setDefaultEdgeLabel(() => ({}));
  dagreGraph.setGraph({ rankdir: direction, ranksep: 80, nodesep: 50 });

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
  const [selectedNode, setSelectedNode] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchMetadata = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/v1/viz/nodes');
        if (response.ok) {
          const metadata = await response.json();
          setNodes((nds) => 
            nds.map((node) => {
              const nodeMeta = metadata.find((m: any) => m.node_id === node.id);
              if (nodeMeta) {
                return {
                  ...node,
                  data: {
                    ...node.data,
                    ...nodeMeta
                  }
                };
              }
              return node;
            })
          );
        }
      } catch (error) {
        console.error('Failed to fetch node metadata:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchMetadata();
  }, [setNodes]);

  const onNodeClick = useCallback((_: any, node: any) => {
    setSelectedNode(node);
  }, []);

  const onPaneClick = useCallback(() => {
    setSelectedNode(null);
  }, []);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  return (
    <div className="h-full w-full bg-[#f7f6f3] flex flex-col overflow-hidden">
      <header className="px-6 py-4 border-b border-[#e9e9e7] bg-white flex items-center justify-between z-10 shrink-0">
        <div>
          <h1 className="text-lg font-bold text-[#37352f]">Architecture Engine</h1>
          <p className="text-xs text-[#787774]">Dynamic data-driven visualization of the Agent's cognitive state machine</p>
        </div>
        <div className="flex items-center gap-2">
           <div className="px-2 py-1 rounded bg-[#f7f6f3] text-[10px] font-bold text-[#787774] flex items-center gap-1 uppercase tracking-tighter">
             <Database size={10} /> Local SQLite
           </div>
           <div className="px-2 py-1 rounded bg-[#f7f6f3] text-[10px] font-bold text-[#787774] flex items-center gap-1 uppercase tracking-tighter">
             <Activity size={10} /> Live API
           </div>
        </div>
      </header>

      <div className="flex-1 flex relative overflow-hidden">
        <div className="flex-1 relative">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={onNodeClick}
            onPaneClick={onPaneClick}
            nodeTypes={nodeTypes}
            fitView
            className="architecture-flow"
          >
            <Background color="#e9e9e7" gap={20} />
            <Controls />
            <MiniMap zoomable pannable />
          </ReactFlow>
        </div>

        <AnimatePresence>
          {selectedNode && (
            <motion.aside
              initial={{ x: 400 }}
              animate={{ x: 0 }}
              exit={{ x: 400 }}
              className="w-[350px] bg-white border-l border-[#e9e9e7] shadow-2xl z-20 flex flex-col shrink-0"
            >
              <div className="p-6 flex flex-col h-full overflow-y-auto">
                <div className="flex items-center justify-between mb-6">
                  <div className="px-2 py-1 bg-[#2383e2]/10 text-[#2383e2] text-[10px] font-bold rounded uppercase tracking-widest">
                    Node Details
                  </div>
                  <button onClick={() => setSelectedNode(null)} className="p-1 hover:bg-[#f7f6f3] rounded-full transition-colors">
                    <X size={18} className="text-[#787774]" />
                  </button>
                </div>

                <div className="flex items-center gap-4 mb-8">
                  <div className="w-12 h-12 rounded-xl bg-[#2383e2] flex items-center justify-center text-white shadow-lg shadow-[#2383e2]/20">
                    <Cpu size={24} />
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-[#37352f]">{selectedNode.data.label}</h2>
                    <p className="text-xs text-[#787774] font-medium uppercase tracking-wider">{selectedNode.data.role}</p>
                  </div>
                </div>

                <div className="space-y-8">
                  <section>
                    <h3 className="text-[11px] font-bold text-[#787774] uppercase tracking-[0.2em] mb-3 flex items-center gap-2">
                      <Layers size={12} /> Description
                    </h3>
                    <p className="text-sm text-[#37352f] leading-relaxed bg-[#f7f6f3] p-4 rounded-lg border border-[#e9e9e7]/50 italic">
                      "{selectedNode.data.description || 'No description available for this node.'}"
                    </p>
                  </section>

                  <section>
                    <h3 className="text-[11px] font-bold text-[#787774] uppercase tracking-[0.2em] mb-3 flex items-center gap-2">
                      <Code2 size={12} /> Implementation
                    </h3>
                    <div className="bg-[#1e1e1e] text-[#d4d4d4] p-3 rounded-lg text-xs font-mono break-all overflow-hidden">
                      {selectedNode.data.code_mapping}
                    </div>
                  </section>

                  <section>
                    <h3 className="text-[11px] font-bold text-[#787774] uppercase tracking-[0.2em] mb-3 flex items-center gap-2">
                      <Activity size={12} /> I/O Schema
                    </h3>
                    <div className="space-y-2">
                      <div className="flex justify-between items-center text-xs p-2 bg-white border border-[#e9e9e7] rounded-md">
                        <span className="font-bold text-[#787774]">Input</span>
                        <span className="text-[#37352f]">{selectedNode.data.io_schema?.input || 'N/A'}</span>
                      </div>
                      <div className="flex justify-between items-center text-xs p-2 bg-white border border-[#e9e9e7] rounded-md">
                        <span className="font-bold text-[#787774]">Output</span>
                        <span className="text-[#37352f]">{selectedNode.data.io_schema?.output || 'N/A'}</span>
                      </div>
                    </div>
                  </section>

                  {selectedNode.data.load_metrics && (
                    <section>
                      <h3 className="text-[11px] font-bold text-[#787774] uppercase tracking-[0.2em] mb-3 flex items-center gap-2">
                        <Cpu size={12} /> Cognitive Load
                      </h3>
                      <div className="px-4 py-3 bg-[#2383e2]/5 border border-[#2383e2]/10 rounded-lg">
                        <div className="text-xs text-[#2383e2] font-bold">
                          {selectedNode.data.load_metrics.cognitive_load_impact || 'N/A'}
                        </div>
                      </div>
                    </section>
                  )}
                </div>

                <div className="mt-auto pt-8 text-[10px] text-[#e9e9e7] text-center uppercase tracking-widest font-black italic">
                  Notion Soul Agent Core
                </div>
              </div>
            </motion.aside>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default ArchitectureDashboard;
