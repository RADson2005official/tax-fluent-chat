# 🏦 Tax Filing AI Agent - Autonomous Tax Assistant# Welcome to your Lovable project



An intelligent, autonomous AI agent system for tax filing built with **Vue 3**, **FastAPI**, **PostgreSQL**, and **Multi-Agent AI** (LangChain + AutoGen).## Project info



> **Status**: 🚧 Active Development | **Version**: 1.0.0-beta**URL**: https://lovable.dev/projects/342d33b1-7401-43c5-83ce-887fada4e7b0



---## How can I edit this code?



## 📋 Table of ContentsThere are several ways of editing your application.



- [Overview](#overview)**Use Lovable**

- [Features](#features)

- [Tech Stack](#tech-stack)Simply visit the [Lovable Project](https://lovable.dev/projects/342d33b1-7401-43c5-83ce-887fada4e7b0) and start prompting.

- [Quick Start](#quick-start)

- [Project Structure](#project-structure)Changes made via Lovable will be committed automatically to this repo.

- [Documentation](#documentation)

- [Development Status](#development-status)**Use your preferred IDE**



---If you want to work locally using your own IDE, you can clone this repo and push changes. Pushed changes will also be reflected in Lovable.



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

# WindowsYes, you can!

.\setup-postgresql.bat

To connect a domain, navigate to Project > Settings > Domains and click Connect Domain.

# Or PowerShell

.\setup-postgresql.ps1Read more here: [Setting up a custom domain](https://docs.lovable.dev/tips-tricks/custom-domain#step-by-step-guide)

```

See [📖 Database Setup Guide](docs/setup/QUICKSTART_DATABASE.md)

### 3. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Test database
python test_db_connection.py

# Start server
uvicorn app.main:app --reload
```

**Backend**: http://localhost:8000 | **API Docs**: http://localhost:8000/docs

### 4. Frontend Setup
```bash
cd ../
npm install
npm run dev
```

**Frontend**: http://localhost:5173

---

## 📁 Project Structure

```
tax-fluent-chat/
├── backend/                      # 🐍 FastAPI Backend
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── database.py          # Database configuration
│   │   ├── models.py            # SQLAlchemy models (9 tables)
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── security.py          # Auth & encryption
│   │   ├── crud.py              # Database operations
│   │   └── api/                 # API routers
│   ├── requirements.txt
│   ├── .env.dev
│   └── test_db_connection.py
│
├── src/                         # 🎨 Vue Frontend
│   ├── agents/                  # AI Agent System
│   │   ├── langchain/          # LangChain integration
│   │   ├── specialized/        # Specialized agents
│   │   ├── tools/              # 25+ Tax tools
│   │   └── llm/                # LLM providers
│   ├── components-vue/         # Vue components
│   ├── stores/                 # Pinia stores
│   ├── pages/                  # Pages
│   └── main.ts
│
├── docs/                        # 📚 Documentation
│   ├── setup/                  # Setup guides
│   ├── guides/                 # User guides
│   └── api/                    # API docs
│
├── docker-compose.yml
├── package.json
└── README.md
```

---

## 📚 Documentation

### 🚀 Getting Started
- [Database Setup](docs/setup/QUICKSTART_DATABASE.md) - Quick database installation
- [PostgreSQL (Windows)](docs/setup/POSTGRESQL_INSTALLATION_WINDOWS.md) - Windows setup
- [PostgreSQL Setup](docs/setup/POSTGRESQL_SETUP.md) - Configuration guide

### 📖 Guides
- [LangChain Integration](docs/guides/LANGCHAIN_INTEGRATION.md) - Multi-agent workflows
- [LangChain Quick Start](docs/guides/LANGCHAIN_QUICKSTART.md) - Quick examples
- [AI Provider Switching](docs/guides/HOW_TO_SWITCH_PROVIDERS.md) - Change providers

### 🔧 API Reference
- [API Reference](docs/api/API_REFERENCE.md) - Complete API docs
- [Agent System](docs/api/AGENT_SYSTEM_SUMMARY.md) - Agent architecture
- [LLM Providers](docs/api/LLM_PROVIDERS_IMPLEMENTATION.md) - Provider details

---

## 📊 Development Status

### ✅ Completed (Tasks 1, 4)
- [x] PostgreSQL 18 with 9 optimized tables
- [x] Security layer (JWT, encryption, hashing)
- [x] Pydantic schemas for validation
- [x] LangChain multi-agent workflow
- [x] 25+ specialized tax tools
- [x] Vue frontend with adaptive UI

### 🚧 In Progress (Task 2)
- [ ] FastAPI CRUD operations (40%)
- [ ] API routers and middleware

### 📋 Planned (Tasks 3, 5-8)
- [ ] AutoGen agent implementation
- [ ] Vector database (RAG)
- [ ] Document OCR
- [ ] E-filing integration
- [ ] Production deployment

---

## 🤝 Contributing

Contributions welcome! Educational/research project.

1. Create feature branch
2. Make changes
3. Test thoroughly
4. Submit pull request

**Code Style**: PEP 8 (backend), Vue 3 Composition API (frontend)

---

## 📄 License

Educational purposes. See LICENSE file.

---

## 📞 Contact

- **GitHub**: [@RADson2005official](https://github.com/RADson2005official)
- **Repository**: [tax-fluent-chat](https://github.com/RADson2005official/tax-fluent-chat)

---

<div align="center">

**Built with ❤️ for automating tax filing**

⭐ Star this repo if you find it helpful!

</div>
