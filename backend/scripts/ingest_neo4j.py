"""
Neo4j Knowledge Graph Ingestion Script

This script ingests the Indian Tax Code (ITR-1 sections, deductions, etc.)
into a Neo4j graph database for GraphRAG queries.

Nodes represent concepts (Sections, Deductions, Forms, etc.)
Edges represent relationships (ALLOWS, EXCLUDES, REQUIRES, etc.)
"""
from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
from llama_index.core import PropertyGraphIndex
import os


# ============================================================================
# Sample Tax Code Documents (ITR-1 Sahaj for AY 2025-26)
# ============================================================================

tax_documents = [
    Document(
        text="""
        Section 80C of the Income Tax Act allows deductions up to ₹1,50,000 for 
        investments in specified instruments including:
        - Public Provident Fund (PPF)
        - Equity Linked Savings Scheme (ELSS)
        - National Savings Certificate (NSC)
        - Life Insurance Premium
        - Employee Provident Fund (EPF)
        
        This deduction is ONLY available under the Old Tax Regime.
        The New Tax Regime (Section 115BAC) explicitly excludes Section 80C deductions.
        """,
        metadata={"section": "80C", "regime": "old", "max_deduction": 150000}
    ),
    Document(
        text="""
        Section 80D allows deduction for health insurance premium:
        - For self, spouse, and dependent children: Up to ₹25,000
        - For senior citizens (age >= 60): Up to ₹50,000
        - Additional ₹5,000 for preventive health checkup
        
        This is available in the Old Tax Regime only.
        """,
        metadata={"section": "80D", "regime": "old", "condition": "age_based"}
    ),
    Document(
        text="""
        Section 115BAC (New Tax Regime) offers lower tax rates but removes most deductions.
        Tax slabs:
        - Up to ₹3,00,000: Nil
        - ₹3,00,001 to ₹7,00,000: 5%
        - ₹7,00,001 to ₹10,00,000: 10%
        - ₹10,00,001 to ₹12,00,000: 15%
        - ₹12,00,001 to ₹15,00,000: 20%
        - Above ₹15,00,000: 30%
        
        Deductions NOT allowed: 80C, 80CCD(1B), 80D, HRA, LTA, etc.
        Only Standard Deduction of ₹50,000 is allowed.
        """,
        metadata={"section": "115BAC", "regime": "new", "standard_deduction": 50000}
    ),
    Document(
        text="""
        ITR-1 SAHAJ form structure:
        - Part A: General Information (PAN, Name, Address, etc.)
        - Part B: Gross Total Income
          - Salary (as per Form 16)
          - Income from Other Sources (Bank Interest, etc.)
        - Part C: Deductions (if Old Regime chosen)
        - Part D: Tax Computation and Tax Status
        
        Eligibility for ITR-1:
        - Indian resident individual
        - Total income up to ₹50 lakh
        - Income from Salary and/or One House Property
        """,
        metadata={"form": "ITR-1", "eligibility": "salary_house_property"}
    ),
    Document(
        text="""
        HRA (House Rent Allowance) exemption:
        - Available only in Old Tax Regime
        - Calculated as minimum of:
          1. Actual HRA received
          2. Rent paid - 10% of salary
          3. 50% of salary (metro) or 40% (non-metro)
        
        NOT available if:
        - New Tax Regime is chosen
        - Individual owns the house in which residing
        """,
        metadata={"exemption": "HRA", "regime": "old", "condition": "rented_house"}
    )
]


def ingest_tax_code():
    """
    Ingests tax documents into Neo4j as a knowledge graph.
    
    Returns:
        PropertyGraphIndex: The created graph index
    """
    # Connect to Neo4j
    neo4j_url = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password = os.getenv("NEO4J_PASSWORD", "taxpassword123")
    
    graph_store = Neo4jPropertyGraphStore(
        username=neo4j_user,
        password=neo4j_password,
        url=neo4j_url
    )
    
    # Initialize LLM and Embedding model
    llm = OpenAI(
        model="gpt-4",
        api_key=os.getenv("VITE_OPENAI_API_KEY")
    )
    
    embed_model = OpenAIEmbedding(
        model="text-embedding-ada-002",
        api_key=os.getenv("VITE_OPENAI_API_KEY")
    )
    
    # Create the graph index
    print("🔧 Building knowledge graph from tax documents...")
    
    index = PropertyGraphIndex.from_documents(
        documents=tax_documents,
        property_graph_store=graph_store,
        llm=llm,
        embed_model=embed_model,
        show_progress=True
    )
    
    print("✅ Knowledge graph created successfully!")
    print(f"   Neo4j Browser: http://localhost:7474")
    print(f"   Credentials: {neo4j_user} / {neo4j_password}")
    
    return index


def test_graph_queries(index: PropertyGraphIndex):
    """
    Tests multi-hop queries on the knowledge graph.
    """
    query_engine = index.as_query_engine(
        include_text=True,
        similarity_top_k=5
    )
    
    print("\n🧪 Testing Knowledge Graph Queries:\n")
    
    # Query 1: New Regime exclusions
    print("Q1: Can I claim HRA deduction in the New Tax Regime?")
    response = query_engine.query(
        "What deductions are excluded if I choose the New Tax Regime (Section 115BAC)?"
    )
    print(f"A1: {response}\n")
    
    # Query 2: Senior citizen benefits
    print("Q2: What additional benefits do senior citizens get?")
    response = query_engine.query(
        "What are the tax deductions available for senior citizens aged 65?"
    )
    print(f"A2: {response}\n")
    
    # Query 3: ITR-1 eligibility
    print("Q3: Can I use ITR-1 for my filing?")
    response = query_engine.query(
        "What is the eligibility criteria for filing ITR-1 SAHAJ?"
    )
    print(f"A3: {response}\n")


if __name__ == "__main__":
    try:
        # Check if Neo4j is running
        import neo4j
        driver = neo4j.GraphDatabase.driver(
            "bolt://localhost:7687",
            auth=("neo4j", "taxpassword123")
        )
        driver.verify_connectivity()
        driver.close()
        
        # Ingest and test
        index = ingest_tax_code()
        test_graph_queries(index)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Make sure Neo4j is running:")
        print("   docker-compose up -d neo4j")
