"""
Main entry point for Customs Calculator Bot.
"""
import asyncio
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler

from config.config import TELEGRAM_BOT_TOKEN, LOGGING_CONFIG, DEBUG
from src.bot.handlers import start_handler, tariffs_handler, help_handler, calculate_handler, history_handler
from src.bot.step_handlers import start_step_by_step, handle_callback_query, handle_text_input
from src.bot.messages import text_message_handler

# Configure logging
import logging.config
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

def main():
    """Start the bot."""
    logger.info("Starting Customs Calculator Bot...")
    
    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add English command handlers
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("tariffs", tariffs_handler))
    application.add_handler(CommandHandler("help", help_handler))
    application.add_handler(CommandHandler("calculate", calculate_handler))
    application.add_handler(CommandHandler("history", history_handler))
    
    # Russian commands via message handler (python-telegram-bot doesn't support Cyrillic commands)
    application.add_handler(MessageHandler(
        filters.Regex(r"^/старт($|\s)"), start_handler
    ))
    application.add_handler(MessageHandler(
        filters.Regex(r"^/тарифы($|\s)"), tariffs_handler
    ))
    application.add_handler(MessageHandler(
        filters.Regex(r"^/помощь($|\s)"), help_handler
    ))
    application.add_handler(MessageHandler(
        filters.Regex(r"^/рассчитать($|\s)"), calculate_handler
    ))
    
    # Add callback query handler for inline buttons (step-by-step interface)
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    
    # Add message handler for text messages (price input, text without commands)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_input))
    
    # Start the bot
    if DEBUG:
        logger.info("Starting in polling mode (debug)...")
        application.run_polling(allowed_updates=["message", "callback_query"])
    else:
        logger.info("Starting in webhook mode (production)...")
        # Webhook configuration will be added later
        application.run_webhook(
            listen="0.0.0.0",
            port=8443,
            url_path=TELEGRAM_BOT_TOKEN,
            webhook_url=f"https://customs.kz/{TELEGRAM_BOT_TOKEN}"
        )

if __name__ == "__main__":
    main()
