/**
 * Toast Notification Store
 * Provides global toast notifications across the application
 */

import { ref, reactive } from 'vue'

export interface ToastMessage {
    id: number
    type: 'success' | 'error' | 'info' | 'warning'
    title?: string
    message: string
    duration?: number
}

// Reactive toast state
const toasts = ref<ToastMessage[]>([])
let toastId = 0

/**
 * Show a toast notification
 */
export function showToast(
    type: ToastMessage['type'],
    message: string,
    title?: string,
    duration: number = 5000
): number {
    const id = ++toastId

    toasts.value.push({
        id,
        type,
        title,
        message,
        duration
    })

    // Auto-remove after duration
    if (duration > 0) {
        setTimeout(() => {
            removeToast(id)
        }, duration)
    }

    return id
}

/**
 * Remove a specific toast
 */
export function removeToast(id: number): void {
    const index = toasts.value.findIndex(t => t.id === id)
    if (index !== -1) {
        toasts.value.splice(index, 1)
    }
}

/**
 * Clear all toasts
 */
export function clearToasts(): void {
    toasts.value = []
}

// Convenience methods
export const toast = {
    success: (message: string, title?: string) => showToast('success', message, title),
    error: (message: string, title?: string) => showToast('error', message, title),
    info: (message: string, title?: string) => showToast('info', message, title),
    warning: (message: string, title?: string) => showToast('warning', message, title),
}

// Export reactive toasts for components
export function useToast() {
    return {
        toasts,
        showToast,
        removeToast,
        clearToasts,
        toast
    }
}
