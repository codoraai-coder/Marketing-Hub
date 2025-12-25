import { Injectable, Logger } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Job, JobStatus } from '../entities/job.entity';
import { Workflow } from '../entities/workflow.entity';
import { ToolRegistryService } from './tool-registry.service';
import { StateManagerService } from './state-manager.service';

@Injectable()
export class ExecutionEngineService {
  private readonly logger = new Logger(ExecutionEngineService.name);

  constructor(
    @InjectRepository(Job)
    private readonly jobRepository: Repository<Job>,
    @InjectRepository(Workflow)
    private readonly workflowRepository: Repository<Workflow>,
    private readonly toolRegistry: ToolRegistryService,
    private readonly stateManager: StateManagerService,
  ) {}

  /**
   * Execute a workflow by creating and running a job
   * This is the heart of MCP
   */
  async executeWorkflow(workflowId: string): Promise<Job> {
    // Load workflow
    const workflow = await this.workflowRepository.findOne({
      where: { id: workflowId },
    });

    if (!workflow) {
      throw new Error(`Workflow ${workflowId} not found`);
    }

    // Create job (status: pending)
    const job = this.jobRepository.create({
      workflowId: workflow.id,
      status: JobStatus.PENDING,
      logs: [],
    });
    await this.jobRepository.save(job);

    this.logger.log(`Job ${job.id} created for workflow ${workflow.name}`);

    // Execute asynchronously (in real implementation, this would be picked by a worker)
    this.runJob(job.id, workflow).catch((error) => {
      this.logger.error(`Job ${job.id} failed: ${error.message}`);
    });

    return job;
  }

  /**
   * Run a job - executes all workflow steps in order
   * This method would typically be called by a Bull worker
   */
  private async runJob(jobId: string, workflow: Workflow): Promise<void> {
    const job = await this.jobRepository.findOne({ where: { id: jobId } });
    if (!job) {
      throw new Error(`Job ${jobId} not found`);
    }

    // Update job status to running
    job.status = JobStatus.RUNNING;
    job.startedAt = new Date();
    job.logs = [];
    await this.jobRepository.save(job);

    this.logger.log(`Job ${jobId} started`);

    try {
      // Execute each workflow step in order
      for (let i = 0; i < workflow.steps.length; i++) {
        const step = workflow.steps[i];
        this.logger.log(`Job ${jobId}: Executing step ${i + 1}/${workflow.steps.length} - ${step.tool}`);

        // Add log entry
        job.logs.push({
          timestamp: new Date().toISOString(),
          step: i + 1,
          tool: step.tool,
          status: 'started',
        });
        await this.jobRepository.save(job);

        // Execute the tool
        const result = await this.toolRegistry.executeTool(step.tool, step.input || {});

        if (!result.success) {
          // Tool execution failed
          job.logs.push({
            timestamp: new Date().toISOString(),
            step: i + 1,
            tool: step.tool,
            status: 'failed',
            error: result.error,
          });
          job.status = JobStatus.FAILED;
          job.finishedAt = new Date();
          await this.jobRepository.save(job);
          
          this.logger.error(`Job ${jobId} failed at step ${i + 1}`);
          return;
        }

        // Tool executed successfully
        job.logs.push({
          timestamp: new Date().toISOString(),
          step: i + 1,
          tool: step.tool,
          status: 'completed',
          output: result.output,
        });
        await this.jobRepository.save(job);

        // Store output in state manager (for multi-step workflows)
        await this.stateManager.storeStepOutput(jobId, step.tool, result.output);
      }

      // All steps completed successfully
      job.status = JobStatus.COMPLETED;
      job.finishedAt = new Date();
      await this.jobRepository.save(job);

      this.logger.log(`Job ${jobId} completed successfully`);
    } catch (error) {
      // Unexpected error
      job.logs.push({
        timestamp: new Date().toISOString(),
        error: error.message,
        stack: error.stack,
      });
      job.status = JobStatus.FAILED;
      job.finishedAt = new Date();
      await this.jobRepository.save(job);

      this.logger.error(`Job ${jobId} failed with error: ${error.message}`);
    }
  }

  /**
   * Get job status
   */
  async getJobStatus(jobId: string): Promise<Job> {
    const job = await this.jobRepository.findOne({
      where: { id: jobId },
      relations: ['workflow'],
    });

    if (!job) {
      throw new Error(`Job ${jobId} not found`);
    }

    return job;
  }
}
