import { Controller, Get, Post, Body, Param } from '@nestjs/common';
import { WorkflowService } from './workflow.service';
import { CreateWorkflowDto } from './dto/create-workflow.dto';
import { ExecutionEngineService } from '../../mcp/execution-engine.service';

@Controller('workflows')
export class WorkflowController {
  constructor(
    private readonly workflowService: WorkflowService,
    private readonly executionEngine: ExecutionEngineService,
  ) {}

  @Post()
  async create(@Body() createWorkflowDto: CreateWorkflowDto) {
    return this.workflowService.create(createWorkflowDto);
  }

  @Get(':id')
  async findOne(@Param('id') id: string) {
    return this.workflowService.findOne(id);
  }

  @Get('workspace/:workspaceId')
  async findByWorkspace(@Param('workspaceId') workspaceId: string) {
    return this.workflowService.findByWorkspace(workspaceId);
  }

  /**
   * MCP EXECUTION ENDPOINT - This is the heart of the system
   * Frontend expresses intent: "run this workflow"
   * MCP decides execution
   */
  @Post(':id/run')
  async runWorkflow(@Param('id') id: string) {
    const job = await this.executionEngine.executeWorkflow(id);
    return {
      message: 'Workflow execution started',
      jobId: job.id,
      status: job.status,
    };
  }
}
