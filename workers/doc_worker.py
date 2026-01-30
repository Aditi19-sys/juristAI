import asyncio
import logging
from services.background.queue_mgr import document_queue
from services.ingestion.pdf_engine import PDFManager
from core.database import get_documents_collection
from dotenv import load_dotenv
load_dotenv()
# Setup logging to see what's happening in the background
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DocumentWorker")

async def document_worker(queue: asyncio.Queue, vector_store):
    """
    The background engine that processes PDFs from the queue.
    """
    pdf_manager = PDFManager()
    logger.info("🚀 Document Worker started and waiting for jobs...")

    while True:
        # 1. Wait for a job from the queue
        job_data = await queue.get()
        
        try:
            file_id = job_data.get("file_id")
            file_path = job_data.get("file_path")
            logger.info(f"📄 Processing document: {job_data.get('filename')}")

            # 2. Run the heavy OCR and Embedding (using run_in_executor to avoid blocking)
            loop = asyncio.get_running_loop()
            chunks = await loop.run_in_executor(
                None, 
                pdf_manager.process_pdf, 
                file_path
            )

            # 3. Format chunks for the Vector Store
            # We add the owner and file_id to each chunk so we can filter searches later
            for chunk in chunks:
                chunk["metadata"] = {
                    "file_id": file_id,
                    "owner": job_data.get("owner"),
                    "filename": job_data.get("filename"),
                    "page": chunk.get("page_num")
                }

            # 4. Save to Vector Store
            # Note: We use the 'text' key expected by our MongoVectorStore wrapper
            formatted_docs = [
                {"text": c["chunk_text"], "embedding": c["embedding"], "metadata": c["metadata"]}
                for c in chunks
            ]
            
            await vector_store.collection.insert_many(formatted_docs)

            # 5. Update the document status in the main library collection
            await get_documents_collection().update_one(
                {"file_id": file_id},
                {"$set": {"status": "completed"}}
            )
            
            logger.info(f"✅ Successfully processed and indexed: {job_data.get('filename')}")

        except Exception as e:
            logger.error(f"❌ Error processing document {job_data.get('filename')}: {str(e)}")
            # Update status to failed so the user knows
            if job_data.get("file_id"):
                await get_documents_collection().update_one(
                    {"file_id": job_data.get("file_id")},
                    {"$set": {"status": "failed", "error": str(e)}}
                )
        
        finally:
            # 6. Mark the task as done in the queue
            queue.task_done()