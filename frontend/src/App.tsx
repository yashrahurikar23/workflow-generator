import React from "react";
import { ThemeProvider } from "./components/theme-provider";
import { ModeToggle } from "./components/mode-toggle";
import { useWorkflowStore } from "./store/workflow-store";
import { Button } from "./components/ui/button";
import { Plus, Play, Save } from "lucide-react";

function App() {
  const {
    workflows,
    currentWorkflow,
    addWorkflow,
    setCurrentWorkflow,
    saveWorkflow,
    isLoading,
    error,
  } = useWorkflowStore();

  const handleCreateWorkflow = () => {
    const name = prompt("Enter workflow name:");
    if (name) {
      const newWorkflow = {
        id: Date.now().toString(),
        name,
        description: "",
        steps: [],
        tags: [],
        parallel_execution: false,
        timeout_minutes: 30,
        status: "draft" as const,
      };
      addWorkflow(newWorkflow);
      setCurrentWorkflow(newWorkflow);
    }
  };

  const handleSaveWorkflow = async () => {
    if (currentWorkflow) {
      await saveWorkflow();
    }
  };

  const handleExecuteWorkflow = () => {
    if (currentWorkflow) {
      // TODO: Implement workflow execution
      console.log("Executing workflow:", currentWorkflow.id);
    }
  };

  return (
    <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
      <div className="min-h-screen bg-background text-foreground">
        {/* Header */}
        <header className="border-b border-border">
          <div className="container mx-auto px-4 py-4 flex items-center justify-between">
            <h1 className="text-2xl font-bold">Workflow Generator</h1>
            <div className="flex items-center gap-4">
              <Button
                onClick={handleCreateWorkflow}
                className="flex items-center gap-2"
                disabled={isLoading}
              >
                <Plus className="h-4 w-4" />
                New Workflow
              </Button>
              <Button
                onClick={handleSaveWorkflow}
                variant="outline"
                className="flex items-center gap-2"
                disabled={!currentWorkflow || isLoading}
              >
                <Save className="h-4 w-4" />
                Save
              </Button>
              <Button
                onClick={handleExecuteWorkflow}
                variant="outline"
                className="flex items-center gap-2"
                disabled={!currentWorkflow || isLoading}
              >
                <Play className="h-4 w-4" />
                Execute
              </Button>
              <ModeToggle />
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="container mx-auto px-4 py-8">
          {error && (
            <div className="bg-destructive/10 border border-destructive/20 text-destructive px-4 py-3 rounded-md mb-6">
              <p className="font-medium">Error</p>
              <p className="text-sm mt-1">{error}</p>
            </div>
          )}

          {isLoading && (
            <div className="text-center py-8">
              <p className="text-muted-foreground">Loading...</p>
            </div>
          )}

          {currentWorkflow ? (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold">
                  {currentWorkflow.name}
                </h2>
                <span className="text-sm text-muted-foreground">
                  Status: {currentWorkflow.status}
                </span>
              </div>

              <div className="bg-card border border-border rounded-lg p-6">
                <h3 className="text-lg font-medium mb-4">
                  Workflow Configuration
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">
                      Description
                    </label>
                    <p className="mt-1">
                      {currentWorkflow.description || "No description"}
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">
                      Steps
                    </label>
                    <p className="mt-1">
                      {currentWorkflow.steps?.length || 0} steps configured
                    </p>
                  </div>
                </div>
              </div>

              {/* Workflow Designer Placeholder */}
              <div className="bg-card border border-border rounded-lg p-6 min-h-[400px] flex items-center justify-center">
                <div className="text-center">
                  <h3 className="text-lg font-medium mb-2">
                    Workflow Designer
                  </h3>
                  <p className="text-muted-foreground mb-4">
                    Visual workflow editor will be implemented here
                  </p>
                  <Button variant="outline">Add Step</Button>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-12">
              <h2 className="text-xl font-semibold mb-4">
                Welcome to Workflow Generator
              </h2>
              <p className="text-muted-foreground mb-6">
                Create your first workflow to get started
              </p>
              <Button
                onClick={handleCreateWorkflow}
                className="flex items-center gap-2 mx-auto"
              >
                <Plus className="h-4 w-4" />
                Create New Workflow
              </Button>
            </div>
          )}

          {/* Workflows List */}
          {workflows.length > 0 && (
            <div className="mt-12">
              <h3 className="text-lg font-semibold mb-4">Recent Workflows</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {workflows.map((workflow) => (
                  <div
                    key={workflow.id}
                    className="bg-card border border-border rounded-lg p-4 hover:bg-accent/50 transition-colors cursor-pointer"
                    onClick={() => setCurrentWorkflow(workflow)}
                  >
                    <h4 className="font-medium mb-2">{workflow.name}</h4>
                    <p className="text-sm text-muted-foreground mb-2">
                      {workflow.description || "No description"}
                    </p>
                    <div className="flex items-center justify-between text-xs text-muted-foreground">
                      <span>Status: {workflow.status}</span>
                      <span>{workflow.steps?.length || 0} steps</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </main>
      </div>
    </ThemeProvider>
  );
}

export default App;
