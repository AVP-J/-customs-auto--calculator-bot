"""
Command handlers for Customs Calculator Bot.
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

def build_welcome_text(user):
    """Build welcome text for /start command."""
    first_name = user.first_name or ""
    return (
        f"🚗 *Добро пожаловать, {first_name}!*\n\n"
        "Я — KZ Customs Calculator Bot, помогу рассчитать таможенные платежи "
        "на легковые автомобили для ввоза в Республику Казахстан.\n\n"
        "📋 *КАК ЭТО РАБОТАЕТ:*\n"
        "• Вводите данные об автомобиле\n"
        "• Получаете расчёт\n\n"
        "💰 *ТАРИФЫ:*\n"
        "• *Новичок:* 3 расчёта/месяц (бесплатно)\n"
        "• *Оплата по факту:* 299 ₸/расчёт\n"
        "• *Пакеты:* 500/1,000/2,000 ₸ (скидка до 44%)\n"
        "• *Подписка PRO:* 2,990 ₸/месяц\n\n"
        "_Больше информации о Калькуляторе — кнопка Справка._\n\n"
        "Если Ваша деятельность связана с автомобильным миром,\n"
        "здесь может быть Ваша реклама.\n\n"
        "Напишите нам: info@calc.kz"
    )

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    user = update.effective_user
    logger.info(f"User {user.id} ({user.username}) started the bot")
    
    first_name = user.first_name or ""
    
    welcome_text = (
        f"🚗 *Добро пожаловать, {first_name}!*\n\n"
        "Я — KZ Customs Calculator Bot, помогу рассчитать таможенные платежи "
        "на легковые автомобили для ввоза в Республику Казахстан.\n\n"
        "📋 *КАК ЭТО РАБОТАЕТ:*\n"
        "• Вводите данные об автомобиле\n"
        "• Получаете расчёт\n\n"
        "💰 *ТАРИФЫ:*\n"
        "• *Новичок:* 3 расчёта/месяц (бесплатно)\n"
        "• *Оплата по факту:* 299 ₸/расчёт\n"
        "• *Пакеты:* 500/1,000/2,000 ₸ (скидка до 44%)\n"
        "• *Подписка PRO:* 2,990 ₸/месяц\n\n"
        "_Больше информации о Калькуляторе — кнопка Справка._\n\n"
        "Если Ваша деятельность связана с автомобильным миром,\n"
        "здесь может быть Ваша реклама.\n\n"
        "Напишите нам: info@calc.kz"
    )
    
    from .keyboards import get_start_keyboard
    
    await update.message.reply_text(
        welcome_text,
        parse_mode="Markdown",
        reply_markup=get_start_keyboard()
    )

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
        "• Детальный отчёт\n"
        "• Неограниченные расчёты\n"
        "• Экспорт в PDF\n"
        "• Приоритетная поддержка\n\n"
        "Если вы таможенный брокер, здесь может быть ваша реклама.\n"
        "Напишите нам: info@calc.kz"
    )
    
    keyboard = [
        [InlineKeyboardButton("🆓 Бесплатный расчёт", callback_data="free_start_input")],
        [InlineKeyboardButton("💳 Оплатить 299 ₸", callback_data="pay:fact")],
        [InlineKeyboardButton("💳 500 ₸ — 2 расчёта", callback_data="pay:500")],
        [InlineKeyboardButton("💳 1,000 ₸ — 5 расчётов", callback_data="pay:1000")],
        [InlineKeyboardButton("💳 2,000 ₸ — 12 расчётов", callback_data="pay:2000")],
        [InlineKeyboardButton("💳 PRO — 2,990 ₸/мес", callback_data="pay:pro")],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(tariffs_text, reply_markup=reply_markup, parse_mode="Markdown")


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    from src.bot.messages import get_help_message
    help_text, help_keyboard = get_help_message()
    await update.message.reply_text(help_text, reply_markup=help_keyboard, parse_mode="Markdown")

async def calculate_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /calculate command - show start button."""
    user = update.effective_user
    logger.info(f"User {user.id} opened calculation")
    
    from .keyboards import get_start_calc_keyboard
    
    await update.message.reply_text(
        "🧮 *РАСЧЁТ ТАМОЖЕННЫХ ПЛАТЕЖЕЙ*\n"
        "(на легковые автомобили при ввозе в Республику Казахстан)\n\n"
        "📊 *ПАРАМЕТРЫ РАСЧЁТА*\n"
        "1. Марка\n"
        "2. Модель\n"
        "3. Тип (электромобиль, гибрид, ДВС — бензин/дизель)\n"
        "4. Год и месяц выпуска (ГГГГ-ММ)\n"
        "5. Валюта покупки автомобиля\n"
        "6. Стоимость автомобиля\n"
        "7. Стоимость доставки автомобиля до границы РК\n\n"
        "Нажмите 🚀 НАЧАТЬ РАСЧЁТ чтобы продолжить.",
        parse_mode="Markdown",
        reply_markup=get_start_calc_keyboard()
    )

async def free_calculate_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /free_calculate command - free tier without delivery cost."""
    user = update.effective_user
    logger.info(f"User {user.id} opened free calculation")
    
    from .keyboards import get_free_start_calc_keyboard
    
    await update.message.reply_text(
        "🚗 *БЕСПЛАТНЫЙ РАСЧЁТ ТАМОЖЕННЫХ ПЛАТЕЖЕЙ*\n"
        "(на легковые автомобили при ввозе в Республику Казахстан)\n\n"
        "📊 *ПАРАМЕТРЫ РАСЧЕТА:*\n"
        "1. Марка\n"
        "2. Модель\n"
        "3. Тип (электромобиль, гибрид, ДВС — бензин/дизель)\n"
        "4. Год и месяц выпуска (ГГГГ-ММ)\n"
        "5. Валюта покупки автомобиля\n"
        "6. Стоимость автомобиля\n\n"
        "Для перехода на полную версию расчета — /tariffs\n\n"
        "Нажмите 🚀 НАЧАТЬ РАСЧЁТ чтобы продолжить.",
        parse_mode="Markdown",
        reply_markup=get_free_start_calc_keyboard()
    )

async def history_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /history command - show calculation history."""
    user = update.effective_user
    logger.info(f"User {user.id} requested history")
    
    history_text = (
        "📋 *ИСТОРИЯ РАСЧЁТОВ*\n\n"
        "У вас пока нет сохранённых расчётов.\n\n"
        "Сделайте первый расчёт: /calculate\n\n"
        "*Бесплатные расчёты осталось:* 3/3\n"
        "*Платные расчёты использовано:* 0\n"
        "*Активная подписка:* Нет"
    )
    
    await update.message.reply_text(history_text, parse_mode="Markdown")
