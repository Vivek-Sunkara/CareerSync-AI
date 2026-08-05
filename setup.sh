#!/bin/bash

# ATS Resume Analyzer Bot - Setup Script
# For Mac, Linux, WSL

echo "🤖 ATS Resume Analyzer Bot - Setup Script"
echo "==========================================="
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "✅ Python $PYTHON_VERSION found"

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "✅ Virtual environment created"
echo ""
echo "🔗 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Dependencies installed"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env created (Please edit and add your API keys)"
else
    echo "✅ .env already exists"
fi

echo ""
echo "==========================================="
echo "✅ Setup Complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your API keys:"
echo "   - TELEGRAM_TOKEN (from @BotFather)"
echo "   - GROQ_API_KEY (from https://console.groq.com)"
echo ""
echo "2. Activate virtual environment (if not already):"
echo "   source venv/bin/activate"
echo ""
echo "3. Run the bot:"
echo "   python main.py"
echo ""
echo "4. Find your bot in Telegram and type /start"
echo ""
echo "==========================================="
