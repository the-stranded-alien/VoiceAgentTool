import axios from 'axios';
import type { AxiosInstance } from 'axios';
import type {
  AgentConfig,
  Call,
  CreateCallRequest,
  CreateWebCallRequest,
  DashboardStats,
  CallFilters,
} from '../types/index';

// Get base URL from environment variable or use default
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Create axios instance with default config
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

// Request interceptor for adding auth token if needed
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token here if needed
    // const token = localStorage.getItem('token');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.detail || error.response.data?.message || 'An error occurred';
      throw new Error(message);
    } else if (error.request) {
      // Request was made but no response received
      throw new Error('No response from server. Please check your connection.');
    } else {
      // Something else happened
      throw new Error(error.message || 'An unexpected error occurred');
    }
  }
);

// Agent Configuration APIs
export const agentConfigApi = {
  // Get all agent configurations
  getAll: async (): Promise<AgentConfig[]> => {
    const response = await apiClient.get<AgentConfig[]>('/agents/');
    return response.data;
  },

  // Get single agent configuration by ID
  getById: async (id: string): Promise<AgentConfig> => {
    const response = await apiClient.get<AgentConfig>(`/agents/${id}`);
    return response.data;
  },

  // Create new agent configuration
  create: async (data: Omit<AgentConfig, 'id' | 'created_at' | 'updated_at'>): Promise<AgentConfig> => {
    const response = await apiClient.post<AgentConfig>('/agents/', data);
    return response.data;
  },

  // Update existing agent configuration
  update: async (id: string, data: Partial<AgentConfig>): Promise<AgentConfig> => {
    const response = await apiClient.put<AgentConfig>(`/agents/${id}`, data);
    return response.data;
  },

  // Delete agent configuration
  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/agents/${id}`);
  },
};

// Call APIs
export const callApi = {
  // Get all calls with optional filters
  getAll: async (filters?: CallFilters): Promise<Call[]> => {
    const params = new URLSearchParams();

    if (filters?.status) params.append('status', filters.status);
    if (filters?.agent_config_id) params.append('agent_config_id', filters.agent_config_id);
    if (filters?.start_date) params.append('start_date', filters.start_date);
    if (filters?.end_date) params.append('end_date', filters.end_date);
    if (filters?.search) params.append('search', filters.search);

    const response = await apiClient.get<Call[]>(`/calls?${params.toString()}`);
    return response.data;
  },

  // Get single call by ID
  getById: async (id: string): Promise<Call> => {
    const response = await apiClient.get<Call>(`/calls/${id}`);
    return response.data;
  },

  // Create new phone call
  create: async (data: CreateCallRequest): Promise<Call> => {
    const response = await apiClient.post<Call>('/calls', data);
    return response.data;
  },

  // Create new web call
  createWebCall: async (data: CreateWebCallRequest): Promise<Call> => {
    const response = await apiClient.post<Call>('/calls/web', data);
    return response.data;
  },

  // Get recent calls (last 10)
  getRecent: async (limit: number = 10): Promise<Call[]> => {
    const response = await apiClient.get<Call[]>(`/calls?limit=${limit}`);
    return response.data;
  },
};

// Dashboard APIs
export const dashboardApi = {
  // Get dashboard statistics
  getStats: async (): Promise<DashboardStats> => {
    const response = await apiClient.get<DashboardStats>('/dashboard/stats');
    return response.data;
  },
};

// Combined API object for convenience with aliases
export const api = {
  // Agent Config methods
  getAgentConfigs: agentConfigApi.getAll,
  getAgentConfig: agentConfigApi.getById,
  createAgentConfig: agentConfigApi.create,
  updateAgentConfig: agentConfigApi.update,
  deleteAgentConfig: agentConfigApi.delete,

  // Call methods
  getCalls: callApi.getAll,
  getCall: callApi.getById,
  createCall: callApi.create,
  createWebCall: callApi.createWebCall,
  getRecentCalls: callApi.getRecent,

  // Dashboard methods
  getDashboardStats: dashboardApi.getStats,
};

// Export the axios instance for custom requests if needed
export default apiClient;
