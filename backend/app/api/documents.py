"""Documents API - Upload and process tax documents."""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.services.ocr import process_document, UPLOAD_DIR
from app.services.document_processor import process_tax_document
from app.api.auth import get_current_active_user
import shutil
import os
import uuid
import json

# Try to import autogen (optional - for legacy /upload endpoint)
try:
    from autogen import UserProxyAgent
    from app.autogen_agents.document_agent import create_document_agent
    AUTOGEN_AVAILABLE = True
except ImportError:
    UserProxyAgent = None
    AUTOGEN_AVAILABLE = False
    print("[Documents API] AutoGen not available - /upload endpoint will use fallback")

router = APIRouter(
    prefix="/documents",
    tags=["documents"]
)

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user = Depends(get_current_active_user)
):
    """
    Upload a tax document, perform OCR, and extract structured data.
    Uses GPT-4 via AutoGen if available, otherwise returns raw OCR text.
    """
    # Save file
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
        
    file_ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Perform OCR
    raw_text = process_document(file_path)
    
    # If AutoGen not available, return raw text
    if not AUTOGEN_AVAILABLE:
        return {
            "filename": file.filename,
            "raw_text": raw_text[:500] + "..." if len(raw_text) > 500 else raw_text,
            "parsed_data": {"note": "AutoGen not available. Use /upload-for-chat endpoint for LLaMA parsing."}
        }
    
    # Use Agent to parse data (legacy GPT-4 method)
    try:
        llm_config = {
            "config_list": [{
                "model": "gpt-4",
                "api_key": os.getenv("OPENAI_API_KEY")
            }],
            "temperature": 0
        }
        
        doc_agent = create_document_agent(llm_config)
        user_proxy = UserProxyAgent(
            name="UserProxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1,
            code_execution_config=False
        )
        
        # Ask agent to parse
        user_proxy.initiate_chat(
            doc_agent,
            message=f"Parse this tax document text into JSON:\n\n{raw_text}"
        )
        
        # Get last message
        last_msg = user_proxy.last_message()["content"]
        
        # Clean up JSON string if needed (remove markdown)
        if "```json" in last_msg:
            last_msg = last_msg.split("```json")[1].split("```")[0].strip()
        elif "```" in last_msg:
            last_msg = last_msg.split("```")[1].split("```")[0].strip()
            
        parsed_data = json.loads(last_msg)
        
    except Exception as e:
        print(f"Agent parsing failed: {e}")
        parsed_data = {"error": "Failed to parse data", "raw_text": raw_text}
    
    return {
        "filename": file.filename,
        "raw_text": raw_text[:500] + "...", # Truncate for response
        "parsed_data": parsed_data
    }


@router.post("/upload-for-chat")
async def upload_document_for_chat(
    file: UploadFile = File(...),
    session_id: str = "default"
):
    """
    Upload a tax document for chat-based extraction using LLaMA.
    This endpoint doesn't require authentication for easier chat integration.
    Returns data in the same format as chat extraction.
    """
    # Validate file type
    allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.bmp']
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Save file
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
        
    filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process document with LLaMA
        result = process_tax_document(file_path, session_id)
        
        return {
            "success": result.get("success", False),
            "filename": file.filename,
            "raw_text_preview": result.get("raw_text", "")[:300] + "...",
            "extracted_data": result.get("extracted_data"),
            "extraction_confidence": result.get("extraction_confidence", 0),
            "error": result.get("error")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
