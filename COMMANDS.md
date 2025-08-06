# EduQuiz Pro - Command Reference Documentation

## 📋 Table of Contents
- [Environment Setup](#environment-setup)
- [Database Commands](#database-commands)
- [Development Commands](#development-commands)
- [Testing Commands](#testing-commands)
- [Production Commands](#production-commands)
- [Troubleshooting Commands](#troubleshooting-commands)
- [Project Structure](#project-structure)
- [Configuration](#configuration)

---

## 🚀 Environment Setup

### Initial Setup
```bash
# Clone or navigate to project directory
cd D:\projects\Quiz

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Activate virtual environment (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install additional dependency for Pydantic V2
pip install pydantic-settings

# Create environment file
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac
```

### Environment Management
```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Deactivate virtual environment
deactivate

# Check installed packages
pip list

# Update pip
python -m pip install --upgrade pip

# Install new package and update requirements
pip install package_name
pip freeze > requirements.txt
```

---

## 🗄️ Database Commands

### Migration Commands
```bash
# Check database status
python migrate_db.py --check

# Run database migrations
python migrate_db.py --migrate

# Create database backup
python migrate_db.py --backup

# Initialize fresh database
python migrate_db.py --init

# Test imports and configuration
python test_imports.py
```

### Database Operations
```bash
# Backup database manually
copy quizapp.db quizapp.db.backup  # Windows
cp quizapp.db quizapp.db.backup    # Linux/Mac

# View database content (if SQLite Browser installed)
sqlitebrowser quizapp.db

# Delete database (start fresh)
del quizapp.db  # Windows
rm quizapp.db   # Linux/Mac
```

---

## 💻 Development Commands

### Running the Application
```bash
# Start development server (basic)
uvicorn app.main:app --host 127.0.0.1 --port 8000

# Start with reload (recommended for development)
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Start with debug logging
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload --log-level debug

# Start on different port
uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload

# Start accessible from all interfaces
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Development Utilities
```bash
# Check code formatting with black (if installed)
black app/ --check

# Format code with black
black app/

# Check imports with isort (if installed)
isort app/ --check-only

# Fix imports with isort
isort app/

# Type checking with mypy (if installed)
mypy app/
```

---

## 🧪 Testing Commands

### Basic Testing
```bash
# Test basic imports
python test_imports.py

# Test API endpoints
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/config

# Test with httpie (if installed)
http GET http://127.0.0.1:8000/health
http GET http://127.0.0.1:8000/config
```

### Advanced Testing (if pytest is set up)
```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run specific test file
pytest tests/test_api.py

# Run tests with coverage
pytest --cov=app tests/
```

---

## 🚀 Production Commands

### Environment Configuration
```bash
# Set production environment
set ENVIRONMENT=production  # Windows
export ENVIRONMENT=production  # Linux/Mac

# Set debug mode off
set DEBUG=false  # Windows
export DEBUG=false  # Linux/Mac
```

### Production Deployment
```bash
# Run with Gunicorn (Linux/Mac)
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Run with production settings
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Run as background process (Linux/Mac)
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Check if process is running
ps aux | grep uvicorn  # Linux/Mac
tasklist | findstr python  # Windows
```

### Process Management
```bash
# Kill process by port (Windows)
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Kill process by port (Linux/Mac)
lsof -ti:8000 | xargs kill -9

# View application logs
tail -f quizapp.log  # Linux/Mac
type quizapp.log     # Windows
```

---

## 🔧 Troubleshooting Commands

### Common Issues
```bash
# Check Python version
python --version

# Check pip version
pip --version

# Check if virtual environment is active
echo $VIRTUAL_ENV  # Linux/Mac
echo %VIRTUAL_ENV%  # Windows

# Reinstall dependencies
pip uninstall -r requirements.txt -y
pip install -r requirements.txt

# Clear pip cache
pip cache purge

# Check port usage
netstat -ano | findstr :8000  # Windows
lsof -i :8000  # Linux/Mac
```

### Import/Module Issues
```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Test specific imports
python -c "import app.config; print('Config OK')"
python -c "import app.database; print('Database OK')"
python -c "import pydantic_settings; print('Pydantic Settings OK')"

# Check installed packages
pip show pydantic
pip show pydantic-settings
pip show fastapi
```

### Database Issues
```bash
# Check database file exists
dir quizapp.db  # Windows
ls -la quizapp.db  # Linux/Mac

# Check database permissions
icacls quizapp.db  # Windows
ls -la quizapp.db  # Linux/Mac

# Test database connection
python -c "from app.database import engine; engine.connect(); print('DB OK')"
```

---

## 📁 Project Structure

```
Quiz/
├── app/                          # Main application package
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # FastAPI application entry point
│   ├── config.py                # Configuration settings
│   ├── database.py              # Database connection and setup
│   ├── models.py                # SQLAlchemy models
│   ├── schemas.py               # Pydantic schemas
│   ├── crud.py                  # Database operations
│   ├── api_utils.py             # AI API utilities
│   ├── base.py                  # SQLAlchemy base
│   └── routers/                 # API route handlers
│       ├── __init__.py
│       ├── quiz_router.py       # Quiz-related endpoints
│       ├── history.py           # History endpoints
│       └── error_router.py      # Error logging endpoints
├── frontend/                    # Frontend files
│   ├── index.html              # Main HTML file
│   └── js/
│       └── app.js              # Frontend JavaScript
├── venv/                       # Virtual environment (auto-generated)
├── migrate_db.py               # Database migration script
├── test_imports.py             # Import testing script
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables
├── .env.example                # Environment template
├── quizapp.db                  # SQLite database (auto-generated)
└── quizapp.log                 # Application logs (auto-generated)
```

---

## ⚙️ Configuration

### Environment Variables (.env file)
```bash
# View current configuration
python -c "from app.config import settings; print(f'Env: {settings.ENVIRONMENT}, Debug: {settings.DEBUG}, DB: {settings.DATABASE_URL}')"

# Edit environment file
notepad .env  # Windows
nano .env     # Linux/Mac
```

### Common .env Settings
```env
# Development
ENVIRONMENT=development
DEBUG=true
HOST=127.0.0.1
PORT=8000
DATABASE_URL=sqlite:///./quizapp.db
LOG_LEVEL=DEBUG

# Production
ENVIRONMENT=production
DEBUG=false
HOST=0.0.0.0
PORT=8000
DATABASE_URL=postgresql://user:password@localhost/eduquiz
LOG_LEVEL=INFO
```

---

## 🔍 Quick Reference Commands

### Daily Development Workflow
```bash
# 1. Activate environment
venv\Scripts\activate

# 2. Check database
python migrate_db.py --check

# 3. Start development server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# 4. Open browser to: http://127.0.0.1:8000
```

### Quick Fixes
```bash
# Fix import errors
pip install pydantic-settings

# Fix database errors
python migrate_db.py --migrate

# Fix port in use
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Reset everything
deactivate
rmdir /s venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python migrate_db.py --init
```

### Health Checks
```bash
# Check if everything is working
python test_imports.py
python migrate_db.py --check
curl http://127.0.0.1:8000/health
```

---

## 📚 Additional Commands

### Package Management
```bash
# Update all packages
pip list --outdated
pip install --upgrade package_name

# Create requirements file
pip freeze > requirements.txt

# Install from requirements
pip install -r requirements.txt

# Uninstall package
pip uninstall package_name
```

### Git Commands (if using Git)
```bash
# Initialize repository
git init

# Add files
git add .

# Commit changes
git commit -m "Initial commit"

# Check status
git status

# View changes
git diff
```

---

## 🆘 Emergency Commands

### Complete Reset
```bash
# Stop all Python processes
taskkill /f /im python.exe  # Windows
pkill -f python             # Linux/Mac

# Remove virtual environment
rmdir /s venv  # Windows
rm -rf venv    # Linux/Mac

# Remove database
del quizapp.db  # Windows
rm quizapp.db   # Linux/Mac

# Start fresh
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python migrate_db.py --init
```

### Backup Everything
```bash
# Create backup folder
mkdir backup_$(date +%Y%m%d)  # Linux/Mac
mkdir backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%  # Windows

# Copy important files
copy quizapp.db backup/  # Windows
copy .env backup/
cp quizapp.db backup/   # Linux/Mac
cp .env backup/
```

---

Save this documentation as `COMMANDS.md` in your project root for easy reference! 📖