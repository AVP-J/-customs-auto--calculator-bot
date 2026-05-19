"""
Inline keyboards for step-by-step interface.
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from .states import UserState


def get_start_calc_keyboard() -> InlineKeyboardMarkup:
    """Start calculation button with cancel."""
    keyboard = [
        [InlineKeyboardButton("🚀 НАЧАТЬ РАСЧЁТ", callback_data="start_input")],
        [InlineKeyboardButton("❌ Отмена", callback_data="calc_cancel")]
    ]
def get_engine_type_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for choosing engine type — only 3 options."""
    keyboard = [
        [InlineKeyboardButton("⚡ Электромобиль", callback_data="engine_type:electric")],
        [InlineKeyboardButton("🔋 Гибрид", callback_data="engine_type:hybrid")],
        [InlineKeyboardButton("⛽ ДВС — бензин/дизель", callback_data="engine_type:gasoline")],
        [InlineKeyboardButton("❌ Отмена", callback_data="calc_cancel")]
    ]
    return InlineKeyboardMarkup(keyboard)
def get_confirmation_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for data confirmation."""
    keyboard = [
        [
            InlineKeyboardButton("✅ Да, всё верно", callback_data="confirm:yes"),
            InlineKeyboardButton("✏️ Исправить", callback_data="confirm:no")
        ],
        [
            InlineKeyboardButton("❌ Отмена", callback_data="calc_cancel")
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
            InlineKeyboardButton("💴 JPY", callback_data="currency:jpy"),
        ],
        [
            InlineKeyboardButton("❌ Отмена", callback_data="calc_cancel"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
def get_free_start_calc_keyboard() -> InlineKeyboardMarkup:
    """Start free calculation button with tariffs and home."""
    keyboard = [
        [InlineKeyboardButton("💰 Тарифы", callback_data="show_tariffs")],
        [InlineKeyboardButton("🚀 НАЧАТЬ РАСЧЁТ", callback_data="free_begin_input")],
        [InlineKeyboardButton("🏠 В начало", callback_data="error_home")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_tariffs_keyboard():
    """Keyboard for tariffs screen."""
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🆓 НОВИЧОК (Бесплатно)", callback_data="free_start_input")],
        [InlineKeyboardButton("💳 ОПЛАТА ПО ФАКТУ — 299 ₸", callback_data="pay_299")],
        [InlineKeyboardButton("📦 ПАКЕТ 500 ₸", callback_data="pay_500")],
        [InlineKeyboardButton("📦 ПАКЕТ 1 000 ₸", callback_data="pay_1000")],
        [InlineKeyboardButton("📦 ПАКЕТ 2 000 ₸", callback_data="pay_2000")],
        [InlineKeyboardButton("👑 ПОДПИСКА PRO — 2 990 ₸/мес", callback_data="pay_pro")],
        [InlineKeyboardButton("🏠 В начало", callback_data="error_home")]
    ])
    return keyboard

def get_error_keyboard() -> InlineKeyboardMarkup:
    """Error screen keyboard with help and home buttons."""
    keyboard = [
        [InlineKeyboardButton("📚 Справка", callback_data="error_help")],
        [InlineKeyboardButton("🏠 В начало", callback_data="error_home")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_start_keyboard() -> InlineKeyboardMarkup:
    """Start screen keyboard with free calculate and help buttons."""
    keyboard = [
        [InlineKeyboardButton("🧮 Рассчитать бесплатно", callback_data="free_start_input")],
        [InlineKeyboardButton("📚 Справка", callback_data="error_help")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_free_result_keyboard() -> InlineKeyboardMarkup:
    """Keyboard after free calculation."""
    keyboard = [
        [InlineKeyboardButton("💰 Купить тариф", callback_data="show_tariffs")],
        [InlineKeyboardButton("🔄 Новый расчёт (бесплатно)", callback_data="free_start_input")],
        [InlineKeyboardButton("🏠 В начало", callback_data="error_home")]
    ]
    return InlineKeyboardMarkup(keyboard)
