import type { Tool } from '../types';
import { taxCalculationTools } from './taxCalculationTools';
import { documentProcessingTools } from './documentProcessingTools';
import { complianceTools } from './complianceTools';
import { advisoryTools } from './advisoryTools';
import { formFillingTools } from './formFillingTools';
import { optimizationTools } from './optimizationTools';

export const ALL_TOOLS: Tool[] = [
  ...taxCalculationTools,
  ...documentProcessingTools,
  ...complianceTools,
  ...advisoryTools,
  ...formFillingTools,
  ...optimizationTools
];

export function getToolsByAgent(agentRole: string): Tool[] {
  const toolMap: Record<string, Tool[]> = {
    tax_calculator: taxCalculationTools,
    document_processor: documentProcessingTools,
    compliance_checker: complianceTools,
    tax_advisor: advisoryTools,
    form_filler: formFillingTools,
    optimization_analyzer: optimizationTools,
    orchestrator: ALL_TOOLS // Orchestrator can access all tools
  };

  return toolMap[agentRole] || [];
}

export function getToolByName(name: string): Tool | undefined {
  return ALL_TOOLS.find(tool => tool.name === name);
}

export {
  taxCalculationTools,
  documentProcessingTools,
  complianceTools,
  advisoryTools,
  formFillingTools,
  optimizationTools
};
