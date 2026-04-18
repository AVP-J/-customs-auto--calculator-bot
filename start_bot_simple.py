#!/usr/bin/env python3
"""
Simple bot starter without event loop issues.
"""
import sys
import os
import asyncio
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load configuration
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not TOKEN or TOKEN == "YOUR_BOT_TOKEN_HERE":
    print("❌ Bot token not set in .env file")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main():
    """Main async function."""
    from telegram.ext import Application
    
    # Create application
    application = Application.builder().token(TOKEN).build()
    
    # Add basic command handlers
    from telegram import Update
    from telegram.ext import CommandHandler
    
    async def start(update: Update, context):
        await update.message.reply_text(
            '🚗 *Customs Calculator Bot запущен!*\n\n'
            'Я помогу рассчитать таможенные платежи для автомобилей из Китая.\n\n'
            '*Команды:*\n'
            '/calculate - Начать расчёт\n'
            '/help - Помощь\n'
            '/history - История расчётов\n\n'
            'Начните с /calculate',
            parse_mode='Markdown'
        )
    
    async def calculate(update: Update, context):
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        keyboard = [
            [InlineKeyboardButton("🚀 НАЧАТЬ ВВОД", callback_data="start_input")],
            [InlineKeyboardButton("ℹ️  О тарифах", callback_data="show_tariffs")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            '🚗 *РАСЧЁТ ТАМОЖЕННЫХ ПЛАТЕЖЕЙ*\n\n'
            'Нажмите *🚀 НАЧАТЬ ВВОД* чтобы начать ввод данных об автомобиле.',
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def help_cmd(update: Update, context):
        await update.message.reply_text(
            '📚 *Помощь*\n\n'
            '*Команды:*\n'
            '/start - Начало работы\n'
            '/calculate - Начать расчёт\n'
            '/help - Эта справка\n'
            '/history - История расчётов\n\n'
            '*Тарифы:*\n'
            '• Бесплатно: 3 расчёта/месяц\n'
            '• Платно: 299 ₸/расчёт\n'
            '• Пакеты: со скидкой до 44%\n'
            '• Подписка: 1,990 ₸/месяц\n\n'
            'Начать: /calculate',
            parse_mode='Markdown'
        )
    
    async def history(update: Update, context):
        await update.message.reply_text(
            '📋 *История расчётов*\n\n'
            'У вас пока нет сохранённых расчётов.\n\n'
            'Сделайте первый расчёт: /calculate',
            parse_mode='Markdown'
        )
    
    # Add callback handler for inline buttons
    from telegram.ext import CallbackQueryHandler
    
    async def button_callback(update: Update, context):
        query = update.callback_query
        await query.answer()
        
        if query.data == "start_input":
            await query.edit_message_text(
                "✅ *Начинаем ввод*\n\n"
                "1️⃣ **Введите марку автомобиля** (например: Li):",
                parse_mode="Markdown"
            )
        elif query.data == "show_tariffs":
            await query.edit_message_text(
                "💰 *Тарифы*\n\n"
                "• Бесплатно: 3 расчёта/месяц\n"
                "• Pay-per-use: 299 ₸/расчёт\n"
                "• Пакеты: 500/1,000/2,000 ₸\n"
                "• Подписка: 1,990 ₸/месяц\n\n"
                "Начать расчёт: /calculate",
                parse_mode="Markdown"
            )
    
    # Add all handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("calculate", calculate))
    application.add_handler(CommandHandler("help", help_cmd))
    application.add_handler(CommandHandler("history", history))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Start polling
    print("✅ Bot started successfully!")
    print("🤖 Bot username: @CustomsCalcKZBot")
    print("📱 Listening for messages...")
    print("Press Ctrl+C to stop")
    
    await application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)