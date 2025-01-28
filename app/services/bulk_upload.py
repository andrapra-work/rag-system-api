from typing import List, Dict, Optional
import pandas as pd
import asyncio
from app.services.embedding import EmbeddingService
from app.services.supabase import SupabaseService
from uuid import UUID
import logging
from fastapi import UploadFile, HTTPException
import io
import json
from app.services.rag import RAGService

logger = logging.getLogger(__name__)

class BulkUploadService:
    def __init__(self, rag_service: RAGService):
        self.embedding_service = EmbeddingService()
        self.supabase = SupabaseService()
        self.batch_size = 5  # Adjust based on your needs
        self.rag_service = rag_service

    async def process_batch(
        self,
        documents: List[Dict],
        client_id: UUID
    ) -> List[Dict]:
        """Process a batch of documents"""
        try:
            # Generate embeddings in parallel
            embeddings = await asyncio.gather(*[
                self.embedding_service.create_embedding(doc['content'])
                for doc in documents
            ])

            # Prepare documents with embeddings
            docs_with_embeddings = [
                {
                    "title": doc["title"],
                    "content": doc["content"],
                    "client_id": str(client_id),
                    "embedding": embedding,
                    "metadata": doc.get("metadata", {})
                }
                for doc, embedding in zip(documents, embeddings)
            ]

            # Bulk insert documents
            response = await self.supabase.client.table('documents')\
                .insert(docs_with_embeddings)\
                .execute()

            return response.data

        except Exception as e:
            logger.error(f"Error processing batch: {str(e)}")
            raise

    async def process_csv(self, file: bytes, client_id: UUID) -> Dict:
        """Process CSV file upload"""
        try:
            # Convert bytes to file-like object
            file_obj = io.BytesIO(file)
            
            # Read CSV file
            df = pd.read_csv(file_obj)
            required_columns = ['title', 'content']
            
            # Validate columns
            if not all(col in df.columns for col in required_columns):
                raise ValueError(f"CSV must contain columns: {required_columns}")
            
            # Process documents
            total = len(df)
            processed = 0
            failed = 0
            errors = []

            for _, row in df.iterrows():
                try:
                    # Handle metadata - convert string to dict if present
                    metadata = {}
                    if 'metadata' in row and pd.notna(row['metadata']):
                        try:
                            metadata = json.loads(row['metadata'])
                        except json.JSONDecodeError:
                            metadata = {'raw': row['metadata']}
                    
                    await self.rag_service.process_document(
                        title=str(row['title']),
                        content=str(row['content']),
                        client_id=client_id,
                        metadata=metadata
                    )
                    processed += 1
                except Exception as e:
                    failed += 1
                    errors.append(f"Error processing row {_}: {str(e)}")
                    logger.error(f"Error processing document: {str(e)}")

            return {
                "status": "completed",
                "total_documents": total,
                "processed_documents": processed,
                "failed_documents": failed,
                "errors": errors
            }
        except Exception as e:
            logger.error(f"Error processing CSV: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))

    async def process_json(self, documents: List[Dict], client_id: UUID) -> Dict:
        """Process JSON documents upload"""
        try:
            total = len(documents)
            processed = 0
            failed = 0
            errors = []

            for doc in documents:
                try:
                    await self.rag_service.process_document(
                        title=doc['title'],
                        content=doc['content'],
                        client_id=client_id,
                        metadata=doc.get('metadata', {})
                    )
                    processed += 1
                except Exception as e:
                    failed += 1
                    errors.append(f"Error processing document: {str(e)}")
                    logger.error(f"Error processing document: {str(e)}")

            return {
                "status": "completed",
                "total_documents": total,
                "processed_documents": processed,
                "failed_documents": failed,
                "errors": errors
            }
        except Exception as e:
            logger.error(f"Error processing JSON documents: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))