// components/ui.js

// Mode switching
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

function showError(message) {
    errorMessage.textContent = message;
    errorContainer.style.display = 'block';
    errorContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function hideResults() {
    resultsContainer.style.display = 'none';
    
    // Remove any existing quiz container
    const existingQuiz = document.getElementById('quizContainer');
    if (existingQuiz) {
        existingQuiz.remove();
    }
    
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