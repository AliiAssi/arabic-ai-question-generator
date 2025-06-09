from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum

class ContentType(Enum):
    """Types of content that can be generated"""
    QUESTIONS = "questions"
    SUMMARY = "summary"
    EXPLANATION = "explanation"
    QUIZ = "quiz"

class Language(Enum):
    """Supported languages"""
    ARABIC = "ar"
    ENGLISH = "en"

@dataclass
class ContentRequest:
    """Request model for content generation"""
    source_text: str
    content_type: ContentType = ContentType.QUESTIONS
    language: Language = Language.ARABIC
    count: int = 3
    additional_instructions: Optional[str] = None
    
    def validate(self) -> None:
        """Validate the request parameters"""
        if not self.source_text.strip():
            raise ValueError("Source text cannot be empty")
        if self.count <= 0:
            raise ValueError("Count must be positive")

@dataclass
class ContentResponse:
    """Response model for generated content"""
    content: str
    request: ContentRequest
    metadata: Dict[str, Any]
    success: bool = True
    error_message: Optional[str] = None