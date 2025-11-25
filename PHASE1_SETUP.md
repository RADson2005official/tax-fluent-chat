# Phase 1 Setup and Testing Guide

## Prerequisites
- Docker Desktop installed
- Python 3.10+
- Rust toolchain (optional, for building Rust engine)

## Step 1: Start Infrastructure

```powershell
# Start Neo4j and PostgreSQL
docker-compose up -d

# Verify services are running
docker ps
# You should see: tax-neo4j, tax-agent-db, tax-agent-pgadmin

# Access Neo4j Browser
# URL: http://localhost:7474
# Credentials: neo4j / taxpassword123

# Access pgAdmin
# URL: http://localhost:5050
# Credentials: admin@taxagent.com / admin123
```

## Step 2: Install Python Dependencies

```powershell
# Navigate to backend
cd backend

# Install Phase 1 dependencies
pip install -r requirements-phase1.txt

# Install existing dependencies (keep core functionality)
pip install -r requirements.txt
```

## Step 3: Initialize Database

```powershell
# The init.sql script runs automatically on first container start
# To manually run migrations:
docker exec -i tax-agent-db psql -U taxuser -d taxdb < db/init.sql
```

## Step 4: Ingest Tax Code into Neo4j

```powershell
# Run the knowledge graph ingestion script
python scripts/ingest_neo4j.py

# Expected output:
# 🔧 Building knowledge graph from tax documents...
# ✅ Knowledge graph created successfully!
```

## Step 5: Build Rust Engine (Optional)

```powershell
# Install Rust (if not already installed)
# https://www.rust-lang.org/tools/install

# Install maturin
pip install maturin

# Build the Rust engine
cd ../rust-engine
maturin develop --release

# Verify installation
python -c "import tax_engine_rs; print(tax_engine_rs.calculate_tax_indian(1000000, 30))"
```

## Step 6: Run Tests

```powershell
cd ../backend

# Run metamorphic tests
pytest tests/test_metamorphic.py -v

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

## Step 7: Start Backend (Development)

```powershell
# Option 1: Run existing backend (keeps core functionality)
uvicorn main:app --reload

# Option 2: Test LangGraph endpoints
python -m app.agents_v2.graph

# The backend will be available at:
# - Existing API: http://localhost:8000/api/*
# - New LangGraph API: http://localhost:8000/api/v2/filing/*
```

## Testing the Phase 1 Architecture

### Test LangGraph Workflow

```python
# test_langgraph.py
import requests

# Start a new filing session
response = requests.post("http://localhost:8000/api/v2/filing/start", json={
    "user_id": "test123",
    "initial_message": "I earn 12 lakh per year and I'm 35 years old"
})

thread_id = response.json()["thread_id"]
print(f"Thread ID: {thread_id}")

# Continue conversation
response = requests.post("http://localhost:8000/api/v2/filing/message", json={
    "thread_id": thread_id,
    "message": "I want to choose the new tax regime"
})

result = response.json()
print(f"Tax liability: ₹{result['calculation_result']['tax_liability']}")
```

### Test Rust Engine Directly

```python
import tax_engine_rs

# New regime
result = tax_engine_rs.calculate_tax_indian(
    income=1250000,
    age=35,
    regime="new"
)
print(f"New regime tax: ₹{result['tax_liability']}")

# Old regime with deductions
result = tax_engine_rs.calculate_tax_indian(
    income=1250000,
    age=35,
    regime="old",
    deductions_80c=150000,
    deductions_80d=25000
)
print(f"Old regime tax: ₹{result['tax_liability']}")
```

### Test GraphRAG Queries

```python
from llama_index.core import PropertyGraphIndex
from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore

graph_store = Neo4jPropertyGraphStore(
    username="neo4j",
    password="taxpassword123",
    url="bolt://localhost:7687"
)

# Query the graph
query_engine = graph_store.as_query_engine()
response = query_engine.query("What deductions are available for senior citizens?")
print(response)
```

## Parallel Architecture Notes

✅ **Core Functionality Preserved**:
- Existing agents in `src/agents/` remain untouched
- Existing API routes continue to work
- Frontend can still use original endpoints

🆕 **Phase 1 Additions**:
- New agents in `backend/app/agents_v2/`
- New API routes at `/api/v2/filing/*`
- Rust engine as optional performance boost
- Neo4j as optional knowledge graph

## Troubleshooting

### Neo4j Connection Error
```powershell
# Check if container is running
docker logs tax-neo4j

# Restart if needed
docker restart tax-neo4j
```

### PostgreSQL Extension Error
```powershell
# Manually enable pgvector
docker exec -it tax-agent-db psql -U taxuser -d taxdb
# IN PSQL:
CREATE EXTENSION IF NOT EXISTS vector;
\q
```

### Rust Build Errors
```powershell
# Ensure Rust is up to date
rustup update

# Clean and rebuild
cd rust-engine
cargo clean
maturin develop --release
```
