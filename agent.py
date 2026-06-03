#!/usr/bin/env python3
"""OpenClaw Telegram Agent."""
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN=os.getenv("TELEGRAM_BOT_TOKEN", "")
ALLOWED = [int(x) for x in os.getenv("TELEGRAM_USER_ID", "").split(",") if x]

async def call_ai(msg, prov="anthropic"):
    import httpx
    cfg = {
        "anthropic": {
            "url": "https://api.anthropic.com/v1/messages",
            "hdr": {"x-api-key": os.getenv("ANTHROPIC_API_KEY", ""), "anthropic-version": "2023-06-01", "content-type": "application/json"},
            "body": {"model": "claude-sonnet-4-20250514", "max_tokens": 4096, "messages": [{"role": "user", "content": msg}]},
            "get": lambda d: d["content"][0]["text"],
        },
        "deepseek": {
            "url": "https://api.deepseek.com/v1/chat/completions",
            "hdr": {"Authorization": "Bearer " + os.getenv("DEEPSEEK_API_KEY", ""), "Content-Type": "application/json"},
            "body": {"model": "deepseek-chat", "messages": [{"role": "user", "content": msg}], "max_tokens": 4096},
            "get": lambda d: d["choices"][0]["message"]["content"],
        },
    }
    for p in [prov] + [k for k in cfg if k != prov]:
        c = cfg[p]
        if not c["hdr"].get("x-api-key") and not c["hdr"].get("Authorization", "").replace("Bearer ", ""):
            continue
        try:
            async with httpx.AsyncClient(timeout=60) as cli:
                r = await cli.post(c["url"], headers=c["hdr"], json=c["body"])
                r.raise_for_status()
                return c["get"](r.json())
        except:
            continue
    return "All providers failed"

async def start(upd, ctx):
    await upd.message.reply_text("OpenClaw Agent\n\n/start /help /model /providers /reset")

async def help_cmd(upd, ctx):
    await upd.message.reply_text("Commands:\n/start\n/help\n/model [name]\n/providers\n/reset")

async def providers(upd, ctx):
    lines = []
    for n in ["anthropic", "deepseek", "openai"]:
        k = os.getenv(f"{n.upper()}_API_KEY", "")
        lines.append(f"{n}: {'Active' if k else 'No key'}")
    await upd.message.reply_text("\n".join(lines))

async def set_model(upd, ctx):
    if ctx.args:
        m = ctx.args[0].lower()
        if m in ("anthropic", "deepseek", "openai"):
            ctx.user_data["provider"] = m
            await upd.message.reply_text(f"Provider: {m}")
        else:
            await upd.message.reply_text("Unknown. Use /providers")
    else:
        cur = ctx.user_data.get("provider", "anthropic")
        await upd.message.reply_text(f"Current: {cur}")

async def reset(upd, ctx):
    ctx.user_data.clear()
    await upd.message.reply_text("Cleared")

async def msg(upd, ctx):
    if upd.effective_user.id not in ALLOWED:
        await upd.message.reply_text("Unauthorized")
        return
    await upd.message.chat.send_action("typing")
    prov = ctx.user_data.get("provider", "anthropic")
    resp = await call_ai(upd.message.text, prov)
    await upd.message.reply_text(resp[:4000])

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("providers", providers))
    app.add_handler(CommandHandler("model", set_model))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, msg))
    print("OpenClaw Agent started!")
    app.run_polling()

if __name__ == "__main__":
    main()
