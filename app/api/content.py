from flask import Blueprint, request, jsonify
import logging
from app.core.models import ContentRequest, ContentType, Language
from app.services.user_tracker import user_tracker, track_concurrent_users

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
                'questions': response.content,
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
    
# @content_api.route('/generate/test', methods=['POST'])
# @track_concurrent_users
# def generate_test():
#     """Test API endpoint that bypasses Gemini - returns mock responses"""
#     try:
#         # Check if it's a file upload (multipart) or JSON request
#         if request.content_type and 'multipart/form-data' in request.content_type:
#             # Handle PDF upload
#             if 'pdf_file' not in request.files:
#                 return jsonify({
#                     'success': False,
#                     'error': 'لم يتم إرفاق ملف PDF'
#                 }), 400
            
#             pdf_file = request.files['pdf_file']
#             if pdf_file.filename == '':
#                 return jsonify({
#                     'success': False,
#                     'error': 'لم يتم اختيار ملف'
#                 }), 400
            
#             # Mock PDF processing
#             text = "هذا نص تجريبي مستخرج من ملف PDF للاختبار"
#             source_type = 'pdf'
#             source_info = {
#                 'filename': pdf_file.filename,
#                 'file_size': len(pdf_file.read()),
#                 'extracted_length': len(text)
#             }
            
#         else:
#             # Handle JSON text input
#             data = request.get_json()
#             text = data.get('text', '').strip()
#             source_type = 'text'
#             source_info = {}
            
#             if not text:
#                 return jsonify({
#                     'success': False,
#                     'error': 'لم يتم إدخال أي نص'
#                 }), 400
        
#         # Mock question generation based on text length
#         if len(text) < 1:
#             return jsonify({
#                 'success': False,
#                 'error': 'there is a problem - النص قصير جداً للمعالجة'
#             }), 400
        
#         # Generate mock questions
#         mock_questions = f"""أسئلة تجريبية مولدة من النص:

# ما هو الموضوع الرئيسي للنص؟

# كيف يمكن تطبيق المفاهيم المذكورة عملياً؟

# ما هي الفوائد المتوقعة من هذا الموضوع؟

# [تم إنشاؤها بواسطة API التجريبي - طول النص: {len(text)} حرف]"""
        
#         return jsonify({
#             'success': True,
#             'questions': mock_questions,
#             'original_text': text,
#             'metadata': {
#                 'source_type': source_type,
#                 'source_info': source_info,
#                 'api_mode': 'test',
#                 'text_length': len(text),
#                 'response_message': 'well received'
#             },
#             'concurrent_users': user_tracker.get_concurrent_users_count()
#         })
        
#     except Exception as e:
#         logging.error(f"Test API error: {e}")
#         return jsonify({
#             'success': False,
#             'error': f'there is a problem - {str(e)}'
#         }), 500