from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.services.rag import RAGService
from app.services.embedding import EmbeddingService
from app.services.completion import CompletionService
from app.services.supabase import SupabaseService
from app.api.dependencies.auth import get_current_user
from typing import Dict
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class SearchQuery(BaseModel):
    query: str

def get_rag_service():
    return RAGService(
        embedding_service=EmbeddingService(),
        completion_service=CompletionService(),
        supabase_service=SupabaseService()
    )

@router.post("/query")
async def search_query(
    search_query: SearchQuery,
    rag_service: RAGService = Depends(get_rag_service),
    current_user: Dict = Depends(get_current_user)
):
    """Search documents and generate response"""
    try:
        result = await rag_service.search_and_generate_response(
            query=search_query.query,
            client_id=current_user["client_id"],
            user_id=current_user["id"]
        )
        return result
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))