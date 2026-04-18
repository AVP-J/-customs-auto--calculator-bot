#!/usr/bin/env python3
"""
Minimal bot starter - simplest possible version.
"""
import os
import sys
from telegram.ext import Application, CommandHandler

# Get token from environment
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TOKEN:
    # Try to load from .env file
    try:
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith('TELEGRAM_BOT_TOKEN='):
                    TOKEN = line.strip().split('=', 1)[1]
                    break
    except:
        pass

if not TOKEN or TOKEN == 'YOUR_BOT_TOKEN_HERE':
    print("ERROR: Bot token not found")
    sys.exit(1)

print(f"Starting bot with token: {TOKEN[:10]}...")

# Create application
app = Application.builder().token(TOKEN).build()

# Add simple handlers
async def start(update, context):
    await update.message.reply_text("🚗 Customs Calculator Bot is running!\nUse /calculate to start.")

async def calculate(update, context):
    await update.message.reply_text("📋 Calculation feature coming soon...")

async def help_cmd(update, context):
    await update.message.reply_text("Help: /start, /calculate, /help")

# Add handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("calculate", calculate))
app.add_handler(CommandHandler("help", help_cmd))

print("Bot is starting...")
print("Press Ctrl+C to stop")

# Run the bot
app.run_polling()