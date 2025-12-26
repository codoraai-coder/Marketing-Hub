# X (Twitter) API - Frontend Integration Guide

> Complete guide for frontend developers to integrate X (Twitter) posting functionality into the Marketing Hub application.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [API Endpoints](#api-endpoints)
4. [Workflow Integration](#workflow-integration)
5. [Posting Flow](#posting-flow)
6. [TypeScript Interfaces](#typescript-interfaces)
7. [React Integration Examples](#react-integration-examples)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)

---

## Overview

The X (Twitter) integration uses a **user-assisted posting model**:

1. **Content is prepared** by the backend (via workflows or manual creation)
2. **Posting job is created** with status `ready`
3. **User manually posts** the content to X (copy/paste or use X's web interface)
4. **User marks the job** as `posted` or `failed`

> ⚠️ **Important**: The backend does NOT post directly to X. It prepares the content and the user must manually post it.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Frontend Application                         │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          Backend API                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐ │
│  │   Workflows     │───▶│  Content Layer  │───▶│  Posting Jobs   │ │
│  │   (post_to_x)   │    │   (approved)    │    │   (ready)       │ │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    User Manual Posting to X                          │
│                    (Copy text → Post on X.com)                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## API Endpoints

### Base URL
```
/api/posting-jobs
```

### 1. Get Ready Posting Jobs

Fetch all jobs waiting to be posted for a workspace.

```http
GET /api/posting-jobs/workspace/{workspace_id}/ready
```

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `workspace_id` | UUID | Yes | Workspace ID |
| `limit` | number | No | Max results (default: 50) |

**Response:**
```json
[
  {
    "id": "uuid",
    "workspace_id": "uuid",
    "content_id": "uuid",
    "platform": "x",
    "status": "ready",
    "prepared_payload": {
      "content_id": "uuid",
      "platform": "x",
      "post_text": "Your prepared post content here...",
      "image_url": "https://...",
      "hashtags": ["#marketing", "#growth"],
      "formatting_hints": {
        "max_length": 280,
        "supports_markdown": false,
        "supports_images": true,
        "supports_videos": true
      },
      "created_at": "2024-12-27T10:00:00Z"
    },
    "error_message": null,
    "retry_count": 0,
    "created_at": "2024-12-27T10:00:00Z",
    "posted_at": null
  }
]
```

---

### 2. Get All Posting Jobs

Fetch all jobs with optional status filter.

```http
GET /api/posting-jobs/workspace/{workspace_id}/all
```

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `workspace_id` | UUID | Yes | Workspace ID |
| `status_filter` | string | No | Filter by status |
| `limit` | number | No | Max results (default: 100) |

**Status Values:**
- `ready` - Prepared and waiting for user to post
- `awaiting_user` - Waiting for user action
- `posted` - Successfully posted
- `failed` - Failed to post

---

### 3. Get Single Posting Job

```http
GET /api/posting-jobs/{job_id}
```

**Response:**
```json
{
  "id": "uuid",
  "workspace_id": "uuid",
  "content_id": "uuid",
  "platform": "x",
  "status": "ready",
  "prepared_payload": {
    "post_text": "Your content here...",
    "image_url": "https://...",
    "formatting_hints": {
      "max_length": 280,
      "supports_markdown": false,
      "supports_images": true,
      "supports_videos": true
    }
  },
  "error_message": null,
  "retry_count": 0,
  "created_at": "2024-12-27T10:00:00Z",
  "posted_at": null
}
```

---

### 4. Mark Job as Posted

Call this after user has successfully posted to X.

```http
POST /api/posting-jobs/{job_id}/mark-posted
```

**Response:**
```json
{
  "id": "uuid",
  "status": "posted",
  "posted_at": "2024-12-27T10:05:00Z"
}
```

> ✅ This also updates the associated content status to `posted`.

---

### 5. Mark Job as Failed

Call this if user encounters an error posting to X.

```http
POST /api/posting-jobs/{job_id}/mark-failed
```

**Query Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `error_message` | string | No | Error description (default: "User reported posting failed") |

**Response:**
```json
{
  "id": "uuid",
  "status": "failed",
  "error_message": "User reported posting failed",
  "retry_count": 1
}
```

---

### 6. Retry Failed Job

Reset a failed job back to `ready` status.

```http
POST /api/posting-jobs/{job_id}/retry
```

**Response:**
```json
{
  "id": "uuid",
  "status": "ready",
  "error_message": null
}
```

---

## Workflow Integration

### Using `post_to_x` in Workflows

The `post_to_x` tool can be added as a step in any workflow to prepare content for X posting.

**Create Workflow with X Posting:**

```http
POST /api/workflows
```

```json
{
  "workspace_id": "your-workspace-uuid",
  "name": "Generate & Post to X",
  "description": "Generate caption and prepare for X posting",
  "target_platform": "x",
  "steps": [
    {
      "order": 1,
      "name": "Generate Caption",
      "tool_name": "caption_generator",
      "config": {
        "topic": "{{topic}}",
        "platform": "twitter",
        "tone": "engaging",
        "include_emojis": true,
        "include_hashtags": true
      }
    },
    {
      "order": 2,
      "name": "Post to X",
      "tool_name": "post_to_x",
      "config": {
        "workspace_id": "{{workspace_id}}",
        "content_id": "{{step_1_content_id}}"
      }
    }
  ]
}
```

### Available Tools

| Tool Name | Description |
|-----------|-------------|
| `blog_generator` | Generate blog posts |
| `image_generator` | Generate images |
| `caption_generator` | Generate captions |
| `content_optimizer` | Optimize existing content |
| `hashtag_generator` | Generate hashtags |
| `post_to_x` | Prepare content for X posting |

---

## Posting Flow

### User Journey

```
1. CONTENT GENERATION
   └── User runs workflow with caption_generator
       └── Content created with status: "draft"

2. CONTENT APPROVAL  
   └── User reviews and approves content
       └── PATCH /api/content/{id} → status: "approved"

3. PREPARE FOR POSTING
   └── Run post_to_x tool (via workflow or manually)
       └── Creates posting_job with status: "ready"

4. USER POSTS MANUALLY
   └── User opens X.com
   └── Copies prepared text from prepared_payload.post_text
   └── Pastes and posts on X

5. CONFIRM POSTING
   └── User clicks "Mark as Posted" button
       └── POST /api/posting-jobs/{id}/mark-posted
       └── Job status: "posted", Content status: "posted"
```

---

## TypeScript Interfaces

```typescript
// Enums
enum PostingStatus {
  READY = 'ready',
  AWAITING_USER = 'awaiting_user',
  POSTED = 'posted',
  FAILED = 'failed'
}

enum SocialPlatform {
  X = 'x'
}

// Posting Job Types
interface FormattingHints {
  max_length: number;
  supports_markdown: boolean;
  supports_images: boolean;
  supports_videos: boolean;
}

interface PreparedPayload {
  content_id: string;
  platform: string;
  post_text: string;
  image_url?: string;
  hashtags?: string[];
  formatting_hints: FormattingHints;
  created_at: string;
}

interface PostingJob {
  id: string;
  workspace_id: string;
  content_id: string;
  platform: string;
  status: PostingStatus;
  prepared_payload: PreparedPayload;
  error_message: string | null;
  retry_count: number;
  created_at: string;
  posted_at: string | null;
}

// API Response Types
interface PostingJobsResponse {
  data: PostingJob[];
}

// API Functions
interface PostingJobsAPI {
  getReadyJobs(workspaceId: string, limit?: number): Promise<PostingJob[]>;
  getAllJobs(workspaceId: string, statusFilter?: PostingStatus, limit?: number): Promise<PostingJob[]>;
  getJob(jobId: string): Promise<PostingJob>;
  markAsPosted(jobId: string): Promise<PostingJob>;
  markAsFailed(jobId: string, errorMessage?: string): Promise<PostingJob>;
  retryJob(jobId: string): Promise<PostingJob>;
}
```

---

## React Integration Examples

### API Service

```typescript
// services/postingJobsApi.ts
import axios from 'axios';

const API_BASE = '/api/posting-jobs';

export const postingJobsApi = {
  async getReadyJobs(workspaceId: string, limit = 50): Promise<PostingJob[]> {
    const { data } = await axios.get(
      `${API_BASE}/workspace/${workspaceId}/ready`,
      { params: { limit } }
    );
    return data;
  },

  async getAllJobs(
    workspaceId: string,
    statusFilter?: string,
    limit = 100
  ): Promise<PostingJob[]> {
    const { data } = await axios.get(
      `${API_BASE}/workspace/${workspaceId}/all`,
      { params: { status_filter: statusFilter, limit } }
    );
    return data;
  },

  async getJob(jobId: string): Promise<PostingJob> {
    const { data } = await axios.get(`${API_BASE}/${jobId}`);
    return data;
  },

  async markAsPosted(jobId: string): Promise<PostingJob> {
    const { data } = await axios.post(`${API_BASE}/${jobId}/mark-posted`);
    return data;
  },

  async markAsFailed(jobId: string, errorMessage?: string): Promise<PostingJob> {
    const { data } = await axios.post(
      `${API_BASE}/${jobId}/mark-failed`,
      null,
      { params: { error_message: errorMessage } }
    );
    return data;
  },

  async retryJob(jobId: string): Promise<PostingJob> {
    const { data } = await axios.post(`${API_BASE}/${jobId}/retry`);
    return data;
  }
};
```

### React Hook

```typescript
// hooks/usePostingJobs.ts
import { useState, useEffect, useCallback } from 'react';
import { postingJobsApi } from '../services/postingJobsApi';

export function usePostingJobs(workspaceId: string) {
  const [jobs, setJobs] = useState<PostingJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchJobs = useCallback(async () => {
    try {
      setLoading(true);
      const data = await postingJobsApi.getReadyJobs(workspaceId);
      setJobs(data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch posting jobs');
    } finally {
      setLoading(false);
    }
  }, [workspaceId]);

  useEffect(() => {
    fetchJobs();
  }, [fetchJobs]);

  const markAsPosted = async (jobId: string) => {
    try {
      await postingJobsApi.markAsPosted(jobId);
      await fetchJobs(); // Refresh list
    } catch (err) {
      throw new Error('Failed to mark as posted');
    }
  };

  const markAsFailed = async (jobId: string, message?: string) => {
    try {
      await postingJobsApi.markAsFailed(jobId, message);
      await fetchJobs();
    } catch (err) {
      throw new Error('Failed to mark as failed');
    }
  };

  const retry = async (jobId: string) => {
    try {
      await postingJobsApi.retryJob(jobId);
      await fetchJobs();
    } catch (err) {
      throw new Error('Failed to retry job');
    }
  };

  return {
    jobs,
    loading,
    error,
    refresh: fetchJobs,
    markAsPosted,
    markAsFailed,
    retry
  };
}
```

### Posting Queue Component

```tsx
// components/XPostingQueue.tsx
import React, { useState } from 'react';
import { usePostingJobs } from '../hooks/usePostingJobs';

interface Props {
  workspaceId: string;
}

export function XPostingQueue({ workspaceId }: Props) {
  const { jobs, loading, error, markAsPosted, markAsFailed, retry } = usePostingJobs(workspaceId);
  const [copying, setCopying] = useState<string | null>(null);

  const handleCopyToClipboard = async (job: PostingJob) => {
    const text = job.prepared_payload.post_text;
    try {
      await navigator.clipboard.writeText(text);
      setCopying(job.id);
      setTimeout(() => setCopying(null), 2000);
    } catch (err) {
      alert('Failed to copy to clipboard');
    }
  };

  const handleOpenX = () => {
    window.open('https://x.com/compose/post', '_blank');
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div className="error">{error}</div>;
  if (jobs.length === 0) return <div>No posts ready for X</div>;

  return (
    <div className="posting-queue">
      <h2>🐦 Ready to Post on X</h2>
      
      {jobs.map(job => (
        <div key={job.id} className="posting-card">
          {/* Content Preview */}
          <div className="content-preview">
            <p>{job.prepared_payload.post_text}</p>
            
            {job.prepared_payload.image_url && (
              <img 
                src={job.prepared_payload.image_url} 
                alt="Post image"
                className="preview-image"
              />
            )}
            
            {job.prepared_payload.hashtags && (
              <div className="hashtags">
                {job.prepared_payload.hashtags.map(tag => (
                  <span key={tag} className="hashtag">{tag}</span>
                ))}
              </div>
            )}
          </div>

          {/* Character Count */}
          <div className="char-count">
            {job.prepared_payload.post_text.length} / 280 characters
            {job.prepared_payload.post_text.length > 280 && (
              <span className="warning">⚠️ Over limit!</span>
            )}
          </div>

          {/* Actions */}
          <div className="actions">
            <button 
              onClick={() => handleCopyToClipboard(job)}
              className="btn-copy"
            >
              {copying === job.id ? '✓ Copied!' : '📋 Copy Text'}
            </button>
            
            <button onClick={handleOpenX} className="btn-open-x">
              🐦 Open X
            </button>
            
            <button 
              onClick={() => markAsPosted(job.id)}
              className="btn-posted"
            >
              ✅ Mark as Posted
            </button>
            
            <button 
              onClick={() => markAsFailed(job.id)}
              className="btn-failed"
            >
              ❌ Failed
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
```

### Post Composer Modal

```tsx
// components/XPostComposer.tsx
import React, { useState } from 'react';

interface Props {
  job: PostingJob;
  onPosted: () => void;
  onFailed: (message: string) => void;
  onClose: () => void;
}

export function XPostComposer({ job, onPosted, onFailed, onClose }: Props) {
  const [step, setStep] = useState<'preview' | 'confirm'>('preview');
  const { prepared_payload: payload } = job;
  
  const charCount = payload.post_text.length;
  const isOverLimit = charCount > 280;

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h3>Post to X (Twitter)</h3>
        
        {step === 'preview' && (
          <>
            {/* Preview Section */}
            <div className="x-post-preview">
              <div className="x-post-header">
                <img src="/x-logo.svg" alt="X" />
                <span>New Post</span>
              </div>
              
              <textarea 
                value={payload.post_text}
                readOnly
                rows={6}
              />
              
              <div className={`char-indicator ${isOverLimit ? 'over' : ''}`}>
                {charCount}/280
              </div>
              
              {payload.image_url && (
                <img 
                  src={payload.image_url} 
                  alt="Attachment"
                  className="attachment-preview"
                />
              )}
            </div>

            {/* Instructions */}
            <div className="instructions">
              <h4>Steps to Post:</h4>
              <ol>
                <li>Click "Copy Text" to copy the post content</li>
                <li>Click "Open X" to go to X.com</li>
                <li>Paste the text and add any images</li>
                <li>Click "Post" on X</li>
                <li>Return here and click "I Posted It"</li>
              </ol>
            </div>

            {/* Action Buttons */}
            <div className="button-row">
              <button 
                onClick={() => navigator.clipboard.writeText(payload.post_text)}
                className="btn-secondary"
              >
                📋 Copy Text
              </button>
              
              <button 
                onClick={() => window.open('https://x.com/compose/post', '_blank')}
                className="btn-primary"
              >
                🐦 Open X
              </button>
            </div>

            <div className="button-row">
              <button onClick={() => setStep('confirm')} className="btn-success">
                I Posted It ✓
              </button>
              <button onClick={onClose} className="btn-cancel">
                Cancel
              </button>
            </div>
          </>
        )}

        {step === 'confirm' && (
          <div className="confirm-section">
            <h4>Confirm Posting Status</h4>
            <p>Did you successfully post to X?</p>
            
            <div className="button-row">
              <button onClick={onPosted} className="btn-success">
                ✅ Yes, Posted Successfully
              </button>
              <button 
                onClick={() => onFailed('User reported posting failed')} 
                className="btn-danger"
              >
                ❌ No, It Failed
              </button>
            </div>
            
            <button onClick={() => setStep('preview')} className="btn-link">
              ← Back to Preview
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
```

---

## Error Handling

### Common Errors

| Status Code | Meaning | Action |
|-------------|---------|--------|
| 404 | Job not found | Check job ID, may have been deleted |
| 400 | Invalid request | Check required parameters |
| 400 | Cannot retry posted job | Job already posted successfully |
| 500 | Server error | Retry request, check logs |

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

### React Error Handling

```typescript
// utils/errorHandler.ts
export function handlePostingError(error: any): string {
  if (error.response) {
    const { status, data } = error.response;
    
    switch (status) {
      case 404:
        return 'This posting job no longer exists.';
      case 400:
        return data.detail || 'Invalid request. Please try again.';
      case 500:
        return 'Server error. Please try again later.';
      default:
        return data.detail || 'An unexpected error occurred.';
    }
  }
  
  return 'Network error. Please check your connection.';
}
```

---

## Best Practices

### 1. Character Limit Validation

Always validate post text length before allowing users to proceed:

```typescript
const MAX_X_CHARS = 280;

function validateXPost(text: string): { valid: boolean; message?: string } {
  if (text.length === 0) {
    return { valid: false, message: 'Post cannot be empty' };
  }
  if (text.length > MAX_X_CHARS) {
    return { 
      valid: false, 
      message: `Post is ${text.length - MAX_X_CHARS} characters over the limit` 
    };
  }
  return { valid: true };
}
```

### 2. Polling for Updates

If multiple users might update posting status, poll for updates:

```typescript
useEffect(() => {
  const interval = setInterval(() => {
    fetchJobs();
  }, 30000); // Poll every 30 seconds
  
  return () => clearInterval(interval);
}, [fetchJobs]);
```

### 3. Optimistic UI Updates

Update UI immediately, then sync with server:

```typescript
const markAsPosted = async (jobId: string) => {
  // Optimistically update UI
  setJobs(jobs.map(j => 
    j.id === jobId 
      ? { ...j, status: 'posted' as PostingStatus } 
      : j
  ));
  
  try {
    await postingJobsApi.markAsPosted(jobId);
  } catch (err) {
    // Revert on error
    await fetchJobs();
    throw err;
  }
};
```

### 4. Image Handling

When displaying images from `prepared_payload.image_url`:

```tsx
<img 
  src={payload.image_url}
  alt="Post attachment"
  onError={(e) => {
    e.currentTarget.style.display = 'none';
  }}
  loading="lazy"
/>
```

### 5. Status Badge Component

```tsx
function PostingStatusBadge({ status }: { status: PostingStatus }) {
  const config = {
    ready: { color: 'blue', icon: '🔵', label: 'Ready to Post' },
    awaiting_user: { color: 'yellow', icon: '🟡', label: 'Awaiting User' },
    posted: { color: 'green', icon: '🟢', label: 'Posted' },
    failed: { color: 'red', icon: '🔴', label: 'Failed' }
  };
  
  const { color, icon, label } = config[status];
  
  return (
    <span className={`status-badge status-${color}`}>
      {icon} {label}
    </span>
  );
}
```

---

## Quick Reference

### Posting Job Status Flow

```
ready → posted    (success)
ready → failed    (error)
failed → ready    (retry)
```

### API Cheat Sheet

| Action | Method | Endpoint |
|--------|--------|----------|
| Get ready jobs | GET | `/api/posting-jobs/workspace/{id}/ready` |
| Get all jobs | GET | `/api/posting-jobs/workspace/{id}/all` |
| Get single job | GET | `/api/posting-jobs/{id}` |
| Mark posted | POST | `/api/posting-jobs/{id}/mark-posted` |
| Mark failed | POST | `/api/posting-jobs/{id}/mark-failed` |
| Retry job | POST | `/api/posting-jobs/{id}/retry` |

---

## Support

For backend issues or questions about the X API integration, check:

- [README_POSTING_PHASE.md](./README_POSTING_PHASE.md) - Full backend documentation
- [test_x_connection.py](./test_x_connection.py) - Test X API credentials
- [POSTING_QUICKSTART.md](./POSTING_QUICKSTART.md) - Quick setup guide
