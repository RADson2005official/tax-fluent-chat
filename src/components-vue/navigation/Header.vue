<template>
  <header class="sticky top-0 z-30 flex h-16 items-center gap-4 border-b border-white/10 bg-background/80 px-6 backdrop-blur-xl">
    <Button variant="ghost" size="icon" class="lg:hidden" @click="$emit('toggleSidebar')">
      <Menu class="h-5 w-5" />
    </Button>

    <div class="flex flex-1 items-center gap-4">
      <div class="relative w-full max-w-md hidden md:block">
        <Search class="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
        <Input
          type="search"
          placeholder="Search forms, sections, or ask AI..."
          class="pl-9 bg-white/5 border-white/10 focus:bg-white/10"
        />
      </div>
    </div>

    <div class="flex items-center gap-2">
      <ModeSwitcher :mode="authStore.mode" @change="authStore.setMode" class="hidden md:flex" />
      <Button variant="ghost" size="icon">
        <Bell class="h-5 w-5" />
      </Button>
      <Button variant="glow" size="sm" class="hidden sm:flex" @click="router.push('/filing/chat')">
        <Plus class="mr-2 h-4 w-4" />
        New Filing
      </Button>
    </div>
  </header>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { Menu, Search, Bell, Plus } from 'lucide-vue-next';
import { useAuthStore } from '@/stores/authStore';
import Button from '@/components-vue/ui/Button.vue';
import Input from '@/components-vue/ui/Input.vue';
import ModeSwitcher from '@/components-vue/adaptive/ModeSwitcher.vue';

defineEmits(['toggleSidebar']);
const router = useRouter();
const authStore = useAuthStore();
</script>
