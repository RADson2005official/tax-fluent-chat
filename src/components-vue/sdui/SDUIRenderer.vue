<script setup lang="ts">
import { computed } from 'vue'
import SDUIButton from './SDUIButton.vue'
import SDUICard from './SDUICard.vue'
import SDUIHeader from './SDUIHeader.vue'
import SDUIText from './SDUIText.vue'
import StatCard from './StatCard.vue'
import ActivityList from './ActivityList.vue'
import SankeyDiagram from '@/components-vue/visualization/SankeyDiagram.vue'

defineOptions({
  name: 'SDUIRenderer'
})

interface UIComponent {
  type: string
  props?: Record<string, any>
  children?: UIComponent[]
}

const props = defineProps<{
  component: UIComponent
}>()

const componentMap: Record<string, any> = {
  Header: SDUIHeader,
  Card: SDUICard,
  Button: SDUIButton,
  Text: SDUIText,
  StatCard: StatCard,
  ActivityList: ActivityList,
  SankeyDiagram: SankeyDiagram
}

const resolvedComponent = computed(() => {
  return componentMap[props.component.type] || 'div'
})
</script>

<template>
  <component 
    :is="resolvedComponent" 
    v-bind="component.props"
  >
    <template v-if="component.children && component.children.length">
      <SDUIRenderer 
        v-for="(child, index) in component.children" 
        :key="index" 
        :component="child" 
      />
    </template>
  </component>
</template>
