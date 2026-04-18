#!/bin/bash
# Скрипт мониторинга для Customs Calculator Bot

echo "📊 Запуск мониторинга..."
echo "📅 $(date)"
echo ""

# Конфигурация
ALERT_THRESHOLD_CPU=80
ALERT_THRESHOLD_MEM=80
ALERT_THRESHOLD_DISK=85
CHECK_INTERVAL=300  # 5 минут

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

success() { echo -e "${GREEN}✅ $1${NC}"; }
warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
error() { echo -e "${RED}❌ $1${NC}"; }
info() { echo -e "${YELLOW}ℹ️  $1${NC}"; }

# Функция отправки алерта в Telegram
send_alert() {
    local message="$1"
    
    if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
        curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
            -d chat_id="$TELEGRAM_CHAT_ID" \
            -d text="$message" \
            -d parse_mode="Markdown" \
            > /dev/null 2>&1
    fi
}

# Шаг 1: Проверка работы бота
info "Шаг 1: Проверка работы бота..."
if systemctl is-active --quiet customs-bot; then
    BOT_STATUS="активен"
    success "Бот работает"
else
    BOT_STATUS="неактивен"
    error "Бот не работает!"
    
    # Пробуем перезапустить
    info "Пробуем перезапустить бота..."
    systemctl restart customs-bot
    sleep 5
    
    if systemctl is-active --quiet customs-bot; then
        success "Бот перезапущен успешно"
        send_alert "🔄 *Customs Bot перезапущен*
        
Бот был перезапущен после сбоя.
✅ Сейчас работает нормально.
📅 $(date)"
    else
        error "Не удалось перезапустить бота"
        send_alert "🚨 *Customs Bot не работает!*
        
Бот перестал работать и не перезапускается.
❌ Требуется ручное вмешательство.
📅 $(date)
📋 Логи: journalctl -u customs-bot -n 20"
    fi
fi

# Шаг 2: Проверка использования CPU
info "Шаг 2: Проверка использования CPU..."
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1 | cut -d'.' -f1)

if [ "$CPU_USAGE" -gt "$ALERT_THRESHOLD_CPU" ]; then
    warning "Высокая загрузка CPU: ${CPU_USAGE}%"
    send_alert "🔥 *Высокая загрузка CPU: ${CPU_USAGE}%*
    
Сервер под высокой нагрузкой.
📊 CPU: ${CPU_USAGE}%
⏰ $(date)"
else
    success "CPU: ${CPU_USAGE}% (норма)"
fi

# Шаг 3: Проверка использования памяти
info "Шаг 3: Проверка использования памяти..."
MEM_TOTAL=$(free -m | awk '/Mem:/ {print $2}')
MEM_USED=$(free -m | awk '/Mem:/ {print $3}')
MEM_PERCENT=$((MEM_USED * 100 / MEM_TOTAL))

if [ "$MEM_PERCENT" -gt "$ALERT_THRESHOLD_MEM" ]; then
    warning "Высокое использование памяти: ${MEM_PERCENT}%"
    send_alert "💾 *Высокое использование памяти: ${MEM_PERCENT}%*
    
Сервер использует много памяти.
📊 Память: ${MEM_PERCENT}% (${MEM_USED}M/${MEM_TOTAL}M)
⏰ $(date)"
else
    success "Память: ${MEM_PERCENT}% (норма)"
fi

# Шаг 4: Проверка дискового пространства
info "Шаг 4: Проверка дискового пространства..."
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | cut -d'%' -f1)

if [ "$DISK_USAGE" -gt "$ALERT_THRESHOLD_DISK" ]; then
    warning "Мало свободного места на диске: ${DISK_USAGE}%"
    send_alert "💿 *Мало свободного места: ${DISK_USAGE}%*
    
На сервере заканчивается место на диске.
📊 Использовано: ${DISK_USAGE}%
⏰ $(date)"
else
    success "Диск: ${DISK_USAGE}% (норма)"
fi

# Шаг 5: Проверка логов на ошибки
info "Шаг 5: Проверка логов на ошибки..."
LOG_ERRORS=$(journalctl -u customs-bot --since "5 minutes ago" | grep -i "error\|fail\|exception" | head -5)

if [ -n "$LOG_ERRORS" ]; then
    warning "Обнаружены ошибки в логах:"
    echo "$LOG_ERRORS"
    
    # Отправляем только первые 3 ошибки (ограничение Telegram)
    ERROR_SUMMARY=$(echo "$LOG_ERRORS" | head -3)
    send_alert "🐛 *Ошибки в логах Customs Bot*
    
Обнаружены ошибки за последние 5 минут:
\`\`\`
$ERROR_SUMMARY
\`\`\`
⏰ $(date)"
else
    success "В логах ошибок нет"
fi

# Шаг 6: Проверка подключения к интернету
info "Шаг 6: Проверка подключения к интернету..."
if ping -c 1 8.8.8.8 &> /dev/null; then
    success "Интернет подключение есть"
else
    error "Нет подключения к интернету"
    send_alert "🌐 *Нет подключения к интернету*
    
Сервер потерял подключение к интернету.
❌ Бот не может работать без интернета.
⏰ $(date)"
fi

# Шаг 7: Проверка подключения к Telegram API
info "Шаг 7: Проверка подключения к Telegram API..."
if curl -s "https://api.telegram.org" > /dev/null; then
    success "Telegram API доступен"
else
    error "Telegram API недоступен"
    send_alert "📱 *Telegram API недоступен*
    
Сервер не может подключиться к Telegram.
❌ Бот не может отправлять/получать сообщения.
⏰ $(date)"
fi

# Шаг 8: Проверка базы данных
info "Шаг 8: Проверка базы данных..."
if command -v psql &> /dev/null; then
    if sudo -u postgres psql -d customs_bot -c "SELECT 1;" &> /dev/null; then
        success "База данных доступна"
    else
        error "База данных недоступна"
        send_alert "🗄️ *База данных недоступна*
        
Не удалось подключиться к PostgreSQL.
❌ Бот не может работать без базы данных.
⏰ $(date)"
    fi
else
    info "PostgreSQL не установлен, пропускаем проверку"
fi

# Шаг 9: Сбор статистики
info "Шаг 9: Сбор статистики..."
UPTIME=$(uptime -p)
LOAD_AVG=$(uptime | awk -F'load average:' '{print $2}')
ACTIVE_CONNECTIONS=$(ss -tun | wc -l)
BOT_PID=$(systemctl show -p MainPID customs-bot | cut -d= -f2)
BOT_MEM=$(ps -o rss= -p "$BOT_PID" 2>/dev/null | awk '{print $1/1024 " MB"}' || echo "N/A")

# Шаг 10: Отчёт
echo ""
echo "=" * 60
success "📊 Мониторинг завершён"
echo ""
echo "📈 СТАТИСТИКА СЕРВЕРА:"
echo "  Время работы: $UPTIME"
echo "  Нагрузка: $LOAD_AVG"
echo "  Активные соединения: $ACTIVE_CONNECTIONS"
echo ""
echo "🤖 СТАТУС БОТА:"
echo "  Статус: $BOT_STATUS"
echo "  PID: $BOT_PID"
echo "  Память бота: $BOT_MEM"
echo ""
echo "📊 МЕТРИКИ:"
echo "  CPU: ${CPU_USAGE}% (порог: ${ALERT_THRESHOLD_CPU}%)"
echo "  Память: ${MEM_PERCENT}% (порог: ${ALERT_THRESHOLD_MEM}%)"
echo "  Диск: ${DISK_USAGE}% (порог: ${ALERT_THRESHOLD_DISK}%)"
echo ""
echo "🔧 РЕКОМЕНДАЦИИ:"
if [ "$CPU_USAGE" -gt 70 ]; then
    echo "  ⚠️  CPU близок к пределу, рассмотрите оптимизацию"
fi
if [ "$MEM_PERCENT" -gt 70 ]; then
    echo "  ⚠️  Память близка к пределу, проверьте утечки"
fi
if [ "$DISK_USAGE" -gt 80 ]; then
    echo "  ⚠️  Диск почти заполнен, очистите старые логи/бэкапы"
fi
if [ -n "$LOG_ERRORS" ]; then
    echo "  ⚠️  Есть ошибки в логах, проверьте journalctl -u customs-bot"
fi
echo ""
echo "⏰ Следующая проверка через $((CHECK_INTERVAL / 60)) минут"
echo "=" * 60

# Сохраняем отчёт в лог
MONITOR_LOG="/var/log/customs-bot/monitor.log"
mkdir -p "$(dirname "$MONITOR_LOG")"
echo "[$(date)] CPU:${CPU_USAGE}% MEM:${MEM_PERCENT}% DISK:${DISK_USAGE}% BOT:$BOT_STATUS" >> "$MONITOR_LOG"

# Ограничиваем размер лога (последние 1000 записей)
tail -n 1000 "$MONITOR_LOG" > "${MONITOR_LOG}.tmp" && mv "${MONITOR_LOG}.tmp" "$MONITOR_LOG"