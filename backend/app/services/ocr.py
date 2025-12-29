"""OCR Service for Document Processing.

Extracts text from images and PDFs using Tesseract OCR and PyMuPDF.
No external dependencies like Poppler required.
"""

import os
import pytesseract
from PIL import Image
import fitz  # PyMuPDF - no external dependencies needed

# Set Tesseract path for Windows
TESSERACT_PATHS = [
    r'C:\Program Files\Tesseract-OCR\tesseract.exe',
    r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
    r'C:\Users\BlueJAY2005\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
]

# Find Tesseract installation
for path in TESSERACT_PATHS:
    if os.path.exists(path):
        pytesseract.pytesseract.tesseract_cmd = path
        print(f"[OCR] Tesseract found at: {path}")
        break
else:
    print("[OCR] WARNING: Tesseract not found in common locations. OCR may fail.")

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")


def check_tesseract() -> bool:
    """Check if Tesseract is properly installed and accessible."""
    try:
        version = pytesseract.get_tesseract_version()
        print(f"[OCR] Tesseract version: {version}")
        return True
    except Exception as e:
        print(f"[OCR] Tesseract check failed: {e}")
        return False


def process_document(file_path: str) -> str:
    """
    Process a document (image or PDF) and extract text.
    
    Args:
        file_path: Path to the document file
        
    Returns:
        Extracted text or error message
    """
    filename = os.path.basename(file_path)
    ext = os.path.splitext(filename)[1].lower()
    
    print(f"[OCR] Processing document: {filename} (type: {ext})")
    
    try:
        if ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
            text = extract_text_from_image(file_path)
        elif ext == '.pdf':
            text = extract_text_from_pdf(file_path)
        else:
            return f"Error: Unsupported file format: {ext}. Supported: PDF, JPG, PNG, BMP"
        
        if text.strip():
            print(f"[OCR] Successfully extracted {len(text)} characters")
        else:
            print("[OCR] Warning: No text extracted from document")
            
        return text
        
    except Exception as e:
        error_msg = f"Error processing document: {str(e)}"
        print(f"[OCR] {error_msg}")
        return error_msg


def extract_text_from_image(image_path: str) -> str:
    """Extract text from an image file using Tesseract OCR."""
    try:
        # Check Tesseract first
        if not check_tesseract():
            return "Error: Tesseract OCR is not installed. Please install Tesseract from https://github.com/UB-Mannheim/tesseract/wiki"
        
        image = Image.open(image_path)
        
        # Convert to RGB if necessary (for RGBA images)
        if image.mode == 'RGBA':
            image = image.convert('RGB')
        
        text = pytesseract.image_to_string(image, lang='eng')
        return text
        
    except pytesseract.TesseractNotFoundError:
        return "Error: Tesseract OCR is not installed. Please install from: https://github.com/UB-Mannheim/tesseract/wiki"
    except Exception as e:
        return f"Error extracting text from image: {str(e)}"


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from PDF using PyMuPDF.
    First tries native text extraction, then falls back to OCR if needed.
    """
    try:
        doc = fitz.open(pdf_path)
        text = ""
        
        print(f"[OCR] PDF has {len(doc)} page(s)")
        
        for page_num, page in enumerate(doc):
            # First try native text extraction (much faster)
            page_text = page.get_text()
            
            if page_text.strip():
                text += f"--- Page {page_num + 1} ---\n{page_text}\n\n"
            else:
                # Page has no text - likely scanned image, use OCR
                print(f"[OCR] Page {page_num + 1} appears to be an image, using OCR...")
                
                # Check if Tesseract is available
                if not check_tesseract():
                    text += f"--- Page {page_num + 1} ---\n[Image page - Tesseract not installed for OCR]\n\n"
                    continue
                
                # Render page to image
                pix = page.get_pixmap(dpi=150)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                
                # Run OCR
                ocr_text = pytesseract.image_to_string(img, lang='eng')
                text += f"--- Page {page_num + 1} (OCR) ---\n{ocr_text}\n\n"
        
        doc.close()
        return text
        
    except Exception as e:
        return f"Error extracting text from PDF: {str(e)}"


# Test OCR on module load
if __name__ == "__main__":
    print("[OCR] Testing OCR setup...")
    if check_tesseract():
        print("[OCR] ✓ Tesseract is properly configured")
    else:
        print("[OCR] ✗ Tesseract is NOT configured")
