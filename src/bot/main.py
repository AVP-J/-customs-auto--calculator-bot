"""
Main entry point for Customs Calculator Bot.
"""
import asyncio
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler

from config.config import TELEGRAM_BOT_TOKEN, LOGGING_CONFIG, DEBUG
from src.bot.handlers import start_handler, tariffs_handler, help_handler, calculate_handler, free_calculate_handler, history_handler
from src.bot.step_handlers import start_step_by_step, handle_callback_query, handle_text_input, handle_voice_message


# Configure logging
import logging.config
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

def main():
    """Start the bot."""
    logger.info("Starting Customs Calculator Bot...")
    
    # Force IPv4 for Telegram API (VPS has IPv6 issues)
    from telegram.request import HTTPXRequest
    request = HTTPXRequest(
        connection_pool_size=1,
    )
    
    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).request(request).build()
    
    # Add command handlers (English)
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("tariffs", tariffs_handler))
    application.add_handler(CommandHandler("help", help_handler))
    application.add_handler(CommandHandler("calculate", calculate_handler))
    application.add_handler(CommandHandler("free_calculate", free_calculate_handler))
    application.add_handler(CommandHandler("history", history_handler))
    
    # Add callback query handler for inline buttons (step-by-step interface)
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    
    # Add message handler for text messages (step input, not a command)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_input))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice_message))
    
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
