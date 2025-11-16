<template>
  <main class="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
    <!-- Landing Page -->
    <div v-if="!hasStarted" class="min-h-screen flex items-center justify-center p-4">
      <div class="max-w-6xl w-full">
        <!-- Hero Section -->
        <div class="text-center mb-12 animate-fade-in">
          <div class="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-primary to-primary/60 rounded-2xl shadow-2xl mb-6 mx-auto">
            <Calculator class="h-10 w-10 text-white" />
          </div>
          <h1 class="text-5xl md:text-6xl font-bold mb-4 bg-gradient-to-r from-primary via-purple-600 to-primary bg-clip-text text-transparent">
            Tax Fluent AI
          </h1>
          <p class="text-xl md:text-2xl text-muted-foreground mb-3">
            Your Intelligent Tax Filing Assistant
          </p>
          <p class="text-sm text-muted-foreground max-w-2xl mx-auto">
            Powered by Multi-Agent AI | 6 LLM Providers | IRS Compliant
          </p>
        </div>

        <!-- Feature Cards -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <Card class="hover:shadow-xl transition-all duration-300 hover:-translate-y-1 border-2 hover:border-primary/50">
            <CardContent class="pt-6">
              <div class="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                <Sparkles class="h-6 w-6 text-primary" />
              </div>
              <h3 class="font-semibold text-lg mb-2">AI-Powered Analysis</h3>
              <p class="text-sm text-muted-foreground">
                Multi-agent system with 6 specialized AI agents for accurate tax calculations
              </p>
            </CardContent>
          </Card>

          <Card class="hover:shadow-xl transition-all duration-300 hover:-translate-y-1 border-2 hover:border-primary/50">
            <CardContent class="pt-6">
              <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
                <Shield class="h-6 w-6 text-green-600" />
              </div>
              <h3 class="font-semibold text-lg mb-2">IRS Compliant</h3>
              <p class="text-sm text-muted-foreground">
                Based on 2024 IRS tax code, Publication 17, and official regulations
              </p>
            </CardContent>
          </Card>

          <Card class="hover:shadow-xl transition-all duration-300 hover:-translate-y-1 border-2 hover:border-primary/50">
            <CardContent class="pt-6">
              <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                <TrendingUp class="h-6 w-6 text-purple-600" />
              </div>
              <h3 class="font-semibold text-lg mb-2">Real-time Optimization</h3>
              <p class="text-sm text-muted-foreground">
                Live tax optimization with AI-detected savings opportunities
              </p>
            </CardContent>
          </Card>
        </div>

        <!-- CTA Section -->
        <div class="text-center mb-12">
          <Card class="max-w-2xl mx-auto border-2 border-primary/20 bg-gradient-to-br from-white to-primary/5">
            <CardContent class="pt-8 pb-8">
              <h2 class="text-2xl font-bold mb-4">Ready to Get Started?</h2>
              <p class="text-muted-foreground mb-6">
                Choose your expertise level to customize your experience
              </p>
              
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <button
                  @click="startWithMode('Novice')"
                  class="p-4 border-2 rounded-lg hover:border-primary hover:bg-primary/5 transition-all text-left group"
                >
                  <div class="flex items-center gap-3 mb-2">
                    <User class="h-5 w-5 text-primary" />
                    <h3 class="font-semibold">Novice Mode</h3>
                  </div>
                  <p class="text-xs text-muted-foreground">Simple language, guided experience</p>
                </button>

                <button
                  @click="startWithMode('Expert')"
                  class="p-4 border-2 border-primary bg-primary text-primary-foreground rounded-lg hover:shadow-lg transition-all text-left group"
                >
                  <div class="flex items-center gap-3 mb-2">
                    <Zap class="h-5 w-5" />
                    <h3 class="font-semibold">Expert Mode</h3>
                  </div>
                  <p class="text-xs opacity-90">Technical terms, power tools</p>
                </button>

                <button
                  @click="startWithMode('Accessibility')"
                  class="p-4 border-2 rounded-lg hover:border-primary hover:bg-primary/5 transition-all text-left group"
                >
                  <div class="flex items-center gap-3 mb-2">
                    <Accessibility class="h-5 w-5 text-primary" />
                    <h3 class="font-semibold">Accessible</h3>
                  </div>
                  <p class="text-xs text-muted-foreground">Screen reader optimized</p>
                </button>
              </div>

              <Button @click="startWithMode('Expert')" size="lg" class="w-full md:w-auto px-8">
                <Rocket class="h-5 w-5 mr-2" />
                Launch Tax Assistant
              </Button>
            </CardContent>
          </Card>
        </div>

        <!-- Features List -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-4xl mx-auto">
          <div class="flex items-start gap-3 p-4 bg-white/50 backdrop-blur rounded-lg">
            <CheckCircle2 class="h-5 w-5 text-green-600 mt-1 flex-shrink-0" />
            <div>
              <h4 class="font-medium text-sm">Multi-Agent AI System</h4>
              <p class="text-xs text-muted-foreground">7 specialized agents working together</p>
            </div>
          </div>
          <div class="flex items-start gap-3 p-4 bg-white/50 backdrop-blur rounded-lg">
            <CheckCircle2 class="h-5 w-5 text-green-600 mt-1 flex-shrink-0" />
            <div>
              <h4 class="font-medium text-sm">6 LLM Providers</h4>
              <p class="text-xs text-muted-foreground">Including 3 FREE options</p>
            </div>
          </div>
          <div class="flex items-start gap-3 p-4 bg-white/50 backdrop-blur rounded-lg">
            <CheckCircle2 class="h-5 w-5 text-green-600 mt-1 flex-shrink-0" />
            <div>
              <h4 class="font-medium text-sm">Export Reports</h4>
              <p class="text-xs text-muted-foreground">PDF & Excel with IRS compliance</p>
            </div>
          </div>
          <div class="flex items-start gap-3 p-4 bg-white/50 backdrop-blur rounded-lg">
            <CheckCircle2 class="h-5 w-5 text-green-600 mt-1 flex-shrink-0" />
            <div>
              <h4 class="font-medium text-sm">Real-time Analysis</h4>
              <p class="text-xs text-muted-foreground">Live optimization suggestions</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Application -->
    <div v-else>
      <header class="sticky top-0 z-20 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b shadow-sm">
        <div class="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="h-10 w-10 bg-gradient-to-br from-primary to-primary/60 rounded-lg flex items-center justify-center shadow-lg">
              <Calculator class="h-6 w-6 text-primary-foreground" />
            </div>
            <div>
              <h1 class="text-xl md:text-2xl font-bold bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
                Tax Fluent AI
              </h1>
              <p class="text-xs text-muted-foreground">Powered by Multi-Agent AI</p>
            </div>
          </div>
          <div class="flex items-center gap-4">
            <div class="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full bg-green-50 border border-green-200">
              <div class="h-2 w-2 rounded-full bg-green-500 animate-pulse"></div>
              <span class="text-xs font-medium text-green-700">6 AI Agents Active</span>
            </div>
            <TransparencyIndicator />
            <ProviderSwitcher />
            <ModeSwitcher :mode="chatStore.mode" @change="chatStore.setMode" />
          </div>
        </div>
        
        <!-- Tab Navigation -->
        <TabNavigation :activeTab="activeTab" @change="handleTabChange" />
      </header>

    <DynamicLayoutContainer>
      <!-- Chat & Calculate Tab -->
      <section v-if="activeTab === 'chat'" class="max-w-7xl mx-auto px-4 py-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Conversation</CardTitle>
            </CardHeader>
            <CardContent>
              <div class="h-[50vh] md:h-[60vh] overflow-hidden flex flex-col">
                <div class="flex-1 overflow-y-auto space-y-3 pr-2">
                  <MessageBubble
                    v-for="m in chatStore.messages"
                    :key="m.id"
                    :message="m"
                    @explain="chatStore.requestExplanation"
                    @formAccept="handleFormAccept"
                    @formDismiss="handleFormDismiss"
                  />
                </div>
                <Separator class="my-3" />
                <InputBar
                  @send="handleSend"
                  :suggestions="chatStore.suggestions"
                  :mode="chatStore.mode"
                />
              </div>
            </CardContent>
          </Card>

          <!-- Tax Breakdown Visualization -->
          <TaxBreakdownChart
            v-if="taxCalculationData"
            :taxBrackets="taxCalculationData.brackets"
            :totalTax="taxCalculationData.totalTax"
            :effectiveRate="taxCalculationData.effectiveRate"
          />
        </div>

        <aside class="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Quick Inputs</CardTitle>
            </CardHeader>
            <CardContent class="space-y-4">
              <IntelligentField
                id="income"
                label="Annual Income"
                type="number"
                :required="true"
                help="Your total income before deductions."
              />
              <IntelligentField
                id="dependents"
                label="Dependents"
                type="number"
                :required="true"
                help="Number of qualifying dependents."
              />
              <IntelligentField
                id="state"
                label="State"
                placeholder="e.g., CA"
                help="State of residence for state taxes."
              />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Tips & Transparency</CardTitle>
            </CardHeader>
            <CardContent class="text-sm text-muted-foreground space-y-2">
              <p>We highlight the rules and thresholds used for each outcome.</p>
              <p>Ask for an explanation any time using the Explain button.</p>
              <div class="mt-4 p-3 bg-primary/5 rounded-lg border border-primary/20">
                <p class="text-xs font-medium text-primary">🏛️ Government Compliance</p>
                <p class="text-xs mt-1">All calculations follow IRS Publication 17 (2024) and current tax code regulations.</p>
              </div>
            </CardContent>
          </Card>

          <!-- Export Functionality -->
          <TaxReportExporter :taxData="taxCalculationData" />
        </aside>
      </section>

      <!-- Real-time Analysis Tab -->
      <section v-if="activeTab === 'analysis'" class="max-w-7xl mx-auto px-4 py-6">
        <RealTimeAnalysis />
      </section>

      <!-- Documents Tab -->
      <section v-if="activeTab === 'documents'" class="max-w-7xl mx-auto px-4 py-6">
        <Card>
          <CardHeader>
            <CardTitle class="flex items-center gap-2">
              <FileText class="h-5 w-5" />
              Document Management
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div class="text-center py-12">
              <Upload class="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <h3 class="text-lg font-semibold mb-2">Upload Tax Documents</h3>
              <p class="text-sm text-muted-foreground mb-4">Drag and drop W-2, 1099, or other tax forms</p>
              <Button>Select Files</Button>
            </div>
          </CardContent>
        </Card>
      </section>

      <!-- Compliance Tab -->
      <section v-if="activeTab === 'compliance'" class="max-w-7xl mx-auto px-4 py-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle class="flex items-center gap-2">
                <Shield class="h-5 w-5 text-green-600" />
                IRS Compliance Checklist
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div class="space-y-3">
                <div v-for="item in complianceItems" :key="item.label"
                     class="flex items-start gap-3 p-3 rounded-lg border">
                  <CheckCircle2 class="h-5 w-5 text-green-600 mt-0.5" v-if="item.completed" />
                  <AlertCircle class="h-5 w-5 text-yellow-600 mt-0.5" v-else />
                  <div class="flex-1">
                    <p class="font-medium text-sm">{{ item.label }}</p>
                    <p class="text-xs text-muted-foreground">{{ item.description }}</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Regulation References</CardTitle>
            </CardHeader>
            <CardContent>
              <div class="space-y-2 text-sm">
                <div v-for="ref in regulationRefs" :key="ref.title"
                     class="p-3 border rounded-lg hover:bg-muted/50 cursor-pointer transition-colors">
                  <p class="font-medium">{{ ref.title }}</p>
                  <p class="text-xs text-muted-foreground">{{ ref.description }}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      <!-- Export Tab -->
      <section v-if="activeTab === 'export'" class="max-w-4xl mx-auto px-4 py-6">
        <TaxReportExporter :taxData="taxCalculationData" />
      </section>

      <!-- Settings Tab -->
      <section v-if="activeTab === 'settings'" class="max-w-6xl mx-auto px-4 py-6">
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <!-- Provider Switcher -->
          <div class="lg:col-span-2">
            <ProviderSwitcher @apply="handleProviderChange" />
          </div>

          <!-- Agent Status -->
          <Card>
            <CardHeader>
              <CardTitle class="flex items-center gap-2">
                <Settings class="h-5 w-5" />
                Multi-Agent System
              </CardTitle>
            </CardHeader>
            <CardContent class="space-y-4">
              <div class="p-4 bg-muted rounded-lg">
                <h4 class="font-medium mb-3 flex items-center gap-2">
                  <Activity class="h-4 w-4 text-green-600" />
                  Agent Status
                </h4>
                <div class="space-y-2 text-sm">
                  <div v-for="agent in agentStatuses" :key="agent.name"
                       class="flex items-center justify-between p-2 rounded hover:bg-background transition-colors">
                    <span class="flex items-center gap-2">
                      <div :class="[
                        'h-2 w-2 rounded-full',
                        agent.active ? 'bg-green-500 animate-pulse' : 'bg-gray-300'
                      ]"></div>
                      {{ agent.name }}
                    </span>
                    <span :class="agent.active ? 'text-green-600' : 'text-gray-400'">{{ agent.status }}</span>
                  </div>
                </div>
              </div>

              <div class="p-4 bg-primary/5 rounded-lg border border-primary/20">
                <h4 class="font-medium mb-2 text-sm">System Info</h4>
                <div class="space-y-1 text-xs text-muted-foreground">
                  <p>• 6 AI Providers Available</p>
                  <p>• 7 Specialized Agents</p>
                  <p>• 22+ Tax Tools Active</p>
                  <p>• Real-time Analysis Enabled</p>
                </div>
              </div>

              <Button @click="reinitializeAgents" variant="outline" class="w-full">
                <RefreshCw class="h-4 w-4 mr-2" />
                Reinitialize Agents
              </Button>
            </CardContent>
          </Card>
        </div>
      </section>
    </DynamicLayoutContainer>
    </div>

    <ExplanationPanel
      :open="chatStore.explanationOpen"
      @update:open="chatStore.setExplanationOpen"
      :content="chatStore.explanationContent"
    />

    <TaxFormFiller
      :open="formFillerOpen"
      @update:open="formFillerOpen = $event"
      :suggestion="activeFormSuggestion"
    />
  </main>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useChatStore } from '@/stores/chatStore';
import { useAgentStore } from '@/stores/agentStore';
import { useToast } from '@/composables/useToast';
import Card from '@/components-vue/ui/Card.vue';
import CardContent from '@/components-vue/ui/CardContent.vue';
import CardHeader from '@/components-vue/ui/CardHeader.vue';
import CardTitle from '@/components-vue/ui/CardTitle.vue';
import Separator from '@/components-vue/ui/Separator.vue';
import MessageBubble from '@/components-vue/chat/MessageBubble.vue';
import InputBar from '@/components-vue/chat/InputBar.vue';
import TaxFormFiller from '@/components-vue/chat/TaxFormFiller.vue';
import ModeSwitcher from '@/components-vue/adaptive/ModeSwitcher.vue';
import ProviderSwitcher from '@/components-vue/adaptive/ProviderSwitcher.vue';
import ExplanationPanel from '@/components-vue/xai/ExplanationPanel.vue';
import TransparencyIndicator from '@/components-vue/shared/TransparencyIndicator.vue';
import IntelligentField from '@/components-vue/inputs/IntelligentField.vue';
import DynamicLayoutContainer from '@/components-vue/dynamic/DynamicLayoutContainer.vue';
import TaxBreakdownChart from '@/components-vue/visualization/TaxBreakdownChart.vue';
import TaxReportExporter from '@/components-vue/export/TaxReportExporter.vue';
import TabNavigation from '@/components-vue/navigation/TabNavigation.vue';
import RealTimeAnalysis from '@/components-vue/analysis/RealTimeAnalysis.vue';
import Button from '@/components-vue/ui/Button.vue';
import Label from '@/components-vue/ui/Label.vue';
import Select from '@/components-vue/ui/Select.vue';
import SelectItem from '@/components-vue/ui/SelectItem.vue';
import { 
  Calculator, FileText, Upload, Shield, CheckCircle2, 
  AlertCircle, Settings, RefreshCw, Activity, Sparkles,
  TrendingUp, User, Zap, Accessibility, Rocket
} from 'lucide-vue-next';

const chatStore = useChatStore();
const agentStore = useAgentStore();
const { toast } = useToast();

// Landing page state
const hasStarted = ref(false);

const startWithMode = (mode: 'Novice' | 'Expert' | 'Accessibility') => {
  chatStore.setMode(mode);
  hasStarted.value = true;
  agentStore.initialize();
  
  toast({
    title: 'Welcome to Tax Fluent AI!',
    description: `${mode} mode activated. Your AI tax assistant is ready.`,
  });
};

// Initialize agent store
// agentStore.initialize(); // Don't auto-initialize, wait for user to start

// Active tab state
const activeTab = ref('chat');

// Form filler state
const formFillerOpen = ref(false);
const activeFormSuggestion = ref();

// Tax calculation data for charts
const taxCalculationData = ref({
  totalIncome: 75000,
  totalDeductions: 0,
  taxableIncome: 0,
  totalTax: 12358,
  effectiveRate: 16.5,
  filingStatus: 'Single',
  childTaxCredit: 0,
  eitc: 0,
  brackets: [
    { label: '10% Bracket', amount: 1160, color: '#3b82f6' },
    { label: '12% Bracket', amount: 4266, color: '#8b5cf6' },
    { label: '22% Bracket', amount: 6127, color: '#ec4899' }
  ]
});

const handleTabChange = (tabId: string) => {
  activeTab.value = tabId;
};

// Compliance data
const complianceItems = ref([
  { label: 'Income Reporting', description: 'All income sources reported per IRS Form 1040', completed: true },
  { label: 'Standard Deduction', description: 'Applied 2024 standard deduction ($14,600)', completed: true },
  { label: 'Tax Brackets', description: 'Calculated per IRS Publication 17 (2024)', completed: true },
  { label: 'Credit Eligibility', description: 'Verified eligibility for tax credits', completed: true },
  { label: 'Document Upload', description: 'Upload W-2 and 1099 forms for verification', completed: false }
]);

const regulationRefs = ref([
  { title: 'IRS Publication 17 (2024)', description: 'Your Federal Income Tax Guide' },
  { title: 'IRS Form 1040 Instructions', description: 'U.S. Individual Income Tax Return' },
  { title: 'IRS Publication 501', description: 'Dependents, Standard Deduction, and Filing Information' },
  { title: 'IRS Publication 972', description: 'Child Tax Credit and Credit for Other Dependents' }
]);

const agentStatuses = ref([
  { name: 'Orchestrator Agent', status: 'Active', active: true },
  { name: 'Tax Calculator', status: 'Active', active: true },
  { name: 'Document Processor', status: 'Active', active: true },
  { name: 'Compliance Checker', status: 'Active', active: true },
  { name: 'Tax Advisor', status: 'Active', active: true },
  { name: 'Form Filler', status: 'Ready', active: false },
  { name: 'Optimization Analyzer', status: 'Ready', active: false }
]);

const handleProviderChange = (provider: any) => {
  console.log('Switching to provider:', provider.name);
  toast({
    title: 'Provider Changed',
    description: `Now using ${provider.name} for AI responses`,
  });
  
  // Set the new provider in agent store
  agentStore.setProvider({
    provider: provider.id,
    model: provider.model,
    apiKey: provider.apiKey,
    temperature: 0.7,
    maxTokens: 2000
  });
};

const reinitializeAgents = () => {
  agentStore.initialize();
  toast({
    title: 'Agents Reinitialized',
    description: 'All AI agents have been reset and reloaded',
  });
};

// Sample tax calculation data (will be populated from agent responses)

const handleSend = async (message: string) => {
  try {
    // Send to AI agent system
    const response = await agentStore.sendMessage(message);
    
    // Update chat with AI response
    chatStore.sendMessage(message);
    
    // Extract tax calculation data if present
    if (response.data) {
      if (response.data.totalTax) {
        taxCalculationData.value = {
          ...taxCalculationData.value,
          ...response.data,
          brackets: response.data.breakdown?.map((b: any, i: number) => ({
            label: `${b.rate}% Bracket`,
            amount: b.tax,
            color: ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981'][i % 5]
          })) || taxCalculationData.value.brackets
        };
      }
    }
    
    if (message.toLowerCase().includes('itemize') && chatStore.mode !== 'Expert') {
      toast({
        title: 'Try Expert Mode?',
        description: "You're using technical terms. Switch to Expert for power tools.",
      });
    }
  } catch (error) {
    console.error('Error sending message:', error);
    toast({
      title: 'Error',
      description: error instanceof Error ? error.message : 'Failed to process message',
      variant: 'destructive'
    });
  }
};

const handleFormAccept = (suggestion: any) => {
  console.log('Form accepted:', suggestion);
  activeFormSuggestion.value = suggestion;
  formFillerOpen.value = true;
  
  toast({
    title: 'Form Filling Started',
    description: `Opening ${suggestion.formName} for filling...`,
  });
};

const handleFormDismiss = (id: string) => {
  console.log('Form dismissed:', id);
  // The chat store already handles removing the suggestion
};
</script>

<style scoped>
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fade-in 0.8s ease-out;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-10px);
  }
}

.animate-float {
  animation: float 3s ease-in-out infinite;
}
</style>
