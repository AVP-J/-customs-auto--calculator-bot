"""
Inline keyboards for step-by-step interface.
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from .states import UserState


def get_keyboard_for_state(state: UserState, user_data: dict = None) -> InlineKeyboardMarkup:
    """
    Get keyboard for specific user state.
    
    Args:
        state: Current user state
        user_data: User session data
    
    Returns:
        InlineKeyboardMarkup for the state
    """
    if state == UserState.CHOOSE_VEHICLE_TYPE:
        return get_vehicle_type_keyboard()
    
    elif state == UserState.CHOOSE_ENGINE_TYPE:
        return get_engine_type_keyboard()
    
    elif state == UserState.CHOOSE_COUNTRY:
        return get_country_keyboard()
    
    elif state == UserState.CONFIRM_DATA:
        return get_confirmation_keyboard()
    
    elif state == UserState.SHOW_RESULT:
        return get_result_keyboard()
    
    # Default empty keyboard
    return InlineKeyboardMarkup([])


def get_vehicle_type_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for choosing vehicle type."""
    keyboard = [
        [
            InlineKeyboardButton("🚗 Легковой", callback_data="vehicle_type:car"),
            InlineKeyboardButton("🚚 Грузовой", callback_data="vehicle_type:truck")
        ],
        [
            InlineKeyboardButton("🏍️ Мотоцикл", callback_data="vehicle_type:motorcycle"),
            InlineKeyboardButton("🚌 Автобус", callback_data="vehicle_type:bus")
        ],
        [
            InlineKeyboardButton("🚜 Спецтехника", callback_data="vehicle_type:special"),
            InlineKeyboardButton("🚲 Велосипед", callback_data="vehicle_type:bicycle")
        ],
        [
            InlineKeyboardButton("❌ Отмена", callback_data="cancel")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_menu_keyboard() -> InlineKeyboardMarkup:
    """Main menu keyboard with commands."""
    keyboard = [
        [
            InlineKeyboardButton("🧮 РАССЧИТАТЬ", callback_data="start_calc"),
        ],
        [
            InlineKeyboardButton("💰 ТАРИФЫ", callback_data="show_tariffs"),
            InlineKeyboardButton("📚 ПОМОЩЬ", callback_data="show_help")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_engine_type_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for choosing engine type."""
    keyboard = [
        [
            InlineKeyboardButton("⚡ Электромобиль", callback_data="engine_type:electric"),
            InlineKeyboardButton("🔋 Гибрид", callback_data="engine_type:hybrid")
        ],
        [
            InlineKeyboardButton("⛽ ДВС — бензин/дизель", callback_data="engine_type:gasoline"),
            InlineKeyboardButton("🛢️ Дизель", callback_data="engine_type:diesel")
        ],
        [
            InlineKeyboardButton("↩️ Назад", callback_data="back"),
            InlineKeyboardButton("❌ Отмена", callback_data="cancel")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_country_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for choosing country of origin."""
    keyboard = [
        [
            InlineKeyboardButton("🇨🇳 Китай", callback_data="country:china"),
            InlineKeyboardButton("🇺🇸 США", callback_data="country:usa")
        ],
        [
            InlineKeyboardButton("🇪🇺 Европа", callback_data="country:europe"),
            InlineKeyboardButton("🇯🇵 Япония", callback_data="country:japan")
        ],
        [
            InlineKeyboardButton("🇰🇷 Корея", callback_data="country:korea"),
            InlineKeyboardButton("🇷🇺 Россия", callback_data="country:russia")
        ],
        [
            InlineKeyboardButton("↩️ Назад", callback_data="back"),
            InlineKeyboardButton("❌ Отмена", callback_data="cancel")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_confirmation_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for data confirmation."""
    keyboard = [
        [
            InlineKeyboardButton("✅ Всё верно, рассчитать", callback_data="confirm:yes"),
            InlineKeyboardButton("✏️ Исправить", callback_data="confirm:no")
        ],
        [
            InlineKeyboardButton("↩️ Начать заново", callback_data="restart"),
            InlineKeyboardButton("❌ Отмена", callback_data="cancel")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_result_keyboard() -> InlineKeyboardMarkup:
    """Keyboard after calculation."""
    keyboard = [
        [
            InlineKeyboardButton("🔄 Новый расчёт", callback_data="new_calculation"),
            InlineKeyboardButton("💾 Сохранить", callback_data="save_result")
        ],
        [
            InlineKeyboardButton("📤 Поделиться", callback_data="share_result"),
            InlineKeyboardButton("📊 История", callback_data="history")
        ],
        [
            InlineKeyboardButton("🏠 В начало", callback_data="start")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_currency_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for choosing currency."""
    keyboard = [
        [
            InlineKeyboardButton("💵 USD", callback_data="currency:usd"),
            InlineKeyboardButton("🇨🇳 CNY", callback_data="currency:cny")
        ],
        [
            InlineKeyboardButton("💶 EUR", callback_data="currency:eur"),
            InlineKeyboardButton("🇰🇿 KZT", callback_data="currency:kzt")
        ],
        [
            InlineKeyboardButton("💴 JPY", callback_data="currency:jpy"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_navigation_keyboard(show_back: bool = True, show_cancel: bool = True) -> InlineKeyboardMarkup:
    """Generic navigation keyboard."""
    buttons = []
    
    if show_back:
        buttons.append(InlineKeyboardButton("↩️ Назад", callback_data="back"))
    
    if show_cancel:
        buttons.append(InlineKeyboardButton("❌ Отмена", callback_data="cancel"))
    
    return InlineKeyboardMarkup([buttons]) if buttons else InlineKeyboardMarkup([])