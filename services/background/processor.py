import asyncio
import os
from services.ingestion.pdf_engine import PDFManager
from core.database import get_knowledge_base_collection, connect_to_mongo

pdf_manager = PDFManager()

async def process_document_job(job, vector_store):
    await connect_to_mongo()
    collection = get_knowledge_base_collection()
    
    loop = asyncio.get_running_loop()
    try:
        chunks = await loop.run_in_executor(None, pdf_manager.process_pdf, job["file_path"])
        
        records = [{
            "embedding": c["embedding"],
            "text": c["chunk_text"],
            "metadata": {**job, "page": c["page_num"]}
        } for c in chunks]

        await collection.insert_many(records, ordered=False)
    finally:
        if os.path.exists(job["file_path"]):
            os.remove(job["file_path"])