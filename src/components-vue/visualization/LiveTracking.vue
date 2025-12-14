<template>
  <Card class="h-full flex flex-col">
    <CardHeader>
      <CardTitle class="text-sm font-medium flex items-center gap-2">
        <Activity class="h-4 w-4 text-primary" />
        Live Agent Activity
      </CardTitle>
    </CardHeader>
    <CardContent class="flex-1 overflow-y-auto space-y-3">
      <div 
        v-for="(log, i) in logs" :key="i" 
        class="flex gap-2 text-sm animate-in fade-in slide-in-from-left-2"
        :style="{ animationDelay: `${i * 100}ms` }"
      >
        <span class="font-mono text-xs text-muted-foreground min-w-[60px]">{{ log.time }}</span>
        <span :class="cn('flex-1', log.type === 'error' ? 'text-red-500' : 'text-foreground')">
          {{ log.message }}
        </span>
      </div>
      <div v-if="logs.length === 0" class="text-center text-muted-foreground text-xs py-4">
        Waiting for agent activity...
      </div>
    </CardContent>
  </Card>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { Activity } from 'lucide-vue-next'
import Card from '@/components-vue/ui/Card.vue'
import CardHeader from '@/components-vue/ui/CardHeader.vue'
import CardTitle from '@/components-vue/ui/CardTitle.vue'
import CardContent from '@/components-vue/ui/CardContent.vue'
import { cn } from '@/lib/utils'

interface Log {
  time: string
  message: string
  type?: 'info' | 'error' | 'success'
}

const logs = ref<Log[]>([])
let ws: WebSocket | null = null
const clientId = Math.random().toString(36).substring(7)

onMounted(() => {
  // Connect to WebSocket
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const wsUrl = `${protocol}//${window.location.hostname}:8000/api/ws/${clientId}`
  
  ws = new WebSocket(wsUrl)
  
  ws.onopen = () => {
    addLog("Connected to Agent Stream", 'success')
  }
  
  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      // We expect data to have a 'message' field or be a log object
      if (data.sender === 'system' || data.sender === 'agent_log') {
        addLog(data.message, data.type || 'info')
      }
    } catch (e) {
      console.error("Failed to parse WS message", e)
    }
  }
  
  ws.onerror = (error) => {
    console.error("WebSocket error:", error)
    addLog("Connection error", 'error')
  }
  
  ws.onclose = () => {
    addLog("Connection closed", 'error')
  }
})

onUnmounted(() => {
  if (ws) {
    ws.close()
  }
})

const addLog = (message: string, type: 'info' | 'error' | 'success' = 'info') => {
  logs.value.unshift({
    time: new Date().toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }),
    message,
    type
  })
}
</script>
