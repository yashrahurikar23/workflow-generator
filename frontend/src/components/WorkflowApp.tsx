import { useState } from "react";
import { API_ENDPOINTS, apiGet, apiPost, apiPut } from "../config/api";
import { CreateWorkflowModal } from "./CreateWorkflowModal";
import { ModeToggle } from "./mode-toggle";
import { ThemeProvider } from "./theme-provider";
import { WorkflowSidebar } from "./WorkflowSidebar";
import { WorkflowVisualization } from "./WorkflowVisualization";

interface WorkflowStep {
  step_id: string;
  name: string;
  step_type: string;
  description?: string;
  depends_on: string[];
  condition?: any;
  config: any;
}

interface WorkflowNode {
  node_id: string;
  node_type_id: string;
  name: string;
  position: { x: number; y: number };
  config: any;
}

interface WorkflowConnection {
  connection_id: string;
  source_node_id: string;
  target_node_id: string;
  source_output: string;
  target_input: string;
}

interface VisualData {
  nodes: WorkflowNode[];
  connections: WorkflowConnection[];
}

interface Workflow {
  workflow_id: string;
  name: string;
  description: string;
  steps: WorkflowStep[];
  tags: string[];
  parallel_execution: boolean;
  status: string;
  created_at: string;
  execution_count: number;
  visual_data?: VisualData;
  messages?: any[]; // Add messages array for chat
}

export function WorkflowApp() {
  const [selectedWorkflow, setSelectedWorkflow] = useState<Workflow | null>(
    null
  );
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [selectedNode, setSelectedNode] = useState<any>(null);
  const [isConfigPanelOpen, setIsConfigPanelOpen] = useState(false);
  const [editedNodeConfig, setEditedNodeConfig] = useState<any>(null);
  const [isEditMode, setIsEditMode] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  // Chat-related state
  const [isChatPanelOpen, setIsChatPanelOpen] = useState(false);
  const [chatMessage, setChatMessage] = useState("");
  const [isSendingMessage, setIsSendingMessage] = useState(false);

  // Workflow list refresh trigger
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleWorkflowSelect = async (workflow: Workflow) => {
    console.log("Workflow selected in WorkflowApp:", workflow);

    try {
      // Fetch detailed workflow data including visual_data
      const response = await apiGet(
        API_ENDPOINTS.workflowById(workflow.workflow_id)
      );

      if (response.ok) {
        const detailedWorkflow = await response.json();
        console.log("Fetched detailed workflow:", detailedWorkflow);
        setSelectedWorkflow(detailedWorkflow);
      } else {
        console.error("Failed to fetch detailed workflow, using basic data");
        setSelectedWorkflow(workflow);
      }
    } catch (error) {
      console.error("Error fetching detailed workflow:", error);
      // Fallback to the basic workflow data
      setSelectedWorkflow(workflow);
    }
  };

  const handleNodeClick = (nodeId: string, step: WorkflowStep) => {
    console.log("Node clicked:", nodeId, step);
    setSelectedNode(step);
    setEditedNodeConfig({ ...step });
    setIsConfigPanelOpen(true);
    setIsEditMode(false);
  };

  const handleCloseConfigPanel = () => {
    setIsConfigPanelOpen(false);
    setSelectedNode(null);
    setEditedNodeConfig(null);
    setIsEditMode(false);
  };

  const handleToggleEditMode = () => {
    setIsEditMode(!isEditMode);
    if (!isEditMode) {
      // Entering edit mode, reset to current values
      setEditedNodeConfig({ ...selectedNode });
    }
  };

  const handleConfigChange = (field: string, value: any) => {
    setEditedNodeConfig((prev: any) => ({ ...prev, [field]: value }));
  };

  const handleSaveConfiguration = async () => {
    if (!selectedWorkflow || !editedNodeConfig) return;

    setIsSaving(true);
    try {
      // Update the workflow with the modified node configuration
      const updatedWorkflow = { ...selectedWorkflow };

      if (updatedWorkflow.visual_data?.nodes) {
        updatedWorkflow.visual_data.nodes =
          updatedWorkflow.visual_data.nodes.map((node) => {
            if (node.node_id === editedNodeConfig.step_id) {
              return {
                ...node,
                name: editedNodeConfig.name,
                config: editedNodeConfig.config,
              };
            }
            return node;
          });
      }

      // Call the API to update the workflow
      const response = await apiPut(
        API_ENDPOINTS.updateVisualWorkflow(selectedWorkflow.workflow_id),
        updatedWorkflow
      );

      if (response.ok) {
        const updatedWorkflowFromServer = await response.json();
        setSelectedWorkflow(updatedWorkflowFromServer);
        setSelectedNode({ ...editedNodeConfig });
        setIsEditMode(false);
        console.log("Configuration saved successfully");
      } else {
        console.error("Failed to save configuration");
        // Could add error notification here
      }
    } catch (error) {
      console.error("Error saving configuration:", error);
      // Could add error notification here
    } finally {
      setIsSaving(false);
    }
  };

  const handleCreateWorkflow = async (workflowData: any) => {
    try {
      console.log("Creating workflow with data:", workflowData);

      // Try to create via API
      const response = await apiPost(API_ENDPOINTS.workflows, workflowData);

      if (response.ok) {
        const newWorkflow = await response.json();
        console.log("Workflow created successfully:", newWorkflow);

        // Auto-select the new workflow
        setSelectedWorkflow(newWorkflow);

        // Close the create modal
        setIsCreateModalOpen(false);

        // Open the chat panel for the new workflow
        setIsChatPanelOpen(true);

        // Trigger workflow list refresh
        setRefreshTrigger((prev) => prev + 1);

        return; // Success, no need to fall back to mock
      } else {
        console.error("API creation failed, creating mock workflow");
        throw new Error("Failed to create workflow via API");
      }
    } catch (error) {
      console.error("Error creating workflow:", error);

      // Create a mock workflow for demo purposes
      const mockWorkflow: Workflow = {
        workflow_id: `workflow_${Date.now()}`,
        name: workflowData.name,
        description:
          workflowData.description || `A new workflow: ${workflowData.name}`,
        steps: [],
        tags: [],
        parallel_execution: false,
        status: "draft",
        created_at: new Date().toISOString(),
        execution_count: 0,
        visual_data: {
          nodes: [],
          connections: [],
        },
        messages: [],
      };

      // Auto-select the mock workflow
      setSelectedWorkflow(mockWorkflow);

      // Close the create modal
      setIsCreateModalOpen(false);

      // Open the chat panel for the new workflow
      setIsChatPanelOpen(true);

      console.log("Created mock workflow for demo:", mockWorkflow);
    }
  };

  // Chat handlers
  const handleToggleChatPanel = () => {
    if (isConfigPanelOpen) {
      setIsConfigPanelOpen(false);
    }
    setIsChatPanelOpen(!isChatPanelOpen);
  };

  const handleSendChatMessage = async () => {
    if (!chatMessage.trim() || !selectedWorkflow || isSendingMessage) return;

    setIsSendingMessage(true);
    try {
      // Add user message to workflow
      const userMessage = {
        id: `msg_${Date.now()}`,
        role: "user" as const,
        content: chatMessage.trim(),
        timestamp: new Date().toISOString(),
      };

      const updatedMessages = [
        ...(selectedWorkflow.messages || []),
        userMessage,
      ];

      // Update workflow with new message locally first
      const updatedWorkflow = {
        ...selectedWorkflow,
        messages: updatedMessages,
      };

      setSelectedWorkflow(updatedWorkflow);
      setChatMessage("");

      try {
        // Call API to process message and update workflow
        const response = await apiPost(
          API_ENDPOINTS.workflowChat(selectedWorkflow.workflow_id),
          {
            message: userMessage.content,
            current_workflow: selectedWorkflow,
          }
        );

        if (response.ok) {
          const result = await response.json();
          // Update with response from server (includes AI message and updated workflow)
          setSelectedWorkflow(result.updated_workflow);
          console.log("Workflow updated via AI:", result);
        } else {
          throw new Error("Failed to process chat message");
        }
      } catch (apiError) {
        console.error("API call failed, using mock response:", apiError);

        // Fallback to mock AI response
        setTimeout(() => {
          const aiMessage = {
            id: `msg_${Date.now() + 1}`,
            role: "assistant" as const,
            content: `I understand you want to work on "${selectedWorkflow.name}". I can help you build this workflow step by step. 

Right now this is a mock response since the AI backend isn't connected yet, but soon I'll be able to:
• Analyze your request and suggest workflow steps
• Generate nodes and connections for your workflow  
• Update the visual workflow in real-time

What specific functionality would you like to add to this workflow?`,
            timestamp: new Date().toISOString(),
          };

          const finalMessages = [...updatedMessages, aiMessage];
          setSelectedWorkflow((prev) =>
            prev ? { ...prev, messages: finalMessages } : null
          );
        }, 1000);
      }
    } catch (error) {
      console.error("Error sending chat message:", error);
    } finally {
      setIsSendingMessage(false);
    }
  };

  const handleChatKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendChatMessage();
    }
  };

  return (
    <ThemeProvider defaultTheme="light" storageKey="workflow-generator-theme">
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex flex-col">
        {/* Header */}
        <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4 flex-shrink-0">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="text-2xl">⚡</div>
              <div>
                <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
                  Workflow Generator
                </h1>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Build and execute workflows with AI
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              {" "}
              {selectedWorkflow && (
                <div className="flex items-center gap-2">
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    <span className="font-medium">{selectedWorkflow.name}</span>
                    <span className="mx-2">•</span>
                    <span className="capitalize">
                      {selectedWorkflow.status}
                    </span>
                  </div>

                  {/* Chat Toggle Button */}
                  <button
                    onClick={handleToggleChatPanel}
                    className={`px-3 py-1 text-xs font-medium rounded-md transition-colors ${
                      isChatPanelOpen
                        ? "bg-green-100 text-green-700 hover:bg-green-200"
                        : "bg-blue-100 text-blue-700 hover:bg-blue-200"
                    }`}
                  >
                    💬 {isChatPanelOpen ? "Close Chat" : "AI Chat"}
                  </button>
                </div>
              )}
              <ModeToggle />
            </div>
          </div>
        </header>

        {/* Main Layout - Two/Three Column */}
        <div className="flex flex-1 min-h-0">
          {/* Left Sidebar - Workflow Management */}
          <WorkflowSidebar
            selectedWorkflow={selectedWorkflow}
            onWorkflowSelect={handleWorkflowSelect}
            onCreateNew={() => setIsCreateModalOpen(true)}
            refreshTrigger={refreshTrigger}
            className="w-80 border-r border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 flex-shrink-0"
          />

          {/* Center Panel - Workflow Visualization */}
          <div
            className={`flex-1 min-w-0 flex flex-col ${
              isConfigPanelOpen || isChatPanelOpen ? "mr-96" : ""
            }`}
          >
            {selectedWorkflow ? (
              <div className="h-full bg-gray-100 dark:bg-gray-900">
                <WorkflowVisualization
                  workflow={selectedWorkflow}
                  onNodeClick={handleNodeClick}
                />
              </div>
            ) : (
              <div className="h-full flex items-center justify-center">
                <div className="text-center text-gray-500 dark:text-gray-400">
                  <div className="text-6xl mb-4">⚡</div>
                  <h2 className="text-2xl font-semibold mb-2">
                    Select a workflow to get started
                  </h2>
                  <p className="text-lg mb-6">
                    Choose a workflow from the sidebar or create a new one
                  </p>
                  <div className="space-y-2 text-sm">
                    <p>✨ Create workflows from templates</p>
                    <p>🔧 Configure workflow steps</p>
                    <p>🚀 Execute workflows with AI integration</p>
                  </div>
                  <button
                    onClick={() => setIsCreateModalOpen(true)}
                    className="mt-6 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Create Your First Workflow
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Right Panel - Node Configuration */}
          {isConfigPanelOpen && selectedNode && (
            <div className="w-96 border-l border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 flex-shrink-0 fixed right-0 top-0 h-full z-10 shadow-lg">
              <div className="h-full flex flex-col">
                {/* Header */}
                <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      Node Configuration
                    </h3>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={handleToggleEditMode}
                        className={`px-3 py-1 text-xs font-medium rounded-md transition-colors ${
                          isEditMode
                            ? "bg-orange-100 text-orange-700 hover:bg-orange-200"
                            : "bg-blue-100 text-blue-700 hover:bg-blue-200"
                        }`}
                      >
                        {isEditMode ? "Cancel" : "Edit"}
                      </button>
                      <button
                        onClick={handleCloseConfigPanel}
                        className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
                      >
                        ✕
                      </button>
                    </div>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    {selectedNode.name} ({selectedNode.step_type})
                  </p>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-4">
                  <div className="space-y-4">
                    {/* Basic Info */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Node Name
                      </label>
                      <input
                        type="text"
                        value={
                          isEditMode
                            ? editedNodeConfig?.name || ""
                            : selectedNode.name
                        }
                        onChange={(e) =>
                          handleConfigChange("name", e.target.value)
                        }
                        className={`w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white ${
                          isEditMode
                            ? "ring-2 ring-blue-500 ring-opacity-50"
                            : ""
                        }`}
                        readOnly={!isEditMode}
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Node Type
                      </label>
                      <input
                        type="text"
                        value={selectedNode.step_type}
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-gray-50 dark:bg-gray-600 text-gray-600 dark:text-gray-400"
                        readOnly
                      />
                    </div>

                    {selectedNode.description && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          Description
                        </label>
                        <textarea
                          value={
                            isEditMode
                              ? editedNodeConfig?.description || ""
                              : selectedNode.description
                          }
                          onChange={(e) =>
                            handleConfigChange("description", e.target.value)
                          }
                          className={`w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white ${
                            isEditMode
                              ? "ring-2 ring-blue-500 ring-opacity-50"
                              : ""
                          }`}
                          rows={3}
                          readOnly={!isEditMode}
                        />
                      </div>
                    )}

                    {/* Configuration */}
                    {selectedNode.config &&
                      Object.keys(selectedNode.config).length > 0 && (
                        <div>
                          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            Configuration
                          </label>
                          {isEditMode ? (
                            <div className="space-y-3">
                              {Object.entries(
                                editedNodeConfig?.config || selectedNode.config
                              ).map(([key, value]) => (
                                <div key={key}>
                                  <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">
                                    {key}
                                  </label>
                                  <input
                                    type="text"
                                    value={String(value)}
                                    onChange={(e) => {
                                      const newConfig = {
                                        ...editedNodeConfig.config,
                                      };
                                      newConfig[key] = e.target.value;
                                      handleConfigChange("config", newConfig);
                                    }}
                                    className="w-full px-2 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white ring-2 ring-blue-500 ring-opacity-50"
                                  />
                                </div>
                              ))}
                            </div>
                          ) : (
                            <div className="bg-gray-50 dark:bg-gray-800 p-3 rounded-md">
                              <pre className="text-xs text-gray-600 dark:text-gray-400 whitespace-pre-wrap">
                                {JSON.stringify(selectedNode.config, null, 2)}
                              </pre>
                            </div>
                          )}
                        </div>
                      )}

                    {/* Actions */}
                    <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
                      {isEditMode ? (
                        <div className="space-y-2">
                          <button
                            onClick={handleSaveConfiguration}
                            disabled={isSaving}
                            className="w-full px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                          >
                            {isSaving ? (
                              <>
                                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                                Saving...
                              </>
                            ) : (
                              <>💾 Save Changes</>
                            )}
                          </button>
                          <button
                            onClick={handleToggleEditMode}
                            className="w-full px-4 py-2 bg-gray-500 text-white rounded-md hover:bg-gray-600"
                          >
                            Cancel
                          </button>
                        </div>
                      ) : (
                        <button
                          onClick={handleToggleEditMode}
                          className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                        >
                          ✏️ Edit Configuration
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Right Panel - Chat Interface */}
          {isChatPanelOpen && selectedWorkflow && (
            <div className="w-96 border-l border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 flex-shrink-0 fixed right-0 top-0 h-full z-10 shadow-lg">
              <div className="h-full flex flex-col">
                {/* Header */}
                <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      AI Workflow Chat
                    </h3>
                    <button
                      onClick={handleToggleChatPanel}
                      className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
                    >
                      ✕
                    </button>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    Describe what you want to build and I'll help you create it
                  </p>
                </div>

                {/* Chat Messages */}
                <div className="flex-1 overflow-y-auto p-4">
                  <div className="space-y-4">
                    {!selectedWorkflow.messages ||
                    selectedWorkflow.messages.length === 0 ? (
                      <div className="text-center text-gray-500 dark:text-gray-400 py-8">
                        <div className="text-4xl mb-2">🤖</div>
                        <p className="text-sm">
                          Start chatting to build your workflow!
                        </p>
                        <p className="text-xs mt-2">
                          Try: "Add an email trigger that sends a notification"
                        </p>
                      </div>
                    ) : (
                      selectedWorkflow.messages.map((message: any) => (
                        <div
                          key={message.id}
                          className={`flex ${
                            message.role === "user"
                              ? "justify-end"
                              : "justify-start"
                          }`}
                        >
                          <div
                            className={`max-w-[85%] rounded-lg px-3 py-2 ${
                              message.role === "user"
                                ? "bg-blue-600 text-white"
                                : "bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white"
                            }`}
                          >
                            <div className="text-sm whitespace-pre-wrap">
                              {message.content}
                            </div>
                            <div
                              className={`text-xs mt-1 opacity-70 ${
                                message.role === "user"
                                  ? "text-blue-100"
                                  : "text-gray-500"
                              }`}
                            >
                              {new Date(message.timestamp).toLocaleTimeString()}
                            </div>
                          </div>
                        </div>
                      ))
                    )}

                    {isSendingMessage && (
                      <div className="flex justify-start">
                        <div className="bg-gray-100 dark:bg-gray-700 rounded-lg px-3 py-2">
                          <div className="flex items-center space-x-2">
                            <div className="flex space-x-1">
                              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                              <div
                                className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                                style={{ animationDelay: "0.1s" }}
                              ></div>
                              <div
                                className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                                style={{ animationDelay: "0.2s" }}
                              ></div>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Chat Input */}
                <div className="border-t border-gray-200 dark:border-gray-700 p-4">
                  <div className="flex space-x-2">
                    <input
                      type="text"
                      value={chatMessage}
                      onChange={(e) => setChatMessage(e.target.value)}
                      onKeyPress={handleChatKeyPress}
                      placeholder="Describe what you want to add to your workflow..."
                      className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      disabled={isSendingMessage}
                    />
                    <button
                      onClick={handleSendChatMessage}
                      disabled={!chatMessage.trim() || isSendingMessage}
                      className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      📤
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Create Workflow Modal */}
        <CreateWorkflowModal
          isOpen={isCreateModalOpen}
          onClose={() => setIsCreateModalOpen(false)}
          onCreateWorkflow={handleCreateWorkflow}
        />
      </div>
    </ThemeProvider>
  );
}
