// LLM Provider Interface and Implementations

export interface LLMMessage {
  role: 'system' | 'user' | 'assistant' | 'tool';
  content: string;
  name?: string;
  tool_calls?: any[];
}

export interface LLMResponse {
  content: string;
  role: string;
  tool_calls?: any[];
  finish_reason?: string;
  usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}

export interface LLMConfig {
  provider: 'openai' | 'anthropic' | 'gemini' | 'qwen' | 'glm' | 'kat' | 'llama' | 'local';
  model: string;
  apiKey?: string;
  baseURL?: string;
  temperature?: number;
  maxTokens?: number;
}

export abstract class LLMProvider {
  protected config: LLMConfig;

  constructor(config: LLMConfig) {
    this.config = config;
  }

  abstract chat(
    messages: LLMMessage[],
    options?: {
      temperature?: number;
      maxTokens?: number;
      tools?: any[];
      stream?: boolean;
    }
  ): Promise<LLMResponse>;

  abstract streamChat(
    messages: LLMMessage[],
    onChunk: (chunk: string) => void,
    options?: {
      temperature?: number;
      maxTokens?: number;
      tools?: any[];
    }
  ): Promise<LLMResponse>;
}

export class OpenAIProvider extends LLMProvider {
  async chat(
    messages: LLMMessage[],
    options?: {
      temperature?: number;
      maxTokens?: number;
      tools?: any[];
    }
  ): Promise<LLMResponse> {
    const apiKey = this.config.apiKey || (import.meta as any).env?.VITE_OPENAI_API_KEY;
    
    if (!apiKey) {
      throw new Error('OpenAI API key not configured');
    }

    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`
      },
      body: JSON.stringify({
        model: this.config.model || 'gpt-4o',
        messages,
        temperature: options?.temperature ?? this.config.temperature ?? 0.7,
        max_tokens: options?.maxTokens ?? this.config.maxTokens ?? 2000,
        tools: options?.tools
      })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(`OpenAI API error: ${error.error?.message || response.statusText}`);
    }

    const data = await response.json();
    const choice = data.choices[0];

    return {
      content: choice.message.content || '',
      role: choice.message.role,
      tool_calls: choice.message.tool_calls,
      finish_reason: choice.finish_reason,
      usage: data.usage
    };
  }

  async streamChat(
    messages: LLMMessage[],
    onChunk: (chunk: string) => void,
    options?: {
      temperature?: number;
      maxTokens?: number;
      tools?: any[];
    }
  ): Promise<LLMResponse> {
    const apiKey = this.config.apiKey || (import.meta as any).env?.VITE_OPENAI_API_KEY;
    
    if (!apiKey) {
      throw new Error('OpenAI API key not configured');
    }

    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`
      },
      body: JSON.stringify({
        model: this.config.model || 'gpt-4o',
        messages,
        temperature: options?.temperature ?? this.config.temperature ?? 0.7,
        max_tokens: options?.maxTokens ?? this.config.maxTokens ?? 2000,
        tools: options?.tools,
        stream: true
      })
    });

    if (!response.ok) {
      throw new Error(`OpenAI API error: ${response.statusText}`);
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();
    let fullContent = '';

    if (!reader) {
      throw new Error('No response body');
    }

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n').filter(line => line.trim() !== '');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          if (data === '[DONE]') continue;

          try {
            const parsed = JSON.parse(data);
            const content = parsed.choices[0]?.delta?.content;
            if (content) {
              fullContent += content;
              onChunk(content);
            }
          } catch (e) {
            console.error('Error parsing stream chunk:', e);
          }
        }
      }
    }

    return {
      content: fullContent,
      role: 'assistant'
    };
  }
}

export class AnthropicProvider extends LLMProvider {
  async chat(
    messages: LLMMessage[],
    options?: {
      temperature?: number;
      maxTokens?: number;
      tools?: any[];
    }
  ): Promise<LLMResponse> {
    const apiKey = this.config.apiKey || (import.meta as any).env?.VITE_ANTHROPIC_API_KEY;
    
    if (!apiKey) {
      throw new Error('Anthropic API key not configured');
    }

    // Convert messages format for Anthropic
    const systemMessage = messages.find(m => m.role === 'system');
    const conversationMessages = messages.filter(m => m.role !== 'system');

    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: this.config.model || 'claude-3-5-sonnet-20241022',
        max_tokens: options?.maxTokens ?? this.config.maxTokens ?? 2000,
        temperature: options?.temperature ?? this.config.temperature ?? 0.7,
        system: systemMessage?.content,
        messages: conversationMessages
      })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(`Anthropic API error: ${error.error?.message || response.statusText}`);
    }

    const data = await response.json();

    return {
      content: data.content[0].text,
      role: 'assistant',
      finish_reason: data.stop_reason,
      usage: data.usage
    };
  }

  async streamChat(
    messages: LLMMessage[],
    onChunk: (chunk: string) => void,
    options?: {
      temperature?: number;
      maxTokens?: number;
    }
  ): Promise<LLMResponse> {
    // Similar implementation with streaming
    return this.chat(messages, options);
  }
}

export class GeminiProvider extends LLMProvider {
  async chat(
    messages: LLMMessage[],
    options?: {
      temperature?: number;
      maxTokens?: number;
      tools?: any[];
    }
  ): Promise<LLMResponse> {
    const apiKey = this.config.apiKey || (import.meta as any).env?.VITE_GEMINI_API_KEY;
    
    if (!apiKey) {
      throw new Error('Gemini API key not configured');
    }

    // Use gemini-1.5-flash-latest which is the correct model name
    const model = this.config.model || 'gemini-1.5-flash-latest';
    
    // Prepare messages in Gemini format
    const contents = messages
      .filter(m => m.role !== 'system')
      .map(msg => ({
        role: msg.role === 'assistant' ? 'model' : 'user',
        parts: [{ text: msg.content }]
      }));

    // Add system message as first user message if present
    const systemMessage = messages.find(m => m.role === 'system');
    if (systemMessage && contents.length > 0) {
      contents[0].parts[0].text = systemMessage.content + '\n\n' + contents[0].parts[0].text;
    }

    const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey}`;

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        contents,
        generationConfig: {
          temperature: options?.temperature ?? this.config.temperature ?? 0.7,
          maxOutputTokens: options?.maxTokens ?? this.config.maxTokens ?? 2000
        }
      })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(`Gemini API error: ${error.error?.message || response.statusText}`);
    }

    const data = await response.json();
    const candidate = data.candidates?.[0];

    if (!candidate || !candidate.content) {
      throw new Error('Gemini API returned no content');
    }

    return {
      content: candidate.content.parts?.[0]?.text || '',
      role: 'assistant',
      finish_reason: candidate.finishReason,
      usage: {
        prompt_tokens: data.usageMetadata?.promptTokenCount || 0,
        completion_tokens: data.usageMetadata?.candidatesTokenCount || 0,
        total_tokens: data.usageMetadata?.totalTokenCount || 0
      }
    };
  }

  async streamChat(
    messages: LLMMessage[],
    onChunk: (chunk: string) => void,
    options?: {
      temperature?: number;
      maxTokens?: number;
    }
  ): Promise<LLMResponse> {
    const apiKey = this.config.apiKey || (import.meta as any).env?.VITE_GEMINI_API_KEY;
    
    if (!apiKey) {
      throw new Error('Gemini API key not configured');
    }

    const model = this.config.model || 'gemini-1.5-flash-latest';
    
    const contents = messages
      .filter(m => m.role !== 'system')
      .map(msg => ({
        role: msg.role === 'assistant' ? 'model' : 'user',
        parts: [{ text: msg.content }]
      }));

    const systemMessage = messages.find(m => m.role === 'system');
    if (systemMessage && contents.length > 0) {
      contents[0].parts[0].text = systemMessage.content + '\n\n' + contents[0].parts[0].text;
    }

    const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:streamGenerateContent?key=${apiKey}`;

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        contents,
        generationConfig: {
          temperature: options?.temperature ?? this.config.temperature ?? 0.7,
          maxOutputTokens: options?.maxTokens ?? this.config.maxTokens ?? 2000
        }
      })
    });

    if (!response.ok) {
      throw new Error(`Gemini API error: ${response.statusText}`);
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();
    let fullContent = '';

    if (!reader) {
      throw new Error('No response body');
    }

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n').filter(line => line.trim() !== '');

      for (const line of lines) {
        try {
          const parsed = JSON.parse(line);
          const content = parsed.candidates?.[0]?.content?.parts?.[0]?.text;
          if (content) {
            fullContent += content;
            onChunk(content);
          }
        } catch (e) {
          console.error('Error parsing stream chunk:', e);
        }
      }
    }

    return {
      content: fullContent,
      role: 'assistant'
    };
  }
}

export class QwenProvider extends LLMProvider {
  async chat(
    messages: LLMMessage[],
    options?: {
      temperature?: number;
      maxTokens?: number;
      tools?: any[];
    }
  ): Promise<LLMResponse> {
    const apiKey = this.config.apiKey || (import.meta as any).env?.VITE_QWEN_API_KEY;
    
    if (!apiKey) {
      throw new Error('Qwen API key not configured');
    }

    const baseURL = this.config.baseURL || 'https://openrouter.ai/api/v1';
    const response = await fetch(`${baseURL}/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`,
        'HTTP-Referer': 'https://tax-fluent-chat.app',
        'X-Title': 'Tax Fluent Chat'
      },
      body: JSON.stringify({
        model: this.config.model || 'qwen/qwen-2.5-72b-instruct:free',
        messages,
        temperature: options?.temperature ?? this.config.temperature ?? 0.7,
        max_tokens: options?.maxTokens ?? this.config.maxTokens ?? 2000,
        tools: options?.tools
      })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(`Qwen API error: ${error.error?.message || response.statusText}`);
    }

    const data = await response.json();
    const choice = data.choices[0];

    return {
      content: choice.message.content || '',
      role: choice.message.role,
      tool_calls: choice.message.tool_calls,
      finish_reason: choice.finish_reason,
      usage: data.usage
    };
  }

  async streamChat(
    messages: LLMMessage[],
    onChunk: (chunk: string) => void,
    options?: {
      temperature?: number;
      maxTokens?: number;
      tools?: any[];
    }
  ): Promise<LLMResponse> {
    const apiKey = this.config.apiKey || (import.meta as any).env?.VITE_QWEN_API_KEY;
    
    if (!apiKey) {
      throw new Error('Qwen API key not configured');
    }

    const baseURL = this.config.baseURL || 'https://openrouter.ai/api/v1';
    const response = await fetch(`${baseURL}/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`,
        'HTTP-Referer': 'https://tax-fluent-chat.app',
        'X-Title': 'Tax Fluent Chat'
      },
      body: JSON.stringify({
        model: this.config.model || 'qwen/qwen-2.5-72b-instruct:free',
        messages,
        temperature: options?.temperature ?? this.config.temperature ?? 0.7,
        max_tokens: options?.maxTokens ?? this.config.maxTokens ?? 2000,
        tools: options?.tools,
        stream: true
      })
    });

    if (!response.ok) {
      throw new Error(`Qwen API error: ${response.statusText}`);
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();
    let fullContent = '';

    if (!reader) {
      throw new Error('No response body');
    }

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n').filter(line => line.trim() !== '');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          if (data === '[DONE]') continue;

          try {
            const parsed = JSON.parse(data);
            const content = parsed.choices[0]?.delta?.content;
            if (content) {
              fullContent += content;
              onChunk(content);
            }
          } catch (e) {
            console.error('Error parsing stream chunk:', e);
          }
        }
      }
    }

    return {
      content: fullContent,
      role: 'assistant'
    };
  }
}

export class GLMProvider extends LLMProvider {
  async chat(
    messages: LLMMessage[],
    options?: {
      temperature?: number;
      maxTokens?: number;
      tools?: any[];
    }
  ): Promise<LLMResponse> {
    const apiKey = this.config.apiKey || (import.meta as any).env?.VITE_GLM_API_KEY;
    
    if (!apiKey) {
      throw new Error('GLM API key not configured');
    }

    const baseURL = this.config.baseURL || 'https://openrouter.ai/api/v1';
    const response = await fetch(`${baseURL}/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`,
        'HTTP-Referer': 'https://tax-fluent-chat.app',
        'X-Title': 'Tax Fluent Chat'
      },
      body: JSON.stringify({
        model: this.config.model || 'zerooneai/glm-4.5-air:free',
        messages,
        temperature: options?.temperature ?? this.config.temperature ?? 0.7,
        max_tokens: options?.maxTokens ?? this.config.maxTokens ?? 2000,
        tools: options?.tools
      })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(`GLM API error: ${error.error?.message || response.statusText}`);
    }

    const data = await response.json();
    const choice = data.choices[0];

    return {
      content: choice.message.content || '',
      role: choice.message.role,
      tool_calls: choice.message.tool_calls,
      finish_reason: choice.finish_reason,
      usage: data.usage
    };
  }

  async streamChat(
    messages: LLMMessage[],
    onChunk: (chunk: string) => void,
    options?: {
      temperature?: number;
      maxTokens?: number;
      tools?: any[];
    }
  ): Promise<LLMResponse> {
    const apiKey = this.config.apiKey || (import.meta as any).env?.VITE_GLM_API_KEY;
    
    if (!apiKey) {
      throw new Error('GLM API key not configured');
    }

    const baseURL = this.config.baseURL || 'https://openrouter.ai/api/v1';
    const response = await fetch(`${baseURL}/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`,
        'HTTP-Referer': 'https://tax-fluent-chat.app',
        'X-Title': 'Tax Fluent Chat'
      },
      body: JSON.stringify({
        model: this.config.model || 'zerooneai/glm-4.5-air:free',
        messages,
        temperature: options?.temperature ?? this.config.temperature ?? 0.7,
        max_tokens: options?.maxTokens ?? this.config.maxTokens ?? 2000,
        tools: options?.tools,
        stream: true
      })
    });

    if (!response.ok) {
      throw new Error(`GLM API error: ${response.statusText}`);
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();
    let fullContent = '';

    if (!reader) {
      throw new Error('No response body');
    }

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n').filter(line => line.trim() !== '');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          if (data === '[DONE]') continue;

          try {
            const parsed = JSON.parse(data);
            const content = parsed.choices[0]?.delta?.content;
            if (content) {
              fullContent += content;
              onChunk(content);
            }
          } catch (e) {
            console.error('Error parsing stream chunk:', e);
          }
        }
      }
    }

    return {
      content: fullContent,
      role: 'assistant'
    };
  }
}

export class KATProvider extends LLMProvider {
  async chat(
    messages: LLMMessage[],
    options?: {
      temperature?: number;
      maxTokens?: number;
      tools?: any[];
    }
  ): Promise<LLMResponse> {
    const apiKey = this.config.apiKey || (import.meta as any).env?.VITE_KAT_API_KEY;
    
    if (!apiKey) {
      throw new Error('KAT API key not configured');
    }

    const baseURL = this.config.baseURL || 'https://openrouter.ai/api/v1';
    const response = await fetch(`${baseURL}/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`,
        'HTTP-Referer': 'https://tax-fluent-chat.app',
        'X-Title': 'Tax Fluent Chat'
      },
      body: JSON.stringify({
        model: this.config.model || 'kat/kat-coder-pro-v1:free',
        messages,
        temperature: options?.temperature ?? this.config.temperature ?? 0.7,
        max_tokens: options?.maxTokens ?? this.config.maxTokens ?? 2000,
        tools: options?.tools
      })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(`KAT API error: ${error.error?.message || response.statusText}`);
    }

    const data = await response.json();
    const choice = data.choices[0];

    return {
      content: choice.message.content || '',
      role: choice.message.role,
      tool_calls: choice.message.tool_calls,
      finish_reason: choice.finish_reason,
      usage: data.usage
    };
  }

  async streamChat(
    messages: LLMMessage[],
    onChunk: (chunk: string) => void,
    options?: {
      temperature?: number;
      maxTokens?: number;
      tools?: any[];
    }
  ): Promise<LLMResponse> {
    const apiKey = this.config.apiKey || (import.meta as any).env?.VITE_KAT_API_KEY;
    
    if (!apiKey) {
      throw new Error('KAT API key not configured');
    }

    const baseURL = this.config.baseURL || 'https://openrouter.ai/api/v1';
    const response = await fetch(`${baseURL}/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`,
        'HTTP-Referer': 'https://tax-fluent-chat.app',
        'X-Title': 'Tax Fluent Chat'
      },
      body: JSON.stringify({
        model: this.config.model || 'kat/kat-coder-pro-v1:free',
        messages,
        temperature: options?.temperature ?? this.config.temperature ?? 0.7,
        max_tokens: options?.maxTokens ?? this.config.maxTokens ?? 2000,
        tools: options?.tools,
        stream: true
      })
    });

    if (!response.ok) {
      throw new Error(`KAT API error: ${response.statusText}`);
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();
    let fullContent = '';

    if (!reader) {
      throw new Error('No response body');
    }

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n').filter(line => line.trim() !== '');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          if (data === '[DONE]') continue;

          try {
            const parsed = JSON.parse(data);
            const content = parsed.choices[0]?.delta?.content;
            if (content) {
              fullContent += content;
              onChunk(content);
            }
          } catch (e) {
            console.error('Error parsing stream chunk:', e);
          }
        }
      }
    }

    return {
      content: fullContent,
      role: 'assistant'
    };
  }
}

export class LlamaProvider extends LLMProvider {
  async chat(
    messages: LLMMessage[],
    options?: {
      temperature?: number;
      maxTokens?: number;
      tools?: any[];
    }
  ): Promise<LLMResponse> {
    const apiKey = this.config.apiKey || (import.meta as any).env?.VITE_LLAMA_API_KEY;
    
    if (!apiKey) {
      throw new Error('Llama API key not configured');
    }

    const baseURL = this.config.baseURL || 'https://openrouter.ai/api/v1';
    const response = await fetch(`${baseURL}/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`,
        'HTTP-Referer': 'https://tax-fluent-chat.app',
        'X-Title': 'Tax Fluent Chat'
      },
      body: JSON.stringify({
        model: this.config.model || 'meta-llama/llama-4-maverick',
        messages,
        temperature: options?.temperature ?? this.config.temperature ?? 0.7,
        max_tokens: options?.maxTokens ?? this.config.maxTokens ?? 2000,
        tools: options?.tools
      })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(`Llama API error: ${error.error?.message || response.statusText}`);
    }

    const data = await response.json();
    const choice = data.choices[0];

    return {
      content: choice.message.content || '',
      role: choice.message.role,
      tool_calls: choice.message.tool_calls,
      finish_reason: choice.finish_reason,
      usage: data.usage
    };
  }

  async streamChat(
    messages: LLMMessage[],
    onChunk: (chunk: string) => void,
    options?: {
      temperature?: number;
      maxTokens?: number;
      tools?: any[];
    }
  ): Promise<LLMResponse> {
    const apiKey = this.config.apiKey || (import.meta as any).env?.VITE_LLAMA_API_KEY;
    
    if (!apiKey) {
      throw new Error('Llama API key not configured');
    }

    const baseURL = this.config.baseURL || 'https://openrouter.ai/api/v1';
    const response = await fetch(`${baseURL}/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`,
        'HTTP-Referer': 'https://tax-fluent-chat.app',
        'X-Title': 'Tax Fluent Chat'
      },
      body: JSON.stringify({
        model: this.config.model || 'meta-llama/llama-4-maverick',
        messages,
        temperature: options?.temperature ?? this.config.temperature ?? 0.7,
        max_tokens: options?.maxTokens ?? this.config.maxTokens ?? 2000,
        tools: options?.tools,
        stream: true
      })
    });

    if (!response.ok) {
      throw new Error(`Llama API error: ${response.statusText}`);
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();
    let fullContent = '';

    if (!reader) {
      throw new Error('No response body');
    }

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n').filter(line => line.trim() !== '');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          if (data === '[DONE]') continue;

          try {
            const parsed = JSON.parse(data);
            const content = parsed.choices[0]?.delta?.content;
            if (content) {
              fullContent += content;
              onChunk(content);
            }
          } catch (e) {
            console.error('Error parsing stream chunk:', e);
          }
        }
      }
    }

    return {
      content: fullContent,
      role: 'assistant'
    };
  }
}

// Factory function to create LLM provider
export function createLLMProvider(config: LLMConfig): LLMProvider {
  switch (config.provider) {
    case 'openai':
      return new OpenAIProvider(config);
    case 'anthropic':
      return new AnthropicProvider(config);
    case 'gemini':
      return new GeminiProvider(config);
    case 'qwen':
      return new QwenProvider(config);
    case 'glm':
      return new GLMProvider(config);
    case 'kat':
      return new KATProvider(config);
    case 'llama':
      return new LlamaProvider(config);
    default:
      throw new Error(`Unsupported LLM provider: ${config.provider}`);
  }
}
