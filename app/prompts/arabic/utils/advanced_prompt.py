def generate_prompt(source_text, num_mcq_questions=None, num_comprehension_questions=None):
    """Generate the prompt for question generation"""
    prompt = f"""أنت مولد أسئلة اختيار من متعدد عربي متخصص. اقرأ النص التالي وأنشئ أسئلة اختيار من متعدد.

النص: "{source_text}"

التعليمات:
- أنشئ أسئلة اختيار من متعدد شاملة
- كل سؤال يجب أن يحتوي على 3 خيارات فقط
- خيار واحد صحيح واثنان خاطئان
- اجعل الخيارات الخاطئة معقولة لكن خاطئة
- غطِ جميع المفاهيم والحقائق المهمة
- تجنب التكرار"""
    
    # Handle different scenarios
    if num_mcq_questions <= 0 and num_comprehension_questions <= 0:
        # Let LLM decide both
        prompt += "\n- حدد العدد المناسب من أسئلة الاختيار من متعدد وأسئلة الفهم بناءً على النص ومحتواه"
    elif num_mcq_questions is not None and num_comprehension_questions is None:
        # Only MCQ specified
        prompt += f"\n- أنشئ {num_mcq_questions} أسئlة اختيار من متعدد فقط"
    elif num_mcq_questions is None and num_comprehension_questions is not None:
        # Only comprehension specified
        prompt += f"\n- أنشئ {num_comprehension_questions} أسئلة فهم فقط"
    else:
        # Both specified
        prompt += f"\n- أنشئ {num_mcq_questions} أسئلة اختيار من متعدد"
        prompt += f"\n- أنشئ {num_comprehension_questions} أسئلة فهم إضافية"
    
    prompt += """

⚠️ مهم جداً: يجب أن تكون الإجابة بتنسيق JSON فقط، بدون أي نص إضافي أو تفسيرات. ابدأ مباشرة بـ { وانته بـ }

يجب أن تكون الإجابة بتنسيق JSON فقط، بدون أي نص إضافي:

{"""
    
    # Add questions array if MCQ is needed
    if num_mcq_questions is not None or (num_mcq_questions is None and num_comprehension_questions is None):
        prompt += """
  "questions": [
    {
      "question": "نص السؤال هنا؟",
      "options": ["الخيار الأول", "الخيار الثاني", "الخيار الثالث"],
      "correct_answer": 0
    }
  ]"""
    
    # Add comprehension questions if needed
    if num_comprehension_questions is not None or (num_mcq_questions is None and num_comprehension_questions is None):
        if num_mcq_questions is not None or (num_mcq_questions is None and num_comprehension_questions is None):
            prompt += ","
        prompt += """
  "comprehension_questions": [
    {
      "question": "سؤال الفهم هنا؟",
      "answer": "الإجابة المتوقعة"
    }
  ]"""
    
    prompt += "\n}"
    return prompt

