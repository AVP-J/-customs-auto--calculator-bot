#!/usr/bin/env python3
"""
Простая версия Customs Calculator Bot для быстрого запуска.
"""
import os
import sys
import logging
from datetime import datetime

# Добавляем пути
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Импорты
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)

# Загрузка конфигурации
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TOKEN or TOKEN == 'YOUR_BOT_TOKEN_HERE':
    print("❌ Bot token not set in .env file")
    sys.exit(1)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== ОБРАБОТЧИКИ КОМАНД ==========

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start."""
    user = update.effective_user
    
    welcome_text = (
        f"🚗 *Добро пожаловать, {user.first_name or 'друг'}!*\n\n"
        "Я — *Customs Calculator Bot*, помогу рассчитать таможенные платежи "
        "для автомобилей из Китая в Казахстан.\n\n"
        
        "*🚀 Как это работает:*\n"
        "1. Отправьте /calculate\n"
        "2. Введите данные об автомобиле\n"
        "3. Получите детальный расчёт\n\n"
        
        "*💰 Тарифы:*\n"
        "• *Бесплатно:* 3 расчёта/месяц (только электромобили)\n"
        "• *Pay-per-use:* 299 ₸/расчёт (все типы авто)\n"
        "• *Пакеты:* 500/1,000/2,000 ₸ (скидка до 44%)\n"
        "• *Подписка:* 1,990 ₸/месяц (неограниченно)\n\n"
        
        "Начнём? Отправьте /calculate или /расчет"
    )
    
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help."""
    help_text = (
        "📚 *ПОМОЩЬ ПО CUSTOMS CALCULATOR BOT*\n\n"
        
        "*📋 КОМАНДЫ:*\n"
        "/start или /старт — Начало работы\n"
        "/calculate или /расчет — Начать расчёт\n"
        "/help или /помощь — Эта справка\n\n"
        
        "*🚗 КАК РАБОТАЕТ РАСЧЁТ:*\n"
        "1. Вы вводите данные об автомобиле\n"
        "2. Бот рассчитывает таможенные платежи\n"
        "3. Вы получаете детальный отчёт\n\n"
        
        "Начать расчёт: /calculate или /расчет"
    )
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def calculate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /calculate."""
    # Создаём клавиатуру
    keyboard = [
        [InlineKeyboardButton("🚀 НАЧАТЬ ВВОД", callback_data="start_input")],
        [InlineKeyboardButton("💰 ТАРИФЫ", callback_data="show_tariffs")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    start_text = (
        "🚗 *РАСЧЁТ ТАМОЖЕННЫХ ПЛАТЕЖЕЙ*\n"
        "*(на легковые автомобили при ввозе в Республику Казахстан)*\n\n"
        "*📊 ПАРАМЕТРЫ РАСЧЕТА:*\n"
        "1. Марка\n"
        "2. Модель\n"
        "3. Тип (электромобиль, гибрид, бензин/дизель)\n"
        "4. Год и месяц выпуска (ГГГГ-ММ)\n"
        "5. Цена в Китае (CNY)\n\n"
        
        "Нажмите *🚀 НАЧАТЬ ВВОД* чтобы продолжить."
    )
    
    await update.message.reply_text(
        start_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

# ========== ОБРАБОТЧИКИ INLINE КНОПОК ==========

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик inline кнопок."""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    callback_data = query.data
    
    if callback_data == "start_input":
        await start_input_flow(query, context)
    elif callback_data == "show_tariffs":
        await show_tariffs(query, context)
    elif callback_data == "car_type_electric":
        await handle_electric_selection(query, context)
    elif callback_data == "car_type_hybrid":
        await handle_hybrid_selection(query, context)
    elif callback_data == "car_type_gasoline_diesel":
        await handle_gasoline_diesel_selection(query, context)
    elif callback_data == "confirm_data":
        await confirm_calculation(query, context)
    elif callback_data == "edit_data":
        await edit_calculation(query, context)
    elif callback_data == "cancel":
        await cancel_operation(query, context)
    else:
        await query.edit_message_text(f"Неизвестная команда: {callback_data}")

async def start_input_flow(query, context):
    """Начинает процесс ввода данных."""
    user = query.from_user
    
    # Инициализируем данные пользователя
    context.user_data["input_step"] = "brand"
    context.user_data["car_data"] = {}
    
    await query.edit_message_text(
        "✅ *Начинаем ввод данных об автомобиле*\n\n"
        "1️⃣ **Введите марку** (например: Li):",
        parse_mode="Markdown"
    )

async def show_tariffs(query, context):
    """Показывает информацию о тарифах."""
    tariffs_text = (
        "💰 *ТАРИФЫ*\n\n"
        
        "*1. БЕСПЛАТНЫЙ ТАРИФ*\n"
        "• 3 расчёта в месяц\n"
        "• Только электромобили\n"
        "• Базовый отчёт\n\n"
        
        "*2. PAY-PER-USE (ОСНОВНОЙ)*\n"
        "• 299 ₸ за 1 расчёт\n"
        "• Все типы автомобилей\n"
        "• Детальный отчёт\n\n"
        
        "*3. ПАКЕТЫ РАСЧЁТОВ*\n"
        "• 500 ₸ = 2 расчёта (250 ₸/расчёт, скидка 16%)\n"
        "• 1,000 ₸ = 5 расчётов (200 ₸/расчёт, скидка 33%)\n"
        "• 2,000 ₸ = 12 расчётов (167 ₸/расчёт, скидка 44%)\n\n"
        
        "*4. ПОДПИСКА (ПРОФЕССИОНАЛЬНАЯ)*\n"
        "• 1,990 ₸/месяц\n"
        "• Неограниченные расчёты\n"
        "• Экспорт в PDF\n"
        "• Приоритетная поддержка\n\n"
        
        "Начать расчёт: /calculate или /расчет"
    )
    
    keyboard = [
        [InlineKeyboardButton("🚀 НАЧАТЬ РАСЧЁТ", callback_data="start_input")],
        [InlineKeyboardButton("❌ ЗАКРЫТЬ", callback_data="cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        tariffs_text,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def handle_electric_selection(query, context):
    """Обрабатывает выбор электромобиля."""
    # Сохраняем тип
    context.user_data["car_data"]["type"] = "electric"
    context.user_data["input_step"] = "year_month"
    
    await query.edit_message_text(
        "✅ Тип: ⚡ Электромобиль\n\n"
        "3️⃣ **Введите год и месяц выпуска** (ГГГГ-ММ, например 2025-04):",
        parse_mode="Markdown"
    )

async def handle_hybrid_selection(query, context):
    """Обрабатывает выбор гибрида."""
    # Сохраняем тип
    context.user_data["car_data"]["type"] = "hybrid"
    context.user_data["input_step"] = "year_month"
    
    await query.edit_message_text(
        "✅ Тип: 🔋 Гибрид\n\n"
        "3️⃣ **Введите год и месяц выпуска** (ГГГГ-ММ, например 2025-04):",
        parse_mode="Markdown"
    )

async def handle_gasoline_diesel_selection(query, context):
    """Обрабатывает выбор бензина/дизеля."""
    # Сохраняем тип
    context.user_data["car_data"]["type"] = "gasoline_diesel"
    context.user_data["input_step"] = "year_month"
    
    await query.edit_message_text(
        "✅ Тип: ⛽ Бензин/Дизель\n\n"
        "3️⃣ **Введите год и месяц выпуска** (ГГГГ-ММ, например 2025-04):",
        parse_mode="Markdown"
    )

async def confirm_calculation(query, context):
    """Подтверждает расчёт и показывает результат."""
    user = query.from_user
    car_data = context.user_data.get("car_data", {})
    
    # Отладочная информация
    print(f"DEBUG: car_data = {car_data}")
    print(f"DEBUG: Все ключи в car_data: {list(car_data.keys())}")
    
    # Проверяем, все ли данные есть
    required_fields = ["brand", "model", "type", "year_month", "price_cny"]
    missing_fields = [field for field in required_fields if field not in car_data]
    
    if missing_fields:
        print(f"DEBUG: Отсутствуют поля: {missing_fields}")
        await query.edit_message_text(
            f"❌ Не хватает данных: {', '.join(missing_fields)}\n\n"
            "Начните заново: /calculate",
            parse_mode="Markdown"
        )
        return
    
    # Показываем простой результат
    type_names = {
        "electric": "⚡ Электромобиль",
        "hybrid": "🔋 Гибрид",
        "gasoline_diesel": "⛽ Бензин/Дизель"
    }
    car_type_name = type_names.get(car_data.get("type", ""), "Неизвестный")
    
    result_text = (
        f"🚗 *РАСЧЁТ ТАМОЖЕННЫХ ПЛАТЕЖЕЙ*\n"
        f"*(на легковые автомобили при ввозе в Республику Казахстан)*\n\n"
        f"*Автомобиль:* {car_data.get('brand')} {car_data.get('model')}\n"
        f"*Тип:* {car_type_name}\n"
        f"*Год выпуска:* {car_data.get('year_month')}\n"
        f"*Цена в Китае:* {car_data.get('price_cny'):,.0f} CNY\n\n"
        "✅ *Данные приняты!*\n\n"
        "*Следующий шаг:*\n"
        "1. Интеграция с калькулятором таможенных платежей\n"
        "2. Расчёт пошлин, НДС, акцизов\n"
        "3. Показ итоговой стоимости\n\n"
        "Эта функция будет добавлена в следующем обновлении!\n"
        "Пока что вы можете использовать команду /calculate для нового расчёта."
    )
    
    await query.edit_message_text(
        result_text,
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

async def edit_calculation(query, context):
    """Позволяет редактировать данные перед расчётом."""
    await query.edit_message_text(
        "✏️ *Редактирование данных*\n\n"
        "Какой параметр хотите изменить?\n\n"
        "1. Марка автомобиля\n"
        "2. Модель\n"
        "3. Тип\n"
        "4. Год-месяц\n"
        "5. Цена\n\n"
        "Отправьте номер параметра (1-5) или /calculate для нового расчёта",
        parse_mode="Markdown"
    )

async def cancel_operation(query, context):
    """Отменяет текущую операцию."""
    # Очищаем данные пользователя
    context.user_data.clear()
    
    await query.edit_message_text(
        "❌ *Операция отменена*\n\n"
        "Все введённые данные удалены.\n\n"
        "Чтобы начать заново, отправьте /calculate",
        parse_mode="Markdown"
    )

# ========== ОБРАБОТЧИКИ ТЕКСТОВЫХ СООБЩЕНИЙ ==========

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений (для пошагового ввода)."""
    user = update.effective_user
    text = update.message.text.strip()
    
    # Проверяем, находится ли пользователь в процессе ввода
    input_step = context.user_data.get("input_step")
    
    if not input_step:
        # Не в процессе ввода, показываем помощь
        await update.message.reply_text(
            "Чтобы начать расчёт, отправьте /calculate\n"
            "Для помощи отправьте /help"
        )
        return
    
    # Обрабатываем в зависимости от текущего шага
    if input_step == "brand":
        await handle_brand_input(update, context, text)
    elif input_step == "model":
        await handle_model_input(update, context, text)
    elif input_step == "year_month":
        await handle_year_month_input(update, context, text)
    elif input_step == "price":
        await handle_price_input(update, context, text)
    else:
        await update.message.reply_text(
            "Неизвестный шаг. Отправьте /calculate чтобы начать заново."
        )

async def handle_brand_input(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    """Обрабатывает ввод марки автомобиля."""
    if len(text) < 2 or len(text) > 50:
        await update.message.reply_text(
            "Марка должна быть от 2 до 50 символов. Попробуйте снова:"
        )
        return
    
    # Сохраняем марку
    context.user_data["car_data"]["brand"] = text
    context.user_data["input_step"] = "model"
    
    await update.message.reply_text(
        f"✅ *Марка принята:* {text}\n\n"
        "2️⃣ **Введите модель** (например: L6):",
        parse_mode="Markdown"
    )

async def handle_model_input(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    """Обрабатывает ввод модели автомобиля."""
    if len(text) < 1 or len(text) > 50:
        await update.message.reply_text(
            "Модель должна быть от 1 до 50 символов. Попробуйте снова:"
        )
        return
    
    # Сохраняем модель
    context.user_data["car_data"]["model"] = text
    context.user_data["input_step"] = "type"
    
    # Показываем выбор типа (3 кнопки в столбик)
    keyboard = [
        [InlineKeyboardButton("⚡ Электромобиль", callback_data="car_type_electric")],
        [InlineKeyboardButton("🔋 Гибрид", callback_data="car_type_hybrid")],
        [InlineKeyboardButton("⛽ Бензин/Дизель", callback_data="car_type_gasoline_diesel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"✅ *Модель принята:* {text}\n\n"
        "3️⃣ **Выберите тип:**",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def handle_year_month_input(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    """Обрабатывает ввод года и месяца."""
    import re
    
    # Проверяем формат ГГГГ-ММ
    pattern = r'^\d{4}-(0[1-9]|1[0-2])$'
    if not re.match(pattern, text):
        await update.message.reply_text(
            "❌ *Неверный формат*\n\n"
            "Введите год и месяц в формате *ГГГГ-ММ* (например: 2025-04):",
            parse_mode="Markdown"
        )
        return
    
    year, month = text.split("-")
    year_int = int(year)
    
    # Проверяем разумный диапазон годов
    current_year = datetime.now().year
    if year_int < 2000 or year_int > current_year + 5:
        await update.message.reply_text(
            f"❌ *Некорректный год*\n\n"
            f"Год должен быть между 2000 и {current_year + 5}.\n"
            f"Попробуйте снова:",
            parse_mode="Markdown"
        )
        return
    
    # Сохраняем год-месяц
    context.user_data["car_data"]["year_month"] = text
    context.user_data["input_step"] = "price"
    
    await update.message.reply_text(
        f"✅ *Год принят:* {text}\n\n"
        "4️⃣ **Введите цену в Китае** (CNY, например 200000):",
        parse_mode="Markdown"
    )

async def handle_price_input(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    """Обрабатывает ввод цены."""
    try:
        # Очищаем от пробелов и запятых
        clean_text = text.replace(",", "").replace(" ", "")
        price = float(clean_text)
        
        if price <= 0 or price > 10000000:  # Разумный диапазон: 0-10 млн CNY
            await update.message.reply_text(
                "❌ *Некорректная цена*\n\n"
                "Цена должна быть от 1 до 10,000,000 CNY.\n"
                "Попробуйте снова:",
                parse_mode="Markdown"
            )
            return
    except ValueError:
        await update.message.reply_text(
            "❌ *Неверный формат*\n\n"
            "Введите число (например: 200000 или 250,000):",
            parse_mode="Markdown"
        )
        return
    
    # Сохраняем цену
    context.user_data["car_data"]["price_cny"] = price
    
    # Показываем подтверждение
    car_data = context.user_data["car_data"]
    
    # Получаем читаемое название типа
    type_names = {
        "electric": "⚡ Электромобиль",
        "hybrid": "🔋 Гибрид",
        "gasoline_diesel": "⛽ Бензин/Дизель"
    }
    car_type_name = type_names.get(car_data.get("type", ""), "Неизвестный")
    
    confirmation_text = (
        "📋 *ПОДТВЕРЖДЕНИЕ ДАННЫХ*\n\n"
        f"*Марка:* {car_data.get('brand', 'Не указано')}\n"
        f"*Модель:* {car_data.get('model', 'Не указано')}\n"
        f"*Тип:* {car_type_name}\n"
        f"*Год-месяц:* {car_data.get('year_month', 'Не указано')}\n"
        f"*Цена в Китае:* {price:,.0f} CNY\n\n"
        "Всё верно?"
    )
    
    keyboard = [
        [InlineKeyboardButton("✅ Да, всё верно", callback_data="confirm_data")],
        [InlineKeyboardButton("✏️  Исправить", callback_data="edit_data")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        confirmation_text,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

# ========== ОСНОВНАЯ ФУНКЦИЯ ==========

def main():
    """Основная функция запуска бота."""
    print("🚀 Starting Customs Calculator Bot...")
    
    # Создаём приложение
    application = Application.builder().token(TOKEN).build()
    
    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("calculate", calculate_command))
    
    # Русские команды
    application.add_handler(CommandHandler("старт", start_command))
    application.add_handler(CommandHandler("помощь", help_command))
    application.add_handler(CommandHandler("расчет", calculate_command))
    application.add_handler(CommandHandler("таможня", calculate_command))
    
    # Добавляем обработчик inline кнопок
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Добавляем обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    
    # Запускаем бота
    print(f"✅ Bot started: @CustomsCalcKZBot")
    print("📱 Listening for messages...")
    print("Press Ctrl+C to stop")
    
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()