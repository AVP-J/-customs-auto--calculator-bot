#!/usr/bin/env python3
"""
Test script for Customs Calculator Bot.
"""
import asyncio
import logging
from telegram import Bot
from config.config import TELEGRAM_BOT_TOKEN, TELEGRAM_ADMIN_ID

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_bot():
    """Test basic bot functionality."""
    logger.info("Testing bot connection...")
    
    try:
        # Create bot instance
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        
        # Test connection by getting bot info
        bot_info = await bot.get_me()
        logger.info(f"✅ Bot connected successfully!")
        logger.info(f"Bot ID: {bot_info.id}")
        logger.info(f"Bot username: @{bot_info.username}")
        logger.info(f"Bot name: {bot_info.first_name}")
        
        # Send test message to admin
        test_message = (
            "🤖 *Customs Calculator Bot - Тестовое сообщение*\n\n"
            "Бот успешно запущен и готов к работе!\n\n"
            "*Команды:*\n"
            "/start - Начало работы\n"
            "/help - Помощь\n"
            "/calculate - Начать расчёт\n"
            "/history - История расчётов\n\n"
            "Попробуйте отправить /start"
        )
        
        await bot.send_message(
            chat_id=TELEGRAM_ADMIN_ID,
            text=test_message,
            parse_mode="Markdown"
        )
        logger.info("✅ Test message sent to admin")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error testing bot: {e}")
        return False

async def main():
    """Main test function."""
    print("🚀 Starting bot test...")
    success = await test_bot()
    
    if success:
        print("\n✅ Все тесты пройдены успешно!")
        print("\n📱 Теперь вы можете:")
        print("1. Открыть Telegram")
        print("2. Найти бота @CustomsKZBot")
        print("3. Отправить команду /start")
        print("4. Протестировать функционал")
    else:
        print("\n❌ Тесты не пройдены. Проверьте конфигурацию.")

if __name__ == "__main__":
    asyncio.run(main())