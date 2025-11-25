<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import Button from '@/components-vue/ui/Button.vue'
import * as Icons from 'lucide-vue-next'
import { cn } from '@/lib/utils'

const props = defineProps<{
  label?: string
  icon?: string
  variant?: any
  size?: any
  block?: boolean
  class?: string
  route?: string
}>()

const router = useRouter()

const IconComponent = computed(() => {
  if (props.icon && (Icons as any)[props.icon]) {
    return (Icons as any)[props.icon]
  }
  return null
})

const handleClick = () => {
  if (props.route) {
    router.push(props.route)
  }
}
</script>

<template>
  <Button 
    :variant="variant" 
    :size="size" 
    :class="cn(props.class, block ? 'w-full' : '')"
    @click="handleClick"
  >
    <component :is="IconComponent" v-if="IconComponent" class="mr-2 h-4 w-4" />
    {{ label }}
    <slot />
  </Button>
</template>
