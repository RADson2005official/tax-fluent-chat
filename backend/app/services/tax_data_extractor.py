"""
Tax Data Extractor Service
==========================
Extracts structured tax form data from conversational chat history.
Uses pattern matching and LLM-based extraction for accuracy.
"""

import re
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class PersonalInfo(BaseModel):
    """Personal information extracted from chat."""
    name: Optional[str] = None
    pan_number: Optional[str] = None
    aadhaar_last4: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[str] = None


class IncomeSource(BaseModel):
    """Income source information."""
    source_type: str  # salary, business, freelance, rental, capital_gains, other
    employer_name: Optional[str] = None
    amount: float = 0.0
    description: Optional[str] = None


class Deduction(BaseModel):
    """Tax deduction information."""
    section: str  # 80C, 80D, 80E, etc.
    description: str
    amount: float = 0.0


class ExtractedTaxData(BaseModel):
    """Complete extracted tax data from conversation."""
    financial_year: str = Field(default_factory=lambda: f"{datetime.now().year - 1}-{datetime.now().year}")
    personal_info: PersonalInfo = Field(default_factory=PersonalInfo)
    income_sources: List[IncomeSource] = Field(default_factory=list)
    deductions: List[Deduction] = Field(default_factory=list)
    filing_status: str = "individual"  # individual, huf, company
    regime: str = "new"  # old, new
    total_income: float = 0.0
    total_deductions: float = 0.0
    taxable_income: float = 0.0
    estimated_tax: float = 0.0
    extraction_confidence: float = 0.0
    missing_fields: List[str] = Field(default_factory=list)


class TaxDataExtractor:
    """Extracts structured tax data from conversation history."""
    
    # Patterns for extracting information
    AMOUNT_PATTERNS = [
        r'(?:₹|rs\.?|inr|rupees?)\s*([\d,]+(?:\.\d{2})?)',
        r'([\d,]+(?:\.\d{2})?)\s*(?:₹|rs\.?|inr|rupees?)',
        r'(\d+)\s*(?:lakh|lac|lacs|lakhs)',
        r'(\d+)\s*(?:crore|cr)',
        r'salary\s*(?:of|is|:)?\s*(?:₹|rs\.?|inr)?\s*([\d,]+)',
        r'(?:earn|earned|earning|income)\s*(?:of|is|:)?\s*(?:₹|rs\.?|inr)?\s*([\d,]+)',
    ]
    
    PAN_PATTERN = r'[A-Z]{5}\d{4}[A-Z]'
    EMAIL_PATTERN = r'[\w\.-]+@[\w\.-]+\.\w+'
    PHONE_PATTERN = r'(?:\+91[-\s]?)?[6-9]\d{9}'
    
    # Employer/Company patterns
    EMPLOYER_PATTERNS = [
        r'(?:work|working|employed|job)\s+(?:at|in|for|with)\s+([A-Za-z\s&]+?)(?:\s+(?:and|,|\.|\d))',
        r'(?:employer|company)\s+(?:is|:)\s+([A-Za-z\s&]+?)(?:\s+(?:and|,|\.|\d))',
        r'(?:from|at)\s+([A-Z][A-Za-z\s&]+?(?:Ltd|Limited|Inc|Corp|Technologies|Tech|Solutions|Services|Pvt|Private))',
    ]
    
    # Deduction patterns
    DEDUCTION_PATTERNS = {
        '80C': [
            r'(?:ppf|public provident fund)\s*(?:₹|rs\.?)?\s*([\d,]+)',
            r'(?:elss|equity linked)\s*(?:₹|rs\.?)?\s*([\d,]+)',
            r'(?:lic|life insurance)\s*(?:premium)?\s*(?:₹|rs\.?)?\s*([\d,]+)',
            r'(?:nps|national pension)\s*(?:₹|rs\.?)?\s*([\d,]+)',
        ],
        '80D': [
            r'(?:health insurance|medical insurance)\s*(?:premium)?\s*(?:₹|rs\.?)?\s*([\d,]+)',
            r'(?:mediclaim)\s*(?:₹|rs\.?)?\s*([\d,]+)',
        ],
        'HRA': [
            r'(?:hra|house rent)\s*(?:₹|rs\.?)?\s*([\d,]+)',
            r'(?:rent|rental)\s*(?:₹|rs\.?)?\s*([\d,]+)',
        ]
    }
    
    def __init__(self):
        self.extracted_data = ExtractedTaxData()
    
    def extract_from_conversation(self, conversation_history: List[Dict[str, str]]) -> ExtractedTaxData:
        """Extract tax data from conversation history."""
        # Reset extraction
        self.extracted_data = ExtractedTaxData()
        
        # Combine all user messages for extraction
        user_messages = []
        for msg in conversation_history:
            if msg.get("role") == "user":
                user_messages.append(msg.get("content", ""))
        
        combined_text = " ".join(user_messages).lower()
        original_text = " ".join(user_messages)
        
        # Extract personal info
        self._extract_personal_info(original_text)
        
        # Extract income
        self._extract_income(combined_text, original_text)
        
        # Extract deductions
        self._extract_deductions(combined_text)
        
        # Calculate totals
        self._calculate_totals()
        
        # Identify missing fields
        self._identify_missing_fields()
        
        # Calculate confidence
        self._calculate_confidence()
        
        return self.extracted_data
    
    def _extract_personal_info(self, text: str):
        """Extract personal information from text."""
        # PAN
        pan_match = re.search(self.PAN_PATTERN, text.upper())
        if pan_match:
            self.extracted_data.personal_info.pan_number = pan_match.group()
        
        # Email
        email_match = re.search(self.EMAIL_PATTERN, text.lower())
        if email_match:
            self.extracted_data.personal_info.email = email_match.group()
        
        # Phone
        phone_match = re.search(self.PHONE_PATTERN, text)
        if phone_match:
            self.extracted_data.personal_info.phone = phone_match.group()
        
        # Name patterns
        name_patterns = [
            r'(?:my name is|i am|i\'m)\s+([A-Za-z\s]+?)(?:\s+and|,|\.|\s+from)',
            r'(?:name|naam)\s*(?:is|:)\s*([A-Za-z\s]+?)(?:\s+and|,|\.)',
        ]
        for pattern in name_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                self.extracted_data.personal_info.name = match.group(1).strip().title()
                break
    
    def _extract_income(self, text_lower: str, text_original: str):
        """Extract income sources from text."""
        income_sources = []
        
        # Salary income
        salary_patterns = [
            r'salary\s*(?:of|is|:)?\s*(?:₹|rs\.?|inr)?\s*([\d,]+)',
            r'(?:earn|earning|earned)\s*(?:₹|rs\.?|inr)?\s*([\d,]+)\s*(?:per month|pm|monthly)?',
            r'(?:ctc|cost to company)\s*(?:of|is|:)?\s*(?:₹|rs\.?|inr)?\s*([\d,]+)',
            r'(?:annual|yearly)\s*(?:income|salary|package)\s*(?:of|is|:)?\s*(?:₹|rs\.?|inr)?\s*([\d,]+)',
        ]
        
        for pattern in salary_patterns:
            match = re.search(pattern, text_lower)
            if match:
                amount_str = match.group(1).replace(',', '')
                amount = float(amount_str)
                
                # Check if it's per month
                if 'month' in text_lower[match.start():match.end()+20] or 'pm' in text_lower[match.start():match.end()+10]:
                    amount *= 12  # Annualize
                
                # Check for lakh/crore
                context = text_lower[max(0, match.start()-5):match.end()+15]
                if 'lakh' in context or 'lac' in context:
                    amount *= 100000
                elif 'crore' in context or 'cr' in context:
                    amount *= 10000000
                
                # Find employer
                employer = None
                for emp_pattern in self.EMPLOYER_PATTERNS:
                    emp_match = re.search(emp_pattern, text_original, re.IGNORECASE)
                    if emp_match:
                        employer = emp_match.group(1).strip()
                        break
                
                income_sources.append(IncomeSource(
                    source_type="salary",
                    employer_name=employer,
                    amount=amount,
                    description="Salary income"
                ))
                break
        
        # Business/Freelance income
        business_patterns = [
            r'(?:business|freelance|self.?employed|consulting)\s*(?:income)?\s*(?:of|is|:)?\s*(?:₹|rs\.?|inr)?\s*([\d,]+)',
        ]
        
        for pattern in business_patterns:
            match = re.search(pattern, text_lower)
            if match:
                amount_str = match.group(1).replace(',', '')
                amount = float(amount_str)
                
                context = text_lower[max(0, match.start()-5):match.end()+15]
                if 'lakh' in context:
                    amount *= 100000
                
                income_sources.append(IncomeSource(
                    source_type="business",
                    amount=amount,
                    description="Business/Freelance income"
                ))
        
        # Rental income
        rental_patterns = [
            r'(?:rental|rent)\s*(?:income)?\s*(?:of|is|:)?\s*(?:₹|rs\.?|inr)?\s*([\d,]+)',
        ]
        
        for pattern in rental_patterns:
            match = re.search(pattern, text_lower)
            if match:
                amount_str = match.group(1).replace(',', '')
                amount = float(amount_str)
                
                income_sources.append(IncomeSource(
                    source_type="rental",
                    amount=amount,
                    description="Rental income"
                ))
        
        self.extracted_data.income_sources = income_sources
    
    def _extract_deductions(self, text: str):
        """Extract deduction information from text."""
        deductions = []
        
        for section, patterns in self.DEDUCTION_PATTERNS.items():
            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    amount_str = match.group(1).replace(',', '')
                    amount = float(amount_str)
                    
                    context = text[max(0, match.start()-5):match.end()+15]
                    if 'lakh' in context:
                        amount *= 100000
                    
                    deductions.append(Deduction(
                        section=section,
                        description=f"Section {section} deduction",
                        amount=amount
                    ))
                    break
        
        self.extracted_data.deductions = deductions
    
    def _calculate_totals(self):
        """Calculate total income and deductions."""
        self.extracted_data.total_income = sum(
            source.amount for source in self.extracted_data.income_sources
        )
        
        self.extracted_data.total_deductions = sum(
            ded.amount for ded in self.extracted_data.deductions
        )
        
        # Apply standard deduction of ₹50,000 for salaried
        has_salary = any(s.source_type == "salary" for s in self.extracted_data.income_sources)
        standard_deduction = 50000 if has_salary else 0
        
        self.extracted_data.taxable_income = max(
            0, 
            self.extracted_data.total_income - self.extracted_data.total_deductions - standard_deduction
        )
        
        # Estimate tax (new regime rates 2024-25)
        self.extracted_data.estimated_tax = self._calculate_tax_new_regime(
            self.extracted_data.taxable_income
        )
    
    def _calculate_tax_new_regime(self, taxable_income: float) -> float:
        """Calculate tax as per new regime 2024-25."""
        # New regime slabs (FY 2024-25)
        slabs = [
            (300000, 0),       # 0-3 lakh: Nil
            (700000, 0.05),    # 3-7 lakh: 5%
            (1000000, 0.10),   # 7-10 lakh: 10%
            (1200000, 0.15),   # 10-12 lakh: 15%
            (1500000, 0.20),   # 12-15 lakh: 20%
            (float('inf'), 0.30),  # Above 15 lakh: 30%
        ]
        
        tax = 0
        remaining = taxable_income
        prev_limit = 0
        
        for limit, rate in slabs:
            if remaining <= 0:
                break
            taxable_in_slab = min(remaining, limit - prev_limit)
            tax += taxable_in_slab * rate
            remaining -= taxable_in_slab
            prev_limit = limit
        
        # Add 4% cess
        tax *= 1.04
        
        return round(tax, 2)
    
    def _identify_missing_fields(self):
        """Identify fields that are missing for a complete tax return."""
        missing = []
        
        if not self.extracted_data.personal_info.name:
            missing.append("Name")
        if not self.extracted_data.personal_info.pan_number:
            missing.append("PAN Number")
        if not self.extracted_data.income_sources:
            missing.append("Income Details")
        if self.extracted_data.total_income == 0:
            missing.append("Income Amount")
        
        self.extracted_data.missing_fields = missing
    
    def _calculate_confidence(self):
        """Calculate extraction confidence score."""
        score = 0.0
        max_score = 6.0
        
        if self.extracted_data.personal_info.name:
            score += 1.0
        if self.extracted_data.personal_info.pan_number:
            score += 1.0
        if self.extracted_data.income_sources:
            score += 2.0
        if self.extracted_data.total_income > 0:
            score += 1.0
        if self.extracted_data.deductions:
            score += 1.0
        
        self.extracted_data.extraction_confidence = round(score / max_score, 2)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert extracted data to dictionary."""
        return self.extracted_data.model_dump()
    
    def to_json(self) -> str:
        """Convert extracted data to JSON string."""
        return self.extracted_data.model_dump_json(indent=2)


# Singleton instance
_extractor_instance: Optional[TaxDataExtractor] = None


def get_tax_extractor() -> TaxDataExtractor:
    """Get or create tax data extractor instance."""
    global _extractor_instance
    if _extractor_instance is None:
        _extractor_instance = TaxDataExtractor()
    return _extractor_instance
