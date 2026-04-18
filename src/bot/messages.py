"""
Text message handlers.
"""
import logging
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def text_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages (for step-by-step input)."""
    user = update.effective_user
    text = update.message.text.strip()
    
    logger.info(f"User {user.id} sent text: {text}")
    
    # Check if user is in input flow
    input_step = context.user_data.get("input_step")
    
    if not input_step:
        # Not in input flow, show help
        await update.message.reply_text(
            "Чтобы начать расчёт, отправьте /calculate\n"
            "Для помощи отправьте /help"
        )
        return
    
    # Handle based on current step
    if input_step == "brand":
        await handle_brand_input(update, context, text)
    elif input_step == "model":
        await handle_model_input(update, context, text)
    elif input_step == "year_month":
        await handle_year_month_input(update, context, text)
    elif input_step == "price":
        await handle_price_input(update, context, text)
    else:
        await update.message.reply_text("Неизвестный шаг. Отправьте /calculate чтобы начать заново.")

async def handle_brand_input(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    """Handle car brand input."""
    if len(text) < 2 or len(text) > 50:
        await update.message.reply_text("Марка должна быть от 2 до 50 символов. Попробуйте снова:")
        return
    
    # Store brand
    context.user_data["car_data"]["brand"] = text
    context.user_data["input_step"] = "model"
    
    await update.message.reply_text(
        f"✅ Марка принята: {text}\n\n"
        "2️⃣ **Введите модель автомобиля** (например: L6):",
        parse_mode="Markdown"
    )

async def handle_model_input(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    """Handle car model input."""
    if len(text) < 1 or len(text) > 50:
        await update.message.reply_text("Модель должна быть от 1 до 50 символов. Попробуйте снова:")
        return
    
    # Store model
    context.user_data["car_data"]["model"] = text
    context.user_data["input_step"] = "type"
    
    # Show car type selection keyboard
    keyboard = [
        [
            InlineKeyboardButton("⚡ Электрический", callback_data="car_type_electric"),
            InlineKeyboardButton("⛽ Бензин", callback_data="car_type_gasoline")
        ],
        [
            InlineKeyboardButton("⛽ Дизель", callback_data="car_type_diesel"),
            InlineKeyboardButton("🌿 Гибрид", callback_data="car_type_hybrid")
        ],
        [InlineKeyboardButton("❌ Отмена", callback_data="cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"✅ Модель принята: {text}\n\n"
        "3️⃣ **Выберите тип автомобиля:**",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def handle_year_month_input(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    """Handle year and month input."""
    # Validate format YYYY-MM
    pattern = r'^\d{4}-(0[1-9]|1[0-2])$'
    if not re.match(pattern, text):
        await update.message.reply_text(
            "Неверный формат. Введите год и месяц в формате ГГГГ-ММ (например: 2025-04):"
        )
        return
    
    year, month = text.split("-")
    year_int = int(year)
    
    # Validate year (reasonable range: 2000-2030)
    if year_int < 2000 or year_int > 2030:
        await update.message.reply_text("Год должен быть между 2000 и 2030. Попробуйте снова:")
        return
    
    # Store year-month
    context.user_data["car_data"]["year_month"] = text
    context.user_data["input_step"] = "price"
    
    await update.message.reply_text(
        f"✅ Год принят: {text}\n\n"
        "5️⃣ **Введите цену в Китае** (CNY, например 200000):",
        parse_mode="Markdown"
    )

async def handle_price_input(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    """Handle price input."""
    try:
        price = float(text.replace(",", ".").replace(" ", ""))
        if price <= 0 or price > 10000000:  # Reasonable range: 0-10 million CNY
            await update.message.reply_text("Цена должна быть от 1 до 10,000,000 CNY. Попробуйте снова:")
            return
    except ValueError:
        await update.message.reply_text("Неверный формат цены. Введите число (например: 200000):")
        return
    
    # Store price
    context.user_data["car_data"]["price_cny"] = price
    
    # Show confirmation
    car_data = context.user_data["car_data"]
    confirmation_text = (
        "📋 *ПОДТВЕРЖДЕНИЕ ДАННЫХ*\n\n"
        f"*Марка:* {car_data.get('brand', 'Не указано')}\n"
        f"*Модель:* {car_data.get('model', 'Не указано')}\n"
        f"*Тип:* {get_car_type_name(car_data.get('type', ''))}\n"
        f"*Год-месяц:* {car_data.get('year_month', 'Не указано')}\n"
        f"*Цена в Китае:* {price:,.0f} CNY\n\n"
        "Всё верно?"
    )
    
    keyboard = [
        [InlineKeyboardButton("✅ Да, всё верно", callback_data="confirm_data")],
        [InlineKeyboardButton("✏️  Исправить", callback_data="edit_data")],
        [InlineKeyboardButton("❌ Отмена", callback_data="cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        confirmation_text,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

def get_car_type_name(car_type: str) -> str:
    """Convert car type code to readable name."""
    type_map = {
        "electric": "⚡ Электрический",
        "gasoline": "⛽ Бензин",
        "diesel": "⛽ Дизель",
        "hybrid": "🌿 Гибрид"
    }
    return type_map.get(car_type, "Неизвестный")
