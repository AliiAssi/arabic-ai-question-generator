# app/services/pdf_service.py
import logging
from typing import Optional, Dict, Any
from google import genai
from google.genai import types
from app.clients.ai_client import AIClient

logger = logging.getLogger(__name__)

class PDFService:
    """Service to extract text from PDF files using Gemini"""
    
    def __init__(self, ai_client: AIClient):
        self.ai_client = ai_client
        self.max_file_size = 50 * 1024 * 1024  # 50MB limit
    
    def validate_pdf(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """Validate PDF file"""
        validation_result = {
            'valid': True,
            'error': None,
            'file_size': len(file_data),
            'filename': filename
        }
        
        # Check file size
        if len(file_data) > self.max_file_size:
            validation_result['valid'] = False
            validation_result['error'] = f"حجم الملف كبير جداً. الحد الأقصى {self.max_file_size // (1024*1024)} ميجابايت"
            return validation_result
        
        # Check if it's actually a PDF
        if not file_data.startswith(b'%PDF'):
            validation_result['valid'] = False
            validation_result['error'] = "الملف ليس PDF صالح"
            return validation_result
        
        # Check filename extension
        if not filename.lower().endswith('.pdf'):
            validation_result['valid'] = False
            validation_result['error'] = "يجب أن يكون الملف بصيغة PDF"
            return validation_result
        
        return validation_result
    
    def extract_text_from_pdf(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """Extract text from PDF using Gemini"""
        try:
            # Validate PDF first
            validation = self.validate_pdf(file_data, filename)
            if not validation['valid']:
                return {
                    'success': False,
                    'error': validation['error'],
                    'text': None
                }
            
            logger.info(f"Extracting text from PDF: {filename} ({len(file_data)} bytes)")
            
            # Use Gemini to extract text from PDF
            client = genai.Client(api_key=self.ai_client.config.api_key)
            
            # Create prompt for text extraction
            extraction_prompt = """استخرج النص من هذا المستند PDF بدقة. 
اكتب النص المستخرج بوضوح ودون إضافة أي تعليقات أو مقدمات.
إذا كان النص باللغة العربية، تأكد من الحفاظ على التنسيق الصحيح."""
            
            # Send PDF to Gemini for text extraction
            contents = [
                types.Part.from_bytes(
                    data=file_data,
                    mime_type='application/pdf'
                ),
                extraction_prompt
            ]
            
            response = client.models.generate_content(
                model=self.ai_client.config.model_name,
                contents=contents
            )
            
            extracted_text = response.text.strip()
            
            if not extracted_text:
                return {
                    'success': False,
                    'error': 'لم يتم العثور على نص قابل للاستخراج في هذا PDF',
                    'text': None
                }
            
            logger.info(f"Successfully extracted {len(extracted_text)} characters from {filename}")
            
            return {
                'success': True,
                'error': None,
                'text': extracted_text,
                'metadata': {
                    'filename': filename,
                    'file_size': len(file_data),
                    'extracted_length': len(extracted_text)
                }
            }
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF {filename}: {e}")
            return {
                'success': False,
                'error': f'خطأ في استخراج النص من PDF: {str(e)}',
                'text': None
            }