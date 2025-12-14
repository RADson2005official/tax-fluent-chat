<template>
  <DynamicLayoutContainer>
    <div class="max-w-6xl mx-auto h-[calc(100vh-8rem)]">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full">
        <!-- Chat Area -->
        <div class="lg:col-span-2 flex flex-col h-full">
          <!-- Header -->
          <div class="flex justify-between items-center mb-4">
            <div class="space-y-1">
              <h1 class="text-2xl font-bold flex items-center gap-2">
                <MessageSquare class="h-6 w-6 text-primary" />
                Conversational Tax Filing
              </h1>
              <p class="text-muted-foreground">Answer questions step-by-step to file your taxes</p>
            </div>
            <div class="flex items-center gap-3">
              <!-- Progress Badge -->
              <div class="px-3 py-1 rounded-full bg-primary/10 text-primary text-sm font-medium">
                {{ Math.round(progress) }}% Complete
              </div>
              <Button variant="outline" size="sm" @click="restartFiling">
                <RotateCcw class="mr-2 h-4 w-4" />
                Restart
              </Button>
            </div>
          </div>

          <!-- Progress Bar -->
          <div class="h-2 bg-muted rounded-full mb-4 overflow-hidden">
            <div 
              class="h-full bg-gradient-to-r from-primary to-purple-500 transition-all duration-500"
              :style="{ width: `${progress}%` }"
            ></div>
          </div>

          <!-- Category Indicator -->
          <div v-if="currentCategory" class="mb-4 flex items-center gap-2">
            <div class="px-3 py-1 rounded-full bg-muted text-sm">
              {{ currentCategory }}
            </div>
            <ChevronRight class="h-4 w-4 text-muted-foreground" />
            <span class="text-sm text-muted-foreground">{{ currentStep }}</span>
          </div>

          <!-- Chat Container -->
          <Card class="flex-1 flex flex-col overflow-hidden">
            <!-- Messages Area -->
            <div ref="messagesContainer" class="flex-1 overflow-y-auto p-6 space-y-4">
              <div 
                v-for="(message, index) in messages" :key="index"
                :class="cn(
                  'flex gap-3',
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                )"
              >
                <div 
                  v-if="message.role === 'assistant'"
                  class="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-primary/20 to-purple-500/20 flex items-center justify-center"
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
                  <div class="text-sm whitespace-pre-wrap" v-html="formatMessage(message.content)"></div>
                </div>
                <div 
                  v-if="message.role === 'user'"
                  class="flex-shrink-0 w-8 h-8 rounded-full bg-primary flex items-center justify-center"
                >
                  <User class="h-5 w-5 text-primary-foreground" />
                </div>
              </div>

              <!-- Typing Indicator -->
              <div v-if="isLoading" class="flex gap-3">
                <div class="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-primary/20 to-purple-500/20 flex items-center justify-center">
                  <Bot class="h-5 w-5 text-primary animate-pulse" />
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
              <form @submit.prevent="sendMessage" class="flex gap-3">
                <Input 
                  v-model="inputMessage" 
                  :placeholder="isComplete ? 'Filing complete! Generate your PDF →' : 'Type your answer...'"
                  class="flex-1"
                  :disabled="isLoading || isComplete"
                />
                <Button 
                  v-if="!isComplete"
                  type="submit" 
                  :disabled="!inputMessage.trim() || isLoading"
                >
                  <Send class="h-4 w-4" />
                </Button>
                <Button 
                  v-else
                  type="button"
                  @click="downloadPDF"
                  class="bg-green-600 hover:bg-green-700"
                >
                  <Download class="mr-2 h-4 w-4" />
                  Download PDF
                </Button>
              </form>
            </div>
          </Card>
        </div>

        <!-- Live Extracted Data Sidebar -->
        <div class="hidden lg:flex flex-col gap-4 h-full overflow-hidden">
          <!-- Progress Summary -->
          <Card class="p-4">
            <h3 class="text-sm font-semibold mb-3 flex items-center gap-2">
              <ClipboardCheck class="h-4 w-4 text-primary" />
              Filing Progress
            </h3>
            <div class="space-y-2">
              <div v-for="category in categories" :key="category.name" class="flex items-center justify-between">
                <span class="text-sm">{{ category.name }}</span>
                <div class="flex items-center gap-2">
                  <div class="w-20 h-1.5 bg-muted rounded-full overflow-hidden">
                    <div 
                      class="h-full bg-primary transition-all"
                      :style="{ width: `${category.progress}%` }"
                    ></div>
                  </div>
                  <Check v-if="category.progress === 100" class="h-4 w-4 text-green-500" />
                </div>
              </div>
            </div>
          </Card>

          <!-- Extracted Data -->
          <Card class="flex-1 flex flex-col overflow-hidden">
            <CardHeader class="pb-2 border-b">
              <CardTitle class="text-sm font-medium flex items-center gap-2">
                <FileText class="h-4 w-4" />
                Extracted Information
              </CardTitle>
            </CardHeader>
            <CardContent class="flex-1 overflow-y-auto p-4 space-y-4">
              <!-- Personal Info -->
              <div v-if="extractedData.personal_info && Object.keys(extractedData.personal_info).length">
                <h4 class="text-xs font-semibold text-muted-foreground uppercase mb-2">Personal Info</h4>
                <div class="space-y-1 text-sm">
                  <div v-if="extractedData.personal_info.name" class="flex justify-between">
                    <span class="text-muted-foreground">Name</span>
                    <span class="font-medium">{{ extractedData.personal_info.name }}</span>
                  </div>
                  <div v-if="extractedData.personal_info.pan_number" class="flex justify-between">
                    <span class="text-muted-foreground">PAN</span>
                    <span class="font-medium font-mono">{{ extractedData.personal_info.pan_number }}</span>
                  </div>
                  <div v-if="extractedData.personal_info.email" class="flex justify-between">
                    <span class="text-muted-foreground">Email</span>
                    <span class="font-medium text-xs">{{ extractedData.personal_info.email }}</span>
                  </div>
                </div>
              </div>

              <!-- Income -->
              <div v-if="extractedData.income && Object.keys(extractedData.income).length">
                <h4 class="text-xs font-semibold text-muted-foreground uppercase mb-2">Income</h4>
                <div class="space-y-1 text-sm">
                  <div v-if="extractedData.income.employer_name" class="flex justify-between">
                    <span class="text-muted-foreground">Employer</span>
                    <span class="font-medium">{{ extractedData.income.employer_name }}</span>
                  </div>
                  <div v-if="extractedData.income.salary" class="flex justify-between">
                    <span class="text-muted-foreground">Salary</span>
                    <span class="font-medium text-green-600">₹{{ formatAmount(extractedData.income.salary) }}</span>
                  </div>
                  <div v-if="extractedData.income.other_income" class="flex justify-between">
                    <span class="text-muted-foreground">Other</span>
                    <span class="font-medium">₹{{ formatAmount(extractedData.income.other_income) }}</span>
                  </div>
                </div>
              </div>

              <!-- Deductions -->
              <div v-if="extractedData.deductions && Object.keys(extractedData.deductions).length">
                <h4 class="text-xs font-semibold text-muted-foreground uppercase mb-2">Deductions</h4>
                <div class="space-y-1 text-sm">
                  <div v-if="extractedData.deductions.section_80c" class="flex justify-between">
                    <span class="text-muted-foreground">80C</span>
                    <span class="font-medium text-blue-600">₹{{ formatAmount(extractedData.deductions.section_80c) }}</span>
                  </div>
                  <div v-if="extractedData.deductions.section_80d" class="flex justify-between">
                    <span class="text-muted-foreground">80D</span>
                    <span class="font-medium text-blue-600">₹{{ formatAmount(extractedData.deductions.section_80d) }}</span>
                  </div>
                  <div v-if="extractedData.deductions.hra_rent" class="flex justify-between">
                    <span class="text-muted-foreground">Monthly Rent</span>
                    <span class="font-medium">₹{{ formatAmount(extractedData.deductions.hra_rent) }}</span>
                  </div>
                </div>
              </div>

              <!-- Empty State -->
              <div v-if="!hasExtractedData" class="text-center py-8 text-muted-foreground">
                <FileSearch class="h-12 w-12 mx-auto mb-3 opacity-50" />
                <p class="text-sm">Answer questions to see extracted data</p>
              </div>
            </CardContent>
          </Card>

          <!-- Live Tracking -->
          <LiveTracking class="h-[200px]" />
        </div>
      </div>
    </div>
  </DynamicLayoutContainer>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { MessageSquare, Bot, User, Send, RotateCcw, ChevronRight, FileText, FileSearch, Download, ClipboardCheck, Check } from 'lucide-vue-next'
import DynamicLayoutContainer from '@/components-vue/dynamic/DynamicLayoutContainer.vue'
import Card from '@/components-vue/ui/Card.vue'
import CardHeader from '@/components-vue/ui/CardHeader.vue'
import CardTitle from '@/components-vue/ui/CardTitle.vue'
import CardContent from '@/components-vue/ui/CardContent.vue'
import Button from '@/components-vue/ui/Button.vue'
import Input from '@/components-vue/ui/Input.vue'
import LiveTracking from '@/components-vue/visualization/LiveTracking.vue'
import { cn } from '@/lib/utils'
import { toast } from '@/stores/toastStore'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

const messages = ref<Message[]>([])
const inputMessage = ref('')
const isLoading = ref(false)
const messagesContainer = ref<HTMLElement | null>(null)
const sessionId = ref(`filing_${Date.now()}`)
const progress = ref(0)
const isComplete = ref(false)
const currentStep = ref('')
const currentCategory = ref('')
const extractedData = ref<Record<string, any>>({})

const categories = computed(() => {
  const cats = [
    { name: 'Personal Info', steps: ['name', 'pan', 'email'], progress: 0 },
    { name: 'Income', steps: ['employer', 'salary', 'other_income'], progress: 0 },
    { name: 'Deductions', steps: ['deduction_80c', 'deduction_80d', 'hra'], progress: 0 },
    { name: 'Tax Regime', steps: ['regime'], progress: 0 },
  ]
  
  // Calculate progress based on extracted data
  const pi = extractedData.value.personal_info || {}
  const inc = extractedData.value.income || {}
  const ded = extractedData.value.deductions || {}
  
  cats[0].progress = ((pi.name ? 1 : 0) + (pi.pan_number ? 1 : 0) + (pi.email ? 1 : 0)) / 3 * 100
  cats[1].progress = ((inc.employer_name ? 1 : 0) + (inc.salary ? 1 : 0) + (inc.other_income !== undefined ? 1 : 0)) / 3 * 100
  cats[2].progress = ((ded.section_80c !== undefined ? 1 : 0) + (ded.section_80d !== undefined ? 1 : 0) + (ded.hra_rent !== undefined ? 1 : 0)) / 3 * 100
  cats[3].progress = extractedData.value.regime ? 100 : 0
  
  return cats
})

const hasExtractedData = computed(() => {
  const pi = extractedData.value.personal_info || {}
  const inc = extractedData.value.income || {}
  return Object.keys(pi).length > 0 || Object.keys(inc).length > 0
})

onMounted(async () => {
  await startFiling()
})

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

const formatAmount = (amount: number): string => {
  if (amount >= 10000000) {
    return `${(amount / 10000000).toFixed(2)} Cr`
  } else if (amount >= 100000) {
    return `${(amount / 100000).toFixed(2)} L`
  }
  return amount.toLocaleString('en-IN')
}

const formatMessage = (content: string): string => {
  // Convert markdown bold to HTML
  return content.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>')
}

const startFiling = async () => {
  try {
    isLoading.value = true
    const response = await fetch(`${API_BASE}/chat/filing/start/${sessionId.value}`)
    const data = await response.json()
    
    messages.value = [{ role: 'assistant', content: data.response }]
    progress.value = data.progress
    isComplete.value = data.is_complete
    currentStep.value = data.current_step
    currentCategory.value = data.current_category
    
    scrollToBottom()
  } catch (error) {
    console.error('Failed to start filing:', error)
    messages.value = [{ role: 'assistant', content: 'Failed to start filing session. Please refresh the page.' }]
  } finally {
    isLoading.value = false
  }
}

const restartFiling = async () => {
  sessionId.value = `filing_${Date.now()}`
  messages.value = []
  extractedData.value = {}
  progress.value = 0
  isComplete.value = false
  await startFiling()
}

const sendMessage = async () => {
  if (!inputMessage.value.trim() || isLoading.value || isComplete.value) return
  
  const userMessage = inputMessage.value.trim()
  messages.value.push({ role: 'user', content: userMessage })
  inputMessage.value = ''
  scrollToBottom()
  
  isLoading.value = true
  
  try {
    const response = await fetch(`${API_BASE}/chat/filing/respond`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: userMessage,
        session_id: sessionId.value
      })
    })
    
    const data = await response.json()
    
    messages.value.push({ role: 'assistant', content: data.response })
    progress.value = data.progress
    isComplete.value = data.is_complete
    currentStep.value = data.current_step
    currentCategory.value = data.current_category
    
    if (data.extracted_data) {
      extractedData.value = data.extracted_data
    }
    
    // Show completion notification
    if (data.is_complete) {
      toast.success(
        'Your tax filing is complete! Click the button below to download your ITR-1 SAHAJ PDF.',
        '🎉 Filing Complete!'
      )
    }
    
    scrollToBottom()
  } catch (error) {
    console.error('Failed to send message:', error)
    messages.value.push({ role: 'assistant', content: 'Sorry, an error occurred. Please try again.' })
  } finally {
    isLoading.value = false
  }
}

const downloadPDF = async () => {
  try {
    toast.info('Generating your ITR-1 SAHAJ PDF...', 'Please wait')
    
    const response = await fetch(`${API_BASE}/chat/filing/generate-pdf/${sessionId.value}`, {
      method: 'POST'
    })
    
    if (!response.ok) {
      throw new Error('PDF generation failed')
    }
    
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `ITR1_SAHAJ_${sessionId.value}.pdf`
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    a.remove()
    
    toast.success(
      'Your ITR-1 SAHAJ tax return has been downloaded successfully!',
      '📄 PDF Downloaded'
    )
    
  } catch (error) {
    console.error('PDF download error:', error)
    toast.error('Failed to generate PDF. Please try again.', 'Download Error')
  }
}
</script>
