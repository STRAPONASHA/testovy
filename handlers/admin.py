"""
Обработчики для админ-панели
"""
import logging
from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.repository import ProductRepository, OrderRepository, UserRepository
from database.models import Product, Category
import config

logger = logging.getLogger(__name__)
router = Router()

# Репозитории
product_repo = ProductRepository()
order_repo = OrderRepository()
user_repo = UserRepository()


class AdminStates(StatesGroup):
    """Состояния для админ-панели"""
    adding_product_name = State()
    adding_product_description = State()
    adding_product_price = State()
    adding_product_category = State()
    adding_product_stock = State()
    adding_product_image = State()
    editing_product = State()
    editing_product_field = State()
    editing_product_value = State()


def is_admin(user_id: int) -> bool:
    """Проверить, является ли пользователь администратором"""
    return user_id in config.ADMIN_IDS


# Убираем отдельные команды - все через админ-панель


@router.message(Command("admin"))
async def admin_panel(message: Message):
    """Показать админ-панель"""
    try:
        if not is_admin(message.from_user.id):
            await message.answer("❌ У вас нет прав доступа к админ-панели.")
            return
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Добавить товар", callback_data="admin_add_product")],
            [InlineKeyboardButton(text="✏️ Редактировать товары", callback_data="admin_edit_products")],
            [InlineKeyboardButton(text="📋 Заказы", callback_data="admin_orders")],
            [InlineKeyboardButton(text="🏠 В меню", callback_data="go_to_main_menu")]
        ])
        
        await message.answer(
            "🔧 <b>Админ-панель</b>\n\n"
            "Выберите действие:",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Ошибка в админ-панели: {e}")
        await message.answer("❌ Ошибка в админ-панели")


@router.callback_query(F.data == "admin_edit_products")
async def show_products_for_edit(callback: CallbackQuery):
    """Показать товары для редактирования"""
    try:
        if not is_admin(callback.from_user.id):
            await callback.answer("❌ Нет прав доступа", show_alert=True)
            return
        
        # Получаем все товары
        products = await product_repo.get_products()
        
        if not products:
            await callback.message.edit_text(
                "📦 Товаров пока нет.\n\nДобавьте товары через кнопку 'Добавить товар'.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="➕ Добавить товар", callback_data="admin_add_product")],
                    [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_panel")]
                ])
            )
            return
        
        text = "📦 <b>Выберите товар для редактирования:</b>\n\n"
        
        keyboard_buttons = []
        for product in products[:10]:  # Показываем первые 10 товаров
            text += f"🆔 {product.id} - {product.name} ({product.price}{config.CURRENCY})\n"
            keyboard_buttons.append([
                InlineKeyboardButton(
                    text=f"✏️ {product.name[:20]}...",
                    callback_data=f"edit_product_{product.id}"
                )
            ])
        
        keyboard_buttons.append([
            InlineKeyboardButton(text="🔙 Назад", callback_data="admin_panel")
        ])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка при показе товаров для редактирования: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


@router.callback_query(F.data == "admin_add_product")
async def start_adding_product(callback: CallbackQuery, state: FSMContext):
    """Начать добавление товара"""
    try:
        if not is_admin(callback.from_user.id):
            await callback.answer("❌ Нет прав доступа", show_alert=True)
            return
        
        await callback.message.edit_text(
            "📝 <b>Добавление товара</b>\n\n"
            "Введите название товара:",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_cancel")],
                [InlineKeyboardButton(text="🏠 В меню", callback_data="go_to_main_menu")]
            ])
        )
        
        await state.set_state(AdminStates.adding_product_name)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка при добавлении товара: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


@router.message(AdminStates.adding_product_name)
async def process_product_name(message: Message, state: FSMContext):
    """Обработать название товара"""
    try:
        if not is_admin(message.from_user.id):
            await message.answer("❌ Нет прав доступа")
            return
        
        name = message.text.strip()
        if len(name) < 3:
            await message.answer("❌ Название должно содержать минимум 3 символа. Попробуйте еще раз:")
            return
        
        await state.update_data(name=name)
        
        await message.answer(
            "📝 Введите описание товара:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_cancel")]
            ])
        )
        
        await state.set_state(AdminStates.adding_product_description)
        
    except Exception as e:
        logger.error(f"Ошибка при обработке названия товара: {e}")
        await message.answer("❌ Ошибка при обработке данных")


@router.message(AdminStates.adding_product_description)
async def process_product_description(message: Message, state: FSMContext):
    """Обработать описание товара"""
    try:
        if not is_admin(message.from_user.id):
            await message.answer("❌ Нет прав доступа")
            return
        
        description = message.text.strip()
        if len(description) < 10:
            await message.answer("❌ Описание должно содержать минимум 10 символов. Попробуйте еще раз:")
            return
        
        await state.update_data(description=description)
        
        await message.answer(
            "💰 Введите цену товара (только число):",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_cancel")]
            ])
        )
        
        await state.set_state(AdminStates.adding_product_price)
        
    except Exception as e:
        logger.error(f"Ошибка при обработке описания товара: {e}")
        await message.answer("❌ Ошибка при обработке данных")


@router.message(AdminStates.adding_product_price)
async def process_product_price(message: Message, state: FSMContext):
    """Обработать цену товара"""
    try:
        if not is_admin(message.from_user.id):
            await message.answer("❌ Нет прав доступа")
            return
        
        try:
            price = float(message.text.strip())
            if price <= 0:
                await message.answer("❌ Цена должна быть больше 0. Попробуйте еще раз:")
                return
        except ValueError:
            await message.answer("❌ Введите корректную цену (число). Попробуйте еще раз:")
            return
        
        await state.update_data(price=price)
        
        # Получаем категории
        categories = await product_repo.get_categories()
        
        if not categories:
            await message.answer("❌ Нет доступных категорий. Сначала создайте категории.")
            await state.clear()
            return
        
        # Создаем клавиатуру с категориями
        keyboard_buttons = []
        for category in categories:
            keyboard_buttons.append([
                InlineKeyboardButton(text=category.name, callback_data=f"category_{category.id}")
            ])
        keyboard_buttons.append([InlineKeyboardButton(text="❌ Отмена", callback_data="admin_cancel")])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        await message.answer(
            "📂 Выберите категорию товара:",
            reply_markup=keyboard
        )
        
        await state.set_state(AdminStates.adding_product_category)
        
    except Exception as e:
        logger.error(f"Ошибка при обработке цены товара: {e}")
        await message.answer("❌ Ошибка при обработке данных")


@router.callback_query(AdminStates.adding_product_category, F.data.startswith("category_"))
async def process_product_category(callback: CallbackQuery, state: FSMContext):
    """Обработать выбранную категорию"""
    try:
        if not is_admin(callback.from_user.id):
            await callback.answer("❌ Нет прав доступа", show_alert=True)
            return
        
        category_id = int(callback.data.split("_")[1])
        await state.update_data(category_id=category_id)
        
        await callback.message.edit_text(
            "📦 Введите количество товара на складе:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_cancel")]
            ])
        )
        
        await state.set_state(AdminStates.adding_product_stock)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка при обработке категории: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


@router.message(AdminStates.adding_product_stock)
async def process_product_stock(message: Message, state: FSMContext):
    """Обработать количество товара"""
    try:
        if not is_admin(message.from_user.id):
            await message.answer("❌ Нет прав доступа")
            return
        
        try:
            stock = int(message.text.strip())
            if stock < 0:
                await message.answer("❌ Количество не может быть отрицательным. Попробуйте еще раз:")
                return
        except ValueError:
            await message.answer("❌ Введите корректное количество (целое число). Попробуйте еще раз:")
            return
        
        await state.update_data(stock=stock)
        
        await message.answer(
            "🖼️ Отправьте фото товара или введите 'пропустить' для добавления без фото:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_cancel")]
            ])
        )
        
        await state.set_state(AdminStates.adding_product_image)
        
    except Exception as e:
        logger.error(f"Ошибка при обработке количества товара: {e}")
        await message.answer("❌ Ошибка при обработке данных")


@router.message(AdminStates.adding_product_image)
async def process_product_image(message: Message, state: FSMContext):
    """Обработать фото товара"""
    try:
        if not is_admin(message.from_user.id):
            await message.answer("❌ Нет прав доступа")
            return
        
        image_url = None
        
        if message.photo:
            # Получаем ID самого большого фото
            image_url = message.photo[-1].file_id
        elif message.text and message.text.lower() != "пропустить":
            await message.answer("❌ Отправьте фото или введите 'пропустить'")
            return
        
        data = await state.get_data()
        
        # Создаем товар
        product = Product(
            id=0,  # Будет установлен при создании
            name=data['name'],
            description=data['description'],
            price=data['price'],
            category_id=data['category_id'],
            image_url=image_url,
            stock=data['stock'],
            is_active=True
        )
        
        # Сохраняем товар
        created_product = await product_repo.add_product(product)
        
        await message.answer(
            f"✅ <b>Товар успешно добавлен!</b>\n\n"
            f"📦 <b>Название:</b> {created_product.name}\n"
            f"💰 <b>Цена:</b> {created_product.price}{config.CURRENCY}\n"
            f"📦 <b>Количество:</b> {created_product.stock} шт.\n"
            f"🆔 <b>ID:</b> {created_product.id}",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔧 Админ-панель", callback_data="admin_panel")],
                [InlineKeyboardButton(text="🏠 В меню", callback_data="go_to_main_menu")]
            ])
        )
        
        await state.clear()
        
    except Exception as e:
        logger.error(f"Ошибка при добавлении товара: {e}")
        await message.answer("❌ Ошибка при добавлении товара")


@router.callback_query(F.data == "admin_orders")
async def show_orders(callback: CallbackQuery):
    """Показать заказы"""
    try:
        if not is_admin(callback.from_user.id):
            await callback.answer("❌ Нет прав доступа", show_alert=True)
            return
        
        orders = await order_repo.get_orders()
        
        if not orders:
            await callback.message.edit_text(
                "📋 Заказов пока нет.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔧 Админ-панель", callback_data="admin_panel")],
                    [InlineKeyboardButton(text="🏠 В меню", callback_data="go_to_main_menu")]
                ])
            )
            return
        
        text = "📋 <b>Заказы:</b>\n\n"
        
        for order in orders[:10]:  # Показываем только первые 10 заказов
            status_text = config.ORDER_STATUSES.get(order.status, order.status)
            text += f"📦 <b>Заказ #{order.id}</b>\n"
            text += f"👤 Пользователь: {order.user_id}\n"
            text += f"💰 Сумма: {order.total_amount}{config.CURRENCY}\n"
            text += f"📊 Статус: {status_text}\n"
            moscow_time = order.created_at.astimezone(config.MOSCOW_TZ)
            text += f"📅 Дата: {moscow_time.strftime('%d.%m.%Y %H:%M')}\n\n"
        
        keyboard_buttons = []
        for order in orders[:5]:  # Кнопки для изменения статуса первых 5 заказов
            keyboard_buttons.append([
                InlineKeyboardButton(
                    text=f"📦 #{order.id}",
                    callback_data=f"order_details_{order.id}"
                )
            ])
        
        keyboard_buttons.append([
            InlineKeyboardButton(text="🔧 Админ-панель", callback_data="admin_panel"),
            InlineKeyboardButton(text="🏠 В меню", callback_data="go_to_main_menu")
        ])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка при показе заказов: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


@router.callback_query(F.data.startswith("order_details_"))
async def show_order_details(callback: CallbackQuery):
    """Показать детали заказа"""
    try:
        if not is_admin(callback.from_user.id):
            await callback.answer("❌ Нет прав доступа", show_alert=True)
            return
        
        order_id = int(callback.data.split("_")[2])
        orders = await order_repo.get_orders()
        order = next((o for o in orders if o.id == order_id), None)
        
        if not order:
            await callback.answer("❌ Заказ не найден", show_alert=True)
            return
        
        # Получаем позиции заказа
        order_items = await order_repo.get_order_items(order_id)
        
        text = f"📦 <b>Заказ #{order.id}</b>\n\n"
        text += f"👤 <b>Пользователь:</b> {order.user_id}\n"
        text += f"📱 <b>Телефон:</b> {order.phone}\n"
        text += f"🏠 <b>Адрес:</b> {order.delivery_address}\n"
        text += f"🚚 <b>Доставка:</b> {config.DELIVERY_METHODS.get(order.delivery_method, order.delivery_method)}\n"
        text += f"📊 <b>Статус:</b> {config.ORDER_STATUSES.get(order.status, order.status)}\n"
        moscow_time = order.created_at.astimezone(config.MOSCOW_TZ)
        text += f"📅 <b>Дата:</b> {moscow_time.strftime('%d.%m.%Y %H:%M')}\n\n"
        
        text += f"📦 <b>Товары:</b>\n"
        for item in order_items:
            product = await product_repo.get_product(item.product_id)
            if product:
                text += f"• {product.name} x{item.quantity} = {item.price * item.quantity}{config.CURRENCY}\n"
        
        text += f"\n💰 <b>Итого: {order.total_amount}{config.CURRENCY}</b>"
        
        # Кнопки для изменения статуса
        keyboard_buttons = []
        for status_key, status_name in config.ORDER_STATUSES.items():
            if status_key != order.status:
                keyboard_buttons.append([
                    InlineKeyboardButton(
                        text=f"📊 {status_name}",
                        callback_data=f"change_status_{order_id}_{status_key}"
                    )
                ])
        
        keyboard_buttons.append([
            InlineKeyboardButton(text="🔙 Назад к заказам", callback_data="admin_orders"),
            InlineKeyboardButton(text="🏠 В меню", callback_data="go_to_main_menu")
        ])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка при показе деталей заказа: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


@router.callback_query(F.data.startswith("change_status_"))
async def change_order_status(callback: CallbackQuery):
    """Изменить статус заказа"""
    try:
        if not is_admin(callback.from_user.id):
            await callback.answer("❌ Нет прав доступа", show_alert=True)
            return
        
        parts = callback.data.split("_")
        order_id = int(parts[2])
        new_status = parts[3]
        
        await order_repo.update_order_status(order_id, new_status)
        
        status_name = config.ORDER_STATUSES.get(new_status, new_status)
        await callback.answer(f"✅ Статус заказа #{order_id} изменен на: {status_name}")
        
        # Обновляем отображение
        await show_order_details(callback)
        
    except Exception as e:
        logger.error(f"Ошибка при изменении статуса заказа: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


@router.callback_query(F.data == "admin_cancel")
async def admin_cancel(callback: CallbackQuery, state: FSMContext):
    """Отменить действие в админ-панели"""
    try:
        await state.clear()
        await callback.message.edit_text(
            "❌ Действие отменено.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔧 Админ-панель", callback_data="admin_panel")],
                [InlineKeyboardButton(text="🏠 В меню", callback_data="go_to_main_menu")]
            ])
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка при отмене: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


@router.callback_query(F.data == "admin_panel")
async def admin_panel_callback(callback: CallbackQuery):
    """Вернуться в админ-панель"""
    try:
        if not is_admin(callback.from_user.id):
            await callback.answer("❌ Нет прав доступа", show_alert=True)
            return
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Добавить товар", callback_data="admin_add_product")],
            [InlineKeyboardButton(text="✏️ Редактировать товары", callback_data="admin_edit_products")],
            [InlineKeyboardButton(text="📋 Заказы", callback_data="admin_orders")],
            [InlineKeyboardButton(text="🏠 В меню", callback_data="go_to_main_menu")]
        ])
        
        await callback.message.edit_text(
            "🔧 <b>Админ-панель</b>\n\n"
            "Выберите действие:",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка при возврате в админ-панель: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


@router.callback_query(F.data.startswith("edit_product_"))
async def edit_product_callback(callback: CallbackQuery, state: FSMContext):
    """Обработчик редактирования товара"""
    try:
        if not is_admin(callback.from_user.id):
            await callback.answer("❌ Нет прав доступа", show_alert=True)
            return
        
        product_id = int(callback.data.split("_")[2])
        product = await product_repo.get_product(product_id)
        
        if not product:
            await callback.answer("❌ Товар не найден", show_alert=True)
            return
        
        await state.update_data(editing_product_id=product_id)
        
        text = f"✏️ <b>Редактирование товара:</b>\n\n"
        text += f"🆔 <b>ID:</b> {product.id}\n"
        text += f"📦 <b>Название:</b> {product.name}\n"
        text += f"📝 <b>Описание:</b> {product.description}\n"
        text += f"💰 <b>Цена:</b> {product.price}{config.CURRENCY}\n"
        text += f"📦 <b>Количество:</b> {product.stock} шт.\n\n"
        text += f"Что хотите изменить?"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📦 Название", callback_data="edit_field_name")],
            [InlineKeyboardButton(text="📝 Описание", callback_data="edit_field_description")],
            [InlineKeyboardButton(text="💰 Цена", callback_data="edit_field_price")],
            [InlineKeyboardButton(text="📦 Количество", callback_data="edit_field_stock")],
            [InlineKeyboardButton(text="🏠 В меню", callback_data="go_to_main_menu")]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка при редактировании товара: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


@router.callback_query(F.data.startswith("edit_field_"))
async def edit_field_callback(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора поля для редактирования"""
    try:
        if not is_admin(callback.from_user.id):
            await callback.answer("❌ Нет прав доступа", show_alert=True)
            return
        
        field = callback.data.split("_")[2]  # name, description, price, stock
        
        field_names = {
            "name": "название",
            "description": "описание", 
            "price": "цену",
            "stock": "количество"
        }
        
        await state.update_data(editing_field=field)
        
        text = f"✏️ Введите новое {field_names[field]}:"
        
        if field == "price":
            text += "\n\n💰 Введите цену (только число):"
        elif field == "stock":
            text += "\n\n📦 Введите количество (целое число):"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_cancel")]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await state.set_state(AdminStates.editing_product_value)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка при выборе поля: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


@router.message(AdminStates.editing_product_value)
async def process_edit_value(message: Message, state: FSMContext):
    """Обработка нового значения поля"""
    try:
        if not is_admin(message.from_user.id):
            await message.answer("❌ Нет прав доступа")
            return
        
        data = await state.get_data()
        product_id = data['editing_product_id']
        field = data['editing_field']
        new_value = message.text.strip()
        
        # Валидация в зависимости от поля
        if field == "price":
            try:
                new_value = float(new_value)
                if new_value <= 0:
                    await message.answer("❌ Цена должна быть больше 0. Попробуйте еще раз:")
                    return
            except ValueError:
                await message.answer("❌ Введите корректную цену (число). Попробуйте еще раз:")
                return
        elif field == "stock":
            try:
                new_value = int(new_value)
                if new_value < 0:
                    await message.answer("❌ Количество не может быть отрицательным. Попробуйте еще раз:")
                    return
            except ValueError:
                await message.answer("❌ Введите корректное количество (целое число). Попробуйте еще раз:")
                return
        elif field in ["name", "description"]:
            if len(new_value) < 3:
                await message.answer("❌ Поле должно содержать минимум 3 символа. Попробуйте еще раз:")
                return
        
        # Обновляем товар в базе данных
        product = await product_repo.get_product(product_id)
        if not product:
            await message.answer("❌ Товар не найден")
            await state.clear()
            return
        
        # Создаем обновленный товар
        updated_product = Product(
            id=product.id,
            name=new_value if field == "name" else product.name,
            description=new_value if field == "description" else product.description,
            price=new_value if field == "price" else product.price,
            category_id=product.category_id,
            image_url=product.image_url,
            stock=new_value if field == "stock" else product.stock,
            is_active=product.is_active
        )
        
        await product_repo.update_product(updated_product)
        
        field_names = {
            "name": "название",
            "description": "описание",
            "price": "цена", 
            "stock": "количество"
        }
        
        await message.answer(
            f"✅ <b>Товар обновлён!</b>\n\n"
            f"📦 <b>ID:</b> {product_id}\n"
            f"✏️ <b>Изменено:</b> {field_names[field]}\n"
            f"🆕 <b>Новое значение:</b> {new_value}",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✏️ Редактировать еще", callback_data=f"edit_product_{product_id}")],
                [InlineKeyboardButton(text="🏠 В меню", callback_data="go_to_main_menu")]
            ])
        )
        
        await state.clear()
        
    except Exception as e:
        logger.error(f"Ошибка при обновлении товара: {e}")
        await message.answer("❌ Ошибка при обновлении товара")


@router.callback_query(F.data.startswith("change_order_status_"))
async def change_order_status_callback(callback: CallbackQuery):
    """Обработчик изменения статуса заказа"""
    try:
        if not is_admin(callback.from_user.id):
            await callback.answer("❌ Нет прав доступа", show_alert=True)
            return
        
        order_id = int(callback.data.split("_")[3])
        
        # Получаем заказ
        orders = await order_repo.get_orders()
        order = next((o for o in orders if o.id == order_id), None)
        
        if not order:
            await callback.answer("❌ Заказ не найден", show_alert=True)
            return
        
        text = f"📦 <b>Заказ №{order_id}</b>\n\n"
        text += f"📊 <b>Текущий статус:</b> {config.ORDER_STATUSES.get(order.status, order.status)}\n\n"
        text += f"Выберите новый статус:"
        
        keyboard_buttons = []
        for status_key, status_name in config.ORDER_STATUSES.items():
            if status_key != order.status:  # Не показываем текущий статус
                keyboard_buttons.append([
                    InlineKeyboardButton(
                        text=f"📊 {status_name}",
                        callback_data=f"set_status_{order_id}_{status_key}"
                    )
                ])
        
        keyboard_buttons.append([
            InlineKeyboardButton(text="🏠 В меню", callback_data="go_to_main_menu")
        ])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка при изменении статуса заказа: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


@router.callback_query(F.data.startswith("set_status_"))
async def set_order_status_callback(callback: CallbackQuery):
    """Обработчик установки нового статуса заказа"""
    try:
        if not is_admin(callback.from_user.id):
            await callback.answer("❌ Нет прав доступа", show_alert=True)
            return
        
        parts = callback.data.split("_")
        order_id = int(parts[2])
        new_status = parts[3]
        
        # Обновляем статус в базе данных
        await order_repo.update_order_status(order_id, new_status)
        
        status_name = config.ORDER_STATUSES.get(new_status, new_status)
        
        await callback.answer(f"✅ Статус заказа №{order_id} изменён на: {status_name}")
        
        # Возвращаемся к списку заказов
        await orders_command(callback.message)
        
    except Exception as e:
        logger.error(f"Ошибка при установке статуса заказа: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)
