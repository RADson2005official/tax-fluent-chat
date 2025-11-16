"""CRUD operations for all database models."""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, List
from datetime import datetime

from app import models, schemas
from app.security import get_password_hash, encrypt_data


# ============================================================================
# User CRUD Operations
# ============================================================================

def get_user(db: Session, user_id: int) -> Optional[models.User]:
    """Get user by ID."""
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Get user by email address."""
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    """Get list of users with pagination."""
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """
    Create new user with hashed password and default profile.
    
    Args:
        db: Database session
        user: User creation schema with email and password
        
    Returns:
        Created user object
        
    Raises:
        IntegrityError: If email already exists
    """
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        is_active=True,
        is_verified=False
    )
    
    try:
        db.add(db_user)
        db.flush()  # Get user ID without committing
        
        # Create default user profile
        db_profile = models.UserProfile(
            user_id=db_user.id,
            preferred_mode="novice",  # Default to novice mode
            theme="light",
            language="en",
            notifications_enabled=True
        )
        db.add(db_profile)
        
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise


def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate) -> Optional[models.User]:
    """Update user information."""
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    """Delete user and all related data (cascades)."""
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    
    db.delete(db_user)
    db.commit()
    return True


# ============================================================================
# User Profile CRUD Operations
# ============================================================================

def get_user_profile(db: Session, user_id: int) -> Optional[models.UserProfile]:
    """Get user profile by user ID."""
    return db.query(models.UserProfile).filter(models.UserProfile.user_id == user_id).first()


def update_user_profile(db: Session, user_id: int, profile_update: schemas.UserProfileUpdate) -> Optional[models.UserProfile]:
    """Update user profile settings."""
    db_profile = get_user_profile(db, user_id)
    if not db_profile:
        return None
    
    update_data = profile_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_profile, field, value)
    
    db.commit()
    db.refresh(db_profile)
    return db_profile


def update_user_interaction_stats(db: Session, user_id: int, help_requested: bool = False):
    """Update user interaction statistics for adaptive UI."""
    db_profile = get_user_profile(db, user_id)
    if not db_profile:
        return
    
    db_profile.interaction_count += 1
    if help_requested:
        db_profile.help_requests += 1
    
    # Calculate proficiency (simple logic for now)
    if db_profile.interaction_count > 10:
        help_rate = db_profile.help_requests / db_profile.interaction_count
        if help_rate < 0.1 and db_profile.preferred_mode == "novice":
            db_profile.preferred_mode = "intermediate"
        elif help_rate < 0.05 and db_profile.preferred_mode == "intermediate":
            db_profile.preferred_mode = "expert"
    
    db.commit()


# ============================================================================
# Tax Form CRUD Operations
# ============================================================================

def get_tax_form(db: Session, form_id: int) -> Optional[models.TaxForm]:
    """Get tax form by ID."""
    return db.query(models.TaxForm).filter(models.TaxForm.id == form_id).first()


def get_user_tax_forms(db: Session, user_id: int, year: Optional[int] = None) -> List[models.TaxForm]:
    """Get all tax forms for a user, optionally filtered by year."""
    query = db.query(models.TaxForm).filter(models.TaxForm.owner_id == user_id)
    if year:
        query = query.filter(models.TaxForm.year == year)
    return query.order_by(models.TaxForm.year.desc()).all()


def create_tax_form(db: Session, user_id: int, form: schemas.TaxFormCreate) -> models.TaxForm:
    """Create a new tax form for a user."""
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
    db.commit()
    db.refresh(db_form)
    return db_form


def update_tax_form(db: Session, form_id: int, form_update: schemas.TaxFormUpdate) -> Optional[models.TaxForm]:
    """Update tax form data."""
    db_form = get_tax_form(db, form_id)
    if not db_form:
        return None
    
    update_data = form_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_form, field, value)
    
    db.commit()
    db.refresh(db_form)
    return db_form


def delete_tax_form(db: Session, form_id: int) -> bool:
    """Delete tax form."""
    db_form = get_tax_form(db, form_id)
    if not db_form:
        return False
    
    db.delete(db_form)
    db.commit()
    return True


# ============================================================================
# Dependent CRUD Operations
# ============================================================================

def create_dependent(db: Session, form_id: int, dependent: schemas.DependentCreate) -> models.Dependent:
    """Create a dependent with encrypted SSN."""
    db_dependent = models.Dependent(
        form_id=form_id,
        full_name=dependent.full_name,
        ssn_encrypted=encrypt_data(dependent.ssn),  # Encrypt SSN
        date_of_birth=dependent.date_of_birth,
        relationship_type=dependent.relationship,
        months_lived_with_taxpayer=dependent.months_lived_with_taxpayer,
        is_qualifying_child=False,
        is_qualifying_relative=False,
        claimed_by_another=False
    )
    
    db.add(db_dependent)
    db.commit()
    db.refresh(db_dependent)
    return db_dependent


def get_form_dependents(db: Session, form_id: int) -> List[models.Dependent]:
    """Get all dependents for a tax form."""
    return db.query(models.Dependent).filter(models.Dependent.form_id == form_id).all()


# ============================================================================
# W-2 Form CRUD Operations
# ============================================================================

def create_w2_form(db: Session, form_id: int, w2: schemas.W2FormCreate) -> models.W2Form:
    """Create a W-2 form entry."""
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
    db.commit()
    db.refresh(db_w2)
    return db_w2


def get_form_w2s(db: Session, form_id: int) -> List[models.W2Form]:
    """Get all W-2 forms for a tax form."""
    return db.query(models.W2Form).filter(models.W2Form.form_id == form_id).all()


# ============================================================================
# 1099 Form CRUD Operations
# ============================================================================

def create_1099_form(db: Session, form_id: int, form_1099: schemas.Form1099Create) -> models.Form1099:
    """Create a 1099 form entry."""
    db_1099 = models.Form1099(
        form_id=form_id,
        form_type=form_1099.form_type,
        payer_name=form_1099.payer_name,
        payer_ein=form_1099.payer_ein,
        form_data=form_1099.form_data,
        total_amount=form_1099.total_amount
    )
    
    db.add(db_1099)
    db.commit()
    db.refresh(db_1099)
    return db_1099


def get_form_1099s(db: Session, form_id: int) -> List[models.Form1099]:
    """Get all 1099 forms for a tax form."""
    return db.query(models.Form1099).filter(models.Form1099.form_id == form_id).all()


# ============================================================================
# User Input Data CRUD Operations
# ============================================================================

def log_user_input(db: Session, form_id: int, input_data: schemas.UserInputDataCreate) -> models.UserInputData:
    """Log user input for audit trail."""
    db_input = models.UserInputData(
        form_id=form_id,
        field_key=input_data.field_key,
        field_value=input_data.field_value,
        field_type=input_data.field_type,
        source=input_data.source,
        confidence_score=input_data.confidence_score
    )
    
    db.add(db_input)
    db.commit()
    db.refresh(db_input)
    return db_input


def get_form_input_history(db: Session, form_id: int) -> List[models.UserInputData]:
    """Get input history for a tax form."""
    return db.query(models.UserInputData).filter(
        models.UserInputData.form_id == form_id
    ).order_by(models.UserInputData.timestamp.desc()).all()


# ============================================================================
# Compliance Check CRUD Operations
# ============================================================================

def create_compliance_check(db: Session, form_id: int, check: schemas.ComplianceCheckCreate) -> models.ComplianceCheck:
    """Create a compliance check result."""
    db_check = models.ComplianceCheck(
        form_id=form_id,
        check_type=check.check_type,
        check_name=check.check_name,
        status=check.status,
        message=check.message,
        details=check.details or {}
    )
    
    db.add(db_check)
    db.commit()
    db.refresh(db_check)
    return db_check


def get_form_compliance_checks(db: Session, form_id: int) -> List[models.ComplianceCheck]:
    """Get all compliance checks for a tax form."""
    return db.query(models.ComplianceCheck).filter(
        models.ComplianceCheck.form_id == form_id
    ).all()


# ============================================================================
# Audit Log CRUD Operations
# ============================================================================

def create_audit_log(db: Session, user_id: int, action: str, resource_type: str = None, 
                    resource_id: int = None, details: dict = None, 
                    ip_address: str = None, user_agent: str = None) -> models.AuditLog:
    """Create an audit log entry."""
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
    db.commit()
    db.refresh(db_log)
    return db_log


def get_user_audit_logs(db: Session, user_id: int, limit: int = 100) -> List[models.AuditLog]:
    """Get audit logs for a user."""
    return db.query(models.AuditLog).filter(
        models.AuditLog.user_id == user_id
    ).order_by(models.AuditLog.timestamp.desc()).limit(limit).all()


# ============================================================================
# Authentication Helper
# ============================================================================

def authenticate_user(db: Session, email: str, password: str) -> Optional[models.User]:
    """Authenticate user with email and password."""
    from app.security import verify_password
    
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
