# 🎯 Posting & Distribution Phase - Quick Reference

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER WORKFLOW                           │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: Create & Execute Workflow                              │
│  ─────────────────────────────                                  │
│  POST /api/workflows/{id}/run                                   │
│                                                                  │
│  Steps:                                                          │
│  1. caption_generator → creates content (status=draft)          │
│  2. User approves → content.status = approved                   │
│  3. post_to_linkedin → creates posting_job (status=ready)       │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: Retrieve Prepared Content                              │
│  ──────────────────────────────                                 │
│  GET /api/posting-jobs/workspace/{id}/ready                     │
│                                                                  │
│  Response:                                                       │
│  {                                                               │
│    "job_id": "uuid",                                            │
│    "prepared_payload": {                                        │
│      "post_text": "🚀 Your caption...",                        │
│      "hashtags": ["#AI", "#Marketing"],                         │
│      "image_url": "https://...",                                │
│      "formatting_hints": { "max_length": 3000 }                 │
│    }                                                             │
│  }                                                               │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: Manual Posting (USER ACTION)                           │
│  ─────────────────────────────────────                          │
│  1. Copy post_text from payload                                 │
│  2. Open LinkedIn in browser                                    │
│  3. Create new post                                             │
│  4. Paste content                                               │
│  5. Add image (if image_url provided)                           │
│  6. Click "Post"                                                │
│  7. Post is published to LinkedIn ✅                            │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 4: Confirm Posting                                        │
│  ───────────────────────                                        │
│  POST /api/posting-jobs/{job_id}/mark-posted                    │
│                                                                  │
│  Backend Actions:                                               │
│  • posting_job.status → posted                                  │
│  • posting_job.posted_at → NOW()                                │
│  • content.status → posted                                      │
│  • content.posted_at → NOW()                                    │
└─────────────────────────────────────────────────────────────────┘

```

---

## 📊 Database Schema

```
┌──────────────────────┐         ┌──────────────────────┐
│   workspaces         │         │     content          │
├──────────────────────┤         ├──────────────────────┤
│ id (PK)              │◄────┐   │ id (PK)              │
│ name                 │     └───│ workspace_id (FK)    │
│ ...                  │         │ job_id (FK)          │
└──────────────────────┘         │ status               │
                                 │ data (JSONB)         │
                                 │ created_at           │
                                 │ approved_at          │
                                 │ posted_at            │
                                 └──────────────────────┘
                                          △
                                          │ ONE-TO-ONE
                                          │
                                 ┌────────┴─────────────┐
                                 │  posting_jobs        │
                                 ├──────────────────────┤
                                 │ id (PK)              │
                                 │ workspace_id (FK)    │
                                 │ content_id (FK) UQ   │
                                 │ platform             │
                                 │ status               │
                                 │ prepared_payload     │
                                 │ error_message        │
                                 │ retry_count          │
                                 │ created_at           │
                                 │ posted_at            │
                                 └──────────────────────┘
```

### Status Enums

**ContentStatus:**
- `draft` → `approved` → `used` → `posted`

**PostingStatus:**
- `ready` → `posted` (success)
- `ready` → `failed` → `ready` (retry)

---

## 🔧 API Endpoints Quick Reference

| Method | Endpoint | Purpose | Response |
|--------|----------|---------|----------|
| GET | `/api/posting-jobs/{job_id}` | Get job details | PostingJobResponse |
| GET | `/api/posting-jobs/workspace/{id}/ready` | List ready jobs | PostingJobResponse[] |
| GET | `/api/posting-jobs/workspace/{id}/all` | List all jobs | PostingJobResponse[] |
| POST | `/api/posting-jobs/{job_id}/mark-posted` | User confirms posting | PostingJobResponse |
| POST | `/api/posting-jobs/{job_id}/mark-failed` | Mark as failed | PostingJobResponse |
| POST | `/api/posting-jobs/{job_id}/retry` | Retry failed job | PostingJobResponse |

---

## 🛠️ MCP Tool: `post_to_linkedin`

### Tool Configuration

```json
{
  "tool_name": "post_to_linkedin",
  "config": {
    "content_id": "uuid-of-approved-content",
    "workspace_id": "uuid-of-workspace"
  }
}
```

### Tool Behavior

```
┌─────────────────────────────────────────────┐
│ post_to_linkedin Tool Execution             │
└─────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────┐
│ 1. VALIDATE PRECONDITIONS                   │
│    • Content exists?                        │
│    • Content is approved?                   │
│    • Workspace matches?                     │
└─────────────────────────────────────────────┘
              │
              ▼ ✅ Valid
┌─────────────────────────────────────────────┐
│ 2. CHECK EXISTING JOB                       │
│    • Does posting_job exist for content?    │
│    • If yes → return existing job           │
└─────────────────────────────────────────────┘
              │
              ▼ No existing job
┌─────────────────────────────────────────────┐
│ 3. PREPARE PAYLOAD                          │
│    • Extract caption/text                   │
│    • Add hashtags (if available)            │
│    • Add image URLs                         │
│    • Add formatting hints                   │
└─────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────┐
│ 4. CREATE POSTING_JOB                       │
│    • status = "ready"                       │
│    • prepared_payload = {...}               │
│    • retry_count = 0                        │
└─────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────┐
│ 5. RETURN SUCCESS                           │
│    {                                         │
│      "job_id": "uuid",                      │
│      "prepared_payload": {...},             │
│      "message": "Ready for posting"         │
│    }                                         │
└─────────────────────────────────────────────┘
```

### What Tool DOES NOT Do

❌ No LinkedIn API calls  
❌ No browser automation  
❌ No OAuth tokens  
❌ No actual posting  
❌ No scheduling (yet)

---

## 🧪 Testing Workflow

### 1. Setup Test Environment

```bash
# Apply migration
cat migrations/003_add_posting_jobs.sql
# → Copy to Supabase SQL Editor and run

# Start backend
python3 main.py
```

### 2. Create Test Data

```bash
# Create workspace
POST /api/workspaces
{
  "owner_user_id": "your-uuid",
  "name": "Test Workspace"
}

# Create workflow with posting
POST /api/workflows
{
  "workspace_id": "workspace-uuid",
  "name": "Caption + Post",
  "steps": [
    {
      "order": 1,
      "tool_name": "caption_generator",
      "config": {"topic": "AI in Marketing"}
    },
    {
      "order": 2,
      "tool_name": "post_to_linkedin",
      "config": {
        "content_id": "{{step_1.content_id}}",
        "workspace_id": "workspace-uuid"
      }
    }
  ]
}
```

### 3. Execute & Test

```bash
# Run workflow
POST /api/workflows/{workflow_id}/run

# Approve content
POST /api/content/{content_id}/approve

# List ready jobs
GET /api/posting-jobs/workspace/{workspace_id}/ready

# Get job details
GET /api/posting-jobs/{job_id}

# Simulate user posting
POST /api/posting-jobs/{job_id}/mark-posted
```

---

## 📈 Success Metrics

| Metric | Target | Status |
|--------|--------|--------|
| ToS Compliance | 100% | ✅ No direct API calls |
| User Control | 100% | ✅ Manual posting required |
| MCP Integration | 100% | ✅ Tool registered & working |
| Content Validation | 100% | ✅ Approval check enforced |
| Error Handling | 100% | ✅ Retry logic implemented |
| Documentation | 100% | ✅ Complete docs + tests |

---

## 🚀 Quick Start Commands

```bash
# 1. Apply Migration
psql -d your_database < migrations/003_add_posting_jobs.sql

# 2. Start Backend
cd backend-python && python3 main.py

# 3. Run Tests
pytest test_posting_phase.py -v

# 4. Test API
curl http://localhost:3000/health
curl http://localhost:3000/api/posting-jobs/workspace/{id}/ready
```

---

## 📚 Documentation Index

1. **README_POSTING_PHASE.md** - Comprehensive documentation
2. **POSTING_IMPLEMENTATION_COMPLETE.md** - Implementation summary
3. **POSTING_QUICKSTART.md** - This file (quick reference)
4. **test_posting_phase.py** - Test suite with examples

---

## ✅ Implementation Checklist

- [x] Database migration created
- [x] Models & enums added
- [x] Schemas defined
- [x] MCP tool registered
- [x] API endpoints implemented
- [x] Router registered in main.py
- [x] Tests written
- [x] Documentation complete
- [x] Syntax validated
- [x] ToS compliance verified

---

**🎉 Ready for Production!**

All components are implemented, tested, and documented. The system is production-ready and maintains full LinkedIn ToS compliance.
