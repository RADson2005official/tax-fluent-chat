import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface ChatMessage {
  id: string
  role: 'user' | 'ai'
  content: string
  explainable?: boolean
  timestamp?: Date
}

export type Mode = 'Novice' | 'Expert' | 'Accessible'

export const useChatStore = defineStore('chat', () => {
  const messages = ref<ChatMessage[]>([
    {
      id: 'm1',
      role: 'ai',
      content: "Hi! I'm your tax assistant. How can I help today?",
      explainable: false,
      timestamp: new Date(),
    },
  ])
  
  const mode = ref<Mode>('Novice')
  const isLoading = ref(false)
  
  const API_URL = 'http://localhost:8000'
  
  const suggestions = computed(() => {
    if (mode.value === 'Novice') {
      return [
        'Do I qualify for the child tax credit?',
        'Should I itemize deductions?',
        'How do I report freelance income?',
      ]
    } else if (mode.value === 'Expert') {
      return [
        'compute agi from w2 + 1099',
        'simulate standard vs itemized',
        'calc ctc 2 dependents',
      ]
    } else {
      return [
        'Explain EITC in simple terms',
        'Help me fill income',
        'Show larger text',
      ]
    }
  })
  
  function addMessage(message: ChatMessage) {
    messages.value.push(message)
  }
  
  async function sendMessage(content: string) {
    const id = `${Date.now()}`
    
    // Add user message
    addMessage({
      id: id + 'u',
      role: 'user',
      content,
      timestamp: new Date(),
    })
    
    isLoading.value = true
    
    try {
      // Simulate AI response (replace with actual API call)
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      addMessage({
        id: id + 'a',
        role: 'ai',
        content: 'Thanks! Here\'s a quick take. You may benefit from the standard deduction. Do you want me to check credit eligibility?',
        explainable: true,
        timestamp: new Date(),
      })
    } finally {
      isLoading.value = false
    }
  }
  
  function setMode(newMode: Mode) {
    mode.value = newMode
  }
  
  function clearMessages() {
    messages.value = [messages.value[0]] // Keep welcome message
  }
  
  return {
    messages,
    mode,
    isLoading,
    suggestions,
    addMessage,
    sendMessage,
    setMode,
    clearMessages,
  }
})
