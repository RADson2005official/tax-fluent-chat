// API Types

export interface UserLogin {
  username: string
  password: string
}

export interface UserRegister {
  username: string
  email: string
  password: string
}

export interface Token {
  access_token: string
  token_type: string
}

export interface TaxInput {
  income: number
  filing_status: 'single' | 'married_joint' | 'married_separate' | 'head_of_household'
  dependents: number
  deductions: number
  state?: string
}

export interface TaxResult {
  gross_income: number
  taxable_income: number
  federal_tax: number
  effective_rate: number
  marginal_rate: number
  tax_bracket: string
  standard_deduction: number
  total_deductions: number
  explanation: string
}

export interface ExplanationRequest {
  query: string
  proficiency: 'novice' | 'intermediate' | 'expert'
  context?: Record<string, any>
}

export interface ExplanationResponse {
  explanation: string
  proficiency: string
  technical_terms: string[]
  related_topics: string[]
}

export type ProficiencyLevel = 'novice' | 'intermediate' | 'expert'
