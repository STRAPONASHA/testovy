"""
Главный файл Telegram-бота для e-commerce
"""
import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.types import BotCommand

from handlers import catalog, cart, order, admin
from database.repository import DatabaseRepository
import config

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


async def setup_bot_commands(bot: Bot):
    """Настройка команд бота"""
    commands = [
        BotCommand(command="start", description="🚀 Запустить бота"),
        BotCommand(command="catalog", description="🛍️ Каталог товаров"),
        BotCommand(command="cart", description="🛒 Корзина"),
        BotCommand(command="orders", description="📋 Мои заказы"),
        BotCommand(command="admin", description="🔧 Админ-панель"),
        BotCommand(command="help", description="❓ Помощь")
    ]
    await bot.set_my_commands(commands)


async def on_startup(bot: Bot):
    """Действия при запуске бота"""
    try:
        logger.info("Инициализация базы данных...")
        db_repo = DatabaseRepository()
        await db_repo.init_db()
        logger.info("База данных инициализирована")
        
        logger.info("Настройка команд бота...")
        await setup_bot_commands(bot)
        logger.info("Команды бота настроены")
        
        logger.info(f"Бот {config.SHOP_NAME} запущен и готов к работе!")
        
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        raise


async def on_shutdown(bot: Bot):
    """Действия при остановке бота"""
    logger.info("Бот остановлен")


async def main():
    """Главная функция"""
    try:
        # Создаем бота и диспетчер
        bot = Bot(token=config.BOT_TOKEN)
        dp = Dispatcher(storage=MemoryStorage())
        
        # Обработчик команды /start (должен быть ПЕРВЫМ!)
        @dp.message(Command("start"))
        async def start_handler(message, state: FSMContext):
            """Обработчик команды /start"""
            try:
                # Очищаем состояние при старте
                await state.clear()
                
                welcome_text = f"""
🛍️ Добро пожаловать в {config.SHOP_NAME}!

Я помогу вам:
• 🛍️ Просматривать каталог товаров
• 🛒 Управлять корзиной
• 📋 Оформлять заказы
• 📊 Отслеживать статус заказов

Используйте команды меню или кнопки ниже для навигации.
"""
                
                from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🛍️ Каталог товаров", callback_data="go_to_catalog")],
                    [InlineKeyboardButton(text="🛒 Корзина", callback_data="view_cart")],
                    [InlineKeyboardButton(text="📋 Мои заказы", callback_data="view_orders")]
                ])
                
                await message.answer(welcome_text, reply_markup=keyboard)
                
            except Exception as e:
                logger.error(f"Ошибка в обработчике /start: {e}")
                await message.answer("❌ Произошла ошибка. Попробуйте позже.")
        
        # Регистрируем обработчики ПОСЛЕ /start
        dp.include_router(catalog.router)
        dp.include_router(cart.router)
        dp.include_router(order.router)
        dp.include_router(admin.router)
        
        # Обработчик команды /help
        @dp.message(lambda message: message.text == "/help")
        async def help_handler(message):
            """Обработчик команды /help"""
            try:
                help_text = f"""
❓ <b>Справка по использованию бота {config.SHOP_NAME}</b>

<b>Основные команды:</b>
/start - Запустить бота
/catalog - Открыть каталог товаров
/cart - Просмотреть корзину
/orders - Посмотреть мои заказы
/help - Показать эту справку

<b>Как сделать заказ:</b>
1. 🛍️ Выберите товары в каталоге
2. 🛒 Добавьте их в корзину
3. 📝 Оформите заказ, указав контактные данные
4. ✅ Подтвердите заказ

<b>Управление корзиной:</b>
• ➕ Увеличить количество товара
• ➖ Уменьшить количество товара
• ❌ Удалить товар из корзины
• 🗑️ Очистить всю корзину

<b>Поддержка:</b>
Если у вас возникли вопросы, обратитесь к администратору.
"""
                await message.answer(help_text, parse_mode="HTML")
                
            except Exception as e:
                logger.error(f"Ошибка в обработчике /help: {e}")
                await message.answer("❌ Произошла ошибка. Попробуйте позже.")
        
        # Обработчик для кнопки "Каталог товаров"
        @dp.callback_query(lambda c: c.data == "go_to_catalog")
        async def go_to_catalog_callback(callback, state):
            """Перейти в каталог"""
            try:
                from handlers.catalog import show_catalog
                await show_catalog(callback.message, state)
                await callback.answer()
            except Exception as e:
                logger.error(f"Ошибка при переходе в каталог: {e}")
                await callback.answer("❌ Ошибка при загрузке каталога", show_alert=True)
        
        # Обработчик для кнопки "В меню"
        @dp.callback_query(lambda c: c.data == "go_to_main_menu")
        async def go_to_main_menu_callback(callback, state: FSMContext):
            """Вернуться в главное меню"""
            try:
                await state.clear()
                welcome_text = f"""
🛍️ Добро пожаловать в {config.SHOP_NAME}!

Я помогу вам:
• 🛍️ Просматривать каталог товаров
• 🛒 Управлять корзиной
• 📋 Оформлять заказы
• 📊 Отслеживать статус заказов

Используйте команды меню или кнопки ниже для навигации.
"""
                
                from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🛍️ Каталог товаров", callback_data="go_to_catalog")],
                    [InlineKeyboardButton(text="🛒 Корзина", callback_data="view_cart")],
                    [InlineKeyboardButton(text="📋 Мои заказы", callback_data="view_orders")]
                ])
                
                await callback.message.edit_text(welcome_text, reply_markup=keyboard)
                await callback.answer()
                
            except Exception as e:
                logger.error(f"Ошибка при возврате в меню: {e}")
                await callback.answer("❌ Ошибка", show_alert=True)
        
        # Обработчик для кнопки "Мои заказы"
        @dp.callback_query(lambda c: c.data == "view_orders")
        async def view_orders_callback(callback):
            """Показать заказы пользователя"""
            try:
                from handlers.order import show_user_orders
                await show_user_orders(callback.message)
                await callback.answer()
            except Exception as e:
                logger.error(f"Ошибка при показе заказов: {e}")
                await callback.answer("❌ Ошибка при загрузке заказов", show_alert=True)
        
        # Обработчик неизвестных сообщений убран - мешает админским командам
        
        # Обработчик ошибок
        @dp.error()
        async def error_handler(event, exception):
            """Глобальный обработчик ошибок"""
            logger.error(f"Необработанная ошибка: {exception}", exc_info=True)
        
        # Настройка событий запуска и остановки
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)
        
        # Запуск бота
        logger.info("Запуск бота...")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Ошибка при запуске: {e}", exc_info=True)
        sys.exit(1)
