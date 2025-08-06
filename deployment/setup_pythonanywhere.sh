#!/bin/bash
# Setup script for PythonAnywhere deployment

echo "🚀 Setting up EduQuiz Pro on PythonAnywhere..."

# Create necessary directories
mkdir -p logs
mkdir -p data

# Install Python dependencies
echo "📦 Installing dependencies..."
pip3.10 install --user -r requirements.txt

# Create production environment file
echo "🔧 Creating production environment..."
cat > .env << EOF
ENVIRONMENT=production
DEBUG=False
DATABASE_URL=sqlite:///./quizapp.db
BASE_URL=https://error8149.pythonanywhere.com
ALLOWED_ORIGINS=https://error8149.pythonanywhere.com
LOG_LEVEL=INFO
EOF

# Set permissions
chmod +x deployment/*.sh

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Go to PythonAnywhere Web tab"
echo "2. Create new web app (Manual configuration, Python 3.10)"
echo "3. Set source code to: /home/error8149/eduquiz-pro"
echo "4. Set WSGI file to: /home/error8149/eduquiz-pro/deployment/pythonanywhere_wsgi.py"
echo "5. Add static files mapping:"
echo "   URL: /static/"
echo "   Directory: /home/error8149/eduquiz-pro/frontend/"
echo "6. Click Reload"
echo ""
echo "Your app will be available at: https://error8149.pythonanywhere.com"