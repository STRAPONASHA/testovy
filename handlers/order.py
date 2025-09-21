"""
Обработчики для оформления заказов
"""
import logging
from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.repository import OrderRepository, CartRepository, ProductRepository, UserRepository
from database.models import Order, OrderItem, User
import config

logger = logging.getLogger(__name__)
router = Router()

# Репозитории
order_repo = OrderRepository()
cart_repo = CartRepository()
product_repo = ProductRepository()
user_repo = UserRepository()


class OrderStates(StatesGroup):
    """Состояния для оформления заказа"""
    waiting_name = State()
    waiting_phone = State()
    waiting_address = State()
    waiting_delivery_method = State()
    waiting_delivery_time = State()
    waiting_payment_method = State()
    waiting_comment = State()
    confirming_order = State()


@router.callback_query(F.data == "checkout")
async def start_checkout(callback: CallbackQuery, state: FSMContext):
    """Начать оформление заказа"""
    try:
        user_id = callback.from_user.id
        
        # Проверяем, что корзина не пуста
        cart_items = await cart_repo.get_cart_items(user_id)
        if not cart_items:
            await callback.answer("🛒 Корзина пуста", show_alert=True)
            return
        
        # Получаем данные пользователя
        user = await user_repo.get_user(user_id)
        
        # Если у пользователя уже есть имя, переходим к телефону
        if user and user.first_name:
            await state.update_data(name=user.first_name)
            await ask_phone(callback, state)
        else:
            await callback.message.edit_text(
                "📝 Для оформления заказа нам нужны ваши данные.\n\n"
                "Введите ваше имя:",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_order")]
                ])
            )
            await state.set_state(OrderStates.waiting_name)
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка при начале оформления заказа: {e}")
        await callback.answer("❌ Ошибка при оформлении заказа", show_alert=True)


@router.message(OrderStates.waiting_name)
async def process_name(message: Message, state: FSMContext):
    """Обработать введенное имя"""
    try:
        name = message.text.strip()
        if len(name) < 2:
            await message.answer("❌ Имя должно содержать минимум 2 символа. Попробуйте еще раз:")
            return
        
        await state.update_data(name=name)
        await ask_phone(message, state)
        
    except Exception as e:
        logger.error(f"Ошибка при обработке имени: {e}")
        await message.answer("❌ Ошибка при обработке данных. Попробуйте еще раз.")


async def ask_phone(callback_or_message, state: FSMContext):
    """Спросить номер телефона"""
    try:
        user_id = callback_or_message.from_user.id
        user = await user_repo.get_user(user_id)
        
        # Если у пользователя уже есть телефон, переходим к адресу
        if user and user.phone:
            await state.update_data(phone=user.phone)
            await ask_address(callback_or_message, state)
        else:
            text = "📱 Введите ваш номер телефона:"
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_order")]
            ])
            
            if isinstance(callback_or_message, CallbackQuery):
                await callback_or_message.message.edit_text(text, reply_markup=keyboard)
            else:
                await callback_or_message.answer(text, reply_markup=keyboard)
            
            await state.set_state(OrderStates.waiting_phone)
        
    except Exception as e:
        logger.error(f"Ошибка при запросе телефона: {e}")


@router.message(OrderStates.waiting_phone)
async def process_phone(message: Message, state: FSMContext):
    """Обработать введенный телефон"""
    try:
        phone = message.text.strip()
        # Простая валидация телефона
        if len(phone) < 10 or not phone.replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '').isdigit():
            await message.answer("❌ Введите корректный номер телефона. Попробуйте еще раз:")
            return
        
        await state.update_data(phone=phone)
        await finish_order(message, state)
        
    except Exception as e:
        logger.error(f"Ошибка при обработке телефона: {e}")
        await message.answer("❌ Ошибка при обработке данных. Попробуйте еще раз.")


async def ask_address(callback_or_message, state: FSMContext):
    """Спросить адрес доставки"""
    try:
        user_id = callback_or_message.from_user.id
        user = await user_repo.get_user(user_id)
        
        # Если у пользователя уже есть адрес, переходим к способу доставки
        if user and user.address:
            await state.update_data(address=user.address)
            await ask_delivery_method(callback_or_message, state)
        else:
            text = "🏠 Введите адрес доставки:"
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_order")]
            ])
            
            if isinstance(callback_or_message, CallbackQuery):
                await callback_or_message.message.edit_text(text, reply_markup=keyboard)
            else:
                await callback_or_message.answer(text, reply_markup=keyboard)
            
            await state.set_state(OrderStates.waiting_address)
        
    except Exception as e:
        logger.error(f"Ошибка при запросе адреса: {e}")


@router.message(OrderStates.waiting_address)
async def process_address(message: Message, state: FSMContext):
    """Обработать введенный адрес"""
    try:
        address = message.text.strip()
        if len(address) < 10:
            await message.answer("❌ Адрес должен содержать минимум 10 символов. Попробуйте еще раз:")
            return
        
        await state.update_data(address=address)
        await ask_delivery_method(message, state)
        
    except Exception as e:
        logger.error(f"Ошибка при обработке адреса: {e}")
        await message.answer("❌ Ошибка при обработке данных. Попробуйте еще раз.")


async def ask_delivery_method(callback_or_message, state: FSMContext):
    """Спросить способ доставки"""
    try:
        text = "🚚 Выберите способ доставки:"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🚚 Доставка (+200₽)", callback_data="delivery_delivery")],
            [InlineKeyboardButton(text="🏪 Самовывоз", callback_data="delivery_pickup")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_order")]
        ])
        
        if isinstance(callback_or_message, CallbackQuery):
            await callback_or_message.message.edit_text(text, reply_markup=keyboard)
        else:
            await callback_or_message.answer(text, reply_markup=keyboard)
        
        await state.set_state(OrderStates.waiting_delivery_method)
        
    except Exception as e:
        logger.error(f"Ошибка при запросе способа доставки: {e}")


@router.callback_query(F.data.startswith("delivery_"))
async def process_delivery_method(callback: CallbackQuery, state: FSMContext):
    """Обработать выбранный способ доставки"""
    try:
        delivery_method = callback.data.split("_")[1]
        await state.update_data(delivery_method=delivery_method)
        
        # Переходим к выбору времени доставки
        await ask_delivery_time(callback, state)
        
    except Exception as e:
        logger.error(f"Ошибка при обработке способа доставки: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


async def ask_delivery_time(callback_or_message, state: FSMContext):
    """Спросить время доставки"""
    try:
        data = await state.get_data()
        delivery_method = data.get('delivery_method', 'delivery')
        
        if delivery_method == 'pickup':
            text = "🕐 Выберите удобное время для самовывоза:"
        else:
            text = "🕐 Выберите удобное время для доставки:"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🌅 9:00-12:00", callback_data="time_morning"),
                InlineKeyboardButton(text="☀️ 12:00-15:00", callback_data="time_afternoon")
            ],
            [
                InlineKeyboardButton(text="🌇 15:00-18:00", callback_data="time_evening"),
                InlineKeyboardButton(text="🌃 18:00-21:00", callback_data="time_night")
            ],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_order")]
        ])
        
        if isinstance(callback_or_message, CallbackQuery):
            await callback_or_message.message.edit_text(text, reply_markup=keyboard)
        else:
            await callback_or_message.answer(text, reply_markup=keyboard)
        
        await state.set_state(OrderStates.waiting_delivery_time)
        
    except Exception as e:
        logger.error(f"Ошибка при запросе времени доставки: {e}")


@router.callback_query(F.data.startswith("time_"))
async def process_delivery_time(callback: CallbackQuery, state: FSMContext):
    """Обработать выбранное время доставки"""
    try:
        time_slot = callback.data.split("_")[1]
        time_mapping = {
            'morning': '9:00-12:00',
            'afternoon': '12:00-15:00',
            'evening': '15:00-18:00',
            'night': '18:00-21:00'
        }
        
        await state.update_data(delivery_time=time_mapping.get(time_slot, '9:00-12:00'))
        
        # Переходим к выбору способа оплаты
        await ask_payment_method(callback, state)
        
    except Exception as e:
        logger.error(f"Ошибка при обработке времени доставки: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


async def ask_payment_method(callback_or_message, state: FSMContext):
    """Спросить способ оплаты"""
    try:
        text = "💳 Выберите способ оплаты:"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💳 Картой онлайн", callback_data="payment_card")],
            [InlineKeyboardButton(text="💵 Наличными", callback_data="payment_cash")],
            [InlineKeyboardButton(text="📱 СБП/QR-код", callback_data="payment_qr")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_order")]
        ])
        
        if isinstance(callback_or_message, CallbackQuery):
            await callback_or_message.message.edit_text(text, reply_markup=keyboard)
        else:
            await callback_or_message.answer(text, reply_markup=keyboard)
        
        await state.set_state(OrderStates.waiting_payment_method)
        
    except Exception as e:
        logger.error(f"Ошибка при запросе способа оплаты: {e}")


@router.callback_query(F.data.startswith("payment_"))
async def process_payment_method(callback: CallbackQuery, state: FSMContext):
    """Обработать выбранный способ оплаты"""
    try:
        payment_method = callback.data.split("_")[1]
        payment_mapping = {
            'card': 'Картой онлайн',
            'cash': 'Наличными',
            'qr': 'СБП/QR-код'
        }
        
        await state.update_data(payment_method=payment_mapping.get(payment_method, 'Наличными'))
        
        # Переходим к комментарию
        await ask_comment(callback, state)
        
    except Exception as e:
        logger.error(f"Ошибка при обработке способа оплаты: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


async def ask_comment(callback_or_message, state: FSMContext):
    """Спросить комментарий к заказу"""
    try:
        text = "💬 Добавьте комментарий к заказу (необязательно):"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➡️ Пропустить", callback_data="comment_skip")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_order")]
        ])
        
        if isinstance(callback_or_message, CallbackQuery):
            await callback_or_message.message.edit_text(text, reply_markup=keyboard)
        else:
            await callback_or_message.answer(text, reply_markup=keyboard)
        
        await state.set_state(OrderStates.waiting_comment)
        
    except Exception as e:
        logger.error(f"Ошибка при запросе комментария: {e}")


@router.callback_query(F.data == "comment_skip")
async def skip_comment(callback: CallbackQuery, state: FSMContext):
    """Пропустить комментарий"""
    try:
        await state.update_data(comment="")
        await confirm_order(callback, state)
    except Exception as e:
        logger.error(f"Ошибка при пропуске комментария: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


@router.message(OrderStates.waiting_comment)
async def process_comment(message: Message, state: FSMContext):
    """Обработать введенный комментарий"""
    try:
        comment = message.text.strip()
        await state.update_data(comment=comment)
        await confirm_order(message, state)
        
    except Exception as e:
        logger.error(f"Ошибка при обработке комментария: {e}")
        await message.answer("❌ Ошибка при обработке данных. Попробуйте еще раз.")


async def confirm_order(callback_or_message, state: FSMContext):
    """Подтвердить заказ"""
    try:
        user_id = callback_or_message.from_user.id
        data = await state.get_data()
        
        # Получаем товары из корзины
        cart_items = await cart_repo.get_cart_items(user_id)
        
        if not cart_items:
            await callback_or_message.answer("🛒 Корзина пуста")
            await state.clear()
            return
        
        # Подсчитываем общую сумму
        total_amount = 0
        order_text = f"📋 <b>Подтверждение заказа</b>\n\n"
        order_text += f"👤 <b>Имя:</b> {data['name']}\n"
        order_text += f"📱 <b>Телефон:</b> {data['phone']}\n"
        order_text += f"🏠 <b>Адрес:</b> {data['address']}\n"
        order_text += f"🚚 <b>Доставка:</b> {config.DELIVERY_METHODS[data['delivery_method']]}\n"
        order_text += f"🕐 <b>Время:</b> {data.get('delivery_time', 'Не указано')}\n"
        order_text += f"💳 <b>Оплата:</b> {data.get('payment_method', 'Наличными')}\n"
        
        if data.get('comment'):
            order_text += f"💬 <b>Комментарий:</b> {data['comment']}\n"
        
        order_text += f"\n📦 <b>Товары:</b>\n"
        
        for item in cart_items:
            product = await product_repo.get_product(item.product_id)
            if product:
                item_total = product.price * item.quantity
                total_amount += item_total
                order_text += f"• {product.name} x{item.quantity} = {item_total}{config.CURRENCY}\n"
        
        # Добавляем стоимость доставки
        if data['delivery_method'] == 'delivery':
            total_amount += 200
        
        order_text += f"\n💰 <b>Итого: {total_amount}{config.CURRENCY}</b>"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Подтвердить заказ", callback_data="confirm_order")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_order")]
        ])
        
        if isinstance(callback_or_message, CallbackQuery):
            await callback_or_message.message.edit_text(
                order_text,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        else:
            await callback_or_message.answer(
                order_text,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        
        await state.set_state(OrderStates.confirming_order)
        
    except Exception as e:
        logger.error(f"Ошибка при подтверждении заказа: {e}")


@router.callback_query(F.data == "confirm_order")
async def process_order_confirmation(callback: CallbackQuery, state: FSMContext):
    """Обработать подтверждение заказа"""
    try:
        user_id = callback.from_user.id
        data = await state.get_data()
        
        # Получаем товары из корзины
        cart_items = await cart_repo.get_cart_items(user_id)
        
        # Подсчитываем общую сумму
        total_amount = 0
        order_items = []
        
        for item in cart_items:
            product = await product_repo.get_product(item.product_id)
            if product:
                item_total = product.price * item.quantity
                total_amount += item_total
                order_items.append(OrderItem(
                    id=0,  # Будет установлен при создании
                    order_id=0,  # Будет установлен при создании
                    product_id=product.id,
                    quantity=item.quantity,
                    price=product.price
                ))
        
        # Добавляем стоимость доставки
        if data['delivery_method'] == 'delivery':
            total_amount += 200
        
        # Создаем заказ
        order = Order(
            id=0,  # Будет установлен при создании
            user_id=user_id,
            status='pending',
            total_amount=total_amount,
            delivery_method=data['delivery_method'],
            delivery_address=data['address'],
            phone=data['phone'],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Сохраняем заказ в базу данных
        created_order = await order_repo.create_order(order, order_items)
        
        # Обновляем данные пользователя
        user = await user_repo.get_user(user_id)
        if user:
            user.first_name = data['name']
            user.phone = data['phone']
            user.address = data['address']
            await user_repo.update_user(user)
        
        # Очищаем корзину
        await cart_repo.clear_cart(user_id)
        
        # Отправляем подтверждение
        await callback.message.edit_text(
            f"✅ <b>Заказ успешно оформлен!</b>\n\n"
            f"📋 <b>Номер заказа:</b> #{created_order.id}\n"
            f"💰 <b>Сумма:</b> {total_amount}{config.CURRENCY}\n\n"
            f"Мы свяжемся с вами в ближайшее время для подтверждения заказа.\n\n"
            f"Спасибо за покупку! 🛍️",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🛍️ Продолжить покупки", callback_data="go_to_catalog")],
                [InlineKeyboardButton(text="🏠 В меню", callback_data="go_to_main_menu")]
            ])
        )
        
        await state.clear()
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка при создании заказа: {e}")
        await callback.answer("❌ Ошибка при создании заказа", show_alert=True)


@router.callback_query(F.data == "cancel_order")
async def cancel_order(callback: CallbackQuery, state: FSMContext):
    """Отменить оформление заказа"""
    try:
        await state.clear()
        
        await callback.message.edit_text(
            "❌ Оформление заказа отменено.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🛒 Корзина", callback_data="view_cart")],
                [
                    InlineKeyboardButton(text="🛍️ Каталог", callback_data="go_to_catalog"),
                    InlineKeyboardButton(text="🏠 В меню", callback_data="go_to_main_menu")
                ]
            ])
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка при отмене заказа: {e}")


async def finish_order(callback_or_message, state: FSMContext):
    """Завершить заказ - простое сообщение"""
    try:
        user_id = callback_or_message.from_user.id
        data = await state.get_data()
        
        # Получаем товары из корзины
        cart_items = await cart_repo.get_cart_items(user_id)
        
        if not cart_items:
            await callback_or_message.answer("🛒 Корзина пуста")
            await state.clear()
            return
        
        # Подсчитываем общую сумму
        total_amount = 0
        order_text = f"📋 <b>Ваш заказ принят!</b>\n\n"
        order_text += f"👤 <b>Имя:</b> {data['name']}\n"
        order_text += f"📱 <b>Телефон:</b> {data['phone']}\n\n"
        order_text += f"📦 <b>Товары:</b>\n"
        
        for item in cart_items:
            product = await product_repo.get_product(item.product_id)
            if product:
                item_total = product.price * item.quantity
                total_amount += item_total
                order_text += f"• {product.name} x{item.quantity} = {item_total}{config.CURRENCY}\n"
        
        order_text += f"\n💰 <b>Итого: {total_amount}{config.CURRENCY}</b>\n\n"
        order_text += f"✅ <b>Спасибо за заказ!</b>\n"
        order_text += f"Мы свяжемся с вами в ближайшее время для подтверждения заказа.\n\n"
        order_text += f"🛍️ <b>Спасибо за покупку!</b>"
        
        # Создаем заказ в базе данных
        order = Order(
            id=0,
            user_id=user_id,
            status='pending',
            total_amount=total_amount,
            delivery_method='delivery',
            delivery_address='Будет уточнен',
            phone=data['phone'],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        order_items = []
        for item in cart_items:
            product = await product_repo.get_product(item.product_id)
            if product:
                order_items.append(OrderItem(
                    id=0,
                    order_id=0,
                    product_id=product.id,
                    quantity=item.quantity,
                    price=product.price
                ))
        
        # Сохраняем заказ
        created_order = await order_repo.create_order(order, order_items)
        
        # Обновляем данные пользователя
        user = await user_repo.get_user(user_id)
        if user:
            user.first_name = data['name']
            user.phone = data['phone']
            await user_repo.update_user(user)
        
        # Очищаем корзину
        await cart_repo.clear_cart(user_id)
        
        # Отправляем подтверждение
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛍️ Продолжить покупки", callback_data="go_to_catalog")],
            [InlineKeyboardButton(text="🏠 В меню", callback_data="go_to_main_menu")]
        ])
        
        if isinstance(callback_or_message, CallbackQuery):
            await callback_or_message.message.edit_text(
                order_text,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        else:
            await callback_or_message.answer(
                order_text,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        
        await state.clear()
        if isinstance(callback_or_message, CallbackQuery):
            await callback_or_message.answer()
        
    except Exception as e:
        logger.error(f"Ошибка при завершении заказа: {e}")
        if isinstance(callback_or_message, CallbackQuery):
            await callback_or_message.answer("❌ Ошибка при создании заказа", show_alert=True)
        else:
            await callback_or_message.answer("❌ Ошибка при создании заказа")


@router.message(Command("orders"))
async def show_user_orders(message: Message):
    """Показать заказы пользователя"""
    try:
        user_id = message.from_user.id
        orders = await order_repo.get_orders(user_id)
        
        if not orders:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🛍️ Перейти в каталог", callback_data="go_to_catalog")],
                [InlineKeyboardButton(text="🏠 В меню", callback_data="go_to_main_menu")]
            ])
            
            if hasattr(message, 'edit_text'):
                await message.edit_text("📋 У вас пока нет заказов.", reply_markup=keyboard)
            else:
                await message.answer("📋 У вас пока нет заказов.", reply_markup=keyboard)
            return
        
        text = "📋 <b>Ваши заказы:</b>\n\n"
        
        for order in orders:
            status_text = config.ORDER_STATUSES.get(order.status, order.status)
            text += f"📦 <b>Заказ #{order.id}</b>\n"
            text += f"💰 Сумма: {order.total_amount}{config.CURRENCY}\n"
            text += f"📊 Статус: {status_text}\n"
            text += f"📅 Дата: {order.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛍️ Перейти в каталог", callback_data="go_to_catalog")],
            [InlineKeyboardButton(text="🏠 В меню", callback_data="go_to_main_menu")]
        ])
        
        if hasattr(message, 'edit_text'):
            await message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)
        else:
            await message.answer(text, parse_mode="HTML", reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Ошибка при показе заказов: {e}")
        if hasattr(message, 'edit_text'):
            await message.edit_text("❌ Ошибка при загрузке заказов")
        else:
            await message.answer("❌ Ошибка при загрузке заказов")
