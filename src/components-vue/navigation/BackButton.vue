<template>
  <Button variant="ghost" size="sm" class="gap-2 mb-4 pl-0 hover:pl-2 transition-all" @click="goBack">
    <ArrowLeft class="h-4 w-4" />
    Back
  </Button>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { ArrowLeft } from 'lucide-vue-next'
import Button from '@/components-vue/ui/Button.vue'

const router = useRouter()

const goBack = () => {
  router.back()
}
</script>
