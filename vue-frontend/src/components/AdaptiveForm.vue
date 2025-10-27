<template>
  <div class="adaptive-form">
    <h2 class="form-title">Tax Information</h2>
    
    <div class="proficiency-display">
      <span class="label">Mode:</span>
      <span class="value">{{ proficiencyLabel }}</span>
    </div>

    <form @submit.prevent="handleSubmit" class="form-content">
      <!-- Income Field - Always visible -->
      <div class="form-field">
        <label for="income" class="field-label">
          {{ getFieldLabel('income') }}
          <span v-if="isRequired('income')" class="required">*</span>
        </label>
        <input
          id="income"
          v-model.number="formData.income"
          type="number"
          :placeholder="getFieldPlaceholder('income')"
          class="field-input"
          :class="{ 'has-error': errors.income }"
          step="0.01"
          min="0"
        />
        <p v-if="showHelp && getFieldHelp('income')" class="field-help">
          {{ getFieldHelp('income') }}
        </p>
        <p v-if="errors.income" class="field-error">{{ errors.income }}</p>
      </div>

      <!-- Filing Status - Complexity based on proficiency -->
      <div class="form-field">
        <label for="filing_status" class="field-label">
          {{ getFieldLabel('filing_status') }}
          <span v-if="isRequired('filing_status')" class="required">*</span>
        </label>
        <select
          id="filing_status"
          v-model="formData.filing_status"
          class="field-input"
          :class="{ 'has-error': errors.filing_status }"
        >
          <option value="single">{{ getFilingStatusLabel('single') }}</option>
          <option value="married_joint">{{ getFilingStatusLabel('married_joint') }}</option>
          <option v-if="showAdvancedFields" value="married_separate">
            {{ getFilingStatusLabel('married_separate') }}
          </option>
          <option v-if="showAdvancedFields" value="head_of_household">
            {{ getFilingStatusLabel('head_of_household') }}
          </option>
        </select>
        <p v-if="showHelp && getFieldHelp('filing_status')" class="field-help">
          {{ getFieldHelp('filing_status') }}
        </p>
      </div>

      <!-- Dependents -->
      <div class="form-field">
        <label for="dependents" class="field-label">
          {{ getFieldLabel('dependents') }}
        </label>
        <input
          id="dependents"
          v-model.number="formData.dependents"
          type="number"
          :placeholder="getFieldPlaceholder('dependents')"
          class="field-input"
          min="0"
          step="1"
        />
        <p v-if="showHelp && getFieldHelp('dependents')" class="field-help">
          {{ getFieldHelp('dependents') }}
        </p>
      </div>

      <!-- Deductions - Only for intermediate and expert -->
      <div v-if="showAdvancedFields" class="form-field">
        <label for="deductions" class="field-label">
          {{ getFieldLabel('deductions') }}
        </label>
        <input
          id="deductions"
          v-model.number="formData.deductions"
          type="number"
          :placeholder="getFieldPlaceholder('deductions')"
          class="field-input"
          step="0.01"
          min="0"
        />
        <p v-if="showHelp && getFieldHelp('deductions')" class="field-help">
          {{ getFieldHelp('deductions') }}
        </p>
      </div>

      <!-- State - Only for expert -->
      <div v-if="showExpertFields" class="form-field">
        <label for="state" class="field-label">
          {{ getFieldLabel('state') }}
        </label>
        <input
          id="state"
          v-model="formData.state"
          type="text"
          :placeholder="getFieldPlaceholder('state')"
          class="field-input"
          maxlength="2"
        />
        <p v-if="showHelp && getFieldHelp('state')" class="field-help">
          {{ getFieldHelp('state') }}
        </p>
      </div>

      <div class="form-actions">
        <button type="submit" class="btn-primary" :disabled="loading">
          {{ loading ? 'Calculating...' : 'Calculate Tax' }}
        </button>
        <button type="button" @click="handleReset" class="btn-secondary">
          Reset
        </button>
      </div>

      <div v-if="error" class="form-error">
        {{ error }}
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useTaxStore } from '@/stores/tax'
import type { TaxInput, ProficiencyLevel } from '@/types/api'

const taxStore = useTaxStore()
const { proficiencyLevel, loading, error } = storeToRefs(taxStore)

const formData = reactive<TaxInput>({
  income: 0,
  filing_status: 'single',
  dependents: 0,
  deductions: 0,
  state: ''
})

const errors = reactive<Record<string, string>>({})

// Computed properties based on proficiency
const proficiencyLabel = computed(() => {
  const labels: Record<ProficiencyLevel, string> = {
    novice: 'Beginner Mode',
    intermediate: 'Intermediate Mode',
    expert: 'Expert Mode'
  }
  return labels[proficiencyLevel.value]
})

const showAdvancedFields = computed(() => 
  proficiencyLevel.value === 'intermediate' || proficiencyLevel.value === 'expert'
)

const showExpertFields = computed(() => proficiencyLevel.value === 'expert')

const showHelp = computed(() => proficiencyLevel.value === 'novice')

// Field configurations based on proficiency
const fieldConfig = {
  income: {
    novice: {
      label: 'Your Annual Income',
      placeholder: 'e.g., 75000',
      help: 'Enter your total yearly income before taxes'
    },
    intermediate: {
      label: 'Gross Income',
      placeholder: 'Enter gross annual income',
      help: 'Your total income from all sources'
    },
    expert: {
      label: 'AGI (Adjusted Gross Income)',
      placeholder: 'Enter AGI',
      help: 'Total income after above-the-line deductions'
    }
  },
  filing_status: {
    novice: {
      label: 'Are you single or married?',
      help: 'Choose your relationship status for tax purposes'
    },
    intermediate: {
      label: 'Filing Status',
      help: 'Select the filing status that applies to you'
    },
    expert: {
      label: 'Tax Filing Status',
      help: 'IRS filing status classification'
    }
  },
  dependents: {
    novice: {
      label: 'Number of Children/Dependents',
      placeholder: '0',
      help: 'How many children or people depend on you financially?'
    },
    intermediate: {
      label: 'Dependents',
      placeholder: 'Number of dependents',
      help: 'Qualifying dependents for tax credits'
    },
    expert: {
      label: 'Qualifying Dependents',
      placeholder: 'Count',
      help: 'Dependents meeting IRS criteria'
    }
  },
  deductions: {
    intermediate: {
      label: 'Additional Deductions',
      placeholder: '0',
      help: 'Itemized deductions (if more than standard deduction)'
    },
    expert: {
      label: 'Itemized Deductions',
      placeholder: 'Total Schedule A',
      help: 'Total from Schedule A (SALT, mortgage interest, etc.)'
    }
  },
  state: {
    expert: {
      label: 'State',
      placeholder: 'CA',
      help: 'State code for state tax considerations'
    }
  }
}

function getFieldLabel(field: string): string {
  const config = fieldConfig[field as keyof typeof fieldConfig]
  if (!config) return field
  return config[proficiencyLevel.value as keyof typeof config]?.label || field
}

function getFieldPlaceholder(field: string): string {
  const config = fieldConfig[field as keyof typeof fieldConfig]
  if (!config) return ''
  return config[proficiencyLevel.value as keyof typeof config]?.placeholder || ''
}

function getFieldHelp(field: string): string {
  const config = fieldConfig[field as keyof typeof fieldConfig]
  if (!config) return ''
  return config[proficiencyLevel.value as keyof typeof config]?.help || ''
}

function getFilingStatusLabel(status: string): string {
  const labels: Record<string, Record<ProficiencyLevel, string>> = {
    single: {
      novice: 'Single',
      intermediate: 'Single',
      expert: 'Single'
    },
    married_joint: {
      novice: 'Married',
      intermediate: 'Married Filing Jointly',
      expert: 'MFJ'
    },
    married_separate: {
      novice: 'Married (Separate)',
      intermediate: 'Married Filing Separately',
      expert: 'MFS'
    },
    head_of_household: {
      novice: 'Head of Household',
      intermediate: 'Head of Household',
      expert: 'HOH'
    }
  }
  return labels[status]?.[proficiencyLevel.value] || status
}

function isRequired(field: string): boolean {
  return field === 'income' || field === 'filing_status'
}

function validateForm(): boolean {
  Object.keys(errors).forEach(key => delete errors[key])
  
  if (!formData.income || formData.income <= 0) {
    errors.income = 'Income is required and must be greater than 0'
    return false
  }
  
  if (!formData.filing_status) {
    errors.filing_status = 'Please select a filing status'
    return false
  }
  
  return true
}

async function handleSubmit() {
  if (!validateForm()) return
  
  taxStore.updateTaxInput(formData)
  await taxStore.calculateTax()
}

function handleReset() {
  formData.income = 0
  formData.filing_status = 'single'
  formData.dependents = 0
  formData.deductions = 0
  formData.state = ''
  Object.keys(errors).forEach(key => delete errors[key])
  taxStore.resetTaxInput()
}

// Watch for proficiency changes and adjust form
watch(proficiencyLevel, () => {
  // Clear advanced fields when switching to novice
  if (proficiencyLevel.value === 'novice') {
    formData.deductions = 0
    formData.state = ''
  }
})
</script>

<style scoped>
.adaptive-form {
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.form-title {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 16px;
  color: #1a202c;
}

.proficiency-display {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 24px;
  padding: 8px 12px;
  background: #f7fafc;
  border-radius: 4px;
  font-size: 14px;
}

.proficiency-display .label {
  font-weight: 600;
  color: #4a5568;
}

.proficiency-display .value {
  color: #2d3748;
}

.form-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field-label {
  font-size: 14px;
  font-weight: 500;
  color: #2d3748;
}

.required {
  color: #e53e3e;
}

.field-input {
  padding: 10px 12px;
  border: 1px solid #cbd5e0;
  border-radius: 4px;
  font-size: 16px;
  transition: border-color 0.2s;
}

.field-input:focus {
  outline: none;
  border-color: #4299e1;
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.1);
}

.field-input.has-error {
  border-color: #e53e3e;
}

.field-help {
  font-size: 12px;
  color: #718096;
  margin: 0;
}

.field-error {
  font-size: 12px;
  color: #e53e3e;
  margin: 0;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 8px;
}

.btn-primary,
.btn-secondary {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #4299e1;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #3182ce;
}

.btn-primary:disabled {
  background: #a0aec0;
  cursor: not-allowed;
}

.btn-secondary {
  background: #edf2f7;
  color: #2d3748;
}

.btn-secondary:hover {
  background: #e2e8f0;
}

.form-error {
  padding: 12px;
  background: #fff5f5;
  border: 1px solid #feb2b2;
  border-radius: 4px;
  color: #c53030;
  font-size: 14px;
}
</style>
