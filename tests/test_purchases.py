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


async def mock_rpc_request(future, raw_data, current):
    '''Мок RPC функции'''
    future.set_result('{"euro": 100, "rub": 10000, "rsd": 11700, "answer": 300}')
    mock_queue = AsyncMock()
    return mock_queue, "consumer_tag"


fake_result = [{ # Объект для замены результата ДБешных функций
                  'id': 1,
                  'name': 'Moza R5',
                  'description': 'Steering Wheel',
                  'price': 700,
                  'currency': 'EUR',
                  'owner_id': 123,
                  'category_id': 9,
                  'created_at': '2025-08-21'
                },
                {
                  'id': 2,
                  'name': 'RTX 3080Ti',
                  'description': 'GPU',
                  'price': 1500,
                  'currency': 'EUR',
                  'owner_id': 123,
                  'category_id': 9,
                  'created_at': '2025-09-21'
                },
                {
                  'id': 1,
                  'name': 'i7 11900kf',
                  'description': 'CPU',
                  'price': 300,
                  'currency': 'EUR',
                  'owner_id': 123,
                  'category_id': 9,
                  'created_at': '2025-10-21'
                }]


@pytest.mark.asyncio
async def test_new_list_purchases(monkeypatch, client_with_overrides):
    mock_create_purchases_list_in_db = AsyncMock(return_value=fake_result)

    # patch dependencies
    monkeypatch.setattr("app.routers.purchases.create_purchases_list_in_db", mock_create_purchases_list_in_db)

    payload = {"purchases":
                [
                    {
                        "name": "string",
                        "description": "string",
                        "price": 0,
                        "currency": "string",
                        "category_id": 0
                    },
                    {
                        "name": "string",
                        "description": "string",
                        "price": 0,
                        "currency": "string",
                        "category_id": 0
                    },
                    {
                        "name": "string",
                        "description": "string",
                        "price": 0,
                        "currency": "string",
                        "category_id": 0
                    }
                ]
              }

    # Запрос
    response = client_with_overrides.post("/purchases/new_purchases", json=payload)

    # Ожидаемые ответы
    assert response.status_code == 201
    data = response.json()
    assert data["transaction"] == "Purchase created successfully"

    mock_create_purchases_list_in_db.assert_awaited_once_with(ANY, ANY, 123)


@pytest.mark.asyncio
async def test_get_all_purchases(monkeypatch, client_with_overrides):
    # mock DB dependency
    mock_get_all_purchases_from_db = AsyncMock(return_value=fake_result)

    # patch dependencies
    monkeypatch.setattr("app.routers.purchases.get_all_purchases_from_db", mock_get_all_purchases_from_db)
    monkeypatch.setattr("app.routers.purchases.rpc_purchases_request", mock_rpc_request)

    # Запрос
    response = client_with_overrides.get("/purchases/all_purchases")

    # Ожидаемые ответы
    assert response.status_code == 200
    data = response.json()
    assert data["purchases"] == fake_result
    assert data["euro"] == 100
    assert data["rub"] == 10000
    assert data["rsd"] == 11700
    assert data["answer"] == 300

    mock_get_all_purchases_from_db.assert_awaited_once_with(ANY, 123)


@pytest.mark.asyncio
@pytest.mark.parametrize("current, expected_status", [ # Тестируем неправильный ввод
    ('INVALID', 422),
])
async def test_get_all_purchases_validation(current, expected_status, client_with_overrides):
    response = client_with_overrides.get("/purchases/all_purchases", params={"current": current})
    assert response.status_code == expected_status


@pytest.mark.asyncio
async def test_get_last_7_days_purchases(monkeypatch, client_with_overrides):
    # mock DB dependency
    mock_get_purchases_current_week_from_db = AsyncMock(return_value=fake_result)

    # patch dependencies
    monkeypatch.setattr("app.routers.purchases.get_purchases_current_week_from_db", mock_get_purchases_current_week_from_db)
    monkeypatch.setattr("app.routers.purchases.rpc_purchases_request", mock_rpc_request)

    # Запрос
    response = client_with_overrides.get("/purchases/last_7_days_purchases")

    # Ожидаемые ответы
    assert response.status_code == 200
    data = response.json()
    assert data["purchases"] == fake_result
    assert data["euro"] == 100
    assert data["rub"] == 10000
    assert data["rsd"] == 11700
    assert data["answer"] == 300

    mock_get_purchases_current_week_from_db.assert_awaited_once_with(ANY, 123)


@pytest.mark.asyncio
@pytest.mark.parametrize("current, expected_status", [ # Тестируем неправильный ввод
    ('INVALID', 422),
])
async def test_get_last_7_days_purchases_validation(current, expected_status, client_with_overrides):
    response = client_with_overrides.get("/purchases/last_7_days_purchases", params={"current": current})
    assert response.status_code == expected_status


@pytest.mark.asyncio
async def test_get_purchases_in_limits(monkeypatch, client_with_overrides):
    # mock DB dependency
    mock_get_purchases_in_limits_from_db = AsyncMock(return_value=fake_result)

    # patch dependencies
    monkeypatch.setattr("app.routers.purchases.get_purchases_in_limits_from_db", mock_get_purchases_in_limits_from_db)
    monkeypatch.setattr("app.routers.purchases.rpc_purchases_request", mock_rpc_request)

    # Запрос
    response = client_with_overrides.get("/purchases/purchases_limits")

    # Ожидаемые ответы
    assert response.status_code == 200
    data = response.json()
    assert data["purchases"] == fake_result
    assert data["euro"] == 100
    assert data["rub"] == 10000
    assert data["rsd"] == 11700
    assert data["answer"] == 300

    mock_get_purchases_in_limits_from_db.assert_awaited_once_with(ANY, 123, ANY, ANY)


@pytest.mark.asyncio
@pytest.mark.parametrize("current, expected_status", [ # Тестируем неправильный ввод
    ('INVALID', 422),
])
async def test_get_purchases_in_limits_validation(current, expected_status, client_with_overrides):
    response = client_with_overrides.get("/purchases/purchases_limits", params={"current": current})
    assert response.status_code == expected_status
