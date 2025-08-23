import { ThemeProvider } from "./components/theme-provider";
import { WorkflowLibrary } from "./components/WorkflowLibrary";

function App() {
  return (
    <ThemeProvider defaultTheme="light" storageKey="workflow-generator-theme">
      <div className="min-h-screen bg-gray-50">
        <WorkflowLibrary />
      </div>
    </ThemeProvider>
  );
}

export default App;
