from app.core.models import ContentRequest

class ArabicQuestionPrompts:
    """Arabic question generation prompts"""
    
    @staticmethod
    def generate_comprehensive_questions(request: ContentRequest) -> str:
        """Generate comprehensive questions prompt with direct output forcing"""
        prompt = f"""أنت مولد أسئلة عربي متخصص. مهمتك هي قراءة النص التالي وإنتاج قائمة أسئلة مباشرة فقط، بدون أي تعليقات أو مقدمات أو خاتمة.

النص:
"{request.source_text}"

التعليمات:
- أنشئ جميع الأسئلة المنطقية الممكنة من النص
- تجنب التكرار تماماً
- كل سؤال يجب أن يركز على جانب مختلف
- اكتب الأسئلة مباشرة بدون ترقيم أو رموز
- لا تكتب أي مقدمة أو تعليق
- لا تكتب "إليك الأسئلة" أو "الأسئلة هي"
- ابدأ مباشرة بالسؤال الأول

اكتب الأسئلة التي تغطي:
- الحقائق الأساسية والمعلومات المباشرة
- المفاهيم والأفكار الرئيسية
- التفاصيل والعناصر المهمة
- العلاقات والروابط بين الأجزاء
- الأسباب والنتائج والتأثيرات

ابدأ الآن بكتابة الأسئلة مباشرة:"""
        
        if request.additional_instructions:
            prompt += f"\n\nمتطلبات إضافية: {request.additional_instructions}"
        
        return prompt