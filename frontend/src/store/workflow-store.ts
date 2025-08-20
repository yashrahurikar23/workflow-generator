import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'

export interface WorkflowStep {
  id: string
  name: string
  type: 'api_call' | 'data_transform' | 'email' | 'database' | 'condition' | 'loop'
  config: Record<string, any>
  position?: { x: number; y: number }
}

export interface Workflow {
  id?: string
  name: string
  description: string
  steps: WorkflowStep[]
  tags: string[]
  parallel_execution: boolean
  timeout_minutes: number
  status?: 'draft' | 'active' | 'inactive'
  created_at?: string
  updated_at?: string
}

interface WorkflowStore {
  // Current workflow being edited
  currentWorkflow: Workflow | null
  
  // List of all workflows
  workflows: Workflow[]
  
  // UI state
  isLoading: boolean
  error: string | null
  
  // Actions
  setCurrentWorkflow: (workflow: Workflow | null) => void
  updateCurrentWorkflow: (updates: Partial<Workflow>) => void
  addStep: (step: WorkflowStep) => void
  updateStep: (stepId: string, updates: Partial<WorkflowStep>) => void
  removeStep: (stepId: string) => void
  reorderSteps: (steps: WorkflowStep[]) => void
  
  // Workflow management
  setWorkflows: (workflows: Workflow[]) => void
  addWorkflow: (workflow: Workflow) => void
  updateWorkflow: (id: string, updates: Partial<Workflow>) => void
  removeWorkflow: (id: string) => void
  
  // API integration
  saveWorkflow: () => Promise<void>
  loadWorkflows: () => Promise<void>
  deleteWorkflow: (id: string) => Promise<void>
  
  // Utility
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  resetStore: () => void
}

const initialState = {
  currentWorkflow: null,
  workflows: [],
  isLoading: false,
  error: null,
}

export const useWorkflowStore = create<WorkflowStore>()(
  devtools(
    persist(
      (set, get) => ({
        ...initialState,
        
        // Current workflow actions
        setCurrentWorkflow: (workflow) => 
          set({ currentWorkflow: workflow }, false, 'setCurrentWorkflow'),
          
        updateCurrentWorkflow: (updates) => 
          set((state) => ({
            currentWorkflow: state.currentWorkflow 
              ? { ...state.currentWorkflow, ...updates }
              : null
          }), false, 'updateCurrentWorkflow'),
          
        addStep: (step) => 
          set((state) => ({
            currentWorkflow: state.currentWorkflow 
              ? {
                  ...state.currentWorkflow,
                  steps: [...state.currentWorkflow.steps, step]
                }
              : null
          }), false, 'addStep'),
          
        updateStep: (stepId, updates) => 
          set((state) => ({
            currentWorkflow: state.currentWorkflow 
              ? {
                  ...state.currentWorkflow,
                  steps: state.currentWorkflow.steps.map(step =>
                    step.id === stepId ? { ...step, ...updates } : step
                  )
                }
              : null
          }), false, 'updateStep'),
          
        removeStep: (stepId) => 
          set((state) => ({
            currentWorkflow: state.currentWorkflow 
              ? {
                  ...state.currentWorkflow,
                  steps: state.currentWorkflow.steps.filter(step => step.id !== stepId)
                }
              : null
          }), false, 'removeStep'),
          
        reorderSteps: (steps) => 
          set((state) => ({
            currentWorkflow: state.currentWorkflow 
              ? { ...state.currentWorkflow, steps }
              : null
          }), false, 'reorderSteps'),
          
        // Workflow list management
        setWorkflows: (workflows) => 
          set({ workflows }, false, 'setWorkflows'),
          
        addWorkflow: (workflow) => 
          set((state) => ({
            workflows: [...state.workflows, workflow]
          }), false, 'addWorkflow'),
          
        updateWorkflow: (id, updates) => 
          set((state) => ({
            workflows: state.workflows.map(workflow =>
              workflow.id === id ? { ...workflow, ...updates } : workflow
            )
          }), false, 'updateWorkflow'),
          
        removeWorkflow: (id) => 
          set((state) => ({
            workflows: state.workflows.filter(workflow => workflow.id !== id)
          }), false, 'removeWorkflow'),
          
        // API integration
        saveWorkflow: async () => {
          const { currentWorkflow } = get()
          if (!currentWorkflow) return
          
          set({ isLoading: true, error: null })
          
          try {
            // TODO: Implement full API integration - type mapping needed
            console.log('Saving workflow:', currentWorkflow)
            
            // Simulate API delay for now
            await new Promise(resolve => setTimeout(resolve, 1000))
            
            // Update the workflows list
            if (currentWorkflow.id) {
              get().updateWorkflow(currentWorkflow.id, currentWorkflow)
            } else {
              const newWorkflow = { ...currentWorkflow, id: Date.now().toString() }
              get().addWorkflow(newWorkflow)
              get().setCurrentWorkflow(newWorkflow)
            }
          } catch (error) {
            set({ error: error instanceof Error ? error.message : 'Failed to save workflow' })
          } finally {
            set({ isLoading: false })
          }
        },
        
        loadWorkflows: async () => {
          set({ isLoading: true, error: null })
          
          try {
            // TODO: Implement API call to load workflows
            console.log('Loading workflows...')
            
            // Simulate API delay
            await new Promise(resolve => setTimeout(resolve, 1000))
            
            // Mock data for now
            const mockWorkflows: Workflow[] = [
              {
                id: '1',
                name: 'Sample Workflow',
                description: 'A sample workflow for demonstration',
                steps: [],
                tags: ['sample'],
                parallel_execution: false,
                timeout_minutes: 30,
                status: 'draft'
              }
            ]
            
            set({ workflows: mockWorkflows })
          } catch (error) {
            set({ error: error instanceof Error ? error.message : 'Failed to load workflows' })
          } finally {
            set({ isLoading: false })
          }
        },
        
        deleteWorkflow: async (id) => {
          set({ isLoading: true, error: null })
          
          try {
            // TODO: Implement API call to delete workflow
            console.log('Deleting workflow:', id)
            
            // Simulate API delay
            await new Promise(resolve => setTimeout(resolve, 500))
            
            get().removeWorkflow(id)
            
            // Clear current workflow if it's the one being deleted
            const { currentWorkflow } = get()
            if (currentWorkflow?.id === id) {
              set({ currentWorkflow: null })
            }
          } catch (error) {
            set({ error: error instanceof Error ? error.message : 'Failed to delete workflow' })
          } finally {
            set({ isLoading: false })
          }
        },
        
        // Utility
        setLoading: (loading) => set({ isLoading: loading }),
        setError: (error) => set({ error }),
        resetStore: () => set(initialState, false, 'resetStore'),
      }),
      {
        name: 'workflow-store',
        partialize: (state) => ({
          currentWorkflow: state.currentWorkflow,
          workflows: state.workflows,
        }),
      }
    ),
    { name: 'workflow-store' }
  )
)
