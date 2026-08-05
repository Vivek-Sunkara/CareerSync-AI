@echo off
REM ATS Resume Analyzer Bot - Setup Script for Windows

echo.
echo 🤖 ATS Resume Analyzer Bot - Setup Script
echo ===========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% found

echo.
echo 📦 Creating virtual environment...
python -m venv venv
echo ✅ Virtual environment created

echo.
echo 🔗 Activating virtual environment...
call venv\Scripts\activate.bat

echo 📥 Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
echo ✅ Dependencies installed

echo.
if not exist .env (
    echo 📝 Creating .env file from template...
    copy .env.example .env
    echo ✅ .env created ^(Please edit and add your API keys^)
) else (
    echo ✅ .env already exists
)

echo.
echo ===========================================
echo ✅ Setup Complete!
echo.
echo Next steps:
echo 1. Edit .env file and add your API keys:
echo    - TELEGRAM_TOKEN ^(from @BotFather^)
echo    - GROQ_API_KEY ^(from https://console.groq.com^)
echo.
echo 2. Run this command to activate venv:
echo    venv\Scripts\activate.bat
echo.
echo 3. Run the bot:
echo    python main.py
echo.
echo 4. Find your bot in Telegram and type /start
echo.
echo ===========================================
pause
