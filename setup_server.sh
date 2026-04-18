#!/bin/bash
# Скрипт настройки сервера для Customs Calculator Bot

set -e

echo "🛠️  Настройка сервера для Customs Calculator Bot..."
echo "📅 $(date)"
echo ""

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
    error "Запустите скрипт с sudo: sudo ./setup_server.sh"
    exit 1
fi

# Шаг 1: Обновление системы
info "Шаг 1: Обновление системы..."
apt-get update
apt-get upgrade -y
success "Система обновлена"

# Шаг 2: Установка базовых пакетов
info "Шаг 2: Установка базовых пакетов..."
apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget \
    htop \
    nginx \
    postgresql \
    postgresql-contrib \
    supervisor \
    ufw \
    fail2ban \
    certbot \
    python3-certbot-nginx
success "Базовые пакеты установлены"

# Шаг 3: Настройка firewall
info "Шаг 3: Настройка firewall..."
ufw allow ssh
ufw allow http
ufw allow https
ufw --force enable
success "Firewall настроен"

# Шаг 4: Создание пользователя для бота
info "Шаг 4: Создание пользователя для бота..."
if ! id "customsbot" &>/dev/null; then
    useradd -m -s /bin/bash customsbot
    usermod -aG sudo customsbot
    success "Пользователь customsbot создан"
else
    info "Пользователь customsbot уже существует"
fi

# Шаг 5: Настройка PostgreSQL
info "Шаг 5: Настройка PostgreSQL..."
sudo -u postgres psql -c "CREATE DATABASE customs_bot;"
sudo -u postgres psql -c "CREATE USER customs_user WITH PASSWORD 'strong_password_here';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE customs_bot TO customs_user;"
sudo -u postgres psql -c "ALTER USER customs_user WITH SUPERUSER;"
success "PostgreSQL настроен"

# Шаг 6: Создание директорий
info "Шаг 6: Создание директорий..."
mkdir -p /opt/customs-bot
mkdir -p /var/log/customs-bot
mkdir -p /etc/customs-bot

chown -R customsbot:customsbot /opt/customs-bot
chown -R customsbot:customsbot /var/log/customs-bot
chmod 755 /opt/customs-bot
success "Директории созданы"

# Шаг 7: Клонирование репозитория
info "Шаг 7: Клонирование репозитория..."
cd /opt/customs-bot
if [ ! -d ".git" ]; then
    sudo -u customsbot git clone https://github.com/AVP-J/-customs-auto--calculator-bot.git .
else
    info "Репозиторий уже клонирован"
fi
success "Репозиторий готов"

# Шаг 8: Настройка виртуального окружения
info "Шаг 8: Настройка виртуального окружения..."
sudo -u customsbot python3 -m venv venv
sudo -u customsbot /opt/customs-bot/venv/bin/pip install --upgrade pip
sudo -u customsbot /opt/customs-bot/venv/bin/pip install -r requirements.txt
success "Виртуальное окружение настроено"

# Шаг 9: Настройка systemd службы
info "Шаг 9: Настройка systemd службы..."
cat > /etc/systemd/system/customs-bot.service << EOF
[Unit]
Description=Customs Calculator Telegram Bot
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=simple
User=customsbot
Group=customsbot
WorkingDirectory=/opt/customs-bot
Environment="PATH=/opt/customs-bot/venv/bin"
ExecStart=/opt/customs-bot/venv/bin/python /opt/customs-bot/bot_simple.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=customs-bot

# Защита
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=/opt/customs-bot /var/log/customs-bot

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable customs-bot
success "Systemd служба настроена"

# Шаг 10: Настройка nginx (для вебхука)
info "Шаг 10: Настройка nginx..."
cat > /etc/nginx/sites-available/customs-bot << EOF
server {
    listen 80;
    server_name ваш-домен.kz;
    
    location / {
        return 301 https://\$server_name\$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name ваш-домен.kz;
    
    ssl_certificate /etc/letsencrypt/live/ваш-домен.kz/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ваш-домен.kz/privkey.pem;
    
    # Настройки SSL
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF

ln -sf /etc/nginx/sites-available/customs-bot /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
success "Nginx настроен"

# Шаг 11: Настройка SSL (нужен домен)
info "Шаг 11: Настройка SSL..."
echo "Для настройки SSL выполните:"
echo "  certbot --nginx -d ваш-домен.kz"
echo ""
echo "Или если нет домена, пропустите этот шаг"

# Шаг 12: Настройка бэкапов
info "Шаг 12: Настройка бэкапов..."
cat > /etc/cron.d/customs-bot-backup << EOF
# Ежедневный бэкап в 3:00
0 3 * * * customsbot /opt/customs-bot/backup.sh >> /var/log/customs-bot/backup.log 2>&1
EOF

# Шаг 13: Настройка мониторинга
info "Шаг 13: Настройка мониторинга..."
cat > /etc/cron.d/customs-bot-monitor << EOF
# Проверка каждые 5 минут
*/5 * * * * root /opt/customs-bot/monitor.sh >> /var/log/customs-bot/monitor.log 2>&1
EOF

# Шаг 14: Финальная настройка прав
info "Шаг 14: Финальная настройка прав..."
chown -R customsbot:customsbot /opt/customs-bot
chmod -R 750 /opt/customs-bot
chmod 755 /opt/customs-bot/*.sh
success "Права настроены"

# Шаг 15: Запуск бота
info "Шаг 15: Запуск бота..."
systemctl start customs-bot
sleep 3

if systemctl is-active --quiet customs-bot; then
    success "Бот запущен и работает!"
else
    error "Бот не запустился, проверьте логи:"
    journalctl -u customs-bot -n 20 --no-pager
    exit 1
fi

# Финальный отчёт
echo ""
echo "=" * 60
success "🎉 Сервер настроен успешно!"
echo ""
echo "📊 ИНФОРМАЦИЯ О СЕРВЕРЕ:"
echo "  IP адрес: $(curl -s ifconfig.me)"
echo "  Пользователь бота: customsbot"
echo "  Директория бота: /opt/customs-bot"
echo "  База данных: customs_bot"
echo "  Служба: customs-bot"
echo ""
echo "🔧 КОМАНДЫ ДЛЯ УПРАВЛЕНИЯ:"
echo "  Статус бота:    systemctl status customs-bot"
echo "  Логи бота:      journalctl -u customs-bot -f"
echo "  Перезапустить:  systemctl restart customs-bot"
echo "  Остановить:     systemctl stop customs-bot"
echo ""
echo "📁 ФАЙЛЫ КОНФИГУРАЦИИ:"
echo "  Конфиг бота:    /opt/customs-bot/.env"
echo "  Systemd служба: /etc/systemd/system/customs-bot.service"
echo "  Nginx конфиг:   /etc/nginx/sites-available/customs-bot"
echo ""
echo "🚀 ДАЛЬНЕЙШИЕ ШАГИ:"
echo "  1. Отредактируйте /opt/customs-bot/.env (добавьте TELEGRAM_BOT_TOKEN)"
echo "  2. Настройте домен и SSL: certbot --nginx -d ваш-домен.kz"
echo "  3. Настройте вебхук Telegram для бота"
echo "  4. Протестируйте бота в Telegram"
echo ""
echo "📞 ЛОГИ И МОНИТОРИНГ:"
echo "  Основные логи:  /var/log/customs-bot/"
echo "  Systemd логи:   journalctl -u customs-bot"
echo "  Nginx логи:     /var/log/nginx/"
echo "=" * 60