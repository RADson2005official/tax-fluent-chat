<template>
  <TooltipProvider>
    <RouterView v-slot="{ Component }">
      <Transition name="fade" mode="out-in">
        <component :is="Component" />
      </Transition>
    </RouterView>
    <LiveActivityIsland />
    <ToastContainer />
  </TooltipProvider>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router';
import { TooltipProvider } from 'radix-vue';
import LiveActivityIsland from '@/components-vue/sdui/LiveActivityIsland.vue';
import ToastContainer from '@/components-vue/ui/ToastContainer.vue';
</script>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
