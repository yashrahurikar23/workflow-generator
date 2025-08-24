// API Configuration for Workflow Generator Frontend

// Backend URL - deployed on Render
const PRODUCTION_API_URL = "https://workflow-backend.onrender.com";

// Determine which API URL to use based on environment
// Use environment variable or default to production URL
export const API_BASE_URL = process.env.REACT_APP_API_URL || PRODUCTION_API_URL;

// API endpoints
export const API_ENDPOINTS = {
  health: `${API_BASE_URL}/health`,
  workflows: `${API_BASE_URL}/api/v1/workflows/`,
  workflowById: (id: string) => `${API_BASE_URL}/api/v1/workflows/${id}`,
  updateWorkflow: (id: string) => `${API_BASE_URL}/api/v1/workflows/${id}`,
  visualWorkflows: `${API_BASE_URL}/api/v1/visual-workflows/`,
  updateVisualWorkflow: (id: string) => `${API_BASE_URL}/api/v1/visual-workflows/${id}`,
  workflowChat: (id: string) => `${API_BASE_URL}/api/v1/workflows/${id}/chat`,
  executeWorkflow: (id: string) => `${API_BASE_URL}/api/v1/workflows/${id}/execute`,
  chatThreads: `${API_BASE_URL}/api/v1/chat/threads`,
  chatInThread: (threadId: string) => `${API_BASE_URL}/api/v1/chat/threads/${threadId}/chat`,
  threadMessages: (threadId: string) => `${API_BASE_URL}/api/v1/chat/threads/${threadId}/messages`,
  // Add more endpoints as needed
};

// Default headers for API requests
export const DEFAULT_HEADERS = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
};

// Helper function to create API fetch with default settings
export const apiRequest = async (
  endpoint: string, 
  options: RequestInit = {}
): Promise<Response> => {
  const config: RequestInit = {
    headers: {
      ...DEFAULT_HEADERS,
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(endpoint, config);
    return response;
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
};

// Helper functions for common API operations
export const apiGet = (endpoint: string) => 
  apiRequest(endpoint, { method: 'GET' });

export const apiPost = (endpoint: string, data: any) => 
  apiRequest(endpoint, {
    method: 'POST',
    body: JSON.stringify(data),
  });

export const apiPut = (endpoint: string, data: any) => 
  apiRequest(endpoint, {
    method: 'PUT',
    body: JSON.stringify(data),
  });

export const apiDelete = (endpoint: string) => 
  apiRequest(endpoint, { method: 'DELETE' });

console.log('API Configuration loaded:', {
  baseUrl: API_BASE_URL,
  environment: process.env.NODE_ENV || 'development',
});
