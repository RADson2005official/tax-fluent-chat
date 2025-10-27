<template>
  <div
    class="p-4 rounded-lg"
    :class="message.role === 'user' ? 'bg-primary text-primary-foreground ml-8' : 'bg-muted mr-8'"
  >
    <div class="flex justify-between items-start gap-2">
      <p class="text-sm">{{ message.content }}</p>
      <button
        v-if="message.explainable"
        @click="$emit('explain', message.id)"
        class="text-xs px-2 py-1 rounded bg-background/10 hover:bg-background/20 transition-colors whitespace-nowrap"
      >
        Explain
      </button>
    </div>
    <div v-if="message.timestamp" class="text-xs opacity-70 mt-2">
      {{ formatTime(message.timestamp) }}
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ChatMessage } from '../../stores/chat'

defineProps<{
  message: ChatMessage
}>()

defineEmits<{
  explain: [id: string]
}>()

function formatTime(date: Date) {
  return new Date(date).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
  })
}
</script>
