// LangChain-based Agent System for Tax Filing
import { tool } from "@langchain/core/tools";
import { z } from "zod";
import type { BaseMessage } from "@langchain/core/messages";

// Import existing tools
import { documentProcessingTools } from '../tools/documentProcessingTools';
import { taxCalculationTools } from '../tools/taxCalculationTools';
import { complianceTools } from '../tools/complianceTools';
import { formFillingTools } from '../tools/formFillingTools';

/**
 * Convert existing tools to LangChain format
 */
export function convertToLangChainTools() {
  const langchainTools = [];

  // Document Processing Tools
  for (const docTool of documentProcessingTools) {
    const parameters = docTool.parameters || [];
    const schemaObj: Record<string, z.ZodType> = {};
    
    parameters.forEach(param => {
      if (param.type === 'string') {
        schemaObj[param.name] = param.required 
          ? z.string().describe(param.description)
          : z.string().optional().describe(param.description);
      } else if (param.type === 'number') {
        schemaObj[param.name] = param.required
          ? z.number().describe(param.description)
          : z.number().optional().describe(param.description);
      } else if (param.type === 'object') {
        schemaObj[param.name] = param.required
          ? z.record(z.unknown()).describe(param.description)
          : z.record(z.unknown()).optional().describe(param.description);
      } else if (param.type === 'array') {
        schemaObj[param.name] = param.required
          ? z.array(z.unknown()).describe(param.description)
          : z.array(z.unknown()).optional().describe(param.description);
      }
    });

    const langchainTool = tool(
      async (input) => {
        const result = await docTool.execute(input);
        return JSON.stringify(result);
      },
      {
        name: docTool.name,
        description: docTool.description,
        schema: z.object(schemaObj),
      }
    );

    langchainTools.push(langchainTool);
  }

  // Tax Calculation Tools
  for (const calcTool of taxCalculationTools) {
    const parameters = calcTool.parameters || [];
    const schemaObj: Record<string, z.ZodType> = {};
    
    parameters.forEach(param => {
      if (param.type === 'string') {
        schemaObj[param.name] = param.required 
          ? z.string().describe(param.description)
          : z.string().optional().describe(param.description);
      } else if (param.type === 'number') {
        schemaObj[param.name] = param.required
          ? z.number().describe(param.description)
          : z.number().optional().describe(param.description);
      } else if (param.type === 'object') {
        schemaObj[param.name] = param.required
          ? z.record(z.unknown()).describe(param.description)
          : z.record(z.unknown()).optional().describe(param.description);
      }
    });

    const langchainTool = tool(
      async (input) => {
        const result = await calcTool.execute(input);
        return JSON.stringify(result);
      },
      {
        name: calcTool.name,
        description: calcTool.description,
        schema: z.object(schemaObj),
      }
    );

    langchainTools.push(langchainTool);
  }

  // Compliance Tools
  for (const compTool of complianceTools) {
    const parameters = compTool.parameters || [];
    const schemaObj: Record<string, z.ZodType> = {};
    
    parameters.forEach(param => {
      if (param.type === 'string') {
        schemaObj[param.name] = param.required 
          ? z.string().describe(param.description)
          : z.string().optional().describe(param.description);
      } else if (param.type === 'number') {
        schemaObj[param.name] = param.required
          ? z.number().describe(param.description)
          : z.number().optional().describe(param.description);
      } else if (param.type === 'object') {
        schemaObj[param.name] = param.required
          ? z.record(z.unknown()).describe(param.description)
          : z.record(z.unknown()).optional().describe(param.description);
      } else if (param.type === 'array') {
        schemaObj[param.name] = param.required
          ? z.array(z.unknown()).describe(param.description)
          : z.array(z.unknown()).optional().describe(param.description);
      }
    });

    const langchainTool = tool(
      async (input) => {
        const result = await compTool.execute(input);
        return JSON.stringify(result);
      },
      {
        name: compTool.name,
        description: compTool.description,
        schema: z.object(schemaObj),
      }
    );

    langchainTools.push(langchainTool);
  }

  // Form Filling Tools
  for (const formTool of formFillingTools) {
    const parameters = formTool.parameters || [];
    const schemaObj: Record<string, z.ZodType> = {};
    
    parameters.forEach(param => {
      if (param.type === 'string') {
        schemaObj[param.name] = param.required 
          ? z.string().describe(param.description)
          : z.string().optional().describe(param.description);
      } else if (param.type === 'number') {
        schemaObj[param.name] = param.required
          ? z.number().describe(param.description)
          : z.number().optional().describe(param.description);
      } else if (param.type === 'object') {
        schemaObj[param.name] = param.required
          ? z.record(z.unknown()).describe(param.description)
          : z.record(z.unknown()).optional().describe(param.description);
      }
    });

    const langchainTool = tool(
      async (input) => {
        const result = await formTool.execute(input);
        return JSON.stringify(result);
      },
      {
        name: formTool.name,
        description: formTool.description,
        schema: z.object(schemaObj),
      }
    );

    langchainTools.push(langchainTool);
  }

  return langchainTools;
}

/**
 * Tax Filing Response Format
 */
export const TaxFilingResponseFormat = z.object({
  summary: z.string().describe("A concise summary of the tax filing assistance provided"),
  nextSteps: z.array(z.string()).describe("Recommended next steps for the user"),
  confidence: z.number().min(0).max(1).describe("Confidence level in the response (0-1)"),
  estimatedTax: z.number().optional().describe("Estimated tax amount if calculated"),
  refundAmount: z.number().optional().describe("Expected refund amount if applicable"),
  warnings: z.array(z.string()).optional().describe("Any warnings or important notices"),
  formsRequired: z.array(z.string()).optional().describe("Tax forms that need to be filled"),
});

export type TaxFilingResponse = z.infer<typeof TaxFilingResponseFormat>;

/**
 * Agent Runtime Context Schema
 */
export const AgentContextSchema = z.object({
  userId: z.string().describe("Unique user identifier"),
  taxYear: z.number().default(2024).describe("Tax year being processed"),
  filingStatus: z.enum(['single', 'married_joint', 'married_separate', 'head_of_household']).optional(),
  conversationId: z.string().optional().describe("Conversation thread ID"),
});

export type AgentContext = z.infer<typeof AgentContextSchema>;
