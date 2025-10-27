<template>
  <div
    ref="containerRef"
    :class="cn(
      'relative',
      interactiveGlow && 'before:pointer-events-none before:absolute before:inset-0 before:bg-[radial-gradient(600px_300px_at_var(--pointer-x,50%)_var(--pointer-y,0),hsl(var(--ring)/0.10),transparent_60%)]',
      $attrs.class
    )"
    @mousemove="onMouseMove"
  >
    <slot />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { cn } from '@/lib/utils';

interface Props {
  interactiveGlow?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  interactiveGlow: true,
});

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
