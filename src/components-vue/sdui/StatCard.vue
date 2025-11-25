<script setup lang="ts">
import { computed } from 'vue'
import { 
  TrendingUp, 
  TrendingDown, 
  IndianRupee, 
  ShieldCheck, 
  Clock, 
  AlertCircle 
} from 'lucide-vue-next'
import Card from '@/components-vue/ui/Card.vue'
import CardContent from '@/components-vue/ui/CardContent.vue'

const props = defineProps<{
  label: string
  value: string
  trend?: string
  icon?: string
  status?: 'default' | 'warning' | 'success' | 'danger'
}>()

const iconMap: Record<string, any> = {
  IndianRupee,
  ShieldCheck,
  Clock,
  AlertCircle
}

const IconComponent = computed(() => props.icon ? iconMap[props.icon] : null)

const trendColor = computed(() => {
  if (!props.trend) return ''
  if (props.trend.startsWith('+')) return 'text-green-500'
  if (props.trend.startsWith('-')) return 'text-red-500'
  return 'text-muted-foreground'
})

const statusColor = computed(() => {
  switch (props.status) {
    case 'warning': return 'text-yellow-500'
    case 'success': return 'text-green-500'
    case 'danger': return 'text-red-500'
    default: return 'text-muted-foreground'
  }
})
</script>

<template>
  <Card class="overflow-hidden transition-all hover:shadow-md">
    <CardContent class="p-6">
      <div class="flex items-center justify-between space-y-0 pb-2">
        <p class="text-sm font-medium text-muted-foreground">
          {{ label }}
        </p>
        <component 
          :is="IconComponent" 
          v-if="IconComponent" 
          class="h-4 w-4 text-muted-foreground" 
        />
      </div>
      <div class="flex items-center justify-between pt-2">
        <div class="text-2xl font-bold">{{ value }}</div>
        <div v-if="trend" :class="['text-xs font-medium flex items-center', trendColor]">
          {{ trend }}
          <TrendingUp v-if="trend.startsWith('+')" class="ml-1 h-3 w-3" />
          <TrendingDown v-if="trend.startsWith('-')" class="ml-1 h-3 w-3" />
        </div>
        <div v-else-if="status" :class="['text-xs font-medium', statusColor]">
          {{ status.charAt(0).toUpperCase() + status.slice(1) }}
        </div>
      </div>
    </CardContent>
  </Card>
</template>
