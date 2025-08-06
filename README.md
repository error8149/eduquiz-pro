# EduQuiz Pro - AI-Powered Quiz Platform

![Version](https://img.shields.io/badge/version-1.3.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)

EduQuiz Pro is an advanced, AI-powered quiz generation platform that supports multiple AI providers, comprehensive analytics, and both cloud and local AI deployment options.

## 🌟 Features

### 🤖 AI Integration
- **13 AI Providers**: Google Gemini, OpenAI, Groq, DeepSeek, Ollama (local), and more
- **Smart Question Generation**: Web-verified questions with duplicate prevention
- **Multiple Grade Levels**: Elementary to Graduate level content
- **Difficulty Scaling**: Easy, Medium, Hard difficulty levels

### 🎯 Quiz Management
- **AI & Manual Modes**: Generate questions with AI or input manually
- **Real-time Feedback**: Instant explanations and AI assistance
- **Timer & Progress**: Customizable time limits with visual progress
- **Comprehensive Analytics**: Detailed performance tracking

### 📊 Analytics & History
- **Quiz History**: Complete record of all quiz attempts
- **Performance Statistics**: Track improvement over time
- **Export Options**: CSV, JSON, and TXT export formats
- **Filter & Search**: Advanced filtering by date, mode, score

### 🔧 Advanced Features
- **Offline Support**: Service Worker for offline functionality
- **Local AI**: Support for Ollama (no API key required)
- **Customizable Topics**: Manage subjects and topics
- **Settings Sync**: Import/export settings
- **Accessibility**: Screen reader support and keyboard shortcuts

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+ (for development)
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/eduquiz-pro.git
cd eduquiz-pro



venv\Scripts\activate

python -m http.server 3000

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000