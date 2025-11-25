"""
LangGraph Agent Nodes for Tax Filing Workflow

These nodes operate on TaxFilingState and are orchestrated by the graph.
They run in PARALLEL to the existing LangChain agents in src/agents/
"""
from typing import Dict, Any
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from .state import TaxFilingState
import os
from app.websockets.manager import manager


# ============================================================================
# Node 1: Interviewer Agent (Frontend Interface)
# ============================================================================

async def interviewer_node(state: TaxFilingState) -> Dict[str, Any]:
    """
    Extracts structured user data from natural language conversation.
    
    Role: The empathetic interface that asks clarifying questions
    Tech: GPT-4 with function calling to extract structured fields
    
    Args:
        state: Current graph state with conversation history
    
    Returns:
        Updated state with extracted user_profile
    """
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0.3,
        api_key=os.getenv("VITE_OPENAI_API_KEY")
    )
    
    # System prompt for structured extraction
    system_prompt = SystemMessage(content="""
    You are a tax filing assistant. Your job is to extract structured information 
    from the user's messages. Extract:
    - income_salary (float)
    - income_other (float) 
    - age (int)
    - filing_status (string: "individual" | "huf")
    - regime (string: "old" | "new")
    - deductions_80c (float, if mentioned)
    
    Respond in a friendly manner and ask for missing information.
    """)
    
    messages = [system_prompt] + state.get("messages", [])
    
    # Call LLM (simplified - in production, use function calling)
    response = llm.invoke(messages)
    
    # Parse response into user_profile (simplified)
    user_profile = state.get("user_profile", {})
    # TODO: Implement proper extraction logic
    user_profile["_last_message"] = response.content
    
    user_profile["_last_message"] = response.content
    
    await manager.broadcast({
        "type": "agent_activity",
        "agent": "Interviewer",
        "message": "Extracted user profile data from conversation."
    })
    
    return {
        "messages": [AIMessage(content=response.content)],
        "user_profile": user_profile,
        "current_agent": "interviewer"
    }


# ============================================================================
# Node 2: Researcher Agent (GraphRAG)
# ============================================================================

async def researcher_node(state: TaxFilingState) -> Dict[str, Any]:
    """
    Queries Neo4j Knowledge Graph for applicable tax codes.
    
    Role: The legal scholar that retrieves relevant statutes
    Tech: LlamaIndex PropertyGraphIndex with Neo4j backend
    
    Args:
        state: Current graph state with user_profile
    
    Returns:
        Updated state with research_results from knowledge graph
    """
    # Placeholder - will be implemented once Neo4j is running
    user_profile = state.get("user_profile", {})
    age = user_profile.get("age", 30)
    
    # Simulate graph query results
    research_results = [
        {
            "section": "80C",
            "description": "Deduction up to ₹1.5L for investments in PPF, ELSS, etc.",
            "applicable": True,
            "conditions": ["Available in Old Regime only"]
        },
        {
            "section": "80D",
            "description": "Health insurance premium deduction",
            "applicable": True,
            "conditions": [f"Senior citizen (age >= 60): {age >= 60}"]
        }
    ]
    
    # TODO: Replace with actual Neo4j query via LlamaIndex
    # from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
    # graph_store = Neo4jPropertyGraphStore(...)
    # query_engine = index.as_query_engine()
    # results = query_engine.query(f"Find deductions for age {age}")
    
    await manager.broadcast({
        "type": "agent_activity",
        "agent": "Researcher",
        "message": f"Found {len(research_results)} applicable tax sections."
    })

    return {
        "research_results": research_results,
        "current_agent": "researcher"
    }


# ============================================================================
# Node 3: Calculator Agent (Rust Engine Wrapper)
# ============================================================================

async def calculator_node(state: TaxFilingState) -> Dict[str, Any]:
    """
    Executes deterministic tax calculations using Rust engine.
    
    Role: The number cruncher with guaranteed precision
    Tech: Rust via PyO3 (NOT an LLM - no hallucination risk)
    
    Args:
        state: Current graph state with user_profile and research_results
    
    Returns:
        Updated state with calculation_result
    """
    user_profile = state.get("user_profile", {})
    
    # Placeholder - will call Rust engine once built
    # import tax_engine_rs
    # result = tax_engine_rs.calculate_tax(
    #     income=user_profile.get("income_salary", 0),
    #     age=user_profile.get("age", 30)
    # )
    
    # Simulate Rust calculation
    income = user_profile.get("income_salary", 0)
    deductions = user_profile.get("deductions_80c", 0)
    taxable_income = income - deductions
    
    # Simplified Indian tax slab (AY 2025-26)
    if taxable_income <= 300000:
        tax = 0
    elif taxable_income <= 700000:
        tax = (taxable_income - 300000) * 0.05
    elif taxable_income <= 1000000:
        tax = 20000 + (taxable_income - 700000) * 0.10
    elif taxable_income <= 1200000:
        tax = 50000 + (taxable_income - 1000000) * 0.15
    elif taxable_income <= 1500000:
        tax = 80000 + (taxable_income - 1200000) * 0.20
    else:
        tax = 140000 + (taxable_income - 1500000) * 0.30
    
    calculation_result = {
        "gross_income": income,
        "deductions": deductions,
        "taxable_income": taxable_income,
        "tax_liability": tax,
        "effective_tax_rate": (tax / income * 100) if income > 0 else 0
    }
    
    await manager.broadcast({
        "type": "agent_activity",
        "agent": "Calculator",
        "message": f"Calculated tax liability: ₹{tax}"
    })

    return {
        "calculation_result": calculation_result,
        "current_agent": "calculator"
    }


# ============================================================================
# Node 4: Auditor Agent (Metamorphic Testing)
# ============================================================================

async def auditor_node(state: TaxFilingState) -> Dict[str, Any]:
    """
    Validates the tax draft against legal invariants.
    
    Role: Internal QA that checks for logical inconsistencies
    Tech: Metamorphic testing (property-based validation)
    
    Args:
        state: Current graph state with calculation_result
    
    Returns:
        Updated state with audit_status and audit_errors
    """
    calculation = state.get("calculation_result", {})
    user_profile = state.get("user_profile", {})
    
    errors = []
    
    # Metamorphic Property 1: Deductions cannot exceed gross income
    gross = calculation.get("gross_income", 0)
    deductions = calculation.get("deductions", 0)
    if deductions > gross:
        errors.append("Deductions exceed gross income")
    
    # Metamorphic Property 2: Tax liability cannot be negative
    tax = calculation.get("tax_liability", 0)
    if tax < 0:
        errors.append("Negative tax liability detected")
    
    # Metamorphic Property 3: Taxable income should be non-negative
    taxable = calculation.get("taxable_income", 0)
    if taxable < 0:
        errors.append("Negative taxable income")
    
    # Metamorphic Property 4: Effective rate should be between 0-30%
    effective_rate = calculation.get("effective_tax_rate", 0)
    if effective_rate > 30:
        errors.append(f"Effective tax rate {effective_rate}% exceeds maximum 30%")
    
    audit_status = "passed" if len(errors) == 0 else "failed"
    
    audit_status = "passed" if len(errors) == 0 else "failed"
    
    await manager.broadcast({
        "type": "agent_activity",
        "agent": "Auditor",
        "message": f"Audit {audit_status}. {len(errors)} issues found."
    })
    
    return {
        "audit_status": audit_status,
        "audit_errors": errors if errors else None,
        "current_agent": "auditor"
    }
