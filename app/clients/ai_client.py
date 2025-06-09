import logging
from typing import Generator
from google import genai
from google.genai import types
from app.core.exceptions import APIConnectionError, ContentGenerationError
from app.config.settings import AIConfig

logger = logging.getLogger(__name__)

class AIClient:
    """Wrapper for Google GenAI client with error handling and retry logic"""
    
    def __init__(self, config: AIConfig):
        self.config = config
        self._client = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize the GenAI client"""
        try:
            self._client = genai.Client(api_key=self.config.api_key)
            logger.info("AI client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AI client: {e}")
            raise APIConnectionError(f"Failed to initialize AI client: {e}")
    
    def generate_content_stream(self, prompt: str) -> Generator[str, None, None]:
        """Generate content using streaming API"""
        if not self._client:
            raise APIConnectionError("AI client not initialized")
        
        try:
            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=prompt)]
                )
            ]
            
            config = types.GenerateContentConfig(
                response_mime_type=self.config.response_mime_type
            )
            
            for chunk in self._client.models.generate_content_stream(
                model=self.config.model_name,
                contents=contents,
                config=config
            ):
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            logger.error(f"Content generation failed: {e}")
            raise ContentGenerationError(f"Failed to generate content: {e}")
    
    def generate_content(self, prompt: str) -> str:
        """Generate content and return complete response"""
        content_parts = []
        try:
            for chunk in self.generate_content_stream(prompt):
                content_parts.append(chunk)
            return "".join(content_parts)
        except Exception as e:
            raise ContentGenerationError(f"Failed to generate complete content: {e}")