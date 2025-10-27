<template>
  <div class="proficiency-switcher">
    <label class="switcher-label">Proficiency Level:</label>
    <div class="switcher-buttons">
      <button
        v-for="level in levels"
        :key="level.value"
        class="level-button"
        :class="{ active: modelValue === level.value }"
        @click="handleChange(level.value)"
      >
        <span class="level-icon">{{ level.icon }}</span>
        <span class="level-name">{{ level.label }}</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ProficiencyLevel } from '@/types/api'

interface Props {
  modelValue: ProficiencyLevel
}

defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: ProficiencyLevel]
}>()

const levels = [
  { value: 'novice' as ProficiencyLevel, label: 'Beginner', icon: '🌱' },
  { value: 'intermediate' as ProficiencyLevel, label: 'Intermediate', icon: '🌿' },
  { value: 'expert' as ProficiencyLevel, label: 'Expert', icon: '🌳' }
]

function handleChange(level: ProficiencyLevel) {
  emit('update:modelValue', level)
}
</script>

<style scoped>
.proficiency-switcher {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.switcher-label {
  font-size: 14px;
  font-weight: 500;
  color: #4a5568;
}

.switcher-buttons {
  display: flex;
  gap: 8px;
  background: #f7fafc;
  padding: 4px;
  border-radius: 8px;
}

.level-button {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 12px;
  background: transparent;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
  color: #4a5568;
}

.level-button:hover {
  background: rgba(66, 153, 225, 0.1);
}

.level-button.active {
  background: #4299e1;
  color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.level-icon {
  font-size: 16px;
}

.level-name {
  font-weight: 500;
}

@media (max-width: 640px) {
  .level-name {
    display: none;
  }
  
  .level-icon {
    font-size: 20px;
  }
}
</style>
