# OpenClaw Agent Setup 🐾

Setup AI agent OpenClaw di VPS dengan Telegram bot.

**Official:** https://github.com/nousresearch/openclaw
**Docs:** https://hermes-agent.nousresearch.com/docs/

> OpenClaw adalah versi awal dari Hermes Agent. Sekarang sudah di-migrate.

## Quick Start

```bash
git clone https://github.com/nousresearch/openclaw.git ~/openclaw
cd ~/openclaw
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp config.example.yaml config.yaml
python main.py
```

## Requirements

| Component | Version |
|-----------|---------|
| Python | 3.11+ |
| pip | 22+ |
| OS | Ubuntu 22.04+ |

## Install

### Step 1: System Setup

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git
```

### Step 2: Clone OpenClaw

```bash
git clone https://github.com/nousresearch/openclaw.git ~/openclaw
cd ~/openclaw
```

### Step 3: Python Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Telegram Dependencies

```bash
pip install python-telegram-bot httpx aiohttp
```

### Step 5: Configuration

```bash
cp config.example.yaml config.yaml
nano config.yaml
```

## Configuration

### config.yaml

```yaml
agent:
  name: "MyAgent"
  model: "claude-sonnet-4-20250514"
  provider: "anthropic"
  system_prompt: |
    You are a helpful AI agent.

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
  allowed_users:
    - "${TELEGRAM_USER_ID}"
  mode: "polling"

tools:
  terminal: {enabled: true}
  file: {enabled: true}
  web_search: {enabled: true}
```

## API Key Setup

### Get Keys

| Provider | URL |
|----------|-----|
| Anthropic | https://console.anthropic.com/ |
| OpenAI | https://platform.openai.com/ |
| DeepSeek | https://platform.deepseek.com/ |
| Kimi | https://platform.moonshot.cn/ |

### Set Environment Variables

```bash
cat > ~/openclaw/.env << 'EOF'
ANTHROPIC_API_KEY=*** TELEGRAM_USER_ID=123456789
EOF
source ~/openclaw/.env
```

## Telegram Bot Setup

### Step 1: Create Bot

1. Open Telegram → Search @BotFather
2. Send /newbot
3. Enter name: My AI Agent
4. Enter username: myaiagent_bot (must end _bot)
5. Copy token

### Step 2: Get User ID

1. Search @userinfobot
2. Send any message
3. Copy User ID

### Step 3: Configure

```bash
echo 'TELEGRAM_BOT_TOKEN=*** echo 'TELEGRAM_USER_ID=123456789' >> ~/openclaw/.env
```

Edit ~/openclaw/config.yaml:

```yaml
telegram:
  enabled: true
  token: "YOUR_TOKEN"
  allowed_users:
    - "YOUR_USER_ID"
  mode: "polling"
```

### Step 4: Run

```bash
cd ~/openclaw
source venv/bin/activate
python main.py
```

## Systemd Service

```bash
sudo tee /etc/systemd/system/openclaw.service << 'EOF'
[Unit]
Description=OpenClaw Agent
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

sudo systemctl daemon-reload
sudo systemctl enable openclaw
sudo systemctl start openclaw
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Module not found | pip install -r requirements.txt |
| API key invalid | Check .env file |
| Telegram not connecting | Verify token |
| Service fail | journalctl -u openclaw -e |

## License

MIT
