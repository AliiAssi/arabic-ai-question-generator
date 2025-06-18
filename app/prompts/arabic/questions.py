from app.core.models import ContentRequest
from app.prompts.arabic.utils.advanced_prompt import generate_prompt
class ArabicQuestionPrompts:
    @staticmethod
    def generate_mcq_questions(request: ContentRequest) -> str:
        """Generate a prompt for creating multiple-choice questions in Arabic."""
        prompt = f"""أنت مولد أسئلة اختيار من متعدد عربي متخصص. اقرأ النص التالي وأنشئ أسئلة اختيار من متعدد.

النص:
"{request.source_text}"

التعليمات:
- أنشئ أسئلة اختيار من متعدد شاملة
- كل سؤال يجب أن يحتوي على 3 خيارات فقط
- خيار واحد صحيح واثنان خاطئان
- اجعل الخيارات الخاطئة معقولة لكن خاطئة
- غطِ جميع المفاهيم والحقائق المهمة
- تجنب التكرار

⚠️ مهم جداً: يجب أن تكون الإجابة بتنسيق JSON فقط، بدون أي نص إضافي أو تفسيرات. ابدأ مباشرة بـ {{ وانته بـ }}

يجب أن تكون الإجابة بتنسيق JSON فقط، بدون أي نص إضافي:

{{
  "questions": [
    {{
      "question": "نص السؤال هنا؟",
      "options": ["الخيار الأول", "الخيار الثاني", "الخيار الثالث"],
      "correct_answer": 0
    }}
  ]
}}"""
        if request.additional_instructions:
            prompt += f"\n\nمتطلبات إضافية: {request.additional_instructions}"
            
        return prompt
    
    @staticmethod
    def generate_questions(request: ContentRequest) -> str:
        """Generate a prompt for creating questions in Arabic."""
        source_text = request.source_text.strip()
        num_mcq_questions = request.advanced_options.get('number_of_qcm_questions', 0)
        num_comprehension_questions = request.advanced_options.get('number_of_comprehension_questions', 0)
        
        return generate_prompt(source_text= source_text, num_comprehension_questions=num_comprehension_questions, num_mcq_questions=num_mcq_questions)

    