#!/bin/bash
# restart_bot.sh — убить все старые процессы, закрыть Telegram сессии, запустить бота
set -e

BOT_DIR="/opt/customs-bot"
TOKEN="8706518864:AAEA1ChSbAG3bxYTIH10OTxR4Olsl_WtsIA"
LOCKFILE="/tmp/customs_bot_restart.lock"

# Блокировка чтобы не запустить параллельные перезапуски
exec 200>"$LOCKFILE"
flock -n 200 || { echo "Already restarting"; exit 1; }

echo "[$(date)] Начинаю перезапуск бота..."

# 1. Убить все старые python процессы бота
OLD_PIDS=$(pgrep -f "python3.*run_bot" || true)
if [ -n "$OLD_PIDS" ]; then
    echo "Убиваю старые PID: $OLD_PIDS"
    kill -9 $OLD_PIDS 2>/dev/null || true
    sleep 2
fi

# 2. Закрыть Telegram сессию (снимает конфликт getUpdates)
echo "Закрываю Telegram сессию..."
for i in 1 2 3; do
    RESULT=$(curl -s -m 5 "https://api.telegram.org/bot${TOKEN}/close" 2>/dev/null)
    if echo "$RESULT" | grep -q '"ok":true'; then
        echo "Telegram сессия закрыта"
        break
    else
        echo "Попытка $i: $RESULT"
        sleep 3
    fi
done

# 3. Удалить вебхук на всякий случай
curl -s -m 5 "https://api.telegram.org/bot${TOKEN}/deleteWebhook" > /dev/null
sleep 2

# 4. Запустить бота
cd "$BOT_DIR"
nohup python3 -u run_bot.py > bot.log 2>&1 &
BOT_PID=$!
echo "Бот запущен, PID: $BOT_PID"

# 5. Подождать и проверить
sleep 10
if grep -q "Application started" bot.log; then
    echo "✅ Бот работает!"
elif grep -q "Conflict" bot.log; then
    echo "❌ Всё ещё Conflict. Экстренный рестарт..."
    # Экстренный вариант: ждать дольше
    kill -9 $BOT_PID 2>/dev/null
    sleep 5
    curl -s -m 5 "https://api.telegram.org/bot${TOKEN}/close" > /dev/null
    sleep 15
    nohup python3 -u run_bot.py > bot.log 2>&1 &
    sleep 10
    if grep -q "Application started" bot.log; then
        echo "✅ Бот работает (с повторной попытки)"
    else
        echo "❌ Не удалось запустить бота"
        tail -5 bot.log
    fi
else
    echo "⚠️ Статус неизвестен:"
    tail -5 bot.log
fi
