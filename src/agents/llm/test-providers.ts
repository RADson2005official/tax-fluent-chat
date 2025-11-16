// Test file to demonstrate all LLM providers
// This file shows how to use all 5 supported LLM providers

import { createLLMProvider } from './LLMProvider';
import type { LLMMessage } from './LLMProvider';

// Sample tax question
const taxQuestion: LLMMessage[] = [
  {
    role: 'user',
    content: 'Calculate federal income tax for a single filer with $75,000 taxable income.'
  }
];

/**
 * Test OpenAI Provider
 */
export async function testOpenAI() {
  console.log('Testing OpenAI Provider...');
  
  const provider = createLLMProvider({
    provider: 'openai',
    model: 'gpt-4o',
    temperature: 0.7,
    maxTokens: 2000
  });

  try {
    const response = await provider.chat(taxQuestion);
    console.log('OpenAI Response:', response.content);
    return response;
  } catch (error) {
    console.error('OpenAI Error:', error);
  }
}

/**
 * Test Anthropic Provider
 */
export async function testAnthropic() {
  console.log('Testing Anthropic Provider...');
  
  const provider = createLLMProvider({
    provider: 'anthropic',
    model: 'claude-3-5-sonnet-20241022',
    temperature: 0.7,
    maxTokens: 2000
  });

  try {
    const response = await provider.chat(taxQuestion);
    console.log('Anthropic Response:', response.content);
    return response;
  } catch (error) {
    console.error('Anthropic Error:', error);
  }
}

/**
 * Test Gemini Provider
 */
export async function testGemini() {
  console.log('Testing Gemini Provider...');
  
  const provider = createLLMProvider({
    provider: 'gemini',
    model: 'gemini-pro',
    apiKey: 'AIzaSyB5oma-7DH9VxKLU-MGFWy1QHf_UugNglE',
    temperature: 0.7,
    maxTokens: 2000
  });

  try {
    const response = await provider.chat(taxQuestion);
    console.log('Gemini Response:', response.content);
    return response;
  } catch (error) {
    console.error('Gemini Error:', error);
  }
}

/**
 * Test Qwen Provider (Free via OpenRouter)
 */
export async function testQwen() {
  console.log('Testing Qwen Provider...');
  
  const provider = createLLMProvider({
    provider: 'qwen',
    model: 'qwen/qwen-2.5-72b-instruct:free',
    apiKey: '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',
    temperature: 0.7,
    maxTokens: 2000
  });

  try {
    const response = await provider.chat(taxQuestion);
    console.log('Qwen Response:', response.content);
    return response;
  } catch (error) {
    console.error('Qwen Error:', error);
  }
}

/**
 * Test GLM Provider (via OpenRouter)
 */
export async function testGLM() {
  console.log('Testing GLM Provider...');
  
  const provider = createLLMProvider({
    provider: 'glm',
    model: 'zerooneai/glm-4.5-air:free',
    apiKey: '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',
    temperature: 0.7,
    maxTokens: 2000
  });

  try {
    const response = await provider.chat(taxQuestion);
    console.log('GLM Response:', response.content);
    return response;
  } catch (error) {
    console.error('GLM Error:', error);
  }
}

/**
 * Test Streaming with Gemini
 */
export async function testGeminiStreaming() {
  console.log('Testing Gemini Streaming...');
  
  const provider = createLLMProvider({
    provider: 'gemini',
    model: 'gemini-pro',
    apiKey: 'AIzaSyB5oma-7DH9VxKLU-MGFWy1QHf_UugNglE'
  });

  try {
    const response = await provider.streamChat(
      taxQuestion,
      (chunk) => {
        process.stdout.write(chunk);
      }
    );
    console.log('\nStreaming Complete');
    return response;
  } catch (error) {
    console.error('Gemini Streaming Error:', error);
  }
}

/**
 * Test Streaming with Qwen
 */
export async function testQwenStreaming() {
  console.log('Testing Qwen Streaming...');
  
  const provider = createLLMProvider({
    provider: 'qwen',
    model: 'qwen/qwen-2.5-72b-instruct:free',
    apiKey: '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'
  });

  try {
    const response = await provider.streamChat(
      taxQuestion,
      (chunk) => {
        process.stdout.write(chunk);
      }
    );
    console.log('\nStreaming Complete');
    return response;
  } catch (error) {
    console.error('Qwen Streaming Error:', error);
  }
}

/**
 * Run all provider tests
 */
export async function testAllProviders() {
  console.log('=== Testing All LLM Providers ===\n');

  await testGemini();
  console.log('\n---\n');

  await testQwen();
  console.log('\n---\n');

  await testGLM();
  console.log('\n---\n');

  await testOpenAI();
  console.log('\n---\n');

  await testAnthropic();
  console.log('\n=== All Tests Complete ===');
}

/**
 * Compare responses from all providers
 */
export async function compareProviders() {
  console.log('=== Comparing Provider Responses ===\n');

  const results = await Promise.allSettled([
    testGemini(),
    testQwen(),
    testGLM()
  ]);

  results.forEach((result, index) => {
    const providers = ['Gemini', 'Qwen', 'GLM'];
    console.log(`\n${providers[index]}:`, result.status);
    if (result.status === 'fulfilled') {
      console.log('Length:', result.value?.content.length);
    }
  });
}

// Usage examples for different scenarios
export const usageExamples = {
  
  // Best for complex calculations
  useOpenAI: () => createLLMProvider({
    provider: 'openai',
    model: 'gpt-4o'
  }),

  // Best for detailed explanations
  useAnthropic: () => createLLMProvider({
    provider: 'anthropic',
    model: 'claude-3-5-sonnet-20241022'
  }),

  // Best for fast responses
  useGemini: () => createLLMProvider({
    provider: 'gemini',
    model: 'gemini-pro',
    apiKey: 'AIzaSyB5oma-7DH9VxKLU-MGFWy1QHf_UugNglE'
  }),

  // Best for cost-effective (FREE)
  useQwen: () => createLLMProvider({
    provider: 'qwen',
    model: 'qwen/qwen-2.5-72b-instruct:free',
    apiKey: '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'
  }),

  // Best for multilingual
  useGLM: () => createLLMProvider({
    provider: 'glm',
    model: 'zerooneai/glm-4.5-air:free',
    apiKey: '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'
  })
};
