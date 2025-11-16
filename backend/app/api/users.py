"""User management API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import crud, schemas
from app.database import get_db
from app.api.auth import get_current_active_user

router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.get("/me", response_model=schemas.User)
async def read_current_user(current_user = Depends(get_current_active_user)):
    """Get current user information."""
    return current_user


@router.put("/me", response_model=schemas.User)
async def update_current_user(
    user_update: schemas.UserUpdate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update current user information.
    
    - **full_name**: Update full name
    - **email**: Update email address (must be unique)
    """
    # If email is being changed, check if it's already taken
    if user_update.email and user_update.email != current_user.email:
        existing_user = crud.get_user_by_email(db, user_update.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
    
    updated_user = crud.update_user(db, current_user.id, user_update)
    
    # Log update
    crud.create_audit_log(
        db=db,
        user_id=current_user.id,
        action="update_user",
        resource_type="user",
        resource_id=current_user.id,
        details=user_update.dict(exclude_unset=True)
    )
    
    return updated_user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete current user account.
    
    WARNING: This will permanently delete all user data including tax forms.
    This action cannot be undone.
    """
    # Log deletion before deleting
    crud.create_audit_log(
        db=db,
        user_id=current_user.id,
        action="delete_user",
        resource_type="user",
        resource_id=current_user.id
    )
    
    crud.delete_user(db, current_user.id)
    return None


# ============================================================================
# User Profile Endpoints
# ============================================================================

@router.get("/me/profile", response_model=schemas.UserProfile)
async def read_current_user_profile(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's profile settings."""
    profile = crud.get_user_profile(db, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )
    return profile


@router.put("/me/profile", response_model=schemas.UserProfile)
async def update_current_user_profile(
    profile_update: schemas.UserProfileUpdate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update user profile settings.
    
    - **preferred_mode**: Filing mode (novice, intermediate, expert)
    - **theme**: UI theme (light, dark)
    - **language**: Preferred language (en, es, etc.)
    - **notifications_enabled**: Enable/disable notifications
    """
    updated_profile = crud.update_user_profile(db, current_user.id, profile_update)
    if not updated_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )
    
    # Log profile update
    crud.create_audit_log(
        db=db,
        user_id=current_user.id,
        action="update_profile",
        resource_type="user_profile",
        resource_id=updated_profile.id,
        details=profile_update.dict(exclude_unset=True)
    )
    
    return updated_profile


# ============================================================================
# Admin Endpoints (Optional - for future use)
# ============================================================================

@router.get("/", response_model=List[schemas.User])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all users (Admin only).
    
    TODO: Add admin role check before allowing access.
    """
    # For now, only allow user to see themselves
    return [current_user]


@router.get("/{user_id}", response_model=schemas.User)
async def read_user(
    user_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get user by ID (Admin only or own user).
    
    TODO: Add admin role check for viewing other users.
    """
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view other users"
        )
    
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return db_user
