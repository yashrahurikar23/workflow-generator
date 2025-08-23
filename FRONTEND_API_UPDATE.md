// Update frontend API configuration
// File: frontend/src/services/api.ts

export const API_CONFIG = {
  // Use deployed backend
  BASE_URL: 'https://workflow-backend.onrender.com',
  
  // Fallback to local for development
  // BASE_URL: 'http://localhost:8004',
  
  ENDPOINTS: {
    WORKFLOWS: '/api/v1/workflows',
    CHAT: '/api/v1/chat',
    EXECUTE: (workflowId: string) => `/api/v1/workflows/${workflowId}/execute`,
  },
  
  TIMEOUT: 30000, // 30 seconds for free tier wake-up
};

// Helper function for API calls
export const apiCall = async (endpoint: string, options = {}) => {
  const url = `${API_CONFIG.BASE_URL}${endpoint}`;
  
  const defaultOptions = {
    timeout: API_CONFIG.TIMEOUT,
    headers: {
      'Content-Type': 'application/json',
    },
    ...options,
  };
  
  try {
    const response = await fetch(url, defaultOptions);
    
    if (!response.ok) {
      throw new Error(`API call failed: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API call error:', error);
    throw error;
  }
};
