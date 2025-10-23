import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, ANY
from app.database.db_depends import get_db
from app.functions.auth_functions import get_current_user
from app.main import app


client = TestClient(app)


@pytest.fixture
def override_get_db():
    async def fake_db():
        yield AsyncMock()  # фейковая сессия SQLAlchemy
    return fake_db


@pytest.fixture
def override_get_current_user():
    def fake_user():
        return {'user_id': 123,
                'username': 'test_username',
                'email': 'test@gmail.com',
                'is_admin': False,
                'expire': False}
    return fake_user


@pytest.fixture
def client_with_overrides(override_get_db, override_get_current_user):
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    with TestClient(app) as c:
        yield c
    app.dependency_overrides = {}  # сбросить после теста


@pytest.mark.asyncio
async def test_create_category(monkeypatch, client_with_overrides):
    """Test successful creation of a new income record."""
    # Мокаем саму функцию записи в базу
    mock_create_category_in_db = AsyncMock()
    monkeypatch.setattr("app.routers.categories.create_category_in_db", mock_create_category_in_db)

    # Отправляем запрос в ендпоинт
    response = client_with_overrides.post("/categories/new_category?category_name=Hardware")

    # Ожидаемые события
    assert response.status_code == 201
    data = response.json()
    assert data["transaction"] == "Category created successfully"

    # Проверяем, что create_income_in_db была вызвана с правильными аргументами
    mock_create_category_in_db.assert_awaited_once_with(ANY, 123, "Hardware")

    # Параметрического теста не буедт, пока что у этого ендпоинта нет валидации.
    # Поскольку никаких ограничений на имя категрии не предусмотренно


fake_result = [{ # Объект для замены результата ДБешных функций
                  "id": 1,
                  "owner_id": None,
                  "category_name": "Food",
                  "is_root": True
                },
                {
                  "id": 2,
                  "owner_id": 123,
                  "category_name": "Hardware",
                  "is_root": False
                },
                {
                  "id": 3,
                  "owner_id": 123,
                  "category_name": "Entertament",
                  "is_root": False
                }]


@pytest.mark.asyncio
async def test_get_all_categories(monkeypatch, client_with_overrides):
    # mock DB dependency
    mock_get_all_categories_from_db = AsyncMock(return_value=fake_result)

    # patch dependencies
    monkeypatch.setattr("app.routers.categories.get_all_categories_from_db", mock_get_all_categories_from_db)

    # Запрос
    response = client_with_overrides.get("/categories/all_your_categories")

    # Ожидаемые ответы
    assert response.status_code == 200
    data = response.json()
    assert data["categories"] == fake_result

    mock_get_all_categories_from_db.assert_awaited_once_with(ANY, 123)
