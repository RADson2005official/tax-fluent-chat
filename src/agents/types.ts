// Core Types for AI Agent System

export type AgentRole = 
  | 'orchestrator'
  | 'tax_calculator' 
  | 'document_processor'
  | 'compliance_checker'
  | 'tax_advisor'
  | 'form_filler'
  | 'optimization_analyzer';

export type AgentStatus = 'idle' | 'thinking' | 'working' | 'waiting' | 'error' | 'completed';

export type MessageRole = 'user' | 'agent' | 'system' | 'tool';

export interface AgentMessage {
  id: string;
  role: MessageRole;
  content: string;
  agentRole?: AgentRole;
  timestamp: Date;
  metadata?: Record<string, any>;
  toolCalls?: ToolCall[];
  reasoning?: string;
}

export interface ToolCall {
  id: string;
  toolName: string;
  parameters: Record<string, any>;
  result?: any;
  error?: string;
}

export interface AgentCapability {
  name: string;
  description: string;
  tools: string[];
  requiredContext?: string[];
}

export interface AgentConfig {
  role: AgentRole;
  name: string;
  description: string;
  capabilities: AgentCapability[];
  systemPrompt: string;
  temperature?: number;
  maxTokens?: number;
  model?: string;
}

export interface AgentState {
  role: AgentRole;
  status: AgentStatus;
  currentTask?: string;
  memory: AgentMemory;
  context: Record<string, any>;
  error?: string;
}

export interface AgentMemory {
  conversationHistory: AgentMessage[];
  userProfile: UserProfile;
  taxContext: TaxContext;
  documents: ProcessedDocument[];
  calculations: TaxCalculation[];
}

export interface UserProfile {
  filingStatus?: 'single' | 'married_joint' | 'married_separate' | 'head_of_household' | 'qualifying_widow';
  dependents?: number;
  state?: string;
  previousFilings?: any[];
  preferences: {
    mode: 'Novice' | 'Expert' | 'Accessibility';
    language: string;
    complexity: 'simple' | 'detailed' | 'expert';
  };
}

export interface TaxContext {
  taxYear: number;
  income: IncomeData;
  deductions: DeductionData;
  credits: CreditData;
  formData: Record<string, any>;
}

export interface IncomeData {
  w2: W2Income[];
  form1099: Form1099[];
  businessIncome?: BusinessIncome[];
  capitalGains?: CapitalGain[];
  other?: OtherIncome[];
}

export interface W2Income {
  employer: string;
  wages: number;
  federalWithheld: number;
  stateWithheld?: number;
  socialSecurity?: number;
  medicare?: number;
}

export interface Form1099 {
  type: '1099-NEC' | '1099-MISC' | '1099-INT' | '1099-DIV' | '1099-B' | '1099-R';
  payer: string;
  amount: number;
  description?: string;
}

export interface BusinessIncome {
  businessName: string;
  revenue: number;
  expenses: number;
  netIncome: number;
}

export interface CapitalGain {
  description: string;
  purchaseDate: Date;
  saleDate: Date;
  costBasis: number;
  salePrice: number;
  type: 'short' | 'long';
}

export interface OtherIncome {
  type: string;
  amount: number;
  description: string;
}

export interface DeductionData {
  standard?: number;
  itemized?: ItemizedDeductions;
  studentLoanInterest?: number;
  ira?: number;
  healthSavingsAccount?: number;
}

export interface ItemizedDeductions {
  medicalExpenses?: number;
  stateTaxes?: number;
  mortgageInterest?: number;
  charitableContributions?: number;
  other?: number;
  total: number;
}

export interface CreditData {
  childTaxCredit?: number;
  earnedIncomeCredit?: number;
  educationCredit?: number;
  childCareCredit?: number;
  other?: Record<string, number>;
}

export interface ProcessedDocument {
  id: string;
  type: 'w2' | '1099' | 'receipt' | 'statement' | 'other';
  fileName: string;
  uploadDate: Date;
  extractedData: Record<string, any>;
  confidence: number;
  status: 'pending' | 'processed' | 'verified' | 'error';
}

export interface TaxCalculation {
  id: string;
  timestamp: Date;
  scenario: string;
  inputs: Record<string, any>;
  results: TaxCalculationResult;
  reasoning: string[];
}

export interface TaxCalculationResult {
  totalIncome: number;
  adjustedGrossIncome: number;
  taxableIncome: number;
  totalTax: number;
  totalCredits: number;
  totalWithheld: number;
  refundOrOwed: number;
  effectiveTaxRate: number;
  marginalTaxRate: number;
  breakdown: TaxBreakdown;
}

export interface TaxBreakdown {
  federalIncomeTax: number;
  stateTax?: number;
  socialSecurityTax?: number;
  medicareTax?: number;
  additionalMedicareTax?: number;
}

export interface AgentTask {
  id: string;
  agentRole: AgentRole;
  type: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  input: any;
  output?: any;
  error?: string;
  createdAt: Date;
  completedAt?: Date;
}

export interface AgentResponse {
  agentRole: AgentRole;
  success: boolean;
  message: string;
  data?: any;
  reasoning?: string[];
  confidence?: number;
  suggestions?: string[];
  nextActions?: string[];
  formSuggestions?: TaxFormSuggestion[];
}

export interface Tool {
  name: string;
  description: string;
  parameters: ToolParameter[];
  execute: (params: Record<string, any>, context: any) => Promise<any>;
}

export interface ToolParameter {
  name: string;
  type: 'string' | 'number' | 'boolean' | 'object' | 'array';
  description: string;
  required: boolean;
  default?: any;
}

export interface ComplianceRule {
  id: string;
  category: string;
  description: string;
  validate: (context: TaxContext) => Promise<ComplianceResult>;
}

export interface ComplianceResult {
  passed: boolean;
  rule: string;
  message: string;
  severity: 'info' | 'warning' | 'error' | 'critical';
  recommendations?: string[];
}

export interface OptimizationStrategy {
  id: string;
  name: string;
  description: string;
  potentialSavings: number;
  complexity: 'easy' | 'moderate' | 'complex';
  steps: string[];
  eligibility: (context: TaxContext) => boolean;
}

export interface TaxFormSuggestion {
  id: string;
  formType: string;
  formName: string;
  confidence: number;
  suggestedFields: Record<string, any>;
  reason: string;
}
