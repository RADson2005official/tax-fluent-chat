import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useAuthStore } from './auth'

export interface TaxInput {
  income: number
  filing_status: string
  dependents: number
  deductions: number
}

export interface TaxResult {
  gross_income: number
  taxable_income: number
  tax_liability: number
  effective_rate: number
  marginal_rate: number
  standard_deduction: number
  breakdown: Array<{
    rate: number
    income_in_bracket: number
    tax_in_bracket: number
    bracket_range: string
  }>
}

export const useTaxStore = defineStore('tax', () => {
  const taxInput = ref<TaxInput>({
    income: 0,
    filing_status: 'single',
    dependents: 0,
    deductions: 0,
  })
  
  const taxResult = ref<TaxResult | null>(null)
  const isCalculating = ref(false)
  const error = ref<string | null>(null)
  
  const API_URL = 'http://localhost:8000'
  
  async function calculateTax() {
    isCalculating.value = true
    error.value = null
    
    try {
      const authStore = useAuthStore()
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      }
      
      if (authStore.user?.token) {
        headers['Authorization'] = `Bearer ${authStore.user.token}`
      }
      
      const response = await fetch(`${API_URL}/calculate-tax`, {
        method: 'POST',
        headers,
        body: JSON.stringify(taxInput.value),
      })
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Tax calculation failed')
      }
      
      const result = await response.json()
      taxResult.value = result
      
      return result
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      throw err
    } finally {
      isCalculating.value = false
    }
  }
  
  function updateInput(updates: Partial<TaxInput>) {
    taxInput.value = { ...taxInput.value, ...updates }
  }
  
  function resetCalculation() {
    taxResult.value = null
    error.value = null
  }
  
  return {
    taxInput,
    taxResult,
    isCalculating,
    error,
    calculateTax,
    updateInput,
    resetCalculation,
  }
})
