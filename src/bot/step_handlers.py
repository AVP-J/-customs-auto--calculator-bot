"""
Step-by-step interface handlers — ЧИСТАЯ ВЕРСИЯ.
Весь флоу через context.user_data. Без мёртвого кода.
"""
import asyncio
import logging
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


# ========== ХЕЛПЕРЫ ==========

def _build_confirm_text(car_data, free_mode: bool = False):
    """Build confirmation text from car_data."""
    type_emoji = {"Электрический": "⚡", "Гибрид": "🔋", "Бензин": "⛽", "Дизель": "🛢️"}.get(car_data.get("type", ""), "")
    currency_emoji = {"USD": "💵", "CNY": "🇨🇳", "EUR": "💶", "KZT": "🇰🇿", "JPY": "💴"}.get(car_data.get("currency", ""), "")
    cur = car_data.get('currency') or 'USD'
    
    delivery_line = ""
    currency_line = ""
    if not free_mode:
        currency_line = f"5. Валюта покупки: {currency_emoji} {car_data.get('currency', '')}\n"
        delivery_line = f"7. Стоимость доставки до границы РК: {car_data.get('delivery_cost', 0):,.2f} {cur}\n"
    
    price_num = "5" if free_mode else "6"
    
    mode_label = "\n(Бесплатный расчёт)" if free_mode else ""
    return (
        "📋 *ПОДТВЕРЖДЕНИЕ ДАННЫХ*" + mode_label + "\n\n"
        f"1. Марка: {car_data.get('brand', '')}\n"
        f"2. Модель: {car_data.get('model', '')}\n"
        f"3. Тип: {type_emoji} {car_data.get('type', '')}\n"
        f"4. Год и месяц выпуска автомобиля: {car_data.get('year_month', '')}\n"
        f"{currency_line}"
        f"{price_num}. Стоимость автомобиля: {car_data.get('price', 0):,.2f} {cur}\n"
        f"{delivery_line}"
        "Всё верно?"
    )

def _build_result_free(car_data):
    """Build free-tier result text."""
    type_emoji = {"Электрический": "⚡", "Гибрид": "🔋", "Бензин": "⛽", "Дизель": "🛢️"}.get(car_data.get("type", ""), "")
    currency_emoji = {"USD": "💵", "CNY": "🇨🇳", "EUR": "💶", "KZT": "🇰🇿", "JPY": "💴"}.get(car_data.get("currency", ""), "")
    cur = car_data.get('currency') or 'USD'
    return (
        "✅ *БЕСПЛАТНЫЙ РАСЧЕТ ГОТОВ!*\n"
        "(Тариф — НОВИЧОК)\n\n"
        f"1. Марка: {car_data.get('brand', '')}\n"
        f"2. Модель: {car_data.get('model', '')}\n"
        f"3. Тип: {type_emoji} {car_data.get('type', '')}\n"
        f"4. Год и месяц выпуска автомобиля: {car_data.get('year_month', '')}\n"
        f"5. Стоимость автомобиля: {car_data.get('price', 0):,.2f} {cur}\n\n"
        "*000000* — Итого по таможенным платежам\n\n"
        "----------------\n\n"
        "💎 *В платной версии Вы увидите:*\n\n"
        "*00000* — Стоимость автомобиля по таможенному каталогу(USD).\n\n"
        "📊 *Платежи (KZT):*\n"
        "• Таможенная пошлина\n"
        "• Таможенный сбор\n"
        "• НДС\n"
        "• Утиль сбор\n"
        "• Первичная регистрация\n"
        "• Сертификат и кнопка\n"
        "• СВХ\n"
        "• Услуги брокера\n"
        "━━━━━━━━━━━━━━━━\n"
        "• *ИТОГО по таможенным платежам(KZT)*\n\n"
        "• Расходы на доставку автомобиля до вашего города.\n\n"
        "• Доп. расходы.\n\n"
        "• Расходы на постановку на гос. учет и получение номера(обычный).\n\n"
        "• Стоимость вашего автомобиля включая таможенные платежи, расходы на доставку, доп. расходы и постановку на учет."
    )


# ========== СТАРТ РАСЧЁТА ==========

async def start_step_by_step(update: Update, context: ContextTypes.DEFAULT_TYPE, free_mode: bool = False):
    """Start step-by-step calculation process."""
    context.user_data["input_step"] = "brand"
    context.user_data["car_data"] = {}
    context.user_data["free_mode"] = free_mode
    
    await update.message.reply_text(
        "🧮 *НАЧАТЬ РАСЧЁТ*\n\n"
        "Для расчёта таможенных платежей введите данные об автомобиле.\n\n"
        "1. Введите марку автомобиля (например: Toyota, Li, Mercedes):",
        parse_mode="Markdown"
    )
    logger.info(f"Started step-by-step for user {update.effective_user.id}")


# ========== ОБРАБОТЧИК КОЛБЭКОВ (КНОПКИ) ==========

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all inline button callbacks."""
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    callback_data = query.data
    
    logger.debug(f"User {user_id}: callback = {callback_data}")
    
    # --- confirm:yes — показать результат ---
    if callback_data == "confirm:yes":
        car_data = context.user_data.get("car_data", {})
        if car_data:
            context.user_data["input_step"] = None  # Расчёт завершён
            from .keyboards import get_free_result_keyboard
            await query.delete_message()
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=_build_result_free(car_data),
                reply_markup=get_free_result_keyboard(),
                parse_mode="Markdown"
            )
        else:
            await query.delete_message()
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="⚠️ Нет данных для расчёта. Начните новый /calculate"
            )
        return
    
    # --- confirm:no — показать меню редактирования ---
    if callback_data == "confirm:no":
        car_data = context.user_data.get("car_data", {})
        if car_data:
            context.user_data["input_step"] = "edit_select"
            cur = car_data.get("currency") or "USD"
            te = {"Электрический": "⚡", "Гибрид": "🔋", "Бензин": "⛽", "Дизель": "🛢️"}.get(car_data.get("type", ""), "")
            ce = {"USD": "💵", "CNY": "🇨🇳", "EUR": "💶", "KZT": "🇰🇿", "JPY": "💴"}.get(car_data.get("currency", ""), "")
            free_mode = context.user_data.get("free_mode", False)
            if free_mode:
                text = (
                    "✏️ *РЕДАКТИРОВАНИЕ ДАННЫХ*\n"
                    "(Бесплатный расчёт)\n\n"
                    f"1. Марка: {car_data.get('brand', '')}\n"
                    f"2. Модель: {car_data.get('model', '')}\n"
                    f"3. Тип: {te} {car_data.get('type', '')}\n"
                    f"4. Год и месяц выпуска: {car_data.get('year_month', '')}\n"
                    f"5. Стоимость: {car_data.get('price', 0):,.2f} {cur}\n\n"
                    "Отправьте номер параметра (1-5) для изменения"
                )
            else:
                text = (
                    "✏️ *РЕДАКТИРОВАНИЕ ДАННЫХ*\n\n"
                    f"1. Марка: {car_data.get('brand', '')}\n"
                    f"2. Модель: {car_data.get('model', '')}\n"
                    f"3. Тип: {te} {car_data.get('type', '')}\n"
                    f"4. Год и месяц выпуска: {car_data.get('year_month', '')}\n"
                    f"5. Валюта покупки: {ce} {car_data.get('currency', '')}\n"
                    f"6. Стоимость: {car_data.get('price', 0):,.2f} {cur}\n"
                    f"7. Доставка: {car_data.get('delivery_cost', 0):,.2f} {cur}\n\n"
                    "Отправьте номер параметра (1-7) для изменения"
                )
            await query.message.reply_text(text)
        else:
            await query.edit_message_text("⚠️ Нет данных. Начните новый расчёт /calculate")
        return
    
    # --- edit_engine_type:* — выбор типа при редактировании ---
    if callback_data.startswith("edit_engine_type:"):
        engine_map = {"electric": "Электрический", "hybrid": "Гибрид", "gasoline": "Бензин"}
        car_data = context.user_data.get("car_data", {})
        car_data["type"] = engine_map.get(callback_data.split(":")[1], "Бензин")
        context.user_data["car_data"] = car_data
        context.user_data["input_step"] = "confirm"
        from .keyboards import get_confirmation_keyboard
        await query.edit_message_text(
            _build_confirm_text(car_data, context.user_data.get("free_mode", False)),
            reply_markup=get_confirmation_keyboard(),
            parse_mode="Markdown"
        )
        return
    
    # --- edit_currency:* — выбор валюты при редактировании ---
    if callback_data.startswith("edit_currency:"):
        cur_map = {"usd": "USD", "cny": "CNY", "eur": "EUR", "kzt": "KZT", "jpy": "JPY"}
        car_data = context.user_data.get("car_data", {})
        car_data["currency"] = cur_map.get(callback_data.split(":")[1].lower(), "USD")
        context.user_data["car_data"] = car_data
        context.user_data["input_step"] = "confirm"
        from .keyboards import get_confirmation_keyboard
        await query.edit_message_text(
            _build_confirm_text(car_data, context.user_data.get("free_mode", False)),
            reply_markup=get_confirmation_keyboard(),
            parse_mode="Markdown"
        )
        return
    
    # --- edit_brand_continue — вернуться к подтверждению ---
    if callback_data == "edit_brand_continue":
        context.user_data["input_step"] = "confirm"
        from .keyboards import get_confirmation_keyboard
        await query.edit_message_text(
            _build_confirm_text(context.user_data.get("car_data", {})),
            reply_markup=get_confirmation_keyboard(),
            parse_mode="Markdown"
        )
        return
    
    # --- edit_brand_restart — начать расчёт заново ---
    if callback_data == "edit_brand_restart":
        context.user_data["input_step"] = "brand"
        context.user_data["car_data"] = {}
        cancel_kb = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Отмена", callback_data="calc_cancel")]])
        await query.edit_message_text(
            "🔄 *Начинаем новый расчёт*\n\n1. Введите марку автомобиля (например: Toyota, Li, Mercedes):",
            reply_markup=cancel_kb,
            parse_mode="Markdown"
        )
        return
    
    # --- engine_type:* — выбор типа в основном флоу ---
    if callback_data.startswith("engine_type:") and "input_step" in context.user_data:
        eng = callback_data.split(":")[1]
        names = {"electric": "Электрический", "hybrid": "Гибрид", "gasoline": "Бензин"}
        emoji = {"electric": "⚡", "hybrid": "🔋", "gasoline": "⛽"}
        car_data = context.user_data.get("car_data", {})
        car_data["type"] = names.get(eng, eng)
        context.user_data["car_data"] = car_data
        context.user_data["input_step"] = "year_month"
        cancel_kb = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Отмена", callback_data="calc_cancel")]])
        await query.message.reply_text(
            f"✅ Тип: {emoji.get(eng, '')} {car_data['type']}\n\n4. Введите год и месяц выпуска (ГГГГ-ММ):",
            reply_markup=cancel_kb,
            parse_mode="Markdown"
        )
        return
    
    # --- currency:* — выбор валюты в основном флоу ---
    if callback_data.startswith("currency:") and "input_step" in context.user_data:
        cur = callback_data.split(":")[1].upper()
        emoji = {"USD": "💵", "CNY": "🇨🇳", "EUR": "💶", "KZT": "🇰🇿", "JPY": "💴"}
        car_data = context.user_data.get("car_data", {})
        car_data["currency"] = cur
        context.user_data["car_data"] = car_data
        context.user_data["input_step"] = "price"
        cancel_kb = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Отмена", callback_data="calc_cancel")]])
        await query.message.reply_text(
            f"✅ Валюта: {emoji.get(cur, '')} {cur}\n\n6. Введите стоимость автомобиля ({cur}):",
            reply_markup=cancel_kb,
            parse_mode="Markdown"
        )
        return
    
    # --- calc_cancel — отмена ---
    if callback_data == "calc_cancel":
        context.user_data["input_step"] = None
        context.user_data["car_data"] = {}
        from .keyboards import get_start_keyboard
        welcome_text = (
            f"🚗 *Добро пожаловать, {query.from_user.first_name or ''}!*\n\n"
            "Я — KZ Customs Calculator Bot, помогу рассчитать таможенные платежи "
            "на легковые автомобили для ввоза в Республику Казахстан.\n\n"
            "📋 *КАК ЭТО РАБОТАЕТ:*\n"
            "• Вводите данные об автомобиле\n"
            "• Получаете расчёт\n\n"
            "💰 *ТАРИФЫ:*\n"
            "• *Новичок:* 3 расчёта/месяц (бесплатно)\n"
            "• *Оплата по факту:* 299 ₸/расчёт\n"
            "• *Пакеты:* 500/1,000/2,000 ₸ (скидка до 44%)\n"
            "• *Подписка PRO:* 2,990 ₸/месяц\n"
            "Если Ваша деятельность связана с автомобильным миром, "
            "здесь может быть Ваша реклама.\n"
            "Напишите нам: info@calc.kz"
        )
        await query.message.reply_text(
            welcome_text,
            parse_mode="Markdown",
            reply_markup=get_start_keyboard()
        )
        try:
            await query.delete_message()
        except:
            pass
        return
    
    # --- start_input — начало с кнопки /calculate ---
    if callback_data == "start_input":
        context.user_data["input_step"] = "brand"
        context.user_data["car_data"] = {}
        context.user_data["free_mode"] = False
        cancel_kb = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Отмена", callback_data="calc_cancel")]])
        await query.edit_message_text(
            "1. Введите марку автомобиля (например: Toyota, Li, Mercedes):",
            reply_markup=cancel_kb,
            parse_mode="Markdown"
        )
        return
    
    # --- error_help — показать справку ---
    if callback_data == "error_help":
        from src.bot.messages import get_help_message
        help_text, help_keyboard = get_help_message()
        await query.message.reply_text(help_text, reply_markup=help_keyboard, parse_mode="Markdown")
        return
    
    # --- show_tariffs — показать тарифы ---
    # --- pay stub handlers (заглушки) ---
    if callback_data in ("pay_299", "pay_500", "pay_1000", "pay_2000", "pay_pro"):
        await query.answer()
        prices = {
            "pay_299": "299 ₸ за 1 расчёт",
            "pay_500": "500 ₸ — пакет на 2 расчёта",
            "pay_1000": "1 000 ₸ — пакет на 5 расчётов",
            "pay_2000": "2 000 ₸ — пакет на 12 расчётов",
            "pay_pro": "2 990 ₸/месяц — подписка PRO",
        }
        from .keyboards import get_tariffs_keyboard
        text = (
            f"💳 *Оплата:* {prices[callback_data]}\n\n"
            "🚧 *Раздел оплаты находится в разработке.*\n\n"
            "Скоро здесь можно будет оплатить тариф напрямую через Kaspi Pay.\n\n"
            "Пока можете воспользоваться бесплатным расчётом.👇"
        )
        await query.message.reply_text(text, parse_mode="Markdown", reply_markup=get_tariffs_keyboard())
        return

    if callback_data == "show_tariffs":
        await query.answer("💰 Загружаю тарифы...")
        from .keyboards import get_tariffs_keyboard
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
            "Если Ваша деятельность связана с автомобильным миром, "
            "здесь может быть Ваша реклама.\n"
            "Напишите нам: info@calc.kz"
        )
        await query.message.reply_text(tariffs_text, parse_mode="Markdown", reply_markup=get_tariffs_keyboard())
        return

    # --- error_home — вернуться на главную ---
    if callback_data == "error_home":
        from .keyboards import get_start_keyboard
        from src.bot.handlers import build_welcome_text
        user = update.effective_user
        welcome_text = build_welcome_text(user)
        await query.message.reply_text(
            welcome_text,
            parse_mode="Markdown",
            reply_markup=get_start_keyboard()
        )
        return
    
    # --- free_start_input — показать описание бесплатного расчёта ---
    if callback_data == "free_start_input":
        from .keyboards import get_free_start_calc_keyboard
        await query.edit_message_text(
            "🚗 *БЕСПЛАТНЫЙ РАСЧЁТ ТАМОЖЕННЫХ ПЛАТЕЖЕЙ*\n"
            "(на легковые автомобили при ввозе в Республику Казахстан)\n\n"
            "📊 *ПАРАМЕТРЫ РАСЧЕТА:*\n"
            "1. Марка\n"
            "2. Модель\n"
            "3. Тип (электромобиль, гибрид, ДВС — бензин/дизель)\n"
            "4. Год и месяц выпуска (ГГГГ-ММ)\n"
            "5. Стоимость автомобиля (в долларах США)\n\n"
            "_Для перехода на полную версию расчета нажмите кнопку —_ *Тарифы*\n\n"
            "Нажмите 🚀 НАЧАТЬ РАСЧЁТ чтобы продолжить.",
            parse_mode="Markdown",
            reply_markup=get_free_start_calc_keyboard()
        )
        return
    
    # --- free_begin_input — фактическое начало бесплатного расчёта (шаг 1) ---
    if callback_data == "free_begin_input":
        context.user_data["input_step"] = "brand"
        context.user_data["car_data"] = {}
        context.user_data["free_mode"] = True
        cancel_kb = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Отмена", callback_data="calc_cancel")]])
        await query.edit_message_text(
            "1. Введите марку автомобиля (например: Toyota, Li, Mercedes):",
            reply_markup=cancel_kb,
            parse_mode="Markdown"
        )
        return
    
    logger.warning(f"User {user_id}: unknown callback: {callback_data}")


# ========== ОБРАБОТЧИК ТЕКСТА ==========

async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle voice messages - show standard error."""
    from .keyboards import get_error_keyboard
    await update.message.reply_text(
        "❌ *ОШИБКА ВВОДА!*\n\n"
        "Если Ваша деятельность связана с автомобильным миром, "
        "здесь может быть Ваша реклама.\n"
        "Напишите нам: info@calc.kz",
        reply_markup=get_error_keyboard(),
        parse_mode="Markdown"
    )

async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text input for all steps."""
    user_id = update.effective_user.id
    text = update.message.text.strip()
    input_step = context.user_data.get("input_step")
    car_data = context.user_data.get("car_data", {})
    
    # Если расчёт уже завершён (есть данные, но input_step не установлен) — показать результат
    if not input_step and car_data:
        from .keyboards import get_result_keyboard
        await update.message.reply_text(
            "❌ *Ошибка ввода!* Используйте кнопки под сообщением или команды.",
            parse_mode="Markdown"
        )
        await update.message.reply_text(
            _build_result_free(car_data),
            reply_markup=get_free_result_keyboard(),
            parse_mode="Markdown"
        )
        return
    
    # Cancel
    if text.lower() in ["отмена", "cancel", "стоп", "stop", "выход"] and input_step:
        context.user_data["input_step"] = None
        context.user_data["car_data"] = {}
        await update.message.reply_text("❌ Расчёт отменён.\n\nНачать новый расчёт: /calculate", parse_mode="Markdown")
        return
    
    # ---- edit_select — ввод номера параметра для редактирования ----
    if input_step == "edit_select":
        free_mode = context.user_data.get("free_mode", False)
        valid_options = ["1", "2", "3", "4", "5"] if free_mode else ["1", "2", "3", "4", "5", "6", "7"]
        if text not in valid_options:
            msg = "❌ Неверный номер. Отправьте число от 1 до 5." if free_mode else "❌ Неверный номер. Отправьте число от 1 до 7."
            await update.message.reply_text(msg, parse_mode="Markdown")
            return
        
        cur = car_data.get("currency") or "USD"
        params = {
            "1": ("brand", "Введите марку"),
            "2": ("model", "Введите модель"),
            "3": ("type", "Выберите тип автомобиля:"),
            "4": ("year_month", "Введите год и месяц (ГГГГ-ММ):"),
            "5": ("price", f"Введите стоимость ({cur}):"),
            "6": ("delivery", f"Введите стоимость доставки до границы РК ({cur}):"),
            "7": ("delivery", f"Введите стоимость доставки до границы РК ({cur}):")
        }
        field, prompt = params[text]
        
        # Параметр 1 (марка) — нельзя изменить
        if field == "brand":
            lock_kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Продолжить расчёт", callback_data="edit_brand_continue")],
                [InlineKeyboardButton("🔄 Начать снова", callback_data="edit_brand_restart")]
            ])
            await update.message.reply_text("❌ Марку автомобиля изменить нельзя!", reply_markup=lock_kb, parse_mode="Markdown")
            context.user_data["input_step"] = "edit_brand_locked"
            return
        
        context.user_data["input_step"] = f"edit_{field}"
        
        # Параметр 3 (тип) — клавиатура
        if field == "type":
            edit_kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("⚡ Электромобиль", callback_data="edit_engine_type:electric")],
                [InlineKeyboardButton("🔋 Гибрид", callback_data="edit_engine_type:hybrid")],
                [InlineKeyboardButton("⛽ ДВС — бензин/дизель", callback_data="edit_engine_type:gasoline")],
                [InlineKeyboardButton("❌ Отмена", callback_data="calc_cancel")]
            ])
            await update.message.reply_text(f"✏️ {prompt}", reply_markup=edit_kb, parse_mode="Markdown")
            return
        
        # Параметр 5 (валюта) — клавиатура
        if field == "currency":
            edit_cur_kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("💵 USD", callback_data="edit_currency:usd"),
                 InlineKeyboardButton("🇨🇳 CNY", callback_data="edit_currency:cny")],
                [InlineKeyboardButton("💶 EUR", callback_data="edit_currency:eur"),
                 InlineKeyboardButton("🇰🇿 KZT", callback_data="edit_currency:kzt")],
                [InlineKeyboardButton("💴 JPY", callback_data="edit_currency:jpy")],
                [InlineKeyboardButton("❌ Отмена", callback_data="calc_cancel")]
            ])
            await update.message.reply_text(f"✏️ {prompt}", reply_markup=edit_cur_kb, parse_mode="Markdown")
            return
        
        # Остальные — текст
        await update.message.reply_text(f"✏️ {prompt}", parse_mode="Markdown")
        return
    
    # ---- edit_* — обработка текстового ввода при редактировании ----
    if input_step and input_step.startswith("edit_"):
        field = input_step.replace("edit_", "")
        
        if field in ["price", "delivery"]:
            try:
                val = float(''.join(c for c in text if c.isdigit() or c == '.'))
                if val <= 0: raise ValueError
                car_data[field] = val
            except:
                await update.message.reply_text("❌ Неверный формат. Введите число.", parse_mode="Markdown")
                return
        elif field == "year_month":
            em = re.match(r'^(\d{4})-(\d{2})$', text)
            if not em:
                await update.message.reply_text("❌ Неверный формат. Введите ГГГГ-ММ\nПример: 2025-04", parse_mode="Markdown")
                return
            eyear, emonth = int(em.group(1)), int(em.group(2))
            if emonth < 1 or emonth > 12:
                await update.message.reply_text("❌ Месяц должен быть от 01 до 12.\nПример: 2025-04", parse_mode="Markdown")
                return
            if eyear > 2026:
                await update.message.reply_text(
                    "❌ Некорректный год выпуска. Год не может быть в будущем.\nПример: 2025-04",
                    parse_mode="Markdown"
                )
                return
            if eyear < 1950:
                await update.message.reply_text(
                    "❌ Некорректный год выпуска. Автомобили выпускаются с 1950 года.\nПример: 2025-04",
                    parse_mode="Markdown"
                )
                return
            if eyear == 2026 and emonth > 5:
                await update.message.reply_text(
                    "❌ Указанный месяц ещё не наступил. Проверьте дату выпуска.",
                    parse_mode="Markdown"
                )
                return
            car_data[field] = text
        elif field == "model":
            if len(text.strip()) < 1:
                await update.message.reply_text("❌ Введите название модели.", parse_mode="Markdown")
                return
            car_data[field] = text
        elif field in ["type", "currency"]:
            # Эти поля редактируются только через кнопки
            await update.message.reply_text(
                "❌ *ОШИБКА ВВОДА!* На этом шаге нужно нажать одну из кнопок.",
                parse_mode="Markdown"
            )
            return
        else:
            car_data[field] = text
        
        context.user_data["car_data"] = car_data
        context.user_data["input_step"] = "confirm"
        from .keyboards import get_confirmation_keyboard
        await update.message.reply_text(
            _build_confirm_text(car_data, context.user_data.get("free_mode", False)),
            reply_markup=get_confirmation_keyboard(),
            parse_mode="Markdown"
        )
        return
    
    # ---- Подтверждение (кнопки) — показать подтверждение заново ----
    if input_step == "confirm":
        from .keyboards import get_confirmation_keyboard
        await update.message.reply_text(
            "❌ *Ошибка ввода!* Используйте кнопки под сообщением.",
            parse_mode="Markdown"
        )
        await update.message.reply_text(
            _build_confirm_text(car_data, context.user_data.get("free_mode", False)),
            reply_markup=get_confirmation_keyboard(),
            parse_mode="Markdown"
        )
        return
    
    # ---- Шаг 1: Марка ----
    if input_step == "brand":
        car_data["brand"] = text
        context.user_data["car_data"] = car_data
        context.user_data["input_step"] = "model"
        cancel_kb = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Отмена", callback_data="calc_cancel")]])
        await update.message.reply_text(
            f"✅ Марка: {text}\n\n2. Введите модель автомобиля:",
            reply_markup=cancel_kb, parse_mode="Markdown"
        )
        return
    
    # ---- Шаг 2: Модель ----
    if input_step == "model":
        car_data["model"] = text
        context.user_data["car_data"] = car_data
        context.user_data["input_step"] = "type"
        from .keyboards import get_engine_type_keyboard
        await update.message.reply_text(
            f"✅ Модель: {text}\n\n3. Выберите тип автомобиля:",
            reply_markup=get_engine_type_keyboard(), parse_mode="Markdown"
        )
        return
    
    # ---- Шаг 3 (кнопки): Тип — только кнопки, текст запрещён ----
    if input_step == "type":
        from .keyboards import get_engine_type_keyboard
        await update.message.reply_text(
            "❌ *ОШИБКА ВВОДА!* На этом шаге нужно нажать одну из кнопок.\n\n"
            "3. Выберите тип автомобиля:",
            reply_markup=get_engine_type_keyboard(), parse_mode="Markdown"
        )
        return
    
    # ---- Шаг 5 (кнопки): Валюта — только кнопки, текст запрещён ----
    if input_step == "currency":
        from .keyboards import get_currency_keyboard
        await update.message.reply_text(
            "❌ *ОШИБКА ВВОДА!* На этом шаге нужно нажать одну из кнопок.\n\n"
            "5. Выберите валюту покупки:",
            reply_markup=get_currency_keyboard(), parse_mode="Markdown"
        )
        return
    
    # ---- Шаг edit_brand_locked — только кнопки ----
    if input_step == "edit_brand_locked":
        lock_kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Продолжить расчёт", callback_data="edit_brand_continue")],
            [InlineKeyboardButton("🔄 Начать снова", callback_data="edit_brand_restart")]
        ])
        await update.message.reply_text(
            "❌ *ОШИБКА ВВОДА!* На этом шаге нужно нажать одну из кнопок.",
            reply_markup=lock_kb, parse_mode="Markdown"
        )
        return
    
    # ---- Шаг 4: Год и месяц ----
    if input_step == "year_month":
        m = re.match(r'^(\d{4})-(\d{2})$', text)
        if m:
            year = int(m.group(1))
            month = int(m.group(2))
            if month < 1 or month > 12:
                await update.message.reply_text(
                    "❌ Неверный месяц. Месяц должен быть от 01 до 12.\nПример: 2025-04",
                    parse_mode="Markdown"
                )
                return
            if year > 2026:
                await update.message.reply_text(
                    "❌ Некорректный год выпуска. Год не может быть в будущем.\nПример: 2025-04",
                    parse_mode="Markdown"
                )
                return
            if year < 1950:
                await update.message.reply_text(
                    "❌ Некорректный год выпуска. Автомобили выпускаются с 1950 года.\nПример: 2025-04",
                    parse_mode="Markdown"
                )
                return
            if year == 2026 and month > 5:
                await update.message.reply_text(
                    "❌ Указанный месяц ещё не наступил. Проверьте дату выпуска.",
                    parse_mode="Markdown"
                )
                return
            car_data["year_month"] = text
            context.user_data["car_data"] = car_data
            free_mode = context.user_data.get("free_mode", False)
            if free_mode:
                context.user_data["input_step"] = "price"
                cancel_kb = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Отмена", callback_data="calc_cancel")]])
                await update.message.reply_text(
                    f"✅ Год и месяц: {text}\n\n5. Введите стоимость автомобиля (в долларах США):",
                    reply_markup=cancel_kb, parse_mode="Markdown"
                )
            else:
                context.user_data["input_step"] = "currency"
                from .keyboards import get_currency_keyboard
                await update.message.reply_text(
                    f"✅ Год и месяц: {text}\n\n5. Выберите валюту покупки:",
                    reply_markup=get_currency_keyboard(), parse_mode="Markdown"
                )
        else:
            await update.message.reply_text(
                "❌ Неверный формат. Введите ГГГГ-ММ\nПример: 2025-04", parse_mode="Markdown"
            )
        return
    
    # ---- Шаг 7: Доставка ----
    if input_step == "delivery":
        try:
            val = float(''.join(c for c in text if c.isdigit() or c == '.'))
            if val < 0: raise ValueError
            car_data["delivery_cost"] = val
            context.user_data["car_data"] = car_data
            context.user_data["input_step"] = "confirm"
            from .keyboards import get_confirmation_keyboard
            await update.message.reply_text(
                _build_confirm_text(car_data, context.user_data.get("free_mode", False)),
                reply_markup=get_confirmation_keyboard(), parse_mode="Markdown"
            )
        except:
            await update.message.reply_text("❌ Неверный формат. Введите число.", parse_mode="Markdown")
        return
    
    # ---- Шаг 6: Стоимость ----
    if input_step == "price":
        try:
            val = float(''.join(c for c in text if c.isdigit() or c == '.'))
            if val <= 0: raise ValueError
            cur = car_data.get("currency", "USD")
            car_data["price"] = val
            car_data["delivery_cost"] = 0  # no delivery in free tier
            context.user_data["car_data"] = car_data
            free_mode = context.user_data.get("free_mode", False)
            if free_mode:
                context.user_data["input_step"] = "confirm"
                from .keyboards import get_confirmation_keyboard
                await update.message.reply_text(
                    _build_confirm_text(car_data, context.user_data.get("free_mode", False)),
                    reply_markup=get_confirmation_keyboard(), parse_mode="Markdown"
                )
            else:
                context.user_data["input_step"] = "delivery"
                cancel_kb = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Отмена", callback_data="calc_cancel")]])
                await update.message.reply_text(
                    f"✅ Стоимость: {val:,.2f} {cur}\n\n7. Введите стоимость доставки до границы РК ({cur}):",
                    reply_markup=cancel_kb, parse_mode="Markdown"
                )
        except:
            await update.message.reply_text("❌ Неверный формат. Введите число.", parse_mode="Markdown")
        return
    
    # Если input_step не установлен — сообщение об ошибке
    if not input_step:
        from .keyboards import get_error_keyboard
        await update.message.reply_text(
            "❌ *ОШИБКА ВВОДА!*\n\n"
            "Если Ваша деятельность связана с автомобильным миром, "
            "здесь может быть Ваша реклама.\n"
            "Напишите нам: info@calc.kz",
            reply_markup=get_error_keyboard(),
            parse_mode="Markdown"
        )
        return
    
    logger.warning(f"User {user_id}: unhandled input_step={input_step}, text={text}")


# ========== СТАРЫЕ ФУНКЦИИ ДЛЯ СОВМЕСТИМОСТИ (не используются) ==========

async def handle_cancel(update, context, session):
    pass

async def handle_back(update, context, session):
    pass

async def handle_restart(update, context, session):
    pass

async def handle_result_action(update, context, session, callback_data):
    pass
