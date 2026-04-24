"""
Callback handlers for inline buttons.
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def button_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline button callbacks."""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    callback_data = query.data
    
    logger.info(f"User {user.id} pressed button: {callback_data}")
    
    if callback_data == "start_input":
        await start_input_flow(query, context)
    elif callback_data == "show_tariffs":
        await show_tariffs(query, context)
    elif callback_data == "cancel":
        await cancel_operation(query, context)
    elif callback_data.startswith("car_type_"):
        await handle_car_type_selection(query, context, callback_data)
    elif callback_data.startswith("currency:"):
        await handle_currency_selection(query, context, callback_data)
    elif callback_data == "confirm:yes":
        await handle_confirmation_yes(query, context)
    elif callback_data == "confirm:no":
        await handle_confirmation_no(query, context)
    elif callback_data == "cancel":
        await cancel_operation(query, context)
    else:
        await query.edit_message_text(f"Неизвестная команда: {callback_data}")

async def start_input_flow(query, context):
    """Start the car data input flow."""
    # Store user state in context
    context.user_data["input_step"] = "brand"
    context.user_data["car_data"] = {}
    
    await query.edit_message_text(
        "1. Введите марку автомобиля (например: Toyota, Li, Mercedes):",
        parse_mode="Markdown"
    )

async def show_tariffs(query, context):
    """Show tariff information."""
    tariffs_text = (
        "💰 *ТАРИФЫ*\n\n"
        "*1. БЕСПЛАТНЫЙ ТАРИФ*\n"
        "• 3 расчёта в месяц\n"
        "• Только электромобили\n"
        "• Базовый отчёт\n\n"
        "*2. PAY-PER-USE (ОСНОВНОЙ)*\n"
        "• 299 ₸ за 1 расчёт\n"
        "• Все типы автомобилей\n"
        "• Детальный отчёт\n"
        "• Сохранение в истории\n\n"
        "*3. ПАКЕТЫ РАСЧЁТОВ*\n"
        "• 500 ₸ = 2 расчёта (250 ₸/расчёт, скидка 16%)\n"
        "• 1,000 ₸ = 5 расчётов (200 ₸/расчёт, скидка 33%)\n"
        "• 2,000 ₸ = 12 расчётов (167 ₸/расчёт, скидка 44%)\n\n"
        "*4. ПОДПИСКА (ПРОФЕССИОНАЛЬНАЯ)*\n"
        "• 1,990 ₸/месяц\n"
        "• Неограниченные расчёты\n"
        "• Экспорт в PDF\n"
        "• Приоритетная поддержка\n\n"
        "*Акция:* Первая покупка со скидкой 50% (150 ₸ вместо 299 ₸)"
    )
    
    keyboard = [
        [InlineKeyboardButton("🚀 НАЧАТЬ РАСЧЁТ", callback_data="start_input")],
        [InlineKeyboardButton("📋 ИСТОРИЯ", callback_data="show_history")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(tariffs_text, parse_mode="Markdown", reply_markup=reply_markup)

async def cancel_operation(query, context):
    """Cancel current operation."""
    # Clear user data
    context.user_data.clear()
    
    await query.edit_message_text(
        "❌ Операция отменена.\n\n"
        "Чтобы начать заново, отправьте /calculate",
        parse_mode="Markdown"
    )

async def handle_car_type_selection(query, context, callback_data):
    """Handle car type selection."""
    car_type = callback_data.replace("car_type_", "")
    car_type_emoji = {
        "electric": "⚡",
        "gasoline": "⛽",
        "diesel": "⛽",
        "hybrid": "🌿"
    }.get(car_type, "")
    
    car_type_name = {
        "electric": "Электрический",
        "gasoline": "Бензин",
        "diesel": "Дизель",
        "hybrid": "Гибрид"
    }.get(car_type, "Неизвестный")
    
    # Store in user data
    context.user_data["car_data"]["type"] = car_type
    context.user_data["input_step"] = "year_month"
    
    # Update context for the new flow
    context.user_data["car_data"]["type"] = car_type_name
    context.user_data["input_step"] = "year_month"
    
    await query.edit_message_text(
        f"✅ Тип: {car_type_emoji} {car_type_name}\n\n"
        "4. Введите год и месяц выпуска (ГГГГ-ММ):",
        parse_mode="Markdown"
    )


async def handle_currency_selection(query, context, callback_data):
    """Handle currency selection."""
    currency = callback_data.split(":")[1]
    
    currency_emoji = {
        "usd": "💵",
        "cny": "🇨🇳",
        "eur": "💶",
        "kzt": "🇰🇿",
        "jpy": "💴"
    }
    
    currency_upper = currency.upper()
    
    # Store in user data
    context.user_data["car_data"]["currency"] = currency_upper
    context.user_data["input_step"] = "price"
    
    await query.edit_message_text(
        f"✅ Валюта: {currency_emoji.get(currency, '')} {currency_upper}\n\n"
        f"6. Введите стоимость автомобиля ({currency_upper}):",
        parse_mode="Markdown"
    )


async def handle_confirmation_yes(query, context):
    """Handle confirmation - proceed to calculation and show result for free tier."""
    context.user_data["input_step"] = "calculating"
    
    # Show calculating message
    await query.edit_message_text(
        "🔄 *Рассчитываю таможенные платежи...*\n\n"
        "Пожалуйста, подождите несколько секунд.",
        parse_mode="Markdown"
    )
    
    # TODO: Call actual calculation (backend)
    import asyncio
    await asyncio.sleep(2)
    
    car = context.user_data.get("car_data", {})
    
    type_emoji = {
        "Электрический": "⚡",
        "Гибрид": "🔋",
        "Бензин": "⛽",
        "Дизель": "🛢️"
    }.get(car.get("type", ""), "")
    
    currency_emoji = {
        "USD": "💵",
        "CNY": "🇨🇳",
        "EUR": "💶",
        "KZT": "🇰🇿",
        "JPY": "💴"
    }.get(car.get("currency", ""), "")
    
    result_text = (
        "🎯 *РАСЧЁТ ГОТОВ!*\n"
        "(Тариф — НОВИЧОК)\n\n"
        "1. Марка: " + car.get("brand", "") + "\n"
        "2. Модель: " + car.get("model", "") + "\n"
        "3. Тип: " + type_emoji + " " + car.get("type", "") + "\n"
        "4. Год и месяц выпуска автомобиля: " + car.get("year_month", "") + "\n"
        "5. Валюта покупки: " + currency_emoji + " " + car.get("currency", "") + "\n"
        "6. Стоимость автомобиля: {price:,.2f}".format(price=car.get("price", 0)) + " " + car.get("currency", "USD") + "\n"
        "7. Стоимость доставки автомобиля до вашего города: {delivery:,.2f} USD\n\n".format(delivery=car.get("delivery_cost", 0)) +
        "0 — Итого по таможенным платежам\n\n"
        "💱 Калькулятор использует средневзвешенный курс валюты "
        "на момент формирования расчёта.\n\n"
        "— — — — — — — — — —\n\n"
        "В платной версии Вы увидите:\n\n"
        "0 — Стоимость автомобиля по таможенному каталогу:\n\n"
        "*Платежи (KZT):*\n"
        "0 — Таможенная пошлина\n"
        "0 — НДС\n"
        "0 — Утиль сбор\n"
        "0 — Первичная регистрация\n"
        "0 — Сертификат и ЭПТС (кнопка)\n"
        "0 — СВХ\n"
        "0 — Услуги брокера\n"
        "*0 — Итого*\n\n"
        "*0 — Стоимость вашего автомобиля включая расходы*\n\n"
        "Выбрать тариф и перейти на платную версию — /tariffs"
    )
    
    await query.edit_message_text(
        result_text,
        parse_mode="Markdown"
    )
    
    # Clear session
    context.user_data.clear()


async def handle_confirmation_no(query, context):
    """Handle confirmation - show editing menu."""
    context.user_data["input_step"] = "edit_select"
    car = context.user_data.get("car_data", {})
    
    type_emoji = {
        "Электрический": "⚡",
        "Гибрид": "🔋",
        "Бензин": "⛽",
        "Дизель": "🛢️"
    }.get(car.get("type", ""), "")
    
    currency_emoji = {
        "USD": "💵",
        "CNY": "🇨🇳",
        "EUR": "💶",
        "KZT": "🇰🇿",
        "JPY": "💴"
    }.get(car.get("currency", ""), "")
    
    edit_text = (
        "📝 *РЕДАКТИРОВАНИЕ ДАННЫХ*\n\n"
        "Какой параметр хотите изменить?\n\n"
        f"1. Марка: {car.get('brand', '')}\n"
        f"2. Модель: {car.get('model', '')}\n"
        f"3. Тип: {type_emoji} {car.get('type', '')}\n"
        f"4. Год и месяц выпуска автомобиля: {car.get('year_month', '')}\n"
        f"5. Валюта покупки: {currency_emoji} {car.get('currency', '')}\n"
        f"6. Стоимость автомобиля: {car.get('price', 0):,.2f} {car.get('currency', 'USD')}\n"
        f"7. Стоимость доставки автомобиля до вашего города: {car.get('delivery_cost', 0):,.2f} USD\n\n"
        "Отправьте номер параметра (1-7) или /рассчитать для нового расчёта"
    )
    
    await query.edit_message_text(
        edit_text,
        parse_mode="Markdown"
    )
