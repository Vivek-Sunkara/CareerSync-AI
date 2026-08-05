# 🤖 ATS Resume Analyzer - Telegram Chatbot

A **production-ready**, **AI-powered** Telegram bot for analyzing resumes against job descriptions. Built for hackathons and real-world use.

## ✨ Features

### 🎯 Core Features
- ✅ **Upload Job Descriptions** - Support PDF, DOCX, TXT formats
- ✅ **Bulk Resume Upload** - Upload multiple resumes at once
- ✅ **AI Analysis** - Smart resume parsing and analysis
- ✅ **Matching Scores** - Rate how well resumes match JD
- ✅ **Improvement Suggestions** - Get specific recommendations
- ✅ **Resume Comparison** - Rank and compare candidates
- ✅ **Information Extraction** - Extract structured data from resumes
- ✅ **Duplicate Detection** - Flag near-identical or repeated resume submissions
- ✅ **Custom Queries** - Ask any question about resumes/JD
- ✅ **All Local Storage** - No external file services needed
- ✅ **100% FREE** - Uses free APIs and services

### 🚀 Technical Highlights
- **AI Engine**: Groq API (fastest free LLM inference)
- **Database**: SQLite (local, fast, reliable)
- **Parser**: Support PDF, DOCX, TXT formats
- **Telegram**: Official python-telegram-bot library
- **Scalable**: Production-ready architecture
- **No Hardcoding**: Smart AI-based analysis, not rules-based

---

## 📊 How It Works

```
User → Telegram → Your Bot → Groq API (LLM) → Analysis → Response
                    ↓
              SQLite Database
              (Stores JD & Resumes)
```

**No External Links**: All file storage happens locally in the bot's database.

---

## 🎮 Quick Demo

```
User: /upload_jd
Bot: "Please upload job description"
User: [uploads job_description.pdf]
Bot: ✅ JD uploaded! Now upload resumes.

User: /upload_resumes
Bot: Please upload resumes (one by one)
User: [uploads resume1.pdf]
User: [uploads resume2.pdf]
User: [uploads resume3.pdf]
User: /done
Bot: ✅ 3 resumes uploaded!

User: /analyze
Bot: 🔍 Analyzing... [Detailed AI analysis]

User: Which resume is best for this job?
Bot: Based on analysis... [Smart comparison]

User: /improvements
Bot: [Specific improvement suggestions for each resume]
```

---

## ⚡ Getting Started (< 10 minutes)

### Prerequisites
- Python 3.8+
- Telegram account
- Free Groq account

### 1️⃣ Get API Keys
```bash
# Telegram Token - Get from @BotFather on Telegram
# Groq API Key - Get from https://console.groq.com
```

### 2️⃣ Install & Setup
```bash
# Clone repo
git clone <repo-url>
cd telegram-ats-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure .env
cp .env.example .env
# Edit .env and add your API keys
```

### 3️⃣ Run
```bash
python main.py
```

### 4️⃣ Test in Telegram
Find your bot and type `/start`

---

## 📱 Available Commands

| Command | Description |
|---------|------------|
| `/start` | Show welcome message |
| `/help` | Show help and all commands |
| `/upload_jd` | Upload job description |
| `/upload_resumes` | Upload resumes (multiple) |
| `/analyze` | Get comprehensive analysis |
| `/improvements` | Get improvement suggestions |
| `/compare` | Compare and rank resumes |
| `/extract` | Extract structured data |
| `/duplicates` | Detect duplicate or near-duplicate resumes |
| `/status` | View uploaded data status |
| `/clear` | Clear all data |

## 💬 Free-Form Queries

You can also ask any question:
```
"Which resume has Python experience?"
"Who has 5+ years of leadership?"
"Which candidate is best fit?"
"Extract all email addresses"
"Compare salary expectations"
```

---

## 🌐 Deployment Options

### Option 1: Local Machine (Recommended for hackathon)
```bash
python main.py
```
Keep terminal running. Bot works only when terminal is open.

### Option 2: Railway (BEST for hackathon)
- Go to https://railway.app
- Connect GitHub
- 1-click deploy
- Bot runs 24/7 for free

### Option 3: Docker
```bash
docker-compose up -d
```

### Option 4: Heroku, Render, or Replit
See `DEPLOYMENT_GUIDE.md` for detailed instructions.

---

## 🔧 Configuration

### Environment Variables (.env)
```
TELEGRAM_TOKEN=your_token_here
GROQ_API_KEY=your_key_here
GROQ_MODEL=mixtral-8x7b-32768
DATABASE_PATH=ats_bot.db
MAX_FILE_SIZE=10485760  # 10MB
GROQ_TIMEOUT=60
```

### Supported File Formats
- ✅ PDF (.pdf)
- ✅ DOCX (.docx)
- ✅ Text (.txt)

### Max File Size
- Default: 10MB
- Configurable in `.env`

---

## 📂 Project Structure

```
telegram-ats-bot/
├── main.py                  # Entry point, all bot handlers
├── config.py               # Configuration & settings
├── database.py             # SQLite database manager
├── document_parser.py      # PDF/DOCX/TXT parser
├── llm_engine.py           # Groq API integration
├── requirements.txt        # Python dependencies
├── .env.example           # Config template
├── .gitignore             # Git ignore rules
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker compose setup
├── DEPLOYMENT_GUIDE.md    # Detailed deployment instructions
└── README.md              # This file
```

---

## 🏗️ Architecture

### Components
1. **Telegram Bot** - Handles user interactions
2. **Document Parser** - Extracts text from documents
3. **LLM Engine** - Groq API for smart analysis
4. **Database** - SQLite for local storage
5. **Config Manager** - Environment and settings

### Data Flow
```
User Input → Telegram Handler → Document Parser
                                      ↓
                                Database (Store)
                                      ↓
                        LLM Engine (Groq API)
                                      ↓
                                   Analysis
                                      ↓
                            Response to User
```

---

## 💰 Cost Breakdown

| Service | Cost | Notes |
|---------|------|-------|
| Telegram Bot | FREE | Unlimited messages |
| Groq API | FREE | 100 req/day free tier |
| SQLite DB | FREE | Local database |
| Railway | FREE | 100 hours/month |
| Total | **$0** | Completely free! |

---

## 🚀 Performance

- **Upload Speed**: Instant (file handling)
- **Analysis Speed**: 2-5 seconds per request
- **API Response**: <3 seconds (Groq is fastest free LLM)
- **Database Queries**: <1 second
- **Concurrent Users**: Unlimited (depends on hosting)

---

## 🔐 Security & Privacy

✅ **Local Storage**
- All resumes and JDs stored locally in SQLite
- No upload to external file services
- Data stays on your server

✅ **API Security**
- Only Groq API gets LLM requests
- `.env` file excluded from Git
- No credentials hardcoded

✅ **Best Practices**
```bash
# Always add to .gitignore
.env
*.db
temp_files/
```

---

## 🐛 Troubleshooting

### Bot not responding?
1. Check `TELEGRAM_TOKEN` in `.env`
2. Make sure bot is running: `python main.py`
3. Verify you're messaging the correct bot

### "API Key not set" error?
1. Create account at https://console.groq.com
2. Generate API key in dashboard
3. Add to `.env`: `GROQ_API_KEY=your_key`

### File upload fails?
1. Check file format (PDF, DOCX, or TXT)
2. Verify file size < 10MB
3. Ensure file is not corrupted

### Database locked error?
```bash
# Stop bot
Ctrl+C

# Remove old database
rm ats_bot.db

# Restart
python main.py
```

### Slow responses?
- Free tier might be slow during peak hours
- Increase timeout: `GROQ_TIMEOUT=120` in `.env`
- Try again in a few seconds

---

## 📚 Usage Examples

### Example 1: Quick Analysis
```
/upload_jd → [upload job_desc.pdf]
/upload_resumes → [upload resume1.pdf, resume2.pdf, resume3.pdf] → /done
/analyze
→ "Resume 1 (John): 85/100 - Strong Python background..."
```

### Example 2: Get Improvements
```
/improvements
→ "Resume 2 (Sarah): Add 'AWS' keyword, expand ML projects..."
```

### Example 3: Custom Query
```
User: "Who has the most DevOps experience?"
Bot: "Based on analysis, Resume 3 (Alex) has strongest DevOps background..."
```

---

## 🎯 For Hackathons

**Why This Bot Is Perfect for Hackathons:**

✅ **Complete** - Everything you need in one project
✅ **Fast** - Deploy in < 10 minutes
✅ **Free** - No cost, no credits needed
✅ **Real** - Production-ready, not a demo
✅ **AI-Powered** - Uses real LLM, not hardcoded logic
✅ **Impressive** - Full-stack application
✅ **Scalable** - Can handle real usage

**Deployment Time**: < 5 minutes on Railway
**Development Time**: Already done! Ready to use

---

## 🔄 What's Included

✅ Complete source code
✅ Dependency management
✅ Configuration template
✅ Database schema
✅ Docker setup
✅ Deployment guides
✅ Comprehensive documentation
✅ Error handling
✅ Logging system
✅ Production-ready

---

## 🚦 Next Steps

1. **Get API keys** (Telegram + Groq)
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Configure**: Copy `.env.example` → `.env`, add keys
4. **Run**: `python main.py`
5. **Test**: Open Telegram, find your bot, type `/start`
6. **Deploy** (optional): Use Railway for 24/7 hosting

---

## 📞 Support

Check the **DEPLOYMENT_GUIDE.md** for:
- Detailed setup instructions
- Deployment options
- Troubleshooting
- Performance optimization

---

## 📄 Requirements

```
python-telegram-bot==20.7    # Telegram bot framework
groq==0.9.0                  # Groq API client
PyPDF2==4.2.0               # PDF parsing
python-docx==0.8.11         # DOCX parsing
python-dotenv==1.0.1        # Environment variables
requests==2.32.3            # HTTP client
aiohttp==3.9.5              # Async HTTP
```

---

## 🎓 Learning Resources

- [Groq Console](https://console.groq.com)
- [Telegram BotFather](https://t.me/BotFather)
- [Python Telegram Bot Docs](https://python-telegram-bot.readthedocs.io/)
- [Railway Deployment](https://railway.app)

---

## 💡 Tips

1. **First Time Setup**: Follow DEPLOYMENT_GUIDE.md step by step
2. **Local Testing**: Always test locally before deploying
3. **API Limits**: Free Groq tier has rate limits, but sufficient for hackathon
4. **Database**: SQLite works great for single-server deployments
5. **Scaling**: For production, consider PostgreSQL + proper hosting

---

## ✅ Deployment Checklist

- [ ] Python 3.8+ installed
- [ ] Telegram bot created (@BotFather)
- [ ] Groq account created
- [ ] API keys obtained
- [ ] Dependencies installed
- [ ] `.env` configured
- [ ] Bot tested locally
- [ ] Code pushed to GitHub (optional)
- [ ] Deployed to Railway/Render/Heroku
- [ ] Bot commands verified
- [ ] Ready for demo!

---

## 🎉 You're All Set!

Your production-ready ATS Resume Analyzer bot is ready to go. Start analyzing resumes! 🚀

**Questions?** Check DEPLOYMENT_GUIDE.md

**Having issues?** See Troubleshooting section above

---

Made with ❤️ for Hackathons | 100% Free | Production Ready
