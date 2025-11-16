# LLM Provider Usage Guide

## Supported Providers

The Tax Fluent Chat system now supports **5 LLM providers**:

1. **OpenAI** (GPT-4o, GPT-4, GPT-3.5)
2. **Anthropic** (Claude 3.5 Sonnet, Claude 3 Opus)
3. **Google Gemini** (Gemini Pro)
4. **Qwen** (Qwen 2.5 72B Instruct - Free via OpenRouter)
5. **GLM** (GLM 4.5 Air - via OpenRouter)

## Configuration

### 1. Set API Keys

Add your API keys to the `.env` file:

```env
# OpenAI
VITE_OPENAI_API_KEY=sk-your-openai-key-here

# Anthropic
VITE_ANTHROPIC_API_KEY=sk-your-anthropic-key-here

# Gemini
VITE_GEMINI_API_KEY=AIzaSyB5oma-7DH9VxKLU-MGFWy1QHf_UugNglE

# Qwen (OpenRouter)
VITE_QWEN_API_KEY=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

# GLM (OpenRouter)
VITE_GLM_API_KEY=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
```

### 2. Get API Keys

- **OpenAI**: https://platform.openai.com/api-keys
- **Anthropic**: https://console.anthropic.com/
- **Gemini**: https://makersuite.google.com/app/apikey
- **Qwen/GLM**: https://openrouter.ai/keys

## Usage Examples

### Using OpenAI

```typescript
import { createLLMProvider } from '@/agents/llm/LLMProvider';

const provider = createLLMProvider({
  provider: 'openai',
  model: 'gpt-4o',
  temperature: 0.7,
  maxTokens: 2000
});

const response = await provider.chat([
  { role: 'user', content: 'Calculate tax on $75,000' }
]);
```

### Using Gemini Pro

```typescript
const provider = createLLMProvider({
  provider: 'gemini',
  model: 'gemini-pro',
  apiKey: 'AIzaSyB5oma-7DH9VxKLU-MGFWy1QHf_UugNglE',
  temperature: 0.7,
  maxTokens: 2000
});

const response = await provider.chat([
  { role: 'user', content: 'Explain tax credits' }
]);
```

### Using Qwen 2.5 72B Instruct (Free)

```typescript
const provider = createLLMProvider({
  provider: 'qwen',
  model: 'qwen/qwen-2.5-72b-instruct:free',
  apiKey: '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',
  temperature: 0.7,
  maxTokens: 2000
});

const response = await provider.chat([
  { role: 'user', content: 'What deductions am I eligible for?' }
]);
```

### Using GLM 4.5 Air

```typescript
const provider = createLLMProvider({
  provider: 'glm',
  model: 'zerooneai/glm-4.5-air:free',
  apiKey: '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',
  temperature: 0.7,
  maxTokens: 2000
});

const response = await provider.chat([
  { role: 'user', content: 'Help me file my taxes' }
]);
```

### Streaming Responses

All providers support streaming:

```typescript
const provider = createLLMProvider({
  provider: 'gemini',
  model: 'gemini-pro'
});

await provider.streamChat(
  [{ role: 'user', content: 'Calculate my tax refund' }],
  (chunk) => {
    console.log('Received chunk:', chunk);
  }
);
```

## Using Different Providers in Agents

### Modify Agent Configuration

In `src/agents/configs.ts`, you can specify which provider each agent should use:

```typescript
export const TAX_CALCULATOR_CONFIG: AgentConfig = {
  role: 'tax_calculator',
  model: 'gemini-pro',  // Change model
  // ... other config
};
```

### Modify Agent Implementation

In specialized agents (e.g., `TaxCalculatorAgent.ts`):

```typescript
// Use Gemini
this.llmProvider = createLLMProvider({
  provider: 'gemini',
  model: 'gemini-pro',
  temperature: this.config.temperature,
  maxTokens: this.config.maxTokens
});

// Use Qwen
this.llmProvider = createLLMProvider({
  provider: 'qwen',
  model: 'qwen/qwen-2.5-72b-instruct:free',
  temperature: this.config.temperature,
  maxTokens: this.config.maxTokens
});

// Use GLM
this.llmProvider = createLLMProvider({
  provider: 'glm',
  model: 'zerooneai/glm-4.5-air:free',
  temperature: this.config.temperature,
  maxTokens: this.config.maxTokens
});
```

## Provider Comparison

| Provider | Model | Cost | Speed | Quality | Best For |
|----------|-------|------|-------|---------|----------|
| OpenAI | GPT-4o | $$$ | Fast | Excellent | Complex tax calculations |
| Anthropic | Claude 3.5 | $$$ | Fast | Excellent | Detailed explanations |
| Gemini | Gemini Pro | $$ | Very Fast | Very Good | General queries |
| Qwen | 2.5 72B | **FREE** | Fast | Good | Cost-effective option |
| GLM | 4.5 Air | **FREE** | Fast | Good | Multilingual support |

## Notes

- **Qwen** and **GLM** use OpenRouter API, which provides free access to these models
- **Gemini** uses Google's Generative AI API directly
- All providers support both standard and streaming responses
- API keys are loaded from environment variables for security
- The system automatically falls back to environment variables if API keys aren't provided in config

## Troubleshooting

### "API key not configured" Error

Make sure:
1. `.env` file exists in project root
2. API key is set correctly
3. Dev server was restarted after adding API key

### Rate Limiting

- OpenRouter (Qwen/GLM): Free tier has rate limits
- Gemini: Check quota at Google AI Studio
- OpenAI/Anthropic: Check your account usage

### Model Not Found

- Ensure model name matches the provider's supported models
- For OpenRouter models, use the full model identifier (e.g., `qwen/qwen-2.5-72b-instruct:free`)
