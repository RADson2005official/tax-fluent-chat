"""
Tax calculation routes
"""

from fastapi import APIRouter, HTTPException

from ..models import TaxInput, TaxResult
from ..services.tax_calculator import calculate_tax, TaxCalculationError

router = APIRouter(prefix="/tax", tags=["tax"])


@router.post("/calculate", response_model=TaxResult)
async def calculate_taxes(tax_input: TaxInput):
    """
    Calculate federal taxes based on input parameters
    
    Args:
        tax_input: Tax calculation inputs
        
    Returns:
        Tax calculation results with detailed breakdown
        
    Raises:
        HTTPException: If calculation fails due to invalid inputs
    """
    try:
        result = calculate_tax(
            income=tax_input.income,
            filing_status=tax_input.filing_status,
            dependents=tax_input.dependents,
            additional_deductions=tax_input.deductions
        )
        return result
    except TaxCalculationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/brackets/{filing_status}")
async def get_tax_brackets(filing_status: str):
    """
    Get tax bracket information for a specific filing status
    
    Args:
        filing_status: Filing status (single, married_joint, etc.)
        
    Returns:
        Tax bracket information
    """
    from ..services.tax_calculator import get_tax_brackets, get_standard_deduction
    
    try:
        brackets = get_tax_brackets(filing_status)
        standard_deduction = get_standard_deduction(filing_status)
        
        bracket_info = []
        previous = 0
        for threshold, rate in brackets:
            if threshold == float('inf'):
                bracket_info.append({
                    "range": f"${previous:,.0f}+",
                    "rate": f"{rate*100:.0f}%"
                })
            else:
                bracket_info.append({
                    "range": f"${previous:,.0f} - ${threshold:,.0f}",
                    "rate": f"{rate*100:.0f}%"
                })
                previous = threshold
        
        return {
            "filing_status": filing_status,
            "standard_deduction": standard_deduction,
            "brackets": bracket_info
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
