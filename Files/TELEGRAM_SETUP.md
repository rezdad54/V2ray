# Telegram Integration Setup Guide

This guide will help you set up the Telegram integration for your V2ray Config Bot.

## Prerequisites

- A Telegram account
- A Telegram channel where the bot will post updates
- Bot token from BotFather

## Step 1: Create a Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Start a chat with BotFather and send `/newbot`
3. Follow the prompts to:
   - Choose a name for your bot (e.g., "V2ray Config Bot")
   - Choose a username for your bot (must end with "bot", e.g., "v2rayconfigbot")
4. BotFather will provide you with a bot token - save this token securely

## Step 2: Create a Telegram Channel

1. Open Telegram and click "New Channel"
2. Choose a name for your channel (e.g., "V2ray Config Updates")
3. Set the channel to public or private as preferred
4. Note the channel username (e.g., `@v2rays_hub`)

## Step 3: Configure Bot Permissions

1. Add your bot to the channel as an administrator:
   - Go to your channel settings
   - Click "Administrators"
   - Click "Add Admin"
   - Search for your bot's username
   - Grant the bot permission to "Post Messages"

## Step 4: Configure Environment Variables

Create a `.env` file in the `Files` directory with the following content:

```bash
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHANNEL_ID=@your_channel_here
```

Or update the `telegram_config.py` file directly:

```python
TELEGRAM_CONFIG = {
    "bot_token": "your_bot_token_here",
    "channel_id": "@your_channel_here",
    # ... rest of configuration
}
```

## Step 5: Test the Integration

Run the test script to verify everything is working:

```bash
cd Files
source venv/bin/activate
python -c "
from telegram_utils import TelegramBot
bot = TelegramBot()
if bot.initialize_bot():
    print('✅ Bot initialized successfully')
    if bot.send_message('🔧 Test message from V2ray Config Bot'):
        print('✅ Test message sent successfully!')
    else:
        print('❌ Failed to send test message')
else:
    print('❌ Bot initialization failed')
"
```

## Step 6: Configure GitHub Actions (Optional)

If you want the bot to run automatically via GitHub Actions, ensure your secrets are configured in the repository:

1. Go to your GitHub repository → Settings → Secrets and variables → Actions
2. Add the following secrets:
   - `TELEGRAM_BOT_TOKEN`: Your bot token
   - `TELEGRAM_CHANNEL_ID`: Your channel ID (e.g., `@v2rays_hub`)

## Troubleshooting

### Common Issues

1. **"Bot is not a member of the chat"**
   - Make sure the bot is added to the channel as an administrator
   - Check that the channel username is correct

2. **"Forbidden: bot can't send messages to bots"**
   - Ensure the bot has permission to post messages in the channel
   - Check channel privacy settings

3. **Network connectivity issues**
   - The bot includes retry logic with exponential backoff
   - Check your internet connection if messages fail

4. **Message formatting issues**
   - The bot uses Markdown formatting
   - Ensure your message content doesn't contain invalid Markdown syntax

## Features

- ✅ Automatic posting of config updates to Telegram
- ✅ Retry logic for network connectivity issues
- ✅ Beautiful message templates with statistics
- ✅ Error handling and error messages
- ✅ Secure configuration (secrets removed from code)

The bot will automatically post updates every time the config files are updated via the GitHub Actions workflow.