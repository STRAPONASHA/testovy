"""
Модели базы данных для e-commerce бота
"""
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime


@dataclass
class User:
    """Модель пользователя"""
    id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class Category:
    """Модель категории товаров"""
    id: int
    name: str
    description: Optional[str] = None


@dataclass
class Product:
    """Модель товара"""
    id: int
    name: str
    description: str
    price: float
    category_id: int
    image_url: Optional[str] = None
    stock: int = 0
    is_active: bool = True
    # Новые поля для улучшенных карточек
    detailed_description: Optional[str] = None  # Подробное описание
    sizes: Optional[str] = None  # Размеры (например: "S,M,L,XL")
    colors: Optional[str] = None  # Цвета (например: "Красный,Синий,Черный")
    material: Optional[str] = None  # Материал
    weight: Optional[str] = None  # Вес
    dimensions: Optional[str] = None  # Размеры (например: "30x40x10 см")
    brand: Optional[str] = None  # Бренд
    country: Optional[str] = None  # Страна производства


@dataclass
class Order:
    """Модель заказа"""
    id: int
    user_id: int
    status: str
    total_amount: float
    delivery_method: str
    delivery_address: Optional[str] = None
    phone: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class OrderItem:
    """Модель позиции заказа"""
    id: int
    order_id: int
    product_id: int
    quantity: int
    price: float


@dataclass
class CartItem:
    """Модель позиции корзины"""
    user_id: int
    product_id: int
    quantity: int
