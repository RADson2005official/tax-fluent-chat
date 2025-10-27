<template>
  <div class="home-view">
    <header class="app-header">
      <div class="header-content">
        <h1 class="app-title">Tax Fluent Chat</h1>
        <div class="header-actions">
          <ProficiencySwitcher v-model="currentProficiency" />
          <button @click="handleLogout" class="logout-button">
            Logout
          </button>
        </div>
      </div>
    </header>

    <main class="main-content">
      <div class="content-grid">
        <div class="form-section">
          <AdaptiveForm />
        </div>

        <div class="dashboard-section">
          <Dashboard @explain-results="openExplanation" />
        </div>
      </div>
    </main>

    <ExplanationPanel
      :is-open="showExplanation"
      :query="explanationQuery"
      :title="explanationTitle"
      :context="explanationContext"
      @close="closeExplanation"
      @query-change="handleQueryChange"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useAuthStore } from '@/stores/auth'
import { useTaxStore } from '@/stores/tax'
import AdaptiveForm from '@/components/AdaptiveForm.vue'
import Dashboard from '@/components/Dashboard.vue'
import ExplanationPanel from '@/components/ExplanationPanel.vue'
import ProficiencySwitcher from '@/components/ProficiencySwitcher.vue'

const router = useRouter()
const authStore = useAuthStore()
const taxStore = useTaxStore()

const { proficiencyLevel, taxResult } = storeToRefs(taxStore)

const currentProficiency = ref(proficiencyLevel.value)
const showExplanation = ref(false)
const explanationQuery = ref('')
const explanationTitle = ref('Explanation')
const explanationContext = ref({})

// Watch for proficiency changes and update store
watch(currentProficiency, (newValue) => {
  taxStore.setProficiency(newValue)
})

function openExplanation() {
  if (taxResult.value) {
    explanationQuery.value = 'tax calculation results'
    explanationTitle.value = 'Understanding Your Tax Calculation'
    explanationContext.value = taxResult.value
    showExplanation.value = true
  }
}

function closeExplanation() {
  showExplanation.value = false
}

function handleQueryChange(query: string) {
  explanationQuery.value = query
}

function handleLogout() {
  authStore.logout()
  router.push('/auth')
}
</script>

<style scoped>
.home-view {
  min-height: 100vh;
  background: #f7fafc;
}

.app-header {
  background: white;
  border-bottom: 1px solid #e2e8f0;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 16px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.app-title {
  font-size: 24px;
  font-weight: 700;
  color: #1a202c;
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.logout-button {
  padding: 8px 16px;
  background: #edf2f7;
  color: #2d3748;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.logout-button:hover {
  background: #e2e8f0;
}

.main-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 32px 24px;
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

@media (max-width: 1024px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
  
  .header-content {
    flex-direction: column;
    gap: 16px;
  }
}
</style>
