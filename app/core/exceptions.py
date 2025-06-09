class AIContentError(Exception):
    """Base exception for AI content generation errors"""
    pass

class APIConnectionError(AIContentError):
    """Raised when API connection fails"""
    pass

class ContentGenerationError(AIContentError):
    """Raised when content generation fails"""
    pass

class ValidationError(AIContentError):
    """Raised when input validation fails"""
    pass