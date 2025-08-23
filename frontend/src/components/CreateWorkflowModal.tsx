import { Plus, Trash2, X } from "lucide-react";
import { useState } from "react";

interface WorkflowStep {
  step_id: string;
  name: string;
  step_type: string;
  description?: string;
  depends_on: string[];
  config: any;
}

interface CreateWorkflowModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreate: (workflowData: any) => void;
}

const STEP_TYPES = [
  {
    value: "url_input",
    label: "URL Input",
    description: "Accept a website URL",
  },
  {
    value: "web_scraping",
    label: "Web Scraping",
    description: "Extract content from a webpage",
  },
  {
    value: "summarization",
    label: "AI Summarization",
    description: "Summarize content using AI",
  },
  { value: "output", label: "Output", description: "Display final results" },
  {
    value: "email_send",
    label: "Send Email",
    description: "Send email with results",
  },
  {
    value: "data_transform",
    label: "Data Transform",
    description: "Transform or filter data",
  },
];

const WORKFLOW_TEMPLATES = [
  {
    name: "Web Scraping Workflow",
    description: "Simple URL to content summarization",
    steps: [
      { step_type: "url_input", name: "Enter URL", config: {} },
      { step_type: "web_scraping", name: "Scrape Content", config: {} },
      { step_type: "summarization", name: "Summarize", config: {} },
      { step_type: "output", name: "Show Results", config: {} },
    ],
  },
  {
    name: "Content Analysis",
    description: "Analyze and transform web content",
    steps: [
      { step_type: "url_input", name: "Enter URL", config: {} },
      { step_type: "web_scraping", name: "Extract Content", config: {} },
      { step_type: "data_transform", name: "Process Data", config: {} },
      { step_type: "summarization", name: "Generate Summary", config: {} },
      { step_type: "output", name: "Display Results", config: {} },
    ],
  },
];

export function CreateWorkflowModal({
  isOpen,
  onClose,
  onCreate,
}: CreateWorkflowModalProps) {
  const [currentStep, setCurrentStep] = useState<
    "template" | "details" | "steps"
  >("template");
  const [selectedTemplate, setSelectedTemplate] = useState<any>(null);
  const [workflowName, setWorkflowName] = useState("");
  const [workflowDescription, setWorkflowDescription] = useState("");
  const [workflowTags, setWorkflowTags] = useState("");
  const [steps, setSteps] = useState<Partial<WorkflowStep>[]>([]);
  const [parallelExecution, setParallelExecution] = useState(false);

  if (!isOpen) return null;

  const handleTemplateSelect = (template: any) => {
    setSelectedTemplate(template);
    setWorkflowName(template.name);
    setWorkflowDescription(template.description);
    setSteps(
      template.steps.map((step: any, index: number) => ({
        step_id: `step_${index + 1}`,
        name: step.name,
        step_type: step.step_type,
        description:
          STEP_TYPES.find((t) => t.value === step.step_type)?.description || "",
        depends_on: index > 0 ? [`step_${index}`] : [],
        config: step.config || {},
      }))
    );
    setCurrentStep("details");
  };

  const handleAddStep = () => {
    const newStep: Partial<WorkflowStep> = {
      step_id: `step_${steps.length + 1}`,
      name: "",
      step_type: "url_input",
      description: "",
      depends_on: steps.length > 0 ? [`step_${steps.length}`] : [],
      config: {},
    };
    setSteps([...steps, newStep]);
  };

  const handleRemoveStep = (index: number) => {
    const newSteps = steps.filter((_, i) => i !== index);
    // Update step IDs and dependencies
    const updatedSteps = newSteps.map((step, i) => ({
      ...step,
      step_id: `step_${i + 1}`,
      depends_on: i > 0 ? [`step_${i}`] : [],
    }));
    setSteps(updatedSteps);
  };

  const handleStepChange = (index: number, field: string, value: any) => {
    const newSteps = [...steps];
    newSteps[index] = { ...newSteps[index], [field]: value };
    setSteps(newSteps);
  };

  const handleCreate = () => {
    const workflowData = {
      name: workflowName,
      description: workflowDescription,
      tags: workflowTags
        .split(",")
        .map((tag) => tag.trim())
        .filter((tag) => tag),
      steps: steps.map((step, index) => ({
        ...step,
        step_id: `step_${index + 1}`,
        depends_on: index > 0 ? [`step_${index}`] : [],
      })),
      parallel_execution: parallelExecution,
      status: "draft",
    };
    onCreate(workflowData);
    handleClose();
  };

  const handleClose = () => {
    setCurrentStep("template");
    setSelectedTemplate(null);
    setWorkflowName("");
    setWorkflowDescription("");
    setWorkflowTags("");
    setSteps([]);
    setParallelExecution(false);
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Create New Workflow
          </h2>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Progress Steps */}
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-4">
            <div
              className={`flex items-center ${
                currentStep === "template" ? "text-blue-600" : "text-gray-400"
              }`}
            >
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                  currentStep === "template"
                    ? "bg-blue-600 text-white"
                    : "bg-gray-200 text-gray-600"
                }`}
              >
                1
              </div>
              <span className="ml-2">Choose Template</span>
            </div>
            <div className="w-8 h-px bg-gray-300"></div>
            <div
              className={`flex items-center ${
                currentStep === "details" ? "text-blue-600" : "text-gray-400"
              }`}
            >
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                  currentStep === "details"
                    ? "bg-blue-600 text-white"
                    : "bg-gray-200 text-gray-600"
                }`}
              >
                2
              </div>
              <span className="ml-2">Workflow Details</span>
            </div>
            <div className="w-8 h-px bg-gray-300"></div>
            <div
              className={`flex items-center ${
                currentStep === "steps" ? "text-blue-600" : "text-gray-400"
              }`}
            >
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                  currentStep === "steps"
                    ? "bg-blue-600 text-white"
                    : "bg-gray-200 text-gray-600"
                }`}
              >
                3
              </div>
              <span className="ml-2">Configure Steps</span>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[60vh]">
          {/* Step 1: Template Selection */}
          {currentStep === "template" && (
            <div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                Choose a Workflow Template
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {WORKFLOW_TEMPLATES.map((template, index) => (
                  <div
                    key={index}
                    className={`border rounded-lg p-4 cursor-pointer transition-all ${
                      selectedTemplate === template
                        ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
                        : "border-gray-200 dark:border-gray-700 hover:border-gray-300"
                    }`}
                    onClick={() => handleTemplateSelect(template)}
                  >
                    <h4 className="font-medium text-gray-900 dark:text-white">
                      {template.name}
                    </h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                      {template.description}
                    </p>
                    <div className="mt-3">
                      <p className="text-xs text-gray-500 dark:text-gray-500 mb-2">
                        Steps:
                      </p>
                      <div className="space-y-1">
                        {template.steps.map((step: any, stepIndex: number) => (
                          <div
                            key={stepIndex}
                            className="flex items-center text-xs text-gray-600 dark:text-gray-400"
                          >
                            <div className="w-2 h-2 bg-gray-400 rounded-full mr-2"></div>
                            {step.name}
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              <div className="mt-6">
                <button
                  onClick={() => {
                    setSteps([]);
                    setCurrentStep("details");
                  }}
                  className="text-sm text-blue-600 hover:text-blue-800 dark:text-blue-400"
                >
                  Or start from scratch →
                </button>
              </div>
            </div>
          )}

          {/* Step 2: Workflow Details */}
          {currentStep === "details" && (
            <div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                Workflow Details
              </h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Workflow Name *
                  </label>
                  <input
                    type="text"
                    value={workflowName}
                    onChange={(e) => setWorkflowName(e.target.value)}
                    className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    placeholder="Enter workflow name"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Description
                  </label>
                  <textarea
                    value={workflowDescription}
                    onChange={(e) => setWorkflowDescription(e.target.value)}
                    className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white h-20"
                    placeholder="Describe what this workflow does"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Tags (comma-separated)
                  </label>
                  <input
                    type="text"
                    value={workflowTags}
                    onChange={(e) => setWorkflowTags(e.target.value)}
                    className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    placeholder="web-scraping, ai, automation"
                  />
                </div>
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="parallel"
                    checked={parallelExecution}
                    onChange={(e) => setParallelExecution(e.target.checked)}
                    className="mr-2"
                  />
                  <label
                    htmlFor="parallel"
                    className="text-sm text-gray-700 dark:text-gray-300"
                  >
                    Enable parallel execution (where possible)
                  </label>
                </div>
              </div>
            </div>
          )}

          {/* Step 3: Configure Steps */}
          {currentStep === "steps" && (
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                  Configure Workflow Steps
                </h3>
                <button
                  onClick={handleAddStep}
                  className="flex items-center px-3 py-1 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  <Plus className="h-4 w-4 mr-1" />
                  Add Step
                </button>
              </div>

              <div className="space-y-4">
                {steps.map((step, index) => (
                  <div
                    key={index}
                    className="border border-gray-200 dark:border-gray-700 rounded-lg p-4"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-sm font-medium text-gray-900 dark:text-white">
                        Step {index + 1}
                      </span>
                      {steps.length > 1 && (
                        <button
                          onClick={() => handleRemoveStep(index)}
                          className="text-red-600 hover:text-red-800"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      )}
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                          Step Name
                        </label>
                        <input
                          type="text"
                          value={step.name || ""}
                          onChange={(e) =>
                            handleStepChange(index, "name", e.target.value)
                          }
                          className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
                          placeholder="Enter step name"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                          Step Type
                        </label>
                        <select
                          value={step.step_type || "url_input"}
                          onChange={(e) =>
                            handleStepChange(index, "step_type", e.target.value)
                          }
                          className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
                        >
                          {STEP_TYPES.map((type) => (
                            <option key={type.value} value={type.value}>
                              {type.label}
                            </option>
                          ))}
                        </select>
                      </div>
                    </div>

                    <div className="mt-3">
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Description
                      </label>
                      <input
                        type="text"
                        value={step.description || ""}
                        onChange={(e) =>
                          handleStepChange(index, "description", e.target.value)
                        }
                        className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
                        placeholder="Describe what this step does"
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-gray-200 dark:border-gray-700">
          <div className="flex space-x-3">
            {currentStep !== "template" && (
              <button
                onClick={() => {
                  if (currentStep === "details") setCurrentStep("template");
                  else if (currentStep === "steps") setCurrentStep("details");
                }}
                className="px-4 py-2 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
              >
                Back
              </button>
            )}
            <button
              onClick={handleClose}
              className="px-4 py-2 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              Cancel
            </button>
          </div>

          <div className="flex space-x-3">
            {currentStep === "template" && selectedTemplate && (
              <button
                onClick={() => setCurrentStep("details")}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Next: Details
              </button>
            )}

            {currentStep === "details" && workflowName && (
              <button
                onClick={() => setCurrentStep("steps")}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Next: Configure Steps
              </button>
            )}

            {currentStep === "steps" && (
              <button
                onClick={handleCreate}
                disabled={!workflowName || steps.length === 0}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                Create Workflow
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
