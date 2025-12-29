"""Add pgvector embedding tables

Revision ID: 001_pgvector
Revises: 
Create Date: 2024-12-28

This migration:
1. Enables the pgvector extension
2. Creates tax_embeddings table for RAG
3. Creates document_embeddings table for user documents
4. Adds HNSW indexes for fast similarity search
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_pgvector'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create pgvector extension and embedding tables.
    """
    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # Create tax_embeddings table
    op.execute('''
        CREATE TABLE IF NOT EXISTS tax_embeddings (
            id SERIAL PRIMARY KEY,
            content TEXT NOT NULL,
            embedding vector(384) NOT NULL,
            metadata JSONB DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    ''')
    
    # Create document_embeddings table
    op.execute('''
        CREATE TABLE IF NOT EXISTS document_embeddings (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            document_type VARCHAR(50) NOT NULL,
            document_id INTEGER,
            content TEXT NOT NULL,
            embedding vector(384) NOT NULL,
            metadata JSONB DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    ''')
    
    # Create indexes for user_id lookup
    op.execute('''
        CREATE INDEX IF NOT EXISTS idx_document_embeddings_user_id 
        ON document_embeddings(user_id)
    ''')
    
    # Create HNSW indexes for fast similarity search
    # HNSW is better than IVFFlat for most use cases (faster queries, no training needed)
    op.execute('''
        CREATE INDEX IF NOT EXISTS idx_tax_embeddings_hnsw 
        ON tax_embeddings 
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
    ''')
    
    op.execute('''
        CREATE INDEX IF NOT EXISTS idx_document_embeddings_hnsw 
        ON document_embeddings 
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
    ''')
    
    print("✅ pgvector extension enabled and embedding tables created with HNSW indexes")


def downgrade() -> None:
    """
    Drop embedding tables (keeps pgvector extension as it may be used elsewhere).
    """
    op.execute('DROP INDEX IF EXISTS idx_document_embeddings_hnsw')
    op.execute('DROP INDEX IF EXISTS idx_tax_embeddings_hnsw')
    op.execute('DROP INDEX IF EXISTS idx_document_embeddings_user_id')
    op.execute('DROP TABLE IF EXISTS document_embeddings')
    op.execute('DROP TABLE IF EXISTS tax_embeddings')
    # Note: We don't drop the vector extension as other tables might use it
    print("✅ Embedding tables dropped")
