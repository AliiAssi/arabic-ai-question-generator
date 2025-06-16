// components/api.js

async function handleTextSubmit(e) {
    e.preventDefault();
    
    const textInput = document.getElementById('textInput');
    const text = textInput.value.trim();
    
    if (!text) {
        showError('الرجاء إدخال نص للتحليل');
        return;
    }

    setLoadingState('text', true);
    hideResults();
    hideError();

    try {
        console.log(`📤 Sending text request to: ${API_ENDPOINT}`);
        
        const response = await fetch(API_ENDPOINT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: text })
        });

        const data = await response.json();
        console.log('📥 Response received:', data);
        
        handleResponse(data, text);

    } catch (error) {
        console.error('❌ Error:', error);
        showError('حدث خطأ في الاتصال بالخادم');
    } finally {
        setLoadingState('text', false);
    }
}

async function handlePdfSubmit(e) {
    e.preventDefault();
    
    const fileInput = document.getElementById('pdfInput');
    const file = fileInput.files[0];
    
    if (!file) {
        showError('الرجاء اختيار ملف PDF');
        return;
    }

    setLoadingState('pdf', true);
    hideResults();
    hideError();

    try {
        console.log(`📤 Sending PDF request to: ${API_ENDPOINT}`);
        
        const formData = new FormData();
        formData.append('pdf_file', file);

        const response = await fetch(API_ENDPOINT, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        console.log('📥 Response received:', data);
        
        handleResponse(data, data.original_text || 'النص المستخرج من PDF');

    } catch (error) {
        console.error('❌ Error:', error);
        showError('حدث خطأ في معالجة ملف PDF');
    } finally {
        setLoadingState('pdf', false);
    }
}

function handleResponse(data, originalText) {
    // Show API mode in response if in test mode
    if (API_MODE === 'test' && data.metadata && data.metadata.api_mode) {
        console.log(`🧪 Test API Response: ${data.metadata.response_message}`);
    }
    
    if (data.success) {
        // Extract questions from the new API structure
        let questions;
        
        // Handle both old format (direct questions array) and new format (LLM.questions)
        if (data.LLM && data.LLM.questions) {
            questions = data.LLM.questions;
        } else if (data.questions) {
            questions = data.questions;
        } else {
            showError('تنسيق الاستجابة غير صحيح - لم يتم العثور على الأسئلة');
            return;
        }
        
        showResults(questions, originalText, data.metadata);
    } else {
        showError(data.error || 'حدث خطأ غير متوقع');
    }
}