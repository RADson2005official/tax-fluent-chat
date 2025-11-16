import type { Tool } from '../types';

// Define proper types for compliance tools
interface ComplianceIssue {
  category?: string;
  issue?: string;
  severity: 'error' | 'warning';
  rule?: string;
  violation?: string;
  warning?: string;
  type?: string;
  description?: string;
  impact?: string;
  message?: string;
  field?: string;
  reference?: string;
}

interface VerificationResult {
  credit?: string;
  eligible?: boolean;
  reason?: string;
}

interface TaxCodeReference {
  title: string;
  description: string;
  keyPoints: string[];
  url: string;
}

interface ComplianceCheckResult {
  taxpayerId: string;
  period: string;
  complianceScore: number;
  issues: ComplianceIssue[];
  recommendations: string[];
  overallStatus: 'good' | 'fair' | 'poor';
}

interface RuleEngineResult {
  passed: string[];
  warnings: ComplianceIssue[];
  errors: ComplianceIssue[];
  score: number;
  processingTime: number;
}

interface ActivityLogEntry {
  type: string;
  late?: boolean;
  status?: string;
  completeness?: number;
}

interface ToolParams {
  [key: string]: unknown;
}

interface TaxCredits {
  childTaxCredit?: number;
  eitc?: number;
  [key: string]: number | undefined;
}

interface TaxContext {
  dependents?: number;
  income?: number;
  [key: string]: unknown;
}

export const complianceTools: Tool[] = [
  {
    name: 'check_filing_requirements',
    description: 'Check if individual is required to file taxes',
    parameters: [
      { name: 'income', type: 'number', description: 'Total income', required: true },
      { name: 'filingStatus', type: 'string', description: 'Filing status', required: true },
      { name: 'age', type: 'number', description: 'Taxpayer age', required: true }
    ],
    execute: async (params: ToolParams) => {
      const { income, filingStatus, age } = params as { income: number; filingStatus: string; age: number };
      
      const thresholds2024: Record<string, number> = {
        single: age >= 65 ? 15700 : 14600,
        married_joint: age >= 65 ? 30700 : 29200,
        married_separate: 5,
        head_of_household: age >= 65 ? 23500 : 21900
      };

      const threshold = thresholds2024[filingStatus] || thresholds2024.single;
      const required = income >= threshold;

      return {
        required,
        threshold,
        income,
        reason: required 
          ? `Income of $${income} exceeds filing threshold of $${threshold}`
          : `Income below filing threshold of $${threshold}`
      };
    }
  },
  {
    name: 'validate_deductions',
    description: 'Validate that claimed deductions are legitimate',
    parameters: [
      { name: 'deductions', type: 'object', description: 'Claimed deductions', required: true },
      { name: 'income', type: 'number', description: 'Total income', required: true }
    ],
    execute: async (params: ToolParams) => {
      const { deductions, income } = params as { deductions: Record<string, number>; income: number };
      const issues: ComplianceIssue[] = [];
      
      // Medical expenses must exceed 7.5% of AGI
      if (deductions.medicalExpenses) {
        const threshold = income * 0.075;
        if (deductions.medicalExpenses <= threshold) {
          issues.push({
            category: 'Medical Expenses',
            issue: `Medical expenses must exceed ${threshold.toFixed(2)} (7.5% of AGI) to be deductible`,
            severity: 'warning'
          });
        }
      }

      // Charitable contributions limit
      if (deductions.charitableContributions) {
        const limit = income * 0.6;
        if (deductions.charitableContributions > limit) {
          issues.push({
            category: 'Charitable Contributions',
            issue: `Charitable contributions exceed 60% of AGI limit`,
            severity: 'error'
          });
        }
      }

      return {
        valid: issues.filter(i => i.severity === 'error').length === 0,
        issues,
        recommendations: issues.map(i => `Review ${i.category}`)
      };
    }
  },
  {
    name: 'verify_credits',
    description: 'Verify eligibility for claimed tax credits',
    parameters: [
      { name: 'credits', type: 'object', description: 'Claimed credits', required: true },
      { name: 'taxContext', type: 'object', description: 'Tax context', required: true }
    ],
    execute: async (params: ToolParams) => {
      const { credits, taxContext } = params as { credits: TaxCredits; taxContext: TaxContext };
      const verifications: VerificationResult[] = [];

      if (credits.childTaxCredit) {
        const eligible = taxContext.dependents > 0;
        verifications.push({
          credit: 'Child Tax Credit',
          eligible,
          reason: eligible ? 'Has qualifying dependents' : 'No qualifying dependents'
        });
      }

      if (credits.eitc) {
        const maxIncome = 60000;
        const eligible = taxContext.income < maxIncome;
        verifications.push({
          credit: 'EITC',
          eligible,
          reason: eligible ? 'Income within limits' : 'Income exceeds limit'
        });
      }

      return {
        allEligible: verifications.every(v => v.eligible),
        verifications
      };
    }
  },
  {
    name: 'detect_errors',
    description: 'Detect common filing errors',
    parameters: [
      { name: 'formData', type: 'object', description: 'Tax form data', required: true }
    ],
    execute: async (params: ToolParams) => {
      const { formData } = params as { formData: Record<string, unknown> };
      const errors: string[] = [];

      if (!formData.name) errors.push('Missing taxpayer name');
      if (!formData.ssn) errors.push('Missing SSN');
      if (typeof formData.totalIncome === 'number' && formData.totalIncome < 0) errors.push('Income cannot be negative');
      if (formData.refund && formData.amountOwed) errors.push('Cannot have both refund and amount owed');

      return {
        hasErrors: errors.length > 0,
        errorCount: errors.length,
        errors
      };
    }
  },
  {
    name: 'irs_rule_validator',
    description: 'Validate tax calculations against IRS rules and regulations',
    parameters: [
      { name: 'taxData', type: 'object', description: 'Complete tax calculation data', required: true },
      { name: 'taxYear', type: 'number', description: 'Tax year for validation', required: true },
      { name: 'rulesToCheck', type: 'array', description: 'Specific IRS rules to validate', required: false }
    ],
    execute: async (params: ToolParams) => {
      const { taxData, taxYear, rulesToCheck = ['all'] } = params as { taxData: Record<string, unknown>; taxYear: number; rulesToCheck?: string[] };
      
      const violations: ComplianceIssue[] = [];
      const warnings: ComplianceIssue[] = [];
      const passedRules: string[] = [];
      
      // Standard deduction validation (IRC Section 63)
      if (typeof taxData.filingStatus === 'string' && typeof taxData.standardDeduction === 'number') {
        const standardDeductions2024 = {
          single: 14600,
          married_joint: 29200,
          married_separate: 14600,
          head_of_household: 21900
        };
        
        const correctDeduction = standardDeductions2024[taxData.filingStatus as keyof typeof standardDeductions2024] || 0;
        if (Math.abs(taxData.standardDeduction - correctDeduction) > 1) {
          violations.push({
            rule: 'IRC Section 63 - Standard Deduction',
            violation: `Incorrect standard deduction amount. Should be $${correctDeduction}`,
            severity: 'error',
            reference: 'https://www.irs.gov/taxtopics/tc551'
          });
        } else {
          passedRules.push('IRC Section 63 - Standard Deduction');
        }
      }
      
      // Tax bracket validation (IRC Section 1)
      if (typeof taxData.taxableIncome === 'number' && typeof taxData.filingStatus === 'string') {
        const brackets2024 = {
          single: [
            { min: 0, max: 11600, rate: 0.10 },
            { min: 11600, max: 47150, rate: 0.12 },
            { min: 47150, max: 100525, rate: 0.22 },
            { min: 100525, max: 191950, rate: 0.24 },
            { min: 191950, max: 243725, rate: 0.32 },
            { min: 243725, max: 609350, rate: 0.35 },
            { min: 609350, max: Infinity, rate: 0.37 }
          ],
          married_joint: [
            { min: 0, max: 23200, rate: 0.10 },
            { min: 23200, max: 94300, rate: 0.12 },
            { min: 94300, max: 201050, rate: 0.22 },
            { min: 201050, max: 383900, rate: 0.24 },
            { min: 383900, max: 487450, rate: 0.32 },
            { min: 487450, max: 731200, rate: 0.35 },
            { min: 731200, max: Infinity, rate: 0.37 }
          ]
        };
        
        const applicableBrackets = brackets2024[taxData.filingStatus as keyof typeof brackets2024] || brackets2024.single;
        const income = taxData.taxableIncome;
        const bracket = applicableBrackets.find(b => income >= b.min && income <= b.max);
        
        if (bracket && typeof taxData.effectiveRate === 'number') {
          const expectedRate = bracket.rate;
          if (Math.abs(taxData.effectiveRate - expectedRate) > 0.001) {
            warnings.push({
              rule: 'IRC Section 1 - Tax Rates',
              warning: `Tax rate may be incorrect for income level $${taxData.taxableIncome}`,
              severity: 'warning',
              reference: 'https://www.irs.gov/taxtopics/tc551'
            });
          } else {
            passedRules.push('IRC Section 1 - Tax Rates');
          }
        }
      }
      
      // Self-employment tax validation (IRC Section 1401)
      if (typeof taxData.selfEmploymentIncome === 'number') {
        const selfEmploymentTax = taxData.selfEmploymentIncome * 0.153;
        const expectedTax = Math.max(0, selfEmploymentTax - 14280); // Half of SS tax is deductible
        
        if (typeof taxData.calculatedSelfEmploymentTax === 'number' && Math.abs(taxData.calculatedSelfEmploymentTax - expectedTax) > 1) {
          violations.push({
            rule: 'IRC Section 1401 - Self-Employment Tax',
            violation: `Incorrect self-employment tax calculation. Expected: $${expectedTax.toFixed(2)}`,
            severity: 'error',
            reference: 'https://www.irs.gov/businesses/small-businesses-self-employed/self-employed-individuals-tax-center'
          });
        } else {
          passedRules.push('IRC Section 1401 - Self-Employment Tax');
        }
      }
      
      return {
        compliant: violations.length === 0,
        violations,
        warnings,
        passedRules,
        summary: {
          totalRulesChecked: passedRules.length + violations.length + warnings.length,
          violationsCount: violations.length,
          warningsCount: warnings.length,
          complianceScore: ((passedRules.length + warnings.length) / (passedRules.length + violations.length + warnings.length)) * 100
        }
      };
    }
  },
  {
    name: 'tax_code_reference',
    description: 'Get detailed IRS code references and explanations',
    parameters: [
      { name: 'section', type: 'string', description: 'IRS code section (e.g., "63", "1", "1401")', required: true },
      { name: 'topic', type: 'string', description: 'Specific tax topic', required: false }
    ],
    execute: async (params: ToolParams) => {
      const { section, topic } = params as { section: string; topic?: string };
      
      const codeReferences: Record<string, TaxCodeReference> = {
        '63': {
          title: 'Taxable Income Defined',
          description: 'Defines taxable income as gross income minus allowable deductions',
          keyPoints: [
            'Standard deduction amounts vary by filing status',
            'Itemized deductions require substantiation',
            'Above-the-line deductions reduce AGI'
          ],
          url: 'https://www.law.cornell.edu/uscode/text/26/63'
        },
        '1': {
          title: 'Tax Imposed',
          description: 'Establishes the income tax rates and brackets',
          keyPoints: [
            'Progressive tax rate structure',
            'Brackets indexed for inflation annually',
            'Applies to taxable income after deductions'
          ],
          url: 'https://www.law.cornell.edu/uscode/text/26/1'
        },
        '1401': {
          title: 'Rate of Tax on Self-Employment Income',
          description: 'Self-employment tax rate and calculation',
          keyPoints: [
            '15.3% total rate (12.4% Social Security + 2.9% Medicare)',
            'Half of self-employment tax is deductible',
            'Applies to net earnings from self-employment'
          ],
          url: 'https://www.law.cornell.edu/uscode/text/26/1401'
        },
        '151': {
          title: 'Allowance of Deductions for Personal Exemptions',
          description: 'Personal and dependency exemptions (repealed for tax years after 2017)',
          keyPoints: [
            'Repealed by Tax Cuts and Jobs Act',
            'No longer applicable for recent tax years',
            'Child Tax Credit now primary dependent benefit'
          ],
          url: 'https://www.law.cornell.edu/uscode/text/26/151'
        }
      };
      
      const reference = codeReferences[section];
      
      if (!reference) {
        return {
          found: false,
          section,
          message: `IRS Code Section ${section} not found in reference database`
        };
      }
      
      return {
        found: true,
        section,
        reference,
        relatedTopics: topic ? [topic] : []
      };
    }
  },
  {
    name: 'compliance_monitor',
    description: 'Monitor ongoing compliance with tax regulations',
    parameters: [
      { name: 'taxpayerId', type: 'string', description: 'Unique taxpayer identifier', required: true },
      { name: 'activityLog', type: 'array', description: 'Log of tax-related activities', required: true },
      { name: 'checkPeriod', type: 'string', description: 'Time period to monitor (e.g., "2024", "last_3_years")', required: false }
    ],
    execute: async (params: ToolParams): Promise<ComplianceCheckResult> => {
      const { taxpayerId, activityLog, checkPeriod = 'current_year' } = params as { taxpayerId: string; activityLog: ActivityLogEntry[]; checkPeriod?: string };
      
      const complianceIssues: ComplianceIssue[] = [];
      const recommendations: string[] = [];
      
      // Check for timely filing patterns
      const filingActivities = activityLog.filter((activity: any) => activity.type === 'file_return');
      const lateFilings = filingActivities.filter((activity: any) => activity.late === true);
      
      if (lateFilings.length > 0) {
        complianceIssues.push({
          type: 'Filing Deadline Compliance',
          severity: 'warning',
          description: `${lateFilings.length} late tax filings detected`,
          impact: 'Potential penalties and interest charges'
        });
        recommendations.push('Consider setting up automatic filing reminders');
      }
      
      // Check for estimated tax payment compliance
      const paymentActivities = activityLog.filter((activity: any) => activity.type === 'estimated_payment');
      const missedPayments = paymentActivities.filter((activity: any) => activity.status === 'missed');
      
      if (missedPayments.length > 0) {
        complianceIssues.push({
          type: 'Estimated Tax Payment Compliance',
          severity: 'error',
          description: `${missedPayments.length} missed estimated tax payments`,
          impact: 'Underpayment penalties under IRC Section 6654'
        });
        recommendations.push('Set up quarterly estimated tax payment schedule');
      }
      
      // Check for record keeping compliance
      const recordActivities = activityLog.filter((activity: any) => activity.type === 'record_keeping');
      const incompleteRecords = recordActivities.filter((activity: any) => activity.completeness < 0.8);
      
      if (incompleteRecords.length > 0) {
        complianceIssues.push({
          type: 'Record Keeping Requirements',
          severity: 'warning',
          description: 'Incomplete tax record keeping detected',
          impact: 'Difficulty substantiating deductions and credits'
        });
        recommendations.push('Implement comprehensive record keeping system');
      }
      
      // Calculate compliance score
      const totalChecks = 3; // filing, payments, records
      const passedChecks = totalChecks - complianceIssues.length;
      const complianceScore = (passedChecks / totalChecks) * 100;
      
      return {
        taxpayerId,
        period: checkPeriod,
        complianceScore,
        issues: complianceIssues,
        recommendations,
        overallStatus: complianceScore >= 80 ? 'good' : complianceScore >= 60 ? 'fair' : 'poor'
      };
    }
  },
  {
    name: 'automated_rule_engine',
    description: 'Apply comprehensive IRS rule engine to tax data',
    parameters: [
      { name: 'taxReturn', type: 'object', description: 'Complete tax return data', required: true },
      { name: 'validationLevel', type: 'string', description: 'strict, normal, or lenient', required: false }
    ],
    execute: async (params: ToolParams): Promise<RuleEngineResult> => {
      const { taxReturn, validationLevel = 'normal' } = params as { taxReturn: Record<string, unknown>; validationLevel?: string };
      
      const results = {
        passed: [] as string[],
        warnings: [] as ComplianceIssue[],
        errors: [] as ComplianceIssue[],
        score: 0,
        processingTime: 0
      };
      
      const startTime = Date.now();
      
      // Income validation rules
      if (taxReturn.income && typeof taxReturn.income === 'object' && taxReturn.income !== null) {
        const income = taxReturn.income as Record<string, unknown>;
        if (typeof income.wages === 'number' && income.wages < 0) {
          results.errors.push({
            rule: 'Income Validation',
            message: 'Wages cannot be negative',
            field: 'wages',
            severity: 'error'
          });
        } else {
          results.passed.push('Income Validation - Wages');
        }
        
        // Check for reasonable income levels
        if (typeof income.total === 'number' && income.total > 10000000) { // $10M threshold
          results.warnings.push({
            rule: 'Income Reasonableness',
            message: 'Extremely high income reported - verify accuracy',
            field: 'totalIncome',
            severity: 'warning'
          });
        }
      }
      
      // Deduction validation
      if (taxReturn.deductions && typeof taxReturn.deductions === 'object' && taxReturn.deductions !== null) {
        const deductions = taxReturn.deductions as Record<string, unknown>;
        const totalDeductions: number = Object.values(deductions).reduce<number>((sum, val) => {
          return sum + (typeof val === 'number' ? val : 0);
        }, 0);
        const income = typeof taxReturn.income === 'object' && taxReturn.income !== null && typeof (taxReturn.income as Record<string, unknown>).total === 'number' 
          ? (taxReturn.income as Record<string, unknown>).total 
          : 0;
        
        if (totalDeductions > income * 0.8) { // 80% of income
          results.warnings.push({
            rule: 'Deduction Limitation',
            message: 'Total deductions exceed 80% of income - review for accuracy',
            field: 'totalDeductions',
            severity: 'warning'
          });
        } else {
          results.passed.push('Deduction Validation');
        }
      }
      
      // Tax calculation validation
      if (typeof taxReturn.calculatedTax === 'number' && typeof taxReturn.taxableIncome === 'number' && taxReturn.taxableIncome > 0) {
        const effectiveRate = taxReturn.calculatedTax / taxReturn.taxableIncome;
        
        if (effectiveRate > 0.5) { // 50% effective rate
          results.errors.push({
            rule: 'Tax Rate Validation',
            message: 'Effective tax rate exceeds 50% - calculation error likely',
            field: 'effectiveTaxRate',
            severity: 'error'
          });
        } else if (effectiveRate < 0) {
          results.errors.push({
            rule: 'Tax Rate Validation',
            message: 'Negative effective tax rate detected',
            field: 'effectiveTaxRate',
            severity: 'error'
          });
        } else {
          results.passed.push('Tax Rate Validation');
        }
      }
      
      // Cross-field validation
      if (taxReturn.refundAmount && taxReturn.amountOwed) {
        results.errors.push({
          rule: 'Mutual Exclusivity',
          message: 'Cannot have both refund and amount owed',
          field: 'refundAmount',
          severity: 'error'
        });
      } else {
        results.passed.push('Mutual Exclusivity Check');
      }
      
      results.processingTime = Date.now() - startTime;
      results.score = (results.passed.length / (results.passed.length + results.warnings.length + results.errors.length)) * 100;
      
      return results;
    }
  }
];
