// main.js
document.addEventListener('DOMContentLoaded', function() {
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
            const response = await fetch('/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: text })
            });

            const data = await response.json();
            handleResponse(data, text);

        } catch (error) {
            console.error('Error:', error);
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
            const formData = new FormData();
            formData.append('pdf_file', file);

            const response = await fetch('/generate', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            handleResponse(data, data.original_text || 'النص المستخرج من PDF');

        } catch (error) {
            console.error('Error:', error);
            showError('حدث خطأ في معالجة ملف PDF');
        } finally {
            setLoadingState('pdf', false);
        }
    }

    function handleResponse(data, originalText) {
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
        // Remove any existing source info
        const existingSourceInfo = document.querySelector('.source-info');
        if (existingSourceInfo) {
            existingSourceInfo.remove();
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
});