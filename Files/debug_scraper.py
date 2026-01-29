#!/usr/bin/env python3
"""
Debug script for Telegram channel scraping functionality
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from telegram_scraper import TelegramScraper

def debug_scraper():
    """Debug the Telegram channel scraping functionality"""
    print("🐛 Debugging Telegram channel scraping...")
    
    scraper = TelegramScraper()
    
    try:
        url = "https://t.me/s/NetAccount"
        print(f"🌐 Testing {url}...")
        
        response = scraper.session.get(url)
        response.raise_for_status()
        
        print(f"✅ Status Code: {response.status_code}")
        print(f"📄 Content Length: {len(response.content)}")
        
        # Save HTML content to file for inspection
        with open('debug_telegram.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print("📁 Saved HTML content to debug_telegram.html")
        
        # Parse with BeautifulSoup
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find message containers
        messages = soup.find_all('div', class_=lambda x: x and ('tgme_widget_message' in x or 'js-widget_message' in x))
        print(f"📨 Found {len(messages)} message containers")
        
        # Check code blocks
        code_blocks = soup.find_all('code')
        print(f"💻 Found {len(code_blocks)} code blocks")
        
        # Show first few code blocks
        for i, code_block in enumerate(code_blocks[:5]):
            code_text = code_block.get_text()
            print(f"  Code {i+1}: {code_text[:100]}...")
        
        # Check for config patterns in the entire HTML
        import re
        config_patterns = [
            r'vmess://[A-Za-z0-9+/=]+',
            r'vless://[A-Za-z0-9+/=]+',
            r'trojan://[A-Za-z0-9+/=]+',
            r'ss://[A-Za-z0-9+/=]+',
            r'ssr://[A-Za-z0-9+/=]+',
            r'hy2://[A-Za-z0-9+/=]+',
            r'tuic://[A-Za-z0-9+/=]+'
        ]
        
        all_configs = []
        for pattern in config_patterns:
            matches = re.findall(pattern, response.text)
            all_configs.extend(matches)
            if matches:
                print(f"🔍 Found {len(matches)} configs with pattern: {pattern}")
                for match in matches[:3]:
                    print(f"   - {match[:50]}...")
        
        print(f"📊 Total configs found in HTML: {len(all_configs)}")
        
        scraper.close()
        return len(all_configs) > 0
        
    except Exception as e:
        print(f"❌ Error during debugging: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = debug_scraper()
    if success:
        print("\n✅ Debugging completed - configs found!")
    else:
        print("\n❌ Debugging completed - no configs found")