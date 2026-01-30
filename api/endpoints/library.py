import os
import shutil
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks, HTTPException
from typing import List
from core.security import get_current_user_email
from core.database import get_documents_collection
from models.domain import DocumentOut
from services.background.processor import process_document_job
from dotenv import load_dotenv
load_dotenv()
router = APIRouter()

# Directory for temporary file storage during processing
UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", status_code=202)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user_email)
):
    """Uploads a PDF and triggers background AI ingestion."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # 1. Save file locally for the worker to read
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 2. Create record in MongoDB
    doc_metadata = {
        "file_id": file_id,
        "owner": current_user,
        "filename": file.filename,
        "status": "processing",
        "file_path": file_path
    }
    await get_documents_collection().insert_one(doc_metadata)

    # 3. Add to background tasks
    background_tasks.add_task(process_document_job, doc_metadata)

    return {"message": "Upload successful. Processing has started.", "file_id": file_id}

@router.get("/", response_model=List[DocumentOut])
async def list_my_documents(current_user: str = Depends(get_current_user_email)):
    """Retrieve only the documents belonging to the logged-in user."""
    cursor = get_documents_collection().find({"owner": current_user})
    docs = await cursor.to_list(length=100)
    return docs