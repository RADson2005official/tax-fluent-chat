<script setup lang="ts">
import Card from '@/components-vue/ui/Card.vue'
import CardHeader from '@/components-vue/ui/CardHeader.vue'
import CardTitle from '@/components-vue/ui/CardTitle.vue'
import CardContent from '@/components-vue/ui/CardContent.vue'

const props = defineProps<{
  title?: string
  variant?: string
  class?: string
}>()
</script>

<template>
  <Card :class="props.class">
    <CardHeader v-if="title" class="pb-2">
      <CardTitle>{{ title }}</CardTitle>
    </CardHeader>
    <CardContent>
      <slot />
    </CardContent>
  </Card>
</template>
