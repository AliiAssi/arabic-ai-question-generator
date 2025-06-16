// components/quiz.js

function showResults(questions, originalText, metadata) {
    // Check if questions is an array (new quiz format) or string (old format)
    if (Array.isArray(questions)) {
        showQuizResults(questions, originalText, metadata);
    } else {
        showTextResults(questions, originalText, metadata);
    }
}

function showTextResults(questions, originalText, metadata) {
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

function showQuizResults(questions, originalText, metadata) {
    // Hide the old results container
    resultsContainer.style.display = 'none';
    
    // Create quiz container
    const quizContainer = document.createElement('div');
    quizContainer.className = 'quiz-container';
    quizContainer.id = 'quizContainer';
    
    // Quiz header with controls
    const quizHeader = document.createElement('div');
    quizHeader.className = 'quiz-header';
    quizHeader.innerHTML = `
        <h2 class="quiz-title">الاختبار المولد (${questions.length} سؤال)</h2>
        <div class="quiz-controls">
            <span class="toggle-label">إظهار الإجابات الصحيحة</span>
            <label class="toggle-switch" style="margin-top: 10px;">
                <input type="checkbox" id="answersToggle">
                <span class="slider"></span>
            </label>
            <button class="download-btn" id="downloadPdfBtn">
                📄 تحميل PDF
            </button>
        </div>
    `;
    
    // Quiz questions
    const quizQuestions = document.createElement('div');
    quizQuestions.className = 'quiz-questions';
    quizQuestions.id = 'quizQuestions';
    
    questions.forEach((q, index) => {
        const questionDiv = document.createElement('div');
        questionDiv.className = 'quiz-question';
        
        const optionLetters = ['أ', 'ب', 'ج'];
        const optionsHtml = q.options.map((option, optIndex) => {
            const isCorrect = optIndex === q.correct_answer;
            return `
                <li class="option-item ${isCorrect ? 'correct' : ''}" data-correct="${isCorrect}">
                    <span class="option-letter">${optionLetters[optIndex]}</span>
                    <span class="option-text">${option}</span>
                </li>
            `;
        }).join('');
        
        questionDiv.innerHTML = `
            <span class="question-number">س${index + 1}</span>
            <div class="question-text">${q.question}</div>
            <ul class="options-list">
                ${optionsHtml}
            </ul>
        `;
        
        quizQuestions.appendChild(questionDiv);
    });
    
    // Quiz stats - enhanced design
    const quizStats = document.createElement('div');
    quizStats.className = 'quiz-stats';
    quizStats.innerHTML = `
        <div class="quiz-stats-card">
            <div class="stats-item">
                <div class="stats-icon">📊</div>
                <div class="stats-content">
                    <div class="stats-label">إجمالي الأسئلة</div>
                    <div class="stats-value">${questions.length}</div>
                </div>
            </div>
        </div>
        <div class="quiz-stats-card original-text-card">
            <div class="stats-item">
                <div class="stats-icon">📝</div>
                <div class="stats-content">
                    <div class="stats-label">النص الأصلي</div>
                    <div class="stats-value original-text-content" title="${originalText.replace(/"/g, '&quot;')}">${originalText}</div>
                </div>
            </div>
        </div>
    `;
    
    // Assemble quiz container
    quizContainer.appendChild(quizHeader);
    quizContainer.appendChild(quizQuestions);
    quizContainer.appendChild(quizStats);
    
    // Add after the main form
    const main = document.querySelector('main');
    main.appendChild(quizContainer);
    
    // Add event listeners
    const answersToggle = document.getElementById('answersToggle');
    const downloadBtn = document.getElementById('downloadPdfBtn');
    
    // Toggle answers visibility
    answersToggle.addEventListener('change', function() {
        const questionsContainer = document.getElementById('quizQuestions');
        if (this.checked) {
            questionsContainer.classList.remove('answers-hidden');
        } else {
            questionsContainer.classList.add('answers-hidden');
        }
    });
    
    // Initially hide answers
    document.getElementById('quizQuestions').classList.add('answers-hidden');
    
    // PDF download functionality
    downloadBtn.addEventListener('click', function() {
        downloadQuizAsPDF(questions, originalText, metadata);
    });
    
    // Scroll to quiz
    quizContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
}