<template>
  <div class="min-h-screen bg-background text-foreground">
    <Sidebar :is-open="sidebarOpen" />
    
    <div class="lg:pl-64 transition-all duration-300">
      <Header @toggle-sidebar="sidebarOpen = !sidebarOpen" />
      
      <main class="p-6 animate-in fade-in duration-500">
        <div
          ref="containerRef"
          :class="cn(
            'relative min-h-[calc(100vh-5rem)]',
            interactiveGlow && 'before:pointer-events-none before:absolute before:inset-0 before:bg-[radial-gradient(600px_300px_at_var(--pointer-x,50%)_var(--pointer-y,0),hsl(var(--ring)/0.10),transparent_60%)]',
            $attrs.class
          )"
          @mousemove="onMouseMove"
        >
          <slot />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { cn } from '@/lib/utils';
import Sidebar from '@/components-vue/navigation/Sidebar.vue';
import Header from '@/components-vue/navigation/Header.vue';

interface Props {
  interactiveGlow?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  interactiveGlow: true,
});

const sidebarOpen = ref(false);
const containerRef = ref<HTMLDivElement | null>(null);

const onMouseMove = (e: MouseEvent) => {
  if (!props.interactiveGlow) return;
  const el = containerRef.value;
  if (!el) return;
  const rect = el.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const y = e.clientY - rect.top;
  el.style.setProperty('--pointer-x', `${x}px`);
  el.style.setProperty('--pointer-y', `${y}px`);
};
</script>
