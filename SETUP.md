# Инструкция по настройке и запуску

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Настройка конфигурации

Отредактируйте файл `config.py`:

```python
# Замените на токен вашего бота
BOT_TOKEN = "8428797317:AAF0cDe_77AIN5XPAHgKZ2ApruT_waWuV4A"

# Замените на ваш Telegram ID
ADMIN_ID = 123456789  # Узнать ID можно у @userinfobot
```

### 3. Инициализация базы данных

```bash
python init_data.py
```

### 4. Запуск бота

```bash
python main.py
```

## 📋 Подробная настройка

### Получение токена бота

1. Найдите @BotFather в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Скопируйте полученный токен в `config.py`

### Получение вашего Telegram ID

1. Найдите @userinfobot в Telegram
2. Отправьте любое сообщение
3. Скопируйте ваш ID в `config.py`

### Структура проекта

```
ecommerce-bot/
├── main.py              # Главный файл
├── config.py           # Конфигурация
├── init_data.py        # Инициализация данных
├── requirements.txt    # Зависимости
├── database/           # База данных
│   ├── models.py
│   └── repository.py
├── handlers/           # Обработчики
│   ├── catalog.py
│   ├── cart.py
│   ├── order.py
│   └── admin.py
├── tests/              # Тесты
└── docs/               # Документация
```

## 🗄️ Настройка базы данных

### Автоматическая инициализация

```bash
python init_data.py
```

Этот скрипт:
- Создает базу данных SQLite
- Создает все необходимые таблицы
- Добавляет тестовые категории и товары

### Ручная инициализация

Если нужно создать базу данных вручную:

```python
from database.repository import DatabaseRepository

async def init_db():
    db = DatabaseRepository()
    await db.init_db()

# Запуск
import asyncio
asyncio.run(init_db())
```

## 🧪 Запуск тестов

```bash
# Все тесты
pytest

# С подробным выводом
pytest -v

# Конкретный тест
pytest tests/test_cart.py -v

# С покрытием
pytest --cov=database tests/
```

## 🔧 Настройка для продакшна

### Переменные окружения

Создайте файл `.env`:

```env
BOT_TOKEN=your_bot_token_here
ADMIN_ID=your_telegram_id_here
DATABASE_URL=sqlite:///ecommerce_bot.db
LOG_LEVEL=INFO
```

### Systemd сервис (Linux)

Создайте файл `/etc/systemd/system/ecommerce-bot.service`:

```ini
[Unit]
Description=E-commerce Telegram Bot
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/ecommerce-bot
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Запуск сервиса:

```bash
sudo systemctl enable ecommerce-bot
sudo systemctl start ecommerce-bot
sudo systemctl status ecommerce-bot
```

### Docker

Создайте `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

Создайте `docker-compose.yml`:

```yaml
version: '3.8'

services:
  bot:
    build: .
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
      - ADMIN_ID=${ADMIN_ID}
    restart: unless-stopped
```

Запуск:

```bash
docker-compose up -d
```

## 📊 Мониторинг

### Логи

Логи сохраняются в файл `bot.log`:

```bash
# Просмотр логов в реальном времени
tail -f bot.log

# Поиск ошибок
grep ERROR bot.log

# Статистика
grep "INFO" bot.log | wc -l
```

### База данных

```bash
# Размер базы данных
ls -lh ecommerce_bot.db

# Резервная копия
cp ecommerce_bot.db backup_$(date +%Y%m%d).db

# Проверка целостности
sqlite3 ecommerce_bot.db "PRAGMA integrity_check;"
```

## 🚨 Устранение неполадок

### Бот не отвечает

1. Проверьте токен бота
2. Убедитесь, что бот не заблокирован
3. Проверьте логи на ошибки

### Ошибки базы данных

1. Проверьте права доступа к файлу БД
2. Убедитесь, что БД не заблокирована
3. Проверьте целостность БД

### Проблемы с админ-панелью

1. Проверьте правильность ADMIN_ID
2. Убедитесь, что вы используете правильный аккаунт
3. Проверьте логи на ошибки доступа

### Частые ошибки

**"Bot token is invalid"**
- Проверьте токен в config.py
- Убедитесь, что токен скопирован полностью

**"Database is locked"**
- Закройте все подключения к БД
- Перезапустите бота

**"Admin access denied"**
- Проверьте ADMIN_ID в config.py
- Убедитесь, что используете правильный аккаунт

## 📈 Масштабирование

### Для больших нагрузок

1. **PostgreSQL вместо SQLite**
2. **Redis для кэширования**
3. **Несколько экземпляров бота**
4. **Load balancer**

### Миграция на PostgreSQL

```python
# config.py
DATABASE_URL = "postgresql://user:password@localhost/ecommerce_bot"

# requirements.txt
# Добавить:
# asyncpg==0.29.0
# sqlalchemy[asyncio]==2.0.23
```

## 🔐 Безопасность

### Рекомендации

1. **Не храните токены в коде**
2. **Используйте переменные окружения**
3. **Регулярно обновляйте зависимости**
4. **Создавайте резервные копии БД**
5. **Мониторьте логи на подозрительную активность**

### Ограничения

1. **Rate limiting** для API запросов
2. **Валидация** всех входных данных
3. **Логирование** всех действий
4. **Проверка прав** доступа

## 📞 Поддержка

При возникновении проблем:

1. Проверьте логи в `bot.log`
2. Убедитесь в правильности конфигурации
3. Проверьте версии зависимостей
4. Создайте issue с подробным описанием

### Полезные команды

```bash
# Проверка версии Python
python --version

# Проверка установленных пакетов
pip list

# Проверка синтаксиса
python -m py_compile main.py

# Проверка импортов
python -c "import aiogram; print('OK')"
```
