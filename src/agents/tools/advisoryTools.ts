import type { Tool } from '../types';

export const advisoryTools: Tool[] = [
  {
    name: 'analyze_tax_situation',
    description: 'Comprehensive analysis of tax situation',
    parameters: [
      { name: 'taxContext', type: 'object', description: 'Complete tax context', required: true }
    ],
    execute: async (params: Record<string, any>) => {
      const { taxContext } = params;
      
      const insights = [];
      
      if (taxContext.income?.w2?.length > 1) {
        insights.push('Multiple W-2 forms detected - ensure all income is reported');
      }

      if (taxContext.deductions?.itemized?.total > taxContext.deductions?.standard) {
        insights.push('Itemizing deductions will save you money');
      } else {
        insights.push('Standard deduction is optimal for your situation');
      }

      return {
        insights,
        riskLevel: 'low',
        confidenceScore: 0.85
      };
    }
  },
  {
    name: 'recommend_strategies',
    description: 'Recommend tax-saving strategies',
    parameters: [
      { name: 'taxContext', type: 'object', description: 'Tax context', required: true }
    ],
    execute: async (params: Record<string, any>) => {
      const { taxContext } = params;
      const strategies: any[] = [];

      if (taxContext.income?.total > 50000) {
        strategies.push({
          strategy: 'Maximize retirement contributions',
          potentialSavings: 1200,
          difficulty: 'easy',
          description: 'Contributing to an IRA or 401(k) can reduce taxable income'
        });
      }

      if (taxContext.dependents > 0) {
        strategies.push({
          strategy: 'Utilize dependent care FSA',
          potentialSavings: 500,
          difficulty: 'moderate',
          description: 'Pre-tax dependent care account'
        });
      }

      return { strategies, recommendedActions: strategies.length };
    }
  },
  {
    name: 'explain_concept',
    description: 'Explain tax concepts in simple terms',
    parameters: [
      { name: 'concept', type: 'string', description: 'Tax concept to explain', required: true },
      { name: 'complexity', type: 'string', description: 'simple, moderate, or detailed', required: false }
    ],
    execute: async (params: Record<string, any>) => {
      const { concept, complexity = 'simple' } = params;
      
      const explanations: Record<string, any> = {
        'agi': {
          simple: 'AGI is your total income minus certain deductions',
          moderate: 'Adjusted Gross Income is calculated by taking your total income and subtracting specific deductions like IRA contributions',
          detailed: 'AGI = Gross Income - Above-the-line deductions. Used to determine eligibility for credits and deductions'
        },
        'standard_deduction': {
          simple: 'A fixed amount that reduces your taxable income',
          moderate: 'The standard deduction is a set dollar amount that reduces your taxable income based on your filing status',
          detailed: 'Standard deduction for 2024: Single $14,600, Married Joint $29,200. Alternative to itemizing deductions'
        }
      };

      const explanation = explanations[concept.toLowerCase()]?.[complexity] || 'Concept not found';

      return { concept, explanation, complexity };
    }
  }
];
