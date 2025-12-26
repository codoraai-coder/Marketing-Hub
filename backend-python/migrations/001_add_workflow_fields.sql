-- Migration: Add workflow schema enhancements
-- Date: 2025-12-26
-- Purpose: Support complete workflow API implementation

-- Add target_platform column to workflows table
ALTER TABLE workflows
ADD COLUMN IF NOT EXISTS target_platform VARCHAR(50),
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP;

-- Create index for soft delete queries
CREATE INDEX IF NOT EXISTS idx_workflows_deleted_at ON workflows(deleted_at);

-- Create index for workspace queries
CREATE INDEX IF NOT EXISTS idx_workflows_workspace_id ON workflows(workspace_id);

-- Add trigger to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_workflows_updated_at BEFORE UPDATE ON workflows
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Add index for job status queries (for checking active jobs)
CREATE INDEX IF NOT EXISTS idx_jobs_workflow_status ON jobs(workflow_id, status);

-- Add comment for documentation
COMMENT ON COLUMN workflows.deleted_at IS 'Soft delete timestamp - workflow is hidden when not null';
COMMENT ON COLUMN workflows.target_platform IS 'Target social media platform (linkedin, etc.)';
COMMENT ON COLUMN workflows.updated_at IS 'Timestamp of last update';
