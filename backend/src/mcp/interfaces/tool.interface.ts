export interface ToolSchema {
  type: string;
  properties: Record<string, any>;
  required?: string[];
}

export interface ToolDefinition {
  name: string;
  description: string;
  inputSchema: ToolSchema;
  outputSchema: ToolSchema;
  executor: (input: any) => Promise<any>;
}

export interface ToolExecutionResult {
  success: boolean;
  output?: any;
  error?: string;
}
