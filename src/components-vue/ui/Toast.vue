<template>
  <Teleport to="body">
    <TransitionGroup 
      name="toast" 
      tag="div" 
      class="fixed bottom-4 right-4 z-50 flex flex-col gap-2"
    >
      <div 
        v-for="toast in toasts" 
        :key="toast.id"
        :class="cn(
          'flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg min-w-[300px] max-w-md',
          'backdrop-blur-xl border transition-all duration-300',
          toast.type === 'success' && 'bg-green-500/90 border-green-400 text-white',
          toast.type === 'error' && 'bg-red-500/90 border-red-400 text-white',
          toast.type === 'info' && 'bg-blue-500/90 border-blue-400 text-white',
          toast.type === 'warning' && 'bg-yellow-500/90 border-yellow-400 text-white'
        )"
      >
        <component :is="getIcon(toast.type)" class="h-5 w-5 flex-shrink-0" />
        <div class="flex-1">
          <div v-if="toast.title" class="font-semibold text-sm">{{ toast.title }}</div>
          <div class="text-sm opacity-90">{{ toast.message }}</div>
        </div>
        <button 
          @click="removeToast(toast.id)" 
          class="p-1 hover:bg-white/20 rounded transition-colors"
        >
          <X class="h-4 w-4" />
        </button>
      </div>
    </TransitionGroup>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { CheckCircle2, XCircle, Info, AlertTriangle, X } from 'lucide-vue-next'
import { cn } from '@/lib/utils'

export interface Toast {
  id: number
  type: 'success' | 'error' | 'info' | 'warning'
  title?: string
  message: string
  duration?: number
}

const toasts = ref<Toast[]>([])
let toastId = 0

const getIcon = (type: Toast['type']) => {
  switch (type) {
    case 'success': return CheckCircle2
    case 'error': return XCircle
    case 'warning': return AlertTriangle
    default: return Info
  }
}

const addToast = (toast: Omit<Toast, 'id'>) => {
  const id = ++toastId
  toasts.value.push({ ...toast, id })
  
  const duration = toast.duration ?? 5000
  if (duration > 0) {
    setTimeout(() => removeToast(id), duration)
  }
  
  return id
}

const removeToast = (id: number) => {
  const index = toasts.value.findIndex(t => t.id === id)
  if (index !== -1) {
    toasts.value.splice(index, 1)
  }
}

// Expose methods
defineExpose({ addToast, removeToast, toasts })
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100px);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100px);
}

.toast-move {
  transition: transform 0.3s ease;
}
</style>
