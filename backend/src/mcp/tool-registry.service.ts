import { Injectable, Logger } from '@nestjs/common';
import { ToolDefinition, ToolExecutionResult } from './interfaces/tool.interface';

@Injectable()
export class ToolRegistryService {
  private readonly logger = new Logger(ToolRegistryService.name);
  private readonly tools: Map<string, ToolDefinition> = new Map();

  /**
   * Register a new tool in the MCP system
   */
  registerTool(tool: ToolDefinition): void {
    if (this.tools.has(tool.name)) {
      this.logger.warn(`Tool ${tool.name} is already registered. Overwriting...`);
    }
    this.tools.set(tool.name, tool);
    this.logger.log(`Tool registered: ${tool.name}`);
  }

  /**
   * Get a tool by name
   */
  getTool(name: string): ToolDefinition | undefined {
    return this.tools.get(name);
  }

  /**
   * Check if a tool exists
   */
  hasTool(name: string): boolean {
    return this.tools.has(name);
  }

  /**
   * Get all registered tools
   */
  getAllTools(): ToolDefinition[] {
    return Array.from(this.tools.values());
  }

  /**
   * Execute a tool with the given input
   */
  async executeTool(name: string, input: any): Promise<ToolExecutionResult> {
    const tool = this.getTool(name);
    
    if (!tool) {
      return {
        success: false,
        error: `Tool ${name} not found`,
      };
    }

    try {
      this.logger.log(`Executing tool: ${name}`);
      const output = await tool.executor(input);
      this.logger.log(`Tool ${name} executed successfully`);
      
      return {
        success: true,
        output,
      };
    } catch (error) {
      this.logger.error(`Tool ${name} execution failed: ${error.message}`);
      return {
        success: false,
        error: error.message,
      };
    }
  }
}
