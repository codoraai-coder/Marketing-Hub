import { IsString, IsNotEmpty, IsUUID, IsArray, IsOptional, ValidateNested } from 'class-validator';
import { Type } from 'class-transformer';
import { WorkflowStep } from '../../../entities/workflow.entity';

class WorkflowStepDto implements WorkflowStep {
  @IsString()
  @IsNotEmpty()
  tool: string;

  @IsOptional()
  input?: Record<string, any>;
}

export class CreateWorkflowDto {
  @IsUUID()
  @IsNotEmpty()
  workspaceId: string;

  @IsString()
  @IsNotEmpty()
  name: string;

  @IsString()
  @IsOptional()
  description?: string;

  @IsArray()
  @ValidateNested({ each: true })
  @Type(() => WorkflowStepDto)
  steps: WorkflowStepDto[];
}
