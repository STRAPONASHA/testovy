# Схема базы данных E-commerce Bot

## Обзор

База данных построена на SQLite и содержит 6 основных таблиц для управления пользователями, товарами, заказами и корзиной.

## Таблицы

### 1. users - Пользователи

Хранит информацию о пользователях Telegram-бота.

| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PRIMARY KEY | Telegram ID пользователя |
| username | TEXT | Username в Telegram |
| first_name | TEXT | Имя пользователя |
| last_name | TEXT | Фамилия пользователя |
| phone | TEXT | Номер телефона |
| address | TEXT | Адрес доставки |
| created_at | TIMESTAMP | Дата регистрации |

**Индексы:**
- PRIMARY KEY на `id`

**Связи:**
- Один ко многим с `orders` (user_id)
- Один ко многим с `cart_items` (user_id)

### 2. categories - Категории товаров

Категории для группировки товаров.

| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PRIMARY KEY AUTOINCREMENT | Уникальный ID категории |
| name | TEXT NOT NULL | Название категории |
| description | TEXT | Описание категории |

**Индексы:**
- PRIMARY KEY на `id`
- UNIQUE на `name`

**Связи:**
- Один ко многим с `products` (category_id)

### 3. products - Товары

Каталог товаров магазина.

| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PRIMARY KEY AUTOINCREMENT | Уникальный ID товара |
| name | TEXT NOT NULL | Название товара |
| description | TEXT NOT NULL | Описание товара |
| price | REAL NOT NULL | Цена товара |
| category_id | INTEGER | ID категории |
| image_url | TEXT | URL или ID изображения |
| stock | INTEGER DEFAULT 0 | Количество на складе |
| is_active | BOOLEAN DEFAULT 1 | Активен ли товар |

**Индексы:**
- PRIMARY KEY на `id`
- FOREIGN KEY на `category_id`

**Связи:**
- Многие к одному с `categories` (category_id)
- Один ко многим с `order_items` (product_id)
- Один ко многим с `cart_items` (product_id)

### 4. orders - Заказы

Заказы пользователей.

| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PRIMARY KEY AUTOINCREMENT | Уникальный ID заказа |
| user_id | INTEGER NOT NULL | ID пользователя |
| status | TEXT DEFAULT 'pending' | Статус заказа |
| total_amount | REAL NOT NULL | Общая сумма заказа |
| delivery_method | TEXT NOT NULL | Способ доставки |
| delivery_address | TEXT | Адрес доставки |
| phone | TEXT | Телефон для связи |
| created_at | TIMESTAMP | Дата создания |
| updated_at | TIMESTAMP | Дата обновления |

**Индексы:**
- PRIMARY KEY на `id`
- FOREIGN KEY на `user_id`
- INDEX на `status`
- INDEX на `created_at`

**Связи:**
- Многие к одному с `users` (user_id)
- Один ко многим с `order_items` (order_id)

**Возможные статусы:**
- `pending` - Ожидает подтверждения
- `confirmed` - Подтвержден
- `preparing` - Готовится
- `shipping` - В пути
- `delivered` - Доставлен
- `cancelled` - Отменен

### 5. order_items - Позиции заказов

Детализация товаров в заказе.

| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PRIMARY KEY AUTOINCREMENT | Уникальный ID позиции |
| order_id | INTEGER NOT NULL | ID заказа |
| product_id | INTEGER NOT NULL | ID товара |
| quantity | INTEGER NOT NULL | Количество |
| price | REAL NOT NULL | Цена на момент заказа |

**Индексы:**
- PRIMARY KEY на `id`
- FOREIGN KEY на `order_id`
- FOREIGN KEY на `product_id`
- COMPOSITE INDEX на `(order_id, product_id)`

**Связи:**
- Многие к одному с `orders` (order_id)
- Многие к одному с `products` (product_id)

### 6. cart_items - Корзина

Временное хранение товаров в корзине пользователя.

| Поле | Тип | Описание |
|------|-----|----------|
| user_id | INTEGER NOT NULL | ID пользователя |
| product_id | INTEGER NOT NULL | ID товара |
| quantity | INTEGER NOT NULL | Количество |

**Индексы:**
- PRIMARY KEY на `(user_id, product_id)`
- FOREIGN KEY на `user_id`
- FOREIGN KEY на `product_id`

**Связи:**
- Многие к одному с `users` (user_id)
- Многие к одному с `products` (product_id)

## Диаграмма связей

```
users (1) -----> (N) orders
users (1) -----> (N) cart_items

categories (1) -----> (N) products

products (1) -----> (N) order_items
products (1) -----> (N) cart_items

orders (1) -----> (N) order_items
```

## Примеры запросов

### Получение заказа с товарами

```sql
SELECT 
    o.id,
    o.total_amount,
    o.status,
    o.created_at,
    u.first_name,
    u.phone,
    GROUP_CONCAT(p.name || ' x' || oi.quantity) as products
FROM orders o
JOIN users u ON o.user_id = u.id
JOIN order_items oi ON o.id = oi.order_id
JOIN products p ON oi.product_id = p.id
WHERE o.id = ?
GROUP BY o.id;
```

### Статистика продаж

```sql
SELECT 
    DATE(created_at) as date,
    COUNT(*) as orders_count,
    SUM(total_amount) as total_revenue
FROM orders 
WHERE status = 'delivered'
GROUP BY DATE(created_at)
ORDER BY date DESC;
```

### Топ товаров

```sql
SELECT 
    p.name,
    SUM(oi.quantity) as total_sold,
    SUM(oi.quantity * oi.price) as total_revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.id
JOIN orders o ON oi.order_id = o.id
WHERE o.status = 'delivered'
GROUP BY p.id, p.name
ORDER BY total_sold DESC
LIMIT 10;
```

### Корзина пользователя

```sql
SELECT 
    p.name,
    p.price,
    ci.quantity,
    (p.price * ci.quantity) as total
FROM cart_items ci
JOIN products p ON ci.product_id = p.id
WHERE ci.user_id = ? AND p.is_active = 1;
```

## Миграции

### Создание таблиц

```sql
-- Создание всех таблиц
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    phone TEXT,
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS products (
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

CREATE TABLE IF NOT EXISTS orders (
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

CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    price REAL NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders (id),
    FOREIGN KEY (product_id) REFERENCES products (id)
);

CREATE TABLE IF NOT EXISTS cart_items (
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    PRIMARY KEY (user_id, product_id),
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (product_id) REFERENCES products (id)
);
```

### Добавление индексов

```sql
-- Индексы для оптимизации
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_products_active ON products(is_active);
CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id);
```

## Резервное копирование

### Создание бэкапа

```bash
# Создание бэкапа базы данных
sqlite3 ecommerce_bot.db ".backup backup_$(date +%Y%m%d_%H%M%S).db"
```

### Восстановление из бэкапа

```bash
# Восстановление из бэкапа
sqlite3 ecommerce_bot.db ".restore backup_20241201_120000.db"
```

## Производительность

### Рекомендации по оптимизации

1. **Индексы**: Созданы индексы на часто используемые поля
2. **Нормализация**: База нормализована до 3NF
3. **Ограничения**: Использованы FOREIGN KEY для целостности данных
4. **Типы данных**: Выбраны оптимальные типы для экономии места

### Мониторинг

```sql
-- Анализ использования индексов
EXPLAIN QUERY PLAN SELECT * FROM orders WHERE status = 'pending';

-- Размер базы данных
SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size();

-- Статистика таблиц
SELECT name, COUNT(*) as row_count FROM sqlite_master 
WHERE type='table' AND name NOT LIKE 'sqlite_%'
GROUP BY name;
```
