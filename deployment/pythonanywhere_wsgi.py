"""
WSGI configuration for EduQuiz Pro on PythonAnywhere
"""
import os
import sys

# Add your project directory to Python path
# IMPORTANT: Replace 'error8149' with your actual username if different
path = '/home/error8149/eduquiz-pro'
if path not in sys.path:
    sys.path.insert(0, path)

# Set production environment variables
os.environ.setdefault('ENVIRONMENT', 'production')
os.environ.setdefault('DEBUG', 'False')
os.environ.setdefault('DATABASE_URL', 'sqlite:///./quizapp.db')
os.environ.setdefault('BASE_URL', 'https://error8149.pythonanywhere.com')
os.environ.setdefault('ALLOWED_ORIGINS', 'https://error8149.pythonanywhere.com')

# Import FastAPI app
from app.main import app

# WSGI application
application = app