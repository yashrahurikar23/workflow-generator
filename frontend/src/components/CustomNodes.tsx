import { Handle, Position } from "@xyflow/react";
import { AlertCircle, CheckCircle, Clock, Settings } from "lucide-react";
import React from "react";

interface CustomNodeData {
  nodeType: {
    id: string;
    name: string;
    icon: string;
    color: string;
    category: string;
  };
  config: Record<string, any>;
  status: "idle" | "running" | "success" | "error" | "pending";
  error?: string;
  selected?: boolean;
}

// AI Model Node Component
export const AIModelNode: React.FC<{
  data: CustomNodeData;
  selected?: boolean;
}> = ({ data, selected }) => {
  const { nodeType, config, status } = data;

  const getStatusIcon = () => {
    switch (status) {
      case "running":
        return <Clock className="w-4 h-4 text-blue-500 animate-spin" />;
      case "success":
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case "error":
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      default:
        return null;
    }
  };

  const getBorderColor = () => {
    if (selected) return "border-blue-500";
    switch (status) {
      case "running":
        return "border-blue-400";
      case "success":
        return "border-green-400";
      case "error":
        return "border-red-400";
      default:
        return "border-gray-300 dark:border-gray-600";
    }
  };

  return (
    <div
      className={`bg-white dark:bg-gray-800 rounded-lg shadow-md border-2 ${getBorderColor()} 
                 min-w-[240px] max-w-[300px] transition-all duration-200 hover:shadow-lg`}
    >
      {/* Node Header */}
      <div
        className="p-3 rounded-t-lg border-b border-gray-200 dark:border-gray-700"
        style={{ backgroundColor: `${nodeType.color}15` }}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-lg">🤖</span>
            <div>
              <div className="font-semibold text-sm text-gray-900 dark:text-gray-100">
                AI Model
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400">
                {config.model || "Not configured"}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-1">
            {getStatusIcon()}
            <Settings className="w-4 h-4 text-gray-400" />
          </div>
        </div>
      </div>

      {/* Node Body */}
      <div className="p-3 space-y-2">
        {/* Model Selection */}
        <div className="flex items-center justify-between">
          <span className="text-xs font-medium text-gray-600 dark:text-gray-400">
            Provider
          </span>
          <span className="text-xs text-gray-900 dark:text-gray-100 bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">
            {config.provider || "Not set"}
          </span>
        </div>

        {/* Model */}
        <div className="flex items-center justify-between">
          <span className="text-xs font-medium text-gray-600 dark:text-gray-400">
            Model
          </span>
          <span className="text-xs text-gray-900 dark:text-gray-100 bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">
            {config.model || "Not set"}
          </span>
        </div>

        {/* Temperature */}
        {config.temperature !== undefined && (
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-gray-600 dark:text-gray-400">
              Temperature
            </span>
            <span className="text-xs text-gray-900 dark:text-gray-100 bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">
              {config.temperature}
            </span>
          </div>
        )}

        {/* Prompt Preview */}
        {config.prompt && (
          <div className="mt-2 p-2 bg-gray-50 dark:bg-gray-700 rounded text-xs">
            <div className="font-medium text-gray-600 dark:text-gray-400 mb-1">
              Prompt
            </div>
            <div className="text-gray-800 dark:text-gray-200 line-clamp-2">
              {config.prompt.length > 50
                ? `${config.prompt.substring(0, 50)}...`
                : config.prompt}
            </div>
          </div>
        )}

        {/* Error Message */}
        {status === "error" && data.error && (
          <div className="mt-2 p-2 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded">
            <div className="text-xs text-red-800 dark:text-red-200">
              {data.error}
            </div>
          </div>
        )}
      </div>

      {/* Input Handle */}
      <Handle
        type="target"
        position={Position.Left}
        id="input"
        className="w-3 h-3 bg-gray-400 border-2 border-white dark:border-gray-800"
        style={{ left: -6 }}
      />

      {/* Output Handle */}
      <Handle
        type="source"
        position={Position.Right}
        id="output"
        className="w-3 h-3 bg-blue-500 border-2 border-white dark:border-gray-800"
        style={{ right: -6 }}
      />
    </div>
  );
};

// Generic Node Component
export const GenericNode: React.FC<{
  data: CustomNodeData;
  selected?: boolean;
}> = ({ data, selected }) => {
  const { nodeType, config, status } = data;

  const getStatusIcon = () => {
    switch (status) {
      case "running":
        return <Clock className="w-4 h-4 text-blue-500 animate-spin" />;
      case "success":
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case "error":
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      default:
        return null;
    }
  };

  const getBorderColor = () => {
    if (selected) return "border-blue-500";
    switch (status) {
      case "running":
        return "border-blue-400";
      case "success":
        return "border-green-400";
      case "error":
        return "border-red-400";
      default:
        return "border-gray-300 dark:border-gray-600";
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
      filter: "🔍",
      "git-branch": "🌿",
      repeat: "🔄",
      play: "▶️",
      zap: "⚡",
    };
    return iconMap[iconName] || "⚙️";
  };

  return (
    <div
      className={`bg-white dark:bg-gray-800 rounded-lg shadow-md border-2 ${getBorderColor()} 
                 min-w-[200px] max-w-[280px] transition-all duration-200 hover:shadow-lg`}
    >
      {/* Node Header */}
      <div
        className="p-3 rounded-t-lg border-b border-gray-200 dark:border-gray-700"
        style={{ backgroundColor: `${nodeType.color}15` }}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-lg">{getNodeIcon(nodeType.icon)}</span>
            <div>
              <div className="font-semibold text-sm text-gray-900 dark:text-gray-100">
                {nodeType.name}
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400 capitalize">
                {nodeType.category.replace("_", " ")}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-1">
            {getStatusIcon()}
            <Settings className="w-4 h-4 text-gray-400" />
          </div>
        </div>
      </div>

      {/* Node Body */}
      <div className="p-3">
        {/* Configuration Summary */}
        {Object.keys(config).length > 0 ? (
          <div className="space-y-1">
            {Object.entries(config)
              .slice(0, 3)
              .map(([key, value]) => (
                <div key={key} className="flex items-center justify-between">
                  <span className="text-xs font-medium text-gray-600 dark:text-gray-400 capitalize">
                    {key.replace("_", " ")}
                  </span>
                  <span className="text-xs text-gray-900 dark:text-gray-100 bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded max-w-[100px] truncate">
                    {typeof value === "object" ? "Object" : String(value)}
                  </span>
                </div>
              ))}
            {Object.keys(config).length > 3 && (
              <div className="text-xs text-gray-500 dark:text-gray-400 text-center">
                +{Object.keys(config).length - 3} more
              </div>
            )}
          </div>
        ) : (
          <div className="text-xs text-gray-500 dark:text-gray-400 text-center py-2">
            No configuration
          </div>
        )}

        {/* Error Message */}
        {status === "error" && data.error && (
          <div className="mt-2 p-2 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded">
            <div className="text-xs text-red-800 dark:text-red-200">
              {data.error}
            </div>
          </div>
        )}
      </div>

      {/* Input Handle */}
      <Handle
        type="target"
        position={Position.Left}
        id="input"
        className="w-3 h-3 bg-gray-400 border-2 border-white dark:border-gray-800"
        style={{ left: -6 }}
      />

      {/* Output Handle */}
      <Handle
        type="source"
        position={Position.Right}
        id="output"
        className="w-3 h-3 border-2 border-white dark:border-gray-800"
        style={{
          right: -6,
          backgroundColor: nodeType.color,
        }}
      />
    </div>
  );
};

// Trigger Node Component
export const TriggerNode: React.FC<{
  data: CustomNodeData;
  selected?: boolean;
}> = ({ data, selected }) => {
  const { nodeType, config, status } = data;

  const getStatusIcon = () => {
    switch (status) {
      case "running":
        return <Clock className="w-4 h-4 text-blue-500 animate-spin" />;
      case "success":
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case "error":
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      default:
        return null;
    }
  };

  const getBorderColor = () => {
    if (selected) return "border-blue-500";
    switch (status) {
      case "running":
        return "border-blue-400";
      case "success":
        return "border-green-400";
      case "error":
        return "border-red-400";
      default:
        return "border-gray-300 dark:border-gray-600";
    }
  };

  return (
    <div
      className={`bg-white dark:bg-gray-800 rounded-lg shadow-md border-2 ${getBorderColor()} 
                 min-w-[200px] max-w-[280px] transition-all duration-200 hover:shadow-lg`}
    >
      {/* Node Header */}
      <div
        className="p-3 rounded-t-lg border-b border-gray-200 dark:border-gray-700"
        style={{ backgroundColor: `${nodeType.color}15` }}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-lg">⚡</span>
            <div>
              <div className="font-semibold text-sm text-gray-900 dark:text-gray-100">
                {nodeType.name}
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400">
                Trigger
              </div>
            </div>
          </div>
          <div className="flex items-center gap-1">
            {getStatusIcon()}
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          </div>
        </div>
      </div>

      {/* Node Body */}
      <div className="p-3">
        {/* Trigger Type */}
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-medium text-gray-600 dark:text-gray-400">
            Type
          </span>
          <span className="text-xs bg-green-100 dark:bg-green-900/20 text-green-800 dark:text-green-200 px-2 py-1 rounded">
            {config.trigger_type || "Manual"}
          </span>
        </div>

        {/* Configuration */}
        {config.url && (
          <div className="mt-2 p-2 bg-gray-50 dark:bg-gray-700 rounded text-xs">
            <div className="font-medium text-gray-600 dark:text-gray-400 mb-1">
              Webhook URL
            </div>
            <div className="text-gray-800 dark:text-gray-200 truncate">
              {config.url}
            </div>
          </div>
        )}

        {config.schedule && (
          <div className="mt-2 p-2 bg-gray-50 dark:bg-gray-700 rounded text-xs">
            <div className="font-medium text-gray-600 dark:text-gray-400 mb-1">
              Schedule
            </div>
            <div className="text-gray-800 dark:text-gray-200">
              {config.schedule}
            </div>
          </div>
        )}
      </div>

      {/* Output Handle (No input for triggers) */}
      <Handle
        type="source"
        position={Position.Right}
        id="output"
        className="w-3 h-3 border-2 border-white dark:border-gray-800"
        style={{
          right: -6,
          backgroundColor: nodeType.color,
        }}
      />
    </div>
  );
};

// Node type registry for custom components
export const nodeTypes = {
  ai_model: AIModelNode,
  trigger: TriggerNode,
  webhook: TriggerNode,
  scheduler: TriggerNode,
  default: GenericNode,
};

export default nodeTypes;
