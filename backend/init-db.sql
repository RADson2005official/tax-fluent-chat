-- Initialize Tax Filing Database
-- This script runs automatically when the PostgreSQL container starts

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";  -- pgvector for embeddings

-- Create schema for better organization
CREATE SCHEMA IF NOT EXISTS tax_data;

-- Set search path
SET search_path TO tax_data, public;

-- Initial grants (more will be added as we create tables)
GRANT USAGE ON SCHEMA tax_data TO taxagent;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA tax_data TO taxagent;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA tax_data TO taxagent;

-- =============================================================================
-- pgvector Embedding Tables
-- =============================================================================

-- Tax rules/documents embeddings for RAG
CREATE TABLE IF NOT EXISTS tax_embeddings (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(384) NOT NULL,  -- all-MiniLM-L6-v2 = 384 dimensions
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User document embeddings for semantic search
CREATE TABLE IF NOT EXISTS document_embeddings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    document_type VARCHAR(50) NOT NULL,
    document_id INTEGER,
    content TEXT NOT NULL,
    embedding vector(384) NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for user_id lookup
CREATE INDEX IF NOT EXISTS idx_document_embeddings_user_id 
ON document_embeddings(user_id);

-- Create HNSW indexes for fast similarity search
-- HNSW provides better query performance than IVFFlat
CREATE INDEX IF NOT EXISTS idx_tax_embeddings_hnsw 
ON tax_embeddings 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

CREATE INDEX IF NOT EXISTS idx_document_embeddings_hnsw 
ON document_embeddings 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'Tax Filing Database initialized successfully with pgvector support';
END $$;
