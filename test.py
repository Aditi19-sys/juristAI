import pytesseract
from pdf2image import convert_from_path
import os

# 1. Manually point to your tools (The "Safe" Way)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseractocr\tesseract.exe'
POPPLER_PATH = r'C:\poppler\Library\bin'

def test_system(pdf_path):
    try:
        # 2. Test Poppler: Convert PDF to Image
        print("Step 1: Converting PDF to Image (Testing Poppler)...")
        images = convert_from_path("uploads\AP_HC_on_FAO_v_JAO_1764002243.pdf", poppler_path=POPPLER_PATH, first_page=1, last_page=1)
        
        # 3. Test Tesseract: Read Text from Image
        print("Step 2: Extracting Text (Testing Tesseract)...")
        text = pytesseract.image_to_string(images[0])
        
        print("\n✅ SYSTEM READY! Extracted Text Snippet:")
        print("-" * 30)
        print(text[:200] + "...") 
        print("-" * 30)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Check if Poppler is in C:\\poppler\\Library\\bin and Tesseract is in C:\\Program Files\\Tesseract-OCR")

# Run the test (Put any PDF file name here)
# test_system("your_test_file.pdf")