# 👨‍💻 Руководство разработчика

## 🎯 Обзор

Данное руководство предназначено для разработчиков, которые хотят понять архитектуру проекта, внести изменения или расширить функциональность бота.

## 🏗️ Архитектура проекта

### Структура модулей

```
ecommerce-bot/
├── main.py                 # Точка входа приложения
├── config.py              # Конфигурация и настройки
├── run.py                 # Скрипт быстрого запуска
├── init_data.py          # Инициализация тестовых данных
├── database/             # Слой данных
│   ├── models.py         # Модели данных
│   └── repository.py     # Repository паттерн
├── handlers/             # Слой представления
│   ├── catalog.py        # Обработчики каталога
│   ├── cart.py          # Обработчики корзины
│   ├── order.py         # Обработчики заказов
│   └── admin.py         # Обработчики админ-панели
└── tests/               # Тесты
    ├── test_cart.py
    ├── test_orders.py
    └── test_products.py
```

### Принципы архитектуры

1. **Разделение ответственности** - каждый модуль отвечает за свою область
2. **Repository паттерн** - абстракция работы с данными
3. **Асинхронное программирование** - использование asyncio
4. **Обработка ошибок** - централизованная обработка исключений
5. **Логирование** - подробное логирование всех операций

## 🔧 Настройка среды разработки

### Требования

- Python 3.8+
- pip
- Git
- IDE (VS Code, PyCharm, etc.)

### Установка зависимостей

```bash
# Клонирование репозитория
git clone <repository-url>
cd ecommerce-bot

# Создание виртуального окружения
python -m venv venv

# Активация окружения
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Установка зависимостей для разработки
pip install pytest pytest-asyncio black flake8 mypy
```

### Настройка IDE

#### VS Code

Создайте `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests"]
}
```

#### PyCharm

1. Откройте проект в PyCharm
2. Настройте интерпретатор Python на виртуальное окружение
3. Включите поддержку pytest
4. Настройте форматирование кода

## 📝 Стандарты кодирования

### PEP 8

Следуйте стандартам PEP 8:

```python
# Хорошо
def calculate_total(items: List[CartItem]) -> float:
    """Подсчитывает общую сумму корзины."""
    total = 0.0
    for item in items:
        total += item.price * item.quantity
    return total

# Плохо
def calculateTotal(items):
    total=0
    for item in items:
        total+=item.price*item.quantity
    return total
```

### Типизация

Используйте type hints:

```python
from typing import List, Optional, Dict, Any

async def get_user_orders(user_id: int) -> List[Order]:
    """Получает заказы пользователя."""
    # Реализация
    pass

def validate_product_data(data: Dict[str, Any]) -> Optional[str]:
    """Валидирует данные товара."""
    # Реализация
    pass
```

### Документация

Используйте docstrings:

```python
async def create_order(order: Order, items: List[OrderItem]) -> Order:
    """
    Создает новый заказ в системе.
    
    Args:
        order: Данные заказа
        items: Позиции заказа
        
    Returns:
        Созданный заказ с присвоенным ID
        
    Raises:
        ValueError: Если данные заказа некорректны
        DatabaseError: Если произошла ошибка БД
    """
    # Реализация
    pass
```

## 🧪 Разработка тестов

### Структура тестов

```python
@pytest.mark.asyncio
async def test_functionality(setup_test_db):
    """Описание теста."""
    # Arrange - подготовка данных
    repo, user_repo, product_repo, test_user, test_product = await setup_test_db
    
    # Act - выполнение действия
    result = await repo.some_function(test_data)
    
    # Assert - проверка результата
    assert result is not None
    assert result.status == "expected_status"
```

### Покрытие тестами

```bash
# Запуск тестов с покрытием
pytest --cov=database --cov=handlers tests/

# Генерация отчета
pytest --cov=database --cov=handlers --cov-report=html tests/
```

### Моки и стабы

```python
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_with_mock():
    """Тест с моком."""
    with patch('module.external_service') as mock_service:
        mock_service.return_value = AsyncMock(return_value="mocked_data")
        
        result = await function_that_uses_service()
        
        assert result == "expected_result"
        mock_service.assert_called_once()
```

## 🔄 Рабочий процесс разработки

### Git workflow

```bash
# Создание ветки для новой функции
git checkout -b feature/new-feature

# Внесение изменений
# ... код ...

# Коммит изменений
git add .
git commit -m "feat: add new feature"

# Отправка в репозиторий
git push origin feature/new-feature

# Создание Pull Request
```

### Коммиты

Используйте conventional commits:

- `feat:` - новая функция
- `fix:` - исправление ошибки
- `docs:` - изменения в документации
- `style:` - форматирование кода
- `refactor:` - рефакторинг
- `test:` - добавление тестов
- `chore:` - обновление зависимостей

### Code review

1. **Проверка кода** на соответствие стандартам
2. **Запуск тестов** и проверка покрытия
3. **Проверка документации** и комментариев
4. **Тестирование функциональности** вручную

## 🚀 Добавление новой функции

### Пример: добавление системы скидок

#### 1. Обновление моделей

```python
# database/models.py
@dataclass
class Discount:
    """Модель скидки."""
    id: int
    code: str
    percentage: float
    min_amount: float
    is_active: bool
    expires_at: Optional[datetime] = None
```

#### 2. Обновление репозитория

```python
# database/repository.py
class DiscountRepository(DatabaseRepository):
    """Репозиторий для работы со скидками."""
    
    async def get_discount(self, code: str) -> Optional[Discount]:
        """Получает скидку по коду."""
        # Реализация
        pass
    
    async def apply_discount(self, order_id: int, discount_code: str) -> bool:
        """Применяет скидку к заказу."""
        # Реализация
        pass
```

#### 3. Обновление обработчиков

```python
# handlers/order.py
@router.callback_query(F.data.startswith("apply_discount_"))
async def apply_discount(callback: CallbackQuery, state: FSMContext):
    """Применяет скидку к заказу."""
    # Реализация
    pass
```

#### 4. Добавление тестов

```python
# tests/test_discounts.py
@pytest.mark.asyncio
async def test_apply_discount():
    """Тест применения скидки."""
    # Реализация
    pass
```

#### 5. Обновление документации

```markdown
# README.md
## Новые возможности
- Система скидок
- Промокоды
```

## 🔍 Отладка

### Логирование

```python
import logging

logger = logging.getLogger(__name__)

async def some_function():
    try:
        # Код
        logger.info("Функция выполнена успешно")
    except Exception as e:
        logger.error(f"Ошибка в функции: {e}", exc_info=True)
```

### Отладка в IDE

#### VS Code

```json
// .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Bot",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/main.py",
            "console": "integratedTerminal",
            "env": {
                "PYTHONPATH": "${workspaceFolder}"
            }
        }
    ]
}
```

### Отладка асинхронного кода

```python
import asyncio
import logging

# Включение отладки asyncio
logging.basicConfig(level=logging.DEBUG)
asyncio.get_event_loop().set_debug(True)
```

## 📊 Профилирование

### Измерение производительности

```python
import time
import asyncio
from functools import wraps

def measure_time(func):
    """Декоратор для измерения времени выполнения."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} выполнен за {end - start:.2f} секунд")
        return result
    return wrapper

@measure_time
async def slow_function():
    """Медленная функция."""
    await asyncio.sleep(1)
    return "result"
```

### Мониторинг памяти

```python
import tracemalloc

# Начало отслеживания
tracemalloc.start()

# Код

# Получение статистики
current, peak = tracemalloc.get_traced_memory()
print(f"Текущее использование памяти: {current / 1024 / 1024:.1f} MB")
print(f"Пиковое использование памяти: {peak / 1024 / 1024:.1f} MB")
```

## 🔒 Безопасность

### Валидация входных данных

```python
from pydantic import BaseModel, validator

class ProductData(BaseModel):
    name: str
    price: float
    stock: int
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError('Название должно содержать минимум 3 символа')
        return v.strip()
    
    @validator('price')
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Цена должна быть больше 0')
        return v
```

### Защита от SQL-инъекций

```python
# Хорошо - использование параметризованных запросов
async with db.execute(
    "SELECT * FROM products WHERE id = ?", (product_id,)
) as cursor:
    row = await cursor.fetchone()

# Плохо - уязвимость к SQL-инъекциям
async with db.execute(
    f"SELECT * FROM products WHERE id = {product_id}"
) as cursor:
    row = await cursor.fetchone()
```

### Ограничение доступа

```python
def require_admin(func):
    """Декоратор для проверки прав администратора."""
    @wraps(func)
    async def wrapper(message: Message, *args, **kwargs):
        if message.from_user.id != config.ADMIN_ID:
            await message.answer("❌ У вас нет прав доступа")
            return
        return await func(message, *args, **kwargs)
    return wrapper

@require_admin
async def admin_command(message: Message):
    """Команда только для администратора."""
    # Реализация
    pass
```

## 📈 Оптимизация

### Кэширование

```python
from functools import lru_cache
import asyncio

@lru_cache(maxsize=128)
def expensive_calculation(data: str) -> str:
    """Дорогая операция с кэшированием."""
    # Реализация
    return result

# Асинхронное кэширование
cache = {}

async def async_cached_function(key: str):
    """Асинхронная функция с кэшированием."""
    if key in cache:
        return cache[key]
    
    result = await expensive_async_operation(key)
    cache[key] = result
    return result
```

### Пакетная обработка

```python
async def batch_process_items(items: List[Item]):
    """Пакетная обработка элементов."""
    batch_size = 100
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        await process_batch(batch)
```

## 🚀 Развертывание

### CI/CD

```yaml
# .github/workflows/ci.yml
name: CI/CD

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-asyncio
    
    - name: Run tests
      run: pytest tests/
    
    - name: Run linting
      run: flake8 .
    
    - name: Run type checking
      run: mypy .
```

### Docker для разработки

```dockerfile
# Dockerfile.dev
FROM python:3.9-slim

WORKDIR /app

# Установка зависимостей для разработки
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install pytest pytest-asyncio black flake8 mypy

# Копирование кода
COPY . .

# Запуск в режиме разработки
CMD ["python", "main.py"]
```

## 📚 Полезные ресурсы

### Документация

- [aiogram 3.x](https://docs.aiogram.dev/)
- [asyncio](https://docs.python.org/3/library/asyncio.html)
- [pytest](https://docs.pytest.org/)
- [SQLite](https://www.sqlite.org/docs.html)

### Инструменты

- **Black** - форматирование кода
- **Flake8** - линтинг
- **MyPy** - проверка типов
- **pytest** - тестирование
- **pre-commit** - хуки Git

### Лучшие практики

1. **Следуйте принципам SOLID**
2. **Пишите тесты для нового кода**
3. **Документируйте публичные API**
4. **Используйте type hints**
5. **Обрабатывайте ошибки gracefully**
6. **Логируйте важные события**
7. **Оптимизируйте производительность**

## 🎉 Заключение

Данное руководство поможет вам эффективно разрабатывать и поддерживать Telegram e-commerce бота. Следуйте принципам чистого кода, пишите тесты и документируйте изменения.

**Удачной разработки! 🚀**
