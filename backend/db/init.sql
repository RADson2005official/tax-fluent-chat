-- Phase 1: LangGraph Checkpoint Tables
CREATE EXTENSION IF NOT EXISTS vector;

-- LangGraph state persistence
CREATE TABLE IF NOT EXISTS langgraph_checkpoints (
    thread_id TEXT NOT NULL,
    checkpoint_id TEXT NOT NULL,
    parent_checkpoint_id TEXT,
    checkpoint JSONB NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (thread_id, checkpoint_id)
);

CREATE INDEX idx_checkpoints_thread ON langgraph_checkpoints(thread_id);
CREATE INDEX idx_checkpoints_parent ON langgraph_checkpoints(parent_checkpoint_id);

-- Tax filing drafts with versioning
CREATE TABLE IF NOT EXISTS tax_drafts (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    thread_id TEXT NOT NULL,
    itr_data JSONB NOT NULL,
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'in_progress', 'completed', 'filed')),
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_drafts_user ON tax_drafts(user_id);
CREATE INDEX idx_drafts_thread ON tax_drafts(thread_id);

-- Tax code embeddings for hybrid search (GraphRAG + Vector)
CREATE TABLE IF NOT EXISTS tax_code_embeddings (
    id SERIAL PRIMARY KEY,
    section_name TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536),  -- OpenAI ada-002 dimension
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_embeddings_section ON tax_code_embeddings(section_name);
CREATE INDEX idx_embeddings_vector ON tax_code_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Agent execution logs for observability
CREATE TABLE IF NOT EXISTS agent_execution_logs (
    id SERIAL PRIMARY KEY,
    thread_id TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    node_name TEXT NOT NULL,
    input_data JSONB,
    output_data JSONB,
    execution_time_ms INTEGER,
    status TEXT CHECK (status IN ('success', 'error', 'timeout')),
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_logs_thread ON agent_execution_logs(thread_id);
CREATE INDEX idx_logs_agent ON agent_execution_logs(agent_name);
CREATE INDEX idx_logs_created ON agent_execution_logs(created_at DESC);
