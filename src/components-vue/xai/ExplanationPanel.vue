<template>
  <Dialog :open="open" @update:open="$emit('update:open', $event)">
    <DialogHeader>
      <DialogTitle>Why the AI said that</DialogTitle>
    </DialogHeader>
    <ScrollArea class="max-h-[60vh] pr-4">
      <div class="prose prose-sm dark:prose-invert">
        <p>{{ content }}</p>
        <ul>
          <li>Attribution to your inputs</li>
          <li>Referenced rules and thresholds</li>
          <li>Confidence and alternatives</li>
        </ul>
      </div>
    </ScrollArea>
  </Dialog>
</template>

<script setup lang="ts">
import Dialog from '@/components-vue/ui/Dialog.vue';
import DialogHeader from '@/components-vue/ui/DialogHeader.vue';
import DialogTitle from '@/components-vue/ui/DialogTitle.vue';
import ScrollArea from '@/components-vue/ui/ScrollArea.vue';

interface Props {
  open: boolean;
  content: string;
}

defineProps<Props>();

defineEmits<{
  'update:open': [value: boolean];
}>();
</script>
