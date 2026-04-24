# 🚀 Настройка автоматического деплоя для тестирования

## **🎯 Цель:**
Автоматически деплоить код из ветки `develop` на VPS сервер для тестирования в реальном Telegram боте.

## **📋 Что нужно сделать:**

### **1. На сервере (VPS):**

#### **1.1. Настроить два конфига:**
```bash
cd /opt/customs-bot

# Продакшен конфиг (для main ветки)
cp .env .env.production
# Отредактируй .env.production - добавь продакшен токен бота

# Тестовый конфиг (для develop ветки)
cp .env.development.example .env.development
# Отредактируй .env.development - добавь тестовый токен бота
```

#### **1.2. Получить тестовый токен бота:**
1. Открой Telegram
2. Найди @BotFather
3. Отправь `/newbot`
4. Имя: "Customs Calculator Dev"
5. Username: "CustomsCalcDevBot"
6. Скопируй токен
7. Добавь в `.env.development`:
```
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ
```

#### **1.3. Дать права на скрипты:**
```bash
chmod +x deploy.sh
chmod +x deployment/test_on_server.sh
```

### **2. На GitHub:**

#### **2.1. Добавить секреты (если ещё не добавлены):**
**Settings → Secrets and variables → Actions → New repository secret**

Нужные секреты:
- `SSH_KEY` — приватный ключ для доступа к серверу
- `SERVER_IP` — IP адрес VPS сервера
- `SERVER_USER` — пользователь на сервере (обычно `root` или `ubuntu`)

#### **2.2. Проверить workflow файл:**
Убедись что `.github/workflows/deploy.yml` содержит:
```yaml
on:
  push:
    branches: [main, develop]  # Деплой из обеих веток
```

### **3. На локальной машине:**

#### **3.1. Работать в ветке `develop`:**
```bash
git checkout develop
git checkout -b feature/новая-фича
# Разрабатываешь новую функцию
git add . && git commit -m "Новая функция"
git push origin feature/новая-фича
```

#### **3.2. Создать Pull Request в `develop`:**
На GitHub создай PR из `feature/новая-фича` в `develop`.

#### **3.3. После мержа в `develop`:**
Автоматически запустится GitHub Actions и задеплоит на сервер.

## **🚀 Как тестировать:**

### **После деплоя из `develop`:**
1. **Открой Telegram**
2. **Найди тестового бота** (по username из `.env.development`)
3. **Отправь `/start`**
4. **Отправь `/calculate`**
5. **Тестируй новую функцию**

### **Быстрая проверка на сервере:**
```bash
ssh user@server_ip
cd /opt/customs-bot
./deployment/test_on_server.sh
```

### **Проверка логов:**
```bash
ssh user@server_ip
sudo journalctl -u customs-bot -f
```

## **📊 Workflow разработки:**

```
Локальная разработка
        ↓
feature/новая-фича ветка
        ↓
Pull Request → develop
        ↓
GitHub Actions (авто-деплой)
        ↓
VPS сервер (тестовый бот)
        ↓
Тестирование в Telegram
        ↓
Если всё OK → Pull Request → main
        ↓
GitHub Actions (продакшен деплой)
        ↓
Продакшен бот
```

## **🐛 Отладка проблем:**

### **Если деплой не запускается:**
1. Проверь что push был в ветку `develop`
2. Проверь GitHub Actions вкладку
3. Проверь секреты на GitHub

### **Если бот не отвечает:**
1. Проверь логи: `sudo journalctl -u customs-bot -f`
2. Проверь токен в `.env.development`
3. Проверь что бот запущен: `sudo systemctl status customs-bot`

### **Если код не обновился:**
1. Проверь что мерж прошёл в `develop`
2. Проверь логи GitHub Actions
3. Запусти деплой вручную: `./deploy.sh` на сервере

## **🎯 Преимущества системы:**

### **✅ Изоляция:**
- **Тестовый бот** для разработки
- **Продакшен бот** для пользователей
- **Разные конфиги** для каждого окружения

### **✅ Автоматизация:**
- **Авто-деплой** при пуше в `develop`
- **Авто-тесты** перед деплоем
- **Уведомления** об успехе/ошибке

### **✅ Безопасность:**
- **Разные токены** для тестов и продакшена
- **GitHub Secrets** для чувствительных данных
- **Ветки защищены** (требуют PR и approval)

## **📱 Быстрые команды:**

### **На сервере:**
```bash
# Проверить статус
sudo systemctl status customs-bot

# Перезапустить
sudo systemctl restart customs-bot

# Посмотреть логи
sudo journalctl -u customs-bot -f

# Запустить тесты
./deployment/test_on_server.sh
```

### **На GitHub:**
- **Actions** → посмотреть статус деплоя
- **Pull Requests** → создать/просмотреть PR
- **Settings → Secrets** → управление секретами

## **🚀 Начинаем тестирование:**

1. **Создай тестового бота** через @BotFather
2. **Обнови `.env.development`** с токеном
3. **Запуш изменения** в `develop`
4. **Проверь GitHub Actions**
5. **Протестируй в Telegram**

**Готово к настройке?**