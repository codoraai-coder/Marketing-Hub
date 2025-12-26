# Content Layer Implementation ✅

## Overview

The Content Layer makes tool outputs **first-class citizens** in the Marketing Hub system. Instead of tool outputs disappearing into job logs, they're now stored as persistent content entities with full lifecycle management.

## 🎯 Benefits

1. **Approval Workflows**: Review and approve AI-generated content before posting
2. **Content Reuse**: Access previously generated content across workflows
3. **Audit Trail**: Complete history of what was generated and when
4. **Analytics Attachment**: Link content to social media posts and track performance
5. **Status Management**: Track content from draft → approved → used → posted

## 📋 Implementation Complete

### 1. Database Schema
- ✅ `migrations/002_add_content_table.sql` - Content table with lifecycle fields
- ✅ Indexes for performance (workspace, job, status, content_type, created_at)
- ✅ JSONB data field for flexible content storage
- ✅ Soft delete support

### 2. Enums Added
- ✅ `ContentType` - blog_post, image, caption, hashtags, optimized_content
- ✅ `ContentStatus` - draft, approved, used, posted

### 3. Schemas
- ✅ `CreateContentDto` - For creating new content
- ✅ `UpdateContentDto` - For updating content
- ✅ `ContentResponse` - Content in API responses

### 4. Job Runner Enhancement
- ✅ `_save_content()` method - Automatically saves tool outputs to content table
- ✅ Maps tool names to content types
- ✅ Extracts titles from results
- ✅ Sets initial status to DRAFT

### 5. Content API Router
- ✅ `GET /api/content/` - List content with filters
- ✅ `GET /api/content/{id}` - Get specific content
- ✅ `PATCH /api/content/{id}` - Update content
- ✅ `DELETE /api/content/{id}` - Soft delete content
- ✅ `POST /api/content/{id}/approve` - Approve content shortcut
- ✅ `GET /api/content/workspace/{id}/pending` - Get pending content for approval

## 🚀 Getting Started

### Step 1: Apply Database Migration

**Option A: Via Supabase Dashboard (Recommended)**
1. Go to: `https://supabase.com/dashboard/project/YOUR_PROJECT/sql`
2. Create new query
3. Copy contents of `migrations/002_add_content_table.sql`
4. Paste and click "Run"
5. Verify: `SELECT * FROM content LIMIT 1;`

**Option B: Via Script**
```bash
python apply_content_migration.py
```

### Step 2: Restart Server
```bash
# Kill existing server
# Restart with:
python -m uvicorn main:app --reload
```

### Step 3: Test Implementation
```bash
python test_content_layer.py
```

## 📖 API Usage

### List All Content
```bash
curl "http://localhost:8000/api/content/?workspace_id=YOUR_WORKSPACE_ID"
```

### Filter by Status
```bash
# Get all draft content
curl "http://localhost:8000/api/content/?status=draft"

# Get all approved content
curl "http://localhost:8000/api/content/?status=approved"
```

### Filter by Content Type
```bash
# Get all captions
curl "http://localhost:8000/api/content/?content_type=caption"

# Get all blog posts
curl "http://localhost:8000/api/content/?content_type=blog_post"
```

### Get Specific Content
```bash
curl "http://localhost:8000/api/content/CONTENT_ID"
```

### Approve Content
```bash
curl -X POST "http://localhost:8000/api/content/CONTENT_ID/approve"
```

### Update Content Status
```bash
curl -X PATCH "http://localhost:8000/api/content/CONTENT_ID" \
  -H "Content-Type: application/json" \
  -d '{"status": "posted"}'
```

### Get Pending Content for Workspace
```bash
curl "http://localhost:8000/api/content/workspace/WORKSPACE_ID/pending"
```

## 🔄 Content Lifecycle

```
┌─────────┐     approve     ┌──────────┐     use in     ┌──────┐     post to     ┌────────┐
│  DRAFT  │ ───────────────> │ APPROVED │ ─────────────> │ USED │ ─────────────> │ POSTED │
└─────────┘                  └──────────┘                └──────┘                └────────┘
     │                            │                           │                        │
     │                            │                           │                        │
     └────────────────────────────┴───────────────────────────┴────────────────────────┘
                            delete (soft delete with deleted_at)
```

### Status Meanings

- **DRAFT**: Just generated, awaiting review
- **APPROVED**: Reviewed and approved for use
- **USED**: Incorporated into a social media post (but not published yet)
- **POSTED**: Published to social media platform

## 🔗 Integration with Workflows

Content is **automatically created** when workflows run:

1. User creates workflow with steps
2. User runs workflow: `POST /api/workflows/{id}/run`
3. Background job executes each step
4. **For each step**: Tool output → Saved as Content (status=DRAFT)
5. Job completes with content IDs in logs

Example job log after completion:
```json
{
  "message": "Completed Generate Caption",
  "step": "Generate Caption",
  "result": {
    "caption": "5 productivity tips for remote work...",
    "platform": "linkedin"
  },
  "content_id": "uuid-of-saved-content"
}
```

## 📊 Content Data Structure

Content is stored with flexible JSONB data field:

### Blog Post Content
```json
{
  "content_type": "blog_post",
  "data": {
    "topic": "AI in marketing",
    "docx_url": "https://s3...",
    "cover_url": "https://s3...",
    "created_at": "2025-12-26T..."
  }
}
```

### Caption Content
```json
{
  "content_type": "caption",
  "data": {
    "caption": "Transform your marketing...",
    "platform": "linkedin",
    "tone": "professional"
  }
}
```

### Hashtag Content
```json
{
  "content_type": "hashtags",
  "data": {
    "hashtags": ["#Marketing", "#AI", "#Productivity"],
    "count": 3,
    "platform": "linkedin"
  }
}
```

## 🧪 Testing

The `test_content_layer.py` script provides comprehensive testing:

1. ✅ Create workspace
2. ✅ Create workflow with caption generator
3. ✅ Run workflow
4. ✅ List generated content
5. ✅ Get content details
6. ✅ Approve content
7. ✅ Update content to posted
8. ✅ Get pending content

Run tests:
```bash
python test_content_layer.py
```

## 🔍 Verification Queries

After migration, verify in Supabase SQL Editor:

```sql
-- Check table exists
SELECT * FROM content LIMIT 5;

-- Check indexes
SELECT indexname FROM pg_indexes WHERE tablename = 'content';

-- Count content by status
SELECT status, COUNT(*) FROM content GROUP BY status;

-- Count content by type
SELECT content_type, COUNT(*) FROM content GROUP BY content_type;

-- Get recent content
SELECT id, content_type, status, created_at, title 
FROM content 
WHERE deleted_at IS NULL 
ORDER BY created_at DESC 
LIMIT 10;
```

## 🎨 Frontend Integration Ideas

1. **Approval Dashboard**: Show all draft content, allow approve/reject
2. **Content Library**: Browse all approved content, filter by type
3. **Content Calendar**: Schedule approved content for posting
4. **Analytics View**: Link posted content to performance metrics

## ⚡ Next Steps

1. **Social Media Posting**: Integrate with LinkedIn/Twitter APIs to post approved content
2. **Content Scheduling**: Add scheduled_for field and cron job for auto-posting
3. **Content Templates**: Allow users to create content templates
4. **A/B Testing**: Generate multiple versions of content for testing
5. **Analytics Integration**: Track engagement metrics for posted content

## 🐛 Troubleshooting

### Migration fails with "relation already exists"
```sql
-- Drop and recreate
DROP TABLE IF EXISTS content CASCADE;
-- Then re-run migration
```

### Content not being created
1. Check job logs: `GET /api/jobs/{job_id}`
2. Verify tool execution succeeds
3. Check JobRunner._save_content() logs
4. Ensure CONTENT_TABLE constant is correct

### Cannot query content
1. Verify migration applied: `SELECT * FROM content LIMIT 1;`
2. Check table permissions in Supabase
3. Ensure content router registered in main.py

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Supabase Documentation](https://supabase.com/docs)
- [Workflow APIs README](./README_WORKFLOW_APIS.md)
- [Main README](./README.md)

---

**Status**: ✅ Implementation Complete  
**Date**: December 26, 2025  
**Version**: 1.0.0
