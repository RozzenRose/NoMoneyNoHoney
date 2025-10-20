import json

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
async def test_create_income(monkeypatch, client_with_overrides):
    """Test successful creation of a new income record."""
    # Мокаем саму функцию записи в базу
    mock_create_income_in_db = AsyncMock()
    monkeypatch.setattr("app.routers.incomes.create_income_in_db", mock_create_income_in_db)

    payload = { # Собираем JSON для отправки в ендпоинт
              "description": "Salary",
              "quantity": 1000,
              "currency": "EUR"
    }

    # Отправляем запрос в ендпоинт
    response = client_with_overrides.post("/incomes/new_income", json=payload)

    # Ожидаемые события
    assert response.status_code == 201
    data = response.json()
    assert data["transaction"] == "Income created successfully"

    # Проверяем, что create_income_in_db была вызвана с правильными аргументами
    mock_create_income_in_db.assert_awaited_once_with(
        ANY,
        123,# db session
        "Salary",  # description
        1000.0,  # quantity
        "EUR"  # currency
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("invalid_payload, expected_status", [ # Параметрические тест
    ({"quantity": 100, "currency": "EUR"}, 422),  # missing description
    ({"description": "Salary", "currency": "EUR"}, 422),  # missing quantity # negative amount
    ({"description": "Salary", "quantity": 100, "currency": "INVALID"}, 422),  # invalid currency
    ({"description": "Salary", "quantity": -100, "currency": "EUR"}, 422),
])
async def test_create_income_validation(invalid_payload, expected_status, client_with_overrides):
    """Test income creation with invalid payloads."""
    response = client.post("/incomes/new_income", json=invalid_payload)
    assert response.status_code == expected_status


fake_result = [{ # Объект для замены результата ДБешных функций
                  "owner_id": 1,
                  "quantity": 100,
                  "description": "Salary",
                  "created_at": "2025-08-16",
                  "id": 1,
                  "currency": "EUR"
                },
                {
                  "owner_id": 1,
                  "quantity": 500,
                  "description": "Salary",
                  "created_at": "2025-09-16",
                  "id": 2,
                  "currency": "EUR"
                },
                {
                  "owner_id": 1,
                  "quantity": 1000,
                  "description": "Salary",
                  "created_at": "2025-10-16",
                  "id": 3,
                  "currency": "EUR"
                }]


async def mock_rpc_incomes_request(future, raw_data, current):
    '''Мок RPC функции'''
    future.set_result('{"euro": 100, "rub": 10000, "rsd": 11700, "answer": 300}')
    mock_queue = AsyncMock()
    return mock_queue, "consumer_tag"


@pytest.mark.asyncio
async def test_get_all_incomes_success(monkeypatch, client_with_overrides):
    # mock DB dependency
    mock_get_all_incomes_from_db = AsyncMock(return_value=fake_result)

    # patch dependencies
    monkeypatch.setattr("app.routers.incomes.get_all_incomes_from_db", mock_get_all_incomes_from_db)
    monkeypatch.setattr("app.routers.incomes.rpc_incomes_request", mock_rpc_incomes_request)

    # Запрос
    response = client_with_overrides.get("/incomes/all_your_incomes")

    # Ожидаемые ответы
    assert response.status_code == 200
    data = response.json()
    assert data["incomes"] == fake_result
    assert data["euro"] == 100
    assert data["rub"] == 10000
    assert data["rsd"] == 11700
    assert data["answer"] == 300


@pytest.mark.asyncio
@pytest.mark.parametrize("current, expected_status", [ # Тестируем неправильный ввод
    ('INVALID', 422),
])
async def test_get_all_incomes_validation(current, expected_status, client_with_overrides):
    response = client_with_overrides.get("/incomes/all_your_incomes", params={"current": current})
    assert response.status_code == expected_status


@pytest.mark.asyncio
async def test_incomes_current_month(monkeypatch, client_with_overrides):
    # Мокаем БД функцию
    mock_get_incomes_current_from_db = AsyncMock(return_value=fake_result)
    
    # Заменяем запвисимости
    monkeypatch.setattr('app.routers.incomes.get_incomes_current_from_db', mock_get_incomes_current_from_db)
    monkeypatch.setattr('app.routers.incomes.rpc_incomes_request', mock_rpc_incomes_request)

    # Запрос
    response = client_with_overrides.get("/incomes/incomes_current_month")

    # Ожидаемые ответы
    assert response.status_code == 200
    data = response.json()
    assert data["incomes"] == fake_result
    assert data["euro"] == 100
    assert data["rub"] == 10000
    assert data["rsd"] == 11700
    assert data["answer"] == 300


@pytest.mark.asyncio
@pytest.mark.parametrize("current, expected_status", [ # Тестируем неправильный ввод
    ('INVALID', 422)
])
async def test_incomes_current_month_validation(current, expected_status, client_with_overrides):
    response = client_with_overrides.get("/incomes/incomes_current_month", params={"current": current})
    assert response.status_code == expected_status


@pytest.mark.asyncio
async def test_get_incomes_in_time_limits(monkeypatch, client_with_overrides):
    # Мокаем БД функцию
    mock_get_incomes_in_time_limits = AsyncMock(return_value=fake_result)

    # Заменяем запвисимости
    monkeypatch.setattr('app.routers.incomes.get_incomes_in_time_limits_from_db', mock_get_incomes_in_time_limits)
    monkeypatch.setattr('app.routers.incomes.rpc_incomes_request', mock_rpc_incomes_request)

    # Запрос
    response = client_with_overrides.get("/incomes/incomes_limits")

    # Ожидаемые ответы
    assert response.status_code == 200
    data = response.json()
    assert data["incomes"] == fake_result
    assert data["euro"] == 100
    assert data["rub"] == 10000
    assert data["rsd"] == 11700
    assert data["answer"] == 300


@pytest.mark.asyncio
@pytest.mark.parametrize("start_date, "
                         "end_date,"
                         "current, expected_status", [  # Тестируем неправильный ввод
    ('2025-07-16', '2025-10-16', 'INVALID', 422), # Валидные даты, невальдная валюта
    ('INVALID', '2025-10-16', 'EUR', 422), # Невалидная дата начала
    ('2025-07-16', 'INVALID', 'EUR', 422), # Невалидная дата конца
    ('INVALID', 'INVALID', 'INVALID', 422) # Все невалидное
])
async def test_get_incomes_in_time_limits_validation(start_date, end_date, current, expected_status, client_with_overrides):
    response = client_with_overrides.get("/incomes/incomes_limits",
                                         params={"current": current, "start_date": start_date, "end_date": end_date})
    assert response.status_code == expected_status
