<script setup lang="ts">
import { ref } from 'vue'
import { FileText, CheckCircle, AlertCircle, Upload } from 'lucide-vue-next'

const props = defineProps<{
  limit?: number
}>()

const activities = ref([
  {
    id: 1,
    title: 'Document Uploaded',
    description: 'Form 16 uploaded successfully',
    time: '2 hours ago',
    icon: Upload,
    status: 'success'
  },
  {
    id: 2,
    title: 'Tax Calculation Updated',
    description: 'New deductions applied',
    time: '5 hours ago',
    icon: FileText,
    status: 'info'
  },
  {
    id: 3,
    title: 'Verification Pending',
    description: 'Please verify your bank details',
    time: '1 day ago',
    icon: AlertCircle,
    status: 'warning'
  },
  {
    id: 4,
    title: 'Profile Updated',
    description: 'Address change detected',
    time: '2 days ago',
    icon: CheckCircle,
    status: 'success'
  },
  {
    id: 5,
    title: 'System Update',
    description: 'New tax regime rules applied',
    time: '3 days ago',
    icon: FileText,
    status: 'info'
  }
])

const displayedActivities = computed(() => {
  return props.limit ? activities.value.slice(0, props.limit) : activities.value
})

import { computed } from 'vue'
</script>

<template>
  <div class="space-y-4">
    <div v-for="activity in displayedActivities" :key="activity.id" class="flex items-start space-x-4 p-3 rounded-lg hover:bg-muted/50 transition-colors">
      <div :class="[
        'p-2 rounded-full',
        activity.status === 'success' ? 'bg-green-100 text-green-600 dark:bg-green-900/20 dark:text-green-400' :
        activity.status === 'warning' ? 'bg-yellow-100 text-yellow-600 dark:bg-yellow-900/20 dark:text-yellow-400' :
        'bg-blue-100 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400'
      ]">
        <component :is="activity.icon" class="h-4 w-4" />
      </div>
      <div class="flex-1 space-y-1">
        <p class="text-sm font-medium leading-none">{{ activity.title }}</p>
        <p class="text-xs text-muted-foreground">{{ activity.description }}</p>
      </div>
      <div class="text-xs text-muted-foreground">{{ activity.time }}</div>
    </div>
  </div>
</template>
