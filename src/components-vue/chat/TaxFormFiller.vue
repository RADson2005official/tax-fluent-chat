<template>
  <Dialog :open="open" @update:open="$emit('update:open', $event)">
    <DialogContent class="max-w-4xl max-h-[80vh] overflow-y-auto">
      <DialogHeader>
        <DialogTitle class="flex items-center gap-2">
          <FileText class="h-5 w-5" />
          {{ suggestion?.formName }} ({{ suggestion?.formType }})
        </DialogTitle>
        <DialogDescription>
          Fill out this tax form based on your conversation. Pre-filled values are suggested based on what you've told me.
        </DialogDescription>
      </DialogHeader>

      <div class="space-y-6 py-4">
        <!-- Form Fields -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div
            v-for="(value, field) in formData"
            :key="field"
            class="space-y-2"
          >
            <Label :for="field" class="text-sm font-medium">
              {{ field }}
              <span v-if="isSuggestedField(field)" class="text-xs text-primary ml-1">(suggested)</span>
            </Label>
            <Input
              :id="field"
              :value="value"
              @input="(e) => updateField(field, (e.target as HTMLInputElement).value)"
              :class="isSuggestedField(field) ? 'border-primary/50 bg-primary/5' : ''"
              placeholder="Enter value..."
            />
          </div>
        </div>

        <!-- Add New Field -->
        <div class="border-t pt-4">
          <div class="flex gap-2">
            <Input
              v-model="newFieldName"
              placeholder="Add new field name..."
              class="flex-1"
            />
            <Input
              v-model="newFieldValue"
              placeholder="Field value..."
              class="flex-1"
            />
            <Button @click="addField" :disabled="!newFieldName.trim()">
              <Plus class="h-4 w-4 mr-2" />
              Add Field
            </Button>
          </div>
        </div>

        <!-- Form Actions -->
        <div class="flex gap-2 pt-4 border-t">
          <Button @click="saveForm" class="flex-1">
            <Save class="h-4 w-4 mr-2" />
            Save Form
          </Button>
          <Button @click="validateForm" variant="outline">
            <CheckCircle class="h-4 w-4 mr-2" />
            Validate
          </Button>
          <Button @click="exportForm" variant="outline">
            <Download class="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>

        <!-- Validation Results -->
        <div v-if="validationResults.length > 0" class="border-t pt-4">
          <h4 class="font-medium mb-2">Validation Results:</h4>
          <div class="space-y-1">
            <div
              v-for="result in validationResults"
              :key="result.field"
              :class="[
                'text-sm p-2 rounded',
                result.valid ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
              ]"
            >
              {{ result.field }}: {{ result.message }}
            </div>
          </div>
        </div>
      </div>

      <DialogFooter>
        <Button variant="outline" @click="$emit('update:open', false)">
          Close
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import Dialog from '@/components-vue/ui/Dialog.vue';
import { DialogContent } from 'radix-vue';
import DialogHeader from '@/components-vue/ui/DialogHeader.vue';
import DialogTitle from '@/components-vue/ui/DialogTitle.vue';
import DialogDescription from '@/components-vue/ui/DialogDescription.vue';
import DialogFooter from '@/components-vue/ui/DialogFooter.vue';
import Button from '@/components-vue/ui/Button.vue';
import Input from '@/components-vue/ui/Input.vue';
import Label from '@/components-vue/ui/Label.vue';
import { FileText, Plus, Save, CheckCircle, Download } from 'lucide-vue-next';
import type { TaxFormSuggestion } from '@/agents/types';

interface Props {
  open: boolean;
  suggestion?: TaxFormSuggestion;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  'update:open': [value: boolean];
}>();

const formData = ref<Record<string, string>>({});
const newFieldName = ref('');
const newFieldValue = ref('');
const validationResults = ref<Array<{field: string, valid: boolean, message: string}>>([]);

// Initialize form data when suggestion changes
watch(() => props.suggestion, (newSuggestion) => {
  if (newSuggestion) {
    formData.value = { ...newSuggestion.suggestedFields };
  }
}, { immediate: true });

const isSuggestedField = (field: string) => {
  return props.suggestion?.suggestedFields && field in props.suggestion.suggestedFields;
};

const updateField = (field: string, value: string) => {
  formData.value[field] = value;
};

const addField = () => {
  if (newFieldName.value.trim()) {
    formData.value[newFieldName.value.trim()] = newFieldValue.value;
    newFieldName.value = '';
    newFieldValue.value = '';
  }
};

const validateForm = () => {
  validationResults.value = [];

  Object.entries(formData.value).forEach(([field, value]) => {
    const isValid = value.trim().length > 0;
    validationResults.value.push({
      field,
      valid: isValid,
      message: isValid ? 'Valid' : 'Field cannot be empty'
    });
  });
};

const saveForm = () => {
  console.log('Saving form:', {
    formType: props.suggestion?.formType,
    formData: formData.value
  });
  // TODO: Save to backend or local storage
  emit('update:open', false);
};

const exportForm = () => {
  const dataStr = JSON.stringify({
    formType: props.suggestion?.formType,
    formName: props.suggestion?.formName,
    data: formData.value,
    exportedAt: new Date().toISOString()
  }, null, 2);

  const dataBlob = new Blob([dataStr], { type: 'application/json' });
  const url = URL.createObjectURL(dataBlob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `${props.suggestion?.formType || 'form'}.json`;
  link.click();
  URL.revokeObjectURL(url);
};
</script>