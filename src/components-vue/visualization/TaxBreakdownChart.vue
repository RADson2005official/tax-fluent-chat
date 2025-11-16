<template>
  <Card class="w-full">
    <CardHeader>
      <CardTitle class="flex items-center justify-between">
        <span>Tax Breakdown</span>
        <Button size="sm" variant="outline" @click="exportChart">
          <Download class="h-4 w-4 mr-2" />
          Export
        </Button>
      </CardTitle>
    </CardHeader>
    <CardContent>
      <div ref="chartContainer" class="w-full h-64">
        <canvas ref="chartCanvas"></canvas>
      </div>
      
      <div class="mt-4 grid grid-cols-2 gap-4">
        <div class="p-3 bg-primary/10 rounded-lg">
          <p class="text-sm text-muted-foreground">Total Tax</p>
          <p class="text-2xl font-bold text-primary">${{ formatNumber(totalTax) }}</p>
        </div>
        <div class="p-3 bg-accent/10 rounded-lg">
          <p class="text-sm text-muted-foreground">Effective Rate</p>
          <p class="text-2xl font-bold text-accent">{{ effectiveRate }}%</p>
        </div>
      </div>

      <div class="mt-4 space-y-2">
        <div v-for="(bracket, index) in taxBrackets" :key="index" 
             class="flex items-center justify-between p-2 border rounded-lg hover:bg-muted/50 transition-colors">
          <div class="flex items-center gap-2">
            <div class="w-3 h-3 rounded-full" :style="{ backgroundColor: bracket.color }"></div>
            <span class="text-sm font-medium">{{ bracket.label }}</span>
          </div>
          <span class="text-sm text-muted-foreground">${{ formatNumber(bracket.amount) }}</span>
        </div>
      </div>
    </CardContent>
  </Card>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import Card from '@/components-vue/ui/Card.vue';
import CardHeader from '@/components-vue/ui/CardHeader.vue';
import CardTitle from '@/components-vue/ui/CardTitle.vue';
import CardContent from '@/components-vue/ui/CardContent.vue';
import Button from '@/components-vue/ui/Button.vue';
import { Download } from 'lucide-vue-next';

interface TaxBracket {
  label: string;
  amount: number;
  color: string;
}

interface Props {
  taxBrackets?: TaxBracket[];
  totalTax?: number;
  effectiveRate?: number;
}

const props = withDefaults(defineProps<Props>(), {
  taxBrackets: () => [],
  totalTax: 0,
  effectiveRate: 0
});

const chartCanvas = ref<HTMLCanvasElement | null>(null);
const chartContainer = ref<HTMLDivElement | null>(null);
let chartInstance: any = null;

const formatNumber = (num: number) => {
  return num.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
};

const createChart = () => {
  if (!chartCanvas.value) return;
  
  const ctx = chartCanvas.value.getContext('2d');
  if (!ctx) return;

  // Simple chart using Canvas API
  const width = chartCanvas.value.width = chartContainer.value?.clientWidth || 400;
  const height = chartCanvas.value.height = 250;
  
  ctx.clearRect(0, 0, width, height);
  
  const total = props.taxBrackets.reduce((sum, b) => sum + b.amount, 0);
  let currentAngle = -0.5 * Math.PI;
  const centerX = width / 2;
  const centerY = height / 2;
  const radius = Math.min(width, height) / 2 - 20;

  // Draw pie chart
  props.taxBrackets.forEach((bracket) => {
    const sliceAngle = (bracket.amount / total) * 2 * Math.PI;
    
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle);
    ctx.lineTo(centerX, centerY);
    ctx.fillStyle = bracket.color;
    ctx.fill();
    ctx.strokeStyle = '#fff';
    ctx.lineWidth = 2;
    ctx.stroke();
    
    currentAngle += sliceAngle;
  });

  // Draw center circle for donut effect
  ctx.beginPath();
  ctx.arc(centerX, centerY, radius * 0.6, 0, 2 * Math.PI);
  ctx.fillStyle = '#fff';
  ctx.fill();
};

const exportChart = () => {
  if (!chartCanvas.value) return;
  
  // Export as PNG
  const link = document.createElement('a');
  link.download = `tax-breakdown-${Date.now()}.png`;
  link.href = chartCanvas.value.toDataURL();
  link.click();
};

onMounted(() => {
  createChart();
});

watch(() => props.taxBrackets, () => {
  createChart();
}, { deep: true });
</script>
