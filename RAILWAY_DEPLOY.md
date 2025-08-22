# 🚂 Railway Deployment Guide

## ⚡ Quick Deploy Steps:

### 1. **Go to Railway:**
```
https://railway.app
```

### 2. **Login:**
- **Sign Up with GitHub**
- Use same GitHub account that has the repo

### 3. **Create Project:**
- **New Project**
- **Deploy from GitHub repo**
- Select: `jadev-a11y/savolia-monitoring-bot`

### 4. **Railway Auto-Setup:**
✅ Detects Python project  
✅ Installs from `requirements-minimal.txt`  
✅ Runs `python quick_demo_bot.py`  
✅ No sleep mode!  

### 5. **Add Environment Variables:**

Go to **Variables** tab and add:

```env
BOT_TOKEN=8087171595:AAGcTv_TiNAY-Mv8CSyaIwk2tzYnnEM4Dsk
ADMIN_PASSWORD=SavoliaAdmin2025!
RENDER_BACKEND_URL=https://savolia-backend.onrender.com
```

**After getting Render API key add:**
```env
RENDER_API_KEY=rnd_your_render_api_key_here
```

### 6. **Deploy:**
- Railway will auto-deploy from GitHub
- Any push to `main` branch triggers redeploy
- Check **Deployments** tab for status

## 🔧 Railway Features:

### ✅ **Advantages:**
- **500 execution hours/month** free
- **No sleeping** unlike Render free tier
- **Instant deployments** (30 seconds)
- **Real-time logs** and metrics
- **Custom domains** available
- **Database add-ons** (PostgreSQL, Redis)
- **Auto-scaling** 

### 📊 **Monitoring:**
- **Metrics** tab - CPU, RAM, Network
- **Logs** tab - Real-time application logs
- **Deployments** tab - Build and deploy history

### 🌍 **Custom Domain (Optional):**
```
Settings → Domains → Add Custom Domain
your-bot-domain.com
```

## 🚨 **After Deployment:**

### 1. **Test Bot:**
- Find bot in Telegram using token
- Send `/start`
- Send `/auth SavoliaAdmin2025!`
- Try `/render_services` (will show error until API key added)

### 2. **Get Render API Key:**
- Go to dashboard.render.com
- Account Settings → API Keys  
- Generate New API Key
- Add to Railway environment variables as `RENDER_API_KEY`

### 3. **Test Full Functionality:**
- `/render_services` - Should show all 4 services
- `/render_logs` - Should show service logs
- `/render_errors` - Should show error logs
- `/render_status` - Should show system status

## 📈 **Usage Monitoring:**

Railway free tier gives you **500 hours/month**:
- **500 hours = ~20.8 days** of continuous running
- **Perfect for 24/7 bot operation**
- Monitor usage in Railway dashboard

## 🔄 **Auto-Deployments:**

Every `git push` to main branch will:
1. **Trigger build** on Railway
2. **Install dependencies** 
3. **Deploy new version**
4. **Zero downtime** deployment

## 🆘 **Troubleshooting:**

### Build Fails:
- Check **Logs** tab for Python errors
- Verify `requirements-minimal.txt` format
- Check Python version compatibility

### Bot Not Responding:
- Verify `BOT_TOKEN` in environment variables
- Check application logs for Telegram API errors
- Ensure bot is not running elsewhere

### Render Integration Not Working:
- Add `RENDER_API_KEY` environment variable
- Verify API key permissions in Render dashboard
- Check logs for Render API connection errors

---

**🎉 Railway + Savolia Bot = Perfect Match!**

*No more sleeping, reliable 24/7 operation* 🚀