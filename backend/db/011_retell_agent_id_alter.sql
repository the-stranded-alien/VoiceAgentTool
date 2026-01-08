-- Add retell_agent_id to agent_configs if not exists
ALTER TABLE agent_configs 
ADD COLUMN IF NOT EXISTS retell_agent_id VARCHAR(255);

-- Add index
CREATE INDEX IF NOT EXISTS idx_agent_configs_retell_id 
ON agent_configs(retell_agent_id);

-- Add comment
COMMENT ON COLUMN agent_configs.retell_agent_id IS 'Retell AI agent ID from their platform';