from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    client_id: Optional[UUID] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    client_id: UUID