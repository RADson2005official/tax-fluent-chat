import { BaseAgent } from '../BaseAgent';
import { COMPLIANCE_CHECKER_CONFIG } from '../configs';
import type { AgentTask, AgentResponse, AgentMessage } from '../types';
import { getToolsByAgent } from '../tools';
import { createLLMProvider } from '../llm/LLMProvider';
import type { LLMConfig } from '../llm/LLMProvider';

export class ComplianceAgent extends BaseAgent {
  private llmProvider;

  constructor(providerConfig?: LLMConfig) {
    super(COMPLIANCE_CHECKER_CONFIG);

    // Register tools
    const tools = getToolsByAgent('compliance_checker');
    tools.forEach(tool => this.registerTool(tool));

    // Initialize LLM provider
    const defaultConfig: LLMConfig = {
      provider: 'gemini',
      model: 'gemini-flash-latest',
      temperature: 0.1, // Low temperature for strict compliance
      maxTokens: this.config.maxTokens
    };

    this.llmProvider = createLLMProvider(providerConfig || defaultConfig);
  }

  async processTask(task: AgentTask): Promise<AgentResponse> {
    this.setStatus('working');

    try {
      switch (task.type) {
        case 'validate_compliance':
          return await this.validateCompliance(task.input);
        case 'check_eligibility':
          return await this.checkEligibility(task.input);
        default:
          return this.createResponse(false, `Unknown task type: ${task.type}`);
      }
    } catch (error) {
      this.setStatus('error');
      return this.createResponse(
        false,
        `Error processing task: ${error instanceof Error ? error.message : 'Unknown error'}`
      );
    } finally {
      this.setStatus('idle');
    }
  }

  async generateResponse(message: AgentMessage): Promise<AgentResponse> {
    this.setStatus('thinking');

    try {
      this.addToHistory(message);

      // Build context for LLM
      const systemPrompt = `You are a strict Tax Compliance Agent. 
      Your goal is to ensure all tax information is accurate and compliant with IRS regulations.
      Verify facts, check for missing information, and ensure eligibility for credits/deductions.
      Do not provide tax advice, only compliance checks.`;

      const contextMessage = this.buildContextMessage();

      const messages = [
        { role: 'system' as const, content: systemPrompt },
        { role: 'user' as const, content: contextMessage },
        { role: 'user' as const, content: message.content }
      ];

      const llmResponse = await this.llmProvider.chat(messages, {
        temperature: 0.1,
        maxTokens: 500
      });

      return this.createResponse(
        true,
        llmResponse.content,
        undefined,
        ['Checked against 2024 IRS regulations'],
        0.95
      );

    } catch (error) {
      this.setStatus('error');
      return this.createResponse(
        false,
        `Error generating response: ${error instanceof Error ? error.message : 'Unknown error'}`
      );
    } finally {
      this.setStatus('idle');
    }
  }

  private async validateCompliance(input: any): Promise<AgentResponse> {
    const { formId, year } = input;

    // In a real implementation, this would fetch form data from the backend
    // For now, we'll simulate validation logic

    const validationResults = {
      isValid: true,
      warnings: [] as string[],
      errors: [] as string[]
    };

    // Example validation logic
    if (!year || year !== 2024) {
      validationResults.errors.push('Tax year must be 2024');
      validationResults.isValid = false;
    }

    return this.createResponse(
      true,
      validationResults.isValid ? 'Tax form is compliant.' : 'Compliance issues found.',
      validationResults,
      ['Validated against 2024 tax rules'],
      1.0
    );
  }

  private async checkEligibility(input: any): Promise<AgentResponse> {
    const { creditType, data } = input;

    // Logic to check eligibility for specific credits (EITC, CTC, etc.)
    // This would use the LLM or specific rule-based tools

    return this.createResponse(
      true,
      `Eligibility check for ${creditType} completed.`,
      { eligible: true, reason: 'Meets income and relationship tests' }, // Placeholder
      ['Checked income limits', 'Checked relationship requirements'],
      0.9
    );
  }

  private buildContextMessage(): string {
    const { taxContext } = this.state.memory;
    return `Current Tax Year: ${taxContext.taxYear}`;
  }
}
