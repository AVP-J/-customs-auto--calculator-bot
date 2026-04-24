"""
Command handlers for Customs Calculator Bot.
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    user = update.effective_user
    logger.info(f"User {user.id} ({user.username}) started the bot")
    
    first_name = user.first_name or ""
    
    welcome_text = (
        f"🚗 *Добро пожаловать, {first_name}!*\n\n"
        "Я — KZ Customs Calculator Bot, помогу рассчитать таможенные платежи "
        "на легковые автомобили для ввоза в Республику Казахстан.\n\n"
        "📋 *Как это работает:*\n\n"
        "1️⃣ Отправьте /calculate\n"
        "2️⃣ Введите данные об автомобиле\n"
        "3️⃣ Получите расчёт\n\n"
        "💰 Тарифы:\n"
        "• Новичок: 3 расчёта/месяц (бесплатно)\n"
        "• Оплата по факту: 299 ₸/расчёт\n"
        "• Пакеты: 500/1,000/2,000 ₸ (скидка до 44%)\n"
        "• Подписка PRO: 2,990 ₸/месяц\n"
        "Подробнее по оплате — /tariffs\n\n"
        "Больше информации о Калькуляторе — /help\n\n"
        "Начнём? Отправьте /calculate\n\n"
        "Если вы таможенный брокер, здесь может быть ваша реклама.\n"
        "Напишите нам: info@calc.kz"
    )
    
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def tariffs_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /tariffs command."""
    user = update.effective_user
    logger.info(f"User {user.id} requested tariffs")
    
    tariffs_text = (
        "💰 *ТАРИФЫ*\n\n"
        "*1. НОВИЧОК (Бесплатно)*\n"
        "• 3 расчёта в месяц\n"
        "• Все типы автомобилей\n"
        "• Базовый расчёт\n\n"
        "*2. ОПЛАТА ПО ФАКТУ*\n"
        "• 299 ₸ за 1 расчёт\n"
        "• Все типы автомобилей\n"
        "• Детальный отчёт\n\n"
        "*3. ПАКЕТЫ РАСЧЁТОВ*\n"
        "• 500 ₸ = 2 расчёта (250 ₸/расчёт, скидка 16%)\n"
        "• 1,000 ₸ = 5 расчётов (200 ₸/расчёт, скидка 33%)\n"
        "• 2,000 ₸ = 12 расчётов (167 ₸/расчёт, скидка 44%)\n"
        "• Детальный отчёт\n\n"
        "*4. ПОДПИСКА PRO*\n"
        "• 2,990 ₸/месяц\n"
        "• Неограниченные расчёты\n"
        "• Экспорт в PDF\n"
        "• Приоритетная поддержка\n\n"
        "Начать расчёт: /calculate\n\n"
        "Если вы таможенный брокер, здесь может быть ваша реклама.\n"
        "Напишите нам: info@calc.kz"
    )
    
    await update.message.reply_text(tariffs_text, parse_mode="Markdown")


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    help_text = (
        "📚 *ПОМОЩЬ ПО KZ CUSTOMS CALCULATOR BOT*\n\n"
        "📋 *КОМАНДЫ*\n"
        "/start — Начало работы\n"
        "/calculate — Начать расчёт\n"
        "/help — Эта справка\n"
        "/tariffs — Стоимость услуг\n\n"
        "⚙️ *КАК РАБОТАЕТ РАСЧЁТ*\n"
        "1. Вводите данные об автомобиле\n"
        "2. Бот рассчитывает таможенные платежи\n"
        "3. Получаете детальный отчёт\n\n"
        "💱 Калькулятор использует средневзвешенный курс валюты "
        "на момент формирования расчёта.\n\n"
        "⚖️ Расчёт калькулятора не является основанием для заполнения декларации, "
        "но максимально приближен к реальным цифрам.\n\n"
        "📞 Для более детальных расчётов рекомендуется обратиться "
        "к Таможенному брокеру.\n\n"
        "Начать расчёт: /calculate\n\n"
        "Если вы таможенный брокер, здесь может быть ваша реклама.\n"
        "Напишите нам: info@calc.kz"
    )
    
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def calculate_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /calculate command - show start button."""
    user = update.effective_user
    logger.info(f"User {user.id} opened calculation")
    
    from .keyboards import get_start_calc_keyboard
    
    await update.message.reply_text(
        "🧮 *РАСЧЁТ ТАМОЖЕННЫХ ПЛАТЕЖЕЙ*\n\n"
        "После нажатия кнопки вам нужно будет ввести данные об автомобиле:\n\n"
        "1. Марка\n"
        "2. Модель\n"
        "3. Тип двигателя\n"
        "4. Год и месяц выпуска\n"
        "5. Валюта покупки\n"
        "6. Стоимость автомобиля\n"
        "7. Стоимость доставки\n\n"
        "Нажмите 🚀 НАЧАТЬ РАСЧЁТ чтобы продолжить",
        parse_mode="Markdown",
        reply_markup=get_start_calc_keyboard()
    )

async def history_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /history command - show calculation history."""
    user = update.effective_user
    logger.info(f"User {user.id} requested history")
    
    # TODO: Fetch from database
    history_text = (
        "📋 *ИСТОРИЯ РАСЧЁТОВ*\n\n"
        "У вас пока нет сохранённых расчётов.\n\n"
        "Сделайте первый расчёт: /calculate\n\n"
        "*Бесплатные расчёты осталось:* 3/3\n"
        "*Платные расчёты использовано:* 0\n"
        "*Активная подписка:* Нет"
    )
    
    await update.message.reply_text(history_text, parse_mode="Markdown")
