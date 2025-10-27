import { ref } from 'vue';

interface Toast {
  id: string;
  title: string;
  description?: string;
  duration?: number;
}

const toasts = ref<Toast[]>([]);

export function useToast() {
  const toast = ({ title, description, duration = 3000 }: Omit<Toast, 'id'>) => {
    const id = `toast-${Date.now()}`;
    const newToast: Toast = { id, title, description, duration };
    
    toasts.value.push(newToast);
    
    if (duration > 0) {
      setTimeout(() => {
        toasts.value = toasts.value.filter(t => t.id !== id);
      }, duration);
    }
  };

  return {
    toast,
    toasts,
  };
}
