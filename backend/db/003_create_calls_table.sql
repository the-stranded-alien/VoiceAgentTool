-- =====================================================
-- TABLE: calls
-- Stores individual call records
-- =====================================================
CREATE TABLE calls (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_config_id UUID REFERENCES agent_configs(id) ON DELETE SET NULL,
    driver_name VARCHAR(255) NOT NULL,
    driver_phone VARCHAR(20) NOT NULL,
    load_number VARCHAR(50) NOT NULL,
    retell_call_id VARCHAR(255) UNIQUE,
    status VARCHAR(50) DEFAULT 'initiated' CHECK (status IN ('initiated', 'in_progress', 'completed', 'failed', 'escalated')),
    call_outcome VARCHAR(100),
    raw_transcript TEXT,
    structured_data JSONB,
    call_duration_seconds INTEGER,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);