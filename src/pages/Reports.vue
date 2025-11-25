<template>
  <div class="p-8 space-y-8">
    <div class="flex justify-between items-center print:hidden">
      <div class="flex items-center gap-4">
        <BackButton />
        <h1 class="text-3xl font-bold">Tax Reports</h1>
      </div>
      <Button variant="outline" @click="printReport">
        <Printer class="mr-2 h-4 w-4" />
        Print Report
      </Button>
    </div>

    <!-- Report Content -->
    <div class="space-y-6 print:space-y-4" id="printable-report">
      <!-- Header for Print -->
      <div class="hidden print:block text-center mb-8 border-b pb-4">
        <h1 class="text-2xl font-bold">TaxFluent Annual Tax Report</h1>
        <p class="text-sm text-gray-500">Assessment Year 2024-25</p>
      </div>

      <!-- Financial Summary Cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 print:grid-cols-3">
        <Card class="bg-blue-50/50 border-blue-100">
          <CardHeader>
            <CardTitle class="text-sm font-medium text-blue-600">Total Income</CardTitle>
            <div class="text-2xl font-bold text-blue-900">₹15,00,000</div>
          </CardHeader>
        </Card>
        <Card class="bg-green-50/50 border-green-100">
          <CardHeader>
            <CardTitle class="text-sm font-medium text-green-600">Total Deductions</CardTitle>
            <div class="text-2xl font-bold text-green-900">₹2,50,000</div>
          </CardHeader>
        </Card>
        <Card class="bg-purple-50/50 border-purple-100">
          <CardHeader>
            <CardTitle class="text-sm font-medium text-purple-600">Net Taxable Income</CardTitle>
            <div class="text-2xl font-bold text-purple-900">₹12,50,000</div>
          </CardHeader>
        </Card>
      </div>

      <!-- Detailed Breakdown -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 print:grid-cols-2">
        <!-- Income Sources -->
        <Card>
          <CardHeader>
            <CardTitle>Income Sources</CardTitle>
          </CardHeader>
          <CardContent>
            <div class="space-y-4">
              <div class="flex justify-between items-center py-2 border-b last:border-0">
                <span class="text-muted-foreground">Salary (Gross)</span>
                <span class="font-medium">₹14,50,000</span>
              </div>
              <div class="flex justify-between items-center py-2 border-b last:border-0">
                <span class="text-muted-foreground">Interest Income</span>
                <span class="font-medium">₹35,000</span>
              </div>
              <div class="flex justify-between items-center py-2 border-b last:border-0">
                <span class="text-muted-foreground">Capital Gains</span>
                <span class="font-medium">₹15,000</span>
              </div>
              <div class="flex justify-between items-center pt-4 border-t font-semibold">
                <span>Total Gross Income</span>
                <span>₹15,00,000</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <!-- Deductions -->
        <Card>
          <CardHeader>
            <CardTitle>Deductions Claimed</CardTitle>
          </CardHeader>
          <CardContent>
            <div class="space-y-4">
              <div class="flex justify-between items-center py-2 border-b last:border-0">
                <span class="text-muted-foreground">Section 80C (LIC, PPF)</span>
                <span class="font-medium">₹1,50,000</span>
              </div>
              <div class="flex justify-between items-center py-2 border-b last:border-0">
                <span class="text-muted-foreground">Standard Deduction</span>
                <span class="font-medium">₹50,000</span>
              </div>
              <div class="flex justify-between items-center py-2 border-b last:border-0">
                <span class="text-muted-foreground">Section 80D (Health Ins)</span>
                <span class="font-medium">₹25,000</span>
              </div>
              <div class="flex justify-between items-center py-2 border-b last:border-0">
                <span class="text-muted-foreground">HRA Exemption</span>
                <span class="font-medium">₹25,000</span>
              </div>
              <div class="flex justify-between items-center pt-4 border-t font-semibold">
                <span>Total Deductions</span>
                <span>₹2,50,000</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <!-- Tax Calculation -->
      <Card class="border-primary/20 bg-primary/5">
        <CardHeader>
          <CardTitle>Tax Calculation</CardTitle>
        </CardHeader>
        <CardContent>
          <div class="space-y-2">
            <div class="flex justify-between items-center">
              <span class="text-muted-foreground">Tax on Income</span>
              <span class="font-medium">₹1,12,500</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-muted-foreground">Health & Education Cess (4%)</span>
              <span class="font-medium">₹4,500</span>
            </div>
            <div class="flex justify-between items-center pt-4 border-t text-lg font-bold text-primary">
              <span>Total Tax Payable</span>
              <span>₹1,17,000</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Printer } from 'lucide-vue-next'
import BackButton from '@/components-vue/navigation/BackButton.vue'
import Button from '@/components-vue/ui/Button.vue'
import Card from '@/components-vue/ui/Card.vue'
import CardHeader from '@/components-vue/ui/CardHeader.vue'
import CardTitle from '@/components-vue/ui/CardTitle.vue'
import CardContent from '@/components-vue/ui/CardContent.vue'

const printReport = () => {
  window.print()
}
</script>

<style scoped>
@media print {
  @page {
    margin: 2cm;
  }
}
</style>
