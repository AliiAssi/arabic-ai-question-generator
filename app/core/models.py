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
    advanced_options: Optional[Dict[str, Any]] = None

    def set_advanced_options(self, options: Dict[str, Any]) -> None:
        """Set advanced options for content generation"""
        self.advanced_options = options
    
    def validate(self) -> None:
        """Validate the request parameters"""
        if not self.source_text.strip():
            raise ValueError("Source text cannot be empty")
        if self.count <= 0:
            raise ValueError("Count must be positive")
    
    def serialize(self) -> Dict[str, Any]:
        """Serialize the request to a dictionary"""
        return {
            "source_text": self.source_text,
            "content_type": self.content_type.value,
            "language": self.language.value,
            "count": self.count,
            "additional_instructions": self.additional_instructions,
            "advanced_options": self.advanced_options
        }

@dataclass
class ContentResponse:
    """Response model for generated content"""
    content: str
    request: ContentRequest
    metadata: Dict[str, Any]
    success: bool = True
    error_message: Optional[str] = None