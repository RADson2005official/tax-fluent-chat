// Tax Knowledge Data for LLM Access
// This file provides a programmatic way to access tax knowledge for LLMs

export const TAX_KNOWLEDGE_FILE_URL = '/llm-tax-knowledge.txt';

export const TAX_KNOWLEDGE_METADATA = {
  version: '2024',
  lastUpdated: '2024',
  description: 'Comprehensive tax knowledge base for LLM assistance',
  fileLocation: '/llm-tax-knowledge.txt',
  accessMethod: 'HTTP GET request to public URL'
};

/**
 * Fetch the LLM tax knowledge file content
 * @returns Promise<string> The tax knowledge content
 */
export async function fetchTaxKnowledge(): Promise<string> {
  try {
    const response = await fetch(TAX_KNOWLEDGE_FILE_URL);
    if (!response.ok) {
      throw new Error(`Failed to fetch tax knowledge: ${response.status}`);
    }
    return await response.text();
  } catch (error) {
    console.error('Error fetching tax knowledge:', error);
    throw error;
  }
}

/**
 * Extract specific sections from the tax knowledge base
 * @param content - The full tax knowledge content
 * @param section - The section to extract (e.g., 'TAX BRACKETS', 'CREDITS AND DEDUCTIONS')
 * @returns string The extracted section content
 */
export function extractTaxSection(content: string, section: string): string {
  const lines = content.split('\n');
  const sectionStart = lines.findIndex(line => 
    line.toUpperCase().includes(section.toUpperCase())
  );
  
  if (sectionStart === -1) return '';
  
  const nextSectionStart = lines.findIndex((line, index) => 
    index > sectionStart && line.match(/^##\s/)
  );
  
  const endIndex = nextSectionStart === -1 ? lines.length : nextSectionStart;
  return lines.slice(sectionStart, endIndex).join('\n');
}