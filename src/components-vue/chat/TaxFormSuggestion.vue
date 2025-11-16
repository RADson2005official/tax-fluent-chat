<template>
  <Card class="border-2 border-dashed border-primary/30 bg-primary/5 p-4">
    <div class="flex items-start gap-3">
      <div class="flex-shrink-0">
        <div class="h-10 w-10 bg-primary/10 rounded-lg flex items-center justify-center">
          <FileText class="h-5 w-5 text-primary" />
        </div>
      </div>

      <div class="flex-1 min-w-0">
        <div class="flex items-center gap-2 mb-2">
          <h4 class="font-semibold text-sm">Form Suggestion</h4>
          <Badge :class="getConfidenceClasses(suggestion.confidence)">
            <component :is="getConfidenceIcon(suggestion.confidence)" class="h-4 w-4" />
            <span class="ml-1">{{ Math.round(suggestion.confidence * 100) }}% confident</span>
          </Badge>
        </div>

        <p class="text-sm text-muted-foreground mb-3">
          Based on our conversation, I can help you fill out the <strong>{{ suggestion.formName }}</strong> ({{ suggestion.formType }}).
        </p>

        <p class="text-xs text-muted-foreground mb-3 italic">
          "{{ suggestion.reason }}"
        </p>

        <div v-if="isExpanded" class="mb-3 p-3 bg-background rounded-lg border">
          <h5 class="font-medium text-sm mb-2">Suggested Values:</h5>
          <div class="space-y-1 text-xs">
            <div v-for="(value, field) in suggestion.suggestedFields" :key="field" class="flex justify-between">
              <span class="text-muted-foreground">{{ field }}:</span>
              <span class="font-mono">{{ value }}</span>
            </div>
          </div>
        </div>

        <div class="flex gap-2">
          <Button
            size="sm"
            @click="isExpanded = !isExpanded"
            variant="outline"
          >
            {{ isExpanded ? 'Hide Details' : 'Show Details' }}
          </Button>

          <Button
            size="sm"
            @click="$emit('accept', suggestion)"
            class="bg-primary hover:bg-primary/90"
          >
            <Zap class="h-4 w-4 mr-2" />
            Fill Form
          </Button>

          <Button
            size="sm"
            @click="$emit('dismiss', suggestion.id)"
            variant="ghost"
          >
            Dismiss
          </Button>
        </div>
      </div>
    </div>
  </Card>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import Card from '@/components-vue/ui/Card.vue';
import Button from '@/components-vue/ui/Button.vue';
import Badge from '@/components-vue/ui/Badge.vue';
import { FileText, CheckCircle, AlertCircle, Zap } from 'lucide-vue-next';

export interface TaxFormSuggestion {
  id: string;
  formType: string;
  formName: string;
  confidence: number;
  suggestedFields: Record<string, any>;
  reason: string;
}

interface Props {
  suggestion: TaxFormSuggestion;
}

const props = defineProps<Props>();
const isExpanded = ref(false);

defineEmits<{
  accept: [suggestion: TaxFormSuggestion];
  dismiss: [id: string];
}>();

const getConfidenceClasses = (confidence: number) => {
  if (confidence >= 0.8) return "bg-green-100 text-green-800 border-green-200";
  if (confidence >= 0.6) return "bg-yellow-100 text-yellow-800 border-yellow-200";
  return "bg-red-100 text-red-800 border-red-200";
};

const getConfidenceIcon = (confidence: number) => {
  if (confidence >= 0.8) return CheckCircle;
  return AlertCircle;
};
</script>