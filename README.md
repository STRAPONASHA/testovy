# Telegram E-commerce Bot

Полнофункциональный Telegram-бот для интернет-магазина, построенный на aiogram 3.x с поддержкой полного цикла покупки товаров.

## 🚀 Возможности

### Для покупателей:
- 🛍️ **Каталог товаров** с категориями и детальными карточками
- 🛒 **Корзина** с управлением количеством товаров
- 📝 **Оформление заказов** с сбором контактных данных
- 🚚 **Выбор способа доставки** (доставка/самовывоз)
- 📋 **Отслеживание заказов** и их статусов
- 💰 **Автоматический подсчет** стоимости с учетом доставки

### Для администраторов:
- ➕ **Добавление товаров** с фото и описанием
- 📦 **Управление товарами** и их количеством
- 📋 **Просмотр заказов** с детальной информацией
- 📊 **Изменение статусов** заказов
- 📈 **Статистика** продаж

## 🏗️ Архитектура

Проект построен с использованием чистого разделения на модули:

```
├── main.py                 # Главный файл бота
├── config.py              # Конфигурация
├── requirements.txt       # Зависимости
├── init_data.py          # Инициализация тестовых данных
├── database/             # Модуль базы данных
│   ├── __init__.py
│   ├── models.py         # Модели данных
│   └── repository.py     # Repository паттерн
├── handlers/             # Обработчики команд
│   ├── __init__.py
│   ├── catalog.py        # Каталог товаров
│   ├── cart.py          # Корзина
│   ├── order.py         # Заказы
│   └── admin.py         # Админ-панель
└── tests/               # Unit-тесты
    ├── __init__.py
    ├── test_cart.py
    ├── test_orders.py
    └── test_products.py
```

## 📋 Требования

- Python 3.8+
- aiogram 3.x
- aiosqlite
- pytest (для тестов)

## 🛠️ Установка и запуск

### 1. Клонирование и установка зависимостей

```bash
# Установка зависимостей
pip install -r requirements.txt
```

### 2. Настройка конфигурации

Отредактируйте файл `config.py`:

```python
# Токен вашего бота (получите у @BotFather)
BOT_TOKEN = "YOUR_BOT_TOKEN"

# Ваш Telegram ID (для админ-панели)
ADMIN_ID = 123456789  # Замените на ваш ID
```

### 3. Инициализация базы данных

```bash
# Создание базы данных и тестовых данных
python init_data.py
```

### 4. Запуск бота

```bash
# Запуск бота
python main.py
```

## 🗄️ База данных

Бот использует SQLite для хранения данных. Схема базы данных включает следующие таблицы:

### Схема базы данных

```sql
-- Пользователи
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    phone TEXT,
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Категории товаров
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT
);

-- Товары
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    price REAL NOT NULL,
    category_id INTEGER,
    image_url TEXT,
    stock INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    FOREIGN KEY (category_id) REFERENCES categories (id)
);

-- Заказы
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    status TEXT DEFAULT 'pending',
    total_amount REAL NOT NULL,
    delivery_method TEXT NOT NULL,
    delivery_address TEXT,
    phone TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Позиции заказов
CREATE TABLE order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    price REAL NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders (id),
    FOREIGN KEY (product_id) REFERENCES products (id)
);

-- Корзина
CREATE TABLE cart_items (
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    PRIMARY KEY (user_id, product_id),
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (product_id) REFERENCES products (id)
);
```

## 🧪 Тестирование

Запуск тестов:

```bash
# Запуск всех тестов
pytest

# Запуск с подробным выводом
pytest -v

# Запуск конкретного теста
pytest tests/test_cart.py -v
```

### Покрытие тестами

Тесты покрывают следующие функции:
- ✅ Добавление товара в корзину
- ✅ Изменение количества товаров в корзине
- ✅ Удаление товаров из корзины
- ✅ Подсчет общей суммы корзины
- ✅ Создание заказов
- ✅ Изменение статусов заказов
- ✅ Управление товарами
- ✅ Обработка ошибок

## 📱 Команды бота

### Основные команды:
- `/start` - Запустить бота
- `/catalog` - Открыть каталог товаров
- `/cart` - Просмотреть корзину
- `/orders` - Посмотреть мои заказы
- `/help` - Показать справку

### Админские команды:
- `/admin` - Открыть админ-панель (только для админов)

## 🔧 API примеры

### Добавление товара через админ-панель

```python
# Пример добавления товара
product = Product(
    name="Новый товар",
    description="Описание товара",
    price=999.99,
    category_id=1,
    stock=10,
    is_active=True
)

created_product = await product_repo.add_product(product)
```

### Создание заказа

```python
# Пример создания заказа
order = Order(
    user_id=12345,
    status="pending",
    total_amount=1299.99,
    delivery_method="delivery",
    delivery_address="Адрес доставки",
    phone="+1234567890"
)

order_items = [
    OrderItem(
        product_id=1,
        quantity=2,
        price=649.99
    )
]

created_order = await order_repo.create_order(order, order_items)
```

## 📊 Статусы заказов

- `pending` - Ожидает подтверждения
- `confirmed` - Подтвержден
- `preparing` - Готовится
- `shipping` - В пути
- `delivered` - Доставлен
- `cancelled` - Отменен

## 🚚 Способы доставки

- `delivery` - Доставка (+200₽)
- `pickup` - Самовывоз

## 📝 Логирование

Бот ведет подробные логи в файле `bot.log` с уровнями:
- INFO - Общая информация
- ERROR - Ошибки
- DEBUG - Отладочная информация

## 🔒 Безопасность

- Проверка прав администратора
- Валидация входных данных
- Обработка ошибок с информативными сообщениями
- Логирование всех действий

## 🚀 Развертывание

### Локальное развертывание:
1. Установите зависимости
2. Настройте конфигурацию
3. Инициализируйте базу данных
4. Запустите бота

### Продакшн развертывание:
- Используйте процесс-менеджер (systemd, supervisor)
- Настройте логирование
- Регулярно создавайте бэкапы базы данных
- Мониторьте работу бота

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции
3. Внесите изменения
4. Добавьте тесты
5. Создайте Pull Request

## 📄 Лицензия

MIT License

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи в файле `bot.log`
2. Убедитесь в правильности конфигурации
3. Проверьте права доступа к файлам
4. Создайте issue в репозитории

---

**Автор:** Timeless Store Bot  
**Версия:** 1.0.0  
**Дата:** 2024
