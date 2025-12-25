# MCP Hub Backend - Architecture Documentation

## Master Control Program (MCP) Design

### Philosophy

The backend is **NOT**:
- An AI playground
- A set of endpoints calling models
- A proxy to AI services

The backend **IS**:
- A Master Control Program (MCP)
- The single source of truth
- A deterministic orchestration engine

### Core Principles

1. **Centralized Control**: All logic flows through MCP
2. **Tool-Based Architecture**: Capabilities are registered as tools
3. **Traceability**: Every output is stored and linked
4. **Intent-Based APIs**: Frontend expresses intent, MCP decides execution
5. **No Bypass**: No feature can bypass MCP logic

## Component Breakdown

### 1. Tool Registry (`ToolRegistryService`)

**Purpose**: Central registry of all system capabilities

**Responsibilities**:
- Register tools with schemas
- Validate tool inputs
- Execute tools
- Return standardized results

**Tools**: Conceptually, anything the system can do:
- `generate_blog`: Existing blog generation model
- `generate_image`: Existing image generation model
- Future: `post_to_linkedin`, `convert_to_instagram`, etc.

### 2. Execution Engine (`ExecutionEngineService`)

**Purpose**: Orchestrates workflow execution

**Flow**:
```
1. Receive workflow ID
2. Create Job (status: pending)
3. Load workflow steps
4. For each step:
   a. Call Tool Registry
   b. Execute tool
   c. Store output
   d. Update logs
5. Mark job completed/failed
```

**Key**: This is the heart of MCP

### 3. State Manager (`StateManagerService`)

**Purpose**: Track execution state across steps

**Use Case**: Multi-step workflows where step N needs output from step N-1

**Example**:
```
Step 1: generate_blog → outputs { blogId, content }
Step 2: generate_image → uses blogId from Step 1
```

### 4. Workflow Loader (`WorkflowLoaderService`)

**Purpose**: Load and validate workflow definitions

**Validation**:
- All tools exist in registry
- Required inputs are provided
- Steps are valid

## Data Model Details

### Content Table (Critical)

**Purpose**: Bridge between S3 and system

**Rule**: Every S3 object MUST have a Content record

**Fields**:
- `type`: blog | image | caption | doc
- `s3_url`: Link to S3 object (nullable for text-only)
- `text_data`: Inline text (nullable for images)
- `status`: draft | approved | used | posted

**Why**: This enables:
- Content lifecycle tracking
- Reusability
- Analytics linkage
- Audit trail

### Workflow Table

**Purpose**: Define what MCP should do

**Structure**:
```json
{
  "name": "Blog Generation Workflow",
  "steps": [
    { "tool": "generate_blog", "input": { "topic": "AI" } }
  ]
}
```

**Key**: Workflows are data, not code

### Job Table

**Purpose**: Track execution

**Lifecycle**:
1. Created (pending)
2. Picked by worker (running)
3. Steps execute (logs updated)
4. Finished (completed | failed)

**Why**: Enables:
- Async execution
- Progress tracking
- Error debugging
- Job history

## Tool Integration Pattern

### Wrapping Existing Models

Existing models (blog gen, image gen) are wrapped as tools:

```typescript
@Injectable()
export class GenerateBlogTool {
  async execute(input: BlogInput): Promise<BlogOutput> {
    // 1. Call existing model
    const content = await existingBlogModel(input);
    
    // 2. Store in S3
    const s3Url = await s3.upload(content);
    
    // 3. Create Content record
    const record = await contentRepo.create({
      type: 'blog',
      s3Url,
      textData: content,
    });
    
    // 4. Return traceable output
    return { contentId: record.id, s3Url };
  }
}
```

**Key**: Tools own the lifecycle:
1. Generate
2. Store
3. Record
4. Return

## API Philosophy

### Bad (Tool-Based)
```
POST /generateBlog
POST /generateImage
```

### Good (Intent-Based)
```
POST /content
POST /workflows/{id}/run
GET /jobs/{id}
```

**Why**: Frontend expresses intent ("run this workflow"), MCP decides execution

## Execution Model

### Current: Synchronous
For simplicity, jobs execute immediately after creation

### Future: Async with Bull Queue

```
POST /workflows/{id}/run
   ↓
Job created → Redis Queue
   ↓
Worker picks job → Executes → Updates DB
   ↓
Frontend polls GET /jobs/{id}
```

## Extensibility

### Adding a New Tool

1. Create tool class:
```typescript
@Injectable()
export class MyNewTool {
  async execute(input: MyInput): Promise<MyOutput> {
    // Implementation
  }
}
```

2. Register in `ToolInitializerService`:
```typescript
this.toolRegistry.registerTool({
  name: 'my_new_tool',
  inputSchema: { ... },
  outputSchema: { ... },
  executor: (input) => this.myNewTool.execute(input),
});
```

3. Use in workflows:
```json
{
  "steps": [
    { "tool": "my_new_tool", "input": { ... } }
  ]
}
```

**No API changes needed**

### Adding a New Module

1. Create module following NestJS patterns
2. Inject MCP services as needed
3. Expose intent-based APIs
4. Let MCP handle execution

## Error Handling

### Tool Execution Failure

1. Tool returns `{ success: false, error: "..." }`
2. Execution engine logs error
3. Job marked as failed
4. Frontend notified via job status

### Job Recovery

Future: Implement retry logic in Bull queue

## Security Considerations

### Future: Authentication
- JWT-based auth
- User → Workspace ownership
- Row-level security

### Current: Trust Model
- API assumes valid workspace IDs
- Add auth before production

## Performance Considerations

### Database
- Index on `workspace_id` for all tables
- Index on job `status` for queue queries
- Use connection pooling

### S3
- Async uploads
- Pre-signed URLs for downloads
- CDN for public content

### Redis (Future)
- Job queue for async execution
- Cache for frequently accessed data

## Monitoring & Observability

### Logging
- Structured logging with timestamps
- Job logs stored in database
- Tool execution tracked

### Metrics (Future)
- Job success/failure rates
- Tool execution times
- Queue depth

## Migration Path

### From Demo to Production

1. ✅ Add PostgreSQL
2. ✅ Create entities
3. ✅ Build MCP core
4. ✅ Integrate existing tools
5. ⏳ Add Bull queue
6. ⏳ Implement auth
7. ⏳ Add social posting
8. ⏳ Implement analytics

## Testing Strategy

### Unit Tests
- Test each tool independently
- Mock S3 and database
- Validate schemas

### Integration Tests
- Test full workflow execution
- Test job lifecycle
- Test error scenarios

### E2E Tests
- Test API endpoints
- Test workflow creation → execution → job status
- Test content lifecycle

## Deployment

### Development
```bash
npm run start:dev
```

### Production
```bash
npm run build
npm run start:prod
```

### Docker
```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY dist ./dist
CMD ["node", "dist/main"]
```

## Conclusion

The MCP architecture ensures:
- ✅ All logic is centralized
- ✅ All outputs are traceable
- ✅ Frontend is decoupled from AI
- ✅ System is extensible
- ✅ Workflows are data-driven

This is a **real system**, not a demo.
