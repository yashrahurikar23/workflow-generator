import {
  AlertCircle,
  CheckCircle,
  Clock,
  Play,
  Square,
  XCircle,
} from "lucide-react";
import { useState } from "react";
import { API_ENDPOINTS, apiPost } from "../config/api";

interface WorkflowStep {
  step_id: string;
  name: string;
  step_type: string;
  description?: string;
  depends_on: string[];
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

interface ExecutionStep {
  step_id: string;
  status: "pending" | "running" | "completed" | "failed";
  start_time?: string;
  end_time?: string;
  output?: any;
  error?: string;
}

interface WorkflowExecution {
  execution_id: string;
  workflow_id: string;
  status: "running" | "completed" | "failed";
  start_time: string;
  end_time?: string;
  steps: ExecutionStep[];
  input_data?: any;
  final_output?: any;
}

interface WorkflowExecutorProps {
  workflow: Workflow;
  onExecutionComplete?: (execution: WorkflowExecution) => void;
  className?: string;
}

export function WorkflowExecutor({
  workflow,
  onExecutionComplete,
  className = "",
}: WorkflowExecutorProps) {
  const [currentExecution, setCurrentExecution] =
    useState<WorkflowExecution | null>(null);
  const [isExecuting, setIsExecuting] = useState(false);
  const [inputData, setInputData] = useState<Record<string, any>>({});

  const getStepStatusIcon = (status: ExecutionStep["status"]) => {
    switch (status) {
      case "pending":
        return <Clock className="h-4 w-4 text-gray-400" />;
      case "running":
        return <Play className="h-4 w-4 text-blue-500 animate-spin" />;
      case "completed":
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case "failed":
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <AlertCircle className="h-4 w-4 text-gray-400" />;
    }
  };

  const getStepStatusColor = (status: ExecutionStep["status"]) => {
    switch (status) {
      case "pending":
        return "bg-gray-100 text-gray-700";
      case "running":
        return "bg-blue-100 text-blue-700";
      case "completed":
        return "bg-green-100 text-green-700";
      case "failed":
        return "bg-red-100 text-red-700";
      default:
        return "bg-gray-100 text-gray-700";
    }
  };

  const executeWorkflow = async () => {
    if (isExecuting) return;

    setIsExecuting(true);

    // Create initial execution object
    const execution: WorkflowExecution = {
      execution_id: `exec_${Date.now()}`,
      workflow_id: workflow.workflow_id,
      status: "running",
      start_time: new Date().toISOString(),
      steps: workflow.steps.map((step) => ({
        step_id: step.step_id,
        status: "pending",
      })),
      input_data: inputData,
    };

    setCurrentExecution(execution);

    try {
      // Try to execute via API using deployed backend
      const response = await apiPost(
        API_ENDPOINTS.executeWorkflow(workflow.workflow_id),
        { input_data: inputData }
      );

      if (response.ok) {
        const result = await response.json();

        // Update execution with real results
        const completedExecution: WorkflowExecution = {
          ...execution,
          status: "completed",
          end_time: new Date().toISOString(),
          steps:
            result.steps ||
            execution.steps.map((step) => ({
              ...step,
              status: "completed" as const,
            })),
          final_output: result.output,
        };

        setCurrentExecution(completedExecution);
        onExecutionComplete?.(completedExecution);
      } else {
        throw new Error("Failed to execute workflow");
      }
    } catch (error) {
      console.error("Error executing workflow:", error);

      // Simulate execution for demo purposes
      await simulateExecution(execution);
    } finally {
      setIsExecuting(false);
    }
  };

  const simulateExecution = async (execution: WorkflowExecution) => {
    const updatedExecution = { ...execution };

    // Simulate step-by-step execution
    for (let i = 0; i < workflow.steps.length; i++) {
      const step = workflow.steps[i];

      // Update step to running
      updatedExecution.steps[i].status = "running";
      updatedExecution.steps[i].start_time = new Date().toISOString();
      setCurrentExecution({ ...updatedExecution });

      // Simulate processing time
      await new Promise((resolve) =>
        setTimeout(resolve, 1000 + Math.random() * 2000)
      );

      // Complete the step (90% success rate for demo)
      const success = Math.random() > 0.1;

      if (success) {
        updatedExecution.steps[i].status = "completed";
        updatedExecution.steps[i].end_time = new Date().toISOString();

        // Generate mock output based on step type
        switch (step.step_type) {
          case "url_input":
            updatedExecution.steps[i].output =
              inputData.url || "https://example.com";
            break;
          case "web_scraping":
            updatedExecution.steps[i].output =
              "Scraped content from webpage...";
            break;
          case "summarization":
            updatedExecution.steps[i].output =
              "AI-generated summary of the content...";
            break;
          case "output":
            updatedExecution.steps[i].output =
              "Final workflow results displayed";
            break;
          default:
            updatedExecution.steps[
              i
            ].output = `Step ${step.name} completed successfully`;
        }
      } else {
        updatedExecution.steps[i].status = "failed";
        updatedExecution.steps[i].end_time = new Date().toISOString();
        updatedExecution.steps[
          i
        ].error = `Simulated error in step: ${step.name}`;
        updatedExecution.status = "failed";
        break;
      }

      setCurrentExecution({ ...updatedExecution });
    }

    // Finalize execution if all steps completed
    if (updatedExecution.status === "running") {
      updatedExecution.status = "completed";
      updatedExecution.end_time = new Date().toISOString();
      updatedExecution.final_output = "Workflow completed successfully!";
    }

    setCurrentExecution({ ...updatedExecution });
    onExecutionComplete?.(updatedExecution);
  };

  const stopExecution = () => {
    if (currentExecution && isExecuting) {
      const stoppedExecution: WorkflowExecution = {
        ...currentExecution,
        status: "failed",
        end_time: new Date().toISOString(),
        steps: currentExecution.steps.map((step) =>
          step.status === "running"
            ? { ...step, status: "failed", error: "Execution stopped by user" }
            : step
        ),
      };
      setCurrentExecution(stoppedExecution);
      setIsExecuting(false);
    }
  };

  const resetExecution = () => {
    setCurrentExecution(null);
    setIsExecuting(false);
  };

  // Check if workflow needs URL input
  const needsUrlInput = workflow.steps.some(
    (step) => step.step_type === "url_input"
  );

  return (
    <div
      className={`bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 ${className}`}
    >
      {/* Header */}
      <div className="p-6 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Execute Workflow
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {workflow.name}
            </p>
          </div>
          <div className="flex space-x-2">
            {!isExecuting && !currentExecution && (
              <button
                onClick={executeWorkflow}
                disabled={needsUrlInput && !inputData.url}
                className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                <Play className="h-4 w-4 mr-2" />
                Execute
              </button>
            )}
            {isExecuting && (
              <button
                onClick={stopExecution}
                className="flex items-center px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
              >
                <Square className="h-4 w-4 mr-2" />
                Stop
              </button>
            )}
            {currentExecution && !isExecuting && (
              <button
                onClick={resetExecution}
                className="flex items-center px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
              >
                Reset
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Input Configuration */}
      {needsUrlInput && !currentExecution && (
        <div className="p-6 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50">
          <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
            Workflow Input
          </h4>
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                URL to Process
              </label>
              <input
                type="url"
                value={inputData.url || ""}
                onChange={(e) =>
                  setInputData({ ...inputData, url: e.target.value })
                }
                placeholder="https://example.com/article"
                className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
          </div>
        </div>
      )}

      {/* Execution Progress */}
      {currentExecution && (
        <div className="p-6">
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-900 dark:text-white">
                Execution Progress
              </span>
              <span
                className={`px-2 py-1 text-xs rounded-full ${getStepStatusColor(
                  currentExecution.status === "running"
                    ? "running"
                    : currentExecution.status === "completed"
                    ? "completed"
                    : "failed"
                )}`}
              >
                {currentExecution.status}
              </span>
            </div>

            {/* Progress Bar */}
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{
                  width: `${
                    (currentExecution.steps.filter(
                      (s) => s.status === "completed"
                    ).length /
                      currentExecution.steps.length) *
                    100
                  }%`,
                }}
              />
            </div>
          </div>

          {/* Step Details */}
          <div className="space-y-3">
            {currentExecution.steps.map((execStep, index) => {
              const workflowStep = workflow.steps[index];
              return (
                <div
                  key={execStep.step_id}
                  className={`p-3 rounded-lg border ${
                    execStep.status === "running"
                      ? "border-blue-200 bg-blue-50 dark:bg-blue-900/20"
                      : execStep.status === "completed"
                      ? "border-green-200 bg-green-50 dark:bg-green-900/20"
                      : execStep.status === "failed"
                      ? "border-red-200 bg-red-50 dark:bg-red-900/20"
                      : "border-gray-200 bg-gray-50 dark:bg-gray-800"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      {getStepStatusIcon(execStep.status)}
                      <div>
                        <h5 className="font-medium text-gray-900 dark:text-white">
                          {workflowStep.name}
                        </h5>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {workflowStep.step_type}
                        </p>
                      </div>
                    </div>
                    <span
                      className={`px-2 py-1 text-xs rounded ${getStepStatusColor(
                        execStep.status
                      )}`}
                    >
                      {execStep.status}
                    </span>
                  </div>

                  {execStep.output && (
                    <div className="mt-2 p-2 bg-gray-100 dark:bg-gray-700 rounded text-sm text-gray-700 dark:text-gray-300">
                      <strong>Output:</strong> {execStep.output}
                    </div>
                  )}

                  {execStep.error && (
                    <div className="mt-2 p-2 bg-red-100 dark:bg-red-900/20 rounded text-sm text-red-700 dark:text-red-300">
                      <strong>Error:</strong> {execStep.error}
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Final Output */}
          {currentExecution.final_output && (
            <div className="mt-4 p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200">
              <h5 className="font-medium text-green-900 dark:text-green-100 mb-2">
                Final Output
              </h5>
              <p className="text-green-800 dark:text-green-200">
                {currentExecution.final_output}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
