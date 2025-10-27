<template>
  <main class="min-h-screen bg-background">
    <header class="sticky top-0 z-10 bg-background/80 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b">
      <div class="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
        <h1 class="text-xl md:text-2xl font-semibold">Tax Fluent Chat</h1>
        <div class="flex items-center gap-4">
          <TransparencyIndicator />
          <ModeSwitcher :mode="chatStore.mode" @change="chatStore.setMode" />
        </div>
      </div>
    </header>

    <DynamicLayoutContainer>
      <section class="max-w-6xl mx-auto px-4 py-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card class="lg:col-span-2">
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
            </CardContent>
          </Card>
        </aside>
      </section>
    </DynamicLayoutContainer>

    <ExplanationPanel
      :open="chatStore.explanationOpen"
      @update:open="chatStore.setExplanationOpen"
      :content="chatStore.explanationContent"
    />
  </main>
</template>

<script setup lang="ts">
import { useChatStore } from '@/stores/chatStore';
import { useToast } from '@/composables/useToast';
import Card from '@/components-vue/ui/Card.vue';
import CardContent from '@/components-vue/ui/CardContent.vue';
import CardHeader from '@/components-vue/ui/CardHeader.vue';
import CardTitle from '@/components-vue/ui/CardTitle.vue';
import Separator from '@/components-vue/ui/Separator.vue';
import MessageBubble from '@/components-vue/chat/MessageBubble.vue';
import InputBar from '@/components-vue/chat/InputBar.vue';
import ModeSwitcher from '@/components-vue/adaptive/ModeSwitcher.vue';
import ExplanationPanel from '@/components-vue/xai/ExplanationPanel.vue';
import TransparencyIndicator from '@/components-vue/shared/TransparencyIndicator.vue';
import IntelligentField from '@/components-vue/inputs/IntelligentField.vue';
import DynamicLayoutContainer from '@/components-vue/dynamic/DynamicLayoutContainer.vue';

const chatStore = useChatStore();
const { toast } = useToast();

const handleSend = (message: string) => {
  chatStore.sendMessage(message);
  
  if (message.toLowerCase().includes('itemize') && chatStore.mode !== 'Expert') {
    toast({
      title: 'Try Expert Mode?',
      description: "You're using technical terms. Switch to Expert for power tools.",
    });
  }
};
</script>
