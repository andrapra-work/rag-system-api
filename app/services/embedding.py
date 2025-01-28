from openai import AsyncOpenAI
from app.config import get_settings
import logging

settings = get_settings()
logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "text-embedding-3-small"

    async def create_embedding(self, text: str) -> list[float]:
        try:
            response = await self.client.embeddings.create(
                model=self.model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error creating embedding: {str(e)}")
            raise