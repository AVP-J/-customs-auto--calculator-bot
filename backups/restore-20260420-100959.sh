#!/bin/bash
# Скрипт восстановления из снепшота pre-deploy-20260420-100959

set -e

BACKUP_DIR="/Users/jarvis/.openclaw/workspacesk-proj-d_KYutoeMeow7LUKRKp-D12q_KmmviQ8zyilVKY-wJIsP62VfJpZtx8nmnNZd8ezeGDPXP2Yo5T3BlbkFJXw0rL0LknE0zFpOslS5kdCHg5xhDNz98vp6cnSCXuWN4lhRtSySJctzElD7OpyBAsBuQII4fkA/customs_calculator_project/backups"
TIMESTAMP="20260420-100959"

echo "🔄 Восстанавливаю из снепшота pre-deploy-20260420-100959..."

# Проверяем что файлы существуют
if [ ! -f "$BACKUP_DIR/code-$TIMESTAMP.tar.gz" ]; then
    echo "❌ Файл бэкапа кода не найден"
    exit 1
fi

# Останавливаем бота
echo "⏸️ Останавливаю бота..."
sudo systemctl stop customs-bot 2>/dev/null || true

# Восстанавливаем код
echo "📦 Восстанавливаю код..."
tar -xzf "$BACKUP_DIR/code-$TIMESTAMP.tar.gz" -C /

# Восстанавливаем конфигурацию если есть
if [ -f "$BACKUP_DIR/config-$TIMESTAMP.tar.gz" ]; then
    echo "⚙️ Восстанавливаю конфигурацию..."
    tar -xzf "$BACKUP_DIR/config-$TIMESTAMP.tar.gz" -C /
fi

# Запускаем бота
echo "▶️ Запускаю бота..."
sudo systemctl start customs-bot

echo ""
echo "✅ Восстановление завершено!"
echo "📊 Метаданные: $BACKUP_DIR/metadata-$TIMESTAMP.json"
echo "📝 Git статус: $BACKUP_DIR/git-status-$TIMESTAMP.txt"
echo ""
echo "Проверьте статус бота:"
echo "  sudo systemctl status customs-bot"
