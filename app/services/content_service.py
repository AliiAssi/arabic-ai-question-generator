import logging
import threading
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Optional, Callable
from app.core.models import ContentRequest, ContentResponse, ContentType, Language
from app.core.exceptions import ContentGenerationError, ValidationError
from app.clients.ai_client import AIClient
from app.prompts.arabic.questions import ArabicQuestionPrompts
from app.config.settings import AppConfig

logger = logging.getLogger(__name__)


class ContentService:
    """Multi-threaded content generation service"""
    
    def __init__(self, ai_client: AIClient, config: AppConfig):
        self.ai_client = ai_client
        self.config = config
        self.executor = ThreadPoolExecutor(max_workers=config.max_workers)
        self._lock = threading.Lock()
    
    def generate_content_async(
        self, 
        request: ContentRequest, 
        callback: Optional[Callable[[ContentResponse], None]] = None
    ) -> Future[ContentResponse]:
        """Generate content asynchronously"""
        def _generate():
            try:
                response = self._generate_content_sync(request)
                if callback:
                    callback(response)
                return response
            except Exception as e:
                logger.error(f"Async content generation failed: {e}")
                error_response = ContentResponse(
                    content="",
                    request=request,
                    metadata={},
                    success=False,
                    error_message=str(e)
                )
                if callback:
                    callback(error_response)
                return error_response
        
        return self.executor.submit(_generate)
    
    def generate_content_sync(self, request: ContentRequest) -> ContentResponse:
        """Generate content synchronously"""
        return self._generate_content_sync(request)
    
    def _generate_content_sync(self, request: ContentRequest) -> ContentResponse:
        """Internal synchronous content generation"""
        try:
            # Validate request
            request.validate()
            
            # Build prompt based on content type and language
            prompt = self._build_prompt(request)
            
            # Generate content using AI client
            logger.info(f"Generating {request.content_type.value} content")
            
            with self._lock:  # Thread-safe AI client usage
                content = self.ai_client.generate_content(prompt)
            
            # Create response
            return ContentResponse(
                content=content,
                request=request,
                metadata={
                    "prompt_length": len(prompt),
                    "response_length": len(content),
                    "thread_id": threading.current_thread().ident
                }
            )
            
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            return ContentResponse(
                content="",
                request=request,
                metadata={},
                success=False,
                error_message=f"خطأ في التحقق: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Content generation failed: {e}")
            return ContentResponse(
                content="",
                request=request,
                metadata={},
                success=False,
                error_message=f"خطأ في توليد المحتوى: {str(e)}"
            )
    
    def _build_prompt(self, request: ContentRequest) -> str:
        """Build prompt based on content type and language"""
        if request.content_type == ContentType.QUESTIONS and request.language == Language.ARABIC:
            return ArabicQuestionPrompts.generate_comprehensive_questions(request)
        else:
            raise ContentGenerationError(f"Unsupported content type: {request.content_type.value} in {request.language.value}")
    
    def create_questions(
        self, 
        text: str, 
        language: Language = Language.ARABIC,
        async_mode: bool = False,
        callback: Optional[Callable[[ContentResponse], None]] = None
    ):
        """Create questions from text"""
        request = ContentRequest(
            source_text=text,
            content_type=ContentType.QUESTIONS,
            language=language
        )
        
        if async_mode:
            return self.generate_content_async(request, callback)
        else:
            return self.generate_content_sync(request)
    
    def shutdown(self):
        """Shutdown the thread pool executor"""
        self.executor.shutdown(wait=True)
        logger.info("Content service shut down")