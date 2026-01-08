-- =====================================================
-- VIEW: Agent Performance Metrics
-- =====================================================
CREATE OR REPLACE VIEW agent_performance_metrics AS
SELECT 
    ac.id,
    ac.name,
    ac.scenario_type,
    ac.status,
    COUNT(c.id) as total_calls,
    COUNT(CASE WHEN c.status = 'completed' THEN 1 END) as successful_calls,
    COUNT(CASE WHEN c.status = 'failed' THEN 1 END) as failed_calls,
    COUNT(CASE WHEN c.status = 'escalated' THEN 1 END) as escalated_calls,
    ROUND(
        (COUNT(CASE WHEN c.status = 'completed' THEN 1 END)::NUMERIC / 
        NULLIF(COUNT(c.id), 0) * 100), 
        2
    ) as success_rate_percent,
    AVG(c.call_duration_seconds) as avg_duration_seconds,
    MAX(c.created_at) as last_used_at
FROM agent_configs ac
LEFT JOIN calls c ON ac.id = c.agent_config_id
GROUP BY ac.id, ac.name, ac.scenario_type, ac.status;