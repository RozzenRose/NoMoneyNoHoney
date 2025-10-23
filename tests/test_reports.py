import io

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, ANY, Mock
from app.database.db_depends import get_db
from app.functions.auth_functions import get_current_user
from app.main import app
from app.database.models import Purchase, Income, Category
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4


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


fake_result_purchases = [Purchase.from_json({ # Объект для замены результата ДБешных функций
                          'id': 1,
                          'name': 'Moza R5',
                          'description': 'Steering Wheel',
                          'price': 700,
                          'currency': 'EUR',
                          'owner_id': 123,
                          'category_id': 9,
                          'created_at': '2025-08-21'
                        }),
                        Purchase.from_json({
                          'id': 2,
                          'name': 'RTX 3080Ti',
                          'description': 'GPU',
                          'price': 1500,
                          'currency': 'EUR',
                          'owner_id': 123,
                          'category_id': 9,
                          'created_at': '2025-09-21'
                        }),
                        Purchase.from_json({
                          'id': 1,
                          'name': 'i7 11900kf',
                          'description': 'CPU',
                          'price': 300,
                          'currency': 'EUR',
                          'owner_id': 123,
                          'category_id': 9,
                          'created_at': '2025-10-21'
                        })]

fake_result_incomes = [Income.from_json({ # Объект для замены результата ДБешных функций
                          "owner_id": 1,
                          "quantity": 100,
                          "description": "Salary",
                          "created_at": "2025-08-16",
                          "id": 1,
                          "currency": "EUR"
                        }),
                        Income.from_json({
                          "owner_id": 1,
                          "quantity": 500,
                          "description": "Salary",
                          "created_at": "2025-09-16",
                          "id": 2,
                          "currency": "EUR"
                        }),
                        Income.from_json({
                          "owner_id": 1,
                          "quantity": 1000,
                          "description": "Salary",
                          "created_at": "2025-10-16",
                          "id": 3,
                          "currency": "EUR"
                        })]

fake_result_categories = [Category.from_json({ # Объект для замены результата ДБешных функций
                              "id": 1,
                              "owner_id": None,
                              "category_name": "Food",
                              "is_root": True
                            }),
                            Category.from_json({
                              "id": 2,
                              "owner_id": 123,
                              "category_name": "Hardware",
                              "is_root": False
                            }),
                            Category.from_json({
                              "id": 3,
                              "owner_id": 123,
                              "category_name": "Entertament",
                              "is_root": False
                            })]


async def mock_rpc_report_request(future, raw_data, current):
    '''Мок RPC функции'''
    pdf_buf = io.BytesIO()
    c = canvas.Canvas(pdf_buf, pagesize=A4)
    c.setFont("DarkGardenMK", 22)
    c.drawString(50, 800, "test")
    pdf_buf.seek(0)
    pdf_bytes = pdf_buf.getvalue()
    future.set_result(pdf_bytes)
    mock_queue = AsyncMock()
    return mock_queue, "consumer_tag"


@pytest.mark.asyncio
async def test_get_rab_report(monkeypatch, client_with_overrides):
    # mock DB dependency
    mock_get_purchases_in_limits_from_db = AsyncMock(return_value=fake_result_purchases)
    mock_get_incomes_in_time_limits_from_db = AsyncMock(return_value=fake_result_incomes)
    mock_get_all_categories_from_db = AsyncMock(return_value=fake_result_categories)

    # patch dependencies
    monkeypatch.setattr("app.routers.reports.get_purchases_in_limits_from_db", mock_get_purchases_in_limits_from_db)
    monkeypatch.setattr("app.routers.reports.get_incomes_in_time_limits_from_db", mock_get_incomes_in_time_limits_from_db)
    monkeypatch.setattr("app.routers.reports.get_all_categories_from_db", mock_get_all_categories_from_db)
    monkeypatch.setattr("app.routers.reports.rpc_report_request", mock_rpc_report_request)

    # Запрос
    response = client_with_overrides.get("/reports/report_ask")

    # Ожидаемые ответы
    assert response.status_code == 200

    mock_get_purchases_in_limits_from_db.assert_awaited_once_with(ANY, 123, ANY, ANY)
    mock_get_incomes_in_time_limits_from_db.assert_awaited_once_with(ANY, 123, ANY, ANY)
    mock_get_all_categories_from_db.assert_awaited_once_with(ANY, 123)
