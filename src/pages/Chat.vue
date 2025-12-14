<template>
  <DynamicLayoutContainer>
    <div class="max-w-7xl mx-auto h-[calc(100vh-8rem)]">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full">
        <!-- Chat Area -->
        <div class="lg:col-span-2 flex flex-col h-full">
          <!-- Chat Header -->
          <div class="flex justify-between items-center mb-4">
            <div class="space-y-1">
              <h1 class="text-2xl font-bold flex items-center gap-2">
                <Sparkles class="h-6 w-6 text-primary" />
                Tax Expert AI
              </h1>
              <p class="text-muted-foreground">Powered by LLaMA 3.2 Fine-tuned Model</p>
            </div>
            <div class="flex gap-2">
              <Button variant="outline" size="sm" @click="clearChat" :disabled="isTyping">
                <Trash2 class="mr-2 h-4 w-4" />
                Clear
              </Button>
              <Button variant="outline" @click="router.push('/dashboard')">
                <ArrowLeft class="mr-2 h-4 w-4" />
                Back
              </Button>
            </div>
          </div>

          <!-- Chat Container -->
          <Card class="flex-1 flex flex-col overflow-hidden">
            <!-- Messages Area -->
            <div ref="messagesContainer" class="flex-1 overflow-y-auto p-6 space-y-4">
              <!-- Welcome Message -->
              <div v-if="messages.length === 0" class="text-center py-12">
                <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-br from-primary/20 to-purple-500/20 mb-4">
                  <Bot class="h-8 w-8 text-primary" />
                </div>
                <h3 class="text-lg font-semibold mb-2">Welcome to Tax Expert AI!</h3>
                <p class="text-muted-foreground mb-6">I'm your AI-powered Chartered Accountant. Tell me about your income and I'll help you file your taxes.</p>
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
              <form @submit.prevent="handleSubmit" class="flex gap-3">
                <Input 
                  v-model="inputMessage" 
                  placeholder="Tell me about your income, deductions, investments..."
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

        <!-- Extracted Data Sidebar -->
        <div class="hidden lg:flex flex-col gap-4 h-full overflow-hidden">
          <!-- Connection Status -->
          <Card class="p-3">
            <div class="flex items-center justify-between">
              <span class="text-sm font-medium">Model Status</span>
              <div class="flex items-center gap-2">
                <div :class="cn('w-2 h-2 rounded-full', modelLoaded ? 'bg-green-500' : 'bg-yellow-500 animate-pulse')"></div>
                <span class="text-xs text-muted-foreground">{{ modelLoaded ? 'Ready' : 'Loading...' }}</span>
              </div>
            </div>
          </Card>

          <!-- Extracted Tax Data -->
          <Card class="flex-1 flex flex-col overflow-hidden">
            <CardHeader class="pb-2 border-b">
              <div class="flex items-center justify-between">
                <CardTitle class="text-sm font-medium flex items-center gap-2">
                  <FileText class="h-4 w-4" />
                  Extracted Tax Data
                </CardTitle>
                <span v-if="extractedData" class="text-xs px-2 py-1 rounded-full bg-primary/10 text-primary">
                  {{ Math.round((extractedData.extraction_confidence || 0) * 100) }}% Complete
                </span>
              </div>
            </CardHeader>
            <CardContent class="flex-1 overflow-y-auto p-4 space-y-4">
              <!-- No Data Yet -->
              <div v-if="!extractedData" class="text-center py-8 text-muted-foreground">
                <FileSearch class="h-12 w-12 mx-auto mb-3 opacity-50" />
                <p class="text-sm">Start chatting to extract tax data</p>
              </div>
              
              <!-- Extracted Data Display -->
              <div v-else class="space-y-4">
                <!-- Personal Info -->
                <div v-if="extractedData.personal_info?.name || extractedData.personal_info?.pan_number">
                  <h4 class="text-xs font-semibold text-muted-foreground uppercase mb-2">Personal Info</h4>
                  <div class="space-y-1 text-sm">
                    <div v-if="extractedData.personal_info?.name" class="flex justify-between">
                      <span class="text-muted-foreground">Name</span>
                      <span class="font-medium">{{ extractedData.personal_info.name }}</span>
                    </div>
                    <div v-if="extractedData.personal_info?.pan_number" class="flex justify-between">
                      <span class="text-muted-foreground">PAN</span>
                      <span class="font-medium font-mono">{{ extractedData.personal_info.pan_number }}</span>
                    </div>
                  </div>
                </div>

                <!-- Income Sources -->
                <div v-if="extractedData.income_sources?.length > 0">
                  <h4 class="text-xs font-semibold text-muted-foreground uppercase mb-2">Income Sources</h4>
                  <div class="space-y-2">
                    <div v-for="(income, idx) in extractedData.income_sources" :key="idx" 
                         class="p-2 rounded bg-green-500/10 border border-green-500/20">
                      <div class="flex justify-between items-center">
                        <span class="text-sm capitalize">{{ income.source_type }}</span>
                        <span class="font-semibold text-green-600">₹{{ formatAmount(income.amount) }}</span>
                      </div>
                      <div v-if="income.employer_name" class="text-xs text-muted-foreground">
                        {{ income.employer_name }}
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Deductions -->
                <div v-if="extractedData.deductions?.length > 0">
                  <h4 class="text-xs font-semibold text-muted-foreground uppercase mb-2">Deductions</h4>
                  <div class="space-y-2">
                    <div v-for="(ded, idx) in extractedData.deductions" :key="idx" 
                         class="p-2 rounded bg-blue-500/10 border border-blue-500/20">
                      <div class="flex justify-between items-center">
                        <span class="text-sm">Section {{ ded.section }}</span>
                        <span class="font-semibold text-blue-600">₹{{ formatAmount(ded.amount) }}</span>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Tax Summary -->
                <div v-if="extractedData.total_income > 0" class="pt-4 border-t">
                  <h4 class="text-xs font-semibold text-muted-foreground uppercase mb-2">Tax Summary</h4>
                  <div class="space-y-2 text-sm">
                    <div class="flex justify-between">
                      <span class="text-muted-foreground">Total Income</span>
                      <span class="font-medium">₹{{ formatAmount(extractedData.total_income) }}</span>
                    </div>
                    <div class="flex justify-between">
                      <span class="text-muted-foreground">Deductions</span>
                      <span class="font-medium text-green-600">-₹{{ formatAmount(extractedData.total_deductions) }}</span>
                    </div>
                    <div class="flex justify-between">
                      <span class="text-muted-foreground">Taxable Income</span>
                      <span class="font-medium">₹{{ formatAmount(extractedData.taxable_income) }}</span>
                    </div>
                    <div class="flex justify-between pt-2 border-t">
                      <span class="font-semibold">Estimated Tax</span>
                      <span class="font-bold text-primary">₹{{ formatAmount(extractedData.estimated_tax) }}</span>
                    </div>
                  </div>
                </div>

                <!-- Missing Fields Warning -->
                <div v-if="extractedData.missing_fields?.length > 0" class="p-3 rounded bg-yellow-500/10 border border-yellow-500/20">
                  <div class="flex items-start gap-2">
                    <AlertCircle class="h-4 w-4 text-yellow-600 mt-0.5" />
                    <div>
                      <p class="text-sm font-medium text-yellow-600">Missing Information</p>
                      <p class="text-xs text-muted-foreground">{{ extractedData.missing_fields.join(', ') }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
            
            <!-- Generate PDF Button -->
            <div class="p-4 border-t">
              <Button 
                class="w-full" 
                :disabled="!extractedData || (extractedData.extraction_confidence || 0) < 0.3"
                @click="downloadPDF"
              >
                <Download class="mr-2 h-4 w-4" />
                Generate Tax Return PDF
              </Button>
            </div>
          </Card>
        </div>
      </div>
    </div>
  </DynamicLayoutContainer>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, Bot, User, Send, Sparkles, Trash2, FileText, FileSearch, Download, AlertCircle } from 'lucide-vue-next'
import DynamicLayoutContainer from '@/components-vue/dynamic/DynamicLayoutContainer.vue'
import CardTitle from '@/components-vue/ui/CardTitle.vue'
import CardContent from '@/components-vue/ui/CardContent.vue'
import CardHeader from '@/components-vue/ui/CardHeader.vue'
import Button from '@/components-vue/ui/Button.vue'
import Input from '@/components-vue/ui/Input.vue'
import { cn } from '@/lib/utils'

const router = useRouter()

// API Base URL
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

interface ExtractedData {
  personal_info?: {
    name?: string
    pan_number?: string
    email?: string
  }
  income_sources?: Array<{
    source_type: string
    employer_name?: string
    amount: number
  }>
  deductions?: Array<{
    section: string
    amount: number
  }>
  total_income: number
  total_deductions: number
  taxable_income: number
  estimated_tax: number
  extraction_confidence: number
  missing_fields?: string[]
}

const messages = ref<Message[]>([])
const inputMessage = ref('')
const isTyping = ref(false)
const messagesContainer = ref<HTMLElement | null>(null)
const extractedData = ref<ExtractedData | null>(null)
const modelLoaded = ref(false)
const sessionId = ref(`session_${Date.now()}`)

const suggestions = [
  "I earn ₹8 lakh salary from TCS",
  "My annual income is ₹5 lakh",
  "I have ₹1.5 lakh in PPF and ELSS",
  "Help me understand tax deductions"
]

// Check model status on mount
onMounted(async () => {
  try {
    const response = await fetch(`${API_BASE}/chat/model-status`)
    const data = await response.json()
    modelLoaded.value = data.is_loaded
  } catch (e) {
    console.log('Model status check failed, assuming not loaded')
    // Try to load the model
    try {
      await fetch(`${API_BASE}/chat/load-model`, { method: 'POST' })
      modelLoaded.value = true
    } catch {
      modelLoaded.value = false
    }
  }
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

const sendMessage = async (content: string) => {
  if (!content.trim()) return

  // Add user message
  messages.value.push({ role: 'user', content })
  inputMessage.value = ''
  scrollToBottom()

  // Show typing indicator
  isTyping.value = true
  scrollToBottom()

  try {
    // Call LLaMA API
    const response = await fetch(`${API_BASE}/chat/message`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: content,
        session_id: sessionId.value,
        include_extraction: true
      })
    })

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`)
    }

    const data = await response.json()
    
    // Add assistant response
    messages.value.push({ role: 'assistant', content: data.response })
    
    // Update extracted data
    if (data.extracted_data) {
      extractedData.value = data.extracted_data
    }
    
    modelLoaded.value = true
    
  } catch (error) {
    console.error('Chat error:', error)
    messages.value.push({ 
      role: 'assistant', 
      content: 'Sorry, I encountered an error. Please make sure the backend server is running and the model is loaded.' 
    })
  } finally {
    isTyping.value = false
    scrollToBottom()
  }
}

const handleSubmit = () => {
  sendMessage(inputMessage.value)
}

const clearChat = async () => {
  try {
    await fetch(`${API_BASE}/chat/clear/${sessionId.value}`, { method: 'POST' })
  } catch (e) {
    console.log('Clear session failed')
  }
  messages.value = []
  extractedData.value = null
  sessionId.value = `session_${Date.now()}`
}

const downloadPDF = async () => {
  try {
    const response = await fetch(`${API_BASE}/chat/generate-pdf`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        session_id: sessionId.value
      })
    })

    if (!response.ok) {
      throw new Error('PDF generation failed')
    }

    // Download the PDF
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `tax_return_${sessionId.value}.pdf`
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    a.remove()
    
  } catch (error) {
    console.error('PDF download error:', error)
    alert('Failed to generate PDF. Please try again.')
  }
}
</script>
