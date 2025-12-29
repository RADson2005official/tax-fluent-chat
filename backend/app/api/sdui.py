"""
Server-Driven UI (SDUI) API

Endpoints to fetch dynamically generated UI schemas.
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from app.sdui.schema import Screen
from app.sdui.generator import generate_dashboard_schema

from sqlalchemy.orm import Session
from app.core.database import get_db
from app import crud

router = APIRouter(prefix="/api/sdui", tags=["Server-Driven UI"])

@router.get("/dashboard/{user_id}", response_model=Screen)
async def get_dashboard_schema(user_id: str, db: Session = Depends(get_db)):
    """
    Get the dashboard UI schema for a specific user.
    The layout adapts based on the user's profile (e.g., age, preferred mode).
    """
    try:
        # Try to parse user_id as int, if it fails, it might be a string ID (like 'user123')
        # For now, we'll assume numeric IDs for real DB users, but handle string IDs for backward compatibility/testing
        if user_id.isdigit():
            db_user = crud.get_user(db, int(user_id))
        else:
            # Fallback for testing with string IDs if needed, or just return 404
            # For Phase 3, let's try to find by email if it looks like an email, otherwise 404
            if "@" in user_id:
                db_user = crud.get_user_by_email(db, user_id)
            else:
                db_user = None
    except Exception:
        db_user = None
    
    if not db_user:
        # If user not found in DB, return a default guest profile for resilience
        # In production, this might be a 404, but for smooth UI dev we'll return default
        user_profile = {"name": "Guest", "age": 30, "mode": "standard"}
    else:
        # Construct profile from DB data
        user_profile = {
            "name": db_user.full_name or "User",
            "age": 30,  # Default age as it's not in User model yet
            "mode": db_user.profile.preferred_mode if db_user.profile else "standard"
        }
    
    return generate_dashboard_schema(user_profile)
