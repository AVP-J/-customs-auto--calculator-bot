#!/bin/bash
# Simple script to start Customs Calculator Bot

cd "$(dirname "$0")"

echo "🚀 Starting Customs Calculator Bot..."
echo "Bot: @CustomsCalcKZBot"
echo "Time: $(date)"
echo ""

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found"
    exit 1
fi

# Check if bot token is set
if grep -q "YOUR_BOT_TOKEN_HERE" .env; then
    echo "❌ Bot token not set in .env file"
    echo "Please replace YOUR_BOT_TOKEN_HERE with your actual token"
    exit 1
fi

# Start the bot
echo "📱 Starting bot in polling mode..."
echo "Press Ctrl+C to stop"
echo ""

python3 -c "
import asyncio
import logging
from telegram.ext import Application

# Load configuration
import os
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def main():
    # Create application
    application = Application.builder().token(TOKEN).build()
    
    # Add basic command handlers
    from telegram import Update
    from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, filters
    
    async def start(update: Update, context):
        await update.message.reply_text('🚗 Customs Calculator Bot запущен! Используйте /calculate для начала расчёта.')
    
    async def calculate(update: Update, context):
        await update.message.reply_text('📋 Начинаем расчёт... (функционал в разработке)')
    
    async def help_cmd(update: Update, context):
        await update.message.reply_text('📚 Помощь: /start, /calculate, /help')
    
    # Add handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('calculate', calculate))
    application.add_handler(CommandHandler('help', help_cmd))
    
    # Start polling
    print('✅ Bot started successfully!')
    print('🤖 Bot is listening for messages...')
    await application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
"