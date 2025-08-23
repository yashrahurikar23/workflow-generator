import { ReactFlowProvider } from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { useCallback, useState } from "react";

import { ChatPanel } from "./components/ChatPanel";
import { ModeToggle } from "./components/mode-toggle";
import NodeConfigPanel from "./components/NodeConfigPanel";
import NodePalette from "./components/NodePalette";
import { ThemeProvider } from "./components/theme-provider";
import { WorkflowVisualization } from "./components/WorkflowVisualization";

// Enhanced interfaces for the node-based editor
interface NodeType {
  id: string;
  name: string;
  description: string;
  category: string;
  icon: string;
  color: string;
  is_template: boolean;
  tags: string[];
  config_fields: ConfigField[];
  inputs: any[];
  outputs: any[];
}

interface ConfigField {
  key: string;
  type:
    | "string"
    | "number"
    | "boolean"
    | "select"
    | "json"
    | "textarea"
    | "slider";
  label: string;
  description?: string;
  required: boolean;
  default_value?: any;
  options?: string[];
  validation?: any;
  min?: number;
  max?: number;
  step?: number;
}

interface NodeCategory {
  id: string;
  name: string;
  description: string;
  icon: string;
  color: string;
  order: number;
}

interface SelectedNode {
  node_id: string;
  node_type_id: string;
  name: string;
  config: Record<string, any>;
  position: { x: number; y: number };
}

interface WorkflowStep {
  step_id: string;
  name: string;
  step_type: string;
  description?: string;
  depends_on: string[];
  condition?: any;
  config: any;
}

interface Workflow {
  workflow_id: string;
  name: string;
  description: string;
  workflow_type?: string;
  steps?: WorkflowStep[];
  visual_data?: {
    nodes: SelectedNode[];
    connections: any[];
  };
  tags?: string[];
  parallel_execution?: boolean;
  status: string;
  created_at: string;
  execution_count?: number;
}

// Mock data for development
const mockNodeCategories: NodeCategory[] = [
  {
    id: "ai_models",
    name: "AI Models",
    description: "Large Language Models and AI processing nodes",
    icon: "brain",
    color: "#8B5CF6",
    order: 1,
  },
  {
    id: "triggers",
    name: "Triggers",
    description: "Events that start workflow execution",
    icon: "zap",
    color: "#F59E0B",
    order: 2,
  },
  {
    id: "data_processing",
    name: "Data Processing",
    description: "Transform, filter, and manipulate data",
    icon: "database",
    color: "#10B981",
    order: 3,
  },
  {
    id: "integrations",
    name: "Integrations",
    description: "Connect to external services and APIs",
    icon: "plug",
    color: "#3B82F6",
    order: 4,
  },
];

const mockNodeTypes: NodeType[] = [
  {
    id: "ai_model",
    name: "AI Model",
    description:
      "Process text using Large Language Models like GPT, Claude, or Llama",
    category: "ai_models",
    icon: "brain",
    color: "#8B5CF6",
    is_template: true,
    tags: ["ai", "llm", "gpt", "claude"],
    config_fields: [
      {
        key: "provider",
        type: "select",
        label: "AI Provider",
        description: "Choose the AI service provider",
        required: true,
        options: ["OpenAI", "Anthropic", "Google", "Local"],
      },
      {
        key: "model",
        type: "select",
        label: "Model",
        description: "Select the specific model to use",
        required: true,
        options: ["gpt-4", "gpt-3.5-turbo", "claude-3-sonnet", "gemini-pro"],
      },
      {
        key: "prompt",
        type: "textarea",
        label: "Prompt",
        description: "The prompt to send to the AI model",
        required: true,
      },
      {
        key: "temperature",
        type: "slider",
        label: "Temperature",
        description:
          "Controls randomness in responses (0 = deterministic, 1 = creative)",
        required: false,
        default_value: 0.7,
        min: 0,
        max: 1,
        step: 0.1,
      },
    ],
    inputs: [
      { name: "text", type: "string", description: "Input text to process" },
    ],
    outputs: [
      { name: "result", type: "string", description: "AI model response" },
    ],
  },
  {
    id: "manual_trigger",
    name: "Manual Trigger",
    description: "Manually start a workflow execution",
    category: "triggers",
    icon: "play",
    color: "#F59E0B",
    is_template: true,
    tags: ["trigger", "manual", "start"],
    config_fields: [
      {
        key: "name",
        type: "string",
        label: "Trigger Name",
        description: "Name for this trigger",
        required: true,
        default_value: "Manual Start",
      },
    ],
    inputs: [],
    outputs: [
      { name: "triggered", type: "boolean", description: "Trigger signal" },
    ],
  },
  {
    id: "data_transformer",
    name: "Data Transformer",
    description: "Transform and manipulate data using custom logic",
    category: "data_processing",
    icon: "shuffle",
    color: "#10B981",
    is_template: true,
    tags: ["data", "transform", "processing"],
    config_fields: [
      {
        key: "operation",
        type: "select",
        label: "Operation",
        description: "Type of data transformation",
        required: true,
        options: ["filter", "map", "reduce", "sort", "group"],
      },
      {
        key: "expression",
        type: "textarea",
        label: "Transformation Logic",
        description: "JavaScript expression for data transformation",
        required: true,
      },
    ],
    inputs: [
      { name: "data", type: "any", description: "Input data to transform" },
    ],
    outputs: [{ name: "result", type: "any", description: "Transformed data" }],
  },
];

// Mock workflow for testing
const mockWorkflow: Workflow = {
  workflow_id: "mock-workflow-1",
  name: "Sample AI Workflow",
  description: "A sample workflow demonstrating AI processing",
  workflow_type: "visual",
  status: "active",
  created_at: new Date().toISOString(),
  steps: [
    {
      step_id: "trigger-1",
      name: "Start Process",
      step_type: "manual_trigger",
      description: "Manual trigger to start the workflow",
      depends_on: [],
      config: { name: "Start Process" },
    },
    {
      step_id: "ai-1",
      name: "AI Analysis",
      step_type: "ai_model",
      description: "Analyze input with AI",
      depends_on: ["trigger-1"],
      config: {
        provider: "OpenAI",
        model: "gpt-4",
        prompt: "Analyze the following text and provide insights:",
        temperature: 0.7,
      },
    },
  ],
};

function App() {
  const [currentWorkflow] = useState<Workflow | null>(mockWorkflow);
  const [selectedNode, setSelectedNode] = useState<SelectedNode | null>(null);
  const [selectedNodeType, setSelectedNodeType] = useState<NodeType | null>(
    null
  );

  // Node palette handlers
  const handleNodeDrag = useCallback((nodeType: NodeType) => {
    console.log("Node dragged:", nodeType);
  }, []);

  const handleNodeClick = useCallback((nodeType: NodeType) => {
    console.log("Node clicked from palette:", nodeType);
    // TODO: Add node to canvas
  }, []);

  // Node selection and configuration
  const handleNodeSelect = useCallback((node: SelectedNode) => {
    setSelectedNode(node);
    const nodeType = mockNodeTypes.find((nt) => nt.id === node.node_type_id);
    setSelectedNodeType(nodeType || null);
  }, []);

  const handleNodeConfigChange = useCallback(
    (nodeId: string, config: Record<string, any>) => {
      console.log("Node config changed:", nodeId, config);
      // TODO: Update node configuration
    },
    []
  );

  const handleNodeRename = useCallback((nodeId: string, newName: string) => {
    console.log("Node renamed:", nodeId, newName);
    // TODO: Update node name
  }, []);

  const handleCloseConfigPanel = useCallback(() => {
    setSelectedNode(null);
    setSelectedNodeType(null);
  }, []);

  const handleExecuteNode = useCallback((nodeId: string) => {
    console.log("Execute node:", nodeId);
    // TODO: Execute single node
  }, []);

  return (
    <ThemeProvider defaultTheme="light" storageKey="workflow-generator-theme">
      <ReactFlowProvider>
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex flex-col">
          {/* Header */}
          <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4 flex-shrink-0">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="text-2xl">🎨</div>
                <div>
                  <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
                    Workflow Builder
                  </h1>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    n8n-style visual workflow automation with AI
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                {currentWorkflow && (
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    <span className="font-medium">{currentWorkflow.name}</span>
                    <span className="mx-2">•</span>
                    <span className="capitalize">{currentWorkflow.status}</span>
                  </div>
                )}
                <ModeToggle />
              </div>
            </div>
          </header>

          {/* Main Layout - Three Column */}
          <div className="flex flex-1 min-h-0">
            {/* Left Sidebar - Node Palette */}
            <NodePalette
              categories={mockNodeCategories}
              nodeTypes={mockNodeTypes}
              onNodeDrag={handleNodeDrag}
              onNodeClick={handleNodeClick}
            />

            {/* Center - Workflow Canvas */}
            <div className="flex-1 min-w-0">
              <div className="h-full bg-gray-100 dark:bg-gray-900">
                {currentWorkflow ? (
                  <WorkflowVisualization
                    workflow={currentWorkflow}
                    onNodeClick={(nodeId, step) => {
                      // Convert step to SelectedNode format
                      const selectedNode: SelectedNode = {
                        node_id: nodeId,
                        node_type_id: step.step_type,
                        name: step.name,
                        config: step.config,
                        position: { x: 0, y: 0 }, // TODO: Get actual position
                      };
                      handleNodeSelect(selectedNode);
                    }}
                  />
                ) : (
                  <div className="h-full flex items-center justify-center">
                    <div className="text-center text-gray-500 dark:text-gray-400">
                      <div className="text-6xl mb-4">🎨</div>
                      <h2 className="text-2xl font-semibold mb-2">
                        Start Building Your Workflow
                      </h2>
                      <p className="text-lg mb-6">
                        Drag nodes from the left panel to create your workflow
                      </p>
                      <div className="space-y-2 text-sm">
                        <p>✨ Drag and drop nodes to build workflows</p>
                        <p>🔧 Configure nodes in the right panel</p>
                        <p>🚀 Execute workflows with AI integration</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Right Sidebar - Node Config or Chat */}
            <div className="w-96 border-l border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 flex-shrink-0">
              {selectedNode && selectedNodeType ? (
                <NodeConfigPanel
                  selectedNode={selectedNode}
                  nodeType={selectedNodeType}
                  onConfigChange={handleNodeConfigChange}
                  onNodeRename={handleNodeRename}
                  onClose={handleCloseConfigPanel}
                  onExecuteNode={handleExecuteNode}
                />
              ) : (
                <ChatPanel className="h-full" />
              )}
            </div>
          </div>
        </div>
      </ReactFlowProvider>
    </ThemeProvider>
  );
}

export default App;
