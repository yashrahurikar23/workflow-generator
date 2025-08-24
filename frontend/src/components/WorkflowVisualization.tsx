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
import React, { useCallback, useEffect, useMemo } from "react";

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
  // Visual node type mappings
  email_trigger: "#EC4899", // Pink
  ai_model: "#06B6D4", // Cyan
  notification: "#F59E0B", // Yellow
  approval: "#EF4444", // Red
  email_sender: "#EC4899", // Pink
  data_logger: "#84CC16", // Lime
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
  // Visual node type mappings
  email_trigger: "📨",
  ai_model: "🤖",
  notification: "🔔",
  approval: "✋",
  email_sender: "📤",
  data_logger: "📊",
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
  const { step, isSelected, sequenceNumber } = data;
  const color =
    stepTypeColors[step.step_type as keyof typeof stepTypeColors] || "#6B7280";
  const icon =
    stepTypeIcons[step.step_type as keyof typeof stepTypeIcons] || "⚡";

  return (
    <div
      className={`
        px-4 py-3 rounded-lg border-2 bg-white shadow-md min-w-[200px] max-w-[250px] relative
        ${
          isSelected
            ? "border-blue-500 shadow-lg ring-2 ring-blue-200"
            : "border-gray-200"
        }
        hover:shadow-lg hover:border-blue-300 transition-all duration-200 cursor-pointer
      `}
      style={{ borderColor: isSelected ? "#3B82F6" : color }}
    >
      {/* Sequence Number Badge */}
      {sequenceNumber && (
        <div className="absolute -top-2 -right-2 w-6 h-6 bg-blue-600 text-white text-xs font-bold rounded-full flex items-center justify-center shadow-md">
          {sequenceNumber}
        </div>
      )}

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

      {/* Visual indicator for connected nodes */}
      <div className="absolute top-1/2 -left-1 w-2 h-2 bg-gray-400 rounded-full transform -translate-y-1/2 opacity-60"></div>
      <div className="absolute top-1/2 -right-1 w-2 h-2 bg-gray-400 rounded-full transform -translate-y-1/2 opacity-60"></div>
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
    console.log(
      "WorkflowVisualization: Recalculating nodes and edges for workflow:",
      workflow?.workflow_id
    );

    if (!workflow) {
      console.log("WorkflowVisualization: No workflow available");
      return { initialNodes: [], initialEdges: [] };
    }

    // Check if we have visual_data.nodes (new format) or fallback to steps (old format)
    let nodes: Node[] = [];
    let edges: Edge[] = [];

    if (
      workflow.visual_data &&
      workflow.visual_data.nodes &&
      workflow.visual_data.nodes.length > 0
    ) {
      console.log(
        "WorkflowVisualization: Using visual_data with",
        workflow.visual_data.nodes.length,
        "nodes for workflow:",
        workflow.name
      );

      // Use visual_data format
      nodes = workflow.visual_data.nodes.map((node, index) => {
        return {
          id: node.node_id,
          type: "customNode",
          position: node.position || { x: 100, y: 100 },
          data: {
            step: {
              step_id: node.node_id,
              name: node.name,
              step_type: node.node_type_id,
              description: `Node Type: ${node.node_type_id}`,
              depends_on: [],
              config: node.config || {},
            },
            isSelected: false,
            sequenceNumber: index + 1, // Add sequence number for visual order
            onClick: () =>
              onNodeClick?.(node.node_id, {
                step_id: node.node_id,
                name: node.name,
                step_type: node.node_type_id,
                description: `Node Type: ${node.node_type_id}`,
                depends_on: [],
                config: node.config || {},
              }),
          },
          sourcePosition: Position.Right,
          targetPosition: Position.Left,
        };
      });

      // Create edges from connections with enhanced styling
      if (workflow.visual_data.connections) {
        edges = workflow.visual_data.connections.map((connection, index) => {
          // Create sequence numbers based on connection order
          const sequenceNumber = index + 1;

          return {
            id: connection.connection_id,
            source: connection.source_node_id,
            target: connection.target_node_id,
            type: "smoothstep",
            animated: true,
            style: {
              stroke: "#2563EB",
              strokeWidth: 4,
              strokeDasharray: "0",
              filter: "drop-shadow(0 2px 4px rgba(0,0,0,0.1))",
            },
            markerEnd: {
              type: "arrowclosed",
              color: "#2563EB",
              width: 24,
              height: 24,
            },
            label: `${sequenceNumber}. ${connection.source_output} → ${connection.target_input}`,
            labelStyle: {
              fontSize: 12,
              fill: "#1F2937",
              fontWeight: 600,
              background: "white",
              padding: "4px 8px",
              borderRadius: "6px",
              border: "2px solid #2563EB",
              boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
            },
            labelBgPadding: [12, 6] as [number, number],
            labelBgBorderRadius: 6,
            labelBgStyle: {
              fill: "#ffffff",
              fillOpacity: 0.95,
              stroke: "#2563EB",
              strokeWidth: 2,
            },
          };
        });
      }
    } else if (workflow.steps && workflow.steps.length > 0) {
      console.log(
        "WorkflowVisualization: Using steps format with",
        workflow.steps.length,
        "steps for workflow:",
        workflow.name
      );

      // Use legacy steps format
      const steps = workflow.steps;

      // Create nodes
      nodes = steps.map((step, index) => {
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
    } else {
      console.log("WorkflowVisualization: No visual data or steps available");
    }

    return { initialNodes: nodes, initialEdges: edges };
  }, [workflow, onNodeClick]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  // Update nodes and edges when workflow changes
  useEffect(() => {
    console.log(
      "WorkflowVisualization: useEffect triggered, updating nodes and edges"
    );
    console.log("WorkflowVisualization: New nodes count:", initialNodes.length);
    console.log("WorkflowVisualization: New edges count:", initialEdges.length);
    setNodes(initialNodes);
    setEdges(initialEdges);
  }, [initialNodes, initialEdges, setNodes, setEdges]);

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
