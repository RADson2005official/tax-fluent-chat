<template>
  <DynamicLayoutContainer>
    <div class="max-w-7xl mx-auto h-[calc(100vh-8rem)] flex flex-col">
      <!-- Stepper -->
      <div class="mb-6">
        <div class="flex justify-between items-center mb-2">
          <h1 class="text-2xl font-bold">Tax Filing Wizard</h1>
          <div class="text-sm text-muted-foreground">Step {{ currentStep + 1 }} of {{ steps.length }}</div>
        </div>
        <div class="h-2 bg-secondary rounded-full overflow-hidden">
          <div 
            class="h-full bg-primary transition-all duration-500 ease-out"
            :style="{ width: `${((currentStep + 1) / steps.length) * 100}%` }"
          ></div>
        </div>
        <div class="flex justify-between mt-2 text-xs text-muted-foreground">
          <span 
            v-for="(step, index) in steps" :key="index"
            :class="cn('transition-colors', index <= currentStep ? 'text-primary font-medium' : '')"
          >
            {{ step.title }}
          </span>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1 overflow-hidden">
        <!-- Left Panel: The Canvas (Form) -->
        <div class="lg:col-span-2 flex flex-col">
          <Card class="flex-1 flex flex-col">
            <CardHeader>
              <CardTitle>{{ steps[currentStep].title }}</CardTitle>
              <p class="text-muted-foreground">{{ steps[currentStep].description }}</p>
            </CardHeader>
            <CardContent class="flex-1 overflow-y-auto space-y-6 p-6">
              
              <!-- Step 1: Personal Info -->
              <div v-if="currentStep === 0" class="space-y-4 animate-in fade-in slide-in-from-right-4">
                <div class="space-y-2">
                  <Label>Do you want to opt-out of the New Tax Regime?</Label>
                  <div class="grid grid-cols-2 gap-4">
                    <div 
                      @click="formData.regime = 'old'"
                      :class="cn(
                        'p-4 border rounded-lg cursor-pointer transition-all hover:border-primary',
                        formData.regime === 'old' ? 'border-primary bg-primary/5 ring-2 ring-primary/20' : ''
                      )"
                    >
                      <div class="font-semibold text-red-600">Old Regime</div>
                      <div class="text-xs text-muted-foreground mt-1">Claim HRA, 80C, 80D deductions. Higher tax rates.</div>
                    </div>
                    <div 
                      @click="formData.regime = 'new'"
                      :class="cn(
                        'p-4 border rounded-lg cursor-pointer transition-all hover:border-primary',
                        formData.regime === 'new' ? 'border-primary bg-primary/5 ring-2 ring-primary/20' : ''
                      )"
                    >
                      <div class="font-semibold text-green-600">New Regime (Default)</div>
                      <div class="text-xs text-muted-foreground mt-1">Lower tax rates. No deductions allowed.</div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Step 2: Income -->
              <div v-if="currentStep === 1" class="space-y-4 animate-in fade-in slide-in-from-right-4">
                <div class="space-y-2">
                  <Label>What is your Gross Salary?</Label>
                  <p class="text-xs text-muted-foreground">Check Part B of your Form 16.</p>
                  <Input type="number" v-model="formData.salary" placeholder="e.g. 1250000" />
                </div>
                <div class="space-y-2">
                  <Label>Do you have a Home Loan?</Label>
                  <p class="text-xs text-muted-foreground">Enter interest paid (negative value for loss).</p>
                  <Input type="number" v-model="formData.homeLoanInterest" placeholder="e.g. 200000" />
                </div>
              </div>

              <!-- Step 3: Deductions -->
              <div v-if="currentStep === 2" class="space-y-4 animate-in fade-in slide-in-from-right-4">
                <div v-if="formData.regime === 'new'" class="p-4 bg-blue-50 text-blue-700 rounded-lg flex items-start gap-3">
                  <Info class="h-5 w-5 mt-0.5" />
                  <div>
                    <p class="font-medium">New Regime Selected</p>
                    <p class="text-sm">Most deductions (80C, 80D) are not applicable. We've hidden them to save you time.</p>
                  </div>
                </div>
                <div v-else class="space-y-4">
                  <div class="space-y-2">
                    <Label>Tax Saving Investments (80C)</Label>
                    <Input type="number" v-model="formData.section80c" />
                    <p v-if="formData.section80c > 150000" class="text-xs text-amber-600 font-medium flex items-center gap-1">
                      <AlertTriangle class="h-3 w-3" />
                      Max deduction is ₹1.5 Lakh. We will cap this value.
                    </p>
                  </div>
                  <div class="space-y-2">
                    <Label>Health Insurance Premium (80D)</Label>
                    <Input type="number" v-model="formData.section80d" />
                  </div>
                </div>
              </div>

              <!-- Step 4: Review -->
              <div v-if="currentStep === 3" class="space-y-4 animate-in fade-in slide-in-from-right-4">
                <div class="bg-muted p-6 rounded-lg space-y-4">
                  <div class="flex justify-between">
                    <span>Total Income</span>
                    <span class="font-mono font-bold">₹{{ calculateTotalIncome() }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span>Tax Payable</span>
                    <span class="font-mono font-bold text-primary">₹{{ calculateTax() }}</span>
                  </div>
                </div>
              </div>

            </CardContent>
            <CardFooter class="flex justify-between border-t p-6">
              <Button variant="outline" @click="prevStep" :disabled="currentStep === 0">Back</Button>
              <Button @click="nextStep">
                {{ currentStep === steps.length - 1 ? 'Submit Filing' : 'Next Step' }}
              </Button>
            </CardFooter>
          </Card>
        </div>

        <!-- Right Panel: Agent & Visualization -->
        <div class="hidden lg:flex flex-col gap-6 h-full overflow-hidden">
          <Card class="flex-1 flex flex-col min-h-[300px]">
             <CardHeader class="pb-2">
              <CardTitle class="text-sm font-medium">Tax Flow Visualization</CardTitle>
            </CardHeader>
            <CardContent class="flex-1 p-0">
              <SankeyDiagram />
            </CardContent>
          </Card>
          <LiveTracking class="h-[300px]" />
        </div>
      </div>
    </div>
  </DynamicLayoutContainer>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { Info, AlertTriangle } from 'lucide-vue-next'
import DynamicLayoutContainer from '@/components-vue/dynamic/DynamicLayoutContainer.vue'
import Card from '@/components-vue/ui/Card.vue'
import CardHeader from '@/components-vue/ui/CardHeader.vue'
import CardTitle from '@/components-vue/ui/CardTitle.vue'
import CardContent from '@/components-vue/ui/CardContent.vue'
import CardFooter from '@/components-vue/ui/CardFooter.vue'
import Button from '@/components-vue/ui/Button.vue'
import Input from '@/components-vue/ui/Input.vue'
import Label from '@/components-vue/ui/Label.vue'
import SankeyDiagram from '@/components-vue/visualization/SankeyDiagram.vue'
import LiveTracking from '@/components-vue/visualization/LiveTracking.vue'
import { cn } from '@/lib/utils'

const router = useRouter()

const currentStep = ref(0)
const steps = [
  { title: 'Personal Info', description: 'Confirm your details and choose tax regime' },
  { title: 'Income', description: 'Enter your salary and other income sources' },
  { title: 'Deductions', description: 'Claim tax saving investments' },
  { title: 'Review & Tax', description: 'Verify your tax calculation' },
]

const formData = reactive({
  regime: 'new',
  salary: 0,
  homeLoanInterest: 0,
  section80c: 0,
  section80d: 0
})

const nextStep = () => {
  if (currentStep.value < steps.length - 1) {
    currentStep.value++
  } else {
    // Submit
    router.push('/filings')
  }
}

const prevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

const calculateTotalIncome = () => {
  return Number(formData.salary) - Number(formData.homeLoanInterest)
}

const calculateTax = () => {
  // Mock calculation
  const income = calculateTotalIncome()
  return Math.max(0, (income - 500000) * 0.1)
}
</script>
