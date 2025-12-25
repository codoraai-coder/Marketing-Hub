# API Examples for MCP Hub

## Base URL
```
http://localhost:3000
```

## 1. Create a Workspace

```bash
curl -X POST http://localhost:3000/workspaces \
  -H "Content-Type: application/json" \
  -d '{
    "ownerUserId": "user-uuid-here",
    "name": "My Marketing Workspace"
  }'
```

Response:
```json
{
  "id": "workspace-uuid",
  "ownerUserId": "user-uuid-here",
  "name": "My Marketing Workspace",
  "createdAt": "2025-12-26T00:00:00.000Z"
}
```

## 2. Create a Workflow

```bash
curl -X POST http://localhost:3000/workflows \
  -H "Content-Type: application/json" \
  -d '{
    "workspaceId": "workspace-uuid",
    "name": "Blog Generation",
    "description": "Generate a blog post about AI",
    "steps": [
      {
        "tool": "generate_blog",
        "input": {
          "workspaceId": "workspace-uuid",
          "topic": "The Future of AI in Marketing",
          "tone": "professional"
        }
      }
    ]
  }'
```

Response:
```json
{
  "id": "workflow-uuid",
  "workspaceId": "workspace-uuid",
  "name": "Blog Generation",
  "description": "Generate a blog post about AI",
  "steps": [...],
  "createdAt": "2025-12-26T00:00:00.000Z"
}
```

## 3. Run a Workflow (MCP Execution)

```bash
curl -X POST http://localhost:3000/workflows/workflow-uuid/run
```

Response:
```json
{
  "message": "Workflow execution started",
  "jobId": "job-uuid",
  "status": "pending"
}
```

## 4. Check Job Status

```bash
curl http://localhost:3000/jobs/job-uuid
```

Response:
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
        "title": "The Future of AI in Marketing",
        "s3Url": "https://..."
      }
    }
  ],
  "startedAt": "2025-12-26T00:00:00.000Z",
  "finishedAt": "2025-12-26T00:00:05.000Z"
}
```

## 5. Get Content

```bash
curl http://localhost:3000/content/content-uuid
```

Response:
```json
{
  "id": "content-uuid",
  "workspaceId": "workspace-uuid",
  "type": "blog",
  "s3Url": "https://bucket.s3.amazonaws.com/blogs/...",
  "textData": "# The Future of AI in Marketing\n\n...",
  "status": "draft",
  "createdAt": "2025-12-26T00:00:00.000Z"
}
```

## 6. List Workspace Content

```bash
# All content
curl http://localhost:3000/content/workspace/workspace-uuid

# Filter by type
curl http://localhost:3000/content/workspace/workspace-uuid?type=blog

# Filter by status
curl http://localhost:3000/content/workspace/workspace-uuid?status=draft
```

## 7. Update Content Status

```bash
curl -X POST http://localhost:3000/content/content-uuid/status \
  -H "Content-Type: application/json" \
  -d '{
    "status": "approved"
  }'
```

## 8. Complex Workflow (Blog + Image)

```bash
curl -X POST http://localhost:3000/workflows \
  -H "Content-Type: application/json" \
  -d '{
    "workspaceId": "workspace-uuid",
    "name": "Blog with Image",
    "description": "Generate blog and accompanying image",
    "steps": [
      {
        "tool": "generate_blog",
        "input": {
          "workspaceId": "workspace-uuid",
          "topic": "AI in Marketing",
          "tone": "professional",
          "length": 1000
        }
      },
      {
        "tool": "generate_image",
        "input": {
          "workspaceId": "workspace-uuid",
          "prompt": "AI marketing visualization, professional, modern",
          "style": "professional"
        }
      }
    ]
  }'
```

## 9. List All Workflows

```bash
curl http://localhost:3000/workflows/workspace/workspace-uuid
```

## 10. Get Workflow Jobs

```bash
curl http://localhost:3000/jobs/workflow/workflow-uuid
```

## Error Responses

### 404 Not Found
```json
{
  "statusCode": 404,
  "message": "Workflow abc123 not found",
  "error": "Not Found"
}
```

### 400 Bad Request
```json
{
  "statusCode": 400,
  "message": ["workspaceId must be a UUID"],
  "error": "Bad Request"
}
```

## Notes

1. Replace `workspace-uuid`, `workflow-uuid`, `job-uuid`, `content-uuid` with actual IDs
2. Add authentication headers when auth is implemented
3. All timestamps are in ISO 8601 format
4. Job status values: `pending`, `running`, `completed`, `failed`
5. Content status values: `draft`, `approved`, `used`, `posted`
6. Content types: `blog`, `image`, `caption`, `doc`

## Integration Example (JavaScript)

```javascript
// Create workflow and run it
async function runContentGeneration() {
  // 1. Create workflow
  const workflow = await fetch('http://localhost:3000/workflows', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      workspaceId: 'workspace-uuid',
      name: 'Quick Blog',
      steps: [
        {
          tool: 'generate_blog',
          input: {
            workspaceId: 'workspace-uuid',
            topic: 'AI Marketing'
          }
        }
      ]
    })
  }).then(r => r.json());

  // 2. Run workflow
  const job = await fetch(`http://localhost:3000/workflows/${workflow.id}/run`, {
    method: 'POST'
  }).then(r => r.json());

  // 3. Poll job status
  let status = 'pending';
  while (status === 'pending' || status === 'running') {
    await new Promise(r => setTimeout(r, 1000)); // Wait 1 second
    const jobStatus = await fetch(`http://localhost:3000/jobs/${job.jobId}`)
      .then(r => r.json());
    status = jobStatus.status;
    console.log('Status:', status);
  }

  // 4. Get generated content
  if (status === 'completed') {
    const contentId = /* extract from job logs */;
    const content = await fetch(`http://localhost:3000/content/${contentId}`)
      .then(r => r.json());
    console.log('Content generated:', content);
  }
}
```

## Testing with Postman

Import these endpoints into Postman:

1. Create a Postman Collection
2. Add environment variables:
   - `BASE_URL`: http://localhost:3000
   - `WORKSPACE_ID`: your-workspace-uuid
3. Create requests for each endpoint above
4. Use `{{BASE_URL}}` and `{{WORKSPACE_ID}}` in requests
