# GitHub Copilot Instructions for Automated Tax Filing Agent

## Project Overview
This is an automated tax filing system for Indian taxes using AI agents.

## Approved Technology Stack

### Backend
- FastAPI (Python 3.11+)
- PostgreSQL 16+ with **pgvector** extension (vector database)
- SQLAlchemy 2.0 async
- Alembic for migrations
- Microsoft AutoGen for AI agents
- sentence-transformers for embeddings

### Frontend  
- Vue 3 with Composition API
- TypeScript (strict)
- Pinia, Radix Vue, TailwindCSS
- Vite

## Critical Rules

### Vector Storage
**ALWAYS use pgvector for vector operations.** Do NOT suggest or add:
- ChromaDB ❌
- Pinecone ❌
- Milvus ❌
- Weaviate ❌
- Qdrant ❌

### Dependencies
Before suggesting new dependencies:
1. Check if approved stack already provides functionality
2. Explicitly ask user for approval
3. Prefer standard library when possible

### Database
- Use SQLAlchemy ORM with async sessions
- All vector columns use `vector(384)` type
- Use HNSW index for similarity search
- Create Alembic migrations for schema changes

### Code Style
- Async/await for all database operations
- Pydantic models for API validation
- Type hints on all functions
- Docstrings for public functions

## File Structure
```
backend/
  app/
    models.py      - SQLAlchemy models (including TaxEmbedding)
    crud_async.py  - Async CRUD operations
    rag/
      ingest.py    - Embedding ingestion
      retriever.py - Similarity search
```

## Common Patterns

### Vector Search (pgvector)
```python
# Cosine similarity search
result = db.execute(text("""
    SELECT content, 1 - (embedding <=> :embedding::vector) as similarity
    FROM tax_embeddings
    ORDER BY embedding <=> :embedding::vector
    LIMIT :limit
"""), {"embedding": embedding_str, "limit": 3})
```

### Embedding Generation
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
embedding = model.encode(text).tolist()  # Returns 384-dim vector
```
