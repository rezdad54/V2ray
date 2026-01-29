import telegram
from telegram import Bot
from telegram.error import TelegramError
import telegram_config
import os
import datetime
import json
import asyncio
from typing import Dict, Any, Optional

class TelegramBot:
    def __init__(self):
        self.config = telegram_config.TELEGRAM_CONFIG
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN', self.config["bot_token"])
        self.channel_id = os.getenv('TELEGRAM_CHANNEL_ID', self.config["channel_id"])
        self.bot = None
        
    def initialize_bot(self) -> bool:
        """Initialize the Telegram bot"""
        try:
            if not self.bot_token or self.bot_token == "YOUR_BOT_TOKEN_HERE":
                print("⚠️ Telegram bot token not configured")
                return False
                
            if not self.channel_id or self.channel_id == "@YOUR_CHANNEL_HERE":
                print("⚠️ Telegram channel ID not configured")
                return False
                
            self.bot = Bot(token=self.bot_token)
            return True
        except Exception as e:
            print(f"❌ Failed to initialize Telegram bot: {e}")
            return False
    
    def send_message(self, message: str, parse_mode: str = "Markdown") -> bool:
        """Send a message to the Telegram channel"""
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
            print(f"❌ Unexpected error sending Telegram message: {e}")
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
                print("✅ Message sent to Telegram channel")
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
        """Format the update message using the template"""
        template = self.config["templates"]["update_message"]
        
        # Format timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        # Generate protocol breakdown
        protocols_breakdown = ""
        if "protocols" in stats:
            for protocol, count in stats["protocols"].items():
                protocols_breakdown += f"• {protocol.upper()}: {count}\n"
        
        # Generate file URLs
        repo_url = self.config["repo_url"]
        main_file_url = f"{repo_url}/blob/main/All_Configs_Sub.txt"
        base64_file_url = f"{repo_url}/blob/main/All_Configs_base64_Sub.txt"
        
        return template.format(
            total_configs=stats.get("total_configs", 0),
            protocols_count=stats.get("protocols_count", 0),
            timestamp=timestamp,
            main_file_url=main_file_url,
            base64_file_url=base64_file_url,
            protocols_breakdown=protocols_breakdown
        )
    
    def format_error_message(self, error_message: str) -> str:
        """Format the error message using the template"""
        template = self.config["templates"]["error_message"]
        
        return template.format(
            error_message=error_message
        )
    
    def post_success_update(self, stats: Dict[str, Any]) -> bool:
        """Post a success update message to Telegram"""
        message = self.format_update_message(stats)
        return self.send_message(message)
    
    def post_individual_configs(self, configs: list) -> bool:
        """Post each config as a separate Telegram message"""
        if not self.initialize_bot():
            return False
            
        if not configs:
            print("⚠️ No configs to post")
            return False
            
        print(f"📤 Posting {len(configs)} individual configs to Telegram...")
        
        success_count = 0
        for i, config in enumerate(configs):
            try:
                # Format individual config message
                message = self.format_individual_config(config, i+1, len(configs))
                if self.send_message(message):
                    success_count += 1
                
                # Add delay between posts to avoid rate limiting
                import time
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Failed to post config {i+1}: {e}")
        
        print(f"✅ Successfully posted {success_count}/{len(configs)} configs")
        return success_count > 0
    
    def format_individual_config(self, config: str, index: int, total: int) -> str:
        """Format an individual config message"""
        template = """🔗 *Config #{index} of {total}*

`{config}`

📊 *Protocol:* {protocol}
⏰ *Posted:* {timestamp}
🔢 *Config Number:* #{index}
📢 *Telegram Channel:* @V2rays_hub

#V2ray #Config #{protocol} #{index} #@V2rays_hub: {index}"""
        
        # Determine protocol
        protocol = "Unknown"
        if config.startswith("vmess://"):
            protocol = "VMESS"
        elif config.startswith("vless://"):
            protocol = "VLESS"
        elif config.startswith("trojan://"):
            protocol = "TROJAN"
        elif config.startswith("ss://"):
            protocol = "SS"
        elif config.startswith("ssr://"):
            protocol = "SSR"
        elif config.startswith("hy2://"):
            protocol = "HY2"
        elif config.startswith("tuic://"):
            protocol = "TUIC"
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        return template.format(
            index=index,
            total=total,
            config=config,
            protocol=protocol,
            timestamp=timestamp
        )
    
    def post_error_update(self, error_message: str) -> bool:
        """Post an error message to Telegram"""
        message = self.format_error_message(error_message)
        return self.send_message(message)


def analyze_config_stats(config_file_path: str) -> Dict[str, Any]:
    """Analyze config file and return statistics"""
    stats = {
        "total_configs": 0,
        "protocols_count": 0,
        "protocols": {}
    }
    
    try:
        with open(config_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        lines = content.split('\n')
        config_lines = [line for line in lines if line.strip() and not line.startswith('#')]
        
        stats["total_configs"] = len(config_lines)
        
        # Count protocols
        protocols = ["vmess", "vless", "trojan", "ss", "ssr", "hy2", "tuic", "warp://"]
        protocol_counts = {}
        
        for line in config_lines:
            for protocol in protocols:
                if protocol in line:
                    protocol_counts[protocol] = protocol_counts.get(protocol, 0) + 1
                    break
        
        stats["protocols"] = protocol_counts
        stats["protocols_count"] = len(protocol_counts)
        
        return stats
        
    except Exception as e:
        print(f"❌ Error analyzing config stats: {e}")
        return stats