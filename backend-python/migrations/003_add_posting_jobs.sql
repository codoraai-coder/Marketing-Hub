-- Migration: Add posting_jobs table
-- Purpose: Track content prepared for posting to social platforms (user-assisted posting)
-- Date: 2025-12-26

-- Create posting_jobs table
CREATE TABLE IF NOT EXISTS posting_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    content_id UUID NOT NULL REFERENCES content(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'ready',
    prepared_payload JSONB NOT NULL,
    error_message TEXT,
    retry_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    posted_at TIMESTAMPTZ,
    CONSTRAINT unique_content_posting_job UNIQUE (content_id)
);

-- Add comments
COMMENT ON TABLE posting_jobs IS 'Tracks content prepared for posting to social platforms. MCP prepares the payload, user posts manually.';
COMMENT ON COLUMN posting_jobs.id IS 'Primary key';
COMMENT ON COLUMN posting_jobs.workspace_id IS 'References workspace this posting job belongs to';
COMMENT ON COLUMN posting_jobs.content_id IS 'References content being posted (one-to-one relationship)';
COMMENT ON COLUMN posting_jobs.platform IS 'Target platform: linkedin, twitter, facebook, etc.';
COMMENT ON COLUMN posting_jobs.status IS 'Job status: ready, awaiting_user, posted, failed';
COMMENT ON COLUMN posting_jobs.prepared_payload IS 'JSON payload ready for user to post (caption, hashtags, formatting)';
COMMENT ON COLUMN posting_jobs.error_message IS 'Error details if posting failed';
COMMENT ON COLUMN posting_jobs.retry_count IS 'Number of retry attempts';
COMMENT ON COLUMN posting_jobs.created_at IS 'When posting job was created';
COMMENT ON COLUMN posting_jobs.posted_at IS 'When user confirmed post was published';

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_posting_jobs_workspace_id ON posting_jobs(workspace_id);
CREATE INDEX IF NOT EXISTS idx_posting_jobs_content_id ON posting_jobs(content_id);
CREATE INDEX IF NOT EXISTS idx_posting_jobs_status ON posting_jobs(status);
CREATE INDEX IF NOT EXISTS idx_posting_jobs_platform ON posting_jobs(platform);
CREATE INDEX IF NOT EXISTS idx_posting_jobs_created_at ON posting_jobs(created_at DESC);

-- Create index for fetching ready jobs per workspace
CREATE INDEX IF NOT EXISTS idx_posting_jobs_workspace_status ON posting_jobs(workspace_id, status);
