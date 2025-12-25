# MCP Hub Backend - Testing Guide

## Manual Testing Steps

### 1. Setup Test Environment

```bash
# Start databases
./setup.sh

# Start backend
npm run start:dev

# In another terminal
export BASE_URL="http://localhost:3000"
```

### 2. Test Workspace Creation

```bash
# Create a workspace
curl -X POST $BASE_URL/workspaces \
  -H "Content-Type: application/json" \
  -d '{
    "ownerUserId": "00000000-0000-0000-0000-000000000001",
    "name": "Test Workspace"
  }' | jq

# Save the workspace ID
export WORKSPACE_ID="<paste-workspace-id-here>"
```

### 3. Test Workflow Creation

```bash
# Create a simple workflow
curl -X POST $BASE_URL/workflows \
  -H "Content-Type: application/json" \
  -d "{
    \"workspaceId\": \"$WORKSPACE_ID\",
    \"name\": \"Test Blog Generation\",
    \"description\": \"Generate a test blog\",
    \"steps\": [
      {
        \"tool\": \"generate_blog\",
        \"input\": {
          \"workspaceId\": \"$WORKSPACE_ID\",
          \"topic\": \"Test Topic\",
          \"tone\": \"professional\"
        }
      }
    ]
  }" | jq

# Save the workflow ID
export WORKFLOW_ID="<paste-workflow-id-here>"
```

### 4. Test MCP Execution

```bash
# Run the workflow
curl -X POST $BASE_URL/workflows/$WORKFLOW_ID/run | jq

# Save the job ID
export JOB_ID="<paste-job-id-here>"
```

### 5. Monitor Job Execution

```bash
# Check job status (run multiple times)
curl $BASE_URL/jobs/$JOB_ID | jq

# Check until status is "completed" or "failed"
watch -n 1 "curl -s $BASE_URL/jobs/$JOB_ID | jq '.status'"
```

### 6. Verify Content Creation

```bash
# List all content in workspace
curl "$BASE_URL/content/workspace/$WORKSPACE_ID" | jq

# Get specific content
export CONTENT_ID="<paste-content-id-from-job-logs>"
curl $BASE_URL/content/$CONTENT_ID | jq
```

### 7. Test Content Status Update

```bash
# Update content status
curl -X POST $BASE_URL/content/$CONTENT_ID/status \
  -H "Content-Type: application/json" \
  -d '{
    "status": "approved"
  }' | jq
```

### 8. Test Complex Workflow

```bash
# Create workflow with multiple steps
curl -X POST $BASE_URL/workflows \
  -H "Content-Type: application/json" \
  -d "{
    \"workspaceId\": \"$WORKSPACE_ID\",
    \"name\": \"Blog + Image\",
    \"description\": \"Generate blog and image\",
    \"steps\": [
      {
        \"tool\": \"generate_blog\",
        \"input\": {
          \"workspaceId\": \"$WORKSPACE_ID\",
          \"topic\": \"AI Marketing\",
          \"tone\": \"professional\"
        }
      },
      {
        \"tool\": \"generate_image\",
        \"input\": {
          \"workspaceId\": \"$WORKSPACE_ID\",
          \"prompt\": \"AI marketing visualization\"
        }
      }
    ]
  }" | jq

# Run and monitor as above
```

## Expected Results

### Successful Workflow Execution

1. Job status progresses: `pending` → `running` → `completed`
2. Job logs show each step execution
3. Content records are created in database
4. S3 URLs are generated (when S3 is configured)

### Error Scenarios

#### Missing Tool
```json
{
  "status": "failed",
  "logs": [
    {
      "error": "Tool not found"
    }
  ]
}
```

#### Invalid Input
```json
{
  "statusCode": 400,
  "message": ["workspaceId must be a UUID"],
  "error": "Bad Request"
}
```

## Database Verification

```bash
# Connect to PostgreSQL
docker exec -it mcp-postgres psql -U postgres -d mcp_hub

# Check tables
\dt

# View workspaces
SELECT * FROM workspaces;

# View workflows
SELECT * FROM workflows;

# View jobs
SELECT id, workflow_id, status FROM jobs;

# View content
SELECT id, workspace_id, type, status FROM contents;

# Exit
\q
```

## Testing Checklist

- [ ] Backend starts without errors
- [ ] Can create workspace
- [ ] Can create workflow
- [ ] Can run workflow
- [ ] Job executes and completes
- [ ] Content is created
- [ ] Can query job status
- [ ] Can list content
- [ ] Can update content status
- [ ] Multi-step workflow works
- [ ] Error handling works

## Common Issues

### Database Connection Failed
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Restart if needed
docker start mcp-postgres

# Check connection
docker exec -it mcp-postgres psql -U postgres -d mcp_hub -c "SELECT 1;"
```

### S3 Upload Failed
```bash
# Check .env configuration
cat .env | grep AWS

# Test with placeholder: S3 errors won't crash the system
# Content will be saved to database even if S3 fails
```

### Tool Not Found
```bash
# Check logs
npm run start:dev | grep "Tool registered"

# Should see:
# Tool registered: generate_blog
# Tool registered: generate_image
```

## Performance Testing

```bash
# Create multiple workflows rapidly
for i in {1..10}; do
  curl -X POST $BASE_URL/workflows \
    -H "Content-Type: application/json" \
    -d "{\"workspaceId\":\"$WORKSPACE_ID\",\"name\":\"Test $i\",\"steps\":[{\"tool\":\"generate_blog\",\"input\":{\"workspaceId\":\"$WORKSPACE_ID\",\"topic\":\"Test $i\"}}]}"
  echo ""
done

# Monitor system
watch -n 1 "curl -s $BASE_URL/jobs/workflow/* | jq '.[] | {id, status}'"
```

## Integration Testing

See test scripts in `test/` directory:
```bash
# Run unit tests
npm run test

# Run e2e tests
npm run test:e2e

# Run with coverage
npm run test:cov
```

## Next Steps

Once basic testing passes:
1. Integrate actual AI models
2. Configure real S3 bucket
3. Add authentication
4. Deploy to staging environment
