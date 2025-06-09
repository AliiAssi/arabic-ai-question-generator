# AI Content Generator 🤖

A scalable, multi-threaded Flask application that generates comprehensive Arabic questions from text input or PDF files using Google's Gemini AI.

## ✨ Features

### 🔥 Current Features
- **📝 Text-to-Questions Generation**: Input Arabic text and generate comprehensive, non-redundant questions
- **📄 PDF Upload & Processing**: Upload PDF files for automatic text extraction and question generation
- **🧵 Multi-threaded Processing**: Concurrent request handling with ThreadPoolExecutor for better performance
- **👥 Real-time User Analytics**: Track concurrent users, session analytics, and detailed usage statistics
- **📊 Admin Dashboard**: Live monitoring of active users, request statistics, and system health
- **🌐 Bilingual Support**: Arabic and English language support (Arabic primary)
- **⚡ Async/Sync Processing**: Choose between synchronous and asynchronous content generation
- **🔒 Thread-safe Operations**: Safe concurrent access to AI APIs with proper locking mechanisms
- **📋 Comprehensive Logging**: Detailed logs for user activity, errors, and system performance
- **🎨 Modern UI**: Clean, responsive Arabic RTL interface with drag-and-drop PDF upload

### 🚀 Future Features
- **🔐 User Authentication**: Login system with role-based access control
- **💾 Database Integration**: Store user sessions, generated content, and analytics
- **🔄 Content Caching**: Cache frequently requested content for faster responses
- **📈 Advanced Analytics**: Export usage reports, user behavior analysis
- **🌍 Multi-language Expansion**: Support for more languages beyond Arabic/English
- **🤖 Multiple AI Models**: Integration with different AI providers (OpenAI, Claude, etc.)
- **📱 API Rate Limiting**: Prevent abuse with configurable rate limits
- **🔔 Real-time Notifications**: WebSocket integration for live updates
- **📤 Content Export**: Export generated questions to various formats (Word, PDF, JSON)
- **🎯 Question Categorization**: Automatic classification of questions by type/difficulty

## 📁 Project Structure

### 🏗️ Core Application (`app/`)
```
app/
├── clients/
│   └── ai_client.py           # Google GenAI client wrapper with error handling
├── config/
│   └── settings.py            # Environment-based configuration management
├── core/
│   ├── exceptions.py          # Custom exception hierarchy for error handling
│   └── models.py              # Data models for requests/responses with validation
├── services/
│   ├── content_service.py     # Multi-threaded content generation orchestration
│   ├── pdf_service.py         # PDF upload, validation, and text extraction
│   └── user_tracker.py        # Concurrent user tracking and analytics
├── prompts/
│   └── arabic/
│       └── questions.py       # Arabic question generation prompt templates
└── app.py                     # Flask application factory with route definitions
```

### 🎨 Frontend (`app/frontend/`)
```
frontend/
├── static/
│   ├── css/
│   │   └── main.css           # Modern RTL styling with responsive design
│   └── js/
│       └── main.js            # Frontend logic for text/PDF upload handling
└── templates/
    ├── admin_dashboard.html   # Real-time user analytics dashboard
    └── index.html             # Main application interface with dual input modes
```

### 📊 Data & Logs
```
docs/                          # Documentation and sample PDFs for testing
logs/                          # Application logs and user activity tracking
requirements.txt               # Python dependencies (Flask, GenAI, threading libs)
run.py                         # Application entry point and server startup
```

## 🚀 Quick Start

### 1️⃣ Environment Setup
```bash
# Clone the repository
git clone <repository-url>
cd ai-content-generator

# Create virtual environment
cd scripts
python setup_env.py

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 2️⃣ Configuration
```bash
# Create environment file
cp app/.env.example app/.env

# Edit app/.env with your settings:
GENAI_API_KEY=your_google_genai_api_key_here
SECRET_KEY=your_secret_key_for_sessions
DEBUG=True
MAX_WORKERS=4
```

### 3️⃣ Run Application
```bash
python run.py
```

Navigate to `http://localhost:5000` to access the application.

## 🎯 Usage

### 📝 Text Input Mode
1. Select "إدخال نص" (Text Input) tab
2. Enter Arabic text in the textarea
3. Click "توليد الأسئلة" (Generate Questions)
4. View comprehensive questions generated from your text

### 📄 PDF Upload Mode
1. Select "رفع ملف PDF" (PDF Upload) tab
2. Drag & drop or click to select a PDF file (max 50MB)
3. Click "استخراج النص وتوليد الأسئلة" (Extract Text & Generate Questions)
4. View questions generated from extracted PDF content

### 📊 Admin Dashboard
Visit `http://localhost:5000/admin/dashboard` to monitor:
- Real-time concurrent user count
- User activity by time frames
- System statistics and performance metrics
- Auto-refreshing analytics every 30 seconds

## 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main application interface |
| `/generate` | POST | Generate questions from text or PDF |
| `/health` | GET | System health check and status |
| `/stats` | GET | JSON user statistics and analytics |
| `/admin/dashboard` | GET | Admin monitoring dashboard |
| `/admin/users` | GET | Detailed user session information |

## 🏗️ Architecture Highlights

### 🧵 Multi-threading Design
- **ThreadPoolExecutor**: Configurable worker threads for concurrent processing
- **Thread-safe AI Client**: Mutex locks prevent API race conditions
- **Async/Sync Support**: Choose processing mode based on requirements

### 📊 User Analytics
- **Session Tracking**: UUID-based user identification across requests
- **Real-time Monitoring**: Live concurrent user counting and activity logging
- **Automatic Cleanup**: Inactive session removal with configurable timeouts

### 🔒 Security Features
- **File Validation**: PDF type checking, size limits, and malware protection
- **Input Sanitization**: Text validation and XSS prevention
- **Rate Limiting Ready**: Framework in place for future rate limiting implementation

## 🛠️ Development

### 📋 Prerequisites
- Python 3.8+
- Google GenAI API key
- Modern web browser with JavaScript enabled

### 🧪 Testing
```bash
# Test PDF functionality
python scripts/generate_arabic_pdf.py

# Extract project structure
python scripts/extract_project_structure.py

# Monitor logs
tail -f logs/concurrent_users.log
tail -f logs/user_activity.log
```

### 🔧 Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `GENAI_API_KEY` | Required | Google GenAI API authentication key |
| `SECRET_KEY` | Required | Flask session encryption key |
| `MAX_WORKERS` | 4 | ThreadPoolExecutor worker count |
| `DEBUG` | False | Development mode toggle |
| `LOG_LEVEL` | INFO | Application logging verbosity |
| `REQUEST_TIMEOUT` | 300 | Maximum request processing time (seconds) |

## 🙏 Acknowledgments

- **Google Gemini AI** for advanced text processing capabilities
- **Flask Community** for the robust web framework
- **Arabic NLP Community** for language processing insights

---

**Built with ❤️ for the Arabic-speaking community**

*Empowering education through AI-driven question generation*