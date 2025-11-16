<template>
  <div class="w-full">
    <div class="border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div class="flex overflow-x-auto scrollbar-hide">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="$emit('change', tab.id)"
          :class="[
            'flex items-center gap-2 px-6 py-4 text-sm font-medium border-b-2 transition-all whitespace-nowrap',
            activeTab === tab.id
              ? 'border-primary text-primary bg-primary/5'
              : 'border-transparent text-muted-foreground hover:text-foreground hover:border-border'
          ]"
        >
          <component :is="tab.icon" class="h-4 w-4" />
          <span>{{ tab.label }}</span>
          <span v-if="tab.badge" class="ml-1 px-2 py-0.5 text-xs rounded-full bg-primary/10 text-primary">
            {{ tab.badge }}
          </span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Calculator, FileText, TrendingUp, Shield, Download, Settings } from 'lucide-vue-next';

interface Tab {
  id: string;
  label: string;
  icon: any;
  badge?: string;
}

interface Props {
  activeTab: string;
  tabs?: Tab[];
}

const props = withDefaults(defineProps<Props>(), {
  tabs: () => [
    { id: 'chat', label: 'Chat & Calculate', icon: Calculator },
    { id: 'analysis', label: 'Real-time Analysis', icon: TrendingUp, badge: 'Live' },
    { id: 'documents', label: 'Documents', icon: FileText },
    { id: 'compliance', label: 'Compliance', icon: Shield },
    { id: 'export', label: 'Export', icon: Download },
    { id: 'settings', label: 'Settings', icon: Settings }
  ]
});

defineEmits<{
  change: [tabId: string];
}>();
</script>

<style scoped>
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
