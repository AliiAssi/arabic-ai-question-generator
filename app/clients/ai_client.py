import logging
from typing import Generator
from google import genai
from google.genai import types
from app.core.exceptions import APIConnectionError, ContentGenerationError
from app.config.settings import AIConfig
from app.config.advanced_response_schema import get_response_schema
from app.core.models import ContentRequest
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
    
    def generate_content(self, prompt: str, advanced_request:ContentRequest = None) -> str:
        """Generate content and return complete response"""
        try:
            contents = self.config.__content_config__(prompt)
            if advanced_request is None:
                config = self.config.__generation_config__()
            else:
                num_mcq_questions = advanced_request.advanced_options.get('number_of_qcm_questions', 0)
                num_comprehension_questions = advanced_request.advanced_options.get('number_of_comprehension_questions', 0) 
                config = self.config.__generation_config__(get_response_schema(
                        num_mcq_questions=num_mcq_questions, 
                        num_comprehension_questions=num_comprehension_questions
                ))         
            response = self._client.models.generate_content(
                model=self.config.model_name,
                contents=contents,
                config=config
            )
            return response.parsed # Since response is a structured object - JSON-like #.parsed may be empty/null.
        except Exception as e:
            raise ContentGenerationError(f"Failed to generate complete content: {e}")