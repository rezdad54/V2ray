#!/usr/bin/env python3
"""
Test script for Telegram posting functionality
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from telegram_utils import TelegramBot

def test_telegram_posting():
    """Test Telegram posting functionality"""
    print("🧪 Testing Telegram posting functionality...")
    
    telegram_bot = TelegramBot()
    
    # Test with sample configs
    sample_configs = [
        "vmess://eyJhZGQiOiI0Ni4yNDYuMTI2LjE1NCIsImFpZCI6IjAiLCJhbHBuIjoiIiwiZnAiOiIiLCJob3N0IjoiIiwiaWQiOiJmMmZkMDc4Ni0xMDU5LTRmNjQtZDU0ZS0zZjNhNTY4YzZjNjgiLCJpbnNlY3VyZSI6IjAiLCJuZXQiOiJ3cyIsInBhdGgiOiIvIiwicG9ydCI6IjQ0MyIsInBzIjoiVGVsZWdyYW0gXHUwMDNkIEBLSUFfTkVUIPCfpYAiLCJzY3kiOiJhdXRvIiwic25pIjoiIiwidGxzIjoiIiwidHlwZSI6Ii0tLSIsInYiOiIyIn0=",
        "vless://1af1162b-045e-4a00-aeb1-8cef98d5670d@ir.peeknet.my.id:504?type=tcp&path=%2F&host=iranserver.com.teloxy.my.id&headerType=http&security=none#NetAccount",
        "ss://YWVzLTI1Ni1nY206dGVzdEBzZXJ2ZXI6ODA4MA==#ExampleSS"
    ]
    
    print(f"📤 Testing posting {len(sample_configs)} configs...")
    
    # Test individual config posting
    success = telegram_bot.post_individual_configs(sample_configs)
    
    if success:
        print("✅ Telegram posting test PASSED")
    else:
        print("❌ Telegram posting test FAILED")
        print("⚠️ Note: This may be due to missing Telegram bot configuration")
        print("   Make sure to set TELEGRAM_BOT_TOKEN and TELEGRAM_CHANNEL_ID environment variables")
    
    return success

if __name__ == "__main__":
    test_telegram_posting()