# Примеры использования API

## 📚 Обзор

Данный документ содержит примеры использования API для управления товарами, заказами и пользователями в Telegram e-commerce боте.

## 🛍️ Управление товарами

### Добавление товара

```python
from database.repository import ProductRepository
from database.models import Product

# Создание репозитория
product_repo = ProductRepository()

# Создание товара
product = Product(
    id=0,  # Будет установлен автоматически
    name="iPhone 15 Pro",
    description="Новейший смартфон Apple с титановым корпусом",
    price=99999.0,
    category_id=1,  # ID категории "Электроника"
    image_url="photo_file_id",  # ID фото в Telegram
    stock=5,
    is_active=True
)

# Сохранение товара
created_product = await product_repo.add_product(product)
print(f"Товар создан с ID: {created_product.id}")
```

### Получение товара по ID

```python
# Получение товара
product = await product_repo.get_product(product_id=1)

if product:
    print(f"Название: {product.name}")
    print(f"Цена: {product.price}₽")
    print(f"В наличии: {product.stock} шт.")
else:
    print("Товар не найден")
```

### Получение товаров по категории

```python
# Получение всех товаров в категории
products = await product_repo.get_products_by_category(category_id=1)

for product in products:
    print(f"{product.name} - {product.price}₽")
```

### Обновление товара

```python
# Получение товара
product = await product_repo.get_product(product_id=1)

# Обновление данных
product.price = 89999.0
product.stock = 3
product.name = "iPhone 15 Pro (обновленная цена)"

# Сохранение изменений
updated_product = await product_repo.update_product(product)
print("Товар обновлен")
```

## 🛒 Управление корзиной

### Добавление товара в корзину

```python
from database.repository import CartRepository

cart_repo = CartRepository()
user_id = 12345
product_id = 1
quantity = 2

# Добавление товара в корзину
await cart_repo.add_to_cart(user_id, product_id, quantity)
print("Товар добавлен в корзину")
```

### Получение содержимого корзины

```python
# Получение товаров в корзине
cart_items = await cart_repo.get_cart_items(user_id)

total_amount = 0
for item in cart_items:
    product = await product_repo.get_product(item.product_id)
    item_total = product.price * item.quantity
    total_amount += item_total
    
    print(f"{product.name} x{item.quantity} = {item_total}₽")

print(f"Итого: {total_amount}₽")
```

### Изменение количества товара

```python
# Увеличение количества
await cart_repo.update_cart_item_quantity(user_id, product_id, 3)

# Уменьшение количества
await cart_repo.update_cart_item_quantity(user_id, product_id, 1)

# Удаление товара (количество = 0)
await cart_repo.update_cart_item_quantity(user_id, product_id, 0)
```

### Удаление товара из корзины

```python
# Удаление конкретного товара
await cart_repo.remove_from_cart(user_id, product_id)

# Очистка всей корзины
await cart_repo.clear_cart(user_id)
```

## 📋 Управление заказами

### Создание заказа

```python
from database.repository import OrderRepository
from database.models import Order, OrderItem
from datetime import datetime

order_repo = OrderRepository()

# Создание заказа
order = Order(
    id=0,  # Будет установлен автоматически
    user_id=12345,
    status="pending",
    total_amount=1299.99,
    delivery_method="delivery",
    delivery_address="ул. Примерная, д. 1, кв. 1",
    phone="+7 (999) 123-45-67",
    created_at=datetime.now(),
    updated_at=datetime.now()
)

# Создание позиций заказа
order_items = [
    OrderItem(
        id=0,
        order_id=0,  # Будет установлен автоматически
        product_id=1,
        quantity=2,
        price=649.99
    )
]

# Сохранение заказа
created_order = await order_repo.create_order(order, order_items)
print(f"Заказ создан с номером: #{created_order.id}")
```

### Получение заказов пользователя

```python
# Получение всех заказов пользователя
user_orders = await order_repo.get_orders(user_id=12345)

for order in user_orders:
    print(f"Заказ #{order.id}")
    print(f"Сумма: {order.total_amount}₽")
    print(f"Статус: {order.status}")
    print(f"Дата: {order.created_at}")
    print("---")
```

### Получение всех заказов (для админа)

```python
# Получение всех заказов
all_orders = await order_repo.get_orders()

for order in all_orders:
    print(f"Заказ #{order.id} от пользователя {order.user_id}")
    print(f"Сумма: {order.total_amount}₽")
    print(f"Статус: {order.status}")
```

### Получение деталей заказа

```python
# Получение позиций заказа
order_items = await order_repo.get_order_items(order_id=1)

for item in order_items:
    product = await product_repo.get_product(item.product_id)
    print(f"{product.name} x{item.quantity} = {item.price * item.quantity}₽")
```

### Изменение статуса заказа

```python
# Изменение статуса заказа
await order_repo.update_order_status(order_id=1, status="confirmed")
print("Статус заказа изменен на 'confirmed'")

# Возможные статусы:
# - "pending" - Ожидает подтверждения
# - "confirmed" - Подтвержден
# - "preparing" - Готовится
# - "shipping" - В пути
# - "delivered" - Доставлен
# - "cancelled" - Отменен
```

## 👥 Управление пользователями

### Создание пользователя

```python
from database.repository import UserRepository
from database.models import User

user_repo = UserRepository()

# Создание пользователя
user = User(
    id=12345,
    username="john_doe",
    first_name="John",
    last_name="Doe",
    phone="+7 (999) 123-45-67",
    address="ул. Примерная, д. 1, кв. 1",
    created_at=datetime.now()
)

# Сохранение пользователя
created_user = await user_repo.create_user(user)
print(f"Пользователь создан: {created_user.first_name}")
```

### Получение пользователя

```python
# Получение пользователя по ID
user = await user_repo.get_user(user_id=12345)

if user:
    print(f"Имя: {user.first_name} {user.last_name}")
    print(f"Телефон: {user.phone}")
    print(f"Адрес: {user.address}")
else:
    print("Пользователь не найден")
```

### Обновление данных пользователя

```python
# Получение пользователя
user = await user_repo.get_user(user_id=12345)

# Обновление данных
user.phone = "+7 (999) 987-65-43"
user.address = "ул. Новая, д. 2, кв. 2"

# Сохранение изменений
updated_user = await user_repo.update_user(user)
print("Данные пользователя обновлены")
```

## 📊 Статистика и аналитика

### Подсчет общей суммы корзины

```python
async def calculate_cart_total(user_id):
    """Подсчет общей суммы корзины"""
    cart_items = await cart_repo.get_cart_items(user_id)
    total = 0
    
    for item in cart_items:
        product = await product_repo.get_product(item.product_id)
        if product:
            total += product.price * item.quantity
    
    return total

# Использование
total = await calculate_cart_total(user_id=12345)
print(f"Общая сумма корзины: {total}₽")
```

### Статистика заказов

```python
async def get_order_statistics():
    """Получение статистики заказов"""
    orders = await order_repo.get_orders()
    
    stats = {
        "total_orders": len(orders),
        "total_revenue": sum(order.total_amount for order in orders),
        "pending_orders": len([o for o in orders if o.status == "pending"]),
        "delivered_orders": len([o for o in orders if o.status == "delivered"])
    }
    
    return stats

# Использование
stats = await get_order_statistics()
print(f"Всего заказов: {stats['total_orders']}")
print(f"Общая выручка: {stats['total_revenue']}₽")
```

### Топ товаров

```python
async def get_top_products(limit=10):
    """Получение топ товаров по продажам"""
    orders = await order_repo.get_orders()
    product_sales = {}
    
    for order in orders:
        if order.status == "delivered":
            order_items = await order_repo.get_order_items(order.id)
            for item in order_items:
                if item.product_id not in product_sales:
                    product_sales[item.product_id] = 0
                product_sales[item.product_id] += item.quantity
    
    # Сортируем по количеству продаж
    top_products = sorted(product_sales.items(), key=lambda x: x[1], reverse=True)
    
    result = []
    for product_id, sales_count in top_products[:limit]:
        product = await product_repo.get_product(product_id)
        if product:
            result.append({
                "product": product,
                "sales_count": sales_count
            })
    
    return result

# Использование
top_products = await get_top_products(5)
for item in top_products:
    print(f"{item['product'].name}: {item['sales_count']} продаж")
```

## 🔄 Обработка ошибок

### Базовый пример с обработкой ошибок

```python
async def safe_add_to_cart(user_id, product_id, quantity):
    """Безопасное добавление товара в корзину"""
    try:
        # Проверяем существование товара
        product = await product_repo.get_product(product_id)
        if not product:
            return {"success": False, "error": "Товар не найден"}
        
        # Проверяем наличие на складе
        if product.stock < quantity:
            return {"success": False, "error": "Недостаточно товара на складе"}
        
        # Добавляем в корзину
        await cart_repo.add_to_cart(user_id, product_id, quantity)
        
        return {"success": True, "message": "Товар добавлен в корзину"}
        
    except Exception as e:
        return {"success": False, "error": f"Ошибка: {str(e)}"}

# Использование
result = await safe_add_to_cart(user_id=12345, product_id=1, quantity=2)
if result["success"]:
    print(result["message"])
else:
    print(f"Ошибка: {result['error']}")
```

### Валидация данных

```python
def validate_product_data(name, description, price, stock):
    """Валидация данных товара"""
    errors = []
    
    if not name or len(name.strip()) < 3:
        errors.append("Название должно содержать минимум 3 символа")
    
    if not description or len(description.strip()) < 10:
        errors.append("Описание должно содержать минимум 10 символов")
    
    try:
        price = float(price)
        if price <= 0:
            errors.append("Цена должна быть больше 0")
    except ValueError:
        errors.append("Цена должна быть числом")
    
    try:
        stock = int(stock)
        if stock < 0:
            errors.append("Количество не может быть отрицательным")
    except ValueError:
        errors.append("Количество должно быть целым числом")
    
    return errors

# Использование
errors = validate_product_data("iPhone", "Смартфон", "99999", "5")
if errors:
    for error in errors:
        print(f"Ошибка: {error}")
else:
    print("Данные валидны")
```

## 🚀 Асинхронное программирование

### Использование asyncio

```python
import asyncio

async def main():
    """Основная функция"""
    # Инициализация репозиториев
    product_repo = ProductRepository()
    cart_repo = CartRepository()
    order_repo = OrderRepository()
    
    # Инициализация базы данных
    await product_repo.init_db()
    
    # Примеры использования
    products = await product_repo.get_products_by_category(1)
    print(f"Найдено товаров: {len(products)}")
    
    # Добавление товара в корзину
    await cart_repo.add_to_cart(12345, 1, 2)
    
    # Получение корзины
    cart_items = await cart_repo.get_cart_items(12345)
    print(f"Товаров в корзине: {len(cart_items)}")

# Запуск
if __name__ == "__main__":
    asyncio.run(main())
```

### Параллельное выполнение

```python
async def get_user_data(user_id):
    """Получение всех данных пользователя параллельно"""
    # Создаем задачи для параллельного выполнения
    user_task = user_repo.get_user(user_id)
    cart_task = cart_repo.get_cart_items(user_id)
    orders_task = order_repo.get_orders(user_id)
    
    # Ждем выполнения всех задач
    user, cart_items, orders = await asyncio.gather(
        user_task, cart_task, orders_task
    )
    
    return {
        "user": user,
        "cart_items": cart_items,
        "orders": orders
    }

# Использование
user_data = await get_user_data(12345)
print(f"Пользователь: {user_data['user'].first_name}")
print(f"Товаров в корзине: {len(user_data['cart_items'])}")
print(f"Заказов: {len(user_data['orders'])}")
```

## 📝 Заключение

Данные примеры демонстрируют основные возможности API для работы с e-commerce ботом. Все операции выполняются асинхронно и включают обработку ошибок для обеспечения надежности системы.

Для получения дополнительной информации обратитесь к документации модулей в папке `database/` и `handlers/`.
