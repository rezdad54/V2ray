import requests
import re
import base64
from bs4 import BeautifulSoup
import time
import os

class TelegramScraper:
    def __init__(self):
        self.session = requests.Session()
        # Set headers to mimic a real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def scrape_channel(self, channel_username, limit=20):
        """Scrape configs from a Telegram channel using web interface"""
        try:
            url = f"https://t.me/s/{channel_username}"
            print(f"🌐 Scraping {url}...")
            
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            configs = []
            config_patterns = [
                r'vmess://[A-Za-z0-9+/=]+',
                r'vless://[A-Za-z0-9+/=]+',
                r'trojan://[A-Za-z0-9+/=]+',
                r'ss://[A-Za-z0-9+/=]+',
                r'ssr://[A-Za-z0-9+/=]+',
                r'hy2://[A-Za-z0-9+/=]+',
                r'tuic://[A-Za-z0-9+/=]+'
            ]
            
            # Search for config patterns in the entire HTML content (like debug script)
            html_text = response.text
            
            # Decode HTML entities first
            from html import unescape
            html_text = unescape(html_text)
            
            # Check for config links in the entire HTML
            for pattern in config_patterns:
                matches = re.findall(pattern, html_text)
                configs.extend(matches)
            
            # Also check for base64 encoded configs
            base64_pattern = r'[A-Za-z0-9+/]{20,}={0,2}'
            potential_configs = re.findall(base64_pattern, html_text)
            for config in potential_configs:
                # Try to decode and check if it's a valid config
                try:
                    decoded = base64.b64decode(config).decode('utf-8', errors='ignore')
                    if any(proto in decoded for proto in ['vmess', 'vless', 'trojan', 'ss', 'ssr']):
                        configs.append(config)
                except:
                    pass
            
            # Remove duplicates
            unique_configs = list(set(configs))
            print(f"📡 Scraped {len(unique_configs)} configs from {channel_username}")
            return unique_configs
            
        except Exception as e:
            print(f"❌ Error scraping channel {channel_username}: {e}")
            return []
    
    def scrape_multiple_channels(self, channels, limit_per_channel=20):
        """Scrape configs from multiple Telegram channels"""
        all_configs = []
        
        for channel in channels:
            print(f"🔍 Scraping configs from {channel}...")
            configs = self.scrape_channel(channel, limit_per_channel)
            all_configs.extend(configs)
            # Add delay to avoid rate limiting
            time.sleep(2)
        
        return all_configs
    
    def close(self):
        """Close the session"""
        self.session.close()


def scrape_telegram_channels_sync(channels, limit_per_channel=20):
    """Synchronous wrapper for Telegram channel scraping"""
    scraper = TelegramScraper()
    
    try:
        configs = scraper.scrape_multiple_channels(channels, limit_per_channel)
        scraper.close()
        return configs
    except Exception as e:
        print(f"❌ Error in synchronous Telegram scraping: {e}")
        return []
