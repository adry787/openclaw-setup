# OpenClaw AI Agent Setup 🤖

Complete guide to deploy OpenClaw AI agent on VPS with Telegram bot. Supports Python3 and Node.js.

## What is OpenClaw?

OpenClaw is an open-source AI agent framework by Nous Research. Supports multiple LLM providers, persistent memory, runs on Telegram, Discord, Slack.

**Official:** https://github.com/nousresearch/openclaw

---

## Requirements

| Component | Python | Node.js |
|-----------|--------|---------|
| Version | 3.10+ | 18+ |
| Package Manager | pip | npm |
| Telegram Library | python-telegram-bot | telegraf |
| HTTP Client | httpx | axios |
| OS | Ubuntu 22.04+ | Ubuntu 22.04+ |

---

## Quick Start

### Python

```bash
git clone https://github.com/nousresearch/openclaw.git ~/openclaw
cd ~/openclaw
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp config.example.yaml config.yaml
python main.py
```

### Node.js

```bash
git clone https://github.com/nousresearch/openclaw.git ~/openclaw
cd ~/openclaw
npm install
cp config.example.yaml config.yaml
node main.js
```

---

## Installation

### Method 1: Python3

```bash
# Install Python
sudo apt update && sudo apt install -y python3 python3-pip python3-venv git

# Clone OpenClaw
git clone https://github.com/nousresearch/openclaw.git ~/openclaw
cd ~/openclaw

# Virtual environment
python3 -m venv venv
source venv/bin/activate

# Install packages
pip install --upgrade pip
pip install -r requirements.txt
pip install python-telegram-bot httpx aiohttp
```

### Method 2: Node.js

```bash
# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo bash -
sudo apt install -y nodejs git

# Verify
node -v && npm -v

# Clone OpenClaw
git clone https://github.com/nousresearch/openclaw.git ~/openclaw
cd ~/openclaw

# Install packages
npm install
npm install telegraf axios dotenv

# Verify
npm ls telegraf
```

---

## API Key Setup

| Provider | URL | Pricing |
|----------|-----|---------|
| Anthropic | https://console.anthropic.com/ | $3/1M |
| OpenAI | https://platform.openai.com/ | $2.50/1M |
| DeepSeek | https://platform.deepseek.com/ | $0.14/1M |
| Kimi | https://platform.moonshot.cn/ | ¥12/1M |
| OpenRouter | https://openrouter.ai/ | Varies |

```bash
# Create .env
cat > ~/openclaw/.env << 'EOF'
ANTHROPIC_API_KEY=sk-ant...port TELEGRAM_USER_ID=123456789
EOF
```

---

## Configuration

### config.yaml

```yaml
agent:
  name: "MyAgent"
  model: "claude-sonnet-4-20250514"
  provider: "anthropic"
  system_prompt: |
    You are a helpful AI agent.
    Be concise and actionable.

providers:
  anthropic:
    api_key: "${ANTHROPIC_API_KEY}"
    model: "claude-sonnet-4-20250514"
  deepseek:
    api_key: "${DEEPSEEK_API_KEY}"
    model: "deepseek-chat"
    base_url: "https://api.deepseek.com/v1"

telegram:
  enabled: true
  token: "${TELEGRAM_BOT_TOKEN}"
  allowed_users: ["${TELEGRAM_USER_ID}"]
  mode: "polling"
```

---

## Telegram Bot Setup

### Step 1: Create Bot

1. Open Telegram → Search **@BotFather**
2. Send `/newbot`
3. Enter name: `My AI Agent`
4. Enter username: `myaiagent_bot` (harus `_bot`)
5. Copy **token**

### Step 2: Get User ID

1. Search **@userinfobot**
2. Send any message
3. Copy **User ID**

### Step 3: Configure

```bash
echo 'TELEGRAM_BOT_TOKEN=*** echo 'TELEGRAM_USER_ID=123456789' >> ~/openclaw/.env
```

---

## Python Agent

Create `~/openclaw/telegram_agent.py`:

```python
#!/usr/bin/env python3
"""OpenClaw Telegram Agent - Python"""
import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN=*** = [int(x) for x in os.getenv("TELEGRAM_USER_ID", "0").split(",")]

async def call_llm(message, provider="anthropic"):
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
        except: continue
    return "Error: All providers failed"

async def start(update, context):
    await update.message.reply_text("🤖 *OpenClaw Agent*\n\n/start - Mulai\n/help - Bantuan\n/model - Ganti model", parse_mode="Markdown")

async def help_cmd(update, context):
    await update.message.reply_text("📖 /start /help /model [nama] /reset", parse_mode="Markdown")

async def set_model(update, context):
    if context.args:
        model = context.args[0].lower()
        if model in ("anthropic", "deepseek"):
            context.user_data["provider"] = model
            await update.message.reply_text(f"✅ Model: *{model}*", parse_mode="Markdown")

async def handle_message(update, context):
    if update.effective_user.id not in ALLOWED_USERS:
        await update.message.reply_text("❌ Unauthorized")
        return
    await update.message.chat.send_action("typing")
    provider = context.user_data.get("provider", "anthropic")
    response = await call_llm(update.message.text, provider)
    await update.message.reply_text(response[:4000])

def main():
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

```bash
python telegram_agent.py
```

---

## Node.js Agent

Create `~/openclaw/telegram_agent.js`:

```javascript
#!/usr/bin/env node
/**
 * OpenClaw Telegram Agent - Node.js
 */
require('dotenv').config();
const { Telegraf } = require('telegraf');
const axios = require('axios');

const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
const ALLOWED_USERS = (process.env.TELEGRAM_USER_ID || '').split(',').map(Number);

const providers = {
  anthropic: {
    url: 'https://api.anthropic.com/v1/messages',
    headers: (key) => ({
      'x-api-key': key,
      'anthropic-version': '2023-06-01',
      'content-type': 'application/json',
    }),
    body: (msg) => ({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 4096,
      messages: [{ role: 'user', content: msg }],
    }),
    extract: (data) => data.content[0].text,
  },
  deepseek: {
    url: 'https://api.deepseek.com/v1/chat/completions',
    headers: (key) => ({
      Authorization: `Bearer ${key}`,
      'Content-Type': 'application/json',
    }),
    body: (msg) => ({
      model: 'deepseek-chat',
      messages: [{ role: 'user', content: msg }],
      max_tokens: 4096,
    }),
    extract: (data) => data.choices[0].message.content,
  },
  openai: {
    url: 'https://api.openai.com/v1/chat/completions',
    headers: (key) => ({
      Authorization: `Bearer ${key}`,
      'Content-Type': 'application/json',
    }),
    body: (msg) => ({
      model: 'gpt-4o',
      messages: [{ role: 'user', content: msg }],
      max_tokens: 4096,
    }),
    extract: (data) => data.choices[0].message.content,
  },
};

async function callLLM(message, provider = 'anthropic') {
  const keyMap = {
    anthropic: 'ANTHROPIC_API_KEY',
    deepseek: 'DEEPSEEK_API_KEY',
    openai: 'OPENAI_API_KEY',
  };

  const order = [provider, ...Object.keys(providers).filter((p) => p !== provider)];

  for (const p of order) {
    const cfg = providers[p];
    const apiKey = process.env[keyMap[p]];
    if (!apiKey) continue;

    try {
      const resp = await axios.post(cfg.url, cfg.body(message), {
        headers: cfg.headers(apiKey),
        timeout: 60000,
      });
      return cfg.extract(resp.data);
    } catch (e) {
      console.error(`Provider ${p} failed:`, e.message);
    }
  }
  return 'Error: All providers failed';
}

// User data store
const userData = {};

const bot = new Telegraf(BOT_TOKEN);

bot.command('start', (ctx) => {
  ctx.reply(
    '🤖 *OpenClaw Agent*\n\n' +
      'Kirim pesan untuk chat.\n\n' +
      '/start - Mulai\n' +
      '/help - Bantuan\n' +
      '/model - Ganti model\n' +
      '/reset - Reset session',
    { parse_mode: 'Markdown' }
  );
});

bot.command('help', (ctx) => {
  ctx.reply(
    '📖 Commands:\n\n' +
      '/start - Mulai\n' +
      '/help - Bantuan\n' +
      '/model [nama] - Ganti model\n' +
      '/reset - Reset session'
  );
});

bot.command('model', (ctx) => {
  const args = ctx.message.text.split(' ').slice(1);
  if (args.length > 0) {
    const model = args[0].toLowerCase();
    if (['anthropic', 'deepseek', 'openai'].includes(model)) {
      userData[ctx.from.id] = { ...userData[ctx.from.id], provider: model };
      ctx.reply(`✅ Model: *${model}*`, { parse_mode: 'Markdown' });
    } else {
      ctx.reply('❌ Model tidak dikenal');
    }
  } else {
    const current = userData[ctx.from.id]?.provider || 'anthropic';
    ctx.reply(`Model saat ini: *${current}*\n\nGanti: /model deepseek`, { parse_mode: 'Markdown' });
  }
});

bot.command('reset', (ctx) => {
  delete userData[ctx.from.id];
  ctx.reply('🔄 Session reset.');
});

bot.on('text', async (ctx) => {
  // Check authorization
  if (!ALLOWED_USERS.includes(ctx.from.id)) {
    ctx.reply('❌ Unauthorized');
    return;
  }

  // Skip commands
  if (ctx.message.text.startsWith('/')) return;

  const provider = userData[ctx.from.id]?.provider || 'anthropic';

  try {
    ctx.replyWithChatAction('typing');
    const response = await callLLM(ctx.message.text, provider);

    // Split long messages
    if (response.length > 4000) {
      for (let i = 0; i < response.length; i += 4000) {
        ctx.reply(response.substring(i, i + 4000));
      }
    } else {
      ctx.reply(response);
    }
  } catch (e) {
    ctx.reply(`❌ Error: ${e.message.substring(0, 100)}`);
  }
});

console.log('Bot started!');
bot.launch();

// Graceful stop
process.once('SIGINT', () => bot.stop('SIGINT'));
process.once('SIGTERM', () => bot.stop('SIGTERM'));
```

```bash
node telegram_agent.js
```

---

## Systemd Service

### Python Service

```bash
sudo tee /etc/systemd/system/openclaw-python.service << 'EOF'
[Unit]
Description=OpenClaw Telegram Agent (Python)
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/openclaw
EnvironmentFile=/root/openclaw/.env
ExecStart=/root/openclaw/venv/bin/python telegram_agent.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable openclaw-python
sudo systemctl start openclaw-python
```

### Node.js Service

```bash
sudo tee /etc/systemd/system/openclaw-node.service << 'EOF'
[Unit]
Description=OpenClaw Telegram Agent (Node.js)
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/openclaw
EnvironmentFile=/root/openclaw/.env
ExecStart=/usr/bin/node telegram_agent.js
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable openclaw-node
sudo systemctl start openclaw-node
```

---

## Telegram Commands

```
/start          — Start conversation
/help           — Show commands
/model          — View current model
/model deepseek — Switch to DeepSeek
/model anthropic — Switch to Claude
/reset          — Reset session
```

---

## Comparison

| Feature | Python | Node.js |
|---------|--------|---------|
| Telegram Library | python-telegram-bot | telegraf |
| HTTP Client | httpx | axios |
| Async Support | asyncio | native |
| Memory Usage | ~50MB | ~30MB |
| Startup Time | ~2s | ~1s |
| Best For | ML integration | Lightweight bots |

---

## Troubleshooting

| Issue | Python | Node.js |
|-------|--------|---------|
| Module not found | `pip install -r requirements.txt` | `npm install` |
| API key invalid | Check `.env` | Check `.env` |
| Telegram error | `curl https://api.telegram.org/bot<TOKEN>/getMe` | Same |
| Service fail | `journalctl -u openclaw-python -e` | `journalctl -u openclaw-node -e` |

---

## License

MIT
