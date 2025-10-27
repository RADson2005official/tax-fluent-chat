<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h2 class="header-title">Tax Calculation Dashboard</h2>
      <button
        v-if="taxResult"
        @click="handleExplain"
        class="explain-button"
      >
        📖 Explain Results
      </button>
    </div>

    <div v-if="!taxResult" class="empty-state">
      <div class="empty-icon">📊</div>
      <h3 class="empty-title">No Tax Calculation Yet</h3>
      <p class="empty-description">
        Fill out the form and click "Calculate Tax" to see your results here.
      </p>
    </div>

    <div v-else class="results-container">
      <!-- Main Tax Summary Card -->
      <div class="summary-card main-summary">
        <h3 class="card-title">Federal Tax Summary</h3>
        
        <div class="main-result">
          <div class="result-label">Total Federal Tax</div>
          <div class="result-value primary">
            {{ formatCurrency(taxResult.federal_tax) }}
          </div>
        </div>

        <div class="result-grid">
          <div class="result-item">
            <span class="item-label">Gross Income</span>
            <span class="item-value">{{ formatCurrency(taxResult.gross_income) }}</span>
          </div>
          <div class="result-item">
            <span class="item-label">Taxable Income</span>
            <span class="item-value">{{ formatCurrency(taxResult.taxable_income) }}</span>
          </div>
        </div>
      </div>

      <!-- Rates Card -->
      <div class="summary-card rates-card">
        <h3 class="card-title">Tax Rates</h3>
        
        <div class="rate-item">
          <div class="rate-info">
            <span class="rate-label">Effective Rate</span>
            <span class="rate-description">
              {{ getEffectiveRateDescription() }}
            </span>
          </div>
          <div class="rate-value effective">
            {{ formatPercent(taxResult.effective_rate) }}
          </div>
        </div>

        <div class="rate-item">
          <div class="rate-info">
            <span class="rate-label">Marginal Rate</span>
            <span class="rate-description">
              {{ getMarginalRateDescription() }}
            </span>
          </div>
          <div class="rate-value marginal">
            {{ formatPercent(taxResult.marginal_rate) }}
          </div>
        </div>

        <div class="bracket-info">
          <span class="bracket-label">Tax Bracket:</span>
          <span class="bracket-value">{{ taxResult.tax_bracket }}</span>
        </div>
      </div>

      <!-- Deductions Card -->
      <div class="summary-card deductions-card">
        <h3 class="card-title">Deductions</h3>
        
        <div class="deduction-item">
          <span class="deduction-label">Standard Deduction</span>
          <span class="deduction-value">
            {{ formatCurrency(taxResult.standard_deduction) }}
          </span>
        </div>

        <div class="deduction-item">
          <span class="deduction-label">Total Deductions Applied</span>
          <span class="deduction-value highlight">
            {{ formatCurrency(taxResult.total_deductions) }}
          </span>
        </div>

        <div v-if="isItemized" class="deduction-note">
          ✓ Using itemized deductions
        </div>
        <div v-else class="deduction-note">
          ✓ Using standard deduction
        </div>
      </div>

      <!-- Breakdown Visualization -->
      <div class="summary-card breakdown-card">
        <h3 class="card-title">Income Breakdown</h3>
        
        <div class="breakdown-bar">
          <div 
            class="bar-segment tax-segment"
            :style="{ width: taxPercentage + '%' }"
          >
            <span v-if="taxPercentage > 10" class="segment-label">
              Tax: {{ formatPercent(taxResult.effective_rate) }}
            </span>
          </div>
          <div 
            class="bar-segment income-segment"
            :style="{ width: incomePercentage + '%' }"
          >
            <span v-if="incomePercentage > 10" class="segment-label">
              After Tax: {{ formatPercent(100 - taxResult.effective_rate) }}
            </span>
          </div>
        </div>

        <div class="breakdown-legend">
          <div class="legend-item">
            <span class="legend-color tax-color"></span>
            <span>Federal Tax: {{ formatCurrency(taxResult.federal_tax) }}</span>
          </div>
          <div class="legend-item">
            <span class="legend-color income-color"></span>
            <span>Take-Home: {{ formatCurrency(taxResult.gross_income - taxResult.federal_tax) }}</span>
          </div>
        </div>
      </div>

      <!-- Detailed Explanation -->
      <div class="summary-card explanation-card">
        <h3 class="card-title">How We Calculated This</h3>
        <p class="explanation-text">{{ taxResult.explanation }}</p>
      </div>

      <!-- Quick Actions -->
      <div class="actions-card">
        <button @click="handlePrint" class="action-button">
          🖨️ Print Summary
        </button>
        <button @click="handleDownload" class="action-button">
          💾 Download PDF
        </button>
        <button @click="handleShare" class="action-button">
          📤 Share Results
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useTaxStore } from '@/stores/tax'

const emit = defineEmits<{
  explainResults: []
}>()

const taxStore = useTaxStore()
const { taxResult, proficiencyLevel } = storeToRefs(taxStore)

const isItemized = computed(() => {
  if (!taxResult.value) return false
  return taxResult.value.total_deductions > taxResult.value.standard_deduction
})

const taxPercentage = computed(() => {
  if (!taxResult.value) return 0
  return taxResult.value.effective_rate
})

const incomePercentage = computed(() => {
  if (!taxResult.value) return 100
  return 100 - taxResult.value.effective_rate
})

function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount)
}

function formatPercent(value: number): string {
  return `${value.toFixed(2)}%`
}

function getEffectiveRateDescription(): string {
  const descriptions = {
    novice: 'Overall percentage of income paid in taxes',
    intermediate: 'Total tax divided by gross income',
    expert: 'Effective marginal rate including phase-outs'
  }
  return descriptions[proficiencyLevel.value] || descriptions.novice
}

function getMarginalRateDescription(): string {
  const descriptions = {
    novice: 'Tax rate on your next dollar earned',
    intermediate: 'Highest tax bracket reached',
    expert: 'Statutory marginal rate (top bracket)'
  }
  return descriptions[proficiencyLevel.value] || descriptions.novice
}

function handleExplain() {
  emit('explainResults')
}

function handlePrint() {
  window.print()
}

function handleDownload() {
  // Placeholder for PDF download functionality
  alert('PDF download feature coming soon!')
}

function handleShare() {
  // Placeholder for share functionality
  alert('Share feature coming soon!')
}
</script>

<style scoped>
.dashboard {
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-title {
  font-size: 24px;
  font-weight: 600;
  color: #1a202c;
  margin: 0;
}

.explain-button {
  padding: 8px 16px;
  background: #4299e1;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.explain-button:hover {
  background: #3182ce;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-title {
  font-size: 20px;
  font-weight: 600;
  color: #2d3748;
  margin: 0 0 8px 0;
}

.empty-description {
  font-size: 14px;
  color: #718096;
  margin: 0;
}

.results-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.summary-card {
  background: #f7fafc;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #e2e8f0;
}

.main-summary {
  grid-column: 1 / -1;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 16px 0;
  color: inherit;
}

.main-result {
  text-align: center;
  margin-bottom: 24px;
}

.result-label {
  font-size: 14px;
  opacity: 0.9;
  margin-bottom: 8px;
}

.result-value {
  font-size: 48px;
  font-weight: 700;
}

.result-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.result-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  text-align: center;
  padding: 12px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}

.item-label {
  font-size: 12px;
  opacity: 0.9;
}

.item-value {
  font-size: 20px;
  font-weight: 600;
}

.rates-card .card-title,
.deductions-card .card-title,
.breakdown-card .card-title,
.explanation-card .card-title {
  color: #2d3748;
}

.rate-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid #e2e8f0;
}

.rate-item:last-of-type {
  border-bottom: none;
}

.rate-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.rate-label {
  font-size: 16px;
  font-weight: 600;
  color: #2d3748;
}

.rate-description {
  font-size: 12px;
  color: #718096;
}

.rate-value {
  font-size: 28px;
  font-weight: 700;
}

.rate-value.effective {
  color: #48bb78;
}

.rate-value.marginal {
  color: #ed8936;
}

.bracket-info {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  font-size: 14px;
}

.bracket-label {
  color: #718096;
}

.bracket-value {
  font-weight: 600;
  color: #2d3748;
}

.deduction-item {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #e2e8f0;
}

.deduction-label {
  color: #4a5568;
  font-size: 14px;
}

.deduction-value {
  font-weight: 600;
  color: #2d3748;
}

.deduction-value.highlight {
  color: #4299e1;
  font-size: 18px;
}

.deduction-note {
  margin-top: 12px;
  padding: 8px 12px;
  background: #c6f6d5;
  color: #22543d;
  border-radius: 4px;
  font-size: 13px;
}

.breakdown-bar {
  display: flex;
  height: 60px;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 16px;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
}

.bar-segment {
  display: flex;
  align-items: center;
  justify-content: center;
  transition: width 0.3s ease;
}

.tax-segment {
  background: #fc8181;
}

.income-segment {
  background: #68d391;
}

.segment-label {
  font-size: 12px;
  font-weight: 600;
  color: white;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.breakdown-legend {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #4a5568;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 2px;
}

.tax-color {
  background: #fc8181;
}

.income-color {
  background: #68d391;
}

.explanation-text {
  font-size: 14px;
  line-height: 1.6;
  color: #4a5568;
  margin: 0;
}

.actions-card {
  grid-column: 1 / -1;
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.action-button {
  flex: 1;
  min-width: 150px;
  padding: 12px 20px;
  background: white;
  border: 2px solid #cbd5e0;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  color: #4a5568;
  cursor: pointer;
  transition: all 0.2s;
}

.action-button:hover {
  border-color: #4299e1;
  color: #2d3748;
  background: #f7fafc;
}

@media print {
  .explain-button,
  .actions-card {
    display: none;
  }
}
</style>
