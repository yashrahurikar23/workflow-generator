import {
  addEdge,
  Background,
  Connection,
  Controls,
  Edge,
  MiniMap,
  Node,
  Position,
  ReactFlow,
  useEdgesState,
  useNodesState,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import React, { useCallback, useMemo } from "react";

// Custom node types for different step types
const stepTypeColors = {
  api_call: "#3B82F6", // Blue
  data_transform: "#10B981", // Green
  condition: "#F59E0B", // Yellow
  loop: "#8B5CF6", // Purple
  manual: "#EF4444", // Red
  llm_process: "#06B6D4", // Cyan
  email: "#EC4899", // Pink
  database: "#84CC16", // Lime
  file_operation: "#6B7280", // Gray
};

const stepTypeIcons = {
  api_call: "🌐",
  data_transform: "🔄",
  condition: "❓",
  loop: "🔁",
  manual: "👤",
  llm_process: "🤖",
  email: "📧",
  database: "🗄️",
  file_operation: "📁",
};

interface WorkflowStep {
  step_id: string;
  name: string;
  step_type: string;
  description?: string;
  depends_on: string[];
  condition?: any;
  config: any;
}

interface WorkflowVisualizationProps {
  workflow: {
    workflow_id: string;
    name: string;
    description: string;
    steps?: WorkflowStep[];
    parallel_execution?: boolean;
    workflow_type?: string;
    status?: string;
    created_at?: string;
    visual_data?: {
      nodes: any[];
      connections: any[];
    };
  };
  onNodeClick?: (nodeId: string, step: WorkflowStep) => void;
}

// Custom node component
const CustomNode = ({ data }: { data: any }) => {
  const { step, isSelected } = data;
  const color =
    stepTypeColors[step.step_type as keyof typeof stepTypeColors] || "#6B7280";
  const icon =
    stepTypeIcons[step.step_type as keyof typeof stepTypeIcons] || "⚡";

  return (
    <div
      className={`
        px-4 py-3 rounded-lg border-2 bg-white shadow-md min-w-[200px] max-w-[250px]
        ${isSelected ? "border-blue-500 shadow-lg" : "border-gray-200"}
        hover:shadow-lg transition-shadow cursor-pointer
      `}
      style={{ borderColor: isSelected ? "#3B82F6" : color }}
    >
      <div className="flex items-center gap-2 mb-2">
        <span className="text-lg">{icon}</span>
        <span
          className="font-semibold text-sm text-gray-800 truncate"
          title={step.name}
        >
          {step.name}
        </span>
      </div>

      <div className="text-xs text-gray-600 mb-2">
        <span
          className="inline-block px-2 py-1 rounded text-white text-xs font-medium"
          style={{ backgroundColor: color }}
        >
          {step.step_type.replace("_", " ")}
        </span>
      </div>

      {step.description && (
        <div
          className="text-xs text-gray-500 line-clamp-2"
          title={step.description}
        >
          {step.description}
        </div>
      )}

      {step.condition && (
        <div className="mt-2 text-xs text-orange-600 font-medium">
          ⚠️ Conditional
        </div>
      )}
    </div>
  );
};

const nodeTypes = {
  customNode: CustomNode,
};

export function WorkflowVisualization({
  workflow,
  onNodeClick,
}: WorkflowVisualizationProps) {
  // Convert workflow steps to React Flow nodes and edges
  const { initialNodes, initialEdges } = useMemo(() => {
    const steps = workflow.steps || [];

    // Create nodes
    const nodes: Node[] = steps.map((step, index) => {
      // Calculate position using a simple grid layout
      const row = Math.floor(index / 3);
      const col = index % 3;
      const x = col * 300 + 50;
      const y = row * 150 + 50;

      return {
        id: step.step_id,
        type: "customNode",
        position: { x, y },
        data: {
          step,
          isSelected: false,
          onClick: () => onNodeClick?.(step.step_id, step),
        },
        sourcePosition: Position.Right,
        targetPosition: Position.Left,
      };
    });

    // Create edges based on dependencies
    const edges: Edge[] = [];
    steps.forEach((step) => {
      step.depends_on.forEach((dependencyId) => {
        edges.push({
          id: `${dependencyId}-${step.step_id}`,
          source: dependencyId,
          target: step.step_id,
          type: "smoothstep",
          animated: true,
          style: { stroke: "#6B7280", strokeWidth: 2 },
          markerEnd: {
            type: "arrowclosed",
            color: "#6B7280",
          },
        });
      });
    });

    return { initialNodes: nodes, initialEdges: edges };
  }, [workflow, onNodeClick]);

  const [nodes, , onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const onNodeDoubleClick = useCallback(
    (event: React.MouseEvent, node: Node) => {
      const steps = workflow.steps || [];
      const step = steps.find((s) => s.step_id === node.id);
      if (step && onNodeClick) {
        onNodeClick(node.id, step);
      }
    },
    [workflow.steps, onNodeClick]
  );

  return (
    <div className="w-full h-full bg-gray-50 rounded-lg overflow-hidden">
      <div className="h-16 bg-white border-b px-4 flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-800">
            {workflow.name}
          </h3>
          <p className="text-sm text-gray-600">
            {(workflow.steps || []).length} steps
          </p>
        </div>
        <div className="flex items-center gap-2">
          {workflow.parallel_execution && (
            <span className="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded">
              Parallel Execution
            </span>
          )}
          <span className="px-2 py-1 bg-gray-100 text-gray-800 text-xs rounded">
            {workflow.workflow_id.slice(0, 8)}...
          </span>
        </div>
      </div>

      <div className="h-[calc(100%-4rem)]">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodeDoubleClick={onNodeDoubleClick}
          nodeTypes={nodeTypes}
          fitView
          fitViewOptions={{
            padding: 0.2,
            minZoom: 0.5,
            maxZoom: 1.5,
          }}
        >
          <Background color="#aaa" gap={16} />
          <Controls />
          <MiniMap
            nodeColor={(node) => {
              const steps = workflow.steps || [];
              const step = steps.find((s) => s.step_id === node.id);
              return step
                ? stepTypeColors[
                    step.step_type as keyof typeof stepTypeColors
                  ] || "#6B7280"
                : "#6B7280";
            }}
            nodeStrokeWidth={3}
            position="top-right"
          />
        </ReactFlow>
      </div>
    </div>
  );
}
