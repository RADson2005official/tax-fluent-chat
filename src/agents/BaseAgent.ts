import type { 
  AgentRole, 
  AgentConfig, 
  AgentState, 
  AgentMessage, 
  AgentTask, 
  AgentResponse,
  AgentMemory,
  Tool,
  TaxFormSuggestion
} from './types';

export abstract class BaseAgent {
  protected config: AgentConfig;
  protected state: AgentState;
  protected tools: Map<string, Tool>;

  constructor(config: AgentConfig) {
    this.config = config;
    this.tools = new Map();
    
    this.state = {
      role: config.role,
      status: 'idle',
      memory: {
        conversationHistory: [],
        userProfile: {
          preferences: {
            mode: 'Novice',
            language: 'en',
            complexity: 'simple'
          }
        },
        taxContext: {
          taxYear: new Date().getFullYear(),
          income: {
            w2: [],
            form1099: []
          },
          deductions: {},
          credits: {},
          formData: {}
        },
        documents: [],
        calculations: []
      },
      context: {}
    };
  }

  // Abstract methods that each agent must implement
  abstract processTask(task: AgentTask): Promise<AgentResponse>;
  
  abstract generateResponse(message: AgentMessage): Promise<AgentResponse>;

  // Common agent methods
  registerTool(tool: Tool): void {
    this.tools.set(tool.name, tool);
  }

  async executeTool(toolName: string, parameters: Record<string, any>): Promise<any> {
    const tool = this.tools.get(toolName);
    if (!tool) {
      throw new Error(`Tool ${toolName} not found`);
    }

    try {
      return await tool.execute(parameters, this.getContext());
    } catch (error) {
      console.error(`Error executing tool ${toolName}:`, error);
      throw error;
    }
  }

  updateMemory(update: Partial<AgentMemory>): void {
    this.state.memory = {
      ...this.state.memory,
      ...update
    };
  }

  addToHistory(message: AgentMessage): void {
    this.state.memory.conversationHistory.push(message);
  }

  getContext(): Record<string, any> {
    return {
      ...this.state.context,
      memory: this.state.memory,
      config: this.config
    };
  }

  updateContext(context: Record<string, any>): void {
    this.state.context = {
      ...this.state.context,
      ...context
    };
  }

  setStatus(status: AgentState['status']): void {
    this.state.status = status;
  }

  getState(): AgentState {
    return this.state;
  }

  getCapabilities(): string[] {
    return this.config.capabilities.map(c => c.name);
  }

  canHandle(taskType: string): boolean {
    return this.config.capabilities.some(
      cap => cap.name === taskType || cap.tools.includes(taskType)
    );
  }

  protected buildSystemPrompt(): string {
    let prompt = this.config.systemPrompt + '\n\n';
    
    prompt += '## Your Capabilities:\n';
    this.config.capabilities.forEach(cap => {
      prompt += `- ${cap.name}: ${cap.description}\n`;
      prompt += `  Tools: ${cap.tools.join(', ')}\n`;
    });

    prompt += '\n## Available Tools:\n';
    this.tools.forEach(tool => {
      prompt += `- ${tool.name}: ${tool.description}\n`;
      prompt += '  Parameters:\n';
      tool.parameters.forEach(param => {
        prompt += `    - ${param.name} (${param.type}${param.required ? ', required' : ', optional'}): ${param.description}\n`;
      });
    });

    return prompt;
  }

  protected async callLLM(messages: AgentMessage[], options?: {
    temperature?: number;
    maxTokens?: number;
    tools?: Tool[];
  }): Promise<string> {
    // This will be implemented when we create the LLM integration layer
    // For now, return a placeholder
    return 'LLM response placeholder - will be implemented with API integration';
  }

  protected formatMessageForLLM(message: AgentMessage): { role: string; content: string } {
    return {
      role: message.role === 'agent' ? 'assistant' : message.role,
      content: message.content
    };
  }

  protected createResponse(
    success: boolean,
    message: string,
    data?: any,
    reasoning?: string[],
    confidence?: number,
    suggestions?: string[],
    nextActions?: string[],
    formSuggestions?: TaxFormSuggestion[]
  ): AgentResponse {
    return {
      agentRole: this.config.role,
      success,
      message,
      data,
      reasoning,
      confidence,
      suggestions,
      nextActions,
      formSuggestions
    };
  }
}
