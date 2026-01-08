-- =====================================================
-- INDEXES for Performance
-- =====================================================
CREATE INDEX idx_calls_agent_config ON calls(agent_config_id);
CREATE INDEX idx_calls_status ON calls(status);
CREATE INDEX idx_calls_created_at ON calls(created_at DESC);
CREATE INDEX idx_calls_retell_id ON calls(retell_call_id);
CREATE INDEX idx_call_events_call_id ON call_events(call_id);
CREATE INDEX idx_call_events_timestamp ON call_events(timestamp DESC);