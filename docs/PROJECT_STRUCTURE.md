# 📂 Project Structure Overview

This document provides a comprehensive overview of the Tax Filing AI Agent project structure.

---

## 🏗️ High-Level Architecture

```
tax-fluent-chat/
│
├── 🐍 backend/              # FastAPI Python Backend
├── 🎨 src/                  # Vue 3 Frontend
├── 📚 docs/                 # Documentation
├── 🔧 public/               # Static Assets
└── ⚙️  config files         # Build & Configuration
```

---

## 📦 Detailed Structure

### 🐍 Backend (`/backend`)

```
backend/
├── app/
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # FastAPI application entry
│   ├── database.py              # SQLAlchemy configuration
│   ├── models.py                # Database models (9 tables)
│   ├── schemas.py               # Pydantic validation schemas
│   ├── security.py              # JWT auth & encryption
│   ├── crud.py                  # Database CRUD operations
│   │
│   └── api/                     # API Endpoints
│       ├── __init__.py
│       ├── auth.py              # Authentication endpoints
│       ├── users.py             # User management
│       ├── tax_forms.py         # Tax form CRUD
│       ├── documents.py         # Document upload/processing
│       ├── agents.py            # AI agent interactions
│       └── health.py            # Health checks
│
├── venv/                        # Python virtual environment
├── requirements.txt             # Python dependencies
├── .env.dev                     # Development environment vars
├── .env.prod                    # Production environment vars
├── init-db.sql                  # Database initialization
├── test_db_connection.py        # Database test script
└── debug_models.py              # Model debugging script
```

**Key Files:**
- **models.py** (9 tables): `users`, `user_profiles`, `tax_forms`, `dependents`, `w2_forms`, `form_1099s`, `user_input_data`, `compliance_checks`, `audit_logs`
- **schemas.py**: 30+ Pydantic schemas for type-safe API
- **security.py**: JWT tokens, bcrypt hashing, Fernet encryption

---

### 🎨 Frontend (`/src`)

```
src/
├── agents/                      # AI Agent System
│   ├── BaseAgent.ts            # Base agent class
│   ├── configs.ts              # Agent configurations
│   ├── index.ts                # Agent exports
│   ├── types.ts                # TypeScript types
│   │
│   ├── langchain/              # LangChain Integration
│   │   ├── LangChainAgent.ts   # Main LangChain agent
│   │   ├── LangChainTools.ts   # Tool conversion layer
│   │   └── WorkflowOrchestrator.ts  # 8-step workflow
│   │
│   ├── specialized/            # Specialized Agents
│   │   ├── OrchestratorAgent.ts     # Main orchestrator
│   │   ├── TaxCalculatorAgent.ts    # Tax calculations
│   │   ├── DocumentProcessorAgent.ts # Document extraction
│   │   ├── ComplianceAgent.ts       # IRS validation
│   │   ├── TaxAdvisorAgent.ts       # Optimization advice
│   │   └── FormFillerAgent.ts       # Form generation
│   │
│   ├── tools/                  # 25+ Tax-Specific Tools
│   │   ├── index.ts
│   │   ├── documentProcessingTools.ts  # 9 tools
│   │   ├── taxCalculationTools.ts      # 8 tools
│   │   ├── complianceTools.ts          # 8 tools
│   │   ├── formFillingTools.ts         # 4 tools
│   │   ├── advisoryTools.ts            # Advisory tools
│   │   └── optimizationTools.ts        # Optimization tools
│   │
│   └── llm/                    # LLM Provider Abstraction
│       ├── LLMProvider.ts      # Provider interface
│       └── test-providers.ts   # Provider testing
│
├── components-vue/             # Vue 3 Components
│   ├── adaptive/               # Adaptive UI Components
│   │   ├── AdaptiveInput.vue
│   │   ├── AdaptiveForm.vue
│   │   └── ProviderSwitcher.vue
│   │
│   ├── chat/                   # Chat Interface
│   │   ├── ChatInterface.vue
│   │   ├── MessageBubble.vue
│   │   └── ChatInput.vue
│   │
│   ├── langchain/              # LangChain UI
│   │   └── WorkflowDemo.vue    # Workflow visualization
│   │
│   ├── inputs/                 # Form Inputs
│   │   ├── TaxFormInput.vue
│   │   ├── DocumentUpload.vue
│   │   └── W2FormInput.vue
│   │
│   ├── analysis/               # Data Analysis
│   │   └── TaxAnalysis.vue
│   │
│   └── ui/                     # Base UI Components
│       ├── Badge.vue
│       ├── Button.vue
│       ├── Card.vue
│       ├── Dialog.vue
│       └── ... (20+ components)
│
├── stores/                     # Pinia State Management
│   ├── agentStore.ts          # Agent state & actions
│   ├── chatStore.ts           # Chat messages & history
│   └── langchainStore.ts      # LangChain workflow state
│
├── pages/                      # Page Components
│   ├── Index.vue              # Main application page
│   └── NotFound.vue           # 404 page
│
├── composables/               # Vue Composables
│   └── useToast.ts           # Toast notifications
│
├── data/                      # Static Data
│   └── tax-knowledge.ts      # Tax knowledge base
│
├── lib/                       # Utilities
│   └── utils.ts              # Helper functions
│
├── main.ts                    # Application entry point
├── router.ts                  # Vue Router configuration
├── index.css                  # Global styles
└── vite-env.d.ts             # Vite types
```

**Key Features:**
- **6 Specialized Agents**: Orchestrator, Calculator, Document Processor, Compliance, Advisor, Form Filler
- **25+ Tax Tools**: Document processing (9), Calculations (8), Compliance (8), Forms (4+)
- **LangChain Integration**: 8-step autonomous workflow
- **Adaptive UI**: Adjusts based on user proficiency

---

### 📚 Documentation (`/docs`)

```
docs/
├── README.md                   # Documentation index
│
├── setup/                      # Installation Guides
│   ├── QUICKSTART_DATABASE.md  # ⭐ Quick database setup
│   ├── POSTGRESQL_INSTALLATION_WINDOWS.md  # Windows install
│   └── POSTGRESQL_SETUP.md     # General PostgreSQL setup
│
├── guides/                     # User Guides
│   ├── LANGCHAIN_INTEGRATION.md     # Multi-agent workflows
│   ├── LANGCHAIN_QUICKSTART.md      # Quick examples
│   └── HOW_TO_SWITCH_PROVIDERS.md   # Change AI providers
│
└── api/                        # API Documentation
    ├── API_REFERENCE.md        # REST API documentation
    ├── AGENT_SYSTEM_SUMMARY.md # Agent architecture
    └── LLM_PROVIDERS_IMPLEMENTATION.md  # Provider details
```

---

### 🔧 Configuration Files

```
tax-fluent-chat/
├── package.json                # Node.js dependencies
├── package-lock.json           # Dependency lock file
├── tsconfig.json               # TypeScript configuration
├── tsconfig.app.json           # App TypeScript config
├── tsconfig.node.json          # Node TypeScript config
├── vite.config.ts              # Vite build configuration
├── tailwind.config.ts          # TailwindCSS configuration
├── postcss.config.js           # PostCSS configuration
├── components.json             # UI component registry
├── eslint.config.js            # ESLint configuration
├── docker-compose.yml          # Docker services
├── setup-postgresql.ps1        # PostgreSQL setup script
├── setup-postgresql.bat        # Windows batch wrapper
└── .gitignore                  # Git ignore rules
```

---

## 🗄️ Database Schema (9 Tables)

```sql
-- User Management
users                   # User accounts with authentication
user_profiles          # Adaptive UI preferences & behavior

-- Tax Data
tax_forms              # Main tax returns with calculations
dependents             # Dependent information (encrypted SSN)
w2_forms               # W-2 income forms
form_1099s             # All types of 1099 forms
user_input_data        # Complete input tracking & audit

-- Compliance & Security
compliance_checks      # IRS validation results
audit_logs            # Security & compliance logging
```

**Relationships:**
- `users` → `user_profiles` (1:1)
- `users` → `tax_forms` (1:N)
- `tax_forms` → `dependents`, `w2_forms`, `form_1099s`, `user_input_data`, `compliance_checks` (1:N)
- `users` → `audit_logs` (1:N)

---

## 📊 File Count Summary

| Category | Count | Description |
|----------|-------|-------------|
| **Python Files** | 15+ | Backend API, models, schemas |
| **TypeScript Files** | 50+ | Agents, tools, components |
| **Vue Components** | 40+ | UI components and pages |
| **Database Tables** | 9 | PostgreSQL schema |
| **AI Agents** | 6 | Specialized agents |
| **Tax Tools** | 25+ | Tax-specific functions |
| **Documentation** | 12 | Setup guides, API docs |

---

## 🔄 Data Flow

```
User Input (Vue)
    ↓
Pinia Store (State Management)
    ↓
Agent System (TypeScript)
    ↓
LLM Provider (OpenAI/Anthropic/Gemini)
    ↓
Tool Execution (Tax Calculations/Document Processing)
    ↓
FastAPI Backend (Python)
    ↓
PostgreSQL Database
    ↓
Response Back to User
```

---

## 🎯 Key Entry Points

1. **Frontend**: `src/main.ts` → Initializes Vue app
2. **Backend**: `backend/app/main.py` → FastAPI application
3. **Agents**: `src/agents/index.ts` → Agent system exports
4. **Database**: `backend/app/database.py` → DB connection
5. **Docs**: `docs/README.md` → Documentation index

---

## 📝 Naming Conventions

**Backend (Python):**
- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions: `snake_case()`
- Constants: `UPPER_SNAKE_CASE`

**Frontend (TypeScript/Vue):**
- Files: `PascalCase.vue`, `camelCase.ts`
- Components: `PascalCase.vue`
- Functions: `camelCase()`
- Constants: `UPPER_SNAKE_CASE`

**Database:**
- Tables: `snake_case`
- Columns: `snake_case`
- Relationships: descriptive names

---

## 🚀 Quick Navigation

**Want to modify...**

| Feature | Location |
|---------|----------|
| Database schema | `backend/app/models.py` |
| API endpoints | `backend/app/api/` |
| Tax calculations | `src/agents/tools/taxCalculationTools.ts` |
| UI components | `src/components-vue/` |
| Agent behavior | `src/agents/specialized/` |
| LangChain workflows | `src/agents/langchain/WorkflowOrchestrator.ts` |
| State management | `src/stores/` |
| Documentation | `docs/` |

---

<div align="center">

**Need more details?** See [Documentation Index](README.md)

**Back to main README**: [README.md](../README.md)

</div>
