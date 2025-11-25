<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  content: string
  size?: 'sm' | 'md' | 'lg' | 'xl'
  class?: string
}>()

const sizeClass = computed(() => {
  switch (props.size) {
    case 'sm': return 'text-sm'
    case 'lg': return 'text-lg font-medium'
    case 'xl': return 'text-xl font-semibold'
    default: return 'text-base'
  }
})
</script>

<template>
  <p :class="[sizeClass, 'text-muted-foreground', props.class]">{{ content }}</p>
</template>
