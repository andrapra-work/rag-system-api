from openai import AsyncOpenAI
from app.config import get_settings, ModelSettings
import logging
from typing import List, Dict

settings = get_settings()
logger = logging.getLogger(__name__)

class CompletionService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.DEFAULT_COMPLETION_MODEL

    async def generate_response(self, query: str, context: List[Dict]) -> str:
        try:
            # Create a more focused system message
            system_message = """You are an AI assistant that provides accurate answers based on the given context.
            Your task is to analyze the provided documents and generate a comprehensive answer.
            Rules:
            1. Only use information present in the provided documents
            2. If the documents contain relevant information, synthesize it into a clear answer
            3. If the documents discuss related topics but don't directly answer the question, 
               explain what relevant information is available
            4. Be specific and cite information from the documents
            5. If the documents are completely unrelated to the question, say 
               "I don't have enough information to answer that question."
            """

            # Create a better structured prompt
            user_prompt = self._create_prompt(query, context)

            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt}
            ]

            logger.info(f"Sending request to OpenAI with {len(context)} documents")
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.5,  # Lower temperature for more focused answers
                max_tokens=500,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            answer = response.choices[0].message.content
            logger.info(f"Generated response: {answer}")
            return answer

        except Exception as e:
            logger.error(f"Error generating completion: {str(e)}")
            raise

    def _create_prompt(self, query: str, context: List[Dict]) -> str:
        # Format each document with its metadata
        formatted_docs = []
        for i, doc in enumerate(context, 1):
            doc_text = f"""Document {i}:
Title: {doc['title']}
Content: {doc['content']}
Relevance: This document has a similarity score of {doc.get('similarity', 'N/A')}
---"""
            formatted_docs.append(doc_text)

        # Join all documents
        context_str = "\n".join(formatted_docs)

        # Create the prompt
        prompt = f"""Please analyze these documents and answer the question.

Context Documents:
{context_str}

Question: {query}

Instructions:
1. Use only information from the provided documents
2. If the documents contain relevant information, provide a detailed answer
3. If the information is partially relevant, explain what information is available
4. Cite specific details from the documents when possible
5. If the documents don't contain relevant information, say "I don't have enough information to answer that question."

Answer:"""

        logger.info(f"Created prompt with {len(context)} documents")
        return prompt