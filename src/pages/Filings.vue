<template>
  <DynamicLayoutContainer>
    <div class="max-w-6xl mx-auto space-y-6">
      <!-- Page Header -->
      <BackButton />
      <div class="flex justify-between items-center">
        <div class="space-y-2">
          <h1 class="text-3xl font-bold">My Tax Filings</h1>
          <p class="text-muted-foreground">View and manage your tax returns</p>
        </div>
        <div class="space-x-2">
          <Button @click="simulateEfiling" :disabled="isSubmitting" variant="default" class="bg-green-600 hover:bg-green-700">
            <Send class="mr-2 h-4 w-4" />
            {{ isSubmitting ? 'Filing...' : 'E-File Now' }}
          </Button>
          <Button @click="router.push('/filing/new')">
            <PlusCircle class="mr-2 h-4 w-4" />
            New Filing
          </Button>
        </div>
      </div>

      <!-- Filings List -->
      <div class="grid gap-4">
        <Card 
          v-for="filing in filings" :key="filing.id"
          class="hover:shadow-md transition-shadow cursor-pointer"
          @click="viewFiling(filing.id)"
        >
          <CardHeader>
            <div class="flex justify-between items-start">
              <div class="space-y-1">
                <CardTitle>Tax Year {{ filing.year }}</CardTitle>
                <div class="text-sm text-muted-foreground">
                  Filed on {{ new Date(filing.filedDate).toLocaleDateString() }}
                </div>
              </div>
              <div 
                :class="cn(
                  'px-3 py-1 rounded-full text-xs font-medium',
                  filing.status === 'accepted' && 'bg-green-100 text-green-700',
                  filing.status === 'in_progress' && 'bg-blue-100 text-blue-700',
                  filing.status === 'draft' && 'bg-gray-100 text-gray-700'
                )"
              >
                {{ filing.status.replace('_', ' ').toUpperCase() }}
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
              <div>
                <div class="text-muted-foreground">Filing Status</div>
                <div class="font-medium">{{ filing.filingStatus }}</div>
              </div>
              <div>
                <div class="text-muted-foreground">Total Income</div>
                <div class="font-medium">₹{{ filing.totalIncome.toLocaleString() }}</div>
              </div>
              <div>
                <div class="text-muted-foreground">Tax Liability</div>
                <div class="font-medium">₹{{ filing.taxLiability.toLocaleString() }}</div>
              </div>
              <div>
                <div class="text-muted-foreground">Refund/Owed</div>
                <div :class="cn('font-medium', filing.refundAmount >= 0 ? 'text-green-600' : 'text-red-600')">
                  {{ filing.refundAmount >= 0 ? '+' : '' }}₹{{ Math.abs(filing.refundAmount).toLocaleString() }}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <!-- Empty State -->
        <Card v-if="filings.length === 0" class="p-12 text-center">
          <FileText class="h-16 w-16 mx-auto mb-4 text-muted-foreground" />
          <h3 class="text-lg font-semibold mb-2">No Tax Filings Yet</h3>
          <p class="text-muted-foreground mb-6">Start your first tax filing to see it here</p>
          <Button @click="router.push('/filing/new')">
            <PlusCircle class="mr-2 h-4 w-4" />
            Create New Filing
          </Button>
        </Card>
      </div>

      <!-- Back Button -->
      <Button variant="outline" @click="router.push('/dashboard')">
        <ArrowLeft class="mr-2 h-4 w-4" />
        Back to Dashboard
      </Button>
    </div>
  </DynamicLayoutContainer>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, PlusCircle, FileText, Send } from 'lucide-vue-next'
import BackButton from '@/components-vue/navigation/BackButton.vue'
import DynamicLayoutContainer from '@/components-vue/dynamic/DynamicLayoutContainer.vue'
import Card from '@/components-vue/ui/Card.vue'
import CardHeader from '@/components-vue/ui/CardHeader.vue'
import CardTitle from '@/components-vue/ui/CardTitle.vue'
import CardContent from '@/components-vue/ui/CardContent.vue'
import Button from '@/components-vue/ui/Button.vue'
import { cn } from '@/lib/utils'

const router = useRouter()
const isSubmitting = ref(false)

// Mock data - in a real app, this would come from an API
const filings = ref([
  {
    id: 1,
    year: 2023,
    filedDate: '2024-03-15',
    status: 'accepted',
    filingStatus: 'Single',
    totalIncome: 1500000,
    taxLiability: 180000,
    refundAmount: 12000
  },
  {
    id: 2,
    year: 2022,
    filedDate: '2023-03-10',
    status: 'accepted',
    filingStatus: 'Single',
    totalIncome: 1350000,
    taxLiability: 150000,
    refundAmount: -5000
  }
])

const viewFiling = (id: number) => {
  // In a real app, this would navigate to a detailed filing view
  console.log('Viewing filing:', id)
}

const simulateEfiling = async () => {
  isSubmitting.value = true
  try {
    const token = localStorage.getItem('token')
    const response = await fetch('http://localhost:8000/api/filing/submit', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (!response.ok) {
      const errorData = await response.json()
      alert(`Filing failed: ${errorData.detail || 'Unknown error'}`)
      return
    }

    // Handle PDF download
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `TaxReturn_2024.pdf`
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
    
    alert('Filing submitted successfully! PDF downloaded.')
    
  } catch (error) {
    console.error('E-filing error:', error)
    alert('An error occurred during e-filing.')
  } finally {
    isSubmitting.value = false
  }
}
</script>
