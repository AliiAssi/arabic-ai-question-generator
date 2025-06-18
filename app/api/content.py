from flask import Blueprint, request, jsonify
import logging
from app.core.models import ContentRequest, ContentType, Language
from app.services.user_tracker import user_tracker, track_concurrent_users
from app.validators.text_validator import text_validate
from app.validators.pdf_validator import pdf_validate, pdf_extraction_validate
from app.helpers.parameter_extraction import extract_parameters, create_content_request

content_api = Blueprint('content_api', __name__)

# will be injected from app:
content_service = None
pdf_service = None
config = None

# Initialize the content API with required services
def init_content_api(content_svc, pdf_svc, app_config):
    """Initialize the API with required services"""
    global content_service, pdf_service, config
    content_service = content_svc
    pdf_service = pdf_svc
    config = app_config

@content_api.route('/generate', methods=['POST'])
@track_concurrent_users
def generate():
    """Generate questions from submitted text or PDF - supports both sync and async"""
    try:
        if request.content_type and 'multipart/form-data' in request.content_type:
            # Handle PDF upload
            if 'pdf_file' not in request.files:
                return jsonify({
                    'success': False,
                    'error': 'لم يتم إرفاق ملف PDF'
                }), 400
            
            pdf_file = request.files['pdf_file']
            if pdf_file.filename == '':
                return jsonify({
                    'success': False,
                    'error': 'لم يتم اختيار ملف'
                }), 400
            
            # Extract text from PDF
            file_data = pdf_file.read()
            extraction_result = pdf_service.extract_text_from_pdf(file_data, pdf_file.filename)
            
            if not extraction_result['success']:
                return jsonify({
                    'success': False,
                    'error': extraction_result['error']
                }), 400
            
            text = extraction_result['text']
            source_type = 'pdf'
            source_info = extraction_result['metadata']

        else:
            # Handle JSON text input (existing functionality)
            data = request.get_json()
            text = data.get('text', '').strip()
            source_type = 'text'
            source_info = {}
            
            if not text:
                return jsonify({
                    'success': False,
                    'error': 'لم يتم إدخال أي نص'
                }), 400
        
        # Get async mode (works for both text and PDF)
        # async_mode = request.form.get('async', 'false').lower() == 'true' if source_type == 'pdf' else request.get_json().get('async', False)
        async_mode = False
        
        # Create content request (same logic for both text and PDF)
        content_request = ContentRequest(
            source_text=text,
            content_type=ContentType.QUESTIONS,
            language=Language.ARABIC
        )
        
        if async_mode:
            # Async processing
            future = content_service.generate_content_async(content_request)
            response = future.result(timeout=config.request_timeout)
        else:
            # Synchronous processing
            response = content_service.generate_content_sync(content_request)
        
        if response.success:
            # Add source information to metadata
            response.metadata['source_type'] = source_type
            response.metadata['source_info'] = source_info
            
            return jsonify({
                'success': True,
                'LLM': response.content,
                'original_text': text,
                'metadata': response.metadata,
                'concurrent_users': user_tracker.get_concurrent_users_count()
            })
        else:
            return jsonify({
                'success': False,
                'error': response.error_message
            }), 500
            
    except Exception as e:
        logging.error(f"API error: {e}")
        return jsonify({
            'success': False,
            'error': f'حدث خطأ في الخادم: {str(e)}'
        }), 500

@content_api.route('/advanced-generate', methods=['POST'])
@track_concurrent_users
def advanced_generate():
    """Generate questions from submitted text or PDF"""
    try:
        source_info = {}
        
        # Handle different input types using existing validators
        if request.content_type and 'multipart/form-data' in request.content_type:
            # PDF upload path
            existing_pdf, error_message = pdf_validate(request)
            if not existing_pdf:
                return jsonify({'success': False, 'error': error_message}), 400
            
            # Extract text from PDF
            file_data = existing_pdf.read()
            extraction_result = pdf_service.extract_text_from_pdf(file_data, existing_pdf.filename)

            
            pdf_text_validation, message = pdf_extraction_validate(extraction_result)
            if not pdf_text_validation:
                return jsonify({'success': False, 'error': message}), 400
            
            text = message.strip()
            source_type = 'pdf'
            source_info = extraction_result['metadata']
            
        else:
            # JSON text input path
            text_validation, text = text_validate(request)
            if not text_validation:
                return jsonify({'success': False, 'error': text}), 400
            source_type = 'text'
        print(f"Source type: {source_type}, Text length: {len(text)}")
        # Extract parameters using helper
        success, params = extract_parameters(request, source_type)
        if not success:
            return jsonify({'success': False, 'error': params['error']}), 400
        
        # Create content request
        content_request, async_mode = create_content_request(text, params)
        
        # Validate content request (using existing validator)
        try:
            content_request.validate()
        except ValueError as e:
            return jsonify({'success': False, 'error': str(e)}), 400
    
        # Process request
        if async_mode:
            future = content_service.generate_content_async(content_request)
            response = future.result(timeout=config.request_timeout)
        else:
            response = content_service.generate_content_sync(content_request)
        
        # Return response
        if response.success:
            response.metadata['source_type'] = source_type
            response.metadata['source_info'] = source_info
            
            return jsonify({
                'success': True,
                'LLM': response.content,
                'original_text': text,
                'metadata': response.metadata,
                'concurrent_users': user_tracker.get_concurrent_users_count()
            })
        else:
            return jsonify({'success': False, 'error': response.error_message}), 500
            
    except Exception as e:
        logging.error(f"API error: {e}")
        return jsonify({'success': False, 'error': f'حدث خطأ في الخادم: {str(e)}'}), 500
