import { Injectable, Logger } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Workflow, WorkflowStep } from '../entities/workflow.entity';

@Injectable()
export class WorkflowLoaderService {
  private readonly logger = new Logger(WorkflowLoaderService.name);

  constructor(
    @InjectRepository(Workflow)
    private readonly workflowRepository: Repository<Workflow>,
  ) {}

  /**
   * Load a workflow by ID
   */
  async loadWorkflow(workflowId: string): Promise<Workflow> {
    const workflow = await this.workflowRepository.findOne({
      where: { id: workflowId },
    });

    if (!workflow) {
      throw new Error(`Workflow ${workflowId} not found`);
    }

    this.logger.log(`Loaded workflow: ${workflow.name}`);
    return workflow;
  }

  /**
   * Create a new workflow
   */
  async createWorkflow(
    workspaceId: string,
    name: string,
    description: string,
    steps: WorkflowStep[],
  ): Promise<Workflow> {
    const workflow = this.workflowRepository.create({
      workspaceId,
      name,
      description,
      steps,
    });

    await this.workflowRepository.save(workflow);
    this.logger.log(`Created workflow: ${workflow.name} (${workflow.id})`);
    
    return workflow;
  }

  /**
   * Get all workflows for a workspace
   */
  async getWorkflowsByWorkspace(workspaceId: string): Promise<Workflow[]> {
    return this.workflowRepository.find({
      where: { workspaceId },
      order: { createdAt: 'DESC' },
    });
  }

  /**
   * Validate workflow steps
   */
  validateWorkflow(workflow: Workflow): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (!workflow.steps || workflow.steps.length === 0) {
      errors.push('Workflow must have at least one step');
    }

    for (let i = 0; i < workflow.steps.length; i++) {
      const step = workflow.steps[i];
      if (!step.tool) {
        errors.push(`Step ${i + 1} is missing tool name`);
      }
    }

    return {
      valid: errors.length === 0,
      errors,
    };
  }
}
