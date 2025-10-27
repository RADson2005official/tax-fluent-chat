"""
Explanation routes
"""

from fastapi import APIRouter

from ..models import ExplanationRequest, ExplanationResponse
from ..services.explanation_engine import explain

router = APIRouter(prefix="/explain", tags=["explanations"])


@router.post("/", response_model=ExplanationResponse)
async def get_explanation(request: ExplanationRequest):
    """
    Get adaptive explanation based on user proficiency level
    
    Args:
        request: Explanation request with query, proficiency, and context
        
    Returns:
        Adaptive explanation with related topics and terms
    """
    result = explain(
        query=request.query,
        proficiency=request.proficiency,
        context=request.context if request.context else None
    )
    
    return result


@router.get("/topics")
async def list_topics():
    """
    List available explanation topics
    
    Returns:
        List of available topics
    """
    from ..services.explanation_engine import ExplanationEngine
    
    topics = list(ExplanationEngine.TOPICS.keys()) + list(ExplanationEngine.TAX_TERMS.keys())
    
    return {
        "topics": topics,
        "count": len(topics)
    }
