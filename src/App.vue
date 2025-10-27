<template>
  <div class="min-h-screen bg-background">
    <header class="sticky top-0 z-10 bg-background/80 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b">
      <div class="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
        <h1 class="text-xl md:text-2xl font-semibold">Tax Fluent Chat</h1>
        <div class="flex items-center gap-4">
          <TransparencyIndicator />
          <ModeSwitcher :mode="chatStore.mode" @change="handleModeChange" />
        </div>
      </div>
    </header>

    <main class="max-w-6xl mx-auto px-4 py-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-2">
        <div class="border rounded-lg shadow-sm bg-card">
          <div class="p-6 border-b">
            <h2 class="text-2xl font-semibold">Conversation</h2>
          </div>
          <div class="p-6">
            <div class="h-[50vh] md:h-[60vh] overflow-hidden flex flex-col">
              <div class="flex-1 overflow-y-auto space-y-3 pr-2">
                <MessageBubble
                  v-for="message in chatStore.messages"
                  :key="message.id"
                  :message="message"
                  @explain="handleExplain"
                />
              </div>
              <div class="border-t my-3"></div>
              <InputBar
                :suggestions="chatStore.suggestions"
                :mode="chatStore.mode"
                @send="handleSend"
              />
            </div>
          </div>
        </div>
      </div>

      <aside class="space-y-4">
        <div class="border rounded-lg shadow-sm bg-card">
          <div class="p-6 border-b">
            <h2 class="text-2xl font-semibold">Quick Inputs</h2>
          </div>
          <div class="p-6 space-y-4">
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
          </div>
        </div>

        <div class="border rounded-lg shadow-sm bg-card">
          <div class="p-6 border-b">
            <h2 class="text-2xl font-semibold">Tips & Transparency</h2>
          </div>
          <div class="p-6 text-sm text-muted-foreground space-y-2">
            <p>We highlight the rules and thresholds used for each outcome.</p>
            <p>Ask for an explanation any time using the Explain button.</p>
          </div>
        </div>
      </aside>
    </main>

    <ExplanationPanel />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useChatStore } from './stores/chat'
import { useExplanationStore } from './stores/explanation'
import { useAuthStore } from './stores/auth'
import MessageBubble from './components/chat/MessageBubble.vue'
import InputBar from './components/chat/InputBar.vue'
import ModeSwitcher from './components/adaptive/ModeSwitcher.vue'
import ExplanationPanel from './components/xai/ExplanationPanel.vue'
import TransparencyIndicator from './components/shared/TransparencyIndicator.vue'
import IntelligentField from './components/inputs/IntelligentField.vue'
import type { Mode } from './stores/chat'

const chatStore = useChatStore()
const explanationStore = useExplanationStore()
const authStore = useAuthStore()

onMounted(() => {
  authStore.loadFromStorage()
})

function handleModeChange(newMode: Mode) {
  chatStore.setMode(newMode)
}

function handleSend(message: string) {
  chatStore.sendMessage(message)
  
  // Show expert mode suggestion for technical terms
  if (message.toLowerCase().includes('itemize') && chatStore.mode !== 'Expert') {
    // Could show a toast notification here
    console.log('Try Expert Mode? You\'re using technical terms.')
  }
}

function handleExplain(id: string) {
  explanationStore.showExplanation(
    'This answer was generated based on your inputs and 2024 IRS thresholds. ' +
    'It considered filing status, dependents, and phase-out ranges, ' +
    'and cross-checked income caps.'
  )
}
  <TooltipProvider>
    <RouterView />
  </TooltipProvider>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router';
import { TooltipProvider } from 'radix-vue';
</script>
