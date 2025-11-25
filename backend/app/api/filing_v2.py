"""
FastAPI Router for LangGraph Tax Filing (Phase 1)

This runs PARALLEL to the existing API routes.
Existing frontend can continue using /api/agents/* endpoints.
New clients (or frontend v2) can use /api/v2/filing/* endpoints.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from langchain_core.messages import HumanMessage
from ..agents_v2.graph import tax_filing_graph
import uuid

router = APIRouter(prefix="/api/v2/filing", tags=["Tax Filing v2 (LangGraph)"])


# ============================================================================
# Request/Response Models
# ============================================================================

class FilingStartRequest(BaseModel):
    """Request to start a new filing session"""
    user_id: str
    initial_message: Optional[str] = "I want to file my taxes"


class FilingMessageRequest(BaseModel):
    """Request to send a message in an existing session"""
    thread_id: str
    message: str


class FilingResponse(BaseModel):
    """Response from the filing system"""
    thread_id: str
    messages: List[Dict[str, Any]]
    user_profile: Optional[Dict[str, Any]] = None
    calculation_result: Optional[Dict[str, Any]] = None
    audit_status: Optional[str] = None
    audit_errors: Optional[List[str]] = None


# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/start", response_model=FilingResponse)
async def start_filing(request: FilingStartRequest):
    """
    Start a new tax filing session.
    
    Creates a new thread and invokes the LangGraph with the initial message.
    The conversation state is persisted to PostgreSQL.
    """
    # Generate unique thread ID for this session
    thread_id = f"tax-{request.user_id}-{uuid.uuid4().hex[:8]}"
    
    # Configuration for LangGraph (enables checkpointing)
    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }
    
    # Initial state
    initial_state = {
        "messages": [HumanMessage(content=request.initial_message)],
        "thread_id": thread_id,
        "user_profile": {},
        "tax_draft": {},
        "research_results": None,
        "calculation_result": None,
        "audit_status": None,
        "audit_errors": None
    }
    
    try:
        # Invoke the graph
        result = await tax_filing_graph.ainvoke(initial_state, config=config)
        
        return FilingResponse(
            thread_id=thread_id,
            messages=[{"role": m.type, "content": m.content} for m in result.get("messages", [])],
            user_profile=result.get("user_profile"),
            calculation_result=result.get("calculation_result"),
            audit_status=result.get("audit_status"),
            audit_errors=result.get("audit_errors")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graph execution failed: {str(e)}")


@router.post("/message", response_model=FilingResponse)
async def send_message(request: FilingMessageRequest):
    """
    Continue an existing filing session.
    
    Retrieves the persisted state from PostgreSQL and continues the graph.
    """
    config = {
        "configurable": {
            "thread_id": request.thread_id
        }
    }
    
    # New message to append
    new_message = HumanMessage(content=request.message)
    
    try:
        # Get current state from checkpoint
        current_state = await tax_filing_graph.aget_state(config)
        
        if not current_state:
            raise HTTPException(status_code=404, detail="Thread not found")
        
        # Update state with new message
        updated_state = {
            **current_state.values,
            "messages": current_state.values.get("messages", []) + [new_message]
        }
        
        # Continue the graph
        result = await tax_filing_graph.ainvoke(updated_state, config=config)
        
        return FilingResponse(
            thread_id=request.thread_id,
            messages=[{"role": m.type, "content": m.content} for m in result.get("messages", [])],
            user_profile=result.get("user_profile"),
            calculation_result=result.get("calculation_result"),
            audit_status=result.get("audit_status"),
            audit_errors=result.get("audit_errors")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graph execution failed: {str(e)}")


@router.get("/status/{thread_id}")
async def get_status(thread_id: str):
    """
    Get the current status of a filing session.
    
    Retrieves the latest checkpoint without invoking the graph.
    """
    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }
    
    try:
        state = await tax_filing_graph.aget_state(config)
        
        if not state:
            raise HTTPException(status_code=404, detail="Thread not found")
        
        return {
            "thread_id": thread_id,
            "current_agent": state.values.get("current_agent"),
            "audit_status": state.values.get("audit_status"),
            "user_profile": state.values.get("user_profile"),
            "calculation_result": state.values.get("calculation_result")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve state: {str(e)}")
