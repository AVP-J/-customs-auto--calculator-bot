#!/bin/bash
# Скрипт деплоя для Customs Calculator Bot

set -e  # Выход при ошибке

echo "🚀 Начинаем деплой Customs Calculator Bot..."
echo "📅 $(date)"
echo ""

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функции для цветного вывода
success() { echo -e "${GREEN}✅ $1${NC}"; }
info() { echo -e "${YELLOW}ℹ️  $1${NC}"; }
error() { echo -e "${RED}❌ $1${NC}"; }

# Проверяем что мы в правильной директории
if [ ! -f "bot_simple.py" ]; then
    error "Файл bot_simple.py не найден. Запустите из директории проекта."
    exit 1
fi

# Шаг 1: Получаем последние изменения
info "Шаг 1: Получаем последние изменения из GitHub..."
if [ -d ".git" ]; then
    git pull origin main
    success "Изменения получены"
else
    info "Git репозиторий не найден, пропускаем..."
fi

# Шаг 2: Активируем виртуальное окружение
info "Шаг 2: Настраиваем Python окружение..."
if [ ! -d "venv" ]; then
    info "Виртуальное окружение не найдено, создаём..."
    python3 -m venv venv
    success "Виртуальное окружение создано"
fi

source venv/bin/activate
success "Виртуальное окружение активировано"

# Шаг 3: Устанавливаем/обновляем зависимости
info "Шаг 3: Устанавливаем зависимости..."
pip install --upgrade pip
pip install -r requirements.txt
success "Зависимости установлены"

# Шаг 4: Проверяем переменные окружения
info "Шаг 4: Проверяем конфигурацию..."

# Определяем окружение по имени бота
if grep -q "DEVELOPMENT" .env 2>/dev/null || [ -f ".env.development" ]; then
    ENVIRONMENT="development"
    BOT_NAME="Customs Calculator Dev Bot"
    info "Окружение: РАЗРАБОТКА ($ENVIRONMENT)"
else
    ENVIRONMENT="production"
    BOT_NAME="Customs Calculator Bot"
    info "Окружение: ПРОДАКШЕН ($ENVIRONMENT)"
fi

if [ ! -f ".env" ]; then
    # Пробуем найти конфиг для окружения
    if [ -f ".env.$ENVIRONMENT" ]; then
        info "Используем конфиг для окружения $ENVIRONMENT"
        cp ".env.$ENVIRONMENT" .env
        success "Файл .env создан из .env.$ENVIRONMENT"
    elif [ -f ".env.example" ]; then
        error "Файл .env не найден"
        info "Создайте .env на основе .env.example:"
        info "  cp .env.example .env"
        info "  # Отредактируйте .env, добавьте TELEGRAM_BOT_TOKEN"
        exit 1
    else
        error "Нет .env или .env.example файлов"
        exit 1
    fi
else
    success "Файл .env найден (окружение: $ENVIRONMENT)"
fi

# Проверяем токен бота
if ! grep -q "TELEGRAM_BOT_TOKEN" .env || grep -q "YOUR_BOT_TOKEN_HERE" .env; then
    error "Токен бота не настроен в .env"
    info "Добавьте TELEGRAM_BOT_TOKEN в .env файл"
    exit 1
else
    success "Токен бота настроен"
fi

# Шаг 5: Проверяем что бот может запуститься
info "Шаг 5: Проверяем бота..."
if python3 -c "import bot_simple; print('✅ Модуль bot_simple импортирован успешно')"; then
    success "Бот проходит базовые проверки"
else
    error "Ошибка при импорте бота"
    exit 1
fi

# Шаг 6: Перезапускаем службу (если настроена)
info "Шаг 6: Перезапускаем службу бота..."
if systemctl list-unit-files | grep -q customs-bot; then
    sudo systemctl restart customs-bot
    success "Служба customs-bot перезапущена"
    
    # Ждём немного и проверяем статус
    sleep 2
    if systemctl is-active --quiet customs-bot; then
        success "Служба customs-bot работает"
    else
        error "Служба customs-bot не запустилась"
        sudo systemctl status customs-bot
        exit 1
    fi
else
    info "Служба customs-bot не настроена"
    info "Для настройки службы выполните:"
    info "  sudo cp deployment/customs-bot.service /etc/systemd/system/"
    info "  sudo systemctl daemon-reload"
    info "  sudo systemctl enable customs-bot"
    info "  sudo systemctl start customs-bot"
fi

# Шаг 7: Проверяем логи
info "Шаг 7: Проверяем логи..."
if systemctl list-unit-files | grep -q customs-bot; then
    echo "Последние 10 строк логов:"
    sudo journalctl -u customs-bot -n 10 --no-pager
fi

# Шаг 8: Финальный отчёт
echo ""
echo "=" * 60
success "🎉 Деплой успешно завершён!"
echo ""
echo "📊 Информация о системе:"
echo "  Окружение: $ENVIRONMENT"
echo "  Бот: $BOT_NAME"
echo "  Python: $(python --version 2>&1)"
echo "  Директория: $(pwd)"
echo "  Время: $(date)"
echo ""

if [ "$ENVIRONMENT" = "development" ]; then
    echo "🧪 ТЕСТОВЫЙ РЕЖИМ:"
    echo "  • DEBUG=True (подробные логи)"
    echo "  • Mock данные для платежей"
    echo "  • Тестовый бот (не продакшен)"
    echo ""
    echo "🚀 Тестовый бот должен быть доступен в Telegram"
    echo "  (используй токен из .env.development)"
else
    echo "🚀 ПРОДАКШЕН РЕЖИМ:"
    echo "  • DEBUG=False (минимальные логи)"
    echo "  • Реальные платежи (если настроены)"
    echo "  • Продакшен бот"
    echo ""
    echo "🚀 Бот должен быть доступен в Telegram:"
    echo "  https://t.me/CustomsCalcKZBot"
fi

echo ""
echo "📝 Команды для управления:"
echo "  Статус бота: sudo systemctl status customs-bot"
echo "  Логи бота:  sudo journalctl -u customs-bot -f"
echo "  Остановить:  sudo systemctl stop customs-bot"
echo "  Запустить:   sudo systemctl start customs-bot"
echo ""
echo "🐛 Если есть проблемы, проверьте:"
echo "  1. Файл .env (TELEGRAM_BOT_TOKEN)"
echo "  2. Логи: sudo journalctl -u customs-bot -f"
echo "  3. Подключение к интернету"
echo "=" * 60