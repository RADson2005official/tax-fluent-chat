"""Tax forms API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app import crud, schemas
from app.database import get_db
from app.api.auth import get_current_active_user

router = APIRouter(
    prefix="/tax-forms",
    tags=["tax-forms"]
)


@router.post("/", response_model=schemas.TaxForm, status_code=status.HTTP_201_CREATED)
async def create_tax_form(
    form: schemas.TaxFormCreate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new tax form for the current tax year.
    
    - **year**: Tax year (e.g., 2024)
    - **filing_status**: single, married_filing_jointly, married_filing_separately, head_of_household, qualifying_widow
    
    Initializes a new tax form with in_progress status.
    """
    # Check if user already has a form for this year
    existing_forms = crud.get_user_tax_forms(db, current_user.id, form.year)
    if existing_forms:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tax form for year {form.year} already exists"
        )
    
    new_form = crud.create_tax_form(db, current_user.id, form)
    
    # Log creation
    crud.create_audit_log(
        db=db,
        user_id=current_user.id,
        action="create_tax_form",
        resource_type="tax_form",
        resource_id=new_form.id,
        details={"year": form.year, "filing_status": form.filing_status}
    )
    
    return new_form


@router.get("/", response_model=List[schemas.TaxForm])
async def list_tax_forms(
    year: Optional[int] = None,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all tax forms for current user.
    
    - **year** (optional): Filter by specific tax year
    
    Returns list of tax forms ordered by year (newest first).
    """
    return crud.get_user_tax_forms(db, current_user.id, year)


@router.get("/{form_id}", response_model=schemas.TaxForm)
async def get_tax_form(
    form_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get specific tax form by ID."""
    form = crud.get_tax_form(db, form_id)
    
    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tax form not found"
        )
    
    # Ensure user owns this form
    if form.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this tax form"
        )
    
    return form


@router.put("/{form_id}", response_model=schemas.TaxForm)
async def update_tax_form(
    form_id: int,
    form_update: schemas.TaxFormUpdate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update tax form data.
    
    Can update any field including form_data, calculations, and status.
    """
    # Get and verify ownership
    form = crud.get_tax_form(db, form_id)
    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tax form not found"
        )
    
    if form.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this tax form"
        )
    
    updated_form = crud.update_tax_form(db, form_id, form_update)
    
    # Log update
    crud.create_audit_log(
        db=db,
        user_id=current_user.id,
        action="update_tax_form",
        resource_type="tax_form",
        resource_id=form_id,
        details=form_update.dict(exclude_unset=True)
    )
    
    return updated_form


@router.delete("/{form_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tax_form(
    form_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete tax form.
    
    WARNING: This will permanently delete the form and all related data 
    (dependents, W-2s, 1099s, etc.). This action cannot be undone.
    """
    # Get and verify ownership
    form = crud.get_tax_form(db, form_id)
    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tax form not found"
        )
    
    if form.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this tax form"
        )
    
    # Log deletion before deleting
    crud.create_audit_log(
        db=db,
        user_id=current_user.id,
        action="delete_tax_form",
        resource_type="tax_form",
        resource_id=form_id
    )
    
    crud.delete_tax_form(db, form_id)
    return None


# ============================================================================
# Dependents Endpoints
# ============================================================================

@router.post("/{form_id}/dependents", response_model=schemas.Dependent, status_code=status.HTTP_201_CREATED)
async def create_dependent(
    form_id: int,
    dependent: schemas.DependentCreate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Add a dependent to a tax form.
    
    SSN is automatically encrypted before storage.
    """
    # Verify form ownership
    form = crud.get_tax_form(db, form_id)
    if not form or form.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this tax form"
        )
    
    new_dependent = crud.create_dependent(db, form_id, dependent)
    
    # Log creation
    crud.create_audit_log(
        db=db,
        user_id=current_user.id,
        action="create_dependent",
        resource_type="dependent",
        resource_id=new_dependent.id,
        details={"form_id": form_id, "name": dependent.full_name}
    )
    
    return new_dependent


@router.get("/{form_id}/dependents", response_model=List[schemas.Dependent])
async def list_dependents(
    form_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all dependents for a tax form."""
    # Verify form ownership
    form = crud.get_tax_form(db, form_id)
    if not form or form.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this tax form"
        )
    
    return crud.get_form_dependents(db, form_id)


# ============================================================================
# W-2 Forms Endpoints
# ============================================================================

@router.post("/{form_id}/w2s", response_model=schemas.W2Form, status_code=status.HTTP_201_CREATED)
async def create_w2_form(
    form_id: int,
    w2: schemas.W2FormCreate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Add a W-2 form to a tax form.
    
    All box values from W-2 form should be entered here.
    """
    # Verify form ownership
    form = crud.get_tax_form(db, form_id)
    if not form or form.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this tax form"
        )
    
    new_w2 = crud.create_w2_form(db, form_id, w2)
    
    # Log creation
    crud.create_audit_log(
        db=db,
        user_id=current_user.id,
        action="create_w2",
        resource_type="w2_form",
        resource_id=new_w2.id,
        details={"form_id": form_id, "employer": w2.employer_name}
    )
    
    return new_w2


@router.get("/{form_id}/w2s", response_model=List[schemas.W2Form])
async def list_w2_forms(
    form_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all W-2 forms for a tax form."""
    # Verify form ownership
    form = crud.get_tax_form(db, form_id)
    if not form or form.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this tax form"
        )
    
    return crud.get_form_w2s(db, form_id)


# ============================================================================
# 1099 Forms Endpoints
# ============================================================================

@router.post("/{form_id}/1099s", response_model=schemas.Form1099, status_code=status.HTTP_201_CREATED)
async def create_1099_form(
    form_id: int,
    form_1099: schemas.Form1099Create,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Add a 1099 form to a tax form.
    
    Supports all 1099 types: INT, DIV, MISC, NEC, etc.
    """
    # Verify form ownership
    form = crud.get_tax_form(db, form_id)
    if not form or form.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this tax form"
        )
    
    new_1099 = crud.create_1099_form(db, form_id, form_1099)
    
    # Log creation
    crud.create_audit_log(
        db=db,
        user_id=current_user.id,
        action="create_1099",
        resource_type="form_1099",
        resource_id=new_1099.id,
        details={"form_id": form_id, "type": form_1099.form_type, "payer": form_1099.payer_name}
    )
    
    return new_1099


@router.get("/{form_id}/1099s", response_model=List[schemas.Form1099])
async def list_1099_forms(
    form_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all 1099 forms for a tax form."""
    # Verify form ownership
    form = crud.get_tax_form(db, form_id)
    if not form or form.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this tax form"
        )
    
    return crud.get_form_1099s(db, form_id)


# ============================================================================
# Compliance Checks Endpoints
# ============================================================================

@router.get("/{form_id}/compliance-checks", response_model=List[schemas.ComplianceCheck])
async def list_compliance_checks(
    form_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all compliance checks for a tax form.
    
    Returns validation results, warnings, and suggestions.
    """
    # Verify form ownership
    form = crud.get_tax_form(db, form_id)
    if not form or form.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this tax form"
        )
    
    return crud.get_form_compliance_checks(db, form_id)
