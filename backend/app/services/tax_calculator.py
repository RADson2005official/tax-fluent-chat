"""
Tax Calculator Service - Task B
Implements progressive slab logic with error handling for 2024 tax year
"""

from typing import Dict, Tuple


# 2024 Federal Tax Brackets (Single filers)
TAX_BRACKETS_SINGLE = [
    (11600, 0.10),      # 10% on income up to $11,600
    (47150, 0.12),      # 12% on income $11,601 to $47,150
    (100525, 0.22),     # 22% on income $47,151 to $100,525
    (191950, 0.24),     # 24% on income $100,526 to $191,950
    (243725, 0.32),     # 32% on income $191,951 to $243,725
    (609350, 0.35),     # 35% on income $243,726 to $609,350
    (float('inf'), 0.37) # 37% on income over $609,350
]

# 2024 Federal Tax Brackets (Married filing jointly)
TAX_BRACKETS_MARRIED_JOINT = [
    (23200, 0.10),
    (94300, 0.12),
    (201050, 0.22),
    (383900, 0.24),
    (487450, 0.32),
    (731200, 0.35),
    (float('inf'), 0.37)
]

# 2024 Federal Tax Brackets (Married filing separately)
TAX_BRACKETS_MARRIED_SEPARATE = [
    (11600, 0.10),
    (47150, 0.12),
    (100525, 0.22),
    (191950, 0.24),
    (243725, 0.32),
    (365600, 0.35),
    (float('inf'), 0.37)
]

# 2024 Federal Tax Brackets (Head of household)
TAX_BRACKETS_HEAD_OF_HOUSEHOLD = [
    (16550, 0.10),
    (63100, 0.12),
    (100500, 0.22),
    (191950, 0.24),
    (243700, 0.32),
    (609350, 0.35),
    (float('inf'), 0.37)
]

# 2024 Standard Deductions
STANDARD_DEDUCTIONS = {
    "single": 14600,
    "married_joint": 29200,
    "married_separate": 14600,
    "head_of_household": 21900
}


class TaxCalculationError(Exception):
    """Custom exception for tax calculation errors"""
    pass


def get_tax_brackets(filing_status: str) -> list[Tuple[float, float]]:
    """
    Get the appropriate tax brackets based on filing status
    
    Args:
        filing_status: One of 'single', 'married_joint', 'married_separate', 'head_of_household'
        
    Returns:
        List of (threshold, rate) tuples
        
    Raises:
        TaxCalculationError: If filing status is invalid
    """
    brackets = {
        "single": TAX_BRACKETS_SINGLE,
        "married_joint": TAX_BRACKETS_MARRIED_JOINT,
        "married_separate": TAX_BRACKETS_MARRIED_SEPARATE,
        "head_of_household": TAX_BRACKETS_HEAD_OF_HOUSEHOLD
    }
    
    if filing_status not in brackets:
        raise TaxCalculationError(
            f"Invalid filing status: {filing_status}. "
            f"Must be one of: {', '.join(brackets.keys())}"
        )
    
    return brackets[filing_status]


def calculate_progressive_tax(taxable_income: float, filing_status: str) -> Tuple[float, float, str]:
    """
    Calculate federal tax using progressive slab logic
    
    Args:
        taxable_income: Income after deductions
        filing_status: Filing status for bracket selection
        
    Returns:
        Tuple of (total_tax, marginal_rate, tax_bracket_description)
        
    Raises:
        TaxCalculationError: If inputs are invalid
    """
    if taxable_income < 0:
        raise TaxCalculationError("Taxable income cannot be negative")
    
    if taxable_income == 0:
        return 0.0, 0.0, "No tax (zero income)"
    
    brackets = get_tax_brackets(filing_status)
    
    total_tax = 0.0
    previous_threshold = 0.0
    marginal_rate = 0.0
    bracket_desc = ""
    
    for threshold, rate in brackets:
        if taxable_income <= threshold:
            # Tax on the remaining income in this bracket
            taxable_in_bracket = taxable_income - previous_threshold
            total_tax += taxable_in_bracket * rate
            marginal_rate = rate
            
            if threshold == float('inf'):
                bracket_desc = f"${previous_threshold:,.0f}+ (Top bracket)"
            else:
                bracket_desc = f"${previous_threshold:,.0f} - ${threshold:,.0f}"
            break
        else:
            # Tax on the full bracket
            taxable_in_bracket = threshold - previous_threshold
            total_tax += taxable_in_bracket * rate
            previous_threshold = threshold
    
    return total_tax, marginal_rate, bracket_desc


def get_standard_deduction(filing_status: str) -> float:
    """
    Get the standard deduction for the given filing status
    
    Args:
        filing_status: Filing status
        
    Returns:
        Standard deduction amount
        
    Raises:
        TaxCalculationError: If filing status is invalid
    """
    if filing_status not in STANDARD_DEDUCTIONS:
        raise TaxCalculationError(
            f"Invalid filing status for deduction: {filing_status}"
        )
    
    return STANDARD_DEDUCTIONS[filing_status]


def calculate_tax(
    income: float,
    filing_status: str = "single",
    dependents: int = 0,
    additional_deductions: float = 0.0
) -> Dict:
    """
    Main tax calculation function with comprehensive error handling
    
    Args:
        income: Gross annual income
        filing_status: Filing status
        dependents: Number of dependents
        additional_deductions: Additional deductions beyond standard
        
    Returns:
        Dictionary with tax calculation results
        
    Raises:
        TaxCalculationError: If inputs are invalid
    """
    # Input validation
    if income < 0:
        raise TaxCalculationError("Income cannot be negative")
    
    if dependents < 0:
        raise TaxCalculationError("Number of dependents cannot be negative")
    
    if additional_deductions < 0:
        raise TaxCalculationError("Additional deductions cannot be negative")
    
    try:
        # Get standard deduction
        standard_deduction = get_standard_deduction(filing_status)
        
        # Calculate total deductions (use standard or itemized, whichever is higher)
        total_deductions = max(standard_deduction, additional_deductions)
        
        # Calculate taxable income
        taxable_income = max(0, income - total_deductions)
        
        # Calculate federal tax using progressive brackets
        federal_tax, marginal_rate, tax_bracket = calculate_progressive_tax(
            taxable_income, filing_status
        )
        
        # Calculate effective tax rate
        effective_rate = (federal_tax / income * 100) if income > 0 else 0.0
        
        # Generate explanation
        explanation = generate_calculation_explanation(
            income, taxable_income, federal_tax, filing_status,
            standard_deduction, total_deductions, marginal_rate
        )
        
        return {
            "gross_income": round(income, 2),
            "taxable_income": round(taxable_income, 2),
            "federal_tax": round(federal_tax, 2),
            "effective_rate": round(effective_rate, 2),
            "marginal_rate": round(marginal_rate * 100, 2),
            "tax_bracket": tax_bracket,
            "standard_deduction": round(standard_deduction, 2),
            "total_deductions": round(total_deductions, 2),
            "explanation": explanation
        }
    
    except TaxCalculationError:
        raise
    except Exception as e:
        raise TaxCalculationError(f"Unexpected error during tax calculation: {str(e)}")


def generate_calculation_explanation(
    income: float,
    taxable_income: float,
    federal_tax: float,
    filing_status: str,
    standard_deduction: float,
    total_deductions: float,
    marginal_rate: float
) -> str:
    """
    Generate a human-readable explanation of the tax calculation
    
    Args:
        income: Gross income
        taxable_income: Income after deductions
        federal_tax: Calculated federal tax
        filing_status: Filing status
        standard_deduction: Standard deduction amount
        total_deductions: Total deductions applied
        marginal_rate: Marginal tax rate
        
    Returns:
        Explanation string
    """
    deduction_type = "standard deduction" if total_deductions == standard_deduction else "itemized deductions"
    
    explanation = (
        f"For filing status '{filing_status.replace('_', ' ')}', "
        f"starting with gross income of ${income:,.2f}, "
        f"we applied ${total_deductions:,.2f} in {deduction_type}. "
        f"This results in taxable income of ${taxable_income:,.2f}. "
        f"Using 2024 progressive tax brackets, your federal tax is ${federal_tax:,.2f}. "
        f"Your marginal rate (rate on next dollar) is {marginal_rate*100:.0f}%."
    )
    
    return explanation
