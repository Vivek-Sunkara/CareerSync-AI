#!/usr/bin/env python3
"""
ATS Bot - Setup Test Script
Verify all configurations and dependencies before running
"""

import sys
import os
from pathlib import Path

def test_python_version():
    """Test Python version"""
    print("🔍 Testing Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor} (OK)")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor} (Need 3.8+)")
        return False

def test_imports():
    """Test all required imports"""
    print("\n🔍 Testing dependencies...")
    
    dependencies = {
        'telegram': 'python-telegram-bot',
        'groq': 'groq',
        'PyPDF2': 'PyPDF2',
        'docx': 'python-docx',
        'dotenv': 'python-dotenv'
    }
    
    all_ok = True
    for module, package_name in dependencies.items():
        try:
            __import__(module)
            print(f"✅ {package_name} - Installed")
        except ImportError:
            print(f"❌ {package_name} - NOT installed")
            all_ok = False
    
    return all_ok

def test_env_file():
    """Test .env file"""
    print("\n🔍 Testing configuration file...")
    
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        print("   Solution: cp .env.example .env")
        return False
    
    print("✅ .env file exists")
    
    # Check required keys
    from dotenv import load_dotenv
    load_dotenv()
    
    required_keys = ['TELEGRAM_TOKEN', 'GROQ_API_KEY']
    all_ok = True
    
    for key in required_keys:
        value = os.getenv(key, '')
        if value:
            if len(value) > 10:
                masked_value = value[:10] + '...'
            else:
                masked_value = value
            print(f"✅ {key} - Found ({masked_value})")
        else:
            print(f"❌ {key} - NOT set")
            all_ok = False
    
    return all_ok

def test_config():
    """Test configuration loading"""
    print("\n🔍 Testing configuration module...")
    
    try:
        from config import Config
        Config.validate()
        print("✅ Configuration valid")
        return True
    except ValueError as e:
        print(f"❌ Configuration error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Error loading config: {str(e)}")
        return False

def test_database():
    """Test database initialization"""
    print("\n🔍 Testing database...")
    
    try:
        from database import Database
        db = Database(":memory:")  # Use in-memory DB for testing
        stats = db.get_stats()
        print("✅ Database initialized")
        print(f"   - JD count: {stats.get('jd_count', 0)}")
        print(f"   - Resume count: {stats.get('resume_count', 0)}")
        return True
    except Exception as e:
        print(f"❌ Database error: {str(e)}")
        return False

def test_document_parser():
    """Test document parser"""
    print("\n🔍 Testing document parser...")
    
    try:
        from document_parser import DocumentParser
        supported = DocumentParser.SUPPORTED_FORMATS
        print(f"✅ Document parser ready")
        print(f"   - Supported formats: {supported}")
        return True
    except Exception as e:
        print(f"❌ Document parser error: {str(e)}")
        return False

def test_llm_engine():
    """Test LLM engine"""
    print("\n🔍 Testing LLM engine...")
    
    try:
        from llm_engine import LLMEngine
        llm = LLMEngine()
        print(f"✅ LLM engine initialized")
        print(f"   - Model: {llm.model}")
        print(f"   - API: Groq")
        return True
    except ValueError as e:
        print(f"❌ LLM engine error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ LLM engine error: {str(e)}")
        return False

def test_telegram_token():
    """Test Telegram bot token format"""
    print("\n🔍 Testing Telegram token...")
    
    try:
        from config import Config
        token = Config.TELEGRAM_TOKEN
        
        if not token:
            print("❌ TELEGRAM_TOKEN not set")
            return False
        
        # Check token format (should have colon)
        if ':' not in token:
            print("❌ Invalid token format (should contain ':')")
            return False
        
        print(f"✅ Telegram token format valid")
        return True
    except Exception as e:
        print(f"❌ Token error: {str(e)}")
        return False

def test_groq_token():
    """Test Groq API token format"""
    print("\n🔍 Testing Groq API token...")
    
    try:
        from config import Config
        token = Config.GROQ_API_KEY
        
        if not token:
            print("❌ GROQ_API_KEY not set")
            return False
        
        if len(token) < 10:
            print("❌ Invalid Groq token (too short)")
            return False
        
        print(f"✅ Groq API token format valid")
        return True
    except Exception as e:
        print(f"❌ Groq token error: {str(e)}")
        return False

def test_file_structure():
    """Test project file structure"""
    print("\n🔍 Testing file structure...")
    
    required_files = [
        'main.py',
        'config.py',
        'database.py',
        'document_parser.py',
        'llm_engine.py',
        'requirements.txt',
        '.env.example'
    ]
    
    all_ok = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING")
            all_ok = False
    
    return all_ok

def main():
    """Run all tests"""
    print("=" * 50)
    print("🤖 ATS Bot - Setup Verification")
    print("=" * 50)
    
    results = []
    
    # Run all tests
    results.append(("Python Version", test_python_version()))
    results.append(("Dependencies", test_imports()))
    results.append(("File Structure", test_file_structure()))
    results.append((".env File", test_env_file()))
    results.append(("Configuration", test_config()))
    results.append(("Telegram Token", test_telegram_token()))
    results.append(("Groq Token", test_groq_token()))
    results.append(("Database", test_database()))
    results.append(("Document Parser", test_document_parser()))
    results.append(("LLM Engine", test_llm_engine()))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("\n" + "=" * 50)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 50)
    
    if passed == total:
        print("\n🎉 All tests passed! Ready to run:")
        print("   python main.py")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check errors above.")
        print("\nCommon fixes:")
        print("1. Missing dependencies? Run: pip install -r requirements.txt")
        print("2. Missing .env? Run: cp .env.example .env")
        print("3. Missing API keys? Add them to .env file")
        return 1

if __name__ == '__main__':
    sys.exit(main())
