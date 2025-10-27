<template>
  <div class="space-y-1.5">
    <div class="flex items-center gap-2">
      <Label :for="id">{{ label }}</Label>
      <Tooltip v-if="help" :content="help">
        <span class="text-muted-foreground text-xs underline decoration-dotted cursor-help">
          help
        </span>
      </Tooltip>
    </div>
    <Input
      :id="id"
      :placeholder="placeholder"
      :inputmode="type === 'number' ? 'numeric' : undefined"
      v-model="value"
      :aria-invalid="!!error"
      :aria-errormessage="error ? `${id}-error` : undefined"
    />
    <p v-if="error" :id="`${id}-error`" class="text-xs text-destructive">
      {{ error }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import Label from '@/components-vue/ui/Label.vue';
import Input from '@/components-vue/ui/Input.vue';
import Tooltip from '@/components-vue/ui/Tooltip.vue';

interface Props {
  id: string;
  label: string;
  placeholder?: string;
  help?: string;
  type?: 'text' | 'number';
  required?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  required: false,
});

const emit = defineEmits<{
  valid: [value: string | number];
}>();

const value = ref<string>('');
const error = ref<string>('');

const validate = (v: string) => {
  if (props.required && !v) return `${props.label} is required.`;
  if (props.type === 'number' && v && isNaN(Number(v))) return `${props.label} must be a number.`;
  return '';
};

watch(value, (newValue) => {
  const err = validate(newValue);
  error.value = err;
  if (!err) {
    emit('valid', props.type === 'number' ? Number(newValue) : newValue);
  }
});
</script>
