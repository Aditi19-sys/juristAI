import asyncio
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import List, Dict
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from core.config import settings
from core.database import get_knowledge_base_collection 

# Create a global executor to avoid repeated creation/destruction
executor = ProcessPoolExecutor(max_workers=4)

def ocr_worker(args):
    page_number, image = args
    pytesseract.pytesseract.tesseract_cmd = r'c:\Program Files\Tesseractocr\tesseract.exe'
    text = pytesseract.image_to_string(image, lang="eng", config="--oem 3 --psm 6")
    return {"page": page_number, "text": text.strip()}

class PDFManager:
    def __init__(self, ocr_workers: int = 8, overlap_ratio: float = 0.2):
        self.ocr_workers = ocr_workers
        self.overlap_ratio = overlap_ratio
        # Ensure the model dimension is 768 to match your Atlas Index
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001", 
            google_api_key=settings.GEMINI_API_KEY
        )

    def process_pdf(self, pdf_path: str) -> List[Dict]:
        images = convert_from_path(pdf_path, dpi=150, poppler_path="c:\\poppler\\Library\\bin")
        tasks = [(i + 1, img) for i, img in enumerate(images)]
        
        # Use the global executor instead of "with ProcessPoolExecutor..."
        futures = [executor.submit(ocr_worker, t) for t in tasks]
        
        pages = []
        for future in as_completed(futures):
            pages.append(future.result())
        
        pages.sort(key=lambda x: x["page"])
        chunks = self._chunk_pages(pages)
        return self._embed_chunks(chunks)

    def _chunk_pages(self, pages: List[Dict]) -> List[Dict]:
        """Adds overlap between pages for better semantic context."""
        chunks = []
        for i, page in enumerate(pages):
            text = page["text"]
            # Simple overlap logic: take a percentage of the next page
            if i + 1 < len(pages):
                next_text = pages[i + 1]["text"]
                overlap_len = int(len(next_text) * self.overlap_ratio)
                overlap = next_text[:overlap_len]
                text += "\n" + overlap
            
            chunks.append({
                "text": text, 
                "metadata": {"page": page["page"]}
            })
        return chunks

    def _embed_chunks(self, chunks: List[Dict]) -> List[Dict]:
        """Generates 768-dimension vectors using Google Generative AI."""
        texts = [c["text"] for c in chunks]
        # langchain_google_genai handles the API calls
        vectors = self.embeddings.embed_documents(texts)
        
        # Map back to a list of dicts suitable for MongoDB
        return [
            {
                "page_num": c["metadata"]["page"], 
                "chunk_text": c["text"], 
                "embedding": v # Must match the 'path' in your Atlas Index
            } 
            for c, v in zip(chunks, vectors)
        ]

    async def save_to_mongo(self, pdf_path: str, document_name: str):
        """
        The main entry point: Processes the PDF and saves to MongoDB asynchronously.
        This prevents the FastAPI 'forever loading' issue.
        """
        # 1. OCR and Embedding (Heavier CPU/Network task)
        # Running in a thread pool to prevent blocking the main async loop
        loop = asyncio.get_event_loop()
        embedded_chunks = await loop.run_in_executor(
            None, self.process_pdf, pdf_path
        )
        
        if not embedded_chunks:
            print(f"⚠️ No text found in {document_name}")
            return

        # 2. Add document metadata for filtering
        for chunk in embedded_chunks:
            chunk["document_name"] = document_name
            chunk["timestamp"] = time.time()

        # 3. Save to MongoDB Knowledge Base
        collection = get_knowledge_base_collection()
        
        try:
            # result = await for Motor/Async driver
            result = await collection.insert_many(embedded_chunks)
            print(f"✅ Successfully saved {len(result.inserted_ids)} chunks for '{document_name}' to MongoDB.")
            return len(result.inserted_ids)
        except Exception as e:
            print(f"💥 Error saving to MongoDB: {str(e)}")
            raise e