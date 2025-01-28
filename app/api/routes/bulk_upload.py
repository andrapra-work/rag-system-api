from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from app.services.bulk_upload import BulkUploadService
from app.services.rag import RAGService
from app.services.embedding import EmbeddingService
from app.services.completion import CompletionService
from app.services.supabase import SupabaseService
from app.api.dependencies.auth import get_current_user
from app.config import get_settings
from typing import Dict, List
import logging

router = APIRouter()
logger = logging.getLogger(__name__)
settings = get_settings()

def get_bulk_upload_service():
    rag_service = RAGService(
        embedding_service=EmbeddingService(),
        completion_service=CompletionService(),
        supabase_service=SupabaseService()
    )
    return BulkUploadService(rag_service=rag_service)

@router.post("/csv")
async def upload_csv(
    file: UploadFile = File(...),
    bulk_upload_service: BulkUploadService = Depends(get_bulk_upload_service),
    current_user: Dict = Depends(get_current_user)
):
    """Upload documents via CSV file"""
    try:
        # Validate file extension
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=400,
                detail="Only CSV files are allowed"
            )
        
        # Read file content
        contents = await file.read()
        if len(contents) > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum limit of {settings.MAX_UPLOAD_SIZE} bytes"
            )
        
        # Process the file
        result = await bulk_upload_service.process_csv(
            file=contents,
            client_id=current_user["client_id"]
        )
        
        return result
    except Exception as e:
        logger.error(f"Error processing CSV upload: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/json")
async def upload_json(
    documents: List[Dict],
    bulk_upload_service: BulkUploadService = Depends(get_bulk_upload_service),
    current_user: Dict = Depends(get_current_user)
):
    """Upload documents via JSON"""
    try:
        # Validate documents structure
        for doc in documents:
            if 'title' not in doc or 'content' not in doc:
                raise HTTPException(
                    status_code=400,
                    detail="Each document must contain 'title' and 'content' fields"
                )
        
        # Process documents
        result = await bulk_upload_service.process_json(
            documents=documents,
            client_id=current_user["client_id"]
        )
        
        return result
    except Exception as e:
        logger.error(f"Error processing JSON upload: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))