#!/bin/bash
# Simple manual start script for Customs Calculator Bot

echo "========================================="
echo "🚗 CUSTOMS CALCULATOR BOT - MANUAL START"
echo "========================================="
echo ""
echo "📋 ИНСТРУКЦИЯ:"
echo "1. Этот скрипт запустит бота в этом терминале"
echo "2. Бот будет работать пока ты не нажмёшь Ctrl+C"
echo "3. Для тестирования открой Telegram и найди @CustomsCalcKZBot"
echo ""
echo "⚙️  ПРОВЕРКА КОНФИГУРАЦИИ..."
echo ""

# Check token
TOKEN=$(grep TELEGRAM_BOT_TOKEN .env | cut -d= -f2)
if [ "$TOKEN" = "YOUR_BOT_TOKEN_HERE" ] || [ -z "$TOKEN" ]; then
    echo "❌ ОШИБКА: Токен бота не установлен в .env файле"
    echo "   Открой файл .env и замени YOUR_BOT_TOKEN_HERE на реальный токен"
    exit 1
fi

echo "✅ Токен бота: ${TOKEN:0:10}..."
echo ""

# Check if bot is accessible
echo "📡 Проверяю доступность бота через Telegram API..."
if curl -s "https://api.telegram.org/bot$TOKEN/getMe" | grep -q '"ok":true'; then
    BOT_INFO=$(curl -s "https://api.telegram.org/bot$TOKEN/getMe")
    BOT_NAME=$(echo "$BOT_INFO" | grep -o '"first_name":"[^"]*"' | cut -d'"' -f4)
    BOT_USERNAME=$(echo "$BOT_INFO" | grep -o '"username":"[^"]*"' | cut -d'"' -f4)
    echo "✅ Бот доступен: $BOT_NAME (@$BOT_USERNAME)"
else
    echo "❌ Бот недоступен через API. Проверь токен."
    exit 1
fi

echo ""
echo "🚀 ЗАПУСК БОТА..."
echo "========================================="
echo "Нажми Ctrl+C чтобы остановить бота"
echo "========================================="
echo ""

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✅ Виртуальное окружение активировано"
else
    echo "❌ Виртуальное окружение не найдено"
    exit 1
fi

# Run the minimal bot
echo "🤖 Запускаю бота..."
python3 start_bot_minimal.py