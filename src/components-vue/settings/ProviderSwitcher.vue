<template>
  <Card class="w-full">
    <CardHeader>
      <CardTitle class="flex items-center justify-between">
        <span class="flex items-center gap-2">
          <Zap class="h-5 w-5 text-primary" />
          AI Provider Selection & Testing
        </span>
        <Button size="sm" @click="testAllProviders" :disabled="isTesting">
          <RefreshCw :class="['h-4 w-4 mr-2', isTesting && 'animate-spin']" />
          Test All
        </Button>
      </CardTitle>
    </CardHeader>
    <CardContent class="space-y-4">
      <!-- Provider Selection -->
      <div class="space-y-2">
        <Label>Select AI Provider</Label>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          <button
            v-for="provider in providers"
            :key="provider.id"
            @click="selectProvider(provider.id)"
            :class="[
              'p-4 rounded-lg border-2 transition-all text-left relative overflow-hidden',
              selectedProvider === provider.id
                ? 'border-primary bg-primary/5 shadow-lg'
                : 'border-border hover:border-primary/50 hover:bg-muted/50'
            ]"
          >
            <div class="flex items-start justify-between mb-2">
              <div>
                <h3 class="font-semibold text-sm">{{ provider.name }}</h3>
                <p class="text-xs text-muted-foreground">{{ provider.model }}</p>
              </div>
              <div v-if="provider.status" 
                   :class="[
                     'h-3 w-3 rounded-full',
                     provider.status === 'working' ? 'bg-green-500 animate-pulse' :
                     provider.status === 'testing' ? 'bg-yellow-500 animate-pulse' :
                     provider.status === 'error' ? 'bg-red-500' : 'bg-gray-300'
                   ]"
              ></div>
            </div>
            
            <div class="flex items-center justify-between">
              <span v-if="provider.free" 
                    class="text-xs px-2 py-1 rounded-full bg-green-100 text-green-700 font-medium">
                FREE
              </span>
              <span v-else 
                    class="text-xs px-2 py-1 rounded-full bg-blue-100 text-blue-700 font-medium">
                Paid
              </span>
              
              <span v-if="provider.responseTime" class="text-xs text-muted-foreground">
                {{ provider.responseTime }}ms
              </span>
            </div>

            <div v-if="provider.error" class="mt-2 text-xs text-red-600 truncate">
              {{ provider.error }}
            </div>
          </button>
        </div>
      </div>

      <!-- Test Results -->
      <div v-if="testResults.length > 0" class="mt-6 space-y-2">
        <h3 class="font-semibold text-sm flex items-center gap-2">
          <CheckCircle2 class="h-4 w-4 text-green-600" />
          Test Results
        </h3>
        <div class="space-y-2 max-h-60 overflow-y-auto">
          <div v-for="(result, index) in testResults" :key="index"
               :class="[
                 'p-3 rounded-lg border text-sm',
                 result.success ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'
               ]">
            <div class="flex items-center justify-between mb-1">
              <span class="font-medium">{{ result.provider }}</span>
              <span :class="result.success ? 'text-green-600' : 'text-red-600'">
                {{ result.success ? '✓ Success' : '✗ Failed' }}
              </span>
            </div>
            <div class="text-xs text-muted-foreground">
              {{ result.message }}
            </div>
            <div v-if="result.responseTime" class="text-xs text-muted-foreground mt-1">
              Response time: {{ result.responseTime }}ms
            </div>
          </div>
        </div>
      </div>

      <!-- Current Provider Info -->
      <div class="p-4 bg-primary/5 rounded-lg border border-primary/20">
        <div class="flex items-start gap-3">
          <Info class="h-5 w-5 text-primary mt-0.5" />
          <div class="flex-1">
            <h4 class="font-semibold text-sm mb-1">Currently Active Provider</h4>
            <p class="text-xs text-muted-foreground mb-2">
              {{ getCurrentProviderInfo() }}
            </p>
            <div class="flex flex-wrap gap-2 text-xs">
              <span class="px-2 py-1 rounded-full bg-primary/10 text-primary">
                Model: {{ getCurrentModel() }}
              </span>
              <span v-if="isCurrentProviderFree()" 
                    class="px-2 py-1 rounded-full bg-green-100 text-green-700">
                FREE Tier
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="flex gap-2">
        <Button @click="testCurrentProvider" variant="outline" class="flex-1" :disabled="isTesting">
          <Play class="h-4 w-4 mr-2" />
          Test Current
        </Button>
        <Button @click="$emit('apply', providers.find(p => p.id === selectedProvider)!)" variant="default" class="flex-1">
          <Check class="h-4 w-4 mr-2" />
          Apply Changes
        </Button>
      </div>
    </CardContent>
  </Card>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import Card from '@/components-vue/ui/Card.vue';
import CardHeader from '@/components-vue/ui/CardHeader.vue';
import CardTitle from '@/components-vue/ui/CardTitle.vue';
import CardContent from '@/components-vue/ui/CardContent.vue';
import Button from '@/components-vue/ui/Button.vue';
import Label from '@/components-vue/ui/Label.vue';
import { 
  Zap, RefreshCw, CheckCircle2, Info, Play, Check, AlertCircle 
} from 'lucide-vue-next';
import { createLLMProvider } from '@/agents/llm/LLMProvider';

interface Provider {
  id: string;
  name: string;
  model: string;
  free: boolean;
  apiKey?: string;
  status?: 'working' | 'testing' | 'error' | 'unknown';
  responseTime?: number;
  error?: string;
}

interface TestResult {
  provider: string;
  success: boolean;
  message: string;
  responseTime?: number;
}

const selectedProvider = ref('gemini');
const isTesting = ref(false);
const testResults = ref<TestResult[]>([]);

const providers = ref<Provider[]>([
  {
    id: 'gemini',
    name: 'Google Gemini',
    model: 'gemini-1.5-flash-latest',
    free: false,
    apiKey: 'AIzaSyB5oma-7DH9VxKLU-MGFWy1QHf_UugNglE',
    status: 'unknown'
  },
  {
    id: 'qwen',
    name: 'Qwen 2.5 72B',
    model: 'qwen/qwen-2.5-72b-instruct:free',
    free: true,
    apiKey: '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',
    status: 'unknown'
  },
  {
    id: 'glm',
    name: 'GLM 4.5 Air',
    model: 'zerooneai/glm-4.5-air:free',
    free: true,
    apiKey: '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',
    status: 'unknown'
  },
  {
    id: 'kat',
    name: 'KAT-Coder-Pro V1',
    model: 'kwaipilot/kat-coder-pro:free',
    free: true,
    apiKey: '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',
    status: 'unknown'
  },
  {
    id: 'llama',
    name: 'Llama 4 Maverick',
    model: 'meta-llama/llama-4-maverick',
    free: false,
    apiKey: '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',
    status: 'unknown'
  },
  {
    id: 'openai',
    name: 'OpenAI GPT-4',
    model: 'gpt-4o',
    free: false,
    status: 'unknown'
  },
  {
    id: 'anthropic',
    name: 'Anthropic Claude',
    model: 'claude-3-5-sonnet-20241022',
    free: false,
    status: 'unknown'
  }
]);

const selectProvider = (providerId: string) => {
  selectedProvider.value = providerId;
};

const testProvider = async (provider: Provider): Promise<TestResult> => {
  const startTime = Date.now();
  
  try {
    provider.status = 'testing';
    
    const llmProvider = createLLMProvider({
      provider: provider.id as any,
      model: provider.model,
      apiKey: provider.apiKey,
      temperature: 0.7,
      maxTokens: 100
    });

    const response = await llmProvider.chat([
      { role: 'user', content: 'Say "Hello, I am working!" in one short sentence.' }
    ]);

    const responseTime = Date.now() - startTime;
    
    provider.status = 'working';
    provider.responseTime = responseTime;
    provider.error = undefined;

    return {
      provider: provider.name,
      success: true,
      message: response.content.substring(0, 100),
      responseTime
    };
  } catch (error) {
    const responseTime = Date.now() - startTime;
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    
    provider.status = 'error';
    provider.error = errorMessage;
    provider.responseTime = responseTime;

    return {
      provider: provider.name,
      success: false,
      message: errorMessage,
      responseTime
    };
  }
};

const testCurrentProvider = async () => {
  const provider = providers.value.find(p => p.id === selectedProvider.value);
  if (!provider) return;

  isTesting.value = true;
  testResults.value = [];
  
  const result = await testProvider(provider);
  testResults.value = [result];
  
  isTesting.value = false;
};

const testAllProviders = async () => {
  isTesting.value = true;
  testResults.value = [];
  
  console.log('🔄 Starting comprehensive provider testing...');
  
  for (let attempt = 1; attempt <= 5; attempt++) {
    console.log(`\n📋 Test Attempt ${attempt}/5`);
    
    for (const provider of providers.value) {
      console.log(`\n🧪 Testing ${provider.name}...`);
      const result = await testProvider(provider);
      
      testResults.value.push({
        ...result,
        provider: `${result.provider} (Attempt ${attempt})`
      });
      
      console.log(result.success ? '✅ Success!' : '❌ Failed!', result.message);
      
      // Small delay between tests
      await new Promise(resolve => setTimeout(resolve, 500));
    }
  }
  
  isTesting.value = false;
  
  // Summary
  const workingProviders = providers.value.filter(p => p.status === 'working');
  console.log(`\n✨ Testing Complete! ${workingProviders.length}/${providers.value.length} providers working`);
};

const getCurrentProviderInfo = () => {
  const provider = providers.value.find(p => p.id === selectedProvider.value);
  return provider ? `${provider.name} - ${provider.model}` : 'No provider selected';
};

const getCurrentModel = () => {
  const provider = providers.value.find(p => p.id === selectedProvider.value);
  return provider?.model || 'Unknown';
};

const isCurrentProviderFree = () => {
  const provider = providers.value.find(p => p.id === selectedProvider.value);
  return provider?.free || false;
};

defineEmits<{
  apply: [provider: Provider];
}>();
</script>
