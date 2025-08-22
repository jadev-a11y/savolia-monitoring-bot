# 🤖 Savolia AI Advanced Monitoring Bot

> **Real-time monitoring and analytics bot for Savolia AI with Render.com integration**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Telegram Bot API](https://img.shields.io/badge/Telegram%20Bot%20API-20.7-blue.svg)](https://python-telegram-bot.org)
[![Render.com](https://img.shields.io/badge/Render.com-Integration-green.svg)](https://render.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 🚀 Features

### 📊 **Real-time Monitoring**
- **4 Services tracking**: `savolia-web`, `savolia-frontend`, `savolia-backend`, `savolia-bot`
- **Live logs streaming** with error detection
- **Deployment status** monitoring  
- **Automated alerts** for critical issues

### 🔥 **Advanced Analytics**
- **AI-powered log analysis** using GPT
- **Interactive charts** and visualizations
- **Performance metrics** extraction
- **Anomaly detection** algorithms
- **Revenue forecasting** with ML

### 🌍 **Multi-language Support**
- **Uzbek Latin** interface for local team
- **Russian** documentation and responses
- **English** technical logs and errors

## 📱 Bot Commands

### 🔐 Authentication
```bash
/start          # Start the bot
/auth PASSWORD  # Login (Password: SavoliaAdmin2025!)
/help           # Show all commands
```

### 🖥️ Render Monitoring
```bash
/render_services  # List all services  
/render_logs     # View logs by service
/render_errors   # Show only errors
/render_deploy   # Deployment status
/render_status   # System health check
/render_realtime # Real-time error monitoring
```

### 📊 Analytics & AI
```bash
/dashboard      # Main monitoring dashboard
/ai_analysis    # AI-powered insights
/metrics        # System metrics
/charts         # Generate visualizations
/predict        # Revenue forecasting
```

## ⚙️ Quick Setup

### 1. **Clone Repository**
```bash
git clone https://github.com/jadev-a11y/savolia-monitoring-bot.git
cd savolia-monitoring-bot
```

### 2. **Install Dependencies**
```bash
# For quick demo (minimal features)
pip install -r requirements-minimal.txt

# For full version (with AI and charts)  
pip install -r requirements.txt
```

### 3. **Environment Setup**
```bash
cp .env.example .env
# Edit .env with your API keys
```

Required environment variables:
```env
BOT_TOKEN=8087171595:AAGcTv_TiNAY-Mv8CSyaIwk2tzYnnEM4Dsk
RENDER_API_KEY=your_render_api_key_here
OPENAI_API_KEY=your_openai_key_here  # Optional
ADMIN_PASSWORD=SavoliaAdmin2025!
```

### 4. **Get Render API Key**
1. Go to [dashboard.render.com](https://dashboard.render.com/account/settings)
2. Navigate to **Account Settings** → **API Keys**
3. Click **Generate New API Key**
4. Copy key to `.env` file

### 5. **Run Bot**
```bash
# Quick demo version (no heavy dependencies)
python quick_demo_bot.py

# Full featured version
python advanced_bot.py
```

## 🚀 Deploy to Render.com

### 1. **Create New Web Service**
- Repository: `https://github.com/jadev-a11y/savolia-monitoring-bot`
- Environment: `Python 3`
- Build Command: `pip install -r requirements-minimal.txt`
- Start Command: `python quick_demo_bot.py`

### 2. **Environment Variables**
```env
BOT_TOKEN=8087171595:AAGcTv_TiNAY-Mv8CSyaIwk2tzYnnEM4Dsk
RENDER_API_KEY=your_render_api_key
ADMIN_PASSWORD=SavoliaAdmin2025!
RENDER_BACKEND_URL=https://savolia-backend.onrender.com
```

### 3. **Deploy**
- Auto-deployment from GitHub
- Health checks included
- 24/7 monitoring

## 🏗️ Architecture

```
┌─────────────────────┐    ┌──────────────────────┐
│   Telegram Bot      │◄───┤   Render.com API     │
│   (Python 3.11)     │    │   (4 Services)       │
├─────────────────────┤    ├──────────────────────┤
│ • Real-time logs    │    │ • savolia-web        │
│ • Error detection   │    │ • savolia-frontend   │
│ • AI analytics      │    │ • savolia-backend    │
│ • Charts generation │    │ • savolia-bot        │
└─────────────────────┘    └──────────────────────┘
           │
           ▼
┌─────────────────────┐    ┌──────────────────────┐
│   SQLite Database   │    │   OpenAI GPT API     │
│   (Metrics & Logs)  │    │   (AI Analysis)      │
└─────────────────────┘    └──────────────────────┘
```

## 📊 Screenshots

### Service Monitoring Dashboard
```
🖥️ RENDER SERVICES
━━━━━━━━━━━━━━━━━━━━━━━

🟢 savolia-web 🚀
   📋 Type: static_site
   📊 Status: available
   🆔 ID: srv_abc123...

🟢 savolia-backend ⚙️  
   📋 Type: web_service
   📊 Status: available
   🆔 ID: srv_def456...
```

### Real-time Error Alerts
```
🚨 YANGI XATO TOPILDI

🔥 ERROR 18:45:32
```
Connection refused to database
Port 5432 unavailable
```

📧 Service: savolia-backend
⏰ Time: 18:45:32
```

## 🛠️ Development

### Project Structure
```
savolia-monitoring-bot/
├── quick_demo_bot.py          # Lightweight bot (recommended)
├── advanced_bot.py            # Full-featured bot with AI
├── render_logs_viewer.py      # Render API integration
├── telegram-logger-bot.py     # Legacy simple version
├── requirements-minimal.txt   # Basic dependencies
├── requirements.txt           # All dependencies
├── .env.example              # Environment template
├── README.md                 # Detailed documentation  
└── SETUP_GUIDE.md           # Quick setup guide
```

### Key Classes
- `RenderAPIClient` - Render.com API integration
- `SavoliaQuickBot` - Main bot logic (demo version)
- `AdvancedSavoliaBot` - Full bot with AI features
- `TelegramLogFormatter` - Message formatting
- `LogAnalyzer` - Error pattern detection

## 📈 Monitoring Capabilities

### ✅ **What Bot Monitors**
- **Service Health**: Up/Down status for all 4 services
- **Deployment Status**: Success/Failure of deployments  
- **Error Logs**: Real-time ERROR level log detection
- **Performance**: Response times and resource usage
- **Uptime**: Service availability tracking

### 🚨 **Alert Types**
- **Deploy Failed**: Immediate notification when deployment fails
- **Critical Errors**: Server errors (500, 503, timeout)
- **Service Down**: When service becomes unavailable
- **High Error Rate**: When error frequency exceeds threshold

## 🔧 Customization

### Adding New Services
```python
# Bot automatically detects all Render services
# No configuration needed for new services
```

### Custom Alert Rules
```python
# In LogAnalyzer class, modify:
if log.level == 'ERROR' and 'critical' in log.message.lower():
    should_alert = True
    alert_type = "🚨 CRITICAL ERROR"
```

### Language Customization
```python
# In TelegramLogFormatter, modify text templates:
"✅ Muvaffaqiyatli" → Your language
"❌ Xatolik" → Your language  
"🔄 Yangilash" → Your language
```

## 📞 Support & Contact

- **Telegram Bot**: Search for token `8087171595:AAGcTv_TiNAY-Mv8CSyaIwk2tzYnnEM4Dsk`
- **Demo Password**: `SavoliaAdmin2025!`
- **GitHub Issues**: [Create Issue](https://github.com/jadev-a11y/savolia-monitoring-bot/issues)
- **Documentation**: [Setup Guide](SETUP_GUIDE.md)

## 📄 License

MIT License - feel free to use, modify, and distribute.

---

**🚀 Built for Savolia AI - Advanced monitoring made simple**

*Developed with ❤️ using Claude Code*