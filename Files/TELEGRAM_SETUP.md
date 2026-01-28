# Telegram Integration Setup Guide

This guide will help you set up the Telegram bot integration for automatic posting of V2ray config updates to your Telegram channel.

## Prerequisites

1. A Telegram account
2. A Telegram channel where you want to post updates
3. BotFather access to create a bot

## Step-by-Step Setup

### 1. Create a Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Start a chat with BotFather
3. Send `/newbot` command
4. Follow the prompts to name your bot
5. Copy the bot token provided by BotFather (it will look like `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Create a Telegram Channel

1. Open Telegram and click "New Channel"
2. Set a name and description for your channel
3. Make the channel public or private as preferred
4. Note the channel username (e.g., `@myv2rayconfigs`) or get the channel ID

### 3. Configure Bot Permissions

1. Add your bot to the channel as an administrator
2. Give the bot permission to post messages

### 4. Configure GitHub Secrets

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add the following secrets:

**Secret Name:** `TELEGRAM_BOT_TOKEN`
**Secret Value:** Your bot token from BotFather

**Secret Name:** `TELEGRAM_CHANNEL_ID`
**Secret Value:** Your channel username (e.g., `@myv2rayconfigs`) or channel ID

### 5. Update Configuration (Optional)

If you prefer to use environment variables instead of GitHub secrets, you can update the `telegram_config.py` file:

```python
TELEGRAM_CONFIG = {
    "bot_token": "YOUR_ACTUAL_BOT_TOKEN",
    "channel_id": "@YOUR_CHANNEL_USERNAME",
    # ... rest of configuration
}
```

## Testing the Setup

1. The GitHub Actions workflow will run automatically every 12 minutes
2. After the first successful run, check your Telegram channel for the update message
3. If no message appears, check the GitHub Actions logs for errors

## Message Template Customization

You can customize the message templates in `telegram_config.py`:

```python
"templates": {
    "update_message": """Your custom message template here...""",
    "error_message": """Your custom error template here..."""
}
```

## Available Template Variables

### Success Message Variables:
- `{total_configs}` - Total number of configs found
- `{protocols_count}` - Number of different protocols
- `{timestamp}` - Current timestamp
- `{main_file_url}` - URL to main config file
- `{base64_file_url}` - URL to base64 config file
- `{protocols_breakdown}` - Breakdown of protocols with counts
- `{next_update_time}` - Time of next scheduled update

### Error Message Variables:
- `{error_message}` - Error description
- `{next_update_time}` - Time of next scheduled update

## Troubleshooting

### Common Issues:

1. **Bot token not working**
   - Verify the token is correct
   - Ensure the bot is active

2. **Channel access denied**
   - Make sure the bot is added to the channel as admin
   - Check channel privacy settings

3. **No messages posted**
   - Check GitHub Actions logs for errors
   - Verify secrets are correctly set

4. **Markdown formatting issues**
   - Ensure your message template uses valid Markdown syntax
   - Avoid special characters that might break formatting

## Security Notes

- Never commit your bot token or channel ID to the repository
- Always use GitHub Secrets for sensitive information
- Regularly rotate your bot token for security

## Support

If you encounter issues, check:
- GitHub Actions workflow logs
- Telegram bot status
- Channel permissions

For persistent issues, create an issue in the repository with detailed error information.