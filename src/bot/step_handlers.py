"""
Step-by-step interface handlers.
"""
import asyncio
import logging
from telegram import Update
from telegram.ext import ContextTypes

from .states import UserState, session_manager
from .keyboards import get_keyboard_for_state
from .messages import get_message_for_state

logger = logging.getLogger(__name__)


async def start_step_by_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start step-by-step calculation process."""
    user_id = update.effective_user.id
    
    # Initialize user data for the flow
    context.user_data["input_step"] = "brand"
    context.user_data["car_data"] = {}
    
    message = (
        "🧮 *НАЧАТЬ РАСЧЁТ*\n\n"
        "Для расчёта таможенных платежей введите данные об автомобиле.\n\n"
        "1. Введите марку автомобиля (например: Toyota, Li, Mercedes):"
    )
    
    await update.message.reply_text(message, parse_mode="Markdown")
    logger.info(f"Started step-by-step calculation for user {user_id}")


async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback queries from inline buttons."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    callback_data = query.data
    
    logger.debug(f"User {user_id}: callback_data = {callback_data}")
    
    # Handle cancel from any step
    if callback_data == "calc_cancel":
        context.user_data["input_step"] = None
        context.user_data["car_data"] = {}
        await query.edit_message_text(
            "❌ Расчёт отменён.\n\n"
            "Чтобы начать новый расчёт, отправьте /calculate",
            parse_mode="Markdown"
        )
        return
    
    # Handle start_input from /calculate button
    if callback_data == "start_input":
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        context.user_data["input_step"] = "brand"
        context.user_data["car_data"] = {}
        cancel_kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Отмена", callback_data="calc_cancel")]
        ])
        await query.edit_message_text(
            "1. Введите марку автомобиля (например: Toyota, Li, Mercedes):",
            reply_markup=cancel_kb,
            parse_mode="Markdown"
        )
        return
    
    # Handle engine type from the new text-only flow (context.user_data)
    if callback_data.startswith("engine_type:") and "input_step" in context.user_data:
        engine_type = callback_data.split(":")[1]
        car_data = context.user_data.get("car_data", {})
        
        type_names = {
            "electric": "Электрический",
            "hybrid": "Гибрид",
            "gasoline": "Бензин"
        }
        car_data["type"] = type_names.get(engine_type, engine_type)
        context.user_data["car_data"] = car_data
        context.user_data["input_step"] = "year_month"
        
        type_emoji = {"electric": "⚡", "hybrid": "🔋", "gasoline": "⛽"}.get(engine_type, "")
        
        # Send type confirmation as new message, then ask for year as another new message with cancel
        await query.edit_message_text(
            f"✅ Тип: {type_emoji} {car_data['type']}",
            parse_mode="Markdown"
        )
        await query.message.reply_text(
            "4. Введите год и месяц выпуска (ГГГГ-ММ):",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Отмена", callback_data="calc_cancel")]
            ]),
            parse_mode="Markdown"
        )
        return
    
    # Handle currency selection from the new text-only flow (context.user_data)
    if callback_data.startswith("currency:") and "input_step" in context.user_data:
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        currency = callback_data.split(":")[1].upper()
        car_data = context.user_data.get("car_data", {})
        
        car_data["currency"] = currency
        context.user_data["car_data"] = car_data
        context.user_data["input_step"] = "price"
        
        currency_emoji = {"USD": "💵", "CNY": "🇨🇳", "EUR": "💶", "KZT": "🇰🇿", "JPY": "💴"}.get(currency, "")
        
        # Send confirmation as new message, then ask for price as another new message with cancel button
        cancel_kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Отмена", callback_data="calc_cancel")]
        ])
        await query.edit_message_text(
            f"✅ Валюта: {currency_emoji} {currency}",
            parse_mode="Markdown"
        )
        await query.message.reply_text(
            f"6. Введите стоимость автомобиля ({currency}):",
            reply_markup=cancel_kb,
            parse_mode="Markdown"
        )
        return
    
    session = session_manager.get_session(user_id)
    
    # Handle navigation commands
    if callback_data == "cancel":
        await handle_cancel(update, context, session)
        return
    
    elif callback_data == "back":
        await handle_back(update, context, session)
        return
    
    elif callback_data == "restart":
        await handle_restart(update, context, session)
        return
    
    # Handle state-specific callbacks
    if session.state == UserState.CHOOSE_VEHICLE_TYPE:
        await handle_vehicle_type(update, context, session, callback_data)
    
    elif session.state == UserState.CHOOSE_ENGINE_TYPE:
        await handle_engine_type(update, context, session, callback_data)
    
    elif session.state == UserState.CHOOSE_COUNTRY:
        await handle_country(update, context, session, callback_data)
    
    elif session.state == UserState.CONFIRM_DATA:
        await handle_confirmation(update, context, session, callback_data)
    
    elif session.state == UserState.SHOW_RESULT:
        await handle_result_action(update, context, session, callback_data)


async def handle_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE, session):
    """Handle cancel action."""
    user_id = update.effective_user.id
    session_manager.delete_session(user_id)
    
    await update.callback_query.edit_message_text(
        "❌ Расчёт отменён.\n\n"
        "Чтобы начать новый расчёт, отправьте /calculate",
        parse_mode="Markdown"
    )
    logger.info(f"User {user_id} cancelled calculation")


async def handle_back(update: Update, context: ContextTypes.DEFAULT_TYPE, session):
    """Handle back action."""
    # Determine previous state based on current state
    state_transitions = {
        UserState.ENTER_PRICE: UserState.CHOOSE_VEHICLE_TYPE,
        UserState.CHOOSE_ENGINE_TYPE: UserState.ENTER_PRICE,
        UserState.CHOOSE_COUNTRY: UserState.CHOOSE_ENGINE_TYPE,
        UserState.CONFIRM_DATA: UserState.CHOOSE_COUNTRY,
    }
    
    if session.state in state_transitions:
        previous_state = state_transitions[session.state]
        session.update_state(previous_state)
        
        message = get_message_for_state(session.state, session.data)
        keyboard = get_keyboard_for_state(session.state, session.data)
        
        await update.callback_query.edit_message_text(message, reply_markup=keyboard, parse_mode="Markdown")
        logger.debug(f"User {update.effective_user.id} went back to {previous_state.value}")


async def handle_restart(update: Update, context: ContextTypes.DEFAULT_TYPE, session):
    """Handle restart action."""
    user_id = update.effective_user.id
    session_manager.delete_session(user_id)
    await start_step_by_step(update, context)


async def handle_vehicle_type(update: Update, context: ContextTypes.DEFAULT_TYPE, session, callback_data):
    """Handle vehicle type selection."""
    if callback_data.startswith("vehicle_type:"):
        vehicle_type = callback_data.split(":")[1]
        session.update_data("vehicle_type", vehicle_type)
        session.update_state(UserState.ENTER_PRICE)
        
        vehicle_names = {
            "car": "легковой автомобиль",
            "truck": "грузовой автомобиль",
            "motorcycle": "мотоцикл",
            "bus": "автобус",
            "special": "спецтехника",
            "bicycle": "велосипед"
        }
        
        message = (
            f"✅ Выбран: {vehicle_names.get(vehicle_type, vehicle_type)}\n\n"
            f"📊 *Шаг 2: Введите стоимость автомобиля*\n\n"
            f"Введите стоимость в долларах США (USD).\n"
            f"Пример: 30000\n\n"
            f"Или выберите валюту:"
        )
        
        # For now, just ask for price in USD
        await update.callback_query.edit_message_text(
            f"✅ Выбран: {vehicle_names.get(vehicle_type, vehicle_type)}\n\n"
            f"📊 *Шаг 2: Введите стоимость автомобиля*\n\n"
            f"Введите стоимость в долларах США (USD).\n"
            f"Пример: 30000",
            parse_mode="Markdown"
        )
        
        logger.info(f"User {update.effective_user.id} selected vehicle type: {vehicle_type}")


async def handle_engine_type(update: Update, context: ContextTypes.DEFAULT_TYPE, session, callback_data):
    """Handle engine type selection."""
    if callback_data.startswith("engine_type:"):
        engine_type = callback_data.split(":")[1]
        session.update_data("engine_type", engine_type)
        session.update_state(UserState.CHOOSE_COUNTRY)
        
        engine_names = {
            "electric": "электромобиль",
            "hybrid": "гибрид",
            "gasoline": "бензин",
            "diesel": "дизель"
        }
        
        message = get_message_for_state(session.state, session.data)
        keyboard = get_keyboard_for_state(session.state, session.data)
        
        await update.callback_query.edit_message_text(message, reply_markup=keyboard, parse_mode="Markdown")
        logger.info(f"User {update.effective_user.id} selected engine type: {engine_type}")


async def handle_country(update: Update, context: ContextTypes.DEFAULT_TYPE, session, callback_data):
    """Handle country selection."""
    if callback_data.startswith("country:"):
        country = callback_data.split(":")[1]
        session.update_data("country", country)
        session.update_state(UserState.CONFIRM_DATA)
        
        country_names = {
            "china": "Китай",
            "usa": "США",
            "europe": "Европа",
            "japan": "Япония",
            "korea": "Корея",
            "russia": "Россия"
        }
        
        message = get_message_for_state(session.state, session.data)
        keyboard = get_keyboard_for_state(session.state, session.data)
        
        await update.callback_query.edit_message_text(message, reply_markup=keyboard, parse_mode="Markdown")
        logger.info(f"User {update.effective_user.id} selected country: {country}")


async def handle_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE, session, callback_data):
    """Handle confirmation."""
    if callback_data == "confirm:yes":
        # All data is complete, proceed to calculation
        session.update_state(UserState.CALCULATING)
        
        # Show calculating message
        await update.callback_query.edit_message_text(
            "🔄 *Рассчитываю таможенные платежи...*\n\n"
            "Пожалуйста, подождите несколько секунд.",
            parse_mode="Markdown"
        )
        
        # TODO: Call calculation function
        # For now, simulate calculation
        await asyncio.sleep(2)
        
        # Show result
        session.update_state(UserState.SHOW_RESULT)
        message = get_message_for_state(session.state, session.data)
        keyboard = get_keyboard_for_state(session.state, session.data)
        
        await update.callback_query.edit_message_text(message, reply_markup=keyboard, parse_mode="Markdown")
        
    elif callback_data == "confirm:no":
        # Go back to first step
        session.update_state(UserState.CHOOSE_VEHICLE_TYPE)
        message = get_message_for_state(session.state, session.data)
        keyboard = get_keyboard_for_state(session.state, session.data)
        
        await update.callback_query.edit_message_text(message, reply_markup=keyboard, parse_mode="Markdown")


async def handle_result_action(update: Update, context: ContextTypes.DEFAULT_TYPE, session, callback_data):
    """Handle actions after calculation."""
    if callback_data == "new_calculation":
        await handle_restart(update, context, session)
    
    elif callback_data == "save_result":
        await update.callback_query.answer("✅ Результат сохранён в историю", show_alert=True)
    
    elif callback_data == "share_result":
        await update.callback_query.answer("📤 Функция 'Поделиться' скоро будет доступна", show_alert=True)
    
    elif callback_data == "history":
        await update.callback_query.answer("📊 История расчётов скоро будет доступна", show_alert=True)
    
    elif callback_data == "start":
        session_manager.delete_session(update.effective_user.id)
        from .handlers import start_handler
        await start_handler(update, context)


async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text input for price and other data."""
    user_id = update.effective_user.id
    text = update.message.text.strip()
    session = session_manager.get_session(user_id)
    
    # Use context.user_data as simple FSM for new flow
    input_step = context.user_data.get("input_step", None)
    car_data = context.user_data.get("car_data", {})
    
    # Handle cancel command from text input
    if text.lower() in ["отмена", "cancel", "стоп", "stop", "выход"] and input_step:
        context.user_data["input_step"] = None
        context.user_data["car_data"] = {}
        await update.message.reply_text(
            "❌ Расчёт отменён.\n\n"
            "Чтобы начать новый расчёт, отправьте /calculate",
            parse_mode="Markdown"
        )
        return
    
    # New flow: starting from /рассчитать button
    if input_step == "brand":
        car_data["brand"] = text
        context.user_data["car_data"] = car_data
        context.user_data["input_step"] = "model"
        
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        cancel_kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Отмена", callback_data="calc_cancel")]
        ])
        
        await update.message.reply_text(
            f"✅ Марка: {text}\n\n"
            "2. Введите модель автомобиля (например: RAV4, L7, E200):",
            reply_markup=cancel_kb,
            parse_mode="Markdown"
        )
        logger.info(f"User {user_id} entered brand: {text}")
        return
    
    elif input_step == "model":
        car_data["model"] = text
        context.user_data["car_data"] = car_data
        context.user_data["input_step"] = "type"
        
        # Show type selection keyboard
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        from .keyboards import get_engine_type_keyboard
        
        await update.message.reply_text(
            f"✅ Марка: {car_data.get('brand', '')}",
            parse_mode="Markdown"
        )
        await update.message.reply_text(
            f"✅ Модель: {text}\n\n"
            "3. Выберите тип автомобиля:",
            reply_markup=get_engine_type_keyboard(),
            parse_mode="Markdown"
        )
        logger.info(f"User {user_id} entered model: {text}")
        return
    
    elif input_step == "price":
        try:
            price_str = ''.join(c for c in text if c.isdigit() or c == '.')
            price = float(price_str)
            if price <= 0:
                raise ValueError("Must be positive")
            
            currency = car_data.get("currency", "USD")
            car_data["price"] = price
            context.user_data["car_data"] = car_data
            context.user_data["input_step"] = "delivery"
            
            await update.message.reply_text(
                f"✅ Стоимость: {price:,.2f} {currency}\n\n"
                "7. Введите стоимость доставки до границы РК (USD):",
                parse_mode="Markdown"
            )
            logger.info(f"User {user_id} entered price: {price} {currency}")
        except (ValueError, TypeError):
            await update.message.reply_text(
                "❌ Неверный формат. Введите число.\n"
                "Пример: 30000 или 29999.99",
                parse_mode="Markdown"
            )
        return
    
    elif input_step == "edit_select":
        # Parse parameter number
        if text in ["1", "2", "3", "4", "5", "6", "7"]:
            param_map = {
                "1": ("brand", "Введите марку автомобиля (например: Toyota, Li, Mercedes):"),
                "2": ("model", "Введите модель автомобиля (например: RAV4, L7, E200):"),
                "3": ("type", "Выберите тип автомобиля:"),
                "4": ("year_month", "Введите год и месяц выпуска (ГГГГ-ММ):"),
                "5": ("currency", "Выберите валюту покупки автомобиля:"),
                "6": ("price", "Введите стоимость автомобиля:"),
                "7": ("delivery", "Введите стоимость доставки до границы РК (USD):")
            }
            
            field, prompt = param_map[text]
            context.user_data["input_step"] = f"edit_{field}"
            
            await update.message.reply_text(
                f"✏️ {prompt}",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                "❌ Неверный номер. Отправьте число от 1 до 7.",
                parse_mode="Markdown"
            )
        return
    
    elif input_step.startswith("edit_"):
        # Handle editing a specific field
        field = input_step.replace("edit_", "")
        
        if field in ["price", "delivery"]:
            try:
                price_str = ''.join(c for c in text if c.isdigit() or c == '.')
                value = float(price_str)
                if value <= 0:
                    raise ValueError("Must be positive")
                car_data[field] = value
            except (ValueError, TypeError):
                await update.message.reply_text(
                    "❌ Неверный формат. Введите число.",
                    parse_mode="Markdown"
                )
                return
        else:
            car_data[field] = text
        
        context.user_data["car_data"] = car_data
        
        # Show confirmation again with updated data
        context.user_data["input_step"] = "confirm"
        
        type_emoji = {
            "Электрический": "⚡",
            "Гибрид": "🔋",
            "Бензин": "⛽",
            "Дизель": "🛢️"
        }.get(car_data.get("type", ""), "")
        
        currency_emoji = {
            "USD": "💵",
            "CNY": "🇨🇳",
            "EUR": "💶",
            "KZT": "🇰🇿",
            "JPY": "💴"
        }.get(car_data.get("currency", ""), "")
        
        confirm_text = (
            "✅ *Данные обновлены*\n\n"
            "📋 *ПОДТВЕРЖДЕНИЕ ДАННЫХ*\n\n"
            f"1. Марка: {car_data.get('brand', '')}\n"
            f"2. Модель: {car_data.get('model', '')}\n"
            f"3. Тип: {type_emoji} {car_data.get('type', '')}\n"
            f"4. Год и месяц выпуска автомобиля: {car_data.get('year_month', '')}\n"
            f"5. Валюта покупки: {currency_emoji} {car_data.get('currency', '')}\n"
            f"6. Стоимость автомобиля: {car_data.get('price', 0):,.2f} {car_data.get('currency', 'USD')}\n"
            f"7. Стоимость доставки до вашего города: {car_data.get('delivery_cost', 0):,.2f} USD\n\n"
            "Всё верно?"
        )
        
        from .keyboards import get_confirmation_keyboard
        
        await update.message.reply_text(
            confirm_text,
            reply_markup=get_confirmation_keyboard(),
            parse_mode="Markdown"
        )
        return
    
    elif input_step == "delivery":
        try:
            price_str = ''.join(c for c in text if c.isdigit() or c == '.')
            delivery = float(price_str)
            if delivery < 0:
                raise ValueError("Delivery cost must be non-negative")
            
            car_data["delivery_cost"] = delivery
            context.user_data["car_data"] = car_data
            context.user_data["input_step"] = "confirm"
            
            # Build confirmation message
            type_emoji = {
                "Электрический": "⚡",
                "Гибрид": "🔋",
                "Бензин": "⛽",
                "Дизель": "🛢️"
            }.get(car_data.get("type", ""), "")
            
            currency_emoji = {
                "USD": "💵",
                "CNY": "🇨🇳",
                "EUR": "💶",
                "KZT": "🇰🇿",
                "JPY": "💴"
            }.get(car_data.get("currency", ""), "")
            
            confirm_text = (
                "📋 *ПОДТВЕРЖДЕНИЕ ДАННЫХ*\n\n"
                f"1. Марка: {car_data.get('brand', '')}\n"
                f"2. Модель: {car_data.get('model', '')}\n"
                f"3. Тип: {type_emoji} {car_data.get('type', '')}\n"
                f"4. Год и месяц выпуска автомобиля: {car_data.get('year_month', '')}\n"
                f"5. Валюта покупки: {currency_emoji} {car_data.get('currency', '')}\n"
                f"6. Стоимость автомобиля: {car_data.get('price', 0):,.2f} {car_data.get('currency', 'USD')}\n"
                f"7. Стоимость доставки до вашего города: {delivery:,.2f} USD\n\n"
                "Всё верно?"
            )
            
            from .keyboards import get_confirmation_keyboard
            
            await update.message.reply_text(
                confirm_text,
                reply_markup=get_confirmation_keyboard(),
                parse_mode="Markdown"
            )
            logger.info(f"User {user_id} entered delivery cost: {delivery} USD")
        except (ValueError, TypeError):
            await update.message.reply_text(
                "❌ Неверный формат стоимости доставки.\n\n"
                "Пожалуйста, введите число.\n"
                "Пример: 2000",
                parse_mode="Markdown"
            )
        return
    
    elif input_step == "price":
        # Parse price number
        try:
            price_str = ''.join(c for c in text if c.isdigit() or c == '.')
            price = float(price_str)
            if price <= 0:
                raise ValueError("Price must be positive")
            
            car_data["price"] = price
            context.user_data["car_data"] = car_data
            context.user_data["input_step"] = "delivery"
            
            await update.message.reply_text(
                f"✅ Стоимость: {price:,.2f} {car_data.get('currency', 'USD')}\n\n"
                "7. Введите стоимость доставки автомобиля до границы РК (USD):",
                parse_mode="Markdown"
            )
            logger.info(f"User {user_id} entered price: {price} {car_data.get('currency', 'USD')}")
        except (ValueError, TypeError):
            await update.message.reply_text(
                "❌ Неверный формат цены.\n\n"
                "Пожалуйста, введите число.\n"
                f"Пример: 30000",
                parse_mode="Markdown"
            )
        return
    
    elif input_step == "year_month":
        # Simple validation: check format YYYY-MM
        import re
        if re.match(r'^\d{4}-\d{2}$', text):
            car_data["year_month"] = text
            context.user_data["car_data"] = car_data
            context.user_data["input_step"] = "currency"
            
            from .keyboards import get_currency_keyboard
            
            await update.message.reply_text(
                f"✅ Год и месяц: {text}\n\n"
                "5. Выберите валюту покупки автомобиля:",
                reply_markup=get_currency_keyboard(),
                parse_mode="Markdown"
            )
            logger.info(f"User {user_id} entered year/month: {text}")
        else:
            await update.message.reply_text(
                "❌ Неверный формат. Введите в формате ГГГГ-ММ\n"
                "Пример: 2025-04",
                parse_mode="Markdown"
            )
        return
    
    if session.state == UserState.ENTER_PRICE:
        # Try to parse price
        try:
            # Remove any non-digit characters except decimal point
            price_str = ''.join(c for c in text if c.isdigit() or c == '.')
            price = float(price_str)
            
            if price <= 0:
                raise ValueError("Price must be positive")
            
            session.update_data("price", price)
            session.update_state(UserState.CHOOSE_ENGINE_TYPE)
            
            message = get_message_for_state(session.state, session.data)
            keyboard = get_keyboard_for_state(session.state, session.data)
            
            await update.message.reply_text(message, reply_markup=keyboard, parse_mode="Markdown")
            logger.info(f"User {user_id} entered price: {price} USD")
            
        except (ValueError, TypeError):
            await update.message.reply_text(
                "❌ Неверный формат цены.\n\n"
                "Пожалуйста, введите число.\n"
                "Пример: 30000 или 29999.99",
                parse_mode="Markdown"
            )