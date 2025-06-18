def text_validate(request):
    """
    Validate if the text input is valid.
    Returns True if valid, False otherwise.
    """
    # Handle text input
    if request.method == 'POST':
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return False, 'لم يتم إدخال أي نص'
        
        # Check for minimum length
        if len(text) < 1:
            return False, 'النص قصير جداً للمعالجة'
        
        return True, text
    
    return False, 'طريقة الطلب غير مدعومة'