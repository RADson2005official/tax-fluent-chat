import os
import chromadb
from chromadb.utils import embedding_functions

PERSIST_DIRECTORY = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "chroma_db")
COLLECTION_NAME = "tax_rules"

class TaxRetriever:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=PERSIST_DIRECTORY, settings=chromadb.Settings(anonymized_telemetry=False))
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        self.collection = self.client.get_collection(name=COLLECTION_NAME, embedding_function=self.embedding_function)

    def retrieve(self, query: str, n_results: int = 3) -> list[str]:
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            return results['documents'][0] if results['documents'] else []
        except Exception as e:
            print(f"Error retrieving documents: {e}")
            return []

if __name__ == "__main__":
    retriever = TaxRetriever()
    results = retriever.retrieve("What is the tax slab for 10 lakhs?")
    print("Results:", results)
