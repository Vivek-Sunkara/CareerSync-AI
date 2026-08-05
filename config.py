"""
Configuration management for ATS Bot
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration class"""
    
    # Telegram Bot Token
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '')
    
    # Groq API Key
    GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
    
    # Groq Model
    GROQ_MODEL = os.getenv('GROQ_MODEL', 'mixtral-8x7b-32768')  # Free Groq model
    
    # Database
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'ats_bot.db')
    
    # Temp files
    TEMP_DIR = os.getenv('TEMP_DIR', 'temp_files')
    
    # Resume image storage
    IMAGE_DIR = os.getenv('IMAGE_DIR', 'resume_images')
    
    # Max file size (10MB)
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 10 * 1024 * 1024))
    
    # Groq API timeout
    GROQ_TIMEOUT = int(os.getenv('GROQ_TIMEOUT', 60))
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        if not cls.TELEGRAM_TOKEN:
            raise ValueError("❌ TELEGRAM_TOKEN not set. Copy .env.example to .env and add your Telegram bot token.")
        if not cls.GROQ_API_KEY:
            raise ValueError("❌ GROQ_API_KEY not set. Copy .env.example to .env and add your Groq API key.")
        return True
    
    @classmethod
    def get_config_status(cls):
        """Get configuration status"""
        return {
            'telegram_token': '✅' if cls.TELEGRAM_TOKEN else '❌',
            'groq_api_key': '✅' if cls.GROQ_API_KEY else '❌',
            'database': cls.DATABASE_PATH,
            'model': cls.GROQ_MODEL
        }
