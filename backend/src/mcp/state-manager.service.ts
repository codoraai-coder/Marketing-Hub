import { Injectable, Logger } from '@nestjs/common';

interface JobState {
  jobId: string;
  outputs: Record<string, any>;
}

@Injectable()
export class StateManagerService {
  private readonly logger = new Logger(StateManagerService.name);
  private readonly states: Map<string, JobState> = new Map();

  /**
   * Store output from a workflow step
   */
  async storeStepOutput(jobId: string, toolName: string, output: any): Promise<void> {
    let state = this.states.get(jobId);
    
    if (!state) {
      state = {
        jobId,
        outputs: {},
      };
      this.states.set(jobId, state);
    }

    state.outputs[toolName] = output;
    this.logger.log(`Stored output for job ${jobId}, tool ${toolName}`);
  }

  /**
   * Get output from a previous step
   */
  getStepOutput(jobId: string, toolName: string): any {
    const state = this.states.get(jobId);
    return state?.outputs[toolName];
  }

  /**
   * Get all outputs for a job
   */
  getJobState(jobId: string): JobState | undefined {
    return this.states.get(jobId);
  }

  /**
   * Clear state for a job (call after job completion)
   */
  clearJobState(jobId: string): void {
    this.states.delete(jobId);
    this.logger.log(`Cleared state for job ${jobId}`);
  }
}
