#!/bin/bash
# Скрипт восстановления из бэкапа для Customs Calculator Bot

set -e

echo "🔄 Запуск восстановления из бэкапа..."
echo "📅 $(date)"
echo ""

# Конфигурация
BACKUP_DIR="/var/backups/customs-bot"
RESTORE_DIR="/tmp/customs-bot-restore"

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

success() { echo -e "${GREEN}✅ $1${NC}"; }
info() { echo -e "${YELLOW}ℹ️  $1${NC}"; }
error() { echo -e "${RED}❌ $1${NC}"; }

# Проверяем что мы root
if [ "$EUID" -ne 0 ]; then
    error "Запустите скрипт с sudo: sudo ./restore.sh"
    exit 1
fi

# Шаг 1: Выбор бэкапа для восстановления
info "Шаг 1: Поиск доступных бэкапов..."
if [ ! -d "$BACKUP_DIR" ]; then
    error "Директория бэкапов не найдена: $BACKUP_DIR"
    exit 1
fi

BACKUP_FILES=($(ls -1t "$BACKUP_DIR"/customs-bot-backup-*.tar.gz 2>/dev/null))

if [ ${#BACKUP_FILES[@]} -eq 0 ]; then
    error "Бэкапы не найдены в $BACKUP_DIR"
    exit 1
fi

echo "📁 Доступные бэкапы:"
for i in "${!BACKUP_FILES[@]}"; do
    BACKUP_FILE="${BACKUP_FILES[$i]}"
    BACKUP_NAME=$(basename "$BACKUP_FILE")
    BACKUP_DATE=$(echo "$BACKUP_NAME" | grep -o '[0-9]\{8\}_[0-9]\{6\}')
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    
    if [ -n "$BACKUP_DATE" ]; then
        DATE_FORMATTED="${BACKUP_DATE:0:4}-${BACKUP_DATE:4:2}-${BACKUP_DATE:6:2} ${BACKUP_DATE:9:2}:${BACKUP_DATE:11:2}:${BACKUP_DATE:13:2}"
        echo "  $((i+1)). $DATE_FORMATTED ($BACKUP_SIZE)"
    else
        echo "  $((i+1)). $BACKUP_NAME ($BACKUP_SIZE)"
    fi
done

# Запрос выбора бэкапа
echo ""
read -p "Выберите номер бэкапа для восстановления (1-${#BACKUP_FILES[@]}): " BACKUP_CHOICE

if ! [[ "$BACKUP_CHOICE" =~ ^[0-9]+$ ]] || [ "$BACKUP_CHOICE" -lt 1 ] || [ "$BACKUP_CHOICE" -gt ${#BACKUP_FILES[@]} ]; then
    error "Неверный выбор"
    exit 1
fi

SELECTED_BACKUP="${BACKUP_FILES[$((BACKUP_CHOICE-1))]}"
SELECTED_BACKUP_NAME=$(basename "$SELECTED_BACKUP")

info "Выбран бэкап: $SELECTED_BACKUP_NAME"

# Шаг 2: Подтверждение
echo ""
warning "⚠️  ВНИМАНИЕ: Восстановление перезапишет текущие данные!"
echo "   - Остановит работающий бот"
echo "   - Восстановит файлы из бэкапа"
echo "   - Восстановит базу данных"
echo ""
read -p "Продолжить восстановление? (y/N): " CONFIRM

if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
    info "Восстановление отменено"
    exit 0
fi

# Шаг 3: Остановка бота
info "Шаг 3: Остановка бота..."
systemctl stop customs-bot 2>/dev/null || true
success "Бот остановлен"

# Шаг 4: Создание временной директории
info "Шаг 4: Подготовка временной директории..."
rm -rf "$RESTORE_DIR"
mkdir -p "$RESTORE_DIR"
success "Временная директория создана: $RESTORE_DIR"

# Шаг 5: Распаковка бэкапа
info "Шаг 5: Распаковка бэкапа..."
tar -xzf "$SELECTED_BACKUP" -C "$RESTORE_DIR"
success "Бэкап распакован"

# Шаг 6: Проверка содержимого
info "Шаг 6: Проверка содержимого бэкапа..."
BACKUP_CONTENT=$(ls -la "$RESTORE_DIR/")
echo "Содержимое бэкапа:"
echo "$BACKUP_CONTENT"

# Шаг 7: Восстановление файлов бота
info "Шаг 7: Восстановление файлов бота..."
if [ -f "$RESTORE_DIR/"*"-files.tar.gz" ]; then
    FILES_BACKUP=$(ls "$RESTORE_DIR/"*"-files.tar.gz")
    
    # Создаём бэкап текущих файлов
    info "Создаём бэкап текущих файлов..."
    CURRENT_BACKUP="/tmp/customs-bot-current-$(date +%Y%m%d_%H%M%S).tar.gz"
    tar -czf "$CURRENT_BACKUP" -C /opt/customs-bot . --exclude='venv' --exclude='__pycache__'
    success "Текущие файлы сохранены в: $CURRENT_BACKUP"
    
    # Очищаем текущую директорию
    info "Очищаем текущую директорию бота..."
    rm -rf /opt/customs-bot/*
    
    # Восстанавливаем файлы из бэкапа
    info "Восстанавливаем файлы из бэкапа..."
    tar -xzf "$FILES_BACKUP" -C /opt/customs-bot
    success "Файлы бота восстановлены"
else
    warning "Файлы бота не найдены в бэкапе, пропускаем"
fi

# Шаг 8: Восстановление базы данных
info "Шаг 8: Восстановление базы данных..."
if [ -f "$RESTORE_DIR/"*"-db.sql" ]; then
    DB_BACKUP=$(ls "$RESTORE_DIR/"*"-db.sql")
    
    # Создаём бэкап текущей базы
    info "Создаём бэкап текущей базы данных..."
    CURRENT_DB_BACKUP="/tmp/customs-bot-db-current-$(date +%Y%m%d_%H%M%S).sql"
    sudo -u postgres pg_dump customs_bot > "$CURRENT_DB_BACKUP"
    success "Текущая база данных сохранена в: $CURRENT_DB_BACKUP"
    
    # Восстанавливаем базу данных
    info "Восстанавливаем базу данных..."
    sudo -u postgres psql -d customs_bot -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
    sudo -u postgres psql customs_bot < "$DB_BACKUP"
    success "База данных восстановлена"
else
    warning "Бэкап базы данных не найден, пропускаем"
fi

# Шаг 9: Восстановление конфигурации
info "Шаг 9: Восстановление конфигурации..."
if [ -f "$RESTORE_DIR/"*"-config.tar.gz" ]; then
    CONFIG_BACKUP=$(ls "$RESTORE_DIR/"*"-config.tar.gz")
    
    # Создаём бэкап текущей конфигурации
    info "Создаём бэкап текущей конфигурации..."
    tar -czf "/tmp/customs-bot-config-current-$(date +%Y%m%d_%H%M%S).tar.gz" \
        /etc/systemd/system/customs-bot.service \
        /etc/nginx/sites-available/customs-bot \
        /etc/customs-bot 2>/dev/null || true
    
    # Восстанавливаем конфигурацию
    info "Восстанавливаем конфигурацию..."
    tar -xzf "$CONFIG_BACKUP" -C /
    systemctl daemon-reload
    success "Конфигурация восстановлена"
else
    warning "Бэкап конфигурации не найден, пропускаем"
fi

# Шаг 10: Настройка прав
info "Шаг 10: Настройка прав..."
chown -R customsbot:customsbot /opt/customs-bot
chmod -R 750 /opt/customs-bot
chmod 755 /opt/customs-bot/*.sh
success "Права настроены"

# Шаг 11: Запуск бота
info "Шаг 11: Запуск бота..."
systemctl start customs-bot
sleep 5

if systemctl is-active --quiet customs-bot; then
    success "Бот запущен успешно"
else
    error "Не удалось запустить бота"
    info "Проверьте логи: journalctl -u customs-bot -n 20"
    exit 1
fi

# Шаг 12: Очистка временных файлов
info "Шаг 12: Очистка временных файлов..."
rm -rf "$RESTORE_DIR"
success "Временные файлы удалены"

# Шаг 13: Отчёт
echo ""
echo "=" * 60
success "🎉 Восстановление завершено успешно!"
echo ""
echo "📊 ОТЧЁТ О ВОССТАНОВЛЕНИИ:"
echo "  Бэкап: $SELECTED_BACKUP_NAME"
echo "  Дата восстановления: $(date)"
echo "  Статус бота: запущен"
echo ""
echo "📁 СОХРАНЕННЫЕ БЭКАПЫ (на случай отката):"
echo "  Файлы бота: $CURRENT_BACKUP"
if [ -f "$CURRENT_DB_BACKUP" ]; then
    echo "  База данных: $CURRENT_DB_BACKUP"
fi
echo ""
echo "🔧 ПРОВЕРЬТЕ:"
echo "  1. Работу бота в Telegram"
echo "  2. Логи: journalctl -u customs-bot -f"
echo "  3. Состояние базы данных"
echo ""
echo "🔄 ЕСЛИ ЧТО-ТО ПОШЛО НЕ ТАК:"
echo "  1. Остановите бота: systemctl stop customs-bot"
echo "  2. Восстановите из сохранённого бэкапа"
echo "  3. Запустите бота: systemctl start customs-bot"
echo "=" * 60

# Шаг 14: Уведомление
if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
    info "Отправляю уведомление в Telegram..."
    MESSAGE="🔄 *Customs Bot восстановлен из бэкапа*
    
✅ Восстановление завершено успешно!
📅 Бэкап: $SELECTED_BACKUP_NAME
⏰ Время: $(date)
🤖 Статус: бот запущен

📁 Сохранённые бэкапы (на случай отката):
- $CURRENT_BACKUP"
    
    if [ -f "$CURRENT_DB_BACKUP" ]; then
        MESSAGE="$MESSAGE
- $CURRENT_DB_BACKUP"
    fi
    
    curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
        -d chat_id="$TELEGRAM_CHAT_ID" \
        -d text="$MESSAGE" \
        -d parse_mode="Markdown" \
        > /dev/null 2>&1 || info "Не удалось отправить в Telegram"
fi