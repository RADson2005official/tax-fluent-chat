# AI Agent System API Reference

## Agent Store API

The main interface for interacting with the AI agent system.

### Import

```typescript
import { useAgentStore } from '@/stores/agentStore';
```

### Initialization

#### `initialize()`

Initializes the AI agent system and creates the orchestrator agent.

```typescript
const agentStore = useAgentStore();
agentStore.initialize();
```

**Returns**: `void`

### State Properties

#### `isInitialized: Ref<boolean>`

Whether the agent system has been initialized.

```typescript
console.log(agentStore.isInitialized); // true/false
```

#### `isProcessing: Ref<boolean>`

Whether an agent is currently processing a request.

```typescript
if (agentStore.isProcessing) {
  console.log('Agent is working...');
}
```

#### `messageHistory: Ref<AgentMessage[]>`

Array of all messages exchanged with the agent system.

```typescript
agentStore.messageHistory.forEach(msg => {
  console.log(`${msg.role}: ${msg.content}`);
});
```

#### `currentAgentStatuses: Ref<Record<string, AgentState>>`

Current status of all agents in the system.

```typescript
console.log(agentStore.currentAgentStatuses);
// {
//   orchestrator: { role: 'orchestrator', status: 'idle', ... },
//   tax_calculator: { role: 'tax_calculator', status: 'working', ... }
// }
```

#### `lastResponse: Ref<AgentResponse | null>`

The most recent agent response.

```typescript
if (agentStore.lastResponse) {
  console.log(agentStore.lastResponse.message);
  console.log(agentStore.lastResponse.confidence);
}
```

### Computed Properties

#### `allAgentsIdle: ComputedRef<boolean>`

Whether all agents are idle (not processing).

```typescript
if (agentStore.allAgentsIdle) {
  console.log('All agents ready');
}
```

#### `activeAgents: ComputedRef<string[]>`

Array of currently active (non-idle) agent roles.

```typescript
console.log(agentStore.activeAgents);
// ['tax_calculator', 'compliance_checker']
```

### Core Methods

#### `sendMessage(messageContent: string): Promise<AgentResponse>`

Send a natural language message to the agent system.

**Parameters:**
- `messageContent` (string): The message to send

**Returns:** Promise<AgentResponse>

```typescript
const response = await agentStore.sendMessage(
  "How much tax will I owe on $75,000?"
);

console.log(response.message);    // AI response text
console.log(response.reasoning);  // Explanation steps
console.log(response.data);       // Structured data
console.log(response.confidence); // Confidence score (0-1)
```

#### `processTask(taskType: string, taskInput: any): Promise<AgentResponse>`

Process a specific task using the appropriate agent.

**Parameters:**
- `taskType` (string): Type of task (e.g., 'calculate_tax', 'process_document')
- `taskInput` (any): Input data for the task

**Returns:** Promise<AgentResponse>

```typescript
const response = await agentStore.processTask('calculate_tax', {
  taxableIncome: 75000,
  filingStatus: 'single'
});
```

#### `clearHistory(): void`

Clear message history and last response.

```typescript
agentStore.clearHistory();
```

#### `updateAgentStatuses(): void`

Manually update agent status information.

```typescript
agentStore.updateAgentStatuses();
```

#### `getAgentState(agentRole: string): AgentState | null`

Get the state of a specific agent.

**Parameters:**
- `agentRole` (string): The agent role to query

**Returns:** AgentState | null

```typescript
const state = agentStore.getAgentState('tax_calculator');
console.log(state.status); // 'idle', 'thinking', 'working', etc.
```

### Tax-Specific Helper Methods

#### `calculateTax(taxData: TaxCalculationInput): Promise<AgentResponse>`

Calculate federal income tax.

**Parameters:**
```typescript
interface TaxCalculationInput {
  taxableIncome: number;
  filingStatus: 'single' | 'married_joint' | 'married_separate' | 'head_of_household';
}
```

**Returns:** Promise<AgentResponse>

```typescript
const result = await agentStore.calculateTax({
  taxableIncome: 75000,
  filingStatus: 'single'
});

// Access results
console.log(result.data.totalTax);        // 12358
console.log(result.data.effectiveRate);   // "16.5%"
console.log(result.data.marginalRate);    // "22%"
console.log(result.data.breakdown);       // Array of tax by bracket
```

#### `calculateCredits(creditData: CreditCalculationInput): Promise<AgentResponse>`

Calculate available tax credits.

**Parameters:**
```typescript
interface CreditCalculationInput {
  dependents: number;
  agi: number;
  filingStatus: string;
  earnedIncome?: number;
}
```

**Returns:** Promise<AgentResponse>

```typescript
const result = await agentStore.calculateCredits({
  dependents: 2,
  agi: 75000,
  filingStatus: 'married_joint',
  earnedIncome: 70000
});

// Access results
console.log(result.data.childTaxCredit); // { credit: 4000, ... }
console.log(result.data.eitc);           // { credit: 3500, ... }
```

#### `analyzeScenarios(scenarios: TaxScenario[]): Promise<AgentResponse>`

Compare multiple tax scenarios.

**Parameters:**
```typescript
interface TaxScenario {
  name: string;
  taxableIncome: number;
  totalTax: number;
  effectiveRate: string;
  refundOrOwed: number;
}
```

**Returns:** Promise<AgentResponse>

```typescript
const result = await agentStore.analyzeScenarios([
  {
    name: 'Standard Deduction',
    taxableIncome: 60000,
    totalTax: 8500,
    effectiveRate: '14.2%',
    refundOrOwed: -1200
  },
  {
    name: 'Itemized Deduction',
    taxableIncome: 55000,
    totalTax: 7800,
    effectiveRate: '14.2%',
    refundOrOwed: -1900
  }
]);

console.log(result.data.bestScenario);      // "Itemized Deduction"
console.log(result.data.potentialSavings);  // 700
```

#### `processDocument(documentData: any): Promise<AgentResponse>`

Process uploaded tax documents.

**Parameters:**
- `documentData` (any): Document data or file information

**Returns:** Promise<AgentResponse>

```typescript
const result = await agentStore.processDocument({
  type: 'w2',
  employer: 'ABC Corp',
  wages: 75000,
  federalWithheld: 12000
});

console.log(result.data.extractedData);
console.log(result.data.confidence);
```

#### `getAdvisory(context: any): Promise<AgentResponse>`

Get personalized tax advisory.

**Parameters:**
- `context` (any): Tax context and user information

**Returns:** Promise<AgentResponse>

```typescript
const result = await agentStore.getAdvisory({
  income: { total: 75000 },
  filingStatus: 'single',
  dependents: 0
});

console.log(result.suggestions);  // Array of recommendations
```

## Type Definitions

### AgentResponse

```typescript
interface AgentResponse {
  agentRole: AgentRole;
  success: boolean;
  message: string;
  data?: any;
  reasoning?: string[];
  confidence?: number;
  suggestions?: string[];
  nextActions?: string[];
}
```

### AgentMessage

```typescript
interface AgentMessage {
  id: string;
  role: 'user' | 'agent' | 'system' | 'tool';
  content: string;
  agentRole?: AgentRole;
  timestamp: Date;
  metadata?: Record<string, any>;
  toolCalls?: ToolCall[];
  reasoning?: string;
}
```

### AgentState

```typescript
interface AgentState {
  role: AgentRole;
  status: 'idle' | 'thinking' | 'working' | 'waiting' | 'error' | 'completed';
  currentTask?: string;
  memory: AgentMemory;
  context: Record<string, any>;
  error?: string;
}
```

### AgentRole

```typescript
type AgentRole = 
  | 'orchestrator'
  | 'tax_calculator'
  | 'document_processor'
  | 'compliance_checker'
  | 'tax_advisor'
  | 'form_filler'
  | 'optimization_analyzer';
```

## Tool API

### Using Tools Directly

```typescript
import { getToolByName } from '@/agents/tools';

// Get a specific tool
const tool = getToolByName('calculate_income_tax');

// Execute the tool
const result = await tool.execute({
  taxableIncome: 75000,
  filingStatus: 'single'
}, context);
```

### Available Tools

#### Tax Calculation Tools

- `calculate_income_tax` - Calculate federal income tax
- `calculate_agi` - Calculate Adjusted Gross Income
- `calculate_taxable_income` - Calculate taxable income
- `calculate_child_tax_credit` - Calculate Child Tax Credit
- `calculate_eitc` - Calculate Earned Income Tax Credit
- `compare_scenarios` - Compare tax scenarios

#### Document Processing Tools

- `extract_w2_data` - Extract W-2 form data
- `extract_1099_data` - Extract 1099 form data
- `validate_document_data` - Validate extracted data
- `classify_document` - Classify document type

#### Compliance Tools

- `check_filing_requirements` - Check filing requirements
- `validate_deductions` - Validate deductions
- `verify_credits` - Verify credit eligibility
- `detect_errors` - Detect filing errors

#### Advisory Tools

- `analyze_tax_situation` - Analyze overall tax situation
- `recommend_strategies` - Recommend tax strategies
- `explain_concept` - Explain tax concepts

#### Form Filling Tools

- `map_data_to_form` - Map data to form fields
- `validate_form_fields` - Validate form fields
- `determine_required_forms` - Determine required forms

#### Optimization Tools

- `compare_deduction_methods` - Compare standard vs itemized
- `find_eligible_credits` - Find eligible credits
- `analyze_timing` - Analyze timing strategies

## Explainable AI API

### Using the XAI System

```typescript
import { ExplainableAI } from '@/agents/xai/ExplainableAI';

// Generate explanation for tax calculation
const explanation = ExplainableAI.explainTaxCalculation(
  { taxableIncome: 75000, filingStatus: 'single' },
  taxResult
);

// Convert to natural language
const text = ExplainableAI.toNaturalLanguage(explanation);
console.log(text);
```

### Explanation Methods

#### `explainTaxCalculation(input, result): Explanation`

Generate explanation for tax calculations.

#### `explainCreditEligibility(creditType, input, result): Explanation`

Generate explanation for credit eligibility.

#### `explainDeductionStrategy(input, recommendation): Explanation`

Generate explanation for deduction recommendations.

#### `explainComplianceCheck(checkType, input, result): Explanation`

Generate explanation for compliance checks.

#### `toNaturalLanguage(explanation): string`

Convert structured explanation to natural language text.

## Error Handling

### API Errors

```typescript
try {
  const result = await agentStore.calculateTax({
    taxableIncome: 75000,
    filingStatus: 'single'
  });
} catch (error) {
  console.error('Tax calculation failed:', error);
  // Handle error
}
```

### Agent Failures

```typescript
const result = await agentStore.sendMessage("Calculate my tax");

if (!result.success) {
  console.error('Agent error:', result.message);
  // Handle failure
}
```

## Best Practices

1. **Always Initialize**
   ```typescript
   agentStore.initialize();
   ```

2. **Check Processing State**
   ```typescript
   if (!agentStore.isProcessing) {
     await agentStore.sendMessage(userInput);
   }
   ```

3. **Handle Errors**
   ```typescript
   try {
     const result = await agentStore.calculateTax(data);
   } catch (error) {
     // Handle error
   }
   ```

4. **Use Typed Inputs**
   ```typescript
   // Good
   const result = await agentStore.calculateTax({
     taxableIncome: 75000,
     filingStatus: 'single'
   });
   
   // Bad
   const result = await agentStore.calculateTax({
     income: "75000", // Wrong type
     status: "single" // Wrong key
   });
   ```

5. **Access Structured Data**
   ```typescript
   // Access the structured data, not just the message
   const result = await agentStore.calculateTax(data);
   const tax = result.data.totalTax;  // Use this
   // Not: parsing result.message
   ```

## Examples

See `QUICK_START.md` for comprehensive examples and usage scenarios.
