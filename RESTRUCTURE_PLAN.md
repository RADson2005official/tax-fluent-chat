# Project Restructure Plan - Tax Filing Agent

## Critical Issues Fixed

### 1. **Remove React Dependencies** (Frontend Confusion)
- Package.json has BOTH React AND Vue
- Removing ALL React dependencies
- Keeping only Vue 3 + TypeScript stack

### 2. **Backend Structure** 
```
backend/
├── app/
│   ├── api/              # REST endpoints
│   ├── agents/           # Merged autogen_agents + agents_v2
│   ├── core/             # config, database, security
│   ├── models/           # SQLAlchemy models
│   ├── rag/              # pgvector RAG only
│   ├── schemas/          # Pydantic schemas
│   └── services/         # Business logic
├── alembic/              # Migrations
├── tests/                # All tests here
├── scripts/              # Utility scripts
├── main.py               # Single entry point
└── requirements.txt      # Dependencies
```

### 3. **Removed Files**
- backend/main.py (duplicate)
- backend/test_*.py (moved to tests/)
- backend/debug_*.py (useless)
- backend/check_imports.py
- backend/verify_*.py (root level - moved to scripts/)
- rust-engine/ (incomplete, unused)
- Neo4j from docker-compose

### 4. **Fixed Docker**
- Removed Neo4j (pgvector only per guidelines)
- Added proper healthchecks
- Environment variables standardized

### 5. **Dependencies Optimized**
- Removed React (59 packages!)
- Removed duplicate/unused Python packages
- Added missing essential packages for RAG

### 6. **Frontend Structure**
```
src/
├── components/           # Shared Vue components
├── pages/               # Route pages
├── stores/              # Pinia state
├── composables/         # Vue composables
├── lib/                 # Utilities
└── router.ts            # Vue Router
```

## Implementation Order

1. ✅ Create backup
2. ⏳ Clean package.json (remove React)
3. ⏳ Restructure backend/app
4. ⏳ Remove useless files
5. ⏳ Fix docker-compose.yml
6. ⏳ Update imports
7. ⏳ Create .env from .env.example
8. ⏳ Test database connection
9. ⏳ Test API endpoints
10. ⏳ Test RAG functionality

## Key Principles Applied

1. **pgvector ONLY** for vector storage (no ChromaDB/Neo4j)
2. **Vue 3 ONLY** for frontend (no React)
3. **Single responsibility** per module
4. **Async-first** database operations
5. **Type safety** with Pydantic + TypeScript
