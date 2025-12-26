-- Fix content table: Change workflow_step_id from UUID to TEXT
-- Run this in Supabase SQL Editor

-- Drop the existing table
DROP TABLE IF EXISTS content CASCADE;

-- Recreate with correct schema
CREATE TABLE IF NOT EXISTS content (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    workflow_step_id TEXT NOT NULL,
    
    -- Content metadata
    content_type TEXT NOT NULL CHECK (content_type IN ('blog_post', 'image', 'caption', 'hashtags', 'optimized_content')),
    title TEXT,
    
    -- Content data (JSONB for flexibility)
    data JSONB NOT NULL,
    
    -- Content lifecycle
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'approved', 'used', 'posted')),
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    approved_at TIMESTAMPTZ,
    posted_at TIMESTAMPTZ,
    
    -- Soft delete
    deleted_at TIMESTAMPTZ
);

-- Indexes for performance
CREATE INDEX idx_content_workspace_id ON content(workspace_id);
CREATE INDEX idx_content_job_id ON content(job_id);
CREATE INDEX idx_content_status ON content(status);
CREATE INDEX idx_content_content_type ON content(content_type);
CREATE INDEX idx_content_created_at ON content(created_at DESC);
CREATE INDEX idx_content_deleted_at ON content(deleted_at) WHERE deleted_at IS NULL;

-- Comments for documentation
COMMENT ON TABLE content IS 'Stores all tool outputs as first-class content entities';
COMMENT ON COLUMN content.data IS 'JSONB field containing the actual content output from tools';
COMMENT ON COLUMN content.workflow_step_id IS 'References the workflow step that generated this content (stored as text like step_1, step_2)';
COMMENT ON COLUMN content.status IS 'Lifecycle status: draft → approved → used → posted';
