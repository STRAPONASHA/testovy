"""
Конфигурация для Telegram-бота e-commerce
"""
import os
from dotenv import load_dotenv
import pytz

load_dotenv()

# Московское время
MOSCOW_TZ = pytz.timezone('Europe/Moscow')

# Токен бота
BOT_TOKEN = "8428797317:AAF0cDe_77AIN5XPAHgKZ2ApruT_waWuV4A"

# ID администраторов
ADMIN_IDS = [808374187, 808374187]  # Массив ID администраторов

# Настройки базы данных
DATABASE_URL = "sqlite:///ecommerce_bot.db"

# Настройки логирования
LOG_LEVEL = "INFO"
LOG_FILE = "bot.log"

# Настройки магазина
SHOP_NAME = "Timeless Store"
CURRENCY = "₽"

# Способы доставки
DELIVERY_METHODS = {
    "delivery": "Доставка (+200₽)",
    "pickup": "Самовывоз"
}

# Статусы заказов (упрощенные для админ-панели)
ORDER_STATUSES = {
    "pending": "Принят",
    "shipping": "В пути", 
    "delivered": "Доставлен"
}
