from pydantic import BaseModel, Field
from typing import Literal


class TaxInput(BaseModel):
    """Input model for tax calculation"""
    income: float = Field(gt=0, description="Annual income")
    filing_status: Literal["single", "married_joint", "married_separate", "head_of_household"] = "single"
    dependents: int = Field(ge=0, default=0, description="Number of dependents")
    deductions: float = Field(ge=0, default=0, description="Total deductions")
    state: str = Field(default="", description="State code for state taxes")


class TaxResult(BaseModel):
    """Result model for tax calculation"""
    gross_income: float
    taxable_income: float
    federal_tax: float
    effective_rate: float
    marginal_rate: float
    tax_bracket: str
    standard_deduction: float
    total_deductions: float
    explanation: str


class ExplanationRequest(BaseModel):
    """Request model for explanation generation"""
    query: str
    proficiency: Literal["novice", "intermediate", "expert"] = "novice"
    context: dict = {}


class ExplanationResponse(BaseModel):
    """Response model for explanation"""
    explanation: str
    proficiency: str
    technical_terms: list[str] = []
    related_topics: list[str] = []
