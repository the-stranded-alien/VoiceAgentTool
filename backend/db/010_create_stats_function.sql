-- =====================================================
-- FUNCTION: Get Today's Statistics
-- =====================================================
CREATE OR REPLACE FUNCTION get_today_stats()
RETURNS TABLE(
    total_calls BIGINT,
    successful_calls BIGINT,
    emergency_calls BIGINT,
    in_progress_calls BIGINT,
    avg_duration_minutes NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*) as total_calls,
        COUNT(CASE WHEN status = 'completed' THEN 1 END) as successful_calls,
        COUNT(CASE WHEN call_outcome LIKE '%Emergency%' THEN 1 END) as emergency_calls,
        COUNT(CASE WHEN status = 'in_progress' THEN 1 END) as in_progress_calls,
        ROUND(AVG(call_duration_seconds) / 60.0, 2) as avg_duration_minutes
    FROM calls
    WHERE DATE(created_at) = CURRENT_DATE;
END;
$$ LANGUAGE plpgsql;