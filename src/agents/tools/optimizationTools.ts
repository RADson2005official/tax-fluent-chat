import type { Tool } from '../types';

export const optimizationTools: Tool[] = [
  {
    name: 'compare_deduction_methods',
    description: 'Compare standard vs itemized deductions',
    parameters: [
      { name: 'filingStatus', type: 'string', description: 'Filing status', required: true },
      { name: 'itemizedDeductions', type: 'object', description: 'Itemized deductions', required: true }
    ],
    execute: async (params: Record<string, any>) => {
      const { filingStatus, itemizedDeductions } = params;
      
      const standardAmounts: Record<string, number> = {
        single: 14600,
        married_joint: 29200,
        married_separate: 14600,
        head_of_household: 21900
      };

      const standardDeduction = standardAmounts[filingStatus] || 14600;
      const itemizedTotal = Object.values(itemizedDeductions).reduce((sum: number, val) => sum + (Number(val) || 0), 0) as number;

      return {
        standardDeduction,
        itemizedTotal,
        recommendation: itemizedTotal > standardDeduction ? 'itemized' : 'standard',
        savings: Math.abs(itemizedTotal - standardDeduction)
      };
    }
  },
  {
    name: 'find_eligible_credits',
    description: 'Identify all eligible tax credits',
    parameters: [
      { name: 'taxContext', type: 'object', description: 'Complete tax context', required: true }
    ],
    execute: async (params: Record<string, any>) => {
      const { taxContext } = params;
      const eligibleCredits: any[] = [];

      if (taxContext.dependents > 0) {
        eligibleCredits.push({
          name: 'Child Tax Credit',
          estimatedAmount: taxContext.dependents * 2000,
          confidence: 0.95
        });
      }

      if (taxContext.income?.total < 60000 && taxContext.income?.earned > 0) {
        eligibleCredits.push({
          name: 'Earned Income Tax Credit',
          estimatedAmount: 3000,
          confidence: 0.80
        });
      }

      return {
        eligibleCredits,
        totalPotentialSavings: eligibleCredits.reduce((sum, c) => sum + c.estimatedAmount, 0)
      };
    }
  },
  {
    name: 'analyze_timing',
    description: 'Analyze income and deduction timing strategies',
    parameters: [
      { name: 'currentYear', type: 'object', description: 'Current year tax data', required: true },
      { name: 'projectedNextYear', type: 'object', description: 'Next year projections', required: false }
    ],
    execute: async (params: Record<string, any>) => {
      const { currentYear, projectedNextYear } = params;
      const recommendations: string[] = [];

      if (currentYear.income > 100000 && projectedNextYear?.income < 80000) {
        recommendations.push('Consider deferring income to next year when you may be in a lower tax bracket');
      }

      if (currentYear.deductions < 10000) {
        recommendations.push('Consider bunching deductions into alternate years');
      }

      return { recommendations, strategyCount: recommendations.length };
    }
  }
];
