import { X } from "lucide-react";
import React, { useState } from "react";

interface CreateWorkflowModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreateWorkflow: (workflowData: {
    name: string;
    description: string;
  }) => Promise<void>;
}

export function CreateWorkflowModal({
  isOpen,
  onClose,
  onCreateWorkflow,
}: CreateWorkflowModalProps) {
  const [workflowName, setWorkflowName] = useState("");
  const [description, setDescription] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!workflowName.trim()) {
      setError("Workflow name is required");
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      await onCreateWorkflow({
        name: workflowName.trim(),
        description:
          description.trim() || `A new workflow: ${workflowName.trim()}`,
      });

      setWorkflowName("");
      setDescription("");
      onClose();
    } catch (err) {
      setError("Failed to create workflow. Please try again.");
      console.error("Error creating workflow:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    if (!isSubmitting) {
      setWorkflowName("");
      setDescription("");
      setError(null);
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      onClick={(e) => {
        if (e.target === e.currentTarget) handleClose();
      }}
    >
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-md mx-4 p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Create New Workflow
          </h2>
          <button
            onClick={handleClose}
            disabled={isSubmitting}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 disabled:opacity-50"
          >
            <X size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label
              htmlFor="workflowName"
              className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
            >
              Workflow Name *
            </label>
            <input
              type="text"
              id="workflowName"
              value={workflowName}
              onChange={(e) => setWorkflowName(e.target.value)}
              placeholder="Enter workflow name..."
              disabled={isSubmitting}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white disabled:opacity-50"
              autoFocus
              maxLength={100}
            />
          </div>

          <div>
            <label
              htmlFor="workflowDescription"
              className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
            >
              Description (Optional)
            </label>
            <textarea
              id="workflowDescription"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe what this workflow will do..."
              disabled={isSubmitting}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white disabled:opacity-50 resize-none"
              maxLength={500}
            />
          </div>

          {error && (
            <div className="text-red-600 dark:text-red-400 text-sm bg-red-50 dark:bg-red-900/20 p-3 rounded-md">
              {error}
            </div>
          )}

          <div className="text-sm text-gray-600 dark:text-gray-400 bg-blue-50 dark:bg-blue-900/20 p-3 rounded-md">
            💡 After creating the workflow, you can use the chat panel to build
            it step by step.
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={handleClose}
              disabled={isSubmitting}
              className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting || !workflowName.trim()}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
            >
              {isSubmitting ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2"></div>
                  Creating...
                </>
              ) : (
                "Create Workflow"
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default CreateWorkflowModal;
