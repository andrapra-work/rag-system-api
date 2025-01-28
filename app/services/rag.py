from app.services.embedding import EmbeddingService
from app.services.completion import CompletionService
from app.services.supabase import SupabaseService
from typing import Dict, List, Optional
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(
        self,
        embedding_service: EmbeddingService,
        completion_service: CompletionService,
        supabase_service: SupabaseService
    ):
        self.embedding_service = embedding_service
        self.completion_service = completion_service
        self.supabase = supabase_service

    async def process_document(
        self,
        title: str,
        content: str,
        client_id: UUID,
        metadata: Optional[Dict] = None
    ) -> Dict:
        try:
            # Generate embedding for the document
            embedding = await self.embedding_service.create_embedding(content)
            
            # Store document with embedding
            result = await self.supabase.create_document(
                title=title,
                content=content,
                client_id=client_id,
                embedding=embedding,
                metadata=metadata
            )
            
            return result
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            raise

    async def search_and_generate_response(
        self,
        query: str,
        client_id: UUID,
        user_id: UUID,
        limit: int = 5,
        threshold: float = 0.3  # Lower threshold further to get more results
    ) -> Dict:
        try:
            # Generate embedding for query
            logger.info(f"Generating embedding for query: {query}")
            query_embedding = await self.embedding_service.create_embedding(query)
            logger.info("Embedding generated successfully")
            
            # Search for relevant documents
            logger.info(f"Searching documents for client_id: {client_id}")
            relevant_docs = await self.supabase.search_documents(
                embedding=query_embedding,
                client_id=client_id,
                limit=limit,
                threshold=threshold
            )
            logger.info(f"Found {len(relevant_docs)} relevant documents with content: {[doc['content'] for doc in relevant_docs]}")
            
            if not relevant_docs:
                logger.warning("No relevant documents found")
                return {
                    "answer": "I don't have enough information to answer that question.",
                    "sources": []
                }
            
            # Generate response using context
            logger.info("Generating response with context")
            response = await self.completion_service.generate_response(
                query=query,
                context=relevant_docs
            )
            logger.info("Response generated successfully")
            
            # Log the query
            await self.supabase.log_query(
                user_id=user_id,
                client_id=client_id,
                query=query,
                embedding=query_embedding
            )
            
            return {
                "answer": response,
                "sources": relevant_docs
            }
        except Exception as e:
            logger.error(f"Error in search_and_generate_response: {str(e)}")
            raise