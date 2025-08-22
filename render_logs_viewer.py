#!/usr/bin/env python3
"""
🖥️ RENDER LOGS REAL-TIME VIEWER FOR SAVOLIA AI
📊 Advanced log streaming and monitoring from Render.com

Features:
- 📡 Real-time log streaming from Render API
- 🔍 Advanced log filtering and search
- 📈 Log analytics and patterns detection
- 🚨 Error detection and alerting
- 💾 Log storage and archiving
- 📊 Performance metrics extraction
- 🎯 Custom log parsing
- 🔄 Auto-refresh and polling
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, AsyncGenerator
import re
from dataclasses import dataclass
import sqlite3
from urllib.parse import urlencode
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
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
    """Render.com API client for log streaming"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.render.com/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.session = None
    
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
    
    async def get_logs(self, service_id: str, start_time: Optional[datetime] = None, 
                      end_time: Optional[datetime] = None, limit: int = 100) -> List[LogEntry]:
        """Get logs for a specific service"""
        try:
            # Default to last hour if no time specified
            if not start_time:
                start_time = datetime.now() - timedelta(hours=1)
            if not end_time:
                end_time = datetime.now()
            
            params = {
                "startTime": start_time.isoformat(),
                "endTime": end_time.isoformat(),
                "limit": limit
            }
            
            url = f"{self.base_url}/services/{service_id}/logs?" + urlencode(params)
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    logs = []
                    
                    for log_data in data.get('data', []):
                        log_entry = LogEntry(
                            timestamp=datetime.fromisoformat(log_data.get('timestamp', '').replace('Z', '+00:00')),
                            level=self.extract_log_level(log_data.get('message', '')),
                            message=log_data.get('message', ''),
                            service_id=service_id,
                            source=log_data.get('source', ''),
                            raw_data=log_data
                        )
                        logs.append(log_entry)
                    
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
    
    async def stream_logs_realtime(self, service_id: str) -> AsyncGenerator[LogEntry, None]:
        """Stream logs in real-time with polling"""
        last_check = datetime.now() - timedelta(minutes=5)
        
        while True:
            try:
                current_time = datetime.now()
                new_logs = await self.get_logs(service_id, last_check, current_time, limit=50)
                
                for log in new_logs:
                    if log.timestamp > last_check:
                        yield log
                
                last_check = current_time
                await asyncio.sleep(10)  # Poll every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in log streaming: {e}")
                await asyncio.sleep(30)  # Wait longer on error

class LogAnalyzer:
    """Advanced log analysis and pattern detection"""
    
    def __init__(self):
        self.error_patterns = [
            r'error\s*:',
            r'exception\s*:',
            r'failed\s+to',
            r'cannot\s+',
            r'timeout',
            r'connection\s+refused',
            r'500\s+internal\s+server\s+error',
            r'404\s+not\s+found',
            r'403\s+forbidden',
            r'401\s+unauthorized'
        ]
        
        self.performance_patterns = [
            r'response\s+time\s*:\s*(\d+\.?\d*)ms',
            r'duration\s*:\s*(\d+\.?\d*)ms',
            r'processed\s+in\s+(\d+\.?\d*)ms',
            r'took\s+(\d+\.?\d*)ms'
        ]
    
    def analyze_logs(self, logs: List[LogEntry]) -> Dict:
        """Analyze logs and extract insights"""
        analysis = {
            'total_logs': len(logs),
            'error_count': 0,
            'warning_count': 0,
            'info_count': 0,
            'debug_count': 0,
            'errors': [],
            'performance_metrics': [],
            'patterns': {},
            'timeline': {}
        }
        
        for log in logs:
            # Count by level
            if log.level == 'ERROR':
                analysis['error_count'] += 1
                analysis['errors'].append({
                    'timestamp': log.timestamp.isoformat(),
                    'message': log.message[:200]  # Truncate long messages
                })
            elif log.level == 'WARNING':
                analysis['warning_count'] += 1
            elif log.level == 'INFO':
                analysis['info_count'] += 1
            elif log.level == 'DEBUG':
                analysis['debug_count'] += 1
            
            # Extract performance metrics
            for pattern in self.performance_patterns:
                matches = re.findall(pattern, log.message, re.IGNORECASE)
                if matches:
                    analysis['performance_metrics'].extend([float(m) for m in matches])
            
            # Timeline analysis (logs per hour)
            hour_key = log.timestamp.strftime('%Y-%m-%d %H:00')
            analysis['timeline'][hour_key] = analysis['timeline'].get(hour_key, 0) + 1
        
        # Calculate average performance
        if analysis['performance_metrics']:
            analysis['avg_response_time'] = sum(analysis['performance_metrics']) / len(analysis['performance_metrics'])
            analysis['max_response_time'] = max(analysis['performance_metrics'])
            analysis['min_response_time'] = min(analysis['performance_metrics'])
        
        return analysis
    
    def detect_anomalies(self, logs: List[LogEntry]) -> List[Dict]:
        """Detect anomalies in logs"""
        anomalies = []
        
        # Check for error spikes
        error_logs = [log for log in logs if log.level == 'ERROR']
        if len(error_logs) > 10:  # More than 10 errors in the time period
            anomalies.append({
                'type': 'error_spike',
                'severity': 'high',
                'message': f'High error rate detected: {len(error_logs)} errors',
                'details': error_logs[:5]  # First 5 errors
            })
        
        # Check for repeated errors
        error_messages = {}
        for log in error_logs:
            key = log.message[:100]  # First 100 chars as key
            error_messages[key] = error_messages.get(key, 0) + 1
        
        for message, count in error_messages.items():
            if count > 3:  # Same error repeated more than 3 times
                anomalies.append({
                    'type': 'repeated_error',
                    'severity': 'medium',
                    'message': f'Repeated error detected {count} times',
                    'details': message
                })
        
        return anomalies

class LogDatabase:
    """SQLite database for storing and querying logs"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database for log storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS render_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                service_id TEXT,
                level TEXT,
                message TEXT,
                source TEXT,
                raw_data TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_render_logs_timestamp 
            ON render_logs(timestamp)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_render_logs_level 
            ON render_logs(level)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_render_logs_service 
            ON render_logs(service_id)
        ''')
        
        conn.commit()
        conn.close()
    
    def store_logs(self, logs: List[LogEntry]):
        """Store logs in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for log in logs:
            cursor.execute('''
                INSERT OR IGNORE INTO render_logs 
                (timestamp, service_id, level, message, source, raw_data)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                log.timestamp,
                log.service_id,
                log.level,
                log.message,
                log.source,
                json.dumps(log.raw_data)
            ))
        
        conn.commit()
        conn.close()
    
    def get_recent_logs(self, service_id: str = None, hours: int = 24, level: str = None) -> List[LogEntry]:
        """Get recent logs from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT timestamp, service_id, level, message, source, raw_data
            FROM render_logs 
            WHERE timestamp >= datetime('now', '-{} hours')
        '''.format(hours)
        
        params = []
        if service_id:
            query += ' AND service_id = ?'
            params.append(service_id)
        
        if level:
            query += ' AND level = ?'
            params.append(level)
        
        query += ' ORDER BY timestamp DESC LIMIT 1000'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        logs = []
        for row in rows:
            log = LogEntry(
                timestamp=datetime.fromisoformat(row[0]),
                service_id=row[1],
                level=row[2],
                message=row[3],
                source=row[4],
                raw_data=json.loads(row[5]) if row[5] else {}
            )
            logs.append(log)
        
        conn.close()
        return logs

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
        
        return f"{emoji} **{log.level}** `{timestamp}`\n```\n{message}\n```"
    
    @staticmethod
    def format_log_summary(analysis: Dict) -> str:
        """Format log analysis summary for Telegram"""
        return f"""
📊 **RENDER LOGS ANALYSIS**
━━━━━━━━━━━━━━━━━━━━━━━

📈 **Statistics:**
• Total logs: {analysis['total_logs']}
• 🔥 Errors: {analysis['error_count']}
• ⚠️ Warnings: {analysis['warning_count']}
• ℹ️ Info: {analysis['info_count']}
• 🔍 Debug: {analysis['debug_count']}

⚡ **Performance:**
• Avg response: {analysis.get('avg_response_time', 0):.2f}ms
• Max response: {analysis.get('max_response_time', 0):.2f}ms

🕒 **Time Range:** Last 24 hours
"""
    
    @staticmethod
    def format_recent_logs(logs: List[LogEntry], limit: int = 10) -> str:
        """Format recent logs for Telegram"""
        if not logs:
            return "📭 Логлар топилмади"
        
        text = f"📋 **SO'NGGI {min(len(logs), limit)} LOGLAR**\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        for log in logs[:limit]:
            text += TelegramLogFormatter.format_log_entry(log) + "\n\n"
        
        if len(logs) > limit:
            text += f"... ва яна {len(logs) - limit} логлар"
        
        return text

# Example usage and testing
async def test_render_logs():
    """Test function for Render logs integration"""
    # You need to set your Render API key
    api_key = "YOUR_RENDER_API_KEY"  # Replace with actual API key
    
    if api_key == "YOUR_RENDER_API_KEY":
        print("⚠️ Please set your Render API key to test log streaming")
        return
    
    async with RenderAPIClient(api_key) as client:
        # Get services
        services = await client.get_services()
        print(f"Found {len(services)} services:")
        for service in services:
            print(f"  - {service.name} ({service.id}) - {service.type}")
        
        if services:
            # Get logs for the first service
            service = services[0]
            print(f"\nGetting logs for {service.name}...")
            
            logs = await client.get_logs(service.id, limit=20)
            print(f"Retrieved {len(logs)} logs")
            
            # Analyze logs
            analyzer = LogAnalyzer()
            analysis = analyzer.analyze_logs(logs)
            
            print("\nLog Analysis:")
            print(f"  Errors: {analysis['error_count']}")
            print(f"  Warnings: {analysis['warning_count']}")
            print(f"  Info: {analysis['info_count']}")
            
            # Format for Telegram
            formatter = TelegramLogFormatter()
            summary = formatter.format_log_summary(analysis)
            print("\nTelegram formatted summary:")
            print(summary)

if __name__ == "__main__":
    print("🖥️ Render Logs Viewer Test")
    asyncio.run(test_render_logs())