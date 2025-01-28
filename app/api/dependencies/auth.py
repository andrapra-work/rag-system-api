from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.config import get_settings
from app.services.supabase import SupabaseService
from typing import Optional
from pydantic import BaseModel

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

class TokenData(BaseModel):
    email: Optional[str] = None
    client_id: Optional[str] = None

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    supabase: SupabaseService = Depends()
) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email, client_id=payload.get("client_id"))
    except JWTError:
        raise credentials_exception
    
    user = supabase.get_user_by_email(email=token_data.email)
    if user is None:
        raise credentials_exception
        
    return user