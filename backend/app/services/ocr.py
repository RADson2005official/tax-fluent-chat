import os
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import shutil

# Set Tesseract path if needed (Windows default)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")

def process_document(file_path: str) -> str:
    """
    Process a document (image or PDF) and extract text.
    """
    filename = os.path.basename(file_path)
    ext = os.path.splitext(filename)[1].lower()
    
    text = ""
    
    try:
        if ext in ['.jpg', '.jpeg', '.png', '.bmp']:
            text = extract_text_from_image(file_path)
        elif ext == '.pdf':
            text = extract_text_from_pdf(file_path)
        else:
            return f"Unsupported file format: {ext}"
            
        return text
    except Exception as e:
        return f"Error processing document: {str(e)}"

def extract_text_from_image(image_path: str) -> str:
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        # Fallback or mock if Tesseract is missing
        if "tesseract is not installed" in str(e).lower() or "not found" in str(e).lower():
             print("Tesseract not found. Returning mock text.")
             return "[MOCK] Tesseract not installed. This is simulated extracted text from the image."
        raise e

def extract_text_from_pdf(pdf_path: str) -> str:
    try:
        # Convert PDF to images
        pages = convert_from_path(pdf_path)
        text = ""
        for page in pages:
            text += pytesseract.image_to_string(page) + "\n\n"
        return text
    except Exception as e:
        if "tesseract is not installed" in str(e).lower() or "not found" in str(e).lower() or "poppler" in str(e).lower():
             print("OCR tools not found. Returning mock text.")
             return "[MOCK] OCR tools missing. This is simulated extracted text from the PDF."
        raise e
