import os
import chromadb
from chromadb.utils import embedding_functions

# Settings
PERSIST_DIRECTORY = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "chroma_db")
COLLECTION_NAME = "tax_rules"
DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "tax_rules.txt")

def ingest_data():
    print(f"Ingesting data from {DATA_FILE} into {PERSIST_DIRECTORY}")
    
    # Initialize Client
    client = chromadb.PersistentClient(path=PERSIST_DIRECTORY, settings=chromadb.Settings(anonymized_telemetry=False))
    
    # Embedding Function
    # Using sentence-transformers model
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    
    # Get or Create Collection
    # Delete if exists to start fresh
    try:
        client.delete_collection(name=COLLECTION_NAME)
    except ValueError:
        pass
        
    collection = client.create_collection(name=COLLECTION_NAME, embedding_function=sentence_transformer_ef)
    
    # Read Data
    if not os.path.exists(DATA_FILE):
        print(f"File {DATA_FILE} not found.")
        return

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        text = f.read()
    
    # Simple splitting by paragraphs
    documents = [chunk.strip() for chunk in text.split("\n\n") if chunk.strip()]
    ids = [f"rule_{i}" for i in range(len(documents))]
    metadatas = [{"source": "tax_rules.txt"} for _ in documents]
    
    if not documents:
        print("No documents found to ingest.")
        return

    # Add to collection
    collection.add(
        documents=documents,
        ids=ids,
        metadatas=metadatas
    )
    
    print(f"Successfully ingested {len(documents)} documents into {COLLECTION_NAME}")

if __name__ == "__main__":
    ingest_data()
