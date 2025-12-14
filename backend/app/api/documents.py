from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.services.ocr import process_document, UPLOAD_DIR
from app.api.auth import get_current_active_user
import shutil
import os
import uuid
from app.autogen_agents.document_agent import create_document_agent
from autogen import UserProxyAgent
import json

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
    
    # Use Agent to parse data
    # Note: In a real app, this should be async or background task
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
