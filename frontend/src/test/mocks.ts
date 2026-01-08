import type { AgentConfig, Call, DashboardStats } from '../types/index';
import { CallStatus } from '../types/index';

export const mockAgentConfig: AgentConfig = {
  id: '1',
  name: 'Test Agent',
  system_prompt: 'You are a helpful assistant',
  voice_id: 'test-voice',
  responsiveness: 0.8,
  interruption_sensitivity: 1.0,
  enable_backchannel: true,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
};

export const mockCall: Call = {
  id: '1',
  driver_name: 'John Doe',
  phone_number: '+1234567890',
  load_number: 'LOAD-001',
  status: CallStatus.COMPLETED,
  agent_config_id: '1',
  agent_config: mockAgentConfig,
  call_id: 'call-123',
  start_time: '2024-01-01T10:00:00Z',
  end_time: '2024-01-01T10:05:00Z',
  duration: 300,
  transcript: 'Test transcript',
  created_at: '2024-01-01T10:00:00Z',
  updated_at: '2024-01-01T10:05:00Z',
};

export const mockDashboardStats: DashboardStats = {
  total_calls: 100,
  successful_calls: 85,
  failed_calls: 10,
  in_progress_calls: 5,
  avg_duration: 180,
  emergency_calls: 3,
};

export const mockCalls: Call[] = [
  mockCall,
  {
    ...mockCall,
    id: '2',
    driver_name: 'Jane Smith',
    phone_number: '+1987654321',
    load_number: 'LOAD-002',
    status: CallStatus.IN_PROGRESS,
  },
  {
    ...mockCall,
    id: '3',
    driver_name: 'Bob Johnson',
    phone_number: '+1122334455',
    load_number: 'LOAD-003',
    status: CallStatus.FAILED,
  },
];
