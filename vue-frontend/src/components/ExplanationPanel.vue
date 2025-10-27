<template>
  <div v-if="isOpen" class="explanation-overlay" @click.self="close">
    <div class="explanation-panel">
      <div class="panel-header">
        <h3 class="panel-title">{{ title }}</h3>
        <button @click="close" class="close-button" aria-label="Close">
          ✕
        </button>
      </div>

      <div class="panel-content">
        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
          <p>Loading explanation...</p>
        </div>

        <div v-else-if="error" class="error-state">
          <p class="error-message">{{ error }}</p>
          <button @click="retry" class="retry-button">Try Again</button>
        </div>

        <div v-else-if="explanation" class="explanation-content">
          <div class="proficiency-indicator">
            <span class="indicator-label">Explanation Level:</span>
            <span class="indicator-badge" :class="`badge-${currentProficiency}`">
              {{ formatProficiency(currentProficiency) }}
            </span>
          </div>

          <div class="explanation-text">
            {{ explanation.explanation }}
          </div>

          <div v-if="explanation.technical_terms?.length" class="technical-terms">
            <h4 class="section-title">Key Terms</h4>
            <div class="terms-list">
              <span
                v-for="term in explanation.technical_terms"
                :key="term"
                class="term-badge"
                @click="explainTerm(term)"
              >
                {{ term }}
              </span>
            </div>
          </div>

          <div v-if="explanation.related_topics?.length" class="related-topics">
            <h4 class="section-title">Related Topics</h4>
            <div class="topics-list">
              <button
                v-for="topic in explanation.related_topics"
                :key="topic"
                class="topic-button"
                @click="explainTopic(topic)"
              >
                {{ formatTopic(topic) }}
              </button>
            </div>
          </div>
        </div>

        <div v-else class="empty-state">
          <p>No explanation available</p>
        </div>
      </div>

      <div class="panel-footer">
        <div class="proficiency-selector">
          <label class="selector-label">Change explanation level:</label>
          <div class="proficiency-buttons">
            <button
              v-for="level in proficiencyLevels"
              :key="level"
              class="proficiency-button"
              :class="{ active: currentProficiency === level }"
              @click="changeProficiency(level)"
            >
              {{ formatProficiency(level) }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useTaxStore } from '@/stores/tax'
import { explainAPI } from '@/composables/useAPI'
import type { ExplanationResponse, ProficiencyLevel } from '@/types/api'

interface Props {
  isOpen: boolean
  query: string
  title?: string
  context?: Record<string, any>
}

const props = withDefaults(defineProps<Props>(), {
  title: 'Explanation',
  context: () => ({})
})

const emit = defineEmits<{
  close: []
  queryChange: [query: string]
}>()

const taxStore = useTaxStore()
const { proficiencyLevel } = storeToRefs(taxStore)

const loading = ref(false)
const error = ref<string | null>(null)
const explanation = ref<ExplanationResponse | null>(null)
const currentProficiency = ref<ProficiencyLevel>(proficiencyLevel.value)

const proficiencyLevels: ProficiencyLevel[] = ['novice', 'intermediate', 'expert']

// Fetch explanation when panel opens or query changes
watch(() => [props.isOpen, props.query], async ([open, query]) => {
  if (open && query) {
    await fetchExplanation(query as string)
  }
}, { immediate: true })

async function fetchExplanation(query: string) {
  if (!query) return
  
  loading.value = true
  error.value = null
  
  try {
    const result = await explainAPI.getExplanation({
      query,
      proficiency: currentProficiency.value,
      context: props.context
    })
    explanation.value = result
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to load explanation'
  } finally {
    loading.value = false
  }
}

async function changeProficiency(level: ProficiencyLevel) {
  if (level === currentProficiency.value) return
  
  currentProficiency.value = level
  await fetchExplanation(props.query)
}

async function explainTerm(term: string) {
  emit('queryChange', term)
  await fetchExplanation(term)
}

async function explainTopic(topic: string) {
  emit('queryChange', topic)
  await fetchExplanation(topic)
}

function retry() {
  fetchExplanation(props.query)
}

function close() {
  emit('close')
}

function formatProficiency(level: string): string {
  const labels: Record<string, string> = {
    novice: 'Beginner',
    intermediate: 'Intermediate',
    expert: 'Expert'
  }
  return labels[level] || level
}

function formatTopic(topic: string): string {
  return topic.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}
</script>

<style scoped>
.explanation-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.explanation-panel {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  max-width: 700px;
  width: 100%;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e2e8f0;
}

.panel-title {
  font-size: 20px;
  font-weight: 600;
  color: #1a202c;
  margin: 0;
}

.close-button {
  background: none;
  border: none;
  font-size: 24px;
  color: #718096;
  cursor: pointer;
  padding: 4px 8px;
  line-height: 1;
  transition: color 0.2s;
}

.close-button:hover {
  color: #2d3748;
}

.panel-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  gap: 16px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e2e8f0;
  border-top-color: #4299e1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 40px;
}

.error-message {
  color: #e53e3e;
  text-align: center;
}

.retry-button {
  padding: 8px 16px;
  background: #4299e1;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.retry-button:hover {
  background: #3182ce;
}

.explanation-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.proficiency-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
}

.indicator-label {
  font-size: 14px;
  color: #718096;
}

.indicator-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.badge-novice {
  background: #c6f6d5;
  color: #22543d;
}

.badge-intermediate {
  background: #bee3f8;
  color: #2c5282;
}

.badge-expert {
  background: #fbd38d;
  color: #744210;
}

.explanation-text {
  font-size: 16px;
  line-height: 1.6;
  color: #2d3748;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #2d3748;
  margin: 0 0 12px 0;
}

.technical-terms,
.related-topics {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.terms-list,
.topics-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.term-badge {
  padding: 6px 12px;
  background: #edf2f7;
  border-radius: 4px;
  font-size: 14px;
  color: #4a5568;
  cursor: pointer;
  transition: all 0.2s;
}

.term-badge:hover {
  background: #e2e8f0;
  color: #2d3748;
}

.topic-button {
  padding: 8px 16px;
  background: white;
  border: 1px solid #cbd5e0;
  border-radius: 4px;
  font-size: 14px;
  color: #4a5568;
  cursor: pointer;
  transition: all 0.2s;
}

.topic-button:hover {
  background: #f7fafc;
  border-color: #4299e1;
  color: #2d3748;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #718096;
}

.panel-footer {
  padding: 20px 24px;
  border-top: 1px solid #e2e8f0;
  background: #f7fafc;
  border-radius: 0 0 12px 12px;
}

.proficiency-selector {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.selector-label {
  font-size: 14px;
  color: #4a5568;
  font-weight: 500;
}

.proficiency-buttons {
  display: flex;
  gap: 8px;
}

.proficiency-button {
  flex: 1;
  padding: 8px 16px;
  background: white;
  border: 2px solid #cbd5e0;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  color: #4a5568;
  cursor: pointer;
  transition: all 0.2s;
}

.proficiency-button:hover {
  border-color: #4299e1;
  color: #2d3748;
}

.proficiency-button.active {
  background: #4299e1;
  border-color: #4299e1;
  color: white;
}
</style>
