#!/bin/bash
# Скрипт резервного копирования для Customs Calculator Bot

set -e

echo "💾 Запуск резервного копирования..."
echo "📅 $(date)"
echo ""

# Конфигурация
BACKUP_DIR="/var/backups/customs-bot"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="customs-bot-backup-$TIMESTAMP"
RETENTION_DAYS=30

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

success() { echo -e "${GREEN}✅ $1${NC}"; }
info() { echo -e "${YELLOW}ℹ️  $1${NC}"; }
error() { echo -e "${RED}❌ $1${NC}"; }

# Проверяем директорию для бэкапов
if [ ! -d "$BACKUP_DIR" ]; then
    info "Создаём директорию для бэкапов: $BACKUP_DIR"
    mkdir -p "$BACKUP_DIR"
    chmod 750 "$BACKUP_DIR"
fi

# Шаг 1: Бэкап базы данных
info "Шаг 1: Бэкап базы данных PostgreSQL..."
if command -v pg_dump &> /dev/null; then
    DB_BACKUP_FILE="$BACKUP_DIR/$BACKUP_NAME-db.sql"
    sudo -u postgres pg_dump customs_bot > "$DB_BACKUP_FILE"
    
    if [ -s "$DB_BACKUP_FILE" ]; then
        DB_SIZE=$(du -h "$DB_BACKUP_FILE" | cut -f1)
        success "Бэкап базы данных создан: $DB_SIZE"
    else
        error "Бэкап базы данных пустой"
        exit 1
    fi
else
    info "PostgreSQL не установлен, пропускаем бэкап БД"
fi

# Шаг 2: Бэкап файлов бота
info "Шаг 2: Бэкап файлов бота..."
FILES_BACKUP_FILE="$BACKUP_DIR/$BACKUP_NAME-files.tar.gz"
tar -czf "$FILES_BACKUP_FILE" \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='*.log' \
    --exclude='*.tar.gz' \
    -C /opt/customs-bot .

if [ -s "$FILES_BACKUP_FILE" ]; then
    FILES_SIZE=$(du -h "$FILES_BACKUP_FILE" | cut -f1)
    success "Бэкап файлов создан: $FILES_SIZE"
else
    error "Бэкап файлов пустой"
    exit 1
fi

# Шаг 3: Бэкап логов
info "Шаг 3: Бэкап логов..."
LOGS_BACKUP_FILE="$BACKUP_DIR/$BACKUP_NAME-logs.tar.gz"
if [ -d "/var/log/customs-bot" ]; then
    tar -czf "$LOGS_BACKUP_FILE" -C /var/log customs-bot
    LOGS_SIZE=$(du -h "$LOGS_BACKUP_FILE" | cut -f1)
    success "Бэкап логов создан: $LOGS_SIZE"
else
    info "Директория логов не найдена, пропускаем"
fi

# Шаг 4: Бэкап конфигурации
info "Шаг 4: Бэкап конфигурации..."
CONFIG_BACKUP_FILE="$BACKUP_DIR/$BACKUP_NAME-config.tar.gz"
tar -czf "$CONFIG_BACKUP_FILE" \
    /etc/systemd/system/customs-bot.service \
    /etc/nginx/sites-available/customs-bot \
    /etc/customs-bot 2>/dev/null || true

if [ -s "$CONFIG_BACKUP_FILE" ]; then
    CONFIG_SIZE=$(du -h "$CONFIG_BACKUP_FILE" | cut -f1)
    success "Бэкап конфигурации создан: $CONFIG_SIZE"
else
    info "Конфигурационные файлы не найдены, пропускаем"
fi

# Шаг 5: Создание общего архива
info "Шаг 5: Создание общего архива..."
FULL_BACKUP_FILE="$BACKUP_DIR/$BACKUP_NAME-full.tar.gz"
tar -czf "$FULL_BACKUP_FILE" \
    -C "$BACKUP_DIR" \
    "$BACKUP_NAME-db.sql" \
    "$BACKUP_NAME-files.tar.gz" \
    "$BACKUP_NAME-logs.tar.gz" \
    "$BACKUP_NAME-config.tar.gz" 2>/dev/null || true

if [ -s "$FULL_BACKUP_FILE" ]; then
    FULL_SIZE=$(du -h "$FULL_BACKUP_FILE" | cut -f1)
    success "Полный архив создан: $FULL_SIZE"
    
    # Удаляем промежуточные файлы
    rm -f "$BACKUP_DIR/$BACKUP_NAME-"*.tar.gz "$BACKUP_DIR/$BACKUP_NAME-"*.sql
else
    error "Не удалось создать полный архив"
    # Не удаляем промежуточные файлы если полный архив не создан
fi

# Шаг 6: Очистка старых бэкапов
info "Шаг 6: Очистка старых бэкапов..."
find "$BACKUP_DIR" -name "customs-bot-backup-*" -type f -mtime +$RETENTION_DAYS -delete
OLD_COUNT=$(find "$BACKUP_DIR" -name "customs-bot-backup-*" -type f | wc -l)
success "Удалены бэкапы старше $RETENTION_DAYS дней. Осталось: $OLD_COUNT"

# Шаг 7: Проверка целостности
info "Шаг 7: Проверка целостности архива..."
if [ -f "$FULL_BACKUP_FILE" ]; then
    if tar -tzf "$FULL_BACKUP_FILE" >/dev/null 2>&1; then
        success "Архив целостный"
    else
        error "Архив повреждён"
        exit 1
    fi
fi

# Шаг 8: Отчёт
echo ""
echo "=" * 60
success "🎉 Резервное копирование завершено успешно!"
echo ""
echo "📊 ОТЧЁТ О БЭКАПЕ:"
echo "  Дата: $(date)"
echo "  Архив: $FULL_BACKUP_FILE"
echo "  Размер: $FULL_SIZE"
echo "  Хранится бэкапов: $OLD_COUNT"
echo "  Хранятся: $RETENTION_DAYS дней"
echo ""
echo "📁 СОДЕРЖИМОЕ АРХИВА:"
if [ -f "$FULL_BACKUP_FILE" ]; then
    tar -tzf "$FULL_BACKUP_FILE" | head -10
    FILE_COUNT=$(tar -tzf "$FULL_BACKUP_FILE" | wc -l)
    echo "  Всего файлов: $FILE_COUNT"
fi
echo ""
echo "🔧 КОМАНДЫ ВОССТАНОВЛЕНИЯ:"
echo "  Просмотр архива: tar -tzf $FULL_BACKUP_FILE"
echo "  Извлечь файлы:   tar -xzf $FULL_BACKUP_FILE -C /путь/для/восстановления"
echo "  Восстановить БД: psql customs_bot < backup-db.sql"
echo ""
echo "📈 СТАТИСТИКА ХРАНЕНИЯ:"
du -sh "$BACKUP_DIR"
echo "=" * 60

# Шаг 9: Уведомление (опционально)
if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
    info "Отправляю уведомление в Telegram..."
    MESSAGE="💾 *Бэкап Customs Bot завершён*
    
📅 $(date)
📦 Архив: $FULL_SIZE
📁 Файлов: $FILE_COUNT
🗓️  Хранится: $OLD_COUNT бэкапов
⏳ Срок хранения: $RETENTION_DAYS дней

✅ Бэкап успешно создан и проверен"
    
    curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
        -d chat_id="$TELEGRAM_CHAT_ID" \
        -d text="$MESSAGE" \
        -d parse_mode="Markdown" \
        > /dev/null 2>&1 || info "Не удалось отправить в Telegram"
fi