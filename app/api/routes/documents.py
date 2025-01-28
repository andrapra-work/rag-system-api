from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, List, Optional
from uuid import UUID
from app.services.supabase import SupabaseService
from app.api.dependencies.database import get_db
from app.api.dependencies.auth import get_current_user
from app.api.models.document import DocumentCreate, DocumentResponse, DocumentUpdate
from app.services.rag import RAGService
from app.services.embedding import EmbeddingService
from app.services.completion import CompletionService
import logging

security = HTTPBearer()
router = APIRouter()
logger = logging.getLogger(__name__)

def get_rag_service():
    return RAGService(
        embedding_service=EmbeddingService(),
        completion_service=CompletionService(),
        supabase_service=SupabaseService()
    )

@router.post("/")
async def create_document(
    document: Dict,
    rag_service: RAGService = Depends(get_rag_service),
    current_user: Dict = Depends(get_current_user)
):
    """Create a new document with embedding"""
    try:
        result = await rag_service.process_document(
            title=document["title"],
            content=document["content"],
            client_id=current_user["client_id"],
            metadata=document.get("metadata")
        )
        return result
    except Exception as e:
        logger.error(f"Error creating document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def list_documents(
    page: int = 1,
    page_size: int = 10,
    rag_service: RAGService = Depends(get_rag_service),
    current_user: Dict = Depends(get_current_user)
):
    """Get paginated list of documents"""
    try:
        result = await rag_service.get_client_documents(
            client_id=current_user["client_id"],
            page=page,
            page_size=page_size
        )
        return result
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/me",
    response_model=List[DocumentResponse],
    summary="Get Current User's Documents",
    description="Retrieve all documents belonging to the authenticated user",
    responses={
        200: {
            "description": "List of user's documents",
            "content": {
                "application/json": {
                    "example": [{
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "title": "Sample Document",
                        "content": "Document content here",
                        "client_id": "123e4567-e89b-12d3-a456-426614174000",
                        "created_at": "2024-02-20T12:00:00Z",
                        "updated_at": "2024-02-20T12:00:00Z"
                    }]
                }
            }
        },
        401: {
            "description": "Unauthorized - Invalid or missing token",
            "content": {
                "application/json": {
                    "example": {"detail": "Could not validate credentials"}
                }
            }
        }
    },
    dependencies=[Depends(security)]
)
async def get_user_documents(
    current_user: dict = Depends(get_current_user),
    page: int = 1,
    page_size: int = 10,
    supabase: SupabaseService = Depends()
):
    """
    Get all documents belonging to the current user.
    
    - **Authorization**: Requires Bearer token
    - **page**: Page number for pagination (optional, default: 1)
    - **page_size**: Number of items per page (optional, default: 10)
    
    Example Authorization header:
    ```
    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    ```
    """
    try:
        result = await supabase.get_client_documents(
            client_id=current_user["client_id"],
            page=page,
            page_size=page_size
        )
        return result["data"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))