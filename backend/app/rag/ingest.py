"""PostgreSQL pgvector-based Tax Rules Ingestion.

Ingests tax rules from text file into PostgreSQL with pgvector embeddings.
Uses SQLAlchemy ORM with pgvector extension for vector storage.
"""

import os
import json
from typing import List, Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sentence_transformers import SentenceTransformer

from app.database import SessionLocal
from app.config import Settings

# Load settings
settings = Settings()

# Settings from config
DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "tax_rules.txt")
EMBEDDING_MODEL = settings.EMBEDDING_MODEL
EMBEDDING_DIMENSION = settings.EMBEDDING_DIMENSION


def get_embedding_model() -> SentenceTransformer:
    """Load and cache the embedding model."""
    print(f"[Ingest] Loading embedding model: {EMBEDDING_MODEL}")
    return SentenceTransformer(EMBEDDING_MODEL)


def ingest_data(data_file: Optional[str] = None):
    """
    Ingest tax rules into PostgreSQL with pgvector embeddings.
    
    Args:
        data_file: Optional path to data file. Defaults to tax_rules.txt
    """
    file_path = data_file or DATA_FILE
    model = get_embedding_model()
    
    print(f"[Ingest] Reading data from: {file_path}")
    
    # Read data file
    if not os.path.exists(file_path):
        print(f"[Ingest] ERROR: File {file_path} not found.")
        return
    
    with open(file_path, "r", encoding="utf-8") as f:
        text_content = f.read()
    
    # Split into paragraphs
    documents = [chunk.strip() for chunk in text_content.split("\n\n") if chunk.strip()]
    
    if not documents:
        print("[Ingest] No documents found to ingest.")
        return
    
    print(f"[Ingest] Found {len(documents)} documents to ingest")
    
    # Generate embeddings
    print("[Ingest] Generating embeddings...")
    embeddings = model.encode(documents)
    
    # Verify embedding dimension
    if embeddings.shape[1] != EMBEDDING_DIMENSION:
        print(f"[Ingest] WARNING: Embedding dimension mismatch. Expected {EMBEDDING_DIMENSION}, got {embeddings.shape[1]}")
    
    # Insert into PostgreSQL using SQLAlchemy
    db = SessionLocal()
    try:
        # Clear existing data
        db.execute(text("DELETE FROM tax_embeddings"))
        db.commit()
        print("[Ingest] Cleared existing embeddings")
        
        # Insert new embeddings
        for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
            # Format embedding as pgvector expects: [1.0, 2.0, 3.0, ...]
            embedding_list = embedding.tolist()
            embedding_str = "[" + ",".join(str(x) for x in embedding_list) + "]"
            metadata = json.dumps({
                "source": os.path.basename(file_path),
                "chunk_id": i,
                "total_chunks": len(documents)
            })
            
            # Insert using parameterized query
            sql = text("""
                INSERT INTO tax_embeddings (content, embedding, metadata)
                VALUES (:content, :embedding::vector, :metadata::jsonb)
            """)
            db.execute(sql, {
                "content": doc,
                "embedding": embedding_str,
                "metadata": metadata
            })
            
            # Progress indicator every 50 documents
            if (i + 1) % 50 == 0:
                print(f"[Ingest] Processed {i + 1}/{len(documents)} documents...")
        
        db.commit()
        print(f"[Ingest] Successfully ingested {len(documents)} documents into PostgreSQL")
        
        # Verify count
        result = db.execute(text("SELECT COUNT(*) FROM tax_embeddings"))
        count = result.scalar()
        print(f"[Ingest] Verified: {count} documents in tax_embeddings table")
        
    except Exception as e:
        print(f"[Ingest] ERROR: {e}")
        db.rollback()
        raise
    finally:
        db.close()


async def ingest_data_async(db: AsyncSession, data_file: Optional[str] = None):
    """
    Async version of ingest_data for use with FastAPI endpoints.
    
    Args:
        db: AsyncSession from dependency injection
        data_file: Optional path to data file
    """
    from app.crud_async import bulk_create_tax_embeddings_async
    
    file_path = data_file or DATA_FILE
    model = get_embedding_model()
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Data file not found: {file_path}")
    
    with open(file_path, "r", encoding="utf-8") as f:
        text_content = f.read()
    
    documents = [chunk.strip() for chunk in text_content.split("\n\n") if chunk.strip()]
    
    if not documents:
        return 0
    
    embeddings = model.encode(documents)
    
    # Prepare data for bulk insert
    embeddings_data = [
        {
            "content": doc,
            "embedding": emb.tolist(),
            "metadata": {
                "source": os.path.basename(file_path),
                "chunk_id": i,
                "total_chunks": len(documents)
            }
        }
        for i, (doc, emb) in enumerate(zip(documents, embeddings))
    ]
    
    count = await bulk_create_tax_embeddings_async(db, embeddings_data)
    return count


if __name__ == "__main__":
    ingest_data()
