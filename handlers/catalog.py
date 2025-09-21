"""
Обработчики для каталога товаров
"""
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.repository import ProductRepository, UserRepository
from database.models import User
import config

logger = logging.getLogger(__name__)
router = Router()

# Репозитории
product_repo = ProductRepository()
user_repo = UserRepository()


class CatalogStates(StatesGroup):
    """Состояния для каталога"""
    viewing_categories = State()
    viewing_products = State()
    viewing_product = State()


@router.message(Command("catalog"))
async def show_catalog(message: Message, state: FSMContext):
    """Показать каталог товаров"""
    try:
        # Создаем или обновляем пользователя
        user = User(
            id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
        await user_repo.create_user(user)
        
        # Получаем категории
        categories = await product_repo.get_categories()
        
        if not categories:
            await message.answer("📦 Каталог пока пуст. Обратитесь к администратору.")
            return
        
        # Создаем клавиатуру с категориями
        keyboard_buttons = [
            [InlineKeyboardButton(text=f"📂 {category.name}", callback_data=f"category_{category.id}")]
            for category in categories
        ]
        
        # Добавляем кнопку "В меню"
        keyboard_buttons.append([
            InlineKeyboardButton(text="🏠 В меню", callback_data="go_to_main_menu")
        ])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        # Проверяем, это callback или обычное сообщение
        if hasattr(message, 'edit_text'):
            # Это callback, редактируем сообщение
            await message.edit_text(
                f"🛍️ Добро пожаловать в {config.SHOP_NAME}!\n\n"
                "Выберите категорию товаров:",
                reply_markup=keyboard
            )
        else:
            # Это обычное сообщение, отправляем новое
            await message.answer(
                f"🛍️ Добро пожаловать в {config.SHOP_NAME}!\n\n"
                "Выберите категорию товаров:",
                reply_markup=keyboard
            )
        
        await state.set_state(CatalogStates.viewing_categories)
        
    except Exception as e:
        logger.error(f"Ошибка при показе каталога: {e}")
        if hasattr(message, 'edit_text'):
            await message.edit_text("❌ Произошла ошибка при загрузке каталога. Попробуйте позже.")
        else:
            await message.answer("❌ Произошла ошибка при загрузке каталога. Попробуйте позже.")


@router.callback_query(F.data.startswith("category_"))
async def show_products(callback: CallbackQuery, state: FSMContext):
    """Показать товары в категории"""
    try:
        category_id = int(callback.data.split("_")[1])
        # Сохраняем category_id в состоянии для кнопки "Назад"
        await state.update_data(category_id=category_id)
        products = await product_repo.get_products_by_category(category_id)
        
        if not products:
            await callback.message.edit_text(
                "📦 В этой категории пока нет товаров.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Назад к категориям", callback_data="back_to_categories")]
                ])
            )
            return
        
        # Создаем клавиатуру с товарами
        keyboard_buttons = []
        for product in products:
            keyboard_buttons.append([
                InlineKeyboardButton(
                    text=f"{product.name} - {product.price}{config.CURRENCY}",
                    callback_data=f"product_{product.id}"
                )
            ])
        
        # Добавляем кнопки навигации
        keyboard_buttons.append([
            InlineKeyboardButton(text="🔙 Назад к категориям", callback_data="back_to_categories"),
            InlineKeyboardButton(text="🏠 В меню", callback_data="go_to_main_menu")
        ])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        await callback.message.edit_text(
            "📋 Выберите товар:",
            reply_markup=keyboard
        )
        
        await state.set_state(CatalogStates.viewing_products)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка при показе товаров: {e}")
        await callback.answer("❌ Ошибка при загрузке товаров", show_alert=True)


@router.callback_query(F.data.startswith("product_"))
async def show_product(callback: CallbackQuery, state: FSMContext):
    """Показать карточку товара"""
    try:
        product_id = int(callback.data.split("_")[1])
        product = await product_repo.get_product(product_id)
        
        if not product:
            await callback.answer("❌ Товар не найден", show_alert=True)
            return
        
        # Формируем текст карточки товара
        text = f"""
🛍️ <b>{product.name}</b>

📝 <b>Описание:</b>
{product.description}
"""
        
        # Добавляем подробную информацию, если есть
        if product.detailed_description:
            text += f"\n📋 <b>Подробное описание:</b>\n{product.detailed_description}"
        
        if product.brand:
            text += f"\n🏷️ <b>Бренд:</b> {product.brand}"
        
        if product.material:
            text += f"\n🧵 <b>Материал:</b> {product.material}"
        
        if product.country:
            text += f"\n🌍 <b>Страна:</b> {product.country}"
        
        if product.weight:
            text += f"\n⚖️ <b>Вес:</b> {product.weight}"
        
        if product.dimensions:
            text += f"\n📏 <b>Размеры:</b> {product.dimensions}"
        
        text += f"\n\n💰 <b>Цена:</b> {product.price}{config.CURRENCY}"
        text += f"\n📦 <b>В наличии:</b> {product.stock} шт."
        
        # Создаем клавиатуру
        keyboard_buttons = []
        
        # Добавляем кнопки для размеров, если есть
        if product.sizes:
            sizes = [size.strip() for size in product.sizes.split(',')]
            if len(sizes) <= 4:  # Если размеров немного, показываем в одну строку
                size_buttons = [
                    InlineKeyboardButton(text=f"📏 {size}", callback_data=f"select_size_{product.id}_{size}")
                    for size in sizes
                ]
                keyboard_buttons.append(size_buttons)
            else:  # Если размеров много, показываем по 2 в строке
                for i in range(0, len(sizes), 2):
                    row = [
                        InlineKeyboardButton(text=f"📏 {sizes[i]}", callback_data=f"select_size_{product.id}_{sizes[i]}")
                    ]
                    if i + 1 < len(sizes):
                        row.append(InlineKeyboardButton(text=f"📏 {sizes[i+1]}", callback_data=f"select_size_{product.id}_{sizes[i+1]}"))
                    keyboard_buttons.append(row)
        
        # Добавляем кнопки для цветов, если есть
        if product.colors:
            colors = [color.strip() for color in product.colors.split(',')]
            if len(colors) <= 4:  # Если цветов немного, показываем в одну строку
                color_buttons = [
                    InlineKeyboardButton(text=f"🎨 {color}", callback_data=f"select_color_{product.id}_{color}")
                    for color in colors
                ]
                keyboard_buttons.append(color_buttons)
            else:  # Если цветов много, показываем по 2 в строке
                for i in range(0, len(colors), 2):
                    row = [
                        InlineKeyboardButton(text=f"🎨 {colors[i]}", callback_data=f"select_color_{product.id}_{colors[i]}")
                    ]
                    if i + 1 < len(colors):
                        row.append(InlineKeyboardButton(text=f"🎨 {colors[i+1]}", callback_data=f"select_color_{product.id}_{colors[i+1]}"))
                    keyboard_buttons.append(row)
        
        # Основные кнопки
        keyboard_buttons.extend([
            [
                InlineKeyboardButton(text="➕ Добавить в корзину", callback_data=f"add_to_cart_{product.id}"),
                InlineKeyboardButton(text="🛒 Корзина", callback_data="view_cart")
            ],
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_products"),
                InlineKeyboardButton(text="🏠 В меню", callback_data="go_to_main_menu")
            ]
        ])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        # Редактируем сообщение
        await callback.message.edit_text(
            text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
        await state.set_state(CatalogStates.viewing_product)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка при показе товара: {e}")
        await callback.answer("❌ Ошибка при загрузке товара", show_alert=True)


@router.callback_query(F.data == "back_to_categories")
async def back_to_categories(callback: CallbackQuery, state: FSMContext):
    """Вернуться к категориям"""
    try:
        categories = await product_repo.get_categories()
        
        keyboard_buttons = [
            [InlineKeyboardButton(text=f"📂 {category.name}", callback_data=f"category_{category.id}")]
            for category in categories
        ]
        
        # Добавляем кнопку "В меню"
        keyboard_buttons.append([
            InlineKeyboardButton(text="🏠 В меню", callback_data="go_to_main_menu")
        ])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        await callback.message.edit_text(
            f"🛍️ {config.SHOP_NAME}\n\nВыберите категорию товаров:",
            reply_markup=keyboard
        )
        
        await state.set_state(CatalogStates.viewing_categories)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка при возврате к категориям: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


@router.callback_query(F.data == "back_to_products")
async def back_to_products(callback: CallbackQuery, state: FSMContext):
    """Вернуться к товарам"""
    try:
        # Получаем сохраненный category_id из состояния
        data = await state.get_data()
        category_id = data.get('category_id')
        
        if not category_id:
            await callback.answer("❌ Ошибка навигации", show_alert=True)
            return
            
        products = await product_repo.get_products_by_category(category_id)
        
        keyboard_buttons = []
        for product in products:
            keyboard_buttons.append([
                InlineKeyboardButton(
                    text=f"{product.name} - {product.price}{config.CURRENCY}",
                    callback_data=f"product_{product.id}"
                )
            ])
        
        keyboard_buttons.append([
            InlineKeyboardButton(text="🔙 Назад к категориям", callback_data="back_to_categories"),
            InlineKeyboardButton(text="🏠 В меню", callback_data="go_to_main_menu")
        ])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        await callback.message.edit_text(
            "📋 Выберите товар:",
            reply_markup=keyboard
        )
        
        await state.set_state(CatalogStates.viewing_products)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка при возврате к товарам: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)
