from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List
from enum import Enum

class ModelSettings(Enum):
    # Embedding Models
    EMBEDDING_MODEL = "text-embedding-3-small"
    EMBEDDING_DIMENSIONS = 1536
    
    # Completion Models
    GPT_4_MINI = "gpt-4o-mini"
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    GPT_4 = "gpt-4"

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

    # Model Configuration
    DEFAULT_EMBEDDING_MODEL: str = ModelSettings.EMBEDDING_MODEL.value
    DEFAULT_COMPLETION_MODEL: str = ModelSettings.GPT_4_MINI.value
    EMBEDDING_DIMENSIONS: int = ModelSettings.EMBEDDING_DIMENSIONS.value
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()