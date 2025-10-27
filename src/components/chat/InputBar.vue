<template>
  <div class="space-y-3">
    <div v-if="suggestions.length > 0" class="flex flex-wrap gap-2">
      <button
        v-for="suggestion in suggestions"
        :key="suggestion"
        @click="handleSuggestionClick(suggestion)"
        class="text-xs px-3 py-1 rounded-full border border-border hover:bg-accent hover:text-accent-foreground transition-colors"
      >
        {{ suggestion }}
      </button>
    </div>
    
    <div class="flex gap-2">
      <input
        v-model="inputValue"
        type="text"
        placeholder="Ask a tax question..."
        class="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-ring bg-background"
        @keypress.enter="handleSend"
      />
      <button
        @click="handleSend"
        class="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
        :disabled="!inputValue.trim()"
      >
        Send
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { Mode } from '../../stores/chat'

defineProps<{
  suggestions: string[]
  mode: Mode
}>()

const emit = defineEmits<{
  send: [message: string]
}>()

const inputValue = ref('')

function handleSend() {
  if (inputValue.value.trim()) {
    emit('send', inputValue.value)
    inputValue.value = ''
  }
}

function handleSuggestionClick(suggestion: string) {
  emit('send', suggestion)
}
</script>
