-- =====================================================
-- TABLE: agent_configs
-- Stores AI agent configuration and prompts
-- =====================================================
CREATE TABLE agent_configs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    scenario_type VARCHAR(50) NOT NULL CHECK (scenario_type IN ('check_in', 'emergency', 'delivery', 'custom')),
    system_prompt TEXT NOT NULL,
    conversation_rules JSONB DEFAULT '{}',
    voice_settings JSONB DEFAULT '{
        "voice_id": "default",
        "response_delay": 0.8,
        "interruption_sensitivity": 0.7,
        "backchannel": {"enabled": true, "frequency": "medium"},
        "filler_words": {"enabled": true},
        "ambient_sound": false,
        "speaking_rate": "normal"
    }',
    advanced_settings JSONB DEFAULT '{
        "max_call_duration_minutes": 10,
        "retry_attempts": 3,
        "auto_escalate_emergency": true,
        "record_calls": true
    }',
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('active', 'draft', 'inactive')),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);