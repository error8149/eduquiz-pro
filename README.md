# 🎓 EduQuiz Pro

**AI-Powered Quiz Generation and Management System**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

EduQuiz Pro is a modern, AI-powered quiz application that generates personalized multiple-choice questions for exam preparation. It supports multiple AI providers (Google Gemini, OpenAI, Groq) and provides comprehensive quiz management features.

## ✨ Features

### 🤖 AI-Powered Question Generation
- **Multiple AI Providers**: Support for Google Gemini, OpenAI GPT, and Groq
- **Smart Question Generation**: Creates unique, high-quality questions based on topics
- **Customizable Difficulty**: Easy, Medium, and Hard difficulty levels
- **Grade Level Adaptation**: Elementary to Graduate level questions
- **Topic-Based Organization**: Organize questions by subjects and topics

### 📊 Quiz Management
- **Real-time Quiz Taking**: Interactive quiz interface with timer
- **Progress Tracking**: Visual progress indicators and scoring
- **Detailed Explanations**: AI-generated explanations for each answer
- **Question Review**: Review incorrect answers with detailed explanations
- **Export Options**: Export quiz results to CSV format

### 📈 Analytics & History
- **Quiz History**: Track all completed quizzes with detailed statistics
- **Performance Analytics**: Score tracking and improvement metrics
- **Filtering & Search**: Filter quizzes by date, mode, and performance
- **Data Export**: Export historical data for analysis

### 🛠️ Advanced Features
- **Manual Mode**: Import custom questions via JSON
- **AI Prompt Generation**: Generate prompts for external AI tools
- **Ask AI**: Get additional explanations during quiz review
- **Responsive Design**: Works seamlessly on desktop and mobile
- **Dark Theme**: Modern, eye-friendly interface

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- At least one AI API key (Google Gemini, OpenAI, or Groq)

### Installation

1. **Clone or Download the Project**
   ```bash
   git clone <repository-url>
   cd Quiz
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install pydantic-settings
   ```

4. **Configure Environment**
   ```bash
   # Copy environment template
   copy .env.example .env  # Windows
   cp .env.example .env    # Linux/Mac
   
   # Edit .env file with your settings
   notepad .env  # Windows
   nano .env     # Linux/Mac
   ```

5. **Initialize Database**
   ```bash
   python migrate_db.py --init
   ```

6. **Start the Application**
   ```bash
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```

7. **Access the Application**
   Open your browser and go to: http://127.0.0.1:8000

## 📖 Usage Guide

### 1. Initial Setup

1. **Configure API Keys**
   - Go to Settings → API Keys
   - Add your API key for at least one provider:
     - **Google Gemini**: Get from [Google AI Studio](https://aistudio.google.com/app/apikey)
     - **OpenAI**: Get from [OpenAI Platform](https://platform.openai.com/api-keys)
     - **Groq**: Get from [Groq Console](https://console.groq.com/keys)

2. **Set Up Topics**
   - Go to Settings → Topics & Sections Management
   - Add your subjects and topics
   - Example: Section: "Mathematics", Topics: "Algebra, Geometry, Calculus"

### 2. Creating a Quiz

1. **Choose Quiz Settings**
   - Select grade level (Elementary to Graduate)
   - Choose difficulty (Easy, Medium, Hard)
   - Pick AI provider
   - Set number of questions (1-50)

2. **Select Mode**
   - **AI Generation**: Let AI create questions based on your topics
   - **Manual Input**: Import your own questions in JSON format

3. **Start Quiz**
   - Click "Start Quiz" and wait for questions to generate
   - Questions are created in real-time using AI

### 3. Taking a Quiz

1. **Answer Questions**
   - Read each question carefully
   - Select your answer from 4 options
   - Questions are automatically graded

2. **Review Explanations**
   - After answering, view detailed explanations
   - Use "Ask AI" for additional clarification
   - Click "Next Question" to continue

3. **Complete Quiz**
   - View your final score and statistics
   - Review incorrect answers
   - Export results or save quiz history

### 4. Managing History

1. **View Past Quizzes**
   - Go to History to see all completed quizzes
   - Filter by date, mode, or score
   - View detailed question-by-question results

2. **Export Data**
   - Export individual quiz results to CSV
   - Use data for progress tracking
   - Share results with instructors

## ⚙️ Configuration

### Environment Variables (.env)

```env
# Application Settings
ENVIRONMENT=development
DEBUG=true
APP_NAME=EduQuiz Pro

# Server Configuration
HOST=127.0.0.1
PORT=8000
RELOAD=true

# Database
DATABASE_URL=sqlite:///./quizapp.db

# CORS Settings (for development)
CORS_ORIGINS=http://127.0.0.1:8001,http://localhost:8001,http://127.0.0.1:8000,http://localhost:8000

# Logging
LOG_LEVEL=DEBUG
ENABLE_FILE_LOGGING=true
ENABLE_CONSOLE_LOGGING=true

# Features
ENABLE_HISTORY=true
ENABLE_EXPORT=true
ENABLE_AI_EXPLANATIONS=true
ENABLE_MANUAL_MODE=true

# API Limits
MAX_QUESTIONS_PER_QUIZ=50
MIN_QUESTIONS_PER_QUIZ=1
AI_REQUEST_TIMEOUT=30
```

### Quiz Settings

| Setting | Description | Default |
|---------|-------------|---------|
| Grade Level | Academic level for questions | High School |
| Difficulty | Question complexity | Medium |
| AI Provider | Which AI service to use | Gemini |
| Question Count | Number of questions per quiz | 10 |
| Time Limit | Quiz duration in minutes | 15 |

## 📡 API Documentation

### Health Check
```bash
GET /health
```
Returns application status and database connectivity.

### Configuration
```bash
GET /config
```
Returns public configuration for frontend.

### Start Quiz
```bash
POST /api/v1/quiz/start
Content-Type: application/json

{
  "topics": [{"section": "Math", "topic": "Algebra"}],
  "num_questions": 10,
  "api_provider": "gemini",
  "api_key": "your-api-key",
  "grade_level": "high school",
  "difficulty": "medium"
}
```

### Save Quiz Results
```bash
POST /api/v1/quiz
Content-Type: application/json

{
  "score": 8,
  "total_questions": 10,
  "time_taken": "5:30",
  "mode": "ai",
  "sections": "Math",
  "questions": [...]
}
```

### Get Quiz History
```bash
GET /api/v1/history?mode=ai&date=2024-01-01&skip=0&limit=50
```

For complete API documentation, visit: http://127.0.0.1:8000/docs (when running)

## 🗄️ Database Management

### Migration Commands

```bash
# Check database status
python migrate_db.py --check

# Run migrations (updates schema)
python migrate_db.py --migrate

# Create backup
python migrate_db.py --backup

# Initialize fresh database
python migrate_db.py --init
```

### Database Schema

**Quizzes Table**
- `id`: Primary key
- `timestamp`: Quiz completion time
- `score`: Number of correct answers
- `total_questions`: Total questions in quiz
- `time_taken`: Duration in MM:SS format
- `mode`: "ai" or "manual"
- `sections`: Comma-separated list of sections
- `grade_level`: Academic level
- `difficulty`: Easy/Medium/Hard

**Quiz Questions Table**
- `id`: Primary key
- `quiz_id`: Foreign key to quizzes
- `question_text`: The question
- `options`: JSON array of 4 options
- `correct_answer`: The correct option
- `user_answer`: User's selected answer
- `explanation`: Detailed explanation
- `section`: Subject area
- `topic`: Specific topic

## 🎨 Frontend Structure

### Views
- **Setup**: Configure and start new quizzes
- **Quiz**: Interactive quiz-taking interface
- **Results**: Score summary and review
- **History**: Past quiz management
- **Settings**: Configuration management

### Technologies
- **HTML5**: Semantic markup
- **Tailwind CSS**: Utility-first styling
- **Vanilla JavaScript**: No framework dependencies
- **Font Awesome**: Icon library
- **Responsive Design**: Mobile-friendly

## 🔧 Development

### Project Structure
```
Quiz/
├── app/                     # Backend application
│   ├── main.py             # FastAPI entry point
│   ├── config.py           # Configuration management
│   ├── database.py         # Database setup
│   ├── models.py           # SQLAlchemy models
│   ├── schemas.py          # Pydantic schemas
│   ├── api_utils.py        # AI API utilities
│   └── routers/            # API endpoints
├── frontend/               # Frontend files
│   ├── index.html         # Main HTML
│   └── js/app.js          # JavaScript logic
├── migrate_db.py          # Database migration
├── requirements.txt       # Python dependencies
└── .env                   # Environment variables
```

### Adding New Features

1. **Backend Changes**
   - Add new endpoints in `app/routers/`
   - Update schemas in `app/schemas.py`
   - Modify database models in `app/models.py`

2. **Frontend Changes**
   - Update JavaScript in `frontend/js/app.js`
   - Modify HTML in `frontend/index.html`

3. **Database Changes**
   - Update models in `app/models.py`
   - Run `python migrate_db.py --migrate`

### Development Commands
```bash
# Start with auto-reload
uvicorn app.main:app --reload

# Check code quality
python test_imports.py

# Test database
python migrate_db.py --check

# View logs
tail -f quizapp.log  # Linux/Mac
type quizapp.log     # Windows
```

## 🚀 Deployment

### Production Setup

1. **Environment Configuration**
   ```bash
   # Set production environment
   export ENVIRONMENT=production
   export DEBUG=false
   export HOST=0.0.0.0
   ```

2. **Database Setup** (PostgreSQL recommended)
   ```bash
   # Install PostgreSQL adapter
   pip install psycopg2-binary
   
   # Update DATABASE_URL in .env
   DATABASE_URL=postgresql://user:password@localhost/eduquiz
   ```

3. **Run with Gunicorn**
   ```bash
   # Install Gunicorn
   pip install gunicorn
   
   # Start production server
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```

### Docker Deployment (Optional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment-Specific Settings

**.env.production**
```env
ENVIRONMENT=production
DEBUG=false
HOST=0.0.0.0
DATABASE_URL=postgresql://user:password@localhost/eduquiz
LOG_LEVEL=INFO
CORS_ORIGINS=https://yourdomain.com
```

## 🐛 Troubleshooting

### Common Issues

**Import Errors**
```bash
# Fix Pydantic settings import
pip install pydantic-settings

# Test imports
python test_imports.py
```

**Database Issues**
```bash
# Reset database
python migrate_db.py --backup
python migrate_db.py --init
```

**Port Already in Use**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

**API Key Issues**
- Verify API keys are valid and have sufficient credits
- Check API key permissions and rate limits
- Ensure correct provider is selected

### Debug Mode

1. **Enable Debug Logging**
   ```env
   DEBUG=true
   LOG_LEVEL=DEBUG
   ```

2. **Check Logs**
   ```bash
   tail -f quizapp.log
   ```

3. **Test API Endpoints**
   ```bash
   curl http://127.0.0.1:8000/health
   curl http://127.0.0.1:8000/config
   ```

## 📊 Performance Tips

### Optimization
- **Use appropriate question limits** (10-20 for faster generation)
- **Choose efficient AI providers** (Groq is typically fastest)
- **Enable caching** for production environments
- **Use PostgreSQL** for better performance at scale

### Rate Limiting
- **Gemini**: 60 requests per minute (free tier)
- **OpenAI**: Varies by plan and model
- **Groq**: High rate limits, fast responses

## 🤝 Contributing

### Getting Started
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable names
- Add comments for complex logic
- Update documentation for new features

### Testing
```bash
# Test imports and basic functionality
python test_imports.py

# Test database operations
python migrate_db.py --check

# Test API endpoints
curl http://127.0.0.1:8000/health
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FastAPI** - Modern, fast web framework
- **SQLAlchemy** - SQL toolkit and ORM
- **Pydantic** - Data validation using Python type hints
- **Tailwind CSS** - Utility-first CSS framework
- **AI Providers** - Google Gemini, OpenAI, Groq for question generation

## 📞 Support

### Documentation
- **Commands Reference**: See [COMMANDS.md](COMMANDS.md)
- **API Documentation**: http://127.0.0.1:8000/docs (when running)
- **Configuration Guide**: See [Configuration](#configuration) section

### Getting Help
1. Check the troubleshooting section
2. Review the commands documentation
3. Check application logs in `quizapp.log`
4. Test with `python test_imports.py`

### Reporting Issues
When reporting issues, please include:
- Error message and stack trace
- Environment details (OS, Python version)
- Steps to reproduce the issue
- Content of `quizapp.log` file

---

## 🚀 Quick Commands Reference

```bash
# Start development
venv\Scripts\activate
uvicorn app.main:app --reload

# Check status
python migrate_db.py --check
python test_imports.py

# Open application
# http://127.0.0.1:8000
```

---

**Made with ❤️ for education and learning**

For detailed command reference, see [COMMANDS.md](COMMANDS.md)