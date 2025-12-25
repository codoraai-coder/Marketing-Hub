# 🚀 Frontend Integration Guide - MCP Hub API

**Version**: 1.0  
**Base URL**: `http://localhost:3000` (Development)  
**Content-Type**: `application/json`

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [API Endpoints](#api-endpoints)
3. [TypeScript Types](#typescript-types)
4. [Integration Examples](#integration-examples)
5. [Error Handling](#error-handling)
6. [Best Practices](#best-practices)

---

## 🎯 Quick Start

### Base Configuration

```typescript
// config/api.ts
export const API_CONFIG = {
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:3000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
};

// Create axios instance (or use fetch)
import axios from 'axios';

export const apiClient = axios.create(API_CONFIG);
```

---

## 📡 API Endpoints

### 1. Workspaces

#### Create Workspace
```http
POST /workspaces
```

**Request Body:**
```json
{
  "ownerUserId": "uuid",
  "name": "My Marketing Workspace"
}
```

**Response (201):**
```json
{
  "id": "workspace-uuid",
  "ownerUserId": "user-uuid",
  "name": "My Marketing Workspace",
  "createdAt": "2025-12-26T00:00:00.000Z"
}
```

**Frontend Usage:**
```typescript
const createWorkspace = async (userId: string, name: string) => {
  const response = await apiClient.post('/workspaces', {
    ownerUserId: userId,
    name: name,
  });
  return response.data;
};
```

---

#### Get Workspace
```http
GET /workspaces/:id
```

**Response (200):**
```json
{
  "id": "workspace-uuid",
  "ownerUserId": "user-uuid",
  "name": "My Marketing Workspace",
  "createdAt": "2025-12-26T00:00:00.000Z",
  "owner": {
    "id": "user-uuid",
    "name": "John Doe",
    "email": "john@example.com"
  }
}
```

**Frontend Usage:**
```typescript
const getWorkspace = async (workspaceId: string) => {
  const response = await apiClient.get(`/workspaces/${workspaceId}`);
  return response.data;
};
```

---

#### Get User's Workspaces
```http
GET /workspaces/user/:userId
```

**Response (200):**
```json
[
  {
    "id": "workspace-1",
    "ownerUserId": "user-uuid",
    "name": "Marketing Workspace",
    "createdAt": "2025-12-26T00:00:00.000Z"
  },
  {
    "id": "workspace-2",
    "ownerUserId": "user-uuid",
    "name": "Sales Workspace",
    "createdAt": "2025-12-25T00:00:00.000Z"
  }
]
```

**Frontend Usage:**
```typescript
const getUserWorkspaces = async (userId: string) => {
  const response = await apiClient.get(`/workspaces/user/${userId}`);
  return response.data;
};
```

---

### 2. Content

#### Create Content (Manual)
```http
POST /content
```

**Request Body:**
```json
{
  "workspaceId": "workspace-uuid",
  "type": "blog",
  "s3Url": "https://bucket.s3.amazonaws.com/path/to/file",
  "textData": "Blog content text...",
  "status": "draft"
}
```

**Types:** `blog`, `image`, `caption`, `doc`  
**Statuses:** `draft`, `approved`, `used`, `posted`

**Response (201):**
```json
{
  "id": "content-uuid",
  "workspaceId": "workspace-uuid",
  "type": "blog",
  "s3Url": "https://...",
  "textData": "Blog content...",
  "status": "draft",
  "createdAt": "2025-12-26T00:00:00.000Z"
}
```

---

#### Get Content by ID
```http
GET /content/:id
```

**Response (200):**
```json
{
  "id": "content-uuid",
  "workspaceId": "workspace-uuid",
  "type": "blog",
  "s3Url": "https://...",
  "textData": "Full blog content...",
  "status": "draft",
  "createdAt": "2025-12-26T00:00:00.000Z",
  "workspace": {
    "id": "workspace-uuid",
    "name": "Marketing Workspace"
  }
}
```

---

#### List Workspace Content
```http
GET /content/workspace/:workspaceId?type=blog&status=draft
```

**Query Parameters:**
- `type` (optional): Filter by type (`blog`, `image`, `caption`, `doc`)
- `status` (optional): Filter by status (`draft`, `approved`, `used`, `posted`)

**Response (200):**
```json
[
  {
    "id": "content-1",
    "workspaceId": "workspace-uuid",
    "type": "blog",
    "s3Url": "https://...",
    "textData": "Content...",
    "status": "draft",
    "createdAt": "2025-12-26T00:00:00.000Z"
  }
]
```

**Frontend Usage:**
```typescript
const getWorkspaceContent = async (
  workspaceId: string,
  filters?: { type?: string; status?: string }
) => {
  const params = new URLSearchParams();
  if (filters?.type) params.append('type', filters.type);
  if (filters?.status) params.append('status', filters.status);
  
  const response = await apiClient.get(
    `/content/workspace/${workspaceId}?${params.toString()}`
  );
  return response.data;
};
```

---

#### Update Content Status
```http
POST /content/:id/status
```

**Request Body:**
```json
{
  "status": "approved"
}
```

**Response (200):**
```json
{
  "id": "content-uuid",
  "status": "approved",
  "...": "other fields"
}
```

**Frontend Usage:**
```typescript
const updateContentStatus = async (contentId: string, status: string) => {
  const response = await apiClient.post(`/content/${contentId}/status`, {
    status,
  });
  return response.data;
};
```

---

### 3. Workflows (MCP Core)

#### Create Workflow
```http
POST /workflows
```

**Request Body:**
```json
{
  "workspaceId": "workspace-uuid",
  "name": "Blog Generation Workflow",
  "description": "Generate a blog post about AI",
  "steps": [
    {
      "tool": "generate_blog",
      "input": {
        "workspaceId": "workspace-uuid",
        "topic": "AI in Marketing",
        "tone": "professional",
        "length": 1000
      }
    }
  ]
}
```

**Available Tools:**
- `generate_blog`: Generate blog content
- `generate_image`: Generate images

**Response (201):**
```json
{
  "id": "workflow-uuid",
  "workspaceId": "workspace-uuid",
  "name": "Blog Generation Workflow",
  "description": "Generate a blog post about AI",
  "steps": [...],
  "createdAt": "2025-12-26T00:00:00.000Z"
}
```

**Frontend Usage:**
```typescript
const createWorkflow = async (workflowData: {
  workspaceId: string;
  name: string;
  description?: string;
  steps: Array<{
    tool: string;
    input?: Record<string, any>;
  }>;
}) => {
  const response = await apiClient.post('/workflows', workflowData);
  return response.data;
};
```

---

#### Get Workflow
```http
GET /workflows/:id
```

**Response (200):**
```json
{
  "id": "workflow-uuid",
  "workspaceId": "workspace-uuid",
  "name": "Blog Generation Workflow",
  "description": "Generate a blog post",
  "steps": [
    {
      "tool": "generate_blog",
      "input": {
        "topic": "AI in Marketing"
      }
    }
  ],
  "createdAt": "2025-12-26T00:00:00.000Z"
}
```

---

#### List Workspace Workflows
```http
GET /workflows/workspace/:workspaceId
```

**Response (200):**
```json
[
  {
    "id": "workflow-1",
    "workspaceId": "workspace-uuid",
    "name": "Blog Generation",
    "description": "...",
    "steps": [...],
    "createdAt": "2025-12-26T00:00:00.000Z"
  }
]
```

---

#### Execute Workflow (⭐ MCP Core)
```http
POST /workflows/:id/run
```

**This is the main execution endpoint that triggers MCP.**

**Response (200):**
```json
{
  "message": "Workflow execution started",
  "jobId": "job-uuid",
  "status": "pending"
}
```

**Frontend Usage:**
```typescript
const executeWorkflow = async (workflowId: string) => {
  const response = await apiClient.post(`/workflows/${workflowId}/run`);
  return response.data;
};
```

**Then poll for job status:**
```typescript
const pollJobStatus = async (jobId: string) => {
  const response = await apiClient.get(`/jobs/${jobId}`);
  return response.data;
};

// Poll every 2 seconds
const waitForJobCompletion = async (jobId: string) => {
  let status = 'pending';
  
  while (status === 'pending' || status === 'running') {
    await new Promise(resolve => setTimeout(resolve, 2000));
    const job = await pollJobStatus(jobId);
    status = job.status;
    
    if (status === 'completed') {
      return job;
    } else if (status === 'failed') {
      throw new Error('Job failed');
    }
  }
};
```

---

### 4. Jobs (Execution Tracking)

#### Get Job Status
```http
GET /jobs/:id
```

**Response (200):**
```json
{
  "id": "job-uuid",
  "workflowId": "workflow-uuid",
  "status": "completed",
  "logs": [
    {
      "timestamp": "2025-12-26T00:00:00.000Z",
      "step": 1,
      "tool": "generate_blog",
      "status": "started"
    },
    {
      "timestamp": "2025-12-26T00:00:05.000Z",
      "step": 1,
      "tool": "generate_blog",
      "status": "completed",
      "output": {
        "contentId": "content-uuid",
        "title": "AI in Marketing",
        "s3Url": "https://..."
      }
    }
  ],
  "startedAt": "2025-12-26T00:00:00.000Z",
  "finishedAt": "2025-12-26T00:00:05.000Z",
  "createdAt": "2025-12-26T00:00:00.000Z",
  "workflow": {
    "id": "workflow-uuid",
    "name": "Blog Generation"
  }
}
```

**Job Statuses:**
- `pending`: Job created, not started
- `running`: Currently executing
- `completed`: Successfully finished
- `failed`: Error occurred

---

#### Get Workflow Jobs
```http
GET /jobs/workflow/:workflowId
```

**Response (200):**
```json
[
  {
    "id": "job-1",
    "workflowId": "workflow-uuid",
    "status": "completed",
    "startedAt": "2025-12-26T00:00:00.000Z",
    "finishedAt": "2025-12-26T00:00:05.000Z",
    "createdAt": "2025-12-26T00:00:00.000Z"
  }
]
```

---

## 📝 TypeScript Types

### Interface Definitions

```typescript
// types/api.ts

export interface Workspace {
  id: string;
  ownerUserId: string;
  name: string;
  createdAt: string;
  owner?: User;
}

export interface User {
  id: string;
  name: string;
  email: string;
  createdAt: string;
}

export interface Content {
  id: string;
  workspaceId: string;
  type: 'blog' | 'image' | 'caption' | 'doc';
  s3Url: string | null;
  textData: string | null;
  status: 'draft' | 'approved' | 'used' | 'posted';
  createdAt: string;
  workspace?: Workspace;
}

export interface WorkflowStep {
  tool: string;
  input?: Record<string, any>;
}

export interface Workflow {
  id: string;
  workspaceId: string;
  name: string;
  description?: string;
  steps: WorkflowStep[];
  createdAt: string;
}

export interface JobLog {
  timestamp: string;
  step?: number;
  tool?: string;
  status: string;
  output?: any;
  error?: string;
}

export interface Job {
  id: string;
  workflowId: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  logs: JobLog[];
  startedAt: string | null;
  finishedAt: string | null;
  createdAt: string;
  workflow?: Workflow;
}

export interface ApiError {
  statusCode: number;
  message: string | string[];
  error: string;
}
```

---

## 💻 Integration Examples

### Complete React Hook Example

```typescript
// hooks/useWorkflow.ts
import { useState } from 'react';
import { apiClient } from '@/config/api';
import { Workflow, Job } from '@/types/api';

export const useWorkflow = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createAndRunWorkflow = async (
    workspaceId: string,
    topic: string
  ): Promise<{ workflow: Workflow; job: Job }> => {
    try {
      setLoading(true);
      setError(null);

      // 1. Create workflow
      const workflowResponse = await apiClient.post('/workflows', {
        workspaceId,
        name: `Blog: ${topic}`,
        description: `Generate blog about ${topic}`,
        steps: [
          {
            tool: 'generate_blog',
            input: {
              workspaceId,
              topic,
              tone: 'professional',
            },
          },
        ],
      });

      const workflow = workflowResponse.data;

      // 2. Execute workflow
      const executeResponse = await apiClient.post(
        `/workflows/${workflow.id}/run`
      );

      const { jobId } = executeResponse.data;

      // 3. Poll for completion
      const job = await pollJobUntilComplete(jobId);

      return { workflow, job };
    } catch (err: any) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const pollJobUntilComplete = async (jobId: string): Promise<Job> => {
    let attempts = 0;
    const maxAttempts = 60; // 2 minutes max

    while (attempts < maxAttempts) {
      const response = await apiClient.get(`/jobs/${jobId}`);
      const job: Job = response.data;

      if (job.status === 'completed') {
        return job;
      }

      if (job.status === 'failed') {
        throw new Error('Job execution failed');
      }

      // Wait 2 seconds before next poll
      await new Promise((resolve) => setTimeout(resolve, 2000));
      attempts++;
    }

    throw new Error('Job execution timeout');
  };

  return {
    createAndRunWorkflow,
    loading,
    error,
  };
};
```

### React Component Example

```typescript
// components/ContentGenerator.tsx
import React, { useState } from 'react';
import { useWorkflow } from '@/hooks/useWorkflow';

export const ContentGenerator: React.FC<{ workspaceId: string }> = ({
  workspaceId,
}) => {
  const [topic, setTopic] = useState('');
  const [generatedContent, setGeneratedContent] = useState<any>(null);
  const { createAndRunWorkflow, loading, error } = useWorkflow();

  const handleGenerate = async () => {
    try {
      const { workflow, job } = await createAndRunWorkflow(workspaceId, topic);

      // Extract content ID from job logs
      const blogLog = job.logs.find(
        (log) => log.tool === 'generate_blog' && log.output
      );

      if (blogLog?.output?.contentId) {
        // Fetch the generated content
        const contentResponse = await fetch(
          `http://localhost:3000/content/${blogLog.output.contentId}`
        );
        const content = await contentResponse.json();
        setGeneratedContent(content);
      }
    } catch (err) {
      console.error('Generation failed:', err);
    }
  };

  return (
    <div>
      <input
        type="text"
        value={topic}
        onChange={(e) => setTopic(e.target.value)}
        placeholder="Enter topic..."
      />
      <button onClick={handleGenerate} disabled={loading}>
        {loading ? 'Generating...' : 'Generate Content'}
      </button>

      {error && <div className="error">{error}</div>}

      {generatedContent && (
        <div>
          <h3>{generatedContent.textData}</h3>
          <a href={generatedContent.s3Url} target="_blank">
            View on S3
          </a>
        </div>
      )}
    </div>
  );
};
```

### Vue 3 Composition API Example

```typescript
// composables/useWorkflow.ts
import { ref } from 'vue';
import axios from 'axios';

export const useWorkflow = () => {
  const loading = ref(false);
  const error = ref<string | null>(null);

  const executeWorkflow = async (workspaceId: string, topic: string) => {
    loading.value = true;
    error.value = null;

    try {
      // Create workflow
      const { data: workflow } = await axios.post('http://localhost:3000/workflows', {
        workspaceId,
        name: `Generate: ${topic}`,
        steps: [
          {
            tool: 'generate_blog',
            input: { workspaceId, topic },
          },
        ],
      });

      // Execute
      const { data: execution } = await axios.post(
        `http://localhost:3000/workflows/${workflow.id}/run`
      );

      // Poll for result
      let status = 'pending';
      while (status === 'pending' || status === 'running') {
        await new Promise((r) => setTimeout(r, 2000));
        const { data: job } = await axios.get(
          `http://localhost:3000/jobs/${execution.jobId}`
        );
        status = job.status;

        if (status === 'completed') {
          return job;
        }
      }
    } catch (err: any) {
      error.value = err.message;
      throw err;
    } finally {
      loading.value = false;
    }
  };

  return {
    loading,
    error,
    executeWorkflow,
  };
};
```

---

## ⚠️ Error Handling

### Error Response Format

```json
{
  "statusCode": 400,
  "message": "Validation failed",
  "error": "Bad Request"
}
```

or

```json
{
  "statusCode": 404,
  "message": "Workspace abc123 not found",
  "error": "Not Found"
}
```

### Frontend Error Handling

```typescript
// utils/errorHandler.ts
export const handleApiError = (error: any): string => {
  if (error.response) {
    // Server responded with error
    const { status, data } = error.response;

    if (status === 400) {
      return Array.isArray(data.message)
        ? data.message.join(', ')
        : data.message;
    }

    if (status === 404) {
      return 'Resource not found';
    }

    if (status === 500) {
      return 'Server error. Please try again later.';
    }

    return data.message || 'An error occurred';
  }

  if (error.request) {
    // Request made but no response
    return 'Network error. Please check your connection.';
  }

  return error.message || 'An unexpected error occurred';
};

// Usage in component
try {
  await createWorkflow(data);
} catch (error) {
  const message = handleApiError(error);
  setError(message);
}
```

---

## 🎯 Best Practices

### 1. Use Environment Variables

```typescript
// .env.local
REACT_APP_API_URL=http://localhost:3000
REACT_APP_API_TIMEOUT=30000

// config/api.ts
export const API_CONFIG = {
  baseURL: process.env.REACT_APP_API_URL,
  timeout: Number(process.env.REACT_APP_API_TIMEOUT),
};
```

### 2. Centralize API Calls

```typescript
// services/api.ts
import axios from 'axios';
import { API_CONFIG } from '@/config/api';

const apiClient = axios.create(API_CONFIG);

export const workspaceApi = {
  create: (data: CreateWorkspaceDto) => 
    apiClient.post('/workspaces', data),
  get: (id: string) => 
    apiClient.get(`/workspaces/${id}`),
  list: (userId: string) => 
    apiClient.get(`/workspaces/user/${userId}`),
};

export const contentApi = {
  list: (workspaceId: string, filters?: any) =>
    apiClient.get(`/content/workspace/${workspaceId}`, { params: filters }),
  get: (id: string) =>
    apiClient.get(`/content/${id}`),
  updateStatus: (id: string, status: string) =>
    apiClient.post(`/content/${id}/status`, { status }),
};

export const workflowApi = {
  create: (data: CreateWorkflowDto) =>
    apiClient.post('/workflows', data),
  execute: (id: string) =>
    apiClient.post(`/workflows/${id}/run`),
  get: (id: string) =>
    apiClient.get(`/workflows/${id}`),
  list: (workspaceId: string) =>
    apiClient.get(`/workflows/workspace/${workspaceId}`),
};

export const jobApi = {
  get: (id: string) =>
    apiClient.get(`/jobs/${id}`),
  listByWorkflow: (workflowId: string) =>
    apiClient.get(`/jobs/workflow/${workflowId}`),
};
```

### 3. Handle Loading States

```typescript
const [state, setState] = useState({
  loading: false,
  error: null,
  data: null,
});

const fetchData = async () => {
  setState({ loading: true, error: null, data: null });
  
  try {
    const response = await apiClient.get('/endpoint');
    setState({ loading: false, error: null, data: response.data });
  } catch (error) {
    setState({ loading: false, error: error.message, data: null });
  }
};
```

### 4. Implement Request Interceptors

```typescript
// Add request interceptor for auth tokens (future)
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

### 5. Use React Query (Recommended)

```typescript
// hooks/useWorkspaces.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { workspaceApi } from '@/services/api';

export const useWorkspaces = (userId: string) => {
  return useQuery({
    queryKey: ['workspaces', userId],
    queryFn: () => workspaceApi.list(userId).then(res => res.data),
  });
};

export const useCreateWorkspace = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: workspaceApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspaces'] });
    },
  });
};
```

---

## 🔒 Security Notes

### Current State
- ✅ CORS enabled
- ✅ Input validation with class-validator
- ⏳ Authentication pending (will use JWT)

### Future Authentication

When JWT authentication is added:

```typescript
// Login will return token
const login = async (email: string, password: string) => {
  const response = await apiClient.post('/auth/login', { email, password });
  localStorage.setItem('auth_token', response.data.token);
  return response.data;
};

// Add to all requests
apiClient.defaults.headers.common['Authorization'] = 
  `Bearer ${localStorage.getItem('auth_token')}`;
```

---

## 📞 Support & Questions

For backend issues or questions:
1. Check [ARCHITECTURE.md](./ARCHITECTURE.md) for system design
2. Review [TESTING.md](./TESTING.md) for debugging
3. See [API_EXAMPLES.md](./API_EXAMPLES.md) for curl examples

---

## 🎯 Quick Reference

### Common Workflow

```typescript
// 1. Get user's workspaces
const workspaces = await workspaceApi.list(userId);

// 2. Create workflow
const workflow = await workflowApi.create({
  workspaceId: workspaces[0].id,
  name: 'Blog Generator',
  steps: [{ tool: 'generate_blog', input: { topic: 'AI' } }]
});

// 3. Execute workflow
const { jobId } = await workflowApi.execute(workflow.id);

// 4. Poll for completion
const job = await pollUntilComplete(jobId);

// 5. Get generated content
const contentId = job.logs.find(l => l.output?.contentId)?.output?.contentId;
const content = await contentApi.get(contentId);
```

---

**Built with ❤️ by MCP Hub Team**  
**Last Updated**: December 26, 2025
