from supabase import create_client
from app.config import get_settings
from typing import Dict, List, Optional, Any
from uuid import UUID
import logging
from fastapi import HTTPException

settings = get_settings()

class SupabaseService:
    def __init__(self):
        self.client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_KEY
        )
        self.logger = logging.getLogger(__name__)

    def get_user_by_email(self, email: str):
        try:
            print(f"Checking email: {email}")  # Debug print
            response = self.client.table('users')\
                .select("*")\
                .eq('email', email)\
                .execute()
            
            print(f"Response data: {response.data}")  # Debug print
            data = response.data
            result = data[0] if data else None
            print(f"Returning result: {result}")  # Debug print
            return result
        except Exception as e:
            print(f"Error in get_user_by_email: {str(e)}")  # Debug print
            return None

    async def get_user_by_id(self, user_id: UUID) -> Optional[Dict]:
        """Retrieve user by ID"""
        try:
            response = self.client.table('users')\
                .select("*")\
                .eq('id', str(user_id))\
                .single()\
                .execute()
            return response.data
        except Exception as e:
            self.logger.error(f"Error fetching user by ID: {str(e)}")
            return None

    async def create_document(
        self,
        title: str,
        content: str,
        client_id: UUID,
        embedding: List[float],
        metadata: Optional[Dict] = None
    ) -> Dict:
        """Create a new document with embedding"""
        try:
            self.logger.info(f"Creating document for client_id: {client_id}")
            self.logger.info(f"Embedding length: {len(embedding)}")
            
            # Verify embedding format
            if not isinstance(embedding, list) or len(embedding) != 1536:
                raise ValueError(f"Invalid embedding format. Expected list of 1536 floats, got length: {len(embedding)}")
            
            document_data = {
                'title': title,
                'content': content,
                'client_id': str(client_id),
                'embedding': embedding,
                'metadata': metadata or {}
            }
            
            self.logger.info("Inserting document with data structure:")
            self.logger.info(f"Title: {title}")
            self.logger.info(f"Content length: {len(content)}")
            self.logger.info(f"Client ID: {client_id}")
            
            response = self.client.table('documents')\
                .insert(document_data)\
                .execute()
            
            if not response.data:
                raise HTTPException(status_code=400, detail="Failed to create document")
            
            created_doc = response.data[0]
            self.logger.info(f"Document created successfully: {created_doc['id']}")
            
            # Verify the document was created with embedding
            verify = self.client.table('documents')\
                .select('id, embedding')\
                .eq('id', created_doc['id'])\
                .execute()
            
            self.logger.info(f"Verification - document has embedding: {bool(verify.data[0].get('embedding'))}")
            
            return created_doc
        except Exception as e:
            self.logger.error(f"Error creating document: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def search_documents(
        self,
        embedding: List[float],
        client_id: UUID,
        limit: int = 5,
        threshold: float = 0.5
    ) -> List[Dict]:
        """Search documents using vector similarity"""
        try:
            self.logger.info(f"Searching documents for client_id: {client_id}")
            
            # First, check if documents exist for this client
            docs_check = self.client.table('documents')\
                .select('id, title')\
                .eq('client_id', str(client_id))\
                .execute()
            
            self.logger.info(f"Found {len(docs_check.data)} total documents for client")
            
            if not docs_check.data:
                self.logger.warning("No documents found for this client")
                return []
            
            # Then perform the vector search
            response = self.client.rpc(
                'match_documents',
                {
                    'query_embedding': embedding,
                    'client_id': str(client_id),
                    'match_threshold': threshold,
                    'match_count': limit
                }
            ).execute()
            
            self.logger.info(f"Vector search response: {response.data}")
            
            return response.data if response.data else []
        except Exception as e:
            self.logger.error(f"Error searching documents: {str(e)}")
            raise

    async def log_query(
        self,
        user_id: UUID,
        client_id: UUID,
        query: str,
        embedding: List[float]
    ) -> None:
        """Log search query with embedding"""
        try:
            self.client.table('query_logs')\
                .insert({
                    'user_id': str(user_id),
                    'client_id': str(client_id),
                    'query': query,
                    'embedding': embedding
                })\
                .execute()
        except Exception as e:
            self.logger.error(f"Error logging query: {str(e)}")
            # Don't raise exception for logging errors

    async def get_client_documents(
        self,
        client_id: UUID,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """Get paginated documents for a client"""
        try:
            # Get total count
            count_response = self.client.table('documents')\
                .select("id", count="exact")\
                .eq('client_id', str(client_id))\
                .execute()
            
            total = count_response.count or 0

            # Get documents
            response = self.client.table('documents')\
                .select("*")\
                .eq('client_id', str(client_id))\
                .range((page - 1) * page_size, page * page_size - 1)\
                .order('created_at', desc=True)\
                .execute()

            return {
                "data": response.data,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
        except Exception as e:
            self.logger.error(f"Error fetching client documents: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def update_document(
        self,
        document_id: UUID,
        client_id: UUID,
        updates: Dict
    ) -> Dict:
        """Update document details"""
        try:
            response = self.client.table('documents')\
                .update(updates)\
                .eq('id', str(document_id))\
                .eq('client_id', str(client_id))\
                .execute()
            
            if not response.data:
                raise HTTPException(status_code=404, detail="Document not found")
                
            return response.data[0]
        except Exception as e:
            self.logger.error(f"Error updating document: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def delete_document(
        self,
        document_id: UUID,
        client_id: UUID
    ) -> bool:
        """Delete a document"""
        try:
            response = self.client.table('documents')\
                .delete()\
                .eq('id', str(document_id))\
                .eq('client_id', str(client_id))\
                .execute()
            
            return bool(response.data)
        except Exception as e:
            self.logger.error(f"Error deleting document: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def create_user(self, user_data: dict):
        response = self.client.table('users')\
            .insert(user_data)\
            .execute()
        return response.data[0] if response.data else None

    async def update_user(self, user_id: str, update_data: dict):
        response = self.client.table('users')\
            .update(update_data)\
            .eq('id', user_id)\
            .execute()
        return response.data[0] if response.data else None