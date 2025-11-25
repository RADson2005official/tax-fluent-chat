<template>
  <DynamicLayoutContainer>
    <div class="max-w-6xl mx-auto space-y-6">
      <!-- Page Header -->
      <div class="space-y-2">
        <h1 class="text-3xl font-bold">Upload Documents</h1>
        <p class="text-muted-foreground">Upload your tax-related documents for processing</p>
      </div>

      <!-- Upload Area -->
      <DocumentUpload />

      <!-- Document Categories -->
      <Card>
        <CardHeader>
          <CardTitle>Common Tax Documents</CardTitle>
        </CardHeader>
        <CardContent>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div 
              v-for="category in documentCategories" :key="category.name"
              class="p-4 rounded-lg border hover:border-primary hover:bg-primary/5 transition-colors cursor-pointer"
            >
              <h4 class="font-semibold mb-1">{{ category.name }}</h4>
              <p class="text-sm text-muted-foreground">{{ category.description }}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <!-- Action Buttons -->
      <div class="flex gap-4">
        <Button variant="outline" @click="router.push('/dashboard')">
          <ArrowLeft class="mr-2 h-4 w-4" />
          Back to Dashboard
        </Button>
      </div>
    </div>
  </DynamicLayoutContainer>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { ArrowLeft } from 'lucide-vue-next'
import DynamicLayoutContainer from '@/components-vue/dynamic/DynamicLayoutContainer.vue'
import Card from '@/components-vue/ui/Card.vue'
import CardHeader from '@/components-vue/ui/CardHeader.vue'
import CardTitle from '@/components-vue/ui/CardTitle.vue'
import CardContent from '@/components-vue/ui/CardContent.vue'
import Button from '@/components-vue/ui/Button.vue'
import DocumentUpload from '@/components-vue/DocumentUpload.vue'

const router = useRouter()

const documentCategories = [
  { name: 'Form 16', description: 'Salary & TDS certificate' },
  { name: 'Form 26AS', description: 'Tax credit statement' },
  { name: 'Investment Proofs', description: '80C, 80D deductions' },
  { name: 'Bank Statements', description: 'Interest income' },
  { name: 'Property Documents', description: 'Home loan interest' },
  { name: 'Medical Bills', description: 'Health insurance claims' },
]
</script>

