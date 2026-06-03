# OpenClaw AI Agent Setup 🤖

Complete guide to deploy OpenClaw AI agent on VPS with Telegram bot. Supports Python3 and Node.js.

## What is OpenClaw?

OpenClaw is an open-source AI agent framework by Nous Research. It supports multiple LLM providers, persistent memory, and runs on Telegram, Discord, Slack, and more.

**Official:** https://github.com/nousresearch/openclaw

## Quick Start

```bash
# Clone
git clone https://github.com/nousresearch/openclaw.git ~/openclaw
cd ~/openclaw

# Python setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp config.example.yaml config.yaml
nano config.yaml

# Run
python main.py
```

## Requirements

### Python Setup

| Component | Version |
|-----------|---------|
| Python | 3.10+ |
| pip | 22+ |
| OS | Ubuntu 22.04+ |

### Node.js Setup (Alternative)

| Component | Version |
|-----------|---------|
| Node.js | 18+ |
| npm | 9+ |
| OS | Ubuntu 22.04+ |

## Installation

### Method 1: Python3 (Recommended)

```bash
# Install dependencies
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git

# Clone OpenClaw
git clone https://github.com/nousresearch/openclaw.git ~/openclaw
cd ~/openclaw

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install packages
pip install --upgrade pip
pip install -r requirements.txt

# Install Telegram dependencies
pip install python-telegram-bot httpx aiohttp

# Verify
python -c "import telegram; print(f'Telegram bot: {telegram.__version__}')"
```

### Method 2: Node.js

```bash
# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo bash -
sudo apt install -y nodejs

# Clone OpenClaw
git clone https://github.com/nousresearch/openclaw.git ~/openclaw
cd ~/openclaw

# Install packages
npm install

# Verify
node -v && npm -v
```

## API Key Setup

### Get API Keys

| Provider | URL | Pricing |
|----------|-----|---------|
| Anthropic | https://console.anthropic.com/ | $3/1M input |
| OpenAI | https://platform.openai.com/ | $2.50/1M input |
| DeepSeek | https://platform.deepseek.com/ | $0.14/1M input |
| Kimi | https://platform.moonshot.cn/ | ¥12/1M input |
| OpenRouter | https://openrouter.ai/ | Varies |

### Set Environment Variables

```bash
# Create .env file
cat > ~/openclaw/.env << 'EOF'
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
DEEPSEEK_API_KEY=sk-...
KIMI_API_KEY=sk-...
TELEGRAM_BOT_TOKEN=123456...port TELEGRAM_USER_ID=123456789
EOF

# Load environment
source ~/openclaw/.env
```

## Configuration

### Config File

Edit `~/openclaw/config.yaml`:

```yaml
# ============================================
# Agent
# ============================================
agent:
  name: "MyAgent"
  description: "My AI agent"
  model: "claude-sonnet-4-20250514"
  provider: "anthropic"
  system_prompt: |
    You are a helpful AI agent.
    Be concise and actionable.

# ============================================
# Providers
# ============================================
providers:
  anthropic:
    api_key: "${ANTHROPIC_API_KEY}"
    model: "claude-sonnet-4-20250514"
    max_tokens: 4096
  openai:
    api_key: "${OPENAI_API_KEY}"
    model: "gpt-4o"
    max_tokens: 4096
  deepseek:
    api_key: "${DEEPSEEK_API_KEY}"
    model: "deepseek-chat"
    base_url: "https://api.deepseek.com/v1"
    max_tokens: 4096
  kimi:
    api_key: "${KIMI_API_KEY}"
    model: "moonshot-v1-8k"
    base_url: "https://api.moonshot.cn/v1"
    max_tokens: 4096
  openrouter:
    api_key: "${OPENROUTER_API_KEY}"
    model: "anthropic/claude-sonnet-4"

# ============================================
# Telegram
# ============================================
telegram:
  enabled: true
  token: "${TELEGRAM_BOT_TOKEN}"
  allowed_users:
    - "${TELEGRAM_USER_ID}"
  mode: "polling"

# ============================================
# Tools
# ============================================
tools:
  terminal: {enabled: true}
  file: {enabled: true}
  web_search: {enabled: true}
  browser: {enabled: false}
```

## Telegram Bot Setup

### Step 1: Create Bot

1. Open **Telegram**
2. Search **@BotFather**
3. Send `/newbot`
4. Enter bot name (e.g., "My AI Agent")
5. Enter username (must end with `_bot`)
6. Copy the **token**

### Step 2: Get User ID

1. Search **@userinfobot** on Telegram
2. Send any message
3. Copy your **User ID**

### Step 3: Configure

```bash
# Set in .env
echo 'TELEGRAM_BOT_TOKEN=123456...port echo 'TELEGRAM_USER_ID=123456789' >> ~/openclaw/.env

# Set in config.yaml
nano ~/openclaw/config.yaml
```

### Step 4: Create Agent Script

Create `~/openclaw/telegram_agent.py`:

```python
#!/usr/bin/env python3
"""
OpenClaw Telegram Agent
Multi-provider AI agent with Telegram integration.
"""
import os
import asyncio
from telegram import Update
from telegram.ext import (
    Application, CommandHandler,
    MessageHandler, filters,
    ContextTypes,
)

TELEGRAM_TOKEN=os.get...SERS = [int(x) for x in os.getenv("TELEGRAM_USER_ID", "0").split(",")]

async def call_llm(message, provider="anthropic"):
    """Call LLM with fallback."""
    import httpx
    
    providers = {
        "anthropic": {
            "url": "https://api.anthropic.com/v1/messages",
            "headers": {"x-api-key": os.getenv("ANTHROPIC_API_KEY", ""), "anthropic-version": "2023-06-01", "content-type": "application/json"},
            "body": {"model": "claude-sonnet-4-20250514", "max_tokens": 4096, "messages": [{"role": "user", "content": message}]},
            "extract": lambda d: d["content"][0]["text"],
        },
        "deepseek": {
            "url": "https://api.deepseek.com/v1/chat/completions",
            "headers": {"Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY', '')}", "Content-Type": "application/json"},
            "body": {"model": "deepseek-chat", "messages": [{"role": "user", "content": message}], "max_tokens": 4096},
            "extract": lambda d: d["choices"][0]["message"]["content"],
        },
    }
    
    for p in [provider] + [k for k in providers if k != provider]:
        cfg = providers[p]
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(cfg["url"], headers=cfg["headers"], json=cfg["body"])
                resp.raise_for_status()
                return cfg["extract"](resp.json())
        except Exception as e:
            continue
    return "Error: All providers failed"

async def start(update, context):
    await update.message.reply_text("🤖 *OpenClaw Agent*\n\nKirim pesan untuk chat.\n\n/start - Mulai\n/help - Bantuan\n/model - Ganti model", parse_mode="Markdown")

async def help_cmd(update, context):
    await update.message.reply_text("📖 Commands:\n\n/start - Mulai\n/help - Bantuan\n/model [nama] - Ganti model\n/reset - Reset session", parse_mode="Markdown")

async def set_model(update, context):
    if context.args:
        model = context.args[0].lower()
        if model in ("anthropic", "deepseek", "openai"):
            context.user_data["provider"] = model
            await update.message.reply_text(f"✅ Model: *{model}*", parse_mode="Markdown")

async def reset(update, context):
    context.user_data.clear()
    await update.message.reply_text("🔄 Session reset.")

async def handle_message(update, context):
    user_id = update.effective_user.id
    if user_id not in ALLOWED_USERS:
        await update.message.reply_text("❌ Unauthorized")
        return
    
    message = update.message.text
    if not message:
        return
    
    await update.message.chat.send_action("typing")
    provider = context.user_data.get("provider", "anthropic")
    
    try:
        response = await call_llm(message, provider)
        if len(response) > 4000:
            for i in range(0, len(response), 4000):
                await update.message.reply_text(response[i:i+4000])
        else:
            await update.message.reply_text(response)
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)[:100]}")

def main():
    print("=" * 50)
    print("  OpenClaw Telegram Agent")
    print("=" * 50)
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("model", set_model))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot started!")
    app.run_polling()

if __name__ == "__main__":
    main()
```

### Step 5: Run

```bash
cd ~/openclaw
source venv/bin/activate
export $(cat .env | xargs)
python main.py
```

### Step 6: Test

1. Open Telegram
2. Find your bot
3. Send `/start`
4. Send any message

## Systemd Service (Production)

### Create Service

```bash
sudo tee /etc/systemd/system/openclaw-telegram.service << 'EOF'
[Unit]
Description=OpenClaw Telegram Agent
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/openclaw
EnvironmentFile=/root/openclaw/.env
ExecStart=/root/openclaw/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
```

### Manage Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable openclaw-telegram
sudo systemctl start openclaw-telegram
sudo systemctl status openclaw-telegram
sudo journalctl -u openclaw-telegram -f
```

## Telegram Commands

```
/start          — Start conversation
/help           — Show commands
/model          — View current model
/model deepseek — Switch to DeepSeek
/model anthropic — Switch to Claude
/reset          — Reset conversation
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | `pip install -r requirements.txt` |
| `API key invalid` | Check `.env` file |
| `Telegram not connecting` | Verify token: `curl https://api.telegram.org/bot<TOKEN>/getMe` |
| `Unauthorized user` | Check `TELEGRAM_USER_ID` in `.env` |
| Service won't start | `sudo journalctl -u openclaw-telegram -e` |

## License

MIT
