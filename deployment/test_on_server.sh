#!/bin/bash
# Скрипт для тестирования бота на сервере

set -e

echo "🧪 Тестирование бота на сервере..."
echo "📅 $(date)"
echo ""

# Цвета
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

success() { echo -e "${GREEN}✅ $1${NC}"; }
info() { echo -e "${YELLOW}ℹ️  $1${NC}"; }
error() { echo -e "${RED}❌ $1${NC}"; }

# Проверяем что мы в правильной директории
cd /opt/customs-bot || {
    error "Директория /opt/customs-bot не найдена"
    exit 1
}

# Шаг 1: Проверяем конфигурацию
info "Шаг 1: Проверка конфигурации..."
if [ ! -f ".env" ]; then
    error "Файл .env не найден"
    if [ -f ".env.development" ]; then
        info "Используем тестовый конфиг..."
        cp .env.development .env
        success "Создан .env из .env.development"
    else
        error "Нет конфигурационных файлов"
        exit 1
    fi
fi

# Проверяем токен
if grep -q "YOUR_BOT_TOKEN_HERE" .env; then
    error "Токен бота не настроен в .env"
    info "Отредактируйте .env и добавьте TELEGRAM_BOT_TOKEN"
    exit 1
fi
success "Конфигурация проверена"

# Шаг 2: Активируем окружение
info "Шаг 2: Активация Python окружения..."
if [ ! -d "venv" ]; then
    error "Виртуальное окружение не найдено"
    info "Создаём venv..."
    python3 -m venv venv
fi

source venv/bin/activate
success "Окружение активировано"

# Шаг 3: Проверяем зависимости
info "Шаг 3: Проверка зависимостей..."
pip install -q -r requirements.txt
success "Зависимости проверены"

# Шаг 4: Запускаем тесты
info "Шаг 4: Запуск тестов..."
if [ -f "test_full_workflow.py" ]; then
    python3 test_full_workflow.py
    success "Тесты workflow пройдены"
else
    info "Файл test_full_workflow.py не найден"
fi

if [ -f "test_step_by_step.py" ]; then
    python3 test_step_by_step.py
    success "Тесты step-by-step пройдены"
else
    info "Файл test_step_by_step.py не найден"
fi

# Шаг 5: Проверяем импорт модулей
info "Шаг 5: Проверка импорта модулей..."
if python3 -c "
import sys
sys.path.insert(0, '.')
from src.bot.states import UserState, SessionManager
from src.bot.keyboards import get_keyboard_for_state
from src.bot.messages import get_message_for_state
print('✅ Все модули импортируются успешно')
"; then
    success "Модули импортируются"
else
    error "Ошибка импорта модулей"
    exit 1
fi

# Шаг 6: Проверяем что бот может запуститься
info "Шаг 6: Проверка запуска бота..."
if python3 -c "
import sys
sys.path.insert(0, '.')
from src.bot.main import main
print('✅ Функция main() найдена')
"; then
    success "Бот может быть запущен"
else
    error "Ошибка при проверке main()"
    exit 1
fi

# Шаг 7: Проверяем сервис
info "Шаг 7: Проверка сервиса бота..."
if systemctl list-unit-files | grep -q customs-bot; then
    sudo systemctl status customs-bot --no-pager | head -20
    success "Сервис customs-bot найден"
else
    info "Сервис customs-bot не настроен"
    info "Для настройки выполните:"
    info "  sudo cp deployment/customs-bot.service /etc/systemd/system/"
    info "  sudo systemctl daemon-reload"
    info "  sudo systemctl enable customs-bot"
    info "  sudo systemctl start customs-bot"
fi

# Шаг 8: Финальный отчёт
echo ""
echo "=" * 60
success "🧪 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!"
echo ""
echo "📊 Результаты:"
echo "  ✅ Конфигурация: OK"
echo "  ✅ Зависимости: OK"
echo "  ✅ Модули: OK"
echo "  ✅ Запуск: OK"
echo ""
echo "🚀 Что делать дальше:"
echo ""
echo "1. Если сервис не запущен:"
echo "   sudo systemctl start customs-bot"
echo ""
echo "2. Проверить логи:"
echo "   sudo journalctl -u customs-bot -f"
echo ""
echo "3. Протестировать в Telegram:"
echo "   - Открой бота"
echo "   - Отправь /start"
echo "   - Отправь /calculate"
echo "   - Пройди все шаги"
echo ""
echo "4. Если есть ошибки:"
echo "   - Проверь .env файл (TELEGRAM_BOT_TOKEN)"
echo "   - Проверь логи: sudo journalctl -u customs-bot -f"
echo "   - Перезапусти: sudo systemctl restart customs-bot"
echo ""
echo "=" * 60

# Шаг 9: Запускаем бота в фоне для быстрого теста (опционально)
read -p "Запустить бота для тестирования? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    info "Запускаем бота в тестовом режиме..."
    echo "Нажми Ctrl+C чтобы остановить"
    echo ""
    python3 -m src.bot.main
fi