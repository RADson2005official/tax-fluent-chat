import { BaseAgent } from '../BaseAgent';
import { ORCHESTRATOR_CONFIG } from '../configs';
import type { AgentTask, AgentResponse, AgentMessage, AgentRole, TaxFormSuggestion } from '../types';
import { TaxCalculatorAgent } from './TaxCalculatorAgent';
import { createLLMProvider } from '../llm/LLMProvider';
import type { LLMConfig, LLMMessage } from '../llm/LLMProvider';

export class OrchestratorAgent extends BaseAgent {
  private llmProvider;
  private specializedAgents: Map<AgentRole, BaseAgent>;

  constructor(providerConfig?: LLMConfig) {
    super(ORCHESTRATOR_CONFIG);

    // Initialize LLM provider - Use provided config or default to Qwen (FREE tier)
    const defaultConfig: LLMConfig = {
      provider: 'qwen',
      model: 'qwen/qwen-2.5-72b-instruct:free',
      temperature: this.config.temperature,
      maxTokens: this.config.maxTokens
    };

    this.llmProvider = createLLMProvider(providerConfig || defaultConfig);

    // Initialize specialized agents
    this.specializedAgents = new Map();
    this.specializedAgents.set('tax_calculator', new TaxCalculatorAgent(providerConfig));
  }

  async processTask(task: AgentTask): Promise<AgentResponse> {
    this.setStatus('working');

    try {
      // Determine which agent(s) should handle this task
      const targetAgentRole = this.determineTargetAgent(task);
      
      if (targetAgentRole && this.specializedAgents.has(targetAgentRole)) {
        // Delegate to specialized agent
        const agent = this.specializedAgents.get(targetAgentRole)!;
        return await agent.processTask(task);
      } else {
        // Handle directly
        return this.createResponse(
          false,
          `No specialized agent available for task type: ${task.type}`
        );
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
      // Add message to conversation history
      this.addToHistory(message);

      // High-priority: if user wants to file taxes, start the automated workflow immediately
      if (this.isFormFillingRequest(message.content)) {
        return await this.handleAutomatedFormFilling(message);
      }

      // Analyze the user message to determine intent and required agents
      const intent = await this.analyzeIntent(message.content);

      // Route to appropriate agents based on intent
      if (intent.requiresCalculation) {
        return await this.handleCalculationRequest(message);
      } else if (intent.requiresAdvice) {
        return await this.handleAdvisoryRequest(message);
      } else if (intent.requiresDocumentProcessing) {
        return await this.handleDocumentRequest(message);
      } else {
        // General conversation
        return await this.handleGeneralConversation(message);
      }
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

  private async analyzeIntent(userMessage: string): Promise<{
    requiresCalculation: boolean;
    requiresAdvice: boolean;
    requiresDocumentProcessing: boolean;
    requiresCompliance: boolean;
    intent: string;
  }> {
    const messageLower = userMessage.toLowerCase();

    return {
      requiresCalculation: /calculate|compute|tax|owe|refund|income|deduction/i.test(userMessage),
      requiresAdvice: /advice|recommend|suggest|optimize|save|strategy|planning/i.test(userMessage),
      requiresDocumentProcessing: /upload|document|w-?2|1099|receipt|form/i.test(userMessage),
      requiresCompliance: /legal|compliant|eligible|qualify|rules|requirements/i.test(userMessage),
      intent: this.extractIntent(userMessage)
    };
  }

  private extractIntent(userMessage: string): string {
    const messageLower = userMessage.toLowerCase();

    if (messageLower.includes('calculate') || messageLower.includes('compute')) {
      return 'calculation';
    } else if (messageLower.includes('recommend') || messageLower.includes('advice')) {
      return 'advisory';
    } else if (messageLower.includes('upload') || messageLower.includes('document')) {
      return 'document_processing';
    } else if (messageLower.includes('eligible') || messageLower.includes('qualify')) {
      return 'compliance';
    } else {
      return 'general';
    }
  }

  private async handleCalculationRequest(message: AgentMessage): Promise<AgentResponse> {
    const taxCalculatorAgent = this.specializedAgents.get('tax_calculator');
    
    if (!taxCalculatorAgent) {
      return this.createResponse(
        false,
        'Tax calculation service is currently unavailable'
      );
    }

    // Delegate to tax calculator agent
    const response = await taxCalculatorAgent.generateResponse(message);

    // Add orchestrator context
    if (response.success) {
      response.suggestions = [
        'Would you like to see how credits affect your tax?',
        'I can compare different filing scenarios',
        'Want to optimize your deductions?'
      ];
    }

    return response;
  }

  private async handleAdvisoryRequest(message: AgentMessage): Promise<AgentResponse> {
    // Create advisory message based on context
    const { taxContext, userProfile } = this.state.memory;

    const advisoryMessage = `Based on your tax situation, here are some personalized recommendations:\\n`;
    const suggestions: string[] = [];

    // Generate recommendations based on context
    if (taxContext.income.w2.length > 0) {
      suggestions.push('Consider maximizing your retirement contributions to reduce taxable income');
    }

    const totalIncome = taxContext.income.w2.reduce((sum, w2) => sum + w2.wages, 0) +
                        taxContext.income.form1099.reduce((sum, f1099) => sum + f1099.amount, 0);
    if (userProfile.filingStatus === 'single' && totalIncome > 50000) {
      suggestions.push('Explore tax-advantaged investment accounts');
    }

    return this.createResponse(
      true,
      advisoryMessage + suggestions.join('\\n'),
      { suggestions },
      ['Generated based on your current tax profile'],
      0.85
    );
  }

  private async handleDocumentRequest(message: AgentMessage): Promise<AgentResponse> {
    return this.createResponse(
      true,
      'I can help you process your tax documents. Please upload your W-2, 1099, or other tax forms, and I\'ll extract the information automatically.',
      undefined,
      ['Document processing uses OCR and AI to extract data'],
      0.90
    );
  }

  private async handleGeneralConversation(message: AgentMessage): Promise<AgentResponse> {
    // Check if this is a form filling request
    if (this.isFormFillingRequest(message.content)) {
      return await this.handleAutomatedFormFilling(message);
    }

    // Generate AI response using LLM
    const systemPrompt = `You are a helpful tax assistant. Keep responses conversational and helpful.
When users mention income, deductions, or tax-related topics, be proactive about suggesting relevant forms.
If user wants to file taxes, guide them through step-by-step automated form filling.`;

    const messages: LLMMessage[] = [
      { role: 'system', content: systemPrompt },
      ...this.state.memory.conversationHistory.slice(-5).map(h => ({
        role: h.role === 'user' ? 'user' as const : 'assistant' as const,
        content: h.content
      })),
      { role: 'user', content: message.content }
    ];

    const response = await this.llmProvider.chat(messages, {
      temperature: 0.7,
      maxTokens: 500
    });

    // Analyze conversation for form suggestions
    const formSuggestions = this.analyzeForFormSuggestions(message.content, this.state.memory.conversationHistory);

    return this.createResponse(
      true,
      response.content,
      undefined,
      ['General assistance provided'],
      0.8,
      [],
      [],
      formSuggestions
    );
  }

  private analyzeForFormSuggestions(currentMessage: string, history: AgentMessage[]): TaxFormSuggestion[] {
  const suggestions: TaxFormSuggestion[] = [];
    const messageLower = currentMessage.toLowerCase();
    const fullConversation = [...history.map(h => h.content), currentMessage].join(' ').toLowerCase();

    // Check for 1040 form indicators
    if ((messageLower.includes('income') || messageLower.includes('wage') || messageLower.includes('salary')) &&
        (messageLower.includes('tax') || messageLower.includes('file') || messageLower.includes('return'))) {
      
  const suggestedFields: Record<string, string> = {};
      
      // Extract potential income information from conversation
      if (fullConversation.includes('wage') || fullConversation.includes('salary')) {
        suggestedFields['Line 1'] = 'Wages, salaries, tips (from W-2)';
      }
      if (fullConversation.includes('interest')) {
        suggestedFields['Line 2'] = 'Taxable interest';
      }
      if (fullConversation.includes('dividend')) {
        suggestedFields['Line 3'] = 'Qualified dividends';
      }

      if (Object.keys(suggestedFields).length > 0) {
        suggestions.push({
          id: `form-1040-${Date.now()}`,
          formType: '1040',
          formName: 'U.S. Individual Income Tax Return',
          confidence: 0.85,
          suggestedFields,
          reason: 'Based on your mention of income and tax filing, I can help fill out Form 1040'
        });
      }
    }

    // Check for Schedule A (itemized deductions)
    if (messageLower.includes('deduction') || messageLower.includes('itemize') || 
        messageLower.includes('charity') || messageLower.includes('medical') || messageLower.includes('mortgage')) {
      
      suggestions.push({
        id: `form-schedule-a-${Date.now()}`,
        formType: 'Schedule A',
        formName: 'Itemized Deductions',
        confidence: 0.75,
        suggestedFields: {
          'Medical and Dental Expenses': 'Medical expenses > 7.5% of AGI',
          'State and Local Taxes': 'State income/property taxes',
          'Home Mortgage Interest': 'Mortgage interest paid',
          'Charitable Contributions': 'Cash and non-cash donations'
        },
        reason: 'You mentioned deductions - Schedule A can help maximize your itemized deductions'
      });
    }

    // Check for W-4 form
    if (messageLower.includes('withholding') || messageLower.includes('w-4') || 
        messageLower.includes('too much') || messageLower.includes('refund') || messageLower.includes('owe')) {
      
      suggestions.push({
        id: `form-w4-${Date.now()}`,
        formType: 'W-4',
        formName: 'Employee\'s Withholding Certificate',
        confidence: 0.7,
        suggestedFields: {
          'Multiple Jobs': 'Extra withholding for multiple jobs',
          'Dependents': 'Number of dependents',
          'Other Income': 'Additional income sources',
          'Extra Withholding': 'Additional tax to withhold'
        },
        reason: 'Based on your withholding concerns, updating Form W-4 can optimize your tax situation'
      });
    }

    return suggestions;
  }

  private determineTargetAgent(task: AgentTask): AgentRole | null {
    const taskTypeToAgent: Record<string, AgentRole> = {
      'calculate_tax': 'tax_calculator',
      'calculate_credits': 'tax_calculator',
      'scenario_analysis': 'tax_calculator',
      'process_document': 'document_processor',
      'validate_compliance': 'compliance_checker',
      'provide_advice': 'tax_advisor',
      'fill_form': 'form_filler',
      'optimize_tax': 'optimization_analyzer'
    };

    return taskTypeToAgent[task.type] || null;
  }

  private buildContextMessage(): string {
    const { taxContext, userProfile } = this.state.memory;
    
    let context = '## User Profile:\n';
    context += `Expertise Level: ${userProfile.preferences.mode}\n`;
    context += `Filing Status: ${userProfile.filingStatus || 'Not specified'}\n`;
    context += `Dependents: ${userProfile.dependents || 0}\n\n`;

    context += '## Tax Context:\n';
    context += `Tax Year: ${taxContext.taxYear}\n`;

    if (taxContext.income.w2.length > 0) {
      context += `W-2 Income Sources: ${taxContext.income.w2.length}\n`;
    }

    if (taxContext.income.form1099.length > 0) {
      context += `1099 Income Sources: ${taxContext.income.form1099.length}\n`;
    }

    return context;
  }

  // Method to register additional specialized agents
  registerSpecializedAgent(role: AgentRole, agent: BaseAgent): void {
    this.specializedAgents.set(role, agent);
  }

  // Get status of all agents
  getAllAgentStatuses(): Record<string, unknown> {
    const statuses: Record<string, unknown> = {
      orchestrator: this.getState()
    };

    this.specializedAgents.forEach((agent, role) => {
      statuses[role] = agent.getState();
    });

    return statuses;
  }

  // ============================================================================
  // Automated Tax Filing Methods
  // ============================================================================

  private isFormFillingRequest(content: string): boolean {
    const keywords = [
      'file tax',
      'file taxes',
      'file my taxes',
      'i want to file my taxes',
      'fill form',
      'start filing',
      'help me file',
      'automated filing',
      'complete my taxes'
    ];
    return keywords.some(keyword => content.toLowerCase().includes(keyword));
  }

  private async handleAutomatedFormFilling(message: AgentMessage): Promise<AgentResponse> {
    // Check current step in tax filing workflow
    const currentStep = this.state.context['fillingStep'] || 'start';

    switch (currentStep) {
      case 'start':
        return await this.startTaxFilingWorkflow();
      case 'personal_info':
        return await this.collectPersonalInfo(message);
      case 'income':
        return await this.collectIncomeInfo(message);
      case 'deductions':
        return await this.collectDeductions(message);
      case 'review':
        return await this.reviewAndSubmit(message);
      default:
        return await this.startTaxFilingWorkflow();
    }
  }

  private async startTaxFilingWorkflow(): Promise<AgentResponse> {
    this.updateContext({ fillingStep: 'personal_info', workflowData: {} });

    const message = `🎯 **Let's file your taxes automatically!**

I'll guide you step-by-step through the tax filing process. I'll ask you questions and automatically fill out your tax forms.

**Step 1: Personal Information**

Let's start with some basic information:

1️⃣ What is your full name?
2️⃣ What is your Social Security Number (SSN)?
3️⃣ What is your filing status? (Single, Married Filing Jointly, Head of Household)

Please provide these details, and I'll automatically fill your Form 1040.`;

    return this.createResponse(
      true,
      message,
      undefined,
      ['Started automated tax filing workflow', 'Step 1: Collecting personal information'],
      1.0
    );
  }

  private async collectPersonalInfo(message: AgentMessage): Promise<AgentResponse> {
    // Extract personal information from message
    const userInput = message.content;
    const workflowData = this.state.context['workflowData'] || {};

    // Use LLM to extract structured data
    const extractionPrompt = `Extract the following information from the user's message:
- Full Name
- SSN (if provided)
- Filing Status (single, married filing jointly, head of household)

User message: "${userInput}"

Return in JSON format: { "name": "...", "ssn": "...", "filingStatus": "..." }`;

    try {
      const response = await this.llmProvider.chat([
        { role: 'system', content: 'You are a data extraction assistant. Extract information and return valid JSON only.' },
        { role: 'user', content: extractionPrompt }
      ], { temperature: 0, maxTokens: 200 });

      const extracted = JSON.parse(response);
      
      // Store extracted data
      workflowData.personalInfo = extracted;
      this.updateContext({ workflowData });

      // Move to next step
      this.updateContext({ fillingStep: 'income' });

      const nextMessage = `✅ **Personal Information Saved!**

📝 Form 1040 - Lines 1-5 have been automatically filled:
- Name: ${extracted.name}
- SSN: ${extracted.ssn ? '***-**-' + extracted.ssn.slice(-4) : 'Not provided'}
- Filing Status: ${extracted.filingStatus}

**Step 2: Income Information**

Now let's collect your income details:

1️⃣ Did you receive a W-2 from an employer?
   - If yes, what was your total wages (Box 1)?
   
2️⃣ Did you have any other income? (1099-INT, 1099-DIV, freelance work)
   - If yes, please describe the type and amount

I'll automatically calculate your Adjusted Gross Income (AGI) and fill Line 11 on Form 1040.`;

      return this.createResponse(
        true,
        nextMessage,
        undefined,
        ['Extracted personal information', 'Filled Form 1040 lines 1-5', 'Moving to income collection'],
        0.95
      );

    } catch (error) {
      return this.createResponse(
        false,
        `I had trouble extracting your information. Could you please provide:
1. Your full name
2. Your filing status (Single/Married/Head of Household)

in a clear format?`,
        undefined,
        ['Failed to extract personal information'],
        0.3
      );
    }
  }

  private async collectIncomeInfo(message: AgentMessage): Promise<AgentResponse> {
    const userInput = message.content;
    const workflowData = this.state.context['workflowData'] || {};

    // Extract income information
    const extractionPrompt = `Extract income information from the user's message:
- W-2 wages amount
- Other income (1099-INT, 1099-DIV, self-employment, etc.) with amounts
- Any other sources of income

User message: "${userInput}"

Return in JSON format: { "w2Wages": number, "otherIncome": [{"type": "...", "amount": number}] }`;

    try {
      const response = await this.llmProvider.chat([
        { role: 'system', content: 'You are a data extraction assistant. Extract income information and return valid JSON only.' },
        { role: 'user', content: extractionPrompt }
      ], { temperature: 0, maxTokens: 200 });

      const extracted = JSON.parse(response);
      
      // Calculate total income
      const w2Income = extracted.w2Wages || 0;
  const otherIncome = (extracted.otherIncome || []).reduce((sum: number, item: { amount: number }) => sum + (item?.amount || 0), 0);
      const totalIncome = w2Income + otherIncome;
      const agi = totalIncome; // Simplified - actual AGI calculation is more complex

      workflowData.incomeInfo = extracted;
      workflowData.calculations = { totalIncome, agi };
      this.updateContext({ workflowData });

      // Move to next step
      this.updateContext({ fillingStep: 'deductions' });

      const nextMessage = `✅ **Income Information Saved!**

📝 Form 1040 - Income section automatically filled:
- Line 1 (W-2 Wages): $${w2Income.toLocaleString()}
${extracted.otherIncome && extracted.otherIncome.length > 0 ? '- Other Income: $' + otherIncome.toLocaleString() : ''}
- Line 9 (Total Income): $${totalIncome.toLocaleString()}
- Line 11 (Adjusted Gross Income): $${agi.toLocaleString()}

**Step 3: Deductions**

Now let's determine your deductions:

1️⃣ Do you want to take the Standard Deduction or Itemize?
   - Standard Deduction 2024: $14,600 (Single)
   
2️⃣ If itemizing, do you have:
   - Mortgage interest?
   - State/local taxes paid?
   - Charitable contributions?
   - Medical expenses?

I'll automatically calculate which option gives you the lowest tax and fill Schedule A if needed.`;

      return this.createResponse(
        true,
        nextMessage,
        undefined,
        ['Extracted income information', 'Calculated AGI', 'Filled Form 1040 income section'],
        0.95
      );

    } catch (error) {
      return this.createResponse(
        false,
        `I had trouble extracting your income. Could you please provide:
1. Your W-2 wages (if applicable)
2. Any other income sources and amounts

in a clear format?`,
        undefined,
        ['Failed to extract income information'],
        0.3
      );
    }
  }

  private async collectDeductions(message: AgentMessage): Promise<AgentResponse> {
    const userInput = message.content;
    const workflowData = this.state.context['workflowData'] || {};

    // Extract deduction preference
    const wantsStandard = userInput.toLowerCase().includes('standard');
    const wantsItemize = userInput.toLowerCase().includes('itemize');

    const agi = workflowData.calculations?.agi || 0;
    const standardDeduction = 14600; // 2024 Single filer

    // Extract itemized deductions if mentioned
    const extractionPrompt = `Extract itemized deductions from the user's message:
- Mortgage interest
- State/local taxes
- Charitable contributions
- Medical expenses

User message: "${userInput}"

Return in JSON format: { "mortgageInterest": number, "stateTaxes": number, "charitable": number, "medical": number }`;

    try {
      let deductionAmount = standardDeduction;
      let deductionType = 'standard';
      let itemizedTotal = 0;

      if (wantsItemize || (!wantsStandard && userInput.match(/\$\d+/))) {
        const response = await this.llmProvider.chat([
          { role: 'system', content: 'You are a data extraction assistant. Extract deduction amounts and return valid JSON only. Use 0 for missing values.' },
          { role: 'user', content: extractionPrompt }
        ], { temperature: 0, maxTokens: 200 });

        const extracted = JSON.parse(response);
        itemizedTotal = (extracted.mortgageInterest || 0) + (extracted.stateTaxes || 0) + 
                       (extracted.charitable || 0) + (extracted.medical || 0);

        if (itemizedTotal > standardDeduction) {
          deductionAmount = itemizedTotal;
          deductionType = 'itemized';
          workflowData.itemizedDeductions = extracted;
        }
      }

      // Calculate taxable income
      const taxableIncome = Math.max(0, agi - deductionAmount);
      
      // Calculate tax (simplified 2024 tax brackets for single filer)
      let tax = 0;
      if (taxableIncome <= 11600) {
        tax = taxableIncome * 0.10;
      } else if (taxableIncome <= 47150) {
        tax = 1160 + (taxableIncome - 11600) * 0.12;
      } else if (taxableIncome <= 100525) {
        tax = 5426 + (taxableIncome - 47150) * 0.22;
      } else {
        tax = 17168.50 + (taxableIncome - 100525) * 0.24;
      }

      workflowData.deductions = {
        type: deductionType,
        amount: deductionAmount,
        itemizedTotal: deductionType === 'itemized' ? itemizedTotal : 0
      };
      workflowData.calculations.taxableIncome = taxableIncome;
      workflowData.calculations.tax = Math.round(tax);
      
      this.updateContext({ workflowData });

      // Move to review step
      this.updateContext({ fillingStep: 'review' });

      const nextMessage = `✅ **Deductions Calculated!**

📝 Form 1040 - Deductions automatically filled:
- Line 12 (Deduction Type): ${deductionType === 'standard' ? 'Standard Deduction' : 'Itemized (Schedule A)'}
- Line 12 (Deduction Amount): $${deductionAmount.toLocaleString()}
${deductionType === 'itemized' ? `
  📋 Schedule A filled:
  - Mortgage Interest: $${workflowData.itemizedDeductions.mortgageInterest || 0}
  - State/Local Taxes: $${workflowData.itemizedDeductions.stateTaxes || 0}
  - Charitable Contributions: $${workflowData.itemizedDeductions.charitable || 0}
` : ''}
- Line 15 (Taxable Income): $${taxableIncome.toLocaleString()}
- Line 24 (Total Tax): $${workflowData.calculations.tax.toLocaleString()}

**Step 4: Review & Submit**

🎉 Your tax return is almost complete! Here's a summary:

**Form 1040 Summary:**
- Total Income: $${agi.toLocaleString()}
- Deductions: $${deductionAmount.toLocaleString()}
- Taxable Income: $${taxableIncome.toLocaleString()}
- Tax Owed: $${workflowData.calculations.tax.toLocaleString()}

Would you like to:
1️⃣ Review the complete form
2️⃣ Make any changes
3️⃣ Submit your tax return

Type "submit" to file your taxes, or ask me to review/change any section.`;

      return this.createResponse(
        true,
        nextMessage,
        undefined,
        ['Calculated deductions', 'Computed tax liability', 'Form 1040 nearly complete'],
        0.98
      );

    } catch (error) {
      return this.createResponse(
        false,
        `I had trouble processing your deductions. Would you like to take the standard deduction of $${standardDeduction.toLocaleString()}?

Type "yes" for standard deduction or provide your itemized deduction details.`,
        undefined,
        ['Failed to process deductions'],
        0.3
      );
    }
  }

  private async reviewAndSubmit(message: AgentMessage): Promise<AgentResponse> {
    const userInput = message.content.toLowerCase();
    const workflowData = this.state.context['workflowData'] || {};

    if (userInput.includes('submit') || userInput.includes('file')) {
      // Reset workflow
      this.updateContext({ fillingStep: 'start', workflowData: {} });

      const finalMessage = `✅ **Tax Return Successfully Filed!**

🎉 Congratulations! Your 2024 tax return has been completed and is ready for submission.

📊 **Final Summary:**
- Name: ${workflowData.personalInfo?.name}
- Filing Status: ${workflowData.personalInfo?.filingStatus}
- AGI: $${workflowData.calculations?.agi.toLocaleString()}
- Tax: $${workflowData.calculations?.tax.toLocaleString()}

📝 **Forms Completed:**
✅ Form 1040 (U.S. Individual Income Tax Return)
${workflowData.deductions?.type === 'itemized' ? '✅ Schedule A (Itemized Deductions)' : ''}

📧 Your tax return has been saved and is ready for e-filing or printing.

Need help with anything else? Ask me about:
- Estimated payments for next year
- Tax planning strategies
- Deduction optimization`;

      return this.createResponse(
        true,
        finalMessage,
        undefined,
        ['Tax return completed', 'Forms ready for submission'],
        1.0
      );
    } else {
      return this.createResponse(
        true,
        `I can help you review or make changes. What would you like to do?

- Type "review" to see the complete form
- Tell me which section to change (personal info, income, or deductions)
- Type "submit" when ready to file

Your current tax: $${workflowData.calculations?.tax.toLocaleString()}`,
        undefined,
        ['Waiting for user decision'],
        0.9
      );
    }
  }
}
