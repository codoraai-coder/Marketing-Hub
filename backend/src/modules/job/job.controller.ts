import { Controller, Get, Param } from '@nestjs/common';
import { JobService } from './job.service';

@Controller('jobs')
export class JobController {
  constructor(private readonly jobService: JobService) {}

  /**
   * Get job status and logs
   * Frontend polls this to track workflow execution
   */
  @Get(':id')
  async getJobStatus(@Param('id') id: string) {
    return this.jobService.getJobStatus(id);
  }

  @Get('workflow/:workflowId')
  async getJobsByWorkflow(@Param('workflowId') workflowId: string) {
    return this.jobService.getJobsByWorkflow(workflowId);
  }
}
