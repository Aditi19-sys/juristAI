import asyncio
from dotenv import load_dotenv
load_dotenv()
# The queue stores document processing jobs
# A 'job' is typically a dictionary containing file_path, user_id, and doc_id
document_queue = asyncio.Queue()

async def add_to_queue(job_data: dict):
    """
    Adds a new processing job to the queue.
    Example job_data: {"file_path": "temp/doc.pdf", "owner": "user@example.com"}
    """
    await document_queue.put(job_data)
    print(f"📥 Job added to queue. Current queue size: {document_queue.qsize()}")

def get_queue_size() -> int:
    """Returns the number of documents waiting to be processed."""
    return document_queue.qsize()