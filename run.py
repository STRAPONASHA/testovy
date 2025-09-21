#!/usr/bin/env python3
"""
Скрипт для быстрого запуска e-commerce бота
"""
import asyncio
import sys
import os
from pathlib import Path

def check_requirements():
    """Проверка установленных зависимостей"""
    try:
        import aiogram
        import aiosqlite
        print("✅ Все зависимости установлены")
        return True
    except ImportError as e:
        print(f"❌ Отсутствует зависимость: {e}")
        print("Установите зависимости: pip install -r requirements.txt")
        return False

def check_config():
    """Проверка конфигурации"""
    try:
        import config
        if not config.BOT_TOKEN or config.BOT_TOKEN == "YOUR_BOT_TOKEN":
            print("❌ Не настроен токен бота в config.py")
            return False
        if not config.ADMIN_ID or config.ADMIN_ID == 123456789:
            print("⚠️  Не настроен ADMIN_ID в config.py")
            print("Рекомендуется установить ваш Telegram ID")
        print("✅ Конфигурация проверена")
        return True
    except ImportError:
        print("❌ Файл config.py не найден")
        return False

def check_database():
    """Проверка базы данных"""
    if not os.path.exists("ecommerce_bot.db"):
        print("⚠️  База данных не найдена")
        print("Запускаю инициализацию...")
        try:
            import init_data
            asyncio.run(init_data.init_test_data())
            print("✅ База данных инициализирована")
        except Exception as e:
            print(f"❌ Ошибка инициализации БД: {e}")
            return False
    else:
        print("✅ База данных найдена")
    return True

def main():
    """Основная функция"""
    print("🚀 Запуск E-commerce Telegram Bot")
    print("=" * 40)
    
    # Проверки
    if not check_requirements():
        sys.exit(1)
    
    if not check_config():
        sys.exit(1)
    
    if not check_database():
        sys.exit(1)
    
    print("\n🎉 Все проверки пройдены!")
    print("Запускаю бота...")
    print("Для остановки нажмите Ctrl+C")
    print("=" * 40)
    
    # Запуск бота
    try:
        import main
        asyncio.run(main.main())
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка при запуске бота: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
