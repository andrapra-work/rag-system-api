from pydantic import BaseModel, UUID4
from typing import Optional, Dict
from datetime import datetime

class DocumentBase(BaseModel):
    title: str
    content: str
    metadata: Optional[Dict] = None

class DocumentCreate(DocumentBase):
    client_id: UUID4

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    metadata: Optional[Dict] = None

class DocumentResponse(DocumentBase):
    id: UUID4
    client_id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 