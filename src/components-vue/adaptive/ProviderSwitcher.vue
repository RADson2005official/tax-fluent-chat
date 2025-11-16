<template>
  <div class="flex flex-col gap-2">
    <Label for="provider">AI Provider</Label>
    <Select v-model="selectedProvider" @update:model-value="handleProviderChange">
      <SelectItem value="qwen">Qwen (Free)</SelectItem>
      <SelectItem value="glm">GLM (Free)</SelectItem>
      <SelectItem value="llama">Llama (Free)</SelectItem>
      <SelectItem value="gemini">Gemini</SelectItem>
      <SelectItem value="openai">OpenAI</SelectItem>
      <SelectItem value="anthropic">Anthropic</SelectItem>
    </Select>
    <p class="text-xs text-muted-foreground">
      Switch providers if experiencing issues
    </p>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import Select from '@/components-vue/ui/Select.vue';
import SelectItem from '@/components-vue/ui/SelectItem.vue';
import Label from '@/components-vue/ui/Label.vue';
import { useAgentStore } from '@/stores/agentStore';
import type { LLMConfig } from '@/agents/llm/LLMProvider';

const agentStore = useAgentStore();

const selectedProvider = ref<string>('qwen');

const providerConfigs: Record<string, LLMConfig> = {
  qwen: {
    provider: 'qwen',
    model: 'qwen/qwen-2.5-72b-instruct:free',
    temperature: 0.7,
    maxTokens: 2000
  },
  glm: {
    provider: 'glm',
    model: 'zhipu/glm-4-9b-chat:free',
    temperature: 0.7,
    maxTokens: 2000
  },
  llama: {
    provider: 'llama',
    model: 'meta-llama/llama-3.1-8b-instruct:free',
    temperature: 0.7,
    maxTokens: 2000
  },
  gemini: {
    provider: 'gemini',
    model: 'gemini-1.5-flash',
    temperature: 0.7,
    maxTokens: 2000
  },
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
  }
};

function handleProviderChange(value: string) {
  const config = providerConfigs[value];
  if (config) {
    agentStore.setProvider(config);
    console.log(`Switched to ${value} provider`);
  }
}

// Initialize with current provider
watch(() => agentStore.currentProvider, (newProvider) => {
  selectedProvider.value = newProvider.provider;
}, { immediate: true });
</script>
