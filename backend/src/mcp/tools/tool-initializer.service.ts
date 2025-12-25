import { Injectable, OnModuleInit, Logger } from '@nestjs/common';
import { ToolRegistryService } from '../tool-registry.service';
import { GenerateBlogTool } from './generate-blog.tool';
import { GenerateImageTool } from './generate-image.tool';

/**
 * Tool initializer - registers all tools with the MCP Tool Registry
 * This is where existing models are integrated into MCP
 */
@Injectable()
export class ToolInitializerService implements OnModuleInit {
  private readonly logger = new Logger(ToolInitializerService.name);

  constructor(
    private readonly toolRegistry: ToolRegistryService,
    private readonly generateBlogTool: GenerateBlogTool,
    private readonly generateImageTool: GenerateImageTool,
  ) {}

  onModuleInit() {
    this.registerTools();
  }

  private registerTools() {
    this.logger.log('Registering MCP tools...');

    // Register generate_blog tool
    this.toolRegistry.registerTool({
      name: 'generate_blog',
      description: 'Generates a blog post using AI',
      inputSchema: {
        type: 'object',
        properties: {
          workspaceId: { type: 'string' },
          topic: { type: 'string' },
          tone: { type: 'string' },
          length: { type: 'number' },
        },
        required: ['workspaceId', 'topic'],
      },
      outputSchema: {
        type: 'object',
        properties: {
          contentId: { type: 'string' },
          title: { type: 'string' },
          body: { type: 'string' },
          s3Url: { type: 'string' },
        },
      },
      executor: async (input) => this.generateBlogTool.execute(input),
    });

    // Register generate_image tool
    this.toolRegistry.registerTool({
      name: 'generate_image',
      description: 'Generates an image using AI',
      inputSchema: {
        type: 'object',
        properties: {
          workspaceId: { type: 'string' },
          prompt: { type: 'string' },
          style: { type: 'string' },
          size: { type: 'string' },
        },
        required: ['workspaceId', 'prompt'],
      },
      outputSchema: {
        type: 'object',
        properties: {
          contentId: { type: 'string' },
          s3Url: { type: 'string' },
          prompt: { type: 'string' },
        },
      },
      executor: async (input) => this.generateImageTool.execute(input),
    });

    this.logger.log(`Registered ${this.toolRegistry.getAllTools().length} tools`);
  }
}
