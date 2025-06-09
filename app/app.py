import sys
import os

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import logging
import atexit

from app.config.settings import load_config
from app.clients.ai_client import AIClient
from app.core.models import ContentRequest, ContentType, Language
from app.services.content_service import ContentService
from app.services.user_tracker import user_tracker, track_concurrent_users
from app.services.pdf_service import PDFService

def create_app():
    """Application factory pattern with proper folder structure"""
    # Set template and static paths relative to project root
    template_path = os.path.join(".", 'frontend', 'templates')
    static_path = os.path.join(".", 'frontend', 'static')
    
    app = Flask(__name__, 
        template_folder=template_path,
        static_folder=static_path
    )
    CORS(app)
    
    # Set secret key for sessions
    app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')
    
    # Load configuration
    config = load_config()
    app.config.from_object(config)
    
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, config.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize services
    ai_client = AIClient(config.ai_config)
    content_service = ContentService(ai_client, config)
    pdf_service = PDFService(ai_client)
    
    # Cleanup on app shutdown
    atexit.register(content_service.shutdown)
    
    @app.route('/')
    @track_concurrent_users
    def index():
        """Render the main page"""
        return render_template('index.html')
    
    @app.route('/generate', methods=['POST'])
    @track_concurrent_users
    def generate():
        """Generate questions from submitted text or PDF - supports both sync and async"""
        try:
            # Check if it's a file upload (multipart) or JSON request
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
            async_mode = request.form.get('async', 'false').lower() == 'true' if source_type == 'pdf' else request.get_json().get('async', False)
            
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
    
    @app.route('/health', methods=['GET'])
    @track_concurrent_users
    def health():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'service': 'ai-content-generator',
            'max_workers': config.max_workers,
            'concurrent_users': user_tracker.get_concurrent_users_count()
        })
    
    @app.route('/stats', methods=['GET'])
    @track_concurrent_users
    def stats():
        """Get detailed user statistics"""
        stats = user_tracker.get_detailed_stats()
        return jsonify(stats)
    
    @app.route('/admin/users', methods=['GET'])
    @track_concurrent_users
    def admin_users():
        """Admin endpoint to view current active users"""
        # In production, add authentication here
        stats = user_tracker.get_detailed_stats()
        return jsonify({
            'current_stats': stats,
            'message': 'Active users monitoring'
        })

    @app.route('/admin/dashboard')
    @track_concurrent_users
    def admin_dashboard():
        """Admin dashboard to view concurrent users"""
        # In production, add authentication here
        return render_template('admin_dashboard.html')
    
    return app