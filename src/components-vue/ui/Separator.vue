<template>
  <div :class="cn('shrink-0 bg-border h-[1px] w-full', $attrs.class)" />
</template>

<script setup lang="ts">
import { cn } from '@/lib/utils';
</script>
