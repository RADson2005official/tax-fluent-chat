<template>
  <div class="space-y-2">
    <label :for="id" class="block text-sm font-medium">
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>
    
    <input
      :id="id"
      v-model="modelValue"
      :type="type"
      :placeholder="placeholder"
      :required="required"
      class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-ring bg-background"
    />
    
    <p v-if="help" class="text-xs text-muted-foreground">
      {{ help }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
  id: string
  label: string
  type?: string
  placeholder?: string
  required?: boolean
  help?: string
}>()

const modelValue = ref('')
</script>
