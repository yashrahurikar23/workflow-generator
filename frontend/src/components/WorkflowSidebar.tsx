import { ChevronRight, Clock, Play, Plus, RefreshCw, Tag } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { API_ENDPOINTS, apiGet } from "../config/api";
import { mockWorkflowsResponse } from "../services/mockData";

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

interface WorkflowSidebarProps {
  selectedWorkflow: Workflow | null;
  onWorkflowSelect: (workflow: Workflow) => void;
  onCreateNew?: () => void;
  refreshTrigger?: number; // Add refresh trigger prop
  className?: string;
}

export function WorkflowSidebar({
  selectedWorkflow,
  onWorkflowSelect,
  onCreateNew,
  refreshTrigger,
  className = "",
}: WorkflowSidebarProps) {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchWorkflows = useCallback(async () => {
    try {
      setLoading(true);

      // Try to fetch from API first using deployed backend
      try {
        const response = await apiGet(API_ENDPOINTS.workflows);
        if (response.ok) {
          const data: WorkflowsResponse = await response.json();
          setWorkflows(data.workflows);

          // Select the first workflow by default if none selected
          if (data.workflows.length > 0 && !selectedWorkflow) {
            onWorkflowSelect(data.workflows[0]);
          }
          setError(null);
          return;
        }
      } catch (apiError) {
        console.log("API not available, using mock data:", apiError);
      }

      // Fallback to mock data
      console.log("Using mock workflow data for demo");
      setWorkflows(mockWorkflowsResponse.workflows);
      setError(null);

      // Select the first workflow by default if none selected
      if (mockWorkflowsResponse.workflows.length > 0 && !selectedWorkflow) {
        onWorkflowSelect(mockWorkflowsResponse.workflows[0]);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
      // Even on error, show mock data
      setWorkflows(mockWorkflowsResponse.workflows);
    } finally {
      setLoading(false);
    }
  }, [selectedWorkflow, onWorkflowSelect]);

  useEffect(() => {
    fetchWorkflows();
  }, [fetchWorkflows]);

  // Refresh workflows when refreshTrigger changes
  useEffect(() => {
    if (refreshTrigger !== undefined && refreshTrigger > 0) {
      fetchWorkflows();
    }
  }, [refreshTrigger, fetchWorkflows]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "bg-green-100 text-green-800";
      case "draft":
        return "bg-yellow-100 text-yellow-800";
      case "paused":
        return "bg-orange-100 text-orange-800";
      case "failed":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getStepTypeIcon = (stepType: string) => {
    const icons: Record<string, string> = {
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
    return icons[stepType] || "⚡";
  };

  if (loading) {
    return (
      <div className={`bg-white border-r border-gray-200 ${className}`}>
        <div className="p-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-800">Workflows</h2>
        </div>
        <div className="p-4">
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`bg-white border-r border-gray-200 ${className}`}>
        <div className="p-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-800">Workflows</h2>
        </div>
        <div className="p-4">
          <div className="text-center text-red-500">
            <p className="text-sm mb-2">Error loading workflows</p>
            <button
              onClick={fetchWorkflows}
              className="text-xs text-blue-600 hover:text-blue-800"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      className={`bg-white border-r border-gray-200 flex flex-col ${className}`}
    >
      {/* Header */}
      <div className="p-4 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-semibold text-gray-800">Workflows</h2>
          <button
            onClick={fetchWorkflows}
            className="p-1 text-gray-500 hover:text-gray-700 rounded"
            title="Refresh workflows"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>

        {/* Create New Workflow Button */}
        <button
          onClick={onCreateNew}
          className="w-full flex items-center justify-center space-x-2 px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-sm font-medium mb-3"
        >
          <Plus className="w-4 h-4" />
          <span>Create New Workflow</span>
        </button>

        <p className="text-sm text-gray-600">
          {workflows.length} workflow{workflows.length !== 1 ? "s" : ""}{" "}
          available
        </p>
      </div>

      {/* Workflows List */}
      <div className="flex-1 overflow-y-auto">
        {workflows.length === 0 ? (
          <div className="p-4 text-center text-gray-500">
            <p className="text-sm">No workflows found</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {workflows.map((workflow) => (
              <div
                key={workflow.workflow_id}
                className={`p-4 cursor-pointer hover:bg-gray-50 transition-colors ${
                  selectedWorkflow?.workflow_id === workflow.workflow_id
                    ? "bg-blue-50 border-r-2 border-blue-500"
                    : ""
                }`}
                onClick={() => onWorkflowSelect(workflow)}
              >
                {/* Workflow Header */}
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-medium text-gray-800 text-sm leading-tight line-clamp-2">
                    {workflow.name}
                  </h3>
                  <ChevronRight
                    className={`w-4 h-4 text-gray-400 ml-2 flex-shrink-0 ${
                      selectedWorkflow?.workflow_id === workflow.workflow_id
                        ? "text-blue-500"
                        : ""
                    }`}
                  />
                </div>

                {/* Status and Execution Count */}
                <div className="flex items-center justify-between mb-2">
                  <span
                    className={`px-2 py-1 text-xs rounded-full ${getStatusColor(
                      workflow.status
                    )}`}
                  >
                    {workflow.status}
                  </span>
                  <div className="flex items-center text-xs text-gray-500">
                    <Play className="w-3 h-3 mr-1" />
                    {workflow.execution_count} runs
                  </div>
                </div>

                {/* Description */}
                <p className="text-xs text-gray-600 mb-3 line-clamp-2">
                  {workflow.description}
                </p>

                {/* Steps Info */}
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center text-xs text-gray-500">
                    <span className="font-medium">{workflow.steps.length}</span>
                    <span className="ml-1">steps</span>
                  </div>
                  {workflow.parallel_execution && (
                    <span className="text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded">
                      Parallel
                    </span>
                  )}
                </div>

                {/* Step Types Preview */}
                <div className="flex items-center space-x-1 mb-2">
                  {Array.from(new Set(workflow.steps.map((s) => s.step_type)))
                    .slice(0, 4)
                    .map((stepType) => (
                      <span key={stepType} className="text-xs" title={stepType}>
                        {getStepTypeIcon(stepType)}
                      </span>
                    ))}
                  {workflow.steps.length > 4 && (
                    <span className="text-xs text-gray-500">
                      +{workflow.steps.length - 4}
                    </span>
                  )}
                </div>

                {/* Tags */}
                <div className="flex flex-wrap gap-1">
                  {workflow.tags.slice(0, 2).map((tag) => (
                    <span
                      key={tag}
                      className="inline-flex items-center px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full"
                    >
                      <Tag className="w-2 h-2 mr-1" />
                      {tag}
                    </span>
                  ))}
                  {workflow.tags.length > 2 && (
                    <span className="text-xs text-gray-500 px-2 py-1">
                      +{workflow.tags.length - 2} more
                    </span>
                  )}
                </div>

                {/* Created Date */}
                <div className="flex items-center text-xs text-gray-400 mt-2">
                  <Clock className="w-3 h-3 mr-1" />
                  {new Date(workflow.created_at).toLocaleDateString()}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200 bg-gray-50">
        <button
          onClick={() =>
            window.open(`${window.location.origin}/create`, "_blank")
          }
          className="w-full px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors"
        >
          Create New Workflow
        </button>
      </div>
    </div>
  );
}
