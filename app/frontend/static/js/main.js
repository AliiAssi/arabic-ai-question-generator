// main.js
document.addEventListener('DOMContentLoaded', function() {
    // API Configuration - Change this to switch between test and production
    const API_MODE = 'test'; // Change to 'production' for real Gemini API
    const API_ENDPOINT = API_MODE === 'test' ? '/generate/test' : '/generate';
    
    console.log(`🔧 API Mode: ${API_MODE} | Endpoint: ${API_ENDPOINT}`);
    
    const textModeBtn = document.getElementById('textModeBtn');
    const pdfModeBtn = document.getElementById('pdfModeBtn');
    const textForm = document.getElementById('textForm');
    const pdfForm = document.getElementById('pdfForm');
    const pdfInput = document.getElementById('pdfInput');
    const fileUploadArea = document.getElementById('fileUploadArea');
    const fileInfo = document.getElementById('fileInfo');
    const pdfSubmitBtn = document.getElementById('pdfSubmitBtn');
    
    const resultsContainer = document.getElementById('results');
    const errorContainer = document.getElementById('error');
    const questionsOutput = document.getElementById('questionsOutput');
    const originalTextOutput = document.getElementById('originalTextOutput');
    const errorMessage = document.getElementById('errorMessage');

    // Mode switching
    textModeBtn.addEventListener('click', () => switchMode('text'));
    pdfModeBtn.addEventListener('click', () => switchMode('pdf'));

    function switchMode(mode) {
        if (mode === 'text') {
            textModeBtn.classList.add('active');
            pdfModeBtn.classList.remove('active');
            textForm.style.display = 'block';
            pdfForm.style.display = 'none';
        } else {
            pdfModeBtn.classList.add('active');
            textModeBtn.classList.remove('active');
            textForm.style.display = 'none';
            pdfForm.style.display = 'block';
        }
        hideResults();
        hideError();
    }

    // File upload handling
    fileUploadArea.addEventListener('click', () => pdfInput.click());
    fileUploadArea.addEventListener('dragover', handleDragOver);
    fileUploadArea.addEventListener('dragleave', handleDragLeave);
    fileUploadArea.addEventListener('drop', handleDrop);
    pdfInput.addEventListener('change', handleFileSelect);

    function handleDragOver(e) {
        e.preventDefault();
        fileUploadArea.classList.add('dragover');
    }

    function handleDragLeave(e) {
        e.preventDefault();
        fileUploadArea.classList.remove('dragover');
    }

    function handleDrop(e) {
        e.preventDefault();
        fileUploadArea.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    }

    function handleFileSelect(e) {
        const file = e.target.files[0];
        if (file) {
            handleFile(file);
        }
    }

    function handleFile(file) {
        // Validate file
        if (!file.type.includes('pdf')) {
            showError('يجب أن يكون الملف بصيغة PDF');
            return;
        }

        const maxSize = 50 * 1024 * 1024; // 50MB
        if (file.size > maxSize) {
            showError('حجم الملف كبير جداً. الحد الأقصى 50 ميجابايت');
            return;
        }

        // Show file info
        const sizeInMB = (file.size / (1024 * 1024)).toFixed(2);
        fileInfo.innerHTML = `
            <div class="file-name">📄 ${file.name}</div>
            <div class="file-details">الحجم: ${sizeInMB} ميجابايت</div>
        `;
        fileInfo.style.display = 'block';
        pdfSubmitBtn.disabled = false;
        hideError();
    }

    // Form submissions
    textForm.addEventListener('submit', handleTextSubmit);
    pdfForm.addEventListener('submit', handlePdfSubmit);

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
            showResults(data.questions, originalText, data.metadata);
        } else {
            showError(data.error || 'حدث خطأ غير متوقع');
        }
    }

    function setLoadingState(mode, isLoading) {
        const submitBtn = mode === 'text' ? document.getElementById('textSubmitBtn') : document.getElementById('pdfSubmitBtn');
        const btnText = submitBtn.querySelector('.btn-text');
        const loader = submitBtn.querySelector('.loader');
        
        submitBtn.disabled = isLoading;
        
        if (isLoading) {
            btnText.style.display = 'none';
            loader.style.display = 'inline-block';
        } else {
            btnText.style.display = 'inline-block';
            loader.style.display = 'none';
        }
    }

    function showResults(questions, originalText, metadata) {
        questionsOutput.textContent = questions;
        originalTextOutput.textContent = originalText;
        
        // Add API mode indicator if in test mode
        if (API_MODE === 'test' && metadata && metadata.api_mode === 'test') {
            const testIndicator = document.createElement('div');
            testIndicator.className = 'test-mode-indicator';
            testIndicator.innerHTML = `
                <strong>🧪 وضع الاختبار:</strong> ${metadata.response_message}<br>
                <small>لتفعيل الذكاء الاصطناعي الحقيقي، غيّر API_MODE إلى 'production'</small>
            `;
            questionsOutput.parentNode.insertBefore(testIndicator, questionsOutput);
        }
        
        // Add source info if available
        if (metadata && metadata.source_type === 'pdf') {
            const sourceInfo = document.createElement('div');
            sourceInfo.className = 'source-info';
            sourceInfo.innerHTML = `
                <strong>المصدر:</strong> ${metadata.source_info.filename}<br>
                <strong>حجم الملف:</strong> ${(metadata.source_info.file_size / (1024 * 1024)).toFixed(2)} ميجابايت<br>
                <strong>طول النص المستخرج:</strong> ${metadata.source_info.extracted_length} حرف
            `;
            originalTextOutput.parentNode.appendChild(sourceInfo);
        }
        
        resultsContainer.style.display = 'block';
        resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    function showError(message) {
        errorMessage.textContent = message;
        errorContainer.style.display = 'block';
        errorContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    function hideResults() {
        resultsContainer.style.display = 'none';
        // Remove any existing source info and test indicators
        const existingSourceInfo = document.querySelector('.source-info');
        if (existingSourceInfo) {
            existingSourceInfo.remove();
        }
        const existingTestIndicator = document.querySelector('.test-mode-indicator');
        if (existingTestIndicator) {
            existingTestIndicator.remove();
        }
    }

    function hideError() {
        errorContainer.style.display = 'none';
    }

    // Auto-resize textarea
    const textInput = document.getElementById('textInput');
    textInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });

    // Display current API mode on page load
    const modeIndicator = document.createElement('div');
    modeIndicator.id = 'api-mode-indicator';
    modeIndicator.style.cssText = `
        position: fixed;
        top: 10px;
        right: 10px;
        background: ${API_MODE === 'test' ? '#ff9800' : '#4caf50'};
        color: white;
        padding: 8px 15px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        z-index: 1000;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    `;
    modeIndicator.textContent = API_MODE === 'test' ? '🧪 وضع الاختبار' : '🤖 وضع الإنتاج';
    document.body.appendChild(modeIndicator);
});