"""
Authentication Routes - Task A
Implements /register and /login endpoints with JWT authentication
"""

from fastapi import APIRouter, HTTPException, status
from datetime import timedelta
from typing import Dict

from ..models import UserCreate, UserLogin, Token
from ..utils.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/auth", tags=["authentication"])

# In-memory user store (replace with database in production)
users_db: Dict[str, dict] = {}


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    """
    Register a new user
    
    Args:
        user: User registration data (email, username, password)
        
    Returns:
        Access token for the newly registered user
        
    Raises:
        HTTPException: If username or email already exists
    """
    # Check if username already exists
    if user.username in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    for existing_user in users_db.values():
        if existing_user["email"] == user.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Hash the password
    hashed_password = get_password_hash(user.password)
    
    # Store user (in production, use a proper database)
    user_id = f"user_{len(users_db) + 1}"
    users_db[user.username] = {
        "id": user_id,
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed_password
    }
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
async def login(user: UserLogin):
    """
    Authenticate user and return access token
    
    Args:
        user: User login credentials (username, password)
        
    Returns:
        Access token for authenticated user
        
    Raises:
        HTTPException: If credentials are invalid
    """
    # Check if user exists
    if user.username not in users_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    stored_user = users_db[user.username]
    
    # Verify password
    if not verify_password(user.password, stored_user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/test")
async def test_auth():
    """
    Test endpoint to verify authentication routes are working
    """
    return {
        "message": "Authentication routes are operational",
        "registered_users": len(users_db)
    }
