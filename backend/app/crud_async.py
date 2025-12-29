"""Async CRUD operations for database models.

This module provides async versions of CRUD operations using SQLAlchemy async sessions.
Import from this module for new async endpoints.

Usage:
    from app.crud_async import get_user_async
    
    async def get_user_endpoint(db: AsyncSession = Depends(get_async_db)):
        user = await get_user_async(db, user_id=1)
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from typing import Optional, List, Sequence
from datetime import datetime

from app import models, schemas
from app.core.security import get_password_hash, encrypt_data


# ============================================================================
# User CRUD Operations (Async)
# ============================================================================

async def get_user_async(db: AsyncSession, user_id: int) -> Optional[models.User]:
    """Get user by ID asynchronously."""
    result = await db.execute(
        select(models.User).where(models.User.id == user_id)
    )
    return result.scalar_one_or_none()


async def get_user_by_email_async(db: AsyncSession, email: str) -> Optional[models.User]:
    """Get user by email address asynchronously."""
    result = await db.execute(
        select(models.User).where(models.User.email == email)
    )
    return result.scalar_one_or_none()


async def get_users_async(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100
) -> Sequence[models.User]:
    """Get list of users with pagination asynchronously."""
    result = await db.execute(
        select(models.User).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def create_user_async(
    db: AsyncSession, 
    user: schemas.UserCreate
) -> models.User:
    """
    Create new user with hashed password and default profile asynchronously.
    
    Args:
        db: Async database session
        user: User creation schema with email and password
        
    Returns:
        Created user object
    """
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        is_active=True,
        is_verified=False
    )
    
    db.add(db_user)
    await db.flush()  # Get user ID without committing
    
    # Create default user profile
    db_profile = models.UserProfile(
        user_id=db_user.id,
        preferred_mode="novice",
        theme="light",
        language="en",
        notifications_enabled=True
    )
    db.add(db_profile)
    
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def update_user_async(
    db: AsyncSession, 
    user_id: int, 
    user_update: schemas.UserUpdate
) -> Optional[models.User]:
    """Update user information asynchronously."""
    db_user = await get_user_async(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def delete_user_async(db: AsyncSession, user_id: int) -> bool:
    """Delete user and all related data asynchronously."""
    db_user = await get_user_async(db, user_id)
    if not db_user:
        return False
    
    await db.delete(db_user)
    await db.commit()
    return True


# ============================================================================
# User Profile CRUD Operations (Async)
# ============================================================================

async def get_user_profile_async(
    db: AsyncSession, 
    user_id: int
) -> Optional[models.UserProfile]:
    """Get user profile by user ID asynchronously."""
    result = await db.execute(
        select(models.UserProfile).where(models.UserProfile.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def update_user_profile_async(
    db: AsyncSession, 
    user_id: int, 
    profile_update: schemas.UserProfileUpdate
) -> Optional[models.UserProfile]:
    """Update user profile settings asynchronously."""
    db_profile = await get_user_profile_async(db, user_id)
    if not db_profile:
        return None
    
    update_data = profile_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_profile, field, value)
    
    await db.commit()
    await db.refresh(db_profile)
    return db_profile


# ============================================================================
# Tax Form CRUD Operations (Async)
# ============================================================================

async def get_tax_form_async(
    db: AsyncSession, 
    form_id: int
) -> Optional[models.TaxForm]:
    """Get tax form by ID asynchronously."""
    result = await db.execute(
        select(models.TaxForm).where(models.TaxForm.id == form_id)
    )
    return result.scalar_one_or_none()


async def get_tax_form_with_relations_async(
    db: AsyncSession, 
    form_id: int
) -> Optional[models.TaxForm]:
    """Get tax form with all relations eagerly loaded."""
    result = await db.execute(
        select(models.TaxForm)
        .where(models.TaxForm.id == form_id)
        .options(
            selectinload(models.TaxForm.dependents),
            selectinload(models.TaxForm.w2_forms),
            selectinload(models.TaxForm.form_1099s),
            selectinload(models.TaxForm.compliance_checks),
        )
    )
    return result.scalar_one_or_none()


async def get_user_tax_forms_async(
    db: AsyncSession, 
    user_id: int, 
    year: Optional[int] = None
) -> Sequence[models.TaxForm]:
    """Get all tax forms for a user asynchronously."""
    query = select(models.TaxForm).where(models.TaxForm.owner_id == user_id)
    if year:
        query = query.where(models.TaxForm.year == year)
    query = query.order_by(models.TaxForm.year.desc())
    
    result = await db.execute(query)
    return result.scalars().all()


async def create_tax_form_async(
    db: AsyncSession, 
    user_id: int, 
    form: schemas.TaxFormCreate
) -> models.TaxForm:
    """Create a new tax form for a user asynchronously."""
    db_form = models.TaxForm(
        owner_id=user_id,
        year=form.year,
        filing_status=form.filing_status,
        status="in_progress",
        form_data={},
        total_income=0.0,
        adjusted_gross_income=0.0,
        taxable_income=0.0,
        total_tax=0.0,
        total_payments=0.0,
        refund_or_amount_owed=0.0
    )
    
    db.add(db_form)
    await db.commit()
    await db.refresh(db_form)
    return db_form


async def update_tax_form_async(
    db: AsyncSession, 
    form_id: int, 
    form_update: schemas.TaxFormUpdate
) -> Optional[models.TaxForm]:
    """Update tax form data asynchronously."""
    db_form = await get_tax_form_async(db, form_id)
    if not db_form:
        return None
    
    update_data = form_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_form, field, value)
    
    await db.commit()
    await db.refresh(db_form)
    return db_form


async def delete_tax_form_async(db: AsyncSession, form_id: int) -> bool:
    """Delete tax form asynchronously."""
    db_form = await get_tax_form_async(db, form_id)
    if not db_form:
        return False
    
    await db.delete(db_form)
    await db.commit()
    return True


# ============================================================================
# W-2 Form CRUD Operations (Async)
# ============================================================================

async def create_w2_form_async(
    db: AsyncSession, 
    form_id: int, 
    w2: schemas.W2FormCreate
) -> models.W2Form:
    """Create a W-2 form entry asynchronously."""
    db_w2 = models.W2Form(
        form_id=form_id,
        employer_name=w2.employer_name,
        employer_ein=w2.employer_ein,
        box_1_wages=w2.box_1_wages,
        box_2_federal_tax_withheld=w2.box_2_federal_tax_withheld,
        box_3_social_security_wages=w2.box_3_social_security_wages,
        box_4_social_security_tax_withheld=w2.box_4_social_security_tax_withheld,
        box_5_medicare_wages=w2.box_5_medicare_wages,
        box_6_medicare_tax_withheld=w2.box_6_medicare_tax_withheld,
        box_12_codes=w2.box_12_codes or [],
        box_13_checkboxes=w2.box_13_checkboxes or {}
    )
    
    db.add(db_w2)
    await db.commit()
    await db.refresh(db_w2)
    return db_w2


async def get_form_w2s_async(
    db: AsyncSession, 
    form_id: int
) -> Sequence[models.W2Form]:
    """Get all W-2 forms for a tax form asynchronously."""
    result = await db.execute(
        select(models.W2Form).where(models.W2Form.form_id == form_id)
    )
    return result.scalars().all()


# ============================================================================
# 1099 Form CRUD Operations (Async)
# ============================================================================

async def create_1099_form_async(
    db: AsyncSession, 
    form_id: int, 
    form_1099: schemas.Form1099Create
) -> models.Form1099:
    """Create a 1099 form entry asynchronously."""
    db_1099 = models.Form1099(
        form_id=form_id,
        form_type=form_1099.form_type,
        payer_name=form_1099.payer_name,
        payer_ein=form_1099.payer_ein,
        form_data=form_1099.form_data,
        total_amount=form_1099.total_amount
    )
    
    db.add(db_1099)
    await db.commit()
    await db.refresh(db_1099)
    return db_1099


async def get_form_1099s_async(
    db: AsyncSession, 
    form_id: int
) -> Sequence[models.Form1099]:
    """Get all 1099 forms for a tax form asynchronously."""
    result = await db.execute(
        select(models.Form1099).where(models.Form1099.form_id == form_id)
    )
    return result.scalars().all()


# ============================================================================
# Dependent CRUD Operations (Async)
# ============================================================================

async def create_dependent_async(
    db: AsyncSession, 
    form_id: int, 
    dependent: schemas.DependentCreate
) -> models.Dependent:
    """Create a dependent with encrypted SSN asynchronously."""
    db_dependent = models.Dependent(
        form_id=form_id,
        full_name=dependent.full_name,
        ssn_encrypted=encrypt_data(dependent.ssn),
        date_of_birth=dependent.date_of_birth,
        relationship_type=dependent.relationship,
        months_lived_with_taxpayer=dependent.months_lived_with_taxpayer,
        is_qualifying_child=False,
        is_qualifying_relative=False,
        claimed_by_another=False
    )
    
    db.add(db_dependent)
    await db.commit()
    await db.refresh(db_dependent)
    return db_dependent


async def get_form_dependents_async(
    db: AsyncSession, 
    form_id: int
) -> Sequence[models.Dependent]:
    """Get all dependents for a tax form asynchronously."""
    result = await db.execute(
        select(models.Dependent).where(models.Dependent.form_id == form_id)
    )
    return result.scalars().all()


# ============================================================================
# Audit Log CRUD Operations (Async)
# ============================================================================

async def create_audit_log_async(
    db: AsyncSession,
    user_id: int,
    action: str,
    resource_type: Optional[str] = None,
    resource_id: Optional[int] = None,
    details: Optional[dict] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> models.AuditLog:
    """Create an audit log entry asynchronously."""
    db_log = models.AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details or {},
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    db.add(db_log)
    await db.commit()
    await db.refresh(db_log)
    return db_log


# ============================================================================
# Authentication Helper (Async)
# ============================================================================

async def authenticate_user_async(
    db: AsyncSession, 
    email: str, 
    password: str
) -> Optional[models.User]:
    """Authenticate user with email and password asynchronously."""
    from app.core.security import verify_password
    
    user = await get_user_by_email_async(db, email)
    if not user:
        return None
    if not verify_password(password, str(user.hashed_password)):
        return None
    return user


# ============================================================================
# Tax Embedding CRUD Operations (pgvector)
# ============================================================================

async def create_tax_embedding_async(
    db: AsyncSession,
    content: str,
    embedding: List[float],
    metadata: Optional[dict] = None
) -> models.TaxEmbedding:
    """Create a new tax embedding record."""
    db_embedding = models.TaxEmbedding(
        content=content,
        embedding=embedding,
        metadata=metadata or {}
    )
    db.add(db_embedding)
    await db.commit()
    await db.refresh(db_embedding)
    return db_embedding


async def bulk_create_tax_embeddings_async(
    db: AsyncSession,
    embeddings_data: List[dict]
) -> int:
    """
    Bulk insert tax embeddings for efficient ingestion.
    
    Args:
        db: AsyncSession
        embeddings_data: List of dicts with 'content', 'embedding', 'metadata' keys
        
    Returns:
        Number of embeddings inserted
    """
    from sqlalchemy import text
    
    # Clear existing embeddings
    await db.execute(text("DELETE FROM tax_embeddings"))
    
    # Bulk insert using executemany pattern
    for data in embeddings_data:
        embedding_str = "[" + ",".join(str(x) for x in data["embedding"]) + "]"
        await db.execute(
            text("""
                INSERT INTO tax_embeddings (content, embedding, metadata)
                VALUES (:content, :embedding::vector, :metadata)
            """),
            {
                "content": data["content"],
                "embedding": embedding_str,
                "metadata": str(data.get("metadata", {})).replace("'", '"')
            }
        )
    
    await db.commit()
    return len(embeddings_data)


async def search_tax_embeddings_async(
    db: AsyncSession,
    query_embedding: List[float],
    limit: int = 3
) -> List[dict]:
    """
    Search tax embeddings using pgvector cosine similarity.
    
    Args:
        db: AsyncSession
        query_embedding: Query vector (384 dimensions for MiniLM)
        limit: Number of results to return
        
    Returns:
        List of dicts with 'content', 'similarity', 'metadata'
    """
    from sqlalchemy import text
    
    embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"
    
    result = await db.execute(
        text("""
            SELECT content, metadata, 1 - (embedding <=> :embedding::vector) as similarity
            FROM tax_embeddings
            ORDER BY embedding <=> :embedding::vector
            LIMIT :limit
        """),
        {"embedding": embedding_str, "limit": limit}
    )
    
    rows = result.fetchall()
    return [
        {"content": row[0], "metadata": row[1], "similarity": row[2]}
        for row in rows
    ]


async def get_tax_embedding_count_async(db: AsyncSession) -> int:
    """Get total count of tax embeddings."""
    from sqlalchemy import text
    result = await db.execute(text("SELECT COUNT(*) FROM tax_embeddings"))
    return result.scalar() or 0


async def delete_all_tax_embeddings_async(db: AsyncSession) -> int:
    """Delete all tax embeddings. Returns count of deleted records."""
    from sqlalchemy import text
    # Get count before deletion
    count_result = await db.execute(text("SELECT COUNT(*) FROM tax_embeddings"))
    count = count_result.scalar() or 0
    await db.execute(text("DELETE FROM tax_embeddings"))
    await db.commit()
    return count


# ============================================================================
# Document Embedding CRUD Operations (User Documents - pgvector)
# ============================================================================

async def create_document_embedding_async(
    db: AsyncSession,
    user_id: int,
    document_type: str,
    content: str,
    embedding: List[float],
    document_id: Optional[int] = None,
    metadata: Optional[dict] = None
) -> models.DocumentEmbedding:
    """Create a new document embedding for a user."""
    db_embedding = models.DocumentEmbedding(
        user_id=user_id,
        document_type=document_type,
        document_id=document_id,
        content=content,
        embedding=embedding,
        metadata=metadata or {}
    )
    db.add(db_embedding)
    await db.commit()
    await db.refresh(db_embedding)
    return db_embedding


async def search_user_documents_async(
    db: AsyncSession,
    user_id: int,
    query_embedding: List[float],
    document_type: Optional[str] = None,
    limit: int = 5
) -> List[dict]:
    """
    Search user's document embeddings using pgvector similarity.
    
    Args:
        db: AsyncSession
        user_id: User ID to search within
        query_embedding: Query vector
        document_type: Optional filter by document type
        limit: Number of results
        
    Returns:
        List of matching documents with similarity scores
    """
    from sqlalchemy import text
    
    embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"
    
    if document_type:
        result = await db.execute(
            text("""
                SELECT id, document_type, document_id, content, metadata,
                       1 - (embedding <=> :embedding::vector) as similarity
                FROM document_embeddings
                WHERE user_id = :user_id AND document_type = :doc_type
                ORDER BY embedding <=> :embedding::vector
                LIMIT :limit
            """),
            {
                "embedding": embedding_str,
                "user_id": user_id,
                "doc_type": document_type,
                "limit": limit
            }
        )
    else:
        result = await db.execute(
            text("""
                SELECT id, document_type, document_id, content, metadata,
                       1 - (embedding <=> :embedding::vector) as similarity
                FROM document_embeddings
                WHERE user_id = :user_id
                ORDER BY embedding <=> :embedding::vector
                LIMIT :limit
            """),
            {"embedding": embedding_str, "user_id": user_id, "limit": limit}
        )
    
    rows = result.fetchall()
    return [
        {
            "id": row[0],
            "document_type": row[1],
            "document_id": row[2],
            "content": row[3],
            "metadata": row[4],
            "similarity": row[5]
        }
        for row in rows
    ]


async def delete_user_document_embeddings_async(
    db: AsyncSession,
    user_id: int,
    document_type: Optional[str] = None
) -> int:
    """Delete document embeddings for a user, optionally filtered by type."""
    from sqlalchemy import text
    
    if document_type:
        # Get count before deletion
        count_result = await db.execute(
            text("SELECT COUNT(*) FROM document_embeddings WHERE user_id = :user_id AND document_type = :doc_type"),
            {"user_id": user_id, "doc_type": document_type}
        )
        count = count_result.scalar() or 0
        await db.execute(
            text("DELETE FROM document_embeddings WHERE user_id = :user_id AND document_type = :doc_type"),
            {"user_id": user_id, "doc_type": document_type}
        )
    else:
        count_result = await db.execute(
            text("SELECT COUNT(*) FROM document_embeddings WHERE user_id = :user_id"),
            {"user_id": user_id}
        )
        count = count_result.scalar() or 0
        await db.execute(
            text("DELETE FROM document_embeddings WHERE user_id = :user_id"),
            {"user_id": user_id}
        )
    
    await db.commit()
    return count
