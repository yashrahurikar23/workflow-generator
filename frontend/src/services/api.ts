import axios from 'axios'

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000'

// Create axios instance with default config
const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
})

// Request interceptor for adding auth token (if needed in future)
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('auth_token')
      // Redirect to login if needed
    }
    return Promise.reject(error)
  }
)

// Workflow API types
export interface WorkflowCreateRequest {
  name: string
  description?: string
  steps: WorkflowStepConfig[]
  tags: string[]
  parallel_execution: boolean
  timeout_minutes: number
}

export interface WorkflowUpdateRequest {
  name?: string
  description?: string
  steps?: WorkflowStepConfig[]
  tags?: string[]
  parallel_execution?: boolean
  timeout_minutes?: number
}

export interface WorkflowStepConfig {
  step_id: string
  name: string
  step_type: string
  description?: string
  config: Record<string, any>
  depends_on: string[]
  condition?: Record<string, any>
}

export interface WorkflowResponse {
  workflow_id: string
  name: string
  description: string
  steps: WorkflowStepConfig[]
  tags: string[]
  parallel_execution: boolean
  timeout_minutes: number
  status: string
  version: number
  generated_by_llm: boolean
  generation_prompt?: string
  created_at: string
  updated_at: string
  created_by?: string
  execution_count: number
}

export interface WorkflowListResponse {
  workflows: WorkflowResponse[]
  total: number
  page: number
  size: number
}

export interface WorkflowExecuteRequest {
  input_data: Record<string, any>
}

export interface WorkflowExecutionResponse {
  execution_id: string
  workflow_id: string
  status: string
  current_step?: string
  completed_steps: string[]
  failed_steps: string[]
  execution_context: Record<string, any>
  started_at: string
  completed_at?: string
  error_message?: string
  error_step?: string
}

export interface WorkflowGenerateRequest {
  prompt: string
  additional_context?: string
  preferred_steps?: string[]
}

// Workflow API functions
export const workflowApi = {
  // Get all workflows
  async getWorkflows(skip = 0, limit = 50): Promise<WorkflowListResponse> {
    const response = await api.get('/workflows/', {
      params: { skip, limit }
    })
    return response.data
  },

  // Get a specific workflow
  async getWorkflow(workflowId: string): Promise<WorkflowResponse> {
    const response = await api.get(`/workflows/${workflowId}`)
    return response.data
  },

  // Create a new workflow
  async createWorkflow(workflow: WorkflowCreateRequest): Promise<WorkflowResponse> {
    const response = await api.post('/workflows/', workflow)
    return response.data
  },

  // Update an existing workflow
  async updateWorkflow(workflowId: string, updates: WorkflowUpdateRequest): Promise<WorkflowResponse> {
    const response = await api.put(`/workflows/${workflowId}`, updates)
    return response.data
  },

  // Delete a workflow
  async deleteWorkflow(workflowId: string): Promise<void> {
    await api.delete(`/workflows/${workflowId}`)
  },

  // Execute a workflow
  async executeWorkflow(workflowId: string, executeRequest: WorkflowExecuteRequest): Promise<WorkflowExecutionResponse> {
    const response = await api.post(`/workflows/${workflowId}/execute`, executeRequest)
    return response.data
  },

  // Get workflow execution
  async getExecution(executionId: string): Promise<WorkflowExecutionResponse> {
    const response = await api.get(`/workflows/executions/${executionId}`)
    return response.data
  },

  // Get executions for a workflow
  async getWorkflowExecutions(workflowId: string, skip = 0, limit = 50): Promise<{ executions: WorkflowExecutionResponse[], total: number }> {
    const response = await api.get(`/workflows/${workflowId}/executions`, {
      params: { skip, limit }
    })
    return response.data
  },

  // Generate workflow with AI
  async generateWorkflow(generateRequest: WorkflowGenerateRequest): Promise<WorkflowResponse> {
    const response = await api.post('/workflows/generate', generateRequest)
    return response.data
  },
}

// Error handling utility
export class ApiError extends Error {
  constructor(
    message: string,
    public status?: number,
    public data?: any
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

// Helper function to handle API errors
export const handleApiError = (error: any): ApiError => {
  if (axios.isAxiosError(error)) {
    const status = error.response?.status
    const message = error.response?.data?.message || error.response?.data?.detail || error.message
    const data = error.response?.data
    
    return new ApiError(message, status, data)
  }
  
  return new ApiError(error.message || 'An unknown error occurred')
}

export default api
