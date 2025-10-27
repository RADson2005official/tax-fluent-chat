<template>
  <div :class="cn('flex w-full', isUser ? 'justify-end' : 'justify-start')">
    <Card
      :class="cn(
        'max-w-[85%] md:max-w-[70%] px-4 py-3 border transition-shadow',
        isUser
          ? 'bg-primary text-primary-foreground shadow-sm'
          : 'bg-muted text-foreground'
      )"
    >
      <div class="text-sm leading-relaxed">{{ message.content }}</div>
      <div v-if="message.explainable && !isUser" class="mt-2 flex justify-end">
        <Button size="sm" variant="glow" @click="$emit('explain', message.id)">
          <Lightbulb class="mr-2 h-4 w-4" /> Explain
        </Button>
      </div>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { cn } from '@/lib/utils';
import Card from '@/components-vue/ui/Card.vue';
import Button from '@/components-vue/ui/Button.vue';
import { Lightbulb } from 'lucide-vue-next';

export interface ChatMessage {
  id: string;
  role: 'user' | 'ai';
  content: string;
  explainable?: boolean;
}

interface Props {
  message: ChatMessage;
}

const props = defineProps<Props>();

defineEmits<{
  explain: [id: string];
}>();

const isUser = computed(() => props.message.role === 'user');
</script>
