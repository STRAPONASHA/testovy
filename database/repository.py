"""
Repository паттерн для работы с базой данных
"""
import aiosqlite
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from .models import User, Product, Category, Order, OrderItem, CartItem
import config


class DatabaseRepository:
    """Базовый класс для работы с базой данных"""
    
    def __init__(self, db_path: str = "ecommerce_bot.db"):
        self.db_path = db_path
    
    async def init_db(self):
        """Инициализация базы данных"""
        async with aiosqlite.connect(self.db_path) as db:
            # Создание таблиц
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    phone TEXT,
                    address TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    price REAL NOT NULL,
                    category_id INTEGER,
                    image_url TEXT,
                    stock INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1,
                    detailed_description TEXT,
                    sizes TEXT,
                    colors TEXT,
                    material TEXT,
                    weight TEXT,
                    dimensions TEXT,
                    brand TEXT,
                    country TEXT,
                    FOREIGN KEY (category_id) REFERENCES categories (id)
                )
            """)
            
            await db.execute("""
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
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS order_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    price REAL NOT NULL,
                    FOREIGN KEY (order_id) REFERENCES orders (id),
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS cart_items (
                    user_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    PRIMARY KEY (user_id, product_id),
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
            """)
            
            await db.commit()


class UserRepository(DatabaseRepository):
    """Репозиторий для работы с пользователями"""
    
    async def get_user(self, user_id: int) -> Optional[User]:
        """Получить пользователя по ID"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM users WHERE id = ?", (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return User(
                        id=row['id'],
                        username=row['username'],
                        first_name=row['first_name'],
                        last_name=row['last_name'],
                        phone=row['phone'],
                        address=row['address'],
                        created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
                    )
                return None
    
    async def create_user(self, user: User) -> User:
        """Создать пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO users 
                (id, username, first_name, last_name, phone, address, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                user.id, user.username, user.first_name, user.last_name,
                user.phone, user.address, user.created_at or datetime.now()
            ))
            await db.commit()
            return user
    
    async def update_user(self, user: User) -> User:
        """Обновить данные пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE users SET 
                username = ?, first_name = ?, last_name = ?, 
                phone = ?, address = ?
                WHERE id = ?
            """, (
                user.username, user.first_name, user.last_name,
                user.phone, user.address, user.id
            ))
            await db.commit()
            return user


class ProductRepository(DatabaseRepository):
    """Репозиторий для работы с товарами"""
    
    async def get_categories(self) -> List[Category]:
        """Получить все категории"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM categories ORDER BY name") as cursor:
                rows = await cursor.fetchall()
                return [
                    Category(
                        id=row['id'],
                        name=row['name'],
                        description=row['description']
                    ) for row in rows
                ]
    
    async def get_products_by_category(self, category_id: int) -> List[Product]:
        """Получить товары по категории"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM products 
                WHERE category_id = ? AND is_active = 1 
                ORDER BY name
            """, (category_id,)) as cursor:
                rows = await cursor.fetchall()
                return [
                    Product(
                        id=row['id'],
                        name=row['name'],
                        description=row['description'],
                        price=row['price'],
                        category_id=row['category_id'],
                        image_url=row['image_url'],
                        stock=row['stock'],
                        is_active=bool(row['is_active']),
                        detailed_description=row['detailed_description'] if 'detailed_description' in row.keys() else None,
                        sizes=row['sizes'] if 'sizes' in row.keys() else None,
                        colors=row['colors'] if 'colors' in row.keys() else None,
                        material=row['material'] if 'material' in row.keys() else None,
                        weight=row['weight'] if 'weight' in row.keys() else None,
                        dimensions=row['dimensions'] if 'dimensions' in row.keys() else None,
                        brand=row['brand'] if 'brand' in row.keys() else None,
                        country=row['country'] if 'country' in row.keys() else None
                    ) for row in rows
                ]
    
    async def get_products(self) -> List[Product]:
        """Получить все товары"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT * FROM products WHERE is_active = 1 ORDER BY id DESC
            """)
            rows = await cursor.fetchall()
            products = []
            for row in rows:
                products.append(Product(
                    id=row['id'],
                    name=row['name'],
                    description=row['description'],
                    price=row['price'],
                    category_id=row['category_id'],
                    image_url=row['image_url'],
                    stock=row['stock'],
                    is_active=bool(row['is_active']),
                    detailed_description=row['detailed_description'] if 'detailed_description' in row.keys() else None,
                    sizes=row['sizes'] if 'sizes' in row.keys() else None,
                    colors=row['colors'] if 'colors' in row.keys() else None,
                    material=row['material'] if 'material' in row.keys() else None,
                    weight=row['weight'] if 'weight' in row.keys() else None,
                    dimensions=row['dimensions'] if 'dimensions' in row.keys() else None,
                    brand=row['brand'] if 'brand' in row.keys() else None,
                    country=row['country'] if 'country' in row.keys() else None
                ))
            return products

    async def get_product(self, product_id: int) -> Optional[Product]:
        """Получить товар по ID"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM products WHERE id = ?", (product_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return Product(
                        id=row['id'],
                        name=row['name'],
                        description=row['description'],
                        price=row['price'],
                        category_id=row['category_id'],
                        image_url=row['image_url'],
                        stock=row['stock'],
                        is_active=bool(row['is_active']),
                        detailed_description=row['detailed_description'] if 'detailed_description' in row.keys() else None,
                        sizes=row['sizes'] if 'sizes' in row.keys() else None,
                        colors=row['colors'] if 'colors' in row.keys() else None,
                        material=row['material'] if 'material' in row.keys() else None,
                        weight=row['weight'] if 'weight' in row.keys() else None,
                        dimensions=row['dimensions'] if 'dimensions' in row.keys() else None,
                        brand=row['brand'] if 'brand' in row.keys() else None,
                        country=row['country'] if 'country' in row.keys() else None
                    )
                return None
    
    async def add_product(self, product: Product) -> Product:
        """Добавить товар"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO products 
                (name, description, price, category_id, image_url, stock, is_active,
                 detailed_description, sizes, colors, material, weight, dimensions, brand, country)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product.name, product.description, product.price,
                product.category_id, product.image_url, product.stock, product.is_active,
                product.detailed_description, product.sizes, product.colors, product.material,
                product.weight, product.dimensions, product.brand, product.country
            ))
            product.id = cursor.lastrowid
            await db.commit()
            return product
    
    async def update_product(self, product: Product) -> Product:
        """Обновить товар"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE products SET 
                name = ?, description = ?, price = ?, category_id = ?,
                image_url = ?, stock = ?, is_active = ?
                WHERE id = ?
            """, (
                product.name, product.description, product.price,
                product.category_id, product.image_url, product.stock,
                product.is_active, product.id
            ))
            await db.commit()
            return product


class CartRepository(DatabaseRepository):
    """Репозиторий для работы с корзиной"""
    
    async def get_cart_items(self, user_id: int) -> List[CartItem]:
        """Получить товары в корзине"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM cart_items WHERE user_id = ?
            """, (user_id,)) as cursor:
                rows = await cursor.fetchall()
                return [
                    CartItem(
                        user_id=row['user_id'],
                        product_id=row['product_id'],
                        quantity=row['quantity']
                    ) for row in rows
                ]
    
    async def add_to_cart(self, user_id: int, product_id: int, quantity: int = 1):
        """Добавить товар в корзину"""
        async with aiosqlite.connect(self.db_path) as db:
            # Проверяем, есть ли уже такой товар в корзине
            async with db.execute("""
                SELECT quantity FROM cart_items 
                WHERE user_id = ? AND product_id = ?
            """, (user_id, product_id)) as cursor:
                existing = await cursor.fetchone()
                
                if existing:
                    # Увеличиваем количество
                    await db.execute("""
                        UPDATE cart_items SET quantity = quantity + ?
                        WHERE user_id = ? AND product_id = ?
                    """, (quantity, user_id, product_id))
                else:
                    # Добавляем новый товар
                    await db.execute("""
                        INSERT INTO cart_items (user_id, product_id, quantity)
                        VALUES (?, ?, ?)
                    """, (user_id, product_id, quantity))
            
            await db.commit()
    
    async def update_cart_item_quantity(self, user_id: int, product_id: int, quantity: int):
        """Обновить количество товара в корзине"""
        async with aiosqlite.connect(self.db_path) as db:
            if quantity <= 0:
                await db.execute("""
                    DELETE FROM cart_items 
                    WHERE user_id = ? AND product_id = ?
                """, (user_id, product_id))
            else:
                await db.execute("""
                    UPDATE cart_items SET quantity = ?
                    WHERE user_id = ? AND product_id = ?
                """, (quantity, user_id, product_id))
            await db.commit()
    
    async def remove_from_cart(self, user_id: int, product_id: int):
        """Удалить товар из корзины"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                DELETE FROM cart_items 
                WHERE user_id = ? AND product_id = ?
            """, (user_id, product_id))
            await db.commit()
    
    async def clear_cart(self, user_id: int):
        """Очистить корзину"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM cart_items WHERE user_id = ?", (user_id,))
            await db.commit()


class OrderRepository(DatabaseRepository):
    """Репозиторий для работы с заказами"""
    
    async def create_order(self, order: Order, order_items: List[OrderItem]) -> Order:
        """Создать заказ"""
        async with aiosqlite.connect(self.db_path) as db:
            # Создаем заказ
            cursor = await db.execute("""
                INSERT INTO orders 
                (user_id, status, total_amount, delivery_method, 
                 delivery_address, phone, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                order.user_id, order.status, order.total_amount,
                order.delivery_method, order.delivery_address,
                order.phone, order.created_at or datetime.now(),
                order.updated_at or datetime.now()
            ))
            order.id = cursor.lastrowid
            
            # Добавляем позиции заказа
            for item in order_items:
                item.order_id = order.id
                await db.execute("""
                    INSERT INTO order_items 
                    (order_id, product_id, quantity, price)
                    VALUES (?, ?, ?, ?)
                """, (item.order_id, item.product_id, item.quantity, item.price))
            
            await db.commit()
            return order
    
    async def get_orders(self, user_id: Optional[int] = None) -> List[Order]:
        """Получить заказы (все или пользователя)"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            if user_id:
                async with db.execute("""
                    SELECT * FROM orders WHERE user_id = ? 
                    ORDER BY created_at DESC
                """, (user_id,)) as cursor:
                    rows = await cursor.fetchall()
            else:
                async with db.execute("""
                    SELECT * FROM orders ORDER BY created_at DESC
                """) as cursor:
                    rows = await cursor.fetchall()
            
            return [
                Order(
                    id=row['id'],
                    user_id=row['user_id'],
                    status=row['status'],
                    total_amount=row['total_amount'],
                    delivery_method=row['delivery_method'],
                    delivery_address=row['delivery_address'],
                    phone=row['phone'],
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                    updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
                ) for row in rows
            ]
    
    async def get_order_items(self, order_id: int) -> List[OrderItem]:
        """Получить позиции заказа"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM order_items WHERE order_id = ?
            """, (order_id,)) as cursor:
                rows = await cursor.fetchall()
                return [
                    OrderItem(
                        id=row['id'],
                        order_id=row['order_id'],
                        product_id=row['product_id'],
                        quantity=row['quantity'],
                        price=row['price']
                    ) for row in rows
                ]
    
    async def update_order_status(self, order_id: int, status: str):
        """Обновить статус заказа"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE orders SET status = ?, updated_at = ?
                WHERE id = ?
            """, (status, datetime.now(), order_id))
            await db.commit()
