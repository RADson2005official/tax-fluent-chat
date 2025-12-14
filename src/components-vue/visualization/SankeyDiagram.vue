<template>
  <div class="w-full h-full p-4">
    <div class="w-full relative aspect-[2/1]">
      <svg class="w-full h-full" viewBox="0 0 800 400">
        <defs>
          <linearGradient id="flowGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="hsl(var(--primary))" stop-opacity="0.5" />
            <stop offset="100%" stop-color="hsl(var(--accent))" stop-opacity="0.5" />
          </linearGradient>
          <filter id="glow">
            <feGaussianBlur stdDeviation="4" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        <!-- Paths -->
        <g class="paths">
          <!-- Salary to Gross -->
          <path
            d="M 150 100 C 250 100, 250 200, 350 200"
            fill="none"
            stroke="url(#flowGradient)"
            stroke-width="20"
            class="flow-path"
          />
          <!-- Other Income to Gross -->
          <path
            d="M 150 300 C 250 300, 250 200, 350 200"
            fill="none"
            stroke="url(#flowGradient)"
            stroke-width="10"
            class="flow-path"
          />
          <!-- Gross to Deductions -->
          <path
            d="M 450 200 C 500 200, 500 150, 550 150"
            fill="none"
            stroke="hsl(var(--destructive))"
            stroke-opacity="0.4"
            stroke-width="15"
            class="flow-path"
          />
          <!-- Gross to Taxable -->
          <path
            d="M 450 200 C 500 200, 500 250, 550 250"
            fill="none"
            stroke="url(#flowGradient)"
            stroke-width="25"
            class="flow-path"
          />
          <!-- Taxable to Tax -->
          <path
            d="M 650 250 C 700 250, 700 250, 750 250"
            fill="none"
            stroke="url(#flowGradient)"
            stroke-width="10"
            class="flow-path"
          />
        </g>

        <!-- Nodes -->
        <g class="nodes">
          <!-- Sources -->
          <foreignObject x="0" y="70" width="150" height="60">
            <div class="glass-card p-2 text-center rounded-lg border-l-4 border-primary">
              <div class="text-xs text-muted-foreground">Salary</div>
              <div class="font-bold">₹12.5L</div>
            </div>
          </foreignObject>
          <foreignObject x="0" y="270" width="150" height="60">
            <div class="glass-card p-2 text-center rounded-lg border-l-4 border-accent">
              <div class="text-xs text-muted-foreground">Other Sources</div>
              <div class="font-bold">₹1.2L</div>
            </div>
          </foreignObject>

          <!-- Gross Total -->
          <foreignObject x="350" y="170" width="100" height="60">
            <div class="glass-card p-2 text-center rounded-lg border-l-4 border-primary">
              <div class="text-xs text-muted-foreground">Gross Total</div>
              <div class="font-bold">₹13.7L</div>
            </div>
          </foreignObject>

          <!-- Deductions -->
          <foreignObject x="550" y="120" width="100" height="60">
            <div class="glass-card p-2 text-center rounded-lg border-l-4 border-destructive">
              <div class="text-xs text-muted-foreground">Deductions</div>
              <div class="font-bold">-₹2.5L</div>
            </div>
          </foreignObject>

          <!-- Taxable -->
          <foreignObject x="550" y="220" width="100" height="60">
            <div class="glass-card p-2 text-center rounded-lg border-l-4 border-primary">
              <div class="text-xs text-muted-foreground">Taxable</div>
              <div class="font-bold">₹11.2L</div>
            </div>
          </foreignObject>

          <!-- Tax -->
          <foreignObject x="700" y="220" width="100" height="60">
            <div class="glass-card p-2 text-center rounded-lg border-l-4 border-accent bg-accent/10">
              <div class="text-xs text-muted-foreground">Tax Payable</div>
              <div class="font-bold text-lg">₹1.45L</div>
            </div>
          </foreignObject>
        </g>
      </svg>
      
      <div class="absolute top-4 right-4">
        <Button size="sm" variant="outline" @click="exportChart">
          <Download class="w-4 h-4 mr-2" />
          Export Report
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Download } from 'lucide-vue-next';
import Button from '@/components-vue/ui/Button.vue';

const exportChart = () => {
  // Placeholder for export functionality
  console.log('Exporting chart...');
};
</script>

<style scoped>
.flow-path {
  transition: all 0.5s ease;
  cursor: pointer;
}
.flow-path:hover {
  stroke-opacity: 0.8;
  filter: url(#glow);
}
</style>
