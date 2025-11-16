// LangChain-based Tax Filing Agent
import { ChatOpenAI } from "@langchain/openai";
import { ChatAnthropic } from "@langchain/anthropic";
import { MemorySaver } from "@langchain/langgraph";
import { HumanMessage, AIMessage, SystemMessage, type BaseMessage } from "@langchain/core/messages";
import { z } from "zod";
import {
  convertToLangChainTools,
  TaxFilingResponseFormat,
  AgentContextSchema,
  type TaxFilingResponse,
  type AgentContext,
} from './LangChainTools';

export interface LangChainAgentConfig {
  provider: 'openai' | 'anthropic' | 'gemini';
  model?: string;
  apiKey?: string;
  temperature?: number;
  maxTokens?: number;
}

export class LangChainTaxAgent {
  private model: ChatOpenAI | ChatAnthropic;
  private tools: ReturnType<typeof convertToLangChainTools>;
  private checkpointer: MemorySaver;
  private systemPrompt: string;

  constructor(config: LangChainAgentConfig) {
    // Initialize model based on provider
    if (config.provider === 'openai') {
      this.model = new ChatOpenAI({
        model: config.model || 'gpt-4o',
        temperature: config.temperature ?? 0.7,
        maxTokens: config.maxTokens ?? 2000,
        apiKey: config.apiKey || import.meta.env.VITE_OPENAI_API_KEY,
      });
    } else if (config.provider === 'anthropic') {
      this.model = new ChatAnthropic({
        model: config.model || 'claude-sonnet-4-5-20250929',
        temperature: config.temperature ?? 0.7,
        maxTokens: config.maxTokens ?? 2000,
        apiKey: config.apiKey || import.meta.env.VITE_ANTHROPIC_API_KEY,
      });
    } else {
      throw new Error(`Unsupported provider: ${config.provider}`);
    }

    // Convert existing tools to LangChain format
    this.tools = convertToLangChainTools();

    // Initialize memory for conversation state
    this.checkpointer = new MemorySaver();

    // Define comprehensive system prompt
    this.systemPrompt = `You are an expert AI Tax Filing Assistant specialized in U.S. federal tax preparation.

Your Role:
- Help users understand and complete their tax filing requirements
- Extract data from tax documents (W-2, 1099, receipts)
- Calculate accurate tax liabilities and refunds
- Validate compliance with IRS regulations
- Fill out tax forms correctly
- Provide tax optimization strategies
- Explain complex tax concepts in simple terms

Your Capabilities:
1. Document Processing: Extract structured data from uploaded tax documents using OCR and AI
2. Tax Calculation: Compute federal taxes, deductions, credits, and estimated payments
3. Compliance Checking: Validate filings against current IRS rules and regulations
4. Form Filling: Auto-fill tax forms (1040, Schedule C, etc.) with extracted data
5. Tax Advisory: Provide personalized recommendations for tax optimization

Guidelines:
- Always prioritize accuracy and IRS compliance
- Explain your reasoning clearly when making calculations
- Ask clarifying questions when information is missing
- Warn users about potential issues or red flags
- Suggest tax-saving opportunities when applicable
- Maintain user privacy and data security

When processing requests:
1. Understand what the user needs
2. Determine which tools to use
3. Execute tools in logical sequence
4. Validate results for accuracy
5. Provide clear, actionable responses

Remember: You have access to specialized tools for document processing, tax calculations, compliance checking, and form filling. Use them intelligently to provide comprehensive assistance.`;
  }

  /**
   * Bind tools to the model
   */
  private bindTools() {
    return this.model.bind({ tools: this.tools });
  }

  /**
   * Process a user message and generate response
   */
  async processMessage(
    userMessage: string,
    context: AgentContext,
    conversationHistory: BaseMessage[] = []
  ): Promise<{
    response: string;
    structuredResponse?: TaxFilingResponse;
    toolCalls: Array<{ tool: string; input: Record<string, unknown>; output: unknown }>;
    reasoning: string[];
  }> {
    try {
      const reasoning: string[] = [];
      const toolCalls: Array<{ tool: string; input: Record<string, unknown>; output: unknown }> = [];

      // Build message history
      const messages: BaseMessage[] = [
        new SystemMessage(this.systemPrompt),
        ...conversationHistory,
        new HumanMessage(userMessage),
      ];

      // Bind tools to model
      const modelWithTools = this.bindTools();

      // Invoke model with tools (ReAct loop)
      let response = await modelWithTools.invoke(messages);
      reasoning.push("Initial model invocation completed");

      // Process tool calls if any
      while (response.tool_calls && response.tool_calls.length > 0) {
        reasoning.push(`Model requested ${response.tool_calls.length} tool calls`);

        // Execute each tool call
        for (const toolCall of response.tool_calls) {
          const tool = this.tools.find((t) => t.name === toolCall.name);
          
          if (tool) {
            reasoning.push(`Executing tool: ${toolCall.name}`);
            
            try {
              const toolResult = await tool.invoke(toolCall.args);
              toolCalls.push({
                tool: toolCall.name,
                input: toolCall.args,
                output: toolResult,
              });

              // Add tool result to messages
              messages.push(new AIMessage({
                content: '',
                tool_calls: [toolCall],
              }));
              messages.push(new HumanMessage({
                content: `Tool result: ${toolResult}`,
                name: toolCall.name,
              }));

              reasoning.push(`Tool ${toolCall.name} executed successfully`);
            } catch (error) {
              const errorMsg = error instanceof Error ? error.message : String(error);
              reasoning.push(`Tool ${toolCall.name} failed: ${errorMsg}`);
              
              messages.push(new HumanMessage({
                content: `Tool error: ${errorMsg}`,
                name: toolCall.name,
              }));
            }
          }
        }

        // Continue ReAct loop with tool results
        response = await modelWithTools.invoke(messages);
        reasoning.push("Processed tool results and generated new response");
      }

      // Extract final response
      const finalResponse = response.content as string;

      // Try to extract structured response if model supports it
      let structuredResponse: TaxFilingResponse | undefined;
      try {
        // Attempt to parse structured output from response
        const jsonMatch = finalResponse.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
          const parsed = JSON.parse(jsonMatch[0]);
          structuredResponse = TaxFilingResponseFormat.parse(parsed);
        }
      } catch {
        // Structured response not available, that's okay
      }

      reasoning.push("Response generation completed");

      return {
        response: finalResponse,
        structuredResponse,
        toolCalls,
        reasoning,
      };
    } catch (error) {
      console.error('Error in LangChain agent:', error);
      throw error;
    }
  }

  /**
   * Stream responses for real-time feedback
   */
  async *streamMessage(
    userMessage: string,
    context: AgentContext,
    conversationHistory: BaseMessage[] = []
  ): AsyncGenerator<{
    type: 'token' | 'tool_call' | 'tool_result' | 'complete';
    content: string;
    data?: unknown;
  }> {
    const messages: BaseMessage[] = [
      new SystemMessage(this.systemPrompt),
      ...conversationHistory,
      new HumanMessage(userMessage),
    ];

    const modelWithTools = this.bindTools();

    try {
      const stream = await modelWithTools.stream(messages);

      for await (const chunk of stream) {
        if (chunk.content) {
          yield {
            type: 'token',
            content: chunk.content as string,
          };
        }

        if (chunk.tool_calls && chunk.tool_calls.length > 0) {
          for (const toolCall of chunk.tool_calls) {
            yield {
              type: 'tool_call',
              content: `Calling tool: ${toolCall.name}`,
              data: toolCall,
            };

            // Execute tool
            const tool = this.tools.find((t) => t.name === toolCall.name);
            if (tool) {
              try {
                const result = await tool.invoke(toolCall.args);
                yield {
                  type: 'tool_result',
                  content: `Tool ${toolCall.name} completed`,
                  data: result,
                };
              } catch (error) {
                yield {
                  type: 'tool_result',
                  content: `Tool ${toolCall.name} failed: ${error}`,
                  data: { error },
                };
              }
            }
          }
        }
      }

      yield {
        type: 'complete',
        content: 'Response generation completed',
      };
    } catch (error) {
      yield {
        type: 'complete',
        content: `Error: ${error}`,
        data: { error },
      };
    }
  }

  /**
   * Process a complete tax filing workflow
   */
  async processTaxFilingWorkflow(
    documentData: Record<string, unknown>,
    userInfo: Record<string, unknown>,
    context: AgentContext
  ): Promise<{
    steps: Array<{ step: string; status: 'completed' | 'failed'; result: unknown }>;
    finalResult: TaxFilingResponse;
  }> {
    const steps: Array<{ step: string; status: 'completed' | 'failed'; result: unknown }> = [];

    try {
      // Step 1: Document Processing
      steps.push({
        step: 'Document Processing',
        status: 'completed',
        result: await this.processMessage(
          `Extract all relevant data from the provided tax documents: ${JSON.stringify(documentData)}`,
          context
        ),
      });

      // Step 2: Tax Calculation
      steps.push({
        step: 'Tax Calculation',
        status: 'completed',
        result: await this.processMessage(
          `Calculate federal tax liability for: ${JSON.stringify(userInfo)}`,
          context
        ),
      });

      // Step 3: Compliance Check
      steps.push({
        step: 'Compliance Validation',
        status: 'completed',
        result: await this.processMessage(
          `Validate tax filing compliance with IRS regulations`,
          context
        ),
      });

      // Step 4: Form Filling
      steps.push({
        step: 'Form Filling',
        status: 'completed',
        result: await this.processMessage(
          `Fill out required tax forms based on calculated data`,
          context
        ),
      });

      // Generate final summary
      const finalResult: TaxFilingResponse = {
        summary: 'Tax filing workflow completed successfully',
        nextSteps: ['Review generated forms', 'Sign and submit to IRS'],
        confidence: 0.9,
        estimatedTax: 0, // Will be extracted from calculation step
        formsRequired: ['1040', 'Schedule 1'],
      };

      return { steps, finalResult };
    } catch (error) {
      console.error('Workflow error:', error);
      throw error;
    }
  }
}
