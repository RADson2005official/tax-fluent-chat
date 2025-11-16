# How to Switch LLM Providers in Tax Agents

This guide shows how to modify your tax agents to use different LLM providers (Gemini, Qwen, GLM, etc.).

## Quick Switch Guide

### Option 1: Modify Individual Agent (Recommended for Testing)

Open any agent file (e.g., `TaxCalculatorAgent.ts`, `OrchestratorAgent.ts`) and change the provider in the constructor:

#### Example: TaxCalculatorAgent.ts

**Current (OpenAI):**
```typescript
constructor() {
  super(TAX_CALCULATOR_CONFIG);
  
  // Register tools
  const tools = getToolsByAgent('tax_calculator');
  tools.forEach(tool => this.registerTool(tool));

  // Initialize LLM provider
  this.llmProvider = createLLMProvider({
    provider: 'openai',
    model: this.config.model || 'gpt-4o',
    temperature: this.config.temperature,
    maxTokens: this.config.maxTokens
  });
}
```

**Switch to Gemini:**
```typescript
constructor() {
  super(TAX_CALCULATOR_CONFIG);
  
  const tools = getToolsByAgent('tax_calculator');
  tools.forEach(tool => this.registerTool(tool));

  // Use Gemini instead
  this.llmProvider = createLLMProvider({
    provider: 'gemini',
    model: 'gemini-pro',
    temperature: this.config.temperature,
    maxTokens: this.config.maxTokens
  });
}
```

**Switch to Qwen (FREE):**
```typescript
constructor() {
  super(TAX_CALCULATOR_CONFIG);
  
  const tools = getToolsByAgent('tax_calculator');
  tools.forEach(tool => this.registerTool(tool));

  // Use Qwen (Free tier)
  this.llmProvider = createLLMProvider({
    provider: 'qwen',
    model: 'qwen/qwen-2.5-72b-instruct:free',
    temperature: this.config.temperature,
    maxTokens: this.config.maxTokens
  });
}
```

**Switch to GLM (FREE):**
```typescript
constructor() {
  super(TAX_CALCULATOR_CONFIG);
  
  const tools = getToolsByAgent('tax_calculator');
  tools.forEach(tool => this.registerTool(tool));

  // Use GLM (Free tier)
  this.llmProvider = createLLMProvider({
    provider: 'glm',
    model: 'zerooneai/glm-4.5-air:free',
    temperature: this.config.temperature,
    maxTokens: this.config.maxTokens
  });
}
```

### Option 2: Environment Variable Configuration (Recommended for Production)

#### 1. Add to `.env`:
```env
# Default provider for all agents
VITE_DEFAULT_LLM_PROVIDER=gemini
VITE_DEFAULT_MODEL=gemini-pro

# Or use Qwen for cost-effective option
# VITE_DEFAULT_LLM_PROVIDER=qwen
# VITE_DEFAULT_MODEL=qwen/qwen-2.5-72b-instruct:free
```

#### 2. Modify Agent Constructor:
```typescript
constructor() {
  super(TAX_CALCULATOR_CONFIG);
  
  const tools = getToolsByAgent('tax_calculator');
  tools.forEach(tool => this.registerTool(tool));

  // Get provider from environment or use default
  const provider = (import.meta as any).env?.VITE_DEFAULT_LLM_PROVIDER || 'openai';
  const model = (import.meta as any).env?.VITE_DEFAULT_MODEL || this.config.model || 'gpt-4o';

  this.llmProvider = createLLMProvider({
    provider,
    model,
    temperature: this.config.temperature,
    maxTokens: this.config.maxTokens
  });
}
```

### Option 3: Per-Agent Provider Configuration

Modify `src/agents/configs.ts` to specify providers for each agent:

```typescript
export const TAX_CALCULATOR_CONFIG: AgentConfig = {
  role: 'tax_calculator',
  name: 'Tax Calculation Specialist',
  description: 'Performs accurate tax calculations',
  model: 'gemini-pro',  // Change model here
  temperature: 0.1,
  maxTokens: 1500,
  // ... rest of config
};

export const ORCHESTRATOR_CONFIG: AgentConfig = {
  role: 'orchestrator',
  name: 'Agent Coordinator',
  description: 'Routes and coordinates agent interactions',
  model: 'qwen/qwen-2.5-72b-instruct:free',  // Use free tier for orchestrator
  temperature: 0.7,
  maxTokens: 2000,
  // ... rest of config
};
```

Then update agent constructors to read provider type:

```typescript
constructor() {
  super(TAX_CALCULATOR_CONFIG);
  
  const tools = getToolsByAgent('tax_calculator');
  tools.forEach(tool => this.registerTool(tool));

  // Determine provider from model name
  let provider: 'openai' | 'anthropic' | 'gemini' | 'qwen' | 'glm' = 'openai';
  const model = this.config.model || 'gpt-4o';
  
  if (model.includes('gemini')) provider = 'gemini';
  else if (model.includes('claude')) provider = 'anthropic';
  else if (model.includes('qwen')) provider = 'qwen';
  else if (model.includes('glm')) provider = 'glm';

  this.llmProvider = createLLMProvider({
    provider,
    model,
    temperature: this.config.temperature,
    maxTokens: this.config.maxTokens
  });
}
```

## Provider Selection Strategy

### By Use Case

**Complex Tax Calculations** → Use OpenAI GPT-4o
- Highest accuracy
- Best for complex scenarios
- Worth the cost for critical calculations

**General Queries** → Use Gemini Pro
- Fast responses
- Good quality
- Lower cost than OpenAI

**Cost-Effective Development** → Use Qwen (FREE)
- No cost
- Good quality
- Perfect for testing

**Multilingual Support** → Use GLM
- Excellent Chinese support
- Free tier available
- Good for international users

**Detailed Explanations** → Use Anthropic Claude
- Best at explaining reasoning
- Great for advisory agent
- Professional quality

### Recommended Agent-Provider Mapping

```typescript
// TaxCalculatorAgent → OpenAI (accuracy critical)
provider: 'openai',
model: 'gpt-4o'

// AdvisoryAgent → Anthropic (explanations important)
provider: 'anthropic',
model: 'claude-3-5-sonnet-20241022'

// OrchestratorAgent → Gemini or Qwen (cost-effective)
provider: 'gemini',
model: 'gemini-pro'

// DocumentProcessor → Qwen (cost-effective)
provider: 'qwen',
model: 'qwen/qwen-2.5-72b-instruct:free'

// ComplianceChecker → OpenAI (accuracy critical)
provider: 'openai',
model: 'gpt-4o'
```

## Testing Different Providers

### Quick Test Script

Create a test file to compare providers:

```typescript
import { TaxCalculatorAgent } from '@/agents/specialized/TaxCalculatorAgent';

async function testProviders() {
  // Test with different providers
  const providers = ['openai', 'gemini', 'qwen', 'glm'];
  
  for (const provider of providers) {
    console.log(`\nTesting ${provider}...`);
    
    // Temporarily modify the agent
    const agent = new TaxCalculatorAgent();
    // (agent as any).llmProvider = createLLMProvider({ provider, ... });
    
    const result = await agent.processTask({
      id: 'test',
      agentRole: 'tax_calculator',
      type: 'calculate_tax',
      priority: 'high',
      status: 'pending',
      input: { taxableIncome: 75000, filingStatus: 'single' },
      createdAt: new Date()
    });
    
    console.log(`Result: ${result.message}`);
    console.log(`Success: ${result.success}`);
  }
}

testProviders();
```

## Common Issues & Solutions

### Issue: "API key not configured"

**Solution:**
1. Check `.env` file has the correct API key
2. Restart dev server: `npm run dev`
3. Verify key is valid

### Issue: Rate limiting

**Solution:**
- Switch to a free provider (Qwen/GLM)
- Implement retry logic
- Add delays between requests

### Issue: Different response quality

**Solution:**
- Test each provider with your specific queries
- Adjust temperature (lower = more consistent)
- Use appropriate provider for task type

## Advanced: Dynamic Provider Selection

Implement automatic provider selection based on query complexity:

```typescript
constructor() {
  super(TAX_CALCULATOR_CONFIG);
  
  const tools = getToolsByAgent('tax_calculator');
  tools.forEach(tool => this.registerTool(tool));

  // Don't initialize provider yet
  this.llmProvider = null;
}

private selectProvider(complexity: 'simple' | 'medium' | 'complex') {
  const providerMap = {
    simple: { provider: 'qwen', model: 'qwen/qwen-2.5-72b-instruct:free' },
    medium: { provider: 'gemini', model: 'gemini-pro' },
    complex: { provider: 'openai', model: 'gpt-4o' }
  };
  
  const config = providerMap[complexity];
  
  return createLLMProvider({
    provider: config.provider as any,
    model: config.model,
    temperature: this.config.temperature,
    maxTokens: this.config.maxTokens
  });
}

async generateResponse(message: AgentMessage): Promise<AgentResponse> {
  // Analyze complexity
  const complexity = this.analyzeComplexity(message.content);
  
  // Select appropriate provider
  this.llmProvider = this.selectProvider(complexity);
  
  // Continue with response generation
  // ...
}
```

## Summary

- ✅ 5 providers available: OpenAI, Anthropic, Gemini, Qwen, GLM
- ✅ Easy to switch: just change provider name and model
- ✅ 2 free options: Qwen and GLM via OpenRouter
- ✅ No code changes needed (use environment variables)
- ✅ Mix and match providers per agent for optimization

**Recommended for most users**: Start with Gemini or Qwen for testing, upgrade to OpenAI for production.
