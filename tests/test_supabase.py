import pytest
from app.services.supabase import SupabaseService
from uuid import uuid4

@pytest.fixture
def supabase_service():
    return SupabaseService()

async def test_create_and_search_document(supabase_service):
    # Test data
    client_id = uuid4()
    document = {
        "title": "Test Document",
        "content": "This is a test document",
        "embedding": [0.1] * 1536  # Mock embedding
    }
    
    # Create document
    created_doc = await supabase_service.create_document(
        title=document["title"],
        content=document["content"],
        client_id=client_id,
        embedding=document["embedding"]
    )
    
    assert created_doc["title"] == document["title"]
    
    # Search documents
    results = await supabase_service.search_documents(
        embedding=document["embedding"],
        client_id=client_id
    )
    
    assert len(results) > 0