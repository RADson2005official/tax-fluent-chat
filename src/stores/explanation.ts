import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface Explanation {
  title: string
  content: string
  key_points: string[]
  expertise_level: string
  related_topics: string[]
}

export const useExplanationStore = defineStore('explanation', () => {
  const currentExplanation = ref<Explanation | null>(null)
  const isOpen = ref(false)
  const isLoading = ref(false)
  
  const API_URL = 'http://localhost:8000'
  
  async function fetchExplanation(topic: string, expertiseLevel: 'novice' | 'expert' = 'novice') {
    isLoading.value = true
    
    try {
      const response = await fetch(`${API_URL}/explain`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          topic,
          context: {},
          expertise_level: expertiseLevel,
        }),
      })
      
      if (!response.ok) {
        throw new Error('Failed to fetch explanation')
      }
      
      const explanation = await response.json()
      currentExplanation.value = explanation
      isOpen.value = true
      
      return explanation
    } catch (error) {
      console.error('Explanation error:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }
  
  function showExplanation(content: string) {
    currentExplanation.value = {
      title: 'Explanation',
      content,
      key_points: [],
      expertise_level: 'novice',
      related_topics: [],
    }
    isOpen.value = true
  }
  
  function closeExplanation() {
    isOpen.value = false
  }
  
  return {
    currentExplanation,
    isOpen,
    isLoading,
    fetchExplanation,
    showExplanation,
    closeExplanation,
  }
})
