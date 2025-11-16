/**
 * Multi-Agent LLM Provider Verification Script
 * Tests all 6 LLM providers with tax-specific queries
 */

import { createLLMProvider } from './LLMProvider';
import type { LLMMessage, LLMConfig } from './LLMProvider';

// Test query for tax agents
const taxTestQuery: LLMMessage[] = [
  {
    role: 'system',
    content: 'You are a tax calculation specialist. Provide accurate, professional tax advice.'
  },
  {
    role: 'user',
    content: 'Calculate federal income tax for a single filer with $75,000 taxable income in 2024. Show the breakdown by tax bracket.'
  }
];

// Provider configurations
const providerConfigs: Record<string, LLMConfig> = {
  openai: {
    provider: 'openai',
    model: 'gpt-4o',
    temperature: 0.7,
    maxTokens: 2000
  },
  anthropic: {
    provider: 'anthropic',
    model: 'claude-3-5-sonnet-20241022',
    temperature: 0.7,
    maxTokens: 2000
  },
  gemini: {
    provider: 'gemini',
    model: 'gemini-pro',
    apiKey: 'AIzaSyB5oma-7DH9VxKLU-MGFWy1QHf_UugNglE',
    temperature: 0.7,
    maxTokens: 2000
  },
  qwen: {
    provider: 'qwen',
    model: 'qwen/qwen-2.5-72b-instruct:free',
    apiKey: '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',
    temperature: 0.7,
    maxTokens: 2000
  },
  glm: {
    provider: 'glm',
    model: 'zerooneai/glm-4.5-air:free',
    apiKey: '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',
    temperature: 0.7,
    maxTokens: 2000
  },
  llama: {
    provider: 'llama',
    model: 'meta-llama/llama-4-maverick',
    apiKey: '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',
    temperature: 0.7,
    maxTokens: 2000
  }
};

interface TestResult {
  provider: string;
  status: 'success' | 'failed';
  responseTime: number;
  contentLength: number;
  error?: string;
  preview?: string;
}

/**
 * Test a single provider
 */
async function testProvider(name: string, config: LLMConfig): Promise<TestResult> {
  const startTime = Date.now();
  
  try {
    console.log(`\n🔄 Testing ${name.toUpperCase()}...`);
    
    const provider = createLLMProvider(config);
    const response = await provider.chat(taxTestQuery);
    
    const responseTime = Date.now() - startTime;
    const contentLength = response.content.length;
    const preview = response.content.substring(0, 150) + '...';
    
    console.log(`✅ ${name.toUpperCase()} - SUCCESS`);
    console.log(`   Response time: ${responseTime}ms`);
    console.log(`   Content length: ${contentLength} chars`);
    console.log(`   Preview: ${preview}`);
    
    return {
      provider: name,
      status: 'success',
      responseTime,
      contentLength,
      preview
    };
  } catch (error) {
    const responseTime = Date.now() - startTime;
    const errorMsg = error instanceof Error ? error.message : 'Unknown error';
    
    console.log(`❌ ${name.toUpperCase()} - FAILED`);
    console.log(`   Error: ${errorMsg}`);
    
    return {
      provider: name,
      status: 'failed',
      responseTime,
      contentLength: 0,
      error: errorMsg
    };
  }
}

/**
 * Test streaming functionality
 */
async function testStreamingProvider(name: string, config: LLMConfig): Promise<TestResult> {
  const startTime = Date.now();
  
  try {
    console.log(`\n🌊 Testing ${name.toUpperCase()} (Streaming)...`);
    
    const provider = createLLMProvider(config);
    let fullContent = '';
    let chunkCount = 0;
    
    await provider.streamChat(
      taxTestQuery,
      (chunk) => {
        fullContent += chunk;
        chunkCount++;
        process.stdout.write('.');
      }
    );
    
    const responseTime = Date.now() - startTime;
    console.log(`\n✅ ${name.toUpperCase()} Streaming - SUCCESS`);
    console.log(`   Response time: ${responseTime}ms`);
    console.log(`   Chunks received: ${chunkCount}`);
    console.log(`   Total content: ${fullContent.length} chars`);
    
    return {
      provider: `${name}-stream`,
      status: 'success',
      responseTime,
      contentLength: fullContent.length
    };
  } catch (error) {
    const responseTime = Date.now() - startTime;
    const errorMsg = error instanceof Error ? error.message : 'Unknown error';
    
    console.log(`\n❌ ${name.toUpperCase()} Streaming - FAILED`);
    console.log(`   Error: ${errorMsg}`);
    
    return {
      provider: `${name}-stream`,
      status: 'failed',
      responseTime,
      contentLength: 0,
      error: errorMsg
    };
  }
}

/**
 * Run comprehensive tests on all providers
 */
export async function verifyAllProviders(): Promise<void> {
  console.log('='.repeat(70));
  console.log('🚀 MULTI-AGENT LLM PROVIDER VERIFICATION');
  console.log('='.repeat(70));
  console.log('\n📋 Testing 6 LLM Providers:');
  console.log('   1. OpenAI (GPT-4o)');
  console.log('   2. Anthropic (Claude 3.5 Sonnet)');
  console.log('   3. Google Gemini Pro');
  console.log('   4. Qwen 2.5 72B Instruct (FREE)');
  console.log('   5. GLM 4.5 Air (FREE)');
  console.log('   6. Llama 4 Maverick');
  console.log('\n' + '='.repeat(70));
  
  const results: TestResult[] = [];
  
  // Test each provider
  for (const [name, config] of Object.entries(providerConfigs)) {
    const result = await testProvider(name, config);
    results.push(result);
    
    // Small delay between tests
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
  
  // Test streaming on key providers
  console.log('\n' + '='.repeat(70));
  console.log('🌊 STREAMING TESTS');
  console.log('='.repeat(70));
  
  const streamProviders = ['gemini', 'qwen', 'llama'];
  for (const name of streamProviders) {
    if (providerConfigs[name]) {
      const result = await testStreamingProvider(name, providerConfigs[name]);
      results.push(result);
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  }
  
  // Summary Report
  console.log('\n' + '='.repeat(70));
  console.log('📊 VERIFICATION SUMMARY');
  console.log('='.repeat(70));
  
  const successful = results.filter(r => r.status === 'success');
  const failed = results.filter(r => r.status === 'failed');
  
  console.log(`\n✅ Successful: ${successful.length}/${results.length}`);
  console.log(`❌ Failed: ${failed.length}/${results.length}`);
  
  if (successful.length > 0) {
    console.log('\n🎉 Working Providers:');
    successful.forEach(r => {
      console.log(`   ✓ ${r.provider.toUpperCase()} - ${r.responseTime}ms - ${r.contentLength} chars`);
    });
  }
  
  if (failed.length > 0) {
    console.log('\n⚠️  Failed Providers:');
    failed.forEach(r => {
      console.log(`   ✗ ${r.provider.toUpperCase()} - ${r.error}`);
    });
  }
  
  // Performance comparison
  const standardTests = results.filter(r => !r.provider.includes('-stream') && r.status === 'success');
  if (standardTests.length > 1) {
    console.log('\n⚡ Performance Ranking:');
    standardTests
      .sort((a, b) => a.responseTime - b.responseTime)
      .forEach((r, i) => {
        console.log(`   ${i + 1}. ${r.provider.toUpperCase()} - ${r.responseTime}ms`);
      });
  }
  
  console.log('\n' + '='.repeat(70));
  console.log('✨ VERIFICATION COMPLETE');
  console.log('='.repeat(70));
  
  // Return exit code
  if (failed.length > 0) {
    console.log('\n⚠️  Some providers failed. Please check API keys and configuration.');
  } else {
    console.log('\n🎊 All providers are working correctly!');
  }
}

/**
 * Quick test for specific provider
 */
export async function quickTestProvider(providerName: string): Promise<void> {
  const config = providerConfigs[providerName.toLowerCase()];
  
  if (!config) {
    console.error(`❌ Provider "${providerName}" not found.`);
    console.log('Available providers:', Object.keys(providerConfigs).join(', '));
    return;
  }
  
  console.log(`\n🔍 Quick test for ${providerName.toUpperCase()}`);
  const result = await testProvider(providerName, config);
  
  if (result.status === 'success') {
    console.log('\n✅ Provider is working correctly!');
  } else {
    console.log('\n❌ Provider test failed:', result.error);
  }
}

// Export for use in other files
export { testProvider, testStreamingProvider };
