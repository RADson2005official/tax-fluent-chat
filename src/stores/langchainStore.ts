// LangChain Integration with existing agent store
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { LangChainTaxAgent, type LangChainAgentConfig } from '@/agents/langchain/LangChainAgent';
import { TaxFilingOrchestrator, type TaxFilingWorkflow, type WorkflowStep } from '@/agents/langchain/WorkflowOrchestrator';
import type { AgentContext } from '@/agents/langchain/LangChainTools';

export const useLangChainStore = defineStore('langchain', () => {
  // State
  const agent = ref<LangChainTaxAgent | null>(null);
  const orchestrator = ref<TaxFilingOrchestrator | null>(null);
  const isInitialized = ref(false);
  const isProcessing = ref(false);
  const currentWorkflow = ref<TaxFilingWorkflow | null>(null);
  const workflowHistory = ref<TaxFilingWorkflow[]>([]);
  
  const config = ref<LangChainAgentConfig>({
    provider: 'openai',
    model: 'gpt-4o',
    temperature: 0.7,
    maxTokens: 2000,
  });

  // Computed
  const workflowProgress = computed(() => {
    if (!currentWorkflow.value) return 0;
    const completed = currentWorkflow.value.steps.filter(s => s.status === 'completed').length;
    return (completed / currentWorkflow.value.steps.length) * 100;
  });

  const currentStep = computed(() => {
    if (!currentWorkflow.value) return null;
    return currentWorkflow.value.steps[currentWorkflow.value.currentStepIndex];
  });

  // Actions
  function initialize(providerConfig?: Partial<LangChainAgentConfig>) {
    if (providerConfig) {
      config.value = { ...config.value, ...providerConfig };
    }

    agent.value = new LangChainTaxAgent(config.value);
    orchestrator.value = new TaxFilingOrchestrator(config.value);
    isInitialized.value = true;
    
    console.log('LangChain agent system initialized with config:', config.value);
  }

  async function sendMessage(
    message: string,
    userId: string,
    taxYear: number = 2024
  ) {
    if (!agent.value) {
      initialize();
    }

    isProcessing.value = true;

    try {
      const context: AgentContext = {
        userId,
        taxYear,
        conversationId: currentWorkflow.value?.id,
      };

      const response = await agent.value!.processMessage(
        message,
        context,
        currentWorkflow.value?.conversationHistory || []
      );

      return {
        success: true,
        message: response.response,
        structuredResponse: response.structuredResponse,
        toolCalls: response.toolCalls,
        reasoning: response.reasoning,
      };
    } catch (error) {
      console.error('LangChain agent error:', error);
      return {
        success: false,
        message: error instanceof Error ? error.message : 'An error occurred',
        error: error,
      };
    } finally {
      isProcessing.value = false;
    }
  }

  async function startWorkflow(
    userId: string,
    taxYear: number = 2024
  ) {
    if (!orchestrator.value) {
      initialize();
    }

    isProcessing.value = true;

    try {
      const workflow = await orchestrator.value!.initializeWorkflow(userId, taxYear);
      currentWorkflow.value = workflow;
      workflowHistory.value.push(workflow);

      return {
        success: true,
        workflowId: workflow.id,
        workflow,
      };
    } catch (error) {
      console.error('Workflow initialization error:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to start workflow',
      };
    } finally {
      isProcessing.value = false;
    }
  }

  async function executeWorkflowStep(
    stepId: string,
    input?: Record<string, unknown>
  ) {
    if (!orchestrator.value || !currentWorkflow.value) {
      throw new Error('Workflow not initialized');
    }

    isProcessing.value = true;

    try {
      const step = await orchestrator.value.executeStep(
        currentWorkflow.value.id,
        stepId,
        input
      );

      // Update current workflow
      currentWorkflow.value = orchestrator.value.getWorkflowStatus(currentWorkflow.value.id)!;

      return {
        success: true,
        step,
        workflow: currentWorkflow.value,
      };
    } catch (error) {
      console.error('Step execution error:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Step execution failed',
      };
    } finally {
      isProcessing.value = false;
    }
  }

  async function executeFullWorkflow(
    userId: string,
    taxYear: number,
    initialData: Record<string, unknown>
  ) {
    if (!orchestrator.value) {
      initialize();
    }

    isProcessing.value = true;

    try {
      // Start workflow
      const { workflowId, workflow } = await startWorkflow(userId, taxYear);
      
      if (!workflowId) {
        throw new Error('Failed to initialize workflow');
      }

      // Execute all steps
      const completedWorkflow = await orchestrator.value!.executeFullWorkflow(
        workflowId,
        initialData
      );

      currentWorkflow.value = completedWorkflow;

      return {
        success: true,
        workflow: completedWorkflow,
      };
    } catch (error) {
      console.error('Full workflow execution error:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Workflow execution failed',
      };
    } finally {
      isProcessing.value = false;
    }
  }

  async function* streamWorkflow(
    userId: string,
    taxYear: number,
    initialData: Record<string, unknown>
  ) {
    if (!orchestrator.value) {
      initialize();
    }

    const { workflowId } = await startWorkflow(userId, taxYear);
    
    if (!workflowId) {
      throw new Error('Failed to initialize workflow');
    }

    for await (const update of orchestrator.value!.streamWorkflow(workflowId, initialData)) {
      if (update.type === 'step_complete' || update.type === 'workflow_complete') {
        // Update current workflow state
        currentWorkflow.value = orchestrator.value!.getWorkflowStatus(workflowId)!;
      }
      
      yield update;
    }
  }

  function setProvider(providerConfig: Partial<LangChainAgentConfig>) {
    config.value = { ...config.value, ...providerConfig };
    
    // Reinitialize agents
    if (isInitialized.value) {
      initialize(providerConfig);
    }
  }

  function reset() {
    currentWorkflow.value = null;
    isProcessing.value = false;
  }

  return {
    // State
    agent,
    orchestrator,
    isInitialized,
    isProcessing,
    currentWorkflow,
    workflowHistory,
    config,
    
    // Computed
    workflowProgress,
    currentStep,
    
    // Actions
    initialize,
    sendMessage,
    startWorkflow,
    executeWorkflowStep,
    executeFullWorkflow,
    streamWorkflow,
    setProvider,
    reset,
  };
});
