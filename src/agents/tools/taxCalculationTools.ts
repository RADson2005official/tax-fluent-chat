import type { Tool } from '../types';

// Tax brackets for 2024
const TAX_BRACKETS_2024 = {
  single: [
    { min: 0, max: 11600, rate: 0.10 },
    { min: 11601, max: 47150, rate: 0.12 },
    { min: 47151, max: 100525, rate: 0.22 },
    { min: 100526, max: 191950, rate: 0.24 },
    { min: 191951, max: 243725, rate: 0.32 },
    { min: 243726, max: 609350, rate: 0.35 },
    { min: 609351, max: Infinity, rate: 0.37 }
  ],
  married_joint: [
    { min: 0, max: 23200, rate: 0.10 },
    { min: 23201, max: 94300, rate: 0.12 },
    { min: 94301, max: 201050, rate: 0.22 },
    { min: 201051, max: 383900, rate: 0.24 },
    { min: 383901, max: 487450, rate: 0.32 },
    { min: 487451, max: 731200, rate: 0.35 },
    { min: 731201, max: Infinity, rate: 0.37 }
  ],
  married_separate: [
    { min: 0, max: 11600, rate: 0.10 },
    { min: 11601, max: 47150, rate: 0.12 },
    { min: 47151, max: 100525, rate: 0.22 },
    { min: 100526, max: 191950, rate: 0.24 },
    { min: 191951, max: 243725, rate: 0.32 },
    { min: 243726, max: 365600, rate: 0.35 },
    { min: 365601, max: Infinity, rate: 0.37 }
  ],
  head_of_household: [
    { min: 0, max: 16550, rate: 0.10 },
    { min: 16551, max: 63100, rate: 0.12 },
    { min: 63101, max: 100500, rate: 0.22 },
    { min: 100501, max: 191950, rate: 0.24 },
    { min: 191951, max: 243700, rate: 0.32 },
    { min: 243701, max: 609350, rate: 0.35 },
    { min: 609351, max: Infinity, rate: 0.37 }
  ]
};

const STANDARD_DEDUCTIONS_2024 = {
  single: 14600,
  married_joint: 29200,
  married_separate: 14600,
  head_of_household: 21900,
  qualifying_widow: 29200
};

export const taxCalculationTools: Tool[] = [
  {
    name: 'calculate_income_tax',
    description: 'Calculate federal income tax based on taxable income and filing status',
    parameters: [
      { name: 'taxableIncome', type: 'number', description: 'Taxable income amount', required: true },
      { name: 'filingStatus', type: 'string', description: 'Filing status (single, married_joint, etc.)', required: true }
    ],
    execute: async (params: Record<string, any>) => {
      const { taxableIncome, filingStatus } = params;
      const brackets = TAX_BRACKETS_2024[filingStatus as keyof typeof TAX_BRACKETS_2024] || TAX_BRACKETS_2024.single;
      
      let tax = 0;
      let previousMax = 0;
      const breakdown: any[] = [];

      for (const bracket of brackets) {
        if (taxableIncome > bracket.min) {
          const taxableInBracket = Math.min(taxableIncome, bracket.max) - bracket.min + 1;
          const taxInBracket = taxableInBracket * bracket.rate;
          tax += taxInBracket;
          
          breakdown.push({
            bracket: `${bracket.rate * 100}%`,
            min: bracket.min,
            max: bracket.max === Infinity ? 'and above' : bracket.max,
            taxableAmount: taxableInBracket,
            tax: taxInBracket
          });

          if (taxableIncome <= bracket.max) break;
          previousMax = bracket.max;
        }
      }

      return {
        totalTax: Math.round(tax * 100) / 100,
        breakdown,
        effectiveRate: (tax / taxableIncome * 100).toFixed(2) + '%',
        marginalRate: (breakdown[breakdown.length - 1]?.bracket || '0%')
      };
    }
  },
  {
    name: 'calculate_agi',
    description: 'Calculate Adjusted Gross Income from total income and above-the-line deductions',
    parameters: [
      { name: 'totalIncome', type: 'number', description: 'Total income from all sources', required: true },
      { name: 'aboveLineDeductions', type: 'object', description: 'Above-the-line deductions', required: false }
    ],
    execute: async (params: Record<string, any>) => {
      const { totalIncome, aboveLineDeductions = {} } = params;
      
      const deductions = {
        studentLoanInterest: aboveLineDeductions.studentLoanInterest || 0,
        iraContributions: aboveLineDeductions.iraContributions || 0,
        healthSavingsAccount: aboveLineDeductions.healthSavingsAccount || 0,
        selfEmploymentTax: aboveLineDeductions.selfEmploymentTax || 0,
        other: aboveLineDeductions.other || 0
      };

      const totalDeductions = Object.values(deductions).reduce((sum, val) => sum + (val as number), 0);
      const agi = totalIncome - totalDeductions;

      return {
        agi: Math.round(agi * 100) / 100,
        totalIncome,
        totalDeductions,
        deductionBreakdown: deductions
      };
    }
  },
  {
    name: 'calculate_taxable_income',
    description: 'Calculate taxable income from AGI, deductions, and exemptions',
    parameters: [
      { name: 'agi', type: 'number', description: 'Adjusted Gross Income', required: true },
      { name: 'filingStatus', type: 'string', description: 'Filing status', required: true },
      { name: 'itemizedDeductions', type: 'number', description: 'Total itemized deductions', required: false }
    ],
    execute: async (params: Record<string, any>) => {
      const { agi, filingStatus, itemizedDeductions = 0 } = params;
      
      const standardDeduction = STANDARD_DEDUCTIONS_2024[filingStatus as keyof typeof STANDARD_DEDUCTIONS_2024] || STANDARD_DEDUCTIONS_2024.single;
      const deduction = Math.max(standardDeduction, itemizedDeductions);
      const deductionType = deduction === standardDeduction ? 'standard' : 'itemized';
      
      const taxableIncome = Math.max(0, agi - deduction);

      return {
        taxableIncome: Math.round(taxableIncome * 100) / 100,
        agi,
        deductionUsed: deduction,
        deductionType,
        standardDeduction,
        itemizedDeductions
      };
    }
  },
  {
    name: 'calculate_child_tax_credit',
    description: 'Calculate Child Tax Credit based on number of qualifying children and income',
    parameters: [
      { name: 'dependents', type: 'number', description: 'Number of qualifying children under 17', required: true },
      { name: 'agi', type: 'number', description: 'Adjusted Gross Income', required: true },
      { name: 'filingStatus', type: 'string', description: 'Filing status', required: true }
    ],
    execute: async (params: Record<string, any>) => {
      const { dependents, agi, filingStatus } = params;
      
      const creditPerChild = 2000;
      const phaseoutThreshold = filingStatus === 'married_joint' ? 400000 : 200000;
      const phaseoutRate = 0.05;
      
      // Base nonrefundable credit before refundable rules
      let credit = dependents * creditPerChild;

      if (agi > phaseoutThreshold) {
        const excessIncome = agi - phaseoutThreshold;
        const reduction = Math.ceil(excessIncome / 1000) * 50;
        credit = Math.max(0, credit - reduction);
      }

      // Simplified refundable portion (Additional CTC) cap for 2024 is $1,700 per child
      // Note: Actual refundable amount also depends on earned income; this is a simplified cap.
      const perChildAfterPhaseout = dependents > 0 ? credit / dependents : 0;
      const refundablePerChildCap = 1700;
      const refundablePerChild = Math.min(perChildAfterPhaseout, refundablePerChildCap);
      const refundablePortion = Math.max(0, refundablePerChild * dependents);

      return {
        credit,
        maxCredit: dependents * creditPerChild,
        phaseoutApplied: agi > phaseoutThreshold,
        refundablePortion
      };
    }
  },
  {
    name: 'calculate_eitc',
    description: 'Calculate Earned Income Tax Credit',
    parameters: [
      { name: 'earnedIncome', type: 'number', description: 'Earned income amount', required: true },
      { name: 'dependents', type: 'number', description: 'Number of qualifying children', required: true },
      { name: 'filingStatus', type: 'string', description: 'Filing status', required: true }
    ],
    execute: async (params: Record<string, any>) => {
      const { earnedIncome, dependents, filingStatus } = params;
      
      // Simplified EITC calculation (actual is more complex)
      const eitcLimits2024 = {
        0: { maxIncome: 17640, maxCredit: 632 },
        1: { maxIncome: 46560, maxCredit: 4213 },
        2: { maxIncome: 52918, maxCredit: 6960 },
        3: { maxIncome: 56838, maxCredit: 7830 }
      };

      const childCount = Math.min(3, dependents);
      const limits = eitcLimits2024[childCount as keyof typeof eitcLimits2024];
      
      if (earnedIncome > limits.maxIncome) {
        return { credit: 0, eligible: false, reason: 'Income exceeds limit' };
      }

      // Simplified credit calculation
      const creditRate = limits.maxCredit / (limits.maxIncome * 0.7);
      const credit = Math.min(limits.maxCredit, earnedIncome * creditRate);

      return {
        credit: Math.round(credit),
        maxCredit: limits.maxCredit,
        eligible: true,
        incomeLimit: limits.maxIncome
      };
    }
  },
  {
    name: 'compare_scenarios',
    description: 'Compare different tax scenarios side by side',
    parameters: [
      { name: 'scenarios', type: 'array', description: 'Array of tax scenarios to compare', required: true }
    ],
    execute: async (params: Record<string, any>) => {
      const { scenarios } = params;
      
      const comparisons = scenarios.map((scenario: any, index: number) => ({
        scenarioName: scenario.name || `Scenario ${index + 1}`,
        taxableIncome: scenario.taxableIncome,
        totalTax: scenario.totalTax,
        effectiveRate: scenario.effectiveRate,
        refundOrOwed: scenario.refundOrOwed
      }));

      const bestScenario = comparisons.reduce((best: any, current: any) => 
        current.totalTax < best.totalTax ? current : best
      );

      return {
        comparisons,
        bestScenario: bestScenario.scenarioName,
        potentialSavings: Math.max(...comparisons.map((s: any) => s.totalTax)) - bestScenario.totalTax
      };
    }
  }
];
