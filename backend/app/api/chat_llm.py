"""
LLaMA Chat API Endpoints
========================
API endpoints for the LLaMA-based Tax Expert chatbot.
Provides REST endpoints for chat, data extraction, and PDF generation.
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
import io

from app.services.llama_service import get_llama_expert, generate_llama_response
from app.services.tax_data_extractor import get_tax_extractor, ExtractedTaxData
from app.services.pdf_generator import generate_tax_return_pdf

router = APIRouter(prefix="/chat", tags=["LLaMA Chat"])


# ============ Request/Response Models ============

class ChatMessageRequest(BaseModel):
    """Request model for chat message."""
    message: str
    session_id: Optional[str] = "default"
    include_extraction: bool = True


class ChatMessageResponse(BaseModel):
    """Response model for chat message."""
    response: str
    session_id: str
    timestamp: str
    extracted_data: Optional[Dict[str, Any]] = None
    extraction_confidence: float = 0.0


class GeneratePDFRequest(BaseModel):
    """Request model for PDF generation."""
    session_id: Optional[str] = "default"
    user_data: Optional[Dict[str, Any]] = None  # Override extracted user data


# ============ In-memory Session Store ============

class SessionStore:
    """Simple in-memory session store for chat history and extracted data."""
    
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
    
    def get_session(self, session_id: str) -> Dict[str, Any]:
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "conversation_history": [],
                "extracted_data": None,
                "created_at": datetime.now().isoformat()
            }
        return self.sessions[session_id]
    
    def update_conversation(self, session_id: str, user_msg: str, assistant_msg: str):
        session = self.get_session(session_id)
        session["conversation_history"].append({"role": "user", "content": user_msg})
        session["conversation_history"].append({"role": "assistant", "content": assistant_msg})
    
    def update_extracted_data(self, session_id: str, data: ExtractedTaxData):
        session = self.get_session(session_id)
        session["extracted_data"] = data.model_dump()
    
    def get_conversation_history(self, session_id: str) -> List[Dict[str, str]]:
        return self.get_session(session_id)["conversation_history"]
    
    def get_extracted_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        return self.get_session(session_id).get("extracted_data")
    
    def clear_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]


# Global session store
session_store = SessionStore()


# ============ API Endpoints ============

@router.post("/message", response_model=ChatMessageResponse)
async def send_chat_message(request: ChatMessageRequest):
    """
    Send a message to the LLaMA Tax Expert and get a response.
    Optionally extracts structured tax data from the conversation.
    """
    try:
        expert = get_llama_expert()
        
        # Get history
        history = session_store.get_conversation_history(request.session_id)
        
        # Generate response with context
        response = await expert.generate(request.message, history=history)
        
        # Update session
        session_store.update_conversation(
            request.session_id, 
            request.message, 
            response
        )
        
        # Extract data if requested
        extracted_data = None
        extraction_confidence = 0.0
        
        if request.include_extraction:
            extractor = get_tax_extractor()
            history = session_store.get_conversation_history(request.session_id)
            extracted = extractor.extract_from_conversation(history)
            session_store.update_extracted_data(request.session_id, extracted)
            extracted_data = extracted.model_dump()
            extraction_confidence = extracted.extraction_confidence
        
        return ChatMessageResponse(
            response=response,
            session_id=request.session_id,
            timestamp=datetime.now().isoformat(),
            extracted_data=extracted_data,
            extraction_confidence=extraction_confidence
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@router.get("/extracted-data/{session_id}")
async def get_extracted_data(session_id: str):
    """Get the extracted tax data for a session."""
    data = session_store.get_extracted_data(session_id)
    if data is None:
        raise HTTPException(status_code=404, detail="No extracted data for this session")
    return data


@router.get("/history/{session_id}")
async def get_chat_history(session_id: str):
    """Get the conversation history for a session."""
    history = session_store.get_conversation_history(session_id)
    return {"session_id": session_id, "history": history}


@router.post("/clear/{session_id}")
async def clear_session(session_id: str):
    """Clear a chat session and its data."""
    session_store.clear_session(session_id)
    # Also clear LLaMA expert history
    expert = get_llama_expert()
    expert.clear_history()
    return {"message": f"Session {session_id} cleared"}


@router.post("/generate-pdf")
async def generate_pdf(request: GeneratePDFRequest):
    """
    Generate a PDF tax return from extracted data.
    Returns the PDF as a downloadable file.
    """
    try:
        # Get extracted data from session
        extracted_data = session_store.get_extracted_data(request.session_id)
        
        if extracted_data is None:
            raise HTTPException(
                status_code=400, 
                detail="No extracted data available. Please have a conversation first."
            )
        
        # Prepare data for PDF generator
        user_data = request.user_data or {}
        personal_info = extracted_data.get("personal_info", {})
        
        user_data_for_pdf = {
            "first_name": personal_info.get("name", "").split()[0] if personal_info.get("name") else "",
            "last_name": " ".join(personal_info.get("name", "").split()[1:]) if personal_info.get("name") else "",
            "email": personal_info.get("email", ""),
            "pan": personal_info.get("pan_number", "")
        }
        user_data_for_pdf.update(user_data)
        
        # Prepare tax data
        tax_data = {
            "filing_status": extracted_data.get("filing_status", "individual"),
            "w2s": [
                {
                    "employer": source.get("employer_name", "Unknown"),
                    "wages": source.get("amount", 0)
                }
                for source in extracted_data.get("income_sources", [])
                if source.get("source_type") == "salary"
            ],
            "form1099s": [
                {
                    "payer": source.get("description", "Other Income"),
                    "amount": source.get("amount", 0)
                }
                for source in extracted_data.get("income_sources", [])
                if source.get("source_type") != "salary"
            ],
            "deductions": extracted_data.get("deductions", []),
            "total_income": extracted_data.get("total_income", 0),
            "taxable_income": extracted_data.get("taxable_income", 0),
            "estimated_tax": extracted_data.get("estimated_tax", 0)
        }
        
        # Generate PDF
        pdf_bytes = generate_tax_return_pdf(user_data_for_pdf, tax_data)
        
        # Return as downloadable file
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=tax_return_{request.session_id}.pdf"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation error: {str(e)}")


@router.get("/model-status")
async def get_model_status():
    """Check if the LLaMA model is loaded and ready."""
    expert = get_llama_expert()
    return {
        "is_loaded": expert.is_loaded,
        "device": expert.device,
        "model_name": "LLaMA 3.2 Tax Expert (Fine-tuned)"
    }


@router.post("/load-model")
async def load_model():
    """Explicitly load the LLaMA model (useful for pre-warming)."""
    expert = get_llama_expert()
    success = expert.load_model()
    return {
        "success": success,
        "is_loaded": expert.is_loaded,
        "device": expert.device
    }


# ============ Conversational Filing Endpoints ============

from app.services.conversational_filing import get_filing_session, clear_filing_session


class ConversationalMessageRequest(BaseModel):
    """Request for conversational filing."""
    message: str
    session_id: Optional[str] = "filing_default"


@router.get("/filing/start/{session_id}")
async def start_filing(session_id: str):
    """Start or get the initial question for a filing session."""
    # Clear any existing session
    clear_filing_session(session_id)
    session = get_filing_session(session_id)
    
    return {
        "session_id": session_id,
        "response": session.get_initial_message(),
        "progress": session.progress_percent,
        "is_complete": session.is_complete,
        "current_step": session.current_step.id if session.current_step else None,
        "current_category": session.current_step.category if session.current_step else None,
    }


@router.post("/filing/respond")
async def filing_respond(request: ConversationalMessageRequest):
    """Process user's response in the filing conversation with AI fallback."""
    from app.services.openrouter_service import get_openrouter_service
    import re
    
    session = get_filing_session(request.session_id)
    
    if session.is_complete:
        return {
            "session_id": request.session_id,
            "response": "Your tax filing is already complete! Click Generate PDF to download.",
            "progress": 100,
            "is_complete": True,
            "extracted_data": session.extracted_data,
            "current_step": None,
            "current_category": None,
        }
    
    step = session.current_step
    user_message = request.message.strip()
    
    # Try pattern-based extraction first
    extracted_value = None
    
    # Enhanced extraction for different field types
    if step.id == "name":
        # Accept any name-like text
        if len(user_message) >= 2 and user_message.replace(" ", "").replace(".", "").isalpha():
            extracted_value = user_message.title()
    
    elif step.id == "pan":
        match = re.search(r"([A-Z]{5}\d{4}[A-Z])", user_message.upper())
        if match:
            extracted_value = match.group(1)
    
    elif step.id == "email":
        match = re.search(r"([\w\.-]+@[\w\.-]+\.\w+)", user_message.lower())
        if match:
            extracted_value = match.group(1)
    
    elif step.id == "employer":
        # Accept any reasonable company name
        if len(user_message) >= 2:
            extracted_value = user_message.title()
    
    elif step.id in ["salary", "other_income", "deduction_80c", "deduction_80d", "hra"]:
        # Handle numeric amounts
        text_lower = user_message.lower()
        
        # Try to extract number patterns
        amount = None
        
        # Pattern: "5 lakh", "5lakh", "5 lakhs"
        match = re.search(r"(\d+(?:\.\d+)?)\s*(?:lakh|lakhs|lac|lacs|l\b)", text_lower)
        if match:
            amount = float(match.group(1)) * 100000
        
        # Pattern: "5 crore"
        if not amount:
            match = re.search(r"(\d+(?:\.\d+)?)\s*(?:crore|cr)", text_lower)
            if match:
                amount = float(match.group(1)) * 10000000
        
        # Pattern: Plain number "500000" or "5,00,000"
        if not amount:
            # Remove commas and spaces, then try to parse
            cleaned = re.sub(r"[,\s₹]", "", user_message)
            match = re.search(r"(\d+(?:\.\d+)?)", cleaned)
            if match:
                amount = float(match.group(1))
        
        if amount and amount > 0:
            extracted_value = amount
    
    elif step.id == "regime":
        text_lower = user_message.lower()
        if "new" in text_lower:
            extracted_value = "new"
        elif "old" in text_lower:
            extracted_value = "old"
        elif "suggest" in text_lower:
            extracted_value = "new"  # Default to new regime
    
    # Check for skip responses
    skip_words = ["no", "none", "nil", "skip", "n/a", "na", "nothing", "nope", "0", "zero"]
    is_skip = user_message.lower() in skip_words
    
    # If extraction failed and not skipping, try AI fallback
    if extracted_value is None and not is_skip and not step.required == False:
        try:
            ai_service = get_openrouter_service()
            
            # Determine field type for AI
            field_type_map = {
                "name": "full name",
                "pan": "PAN number (format ABCDE1234F)",
                "email": "email address",
                "employer": "company/employer name",
                "salary": "annual salary amount in rupees",
                "other_income": "income amount in rupees",
                "deduction_80c": "investment amount in rupees",
                "deduction_80d": "insurance premium in rupees",
                "hra": "monthly rent amount in rupees",
                "regime": "tax regime (new or old)",
            }
            
            field_type = field_type_map.get(step.id, step.id)
            
            # Try AI extraction
            ai_result = await ai_service.extract_value(
                user_message, 
                field_type, 
                step.question
            )
            
            if ai_result and ai_result not in ["NOT_FOUND", "SKIP"]:
                # For amounts, try to parse the AI result
                if step.id in ["salary", "other_income", "deduction_80c", "deduction_80d", "hra"]:
                    try:
                        # Clean and parse
                        cleaned = re.sub(r"[,\s₹]", "", ai_result)
                        amount = float(cleaned)
                        if amount > 0:
                            extracted_value = amount
                    except:
                        # Try AI amount parser
                        parsed = await ai_service.parse_amount(ai_result)
                        if parsed:
                            extracted_value = parsed
                else:
                    extracted_value = ai_result
                    
            elif ai_result == "SKIP":
                is_skip = True
                
        except Exception as e:
            print(f"[Filing] AI fallback error: {e}")
    
    # Process the result
    if extracted_value is not None:
        # Store the value
        parts = step.field_name.split(".")
        target = session.extracted_data
        for part in parts[:-1]:
            if part not in target:
                target[part] = {}
            target = target[part]
        target[parts[-1]] = extracted_value
        
        step.extracted_value = extracted_value
        step.completed = True
        session.current_step_index += 1
        
        # Generate confirmation
        confirmations = {
            "name": f"Nice to meet you, **{extracted_value}**! ✓",
            "pan": f"PAN recorded as **{extracted_value}** ✓",
            "email": f"Got it, I'll use **{extracted_value}** ✓",
            "employer": f"You work at **{extracted_value}** ✓",
            "salary": f"Annual salary: **₹{extracted_value:,.0f}** ✓" if isinstance(extracted_value, (int, float)) else "Salary recorded ✓",
            "other_income": f"Other income: **₹{extracted_value:,.0f}** ✓" if isinstance(extracted_value, (int, float)) else "Noted ✓",
            "deduction_80c": f"Section 80C: **₹{extracted_value:,.0f}** ✓" if isinstance(extracted_value, (int, float)) else "Recorded ✓",
            "deduction_80d": f"Section 80D: **₹{extracted_value:,.0f}** ✓" if isinstance(extracted_value, (int, float)) else "Recorded ✓",
            "hra": f"Monthly rent: **₹{extracted_value:,.0f}** ✓" if isinstance(extracted_value, (int, float)) else "Recorded ✓",
            "regime": f"Using **{extracted_value.upper() if isinstance(extracted_value, str) else 'NEW'} tax regime** ✓",
        }
        response = confirmations.get(step.id, "Got it! ✓")
        
        if not session.is_complete:
            response += f"\n\n{session.current_step.question}"
        else:
            response += session._get_summary()
        
        return {
            "session_id": request.session_id,
            "response": response,
            "progress": session.progress_percent,
            "is_complete": session.is_complete,
            "extracted_data": session.extracted_data,
            "current_step": session.current_step.id if session.current_step else None,
            "current_category": session.current_step.category if session.current_step else None,
        }
    
    elif is_skip and not step.required:
        step.completed = True
        session.current_step_index += 1
        
        if session.is_complete:
            response = "Got it!" + session._get_summary()
        else:
            response = f"No problem, skipping that.\n\n{session.current_step.question}"
        
        return {
            "session_id": request.session_id,
            "response": response,
            "progress": session.progress_percent,
            "is_complete": session.is_complete,
            "extracted_data": session.extracted_data,
            "current_step": session.current_step.id if session.current_step else None,
            "current_category": session.current_step.category if session.current_step else None,
        }
    
    else:
        # Couldn't extract - ask for clarification
        clarification = f"I couldn't quite understand that. Could you please provide your **{step.id.replace('_', ' ')}** clearly?\n\n{step.question}"
        
        return {
            "session_id": request.session_id,
            "response": clarification,
            "progress": session.progress_percent,
            "is_complete": False,
            "extracted_data": session.extracted_data,
            "current_step": step.id,
            "current_category": step.category,
        }


@router.get("/filing/status/{session_id}")
async def filing_status(session_id: str):
    """Get the current status of a filing session."""
    session = get_filing_session(session_id)
    return {
        "session_id": session_id,
        "progress": session.progress_percent,
        "is_complete": session.is_complete,
        "extracted_data": session.extracted_data,
        "current_step": session.current_step.id if session.current_step else None,
        "current_category": session.current_step.category if session.current_step else None,
    }


@router.post("/filing/generate-pdf/{session_id}")
async def filing_generate_pdf(session_id: str):
    """Generate ITR-1 SAHAJ PDF from conversational filing session."""
    from app.services.pdf_generator import generate_itr1_pdf
    
    session = get_filing_session(session_id)
    
    if not session.is_complete:
        raise HTTPException(
            status_code=400,
            detail="Filing is not complete. Please answer all questions first."
        )
    
    # Use the session's extracted data directly
    data = session.extracted_data
    
    # Generate ITR-1 format PDF
    pdf_bytes = generate_itr1_pdf(data)
    
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=ITR1_SAHAJ_{session_id}.pdf"
        }
    )


@router.delete("/filing/{session_id}")
async def clear_filing(session_id: str):
    """Clear a filing session."""
    clear_filing_session(session_id)
    return {"message": f"Filing session {session_id} cleared"}

