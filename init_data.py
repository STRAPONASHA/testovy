"""
Скрипт для инициализации тестовых данных
"""
import asyncio
import logging
from database.repository import DatabaseRepository, ProductRepository
from database.models import Category, Product
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_test_data():
    """Инициализация тестовых данных"""
    try:
        # Инициализируем базу данных
        db_repo = DatabaseRepository()
        await db_repo.init_db()
        logger.info("База данных инициализирована")
        
        # Создаем репозиторий для товаров
        product_repo = ProductRepository()
        
        # Создаем категории
        categories_data = [
            {"name": "Электроника", "description": "Смартфоны, планшеты, ноутбуки и аксессуары"},
            {"name": "Одежда", "description": "Мужская и женская одежда"},
            {"name": "Книги", "description": "Художественная и техническая литература"},
            {"name": "Спорт", "description": "Спортивные товары и инвентарь"},
            {"name": "Дом и сад", "description": "Товары для дома и сада"}
        ]
        
        logger.info("Создание категорий...")
        for cat_data in categories_data:
            # Проверяем, существует ли категория
            existing_categories = await product_repo.get_categories()
            if not any(cat.name == cat_data["name"] for cat in existing_categories):
                category = Category(
                    id=0,  # Будет установлен автоматически
                    name=cat_data["name"],
                    description=cat_data["description"]
                )
                
                # Добавляем категорию напрямую в базу
                import aiosqlite
                async with aiosqlite.connect("ecommerce_bot.db") as db:
                    await db.execute(
                        "INSERT INTO categories (name, description) VALUES (?, ?)",
                        (category.name, category.description)
                    )
                    await db.commit()
                logger.info(f"Создана категория: {category.name}")
        
        # Получаем созданные категории
        categories = await product_repo.get_categories()
        category_map = {cat.name: cat.id for cat in categories}
        
        # Создаем тестовые товары
        products_data = [
            {
                "name": "iPhone 15 Pro",
                "description": "Новейший смартфон Apple с титановым корпусом, камерой 48 МП и чипом A17 Pro. Поддержка 5G, Face ID, беспроводная зарядка.",
                "price": 99999.0,
                "category": "Электроника",
                "stock": 5,
                "image_url": None,
                "detailed_description": "iPhone 15 Pro оснащен 6.1-дюймовым Super Retina XDR дисплеем с технологией ProMotion. Титановый корпус обеспечивает прочность и легкость. Камера 48 МП с оптическим зумом 3x, поддержка ProRAW и ProRes. Чип A17 Pro обеспечивает максимальную производительность. Водонепроницаемость IP68.",
                "sizes": "128GB,256GB,512GB,1TB",
                "colors": "Титан,Титан синий,Титан белый,Титан черный",
                "material": "Титан, керамический щит",
                "weight": "187 г",
                "dimensions": "146.6 x 70.6 x 8.25 мм",
                "brand": "Apple",
                "country": "Китай"
            },
            {
                "name": "MacBook Air M2",
                "description": "Ультратонкий ноутбук с чипом Apple M2, 13.6-дюймовым дисплеем Liquid Retina, 8 ГБ RAM, 256 ГБ SSD. До 18 часов работы от батареи.",
                "price": 129999.0,
                "category": "Электроника",
                "stock": 3,
                "image_url": None,
                "detailed_description": "MacBook Air с чипом M2 обеспечивает невероятную производительность и энергоэффективность. 13.6-дюймовый Liquid Retina дисплей с поддержкой P3 цветового пространства. 8-ядерный CPU и 8-ядерный GPU. До 18 часов работы от батареи. Беспроводная зарядка MagSafe.",
                "sizes": "256GB,512GB,1TB,2TB",
                "colors": "Серебристый,Звездный серый,Полночь,Старлайт",
                "material": "Алюминий",
                "weight": "1.24 кг",
                "dimensions": "304.1 x 215.0 x 11.3 мм",
                "brand": "Apple",
                "country": "Китай"
            },
            {
                "name": "Джинсы Levi's 501",
                "description": "Классические прямые джинсы из 100% хлопка. Универсальная модель, подходящая для любого стиля. Размеры от 28 до 40.",
                "price": 5999.0,
                "category": "Одежда",
                "stock": 15,
                "image_url": None,
                "detailed_description": "Классические джинсы Levi's 501 - это икона американского стиля. Прямой крой, высокая посадка, застежка на пуговицы. Изготовлены из прочного денима с добавлением эластана для комфорта. Классические карманы и строчка в стиле Levi's.",
                "sizes": "28,30,32,34,36,38,40",
                "colors": "Синий,Черный,Светло-синий",
                "material": "98% хлопок, 2% эластан",
                "weight": "0.8 кг",
                "dimensions": "Длина по внутреннему шву: 76 см",
                "brand": "Levi's",
                "country": "Мексика"
            },
            {
                "name": "Футболка Nike Dri-FIT",
                "description": "Спортивная футболка из технологии Dri-FIT для отвода влаги. Удобная посадка, дышащий материал. Доступна в разных цветах.",
                "price": 2999.0,
                "category": "Одежда",
                "stock": 25,
                "image_url": None
            },
            {
                "name": "1984 - Джордж Оруэлл",
                "description": "Классический роман-антиутопия о тоталитарном обществе. Одно из самых влиятельных произведений XX века. Твердый переплет.",
                "price": 899.0,
                "category": "Книги",
                "stock": 20,
                "image_url": None
            },
            {
                "name": "Python для начинающих",
                "description": "Подробное руководство по изучению Python с нуля. Примеры кода, упражнения, проекты. Идеально для новичков в программировании.",
                "price": 1299.0,
                "category": "Книги",
                "stock": 12,
                "image_url": None
            },
            {
                "name": "Беговая дорожка ProForm",
                "description": "Электрическая беговая дорожка с 12 предустановленными программами тренировок. Максимальная скорость 16 км/ч, наклон до 12%.",
                "price": 89999.0,
                "category": "Спорт",
                "stock": 2,
                "image_url": None
            },
            {
                "name": "Гантели разборные 20 кг",
                "description": "Набор разборных гантелей с блинами по 2.5 кг каждый. Хромированные грифы, резиновые блины. В комплекте стойка для хранения.",
                "price": 15999.0,
                "category": "Спорт",
                "stock": 8,
                "image_url": None
            },
            {
                "name": "Кофемашина De'Longhi",
                "description": "Автоматическая кофемашина с встроенной кофемолкой. Приготовление эспрессо, капучино, латте. 15 бар давления, 1.8 л бак для воды.",
                "price": 45999.0,
                "category": "Дом и сад",
                "stock": 4,
                "image_url": None
            },
            {
                "name": "Набор кастрюль Tefal",
                "description": "Набор из 3 кастрюль с антипригарным покрытием. Размеры: 16, 20, 24 см. Стеклянные крышки, эргономичные ручки.",
                "price": 7999.0,
                "category": "Дом и сад",
                "stock": 6,
                "image_url": None
            }
        ]
        
        logger.info("Создание товаров...")
        for prod_data in products_data:
            # Проверяем, существует ли товар
            existing_products = await product_repo.get_products_by_category(category_map[prod_data["category"]])
            if not any(prod.name == prod_data["name"] for prod in existing_products):
                product = Product(
                    id=0,  # Будет установлен автоматически
                    name=prod_data["name"],
                    description=prod_data["description"],
                    price=prod_data["price"],
                    category_id=category_map[prod_data["category"]],
                    image_url=prod_data["image_url"],
                    stock=prod_data["stock"],
                    is_active=True,
                    detailed_description=prod_data.get("detailed_description"),
                    sizes=prod_data.get("sizes"),
                    colors=prod_data.get("colors"),
                    material=prod_data.get("material"),
                    weight=prod_data.get("weight"),
                    dimensions=prod_data.get("dimensions"),
                    brand=prod_data.get("brand"),
                    country=prod_data.get("country")
                )
                
                await product_repo.add_product(product)
                logger.info(f"Создан товар: {product.name}")
        
        logger.info("Тестовые данные успешно созданы!")
        
    except Exception as e:
        logger.error(f"Ошибка при создании тестовых данных: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(init_test_data())
