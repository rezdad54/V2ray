#!/usr/bin/env python3
"""
MTProto Telegram Bot
Posts MTProto proxies to a dedicated Telegram channel
"""

import telegram
from telegram import Bot
from telegram.error import TelegramError
import telegram_config
import os
import datetime
import asyncio
from typing import Dict, Any, Optional

class MTProtoTelegramBot:
    def __init__(self):
        self.config = telegram_config.MTPROTO_CONFIG
        self.bot_token = os.getenv('MTPROTO_BOT_TOKEN', self.config["bot_token"])
        self.channel_id = os.getenv('MTPROTO_CHANNEL_ID', self.config["channel_id"])
        self.bot = None
        
    def initialize_bot(self) -> bool:
        """Initialize the MTProto Telegram bot"""
        try:
            if not self.bot_token or self.bot_token == "YOUR_MTPROTO_BOT_TOKEN_HERE":
                print("⚠️ MTProto Telegram bot token not configured")
                return False
                
            if not self.channel_id or self.channel_id == "@YOUR_MTPROTO_CHANNEL_HERE":
                print("⚠️ MTProto Telegram channel ID not configured")
                return False
                
            self.bot = Bot(token=self.bot_token)
            return True
        except Exception as e:
            print(f"❌ Failed to initialize MTProto Telegram bot: {e}")
            return False
    
    def send_message(self, message: str, parse_mode: str = "Markdown") -> bool:
        """Send a message to the MTProto Telegram channel"""
        if not self.initialize_bot():
            return False
            
        try:
            # Use asyncio to run the async function
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self._send_message_async(message, parse_mode))
            loop.close()
            return result
        except Exception as e:
            print(f"❌ Unexpected error sending MTProto Telegram message: {e}")
            return False
    
    async def _send_message_async(self, message: str, parse_mode: str = "Markdown") -> bool:
        """Async method to send message"""
        max_retries = 3
        retry_delay = 5  # seconds
        
        for attempt in range(max_retries):
            try:
                await self.bot.send_message(
                    chat_id=self.channel_id,
                    text=message,
                    parse_mode=parse_mode,
                    disable_web_page_preview=True
                )
                print("✅ Message sent to MTProto Telegram channel")
                return True
            except TelegramError as e:
                print(f"❌ Attempt {attempt + 1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    print(f"🔄 Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    print("❌ All retry attempts failed")
                    return False
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                return False
    
    def format_update_message(self, stats: Dict[str, Any]) -> str:
        """Format the MTProto update message"""
        template = self.config["templates"]["update_message"]
        
        # Format timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        return template.format(
            total_proxies=stats.get("total_proxies", 0),
            website_proxies=stats.get("website_proxies", 0),
            telegram_proxies=stats.get("telegram_proxies", 0),
            timestamp=timestamp
        )
    
    def format_error_message(self, error_message: str) -> str:
        """Format the MTProto error message"""
        template = self.config["templates"]["error_message"]
        
        return template.format(
            error_message=error_message
        )
    
    def post_success_update(self, stats: Dict[str, Any]) -> bool:
        """Post a success update message to MTProto Telegram channel"""
        message = self.format_update_message(stats)
        return self.send_message(message)
    
    def post_individual_proxies(self, proxies: list) -> bool:
        """Post each MTProto proxy as a separate Telegram message"""
        if not self.initialize_bot():
            return False
            
        if not proxies:
            print("⚠️ No MTProto proxies to post")
            return False
            
        print(f"📤 Posting {len(proxies)} MTProto proxies to Telegram...")
        
        success_count = 0
        for i, proxy in enumerate(proxies):
            try:
                # Format individual proxy message
                message = self.format_individual_proxy(proxy, i+1, len(proxies))
                if self.send_message(message):
                    success_count += 1
                
                # Add delay between posts to avoid rate limiting
                import time
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Failed to post MTProto proxy {i+1}: {e}")
        
        print(f"✅ Successfully posted {success_count}/{len(proxies)} MTProto proxies")
        return success_count > 0
    
    def format_individual_proxy(self, proxy: str, index: int, total: int) -> str:
        """Format an individual MTProto proxy message"""
        # Clean the proxy string to remove problematic characters for Markdown
        clean_proxy = proxy.replace('`', '\\`').replace('*', '\\*').replace('_', '\\_')
        
        template = """🔗 MTProto Proxy #{index}

`{proxy}`

⏰ Posted: {timestamp}
📢 Telegram Channel: @MTProtoProxieshub

#MTProto #Proxy #{index}"""
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        return template.format(
            index=index,
            total=total,
            proxy=clean_proxy,
            timestamp=timestamp
        )
    
    def post_error_update(self, error_message: str) -> bool:
        """Post an error message to MTProto Telegram channel"""
        message = self.format_error_message(error_message)
        return self.send_message(message)


def analyze_mtproto_stats(proxy_file_path: str) -> Dict[str, Any]:
    """Analyze MTProto proxy file and return statistics"""
    stats = {
        "total_proxies": 0,
        "website_proxies": 0,
        "telegram_proxies": 0
    }
    
    try:
        with open(proxy_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        lines = content.split('\n')
        proxy_lines = [line for line in lines if line.strip() and not line.startswith('#')]
        
        stats["total_proxies"] = len(proxy_lines)
        
        # Count proxies by type (basic classification)
        tg_proxies = [line for line in proxy_lines if line.startswith('tg://')]
        http_proxies = [line for line in proxy_lines if line.startswith('http://')]
        https_proxies = [line for line in proxy_lines if line.startswith('https://')]
        
        stats["tg_proxies"] = len(tg_proxies)
        stats["http_proxies"] = len(http_proxies)
        stats["https_proxies"] = len(https_proxies)
        
        return stats
        
    except Exception as e:
        print(f"❌ Error analyzing MTProto stats: {e}")
        return stats