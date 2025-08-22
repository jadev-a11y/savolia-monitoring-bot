#!/usr/bin/env python3
"""
Savolia AI Telegram Logger Bot
Monitors logs, errors, subscriptions, and backend status
Token: 8087171595:AAGcTv_TiNAY-Mv8CSyaIwk2tzYnnEM4Dsk
"""

import asyncio
import logging
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List
import aiohttp
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Configuration
BOT_TOKEN = "8087171595:AAGcTv_TiNAY-Mv8CSyaIwk2tzYnnEM4Dsk"
RENDER_BACKEND_URL = "https://savolia-backend.onrender.com"  # Replace with your actual backend URL
ADMIN_CHAT_ID = None  # Will be set when admin starts the bot

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('telegram_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SavoliaLoggerBot:
    def __init__(self, token: str):
        self.token = token
        self.bot = Bot(token=token)
        self.application = Application.builder().token(token).build()
        self.session = None
        
        # Statistics storage
        self.stats = {
            'errors': 0,
            'subscriptions': 0,
            'users': 0,
            'messages': 0,
            'uptime_start': datetime.now()
        }
        
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup command and callback handlers"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        self.application.add_handler(CommandHandler("logs", self.logs_command))
        self.application.add_handler(CommandHandler("users", self.users_command))
        self.application.add_handler(CommandHandler("subscriptions", self.subscriptions_command))
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        global ADMIN_CHAT_ID
        ADMIN_CHAT_ID = update.effective_chat.id
        
        keyboard = [
            [InlineKeyboardButton("📊 Status", callback_data="status"),
             InlineKeyboardButton("📈 Statistics", callback_data="stats")],
            [InlineKeyboardButton("📋 Logs", callback_data="logs"),
             InlineKeyboardButton("👥 Users", callback_data="users")],
            [InlineKeyboardButton("💰 Subscriptions", callback_data="subscriptions"),
             InlineKeyboardButton("🔄 Refresh", callback_data="refresh")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🤖 **Savolia AI Logger Bot Ishga tushdi!**\n\n"
            "Bu bot orqali siz quyidagilarni kuzatishingiz mumkin:\n"
            "• 🔥 Backend xatoliklari\n"
            "• 💰 Yangi obunalar\n"
            "• 📊 Sistema statistikasi\n"
            "• 📋 Real-time loglar\n"
            "• 👥 Foydalanuvchilar holatini\n\n"
            "Boshqaruv uchun tugmalarni bosing:",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check backend status"""
        await self.send_status_info(update.effective_chat.id)
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show statistics"""
        await self.send_stats_info(update.effective_chat.id)
    
    async def logs_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show recent logs"""
        await self.send_logs_info(update.effective_chat.id)
    
    async def users_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user information"""
        await self.send_users_info(update.effective_chat.id)
    
    async def subscriptions_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show subscription information"""
        await self.send_subscriptions_info(update.effective_chat.id)
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries from inline keyboards"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "status":
            await self.send_status_info(query.message.chat_id, query.message.message_id)
        elif query.data == "stats":
            await self.send_stats_info(query.message.chat_id, query.message.message_id)
        elif query.data == "logs":
            await self.send_logs_info(query.message.chat_id, query.message.message_id)
        elif query.data == "users":
            await self.send_users_info(query.message.chat_id, query.message.message_id)
        elif query.data == "subscriptions":
            await self.send_subscriptions_info(query.message.chat_id, query.message.message_id)
        elif query.data == "refresh":
            await self.send_main_menu(query.message.chat_id, query.message.message_id)
    
    async def send_main_menu(self, chat_id: int, message_id: int = None):
        """Send main menu"""
        keyboard = [
            [InlineKeyboardButton("📊 Status", callback_data="status"),
             InlineKeyboardButton("📈 Statistics", callback_data="stats")],
            [InlineKeyboardButton("📋 Logs", callback_data="logs"),
             InlineKeyboardButton("👥 Users", callback_data="users")],
            [InlineKeyboardButton("💰 Subscriptions", callback_data="subscriptions"),
             InlineKeyboardButton("🔄 Refresh", callback_data="refresh")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = "🤖 **Savolia AI Monitoring Panel**\n\nTanlang:"
        
        if message_id:
            await self.bot.edit_message_text(
                text=text,
                chat_id=chat_id,
                message_id=message_id,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        else:
            await self.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
    
    async def send_status_info(self, chat_id: int, message_id: int = None):
        """Send backend status information"""
        try:
            # Check backend health
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{RENDER_BACKEND_URL}/health", timeout=10) as response:
                    if response.status == 200:
                        backend_status = "🟢 Online"
                        response_time = "< 1s"
                    else:
                        backend_status = f"🟡 Issues (HTTP {response.status})"
                        response_time = "Slow"
        except Exception as e:
            backend_status = "🔴 Offline"
            response_time = "Timeout"
        
        uptime = datetime.now() - self.stats['uptime_start']
        uptime_str = str(uptime).split('.')[0]
        
        text = f"""📊 **Sistema Holati**

🖥️ **Backend**: {backend_status}
⚡ **Response Time**: {response_time}
⏰ **Bot Uptime**: {uptime_str}
📊 **Xatoliklar**: {self.stats['errors']}
💰 **Obunalar**: {self.stats['subscriptions']}
👥 **Foydalanuvchilar**: {self.stats['users']}
💬 **Xabarlar**: {self.stats['messages']}

🕒 **Oxirgi tekshiruv**: {datetime.now().strftime('%H:%M:%S')}"""

        keyboard = [[InlineKeyboardButton("🔄 Yangilash", callback_data="status"),
                    InlineKeyboardButton("◀️ Orqaga", callback_data="refresh")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if message_id:
            await self.bot.edit_message_text(
                text=text,
                chat_id=chat_id,
                message_id=message_id,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        else:
            await self.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
    
    async def send_stats_info(self, chat_id: int, message_id: int = None):
        """Send detailed statistics"""
        try:
            # Try to get stats from backend
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{RENDER_BACKEND_URL}/api/admin/stats", timeout=10) as response:
                    if response.status == 200:
                        backend_stats = await response.json()
                    else:
                        backend_stats = {"error": "Could not fetch stats"}
        except Exception as e:
            backend_stats = {"error": str(e)}
        
        uptime = datetime.now() - self.stats['uptime_start']
        
        text = f"""📈 **Detallı Statistika**

📊 **Bot Statistikasi**:
• Ishga tushgan: {self.stats['uptime_start'].strftime('%d.%m.%Y %H:%M')}
• Ishlash muddati: {str(uptime).split('.')[0]}
• Xatoliklar: {self.stats['errors']}
• Obunalar: {self.stats['subscriptions']}

🖥️ **Backend Statistikasi**:"""

        if "error" not in backend_stats:
            text += f"""
• Total Users: {backend_stats.get('totalUsers', 'N/A')}
• Active Subscriptions: {backend_stats.get('activeSubscriptions', 'N/A')}
• Messages Today: {backend_stats.get('messagesToday', 'N/A')}
• Revenue This Month: ${backend_stats.get('monthlyRevenue', 'N/A')}"""
        else:
            text += f"\n• Error: {backend_stats['error']}"

        keyboard = [[InlineKeyboardButton("🔄 Yangilash", callback_data="stats"),
                    InlineKeyboardButton("◀️ Orqaga", callback_data="refresh")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if message_id:
            await self.bot.edit_message_text(
                text=text,
                chat_id=chat_id,
                message_id=message_id,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        else:
            await self.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
    
    async def send_logs_info(self, chat_id: int, message_id: int = None):
        """Send recent logs"""
        try:
            # Try to get recent logs from backend
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{RENDER_BACKEND_URL}/api/admin/logs", timeout=10) as response:
                    if response.status == 200:
                        logs_data = await response.json()
                        recent_logs = logs_data.get('logs', [])
                    else:
                        recent_logs = []
        except Exception as e:
            recent_logs = []
        
        text = "📋 **So'nggi Loglar**\n\n"
        
        if recent_logs:
            for log in recent_logs[:5]:  # Show last 5 logs
                timestamp = log.get('timestamp', 'Unknown')
                level = log.get('level', 'INFO')
                message = log.get('message', 'No message')[:100]
                
                emoji = {"ERROR": "🔥", "WARNING": "⚠️", "INFO": "ℹ️"}.get(level, "📄")
                text += f"{emoji} **{level}** - {timestamp}\n`{message}`\n\n"
        else:
            text += "Hozircha loglar mavjud emas yoki backend bilan bog'lanishda muammo."
        
        keyboard = [[InlineKeyboardButton("🔄 Yangilash", callback_data="logs"),
                    InlineKeyboardButton("◀️ Orqaga", callback_data="refresh")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if message_id:
            await self.bot.edit_message_text(
                text=text,
                chat_id=chat_id,
                message_id=message_id,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        else:
            await self.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
    
    async def send_users_info(self, chat_id: int, message_id: int = None):
        """Send user information"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{RENDER_BACKEND_URL}/api/admin/users", timeout=10) as response:
                    if response.status == 200:
                        users_data = await response.json()
                    else:
                        users_data = {"error": "Could not fetch users"}
        except Exception as e:
            users_data = {"error": str(e)}
        
        text = "👥 **Foydalanuvchilar Ma'lumoti**\n\n"
        
        if "error" not in users_data:
            text += f"""📊 **Umumiy Statistika**:
• Jami foydalanuvchilar: {users_data.get('totalUsers', 0)}
• Faol foydalanuvchilar: {users_data.get('activeUsers', 0)}
• Bugun ro'yxatdan o'tganlar: {users_data.get('newUsersToday', 0)}

👑 **Obuna bo'yicha**:
• Free: {users_data.get('freeUsers', 0)}
• Pro: {users_data.get('proUsers', 0)}
• Premium: {users_data.get('premiumUsers', 0)}"""
        else:
            text += f"Xatolik: {users_data['error']}"
        
        keyboard = [[InlineKeyboardButton("🔄 Yangilash", callback_data="users"),
                    InlineKeyboardButton("◀️ Orqaga", callback_data="refresh")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if message_id:
            await self.bot.edit_message_text(
                text=text,
                chat_id=chat_id,
                message_id=message_id,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        else:
            await self.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
    
    async def send_subscriptions_info(self, chat_id: int, message_id: int = None):
        """Send subscription information"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{RENDER_BACKEND_URL}/api/admin/subscriptions", timeout=10) as response:
                    if response.status == 200:
                        subs_data = await response.json()
                    else:
                        subs_data = {"error": "Could not fetch subscriptions"}
        except Exception as e:
            subs_data = {"error": str(e)}
        
        text = "💰 **Obunalar Ma'lumoti**\n\n"
        
        if "error" not in subs_data:
            text += f"""📊 **Umumiy**:
• Faol obunalar: {subs_data.get('activeSubscriptions', 0)}
• Bu oylik daromad: ${subs_data.get('monthlyRevenue', 0)}
• Bugun sotilgan: {subs_data.get('todaySales', 0)}

📈 **Tariflar bo'yicha**:
• Basic ($9.99): {subs_data.get('basicSubs', 0)}
• Pro ($19.99): {subs_data.get('proSubs', 0)}
• Premium ($39.99): {subs_data.get('premiumSubs', 0)}

🔄 **So'nggi obunalar**:"""
            
            recent_subs = subs_data.get('recentSubscriptions', [])
            for sub in recent_subs[:3]:
                text += f"\n• {sub.get('plan', 'Unknown')} - {sub.get('date', 'Unknown')}"
        else:
            text += f"Xatolik: {subs_data['error']}"
        
        keyboard = [[InlineKeyboardButton("🔄 Yangilash", callback_data="subscriptions"),
                    InlineKeyboardButton("◀️ Orqaga", callback_data="refresh")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if message_id:
            await self.bot.edit_message_text(
                text=text,
                chat_id=chat_id,
                message_id=message_id,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        else:
            await self.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
    
    async def notify_error(self, error_message: str, error_type: str = "ERROR"):
        """Send error notification to admin"""
        if ADMIN_CHAT_ID:
            emoji = {"ERROR": "🔥", "WARNING": "⚠️", "INFO": "ℹ️"}.get(error_type, "🔥")
            
            text = f"""{emoji} **{error_type} - Savolia AI**

🕒 **Vaqt**: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
📝 **Xatolik**: 
```
{error_message[:800]}
```

🔧 Backend holatini tekshiring!"""
            
            try:
                await self.bot.send_message(
                    chat_id=ADMIN_CHAT_ID,
                    text=text,
                    parse_mode='Markdown'
                )
                self.stats['errors'] += 1
            except Exception as e:
                logger.error(f"Failed to send error notification: {e}")
    
    async def notify_subscription(self, subscription_data: dict):
        """Send subscription notification to admin"""
        if ADMIN_CHAT_ID:
            plan = subscription_data.get('plan', 'Unknown')
            amount = subscription_data.get('amount', 0)
            user = subscription_data.get('user', 'Unknown')
            
            text = f"""💰 **Yangi Obuna!**

👤 **Foydalanuvchi**: {user}
📦 **Tarif**: {plan}
💵 **Narx**: ${amount}
🕒 **Vaqt**: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}

🎉 Tabriklaymiz! Yangi mijoz!"""
            
            try:
                await self.bot.send_message(
                    chat_id=ADMIN_CHAT_ID,
                    text=text,
                    parse_mode='Markdown'
                )
                self.stats['subscriptions'] += 1
            except Exception as e:
                logger.error(f"Failed to send subscription notification: {e}")
    
    async def start_monitoring(self):
        """Start the monitoring loop"""
        logger.info("Starting Telegram bot monitoring...")
        
        # Start the bot
        await self.application.initialize()
        await self.application.start()
        
        # Start periodic monitoring tasks
        asyncio.create_task(self.periodic_health_check())
        asyncio.create_task(self.periodic_stats_update())
        
        # Start polling
        await self.application.updater.start_polling()
    
    async def periodic_health_check(self):
        """Periodic health check of the backend"""
        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{RENDER_BACKEND_URL}/health", timeout=10) as response:
                        if response.status != 200:
                            await self.notify_error(
                                f"Backend health check failed with status {response.status}",
                                "WARNING"
                            )
            except Exception as e:
                await self.notify_error(f"Backend unreachable: {str(e)}", "ERROR")
            
            # Check every 5 minutes
            await asyncio.sleep(300)
    
    async def periodic_stats_update(self):
        """Periodic stats update"""
        while True:
            try:
                # Update stats from backend
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{RENDER_BACKEND_URL}/api/admin/stats", timeout=10) as response:
                        if response.status == 200:
                            backend_stats = await response.json()
                            self.stats.update({
                                'users': backend_stats.get('totalUsers', 0),
                                'messages': backend_stats.get('totalMessages', 0)
                            })
            except Exception as e:
                logger.warning(f"Failed to update stats: {e}")
            
            # Update every hour
            await asyncio.sleep(3600)
    
    async def stop(self):
        """Stop the bot"""
        await self.application.stop()
        await self.application.shutdown()

# Create webhook endpoint handler for backend integration
class WebhookHandler:
    def __init__(self, bot: SavoliaLoggerBot):
        self.bot = bot
    
    async def handle_error(self, error_data):
        """Handle error webhook from backend"""
        await self.bot.notify_error(
            error_data.get('message', 'Unknown error'),
            error_data.get('level', 'ERROR')
        )
    
    async def handle_subscription(self, subscription_data):
        """Handle subscription webhook from backend"""
        await self.bot.notify_subscription(subscription_data)

async def main():
    """Main function to run the bot"""
    bot = SavoliaLoggerBot(BOT_TOKEN)
    
    try:
        await bot.start_monitoring()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")
    finally:
        await bot.stop()

if __name__ == "__main__":
    print("🤖 Starting Savolia AI Telegram Logger Bot...")
    print(f"Bot Token: {BOT_TOKEN[:20]}...")
    print(f"Backend URL: {RENDER_BACKEND_URL}")
    print("\nPress Ctrl+C to stop the bot")
    
    asyncio.run(main())