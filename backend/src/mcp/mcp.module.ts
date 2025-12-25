import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { Job } from '../entities/job.entity';
import { Workflow } from '../entities/workflow.entity';
import { Content } from '../entities/content.entity';
import { ToolRegistryService } from './tool-registry.service';
import { ExecutionEngineService } from './execution-engine.service';
import { StateManagerService } from './state-manager.service';
import { WorkflowLoaderService } from './workflow-loader.service';
import { GenerateBlogTool } from './tools/generate-blog.tool';
import { GenerateImageTool } from './tools/generate-image.tool';
import { ToolInitializerService } from './tools/tool-initializer.service';
import { S3Service } from '../services/s3.service';

/**
 * MCP Module - The Master Control Program Core
 * This module contains all MCP logic and should not be modified
 * unless adding new tools or core functionality
 */
@Module({
  imports: [
    TypeOrmModule.forFeature([Job, Workflow, Content]),
  ],
  providers: [
    // MCP Core Services
    ToolRegistryService,
    ExecutionEngineService,
    StateManagerService,
    WorkflowLoaderService,
    
    // Infrastructure
    S3Service,
    
    // Tools (Existing Models Wrapped as MCP Tools)
    GenerateBlogTool,
    GenerateImageTool,
    ToolInitializerService,
  ],
  exports: [
    ToolRegistryService,
    ExecutionEngineService,
    StateManagerService,
    WorkflowLoaderService,
  ],
})
export class McpModule {}
