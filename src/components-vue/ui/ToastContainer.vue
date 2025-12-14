<template>
  <Teleport to="body">
    <TransitionGroup 
      name="toast" 
      tag="div" 
      class="fixed bottom-6 right-6 z-[100] flex flex-col gap-3"
    >
      <div 
        v-for="toast in toasts" 
        :key="toast.id"
        :class="cn(
          'flex items-start gap-3 px-5 py-4 rounded-xl shadow-2xl min-w-[320px] max-w-md',
          'backdrop-blur-xl border-2 transition-all duration-300',
          toast.type === 'success' && 'bg-gradient-to-r from-green-500 to-emerald-600 border-green-400/50 text-white',
          toast.type === 'error' && 'bg-gradient-to-r from-red-500 to-rose-600 border-red-400/50 text-white',
          toast.type === 'info' && 'bg-gradient-to-r from-blue-500 to-indigo-600 border-blue-400/50 text-white',
          toast.type === 'warning' && 'bg-gradient-to-r from-amber-500 to-orange-600 border-amber-400/50 text-white'
        )"
      >
        <div :class="cn(
          'flex-shrink-0 p-2 rounded-full',
          toast.type === 'success' && 'bg-white/20',
          toast.type === 'error' && 'bg-white/20',
          toast.type === 'info' && 'bg-white/20',
          toast.type === 'warning' && 'bg-white/20'
        )">
          <component :is="getIcon(toast.type)" class="h-5 w-5" />
        </div>
        <div class="flex-1 pt-0.5">
          <div v-if="toast.title" class="font-bold text-sm mb-0.5">{{ toast.title }}</div>
          <div class="text-sm opacity-95 leading-relaxed">{{ toast.message }}</div>
        </div>
        <button 
          @click="removeToast(toast.id)" 
          class="p-1.5 hover:bg-white/20 rounded-full transition-colors flex-shrink-0"
        >
          <X class="h-4 w-4" />
        </button>
      </div>
    </TransitionGroup>
  </Teleport>
</template>

<script setup lang="ts">
import { CheckCircle2, XCircle, Info, AlertTriangle, X } from 'lucide-vue-next'
import { cn } from '@/lib/utils'
import { useToast, type ToastMessage } from '@/stores/toastStore'

const { toasts, removeToast } = useToast()

const getIcon = (type: ToastMessage['type']) => {
  switch (type) {
    case 'success': return CheckCircle2
    case 'error': return XCircle
    case 'warning': return AlertTriangle
    default: return Info
  }
}
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%) scale(0.8);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100%) scale(0.8);
}

.toast-move {
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}
</style>
