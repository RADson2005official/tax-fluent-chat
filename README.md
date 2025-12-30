# 🏦 Tax Filing AI Agent - Autonomous Tax Assistant# Welcome to your Lovable project



An intelligent, autonomous AI agent system for tax filing built with **Vue 3**, **FastAPI**, **PostgreSQL**, and **Multi-Agent AI** (LangChain + AutoGen).## Project info




## 🎯 OverviewThe only requirement is having Node.js & npm installed - [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating)



This project is a complete autonomous tax filing system that uses multi-agent AI to:Follow these steps:

- 📄 **Extract data** from tax documents (W-2, 1099, receipts) using OCR and AI

- 🧮 **Calculate taxes** automatically based on IRS regulations```sh

- ✅ **Validate compliance** against current tax codes# Step 1: Clone the repository using the project's Git URL.

- 💡 **Optimize deductions** to maximize refundsgit clone <YOUR_GIT_URL>

- 📝 **Generate tax forms** ready for e-filing

- 🤖 **Interact naturally** via conversational AI interface# Step 2: Navigate to the project directory.

cd <YOUR_PROJECT_NAME>

---

# Step 3: Install the necessary dependencies.

## ✨ Featuresnpm i



### 🤖 Multi-Agent AI System# Step 4: Start the development server with auto-reloading and an instant preview.

- **Orchestrator Agent**: Coordinates workflow between specialized agentsnpm run dev

- **Tax Calculator Agent**: Performs accurate tax calculations```

- **Document Processing Agent**: Extracts data from uploaded documents

- **Compliance Agent**: Validates against IRS regulations**Edit a file directly in GitHub**

- **Advisory Agent**: Provides tax optimization suggestions

- **Form Filler Agent**: Generates completed tax forms- Navigate to the desired file(s).

- Click the "Edit" button (pencil icon) at the top right of the file view.

### 🎨 Adaptive User Interface- Make your changes and commit the changes.

- **Smart UI Adaptation**: Adjusts complexity based on user proficiency

- **Real-time Guidance**: Context-aware help and tooltips**Use GitHub Codespaces**

- **Progress Tracking**: Visual workflow progress indicators

- **Multi-Provider Support**: Switch between AI providers (OpenAI, Anthropic, Gemini, etc.)- Navigate to the main page of your repository.

- Click on the "Code" button (green button) near the top right.

### 🔐 Enterprise-Grade Security- Select the "Codespaces" tab.

- **JWT Authentication**: Secure user sessions- Click on "New codespace" to launch a new Codespace environment.

- **Data Encryption**: SSN and sensitive data encrypted at rest- Edit files directly within the Codespace and commit and push your changes once you're done.

- **Audit Logging**: Complete audit trail for compliance

- **RBAC**: Role-based access control## LLM Tax Knowledge Base



### 📊 Database & StorageThis project includes a comprehensive tax knowledge file that can be accessed by Large Language Models (LLMs) to provide accurate tax assistance:

- **PostgreSQL 18**: Robust relational database

- **9 Optimized Tables**: Users, tax forms, W-2s, 1099s, dependents, compliance checks, etc.**File Location**: `/public/llm-tax-knowledge.txt`  

- **Vector Database Ready**: ChromaDB/FAISS for RAG (Retrieval-Augmented Generation)**Access URL**: `http://localhost:8080/llm-tax-knowledge.txt` (when running locally)



---The knowledge base includes:

- 2024 tax year information

## 🛠 Tech Stack- Tax brackets and filing status details

- Credits and deductions (Child Tax Credit, EITC, etc.)

### Frontend- Business and self-employment tax guidance

- **Vue 3** (Composition API)- Common tax scenarios and calculations

- **TypeScript**- Filing requirements and important dates

- **Pinia** (State Management)

- **Radix Vue** (UI Components)### For Developers

- **TailwindCSS** (Styling)

- **Vite** (Build Tool)Use the TypeScript helper functions in `src/data/tax-knowledge.ts`:



### Backend```typescript

- **FastAPI** (Python 3.10+)import { fetchTaxKnowledge, extractTaxSection } from '@/data/tax-knowledge';

- **SQLAlchemy 2.0** (ORM)

- **PostgreSQL 18** (Database)// Fetch the complete tax knowledge

- **Pydantic v2** (Validation)const taxData = await fetchTaxKnowledge();

- **Alembic** (Migrations)

// Extract specific sections

### AI & Agentsconst creditInfo = extractTaxSection(taxData, 'CREDITS AND DEDUCTIONS');

- **LangChain** (Agent Framework)```

- **AutoGen** (Multi-Agent Orchestration)

- **OpenAI / Anthropic / Gemini** (LLM Providers)### For LLMs

- **ChromaDB** (Vector Database for RAG)

Access the knowledge base directly via HTTP GET request to `/llm-tax-knowledge.txt` for comprehensive tax information to assist users with tax-related questions.

---

## What technologies are used for this project?

## 🚀 Quick Start

This project is built with:

### Prerequisites

- **Python 3.10+**- Vite

- **Node.js 18+**- TypeScript

- **PostgreSQL 18**- Vue.js 3

- **Git**- Pinia (State Management)

- Vue Router

### 1. Clone Repository- Radix Vue (UI Components)

```bash- Tailwind CSS

git clone https://github.com/RADson2005official/tax-fluent-chat.git

cd tax-fluent-chat## How can I deploy this project?

```

Simply open [Lovable](https://lovable.dev/projects/342d33b1-7401-43c5-83ce-887fada4e7b0) and click on Share -> Publish.

### 2. Database Setup

## Can I connect a custom domain to my Lovable project?

```bash
# 1. Backend
cd backend
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
python main.py

# 2. Frontend (new terminal)
npm install && npm run dev
```

**URLs:**
- Frontend: http://localhost:8080
- Backend API: http://localhost:8000/api/docs

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Vue 3, TypeScript, Pinia, TailwindCSS |
| Backend | FastAPI, SQLAlchemy, Pydantic |
| Database | PostgreSQL + pgvector |
| AI | Microsoft AutoGen, sentence-transformers |

## Project Structure

```
backend/
├── app/
│   ├── api/           # REST endpoints
│   ├── autogen_agents/# AI agents (tax_expert, form_filler, etc.)
│   ├── rag/           # Vector search with pgvector
│   ├── services/      # Business logic
│   └── models.py      # Database models
src/
├── components-vue/    # Vue components
├── pages/            # Page views
└── stores/           # Pinia state
```

## Key Features

- 🤖 **Conversational Filing** - Chat-based tax data collection
- 📄 **Document OCR** - Extract data from tax documents
- 📊 **Tax Calculation** - Indian tax slabs (Old/New regime)
- 📝 **ITR-1 Generation** - PDF export

## LLM Rules

See [AGENTS.md](AGENTS.md) for LLM instructions. Key rule: **Use pgvector only** (no ChromaDB/Pinecone).

---

*Educational project for Indian tax filing automation.*
