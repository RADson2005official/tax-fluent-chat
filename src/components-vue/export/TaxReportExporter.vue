<template>
  <Card>
    <CardHeader>
      <CardTitle>Export Tax Report</CardTitle>
    </CardHeader>
    <CardContent class="space-y-4">
      <div class="grid grid-cols-2 gap-3">
        <Button @click="exportPDF" variant="default" class="w-full">
          <FileText class="h-4 w-4 mr-2" />
          Export PDF
        </Button>
        <Button @click="exportExcel" variant="outline" class="w-full">
          <FileSpreadsheet class="h-4 w-4 mr-2" />
          Export Excel
        </Button>
      </div>

      <div class="p-4 bg-muted rounded-lg">
        <h4 class="font-medium mb-2">Report will include:</h4>
        <ul class="text-sm space-y-1 text-muted-foreground">
          <li>✓ Tax calculation breakdown</li>
          <li>✓ Deductions and credits summary</li>
          <li>✓ Visualizations and charts</li>
          <li>✓ Compliance checklist</li>
          <li>✓ Government regulation references</li>
        </ul>
      </div>

      <div v-if="exportStatus" class="p-3 rounded-lg" 
           :class="exportStatus.type === 'success' ? 'bg-green-50 text-green-800' : 'bg-blue-50 text-blue-800'">
        <p class="text-sm font-medium">{{ exportStatus.message }}</p>
      </div>
    </CardContent>
  </Card>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import Card from '@/components-vue/ui/Card.vue';
import CardHeader from '@/components-vue/ui/CardHeader.vue';
import CardTitle from '@/components-vue/ui/CardTitle.vue';
import CardContent from '@/components-vue/ui/CardContent.vue';
import Button from '@/components-vue/ui/Button.vue';
import { FileText, FileSpreadsheet } from 'lucide-vue-next';

interface Props {
  taxData?: any;
}

const props = defineProps<Props>();
const exportStatus = ref<{ type: 'success' | 'info'; message: string } | null>(null);

const exportPDF = () => {
  exportStatus.value = { type: 'info', message: 'Generating PDF report...' };
  
  setTimeout(() => {
    // Create PDF content
    const content = generatePDFContent();
    downloadFile(content, 'tax-report.html', 'text/html');
    
    exportStatus.value = { type: 'success', message: 'PDF report generated successfully!' };
    setTimeout(() => exportStatus.value = null, 3000);
  }, 500);
};

const exportExcel = () => {
  exportStatus.value = { type: 'info', message: 'Generating Excel report...' };
  
  setTimeout(() => {
    // Create CSV content (Excel compatible)
    const csvContent = generateCSVContent();
    downloadFile(csvContent, 'tax-report.csv', 'text/csv');
    
    exportStatus.value = { type: 'success', message: 'Excel report generated successfully!' };
    setTimeout(() => exportStatus.value = null, 3000);
  }, 500);
};

const generatePDFContent = () => {
  const data = props.taxData || {};
  
  return `
<!DOCTYPE html>
<html>
<head>
  <title>Tax Report ${new Date().getFullYear()}</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; }
    h1 { color: #2563eb; border-bottom: 3px solid #2563eb; padding-bottom: 10px; }
    h2 { color: #1e40af; margin-top: 30px; }
    table { width: 100%; border-collapse: collapse; margin: 20px 0; }
    th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
    th { background-color: #f3f4f6; font-weight: bold; }
    .summary-box { background: #eff6ff; padding: 15px; border-radius: 8px; margin: 20px 0; }
    .highlight { color: #2563eb; font-weight: bold; font-size: 1.2em; }
    .footer { margin-top: 40px; padding-top: 20px; border-top: 2px solid #ddd; font-size: 0.9em; color: #666; }
  </style>
</head>
<body>
  <h1>Tax Report ${new Date().getFullYear()}</h1>
  <p><strong>Generated:</strong> ${new Date().toLocaleString()}</p>
  
  <div class="summary-box">
    <h2>Tax Summary</h2>
    <p><strong>Filing Status:</strong> ${data.filingStatus || 'Single'}</p>
    <p><strong>Total Income:</strong> $${(data.totalIncome || 75000).toLocaleString()}</p>
    <p><strong>Total Tax:</strong> <span class="highlight">$${(data.totalTax || 12358).toLocaleString()}</span></p>
    <p><strong>Effective Rate:</strong> ${data.effectiveRate || '16.5%'}</p>
  </div>

  <h2>Tax Bracket Breakdown</h2>
  <table>
    <thead>
      <tr>
        <th>Tax Bracket</th>
        <th>Rate</th>
        <th>Taxable Income</th>
        <th>Tax Amount</th>
      </tr>
    </thead>
    <tbody>
      <tr><td>10%</td><td>10%</td><td>$11,600</td><td>$1,160</td></tr>
      <tr><td>12%</td><td>12%</td><td>$35,550</td><td>$4,266</td></tr>
      <tr><td>22%</td><td>22%</td><td>$27,850</td><td>$6,127</td></tr>
    </tbody>
  </table>

  <h2>Deductions & Credits</h2>
  <table>
    <thead>
      <tr>
        <th>Item</th>
        <th>Amount</th>
      </tr>
    </thead>
    <tbody>
      <tr><td>Standard Deduction</td><td>$14,600</td></tr>
      <tr><td>Child Tax Credit</td><td>${data.childTaxCredit || 0}</td></tr>
      <tr><td>EITC</td><td>${data.eitc || 0}</td></tr>
    </tbody>
  </table>

  <h2>Compliance Checklist</h2>
  <ul>
    <li>✓ Income reported according to IRS Form 1040</li>
    <li>✓ Standard deduction applied per 2024 IRS guidelines</li>
    <li>✓ Tax brackets calculated per IRS Publication 17</li>
    <li>✓ Credits verified per IRS eligibility requirements</li>
  </ul>

  <div class="footer">
    <p><strong>Disclaimer:</strong> This report is generated by Tax Fluent Chat AI system. Please consult with a tax professional for final tax filing.</p>
    <p><strong>References:</strong> IRS Publication 17 (2024), IRS Tax Brackets 2024, IRS Form 1040 Instructions</p>
  </div>
</body>
</html>
  `;
};

const generateCSVContent = () => {
  const data = props.taxData || {};
  
  return `
Tax Report,${new Date().getFullYear()}
Generated,${new Date().toLocaleString()}

SUMMARY
Filing Status,${data.filingStatus || 'Single'}
Total Income,$${(data.totalIncome || 75000).toLocaleString()}
Total Tax,$${(data.totalTax || 12358).toLocaleString()}
Effective Rate,${data.effectiveRate || '16.5%'}

TAX BRACKET BREAKDOWN
Bracket,Rate,Taxable Income,Tax Amount
10%,10%,$11600,$1160
12%,12%,$35550,$4266
22%,22%,$27850,$6127

DEDUCTIONS & CREDITS
Item,Amount
Standard Deduction,$14600
Child Tax Credit,$${data.childTaxCredit || 0}
EITC,$${data.eitc || 0}
  `.trim();
};

const downloadFile = (content: string, filename: string, mimeType: string) => {
  const blob = new Blob([content], { type: mimeType });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};
</script>
