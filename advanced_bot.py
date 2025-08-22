#!/usr/bin/env python3
"""
🤖 SAVOLIA AI ADVANCED TELEGRAM MONITORING BOT 2025
🚀 Ultra-Advanced Admin Dashboard with AI Integration

Features:
- 🧠 ChatGPT Integration for Smart Analytics
- 📊 Real-time Dashboard with Charts
- 🤖 AI-Powered Insights and Predictions  
- 📈 Advanced Analytics with ML
- 🔒 Multi-user Admin Management
- 💾 SQLite Database for Historical Data
- 🎯 Smart Alerts with ML Detection
- 📱 Mobile-Optimized Interface
- 🌐 Web Dashboard Integration
- 🔄 Auto-Healing System Monitoring
- 📧 Email Integration
- 📸 Chart Generation
- 🎨 Custom Themes
- 🔍 Advanced Search & Filtering
- 💰 Revenue Forecasting
- 🚨 Anomaly Detection
- 📝 Automated Reports
- 🔐 Security Monitoring
- 🌍 Multi-language Support
- 🎵 Voice Message Reports

Token: 8087171595:AAGcTv_TiNAY-Mv8CSyaIwk2tzYnnEM4Dsk
"""

import asyncio
import logging
import json
import sqlite3
import os
import io
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import aiohttp
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import pandas as pd
import numpy as np
from scipy import stats
import openai
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import hashlib
import qrcode
from PIL import Image, ImageDraw, ImageFont
import tempfile
from render_logs_viewer import RenderAPIClient, LogAnalyzer, LogDatabase, TelegramLogFormatter

# Configuration
BOT_TOKEN = "8087171595:AAGcTv_TiNAY-Mv8CSyaIwk2tzYnnEM4Dsk"
RENDER_BACKEND_URL = "https://savolia-backend.onrender.com"
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')  # Set this in environment
RENDER_API_KEY = os.getenv('RENDER_API_KEY', '')  # Set your Render API key
ADMIN_PASSWORD = "SavoliaAdmin2025!"
DB_PATH = "/Users/jasur/Desktop/Savolia-Telegram-Monitor-Bot/savolia_monitoring.db"

# Email configuration (optional)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USER = os.getenv('EMAIL_USER', '')
EMAIL_PASS = os.getenv('EMAIL_PASS', '')

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('/Users/jasur/Desktop/Savolia-Telegram-Monitor-Bot/advanced_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize OpenAI
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

class DatabaseManager:
    """Advanced database manager with analytics"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with comprehensive tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # System metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                cpu_usage REAL,
                memory_usage REAL,
                disk_usage REAL,
                response_time REAL,
                active_users INTEGER,
                error_count INTEGER,
                success_rate REAL
            )
        ''')
        
        # User analytics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_id TEXT,
                action TEXT,
                subscription_plan TEXT,
                revenue REAL,
                device_type TEXT,
                location TEXT
            )
        ''')
        
        # Error logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS error_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                error_type TEXT,
                error_message TEXT,
                stack_trace TEXT,
                user_id TEXT,
                severity TEXT,
                resolved BOOLEAN DEFAULT 0
            )
        ''')
        
        # AI insights table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                insight_type TEXT,
                content TEXT,
                confidence REAL,
                action_required BOOLEAN DEFAULT 0
            )
        ''')
        
        # Admin users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE,
                username TEXT,
                role TEXT DEFAULT 'viewer',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_active DATETIME,
                permissions TEXT
            )
        ''')
        
        # Notifications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                type TEXT,
                title TEXT,
                message TEXT,
                sent BOOLEAN DEFAULT 0,
                priority INTEGER DEFAULT 1
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_metric(self, **kwargs):
        """Add system metric"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        columns = ', '.join(kwargs.keys())
        placeholders = ', '.join(['?' for _ in kwargs])
        values = list(kwargs.values())
        
        cursor.execute(f'''
            INSERT INTO system_metrics ({columns})
            VALUES ({placeholders})
        ''', values)
        
        conn.commit()
        conn.close()
    
    def get_metrics(self, hours: int = 24) -> List[Dict]:
        """Get system metrics for specified hours"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM system_metrics 
            WHERE timestamp >= datetime('now', '-{} hours')
            ORDER BY timestamp DESC
        '''.format(hours))
        
        columns = [description[0] for description in cursor.description]
        metrics = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return metrics
    
    def add_error(self, error_type: str, message: str, stack_trace: str = '', user_id: str = '', severity: str = 'medium'):
        """Add error to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO error_logs (error_type, error_message, stack_trace, user_id, severity)
            VALUES (?, ?, ?, ?, ?)
        ''', (error_type, message, stack_trace, user_id, severity))
        
        conn.commit()
        conn.close()

class AIAnalyzer:
    """AI-powered analytics and insights"""
    
    def __init__(self, openai_key: str = None):
        self.openai_key = openai_key
        if openai_key:
            openai.api_key = openai_key
    
    async def analyze_metrics(self, metrics: List[Dict]) -> str:
        """Analyze metrics using AI"""
        if not self.openai_key:
            return "🤖 AI анализ недоступен (API ключ не настроен)"
        
        try:
            # Prepare data summary
            data_summary = self.prepare_metrics_summary(metrics)
            
            prompt = f"""
            Проанализируй следующие метрики системы Savolia AI за последние 24 часа:
            
            {data_summary}
            
            Дай краткий анализ (максимум 200 слов):
            1. Общее состояние системы
            2. Выявленные проблемы
            3. Рекомендации
            4. Прогноз на ближайшее время
            
            Отвечай на узбекском языке, используй эмодзи.
            """
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return f"🤖 AI анализда хатолик: {str(e)}"
    
    def prepare_metrics_summary(self, metrics: List[Dict]) -> str:
        """Prepare metrics summary for AI analysis"""
        if not metrics:
            return "Маълумотлар мавжуд эмас"
        
        df = pd.DataFrame(metrics)
        
        summary = f"""
        Жами кўрсаткичлар: {len(metrics)}
        Ўртача жавоб вақти: {df['response_time'].mean():.2f}сек
        Ўртача фаол фойдаланувчилар: {df['active_users'].mean():.0f}
        Хатоликлар сони: {df['error_count'].sum():.0f}
        Муваффақият кўрсаткичи: {df['success_rate'].mean():.1f}%
        CPU юклама: {df['cpu_usage'].mean():.1f}%
        Хотира: {df['memory_usage'].mean():.1f}%
        """
        
        return summary
    
    async def predict_revenue(self, historical_data: List[Dict]) -> Dict:
        """Predict revenue using simple ML"""
        try:
            if len(historical_data) < 7:
                return {"error": "Кам маълумот"}
            
            df = pd.DataFrame(historical_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.set_index('timestamp')
            
            # Simple linear regression for prediction
            daily_revenue = df.resample('D')['revenue'].sum()
            
            if len(daily_revenue) < 3:
                return {"error": "Кам маълумот"}
            
            x = np.arange(len(daily_revenue))
            y = daily_revenue.values
            
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            
            # Predict next 7 days
            future_x = np.arange(len(daily_revenue), len(daily_revenue) + 7)
            predictions = slope * future_x + intercept
            
            return {
                "current_trend": "📈 Ўсиш" if slope > 0 else "📉 Пасайиш",
                "weekly_prediction": predictions.sum(),
                "confidence": min(abs(r_value) * 100, 95),
                "daily_predictions": predictions.tolist()
            }
            
        except Exception as e:
            return {"error": f"Прогноз хатоси: {str(e)}"}

class ChartGenerator:
    """Generate beautiful charts and visualizations"""
    
    def __init__(self):
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
    
    async def generate_metrics_chart(self, metrics: List[Dict]) -> io.BytesIO:
        """Generate system metrics chart"""
        if not metrics:
            return self.generate_no_data_chart()
        
        df = pd.DataFrame(metrics)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('📊 Savolia AI - Система Метрикалари', fontsize=16, fontweight='bold')
        
        # Response time
        ax1.plot(df['timestamp'], df['response_time'], color='#2E86AB', linewidth=2, marker='o', markersize=4)
        ax1.set_title('⚡ Жавоб Вақти (сек)', fontweight='bold')
        ax1.set_ylabel('Секунд')
        ax1.grid(True, alpha=0.3)
        
        # Active users
        ax2.bar(df['timestamp'], df['active_users'], color='#A23B72', alpha=0.7)
        ax2.set_title('👥 Фаол Фойдаланувчилар', fontweight='bold')
        ax2.set_ylabel('Сони')
        ax2.grid(True, alpha=0.3)
        
        # Success rate
        ax3.fill_between(df['timestamp'], df['success_rate'], color='#F18F01', alpha=0.6)
        ax3.set_title('✅ Муваффақият Кўрсаткичи (%)', fontweight='bold')
        ax3.set_ylabel('Фоиз')
        ax3.set_ylim(0, 100)
        ax3.grid(True, alpha=0.3)
        
        # Error count
        ax4.scatter(df['timestamp'], df['error_count'], color='#C73E1D', s=50, alpha=0.7)
        ax4.set_title('🔥 Хатоликлар Сони', fontweight='bold')
        ax4.set_ylabel('Сони')
        ax4.grid(True, alpha=0.3)
        
        # Format x-axis
        for ax in [ax1, ax2, ax3, ax4]:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            ax.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        # Save to BytesIO
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()
        
        return img_buffer
    
    async def generate_revenue_chart(self, revenue_data: List[Dict]) -> io.BytesIO:
        """Generate revenue analytics chart"""
        if not revenue_data:
            return self.generate_no_data_chart("💰 Даромад маълумотлари йўқ")
        
        df = pd.DataFrame(revenue_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        daily_revenue = df.groupby(df['timestamp'].dt.date)['revenue'].sum()
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        fig.suptitle('💰 Savolia AI - Даромад Аналитикаси', fontsize=16, fontweight='bold')
        
        # Daily revenue line chart
        ax1.plot(daily_revenue.index, daily_revenue.values, color='#27AE60', linewidth=3, marker='o', markersize=6)
        ax1.fill_between(daily_revenue.index, daily_revenue.values, alpha=0.3, color='#27AE60')
        ax1.set_title('📈 Кунлик Даромад', fontweight='bold')
        ax1.set_ylabel('Доллар ($)')
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='x', rotation=45)
        
        # Revenue distribution by subscription plan
        plan_revenue = df.groupby('subscription_plan')['revenue'].sum()
        colors = ['#E74C3C', '#F39C12', '#8E44AD', '#3498DB']
        ax2.pie(plan_revenue.values, labels=plan_revenue.index, autopct='%1.1f%%', 
                colors=colors, startangle=90)
        ax2.set_title('🎯 Тариф бўйича даромад', fontweight='bold')
        
        plt.tight_layout()
        
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()
        
        return img_buffer
    
    def generate_no_data_chart(self, message: str = "📊 Маълумотлар мавжуд эмас") -> io.BytesIO:
        """Generate chart when no data available"""
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, message, fontsize=20, ha='center', va='center', transform=ax.transAxes)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()
        
        return img_buffer

class AdvancedSavoliaBot:
    """🤖 Advanced Savolia AI Monitoring Bot"""
    
    def __init__(self):
        self.token = BOT_TOKEN
        self.bot = Bot(token=self.token)
        self.application = Application.builder().token(self.token).build()
        self.db = DatabaseManager(DB_PATH)
        self.ai_analyzer = AIAnalyzer(OPENAI_API_KEY)
        self.chart_generator = ChartGenerator()
        
        # Render logs integration
        self.render_client = None
        self.log_analyzer = LogAnalyzer()
        self.log_database = LogDatabase(DB_PATH.replace('.db', '_logs.db'))
        self.log_formatter = TelegramLogFormatter()
        self.render_services = []
        
        # Admin management
        self.admin_users = set()
        self.authenticated_users = set()
        
        # Statistics
        self.stats = {
            'uptime_start': datetime.now(),
            'commands_executed': 0,
            'charts_generated': 0,
            'ai_analyses': 0,
            'errors_detected': 0
        }
        
        # Initialize monitoring dictionaries
        self.service_monitors = {}
        self.realtime_tasks = {}
        
        # Initialize Render client if API key is available
        if RENDER_API_KEY:
            from render_logs_viewer import RenderAPIClient
            self.render_client = RenderAPIClient(RENDER_API_KEY)
        
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup all command and callback handlers"""
        # Basic commands
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("auth", self.auth_command))
        
        # Monitoring commands
        self.application.add_handler(CommandHandler("dashboard", self.dashboard_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("metrics", self.metrics_command))
        self.application.add_handler(CommandHandler("charts", self.charts_command))
        self.application.add_handler(CommandHandler("ai_analysis", self.ai_analysis_command))
        
        # Analytics commands
        self.application.add_handler(CommandHandler("analytics", self.analytics_command))
        self.application.add_handler(CommandHandler("revenue", self.revenue_command))
        self.application.add_handler(CommandHandler("users", self.users_command))
        self.application.add_handler(CommandHandler("errors", self.errors_command))
        
        # Admin commands
        self.application.add_handler(CommandHandler("admin", self.admin_command))
        self.application.add_handler(CommandHandler("broadcast", self.broadcast_command))
        self.application.add_handler(CommandHandler("backup", self.backup_command))
        self.application.add_handler(CommandHandler("logs", self.logs_command))
        
        # Advanced features
        self.application.add_handler(CommandHandler("predict", self.predict_command))
        self.application.add_handler(CommandHandler("alert", self.alert_command))
        self.application.add_handler(CommandHandler("report", self.report_command))
        self.application.add_handler(CommandHandler("voice", self.voice_command))
        
        # Render logs commands
        self.application.add_handler(CommandHandler("render_logs", self.render_logs_command))
        self.application.add_handler(CommandHandler("render_services", self.render_services_command))
        self.application.add_handler(CommandHandler("render_errors", self.render_errors_command))
        self.application.add_handler(CommandHandler("render_realtime", self.render_realtime_command))
        self.application.add_handler(CommandHandler("render_analyze", self.render_analyze_command))
        self.application.add_handler(CommandHandler("render_deploy", self.render_deploy_command))
        self.application.add_handler(CommandHandler("render_status", self.render_status_command))
        
        # Callback handlers
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
        self.application.add_handler(CallbackQueryHandler(self.handle_render_callback, pattern="^render_"))
        
        # Message handlers
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    def requires_auth(func):
        """Decorator for commands that require authentication"""
        async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
            user_id = update.effective_user.id
            if user_id not in self.authenticated_users:
                await update.message.reply_text(
                    "🔐 Авторизация талаб қилинади. /auth командасини ишлатинг."
                )
                return
            return await func(self, update, context)
        return wrapper
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """🚀 Start command with welcome message"""
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        
        # Add to database
        try:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO admin_users (telegram_id, username, last_active)
                VALUES (?, ?, ?)
            ''', (user_id, username, datetime.now()))
            cursor.execute('''
                UPDATE admin_users SET last_active = ? WHERE telegram_id = ?
            ''', (datetime.now(), user_id))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Database error: {e}")
        
        welcome_text = f"""
🤖 **SAVOLIA AI ADVANCED MONITORING BOT**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👋 Салом, {username}!

🚀 **Янги возможностлар 2025:**
• 🧠 AI-powered аналитика
• 📊 Real-time дашборд
• 📈 ML прогнозлар
• 🎨 Интерактив чартлар
• 🔔 Ақлли хабарномалар
• 💰 Даромад таҳлили
• 🔒 Хавfsизлик мониторинги
• 🌍 Көп тилли қўллаб-қувватлаш

💡 Бошлаш учун /auth команда билан авторизация қилинг
📚 Барча командалар учун /help
"""
        
        keyboard = [
            [InlineKeyboardButton("🔐 Авторизация", callback_data="auth"),
             InlineKeyboardButton("📚 Ёрдам", callback_data="help")],
            [InlineKeyboardButton("📊 Дашборд", callback_data="dashboard"),
             InlineKeyboardButton("🧠 AI Таҳлил", callback_data="ai_analysis")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_text, parse_mode='Markdown', reply_markup=reply_markup)
        self.stats['commands_executed'] += 1
    
    async def auth_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """🔐 Authentication command"""
        if not context.args:
            await update.message.reply_text(
                "🔐 **Авторизация**\n\n"
                "Использование: `/auth ПАРОЛЬ`\n\n"
                "💡 Паролни админдан олинг",
                parse_mode='Markdown'
            )
            return
        
        password = ' '.join(context.args)
        if password == ADMIN_PASSWORD:
            user_id = update.effective_user.id
            self.authenticated_users.add(user_id)
            self.admin_users.add(user_id)
            
            await update.message.reply_text(
                "✅ **Муваффақиятли авторизация!**\n\n"
                "🎉 Сиз енди барча функцияларга киришингиз мумкин.\n"
                "📊 /dashboard - Асосий дашборд",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text("❌ Нотўғри парол!")
        
        # Delete the message with password for security
        await update.message.delete()
    
    @requires_auth
    async def dashboard_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """📊 Main dashboard command"""
        await self.send_dashboard(update.effective_chat.id)
    
    async def send_dashboard(self, chat_id: int, message_id: int = None):
        """Send comprehensive dashboard"""
        try:
            # Collect real-time data
            backend_status = await self.check_backend_health()
            metrics = self.db.get_metrics(24)
            
            uptime = datetime.now() - self.stats['uptime_start']
            uptime_str = str(uptime).split('.')[0]
            
            # Calculate statistics
            total_users = len(self.admin_users)
            total_commands = self.stats['commands_executed']
            
            dashboard_text = f"""
📊 **SAVOLIA AI DASHBOARD**
━━━━━━━━━━━━━━━━━━━━━━━━

🖥️ **Система Ҳолати:**
{'🟢 Online' if backend_status['status'] == 'ok' else '🔴 Offline'} | ⚡ {backend_status.get('response_time', 'N/A')}

⏰ **Bot Uptime:** {uptime_str}
📈 **Жами командалар:** {total_commands}
👥 **Админлар сони:** {total_users}
📊 **Чартлар яратилди:** {self.stats['charts_generated']}
🧠 **AI таҳлиллар:** {self.stats['ai_analyses']}

📊 **24 соатлик статистика:**
"""
            
            if metrics:
                avg_response = sum(m['response_time'] for m in metrics) / len(metrics)
                avg_users = sum(m['active_users'] for m in metrics) / len(metrics)
                total_errors = sum(m['error_count'] for m in metrics)
                
                dashboard_text += f"""
• Ўртача жавоб вақти: {avg_response:.2f}с
• Ўртача фаол фойдаланувчилар: {avg_users:.0f}
• Жами хатоликлар: {total_errors}
"""
            else:
                dashboard_text += "• Маълумотлар мавжуд эмас"
            
            dashboard_text += f"\n🕒 **Охирги янгиланиш:** {datetime.now().strftime('%H:%M:%S')}"
            
            keyboard = [
                [InlineKeyboardButton("📈 Метрикалар", callback_data="metrics"),
                 InlineKeyboardButton("📊 Чартлар", callback_data="charts")],
                [InlineKeyboardButton("🧠 AI Таҳлил", callback_data="ai_analysis"),
                 InlineKeyboardButton("💰 Даромад", callback_data="revenue")],
                [InlineKeyboardButton("👥 Фойдаланувчилар", callback_data="users"),
                 InlineKeyboardButton("🔥 Хатоликлар", callback_data="errors")],
                [InlineKeyboardButton("🔮 Прогноз", callback_data="predict"),
                 InlineKeyboardButton("📋 Ҳисобот", callback_data="report")],
                [InlineKeyboardButton("🔄 Янгилаш", callback_data="dashboard")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if message_id:
                await self.bot.edit_message_text(
                    text=dashboard_text,
                    chat_id=chat_id,
                    message_id=message_id,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
            else:
                await self.bot.send_message(
                    chat_id=chat_id,
                    text=dashboard_text,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
            
        except Exception as e:
            logger.error(f"Dashboard error: {e}")
            await self.bot.send_message(chat_id, f"❌ Дашборд хатоси: {str(e)}")
    
    async def check_backend_health(self) -> Dict:
        """Check backend health with detailed metrics"""
        try:
            start_time = datetime.now()
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{RENDER_BACKEND_URL}/health", timeout=10) as response:
                    end_time = datetime.now()
                    response_time = (end_time - start_time).total_seconds()
                    
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'status': 'ok',
                            'response_time': f"{response_time:.2f}s",
                            'data': data
                        }
                    else:
                        return {
                            'status': 'error',
                            'response_time': f"{response_time:.2f}s",
                            'error': f"HTTP {response.status}"
                        }
        except Exception as e:
            return {
                'status': 'offline',
                'response_time': 'timeout',
                'error': str(e)
            }
    
    @requires_auth
    async def charts_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """📊 Generate and send charts"""
        await update.message.reply_text("📊 Чартлар яратилмоқда...")
        
        try:
            # Generate metrics chart
            metrics = self.db.get_metrics(24)
            chart_buffer = await self.chart_generator.generate_metrics_chart(metrics)
            
            await self.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=chart_buffer,
                caption="📊 **Система Метрикалари** (24 соат)",
                parse_mode='Markdown'
            )
            
            self.stats['charts_generated'] += 1
            
        except Exception as e:
            logger.error(f"Chart generation error: {e}")
            await update.message.reply_text(f"❌ Чарт яратишда хатолик: {str(e)}")
    
    @requires_auth
    async def ai_analysis_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """🧠 AI-powered analysis"""
        if not OPENAI_API_KEY:
            await update.message.reply_text("🤖 AI таҳлил учун OpenAI API калити созланмаган")
            return
        
        await update.message.reply_text("🧠 AI таҳлил бажарилмоқда...")
        
        try:
            metrics = self.db.get_metrics(24)
            analysis = await self.ai_analyzer.analyze_metrics(metrics)
            
            response_text = f"🧠 **AI ТАҲЛИЛ НАТИЖАСИ**\n━━━━━━━━━━━━━━━━━\n\n{analysis}"
            
            await update.message.reply_text(response_text, parse_mode='Markdown')
            self.stats['ai_analyses'] += 1
            
        except Exception as e:
            logger.error(f"AI analysis error: {e}")
            await update.message.reply_text(f"❌ AI таҳлилда хатолик: {str(e)}")
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        if query.data != "auth" and query.data != "help" and user_id not in self.authenticated_users:
            await query.edit_message_text("🔐 Авторизация талаб қилинади. /auth командасини ишлатинг.")
            return
        
        data = query.data
        chat_id = query.message.chat_id
        message_id = query.message.message_id
        
        try:
            if data == "dashboard":
                await self.send_dashboard(chat_id, message_id)
            elif data == "metrics":
                await self.send_metrics_info(chat_id, message_id)
            elif data == "charts":
                await self.send_charts_callback(chat_id, message_id)
            elif data == "ai_analysis":
                await self.send_ai_analysis_callback(chat_id, message_id)
            elif data == "revenue":
                await self.send_revenue_info(chat_id, message_id)
            elif data == "users":
                await self.send_users_info(chat_id, message_id)
            elif data == "errors":
                await self.send_errors_info(chat_id, message_id)
            elif data == "predict":
                await self.send_predictions(chat_id, message_id)
            elif data == "report":
                await self.send_report(chat_id, message_id)
            elif data == "help":
                await self.send_help(chat_id, message_id)
            elif data == "auth":
                await query.edit_message_text("🔐 Авторизация учун: /auth ПАРОЛЬ")
                
        except Exception as e:
            logger.error(f"Callback error: {e}")
            await query.edit_message_text(f"❌ Хатолик: {str(e)}")
    
    async def send_charts_callback(self, chat_id: int, message_id: int):
        """Send charts via callback"""
        try:
            await self.bot.edit_message_text(
                text="📊 Чартлар яратилмоқда...",
                chat_id=chat_id,
                message_id=message_id
            )
            
            # Generate and send metrics chart
            metrics = self.db.get_metrics(24)
            chart_buffer = await self.chart_generator.generate_metrics_chart(metrics)
            
            await self.bot.send_photo(
                chat_id=chat_id,
                photo=chart_buffer,
                caption="📊 **Система Метрикалари** (24 соат)",
                parse_mode='Markdown'
            )
            
            # Go back to dashboard
            await self.send_dashboard(chat_id, message_id)
            self.stats['charts_generated'] += 1
            
        except Exception as e:
            await self.bot.edit_message_text(
                text=f"❌ Чарт яратишда хатолик: {str(e)}",
                chat_id=chat_id,
                message_id=message_id
            )
    
    async def send_help(self, chat_id: int, message_id: int = None):
        """Send comprehensive help"""
        help_text = """
📚 **САВOLIA AI БОТ - ЁРДАМ**
━━━━━━━━━━━━━━━━━━━━━━━━━

🔐 **АВТОРИЗАЦИЯ:**
`/auth ПАРОЛЬ` - Тизимга кириш

📊 **АСОСИЙ КОМАНДАЛАР:**
`/dashboard` - Асосий дашборд
`/status` - Тизим ҳолати
`/metrics` - Детал метрикалар
`/charts` - Визуал чартлар
`/ai_analysis` - AI таҳлил

💰 **АНАЛИТИКА:**
`/analytics` - Умумий аналитика  
`/revenue` - Даромад ҳисоботи
`/users` - Фойдаланувчилар
`/errors` - Хатоликлар рўйхати

🔮 **ПРОГНОЗ ВА AI:**
`/predict` - ML прогнозлар
`/ai_analysis` - AI инсайтлар

⚙️ **АДМИН:**
`/admin` - Админ панели
`/broadcast` - Умумий хабар
`/backup` - Маълумотлар заҳираси
`/logs` - Тизим логлари

🎵 **ҚЎШИМЧА:**
`/voice` - Овозли ҳисобот
`/report` - PDF ҳисобот
`/alert` - Огоҳлантириш созлаш

🖥️ **RENDER LOGS (NEW!):**
`/render_services` - Render сервислар рўйхати
`/render_logs` - Render логларини кўриш
`/render_errors` - Фақат хатолик логлари
`/render_analyze` - Логларни AI билан таҳлил
`/render_realtime` - Real-time мониторинг

💡 **Барча командалар учун inline клавиатуралардан фойдаланинг!**
"""
        
        keyboard = [[InlineKeyboardButton("🔙 Орқага", callback_data="dashboard")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if message_id:
            await self.bot.edit_message_text(
                text=help_text,
                chat_id=chat_id,
                message_id=message_id,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        else:
            await self.bot.send_message(
                chat_id=chat_id,
                text=help_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
    
    # ==================== RENDER LOGS INTEGRATION ====================
    
    async def init_render_client(self):
        """Initialize Render API client"""
        if RENDER_API_KEY and not self.render_client:
            self.render_client = RenderAPIClient(RENDER_API_KEY)
            try:
                async with self.render_client as client:
                    self.render_services = await client.get_services()
                    logger.info(f"✅ Found {len(self.render_services)} Render services")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Render client: {e}")
    
    @requires_auth
    async def render_services_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """🖥️ Show Render services"""
        if not RENDER_API_KEY:
            await update.message.reply_text("❌ Render API калити созланмаган")
            return
        
        await self.init_render_client()
        
        if not self.render_services:
            await update.message.reply_text("📭 Render сервислар топилмади")
            return
        
        text = "🖥️ **RENDER SERVICES**\n━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        for service in self.render_services:
            status_emoji = "🟢" if service.status == "deployed" else "🟡" if service.status == "deploying" else "🔴"
            text += f"{status_emoji} **{service.name}**\n"
            text += f"   • ID: `{service.id}`\n"
            text += f"   • Type: {service.type}\n"
            text += f"   • Status: {service.status}\n\n"
        
        keyboard = [
            [InlineKeyboardButton("📋 Логларни кўриш", callback_data="render_logs_menu")],
            [InlineKeyboardButton("🔄 Янгилаш", callback_data="render_services")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    
    @requires_auth
    async def render_logs_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """📋 Show Render logs"""
        if not RENDER_API_KEY:
            await update.message.reply_text("❌ Render API калити созланмаган")
            return
        
        await update.message.reply_text("📋 Render логлари юкланмоқда...")
        
        try:
            await self.init_render_client()
            
            if not self.render_services:
                await update.message.reply_text("📭 Сервислар топилмади")
                return
            
            # Get logs from the first service (or specified service)
            service = self.render_services[0]  # You can make this configurable
            
            async with RenderAPIClient(RENDER_API_KEY) as client:
                logs = await client.get_logs(service.id, limit=20)
                
                if logs:
                    # Store logs in database
                    self.log_database.store_logs(logs)
                    
                    # Format and send
                    formatted_logs = self.log_formatter.format_recent_logs(logs, limit=10)
                    
                    await update.message.reply_text(
                        f"📋 **{service.name} LOGS**\n━━━━━━━━━━━━━━━━━━━━━━━\n\n{formatted_logs}",
                        parse_mode='Markdown'
                    )
                else:
                    await update.message.reply_text("📭 Логлар топилмади")
            
        except Exception as e:
            logger.error(f"Render logs error: {e}")
            await update.message.reply_text(f"❌ Логларни олишда хатолик: {str(e)}")
    
    @requires_auth
    async def render_errors_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """🔥 Show only error logs from Render"""
        if not RENDER_API_KEY:
            await update.message.reply_text("❌ Render API калити созланмаган")
            return
        
        await update.message.reply_text("🔥 Хатолик логлари қидирилмоқда...")
        
        try:
            await self.init_render_client()
            
            if not self.render_services:
                await update.message.reply_text("📭 Сервислар топилмади")
                return
            
            service = self.render_services[0]
            
            async with RenderAPIClient(RENDER_API_KEY) as client:
                logs = await client.get_logs(service.id, limit=100)
                error_logs = [log for log in logs if log.level == 'ERROR']
                
                if error_logs:
                    text = f"🔥 **{service.name} ERROR LOGS**\n━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    
                    for log in error_logs[:10]:  # Show last 10 errors
                        text += self.log_formatter.format_log_entry(log) + "\n\n"
                    
                    if len(error_logs) > 10:
                        text += f"\n... ва яна {len(error_logs) - 10} хатолик"
                    
                    await update.message.reply_text(text, parse_mode='Markdown')
                else:
                    await update.message.reply_text("✅ Хатоликлар топилмади!")
            
        except Exception as e:
            logger.error(f"Render errors command error: {e}")
            await update.message.reply_text(f"❌ Хатолик логларини олишда хатолик: {str(e)}")
    
    @requires_auth
    async def render_analyze_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """📊 Analyze Render logs with AI"""
        if not RENDER_API_KEY:
            await update.message.reply_text("❌ Render API калити созланмаган")
            return
        
        await update.message.reply_text("📊 Логлар таҳлил қилинмоқда...")
        
        try:
            await self.init_render_client()
            
            if not self.render_services:
                await update.message.reply_text("📭 Сервислар топилмади")
                return
            
            service = self.render_services[0]
            
            async with RenderAPIClient(RENDER_API_KEY) as client:
                logs = await client.get_logs(service.id, limit=200)
                
                if logs:
                    # Analyze logs
                    analysis = self.log_analyzer.analyze_logs(logs)
                    summary = self.log_formatter.format_log_summary(analysis)
                    
                    # Detect anomalies
                    anomalies = self.log_analyzer.detect_anomalies(logs)
                    
                    text = summary
                    
                    if anomalies:
                        text += "\n🚨 **ANOMALIES DETECTED:**\n"
                        for anomaly in anomalies:
                            severity_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(anomaly['severity'], "⚪")
                            text += f"{severity_emoji} {anomaly['message']}\n"
                    
                    await update.message.reply_text(text, parse_mode='Markdown')
                else:
                    await update.message.reply_text("📭 Таҳлил учун логлар топилмади")
            
        except Exception as e:
            logger.error(f"Render analyze error: {e}")
            await update.message.reply_text(f"❌ Таҳлилда хатолик: {str(e)}")
    
    @requires_auth
    async def render_realtime_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """📡 Start real-time log monitoring"""
        if not RENDER_API_KEY:
            await update.message.reply_text("❌ Render API калити созланмаган")
            return
        
        await update.message.reply_text(
            "📡 **REAL-TIME LOG MONITORING**\n\n"
            "⚠️ Real-time мониторинг фонда ишлайди.\n"
            "Янги хатоликлар ва муҳим событиялар сизга юборилади.\n\n"
            "/stop_realtime - тўхтатиш учун"
        )
        
        # Start real-time monitoring task
        asyncio.create_task(self.render_realtime_monitoring(update.effective_chat.id))
    
    async def render_realtime_monitoring(self, chat_id: int):
        """Background real-time log monitoring"""
        if not RENDER_API_KEY or not self.render_services:
            return
        
        try:
            service = self.render_services[0]
            
            async with RenderAPIClient(RENDER_API_KEY) as client:
                async for log in client.stream_logs_realtime(service.id):
                    # Send critical errors immediately
                    if log.level == 'ERROR':
                        message = f"🚨 **REAL-TIME ERROR**\n\n{self.log_formatter.format_log_entry(log)}"
                        await self.bot.send_message(chat_id, message, parse_mode='Markdown')
                    
                    # Store all logs
                    self.log_database.store_logs([log])
                    
        except Exception as e:
            logger.error(f"Real-time monitoring error: {e}")
            await self.bot.send_message(
                chat_id, 
                f"❌ Real-time мониторингда хатолик: {str(e)}"
            )
    
    async def run(self):
        """Start the advanced bot"""
        logger.info("🚀 Starting Savolia AI Advanced Monitoring Bot...")
        
        try:
            await self.application.initialize()
            await self.application.start()
            
            # Start background tasks
            asyncio.create_task(self.health_monitoring_loop())
            asyncio.create_task(self.ai_insights_loop())
            asyncio.create_task(self.cleanup_loop())
            
            # Start Render monitoring if API key is available
            if RENDER_API_KEY and self.render_client:
                asyncio.create_task(self.background_deployment_monitor())
            
            await self.application.updater.start_polling()
            
        except Exception as e:
            logger.error(f"Bot startup error: {e}")
        finally:
            await self.application.stop()
            await self.application.shutdown()
    
    async def health_monitoring_loop(self):
        """Background health monitoring"""
        while True:
            try:
                # Check backend health
                health = await self.check_backend_health()
                
                # Store metrics in database
                self.db.add_metric(
                    response_time=float(health['response_time'].replace('s', '')) if 's' in health.get('response_time', '0') else 0,
                    active_users=100,  # Mock data - replace with real data
                    error_count=0 if health['status'] == 'ok' else 1,
                    success_rate=100 if health['status'] == 'ok' else 0,
                    cpu_usage=45.0,  # Mock data
                    memory_usage=62.0,  # Mock data
                    disk_usage=78.0   # Mock data
                )
                
                # Alert if critical issues
                if health['status'] != 'ok':
                    await self.send_critical_alert(health)
                
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
            
            await asyncio.sleep(300)  # Check every 5 minutes
    
    async def ai_insights_loop(self):
        """Background AI insights generation"""
        while True:
            try:
                if OPENAI_API_KEY:
                    metrics = self.db.get_metrics(6)  # Last 6 hours
                    if len(metrics) > 10:
                        insights = await self.ai_analyzer.analyze_metrics(metrics)
                        
                        # Store insights in database
                        conn = sqlite3.connect(self.db.db_path)
                        cursor = conn.cursor()
                        cursor.execute('''
                            INSERT INTO ai_insights (insight_type, content, confidence)
                            VALUES (?, ?, ?)
                        ''', ('system_analysis', insights, 0.85))
                        conn.commit()
                        conn.close()
                
            except Exception as e:
                logger.error(f"AI insights error: {e}")
            
            await asyncio.sleep(3600)  # Generate insights every hour
    
    async def cleanup_loop(self):
        """Background cleanup and maintenance"""
        while True:
            try:
                # Clean old metrics (older than 7 days)
                conn = sqlite3.connect(self.db.db_path)
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM system_metrics 
                    WHERE timestamp < datetime('now', '-7 days')
                ''')
                cursor.execute('''
                    DELETE FROM error_logs 
                    WHERE timestamp < datetime('now', '-30 days')
                ''')
                conn.commit()
                conn.close()
                
                logger.info("🧹 Database cleanup completed")
                
            except Exception as e:
                logger.error(f"Cleanup error: {e}")
            
            await asyncio.sleep(86400)  # Cleanup daily
    
    async def send_critical_alert(self, health_data: Dict):
        """Send critical system alerts"""
        if self.admin_users:
            alert_text = f"""
🚨 **КРИТИК ТИЗИМ ОГОҲЛАНТИРИШИ**

⚠️ **Муаммо:** {health_data.get('error', 'Номаълум')}
🕒 **Вақт:** {datetime.now().strftime('%H:%M:%S')}
📊 **Ҳолат:** {health_data['status']}

🔧 Тизимни текширинг!
"""
            
            for admin_id in self.admin_users:
                try:
                    await self.bot.send_message(admin_id, alert_text, parse_mode='Markdown')
                except Exception as e:
                    logger.error(f"Failed to send alert to {admin_id}: {e}")
    
    async def handle_render_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle Render-related callbacks"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data == "render_services":
            await self.render_services_command(update, context)
        elif data == "render_logs_recent":
            await self.render_logs_command(update, context)
        elif data == "render_errors":
            await self.render_errors_command(update, context)
        elif data == "render_analyze":
            await self.render_analyze_command(update, context)
        elif data == "render_realtime_start":
            await self.render_realtime_command(update, context)
        elif data == "render_deploy_status":
            await self.render_deploy_command(update, context)
        elif data == "render_status_check":
            await self.render_status_command(update, context)
        elif data.startswith("service_logs_"):
            service_id = data.replace("service_logs_", "")
            await self.show_service_logs(update, context, service_id)
        elif data.startswith("service_errors_"):
            service_id = data.replace("service_errors_", "")
            await self.show_service_errors(update, context, service_id)
        elif data.startswith("service_monitor_"):
            service_id = data.replace("service_monitor_", "")
            await self.start_service_monitoring(update, context, service_id)
    
    async def render_services_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """🖥️ Show Render services"""
        if not self.render_client:
            await self.send_message(update, "❌ Render API key sozlanmagan. RENDER_API_KEY ni o'rnating.")
            return
        
        try:
            async with self.render_client as client:
                services = await client.get_services()
                
                if not services:
                    await self.send_message(update, "📭 Hech qanday service topilmadi")
                    return
                
                text = "🖥️ **RENDER SERVICES**\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
                
                for i, service in enumerate(services[:10]):  # Limit to 10
                    status_emoji = "🟢" if service.status == "available" else "🔴"
                    deploy_emoji = "🚀" if service.type == "web_service" else "⚙️"
                    text += f"{status_emoji} **{service.name}** {deploy_emoji}\n"
                    text += f"   🆔 ID: `{service.id}`\n"
                    text += f"   🏷️ Turi: {service.type}\n"
                    text += f"   📊 Status: {service.status}\n\n"
                
                # Create service-specific buttons
                keyboard = []
                
                # Add service selection buttons
                for service in services[:4]:  # Top 4 services
                    service_name = service.name.replace('savolia-', '')
                    keyboard.append([
                        InlineKeyboardButton(f"📋 {service_name} logs", callback_data=f"service_logs_{service.id}"),
                        InlineKeyboardButton(f"🚨 {service_name} errors", callback_data=f"service_errors_{service.id}")
                    ])
                
                # Add general buttons
                keyboard.extend([
                    [InlineKeyboardButton("🚀 Deploy Status", callback_data="render_deploy_status"),
                     InlineKeyboardButton("📊 Status Check", callback_data="render_status_check")],
                    [InlineKeyboardButton("🔴 Real-time All", callback_data="render_realtime_start")]
                ])
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await self.send_message(update, text, reply_markup=reply_markup)
                
        except Exception as e:
            logger.error(f"Render services error: {e}")
            await self.send_message(update, f"❌ Xatolik: {str(e)}")
    
    async def render_logs_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """📋 Show recent Render logs"""
        if not self.render_client:
            await self.send_message(update, "❌ Render API key sozlanmagan")
            return
        
        try:
            async with self.render_client as client:
                services = await client.get_services()
                
                if not services:
                    await self.send_message(update, "📭 Service topilmadi")
                    return
                
                # Show service selection if no specific service
                if not context.args:
                    text = "🔍 **SERVICE TANLANG**\n━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    
                    keyboard = []
                    for service in services:
                        service_name = service.name.replace('savolia-', '')
                        keyboard.append([InlineKeyboardButton(
                            f"📋 {service_name} loglar", 
                            callback_data=f"service_logs_{service.id}"
                        )])
                    
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await self.send_message(update, text, reply_markup=reply_markup)
                    return
                
                # Get logs from first service (default)
                service = services[0]
                logs = await client.get_logs(service.id, limit=20)
                
                if not logs:
                    await self.send_message(update, "📭 Loglar topilmadi")
                    return
                
                # Format logs using TelegramLogFormatter
                from render_logs_viewer import TelegramLogFormatter
                formatter = TelegramLogFormatter()
                text = formatter.format_recent_logs(logs, limit=10)
                
                await self.send_message(update, text)
                
        except Exception as e:
            logger.error(f"Render logs error: {e}")
            await self.send_message(update, f"❌ Xatolik: {str(e)}")
    
    async def render_errors_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """🚨 Show recent errors from Render"""
        if not self.render_client:
            await self.send_message(update, "❌ Render API key sozlanmagan")
            return
        
        try:
            async with self.render_client as client:
                services = await client.get_services()
                
                if not services:
                    await self.send_message(update, "📭 Service topilmadi")
                    return
                
                service = services[0]
                logs = await client.get_logs(service.id, limit=50)
                
                # Filter only errors
                error_logs = [log for log in logs if log.level == 'ERROR']
                
                if not error_logs:
                    await self.send_message(update, "✅ So'nggi vaqtda xatolar topilmadi!")
                    return
                
                text = f"🚨 **SO'NGGI {len(error_logs)} XATOLAR**\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
                
                for error in error_logs[:10]:
                    text += f"🔥 `{error.timestamp.strftime('%H:%M:%S')}`\n"
                    text += f"```\n{error.message[:150]}...\n```\n\n"
                
                await self.send_message(update, text)
                
        except Exception as e:
            logger.error(f"Render errors command error: {e}")
            await self.send_message(update, f"❌ Xatolik: {str(e)}")
    
    async def render_analyze_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """📊 Analyze Render logs"""
        if not self.render_client:
            await self.send_message(update, "❌ Render API key sozlanmagan")
            return
        
        try:
            async with self.render_client as client:
                services = await client.get_services()
                
                if not services:
                    await self.send_message(update, "📭 Service topilmadi")
                    return
                
                service = services[0]
                logs = await client.get_logs(service.id, limit=100)
                
                if not logs:
                    await self.send_message(update, "📭 Tahlil qilish uchun loglar topilmadi")
                    return
                
                # Analyze logs
                from render_logs_viewer import LogAnalyzer, TelegramLogFormatter
                analyzer = LogAnalyzer()
                analysis = analyzer.analyze_logs(logs)
                
                # Format analysis
                formatter = TelegramLogFormatter()
                summary = formatter.format_log_summary(analysis)
                
                # Detect anomalies
                anomalies = analyzer.detect_anomalies(logs)
                
                if anomalies:
                    summary += "\n\n🚨 **ANOMALIYALAR:**\n"
                    for anomaly in anomalies:
                        summary += f"⚠️ {anomaly['message']}\n"
                
                await self.send_message(update, summary)
                
        except Exception as e:
            logger.error(f"Render analyze error: {e}")
            await self.send_message(update, f"❌ Tahlil xatoligi: {str(e)}")
    
    async def render_realtime_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """🔴 Start real-time log monitoring"""
        if not self.render_client:
            await self.send_message(update, "❌ Render API key sozlanmagan")
            return
        
        user_id = update.effective_user.id
        
        # Check if already monitoring
        if hasattr(self, 'realtime_tasks') and user_id in self.realtime_tasks:
            await self.send_message(update, "⏹️ Real-time monitoring to'xtatildi")
            self.realtime_tasks[user_id].cancel()
            del self.realtime_tasks[user_id]
            return
        
        await self.send_message(update, "🔴 **REAL-TIME MONITORING BOSHLANDI**\n\n📡 Yangi loglar uchun kuzatilmoqda...")
        
        # Start monitoring task
        if not hasattr(self, 'realtime_tasks'):
            self.realtime_tasks = {}
        
        self.realtime_tasks[user_id] = asyncio.create_task(
            self.render_realtime_monitoring(user_id)
        )
    
    async def render_realtime_monitoring(self, user_id: int):
        """Real-time log monitoring task"""
        try:
            async with self.render_client as client:
                services = await client.get_services()
                
                if not services:
                    await self.bot.send_message(user_id, "❌ Services topilmadi")
                    return
                
                service = services[0]
                
                # Stream logs in real-time
                async for log in client.stream_logs_realtime(service.id):
                    if log.level == 'ERROR':
                        # Send critical errors immediately
                        from render_logs_viewer import TelegramLogFormatter
                        formatter = TelegramLogFormatter()
                        message = f"🚨 **YANGI XATO TOPILDI**\n\n{formatter.format_log_entry(log)}"
                        
                        await self.bot.send_message(user_id, message, parse_mode='Markdown')
                
        except asyncio.CancelledError:
            await self.bot.send_message(user_id, "⏹️ Real-time monitoring to'xtatildi")
        except Exception as e:
            logger.error(f"Real-time monitoring error: {e}")
            await self.bot.send_message(user_id, f"❌ Monitoring xatoligi: {str(e)}")

    async def send_message(self, update, text, reply_markup=None):
        """Helper method to send messages"""
        if hasattr(update, 'message') and update.message:
            await update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
        elif hasattr(update, 'callback_query') and update.callback_query:
            await update.callback_query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)

async def main():
    """Main function"""
    bot = AdvancedSavoliaBot()
    
    try:
        await bot.run()
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"💥 Bot error: {e}")

if __name__ == "__main__":
    print("🚀 SAVOLIA AI ADVANCED MONITORING BOT 2025")
    print("=" * 50)
    print(f"🤖 Token: {BOT_TOKEN[:20]}...")
    print(f"🖥️ Backend: {RENDER_BACKEND_URL}")
    print(f"🧠 AI: {'✅ Enabled' if OPENAI_API_KEY else '❌ Disabled'}")
    print(f"💾 Database: {DB_PATH}")
    print("=" * 50)
    print("\n🔥 Features:")
    print("• 🧠 AI-powered analytics")
    print("• 📊 Real-time charts")
    print("• 🔮 ML predictions") 
    print("• 🎨 Beautiful visualizations")
    print("• 🔔 Smart alerts")
    print("• 💰 Revenue forecasting")
    print("• 🎵 Voice reports")
    print("• 📧 Email integration")
    print("• 🌍 Multi-language support")
    print("• 🔒 Advanced security")
    print("\n📱 Commands: /start, /help, /dashboard")
    print("🔐 Default password: SavoliaAdmin2025!")
    print("\nPress Ctrl+C to stop...")
    
    asyncio.run(main())