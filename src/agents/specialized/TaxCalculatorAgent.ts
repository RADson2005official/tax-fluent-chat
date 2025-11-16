import { BaseAgent } from '../BaseAgent';
import { TAX_CALCULATOR_CONFIG } from '../configs';
import type { AgentTask, AgentResponse, AgentMessage } from '../types';
import { getToolsByAgent } from '../tools';
import { createLLMProvider } from '../llm/LLMProvider';
import type { LLMConfig } from '../llm/LLMProvider';

export class TaxCalculatorAgent extends BaseAgent {
  private llmProvider;

  constructor(providerConfig?: LLMConfig) {
    super(TAX_CALCULATOR_CONFIG);
    
    // Register tools
    const tools = getToolsByAgent('tax_calculator');
    tools.forEach(tool => this.registerTool(tool));

    // Initialize LLM provider - Use provided config or default to Gemini
    const defaultConfig: LLMConfig = {
      provider: 'gemini',
      model: 'gemini-1.5-flash-latest',
      temperature: this.config.temperature,
      maxTokens: this.config.maxTokens
    };

    this.llmProvider = createLLMProvider(providerConfig || defaultConfig);
  }

  async processTask(task: AgentTask): Promise<AgentResponse> {
    this.setStatus('working');

    try {
      switch (task.type) {
        case 'calculate_tax':
          return await this.calculateTax(task.input);
        case 'calculate_credits':
          return await this.calculateCredits(task.input);
        case 'scenario_analysis':
          return await this.performScenarioAnalysis(task.input);
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
      // Add message to history
      this.addToHistory(message);

      // Fast-path: handle common quick commands deterministically without LLM
      const text = message.content.toLowerCase().trim();

      // Helper parsers
      const parseMoney = (s: string): number => {
        const m = s.replace(/[,\s]/g, '').match(/\$?(-?\d+(?:\.\d+)?)/);
        return m ? Number(m[1]) : NaN;
      };
      const findNumberAfter = (key: string): number | undefined => {
        const re = new RegExp(key + "[\\:\\s]*\\$?(-?\\d[\\d,]*(?:\\.\\d+)?)", 'i');
        const m = message.content.match(re);
        return m ? parseMoney(m[1]) : undefined;
      };
      const extractFilingStatus = (): string | undefined => {
        if (text.includes('married filing jointly') || text.includes('mfj') || text.includes('married_joint')) return 'married_joint';
        if (text.includes('married filing separately') || text.includes('mfs') || text.includes('married_separate')) return 'married_separate';
        if (text.includes('head of household') || text.includes('hoh') || text.includes('head_of_household')) return 'head_of_household';
        if (text.includes('qualifying widow') || text.includes('qualifying_widow')) return 'qualifying_widow';
        if (text.includes('single')) return 'single';
        return undefined;
      };

      if (text.startsWith('compute agi')) {
        // Expected: "compute agi from w2 + 1099 [w2: <amt>] [1099: <amt>] [deductions: <amt>]"
        const w2 = findNumberAfter('w2') ?? undefined;
        const f1099 = findNumberAfter('1099') ?? undefined;
        const aboveLine = findNumberAfter('deductions') ?? 0;

        if (w2 === undefined && f1099 === undefined) {
          return this.createResponse(
            true,
            'Please provide amounts, e.g.: "compute agi from w2 + 1099 w2: 75000 1099: 1200 deductions: 0"',
            undefined,
            ['Awaiting W-2 and 1099 amounts to compute AGI'],
            0.9
          );
        }

        const totalIncome = (w2 || 0) + (f1099 || 0);
        const agiResult = await this.executeTool('calculate_agi', {
          totalIncome,
          aboveLineDeductions: { other: aboveLine }
        });

        return this.createResponse(
          true,
          `AGI computed. Total income: $${totalIncome.toLocaleString()} − Above-the-line: $${(aboveLine||0).toLocaleString()} → AGI: $${agiResult.agi.toLocaleString()}.`,
          agiResult,
          ['Computed AGI from W-2 and 1099 inputs'],
          0.99
        );
      }

      if (text.startsWith('simulate standard vs itemized')) {
        // Expected: "simulate standard vs itemized [status: single] [agi: 75000] [itemized: 18000]"
        const filingStatus = extractFilingStatus();
        const agi = findNumberAfter('agi');
        const itemized = findNumberAfter('itemized');

        if (!filingStatus || agi === undefined) {
          return this.createResponse(
            true,
            'Please provide filing status and AGI, e.g.: "simulate standard vs itemized status: single agi: 75000 itemized: 18000"',
            undefined,
            ['Awaiting filing status and AGI to compare deductions'],
            0.9
          );
        }

        const tiResult = await this.executeTool('calculate_taxable_income', {
          agi,
          filingStatus,
          itemizedDeductions: itemized ?? 0
        });

        const better = tiResult.deductionType === 'standard' ? `Standard Deduction ($${tiResult.standardDeduction.toLocaleString()})` : `Itemized ($${(itemized ?? 0).toLocaleString()})`;

        return this.createResponse(
          true,
          `Best option: ${better}. Taxable income: $${tiResult.taxableIncome.toLocaleString()} (AGI $${agi.toLocaleString()} − deduction $${tiResult.deductionUsed.toLocaleString()}).`,
          tiResult,
          ['Compared standard vs itemized deductions for 2024'],
          0.99
        );
      }

      if (text.startsWith('calc ctc')) {
        // Expected: "calc ctc 2 dependents [status: single] [agi: 75000]"
        const depMatch = text.match(/calc\s+ctc\s+(\d+)/i);
        const dependents = depMatch ? Number(depMatch[1]) : undefined;
        const filingStatus = extractFilingStatus();
        const agi = findNumberAfter('agi');

        if (!dependents) {
          return this.createResponse(
            true,
            'How many qualifying children (under 17)? Example: "calc ctc 2 dependents status: single agi: 75000"',
            undefined,
            ['Prompted for number of qualifying children'],
            0.9
          );
        }
        if (!filingStatus || agi === undefined) {
          return this.createResponse(
            true,
            'Please add filing status and AGI. Example: "calc ctc ' + dependents + ' dependents status: single agi: 75000"',
            undefined,
            ['Awaiting filing status and AGI to compute Child Tax Credit'],
            0.9
          );
        }

        const ctc = await this.executeTool('calculate_child_tax_credit', {
          dependents,
          agi,
          filingStatus
        });

        return this.createResponse(
          true,
          `Child Tax Credit: $${ctc.credit.toLocaleString()} (max $${ctc.maxCredit.toLocaleString()})${ctc.phaseoutApplied ? ' after phase-out' : ''}. Simplified refundable portion (cap): $${ctc.refundablePortion.toLocaleString()}.`,
          ctc,
          ['Computed Child Tax Credit using 2024 phase-out rules'],
          0.99
        );
      }

      // Build context for LLM
      const systemPrompt = this.buildSystemPrompt();
      const contextMessage = this.buildContextMessage();

      // Prepare messages for LLM
      const messages = [
        { role: 'system' as const, content: systemPrompt },
        { role: 'user' as const, content: contextMessage },
        { role: 'user' as const, content: message.content }
      ];

      // Get LLM response
      const llmResponse = await this.llmProvider.chat(messages, {
        temperature: this.config.temperature,
        maxTokens: this.config.maxTokens
      });

      // Parse response and extract tool calls if any
      const responseText = llmResponse.content;

      return this.createResponse(
        true,
        responseText,
        undefined,
        ['Based on 2024 IRS tax code and regulations'],
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

  private async calculateTax(input: any): Promise<AgentResponse> {
    const { taxableIncome, filingStatus } = input;

    try {
      // Use the calculate_income_tax tool
      const result = await this.executeTool('calculate_income_tax', {
        taxableIncome,
        filingStatus
      });

      const reasoning = [
        `Calculated federal income tax for ${filingStatus} filing status`,
        `Taxable income: $${taxableIncome.toLocaleString()}`,
        `Applied 2024 tax brackets`,
        `Total tax: $${result.totalTax.toLocaleString()}`,
        `Effective rate: ${result.effectiveRate}`,
        `Marginal rate: ${result.marginalRate}`
      ];

      return this.createResponse(
        true,
        `Your federal income tax is $${result.totalTax.toLocaleString()} with an effective rate of ${result.effectiveRate}.`,
        result,
        reasoning,
        0.99
      );
    } catch (error) {
      return this.createResponse(
        false,
        `Error calculating tax: ${error instanceof Error ? error.message : 'Unknown error'}`
      );
    }
  }

  private async calculateCredits(input: any): Promise<AgentResponse> {
    const { dependents, agi, filingStatus, earnedIncome } = input;
    const credits: any = {};
    const reasoning: string[] = [];

    try {
      // Calculate Child Tax Credit if applicable
      if (dependents > 0) {
        const ctcResult = await this.executeTool('calculate_child_tax_credit', {
          dependents,
          agi,
          filingStatus
        });
        credits.childTaxCredit = ctcResult;
        reasoning.push(`Child Tax Credit: $${ctcResult.credit} for ${dependents} dependent(s)`);
      }

      // Calculate EITC if applicable
      if (earnedIncome) {
        const eitcResult = await this.executeTool('calculate_eitc', {
          earnedIncome,
          dependents,
          filingStatus
        });
        credits.eitc = eitcResult;
        if (eitcResult.eligible) {
          reasoning.push(`Earned Income Tax Credit: $${eitcResult.credit}`);
        }
      }

      const totalCredits = (credits.childTaxCredit?.credit || 0) + (credits.eitc?.credit || 0);

      return this.createResponse(
        true,
        `Total available tax credits: $${totalCredits.toLocaleString()}`,
        credits,
        reasoning,
        0.95
      );
    } catch (error) {
      return this.createResponse(
        false,
        `Error calculating credits: ${error instanceof Error ? error.message : 'Unknown error'}`
      );
    }
  }

  private async performScenarioAnalysis(input: any): Promise<AgentResponse> {
    const { scenarios } = input;

    try {
      const result = await this.executeTool('compare_scenarios', { scenarios });

      const reasoning = [
        `Analyzed ${scenarios.length} tax scenarios`,
        `Best scenario: ${result.bestScenario}`,
        `Potential savings: $${result.potentialSavings.toLocaleString()}`
      ];

      return this.createResponse(
        true,
        `After analyzing your scenarios, ${result.bestScenario} provides the best outcome with potential savings of $${result.potentialSavings.toLocaleString()}.`,
        result,
        reasoning,
        0.90
      );
    } catch (error) {
      return this.createResponse(
        false,
        `Error performing scenario analysis: ${error instanceof Error ? error.message : 'Unknown error'}`
      );
    }
  }

  private buildContextMessage(): string {
    const { taxContext, userProfile } = this.state.memory;
    
    let context = '## Current Tax Context:\n';
    context += `Tax Year: ${taxContext.taxYear}\n`;
    context += `User Expertise: ${userProfile.preferences.mode}\n\n`;

    if (taxContext.income.w2.length > 0) {
      context += '### W-2 Income:\n';
      taxContext.income.w2.forEach((w2, i) => {
        context += `  ${i + 1}. ${w2.employer}: $${w2.wages}\n`;
      });
    }

    if (taxContext.income.form1099.length > 0) {
      context += '### 1099 Income:\n';
      taxContext.income.form1099.forEach((form, i) => {
        context += `  ${i + 1}. ${form.payer} (${form.type}): $${form.amount}\n`;
      });
    }

    return context;
  }
}
