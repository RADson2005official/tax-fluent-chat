# 🏦 Automated Tax Filing Agent

**AI-powered tax filing system for Indian taxes (ITR-1 SAHAJ)**

> **Status**: 🚧 Active Development | **Version**: 1.0.0-beta

---

## 🎯 Overview

Complete autonomous tax filing system using multi-agent AI architecture:
- 📄 **Data Extraction** from tax documents using OCR
- 🧮 **Automatic Tax Calculation** (Old/New regime)
- ✅ **Compliance Validation** against Indian tax regulations
- 💡 **Deduction Optimization** to maximize refunds
- 📝 **ITR-1 Form Generation** (PDF export)
- 🤖 **Conversational Interface** for natural interaction

---

## ✨ Key Features

### 🤖 Multi-Agent AI System (AutoGen)
- **Tax Expert Agent**: Tax calculations and advice
- **Document Processor**: OCR and data extraction
- **Compliance Agent**: Validates against Indian tax laws
- **Form Filler**: Generates ITR-1 forms

### 🎨 Adaptive UI
- **Vue 3** with TypeScript
- **Radix Vue** components
- **TailwindCSS** styling
- Real-time progress tracking

### 🔐 Enterprise Security
- JWT authentication
- SSN/PAN encryption
- Audit logging
- Role-based access control

### 📊 Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | Vue 3 + TypeScript | Reactive UI |
| **State** | Pinia | State management |
| **UI Components** | Radix Vue | Accessible components |
| **Styling** | TailwindCSS | Utility-first CSS |
| **Backend** | FastAPI | High-performance API |
| **Database** | PostgreSQL 16+ | Relational data |
| **Vector DB** | pgvector | RAG embeddings |
| **ORM** | SQLAlchemy 2.0 | Database ORM |
| **AI Agents** | Microsoft AutoGen | Multi-agent system |
| **Embeddings** | sentence-transformers | Text embeddings |
| **LLM** | Multi-provider | OpenAI, Anthropic, etc. |
| **Local LLM** | Transformers + 4-bit quantization | Offline inference |

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+**
- **Node.js 18+**
- **PostgreSQL 16+** (or use Docker)
- **Git**

### 1. Clone Repository
```bash
git clone https://github.com/YOUR_USERNAME/tax-filing-agent.git
cd tax-filing-agent
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your API keys and settings

# Run migrations (if using Alembic)
alembic upgrade head

# Start backend
python main.py
```

### 3. Frontend Setup
```bash
# In project root (new terminal)
npm install
npm run dev
```

### 4. Database Setup (Docker)
```bash
# Start PostgreSQL with pgvector
docker-compose up -d

# Check status
docker-compose ps
```

### 5. Access Application
- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:8000/api/docs
- **PostgreSQL**: localhost:5432
- **pgAdmin**: http://localhost:5050

---

## 📁 Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/              # REST API endpoints
│   │   ├── agents/           # AutoGen AI agents
│   │   ├── core/             # Config, database, security
│   │   ├── models/           # SQLAlchemy models
│   │   ├── rag/              # RAG with pgvector
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # Business logic
│   │   └── websockets/       # WebSocket handlers
│   ├── alembic/              # Database migrations
│   ├── scripts/              # Utility scripts
│   ├── tests/                # Unit & integration tests
│   ├── main.py               # Application entry point
│   └── requirements.txt      # Python dependencies
│
├── src/
│   ├── components/           # Vue components
│   ├── pages/                # Route pages
│   ├── stores/               # Pinia stores
│   ├── composables/          # Vue composables
│   ├── lib/                  # Utilities
│   └── router.ts             # Vue Router config
│
├── docs/                     # Documentation
├── public/                   # Static assets
├── docker-compose.yml        # Docker services
└── package.json              # Node dependencies
```

---

## 🔧 Configuration

### Environment Variables

Edit `backend/.env`:

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/tax_filing_db

# Security
SECRET_KEY=your-secret-key-min-32-chars
ENCRYPTION_KEY=your-fernet-key

# LLM Providers
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# RAG Settings
EMBEDDING_MODEL=all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
RAG_TOP_K=3
```

---

## 🤖 AI Agent Architecture

### RAG with pgvector

**CRITICAL**: This project uses **pgvector ONLY** for vector storage.

```python
# Embedding ingestion
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
embedding = model.encode(text).tolist()  # 384-dim vector

# Similarity search
SELECT content, 1 - (embedding <=> :query_embedding) as similarity
FROM tax_embeddings
ORDER BY embedding <=> :query_embedding
LIMIT 3
```

### AutoGen Agents

- **orchestrator.py**: Coordinates agent workflow
- **tax_expert.py**: Tax calculations and advice
- **document_agent.py**: Document processing
- **compliance_agent.py**: Tax law validation
- **form_filler.py**: ITR-1 form generation

---

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/

# Run specific test
pytest tests/test_rag.py -v

# Frontend tests (if configured)
npm run test
```

---

## 📝 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register` | POST | User registration |
| `/api/auth/login` | POST | User login |
| `/api/tax-forms` | GET/POST | Tax form CRUD |
| `/api/documents/upload` | POST | Upload tax documents |
| `/api/filing/chat` | POST | Conversational filing |
| `/api/rag/query` | POST | Query tax knowledge base |

---

## 🐳 Docker Deployment

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v
```

---

## 🔒 Security Best Practices

1. **Never commit** `.env` files
2. Use **strong SECRET_KEY** (32+ chars)
3. Enable **HTTPS** in production
4. Set **ENVIRONMENT=production** in prod
5. Use **prepared statements** (SQLAlchemy ORM does this)
6. Encrypt sensitive data (PAN, Aadhaar)

---

## 🐛 Troubleshooting

### Database Connection Failed
```bash
# Check PostgreSQL is running
docker-compose ps

# Test connection
psql -h localhost -U taxagent -d tax_filing_db
```

### pgvector Extension Missing
```sql
-- Connect to database and run:
CREATE EXTENSION IF NOT EXISTS vector;
```

### Import Errors
```bash
# Ensure virtual environment is activated
cd backend
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Reinstall dependencies
pip install -r requirements.txt
```

---

## 📚 Documentation

- [AGENTS.md](AGENTS.md) - AI agent architecture
- [PHASE1_SETUP.md](PHASE1_SETUP.md) - Initial setup guide
- [implementation_plan.md](implementation_plan.md) - Development plan
- [walkthrough.md](walkthrough.md) - Feature walkthrough

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📄 License

This project is for educational purposes. See LICENSE file for details.

---

## ⚠️ Disclaimer

This is an **educational project**. For actual tax filing, consult a certified tax professional and use official government portals.

---

**Built with ❤️ for Indian taxpayers**
