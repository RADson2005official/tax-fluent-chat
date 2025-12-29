<<<<<<< Updated upstream
# Automated Tax Filing Agent - LLM Rules

## Purpose
This file provides instructions for LLMs (GitHub Copilot, Claude, GPT, etc.) working on this codebase.
These rules ensure consistency and prevent unauthorized technology changes.

---

## APPROVED TECH STACK

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 16+ with pgvector extension
- **ORM**: SQLAlchemy 2.0 (async support)
- **Migrations**: Alembic
- **Vector Storage**: pgvector (PostgreSQL extension) - NO external vector DBs
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)
- **AI Agents**: Microsoft AutoGen
- **LLM Providers**: OpenAI, Anthropic, Google (Gemini), X.AI (via API)
- **Authentication**: JWT (python-jose), passlib with bcrypt
- **Validation**: Pydantic v2

### Frontend
- **Framework**: Vue 3 with Composition API
- **Language**: TypeScript (strict mode)
- **State Management**: Pinia
- **UI Components**: Radix Vue, shadcn-vue
- **Styling**: TailwindCSS
- **Build Tool**: Vite
- **HTTP Client**: Axios or native fetch

### Infrastructure
- **Container**: Docker with docker-compose
- **Database Image**: pgvector/pgvector:pg16
- **Python Environment**: venv or conda

---

## PROHIBITED TECHNOLOGIES

The following technologies are NOT approved for this project. Do NOT introduce them without explicit user approval:

### Vector Databases (Use pgvector instead)
- ❌ ChromaDB
- ❌ Pinecone
- ❌ Milvus
- ❌ Weaviate
- ❌ Qdrant
- ❌ FAISS (as primary storage)

### Alternative Databases
- ❌ MongoDB
- ❌ Redis (for primary data storage)
- ❌ Elasticsearch (for vector search)
- ❌ Neo4j (unless specifically for GraphRAG feature)

### Alternative Frameworks
- ❌ Django (use FastAPI)
- ❌ Flask (use FastAPI)
- ❌ React (use Vue 3)
- ❌ Next.js (use Vite + Vue)
- ❌ Angular

### Alternative AI/ML
- ❌ LangChain (for agent orchestration - use AutoGen)
- ❌ LlamaIndex (unless for specific GraphRAG feature)
- ❌ Haystack

---

## RULES FOR LLMs

### Before Adding Dependencies
1. Check if functionality exists in approved tech stack
2. Verify the dependency is actively maintained
3. Consider bundle size impact (frontend) or memory footprint (backend)
4. ASK USER before adding any new pip/npm dependency

### Code Style
- Use async/await for all database operations
- Use Pydantic models for API request/response validation
- Use SQLAlchemy ORM models (not raw SQL) where possible
- Follow existing project structure and naming conventions

### Database Operations
- All vector operations MUST use pgvector
- Use SQLAlchemy async sessions for new code
- Create Alembic migrations for schema changes
- Never hardcode database credentials

### Security
- Never commit API keys or secrets
- Use environment variables for all configuration
- Encrypt sensitive data (SSN, etc.) at rest
- Validate all user inputs

### Documentation
- Update docstrings when modifying functions
- Keep README.md current with setup instructions
- Document breaking changes in commit messages

---

## WHEN IN DOUBT

If you're unsure whether a technology or approach is appropriate:
1. **ASK THE USER** before proceeding
2. Explain the trade-offs of different approaches
3. Suggest alternatives from the approved stack
4. Document the decision rationale

---

## VERSION HISTORY

- 2024-12-28: Initial rules file created
  - Established pgvector as the only vector database
  - Removed ChromaDB from approved stack
  - Documented prohibited technologies
=======
# LLM Rules for Tax Filing Agent

## Approved Stack

### Backend
- FastAPI (Python 3.11+)
- PostgreSQL 16+ with **pgvector**
- SQLAlchemy 2.0, Alembic
- Microsoft AutoGen
- sentence-transformers

### Frontend  
- Vue 3 (Composition API)
- TypeScript, Pinia, TailwindCSS, Vite

## ❌ PROHIBITED

**Vector DBs** (use pgvector):
- ChromaDB, Pinecone, Milvus, Weaviate, Qdrant

**Frameworks**:
- React, Django, Flask, LangChain (for agents)

## Rules

1. **ASK before adding dependencies**
2. Use async/await for DB operations
3. Use Pydantic for API validation
4. Never hardcode credentials
5. Vector operations MUST use pgvector:

```python
# Correct - pgvector
from sqlalchemy import text
result = db.execute(text("""
    SELECT content, 1 - (embedding <=> :emb::vector) as similarity
    FROM tax_embeddings
    ORDER BY embedding <=> :emb::vector LIMIT 3
"""), {"emb": embedding_str})
```

## File Locations

- Models: `backend/app/models.py`
- CRUD: `backend/app/crud.py`
- RAG: `backend/app/rag/`
- Agents: `backend/app/autogen_agents/`
- Vue components: `src/components-vue/` (NOT src/components)
>>>>>>> Stashed changes
