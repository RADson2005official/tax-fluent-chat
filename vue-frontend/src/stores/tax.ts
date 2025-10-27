import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { TaxInput, TaxResult, ProficiencyLevel } from '@/types/api'
import { taxAPI } from '@/composables/useAPI'

export const useTaxStore = defineStore('tax', () => {
  const proficiencyLevel = ref<ProficiencyLevel>('novice')
  const taxInput = ref<TaxInput>({
    income: 0,
    filing_status: 'single',
    dependents: 0,
    deductions: 0,
    state: ''
  })
  const taxResult = ref<TaxResult | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  function setProficiency(level: ProficiencyLevel) {
    proficiencyLevel.value = level
  }

  function updateTaxInput(updates: Partial<TaxInput>) {
    taxInput.value = { ...taxInput.value, ...updates }
  }

  async function calculateTax() {
    loading.value = true
    error.value = null
    
    try {
      const result = await taxAPI.calculate(taxInput.value)
      taxResult.value = result
      return { success: true, result }
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Tax calculation failed'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  function resetTaxInput() {
    taxInput.value = {
      income: 0,
      filing_status: 'single',
      dependents: 0,
      deductions: 0,
      state: ''
    }
    taxResult.value = null
    error.value = null
  }

  return {
    proficiencyLevel,
    taxInput,
    taxResult,
    loading,
    error,
    setProficiency,
    updateTaxInput,
    calculateTax,
    resetTaxInput
  }
})
