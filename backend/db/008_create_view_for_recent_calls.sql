-- =====================================================
-- VIEW: Recent Calls Summary
-- =====================================================
CREATE OR REPLACE VIEW recent_calls_summary AS
SELECT 
    c.id,
    c.driver_name,
    c.driver_phone,
    c.load_number,
    c.status,
    c.call_outcome,
    c.call_duration_seconds,
    c.created_at,
    c.completed_at,
    ac.name as agent_name,
    ac.scenario_type,
    CASE 
        WHEN c.completed_at IS NOT NULL THEN 
            EXTRACT(EPOCH FROM (c.completed_at - c.created_at)) / 60
        ELSE NULL
    END as duration_minutes
FROM calls c
LEFT JOIN agent_configs ac ON c.agent_config_id = ac.id
ORDER BY c.created_at DESC;