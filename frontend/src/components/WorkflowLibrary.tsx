import { useEffect, useState } from "react";
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

interface WorkflowsResponse {
  workflows: Workflow[];
  total: number;
  page: number;
  size: number;
}

export function WorkflowLibrary() {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [selectedWorkflow, setSelectedWorkflow] = useState<Workflow | null>(
    null
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedStep, setSelectedStep] = useState<WorkflowStep | null>(null);

  useEffect(() => {
    fetchWorkflows();
  }, []);

  const fetchWorkflows = async () => {
    try {
      setLoading(true);
      const response = await fetch("http://localhost:8003/api/v1/workflows/");
      if (!response.ok) {
        throw new Error("Failed to fetch workflows");
      }
      const data: WorkflowsResponse = await response.json();
      setWorkflows(data.workflows);

      // Select the first workflow by default
      if (data.workflows.length > 0) {
        setSelectedWorkflow(data.workflows[0]);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  const handleWorkflowSelect = (workflow: Workflow) => {
    setSelectedWorkflow(workflow);
    setSelectedStep(null);
  };

  const handleNodeClick = (nodeId: string, step: WorkflowStep) => {
    setSelectedStep(step);
  };

  const getStepTypeColor = (stepType: string) => {
    const colors: Record<string, string> = {
      api_call: "bg-blue-100 text-blue-800",
      data_transform: "bg-green-100 text-green-800",
      condition: "bg-yellow-100 text-yellow-800",
      loop: "bg-purple-100 text-purple-800",
      manual: "bg-red-100 text-red-800",
      llm_process: "bg-cyan-100 text-cyan-800",
      email: "bg-pink-100 text-pink-800",
      database: "bg-lime-100 text-lime-800",
      file_operation: "bg-gray-100 text-gray-800",
    };
    return colors[stepType] || "bg-gray-100 text-gray-800";
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading workflows...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="text-red-500 text-lg mb-2">⚠️ Error</div>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={fetchWorkflows}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex">
      {/* Sidebar - Workflow List */}
      <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-800">Workflows</h2>
          <p className="text-sm text-gray-600">
            {workflows.length} workflows available
          </p>
        </div>

        <div className="flex-1 overflow-y-auto">
          {workflows.map((workflow) => (
            <div
              key={workflow.workflow_id}
              className={`p-4 border-b border-gray-100 cursor-pointer hover:bg-gray-50 ${
                selectedWorkflow?.workflow_id === workflow.workflow_id
                  ? "bg-blue-50 border-blue-200"
                  : ""
              }`}
              onClick={() => handleWorkflowSelect(workflow)}
            >
              <div className="flex items-start justify-between mb-2">
                <h3 className="font-medium text-gray-800 truncate">
                  {workflow.name}
                </h3>
                <span
                  className={`px-2 py-1 text-xs rounded ${
                    workflow.status === "active"
                      ? "bg-green-100 text-green-800"
                      : "bg-gray-100 text-gray-800"
                  }`}
                >
                  {workflow.status}
                </span>
              </div>

              <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                {workflow.description}
              </p>

              <div className="flex items-center justify-between text-xs text-gray-500">
                <span>{workflow.steps.length} steps</span>
                <span>{workflow.execution_count} runs</span>
              </div>

              <div className="flex flex-wrap gap-1 mt-2">
                {workflow.tags.slice(0, 3).map((tag) => (
                  <span
                    key={tag}
                    className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded"
                  >
                    {tag}
                  </span>
                ))}
                {workflow.tags.length > 3 && (
                  <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                    +{workflow.tags.length - 3}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Main Content - Workflow Visualization */}
      <div className="flex-1 flex flex-col">
        {selectedWorkflow ? (
          <>
            {/* Workflow Visualization */}
            <div className="flex-1">
              <WorkflowVisualization
                workflow={selectedWorkflow}
                onNodeClick={handleNodeClick}
              />
            </div>

            {/* Step Details Panel */}
            {selectedStep && (
              <div className="h-64 bg-white border-t border-gray-200 p-4 overflow-y-auto">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-lg font-semibold text-gray-800">
                    {selectedStep.name}
                  </h3>
                  <button
                    onClick={() => setSelectedStep(null)}
                    className="text-gray-500 hover:text-gray-700"
                  >
                    ✕
                  </button>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <h4 className="font-medium text-gray-700 mb-2">Details</h4>
                    <div className="space-y-2 text-sm">
                      <div>
                        <span className="text-gray-600">Type:</span>
                        <span
                          className={`ml-2 px-2 py-1 rounded text-xs ${getStepTypeColor(
                            selectedStep.step_type
                          )}`}
                        >
                          {selectedStep.step_type.replace("_", " ")}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-600">ID:</span>
                        <span className="ml-2 font-mono text-xs">
                          {selectedStep.step_id}
                        </span>
                      </div>
                      {selectedStep.description && (
                        <div>
                          <span className="text-gray-600">Description:</span>
                          <p className="ml-2 text-gray-800">
                            {selectedStep.description}
                          </p>
                        </div>
                      )}
                      {selectedStep.depends_on.length > 0 && (
                        <div>
                          <span className="text-gray-600">Depends on:</span>
                          <div className="ml-2 flex flex-wrap gap-1">
                            {selectedStep.depends_on.map((dep) => (
                              <span
                                key={dep}
                                className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded"
                              >
                                {dep}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>

                  <div>
                    <h4 className="font-medium text-gray-700 mb-2">
                      Configuration
                    </h4>
                    <div className="bg-gray-50 p-3 rounded text-xs">
                      <pre className="whitespace-pre-wrap text-gray-800">
                        {JSON.stringify(selectedStep.config, null, 2)}
                      </pre>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center text-gray-500">
              <div className="text-6xl mb-4">📋</div>
              <p>Select a workflow to view its visualization</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
