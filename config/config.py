"""
Configuration module for Customs Calculator Bot.
Replace placeholder values with actual credentials.
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Telegram Bot Configuration
# TODO: Replace with your actual bot token from @BotFather
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Example: "1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ"

# Admin user ID (your Telegram ID)
# TODO: Replace with your actual Telegram ID
TELEGRAM_ADMIN_ID = 1605591886  # Your Telegram ID

# Database Configuration
# Using SQLite for local development, will switch to PostgreSQL later
DATABASE_URL = f"sqlite:///{BASE_DIR}/data/customs_bot.db"
DATABASE_POOL_SIZE = 5
DATABASE_MAX_OVERFLOW = 10

# Payment Configuration (mock for now)
KASPI_API_KEY = "mock_kaspi_api_key"
KASPI_MERCHANT_ID = "mock_merchant_id"
KASPI_SECRET_KEY = "mock_secret_key"

# Stripe Configuration (backup, mock for now)
STRIPE_API_KEY = "mock_stripe_api_key"
STRIPE_WEBHOOK_SECRET = "mock_webhook_secret"

# Application Configuration
DEBUG = True
LOG_LEVEL = "DEBUG"
TIMEZONE = "Asia/Almaty"

# Currency rates
CURRENCY_SOURCE = BASE_DIR / "data" / "currency_rates.json"
CURRENCY_UPDATE_INTERVAL = 3600  # 1 hour

# Business rules
FREE_CALCULATIONS_PER_MONTH = 3
PAY_PER_USE_PRICE = 299  # ₸
PACKAGE_1_PRICE = 500    # ₸ for 2 calculations
PACKAGE_1_CALCULATIONS = 2
PACKAGE_2_PRICE = 1000   # ₸ for 5 calculations
PACKAGE_2_CALCULATIONS = 5
PACKAGE_3_PRICE = 2000   # ₸ for 12 calculations
PACKAGE_3_CALCULATIONS = 12
SUBSCRIPTION_PRICE = 1990  # ₸/month

# File paths
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"
CACHE_DIR = BASE_DIR / "cache"

# Create directories
for directory in [DATA_DIR, LOG_DIR, CACHE_DIR]:
    directory.mkdir(exist_ok=True)

# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": LOG_LEVEL,
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": LOG_DIR / "bot.log",
            "formatter": "standard",
            "level": "INFO",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console", "file"],
            "level": LOG_LEVEL,
            "propagate": True,
        },
    },
}
