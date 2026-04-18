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
    
    welcome_text = (
        "🚗 *Добро пожаловать в Customs Calculator Bot!*\n\n"
        "Я помогу рассчитать таможенные платежи для автомобилей из Китая в Казахстан.\n\n"
        "*Доступные команды:*\n"
        "/calculate - Начать расчёт\n"
        "/history - История расчётов\n"
        "/help - Помощь\n\n"
        "*Бесплатно:* 3 расчёта в месяц (только электромобили)\n"
        "*Платно:* 299 ₸/расчёт (все типы авто)\n"
        "*Пакеты:* 500/1,000/2,000 ₸ (со скидкой до 44%)\n"
        "*Подписка:* 1,990 ₸/месяц (неограниченно)\n\n"
        "Начнём? Отправь /calculate"
    )
    
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    help_text = (
        "📚 *Помощь по Customs Calculator Bot*\n\n"
        "*Как это работает:*\n"
        "1. Отправь /calculate\n"
        "2. Введи данные об автомобиле (марка, модель, тип, год, цена)\n"
        "3. Получи расчёт таможенных платежей\n\n"
        "*Тарифы:*\n"
        "• Бесплатно: 3 расчёта/месяц, только электромобили\n"
        "• Pay-per-use: 299 ₸/расчёт, все типы авто\n"
        "• Пакеты: 500/1,000/2,000 ₸ (со скидкой)\n"
        "• Подписка: 1,990 ₸/месяц, неограниченно\n\n"
        "*Поддержка:*\n"
        "По вопросам и предложениям пиши @avp_support\n\n"
        "Начать расчёт: /calculate"
    )
    
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def calculate_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /calculate command - start calculation process."""
    user = update.effective_user
    logger.info(f"User {user.id} started calculation")
    
    # Check if user has free calculations left
    # TODO: Implement database check
    
    keyboard = [
        [InlineKeyboardButton("🚀 НАЧАТЬ ВВОД", callback_data="start_input")],
        [InlineKeyboardButton("ℹ️  О тарифах", callback_data="show_tariffs")],
        [InlineKeyboardButton("❌ Отмена", callback_data="cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    start_text = (
        "🚗 *РАСЧЁТ ТАМОЖЕННЫХ ПЛАТЕЖЕЙ*\n\n"
        "Сейчас начнём ввод данных об автомобиле.\n\n"
        "*Шаги:*\n"
        "1. Марка автомобиля\n"
        "2. Модель\n"
        "3. Тип (электрический, бензин, дизель, гибрид)\n"
        "4. Год и месяц выпуска\n"
        "5. Цена в Китае (CNY)\n\n"
        "Нажми *🚀 НАЧАТЬ ВВОД* чтобы продолжить."
    )
    
    await update.message.reply_text(start_text, parse_mode="Markdown", reply_markup=reply_markup)

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
