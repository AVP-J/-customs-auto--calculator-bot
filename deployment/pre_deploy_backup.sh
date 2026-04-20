#!/bin/bash
# Автоматический снепшот перед деплоем

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="/opt/customs-bot"
BACKUP_DIR="/opt/customs-bot/backups"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
TAG="pre-deploy-$TIMESTAMP"

# Если запускаем с локального компьютера, используем текущую директорию
if [ ! -d "$PROJECT_DIR" ]; then
    PROJECT_DIR="$(pwd)"
    BACKUP_DIR="$(pwd)/backups"
fi

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >&2
}

# Создаем директорию для бэкапов если нет
mkdir -p "$BACKUP_DIR"

log_message "🚀 Создаю снепшот перед деплоем ($TAG)..."

# 1. Бэкап кода
log_message "📦 Бэкапирую код..."
CODE_BACKUP="$BACKUP_DIR/code-$TIMESTAMP.tar.gz"
tar -czf "$CODE_BACKUP" -C "$PROJECT_DIR" --exclude="backups" --exclude="*.log" .

# 2. Бэкап конфигурации
log_message "⚙️ Бэкапирую конфигурацию..."
CONFIG_BACKUP="$BACKUP_DIR/config-$TIMESTAMP.tar.gz"
tar -czf "$CONFIG_BACKUP" -C "$PROJECT_DIR" \
    .env \
    config/ \
    deployment/ \
    .github/workflows/ 2>/dev/null || true

# 3. Сохраняем текущий git статус
log_message "🔧 Сохраняю git статус..."
GIT_STATUS_FILE="$BACKUP_DIR/git-status-$TIMESTAMP.txt"
{
    echo "=== Git Status ==="
    git -C "$PROJECT_DIR" status
    echo ""
    echo "=== Git Log (последние 10 коммитов) ==="
    git -C "$PROJECT_DIR" log --oneline -n 10
    echo ""
    echo "=== Git Branch ==="
    git -C "$PROJECT_DIR" branch -a
} > "$GIT_STATUS_FILE"

# 4. Сохраняем системную информацию
log_message "💻 Сохраняю системную информацию..."
SYS_INFO_FILE="$BACKUP_DIR/system-info-$TIMESTAMP.txt"
{
    echo "=== System Info ==="
    echo "Date: $(date)"
    echo "Hostname: $(hostname)"
    echo "User: $(whoami)"
    echo ""
    echo "=== Python Info ==="
    python3 --version
    echo ""
    echo "=== Process Info ==="
    systemctl status customs-bot --no-pager || true
    echo ""
    echo "=== Disk Usage ==="
    df -h
} > "$SYS_INFO_FILE"

# 5. Создаем файл метаданных
log_message "📝 Создаю метаданные..."
META_FILE="$BACKUP_DIR/metadata-$TIMESTAMP.json"
{
    echo "{"
    echo "  \"timestamp\": \"$(date -Iseconds)\","
    echo "  \"tag\": \"$TAG\","
    echo "  \"backups\": {"
    echo "    \"code\": \"$(basename "$CODE_BACKUP")\","
    echo "    \"config\": \"$(basename "$CONFIG_BACKUP")\","
    echo "    \"git_status\": \"$(basename "$GIT_STATUS_FILE")\","
    echo "    \"system_info\": \"$(basename "$SYS_INFO_FILE")\""
    echo "  },"
    echo "  \"git\": {"
    echo "    \"branch\": \"$(git -C "$PROJECT_DIR" branch --show-current)\","
    echo "    \"commit\": \"$(git -C "$PROJECT_DIR" log --oneline -n 1 --pretty=format:'%h')\","
    echo "    \"message\": \"$(git -C "$PROJECT_DIR" log --oneline -n 1 --pretty=format:'%s')\""
    echo "  }"
    echo "}"
} > "$META_FILE"

# 6. Создаем скрипт восстановления
log_message "🔄 Создаю скрипт восстановления..."
RESTORE_SCRIPT="$BACKUP_DIR/restore-$TIMESTAMP.sh"
cat > "$RESTORE_SCRIPT" << EOF
#!/bin/bash
# Скрипт восстановления из снепшота $TAG

set -e

BACKUP_DIR="$BACKUP_DIR"
TIMESTAMP="$TIMESTAMP"

echo "🔄 Восстанавливаю из снепшота $TAG..."

# Проверяем что файлы существуют
if [ ! -f "\$BACKUP_DIR/code-\$TIMESTAMP.tar.gz" ]; then
    echo "❌ Файл бэкапа кода не найден"
    exit 1
fi

# Останавливаем бота
echo "⏸️ Останавливаю бота..."
sudo systemctl stop customs-bot 2>/dev/null || true

# Восстанавливаем код
echo "📦 Восстанавливаю код..."
tar -xzf "\$BACKUP_DIR/code-\$TIMESTAMP.tar.gz" -C /

# Восстанавливаем конфигурацию если есть
if [ -f "\$BACKUP_DIR/config-\$TIMESTAMP.tar.gz" ]; then
    echo "⚙️ Восстанавливаю конфигурацию..."
    tar -xzf "\$BACKUP_DIR/config-\$TIMESTAMP.tar.gz" -C /
fi

# Запускаем бота
echo "▶️ Запускаю бота..."
sudo systemctl start customs-bot

echo ""
echo "✅ Восстановление завершено!"
echo "📊 Метаданные: \$BACKUP_DIR/metadata-\$TIMESTAMP.json"
echo "📝 Git статус: \$BACKUP_DIR/git-status-\$TIMESTAMP.txt"
echo ""
echo "Проверьте статус бота:"
echo "  sudo systemctl status customs-bot"
EOF

chmod +x "$RESTORE_SCRIPT"

# 7. Очищаем старые бэкапы (оставляем последние 10)
log_message "🧹 Очищаю старые бэкапы..."
cd "$BACKUP_DIR"
ls -t code-*.tar.gz 2>/dev/null | tail -n +11 | xargs rm -f 2>/dev/null || true
ls -t config-*.tar.gz 2>/dev/null | tail -n +11 | xargs rm -f 2>/dev/null || true
ls -t git-status-*.txt 2>/dev/null | tail -n +11 | xargs rm -f 2>/dev/null || true
ls -t system-info-*.txt 2>/dev/null | tail -n +11 | xargs rm -f 2>/dev/null || true
ls -t metadata-*.json 2>/dev/null | tail -n +11 | xargs rm -f 2>/dev/null || true
ls -t restore-*.sh 2>/dev/null | tail -n +11 | xargs rm -f 2>/dev/null || true

log_message "✅ Снепшот создан: $TAG"
log_message "📁 Директория: $BACKUP_DIR"
log_message "📦 Файлы:"
ls -lh "$BACKUP_DIR"/*"$TIMESTAMP"* 2>/dev/null | awk '{print "  " $0}'

echo ""
echo "🎯 Снепшот $TAG создан успешно!"
echo "📊 Для восстановления выполните:"
echo "  sudo $RESTORE_SCRIPT"
echo ""
echo "📁 Файлы:"
find "$BACKUP_DIR" -name "*$TIMESTAMP*" -type f | sort