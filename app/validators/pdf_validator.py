def pdf_validate(request):
    """
    Validate if the uploaded file is a valid PDF.
    Returns True if valid, False otherwise.
    """
    # Handle PDF upload
    if 'pdf_file' not in request.files:
        return False, 'لم يتم إرفاق ملف PDF'
    
    pdf_file = request.files['pdf_file']
    
    if pdf_file.filename == '':
        return False, 'لم يتم اختيار ملف'
    
    return pdf_file, None

def pdf_extraction_validate(result):
    if not result['success']:
        return False, result['error']
    else:
        return True, result['text']