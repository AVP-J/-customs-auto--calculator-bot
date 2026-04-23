"""
Messages for step-by-step interface.
"""
from .states import UserState


def get_message_for_state(state: UserState, user_data: dict = None) -> str:
    """
    Get message for specific user state.
    
    Args:
        state: Current user state
        user_data: User session data
    
    Returns:
        Message text for the state
    """
    if state == UserState.CHOOSE_VEHICLE_TYPE:
        return get_vehicle_type_message()
    
    elif state == UserState.ENTER_PRICE:
        return get_price_message(user_data)
    
    elif state == UserState.CHOOSE_ENGINE_TYPE:
        return get_engine_type_message(user_data)
    
    elif state == UserState.CHOOSE_COUNTRY:
        return get_country_message(user_data)
    
    elif state == UserState.CONFIRM_DATA:
        return get_confirmation_message(user_data)
    
    elif state == UserState.SHOW_RESULT:
        return get_result_message(user_data)
    
    # Default message
    return "🚗 *Customs Calculator Bot*\n\nВыберите действие:"


def get_vehicle_type_message() -> str:
    """Message for vehicle type selection."""
    return (
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
        "Нажмите 🚀 НАЧАТЬ РАСЧЁТ чтобы продолжить."
    )


def get_price_message(user_data: dict) -> str:
    """Message for price input."""
    vehicle_type = user_data.get("vehicle_type", "автомобиль")
    vehicle_names = {
        "car": "легкового автомобиля",
        "truck": "грузового автомобиля",
        "motorcycle": "мотоцикла",
        "bus": "автобуса",
        "special": "спецтехники",
        "bicycle": "велосипеда"
    }
    
    vehicle_name = vehicle_names.get(vehicle_type, "транспортного средства")
    
    return (
        f"📊 *Шаг 2: Введите стоимость {vehicle_name}*\n\n"
        f"Введите стоимость в долларах США (USD).\n"
        f"Пример: 30000\n\n"
        f"*Примечание:*\n"
        f"• Укажите стоимость без НДС и других налогов\n"
        f"• Если цена в другой валюте, конвертируйте в USD\n"
        f"• Можно указать дробное число: 29999.99\n\n"
        f"Введите число:"
    )


def get_engine_type_message(user_data: dict) -> str:
    """Message for engine type selection."""
    price = user_data.get("price")
    price_text = f"{price:,.0f} USD" if price else "___ USD"
    
    return (
        f"✅ Стоимость: {price_text}\n\n"
        f"🔧 *Шаг 3: Выберите тип двигателя*\n\n"
        f"Выберите тип двигателя:\n\n"
        f"• ⚡ *Электромобиль* — 0% пошлина до 2028 года\n"
        f"• 🔋 *Гибрид* — скидка 50% на пошлину\n"
        f"• ⛽ *Бензин* — стандартная пошлина\n"
        f"• 🛢️ *Дизель* — повышенная пошлина\n\n"
        f"Выберите тип кнопкой ниже:"
    )


def get_country_message(user_data: dict) -> str:
    """Message for country selection."""
    engine_type = user_data.get("engine_type", "двигателя")
    engine_names = {
        "electric": "электромобиль",
        "hybrid": "гибрид",
        "gasoline": "бензиновый",
        "diesel": "дизельный"
    }
    
    engine_name = engine_names.get(engine_type, engine_type)
    
    return (
        f"✅ Двигатель: {engine_name}\n\n"
        f"🌍 *Шаг 4: Выберите страну происхождения*\n\n"
        f"Выберите страну, из которой ввозится автомобиль:\n\n"
        f"• 🇨🇳 *Китай* — большинство электромобилей\n"
        f"• 🇺🇸 *США* — американские автомобили\n"
        f"• 🇪🇺 *Европа* — европейские бренды\n"
        f"• 🇯🇵 *Япония* — японские автомобили\n"
        f"• 🇰🇷 *Корея* — корейские автомобили\n"
        f"• 🇷🇺 *Россия* — российские автомобили\n\n"
        f"Выберите страну кнопкой ниже:"
    )


def get_confirmation_message(user_data: dict) -> str:
    """Message for data confirmation."""
    # Format data for display
    vehicle_type = user_data.get("vehicle_type", "не указан")
    price = user_data.get("price", 0)
    engine_type = user_data.get("engine_type", "не указан")
    country = user_data.get("country", "не указана")
    
    # Human-readable names
    vehicle_names = {
        "car": "🚗 Легковой автомобиль",
        "truck": "🚚 Грузовой автомобиль",
        "motorcycle": "🏍️ Мотоцикл",
        "bus": "🚌 Автобус",
        "special": "🚜 Спецтехника",
        "bicycle": "🚲 Велосипед"
    }
    
    engine_names = {
        "electric": "⚡ Электромобиль",
        "hybrid": "🔋 Гибрид",
        "gasoline": "⛽ Бензин",
        "diesel": "🛢️ Дизель"
    }
    
    country_names = {
        "china": "🇨🇳 Китай",
        "usa": "🇺🇸 США",
        "europe": "🇪🇺 Европа",
        "japan": "🇯🇵 Япония",
        "korea": "🇰🇷 Корея",
        "russia": "🇷🇺 Россия"
    }
    
    return (
        f"📋 *Проверьте введённые данные:*\n\n"
        f"• *Тип ТС:* {vehicle_names.get(vehicle_type, vehicle_type)}\n"
        f"• *Стоимость:* {price:,.0f} USD\n"
        f"• *Двигатель:* {engine_names.get(engine_type, engine_type)}\n"
        f"• *Страна:* {country_names.get(country, country)}\n\n"
        f"*Всё верно?*\n\n"
        f"Если да — нажмите «Всё верно, рассчитать»\n"
        f"Если нужно исправить — нажмите «Исправить»"
    )


def get_result_message(user_data: dict) -> str:
    """Message for calculation result."""
    # TODO: Replace with actual calculation
    # For now, show dummy result
    
    price = user_data.get("price", 30000)
    
    # Dummy calculation
    customs_duty = price * 0.15  # 15%
    vat = (price + customs_duty) * 0.16  # 16% VAT
    excise_tax = price * 0.05  # 5%
    clearance_fee = 50000  # 50,000 KZT
    total_kzt = (price + customs_duty + vat + excise_tax) * 470 + clearance_fee
    
    return (
        f"🎯 *Результат расчёта таможенных платежей*\n\n"
        f"📊 *Исходные данные:*\n"
        f"• Стоимость автомобиля: {price:,.0f} USD\n"
        f"• Курс USD/KZT: 470 ₸\n\n"
        f"💰 *Таможенные платежи:*\n"
        f"• Таможенная пошлина: {customs_duty:,.0f} USD ({customs_duty/price*100:.1f}%)\n"
        f"• НДС (16%): {vat:,.0f} USD\n"
        f"• Акцизный налог: {excise_tax:,.0f} USD\n"
        f"• Сбор за таможенное оформление: 50,000 ₸\n\n"
        f"💵 *Итого к оплате:*\n"
        f"• В USD: {price + customs_duty + vat + excise_tax:,.0f} USD\n"
        f"• В KZT: {total_kzt:,.0f} ₸\n\n"
        f"📈 *Итоговая стоимость автомобиля в Казахстане:*\n"
        f"*{total_kzt:,.0f} ₸*\n\n"
        f"⏱️ *Расчёт действителен:* 24 часа\n"
        f"📅 *Дата расчёта:* 20.04.2026\n\n"
        f"*Примечание:* Это предварительный расчёт. "
        f"Точную сумму уточняйте у таможенного брокера."
    )


def text_message_handler(update, context):
    """Handle text messages (for backward compatibility)."""
    # This will be replaced by step_handlers.handle_text_input
    pass