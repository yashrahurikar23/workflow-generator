import { ChevronDown, ChevronRight, Plus, Search } from "lucide-react";
import React, { useMemo, useState } from "react";

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
  is_template: boolean;
  tags: string[];
  config_fields: ConfigField[];
  inputs: any[];
  outputs: any[];
}

interface NodeCategory {
  id: string;
  name: string;
  description: string;
  icon: string;
  color: string;
  order: number;
}

interface NodePaletteProps {
  categories: NodeCategory[];
  nodeTypes: NodeType[];
  onNodeDrag: (nodeType: NodeType) => void;
  onNodeClick: (nodeType: NodeType) => void;
}

const NodePalette: React.FC<NodePaletteProps> = ({
  categories,
  nodeTypes,
  onNodeDrag,
  onNodeClick,
}) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(
    new Set(["ai_models", "triggers"]) // Expand AI Models and Triggers by default
  );

  // Filter and group nodes by category
  const filteredNodesGrouped = useMemo(() => {
    const filtered = nodeTypes.filter(
      (node) =>
        node.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        node.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        node.tags.some((tag) =>
          tag.toLowerCase().includes(searchTerm.toLowerCase())
        )
    );

    const grouped = categories.reduce((acc, category) => {
      acc[category.id] = {
        category,
        nodes: filtered.filter((node) => node.category === category.id),
      };
      return acc;
    }, {} as Record<string, { category: NodeCategory; nodes: NodeType[] }>);

    return grouped;
  }, [nodeTypes, categories, searchTerm]);

  const toggleCategory = (categoryId: string) => {
    const newExpanded = new Set(expandedCategories);
    if (newExpanded.has(categoryId)) {
      newExpanded.delete(categoryId);
    } else {
      newExpanded.add(categoryId);
    }
    setExpandedCategories(newExpanded);
  };

  const handleDragStart = (event: React.DragEvent, nodeType: NodeType) => {
    event.dataTransfer.setData(
      "application/reactflow",
      JSON.stringify(nodeType)
    );
    event.dataTransfer.effectAllowed = "move";
    onNodeDrag(nodeType);
  };

  const getIconForCategory = (iconName: string) => {
    // Map icon names to emoji or Lucide icons
    const iconMap: Record<string, string> = {
      brain: "🧠",
      database: "💾",
      zap: "⚡",
      plug: "🔌",
      "git-branch": "🌿",
      mail: "📧",
      cog: "⚙️",
      shield: "🛡️",
    };
    return iconMap[iconName] || "📦";
  };

  const getIconForNode = (iconName: string) => {
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
    };
    return iconMap[iconName] || "⚙️";
  };

  return (
    <div className="w-80 h-full bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-3">
          Node Library
        </h2>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <input
            type="text"
            placeholder="Search nodes..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg 
                     bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100
                     focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
      </div>

      {/* Node Categories */}
      <div className="flex-1 overflow-y-auto">
        {Object.entries(filteredNodesGrouped)
          .sort(([, a], [, b]) => a.category.order - b.category.order)
          .map(([categoryId, { category, nodes }]) => {
            if (nodes.length === 0 && searchTerm) return null;

            const isExpanded = expandedCategories.has(categoryId);
            const categoryIcon = getIconForCategory(category.icon);

            return (
              <div
                key={categoryId}
                className="border-b border-gray-200 dark:border-gray-700"
              >
                {/* Category Header */}
                <button
                  onClick={() => toggleCategory(categoryId)}
                  className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-lg">{categoryIcon}</span>
                    <div className="text-left">
                      <div className="font-medium text-gray-900 dark:text-gray-100 text-sm">
                        {category.name}
                      </div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">
                        {nodes.length} node{nodes.length !== 1 ? "s" : ""}
                      </div>
                    </div>
                  </div>
                  {isExpanded ? (
                    <ChevronDown className="w-4 h-4 text-gray-400" />
                  ) : (
                    <ChevronRight className="w-4 h-4 text-gray-400" />
                  )}
                </button>

                {/* Category Nodes */}
                {isExpanded && (
                  <div className="pb-2">
                    {nodes.map((nodeType) => {
                      const nodeIcon = getIconForNode(nodeType.icon);

                      return (
                        <div
                          key={nodeType.id}
                          draggable
                          onDragStart={(e) => handleDragStart(e, nodeType)}
                          onClick={() => onNodeClick(nodeType)}
                          className="mx-2 mb-2 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700
                                   hover:bg-gray-100 dark:hover:bg-gray-700 hover:border-gray-300 dark:hover:border-gray-600
                                   cursor-move transition-all duration-200 group"
                          style={{
                            borderLeftColor: nodeType.color,
                            borderLeftWidth: "3px",
                          }}
                        >
                          <div className="flex items-start gap-3">
                            <span className="text-lg flex-shrink-0">
                              {nodeIcon}
                            </span>
                            <div className="flex-1 min-w-0">
                              <div className="font-medium text-sm text-gray-900 dark:text-gray-100 truncate">
                                {nodeType.name}
                              </div>
                              <div className="text-xs text-gray-500 dark:text-gray-400 mt-1 line-clamp-2">
                                {nodeType.description}
                              </div>

                              {/* Tags */}
                              {nodeType.tags.length > 0 && (
                                <div className="flex flex-wrap gap-1 mt-2">
                                  {nodeType.tags.slice(0, 2).map((tag) => (
                                    <span
                                      key={tag}
                                      className="px-2 py-1 text-xs bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300 rounded"
                                    >
                                      {tag}
                                    </span>
                                  ))}
                                  {nodeType.tags.length > 2 && (
                                    <span className="text-xs text-gray-400">
                                      +{nodeType.tags.length - 2}
                                    </span>
                                  )}
                                </div>
                              )}

                              {/* Template Badge */}
                              {nodeType.is_template && (
                                <div className="mt-2">
                                  <span className="inline-flex items-center px-2 py-1 text-xs bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded">
                                    Template
                                  </span>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            );
          })}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-700">
        <button
          className="w-full flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium 
                         text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20 rounded-lg
                         hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors"
        >
          <Plus className="w-4 h-4" />
          Create Custom Node
        </button>
      </div>
    </div>
  );
};

export default NodePalette;
