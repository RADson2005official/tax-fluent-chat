<template>
  <DynamicLayoutContainer>
    <div class="max-w-7xl mx-auto h-[calc(100vh-8rem)]">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full">
        <!-- Chat Area -->
        <div class="lg:col-span-2 flex flex-col h-full">
          <!-- Chat Header -->
          <div class="flex justify-between items-center mb-4">
            <div class="space-y-1">
              <h1 class="text-2xl font-bold">Tax Assistant</h1>
              <p class="text-muted-foreground">Ask questions about your tax filing</p>
            </div>
            <Button variant="outline" @click="router.push('/dashboard')">
              <ArrowLeft class="mr-2 h-4 w-4" />
              Back
            </Button>
          </div>

          <!-- Chat Container -->
          <Card class="flex-1 flex flex-col overflow-hidden">
            <!-- Messages Area -->
            <div ref="messagesContainer" class="flex-1 overflow-y-auto p-6 space-y-4">
              <!-- Welcome Message -->
              <div v-if="messages.length === 0" class="text-center py-12">
                <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 mb-4">
                  <Bot class="h-8 w-8 text-primary" />
                </div>
                <h3 class="text-lg font-semibold mb-2">Welcome to Tax Assistant!</h3>
                <p class="text-muted-foreground mb-6">I'm here to help you with your tax filing questions.</p>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-2xl mx-auto">
                  <button 
                    v-for="suggestion in suggestions" :key="suggestion"
                    @click="sendMessage(suggestion)"
                    class="p-3 text-left rounded-lg border hover:border-primary hover:bg-primary/5 transition-colors"
                  >
                    <div class="text-sm">{{ suggestion }}</div>
                  </button>
                </div>
              </div>

              <!-- Chat Messages -->
              <div 
                v-for="(message, index) in messages" :key="index"
                :class="cn(
                  'flex gap-3',
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                )"
              >
                <div 
                  v-if="message.role === 'assistant'"
                  class="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center"
                >
                  <Bot class="h-5 w-5 text-primary" />
                </div>
                <div 
                  :class="cn(
                    'max-w-[85%] rounded-lg p-4',
                    message.role === 'user' 
                      ? 'bg-primary text-primary-foreground' 
                      : 'bg-muted'
                  )"
                >
                  <p class="text-sm whitespace-pre-wrap">{{ message.content }}</p>
                </div>
                <div 
                  v-if="message.role === 'user'"
                  class="flex-shrink-0 w-8 h-8 rounded-full bg-primary flex items-center justify-center"
                >
                  <User class="h-5 w-5 text-primary-foreground" />
                </div>
              </div>

              <!-- Typing Indicator -->
              <div v-if="isTyping" class="flex gap-3">
                <div class="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                  <Bot class="h-5 w-5 text-primary" />
                </div>
                <div class="bg-muted rounded-lg p-4">
                  <div class="flex gap-1">
                    <div class="w-2 h-2 rounded-full bg-muted-foreground animate-bounce" style="animation-delay: 0ms"></div>
                    <div class="w-2 h-2 rounded-full bg-muted-foreground animate-bounce" style="animation-delay: 150ms"></div>
                    <div class="w-2 h-2 rounded-full bg-muted-foreground animate-bounce" style="animation-delay: 300ms"></div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Input Area -->
            <div class="border-t p-4">
              <form @submit.prevent="handleSubmit" class="flex gap-3">
                <Input 
                  v-model="inputMessage" 
                  placeholder="Ask me anything about your taxes..."
                  class="flex-1"
                  :disabled="isTyping"
                />
                <Button type="submit" :disabled="!inputMessage.trim() || isTyping">
                  <Send class="h-4 w-4" />
                </Button>
              </form>
            </div>
          </Card>
        </div>

        <!-- Visualization Sidebar -->
        <div class="hidden lg:flex flex-col gap-6 h-full overflow-hidden">
          <Card class="flex-1 flex flex-col min-h-[300px]">
            <CardHeader class="pb-2">
              <CardTitle class="text-sm font-medium">Tax Flow Visualization</CardTitle>
            </CardHeader>
            <CardContent class="flex-1 p-0">
              <SankeyDiagram />
            </CardContent>
          </Card>
          <LiveTracking class="h-[300px]" />
        </div>
      </div>
    </div>
  </DynamicLayoutContainer>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, Bot, User, Send } from 'lucide-vue-next'
import DynamicLayoutContainer from '@/components-vue/dynamic/DynamicLayoutContainer.vue'
import CardTitle from '@/components-vue/ui/CardTitle.vue'
import CardContent from '@/components-vue/ui/CardContent.vue'
import Button from '@/components-vue/ui/Button.vue'
import Input from '@/components-vue/ui/Input.vue'
import { cn } from '@/lib/utils'
import SankeyDiagram from '@/components-vue/visualization/SankeyDiagram.vue'
import LiveTracking from '@/components-vue/visualization/LiveTracking.vue'

const router = useRouter()

interface Message {
  role: 'user' | 'assistant'
  content: string
}

const messages = ref<Message[]>([])
const inputMessage = ref('')
const isTyping = ref(false)
const messagesContainer = ref<HTMLElement | null>(null)

const suggestions = [
  "What deductions am I eligible for?",
  "How is my tax calculated?",
  "What documents do I need?",
  "Can I claim home office deduction?"
]

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

const sendMessage = async (content: string) => {
  if (!content.trim()) return

  // Add user message
  messages.value.push({ role: 'user', content })
  inputMessage.value = ''
  scrollToBottom()

  // Simulate AI response
  isTyping.value = true
  scrollToBottom()

  setTimeout(() => {
    isTyping.value = false
    const responses = [
      "I can help you with that! To claim deductions, you'll need to gather all your eligible expenses and receipts. Common deductions include: 80C (investments), 80D (health insurance), and HRA (house rent allowance).",
      "Your tax is calculated based on your income slab. For the financial year 2024-25, if you earn between ₹3-7 lakhs, you pay 5% tax. Between ₹7-10 lakhs, it's 10%, and so on.",
      "You'll need your Form 16 from your employer, bank statements, investment proofs, and details of any additional income. I can guide you through uploading these documents.",
      "Yes! If you work from home, you may be eligible for home office deductions. This includes a portion of rent, electricity, and internet bills proportional to your workspace."
    ]
    const randomResponse = responses[Math.floor(Math.random() * responses.length)]
    messages.value.push({ role: 'assistant', content: randomResponse })
    scrollToBottom()
  }, 1500)
}

const handleSubmit = () => {
  sendMessage(inputMessage.value)
}
</script>
