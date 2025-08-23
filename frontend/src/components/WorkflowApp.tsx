import { useState } from "react";
import { API_ENDPOINTS, apiPost } from "../config/api";
import { ChatPanel } from "./ChatPanel";
import { CreateWorkflowModal } from "./CreateWorkflowModal";
import { ModeToggle } from "./mode-toggle";
import { ThemeProvider } from "./theme-provider";
import { WorkflowExecutor } from "./WorkflowExecutor";
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
}

export function WorkflowApp() {
  const [selectedWorkflow, setSelectedWorkflow] = useState<Workflow | null>(
    null
  );
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  const handleWorkflowSelect = (workflow: Workflow) => {
    setSelectedWorkflow(workflow);
  };

  const handleCreateWorkflow = async (workflowData: any) => {
    try {
      // Try to create via API using deployed backend
      const response = await apiPost(API_ENDPOINTS.workflows, workflowData);

      if (response.ok) {
        const newWorkflow = await response.json();
        setSelectedWorkflow(newWorkflow);
        // Refresh workflow list would happen in WorkflowSidebar
        console.log("Workflow created successfully:", newWorkflow);
      } else {
        throw new Error("Failed to create workflow");
      }
    } catch (error) {
      console.error("Error creating workflow:", error);
      // For demo purposes, create a mock workflow
      const mockWorkflow: Workflow = {
        workflow_id: `workflow_${Date.now()}`,
        name: workflowData.name,
        description: workflowData.description,
        steps: workflowData.steps || [],
        tags: workflowData.tags || [],
        parallel_execution: workflowData.parallel_execution || false,
        status: "draft",
        created_at: new Date().toISOString(),
        execution_count: 0,
      };
      setSelectedWorkflow(mockWorkflow);
      console.log("Created mock workflow for demo:", mockWorkflow);
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
              {selectedWorkflow && (
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  <span className="font-medium">{selectedWorkflow.name}</span>
                  <span className="mx-2">•</span>
                  <span className="capitalize">{selectedWorkflow.status}</span>
                </div>
              )}
              <ModeToggle />
            </div>
          </div>
        </header>

        {/* Main Layout - Three Column */}
        <div className="flex flex-1 min-h-0">
          {/* Left Sidebar - Workflow Management */}
          <WorkflowSidebar
            selectedWorkflow={selectedWorkflow}
            onWorkflowSelect={handleWorkflowSelect}
            onCreateNew={() => setIsCreateModalOpen(true)}
            className="w-80 border-r border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 flex-shrink-0"
          />

          {/* Center Panel - Workflow Visualization */}
          <div className="flex-1 min-w-0 flex flex-col">
            {selectedWorkflow ? (
              <>
                {/* Workflow Visualization - Top Half */}
                <div className="flex-1 bg-gray-100 dark:bg-gray-900">
                  <WorkflowVisualization
                    workflow={selectedWorkflow}
                    onNodeClick={(nodeId, step) => {
                      console.log("Node clicked:", nodeId, step);
                      // TODO: Handle node click for configuration
                    }}
                  />
                </div>

                {/* Workflow Execution - Bottom Half */}
                <div className="h-96 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 overflow-y-auto">
                  <WorkflowExecutor
                    workflow={selectedWorkflow}
                    onExecutionComplete={(execution) => {
                      console.log("Execution completed:", execution);
                      // TODO: Handle execution completion
                    }}
                    className="h-full"
                  />
                </div>
              </>
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

          {/* Right Sidebar - AI Chat */}
          <div className="w-96 border-l border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 flex-shrink-0">
            <ChatPanel className="h-full" />
          </div>
        </div>

        {/* Create Workflow Modal */}
        <CreateWorkflowModal
          isOpen={isCreateModalOpen}
          onClose={() => setIsCreateModalOpen(false)}
          onCreate={handleCreateWorkflow}
        />
      </div>
    </ThemeProvider>
  );
}
