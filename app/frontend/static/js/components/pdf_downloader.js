// components/pdf_downloader.js - Proper Arabic PDF Support

function downloadQuizAsPDF(questions, originalText, metadata) {
    const downloadBtn = document.getElementById('downloadPdfBtn');
    downloadBtn.classList.add('loading-download');
    downloadBtn.innerHTML = '⏳ جاري التحضير...';
    
    // Check if answers should be shown
    const answersToggle = document.getElementById('answersToggle');
    const showAnswers = answersToggle ? answersToggle.checked : false;
    
    // Try different approach: Create HTML and use browser's print-to-PDF capability
    createPrintablePDF(questions, originalText, metadata, showAnswers);
}

function createPrintablePDF(questions, originalText, metadata, showAnswers = false) {
    // Create a new window with properly formatted HTML
    const printWindow = window.open('', '_blank');
    
    const htmlContent = `
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Arabic Quiz</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Arial', 'Tahoma', sans-serif;
                font-size: 14px;
                line-height: 1.6;
                color: #042328;
                direction: rtl;
                text-align: right;
                padding: 20px;
                background: white;
            }
            
            .header {
                text-align: center;
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 3px solid #EAAA7A;
            }
            
            .title {
                font-size: 24px;
                font-weight: bold;
                color: #042328;
                margin-bottom: 10px;
            }
            
            .subtitle {
                font-size: 18px;
                color: #2A615E;
                margin-bottom: 15px;
            }
            
            .metadata {
                background: #CDE7E8;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 25px;
                direction: ltr;
                text-align: left;
            }
            
            .metadata h3 {
                color: #042328;
                margin-bottom: 10px;
                font-size: 16px;
            }
            
            .metadata p {
                margin: 5px 0;
                color: #2A615E;
            }
            
            .question {
                background: white;
                border: 2px solid #CDE7E8;
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 25px;
                page-break-inside: avoid;
            }
            
            .question-header {
                background: #EAAA7A;
                color: white;
                padding: 8px 15px;
                border-radius: 20px;
                display: inline-block;
                font-weight: bold;
                margin-bottom: 15px;
                font-size: 14px;
            }
            
            .question-text {
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 15px;
                line-height: 1.8;
                color: #042328;
            }
            
            .options {
                list-style: none;
                padding: 0;
            }
            
            .option {
                padding: 10px 15px;
                margin: 8px 0;
                border-radius: 8px;
                background: #f8f9fa;
                border: 1px solid #CDE7E8;
                display: flex;
                align-items: center;
                direction: rtl;
            }
            
            .option.correct {
                background: linear-gradient(145deg, #2A615E, #30625F);
                color: white;
                border-color: #EAAA7A;
                font-weight: bold;
            }
            
            .option-letter {
                background: #042328;
                color: white;
                width: 25px;
                height: 25px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                font-size: 12px;
                margin-left: 10px;
                flex-shrink: 0;
            }
            
            .option.correct .option-letter {
                background: #EAAA7A;
            }
            
            .option-text {
                flex: 1;
                font-size: 14px;
            }
            
            .correct-marker {
                color: #EAAA7A;
                font-weight: bold;
                margin-right: 10px;
                font-size: 16px;
            }
            
            .original-text {
                margin-top: 30px;
                padding: 20px;
                background: linear-gradient(145deg, #CDE7E8, #ffffff);
                border-radius: 12px;
                border-left: 5px solid #EAAA7A;
            }
            
            .original-text h3 {
                color: #042328;
                margin-bottom: 15px;
                font-size: 18px;
            }
            
            .original-text-content {
                background: rgba(255, 255, 255, 0.8);
                padding: 15px;
                border-radius: 8px;
                font-style: italic;
                line-height: 1.7;
                max-height: 200px;
                overflow-y: auto;
            }
            
            .footer {
                margin-top: 40px;
                text-align: center;
                color: #2A615E;
                font-size: 12px;
                border-top: 1px solid #CDE7E8;
                padding-top: 15px;
            }
            
            .answers-note {
                background: #CDE7E8;
                padding: 10px 15px;
                border-radius: 8px;
                margin-bottom: 20px;
                text-align: center;
                font-weight: bold;
                color: #042328;
            }
            
            @media print {
                body {
                    padding: 15px;
                    font-size: 12px;
                }
                
                .question {
                    margin-bottom: 20px;
                    page-break-inside: avoid;
                }
                
                .header {
                    margin-bottom: 20px;
                }
                
                .original-text-content {
                    max-height: none;
                    overflow: visible;
                }
            }
            
            @page {
                margin: 2cm;
                size: A4;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <div class="title">اختبار مولد تلقائياً</div>
            <div class="subtitle">Arabic Quiz Generated</div>
        </div>
        
        <div class="metadata">
            <h3>Quiz Information</h3>
            <p><strong>Total Questions:</strong> ${questions.length}</p>
            <p><strong>Generated:</strong> ${new Date().toLocaleDateString('en-GB')}</p>
            <p><strong>Answers Shown:</strong> ${showAnswers ? 'Yes' : 'No'}</p>
            ${metadata && metadata.thread_id ? `<p><strong>Thread ID:</strong> ${metadata.thread_id}</p>` : ''}
            ${metadata && metadata.concurrent_users ? `<p><strong>Concurrent Users:</strong> ${metadata.concurrent_users}</p>` : ''}
        </div>
        
        ${showAnswers ? '<div class="answers-note">✓ تم عرض الإجابات الصحيحة | Correct Answers Shown</div>' : '<div class="answers-note">الإجابات الصحيحة مخفية | Correct Answers Hidden</div>'}
        
        ${questions.map((q, index) => `
            <div class="question">
                <div class="question-header">السؤال ${index + 1}</div>
                <div class="question-text">${q.question}</div>
                <ul class="options">
                    ${q.options.map((option, optIndex) => {
                        const isCorrect = optIndex === q.correct_answer;
                        const optionLetters = ['أ', 'ب', 'ج'];
                        return `
                            <li class="option ${showAnswers && isCorrect ? 'correct' : ''}">
                                <span class="option-letter">${optionLetters[optIndex]}</span>
                                <span class="option-text">${option}</span>
                                ${showAnswers && isCorrect ? '<span class="correct-marker">✓</span>' : ''}
                            </li>
                        `;
                    }).join('')}
                </ul>
            </div>
        `).join('')}
        
        <div class="original-text">
            <h3>النص الأصلي</h3>
            <div class="original-text-content">${originalText}</div>
        </div>
        
        <div class="footer">
            <p>تم إنشاؤه بواسطة مولد الأسئلة الذكي | Generated by Smart Quiz Generator</p>
            <p>التاريخ: ${new Date().toLocaleDateString('ar')}</p>
        </div>
    </body>
    </html>
    `;
    
    printWindow.document.writeln(htmlContent);
    printWindow.document.close();
    
    // Wait for content to load, then trigger print
    printWindow.onload = function() {
        setTimeout(() => {
            printWindow.print();
            
            // Reset download button
            const downloadBtn = document.getElementById('downloadPdfBtn');
            downloadBtn.classList.remove('loading-download');
            downloadBtn.innerHTML = '📄 تحميل PDF';
            
            // Close window after print dialog
            printWindow.onafterprint = function() {
                printWindow.close();
            };
            
            // Also close if user cancels (fallback)
            setTimeout(() => {
                if (!printWindow.closed) {
                    printWindow.close();
                }
            }, 30000); // Close after 30 seconds if still open
            
            // Close on window focus loss (when user cancels)
            printWindow.onblur = function() {
                setTimeout(() => {
                    if (!printWindow.closed) {
                        printWindow.close();
                    }
                }, 1000);
            };
            
        }, 500);
    };
}

// Alternative: Create downloadable HTML file
function downloadQuizAsHTML(questions, originalText, metadata) {
    const htmlContent = `<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Arabic Quiz</title>
    <style>
        body {
            font-family: 'Arial', 'Tahoma', sans-serif;
            direction: rtl;
            text-align: right;
            padding: 20px;
            background: #f8f9fa;
            color: #042328;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(4, 35, 40, 0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 3px solid #EAAA7A;
        }
        .title {
            font-size: 28px;
            font-weight: bold;
            color: #042328;
            margin-bottom: 10px;
        }
        .question {
            background: white;
            border: 2px solid #CDE7E8;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 25px;
        }
        .question-header {
            background: #EAAA7A;
            color: white;
            padding: 8px 15px;
            border-radius: 20px;
            display: inline-block;
            font-weight: bold;
            margin-bottom: 15px;
        }
        .option {
            padding: 10px 15px;
            margin: 8px 0;
            border-radius: 8px;
            background: #CDE7E8;
            display: flex;
            align-items: center;
        }
        .option.correct {
            background: linear-gradient(145deg, #2A615E, #30625F);
            color: white;
            font-weight: bold;
        }
        .option-letter {
            background: #042328;
            color: white;
            width: 25px;
            height: 25px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            margin-left: 10px;
        }
        
        /* Quiz Display Styles - Enhanced Design with Catalog Colors */

.quiz-container {
    background: linear-gradient(145deg, rgba(205, 231, 232, 0.15) 0%, rgba(255, 255, 255, 0.98) 100%);
    padding: 30px;
    border-radius: 20px;
    margin-top: 30px;
    border: 3px solid transparent;
    background-clip: padding-box;
    box-shadow: 
        0 20px 40px rgba(4, 35, 40, 0.15),
        0 8px 25px rgba(42, 97, 94, 0.1),
        inset 0 1px 0 rgba(205, 231, 232, 0.3);
    animation: fadeInScale 0.8s cubic-bezier(0.16, 1, 0.3, 1);
    width: 100%;
    box-sizing: border-box;
    overflow: hidden;
    position: relative;
}

.quiz-container::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, #CDE7E8 0%, #EAAA7A 50%, #2A615E 100%);
    padding: 3px;
    border-radius: 20px;
    z-index: -1;
    mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    mask-composite: exclude;
}

.quiz-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 25px;
    flex-wrap: wrap;
    gap: 20px;
    padding-bottom: 20px;
    border-bottom: 2px solid rgba(205, 231, 232, 0.3);
}

.quiz-title {
    color: #042328;
    font-size: 1.6rem;
    font-weight: 800;
    margin: 0;
    word-wrap: break-word;
    text-shadow: 0 2px 4px rgba(4, 35, 40, 0.1);
    position: relative;
}

.quiz-title::after {
    content: '';
    position: absolute;
    bottom: -8px;
    left: 0;
    width: 60px;
    height: 3px;
    background: linear-gradient(90deg, #EAAA7A 0%, #2A615E 100%);
    border-radius: 2px;
}

.quiz-controls {
    display: flex;
    gap: 20px;
    align-items: center;
    flex-wrap: wrap;
    background: rgba(205, 231, 232, 0.1);
    padding: 12px 18px;
    border-radius: 15px;
    backdrop-filter: blur(10px);
}

.toggle-switch {
    position: relative;
    display: inline-block;
    width: 65px;
    height: 36px;
    flex-shrink: 0;
}

.toggle-switch input {
    opacity: 0;
    width: 0;
    height: 0;
}

.slider {
    position: absolute;
    cursor: pointer;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, #CDE7E8 0%, #CDE7E8 100%);
    transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1);
    border-radius: 36px;
    box-shadow: inset 0 2px 4px rgba(4, 35, 40, 0.1);
}

.slider:before {
    position: absolute;
    content: "";
    height: 28px;
    width: 28px;
    left: 4px;
    bottom: 4px;
    background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
    transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1);
    border-radius: 50%;
    box-shadow: 
        0 4px 8px rgba(4, 35, 40, 0.2),
        0 2px 4px rgba(42, 97, 94, 0.1);
}

input:checked + .slider {
    background: linear-gradient(135deg, #2A615E 0%, #2A615E 100%);
    box-shadow: 
        inset 0 2px 4px rgba(4, 35, 40, 0.2),
        0 0 15px rgba(234, 170, 122, 0.3);
}

input:focus + .slider {
    box-shadow: 0 0 0 3px rgba(234, 170, 122, 0.2);
}

input:checked + .slider:before {
    transform: translateX(29px);
    background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
    box-shadow: 
        0 4px 12px rgba(234, 170, 122, 0.3),
        0 2px 6px rgba(4, 35, 40, 0.1);
}

.toggle-label {
    font-size: 15px;
    color: #042328;
    margin-right: 12px;
    font-weight: 600;
    white-space: nowrap;
    text-shadow: 0 1px 2px rgba(4, 35, 40, 0.1);
}

.download-btn {
    background: linear-gradient(135deg, #EAAA7A 0%, #EAAA7A 100%);
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 25px;
    cursor: pointer;
    font-size: 15px;
    font-weight: 700;
    transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1);
    display: flex;
    align-items: center;
    gap: 10px;
    white-space: nowrap;
    flex-shrink: 0;
    box-shadow: 
        0 8px 16px rgba(234, 170, 122, 0.3),
        0 4px 8px rgba(4, 35, 40, 0.1);
    position: relative;
    overflow: hidden;
}

.download-btn::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
    transition: left 0.6s;
}

.download-btn:hover::before {
    left: 100%;
}

.download-btn:hover {
    background: linear-gradient(135deg, #2A615E 0%, #30625F 100%);
    transform: translateY(-3px);
    box-shadow: 
        0 12px 24px rgba(42, 97, 94, 0.4),
        0 6px 12px rgba(4, 35, 40, 0.2);
}

.quiz-question {
    background: linear-gradient(145deg, rgba(255, 255, 255, 0.9) 0%, rgba(205, 231, 232, 0.05) 100%);
    margin-bottom: 25px;
    padding: 25px;
    border-radius: 16px;
    border: 2px solid rgba(205, 231, 232, 0.3);
    transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1);
    position: relative;
    overflow: hidden;
    width: 100%;
    box-sizing: border-box;
    backdrop-filter: blur(10px);
}

.quiz-question::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 4px;
    height: 100%;
    background: linear-gradient(180deg, #EAAA7A 0%, #2A615E 100%);
    transform: scaleY(0);
    transition: transform 0.4s cubic-bezier(0.23, 1, 0.32, 1);
}

.quiz-question:hover {
    border-color: rgba(234, 170, 122, 0.6);
    box-shadow: 
        0 12px 30px rgba(234, 170, 122, 0.15),
        0 6px 15px rgba(4, 35, 40, 0.1);
    transform: translateY(-2px);
}

.quiz-question:hover::before {
    transform: scaleY(1);
}

.question-number {
    position: absolute;
    top: 8px;
    right: 25px;
    background: linear-gradient(135deg, #EAAA7A 0%, #2A615E 100%);
    color: white;
    padding: 8px 16px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 800;
    white-space: nowrap;
    box-shadow: 
        0 4px 8px rgba(234, 170, 122, 0.3),
        0 2px 4px rgba(4, 35, 40, 0.1);
    animation: numberFloat 3s ease-in-out infinite;
}

@keyframes numberFloat {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-2px); }
}

.question-text {
    font-size: 1.2rem;
    font-weight: 700;
    color: #042328;
    margin-bottom: 20px;
    margin-top: 15px;
    line-height: 1.6;
    word-wrap: break-word;
    word-break: break-word;
    overflow-wrap: break-word;
    padding-right: 90px;
    text-shadow: 0 1px 2px rgba(4, 35, 40, 0.1);
}

.options-list {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.option-item {
    background: linear-gradient(135deg, rgba(205, 231, 232, 0.8) 0%, rgba(205, 231, 232, 0.4) 100%);
    margin-bottom: 0;
    padding: 16px 20px;
    border-radius: 12px;
    border: 2px solid transparent;
    transition: none;
    cursor: default;
    position: relative;
    display: flex;
    align-items: center;
    width: 100%;
    box-sizing: border-box;
    overflow: hidden;
    backdrop-filter: blur(5px);
}

.option-item::before {
    display: none;
}

.option-letter {
    background: linear-gradient(135deg, #042328 0%, #2A615E 100%);
    color: white;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    font-weight: 800;
    margin-left: 15px;
    flex-shrink: 0;
    box-shadow: 
        0 4px 8px rgba(4, 35, 40, 0.2),
        0 2px 4px rgba(42, 97, 94, 0.1);
    transition: none;
}

.option-text {
    flex: 1;
    font-size: 1.05rem;
    line-height: 1.5;
    word-wrap: break-word;
    word-break: break-word;
    overflow-wrap: break-word;
    min-width: 0;
    font-weight: 500;
}

/* Correct answer highlighting */
.option-item.correct {
    background: linear-gradient(145deg, #2A615E 0%, #30625F 100%);
    border-color: #EAAA7A;
    color: white;
    animation: correctPulse 0.8s ease;
    box-shadow: 
        0 8px 20px rgba(42, 97, 94, 0.4),
        0 4px 10px rgba(234, 170, 122, 0.3),
        inset 0 1px 0 rgba(234, 170, 122, 0.2);
}

.option-item.correct .option-letter {
    background: linear-gradient(135deg, #EAAA7A 0%, #EAAA7A 100%);
    box-shadow: 
        0 6px 12px rgba(234, 170, 122, 0.5),
        0 3px 6px rgba(4, 35, 40, 0.2);
}

.option-item.correct::after {
    content: "✓";
    position: absolute;
    left: 20px;
    color: #EAAA7A;
    font-size: 20px;
    font-weight: 900;
    text-shadow: 0 2px 4px rgba(4, 35, 40, 0.3);
    animation: checkmarkBounce 0.6s ease;
}

@keyframes correctPulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.03); }
    100% { transform: scale(1); }
}

@keyframes checkmarkBounce {
    0% { transform: scale(0) rotate(-45deg); }
    50% { transform: scale(1.2) rotate(0deg); }
    100% { transform: scale(1) rotate(0deg); }
}

/* Hidden answers state */
.answers-hidden .option-item.correct {
    background: linear-gradient(135deg, rgba(205, 231, 232, 0.8) 0%, rgba(205, 231, 232, 0.4) 100%);
    color: #042328;
    border-color: transparent;
    animation: none;
    box-shadow: none;
}

.answers-hidden .option-item.correct .option-letter {
    background: linear-gradient(135deg, #042328 0%, #2A615E 100%);
    box-shadow: 
        0 4px 8px rgba(4, 35, 40, 0.2),
        0 2px 4px rgba(42, 97, 94, 0.1);
}

.answers-hidden .option-item.correct::after {
    display: none;
}

/* Enhanced Quiz Stats Styles */
.quiz-stats {
    display: flex !important;
    flex-direction: column !important;
    gap: 20px !important;
    margin-top: 30px !important;
    padding: 25px !important;
    background: linear-gradient(135deg, rgba(42, 97, 94, 0.9) 0%, rgba(48, 98, 95, 0.9) 100%) !important;
    border-radius: 16px !important;
    border: 2px solid #EAAA7A !important;
    width: 100% !important;
    box-sizing: border-box !important;
    overflow: hidden !important;
    backdrop-filter: blur(15px) !important;
    box-shadow: 
        0 12px 30px rgba(4, 35, 40, 0.2),
        0 6px 15px rgba(42, 97, 94, 0.1),
        inset 0 1px 0 rgba(234, 170, 122, 0.1) !important;
}

.quiz-stats::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(45deg, rgba(234, 170, 122, 0.1) 0%, transparent 50%, rgba(205, 231, 232, 0.1) 100%);
    pointer-events: none;
}

.quiz-stats-card {
    background: linear-gradient(145deg, rgba(255, 255, 255, 0.95) 0%, rgba(205, 231, 232, 0.1) 100%) !important;
    border-radius: 14px !important;
    padding: 20px !important;
    box-shadow: 
        0 8px 20px rgba(4, 35, 40, 0.1),
        0 4px 10px rgba(42, 97, 94, 0.05) !important;
    border: 2px solid rgba(205, 231, 232, 0.3) !important;
    transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1) !important;
    width: 100% !important;
    box-sizing: border-box !important;
    overflow: hidden !important;
    backdrop-filter: blur(10px) !important;
    position: relative;
}

.quiz-stats-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 3px;
    background: linear-gradient(90deg, #EAAA7A 0%, #2A615E 100%);
    transform: scaleX(0);
    transition: transform 0.4s cubic-bezier(0.23, 1, 0.32, 1);
}

.quiz-stats-card:hover {
    box-shadow: 
        0 12px 30px rgba(4, 35, 40, 0.15),
        0 6px 15px rgba(42, 97, 94, 0.1) !important;
    transform: translateY(-4px) !important;
    border-color: rgba(234, 170, 122, 0.5) !important;
}

.quiz-stats-card:hover::before {
    transform: scaleX(1);
}

.stats-item {
    display: flex !important;
    align-items: flex-start !important;
    gap: 16px !important;
    width: 100% !important;
    overflow: hidden !important;
}

.stats-icon {
    font-size: 26px !important;
    background: linear-gradient(135deg, #2A615E, #30625F) !important;
    color: white !important;
    width: 48px !important;
    height: 48px !important;
    border-radius: 14px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    flex-shrink: 0 !important;
    box-shadow: 
        0 6px 12px rgba(42, 97, 94, 0.3),
        0 3px 6px rgba(4, 35, 40, 0.1) !important;
    transition: all 0.3s ease !important;
}

.quiz-stats-card:hover .stats-icon {
    transform: scale(1.1) rotate(5deg);
    background: linear-gradient(135deg, #EAAA7A, #EAAA7A) !important;
    box-shadow: 
        0 8px 16px rgba(234, 170, 122, 0.4),
        0 4px 8px rgba(4, 35, 40, 0.2) !important;
}

.stats-content {
    flex: 1 !important;
    min-width: 0 !important;
    overflow: hidden !important;
    width: calc(100% - 64px) !important;
}

.stats-label {
    font-size: 15px !important;
    font-weight: 700 !important;
    color: #042328 !important;
    margin-bottom: 8px !important;
    text-align: right !important;
    word-wrap: break-word !important;
    text-shadow: 0 1px 2px rgba(4, 35, 40, 0.1) !important;
}

.stats-value {
    font-size: 17px !important;
    font-weight: 800 !important;
    color: #042328 !important;
    line-height: 1.5 !important;
    text-align: right !important;
    width: 100% !important;
    word-wrap: break-word !important;
    word-break: break-word !important;
    overflow-wrap: break-word !important;
}

/* Original text specific styles */
.original-text-card {
    border-left: 6px solid #EAAA7A !important;
}

.original-text-card .stats-icon {
    background: linear-gradient(135deg, #EAAA7A, #EAAA7A) !important;
}

.original-text-content {
    max-height: 140px !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;
    padding: 16px !important;
    background: linear-gradient(145deg, rgba(205, 231, 232, 0.4) 0%, rgba(255, 255, 255, 0.8) 100%) !important;
    border-radius: 10px !important;
    border: 2px solid rgba(42, 97, 94, 0.2) !important;
    font-family: 'Arial', sans-serif !important;
    font-size: 15px !important;
    line-height: 1.7 !important;
    word-wrap: break-word !important;
    word-break: break-word !important;
    overflow-wrap: break-word !important;
    white-space: pre-wrap !important;
    direction: rtl !important;
    text-align: right !important;
    width: 100% !important;
    box-sizing: border-box !important;
    color: #042328 !important;
    backdrop-filter: blur(5px) !important;
    box-shadow: inset 0 2px 4px rgba(4, 35, 40, 0.05) !important;
}

.original-text-content::-webkit-scrollbar {
    width: 8px;
}

.original-text-content::-webkit-scrollbar-track {
    background: rgba(205, 231, 232, 0.3);
    border-radius: 4px;
}

.original-text-content::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #2A615E 0%, #30625F 100%);
    border-radius: 4px;
    transition: background 0.3s ease;
}

.original-text-content::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, #EAAA7A 0%, #2A615E 100%);
}

.loading-download {
    opacity: 0.6;
    pointer-events: none;
    transform: scale(0.98);
}

/* Responsive design for quiz */
@media (max-width: 768px) {
    .quiz-container {
        padding: 20px;
        margin-top: 20px;
    }
    
    .quiz-header {
        flex-direction: column;
        align-items: stretch;
        gap: 15px;
    }
    
    .quiz-controls {
        justify-content: center;
        flex-wrap: wrap;
        padding: 10px 15px;
    }
    
    .quiz-question {
        padding: 20px;
        margin-bottom: 20px;
    }
    
    .question-text {
        font-size: 1.1rem;
        padding-right: 80px;
    }
    
    .option-item {
        padding: 14px 16px;
    }
    
    .quiz-stats {
        padding: 20px !important;
        gap: 16px !important;
        margin-top: 25px !important;
    }
    
    .quiz-stats-card {
        padding: 16px !important;
    }
    
    .stats-icon {
        width: 40px !important;
        height: 40px !important;
        font-size: 22px !important;
    }
    
    .stats-label {
        font-size: 14px !important;
    }
    
    .stats-value {
        font-size: 16px !important;
    }
    
    .original-text-content {
        font-size: 14px !important;
        max-height: 120px !important;
        padding: 14px !important;
    }
    
    .toggle-label {
        font-size: 13px;
        margin-right: 8px;
    }
    
    .download-btn {
        font-size: 13px;
        padding: 10px 20px;
    }
}

/* Animation for when stats appear */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes fadeInScale {
    from {
        opacity: 0;
        transform: scale(0.9) translateY(20px);
    }
    to {
        opacity: 1;
        transform: scale(1) translateY(0);
    }
}

.quiz-stats-card {
    animation: fadeInUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) ease-out;
}

.quiz-stats-card:nth-child(2) {
    animation-delay: 0.15s;
}

/* Loading states */
@keyframes shimmer {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
}

.quiz-question:hover .option-item {
    animation: none;
}

/* Enhanced focus states for accessibility */
.toggle-switch input:focus + .slider,
.download-btn:focus {
    outline: 3px solid rgba(234, 170, 122, 0.4);
    outline-offset: 2px;
}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="title">اختبار مولد تلقائياً</div>
            <p>إجمالي الأسئلة: ${questions.length} | التاريخ: ${new Date().toLocaleDateString('ar')}</p>
        </div>
        
        ${questions.map((q, index) => `
            <div class="question">
                <div class="question-header">السؤال ${index + 1}</div>
                <div style="font-size: 16px; font-weight: bold; margin-bottom: 15px;">${q.question}</div>
                ${q.options.map((option, optIndex) => {
                    const isCorrect = optIndex === q.correct_answer;
                    const optionLetters = ['أ', 'ب', 'ج'];
                    return `
                        <div class="option ${isCorrect ? 'correct' : ''}">
                            <span class="option-letter">${optionLetters[optIndex]}</span>
                            <span>${option}</span>
                            ${isCorrect ? '<span style="color: #EAAA7A; font-weight: bold; margin-right: 10px;">✓</span>' : ''}
                        </div>
                    `;
                }).join('')}
            </div>
        `).join('')}
        
        <div style="margin-top: 30px; padding: 20px; background: #CDE7E8; border-radius: 12px;">
            <h3>النص الأصلي</h3>
            <div style="background: white; padding: 15px; border-radius: 8px; margin-top: 10px;">
                ${originalText}
            </div>
        </div>
    </div>
</body>
</html>`;

    const blob = new Blob([htmlContent], { type: 'text/html; charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `arabic_quiz_${new Date().getTime()}.html`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}