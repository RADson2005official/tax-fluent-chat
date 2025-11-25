from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.api import auth
from app.models import User, TaxForm, W2Form, Form1099
from app.services.pdf_generator import generate_tax_return_pdf
from datetime import datetime

router = APIRouter(
    prefix="/filing",
    tags=["filing"]
)

@router.post("/submit")
async def submit_filing(
    current_user: User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    # 1. Aggregate Data
    # In a real app, we might have a specific "TaxReturn" object. 
    # Here we'll aggregate from what we have.
    
    # Get latest filing or create a dummy one if none exists for this year
    # For simplicity, we'll just gather all W2s and 1099s for the user
    
    w2s = db.query(W2Form).filter(W2Form.user_id == current_user.id).all()
    form1099s = db.query(Form1099).filter(Form1099.user_id == current_user.id).all()
    
    if not w2s and not form1099s:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No income forms found. Cannot file taxes without income data."
        )

    user_data = {
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "email": current_user.email
    }
    
    tax_data = {
        "filing_status": "Single", # Defaulting for now as we don't have this in User model explicitly yet
        "w2s": [{"employer": w.employer, "wages": w.wages} for w in w2s],
        "form1099s": [{"payer": f.payer, "amount": f.amount} for f in form1099s]
    }

    # 2. Generate PDF
    pdf_content = generate_tax_return_pdf(user_data, tax_data)
    
    # 3. Simulate Submission (Mock)
    # In a real app, we'd send this to the IRS API
    
    # 4. Return PDF
    filename = f"TaxReturn_{datetime.now().year}_{current_user.last_name}.pdf"
    
    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
