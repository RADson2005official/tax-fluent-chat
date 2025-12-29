"""PostgreSQL pgvector-based Tax RAG Retriever.

Provides semantic search over tax rules stored in PostgreSQL with pgvector.
Uses sentence-transformers for embeddings and SQLAlchemy for database access.
"""

import os
from typing import List, Optional, Dict, Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sentence_transformers import SentenceTransformer

# Use the database from app.database
from app.core.database import SessionLocal
from app.core.config import Settings

# Load settings
settings = Settings()

# Embedding configuration from centralized config
EMBEDDING_MODEL = settings.EMBEDDING_MODEL
EMBEDDING_DIMENSION = settings.EMBEDDING_DIMENSION
DEFAULT_TOP_K = settings.RAG_TOP_K


class TaxRetriever:
    """
    PostgreSQL pgvector-based retriever for tax rules.
    
    Features:
    - Lazy-loaded embedding model for efficient memory usage
    - Configurable similarity threshold and result count
    - Both sync and async retrieval methods
    - Support for metadata filtering
    """
    
    def __init__(self, top_k: int = DEFAULT_TOP_K):
        self._model: Optional[SentenceTransformer] = None
        self.top_k = top_k
    
    @property
    def model(self) -> SentenceTransformer:
        """Lazy load embedding model."""
        if self._model is None:
            print(f"[TaxRetriever] Loading embedding model: {EMBEDDING_MODEL}")
            self._model = SentenceTransformer(EMBEDDING_MODEL)
        return self._model
    
    def _get_embedding(self, text_input: str) -> List[float]:
        """Generate embedding for text."""
        return self.model.encode(text_input).tolist()
    
    def _format_embedding(self, embedding: List[float]) -> str:
        """Format embedding list as pgvector string."""
        return "[" + ",".join(str(x) for x in embedding) + "]"
    
    def retrieve(self, query: str, n_results: Optional[int] = None) -> List[str]:
        """
        Retrieve most relevant tax rules for a query using pgvector similarity.
        
        Args:
            query: User query text
            n_results: Number of results to return (defaults to self.top_k)
            
        Returns:
            List of relevant document contents
        """
        n_results = n_results or self.top_k
        
        try:
            query_embedding = self._get_embedding(query)
            embedding_str = self._format_embedding(query_embedding)
            
            db = SessionLocal()
            try:
                result = db.execute(
                    text("""
                        SELECT content, 1 - (embedding <=> :embedding::vector) as similarity
                        FROM tax_embeddings
                        ORDER BY embedding <=> :embedding::vector
                        LIMIT :limit
                    """),
                    {"embedding": embedding_str, "limit": n_results}
                )
                
                documents = [row[0] for row in result.fetchall()]
                return documents
                
            finally:
                db.close()
                
        except Exception as e:
            print(f"[TaxRetriever] Error retrieving documents: {e}")
            return []
    
    def retrieve_with_scores(
        self, 
        query: str, 
        n_results: Optional[int] = None,
        min_similarity: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Retrieve documents with similarity scores.
        
        Args:
            query: User query text
            n_results: Number of results to return
            min_similarity: Minimum similarity threshold (0.0-1.0)
            
        Returns:
            List of dicts with 'content', 'similarity', 'metadata'
        """
        n_results = n_results or self.top_k
        
        try:
            query_embedding = self._get_embedding(query)
            embedding_str = self._format_embedding(query_embedding)
            
            db = SessionLocal()
            try:
                result = db.execute(
                    text("""
                        SELECT content, metadata, 1 - (embedding <=> :embedding::vector) as similarity
                        FROM tax_embeddings
                        WHERE 1 - (embedding <=> :embedding::vector) >= :min_sim
                        ORDER BY embedding <=> :embedding::vector
                        LIMIT :limit
                    """),
                    {
                        "embedding": embedding_str,
                        "limit": n_results,
                        "min_sim": min_similarity
                    }
                )
                
                return [
                    {"content": row[0], "metadata": row[1], "similarity": row[2]}
                    for row in result.fetchall()
                ]
                
            finally:
                db.close()
                
        except Exception as e:
            print(f"[TaxRetriever] Error retrieving documents with scores: {e}")
            return []
    
    async def retrieve_async(
        self, 
        db: AsyncSession, 
        query: str, 
        n_results: Optional[int] = None
    ) -> List[str]:
        """
        Async version of retrieve for FastAPI endpoints.
        
        Args:
            db: AsyncSession from dependency injection
            query: User query text
            n_results: Number of results to return
            
        Returns:
            List of relevant document contents
        """
        from app.crud_async import search_tax_embeddings_async
        
        n_results = n_results or self.top_k
        query_embedding = self._get_embedding(query)
        
        results = await search_tax_embeddings_async(db, query_embedding, n_results)
        return [r["content"] for r in results]
    
    def get_document_count(self) -> int:
        """Get number of documents in the embeddings table."""
        db = SessionLocal()
        try:
            result = db.execute(text("SELECT COUNT(*) FROM tax_embeddings"))
            return result.scalar() or 0
        finally:
            db.close()
    
    async def get_document_count_async(self, db: AsyncSession) -> int:
        """Async version of get_document_count."""
        from app.crud_async import get_tax_embedding_count_async
        return await get_tax_embedding_count_async(db)


# Singleton instance
_retriever: Optional[TaxRetriever] = None


def get_tax_retriever() -> TaxRetriever:
    """Get or create the TaxRetriever singleton."""
    global _retriever
    if _retriever is None:
        _retriever = TaxRetriever()
    return _retriever


def reset_retriever():
    """Reset the singleton (useful for testing)."""
    global _retriever
    _retriever = None


if __name__ == "__main__":
    # Test retrieval
    retriever = TaxRetriever()
    print(f"Document count: {retriever.get_document_count()}")
    
    # Test basic retrieval
    results = retriever.retrieve("What is the tax slab for 10 lakhs?")
    print(f"Results: {results}")
    
    # Test retrieval with scores
    results_with_scores = retriever.retrieve_with_scores(
        "What is the tax slab for 10 lakhs?",
        min_similarity=0.3
    )
    for r in results_with_scores:
        print(f"Similarity: {r['similarity']:.3f} - {r['content'][:100]}...")
