import { Play, RotateCcw, Save, Settings, X } from "lucide-react";
import React, { useEffect, useState } from "react";

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

interface NodeType {
  id: string;
  name: string;
  description: string;
  category: string;
  icon: string;
  color: string;
  config_fields: ConfigField[];
  inputs: any[];
  outputs: any[];
}

interface SelectedNode {
  node_id: string;
  node_type_id: string;
  name: string;
  config: Record<string, any>;
  position: { x: number; y: number };
}

interface NodeConfigPanelProps {
  selectedNode: SelectedNode | null;
  nodeType: NodeType | null;
  onConfigChange: (nodeId: string, config: Record<string, any>) => void;
  onNodeRename: (nodeId: string, name: string) => void;
  onClose: () => void;
  onExecuteNode?: (nodeId: string) => void;
}

const NodeConfigPanel: React.FC<NodeConfigPanelProps> = ({
  selectedNode,
  nodeType,
  onConfigChange,
  onNodeRename,
  onClose,
  onExecuteNode,
}) => {
  const [config, setConfig] = useState<Record<string, any>>({});
  const [nodeName, setNodeName] = useState("");
  const [activeTab, setActiveTab] = useState<"config" | "docs" | "testing">(
    "config"
  );
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

  useEffect(() => {
    if (selectedNode && nodeType) {
      setConfig(selectedNode.config || {});
      setNodeName(selectedNode.name || nodeType.name);
      setHasUnsavedChanges(false);
    }
  }, [selectedNode, nodeType]);

  if (!selectedNode || !nodeType) {
    return null;
  }

  const handleConfigFieldChange = (fieldKey: string, value: any) => {
    const newConfig = { ...config, [fieldKey]: value };
    setConfig(newConfig);
    setHasUnsavedChanges(true);
  };

  const handleSaveChanges = () => {
    onConfigChange(selectedNode.node_id, config);
    if (nodeName !== selectedNode.name) {
      onNodeRename(selectedNode.node_id, nodeName);
    }
    setHasUnsavedChanges(false);
  };

  const handleResetChanges = () => {
    setConfig(selectedNode.config || {});
    setNodeName(selectedNode.name || nodeType.name);
    setHasUnsavedChanges(false);
  };

  const renderConfigField = (field: ConfigField) => {
    const value = config[field.key] ?? field.default_value;

    switch (field.type) {
      case "string":
        return (
          <input
            type="text"
            value={value || ""}
            onChange={(e) => handleConfigFieldChange(field.key, e.target.value)}
            placeholder={field.description}
            className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg
                     bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100
                     focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        );

      case "textarea":
        return (
          <textarea
            value={value || ""}
            onChange={(e) => handleConfigFieldChange(field.key, e.target.value)}
            placeholder={field.description}
            rows={4}
            className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg
                     bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100
                     focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
          />
        );

      case "number":
        return (
          <input
            type="number"
            value={value || ""}
            onChange={(e) =>
              handleConfigFieldChange(
                field.key,
                parseFloat(e.target.value) || 0
              )
            }
            min={field.min}
            max={field.max}
            step={field.step}
            className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg
                     bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100
                     focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        );

      case "slider":
        return (
          <div className="space-y-2">
            <input
              type="range"
              value={value || field.default_value || 0}
              onChange={(e) =>
                handleConfigFieldChange(field.key, parseFloat(e.target.value))
              }
              min={field.min || 0}
              max={field.max || 100}
              step={field.step || 1}
              className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer
                       slider:bg-blue-500"
            />
            <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400">
              <span>{field.min || 0}</span>
              <span className="font-medium">
                {value || field.default_value || 0}
              </span>
              <span>{field.max || 100}</span>
            </div>
          </div>
        );

      case "boolean":
        return (
          <label className="flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={value || false}
              onChange={(e) =>
                handleConfigFieldChange(field.key, e.target.checked)
              }
              className="w-4 h-4 text-blue-600 bg-gray-100 dark:bg-gray-700 border-gray-300 dark:border-gray-600 rounded
                       focus:ring-blue-500 focus:ring-2"
            />
            <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
              {field.description || "Enable this option"}
            </span>
          </label>
        );

      case "select":
        return (
          <select
            value={value || ""}
            onChange={(e) => handleConfigFieldChange(field.key, e.target.value)}
            className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg
                     bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100
                     focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">Select an option</option>
            {field.options?.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        );

      case "json":
        return (
          <textarea
            value={
              typeof value === "object"
                ? JSON.stringify(value, null, 2)
                : value || ""
            }
            onChange={(e) => {
              try {
                const parsed = JSON.parse(e.target.value);
                handleConfigFieldChange(field.key, parsed);
              } catch {
                handleConfigFieldChange(field.key, e.target.value);
              }
            }}
            placeholder='{"key": "value"}'
            rows={6}
            className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg
                     bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 font-mono
                     focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
          />
        );

      default:
        return (
          <div className="text-sm text-gray-500 dark:text-gray-400">
            Unsupported field type: {field.type}
          </div>
        );
    }
  };

  const getNodeIcon = (iconName: string) => {
    const iconMap: Record<string, string> = {
      brain: "🤖",
      "message-square": "💬",
      image: "🖼️",
      calendar: "📅",
      webhook: "🔗",
      mail: "📧",
      database: "🗄️",
      "file-text": "📄",
    };
    return iconMap[iconName] || "⚙️";
  };

  return (
    <div className="w-96 h-full bg-white dark:bg-gray-900 border-l border-gray-200 dark:border-gray-700 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-3">
            <span className="text-xl">{getNodeIcon(nodeType.icon)}</span>
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-gray-100">
                {nodeType.name}
              </h3>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {nodeType.category.replace("_", " ")}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          >
            <X className="w-4 h-4 text-gray-500 dark:text-gray-400" />
          </button>
        </div>

        {/* Node Name Input */}
        <div className="space-y-2">
          <label className="text-xs font-medium text-gray-700 dark:text-gray-300">
            Node Name
          </label>
          <input
            type="text"
            value={nodeName}
            onChange={(e) => {
              setNodeName(e.target.value);
              setHasUnsavedChanges(true);
            }}
            className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg
                     bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100
                     focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200 dark:border-gray-700">
        {["config", "docs", "testing"].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab as any)}
            className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
              activeTab === tab
                ? "text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400 bg-blue-50 dark:bg-blue-900/10"
                : "text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800"
            }`}
          >
            {tab === "config" && <Settings className="w-4 h-4 inline mr-2" />}
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto">
        {activeTab === "config" && (
          <div className="p-4 space-y-6">
            {nodeType.config_fields.length === 0 ? (
              <div className="text-center text-gray-500 dark:text-gray-400 py-8">
                <Settings className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p>No configuration required</p>
              </div>
            ) : (
              nodeType.config_fields.map((field) => (
                <div key={field.key} className="space-y-2">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    {field.label}
                    {field.required && (
                      <span className="text-red-500 ml-1">*</span>
                    )}
                  </label>
                  {field.description && (
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {field.description}
                    </p>
                  )}
                  {renderConfigField(field)}
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === "docs" && (
          <div className="p-4 space-y-4">
            <div>
              <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-2">
                Description
              </h4>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {nodeType.description}
              </p>
            </div>

            <div>
              <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-2">
                Inputs
              </h4>
              {nodeType.inputs.length === 0 ? (
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  No inputs
                </p>
              ) : (
                <div className="space-y-2">
                  {nodeType.inputs.map((input: any) => (
                    <div
                      key={input.id}
                      className="p-2 bg-gray-50 dark:bg-gray-800 rounded"
                    >
                      <div className="font-medium text-sm">{input.label}</div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">
                        Type: {input.type}{" "}
                        {input.required ? "(required)" : "(optional)"}
                      </div>
                      {input.description && (
                        <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                          {input.description}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div>
              <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-2">
                Outputs
              </h4>
              {nodeType.outputs.length === 0 ? (
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  No outputs
                </p>
              ) : (
                <div className="space-y-2">
                  {nodeType.outputs.map((output: any) => (
                    <div
                      key={output.id}
                      className="p-2 bg-gray-50 dark:bg-gray-800 rounded"
                    >
                      <div className="font-medium text-sm">{output.label}</div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">
                        Type: {output.type}
                      </div>
                      {output.description && (
                        <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                          {output.description}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === "testing" && (
          <div className="p-4 space-y-4">
            <div>
              <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-2">
                Test Node
              </h4>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                Execute this node with current configuration to test its
                functionality.
              </p>

              <button
                onClick={() => onExecuteNode?.(selectedNode.node_id)}
                disabled={!onExecuteNode}
                className="w-full flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium 
                         text-white bg-green-600 rounded-lg hover:bg-green-700 disabled:bg-gray-400 
                         disabled:cursor-not-allowed transition-colors"
              >
                <Play className="w-4 h-4" />
                Execute Node
              </button>
            </div>

            <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <h5 className="font-medium text-sm mb-2">
                Current Configuration
              </h5>
              <pre className="text-xs text-gray-600 dark:text-gray-400 overflow-auto">
                {JSON.stringify(config, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      {hasUnsavedChanges && (
        <div className="p-4 border-t border-gray-200 dark:border-gray-700 bg-yellow-50 dark:bg-yellow-900/20">
          <div className="text-sm text-yellow-800 dark:text-yellow-200 mb-3">
            You have unsaved changes
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleSaveChanges}
              className="flex-1 flex items-center justify-center gap-2 px-3 py-2 text-sm font-medium 
                       text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Save className="w-4 h-4" />
              Save
            </button>
            <button
              onClick={handleResetChanges}
              className="flex items-center justify-center gap-2 px-3 py-2 text-sm font-medium 
                       text-gray-600 dark:text-gray-400 bg-gray-100 dark:bg-gray-800 rounded-lg 
                       hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
            >
              <RotateCcw className="w-4 h-4" />
              Reset
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default NodeConfigPanel;
