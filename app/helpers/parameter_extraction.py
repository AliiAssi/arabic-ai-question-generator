from typing import Dict, Any, Tuple
from flask import Request


def extract_parameters(request: Request, source_type: str) -> Tuple[bool, Dict[str, Any]]:
    """
    Extract parameters from request based on source type.
    
    Args:
        request: Flask request object
        source_type: 'pdf' or 'text'
    
    Returns:
        Tuple of (success: bool, parameters: dict)
        If success is False, parameters dict contains 'error' key with message
    """
    try:
        if source_type == 'pdf':
            return _extract_from_form(request)
        else:
            return _extract_from_json(request)
    except Exception as e:
        return False, {'error': f"Parameter extraction failed: {str(e)}"}


def _extract_from_form(request: Request) -> Tuple[bool, Dict[str, Any]]:
    """Extract parameters from form data (PDF uploads)"""
    try:
        params = {
            'difficulty': request.form.get('difficulty', 'medium'),
            'objective': request.form.get('objective', ''),
            'with_comprehension_questions': request.form.get('with_comprehension_questions', 'false').lower() == 'true',
            'number_of_comprehension_questions': int(request.form.get('number_of_comprehension_questions', '1')),
            'number_of_qcm_questions': int(request.form.get('number_of_qcm_questions', '2')),
            'with_grades': request.form.get('with_grades', 'false').lower() == 'true',
            'total_grades': int(request.form.get('total_grades', '100')),
            'async_mode': request.form.get('async', 'false').lower() == 'true'
        }
        return True, params
        
    except ValueError as e:
        return False, {'error': f'Invalid form parameter: {str(e)}'}


def _extract_from_json(request: Request) -> Tuple[bool, Dict[str, Any]]:
    """Extract parameters from JSON data (text input)"""
    try:
        json_data = request.get_json() or {}
        
        params = {
            'difficulty': json_data.get('difficulty', 'medium'),
            'objective': json_data.get('objective', ''),
            'with_comprehension_questions': bool(json_data.get('with_comprehension_questions', False)),
            'number_of_comprehension_questions': int(json_data.get('number_of_comprehension_questions', 1)),
            'number_of_qcm_questions': int(json_data.get('number_of_qcm_questions', 2)),
            'with_grades': bool(json_data.get('with_grades', False)),
            'total_grades': int(json_data.get('total_grades', 100)),
            'async_mode': bool(json_data.get('async', False))
        }
        return True, params
        
    except (ValueError, TypeError) as e:
        return False, {'error': f'Invalid JSON parameter: {str(e)}'}


def create_content_request(text: str, params: Dict[str, Any]):
    """
    Create ContentRequest with parameters.
    
    Returns:
        Tuple of (ContentRequest, async_mode)
    """
    from app.core.models import ContentRequest, ContentType, Language
    
    # Extract async_mode
    async_mode = params.pop('async_mode', False)
    
    # Create request
    content_request = ContentRequest(
        source_text=text,
        content_type=ContentType.QUESTIONS,
        language=Language.ARABIC
    )
    
    # Set options
    content_request.set_advanced_options(params)
    
    return content_request, async_mode