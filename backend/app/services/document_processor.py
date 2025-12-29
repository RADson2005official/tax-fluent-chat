"""Document Processor Service.

Processes uploaded documents using OCR and LLaMA for tax data extraction.
Replaces GPT-4 based parsing with the local LLaMA model.
"""

from typing import Dict, Any, Optional
from app.services.ocr import process_document
from app.services.llama_service import get_llama_expert
from app.services.tax_data_extractor import ExtractedTaxData, get_tax_extractor
import json
import re


# Prompt template for document parsing
DOCUMENT_PARSE_PROMPT = """You are an expert at parsing Indian tax documents. 
Analyze the following OCR-extracted text from a tax document (Form 16, salary slip, etc.) and extract all relevant tax information.

Document Text:
---
{document_text}
---

Extract and return a JSON object with:
- employer_name: Name of employer (if found)
- employee_name: Name of employee (if found)  
- pan_number: PAN number (if found, format: XXXXX0000X)
- financial_year: Financial year (if found)
- income_details:
  - gross_salary: Total gross salary amount
  - basic_salary: Basic salary (if specified separately)
  - hra: House Rent Allowance (if found)
  - other_allowances: Other allowances
- deductions:
  - section_80c: Amount under 80C (PPF, ELSS, LIC, etc.)
  - section_80d: Medical insurance premium
  - hra_exemption: HRA exemption claimed
  - standard_deduction: Standard deduction (usually 50,000)
  - professional_tax: Professional tax deducted
- tax_details:
  - tds_deducted: Total TDS deducted
  - tax_payable: Tax payable

Return ONLY valid JSON, no other text. Use null for fields not found."""


def extract_json_from_response(response: str) -> Dict[str, Any]:
    """Extract JSON from LLaMA response, handling markdown code blocks."""
    # Try to find JSON in code blocks
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', response)
    if json_match:
        response = json_match.group(1).strip()
    
    # Try to parse as-is
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        pass
    
    # Try to find JSON object in response
    json_match = re.search(r'\{[\s\S]*\}', response)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
    
    return {"error": "Failed to parse response", "raw_response": response[:500]}


def process_tax_document(file_path: str, session_id: str = "default") -> Dict[str, Any]:
    """
    Process a tax document file and extract structured data using OCR + LLaMA.
    
    Args:
        file_path: Path to the uploaded document
        session_id: Chat session ID for context
        
    Returns:
        Dict with extracted tax data and confidence scores
    """
    # Step 1: OCR - Extract text from document
    raw_text = process_document(file_path)
    
    if raw_text.startswith("Error") or raw_text.startswith("[MOCK]"):
        return {
            "success": False,
            "error": raw_text,
            "raw_text": raw_text,
            "extracted_data": None
        }
    
    # Step 2: Use LLaMA to parse the document
    llama = get_llama_expert()
    
    # Load model if not loaded
    if not llama._is_loaded:
        loaded = llama.load_model()
        if not loaded:
            return {
                "success": False,
                "error": "Failed to load LLaMA model",
                "raw_text": raw_text[:500],
                "extracted_data": None
            }
    
    # Prepare prompt for document parsing
    parse_prompt = DOCUMENT_PARSE_PROMPT.format(document_text=raw_text[:4000])
    
    try:
        # Generate response using LLaMA
        response = llama.generate(parse_prompt)
        
        # Parse JSON from response
        parsed_data = extract_json_from_response(response)
        
        # Convert to ExtractedTaxData format for consistency
        extracted = convert_to_extracted_format(parsed_data)
        
        return {
            "success": True,
            "raw_text": raw_text[:1000] + "..." if len(raw_text) > 1000 else raw_text,
            "parsed_data": parsed_data,
            "extracted_data": extracted,
            "extraction_confidence": calculate_confidence(extracted)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "raw_text": raw_text[:500],
            "extracted_data": None
        }


def convert_to_extracted_format(parsed_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert parsed document data to ExtractedTaxData format."""
    
    income_sources = []
    
    # Add salary income if found
    income_details = parsed_data.get("income_details", {})
    if income_details:
        gross_salary = income_details.get("gross_salary") or 0
        if gross_salary:
            income_sources.append({
                "source_type": "salary",
                "employer_name": parsed_data.get("employer_name", ""),
                "amount": float(str(gross_salary).replace(",", "").replace("₹", ""))
            })
    
    # Collect deductions
    deductions = []
    deduction_data = parsed_data.get("deductions", {})
    
    if deduction_data.get("section_80c"):
        deductions.append({
            "section": "80C",
            "amount": float(str(deduction_data["section_80c"]).replace(",", "").replace("₹", ""))
        })
    
    if deduction_data.get("section_80d"):
        deductions.append({
            "section": "80D", 
            "amount": float(str(deduction_data["section_80d"]).replace(",", "").replace("₹", ""))
        })
    
    if deduction_data.get("standard_deduction"):
        deductions.append({
            "section": "Standard",
            "amount": float(str(deduction_data["standard_deduction"]).replace(",", "").replace("₹", ""))
        })
    
    # Calculate totals
    total_income = sum(inc.get("amount", 0) for inc in income_sources)
    total_deductions = sum(ded.get("amount", 0) for ded in deductions)
    taxable_income = max(0, total_income - total_deductions)
    
    # Determine missing fields
    missing_fields = []
    if not parsed_data.get("employee_name"):
        missing_fields.append("Name")
    if not parsed_data.get("pan_number"):
        missing_fields.append("PAN Number")
    if total_income == 0:
        missing_fields.append("Income Details")
    
    return {
        "personal_info": {
            "name": parsed_data.get("employee_name"),
            "pan_number": parsed_data.get("pan_number"),
            "email": None
        },
        "income_sources": income_sources,
        "deductions": deductions,
        "total_income": total_income,
        "total_deductions": total_deductions,
        "taxable_income": taxable_income,
        "estimated_tax": estimate_tax(taxable_income),
        "extraction_confidence": 0.7 if total_income > 0 else 0.3,
        "missing_fields": missing_fields
    }


def calculate_confidence(extracted: Dict[str, Any]) -> float:
    """Calculate extraction confidence based on filled fields."""
    score = 0.0
    
    if extracted.get("personal_info", {}).get("name"):
        score += 0.15
    if extracted.get("personal_info", {}).get("pan_number"):
        score += 0.15
    if extracted.get("income_sources"):
        score += 0.3
    if extracted.get("deductions"):
        score += 0.2
    if extracted.get("total_income", 0) > 0:
        score += 0.2
    
    return min(1.0, score)


def estimate_tax(taxable_income: float) -> float:
    """Estimate tax based on new tax regime slabs (FY 2024-25)."""
    if taxable_income <= 300000:
        return 0
    elif taxable_income <= 700000:
        return (taxable_income - 300000) * 0.05
    elif taxable_income <= 1000000:
        return 20000 + (taxable_income - 700000) * 0.10
    elif taxable_income <= 1200000:
        return 50000 + (taxable_income - 1000000) * 0.15
    elif taxable_income <= 1500000:
        return 80000 + (taxable_income - 1200000) * 0.20
    else:
        return 140000 + (taxable_income - 1500000) * 0.30
