"""
ITR-1 SAHAJ Form Data Model
===========================
Official Indian Income Tax Return Form structure for AY 2024-25.
For resident individuals with income up to ₹50 lakh from:
- Salary/Pension
- One House Property
- Other Sources (interest, etc.)
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
from enum import Enum


class TaxRegime(str, Enum):
    """Tax regime options."""
    NEW = "new"  # Section 115BAC - Default
    OLD = "old"  # Chapter VI-A deductions allowed


class FilingStatus(str, Enum):
    """Filing status."""
    ORIGINAL = "original"
    REVISED = "revised"
    BELATED = "belated"


class EmploymentType(str, Enum):
    """Nature of employment."""
    GOVERNMENT = "government"
    PSU = "psu"
    PENSIONER = "pensioner"
    PRIVATE = "private"
    NOT_APPLICABLE = "not_applicable"


# ============================================================================
# PART A: GENERAL INFORMATION
# ============================================================================

class PartA_PersonalInfo(BaseModel):
    """Part A - General Information (Personal Details)."""
    
    # Identification
    pan: str = Field(..., pattern=r"^[A-Z]{5}\d{4}[A-Z]$", description="PAN Number")
    aadhaar: Optional[str] = Field(None, pattern=r"^\d{12}$", description="12-digit Aadhaar")
    
    # Personal Details
    first_name: str = Field(..., min_length=1, max_length=25)
    middle_name: Optional[str] = Field(None, max_length=25)
    last_name: str = Field(..., min_length=1, max_length=25)
    date_of_birth: date
    father_name: Optional[str] = Field(None, max_length=50)
    
    # Contact
    email: str = Field(..., description="Email for communication")
    mobile: str = Field(..., pattern=r"^\d{10}$", description="10-digit mobile")
    
    # Address
    flat_door_building: str = Field(..., max_length=50)
    road_street: Optional[str] = Field(None, max_length=50)
    area_locality: str = Field(..., max_length=50)
    city_town: str = Field(..., max_length=50)
    state: str = Field(..., max_length=50)
    pincode: str = Field(..., pattern=r"^\d{6}$")
    country: str = Field(default="INDIA")
    
    # Filing Details
    assessment_year: str = Field(default="2024-25")
    filing_status: FilingStatus = Field(default=FilingStatus.ORIGINAL)
    return_filed_under: str = Field(default="Section 139(1)")
    
    # Employment
    employment_type: EmploymentType = Field(default=EmploymentType.PRIVATE)
    employer_category: Optional[str] = None


# ============================================================================
# PART B: GROSS TOTAL INCOME
# ============================================================================

class SalaryIncome(BaseModel):
    """Income from Salary/Pension - Section 17."""
    
    employer_name: str
    employer_tan: Optional[str] = Field(None, pattern=r"^[A-Z]{4}\d{5}[A-Z]$")
    
    # Salary Components
    gross_salary: float = Field(ge=0, description="Section 17(1)")
    value_of_perquisites: float = Field(default=0, ge=0, description="Section 17(2)")
    profit_in_lieu_of_salary: float = Field(default=0, ge=0, description="Section 17(3)")
    
    # Exemptions under Section 10
    hra_exemption: float = Field(default=0, ge=0, description="HRA u/s 10(13A)")
    lta_exemption: float = Field(default=0, ge=0, description="LTA u/s 10(5)")
    other_exemptions: float = Field(default=0, ge=0)
    
    # Standard Deduction
    standard_deduction: float = Field(default=50000, ge=0, description="u/s 16(ia)")
    professional_tax: float = Field(default=0, ge=0, description="u/s 16(iii)")
    entertainment_allowance: float = Field(default=0, ge=0, description="u/s 16(ii)")
    
    @property
    def total_salary(self) -> float:
        return self.gross_salary + self.value_of_perquisites + self.profit_in_lieu_of_salary
    
    @property
    def total_exemptions(self) -> float:
        return self.hra_exemption + self.lta_exemption + self.other_exemptions
    
    @property
    def net_salary(self) -> float:
        return self.total_salary - self.total_exemptions - self.standard_deduction - self.professional_tax - self.entertainment_allowance


class HousePropertyIncome(BaseModel):
    """Income from House Property - Section 22-27."""
    
    is_self_occupied: bool = Field(default=True)
    
    # If let out
    annual_rent_received: float = Field(default=0, ge=0)
    municipal_taxes_paid: float = Field(default=0, ge=0)
    
    # Interest on borrowed capital (Section 24)
    interest_on_housing_loan: float = Field(default=0, ge=0, description="Max ₹2L for self-occupied")
    lender_name: Optional[str] = None
    lender_pan: Optional[str] = None
    loan_account_number: Optional[str] = None
    
    @property
    def net_annual_value(self) -> float:
        if self.is_self_occupied:
            return 0
        return self.annual_rent_received - self.municipal_taxes_paid
    
    @property
    def standard_deduction_30_percent(self) -> float:
        return self.net_annual_value * 0.30
    
    @property
    def income_from_house_property(self) -> float:
        nav = self.net_annual_value
        deduction = self.standard_deduction_30_percent
        interest = min(self.interest_on_housing_loan, 200000) if self.is_self_occupied else self.interest_on_housing_loan
        return nav - deduction - interest


class OtherSourcesIncome(BaseModel):
    """Income from Other Sources - Section 56."""
    
    # Interest Income
    savings_bank_interest: float = Field(default=0, ge=0)
    fixed_deposit_interest: float = Field(default=0, ge=0)
    income_tax_refund_interest: float = Field(default=0, ge=0)
    
    # Other
    family_pension: float = Field(default=0, ge=0)
    dividend_income: float = Field(default=0, ge=0)
    other_income: float = Field(default=0, ge=0)
    
    @property
    def total_other_income(self) -> float:
        return (
            self.savings_bank_interest +
            self.fixed_deposit_interest +
            self.income_tax_refund_interest +
            self.family_pension +
            self.dividend_income +
            self.other_income
        )


class PartB_GrossIncome(BaseModel):
    """Part B - Gross Total Income."""
    
    salary: Optional[SalaryIncome] = None
    house_property: Optional[HousePropertyIncome] = None
    other_sources: Optional[OtherSourcesIncome] = None
    agricultural_income: float = Field(default=0, ge=0, le=5000, description="Max ₹5000 for ITR-1")
    
    @property
    def gross_total_income(self) -> float:
        total = 0
        if self.salary:
            total += self.salary.net_salary
        if self.house_property:
            total += self.house_property.income_from_house_property
        if self.other_sources:
            total += self.other_sources.total_other_income
        return total


# ============================================================================
# PART C: DEDUCTIONS UNDER CHAPTER VI-A
# ============================================================================

class ChapterVIA_Deductions(BaseModel):
    """Part C - Deductions under Chapter VI-A (Old Regime)."""
    
    # Section 80C (Max ₹1,50,000)
    section_80c_total: float = Field(default=0, ge=0, le=150000)
    # Components: PPF, ELSS, LIC, NSC, Sukanya Samriddhi, etc.
    
    # Section 80CCC - Pension Fund (Part of 80C limit)
    section_80ccc: float = Field(default=0, ge=0)
    
    # Section 80CCD(1) - NPS Employee contribution (Part of 80C limit)
    section_80ccd_1: float = Field(default=0, ge=0)
    
    # Section 80CCD(1B) - Additional NPS (Max ₹50,000)
    section_80ccd_1b: float = Field(default=0, ge=0, le=50000)
    
    # Section 80CCD(2) - Employer NPS contribution (Max 10% of salary)
    section_80ccd_2: float = Field(default=0, ge=0)
    
    # Section 80CCH - Agniveer Corpus Fund
    section_80cch: float = Field(default=0, ge=0)
    
    # Section 80D - Health Insurance (Max ₹25,000 self, ₹50,000 senior)
    section_80d_self: float = Field(default=0, ge=0, le=25000)
    section_80d_parents: float = Field(default=0, ge=0, le=50000)
    health_checkup: float = Field(default=0, ge=0, le=5000, description="Included in 80D limit")
    
    # Section 80DD - Disabled Dependent
    section_80dd: float = Field(default=0, ge=0)
    
    # Section 80DDB - Medical Treatment
    section_80ddb: float = Field(default=0, ge=0)
    
    # Section 80E - Education Loan Interest
    section_80e: float = Field(default=0, ge=0)
    
    # Section 80EE/80EEA - Home Loan Interest (First-time buyers)
    section_80ee: float = Field(default=0, ge=0, le=50000)
    section_80eea: float = Field(default=0, ge=0, le=150000)
    
    # Section 80G - Donations
    section_80g: float = Field(default=0, ge=0)
    
    # Section 80GG - Rent Paid (no HRA received)
    section_80gg: float = Field(default=0, ge=0)
    
    # Section 80TTA - Savings Interest (Max ₹10,000)
    section_80tta: float = Field(default=0, ge=0, le=10000)
    
    # Section 80TTB - Senior Citizen Interest (Max ₹50,000)
    section_80ttb: float = Field(default=0, ge=0, le=50000)
    
    # Section 80U - Person with Disability
    section_80u: float = Field(default=0, ge=0)
    
    @property
    def total_deductions(self) -> float:
        return (
            min(self.section_80c_total + self.section_80ccc + self.section_80ccd_1, 150000) +
            self.section_80ccd_1b +
            self.section_80ccd_2 +
            self.section_80cch +
            self.section_80d_self +
            self.section_80d_parents +
            self.section_80dd +
            self.section_80ddb +
            self.section_80e +
            self.section_80ee +
            self.section_80eea +
            self.section_80g +
            self.section_80gg +
            self.section_80tta +
            self.section_80ttb +
            self.section_80u
        )


# ============================================================================
# PART D: TAX COMPUTATION
# ============================================================================

class TaxComputation(BaseModel):
    """Part D - Tax Computation."""
    
    gross_total_income: float = Field(ge=0)
    total_deductions: float = Field(default=0, ge=0)
    taxable_income: float = Field(ge=0)
    
    # Tax Payable
    tax_on_total_income: float = Field(ge=0)
    rebate_87a: float = Field(default=0, ge=0, description="Rebate u/s 87A")
    tax_after_rebate: float = Field(ge=0)
    surcharge: float = Field(default=0, ge=0)
    health_education_cess: float = Field(ge=0, description="4% cess")
    total_tax_payable: float = Field(ge=0)
    
    # Relief and Taxes Paid
    relief_89: float = Field(default=0, ge=0, description="Relief u/s 89")
    tds_total: float = Field(default=0, ge=0)
    advance_tax_paid: float = Field(default=0, ge=0)
    self_assessment_tax: float = Field(default=0, ge=0)
    
    @property
    def net_tax_payable_or_refund(self) -> float:
        paid = self.tds_total + self.advance_tax_paid + self.self_assessment_tax
        return self.total_tax_payable - paid - self.relief_89


# ============================================================================
# PART E: OTHER INFORMATION
# ============================================================================

class BankAccount(BaseModel):
    """Bank account for refund."""
    
    ifsc_code: str = Field(..., pattern=r"^[A-Z]{4}0[A-Z0-9]{6}$")
    bank_name: str
    account_number: str
    account_type: str = Field(default="Savings")  # Savings/Current
    is_refund_account: bool = Field(default=False)


class PartE_OtherInfo(BaseModel):
    """Part E - Other Information."""
    
    bank_accounts: List[BankAccount] = Field(default_factory=list)
    

# ============================================================================
# SCHEDULES
# ============================================================================

class TDSEntry(BaseModel):
    """Schedule TDS - TDS details."""
    
    tan_of_deductor: str = Field(..., pattern=r"^[A-Z]{4}\d{5}[A-Z]$")
    name_of_deductor: str
    income_under_head: str  # Salary, Other Sources, etc.
    amount_of_income: float = Field(ge=0)
    tds_deducted: float = Field(ge=0)
    tds_claimed_this_year: float = Field(ge=0)


class AdvanceTaxEntry(BaseModel):
    """Schedule IT - Advance Tax/Self-Assessment Tax."""
    
    bsr_code: str
    challan_date: date
    challan_serial: str
    amount: float = Field(ge=0)


# ============================================================================
# COMPLETE ITR-1 FORM
# ============================================================================

class ITR1_SAHAJ(BaseModel):
    """Complete ITR-1 SAHAJ Form for AY 2024-25."""
    
    # Form Identification
    form_name: str = Field(default="ITR-1 SAHAJ")
    assessment_year: str = Field(default="2024-25")
    financial_year: str = Field(default="2023-24")
    
    # Tax Regime Selection
    tax_regime: TaxRegime = Field(default=TaxRegime.NEW)
    
    # Form Parts
    part_a: PartA_PersonalInfo
    part_b: PartB_GrossIncome
    part_c: Optional[ChapterVIA_Deductions] = None  # Only for Old Regime
    part_d: Optional[TaxComputation] = None
    part_e: Optional[PartE_OtherInfo] = None
    
    # Schedules
    schedule_tds: List[TDSEntry] = Field(default_factory=list)
    schedule_it: List[AdvanceTaxEntry] = Field(default_factory=list)
    
    # Verification
    verification_place: Optional[str] = None
    verification_date: Optional[date] = None
    
    def compute_tax(self) -> TaxComputation:
        """Compute tax based on regime and income."""
        gti = self.part_b.gross_total_income
        
        # Deductions (only for old regime)
        deductions = 0
        if self.tax_regime == TaxRegime.OLD and self.part_c:
            deductions = self.part_c.total_deductions
        
        taxable = max(0, gti - deductions)
        
        # Calculate tax based on regime
        if self.tax_regime == TaxRegime.NEW:
            tax = self._calculate_tax_new_regime(taxable)
        else:
            tax = self._calculate_tax_old_regime(taxable)
        
        # Rebate u/s 87A
        rebate = 0
        if self.tax_regime == TaxRegime.NEW and taxable <= 700000:
            rebate = min(tax, 25000)
        elif self.tax_regime == TaxRegime.OLD and taxable <= 500000:
            rebate = min(tax, 12500)
        
        tax_after_rebate = max(0, tax - rebate)
        cess = tax_after_rebate * 0.04
        
        return TaxComputation(
            gross_total_income=gti,
            total_deductions=deductions,
            taxable_income=taxable,
            tax_on_total_income=tax,
            rebate_87a=rebate,
            tax_after_rebate=tax_after_rebate,
            surcharge=0,
            health_education_cess=cess,
            total_tax_payable=tax_after_rebate + cess,
            tds_total=sum(t.tds_claimed_this_year for t in self.schedule_tds)
        )
    
    def _calculate_tax_new_regime(self, taxable: float) -> float:
        """New Tax Regime (Section 115BAC) - AY 2024-25."""
        slabs = [
            (300000, 0),      # 0-3L: Nil
            (600000, 0.05),   # 3-6L: 5%
            (900000, 0.10),   # 6-9L: 10%
            (1200000, 0.15),  # 9-12L: 15%
            (1500000, 0.20),  # 12-15L: 20%
            (float('inf'), 0.30),  # Above 15L: 30%
        ]
        return self._apply_slabs(taxable, slabs)
    
    def _calculate_tax_old_regime(self, taxable: float) -> float:
        """Old Tax Regime - AY 2024-25."""
        slabs = [
            (250000, 0),      # 0-2.5L: Nil
            (500000, 0.05),   # 2.5-5L: 5%
            (1000000, 0.20),  # 5-10L: 20%
            (float('inf'), 0.30),  # Above 10L: 30%
        ]
        return self._apply_slabs(taxable, slabs)
    
    def _apply_slabs(self, income: float, slabs: list) -> float:
        """Apply tax slabs to income."""
        tax = 0
        prev = 0
        for limit, rate in slabs:
            if income <= prev:
                break
            taxable_in_slab = min(income, limit) - prev
            tax += taxable_in_slab * rate
            prev = limit
        return tax


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def create_itr1_from_conversational_data(data: dict) -> ITR1_SAHAJ:
    """Convert conversational filing data to ITR-1 format."""
    personal = data.get("personal_info", {})
    income = data.get("income", {})
    deductions = data.get("deductions", {})
    
    # Build Part A
    name_parts = personal.get("name", "").split()
    part_a = PartA_PersonalInfo(
        pan=personal.get("pan_number", "AAAAA0000A"),
        first_name=name_parts[0] if name_parts else "",
        last_name=" ".join(name_parts[1:]) if len(name_parts) > 1 else "",
        date_of_birth=date(1990, 1, 1),  # Placeholder
        email=personal.get("email", ""),
        mobile="0000000000",  # Placeholder
        flat_door_building="NA",
        area_locality="NA",
        city_town="NA",
        state="NA",
        pincode="000000",
    )
    
    # Build Part B
    salary_income = None
    if income.get("salary"):
        salary_income = SalaryIncome(
            employer_name=income.get("employer_name", "Unknown"),
            gross_salary=income.get("salary", 0),
        )
    
    part_b = PartB_GrossIncome(
        salary=salary_income,
        other_sources=OtherSourcesIncome(
            other_income=income.get("other_income", 0)
        ) if income.get("other_income") else None
    )
    
    # Build Part C (Deductions)
    part_c = ChapterVIA_Deductions(
        section_80c_total=min(deductions.get("section_80c", 0), 150000),
        section_80d_self=min(deductions.get("section_80d", 0), 25000),
    )
    
    # Create ITR-1
    regime = TaxRegime.NEW if data.get("regime", "new") == "new" else TaxRegime.OLD
    
    itr = ITR1_SAHAJ(
        tax_regime=regime,
        part_a=part_a,
        part_b=part_b,
        part_c=part_c if regime == TaxRegime.OLD else None,
    )
    
    # Compute tax
    itr.part_d = itr.compute_tax()
    
    return itr
