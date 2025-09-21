"""
Обработчики для корзины
"""
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from database.repository import CartRepository, ProductRepository
from database.models import CartItem
import config

logger = logging.getLogger(__name__)
router = Router()

# Репозитории
cart_repo = CartRepository()
product_repo = ProductRepository()


@router.callback_query(F.data.startswith("add_to_cart_"))
async def add_to_cart(callback: CallbackQuery):
    """Добавить товар в корзину"""
    try:
        product_id = int(callback.data.split("_")[3])
        user_id = callback.from_user.id
        
        # Проверяем, есть ли товар
        product = await product_repo.get_product(product_id)
        if not product:
            await callback.answer("❌ Товар не найден", show_alert=True)
            return
        
        # Добавляем в корзину
        await cart_repo.add_to_cart(user_id, product_id, 1)
        
        await callback.answer(f"✅ {product.name} добавлен в корзину!")
        
    except Exception as e:
        logger.error(f"Ошибка при добавлении в корзину: {e}")
        await callback.answer("❌ Ошибка при добавлении в корзину", show_alert=True)


@router.callback_query(F.data == "view_cart")
@router.message(Command("cart"))
async def view_cart(callback_or_message, state: FSMContext):
    """Показать корзину"""
    try:
        user_id = callback_or_message.from_user.id
        cart_items = await cart_repo.get_cart_items(user_id)
        
        if not cart_items:
            text = "🛒 Ваша корзина пуста"
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🛍️ Перейти в каталог", callback_data="go_to_catalog")],
                [InlineKeyboardButton(text="🏠 В меню", callback_data="go_to_main_menu")]
            ])
        else:
            text = "🛒 <b>Ваша корзина:</b>\n\n"
            total_amount = 0
            
            keyboard_buttons = []
            
            for item in cart_items:
                product = await product_repo.get_product(item.product_id)
                if product:
                    item_total = product.price * item.quantity
                    total_amount += item_total
                    
                    text += f"📦 <b>{product.name}</b>\n"
                    text += f"   Цена: {product.price}{config.CURRENCY}\n"
                    text += f"   Количество: {item.quantity}\n"
                    text += f"   Сумма: {item_total}{config.CURRENCY}\n\n"
                    
                    # Кнопки для управления количеством
                    keyboard_buttons.append([
                        InlineKeyboardButton(text=f"➖", callback_data=f"decrease_{item.product_id}"),
                        InlineKeyboardButton(text=f"{item.quantity}", callback_data="noop"),
                        InlineKeyboardButton(text=f"➕", callback_data=f"increase_{item.product_id}"),
                        InlineKeyboardButton(text=f"❌", callback_data=f"remove_{item.product_id}")
                    ])
            
            text += f"💰 <b>Итого: {total_amount}{config.CURRENCY}</b>"
            
            # Кнопки для оформления заказа
            keyboard_buttons.extend([
                [InlineKeyboardButton(text="🛒 Оформить заказ", callback_data="checkout")],
                [InlineKeyboardButton(text="🗑️ Очистить корзину", callback_data="clear_cart")],
                [
                    InlineKeyboardButton(text="🛍️ Продолжить покупки", callback_data="go_to_catalog"),
                    InlineKeyboardButton(text="🏠 В меню", callback_data="go_to_main_menu")
                ]
            ])
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        if isinstance(callback_or_message, CallbackQuery):
            await callback_or_message.message.edit_text(
                text,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
            await callback_or_message.answer()
        else:
            await callback_or_message.answer(
                text,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        
    except Exception as e:
        logger.error(f"Ошибка при показе корзины: {e}")
        error_text = "❌ Ошибка при загрузке корзины"
        if isinstance(callback_or_message, CallbackQuery):
            await callback_or_message.answer(error_text, show_alert=True)
        else:
            await callback_or_message.answer(error_text)


@router.callback_query(F.data.startswith("increase_"))
async def increase_quantity(callback: CallbackQuery):
    """Увеличить количество товара"""
    try:
        product_id = int(callback.data.split("_")[1])
        user_id = callback.from_user.id
        
        # Получаем текущее количество
        cart_items = await cart_repo.get_cart_items(user_id)
        current_quantity = 0
        for item in cart_items:
            if item.product_id == product_id:
                current_quantity = item.quantity
                break
        
        # Увеличиваем количество
        await cart_repo.update_cart_item_quantity(user_id, product_id, current_quantity + 1)
        
        # Обновляем отображение корзины
        await view_cart(callback, None)
        
    except Exception as e:
        logger.error(f"Ошибка при увеличении количества: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


@router.callback_query(F.data.startswith("decrease_"))
async def decrease_quantity(callback: CallbackQuery):
    """Уменьшить количество товара"""
    try:
        product_id = int(callback.data.split("_")[1])
        user_id = callback.from_user.id
        
        # Получаем текущее количество
        cart_items = await cart_repo.get_cart_items(user_id)
        current_quantity = 0
        for item in cart_items:
            if item.product_id == product_id:
                current_quantity = item.quantity
                break
        
        # Уменьшаем количество
        new_quantity = max(0, current_quantity - 1)
        await cart_repo.update_cart_item_quantity(user_id, product_id, new_quantity)
        
        # Обновляем отображение корзины
        await view_cart(callback, None)
        
    except Exception as e:
        logger.error(f"Ошибка при уменьшении количества: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


@router.callback_query(F.data.startswith("remove_"))
async def remove_from_cart(callback: CallbackQuery):
    """Удалить товар из корзины"""
    try:
        product_id = int(callback.data.split("_")[1])
        user_id = callback.from_user.id
        
        await cart_repo.remove_from_cart(user_id, product_id)
        
        # Обновляем отображение корзины
        await view_cart(callback, None)
        
    except Exception as e:
        logger.error(f"Ошибка при удалении из корзины: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


@router.callback_query(F.data == "clear_cart")
async def clear_cart(callback: CallbackQuery):
    """Очистить корзину"""
    try:
        user_id = callback.from_user.id
        await cart_repo.clear_cart(user_id)
        
        await callback.answer("🗑️ Корзина очищена!")
        
        # Обновляем отображение корзины
        await view_cart(callback, None)
        
    except Exception as e:
        logger.error(f"Ошибка при очистке корзины: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


@router.callback_query(F.data == "go_to_catalog")
async def go_to_catalog(callback: CallbackQuery, state: FSMContext):
    """Перейти в каталог"""
    try:
        from handlers.catalog import show_catalog
        # Редактируем сообщение вместо создания нового
        await show_catalog(callback.message, state)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка при переходе в каталог: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


@router.callback_query(F.data == "noop")
async def noop(callback: CallbackQuery):
    """Пустой обработчик для кнопок-заглушек"""
    await callback.answer()
