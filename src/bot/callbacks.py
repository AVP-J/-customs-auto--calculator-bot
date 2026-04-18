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
    else:
        await query.edit_message_text(f"Неизвестная команда: {callback_data}")

async def start_input_flow(query, context):
    """Start the car data input flow."""
    # Store user state in context
    context.user_data["input_step"] = "brand"
    context.user_data["car_data"] = {}
    
    await query.edit_message_text(
        "✅ *Начинаем ввод*\n\n"
        "1️⃣ **Введите марку автомобиля** (например: Li):",
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
        [InlineKeyboardButton("📋 ИСТОРИЯ", callback_data="show_history")],
        [InlineKeyboardButton("❌ ЗАКРЫТЬ", callback_data="cancel")]
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
    
    await query.edit_message_text(
        f"✅ Тип: {car_type_emoji} {car_type_name}\n\n"
        "4️⃣ **Введите год и месяц выпуска** (ГГГГ-ММ, например 2025-04):",
        parse_mode="Markdown"
    )
