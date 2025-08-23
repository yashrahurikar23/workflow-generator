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

interface Workflow {
  workflow_id: string;
  name: string;
  description: string;
  workflow_type: string;
  visual_data?: {
    nodes: SelectedNode[];
    connections: any[];
  };
  status: string;
  created_at: string;
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
      {
        key: "max_tokens",
        type: "number",
        label: "Max Tokens",
        description: "Maximum number of tokens to generate",
        required: false,
        default_value: 1000,
      },
    ],
    inputs: [{ id: "input", label: "Input", type: "string", required: true }],
    outputs: [{ id: "output", label: "Generated Text", type: "string" }],
  },
  {
    id: "webhook_trigger",
    name: "Webhook Trigger",
    description: "Start workflow when a webhook is called",
    category: "triggers",
    icon: "webhook",
    color: "#F59E0B",
    is_template: true,
    tags: ["trigger", "webhook", "http"],
    config_fields: [
      {
        key: "method",
        type: "select",
        label: "HTTP Method",
        description: "HTTP method to accept",
        required: true,
        options: ["GET", "POST", "PUT", "DELETE"],
      },
      {
        key: "path",
        type: "string",
        label: "Webhook Path",
        description: "URL path for the webhook",
        required: true,
      },
    ],
    inputs: [],
    outputs: [{ id: "output", label: "Webhook Data", type: "object" }],
  },
  {
    id: "email_node",
    name: "Send Email",
    description: "Send emails via SMTP or email service provider",
    category: "integrations",
    icon: "mail",
    color: "#3B82F6",
    is_template: false,
    tags: ["email", "notification", "smtp"],
    config_fields: [
      {
        key: "to",
        type: "string",
        label: "To Email",
        description: "Recipient email address",
        required: true,
      },
      {
        key: "subject",
        type: "string",
        label: "Subject",
        description: "Email subject line",
        required: true,
      },
      {
        key: "body",
        type: "textarea",
        label: "Email Body",
        description: "Email content",
        required: true,
      },
    ],
    inputs: [
      { id: "input", label: "Email Data", type: "object", required: true },
    ],
    outputs: [{ id: "output", label: "Send Result", type: "object" }],
  },
];

function App() {
  const [selectedNode, setSelectedNode] = useState<SelectedNode | null>(null);
  const [selectedNodeType, setSelectedNodeType] = useState<NodeType | null>(
    null
  );
  const [currentWorkflow, setCurrentWorkflow] = useState<Workflow | null>(null);

  // Handle node selection from canvas
  const handleNodeSelect = useCallback((node: SelectedNode) => {
    setSelectedNode(node);
    const nodeType = mockNodeTypes.find((nt) => nt.id === node.node_type_id);
    setSelectedNodeType(nodeType || null);
  }, []);

  // Handle node configuration changes
  const handleNodeConfigChange = useCallback(
    (nodeId: string, config: Record<string, any>) => {
      console.log(`Updating config for node ${nodeId}:`, config);
      // TODO: Update node in workflow and save to backend
    },
    []
  );

  // Handle node rename
  const handleNodeRename = useCallback((nodeId: string, name: string) => {
    console.log(`Renaming node ${nodeId} to: ${name}`);
    // TODO: Update node name in workflow and save to backend
  }, []);

  // Handle node drag from palette
  const handleNodeDrag = useCallback((nodeType: NodeType) => {
    console.log(`Dragging node type: ${nodeType.name}`);
  }, []);

  // Handle node click in palette
  const handleNodeClick = useCallback((nodeType: NodeType) => {
    console.log(`Clicked node type: ${nodeType.name}`);
    // TODO: Show node type details or add to canvas
  }, []);

  // Handle closing config panel
  const handleCloseConfigPanel = useCallback(() => {
    setSelectedNode(null);
    setSelectedNodeType(null);
  }, []);

  // Handle node execution for testing
  const handleExecuteNode = useCallback((nodeId: string) => {
    console.log(`Executing node: ${nodeId}`);
    // TODO: Execute single node for testing
  }, []);

  return (
    <ThemeProvider defaultTheme="light" storageKey="workflow-generator-theme">
      <ReactFlowProvider>
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex flex-col">
          {/* Header */}
          <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4 flex-shrink-0">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="text-2xl">🔄</div>
                <div>
                  <h1 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
                    Advanced Workflow Builder
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
