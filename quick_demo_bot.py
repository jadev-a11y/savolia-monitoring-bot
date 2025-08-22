#!/usr/bin/env python3
"""
🚀 SAVOLIA AI QUICK DEMO BOT WITH RENDER LOGS
Демо версия для быстрого тестирования без зависимостей
"""

import asyncio
import aiohttp
import logging
import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass

# Telegram Bot imports (базовые)
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Configuration
BOT_TOKEN = "8087171595:AAGcTv_TiNAY-Mv8CSyaIwk2tzYnnEM4Dsk"
ADMIN_PASSWORD = "SavoliaAdmin2025!"
RENDER_API_KEY = os.getenv('RENDER_API_KEY', '')
RENDER_BACKEND_URL = "https://savolia-backend.onrender.com"

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class LogEntry:
    """Represents a single log entry from Render"""
    timestamp: datetime
    level: str
    message: str
    service_id: str
    source: str
    raw_data: Dict

@dataclass
class RenderService:
    """Represents a Render service"""
    id: str
    name: str
    type: str
    status: str

class RenderAPIClient:
    """Simplified Render.com API client"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.render.com/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_services(self) -> List[RenderService]:
        """Get all services from Render account"""
        try:
            async with self.session.get(f"{self.base_url}/services") as response:
                if response.status == 200:
                    data = await response.json()
                    services = []
                    for service_data in data.get('data', []):
                        service = RenderService(
                            id=service_data.get('id', ''),
                            name=service_data.get('name', ''),
                            type=service_data.get('type', ''),
                            status=service_data.get('status', '')
                        )
                        services.append(service)
                    return services
                else:
                    logger.error(f"Failed to get services: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error getting services: {e}")
            return []
    
    async def get_logs(self, service_id: str, limit: int = 50) -> List[LogEntry]:
        """Get logs for a specific service"""
        try:
            start_time = datetime.now() - timedelta(hours=24)
            end_time = datetime.now()
            
            params = {
                "startTime": start_time.isoformat(),
                "endTime": end_time.isoformat(),
                "limit": limit
            }
            
            url = f"{self.base_url}/services/{service_id}/logs"
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    logs = []
                    
                    for log_data in data.get('data', []):
                        try:
                            timestamp_str = log_data.get('timestamp', '')
                            if timestamp_str:
                                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                            else:
                                timestamp = datetime.now()
                            
                            log_entry = LogEntry(
                                timestamp=timestamp,
                                level=self.extract_log_level(log_data.get('message', '')),
                                message=log_data.get('message', ''),
                                service_id=service_id,
                                source=log_data.get('source', ''),
                                raw_data=log_data
                            )
                            logs.append(log_entry)
                        except Exception as e:
                            logger.error(f"Error parsing log entry: {e}")
                            continue
                    
                    return sorted(logs, key=lambda x: x.timestamp, reverse=True)
                else:
                    logger.error(f"Failed to get logs: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error getting logs: {e}")
            return []
    
    def extract_log_level(self, message: str) -> str:
        """Extract log level from message"""
        message_upper = message.upper()
        if 'ERROR' in message_upper or 'FATAL' in message_upper:
            return 'ERROR'
        elif 'WARN' in message_upper:
            return 'WARNING'
        elif 'INFO' in message_upper:
            return 'INFO'
        elif 'DEBUG' in message_upper:
            return 'DEBUG'
        else:
            return 'INFO'

class TelegramLogFormatter:
    """Format logs for Telegram display"""
    
    @staticmethod
    def format_log_entry(log: LogEntry) -> str:
        """Format a single log entry for Telegram"""
        emoji = {
            'ERROR': '🔥',
            'WARNING': '⚠️',
            'INFO': 'ℹ️',
            'DEBUG': '🔍'
        }.get(log.level, '📄')
        
        timestamp = log.timestamp.strftime('%H:%M:%S')
        message = log.message[:200] + '...' if len(log.message) > 200 else log.message
        
        return f"{emoji} **{log.level}** `{timestamp}`\\n```\\n{message}\\n```"
    
    @staticmethod
    def format_recent_logs(logs: List[LogEntry], limit: int = 10) -> str:
        """Format recent logs for Telegram"""
        if not logs:
            return "📭 Loglar topilmadi"
        
        text = f"📋 **SO'NGGI {min(len(logs), limit)} LOGLAR**\\n━━━━━━━━━━━━━━━━━━━━━━\\n\\n"
        
        for log in logs[:limit]:
            text += TelegramLogFormatter.format_log_entry(log) + "\\n\\n"
        
        if len(logs) > limit:
            text += f"... va yana {len(logs) - limit} loglar"
        
        return text

class SavoliaQuickBot:
    """Quick demo bot for Savolia AI monitoring"""
    
    def __init__(self):
        self.token = BOT_TOKEN
        self.bot = Bot(token=self.token)
        self.application = Application.builder().token(self.token).build()
        
        # Authentication
        self.authenticated_users = set()
        self.admin_users = set()
        
        # Render integration
        self.render_client = None
        if RENDER_API_KEY:
            self.render_client = RenderAPIClient(RENDER_API_KEY)
        
        # Statistics
        self.stats = {
            'start_time': datetime.now(),
            'commands_executed': 0
        }
        
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup command handlers"""
        # Basic commands
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("auth", self.auth_command))
        
        # Render commands
        self.application.add_handler(CommandHandler("render_services", self.render_services_command))
        self.application.add_handler(CommandHandler("render_logs", self.render_logs_command))
        self.application.add_handler(CommandHandler("render_errors", self.render_errors_command))
        self.application.add_handler(CommandHandler("render_status", self.render_status_command))
        
        # Callback handlers
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command"""
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        
        welcome_text = f"""
🤖 **SAVOLIA AI QUICK DEMO BOT**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👋 Salom, {username}!

🚀 **Demo Features:**
• 🖥️ Render services monitoring  
• 📋 Real-time logs viewing
• 🚨 Error detection
• 📊 Service status checking

💡 Avval /auth parol bilan kirinng
📚 Barcha kommandalar: /help

🔑 **Demo Access:** 
`/auth {ADMIN_PASSWORD}`
"""
        
        keyboard = [
            [InlineKeyboardButton("🔐 Login", callback_data="show_auth"),
             InlineKeyboardButton("📚 Help", callback_data="show_help")],
            [InlineKeyboardButton("🖥️ Services", callback_data="render_services")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_text, parse_mode='Markdown', reply_markup=reply_markup)
        self.stats['commands_executed'] += 1
    
    async def auth_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Authentication command"""
        if not context.args:
            await update.message.reply_text(
                "🔐 **Authentication**\\n\\n"
                "Usage: `/auth PASSWORD`\\n\\n"
                f"💡 Demo password: `{ADMIN_PASSWORD}`",
                parse_mode='Markdown'
            )
            return
        
        password = ' '.join(context.args)
        if password == ADMIN_PASSWORD:
            user_id = update.effective_user.id
            self.authenticated_users.add(user_id)
            self.admin_users.add(user_id)
            
            await update.message.reply_text(
                "✅ **Muvaffaqiyatli kirish!**\\n\\n"
                "🎉 Endi barcha funksiyalardan foydalanishingiz mumkin\\n"
                "🖥️ /render_services - Render monitoring",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text("❌ Noto'g'ri parol!")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Help command"""
        help_text = """
📚 **SAVOLIA AI DEMO BOT COMMANDS**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔐 **Authentication:**
• `/start` - Bot boshlash
• `/auth PASSWORD` - Kirish (demo password)
• `/help` - Bu yordam

🖥️ **Render Monitoring:**
• `/render_services` - Barcha servicelar
• `/render_logs` - Service loglarini ko'rish
• `/render_errors` - Faqat xatolar
• `/render_status` - Umumiy holat

💡 **Quick Access:**
Demo password: `SavoliaAdmin2025!`

🔧 **Status:**
Bot started: {self.stats['start_time'].strftime('%H:%M:%S')}
Commands executed: {self.stats['commands_executed']}
Render API: {'✅ Connected' if RENDER_API_KEY else '❌ Not configured'}
"""
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
        self.stats['commands_executed'] += 1
    
    def requires_auth(func):
        """Authentication decorator"""
        async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
            user_id = update.effective_user.id
            if user_id not in self.authenticated_users:
                await update.message.reply_text(
                    "🔐 Avval autentifikatsiya qiling: `/auth SavoliaAdmin2025!`",
                    parse_mode='Markdown'
                )
                return
            return await func(self, update, context)
        return wrapper
    
    @requires_auth
    async def render_services_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show Render services"""
        if not RENDER_API_KEY:
            await update.message.reply_text("❌ Render API key sozlanmagan")
            return
        
        try:
            async with self.render_client as client:
                services = await client.get_services()
                
                if not services:
                    await update.message.reply_text("📭 Services topilmadi")
                    return
                
                text = "🖥️ **RENDER SERVICES**\\n━━━━━━━━━━━━━━━━━━━━━━━\\n\\n"
                
                for i, service in enumerate(services):
                    if service.status == "available":
                        status_emoji = "🟢"
                    elif service.status == "deploying":
                        status_emoji = "🟡"  
                    elif service.status == "failed":
                        status_emoji = "🔴"
                    else:
                        status_emoji = "⚪"
                    
                    text += f"{status_emoji} **{service.name}**\\n"
                    text += f"   📋 Type: {service.type}\\n"
                    text += f"   📊 Status: {service.status}\\n"
                    text += f"   🆔 ID: `{service.id[:8]}...`\\n\\n"
                
                # Create service-specific buttons
                keyboard = []
                for service in services[:4]:  # Top 4 services
                    service_name = service.name.replace('savolia-', '')
                    keyboard.append([
                        InlineKeyboardButton(f"📋 {service_name} logs", callback_data=f"logs_{service.id}"),
                        InlineKeyboardButton(f"🚨 {service_name} errors", callback_data=f"errors_{service.id}")
                    ])
                
                keyboard.append([
                    InlineKeyboardButton("🔄 Yangilash", callback_data="render_services"),
                    InlineKeyboardButton("📊 Status", callback_data="render_status")
                ])
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
                
        except Exception as e:
            logger.error(f"Render services error: {e}")
            await update.message.reply_text(f"❌ Xatolik: {str(e)}")
        
        self.stats['commands_executed'] += 1
    
    @requires_auth  
    async def render_logs_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show render logs"""
        if not RENDER_API_KEY:
            await update.message.reply_text("❌ Render API key sozlanmagan")
            return
        
        try:
            async with self.render_client as client:
                services = await client.get_services()
                
                if not services:
                    await update.message.reply_text("📭 Services topilmadi")
                    return
                
                # Show service selection
                text = "📋 **LOG QAYSI SERVICE UCHUN?**\\n━━━━━━━━━━━━━━━━━━━━━━━\\n\\n"
                
                keyboard = []
                for service in services:
                    service_name = service.name.replace('savolia-', '')
                    keyboard.append([InlineKeyboardButton(
                        f"📋 {service_name} loglar",
                        callback_data=f"logs_{service.id}"
                    )])
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
                
        except Exception as e:
            await update.message.reply_text(f"❌ Xatolik: {str(e)}")
        
        self.stats['commands_executed'] += 1
    
    @requires_auth
    async def render_errors_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show recent errors"""
        if not RENDER_API_KEY:
            await update.message.reply_text("❌ Render API key sozlanmagan")
            return
        
        try:
            async with self.render_client as client:
                services = await client.get_services()
                
                if not services:
                    await update.message.reply_text("📭 Services topilmadi")
                    return
                
                all_errors = []
                
                for service in services:
                    logs = await client.get_logs(service.id, limit=20)
                    errors = [log for log in logs if log.level == 'ERROR']
                    for error in errors:
                        error.service_name = service.name
                    all_errors.extend(errors)
                
                if not all_errors:
                    await update.message.reply_text("✅ So'nggi vaqtda xatolar topilmadi!")
                    return
                
                # Sort by timestamp
                all_errors.sort(key=lambda x: x.timestamp, reverse=True)
                
                text = f"🚨 **SO'NGGI {len(all_errors)} XATOLAR**\\n━━━━━━━━━━━━━━━━━━━━━━━\\n\\n"
                
                for error in all_errors[:10]:  # Show latest 10 errors
                    text += f"🔥 **{error.service_name}**\\n"
                    text += f"⏰ {error.timestamp.strftime('%H:%M:%S')}\\n"
                    text += f"```\\n{error.message[:150]}...\\n```\\n\\n"
                
                await update.message.reply_text(text, parse_mode='Markdown')
                
        except Exception as e:
            await update.message.reply_text(f"❌ Xatolik: {str(e)}")
        
        self.stats['commands_executed'] += 1
    
    @requires_auth
    async def render_status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Overall system status"""
        if not RENDER_API_KEY:
            await update.message.reply_text("❌ Render API key sozlanmagan")
            return
        
        try:
            async with self.render_client as client:
                services = await client.get_services()
                
                if not services:
                    await update.message.reply_text("📭 Services topilmadi")
                    return
                
                # Count statuses
                status_counts = {}
                for service in services:
                    status_counts[service.status] = status_counts.get(service.status, 0) + 1
                
                total = len(services)
                healthy = status_counts.get('available', 0)
                health_percentage = (healthy / total * 100) if total > 0 else 0
                
                if health_percentage >= 80:
                    health_emoji = "🟢"
                    health_text = "Excellent"
                elif health_percentage >= 60:
                    health_emoji = "🟡"
                    health_text = "Good"
                else:
                    health_emoji = "🔴" 
                    health_text = "Issues"
                
                text = f"""
📊 **TIZIM HOLATI**
━━━━━━━━━━━━━━━━━━━━━━━

{health_emoji} **Overall Health:** {health_text} ({health_percentage:.1f}%)

📈 **Statistics:**
✅ Available: {status_counts.get('available', 0)}
🟡 Deploying: {status_counts.get('deploying', 0)}
❌ Failed: {status_counts.get('failed', 0)}
📊 Total: {total}

🕐 **Checked:** {datetime.now().strftime('%H:%M:%S')}
"""
                
                keyboard = [
                    [InlineKeyboardButton("🔄 Refresh", callback_data="render_status"),
                     InlineKeyboardButton("🚨 Show Errors", callback_data="render_errors")],
                    [InlineKeyboardButton("🖥️ Services", callback_data="render_services")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
                
        except Exception as e:
            await update.message.reply_text(f"❌ Xatolik: {str(e)}")
        
        self.stats['commands_executed'] += 1
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data == "show_auth":
            await query.edit_message_text(
                f"🔐 **AUTHENTICATION**\\n\\n"
                f"Demo password: `{ADMIN_PASSWORD}`\\n\\n"
                f"Usage: `/auth {ADMIN_PASSWORD}`",
                parse_mode='Markdown'
            )
        elif data == "show_help":
            await self.help_command(update, context)
        elif data == "render_services":
            await self.render_services_command(update, context)
        elif data == "render_status":
            await self.render_status_command(update, context)
        elif data == "render_errors":
            await self.render_errors_command(update, context)
        elif data.startswith("logs_"):
            service_id = data.replace("logs_", "")
            await self.show_service_logs(update, service_id)
        elif data.startswith("errors_"):
            service_id = data.replace("errors_", "")
            await self.show_service_errors(update, service_id)
    
    async def show_service_logs(self, update, service_id: str):
        """Show logs for specific service"""
        try:
            async with self.render_client as client:
                services = await client.get_services()
                service = next((s for s in services if s.id == service_id), None)
                
                if not service:
                    await update.callback_query.edit_message_text("❌ Service topilmadi")
                    return
                
                logs = await client.get_logs(service_id, limit=20)
                
                if not logs:
                    await update.callback_query.edit_message_text(
                        f"📭 {service.name} uchun loglar topilmadi"
                    )
                    return
                
                text = f"📋 **{service.name.upper()} LOGS**\\n━━━━━━━━━━━━━━━━━━━━━━━\\n\\n"
                
                for log in logs[:10]:
                    emoji = {'ERROR': '🔥', 'WARNING': '⚠️', 'INFO': 'ℹ️', 'DEBUG': '🔍'}.get(log.level, '📄')
                    text += f"{emoji} `{log.timestamp.strftime('%H:%M:%S')}`\\n"
                    text += f"```\\n{log.message[:100]}...\\n```\\n\\n"
                
                keyboard = [
                    [InlineKeyboardButton("🚨 Faqat xatolar", callback_data=f"errors_{service_id}")],
                    [InlineKeyboardButton("🔄 Yangilash", callback_data=f"logs_{service_id}"),
                     InlineKeyboardButton("⬅️ Orqaga", callback_data="render_services")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.callback_query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
                
        except Exception as e:
            await update.callback_query.edit_message_text(f"❌ Xatolik: {str(e)}")
    
    async def show_service_errors(self, update, service_id: str):
        """Show errors for specific service"""
        try:
            async with self.render_client as client:
                services = await client.get_services()
                service = next((s for s in services if s.id == service_id), None)
                
                if not service:
                    await update.callback_query.edit_message_text("❌ Service topilmadi")
                    return
                
                logs = await client.get_logs(service_id, limit=50)
                errors = [log for log in logs if log.level == 'ERROR']
                
                if not errors:
                    await update.callback_query.edit_message_text(
                        f"✅ {service.name} da xatolar topilmadi!"
                    )
                    return
                
                text = f"🚨 **{service.name.upper()} ERRORS**\\n━━━━━━━━━━━━━━━━━━━━━━━\\n"
                text += f"🔥 Found: **{len(errors)}** errors\\n\\n"
                
                for error in errors[:8]:
                    text += f"🔥 `{error.timestamp.strftime('%H:%M:%S')}`\\n"
                    text += f"```\\n{error.message[:120]}...\\n```\\n\\n"
                
                keyboard = [
                    [InlineKeyboardButton("📋 All logs", callback_data=f"logs_{service_id}")],
                    [InlineKeyboardButton("🔄 Refresh", callback_data=f"errors_{service_id}"),
                     InlineKeyboardButton("⬅️ Back", callback_data="render_services")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.callback_query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
                
        except Exception as e:
            await update.callback_query.edit_message_text(f"❌ Xatolik: {str(e)}")
    
    async def run(self):
        """Start the bot"""
        logger.info("🚀 Starting Savolia AI Quick Demo Bot...")
        
        try:
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            
            # Keep running until stopped
            await asyncio.Future()  # Run forever
            
        except KeyboardInterrupt:
            logger.info("🛑 Bot stopped by user")
        except Exception as e:
            logger.error(f"Bot error: {e}")
        finally:
            if self.application.running:
                await self.application.stop()
                await self.application.shutdown()

async def main():
    """Main function"""
    bot = SavoliaQuickBot()
    
    try:
        await bot.run()
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"💥 Bot error: {e}")

if __name__ == "__main__":
    print("🚀 SAVOLIA AI QUICK DEMO BOT 2025")
    print("=" * 50)
    print(f"🤖 Token: {BOT_TOKEN[:20]}...")
    print(f"🖥️ Backend: {RENDER_BACKEND_URL}")
    print(f"🔑 Render API: {'✅ Set' if RENDER_API_KEY else '❌ Not set'}")
    print("=" * 50)
    print("\\n🔥 Quick Demo Features:")
    print("• 🖥️ Render services monitoring")
    print("• 📋 Real-time logs viewing") 
    print("• 🚨 Error detection")
    print("• 📊 Service status")
    print("\\n📱 Commands: /start, /auth, /render_services")
    print(f"🔐 Demo password: {ADMIN_PASSWORD}")
    print("\\nPress Ctrl+C to stop...")
    
    asyncio.run(main())