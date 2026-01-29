# GitHub Actions Setup Guide for V2ray Config Bot

This guide provides detailed step-by-step instructions for setting up automatic Telegram notifications via GitHub Actions.

## Prerequisites

- GitHub repository with your V2ray Config Bot code
- Telegram bot created and configured (see `TELEGRAM_SETUP.md`)
- Telegram channel ready for notifications

## Step 1: Configure GitHub Secrets

GitHub Secrets are encrypted environment variables that allow you to store sensitive information securely.

### 1.1 Navigate to Repository Settings
1. Go to your GitHub repository
2. Click on **Settings** tab
3. In the left sidebar, click on **Secrets and variables** → **Actions**

### 1.2 Add Required Secrets
Click **New repository secret** and add the following secrets:

#### TELEGRAM_BOT_TOKEN
- **Name:** `TELEGRAM_BOT_TOKEN`
- **Value:** Your Telegram bot token (from @BotFather)
- Example: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`

#### TELEGRAM_CHANNEL_ID
- **Name:** `TELEGRAM_CHANNEL_ID`
- **Value:** Your Telegram channel ID (e.g., `@v2rays_hub`)
- Note: Include the `@` symbol if using channel username

### 1.3 Verify Secrets
After adding both secrets, your repository secrets should look like this:
```
TELEGRAM_BOT_TOKEN: [hidden]
TELEGRAM_CHANNEL_ID: [hidden]
```

## Step 2: Understanding the GitHub Actions Workflow

The workflow is defined in `.github/workflows/main.yml`:

```yaml
name: Update Configs
permissions: write-all

on:
  push:
    branches:
      - main
  schedule:
    - cron: "*/12 * * * *"

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code  
      uses: actions/checkout@v2  
      with:
        fetch-depth: 0  
        persist-credentials: true  

    - name: Set up Python  
      uses: actions/setup-python@v2  
      with:
        python-version: '3.11'

    - name: Install dependencies  
      working-directory: Files  
      run: pip install -r requirements.txt

    - name: Run Python scripts  
      working-directory: Files  
      env:
        TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
        TELEGRAM_CHANNEL_ID: ${{ secrets.TELEGRAM_CHANNEL_ID }}
      run: |
        python app.py
        python sort.py

    - name: Commit and push changes
      uses: EndBug/add-and-commit@v7
      with:
        author_name: "GitHub Actions"
        author_email: "actions@github.com"
        message: "Updated 11 minutes Ago🤝"
        add: "."
        pull: "NO-PULL"
        push: true
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Workflow Explanation

**Triggers:**
- **On push:** Runs when code is pushed to the main branch
- **Schedule:** Runs every 12 minutes (`*/12 * * * *`)

**Steps:**
1. **Checkout code:** Gets the latest code from repository
2. **Set up Python:** Installs Python 3.11
3. **Install dependencies:** Installs required Python packages
4. **Run scripts:** Executes the config fetching and Telegram notification logic
5. **Commit changes:** Automatically commits any updated config files

## Step 3: Schedule Configuration

The workflow uses cron syntax for scheduling:

```yaml
schedule:
  - cron: "*/12 * * * *"
```

This means:
- Runs every 12 minutes
- 24/7 operation

### Customizing the Schedule

You can modify the cron expression to suit your needs:

| Schedule | Cron Expression | Description |
|----------|----------------|-------------|
| Every 5 minutes | `*/5 * * * *` | More frequent updates |
| Every hour | `0 * * * *` | Hourly updates |
| Every 6 hours | `0 */6 * * *` | 4 times per day |
| Daily at 2 AM | `0 2 * * *` | Once per day |

**Cron Format:** `minute hour day month day-of-week`

## Step 4: Manual Testing

### 4.1 Test the Workflow Manually
1. Go to your repository → **Actions** tab
2. Click on **Update Configs** workflow
3. Click **Run workflow** → **Run workflow**
4. Monitor the execution in real-time

### 4.2 Check Workflow Results
After the workflow completes:
- Check the **Actions** tab for execution logs
- Verify config files are updated in your repository
- Check your Telegram channel for notifications

## Step 5: Monitoring and Troubleshooting

### 5.1 Monitoring Workflow Execution
- **Actions tab:** View all workflow runs and their status
- **Notifications:** GitHub will notify you of workflow failures
- **Telegram channel:** Receive success/error notifications

### 5.2 Common Issues and Solutions

#### Issue: Workflow fails to start
**Solution:** Check repository permissions and workflow file syntax

#### Issue: Telegram notifications not working
**Solution:**
1. Verify secrets are correctly configured
2. Check bot has permission to post in channel
3. Review workflow logs for error messages

#### Issue: Config files not updating
**Solution:**
1. Check internet connectivity in workflow logs
2. Verify config sources are accessible
3. Review error messages in workflow execution

#### Issue: Too many commits
**Solution:** Adjust the schedule to run less frequently

## Step 6: Advanced Configuration

### 6.1 Environment-Specific Settings
You can create different workflows for different branches:

```yaml
on:
  push:
    branches: [main, develop]
  schedule:
    - cron: "*/12 * * * *"
```

### 6.2 Conditional Execution
Add conditions to control when the workflow runs:

```yaml
- name: Run Python scripts  
  working-directory: Files  
  env:
    TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
    TELEGRAM_CHANNEL_ID: ${{ secrets.TELEGRAM_CHANNEL_ID }}
  run: |
    python app.py
    python sort.py
  if: github.ref == 'refs/heads/main'
```

### 6.3 Multiple Schedules
Run at different intervals:

```yaml
schedule:
  - cron: "0 9 * * *"    # Daily at 9 AM
  - cron: "0 21 * * *"   # Daily at 9 PM
```

## Step 7: Security Considerations

### 7.1 Secret Management
- Never commit secrets to code
- Use GitHub Secrets for all sensitive data
- Regularly rotate bot tokens

### 7.2 Repository Permissions
- Use minimal required permissions
- Review third-party actions before use
- Enable branch protection rules

## Step 8: Performance Optimization

### 8.1 Caching Dependencies
Add caching to speed up workflow execution:

```yaml
- name: Cache pip packages
  uses: actions/cache@v2
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-
```

### 8.2 Workflow Timeouts
GitHub Actions have a 6-hour timeout limit. For long-running processes, consider:
- Breaking into smaller jobs
- Using faster config sources
- Optimizing Python code

## Verification Checklist

- [ ] GitHub Secrets configured correctly
- [ ] Workflow file exists in `.github/workflows/main.yml`
- [ ] Manual workflow run successful
- [ ] Config files updated in repository
- [ ] Telegram notifications received
- [ ] Schedule running as expected

## Support

If you encounter issues:
1. Check workflow logs in GitHub Actions
2. Review error messages carefully
3. Verify Telegram bot configuration
4. Ensure config sources are accessible

The bot will now automatically fetch configs and send Telegram notifications according to your schedule!