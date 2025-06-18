import sys
import os
from flask import Flask
from flask_cors import CORS
import logging
import atexit

from app.config.settings import load_config
from app.clients.ai_client import AIClient
from app.services.content_service import ContentService
from app.services.pdf_service import PDFService

# Import blueprints
from app.routes import main_bp, dashboard_bp
from app.api import content_api, init_content_api, system_api, init_system_api

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
    app.secret_key = os.environ.get('SECRET_KEY', 'SECRET')
    
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
    
    # Initialize API modules with services
    init_content_api(content_service, pdf_service, config)
    init_system_api(config)
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(content_api)
    app.register_blueprint(system_api)
    
    # Cleanup when app is shutdown
    atexit.register(content_service.shutdown)
    
    return app