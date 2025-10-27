<template>
  <div class="w-full">
    <div class="flex items-center gap-2">
      <Tooltip content="Attach documents">
        <Button variant="soft" size="icon" aria-label="Attach file">
          <Paperclip class="h-4 w-4" />
        </Button>
      </Tooltip>

      <Input
        v-model="value"
        :placeholder="placeholderText"
        class="flex-1"
        @keydown.enter="handleSend"
      />

      <Tooltip content="Voice input coming soon">
        <Button variant="soft" size="icon" aria-label="Voice input (coming soon)" :disabled="true">
          <Mic class="h-4 w-4" />
        </Button>
      </Tooltip>

      <Button variant="hero" @click="handleSend" :disabled="disabled" aria-label="Send message">
        <Send class="mr-2 h-4 w-4" /> Send
      </Button>
    </div>

    <div v-if="suggestions.length > 0" class="mt-2 flex flex-wrap gap-2">
      <Button
        v-for="s in suggestions"
        :key="s"
        size="sm"
        variant="soft"
        @click="() => { value = s; handleSend(); }"
      >
        {{ s }}
      </Button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import Button from '@/components-vue/ui/Button.vue';
import Input from '@/components-vue/ui/Input.vue';
import Tooltip from '@/components-vue/ui/Tooltip.vue';
import { Mic, Send, Paperclip } from 'lucide-vue-next';

type Mode = 'Novice' | 'Expert' | 'Accessibility';

interface Props {
  disabled?: boolean;
  suggestions?: string[];
  mode?: Mode;
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
  suggestions: () => [],
  mode: 'Novice',
});

const emit = defineEmits<{
  send: [message: string];
}>();

const value = ref('');

const placeholderText = computed(() => {
  if (props.mode === 'Novice') {
    return 'Ask in plain language: e.g., Do I qualify for the child tax credit?';
  } else if (props.mode === 'Expert') {
    return 'Type commands or forms: e.g., compute itemized deduction with SALT cap';
  } else {
    return 'Write or dictate your question';
  }
});

const handleSend = () => {
  const v = value.value.trim();
  if (!v) return;
  emit('send', v);
  value.value = '';
};
</script>
