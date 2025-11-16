// Multi-Agent Workflow Orchestrator using LangChain
import { LangChainTaxAgent, type LangChainAgentConfig } from './LangChainAgent';
import { type AgentContext, TaxFilingResponseFormat } from './LangChainTools';
import { HumanMessage, AIMessage, type BaseMessage } from "@langchain/core/messages";

export interface WorkflowStep {
  id: string;
  name: string;
  description: string;
  status: 'pending' | 'in-progress' | 'completed' | 'failed' | 'skipped';
  agent: 'document' | 'calculator' | 'compliance' | 'advisor' | 'orchestrator';
  input?: Record<string, unknown>;
  output?: unknown;
  error?: string;
  startTime?: Date;
  endTime?: Date;
}

export interface TaxFilingWorkflow {
  id: string;
  userId: string;
  taxYear: number;
  status: 'initialized' | 'in-progress' | 'completed' | 'failed';
  steps: WorkflowStep[];
  currentStepIndex: number;
  conversationHistory: BaseMessage[];
  extractedData: Record<string, unknown>;
  calculatedTax: Record<string, unknown>;
  complianceResults: Record<string, unknown>;
  formsGenerated: string[];
  createdAt: Date;
  updatedAt: Date;
}

export class TaxFilingOrchestrator {
  private agent: LangChainTaxAgent;
  private workflows: Map<string, TaxFilingWorkflow> = new Map();

  constructor(config: LangChainAgentConfig) {
    this.agent = new LangChainTaxAgent(config);
  }

  /**
   * Initialize a new tax filing workflow
   */
  async initializeWorkflow(
    userId: string,
    taxYear: number = 2024
  ): Promise<TaxFilingWorkflow> {
    const workflowId = `wf-${userId}-${taxYear}-${Date.now()}`;

    const workflow: TaxFilingWorkflow = {
      id: workflowId,
      userId,
      taxYear,
      status: 'initialized',
      currentStepIndex: 0,
      conversationHistory: [],
      extractedData: {},
      calculatedTax: {},
      complianceResults: {},
      formsGenerated: [],
      createdAt: new Date(),
      updatedAt: new Date(),
      steps: [
        {
          id: 'step-1-intake',
          name: 'Information Intake',
          description: 'Gather taxpayer information and uploaded documents',
          status: 'pending',
          agent: 'orchestrator',
        },
        {
          id: 'step-2-document-processing',
          name: 'Document Processing',
          description: 'Extract data from W-2, 1099, receipts using OCR and AI',
          status: 'pending',
          agent: 'document',
        },
        {
          id: 'step-3-data-validation',
          name: 'Data Validation',
          description: 'Verify extracted data completeness and accuracy',
          status: 'pending',
          agent: 'orchestrator',
        },
        {
          id: 'step-4-tax-calculation',
          name: 'Tax Calculation',
          description: 'Calculate federal tax, deductions, and credits',
          status: 'pending',
          agent: 'calculator',
        },
        {
          id: 'step-5-compliance-check',
          name: 'Compliance Validation',
          description: 'Validate calculations against IRS regulations',
          status: 'pending',
          agent: 'compliance',
        },
        {
          id: 'step-6-optimization',
          name: 'Tax Optimization',
          description: 'Identify tax-saving opportunities and recommendations',
          status: 'pending',
          agent: 'advisor',
        },
        {
          id: 'step-7-form-generation',
          name: 'Form Generation',
          description: 'Generate and fill required tax forms (1040, schedules)',
          status: 'pending',
          agent: 'orchestrator',
        },
        {
          id: 'step-8-final-review',
          name: 'Final Review',
          description: 'Review completed forms and prepare for submission',
          status: 'pending',
          agent: 'orchestrator',
        },
      ],
    };

    this.workflows.set(workflowId, workflow);
    return workflow;
  }

  /**
   * Execute a specific workflow step
   */
  async executeStep(
    workflowId: string,
    stepId: string,
    input?: Record<string, unknown>
  ): Promise<WorkflowStep> {
    const workflow = this.workflows.get(workflowId);
    if (!workflow) {
      throw new Error(`Workflow ${workflowId} not found`);
    }

    const step = workflow.steps.find((s) => s.id === stepId);
    if (!step) {
      throw new Error(`Step ${stepId} not found in workflow`);
    }

    // Update step status
    step.status = 'in-progress';
    step.startTime = new Date();
    step.input = input;
    workflow.updatedAt = new Date();

    try {
      const context: AgentContext = {
        userId: workflow.userId,
        taxYear: workflow.taxYear,
        conversationId: workflowId,
      };

      let prompt = '';
      
      // Build prompts based on step type
      switch (step.id) {
        case 'step-1-intake':
          prompt = 'Welcome the user and explain the tax filing process. Ask what documents they have ready.';
          break;
        
        case 'step-2-document-processing':
          prompt = `Process the following tax documents and extract all relevant data: ${JSON.stringify(input)}. Use OCR and AI extraction tools.`;
          break;
        
        case 'step-3-data-validation':
          prompt = `Validate the extracted tax data for completeness and accuracy: ${JSON.stringify(workflow.extractedData)}. Identify any missing information.`;
          break;
        
        case 'step-4-tax-calculation':
          prompt = `Calculate federal tax liability using the extracted data: ${JSON.stringify(workflow.extractedData)}. Include all applicable deductions and credits.`;
          break;
        
        case 'step-5-compliance-check':
          prompt = `Validate the tax calculation against IRS regulations: ${JSON.stringify(workflow.calculatedTax)}. Check for compliance issues and flag any warnings.`;
          break;
        
        case 'step-6-optimization':
          prompt = `Analyze the tax situation and provide optimization recommendations: ${JSON.stringify({ extracted: workflow.extractedData, calculated: workflow.calculatedTax })}`;
          break;
        
        case 'step-7-form-generation':
          prompt = `Generate and fill the required tax forms using the calculated data: ${JSON.stringify(workflow.calculatedTax)}`;
          break;
        
        case 'step-8-final-review':
          prompt = 'Provide a comprehensive summary of the tax filing, including estimated tax/refund, forms completed, and next steps for submission.';
          break;
        
        default:
          prompt = `Execute workflow step: ${step.name}`;
      }

      // Execute using LangChain agent
      const result = await this.agent.processMessage(
        prompt,
        context,
        workflow.conversationHistory
      );

      // Update workflow history
      workflow.conversationHistory.push(new HumanMessage(prompt));
      workflow.conversationHistory.push(new AIMessage(result.response));

      // Store results in appropriate workflow fields
      if (step.id === 'step-2-document-processing') {
        // Extract data from tool calls
        const extractedData = result.toolCalls
          .filter((tc) => tc.tool.includes('extract'))
          .reduce((acc, tc) => ({ ...acc, ...tc.output }), {});
        workflow.extractedData = extractedData;
      } else if (step.id === 'step-4-tax-calculation') {
        const calculatedData = result.toolCalls
          .filter((tc) => tc.tool.includes('calculate'))
          .reduce((acc, tc) => ({ ...acc, ...tc.output }), {});
        workflow.calculatedTax = calculatedData;
      } else if (step.id === 'step-5-compliance-check') {
        const complianceData = result.toolCalls
          .filter((tc) => tc.tool.includes('compliance') || tc.tool.includes('validate'))
          .reduce((acc, tc) => ({ ...acc, ...tc.output }), {});
        workflow.complianceResults = complianceData;
      } else if (step.id === 'step-7-form-generation') {
        const forms = result.toolCalls
          .filter((tc) => tc.tool.includes('form'))
          .map((tc) => tc.tool);
        workflow.formsGenerated = forms;
      }

      // Mark step as completed
      step.status = 'completed';
      step.endTime = new Date();
      step.output = {
        response: result.response,
        structuredResponse: result.structuredResponse,
        toolCalls: result.toolCalls,
        reasoning: result.reasoning,
      };

      // Move to next step
      workflow.currentStepIndex++;
      workflow.updatedAt = new Date();

      return step;
    } catch (error) {
      step.status = 'failed';
      step.endTime = new Date();
      step.error = error instanceof Error ? error.message : String(error);
      workflow.updatedAt = new Date();
      throw error;
    }
  }

  /**
   * Execute the entire workflow autonomously
   */
  async executeFullWorkflow(
    workflowId: string,
    initialData: Record<string, unknown>
  ): Promise<TaxFilingWorkflow> {
    const workflow = this.workflows.get(workflowId);
    if (!workflow) {
      throw new Error(`Workflow ${workflowId} not found`);
    }

    workflow.status = 'in-progress';

    try {
      // Execute each step in sequence
      for (const step of workflow.steps) {
        let stepInput: Record<string, unknown> = {};

        // Prepare input based on step
        if (step.id === 'step-1-intake') {
          stepInput = initialData;
        } else if (step.id === 'step-2-document-processing') {
          stepInput = { documents: initialData.documents || [] };
        }

        await this.executeStep(workflowId, step.id, stepInput);

        // Check for failures
        if (step.status === 'failed') {
          workflow.status = 'failed';
          return workflow;
        }
      }

      workflow.status = 'completed';
      workflow.updatedAt = new Date();
      return workflow;
    } catch (error) {
      workflow.status = 'failed';
      workflow.updatedAt = new Date();
      throw error;
    }
  }

  /**
   * Get workflow status
   */
  getWorkflowStatus(workflowId: string): TaxFilingWorkflow | undefined {
    return this.workflows.get(workflowId);
  }

  /**
   * Stream workflow execution with real-time updates
   */
  async *streamWorkflow(
    workflowId: string,
    initialData: Record<string, unknown>
  ): AsyncGenerator<{
    type: 'step_start' | 'step_progress' | 'step_complete' | 'workflow_complete' | 'error';
    step?: WorkflowStep;
    message: string;
    data?: unknown;
  }> {
    const workflow = this.workflows.get(workflowId);
    if (!workflow) {
      yield {
        type: 'error',
        message: `Workflow ${workflowId} not found`,
      };
      return;
    }

    workflow.status = 'in-progress';

    try {
      for (const step of workflow.steps) {
        yield {
          type: 'step_start',
          step,
          message: `Starting: ${step.name}`,
        };

        let stepInput: Record<string, unknown> = {};
        if (step.id === 'step-1-intake') {
          stepInput = initialData;
        } else if (step.id === 'step-2-document-processing') {
          stepInput = { documents: initialData.documents || [] };
        }

        await this.executeStep(workflowId, step.id, stepInput);

        yield {
          type: 'step_complete',
          step,
          message: `Completed: ${step.name}`,
          data: step.output,
        };

        if (step.status === 'failed') {
          yield {
            type: 'error',
            step,
            message: `Step failed: ${step.error}`,
          };
          return;
        }
      }

      workflow.status = 'completed';
      yield {
        type: 'workflow_complete',
        message: 'Tax filing workflow completed successfully',
        data: workflow,
      };
    } catch (error) {
      workflow.status = 'failed';
      yield {
        type: 'error',
        message: error instanceof Error ? error.message : String(error),
      };
    }
  }
}
