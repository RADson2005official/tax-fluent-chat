<template>
  <DynamicLayoutContainer>
    <div class="max-w-4xl mx-auto space-y-6">
      <!-- Page Header -->
      <BackButton />
      <div class="space-y-2">
        <h1 class="text-3xl font-bold">New Tax Filing</h1>
        <p class="text-muted-foreground">Start your tax filing journey with our AI-powered assistant</p>
      </div>

      <!-- Filing Year Selection -->
      <Card>
        <CardHeader>
          <CardTitle>Select Filing Year</CardTitle>
        </CardHeader>
        <CardContent class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button 
              v-for="year in [2024, 2023, 2022]" :key="year"
              @click="selectedYear = year"
              :class="cn(
                'p-4 rounded-lg border-2 transition-all',
                selectedYear === year 
                  ? 'border-primary bg-primary/5' 
                  : 'border-border hover:border-primary/50'
              )"
            >
              <div class="text-lg font-semibold">{{ year }}</div>
              <div class="text-sm text-muted-foreground">Tax Year</div>
            </button>
          </div>
        </CardContent>
      </Card>

      <!-- Filing Status -->
      <Card>
        <CardHeader>
          <CardTitle>Filing Status</CardTitle>
        </CardHeader>
        <CardContent class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <button 
              v-for="status in filingStatuses" :key="status.value"
              @click="selectedStatus = status.value"
              :class="cn(
                'p-4 rounded-lg border-2 transition-all text-left',
                selectedStatus === status.value 
                  ? 'border-primary bg-primary/5' 
                  : 'border-border hover:border-primary/50'
              )"
            >
              <div class="font-semibold">{{ status.label }}</div>
              <div class="text-sm text-muted-foreground">{{ status.description }}</div>
            </button>
          </div>
        </CardContent>
      </Card>

      <!-- Action Buttons -->
      <div class="flex gap-4">
        <Button variant="outline" size="lg" @click="router.push('/dashboard')" class="flex-1">
          <ArrowLeft class="mr-2 h-4 w-4" />
          Back to Dashboard
        </Button>
        <Button 
          size="lg" 
          @click="startFiling" 
          :disabled="!selectedYear || !selectedStatus"
          class="flex-1"
        >
          Start Filing
          <ArrowRight class="ml-2 h-4 w-4" />
        </Button>
      </div>
    </div>
  </DynamicLayoutContainer>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, ArrowRight } from 'lucide-vue-next'
import BackButton from '@/components-vue/navigation/BackButton.vue'
import DynamicLayoutContainer from '@/components-vue/dynamic/DynamicLayoutContainer.vue'
import Card from '@/components-vue/ui/Card.vue'
import CardHeader from '@/components-vue/ui/CardHeader.vue'
import CardTitle from '@/components-vue/ui/CardTitle.vue'
import CardContent from '@/components-vue/ui/CardContent.vue'
import Button from '@/components-vue/ui/Button.vue'
import { cn } from '@/lib/utils'

import { useAuthStore } from '@/stores/authStore'

const router = useRouter()
const authStore = useAuthStore()

const selectedYear = ref<number | null>(2024)
const selectedStatus = ref<string | null>(null)

const filingStatuses = [
  { value: 'single', label: 'Single', description: 'Filing as an individual' },
  { value: 'married_joint', label: 'Married Filing Jointly', description: 'Filing with spouse' },
  { value: 'married_separate', label: 'Married Filing Separately', description: 'Filing separately from spouse' },
  { value: 'head_household', label: 'Head of Household', description: 'Filing as head of household' },
]

const startFiling = () => {
  if (selectedYear.value && selectedStatus.value) {
    if (authStore.mode === 'expert') {
      router.push('/filing/grid')
    } else {
      router.push({ 
        path: '/filing/wizard',
        query: { 
          context: 'new_filing',
          year: selectedYear.value,
          status: selectedStatus.value
        }
      })
    }
  }
}
</script>
