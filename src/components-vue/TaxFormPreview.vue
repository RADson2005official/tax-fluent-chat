<template>
  <div class="tax-form-preview">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6 pb-4 border-b">
      <div>
        <h2 class="text-xl font-bold">Income Tax Return Preview</h2>
        <p class="text-sm text-muted-foreground">Financial Year {{ data.financial_year || '2024-25' }}</p>
      </div>
      <div class="flex items-center gap-2">
        <span class="text-xs px-2 py-1 rounded-full bg-blue-500/10 text-blue-600">
          {{ data.regime === 'new' ? 'New Regime' : 'Old Regime' }}
        </span>
        <span class="text-xs px-2 py-1 rounded-full bg-primary/10 text-primary">
          ITR-1 SAHAJ
        </span>
      </div>
    </div>

    <!-- Personal Information Section -->
    <section class="mb-6">
      <h3 class="text-sm font-semibold text-muted-foreground uppercase mb-3 flex items-center gap-2">
        <User class="h-4 w-4" />
        Part A - Personal Information
      </h3>
      <div class="grid grid-cols-2 gap-4 p-4 rounded-lg bg-muted/30 border">
        <FormField label="Full Name" :value="data.personal_info?.name" required />
        <FormField label="PAN" :value="data.personal_info?.pan_number" required mask="XXXXX0000X" />
        <FormField label="Email" :value="data.personal_info?.email" />
        <FormField label="Mobile" :value="data.personal_info?.phone" />
        <FormField label="Filing Status" :value="capitalize(data.filing_status)" class="col-span-2" />
      </div>
    </section>

    <!-- Income Details Section -->
    <section class="mb-6">
      <h3 class="text-sm font-semibold text-muted-foreground uppercase mb-3 flex items-center gap-2">
        <Wallet class="h-4 w-4" />
        Part B - Income Details
      </h3>
      <div class="space-y-3">
        <!-- Salary Income -->
        <div v-for="(income, idx) in salaryIncome" :key="'salary-' + idx" 
             class="p-4 rounded-lg bg-green-500/5 border border-green-500/20">
          <div class="flex items-center justify-between mb-2">
            <span class="font-medium">Salary Income</span>
            <span class="font-bold text-green-600">₹{{ formatAmount(income.amount) }}</span>
          </div>
          <div v-if="income.employer_name" class="text-sm text-muted-foreground">
            Employer: {{ income.employer_name }}
          </div>
        </div>

        <!-- Other Income -->
        <div v-for="(income, idx) in otherIncome" :key="'other-' + idx" 
             class="p-4 rounded-lg bg-blue-500/5 border border-blue-500/20">
          <div class="flex items-center justify-between mb-2">
            <span class="font-medium capitalize">{{ income.source_type.replace('_', ' ') }} Income</span>
            <span class="font-bold text-blue-600">₹{{ formatAmount(income.amount) }}</span>
          </div>
          <div v-if="income.description" class="text-sm text-muted-foreground">
            {{ income.description }}
          </div>
        </div>

        <!-- No Income Warning -->
        <div v-if="!data.income_sources?.length" class="p-4 rounded-lg bg-yellow-500/10 border border-yellow-500/20 text-center">
          <AlertCircle class="h-8 w-8 mx-auto mb-2 text-yellow-500" />
          <p class="text-sm">No income sources detected. Please provide income details in the chat.</p>
        </div>
      </div>
    </section>

    <!-- Deductions Section -->
    <section class="mb-6">
      <h3 class="text-sm font-semibold text-muted-foreground uppercase mb-3 flex items-center gap-2">
        <Receipt class="h-4 w-4" />
        Part C - Deductions (Chapter VI-A)
      </h3>
      <div class="p-4 rounded-lg bg-muted/30 border">
        <div v-if="data.deductions?.length" class="space-y-2">
          <div v-for="(ded, idx) in data.deductions" :key="idx" 
               class="flex items-center justify-between py-2 border-b last:border-0">
            <div>
              <span class="font-medium">Section {{ ded.section }}</span>
              <span class="text-sm text-muted-foreground ml-2">{{ ded.description }}</span>
            </div>
            <span class="font-semibold">₹{{ formatAmount(ded.amount) }}</span>
          </div>
        </div>
        <div v-else class="text-center py-4 text-muted-foreground">
          <p class="text-sm">No deductions claimed. Mention investments like PPF, ELSS, or health insurance to claim deductions.</p>
        </div>
        
        <!-- Standard Deduction -->
        <div class="flex items-center justify-between py-2 mt-2 pt-2 border-t">
          <div>
            <span class="font-medium">Standard Deduction</span>
            <span class="text-sm text-muted-foreground ml-2">(Automatically applied for salaried)</span>
          </div>
          <span class="font-semibold">₹50,000</span>
        </div>
      </div>
    </section>

    <!-- Tax Computation Section -->
    <section class="mb-6">
      <h3 class="text-sm font-semibold text-muted-foreground uppercase mb-3 flex items-center gap-2">
        <Calculator class="h-4 w-4" />
        Part D - Tax Computation
      </h3>
      <div class="p-4 rounded-lg bg-gradient-to-br from-primary/5 to-purple-500/5 border">
        <div class="space-y-3">
          <div class="flex justify-between py-2 border-b">
            <span>Gross Total Income</span>
            <span class="font-medium">₹{{ formatAmount(data.total_income || 0) }}</span>
          </div>
          <div class="flex justify-between py-2 border-b">
            <span>Less: Deductions under Chapter VI-A</span>
            <span class="font-medium text-green-600">-₹{{ formatAmount(data.total_deductions || 0) }}</span>
          </div>
          <div class="flex justify-between py-2 border-b">
            <span>Less: Standard Deduction</span>
            <span class="font-medium text-green-600">-₹50,000</span>
          </div>
          <div class="flex justify-between py-2 border-b font-medium">
            <span>Total Taxable Income</span>
            <span>₹{{ formatAmount(data.taxable_income || 0) }}</span>
          </div>
          <div class="flex justify-between py-3 text-lg font-bold">
            <span>Tax Payable</span>
            <span class="text-primary">₹{{ formatAmount(data.estimated_tax || 0) }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Verification -->
    <section v-if="data.missing_fields?.length" class="mb-6">
      <div class="p-4 rounded-lg bg-yellow-500/10 border border-yellow-500/20">
        <div class="flex items-start gap-3">
          <AlertCircle class="h-5 w-5 text-yellow-600 mt-0.5" />
          <div>
            <h4 class="font-medium text-yellow-700">Missing Information</h4>
            <p class="text-sm text-muted-foreground mt-1">
              The following fields are required for a complete tax return:
            </p>
            <ul class="list-disc list-inside text-sm mt-2">
              <li v-for="field in data.missing_fields" :key="field">{{ field }}</li>
            </ul>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { User, Wallet, Receipt, Calculator, AlertCircle } from 'lucide-vue-next'

interface IncomeSource {
  source_type: string
  employer_name?: string
  amount: number
  description?: string
}

interface Deduction {
  section: string
  description: string
  amount: number
}

interface PersonalInfo {
  name?: string
  pan_number?: string
  email?: string
  phone?: string
}

interface TaxData {
  financial_year?: string
  personal_info?: PersonalInfo
  income_sources?: IncomeSource[]
  deductions?: Deduction[]
  filing_status?: string
  regime?: string
  total_income?: number
  total_deductions?: number
  taxable_income?: number
  estimated_tax?: number
  missing_fields?: string[]
}

const props = defineProps<{
  data: TaxData
}>()

const salaryIncome = computed(() => 
  props.data.income_sources?.filter(i => i.source_type === 'salary') || []
)

const otherIncome = computed(() => 
  props.data.income_sources?.filter(i => i.source_type !== 'salary') || []
)

const formatAmount = (amount: number): string => {
  if (amount >= 10000000) {
    return `${(amount / 10000000).toFixed(2)} Cr`
  } else if (amount >= 100000) {
    return `${(amount / 100000).toFixed(2)} L`
  }
  return amount.toLocaleString('en-IN')
}

const capitalize = (str?: string): string => {
  if (!str) return ''
  return str.charAt(0).toUpperCase() + str.slice(1)
}

// FormField subcomponent
</script>

<script lang="ts">
import { defineComponent, h } from 'vue'

const FormField = defineComponent({
  props: {
    label: String,
    value: String,
    required: Boolean,
    mask: String
  },
  setup(props) {
    return () => h('div', { class: 'space-y-1' }, [
      h('label', { class: 'text-xs font-medium text-muted-foreground' }, [
        props.label,
        props.required ? h('span', { class: 'text-red-500 ml-1' }, '*') : null
      ]),
      h('div', { 
        class: `p-2 rounded border text-sm ${props.value ? 'bg-white dark:bg-gray-900' : 'bg-muted/50 italic text-muted-foreground'}`
      }, props.value || 'Not provided')
    ])
  }
})

export { FormField }
</script>

<style scoped>
.tax-form-preview {
  @apply max-w-3xl mx-auto;
}
</style>
