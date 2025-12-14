<template>
  <DynamicLayoutContainer>
    <div class="max-w-6xl mx-auto space-y-6">
      <!-- Page Header -->
      <div class="space-y-2">
        <h1 class="text-3xl font-bold">Upload Documents</h1>
        <p class="text-muted-foreground">Upload your tax-related documents for processing</p>
      </div>

      <!-- Smart Upload Zone -->
      <Card 
        :class="cn(
          'border-2 border-dashed transition-all duration-300',
          isDragging ? 'border-primary bg-primary/5' : 'border-muted-foreground/25'
        )"
        @dragover.prevent="isDragging = true"
        @dragleave.prevent="isDragging = false"
        @drop.prevent="handleDrop"
      >
        <CardContent class="flex flex-col items-center justify-center py-12 text-center space-y-4">
          <div class="p-4 rounded-full bg-primary/10">
            <Upload class="h-8 w-8 text-primary" />
          </div>
          <div class="space-y-1">
            <h3 class="text-lg font-semibold">Drag & Drop your Tax Documents</h3>
            <p class="text-sm text-muted-foreground">
              Upload Form 16, 26AS, or Bank Statements. We'll extract the data automatically.
            </p>
          </div>
          <div class="flex items-center gap-2">
            <Button variant="outline" @click="fileInput?.click()">
              Browse Files
            </Button>
            <input 
              ref="fileInput"
              type="file" 
              multiple 
              class="hidden" 
              @change="handleFileSelect"
              accept=".pdf,.json,.xml"
            />
          </div>
          <div v-if="uploadStatus" class="flex items-center gap-2 text-sm font-medium text-primary animate-pulse">
            <AlertCircle class="h-4 w-4" />
            {{ uploadStatus }}
          </div>
        </CardContent>
      </Card>

      <!-- Essential Documents Checklist -->
      <Card>
        <CardHeader>
          <CardTitle>Essential Documents Checklist</CardTitle>
        </CardHeader>
        <CardContent>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div 
              v-for="category in documentCategories" :key="category.id"
              :class="cn(
                'p-4 rounded-lg border transition-all flex items-start gap-3',
                category.uploaded ? 'bg-green-50 border-green-200' : 'hover:border-primary/50'
              )"
            >
              <div :class="cn('mt-1', category.uploaded ? 'text-green-600' : 'text-muted-foreground')">
                <CheckCircle v-if="category.uploaded" class="h-5 w-5" />
                <FileText v-else class="h-5 w-5" />
              </div>
              <div>
                <h4 class="font-semibold text-sm">{{ category.name }}</h4>
                <p class="text-xs text-muted-foreground">{{ category.description }}</p>
                <p v-if="category.uploaded" class="text-xs text-green-600 mt-1 font-medium">
                  {{ category.fileName }}
                </p>
              </div>
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
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, Upload, CheckCircle, FileText, AlertCircle } from 'lucide-vue-next'
import DynamicLayoutContainer from '@/components-vue/dynamic/DynamicLayoutContainer.vue'
import Card from '@/components-vue/ui/Card.vue'
import CardHeader from '@/components-vue/ui/CardHeader.vue'
import CardTitle from '@/components-vue/ui/CardTitle.vue'
import CardContent from '@/components-vue/ui/CardContent.vue'
import Button from '@/components-vue/ui/Button.vue'
import { cn } from '@/lib/utils'

const router = useRouter()

interface DocCategory {
  id: string
  name: string
  description: string
  uploaded: boolean
  fileName?: string
}

const documentCategories = ref<DocCategory[]>([
  { id: 'form16', name: 'Form 16', description: 'Salary & TDS certificate', uploaded: false },
  { id: 'form26as', name: 'Form 26AS', description: 'Tax credit statement', uploaded: false },
  { id: 'ais', name: 'AIS', description: 'Annual Information Statement', uploaded: false },
  { id: 'bank', name: 'Bank Statements', description: 'Interest income proofs', uploaded: false },
  { id: 'investments', name: 'Investment Proofs', description: '80C, 80D deductions', uploaded: false },
])

const isDragging = ref(false)
const uploadStatus = ref<string | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)

const handleDrop = (e: DragEvent) => {
  isDragging.value = false
  const files = e.dataTransfer?.files
  if (files && files.length > 0) {
    processFiles(files)
  }
}

const handleFileSelect = (e: Event) => {
  const input = e.target as HTMLInputElement
  if (input.files && input.files.length > 0) {
    processFiles(input.files)
  }
}

const processFiles = (files: FileList) => {
  // Simulate processing
  uploadStatus.value = "Processing uploaded files..."
  
  setTimeout(() => {
    // Mock logic: Auto-tick categories based on random success or filename matching
    // For demo, we just tick the first unticked mandatory doc
    const unticked = documentCategories.value.find(d => !d.uploaded)
    if (unticked) {
      unticked.uploaded = true
      unticked.fileName = files[0].name
      uploadStatus.value = `Successfully processed ${files[0].name}. Extracted data for ${unticked.name}.`
    } else {
      uploadStatus.value = "File uploaded. No new categories matched."
    }
  }, 1500)
}
</script>

