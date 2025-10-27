from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, validator
from enum import Enum

class FilingStatus(str, Enum):
    SINGLE = "single"
    MARRIED_JOINT = "married_joint"
    MARRIED_SEPARATE = "married_separate"
    HEAD_OF_HOUSEHOLD = "head_of_household"

class TaxInput(BaseModel):
    """Input model for tax calculation"""
    income: float = Field(..., gt=0, description="Annual income")
    filing_status: FilingStatus
    dependents: int = Field(0, ge=0, description="Number of dependents")
    deductions: float = Field(0, ge=0, description="Additional deductions")
    
    @validator('income')
    def validate_income(cls, v):
        if v <= 0:
            raise ValueError("Income must be positive")
        if v > 10000000:
            raise ValueError("Income exceeds reasonable limit")
        return v

class TaxResult(BaseModel):
    """Result model for tax calculation"""
    gross_income: float
    taxable_income: float
    tax_liability: float
    effective_rate: float
    marginal_rate: float
    standard_deduction: float
    breakdown: List[Dict[str, Any]]

class TaxCalculator:
    """
    Tax calculator with progressive slab logic and error handling
    Based on 2024 tax year brackets
    """
    
    # 2024 Standard deductions
    STANDARD_DEDUCTIONS = {
        FilingStatus.SINGLE: 14600,
        FilingStatus.MARRIED_JOINT: 29200,
        FilingStatus.MARRIED_SEPARATE: 14600,
        FilingStatus.HEAD_OF_HOUSEHOLD: 21900,
    }
    
    # 2024 Tax brackets (rate, upper limit)
    TAX_BRACKETS = {
        FilingStatus.SINGLE: [
            (0.10, 11600),
            (0.12, 47150),
            (0.22, 100525),
            (0.24, 191950),
            (0.32, 243725),
            (0.35, 609350),
            (0.37, float('inf')),
        ],
        FilingStatus.MARRIED_JOINT: [
            (0.10, 23200),
            (0.12, 94300),
            (0.22, 201050),
            (0.24, 383900),
            (0.32, 487450),
            (0.35, 731200),
            (0.37, float('inf')),
        ],
        FilingStatus.MARRIED_SEPARATE: [
            (0.10, 11600),
            (0.12, 47150),
            (0.22, 100525),
            (0.24, 191950),
            (0.32, 243725),
            (0.35, 365600),
            (0.37, float('inf')),
        ],
        FilingStatus.HEAD_OF_HOUSEHOLD: [
            (0.10, 16550),
            (0.12, 63100),
            (0.22, 100500),
            (0.24, 191950),
            (0.32, 243700),
            (0.35, 609350),
            (0.37, float('inf')),
        ],
    }
    
    def calculate_tax(self, tax_input: TaxInput) -> TaxResult:
        """
        Calculate tax with progressive slab logic
        
        Args:
            tax_input: TaxInput model with income and filing details
            
        Returns:
            TaxResult with detailed tax calculation
            
        Raises:
            ValueError: If input validation fails
        """
        try:
            # Get standard deduction
            standard_deduction = self.STANDARD_DEDUCTIONS[tax_input.filing_status]
            
            # Calculate taxable income
            total_deductions = standard_deduction + tax_input.deductions
            taxable_income = max(0, tax_input.income - total_deductions)
            
            # Calculate tax using progressive slabs
            tax_liability, breakdown = self._calculate_progressive_tax(
                taxable_income, 
                tax_input.filing_status
            )
            
            # Calculate rates
            effective_rate = (tax_liability / tax_input.income * 100) if tax_input.income > 0 else 0
            marginal_rate = self._get_marginal_rate(taxable_income, tax_input.filing_status)
            
            return TaxResult(
                gross_income=tax_input.income,
                taxable_income=taxable_income,
                tax_liability=round(tax_liability, 2),
                effective_rate=round(effective_rate, 2),
                marginal_rate=round(marginal_rate * 100, 2),
                standard_deduction=standard_deduction,
                breakdown=breakdown
            )
            
        except KeyError as e:
            raise ValueError(f"Invalid filing status: {e}")
        except Exception as e:
            raise ValueError(f"Tax calculation error: {str(e)}")
    
    def _calculate_progressive_tax(
        self, 
        taxable_income: float, 
        filing_status: FilingStatus
    ) -> tuple[float, List[Dict[str, Any]]]:
        """
        Calculate tax using progressive bracket system
        
        Returns:
            Tuple of (total_tax, breakdown)
        """
        brackets = self.TAX_BRACKETS[filing_status]
        total_tax = 0
        breakdown = []
        previous_limit = 0
        
        for rate, upper_limit in brackets:
            if taxable_income <= previous_limit:
                break
                
            # Calculate taxable amount in this bracket
            bracket_income = min(taxable_income, upper_limit) - previous_limit
            
            if bracket_income > 0:
                bracket_tax = bracket_income * rate
                total_tax += bracket_tax
                
                breakdown.append({
                    "rate": rate * 100,
                    "income_in_bracket": round(bracket_income, 2),
                    "tax_in_bracket": round(bracket_tax, 2),
                    "bracket_range": f"${previous_limit:,.0f} - ${upper_limit:,.0f}" if upper_limit != float('inf') else f"${previous_limit:,.0f}+"
                })
            
            previous_limit = upper_limit
            
            if taxable_income <= upper_limit:
                break
        
        return total_tax, breakdown
    
    def _get_marginal_rate(
        self, 
        taxable_income: float, 
        filing_status: FilingStatus
    ) -> float:
        """Get the marginal tax rate for the given income"""
        brackets = self.TAX_BRACKETS[filing_status]
        
        for rate, upper_limit in brackets:
            if taxable_income <= upper_limit:
                return rate
        
        return brackets[-1][0]  # Return highest rate if income exceeds all brackets

# Create calculator instance
tax_calculator = TaxCalculator()
