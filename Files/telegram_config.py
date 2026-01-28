# Telegram Bot Configuration
TELEGRAM_CONFIG = {
    # Telegram Bot Token (get from @BotFather)
    "bot_token": "YOUR_BOT_TOKEN_HERE",
    
    # Telegram Channel ID (e.g., @yourchannelname or channel ID)
    "channel_id": "@YOUR_CHANNEL_HERE",
    
    # Message templates
    "templates": {
        "update_message": """🚀 *V2ray Config Update* 🚀

📊 *Statistics:*
• Total Configs: {total_configs}
• Protocols: {protocols_count}
• Last Updated: {timestamp}

🔗 *Download Links:*
• [Main Config File]({main_file_url})
• [Base64 Version]({base64_file_url})

📋 *Protocol Breakdown:*
{protocols_breakdown}

⏰ *Next Update:* {next_update_time}

#V2ray #Proxy #Configs #Update
""",
        
        "error_message": """❌ *V2ray Config Update Failed* ❌

⚠️ Error occurred while fetching configs:
{error_message}

🔄 *Next Attempt:* {next_update_time}

#V2ray #Error #UpdateFailed
"""
    },
    
    # Update schedule information (for message template)
    "update_schedule": "Every 12 minutes",
    
    # GitHub repository URL for file links
    "repo_url": "https://github.com/rezdad54/V2ray"
}