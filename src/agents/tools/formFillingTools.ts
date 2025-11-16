import type { Tool } from '../types';

export const formFillingTools: Tool[] = [
  {
    name: 'map_data_to_form',
    description: 'Map user data to tax form fields',
    parameters: [
      { name: 'formType', type: 'string', description: 'Tax form type (e.g., 1040)', required: true },
      { name: 'userData', type: 'object', description: 'User tax data', required: true }
    ],
    execute: async (params: Record<string, any>) => {
      const { formType, userData } = params;
      
      const mappings: Record<string, any> = {};

      if (formType === '1040') {
        mappings['Line 1'] = userData.wages || 0;
        mappings['Line 2'] = userData.interest || 0;
        mappings['Line 3'] = userData.dividends || 0;
        mappings['Line 11'] = (userData.wages || 0) + (userData.interest || 0) + (userData.dividends || 0);
      }

      return {
        formType,
        mappings,
        completedFields: Object.keys(mappings).length
      };
    }
  },
  {
    name: 'validate_form_fields',
    description: 'Validate tax form field values',
    parameters: [
      { name: 'formData', type: 'object', description: 'Form field data', required: true }
    ],
    execute: async (params: Record<string, any>) => {
      const { formData } = params;
      const validations: any[] = [];

      Object.entries(formData).forEach(([field, value]) => {
        const isValid = typeof value === 'number' && value >= 0;
        validations.push({
          field,
          valid: isValid,
          message: isValid ? 'Valid' : 'Invalid value'
        });
      });

      return {
        allValid: validations.every(v => v.valid),
        validations
      };
    }
  },
  {
    name: 'determine_required_forms',
    description: 'Determine which tax forms are required',
    parameters: [
      { name: 'taxContext', type: 'object', description: 'Tax context', required: true }
    ],
    execute: async (params: Record<string, any>) => {
      const { taxContext } = params;
      const requiredForms = ['Form 1040'];

      if (taxContext.deductions?.itemized) requiredForms.push('Schedule A');
      if (taxContext.income?.businessIncome) requiredForms.push('Schedule C');
      if (taxContext.income?.capitalGains) requiredForms.push('Schedule D');

      return { requiredForms };
    }
  }
];
