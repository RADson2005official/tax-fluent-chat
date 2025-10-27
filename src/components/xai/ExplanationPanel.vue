<template>
  <Teleport to="body">
    <div
      v-if="explanationStore.isOpen"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      @click="handleClose"
    >
      <div
        class="bg-background rounded-lg shadow-lg max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto"
        @click.stop
      >
        <div class="p-6 border-b flex justify-between items-center">
          <h2 class="text-2xl font-semibold">
            {{ explanationStore.currentExplanation?.title || 'Explanation' }}
          </h2>
          <button
            @click="handleClose"
            class="text-muted-foreground hover:text-foreground transition-colors"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>
        
        <div class="p-6 space-y-4">
          <p class="text-sm">
            {{ explanationStore.currentExplanation?.content }}
          </p>
          
          <div v-if="explanationStore.currentExplanation?.key_points?.length">
            <h3 class="text-lg font-semibold mb-2">Key Points:</h3>
            <ul class="list-disc list-inside space-y-1 text-sm">
              <li v-for="point in explanationStore.currentExplanation.key_points" :key="point">
                {{ point }}
              </li>
            </ul>
          </div>
          
          <div v-if="explanationStore.currentExplanation?.related_topics?.length">
            <h3 class="text-lg font-semibold mb-2">Related Topics:</h3>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="topic in explanationStore.currentExplanation.related_topics"
                :key="topic"
                class="text-xs px-3 py-1 rounded-full bg-muted"
              >
                {{ topic }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { useExplanationStore } from '../../stores/explanation'

const explanationStore = useExplanationStore()

function handleClose() {
  explanationStore.closeExplanation()
}
</script>
