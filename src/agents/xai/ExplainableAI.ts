// Explainable AI System for Tax Agents

export interface Explanation {
  id: string;
  agentRole: string;
  decision: string;
  reasoning: ReasoningStep[];
  dataUsed: DataSource[];
  alternatives: Alternative[];
  confidence: number;
  timestamp: Date;
}

export interface ReasoningStep {
  step: number;
  description: string;
  calculation?: string;
  reference?: string;
  result?: any;
}

export interface DataSource {
  source: string;
  type: 'user_input' | 'tax_law' | 'calculation' | 'historical_data' | 'external_api';
  data: any;
  relevance: number;
}

export interface Alternative {
  option: string;
  outcome: any;
  tradeoffs: string[];
  recommendation: boolean;
}

export class ExplainableAI {
  /**
   * Generate a comprehensive explanation for a tax calculation
   */
  static explainTaxCalculation(
    input: { taxableIncome: number; filingStatus: string },
    result: any
  ): Explanation {
    const reasoning: ReasoningStep[] = [
      {
        step: 1,
        description: 'Determined filing status and applicable tax brackets',
        reference: '2024 IRS Tax Brackets',
        result: input.filingStatus
      },
      {
        step: 2,
        description: 'Applied progressive tax rates to income',
        calculation: 'Tax calculated by bracket segments',
        result: result.breakdown
      },
      {
        step: 3,
        description: 'Summed tax across all brackets',
        calculation: result.breakdown.map((b: any) => `$${b.tax}`).join(' + '),
        result: `Total: $${result.totalTax}`
      },
      {
        step: 4,
        description: 'Calculated effective and marginal tax rates',
        calculation: `Effective: ${result.effectiveRate}, Marginal: ${result.marginalRate}`,
        result: { effective: result.effectiveRate, marginal: result.marginalRate }
      }
    ];

    const dataUsed: DataSource[] = [
      {
        source: '2024 IRS Tax Brackets',
        type: 'tax_law',
        data: 'Federal income tax brackets for all filing statuses',
        relevance: 1.0
      },
      {
        source: 'User Input',
        type: 'user_input',
        data: input,
        relevance: 1.0
      }
    ];

    const alternatives: Alternative[] = [
      {
        option: 'Change filing status',
        outcome: 'May reduce or increase tax liability',
        tradeoffs: ['Eligibility requirements', 'Complexity'],
        recommendation: false
      }
    ];

    return {
      id: `exp-${Date.now()}`,
      agentRole: 'tax_calculator',
      decision: `Federal income tax calculated as $${result.totalTax}`,
      reasoning,
      dataUsed,
      alternatives,
      confidence: 0.99,
      timestamp: new Date()
    };
  }

  /**
   * Explain credit eligibility determination
   */
  static explainCreditEligibility(
    creditType: string,
    input: any,
    result: any
  ): Explanation {
    const reasoning: ReasoningStep[] = [
      {
        step: 1,
        description: `Evaluated eligibility for ${creditType}`,
        reference: 'IRS Publication 972 (Child Tax Credit) or 596 (EITC)',
        result: result.eligible ? 'Eligible' : 'Not Eligible'
      }
    ];

    if (result.eligible) {
      reasoning.push({
        step: 2,
        description: 'Calculated credit amount',
        calculation: result.calculation || 'Based on income and dependents',
        result: `$${result.credit}`
      });

      if (result.phaseoutApplied) {
        reasoning.push({
          step: 3,
          description: 'Applied income phase-out reduction',
          calculation: 'Credit reduced due to income exceeding threshold',
          result: `Reduced from $${result.maxCredit} to $${result.credit}`
        });
      }
    }

    return {
      id: `exp-${Date.now()}`,
      agentRole: 'tax_calculator',
      decision: result.eligible 
        ? `Eligible for ${creditType}: $${result.credit}`
        : `Not eligible for ${creditType}`,
      reasoning,
      dataUsed: [
        {
          source: 'IRS Credit Rules',
          type: 'tax_law',
          data: `${creditType} eligibility and calculation rules`,
          relevance: 1.0
        },
        {
          source: 'User Tax Data',
          type: 'user_input',
          data: input,
          relevance: 1.0
        }
      ],
      alternatives: result.eligible ? [] : [
        {
          option: 'Explore alternative credits',
          outcome: 'Other credits may be available',
          tradeoffs: ['Different eligibility requirements'],
          recommendation: true
        }
      ],
      confidence: result.eligible ? 0.95 : 0.90,
      timestamp: new Date()
    };
  }

  /**
   * Explain deduction optimization recommendation
   */
  static explainDeductionStrategy(
    input: { standard: number; itemized: number },
    recommendation: 'standard' | 'itemized'
  ): Explanation {
    const savings = Math.abs(input.standard - input.itemized);
    
    const reasoning: ReasoningStep[] = [
      {
        step: 1,
        description: 'Compared standard and itemized deduction amounts',
        calculation: `Standard: $${input.standard}, Itemized: $${input.itemized}`,
        result: `Difference: $${savings}`
      },
      {
        step: 2,
        description: `Recommended ${recommendation} deduction`,
        reference: 'IRS Tax Code - Deductions',
        result: recommendation === 'itemized' 
          ? `Itemized saves $${savings} more`
          : `Standard deduction is higher by $${savings}`
      }
    ];

    return {
      id: `exp-${Date.now()}`,
      agentRole: 'optimization_analyzer',
      decision: `Use ${recommendation} deduction for optimal tax savings`,
      reasoning,
      dataUsed: [
        {
          source: '2024 Standard Deduction Amounts',
          type: 'tax_law',
          data: input.standard,
          relevance: 1.0
        },
        {
          source: 'Calculated Itemized Deductions',
          type: 'calculation',
          data: input.itemized,
          relevance: 1.0
        }
      ],
      alternatives: [
        {
          option: recommendation === 'standard' ? 'Itemize' : 'Standard',
          outcome: `Results in $${savings} less deduction`,
          tradeoffs: recommendation === 'standard' 
            ? ['Simplified filing', 'Less documentation needed']
            : ['More complex filing', 'Requires documentation'],
          recommendation: false
        }
      ],
      confidence: 1.0,
      timestamp: new Date()
    };
  }

  /**
   * Explain compliance validation result
   */
  static explainComplianceCheck(
    checkType: string,
    input: any,
    result: any
  ): Explanation {
    const reasoning: ReasoningStep[] = [
      {
        step: 1,
        description: `Performed ${checkType} compliance check`,
        reference: 'IRS Regulations and Tax Code',
        result: result.valid ? 'Passed' : 'Failed'
      }
    ];

    if (!result.valid && result.errors) {
      result.errors.forEach((error: string, index: number) => {
        reasoning.push({
          step: index + 2,
          description: `Compliance Issue: ${error}`,
          reference: 'IRS Requirements',
          result: 'Must be corrected'
        });
      });
    }

    return {
      id: `exp-${Date.now()}`,
      agentRole: 'compliance_checker',
      decision: result.valid 
        ? 'All compliance checks passed'
        : `${result.errors?.length || 0} compliance issues found`,
      reasoning,
      dataUsed: [
        {
          source: 'IRS Compliance Rules',
          type: 'tax_law',
          data: checkType,
          relevance: 1.0
        },
        {
          source: 'User Submission Data',
          type: 'user_input',
          data: input,
          relevance: 1.0
        }
      ],
      alternatives: !result.valid ? [
        {
          option: 'Correct identified issues',
          outcome: 'Achieve full compliance',
          tradeoffs: ['Requires data correction'],
          recommendation: true
        }
      ] : [],
      confidence: 0.98,
      timestamp: new Date()
    };
  }

  /**
   * Generate natural language explanation from structured explanation
   */
  static toNaturalLanguage(explanation: Explanation): string {
    let text = `## ${explanation.decision}\n\n`;
    
    text += '### How we arrived at this answer:\n\n';
    explanation.reasoning.forEach(step => {
      text += `${step.step}. ${step.description}\n`;
      if (step.calculation) {
        text += `   Calculation: ${step.calculation}\n`;
      }
      if (step.reference) {
        text += `   Reference: ${step.reference}\n`;
      }
      text += `   Result: ${typeof step.result === 'object' ? JSON.stringify(step.result) : step.result}\n\n`;
    });

    text += '### Data sources used:\n\n';
    explanation.dataUsed.forEach(source => {
      text += `- ${source.source} (${source.type})\n`;
    });

    if (explanation.alternatives.length > 0) {
      text += '\n### Alternative options considered:\n\n';
      explanation.alternatives.forEach(alt => {
        text += `- ${alt.option}\n`;
        text += `  Outcome: ${alt.outcome}\n`;
        text += `  Trade-offs: ${alt.tradeoffs.join(', ')}\n`;
        text += `  Recommended: ${alt.recommendation ? 'Yes' : 'No'}\n\n`;
      });
    }

    text += `\n**Confidence Level:** ${(explanation.confidence * 100).toFixed(0)}%\n`;
    
    return text;
  }
}
