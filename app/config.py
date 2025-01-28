from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List

class Settings(BaseSettings):
    # API Configuration
    API_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"

    # OpenAI
    OPENAI_API_KEY: str
    
    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_KEY: str
    
    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS Settings
    CORS_ORIGINS: List[str] = ["*"]
    
    # Upload Settings
    MAX_UPLOAD_SIZE: int = 10_000_000  # 10MB
    ALLOWED_EXTENSIONS: List[str] = ["csv", "json"]
    BATCH_SIZE: int = 5
    # Model Settings
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    COMPLETION_MODEL: str = "gpt-4o-mini"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()