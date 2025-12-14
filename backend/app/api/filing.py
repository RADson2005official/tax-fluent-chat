from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response, JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.api import auth
from app import crud
from app.models import User, TaxForm, W2Form, Form1099, Dependent
from app.services.pdf_generator import generate_tax_return_pdf
from datetime import datetime
import json

router = APIRouter(
    prefix="/filing",
    tags=["filing"]
)

@router.post("/export/{form_id}")
async def export_itr_json(
    form_id: int,
    current_user: User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Export tax return in official ITR-1 JSON format.
    """
    # Verify ownership
    form = crud.get_tax_form(db, form_id)
    if not form or form.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tax form not found or access denied"
        )

    # Fetch related data
    dependents = crud.get_form_dependents(db, form_id)
    w2s = crud.get_form_w2s(db, form_id)
    form1099s = crud.get_form_1099s(db, form_id)

    # Construct ITR-1 JSON Structure
    # This is a simplified mapping to the official schema
    itr_data = {
        "ITR": {
            "ITR-1": {
                "CreationInfo": {
                    "SWVersionNo": "1.0",
                    "SWCreatedBy": "TaxFluent_Agent",
                    "XMLCreatedBy": "TaxFluent_Agent",
                    "XMLCreationDate": datetime.now().strftime("%Y-%m-%d"),
                    "IntermediaryCity": "Bangalore",
                    "Digest": "SHA256_HASH_PLACEHOLDER"
                },
                "Form_ITR1": {
                    "PersonalInfo": {
                        "AssesseeName": {
                            "FirstName": current_user.full_name.split()[0] if current_user.full_name else "",
                            "SurNameOrOrgName": current_user.full_name.split()[-1] if current_user.full_name else ""
                        },
                        "PAN": "ABCDE1234F",  # Placeholder or from profile
                        "Address": {
                            "ResidenceNo": "123",
                            "ResidenceName": "TaxFluent Apt",
                            "RoadOrStreet": "Tech Park Road",
                            "LocalityOrArea": "Electronic City",
                            "CityOrTownOrDistrict": "Bangalore",
                            "StateCode": "29",
                            "PinCode": "560100",
                            "CountryCode": "91"
                        },
                        "DOB": "1990-01-01", # Placeholder
                        "EmployerCategory": "OTH",
                        "EmailAddress": current_user.email,
                        "MobileNo": "9876543210"
                    },
                    "FilingStatus": {
                        "ReturnFileSec": "11", # On or before due date
                        "TaxStatus": "TR", # Tax Refund
                        "ResidentialStatus": "RES" # Resident
                    },
                    "IncomeDeductions": {
                        "GrossSalary": sum(w.box_1_wages for w in w2s),
                        "IncomeFromOtherSources": sum(f.total_amount for f in form1099s),
                        "GrossTotalIncome": form.total_income,
                        "Deductions": {
                            "Section80C": 150000, # Mock logic
                            "Section80D": 25000,
                            "TotalDeductions": 175000
                        },
                        "TotalIncome": form.taxable_income
                    },
                    "TaxComputation": {
                        "TotalTaxPayable": form.total_tax,
                        "Rebate87A": 0,
                        "TaxPayableOnRebate": form.total_tax,
                        "EducationCess": round(form.total_tax * 0.04),
                        "GrossTaxLiability": round(form.total_tax * 1.04)
                    },
                    "TaxesPaid": {
                        "TDS": sum(w.box_2_federal_tax_withheld for w in w2s),
                        "AdvanceTax": 0,
                        "SelfAssessmentTax": 0,
                        "TotalTaxesPaid": form.total_payments
                    },
                    "Refund": {
                        "RefundDue": form.refund_or_amount_owed if form.refund_or_amount_owed > 0 else 0,
                        "AmountPayable": abs(form.refund_or_amount_owed) if form.refund_or_amount_owed < 0 else 0
                    },
                    "Verification": {
                        "Declaration": {
                            "AssesseeVerName": current_user.full_name,
                            "FatherName": "Father Name",
                            "Capacity": "S" # Self
                        },
                        "Date": datetime.now().strftime("%Y-%m-%d"),
                        "Place": "Bangalore"
                    }
                }
            }
        }
    }

    filename = f"ITR-1_{form.year}_{current_user.id}.json"
    
    return JSONResponse(
        content=itr_data,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.post("/submit/{form_id}")
async def submit_filing(
    form_id: int,
    current_user: User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Simulate e-filing submission and generate PDF.
    """
    # Verify ownership
    form = crud.get_tax_form(db, form_id)
    if not form or form.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tax form not found or access denied"
        )

    # Fetch data
    w2s = crud.get_form_w2s(db, form_id)
    form1099s = crud.get_form_1099s(db, form_id)

    user_data = {
        "first_name": current_user.full_name.split()[0] if current_user.full_name else "",
        "last_name": current_user.full_name.split()[-1] if current_user.full_name else "",
        "email": current_user.email
    }
    
    tax_data = {
        "filing_status": form.filing_status,
        "w2s": [{"employer": w.employer_name, "wages": w.box_1_wages} for w in w2s],
        "form1099s": [{"payer": f.payer_name, "amount": f.total_amount} for f in form1099s],
        "total_income": form.total_income,
        "taxable_income": form.taxable_income,
        "total_tax": form.total_tax,
        "refund": form.refund_or_amount_owed
    }

    # Generate PDF
    # Note: generate_tax_return_pdf might need updates to match this data structure
    # For now, we pass what we have
    try:
        pdf_content = generate_tax_return_pdf(user_data, tax_data)
    except Exception as e:
        # Fallback if PDF generation fails (e.g. missing template)
        print(f"PDF Generation failed: {e}")
        pdf_content = b"PDF Generation Failed. Please contact support."

    # Update status
    crud.update_tax_form(db, form_id, schemas.TaxFormUpdate(status="filed"))

    filename = f"TaxReturn_{form.year}_{current_user.id}.pdf"
    
    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
