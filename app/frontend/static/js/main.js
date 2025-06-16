// main.js

document.addEventListener('DOMContentLoaded', function() {
    
    // Mode switching
    textModeBtn.addEventListener('click', () => switchMode('text'));
    pdfModeBtn.addEventListener('click', () => switchMode('pdf'));

    // File upload handling
    fileUploadArea.addEventListener('click', () => pdfInput.click());
    fileUploadArea.addEventListener('dragover', handleDragOver);
    fileUploadArea.addEventListener('dragleave', handleDragLeave);
    fileUploadArea.addEventListener('drop', handleDrop);
    pdfInput.addEventListener('change', handleFileSelect);

    // Form submissions
    textForm.addEventListener('submit', handleTextSubmit);
    pdfForm.addEventListener('submit', handlePdfSubmit);

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