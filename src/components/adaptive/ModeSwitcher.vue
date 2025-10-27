<template>
  <div class="flex items-center gap-2">
    <label class="text-sm font-medium">Mode:</label>
    <select
      :value="mode"
      @change="handleChange"
      class="px-3 py-1 border rounded-lg text-sm bg-background focus:outline-none focus:ring-2 focus:ring-ring"
    >
      <option value="Novice">Novice</option>
      <option value="Expert">Expert</option>
      <option value="Accessible">Accessible</option>
    </select>
  </div>
</template>

<script setup lang="ts">
import type { Mode } from '../../stores/chat'

defineProps<{
  mode: Mode
}>()

const emit = defineEmits<{
  change: [mode: Mode]
}>()

function handleChange(event: Event) {
  const target = event.target as HTMLSelectElement
  emit('change', target.value as Mode)
}
</script>
