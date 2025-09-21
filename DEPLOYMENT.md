# 🚀 Руководство по развертыванию

## 📋 Обзор

Данное руководство описывает различные способы развертывания Telegram e-commerce бота в продакшене.

## 🏠 Локальное развертывание

### Требования
- Python 3.8+
- pip
- Доступ к интернету

### Шаги развертывания

```bash
# 1. Клонирование проекта
git clone <repository-url>
cd ecommerce-bot

# 2. Установка зависимостей
pip install -r requirements.txt

# 3. Настройка конфигурации
cp config.py.example config.py
# Отредактируйте config.py

# 4. Инициализация базы данных
python init_data.py

# 5. Запуск бота
python main.py
```

## 🐳 Docker развертывание

### Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY . .

# Создание пользователя
RUN useradd -m -u 1000 botuser && chown -R botuser:botuser /app
USER botuser

# Запуск бота
CMD ["python", "main.py"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  bot:
    build: .
    container_name: ecommerce-bot
    restart: unless-stopped
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
      - ADMIN_ID=${ADMIN_ID}
    networks:
      - bot-network

networks:
  bot-network:
    driver: bridge
```

### Запуск с Docker

```bash
# Сборка образа
docker build -t ecommerce-bot .

# Запуск контейнера
docker run -d \
  --name ecommerce-bot \
  -e BOT_TOKEN="your_token" \
  -e ADMIN_ID="your_id" \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  ecommerce-bot

# Или с docker-compose
docker-compose up -d
```

## 🐧 Linux Systemd развертывание

### Создание пользователя

```bash
sudo useradd -m -s /bin/bash botuser
sudo mkdir -p /opt/ecommerce-bot
sudo chown botuser:botuser /opt/ecommerce-bot
```

### Установка приложения

```bash
# Переключение на пользователя бота
sudo su - botuser

# Клонирование и установка
cd /opt/ecommerce-bot
git clone <repository-url> .
pip install -r requirements.txt
python init_data.py
```

### Создание systemd сервиса

```bash
sudo nano /etc/systemd/system/ecommerce-bot.service
```

Содержимое файла:

```ini
[Unit]
Description=E-commerce Telegram Bot
After=network.target

[Service]
Type=simple
User=botuser
Group=botuser
WorkingDirectory=/opt/ecommerce-bot
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Переменные окружения
Environment=BOT_TOKEN=your_bot_token
Environment=ADMIN_ID=your_admin_id

[Install]
WantedBy=multi-user.target
```

### Управление сервисом

```bash
# Включение автозапуска
sudo systemctl enable ecommerce-bot

# Запуск сервиса
sudo systemctl start ecommerce-bot

# Проверка статуса
sudo systemctl status ecommerce-bot

# Просмотр логов
sudo journalctl -u ecommerce-bot -f

# Остановка сервиса
sudo systemctl stop ecommerce-bot
```

## ☁️ Облачное развертывание

### Heroku

#### Procfile
```
worker: python main.py
```

#### runtime.txt
```
python-3.9.18
```

#### requirements.txt
```
aiogram==3.4.1
aiosqlite==0.19.0
pydantic==2.5.3
python-dotenv==1.0.0
```

#### Развертывание
```bash
# Установка Heroku CLI
# Создание приложения
heroku create your-bot-name

# Установка переменных окружения
heroku config:set BOT_TOKEN=your_token
heroku config:set ADMIN_ID=your_id

# Развертывание
git push heroku main

# Запуск воркера
heroku ps:scale worker=1
```

### Railway

#### railway.json
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python main.py",
    "healthcheckPath": "/",
    "healthcheckTimeout": 100
  }
}
```

### DigitalOcean App Platform

#### .do/app.yaml
```yaml
name: ecommerce-bot
services:
- name: bot
  source_dir: /
  github:
    repo: your-username/your-repo
    branch: main
  run_command: python main.py
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: BOT_TOKEN
    value: your_token
  - key: ADMIN_ID
    value: your_id
```

## 🔒 Безопасность

### Переменные окружения

```bash
# Создание .env файла
cat > .env << EOF
BOT_TOKEN=your_bot_token_here
ADMIN_ID=your_telegram_id_here
DATABASE_URL=sqlite:///data/ecommerce_bot.db
LOG_LEVEL=INFO
EOF
```

### Права доступа

```bash
# Установка правильных прав
chmod 600 .env
chmod 755 main.py
chmod 644 config.py
```

### Firewall

```bash
# Настройка UFW (Ubuntu)
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

## 📊 Мониторинг

### Логирование

```python
# Настройка логирования в config.py
LOG_LEVEL = "INFO"
LOG_FILE = "/var/log/ecommerce-bot/bot.log"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

### Мониторинг с Prometheus

```python
# requirements.txt
prometheus-client==0.19.0

# main.py
from prometheus_client import Counter, Histogram, start_http_server

# Метрики
messages_total = Counter('bot_messages_total', 'Total messages processed')
response_time = Histogram('bot_response_time_seconds', 'Response time')

# Запуск метрик сервера
start_http_server(8000)
```

### Health Check

```python
# health_check.py
import asyncio
import aiosqlite
from aiogram import Bot

async def health_check():
    """Проверка здоровья бота"""
    try:
        # Проверка базы данных
        async with aiosqlite.connect("ecommerce_bot.db") as db:
            await db.execute("SELECT 1")
        
        # Проверка бота
        bot = Bot(token=config.BOT_TOKEN)
        await bot.get_me()
        await bot.session.close()
        
        return True
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(health_check())
    exit(0 if result else 1)
```

## 🔄 Обновления

### Автоматические обновления

```bash
#!/bin/bash
# update.sh

cd /opt/ecommerce-bot
git pull origin main
pip install -r requirements.txt
sudo systemctl restart ecommerce-bot
```

### Резервное копирование

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Создание резервной копии БД
cp ecommerce_bot.db "$BACKUP_DIR/ecommerce_bot_$DATE.db"

# Очистка старых бэкапов (старше 30 дней)
find "$BACKUP_DIR" -name "ecommerce_bot_*.db" -mtime +30 -delete
```

## 📈 Масштабирование

### Горизонтальное масштабирование

```yaml
# docker-compose.yml
version: '3.8'

services:
  bot-1:
    build: .
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
      - ADMIN_ID=${ADMIN_ID}
      - INSTANCE_ID=1
    volumes:
      - ./data:/app/data

  bot-2:
    build: .
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
      - ADMIN_ID=${ADMIN_ID}
      - INSTANCE_ID=2
    volumes:
      - ./data:/app/data

  nginx:
    image: nginx
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

### Вертикальное масштабирование

```yaml
# docker-compose.yml
services:
  bot:
    build: .
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 1G
        reservations:
          cpus: '1.0'
          memory: 512M
```

## 🚨 Устранение неполадок

### Общие проблемы

**Бот не отвечает:**
```bash
# Проверка статуса
sudo systemctl status ecommerce-bot

# Просмотр логов
sudo journalctl -u ecommerce-bot -f

# Проверка токена
python -c "import config; print(config.BOT_TOKEN[:10])"
```

**Ошибки базы данных:**
```bash
# Проверка целостности
sqlite3 ecommerce_bot.db "PRAGMA integrity_check;"

# Восстановление из бэкапа
cp backup.db ecommerce_bot.db
```

**Проблемы с памятью:**
```bash
# Мониторинг ресурсов
htop
free -h
df -h
```

### Логи и отладка

```bash
# Просмотр логов в реальном времени
tail -f /var/log/ecommerce-bot/bot.log

# Поиск ошибок
grep ERROR /var/log/ecommerce-bot/bot.log

# Статистика логов
grep "INFO" /var/log/ecommerce-bot/bot.log | wc -l
```

## 📝 Заключение

Выберите подходящий способ развертывания в зависимости от ваших потребностей:

- **Локальное**: Для разработки и тестирования
- **Docker**: Для простого развертывания
- **Systemd**: Для продакшена на Linux
- **Облачное**: Для масштабируемых решений

Не забудьте настроить мониторинг, резервное копирование и безопасность!
