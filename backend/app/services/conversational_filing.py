"""
Conversational Tax Filing Service
=================================
Manages a guided conversation flow for tax filing.
The chatbot asks questions step-by-step and extracts data from user responses.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import re


class FilingStep(BaseModel):
    """Represents a step in the tax filing conversation."""
    id: str
    category: str
    question: str
    follow_up: Optional[str] = None
    field_name: str
    extraction_patterns: List[str] = []
    required: bool = True
    completed: bool = False
    extracted_value: Any = None


class ConversationalFiling:
    """Manages the conversational tax filing flow."""
    
    # Define the filing steps/questions
    FILING_STEPS = [
        FilingStep(
            id="name",
            category="Personal Info",
            question="Hello! I'm your AI Tax Assistant. Let's start filing your tax return. First, could you please tell me your **full name** as it appears on your PAN card?",
            field_name="personal_info.name",
            extraction_patterns=[r"(?:my name is|i am|i'm)\s+([A-Za-z\s]+)", r"^([A-Za-z\s]{3,50})$"],
        ),
        FilingStep(
            id="pan",
            category="Personal Info", 
            question="Great! Now, what is your **PAN number**? (Format: ABCDE1234F)",
            field_name="personal_info.pan_number",
            extraction_patterns=[r"([A-Z]{5}\d{4}[A-Z])"],
        ),
        FilingStep(
            id="email",
            category="Personal Info",
            question="What is your **email address** for communication?",
            field_name="personal_info.email",
            extraction_patterns=[r"([\w\.-]+@[\w\.-]+\.\w+)"],
            required=False,
        ),
        FilingStep(
            id="employer",
            category="Income",
            question="Now let's move to your income. Who is your **employer** or company name?",
            field_name="income.employer_name",
            extraction_patterns=[r"(?:work at|employed at|company is|employer is)\s+(.+?)(?:\.|$)", r"^(.{3,100})$"],
        ),
        FilingStep(
            id="salary",
            category="Income",
            question="What is your **annual gross salary** (CTC)? You can say it in lakhs, like '8 lakh' or '₹800000'.",
            field_name="income.salary",
            extraction_patterns=[
                r"(?:₹|rs\.?|inr)\s*([\d,]+)",
                r"([\d,]+)\s*(?:₹|rs|inr|rupees)",
                r"(\d+(?:\.\d+)?)\s*(?:lakh|lac|l)",
                r"(\d+(?:\.\d+)?)\s*(?:crore|cr)",
            ],
        ),
        FilingStep(
            id="other_income",
            category="Income",
            question="Do you have any **other income** sources? (freelancing, rental income, interest, etc.) If yes, please mention the amount. If no, just say 'No' or 'None'.",
            field_name="income.other_income",
            extraction_patterns=[r"([\d,]+)", r"(\d+(?:\.\d+)?)\s*(?:lakh|lac|l)"],
            required=False,
        ),
        FilingStep(
            id="deduction_80c",
            category="Deductions",
            question="Let's check your deductions. How much have you invested in **Section 80C** instruments? (PPF, ELSS, LIC, NPS, etc.) Maximum limit is ₹1.5 lakh.",
            field_name="deductions.section_80c",
            extraction_patterns=[r"([\d,]+)", r"(\d+(?:\.\d+)?)\s*(?:lakh|lac|l)"],
            required=False,
        ),
        FilingStep(
            id="deduction_80d",
            category="Deductions",
            question="Do you pay **health insurance premium** (Section 80D)? If yes, how much per year?",
            field_name="deductions.section_80d",
            extraction_patterns=[r"([\d,]+)", r"(\d+(?:\.\d+)?)\s*(?:lakh|lac|l)"],
            required=False,
        ),
        FilingStep(
            id="hra",
            category="Deductions",
            question="Do you pay **house rent**? If yes, what is your monthly rent amount? (This helps claim HRA exemption)",
            field_name="deductions.hra_rent",
            extraction_patterns=[r"([\d,]+)"],
            required=False,
        ),
        FilingStep(
            id="regime",
            category="Tax Regime",
            question="Finally, which **tax regime** would you like to use?\n\n**New Regime**: Lower rates, no deductions\n**Old Regime**: Higher rates, allows deductions\n\nSay 'new' or 'old'. If unsure, say 'suggest' and I'll recommend based on your data.",
            field_name="regime",
            extraction_patterns=[r"\b(new|old|suggest)\b"],
        ),
    ]
    
    def __init__(self):
        self.steps = [step.model_copy() for step in self.FILING_STEPS]
        self.current_step_index = 0
        self.extracted_data = {
            "personal_info": {},
            "income": {},
            "deductions": {},
            "regime": "new",
            "financial_year": f"{datetime.now().year - 1}-{datetime.now().year}",
        }
        self.conversation_history = []
        
    @property
    def current_step(self) -> Optional[FilingStep]:
        if self.current_step_index < len(self.steps):
            return self.steps[self.current_step_index]
        return None
    
    @property
    def is_complete(self) -> bool:
        return self.current_step_index >= len(self.steps)
    
    @property
    def progress_percent(self) -> float:
        return (self.current_step_index / len(self.steps)) * 100
    
    def get_initial_message(self) -> str:
        """Get the first question to start the conversation."""
        return self.current_step.question if self.current_step else "All information collected!"
    
    def process_response(self, user_message: str) -> Dict[str, Any]:
        """
        Process user's response, extract data, and return next question or summary.
        """
        if self.is_complete:
            return self._get_completion_response()
        
        step = self.current_step
        
        # Try to extract value from user's response
        extracted_value = self._extract_value(user_message, step)
        
        # Check for skip/none responses
        is_skip = self._is_skip_response(user_message)
        
        if extracted_value is not None:
            # Store extracted value
            self._store_value(step.field_name, extracted_value)
            step.extracted_value = extracted_value
            step.completed = True
            
            # Move to next step
            self.current_step_index += 1
            
            # Generate response with confirmation and next question
            response = self._generate_confirmation(step, extracted_value)
            
            if not self.is_complete:
                response += f"\n\n{self.current_step.question}"
            else:
                response += self._get_summary()
                
            return {
                "response": response,
                "extracted_value": extracted_value,
                "field": step.field_name,
                "progress": self.progress_percent,
                "is_complete": self.is_complete,
                "extracted_data": self.extracted_data,
            }
            
        elif is_skip and not step.required:
            # Skip optional field
            step.completed = True
            self.current_step_index += 1
            
            if not self.is_complete:
                response = f"No problem, skipping that. {self.current_step.question}"
            else:
                response = "Got it!" + self._get_summary()
                
            return {
                "response": response,
                "extracted_value": None,
                "field": step.field_name,
                "progress": self.progress_percent,
                "is_complete": self.is_complete,
                "extracted_data": self.extracted_data,
            }
        else:
            # Couldn't extract, ask for clarification
            return {
                "response": f"I couldn't quite understand that. {step.follow_up or step.question}",
                "extracted_value": None,
                "field": step.field_name,
                "progress": self.progress_percent,
                "is_complete": False,
                "extracted_data": self.extracted_data,
            }
    
    def _extract_value(self, text: str, step: FilingStep) -> Optional[Any]:
        """Extract value from text using patterns."""
        text_lower = text.lower().strip()
        text_original = text.strip()
        
        for pattern in step.extraction_patterns:
            match = re.search(pattern, text_original, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                
                # Handle amount conversion
                if step.field_name in ["income.salary", "income.other_income", 
                                       "deductions.section_80c", "deductions.section_80d", 
                                       "deductions.hra_rent"]:
                    value = self._parse_amount(text_lower, value)
                
                return value
        
        # Special handling for name (accept any reasonable text)
        if step.id == "name" and len(text_original) >= 3 and text_original.replace(" ", "").isalpha():
            return text_original.title()
            
        return None
    
    def _parse_amount(self, context: str, value: str) -> float:
        """Parse amount with lakh/crore handling."""
        try:
            amount = float(value.replace(",", ""))
            
            if "lakh" in context or "lac" in context or " l" in context:
                amount *= 100000
            elif "crore" in context or "cr" in context:
                amount *= 10000000
                
            return amount
        except ValueError:
            return 0.0
    
    def _is_skip_response(self, text: str) -> bool:
        """Check if user wants to skip."""
        skip_words = ["no", "none", "nil", "skip", "n/a", "na", "nothing", "nope"]
        return text.lower().strip() in skip_words
    
    def _store_value(self, field_path: str, value: Any):
        """Store value in extracted_data using dot notation path."""
        parts = field_path.split(".")
        target = self.extracted_data
        
        for part in parts[:-1]:
            if part not in target:
                target[part] = {}
            target = target[part]
        
        target[parts[-1]] = value
    
    def _generate_confirmation(self, step: FilingStep, value: Any) -> str:
        """Generate confirmation message for extracted value."""
        confirmations = {
            "name": f"Nice to meet you, **{value}**! ✓",
            "pan": f"PAN recorded as **{value}** ✓",
            "email": f"Got it, I'll use **{value}** ✓",
            "employer": f"You work at **{value}** ✓",
            "salary": f"Annual salary: **₹{value:,.0f}** ✓" if isinstance(value, (int, float)) else f"Salary recorded ✓",
            "other_income": f"Other income: **₹{value:,.0f}** ✓" if isinstance(value, (int, float)) and value > 0 else "Noted ✓",
            "deduction_80c": f"Section 80C: **₹{value:,.0f}** ✓" if isinstance(value, (int, float)) else "Recorded ✓",
            "deduction_80d": f"Section 80D: **₹{value:,.0f}** ✓" if isinstance(value, (int, float)) else "Recorded ✓",
            "hra": f"Monthly rent: **₹{value:,.0f}** ✓" if isinstance(value, (int, float)) else "Recorded ✓",
            "regime": f"Using **{value.upper()} tax regime** ✓",
        }
        return confirmations.get(step.id, "Got it! ✓")
    
    def _get_summary(self) -> str:
        """Generate summary of collected data."""
        pi = self.extracted_data.get("personal_info", {})
        inc = self.extracted_data.get("income", {})
        ded = self.extracted_data.get("deductions", {})
        
        salary = inc.get("salary", 0) or 0
        other = inc.get("other_income", 0) or 0
        total_income = salary + other
        
        d80c = ded.get("section_80c", 0) or 0
        d80d = ded.get("section_80d", 0) or 0
        total_deductions = min(d80c, 150000) + min(d80d, 25000)  # Apply limits
        
        standard_deduction = 50000
        taxable = max(0, total_income - total_deductions - standard_deduction)
        
        # Calculate tax (new regime)
        tax = self._calculate_tax(taxable)
        
        return f"""

---

## 📋 Tax Filing Summary

**Personal Details**
- Name: {pi.get('name', 'N/A')}
- PAN: {pi.get('pan_number', 'N/A')}

**Income**
- Salary: ₹{salary:,.0f}
- Other Income: ₹{other:,.0f}
- **Total Income: ₹{total_income:,.0f}**

**Deductions**
- Section 80C: ₹{min(d80c, 150000):,.0f}
- Section 80D: ₹{min(d80d, 25000):,.0f}
- Standard Deduction: ₹{standard_deduction:,}

**Tax Calculation**
- Taxable Income: ₹{taxable:,.0f}
- **Estimated Tax: ₹{tax:,.0f}**

---

Your tax return is ready! Click **"Generate PDF"** to download your filled tax form."""
    
    def _calculate_tax(self, taxable_income: float) -> float:
        """Calculate tax under new regime."""
        slabs = [
            (300000, 0),
            (700000, 0.05),
            (1000000, 0.10),
            (1200000, 0.15),
            (1500000, 0.20),
            (float('inf'), 0.30),
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
        
        return round(tax * 1.04, 2)  # Add 4% cess
    
    def _get_completion_response(self) -> Dict[str, Any]:
        """Return response when filing is complete."""
        return {
            "response": "Your tax filing information is complete! You can now generate your PDF tax return.",
            "is_complete": True,
            "progress": 100,
            "extracted_data": self.extracted_data,
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary for storage."""
        return {
            "current_step_index": self.current_step_index,
            "extracted_data": self.extracted_data,
            "steps": [s.model_dump() for s in self.steps],
        }


# Session storage
_filing_sessions: Dict[str, ConversationalFiling] = {}


def get_filing_session(session_id: str) -> ConversationalFiling:
    """Get or create a filing session."""
    if session_id not in _filing_sessions:
        _filing_sessions[session_id] = ConversationalFiling()
    return _filing_sessions[session_id]


def clear_filing_session(session_id: str):
    """Clear a filing session."""
    if session_id in _filing_sessions:
        del _filing_sessions[session_id]
