// TypeScript interfaces and types for the Voice Agent Tool

// CallStatus as const object for type-safe values
export const CallStatus = {
  INITIATED: 'initiated',
  RINGING: 'ringing',
  IN_PROGRESS: 'in_progress',
  COMPLETED: 'completed',
  FAILED: 'failed',
  NO_ANSWER: 'no_answer',
  BUSY: 'busy',
  CANCELLED: 'cancelled',
  CALL_ENDED: "call_ended"
} as const;

// CallStatus type derived from the const object
export type CallStatus = typeof CallStatus[keyof typeof CallStatus];

export interface StructuredData {
  [key: string]: any;
}

export interface AgentConfig {
  id?: string;
  name: string;
  system_prompt: string;
  voice_id?: string;
  voice_temperature?: number;
  voice_speed?: number;
  responsiveness?: number;
  interruption_sensitivity?: number;
  enable_backchannel?: boolean;
  backchannel_frequency?: number;
  backchannel_words?: string[];
  reminder_trigger_ms?: number;
  reminder_max_count?: number;
  ambient_sound?: string;
  ambient_sound_volume?: number;
  language?: string;
  webhook_url?: string;
  boosted_keywords?: string[];
  opt_out_sensitive_data_storage?: boolean;
  normalize_for_speech?: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface Call {
  id: string;
  driver_name: string;
  phone_number: string;
  load_number?: string;
  status: CallStatus;
  agent_config_id?: string;
  agent_config?: AgentConfig;
  call_id?: string;
  access_token?: string;
  start_time?: string;
  end_time?: string;
  duration?: number;
  transcript?: string;
  structured_data?: StructuredData;
  recording_url?: string;
  error_message?: string;
  created_at: string;
  updated_at?: string;
}

export interface DashboardStats {
  total_calls: number;
  successful_calls: number;
  failed_calls: number;
  in_progress_calls: number;
  avg_duration?: number;
  emergency_calls?: number;
}

export interface ApiError {
  message: string;
  details?: any;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface CreateCallRequest {
  driver_name: string;
  phone_number: string;
  load_number?: string;
  agent_config_id: string;
}

// Alias for CreateCallRequest
export type CallCreate = CreateCallRequest;

export interface CreateWebCallRequest {
  driver_name: string;
  load_number?: string;
  agent_config_id: string;
}

export interface CallUpdate {
  driver_name?: string;
  phone_number?: string;
  load_number?: string;
  status?: CallStatus;
  transcript?: string;
  structured_data?: StructuredData;
  recording_url?: string;
  error_message?: string;
  start_time?: string;
  end_time?: string;
  duration?: number;
}

export interface CallFilters {
  status?: CallStatus;
  agent_config_id?: string;
  start_date?: string;
  end_date?: string;
  search?: string;
}
