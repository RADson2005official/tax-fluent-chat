<template>
  <Card class="w-full max-w-4xl mx-auto">
    <CardHeader>
      <CardTitle class="flex items-center gap-2">
        <Zap class="h-5 w-5 text-blue-600" />
        LangChain Autonomous Tax Filing
      </CardTitle>
      <p class="text-sm text-muted-foreground">
        Powered by LangChain multi-agent workflow orchestration
      </p>
    </CardHeader>
    
    <CardContent>
      <!-- Workflow Progress -->
      <div v-if="langchainStore.currentWorkflow" class="mb-6">
        <div class="flex justify-between items-center mb-2">
          <span class="text-sm font-medium">Workflow Progress</span>
          <span class="text-sm text-muted-foreground">
            {{ Math.round(langchainStore.workflowProgress) }}%
          </span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-2">
          <div 
            class="bg-blue-600 h-2 rounded-full transition-all duration-300"
            :style="{ width: `${langchainStore.workflowProgress}%` }"
          ></div>
        </div>
      </div>

      <!-- Current Step -->
      <div v-if="langchainStore.currentStep" class="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
        <div class="flex items-start gap-3">
          <div class="mt-0.5">
            <CheckCircle v-if="langchainStore.currentStep.status === 'completed'" class="h-5 w-5 text-green-600" />
            <Loader v-else-if="langchainStore.currentStep.status === 'in-progress'" class="h-5 w-5 text-blue-600 animate-spin" />
            <Circle v-else class="h-5 w-5 text-gray-400" />
          </div>
          <div class="flex-1">
            <h4 class="font-medium text-sm">{{ langchainStore.currentStep.name }}</h4>
            <p class="text-xs text-muted-foreground mt-1">
              {{ langchainStore.currentStep.description }}
            </p>
          </div>
        </div>
      </div>

      <!-- Workflow Steps -->
      <div v-if="langchainStore.currentWorkflow" class="space-y-2 mb-6">
        <h4 class="text-sm font-medium mb-3">Workflow Steps</h4>
        <div
          v-for="step in langchainStore.currentWorkflow.steps"
          :key="step.id"
          class="flex items-center gap-3 p-3 rounded-lg border"
          :class="{
            'bg-green-50 border-green-200': step.status === 'completed',
            'bg-blue-50 border-blue-200': step.status === 'in-progress',
            'bg-gray-50 border-gray-200': step.status === 'pending',
            'bg-red-50 border-red-200': step.status === 'failed'
          }"
        >
          <CheckCircle v-if="step.status === 'completed'" class="h-4 w-4 text-green-600" />
          <Loader v-else-if="step.status === 'in-progress'" class="h-4 w-4 text-blue-600 animate-spin" />
          <AlertCircle v-else-if="step.status === 'failed'" class="h-4 w-4 text-red-600" />
          <Circle v-else class="h-4 w-4 text-gray-400" />
          
          <div class="flex-1">
            <p class="text-sm font-medium">{{ step.name }}</p>
            <p v-if="step.error" class="text-xs text-red-600 mt-1">{{ step.error }}</p>
          </div>
          
          <Badge v-if="step.status === 'completed'" variant="default">Complete</Badge>
          <Badge v-else-if="step.status === 'in-progress'" variant="secondary">In Progress</Badge>
          <Badge v-else-if="step.status === 'failed'" variant="destructive">Failed</Badge>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex gap-3">
        <Button
          @click="startWorkflow"
          :disabled="langchainStore.isProcessing"
          class="flex-1"
        >
          <Play class="h-4 w-4 mr-2" />
          Start Autonomous Workflow
        </Button>
        
        <Button
          v-if="langchainStore.currentWorkflow"
          @click="resetWorkflow"
          variant="outline"
        >
          <RotateCcw class="h-4 w-4 mr-2" />
          Reset
        </Button>
      </div>

      <!-- Status Messages -->
      <div v-if="statusMessages.length > 0" class="mt-6">
        <h4 class="text-sm font-medium mb-2">Activity Log</h4>
        <div class="space-y-1 max-h-40 overflow-y-auto">
          <p
            v-for="(msg, index) in statusMessages.slice(-10)"
            :key="index"
            class="text-xs text-muted-foreground"
          >
            {{ msg }}
          </p>
        </div>
      </div>
    </CardContent>
  </Card>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useLangChainStore } from '@/stores/langchainStore';
import Card from '@/components-vue/ui/Card.vue';
import CardHeader from '@/components-vue/ui/CardHeader.vue';
import CardTitle from '@/components-vue/ui/CardTitle.vue';
import CardContent from '@/components-vue/ui/CardContent.vue';
import Button from '@/components-vue/ui/Button.vue';
import Badge from '@/components-vue/ui/Badge.vue';
import { Zap, Play, RotateCcw, CheckCircle, Loader, Circle, AlertCircle } from 'lucide-vue-next';

const langchainStore = useLangChainStore();
const statusMessages = ref<string[]>([]);

async function startWorkflow() {
  statusMessages.value = [];
  statusMessages.value.push('Initializing LangChain workflow...');

  // Sample data - in production, get from user input
  const initialData = {
    filingStatus: 'single',
    documents: [
      { type: 'w2', file: 'sample-w2-data' },
      { type: '1099', file: 'sample-1099-data' }
    ],
    income: {
      wages: 75000,
      selfEmployment: 15000
    }
  };

  try {
    for await (const update of langchainStore.streamWorkflow(
      'demo-user',
      2024,
      initialData
    )) {
      if (update.type === 'step_start') {
        statusMessages.value.push(`▶️ Starting: ${update.step?.name}`);
      } else if (update.type === 'step_complete') {
        statusMessages.value.push(`✅ Completed: ${update.step?.name}`);
      } else if (update.type === 'step_progress') {
        statusMessages.value.push(`⚙️ ${update.message}`);
      } else if (update.type === 'workflow_complete') {
        statusMessages.value.push('🎉 Tax filing workflow completed successfully!');
      } else if (update.type === 'error') {
        statusMessages.value.push(`❌ Error: ${update.message}`);
      }
    }
  } catch (error) {
    statusMessages.value.push(`❌ Workflow failed: ${error}`);
  }
}

function resetWorkflow() {
  langchainStore.reset();
  statusMessages.value = [];
}
</script>
