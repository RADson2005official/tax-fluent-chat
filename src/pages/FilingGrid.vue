<template>
  <DynamicLayoutContainer>
    <div class="max-w-7xl mx-auto space-y-6">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-4">
          <BackButton />
          <div>
            <h1 class="text-2xl font-bold">Expert Filing Mode</h1>
            <p class="text-sm text-muted-foreground">Direct data entry for ITR-1 (AY 2024-25)</p>
          </div>
        </div>
        <div class="flex gap-2">
          <Button variant="outline">Save Draft</Button>
          <Button>Validate & File</Button>
        </div>
      </div>

      <!-- Schedule Tabs -->
      <div class="flex border-b overflow-x-auto">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="cn(
            'px-4 py-2 text-sm font-medium border-b-2 transition-colors whitespace-nowrap',
            activeTab === tab.id
              ? 'border-primary text-primary'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          )"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- Grid Content -->
      <Card class="min-h-[500px]">
        <CardContent class="p-6">
          <!-- General Information -->
          <div v-if="activeTab === 'general'" class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="space-y-2">
              <Label>First Name</Label>
              <Input v-model="formData.general.firstName" />
            </div>
            <div class="space-y-2">
              <Label>Middle Name</Label>
              <Input v-model="formData.general.middleName" />
            </div>
            <div class="space-y-2">
              <Label>Last Name</Label>
              <Input v-model="formData.general.lastName" />
            </div>
            <div class="space-y-2">
              <Label>PAN</Label>
              <Input v-model="formData.general.pan" uppercase />
            </div>
            <div class="space-y-2">
              <Label>Aadhaar Number</Label>
              <Input v-model="formData.general.aadhaar" />
            </div>
            <div class="space-y-2">
              <Label>Date of Birth</Label>
              <Input type="date" v-model="formData.general.dob" />
            </div>
          </div>

          <!-- Salary Schedule -->
          <div v-if="activeTab === 'salary'" class="space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div class="space-y-2">
                <Label>Gross Salary (Section 17(1))</Label>
                <Input type="number" v-model="formData.salary.gross" />
              </div>
              <div class="space-y-2">
                <Label>Value of Perquisites (Section 17(2))</Label>
                <Input type="number" v-model="formData.salary.perquisites" />
              </div>
              <div class="space-y-2">
                <Label>Profits in lieu of salary (Section 17(3))</Label>
                <Input type="number" v-model="formData.salary.profits" />
              </div>
            </div>
            <div class="border-t pt-4">
              <h3 class="font-semibold mb-4">Allowances (Section 10)</h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="space-y-2">
                  <Label>HRA (10(13A))</Label>
                  <Input type="number" v-model="formData.salary.hra" />
                </div>
                <div class="space-y-2">
                  <Label>LTA (10(5))</Label>
                  <Input type="number" v-model="formData.salary.lta" />
                </div>
              </div>
            </div>
          </div>

          <!-- Deductions -->
          <div v-if="activeTab === 'deductions'" class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="space-y-2">
              <Label>80C (LIC, PPF, etc.)</Label>
              <Input type="number" v-model="formData.deductions.section80c" />
            </div>
            <div class="space-y-2">
              <Label>80D (Health Insurance)</Label>
              <Input type="number" v-model="formData.deductions.section80d" />
            </div>
            <div class="space-y-2">
              <Label>80TTA (Interest on Savings)</Label>
              <Input type="number" v-model="formData.deductions.section80tta" />
            </div>
          </div>

          <!-- Taxes -->
          <div v-if="activeTab === 'taxes'" class="space-y-6">
            <div class="bg-muted p-4 rounded-lg">
              <div class="flex justify-between items-center mb-2">
                <span>Total Income</span>
                <span class="font-bold">₹{{ calculateTotalIncome() }}</span>
              </div>
              <div class="flex justify-between items-center mb-2">
                <span>Tax Payable</span>
                <span class="font-bold">₹{{ calculateTax() }}</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  </DynamicLayoutContainer>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { cn } from '@/lib/utils'
import DynamicLayoutContainer from '@/components-vue/dynamic/DynamicLayoutContainer.vue'
import BackButton from '@/components-vue/navigation/BackButton.vue'
import Button from '@/components-vue/ui/Button.vue'
import Card from '@/components-vue/ui/Card.vue'
import CardContent from '@/components-vue/ui/CardContent.vue'
import Input from '@/components-vue/ui/Input.vue'
import Label from '@/components-vue/ui/Label.vue'

const activeTab = ref('general')

const tabs = [
  { id: 'general', label: 'General Information' },
  { id: 'salary', label: 'Schedule Salary' },
  { id: 'house_property', label: 'Schedule HP' },
  { id: 'other_sources', label: 'Schedule OS' },
  { id: 'deductions', label: 'Deductions (VI-A)' },
  { id: 'taxes', label: 'Tax Computation' },
]

const formData = reactive({
  general: {
    firstName: '',
    middleName: '',
    lastName: '',
    pan: '',
    aadhaar: '',
    dob: ''
  },
  salary: {
    gross: 0,
    perquisites: 0,
    profits: 0,
    hra: 0,
    lta: 0
  },
  deductions: {
    section80c: 0,
    section80d: 0,
    section80tta: 0
  }
})

const calculateTotalIncome = () => {
  const grossSalary = Number(formData.salary.gross) + Number(formData.salary.perquisites) + Number(formData.salary.profits)
  const exemptions = Number(formData.salary.hra) + Number(formData.salary.lta)
  const netSalary = grossSalary - exemptions
  const deductions = Number(formData.deductions.section80c) + Number(formData.deductions.section80d) + Number(formData.deductions.section80tta)
  return Math.max(0, netSalary - deductions)
}

const calculateTax = () => {
  // Simplified tax calc
  const income = calculateTotalIncome()
  if (income <= 250000) return 0
  return (income - 250000) * 0.05 // Mock
}
</script>
